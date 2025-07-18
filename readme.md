# Projet : Scripting de sécurité

## Objectif

Développer une suite de scripts en **Python** et **Bash** pour automatiser des tâches de sécurité sur un système Linux. Ces outils permettent de renforcer 
la protection du système grâce à la surveillance, la détection, la gestion des utilisateurs et l'automatisation des mises à jour.
---
## Fonctionnalités principales

### 1. Surveillance de fichiers sensibles
- **Bash** : Génération de hachages (`sha256sum`) sur des fichiers critiques (`/etc/passwd`, `/etc/shadow`, etc.).
- **Python** : Comparaison automatique avec les anciens hachages, génération d’alertes et de rapports en cas de modification.

### 2. Gestion sécurisée des mots de passe
- **Python** : Chiffrement/déchiffrement via la bibliothèque `cryptography`.
- **Bash** : Sauvegardes automatisées des fichiers chiffrés.

### 3. Détection des ports ouverts et services vulnérables
- **Bash** : Scans avec `nmap`, `nikto` et `hydra`.
- **Python** : Analyse des résultats, identification de failles connues, génération d’alertes.

### 4. Automatisation de la gestion des utilisateurs
- **Bash** : Création et modification d’utilisateurs avec `useradd`, `usermod`, `passwd`.
- **Python** : Vérification de la complexité des mots de passe, application de règles de sécurité, rapports de conformité.

### 5. Surveillance des logs de sécurité
- **Bash** : Analyse en temps réel des échecs de connexion via `auth.log`.
- **Python** : Détection d’anomalies (ex : brute-force), génération de rapports et alertes par e-mail.

### 6. Mises à jour de sécurité automatisées
- **Bash** : Mise à jour système.
- **Python** : Analyse des logs de mise à jour, rapport des correctifs appliqués.

### 7. Planification automatique avec Cron
Tous les scripts sont exécutés régulièrement grâce à des tâches planifiées via **Cron**, garantissant une surveillance continue.
---

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
├── requirements.txt            # Dépendances Python à installer
├── scan_ports.sh               # Script Bash pour scanner les ports et services
├── surveillance.sh             # Script Bash de surveillance des connexions SSH échouées
├── maj_securite.sh              # Mise à jour automatique des paquets système
```
### Système
  - `nmap` : Outil de scan réseau.
  - `nikto` : Scanner de vulnérabilités web.
  - `hydra` : Outil de bruteforce pour tester les mots de passe.
  - `fail2ban` : Utilitaire de sécurité pour bloquer les adresses IP après un certain nombre de tentatives de connexion échouées.
### Dépendances Python
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
Pour utiliser un fichier .env avec python-dotenv
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

wordlist plus complète
```bash
locate rockyou.txt
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz
```
```bash
ls -l /usr/share/wordlists/rockyou.txt
```

- **Chemin des fichiers** : Assurez-vous que les chemins des fichiers référencés dans les scripts sont corrects. Par exemple, les fichiers de log, les répertoires de sauvegarde, etc.
- **Adresse e-mail** : Si des alertes par e-mail doivent être envoyées, vous devrez configurer votre adresse e-mail dans les scripts.
- **Adresse IP** : Vérifiez que l'adresse IP du système cible ou du réseau est correctement définie dans les fichiers de configuration si nécessaire.

### 2. **Permissions des fichiers**
Certains scripts nécessitent des permissions spécifiques pour pouvoir s'exécuter correctement. 

**Exécution:**
```bash
sudo chmod +x /chemin/vers/votre/nom_du_scrip.sh
```

Fichiers .py
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
  - Lecture des logs (ex : `auth.log`, `hash_changes.log`).  
  - Extraction des événements suspects ou d’échecs de connexion.  
  - Génération de rapports (JSON, base de données SQLite).  
  - Envoi d’alertes ou notifications en cas d’anomalies.

- **Usage** :  
  - À lancer pour analyser en détail les logs, détecter des comportements anormaux ou attaques potentielles.  
  - Script spécialisé dans l’analyse des événements.

---

Après execution du fichier: analyse-surveillance.py, les événement détecté  sont dans le fichier hash_changes.log.

## automatisation avec cron

Fichier crontab
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

Fichier de configuration /etc/systemd/system/surveillance_fichiers.service

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


