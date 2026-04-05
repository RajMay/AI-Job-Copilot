"""
Fallback extraction when LLM output is empty or unusable.
Uses keyword / phrase matching on raw resume text.
"""

import re
from typing import List, Set, Tuple

# Longest phrases first so "machine learning engineer" beats "engineer"
_ROLE_PHRASES: Tuple[str, ...] = (
    "machine learning engineer",
    "ml engineer",
    "data scientist",
    "data analyst",
    "business analyst",
    "financial analyst",
    "research scientist",
    "software engineer",
    "full stack developer",
    "frontend developer",
    "front-end developer",
    "backend developer",
    "back-end developer",
    "devops engineer",
    "site reliability engineer",
    "cloud engineer",
    "security engineer",
    "product manager",
    "project manager",
    "program manager",
    "technical lead",
    "engineering manager",
    "solutions architect",
    "data engineer",
    "business intelligence",
    "bi developer",
    "qa engineer",
    "quality assurance",
    "ux designer",
    "ui designer",
    "graphic designer",
    "web developer",
    "mobile developer",
    "ios developer",
    "android developer",
    "salesforce developer",
    "java developer",
    "python developer",
    "net developer",
    "systems administrator",
    "network engineer",
    "database administrator",
    "hr manager",
    "human resources",
    "account executive",
    "marketing manager",
    "content writer",
)

_SKILL_PATTERN = re.compile(
    r"\b("
    r"Python|JavaScript|TypeScript|Java|C\+\+|C#|Ruby|Go|Rust|PHP|Swift|Kotlin|"
    r"SQL|NoSQL|PostgreSQL|MySQL|MongoDB|Redis|Oracle|Snowflake|BigQuery|"
    r"Excel|VBA|Tableau|Power\s*BI|Looker|Qlik|"
    r"AWS|Azure|GCP|Google\s*Cloud|Docker|Kubernetes|Terraform|Ansible|"
    r"React|Angular|Vue\.js|Node\.js|Django|Flask|FastAPI|Spring\s*Boot|\.NET|"
    r"PyTorch|TensorFlow|Keras|scikit-learn|scikit\s*learn|Pandas|NumPy|Spark|"
    r"Hadoop|Kafka|Airflow|dbt|ETL|Git|JIRA|Jenkins|Linux|Unix|Bash|Shell|"
    r"Machine\s*Learning|Deep\s*Learning|NLP|Computer\s*Vision|Statistics|"
    r"A/B\s*Testing|Agile|Scrum|REST|GraphQL|API|HTML|CSS|SASS|Tailwind|"
    r"Salesforce|SAP|Figma|Photoshop|Illustrator|RStudio"
    r")\b",
    re.IGNORECASE,
)


def _title_case_skill(match: str) -> str:
    m = match.strip()
    if re.match(r"^A/B\b", m, re.I):
        return "A/B Testing"
    low = m.lower()
    specials = {
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "graphql": "GraphQL",
        "html": "HTML",
        "css": "CSS",
        "sql": "SQL",
        "nosql": "NoSQL",
        "aws": "AWS",
        "gcp": "GCP",
        "git": "Git",
        "nlp": "NLP",
        "api": "API",
        "vba": "VBA",
        "dbt": "dbt",
        "etl": "ETL",
    }
    if low in specials:
        return specials[low]
    if " " in m or "-" in m:
        return " ".join(w.capitalize() if w.lower() not in ("and", "or", "of") else w for w in re.split(r"[\s-]+", m) if w)
    return m[:1].upper() + m[1:].lower() if m else m


def infer_roles_from_text(text: str, max_roles: int = 4) -> List[str]:
    if not text or not text.strip():
        return []
    low = text.lower()
    found: List[str] = []
    seen: Set[str] = set()
    for phrase in _ROLE_PHRASES:
        if phrase in low:
            key = phrase.title()
            if phrase == "business intelligence":
                key = "Business Intelligence"
            if key.lower() not in seen:
                seen.add(key.lower())
                found.append(key)
        if len(found) >= max_roles:
            break
    return found


def infer_skills_from_text(text: str, max_skills: int = 20) -> List[str]:
    if not text or not text.strip():
        return []
    seen: Set[str] = set()
    out: List[str] = []
    for m in _SKILL_PATTERN.finditer(text):
        label = _title_case_skill(m.group(1))
        lk = label.lower()
        if lk not in seen:
            seen.add(lk)
            out.append(label)
        if len(out) >= max_skills:
            break
    return out


def infer_headline_role(text: str) -> List[str]:
    """First substantial line often is a target title (many resume templates)."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:12]:
        if 3 <= len(ln) <= 70 and ln.count(" ") <= 8:
            if re.search(r"[.!?]", ln):
                continue
            if re.match(r"^[\d\s\-+().]+$", ln):
                continue
            if "@" in ln and "." in ln:
                continue
            if re.match(r"^(phone|email|linkedin|github|http)\b", ln, re.I):
                continue
            if sum(c.isdigit() for c in ln) > len(ln) // 2:
                continue
            return [ln]
    return []


def boost_profile_from_raw_text(resume_text: str, profile: dict) -> dict:
    """
    If roles/skills are missing, fill from heuristics. Never removes LLM data.
    """
    roles = list(profile.get("roles") or [])
    skills = list(profile.get("skills") or [])
    if roles and skills:
        return profile

    r_set = {r.lower() for r in roles}
    s_set = {s.lower() for s in skills}

    if not roles:
        for r in infer_roles_from_text(resume_text):
            if r.lower() not in r_set:
                roles.append(r)
                r_set.add(r.lower())
        if not roles:
            for r in infer_headline_role(resume_text):
                if r.lower() not in r_set:
                    roles.append(r)
                    r_set.add(r.lower())

    if not skills:
        for s in infer_skills_from_text(resume_text):
            if s.lower() not in s_set:
                skills.append(s)
                s_set.add(s.lower())

    out = {**profile, "roles": roles, "skills": skills}
    if not out.get("preferred_locations"):
        out["preferred_locations"] = ["Worldwide"]
    return out
