#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <target_ip>"
    exit 1
fi

# Cible de scan
TARGET=$1

# Affichage d'un message de démarrage
echo "Scanning ports on $TARGET..."

# Exécutez nmap pour scanner les ports ouverts
open_ports=$(nmap -p- --open --min-rate=1000 "$TARGET" | grep ^[0-9] | cut -d '/' -f 1)

# Vérifier les résultats du scan Nmap
if [ -z "$open_ports" ]; then
    echo "Aucun port ouvert trouvé sur $TARGET."
    exit 1
else
    echo "Ports ouverts trouvés sur $TARGET : $open_ports"
fi

# Scanner les services web (HTTP et HTTPS) avec Nikto
echo "Scanning web services on $TARGET with Nikto..."

# Scanner les ports HTTP (80) et HTTPS (443)
if [[ "$open_ports" =~ "80" || "$open_ports" =~ "443" ]]; then
    nikto -h "http://$TARGET"
else
    echo "Aucun service HTTP/HTTPS trouvé, skipping Nikto scan."
fi

# Tester la force brute sur les services SSH avec Hydra
echo "Testing SSH login with Hydra on $TARGET..."

WORDLIST="/home/sylvie/smallwordlist.txt"

if [[ "$open_ports" =~ "22" ]]; then
    if [ ! -f "$WORDLIST" ]; then
        echo "[ERREUR] Wordlist non trouvée : $WORDLIST"
        exit 1
    fi
    sudo hydra -l sylvie -P "$WORDLIST" -t 1 ssh://"$TARGET"
else
    echo "Aucun service SSH trouvé, skipping Hydra SSH brute force test."
fi
