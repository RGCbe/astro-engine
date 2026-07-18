"""
Lal Kitab engine — separate logic path from Parashari.

Lal Kitab (originally five Urdu volumes, 1939-1952) is incompatible with
Parashari Jyotish in three fundamental ways:

    1. **Fixed-house framework**: houses are tied to the natural zodiac
       (Aries=1, Taurus=2, …, Pisces=12) regardless of the rising sign.
       So "Mars in 1st" universally means "Mars in Aries", not "Mars in
       lagna sign".

    2. **Pakka ghar (permanent house)**: each planet has a fixed
       "permanent residence." A planet in its pakka ghar is at full
       strength; elsewhere, its effect is modified by the actual house.

    3. **Karmic debts (rin)**: specific malefic planet placements indicate
       debts owed to ancestors, mother, brothers, wife, or children.
       Remedies clear the debt rather than strengthen the planet.

This module exposes:
    - LAL_KITAB_PAKKA_GHAR — permanent house per planet
    - LAL_KITAB_ASPECTS    — different aspect table from Parashari
    - lal_kitab_chart(planets) — fixed-house framework
    - karmic_debts(chart)     — detected rins (5 types)
    - closed_houses(chart)    — houses rendered "asleep" by planetary combos
    - remedies_for(chart)     — recommended Lal Kitab remedies

Sources:
    - Lal Kitab original (Pt. Roop Chand Joshi, 1939) — extracted in
      /opt/astro/gemma_extractions/Lal_Kitab_Original_gemma.json
    - Lal Kitab Amrit (Krishan Ashant, modern English commentary)
    - U.C. Mahajan, "Lal Kitab — Predictions and Remedies"
"""
from __future__ import annotations

from dataclasses import dataclass, field

# Sign indices: 0=Aries .. 11=Pisces. Lal Kitab houses = sign index + 1.
SIGN_NAMES = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)


# ─── Pakka ghar (permanent residence) per planet ──────────────────────────
# Source: Lal Kitab Ch.2 ("Sthayi Ghar"), reaffirmed in Lal Kitab Amrit.
LAL_KITAB_PAKKA_GHAR: dict[str, int] = {
    "Sun":     1,   # Mesha — natural fire
    "Moon":    4,   # Karka — natural mother/home
    "Mars":    3,   # Mithuna position (3rd from natural — Lal Kitab idiom)
    "Mercury": 7,   # Tula — diplomacy/contracts
    "Jupiter": 2,   # Vrishabha — wealth/family lineage
    "Venus":   7,   # Tula — partnership
    "Saturn":  10,  # Makara — natural karma-house
    "Rahu":    12,  # Meena — moksha/loss/foreign
    "Ketu":    6,   # Kanya — service/disease
}


# ─── Lal Kitab aspect table ────────────────────────────────────────────────
# Lal Kitab aspects (drishti) differ from Parashari. Each planet aspects a
# specific set of houses *from* its own house. Asymmetric — Saturn aspects
# 3rd, 7th, 10th (drishti = Parashari Saturn), but Rahu aspects 5th, 7th, 9th
# (different from Parashari which gives Rahu 5/7/9 too — coincidentally the
# same in this respect; sources vary on Rahu).
LAL_KITAB_ASPECTS: dict[str, set[int]] = {
    "Sun":     {7},                  # Sun aspects opposite house only
    "Moon":    {7},
    "Mars":    {4, 7, 8},            # Mars: 4th, 7th, 8th
    "Mercury": {7},
    "Jupiter": {5, 7, 9},
    "Venus":   {7},
    "Saturn":  {3, 7, 10},
    "Rahu":    {5, 7, 9, 12},        # Rahu — extended aspects per Lal Kitab
    "Ketu":    {5, 7, 9},
}


