import streamlit as st
import pandas as pd
import time
from ai_engine import analyze_image

# ==========================================
# 1. KONFIGURATION & CSS SYSTEM
# ==========================================

st.set_page_config(layout="wide", page_title="Rechnungs-Manager AI", initial_sidebar_state="collapsed")

def inject_custom_css():
    st.markdown("""
        <style>
        /* --- FARBPALETTE & VARIABLES --- */
        :root {
            --bg-dark: #020c1b;
            --card-bg: #112240;
            --text-highlight: #e6f1ff;
            --text-muted: #8892b0;
            --cyan: #64ffda;
            --blue-neon: #00d2ff;
        }

        /* --- GLOBAL RESET --- */
        .stApp {
            background-color: var(--bg-dark);
            color: var(--text-highlight);
        }

        /* --- DARK MODE UPLOADER FIX (Das Wichtigste!) --- */
        /* Den weißen Hintergrund entfernen und Text weiß machen */
        [data-testid='stFileUploader'] {
            width: 100%;
        }
        [data-testid='stFileUploader'] section {
            background-color: #172a45 !important; /* Dunkler Hintergrund */
            border: 2px dashed var(--blue-neon) !important; /* Neon Rahmen */
            border-radius: 10px;
            padding: 20px;
        }
        /* Den "Browse Files" Button stylen */
        [data-testid='stFileUploader'] button {
            background-color: transparent !important;
            color: var(--cyan) !important;
            border: 1px solid var(--cyan) !important;
        }
        /* Die Texte "Drag and Drop" etc. weiß machen */
        [data-testid='stFileUploader'] span, 
        [data-testid='stFileUploader'] div,
        [data-testid='stFileUploader'] small {
            color: var(--text-muted) !important;
        }
        /* Entfernt das weiße Icon falls vorhanden und färbt es */
        [data-testid='stFileUploader'] svg {
            fill: var(--blue-neon) !important;
        }

        /* --- CARD HEADER STYLING --- */
        .step-header {
            display: flex;
            align-items: center;
            background: linear-gradient(90deg, #112240 0%, #172a45 100%);
            padding: 15px 20px;
            border-radius: 10px 10px 0 0;
            border-bottom: 1px solid #233554;
            margin-bottom: 20px;
        }
        .step-number {
            background: var(--blue-neon);
            color: #020c1b;
            width: 35px; height: 35px;
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.2rem; font-weight: 800;
            margin-right: 15px;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.6);
        }
        .step-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            letter-spacing: 0.5px;
        }

        /* --- ANIMATION: RADAR SCANNER --- */
        @keyframes scan {
            0% { top: 0%; opacity: 0; }
            10% { opacity: 1; }
            90% { opacity: 1; }
            100% { top: 100%; opacity: 0; }
        }
        .scanner-box {
            position: relative;
            height: 150px;
            background: #112240;
            border: 1px solid var(--blue-neon);
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 20px;
            box-shadow: inset 0 0 20px rgba(0, 210, 255, 0.1);
        }
        .scanner-line {
            position: absolute;
            width: 100%;
            height: 4px;
            background: var(--cyan);
            box-shadow: 0 0 15px var(--cyan), 0 0 30px var(--cyan);
            animation: scan 2s infinite linear;
            left: 0;
            z-index: 2;
        }
        .scanner-text {
            color: var(--cyan);
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 1.2rem;
            z-index: 1;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        /* --- ANIMATION: SUCCESS --- */
        @keyframes pulse-green {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(100, 255, 218, 0.7); }
            70% { transform: scale(1.05); box-shadow: 0 0 0 10px rgba(100, 255, 218, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(100, 255, 218, 0); }
        }
        .success-box {
            text-align: center;
            padding: 30px;
            background: rgba(100, 255, 218, 0.1);
            border: 1px solid var(--cyan);
            border-radius: 10px;
            margin-top: 20px;
            animation: pulse-green 2s infinite;
        }

        /* --- BUTTONS --- */
        div.stButton > button {
            width: 100%; /* Volle Breite */
            border-radius: 8px;
            padding: 0.75rem 1rem;
            font-size: 1.1rem;
        }
        /* Primary Button Style */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(45deg, #00d2ff, #007bff);
            border: none;
            color: white;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: transform 0.2s;
        }
        div.stButton > button[kind="primary"]:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(0, 210, 255, 0.6);
        }

        /* --- CONTAINER STYLING --- */
        .main-card {
            background-color: #0f1c30; /* Sehr dunkles Blau */
            border: 1px solid #233554;
            border-radius: 15px;
            padding: 0; /* Padding innen entfernen für Header */
            margin-bottom: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
            overflow: hidden;
        }
        .card-content {
            padding: 25px;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. LOGIN (Kurzfassung)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<h2 style='text-align:center; color:white;'>🔒 Login</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Passwort", type="password")
        if st.button("Enter", type="primary"):
            if pwd == "Start123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Falsch.")
    st.stop()

# ==========================================
# 3. HEADER & TITLE
# ==========================================
st.markdown("""
    <div style='text-align: center; padding: 20px 0 40px 0;'>
        <h1 style='font-size: 3.5rem; margin: 0; text-shadow: 0 0 20px rgba(0,210,255,0.5);'>
            Rechnungs Scanner <span style='color:#64ffda;'>PRO</span>
        </h1>
        <p style='color: #8892b0; font-size: 1.2rem;'>Automatisierte KI-Extraktion</p>
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.5], gap="large")

