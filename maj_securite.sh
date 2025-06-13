#!/bin/bash

# Fichier de log des mises à jour
LOG_FILE="/home/sylvie/Projet_scripting_securise_sylvie/update_log.txt"

# Met à jour la liste des paquets et installe les mises à jour de sécurité
echo "==== $(date '+%Y-%m-%d %H:%M:%S') - Début mise à jour de sécurité ====" >> "$LOG_FILE"
apt-get update >> "$LOG_FILE" 2>&1
apt-get upgrade -y >> "$LOG_FILE" 2>&1
echo "==== Fin mise à jour ====" >> "$LOG_FILE"