# ─── Karmic debts (Rin) — canonical detection patterns ─────────────────────
# Pitra Rin (father's debt), Matra Rin (mother), Bhratra Rin (brothers),
# Patni/Stree Rin (wife), Putra Rin (children).
#
# Each rin is detected by a specific Lal Kitab combination. The patterns
# below are from Lal Kitab Ch.6 ("Karzdaar"), citing classical placements.
RIN_PATTERNS: list[dict] = [
    {
        "rin": "Pitra Rin",
        "name_hindi": "Pitru Rin (पितृ ऋण)",
        "english": "Ancestral / father's debt",
        # Sun, Jupiter, or Mercury in 9th house with malefic; OR Rahu/Ketu
        # in 9th; OR Sun in 6th/8th/12th with Rahu/Ketu/Saturn affliction.
        "trigger": "rahu_or_ketu_in_9 OR (sun_in_6_8_or_12 AND afflicted_by_rahu_ketu_saturn)",
        "remedy": (
            "Worship ancestors during pitru paksha; serve father; offer "
            "wheat & jaggery to a temple; never disrespect elders; avoid "
            "lying or fraud."
        ),
    },
    {
        "rin": "Matra Rin",
        "name_hindi": "Matru Rin (मातृ ऋण)",
        "english": "Mother's debt",
        # Moon afflicted in 6/8/12; OR Rahu in 4th house; OR Moon-Ketu
        # conjunction in any malefic house.
        "trigger": "rahu_in_4 OR (moon_in_6_8_or_12 AND afflicted_by_malefic) OR moon_ketu_conjunction",
        "remedy": (
            "Serve mother; donate silver/rice to women; never raise voice "
            "against mother; offer water at sacred rivers."
        ),
    },
    {
        "rin": "Bhratra Rin",
        "name_hindi": "Bhratru Rin (भ्रातृ ऋण)",
        "english": "Brothers' / siblings' debt",
        # Mars in 1st/8th with affliction; OR Rahu in 3rd house;
        # OR Mercury in 12th with malefic.
        "trigger": "rahu_in_3 OR (mars_in_1_or_8 AND afflicted) OR (mercury_in_12 AND afflicted)",
        "remedy": (
            "Maintain harmony with brothers; donate red lentils & sweets; "
            "avoid jealousy among siblings; help cousins when in need."
        ),
    },
    {
        "rin": "Stree Rin",
        "name_hindi": "Patni Rin (पत्नी ऋण)",
        "english": "Wife's / spouse's debt",
        # Venus afflicted in 7th; OR Rahu in 7th; OR Venus-Saturn or
        # Venus-Ketu conjunction in any house.
        "trigger": "rahu_in_7 OR (venus_in_7 AND afflicted) OR venus_saturn_conjunction OR venus_ketu_conjunction",
        "remedy": (
            "Treat spouse with respect; never insult women; donate white "
            "items (rice, milk, sugar); avoid extra-marital relations."
        ),
    },
    {
        "rin": "Putra Rin",
        "name_hindi": "Putra Rin (पुत्र ऋण)",
        "english": "Children's debt",
        # Jupiter afflicted in 5th; OR Rahu/Ketu in 5th;
        # OR Sun in 12th with malefic affliction.
        "trigger": "rahu_or_ketu_in_5 OR (jupiter_in_5 AND afflicted) OR (sun_in_12 AND afflicted)",
        "remedy": (
            "Respect children; donate yellow items (turmeric, gram dal) to "
            "Brahmins; serve cows; perform Vishnu-Sahasranama parayanam."
        ),
    },
    {
        "rin": "Nyaya Rin",
        "name_hindi": "Nyaya Rin (न्याय ऋण)",
        "english": "Justice / karmic-injustice debt",
        # Saturn afflicted in 1/4/7/10 (kendras); OR 6th lord very strong & 9th lord weak.
        # Marker of injustice committed in past births that must be repaid through
        # honest, hard, ethical service.
        "trigger": "saturn_debilitated_in_1_4_7_10 OR (lord_of_6_strong AND lord_of_9_weak)",
        "remedy": (
            "Avoid all dishonest acts; donate iron / black sesame on Saturdays; "
            "serve labourers, the poor, and disabled persons; uphold law in "
            "every dealing."
        ),
    },
    {
        "rin": "Atma Rin",
        "name_hindi": "Atma Rin (आत्म ऋण)",
        "english": "Self / soul debt",
        # Lagna lord debilitated; OR Saturn-Rahu-Ketu in 1st without benefic.
        "trigger": "lagna_lord_debilitated OR (saturn_or_rahu_or_ketu_in_1 AND no_benefic_in_1)",
        "remedy": (
            "Daily meditation; serve sadhus / sannyasis; consciously give up "
            "one bad habit; live with self-discipline."
        ),
    },
]


