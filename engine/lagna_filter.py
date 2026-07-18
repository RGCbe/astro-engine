"""Drop corpus lines scoped to a different ascendant than the native chart."""
from __future__ import annotations

import re

RASIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

_SIGN_ALT = {
    "mesha": "Aries", "mesh": "Aries", "vrishabha": "Taurus", "rishaba": "Taurus",
    "mithuna": "Gemini", "mithun": "Gemini", "karka": "Cancer", "kataka": "Cancer",
    "simha": "Leo", "kanya": "Virgo", "tula": "Libra", "thula": "Libra",
    "vrischika": "Scorpio", "viruchigam": "Scorpio", "dhanu": "Sagittarius",
    "dhanusu": "Sagittarius", "makara": "Capricorn", "kumbha": "Aquarius",
    "kumbam": "Aquarius", "meena": "Pisces", "meenam": "Pisces",
}

_LAGNA_SCOPED = re.compile(
    r"(?:\bfor\b|\bwhen\b|\bif\b|\bin case of\b|\bapplicable to\b|\bwith\b)\s+"
    r"(?:a\s+)?(?P<sign>[A-Za-z]+)\s+"
    r"(?:lagna|ascendant|ascendent|lagnam|native|horoscope)\b",
    re.IGNORECASE,
)
_SIGN_LAGNA = re.compile(
    r"\b(?P<sign>Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpio|"
    r"Sagittarius|Capricorn|Aquarius|Pisces)\s+"
    r"(?:lagna|ascendant|ascendent|lagnam)\b",
    re.IGNORECASE,
)
_SANSKRIT_LAGNA = re.compile(
    r"\b(?P<sign>mesha|mesh|vrishabha|rishaba|mithuna|mithun|karka|kataka|"
    r"simha|kanya|tula|thula|vrischika|viruchigam|dhanu|dhanusu|makara|"
    r"kumbha|kumbam|meena|meenam)\s+"
    r"(?:lagna|ascendant|ascendent|lagnam)\b",
    re.IGNORECASE,
)
_BORN_IN_SIGN = re.compile(
    r"\bborn\s+in\s+(?P<sign>[A-Za-z]+)\b",
    re.IGNORECASE,
)


def _norm_sign(token: str) -> str | None:
    t = token.strip().title()
    if t in RASIS:
        return t
    low = token.strip().lower()
    return _SIGN_ALT.get(low)


def lagna_signs_mentioned(text: str) -> set[str]:
    found: set[str] = set()
    for m in _LAGNA_SCOPED.finditer(text):
        s = _norm_sign(m.group("sign"))
        if s:
            found.add(s)
    for m in _SIGN_LAGNA.finditer(text):
        s = _norm_sign(m.group("sign"))
        if s:
            found.add(s)
    for m in _SANSKRIT_LAGNA.finditer(text):
        s = _norm_sign(m.group("sign"))
        if s:
            found.add(s)
    for m in _BORN_IN_SIGN.finditer(text):
        s = _norm_sign(m.group("sign"))
        if s:
            found.add(s)
    return found


def rule_applies_to_lagna(text: str, lagna_sign: str | None) -> bool:
    """True if rule is universal or explicitly for this lagna; False if for another lagna only."""
    if not lagna_sign:
        return True
    mentioned = lagna_signs_mentioned(text)
    if not mentioned:
        return True
    return lagna_sign in mentioned
