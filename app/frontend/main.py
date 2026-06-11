import streamlit as st
import time
import sys
import os

# Zorg dat Python de 'app' map kan vinden voor de backend import vanaf de root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.backend.api import fetch_filtered_cve_data

# ==============================================================================
# 1. PAGE CONFIG & LAYOUT
# ==============================================================================
st.set_page_config(
    page_title="Lumenist - Cyber Risk Calculator",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialiseer session_state voor scan-status en data-opslag
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
# 2. CYBERPUNK / ASTRA MUSIC STYLE CSS INJECTION
# ==============================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Plus+Jakarta+Sans:wght@300;400;700&display=swap');

    /* Globale resets naar Astra's donkere matrix */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #030712 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: #f3f4f6 !important;
    }

    /* Subtiele achtergrond grid zoals astramusic.dev */
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-image: 
            linear-gradient(rgba(37, 99, 235, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(37, 99, 235, 0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        z-index: 0;
        pointer-events: none;
    }

    /* Titels met cyber glow */
    h1 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: -1px !important;
        background: linear-gradient(135deg, #ffffff 0%, #93c5fd 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 30px rgba(37, 99, 235, 0.2);
    }
    
    h3 {
        font-family: 'JetBrains Mono', monospace !important;
        color: #60a5fa !important;
        font-size: 14px !important;
        letter-spacing: 2px !important;
        text-transform: uppercase;
    }

    /* Gecentreerde hoofdstructuur */
    div[data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }
    div[data-testid="stVerticalBlock"] > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* Astra stijl Translucente Invoervelden (Glassmorphism) */
    div[data-testid="stWidgetLabel"] p {
        color: #9ca3af !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px !important;
    }
    
    .stSelectbox div[data-baseweb="select"], .stSlider, div[data-testid="stRadio"] {
        background: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        backdrop-filter: blur(12px);
        transition: all 0.3s ease;
    }
    .stSelectbox div[data-baseweb="select"]:hover {
        border-color: rgba(59, 130, 246, 0.4) !important;
        box-shadow: 0 0 15px rgba(37, 99, 235, 0.1);
    }

    /* Inputs links uitlijnen */
    div[data-testid="stHorizontalBlock"] > div,
    div[data-testid="stRadio"],
    div[data-testid="stSelectbox"] {
        align-items: flex-start !important;
        text-align: left !important;
    }

    /* Ultra-minimalistische Cirkelknop */
    .interaction-wrapper {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 50px auto !important;
    }

    div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    
    div.stButton > button {
        width: 150px !important;
        height: 150px !important;
        border-radius: 9999px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background: radial-gradient(circle, rgba(30, 41, 59, 0.5) 0%, rgba(3, 7, 18, 0.8) 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 0 40px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(255, 255, 255, 0.02) !important;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 16px !important;
        font-weight: 400 !important;
        letter-spacing: 4px !important;
        backdrop-filter: blur(8px);
    }
    
    /* Neon Cyber Hover van Astra */
    div.stButton > button:hover {
        transform: scale(1.03) !important;
        border-color: #60a5fa !important;
        background: #020617 !important;
        box-shadow: 0 0 40px rgba(37, 99, 235, 0.3), inset 0 0 15px rgba(59, 130, 246, 0.2) !important;
        color: #60a5fa !important;
    }

    div.stButton > button p {
        margin: 0 !important;
        text-transform: uppercase !important;
    }

    /* Fijne lijn Cyber Loader */
    .pulsing-loader {
        width: 150px !important;
        height: 150px !important;
        border-radius: 50% !important;
        border: 2px solid rgba(255, 255, 255, 0.05) !important;
        border-top: 2px solid #3b82f6 !important;
        border-bottom: 2px solid #60a5fa !important;
        animation: spin 2s cubic-bezier(0.4, 0, 0.2, 1) infinite;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 0 30px rgba(37, 99, 235, 0.1) !important;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    
    .scan-text {
        font-family: 'JetBrains Mono', monospace !important;
        color: #60a5fa;
        font-size: 11px;
        letter-spacing: 3px;
        margin-top: 30px;
        text-transform: uppercase;
        opacity: 0.8;
    }

    /* Astra Glassmorphism Expanders / Cards */
    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(20px);
        margin-bottom: 15px !important;
        width: 100% !important;
    }
    
    div[data-testid="stExpander"] details {
        border: none !important;
    }

    /* Sortering dropdown styling tweak */
    .stSelectbox {
        width: 100% !important;
    }

    /* Custom strakke banners */
    div.stAlert {
        background: rgba(30, 41, 59, 0.3) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 3. HEADER SECTION
# ==============================================================================
st.markdown("<h3>Calculated Risk Registry</h3>", unsafe_allow_html=True)
st.title("LUMENIST")
st.write("Breng kwetsbaarheden binnen je infrastructuur en softwarepakketten direct in kaart via fine-line dependency checks.")

# ==============================================================================
# 4. INPUT DROPDOWNS
# ==============================================================================
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

# ==============================================================================
# 5. UNIFIED INTERACTION ZONE
# ==============================================================================
interaction_placeholder = st.empty()

if not st.session_state.scan_active:
    with interaction_placeholder.container():
        st.markdown('<div class="interaction-wrapper">', unsafe_allow_html=True)
        if st.button("Scan", key="scan_btn_initial"):
            st.session_state.scan_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.scan_active and not st.session_state.scan_completed:
    total, cves = fetch_filtered_cve_data(selected_vendor, selected_product, year)
    st.session_state.total_found = total
    st.session_state.cve_results = cves

    for percent_complete in range(0, 101, 10):
        interaction_placeholder.markdown(
            f"""
            <div class="interaction-wrapper">
                <div class="pulsing-loader">
                    <span style="color: #ffffff; font-family: 'JetBrains Mono', monospace; font-size: 18px; font-weight:300;">{percent_complete}%</span>
                </div>
                <div class="scan-text">Indexing local registries...</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.06)
    
    st.session_state.scan_active = False
    st.session_state.scan_completed = True
    st.rerun()

# ==============================================================================
# 6. RESULTS SECTION
# ==============================================================================
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
    
    if total_found > 300:
        st.error(
            f"⚠️ **System Threshold Exceeded.** Er zijn in totaal **{total_found}** kwetsbaarheden gevonden. "
            f"De sandbox webomgeving toont uitsluitend de **300 meest kritieke exploits**. "
            f"**Download de Lumenist Desktop Client** voor diepgaande geautomatiseerde patch-adviezen en volledige logs."
        )
    else:
        st.success(f"✓ Scan completed. Er zijn **{total_found}** kwetsbaarheden gevonden.")
        
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
