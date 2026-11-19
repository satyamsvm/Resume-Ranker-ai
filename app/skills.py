"""Step 3 - skill extraction using a transparent, editable taxonomy.

data/skills.json maps a canonical skill name to its aliases. Add your own
skills there (no code change needed).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

SKILLS_FILE = Path(__file__).resolve().parent.parent / "data" / "skills.json"


@lru_cache(maxsize=1)
def _patterns() -> dict[str, re.Pattern]:
    with open(SKILLS_FILE, encoding="utf-8") as fh:
        taxonomy = json.load(fh)
    compiled = {}
    for canonical, aliases in taxonomy.items():
        names = sorted({canonical, *aliases}, key=len, reverse=True)
        alt = "|".join(re.escape(n) for n in names)
        # not preceded/followed by letters/digits/+/#  -> "java" != "javascript"
        compiled[canonical] = re.compile(
            rf"(?<![a-z0-9+#]){'(?:' + alt + ')'}(?![a-z0-9+#])", re.IGNORECASE
        )
    return compiled


def extract_skills(text: str) -> list[str]:
    """Return canonical skill names found in `text` (sorted)."""
    found = [name for name, pat in _patterns().items() if pat.search(text)]
    return sorted(found)
