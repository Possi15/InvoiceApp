import streamlit as st
import pandas as pd
import time
from ai_engine import analyze_image

# ==========================================
# 1. KONFIGURATION & CSS
# ==========================================

st.set_page_config(layout="wide", page_title="Universal Scanner", initial_sidebar_state="collapsed")

def inject_custom_css():
    st.markdown("""
        <style>
        :root {
            --bg-dark: #020c1b;
            --text-highlight: #e6f1ff;
            --cyan: #64ffda;
            --blue-neon: #00d2ff;
            --orange: #ffb86c;
            --green: #50fa7b;
        }
        .stApp { background-color: var(--bg-dark); color: var(--text-highlight); }
        
        /* Uploader Styling */
        [data-testid='stFileUploader'] section {
            background-color: #172a45 !important;
            border: 2px dashed var(--blue-neon) !important;
            border-radius: 10px;
        }
        [data-testid='stFileUploader'] button { color: var(--cyan) !important; border-color: var(--cyan) !important; }
        [data-testid='stFileUploader'] small, [data-testid='stFileUploader'] span { color: #8892b0 !important; }

        /* Container & Header */
        .main-card {
            background-color: #0f1c30; border: 1px solid #233554;
            border-radius: 15px; margin-bottom: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.5); overflow: visible;
        }
        .card-content { padding: 20px; overflow-x: auto; }
        
        .step-header {
            display: flex; align-items: center; background: linear-gradient(90deg, #112240 0%, #172a45 100%);
            padding: 15px 20px; border-radius: 10px 10px 0 0; border-bottom: 1px solid #233554;
        }
        .step-number {
            background: var(--blue-neon); color: #020c1b; width: 30px; height: 30px;
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-weight: 800; margin-right: 15px;
        }
        .step-title { font-weight: 700; color: white; }

        /* Kategorien */
        .cat-header {
            font-size: 1.2rem; font-weight: bold; margin-top: 20px; margin-bottom: 10px;
            padding-bottom: 5px; border-bottom: 1px solid #233554;
        }
        .cat-open { color: var(--orange); }
        .cat-done { color: var(--green); }
        .cat-offer { color: var(--cyan); }

        /* Buttons & Editor */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(45deg, #00d2ff, #007bff); border: none; color: white; font-weight: bold;
        }
        div[data-testid="stDataEditor"] { overflow-x: auto; }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==========================================
# 2. HELPER: SICHERE DATENTYPEN
# ==========================================

def clean_float(val):
    """
    Wandelt Input sicher in Float um.
    WICHTIG: Gibt 0.0 zurück statt "-", damit der NumberColumn Editor nicht abstürzt.
    """
    if val is None: return 0.0
    try:
        if isinstance(val, (float, int)): return float(val)
        # String bereinigen (1.000,00 € -> 1000.00)
        s = str(val).replace("€", "").replace("EUR", "").strip()
        s = s.replace(".", "").replace(",", ".") # Deutsche Formatierung grob fixen
        return float(s)
    except:
        return 0.0

def auto_categorize(row):
    text = " ".join([str(v).lower() for v in row.values()])
    status = str(row.get("Zahlungsstatus", "")).lower()
    
    if "angebot" in text or "kostenvoranschlag" in text: return "Angebot"
    if "bezahlt" in status or "beglichen" in status or "erledigt" in status: return "Erledigt"
    return "Offene Zahlung"

# ==========================================
# 3. HEADER (OHNE LOGIN)
# ==========================================

st.markdown("""
    <div style='text-align: center; padding: 20px 0 40px 0;'>
        <h1 style='font-size: 3.5rem; margin: 0;'>Universal <span style='color:#64ffda;'>Scanner</span></h1>
        <p style='color: #8892b0;'>Login deaktiviert – Testmodus</p>
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.8], gap="large")

