import streamlit as st
import time

# ==============================================================================
# 1. PAGE CONFIG & LAYOUT
# ==============================================================================
st.set_page_config(
    page_title="Lumenist - Cyber Risk Calculator",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialiseer session_state om de scan-status bij te houden
if "scan_active" not in st.session_state:
    st.session_state.scan_active = False
if "scan_completed" not in st.session_state:
    st.session_state.scan_completed = False

# ==============================================================================
# 2. HARDCORE UNIFIED CENTERING CSS
# ==============================================================================
st.markdown(
    """
    <style>
    /* 1. Target de interne blokken van Streamlit om CENTRERING af te dwingen */
    div[data-testid="stVerticalBlock"] > div {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* Zorg dat invoervelden en radiobuttons wel gewoon de normale breedte pakken */
    div[data-testid="stHorizontalBlock"] > div,
    div[data-testid="stRadio"] {
        align-items: flex-start !important; /* Houd invoervelden links uitgelijnd */
    }

    /* 2. Onze eigen wrapper die zowel de knop als de animatie inpakt */
    .interaction-wrapper {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        width: 100% !important;
        margin: 40px auto !important;
        text-align: center !important;
    }

    /* 3. Overschrijf de Streamlit knop-container rigoureus */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        text-align: center !important;
    }
    
    /* 4. Maak van de knop een perfecte, gecentreerde cirkel */
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
        margin: 0 auto !important; /* Forceer absolute centrering */
    }
    
    /* Hover-interactie */
    div.stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 0 45px rgba(37, 99, 235, 0.8) !important;
        background-color: #2563eb !important;
        border-color: #3b82f6 !important;
    }
    
    /* Klik-interactie */
    div.stButton > button:active {
        transform: scale(0.95) !important;
    }
    
    /* Tekst binnen de knop */
    div.stButton > button p {
        font-size: 24px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        margin: 0 !important;
        line-height: 1 !important;
        text-transform: uppercase !important;
    }

    /* 5. CSS voor de animatie-indicator (exact dezelfde uitlijning) */
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
# 3. HEADER SECTION
# ==============================================================================
st.title("🛡️ LUMENIST")
st.subheader("Cyber Risk & CVE Dependency Calculator")
st.write("Breng kwetsbaarheden binnen je infrastructuur en softwarepakketten direct in kaart.")

# ==============================================================================
# 4. INPUT FIELDS
# ==============================================================================
col1, col2 = st.columns(2)
with col1:
    vendor = st.text_input("Vendor / Fabrikant", placeholder="bijv. Apache, Microsoft")
with col2:
    product = st.text_input("Product Naam", placeholder="bijv. http_server, windows_server")

scan_type = st.radio("Kies scanmethode:", ["Time Capsule Scan (Laatste Update)", "Exact Version Scan"])

if scan_type == "Time Capsule Scan (Laatste Update)":
    year = st.slider("Jaar van de laatste software-update:", min_value=2010, max_value=2026, value=2022)
else:
    exact_version = st.text_input("Exacte Versie", placeholder="bijv. 2.4.41")

# ==============================================================================
# 5. UNIFIED INTERACTION ZONE
# ==============================================================================
interaction_placeholder = st.empty()

# Als de scan niet actief is, tonen we de knop gecentreerd via de wrapper
if not st.session_state.scan_active:
    with interaction_placeholder.container():
        st.markdown('<div class="interaction-wrapper">', unsafe_allow_html=True)
        if st.button("Scan"):
            st.session_state.scan_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Als de scan loopt, tonen we de animatie op exact dezelfde plek
if st.session_state.scan_active and not st.session_state.scan_completed:
    for percent_complete in range(0, 101, 5):
        interaction_placeholder.markdown(
            f"""
            <div class="interaction-wrapper">
                <div class="pulsing-loader">
                    <span style="color: #ffffff; font-weight: 700; font-size: 24px; display: inline-block;">
                        {percent_complete}%
                    </span>
                </div>
                <div class="scan-text">Mapping CVE Registry...</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.07)
    
    st.session_state.scan_active = False
    st.session_state.scan_completed = True
    st.rerun()

# Na het scannen herstellen we de knop boven de resultaten
if st.session_state.scan_completed:
    with interaction_placeholder.container():
        st.markdown('<div class="interaction-wrapper">', unsafe_allow_html=True)
        if st.button("Scan"):
            st.session_state.scan_completed = False
            st.session_state.scan_active = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================================================
    # 6. RESULTS SECTION
    # ==========================================================================
    st.success("✓ Scan Succesvol Afgerond!")
    st.markdown("### Gevonden Risicoprofielen")
    
    with st.expander("🚨 Critical & High Severity Vulnerabilities", expanded=True):
        st.write(f"Er zijn kritieke kwetsbaarheden gevonden voor **{vendor if vendor else 'Onbekend'} - {product if product else 'Onbekend'}**.")
        st.info("Advies: Update per direct naar de meest recente stabiele runtime-versie om remote code execution (RCE) te voorkomen.")
        
    with st.expander("⚠️ Medium Severity Vulnerabilities"):
        st.write("Potentiële denial-of-service (DoS) risico's geïdentificeerd bij langdurige netwerkbelasting.")
        
    with st.expander("ℹ️ Low Severity & Best Practices"):
        st.write("Configuratietip: Schakel ongebruikte modules uit binnen je backend/api.py om het aanvalsoppervlak te verkleinen.")
