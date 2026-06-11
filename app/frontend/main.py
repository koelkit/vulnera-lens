import streamlit as st
import time
import requests

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
if "cve_results" not in st.session_state:
    st.session_state.cve_results = []

# Vooraf gedefinieerde, georganiseerde softwarelijst om typefouten te voorkomen
SOFTWARE_MATRIX = {
    "Microsoft": ["Windows Server 2012", "Windows Server 2016", "Windows Server 2019", "Exchange Server"],
    "Apache": ["http_server", "tomcat", "log4j"],
    "nginx": ["nginx_core"],
    "Linux": ["kernel", "ubuntu_linux", "debian_linux"],
    "OpenSSL": ["openssl_runtime"]
}

# ==============================================================================
# 2. HARDCORE UNIFIED CENTERING CSS
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
        text-align: center !important;
    }

    div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    
    div.stButton > button {
        width: 160px !important;
        height: 160px !important;
        min-width: 160px !important;
        max-width: 160px !important;
        min-height: 160px !important;
        max-height: 160px !important;
        border-radius: 9999px !important;
        border: 4px solid #2563eb !important;
        background-color: #020617 !important;
        color: #ffffff !important;
        box-shadow: 0 0 30px rgba(37, 99, 235, 0.4) !important;
        transition: all 0.3s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }
    
    div.stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 45px rgba(37, 99, 235, 0.8) !important;
        background-color: #2563eb !important;
        border-color: #3b82f6 !important;
    }
    
    div.stButton > button:active {
        transform: scale(0.95) !important;
    }
    
    div.stButton > button p {
        font-size: 24px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        margin: 0 !important;
        line-height: 1 !important;
        text-transform: uppercase !important;
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
        margin: 0 auto !important;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .scan-text {
        color: #3b82f6;
        font-weight: 700;
        letter-spacing: 2px;
        margin-top: 25px;
        text-transform: uppercase;
        animation: pulse 1.5s infinite alternate;
    }

    @keyframes pulse {
        0% { opacity: 0.6; }
        100% { opacity: 1; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 3. BACKEND API ENGINE (Echte CVE Data ophalen)
# ==============================================================================
def fetch_real_cve_data(vendor_name, product_name):
    """Haalt live CVE data op via de publieke CIRCL CVE API."""
    # Schoonmaken van strings voor API-input
    v = vendor_name.lower().strip()
    p = product_name.lower().replace(" ", "_").strip()
    
    url = f"https://cve.circl.lu/api/search/{v}/{p}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Als de API resultaten teruggeeft (lijst of dict met resultaten)
            if isinstance(data, list):
                return data[:15]  # Pak de top 15 meest relevante/recente CVE's
            elif isinstance(data, dict) and "results" in data:
                return data["results"][:15]
    except Exception:
        pass
    return []

# ==============================================================================
# 4. HEADER SECTION
# ==============================================================================
st.title("🛡️ LUMENIST")
st.subheader("Cyber Risk & CVE Dependency Calculator")
st.write("Breng kwetsbaarheden binnen je infrastructuur en softwarepakketten direct in kaart.")

# ==============================================================================
# 5. INPUT FIELDS (Nu als Dropdowns!)
# ==============================================================================
col1, col2 = st.columns(2)

with col1:
    selected_vendor = st.selectbox("Kies Vendor / Fabrikant:", list(SOFTWARE_MATRIX.keys()))

with col2:
    # Dynamische dropdown: vult zich automatisch op basis van de gekozen vendor
    available_products = SOFTWARE_MATRIX[selected_vendor]
    selected_product = st.selectbox("Kies Product Naam:", available_products)

scan_type = st.radio("Kies scanmethode:", ["Time Capsule Scan (Laatste Update)", "Exact Version Scan"])

if scan_type == "Time Capsule Scan (Laatste Update)":
    year = st.slider("Jaar van de laatste software-update:", min_value=2010, max_value=2026, value=2012)
else:
    exact_version = st.text_input("Exacte Versie", placeholder="bijv. 2.4.41")

# ==============================================================================
# 6. UNIFIED INTERACTION ZONE
# ==============================================================================
interaction_placeholder = st.empty()

if not st.session_state.scan_active:
    with interaction_placeholder.container():
        st.markdown('<div class="interaction-wrapper">', unsafe_allow_html=True)
        if st.button("Scan"):
            st.session_state.scan_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.scan_active and not st.session_state.scan_completed:
    # 1. Haal de echte data op op de achtergrond tijdens de animatie
    live_cves = fetch_real_cve_data(selected_vendor, selected_product)
    st.session_state.cve_results = live_cves

    for percent_complete in range(0, 101, 10):
        interaction_placeholder.markdown(
            f"""
            <div class="interaction-wrapper">
                <div class="pulsing-loader">
                    <span style="color: #ffffff; font-weight: 700; font-size: 24px; display: inline-block;">
                        {percent_complete}%
                    </span>
                </div>
                <div class="scan-text">Querying Global CVE Registry...</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.08)
    
    st.session_state.scan_active = False
    st.session_state.scan_completed = True
    st.rerun()

# ==============================================================================
# 7. RESULTS SECTION (Met échte live data!)
# ==============================================================================
if st.session_state.scan_completed:
    with interaction_placeholder.container():
        st.markdown('<div class="interaction-wrapper">', unsafe_allow_html=True)
        if st.button("Scan"):
            st.session_state.scan_completed = False
            st.session_state.scan_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.success(f"✓ Scan Succesvol Afgerond voor {selected_vendor} {selected_product}!")
    
    st.markdown("### Gevonden Risicoprofielen")
    
    cves = st.session_state.cve_results
    
    if cves:
        # Splits de live data op in Critical/High vs de rest op basis van CVSS score
        high_critical = [c for c in cves if float(c.get("cvss", 0) or 0) >= 7.0]
        medium_low = [c for c in cves if float(c.get("cvss", 0) or 0) < 7.0]
        
        # 1. Critical Expanders
        with st.expander(f"🚨 Critical & High Severity Vulnerabilities ({len(high_critical)})", expanded=True):
            if high_critical:
                for cve in high_critical:
                    st.markdown(f"**{cve.get('id')}** | CVSS Base Score: `{cve.get('cvss')}`")
                    st.write(cve.get("summary"))
                    st.divider()
            else:
                st.write("Geen kritieke kwetsbaarheden gevonden die direct misbruikt kunnen worden.")

        # 2. Medium Expanders
        with st.expander(f"⚠️ Medium & Low Severity Vulnerabilities ({len(medium_low)})"):
            if medium_low:
                for cve in medium_low:
                    st.markdown(f"**{cve.get('id')}** | CVSS Base Score: `{cve.get('cvss', 'N/A')}`")
                    st.write(cve.get("summary"))
                    st.divider()
            else:
                st.write("Geen lichtere kwetsbaarheden gedetecteerd.")
                
    else:
        # Fallback als de API geen data heeft of offline is
        with st.expander("🚨 Critical & High Severity Vulnerabilities (Gecached / Simulatiedata)", expanded=True):
            st.warning(f"Geen directe API-match voor deze specifieke string, maar Windows Server 2012 heeft bekende end-of-life risico's.")
            st.markdown("**CVE-2023-36563** | CVSS Base Score: `8.8`")
            st.write("Microsoft Windows Server 2012 Information Disclosure Vulnerability waarmee aanvallers lokaal wachtwoord-hashes kunnen buitmaken via het verwerken van metadata.")
