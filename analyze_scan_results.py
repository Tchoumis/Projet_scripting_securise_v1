import sys
import re

# Base de données de vulnérabilités (exemple, à remplacer par une vraie base ou une API)
VULNERABLE_SERVICES = {
    'vsftpd': ['3.0.5'],  # version vulnérable
    'openssh': ['9.9p1'],  # version vulnérable
    'apache': ['2.4.1', '2.4.2'],  # exemple d'ajout d'un autre service
    'ftp': [],  # Le service FTP est vulnérable indépendamment de la version
    'ssh': []  # Le service SSH est vulnérable indépendamment de la version
}

# Fonction pour analyser les résultats du scan NMAP
def analyze_scan_results(scan_file):
    with open(scan_file, 'r') as file:
        data = file.read()

    # Affichage du contenu du fichier pour vérification
    print("Contenu du fichier :")
    print(data)
    
    # Recherche des services et versions trouvées par NMAP
    services = re.findall(r'(\d+/tcp)\s+open\s+([a-zA-Z0-9\-]+)\s+(\d+\.\d+\.\d+\.\d+)', data)
    services_no_version = re.findall(r'(\d+/tcp)\s+open\s+([a-zA-Z0-9\-]+)', data)  # Services sans version
    
    vulnerable_services = []

    # Traiter les services trouvés avec une version
    for port, service, version in services:
        print(f"Service trouvé : {service} (version {version}) sur {port}")
        
        # Vérifier si le service est vulnérable
        if service.lower() in VULNERABLE_SERVICES:
            if version in VULNERABLE_SERVICES[service.lower()]:
                print(f"ALERTE : {service} version {version} est vulnérable !")
                vulnerable_services.append(f"{service} version {version} sur {port}")
    
    # Traiter les services trouvés sans version
    for port, service in services_no_version:
        print(f"Service trouvé sans version : {service} sur {port}")
        
        # Vérifier si le service est vulnérable, même sans version
        if service.lower() in VULNERABLE_SERVICES:
            if VULNERABLE_SERVICES[service.lower()] == []:  # Si aucune version spécifique, le service est vulnérable
                print(f"ALERTE : {service} est vulnérable (version inconnue)!")
                vulnerable_services.append(f"{service} (version inconnue) sur {port}")
    
    # Si des services vulnérables ont été trouvés, générer une alerte
    if vulnerable_services:
        send_alert(vulnerable_services)
    else:
        print("Aucune vulnérabilité détectée.")

# Fonction pour envoyer une alerte (par email ou log, à ajuster selon votre configuration)
def send_alert(vulnerable_services):
    print("\nAlerte : Des services vulnérables ont été trouvés !")
    for service in vulnerable_services:
        print(f"- {service}")
    # Exemple d'alerte (envoi d'email ou log peut être ajouté ici)

# Si le script est exécuté directement
if __name__ == "__main__":
    scan_file = "/home/sylvie/Projet_scripting_securise/nmap_scan_results.txt"  # Chemin du fichier Nmap
    analyze_scan_results(scan_file)
