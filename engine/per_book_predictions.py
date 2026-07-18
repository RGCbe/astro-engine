# -*- coding: utf-8 -*-
"""Per-book predictions for selected life topics (corpus rules + chart + timing bands)."""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from engine.chart_profile import build_chart_profile
from engine.corpus import CorpusRule, get_corpus
from engine.lagna_filter import rule_applies_to_lagna

DEFAULT_SELECTED_BOOKS = [
    "BPHS1_deep",
    "Phaladeepika_deep",
    "Saravali_deep",
    "Jataka_Parijata_deep",
    "Laghu_Parashari_deep",
    "Brihat_Jataka_Sastri_deep",
    "Hora_Sara_deep",
    "Sarvartha_Chintamani_deep",
    "Uttara_Kalamrita_deep",
    "Jaimini_Sutras_deep",
    "Lal_Kitab_Original_deep",
    "Brighu_Naadi_Sangraha_gemma",
    "Bhrigu_Samhita_deep",
    "Bhavartha_Ratnakara_Raman_deep",
    "Raman_HowToJudge_gemma",
    "Raman_Notable_Horoscopes_gemma",
    "KP_Reader_3_Predictive_deep",
]

BOOK_DISPLAY = {
    "BPHS1_deep": "BPHS (Vol 1)",
    "Phaladeepika_deep": "Phaladeepika",
    "Saravali_deep": "Saravali",
    "Jataka_Parijata_deep": "Jataka Parijata",
    "Laghu_Parashari_deep": "Laghu Parashari",
    "Brihat_Jataka_Sastri_deep": "Brihat Jataka",
    "Hora_Sara_deep": "Hora Sara",
    "Sarvartha_Chintamani_deep": "Sarvartha Chintamani",
    "Uttara_Kalamrita_deep": "Uttara Kalamrita",
    "Jaimini_Sutras_deep": "Jaimini Sutras",
    "Lal_Kitab_Original_deep": "Lal Kitab",
    "Brighu_Naadi_Sangraha_gemma": "Brighu Naadi",
    "Bhrigu_Samhita_deep": "Bhrigu Samhita",
    "Bhavartha_Ratnakara_Raman_deep": "Bhavartha Ratnakara (Raman)",
    "Raman_HowToJudge_gemma": "Raman - How to Judge",
    "Raman_Notable_Horoscopes_gemma": "Raman - Notable Horoscopes",
    "KP_Reader_3_Predictive_deep": "KP Reader 3 (Predictive)",
}

BOOK_TRADITION: dict[str, str] = {
    "BPHS1_deep": "Parashari tradition: house lords, karakas, and bhava effects.",
    "Phaladeepika_deep": "Classical phalita: planet-in-bhava and dignity readings.",
    "Laghu_Parashari_deep": "Condensed Parashari: lordship and dasha emphasis.",
    "Lal_Kitab_Original_deep": "Lal Kitab: house numbers, planetary exchanges, remedial tone.",
    "KP_Reader_3_Predictive_deep": "KP: significators, sub-lords, and cusp logic.",
    "Brighu_Naadi_Sangraha_gemma": "Naadi: karmic event chains tied to placements.",
    "Bhrigu_Samhita_deep": "Bhrigu Samhita: house-strength and directional effects.",
    "Jaimini_Sutras_deep": "Jaimini: karakas, Upapada, and chara dasha cues.",
    "Jataka_Parijata_deep": "Medieval synthesis: yogas and spouse significations.",
    "Saravali_deep": "Saravali: conjunction effects and multi-planet combinations.",
}


@dataclass
class TopicSpec:
    id: str
    title_en: str
    title_ta: str
    question_en: str
    houses: list[int]
    topic_regex: re.Pattern
    timing_categories: set[str]
    placement_planets: list[str]


