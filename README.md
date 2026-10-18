# Resume Evidence Explorer V2

A self-contained **Python + Streamlit** resume/JD *text-evidence exploration* demo. Replaces invented ATS/hiring scores and random percentages from the original repo with reproducible skill mentions, excerpts, and TF-IDF shared terms.

## Features
- PDF, DOCX, TXT upload, or fictional example (no upload needed)
- Deterministic canonical skill mention extraction with aliases and boundaries
- Job terms present in resume, not mentioned, and extra resume mentions
- Redacted context excerpts, lexical overlap via TF-IDF (1–2-grams)
- Clear method/limitations and sanitized JSON report
- Optional local-only FastAPI `/api/explore` and `/health` endpoints
- All processing local in the Streamlit Python process; no third-party LLM/API

## Limitations and privacy
This is **not a validated applicant screening, ATS, suitability, fairness or hiring decision tool**. Skill mentions do not establish experience; keywords may be misleading, missed or negated. **No candidate ranking or recommendation**. Uploading real resumes to an online Streamlit instance sends personal data to that hosting provider even though this app does not persist files in a database. Use fictional/test resumes for the public demo. Redaction masks common emails, phones and URLs, but **does not guarantee anonymity**. No raw uploads are exported by default.

## Mac quick start
```bash
cd ~/Downloads/AI_Resume_Explorer_V2
bash scripts/start_mac.sh
```
Open the printed localhost URL. To test:
```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
```
Optional API (local development, not public production):
```bash
PYTHONPATH=. uvicorn api.main:app --host 127.0.0.1 --port 8000
```

## Streamlit Community Cloud
Repository: `xansar1/Ai-resume-screening`, branch: **`resume-evidence-v2-preview`** after running the publish script, main file: `app.py`.

## GitHub publishing
Run `bash scripts/publish_preview.sh` to publish a clean-history preview branch with the standalone demo only. Requires GitHub write access on your Mac. Existing `main` remains untouched. Existing public Git history still contains the former sample resume; remove private documents from published history as needed.

## Validation
`python -m pytest -q`; `python -m py_compile app.py resume_explorer/engine.py api/main.py`.
