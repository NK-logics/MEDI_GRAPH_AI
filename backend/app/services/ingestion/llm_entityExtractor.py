import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key="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")


def extract_entities_llm(message: str):

    system_prompt = """
You are a medical entity extraction system.

Extract entities from the user message.

Return ONLY valid JSON.

JSON format:

{
 "symptoms": [],
 "triggers": [],
 "medications": []
}

Rules:
- Do not explain anything
- Do not add extra text
- Only return JSON

If no entity is present return empty lists.
"""

    user_prompt = f"""
User message:
{message}
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0
    )

    response = completion.choices[0].message.content

    try:
        entities = json.loads(response)
    except Exception:
        entities = {
            "symptoms": [],
            "triggers": [],
            "medications": []
        }

    return entities