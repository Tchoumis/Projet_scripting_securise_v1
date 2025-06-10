import os
import json
import sqlite3
from datetime import datetime
import time
from sauvegarde import rotate_log, backup_files
from gestionnaire_mdp import add_password, retrieve_password, load_key
import subprocess
from gestion_utilisateur.gestion_mdp import check_password_complexity, generate_password_report, force_password_change
from dateutil import parser
import logging


# =======================================================
# Configuration des fichiers
# =======================================================
LOG_FILE = "/home/sylvie/Projet_scripting_securise/hash_changes.log"
JSON_FILE = "/home/sylvie/Projet_scripting_securise/alerts.json"
SQLITE_DB = "/home/sylvie/sqlite_db/alerts.db"


logging.basicConfig(level=logging.INFO)
# =======================================================
# Initialisation des fichiers nécessaires
# =======================================================
def initialize_files():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(JSON_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(SQLITE_DB), exist_ok=True)

    if not os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'w'): pass
            print(f"[INFO] Fichier de log créé : {LOG_FILE}")
        except PermissionError:
            print(f"[ERROR] Permission refusée pour créer le fichier de log : {LOG_FILE}")

    if not os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'w'): pass
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
            print(f"[INFO] Base de données SQLite créée : {SQLITE_DB}")
        except PermissionError:
            print(f"[ERROR] Permission refusée pour créer la base SQLite : {SQLITE_DB}")

# =======================================================
# Analyse du fichier de log
# =======================================================

def parse_log_file():
    events = []
    error_lines = []

    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if " - " in line:
                    parts = line.split(" - ", 1)
                    if len(parts) == 2:
                        timestamp_str, message = parts
                        try:
                            # Tente de parser la date
                            datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            events.append({"timestamp": timestamp_str, "message": message})
                        except ValueError:
                            # Enregistre les lignes avec des dates invalides
                            error_lines.append(line)
                            logging.warning(f"Format de date invalide dans la ligne : {line}")

        # Sauvegarde les lignes erronées dans un fichier
        if error_lines:
            with open("log_errors.txt", "w") as err_file:
                err_file.write("\n".join(error_lines))
            logging.info(f"{len(error_lines)} lignes avec des dates invalides enregistrées dans 'log_errors.txt'.")

    except Exception as e:
        logging.error(f"Échec de la lecture du fichier log : {e}")

    return events


# =======================================================
# Sauvegarde dans JSON
# =======================================================
def store_events_json(events):
    try:
        with open(JSON_FILE, "w", encoding='utf-8') as f:
            json.dump(events, f, indent=4, ensure_ascii=False)
        print(f"[INFO] Événements enregistrés dans : {JSON_FILE}")
    except Exception as e:
        print(f"[ERROR] Enregistrement JSON échoué : {e}")

# =======================================================
# Sauvegarde dans SQLite
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
        print(f"[INFO] Événements enregistrés dans la base SQLite : {SQLITE_DB}")
    except sqlite3.Error as e:
        print(f"[ERROR] Insertion dans SQLite échouée : {e}")
    finally:
        if conn:
            conn.close()

# =======================================================
# Fonction principale
# =======================================================
def main():
    initialize_files()

    print("[INFO] Analyse du fichier de log...")
    events = parse_log_file()

    if not events:
        print("[INFO] Aucun événement détecté.")
        return

    print(f"[INFO] {len(events)} événement(s) détecté(s).")
    store_events_json(events)
    store_events_sql(events)

if __name__ == "__main__":
    main()
