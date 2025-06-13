import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

LOG_FILE = "/home/sylvie/Projet_scripting_securise_sylvie/update_log.txt"

def send_update_report():
    if not os.path.exists(LOG_FILE):
        print("Fichier de log non trouvé.")
        return

    with open(LOG_FILE, "r") as f:
        content = f.read()

    message = MIMEText(content)
    message["Subject"] = f"Rapport de mise à jour - {datetime.now().strftime('%Y-%m-%d')}"
    message["From"] = SMTP_USER
    message["To"] = ADMIN_EMAIL

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, ADMIN_EMAIL, message.as_string())
        server.quit()
        print("Rapport envoyé avec succès.")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")

if __name__ == "__main__":
    send_update_report()
