import smtplib
from email.mime.text import MIMEText

# Paramètres de connexion
user = 'sylviekelkeu@gmail.com'  # Votre adresse email Gmail
password = 'wprm lwku tsmd vnyq'  # Mot de passe d'application Gmail

# Informations sur l'email
subject = "Test Email"
body = "Ceci est un test de l'envoi d'un email depuis le script."

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = user
msg['To'] = user

try:
    # Connexion au serveur SMTP de Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()  # Démarrer le chiffrement TLS
    server.login(user, password)
    server.sendmail(user, user, msg.as_string())
    server.quit()
    print("Email envoyé avec succès !")
except Exception as e:
    print(f"Erreur lors de l'envoi de l'email : {e}")
