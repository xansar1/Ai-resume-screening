from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
import json
import io
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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


@app.post("/parse_resume/")
async def parse_resume(file: UploadFile = File(...)):
    try:
        text = extract_text_from_pdf(file)

        prompt = f"""
        Extract this resume into structured JSON.

        Required fields:
        - name
        - email
        - phone
        - skills
        - total_experience_years
        - top_role
        - education
        - projects
        - ats_score (0-100)
        - summary

        Resume:
        {text}
        """

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return json.loads(resp.choices[0].message.content)

    except Exception as e:
        return {"error": str(e)}
