import streamlit as st
import pandas as pd
import time
import concurrent.futures
from datetime import datetime

# ==========================================
# 0. KONFIGURATION & SETUP
# ==========================================
st.set_page_config(layout="wide", page_title="Rechnungs-Manager AI", initial_sidebar_state="collapsed")

# --- MOCK FUNKTION (Simuliert die AI) ---
# Falls du deine echte AI nutzen willst, importiere sie hier und tausche den Aufruf unten aus.
def analyze_image(file):
    # Simuliert eine Verzögerung (AI Denken)
    time.sleep(1.0)
    
    # Simulierter Fehler bei Dateien mit "error" im Namen
    if "error" in file.name.lower():
        return None
        
    # Simulierte Datenrückgabe
    return {
        "lieferant": "Amazon Europe Core S.à r.l.",
        "beschreibung": "Server Equipment & Kabel",
        "betrag_gesamt": 45.99,
        "datum": "2023-11-24",
        "kategorie": "IT & Hardware",
        "rechnungsnummer": "INV-2023-998877"
    }

# ==========================================
# 1. CSS STYLING (Das Design)
# ==========================================
def inject_custom_css():
    st.markdown("""
        <style>
        :root { --bg-dark: #020c1b; --card-bg: #112240; --text-highlight: #e6f1ff; --text-muted: #8892b0; --cyan: #64ffda; --blue-neon: #00d2ff; }
        .stApp { background-color: var(--bg-dark); color: var(--text-highlight); }
        
        /* Uploader Styling */
        [data-testid='stFileUploader'] section { background-color: #172a45 !important; border: 2px dashed var(--blue-neon) !important; border-radius: 10px; }
        [data-testid='stFileUploader'] button { border: 1px solid var(--cyan) !important; color: var(--cyan) !important; }
        [data-testid='stFileUploader'] span, [data-testid='stFileUploader'] small { color: var(--text-muted) !important; }
        [data-testid='stFileUploader'] svg { fill: var(--blue-neon) !important; }

        /* Headers */
        .step-header { display: flex; align-items: center; background: linear-gradient(90deg, #112240 0%, #172a45 100%); padding: 15px 20px; border-radius: 10px 10px 0 0; border-bottom: 1px solid #233554; }
        .step-number { background: var(--blue-neon); color: #020c1b; width: 35px; height: 35px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 800; margin-right: 15px; box-shadow: 0 0 10px rgba(0, 210, 255, 0.6); }
        .step-title { font-size: 1.5rem; font-weight: 700; color: white; }
        
        /* Cards */
        .main-card { background-color: #0f1c30; border: 1px solid #233554; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); overflow: visible; }
        .card-content { padding: 20px; }

        /* Animationen */
        @keyframes scan { 0% { top: 0%; opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { top: 100%; opacity: 0; } }
        .scanner-box { position: relative; height: 120px; background: #112240; border: 1px solid var(--blue-neon); border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center; margin-top: 20px; }
        .scanner-line { position: absolute; width: 100%; height: 4px; background: var(--cyan); box-shadow: 0 0 15px var(--cyan); animation: scan 2s infinite linear; left: 0; z-index: 2; }
        .scanner-text { color: var(--cyan); font-family: monospace; font-weight: bold; z-index: 1; letter-spacing: 2px; }
        
        /* Buttons */
        div.stButton > button[kind="primary"] { background: linear-gradient(45deg, #00d2ff, #007bff); border: none; color: white; font-weight: bold; transition: 0.2s; }
        div.stButton > button[kind="primary"]:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 210, 255, 0.6); }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. SESSION STATE MANAGEMENT
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "analyzed_data" not in st.session_state:
    st.session_state.analyzed_data = [] 
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False

# ==========================================
# 3. HELPER FUNKTIONEN (Logik)
# ==========================================
def process_single_file(file):
    """Wrapper für die Analyse mit Fehlerbehandlung"""
    try:
        data = analyze_image(file) # Hier wird die Mock/AI Funktion gerufen
        
        if data:
            data["Datei-Name"] = file.name
            return data
        else:
            # Fallback bei nicht lesbarer Datei
            return {
                "Datei-Name": file.name,
                "lieferant": "❌ FEHLER",
                "beschreibung": "Datei nicht lesbar",
                "betrag_gesamt": 0.00,
                "datum": "",
                "kategorie": "Error"
            }
    except Exception as e:
        # Systemfehler abfangen
        return {
            "Datei-Name": file.name,
            "lieferant": "❌ SYSTEM-ERROR",
            "beschreibung": str(e),
            "betrag_gesamt": 0.00,
            "kategorie": "Error"
        }

def run_batch_processing(uploaded_files, progress_bar, status_text):
    """Verarbeitet Dateien parallel"""
    results = []
    total_files = len(uploaded_files)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {executor.submit(process_single_file, f): f for f in uploaded_files}
        completed_count = 0
        
        for future in concurrent.futures.as_completed(future_to_file):
            result = future.result()
            results.append(result)
            
            completed_count += 1
            progress_bar.progress(completed_count / total_files)
            status_text.text(f"Analysiere Datei {completed_count}/{total_files}...")
            
    return results

# ==========================================
# 4. LOGIN SCREEN
# ==========================================
if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,1,1])
    with c2:
        st.markdown("<div class='main-card' style='padding:40px; text-align:center;'><h2 style='color:white;'>🔒 Secure Access</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Passwort eingeben", type="password", label_visibility="collapsed", placeholder="Passwort")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("UNLOCK SYSTEM", type="primary"):
            if pwd == "Start123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Zugriff verweigert.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. HAUPTANWENDUNG (Layout)
# ==========================================

# Titel Header
st.markdown("""
    <div style='text-align: center; padding: 20px 0 40px 0;'>
        <h1 style='font-size: 3rem; margin: 0; text-shadow: 0 0 20px rgba(0,210,255,0.5);'>
            RECHNUNGS SCANNER <span style='color:#64ffda;'>AI</span>
        </h1>
        <p style='color: #8892b0;'>Intelligent Document Processing Core</p>
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.5], gap="large")

