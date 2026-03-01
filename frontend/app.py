import streamlit as st
import requests

API_URL = "https://ai-job-copilot-1.onrender.com"

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AI Job Copilot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
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
[data-testid="stSidebar"] { display: none !important; }
.block-container { max-width: 1100px !important; padding: 3rem 2rem !important; }

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
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def source_class(source: str) -> str:
    return f"source-{source.lower().replace(' ', '')}"

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
    cards_html = '<div class="jobs-grid">'
    for job in jobs:
        title = job.get("title", "Unknown Role")
        company = job.get("company", "Unknown Company")
        location = job.get("location", "")
        link = job.get("link", "#")
        source = job.get("source", "")
        src_cls = source_class(source)

        link_html = f'<a class="job-link" href="{link}" target="_blank">View Position →</a>' if link and link != "N/A" else ""

        cards_html += f"""
        <div class="job-card">
            <div class="job-source-badge {src_cls}">{source}</div>
            <div class="job-title">{title}</div>
            <div class="job-company">{company}</div>
            {"<div class='job-location'>📍 " + location + "</div>" if location and location != "N/A" else ""}
            {link_html}
        </div>"""

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
    <div class="hero-subtitle">Upload your resume and let AI match you with opportunities across the world</div>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# UPLOAD SECTION
# ─────────────────────────────────────────
section_header("Upload Resume")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader(
        "Drop your resume here",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.markdown(f"<div style='text-align:center; font-size:0.8rem; color:#b8945a; margin:0.5rem 0;'>📄 {uploaded_file.name}</div>", unsafe_allow_html=True)

        if st.button("✦  Analyze Resume"):
            with st.spinner("Reading your story..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/upload-resume",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        timeout=60
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if "profile" in data:
                            st.session_state["profile"] = data["profile"]
                            st.success("✦ Resume analyzed successfully")
                        else:
                            st.error("No profile returned")
                    else:
                        st.error(f"Failed ({response.status_code}): {response.text}")
                except requests.exceptions.Timeout:
                    st.error("Request timed out — try again")
                except Exception as e:
                    st.error(f"Error: {e}")


# ─────────────────────────────────────────
# PROFILE DISPLAY
# ─────────────────────────────────────────
if "profile" in st.session_state:
    section_header("Your Profile")
    render_profile_card(st.session_state["profile"])

    # Edit expander
    with st.expander("✎  Refine before searching"):
        profile = st.session_state["profile"]
        c1, c2 = st.columns(2)
        with c1:
            roles_input = st.text_input("Roles", value=", ".join(profile.get("roles", [])))
            location_input = st.text_input("Locations", value=", ".join(profile.get("preferred_locations", [])))
        with c2:
            seniority_input = st.selectbox(
                "Seniority",
                ["", "Junior", "Mid", "Senior", "Lead"],
                index=["", "Junior", "Mid", "Senior", "Lead"].index(profile.get("seniority_level", ""))
                if profile.get("seniority_level", "") in ["", "Junior", "Mid", "Senior", "Lead"] else 0
            )
            skills_input = st.text_input("Key Skills", value=", ".join(profile.get("skills", [])[:5]))

        if st.button("✦  Update Profile"):
            st.session_state["profile"]["roles"] = [r.strip() for r in roles_input.split(",") if r.strip()]
            st.session_state["profile"]["preferred_locations"] = [l.strip() for l in location_input.split(",") if l.strip()]
            st.session_state["profile"]["seniority_level"] = seniority_input
            st.session_state["profile"]["skills"] = [s.strip() for s in skills_input.split(",") if s.strip()]
            st.rerun()

    # ─────────────────────────────────────────
    # JOB SEARCH
    # ─────────────────────────────────────────
    section_header("Matched Opportunities")
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        if st.button("✦  Find My Dream Jobs"):
            with st.spinner("Searching across LinkedIn, Indeed, RemoteOK and more..."):
                try:
                    response = requests.post(
                        f"{API_URL}/api/jobs",
                        json=st.session_state["profile"],
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
                        st.error(f"Search failed ({response.status_code})")
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
    query = st.text_input("", placeholder="e.g.  Python Developer  ·  Data Scientist  ·  UX Designer", label_visibility="collapsed")
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
                "seniority_level": ""
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
                st.error(f"Search failed ({response.status_code})")
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