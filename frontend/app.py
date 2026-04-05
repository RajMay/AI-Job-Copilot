import base64
import html
import os
import re

import streamlit as st
import requests

# Default: deployed FastAPI (Render). For local backend, set:
#   PowerShell:  $env:AI_JOB_COPILOT_API_URL="http://127.0.0.1:8000"
#   Streamlit Cloud: override in Secrets if you use a different API host
_DEPLOYED_API_DEFAULT = "https://ai-job-copilot-1.onrender.com"
API_URL = os.environ.get("AI_JOB_COPILOT_API_URL", _DEPLOYED_API_DEFAULT).rstrip("/")

# If GET /api/indian-states fails (offline API), multiselect still works
_INDIAN_STATES_FALLBACK = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat",
    "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
    "Uttarakhand", "West Bengal", "Delhi", "Chandigarh", "Jammu and Kashmir", "Ladakh",
    "Puducherry", "Andaman and Nicobar Islands",
]

REFINE_WIDGET_KEYS = ("refine_roles", "refine_skills", "refine_locations", "refine_seniority")


@st.cache_data(ttl=3600)
def _cached_indian_states():
    try:
        r = requests.get(f"{API_URL}/api/indian-states", timeout=15)
        r.raise_for_status()
        data = r.json().get("states")
        if isinstance(data, list) and data:
            return tuple(data)
    except Exception:
        pass
    return None


def indian_state_options():
    t = _cached_indian_states()
    return list(t) if t else list(_INDIAN_STATES_FALLBACK)


def sanitize_job_text(value, max_len: int = 500) -> str:
    """Strip HTML / encoded markup from scraper noise, then escape for safe text nodes."""
    if value is None:
        return ""
    text = str(value)
    # Decode entities (&lt;div&gt; → <div>) and strip tags until stable (handles nested encoding).
    for _ in range(24):
        unescaped = html.unescape(text)
        stripped = re.sub(r"<[^>]+>", " ", unescaped, flags=re.IGNORECASE)
        if unescaped == text and stripped == text:
            text = stripped
            break
        text = stripped
    text = re.sub(r"\s+", " ", text).strip()
    if max_len and len(text) > max_len:
        text = text[: max_len - 1] + "…"
    return html.escape(text)


def sanitize_job_href(url) -> str:
    if not url or url == "N/A":
        return ""
    u = str(url).strip()
    if not (u.startswith("http://") or u.startswith("https://")):
        return ""
    return html.escape(u, quote=True)


def clear_refine_widget_keys():
    for k in REFINE_WIDGET_KEYS:
        st.session_state.pop(k, None)


def api_error_message(response: requests.Response) -> str:
    try:
        body = response.json()
        detail = body.get("detail")
        if isinstance(detail, list):
            return "; ".join(
                str(x.get("msg", x)) if isinstance(x, dict) else str(x) for x in detail
            )
        if detail is not None:
            return str(detail)
    except Exception:
        pass
    return response.text or "Unknown error"


def seed_refine_keys_from_profile():
    """Ensure widget keys exist (run before text_input/selectbox; not inside lazy expanders)."""
    if "profile" not in st.session_state:
        return
    profile = st.session_state["profile"]
    if "refine_roles" not in st.session_state:
        st.session_state["refine_roles"] = ", ".join(profile.get("roles", []))
    if "refine_skills" not in st.session_state:
        st.session_state["refine_skills"] = ", ".join(profile.get("skills", [])[:12])
    if "refine_locations" not in st.session_state:
        locs = profile.get("preferred_locations", [])
        st.session_state["refine_locations"] = ", ".join(locs) if locs else "Worldwide"
    seniority_options = ["", "Junior", "Mid", "Senior", "Lead"]
    if "refine_seniority" not in st.session_state:
        s = (profile.get("seniority_level") or "").strip()
        st.session_state["refine_seniority"] = s if s in seniority_options else ""


