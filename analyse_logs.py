import os
import re
import subprocess

# Chemins des fichiers de log
auth_log = "/var/log/auth.log"
syslog_journal_cmd = "journalctl -u ssh.service"

# Fonction pour analyser un fichier de log
def analyse_log(file_path, output_file, is_journal=False):
    if not is_journal and not os.path.exists(file_path):
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        return

    logs = []
    if is_journal:
        # Utiliser journalctl pour obtenir les logs
        try:
            logs = subprocess.check_output(syslog_journal_cmd, shell=True).decode('utf-8').splitlines()
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de journalctl: {e}")
            return
    else:
        with open(file_path, 'r') as f:
            logs = f.readlines()

    failed_logins = []

    # Chercher les lignes correspondant à "Failed password"
    for line in logs:
        if "Failed password" in line:
            failed_logins.append(line)

    # Écrire les tentatives échouées dans un fichier
    with open(output_file, 'w') as out_file:
        for line in failed_logins:
            out_file.write(line)

    print(f"Analyse terminée. Les résultats sont enregistrés dans '{output_file}'.")

# Analyser le fichier auth.log pour les tentatives échouées
analyse_log(auth_log, "failed_auth_logins_python.txt")

# Analyser les logs SSH via journalctl pour les tentatives échouées
analyse_log("", "failed_syslog_logins_python.txt", is_journal=True)

# Afficher un résumé des résultats
def display_summary():
    print("\nRésumé des tentatives échouées:")
    print("-------------------------------")

    print("Tentatives échouées dans auth.log:")
    with open("failed_auth_logins_python.txt", 'r') as f:
        print(f.read())

    print("-------------------------------")
    print("Tentatives échouées dans syslog (via journalctl):")
    with open("failed_syslog_logins_python.txt", 'r') as f:
        print(f.read())

# Appel de la fonction display_summary() si tu souhaites afficher directement un résumé
# display_summary()
