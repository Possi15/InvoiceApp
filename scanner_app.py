import streamlit as st
import pandas as pd
import time
from ai_engine import analyze_image

# ==========================================
# 1. SETUP & MINIMALISTISCHES DESIGN
# ==========================================

st.set_page_config(layout="wide", page_title="Universal Scanner", initial_sidebar_state="collapsed")

def inject_clean_css():
    st.markdown("""
        <style>
        /* --- GRUNDLAGEN (Flat Dark Theme) --- */
        :root {
            --bg-color: #0d1117; /* Sehr dunkles Grau (GitHub Style) */
            --card-bg: #161b22;  /* Etwas helleres Grau für Karten */
            --border-color: #30363d; /* Subtile Rahmen */
            --accent-color: #2f81f7; /* Professionelles Blau */
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
        }

        .stApp {
            background-color: var(--bg-color);
            color: var(--text-primary);
        }

        /* --- KARTEN DESIGN --- */
        .simple-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 24px;
            margin-bottom: 24px;
        }
        
        /* --- TYPOGRAPHIE --- */
        h1, h2, h3 { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; letter-spacing: -0.5px; }
        h1 { font-size: 2.2rem; font-weight: 600; }
        .step-label { 
            text-transform: uppercase; 
            font-size: 0.75rem; 
            font-weight: bold; 
            color: var(--text-secondary); 
            letter-spacing: 1px;
            margin-bottom: 8px;
            display: block;
        }

        /* --- UPLOADER CLEANUP --- */
        [data-testid='stFileUploader'] section {
            background-color: var(--bg-color);
            border: 1px dashed var(--border-color);
            border-radius: 6px;
        }
        [data-testid='stFileUploader'] small { display: none; } /* Versteckt "Limit 200MB..." */

        /* --- BUTTONS --- */
        div.stButton > button[kind="primary"] {
            background-color: var(--accent-color);
            border: none;
            color: white;
            font-weight: 500;
            border-radius: 6px;
            transition: opacity 0.2s;
        }
        div.stButton > button[kind="primary"]:hover {
            opacity: 0.9;
        }

        /* --- TABELLEN --- */
        div[data-testid="stDataEditor"] {
            border: 1px solid var(--border-color);
            border-radius: 6px;
            overflow: hidden;
        }
        
        /* Kategorie Header */
        .cat-header {
            font-size: 1rem;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-primary);
        }
        </style>
    """, unsafe_allow_html=True)

inject_clean_css()

# ==========================================
# 2. LOGIK-FUNKTIONEN (Bugfix & Typen)
# ==========================================

def clean_float(val):
    """Konvertiert alles sicher in Float (0.00 bei Fehler)"""
    if val is None or val == "" or val == "-": 
        return 0.0
    try:
        if isinstance(val, (float, int)): 
            return float(val)
        # String Reinigung
        s = str(val).replace("€", "").replace("EUR", "").strip()
        s = s.replace(".", "").replace(",", ".") 
        return float(s)
    except:
        return 0.0

def auto_categorize(row):
    """
    BUGFIX: Wir greifen nicht mehr mit .values() zu (das war der Fehler),
    sondern wandeln die Reihe explizit in Strings um.
    """
    try:
        # Wir wandeln die ganze Zeile in einen langen String um für die Suche
        full_text = " ".join(row.astype(str).tolist()).lower()
        status = str(row.get("Zahlungsstatus", "")).lower()
        
        if "angebot" in full_text or "kostenvoranschlag" in full_text: 
            return "Angebot"
        if "bezahlt" in status or "beglichen" in status or "erledigt" in status: 
            return "Erledigt"
        return "Offene Zahlung"
    except:
        return "Offene Zahlung"

# ==========================================
# 3. LAYOUT & HEADER
# ==========================================