def sync_profile_from_refine_widgets():
    """Copy refine widget values into profile every run so Find Jobs uses current text."""
    if "profile" not in st.session_state:
        return
    if "refine_roles" in st.session_state:
        r = st.session_state["refine_roles"] or ""
        st.session_state["profile"]["roles"] = [x.strip() for x in r.split(",") if x.strip()]
    if "refine_skills" in st.session_state:
        s = st.session_state["refine_skills"] or ""
        st.session_state["profile"]["skills"] = [x.strip() for x in s.split(",") if x.strip()]
    if "refine_locations" in st.session_state:
        l = st.session_state["refine_locations"] or ""
        parts = [x.strip() for x in l.split(",") if x.strip()]
        if parts:
            st.session_state["profile"]["preferred_locations"] = parts
    if "refine_seniority" in st.session_state:
        st.session_state["profile"]["seniority_level"] = st.session_state.get("refine_seniority") or ""

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AI Job Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e0d5 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
    background: 
        radial-gradient(ellipse 80% 50% at 20% 10%, rgba(180,140,100,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(140,100,180,0.05) 0%, transparent 60%),
        #0a0a0f !important;
}

[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12121a 0%, #0e0e14 100%) !important;
    border-right: 1px solid rgba(184, 148, 90, 0.22) !important;
    min-width: 280px !important;
}
[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span { color: #d4c8b8 !important; }
[data-testid="stSidebar"] .block-container { padding: 1.25rem 1rem 2rem !important; }

.block-container { max-width: 1100px !important; padding: 3rem 2rem !important; }

.stDownloadButton > button {
    background: rgba(255,255,255,0.06) !important;
    color: #e8e0d5 !important;
    border: 1px solid rgba(184, 148, 90, 0.35) !important;
    border-radius: 8px !important;
}
.stDownloadButton > button:hover {
    border-color: rgba(184, 148, 90, 0.6) !important;
    background: rgba(184, 148, 90, 0.12) !important;
}

/* ── Typography ── */
h1, h2, h3 { font-family: 'Cormorant Garamond', serif !important; }

/* ── Hero ── */
.hero {
    text-align: center;
    padding: 4rem 0 3rem;
    position: relative;
}
.hero-eyebrow {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #b8945a;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(3rem, 8vw, 5.5rem);
    font-weight: 300;
    line-height: 1.05;
    color: #f0e8dc;
    letter-spacing: -0.02em;
}
.hero-title em {
    font-style: italic;
    color: #c9a06a;
}
.hero-subtitle {
    font-size: 0.95rem;
    color: #8a8070;
    margin-top: 1.2rem;
    font-weight: 300;
    letter-spacing: 0.05em;
}

/* ── Divider ── */
.divider {
    width: 60px;
    height: 1px;
    background: linear-gradient(90deg, transparent, #b8945a, transparent);
    margin: 2rem auto;
}

/* ── Upload Zone ── */
.upload-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #b8945a;
    margin-bottom: 0.5rem;
    display: block;
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(184,148,90,0.2) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: border-color 0.3s ease !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(184,148,90,0.5) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #b8945a 0%, #c9a06a 100%) !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.7rem 2rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(184,148,90,0.3) !important;
}

/* ── Profile Card ── */
.profile-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(184,148,90,0.15);
    border-radius: 16px;
    padding: 2rem;
    margin: 1.5rem 0;
    position: relative;
    overflow: hidden;
}
.profile-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #b8945a, transparent);
}
.profile-section-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #b8945a;
    margin-bottom: 0.6rem;
    margin-top: 1.2rem;
}
.profile-section-title:first-child { margin-top: 0; }
.profile-value {
    font-size: 0.95rem;
    color: #d4c8b8;
    font-weight: 300;
    line-height: 1.6;
}
.tag {
    display: inline-block;
    background: rgba(184,148,90,0.12);
    border: 1px solid rgba(184,148,90,0.25);
    color: #c9a06a;
    border-radius: 20px;
    padding: 0.2rem 0.75rem;
    font-size: 0.78rem;
    margin: 0.2rem 0.2rem 0.2rem 0;
    font-family: 'DM Sans', sans-serif;
}
.seniority-badge {
    display: inline-block;
    background: rgba(184,148,90,0.2);
    border: 1px solid rgba(184,148,90,0.4);
    color: #f0d5a0;
    border-radius: 6px;
    padding: 0.3rem 1rem;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Job Cards ── */
.jobs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 1.2rem;
    margin-top: 1.5rem;
}
.job-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.5rem;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.job-card:hover {
    border-color: rgba(184,148,90,0.35);
    background: rgba(184,148,90,0.04);
    transform: translateY(-3px);
    box-shadow: 0 12px 35px rgba(0,0,0,0.3);
}
.job-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(184,148,90,0.3), transparent);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.job-card:hover::after { opacity: 1; }
.job-source-badge {
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #b8945a;
    font-family: 'DM Sans', sans-serif;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}
