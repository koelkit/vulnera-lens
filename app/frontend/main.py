import streamlit as st
import sys
import os
import time

# 1. Zorg dat de backend map correct wordt gevonden voor de API functionaliteit
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.api import fetch_cve_data
from backend.utils import filter_cves_by_year

# 2. Pagina configuratie (Dark mode basis)
st.set_page_config(
    page_title="Lumenist",
    page_icon="🛡️",
    layout="centered"
)

# 3. Injecteer je strakke CSS styling
try:
    with open("app/frontend/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    # Veiligheidsklep voor als het pad lokaal anders is
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 4. Laad en toon de Markdown teksten (De bovenkant van je site!)
try:
    with open("app/frontend/content.md") as f:
        content = f.read()
except FileNotFoundError:
    with open("content.md") as f:
        content = f.read()

header_part, input_part = content.split("---")
st.markdown(header_part)
st.markdown(input_part)

# 5. Gebruikersinvoer velden (Eerst aanmaken zodat ze BESTAAN!)
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

# 6. Placeholder klaarzetten voor de cirkel-animatie
animation_placeholder = st.empty()

# 7. De Actieknop
if st.button("🚀 CALCULATE CYBER RISKS", use_container_width=True):
    if not vendor or not product:
        st.error("❌ Please fill in both the Vendor and Product fields.")
    else:
        # Start de Speedtest-style Cirkel Animatie
        for progress in range(0, 101, 2):
            time.sleep(0.04)  # Snelheid van de animatie
            angle = progress * 3.6
            
            animation_placeholder.markdown(
                f"""
                <div class="speedtest-container">
                    <div class="circular-progress" style="background: conic-gradient(#2563eb {angle}deg, #1e293b {angle}deg);">
                        <div class="value-container">{progress}%</div>
                    </div>
                    <div class="loading-text">MAPPING CVE REGISTRY...</div>
                </div>
                <style>
                .speedtest-container {{ display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 30px; }}
                .circular-progress {{ position: relative; height: 180px; width: 180px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 30px rgba(37, 99, 235, 0.2); }}
                .circular-progress::before {{ content: ""; position: absolute; height: 140px; width: 140px; border-radius: 50%; background-color: #020617; }}
                .value-container {{ position: relative; font-family: 'Inter', sans-serif; font-size: 32px; font-weight: 700; color: #ffffff; }}
                .loading-text {{ margin-top: 15px; font-family: 'Inter', sans-serif; font-size: 13px; letter-spacing: 2px; color: #2563eb; font-weight: 600; animation: pulse 1.5s infinite; }}
                @keyframes pulse {{ 0% {{ opacity: 0.6; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.6; }} }}
                </style>
                """,
                unsafe_allow_html=True
            )

        # Maak de animatie leeg zodra hij op 100% staat
        animation_placeholder.empty()
        
        # Voer de backend API-koppeling uit
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

                # Resultaten tonen
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
                        if severity != "Unknown" and float
