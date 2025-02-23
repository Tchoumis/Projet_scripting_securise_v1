import os
import json
import sqlite3
from datetime import datetime
import time
from sauvegarde import rotate_log, backup_files  # Importer les fonctions spécifiques
from gestionnaire_mdp import add_password, retrieve_password, load_key
import subprocess

# =======================================================
# Configuration des fichiers
# =======================================================
LOG_FILE = "/home/sylvie/Projet_scripting_securise/hash_changes.log"
JSON_FILE = "/home/sylvie/Projet_scripting_securise/alerts.json"
SQLITE_DB = "/var/log/alerts.db"


def initialize_files():
    # Déclaration globale des variables avant toute utilisation
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

def parse_log_file():
    """
    Analyse le fichier de log et renvoie une liste d'événements sous forme de dictionnaires.
    Format attendu pour chaque ligne : "YYYY-MM-DD HH:MM:SS - Message d'événement"
    """
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

def store_events_json(events):
    """
    Enregistre la liste des événements dans un fichier JSON.
    """
    try:
        with open(JSON_FILE, "w") as f:
            json.dump(events, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Les événements ont été enregistrés dans le fichier JSON : {JSON_FILE}")
    except Exception as e:
        print(f"[ERREUR] Échec de l'enregistrement dans le fichier JSON : {e}")

def store_events_sql(events):
    """
    Insère les événements dans la base de données SQLite.
    """
    conn = None
    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()

        for event in events:
            # Vérifier si l'événement existe déjà dans la base de données
            c.execute("SELECT COUNT(*) FROM alerts WHERE timestamp = ? AND message = ?", 
                      (event["timestamp"], event["message"]))
            result = c.fetchone()

            # Si l'événement n'existe pas, l'insérer
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

def main():
    # Initialisation des fichiers
    initialize_files()
    
    print("[INFO] Analyse du fichier de log...")
    events = parse_log_file()
    if not events:
        print("[INFO] Aucun événement détecté.")
        return

    print(f"[INFO] {len(events)} événement(s) détecté(s).")
    store_events_json(events)
    store_events_sql(events)

# Vous pouvez appeler les fonctions de sauvegarde dans le script principal selon vos besoins
def main():
    # Exemple de surveillance de fichiers
    print("Démarrage de la surveillance des fichiers...")
    # Par exemple, vérifier la rotation des logs tous les 10 minutes
    while True:
        # Rotation des logs
        rotate_log()

        # Sauvegarde des fichiers
        backup_files()

        # Attendre avant de vérifier à nouveau
        time.sleep(600)  # Par exemple, toutes les 10 minutes

def main():
    # Charger la clé de chiffrement
    key = load_key()

    # Ajouter un mot de passe (exemple)
    add_password('Gmail', 'mon_username', 'mon_password', key)

    # Récupérer un mot de passe pour un service
    creds = retrieve_password('Gmail', key)
    if creds:
        print(f"Service   : {creds['username']}")
        print(f"Mot de passe  : {creds['password']}")





# Fonction pour scanner les ports d'une cible
def scan_ports(target_ip):
    try:
        print(f"Scanning ports on {target_ip}...")
        # Exécution du script bash
        result = subprocess.run(
            ["bash", "/home/sylvie/Projet_scripting_securise/scan_ports.sh", target_ip],
            check=True, capture_output=True, text=True
        )
        return result.stdout  # Retourne la sortie du scan
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors du scan des ports: {e}")
        return None

# Fonction pour analyser les résultats du scan
def analyze_scan_results(scan_file):
    try:
        # Exécuter analyze_scan_results.py
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

# Fonction principale qui exécute les étapes
def main():
    target_ip = "192.168.1.115"  # Remplace par l'adresse IP cible
    
    # Scanner les ports
    scan_results = scan_ports(target_ip)
    
    if scan_results:
        # Sauvegarder les résultats dans un fichier pour analyse
        with open("nmap_scan_results.txt", "w") as f:
            f.write(scan_results)
        
        # Analyser les résultats du scan
        analyze_scan_results("nmap_scan_results.txt")
    else:
        print("Aucun résultat de scan n'a été généré.")

if __name__ == "__main__":
    main()

