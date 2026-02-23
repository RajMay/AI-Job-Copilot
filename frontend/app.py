import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Job Copilot",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 AI Job Copilot")
st.write("Find jobs tailored to your resume")

# --------------------------------
# 📄 Resume Upload Section
# --------------------------------
st.header("📄 Upload Resume")

uploaded_file = st.file_uploader(
    "Upload PDF/DOCX/TXT",
    type=["pdf", "docx", "txt"]
)

if uploaded_file:

    if st.button("🔍 Analyze Resume"):

        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type
            )
        }

        response = requests.post(
            f"{API_URL}/upload-resume",
            files=files
        )

        if response.status_code == 200:

            data = response.json()

            st.write("DEBUG API RESPONSE:")
            st.json(data)

            # ⭐ IMPORTANT — Extract profile safely
            if "profile" in data:

                profile = data["profile"]

                st.success("✅ Resume analyzed!")

                st.subheader("🧠 Extracted Profile")
                st.json(profile)

                # Save profile for later
                st.session_state["profile"] = profile

            else:
                st.error("❌ No profile returned by API")
                st.json(data)

        else:
            st.error("❌ Failed to analyze resume")


# --------------------------------
# 🤖 Job Search From Resume
# --------------------------------
st.header("🤖 Find Jobs From Resume")

if "profile" in st.session_state:

    if st.button("✨ Find Jobs Matching My Profile"):

        response = requests.post(
            f"{API_URL}/jobs-from-resume",
            json={"profile": st.session_state["profile"]}
        )

        if response.status_code == 200:

            jobs = response.json().get("results", [])

            if not jobs:
                st.warning("No jobs found")
            else:
                st.success(f"Found {len(jobs)} jobs")

                for job in jobs:

                    with st.container():
                        st.markdown("---")

                        st.subheader(job.get("title", "Unknown"))

                        st.write(
                            f"🏢 {job.get('company', 'Unknown')} "
                            f"| 📍 {job.get('location', 'Unknown')}"
                        )

                        st.write(f"🌐 Source: {job.get('source')}")

                        st.link_button(
                            "🔗 View Job",
                            job.get("link", "#")
                        )

        else:
            st.error("❌ Job search failed")

else:
    st.info("Upload and analyze a resume first")


# --------------------------------
# 🔎 Manual Job Search
# --------------------------------
st.header("🔎 Manual Search")

query = st.text_input("Search jobs manually")

if st.button("Search"):

    if query:

        response = requests.post(
            f"{API_URL}/jobs",
            json={"query": query}
        )

        if response.status_code == 200:

            jobs = response.json().get("results", [])

            if not jobs:
                st.warning("No results")
            else:
                for job in jobs:

                    with st.container():
                        st.markdown("---")

                        st.subheader(job.get("title", "Unknown"))

                        st.write(
                            f"🏢 {job.get('company', 'Unknown')} "
                            f"| 📍 {job.get('location', 'Unknown')}"
                        )

                        st.link_button(
                            "🔗 View Job",
                            job.get("link", "#")
                        )

        else:
            st.error("Search failed")