# Minimalistischer Header
st.markdown("<h1>Universal Scanner</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8b949e; margin-top:-15px;'>KI-gestützte Belegerfassung</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

col_input, col_output = st.columns([1, 2], gap="large")

# ==========================================
# 4. LINKER BEREICH (INPUT)
# ==========================================
with col_input:
    st.markdown("<div class='simple-card'>", unsafe_allow_html=True)
    st.markdown("<span class='step-label'>1. DATEIEN HOCHLADEN</span>", unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        "Upload", 
        accept_multiple_files=True, 
        label_visibility="collapsed"
    )

    start_btn = False
    if uploaded_files:
        st.markdown("<br>", unsafe_allow_html=True)
        # Schlichter Button
        start_btn = st.button(f"Analyse starten ({len(uploaded_files)})", type="primary", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 5. VERARBEITUNGSLOGIK
# ==========================================
results_list = []
processing_done = False

if start_btn and uploaded_files:
    # Schlichte Progress Bar statt wilder Animation
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, file in enumerate(uploaded_files):
        status_text.caption(f"Verarbeite: {file.name}...")
        
        try:
            # --- AI ENGINE ---
            raw = analyze_image(file)
            if raw is None: raw = {}

            # --- MAPPING & CLEANING ---
            entry = {
                "Datei": file.name,
                # Textfelder: Dürfen "-" sein
                "Lieferant": raw.get("lieferant", raw.get("firma", "-")) or "-",
                "IBAN_Ziel": raw.get("iban", raw.get("zahlungsziel", "-")) or "-",
                "Zahlungsstatus": raw.get("zahlungsstatus", raw.get("status", "-")) or "-",
                "USt_Satz": raw.get("ust_satz", "-") or "-",
                
                # Zahlenfelder: Müssen 0.0 sein (KEIN "-")
                "Netto": clean_float(raw.get("netto", raw.get("nettobetrag"))),
                "Steuer": clean_float(raw.get("steuer", raw.get("umsatzsteuerbetrag"))),
                "Brutto": clean_float(raw.get("brutto", raw.get("bruttobetrag", raw.get("betrag_gesamt")))),
                
                # Datum: Muss Datum oder None sein (KEIN "-")
                "Datum": raw.get("datum", raw.get("rechnungsdatum")),
                
                "_error": False
            }
            results_list.append(entry)

        except Exception as e:
            # Fehlerfall (sicher abfangen)
            results_list.append({
                "Datei": file.name, "Lieferant": "⚠️ Fehler", 
                "Netto": 0.0, "Steuer": 0.0, "Brutto": 0.0,
                "Datum": None, "Zahlungsstatus": "Systemfehler", "_error": True
            })
            print(f"Error processing {file.name}: {e}") # Log für Konsole

        # Update Progress
        progress_bar.progress((i + 1) / len(uploaded_files))

    progress_bar.empty()
    status_text.empty()
    processing_done = True

# ==========================================
# 6. RECHTER BEREICH (OUTPUT)
# ==========================================
with col_output:
    st.markdown("<div class='simple-card'>", unsafe_allow_html=True)
    st.markdown("<span class='step-label'>2. ERGEBNIS & EXPORT</span>", unsafe_allow_html=True)

    if processing_done and results_list:
        df = pd.DataFrame(results_list)

        # --- PANDAS TYPEN FIXEN (Verhindert Editor-Absturz) ---
        if "Datum" in df.columns:
            df["Datum"] = pd.to_datetime(df["Datum"], errors='coerce')
        
        for col in ["Netto", "Steuer", "Brutto"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        # --- KATEGORISIERUNG (BUGFIXED VERSION) ---
        df["Kategorie"] = df.apply(auto_categorize, axis=1)
        df.loc[df["_error"]==True, "Kategorie"] = "Offene Zahlung"

        # --- TABELLEN KONFIGURATION ---
        col_config = {
            "Lieferant": st.column_config.TextColumn("Lieferant", width="medium"),
            "Datum": st.column_config.DateColumn("Datum", format="DD.MM.YYYY"),
            "USt_Satz": st.column_config.SelectboxColumn("USt", options=["0%", "10%", "20%", "-"], width="small"),
            "Netto": st.column_config.NumberColumn("Netto", format="%.2f €"),
            "Steuer": st.column_config.NumberColumn("Steuer", format="%.2f €"),
            "Brutto": st.column_config.NumberColumn("Brutto", format="%.2f €"),
            "IBAN_Ziel": st.column_config.TextColumn("Info", width="small"),
            "Zahlungsstatus": st.column_config.SelectboxColumn("Status", options=["Offen", "Bezahlt", "Storniert", "-"], width="small"),
            "Datei": st.column_config.TextColumn("Quelle", disabled=True),
            "Kategorie": st.column_config.Column(hidden=True),
            "_error": st.column_config.Column(hidden=True)
        }

        # --- GRUPPIERTE ANZEIGE ---
        groups = ["Offene Zahlung", "Angebot", "Erledigt"]
        has_data = False

        for group in groups:
            sub_df = df[df["Kategorie"] == group].copy()
            if not sub_df.empty:
                has_data = True
                
                # Schlichter Header
                st.markdown(f"<div class='cat-header'>{group}</div>", unsafe_allow_html=True)
                
                st.data_editor(
                    sub_df,
                    column_config=col_config,
                    use_container_width=True,
                    num_rows="dynamic",
                    hide_index=True,
                    key=f"editor_{group}"
                )

        if not has_data:
            st.info("Keine Daten gefunden.")

        # --- EXPORT ---
        st.markdown("---")
        total = df["Brutto"].sum()
        c1, c2 = st.columns([1, 1])
        c1.markdown(f"**Gesamtsumme:** {total:.2f} €")
        c2.download_button("CSV Exportieren", df.to_csv(index=False).encode("utf-8"), "export.csv", "text/csv", type="primary", use_container_width=True)

    elif processing_done:
        st.error("Konnte keine Daten aus den Bildern lesen.")
    else:
        st.markdown("<p style='color:#8b949e; font-style:italic;'>Bitte Dateien hochladen und Analyse starten.</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)