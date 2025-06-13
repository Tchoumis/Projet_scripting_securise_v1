# Projet de Sécurisation Système avec Python et Bash

Ce projet a pour objectif de créer une série de scripts en **Python** et **Bash** afin d'automatiser certaines tâches de sécurité sur un système Linux. Il inclut des outils pour la surveillance des fichiers sensibles, la gestion des mots de passe, la détection d'intrusions, et l'automatisation des mises à jour de sécurité.

## Description

Ce projet implémente une série de scripts en **Python** et **Bash** visant à améliorer la sécurité d'un système informatique à travers diverses tâches d'analyse, de surveillance et de gestion. Les principales fonctionnalités incluent la surveillance des fichiers sensibles, la gestion des mots de passe, la détection des ports ouverts et des services vulnérables, ainsi que l'automatisation de la gestion des utilisateurs.

## Fonctionnalités

### 1. Analyse et Surveillance de Fichiers Sensibles (Bash + Python)
- **Bash** : Surveille les fichiers sensibles (/etc/passwd, /etc/shadow, etc/ssh/ssh_config) en générant des hachages avec `sha256sum` ou `md5sum`.
- **Python** : Compare les hachages avec des versions précédentes pour détecter toute modification. Envoie des alertes et génère des rapports détaillés en cas de changement détecté.

**Exemple de flux de travail** :
- **Bash** : Vérifie les fichiers sensibles et génère un fichier de hachage.
- **Python** : Charge le fichier de hachage et compare avec les précédents. Si des changements sont détectés, génère un rapport.

### 2. Gestion de Mots de Passe (Bash + Python)
- **Python** : Chiffre et déchiffre les mots de passe en utilisant des bibliothèques comme `cryptography`.
- **Bash** : Automatise la gestion des fichiers chiffrés et effectue des sauvegardes régulières pour garantir la sécurité des mots de passe.

**Exemple de flux de travail** :
- **Python** : Gère la logique de stockage et de récupération des mots de passe (chiffrement et déchiffrement).
- **Bash** : Automatise les sauvegardes et gère les fichiers chiffrés.

### 3. Détection des Ports Ouverts et des Services Vulnérables (Bash + Python)
- **Bash** : Utilise des outils comme `nmap`, `netstat` pour scanner les ports ouverts sur un système.
- **Python** : Analyse les résultats du scan pour identifier les services vulnérables et génère des alertes en cas de détection de failles de sécurité.

**Exemple de flux de travail** :
- **Bash** : Exécute un scan avec `nmap, Nikto et hydra` pour identifier les ports ouverts, services vulnérables et attaque force brute.
- **Python** : Analyse les services trouvés, compare les versions avec une base de données de vulnérabilités, et génère des alertes si un service vulnérable est détecté.

### 4. Automatisation de la Gestion des Utilisateurs et Sécurité des Mots de Passe (Bash + Python)
- **Bash** : Utilise les commandes `useradd`, `usermod`, et `passwd` pour gérer les utilisateurs (création, modification, suppression).
- **Python** : Vérifie la complexité des mots de passe, force les utilisateurs à changer leur mot de passe après un certain temps et génère des rapports de conformité.

**Exemple de flux de travail** :
- **Bash** : Crée un nouvel utilisateur avec des permissions spécifiques.
- **Python** : Vérifie la complexité du mot de passe, applique des règles de sécurité (longueur, complexité), et génère un rapport de conformité.

### 5. Surveillance des Logs de Sécurité (auth.log) (Bash + Python)
- **Bash** : Surveille en temps réel le fichier `failed_auth_logins` pour détecter les échecs de connexion, les tentatives d'accès non autorisées et les comportements suspects en utilisant des commandes comme `grep`, `awk` et `tail`.
- **Python** : Analyse les échecs de connexion et génère des rapports détaillés. Si un nombre anormal d'échecs est détecté, il envoie une alerte par e-mail ou génère un rapport détaillé.

**Exemple de flux de travail** :
- **Bash** : Surveille `failed_auth_logins` pour détecter les échecs de connexion.
- **Python** : Analyse les événements et génère une alerte par e-mail ou crée un rapport détaillé.

