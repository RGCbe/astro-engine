#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate MANOJ_TIMELINE.md from event_predictor_v2 + existing predictions data."""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_SCRATCH = Path(__file__).resolve().parent
ROOT = _SCRATCH.parent
RUNTIME = ROOT / "runtime"
REPORTS = ROOT / "reports"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(_SCRATCH))
sys.path.insert(0, str(RUNTIME))

from _report_out_dir import category_report_dir
from engine.event_age_policy import filter_bands_for_age
from _manoj_tamil_predictions_report import (
    TAMIL_MONTHS,
    CAT_TA,
    fmt_win,
    top_bands,
    filter_bands,
    row_dict,
)
from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from granular_dasha import build_full_timeline, lookup
from tamil_translations import RULE_ENGINE_DISCLAIMER_TA, ta_dasha_chain, ta_event

CHART_PATH = ROOT / "charts" / "manoj_chart.json"
TODAY = dt.datetime(2026, 6, 2)
OUT_DIR = category_report_dir("manoj", base=REPORTS, when=TODAY.date())
OUT_MD = OUT_DIR / "MANOJ_TIMELINE.md"
OUT_EN = OUT_DIR / "MANOJ_TIMELINE_EN.md"

DOMAIN_MAP = {
    "childhood": {"birth_mark", "d60_event", "kala_sarpa", "mouth_lip", "nadi", "nadi_pair", "sibling_health"},
    "education": {"education", "learning"},
    "career": {"career", "promotion", "career_breakthrough", "leadership_emergence"},
    "marriage": {"marriage", "engagement", "relationship_phase", "relationship_break", "saham_kalatra"},
    "health": {"health", "health_self", "self_accident", "saham_roga"},
    "wealth": {"wealth", "wealth_peak", "inheritance", "property", "lakshmi_yoga", "speculation_gain"},
    "father": {"father"},
    "travel": {"travel", "foreign"},
    "children": {"children", "progeny"},
    "music": {"music", "creativity"},
}

DOMAIN_LABEL_EN = {
    "childhood": "Childhood",
    "education": "Education",
    "career": "Career",
    "marriage": "Marriage / Relationship",
    "health": "Health",
    "wealth": "Wealth",
    "father": "Father",
    "travel": "Travel / Foreign",
    "children": "Children",
    "music": "Music / Creativity",
}


def domain_of(cat: str) -> str:
    for dom, cats in DOMAIN_MAP.items():
        if cat in cats:
            return dom
    return cat.replace("_", " ")


def strength_stars(sev: int, stars: str = "") -> str:
    if stars:
        return stars.strip()
    if sev >= 5:
        return "***"
    if sev >= 4:
        return "**"
    if sev >= 3:
        return "*"
    return "-"


def filter_past(bands, cutoff: dt.date):
    out = []
    for b in bands:
        ws = b.get("window_start")
        if not ws:
            continue
        if ws.date() > cutoff:
            continue
        out.append(b)
    return out


def row_bilingual(b):
    cat = b.get("category", "")
    ws, we = b.get("window_start"), b.get("window_end")
    sev = b.get("max_sev", b.get("severity", 0))
    dom = domain_of(cat)
    r_ta = row_dict(b, "ta")
    r_en = row_dict(b, "en")
    return {
        "range_en": fmt_win(ws, we, "en"),
        "range_ta": fmt_win(ws, we, "ta"),
        "domain_en": DOMAIN_LABEL_EN.get(dom, dom.title()),
        "domain_ta": CAT_TA.get(cat, r_ta["category"]),
        "what_en": r_en["plain"],
        "what_ta": r_ta["plain"],
        "strength": strength_stars(sev, b.get("stars", "")),
    }


def collect():
    chart = json.loads(CHART_PATH.read_text(encoding="utf-8"))
    tl = build_full_timeline(chart, levels=4)
    active = lookup(tl, TODAY)
    dasha_rows = ta_dasha_chain(active)

    raw_past = scan_lifetime_v2(chart, 1996, 2026, sample_days=14, min_severity=3)
    bands_past = filter_bands_for_age(chart, rank_and_consume(collapse_consecutive(raw_past)))
    past_bands = filter_past(bands_past, TODAY.date())

    raw_5y = scan_lifetime_v2(chart, TODAY.year, TODAY.year + 5, sample_days=14, min_severity=2)
    bands_5y = filter_bands_for_age(chart, rank_and_consume(collapse_consecutive(raw_5y)))

    raw_decade = scan_lifetime_v2(chart, 2020, 2030, sample_days=14, min_severity=3)
    bands_decade = filter_bands_for_age(chart, rank_and_consume(collapse_consecutive(raw_decade)))

    raw_child = scan_lifetime_v2(chart, 1996, 1998, sample_days=14, min_severity=2)
    bands_child = filter_bands_for_age(chart, rank_and_consume(collapse_consecutive(raw_child)))

    past_top = sorted(
        sorted(past_bands, key=lambda x: (-x.get("score", 0), -x.get("max_sev", x.get("severity", 0))))[:35],
        key=lambda x: x.get("window_start") or dt.datetime.min,
    )

    childhood = top_bands(filter_past(bands_child, TODAY.date()), limit=8)
    forward15 = top_bands(bands_5y, limit=15)
    forward15 = sorted(forward15, key=lambda x: x.get("window_start") or dt.datetime.min)
    decade = top_bands(filter_bands(bands_decade, 2020, 2030), limit=12)
    decade = sorted(decade, key=lambda x: x.get("window_start") or dt.datetime.min)

    return {
        "chart": chart,
        "dasha_rows": dasha_rows,
        "past": past_top,
        "childhood": childhood,
        "forward15": forward15,
        "decade": decade,
    }