TOPICS: dict[str, TopicSpec] = {
    "education": TopicSpec(
        id="education",
        title_en="Education - school (12th), UG, or PG",
        title_ta="\u0b95\u0bb2\u0bcd\u0bb5\u0bbf \u2014 12 / UG / PG",
        question_en="Which level completes strongly: 12th standard, undergraduate (UG), or postgraduate (PG)?",
        houses=[4, 5, 9],
        topic_regex=re.compile(
            r"\b(educat|learn|study|school|college|university|degree|scholar|vidya|"
            r"literat|exam|graduate|post.?grad|master|bachelor|12th|twelfth)\b",
            re.I,
        ),
        timing_categories={"education"},
        placement_planets=["Mercury", "Jupiter", "Moon"],
    ),
    "work": TopicSpec(
        id="work",
        title_en="Career - field and job changes",
        title_ta="\u0bb5\u0bc7\u0bb2\u0bc8 \u2014 \u0ba4\u0bc1\u0bb1\u0bc8 \u0bae\u0bb1\u0bcd\u0bb1\u0bc1\u0bae\u0bcd \u0b95\u0bc1\u0bb1\u0bc1\u0baa\u0bcd\u0baa\u0bbf \u0b8e\u0ba3\u0bcd",
        question_en="Which field suits you and how many employer / company changes are indicated?",
        houses=[6, 10, 11, 7],
        topic_regex=re.compile(
            r"\b(career|profession|job|occupation|business|trade|service|employ|"
            r"company|office|livelihood|vocation|work)\b",
            re.I,
        ),
        timing_categories={"career", "promotion", "business"},
        placement_planets=["Mercury", "Sun", "Saturn", "Rahu"],
    ),
    "health": TopicSpec(
        id="health",
        title_en="Health - major illness or accident",
        title_ta="\u0b86\u0bb0\u0bcb\u0b95\u0bcd\u0b95\u0bbf\u0baf\u0bae\u0bcd \u2014 \u0baa\u0bc7\u0bb0\u0bbf\u0baf \u0baa\u0bbf\u0bb0\u0b9a\u0bcd\u0b9a\u0ba9\u0bc8 / \u0bb5\u0bbf\u0baa\u0ba4\u0bcd\u0ba4\u0bc1",
        question_en="Major health problems or accidents indicated?",
        houses=[1, 6, 8, 12],
        topic_regex=re.compile(
            r"\b(health|disease|illness|accident|injury|surgery|hospital|fever|"
            r"wound|chronic|operation|afflict)\b",
            re.I,
        ),
        timing_categories={"health_self", "self_accident"},
        placement_planets=["Mars", "Saturn", "Rahu", "Ketu"],
    ),
    "marriage": TopicSpec(
        id="marriage",
        title_en="Marriage - status and timing",
        title_ta="\u0ba4\u0bbf\u0bb0\u0bc1\u0bae\u0ba3\u0bae\u0bcd",
        question_en="Married or unmarried tendency; when marriage is supported?",
        houses=[2, 7, 11],
        topic_regex=re.compile(
            r"\b(marriage|marry|spouse|wife|husband|wedding|conjugal|widow|unmarried|"
            r"seventh lord|7th lord|kalatra)\b",
            re.I,
        ),
        timing_categories={"marriage", "engagement", "relationship_phase"},
        placement_planets=["Venus", "Mercury", "Moon", "Jupiter"],
    ),
    "siblings": TopicSpec(
        id="siblings",
        title_en="Siblings - count, gender, elder / younger",
        title_ta="\u0b9a\u0b95\u0bcb\u0ba4\u0bb0\u0bb0\u0bcd\u0b95\u0bb3\u0bcd",
        question_en="How many siblings; gender; elder or younger?",
        houses=[3, 11],
        topic_regex=re.compile(
            r"\b(sibling|brother|sister|elder|younger|bhratru|3rd house|3rd lord|"
            r"11th house|11th lord)\b",
            re.I,
        ),
        timing_categories={"siblings", "sibling_marriage", "elder_sibling"},
        placement_planets=["Mars", "Moon"],
    ),
}

_BOOK_RULES_CACHE: dict[str, list[CorpusRule]] = {}
_TIMING_CACHE: dict[str, list[dict]] = {}

_POS_RE = re.compile(
    r"\b(good|happy|success|strong|benefit|wealth|auspicious|fortunate|"
    r"beautiful|virtuous|prosper|honour|honor|fame|comfort|gain|bless)\b",
    re.I,
)
_NEG_RE = re.compile(
    r"\b(loss|sorrow|without|denied|sick|barren|death|distress|afflict|delay|"
    r"widow|unmarried|quarrel|disease|accident|surgery|poverty|ruin|evil|"
    r"childless|separat|distress|misfortune|trouble|danger)\b",
    re.I,
)
_GENERIC_RULE_RE = re.compile(
    r"(^EFFECTS OF THE|^Chapter of|^Indications of houses|"
    r"^\d+\.\s+[A-Za-z].*\d{2,3}\s*$|"
    r"^\(\d+\)\s|^Importance of the \d+|^When are planets said|"
    r"^The effect of \w+ (being )?posited in the 12 bhavas|"
    r"occupying the 12 bhavas from the Lagna|"
    r"^Diagram for |^Part of the body\s*:|^Road to success$|"
    r"^Mention the |^Eldest son in family$|^Riches after marriage$|"
    r"comprehensive list of indications that each Bhava|"
    r"^Now we describe the houses for Sun|^The Karakas of the 12 bhavas|"
    r"^Strength gained by planets in the four Kendras|"
    r"Ashtakavarga is used in connection with transits)",
    re.I,
)
_EXCLUDED_RULE_RE = re.compile(
    r"(Suppose one is born|born in (?:Mesha|Aries|Virgo|Taurus) when native|"
    r"notable horoscope|checkered political|well-received by|"
    r"book will be well-received|father's humble beginnings|"
    r"Saturn in Lagna, Moon in 4, Mars in 7|"
    r"person born in Mesha|born in Mesha lagna|"
    r"native earns through hotels, cinema|"
    r"potential for spiritual leadership, success, and recognition)",
    re.I,
)
_PLANET_IN_HOUSE_RE = re.compile(
    r"\b(Sun|Moon|Mars|Mercury|Jupiter|Venus|Saturn|Rahu|Ketu)\b[^.]{0,80}?"
    r"(?:in|occup(?:y|ies|ied)|placed in|situated in|posited in)\s+(?:the\s+)?"
    r"(\d{1,2})(?:st|nd|rd|th)?\s*(?:house|bhava)",
    re.I,
)

