import streamlit as st
import requests
import plotly.express as px
import pandas as pd

API_URL = "http://127.0.0.1:8000/screen_resume/"

st.set_page_config(layout="wide")
st.title("🚀 AI Hiring Intelligence Platform")

uploaded_file = st.file_uploader("Upload Resume PDF", type="pdf")
jd = st.text_area("Paste Job Description")

if st.button("Run AI Screening"):
    if uploaded_file:
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        data = {"job_description": jd}

        res = requests.post(API_URL, files=files, data=data)
        result = res.json()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("ATS Score", f"{result['ats_score']}%")

        with col2:
            st.metric("Recommendation", result["recommendation"])

        with col3:
            st.metric("Candidate", result["candidate_data"].get("name", "Unknown"))

        st.subheader("📌 Candidate Summary")
        st.write(result["candidate_data"].get("summary", ""))

        st.subheader("🛠 Skills")
        skills = result["candidate_data"].get("skills", [])

        if skills:
            df = pd.DataFrame({
                "Skill": skills,
                "Strength": [90] * len(skills)
            })

            fig = px.bar(df, x="Skill", y="Strength")
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("📦 Parsed JSON")
        st.json(result["candidate_data"])
