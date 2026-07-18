"""
Synth — the chart synthesizer.

Combines positions + houses + lordships + karakas into structured ChartFact
tuples that downstream engines (timeline, narrative, feedback) can compose
without re-doing the joins.

Single source of truth for "what does <planet> mean in <this chart>".
"""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.engines import SIGNS, SIGN_LORD


# ─── Reference tables ─────────────────────────────────────────────────────

PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
           "Venus", "Saturn", "Rahu", "Ketu")

# What each planet signifies (karaka roles). Used by timeline.py to assign
# life-areas to a dasha.
KARAKA: dict[str, list[str]] = {
    "Sun":     ["father", "self_authority", "government", "career_authority",
                "bones", "pride", "ego"],
    "Moon":    ["mother", "mind", "emotions", "public", "fluids",
                "comfort_home"],
    "Mars":    ["siblings_younger", "land_property", "courage", "energy",
                "blood", "real_estate", "engineering", "military"],
    "Mercury": ["communication", "business", "education_intellect",
                "writing", "skin", "trade", "analytics"],
    "Jupiter": ["wisdom", "children", "guru_teacher", "wealth",
                "dharma", "spouse_for_woman", "expansion"],
    "Venus":   ["spouse", "luxury", "vehicles", "creativity",
                "arts", "comforts", "relationships"],
    "Saturn":  ["service_employer", "longevity", "discipline",
                "labour", "delays", "older_people", "responsibility"],
    "Rahu":    ["foreign_lands", "ambition", "novelty", "obsession",
                "technology", "outsider", "intoxicants"],
    "Ketu":    ["spirituality", "loss", "hidden_skills", "moksha",
                "research", "occult", "detachment"],
}

# Bhava significations (which life areas a house governs).
BHAVA_AREAS: dict[int, list[str]] = {
    1:  ["self", "body", "appearance", "vitality"],
    2:  ["family", "speech", "wealth_accumulated", "food"],
    3:  ["siblings", "courage", "communication", "short_travel"],
    4:  ["mother", "home", "property", "vehicles", "comfort"],
    5:  ["children", "creativity", "education", "speculation",
         "ancestral_merit"],
    6:  ["service", "enemies", "disease", "debt", "daily_work"],
    7:  ["spouse", "partnership", "business_partner", "open_enemies",
         "foreign_residence"],
    8:  ["longevity", "occult", "inheritance", "transformation",
         "sudden_events"],
    9:  ["father", "fortune", "dharma", "guru", "long_travel",
         "higher_learning"],
    10: ["career", "status", "fame", "public_role"],
    11: ["gains", "income", "elder_siblings", "friends_network"],
    12: ["loss", "expense", "foreign", "moksha", "bed_pleasures"],
}

# Vedic full aspects (drishti). Every planet aspects 7th; specials below.
SPECIAL_ASPECTS: dict[str, tuple[int, ...]] = {
    "Mars":    (4, 7, 8),
    "Jupiter": (5, 7, 9),
    "Saturn":  (3, 7, 10),
    "Rahu":    (5, 7, 9),   # Rahu/Ketu treated like Jupiter (some traditions)
    "Ketu":    (5, 7, 9),
}

# Friendship tables → dignity scoring
EXALTATION = {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
              "Mercury": "Virgo", "Jupiter": "Cancer",
              "Venus": "Pisces", "Saturn": "Libra"}
DEBILITATION = {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
                "Mercury": "Pisces", "Jupiter": "Capricorn",
                "Venus": "Virgo", "Saturn": "Aries"}
OWN_SIGNS = {
    "Sun": ("Leo",), "Moon": ("Cancer",),
    "Mars": ("Aries", "Scorpio"),
    "Mercury": ("Gemini", "Virgo"),
    "Jupiter": ("Sagittarius", "Pisces"),
    "Venus": ("Taurus", "Libra"),
    "Saturn": ("Capricorn", "Aquarius"),
}


# ─── Data class ───────────────────────────────────────────────────────────

@dataclass
class ChartFact:
    """Everything the engine knows about one planet in one chart."""
    planet: str
    house: int
    sign: str
    nakshatra: str
    pada: int
    karaka_roles: list[str]              # from KARAKA[planet]
    bhavas_owned: list[int] = field(default_factory=list)  # houses where this planet is sign-lord
    bhava_areas: list[str] = field(default_factory=list)   # union of BHAVA_AREAS for owned + occupied
    dignity: str = "neutral"             # exalted / debilitated / own / neutral
    conjunctions: list[str] = field(default_factory=list)
    aspected_by: list[str] = field(default_factory=list)
    aspects_to: list[str] = field(default_factory=list)
    is_combust: bool = False
    is_retrograde: bool = False
    activates_when: list[tuple[str, str]] = field(default_factory=list)
    # life_areas — fully-merged list of life domains this planet activates
    life_areas: list[str] = field(default_factory=list)


