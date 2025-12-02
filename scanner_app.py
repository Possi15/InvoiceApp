import pandas as pd
import streamlit as st
from PIL import Image   
from ai_engine import analyze_image

## Seite Konfigurieren
st.set_page_config(page_title="AI-Scanner", page_icon="🧾", layout="wide")
st.title("Moderne Buchhaltung")
st.markdown("Lade deine Bilder & PDF's hier hoch für eine Auswertung")

## Layout definieren ##
col_input, col_result = st.columns([1, 2])

with col_input:
    st.subheader("Upload")
    
    uploaded_files = st.file_uploader("Lade alle deine Belege hoch", type=["jpg", "png", "jpg", "pdf"], accept_multiple_files=True)

    ##Start Button ##
    start_btn = False

    if uploaded_files:
        st.info(f"{len(uploaded_files)} Dateien warten auf Analyse!")
        start_btn = st.button("🚀 Batch-Analyse starten", type="primary")
    else:
        st.info("Bitte Dateien laden!")

    status_container = st.empty()
    progress_bar = st.empty()

####################    
## Logik aufbauen ##
####################
if start_btn and uploaded_files:
    
    results_list = []

    ## Fortschrittsanzeige ##
    progress_bar.progress(0)
          
    ## Die Schleife ##
    for index, file in enumerate(uploaded_files):
        status_container.info(f"⏳ Analysiere **{file.name}**")

        data = analyze_image(file)

        if data:
            data["Datei-Name"] = file.name
            results_list.append(data)
        else:
            st.toast(f"Fehler beim {file.name}", icon="⚠️")
        
        ## Update vom Balken ##
        progress_bar.progress((index+1) / len(uploaded_files))
    
    ## Aufräumen der Platzhalter ##
    status_container.success("✅ Fertig!")
    progress_bar.empty()

    ################
    ## Ergebnisse ##
    ################

    with col_result:
        st.subheader("Ergbnisse")

        if results_list:
            df = pd.DataFrame(results_list)

            ## Spalten Logik ##
            cols = ["Datei-Name", "datum", "lieferant", "betrag_gesamt", "rechnungsnummer"]
            final_cols = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
            df = df[final_cols]

            ## Tabelle & Metriken
            st.dataframe(df, use_container_width=True)

            if "betrag_gesamt" in df.columns:
                total = pd.to_numeric(df["betrag_gesamt"], errors='coerce').sum()
                st.metric("Gesamtvolumen", f"{total:.2f} €")

            ## Export ##
            st.divider()
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("CSV-Export", csv, "export.csv", "text/csv")

        else:
            st.warning("Keine Daten extrahiert")

elif not uploaded_files:
    ## Leerer Zustand auf der rechten Seite ##
    with col_result:
        st.info("Warten auf Input..")            