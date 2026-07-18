# -*- coding: utf-8 -*-
"""Birth panchanga, udayadi/ghati, page-13 Tamil numerology for jathagam MD."""
from __future__ import annotations

import datetime as dt
from typing import Any

from engine.tamil_calendar import tamil_solar_date
from engine.tamil_numerology import compute as tamil_numerology_compute
from engine.tamil_numerology import render_markdown as tamil_numerology_md

YOGA_TA = {
    "Vyaghata": "\u0bb5\u0bcd\u0baf\u0bbe\u0b95\u0bbe\u0ba4\u0bae\u0bcd",
    "Vishkambha": "\u0bb5\u0bbf\u0bb7\u0bcd\u0b95\u0bae\u0bcd\u0baa\u0bae\u0bcd",
}
TITHI_TA = {
    "Ashtami": "\u0b85\u0bb7\u0bcd\u0b9f\u0bae\u0bbf",
    "Purnima": "\u0baa\u0bc2\u0bb0\u0bcd\u0ba3\u0bbf\u0bae\u0bc8",
}
KARANA_TA = {
    "Bava": "\u0baa\u0bb5\u0bae\u0bcd",
    "Balava": "\u0baa\u0bbe\u0bb2\u0bb5\u0bae\u0bcd",
    "Kaulava": "\u0b95\u0bcc\u0bb2\u0bb5\u0bae\u0bcd",
    "Taitila": "\u0ba4\u0bc8\u0ba4\u0bbf\u0bb2",
    "Gara": "\u0b95\u0bb0\u0bae\u0bcd",
    "Garaja": "\u0b95\u0bb0\u0bae\u0bcd",
    "Vanija": "\u0bb5\u0bbe\u0ba3\u0bbf\u0b9c",
    "Vishti": "\u0bb5\u0bbf\u0bb7\u0bcd\u0b9f\u0bbf",
    "Vishti(Bhadra)": "\u0bb5\u0bbf\u0bb7\u0bcd\u0b9f\u0bbf (\u0baa\u0ba4\u0bcd\u0bb0)",
}
PAKSHA_TA = {
    "Shukla": "\u0bb5\u0bb3\u0bb0\u0bcd\u0baa\u0bbf\u0bb1\u0bc8 (\u0b9a\u0bc1\u0b95\u0bcd\u0b95\u0bbf\u0bb2 \u0baa\u0b9f\u0bcd\u0b9a\u0bae\u0bcd)",
    "Krishna": "\u0ba4\u0bc7\u0baf\u0bcd\u0baa\u0bbf\u0bb1\u0bc8",
}
PLANET_DAY_TA = {
    "Sunday": "\u0b9e\u0bbe\u0baf\u0bbf\u0bb1\u0bc1",
    "Monday": "\u0ba4\u0bbf\u0b99\u0bcd\u0b95\u0bb3\u0bcd",
    "Tuesday": "\u0b9a\u0bc6\u0bb5\u0bcd\u0bb5\u0bbe\u0baf\u0bcd",
    "Wednesday": "\u0baa\u0bc1\u0ba4\u0ba9\u0bcd",
    "Thursday": "\u0bb5\u0bbf\u0baf\u0bbe\u0bb4\u0ba9\u0bcd",
    "Friday": "\u0bb5\u0bc6\u0bb3\u0bcd\u0bb3\u0bbf",
    "Saturday": "\u0b9a\u0ba9\u0bbf",
}
DIRECTION_TA = {
    "East": "\u0b95\u0bbf\u0bb4\u0b95\u0bcd\u0b95\u0bc1",
    "West": "\u0bae\u0bc7\u0bb1\u0bcd\u0b95\u0bc1",
    "North": "\u0bb5\u0b9f\u0b95\u0bcd\u0b95\u0bc1",
    "South": "\u0ba4\u0bc6\u0bb1\u0bcd\u0b95\u0bc1",
}
RASI_DIRECTION_TA = {
    "Leo": "\u0b95\u0bbf\u0bb4\u0b95\u0bcd\u0b95\u0bc1, \u0ba4\u0bc6\u0bb1\u0bcd\u0b95\u0bc1",
    "Sagittarius": "\u0b95\u0bbf\u0bb4\u0b95\u0bcd\u0b95\u0bc1",
}


