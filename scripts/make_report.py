"""Builds docs/Project_Report.pdf (must stay <= 2 pages). Edit NAME below."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

NAME = "YOUR NAME"
GITHUB = "github.com/YOUR-USERNAME/resume-ranker-ai"

ss = getSampleStyleSheet()
body = ParagraphStyle("b", parent=ss["BodyText"], fontSize=9.6, leading=13, alignment=TA_JUSTIFY)
h = ParagraphStyle("h", parent=ss["Heading2"], fontSize=12, spaceBefore=8, spaceAfter=3,
                   textColor=colors.HexColor("#0E6B8A"), keepWithNext=1)
title = ParagraphStyle("t", parent=ss["Title"], fontSize=18, spaceAfter=2)
sub = ParagraphStyle("s", parent=ss["BodyText"], fontSize=9.5, alignment=1, textColor=colors.HexColor("#444444"))


def bullets(items):
    return ListFlowable([ListItem(Paragraph(i, body), leftIndent=12) for i in items],
                        bulletType="bullet", start="-", leftIndent=12, bulletFontSize=8)


story = [
    Paragraph("AI-Powered Resume Ranker (ResumeRank AI)", title),
    Paragraph(f"AI/ML Internship Project Report - Elevate Labs | {NAME} | {GITHUB}", sub),
    Spacer(1, 4),

    Paragraph("1. Introduction", h),
    Paragraph(
        "Recruiters often receive hundreds of resumes for a single opening and screen them manually, which is slow, "
        "inconsistent and easy to get wrong. This project builds a web application that reads resumes in PDF, DOCX "
        "or TXT format, compares them with a job description using Natural Language Processing, and returns a ranked "
        "shortlist together with the reasons behind each score. Unlike a plain keyword counter, the system combines "
        "several signals and explains its output, so that a recruiter can trust and verify it.", body),

    Paragraph("2. Abstract", h),
    Paragraph(
        "The system extracts text from uploaded files, cleans it with spaCy (lemmatisation and stop-word removal) and "
        "converts it to TF-IDF vectors (unigrams and bigrams). A hybrid score between 0 and 100 is computed as: "
        "45% skill match + 30% TF-IDF cosine similarity + 15% experience + 10% education. Skills are detected through "
        "an editable taxonomy of about 50 skills with aliases (for example sklearn = scikit-learn); experience is "
        "estimated from date ranges and phrases such as \"4 years\"; education is detected from degree keywords. "
        "Experience is scaled by skill relevance so that, for example, a senior Java developer does not outrank a "
        "relevant fresher for a machine-learning role. The web interface (Flask) shows a score breakdown, matched and "
        "missing skills per candidate, and offers PDF and CSV reports. A JSON API, 13 automated tests, a Dockerfile "
        "and a CI workflow make the project ready to deploy.", body),

    Paragraph("3. Tools Used", h),
    Table([
        ["Area", "Tools"],
        ["Language", "Python 3.12"],
        ["NLP / ML", "spaCy, scikit-learn (TF-IDF, cosine similarity), regular expressions"],
        ["File parsing", "pdfplumber (PDF), python-docx (DOCX)"],
        ["Web / API", "Flask, Jinja2, HTML/CSS, Gunicorn"],
        ["Reports / Data", "ReportLab (PDF), pandas (CSV)"],
        ["Quality / DevOps", "unittest, GitHub Actions, Docker, Git/GitHub"],
    ], colWidths=[32 * mm, 140 * mm], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17212B")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9), ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#C9D1D9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])),

    Paragraph("4. Steps Involved in Building the Project", h),
    bullets([
        "<b>Text extraction:</b> read PDF/DOCX/TXT uploads in memory, handle corrupt or scanned files with clear errors.",
        "<b>Preprocessing:</b> remove URLs and emails, lower-case, lemmatise and drop stop-words using spaCy "
        "(with an automatic regex fallback when the model is not installed).",
        "<b>Skill extraction:</b> match canonical skills and their aliases with word-boundary regular expressions, so "
        "\"java\" is not found inside \"javascript\" and symbols such as C++ and C# work.",
        "<b>Feature extraction:</b> email, phone, candidate name, years of experience (merged non-overlapping date "
        "ranges) and highest education level.",
        "<b>Vectorisation and similarity:</b> fit TF-IDF on the job description and all resumes, then compute cosine "
        "similarity of each resume with the job description.",
        "<b>Scoring and ranking:</b> combine the four components with tunable weights (config.py), sort candidates and "
        "attach matched / missing skills as an explanation.",
        "<b>Web application:</b> Flask upload form, results page with score bars, PDF/CSV download and a JSON API; "
        "input validation, file-type and size limits and CSV-injection protection.",
        "<b>Testing and deployment:</b> unit and web tests, GitHub Actions CI, Dockerfile and render.yaml for hosting.",
    ]),

    Paragraph("5. Conclusion", h),
    Paragraph(
        "ResumeRank AI shows that combining semantic text similarity with explicit skill, experience and education "
        "signals produces rankings that are both accurate and explainable. On the six sample resumes included in the "
        "repository, the two candidates with matching ML/NLP skills ranked first and second, while an unrelated "
        "backend profile and an almost empty resume ranked low. Current limitations are the fixed skill taxonomy, no "
        "OCR for image-only PDFs and year-level experience estimation. Planned improvements are sentence-embedding "
        "similarity, OCR, a database with user accounts, an anonymised screening mode to reduce bias, and a "
        "recruiter feedback loop. The scores are designed to assist, not replace, a human hiring decision.", body),
]

doc = SimpleDocTemplate("docs/Project_Report.pdf", pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                        topMargin=14 * mm, bottomMargin=14 * mm, title="ResumeRank AI - Project Report",
                        author=NAME)
doc.build(story)
