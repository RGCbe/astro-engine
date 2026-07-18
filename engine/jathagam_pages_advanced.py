# -*- coding: utf-8 -*-
"""Part 1 pages 6-12: bhava cusps, shadbala, ashtakavarga, Vimshottari tables."""
from __future__ import annotations

import datetime as dt
from typing import Any

from engine.report_chart_details import _planet_name, _sign_name, normalize_chart

# Tamil bhava names (Logic Vision style)
BHAVA_TA = [
    "\u0bb2\u0b95\u0bcd\u0ba9 \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0ba4\u0ba9 \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0b9a\u0b95\u0bcb\u0ba4\u0bb0 \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0bae\u0bbe\u0ba4\u0bb0\u0bcd \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0baa\u0bc2\u0ba4\u0bcd\u0bb0 \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0b9a\u0ba4\u0bcd\u0bb0\u0bc1 \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0b95\u0bb3\u0ba4\u0bcd\u0ba4\u0bbf\u0bb0 \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0b86\u0baf\u0bc1\u0bb3\u0bcd \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0baa\u0bbf\u0ba4\u0bc1\u0bb0\u0bcd \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0b9c\u0bc0\u0bb5\u0ba9 \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0b87\u0bb2\u0bbe\u0baa \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
    "\u0bb5\u0bbf\u0bb0\u0baf \u0baa\u0bbe\u0bb5\u0bae\u0bcd",
]

RASIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

PLANETS_SB = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")


def _lagna_lon(chart: dict) -> float:
    if chart.get("lagna_lon") is not None:
        return float(chart["lagna_lon"]) % 360
    idx = int(chart.get("lagna_idx", 0))
    deg = float(chart.get("lagna_deg", 0))
    return (idx * 30 + deg) % 360


def _dms_in_sign(lon: float) -> tuple[int, int, int, str]:
    lon = lon % 360
    sign = RASIS[int(lon / 30)]
    in_sign = lon % 30
    d = int(in_sign)
    m = int((in_sign - d) * 60)
    s = int(round(((in_sign - d) * 60 - m) * 60))
    if s >= 60:
        s, m = 0, m + 1
    if m >= 60:
        m, d = 0, d + 1
    return d, m, s, sign


def _fmt_dms(d: int, m: int, s: int) -> str:
    return f"{d} {m:02d} {s:02d}"


def _birth_dt(chart: dict) -> dt.datetime:
    b = chart["birth"]
    return dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))