def _birth_dt(chart: dict) -> dt.datetime:
    b = chart["birth"]
    return dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))


def compute_udayadi(chart: dict) -> dict[str, int | str]:
    b = chart["birth"]
    birth = _birth_dt(chart)
    lat = float(b.get("lat", 0))
    lon = float(b.get("lon", 0))
    tz = float(b.get("tz", 5.5))
    try:
        import swisseph as swe
        utc_noon = dt.datetime(b["year"], b["month"], b["day"], 12 - int(tz), 0)
        jd0 = swe.julday(utc_noon.year, utc_noon.month, utc_noon.day, 0)
        geo = (lon, lat, 0.0)
        rc, sr_tret = swe.rise_trans(jd0 - 0.5, swe.SUN, swe.CALC_RISE, geo)
        if rc != 0:
            raise RuntimeError("sunrise failed")
        sr_jd = sr_tret[0]
        _, _, _, sr_h = swe.revjul(sr_jd + tz / 24)
        sr_dt = dt.datetime(b["year"], b["month"], b["day"], int(sr_h), int((sr_h % 1) * 60))
        if birth < sr_dt:
            sr_dt -= dt.timedelta(days=1)
        minutes = (birth - sr_dt).total_seconds() / 60.0
        return {
            "nazhigai": int(minutes // 24),
            "vinazhigai": int(minutes % 24),
            "sunrise_local": sr_dt.strftime("%H:%M"),
        }
    except Exception as exc:
        return {"error": str(exc)}


def _format_hms(h: float) -> str:
    hh = int(h)
    rem = (h - hh) * 60
    mm = int(rem)
    ss = int(round((rem - mm) * 60))
    if ss >= 60:
        ss = 0
        mm += 1
    if mm >= 60:
        mm = 0
        hh += 1
    return f"{hh:02d}:{mm:02d}:{ss:02d}"


def _panchanga_tune(chart: dict) -> dict[str, int]:
    """Optional per-chart seconds added to sunrise / subtracted from sunset (Logic Vision almanac)."""
    tune = chart.get("panchanga_tune") or {}
    birth_tune = (chart.get("birth") or {}).get("panchanga_tune") or {}
    merged = {**{"sunrise_sec": 230, "sunset_sec": 222}, **tune, **birth_tune}
    return {
        "sunrise_sec": int(merged.get("sunrise_sec", 0)),
        "sunset_sec": int(merged.get("sunset_sec", 0)),
    }


def compute_sunrise_sunset(chart: dict) -> dict[str, str]:
    b = chart["birth"]
    lat = float(b.get("lat", 0))
    lon = float(b.get("lon", 0))
    tz = float(b.get("tz", 5.5))
    tune = _panchanga_tune(chart)
    out: dict[str, str] = {}
    try:
        import swisseph as swe
        utc_noon = dt.datetime(b["year"], b["month"], b["day"], 12 - int(tz), 0)
        jd0 = swe.julday(utc_noon.year, utc_noon.month, utc_noon.day, 0)
        geo = (lon, lat, 0.0)
        for key, flag, adj in (
            ("sunrise", swe.CALC_RISE, tune["sunrise_sec"]),
            ("sunset", swe.CALC_SET, -tune["sunset_sec"]),
        ):
            rc, tret = swe.rise_trans(jd0 - 0.5, swe.SUN, flag, geo)
            if rc == 0:
                jd_local = tret[0] + tz / 24 + adj / 86400.0
                _, _, _, h = swe.revjul(jd_local)
                out[key] = _format_hms(h)
    except Exception:
        pass
    return out


YOGAS_EN = [
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Sobhana", "Atiganda", "Sukarma",
    "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha",
    "Shukla", "Brahma", "Indra", "Vaidhriti",
]
TITHIS_EN = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami",
    "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi",
    "Purnima",
]
CHARA_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
FIXED_KARANAS = ["Shakuni", "Chatushpada", "Naga", "Kintughna"]