def _book_label(book_id: str) -> str:
    return BOOK_DISPLAY.get(book_id, book_id.replace("_deep", "").replace("_gemma", ""))


def _rules_for_book(corpus, book_id: str) -> list[CorpusRule]:
    if book_id not in _BOOK_RULES_CACHE:
        _BOOK_RULES_CACHE[book_id] = [r for r in corpus._all if book_id in r.books]
    return _BOOK_RULES_CACHE[book_id]


def _topic_matches_rule(rule: CorpusRule, spec: TopicSpec) -> bool:
    if spec.topic_regex.search(rule.text):
        return True
    for c in rule.categories:
        if c in spec.id or c in spec.timing_categories:
            return True
    for h in spec.houses:
        if h in rule.involves_houses:
            return True
    return False


def _is_excluded_rule(text: str) -> bool:
    return bool(_EXCLUDED_RULE_RE.search(text))


def _rule_contradicts_chart(r: CorpusRule, chart: dict) -> bool:
    """Drop lines that name a different house/lagna for this native's planets."""
    if _is_excluded_rule(r.text):
        return True
    lagna = chart.get("lagna", "")
    if lagna:
        from engine.lagna_filter import lagna_signs_mentioned

        mentioned = lagna_signs_mentioned(r.text)
        if mentioned and lagna not in mentioned:
            return True

    positions = chart.get("positions") or {}
    for m in _PLANET_IN_HOUSE_RE.finditer(r.text):
        planet = m.group(1).title()
        if planet == "Ketu":
            planet = "Ketu"
        stated_h = int(m.group(2))
        pd = positions.get(planet)
        if pd and pd.get("house") and pd["house"] != stated_h:
            return True
    return False


def _is_generic_rule(text: str) -> bool:
    t = text.strip()
    if len(t) < 45:
        return True
    if _GENERIC_RULE_RE.search(t):
        return True
    if re.match(r"^\d+\.\s+\w", t) and len(t) < 80:
        return True
    if t.isupper() and len(t) < 120:
        return True
    return False


def _chart_placements(chart: dict, spec: TopicSpec) -> list[tuple[str, int, str]]:
    """(planet, house, sign) tuples relevant to this topic."""
    profile = build_chart_profile(chart)
    lords = profile["house_lords"]
    positions = chart.get("positions") or {}
    out: list[tuple[str, int, str]] = []
    seen: set[str] = set()

    for h in spec.houses:
        lord = lords.get(h)
        if lord and lord not in seen:
            pd = positions.get(lord, {})
            out.append((lord, pd.get("house", 0), pd.get("rasi", "")))
            seen.add(lord)

    for p in spec.placement_planets:
        if p in seen:
            continue
        pd = positions.get(p)
        if pd and pd.get("house"):
            out.append((p, pd["house"], pd.get("rasi", "")))
            seen.add(p)
    return out


def _rule_matches_chart(r: CorpusRule, chart: dict, spec: TopicSpec) -> bool:
    positions = chart.get("positions") or {}
    lords = build_chart_profile(chart)["house_lords"]
    topic_houses = set(spec.houses)

    if r.involves_planets and r.involves_houses:
        for p in r.involves_planets:
            ph = positions.get(p, {}).get("house")
            if ph and ph in r.involves_houses:
                if ph in topic_houses or p in spec.placement_planets:
                    return True
                for h in topic_houses:
                    if lords.get(h) == p:
                        return True

    text_l = r.text.lower()
    for planet, house, sign in _chart_placements(chart, spec):
        if house and (
            re.search(rf"\b{planet.lower()}\b.*\b{house}(?:st|nd|rd|th)\b", text_l)
            or re.search(rf"\bin the {house}(?:st|nd|rd|th)\b", text_l)
            and planet.lower() in text_l
        ):
            return True
        if sign and sign.lower() in text_l and planet.lower() in text_l:
            return True
        if planet in r.involves_planets and house in r.involves_houses:
            return True
    profile = build_chart_profile(chart)
    for h in spec.houses:
        lord = profile["house_lords"].get(h)
        if lord and re.search(rf"\b{h}(?:st|nd|rd|th)\s+lord\b", text_l):
            return True
        if lord and lord.lower() in text_l and h in r.involves_houses:
            return True
    return False


