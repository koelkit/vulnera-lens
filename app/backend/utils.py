def translate_to_dummy_language(summary):
    """
    Scans the technical CVE summary for keywords and translates it
    into clear business risks + a reason why to patch.
    """
    summary_lower = summary.lower()
    
    impact = "This vulnerability could allow attackers to disrupt your software or access restricted data."
    why_patch = "To prevent unauthorized changes to your system and keep your business running smoothly."
    
    if "execute arbitrary code" in summary_lower or "remote code execution" in summary_lower or "rce" in summary_lower:
        impact = "💥 **Total Takeover:** A hacker can completely take over your server from anywhere in the world. They can run malicious software, steal files, or lock you out."
        why_patch = "This is the most dangerous type of attack. Failing to patch this allows cybercriminals to deploy ransomware and shut down your business operations."
        
    elif "denial of service" in summary_lower or "crash" in summary_lower or "dos" in summary_lower:
        impact = "🛑 **System Crash:** An attacker can overload your server, causing it to freeze or crash. Your customers won't be able to access your website or services."
        why_patch = "To prevent costly downtime. If your platform goes offline, you risk losing revenue, customer trust, and brand reputation."
        
    elif "information disclosure" in summary_lower or "obtain information" in summary_lower or "leak" in summary_lower or "read" in summary_lower:
        impact = "🔓 **Data Leak:** An attacker can peek inside your server and read private information, such as customer credentials, credit card details, or company secrets."
        why_patch = "To protect user privacy and comply with regulations (like GDPR). Data leaks can result in severe legal fines and lawsuits."
        
    elif "gain privileges" in summary_lower or "privilege escalation" in summary_lower or "bypass security" in summary_lower:
        impact = "🔑 **Security Bypass:** Someone with low-level access can trick the system into granting them 'Admin' rights, allowing them to bypass security controls entirely."
        why_patch = "To maintain strict access control. Unauthorized users shouldn't have the power to modify system settings, delete logs, or view financial data."

    return impact, why_patch


def filter_cves_by_year(cve_data, start_year):
    """
    Filters the fetched CVE data based on the software's age/last update year.
    """
    filtered_results = []
    if isinstance(cve_data, dict) and "error" in cve_data:
        return filtered_results

    results = cve_data if isinstance(cve_data, list) else cve_data.get('results', [])

    for cve in results:
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
