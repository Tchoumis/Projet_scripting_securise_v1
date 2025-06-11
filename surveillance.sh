#!/bin/bash

# ===============================================
# Configuration
FILES="/etc/passwd /etc/shadow /etc/ssh/sshd_config"
HASH_FILE="/home/sylvie/Projet_scripting_securise_sylvie/file_hashes.log"
CHANGE_LOG="/home/sylvie/Projet_scripting_securise_sylvie/hash_changes.log"
HASH_CMD="sha256sum"
INOTIFY_EVENTS="modify,create,delete,move"
LOG_FILE="/home/sylvie/Projet_scripting_securise_sylvie/logs/auth.log"
FAILED_LOGINS="/home/sylvie/Projet_scripting_securise_sylvie/logs/failed_logins.log"

# ===============================================
# Chargement et export des variables d'environnement
set -a
if [ -f /home/sylvie/Projet_scripting_securise_sylvie/.env ]; then
    source /home/sylvie/Projet_scripting_securise_sylvie/.env
else
    echo "Fichier .env introuvable !" >&2
    exit 1
fi
set +a

# ===============================================
# Vérification des commandes requises
for cmd in inotifywait $HASH_CMD python3; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Erreur : la commande '$cmd' n'est pas installée." >&2
        exit 1
    fi
done

# ===============================================
# Fonctions utilitaires

log_message() {
    local message="$1"
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $message" | tee -a "$CHANGE_LOG"
}

send_email_alert() {
    local message="$1"
    local subject="Alerte : Changement détecté dans un fichier sensible"
    local body="Un changement a été détecté dans un fichier sensible. Détails : $message"

    python3 - <<EOF
import yagmail
import os
user = os.getenv('SMTP_USER')
password = os.getenv('SMTP_PASSWORD')
recipient = os.getenv('ADMIN_EMAIL')

try:
    yag = yagmail.SMTP(user=user, password=password)
    yag.send(to=recipient, subject='$subject', contents='$body')
    print("Email envoyé avec succès.")
except Exception as e:
    print(f"Erreur lors de l'envoi de l'email : {e}")
EOF

    if [ $? -eq 0 ]; then
        log_message "L'email d'alerte a été envoyé avec succès."
    else
        log_message "Erreur lors de l'envoi de l'email."
    fi
}

initialize_hashes() {
    log_message "Initialisation des hachages..."
    > "$HASH_FILE"
    for file in $FILES; do
        if [ -f "$file" ]; then
            local file_hash
            file_hash=$($HASH_CMD "$file" | awk '{print $1}')
            echo "$file $file_hash" >> "$HASH_FILE"
        else
            log_message "Fichier non trouvé lors de l'initialisation : $file"
        fi
    done
}

update_hash() {
    local file="$1"
    if [ -f "$file" ]; then
        local new_hash
        new_hash=$($HASH_CMD "$file" | awk '{print $1}')
        grep -v "^$file " "$HASH_FILE" > "${HASH_FILE}.tmp" || true
        echo "$file $new_hash" >> "${HASH_FILE}.tmp"
        mv "${HASH_FILE}.tmp" "$HASH_FILE"
    else
        grep -v "^$file " "$HASH_FILE" > "${HASH_FILE}.tmp" || true
        mv "${HASH_FILE}.tmp" "$HASH_FILE"
    fi
}

get_stored_hash() {
    local file="$1"
    grep "^$file " "$HASH_FILE" | awk '{print $2}'
}

cleanup() {
    log_message "Arrêt du script et nettoyage."
    exit 0
}
trap cleanup SIGINT SIGTERM

# ===============================================
# Exécution principale

if [ ! -f "$HASH_FILE" ]; then
    initialize_hashes
fi

log_message "Démarrage de la surveillance des fichiers sensibles : $FILES"

# Lancer inotifywait et traiter les événements
inotifywait -m -e $INOTIFY_EVENTS $FILES --format '%w%f %e' | while read -r file event; do
    # Ignorer certains événements non pertinents
    if [[ "$event" =~ ATTRIB ]]; then
        continue
    fi

    if [[ "$event" =~ DELETE ]] || [[ "$event" =~ MOVED_FROM ]]; then
        log_message "Fichier supprimé ou déplacé : $file"
        update_hash "$file"
        continue
    fi

    if [ -f "$file" ]; then
        new_hash=$($HASH_CMD "$file" | awk '{print $1}')
        stored_hash=$(get_stored_hash "$file")

        if [ -z "$stored_hash" ]; then
            log_message "Nouveau fichier détecté : $file, hash : $new_hash"
            echo "$file $new_hash" >> "$HASH_FILE"
            send_email_alert "Nouveau fichier détecté : $file, hash : $new_hash"
        elif [ "$new_hash" != "$stored_hash" ]; then
            log_message "Modification détectée sur $file. Ancien hash : $stored_hash, Nouveau hash : $new_hash"
            update_hash "$file"
            send_email_alert "Modification détectée sur $file. Ancien hash : $stored_hash, Nouveau hash : $new_hash"
            # Appel au script python d'analyse (assure-toi qu'il existe et fonctionne)
            python3 /home/sylvie/Projet_scripting_securise_sylvie/analyse_surveillance.py
        else
            log_message "Aucune modification de hash pour $file (événement : $event)"
        fi
    else
        log_message "Fichier $file n'existe plus après l'événement."
        update_hash "$file"
    fi
done
