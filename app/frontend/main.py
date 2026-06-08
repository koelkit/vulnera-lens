import streamlit as st
import sys
import os
import time

# 1. Zorg dat Python de backend map kan vinden voor de API functionaliteit
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from backend.api import fetch_cve_data
    from backend.utils import filter_cves_by_year
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(current_dir, '../../')))
    from backend.api import fetch_cve_data
    from backend.utils import filter_cves_by_year

# 2. Pagina configuratie (Strakke dark mode basis)
st.set_page_config(
    page_title="Lumenist",
    page_icon="🛡️",
    layout="centered"
)

# 3. Correcte paden ingesteld op de 'app' mappenstructuur
possible_css_paths = [
    os.path.join(current_dir, "style.css"),
    "app/frontend/style.css",
    "style.css"
]

possible_md_paths = [
    os.path.join(current_dir, "content.md"),
    "app/frontend/content.md",
    "content.md"
]

# Laad CSS
css_content = ""
for path in possible_css_paths:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            css_content = f.read()
        break

if css_content:
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Laad Content.md
md_content = ""
for path in possible_md_paths:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            md_content = f.read()
        break

# 4. Toon de content (De bovenkant van je site!)
if md_content:
    if "---" in md_content:
        header_part, input_part = md_content.split("---", 1)
        st.markdown(header_part)
        st.markdown(input_part)
    else:
        st.markdown(md_content)
else:
    st.title("🛡️ LUMENIST")
    st.subheader("Simpele Cyber-Risico Calculator voor Startups")

# 5. Invoervelden voor de gebruiker
col1, col2 = st.columns(2)
with col1:
    vendor = st.text_input("Vendor / Manufacturer", placeholder="e.g., apache, microsoft").strip()
with col2:
    product = st.text_input("Product Name", placeholder="e.g., http_server, windows_server").strip()

search_method = st.radio(
    "How do you want to calculate your risk?",
    ["I only know the year of my last update (Time Capsule Scan)", "I know the exact software version"]
)

start_year = 2010
version_to_check = ""

if search_method == "I only know the year of my last update (Time Capsule Scan)":
    start_year = st.slider("When was this server or application last updated?", 2010, 2026, 2018)
else:
    version_to_check = st.text_input("Enter exact version (e.g., 2.4.52):").strip()

st.markdown("---")

# Injecteer agressieve CSS om de knop PERFECT CENTRAAL en 100% ROND te maken
st.markdown(
    """
    <style>
    /* Centreer de Streamlit widget container op de pagina */
    div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        text-align: center !important;
        margin: 30px auto !important;
    }
    
    /* Maak van de knop zelf een perfecte, strakke cirkel */
    div[data-testid="stButton"] > button {
        width: 160px !important;
        height: 160px !important;
        min-width: 160px !important;
        max-width: 160px !important;
        min-height: 160px !important;
        max-height: 160px !important;
        border-radius: 9999px !important; /* Voorkomt de 'squircle' vorm */
        border: 4px solid #2563eb !important;
        background-color: #020617 !important;
        color: #ffffff !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        box-shadow: 0 0 30px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Hover en actieve klik effecten */
    div[data-testid="stButton"] > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 45px rgba(37, 99, 235, 0.8) !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-color: #3b82f6 !important;
    }
    
    div[data-testid="stButton"] > button:active {
        transform: scale(0.95) !important;
    }
    
    /* Zorg dat Streamlit de tekst in de knop niet vervormt */
    div[data-testid="stButton"] > button p {
        font-size: 22px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        line-height: 1 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Placeholder klaarzetten voor de animatie
animation_placeholder = st.empty()

# 6. De Actieknop (Nu met de tekst SCAN en volledig gecentreerd)
if st.button("SCAN"):
    if not vendor or not product:
        st.error("❌ Please fill in both the Vendor and Product fields.")
    else:
        # Start direct de Speedtest-style Cirkel Animatie op exact dezelfde centrale plek
        for progress in range(0, 101, 2):
            time.sleep(0.04)
            angle = progress * 3.6
            
            # Alle interne CSS-accolades zijn hier dubbel {{ }} om f-string crashes te voorkomen
            animation_placeholder.markdown(
                f"""
                <div class="speedtest-container">
                    <div class="circular-progress" style="background: conic-gradient(#2563eb {angle}deg, #1e293b {angle}deg);">
                        <div class="value-container">{progress}%</div>
                    </div>
                    <div class="loading-text">MAPPING CVE REGISTRY...</div>
                </div>
                <style>
                /* Verberg de startknop tijdens het laden */
                div[data-testid="stButton"] {{ display: none !important; }}
                
                .speedtest-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px; width: 100%; }}
                .circular-progress {{ position: relative; height: 160px; width: 160px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 30px rgba(37, 99, 235, 0.4); }}
                .circular-progress::before {{ content: ""; position: absolute; height: 120px; width: 120px; border-radius: 50%; background-color: #020617; }}
                .value-container {{ position: relative; font-family: 'Inter', sans-serif; font-size: 28px; font-weight: 700; color: #ffffff; }}
                .loading-text {{ margin-top: 15px; font-family: 'Inter', sans-serif; font-size: 13px; letter-spacing: 2px; color: #2563eb; font-weight: 600; animation: pulse 1.5s infinite; }}
                @keyframes pulse {{ 0% {{ opacity: 0.6; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.6; }} }}
                </style>
                """,
                unsafe_allow_html=True
            )

        # Maak de animatie leeg zodra hij op 100% staat
        animation_placeholder.empty()
        
        # Haal de echte backend data op
        with st.spinner("Fetching final results..."):
            raw_data = fetch_cve_data(vendor, product)
            
            if isinstance(raw_data, dict) and "error" in raw_data:
                st.error(f"❌ {raw_data['error']}")
            else:
                if search_method == "I only know the year of my last update (Time Capsule Scan)":
                    results = filter_cves_by_year(raw_data, start_year)
                else:
                    results = []
                    cve_list = raw_data if isinstance(raw_data, list) else raw_data.get('results', [])
                    for cve in cve_list:
                        if version_to_check and version_to_check in str(cve.get('vulnerable_configuration', '')):
                            results.append({
                                "id": cve.get('id'),
                                "severity": cve.get('cvss', 'Unknown'),
                                "summary": cve.get('summary', 'No description available.'),
                                "dummy_impact": "Analysis pending...",
                                "why_patch": "Review details below."
                            })

                # Resultaten op het scherm tonen
                if not results:
                    st.info(
                        "📊 **Risk Profile: Low**\n\n"
                        "No major open vulnerabilities were detected in our current registry mapping for this configuration. "
                        "Please note that this is a baseline check and not a guarantee against all cyber threats."
                    )
                else:
                    st.warning(f"⚠️ Found **{len(results)}** potential vulnerabilities matching your profile.")
                    
                    for vuln in results[:30]:
                        severity = vuln.get('severity', 'Unknown')
                        
                        if severity != "Unknown" and float(severity) >= 7.0:
                            badge = f"🔴 CRITICAL/HIGH ({severity})"
                        elif severity != "Unknown" and float(severity) >= 4.0:
                            badge = f"🟠 MEDIUM ({severity})"
                        else:
                            badge = f"🟡 LOW ({severity})"
                            
                        with st.expander(f"{vuln.get('id', 'CVE')} - {badge}"):
                            st.markdown("### 🔍 What can this do?")
                            st.write(vuln.get('dummy_impact', 'N/A'))
                            st.markdown("### 🛠️ Why should you patch this?")
                            st.write(vuln.get('why_patch', 'N/A'))
