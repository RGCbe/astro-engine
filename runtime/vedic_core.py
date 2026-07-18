"""Vedic Core — shared constants and helpers used by all engine modules.

Single source of truth for RASIS, RASI_LORDS, DIGNITIES, NAKSHATRAS, planet lists, etc.
All engine modules SHOULD import from here. Existing modules with inline copies still work.
"""
# ============================================================
# SIGNS
# ============================================================
RASIS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]

RASI_SHORT = ["Ari","Tau","Gem","Can","Leo","Vir","Lib","Sco","Sag","Cap","Aqu","Pis"]

RASI_LORDS = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
              "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
              "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}

# Sign quality
MOVABLE_SIGNS = ["Aries","Cancer","Libra","Capricorn"]
FIXED_SIGNS   = ["Taurus","Leo","Scorpio","Aquarius"]
DUAL_SIGNS    = ["Gemini","Virgo","Sagittarius","Pisces"]

# Sign element
FIRE_SIGNS  = ["Aries","Leo","Sagittarius"]
EARTH_SIGNS = ["Taurus","Virgo","Capricorn"]
AIR_SIGNS   = ["Gemini","Libra","Aquarius"]
WATER_SIGNS = ["Cancer","Scorpio","Pisces"]

# Sign gender
MASCULINE_SIGN_IDX = {0, 2, 4, 6, 8, 10}  # Aries, Gemini, Leo, Libra, Sag, Aqu
FEMININE_SIGN_IDX  = {1, 3, 5, 7, 9, 11}

# ============================================================
# PLANETS
# ============================================================
PLANETS_MAIN = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
PLANETS_ALL = PLANETS_MAIN + ["Rahu","Ketu"]
NATURAL_BENEFICS = ["Moon","Mercury","Jupiter","Venus"]
NATURAL_MALEFICS = ["Sun","Mars","Saturn","Rahu","Ketu"]
MALE_PLANETS = ["Sun","Mars","Jupiter"]
FEMALE_PLANETS = ["Moon","Venus"]
NEUTRAL_PLANETS = ["Mercury","Saturn","Rahu","Ketu"]

# ============================================================
# DIGNITIES
# ============================================================
DIGNITIES = {
    ("Sun","Aries"):"Exalted",("Sun","Libra"):"Debil",("Sun","Leo"):"Own",
    ("Moon","Taurus"):"Exalted",("Moon","Scorpio"):"Debil",("Moon","Cancer"):"Own",
    ("Mars","Capricorn"):"Exalted",("Mars","Cancer"):"Debil",("Mars","Aries"):"Own",("Mars","Scorpio"):"Own",
    ("Mercury","Virgo"):"Exalted/Own",("Mercury","Pisces"):"Debil",("Mercury","Gemini"):"Own",
    ("Jupiter","Cancer"):"Exalted",("Jupiter","Capricorn"):"Debil",("Jupiter","Sagittarius"):"Own",("Jupiter","Pisces"):"Own",
    ("Venus","Pisces"):"Exalted",("Venus","Virgo"):"Debil",("Venus","Taurus"):"Own",("Venus","Libra"):"Own",
    ("Saturn","Libra"):"Exalted",("Saturn","Aries"):"Debil",("Saturn","Capricorn"):"Own",("Saturn","Aquarius"):"Own",
}

EXALTATION_SIGNS = {"Sun":"Aries","Moon":"Taurus","Mars":"Capricorn","Mercury":"Virgo",
                    "Jupiter":"Cancer","Venus":"Pisces","Saturn":"Libra"}

DEBILITATION_SIGNS = {"Sun":"Libra","Moon":"Scorpio","Mars":"Cancer","Mercury":"Pisces",
                      "Jupiter":"Capricorn","Venus":"Virgo","Saturn":"Aries"}

# ============================================================
# NAKSHATRAS (27 + Abhijit)
# ============================================================
NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya",
              "Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
              "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
              "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]

NAK_LORDS_27 = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"] * 3

# ============================================================
# VIMSHOTTARI
# ============================================================
VIMSHOTTARI_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
VIMSHOTTARI_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

# ============================================================
# HOUSES
# ============================================================
KENDRA_HOUSES = [1, 4, 7, 10]
TRIKONA_HOUSES = [1, 5, 9]
DUSTHANA_HOUSES = [6, 8, 12]
UPACHAYA_HOUSES = [3, 6, 10, 11]
MARAKA_HOUSES = [2, 7]
BAD_HOUSES = [6, 8, 12]
GOOD_HOUSES = [1, 2, 4, 5, 7, 9, 10, 11]

