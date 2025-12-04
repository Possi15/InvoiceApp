import streamlit as st
import pandas as pd
import time
from ai_engine import analyze_image

# ==========================================
# 1. KONFIGURATION & CSS SYSTEM
# ==========================================

st.set_page_config(
    layout="wide", 
    page_title="Rechnungs-Manager AI",
    initial_sidebar_state="collapsed"
)

# Custom CSS für das "Deep Navy & Glow" Design
def inject_custom_css():
    st.markdown("""
        <style>
        /* --- GLOBAL VARIABLES --- */
        :root {
            --bg-color: #0a192f;
            --card-bg: #112240;
            --text-primary: #e6f1ff;
            --text-secondary: #8892b0;
            --accent-color: #64ffda; /* Teal/Cyan Akzent */
            --accent-glow: rgba(100, 255, 218, 0.1);
            --blue-bright: #00d2ff;
            --border-color: #233554;
        }

        /* --- BACKGROUND & RESET --- */
        .stApp {
            background-color: var(--bg-color);
            color: var(--text-primary);
        }
        
        /* Force Dark Scrollbars */
        ::-webkit-scrollbar { width: 10px; background: var(--bg-color); }
        ::-webkit-scrollbar-thumb { background: #233554; border-radius: 5px; }

        /* --- GLOW EFFECTS (BACKGROUND) --- */
        /* Wir nutzen Pseudo-Elemente auf dem Main Container für den Glow */
        .stApp::before {
            content: "";
            position: absolute;
            top: -10%;
            left: -10%;
            width: 50%;
            height: 50%;
            background: radial-gradient(circle, rgba(0, 210, 255, 0.08), transparent 60%);
            z-index: 0;
            pointer-events: none;
        }
        .stApp::after {
            content: "";
            position: absolute;
            bottom: -10%;
            right: -10%;
            width: 50%;
            height: 50%;
            background: radial-gradient(circle, rgba(100, 255, 218, 0.05), transparent 60%);
            z-index: 0;
            pointer-events: none;
        }

        /* --- TYPOGRAPHY --- */
        h1, h2, h3 {
            font-family: 'Inter', sans-serif;
            font-weight: 700;
            color: var(--text-primary) !important;
            letter-spacing: -0.5px;
        }
        p, label, .stMarkdown {
            color: var(--text-secondary) !important;
            font-family: 'Inter', sans-serif;
        }

        /* --- HEADER CLEANUP --- */
        header[data-testid="stHeader"] {
            background: transparent;
        }
        .block-container {
            padding-top: 3rem;
            padding-bottom: 5rem;
        }

        /* --- COMPONENT STYLING --- */
        
        /* Cards (Upload Box, Results) */
        .css-card {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 20px;
            border: 1px solid var(--border-color);
            box-shadow: 0 10px 30px -10px rgba(2, 12, 27, 0.7);
        }

        /* File Uploader Customization */
        section[data-testid="stFileUploader"] {
            background-color: var(--card-bg);
            border: 1px dashed var(--blue-bright);
            border-radius: 10px;
            padding: 20px;
        }
        section[data-testid="stFileUploader"] small {
            color: var(--text-secondary);
        }

        /* Input Fields */
        div[data-baseweb="input"] {
            background-color: #172a45;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            color: white;
        }
        input.st-ai {
            color: white !important;
        }

        /* Buttons */
        div.stButton > button {
            background-color: transparent;
            color: var(--blue-bright);
            border: 1px solid var(--blue-bright);
            border-radius: 4px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            background-color: rgba(0, 210, 255, 0.1);
            border-color: var(--blue-bright);
            color: #ffffff;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);
        }
        
        /* Primary Button (Analyse Starten) */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(90deg, #00d2ff 0%, #007bff 100%);
            border: none;
            color: #0a192f; /* Dark text on bright button */
            font-weight: bold;
            box-shadow: 0 4px 14px 0 rgba(0, 118, 255, 0.39);
        }
        div.stButton > button[kind="primary"]:hover {
            box-shadow: 0 6px 20px rgba(0, 118, 255, 0.23);
            transform: translateY(-1px);
            color: #0a192f;
        }

        /* Data Editor / Dataframe fixes for dark mode */
        div[data-testid="stDataEditor"] {
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Toast & Alerts */
        div[data-baseweb="notification"] {
            background-color: var(--card-bg);
            border: 1px solid var(--blue-bright);
            color: white;
        }

        /* Dividers */
        hr {
            border-color: var(--border-color);
        }
        
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. SESSION STATE
# ==========================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ==========================================
# 3. LOGIN SCREEN (Neu gestaltet)
# ==========================================

if not st.session_state.authenticated:
    # Spacer, um den Inhalt vertikal zu zentrieren (visuell)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 1, 1])
    
    with col_center:
        st.markdown("""
            <div style='background-color: #112240; padding: 40px; border-radius: 15px; border: 1px solid #233554; text-align: center; box-shadow: 0 20px 50px rgba(0,0,0,0.5);'>
                <h1 style='color: white; font-size: 2rem; margin-bottom: 10px;'>🔒 Secure Access</h1>
                <p style='margin-bottom: 30px;'>Rechnungs-Manager AI System</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Eingabefelder direkt unterhalb des dekorativen Headers
        password = st.text_input("Zugangscode", type="password", placeholder="••••••••")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("System entsperren", type="primary", use_container_width=True):
            if password == "Start123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Zugriff verweigert.")

    st.stop()