# --- LINKE SPALTE: UPLOAD & CONTROL ---
with col_left:
    st.markdown("""
        <div class='main-card'>
            <div class='step-header'>
                <div class='step-number'>1</div>
                <div class='step-title'>Upload & Scan</div>
            </div>
            <div class='card-content'>
    """, unsafe_allow_html=True)

    # Reset Button falls Scan fertig ist
    if st.session_state.processing_complete:
        if st.button("🔄 Neuer Scan starten"):
            st.session_state.analyzed_data = []
            st.session_state.processing_complete = False
            st.rerun()

    uploaded_files = st.file_uploader(
        "Dateien hier ablegen",
        type=["jpg", "png", "pdf", "jpeg"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        disabled=st.session_state.processing_complete
    )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    if uploaded_files and not st.session_state.processing_complete:
        if st.button(f"⚡ SCAN STARTEN ({len(uploaded_files)} FILES)", type="primary"):
            
            # Scanner Animation
            scanner_placeholder = st.empty()
            scanner_placeholder.markdown("""
                <div class='scanner-box'>
                    <div class='scanner-line'></div>
                    <div class='scanner-text'>NEURALE VERARBEITUNG...</div>
                </div>
            """, unsafe_allow_html=True)
            
            prog_bar = st.progress(0)
            status_txt = st.empty()
            
            # Verarbeitung starten
            results = run_batch_processing(uploaded_files, prog_bar, status_txt)
            
            # Ergebnisse speichern
            st.session_state.analyzed_data = results
            st.session_state.processing_complete = True
            
            # UI Cleanup
            time.sleep(0.5)
            scanner_placeholder.empty()
            prog_bar.empty()
            status_txt.empty()
            st.rerun()

    elif not uploaded_files:
        st.caption("Bitte PDF oder Bilder hochladen.")

    st.markdown("</div></div>", unsafe_allow_html=True)
    
    if st.session_state.processing_complete:
         st.markdown(f"""
            <div style='background: rgba(100, 255, 218, 0.1); border: 1px solid #64ffda; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color:#64ffda; margin:0;'>✅ Scan Abgeschlossen</h3>
                <p style='margin:0;'>{len(st.session_state.analyzed_data)} Dokumente verarbeitet</p>
            </div>
        """, unsafe_allow_html=True)

# --- RECHTE SPALTE: ERGEBNIS TABELLE ---
with col_right:
    st.markdown("""
        <div class='main-card'>
            <div class='step-header'>
                <div class='step-number'>2</div>
                <div class='step-title'>Ergebnisse prüfen</div>
            </div>
            <div class='card-content'>
    """, unsafe_allow_html=True)

    if st.session_state.analyzed_data:
        df = pd.DataFrame(st.session_state.analyzed_data)
        
        # Spalten sortieren
        preferred_cols = ["Datei-Name", "datum", "lieferant", "betrag_gesamt", "kategorie", "beschreibung"]
        cols_to_show = [c for c in preferred_cols if c in df.columns]
        cols_to_show += [c for c in df.columns if c not in cols_to_show]
        df = df[cols_to_show]

        # Datentyp Konvertierung (Nur "betrag_gesamt" für Summe, Rest bleibt Text um Fehler zu vermeiden)
        if "betrag_gesamt" in df.columns:
             # Umwandlung von String zu Float, Fehler werden 0.0
             df["betrag_gesamt"] = pd.to_numeric(df["betrag_gesamt"], errors='coerce').fillna(0.0)

        # STABILER EDITOR (Ohne column_config, damit keine Type-Errors entstehen)
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            height=500,
            key="data_editor_safe"
        )
        
        # Zusammenfassung
        st.markdown("---")
        col_sum, col_act = st.columns([1, 1])
        
        total_sum = 0.0
        if "betrag_gesamt" in edited_df.columns:
            total_sum = edited_df["betrag_gesamt"].sum()
        
        with col_sum:
            st.markdown(f"<div style='font-size:1.2rem; color:#8892b0;'>Summe (Erkannt)</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:2.2rem; font-weight:bold; color:#64ffda;'>{total_sum:,.2f} €</div>", unsafe_allow_html=True)
            
        with col_act:
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            csv = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 EXPORT CSV",
                data=csv,
                file_name=f"export_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

    else:
        # Platzhalter leer
        st.markdown("""
            <div style='height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0.3;'>
                <div style='font-size: 4rem; filter: grayscale(100%);'>📊</div>
                <p style='margin-top:10px;'>Daten erscheinen hier...</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)