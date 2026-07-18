"""
Verbatim remedies surfaced from the deep-extracted classical corpus.

Whereas `engine.remedies` carries paraphrased modern wording for each
affliction, this module returns the *verse-by-verse classical text*
with book+verse_id citation so the reading layer can quote source
material directly. Per the truth-only directive: never substitute our
words for the verse when the verse is available.

Source: `engine.verse_locator._load_all_deep()` filtered to
`type == "remedy"` (30 rules across Bhrigu_Samhita, KP_Reader_3_Predictive,
Lal_Kitab_Original, Muhurtha_Chintamani, Phaladeepika, Sarvartha_Chintamani).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from functools import lru_cache


@dataclass
class VerbatimRemedy:
    book: str
    verse_id: str
    text: str
    planets: list[str]
    houses: list[int]
    categories: list[str]

    def cite(self) -> str:
        if self.verse_id:
            return f"{self.book} {self.verse_id}"
        return self.book


@lru_cache(maxsize=1)
def _all_remedies() -> list[VerbatimRemedy]:
    from .verse_locator import _load_all_deep
    out = []
    for r in _load_all_deep():
        if (r.get("rule_type") or r.get("type")) != "remedy":
            continue
        text = (r.get("english_translation") or r.get("original_text") or "").strip()
        if not text:
            continue
        out.append(VerbatimRemedy(
            book=r.get("_book", ""),
            verse_id=r.get("verse_id", "") or "",
            text=text,
            planets=list(r.get("involves_planets") or []),
            houses=list(r.get("involves_houses") or []),
            categories=list(r.get("categories") or []),
        ))
    return out


def remedies_for_planet(planet: str) -> list[VerbatimRemedy]:
    """Verbatim remedies invoking a specific planet."""
    p = planet.title()
    return [r for r in _all_remedies() if p in r.planets]


def remedies_in_category(category: str) -> list[VerbatimRemedy]:
    """Verbatim remedies tagged with a category (e.g. 'marriage', 'gem',
    'spiritual', 'karmic')."""
    c = category.lower()
    return [r for r in _all_remedies() if c in [x.lower() for x in r.categories]]


def remedies_for_affliction_code(code: str, involved_planets: list[str]) -> list[VerbatimRemedy]:
    """Surface verbatim remedies relevant to an affliction.
    Maps affliction → search terms:
        COMBUST_X / DEBIL_X / WEAK_X → planet X
        MARRIAGE_* / DOSHA_VIVAHA / MANGAL → category 'marriage'
        DEATH_* / MARANA_* → category 'death'
    """
    out: list[VerbatimRemedy] = []
    seen = set()

    def _add(r: VerbatimRemedy):
        key = (r.book, r.verse_id, r.text[:60])
        if key not in seen:
            seen.add(key)
            out.append(r)

    for p in involved_planets:
        for r in remedies_for_planet(p):
            _add(r)

    code_upper = code.upper()
    if any(k in code_upper for k in ("MARRIAGE", "VIVAHA", "MANGAL", "WIDOW")):
        for r in remedies_in_category("marriage"):
            _add(r)
    if any(k in code_upper for k in ("DEATH", "MARANA", "MRITYU")):
        for r in remedies_in_category("death"):
            _add(r)
    if "KARMIC" in code_upper or "PITRU" in code_upper or "SHRAPIT" in code_upper:
        for r in remedies_in_category("karmic"):
            _add(r)
        for r in remedies_in_category("spiritual"):
            _add(r)
    return out


def stats() -> dict:
    rems = _all_remedies()
    by_book = {}
    by_planet = {}
    by_cat = {}
    for r in rems:
        by_book[r.book] = by_book.get(r.book, 0) + 1
        for p in r.planets:
            by_planet[p] = by_planet.get(p, 0) + 1
        for c in r.categories:
            by_cat[c] = by_cat.get(c, 0) + 1
    return {
        "total": len(rems),
        "by_book": by_book,
        "by_planet": by_planet,
        "by_category": by_cat,
    }


def to_dict(r: VerbatimRemedy) -> dict:
    d = asdict(r)
    d["citation"] = r.cite()
    return d
