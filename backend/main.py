from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import io
import re

app = FastAPI(title="AI Hiring Intelligence API")

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== PDF TEXT EXTRACTION =====
def extract_text_from_pdf(uploaded_file):
    contents = uploaded_file.file.read()
    uploaded_file.file.seek(0)

    text = ""
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text.strip()


# ===== SKILL EXTRACTION =====
def extract_skills(text):
    common_skills = [
        "Python",
        "SQL",
        "Machine Learning",
        "FastAPI",
        "Streamlit",
        "Pandas",
        "NLP",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Data Visualization",
        "Power BI",
        "Excel"
    ]

    found_skills = []

    for skill in common_skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    return found_skills


# ===== ATS SCORE =====
def calculate_ats_score(skills, jd_text=""):
    base_score = 60
    skill_bonus = min(len(skills) * 5, 30)

    jd_bonus = 0
    if jd_text:
        jd_keywords = jd_text.lower().split()
        matched = sum(
            1 for skill in skills
            if skill.lower() in jd_keywords
        )
        jd_bonus = min(matched * 2, 10)

    return min(base_score + skill_bonus + jd_bonus, 100)


# ===== RECOMMENDATION =====
def generate_recommendation(score):
    if score >= 90:
        return "Excellent Fit"
    elif score >= 75:
        return "Good Fit"
    elif score >= 60:
        return "Average Fit"
    return "Needs Improvement"


# ===== MAIN ENDPOINT =====
@app.post("/parse_resume/")
async def parse_resume(
    file: UploadFile = File(...),
    job_description: str = Form(default="")
):
    try:
        text = extract_text_from_pdf(file)

        email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
        phone = re.findall(r'\+?\d[\d\s-]{8,}', text)

        skills = extract_skills(text)

        ats_score = calculate_ats_score(skills, job_description)
        recommendation = generate_recommendation(ats_score)

        name = text.split("\n")[0] if text else "Unknown"

        return {
            "name": name,
            "email": email[0] if email else "",
            "phone": phone[0] if phone else "",
            "skills": skills,
            "preview": text[:500],
            "ats_score": ats_score,
            "recommendation": recommendation,
            "jd_match": min(ats_score + 5, 100),
            "recruiter_insights": [
                "Strong Python foundation",
                "Good ML & NLP exposure",
                "FastAPI + Streamlit experience",
                "ATS-friendly resume structure"
            ]
        }

    except Exception as e:
        return {
            "error": str(e),
            "name": "Unknown",
            "skills": [],
            "ats_score": 0
        }
