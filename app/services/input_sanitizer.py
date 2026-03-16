from __future__ import annotations

import re


BLOCKLIST_PATTERNS = [
    r"ignore\s+all\s+previous\s+instructions",
    r"ignore\s+previous\s+instructions",
    r"disregard\s+the\s+above",
    r"reveal\s+the\s+system\s+prompt",
    r"show\s+the\s+hidden\s+prompt",
    r"developer\s+mode",
    r"dan\s+mode",
    r"pretend\s+to\s+be",
]


def sanitize_idea_text(value: str) -> str:
    cleaned = value.strip()
    cleaned = re.sub(r"[\x00-\x1F\x7F]", " ", cleaned)
    cleaned = cleaned.replace("<", "＜").replace(">", "＞")
    cleaned = cleaned.replace("[", "［").replace("]", "］")
    for pattern in BLOCKLIST_PATTERNS:
        cleaned = re.sub(pattern, "[filtered]", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
