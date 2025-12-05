import streamlit as st
import pandas as pd
import time
import concurrent.futures
from datetime import datetime

# ==========================================
# 0. SETUP & MOCKING (Für Demo-Zwecke)
# ==========================================
st.set_page_config(layout="wide", page_title="Rechnungs-Manager AI", initial_sidebar_state="collapsed")

# HINWEIS: Hier deinen echten Import wieder aktivieren:
# from ai_engine import analyze_image

# MOCK-FUNKTION (Damit der Code ohne externes Modul läuft - bitte entfernen, wenn ai_engine da ist)
def analyze_image(file):
    # Simuliert eine AI-Analyse
    time.sleep(1.5) # Simuliert Netzwerk-Latenz
    if "error" in file.name.lower():
        return None
    return {
        "lieferant": "Amazon Web Services",
        "beschreibung": "Server Hosting Gebühr",
        "betrag_gesamt": 45.20,
        "datum": "2023-11-24",
        "kategorie": "IT & Software",
        "rechnungsnummer": "INV-2023-001"
    }

# ==========================================
# 1. CSS & STYLING
# ==========================================
def inject_custom_css():
    st.markdown("""
        <style>
        :root { --bg-dark: #020c1b; --card-bg: #112240; --text-highlight: #e6f1ff; --text-muted: #8892b0; --cyan: #64ffda; --blue-neon: #00d2ff; }
        .stApp { background-color: var(--bg-dark); color: var(--text-highlight); }
        
        /* Uploader Styling */
        [data-testid='stFileUploader'] section { background-color: #172a45 !important; border: 2px dashed var(--blue-neon) !important; border-radius: 10px; }
        [data-testid='stFileUploader'] button { border: 1px solid var(--cyan) !important; color: var(--cyan) !important; }
        
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
        
        /* Buttons & Dataframe */
        div.stButton > button[kind="primary"] { background: linear-gradient(45deg, #00d2ff, #007bff); border: none; color: white; font-weight: bold; transition: 0.2s; }
        div.stButton > button[kind="primary"]:hover { transform: scale(1.02); box-shadow: 0 0 20px rgba(0, 210, 255, 0.6); }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. SESSION STATE MANAGEMENT (WICHTIG!)
# ==========================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "analyzed_data" not in st.session_state:
    st.session_state.analyzed_data = [] # Hier speichern wir die Ergebnisse dauerhaft
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False

# ==========================================
# 3. HELPER FUNKTIONEN
# ==========================================
def process_single_file(file):
    """Wrapper für die AI-Analyse mit Fehlerbehandlung"""
    try:
        # Hier wird die externe Funktion aufgerufen
        data = analyze_image(file)
        
        if data:
            data["Datei-Name"] = file.name
            return data
        else:
            return {
                "Datei-Name": file.name,
                "lieferant": "❌ FEHLER",
                "beschreibung": "Nicht lesbar / Unscharf",
                "betrag_gesamt": 0.00,
                "datum": None,
                "kategorie": "Error"
            }
    except Exception as e:
        return {
            "Datei-Name": file.name,
            "lieferant": "❌ SYSTEM-ERROR",
            "beschreibung": str(e),
            "betrag_gesamt": 0.00,
            "kategorie": "Error"
        }

def run_batch_processing(uploaded_files, progress_bar, status_text):
    """Parallele Verarbeitung der Dateien"""
    results = []
    total_files = len(uploaded_files)
    
    # ThreadPoolExecutor für parallele Ausführung (schneller als for-loop)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Wir mappen die Dateien auf die Funktion
        future_to_file = {executor.submit(process_single_file, f): f for f in uploaded_files}
        
        completed_count = 0
        for future in concurrent.futures.as_completed(future_to_file):
            result = future.result()
            results.append(result)
            
            # Progress Update
            completed_count += 1
            progress_val = completed_count / total_files
            progress_bar.progress(progress_val)
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
# 5. HAUPTANWENDUNG
# ==========================================

# Header
st.markdown("""
    <div style='text-align: center; padding: 20px 0 40px 0;'>
        <h1 style='font-size: 3rem; margin: 0; text-shadow: 0 0 20px rgba(0,210,255,0.5);'>
            RECHNUNGS SCANNER <span style='color:#64ffda;'>AI</span>
        </h1>
        <p style='color: #8892b0;'>Intelligent Document Processing Core</p>
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.5], gap="large")

