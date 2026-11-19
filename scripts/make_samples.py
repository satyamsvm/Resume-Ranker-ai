"""Turn some of the sample .txt resumes into real PDF / DOCX files for demos.
Run:  python scripts/make_samples.py
"""
from pathlib import Path

from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent / "data" / "sample_resumes"


def to_pdf(txt: Path):
    c = canvas.Canvas(str(txt.with_suffix(".pdf")), pagesize=A4)
    y = A4[1] - 20 * mm
    for line in txt.read_text(encoding="utf-8").splitlines():
        c.setFont("Helvetica-Bold" if line.isupper() and line.strip() else "Helvetica", 10)
        c.drawString(18 * mm, y, line[:110])
        y -= 5.5 * mm
    c.save()


def to_docx(txt: Path):
    doc = Document()
    for line in txt.read_text(encoding="utf-8").splitlines():
        doc.add_paragraph(line)
    doc.save(str(txt.with_suffix(".docx")))


if __name__ == "__main__":
    to_pdf(ROOT / "aarav_mehta.txt")
    to_pdf(ROOT / "rohan_verma.txt")
    to_pdf(ROOT / "ananya_rao.txt")
    to_docx(ROOT / "sneha_kulkarni.txt")
    # keep the PDF/DOCX versions only for those, remove duplicate txt
    for n in ("aarav_mehta", "rohan_verma", "ananya_rao", "sneha_kulkarni"):
        (ROOT / f"{n}.txt").unlink()
    print("Sample PDF/DOCX resumes created in", ROOT)
