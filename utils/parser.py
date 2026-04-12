from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_resume_text(text):
    prompt = f"""
    Parse this resume into JSON:
    name, email, phone, skills, education, projects, experience, summary
    Resume: {text}
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    return json.loads(res.choices[0].message.content)