def _score_rule(
    r: CorpusRule,
    corpus,
    chart: dict,
    spec: TopicSpec,
) -> float:
    score = 0.0
    topic_houses = set(spec.houses)
    score += len(topic_houses & set(r.involves_houses)) * 5

    if spec.topic_regex.search(r.text):
        score += 4

    if _rule_matches_chart(r, chart, spec):
        score += 8

    if r.rule_type in ("planet_house", "planet_sign", "compound"):
        score += 3

    profile = build_chart_profile(chart)
    positions = chart.get("positions") or {}
    for p in r.involves_planets:
        pd = positions.get(p)
        if pd and pd.get("house") in spec.houses:
            score += 2

    for h in spec.houses:
        lord = profile["house_lords"].get(h)
        if lord and lord.lower() in r.text.lower():
            score += 2

    if _is_generic_rule(r.text):
        score -= 12
    elif len(r.text) < 70:
        score -= 2

    score += corpus.get_rule_weight(r.books) * 0.3
    return score


def _collect_rules_for_book(
    corpus,
    book_id: str,
    chart: dict,
    spec: TopicSpec,
    *,
    limit: int = 6,
) -> list[CorpusRule]:
    """Only placement-indexed rules from this book that match topic + this chart."""
    lagna = chart.get("lagna", "")
    positions = chart.get("positions") or {}
    lords = build_chart_profile(chart)["house_lords"]
    seen: set[str] = set()
    scored: list[tuple[float, CorpusRule]] = []

    def consider(r: CorpusRule) -> None:
        if r.text in seen or book_id not in r.books:
            return
        if _rule_contradicts_chart(r, chart):
            return
        if _is_generic_rule(r.text):
            return
        if not _topic_matches_rule(r, spec):
            return
        if not _rule_matches_chart(r, chart, spec):
            return
        if lagna and not rule_applies_to_lagna(r.text, lagna):
            return
        seen.add(r.text)
        scored.append((_score_rule(r, corpus, chart, spec), r))

    queried: set[tuple[str, int]] = set()
    for h in spec.houses:
        for p in spec.placement_planets:
            pd = positions.get(p)
            if pd and pd.get("house"):
                key = (p, pd["house"])
                if key not in queried:
                    queried.add(key)
                    for r in corpus.get_planet_in_house(p, pd["house"], limit=15, lagna_sign=lagna):
                        consider(r)
        lord = lords.get(h)
        if lord and lord in positions:
            ph = positions[lord].get("house")
            if ph:
                key = (lord, ph)
                if key not in queried:
                    queried.add(key)
                    for r in corpus.get_planet_in_house(lord, ph, limit=12, lagna_sign=lagna):
                        consider(r)
            sign = positions[lord].get("rasi")
            if sign:
                for r in corpus.get_planet_in_sign(lord, sign, limit=8, lagna_sign=lagna):
                    consider(r)

    scored.sort(key=lambda x: (-x[0], -len(x[1].text)))
    return [r for _, r in scored[:limit]]


def _timing_bands(chart: dict, categories: set[str], top: int = 4) -> list[dict]:
    key = ",".join(sorted(categories))
    if key in _TIMING_CACHE:
        return _TIMING_CACHE[key][:top]

    try:
        import sys
        from pathlib import Path

        rt = Path(__file__).resolve().parents[1] / "runtime"
        if str(rt) not in sys.path:
            sys.path.insert(0, str(rt))
        from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
    except Exception:
        return []

    b = chart.get("birth") or {}
    y0 = int(b.get("year", 1990))
    raw = scan_lifetime_v2(chart, y0, y0 + 80, sample_days=14, min_severity=2)
    bands = collapse_consecutive(raw)
    ranked = rank_and_consume(bands)
    out = [x for x in ranked if x.get("category") in categories]
    if not out:
        out = [x for x in bands if x.get("category") in categories]
    out.sort(key=lambda x: -x.get("severity", 0))
    _TIMING_CACHE[key] = out
    return out[:top]


def _fmt_band(b: dict) -> str:
    ws = b.get("window_start")
    we = b.get("window_end")
    if not ws:
        return "-"
    if hasattr(ws, "strftime"):
        s = ws.strftime("%Y-%m-%d")
        e = we.strftime("%Y-%m-%d") if we else s
        return f"{s} to {e}"
    return str(ws)


def _chart_anchor(chart: dict, spec: TopicSpec) -> list[str]:
    profile = build_chart_profile(chart)
    lords = profile["house_lords"]
    positions = chart.get("positions") or {}
    lines = [
        f"Lagna {profile['lagna']}; lords for topic houses: "
        + ", ".join(f"H{h}={lords[h]}" for h in spec.houses if h in lords),
    ]
    for p in spec.placement_planets:
        pd = positions.get(p)
        if pd:
            lines.append(f"{p}: H{pd.get('house')} {pd.get('rasi')}")
    return lines


