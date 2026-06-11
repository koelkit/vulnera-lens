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

# ==============================================================================
# 2. AGGRESSIVE CSS STYLE INJECTION
# ==============================================================================
# Dit blok dwingt de knop in het midden en maakt hem 100% rond (160x160px).
# Het overschrijft de standaard HTML-containers van Streamlit.
st.markdown(
    """
    <style>
    /* 1. Centreer de Streamlit button-container op de pagina */
    div.stButton {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin: 40px 0 !important; /* Ruimte boven en onder de knop */
        position: relative !important;
    }
    
    /* 2. Transformeer de knop zelf naar een perfecte, strakke cirkel */
    div.stButton > button {
        width: 160px !important;
        height: 160px !important;
        min-width: 160px !important;
        max-width: 160px !important;
        min-height: 160px !important;
        max-height: 160px !important;
        border-radius: 9999px !important; /* Dwingt een 100% cirkel af */
        border: 4px solid #2563eb !important; /* Felblauwe security rand */
        background-color: #020617 !important; /* Donkere cybersecurity achtergrond */
        color: #ffffff !important;
        box-shadow: 0 0 30px rgba(37, 99, 235, 0.4) !important; /* Glow-effect */
        transition: all 0.3s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        cursor: pointer !important;
    }
    
    /* 3. Hover-interactie voor de ronde knop */
    div.stButton > button:hover {
        transform: scale(1.05) !important; /* Subtiel groter worden */
        box-shadow: 0 0 45px rgba(37, 99, 235, 0.8) !important; /* Sterkere gloed */
        background-color: #2563eb !important; /* Knoophintergrond kleurt blauw */
        border-color: #3b82f6 !important;
    }
    
    /* 4. Klik-interactie (active state) */
    div.stButton > button:active {
        transform: scale(0.95) !important; /* Kinkt een klein beetje in */
    }
    
    /* 5. Zorg dat de tekst "SCAN" strak gecentreerd blijft binnen de cirkel */
    div.stButton > button p {
        font-size: 24px !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        margin: 0 !important;
        line-height: 1 !important;
        text-transform: uppercase !important;
    }

    /* 6. CSS voor de voortgangsindicator/animatie zodat deze exact op dezelfde plek staat */
    .scan-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 100%;
        margin: 40px 0;
    }

    .pulsing-loader {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        border: 4px dashed #2563eb;
        animation: spin 4s linear infinite;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 30px rgba(37, 99, 235, 0.2);
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .scan-text {
        color: #3b82f6;
        font-weight: 700;
        letter-spacing: 2px;
        margin-top: 20px;
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
# 4. INPUT FIELDS (VENDOR & PRODUCT)
# ==============================================================================
col1, col2 = st.columns(2)
with col1:
    vendor = st.text_input("Vendor / Fabrikant", placeholder="bijv. Apache, Microsoft")
with col2:
    product = st.text_input("Product Naam", placeholder="bijv. http_server, windows_server")

# Risicoberekening selectie (slider of specifieke versie)
scan_type = st.radio("Kies scanmethode:", ["Time Capsule Scan (Laatste Update)", "Exact Version Scan"])

if scan_type == "Time Capsule Scan (Laatste Update)":
    year = st.slider("Jaar van de laatste software-update:", min_value=2010, max_value=2026, value=2022)
else:
    exact_version = st.text_input("Exacte Versie", placeholder="bijv. 2.4.41")

# ==============================================================================
# 5. DYNAMIC INTERACTION ZONE (BUTTON & ANIMATION PLACEHOLDER)
# ==============================================================================
# Maak een lege placeholder aan. Hierin wisselen we de knop en de animatie uit.
interaction_placeholder = st.empty()

# Controleer of de gebruiker op de scan-knop heeft gedrukt
# We stoppen de knop binnen de placeholder
if interaction_placeholder.button("Scan"):
    
    # 1. Zodra er geklikt is, overschrijven we de placeholder met de gecentreerde animatie.
    # Hierdoor verdwijnt de knop en verschijnt de animatie op PRECIES dezelfde plek.
    for percent_complete in range(0, 101, 5):
        interaction_placeholder.markdown(
            f"""
            <div class="scan-container">
                <div class="pulsing-loader">
                    <span style="color: #ffffff; font-weight: 700; font-size: 24px; transform: rotate(-{{percent_complete*3.6}}deg); display: inline-block;">
                        {percent_complete}%
                    </span>
                </div>
                <div class="scan-text">Mapping CVE Registry...</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        time.sleep(0.1)  # Simuleer scantijd
        
    # 2. Maak de placeholder leeg als de scan klaar is (zodat de animatie verdwijnt)
    interaction_placeholder.empty()

    # ==========================================================================
    # 6. RESULTS SECTION (Wordt pas getoond NA het scannen)
    # ==========================================================================
    st.success("✓ Scan Succesvol Afgerond!")
    
    st.markdown("### Gevonden Risicoprofielen")
    
    with st.expander("🚨 Critical & High Severity Vulnerabilities", expanded=True):
        st.write(f"Er zijn kritieke kwetsbaarheden gevonden voor **{vendor} - {product}**.")
        st.info("Advies: Update per direct naar de meest recente stabiele runtime-versie om remote code execution (RCE) te voorkomen.")
        
    with st.expander("⚠️ Medium Severity Vulnerabilities"):
        st.write("Potentiële denial-of-service (DoS) risico's geïdentificeerd bij langdurige netwerkbelasting.")
        
    with st.expander("ℹ️ Low Severity & Best Practices"):
        st.write("Configuratietip: Schakel ongebruikte modules uit binnen je backend/api.py om het aanvalsoppervlak te verkleinen.")
