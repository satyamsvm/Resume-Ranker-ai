"""Step 1 - get plain text out of PDF / DOCX / TXT uploads."""
from __future__ import annotations

import io
import os

import pdfplumber
from docx import Document


class ExtractionError(Exception):
    """Raised when a file cannot be read."""


def _from_pdf(data: bytes) -> str:
    parts = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts)


def _from_docx(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    lines = [p.text for p in doc.paragraphs]
    for table in doc.tables:                      # resumes often use tables
        for row in table.rows:
            lines.append(" ".join(cell.text for cell in row.cells))
    return "\n".join(lines)


def _from_txt(data: bytes) -> str:
    for enc in ("utf-8", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return ""


def extract_text(filename: str, data: bytes) -> str:
    """Return the text of an uploaded file, based on its extension."""
    ext = os.path.splitext(filename)[1].lower()
    try:
        if ext == ".pdf":
            text = _from_pdf(data)
        elif ext == ".docx":
            text = _from_docx(data)
        elif ext == ".txt":
            text = _from_txt(data)
        else:
            raise ExtractionError(f"Unsupported file type: {ext or 'unknown'}")
    except ExtractionError:
        raise
    except Exception as exc:  # corrupt / encrypted files
        raise ExtractionError(f"Could not read {filename}: {exc}") from exc

    text = text.strip()
    if len(text) < 30:
        raise ExtractionError(
            f"{filename}: no readable text found (scanned image PDF? try OCR first)."
        )
    return text