HOUSE_THEMES = {
    1:"self, body, personality",
    2:"wealth, family, speech, food",
    3:"siblings, courage, communication, short journeys",
    4:"home, mother, comforts, vehicles, education-foundation",
    5:"children, creativity, intelligence, romance, speculation",
    6:"work, enemies, health, debt, service",
    7:"spouse, partnerships, business, public-dealings",
    8:"transformation, occult, longevity, surgery, inheritance",
    9:"dharma, fortune, father, foreign, higher-learning",
    10:"career, fame, status, public-role, action",
    11:"gains, friends, elder-siblings, hopes-fulfilled",
    12:"loss, foreign, spirituality, expenses, liberation",
}

PLANET_ARCHETYPES = {
    "Sun":"father, authority, ego, leadership, government, soul",
    "Moon":"mother, mind, emotions, public, comforts",
    "Mars":"siblings, courage, energy, conflict, real estate, surgery",
    "Mercury":"intellect, speech, commerce, writing, communication",
    "Jupiter":"wisdom, dharma, children, wealth, expansion",
    "Venus":"spouse, luxury, arts, beauty, vehicles, comforts",
    "Saturn":"discipline, longevity, servants, delays, sorrow",
    "Rahu":"foreign, unconventional, technology, sudden gain",
    "Ketu":"spirituality, detachment, past karma, moksha",
}

# ============================================================
# COLOR PALETTE (for PDFs / UI)
# ============================================================
PLANET_COLOR_HEX = {
    "Sun":"#e07a1f","Moon":"#7798bd","Mars":"#b91c4f","Mercury":"#0d8a8a",
    "Jupiter":"#c9802a","Venus":"#d65a8c","Saturn":"#1f3a4a",
    "Rahu":"#3d4f7a","Ketu":"#5a3a8c"
}

PLANET_GLYPH = {"Sun":"☉","Moon":"☾","Mars":"♂","Mercury":"☿","Jupiter":"♃",
                "Venus":"♀","Saturn":"♄","Rahu":"☊","Ketu":"☋"}

# ============================================================
# COMMON HELPER FUNCTIONS
# ============================================================
def planet_house(chart, planet):
    """Get planet's house, or None."""
    return chart["positions"].get(planet, {}).get("house")


def planet_sign(chart, planet):
    return chart["positions"].get(planet, {}).get("rasi")


def planet_dignity(chart, planet):
    p = chart["positions"].get(planet)
    if not p: return "neutral"
    return DIGNITIES.get((planet, p["rasi"]), "neutral")


def is_dignified(chart, planet):
    return planet_dignity(chart, planet) in ["Own", "Exalted", "Exalted/Own"]


def is_debilitated(chart, planet):
    return planet_dignity(chart, planet) == "Debil"


def house_lord(chart, house):
    """Get the lord of nth house from chart's lagna."""
    lagna_idx = chart["lagna_idx"]
    sign = RASIS[(lagna_idx + house - 1) % 12]
    return RASI_LORDS[sign]


def house_lord_position(chart, house):
    """Get the house where the lord of nth house sits."""
    lord = house_lord(chart, house)
    return planet_house(chart, lord)


def house_occupants(chart, house):
    """List planets in given house."""
    return [p for p, pd in chart["positions"].items() if pd["house"] == house]


def house_sign(chart, house):
    """Sign of nth house."""
    lagna_idx = chart["lagna_idx"]
    return RASIS[(lagna_idx + house - 1) % 12]


def planet_aspects_houses(chart, planet):
    """Return list of houses aspected by `planet` (Vedic special aspects)."""
    h = planet_house(chart, planet)
    if h is None: return []
    if planet == "Jupiter":
        return [((h+4-1)%12)+1, ((h+6-1)%12)+1, ((h+8-1)%12)+1]
    if planet == "Mars":
        return [((h+3-1)%12)+1, ((h+6-1)%12)+1, ((h+7-1)%12)+1]
    if planet == "Saturn":
        return [((h+2-1)%12)+1, ((h+6-1)%12)+1, ((h+9-1)%12)+1]
    if planet in ["Rahu", "Ketu"]:
        return [((h+4-1)%12)+1, ((h+6-1)%12)+1, ((h+8-1)%12)+1]
    return [((h+6-1)%12)+1]  # 7th aspect for everyone else


def is_natural_benefic(planet):
    return planet in NATURAL_BENEFICS


def is_natural_malefic(planet):
    return planet in NATURAL_MALEFICS


# ============================================================
# FUNCTIONAL LORDSHIPS (BPHS)
# ============================================================
# Functional Benefics and Malefics based on Lagna (0=Aries, 11=Pisces)
FUNCTIONAL_BENEFICS = {
    0: ["Sun", "Moon", "Jupiter", "Mars"],
    1: ["Sun", "Saturn", "Mercury", "Mars"], # Mars is often considered neutral but sometimes benefic
    2: ["Venus"],
    3: ["Mars", "Jupiter", "Moon"],
    4: ["Mars", "Sun", "Jupiter"],
    5: ["Venus"],
    6: ["Saturn", "Mercury", "Venus"],
    7: ["Jupiter", "Moon", "Sun", "Mars"],
    8: ["Mars", "Sun"],
    9: ["Venus", "Mercury", "Saturn"],
    10: ["Venus", "Saturn", "Sun"],
    11: ["Mars", "Moon", "Jupiter"]
}

