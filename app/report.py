"""Step 7 - downloadable HR reports (CSV + PDF)."""
from __future__ import annotations

import io

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape


def _csv_safe(value):
    """Stop spreadsheet formula injection from malicious resume text."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
        return "'" + value
    return value


def to_csv(candidates: list[dict]) -> bytes:
    rows = [{
        "Rank": c["rank"], "Name": c["name"], "Score (%)": c["score"],
        "Email": c["email"], "Phone": c["phone"], "File": c["filename"],
        "Experience (yrs)": c["experience_years"], "Education": c["education"],
        "Skill match (%)": round(c["skill_score"] * 100),
        "Matched skills": ", ".join(c["matched_skills"]),
        "Missing skills": ", ".join(c["missing_skills"]),
    } for c in candidates]
    df = pd.DataFrame(rows).map(_csv_safe)
    return df.to_csv(index=False).encode("utf-8-sig")


def to_pdf(candidates: list[dict], job_title: str, jd: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=14*mm,
                            rightMargin=14*mm, topMargin=14*mm, bottomMargin=14*mm,
                            title="Resume Ranking Report")
    styles = getSampleStyleSheet()
    small = styles["BodyText"].clone("small")
    small.fontSize, small.leading = 8, 10

    story = [
        Paragraph("Resume Ranking Report", styles["Title"]),
        Paragraph(f"<b>Role:</b> {escape(job_title or 'Not specified')}", styles["BodyText"]),
        Paragraph(f"<b>Skills required:</b> {escape(', '.join(jd['skills']) or '-')}", styles["BodyText"]),
        Spacer(1, 6 * mm),
    ]
    data = [["#", "Candidate", "Score", "Exp (yrs)", "Education", "Matched skills", "Missing skills"]]
    for c in candidates:
        data.append([
            c["rank"],
            Paragraph(escape(f"{c['name']}\n{c['email']}").replace("\n", "<br/>"), small),
            f"{c['score']}%", f"{c['experience_years']:g}", c["education"],
            Paragraph(escape(", ".join(c["matched_skills"]) or "-"), small),
            Paragraph(escape(", ".join(c["missing_skills"]) or "-"), small),
        ])
    table = Table(data, repeatRows=1,
                  colWidths=[10*mm, 52*mm, 18*mm, 20*mm, 24*mm, 70*mm, 70*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2430")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F4F7")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#C9D1D9")),
    ]))
    story.append(table)
    doc.build(story)
    return buf.getvalue()
