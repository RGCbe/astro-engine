"""Section 0 for every client report: full person + chart details before timing."""
from __future__ import annotations

import datetime as dt
from typing import Any

from engine.chart_profile import build_chart_profile

RASIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}
HOUSE_THEMES_EN = {
    1: "self, body, identity", 2: "wealth, speech, family", 3: "siblings, courage, skills",
    4: "home, mother, peace", 5: "children, creativity, romance", 6: "health, service, enemies",
    7: "marriage, partner, contracts", 8: "longevity, inheritance, stress",
    9: "dharma, father, fortune", 10: "career, status, authority",
    11: "gains, networks, hopes", 12: "loss, abroad, moksha",
}
PLANET_ORDER = (
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
    "Rahu", "Ketu", "Mandi", "Gulika",
)

LABELS = {
    "en": {
        "title": "Person and full birth chart",
        "birth_record": "Birth record",
        "chart_identity": "Chart identity",
        "planets": "Planetary positions (sidereal)",
        "houses": "Twelve houses from lagna",
        "functional": "Functional lords (this lagna)",
        "synthesis": "Chart synthesis (read this first)",
        "current_dasha": "Current Vimshottari dasha",
        "name": "Name",
        "date": "Date",
        "time": "Time",
        "place": "Place",
        "coordinates": "Coordinates",
        "weekday": "Weekday",
        "timezone": "Timezone used",
        "ayanamsa": "Ayanamsa",
        "lagna": "Lagna (ascendant)",
        "lagna_deg": "Lagna degree",
        "lagna_lord": "Lagna lord",
        "moon_rasi": "Moon sign (Janma rasi)",
        "janma_nak": "Janma nakshatra",
        "nak_lord": "Nakshatra lord (starting dasha theme)",
        "sun_rasi": "Sun sign",
        "col_planet": "Planet",
        "col_sign": "Sign",
        "col_house": "House",
        "col_deg": "Deg",
        "col_nak": "Nakshatra",
        "col_pada": "Pada",
        "col_nak_lord": "Nak lord",
        "col_house_n": "House",
        "col_sign_h": "Sign on cusp",
        "col_lord": "Lord",
        "col_occupants": "Planets here",
        "col_theme": "Life theme",
        "lord_h": "rules H",
        "no_planets": "(empty)",
        "before_timing": (
            "All prediction sections below refer to **this** chart only. "
            "Verify birth time with the native before treating sub-day windows as final."
        ),
    },
    "ta": {
        "title": "???? ??????? ???? ??????? ???????",
        "birth_record": "??????? ?????",
        "chart_identity": "????? ????????",
        "planets": "???? ??????? (???????)",
        "houses": "???????????????? 12 ???????",
        "functional": "??????????? ????????? (??? ??????)",
        "synthesis": "????? ???????? (??????? ??? ??????????)",
        "current_dasha": "???????? ???????????? ???",
        "name": "?????",
        "date": "????",
        "time": "?????",
        "place": "????",
        "coordinates": "???????????",
        "weekday": "??? ????",
        "timezone": "??? ???????",
        "ayanamsa": "?????????",
        "lagna": "?????? (?????)",
        "lagna_deg": "???? ????",
        "lagna_lord": "???? ??????",
        "moon_rasi": "?????? ???? (???? ????)",
        "janma_nak": "???? ???????????",
        "nak_lord": "????????? ??????",
        "sun_rasi": "????? ????",
        "col_planet": "??????",
        "col_sign": "????",
        "col_house": "????",
        "col_deg": "????",
        "col_nak": "???????????",
        "col_pada": "?????",
        "col_nak_lord": "?.?.",
        "col_house_n": "????",
        "col_sign_h": "?????? ????",
        "col_lord": "??????",
        "col_occupants": "????????? ?????????",
        "col_theme": "???????? ????",
        "lord_h": "????.??",
        "no_planets": "(????)",
        "before_timing": (
            "????????? ??????? ??????????? ???? ??????????? ????????????????. "
            "??? ??????? ??????? ????????????????? ?????????."
        ),
    },
}


def _t(lang: str, key: str) -> str:
    return LABELS.get(lang, LABELS["en"]).get(key, key)


def _planet_name(p: str, lang: str) -> str:
    if lang != "ta":
        return p
    try:
        from runtime.tamil_translations import PLANETS_TA
        return PLANETS_TA.get(p, p)
    except ImportError:
        return p


def _sign_name(s: str, lang: str) -> str:
    if lang != "ta":
        return s
    try:
        from runtime.tamil_translations import RASIS_TA
        return RASIS_TA.get(s, s)
    except ImportError:
        return s


def _nak_name(n: str, lang: str) -> str:
    if not n or lang != "ta":
        return n or ""
    try:
        from runtime.tamil_translations import NAKSHATRAS_TA
        return NAKSHATRAS_TA.get(n, n)
    except ImportError:
        return n