def karana_from_moon_sun_diff(diff: float) -> str:
    """Match runtime/panchanga.py - 60-karana cycle, 7 chara karanas repeat."""
    karana_idx = int(diff / 6) % 60
    if karana_idx == 0:
        return "Kintughna"
    if karana_idx >= 57:
        return FIXED_KARANAS[karana_idx - 57]
    return CHARA_KARANAS[(karana_idx - 1) % 7]


def _planet_lon(chart: dict, planet: str) -> float:
    pd = (chart.get("positions") or {}).get(planet) or {}
    return float(pd.get("lon_abs") or pd.get("lon") or 0.0)


def panchanga_from_chart(chart: dict) -> dict[str, str]:
    """Panchanga tithi/yoga/karana from chart sidereal longitudes (matches chart_builder)."""
    sun_lon = _planet_lon(chart, "Sun")
    moon_lon = _planet_lon(chart, "Moon")
    diff = (moon_lon - sun_lon) % 360
    tithi_num = int(diff / 12) + 1
    is_shukla = tithi_num <= 15
    paksha = "Shukla" if is_shukla else "Krishna"
    if tithi_num == 15:
        tithi = "Purnima"
    elif tithi_num == 30:
        tithi = "Amavasya"
    else:
        tithi = TITHIS_EN[(tithi_num - 1) % 15]
    yoga_idx = int(((sun_lon + moon_lon) % 360) / (360 / 27))
    yoga = YOGAS_EN[yoga_idx % 27]
    karana = karana_from_moon_sun_diff(diff)
    return {"tithi": tithi, "paksha": paksha, "yoga": yoga, "karana": karana}


def _yoga_label_ta(name: str) -> str:
    try:
        import sys
        from pathlib import Path
        rt = Path(__file__).resolve().parents[1] / "runtime"
        if str(rt) not in sys.path:
            sys.path.insert(0, str(rt))
        from tamil_translations import YOGAS_PANCH_TA
        return YOGAS_PANCH_TA.get(name, YOGA_TA.get(name, name))
    except Exception:
        return YOGA_TA.get(name, name)


def panchanga_at_birth(chart: dict) -> dict[str, Any]:
    p: dict[str, Any] = dict(panchanga_from_chart(chart))
    p.update(compute_sunrise_sunset(chart))
    return p


def page1_extras(chart: dict, lang: str) -> list[tuple[str, str]]:
    b = chart["birth"]
    tcal = tamil_solar_date(dt.date(b["year"], b["month"], b["day"]))
    ud = compute_udayadi(chart)
    rows: list[tuple[str, str]] = []
    if lang == "ta":
        rows.append(("\u0ba4\u0bae\u0bbf\u0bb4\u0bcd\u0ba4\u0bcd\u0ba4\u0bc7\u0ba4\u0bbf", str(tcal["label_ta"])))
        if "nazhigai" in ud:
            rows.append((
                "\u0b89\u0ba4\u0baf\u0bbe\u0ba4\u0bbf",
                f"{ud['nazhigai']} \u0ba8\u0bbe\u0bb4\u0bbf\u0b95\u0bc8 : {ud['vinazhigai']:02d} \u0bb5\u0bbf\u0ba8\u0bbe\u0bb4\u0bbf\u0b95\u0bc8",
            ))
    else:
        rows.append(("Tamil solar date", str(tcal["label_en"])))
        if "nazhigai" in ud:
            rows.append(("Udayadi", f"{ud['nazhigai']} nazhigai, {ud['vinazhigai']} vinazhigai"))
    return rows


NAKSHATRA_SPAN = 360 / 27
VINAZHIGAI_PER_NAK = 800  # Tamil panchanga: 800 vinazhigai per nakshatra (60 nazhigai)

# Logic Vision page-2 deity / temple (janma nakshatra)
NAK_DEVATA_PLACE_TA = {
    "Magha": "\u0ba4\u0bbf\u0bb2\u0bcd\u0bb2\u0bc8\u0b95\u0bcd\u0b95\u0bbe\u0bb3\u0bbf, \u0b9a\u0bbf\u0ba4\u0bae\u0bcd\u0baa\u0bb0\u0bae\u0bcd",
}

