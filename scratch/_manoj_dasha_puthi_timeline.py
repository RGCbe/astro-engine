#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manoj Mahadasha / Puthi (AD) timeline with event bands, Expect & Watch (TA + EN)."""
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
ROOT = _SCRATCH.parent if sys.platform == "win32" else (Path("/opt/astro") if Path("/opt/astro").exists() else _SCRATCH.parent)
RUNTIME = ROOT / "runtime"
ENGINE = ROOT / "engine"
REPORTS = ROOT / "reports"
sys.path.insert(0, str(_SCRATCH))
sys.path.insert(0, str(ENGINE))
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(ROOT))

from _report_out_dir import category_report_dir
from _manoj_tamil_predictions_report import fmt_win, row_dict
from event_narrative import (
    format_source_mechanism_cell,
    infer_source_and_mechanism,
    is_life_event_band,
    narrative_for_band,
    summarize_puthi_narrative,
)
from event_age_policy import (
    filter_bands_for_age,
    band_fits_puthi_window,
    client_age_label,
)
from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from granular_dasha import build_full_timeline
from tamil_translations import (
    MD_THEME_TA,
    MD_EXPECT_TA,
    PLANETS_TA,
    RASIS_TA,
    RULE_ENGINE_DISCLAIMER_TA,
)
from generate_tamil_pdf import MD_WATCH_TA
from generate_deep_pdf import MD_EXPECT, MD_WATCH
from engine.jathagam_template import build_jathagam_full, build_prediction_section_header

CHART_PATH = ROOT / "charts" / "manoj_chart.json"
END_YEAR = 2035
TODAY = dt.datetime(2026, 6, 2)
OUT_DIR = category_report_dir("manoj", base=REPORTS, when=TODAY.date())
OUT_TA = OUT_DIR / "MANOJ_DASHA_PUTHI_TIMELINE_TA.md"
OUT_EN = OUT_DIR / "MANOJ_DASHA_PUTHI_TIMELINE_EN.md"

RASIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
RASI_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

CAT_PRIORITY = {
    "father": 0, "mother": 1, "health": 2, "health_self": 2, "self_accident": 2,
    "saham_roga": 2, "marriage": 3, "engagement": 3, "relationship_phase": 3,
    "saham_kalatra": 3, "career": 4, "promotion": 4, "career_breakthrough": 4,
    "leadership_emergence": 4, "wealth": 5, "wealth_peak": 5, "education": 6,
    "travel": 7, "children": 8,
}

# English chart-specific AD notes; Tamil built at runtime via _ta_pair_notes()
MANOJ_CHART_NOTES_EN = {
    ("Ketu", "Saturn"): {
        "expect": [
            "Ketu+Saturn in 4th - home, mother, inner peace, property foundations",
            "First months after birth - family climate; father-band flagged by rule engine",
        ],
        "watch": [
            "Saturn in 4th - delays at home, mother/family emotional load",
            "Ketu - vague symptoms; get medical check if unclear",
        ],
    },
    ("Ketu", "Mercury"): {
        "expect": [
            "Mercury (7L+10L) in 5th - early learning, speech, creativity, childhood intellect",
            "End of Ketu MD - shedding old patterns; first spiritual/intuitive wave",
        ],
        "watch": [
            "Mercury with Mars in 5th - hyperactivity; watch childhood bumps/injuries",
            "7L Mercury - early relationship/circle changes or separation stress",
        ],
    },
}