def normalize_chart(chart: Any) -> dict[str, Any]:
    """Accept manoj-style dict or runtime Chart-like object."""
    if isinstance(chart, dict) and chart.get("birth"):
        return chart
    birth_dt = getattr(chart, "birth_dt", None)
    if birth_dt is None:
        raise TypeError("chart must be dict with birth= or object with birth_dt")
    b = {
        "year": birth_dt.year,
        "month": birth_dt.month,
        "day": birth_dt.day,
        "hour": birth_dt.hour,
        "min": birth_dt.minute,
        "lat": getattr(chart, "lat", 0),
        "lon": getattr(chart, "lon", 0),
        "place": getattr(chart, "place", "") or "",
        "weekday": birth_dt.strftime("%A"),
    }
    lagna_idx = int(getattr(chart, "lagna_lon", 0) // 30) % 12
    lagna = RASIS[lagna_idx]
    positions: dict[str, Any] = {}
    lagna_lon = float(getattr(chart, "lagna_lon", 0))
    nakshatras = getattr(chart, "nakshatras", {}) or {}
    for p in PLANET_ORDER:
        lon = (getattr(chart, "positions", None) or {}).get(p)
        if lon is None:
            continue
        ri = int(lon // 30) % 12
        nk = nakshatras.get(p, {})
        positions[p] = {
            "rasi": RASIS[ri],
            "rasi_idx": ri,
            "house": ((ri - lagna_idx) % 12) + 1,
            "deg": round(lon - ri * 30, 4),
            "lon_abs": lon,
            "nak": nk.get("name", ""),
            "nak_lord": nk.get("lord", ""),
            "pada": nk.get("pada", ""),
        }
    return {
        "name": getattr(chart, "name", "Native"),
        "birth": b,
        "lagna": lagna,
        "lagna_idx": lagna_idx,
        "lagna_lon": lagna_lon,
        "lagna_deg": round(lagna_lon - lagna_idx * 30, 4),
        "lagna_lord": getattr(chart, "lagna_lord", SIGN_LORD.get(lagna, "")),
        "janma_nakshatra": getattr(chart, "janma_nakshatra", None)
        or nakshatras.get("Moon", {}).get("name", ""),
        "janma_nakshatra_lord": getattr(chart, "janma_nakshatra_lord", None)
        or nakshatras.get("Moon", {}).get("lord", ""),
        "moon_rasi": positions.get("Moon", {}).get("rasi", ""),
        "positions": positions,
        "ayanamsa": getattr(chart, "ayanamsa", None),
    }


def _current_dasha_rows(chart: dict[str, Any], when: dt.datetime | None, lang: str) -> list[dict[str, str]]:
    when = when or dt.datetime.now()
    try:
        import sys
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        rt = root / "runtime"
        if str(rt) not in sys.path:
            sys.path.insert(0, str(rt))
        from granular_dasha import build_full_timeline, lookup

        active = lookup(build_full_timeline(chart, levels=4), when)
        if not active:
            return []
        level_en = {1: "MD", 2: "AD", 3: "PD", 4: "SD"}
        rows = []
        for lvl in sorted(active):
            rec = active[lvl]
            parts = [rec[k] for k in ("md", "ad", "pd", "sd") if k in rec]
            end = rec.get("end")
            end_s = end.strftime("%Y-%m-%d") if end else "-"
            if lang == "ta":
                from tamil_translations import PLANETS_TA, DASHA_LEVEL_TA, DASHA_EFFECT_TA, MD_THEME_TA
                lords = "-".join(PLANETS_TA.get(x, x) for x in parts)
                effect_lord = rec.get("sd") or rec.get("pd") or rec.get("ad") or rec.get("md")
                effect = DASHA_EFFECT_TA.get(effect_lord, MD_THEME_TA.get(effect_lord, ""))
                rows.append({
                    "level": DASHA_LEVEL_TA.get(lvl, str(lvl)),
                    "lords": lords,
                    "until": end.strftime("%d-%m-%Y") if end else "-",
                    "effect": effect,
                })
            else:
                rows.append({
                    "level": level_en.get(lvl, str(lvl)),
                    "lords": "-".join(parts),
                    "until": end_s,
                    "effect": f"Active {parts[-1]} period themes",
                })
        return rows
    except Exception:
        return []


def build_chart_details_markdown(
    chart: Any,
    lang: str = "en",
    *,
    when: dt.datetime | None = None,
    include_synthesis: bool = True,
    include_current_dasha: bool = True,
) -> str:
    """Markdown section 0: must be first in every client report."""
    c = normalize_chart(chart)
    L = lambda k: _t(lang, k)
    b = c["birth"]
    lines: list[str] = []

    lines.append(f"## {L('title')}")
    lines.append("")
    lines.append(f"> {L('before_timing')}")
    lines.append("")

    lines.append(f"### {L('birth_record')}")
    lines.append("")
    lines.append(f"| Field | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| {L('name')} | **{c.get('name', 'Native')}** |")
    lines.append(
        f"| {L('date')} | {b['year']}-{b['month']:02d}-{b['day']:02d} |"
    )
    lines.append(
        f"| {L('time')} | {b.get('hour', 0):02d}:{b.get('min', 0):02d} (local civil) |"
    )
    lines.append(f"| {L('place')} | {b.get('place', '')} |")
    lines.append(
        f"| {L('coordinates')} | {b.get('lat', 0):.4f}N, {b.get('lon', 0):.4f}E |"
    )
    if b.get("weekday"):
        lines.append(f"| {L('weekday')} | {b.get('weekday')} |")
    lines.append(f"| {L('timezone')} | IST (+5:30) unless corrected |")
    if c.get("ayanamsa") is not None:
        aya_note = c.get("ayanamsa_name") or "Lahiri"
        lines.append(f"| {L('ayanamsa')} | {c.get('ayanamsa')} ({aya_note}) |")
    lines.append("")

    lagna = c.get("lagna", "")
    profile = build_chart_profile(c)
    lines.append(f"### {L('chart_identity')}")
    lines.append("")
    lines.append(f"- **{L('lagna')}:** {_sign_name(lagna, lang)} ({lagna})")
    lines.append(f"- **{L('lagna_deg')}:** {c.get('lagna_deg', '')} (sidereal)")
    lines.append(
        f"- **{L('lagna_lord')}:** {_planet_name(profile['lagna_lord'], lang)} "
        f"in house {profile.get('lagna_lord_house', '?')}"
    )
    moon_r = c.get("moon_rasi") or profile.get("moon_rasi", "")
    lines.append(
        f"- **{L('moon_rasi')}:** {_sign_name(moon_r, lang)} "
        f"(house {profile.get('moon_house', '?')})"
    )
    sun_r = (c.get("positions") or {}).get("Sun", {}).get("rasi", "")
    if sun_r:
        lines.append(f"- **{L('sun_rasi')}:** {_sign_name(sun_r, lang)}")
    jn = c.get("janma_nakshatra", "")
    if jn:
        lines.append(f"- **{L('janma_nak')}:** {_nak_name(jn, lang)} ({jn})")
    jnl = c.get("janma_nakshatra_lord", "")
    if jnl:
        lines.append(f"- **{L('nak_lord')}:** {_planet_name(jnl, lang)}")
    lines.append("")

    lines.append(f"### {L('planets')}")
    lines.append("")
    lines.append(
        f"| {L('col_planet')} | {L('col_sign')} | {L('col_house')} | {L('col_deg')} | "
        f"{L('col_nak')} | {L('col_pada')} | {L('col_nak_lord')} |"
    )
    lines.append("|---|---:|---:|---:|---|---:|---|")
    for p in PLANET_ORDER:
        pd = (c.get("positions") or {}).get(p)
        if not pd:
            continue
        rasi = pd.get("rasi", "")
        lines.append(
            f"| {_planet_name(p, lang)} | {_sign_name(rasi, lang)} | {pd.get('house', '')} | "
            f"{pd.get('deg', '')} | {_nak_name(pd.get('nak', ''), lang)} | "
            f"{pd.get('pada', '')} | {_planet_name(pd.get('nak_lord', ''), lang)} |"
        )
    lines.append("")

    lords = profile["house_lords"]
    by_house: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for p in PLANET_ORDER:
        pd = (c.get("positions") or {}).get(p)
        if pd and pd.get("house"):
            by_house[int(pd["house"])].append(_planet_name(p, lang))

    lines.append(f"### {L('houses')}")
    lines.append("")
    lines.append(
        f"| {L('col_house_n')} | {L('col_sign_h')} | {L('col_lord')} | "
        f"{L('col_occupants')} | {L('col_theme')} |"
    )
    lines.append("|---:|---|---|---|---|")
    lagna_idx = int(c.get("lagna_idx", 0))
    for h in range(1, 13):
        sign = RASIS[(lagna_idx + h - 1) % 12]
        occ = ", ".join(by_house[h]) if by_house[h] else L("no_planets")
        lord = _planet_name(lords[h], lang)
        theme = HOUSE_THEMES_EN[h]
        lines.append(
            f"| {h} | {_sign_name(sign, lang)} | {lord} | {occ} | {theme} |"
        )
    lines.append("")

    lines.append(f"### {L('functional')}")
    lines.append("")
    for h in (1, 2, 4, 5, 7, 9, 10, 11):
        lord = lords[h]
        ph = (c.get("positions") or {}).get(lord, {}).get("house", "?")
        lines.append(
            f"- **H{h} lord** {_planet_name(lord, lang)} -> house {ph} "
            f"({L('lord_h')}{h})"
        )
    lines.append("")

    if include_synthesis:
        lines.append(f"### {L('synthesis')}")
        lines.append("")
        lines.append(profile["executive_summary_en"])
        lines.append("")
        for pl in profile.get("key_placements", [])[:12]:
            lines.append(f"- {pl}")
        lines.append("")

    if include_current_dasha:
        rows = _current_dasha_rows(c, when, lang)
        if rows:
            lines.append(f"### {L('current_dasha')}")
            lines.append("")
            lines.append(f"*As of {(when or dt.datetime.now()).date().isoformat()}*")
            lines.append("")
            lines.append("| Level | Dasha | Until | Effect |")
            lines.append("|---|---|---|---|")
            for r in rows:
                lines.append(
                    f"| {r['level']} | {r['lords']} | {r['until']} | {r['effect']} |"
                )
            lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)