# --- LINKE SPALTE: UPLOAD & KONTROLLE ---
with col_left:
    st.markdown("""
        <div class='main-card'>
            <div class='step-header'>
                <div class='step-number'>1</div>
                <div class='step-title'>Input Data</div>
            </div>
            <div class='card-content'>
    """, unsafe_allow_html=True)

    # Reset Button (falls man von vorne beginnen will)
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
        disabled=st.session_state.processing_complete # Deaktivieren wenn fertig
    )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # UI Logik für den Start-Button
    if uploaded_files and not st.session_state.processing_complete:
        if st.button(f"⚡ SCAN STARTEN ({len(uploaded_files)} FILES)", type="primary"):
            
            # Animation Placeholder
            scanner_placeholder = st.empty()
            scanner_placeholder.markdown("""
                <div class='scanner-box'>
                    <div class='scanner-line'></div>
                    <div class='scanner-text'>NEURALE VERARBEITUNG...</div>
                </div>
            """, unsafe_allow_html=True)
            
            prog_bar = st.progress(0)
            status_txt = st.empty()
            
            # Start Processing
            results = run_batch_processing(uploaded_files, prog_bar, status_txt)
            
            # Daten in Session State speichern
            st.session_state.analyzed_data = results
            st.session_state.processing_complete = True
            
            # Cleanup UI
            time.sleep(0.5)
            scanner_placeholder.empty()
            prog_bar.empty()
            status_txt.empty()
            st.rerun() # Rerun um UI zu aktualisieren

    # Leere State Anzeige
    elif not uploaded_files:
        st.caption("Unterstützte Formate: PDF, JPG, PNG")

    st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Success Indikator (Nur anzeigen wenn fertig)
    if st.session_state.processing_complete:
         st.markdown(f"""
            <div style='background: rgba(100, 255, 218, 0.1); border: 1px solid #64ffda; padding: 20px; border-radius: 10px; text-align: center;'>
                <h3 style='color:#64ffda; margin:0;'>✅ Scan Abgeschlossen</h3>
                <p style='margin:0;'>{len(st.session_state.analyzed_data)} Dokumente verarbeitet</p>
            </div>
        """, unsafe_allow_html=True)

# --- RECHTE SPALTE: DATEN EDITOR ---
with col_right:
    st.markdown("""
        <div class='main-card'>
            <div class='step-header'>
                <div class='step-number'>2</div>
                <div class='step-title'>Data Validation</div>
            </div>
            <div class='card-content'>
    """, unsafe_allow_html=True)

    if st.session_state.analyzed_data:
        # DataFrame erstellen
        df = pd.DataFrame(st.session_state.analyzed_data)
        
        # Sicherstellen, dass die Spaltenreihenfolge passt
        preferred_cols = ["Datei-Name", "datum", "lieferant", "betrag_gesamt", "kategorie", "beschreibung"]
        # Vorhandene Spalten filtern
        cols_to_show = [c for c in preferred_cols if c in df.columns]
        # Restliche Spalten anhängen
        cols_to_show += [c for c in df.columns if c not in cols_to_show]
        
        df = df[cols_to_show]

        # Datentyp Konvertierung für saubere Anzeige
        if "betrag_gesamt" in df.columns:
            df["betrag_gesamt"] = pd.to_numeric(df["betrag_gesamt"], errors='coerce').fillna(0.0)

        # ... (dein vorhandener Code zum Filtern der Spalten)
        df = df[cols_to_show]

        # --- HIER IST DER FIX ---
        
        # 1. Betrag sicher in Zahlen umwandeln (Kommas durch Punkte ersetzen falls nötig)
        if "betrag_gesamt" in df.columns:
            # Falls Strings wie "12,50" kommen, erst Komma zu Punkt
            df["betrag_gesamt"] = df["betrag_gesamt"].astype(str).str.replace(',', '.', regex=False)
            df["betrag_gesamt"] = pd.to_numeric(df["betrag_gesamt"], errors='coerce').fillna(0.0)

        # 2. Datum sicher von String ("2023-11-24") in echtes Datumsobjekt umwandeln
        if "datum" in df.columns:
            df["datum"] = pd.to_datetime(df["datum"], errors='coerce').dt.date

        # --- ENDE FIX ---

        # DATA EDITOR (ab hier dein normaler Code weiter)
        edited_df = st.data_editor(...)

        # DATA EDITOR
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            height=500,
            column_config={
                "betrag_gesamt": st.column_config.NumberColumn("Betrag", format="%.2f €", min_value=0),
                "datum": st.column_config.DateColumn("Datum", format="YYYY-MM-DD"),
                "lieferant": st.column_config.TextColumn("Lieferant", width="medium"),
                "kategorie": st.column_config.SelectboxColumn("Kategorie", options=["Büro", "IT & Software", "Reise", "Marketing", "Sonstiges", "Error"], required=True)
            },
            key="data_editor_main"
        )
        
        # Summary Section
        st.markdown("---")
        col_sum, col_act = st.columns([1, 1])
        
        total_sum = edited_df["betrag_gesamt"].sum() if "betrag_gesamt" in edited_df.columns else 0.0
        
        with col_sum:
            st.markdown(f"<div style='font-size:1.2rem; color:#8892b0;'>Gesamtsumme (Netto)</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:2.2rem; font-weight:bold; color:#64ffda;'>{total_sum:,.2f} €</div>", unsafe_allow_html=True)
            
        with col_act:
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            csv = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 EXPORT CSV",
                data=csv,
                file_name=f"export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

    else:
        # Platzhalter wenn keine Daten
        st.markdown("""
            <div style='height: 300px; display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0.3;'>
                <div style='font-size: 4rem; filter: grayscale(100%);'>📊</div>
                <p style='margin-top:10px;'>Warte auf Scan-Daten...</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)