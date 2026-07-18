"""
Education / major-subject predictor.

Combines six signals from the chart to name the natural field(s) of study:

    1. D24 (Chaturvimshamsa) — the dedicated education varga
       Position of Mercury (intellect) and Jupiter (wisdom) in D24.
    2. 5th house — natural house of intelligence and learning.
    3. 2nd house — house of speech and accumulated knowledge.
    4. 4th house — formal education, schooling.
    5. Saturn's sign / nakshatra — the subject of long discipline.
    6. Mercury's nakshatra lord — the texture of intellect.

Output: ranked list of probable subject domains with the contributing
signals enumerated so the client can verify.
"""
from __future__ import annotations

from dataclasses import dataclass


SIGN_FIELD_AFFINITY = {
    # Each sign maps to subjects/fields it tends to amplify
    "Aries":      ["engineering", "military / sports", "surgery", "metallurgy", "mechanical"],
    "Taurus":     ["finance", "agriculture", "music", "fashion / design", "real estate"],
    "Gemini":     ["communication", "journalism", "writing", "computer science", "trade"],
    "Cancer":     ["psychology", "hospitality", "nursing", "marine sciences", "history"],
    "Leo":        ["administration", "politics", "drama", "leadership", "luxury"],
    "Virgo":      ["accounting", "data analysis", "medicine", "linguistics", "research"],
    "Libra":      ["law", "fashion design", "diplomacy", "fine arts", "interior design"],
    "Scorpio":    ["medicine / surgery", "occult / research", "investigation", "biotech", "psychology"],
    "Sagittarius": ["philosophy", "law", "teaching", "religion / theology", "publishing"],
    "Capricorn":  ["civil engineering", "administration", "business management", "geology", "law"],
    "Aquarius":   ["aerospace", "computer science / IT", "humanitarian work", "astrology", "innovation"],
    "Pisces":     ["psychology", "spiritual / mystical studies", "fine arts", "marine biology", "music"],
}

PLANET_FIELD_AFFINITY = {
    "Sun":     ["administration", "medicine", "politics", "leadership"],
    "Moon":    ["psychology", "nursing", "hospitality", "literature"],
    "Mars":    ["engineering", "military", "surgery", "sports", "land"],
    "Mercury": ["mathematics", "computer science", "communication", "commerce", "writing"],
    "Jupiter": ["law", "philosophy", "teaching", "finance / banking", "religion"],
    "Venus":   ["fine arts", "music", "fashion", "luxury / hospitality", "design"],
    "Saturn":  ["civil engineering", "research", "mining", "law", "labour management"],
    "Rahu":    ["aerospace", "foreign trade", "computer science", "media", "research"],
    "Ketu":    ["mystical / occult", "research", "medicine", "spirituality"],
}


@dataclass
class SubjectSignal:
    field: str
    score: float
    sources: list[str]


