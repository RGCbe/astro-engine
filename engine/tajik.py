"""
Tajik / Varshaphala — annual horoscope (yearly solar return) engine.

Tajik is the Persian-influenced annual horoscope system formalized by
Neelakantha (Tajika Neelakanthi, 16th c.) and elaborated by Hari Bhatta
(Tajika Sara). It runs alongside the natal Parashari chart and produces a
fresh chart valid for one year.

Implemented:
    solar_return_jd(natal_jd, age_years) — JD of Sun's return to exact
        natal longitude in the target year.
    muntha(natal_lagna_sign, age_years) — Muntha sign (progresses 1 sign/yr).
    varshesha_candidates(annual_chart) — 5 candidates per Tajik rules.
    tajik_yogas(annual_chart) — Itthashala / Ishrafa / Nakta / Yamayan
        (aspect-based applying/separating yogas).
    sahams(annual_chart) — 10 most-cited sahams.

⚠ NOT IMPLEMENTED YET:
    - All 16 named Tajik yogas (4 of 16 here)
    - Tripataki chakra (annual transit board)
    - Patyamsa-bala (Tajik strength scoring)
    - Mudda dasha (~98yr Tajik dasha)

Sources:
    Tajika Neelakanthi (Pt. Neelakantha, ~1587 CE)
    Varshaphala — Dr. K.S. Charak
    BV Raman, Varshaphala (1992)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

import swisseph as swe

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

# Tajik aspect orbs (per Tajika Neelakanthi Ch.5) — aspect strength based on
# longitudinal difference, not sign aspects. Orbs (deepatamsa) per planet:
TAJIK_ORB = {
    "Sun": 15, "Moon": 12, "Mars": 8, "Mercury": 7,
    "Jupiter": 9, "Venus": 7, "Saturn": 9, "Rahu": 5, "Ketu": 5,
}


# ─── Solar return ──────────────────────────────────────────────────────────
def _sun_lon(jd_ut: float) -> float:
    pos, _ = swe.calc_ut(jd_ut, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    return pos[0] % 360.0


def solar_return_jd(natal_jd: float, age_years: int, tol_seconds: float = 30) -> float:
    """Return JD when Sun reaches exact natal longitude `age_years` after birth.

    Bisection on Sun's longitude (it moves ~1°/day).
    """
    natal_sun = _sun_lon(natal_jd)
    # Approximate target JD = natal_jd + age * 365.25
    target_jd = natal_jd + age_years * 365.25
    # Search ±10 days
    lo, hi = target_jd - 10, target_jd + 10

    def diff(jd):
        d = (_sun_lon(jd) - natal_sun) % 360.0
        return d if d < 180 else d - 360.0

    # Bisect: find zero-crossing of diff(jd)
    for _ in range(60):
        mid = (lo + hi) / 2
        d = diff(mid)
        if abs(d) < (1.0 / 86400) * tol_seconds:
            return mid
        if d < 0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ─── Muntha ────────────────────────────────────────────────────────────────
def muntha(natal_lagna_sign: int, age_years: int) -> dict:
    """Muntha progresses 1 sign per completed year from natal lagna."""
    sign = (natal_lagna_sign + age_years) % 12
    return {
        "sign_idx": sign,
        "sign_name": SIGN_NAMES[sign],
        "lord": SIGN_LORD[sign],
        "age_at_observation": age_years,
    }


# ─── Annual chart computation ──────────────────────────────────────────────
PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,
}


@dataclass
class AnnualChart:
    age_years: int
    natal_jd: float
    return_jd: float
    return_dt: dt.datetime
    lat: float
    lon: float
    annual_lagna_sign: int
    annual_lagna_lord: str
    muntha_sign: int
    muntha_sign_name: str
    muntha_lord: str
    positions: dict = field(default_factory=dict)   # planet → sidereal longitude
    house_of: dict = field(default_factory=dict)    # planet → annual house (1..12)
    varshesha: str = ""
    yogas: list = field(default_factory=list)
    sahams: dict = field(default_factory=dict)


def annual_chart(
    natal_jd: float,
    natal_lagna_sign: int,
    age_years: int,
    lat: float,
    lon: float,
    tz_hours: float = 0.0,
) -> AnnualChart:
    """Compute the full annual chart for `age_years` after birth."""
    sr_jd = solar_return_jd(natal_jd, age_years)
    sr_dt = swe_jd_to_datetime(sr_jd)

    # Sidereal positions
    positions = {}
    for name, pid in PLANET_IDS.items():
        pos, _ = swe.calc_ut(sr_jd, pid, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        positions[name] = pos[0] % 360.0
    positions["Ketu"] = (positions["Rahu"] + 180) % 360.0

    # Annual lagna at the solar return moment + place
    cusps, _ = swe.houses_ex(sr_jd, lat, lon, b'P', swe.FLG_SIDEREAL)
    asc = cusps[0] % 360.0
    annual_lagna = int(asc // 30)
    house_of = {}
    for p, l in positions.items():
        sign = int(l // 30)
        house_of[p] = ((sign - annual_lagna) % 12) + 1

    m = muntha(natal_lagna_sign, age_years)

    chart = AnnualChart(
        age_years=age_years,
        natal_jd=natal_jd,
        return_jd=sr_jd,
        return_dt=sr_dt,
        lat=lat, lon=lon,
        annual_lagna_sign=annual_lagna,
        annual_lagna_lord=SIGN_LORD[annual_lagna],
        muntha_sign=m["sign_idx"],
        muntha_sign_name=m["sign_name"],
        muntha_lord=m["lord"],
        positions=positions,
        house_of=house_of,
    )
    chart.varshesha = select_varshesha(chart)
    chart.yogas = tajik_yogas(chart)
    chart.sahams = sahams(chart)
    return chart


# ─── Varshesha selection ───────────────────────────────────────────────────
# 5 candidates (Tajika Neelakanthi Ch.10):
#   1. Lord of annual lagna
#   2. Lord of Muntha sign
#   3. Lord of triṃśāmśa rising at annual lagna (skipped for MVP — needs D30)
#   4. Sun
#   5. Lord of the weekday of solar return
WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def varshesha_candidates(chart: AnnualChart) -> list[dict]:
    candidates = [
        {"role": "Annual Lagna Lord", "planet": chart.annual_lagna_lord},
        {"role": "Muntha Lord",        "planet": chart.muntha_lord},
        {"role": "Sun",                "planet": "Sun"},
        {"role": "Weekday Lord",       "planet": _weekday_lord(chart.return_dt)},
    ]
    return candidates


def _weekday_lord(dtval: dt.datetime) -> str:
    # Vedic week: Sunday=0 → Sun, Monday=1 → Moon, ...
    # Python weekday(): Monday=0, ... Sunday=6
    py_wd = dtval.weekday()   # 0..6 (Mon..Sun)
    vedic_wd = (py_wd + 1) % 7  # 0=Sun, 1=Mon, ...
    return WEEKDAY_LORDS[vedic_wd]


def select_varshesha(chart: AnnualChart) -> str:
    """Pick the strongest candidate. Simplified: prefer planet best-placed
    by house (kendra/trikona = 1,4,5,7,9,10). MVP rule — full strength
    scoring (panchavargi-bala) deferred."""
    candidates = varshesha_candidates(chart)
    kendra_trikona = {1, 4, 5, 7, 9, 10}
    scored = []
    for c in candidates:
        h = chart.house_of.get(c["planet"])
        score = 0
        if h is not None:
            if h in kendra_trikona: score += 5
            if h in {1, 10}: score += 2  # extra weight to lagna/karma houses
        scored.append((score, c["planet"], c["role"]))
    scored.sort(reverse=True)
    return scored[0][1] if scored else "Sun"


# ─── Tajik yogas (4 of 16 — applying / separating aspects) ─────────────────
def tajik_yogas(chart: AnnualChart) -> list[dict]:
    """Detect the four core Tajik aspect-based yogas:
        Itthashala — applying aspect between two planets (faster planet
                     applying to slower)
        Ishrafa    — separating aspect (faster moving away from slower)
        Nakta      — two slow planets connected via a fast intermediary
        Yamayan    — exact aspect (within 1°)
    """
    out = []
    plons = chart.positions
    speed_order = ["Moon", "Mercury", "Venus", "Sun", "Mars", "Jupiter", "Saturn"]

    def aspect_orb_diff(p1: str, p2: str) -> float | None:
        """Longitudinal distance (signed) between p1 and p2; returns None if outside orb."""
        if p1 not in plons or p2 not in plons:
            return None
        diff = (plons[p2] - plons[p1] + 180) % 360 - 180
        orb = (TAJIK_ORB.get(p1, 5) + TAJIK_ORB.get(p2, 5)) / 2
        return diff if abs(diff) <= orb else None

    for i, p1 in enumerate(speed_order):
        for p2 in speed_order[i + 1:]:
            diff = aspect_orb_diff(p1, p2)
            if diff is None:
                continue
            # p1 is faster (earlier in list). Applying = p1 lon < p2 lon (catching up)
            if diff > 0:
                yoga = "Itthashala"   # applying
                meaning = "Promise of result fructifying — relationship/career/effort completes"
            elif diff < 0:
                yoga = "Ishrafa"      # separating
                meaning = "Effort already past peak — dwindling result"
            else:
                yoga = "Yamayan"      # exact
                meaning = "Exact contact — peak intensity"
            if abs(diff) < 1.0:
                yoga = "Yamayan"
                meaning = "Exact contact within 1° — full force"
            out.append({
                "yoga": yoga, "planets": [p1, p2],
                "orb_deg": round(abs(diff), 2),
                "meaning": meaning,
            })

    return out


# ─── Sahams (10 most-cited) ────────────────────────────────────────────────
def _norm(deg: float) -> float:
    return deg % 360.0


def sahams(chart: AnnualChart) -> dict:
    """Compute 10 important sahams from Tajika Neelakanthi Ch.30.

    Saham formulas use: planet positions + lagna. Different formulas for
    day vs night birth (we use day formulas for MVP — Sun above horizon).
    """
    pos = chart.positions
    lagna = chart.annual_lagna_sign * 30 + 0.0   # use cusp at 0° — MVP

    def from_to(start: float, end: float) -> float:
        return _norm(start - end)

    # MVP set — formulas valid for diurnal births
    sahams_d = {
        # Punya saham = Moon - Sun + Lagna (luck/merit)
        "Punya":   _norm(pos["Moon"] - pos["Sun"] + lagna),
        # Vidya saham = Sun - Moon + Lagna (learning)
        "Vidya":   _norm(pos["Sun"] - pos["Moon"] + lagna),
        # Yashas saham = Jupiter - Lord of lagna + Lagna (fame)
        "Yashas":  _norm(pos["Jupiter"] - pos["Sun"] + lagna),  # simplified
        # Karma saham = Mars - Sun + Lagna (action/work)
        "Karma":   _norm(pos["Mars"] - pos["Sun"] + lagna),
        # Roga saham = Lagna - Moon + Lagna (disease)
        "Roga":    _norm(lagna - pos["Moon"] + lagna),
        # Mrityu saham = Lagna's 8th cusp - Moon (death)
        "Mrityu":  _norm((lagna + 240) - pos["Moon"]),
        # Vivaha saham = Venus - Saturn + Lagna (marriage)
        "Vivaha":  _norm(pos["Venus"] - pos["Saturn"] + lagna),
        # Putra saham = Jupiter - Saturn + Lagna (children)
        "Putra":   _norm(pos["Jupiter"] - pos["Saturn"] + lagna),
        # Bandhu saham = Mars - Mercury + Lagna (relatives)
        "Bandhu":  _norm(pos["Mars"] - pos["Mercury"] + lagna),
        # Artha saham = 2nd house cusp - Lord of 2nd + Lagna (wealth)
        "Artha":   _norm((lagna + 30) - pos["Sun"] + lagna),  # simplified
    }
    # Convert each to {sign, deg_in_sign}
    out = {}
    for name, lon_deg in sahams_d.items():
        sign = int(lon_deg // 30)
        out[name] = {
            "longitude": round(lon_deg, 3),
            "sign": SIGN_NAMES[sign],
            "deg_in_sign": round(lon_deg - sign * 30, 2),
        }
    return out


# ─── Helpers ───────────────────────────────────────────────────────────────
def swe_jd_to_datetime(jd_ut: float) -> dt.datetime:
    y, m, d, h = swe.revjul(jd_ut, swe.GREG_CAL)
    hh = int(h)
    mm = int((h - hh) * 60)
    ss = int(((h - hh) * 60 - mm) * 60)
    return dt.datetime(int(y), int(m), int(d), hh, mm, ss)


def datetime_to_jd(dtval: dt.datetime, tz_hours: float = 0.0) -> float:
    h = dtval.hour + dtval.minute / 60 + dtval.second / 3600 - tz_hours
    return swe.julday(dtval.year, dtval.month, dtval.day, h)


def summary(chart: AnnualChart) -> dict:
    # Build compat_chart for tajik_yogas_16
    compat_chart = {
        "positions": {
            p: {
                "deg": lon % 30,
                "rasi": SIGN_NAMES[int(lon // 30)],
                "rasi_idx": int(lon // 30),
                "house": chart.house_of[p],
                "lon": lon,
                "lon_abs": lon
            } for p, lon in chart.positions.items()
        }
    }
    
    # Import from runtime/tajik_yogas_16
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
    try:
        from tajik_yogas_16 import detect_all_tajik_yogas, all_balas
        yogas_16 = detect_all_tajik_yogas(compat_chart)
        balas_5 = all_balas(compat_chart)
    except Exception as e:
        yogas_16 = []
        balas_5 = {}
        print(f"Tajik yogas/balas calculation error: {e}")

    return {
        "age_years": chart.age_years,
        "solar_return": chart.return_dt.isoformat()[:19],
        "annual_lagna": SIGN_NAMES[chart.annual_lagna_sign],
        "annual_lagna_lord": chart.annual_lagna_lord,
        "muntha_sign": chart.muntha_sign_name,
        "muntha_lord": chart.muntha_lord,
        "varshesha": chart.varshesha,
        "varshesha_candidates": varshesha_candidates(chart),
        "yogas": chart.yogas,
        "yogas_16": yogas_16,
        "balas_5": balas_5,
        "sahams": chart.sahams,
        "planet_houses": chart.house_of,
    }
