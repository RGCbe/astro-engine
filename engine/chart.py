"""
Chart object — single entry point for the whole engine.

Usage:
    from engine.chart import compute_chart
    chart = compute_chart(
        date="1996-05-25", time="20:25", tz_hours=5.5,
        place="Kovilpalayam, Coimbatore",
    )
    print(chart.summary())

Wraps:
    - geocoding (engine.geocode)
    - swisseph sidereal positions + ascendant
    - all 16 vargas (engine.vargas)
    - KP sub-lord chart (engine.kp_sublord)
    - Vimshottari + Ashtottari dasha (engine.dasha)
    - 12 yoga detectors (engine.yogas)
    - Shadbala (engine.shadbala)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, asdict
from typing import Any

import swisseph as swe

from engine.geocode import geocode
from engine.vargas import all_vargas, vargottama
from engine.kp_sublord import get_kp_chart
from engine.dasha import (
    ashtottari, current_dasha, vimshottari,
)

# 27-nakshatra → dasha lord mapping (Ketu starts from Ashvini).
# NAKSHATRA_LORDS_VIMSHOTTARI in dasha.py is the 9-lord *sequence*, not a
# 27-element lookup. Build the full 27-entry table here.
_VIMSHOTTARI_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars",
                          "Rahu", "Jupiter", "Saturn", "Mercury"]
NAKSHATRA_LORD_TABLE: list[str] = [
    _VIMSHOTTARI_SEQUENCE[i % 9] for i in range(27)
]
from engine.yogas import detect_all as detect_yogas
from engine.shadbala import compute as compute_shadbala, summary as bala_summary

from pathlib import Path
EPHE_PATH = str(Path(__file__).parent.parent / "ephe")
swe.set_ephe_path(EPHE_PATH)
swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)

from engine.constants import SIGNS, NAKSHATRAS, SIGN_LORDS, SIGNS_TAMIL


BODIES = [
    ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS),
    ("Mercury", swe.MERCURY), ("Jupiter", swe.JUPITER),
    ("Venus", swe.VENUS), ("Saturn", swe.SATURN),
    ("Rahu", swe.MEAN_NODE),
]


@dataclass
class Chart:
    name: str
    birth_dt: dt.datetime
    place: str
    lat: float
    lon: float
    tz_hours: float
    ayanamsa: float
    lagna_lon: float
    lagna_sign: str
    lagna_lord: str
    lagna_nakshatra: str
    positions: dict[str, float]
    house_of: dict[str, int]
    nakshatras: dict[str, dict]
    kp: dict[str, dict]
    vargas: dict[str, dict]
    vargottama: list[str]
    yogas: list
    shadbala: dict
    bala_summary: dict
    vimshottari_periods: list
    ashtottari_periods: list
    current_md: str | None
    current_ad: str | None
    current_md_end: str | None

    def summary(self) -> dict:
        """JSON-friendly compact summary."""
        return {
            "name": self.name,
            "birth": {
                "datetime": self.birth_dt.isoformat(),
                "place": self.place,
                "coords": [self.lat, self.lon, self.tz_hours],
            },
            "ayanamsa": round(self.ayanamsa, 4),
            "lagna": {
                "sign": self.lagna_sign, "lord": self.lagna_lord,
                "nakshatra": self.lagna_nakshatra,
                "longitude": round(self.lagna_lon, 4),
            },
            "moon_sign": self.nakshatras["Moon"]["sign"],
            "janma_nakshatra": self.nakshatras["Moon"]["name"],
            "janma_pada": self.nakshatras["Moon"]["pada"],
            "positions": {b: round(self.positions[b], 4) for b in self.positions},
            "houses": self.house_of,
            "vargottama": self.vargottama,
            "yogas": [{"name": y.name, "category": y.category,
                       "is_strong": y.is_strong} for y in self.yogas],
            "shadbala": self.bala_summary,
            "current_dasha": {
                "vimshottari_md": self.current_md,
                "vimshottari_ad": self.current_ad,
                "vimshottari_md_ends": self.current_md_end,
            },
        }


def _info(lon: float) -> dict:
    lon = lon % 360  # normalise to [0, 360)
    sign_idx = int(lon // 30)
    sign_deg = lon - sign_idx * 30
    nak_idx = int(lon / (360 / 27)) % 27  # clamp — 360.0 edge case gives 27
    nak_deg = lon - nak_idx * (360 / 27)
    pada = int(nak_deg / (360 / 108)) + 1
    return {
        "lon": round(lon, 4),
        "sign": SIGNS[sign_idx],
        "sign_deg": round(sign_deg, 4),
        "name": NAKSHATRAS[nak_idx],
        "pada": pada,
        "lord": NAKSHATRA_LORD_TABLE[nak_idx],
    }


def _house_of(lon: float, lagna_lon: float) -> int:
    return ((int(lon // 30) - int(lagna_lon // 30)) % 12) + 1


AYANAMSA_MODES = {
    # Standard Lahiri (Government of India 1956, refined; what we used until now)
    "lahiri": (swe.SIDM_LAHIRI, None),
    # K.S. Krishnamurti's Lahiri variant (Tamil Nadu KP / older Thirukanitham
    # software like LOGIC VISION used this — matches your printed jadhagam)
    "kp":    (swe.SIDM_KRISHNAMURTI, None),
    # True Chitrapaksha (most astronomically accurate today)
    "true_chitrapaksha": (swe.SIDM_TRUE_CITRA, None),
    # User-overridden fixed value: degrees
    # (use ayanamsa_deg=23.6792 to force exactly the printed-jadhagam offset)
}


def compute_chart(
    *,
    date: str,                 # "YYYY-MM-DD"
    time: str,                 # "HH:MM"
    tz_hours: float,
    place: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    name: str = "",
    ayanamsa: str | None = None,         # None = auto-pick by birthplace.
                                         # Pass "lahiri" / "kp" / "true_chitrapaksha"
                                         # to override.
    ayanamsa_deg: float | None = None,   # explicit override in degrees
    apply_lmt: bool | None = None,       # None = auto by ayanamsa-picker
) -> Chart:
    """Compute a full chart. Provide place name OR explicit lat/lon.

    Ayanamsa is auto-picked from birthplace by default
    (Tamil Nadu / Kerala / South AP / Sri Lanka → KP-Lahiri to match printed
    Tamil jadhagams; rest of India → standard Lahiri; outside India →
    True Chitrapaksha). Override with the `ayanamsa` argument if needed.
    """
    # Resolve coordinates
    if lat is None or lon is None:
        if not place:
            raise ValueError("Provide either lat/lon or place")
        city = geocode(place.split(",")[0].strip())
        if city is None:
            raise ValueError(f"Could not geocode '{place}'")
        lat, lon = city.lat, city.lon
        if not place:
            place = f"{city.name}, {city.country}"

    # Auto-pick ayanamsa + LMT correction
    from engine.ayanamsa_picker import pick as _pick_ayanamsa
    _choice = _pick_ayanamsa(lat, lon, tz_hours, tradition_hint=ayanamsa)
    if ayanamsa_deg is None and _choice.pinned_deg is not None:
        ayanamsa_deg = _choice.pinned_deg
    if ayanamsa is None:
        ayanamsa = _choice.mode
    _do_lmt = apply_lmt if apply_lmt is not None else _choice.apply_lmt

    # Parse datetime
    y, m, d = (int(x) for x in date.split("-"))
    hh, mm = (int(x) for x in time.split(":"))
    birth_dt = dt.datetime(y, m, d, hh, mm)
    # Apply Local Mean Time correction if the picker says so
    # (printed Tamil-Nadu jadhagams effectively used LMT).
    lmt_offset_hours = (_choice.lmt_correction_minutes / 60.0) if _do_lmt else 0.0
    hour_ut = (hh + mm / 60) - tz_hours - lmt_offset_hours
    jd_ut = swe.julday(y, m, d, hour_ut)

    if ayanamsa_deg is not None:
        # User-pinned ayanamsa value (e.g. printed jadhagam's 23.6792°).
        # We set sid mode to USER and pass the offset at J2000.
        # Compute reference value at jd_ut by linear approximation: ayanamsa
        # increases by ~50.27"/yr ≈ 0.01396°/yr.
        years_from_2000 = (jd_ut - 2451545.0) / 365.25
        # Solve: at jd_ut we want = ayanamsa_deg, so j2000_value = ayanamsa_deg - rate*years
        j2000_value = ayanamsa_deg - 0.01396 * years_from_2000
        swe.set_sid_mode(swe.SIDM_USER, 2451545.0, j2000_value)
        ayanamsa_value = ayanamsa_deg
    else:
        mode, _ = AYANAMSA_MODES.get(ayanamsa, AYANAMSA_MODES["lahiri"])
        swe.set_sid_mode(mode, 0, 0)
        ayanamsa_value = swe.get_ayanamsa_ut(jd_ut)
    ayanamsa = ayanamsa_value

    # Positions
    positions: dict[str, float] = {}
    for body_name, code in BODIES:
        pos, _ = swe.calc_ut(jd_ut, code, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        positions[body_name] = pos[0]
    positions["Ketu"] = (positions["Rahu"] + 180.0) % 360

    # Ascendant
    houses, ascmc = swe.houses_ex(jd_ut, lat, lon, b"P", swe.FLG_SIDEREAL)
    lagna_lon = ascmc[0]

    lagna_info = _info(lagna_lon)
    lagna_lord = SIGN_LORDS[lagna_info["sign"]]

    # Per-body info
    nak_info = {b: _info(p) for b, p in positions.items()}
    house_of = {b: _house_of(p, lagna_lon) for b, p in positions.items()}

    # KP chart — needs lagna_idx + positions + house_of
    try:
        _kp_natal = {
            "lagna_idx": int(lagna_lon // 30),
            "lagna_lon": lagna_lon,
            "positions": positions,
            "house_of": {b: _house_of(p, lagna_lon) for b, p in positions.items()},
        }
        kp = get_kp_chart(_kp_natal)
    except Exception:
        kp = {}

    # All 16 vargas per body computed properly using the divisional charts engine
    from engine.vargas import build_divisional_chart, VARGA_LIST
    
    mini_natal = {
        "name": name,
        "birth": {"year": birth_dt.year, "month": birth_dt.month, "day": birth_dt.day, "hour": birth_dt.hour, "min": birth_dt.minute},
        "lagna_idx": int(lagna_lon // 30),
        "lagna_lon": lagna_lon,
        "lagna_deg": lagna_lon % 30,
        "positions": {
            b: {
                "rasi_idx": int(p // 30),
                "deg": p % 30,
                "lon_abs": p,
            } for b, p in positions.items()
        }
    }
    
    vargas_by_vname = all_vargas(mini_natal)
    
    vargas = {}
    for b in positions:
        vargas[b] = {}
        for vname in VARGA_LIST:
            d_chart = vargas_by_vname.get(vname)
            if d_chart and "positions" in d_chart:
                p_data = d_chart["positions"].get(b)
                if p_data:
                    vargas[b][vname] = {
                        "sign": SIGNS_TAMIL[p_data["rasi_idx"]],
                        "rasi": SIGNS_TAMIL[p_data["rasi_idx"]],
                        "longitude": p_data.get("lon_abs") or (p_data["rasi_idx"] * 30 + p_data["deg"])
                    }

    # Vargottama (only for the 7 traditional planets, exclude shadow nodes)
    vg = []
    for b in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        if b in vargas and "D1" in vargas[b] and "D9" in vargas[b]:
            if vargas[b]["D1"]["sign"] == vargas[b]["D9"]["sign"]:
                vg.append(b)

    # Yoga detection
    chart_for_yogas = {"lagna": lagna_lon, "positions": positions}
    yogas = detect_yogas(chart_for_yogas)

    # Shadbala — full 6-fold including Cheshta + Drig + saptavargaja
    try:
        bala = compute_shadbala(positions, lagna_lon, jd_ut, vargas_dict=vargas)
        bsumm = bala_summary(bala)
    except Exception:
        bala = {}
        bsumm = {}

    # Dasha
    v_periods = vimshottari(positions["Moon"], birth_dt)
    try:
        a_periods = ashtottari(_fake)
    except Exception:
        a_periods = []
    today = dt.datetime.now()
    # current_dasha() expects a chart dict, not raw periods
    _moon_lon_val = positions["Moon"]
    _b = {"year": birth_dt.year, "month": birth_dt.month, "day": birth_dt.day,
          "hour": birth_dt.hour, "min": birth_dt.minute}
    _fake = {"positions": {"Moon": {"lon": _moon_lon_val, "lon_abs": _moon_lon_val}},
             "birth": _b}
    _active = current_dasha(_fake, today)
    _md_block = _active.get("md")
    _ad_block = _active.get("ad")
    _cur_md     = (_md_block.get("md") or _md_block.get("lord")) if _md_block else None
    _cur_ad     = (_ad_block.get("ad") or _ad_block.get("lord")) if _ad_block else None
    _cur_md_end = _md_block.get("end") if _md_block else None

    return Chart(
        name=name,
        birth_dt=birth_dt,
        place=place or f"{lat},{lon}",
        lat=lat, lon=lon, tz_hours=tz_hours,
        ayanamsa=ayanamsa,
        lagna_lon=lagna_lon,
        lagna_sign=lagna_info["sign"],
        lagna_lord=lagna_lord,
        lagna_nakshatra=lagna_info["name"],
        positions=positions,
        house_of=house_of,
        nakshatras=nak_info,
        kp=kp,
        vargas=vargas,
        vargottama=vg,
        yogas=yogas,
        shadbala={b: asdict(s) for b, s in bala.items()},
        bala_summary=bsumm,
        vimshottari_periods=v_periods,
        ashtottari_periods=a_periods,
        current_md=_cur_md,
        current_ad=_cur_ad,
        current_md_end=_cur_md_end.isoformat()[:10] if _cur_md_end else None,
    )