def _ta_ui():
    """Tamil UI strings (unicode escapes only - safe on Windows save)."""
    return {
        "title_suffix": "\u0ba4\u0bbf\u0b9a\u0bc8 / \u0baa\u0bc1\u0ba4\u0bcd\u0ba4\u0bbf \u0b95\u0bbe\u0bb2\u0bb5\u0bb0\u0bbf\u0b9a\u0bc8",
        "birth": "\u0baa\u0bbf\u0bb1\u0baa\u0bcd\u0baa\u0bc1",
        "place": "\u0b95\u0bcb\u0baf\u0bae\u0bcd\u0baa\u0bc1\u0ba4\u0bcd\u0ba4\u0bc2\u0bb0\u0bcd",
        "lagna": "\u0ba4\u0ba9\u0bc1\u0bb8\u0bc1 \u0bb2\u0b95\u0bcd\u0ba9\u0bae\u0bcd",
        "nak": "\u0bae\u0b95 \u0ba8\u0b9f\u0bcd\u0b9a\u0ba4\u0bcd\u0ba4\u0bbf\u0bb0\u0bae\u0bcd",
        "md": "\u0bae\u0b95\u0bbe \u0ba4\u0bbf\u0b9a\u0bc8",
        "puthi": "\u0baa\u0bc1\u0ba4\u0bcd\u0ba4\u0bbf",
        "expect": "\u0b8e\u0ba4\u0bbf\u0bb0\u0bcd\u0baa\u0bbe\u0bb0\u0bcd",
        "watch": "\u0b95\u0bb5\u0ba9\u0bbf\u0b95\u0bcd\u0b95",
        "events": "\u0b87\u0b95\u0bcd\u0b95\u0bbe\u0bb2 \u0ba8\u0bbf\u0b95\u0bb4\u0bcd\u0bb5\u0bc1 \u0b9a\u0bbe\u0bb3\u0bb0\u0b99\u0bcd\u0b95\u0bb3\u0bcd (event_predictor_v2)",
        "houses": "\u0b9a\u0bc6\u0baf\u0bb2\u0bcd\u0baa\u0b9f\u0bc1\u0bae\u0bcd \u0bb5\u0bc0\u0b9f\u0bcd\u0b9f\u0bc1 \u0b85\u0ba4\u0bbf\u0baa\u0ba4\u0bbf\u0b95\u0bb3\u0bcd",
        "age": "\u0bb5\u0baf\u0ba4\u0bc1 \u0bae\u0bc1\u0b9f\u0bbf\u0bb5\u0bbf\u0bb2\u0bcd",
        "lord_of": "\u0bb5\u0bc0\u0b9f\u0bcd\u0b9f\u0bc1 \u0b85\u0ba4\u0bbf\u0baa\u0ba4\u0bbf",
        "in_house": "\u0bb5\u0bc0\u0b9f\u0bcd\u0b9f\u0bbf\u0bb2\u0bcd",
        "puthi_word": "\u0baa\u0bc1\u0ba4\u0bcd\u0ba4\u0bbf:",
        "h_suffix": "\u0bae\u0bcd",
        "4th": "4-\u0bb5\u0ba4\u0bc1",
        "source": "\u0bae\u0bc2\u0bb2\u0bae\u0bcd / \u0bb5\u0bb4\u0bbf",
        "active_lords": "\u0b9a\u0bc6\u0baf\u0bb2\u0bcd\u0baa\u0b9f\u0bc1\u0bae\u0bcd \u0b85\u0ba4\u0bbf\u0baa\u0ba4\u0bbf\u0b95\u0bb3\u0bcd",
        "income_sources": "\u0bb5\u0bb0\u0bc1\u0bae\u0bbe\u0ba9 \u0bb5\u0bb4\u0b99\u0bcd\u0b95\u0bb3\u0bcd",
        "loss_mechanism": "\u0b87\u0bb4\u0baa\u0bcd\u0baa\u0bc1 \u0b8e\u0bb5\u0bb5\u0bc1",
        "career_sum": "\u0ba4\u0bca\u0bb4\u0bbf\u0bb2\u0bcd \u0b9a\u0bc1\u0bb1\u0bc1\u0b95\u0bb3\u0bcd",
        "marriage_sum": "\u0bb5\u0bbe\u0bb4\u0bcd\u0b95\u0bcd\u0b95\u0bc8 \u0b9a\u0bc1\u0bb1\u0bc1\u0b95\u0bb3\u0bcd",
        "life_events": "\u0b87\u0ba8\u0bcd\u0ba4 \u0baa\u0bc1\u0ba4\u0bcd\u0ba4\u0bbf\u0baf\u0bbf\u0bb2\u0bcd \u0bae\u0b9f\u0bcd\u0b9f\u0bc1\u0bae\u0bcd \u0ba8\u0bbf\u0b95\u0bb4\u0bcd\u0bb5\u0bc1 \u0b9a\u0bbe\u0bb3\u0bb0\u0b99\u0bcd\u0b95\u0bb3\u0bcd",
        "dates": "\u0ba4\u0bc7\u0ba4\u0bbf",
        "event": "\u0ba8\u0bbf\u0b95\u0bb4\u0bcd\u0bb5\u0bc1",
        "source_mech": "\u0bae\u0bc2\u0bb2\u0bae\u0bcd/\u0bb5\u0bb4? (TA+EN)",
        "strength": "\u0bb5\u0bb2\u0bc1\u0bae\u0bcd",
    }