# ==========================================
# 4. UPLOAD (LINKS)
# ==========================================
with col_left:
    st.markdown("""
        <div class='main-card'>
            <div class='step-header'><div class='step-number'>1</div><div class='step-title'>Upload</div></div>
            <div class='card-content'>
    """, unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader("Dateien", accept_multiple_files=True, label_visibility="collapsed")
    
    start_btn = False
    if uploaded_files:
        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button(f"⚡ SCAN STARTEN ({len(uploaded_files)})", type="primary")
    
    st.markdown("</div></div>", unsafe_allow_html=True)

# ==========================================
# 5. VERARBEITUNG
# ==========================================
results_list = []
processing_done = False

if start_btn and uploaded_files:
    progress_bar = st.progress(0)
    
    for i, file in enumerate(uploaded_files):
        try:
            # AI ENGINE AUFRUF
            raw = analyze_image(file)

            if raw is None: raw = {}
            
            # DATEN SICHERN (Hier verhindern wir den Absturz!)
            entry = {
                "Datei": file.name,
                
                # TEXTFELDER: Hier ist "-" erlaubt
                "Lieferant": raw.get("lieferant", raw.get("firma", "-")) or "-",
                "IBAN_Ziel": raw.get("iban", raw.get("zahlungsziel", "-")) or "-",
                "Zahlungsstatus": raw.get("zahlungsstatus", raw.get("status", "-")) or "-",
                "USt_Satz": raw.get("ust_satz", "-") or "-", 
                
                # ZAHLENFELDER: Hier MUSS es eine Zahl sein (0.00), KEIN "-"
                "Netto": clean_float(raw.get("netto", raw.get("nettobetrag"))),
                "Steuer": clean_float(raw.get("steuer", raw.get("umsatzsteuerbetrag"))),
                "Brutto": clean_float(raw.get("brutto", raw.get("bruttobetrag", raw.get("betrag_gesamt")))),
                
                # DATUMSFELD: Hier MUSS es ein Datum oder None sein, KEIN "-"
                "Datum": raw.get("datum", raw.get("rechnungsdatum")), 
                
                "_error": False
            }
            results_list.append(entry)
            
        except Exception as e:
            # Fallback bei Crash
            results_list.append({
                "Datei": file.name, "Lieferant": "❌ FEHLER", 
                "Netto": 0.0, "Steuer": 0.0, "Brutto": 0.0,
                "Datum": None, "Zahlungsstatus": "Fehler", "_error": True
            })
        
        progress_bar.progress((i + 1) / len(uploaded_files))
        time.sleep(0.1)

    progress_bar.empty()
    processing_done = True

# ==========================================
# 6. AUSGABE (RECHTS)
# ==========================================
with col_right:
    st.markdown("""
        <div class='main-card'>
            <div class='step-header'><div class='step-number'>2</div><div class='step-title'>Ergebnis</div></div>
            <div class='card-content'>
    """, unsafe_allow_html=True)

    if processing_done and results_list:
        df = pd.DataFrame(results_list)
        
        # --- TYP-ERZWINGUNG (Verhindert Absturz) ---
        
        # 1. Datum zu echtem Datetime (Fehlerhafte werden zu NaT/Leer)
        if "Datum" in df.columns:
            df["Datum"] = pd.to_datetime(df["Datum"], errors='coerce')

        # 2. Zahlen sicherstellen
        cols_num = ["Netto", "Steuer", "Brutto"]
        for c in cols_num:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0.0)

        # 3. Kategorisierung
        df["Kategorie"] = df.apply(auto_categorize, axis=1)
        df.loc[df["_error"]==True, "Kategorie"] = "Offene Zahlung"

        # SPALTEN KONFIGURATION
        col_config = {
            "Lieferant": st.column_config.TextColumn("Lieferant", width="medium"),
            "Datum": st.column_config.DateColumn("Datum", format="DD.MM.YYYY"),
            "USt_Satz": st.column_config.SelectboxColumn("USt", options=["0%", "10%", "20%", "-"], width="small"),
            "Netto": st.column_config.NumberColumn("Netto", format="%.2f €"),
            "Steuer": st.column_config.NumberColumn("Steuer", format="%.2f €"),
            "Brutto": st.column_config.NumberColumn("Brutto", format="%.2f €"),
            "IBAN_Ziel": st.column_config.TextColumn("IBAN / Info", width="medium"),
            "Zahlungsstatus": st.column_config.SelectboxColumn("Status", options=["Offen", "Bezahlt", "Storniert", "-"], width="small"),
            "Datei": st.column_config.TextColumn("Datei", disabled=True),
            "Kategorie": st.column_config.Column(hidden=True),
            "_error": st.column_config.Column(hidden=True)
        }

        # GRUPPIERTE AUSGABE
        groups = ["Offene Zahlung", "Angebot", "Erledigt"]
        has_data = False

        for group in groups:
            sub_df = df[df["Kategorie"] == group].copy()
            if not sub_df.empty:
                has_data = True
                
                # Icon wählen
                icon = "📝"
                css = "cat-open"
                if group == "Angebot": icon, css = "📑", "cat-offer"
                if group == "Erledigt": icon, css = "✅", "cat-done"
                
                st.markdown(f"<div class='cat-header {css}'>{icon} {group}</div>", unsafe_allow_html=True)
                
                st.data_editor(
                    sub_df,
                    column_config=col_config,
                    use_container_width=True,
                    num_rows="dynamic",
                    hide_index=True,
                    key=f"editor_group_{group}" 
                )

        if not has_data:
            st.warning("Keine Daten.")
        
        # EXPORT
        st.markdown("---")
        total = df["Brutto"].sum()
        c1, c2 = st.columns([1,1])
        c1.markdown(f"**Gesamt:** :green[{total:.2f} €]")
        c2.download_button("💾 CSV Export", df.to_csv(index=False).encode("utf-8"), "export.csv", "text/csv", type="primary")

    elif processing_done:
        st.error("Fehler: Keine Daten extrahiert.")
    else:
        st.info("Warte auf Upload...")

    st.markdown("</div></div>", unsafe_allow_html=True)