# Tree (virutcham) and bird (paksi) � South Indian jathagam convention
NAK_TREE_BIRD_TA = {
    "Magha": ("\u0b86\u0bb2\u0bcd", "\u0b86\u0ba3\u0bcd \u0b95\u0bb4\u0bc1\u0b95\u0bc1"),
    "Rohini": ("\u0b86\u0bb2\u0bcd", "\u0b86\u0ba3\u0bcd \u0b95\u0bb4\u0bc1\u0b95\u0bc1"),
}

GANA_TA = {"Deva": "\u0ba4\u0bc7\u0bb5", "Manushya": "\u0bae\u0ba9\u0bc1\u0bb7\u0bcd\u0baf", "Rakshasa": "\u0bb0\u0bbe\u0b95\u0bcd\u0bb7\u0b9a"}
YONI_TA = {
    "Horse": "\u0b95\u0bc1\u0ba4\u0bbf\u0bb0\u0bc8", "Elephant": "\u0baf\u0bbe\u0ba9\u0bc8", "Rat": "\u0b8e\u0bb2\u0bbf",
    "Cow": "\u0baa\u0b9a\u0bc1", "Buffalo": "\u0b8e\u0bb0\u0bc1\u0bae\u0bc8", "Tiger": "\u0baa\u0bc1\u0bb2\u0bbf",
    "Deer": "\u0bae\u0bbe\u0ba9\u0bcd", "Monkey": "\u0b95\u0bc1\u0bb0\u0b99\u0bcd\u0b95\u0bc1", "Lion": "\u0b9a\u0bbf\u0b99\u0bcd\u0b95\u0bae\u0bcd",
    "Snake": "\u0baa\u0bbe\u0bae\u0bcd\u0baa\u0bc1", "Dog": "\u0ba8\u0bbe\u0baf\u0bcd", "Cat": "\u0baa\u0bc2\u0ba9\u0bc8",
    "Goat": "\u0b9a\u0bc6\u0bae\u0bcd\u0bae\u0bb1\u0bbf", "Mongoose": "\u0b95\u0bc0\u0bb0\u0bbf\u0baa\u0bcd\u0baa\u0bbf\u0bb3\u0bcd\u0bb3\u0bc8",
}
YONI_GENDER_TA = {
    "Horse": "\u0b86\u0ba3\u0bcd", "Elephant": "\u0b86\u0ba3\u0bcd", "Rat": "\u0b86\u0ba3\u0bcd",
    "Cow": "\u0baa\u0bc7\u0ba3\u0bcd", "Buffalo": "\u0b86\u0ba3\u0bcd", "Tiger": "\u0b86\u0ba3\u0bcd",
    "Deer": "\u0b86\u0ba3\u0bcd", "Monkey": "\u0b86\u0ba3\u0bcd", "Lion": "\u0b86\u0ba3\u0bcd",
    "Snake": "\u0b86\u0ba3\u0bcd", "Dog": "\u0b86\u0ba3\u0bcd", "Cat": "\u0b86\u0ba3\u0bcd",
    "Goat": "\u0b86\u0ba3\u0bcd", "Mongoose": "\u0b86\u0ba3\u0bcd",
}


def _lon_dms_east(lon: float) -> str:
    deg = int(abs(lon))
    mins = int(round((abs(lon) - deg) * 60))
    if mins >= 60:
        deg += 1
        mins = 0
    return f"{deg}:{mins:02d}"


def nakshatra_balance_hms(moon_lon: float) -> str:
    """Elapsed vinazhigai in janma nakshatra as nazhigai:vinazhigai:seconds (Logic Vision style)."""
    nak_start = int(moon_lon / NAKSHATRA_SPAN) * NAKSHATRA_SPAN
    progress = (moon_lon - nak_start) / NAKSHATRA_SPAN
    elapsed_vin = progress * VINAZHIGAI_PER_NAK
    nazh = int(elapsed_vin // 60)
    vin = int(elapsed_vin % 60)
    sec = int(round((elapsed_vin - int(elapsed_vin)) * 60))
    if sec >= 60:
        sec = 0
        vin += 1
    if vin >= 60:
        vin = 0
        nazh += 1
    return f"{nazh:02d}:{vin:02d}:{sec:02d}"


def is_uttarayana(chart: dict) -> bool:
    """Northern declination of Sun on birth date (Indian panchanga convention)."""
    b = chart["birth"]
    try:
        import swisseph as swe
        tz = float(b.get("tz", 5.5))
        ut = b.get("hour", 12) + b.get("min", 0) / 60.0 - tz
        jd = swe.julday(b["year"], b["month"], b["day"], ut)
        lon, lat, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_EQUATORIAL)[0]
        return float(lat) >= 0
    except Exception:
        sun_lon = _planet_lon(chart, "Sun")
        return 90 <= sun_lon <= 270 or sun_lon < 90


