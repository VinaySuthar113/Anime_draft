from google import genai
import json
import os

client = genai.Client(api_key=os.environ.get("AIzaSyDf8VMXDpbdPnCfGnO3a00i53oC-vV7TNI"))

def judge_teams(teamA, teamB, scoreA, scoreB):
    prompt = f"""
You are an expert anime battle analyst.

Rules:
- Apply only small adjustments (-10 to +10)
- Base scores are already calculated
- Judge balance, roles, and synergy
- Do NOT invent new powers

Team A:
{teamA}
Base Score: {scoreA}

Team B:
{teamB}
Base Score: {scoreB}

Return ONLY valid JSON:

{{
  "teamA_adjustment": number,
  "teamB_adjustment": number,
  "reasoning": ""
}}
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    raw = response.text.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1

    return json.loads(raw[start:end])
