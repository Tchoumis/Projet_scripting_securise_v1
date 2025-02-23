#!/bin/bash

# Fonction pour créer un nouvel utilisateur
create_toto() {
    local username=$1
    local password=$2
    local group=$3

    # Vérifier si l'utilisateur existe déjà
    if id "$username" &>/dev/null; then
        echo "L'utilisateur $username existe déjà."
    else
        # Créer l'utilisateur et l'ajouter au groupe
        useradd -m -g $group -s /bin/bash $username
        echo "$username:$password" | chpasswd

        # Forcer le changement de mot de passe au premier login
        chage -d 0 $username

        echo "Utilisateur $username créé et ajouté au groupe $group."
    fi
}

# Fonction pour modifier un utilisateur
modify_toto() {
    local username=$1
    local new_password=$2
    local new_group=$3    # Ajouter un groupe supplémentaire
    local new_shell=$4    # Nouveau shell (facultatif)

    # Vérifier si l'utilisateur existe avant de modifier
    if id "$username" &>/dev/null; then
        # Modifier le mot de passe de l'utilisateur
        echo "$username:$new_password" | chpasswd

        # Ajouter l'utilisateur à un groupe supplémentaire
        if [ -n "$new_group" ]; then
            # Vérifier si le groupe existe, sinon le créer
            if ! getent group "$new_group" > /dev/null; then
                echo "Le groupe $new_group n'existe pas. Création du groupe."
                groupadd "$new_group"
            fi
            usermod -aG "$new_group" "$username"
            echo "L'utilisateur $username a été ajouté au groupe $new_group."
        fi

        # Modifier le shell de l'utilisateur (optionnel)
        if [ -n "$new_shell" ]; then
            usermod -s "$new_shell" "$username"
            echo "Le shell de l'utilisateur $username a été changé en $new_shell."
        fi

        # Forcer le changement de mot de passe
        chage -d 0 $username

        echo "Mot de passe de $username modifié."
    else
        echo "L'utilisateur $username n'existe pas."
    fi
}

# Fonction pour supprimer un utilisateur
delete_user() {
    local username=$1

    # Vérifier si l'utilisateur existe avant la suppression
    if id "$username" &>/dev/null; then
        # Supprimer l'utilisateur et ses fichiers sans tenir compte du mail spool
        userdel -rf "$username"
        echo "Utilisateur $username supprimé."

        # Vérifier si le spool mail existe et le supprimer si nécessaire
        if [ -f "/var/mail/$username" ]; then
            rm -f "/var/mail/$username"
            echo "Spool mail de $username supprimé."
        fi
    else
        echo "L'utilisateur $username n'existe pas ou a déjà été supprimé."
    fi

    # Vérification après suppression pour s'assurer que l'utilisateur n'existe plus
    if id "$username" &>/dev/null; then
        echo "L'utilisateur $username existe toujours, il y a eu une erreur lors de la suppression."
    else
        echo "L'utilisateur $username a été correctement supprimé."
    fi
}

# Fonction pour vérifier si un utilisateur doit changer son mot de passe
check_password_expiry() {
    local username=$1
    local days_until_expiry=$2

    # Vérifier si l'utilisateur existe avant d'appliquer l'expiration
    if id "$username" &>/dev/null; then
        chage -M $days_until_expiry $username
        echo "Le mot de passe de $username expirera dans $days_until_expiry jours."
    else
        echo "L'utilisateur $username n'existe pas."
    fi
}

# Exemple d'appel des fonctions
# Créer un utilisateur
create_toto "testtoto" "toto@1234" "sudo"

# Modifier un utilisateur
modify_toto "testtoto" "abcd!123" "dev" "/bin/zsh"

# Supprimer un utilisateur
delete_user "testtoto"

# Vérifier l'expiration du mot de passe
check_password_expiry "testtoto" 30
