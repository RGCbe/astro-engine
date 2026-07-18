"""
Gochara — transit triggers.

Slow planets (Saturn, Jupiter, Rahu/Ketu, Mars) transiting natal sensitive
points narrow event windows from MD-AD scale (years) to month-scale.

Implemented:
    saturn_returns(natal_dt, n_returns=3)
        — Saturn-on-natal-Saturn returns at ages ~29, ~58, ~87.
    sade_sati_windows(natal_moon_lon, search_start, search_end)
        — Saturn transits the 12th, 1st, 2nd from natal Moon (Sade Sati,
          7.5 yrs total). Each phase ~2.5 yrs.
    jupiter_transits_house(natal_lagna_lon, search_start, search_end, house)
        — Jupiter passes through the sign of the requested natal house.
    transit_triggers_at(at_dt, natal_chart, planets=...)
        — what each transit planet is doing relative to natal points NOW.

Per the truth-only directive: returned trigger windows are reported with
their dates only — never wrapped in "auspicious" or "inauspicious"
adjectives. The reading layer assigns meaning via classical association,
labeled with confidence.
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
PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,
}

# Approximate sidereal periods (years) — used as initial step for searches
PLANET_PERIOD_YRS = {
    "Sun": 1.0, "Moon": 0.075, "Mars": 1.88, "Mercury": 0.24,
    "Jupiter": 11.86, "Venus": 0.615, "Saturn": 29.46,
    "Rahu": 18.6, "Ketu": 18.6,
}


def _sidereal_lon(jd_ut: float, planet: str) -> float:
    if planet == "Ketu":
        pos, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE,
                             swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        return (pos[0] + 180) % 360
    pos, _ = swe.calc_ut(jd_ut, PLANET_IDS[planet],
                         swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    return pos[0] % 360


def _datetime_to_jd(d: dt.datetime, tz: float = 0.0) -> float:
    h = d.hour + d.minute / 60 + d.second / 3600 - tz
    return swe.julday(d.year, d.month, d.day, h)


def _jd_to_datetime(jd: float) -> dt.datetime:
    y, m, d, h = swe.revjul(jd, swe.GREG_CAL)
    hh = int(h); mm = int((h - hh) * 60); ss = int(((h - hh) * 60 - mm) * 60)
    return dt.datetime(int(y), int(m), int(d), hh, mm, ss)


# ─── Sign-ingress finder ───────────────────────────────────────────────────
@dataclass
class SignIngress:
    planet: str
    from_sign: str
    to_sign: str
    moment: dt.datetime


def _find_sign_changes(planet: str, start_dt: dt.datetime, end_dt: dt.datetime,
                       step_days: int = 7) -> list[SignIngress]:
    """Scan in step_days, refine each sign change to ~1 minute precision."""
    jd_start = _datetime_to_jd(start_dt)
    jd_end = _datetime_to_jd(end_dt)
    out: list[SignIngress] = []
    jd = jd_start
    prev_sign = int(_sidereal_lon(jd, planet) // 30)
    while jd < jd_end:
        nxt = min(jd + step_days, jd_end)
        cur_sign = int(_sidereal_lon(nxt, planet) // 30)
        if cur_sign != prev_sign:
            # Bisect for exact ingress
            lo, hi = jd, nxt
            for _ in range(40):
                mid = (lo + hi) / 2
                m_sign = int(_sidereal_lon(mid, planet) // 30)
                if m_sign == prev_sign:
                    lo = mid
                else:
                    hi = mid
            ingress_jd = (lo + hi) / 2
            out.append(SignIngress(
                planet=planet,
                from_sign=SIGN_NAMES[prev_sign],
                to_sign=SIGN_NAMES[cur_sign],
                moment=_jd_to_datetime(ingress_jd),
            ))
            prev_sign = cur_sign
        jd = nxt
    return out


# ─── Saturn returns ────────────────────────────────────────────────────────
@dataclass
class SaturnReturn:
    return_index: int       # 1 = first (~age 29), 2 = second (~58), 3 = third
    moment: dt.datetime
    age_years: float


def saturn_returns(natal_dt: dt.datetime, n_returns: int = 3,
                   tz_hours: float = 0.0) -> list[SaturnReturn]:
    """Find dates Saturn returns to natal Saturn longitude."""
    natal_jd = _datetime_to_jd(natal_dt, tz_hours)
    natal_sat = _sidereal_lon(natal_jd, "Saturn")
    out: list[SaturnReturn] = []
    for i in range(1, n_returns + 1):
        target_jd = natal_jd + i * PLANET_PERIOD_YRS["Saturn"] * 365.25
        # ±1 yr search window
        lo = target_jd - 365
        hi = target_jd + 365

        def signed_diff(jd):
            d = (_sidereal_lon(jd, "Saturn") - natal_sat + 540) % 360 - 180
            return d

        # Coarse scan to find zero crossing
        prev = signed_diff(lo)
        zero_jd = None
        scan_jd = lo
        while scan_jd < hi:
            scan_jd += 7
            cur = signed_diff(scan_jd)
            if prev * cur < 0:
                # Bisect
                a, b = scan_jd - 7, scan_jd
                for _ in range(40):
                    m = (a + b) / 2
                    if signed_diff(a) * signed_diff(m) <= 0:
                        b = m
                    else:
                        a = m
                zero_jd = (a + b) / 2
                break
            prev = cur
        if zero_jd is None:
            continue
        moment = _jd_to_datetime(zero_jd)
        age = (zero_jd - natal_jd) / 365.25
        out.append(SaturnReturn(return_index=i, moment=moment, age_years=round(age, 2)))
    return out


# ─── Sade Sati ─────────────────────────────────────────────────────────────
@dataclass
class SadeSatiPhase:
    phase: str             # "Rising (12th from Moon)" | "Peak (1st)" | "Setting (2nd)"
    sign: str
    start: dt.datetime
    end: dt.datetime


def sade_sati_windows(
    natal_moon_lon: float,
    search_start: dt.datetime,
    search_end: dt.datetime,
) -> list[SadeSatiPhase]:
    """Saturn's 7.5-year transit through 12th/1st/2nd from natal Moon."""
    moon_sign = int(natal_moon_lon // 30)
    target_signs = {
        (moon_sign - 1) % 12: "Rising (12th from Moon)",
        moon_sign:              "Peak (Moon sign)",
        (moon_sign + 1) % 12:   "Setting (2nd from Moon)",
    }
    ingresses = _find_sign_changes("Saturn", search_start, search_end, step_days=15)

    # Build (sign, start, end) windows
    out: list[SadeSatiPhase] = []
    if not ingresses:
        return out
    # Pre-pad with the sign at search_start
    cur_sign = int(_sidereal_lon(_datetime_to_jd(search_start), "Saturn") // 30)
    cur_start = search_start
    for ing in ingresses:
        if cur_sign in target_signs:
            out.append(SadeSatiPhase(
                phase=target_signs[cur_sign],
                sign=SIGN_NAMES[cur_sign],
                start=cur_start, end=ing.moment,
            ))
        cur_sign = SIGN_NAMES.index(ing.to_sign)
        cur_start = ing.moment
    if cur_sign in target_signs:
        out.append(SadeSatiPhase(
            phase=target_signs[cur_sign],
            sign=SIGN_NAMES[cur_sign],
            start=cur_start, end=search_end,
        ))
    return out


# ─── Jupiter transits a given sign ─────────────────────────────────────────
@dataclass
class TransitWindow:
    planet: str
    sign: str
    start: dt.datetime
    end: dt.datetime
    house_from_lagna: int


def jupiter_transits_sign(
    sign_idx: int,
    natal_lagna_sign: int,
    search_start: dt.datetime,
    search_end: dt.datetime,
) -> list[TransitWindow]:
    """All Jupiter windows where it occupies `sign_idx` within the search range."""
    ingresses = _find_sign_changes("Jupiter", search_start, search_end, step_days=15)
    out: list[TransitWindow] = []
    cur_sign = int(_sidereal_lon(_datetime_to_jd(search_start), "Jupiter") // 30)
    cur_start = search_start
    for ing in ingresses:
        if cur_sign == sign_idx:
            out.append(TransitWindow(
                planet="Jupiter",
                sign=SIGN_NAMES[cur_sign],
                start=cur_start, end=ing.moment,
                house_from_lagna=((cur_sign - natal_lagna_sign) % 12) + 1,
            ))
        cur_sign = SIGN_NAMES.index(ing.to_sign)
        cur_start = ing.moment
    if cur_sign == sign_idx:
        out.append(TransitWindow(
            planet="Jupiter", sign=SIGN_NAMES[cur_sign],
            start=cur_start, end=search_end,
            house_from_lagna=((cur_sign - natal_lagna_sign) % 12) + 1,
        ))
    return out


# ─── Snapshot at a moment ──────────────────────────────────────────────────
def transit_snapshot(
    at_dt: dt.datetime,
    natal_lagna_sign: int,
    natal_positions: dict[str, float],
    tz_hours: float = 0.0,
) -> dict:
    """What's transiting where, RIGHT NOW, relative to natal positions."""
    jd = _datetime_to_jd(at_dt, tz_hours)
    out = {"moment": at_dt.isoformat()[:19], "transits": []}
    for planet in ("Mars", "Jupiter", "Saturn", "Rahu", "Ketu"):
        try:
            lon = _sidereal_lon(jd, planet)
        except Exception:
            continue
        sign = int(lon // 30)
        house = ((sign - natal_lagna_sign) % 12) + 1
        # Distance to nearest natal point
        nearest = None
        nearest_dist = 999
        for npname, nlon in natal_positions.items():
            diff = abs((lon - nlon + 540) % 360 - 180)
            if diff < nearest_dist:
                nearest = npname
                nearest_dist = diff
        out["transits"].append({
            "planet": planet,
            "sign": SIGN_NAMES[sign],
            "longitude": round(lon, 2),
            "house_from_natal_lagna": house,
            "nearest_natal_point": nearest,
            "orb_to_natal_deg": round(nearest_dist, 2),
            "tight_aspect": nearest_dist < 3.0,    # within 3° = significant
        })
    return out