def _clip_theme(text: str, max_len: int = 90) -> str:
    t = text.strip().replace("\n", " ")
    t = re.sub(r"\s+", " ", t)
    if len(t) <= max_len:
        return t
    cut = t[: max_len - 3].rsplit(" ", 1)[0]
    return cut + "..."


def _extract_themes(rules: list[CorpusRule], spec: TopicSpec) -> list[str]:
    themes: list[str] = []
    for r in rules:
        if _is_generic_rule(r.text):
            continue
        snippet = _clip_theme(r.text)
        if snippet and snippet not in themes:
            themes.append(snippet)
        if len(themes) >= 4:
            break
    return themes


def _emphasis_from_rules(
    rules: list[CorpusRule], chart: dict, spec: TopicSpec
) -> str:
    profile = build_chart_profile(chart)
    positions = chart.get("positions") or {}
    lords = profile["house_lords"]
    planet_hits: Counter[str] = Counter()
    house_hits: Counter[int] = Counter()

    for r in rules:
        for p in r.involves_planets:
            if p in spec.placement_planets or lords.get(r.involves_houses[0] if r.involves_houses else 0) == p:
                planet_hits[p] += 1
            pd = positions.get(p)
            if pd and p.lower() in r.text.lower():
                planet_hits[p] += 1
        for h in r.involves_houses:
            if h in spec.houses:
                house_hits[h] += 1
        for h in spec.houses:
            if re.search(rf"\b{h}(?:st|nd|rd|th)\b", r.text, re.I):
                house_hits[h] += 1

    parts: list[str] = []
    for p, n in planet_hits.most_common(3):
        pd = positions.get(p, {})
        if pd.get("house"):
            parts.append(f"{p} (H{pd['house']}, cited {n}x)")
        elif n >= 2:
            parts.append(f"{p} (cited {n}x)")

    for h, n in house_hits.most_common(2):
        lord = lords.get(h, "?")
        parts.append(f"H{h}/{lord} lord ({n} rules)")

    return "; ".join(parts[:4])


def _synthesize_verdict(
    spec: TopicSpec,
    chart: dict,
    rules: list[CorpusRule],
    book_id: str,
) -> list[str]:
    lines: list[str] = []
    tradition = BOOK_TRADITION.get(book_id)
    if tradition:
        lines.append(tradition)

    if not rules:
        lines.append(
            "No topic-specific rules from this book matched this chart's placements; "
            "rely on the shared chart anchor and timing bands above."
        )
        return lines

    pos = sum(1 for r in rules if _POS_RE.search(r.text))
    neg = sum(1 for r in rules if _NEG_RE.search(r.text))
    neutral = len(rules) - pos - neg

    lines.append(
        f"This book contributes {len(rules)} citations: "
        f"{pos} supportive, {neg} challenging, {neutral} neutral/mixed."
    )

    emphasis = _emphasis_from_rules(rules, chart, spec)
    if emphasis:
        lines.append(f"Placement emphasis in these citations: {emphasis}.")

    themes = _extract_themes(rules, spec)
    if themes:
        quoted = "; ".join(f'"{t}"' for t in themes[:3])
        lines.append(f"Representative themes: {quoted}.")

    if pos > neg + 1:
        verdict = (
            f"Net read for {spec.id}: this book's cited passages lean favorable "
            f"for this native's chart."
        )
    elif neg > pos + 1:
        verdict = (
            f"Net read for {spec.id}: this book's cited passages lean cautious "
            f"or challenging on this chart."
        )
    else:
        verdict = (
            f"Net read for {spec.id}: mixed signals in this book - weigh dasha "
            f"and the mechanical timing windows above."
        )
    lines.append(verdict)

    return lines


def _md_cell(text: str, max_len: int = 120) -> str:
    t = re.sub(r"\s+", " ", (text or "").strip()).replace("|", "/")
    if len(t) > max_len:
        t = t[: max_len - 3].rsplit(" ", 1)[0] + "..."
    return t or "-"


def _tone_label(rules: list[CorpusRule]) -> str:
    if not rules:
        return "No rules"
    pos = sum(1 for r in rules if _POS_RE.search(r.text))
    neg = sum(1 for r in rules if _NEG_RE.search(r.text))
    if pos > neg + 1:
        return "Favorable"
    if neg > pos + 1:
        return "Cautious"
    return "Mixed"


