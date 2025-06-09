import os
import json
import sqlite3
import time
import subprocess
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from sauvegarde import rotate_log, backup_files
from gestionnaire_mdp import add_password, retrieve_password, load_key
from gestion_utilisateur.gestion_mdp import check_password_complexity, generate_password_report, force_password_change

from dotenv import load_dotenv
load_dotenv()

LOG_FILE = os.getenv("LOG_FILE")
JSON_FILE = os.getenv("JSON_FILE")
SQLITE_DB = os.getenv("SQLITE_DB")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

def initialize_files():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(SQLITE_DB), exist_ok=True)

    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w'): pass
            print(f"[INFO] Fichier log créé : {LOG_FILE}")
        if not os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'w'): pass
            print(f"[INFO] Fichier JSON créé : {JSON_FILE}")
        if not os.path.exists(SQLITE_DB):
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
            print(f"[INFO] DB SQLite créée : {SQLITE_DB}")
    except PermissionError as e:
        print(f"[ERREUR] Permission refusée : {e}")

def parse_log_file():
    events = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                for line in f:
                    line = line.strip()
                    if " - " in line:
                        timestamp_str, message = line.split(" - ", 1)
                        try:
                            datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            events.append({"timestamp": timestamp_str, "message": message})
                        except ValueError:
                            continue
        except Exception as e:
            print(f"[ERREUR] Lecture du log : {e}")
    return events

def store_events_json(events):
    try:
        with open(JSON_FILE, "w") as f:
            json.dump(events, f, indent=4, ensure_ascii=False)
        print("[INFO] Événements sauvegardés dans JSON.")
    except Exception as e:
        print(f"[ERREUR] Sauvegarde JSON : {e}")

def store_events_sql(events):
    try:
        conn = sqlite3.connect(SQLITE_DB)
        c = conn.cursor()
        for event in events:
            c.execute("SELECT COUNT(*) FROM alerts WHERE timestamp = ? AND message = ?", (event["timestamp"], event["message"]))
            if c.fetchone()[0] == 0:
                c.execute("INSERT INTO alerts (timestamp, message) VALUES (?, ?)", (event["timestamp"], event["message"]))
        conn.commit()
        print("[INFO] Événements sauvegardés dans SQLite.")
    except sqlite3.Error as e:
        print(f"[ERREUR] SQLite : {e}")
    finally:
        conn.close()

def scan_ports(target_ip):
    try:
        print(f"Scan de ports sur {target_ip}...")
        result = subprocess.run(
            ["bash", "/home/sylvie/Projet_scripting_securise_sylvie/scan_ports.sh", target_ip],
            check=True, capture_output=True, text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Scan ports : {e}")
        print(f"stdout : {e.stdout}")
        print(f"stderr : {e.stderr}")
        return None

def analyze_scan_results(scan_file):
    try:
        result = subprocess.run(
            ['python3', './analyze_scan_results.py', scan_file],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(result.stderr)
    except Exception as e:
        print(f"[ERREUR] Analyse scan : {e}")

def run_bash_script(script_path):
    try:
        result = subprocess.run([script_path], check=True, text=True, capture_output=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"[ERREUR] Script Bash : {e}")

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
        print("[INFO] Email d'alerte envoyé.")
    except Exception as e:
        print(f"[ERREUR] Email : {e}")

def test_fail2ban_bruteforce(ip):
    print(f"[TEST] Lancement du bruteforce SSH simulé sur {ip}...")
    try:
        subprocess.run([
            "hydra", "-l", "root", "-P", "/home/sylvie/smallwordlist.txt", f"ssh://{ip}"
        ], check=False, capture_output=True, text=True)
    except Exception as e:
        print(f"[ERREUR] Échec du test bruteforce : {e}")

def check_fail2ban_status(ip):
    try:
        result = subprocess.run(["sudo", "fail2ban-client", "status", "sshd"],
                                capture_output=True, text=True)

        output = result.stdout
        print(output)

        banned_ips = None
        if "Banned IP list:" in output:
            banned_ips = output.split("Banned IP list:")[1].strip()
            banned_ips = banned_ips if banned_ips else "Aucune"
            print("[INFO] IPs bannies :", banned_ips)

            # Écriture dans le fichier de log
            with open(LOG_FILE, "a") as log:
                log.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - IPs bannies : {banned_ips}\n")

            # Envoi d'une alerte si des IPs sont bannies
            if banned_ips != "Aucune":
                send_alert_email("Alerte Fail2ban", f"IP(s) actuellement bannie(s) : {banned_ips}")

    except Exception as e:
        print(f"[ERREUR] Vérification Fail2ban : {e}")





def main():
    print("=== Initialisation des fichiers ===")
    initialize_files()

    print("=== Analyse des logs ===")
    events = parse_log_file()
    if events:
        store_events_json(events)
        store_events_sql(events)

    print("=== Vérification des mots de passe ===")
    username = "testuser"
    password = "Test@1234"
    generate_password_report(username, password)
    if not check_password_complexity(password)[0]:
        force_password_change(username)

    key = load_key()
    add_password('Gmail', 'mon_username', 'mon_password', key)
    creds = retrieve_password('Gmail', key)
    if creds:
        print(f"Service: {creds['username']}, Mot de passe: {creds['password']}")

    print("=== Lancement du scan de ports ===")
    ip = "192.168.1.125"
    results = scan_ports(ip)
    if results:
        with open("nmap_scan_results.txt", "w") as f:
            f.write(results)
        analyze_scan_results("nmap_scan_results.txt")

        print("=== Test du système de défense avec Fail2ban ===")
        test_fail2ban_bruteforce(ip)
        check_fail2ban_status(ip)

    print("=== Lancement du script utilisateur ===")
    run_bash_script("./gestion_utilisateur/gestion_utilisateur.sh")

    print("=== Sauvegarde et rotation des logs toutes les 10 minutes ===")
    try:
        while True:
            rotate_log()
            backup_files()
            time.sleep(600)
    except KeyboardInterrupt:
        print("\n[INFO] Surveillance interrompue par l'utilisateur.")

if __name__ == "__main__":
    main()