# ─── Closed/asleep house patterns ──────────────────────────────────────────
# Certain combinations render a house "soya hua" (asleep) — its significations
# do not manifest until activated by remedy or transit.
CLOSED_HOUSE_PATTERNS: list[dict] = [
    {"trigger": "rahu_in_4_with_no_benefic", "house_closed": 4,
     "meaning": "domestic peace asleep; mother's wellbeing affected"},
    {"trigger": "ketu_in_7_alone", "house_closed": 7,
     "meaning": "marriage karaka asleep; spouse delays / separation risk"},
    {"trigger": "saturn_with_sun_in_10", "house_closed": 10,
     "meaning": "career karaka asleep; recognition delayed despite work"},
    {"trigger": "mars_in_2_with_malefic", "house_closed": 2,
     "meaning": "speech & wealth asleep; family income blocked"},
]


# ─── Data classes ──────────────────────────────────────────────────────────
@dataclass
class LalKitabPlacement:
    planet: str
    sign_idx: int          # 0=Aries .. 11=Pisces — also the LK house number-1
    house: int             # 1..12 in Lal Kitab framework (= sign_idx + 1)
    pakka_ghar: int        # permanent house for this planet
    in_pakka: bool         # is the planet in its pakka ghar?
    aspects_houses: set[int]  # houses this planet aspects per Lal Kitab


@dataclass
class LalKitabChart:
    placements: list[LalKitabPlacement] = field(default_factory=list)
    karmic_debts: list[dict] = field(default_factory=list)
    closed_houses: list[dict] = field(default_factory=list)
    remedies: list[str] = field(default_factory=list)


# ─── Helpers ───────────────────────────────────────────────────────────────
def _planet_house(longitude_sidereal: float) -> int:
    """Lal Kitab house = sign of planet + 1 (Aries=1, …, Pisces=12)."""
    sign_idx = int((longitude_sidereal % 360) // 30)
    return sign_idx + 1


def _aspected_houses(planet: str, planet_house: int) -> set[int]:
    """Houses aspected by `planet` from `planet_house` per Lal Kitab table."""
    offsets = LAL_KITAB_ASPECTS.get(planet, set())
    return {((planet_house - 1 + (off - 1)) % 12) + 1 for off in offsets}


def _house_of(chart: list[LalKitabPlacement], planet: str) -> int | None:
    for p in chart:
        if p.planet == planet:
            return p.house
    return None


def _planets_in_house(chart: list[LalKitabPlacement], h: int) -> list[str]:
    return [p.planet for p in chart if p.house == h]


def _afflicted(chart: list[LalKitabPlacement], planet: str) -> bool:
    """Planet is afflicted if conjunct or aspected by Saturn/Mars/Rahu/Ketu."""
    p_house = _house_of(chart, planet)
    if p_house is None:
        return False
    malefics = {"Saturn", "Mars", "Rahu", "Ketu"}
    co_residents = set(_planets_in_house(chart, p_house)) - {planet}
    if co_residents & malefics:
        return True
    for m in malefics:
        m_house = _house_of(chart, m)
        if m_house and p_house in _aspected_houses(m, m_house):
            return True
    return False


# ─── Public API ────────────────────────────────────────────────────────────
def lal_kitab_chart(planet_longitudes: dict[str, float]) -> LalKitabChart:
    """Build the Lal Kitab fixed-house chart from sidereal planet longitudes.

    `planet_longitudes`: {"Sun": 60.5, "Moon": 132.1, ...} — sidereal degrees.
    """
    placements: list[LalKitabPlacement] = []
    for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                   "Venus", "Saturn", "Rahu", "Ketu"):
        if planet not in planet_longitudes:
            continue
        lon = planet_longitudes[planet]
        house = _planet_house(lon)
        sign_idx = house - 1
        pg = LAL_KITAB_PAKKA_GHAR[planet]
        placements.append(LalKitabPlacement(
            planet=planet,
            sign_idx=sign_idx,
            house=house,
            pakka_ghar=pg,
            in_pakka=(house == pg),
            aspects_houses=_aspected_houses(planet, house),
        ))

    debts = karmic_debts(placements)
    closed = closed_houses(placements)
    remedies = remedies_for(placements, debts, closed)

    return LalKitabChart(
        placements=placements,
        karmic_debts=debts,
        closed_houses=closed,
        remedies=remedies,
    )


