"""
Prashna — horary (question-time) chart engine.

Two traditions:
    Krishneeyam (Kerala school): question-time chart + signator analysis
                                  on the question's "house of meaning"
    KP Prashna  (sub-lord school): ruling planets at question moment +
                                  cuspal sub-lord verdict (yes/no)

Implemented (MVP):
    cast(question_dt, lat, lon, tz)            — chart at question moment
    significators(chart, house)                — Krishneeyam signator chain
    kp_verdict(chart, house, expected="yes")   — KP cuspal sub-lord yes/no
    ruling_planets(chart)                      — KP ruling planet set
    answer(question_dt, lat, lon, tz, house)   — combined verdict

Question→house mapping (standard Prashna Marga + KP):
    H1=self/health, H2=family/wealth, H3=siblings/courage, H4=home/mother,
    H5=children/learning, H6=enemy/litigation/disease, H7=marriage/spouse,
    H8=longevity/secrets, H9=fortune/dharma, H10=career/status,
    H11=gains/desires, H12=loss/foreign/expense.

Per the engine's truth-only directive, kp_verdict returns the actual sub-
lord verdict — never softens "no" into "perhaps yes."
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import swisseph as swe

from engine.kp_sublord import get_kp_position


def kp_sublord_at(longitude_degrees: float) -> str:
    return get_kp_position(longitude_degrees)["sub_lord"]

EPHE_PATH = "/opt/astro/ephe"
swe.set_ephe_path(EPHE_PATH)
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

SIGN_NAMES = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)
SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}
PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,
}

# Standard question→house mapping
QUESTION_HOUSE = {
    "self": 1, "health": 1, "vitality": 1,
    "wealth": 2, "family": 2, "savings": 2,
    "siblings": 3, "courage": 3, "short_travel": 3,
    "home": 4, "mother": 4, "vehicle": 4, "property": 4,
    "children": 5, "education": 5, "creativity": 5, "speculation": 5,
    "enemy": 6, "litigation": 6, "disease": 6, "loan": 6, "service_job": 6,
    "marriage": 7, "spouse": 7, "partnership": 7,
    "longevity": 8, "death": 8, "inheritance": 8, "secrets": 8,
    "fortune": 9, "dharma": 9, "guru": 9, "long_travel": 9,
    "career": 10, "status": 10, "promotion": 10,
    "gains": 11, "desires": 11, "elder_sibling": 11, "income": 11,
    "loss": 12, "foreign": 12, "expense": 12, "moksha": 12,
}


@dataclass
class PrashnaChart:
    question_dt: dt.datetime
    jd_ut: float
    lat: float
    lon: float
    lagna_lon: float
    lagna_sign: int
    cusps: list[float] = field(default_factory=list)
    positions: dict = field(default_factory=dict)   # planet → sidereal lon
    sublords: dict = field(default_factory=dict)    # planet → KP sub-lord
    cusp_sublords: list[str] = field(default_factory=list)


# ─── Chart casting ─────────────────────────────────────────────────────────
def cast(question_dt: dt.datetime, lat: float, lon: float, tz_hours: float) -> PrashnaChart:
    """Cast a Prashna chart at the question moment (place = querent's location)."""
    h = question_dt.hour + question_dt.minute / 60 + question_dt.second / 3600 - tz_hours
    jd = swe.julday(question_dt.year, question_dt.month, question_dt.day, h)

    cusps_arr, _ = swe.houses_ex(jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    cusps = [c % 360.0 for c in cusps_arr]
    lagna_lon = cusps[0]
    lagna_sign = int(lagna_lon // 30)

    positions = {}
    sublords = {}
    for name, pid in PLANET_IDS.items():
        pos, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        positions[name] = pos[0] % 360.0
        sublords[name] = kp_sublord_at(positions[name])
    positions["Ketu"] = (positions["Rahu"] + 180) % 360.0
    sublords["Ketu"] = kp_sublord_at(positions["Ketu"])

    cusp_sublords = [kp_sublord_at(c) for c in cusps]

    return PrashnaChart(
        question_dt=question_dt, jd_ut=jd, lat=lat, lon=lon,
        lagna_lon=lagna_lon, lagna_sign=lagna_sign,
        cusps=cusps, positions=positions,
        sublords=sublords, cusp_sublords=cusp_sublords,
    )


# ─── Significators (Krishneeyam) ───────────────────────────────────────────
def significators(chart: PrashnaChart, house: int) -> list[dict]:
    """Krishneeyam significator chain for `house` (1-12).

    Layers (ranked):
        L1: planets in the house
        L2: lord of the house
        L3: planets aspecting the house (basic Parashari aspects)
        L4: occupants of the house's nakshatra-lord's house (KP overlay)
    """
    # Sign occupying the cusp of `house`
    cusp_lon = chart.cusps[house - 1]
    cusp_sign = int(cusp_lon // 30)
    house_lord = SIGN_LORD[cusp_sign]

    # Planets in the house (occupants of cusp_sign)
    occupants = []
    for p, lon in chart.positions.items():
        if int(lon // 30) == cusp_sign:
            occupants.append(p)

    # Aspecting planets (Parashari basic — opposite house = 7th aspect for all,
    # plus Mars 4/8, Jupiter 5/9, Saturn 3/10)
    sign_aspects = {
        "Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7],
        "Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10],
        "Rahu": [5, 7, 9], "Ketu": [5, 7, 9],
    }
    aspecters = []
    for p, lon in chart.positions.items():
        p_sign = int(lon // 30)
        for offset in sign_aspects.get(p, [7]):
            if (p_sign + offset - 1) % 12 == cusp_sign:
                aspecters.append(p)
                break

    return [
        {"layer": "L1_occupants", "planets": occupants},
        {"layer": "L2_house_lord", "planets": [house_lord]},
        {"layer": "L3_aspecting",  "planets": aspecters},
    ]


# ─── KP cuspal sub-lord verdict ────────────────────────────────────────────
# In KP Prashna: the sub-lord of the cusp of the question's house must be
# a *significator* of either that house OR a friendly outcome house. If
# sub-lord signifies obstruction houses (6/8/12 from question house), answer
# is NO.

OBSTRUCTING_HOUSES = {1: [6,8,12], 2:[6,8,12], 4:[5,9,12], 5:[4,11], 6:[5,9,12],
                       7:[1,6,10], 8:[1,7,12], 9:[3,6,8,10,12],
                       10:[3,9,12], 11:[5,12], 12:[5,11]}


def kp_verdict(chart: PrashnaChart, house: int) -> dict:
    """Return KP yes/no verdict + reasoning based on cusp sub-lord."""
    cusp_sl = chart.cusp_sublords[house - 1]
    sl_lon = chart.positions.get(cusp_sl)
    sl_house = None
    if sl_lon is not None:
        sl_sign = int(sl_lon // 30)
        sl_house = ((sl_sign - chart.lagna_sign) % 12) + 1

    obstructing = OBSTRUCTING_HOUSES.get(house, [])
    favourable = [house] + [h for h in range(1, 13)
                            if h not in obstructing and h != house]

    if sl_house is None:
        return {
            "verdict": "INDETERMINATE",
            "cusp_sublord": cusp_sl,
            "reason": "Sub-lord position not computed",
        }

    if sl_house in obstructing:
        return {
            "verdict": "NO",
            "cusp_sublord": cusp_sl,
            "sublord_in_house": sl_house,
            "reason": f"Cusp sub-lord {cusp_sl} sits in H{sl_house} — "
                      f"obstructs H{house}'s significations",
        }
    if sl_house == house:
        return {
            "verdict": "STRONG YES",
            "cusp_sublord": cusp_sl,
            "sublord_in_house": sl_house,
            "reason": f"Cusp sub-lord {cusp_sl} sits in own house H{house} — "
                      f"strong promise",
        }
    return {
        "verdict": "YES" if sl_house in favourable[:6] else "WEAK YES",
        "cusp_sublord": cusp_sl,
        "sublord_in_house": sl_house,
        "reason": f"Cusp sub-lord {cusp_sl} in H{sl_house} — supports H{house}",
    }


# ─── Ruling planets (KP) ───────────────────────────────────────────────────
def ruling_planets(chart: PrashnaChart) -> list[str]:
    """KP ruling planets at the question moment.

    Standard KP set:
        1. Ascendant sign-lord
        2. Ascendant nakshatra-lord (star-lord of lagna)
        3. Ascendant sub-lord
        4. Moon sign-lord
        5. Moon nakshatra-lord
        6. Day-lord (weekday lord)
    """
    weekday_lords = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    py_wd = chart.question_dt.weekday()
    vedic_wd = (py_wd + 1) % 7
    day_lord = weekday_lords[vedic_wd]

    rps = []
    rps.append(SIGN_LORD[chart.lagna_sign])              # asc sign-lord
    # Nakshatra lord of lagna
    from engine.dasha import NAKSHATRA_LORDS_VIMSHOTTARI, NAKSHATRA_SPAN
    lagna_nak_idx = int(chart.lagna_lon // NAKSHATRA_SPAN) % len(NAKSHATRA_LORDS_VIMSHOTTARI)
    rps.append(NAKSHATRA_LORDS_VIMSHOTTARI[lagna_nak_idx])
    rps.append(chart.cusp_sublords[0])                   # asc sub-lord
    moon_lon = chart.positions["Moon"]
    rps.append(SIGN_LORD[int(moon_lon // 30)])           # moon sign-lord
    moon_nak_idx = int(moon_lon // NAKSHATRA_SPAN) % len(NAKSHATRA_LORDS_VIMSHOTTARI)
    rps.append(NAKSHATRA_LORDS_VIMSHOTTARI[moon_nak_idx])
    rps.append(day_lord)
    # Deduplicate preserving order
    seen = set()
    uniq = []
    for r in rps:
        if r not in seen:
            uniq.append(r); seen.add(r)
    return uniq


# ─── High-level answer ─────────────────────────────────────────────────────
def answer(
    question_dt: dt.datetime,
    lat: float,
    lon: float,
    tz_hours: float,
    house: int = None,
    topic: str = None,
) -> dict:
    """Produce a complete Prashna verdict for a topic or house."""
    if house is None and topic is None:
        raise ValueError("Provide either `house` (1-12) or `topic` (mapped key)")
    if house is None:
        topic_key = topic.lower().replace(" ", "_")
        if topic_key not in QUESTION_HOUSE:
            raise ValueError(
                f"Unknown topic '{topic}'. Known: {sorted(QUESTION_HOUSE)}"
            )
        house = QUESTION_HOUSE[topic_key]

    chart = cast(question_dt, lat, lon, tz_hours)
    sigs = significators(chart, house)
    verdict = kp_verdict(chart, house)
    rps = ruling_planets(chart)

    return {
        "question_moment": chart.question_dt.isoformat(),
        "house_questioned": house,
        "lagna": SIGN_NAMES[chart.lagna_sign],
        "kp_verdict": verdict,
        "krishneeyam_significators": sigs,
        "ruling_planets": rps,
        "moon_sublord": chart.sublords["Moon"],
        "interpretation_note": (
            "KP verdict is from the cusp sub-lord of the question's house. "
            "Krishneeyam significators give the supporting/obstructing chain. "
            "Ruling planets at the question moment indicate timing if 'YES'. "
            "Per the engine's truth-only directive, NO results are reported "
            "unsoftened."
        ),
    }