def write_timeline_md(data):
    name = data["chart"].get("name", "Manoj")
    birth_line = "25-05-1996 20:25 | Coimbatore | Dhanus lagna | Magha nakshatra"

    lines = [
        f"# {name} - Lifetime and Forward Timeline",
        "",
        f"**Birth:** {birth_line}  ",
        f"**As of:** 2026-06-02 | Source: event_predictor_v2",
        "",
        f"> {RULE_ENGINE_DISCLAIMER_TA}",
        "",
        "---",
        "",
        "## Section A - Past (1996 to 2026-06-02)",
        "",
        "Top engine windows by life domain (childhood, father, health, education, career, marriage, wealth, travel).",
        "",
        "| Date range | Domain | What (English) | Tamil one-liner | Strength |",
        "|---|---|---|---|---|",
    ]
    for b in data["past"]:
        r = row_bilingual(b)
        lines.append(
            f"| {r['range_en']} | {r['domain_en']} | {r['what_en']} | {r['what_ta']} | {r['strength']} |"
        )

    lines += [
        "",
        "### Childhood highlight band (1996-1998)",
        "",
        "| Date range | Domain | What (English) | Tamil | Strength |",
        "|---|---|---|---|---|",
    ]
    for b in data["childhood"]:
        r = row_bilingual(b)
        lines.append(
            f"| {r['range_en']} | {r['domain_en']} | {r['what_en']} | {r['what_ta']} | {r['strength']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Section B - Active now (June 2026)",
        "",
        "| Level | Dasha | Until | Effect |",
        "|---|---|---|---|",
    ]
    for r in data["dasha_rows"]:
        lines.append(f"| {r['level']} | {r['lords']} | {r['until']} | {r['effect']} |")

    lines += [
        "",
        "**Summary (English):** Moon MD (until Jul 2033) | Moon-Rahu AD and PD (until 11 Jun 2026) | Mars PD - action, foreign/career shifts | Venus SD - partnership focus.",
        "",
        "---",
        "",
        "## Section C - Next 5 years (2026-2030)",
        "",
        "Top 15 forward windows (chronological).",
        "",
        "| Date range | Domain | What (English) | Tamil one-liner | Strength |",
        "|---|---|---|---|---|",
    ]
    for b in data["forward15"]:
        r = row_bilingual(b)
        lines.append(
            f"| {r['range_en']} | {r['domain_en']} | {r['what_en']} | {r['what_ta']} | {r['strength']} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Section D - Decade summary (2020-2030)",
        "",
        "| Date range | Domain | What (English) | Tamil one-liner | Strength |",
        "|---|---|---|---|---|",
    ]
    for b in data["decade"]:
        r = row_bilingual(b)
        lines.append(
            f"| {r['range_en']} | {r['domain_en']} | {r['what_en']} | {r['what_ta']} | {r['strength']} |"
        )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_MD}")


def write_timeline_en(data):
    name = data["chart"].get("name", "Manoj")
    lines = [
        f"# {name} - Lifetime and Forward Timeline (English)",
        "",
        "**DOB:** 1996-05-25 20:25 Coimbatore  ",
        "**As of:** 2026-06-02 | event_predictor_v2",
        "",
        "> Mechanical rule-engine windows - not guaranteed predictions.",
        "",
        "## A - Past (1996 to 2026-06-02)",
        "",
        "| Date range | Domain | What | Strength |",
        "|---|---|---|---|",
    ]
    for b in data["past"]:
        r = row_bilingual(b)
        lines.append(f"| {r['range_en']} | {r['domain_en']} | {r['what_en']} | {r['strength']} |")

    lines += [
        "",
        "## B - Active now (June 2026)",
        "",
        "| Level | Dasha | Until | Effect |",
        "|---|---|---|---|",
    ]
    for r in data["dasha_rows"]:
        lines.append(f"| {r['level']} | {r['lords']} | {r['until']} | {r['effect']} |")

    lines += [
        "",
        "## C - Next 5 years (2026-2030)",
        "",
        "| Date range | Domain | What | Strength |",
        "|---|---|---|---|",
    ]
    for b in data["forward15"]:
        r = row_bilingual(b)
        lines.append(f"| {r['range_en']} | {r['domain_en']} | {r['what_en']} | {r['strength']} |")

    lines += [
        "",
        "## D - Decade 2020-2030",
        "",
        "| Date range | Domain | What | Strength |",
        "|---|---|---|---|",
    ]
    for b in data["decade"]:
        r = row_bilingual(b)
        lines.append(f"| {r['range_en']} | {r['domain_en']} | {r['what_en']} | {r['strength']} |")

    OUT_EN.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_EN}")


def main():
    if not CHART_PATH.exists():
        print(f"Missing chart: {CHART_PATH}")
        sys.exit(1)
    data = collect()
    write_timeline_md(data)
    write_timeline_en(data)


if __name__ == "__main__":
    main()
