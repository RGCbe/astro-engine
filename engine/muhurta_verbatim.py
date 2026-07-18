"""
Verbatim muhurta rules surfaced from Muhurtha_Chintamani + companion books.

The 691 muhurta-tagged rules across the deep corpus carry their own
sub-categories ('marriage', 'travel', 'education', 'children', 'death',
'career', 'wealth', 'health', 'dosha', etc.). This module exposes them
as cited verbatim text so the muhurta engine can ground each
recommendation in a primary classical source.

Used by `engine.muhurta` to attach citations to each activity-rule
table and by the reading layer when explaining auspicious-window picks.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache


# Map from `engine.muhurta` activity keys → sub-category labels in the corpus
ACTIVITY_TO_CATEGORIES = {
    "marriage":          ("marriage",),
    "business_start":    ("wealth", "career"),
    "travel":            ("travel",),
    "naming_ceremony":   ("children",),
    "education_start":   ("education", "children"),
    "general":           ("muhurta",),
}


@dataclass
class VerbatimMuhurtaRule:
    book: str
    verse_id: str
    text: str
    categories: list[str]
    rule_type: str

    def cite(self) -> str:
        if self.verse_id:
            return f"{self.book} {self.verse_id}"
        return self.book


@lru_cache(maxsize=1)
def _all_muhurta_rules() -> list[VerbatimMuhurtaRule]:
    from .verse_locator import _load_all_deep
    out: list[VerbatimMuhurtaRule] = []
    for r in _load_all_deep():
        cats = [c.lower() for c in (r.get("categories") or [])]
        if "muhurta" not in cats:
            continue
        text = (r.get("english_translation") or r.get("original_text") or "").strip()
        if len(text) < 30:
            continue
        out.append(VerbatimMuhurtaRule(
            book=r.get("_book", ""),
            verse_id=r.get("verse_id") or "",
            text=text,
            categories=cats,
            rule_type=(r.get("rule_type") or r.get("type") or "rule"),
        ))
    return out


def rules_for_activity(activity: str, max_results: int = 10
                       ) -> list[VerbatimMuhurtaRule]:
    """Verbatim muhurta rules relevant to an activity (e.g. 'marriage')."""
    cats = ACTIVITY_TO_CATEGORIES.get(activity, (activity,))
    cats_lc = {c.lower() for c in cats}
    matches = [r for r in _all_muhurta_rules()
               if any(c in cats_lc for c in r.categories)]
    # Prefer Muhurtha_Chintamani > Phaladeepika > others, with verse_id first
    book_pri = {"Muhurtha_Chintamani": 0, "Phaladeepika": 1, "BPHS1": 2,
                "Sarvartha_Chintamani": 3, "Bhrigu_Samhita": 4}
    matches.sort(key=lambda r: (book_pri.get(r.book, 9),
                                 0 if r.verse_id else 1,
                                 -len(r.text)))
    return matches[:max_results]


def _ascii_fold(s: str) -> str:
    """Strip Sanskrit diacritics so 'Bāṇa' matches 'Bana'."""
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFKD', s)
                   if not unicodedata.combining(c)).lower()


def rules_for_dosha(dosha_name: str, max_results: int = 5
                    ) -> list[VerbatimMuhurtaRule]:
    """Verbatim rules tagged with both 'muhurta' and 'dosha' that mention
    the given dosha name (e.g. 'Bana', 'Tripushkar', 'Mrityu').
    Diacritic-insensitive so 'Bana' matches 'Bāṇa'."""
    needle = _ascii_fold(dosha_name)
    out = [r for r in _all_muhurta_rules()
           if "dosha" in r.categories and needle in _ascii_fold(r.text)]
    return out[:max_results]


def stats() -> dict:
    rules = _all_muhurta_rules()
    by_book = {}
    by_subcat = {}
    for r in rules:
        by_book[r.book] = by_book.get(r.book, 0) + 1
        for c in r.categories:
            if c == "muhurta":
                continue
            by_subcat[c] = by_subcat.get(c, 0) + 1
    return {
        "total": len(rules),
        "by_book": by_book,
        "by_subcategory": dict(sorted(by_subcat.items(),
                                      key=lambda x: -x[1])[:20]),
    }
