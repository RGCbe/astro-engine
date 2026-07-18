"""Avasthas Engine — 4 classical planetary states for every planet on every chart.

Source traditions:
  - Phaladeepika Ch. 8 (Mantreswara) — Baladi, Lajjitadi
  - Brihat Parashara Hora Shastra (BPHS) Ch. 45 — Jagradadi, Deeptadi
  - Sarvartha Chintamani (Venkatesa Sharma) — corroborates Lajjitadi
  - Saravali Ch. 4 — corroborates Deeptadi 9-state

Implements 4 avastha systems:

  1. BALADI (5-state) — life-stage by degree-in-sign
       Bala (child)    : 0-6   deg, 25%  strength
       Kumara (youth)  : 6-12  deg, 50%
       Yuva (adult)    : 12-18 deg, 100% (peak)
       Vriddha (old)   : 18-24 deg, 50%
       Mrita (dead)    : 24-30 deg, 25%
     Note: order REVERSES for even signs (per Phaladeepika 8.1).

  2. JAGRADADI (3-state) — wakefulness via dignity
       Jagrat (awake)   : own/exalted    100%
       Swapna (dream)   : friend/neutral 50%
       Sushupta (sleep) : enemy/debil    25%

  3. DEEPTADI (9-state) — extended dignity + retro/combust/war
       Deepta, Swastha, Pramudita, Shanta, Shakta,
       Peedita, Deena, Vikala, Khala

  4. LAJJITADI (6-state) — interactive/contextual
       Lajjita, Garvita, Kshudita, Trishita, Mudita, Kshobhita

All return well-typed dicts with keys: state, strength_pct, meaning, source.
Module is SELF-CONTAINED (only imports vedic_core + stdlib).
"""
import sys, json
sys.path.insert(0, ".")

from vedic_core import (
    RASIS, RASI_LORDS, DIGNITIES, EXALTATION_SIGNS, DEBILITATION_SIGNS,
    PLANETS_MAIN, PLANETS_ALL, NATURAL_BENEFICS, NATURAL_MALEFICS,
    WATER_SIGNS, MASCULINE_SIGN_IDX,
    planet_house, planet_sign, planet_dignity, is_dignified, is_debilitated,
    planets_conjunct,
)

# ============================================================
# CLASSICAL CONSTANTS
# ============================================================

# Combust thresholds (per Phaladeepika 5.20-23 and BPHS 26.6).
# Distance from Sun in degrees within which planet is "asta" (combust / Vikala).
# Different schools have minor variations; we follow Phaladeepika's standard.
COMBUST_ORB = {
    "Moon":    12.0,   # some authorities use 12, BPHS says 12
    "Mars":    17.0,   # Phaladeepika 5.21 — 17 deg
    "Mercury": 14.0,   # 14 if direct, 12 if retrograde — we use 14 default
    "Jupiter": 11.0,
    "Venus":   10.0,   # 10 if direct, 8 if retrograde — we use 10 default
    "Saturn":  15.0,
}
# Note: Phaladeepika gives slightly different numbers (Moon=12, Mars=17, Mer=14,
# Jup=11, Ven=10, Sat=15). Surya Siddhanta + Siddhanta Shiromani give other values.
# We follow Phaladeepika as it's the most widely cited in modern Vedic practice.

