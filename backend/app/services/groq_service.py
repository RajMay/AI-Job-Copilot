import os
import json
import re
from typing import Any, Dict

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ✅ Removed dead GEMINI_API_KEY load — this service uses Groq only
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is not set. Please add it to your .env file."
    )

client = Groq(api_key=GROQ_API_KEY)

# ✅ Empty/fallback profile so callers always get a valid shape
EMPTY_PROFILE = {
    "roles": [],
    "skills": [],
    "experience_years": 0,
    "education": [],
    "preferred_locations": [],
    "seniority_level": ""
}


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract and parse the first valid JSON object from messy LLM output.

    Handles:
    - ```json code fences
    - Leading 'json' text
    - Explanations before/after JSON
    """

    if not text or not text.strip():
        return {"error": "Empty response from model"}

    cleaned = text.strip()

    # Remove markdown code fences
    cleaned = re.sub(r"```json", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"```", "", cleaned)

    # Remove leading 'json' word if present
    cleaned = re.sub(r"^json\s*", "", cleaned, flags=re.IGNORECASE)

    # Find JSON object boundaries
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1:
        return {
            "error": "No JSON object found in model response",
            "raw_output": text
        }

    json_str = cleaned[start:end + 1]

    try:
        return json.loads(json_str)

    except json.JSONDecodeError as e:
        return {
            "error": "JSON parsing failed",
            "details": str(e),
            "raw_output": text
        }


def extract_resume_profile(resume_text: str) -> dict:
    """
    Convert resume text into a structured profile dict using Groq (LLaMA).
    Always returns a valid profile shape — never raises on API errors.
    """

    if not resume_text or not resume_text.strip():
        print("⚠️ Empty resume text provided.")
        return EMPTY_PROFILE.copy()

    prompt = f"""You are an expert resume analyzer.

Extract the following fields from the resume text below.
If the candidate does not state a headline, infer 1–3 realistic job titles from their work history.
Always include at least one role OR at least three skills when the resume describes any work, education, or projects.

Return ONLY a valid JSON object. No explanation. No markdown. No extra text.

JSON format:
{{
  "roles": ["list of target job titles"],
  "skills": ["list of technical and soft skills"],
  "experience_years": <integer>,
  "education": ["list of degrees or certifications"],
  "preferred_locations": ["list of preferred work locations, or ['Worldwide'] if not specified"],
  "seniority_level": "<Junior | Mid | Senior | Lead>"
}}

Resume:
{resume_text}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    # ✅ System message forces stricter JSON-only output
                    "role": "system",
                    "content": "You are a JSON-only resume parser. You output nothing except valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=1024  # ✅ Prevents runaway responses
        )

        raw_text = response.choices[0].message.content
        parsed = extract_json_from_text(raw_text)

        # ✅ Check if parsing produced an error dict — fall back gracefully
        if "error" in parsed:
            print(f"⚠️ Profile extraction error: {parsed['error']}")
            print(f"   Raw output: {parsed.get('raw_output', '')[:200]}")
            return EMPTY_PROFILE.copy()

        # ✅ Merge with empty profile to ensure all keys exist
        # (guards against model omitting a field)
        profile = {**EMPTY_PROFILE, **parsed}
        return profile

    except Exception as e:
        # ✅ API failure (rate limit, network, etc.) doesn't crash the app
        print(f"❌ Groq API call failed: {e}")
        return EMPTY_PROFILE.copy()
    
    # ... all your existing groq_service.py code above ...

def generate_job_queries(profile: dict) -> list:
    queries = []
    locations = profile.get("preferred_locations") or ["Worldwide"]
    seniority = profile.get("seniority_level", "")

    for role in profile.get("roles", []):
        for location in locations:
            prefix = f"{seniority} " if seniority else ""
            queries.append(f"{prefix}{role} {location}".strip())

    if not queries:
        for skill in profile.get("skills", [])[:3]:
            queries.append(f"{skill} developer Worldwide")

    return queries[:5]