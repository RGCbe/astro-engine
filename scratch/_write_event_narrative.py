# -*- coding: utf-8 -*-
"""One-shot writer for event_narrative.py with clean unicode escapes."""
from pathlib import Path

BODY = r'''
SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

SOURCE_TA = {
    "salary": "\u0baa\u0b9f\u0bcd\u0b9a\u0bbf / \u0b89\u0baf\u0bb0\u0bcd\u0bb5\u0bc1",
    "business": "\u0bb5\u0ba3\u0bbf\u0b95 / \u0ba4\u0bca\u0bb4\u0bbf\u0bb2\u0bcd",
    "land": "\u0ba8\u0bbf\u0bb2\u0bae\u0bcd / \u0b9a\u0bca\u0ba4\u0bcd\u0ba4\u0bc1",
    "rental": "\u0bb5\u0bbe\u0b9f\u0b95\u0bc8 \u0bb5\u0bb0\u0bc1\u0bae\u0bbe\u0ba9\u0bae\u0bcd",
    "inheritance": "\u0baa\u0bbe\u0bb0\u0b9a\u0bc1 / \u0b95\u0bc1\u0b9f\u0bc1\u0bae\u0bcd\u0baa\u0bae\u0bcd",
    "spouse": "\u0b9a\u0bc1\u0ba4\u0bbf / \u0baa\u0ba4\u0bcd\u0ba9\u0bbf",
    "network": "\u0b8e\u0ba4\u0bbf\u0bb0\u0bcd / \u0b95\u0bc1\u0bb1\u0bbf\u0baa\u0bcd\u0baa\u0bc1",
    "speculation": "\u0b9a\u0bc1\u0baa\u0bcd\u0baa\u0bc1\u0bb1\u0bc1\u0bb5\u0bc1 / \u0baa\u0b99\u0bcd\u0b95\u0bc1",
    "father": "\u0ba4\u0ba8\u0bcd\u0ba4\u0bc8 / \u0b95\u0bc1\u0bb0\u0bc1",
    "grace": "\u0b95\u0bc1\u0bb0\u0bc1 \u0b85\u0ba9\u0bc1\u0b95\u0bcd\u0b95\u0bbf\u0bb0\u0b95\u0bae\u0bcd",
    "education": "\u0bb5\u0bbf\u0ba4\u0bcd\u0ba4\u0bbf\u0baf\u0bbe\u0b9a\u0bae\u0bcd",
    "foreign": "\u0bb5\u0bc6\u0bb3\u0bbf\u0ba8\u0bbe\u0b9f\u0bc1",
}

MECHANISM_TA = {
    "legal": "\u0b9a\u0b9f\u0bcd\u0b9f\u0bc1 / \u0bb5\u0bb0\u0bbf \u0bb5\u0bb4\u0b95\u0bcd\u0b95\u0bc1",
    "medical": "\u0b86\u0bb0\u0bcb\u0b95 \u0b9a\u0bc6\u0bb2\u0bb5\u0bc1",
    "job_loss": "\u0bb\u0bc7\u0bb2\u0bc8 \u0b87\u0bb4\u0baa\u0bcd\u0baa\u0bc1",
    "partnership": "\u0b95\u0bc2\u0b9f\u0bcd\u0b9f\u0bc1 \u0b89\u0b9f\u0bc8\u0bb5\u0bc1",
    "fraud": "\u0b8e\u0bb0\u0bbf / \u0bb0\u0bbe\u0b95\u0bc1",
    "family_expense": "\u0b95\u0bc1\u0b9f\u0bc1\u0bae\u0bcd\u0baa \u0b9a\u0bc6\u0bb2\u0bb5\u0bc1",
    "market": "\u0b9a\u0ba8\u0bcd\u0ba4\u0bc8 \u0b87\u0bb4\u0baa\u0bcd\u0baa\u0bc1",
    "delay": "\u0b9a\u0ba9\u0bbf \u0ba4\u0bbe\u0bae\u0ba4\u0bae\u0bcd",
    "sudden": "8\u0bb5\u0ba4\u0bc1 \u0ba4\u0bbf\u0b9f\u0bc0\u0bb0\u0bcd \u0b87\u0bb4\u0baa\u0bcd\u0baa\u0bc1",
    "abroad_drain": "12\u0bb5\u0ba4\u0bc1 \u0bb5\u0bc6\u0bb3\u0bbf\u0ba8\u0bbe\u0b9f\u0bc1 \u0b9a\u0bc6\u0bb2\u0bb5\u0bc1",
}

DISCLAIMER_EN = "Mechanical inference, not guaranteed."
DISCLAIMER_TA = "\u0b95\u0ba3\u0bbf\u0ba4\u0bcd\u0ba4 \u0b85\u0ba9\u0bc1\u0bae\u0bbe\u0ba9\u0bae\u0bcd \u2014 \u0b89???? \u0b87????."
'''

# Read the rest from existing file logic - append main functions
Path(r"F:\astro\engine\event_narrative.py").write_text(
    "# -*- coding: utf-8 -*-\n"
    '"""Infer wealth/career/marriage source and loss mechanism from chart + why[] + dasha."""\n'
    "from __future__ import annotations\n\nimport re\nfrom typing import Any\n\n"
    + BODY.encode("utf-8").decode("unicode_escape") if False else "",
    encoding="utf-8",
)
print("stub")
