#!/bin/bash

# Vérifiez que l'IP cible est fournie
if [ -z "$1" ]; then
    echo "Usage: $0 <target_ip>"
    exit 1
fi

# Cible de scan
TARGET=$1

# Affichage d'un message de démarrage
echo "Scanning ports on $TARGET..."

# Exécutez nmap pour scanner les ports ouverts
nmap -p- --open $TARGET