.job-source-badge::before {
    content: '';
    width: 4px; height: 4px;
    background: #b8945a;
    border-radius: 50%;
    display: inline-block;
}
.job-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.25rem;
    font-weight: 400;
    color: #f0e8dc;
    line-height: 1.3;
    margin-bottom: 0.4rem;
}
.job-company {
    font-size: 0.85rem;
    color: #a09080;
    font-weight: 400;
    margin-bottom: 0.3rem;
}
.job-location {
    font-size: 0.78rem;
    color: #706050;
    display: flex;
    align-items: center;
    gap: 0.3rem;
    margin-bottom: 1rem;
}
.job-link {
    display: inline-block;
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #b8945a;
    text-decoration: none;
    border-bottom: 1px solid rgba(184,148,90,0.3);
    padding-bottom: 1px;
    transition: all 0.2s ease;
    font-family: 'DM Sans', sans-serif;
}
.job-link:hover {
    color: #f0d5a0;
    border-bottom-color: #f0d5a0;
}

/* ── Stats Row ── */
.stats-row {
    display: flex;
    gap: 1.5rem;
    margin: 1.5rem 0;
    flex-wrap: wrap;
}
.stat-item {
    flex: 1;
    min-width: 140px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.stat-number {
    font-family: 'Cormorant Garamond', serif;
    font-size: 2rem;
    color: #c9a06a;
    font-weight: 300;
    line-height: 1;
}
.stat-label {
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #605040;
    margin-top: 0.3rem;
    font-family: 'DM Sans', sans-serif;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 2.5rem 0 1rem;
}
.section-header-line {
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}
.section-header-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: #605040;
    white-space: nowrap;
}