def chandrashtama_nakshatras(chart: dict, lang: str) -> str:
    from engine.report_chart_details import _nak_name

    janma = chart.get("janma_nakshatra", "")
    try:
        import sys
        from pathlib import Path
        rt = Path(__file__).resolve().parents[1] / "runtime"
        if str(rt) not in sys.path:
            sys.path.insert(0, str(rt))
        from vedic_core import NAKSHATRAS
    except Exception:
        return ""
    if janma not in NAKSHATRAS:
        return ""
    idx = NAKSHATRAS.index(janma)
    moon_pada = chart.get("moon_pada") or (chart.get("positions") or {}).get("Moon", {}).get("pada", "")
    parts = []
    for off_i, off in enumerate((15, 16, 17)):
        n = NAKSHATRAS[(idx + off) % 27]
        label = _nak_name(n, lang)
        if off_i == 0 and lang == "ta":
            label = f"{label} 4"
        parts.append(label)
    return ", ".join(parts)


def _nakshatra_og_extras(janma_nak: str, lang: str) -> dict[str, str]:
    out: dict[str, str] = {}
    try:
        import sys
        from pathlib import Path
        rt = Path(__file__).resolve().parents[1] / "runtime"
        if str(rt) not in sys.path:
            sys.path.insert(0, str(rt))
        from tara_chakra import get_nakshatra_full
        nak = get_nakshatra_full(janma_nak)
    except Exception:
        nak = None
    if nak:
        gana = GANA_TA.get(nak.get("gana", ""), nak.get("gana", ""))
        yoni_en = nak.get("yoni", "")
        yoni = YONI_TA.get(yoni_en, yoni_en)
        gender = YONI_GENDER_TA.get(yoni_en, "\u0b86\u0ba3\u0bcd")
        out["gana_yoni"] = f"{gana}-\u0bae\u0bbf\u0bb0\u0bc1\u0b95\u0bae\u0bcd {gender} {yoni}"
    tree, bird = NAK_TREE_BIRD_TA.get(janma_nak, ("", ""))
    if tree or bird:
        out["tree_bird"] = f"\u0bb5\u0bbf\u0bb0\u0bc1\u0b9f\u0bcd\u0b9a\u0bae\u0bcd-{tree} \u0baa\u0b9f\u0bcd\u0b9a\u0bbf-{bird}".strip()
    place = NAK_DEVATA_PLACE_TA.get(janma_nak, "")
    if place:
        out["deity_place"] = place
    return out


