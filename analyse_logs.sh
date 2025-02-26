#!/bin/bash

# Fichiers de log à analyser
AUTH_LOG="/var/log/auth.log"
SYSLOG_JOURNAL="journalctl -u ssh.service"

# Vérification de l'existence des fichiers de log
if [ ! -f "$AUTH_LOG" ]; then
  echo "Erreur: Le fichier $AUTH_LOG n'existe pas ou est inaccessibile."
  exit 1
fi

# Analyser /var/log/auth.log pour les tentatives de connexion échouées
echo "Analyse de /var/log/auth.log pour les tentatives de connexion échouées:"
grep "Failed password" $AUTH_LOG | awk '{print $1, $2, $3, $0}' > failed_auth_logins.txt
echo "Les tentatives échouées de connexion ont été enregistrées dans 'failed_auth_logins.txt'"

# Analyser les journaux SSH via journalctl pour les tentatives d'accès échouées
echo "Analyse des journaux SSH via journalctl pour les tentatives d'accès échouées:"
$SYSLOG_JOURNAL | grep "Failed password" | awk '{print $1, $2, $3, $0}' > failed_syslog_logins.txt
echo "Les tentatives échouées dans les journaux SSH ont été enregistrées dans 'failed_syslog_logins.txt'"

# Afficher un résumé des résultats
echo "Résumé des tentatives échouées :"
echo "-------------------------------"
echo "Tentatives échouées dans auth.log:"
head -n 10 failed_auth_logins.txt
echo "-------------------------------"
echo "Tentatives échouées dans syslog (via journalctl) :"
head -n 10 failed_syslog_logins.txt
