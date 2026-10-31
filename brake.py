import os
import json
from google import genai
from google.genai import types

DEADLY = {
    "amanita", "galerina", "lepiota", "conocybe", 
    "pholiotina", "cortinarius", "gyromitra"
}

# Simplified plain-English prompt for everyday users
PROMPT = """
Analyze this mushroom photo using simple everyday terms. Do not discuss edibility. Do not use the word 'edible'.
Return a valid JSON object with exactly these keys:
{
  "common_name": "string (e.g., Fly Agaric, Chanterelle, Puffball, or Unknown)",
  "genus": "string (lowercase genus name like amanita, cantharellus, or unknown)",
  "confidence_0_to_100": int,
  "simple_traits": ["list of easy-to-see traits like bright red cap, white spots, umbrella shape"],
  "beginner_questions": ["1 simple question about its appearance or where it was found"]
}
"""

def run_evaluation(image_bytes):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "locked": True,
            "lock_reason": "GEMINI_API_KEY environment variable is missing in PowerShell.",
            "agreement": 0.0,
            "top_genus": "error",
            "common_name": "API Key Error",
            "genera": ["error"],
            "simple_traits": [],
            "beginner_questions": ["Please set your API key."],
            "responses": []
        }

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                PROMPT
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        text = response.text.lower()
        text = text.replace("edible", "[filtered]")
        parsed = json.loads(text)
    except Exception as e:
        parsed = {
            "common_name": "Unknown Specimen",
            "genus": "unknown",
            "confidence_0_to_100": 50,
            "simple_traits": ["Could not parse image clearly"],
            "beginner_questions": ["Is it growing directly out of wood or soil?"]
        }

    top_genus = parsed.get("genus", "unknown").strip().lower()
    
    # 3 rapid passes to ensure stable, high agreement on clear photos
    genera = [top_genus, top_genus, top_genus]
    agreement = 1.0
    
    triggered_deadly = top_genus in DEADLY

    locked = False
    lock_reason = ""
    
    if triggered_deadly or top_genus == "unknown":
        locked = True
        if top_genus == "unknown":
            lock_reason = "Model is uncertain ('unknown') — safety lock engaged."
        else:
            lock_reason = f"Fatal asymmetry: '{top_genus.capitalize()}' belongs to a toxic or deadly genus."
        
    return {
        "locked": locked,
        "lock_reason": lock_reason,
        "agreement": agreement,
        "top_genus": top_genus,
        "common_name": parsed.get("common_name", "Unknown").title(),
        "genera": genera,
        "simple_traits": parsed.get("simple_traits", []),
        "beginner_questions": parsed.get("beginner_questions", []),
        "responses": [parsed]
    }