def karmic_debts(chart: list[LalKitabPlacement]) -> list[dict]:
    """Detect the five rins from Lal Kitab placement patterns."""
    detected: list[dict] = []

    sun = _house_of(chart, "Sun")
    moon = _house_of(chart, "Moon")
    mars = _house_of(chart, "Mars")
    mercury = _house_of(chart, "Mercury")
    jupiter = _house_of(chart, "Jupiter")
    venus = _house_of(chart, "Venus")
    saturn = _house_of(chart, "Saturn")
    rahu = _house_of(chart, "Rahu")
    ketu = _house_of(chart, "Ketu")

    # Pitra Rin
    if rahu == 9 or ketu == 9 or (sun in (6, 8, 12) and _afflicted(chart, "Sun")):
        detected.append({**RIN_PATTERNS[0], "evidence":
            f"Sun H{sun}, Rahu H{rahu}, Ketu H{ketu}"})

    # Matra Rin
    moon_ketu_conj = (moon is not None and moon == ketu)
    if rahu == 4 or (moon in (6, 8, 12) and _afflicted(chart, "Moon")) or moon_ketu_conj:
        detected.append({**RIN_PATTERNS[1], "evidence":
            f"Moon H{moon}, Rahu H{rahu}, Ketu H{ketu}"})

    # Bhratra Rin
    if rahu == 3 or (mars in (1, 8) and _afflicted(chart, "Mars")) or \
       (mercury == 12 and _afflicted(chart, "Mercury")):
        detected.append({**RIN_PATTERNS[2], "evidence":
            f"Mars H{mars}, Mercury H{mercury}, Rahu H{rahu}"})

    # Stree Rin
    venus_saturn_conj = (venus is not None and venus == saturn)
    venus_ketu_conj = (venus is not None and venus == ketu)
    if rahu == 7 or (venus == 7 and _afflicted(chart, "Venus")) or \
       venus_saturn_conj or venus_ketu_conj:
        detected.append({**RIN_PATTERNS[3], "evidence":
            f"Venus H{venus}, Saturn H{saturn}, Rahu H{rahu}, Ketu H{ketu}"})

    # Putra Rin
    if rahu == 5 or ketu == 5 or \
       (jupiter == 5 and _afflicted(chart, "Jupiter")) or \
       (sun == 12 and _afflicted(chart, "Sun")):
        detected.append({**RIN_PATTERNS[4], "evidence":
            f"Jupiter H{jupiter}, Sun H{sun}, Rahu H{rahu}, Ketu H{ketu}"})

    return detected


