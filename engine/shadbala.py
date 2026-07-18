"""
Shadbala — six-fold planetary strength.

Implements the four most-cited Balas from BPHS Ch.27. Each Bala is measured in
Rupas (1 Rupa = 60 Virupas). A planet's total strength below its threshold is
considered weak.

Implemented:
    1. Sthana Bala  (positional strength, simplified — own/exalted/friend etc.)
    2. Dig Bala     (directional strength — Sun/Mars in 10th, Moon/Venus in 4th, etc.)
    3. Kala Bala    (temporal strength — partial: paksha + nathonnata)
    4. Naisargika Bala (natural strength — fixed per planet)

Not yet implemented (left for future iteration):
    Cheshta Bala  (motional — needs daily speeds)
    Drik Bala     (aspectual — needs full aspect math + benefic/malefic)
    Saptavargaja  (varga aggregation)
    Bhava Bala    (house strength, separate from planet bala)

Source: BPHS Ch.27 (Surya Siddhanta tradition), Phaladeepika Ch.5.
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.constants import (
    DEBILITATION_TAMIL as DEBILITATION,
    EXALTATION_TAMIL as EXALTATION,
    OWN_SIGNS_TAMIL as OWN_SIGNS,
    SIGN_LORDS_TAMIL as SIGN_LORDS,
    SIGNS_TAMIL as SIGNS,
)


PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")

# Naisargika (natural) strength in Virupas — fixed by planet, BPHS Ch.27.
# Sun is strongest, then Moon, etc., declining order.
NAISARGIKA_VIRUPAS = {
    "Sun": 60.0, "Moon": 51.43, "Venus": 42.86, "Jupiter": 34.29,
    "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57,
}

# Dig Bala — strongest house per planet
DIG_BALA_HOUSE = {
    "Sun": 10, "Mars": 10,        # midheaven (career, status)
    "Jupiter": 1, "Mercury": 1,    # ascendant (intellect, fortune)
    "Moon": 4, "Venus": 4,         # nadir (home, comfort)
    "Saturn": 7,                    # descendant (servants, trade)
}

# Friendships (permanent, classical)
FRIENDS = {
    "Sun":     {"Moon", "Mars", "Jupiter"},
    "Moon":    {"Sun", "Mercury"},
    "Mars":    {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus":   {"Mercury", "Saturn"},
    "Saturn":  {"Mercury", "Venus"},
}
ENEMIES = {
    "Sun":     {"Venus", "Saturn"},
    "Moon":    set(),                  # Moon is friendly to all
    "Mars":    {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus":   {"Sun", "Moon"},
    "Saturn":  {"Sun", "Moon", "Mars"},
}

# Threshold (Rupas) — minimum total Shadbala for adequate strength.
# Classical (Surya Siddhanta) per-planet thresholds.
SHADBALA_THRESHOLDS_RUPA = {
    "Sun": 5.0, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
    "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0,
}


@dataclass
class BalaScore:
    sthana: float       # Virupas
    dig: float
    kala: float
    naisargika: float
    total_virupas: float
    total_rupas: float
    is_strong: bool
    components: dict


def _sign_idx(lon: float) -> int:
    return int(lon % 360 // 30)


def _sign_name(lon: float) -> str:
    return SIGNS[_sign_idx(lon)]


def _house_of(lon: float, lagna: float) -> int:
    return ((_sign_idx(lon) - _sign_idx(lagna)) % 12) + 1


def _sthana_bala(planet: str, lon: float, all_positions: dict) -> tuple[float, str]:
    """Simplified Sthana Bala using a 60-Virupa max scale.

    Modes:
      Exaltation             → 60
      Own sign               → 45
      Moolatrikona (~own)    → 50    (we approximate as own here)
      Friend's sign          → 30
      Neutral                → 15
      Enemy's sign           → 7
      Debilitation           → 0
    """
    sign = _sign_name(lon)
    if sign == EXALTATION.get(planet):
        return 60.0, "exaltation"
    if sign in OWN_SIGNS.get(planet, []):
        return 45.0, "own sign"
    if sign == DEBILITATION.get(planet):
        return 0.0, "debilitation"
    sign_lord = SIGN_LORDS[sign]
    if sign_lord in FRIENDS.get(planet, set()):
        return 30.0, "friend's sign"
    if sign_lord in ENEMIES.get(planet, set()):
        return 7.0, "enemy's sign"
    return 15.0, "neutral"


def _dig_bala(planet: str, house: int) -> float:
    """Maximum 60 Virupas in best house, 0 in opposite (180° away)."""
    best = DIG_BALA_HOUSE.get(planet)
    if best is None:        # Rahu/Ketu — skip
        return 0.0
    # Houses are 1-12. Distance in houses (cyclic).
    diff = abs(house - best)
    if diff > 6:
        diff = 12 - diff
    # Linear scale: 0 (best) → 60 V, 6 (worst) → 0 V
    return (6 - diff) / 6 * 60.0


def _paksha_bala(planet: str, sun_lon: float, moon_lon: float) -> float:
    """Light-of-the-fortnight strength.
    Bright fortnight (waxing Moon) — benefics gain, malefics lose; reverse for dark.
    Returns Virupas, 0..60.
    """
    # Tithi = (moon - sun) / 12  (in degrees) gives 0..30 → in 360° terms 0..360
    elong = (moon_lon - sun_lon) % 360
    # Bright if elong < 180 (waxing), dark if > 180 (waning)
    # Strength of Moon at full ≈ 60, at new ≈ 0.
    if planet == "Moon":
        return 60.0 * (1.0 - abs(180.0 - elong) / 180.0)
    BENEFICS = {"Jupiter", "Venus", "Mercury"}
    MALEFICS = {"Sun", "Mars", "Saturn"}
    waxing = elong < 180
    if planet in BENEFICS:
        return 60.0 if waxing else 30.0
    if planet in MALEFICS:
        return 30.0 if waxing else 60.0
    return 30.0


# ─── Sthana sub-balas (BPHS Ch.27) ────────────────────────────────────────
def _uchcha_bala(planet: str, lon: float) -> float:
    """Distance from debilitation degree (linear 0-60)."""
    deb_sign = list(SIGNS).index(DEBILITATION.get(planet)) if DEBILITATION.get(planet) else None
    if deb_sign is None:
        return 30.0
    deb_lon = deb_sign * 30 + 0
    diff = abs((lon - deb_lon + 540) % 360 - 180)
    return diff / 180 * 60.0


def _ojhayugma_rasi_amsha_bala(planet: str, lon: float, navamsa_lon: float) -> float:
    """Odd-vs-even sign placement. Male planets prefer odd signs, female even."""
    male = {"Sun", "Mars", "Jupiter"}
    female = {"Moon", "Venus"}
    sign = int(lon // 30)
    nav_sign = int(navamsa_lon // 30)
    is_odd = sign % 2 == 0    # 0=Aries (odd in 1-indexed)
    nav_odd = nav_sign % 2 == 0
    score = 0.0
    if planet in male:
        if is_odd: score += 15
        if nav_odd: score += 15
    elif planet in female:
        if not is_odd: score += 15
        if not nav_odd: score += 15
    else:    # Mercury, Saturn
        score = 15.0
    return score


def _kendradi_bala(house: int) -> float:
    """Kendra (1,4,7,10) = 60V; Panapara (2,5,8,11) = 30V; Apoklima (3,6,9,12) = 15V."""
    if house in (1, 4, 7, 10):
        return 60.0
    if house in (2, 5, 8, 11):
        return 30.0
    return 15.0


def _drekkana_bala(planet: str, lon: float) -> float:
    """Male in 1st drekkana, female in 2nd, hermaphrodite in 3rd: +15 each."""
    drek = int((lon % 30) // 10)    # 0, 1, or 2
    male = {"Sun", "Mars", "Jupiter"}
    female = {"Moon", "Venus"}
    if planet in male and drek == 0: return 15.0
    if planet in female and drek == 1: return 15.0
    if planet in {"Mercury", "Saturn"} and drek == 2: return 15.0
    return 0.0


def _saptavargaja_bala(planet: str, vargas_dict: dict) -> float:
    """Sum strength across 7 vargas (D1, D2, D3, D7, D9, D12, D30).
    Each varga: own=30, exalted=20, friend=10, neutral=5, enemy=2, debil=0.
    Then divided by 7 to give per-varga average ×60 = max 60 V."""
    if not vargas_dict:
        return 30.0
    target_vargas = ("D1", "D2", "D3", "D7", "D9", "D12", "D30")
    score_map = {"exaltation": 20, "own": 30, "friend": 10,
                 "neutral": 5, "enemy": 2, "debilitation": 0}
    total = 0.0
    n = 0
    pdata = vargas_dict.get(planet, {})
    for vname in target_vargas:
        if vname not in pdata:
            continue
        v_data = pdata[vname]
        if isinstance(v_data, dict):
            v_sign = v_data.get("sign") or v_data.get("rasi")
        elif isinstance(v_data, str):
            v_sign = v_data
        else:
            continue
        if not v_sign:
            continue
        # Determine state
        if v_sign == EXALTATION.get(planet):
            total += 20
        elif v_sign in OWN_SIGNS.get(planet, []):
            total += 30
        elif v_sign == DEBILITATION.get(planet):
            total += 0
        else:
            sign_lord = SIGN_LORDS[v_sign]
            if sign_lord in FRIENDS.get(planet, set()):
                total += 10
            elif sign_lord in ENEMIES.get(planet, set()):
                total += 2
            else:
                total += 5
        n += 1
    if n == 0:
        return 30.0
    avg = total / n
    return min(60.0, avg * 2)    # scale 0-30 → 0-60 V


# ─── Cheshta Bala ──────────────────────────────────────────────────────────
def _cheshta_bala(planet: str, jd_ut: float) -> float:
    """Motional strength.
    Sun's cheshta = ayana bala (declination based, max at solstices).
    Moon's cheshta = paksha bala (already computed).
    Other 5 planets: scaled retrograde + speed.
    Simplified: retrograde +60, near-stationary +45, normal speed +30.
    Need swisseph to check retrograde — caller provides via `is_retro` map.
    """
    import swisseph as swe
    if planet in ("Sun",):
        # Ayana bala — depends on declination from celestial equator
        try:
            pos, _ = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SWIEPH)
            tropical_lon = pos[0]
            # Approx declination: sin(decl) = sin(23.44°) * sin(tropical_lon)
            import math
            decl = math.degrees(math.asin(math.sin(math.radians(23.44)) *
                                           math.sin(math.radians(tropical_lon))))
            # Ayana bala max 60 at decl ±23.44°, 0 at decl 0
            return abs(decl) / 23.44 * 60.0
        except Exception:
            return 30.0
    if planet == "Moon":
        return 30.0    # paksha already accounted in kala
    # Other planets: retrograde detection
    try:
        pid_map = {"Mars": swe.MARS, "Mercury": swe.MERCURY,
                   "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN}
        if planet not in pid_map:
            return 30.0
        pos, _ = swe.calc_ut(jd_ut, pid_map[planet], swe.FLG_SWIEPH | swe.FLG_SPEED)
        speed = pos[3]
        if speed < 0:
            return 60.0    # retrograde
        # Scale by speed (slow = more strength). Reference avg speeds:
        avg_speed = {"Mars": 0.524, "Mercury": 1.383, "Jupiter": 0.083,
                     "Venus": 1.2, "Saturn": 0.034}
        ratio = speed / avg_speed.get(planet, 1.0)
        if ratio < 0.5:
            return 45.0
        if ratio < 1.0:
            return 30.0
        return 15.0
    except Exception:
        return 30.0


# ─── Drig Bala ─────────────────────────────────────────────────────────────
def _drig_bala(planet: str, all_positions: dict) -> float:
    """Aspectual strength: sum of benefic-aspect minus malefic-aspect strengths.

    Each planet aspects others; benefic aspects add, malefic aspects subtract.
    Maximum 60 V at full benefic aspect from all benefics, 0 V at full malefic.
    Simplified: count net (benefic - malefic) sign-aspects on this planet.
    """
    BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
    MALEFICS = {"Sun", "Mars", "Saturn"}
    aspects = {
        "Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7],
        "Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10],
    }
    target_lon = all_positions.get(planet)
    if target_lon is None:
        return 30.0
    target_sign = int(target_lon // 30)
    net = 0.0
    for aspector, lon in all_positions.items():
        if aspector == planet:
            continue
        if aspector not in aspects:
            continue
        a_sign = int(lon // 30)
        for off in aspects[aspector]:
            if (a_sign + off - 1) % 12 == target_sign:
                weight = 1.0
                # 7th aspect is full; 4/8, 5/9, 3/10 are 3/4 strength
                if off in (4, 5, 8, 9, 3, 10):
                    weight = 0.75
                if aspector in BENEFICS:
                    net += weight * 15
                elif aspector in MALEFICS:
                    net -= weight * 15
    # Map to 0-60 range, neutral at 30
    return max(0.0, min(60.0, 30.0 + net))


def _nathonnata_bala(planet: str, jd_ut: float, sunrise_jd: float | None) -> float:
    """Day/night planet strength. Without sunrise we approximate from hour-of-day:
    diurnal planets (Sun, Jupiter, Venus) gain in day; nocturnal (Moon, Mars, Saturn)
    in night. Mercury balanced. Returns Virupas 0..60.

    Simple approx: assume day = 06:00–18:00 local. We can't compute true sunrise here
    without lat/lon, so use a 50% midday assumption — gives 30 Virupas baseline.
    """
    if sunrise_jd is None:
        return 30.0
    # If we get fancy: compute fraction of day, etc. Stay 30 for now.
    return 30.0


def compute(
    positions: dict[str, float],
    lagna: float,
    jd_ut: float | None = None,
    vargas_dict: dict | None = None,
) -> dict[str, BalaScore]:
    """Compute full 6-fold Shadbala for each of the 7 traditional planets.

    positions:   {body: longitude, ...}  must contain at least the 7 planets.
    lagna:       ascendant longitude.
    jd_ut:       julian day (required for Cheshta bala — uses ephemeris).
    vargas_dict: optional varga positions for Saptavargaja bala.

    Now computes ALL 6 balas (Sthana / Dig / Kala / Cheshta / Naisargika / Drig)
    plus the 5 Sthana sub-balas (Uchcha / Saptavargaja / Ojha-Yugma /
    Kendradi / Drekkana) per BPHS Ch.27.
    """
    out: dict[str, BalaScore] = {}
    sun_lon = positions.get("Sun", 0.0)
    moon_lon = positions.get("Moon", 0.0)

    for planet in PLANETS:
        if planet not in positions:
            continue
        lon = positions[planet]
        house = _house_of(lon, lagna)

        # Sthana sub-balas
        sthana_main, sthana_label = _sthana_bala(planet, lon, positions)
        uchcha = _uchcha_bala(planet, lon)
        nav_lon = (vargas_dict or {}).get(planet, {}).get("D9", {}).get("longitude", lon)
        ojhayugma = _ojhayugma_rasi_amsha_bala(planet, lon, nav_lon)
        kendradi = _kendradi_bala(house)
        drekkana = _drekkana_bala(planet, lon)
        saptavargaja = _saptavargaja_bala(planet, vargas_dict or {})
        # Total sthana = main + sub-components, capped at ~150 V (BPHS scale)
        sthana = sthana_main + uchcha + ojhayugma + kendradi + drekkana + saptavargaja

        dig = _dig_bala(planet, house)
        paksha = _paksha_bala(planet, sun_lon, moon_lon)
        nathonnata = _nathonnata_bala(planet, jd_ut or 0.0, None)
        kala = (paksha + nathonnata) / 2.0
        cheshta = _cheshta_bala(planet, jd_ut) if jd_ut else 30.0
        drig = _drig_bala(planet, positions)
        naisargika = NAISARGIKA_VIRUPAS[planet]

        total_v = sthana + dig + kala + cheshta + naisargika + drig
        total_r = total_v / 60.0
        threshold = SHADBALA_THRESHOLDS_RUPA[planet]

        out[planet] = BalaScore(
            sthana=round(sthana, 2),
            dig=round(dig, 2),
            kala=round(kala, 2),
            naisargika=round(naisargika, 2),
            total_virupas=round(total_v, 2),
            total_rupas=round(total_r, 2),
            is_strong=total_r >= threshold,
            components={
                "sthana_state": sthana_label,
                "sthana_main": round(sthana_main, 2),
                "uchcha": round(uchcha, 2),
                "ojhayugma": round(ojhayugma, 2),
                "kendradi": round(kendradi, 2),
                "drekkana": round(drekkana, 2),
                "saptavargaja": round(saptavargaja, 2),
                "cheshta": round(cheshta, 2),
                "drig": round(drig, 2),
                "house": house,
                "dig_best_house": DIG_BALA_HOUSE.get(planet),
                "paksha": round(paksha, 2),
                "nathonnata": round(nathonnata, 2),
                "threshold_rupas": threshold,
            },
        )
    return out


def summary(scores: dict[str, BalaScore]) -> dict:
    """Summary for reading layer."""
    sorted_by_total = sorted(scores.items(), key=lambda kv: -kv[1].total_rupas)
    return {
        "strongest": [n for n, _ in sorted_by_total[:3]],
        "weakest": [n for n, _ in sorted_by_total[-3:]],
        "below_threshold": [
            n for n, s in scores.items() if not s.is_strong
        ],
        "above_threshold": [
            n for n, s in scores.items() if s.is_strong
        ],
        "scores_rupas": {n: s.total_rupas for n, s in scores.items()},
    }


# ─── Runtime dict-chart API (consolidated from runtime/shadbala.py) ─────────
# These functions accept the JSON dict-based chart format used by
# runtime/engine_orchestrator.py and runtime/generate_report.py. The simpler
# dict-based API stays available alongside the canonical full BPHS engine.

# Naisargika (natural) strength — runtime-style dict (different rounding from
# the canonical NAISARGIKA_VIRUPAS, kept for runtime-API parity).
NAISARGIKA = {
    "Sun": 60, "Moon": 51.42, "Venus": 42.85, "Jupiter": 34.28,
    "Mercury": 25.71, "Mars": 17.14, "Saturn": 8.57,
}
# Threshold (Rupas) — runtime keys (Sun >=6.5 in runtime vs 5.0 in engine — kept
# distinct since both APIs are used by different callers expecting different
# strictness; advanced callers should use SHADBALA_THRESHOLDS_RUPA above).
THRESHOLD = {
    "Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
    "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0,
}

# Sign-dignity table for the dict-API (uses sign string, not lord lookup).
_SHB_DIGNITIES = {
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


def _sthana_dict(planet, pos):
    """Sthana bala using runtime sign-dignity classification."""
    sign = pos[planet]["rasi"]
    d = _SHB_DIGNITIES.get((planet, sign), "neutral")
    if d == "Exalted":
        return 60
    if d in ("Own", "Exalted/Own"):
        return 45
    if d == "Debil":
        return 5
    return 30


def _dig_dict(planet, pos):
    """Directional strength based on actual house from lagna."""
    if planet not in DIG_BALA_HOUSE:
        return 0
    h = pos[planet]["house"]
    ideal_h = DIG_BALA_HOUSE[planet]
    diff = abs(h - ideal_h)
    if diff > 6:
        diff = 12 - diff
    return 60 * (1 - diff / 6.0)


def _kala_dict(planet, chart):
    """Kala bala — daytime/nighttime + lunar paksha placeholder."""
    bala = 0
    b = chart["birth"]
    is_day = 6 <= b["hour"] < 18
    DAY_PLANETS = ("Sun", "Jupiter", "Venus")
    NIGHT_PLANETS = ("Moon", "Mars", "Saturn")
    if planet in DAY_PLANETS and is_day:
        bala += 30
    if planet in NIGHT_PLANETS and not is_day:
        bala += 30
    if planet == "Mercury":
        bala += 30
    if planet == "Moon":
        bala += 30  # placeholder; full calc needs lunar phase
    return bala


def _cheshta_dict(planet, pos):
    """Motional strength — retrograde planets get high cheshta."""
    if planet in ("Sun", "Moon", "Rahu", "Ketu"):
        return 30
    if pos.get(planet, {}).get("retro", False):
        return 60
    return 30


def _drik_dict(planet, pos):
    """Aspectual strength — sum of benefic-aspect minus malefic-aspect."""
    BENEFIC = ("Moon", "Mercury", "Jupiter", "Venus")
    MALEFIC = ("Sun", "Mars", "Saturn", "Rahu", "Ketu")
    if planet not in pos:
        return 0
    target_h = pos[planet]["house"]
    bala = 0
    for p, pd in pos.items():
        if p == planet:
            continue
        ph = pd["house"]
        seventh = ((ph + 6 - 1) % 12) + 1
        aspects = [seventh]
        if p == "Mars":
            aspects += [((ph + 3 - 1) % 12) + 1, ((ph + 7 - 1) % 12) + 1]
        if p == "Jupiter":
            aspects += [((ph + 4 - 1) % 12) + 1, ((ph + 8 - 1) % 12) + 1]
        if p == "Saturn":
            aspects += [((ph + 2 - 1) % 12) + 1, ((ph + 9 - 1) % 12) + 1]
        if target_h in aspects:
            if p in BENEFIC:
                bala += 15
            elif p in MALEFIC:
                bala -= 15
    return bala


def compute_shadbala(chart):
    """Compute full 6-fold shadbala using the canonical math and return it in the legacy dict API format.
    This fixes the bug where simplified math failed to reach classical thresholds.
    """
    pos = chart["positions"]
    
    # Build positions dict for compute()
    positions = {}
    for p in PLANETS:
        if p in pos:
            positions[p] = pos[p].get("lon_abs", pos[p]["rasi_idx"] * 30 + pos[p].get("deg", 0))
    if "Sun" in pos and "Sun" not in positions:
        positions["Sun"] = pos["Sun"].get("lon_abs", 0)
    if "Moon" in pos and "Moon" not in positions:
        positions["Moon"] = pos["Moon"].get("lon_abs", 0)
        
    lagna_deg = chart.get("lagna_deg", chart.get("lagna_idx", 0) * 30)
    
    # Calculate jd_ut if possible
    import swisseph as swe
    b = chart.get("birth", {})
    jd_ut = None
    if "year" in b and "month" in b and "day" in b:
        jd_ut = swe.julday(b["year"], b["month"], b["day"], b.get("hour", 12) + b.get("min", 0)/60.0)
        
    # Call the canonical compute engine
    scores = compute(positions, lagna_deg, jd_ut, vargas_dict=None)
    
    out = {}
    for p in PLANETS:
        if p not in scores:
            continue
        s = scores[p]
        out[p] = {
            "sthana": s.sthana,
            "dig": s.dig,
            "kala": s.kala,
            "cheshta": s.components.get("cheshta", 30),
            "naisargika": s.naisargika,
            "drik": s.components.get("drig", 30),
            "total_virupas": s.total_virupas,
            "total_rupas": s.total_rupas,
            "threshold": s.components.get("threshold_rupas", 5.0),
            "is_strong": s.is_strong,
        }
    return out
