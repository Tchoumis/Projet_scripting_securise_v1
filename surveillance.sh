#!/bin/bash

# ===============================================
# Configuration
FILES="/etc/passwd /etc/shadow /etc/ssh/sshd_config"
HASH_FILE="/home/sylvie/Projet_scripting_securise/file_hashes.log"  # Mettez à jour ce chemin si vous voulez utiliser un chemin relatif ou spécifique.
CHANGE_LOG="/home/sylvie/Projet_scripting_securise/hash_changes.log"  # Mettez à jour ce chemin pour correspondre au fichier log Python.
HASH_CMD="sha256sum"
INOTIFY_EVENTS="modify,create,delete,move"


source /home/sylvie/Projet_scripting_securise/.env  # Remplacez par le chemin correct si nécessaire

# ===============================================
# Vérification des commandes requises
# ===============================================
for cmd in inotifywait $HASH_CMD; do
    if ! command -v $cmd >/dev/null 2>&1; then
        echo "Erreur : la commande '$cmd' n'est pas installée." >&2
        exit 1
    fi
done

# ===============================================
# Fonctions utilitaires
# ===============================================

# Affiche et enregistre un message avec horodatage.
log_message() {
    local message="$1"
    echo "$(date +'%Y-%m-%d %H:%M:%S') - $message" | tee -a "$CHANGE_LOG"
}

# Envoi d'une alerte par email avec yagmail


send_email_alert() {
    local message="$1"
    local subject="Alerte : Changement détecté dans un fichier sensible"
    local body="Un changement a été détecté dans un fichier sensible. Détails : $message"
    
    python3 -c "
import yagmail
import os

# Charger les variables d'environnement
user = 'sylviekelkeu@gmail.com'  # Remplacez par votre email Gmail
password = os.getenv('EMAIL_PASSWORD')  # Récupère le mot de passe depuis .env

# Envoyer l'email
yag = yagmail.SMTP(user=user, password=password)
yag.send(to='sylviekelkeu@gmail.com', subject='$subject', contents='$body')
    "
    if [ $? -eq 0 ]; then
        log_message "L'email d'alerte a été envoyé avec succès."
    else
        log_message "Erreur lors de l'envoi de l'email."
    fi
}


# Initialise le fichier de hachages en calculant l'empreinte de chaque fichier.
initialize_hashes() {
    log_message "Initialisation des hachages..."
    > "$HASH_FILE"  # Vider le fichier existant
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

# Met à jour le hachage d'un fichier dans le fichier de référence.
update_hash() {
    local file="$1"
    if [ -f "$file" ]; then
        local new_hash
        new_hash=$($HASH_CMD "$file" | awk '{print $1}')
        grep -v "^$file " "$HASH_FILE" > "${HASH_FILE}.tmp"
        echo "$file $new_hash" >> "${HASH_FILE}.tmp"
        mv "${HASH_FILE}.tmp" "$HASH_FILE"
    else
        # Si le fichier n'existe plus, on retire son entrée.
        grep -v "^$file " "$HASH_FILE" > "${HASH_FILE}.tmp"
        mv "${HASH_FILE}.tmp" "$HASH_FILE"
    fi
}

# Récupère le hachage enregistré pour un fichier donné.
get_stored_hash() {
    local file="$1"
    grep "^$file " "$HASH_FILE" | awk '{print $2}'
}

# Gestion propre de l'arrêt du script.
cleanup() {
    log_message "Arrêt du script et nettoyage."
    exit 0
}
trap cleanup SIGINT SIGTERM

# ===============================================
# Exécution principale
# ===============================================

# Création du fichier de hachages s'il n'existe pas.
if [ ! -f "$HASH_FILE" ]; then
    initialize_hashes
fi

log_message "Démarrage de la surveillance des fichiers sensibles : $FILES"

# Surveillance en temps réel à l'aide d'inotifywait.
inotifywait -m -e $INOTIFY_EVENTS $FILES --format '%w%f %e' | while read -r file event; do
    # Ignorer les événements de type 'attrib' qui ne sont pas des changements réels.
    if [[ "$event" =~ ATTRIB ]]; then
        continue
    fi

    # Gérer la suppression ou le déplacement hors de la zone surveillée.
    if [[ "$event" =~ DELETE ]] || [[ "$event" =~ MOVED_FROM ]]; then
        log_message "Fichier supprimé ou déplacé : $file"
        update_hash "$file"
        continue
    fi

    # Pour les fichiers créés, modifiés ou déplacés dans la zone surveillée.
    if [ -f "$file" ]; then
        new_hash=$($HASH_CMD "$file" | awk '{print $1}')
        stored_hash=$(get_stored_hash "$file")
        
        if [ -z "$stored_hash" ]; then
            log_message "Nouveau fichier détecté : $file, hash : $new_hash"
            echo "$file $new_hash" >> "$HASH_FILE"
            send_email_alert "Nouveau fichier détecté : $file, hash : $new_hash"  # Envoi d'email seulement pour un nouveau fichier
        elif [ "$new_hash" != "$stored_hash" ]; then
            log_message "Modification détectée sur $file. Ancien hash : $stored_hash, Nouveau hash : $new_hash"
            update_hash "$file"
            send_email_alert "Modification détectée sur $file. Ancien hash : $stored_hash, Nouveau hash : $new_hash"  # Envoi d'email seulement pour modification
        else
            log_message "Aucune modification de hash pour $file (événement : $event)"
        fi
    else
        log_message "Fichier $file n'existe plus après l'événement."
        update_hash "$file"
    fi
done
