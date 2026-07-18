"""
KP (Krishnamurti Paddhati) sub-lord-driven verbatim predictions.

Surfaces verbatim rules from the deep extraction of KP_Reader_3_Predictive
(2,560 rules). Two retrieval modes:

    1. House-based:  for any house 1..12, return the verbatim KP rules
       categorised under that house's primary domain (career=10, wealth=2,
       marriage=7, children=5, etc.).

    2. Sub-lord-based: given a planet's KP sub_lord, surface rules
       mentioning that sub-lord by name. Used for cuspal sub-lord
       interpretation in horary and natal KP.

This module provides only retrieval. Existing engine.kp_sublord computes
the actual sub_lord per planet — this layer enriches that with classical
prose.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


# House → primary categories used by the deep-extracted KP corpus
HOUSE_TO_CATEGORIES = {
    1:  ("personality", "health"),
    2:  ("wealth",),
    3:  ("travel",),                 # short journeys / siblings
    4:  ("home", "education"),       # mother / property / vehicles
    5:  ("children", "education"),
    6:  ("disease", "health", "career"),  # service / debts / enemies
    7:  ("marriage",),
    8:  ("longevity", "death", "karmic"),
    9:  ("spiritual", "karmic"),     # luck / father / dharma
    10: ("career",),
    11: ("wealth", "career"),        # gains / friends
    12: ("spiritual", "death", "karmic"),  # losses / moksha / foreign
}


@dataclass
class KPPrediction:
    text: str
    book: str
    verse_id: str
    rule_type: str
    categories: list[str]
    houses: list[str]
    planets: list[str]

    def cite(self) -> str:
        if self.verse_id:
            return f"{self.book} {self.verse_id}"
        return self.book


@lru_cache(maxsize=1)
def _all_kp_rules() -> list[KPPrediction]:
    from .verse_locator import _load_all_deep
    out: list[KPPrediction] = []
    for r in _load_all_deep():
        if r.get("_book") != "KP_Reader_3_Predictive":
            continue
        text = (r.get("english_translation") or r.get("original_text") or "").strip()
        if len(text) < 30:
            continue
        out.append(KPPrediction(
            text=text,
            book=r.get("_book", "KP_Reader_3_Predictive"),
            verse_id=r.get("verse_id") or "",
            rule_type=(r.get("rule_type") or r.get("type") or "rule"),
            categories=list(r.get("categories") or []),
            houses=[str(h) for h in (r.get("involves_houses") or [])],
            planets=list(r.get("involves_planets") or []),
        ))
    return out


def predictions_for_house(house: int, max_results: int = 5
                          ) -> list[KPPrediction]:
    """Verbatim KP rules whose categories match the given house's domain."""
    cats = HOUSE_TO_CATEGORIES.get(house, ("rule",))
    cats_lc = {c.lower() for c in cats}
    matches = [r for r in _all_kp_rules()
               if any(c in cats_lc for c in (x.lower() for x in r.categories))]
    # Prefer rules that explicitly involve that house number
    matches.sort(key=lambda r: (
        0 if str(house) in r.houses else 1,
        0 if r.verse_id else 1,
        0 if r.rule_type in ("rule", "aphorism", "yoga") else 1,
        -len(r.text),
    ))
    return matches[:max_results]


def predictions_for_planet(planet: str, max_results: int = 5
                           ) -> list[KPPrediction]:
    """Verbatim KP rules involving a planet (as Sub-lord, Star-lord, or transit)."""
    p = planet.title()
    matches = [r for r in _all_kp_rules() if p in r.planets]
    matches.sort(key=lambda r: (
        0 if r.verse_id else 1,
        0 if r.rule_type in ("rule", "aphorism") else 1,
        -len(r.text),
    ))
    return matches[:max_results]


def predictions_for_sublord(sublord_planet: str, max_results: int = 5
                            ) -> list[KPPrediction]:
    """Verbatim KP rules that mention the given planet by name in the
    context of being a sub-lord (KP cuspal interpretation)."""
    needle = sublord_planet.lower()
    matches = [r for r in _all_kp_rules()
               if needle in r.text.lower() and "sub" in r.text.lower()]
    matches.sort(key=lambda r: (0 if r.verse_id else 1, -len(r.text)))
    return matches[:max_results]


def predictions_for_chart(chart, max_per_house: int = 2) -> list[dict]:
    """For each of the 12 cusps, surface verbatim KP rules tied to its
    domain. Also tag the cusp's sub_lord (when chart has KP fields).
    """
    out = []
    cusps = getattr(chart, "kp_cusps", None) or {}
    for h in range(1, 13):
        sub_lord = ""
        if cusps:
            cusp = cusps.get(h) or cusps.get(str(h))
            if isinstance(cusp, dict):
                sub_lord = cusp.get("sub_lord", "") or ""
        rules = predictions_for_house(h, max_results=max_per_house)
        if rules:
            out.append({
                "house": h,
                "sub_lord": sub_lord,
                "predictions": [
                    {"text": r.text, "citation": r.cite(),
                     "rule_type": r.rule_type}
                    for r in rules
                ],
            })
    return out


def stats() -> dict:
    rules = _all_kp_rules()
    by_cat = {}
    by_type = {}
    for r in rules:
        for c in r.categories:
            by_cat[c] = by_cat.get(c, 0) + 1
        by_type[r.rule_type] = by_type.get(r.rule_type, 0) + 1
    return {
        "total": len(rules),
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])),
        "top_categories": dict(sorted(by_cat.items(),
                                       key=lambda x: -x[1])[:15]),
    }