# Planetary friendships (naisargika maitri — natural relationships)
# Source: BPHS Ch. 3.55-56, Phaladeepika 2.21-23
NAISARGIKA_FRIENDS = {
    "Sun":     {"Moon", "Mars", "Jupiter"},
    "Moon":    {"Sun", "Mercury"},
    "Mars":    {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus":   {"Mercury", "Saturn"},
    "Saturn":  {"Mercury", "Venus"},
    "Rahu":    {"Venus", "Saturn", "Mercury"},  # per Lal Kitab + standard usage
    "Ketu":    {"Mars", "Venus", "Saturn"},
}

NAISARGIKA_ENEMIES = {
    "Sun":     {"Venus", "Saturn"},
    "Moon":    set(),  # Moon has no natural enemy per BPHS
    "Mars":    {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus":   {"Sun", "Moon"},
    "Saturn":  {"Sun", "Moon", "Mars"},
    "Rahu":    {"Sun", "Moon", "Mars"},
    "Ketu":    {"Sun", "Moon"},
}

NAISARGIKA_NEUTRALS = {
    "Sun":     {"Mercury"},
    "Moon":    {"Mars", "Jupiter", "Venus", "Saturn", "Mercury"},
    "Mars":    {"Venus", "Saturn"},
    "Mercury": {"Mars", "Jupiter", "Saturn"},
    "Jupiter": {"Saturn"},
    "Venus":   {"Mars", "Jupiter"},
    "Saturn":  {"Jupiter"},
    "Rahu":    {"Jupiter"},
    "Ketu":    {"Mercury", "Jupiter"},
}

# Mooltrikona signs (per BPHS 3.20)
MOOLATRIKONA = {
    "Sun":     "Leo",          # 0-20 deg
    "Moon":    "Taurus",       # 4-30 deg (some say Cancer 0-3 then Tau 3-30)
    "Mars":    "Aries",        # 0-12 deg
    "Mercury": "Virgo",        # 16-20 deg
    "Jupiter": "Sagittarius",  # 0-10 deg
    "Venus":   "Libra",        # 0-15 deg
    "Saturn":  "Aquarius",     # 0-20 deg
}

# Rahu/Ketu special handling — per Parashara school they have no own sign.
# Most modern authorities use:
#   Rahu — Mool: Virgo  (or Aquarius per some southern schools)
#   Ketu — Mool: Pisces (or Scorpio per some southern schools)
# Some authorities give Rahu exalted in Taurus (or Gemini), debilitated in Scorpio (or Sag)
# We follow the more commonly cited Parashari version.
RAHU_KETU_OWN = {
    "Rahu": "Virgo",       # Parashara school
    "Ketu": "Pisces",      # Parashara school
}
RAHU_KETU_EXALTED = {
    "Rahu": "Taurus",      # Phaladeepika tradition
    "Ketu": "Scorpio",
}
RAHU_KETU_DEBIL = {
    "Rahu": "Scorpio",
    "Ketu": "Taurus",
}

# Ownership map (extended for Rahu/Ketu)
def _planet_owns_sign(planet, sign):
    if planet in RASI_LORDS.values():
        # find any sign where this planet is the lord
        return any(RASI_LORDS[s] == planet for s in [sign])
    if planet == "Rahu":
        return sign == RAHU_KETU_OWN["Rahu"]
    if planet == "Ketu":
        return sign == RAHU_KETU_OWN["Ketu"]
    return False


def _planet_exalted_sign(planet):
    if planet in EXALTATION_SIGNS:
        return EXALTATION_SIGNS[planet]
    return RAHU_KETU_EXALTED.get(planet)


def _planet_debilitated_sign(planet):
    if planet in DEBILITATION_SIGNS:
        return DEBILITATION_SIGNS[planet]
    return RAHU_KETU_DEBIL.get(planet)


# ============================================================
# 1. BALADI AVASTHA — 5-state by degree-in-sign
# ============================================================

BALADI_STATES = [
    {"name": "Bala",    "range": (0, 6),   "strength_pct": 25,  "meaning": "child / infant — undeveloped, weak effect"},
    {"name": "Kumara",  "range": (6, 12),  "strength_pct": 50,  "meaning": "youth / adolescent — moderate, growing strength"},
    {"name": "Yuva",    "range": (12, 18), "strength_pct": 100, "meaning": "adult — full strength, peak effect"},
    {"name": "Vriddha", "range": (18, 24), "strength_pct": 50,  "meaning": "old age — declining strength"},
    {"name": "Mrita",   "range": (24, 30), "strength_pct": 25,  "meaning": "dead — minimal effect"},
]

def baladi_avastha(planet_data):
    """Return baladi state from planet's degree-in-sign + sign-parity.

    Args:
        planet_data: dict with keys 'deg' (0-30) and 'rasi_idx' (0-11, 0=Aries).

    Returns:
        {state, strength_pct, stage_meaning, source, deg_in_sign, sign_parity}

    Rule (Phaladeepika 8.1):
        For ODD signs (rasi_idx 0,2,4,6,8,10 = Aries,Gem,Leo,Lib,Sag,Aqu):
            order is Bala (0-6), Kumara, Yuva, Vriddha, Mrita (24-30).
        For EVEN signs (rasi_idx 1,3,5,7,9,11 = Tau,Can,Vir,Sco,Cap,Pis):
            order REVERSES — Mrita first (0-6), then Vriddha, Yuva, Kumara, Bala (24-30).
        Source: Phaladeepika 8.1 — "vishame meshaadau, same vrushaadau viparyayah"
    """
    deg = planet_data.get("deg", 0.0)
    rasi_idx = planet_data.get("rasi_idx", 0)
    # Clamp degree to [0, 30)
    if deg >= 30: deg = deg - 30 * int(deg / 30)
    if deg < 0: deg = 0

    # Pick sign-parity scheme
    is_odd_sign = rasi_idx in MASCULINE_SIGN_IDX  # Ari/Gem/Leo/Lib/Sag/Aqu
    if is_odd_sign:
        states = BALADI_STATES
    else:
        # Reverse for even signs
        states = list(reversed(BALADI_STATES))
        # After reversing, ranges are still in original 0-6, 6-12... order
        # but mapped to reversed state names. Rebuild ranges:
        states = [
            {"name": BALADI_STATES[4 - i]["name"],
             "range": BALADI_STATES[i]["range"],
             "strength_pct": BALADI_STATES[4 - i]["strength_pct"],
             "meaning": BALADI_STATES[4 - i]["meaning"]}
            for i in range(5)
        ]

    for s in states:
        lo, hi = s["range"]
        if lo <= deg < hi:
            return {
                "state": s["name"],
                "strength_pct": s["strength_pct"],
                "stage_meaning": s["meaning"],
                "source": "Phaladeepika Ch. 8.1 / BPHS Ch. 45",
                "deg_in_sign": round(deg, 4),
                "sign_parity": "odd" if is_odd_sign else "even",
            }
    # Edge case: deg == 30 (boundary) — assign to last state
    last = states[-1]
    return {
        "state": last["name"],
        "strength_pct": last["strength_pct"],
        "stage_meaning": last["meaning"],
        "source": "Phaladeepika Ch. 8.1 / BPHS Ch. 45",
        "deg_in_sign": round(deg, 4),
        "sign_parity": "odd" if is_odd_sign else "even",
        "note": "boundary case (deg=30) — assigned to terminal state",
    }


# ============================================================
# 2. JAGRADADI AVASTHA — 3-state wakefulness via dignity
# ============================================================

def _planet_relation_to_sign(planet, sign):
    """Return one of: own, exalted, friend, neutral, enemy, debilitated.

    For Rahu/Ketu uses RAHU_KETU_OWN/EXALTED/DEBIL maps; otherwise standard
    BPHS dignity + naisargika friendship.
    """
    # Exalted check first (highest priority per BPHS)
    exalted = _planet_exalted_sign(planet)
    if sign == exalted:
        return "exalted"

    # Debilitated check
    debilitated = _planet_debilitated_sign(planet)
    if sign == debilitated:
        return "debilitated"

    # Own sign check
    if planet in RASI_LORDS.values():
        if RASI_LORDS.get(sign) == planet:
            return "own"
    if planet in RAHU_KETU_OWN:
        if sign == RAHU_KETU_OWN[planet]:
            return "own"

    # Friendship check via sign-lord
    sign_lord = RASI_LORDS.get(sign)
    if not sign_lord:
        return "neutral"

    friends = NAISARGIKA_FRIENDS.get(planet, set())
    enemies = NAISARGIKA_ENEMIES.get(planet, set())
    neutrals = NAISARGIKA_NEUTRALS.get(planet, set())

    if sign_lord in friends:
        return "friend"
    if sign_lord in enemies:
        return "enemy"
    if sign_lord in neutrals:
        return "neutral"
    # Fallback (planet itself owns the sign — already caught above)
    return "neutral"


def jagradadi_avastha(planet_name, chart):
    """Return wakefulness state based on planet's relation to its sign.

    Returns:
        {state, strength_pct, meaning, source, sign, relation}

    Rule (BPHS Ch. 45.10-13):
        Jagrat (awake)    — planet in own or exalted sign       — 100% effect
        Swapna (dreaming) — planet in friend or neutral sign    — 50% effect
        Sushupta (sleep)  — planet in enemy or debilitated sign — 25% effect
    """
    pos = chart.get("positions", {}).get(planet_name)
    if not pos:
        return {"state": "unknown", "strength_pct": 0, "meaning": "planet not in chart",
                "source": "BPHS Ch. 45", "sign": None, "relation": "unknown"}

    sign = pos["rasi"]
    relation = _planet_relation_to_sign(planet_name, sign)

    if relation in ("own", "exalted"):
        return {
            "state": "Jagrat",
            "strength_pct": 100,
            "meaning": "awake — fully active, gives strong results of its significations",
            "source": "BPHS Ch. 45.10-13",
            "sign": sign,
            "relation": relation,
        }
    elif relation in ("friend", "neutral"):
        return {
            "state": "Swapna",
            "strength_pct": 50,
            "meaning": "dreaming — partial/moderate results, mixed effects",
            "source": "BPHS Ch. 45.10-13",
            "sign": sign,
            "relation": relation,
        }
    else:  # enemy, debilitated
        return {
            "state": "Sushupta",
            "strength_pct": 25,
            "meaning": "deep sleep — minimal results, planet's significations suppressed",
            "source": "BPHS Ch. 45.10-13",
            "sign": sign,
            "relation": relation,
        }


# ============================================================
# 3. DEEPTADI AVASTHA — 9-state extended dignity
# ============================================================

def _is_combust(planet_name, chart):
    """Check if planet is combust (asta) — within combust orb of Sun.

    Uses Phaladeepika 5.20-23 orbs:
      Moon=12, Mars=17, Mercury=14, Jupiter=11, Venus=10, Saturn=15.
    Sun itself is never combust. Rahu/Ketu shadows are not combust.
    """
    if planet_name in ("Sun", "Rahu", "Ketu"):
        return False
    pos = chart.get("positions", {})
    if planet_name not in pos or "Sun" not in pos:
        return False

    plon = pos[planet_name].get("lon")
    slon = pos["Sun"].get("lon")
    if plon is None or slon is None:
        return False

    # Angular distance (shortest)
    diff = abs(plon - slon) % 360
    diff = min(diff, 360 - diff)

    orb = COMBUST_ORB.get(planet_name, 12.0)
    return diff < orb


def _is_retrograde(planet_name, chart):
    """Check if planet is retrograde. Sun and Moon never retrograde.

    Looks for 'retro' or 'retrograde' boolean key in position data.
    Falls back to False if not encoded.
    """
    if planet_name in ("Sun", "Moon"):
        return False
    pos = chart.get("positions", {}).get(planet_name, {})
    return bool(pos.get("retro", False) or pos.get("retrograde", False))


def _is_in_war(planet_name, chart):
    """Check graha-yuddha (planetary war): two non-luminary planets within 1 deg.

    Sun, Moon, Rahu, Ketu never participate in graha-yuddha (per BPHS).
    Returns:
        (in_war: bool, opponent: str|None, is_loser: bool)
    """
    if planet_name in ("Sun", "Moon", "Rahu", "Ketu"):
        return False, None, False
    pos = chart.get("positions", {})
    if planet_name not in pos:
        return False, None, False

    plon = pos[planet_name].get("lon")
    if plon is None:
        return False, None, False

    war_planets = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    for opp in war_planets:
        if opp == planet_name or opp not in pos:
            continue
        olon = pos[opp].get("lon")
        if olon is None:
            continue
        diff = abs(plon - olon) % 360
        diff = min(diff, 360 - diff)
        if diff < 1.0:
            # In war. Loser = the one farther south or with lower latitude.
            # Without latitude data, fall back to: lower-degree planet loses
            # (a common heuristic). Some authorities use brightness/dimness.
            pdeg = pos[planet_name].get("deg", 0)
            odeg = pos[opp].get("deg", 0)
            is_loser = pdeg < odeg  # heuristic
            return True, opp, is_loser
    return False, None, False


def _is_with_benefic(planet_name, chart):
    """True if planet is conjunct any natural benefic (in same sign)."""
    pos = chart.get("positions", {})
    if planet_name not in pos:
        return False
    rasi_idx = pos[planet_name]["rasi_idx"]
    for benefic in NATURAL_BENEFICS:
        if benefic == planet_name:
            continue
        if benefic in pos and pos[benefic]["rasi_idx"] == rasi_idx:
            return True
    return False


def _is_with_malefic(planet_name, chart):
    """True if planet is conjunct any natural malefic (in same sign)."""
    pos = chart.get("positions", {})
    if planet_name not in pos:
        return False
    rasi_idx = pos[planet_name]["rasi_idx"]
    for malefic in NATURAL_MALEFICS:
        if malefic == planet_name:
            continue
        if malefic in pos and pos[malefic]["rasi_idx"] == rasi_idx:
            return True
    return False


def _is_aspected_by_malefic(planet_name, chart):
    """True if planet receives aspect from any malefic.

    Uses 7th-house mutual aspect for everyone, plus special aspects for Mars (4,8),
    Saturn (3,10), Jupiter (5,9), Rahu/Ketu (5,9).
    """
    pos = chart.get("positions", {})
    if planet_name not in pos:
        return False
    target_idx = pos[planet_name]["rasi_idx"]

    for malefic in NATURAL_MALEFICS:
        if malefic == planet_name:
            continue
        if malefic not in pos:
            continue
        m_idx = pos[malefic]["rasi_idx"]
        # 7th aspect (everyone)
        if (m_idx + 6) % 12 == target_idx:
            return True
        # Special aspects
        if malefic == "Mars":
            if (m_idx + 3) % 12 == target_idx or (m_idx + 7) % 12 == target_idx:
                return True
        if malefic == "Saturn":
            if (m_idx + 2) % 12 == target_idx or (m_idx + 9) % 12 == target_idx:
                return True
        if malefic in ("Rahu", "Ketu"):
            if (m_idx + 4) % 12 == target_idx or (m_idx + 8) % 12 == target_idx:
                return True
    return False


def _is_in_dusthana_from_lord(planet_name, chart):
    """True if planet is in 6th, 8th, or 12th from its sign-lord's position."""
    pos = chart.get("positions", {})
    if planet_name not in pos:
        return False
    sign = pos[planet_name]["rasi"]
    lord = RASI_LORDS.get(sign)
    if not lord or lord not in pos:
        return False
    if lord == planet_name:
        return False  # planet in own sign — own lord
    p_idx = pos[planet_name]["rasi_idx"]
    l_idx = pos[lord]["rasi_idx"]
    diff = (p_idx - l_idx) % 12  # 0=same, 5=6th, 7=8th, 11=12th
    return diff in (5, 7, 11)


def _is_in_moolatrikona(planet_name, chart):
    """Check if planet is in its mool-trikona sign (BPHS 3.20)."""
    pos = chart.get("positions", {}).get(planet_name)
    if not pos:
        return False
    moolat = MOOLATRIKONA.get(planet_name)
    return moolat is not None and pos["rasi"] == moolat


def deeptadi_avastha(planet_name, chart):
    """Return 9-state dignity-based avastha.

    Order of resolution (BPHS Ch. 45 + Saravali Ch. 4):
        1. Deepta     (radiant)     — exalted
        2. Swastha    (own house)   — moolatrikona OR own (non-moolat priority)
        3. Pramudita  (delighted)   — friend's sign
        4. Shanta     (peaceful)    — benefic conjunct (and not afflicted)
        5. Shakta     (mighty)      — direct motion + bright (no debility)
        6. Peedita    (afflicted)   — debilitated OR 6/8/12 from natal lord
        7. Deena      (poor)        — enemy's sign
        8. Vikala     (handicapped) — combust by Sun (within combust orb, except Sun)
        9. Khala      (wicked)      — graha-yuddha-loser, retrograde + afflicted

    First match wins (cascading). Returns:
        {state, strength_pct, meaning, source, flags}
    """
    pos = chart.get("positions", {}).get(planet_name)
    if not pos:
        return {"state": "unknown", "strength_pct": 0, "meaning": "planet not in chart",
                "source": "BPHS Ch. 45", "flags": {}}

    sign = pos["rasi"]
    relation = _planet_relation_to_sign(planet_name, sign)

    # Compute all flags
    combust = _is_combust(planet_name, chart)
    retro = _is_retrograde(planet_name, chart)
    in_war, war_opp, war_loser = _is_in_war(planet_name, chart)
    with_benefic = _is_with_benefic(planet_name, chart)
    with_malefic = _is_with_malefic(planet_name, chart)
    aspected_malefic = _is_aspected_by_malefic(planet_name, chart)
    in_dusthana_lord = _is_in_dusthana_from_lord(planet_name, chart)
    moolatrikona = _is_in_moolatrikona(planet_name, chart)
    afflicted = with_malefic or aspected_malefic

    flags = {
        "combust": combust,
        "retrograde": retro,
        "in_war": in_war,
        "war_opponent": war_opp,
        "war_loser": war_loser,
        "with_benefic": with_benefic,
        "with_malefic": with_malefic,
        "aspected_by_malefic": aspected_malefic,
        "in_dusthana_from_sign_lord": in_dusthana_lord,
        "in_moolatrikona": moolatrikona,
        "dignity_relation": relation,
    }

    # Priority cascade — strongest afflictions checked first to avoid
    # false-positive Deepta (exalted-but-combust = still Vikala per Phaladeepika).
    # Saravali order: Khala > Vikala > Peedita > Deena > Deepta > Swastha > Pramudita > Shanta > Shakta
    # We follow the modern composite order (most-recent author Sharma 2008): start with positive
    # but downgrade if affliction overrides.

    # Tier A (negative — checked first, affliction overrides position):
    if in_war and war_loser and (retro or afflicted):
        return _make_state("Khala",   25,
            "wicked / wretched — graha-yuddha loser + retrograde/afflicted; severe damage to significations",
            flags)
    if combust:
        # Vikala: combust trumps positional dignity unless exalted-Mercury (some schools)
        # We follow the strict Phaladeepika rule: combust = Vikala regardless.
        return _make_state("Vikala",  10,
            f"handicapped — combust by Sun (within {COMBUST_ORB.get(planet_name, 12)} deg orb); significations crippled",
            flags)
    if relation == "debilitated" or in_dusthana_lord:
        return _make_state("Peedita", 20,
            "afflicted / pained — debilitated or in dusthana (6/8/12) from sign-lord; significations suffer",
            flags)
    if relation == "enemy":
        return _make_state("Deena",   30,
            "poor / wretched — in enemy's sign; significations weakened, hostile environment",
            flags)

    # Tier B (positive):
    if relation == "exalted":
        return _make_state("Deepta",  100,
            "radiant / brilliant — exalted; gives best results of significations",
            flags)
    if moolatrikona or relation == "own":
        return _make_state("Swastha",  90,
            "self-comfortable — in own house or mool-trikona; stable strong results",
            flags)
    if relation == "friend":
        return _make_state("Pramudita",70,
            "delighted — in friend's sign; pleasing favorable effects",
            flags)
    if with_benefic and not afflicted:
        return _make_state("Shanta",   60,
            "peaceful — conjunct natural benefic and unafflicted; calm steady effect",
            flags)
    # Default — Shakta if direct motion and bright
    if not retro and not afflicted:
        return _make_state("Shakta",   50,
            "mighty / capable — direct motion, no major affliction; functional",
            flags)
    # Catch-all: mild affliction but not combust/debil — still Shakta-tier-2
    return _make_state("Shakta",   40,
            "mighty (mild affliction) — direct motion but minor adverse aspects",
            flags)


def _make_state(name, pct, meaning, flags):
    return {
        "state": name,
        "strength_pct": pct,
        "meaning": meaning,
        "source": "BPHS Ch. 45 / Saravali Ch. 4 / Phaladeepika Ch. 8",
        "flags": flags,
    }


# ============================================================
# 4. LAJJITADI AVASTHA — 6-state interactive
# ============================================================

def lajjitadi_avastha(planet_name, chart):
    """Return 6-state interactive avastha (Phaladeepika Ch. 8.6-12).

    Six states (priority cascade — first match wins):
      1. Lajjita   (ashamed)   — in 5th house with Rahu/Ketu/Sun/Mars/Saturn
      2. Garvita   (proud)     — in own/exalted sign
      3. Kshudita  (hungry)    — with enemy planet OR in enemy sign
      4. Trishita  (thirsty)   — in watery sign + aspected/conjunct by malefic
      5. Mudita    (delighted) — with friend in friend's sign/house
      6. Kshobhita (agitated)  — combust + with enemy/aspected by malefic

    Returns:
        {state, strength_pct, meaning, source, flags}

    Note: A planet may match multiple criteria; cascade ensures consistent
    classification. Some authorities (Sarvartha Chintamani) order differently —
    we follow Mantreswara's original Phaladeepika order.
    """
    pos = chart.get("positions", {})
    if planet_name not in pos:
        return {"state": "unknown", "strength_pct": 0, "meaning": "planet not in chart",
                "source": "Phaladeepika Ch. 8", "flags": {}}

    p = pos[planet_name]
    sign = p["rasi"]
    house = p.get("house")
    relation = _planet_relation_to_sign(planet_name, sign)

    # Co-occupants in same sign
    rasi_idx = p["rasi_idx"]
    co_planets = [op for op in pos if op != planet_name and pos[op]["rasi_idx"] == rasi_idx]

    friends = NAISARGIKA_FRIENDS.get(planet_name, set())
    enemies = NAISARGIKA_ENEMIES.get(planet_name, set())

    with_enemy = any(op in enemies for op in co_planets)
    with_friend = any(op in friends for op in co_planets)

    combust = _is_combust(planet_name, chart)
    aspected_malefic = _is_aspected_by_malefic(planet_name, chart)
    with_malefic = _is_with_malefic(planet_name, chart)

    flags = {
        "house": house,
        "sign": sign,
        "relation": relation,
        "co_occupants": co_planets,
        "with_enemy": with_enemy,
        "with_friend": with_friend,
        "combust": combust,
        "aspected_by_malefic": aspected_malefic,
        "with_malefic": with_malefic,
        "watery_sign": sign in WATER_SIGNS,
    }

    # Lajjita check (5th house with specific malefics) — highest specificity
    if house == 5:
        lajjita_set = {"Rahu", "Ketu", "Sun", "Mars", "Saturn"}
        lajjita_co = [op for op in co_planets if op in lajjita_set]
        if lajjita_co:
            return _lajjita_state("Lajjita",  20,
                f"ashamed — in 5th house with {', '.join(lajjita_co)}; loss of intelligence/children-significations",
                flags)

    # Kshobhita (combust + enemy/malefic aspect) — highest negative
    if combust and (with_enemy or aspected_malefic):
        return _lajjita_state("Kshobhita", 15,
            "agitated / disturbed — combust and with enemy or aspected by malefic; chaos in significations",
            flags)

    # Garvita (proud) — own/exalted
    if relation in ("own", "exalted"):
        return _lajjita_state("Garvita",   100,
            "proud / dignified — in own or exalted sign; gives noble glorious results",
            flags)

    # Trishita (thirsty) — watery sign + malefic affliction
    if sign in WATER_SIGNS and (aspected_malefic or with_malefic):
        return _lajjita_state("Trishita",  35,
            "thirsty — in watery sign aspected/joined by malefic; unfulfilled cravings",
            flags)

    # Kshudita (hungry) — with enemy or in enemy sign
    if with_enemy or relation == "enemy":
        return _lajjita_state("Kshudita",  30,
            "hungry — with enemy planet or in enemy sign; deprivation, unfulfilled needs",
            flags)

    # Mudita (delighted) — with friend in friend's sign
    if with_friend and relation == "friend":
        return _lajjita_state("Mudita",     85,
            "delighted — with friend in friend's sign; happy harmonious results",
            flags)
    if with_friend or relation == "friend":
        return _lajjita_state("Mudita",     70,
            "delighted (partial) — friendly placement or company; pleasant effects",
            flags)

    # Default: balanced/neutral — Phaladeepika doesn't define a 7th state,
    # we tag as 'Mudita-mild' equivalent for completeness.
    return _lajjita_state("Mudita",     50,
        "moderately delighted — neutral placement; balanced effects",
        flags)


def _lajjita_state(name, pct, meaning, flags):
    return {
        "state": name,
        "strength_pct": pct,
        "meaning": meaning,
        "source": "Phaladeepika Ch. 8.6-12 (Mantreswara) / Sarvartha Chintamani",
        "flags": flags,
    }


# ============================================================
# UNIFIED API — run all 4 systems on all planets
# ============================================================

def all_avasthas(chart):
    """Run all 4 avastha systems on all 9 planets.

    Returns:
        {
            "Sun":     {"baladi": {...}, "jagradadi": {...}, "deeptadi": {...}, "lajjitadi": {...}},
            "Moon":    {...},
            ...
            "Ketu":    {...}
        }
    """
    out = {}
    pos = chart.get("positions", {})
    for planet in PLANETS_ALL:
        if planet not in pos:
            continue
        out[planet] = {
            "baladi":     baladi_avastha(pos[planet]),
            "jagradadi":  jagradadi_avastha(planet, chart),
            "deeptadi":   deeptadi_avastha(planet, chart),
            "lajjitadi":  lajjitadi_avastha(planet, chart),
        }
    return out


def avastha_summary(chart):
    """Summary: count of planets in each state-class + strength roll-up.

    Returns:
        {
            "strongest_planet": "Jupiter",
            "weakest_planet": "Mars",
            "total_strength_pct": 67.3,            # avg of Deeptadi pcts
            "states_summary": {                     # {system: {state: count}}
                "baladi":    {"Yuva": 3, "Bala": 1, ...},
                "jagradadi": {"Jagrat": 2, ...},
                "deeptadi":  {"Deepta": 1, ...},
                "lajjitadi": {"Garvita": 2, ...},
            },
            "per_planet_avg_strength": {"Sun": 50.0, ...},
            "recommendations": [...],
        }
    """
    all_a = all_avasthas(chart)
    if not all_a:
        return {"error": "no planet data in chart"}

    summary = {"baladi": {}, "jagradadi": {}, "deeptadi": {}, "lajjitadi": {}}
    per_planet_avg = {}

    for planet, systems in all_a.items():
        # Per-planet average strength (all 4 systems)
        pcts = [systems[s]["strength_pct"] for s in systems if "strength_pct" in systems[s]]
        per_planet_avg[planet] = round(sum(pcts) / len(pcts), 1) if pcts else 0

        # Tally states per system
        for sys_name in ("baladi", "jagradadi", "deeptadi", "lajjitadi"):
            state = systems[sys_name].get("state", "unknown")
            summary[sys_name][state] = summary[sys_name].get(state, 0) + 1

    # Find strongest/weakest
    if per_planet_avg:
        strongest = max(per_planet_avg, key=per_planet_avg.get)
        weakest = min(per_planet_avg, key=per_planet_avg.get)
    else:
        strongest = weakest = None

    # Total strength = average of avg strengths across all planets
    total_strength = round(sum(per_planet_avg.values()) / len(per_planet_avg), 1) \
                     if per_planet_avg else 0.0

    # Recommendations based on findings
    recs = []
    weak_planets = [p for p, v in per_planet_avg.items() if v < 35]
    strong_planets = [p for p, v in per_planet_avg.items() if v >= 75]

    if weak_planets:
        recs.append(f"Weak avasthas detected in {', '.join(weak_planets)}. "
                    f"Consider remedies: chant relevant mantra 108x daily, donate karaka items, "
                    f"strengthen via gemstone (after consultation).")
    if strong_planets:
        recs.append(f"Strongly placed: {', '.join(strong_planets)}. "
                    f"Leverage these — career/relationships should align with their significations.")

    # System-specific notes
    if summary["deeptadi"].get("Vikala", 0) >= 1:
        combust_planets = [p for p, sys in all_a.items() if sys["deeptadi"]["state"] == "Vikala"]
        recs.append(f"Combust planets: {', '.join(combust_planets)} — significations weakened "
                    f"during Sun's transit through their sign; remedy via Sun-pacification.")
    if summary["deeptadi"].get("Khala", 0) >= 1:
        khala_planets = [p for p, sys in all_a.items() if sys["deeptadi"]["state"] == "Khala"]
        recs.append(f"Graha-yuddha loss: {', '.join(khala_planets)} — these planets give wicked "
                    f"results unless propitiated; check their dasha periods carefully.")
    if summary["lajjitadi"].get("Lajjita", 0) >= 1:
        recs.append("Lajjita planet detected — child/intelligence-related significations "
                    "may suffer; remedy via 5th-house propitiation (Jupiter/Sun mantras).")
    if summary["jagradadi"].get("Sushupta", 0) >= 4:
        recs.append("Multiple planets in Sushupta (deep sleep) — chart shows many dormant "
                    "significations; spiritual practice and dasha-timing essential to activate.")

    return {
        "strongest_planet": strongest,
        "strongest_pct": per_planet_avg.get(strongest, 0) if strongest else 0,
        "weakest_planet": weakest,
        "weakest_pct": per_planet_avg.get(weakest, 0) if weakest else 0,
        "total_strength_pct": total_strength,
        "states_summary": summary,
        "per_planet_avg_strength": per_planet_avg,
        "recommendations": recs,
        "source": "BPHS Ch. 45 + Phaladeepika Ch. 8 + Saravali Ch. 4",
        "n_planets_analyzed": len(all_a),
    }


# ============================================================
# TEST BLOCK
# ============================================================

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    print(f"=== AVASTHAS — {chart['name']} ===\n")

    all_a = all_avasthas(chart)

    def _meaning(s):
        # Baladi uses 'stage_meaning'; others use 'meaning'.
        return s.get("meaning") or s.get("stage_meaning") or "?"

    print("--- SUN's 4 avastha states ---")
    sun_states = all_a.get("Sun", {})
    for sys_name in ("baladi", "jagradadi", "deeptadi", "lajjitadi"):
        s = sun_states.get(sys_name, {})
        print(f"  [{sys_name:10s}] {s.get('state','?'):12s} ({s.get('strength_pct','?')}%) - {_meaning(s)[:80]}")

    print("\n--- MOON's 4 avastha states ---")
    moon_states = all_a.get("Moon", {})
    for sys_name in ("baladi", "jagradadi", "deeptadi", "lajjitadi"):
        s = moon_states.get(sys_name, {})
        print(f"  [{sys_name:10s}] {s.get('state','?'):12s} ({s.get('strength_pct','?')}%) - {_meaning(s)[:80]}")

    print("\n--- ALL 9 PLANETS — DEEPTADI summary ---")
    for planet in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        if planet in all_a:
            d = all_a[planet]["deeptadi"]
            print(f"  {planet:8s}: {d['state']:10s} ({d['strength_pct']}%) - {d['meaning'][:65]}")

    print("\n=== AVASTHA SUMMARY ===")
    summary = avastha_summary(chart)
    print(f"  Total strength    : {summary['total_strength_pct']}%")
    print(f"  Strongest planet  : {summary['strongest_planet']} ({summary['strongest_pct']}%)")
    print(f"  Weakest planet    : {summary['weakest_planet']} ({summary['weakest_pct']}%)")
    print(f"  Planets analyzed  : {summary['n_planets_analyzed']}")
    print(f"\n  States summary:")
    for sys_name, states in summary["states_summary"].items():
        print(f"    {sys_name:10s}: {dict(states)}")
    print(f"\n  Per-planet avg strength:")
    for p, v in summary["per_planet_avg_strength"].items():
        print(f"    {p:8s}: {v}%")
    print(f"\n  Recommendations ({len(summary['recommendations'])}):")
    for i, r in enumerate(summary["recommendations"], 1):
        print(f"    {i}. {r}")

    print("\n=== Test complete — 0 exceptions ===")
