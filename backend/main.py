from fastapi import FastAPI, UploadFile, File
import pdfplumber
import io
import re

app = FastAPI()

def extract_text_from_pdf(uploaded_file):
    contents = uploaded_file.file.read()
    uploaded_file.file.seek(0)

    text = ""
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


@app.post("/parse_resume/")
async def parse_resume(file: UploadFile = File(...)):
    text = extract_text_from_pdf(file)

    email = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    phone = re.findall(r'\+?\d[\d\s-]{8,}', text)

    skills = []
    common_skills = [
        "Python", "SQL", "Machine Learning",
        "FastAPI", "Streamlit", "Pandas", "NLP"
    ]

    for skill in common_skills:
        if skill.lower() in text.lower():
            skills.append(skill)

    return {
        "name": text.split("\n")[0] if text else "Unknown",
        "email": email[0] if email else "",
        "phone": phone[0] if phone else "",
        "skills": skills,
        "preview": text[:300]
    }
