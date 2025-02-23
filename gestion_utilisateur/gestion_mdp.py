import re
import subprocess
from datetime import datetime

# Fonction pour vérifier la complexité du mot de passe
def check_password_complexity(password):
    # Critères de sécurité du mot de passe
    min_length = 8
    complexity_pattern = re.compile(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    
    if len(password) < min_length:
        return False, "Le mot de passe doit contenir au moins 8 caractères."
    
    if not complexity_pattern.match(password):
        return False, "Le mot de passe doit contenir une majuscule, une minuscule, un chiffre et un caractère spécial."

    return True, "Le mot de passe est conforme."

# Fonction pour forcer le changement de mot de passe
def force_password_change(username):
    try:
        subprocess.run(["sudo", "chage", "-d", "0", username], check=True)
        print(f"Le mot de passe de {username} a été réinitialisé, il doit changer lors de la prochaine connexion.")
    except subprocess.CalledProcessError:
        print(f"Erreur lors du réinitialisation du mot de passe pour {username}.")

# Fonction pour générer un rapport de conformité des mots de passe
def generate_password_report(username, password):
    is_valid, message = check_password_complexity(password)
    with open("password_report.txt", "a") as report_file:
        report_file.write(f"{datetime.now()} - Utilisateur: {username}, Validité: {is_valid}, Message: {message}\n")
    if not is_valid:
        print(f"[ALERTE] {username} - {message}")

# Exemple d'utilisation
username = "testuser"
password = "Test@1234"

# Vérifier la complexité du mot de passe
generate_password_report(username, password)

# Si le mot de passe n'est pas conforme, forcer le changement
if not check_password_complexity(password)[0]:
    force_password_change(username)
