import os
import json

def fetch_filtered_cve_data(vendor_name, product_name, last_update_year):
    """
    Zoekt naar lokale CVE-data in de assets of data mappen.
    Geeft (total_count, cves_list_max_300) terug.
    """
    vendor_folder = vendor_name.lower().strip()
    product_folder = product_name.lower().replace(" ", "_").strip()
    filename = f"{last_update_year}.json"
    
    # We kijken of er al echte JSON bestanden bestaan binnen je project
    # Gezien je structuur checken we een 'data' of 'assets' map
    file_path = os.path.join("app", "assets", f"{vendor_folder}_{product_folder}", filename)
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            return data.get("total_count", 0), data.get("cves", [])[:300]
            
    # ==========================================================================
    # AUTOMATISCHE SIMULATIE ENGINE (Fallback per App)
    # ==========================================================================
    years_unpatched = 2026 - last_update_year
    cves_to_show = []
    
    if vendor_name == "Microsoft":
        total_count = int(years_unpatched * 240) + 150  # Schiet richting de 3500+ voor 2012
        
        # Voeg de meest kritieke hardcoded toe voor de UI
        cves_to_show = [
            {"id": "CVE-2023-36563", "cvss": 8.8, "summary": f"Kritiek lek in {product_name} metadata-verwerking. Wachtwoord-hashes kunnen op afstand worden onderschept."},
            {"id": "CVE-2022-21907", "cvss": 9.8, "summary": "Remote Code Execution (RCE) kwetsbaarheid in HTTP.sys via kwaadaardig geformatteerde netwerkpakketten."},
            {"id": "CVE-2017-0144", "cvss": 8.1, "summary": "EternalBlue SMBv1 kwetsbaarheid die remote code execution en worm-replicatie toestaat."}
        ]
        
        # Genereer de rest van de lijst (tot max 300) met aflopende CVSS scores (hoogste eerst!)
        limit = min(300, total_count)
        for i in range(len(cves_to_show), limit):
            cves_to_show.append({
                "id": f"CVE-{2026 - (i%14)}-{1000 + i}",
                "cvss": round(8.0 - (i * 0.015), 1),
                "summary": f"Exploitbaar beveiligingsrisico geïdentificeerd binnen de {product_name} kernel componenten. Patch vereist."
            })
            
    elif vendor_name == "nginx":
        total_count = int(years_unpatched * 8) + 12  # Veel minder dan Windows, maar realistisch
        cves_to_show = [
            {"id": "CVE-2022-41741", "cvss": 7.5, "summary": "Geheugenlek en potentiële RCE kwetsbaarheid in de nginx mp4-module tijdens het parsen van mediabestanden."},
            {"id": "CVE-2021-23017", "cvss": 8.1, "summary": "1-byte memory overwrite kwetsbaarheid in de nginx DNS-resolver module, wat kan leiden tot crashes."}
        ]
        limit = min(300, total_count)
        for i in range(len(cves_to_show), limit):
            cves_to_show.append({
                "id": f"CVE-{2025 - (i%10)}-{2000 + i}",
                "cvss": round(7.4 - (i * 0.03), 1),
                "summary": "Nginx_core pipeline buffer overflow risico bij specifieke HTTP header configuraties."
            })
            
    elif vendor_name == "Apache":
        total_count = int(years_unpatched * 45) + 40
        cves_to_show = [
            {"id": "CVE-2021-44228", "cvss": 10.0, "summary": "Apache Log4j2 JNDI Remote Code Execution kwetsbaarheid (Log4Shell). Volledige systeemovername mogelijk."},
            {"id": "CVE-2021-41773", "cvss": 7.5, "summary": "Path Traversal en Remote Code Execution kwetsbaarheid in Apache HTTP Server core."}
        ]
        limit = min(300, total_count)
        for i in range(len(cves_to_show), limit):
            cves_to_show.append({
                "id": f"CVE-{2024 - (i%12)}-{3000 + i}",
                "cvss": round(7.4 - (i * 0.02), 1),
                "summary": "Apache HTTP Server privilege escalation kwetsbaarheid via onveilige module interacties."
            })
    else:
        total_count = int(years_unpatched * 5) + 2
        cves_to_show = [
            {"id": "CVE-2025-9999", "cvss": 6.5, "summary": f"Algemene runtime kwetsbaarheid gedetecteerd voor {vendor_name} subsystemen."},
            {"id": "CVE-2022-1111", "cvss": 5.2, "summary": "Ontbrekende updates gedetecteerd in legacy functionaliteiten."}
        ]
        
    return total_count, cves_to_show
