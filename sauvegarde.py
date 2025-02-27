import os
import shutil
import gzip
from datetime import datetime

# =======================================================
# Configuration des fichiers
# =======================================================
LOG_FILE = "/home/sylvie/Projet_scripting_securise/hash_changes.log"
BACKUP_DIR = "/home/sylvie/Projet_scripting_securise/backups/"
MAX_LOG_SIZE = 10 * 1024 * 1024
DATE_FORMAT = "%Y%m%d_%H%M%S"

# Créer les répertoires nécessaires si ils n'existent pas
os.makedirs(BACKUP_DIR, exist_ok=True)

# Fonction de rotation des logs
def rotate_log():
    """
    Vérifie la taille du fichier de log et effectue une rotation si nécessaire.
    """
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
        # Crée un nom pour le fichier de log compressé avec la date et l'heure actuelle
        timestamp = datetime.now().strftime(DATE_FORMAT)
        archive_log = os.path.join(BACKUP_DIR, f"{os.path.basename(LOG_FILE)}.{timestamp}.gz")
        
        # Compresser le fichier de log actuel et le renommer
        with open(LOG_FILE, 'rb') as f_in:
            with gzip.open(archive_log, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Vider le fichier de log
        with open(LOG_FILE, 'w'):
            pass
        
        print(f"[INFO] Rotation du fichier de log effectuée. Nouveau fichier : {archive_log}")

# Fonction pour effectuer une sauvegarde de fichiers importants
def backup_files():
    """
    Effectue une sauvegarde des fichiers importants.
    """
    files_to_backup = [
        "/etc/passwd", "/etc/shadow", "/etc/ssh/sshd_config",
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            # Créer un nom de fichier pour la sauvegarde
            timestamp = datetime.now().strftime(DATE_FORMAT)
            backup_file = os.path.join(BACKUP_DIR, f"{os.path.basename(file)}.{timestamp}.bak")
            
            try:
                # Copier le fichier dans le répertoire de sauvegarde
                shutil.copy2(file, backup_file)
                print(f"[INFO] Sauvegarde effectuée : {backup_file}")
            except PermissionError:
                print(f"[ERROR] Permission refusée pour sauvegarder le fichier : {file}")
            except Exception as e:
                print(f"[ERREUR] Échec de la sauvegarde du fichier {file} : {e}")
        else:
            print(f"[WARNING] Le fichier n'existe pas, impossible de le sauvegarder : {file}")

# Fonction principale
def main():
    # Effectuer la rotation des logs
    rotate_log()
    
    # Effectuer la sauvegarde des fichiers importants
    backup_files()

if __name__ == "__main__":
    main()
