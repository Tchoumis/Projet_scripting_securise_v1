import sys
import re

# Base de données de vulnérabilités
VULNERABLE_SERVICES = {
    'vsftpd': ['3.0.5'],
    'openssh': ['9.9p1'],
    'apache': ['2.4.1', '2.4.2'],
    'ftp': [],
    'ssh': []
}

# Fonction pour analyser les résultats du scan nmap
def analyze_scan_results(scan_file):
    with open(scan_file, 'r') as file:
        data = file.read()

    # Affichage du contenu du fichier pour vérification
    print("Contenu du fichier :")
    print(data)
    
    # Recherche des services et versions trouvées par nmap
    services = re.findall(r'(\d+/tcp)\s+open\s+([a-zA-Z0-9\-]+)\s+([0-9.]+)', data)
    services_no_version = re.findall(r'(\d+/tcp)\s+open\s+([a-zA-Z0-9\-]+)', data)
    
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

# Fonction pour envoyer une alerte
def send_alert(vulnerable_services):
    print("\nAlerte : Des services vulnérables ont été trouvés !")
    for service in vulnerable_services:
        print(f"- {service}")


# Si le script est exécuté directement
if __name__ == "__main__":
    scan_file = "/home/sylvie/Projet_scripting_securise/nmap_scan_results.txt"
    analyze_scan_results(scan_file)