def _planet_sign(chart, planet: str) -> str:
    lon = chart.positions.get(planet)
    if lon is None:
        return ""
    SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return SIGNS[int(lon // 30)]


def _d24_sign(chart, planet: str) -> str:
    d24 = (getattr(chart, "vargas", None) or {}).get("D24", {})
    return d24.get(planet, "")


def _lord_of_house(chart, house: int) -> str:
    SIGN_LORD = {
        0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
        5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter",
        9: "Saturn", 10: "Saturn", 11: "Jupiter",
    }
    lagna = int(chart.lagna_lon // 30)
    return SIGN_LORD[(lagna + house - 1) % 12]


def predict_subjects(chart, top_n: int = 5) -> list[SubjectSignal]:
    scores: dict[str, list[str]] = {}

    def _add(field: str, source: str, weight: float = 1.0):
        scores.setdefault(field, [])
        scores[field].append(f"{source} (+{weight})")

    # 1. D24 placements of Mercury and Jupiter — STRONGEST signal
    for p, w in (("Mercury", 3.0), ("Jupiter", 2.5)):
        s = _d24_sign(chart, p)
        if s:
            for field in SIGN_FIELD_AFFINITY.get(s, []):
                _add(field, f"{p} in D24-{s}", w)
        # Also use natal sign for Mercury (intellect karaka)
        natal = _planet_sign(chart, p)
        if natal:
            for field in SIGN_FIELD_AFFINITY.get(natal, []):
                _add(field, f"{p} natally in {natal}", w * 0.6)
            # Planet's own affinity
            for field in PLANET_FIELD_AFFINITY.get(p, []):
                _add(field, f"{p} (intellect karaka)", 1.5)

    # 2. 5th house lord — sign + planet itself (downweighted vs Mercury/Jupiter)
    l5 = _lord_of_house(chart, 5)
    s5 = _planet_sign(chart, l5)
    if s5:
        for field in SIGN_FIELD_AFFINITY.get(s5, []):
            _add(field, f"5th-lord {l5} in {s5}", 1.0)
    for field in PLANET_FIELD_AFFINITY.get(l5, []):
        _add(field, f"5th-lord is {l5}", 0.7)

    # 3. 4th house lord (formal schooling)
    l4 = _lord_of_house(chart, 4)
    s4 = _planet_sign(chart, l4)
    if s4:
        for field in SIGN_FIELD_AFFINITY.get(s4, []):
            _add(field, f"4th-lord {l4} in {s4}", 0.9)

    # 4. 2nd house lord (accumulated knowledge / speech)
    l2 = _lord_of_house(chart, 2)
    s2 = _planet_sign(chart, l2)
    if s2:
        for field in SIGN_FIELD_AFFINITY.get(s2, []):
            _add(field, f"2nd-lord {l2} in {s2}", 0.7)

    # 5. Mercury's natal sign + nakshatra-lord
    merc_sign = _planet_sign(chart, "Mercury")
    if merc_sign:
        for field in SIGN_FIELD_AFFINITY.get(merc_sign, []):
            _add(field, f"Mercury in {merc_sign}", 1.2)

    # 6. Saturn's sign + planet itself — long-discipline subject
    sat_sign = _planet_sign(chart, "Saturn")
    if sat_sign:
        for field in SIGN_FIELD_AFFINITY.get(sat_sign, []):
            _add(field, f"Saturn in {sat_sign} (the discipline subject)", 0.8)
    for field in PLANET_FIELD_AFFINITY.get("Saturn", []):
        _add(field, "Saturn (discipline/labor focus)", 0.6)

    # Aggregate
    out: list[SubjectSignal] = []
    for field, sources in scores.items():
        # parse weights from sources
        total = sum(float(s.rsplit("(+", 1)[1].rstrip(")"))
                    for s in sources)
        out.append(SubjectSignal(field=field, score=total, sources=sources))
    out.sort(key=lambda s: -s.score)
    return out[:top_n]


def render_education_markdown(chart) -> str:
    out = ["## ✦ Your Natural Subjects (what your chart says you should study)\n"]
    sigs = predict_subjects(chart, top_n=6)
    if not sigs:
        out.append("_Insufficient varga data to predict subjects._")
        return "\n".join(out)
    out.append(
        "The classical Vedic method for subject-prediction uses six "
        "channels: D24 (the education-varga) for Mercury and Jupiter, "
        "the 4th lord (formal schooling), 5th lord (intellect), "
        "2nd lord (speech), Mercury's natal sign, and Saturn's "
        "discipline-subject. Below are the fields where the most signals "
        "converge."
    )
    out.append("")
    out.append("| Rank | Field | Signal weight | Sources |")
    out.append("|---:|---|---:|---|")
    for i, sig in enumerate(sigs, 1):
        sources_short = "; ".join(s.rsplit(" (+", 1)[0] for s in sig.sources[:3])
        out.append(f"| {i} | **{sig.field}** | {sig.score:.1f} | {sources_short} |")
    out.append("")
    top = sigs[0]
    out.append(
        f"**The strongest single fit:** {top.field}. Multiple signals "
        f"converge here ({', '.join(s.rsplit(' (+', 1)[0] for s in top.sources[:4])}). "
        "If you have already studied something — verify whether it is "
        "near this list. If not, the chart is suggesting a different "
        "calling than your current path."
    )
    return "\n".join(out)