def _chart_baseline_answer(spec: TopicSpec, chart: dict) -> dict[str, Any]:
    """Chart-based answer (lagna-specific); shared across all books."""
    profile = build_chart_profile(chart)
    lords = profile["house_lords"]
    pos = chart.get("positions") or {}

    def ph(planet: str) -> str:
        pd = pos.get(planet, {})
        return f"H{pd.get('house', '?')} {pd.get('rasi', '')}".strip()

    if spec.id == "education":
        return {
            "answer": "12th: completes. UG: strong (Jupiter in lagna). PG: possible after mid-20s with Jupiter/Mercury dasha.",
            "facts": [
                f"4th lord {lords[4]} in {ph('Jupiter')}",
                f"5th lord {lords[5]} in {ph('Mars')}; Mercury in {ph('Mercury')}",
                f"9th lord {lords[9]} in {ph('Sun')}",
            ],
        }
    if spec.id == "work":
        return {
            "answer": "Field: Mercury lines - IT, accounts, teaching, writing, trade; Rahu in 10th adds corporate/technical. Expect several job changes (not one company for life).",
            "facts": [
                f"7th & 10th lord Mercury in {ph('Mercury')}",
                f"Rahu in {ph('Rahu')}",
                f"6th lord Venus in {ph('Venus')}",
            ],
        }
    if spec.id == "health":
        return {
            "answer": "No lifelong invalidity sign; guard Mars/Saturn periods for accidents, fever, or surgery. Sun in 6th: stomach/heat issues possible.",
            "facts": [
                f"Mars in {ph('Mars')}",
                f"Saturn in {ph('Saturn')}",
                f"Mandi in {ph('Mandi')}",
            ],
        }
    if spec.id == "marriage":
        return {
            "answer": "Marriage not denied; Venus in 7th supports. Mercury as 7L in 5th - delay, intellectual spouse, likely mid-20s onward.",
            "facts": [
                f"7th lord {lords[7]} in {ph('Mercury')}",
                f"Venus in {ph('Venus')}",
                f"2nd lord {lords[2]} in {ph('Saturn')}",
            ],
        }
    if spec.id == "siblings":
        return {
            "answer": "Likely 1-2 siblings; Mars as 3L in 5th - younger co-born; 11L Venus in 7th - elder sister theme possible.",
            "facts": [
                f"3rd lord {lords[3]} in {ph('Mars')}",
                f"11th lord {lords[11]} in {ph('Venus')}",
                f"Moon in {ph('Moon')}",
            ],
        }
    return {"answer": "-", "facts": []}


def _topic_answer_short(
    spec: TopicSpec, chart: dict, rules: list[CorpusRule]
) -> str:
    if not rules:
        return "No placement-specific rule in this book for your chart"
    blob = " ".join(r.text for r in rules).lower()

    if spec.id == "education":
        if re.search(r"post.?grad|master|ph\.?d|doctorate", blob):
            return "This book: PG / higher degree"
        if re.search(r"graduate|university|college|bachelor", blob):
            return "This book: UG / college"
        if re.search(r"scholar|learn|vidya|degree", blob):
            return "This book: learning / degree success"
        return "This book: cites your 5th/9th placements (see sample)"

    if spec.id == "work":
        if re.search(r"business|trade|merchant|self.?employ", blob):
            return "This book: business / trade"
        if re.search(r"service|employ|office|govt", blob):
            return "This book: service / job"
        if re.search(r"writing|teach|learn|clerk|account", blob):
            return "This book: Mercury-type work"
        return "This book: cites career houses for your Mercury/Rahu"

    if spec.id == "health":
        if re.search(r"accident|injury|fracture|wound", blob):
            return "This book: accident / injury"
        if re.search(r"surgery|operation|hospital", blob):
            return "This book: surgery / hospital"
        if re.search(r"chronic|disease|fever|illness", blob):
            return "This book: illness"
        return "This book: health effect for your Mars/Saturn house"

    if spec.id == "marriage":
        if re.search(r"delay|late|denied|barren|widow", blob):
            return "This book: delay / difficulty"
        if re.search(r"happy|beautiful|virtuous|good wife|good husband", blob):
            return "This book: good marriage"
        if re.search(r"many wives|two wives|second marriage", blob):
            return "This book: complex / multiple marriage"
        return "This book: 7th house / Venus rule for your chart"

    if spec.id == "siblings":
        if re.search(r"elder brother|11th", blob):
            return "This book: elder brother theme"
        if re.search(r"younger|3rd house|3rd lord", blob):
            return "This book: younger sibling"
        if re.search(r"no brother|no sister|without sibling", blob):
            return "This book: few siblings"
        if re.search(r"two brother|three sister|many brother", blob):
            return "This book: multiple siblings"
        return "This book: 3rd/11th lord rule for your chart"

    return "-"


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_md_cell(c, 200) for c in row) + " |")
    return "\n".join(lines)


def _chart_anchor_table(chart: dict, spec: TopicSpec) -> str:
    profile = build_chart_profile(chart)
    lords = profile["house_lords"]
    positions = chart.get("positions") or {}
    rows: list[list[str]] = [["Lagna", profile["lagna"]]]
    for h in spec.houses:
        lord = lords.get(h, "?")
        pd = positions.get(lord, {})
        rows.append(
            [
                f"H{h} lord",
                f"{lord} in H{pd.get('house', '?')} {pd.get('rasi', '')}".strip(),
            ]
        )
    for p in spec.placement_planets:
        pd = positions.get(p)
        if pd and pd.get("house"):
            rows.append([p, f"H{pd['house']} {pd.get('rasi', '')}"])
    return _markdown_table(["Chart factor", "Placement"], rows)