TA_UI = _ta_ui()

PLANET_MANOJ_EN = {
    "Jupiter": "Lagna lord Jupiter in 1st - identity, body, public persona",
    "Moon": "Moon in 9th - father, dharma, higher learning, travel",
    "Mercury": "Mercury in 5th, rules 7+10 - career/marriage via creativity and 5th-house themes",
    "Venus": "Venus in 7th - spouse, contracts, arts",
    "Saturn": "Saturn in 4th (with Ketu) - home, mother, patience lessons",
    "Ketu": "Ketu in 4th - detachment at home, spirituality",
    "Rahu": "Rahu in 10th - career, fame, unconventional path",
    "Sun": "Sun in 6th - service, work pressure, father/health themes",
    "Mars": "Mars in 5th - courage, sport, property/creativity",
}


def _ta_pair_notes(md: str, ad: str) -> dict[str, list[str]]:
    k, s, m, me = PLANETS_TA["Ketu"], PLANETS_TA["Saturn"], PLANETS_TA["Mars"], PLANETS_TA["Mercury"]
    u = TA_UI
    if (md, ad) == ("Ketu", "Saturn"):
        return {
            "expect": [
                f"{k}+{s} {u['4th']} - \u0bb5\u0bc0\u0b9f\u0bc1, \u0ba4\u0bbe\u0baf\u0bcd",
                "\u0baa\u0bbf\u0bb1\u0baa\u0bcd\u0baa\u0bc1 \u0bae\u0bc1\u0ba4\u0bb2\u0bcd - \u0b95\u0bc1\u0b9f\u0bc1\u0bae\u0bcd\u0baa \u0b9a\u0bc2\u0bb4\u0bb2\u0bcd",
            ],
            "watch": [
                f"{s} {u['4th']} - \u0bb5\u0bc0\u0b9f\u0bcd\u0b9f\u0bbf\u0bb2\u0bcd \u0ba4\u0bbe\u0bae\u0ba4\u0bae\u0bcd",
                f"{k} - \u0ba4\u0bc6\u0bb3\u0bbf\u0bb5\u0bbf\u0bb1\u0bcd\u0bb1 \u0b89\u0b9f\u0bb2\u0bcd",
            ],
        }
    if (md, ad) == ("Ketu", "Mercury"):
        return {
            "expect": [
                f"{me} (7+10 \u0b85\u0ba4\u0bbf\u0baa\u0ba4\u0bbf) 5-\u0bb5\u0ba4\u0bc1",
                f"{k} \u0ba4\u0bbf\u0b9a\u0bc8 \u0bae\u0bc1\u0b9f\u0bbf\u0bb5\u0bc1",
            ],
            "watch": [
                f"{me} {m} 5-\u0bb5\u0ba4\u0bc1 - \u0b85\u0ba4\u0bbf\u0b95 \u0b9a\u0bc1\u0bb1\u0bc1\u0bb1\u0bc1\u0bb5\u0bc1",
                "7L \u0baa\u0bc1\u0ba4\u0ba9\u0bcd - \u0b9a\u0bbf\u0bb1\u0bc1 \u0bb5\u0baf\u0ba4\u0bbf\u0bb2\u0bcd \u0b89\u0bb1\u0bb5\u0bc1",
            ],
        }
    return {"expect": [], "watch": []}