/* ── Spinner & Alerts ── */
[data-testid="stSpinner"] { color: #b8945a !important; }
.stAlert { border-radius: 10px !important; border: none !important; }
[data-testid="stSuccess"] {
    background: rgba(100,180,100,0.08) !important;
    color: #90c890 !important;
    border: 1px solid rgba(100,180,100,0.2) !important;
}
[data-testid="stError"] {
    background: rgba(180,80,80,0.08) !important;
    color: #d09090 !important;
    border: 1px solid rgba(180,80,80,0.2) !important;
}
[data-testid="stInfo"] {
    background: rgba(184,148,90,0.06) !important;
    color: #b8945a !important;
    border: 1px solid rgba(184,148,90,0.15) !important;
}
[data-testid="stWarning"] {
    background: rgba(200,160,60,0.08) !important;
    color: #c8a060 !important;
    border: 1px solid rgba(200,160,60,0.2) !important;
}

/* ── Text inputs ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #e8e0d5 !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(184,148,90,0.4) !important;
    box-shadow: 0 0 0 2px rgba(184,148,90,0.1) !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    color: #e8e0d5 !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 8px !important;
    color: #8a8070 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.05em !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(184,148,90,0.3); border-radius: 4px; }

/* ── Source color coding ── */
.source-linkedin { color: #7bb4e3; }
.source-indeed { color: #e38a7b; }
.source-remoteok { color: #7be3a0; }
.source-weworkremotely { color: #a07be3; }
.source-naukri { color: #e3c97b; }
.source-simplyhired { color: #7be3d4; }
.source-careerjet { color: #e37bb4; }
.sidebar-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #b8945a;
    margin: 0 0 0.25rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid rgba(184,148,90,0.2);
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# SIDEBAR — location filters
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-title">Filters</p>', unsafe_allow_html=True)
    st.caption("Applies to company list, matched jobs & manual search.")
    with st.expander("India & states", expanded=True):
        india_only_jobs = st.checkbox(
            "Only **India** locations",
            value=False,
            key="cb_india_only",
            help="Job location text must look Indian. Combine with states to narrow further.",
        )
        india_state_pick = st.multiselect(
            "States / UT (optional)",
            options=indian_state_options(),
            default=[],
            key="ms_india_states",
            help="Matches state names and major cities in the job location field.",
        )


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def source_class(source: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9]+", "", (source or "unknown").lower())[:24] or "unknown"
    return f"source-{safe}"

def render_profile_card(profile: dict):
    roles = profile.get("roles", [])
    skills = profile.get("skills", [])
    education = profile.get("education", [])
    locations = profile.get("preferred_locations", [])
    seniority = profile.get("seniority_level", "")
    experience = profile.get("experience_years", 0)

    roles_html = "".join(f'<span class="tag">{r}</span>' for r in roles) or "<span class='profile-value'>—</span>"
    skills_html = "".join(f'<span class="tag">{s}</span>' for s in skills) or "<span class='profile-value'>—</span>"
    edu_html = "".join(f'<span class="tag">{e}</span>' for e in education) or "<span class='profile-value'>—</span>"
    loc_html = "".join(f'<span class="tag">{l}</span>' for l in locations) or "<span class='profile-value'>Worldwide</span>"
    seniority_html = f'<span class="seniority-badge">{seniority}</span>' if seniority else "<span class='profile-value'>—</span>"

    st.markdown(f"""
    <div class="profile-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
            <div style="flex:1; min-width:200px;">
                <div class="profile-section-title">Target Roles</div>
                <div>{roles_html}</div>
                <div class="profile-section-title">Skills</div>
                <div>{skills_html}</div>
                <div class="profile-section-title">Education</div>
                <div>{edu_html}</div>
            </div>
            <div style="min-width:180px;">
                <div class="profile-section-title">Seniority</div>
                <div>{seniority_html}</div>
                <div class="profile-section-title">Experience</div>
                <div class="profile-value">{experience} year{"s" if experience != 1 else ""}</div>
                <div class="profile-section-title">Locations</div>
                <div>{loc_html}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_job_cards(jobs: list):
    # Group by source for stats
    sources = {}
    for job in jobs:
        src = job.get("source", "Unknown")
        sources[src] = sources.get(src, 0) + 1

    # Stats row
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="stat-item"><div class="stat-number">{len(jobs)}</div><div class="stat-label">Total Jobs Found</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-item"><div class="stat-number">{len(sources)}</div><div class="stat-label">Sources Searched</div></div>', unsafe_allow_html=True)

    # Cards grid
    # No leading indentation on HTML lines — Markdown treats 4+ space indent as a code block
    # and Streamlit would show raw tags in a grey box instead of rendering the card.
    cards_html = '<div class="jobs-grid">'
    for job in jobs:
        if not isinstance(job, dict):
            continue
        title = sanitize_job_text(job.get("title") or "Unknown Role")
        company = sanitize_job_text(job.get("company") or "Unknown Company")
        location = sanitize_job_text(job.get("location") or "")
        link = job.get("link", "") or ""
        source = sanitize_job_text(job.get("source") or "")
        src_cls = source_class(job.get("source") or "")

        safe_href = sanitize_job_href(link)
        link_html = (
            f'<a class="job-link" href="{safe_href}" target="_blank" rel="noopener noreferrer">View Position →</a>'
            if safe_href
            else ""
        )
        list_co_raw = job.get("matched_sheet_company") or ""
        list_co = sanitize_job_text(list_co_raw)
        list_html = (
            f"<div class='job-location'>✦ From your list: {list_co}</div>" if list_co_raw else ""
        )

        loc_block = ""
        if location and job.get("location") not in (None, "", "N/A"):
            loc_block = f"<div class='job-location'>📍 {location}</div>"

        cards_html += (
            f'<div class="job-card">'
            f'<div class="job-source-badge {src_cls}">{source}</div>'
            f'<div class="job-title">{title}</div>'
            f'<div class="job-company">{company}</div>'
            f"{loc_block}{list_html}{link_html}"
            f"</div>"
        )

    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)


def section_header(text: str):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-line"></div>
        <div class="section-header-title">{text}</div>
        <div class="section-header-line"></div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# HERO
# ─────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">✦ AI-Powered Career Discovery</div>
    <div class="hero-title">Find Your<br><em>Dream Role</em></div>
    <div class="hero-subtitle">Upload your resume—or a company list in Excel—to discover analyst roles</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# UPLOAD SECTION (resume OR company spreadsheet)
# ─────────────────────────────────────────
section_header("Upload")

st.markdown(
    "<p style='color:#8a8070;font-size:0.9rem;margin:0 0 1rem;text-align:center;'>"
    "<strong>Resume</strong> — PDF, Word, or text · "
    "<strong>Company list</strong> — .xlsx with a <strong>Company</strong> column (or names in column C). "
    "For Excel we search <strong>data / business analyst</strong> roles and can "
    "<strong>fill the Role / Links column</strong> when you download. "
    "Use <strong>Filters</strong> in the left sidebar for India / state.</p>",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader(
        "Resume or company spreadsheet",
        type=["pdf", "docx", "txt", "xlsx"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        fname = uploaded_file.name or ""
        is_xlsx = fname.lower().endswith(".xlsx")
        icon = "📊" if is_xlsx else "📄"
        st.markdown(
            f"<div style='text-align:center; font-size:0.8rem; color:#b8945a; margin:0.5rem 0;'>"
            f"{icon} {fname}</div>",
            unsafe_allow_html=True,
        )

        if is_xlsx:
            fill_excel_links = st.checkbox(
                "Put job links in the spreadsheet (Role / Links column, matched to each company)",
                value=True,
                key="cb_fill_excel_links",
            )
            c_find, c_dl = st.columns(2, gap="large")
            with c_find:
                excel_run = st.button(
                    "✦  Find analyst jobs at these companies",
                    use_container_width=True,
                    key="btn_excel_jobs",
                )
            with c_dl:
                if st.session_state.get("company_excel_bytes"):
                    st.download_button(
                        label="✦  Download spreadsheet with links",
                        data=st.session_state["company_excel_bytes"],
                        file_name=st.session_state.get(
                            "company_excel_filename",
                            "companies_with_job_links.xlsx",
                        ),
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="dl_company_xlsx_persist",
                    )

            flash_ok = st.session_state.pop("company_excel_success_msg", None)
            flash_warn = st.session_state.pop("company_excel_warn_msg", None)
            flash_info = st.session_state.pop("company_excel_info_msg", None)
            if flash_ok:
                st.success(flash_ok)
            if flash_info:
                st.info(flash_info)
            if flash_warn:
                st.warning(flash_warn)

            if excel_run:
                resp = None
                with st.spinner(
                    "Searching job boards for each company (this can take a few minutes)..."
                ):
                    try:
                        form_data = {
                            "fill_spreadsheet": "true" if fill_excel_links else "false",
                            "india_only": "true" if india_only_jobs else "false",
                            "india_states": ",".join(india_state_pick),
                        }
                        resp = requests.post(
                            f"{API_URL}/api/jobs-from-companies",
                            files={
                                "file": (
                                    uploaded_file.name,
                                    uploaded_file.getvalue(),
                                    uploaded_file.type,
                                )
                            },
                            data=form_data,
                            timeout=300,
                        )
                    except requests.exceptions.Timeout:
                        st.error("Timed out — try a smaller list or run again.")
                    except Exception as e:
                        st.error(f"Error: {e}")

                if resp is not None:
                    if resp.status_code == 200:
                        data = resp.json()
                        jobs = data.get("results", [])
                        meta = data.get("meta") or {}
                        st.session_state["company_jobs"] = jobs
                        ind_parts = []
                        if meta.get("india_only"):
                            ind_parts.append("India only")
                        if meta.get("india_states"):
                            ind_parts.append(
                                f"states: {', '.join(meta.get('india_states', []))}"
                            )
                        ind_note = f" ({'; '.join(ind_parts)})" if ind_parts else ""
                        st.session_state["company_excel_success_msg"] = (
                            f"✦ Searched **{meta.get('companies_searched', '?')}** companies "
                            f"({meta.get('queries_run', '?')} queries) — **{len(jobs)}** "
                            f"matching analyst roles{ind_note}."
                        )
                        b64 = data.get("filled_xlsx_base64")
                        if b64:
                            out_name = (
                                data.get("filled_filename")
                                or "companies_with_job_links.xlsx"
                            )
                            st.session_state["company_excel_bytes"] = (
                                base64.standard_b64decode(b64)
                            )
                            st.session_state["company_excel_filename"] = out_name
                        else:
                            st.session_state.pop("company_excel_bytes", None)
                            st.session_state.pop("company_excel_filename", None)
                            if fill_excel_links:
                                st.session_state["company_excel_info_msg"] = (
                                    "No filled spreadsheet in the response. "
                                    "Redeploy the backend with the latest code if this persists."
                                )
                        if meta.get("raw_unique", 0) and not jobs:
                            st.session_state["company_excel_warn_msg"] = (
                                "Jobs were found but none passed the analyst + company filter. "
                                "Try shortening company names to match how job sites display them."
                            )
                        st.rerun()
                    else:
                        st.error(
                            f"Request failed ({resp.status_code}): {api_error_message(resp)}"
                        )

        else:
            if st.button("✦  Analyze Resume"):
                with st.spinner("Reading your story..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/api/upload-resume",
                            files={
                                "file": (
                                    uploaded_file.name,
                                    uploaded_file.getvalue(),
                                    uploaded_file.type,
                                )
                            },
                            timeout=60,
                        )
                        if response.status_code == 200:
                            data = response.json()
                            if "profile" in data:
                                clear_refine_widget_keys()
                                st.session_state["profile"] = data["profile"]
                                st.success("✦ Resume analyzed successfully")
                                warn = data.get("warning")
                                if warn:
                                    st.warning(warn)
                            else:
                                st.error("No profile returned")
                        else:
                            st.error(f"Failed ({response.status_code}): {response.text}")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out — try again")
                    except Exception as e:
                        st.error(f"Error: {e}")

if st.session_state.get("company_jobs"):
    render_job_cards(st.session_state["company_jobs"])


# ─────────────────────────────────────────
# PROFILE DISPLAY
# ─────────────────────────────────────────
if "profile" in st.session_state:
    section_header("Your Profile")

    # Seed keys before any widgets (Streamlit expanders may not mount children while collapsed.)
    seed_refine_keys_from_profile()

    st.markdown(
        "<p style='color:#8a8070;font-size:0.9rem;margin:0.4rem 0 0.8rem;'>"
        "Job search uses the fields below. Add <strong>at least one role or skill</strong> "
        "(comma-separated) if your resume summary is empty.</p>",
        unsafe_allow_html=True,
    )
    seniority_options = ["", "Junior", "Mid", "Senior", "Lead"]
    rc1, rc2 = st.columns(2)
    with rc1:
        st.text_input("Target roles (comma-separated)", key="refine_roles")
        st.text_input("Locations (comma-separated)", key="refine_locations")
    with rc2:
        st.text_input("Key skills (comma-separated)", key="refine_skills")
        st.selectbox("Seniority", seniority_options, key="refine_seniority")

    sync_profile_from_refine_widgets()
    render_profile_card(st.session_state["profile"])

    # ─────────────────────────────────────────
    # JOB SEARCH
    # ─────────────────────────────────────────
    section_header("Matched Opportunities")
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("✦  Find My Dream Jobs"):
            sync_profile_from_refine_widgets()
            payload = dict(st.session_state["profile"])
            # Prefer live widget strings so the request always matches what the user typed
            rraw = (st.session_state.get("refine_roles") or "").strip()
            sraw = (st.session_state.get("refine_skills") or "").strip()
            if rraw:
                payload["roles"] = [x.strip() for x in rraw.split(",") if x.strip()]
            if sraw:
                payload["skills"] = [x.strip() for x in sraw.split(",") if x.strip()]
            if not payload.get("roles") and not payload.get("skills"):
                st.error(
                    "Add at least one **target role** or **key skill** in the fields above "
                    "(comma-separated), then try again."
                )
            else:
                payload["india_only"] = bool(india_only_jobs)
                payload["india_states"] = list(india_state_pick)
                with st.spinner("Searching across LinkedIn, Indeed, RemoteOK and more..."):
                    try:
                        response = requests.post(
                            f"{API_URL}/api/jobs",
                            json=payload,
                            timeout=180
                        )
                        if response.status_code == 200:
                            data = response.json()
                            jobs = data.get("results", [])
                            if jobs:
                                st.session_state["jobs"] = jobs
                            else:
                                st.warning("No jobs found — try refining your profile above")
                        else:
                            st.error(
                                f"Search failed ({response.status_code}): {api_error_message(response)}"
                            )
                    except requests.exceptions.Timeout:
                        st.error("Search timed out — scraping can be slow, try again")
                    except Exception as e:
                        st.error(f"Error: {e}")

    if "jobs" in st.session_state:
        render_job_cards(st.session_state["jobs"])

else:
    st.markdown("""
    <div style="text-align:center; padding: 3rem; color: #504030;">
        <div style="font-size:2rem; margin-bottom:0.5rem;">✦</div>
        <div style="font-family:'DM Sans',sans-serif; font-size:0.85rem; letter-spacing:0.1em;">
            Upload a resume to begin
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────
# MANUAL SEARCH
# ─────────────────────────────────────────
section_header("Manual Search")

col1, col2 = st.columns([3, 1])
with col1:
    query = st.text_input(
        "Search keywords",
        placeholder="e.g.  Python Developer  ·  Data Scientist  ·  UX Designer",
        label_visibility="collapsed",
    )
with col2:
    search_clicked = st.button("✦  Search")

if search_clicked and query.strip():
    with st.spinner(f'Searching for "{query}"...'):
        try:
            manual_profile = {
                "roles": [query.strip()],
                "skills": [],
                "experience_years": 0,
                "education": [],
                "preferred_locations": ["Worldwide"],
                "seniority_level": "",
                "india_only": bool(india_only_jobs),
                "india_states": list(india_state_pick),
            }
            response = requests.post(
                f"{API_URL}/api/jobs",
                json=manual_profile,
                timeout=180
            )
            if response.status_code == 200:
                jobs = response.json().get("results", [])
                if jobs:
                    render_job_cards(jobs)
                else:
                    st.warning("No results found — try a different query")
            else:
                st.error(
                    f"Search failed ({response.status_code}): {api_error_message(response)}"
                )
        except Exception as e:
            st.error(f"Error: {e}")


# ─────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 4rem 0 2rem; color: #302010;">
    <div style="font-family:'Cormorant Garamond',serif; font-size:1.1rem; font-style:italic; color:#504030;">
        Made with love ♡
    </div>
    <div style="font-size:0.65rem; letter-spacing:0.2em; text-transform:uppercase; margin-top:0.5rem; color:#302010;">
        AI Job Copilot · Powered by Groq
    </div>
</div>
""", unsafe_allow_html=True)