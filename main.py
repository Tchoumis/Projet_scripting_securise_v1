import os
import json
import sqlite3
import time
import subprocess
import threading
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sauvegarde import rotate_log, backup_files
from gestionnaire_mdp import add_password, retrieve_password, load_key
from gestion_utilisateur.gestion_mdp import check_password_complexity, generate_password_report, force_password_change

from dotenv import load_dotenv
load_dotenv()

# Chargement des variables d'environnement
LOG_FILE = os.getenv("LOG_FILE")
JSON_FILE = os.getenv("JSON_FILE")
SQLITE_DB = os.getenv("SQLITE_DB")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE) if LOG_FILE else logging.NullHandler(),
        logging.StreamHandler()
    ]
)

def validate_env_vars():
    required_vars = {
        "LOG_FILE": LOG_FILE,
        "JSON_FILE": JSON_FILE,
        "SQLITE_DB": SQLITE_DB,
        "ADMIN_EMAIL": ADMIN_EMAIL,
        "SMTP_SERVER": SMTP_SERVER,
        "SMTP_USER": SMTP_USER,
        "SMTP_PASSWORD": SMTP_PASSWORD
    }
    missing = [k for k,v in required_vars.items() if not v]
    if missing:
        logging.error(f"Variables d'environnement manquantes : {missing}")
        return False
    return True

def initialize_files():
    for path in [LOG_FILE, JSON_FILE, SQLITE_DB]:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except Exception as e:
            logging.error(f"Erreur création dossier {os.path.dirname(path)} : {e}")
    
    try:
        if LOG_FILE and not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w'): pass
            logging.info(f"Fichier log créé : {LOG_FILE}")
        if JSON_FILE and not os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'w'): pass
            logging.info(f"Fichier JSON créé : {JSON_FILE}")
        if SQLITE_DB and not os.path.exists(SQLITE_DB):
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
            logging.info(f"Base SQLite créée : {SQLITE_DB}")
    except PermissionError as e:
        logging.error(f"Permission refusée : {e}")
    except Exception as e:
        logging.error(f"Erreur lors de l'initialisation des fichiers : {e}")

def parse_log_file():
    events = []
    if LOG_FILE and os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if " - " in line:
                        timestamp_str, message = line.split(" - ", 1)
                        try:
                            # Acceptation des millisecondes
                            datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                            # Par exemple on peut filtrer certains messages ici (optionnel)
                            if not message.startswith("IPs bannies :"):
                                events.append({"timestamp": timestamp_str, "message": message})
                        except ValueError:
                            logging.warning(f"Format date invalide dans la ligne : {line}")
        except Exception as e:
            logging.error(f"Lecture du log : {e}")
    else:
        logging.warning(f"Fichier log introuvable : {LOG_FILE}")
    return events



def store_events_json(events):
    if not JSON_FILE:
        logging.error("JSON_FILE non défini")
        return
    try:
        with open(JSON_FILE, "w") as f:
            json.dump(events, f, indent=4, ensure_ascii=False)
        logging.info("Événements sauvegardés dans JSON.")
    except Exception as e:
        logging.error(f"Sauvegarde JSON : {e}")

def store_events_sql(events):
    if not SQLITE_DB:
        logging.error("SQLITE_DB non défini")
        return
    conn = None
    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()
        for event in events:
            c.execute("SELECT COUNT(*) FROM alerts WHERE timestamp = ? AND message = ?", (event["timestamp"], event["message"]))
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO alerts (timestamp, message) VALUES (?, ?)", (event["timestamp"], event["message"]))
        conn.commit()
        logging.info("Événements sauvegardés dans SQLite.")
    except sqlite3.Error as e:
        logging.error(f"SQLite : {e}")
    finally:
        if conn:
            conn.close()

def scan_ports(target_ip):
    try:
        logging.info(f"Scan de ports sur {target_ip}...")
        result = subprocess.run(
            ["bash", "/home/sylvie/Projet_scripting_securise_sylvie/scan_ports.sh", target_ip],
            check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"Scan ports : {e}")
        logging.error(f"stdout : {e.stdout}")
        logging.error(f"stderr : {e.stderr}")
        return None

