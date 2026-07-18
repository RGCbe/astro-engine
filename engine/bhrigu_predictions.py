"""
Bhrigu-nadi-style point predictions.

Surfaces verbatim planet-in-house outcome verses from the deep extraction
of Bhrigu_Samhita (2,112 rules). Given a chart, for each of the 9 grahas
look up rules indexed at its actual house from the lagna, and return the
top-N most relevant verbatim outcome statements.

This is read-only retrieval — no scoring. The verbatim text IS the
prediction. Per the truth-only directive: do not paraphrase.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")


@dataclass
class BhriguPrediction:
    planet: str
    house: int
    text: str
    book: str
    verse_id: str
    rule_type: str       # rule | yoga | aphorism | commentary | …

    def cite(self) -> str:
        if self.verse_id:
            return f"{self.book} {self.verse_id}"
        return self.book


import re as _re


def _detect_primary_pair(text: str) -> tuple[str, int] | None:
    """Detect the PRIMARY (planet, house) pair the rule actually describes.

    Looks at the first ~250 chars for a pattern like
        '{planet} (in|situated in|sits in) (the)? {N}th house'
    Returns the first match, or None if ambiguous.
    """
    head = text[:250].lower()
    # Map of planet aliases → canonical name
    PLANET_ALIASES = {
        "Sun":     ["sun"],
        "Moon":    ["moon"],
        "Mars":    ["mars", "mangal"],
        "Mercury": ["mercury", "budha"],
        "Jupiter": ["jupiter", "guru", "brihaspati"],
        "Venus":   ["venus", "shukra"],
        "Saturn":  ["saturn", "shani"],
        "Rahu":    ["rahu"],
        "Ketu":    ["ketu"],
    }
    HOUSE_NUMS = {
        "1st": 1, "first": 1, "ascendant": 1, "lagna": 1,
        "2nd": 2, "second": 2,
        "3rd": 3, "third": 3,
        "4th": 4, "fourth": 4,
        "5th": 5, "fifth": 5,
        "6th": 6, "sixth": 6,
        "7th": 7, "seventh": 7,
        "8th": 8, "eighth": 8,
        "9th": 9, "ninth": 9,
        "10th": 10, "tenth": 10,
        "11th": 11, "eleventh": 11,
        "12th": 12, "twelfth": 12,
    }

    # Try to find the leading {planet} + {house} pattern
    for canon, aliases in PLANET_ALIASES.items():
        for alias in aliases:
            # planet token, then up to 80 chars of intervening words, then house ordinal
            pat = (rf"\b{alias}\b[^.]{{0,80}}?"
                   r"\b(1st|first|2nd|second|3rd|third|4th|fourth|5th|fifth|"
                   r"6th|sixth|7th|seventh|8th|eighth|9th|ninth|10th|tenth|"
                   r"11th|eleventh|12th|twelfth)\b\s*(?:house|bhava)?")
            m = _re.search(pat, head)
            if m:
                return (canon, HOUSE_NUMS[m.group(1)])
    return None


@lru_cache(maxsize=1)
def _build_index() -> dict[tuple[str, int], list[BhriguPrediction]]:
    """(planet, house) → list of verbatim BhriguPrediction objects.

    Strict indexing: only puts a rule under (planet, house) if the rule
    text actually opens with that placement. Falls back to involves_*
    cross-product only when no primary pair is detected (treats those
    as 'context' not 'subject' rules).
    """
    from .verse_locator import _load_all_deep
    idx: dict[tuple[str, int], list[BhriguPrediction]] = {}
    for r in _load_all_deep():
        if r.get("_book") != "Bhrigu_Samhita":
            continue
        text = (r.get("english_translation") or r.get("original_text") or "").strip()
        if len(text) < 20:
            continue
        rule_type = (r.get("rule_type") or r.get("type") or "rule")
        primary = _detect_primary_pair(text)
        if primary:
            # Index only under the detected primary pair (precise)
            p, h = primary
            idx.setdefault((p, h), []).append(BhriguPrediction(
                planet=p, house=h, text=text,
                book=r.get("_book", "Bhrigu_Samhita"),
                verse_id=r.get("verse_id") or "",
                rule_type=rule_type,
            ))
        # else: skip — don't pollute the index with cross-product matches
    return idx


ASCENDANT_TOKENS = {
    "Aries":      ("aries ascendant", "mesha", "मेष"),
    "Taurus":     ("taurus ascendant", "vrishabha", "वृषभ"),
    "Gemini":     ("gemini ascendant", "mithuna", "मिथुन"),
    "Cancer":     ("cancer ascendant", "karka", "कर्क"),
    "Leo":        ("leo ascendant", "simha", "सिंह"),
    "Virgo":      ("virgo ascendant", "kanya", "कन्या"),
    "Libra":      ("libra ascendant", "tula", "तुला"),
    "Scorpio":    ("scorpio ascendant", "vrischika", "वृश्चिक"),
    "Sagittarius": ("sagittarius ascendant", "dhanu", "धनु"),
    "Capricorn":  ("capricorn ascendant", "makara", "मकर"),
    "Aquarius":   ("aquarius ascendant", "kumbha", "कुम्भ"),
    "Pisces":     ("pisces ascendant", "meena", "मीन"),
}

_ALL_LAGNA_TOKENS = [t for tokens in ASCENDANT_TOKENS.values() for t in tokens]


def _matches_ascendant(text: str, lagna_sign: str) -> bool | None:
    """Returns True if text mentions THIS ascendant, False if it mentions
    a DIFFERENT ascendant, None if it mentions no ascendant context."""
    txt = text.lower()
    own_tokens = ASCENDANT_TOKENS.get(lagna_sign, ())
    if any(t in txt for t in own_tokens):
        return True
    # Does it mention some other ascendant?
    if any(t in txt for t in _ALL_LAGNA_TOKENS):
        return False
    return None


HOUSE_ORDINALS = {
    1: ["1st house", "ascendant", "lagna", "first house"],
    2: ["2nd house", "second house"],
    3: ["3rd house", "third house"],
    4: ["4th house", "fourth house"],
    5: ["5th house", "fifth house"],
    6: ["6th house", "sixth house"],
    7: ["7th house", "seventh house"],
    8: ["8th house", "eighth house"],
    9: ["9th house", "ninth house"],
    10: ["10th house", "tenth house"],
    11: ["11th house", "eleventh house"],
    12: ["12th house", "twelfth house"],
}


def _text_states_planet_in_house(text: str, planet: str, house: int) -> bool:
    """Does the rule text actually claim '{planet} in the {house}th house'?
    This filters out rules that were indexed under (planet, house) due to
    cross-product but actually describe a different placement."""
    lo = text.lower()
    if planet.lower() not in lo:
        return False
    if not any(o in lo for o in HOUSE_ORDINALS.get(house, [])):
        return False
    return True


def predictions_for(planet: str, house: int, max_results: int = 5,
                    lagna_sign: str | None = None
                    ) -> list[BhriguPrediction]:
    """Verbatim Bhrigu predictions for a (planet, house) cell.

    Filters:
        1. Drop rules whose text explicitly mentions a *different* ascendant.
        2. Prefer rules whose text actually states '{planet} in {house}th'.
    """
    pool = _build_index().get((planet, house), [])
    if lagna_sign:
        pool = [r for r in pool if _matches_ascendant(r.text, lagna_sign) is not False]
    pool = sorted(
        pool,
        key=lambda p: (
            # 1st: explicit match for our ascendant
            0 if (lagna_sign and _matches_ascendant(p.text, lagna_sign) is True) else 1,
            # 2nd: text actually states this planet-in-this-house
            0 if _text_states_planet_in_house(p.text, planet, house) else 1,
            # 3rd: has a verse_id citation
            0 if p.verse_id else 1,
            # 4th: prefer rule/aphorism/yoga types
            0 if p.rule_type in ("yoga", "rule", "aphorism") else 1,
            # 5th: longer text = more detail
            -len(p.text),
        ),
    )
    return pool[:max_results]


def predictions_for_chart(chart, max_per_planet: int = 3
                          ) -> list[dict]:
    """For each graha in the chart, surface verbatim predictions for its
    actual house from the lagna — filtered to this chart's ascendant."""
    from .yogas_extended import _planet_house
    SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    lagna_sign = SIGNS[int(chart.lagna_lon // 30)]
    out = []
    for p in PLANETS:
        if chart.positions.get(p) is None:
            continue
        h = _planet_house(chart, p)
        rules = predictions_for(p, h, max_results=max_per_planet,
                                 lagna_sign=lagna_sign)
        if rules:
            out.append({
                "planet": p,
                "house": h,
                "predictions": [
                    {
                        "text": r.text,
                        "citation": r.cite(),
                        "rule_type": r.rule_type,
                    }
                    for r in rules
                ],
            })
    return out


def stats() -> dict:
    idx = _build_index()
    counts = {f"{p}-H{h}": len(v) for (p, h), v in idx.items()}
    return {
        "total_rules": sum(len(v) for v in idx.values()),
        "distinct_cells": len(idx),
        "top_cells": sorted(counts.items(), key=lambda x: -x[1])[:15],
    }
