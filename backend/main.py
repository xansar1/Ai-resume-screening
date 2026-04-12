from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from utils.parser import parse_resume_text
from utils.ats_score import calculate_ats_score
from utils.recommender import generate_recommendation
import pdfplumber
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text(file):
    text = ""
    contents = file.file.read()
    with pdfplumber.open(io.BytesIO(contents)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


@app.post("/screen_resume/")
async def screen_resume(
    file: UploadFile = File(...),
    job_description: str = ""
):
    text = extract_text(file)

    parsed = parse_resume_text(text)
    ats = calculate_ats_score(parsed, job_description)
    recommendation = generate_recommendation(parsed, ats)

    return {
        "candidate_data": parsed,
        "ats_score": ats,
        "recommendation": recommendation
    }
