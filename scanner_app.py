import streamlit as st
import pandas as pd
import time
# from PIL import Image
from ai_engine import analyze_image

# ==========================================
# 1. KONFIGURATION & CSS SYSTEM
# ==========================================

st.set_page_config(
    layout="wide", 
    page_title="Rechnungs-Manager AI",
    initial_sidebar_state="collapsed"
)

def inject_custom_css():
    st.markdown("""
        <style>
        /* --- FARBPALETTE --- */
        :root {
            --bg-dark: #0a192f;
            --card-bg: #112240;
            --text-main: #e6f1ff;
            --text-muted: #8892b0;
            --cyan: #64ffda;
            --blue-neon: #00d2ff;
            --border-color: #233554;
        }

        /* --- GLOBAL SETUP --- */
        .stApp {
            background-color: var(--bg-dark);
            color: var(--text-main);
        }
        
        /* Hintergrund-Glow (Subtil) */
        .stApp::before {
            content: ""; position: absolute; top: -10%; left: -10%; width: 60%; height: 60%;
            background: radial-gradient(circle, rgba(0, 210, 255, 0.05), transparent 70%);
            pointer-events: none; z-index: 0;
        }

        /* --- TYPOGRAPHIE --- */
        h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 700; color: var(--text-main) !important; }
        p, label, .stMarkdown { color: var(--text-muted); }

        /* --- BUTTON STYLING (NAVY FILL + HOVER) --- */
        /* Basis Button */
        div.stButton > button {
            background-color: var(--bg-dark); /* Navy Füllung */
            color: var(--blue-neon);
            border: 1px solid var(--blue-neon);
            border-radius: 6px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        
        /* Hover Effekt */
        div.stButton > button:hover {
            background-color: var(--blue-neon); /* Füllt sich hellblau */
            color: var(--bg-dark); /* Text wird dunkel */
            border-color: var(--blue-neon);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.5); /* Glow */
            transform: translateY(-2px);
        }
        
        /* Primary Button (Start Analyse) - Extra Hervorhebung */
        div.stButton > button[kind="primary"] {
            background-color: var(--card-bg);
            border: 2px solid var(--cyan);
            color: var(--cyan);
        }
        div.stButton > button[kind="primary"]:hover {
            background-color: var(--cyan);
            color: var(--bg-dark);
            box-shadow: 0 0 20px rgba(100, 255, 218, 0.4);
        }

        /* --- CARDS & UMRANDUNGEN (Die Schritte) --- */
        /* Wir erstellen eine CSS-Klasse für die Container, die wir per Markdown injecten */
        .step-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px -15px rgba(2, 12, 27, 0.7);
            height: 100%;
        }
        
        /* Header innerhalb der Cards */
        .card-header {
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
            margin-bottom: 20px;
            font-size: 1.1rem;
            font-weight: bold;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* Nummerierung (1, 2) Kreise */
        .step-number {
            background: var(--blue-neon);
            color: var(--bg-dark);
            width: 24px; height: 24px;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 800;
        }

        /* --- WORKFLOW VISUAL (Oben) --- */
        .workflow-box {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            margin: 20px auto 50px auto;
            padding: 15px;
            background: rgba(17, 34, 64, 0.5);
            border: 1px dashed var(--border-color);
            border-radius: 50px;
            width: fit-content;
        }
        .wf-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-main);
            font-weight: 500;
        }
        .wf-arrow { color: var(--text-muted); font-size: 1.2rem; }
        .wf-icon { color: var(--cyan); font-size: 1.2rem; }

        /* --- SONSTIGES --- */
        div[data-testid="stFileUploader"] {
            padding: 10px;
        }
        
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. SESSION STATE & LOGIN
# ==========================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col_l, col_center, col_r = st.columns([1, 1, 1])
    
    with col_center:
        # Login Card Design
        st.markdown("""
            <div style='background-color: #112240; padding: 40px; border-radius: 12px; border: 1px solid #233554; text-align: center;'>
                <h2 style='color: white; margin-bottom: 0;'>🔐 Secure Access</h2>
                <p style='font-size: 0.9rem; margin-bottom: 20px;'>Rechnungs-Manager AI</p>
            </div>
        """, unsafe_allow_html=True)
        
        password = st.text_input("Zugangscode", type="password", label_visibility="collapsed", placeholder="Passwort eingeben...")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Anmelden", use_container_width=True):
            if password == "Start123":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Zugriff verweigert.")
    st.stop()

# ==========================================
# 3. HAUPT-LAYOUT
# ==========================================

# Header & Logout
c1, c2 = st.columns([10, 1])
with c2:
    if st.button("Abmelden"):
        st.session_state.authenticated = False
        st.rerun()

# --- TITEL & VALUE PROPOSITION ---
st.markdown("""
    <div style='text-align: center; margin-bottom: 10px;'>
        <h1 style='font-size: 3.5rem; margin-bottom: 5px;'>Rechnungs Fabrik <span style='color: #00d2ff;'>AI</span></h1>
        <p style='font-size: 1.2rem; color: #8892b0;'>Vom Papierchaos zur perfekten Buchhaltung in Sekunden.</p>
    </div>
    
    <!-- WORKFLOW VISUALISIERUNG -->
    <div class='workflow-box'>
        <div class='wf-item'><span class='wf-icon'>📄</span> PDF/Bild Upload</div>
        <div class='wf-arrow'>➔</div>
        <div class='wf-item'><span class='wf-icon'>🧠</span> KI Extraktion</div>
        <div class='wf-arrow'>➔</div>
        <div class='wf-item'><span class='wf-icon'>📊</span> Fertige CSV/Tabelle</div>
    </div>
""", unsafe_allow_html=True)

# Layout Spalten
col_left, col_right = st.columns([1, 2])

# ==========================================
# LINKS: INPUT (STEP 1)
# ==========================================
with col_left:
    # START CARD 1
    st.markdown("""
        <div class='step-card'>
            <div class='card-header'>
                <span class='step-number'>1</span> Dateneingang
            </div>
    """, unsafe_allow_html=True)
    
    st.caption("Lade hier deine Rechnungen hoch.")
    
    uploaded_files = st.file_uploader(
        "Files",
        type=["jpg", "png", "jpeg", "pdf"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    start_btn = False
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if uploaded_files:
        st.info(f"{len(uploaded_files)} Dokumente bereit.")
        # Der Primary Button hat jetzt unser Custom Design
        start_btn = st.button("⚡ Analyse Starten", type="primary", use_container_width=True)
    else:
        st.markdown("<div style='text-align:center; padding: 20px; color: #495670; border: 1px dashed #233554; border-radius:8px;'>Warte auf Upload...</div>", unsafe_allow_html=True)

    # Platzhalter für Status
    st.markdown("<br>", unsafe_allow_html=True)
    status_box = st.empty()
    progress_bar = st.empty()

    # END CARD 1
    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# LOGIK LOOP
# ==========================================
results_list = []
processing_done = False

if start_btn and uploaded_files:
    progress_bar.progress(0)
    for index, file in enumerate(uploaded_files):
        status_box.markdown(f"<span style='color:#00d2ff'>⏳ Analysiere: {file.name}...</span>", unsafe_allow_html=True)
        
        try:
            data = analyze_image(file)
            if data:
                data["Datei-Name"] = file.name
                results_list.append(data)
            else:
                st.toast(f"Fehler bei {file.name}", icon="⚠️")
        except Exception as e:
            st.error(f"Error: {e}")
            
        progress_bar.progress((index + 1) / len(uploaded_files))
        time.sleep(0.1) # UI Feel

    status_box.success("Fertig!")
    progress_bar.empty()
    processing_done = True


# ==========================================
# RECHTS: OUTPUT (STEP 2)
# ==========================================
with col_right:
    # START CARD 2
    st.markdown("""
        <div class='step-card'>
            <div class='card-header'>
                <span class='step-number'>2</span> Ergebnis & Export
            </div>
    """, unsafe_allow_html=True)

    if processing_done and results_list:
        # DataFrame Logic
        df = pd.DataFrame(results_list)
        cols = ["Datei-Name", "datum", "lieferant", "beschreibung", "betrag_gesamt", "kategorie", "rechnungsnummer"]
        final_cols = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
        df = df[final_cols]
        
        # Cleanup Types
        if "betrag_gesamt" in df.columns:
             df["betrag_gesamt"] = pd.to_numeric(df["betrag_gesamt"], errors='coerce').fillna(0.0)
        if "datum" in df.columns:
            df["datum"] = pd.to_datetime(df["datum"], errors='coerce').dt.date

        # Metrik
        total_val = df["betrag_gesamt"].sum() if "betrag_gesamt" in df.columns else 0.0
        
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            st.markdown(f"<div style='font-size: 0.9rem; color: #8892b0;'>Dokumente</div><div style='font-size: 1.5rem; font-weight:bold; color: white;'>{len(results_list)}</div>", unsafe_allow_html=True)
        with m_col2:
            st.markdown(f"<div style='font-size: 0.9rem; color: #8892b0;'>Gesamtsumme</div><div style='font-size: 1.5rem; font-weight:bold; color: #64ffda;'>{total_val:.2f} €</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("✏️ Klicke in die Tabelle zum Korrigieren:")

        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            height=400,
            column_config={
                "betrag_gesamt": st.column_config.NumberColumn("Betrag (€)", format="%.2f €"),
                "datum": st.column_config.DateColumn("Belegdatum", format="YYYY-MM-DD"),
                "beschreibung": st.column_config.TextColumn("Inhalt", width="medium"),
                "kategorie": st.column_config.SelectboxColumn(
                    "Kategorie",
                    options=["Bewirtung", "Reise", "Büro", "Software", "Hardware", "Marketing", "Sonstiges"],
                    required=True
                )
            },
            key="editor_main_v4"
        )
        
        st.markdown("---")
        
        # Export Button (Rechtsbündig)
        col_space, col_dl = st.columns([2, 1])
        with col_dl:
            csv = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 CSV Herunterladen",
                data=csv,
                file_name="export.csv",
                mime="text/csv",
                type="primary", # Nutzt unseren Custom Style
                use_container_width=True
            )

    else:
        # EMPTY STATE VISUAL
        st.markdown("""
            <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px; color: #495670;'>
                <div style='font-size: 4rem; margin-bottom: 20px; opacity: 0.3;'>📊</div>
                <p>Noch keine Daten vorhanden.</p>
                <small>Starte Schritt 1 um Ergebnisse zu sehen.</small>
            </div>
        """, unsafe_allow_html=True)

    # END CARD 2
    st.markdown("</div>", unsafe_allow_html=True)