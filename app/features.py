"""Step 4 - structured features: contact info, experience years, education."""
from __future__ import annotations

import re
from datetime import date

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3,5}\)?[\s-]?)\d{3,5}[\s-]?\d{3,5}")

MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec"
_RANGE_RE = re.compile(
    rf"(?:(?:{MONTHS})[a-z]*\.?\s+)?((?:19|20)\d{{2}})\s*(?:-|–|—|to)\s*"
    rf"(?:(?:{MONTHS})[a-z]*\.?\s+)?((?:19|20)\d{{2}}|present|current|now|till date)",
    re.IGNORECASE,
)
_YEARS_RE = re.compile(r"(\d{1,2})(?:\.\d)?\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE)

EDU_LEVELS = [  # (level, regex) - checked from highest to lowest
    (4, r"\bph\.?d\b|\bdoctorate\b"),
    (3, r"\bm\.?\s?tech\b|\bm\.?\s?sc\b|\bm\.?\s?e\b(?=\.|\s|,)|\bmaster'?s?\b|\bmba\b|\bm\.?\s?c\.?\s?a\b"),
    (2, r"\bb\.?\s?tech\b|\bb\.?\s?e\b(?=\.|\s|,)|\bb\.?\s?sc\b|\bbachelor'?s?\b|\bb\.?\s?c\.?\s?a\b|\bb\.?\s?com\b|\bundergraduate\b"),
    (1, r"\bdiploma\b|\bassociate degree\b"),
]
EDU_NAMES = {0: "Not found", 1: "Diploma", 2: "Bachelor's", 3: "Master's", 4: "PhD"}


def extract_email(text: str) -> str:
    m = EMAIL_RE.search(text)
    return m.group(0) if m else ""


def extract_phone(text: str) -> str:
    for m in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", m.group(0))
        if 10 <= len(digits) <= 13:
            return m.group(0).strip()
    return ""


def guess_name(text: str, fallback: str) -> str:
    """Resumes usually start with the candidate name."""
    for line in text.splitlines()[:5]:
        line = line.strip()
        if not line or "@" in line or any(c.isdigit() for c in line):
            continue
        words = line.split()
        if 1 < len(words) <= 4 and all(w[0].isalpha() for w in words):
            return line.title() if line.isupper() else line
    return fallback


def estimate_experience_years(text: str, today: date | None = None) -> float:
    """Max of (explicit 'N years') and (sum of non-overlapping date ranges)."""
    today = today or date.today()
    explicit = [int(m.group(1)) for m in _YEARS_RE.finditer(text) if int(m.group(1)) <= 40]

    spans = []
    for m in _RANGE_RE.finditer(text):
        start = int(m.group(1))
        end_raw = m.group(2).lower()
        end = today.year if end_raw[0].isalpha() else int(end_raw)
        if 1970 <= start <= end <= today.year:
            spans.append((start, end))
    spans.sort()
    total, cur_end = 0, None
    for s, e in spans:                       # merge overlaps
        if cur_end is None or s > cur_end:
            total += e - s
            cur_end = e
        elif e > cur_end:
            total += e - cur_end
            cur_end = e

    return float(max(max(explicit, default=0), total))


def required_years(jd_text: str) -> float:
    vals = [int(m.group(1)) for m in _YEARS_RE.finditer(jd_text) if int(m.group(1)) <= 25]
    return float(min(vals)) if vals else 0.0     # lowest number = the minimum asked


def education_level(text: str) -> int:
    low = text.lower()
    for level, pattern in EDU_LEVELS:
        if re.search(pattern, low):
            return level
    return 0