def _ta_planet_note(planet: str) -> str:
    p = PLANETS_TA.get(planet, planet)
    u = TA_UI
    h = u["4th"][2:]
    notes = {
        "Jupiter": f"\u0bb2\u0b95\u0bcd\u0ba9\u0bbe\u0ba4\u0bbf\u0baa\u0ba4\u0bbf {p} 1-{h}",
        "Moon": f"{p} 9-{h}",
        "Mercury": f"{p} 5-{h}, 7+10 \u0b85\u0ba4\u0bbf\u0baa\u0ba4\u0bbf",
        "Venus": f"{p} 7-{h}",
        "Saturn": f"{p} {u['4th']} (\u0b95\u0bc7\u0ba4\u0bc1)",
        "Ketu": f"{p} {u['4th']}",
        "Rahu": f"{p} 10-{h}",
        "Sun": f"{p} 6-{h}",
        "Mars": f"{p} 5-{h}",
    }
    return notes.get(planet, "")


def house_lord(lagna_idx: int, house: int) -> str:
    return RASI_LORDS[RASIS[(lagna_idx + house - 1) % 12]]


def houses_ruled_by(lagna_idx: int, planet: str) -> list[int]:
    return [h for h in range(1, 13) if house_lord(lagna_idx, h) == planet]


def fmt_range(start: dt.datetime, end: dt.datetime, lang: str) -> str:
    if lang == "ta":
        return fmt_win(start, end, "ta")
    return f"{start.strftime('%Y-%m-%d')} -> {end.strftime('%Y-%m-%d')}"


def age_years(birth: dt.datetime, when: dt.datetime) -> float:
    return round((when - birth).days / 365.25, 1)


def overlaps(ws, we, start, end) -> bool:
    if not ws:
        return False
    we = we or ws
    return ws <= end and we >= start


def lord_activation_text(chart: dict, md: str, ad: str, lang: str) -> list[str]:
    lagna_idx = chart.get("lagna_idx", 8)
    lines = []
    for planet in (md, ad):
        hs = houses_ruled_by(lagna_idx, planet)
        pos = chart.get("positions", {}).get(planet, {})
        ph = pos.get("house")
        if lang == "ta":
            u = TA_UI
            hs_s = ", ".join(f"{h}{u['h_suffix']}" for h in hs) if hs else "-"
            pl = PLANETS_TA.get(planet, planet)
            rasi = RASIS_TA.get(pos.get("rasi", ""), pos.get("rasi", ""))
            line = f"{pl} - {hs_s} {u['lord_of']}"
            if ph:
                line += f"; {ph}\u0bb5\u0ba4\u0bc1 {u['in_house']} ({rasi})"
            note = _ta_planet_note(planet)
        else:
            hs_s = ", ".join(f"{h}H" for h in hs) if hs else "-"
            line = f"{planet} rules {hs_s}"
            if ph:
                line += f"; placed in H{ph} ({pos.get('rasi', '')})"
            note = PLANET_MANOJ_EN.get(planet, "")
        lines.append(line)
        if note:
            lines.append(note)
    return lines


def rank_band(b: dict) -> tuple:
    cat = b.get("category", "")
    return (
        CAT_PRIORITY.get(cat, 50),
        -b.get("max_sev", b.get("severity", 0)),
        -b.get("score", 0),
        b.get("window_start") or dt.datetime.min,
    )


def events_in_window(bands, start, end, chart=None, limit=10):
    """Bands overlapping puthi: event.start <= puthi.end AND event.end >= puthi.start."""
    hits = [
        b for b in bands
        if overlaps(b.get("window_start"), b.get("window_end"), start, end)
    ]
    if chart is not None:
        INFANT_OK = frozenset({"father", "mother", "health", "health_self"})
        hits = [
            b for b in hits
            if b.get("category") in INFANT_OK
            or band_fits_puthi_window(chart, b, start, end)
        ]
    life = [b for b in hits if is_life_event_band(b)]
    pool = life if life else hits
    pool.sort(key=rank_band)
    return pool[:limit]


