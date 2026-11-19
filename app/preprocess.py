"""Step 2 - text cleaning.

Uses spaCy (lemmatisation + stop-word removal) when the English model is
installed. If not, it falls back to a lightweight regex pipeline so the app
still runs everywhere (CI, small free hosting tiers, etc.).
"""
from __future__ import annotations

import re
from functools import lru_cache

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

_TOKEN_RE = re.compile(r"[a-z][a-z0-9+#.]*")


@lru_cache(maxsize=1)
def _load_spacy():
    try:
        import spacy
        return spacy.load("en_core_web_sm", disable=["ner", "parser"])
    except Exception:
        return None


def backend_name() -> str:
    return "spaCy" if _load_spacy() is not None else "regex-fallback"


def _fallback_tokens(text: str) -> list[str]:
    tokens = (t.rstrip(".") for t in _TOKEN_RE.findall(text.lower()))
    return [t for t in tokens if len(t) > 1 and t not in ENGLISH_STOP_WORDS]


def clean_text(text: str) -> str:
    """Lower-case, strip URLs/emails, lemmatise, drop stop-words."""
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    nlp = _load_spacy()
    if nlp is None:
        return " ".join(_fallback_tokens(text))

    doc = nlp(text.lower()[:200_000])
    out = []
    for tok in doc:
        if tok.is_stop or tok.is_punct or tok.is_space or len(tok.text) < 2:
            continue
        lemma = tok.lemma_.strip()
        if lemma and lemma[0].isalpha():
            out.append(lemma)
    return " ".join(out)
