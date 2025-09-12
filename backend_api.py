from fastapi import FastAPI, UploadFile
import pdfplumber
import json
import io
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key="YOUR_OPENAI_KEY")

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
async def parse_resume(file: UploadFile):
    try:
        text = extract_text_from_pdf(file)

        prompt = f"""
        Extract this resume into a JSON object with fields:
        - name (string)
        - email (string)
        - phone (string)
        - skills (array of strings)
        - experience (array of objects with company, role, start, end, description)
        - education (array of strings)

        Resume text:
        \"\"\"{text}\"\"\"
        """

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}  # ✅ forces valid JSON
        )

        output = resp.choices[0].message.content
        return json.loads(output)   # should always parse now

    except Exception as e:
        return {"error": str(e)}