def event_strength(b: dict) -> str:
    sev = b.get("max_sev", b.get("severity", 0))
    stars = b.get("stars", "") or ("*" * min(int(sev or 0), 3) if sev else "")
    conf = b.get("confidence", "")
    return stars or conf or str(sev or "-")


def format_event_table_row(b: dict, chart: dict, dasha_ctx: dict, lang: str) -> str:
    r = row_dict(b, lang)
    narr = narrative_for_band(chart, b, dasha_ctx)
    cell = format_source_mechanism_cell(narr)
    ev = (r["plain"] or "").replace("|", "/")
    prefix = client_age_label(b, lang)
    if prefix:
        ev = prefix + ev
    dates = (r["window"] or "").replace("|", "/")
    return f"| {dates} | {ev} | {cell} | {event_strength(b)} |"


def build_expect(md, ad, chart, lang):
    custom_en = MANOJ_CHART_NOTES_EN.get((md, ad), {})
    if lang == "ta":
        base = list(MD_EXPECT_TA.get(ad, []))[:3] + list(MD_EXPECT_TA.get(md, []))[:2]
        extra = list(_ta_pair_notes(md, ad).get("expect", []))
        theme = MD_THEME_TA.get(ad, "")
        if theme:
            base.insert(0, f"{PLANETS_TA.get(ad, ad)} {TA_UI['puthi_word']} {theme}")
    else:
        base = list(MD_EXPECT.get(ad, []))[:3] + list(MD_EXPECT.get(md, []))[:2]
        extra = list(custom_en.get("expect", []))
        if ad != md:
            base.insert(0, f"{ad} antardasha themes within {md} mahadasha")
    for planet in (ad, md):
        note = _ta_planet_note(planet) if lang == "ta" else PLANET_MANOJ_EN.get(planet, "")
        if note and note not in base and note not in extra:
            extra.append(note)
    merged, seen = [], set()
    for line in base + extra:
        if line and line not in seen:
            seen.add(line)
            merged.append(line)
    return merged[:6]


def build_watch(md, ad, chart, lang):
    custom_en = MANOJ_CHART_NOTES_EN.get((md, ad), {})
    if lang == "ta":
        base = list(MD_WATCH_TA.get(ad, []))[:3] + list(MD_WATCH_TA.get(md, []))[:2]
        extra = list(_ta_pair_notes(md, ad).get("watch", []))
    else:
        base = list(MD_WATCH.get(ad, []))[:3] + list(MD_WATCH.get(md, []))[:2]
        extra = list(custom_en.get("watch", []))
    if chart["positions"].get("Saturn", {}).get("house") == 4:
        line = (
            f"{TA_UI['4th']} \u0b9a\u0ba9\u0bbf+\u0b95\u0bc7\u0ba4\u0bc1 - \u0bb5\u0bc0\u0b9f\u0bc1/\u0ba4\u0bbe\u0baf\u0bcd"
            if lang == "ta"
            else "Saturn+Ketu in 4th - home/mother/inner peace strain"
        )
        if line not in base:
            extra.append(line)
    if ad == "Mercury" or md == "Mercury":
        line = (
            "\u0baa\u0bc1\u0ba4\u0ba9\u0bcd 5-\u0bb5\u0ba4\u0bc1+7/10 \u0b85\u0ba4\u0bbf\u0baa\u0ba4\u0bbf - \u0b92\u0baa\u0bcd\u0baa\u0ba8\u0bcd\u0ba4\u0bae\u0bcd/\u0ba4\u0bca\u0bb4\u0bbf\u0bb2\u0bcd"
            if lang == "ta"
            else "Mercury 5th + 7L/10L - overthinking contracts/career moves"
        )
        if line not in base:
            extra.append(line)
    merged, seen = [], set()
    for line in base + extra:
        if line and line not in seen:
            seen.add(line)
            merged.append(line)
    return merged[:6]


