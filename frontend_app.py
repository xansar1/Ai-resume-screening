import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/parse_resume/"

st.title("📄 AI Resume Reader")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

if uploaded_file is not None:
    st.info("⏳ Sending resume to backend for parsing...")

    # Send the file to FastAPI backend
    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
    try:
        res = requests.post(API_URL, files=files)

        # Debug: show raw API response
        st.write("🔍 Raw API Response:", res.text)

        if res.status_code == 200:
            try:
                data = res.json()
                st.success("✅ Resume parsed successfully!")
                st.json(data)   # nicely formatted JSON output
            except Exception as e:
                st.error("⚠️ Parsing failed")
                st.write("Error details:", str(e))
        else:
            st.error(f"⚠️ API request failed with status code {res.status_code}")

    except Exception as e:
        st.error("❌ Could not connect to backend API.")
        st.write("Error details:", str(e))
