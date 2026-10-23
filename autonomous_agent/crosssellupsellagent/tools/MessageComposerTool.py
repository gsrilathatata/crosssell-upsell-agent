import requests
import json
from vertexai.preview.generative_models import GenerativeModel

def compose_message(combined_response: str) -> str:
    model = GenerativeModel("gemini-2.5-flash")
    prompt = f"""
You are a email assistant. Given this recommended plan and its summary in JSON:

{combined_response}

write an email to the user for a promotional offer mentioning that based on recent conversation the user shown on some interest to check if there are any cross sell or up sell oppurtunities.

Only return the dictionary in JSON format and do not change the structure everytime and json shoud have email and inside email should have subject and body.
"""
    result = model.generate_content(prompt)
    raw_text = result.text.strip()
    if raw_text.startswith("```json"):
       raw_text = raw_text.replace("```json", "").replace("```", "").strip() 

    return raw_text
