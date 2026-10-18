"""Optional local FastAPI integration. Deploy with auth/rate limiting before public exposure."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from resume_explorer.engine import analyze, MAX_CHARS

app = FastAPI(title='Resume Evidence Explorer API', version='2.0.0', docs_url='/docs')

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=30, max_length=MAX_CHARS)
    job_description: str = Field(min_length=30, max_length=MAX_CHARS)

@app.get('/health')
def health():
    return {'ok': True, 'demo': True, 'external_ai': False}

@app.post('/api/explore')
def explore(request: AnalyzeRequest):
    try:
        return analyze(request.resume_text, request.job_description)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
