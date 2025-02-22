#!/usr/bin/env python3
import os
import json
from cryptography.fernet import Fernet
import argparse

# Fichiers de stockage
KEY_FILE = "key.key"         # Fichier contenant la clé de chiffrement
DATA_FILE = "passwords.enc"  # Fichier chiffré contenant les mots de passe

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as key_file:
        key_file.write(key)
    print("Clé générée et sauvegardée dans", KEY_FILE)
    return key

def load_key():
    if not os.path.exists(KEY_FILE):
        return generate_key()
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

def encrypt_data(data, key):
    fernet = Fernet(key)
    data_bytes = json.dumps(data).encode()
    return fernet.encrypt(data_bytes)

def decrypt_data(token, key):
    fernet = Fernet(key)
    data_bytes = fernet.decrypt(token)
    return json.loads(data_bytes)

def load_passwords(key):
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "rb") as file:
        encrypted = file.read()
    return decrypt_data(encrypted, key)

def save_passwords(passwords, key):
    encrypted = encrypt_data(passwords, key)
    with open(DATA_FILE, "wb") as file:
        file.write(encrypted)

def add_password(service, username, password, key):
    passwords = load_passwords(key)
    passwords[service] = {"username": username, "password": password}
    save_passwords(passwords, key)
    print(f"Mot de passe pour '{service}' ajouté/mis à jour.")

def retrieve_password(service, key):
    passwords = load_passwords(key)
    if service in passwords:
        return passwords[service]
    else:
        print(f"Aucun mot de passe trouvé pour '{service}'.")
        return None

def main():
    parser = argparse.ArgumentParser(description="Gestionnaire de mots de passe sécurisé")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Commande pour ajouter un mot de passe
    add_parser = subparsers.add_parser("add", help="Ajouter ou mettre à jour un mot de passe")
    add_parser.add_argument("service", help="Nom du service (ex: Gmail)")
    add_parser.add_argument("username", help="Nom d'utilisateur")
    add_parser.add_argument("password", help="Mot de passe")

    # Commande pour récupérer un mot de passe
    get_parser = subparsers.add_parser("get", help="Récupérer un mot de passe")
    get_parser.add_argument("service", help="Nom du service (ex: Gmail)")

    args = parser.parse_args()
    key = load_key()

    if args.command == "add":
        add_password(args.service, args.username, args.password, key)
    elif args.command == "get":
        creds = retrieve_password(args.service, key)
        if creds:
            print(f"Service   : {args.service}")
            print(f"Username  : {creds['username']}")
            print(f"Password  : {creds['password']}")

if __name__ == "__main__":
    main()
