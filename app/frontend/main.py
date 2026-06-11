import streamlit as st
import time
import sys
import os

# Zorg dat Python de 'app' map kan vinden voor de backend import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.backend.api import fetch_filtered_cve_data

# ==============================================================================
# PAGE CONFIG
# ==============================================================================
st.set_page_config(
    page_title="Lumenist - Cyber Risk Calculator",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

if "scan_active" not in st.session_state:
    st.session_state.scan_active = False
if "scan_completed" not in st.session_state:
    st.session_state.scan_completed = False
if "total_found" not in st.session_state:
    st.session_state.total_found = 0
if "cve_results" not in st.session_state:
    st.session_state.cve_results = []

SOFTWARE_MATRIX = {
    "Microsoft": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Exchange Server"],
    "Apache": ["http_server", "tomcat", "log4j"],
    "nginx": ["nginx_core"],
    "Linux": ["kernel", "ubuntu_linux"],
    "OpenSSL": ["openssl"]
}

# ==============================================================================
# CSS STYLING (Inclusief gecentreerde knop & loader)
# ==============================================================================
st.markdown(
    """
    <style>
    div[data-testid="stVerticalBlock"] > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }
    div[data-testid="stHorizontalBlock"] > div,
    div[data-testid="stRadio"],
    div[data-testid="stSelectbox"] {
        align-items: flex-start !important;
        text-align: left !important;
    }
    .interaction-wrapper {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 40px auto !important;
    }
    div.stButton > button {
        width: 160px !important;
        height: 160px !important;
        border-radius: 9999px !important;
        border: 4px solid #2563eb !important;
        background-color: #020617 !important;
        color: #ffffff !important;
        box-shadow: 0 0 30px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
    }
    div.stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 45px rgba(37, 99, 235, 0.8) !important;
        background-color: #2563eb !important;
    }
    .pulsing-loader {
        width: 160px !important;
        height: 160px !important;
        border-radius: 50% !important;
        border: 4px dashed #2563eb !important;
        animation: spin 4s linear infinite;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 0 30px rgba(37, 99, 235, 0.2) !important;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    .scan-text {
        color: #3b82f6;
        font-weight: 700;
        letter-spacing: 2px;
        margin-top: 25px;
        text-transform: uppercase;
        animation: pulse 1.5s infinite alternate;
    }
    @keyframes pulse { 0% { opacity: 0.6; } 100% { opacity: 1; } }
    </style>
    """,
    unsafe_allow_html=True
)

# UI HEADERS
st.title("🛡️ LUMENIST")
st.subheader("Cyber Risk & CVE Dependency Calculator")

# INPUT DROPDOWNS
col1, col2 = st.columns(2)
with col1:
    selected_vendor = st.selectbox("Kies Vendor / Fabrikant:", list(SOFTWARE_MATRIX.keys()))
with col2:
    selected_product = st.selectbox("Kies Product Naam:", SOFTWARE_MATRIX[selected_vendor])

scan_type = st.radio("Kies scanmethode:", ["Time Capsule Scan (Laatste Update)", "Exact Version Scan"])

if scan_type == "Time Capsule Scan (Laatste Update)":
    default_year = 2012 if "2012" in selected_product else 2018
    year = st.slider("Jaar van de laatste software-update:", min_value=2010, max_value=2026, value=default_year)
else:
    exact_version = st.text_input("Exacte Versie", placeholder="bijv. 2.4.41")
    year = 2026

# INTERACTION ZONE
interaction_placeholder = st.empty()

if not st.session_state.scan_active:
    with interaction_placeholder.container():
        st.markdown('<div class="interaction-wrapper">', unsafe_allow_html=True)
        if st.button("Scan", key="scan_btn_initial"):
            st.session_state.scan_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.scan_active and not st.session_state.scan_completed:
    # Roep de backend api aan
    total, cves = fetch_filtered_cve_data(selected_vendor, selected_product, year)
    st.session_state.total_found = total
    st.session_state.cve_results = cves

    for percent_complete in range(0, 101, 10):
        interaction_placeholder.markdown(
            f"""
            <div class="interaction-wrapper">
                <div class="pulsing-loader">
                    <span style="color: #ffffff; font-weight: 700; font-size: 24px;">{percent_complete}%</span>
                </div>
                <div class="scan-text">Mapping Local CVE Registry...</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.06)
    
    st.session_state.scan_active = False
    st.session_state.scan_completed = True
    st.rerun()

# RESULTS BLOCK
if st.session_state.scan_completed:
    with interaction_placeholder.container():
        st.markdown('<div class="interaction-wrapper">', unsafe_allow_html=True)
        if st.button("Scan", key="scan_btn_result"):
            st.session_state.scan_completed = False
            st.session_state.scan_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    total_found = st.session_state.total_found
    cves_displayed = len(st.session_state.cve_results)
    
    # COMMERCIËLE COMMERCIAL/PREMIUM UPSELL BANNER
    if total_found > 300:
        st.error(
            f"⚠️ **Kritiek Beveiligingsrisico!** Er zijn in totaal **{total_found}** kwetsbaarheden gevonden voor deze configuratie. "
            f"De webversie van Lumenist toont standaard de **300 meest kritieke exploits** om het systeem niet te overbelasten. "
            f"**Download de volledige Lumenist Desktop App (binnenkort beschikbaar)** om alle {total_found} problemen in te zien, "
            f"automatische patch-adviezen te genereren en volledige compliance-rapporten te exporteren."
        )
    else:
        st.success(f"✓ Scan Succesvol Afgerond! Er zijn **{total_found}** kwetsbaarheden gevonden voor {selected_vendor} {selected_product}.")
        
    st.markdown("### Gevonden Risicoprofielen")
    
    if cves_displayed > 0:
        sort_order = st.selectbox("Sorteer op CVSS-score:", ["Hoog naar Laag (Meest Kritiek)", "Laag naar Hoog (Minst Kritiek)"])
        reverse_bool = True if sort_order == "Hoog naar Laag (Meest Kritiek)" else False
        
        sorted_cves = sorted(st.session_state.cve_results, key=lambda x: float(x.get("cvss", 0)), reverse=reverse_bool)
        
        high_critical = [c for c in sorted_cves if float(c.get("cvss", 0)) >= 7.0]
        medium_low = [c for c in sorted_cves if float(c.get("cvss", 0)) < 7.0]
        
        with st.expander(f"🚨 Critical & High Severity Vulnerabilities ({len(high_critical)})", expanded=True):
            for cve in high_critical:
                st.markdown(f"**{cve.get('id')}** | CVSS: `{cve.get('cvss')}`")
                st.write(cve.get("summary"))
                st.divider()

        with st.expander(f"⚠️ Medium & Low Severity Vulnerabilities ({len(medium_low)})"):
            for cve in medium_low:
                st.markdown(f"**{cve.get('id')}** | CVSS: `{cve.get('cvss')}`")
                st.write(cve.get("summary"))
                st.divider()