FUNCTIONAL_MALEFICS = {
    0: ["Mercury", "Venus", "Saturn"],
    1: ["Jupiter", "Venus", "Moon"],
    2: ["Mars", "Jupiter", "Sun"],
    3: ["Venus", "Mercury", "Saturn"],
    4: ["Mercury", "Venus", "Saturn"],
    5: ["Mars", "Jupiter", "Moon"],
    6: ["Jupiter", "Sun", "Mars"],
    7: ["Mercury", "Venus", "Saturn"],
    8: ["Venus", "Saturn", "Mercury"],
    9: ["Mars", "Jupiter", "Moon"],
    10: ["Jupiter", "Moon", "Mars"],
    11: ["Sun", "Venus", "Saturn", "Mercury"]
}

def is_functional_benefic(chart, planet):
    lagna_idx = chart.get("lagna_idx", 0)
    return planet in FUNCTIONAL_BENEFICS.get(lagna_idx, [])

def is_functional_malefic(chart, planet):
    lagna_idx = chart.get("lagna_idx", 0)
    return planet in FUNCTIONAL_MALEFICS.get(lagna_idx, [])


def planets_conjunct(chart, p1, p2):
    """Are two planets in same sign?"""
    pos = chart["positions"]
    if p1 not in pos or p2 not in pos: return False
    return pos[p1]["rasi_idx"] == pos[p2]["rasi_idx"]


def degree_distance(deg1, deg2):
    """Shortest angular distance between two longitudes (0-180°)."""
    diff = abs(deg1 - deg2) % 360
    return min(diff, 360 - diff)


# ============================================================
# TAMIL-SANSKRIT-INTEGER MAPPING TABLES
# (Bidirectional translation utilities — engine/ files use Tamil names
#  e.g. "Mesham", "Rishabam"; engine/* SIGN_LORD dicts use integer keys
#  0..11. These maps allow safe imports without forcing renames.)
# ============================================================
RASIS_TAMIL = ["Mesham","Rishabam","Mithunam","Kadagam","Simmam","Kanni",
               "Thulaam","Viruchigam","Dhanusu","Makaram","Kumbam","Meenam"]

RASI_TAMIL_TO_ENGLISH = dict(zip(RASIS_TAMIL, RASIS))
RASI_ENGLISH_TO_TAMIL = dict(zip(RASIS, RASIS_TAMIL))

# Integer-indexed (0=Aries..11=Pisces) — used by engine/*
SIGN_LORD_BY_INDEX = {i: RASI_LORDS[r] for i, r in enumerate(RASIS)}

# Tamil-keyed — used by engine/yogas.py, engine/shadbala.py, engine/chart.py
SIGN_LORDS_TAMIL = {tamil: RASI_LORDS[en] for en, tamil in RASI_ENGLISH_TO_TAMIL.items()}
EXALTATION_TAMIL = {p: RASI_ENGLISH_TO_TAMIL[s] for p, s in EXALTATION_SIGNS.items()}
DEBILITATION_TAMIL = {p: RASI_ENGLISH_TO_TAMIL[s] for p, s in DEBILITATION_SIGNS.items()}

# Sanskrit/Hindi planet aliases — never auto-rename, just provide map
PLANET_ENGLISH_TO_SANSKRIT = {
    "Sun":"Surya","Moon":"Chandra","Mars":"Mangala","Mercury":"Budha",
    "Jupiter":"Guru","Venus":"Shukra","Saturn":"Shani","Rahu":"Rahu","Ketu":"Ketu"
}
PLANET_SANSKRIT_TO_ENGLISH = {v: k for k, v in PLANET_ENGLISH_TO_SANSKRIT.items()}

# Spelling variants of the 27 nakshatras (alternate transliterations
# observed in engine/chart.py — kept here as reference, NOT enforced).
# vedic_core.NAKSHATRAS uses ("Ashwini","Mrigashira") — engine uses ("Ashvini","Mrigashirsha").
NAKSHATRA_ALIASES = {
    "Ashwini":"Ashvini","Mrigashira":"Mrigashirsha",
}
NAKSHATRA_ALIASES_INVERSE = {v: k for k, v in NAKSHATRA_ALIASES.items()}


# ============================================================
# VERSION
# ============================================================
ENGINE_VERSION = "v13.0"
ENGINE_BUILD = "2026-05-05"
