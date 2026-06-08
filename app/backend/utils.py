def filter_cves_by_year(cve_data, start_year):
    """
    Filters the fetched CVE data based on the software's age/last update year.
    Safe against API errors and unexpected dictionary responses.
    """
    filtered_results = []
    
    # VEILIGHEIDSKLEP 1: Als de API een error-bericht heeft gestuurd, breek direct veilig af
    if isinstance(cve_data, dict) and "error" in cve_data:
        return filtered_results

    # VEILIGHEIDSKLEP 2: Zorg dat we ALTIJD een lijst hebben om doorheen te loopen
    if isinstance(cve_data, dict):
        # Sommige API-endpoints sturen een dict met een 'results' key
        results = cve_data.get('results', [])
    elif isinstance(cve_data, list):
        results = cve_data
    else:
        # Als de data compleet onverwacht is (bijv. een losse string), voorkom een crash
        return filtered_results

    # De loop is nu 100% veilig omdat 'results' gegarandeerd een lijst is
    for cve in results:
        # Extra check: zorg dat het individuele CVE-item ook echt een dictionary is
        if not isinstance(cve, dict):
            continue
            
        cve_id = cve.get('id', '')
        try:
            if cve_id.startswith("CVE-"):
                cve_year = int(cve_id.split("-")[1])
                if cve_year >= int(start_year):
                    tech_summary = cve.get("summary", "No description available.")
                    dummy_impact, why_patch = translate_to_dummy_language(tech_summary)
                    
                    filtered_results.append({
                        "id": cve_id,
                        "severity": cve.get("cvss", "Unknown"),
                        "summary": tech_summary,
                        "dummy_impact": dummy_impact,
                        "why_patch": why_patch
                    })
        except (ValueError, IndexError):
            continue
            
    return sorted(filtered_results, key=lambda x: str(x['severity']), reverse=True)