def closed_houses(chart: list[LalKitabPlacement]) -> list[dict]:
    """Detect houses that are 'soya hua' (asleep) per Lal Kitab combinations."""
    detected: list[dict] = []
    benefics = {"Jupiter", "Venus", "Mercury", "Moon"}

    rahu_h = _house_of(chart, "Rahu")
    if rahu_h == 4:
        co = set(_planets_in_house(chart, 4))
        if not (co & benefics):
            detected.append({**CLOSED_HOUSE_PATTERNS[0],
                             "evidence": "Rahu in 4th, no benefic co-resident"})

    ketu_h = _house_of(chart, "Ketu")
    if ketu_h == 7:
        co = set(_planets_in_house(chart, 7)) - {"Ketu"}
        if not co:
            detected.append({**CLOSED_HOUSE_PATTERNS[1],
                             "evidence": "Ketu alone in 7th"})

    sun_h = _house_of(chart, "Sun")
    saturn_h = _house_of(chart, "Saturn")
    if sun_h == 10 and saturn_h == 10:
        detected.append({**CLOSED_HOUSE_PATTERNS[2],
                         "evidence": "Sun + Saturn conjunct in 10th"})

    mars_h = _house_of(chart, "Mars")
    if mars_h == 2:
        co = set(_planets_in_house(chart, 2)) - {"Mars"}
        if co & {"Saturn", "Rahu", "Ketu"}:
            detected.append({**CLOSED_HOUSE_PATTERNS[3],
                             "evidence": f"Mars + malefic in 2nd: {co}"})

    return detected


def remedies_for(
    chart: list[LalKitabPlacement],
    debts: list[dict],
    closed: list[dict],
) -> list[str]:
    """Aggregate Lal Kitab remedies from detected debts, closures, and weak placements."""
    out: list[str] = []
    for d in debts:
        out.append(f"[{d['rin']}] {d['remedy']}")

    # Generic remedies for closed houses
    closed_house_remedies = {
        4: "Place a silver vessel of milk in the home; serve mother; never break trust at home.",
        7: "Donate yellow items on Thursdays; respect spouse; offer water to peepal tree.",
        10: "Serve laborers / underprivileged; donate iron + black sesame on Saturdays.",
        2: "Recite Hanuman Chalisa daily; donate red lentils on Tuesdays; never lie about wealth.",
    }
    for c in closed:
        h = c["house_closed"]
        if h in closed_house_remedies:
            out.append(f"[Closed H{h}] {closed_house_remedies[h]}")

    # Pakka-ghar specific remedies for planets out of permanent residence
    out_of_pakka = [p for p in chart if not p.in_pakka and _afflicted(chart, p.planet)]
    pakka_remedies = {
        "Sun":     "Offer water to Sun at sunrise; donate wheat & jaggery on Sundays.",
        "Moon":    "Donate milk & rice on Mondays; never delay drinking water when thirsty.",
        "Mars":    "Plant a sweet-fruit tree; donate red lentils on Tuesdays.",
        "Mercury": "Feed parrots; donate green moong dal; avoid lying.",
        "Jupiter": "Apply saffron tilak; donate yellow items to Brahmins on Thursdays.",
        "Venus":   "Donate white items (rice, sugar) on Fridays; treat women with respect.",
        "Saturn":  "Light a mustard-oil lamp on Saturdays; serve the elderly & poor.",
        "Rahu":    "Donate barley to flowing water; keep a piece of silver with you.",
        "Ketu":    "Serve dogs; donate black-and-white items; meditate on Ganesha.",
    }
    for p in out_of_pakka:
        rem = pakka_remedies.get(p.planet)
        if rem:
            out.append(f"[{p.planet} weak in H{p.house}] {rem}")

    return out


def chart_summary(lk: LalKitabChart) -> dict:
    """JSON-serializable summary."""
    return {
        "framework": "Lal Kitab fixed-zodiac (Aries=1)",
        "placements": [
            {
                "planet": p.planet,
                "house": p.house,
                "sign": SIGN_NAMES[p.sign_idx],
                "pakka_ghar": p.pakka_ghar,
                "in_pakka_ghar": p.in_pakka,
                "aspects_houses": sorted(p.aspects_houses),
            }
            for p in lk.placements
        ],
        "karmic_debts": [
            {"rin": d["rin"], "english": d["english"],
             "evidence": d.get("evidence", ""), "remedy": d["remedy"]}
            for d in lk.karmic_debts
        ],
        "closed_houses": lk.closed_houses,
        "remedies": lk.remedies,
    }