def analyze_scan_results(scan_file):
    try:
        result = subprocess.run(
            ['python3', './analyze_scan_results.py', scan_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
            logging.info(result.stdout)
        else:
            logging.error(result.stderr)
    except Exception as e:
        logging.error(f"Analyse scan : {e}")

def run_bash_script(script_path):
    try:
        result = subprocess.run([script_path], check=True, text=True, capture_output=True)
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Script Bash : {e}")

def send_alert_email(subject, message):
    if not all([SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, ADMIN_EMAIL]):
        logging.error("Variables SMTP ou email admin non définies, impossible d'envoyer l'alerte.")
        return
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
        logging.info("Email d'alerte envoyé.")
    except Exception as e:
        logging.error(f"Email : {e}")

def test_fail2ban_bruteforce(ip):
    logging.info(f"Lancement du bruteforce SSH simulé sur {ip}...")
    try:
        subprocess.run([
            "hydra", "-l", "root", "-P", "/home/sylvie/smallwordlist.txt", f"ssh://{ip}"
        ], check=False, capture_output=True, text=True)
    except Exception as e:
        logging.error(f"Échec du test bruteforce : {e}")

def check_fail2ban_status(ip):
    try:
        result = subprocess.run(["sudo", "fail2ban-client", "status", "sshd"],
                                capture_output=True, text=True)

        output = result.stdout
        logging.info(f"Status fail2ban sshd:\n{output}")

        if "Banned IP list:" in output:
            banned_ips = output.split("Banned IP list:")[1].strip()
            banned_ips = banned_ips if banned_ips else "Aucune"
            logging.info(f"IPs bannies : {banned_ips}")

            # Ecrire dans le log
            with open(LOG_FILE, "a") as log:
                log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - IPs bannies : {banned_ips}\n")

            if banned_ips != "Aucune":
                send_alert_email("Alerte Fail2ban", f"IP(s) actuellement bannie(s) : {banned_ips}")

    except Exception as e:
        logging.error(f"Vérification Fail2ban : {e}")

def periodic_backup_rotation():
    while True:
        rotate_log()
        backup_files()
        logging.info("Rotation et sauvegarde effectuées.")
        time.sleep(600)  # 10 minutes

def main():
    if not validate_env_vars():
        logging.error("Variables d'environnement manquantes. Arrêt du script.")
        return

    logging.info("=== Initialisation des fichiers ===")
    initialize_files()

    logging.info("=== Analyse des logs ===")
    events = parse_log_file()
    if events:
        store_events_json(events)
        store_events_sql(events)
    else:
        logging.info("Aucun événement détecté dans les logs.")

    logging.info("=== Vérification des mots de passe ===")
    username = "testuser"
    password = "Test@1234"
    generate_password_report(username, password)
    if not check_password_complexity(password)[0]:
        force_password_change(username)

    key = load_key()
    add_password('Gmail', 'mon_username', 'mon_password', key)
    creds = retrieve_password('Gmail', key)
    if creds:
        logging.info(f"Service: {creds['username']}, Mot de passe: {creds['password']}")

    logging.info("=== Lancement du scan de ports ===")
    ip = "192.168.1.125"
    results = scan_ports(ip)
    if results:
        with open("nmap_scan_results.txt", "w") as f:
            f.write(results)
        analyze_scan_results("nmap_scan_results.txt")

        logging.info("=== Test du système de défense avec Fail2ban ===")
        test_fail2ban_bruteforce(ip)
        check_fail2ban_status(ip)
    else:
        logging.warning("Aucun résultat de scan généré.")

    logging.info("=== Lancement du script utilisateur ===")
    run_bash_script("./gestion_utilisateur/gestion_utilisateur.sh")

    logging.info("=== Démarrage de la surveillance de la sauvegarde et rotation ===")
    try:
        backup_thread = threading.Thread(target=periodic_backup_rotation, daemon=True)
        backup_thread.start()
        # Le thread tourne en arrière-plan, on peut éventuellement faire autre chose ici ou juste attendre.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Surveillance interrompue par l'utilisateur.")

if __name__ == "__main__":
    main()