def build_timeline(chart):
    b = chart["birth"]
    birth = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    horizon = dt.datetime(END_YEAR, 12, 31)
    tl = build_full_timeline(chart, levels=2)
    mds = [r for r in tl if r["level"] == 1 and r["start"] <= horizon]
    ads = [r for r in tl if r["level"] == 2 and r["start"] <= horizon]
    raw = scan_lifetime_v2(chart, b["year"], END_YEAR, sample_days=14, min_severity=2)
    bands = rank_and_consume(collapse_consecutive(raw))
    bands = filter_bands_for_age(chart, bands)
    # Childhood scan after age filter � restores early father/mother bands dropped globally
    raw_child = scan_lifetime_v2(chart, b["year"], b["year"] + 2, sample_days=14, min_severity=2)
    bands_child = rank_and_consume(collapse_consecutive(raw_child))
    CHILD_INJECT = frozenset({"father", "mother", "health", "health_self", "children"})
    seen = {(x.get("category"), x.get("window_start")) for x in bands}
    for bc in bands_child:
        if bc.get("category") not in CHILD_INJECT:
            continue
        key = (bc.get("category"), bc.get("window_start"))
        if key in seen:
            continue
        try:
            from event_age_policy import annotate_band_age_fit as _abf
            _abf(chart, bc)
        except Exception:
            pass
        bands.append(bc)
        seen.add(key)
    md_blocks = []
    for md_rec in mds:
        ad_list = sorted(
            [a for a in ads if a["md"] == md_rec["md"] and a["start"] < md_rec["end"]],
            key=lambda x: x["start"],
        )
        md_blocks.append({"md": md_rec, "ads": ad_list})
    return md_blocks, bands, birth