### 6. Automatisation des Mises à Jour de Sécurité (Bash + Python)
- **Bash** : Exécute des commandes comme `apt-get update` ou `yum update` pour mettre à jour automatiquement les packages de sécurité du système.
- **Python** : Analyse les logs des mises à jour et génère un rapport détaillé sur les mises à jour appliquées, y compris les vulnérabilités corrigées.
### 7. Automatisation avec Cron
Afin d'exécuter ces tests à intervalles réguliers, l'automatisation via Cron permet d'améliorer l'efficacité et d'assurer une surveillance continue.

## Architecture

https://github.com/Tchoumis/Projet_scripting_securise_sylvie/blob/930092fe77b785b82cc7640624001b6ace2d4e47/Architecture.png


## Arborescence du Projet

```bash=
Projet_scripting_securise_sylvie/
├── .env                        # Variables d’environnement (ex : mots de passe, config email SMTP)
├── .gitignore                  # Fichier pour ignorer certains fichiers/dossiers dans Git
├── .venv/                      # Environnement virtuel Python isolé
│
├── alerts.json                 # Fichier JSON contenant les alertes détectées
├── analyse_logs.py             # Script Python pour analyser auth.log et syslog
├── analyse_logs.sh             # Script Bash de surveillance temps réel des logs
├── analyse-surveillance.py     # Script Python pour la détection de tentatives d'intrusion
├── analyze_scan_results.py     # Analyse des résultats de scan de ports/services (via Nmap)
│
├── file_hashes.log             # Journal des hachages SHA256 des fichiers sensibles
├── hash_changes.log            # Journal des modifications détectées sur fichiers critiques
├── key.key                     # Clé symétrique utilisée pour le chiffrement/déchiffrement
│
├── gestionnaire_mdp.py         # Gestionnaire de mots de passe sécurisé (avec chiffrement)
├── sauvegarde.py               # Script Python de sauvegarde automatique des mots de passe
├── passwords.enc               # Fichier chiffré contenant les mots de passe enregistrés
│
├── gestion_utilisateur/        # Dossier de gestion des utilisateurs
│   ├── gestion_mdp.py          # Vérification des règles de complexité des mots de passe
│   └── gestion_utilisateur.sh  # Script Bash pour gérer les utilisateurs système
│
├── main.py                     # Script principal orchestrant l’exécution des autres scripts
├── readme.md                   # Documentation du projet
├── requirements.txt            # Dépendances Python à installer via pip
├── scan_ports.sh               # Script Bash pour scanner les ports et services (Nmap)
├── surveillance.sh             # Script Bash de surveillance des connexions SSH échouées
├── maj_securite.sh              # Mise à jour automatique des paquets système
├── maj_securite.sh              # Mise à jour automatique des paquets système

```

### Système
- **Kali Linux** : Ce projet est conçu pour fonctionner sur Kali Linux, une distribution spécialisée dans les tests de sécurité.
- Outils nécessaires:
  - `nmap` : Outil de scan réseau.
  - `nikto` : Scanner de vulnérabilités web.
  - `hydra` : Outil de bruteforce pour tester les mots de passe.
  - `fail2ban` : Utilitaire de sécurité pour bloquer les adresses IP après un certain nombre de tentatives de connexion échouées.

### Dépendances Python
Pour installer les dépendances nécessaires à Python, suivez les étapes ci-dessous.

1. Installez les paquets nécessaires pour l'envoi d'e-mails et les notifications :
   ```bash
   sudo apt-get install mailutils
   sudo apt-get install notify
   sudo apt-get install yagmail
   sudo apt install inotify-tools
   ```

Créez un mot de passe d'application pour l'envoi d'e-mails.

Installez Python et créez un environnement virtuel:   
```bash
sudo apt install python3.13-venv
python3 -m venv venv
source venv/bin/activate
```

Installez toutes les dépendances Python requises en utilisant le fichier requirements.txt:
```bash
pip install -r requirements.txt
```

pour utiliser un fichier .env avec python-dotenv
```bash
pip install python-dotenv
```

Contenu du fichier .venv
```bash
LOG_FILE=/home/sylvie/Projet_scripting_securise_sylvie/hash_changes.log
JSON_FILE=/home/sylvie/Projet_scripting_securise_sylvie/alerts.json
SQLITE_DB=/var/log/alerts.db

ADMIN_EMAIL=e.mail Admin
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=e.mail User
SMTP_PASSWORD="mot de passe_application"
```


