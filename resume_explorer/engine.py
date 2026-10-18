"""Local explainable text comparison. All matches are mentions, not verified proficiency."""
from __future__ import annotations
import io
import re
from pathlib import Path
import zipfile
from typing import Any

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_PAGES = 20
MAX_CHARS = 50_000

# Case-insensitive literal/alias lookup: boundary guards prevent substrings
# such as SQL inside another token. Skills mentioned in negated text are NOT inferred.
SKILLS: dict[str, tuple[str, ...]] = {
    'Python': ('python',),
    'SQL': ('sql', 'postgresql', 'postgres', 'mysql', 'sqlite'),
    'Machine Learning': ('machine learning', 'ml models', 'ml pipeline'),
    'NLP': ('natural language processing', 'nlp'),
    'FastAPI': ('fastapi',),
    'Streamlit': ('streamlit',),
    'Pandas': ('pandas',),
    'NumPy': ('numpy',),
    'scikit-learn': ('scikit-learn', 'scikit learn', 'sklearn'),
    'PyTorch': ('pytorch',),
    'TensorFlow': ('tensorflow',),
    'Docker': ('docker',),
    'Git': ('git', 'github', 'gitlab'),
    'AWS': ('aws', 'amazon web services'),
    'Azure': ('azure',),
    'GCP': ('google cloud', 'gcp'),
    'JavaScript': ('javascript',),
    'TypeScript': ('typescript',),
    'React': ('react', 'react.js', 'reactjs'),
    'Node.js': ('node.js', 'nodejs'),
    'REST APIs': ('rest api', 'restful api', 'rest apis'),
    'Data Visualization': ('data visualization', 'data visualisation', 'plotly', 'matplotlib', 'tableau'),
    'Power BI': ('power bi',),
    'Excel': ('excel', 'spreadsheets'),
    'Statistics': ('statistics', 'statistical analysis'),
    'ETL': ('etl', 'data pipelines', 'data pipeline'),
    'MongoDB': ('mongodb',),
    'PostgreSQL': ('postgresql', 'postgres'),
    'Testing': ('pytest', 'unit testing', 'automated tests', 'integration testing'),
    'Communication': ('stakeholder communication', 'technical communication'),
}

SAMPLE_RESUME = '''SAMPLE RESUME — FICTIONAL PERSON
Alex Morgan, Software & Data Projects
Summary: Built Python data-processing and analytics demonstrations.
Projects:
- Designed a Streamlit dashboard using Pandas and Plotly for a synthetic academic dataset.
- Built REST APIs with FastAPI and SQL-based sample reporting.
- Used Git and pytest for version control and automated tests.
Tools: Python, Pandas, FastAPI, Streamlit, SQL, Git, pytest, Plotly.
Education: Bachelor's degree (fictional example).
'''
SAMPLE_JD = '''Sample project brief (fictional): Looking for a contributor familiar with Python,
SQL, FastAPI, Docker, Streamlit, Pandas, Git and AWS. Experience creating REST APIs,
writing automated tests and communicating findings is helpful.
'''

EMAIL_RE = re.compile(r'(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?!\w)')
PHONE_RE = re.compile(r'(?<!\w)(?:\+?\d[\d ().-]{7,}\d)(?!\w)')
URL_RE = re.compile(r'https?://\S+|www\.\S+', re.I)


def redact(text: str) -> str:
    """Best-effort removal of email, phone and URLs, not a guarantee of anonymity."""
    text = EMAIL_RE.sub('[email redacted]', text)
    text = PHONE_RE.sub('[phone redacted]', text)
    return URL_RE.sub('[url redacted]', text)


def _patterns(name: str):
    for alias in SKILLS[name]:
        # Unicode-aware boundaries avoid finding skill names in longer words.
        yield re.compile(r'(?<![\w])' + re.escape(alias).replace(r'\ ', r'\s+') + r'(?![\w])', re.IGNORECASE)


def mentioned_skills(text: str) -> dict[str, str]:
    """Map canonical skill to a short redacted evidence excerpt."""
    if not isinstance(text, str):
        raise ValueError('Expected a text string')
    result: dict[str, str] = {}
    for skill in SKILLS:
        hits = [m for pattern in _patterns(skill) for m in pattern.finditer(text)]
        if hits:
            earliest = min(hits, key=lambda m: m.start())
            start, end = max(0, earliest.start()-57), min(len(text), earliest.end()+64)
            preview = text[start:end].replace('\n', ' ').strip()
            result[skill] = redact(('…' if start else '') + preview + ('…' if end < len(text) else ''))
    return result