def render_report(chart, md_blocks, bands, birth, lang):
    name = chart.get("name", "Manoj")
    b = chart["birth"]
    if lang == "ta":
        u = TA_UI
        title = f"# {name} - {u['title_suffix']}"
        birth_line = (
            f"**{u['birth']}:** {b['day']:02d}-{b['month']:02d}-{b['year']} "
            f"{b.get('hour', 0):02d}:{b.get('min', 0):02d} | {u['place']} | {u['lagna']} | {u['nak']}"
        )
        md_lbl, puthi_lbl = u["md"], u["puthi"]
        expect_lbl, watch_lbl = u["expect"], u["watch"]
        age_lbl = u["age"]
        active_lbl = u["active_lords"]
        income_lbl = u["income_sources"]
        loss_lbl = u["loss_mechanism"]
        career_lbl = u["career_sum"]
        marriage_lbl = u["marriage_sum"]
        life_lbl = u["life_events"]
        disclaimer = f"> {RULE_ENGINE_DISCLAIMER_TA}"
        sep = " | "
        chain_sep = "-"
    else:
        title = f"# {name} - Mahadasha / Puthi (Antardasha) Timeline"
        birth_line = (
            f"**Birth:** {b['year']}-{b['month']:02d}-{b['day']:02d} "
            f"{b.get('hour', 0):02d}:{b.get('min', 0):02d} Coimbatore | Sagittarius lagna | Magha nakshatra"
        )
        md_lbl, puthi_lbl = "Mahadasha", "Puthi"
        expect_lbl, watch_lbl = "Expect", "Watch"
        age_lbl = "Age at end"
        active_lbl = "Active lords"
        income_lbl = "Likely income sources"
        loss_lbl = "How losses may occur"
        career_lbl = "Career highlights (this Puthi)"
        marriage_lbl = "Marriage / relationship (this Puthi)"
        life_lbl = "Life events in this Puthi only"
        disclaimer = "> Rule-engine windows from event_predictor_v2 - not guaranteed predictions."
        sep = " | "
        chain_sep = "-"

    lines = [
        title,
        "",
        build_jathagam_full(chart, lang, when=TODAY),
        build_prediction_section_header(lang),
        f"**Generated:** {TODAY.date().isoformat()}{sep}Vimshottari through {END_YEAR}",
        "",
        disclaimer,
        "",
    ]

    for block in md_blocks:
        md_rec = block["md"]
        md = md_rec["md"]
        md_end = md_rec["end"]
        lines.append(
            f"## {md_lbl} ({md}){sep}{fmt_range(md_rec['start'], md_end, lang)}{sep}"
            f"{age_lbl}: {age_years(birth, md_end)}"
        )
        if lang == "ta":
            lines.append(f"*{MD_THEME_TA.get(md, '')}*")
        lines.append("")

        for i, ad_rec in enumerate(block["ads"], 1):
            ad = ad_rec["ad"]
            ad_end = ad_rec["end"]
            chain = f"{md}{chain_sep}{ad}"
            lines.append(
                f"### {puthi_lbl} {i}: {chain}{sep}{fmt_range(ad_rec['start'], ad_end, lang)}{sep}"
                f"{age_lbl}: {age_years(birth, ad_end)}"
            )
            lines.append("")
            lines.append(f"**{active_lbl}:**")
            for hl in lord_activation_text(chart, md, ad, lang):
                lines.append(f"- {hl}")
            evs = events_in_window(bands, ad_rec["start"], ad_end, chart=chart)
            dasha_ctx = {"md": md, "ad": ad}
            summary = summarize_puthi_narrative(chart, md, ad, evs)
            lines.append("")
            lines.append(f"**{income_lbl}:**")
            for bullet in (summary["income_ta" if lang == "ta" else "income_en"].split("; ")[:4]):
                lines.append(f"- {bullet}")
            lines.append("")
            lines.append(f"**{loss_lbl}:**")
            for bullet in (summary["loss_ta" if lang == "ta" else "loss_en"].split("; ")[:4]):
                lines.append(f"- {bullet}")
            if summary.get("has_career") and summary.get("career_en"):
                lines.append("")
                lines.append(f"**{career_lbl}:**")
                key = "career_ta" if lang == "ta" else "career_en"
                for bullet in summary[key].split("; ")[:3]:
                    if bullet.strip():
                        lines.append(f"- {bullet.strip()}")
            if summary.get("has_marriage") and summary.get("marriage_en"):
                lines.append("")
                lines.append(f"**{marriage_lbl}:**")
                key = "marriage_ta" if lang == "ta" else "marriage_en"
                for bullet in summary[key].split("; ")[:3]:
                    if bullet.strip():
                        lines.append(f"- {bullet.strip()}")
            lines.append("")
            lines.append(f"**{life_lbl}:**")
            u = TA_UI if lang == "ta" else {}
            hdr_dates = u.get("dates", "dates")
            hdr_event = u.get("event", "event")
            hdr_sm = u.get("source_mech", "source/mechanism TA+EN")
            hdr_str = u.get("strength", "strength")
            lines.append(f"| {hdr_dates} | {hdr_event} | {hdr_sm} | {hdr_str} |")
            lines.append("|---|---|---|---|")
            if evs:
                for bnd in evs:
                    lines.append(format_event_table_row(bnd, chart, dasha_ctx, lang))
            else:
                lines.append("| - | - | - | - |")
            lines.append("")
            lines.append(f"**{expect_lbl}:**")
            for ex in build_expect(md, ad, chart, lang):
                lines.append(f"- {ex}")
            lines.append("")
            lines.append(f"**{watch_lbl}:**")
            for w in build_watch(md, ad, chart, lang):
                lines.append(f"- {w}")
            lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    if not CHART_PATH.exists():
        print(f"Missing chart: {CHART_PATH}")
        sys.exit(1)
    chart = json.loads(CHART_PATH.read_text(encoding="utf-8"))
    md_blocks, bands, birth = build_timeline(chart)
    OUT_TA.write_text(render_report(chart, md_blocks, bands, birth, "ta"), encoding="utf-8")
    OUT_EN.write_text(render_report(chart, md_blocks, bands, birth, "en"), encoding="utf-8")
    print(f"Wrote {OUT_TA}")
    print(f"Wrote {OUT_EN}")


if __name__ == "__main__":
    main()