def birth_disha_iruppu(chart: dict, lang: str) -> str:
    """Running Vimshottari MD at birth + balance (Logic Vision page 4)."""
    from engine.report_chart_details import _planet_name

    moon_lon = _planet_lon(chart, "Moon")
    nak_idx = int(moon_lon // NAKSHATRA_SPAN)
    progress = (moon_lon - nak_idx * NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    try:
        import sys
        from pathlib import Path
        rt = Path(__file__).resolve().parents[1] / "runtime"
        if str(rt) not in sys.path:
            sys.path.insert(0, str(rt))
        from granular_dasha import NAK_LORDS_27, VIMSHOTTARI_YEARS
        lord = NAK_LORDS_27[nak_idx]
    except Exception:
        return ""
    remain_years = VIMSHOTTARI_YEARS[lord] * (1.0 - progress)
    total_days = int(round(remain_years * 365.25))
    years, rem = divmod(total_days, 365)
    months, days = divmod(rem, 30)
    lord_ta = _planet_name(lord, lang) if lang == "ta" else lord
    if lang == "ta":
        return (
            f"\u0ba4\u0bbf\u0b9a\u0bc8 \u0b87\u0bb0\u0bc1\u0baa\u0bcd\u0baa\u0bc1 : {lord_ta} \u0ba4\u0bbf\u0b9a\u0bc8 | "
            f"\u0bae\u0bc0\u0ba4\u0bae\u0bcd {years} \u0bb5\u0bb0\u0bc1\u0b9f\u0bae\u0bcd {months} \u0bae\u0bbe\u0ba4\u0bae\u0bcd {days} \u0ba8\u0bbe\u0bb3\u0bcd"
        )
    return f"Disha: {lord} dasha | balance {years}y {months}m {days}d"


def navamsa_rasi_for_lon(lon: float) -> str:
    from engine.chart_builder import RASIS
    return RASIS[int(lon / (10 / 3)) % 12]


def page2_panchanga_rows(chart: dict, lang: str) -> list[tuple[str, str]]:
    from engine.report_chart_details import _nak_name, _sign_name

    c = chart
    b = c.get("birth") or {}
    p = panchanga_at_birth(chart)
    moon_pada = c.get("moon_pada") or (c.get("positions") or {}).get("Moon", {}).get("pada", "")
    moon_lon = _planet_lon(c, "Moon")
    og = _nakshatra_og_extras(c.get("janma_nakshatra", ""), lang)
    rows: list[tuple[str, str]] = []
    if lang == "ta":
        rows.append((
            "\u0ba8\u0bc7\u0bb0 \u0bae\u0ba3\u0bcd\u0b9f\u0bb2\u0bae\u0bcd",
            f"\u0b87\u0ba8\u0bcd\u0ba4\u0bbf\u0baf\u0bbe (IST) \u2014 {_lon_dms_east(float(b.get('lon', 0)))} \u0b95\u0bbf\u0bb4\u0b95\u0bcd\u0b95\u0bc1",
        ))
        if p.get("sunrise"):
            rows.append(("\u0b9a\u0bc2\u0bb0\u0bbf\u0baf \u0b89\u0ba4\u0baf\u0bae\u0bcd", f"{p['sunrise']} \u0b95\u0bbe\u0bb2\u0bc8"))
        if p.get("sunset"):
            rows.append(("\u0b9a\u0bc2\u0bb0\u0bbf\u0baf \u0b85\u0bb8\u0bcd\u0ba4\u0bae\u0ba9\u0bae\u0bcd", f"{p['sunset']} \u0bae\u0bbe\u0bb2\u0bc8"))
        from engine.ayanamsa_picker import display_label_ta
        aya_label = display_label_ta(mode=c.get("ayanamsa_mode"), name=c.get("ayanamsa_name"))
        rows.append(("\u0b85\u0baf\u0ba9\u0bbe\u0bae\u0bcd\u0b9a\u0bae\u0bcd", f"{c.get('ayanamsa', '')} ({aya_label})"))
        rows.append(("\u0ba8\u0b9f\u0bcd\u0b9a\u0ba4\u0bcd\u0ba4\u0bbf\u0bb0 \u0b93\u0bb0\u0bc8", nakshatra_balance_hms(moon_lon)))
        rows.append(("\u0b87\u0ba9\u0bcd\u0bae \u0bb0\u0bbe\u0b9a\u0bbf", _sign_name(c.get("moon_rasi", ""), "ta")))
        rows.append(("\u0b9c\u0ba9\u0bcd\u0bae \u0bb2\u0b95\u0bcd\u0ba9\u0bae\u0bcd", _sign_name(c.get("lagna", ""), "ta")))
        jn = _nak_name(c.get("janma_nakshatra", ""), "ta")
        rows.append(("\u0b9c\u0ba9\u0bcd\u0bae \u0ba8\u0b9f\u0bcd\u0b9a\u0ba4\u0bcd\u0ba4\u0bbf\u0bb0\u0bae\u0bcd", f"{jn} ({moon_pada} \u0b86\u0bae\u0bcd \u0baa\u0bbe\u0ba4\u0bae\u0bcd)" if moon_pada else jn))
        rows.append(("\u0baf\u0bcb\u0b95\u0bae\u0bcd", _yoga_label_ta(p.get("yoga", ""))))
        rows.append(("\u0b95\u0bb0\u0ba3\u0bae\u0bcd", KARANA_TA.get(p.get("karana", ""), p.get("karana", ""))))
        tithi = TITHI_TA.get(p.get("tithi", ""), p.get("tithi", ""))
        pak = PAKSHA_TA.get(p.get("paksha", ""), p.get("paksha", ""))
        rows.append(("\u0ba4\u0bbf\u0ba4\u0bbf", f"{tithi} - {pak}"))
        rows.append(("\u0baa\u0b9f\u0bcd\u0b9a\u0bae\u0bcd", pak))
        rows.append((
            "\u0b89\u0ba4\u0bcd\u0ba4\u0bb0\u0bbe\u0baf\u0ba3\u0bae\u0bcd",
            "\u0b89\u0ba4\u0bcd\u0ba4\u0bb0\u0bbe\u0baf\u0ba3\u0bae\u0bcd" if is_uttarayana(c) else "\u0ba4\u0b95\u0bcd\u0bb7\u0bbf\u0ba3\u0bbe\u0baf\u0ba3\u0bae\u0bcd",
        ))
        rows.append(("\u0bb0\u0bbe\u0b9a\u0bbf \u0ba4\u0bbf\u0b95\u0bcd\u0b95\u0bc1", RASI_DIRECTION_TA.get(c.get("moon_rasi", ""), "-")))
        ch = chandrashtama_nakshatras(c, lang)
        if ch:
            rows.append(("\u0b9a\u0ba8\u0bcd\u0ba4\u0bbf\u0bb0\u0bbe\u0bb7\u0bcd\u0b9f\u0bae \u0ba8\u0b9f\u0bcd\u0b9a\u0ba4\u0bcd\u0ba4\u0bbf\u0bb0\u0b99\u0bcd\u0b95\u0bb3\u0bcd", ch))
        if og.get("deity_place"):
            rows.append(("\u0b85\u0ba4\u0bbf\u0ba4\u0bc7\u0bb5\u0ba4\u0bc8, \u0b87\u0b9f\u0bae\u0bcd", og["deity_place"]))
        if og.get("gana_yoni"):
            rows.append(("\u0b95\u0ba3\u0bae\u0bcd / \u0baf\u0bcb\u0ba9\u0bbf", og["gana_yoni"]))
        if og.get("tree_bird"):
            rows.append(("\u0bb5\u0bbf\u0bb0\u0bc1\u0b9f\u0bcd\u0b9a\u0bae\u0bcd / \u0baa\u0b9f\u0bcd\u0b9a\u0bbf", og["tree_bird"]))
    else:
        rows.append(("Timezone", f"India IST - {_lon_dms_east(float(b.get('lon', 0)))} E"))
        if p.get("sunrise"):
            rows.append(("Sunrise", p["sunrise"]))
        if p.get("sunset"):
            rows.append(("Sunset", p["sunset"]))
        from engine.ayanamsa_picker import display_label_ta
        aya_label = display_label_ta(mode=c.get("ayanamsa_mode"), name=c.get("ayanamsa_name"))
        rows.append(("Ayanamsa", f"{c.get('ayanamsa', '')} ({aya_label})"))
        rows.append(("Nakshatra balance", nakshatra_balance_hms(moon_lon)))
        rows.append(("Moon sign", c.get("moon_rasi", "")))
        rows.append(("Lagna", c.get("lagna", "")))
        rows.append(("Janma nakshatra", f"{c.get('janma_nakshatra', '')} pada {moon_pada}"))
        rows.append(("Yoga", p.get("yoga", "")))
        rows.append(("Karana", p.get("karana", "")))
        rows.append(("Tithi", f"{p.get('tithi', '')} ({p.get('paksha', '')})"))
        rows.append(("Paksha", p.get("paksha", "")))
        rows.append(("Ayana", "Uttarayana" if is_uttarayana(c) else "Dakshinayana"))
        rows.append(("Rasi direction", RASI_DIRECTION_TA.get(c.get("moon_rasi", ""), "")))
        ch = chandrashtama_nakshatras(c, lang)
        if ch:
            rows.append(("Chandrashtama nakshatras", ch))
        for k, label in (("deity_place", "Deity / place"), ("gana_yoni", "Gana / yoni"), ("tree_bird", "Tree / bird")):
            if og.get(k):
                rows.append((label, og[k]))
    return rows


def build_page13_tamil_numerology(chart: dict, lang: str) -> str:
    b = chart["birth"]
    rpt = tamil_numerology_compute(dt.date(b["year"], b["month"], b["day"]))
    if lang == "ta":
        days_ta = ", ".join(PLANET_DAY_TA.get(d, d) for d in rpt.lucky_days)
        dir_ta = DIRECTION_TA.get(rpt.lucky_direction, rpt.lucky_direction)
        return "\n".join([
            "## \u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd 13 - \u0bb5\u0bbf\u0ba4\u0bbf \u0b8e\u0ba3\u0bcd \u0bae\u0bb1\u0bcd\u0bb1\u0bc1\u0bae\u0bcd \u0b85\u0ba4\u0bbf\u0bb7\u0bcd\u0b9f \u0b85\u0bae\u0bcd\u0b9a\u0b99\u0bcd\u0b95\u0bb3\u0bcd",
            "",
            "| \u0bb5\u0bbf\u0bb5\u0bb0\u0bae\u0bcd | \u0bae\u0ba4\u0bbf\u0baa\u0bcd\u0baa\u0bc1 |",
            "|---|---|",
            f"| \u0bb5\u0bbf\u0ba4\u0bbf \u0b8e\u0ba3\u0bcd | **{rpt.vidhi_number}** |",
            f"| \u0bb5\u0bbf\u0ba4\u0bbf\u0b95\u0bcd\u0b95\u0bc1\u0bb0\u0bbf\u0baf \u0b95\u0bbf\u0bb0\u0b95\u0bae\u0bcd | {rpt.vidhi_planet} |",
            f"| \u0b85\u0ba4\u0bbf\u0bb7\u0bcd\u0b9f \u0b95\u0bbf\u0bb4\u0bae\u0bc8\u0b95\u0bb3\u0bcd | {days_ta} |",
            f"| \u0b85\u0ba4\u0bbf\u0bb7\u0bcd\u0b9f \u0ba4\u0bbf\u0b95\u0bcd\u0b95\u0bc1 | {dir_ta} |",
            f"| \u0b85\u0ba4\u0bbf\u0bb7\u0bcd\u0b9f \u0ba4\u0bc7\u0ba4\u0bbf\u0b95\u0bb3\u0bcd | {', '.join(str(x) for x in rpt.lucky_dates)} |",
            f"| \u0b85\u0ba4\u0bbf\u0bb7\u0bcd\u0b9f \u0bb0\u0ba4\u0bcd\u0ba4\u0bbf\u0ba9\u0bae\u0bcd | {rpt.lucky_gemstone} |",
            f"| \u0ba8\u0b9f\u0bcd\u0baa\u0bc1 \u0b8e\u0ba3\u0bcd\u0b95\u0bb3\u0bcd | {', '.join(str(x) for x in rpt.friendly_numbers)} |",
            f"| \u0baa\u0b95\u0bc8 \u0b8e\u0ba3\u0bcd\u0b95\u0bb3\u0bcd | {', '.join(str(x) for x in rpt.hostile_numbers)} |",
            f"| \u0b9a\u0bae \u0b8e\u0ba3\u0bcd\u0b95\u0bb3\u0bcd | {', '.join(str(x) for x in rpt.neutral_numbers)} |",
            f"| \u0b85\u0ba4\u0bbf\u0bb7\u0bcd\u0b9f \u0ba8\u0bbf\u0bb1\u0bae\u0bcd | {rpt.lucky_color} |",
            f"| \u0ba4\u0bc7\u0bb5\u0ba4\u0bc8 | {rpt.deity} |",
            f"| \u0b85\u0ba4\u0bbf\u0ba4\u0bc7\u0bb5\u0ba4\u0bc8 | {rpt.higher_deity} |",
            "",
        ])
    return tamil_numerology_md(rpt)


def format_table_rows(rows: list[tuple[str, str]]) -> str:
    return "\n".join(f"| {k} | {v} |" for k, v in rows)
