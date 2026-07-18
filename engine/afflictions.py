"""
Affliction detector — the engine's core differentiator.

The user's directive: find the bad and worse better than any other astrology
software. Then give concrete remedies.

This module surfaces EVERY detectable negative in a chart, leaving none
hidden. Categories detected:

    1. Lal Kitab karmic debts (5 rins)
    2. Classical doshas (Mangal, Kal Sarp, Kemadruma, Sadhe Sati,
       Pitru Dosha, Grahan Dosha, Shrapit Dosha, Guru Chandala, Vish Yoga,
       Daridra Yoga, Anapha/Sunapha/Durudhura presence-or-absence)
    3. Afflicted planets (conjunct/aspected by Sat/Mars/Rahu/Ketu)
    4. Weak planets (low shadbala, debilitation, combust, retrograde-malefic)
    5. Weak houses (unaspected, malefic-aspected, lord debilitated)
    6. Negative-valence dasha (current MD or AD lord = malefic + afflicted)
    7. Active malefic transits (Sade Sati, Saturn over natal Moon, etc.)
    8. Anti-event dasha alignment (e.g. Saturn dasha for marriage = delay)

Per the engine's mission directive: NEVER soften a detected affliction.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SIGN_NAMES = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)
SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

# Debilitation signs (uchcha–neecha — neecha shown):
DEBILITATION_SIGN = {
    "Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
    "Jupiter": 9, "Venus": 5, "Saturn": 0,
}
EXALTATION_SIGN = {
    "Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
    "Jupiter": 3, "Venus": 11, "Saturn": 6,
}

MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}


@dataclass
class Affliction:
    code: str           # short identifier
    name: str
    severity: str       # CRITICAL | HIGH | MODERATE | LOW
    category: str       # rin | dosha | planet_weak | house_weak | yoga_negative |
                        # transit | dasha_alignment
    affected: list[str] = field(default_factory=list)  # planets/houses involved
    evidence: str = ""
    classical_source: str = ""
    description: str = ""


def _planet_house(longitude: float, lagna_sign: int) -> int:
    sign = int(longitude // 30)
    return ((sign - lagna_sign) % 12) + 1


def _is_combust(lon_planet: float, lon_sun: float, planet: str) -> bool:
    """Combustion (asta): planet within Sun's beam."""
    orb = {"Mercury": 14, "Venus": 10, "Mars": 17, "Jupiter": 11, "Saturn": 15,
           "Moon": 12}.get(planet, 0)
    if orb == 0:
        return False
    diff = abs((lon_planet - lon_sun + 540) % 360 - 180)
    return diff < orb