# ==========================================
# 4. HAUPT-APPLIKATION (Eingeloggt)
# ==========================================

# Optional: Header-Leiste mit Logout
c1, c2 = st.columns([8, 1])
with c2:
    if st.button("Logout 🔒", key="logout_btn"):
        st.session_state.authenticated = False
        st.rerun()

# --- HERO AREA ---
st.markdown("""
    <div style='text-align: center; padding: 40px 0 60px 0;'>
        <h1 style='font-size: 4rem; margin-bottom: 10px; background: -webkit-linear-gradient(white, #8892b0); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            Rechnungs Fabrik AI
        </h1>
        <p style='font-size: 1.3rem; color: #8892b0; max-width: 600px; margin: 0 auto;'>
            Automatisierte Belegerfassung, Klassifizierung und Export für Finanz-Profis.
            <span style='color: #00d2ff;'>Powered by Neural Networks.</span>
        </p>
    </div>
""", unsafe_allow_html=True)


# Layout: Split 30% / 70%
col_input, col_spacer, col_result = st.columns([10, 1, 20])

# --- LINKER BEREICH: UPLOAD ---
with col_input:
    st.markdown("<h3 style='border-bottom: 2px solid #00d2ff; padding-bottom: 10px; display: inline-block;'>1. Dateneingang</h3>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.9rem; margin-bottom: 20px;'>Lade deine Belege (PDF, JPG, PNG) hier hoch. Die KI startet auf Knopfdruck.</p>", unsafe_allow_html=True)

    # Container-Look für Upload
    with st.container():
        uploaded_files = st.file_uploader(
            "Dateien auswählen",
            type=["jpg", "png", "jpeg", "pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    start_btn = False
    
    # Status Container für dynamische Meldungen
    status_box = st.empty()
    progress_bar = st.empty()

    if uploaded_files:
        st.markdown(f"""
            <div style='background: rgba(0, 210, 255, 0.1); border-left: 4px solid #00d2ff; padding: 10px; border-radius: 4px; margin-bottom: 20px;'>
                <strong style='color: #00d2ff;'>{len(uploaded_files)} Dateien</strong> bereit zur Analyse.
            </div>
        """, unsafe_allow_html=True)
        
        start_btn = st.button("🚀 Analyse Starten", type="primary", use_container_width=True)
    else:
        st.markdown("""
            <div style='padding: 20px; border: 1px dashed #233554; border-radius: 8px; text-align: center; color: #8892b0;'>
                <i>Keine Dateien gewählt</i>
            </div>
        """, unsafe_allow_html=True)


# --- LOGIK: VERARBEITUNG ---
results_list = []
processing_done = False

if start_btn and uploaded_files:
    
    progress_bar.progress(0)
    
    for index, file in enumerate(uploaded_files):
        # Visuelles Feedback
        status_box.markdown(f"""
            <div style='color: #00d2ff; font-weight: bold;'>
                ⏳ Verarbeite: {file.name}...
            </div>
        """, unsafe_allow_html=True)

        # AI ENGINE CALL
        try:
            data = analyze_image(file)
            
            if data:
                data["Datei-Name"] = file.name
                results_list.append(data)
            else:
                st.toast(f"Konnte Daten nicht extrahieren: {file.name}", icon="⚠️")
        except Exception as e:
             st.error(f"Systemfehler bei {file.name}: {e}")

        # Balken update
        progress_bar.progress((index + 1) / len(uploaded_files))
        time.sleep(0.1) # Kurzer visueller Delay für UX

    # Abschluss
    status_box.markdown("""
        <div style='color: #64ffda; font-weight: bold; padding: 10px; border: 1px solid #64ffda; border-radius: 5px; text-align: center;'>
            ✅ Verarbeitung abgeschlossen!
        </div>
    """, unsafe_allow_html=True)
    progress_bar.empty()
    processing_done = True


# --- RECHTER BEREICH: ERGEBNISSE ---
with col_result:
    st.markdown("<h3 style='border-bottom: 2px solid #00d2ff; padding-bottom: 10px; display: inline-block;'>2. Prüfstand & Export</h3>", unsafe_allow_html=True)
    
    if processing_done and results_list:
        # Datenvorbereitung
        df = pd.DataFrame(results_list)

        # Spalten aufräumen
        cols = ["Datei-Name", "datum", "lieferant", "beschreibung", "betrag_gesamt", "kategorie", "rechnungsnummer"]
        final_cols = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
        df = df[final_cols]

        # Datentypen fixen
        if "betrag_gesamt" in df.columns:
             df["betrag_gesamt"] = pd.to_numeric(df["betrag_gesamt"], errors='coerce').fillna(0.0)
        
        if "datum" in df.columns:
            df["datum"] = pd.to_datetime(df["datum"], errors='coerce')
            df["datum"] = df["datum"].dt.date

        # Layout für Metriken oben drüber
        m1, m2 = st.columns(2)
        total_sum = df["betrag_gesamt"].sum() if "betrag_gesamt" in df.columns else 0.0
        
        with m1:
            st.metric("Erfasste Dokumente", len(results_list))
        with m2:
            st.metric("Vorläufige Summe", f"{total_sum:.2f} €")

        st.markdown("<br>", unsafe_allow_html=True)
        st.info("💡 Interaktive Tabelle: Klicke in Zellen zum Bearbeiten.")

        # DATA EDITOR
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            height=500,
            column_config={
                "betrag_gesamt": st.column_config.NumberColumn(
                    "Betrag (€)", 
                    format="%.2f €",
                    help="Brutto Gesamtbetrag"
                ),
                "datum": st.column_config.DateColumn(
                    "Belegdatum", 
                    format="YYYY-MM-DD"
                ),
                "beschreibung": st.column_config.TextColumn(
                    "Inhalt (KI Summary)", 
                    width="large"
                ),
                "lieferant": st.column_config.TextColumn("Lieferant"),
                "kategorie": st.column_config.SelectboxColumn(
                    "Kategorie",
                    options=["Bewirtung", "Reise", "Büro", "Software", "Hardware", "Marketing", "Sonstiges"],
                    required=True
                )
            },
            key="editor_main_modern"
        )

        # Live-Update der Summe nach Editierung
        if "betrag_gesamt" in edited_df.columns:
            new_total = pd.to_numeric(edited_df["betrag_gesamt"], errors='coerce').sum()
            # Kleiner Trick: Metrik in Container anzeigen, um "Checked" Look zu geben
            st.markdown(f"""
                <div style='background: #112240; padding: 15px; border-radius: 8px; margin-top: 20px; display: flex; justify-content: space-between; align-items: center; border: 1px solid #233554;'>
                    <span style='color: #8892b0;'>Geprüfte Gesamtsumme:</span>
                    <span style='color: #64ffda; font-size: 1.5rem; font-weight: bold;'>{new_total:.2f} €</span>
                </div>
            """, unsafe_allow_html=True)

        # EXPORT
        st.markdown("---")
        csv = edited_df.to_csv(index=False).encode('utf-8')

        col_export_l, col_export_r = st.columns([3, 2])
        with col_export_r:
            st.download_button(
                label="💾 CSV Exportieren",
                data=csv,
                file_name="buchhaltung_export.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

    elif not uploaded_files:
        # Leerer State (Placeholder Design)
        st.markdown("""
            <div style='height: 400px; display: flex; flex-direction: column; align-items: center; justify-content: center; border: 2px dashed #233554; border-radius: 12px; margin-top: 20px; color: #495670;'>
                <div style='font-size: 3rem; margin-bottom: 10px; opacity: 0.5;'>📊</div>
                <p>Warte auf Daten...</p>
                <small>Bitte links Dateien hochladen und Analyse starten.</small>
            </div>
        """, unsafe_allow_html=True)