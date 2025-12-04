import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# 1. Umgebungsvariablen laden
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY ist nicht gesetzt.")

# 2. Konfiguration
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def analyze_image(image_path):
    try:
        # Laden
        mime_type = image_path.type
        content_part = None

        if "pdf" in mime_type:
            content_part = {
                "mime_type": "application/pdf",
                "data": image_path.getvalue()
            }
        else:
            content_part = Image.open(image_path)

        # 2. Der Prompt (Der fehlte vorher!)
        prompt = """
        Du bist ein Buchhaltungs-Experte. 
        Analysiere dieses Dokument. Extrahiere als JSON:
        - datum (Format YYYY-MM-DD)
        - rechnungsnummer
        - betrag (als Zahl, Punkt als Dezimaltrenner)
        - lieferant (Firmenname)
        - kategorie (Vorschlag: Supermarkt, Versicherung, Tech, Sonstiges)
        - beschreibung (WICHTIG: Eine extrem kurze Zusammenfassung des Inhalts in max 6 Wörtern. Bsp: "2x Monitor & Maus" oder "Zugfahrt Berlin-München")
        """

        response = model.generate_content([prompt, content_part])

        # Putzen & Parsen
        return clean_and_parse_json(response.text)
    
    except Exception as e:
        print(f"AI Engine Error: {e}")
        return None

def clean_and_parse_json(text):
    ## Verwandelt den AI Text in ein Dictionary

    # 1.Markdown wird entfernt (```json ... ```)
    clean_text = text.strip()
    if clean_text.startswith("```"):
        lines = clean_text.splitlines() ## Die erste und letzte Zeile wird entfernt
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].startswith("```"):
            lines = lines[:-1]
        clean_text = "\n".join(lines)

    ## 2.String in Dictionary umwandeln
    try:
        data = json.loads(clean_text)
        return data
    except json.JSONDecodeError:
        print("FEHLER: Die Ai hat kein valides JSON geliefert!")
        print(f"Rohdaten {text}")
        return None



# ==========================================
# DER ZÜNDSCHLÜSSEL (Execution Block)
# ==========================================
if __name__ == "__main__":
    # Hier wird die Funktion erst wirklich gestartet!
    # Stelle sicher, dass dein Bild wirklich 'rechnung.jpg' heißt.
    analyze_image("rechnung.jpg")