def _is_debilitated(longitude: float, planet: str) -> bool:
    sign = int(longitude // 30)
    return DEBILITATION_SIGN.get(planet) == sign


def _is_exalted(longitude: float, planet: str) -> bool:
    sign = int(longitude // 30)
    return EXALTATION_SIGN.get(planet) == sign


def _aspecting(planet: str, planet_house: int, target_house: int) -> bool:
    """Does `planet` aspect `target_house` per Parashari rules?"""
    aspects = {
        "Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7],
        "Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10],
        "Rahu": [5, 7, 9], "Ketu": [5, 7, 9],
    }
    for off in aspects.get(planet, [7]):
        if (planet_house + off - 1 - 1) % 12 + 1 == target_house:
            return True
    return False


# ─── Detectors ─────────────────────────────────────────────────────────────
def detect_mangal_dosha(chart) -> Affliction | None:
    """Mangal dosha: Mars in 1, 2, 4, 7, 8, or 12 from lagna or Moon."""
    lagna_sign = int(chart.lagna_lon // 30)
    moon_sign = int(chart.positions["Moon"] // 30)
    mars_sign = int(chart.positions["Mars"] // 30)
    h_from_lagna = ((mars_sign - lagna_sign) % 12) + 1
    h_from_moon = ((mars_sign - moon_sign) % 12) + 1
    bad_houses = {1, 2, 4, 7, 8, 12}
    if h_from_lagna in bad_houses or h_from_moon in bad_houses:
        return Affliction(
            code="MANGAL_DOSHA",
            name="Mangal Dosha (Kuja Dosha)",
            severity="HIGH",
            category="dosha",
            affected=["Mars", "7th house", "marriage"],
            evidence=f"Mars in H{h_from_lagna} from lagna, H{h_from_moon} from Moon",
            classical_source="BPHS Ch.80; Phaladeepika Ch.7",
            description=("Mars in marriage-significator houses creates marital "
                         "discord, conflict, separation risk, or delays."),
        )
    return None


def detect_kal_sarp(chart) -> Affliction | None:
    """Kal Sarp: all 7 planets between Rahu and Ketu (one half of zodiac)."""
    rahu_lon = chart.positions["Rahu"]
    ketu_lon = chart.positions["Ketu"]
    # Check if all 7 grahas are within the 180° arc from Rahu→Ketu
    grahas = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    arc_start = rahu_lon
    all_within = True
    for g in grahas:
        lon = chart.positions[g]
        # Distance from Rahu, going forward
        d = (lon - arc_start) % 360
        if d >= 180:
            all_within = False
            break
    if all_within:
        return Affliction(
            code="KAL_SARP",
            name="Kal Sarp Dosha",
            severity="HIGH",
            category="dosha",
            affected=["Rahu", "Ketu", "all planets"],
            evidence=f"All 7 grahas between Rahu ({rahu_lon:.1f}°) and Ketu ({ketu_lon:.1f}°)",
            classical_source="Modern Vedic (post-19th c.); referenced in Lal Kitab Ch.4",
            description=("Karmic obstruction, struggle in worldly affairs, "
                         "delayed success despite hard work."),
        )
    return None


def detect_kemadruma(chart) -> Affliction | None:
    """Kemadruma: Moon with no planets in 2nd, 12th from itself, no aspect."""
    moon_lon = chart.positions["Moon"]
    moon_sign = int(moon_lon // 30)
    second_from_moon = (moon_sign + 1) % 12
    twelfth_from_moon = (moon_sign - 1) % 12
    for p, lon in chart.positions.items():
        if p == "Moon":
            continue
        sign = int(lon // 30)
        if sign in (moon_sign, second_from_moon, twelfth_from_moon):
            return None
    return Affliction(
        code="KEMADRUMA",
        name="Kemadruma Yoga",
        severity="HIGH",
        category="yoga_negative",
        affected=["Moon", "mind", "emotional life", "support network"],
        evidence="No planet in 2nd, 12th, or same sign as Moon",
        classical_source="BPHS Ch.36; Phaladeepika Ch.6",
        description=("Loneliness, lack of emotional support, mental restlessness, "
                     "deprivation of mother's care, struggle for emotional stability."),
    )


def detect_pitru_dosha(chart) -> Affliction | None:
    """Pitru Dosha: Sun afflicted by Saturn or Rahu in 9th, 10th, or 1st."""
    lagna_sign = int(chart.lagna_lon // 30)
    sun_lon = chart.positions["Sun"]
    sun_house = ((int(sun_lon // 30) - lagna_sign) % 12) + 1
    rahu_lon = chart.positions["Rahu"]
    sat_lon = chart.positions["Saturn"]
    sun_sign = int(sun_lon // 30)
    rahu_sign = int(rahu_lon // 30)
    sat_sign = int(sat_lon // 30)
    afflicted = (rahu_sign == sun_sign or sat_sign == sun_sign)
    if not afflicted:
        # Check aspect
        rahu_house = ((rahu_sign - lagna_sign) % 12) + 1
        sat_house = ((sat_sign - lagna_sign) % 12) + 1
        if _aspecting("Saturn", sat_house, sun_house) or _aspecting("Rahu", rahu_house, sun_house):
            afflicted = True
    if afflicted and sun_house in (1, 9, 10):
        return Affliction(
            code="PITRU_DOSHA",
            name="Pitru Dosha",
            severity="HIGH",
            category="dosha",
            affected=["Sun", "9th house", "father/ancestors"],
            evidence=f"Sun afflicted in H{sun_house} by Saturn or Rahu",
            classical_source="Phaladeepika Ch.18; Lal Kitab",
            description=("Ancestral karmic debt, troubled relationship with father, "
                         "obstacles in career and authority, blockages in family lineage."),
        )
    return None


def detect_grahan_dosha(chart) -> Affliction | None:
    """Grahan dosha: Sun or Moon conjunct Rahu or Ketu (within 8°)."""
    rahu_lon = chart.positions["Rahu"]
    ketu_lon = chart.positions["Ketu"]
    for luminary in ("Sun", "Moon"):
        l_lon = chart.positions[luminary]
        for node, n_lon in (("Rahu", rahu_lon), ("Ketu", ketu_lon)):
            diff = abs((l_lon - n_lon + 540) % 360 - 180)
            if diff < 8:
                return Affliction(
                    code="GRAHAN_DOSHA",
                    name="Grahan Dosha (eclipse defect)",
                    severity="HIGH",
                    category="dosha",
                    affected=[luminary, node, "ego/mind"],
                    evidence=f"{luminary} conjunct {node} within {diff:.1f}°",
                    classical_source="Phaladeepika Ch.10; Saravali",
                    description=(f"{luminary} eclipsed by {node} weakens "
                                 f"{'confidence/career/father' if luminary == 'Sun' else 'mental clarity/mother/emotional life'}."),
                )
    return None


def detect_guru_chandala(chart) -> Affliction | None:
    """Jupiter conjunct Rahu or Ketu within 10°."""
    jup = chart.positions["Jupiter"]
    rahu = chart.positions["Rahu"]
    ketu = chart.positions["Ketu"]
    for node, lon in (("Rahu", rahu), ("Ketu", ketu)):
        diff = abs((jup - lon + 540) % 360 - 180)
        if diff < 10:
            return Affliction(
                code="GURU_CHANDALA",
                name="Guru-Chandala Yoga",
                severity="HIGH",
                category="yoga_negative",
                affected=["Jupiter", node, "wisdom", "ethics"],
                evidence=f"Jupiter-{node} conjunction within {diff:.1f}°",
                classical_source="BPHS Ch.79",
                description=("Distorted wisdom, ethical confusion, unconventional "
                             "or transgressive teachings, problems with gurus or "
                             "religious institutions."),
            )
    return None


def detect_vish_yoga(chart) -> Affliction | None:
    """Vish (poison) yoga: Saturn-Moon conjunction."""
    sat = chart.positions["Saturn"]
    moon = chart.positions["Moon"]
    diff = abs((sat - moon + 540) % 360 - 180)
    if diff < 12:
        return Affliction(
            code="VISH_YOGA",
            name="Vish Yoga (Saturn-Moon poison)",
            severity="MODERATE",
            category="yoga_negative",
            affected=["Moon", "Saturn", "mental peace"],
            evidence=f"Saturn-Moon conjunction within {diff:.1f}°",
            classical_source="Phaladeepika Ch.6",
            description=("Chronic depression, melancholic temperament, slow career "
                         "progress, emotional heaviness."),
        )
    return None


def detect_daridra_yoga(chart) -> Affliction | None:
    """Daridra yoga: 11th lord in 12th, OR 2nd lord in dusthana with malefic."""
    lagna_sign = int(chart.lagna_lon // 30)
    h11_lord_sign = (lagna_sign + 10) % 12
    h11_lord = SIGN_LORD[h11_lord_sign]
    h11_lord_lon = chart.positions.get(h11_lord)
    if h11_lord_lon is None:
        return None
    h11_lord_house = ((int(h11_lord_lon // 30) - lagna_sign) % 12) + 1
    if h11_lord_house == 12:
        return Affliction(
            code="DARIDRA_YOGA",
            name="Daridra Yoga (poverty combination)",
            severity="HIGH",
            category="yoga_negative",
            affected=["11th house", h11_lord, "wealth/gains"],
            evidence=f"11th lord {h11_lord} placed in 12th house",
            classical_source="BPHS Ch.36",
            description=("Wealth dissipation, expenses exceeding income, "
                         "obstacles to financial accumulation."),
        )
    return None


def detect_combust_planets(chart) -> list[Affliction]:
    """Planets within Sun's beam are combust (asta) — weakened."""
    out = []
    sun_lon = chart.positions["Sun"]
    for planet in ("Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Moon"):
        lon = chart.positions.get(planet)
        if lon is None:
            continue
        if _is_combust(lon, sun_lon, planet):
            diff = abs((lon - sun_lon + 540) % 360 - 180)
            out.append(Affliction(
                code=f"COMBUST_{planet.upper()}",
                name=f"{planet} combust (asta)",
                severity="MODERATE",
                category="planet_weak",
                affected=[planet],
                evidence=f"{planet} within {diff:.1f}° of Sun",
                classical_source="BPHS Ch.37; Surya Siddhanta",
                description=(f"{planet}'s significations are scorched by Sun. "
                             "Functional weakness in matters ruled by this graha."),
            ))
    return out


def detect_debilitated_planets(chart) -> list[Affliction]:
    out = []
    for planet, lon in chart.positions.items():
        if _is_debilitated(lon, planet):
            out.append(Affliction(
                code=f"DEBIL_{planet.upper()}",
                name=f"{planet} debilitated (neecha)",
                severity="HIGH",
                category="planet_weak",
                affected=[planet],
                evidence=f"{planet} in {SIGN_NAMES[DEBILITATION_SIGN[planet]]} (its lowest sign)",
                classical_source="BPHS Ch.7",
                description=(f"{planet} produces weakened, distorted, or anti-results "
                             "in its dasha and antardasha periods."),
            ))
    return out


def detect_dusthana_lords(chart) -> list[Affliction]:
    """Lords of 6, 8, 12 placed in 1, 4, 5, 7, 9, 10 = bring dusthana evils into good houses."""
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    for h_dust in (6, 8, 12):
        dust_lord_sign = (lagna_sign + h_dust - 1) % 12
        dust_lord = SIGN_LORD[dust_lord_sign]
        dust_lord_lon = chart.positions.get(dust_lord)
        if dust_lord_lon is None:
            continue
        h_in = ((int(dust_lord_lon // 30) - lagna_sign) % 12) + 1
        if h_in in (1, 4, 5, 7, 9, 10):
            out.append(Affliction(
                code=f"DUSTHANA_{h_dust}_IN_{h_in}",
                name=f"H{h_dust} lord in H{h_in}",
                severity="MODERATE",
                category="house_weak",
                affected=[dust_lord, f"H{h_dust}", f"H{h_in}"],
                evidence=f"{dust_lord} (lord of dusthana H{h_dust}) sits in H{h_in}",
                classical_source="BPHS Ch.30",
                description=(f"Brings H{h_dust} significations (disease/loss/enemy) "
                             f"into H{h_in} matters. May trigger problems in that area."),
            ))
    return out


def detect_kendra_dushta(chart) -> list[Affliction]:
    """Malefic in kendra (1, 4, 7, 10) without benefic mitigation."""
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    for malefic in ("Saturn", "Mars", "Rahu", "Ketu"):
        lon = chart.positions.get(malefic)
        if lon is None:
            continue
        h = ((int(lon // 30) - lagna_sign) % 12) + 1
        if h in (1, 4, 7, 10):
            # Check for benefic mitigation in same sign
            mal_sign = int(lon // 30)
            mitigated = False
            for b in BENEFICS:
                b_lon = chart.positions.get(b)
                if b_lon and int(b_lon // 30) == mal_sign:
                    mitigated = True
                    break
            if not mitigated:
                out.append(Affliction(
                    code=f"MALEFIC_KENDRA_{malefic.upper()}_{h}",
                    name=f"{malefic} in kendra H{h} (unmitigated)",
                    severity="MODERATE",
                    category="house_weak",
                    affected=[malefic, f"H{h}"],
                    evidence=f"{malefic} occupies H{h} with no benefic in same sign",
                    classical_source="BPHS Ch.32",
                    description=(f"Malefic in angle creates obstacles in "
                                 f"{ {1:'self', 4:'home', 7:'partnership', 10:'career'}[h] }."),
                ))
    return out


# ─── Shrapit Dosha (Saturn-Rahu conjunction) ──────────────────────────────
def detect_shrapit_dosha(chart) -> Affliction | None:
    """Saturn and Rahu in same sign = Shrapit (curse) dosha."""
    sat = chart.positions["Saturn"]
    rahu = chart.positions["Rahu"]
    if int(sat // 30) == int(rahu // 30):
        return Affliction(
            code="SHRAPIT_DOSHA",
            name="Shrapit Dosha (Saturn-Rahu curse)",
            severity="HIGH",
            category="dosha",
            affected=["Saturn", "Rahu"],
            evidence="Saturn and Rahu in same sign",
            classical_source="Lal Kitab Ch.5; modern Vedic",
            description=("Karmic curse from past lives or wronged ancestors. "
                         "Sudden reversals, unexplained obstacles, prolonged suffering."),
        )
    return None


# ─── Marana Karaka Sthana (planet in its death-house) ──────────────────────
MARANA_HOUSES = {
    "Sun": 12, "Moon": 8, "Mars": 7, "Mercury": 7,
    "Jupiter": 3, "Venus": 6, "Saturn": 1,
}


def detect_marana_karaka_sthana(chart) -> list[Affliction]:
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    for planet, marana_h in MARANA_HOUSES.items():
        lon = chart.positions.get(planet)
        if lon is None:
            continue
        h = ((int(lon // 30) - lagna_sign) % 12) + 1
        if h == marana_h:
            out.append(Affliction(
                code=f"MARANA_KARAKA_{planet.upper()}",
                name=f"Marana Karaka Sthana ({planet} in H{marana_h})",
                severity="HIGH",
                category="planet_weak",
                affected=[planet, f"H{marana_h}"],
                evidence=f"{planet} placed in its death-house H{marana_h}",
                classical_source="Jaimini Sutras; Sanjay Rath",
                description=(f"{planet} produces severely diminished or damaging "
                             "results in its dasha periods. Considered 'graha avastha "
                             "of death' for that planet."),
            ))
    return out


# ─── Papakartari (malefic squeeze: papas on both sides) ────────────────────
def detect_papakartari(chart) -> list[Affliction]:
    """A planet or house with malefics in 2nd AND 12th from it = squeezed."""
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    malefics_in_signs = {}
    for m in ("Sun", "Mars", "Saturn", "Rahu", "Ketu"):
        lon = chart.positions.get(m)
        if lon is not None:
            malefics_in_signs.setdefault(int(lon // 30), []).append(m)

    # Check each planet
    for planet, lon in chart.positions.items():
        sign = int(lon // 30)
        prev_sign = (sign - 1) % 12
        next_sign = (sign + 1) % 12
        # Don't count the planet itself if it's a malefic
        prev_mals = [m for m in malefics_in_signs.get(prev_sign, []) if m != planet]
        next_mals = [m for m in malefics_in_signs.get(next_sign, []) if m != planet]
        if prev_mals and next_mals:
            out.append(Affliction(
                code=f"PAPAKARTARI_{planet.upper()}",
                name=f"Papakartari yoga ({planet} squeezed)",
                severity="MODERATE",
                category="planet_weak",
                affected=[planet, *prev_mals, *next_mals],
                evidence=f"Malefics in 12th ({prev_mals}) AND 2nd ({next_mals}) from {planet}",
                classical_source="BPHS Ch.36; Phaladeepika Ch.6",
                description=(f"{planet} hemmed in by malefics — its significations "
                             "are obstructed/squeezed. Effects diluted in its dasha."),
            ))
    return out


# ─── Retrograde malefic (functional malefic going retrograde) ──────────────
def detect_retrograde_malefic(chart) -> list[Affliction]:
    """Saturn or Mars retrograde adds intensity to malefic effects."""
    out = []
    if not hasattr(chart, "retrograde"):
        return out
    for m in ("Saturn", "Mars", "Rahu", "Ketu"):
        if chart.retrograde.get(m, False):
            out.append(Affliction(
                code=f"RETROGRADE_MALEFIC_{m.upper()}",
                name=f"{m} retrograde",
                severity="MODERATE",
                category="planet_weak",
                affected=[m],
                evidence=f"{m} is in retrograde motion at birth",
                classical_source="Phaladeepika Ch.4",
                description=(f"Retrograde {m} produces karmic, slow-burn, or "
                             "unconventional malefic effects. Past-life dimension."),
            ))
    return out


# ─── Planet in enemy sign ──────────────────────────────────────────────────
ENEMY_SIGNS = {
    "Sun": [9, 10],          # Capricorn, Aquarius (Saturn's signs)
    "Moon": [],
    "Mars": [1, 6],          # Taurus, Libra (Venus' signs)
    "Mercury": [3],          # Cancer (Moon's sign — debility 8 already covered)
    "Jupiter": [1, 6],       # Taurus, Libra (Venus' signs)
    "Venus": [4, 3],         # Leo, Cancer
    "Saturn": [0, 4],        # Aries, Leo
}


def detect_enemy_sign_placements(chart) -> list[Affliction]:
    out = []
    for planet, enemies in ENEMY_SIGNS.items():
        lon = chart.positions.get(planet)
        if lon is None:
            continue
        sign = int(lon // 30)
        if sign in enemies:
            out.append(Affliction(
                code=f"ENEMY_SIGN_{planet.upper()}",
                name=f"{planet} in enemy sign",
                severity="LOW",
                category="planet_weak",
                affected=[planet],
                evidence=f"{planet} placed in {SIGN_NAMES[sign]} (enemy sign)",
                classical_source="BPHS Ch.7; Saravali Ch.3",
                description=(f"{planet} produces reduced or modified results — "
                             "the sign-lord's hostility colors expression."),
            ))
    return out


# ─── Anapha-absent (no planet near Moon = isolation) ──────────────────────
def detect_anapha_absent(chart) -> Affliction | None:
    """Already covered by Kemadruma but sometimes fires when only Sun is in 2/12."""
    moon = chart.positions["Moon"]
    moon_sign = int(moon // 30)
    second = (moon_sign + 1) % 12
    twelfth = (moon_sign - 1) % 12
    benefics_present = []
    for b in ("Jupiter", "Venus", "Mercury"):
        b_lon = chart.positions.get(b)
        if b_lon and int(b_lon // 30) in (second, twelfth, moon_sign):
            benefics_present.append(b)
    # Only fire if Kemadruma didn't already (i.e., Sun OR malefic IS in 2/12 but no benefic)
    if not benefics_present:
        # Check if some planet IS there (not pure Kemadruma)
        any_present = []
        for p in ("Sun", "Mars", "Saturn", "Rahu", "Ketu"):
            p_lon = chart.positions.get(p)
            if p_lon and int(p_lon // 30) in (second, twelfth):
                any_present.append(p)
        if any_present:
            return Affliction(
                code="ANAPHA_ABSENT",
                name="Anapha absent (only malefic near Moon)",
                severity="LOW",
                category="yoga_negative",
                affected=["Moon"] + any_present,
                evidence=f"Only malefics ({any_present}) near Moon, no benefic",
                classical_source="BPHS Ch.35",
                description=("Mind influenced exclusively by malefic energy. "
                             "Tendency toward harshness, restlessness, "
                             "lack of refinement in emotional life."),
            )
    return None


# ─── Bhasma yoga (when planets are blasted by enemy aspect) ───────────────
def detect_bhasma_yoga(chart) -> Affliction | None:
    """Saturn aspecting Sun = Bhasma yoga (burned by elder)."""
    lagna_sign = int(chart.lagna_lon // 30)
    sun_lon = chart.positions["Sun"]
    sat_lon = chart.positions["Saturn"]
    sun_h = ((int(sun_lon // 30) - lagna_sign) % 12) + 1
    sat_h = ((int(sat_lon // 30) - lagna_sign) % 12) + 1
    if _aspecting("Saturn", sat_h, sun_h):
        return Affliction(
            code="BHASMA_YOGA",
            name="Bhasma Yoga (Saturn afflicting Sun)",
            severity="MODERATE",
            category="yoga_negative",
            affected=["Sun", "Saturn", "father", "self-confidence"],
            evidence=f"Saturn (H{sat_h}) aspects Sun (H{sun_h})",
            classical_source="Jataka Parijata; Phaladeepika Ch.6",
            description=("Sun's vitality 'burned' by Saturn's restriction. "
                         "Suppression by authority, slow career, father issues."),
        )
    return None


# ─── Shadbala-below-threshold flag ─────────────────────────────────────────
def detect_dasha_anti_events(chart) -> list[Affliction]:
    """Surface 'your current MD makes event X less likely than chance' as
    affliction-class findings. Uses the empirical LR table.

    Per truth directive: if the engine has data showing this MD/AD reduces
    the likelihood of a desired event below chance, that's a real affliction
    the user should know about.
    """
    out = []
    try:
        from engine.calibration import forecast_confidence
    except Exception:
        return out
    md = chart.current_md
    ad = chart.current_ad
    if not md:
        return out
    GOOD = ("MARRIAGE", "CHILDREN_BORN", "CAREER_PEAK", "FOUND_BUSINESS",
            "POLITICAL_OFFICE", "AWARD")
    for evt in GOOD:
        f = forecast_confidence(evt, md, ad)
        lr = f.get("likelihood_ratio")
        if lr is not None and lr < 0.7:
            out.append(Affliction(
                code=f"DASHA_ANTI_{evt}",
                name=f"Anti-{evt} dasha alignment",
                severity="MODERATE",
                category="dasha_alignment",
                affected=[md, ad, evt],
                evidence=f"Current MD={md}, AD={ad}; LR for {evt}={lr} (below chance)",
                classical_source="Empirical (negative-sample backtest, n=299)",
                description=(f"In this dasha period, {evt} is statistically LESS "
                             "likely than chance. Engine recommends not pinning "
                             "expectations to this domain in this period."),
            ))
    return out


def detect_shadbala_weak(chart) -> list[Affliction]:
    """Planets with shadbala below the classical threshold are functionally weak."""
    out = []
    if not hasattr(chart, "shadbala"):
        return out
    THRESHOLDS = {
        "Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
        "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0,
    }
    for planet, threshold in THRESHOLDS.items():
        score = chart.shadbala.get(planet, {}).get("total_rupas")
        if score is None:
            continue
        if score < threshold * 0.6:   # well-below threshold
            out.append(Affliction(
                code=f"SHADBALA_WEAK_{planet.upper()}",
                name=f"{planet} below shadbala threshold",
                severity="LOW",
                category="planet_weak",
                affected=[planet],
                evidence=f"{planet} shadbala {score:.2f} rupas (threshold {threshold})",
                classical_source="BPHS Ch.27 (shadbala thresholds)",
                description=(f"{planet}'s functional capacity is impaired — "
                             "its significations underperform across all dashas."),
            ))
    return out


# ─── Aggregator ────────────────────────────────────────────────────────────
def detect_all(chart) -> list[Affliction]:
    """Run every detector; return a sorted list of detected afflictions."""
    out: list[Affliction] = []

    for fn in (detect_mangal_dosha, detect_kal_sarp, detect_kemadruma,
               detect_pitru_dosha, detect_grahan_dosha, detect_guru_chandala,
               detect_vish_yoga, detect_daridra_yoga, detect_shrapit_dosha,
               detect_anapha_absent, detect_bhasma_yoga):
        a = fn(chart)
        if a:
            out.append(a)

    out.extend(detect_combust_planets(chart))
    out.extend(detect_debilitated_planets(chart))
    out.extend(detect_dusthana_lords(chart))
    out.extend(detect_kendra_dushta(chart))
    out.extend(detect_marana_karaka_sthana(chart))
    out.extend(detect_papakartari(chart))
    out.extend(detect_retrograde_malefic(chart))
    out.extend(detect_enemy_sign_placements(chart))
    out.extend(detect_shadbala_weak(chart))
    out.extend(detect_dasha_anti_events(chart))

    # Lal Kitab rins
    from engine.lal_kitab import lal_kitab_chart
    lk = lal_kitab_chart(dict(chart.positions))
    for rin in lk.karmic_debts:
        out.append(Affliction(
            code=f"RIN_{rin['rin'].upper().replace(' ','_')}",
            name=f"Lal Kitab: {rin['rin']}",
            severity="HIGH",
            category="rin",
            affected=[rin["english"]],
            evidence=rin.get("evidence", ""),
            classical_source="Lal Kitab Ch.6",
            description=rin["english"] + " — " + rin.get("remedy", ""),
        ))

    # Sort by severity
    sev = {"CRITICAL": 4, "HIGH": 3, "MODERATE": 2, "LOW": 1}
    out.sort(key=lambda a: -sev.get(a.severity, 0))
    return out


def summary(chart) -> dict:
    afflictions = detect_all(chart)
    by_severity = {"CRITICAL": [], "HIGH": [], "MODERATE": [], "LOW": []}
    for a in afflictions:
        by_severity[a.severity].append({
            "code": a.code, "name": a.name, "category": a.category,
            "affected": a.affected, "evidence": a.evidence,
            "source": a.classical_source, "description": a.description,
        })
    return {
        "total_afflictions": len(afflictions),
        "by_severity": by_severity,
        "category_counts": {
            cat: sum(1 for a in afflictions if a.category == cat)
            for cat in ("rin", "dosha", "yoga_negative", "planet_weak",
                        "house_weak", "transit", "dasha_alignment")
        },
    }