# ==========================================
# LINKS: UPLOAD & ANALYSE
# ==========================================
with col_left:
    # START CARD HTML
    st.markdown("""
        <div class='main-card'>
            <div class='step-header'>
                <div class='step-number'>1</div>
                <div class='step-title'>Upload & Scan</div>
            </div>
            <div class='card-content'>
    """, unsafe_allow_html=True)

    # --- UPLOADER ---
    # Der CSS Fix oben macht diesen Bereich jetzt dunkel
    uploaded_files = st.file_uploader(
        "Dateien hier ablegen",
        type=["jpg", "png", "pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed" 
    )

    # --- LOGIC VARIABLES ---
    start_btn = False
    
    # Abstand
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # --- BUTTON LOGIC ---
    if uploaded_files:
        # Großer sichtbarer Button
        start_btn = st.button(f"⚡ {len(uploaded_files)} DATEIEN ANALYSIEREN", type="primary")
    else:
        # Platzhalter Text wenn leer
        st.markdown("""
            <div style='text-align: center; color: #495670; padding: 20px; border: 1px dashed #233554; border-radius: 8px;'>
                <i>Bitte Dateien oben auswählen</i>
            </div>
        """, unsafe_allow_html=True)

    # --- ANIMATION AREA ---
    animation_placeholder = st.empty()
    
    # END CARD HTML
    st.markdown("</div></div>", unsafe_allow_html=True)


# ==========================================
# VERARBEITUNG & ANIMATION
# ==========================================
results_list = []
processing_done = False

if start_btn and uploaded_files:
    
    # 1. ANIMATION: SCANNING STARTET
    # Wir zeigen den Scanner im Placeholder an
    animation_placeholder.markdown("""
        <div class='scanner-box'>
            <div class='scanner-line'></div>
            <div class='scanner-text'>AI ANALYSE LÄUFT...</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Progress Bar (Optional, für Details)
    progress_bar = st.progress(0)
    
    for index, file in enumerate(uploaded_files):
        # AI Aufruf simulieren (oder echt machen)
        try:
            data = analyze_image(file)
            if data:
                data["Datei-Name"] = file.name
                results_list.append(data)
        except Exception as e:
            st.error(f"Fehler: {e}")
        
        # Kleiner Sleep für den Effekt (Scanner wirkt besser)
        time.sleep(0.8) 
        progress_bar.progress((index + 1) / len(uploaded_files))

    progress_bar.empty()
    
    # 2. ANIMATION: SUCCESS
    animation_placeholder.markdown("""
        <div class='success-box'>
            <h2 style='color: #64ffda; margin:0;'>✅ FERTIG!</h2>
            <p style='margin:0;'>Daten erfolgreich extrahiert.</p>
        </div>
    """, unsafe_allow_html=True)
    
    processing_done = True


# ==========================================
# RECHTS: ERGEBNISSE
# ==========================================
with col_right:
    # START CARD HTML
    st.markdown("""
        <div class='main-card'>
            <div class='step-header'>
                <div class='step-number'>2</div>
                <div class='step-title'>Ergebnis</div>
            </div>
            <div class='card-content'>
    """, unsafe_allow_html=True)

    if processing_done and results_list:
        df = pd.DataFrame(results_list)
        
        # Spalten aufräumen
        cols = ["Datei-Name", "datum", "lieferant", "beschreibung", "betrag_gesamt", "kategorie"]
        final_cols = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
        df = df[final_cols]
        
        if "betrag_gesamt" in df.columns:
            df["betrag_gesamt"] = pd.to_numeric(df["betrag_gesamt"], errors='coerce').fillna(0.0)

        # Editor
        st.info("💡 Du kannst die Tabelle direkt bearbeiten:")
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            height=450,
            column_config={
                "betrag_gesamt": st.column_config.NumberColumn("Betrag", format="%.2f €"),
                "beschreibung": st.column_config.TextColumn("Inhalt", width="medium"),
            },
            key="final_editor"
        )
        
        # Summe
        total = edited_df["betrag_gesamt"].sum() if "betrag_gesamt" in edited_df.columns else 0
        
        # Abschlussleiste
        st.markdown("---")
        c_sum, c_btn = st.columns([1, 1])
        with c_sum:
            st.markdown(f"<div style='font-size:1.8rem; font-weight:bold; color:#64ffda;'>Summe: {total:.2f} €</div>", unsafe_allow_html=True)
        with c_btn:
            csv = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 CSV Exportieren", data=csv, file_name="export.csv", mime="text/csv", type="primary")

    else:
        # LEERZUSTAND
        st.markdown("""
            <div style='height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0.5;'>
                <div style='font-size: 5rem;'>📊</div>
                <p>Noch keine Daten vorhanden.</p>
            </div>
        """, unsafe_allow_html=True)

    # END CARD HTML
    st.markdown("</div></div>", unsafe_allow_html=True)