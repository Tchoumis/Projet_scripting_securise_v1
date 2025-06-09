import os
import json
import sqlite3
from datetime import datetime
import time
from sauvegarde import rotate_log, backup_files  # Importer les fonctions spécifiques
from gestionnaire_mdp import add_password, retrieve_password, load_key
import subprocess
from gestion_utilisateur.gestion_mdp import check_password_complexity, generate_password_report, force_password_change
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# =======================================================
# Configuration des fichiers
# =======================================================
LOG_FILE = "/home/sylvie/Projet_scripting_securise_sylvie/hash_changes.log"
JSON_FILE = "/home/sylvie/Projet_scripting_securise_sylvie/alerts.json"
SQLITE_DB = "/home/sylvie/sqlite_db/alerts.db"



# =======================================================
# Initialisation des fichiers nécessaires
# =======================================================
def initialize_files():
    global LOG_FILE, JSON_FILE, SQLITE_DB

    # Créer les répertoires si nécessaires
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(SQLITE_DB), exist_ok=True)

    # Créer les fichiers si ils n'existent pas
    if not os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'w'): pass  # Créer un fichier vide si nécessaire
            print(f"[INFO] Fichier de log créé : {LOG_FILE}")
        except PermissionError:
            print(f"[ERROR] Permission refusée pour créer le fichier de log : {LOG_FILE}")
    
    if not os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'w'): pass  # Créer un fichier vide si nécessaire
            print(f"[INFO] Fichier JSON créé : {JSON_FILE}")
        except PermissionError:
            print(f"[ERROR] Permission refusée pour créer le fichier JSON : {JSON_FILE}")

    if not os.path.exists(SQLITE_DB):
        try:
            conn = sqlite3.connect(SQLITE_DB)
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS alerts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            timestamp TEXT NOT NULL,
                            message TEXT NOT NULL,
                            UNIQUE(timestamp, message)
                        )''')
            conn.commit()
            conn.close()
            print(f"[INFO] Base de données SQLite et table 'alerts' créées : {SQLITE_DB}")
        except PermissionError:
            print(f"[ERROR] Permission refusée pour créer la base de données SQLite : {SQLITE_DB}")


# =======================================================
# Fonction pour analyser le fichier de log
# =======================================================
def parse_log_file():
    events = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if " - " in line:
                        parts = line.split(" - ", 1)
                        if len(parts) == 2:
                            timestamp_str, message = parts
                            try:
                                datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                print(f"[ERREUR] Format de date invalide dans la ligne : {line}")
                                continue
                            events.append({
                                "timestamp": timestamp_str,
                                "message": message
                            })
        except Exception as e:
            print(f"[ERREUR] Échec de la lecture du fichier log : {e}")
    else:
        print(f"[INFO] Le fichier log '{LOG_FILE}' n'existe pas.")
    return events


# =======================================================
# Fonction pour stocker les événements dans un fichier JSON
# =======================================================
def store_events_json(events):
    try:
        with open(JSON_FILE, "w") as f:
            json.dump(events, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Les événements ont été enregistrés dans le fichier JSON : {JSON_FILE}")
    except Exception as e:
        print(f"[ERREUR] Échec de l'enregistrement dans le fichier JSON : {e}")


# =======================================================
# Fonction pour stocker les événements dans une base SQLite
# =======================================================
def store_events_sql(events):
    conn = None
    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()

        for event in events:
            c.execute("SELECT COUNT(*) FROM alerts WHERE timestamp = ? AND message = ?", 
                      (event["timestamp"], event["message"]))
            result = c.fetchone()

            if result[0] == 0:
                c.execute("INSERT INTO alerts (timestamp, message) VALUES (?, ?)", 
                          (event["timestamp"], event["message"]))
        
        conn.commit()
        print(f"[INFO] Les événements ont été enregistrés dans la base de données SQLite : {SQLITE_DB}")
    except sqlite3.Error as e:
        print(f"[ERREUR] Échec de l'insertion des événements dans SQLite : {e}")
    finally:
        if conn:
            conn.close()


# =======================================================
# Fonction pour scanner les ports d'une cible
# =======================================================
def scan_ports(target_ip):
    try:
        print(f"Scanning ports on {target_ip}...")
        result = subprocess.run(
            ["bash", "/home/sylvie/Projet_scripting_securise/scan_ports.sh", target_ip],
            check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du scan des ports: {e}")
        return None


# =======================================================
# Fonction pour analyser les résultats du scan
# =======================================================
def analyze_scan_results(scan_file):
    try:
        result = subprocess.run(
            ['python3', './analyze_scan_results.py', scan_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        
        if result.returncode == 0:
            print("Analyse des résultats du scan réussie.")
            print(result.stdout)
        else:
            print(f"Erreur lors de l'analyse des résultats : {result.stderr}")
    except Exception as e:
        print(f"Erreur : {e}")


# =======================================================
# Fonction pour exécuter un script bash
# =======================================================
def run_bash_script(script_path):
    try:
        result = subprocess.run([script_path], check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script: {e}")


# Fonction envoi de mail
def send_alert_email(subject, message):
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USER
        msg["To"] = ADMIN_EMAIL
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, ADMIN_EMAIL, msg.as_string())
        server.quit()
        print("[INFO] Email d'alerte envoyé avec succès.")
    except Exception as e:
        print(f"[ERREUR] Échec de l'envoi de l'email : {e}")


# =======================================================
# Fonction principale
# =======================================================
def main():
    # Initialisation des fichiers
    initialize_files()

    # Exemple d'utilisation de la gestion des mots de passe
    username = "testuser"
    password = "Test@1234"
    
    # Vérifier la complexité du mot de passe
    generate_password_report(username, password)
    if not check_password_complexity(password)[0]:
        force_password_change(username)

    # Analyse du fichier de log
    print("[INFO] Analyse du fichier de log...")
    events = parse_log_file()
    if not events:
        print("[INFO] Aucun événement détecté.")
        return

    print(f"[INFO] {len(events)} événement(s) détecté(s).")
    store_events_json(events)
    store_events_sql(events)

    # Exemple de surveillance des fichiers
    print("[INFO] Surveillance des fichiers...")
    while True:
        rotate_log()  # Rotation des logs
        backup_files()  # Sauvegarde des fichiers
        time.sleep(3600)  # 10 minutes

    # Exemple de scan de port
    target_ip = "192.168.1.125"
    scan_results = scan_ports(target_ip)
    if scan_results:
        with open("nmap_scan_results.txt", "w") as f:
            f.write(scan_results)
        analyze_scan_results("nmap_scan_results.txt")
    else:
        print("Aucun résultat de scan n'a été généré.")

    # Exemple d'ajout et récupération de mot de passe
    key = load_key()
    add_password('Gmail', 'mon_username', 'mon_password', key)
    creds = retrieve_password('Gmail', key)
    if creds:
        print(f"Service : {creds['username']}")
        print(f"Mot de passe : {creds['password']}")

    # Exécuter le script bash gestion_utilisateur.sh
    script_path = "./gestion_utilisateur/gestion_utilisateur.sh"
    run_bash_script(script_path)


if __name__ == "__main__":
    main()