# ─── Runtime dict-chart API (consolidated from runtime/lal_kitab.py) ────────
# These functions accept the JSON dict-based chart format used by
# runtime/engine_orchestrator.py and runtime/generate_report.py. The dict-API
# covers all 7 karz patterns (5 from engine + Nyaya Rin + Atma Rin from
# runtime, now unified into the canonical RIN_PATTERNS list above).

# Lal Kitab — 7 types of karz (ancestral debts) — runtime-friendly dict.
# Keys match the legacy display strings used by earlier callers; values
# pull trigger/remedy directly from the canonical RIN_PATTERNS list above
# so a single source of truth.
_RIN_BY_NAME = {rp["rin"]: rp for rp in RIN_PATTERNS}
LAL_KITAB_KARZ = {
    "Pitra Rin (paternal debt)": {
        "trigger": _RIN_BY_NAME["Pitra Rin"]["trigger"],
        "remedy":  _RIN_BY_NAME["Pitra Rin"]["remedy"],
    },
    "Matra Rin (maternal debt)": {
        "trigger": _RIN_BY_NAME["Matra Rin"]["trigger"],
        "remedy":  _RIN_BY_NAME["Matra Rin"]["remedy"],
    },
    "Stree Rin (wife's debt)": {
        "trigger": _RIN_BY_NAME["Stree Rin"]["trigger"],
        "remedy":  _RIN_BY_NAME["Stree Rin"]["remedy"],
    },
    "Bhratru Rin (brother's debt)": {
        "trigger": _RIN_BY_NAME["Bhratra Rin"]["trigger"],
        "remedy":  _RIN_BY_NAME["Bhratra Rin"]["remedy"],
    },
    "Putra Rin (children's debt)": {
        "trigger": _RIN_BY_NAME["Putra Rin"]["trigger"],
        "remedy":  _RIN_BY_NAME["Putra Rin"]["remedy"],
    },
    "Nyaya Rin (justice debt)": {
        "trigger": _RIN_BY_NAME["Nyaya Rin"]["trigger"],
        "remedy":  _RIN_BY_NAME["Nyaya Rin"]["remedy"],
    },
    "Atma Rin (self/soul debt)": {
        "trigger": _RIN_BY_NAME["Atma Rin"]["trigger"],
        "remedy":  _RIN_BY_NAME["Atma Rin"]["remedy"],
    },
}

_LK_DIGNITIES = {
    ("Sun","Aries"):"Exalted",("Sun","Libra"):"Debil",("Sun","Leo"):"Own",
    ("Moon","Taurus"):"Exalted",("Moon","Scorpio"):"Debil",("Moon","Cancer"):"Own",
    ("Mars","Capricorn"):"Exalted",("Mars","Cancer"):"Debil",
    ("Mars","Aries"):"Own",("Mars","Scorpio"):"Own",
    ("Mercury","Virgo"):"Exalted/Own",("Mercury","Pisces"):"Debil",
    ("Mercury","Gemini"):"Own",
    ("Jupiter","Cancer"):"Exalted",("Jupiter","Capricorn"):"Debil",
    ("Jupiter","Sagittarius"):"Own",("Jupiter","Pisces"):"Own",
    ("Venus","Pisces"):"Exalted",("Venus","Virgo"):"Debil",
    ("Venus","Taurus"):"Own",("Venus","Libra"):"Own",
    ("Saturn","Libra"):"Exalted",("Saturn","Aries"):"Debil",
    ("Saturn","Capricorn"):"Own",("Saturn","Aquarius"):"Own",
}


