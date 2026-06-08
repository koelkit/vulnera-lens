import streamlit as st
import sys
import os

# Zorg dat de backend map correct wordt ingeladen in de cloud
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.api import fetch_cve_data
from backend.utils import filter_cves_by_year

# 1. Page Configuration (Dark theme foundation)
st.set_page_config(
    page_title="Simple Vulnerability Calculator",
    page_icon="🛡️",
    layout="centered"
)

# 2. Inject de "Astra-stijl" (CSS)
with open("app/frontend/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. Laad de Markdown teksten
with open("app/frontend/content.md") as f:
    content = f.read()

header_part, input_part = content.split("---")
st.markdown(header_part)
st.markdown(input_part)

# 4. User Inputs
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
    # De core feature: slider tot het huidige jaar (2026)
    start_year = st.slider("When was this server or application last updated?", 2010, 2026, 2018)
else:
    version_to_check = st.text_input("Enter exact version (e.g., 2.4.52):").strip()

st.markdown("---")

# 5. Het startschot (De Berekening)
if st.button("🚀 Calculate Cyber Risks", use_container_width=True):
    if not vendor or not product:
        st.error("❌ Please fill in both the Vendor and Product fields.")
    else:
        with st.spinner("Connecting to global CVE registry..."):
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
                                "summary": cve.get('summary', 'No description available.')
                            })

                # 6. Resultaten tonen in de strakke tech-vibe
                if not results:
                    st.info(
                        "📊 **Risk Profile: Low**\n\n"
                        "No major open vulnerabilities were detected in our current registry mapping for this configuration. "
                        "Please note that this is a baseline check and not a guarantee against all cyber threats."
                    )
                else:
                    st.warning(f"⚠️ Found **{len(results)}** potential vulnerabilities matching your profile.")
                    
                    for vuln in results[:30]:
                        severity = vuln['severity']
                        if severity != "Unknown" and float(severity) >= 7.0:
                            badge = f"🔴 CRITICAL/HIGH ({severity})"
                        elif severity != "Unknown" and float(severity) >= 4.0:
                            badge = f"🟠 MEDIUM ({severity})"
                        else:
                            badge = f"🟡 LOW ({severity})"
                            
                        with st.expander(f"{vuln['id']} - {badge}"):
                            st.markdown("### 🔍 What can this do?")
                            st.write(vuln['dummy_impact'])
                            
                            st.markdown("### 🛠️ Why should you patch this?")
                            st.write(vuln['why_patch'])
                            
                            st.markdown("---")
                            st.caption(f"💾 *Technical Summary:* {vuln['summary']}")

# 7. De Juridische Disclaimer onderaan de site
st.markdown("---")
st.caption(
    "⚖️ **Legal Disclaimer:** This calculator provides a risk assessment based on publicly available CVE data. "
    "It does not constitute a full security audit. The creator cannot be held liable for any damages."
)
