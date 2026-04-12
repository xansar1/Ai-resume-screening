import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/parse_resume/"

st.set_page_config(page_title="AI Resume Screening", layout="wide")

st.title("📄 AI Resume Screening Dashboard")
st.write("Upload a candidate resume and get AI-powered structured insights.")

uploaded_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

if uploaded_file:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.info("⏳ Parsing resume...")
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        res = requests.post(API_URL, files=files)

    with col2:
        if res.status_code == 200:
            data = res.json()

            if "error" in data:
                st.error(data["error"])
            else:
                st.success("✅ Resume parsed successfully")

                st.metric("ATS Score", f"{data.get('ats_score', 0)}%")
                st.subheader("👤 Candidate Summary")
                st.write(data.get("summary", "No summary"))

                st.subheader("🛠 Skills")
                skills = data.get("skills", [])
                for skill in skills:
                    st.badge(skill)

                st.subheader("📦 Full JSON Output")
                st.json(data)