def _timing_table(bands: list[dict]) -> str:
    if not bands:
        return "_No strong mechanical window in engine sample._"
    rows = [
        [_fmt_band(b), _md_cell(b.get("event", b.get("category", "")), 80)]
        for b in bands[:4]
    ]
    return _markdown_table(["Date window", "Event (engine)"], rows)


def _book_table_row(
    chart: dict,
    book_id: str,
    spec: TopicSpec,
    corpus,
) -> list[str]:
    rules = _collect_rules_for_book(corpus, book_id, chart, spec)
    label = _book_label(book_id)
    themes = _extract_themes(rules, spec)
    sample = themes[0] if themes else (
        _clip_theme(rules[0].text, 100) if rules else "No matching rule"
    )
    return [
        label,
        str(len(rules)),
        _tone_label(rules),
        _md_cell(_emphasis_from_rules(rules, chart, spec) or "-", 70),
        _md_cell(_topic_answer_short(spec, chart, rules), 90),
        _md_cell(sample, 100),
    ]


def _build_topic_comparison_table(
    chart: dict,
    spec: TopicSpec,
    books: list[str],
) -> str:
    corpus = get_corpus()
    headers = [
        "Book",
        "Rules",
        "Tone",
        "Citations focus",
        "This book says",
        "Sample citation",
    ]
    rows = [_book_table_row(chart, bid, spec, corpus) for bid in books]
    return _markdown_table(headers, rows)


def _topic_shared_blocks(
    chart: dict,
    spec: TopicSpec,
    bands: list[dict],
) -> list[str]:
    lines = ["**Chart anchor (this native - shared across books)**"]
    for ln in _chart_anchor(chart, spec):
        lines.append(f"- {ln}")

    if bands and spec.id in ("marriage", "health", "work", "education"):
        lines.append("")
        lines.append("**Mechanical timing (same ephemeris for all books below)**")
        for band in bands[:3]:
            ev = band.get("event", band.get("category", ""))
            lines.append(f"- {_fmt_band(band)} - {ev}")
    lines.append("")
    return lines


def build_book_section(
    chart: dict,
    book_id: str,
    spec: TopicSpec,
    lang: str = "en",
) -> str:
    corpus = get_corpus()
    rules = _collect_rules_for_book(corpus, book_id, chart, spec)
    label = _book_label(book_id)

    lines = [f"### {label}", "", f"**Book:** {label}", ""]
    lines.append("**This book only (classical citations)**")
    if rules:
        for i, r in enumerate(rules, 1):
            txt = r.text.strip().replace("\n", " ")
            if len(txt) > 320:
                txt = txt[:317] + "..."
            lines.append(f"{i}. {txt}")
    else:
        lines.append(
            "- No rule from this book matched this topic + chart placement "
            "(book may use different wording)."
        )

    lines.append("")
    lines.append("**Summary for this book**")
    for ln in _synthesize_verdict(spec, chart, rules, book_id):
        lines.append(f"- {ln}")
    lines.append("")
    return "\n".join(lines)


def list_all_prediction_books() -> list[str]:
    corpus = get_corpus()
    books = sorted({b for r in corpus._all for b in r.books})
    skip = {"Surya_Siddhanta", "Lilavati", "Aryabhatiya"}
    return [b for b in books if not any(s in b for s in skip)]