Créer un fichier wordlist pour Hydra, avec quelques mots de passe simples, pour les tests
```bash
echo -e "password\n123456\nadmin\nroot\nsylvie" > /home/sylvie/smallwordlist.txt
chmod 600 /home/sylvie/smallwordlist.txt
```
wordlist plus complète
```bash
locate rockyou.txt

sudo gzip -d /usr/share/wordlists/rockyou.txt.gz
```

```bash
ls -l /usr/share/wordlists/rockyou.txt
```

Avant de commencer l'exécution des scripts, veuillez suivre ces étapes importantes:

Avant de lancer les scripts, il est essentiel de personnaliser certains paramètres spécifiques à votre environnement:

- **Chemin des fichiers** : Assurez-vous que les chemins des fichiers référencés dans les scripts sont corrects. Par exemple, les fichiers de log, les répertoires de sauvegarde, etc.
- **Adresse e-mail** : Si des alertes par e-mail doivent être envoyées, vous devrez configurer votre adresse e-mail dans les scripts.
- **Adresse IP** : Vérifiez que l'adresse IP du système cible ou du réseau est correctement définie dans les fichiers de configuration si nécessaire.

### 2. **Permissions des fichiers**
Certains scripts nécessitent des permissions spécifiques pour pouvoir s'exécuter correctement, en particulier les scripts Bash qui interagissent avec des fichiers systèmes ou des fichiers de log. 
```bash
sudo chmod +x /chemin/vers/votre/nom_du_scrip.sh
```

Exécution individuelle des fichiers .py
```bash
python3 /chemin/vers/votre/nom_du_script.py
```
# Description des fichiers main.py et analyse_surveillance.py

---

## main.py

- **Rôle principal** : Point d'entrée général du projet.
- **Fonctions clés** :  
  - Exécution de tâches automatisées : gestion des utilisateurs, contrôle des mots de passe, scan de ports réseau.    
  - Récupération des résultats et traitement des retours (ex : analyse des scans, gestion des erreurs).  
  - Orchestration globale des sous-tâches du projet.

- **Usage** :  
  - À lancer pour démarrer l’ensemble des opérations principales du projet de sécurité.  
  - Script global qui englobe plusieurs sous-tâches.

---

## analyse_surveillance.py

- **Rôle principal** : Analyse des fichiers de logs de sécurité (ex : échecs de connexion, changements système).
- **Fonctions clés** :  
  - Lecture et parsing des logs (ex : `auth.log`, `hash_changes.log`).  
  - Extraction des événements suspects ou d’échecs de connexion.  
  - Génération de rapports (JSON, base de données SQLite).  
  - Envoi d’alertes ou notifications en cas d’anomalies.

- **Usage** :  
  - À lancer pour analyser en détail les logs, détecter des comportements anormaux ou attaques potentielles.  
  - Script spécialisé dans l’analyse des événements.

---

Après execution du fichier: analyse-surveillance.py

les événement détecté  sont dans le fichier hash_changes.log.

## automatisation avec cron

fichier crontab
```bash
crontab -e
```
Fichier Bash tous les jours à 2h du matin, exemple:
```bash
0 2 * * * /bin/bash /home/sylvie/Projet_scripting_securise_sylvie/surveillance.sh
```

Fichier ptyhon tous les jours à 8h30 du matin, exemple:
```bash
30 8 * * * /usr/bin/python3 /home/sylvie/Projet_scripting_securise_sylvie/analyse-surveillance.py
```
## Mise en service automatique de la surveillance
Pour garantir une surveillance continue des fichiers sensibles dès le démarrage du système, intégré le script surveillance.sh  comme service systemd.

fichier de configuration /etc/systemd/system/surveillance_fichiers.service

```bash=
[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/home/sylvie/Projet_scripting_securise_sylvie
ExecStart=/bin/bash /home/sylvie/Projet_scripting_securise_sylvie/surveillance.sh
Restart=always
RestartSec=5
EnvironmentFile=/home/sylvie/Projet_scripting_securise_sylvie/.env
StandardOutput=journal
StandardError=journal
KillMode=process
```

Enregistrement et activation du service: 

```bash=
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable surveillance_fichiers.service
sudo systemctl start surveillance_fichiers.service
```
