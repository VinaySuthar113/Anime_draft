from google import genai
import json
import os

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("AIzaSyDf8VMXDpbdPnCfGnO3a00i53oC-vV7TNI"))

def normalize_character(c):
    c["base_power"] = max(60, min(95, c["base_power"]))
    for role in c["role_bonus"]:
        c["role_bonus"][role] = max(-15, min(25, c["role_bonus"][role]))
    return c

def generate_character():
    prompt = """
Create ONE original anime-style character.
Do NOT reference or copy real anime characters.

Return ONLY valid JSON in this exact format:

{
  "name": "",
  "archetype": "",
  "base_power": number,
  "role_bonus": {
    "captain": number,
    "vice_captain": number,
    "tank": number,
    "healer": number,
    "support": number
  },
  "traits": []
}
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    raw = response.text.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1

    character = json.loads(raw[start:end])
    return normalize_character(character)
