import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Laden
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("FEHLER: Kein API Key in .env gefunden!")
else:
    # 2. Config
    genai.configure(api_key=api_key)

    print("--- Verfügbare Modelle für deinen Key ---")
    try:
        # Wir listen alle Modelle auf und filtern nur die, die Text generieren können
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Name: {m.name}")
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")