"""
Shared sidereal chart computation for main.py and runtime engines.

Single source for: Julian day (with tz), planet positions, Gulika/Mandi, Lagna.
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import swisseph as swe

_ROOT = Path(__file__).resolve().parent.parent
_RULES_PATH = _ROOT / "logic_base" / "rule_engine.json"
with open(_RULES_PATH, "r", encoding="utf-8") as _f:
    RULES = json.load(_f)

RASIS = list(RULES["rasi_descriptions"].keys())
NAKSHATRAS = list(RULES["nakshatra_descriptions"].keys())

DEFAULT_TZ_HOURS = 5.5  # IST; override per birth place

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mars": swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS,
    "Saturn": swe.SATURN,
    "Rahu": swe.MEAN_NODE,
}

SEVEN_GRAHAS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn", "Mercury": "Virgo",
    "Jupiter": "Cancer", "Venus": "Pisces", "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio",
}

DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer", "Mercury": "Pisces",
    "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus",
}


def parse_birth_time(time_str: str) -> tuple[int, int, float]:
    hrs, mins = map(int, time_str.split(":"))
    return hrs, mins, hrs + mins / 60.0


def ut_hour_from_local(decimal_hour: float, tz_hours: float) -> float:
    """Convert local civil time to UT hours for swe.julday."""
    return decimal_hour - tz_hours


def julday_from_birth(
    year: int, month: int, day: int, time_str: str, tz_hours: float = DEFAULT_TZ_HOURS
) -> tuple[float, int, int, float]:
    hrs, mins, decimal_hour = parse_birth_time(time_str)
    jd = swe.julday(year, month, day, ut_hour_from_local(decimal_hour, tz_hours))
    return jd, hrs, mins, decimal_hour


def get_dignity(planet: str, rasi: str) -> str:
    if EXALTATION.get(planet) == rasi:
        return "Exalted"
    if DEBILITATION.get(planet) == rasi:
        return "Debilitated"
    return "Neutral"


def get_gulika_mandi_time(
    year: int, month: int, day: int, decimal_hour: float, lat: float, lon: float,
    tz_hours: float = DEFAULT_TZ_HOURS,
) -> tuple[float, float]:
    jd_noon = swe.julday(year, month, day, 6.0)
    _, tret_rise = swe.rise_trans(jd_noon, swe.SUN, swe.CALC_RISE, (lon, lat, 0))
    s1 = tret_rise[0]
    _, tret_set = swe.rise_trans(jd_noon, swe.SUN, swe.CALC_SET, (lon, lat, 0))
    s2 = tret_set[0]
    _, tret_rise_next = swe.rise_trans(jd_noon + 1, swe.SUN, swe.CALC_RISE, (lon, lat, 0))
    s3 = tret_rise_next[0]

    jd_birth = swe.julday(year, month, day, ut_hour_from_local(decimal_hour, tz_hours))

    dt_birth = dt.date(year, month, day)
    vedic_weekday = (dt_birth.weekday() + 1) % 7

    if jd_birth < s1:
        vedic_weekday = (vedic_weekday - 1) % 7
        _, tret_rise_prev = swe.rise_trans(jd_noon - 1, swe.SUN, swe.CALC_RISE, (lon, lat, 0))
        s3, s2, s1 = s2, s1, tret_rise_prev[0]

    is_daytime = s1 <= jd_birth < s2
    day_saturn = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0}
    night_saturn = {0: 2, 1: 1, 2: 0, 3: 6, 4: 5, 5: 4, 6: 3}

    if is_daytime:
        part_dur = (s2 - s1) / 8.0
        part_idx = day_saturn[vedic_weekday]
        jd_gulika = s1 + part_idx * part_dur
        jd_mandi = s1 + (part_idx + 0.5) * part_dur
    elif jd_birth >= s2:
        part_dur = (s3 - s2) / 8.0
        part_idx = night_saturn[vedic_weekday]
        jd_gulika = s2 + part_idx * part_dur
        jd_mandi = s2 + (part_idx + 0.5) * part_dur
    else:
        part_dur = (s2 - s1) / 8.0
        part_idx = night_saturn[vedic_weekday]
        jd_gulika = s1 + part_idx * part_dur
        jd_mandi = s1 + (part_idx + 0.5) * part_dur

    asc_gul = swe.houses_ex(jd_gulika, lat, lon, b"P")[0][0]
    asc_man = swe.houses_ex(jd_mandi, lat, lon, b"P")[0][0]
    lon_gul = (asc_gul - swe.get_ayanamsa_ut(jd_gulika)) % 360
    lon_man = (asc_man - swe.get_ayanamsa_ut(jd_mandi)) % 360
    return lon_gul, lon_man


def make_planet_data(name: str, longitude: float) -> dict:
    longitude = longitude % 360
    rasi_idx = int(longitude / 30)
    nakshatra_idx = int(longitude / (360 / 27))
    pada = int((longitude % (360 / 27)) / (360 / 108)) + 1
    rasi_name = RASIS[rasi_idx]
    nakshatra_name = NAKSHATRAS[nakshatra_idx]
    nav_rasi_idx = int(longitude / (10 / 3)) % 12
    nav_rasi_name = RASIS[nav_rasi_idx]
    d10_part = int((longitude % 30) / 3)
    d10_rasi_idx = (rasi_idx + d10_part) % 12 if rasi_idx % 2 == 0 else (rasi_idx + 8 + d10_part) % 12
    d60_part = int((longitude % 30) / 0.5)
    d60_rasi_idx = (rasi_idx + d60_part) % 12
    return {
        "longitude": round(longitude, 4),
        "rasi": rasi_name,
        "rasi_tamil": RULES["rasi_descriptions"][rasi_name]["tamil"],
        "d1_dignity": get_dignity(name, rasi_name),
        "nakshatra": nakshatra_name,
        "nakshatra_pada": pada,
        "nakshatra_lord": RULES["nakshatra_descriptions"].get(nakshatra_name, {}).get("lord", ""),
        "navamsa_rasi": nav_rasi_name,
        "navamsa_rasi_tamil": RULES["rasi_descriptions"][nav_rasi_name]["tamil"],
        "d9_dignity": get_dignity(name, nav_rasi_name),
        "is_vargottama": rasi_name == nav_rasi_name,
        "dasamsa_rasi": RASIS[d10_rasi_idx],
        "shashtiamsa_rasi": RASIS[d60_rasi_idx],
    }


def build_sidereal_chart(
    year: int,
    month: int,
    day: int,
    time_str: str,
    lat: float,
    lon: float,
    tz_hours: float = DEFAULT_TZ_HOURS,
    *,
    tradition_hint: str | None = None,
    ayanamsa_deg: float | None = None,
) -> dict:
    """Full planet_positions + ascendant metadata for jathagam.

    Ayanamsa defaults by birthplace (TN/Kerala → Thirukanitham print tradition;
    rest of India → Lahiri). Pass tradition_hint='lahiri' for modern pan-India apps.
    """
    from engine.ayanamsa_picker import configure_swe_ayanamsa, resolve_for_birthplace

    jd, hrs, mins, decimal_hour = julday_from_birth(year, month, day, time_str, tz_hours)
    choice, pin_deg = resolve_for_birthplace(
        lat, lon, tz_hours, tradition_hint=tradition_hint, ayanamsa_deg=ayanamsa_deg
    )
    ayanamsa_value = configure_swe_ayanamsa(jd, choice, pinned_deg=pin_deg)

    planet_positions = {}
    for name, planet_id in PLANETS.items():
        pos, _ = swe.calc_ut(jd, planet_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        planet_positions[name] = make_planet_data(name, pos[0])

    ak_planet = max(SEVEN_GRAHAS, key=lambda p: planet_positions[p]["longitude"] % 30)
    for p in SEVEN_GRAHAS:
        planet_positions[p]["is_atmakaraka"] = (p == ak_planet)

    rahu_lon = planet_positions["Rahu"]["longitude"]
    planet_positions["Ketu"] = make_planet_data("Ketu", (rahu_lon + 180) % 360)

    lon_gulika, lon_mandi = get_gulika_mandi_time(
        year, month, day, decimal_hour, lat, lon, tz_hours
    )
    planet_positions["Gulika"] = make_planet_data("Gulika", lon_gulika)
    planet_positions["Mandi"] = make_planet_data("Mandi", lon_mandi)

    asc = swe.houses_ex(jd, lat, lon, b"P")[0][0]
    asc_sid = (asc - swe.get_ayanamsa_ut(jd)) % 360
    lagnam_rasi = RASIS[int(asc_sid / 30)]
    planet_positions["Lagna"] = make_planet_data("Lagna", asc_sid)

    lagnam_idx = RASIS.index(lagnam_rasi)
    for pname, pdata in planet_positions.items():
        p_rasi_idx = RASIS.index(pdata["rasi"])
        pdata["house"] = ((p_rasi_idx - lagnam_idx) % 12) + 1
    planet_positions["Lagna"]["house"] = 1

    nav_lagna_idx = int(asc_sid / (10 / 3)) % 12
    lagna_lord = SIGN_LORD[int(asc_sid / 30)]
    lord_lon = planet_positions[lagna_lord]["longitude"]
    lord_house_idx = int(lord_lon / 30)
    lagna_house_idx = int(asc_sid / 30)
    dist = (lord_house_idx - lagna_house_idx) % 12
    al_idx = (lord_house_idx + dist) % 12

    return {
        "jd": jd,
        "hrs": hrs,
        "mins": mins,
        "decimal_hour": decimal_hour,
        "tz_hours": tz_hours,
        "ayanamsa": round(ayanamsa_value, 4),
        "ayanamsa_mode": choice.mode,
        "ayanamsa_name": choice.name,
        "planet_positions": planet_positions,
        "asc_sid": asc_sid,
        "lagnam_rasi": lagnam_rasi,
        "lagnam_idx": lagnam_idx,
        "navamsa_lagnam": RASIS[nav_lagna_idx],
        "arudha_lagna": RASIS[al_idx],
        "janma_rasi": planet_positions["Moon"]["rasi"],
        "janma_nakshatra": planet_positions["Moon"]["nakshatra"],
        "birth_dt": dt.datetime(year, month, day, hrs, mins),
    }


def build_orchestrator_chart_dict(
    year: int,
    month: int,
    day: int,
    time_str: str,
    lat: float,
    lon: float,
    tz_hours: float = DEFAULT_TZ_HOURS,
    *,
    tradition_hint: str | None = None,
    ayanamsa_deg: float | None = None,
) -> dict:
    """Slim chart dict for category_engine / pure_classical / hybrid."""
    core = build_sidereal_chart(
        year, month, day, time_str, lat, lon, tz_hours,
        tradition_hint=tradition_hint,
        ayanamsa_deg=ayanamsa_deg,
    )
    pp = core["planet_positions"]
    return {
        "birth": {
            "year": year,
            "month": month,
            "day": day,
            "hour": core["hrs"],
            "min": core["mins"],
            "lat": lat,
            "lon": lon,
            "tz_hours": tz_hours,
        },
        "ayanamsa": core.get("ayanamsa"),
        "ayanamsa_mode": core.get("ayanamsa_mode"),
        "ayanamsa_name": core.get("ayanamsa_name"),
        "lagna_idx": int(core["asc_sid"] / 30) % 12,
        "positions": {
            p: {
                "deg": d["longitude"] % 30,
                "rasi_idx": int(d["longitude"] / 30) % 12,
                "rasi": d["rasi"],
                "lon": d["longitude"],
                "longitude": d["longitude"],
                "house": d["house"],
            }
            for p, d in pp.items()
            if p not in ("Gulika", "Mandi")
        },
    }