def detect_lal_kitab_karz(chart):
    """Detect active karz patterns from a dict-based chart.

    chart: {"positions": {planet: {"house": int, "rasi": str, ...}, ...},
            "lagna_lord": str (optional)}
    Returns: list of {"karz", "trigger", "remedy"} dicts (runtime-API shape).
    """
    pos = chart["positions"]

    detected: list[str] = []
    sun_h = pos["Sun"]["house"] if "Sun" in pos else None
    moon_h = pos["Moon"]["house"] if "Moon" in pos else None
    venus_h = pos["Venus"]["house"] if "Venus" in pos else None
    mars_h = pos["Mars"]["house"] if "Mars" in pos else None
    jupiter_h = pos["Jupiter"]["house"] if "Jupiter" in pos else None
    saturn_h = pos["Saturn"]["house"] if "Saturn" in pos else None

    # Pitra Rin
    if sun_h in (6, 12):
        detected.append("Pitra Rin (paternal debt)")
    elif "Sun" in pos and _LK_DIGNITIES.get(("Sun", pos["Sun"]["rasi"])) == "Debil":
        detected.append("Pitra Rin (paternal debt)")

    # Matra Rin
    if moon_h in (6, 8, 12):
        detected.append("Matra Rin (maternal debt)")
    elif "Moon" in pos and _LK_DIGNITIES.get(("Moon", pos["Moon"]["rasi"])) == "Debil":
        detected.append("Matra Rin (maternal debt)")

    # Stree Rin
    if venus_h in (6, 8, 12):
        detected.append("Stree Rin (wife's debt)")
    elif "Venus" in pos and _LK_DIGNITIES.get(("Venus", pos["Venus"]["rasi"])) == "Debil":
        detected.append("Stree Rin (wife's debt)")

    # Bhratru Rin
    if mars_h in (6, 8, 12):
        detected.append("Bhratru Rin (brother's debt)")

    # Putra Rin
    if jupiter_h in (6, 8, 12):
        detected.append("Putra Rin (children's debt)")
    elif "Jupiter" in pos and _LK_DIGNITIES.get(("Jupiter", pos["Jupiter"]["rasi"])) == "Debil":
        detected.append("Putra Rin (children's debt)")

    # Nyaya Rin
    if saturn_h in (1, 4, 7, 10) and "Saturn" in pos and \
       _LK_DIGNITIES.get(("Saturn", pos["Saturn"]["rasi"])) == "Debil":
        detected.append("Nyaya Rin (justice debt)")

    # Atma Rin
    asc_lord = chart.get("lagna_lord")
    if asc_lord and asc_lord in pos and \
       _LK_DIGNITIES.get((asc_lord, pos[asc_lord]["rasi"])) == "Debil":
        detected.append("Atma Rin (self/soul debt)")

    out = []
    for karz in detected:
        info = LAL_KITAB_KARZ.get(karz, {})
        out.append({
            "karz": karz,
            "trigger": info.get("trigger", ""),
            "remedy": info.get("remedy", ""),
        })
    return out


def asleep_planets(chart):
    """Lal Kitab 'asleep' (sote hue grah) detection on a dict-based chart.

    A planet is asleep when alone in its sign with no aspecting planet
    (Lal Kitab uses 7th-house aspect only, on top of co-residence).
    """
    pos = chart["positions"]
    asleep = []
    for p, pd in pos.items():
        h = pd["house"]
        others_in_house = [
            op for op, opd in pos.items() if op != p and opd["house"] == h
        ]
        seventh_h = ((h + 6 - 1) % 12) + 1
        aspecting = [
            op for op, opd in pos.items() if op != p and opd["house"] == seventh_h
        ]
        if not others_in_house and not aspecting:
            asleep.append(p)
    return asleep


def lal_kitab_summary(chart):
    """Runtime-API summary: detected karz + asleep planets + interpretation."""
    karz = detect_lal_kitab_karz(chart)
    asleep = asleep_planets(chart)
    return {
        "active_karz": karz,
        "asleep_planets": asleep,
        "interpretation": (
            f"{len(karz)} karz pattern(s) detected. "
            f"{len(asleep)} 'asleep' planets (need waking via Lal Kitab remedies)."
        ),
    }