# ─── Builders ─────────────────────────────────────────────────────────────

def _bhavas_owned(chart, planet: str) -> list[int]:
    """Houses (1..12) where this planet is the sign-lord, from the lagna."""
    out: list[int] = []
    lagna_idx = int(chart.lagna_lon // 30)
    for h in range(1, 13):
        sign_idx = (lagna_idx + h - 1) % 12
        if SIGN_LORD[sign_idx] == planet:
            out.append(h)
    return out


def _dignity(planet: str, sign: str) -> str:
    if EXALTATION.get(planet) == sign:
        return "exalted"
    if DEBILITATION.get(planet) == sign:
        return "debilitated"
    if sign in OWN_SIGNS.get(planet, ()):
        return "own"
    return "neutral"


def _aspects_from(chart, aspector: str) -> list[str]:
    """Planets this `aspector` casts an aspect on."""
    h_a = chart.house_of.get(aspector)
    if h_a is None:
        return []
    out: list[str] = []
    aspect_houses = {7}
    aspect_houses.update(SPECIAL_ASPECTS.get(aspector, ()))
    for p in PLANETS:
        if p == aspector:
            continue
        h_p = chart.house_of.get(p)
        if h_p is None:
            continue
        diff = ((h_p - h_a) % 12) + 1
        if diff in aspect_houses:
            out.append(p)
    return out


def _conjunctions(chart, planet: str) -> list[str]:
    h = chart.house_of.get(planet)
    if h is None:
        return []
    return [p for p in PLANETS
            if p != planet and chart.house_of.get(p) == h]


def _is_combust(chart, planet: str) -> bool:
    """Within ~6° of Sun (excluding Sun itself)."""
    if planet == "Sun":
        return False
    sun = chart.positions.get("Sun")
    p = chart.positions.get(planet)
    if sun is None or p is None:
        return False
    diff = abs(((p - sun + 180) % 360) - 180)
    return diff < 6.0


def _build_fact(chart, planet: str) -> ChartFact:
    house = chart.house_of.get(planet, 0)
    sign_idx = int(chart.positions[planet] // 30) if planet in chart.positions else 0
    sign = SIGNS[sign_idx]
    nak_info = (chart.nakshatras or {}).get(planet, {})
    nakshatra = nak_info.get("name", "")
    pada = int(nak_info.get("pada", 0))

    bhavas_owned = _bhavas_owned(chart, planet)
    bhava_areas: list[str] = []
    if house:
        bhava_areas.extend(BHAVA_AREAS.get(house, []))
    for b in bhavas_owned:
        bhava_areas.extend(BHAVA_AREAS.get(b, []))
    # de-dupe but keep order
    seen: set[str] = set()
    bhava_areas = [a for a in bhava_areas if not (a in seen or seen.add(a))]

    karaka_roles = list(KARAKA.get(planet, []))

    # life_areas = karaka ∪ bhava_areas (full life-domain footprint)
    life_areas: list[str] = []
    seen2: set[str] = set()
    for x in karaka_roles + bhava_areas:
        if x not in seen2:
            seen2.add(x); life_areas.append(x)

    return ChartFact(
        planet=planet,
        house=house,
        sign=sign,
        nakshatra=nakshatra,
        pada=pada,
        karaka_roles=karaka_roles,
        bhavas_owned=bhavas_owned,
        bhava_areas=bhava_areas,
        dignity=_dignity(planet, sign),
        conjunctions=_conjunctions(chart, planet),
        aspected_by=[p for p in PLANETS if p != planet
                     and planet in _aspects_from(chart, p)],
        aspects_to=_aspects_from(chart, planet),
        is_combust=_is_combust(chart, planet),
        life_areas=life_areas,
    )


def synthesize(chart) -> dict[str, ChartFact]:
    """Build a ChartFact for every planet. Pure function — call it once."""
    return {p: _build_fact(chart, p) for p in PLANETS
            if p in chart.house_of}


# ─── Convenience lookups ──────────────────────────────────────────────────

def fact(chart, planet: str) -> ChartFact:
    return _build_fact(chart, planet)


def planets_for_area(chart, area: str) -> list[str]:
    """All planets that activate the given life-area (e.g. 'father', 'children')."""
    facts = synthesize(chart)
    return [p for p, f in facts.items() if area in f.life_areas]


def lord_of(chart, house: int) -> str:
    """Sign-lord of the Nth house from lagna."""
    sign_idx = (int(chart.lagna_lon // 30) + house - 1) % 12
    return SIGN_LORD[sign_idx]
