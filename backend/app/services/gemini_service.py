import os

from dotenv import load_dotenv
from typing import Any, Dict
import re
import json
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

# Create client (NEW WAY)
API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY)


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract and parse the first valid JSON object from messy LLM output.

    Handles:
    - ```json code fences
    - Leading 'json' text
    - Explanations before/after JSON
    - Extra whitespace
    - Newlines
    """

    if not text:
        return {"error": "Empty response"}

    cleaned = text.strip()

    # 🔹 Remove markdown code fences
    cleaned = re.sub(r"```json", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"```", "", cleaned)

    # 🔹 Remove leading 'json' word
    cleaned = re.sub(r"^json\s*", "", cleaned, flags=re.IGNORECASE)

    # 🔹 Find JSON object boundaries
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        return {
            "error": "No JSON object found",
            "raw_output": text
        }

    json_str = cleaned[start:end + 1]

    # 🔹 Attempt to parse JSON
    try:
        parsed = json.loads(json_str)
        return parsed

    except json.JSONDecodeError as e:
        return {
            "error": "JSON parsing failed",
            "details": str(e),
            "raw_output": text
        }


def extract_resume_profile(resume_text: str) -> dict:
    """
    Convert resume text into structured profile JSON using Gemini.
    """

    prompt = f"""
    You are an expert resume analyzer.

    Extract the following from the resume:

    - Target roles
    - Skills
    - Years of experience
    - Education
    - Preferred locations
    - Seniority level (Junior, Mid, Senior)

    IMPORTANT:
    Return ONLY valid JSON.
    Do not include explanations or markdown.

    Format:

    {{
      "roles": [],
      "skills": [],
      "experience_years": 0,
      "education": [],
      "preferred_locations": [],
      "seniority_level": ""
    }}

    Resume Text:
    {resume_text}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )


    raw_text = response.choices[0].message.content

    cleaned_text = extract_json_from_text(raw_text)

    
    return cleaned_text