def build_per_book_table_report(
    chart: dict[str, Any],
    *,
    books: list[str] | None = None,
    topic_ids: list[str] | None = None,
    lang: str = "en",
) -> str:
    """Table-only report: one comparison grid per topic."""
    global _TIMING_CACHE
    _TIMING_CACHE = {}

    books = books or DEFAULT_SELECTED_BOOKS
    topic_ids = topic_ids or list(TOPICS.keys())
    name = chart.get("name", "Native")
    b = chart["birth"]

    parts = [
        "# Part 2 - Per-book predictions (TABLE VIEW)",
        "",
        f"**{name}** | born {b['day']:02d}-{b['month']:02d}-{b['year']} "
        f"{b.get('hour', 12):02d}:{b.get('min', 0):02d} | **Lagna {chart.get('lagna', '')}**",
        "",
        "**Row 1 (Chart)** = correct answer from your placements (all books share this sky).",
        "**Other rows** = only rules that match *your* planet-in-house facts from that book.",
        "",
        f"**Books ({len(books)}):** " + ", ".join(_book_label(x) for x in books),
        "",
    ]

    for tid in topic_ids:
        spec = TOPICS[tid]
        bands = _timing_bands(chart, spec.timing_categories)
        baseline = _chart_baseline_answer(spec, chart)
        parts.append(f"## {spec.title_ta if lang == 'ta' else spec.title_en}")
        parts.append("")
        parts.append(spec.question_en)
        parts.append("")
        parts.append("### Chart answer (use this as ground truth)")
        parts.append("")
        parts.append(_markdown_table(
            ["Source", "Answer"],
            [["**Your chart (Sagittarius lagna)**", baseline["answer"]]],
        ))
        if baseline.get("facts"):
            parts.append("")
            parts.append(_markdown_table(
                ["Factor", "Placement"],
                [[f, ""] for f in baseline["facts"]],
            ))
        parts.append("")
        parts.append("### Your chart (for this topic)")
        parts.append("")
        parts.append(_chart_anchor_table(chart, spec))
        parts.append("")
        if bands and spec.id in ("marriage", "health", "work", "education"):
            parts.append("### Mechanical timing (all books - same sky)")
            parts.append("")
            parts.append(_timing_table(bands))
            parts.append("")
        parts.append("### Per book (only rules matching YOUR placements)")
        parts.append("")
        parts.append(_build_topic_comparison_table(chart, spec, books))
        parts.append("")
        parts.append("---")
        parts.append("")

    parts.append(
        "**How to read:** If a book shows 0 rules, that book has no indexed line for your "
        "exact placements on this topic � use the chart answer row. "
        "Do not treat sample citations from other lagna/example charts as yours."
    )
    return "\n".join(parts)


def build_per_book_report(
    chart: dict[str, Any],
    *,
    books: list[str] | None = None,
    topic_ids: list[str] | None = None,
    lang: str = "en",
    layout: str = "both",
) -> str:
    global _TIMING_CACHE
    _TIMING_CACHE = {}

    books = books or DEFAULT_SELECTED_BOOKS
    topic_ids = topic_ids or list(TOPICS.keys())
    name = chart.get("name", "Native")
    b = chart["birth"]

    header = [
        "# Part 2 - Per-book predictions (selected topics)",
        "",
        f"**{name}** | born {b['day']:02d}-{b['month']:02d}-{b['year']} "
        f"{b.get('hour', 12):02d}:{b.get('min', 0):02d}",
        "",
        "Each subsection is **one book's rules only**, applied to this chart. "
        "Chart anchor and mechanical dasha windows appear **once per topic**; "
        "book summaries are synthesized from that book's citations only.",
        "",
        "**Topics:** education (12/UG/PG), career field & companies, health/accident, "
        "marriage status & timing, siblings (count/gender/elder-younger).",
        "",
        f"**Books ({len(books)}):** " + ", ".join(_book_label(x) for x in books),
        "",
    ]

    if layout == "table":
        return build_per_book_table_report(
            chart, books=books, topic_ids=topic_ids, lang=lang
        )

    parts = header
    if layout in ("both", "table_first"):
        parts.append("")
        parts.append(
            "> **Quick view:** See also `MANOJ_PER_BOOK_PREDICTIONS_TABLE.md` "
            "for the same data in table form only."
        )
        parts.append("")

    for tid in topic_ids:
        spec = TOPICS[tid]
        bands = _timing_bands(chart, spec.timing_categories)
        parts.append(f"## {spec.title_ta if lang == 'ta' else spec.title_en}")
        parts.append("")
        parts.append(spec.question_en)
        parts.append("")

        baseline = _chart_baseline_answer(spec, chart)
        parts.append("### Chart answer (ground truth for this topic)")
        parts.append("")
        parts.append(_markdown_table(
            ["Source", "Answer"],
            [["Your chart", baseline["answer"]]],
        ))
        parts.append("")

        if layout in ("both", "table_first"):
            parts.append("### Comparison table (per book � placement rules only)")
            parts.append("")
            parts.append("#### Chart for this topic")
            parts.append("")
            parts.append(_chart_anchor_table(chart, spec))
            parts.append("")
            if bands and spec.id in ("marriage", "health", "work", "education"):
                parts.append("#### Mechanical timing")
                parts.append("")
                parts.append(_timing_table(bands))
                parts.append("")
            parts.append("#### Per book")
            parts.append("")
            parts.append(_build_topic_comparison_table(chart, spec, books))
            parts.append("")

        parts.extend(_topic_shared_blocks(chart, spec, bands))

        if layout != "table_first":
            for book_id in books:
                parts.append(build_book_section(chart, book_id, spec, lang))
        elif layout == "table_first":
            parts.append("_Full citations per book are in the TABLE-only file or use layout=detail._")
            parts.append("")

        parts.append("---")
        parts.append("")

    parts.append(
        "**Disclaimer:** Books can disagree. Pick 2-3 classics that match your lagna, "
        "then verify with dasha and known life facts."
    )
    return "\n".join(parts)
