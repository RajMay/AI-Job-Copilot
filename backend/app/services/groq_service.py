import os
import json
import re
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from groq import Groq

from app.services.resume_heuristics import boost_profile_from_raw_text

load_dotenv()

# ✅ Removed dead GEMINI_API_KEY load — this service uses Groq only
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is not set. Please add it to your .env file."
    )

client = Groq(api_key=GROQ_API_KEY)

# Stronger model parses JSON more reliably; override with GROQ_EXTRACT_MODEL if needed
GROQ_EXTRACT_MODEL = os.getenv("GROQ_EXTRACT_MODEL", "llama-3.3-70b-versatile")

# Cap prompt size so the model always has room to finish JSON
_MAX_RESUME_CHARS = int(os.getenv("GROQ_RESUME_MAX_CHARS", "14000"))

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


def _as_str_list(val: Any) -> List[str]:
    if val is None:
        return []
    if isinstance(val, str):
        return [s.strip() for s in re.split(r"[,;|]", val) if s.strip()]
    if isinstance(val, list):
        out: List[str] = []
        for x in val:
            if isinstance(x, str) and x.strip():
                out.append(x.strip())
            elif isinstance(x, dict):
                t = x.get("title") or x.get("name") or x.get("role")
                if t and str(t).strip():
                    out.append(str(t).strip())
        return out
    return []


def normalize_profile_dict(parsed: Dict[str, Any]) -> Dict[str, Any]:
    """Coerce LLM output into the shapes FastAPI and the UI expect."""
    base = {**EMPTY_PROFILE, **{k: v for k, v in parsed.items() if k != "error"}}
    base["roles"] = _as_str_list(base.get("roles"))
    base["skills"] = _as_str_list(base.get("skills"))
    base["education"] = _as_str_list(base.get("education"))
    locs = _as_str_list(base.get("preferred_locations"))
    base["preferred_locations"] = locs if locs else ["Worldwide"]
    sl = base.get("seniority_level")
    base["seniority_level"] = str(sl).strip() if sl not in (None, "") else ""
    ey = base.get("experience_years", 0)
    try:
        base["experience_years"] = max(0, int(float(ey)))
    except (TypeError, ValueError):
        base["experience_years"] = 0
    return base


def extract_resume_profile(resume_text: str) -> dict:
    """
    Convert resume text into a structured profile dict using Groq (LLaMA).
    Always returns a valid profile shape — never raises on API errors.
    """

    if not resume_text or not resume_text.strip():
        print("⚠️ Empty resume text provided.")
        return EMPTY_PROFILE.copy()

    full_text = resume_text.strip()
    text_for_prompt = full_text[:_MAX_RESUME_CHARS]
    if len(full_text) > _MAX_RESUME_CHARS:
        text_for_prompt += "\n\n[Resume truncated for processing; earlier sections weighted more.]"

    prompt = f"""You are an expert resume analyzer.

Extract the following fields from the resume text below.
If the candidate does not state a headline, infer 1–3 realistic job titles from their work history.
Always include at least one role OR at least three skills when the resume describes any work, education, or projects.
Use JSON arrays of strings for roles, skills, education, and preferred_locations only (never a single string).

Return ONLY a valid JSON object. No explanation. No markdown. No extra text.

JSON format:
{{
  "roles": ["target job titles"],
  "skills": ["technical and soft skills"],
  "experience_years": <integer>,
  "education": ["degrees or certifications"],
  "preferred_locations": ["locations or Worldwide"],
  "seniority_level": "Junior|Mid|Senior|Lead or empty string"
}}

Resume:
{text_for_prompt}"""

    def _call_llm(use_json_mode: bool):
        kwargs = dict(
            model=GROQ_EXTRACT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a JSON-only resume parser. Output a single valid JSON object and nothing else.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            max_tokens=2048,
        )
        if use_json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        return client.chat.completions.create(**kwargs)

    profile: Dict[str, Any] = EMPTY_PROFILE.copy()
    raw_text: Optional[str] = None

    try:
        try:
            response = _call_llm(use_json_mode=True)
        except Exception as e_json:
            print(f"⚠️ Groq json_mode failed ({e_json}), retrying without response_format")
            response = _call_llm(use_json_mode=False)

        raw_text = response.choices[0].message.content
        parsed = extract_json_from_text(raw_text or "")

        if "error" in parsed:
            print(f"⚠️ Profile extraction error: {parsed['error']}")
            print(f"   Raw output: {parsed.get('raw_output', '')[:300]}")
        else:
            profile = normalize_profile_dict(parsed)

    except Exception as e:
        print(f"❌ Groq API call failed: {e}")

    profile = boost_profile_from_raw_text(full_text, profile)
    return profile

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