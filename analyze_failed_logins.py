import re
import os
import yagmail
from collections import defaultdict
from datetime import datetime

# Configuration des chemins de fichiers
LOG_FILE = "/home/sylvie/Projet_scripting_securise/logs/auth.log"  # Chemin du fichier de log à surveiller
ALERT_THRESHOLD = 5  # Seuil de tentatives échouées avant d'envoyer une alerte (ex : 5 tentatives)
ALERT_EMAIL = "sylviekelkeu@gmail.com"  # Remplacez par votre email
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Récupérer le mot de passe email depuis les variables d'environnement

# Expression régulière pour détecter les échecs de connexion
failed_login_pattern = r"Failed password for .* from (\S+)"

# Fonction pour envoyer une alerte par email
def send_alert(subject, body):
    try:
        yag = yagmail.SMTP(user=ALERT_EMAIL, password=EMAIL_PASSWORD)
        yag.send(to=ALERT_EMAIL, subject=subject, contents=body)
        print(f"Alert sent to {ALERT_EMAIL}")
    except Exception as e:
        print(f"Error sending alert: {e}")

# Fonction pour analyser les logs
def analyze_logs():
    # Dictionnaire pour compter les échecs par adresse IP
    failed_attempts = defaultdict(int)
    
    # Lecture du fichier de logs
    with open(LOG_FILE, 'r') as f:
        for line in f:
            # Chercher les tentatives de connexion échouées
            match = re.search(failed_login_pattern, line)
            if match:
                ip_address = match.group(1)  # Récupérer l'adresse IP
                failed_attempts[ip_address] += 1
    
    # Vérification des adresses IP avec des tentatives échouées au-delà du seuil
    for ip, count in failed_attempts.items():
        if count >= ALERT_THRESHOLD:
            alert_subject = f"Alerte : Tentatives de connexion échouées multiples de {ip}"
            alert_body = f"Il y a eu {count} tentatives échouées de connexion depuis l'adresse IP {ip}.\n\nVérifiez si cela constitue une tentative d'attaque par force brute."
            send_alert(alert_subject, alert_body)

# Lancer l'analyse des logs
if __name__ == "__main__":
    analyze_logs()
