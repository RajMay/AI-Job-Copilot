from typing import Dict, List
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_job_queries(profile: Dict) -> List[str]:
    """
    Generate intelligent job search queries from resume profile.
    """

    prompt = f"""
    You are an expert job search assistant.

    Generate 5 HIGHLY RELEVANT job search queries
    for web scraping based on this candidate profile.

    Include:
    - Target role
    - Key skills
    - Seniority level
    - Location (if available)

    Keep queries concise and realistic.

    Return ONLY JSON:

    {{
      "queries": ["query1", "query2", ...]
    }}

    Candidate Profile:
    {profile}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    raw = response.choices[0].message.content

    from app.services.gemini_service import extract_json_from_text
    data = extract_json_from_text(raw)

    return data.get("queries", [])