def shared_terms(resume: str, job: str, limit: int = 12) -> list[str]:
    """TF-IDF overlapping 1–2-gram terms; lexical evidence, NOT semantic fit."""
    from sklearn.feature_extraction.text import TfidfVectorizer
    if not resume.strip() or not job.strip():
        return []
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2),
                                     token_pattern=r'(?u)\b[a-zA-Z][\w+#.-]*\b', max_features=4000)
        matrix = vectorizer.fit_transform([resume[:MAX_CHARS], job[:MAX_CHARS]])
        names = vectorizer.get_feature_names_out()
        strengths = matrix[0].multiply(matrix[1]).toarray().ravel()
        ranked = sorted(range(len(names)), key=lambda i: (-strengths[i], names[i]))
        return [str(names[i]) for i in ranked if strengths[i] > 0][:limit]
    except ValueError:  # empty vocabulary, e.g. all stopwords
        return []


def analyze(resume: str, job: str) -> dict[str, Any]:
    if not resume or len(resume.strip()) < 30:
        raise ValueError('Provide resume text with at least 30 characters.')
    if not job or len(job.strip()) < 30:
        raise ValueError('Provide a job description with at least 30 characters.')
    if len(resume) > MAX_CHARS or len(job) > MAX_CHARS:
        raise ValueError('Text too long (maximum 50,000 characters per document).')
    resume_hits = mentioned_skills(resume)
    jd_hits = mentioned_skills(job)
    matched = sorted(set(jd_hits) & set(resume_hits), key=str.casefold)
    jd_only = sorted(set(jd_hits) - set(resume_hits), key=str.casefold)
    resume_only = sorted(set(resume_hits) - set(jd_hits), key=str.casefold)
    return {
        'source': 'text mention comparison (not a candidate score)',
        'job_skills': sorted(jd_hits, key=str.casefold),
        'resume_skills': sorted(resume_hits, key=str.casefold),
        'mentioned_in_both': matched,
        'mentioned_only_in_job': jd_only,
        'mentioned_only_in_resume': resume_only,
        'evidence': [{'skill': s, 'resume_excerpt': resume_hits[s], 'job_excerpt': jd_hits[s]} for s in matched],
        'overlapping_terms': shared_terms(resume, job),
        'resume_excerpt_redacted': redact(resume[:700]),
        'limitations': [
            'Keyword mentions do not prove skills, expertise, qualifications or experience.',
            'Absence of a keyword does not mean absence of ability.',
            'Negated or hypothetical skill mentions may be counted; manually verify context.',
            'Lexical overlap is not semantic understanding or a hiring suitability assessment.',
            'Do not use this tool to rank, reject or select applicants.'
        ]
    }


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from supported types; never persist uploaded bytes."""
    if not isinstance(file_bytes, bytes) or not file_bytes:
        raise ValueError('Choose a nonempty file.')
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise ValueError('File exceeds the 5 MB demo limit.')
    ext = Path(filename).suffix.lower()
    try:
        if ext == '.pdf':
            if not file_bytes.startswith(b'%PDF'):
                raise ValueError('File is not a valid PDF.')
            import pdfplumber
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                if len(pdf.pages) > MAX_PAGES:
                    raise ValueError('Only PDFs with 20 pages or fewer are supported.')
                text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
        elif ext == '.docx':
            if not file_bytes.startswith(b'PK'):
                raise ValueError('File is not a valid DOCX.')
            with zipfile.ZipFile(io.BytesIO(file_bytes)) as archive:
                if sum(info.file_size for info in archive.infolist()) > 15 * 1024 * 1024:
                    raise ValueError('DOCX expanded contents exceed the safety limit.')
            from docx import Document
            document = Document(io.BytesIO(file_bytes))
            lines = [p.text for p in document.paragraphs]
            for table in document.tables:
                for row in table.rows:
                    lines.append(' | '.join(cell.text for cell in row.cells))
            text = '\n'.join(lines)
        elif ext == '.txt':
            text = file_bytes.decode('utf-8-sig', errors='strict')
        else:
            raise ValueError('Supported file formats: PDF, DOCX or TXT.')
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError('Could not extract text. Check that the file is not corrupt, encrypted or scanned.') from exc
    if len(text) > MAX_CHARS:
        raise ValueError('Extracted text exceeds the 50,000-character demo limit.')
    if len(text.strip()) < 30:
        raise ValueError('Too little extractable text. Scanned PDFs require OCR (not included).')
    return text
