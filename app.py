"""Streamlit Resume Evidence Explorer V2 (human review only)."""
from __future__ import annotations
import html
import json
import hashlib

import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from resume_explorer import SAMPLE_JD, SAMPLE_RESUME, analyze, extract_text

st.set_page_config(page_title='Resume Evidence Explorer · V2', page_icon='📄', layout='wide', initial_sidebar_state='expanded')

CSS = '''
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--mint:#8CF5D8;--lav:#B8A8FF;--navy:#0b1325;--white:#f3f7ff;--dim:#b4c2d6}
html,body,[data-testid="stApp"]{font-family:'DM Sans',sans-serif!important}
[data-testid="stApp"]{background:radial-gradient(ellipse 70% 36% at 82% 4%,rgba(100,76,180,.2),transparent),radial-gradient(ellipse 44% 38% at 2% 75%,rgba(20,135,136,.13),transparent),#090f1f}
#MainMenu,footer,[data-testid="stDecoration"]{visibility:hidden}
[data-testid="stMainBlockContainer"]{max-width:1430px;padding-top:2.2rem;padding-bottom:4rem}
[data-testid="stSidebar"]{background:#0c162a;border-right:1px solid #253553}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p{color:#b5c5d8}
h1,h2,h3{font-family:'Space Grotesk','DM Sans',sans-serif!important;letter-spacing:-.047em!important}
.hero{background:linear-gradient(125deg,#122c37 0%,#191f3a 51%,#292248 100%);border:1px solid #344d68;border-radius:24px;padding:36px 43px 33px;margin:10px 0 23px;position:relative;overflow:hidden}
.hero:after{content:'◌';position:absolute;right:28px;top:-95px;color:#a9baff14;font-size:380px;line-height:1;pointer-events:none}
.kicker{color:#9ff8df;font-size:11px;letter-spacing:.2em;font-weight:800}.hero h1{font-size:clamp(39px,4.65vw,72px);line-height:1.08;margin:14px 0 17px;color:#f4f7ff;max-width:950px}.hero h1 span{color:var(--mint)}.hero p{max-width:840px;font-size:17px;line-height:1.72;color:#c0cee1;margin:0}.hero .sub{font-size:11px;letter-spacing:.18em;color:#9ff5da;margin-top:25px;font-weight:800}
.brand{display:flex;align-items:center;gap:12px;margin:15px 0 41px;color:#effaff;font:700 23px 'Space Grotesk',sans-serif;letter-spacing:-.06em}.brand strong{color:#a3f8dd}.brand-icon{border-radius:14px;width:45px;height:45px;background:linear-gradient(135deg,#8af7dc,#a8b7ff);display:flex;align-items:center;justify-content:center;color:#102841;font-weight:800;font-size:24px}
.side-overline{font-size:10px;letter-spacing:.19em;color:#90abc5;font-weight:800;margin-bottom:10px}
.side-card{border:1px solid #334963;border-radius:13px;padding:19px 17px;margin:15px 0 30px;background:linear-gradient(125deg,#12243a,#121b30)}.side-card b{color:#9ff3dc}.side-card p{font-size:12px;color:#b1c3d6;margin-bottom:0}
.warn{border-left:3px solid #f1c58b;background:linear-gradient(95deg,#262338,#1c2036);padding:17px 21px;border-radius:8px;font-size:13px;color:#e6d9c4;margin:3px 0 24px}
[data-testid="stMetric"]{background:linear-gradient(140deg,#111f34,#141b2f);border:1px solid #314158;border-radius:15px;padding:18px 20px;min-height:123px}
[data-testid="stMetricLabel"] p{color:#a4b8d2;font-weight:600;font-size:13px}
[data-testid="stMetricValue"]{color:#e6f8f2;font-family:'Space Grotesk',sans-serif;font-weight:700}
[data-testid="stFileUploader"],[data-testid="stTextArea"]{border-radius:13px}
.stButton > button[kind="primary"],.stDownloadButton button[kind="primary"]{background:#96f6df;color:#0d2434;border:0;border-radius:10px;font-weight:800;min-height:48px}
.stButton > button[kind="primary"]:hover{background:#bcffe9;color:#0d2434}
.stButton > button[kind="secondary"]{background:#17253a;border:1px solid #465b74;border-radius:10px;color:#e4ecf8}
[data-testid="stTabs"] [role="tab"]{font-weight:700}
.rule{color:#8d9fb7;font-size:12px;margin:16px 0 8px}.chip{display:inline-block;background:#182d37;border:1px solid #285d58;padding:7px 12px;border-radius:999px;color:#a5ffe3;font-weight:700;font-size:12px;margin:4px 5px 4px 0}.chip.miss{background:#31263c;border-color:#665070;color:#f5c6d1}.chip.extra{background:#262643;border-color:#4e4b8f;color:#d4c7ff}
.mini-info{color:#b3c1d5;font-size:13px;line-height:1.7}.footer-note{border-top:1px solid #34445b;padding-top:17px;margin-top:45px;color:#8197b1;font-size:12px}
@media(max-width:650px){.hero{padding:25px 22px;border-radius:17px}.hero h1{font-size:43px}.hero p{font-size:14px}[data-testid="stMainBlockContainer"]{padding:15px 17px}.brand{margin:5px 0 24px}}
</style>
'''
st.markdown(CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="brand"><span class="brand-icon">R</span><span>resume<strong>.lab</strong></span></div>', unsafe_allow_html=True)
    st.markdown('<div class="side-overline">EXPLORATION WORKSPACE / V2</div>', unsafe_allow_html=True)
    st.markdown('**Modules**')
    st.caption('Document parsing  ·  Skill mentions  ·  Evidence explorer  ·  Lexical NLP')
    st.markdown('<div class="side-card"><b>Privacy-first demo</b><p>No external AI API, database writes or candidate scoring. Uploaded documents are processed temporarily on the running server.</p></div>', unsafe_allow_html=True)
    st.markdown('**Supported formats**')
    st.caption('PDF · DOCX · TXT  /  5 MB max  /  20 PDF pages')
    st.markdown('**Method**')
    st.caption('Skill-alias matching and TF-IDF overlapping terms. Results require human verification.')
    st.divider()
    st.caption('Portfolio research prototype · Built with Python, Streamlit and scikit-learn')

st.markdown('''<section class="hero"><div class="kicker">RESEARCH INTELLIGENCE / RESUME ANALYSIS / 2026</div><h1>See the evidence.<br><span>Not a hiring verdict.</span></h1><p>Explore resume text alongside a job description, find explicit skills mentioned in both documents, and inspect source evidence. A transparent NLP workspace designed for human review — not automatic candidate selection.</p><div class="sub">PYTHON  /  STREAMLIT  /  SCIKIT-LEARN  /  DOCUMENT PARSING</div></section>''', unsafe_allow_html=True)
st.markdown('<div class="warn"><strong>Demonstration only.</strong> This is not a validated ATS score, applicant ranking or hiring decision system. Please use fictional resumes in the public demo. Uploads are handled by the cloud hosting service and redaction is not guaranteed to remove all personal details.</div>',unsafe_allow_html=True)

st.subheader('01 / Input documents')
mode = st.radio('Resume source', ['Fictional sample', 'Upload your own PDF / DOCX / TXT'], horizontal=True,
                help='The fictional sample contains no real applicant information.')
left,right = st.columns([1,1],gap='large')
with left:
    st.markdown('**Resume / project experience**')
    if mode == 'Fictional sample':
        st.text_area('Sample resume', value=SAMPLE_RESUME, height=260, disabled=True, label_visibility='collapsed')
        resume_content = SAMPLE_RESUME
    else:
        uploaded = st.file_uploader('Choose a resume', type=['pdf','docx','txt'], accept_multiple_files=False,
                                    help='Files are read in memory. Avoid uploading real personal information to public apps.')
        resume_content = None
        if uploaded is not None:
            try:
                resume_content = extract_text(uploaded.getvalue(), uploaded.name)
                st.success(f'Extracted {len(resume_content):,} characters from document. No file saved by this app.')
            except ValueError as exc:
                st.error(str(exc))
with right:
    st.markdown('**Job description / role requirements**')
    jd = st.text_area('Job description', value=SAMPLE_JD, height=260, label_visibility='collapsed',
                      placeholder='Paste requirements here…', max_chars=50_000)

current_fingerprint = hashlib.sha256(((resume_content or '') + '\0' + jd).encode('utf-8')).hexdigest()
analyze_pressed = st.button('Analyze text evidence  →', type='primary', use_container_width=True)
if 'analysis' not in st.session_state:
    st.session_state.analysis = analyze(SAMPLE_RESUME,SAMPLE_JD)
    st.session_state.analysis_mode = 'Fictional sample'
    st.session_state.analysis_fingerprint = current_fingerprint
if analyze_pressed:
    if resume_content is None:
        st.warning('Upload a supported document first.')
    else:
        try:
            st.session_state.analysis = analyze(resume_content,jd)
            st.session_state.analysis_mode = mode
            st.session_state.analysis_fingerprint = current_fingerprint
        except ValueError as exc:
            st.error(str(exc))
            st.session_state.analysis = None
if mode != st.session_state.get('analysis_mode') or current_fingerprint != st.session_state.get('analysis_fingerprint'):
    st.info('Your input document or job description changed. Click Analyze to refresh the report.')
    result = None
else:
    result = st.session_state.get('analysis')

if result is not None:
    st.divider()
    st.subheader('02 / Evidence snapshot')
    a,b,c,d = st.columns(4)
    a.metric('Job skill mentions',len(result['job_skills']))
    b.metric('Mentioned in both',len(result['mentioned_in_both']))
    c.metric('Not found in resume',len(result['mentioned_only_in_job']))
    d.metric('Extra resume mentions',len(result['mentioned_only_in_resume']))
    st.caption('Counts of explicit dictionary-based skill mentions, not competence, scores, qualifications or suitability.')
    overview,evidence,lexical,method = st.tabs(['Overview','Source evidence','NLP terms','Methodology'])
    with overview:
        c1,c2=st.columns(2,gap='large')
        with c1:
            st.markdown('#### Skills mentioned in both')
            if result['mentioned_in_both']:
                st.markdown(''.join('<span class="chip">'+html.escape(s)+'</span>' for s in result['mentioned_in_both']),unsafe_allow_html=True)
            else: st.info('No recognized skill names appear in both documents.')
            st.markdown('#### Job skills not explicitly found in resume')
            if result['mentioned_only_in_job']:
                st.markdown(''.join('<span class="chip miss">'+html.escape(s)+'</span>' for s in result['mentioned_only_in_job']),unsafe_allow_html=True)
            else: st.caption('No missing recognized keywords in the supplied description.')
        with c2:
            st.markdown('#### Additional resume skill mentions')
            if result['mentioned_only_in_resume']:
                st.markdown(''.join('<span class="chip extra">'+html.escape(s)+'</span>' for s in result['mentioned_only_in_resume']),unsafe_allow_html=True)
            else: st.caption('No additional recognized keywords detected.')
            fig = go.Figure(go.Bar(x=['Both','Only in job','Only in resume'],
                                 y=[len(result['mentioned_in_both']),len(result['mentioned_only_in_job']),len(result['mentioned_only_in_resume'])],
                                 marker_color=['#8ef7d9','#f1a6c8','#b7a7ff'],textposition='outside'))
            fig.update_layout(height=300,margin=dict(l=5,r=5,t=18,b=0),paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)',font_color='#bed2e2',showlegend=False,
                              yaxis=dict(gridcolor='#28374d',rangemode='tozero',title=None),xaxis=dict(title=None))
            st.plotly_chart(fig,use_container_width=True)
    with evidence:
        st.markdown('#### Where the terms appeared')
        st.caption('Excerpts have best-effort email/phone/URL redaction. Context can be misleading or negated; verify manually.')
        if result['evidence']:
            st.dataframe(pd.DataFrame(result['evidence']).rename(columns={
                'skill':'Skill keyword','resume_excerpt':'Resume evidence','job_excerpt':'Job description evidence'}),
                hide_index=True,use_container_width=True)
        else: st.info('No shared recognized skill mentions to display.')
        with st.expander('Resume text excerpt (redacted, up to 700 characters)'):
            st.text(result['resume_excerpt_redacted'])
    with lexical:
        st.markdown('#### Shared vocabulary (TF-IDF)')
        st.caption('Words/phrases seen in both documents, sorted by combined TF-IDF weight. This is lexical comparison, not a semantic understanding, prediction or fit score.')
        if result['overlapping_terms']:
            st.markdown(''.join('<span class="chip extra">'+html.escape(s)+'</span>' for s in result['overlapping_terms']),unsafe_allow_html=True)
        else: st.info('No significant shared terms found by the current vocabulary settings.')
    with method:
        st.markdown('#### How this demo works')
        st.markdown('1. Extract plain text from PDF, DOCX or TXT (no OCR).\n2. Detect mentions from a fixed transparent skill/alias vocabulary.\n3. Compare the two skill sets and display surrounding text.\n4. Compute TF-IDF terms shared by both texts for lexical exploration.\n5. Export a reduced JSON report — no original resume file or full raw text.')
        st.markdown('#### Important limitations')
        for note in result['limitations']: st.markdown('- '+note)
        st.info('Human reviewers should check actual experience, evidence, context, accessibility and relevance. Absence of a keyword is not proof of missing ability.')
    st.markdown('### Export analysis')
    st.download_button('Download redacted JSON report',data=json.dumps(result,indent=2,ensure_ascii=False),
                       file_name='resume_text_evidence_demo.json',mime='application/json',use_container_width=True)

st.markdown('<div class="footer-note">© 2026 · Muhammed Ansar · Resume Evidence Explorer V2  ·  Fictional default data  ·  Human review required  ·  No automated hiring decisions</div>',unsafe_allow_html=True)