def _age_at(birth: dt.datetime, when: dt.datetime) -> str:
    days = (when - birth).days
    if days < 0:
        return "0"
    y = int(days // 365.25)
    rem = days - y * 365.25
    m = int(rem // 30.44)
    d = int(rem % 30.44)
    return f"{y}" if m == 0 and d == 0 else f"{y}.{m:02d}"


def build_page6_bhava_cusps(chart: dict[str, Any], lang: str, title: str) -> str:
    c = normalize_chart(chart)
    lagna_lon = _lagna_lon(c)
    lines = [f"## {title}", ""]
    if lang == "ta":
        lines.append(
            "\u0baa\u0bbe\u0bb5 \u0bb8\u0bcd\u0baa\u0bc1\u0b9f\u0b99\u0bcd\u0b95\u0bb3\u0bcd "
            "(\u0b87\u0bb0\u0bbe\u0baf\u0ba3 \u0bae\u0bc1\u0bb1\u0bc8, \u0b9a\u0bae \u0baa\u0bbe\u0b95\u0bae\u0bcd "
            "\u2014 \u0ba4\u0bca\u0b9f\u0b95\u0bcd\u0b95\u0bae\u0bcd / \u0b87\u0bb3\u0bc8\u0bb5\u0bc1 / \u0bae\u0bc1\u0b9f\u0bbf\u0bb5\u0bc1)"
        )
        hdr = (
            "| \u0baa\u0bbe\u0bb5\u0bae\u0bcd | \u0bb0\u0bbe\u0b9a\u0bbf | "
            "\u0ba4\u0bca\u0b9f\u0b95\u0bcd\u0b95\u0bae\u0bcd | \u0b87\u0bb3\u0bc8\u0bb5\u0bc1 | \u0bae\u0bc1\u0b9f\u0bbf\u0bb5\u0bc1 |"
        )
    else:
        lines.append("Bhava cusps (equal 30 deg from sidereal lagna; start / middle / end in sign DMS)")
        hdr = "| House | Sign | Start | Middle | End |"
    lines.append(hdr)
    lines.append("|---:|---|---|---|---|")
    for h in range(1, 13):
        start_lon = (lagna_lon + (h - 1) * 30) % 360
        mid_lon = (start_lon + 15) % 360
        end_lon = (start_lon + 30) % 360
        ds, ms, ss, sign = _dms_in_sign(start_lon)
        dm, mm, sm, _ = _dms_in_sign(mid_lon)
        de, me, se, _ = _dms_in_sign(end_lon)
        name = BHAVA_TA[h - 1] if lang == "ta" else f"House {h}"
        sign_l = _sign_name(sign, lang)
        lines.append(
            f"| {name} | {sign_l} | {_fmt_dms(ds, ms, ss)} | {_fmt_dms(dm, mm, sm)} | {_fmt_dms(de, me, se)} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_page7_shadbala_table(chart: dict[str, Any], lang: str, title: str) -> str:
    from engine.shadbala import compute_shadbala

    c = normalize_chart(chart)
    lines = [f"## {title}", ""]
    try:
        sb = compute_shadbala(c)
    except Exception as exc:
        return f"## {title}\n\n(Shadbala unavailable: {exc})\n"
    lines.append("Shadbala (Virupas; total_rupas = total/60)")
    hdr = "| Planet | Sthana | Dig | Kala | Cheshta | Naisargika | Drik | Total Rupa | Status |"
    if lang == "ta":
        strong_ta = "\u0baa\u0bb2\u0bae\u0bcd"
        weak_ta = "\u0baa\u0bb2\u0bae\u0bbf\u0ba9\u0bae\u0bcd"
    else:
        strong_ta, weak_ta = "Strong", "Weak"
    lines.append(hdr)
    lines.append("|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for p in PLANETS_SB:
        if p not in sb:
            continue
        b = sb[p]
        st = strong_ta if b["is_strong"] else weak_ta
        pname = _planet_name(p, lang)
        lines.append(
            f"| {pname} | {b['sthana']:.0f} | {b['dig']:.0f} | {b['kala']:.0f} | "
            f"{b['cheshta']:.0f} | {b['naisargika']:.0f} | {b['drik']:.0f} | "
            f"{b['total_rupas']:.2f} | {st} |"
        )
    lines.append("")
    return "\n".join(lines)


def build_page8_sav_table(chart: dict[str, Any], lang: str, title: str) -> str:
    from engine.ashtakavarga import (
        compute_bhinna_ashtakavarga,
        compute_sarvashtakavarga,
        interpret_house_bindus,
    )

    c = normalize_chart(chart)
    lines = [f"## {title}", ""]
    try:
        bhinna = compute_bhinna_ashtakavarga(c)
        sarva = compute_sarvashtakavarga(bhinna)
    except Exception as exc:
        return f"## {title}\n\n(Ashtakavarga unavailable: {exc})\n"
    if lang == "ta":
        lines.append("\u0b85\u0bb7\u0bcd\u0b9f\u0b95\u0bb5\u0bb0\u0bcd\u0b95\u0bae\u0bcd (\u0b95\u0bc2\u0b9f\u0bcd\u0b9f\u0bc1 \u0baa\u0bbe\u0b95\u0bae\u0bcd 337)")
    else:
        lines.append("Sarvashtakavarga (classical grand total target 337)")
    hdr = "| Planet |" + "".join(f" H{h} |" for h in range(1, 13)) + " Sum |"
    lines.append(hdr)
    lines.append("|---|" + "---:|" * 12 + "---:|")
    for p in PLANETS_SB:
        if p not in bhinna:
            continue
        av = bhinna[p]
        row = f"| {_planet_name(p, lang)} |"
        for h in range(1, 13):
            row += f" {av.get(f'house_{h}', 0)} |"
        row += f" {av.get('total', 0)} |"
        lines.append(row)
    lines.append("")
    lines.append("**Sarvashtakavarga (combined)**")
    sh = "| House | Bindus | Verdict |"
    lines.append(sh)
    lines.append("|---:|---:|---|")
    for h in range(1, 13):
        b = sarva[f"house_{h}"]
        verdict = interpret_house_bindus(h, b)
        if lang == "ta":
            lines.append(f"| {h} | {b} | {verdict} |")
        else:
            lines.append(f"| {h} | {b} | {verdict} |")
    gt = sarva["grand_total"]
    lines.append("")
    lines.append(f"**Grand total:** {gt} (BPHS reference 337)")
    lines.append("")
    return "\n".join(lines)


def _dasha_timeline(chart: dict) -> list[dict]:
    import sys
    from pathlib import Path

    rt = Path(__file__).resolve().parents[1] / "runtime"
    if str(rt) not in sys.path:
        sys.path.insert(0, str(rt))
    from granular_dasha import build_full_timeline

    return build_full_timeline(normalize_chart(chart), levels=2)


def _fmt_period(start: dt.datetime, end: dt.datetime, lang: str) -> str:
    if lang == "ta":
        return f"{start.strftime('%d-%m-%Y')} \u2014 {end.strftime('%d-%m-%Y')}"
    return f"{start.date()} to {end.date()}"


def _fmt_ymd_delta(start: dt.datetime, end: dt.datetime) -> str:
    days = (end - start).days
    y, rem = divmod(days, 365)
    m, d = divmod(rem, 30)
    return f"{y} \u0bb5\u0bb0\u0bc1\u0b9f\u0bae\u0bcd {m} \u0bae\u0bbe\u0ba4\u0bae\u0bcd {d} \u0ba8\u0bbe\u0bb3\u0bcd"


def build_page9_maha_dasha(chart: dict[str, Any], lang: str, title: str) -> str:
    c = normalize_chart(chart)
    birth = _birth_dt(c)
    lines = [f"## {title}", ""]
    if lang == "ta":
        lines.append("\u0bb5\u0bbf\u0bae\u0bcd\u0b9a\u0bcb\u0ba4\u0bcd\u0ba4\u0bbe\u0bb0\u0bbf \u0bae\u0b95\u0bbe \u0ba4\u0bbf\u0b9a\u0bc8 (\u0bae\u0b9a\u0bbe \u0ba4\u0bbf\u0b9a\u0bc8)")
        hdr = (
            "| \u0ba4\u0bbf\u0b9a\u0bc8 \u0b85\u0ba4\u0bbf\u0baa\u0ba4\u0bbf | \u0b86\u0bb0\u0bae\u0bcd\u0baa\u0bae\u0bcd | "
            "\u0bae\u0bc1\u0b9f\u0bbf\u0bb5\u0bc1 | \u0bb5\u0baf\u0ba4\u0bc1 \u0b86\u0bb0\u0bae\u0bcd\u0baa\u0bae\u0bcd | \u0b95\u0bbe\u0bb2\u0bae\u0bcd |"
        )
    else:
        lines.append("Vimshottari Mahadasha")
        hdr = "| MD Lord | Start | End | Age at start | Duration |"
    lines.append(hdr)
    lines.append("|---|---|---|---|---|")
    try:
        tl = _dasha_timeline(c)
    except Exception as exc:
        lines.append(f"| - | - | - | - | ({exc}) |")
        lines.append("")
        return "\n".join(lines)
    for r in tl:
        if r.get("level") != 1:
            continue
        lord = _planet_name(r["md"], lang)
        dur = _fmt_ymd_delta(r["start"], r["end"]) if lang == "ta" else f"{r['years']:.2f} y"
        age = _age_at(birth, r["start"])
        lines.append(
            f"| {lord} | {r['start'].strftime('%d-%m-%Y')} | {r['end'].strftime('%d-%m-%Y')} | "
            f"{age} | {dur} |"
        )
    lines.append("")
    return "\n".join(lines)


def _ad_table_for_md(chart: dict, md_lord: str, lang: str, birth: dt.datetime) -> list[str]:
    lines = []
    if lang == "ta":
        lines.append(
            f"### {_planet_name(md_lord, lang)} \u0bae\u0b95\u0bbe \u0ba4\u0bbf\u0b9a\u0bc8 \u2014 \u0b85\u0ba4\u0bbf\u0ba4\u0bbe\u0bb0 \u0ba4\u0bbf\u0b9a\u0bc8"
        )
        hdr = (
            "| \u0b85\u0ba4\u0bbf\u0ba4\u0bbe\u0bb0\u0bbf | \u0b86\u0bb0\u0bae\u0bcd\u0baa\u0bae\u0bcd | \u0bae\u0bc1\u0b9f\u0bbf\u0bb5\u0bc1 | "
            "\u0bb5\u0baf\u0ba4\u0bc1 | \u0b95\u0bbe\u0bb2\u0bae\u0bcd |"
        )
    else:
        lines.append(f"### Antardashas under {md_lord}")
        hdr = "| AD Lord | Start | End | Age at start | Duration |"
    lines.append(hdr)
    lines.append("|---|---|---|---|---|")
    tl = _dasha_timeline(chart)
    for r in tl:
        if r.get("level") != 2 or r.get("md") != md_lord:
            continue
        lord = _planet_name(r["ad"], lang)
        dur = _fmt_ymd_delta(r["start"], r["end"]) if lang == "ta" else f"{r['years']:.2f} y"
        age = _age_at(birth, r["start"])
        lines.append(
            f"| {lord} | {r['start'].strftime('%d-%m-%Y')} | {r['end'].strftime('%d-%m-%Y')} | "
            f"{age} | {dur} |"
        )
    lines.append("")
    return lines


def build_pages_10_12_antardasha(chart: dict[str, Any], lang: str, titles: tuple[str, str, str]) -> tuple[str, str, str]:
    c = normalize_chart(chart)
    birth = _birth_dt(c)
    try:
        tl = _dasha_timeline(c)
        md_lords = [r["md"] for r in tl if r.get("level") == 1]
    except Exception as exc:
        msg = f"(Dasha unavailable: {exc})\n"
        return (
            f"## {titles[0]}\n\n{msg}",
            f"## {titles[1]}\n\n{msg}",
            f"## {titles[2]}\n\n{msg}",
        )
    # Split MD blocks across 3 pages (4 MDs each typical)
    chunk = max(1, (len(md_lords) + 2) // 3)
    parts: list[list[str]] = [[], [], []]
    for i, md in enumerate(md_lords):
        parts[min(i // chunk, 2)].extend(_ad_table_for_md(c, md, lang, birth))
    out = []
    for title, body in zip(titles, parts):
        lines = [f"## {title}", ""]
        if lang == "ta":
            lines.append("\u0bb5\u0bbf\u0bae\u0bcd\u0b9a\u0bcb\u0ba4\u0bcd\u0ba4\u0bbe\u0bb0\u0bbf \u0b85\u0ba4\u0bbf\u0ba4\u0bbe\u0bb0 \u0ba4\u0bbf\u0b9a\u0bc8")
        else:
            lines.append("Vimshottari Antardasha tables")
        lines.append("")
        if body:
            lines.extend(body)
        else:
            lines.append("(No periods in this slice)")
            lines.append("")
        out.append("\n".join(lines))
    return tuple(out)
