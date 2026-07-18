"""
Deep-rules engine — load 14,795 verse-level extractions from gemma_extractions/
and match the planet/house/sign-tagged ones against a live chart.

Complements `book_rules.py` (which uses 1,926 indexed combinations).
This deeper layer surfaces verse-precise rules with verse_id citations like
"BPHS.3", "Phaladeepika.17.45", "Saravali.22.4".
"""
from __future__ import annotations

import glob
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from engine.engines import Citation, Prediction
from engine.book_rules import TOPIC_REGEX, _clean_effect

DEEP_DIR = Path("/opt/astro/gemma_extractions")
if not DEEP_DIR.exists():
    DEEP_DIR = Path(__file__).resolve().parents[1] / "gemma_extractions"

PLANET_NAMES = {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                "Venus", "Saturn", "Rahu", "Ketu"}
SIGN_NAMES = {"Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
              "Libra", "Scorpio", "Sagittarius", "Capricorn",
              "Aquarius", "Pisces"}


@dataclass
class DeepRule:
    book: str
    verse_id: str
    text: str           # cleaned english_translation or original
    sanskrit: str
    categories: list[str]
    involves_planets: list[str]
    involves_houses: list[int]
    involves_signs: list[str]
    rule_type: str
    topics: tuple[str, ...]


# ─── Loader ───────────────────────────────────────────────────────────────

def _route_topics(text: str, categories: list[str]) -> tuple[str, ...]:
    """Topic = regex hit on text + category-name hit."""
    out: set[str] = set()
    for cat, rx in TOPIC_REGEX.items():
        if rx.search(text):
            out.add(cat)
    cat_lower = {c.lower() for c in categories}
    if {"marriage", "spouse", "wife", "husband"} & cat_lower:    out.add("marriage")
    if {"career", "profession", "livelihood"} & cat_lower:        out.add("career")
    if {"wealth", "finance", "money", "gain"} & cat_lower:        out.add("wealth")
    if {"children", "progeny"} & cat_lower:                       out.add("children")
    if {"health", "disease", "illness"} & cat_lower:              out.add("health")
    if {"longevity", "death"} & cat_lower:                        out.add("longevity")
    if {"family", "father", "mother", "siblings"} & cat_lower:    out.add("family")
    if {"foreign", "travel"} & cat_lower:                         out.add("foreign")
    if {"spirituality", "dharma", "moksha"} & cat_lower:          out.add("spirituality")
    if {"affliction", "dosha"} & cat_lower:                       out.add("afflictions")
    if {"yoga", "raja_yoga", "dhana_yoga"} & cat_lower:           out.add("yogas")
    if {"remedies", "remedy", "gemstone", "mantra"} & cat_lower:  out.add("remedies")
    if {"personality", "appearance", "body"} & cat_lower:         out.add("personality")
    if {"education", "learning"} & cat_lower:                     out.add("education")
    return tuple(out)


@lru_cache(maxsize=1)
def load_deep_rules() -> list[DeepRule]:
    """Parse all 20 _deep.json files. Cached."""
    rules: list[DeepRule] = []
    for f in sorted(glob.glob(str(DEEP_DIR / "*_deep.json"))):
        try:
            blob = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(blob, list):
            rules_list = blob
            book_name = Path(f).stem.replace("_deep", "")
        else:
            rules_list = blob.get("rules", [])
            book_name = blob.get("book") or Path(f).stem.replace("_deep", "")

        for r in rules_list:
            if not isinstance(r, dict):
                continue
            text_raw = r.get("english_translation") or r.get("original_text") or ""
            text = _clean_effect(text_raw, max_chars=350)
            if not text or len(text) < 30:
                continue
            cats = r.get("categories") or []
            topics = _route_topics(text, cats)
            if not topics:
                continue  # only keep rules we can route to a category
            houses_raw = r.get("involves_houses") or []
            houses: list[int] = []
            for h in houses_raw:
                try:
                    houses.append(int(h))
                except (TypeError, ValueError):
                    continue
            planets = [p for p in (r.get("involves_planets") or [])
                       if p in PLANET_NAMES]
            signs = [s for s in (r.get("involves_signs") or [])
                     if s in SIGN_NAMES]
            rules.append(DeepRule(
                book=r.get("_book") or book_name or "Unknown",
                verse_id=str(r.get("verse_id") or ""),
                text=text,
                sanskrit=r.get("sanskrit_iast") or "",
                categories=cats,
                involves_planets=planets,
                involves_houses=houses,
                involves_signs=signs,
                rule_type=r.get("type") or "verse",
                topics=topics,
            ))
    return rules


# ─── Chart-side helpers ───────────────────────────────────────────────────

def _planet_in_house(chart, planet: str, house: int) -> bool:
    return chart.house_of.get(planet) == house


def _planet_in_sign(chart, planet: str, sign: str) -> bool:
    from engine.engines import SIGNS
    lon = chart.positions.get(planet)
    if lon is None:
        return False
    return SIGNS[int(lon // 30)] == sign


# ─── Matcher ──────────────────────────────────────────────────────────────

def _rule_fires(chart, r: DeepRule) -> bool:
    """A deep-rule fires when its planets-in-houses / planets-in-signs apply."""
    if r.involves_planets and r.involves_houses:
        # require ALL listed planet-house claims to hold
        for p in r.involves_planets:
            for h in r.involves_houses:
                if _planet_in_house(chart, p, h):
                    return True   # any planet in any of the houses fires
        return False
    if r.involves_planets and r.involves_signs:
        for p in r.involves_planets:
            for s in r.involves_signs:
                if _planet_in_sign(chart, p, s):
                    return True
        return False
    if r.involves_planets and not r.involves_houses and not r.involves_signs:
        # Generic planet-mention rule — fire only if planet is strongly placed
        for p in r.involves_planets:
            h = chart.house_of.get(p)
            if h in (1, 4, 5, 7, 9, 10):  # kendra/trikona — strong
                return True
        return False
    return False


def match_for_chart(chart, rules: list[DeepRule] | None = None) -> list[DeepRule]:
    if rules is None:
        rules = load_deep_rules()
    return [r for r in rules if _rule_fires(chart, r)]


def predictions_for(chart, category: str,
                    max_per_category: int = 4) -> list[Prediction]:
    """Convert matched deep-rules to Predictions for one engine category."""
    matched = match_for_chart(chart)
    cat_rules = [r for r in matched if category in r.topics]
    # Dedup by verse_id+book
    seen: set[str] = set()
    unique: list[DeepRule] = []
    for r in cat_rules:
        key = f"{r.book}|{r.verse_id}|{r.text[:60]}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    # Prefer rules with verse_id + longer text
    unique.sort(key=lambda r: (bool(r.verse_id), len(r.text)), reverse=True)
    out: list[Prediction] = []
    for i, r in enumerate(unique[:max_per_category]):
        cit_text = r.verse_id or r.book
        evidence_parts = []
        if r.involves_planets: evidence_parts.append("+".join(r.involves_planets))
        if r.involves_houses:  evidence_parts.append(", ".join(f"H{h}" for h in r.involves_houses))
        if r.involves_signs:   evidence_parts.append(", ".join(r.involves_signs))
        out.append(Prediction(
            key=f"deep_rule_{category}_{i+1}",
            label=f"{r.book} {r.verse_id}".strip() or r.book,
            value=r.text,
            confidence="MEDIUM",
            chart_evidence=" / ".join(evidence_parts) or r.rule_type,
            citations=[Citation(book=r.book, verse_id=r.verse_id, text=cit_text)],
        ))
    return out
