#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manoj multi-engine comparison - Pure books / Pure match / Hybrid / Life-event engine."""
from __future__ import annotations

import csv
import datetime as dt
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_SCRATCH = Path(__file__).resolve().parent
ROOT = Path("/opt/astro") if Path("/opt/astro").exists() else _SCRATCH.parent
sys.path.insert(0, str(_SCRATCH))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(ROOT / "engine"))

from _report_out_dir import category_report_dir

CHART_PATH = ROOT / "charts" / "manoj_chart.json"
REPORTS = ROOT / "reports"
MANOJ_REPORTS = category_report_dir("manoj", base=REPORTS)
OUT_JSON = MANOJ_REPORTS / "MANOJ_ENGINE_COMPARISON.json"
OUT_MD = MANOJ_REPORTS / "MANOJ_ENGINE_COMPARISON.md"
OUT_CSV = MANOJ_REPORTS / "MANOJ_ENGINE_COMPARISON.csv"

RASIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
RASI_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

DOMAIN_SPECS = [
    {
        "id": "personality",
        "label": "Personality/self (1st/lagna)",
        "placements": [("Jupiter", 1)],
        "nak": "Magha",
        "event_cats": {"health_self", "honor"},
    },
    {
        "id": "career",
        "label": "Career (10th)",
        "placements": [("Rahu", 10)],
        "event_cats": {"career", "career_breakthrough", "promotion", "education"},
    },
    {
        "id": "marriage",
        "label": "Marriage (7th)",
        "placements": [("Venus", 7)],
        "event_cats": {"marriage", "engagement", "relationship_phase", "relationship_break"},
    },
    {
        "id": "father",
        "label": "Father (9th/Sun)",
        "placements": [("Sun", 6), ("Moon", 9)],
        "event_cats": {"father"},
    },
    {
        "id": "mother",
        "label": "Mother (4th/Moon)",
        "placements": [("Saturn", 4), ("Ketu", 4), ("Moon", 9)],
        "event_cats": {"mother"},
    },
    {
        "id": "wealth",
        "label": "Wealth (2nd/11th lords)",
        "placements": [("Mars", 5), ("Mercury", 5)],
        "lords": [2, 11],
        "event_cats": {"wealth", "wealth_peak", "wealth_loss", "property", "inheritance"},
    },
    {
        "id": "health",
        "label": "Health (6th/1st)",
        "placements": [("Sun", 6), ("Jupiter", 1)],
        "event_cats": {"health_self", "health"},
    },
]


def _clip(s: str, n: int = 140) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def house_lord(chart: dict, house: int) -> str:
    lagna_idx = chart.get("lagna_idx", 0)
    sign = RASIS[(lagna_idx + house - 1) % 12]
    return RASI_LORDS[sign]


def build_house_predictions(chart: dict) -> list[dict]:
    by_house: dict[int, list[str]] = {}
    for planet, pdata in chart.get("positions", {}).items():
        h = pdata.get("house")
        if h:
            by_house.setdefault(h, []).append(planet)
    return [{"house": h, "planets": sorted(ps)} for h, ps in sorted(by_house.items())]


def fmt_corpus_rule(r, max_books: int = 2) -> str:
    books = ", ".join((r.books or [])[:max_books])
    return f"{_clip(r.text, 100)} [{books}]"


def pure_books_domain(corpus, spec: dict, chart: dict, top_n: int = 5) -> list[dict]:
    rows = []
    for planet, house in spec.get("placements", []):
        for r in corpus.get_planet_in_house(planet, house, limit=top_n):
            rows.append({
                "placement": f"{planet} in H{house}",
                "text": _clip(r.text, 200),
                "books": r.books[:4],
                "n_books": len(r.books),
            })
    nak = spec.get("nak")
    if nak:
        for r in corpus.get_nakshatra_rules(nak, limit=3):
            rows.append({
                "placement": f"Janma nak {nak}",
                "text": _clip(r.text, 200),
                "books": r.books[:4],
                "n_books": len(r.books),
            })
    for h in spec.get("lords", []):
        lord = house_lord(chart, h)
        pos = chart["positions"].get(lord, {})
        ph = pos.get("house")
        if ph:
            for r in corpus.get_planet_in_house(lord, ph, limit=3):
                rows.append({
                    "placement": f"H{h} lord {lord} in H{ph}",
                    "text": _clip(r.text, 200),
                    "books": r.books[:4],
                    "n_books": len(r.books),
                })
    rows.sort(key=lambda x: -x.get("n_books", 0))
    return rows[:top_n]


def pure_match_domain(corpus, spec: dict, chart: dict) -> dict:
    from engine.comparative_test import synthesize_consensus

    all_rules = []
    snippets = []
    for planet, house in spec.get("placements", []):
        rules = corpus.get_planet_in_house(planet, house, limit=50)
        all_rules.extend(rules)
        if rules:
            snippets.append(f"{planet}×H{house}: {synthesize_consensus(rules)['status']} ({synthesize_consensus(rules)['consensus_percent']}%)")
    if not all_rules:
        return {"summary": "No indexed rules", "consensus_percent": None, "status": "N/A"}
    cons = synthesize_consensus(all_rules)
    return {
        "summary": "; ".join(snippets[:3]) or cons["status"],
        "consensus_percent": cons["consensus_percent"],
        "status": cons["status"],
        "disclaimer": cons["disclaimer"],
        "n_rules": cons["total_rules_analyzed"],
    }


def summarize_hybrid_bands(bands: list, cats: set, year_from: int, year_to: int, top: int = 3) -> str:
    hits = []
    for b in bands:
        cat = b.get("category", "")
        norm = cat[6:] if cat.startswith("event_") else cat
        if norm not in cats and cat not in cats:
            continue
        ws = str(b.get("window_start", ""))[:10]
        we = str(b.get("window_end", ""))[:10]
        if ws and ws[:4] > str(year_to):
            continue
        if we and we[:4] < str(year_from):
            continue
        hits.append(b)
    hits.sort(key=lambda x: x.get("severity", 0), reverse=True)
    parts = []
    for b in hits[:top]:
        cite = ""
        if b.get("verified_classical"):
            cite = f" [verified:{b.get('scripture_source', '')}]"
        parts.append(
            f"{_clip(b.get('event', b.get('classical_title', '')), 60)} "
            f"({ws if (ws := str(b.get('window_start', ''))[:10]) else '?'}) sev={b.get('severity')}{cite}"
        )
    return " | ".join(parts) if parts else "—"


def summarize_event_bands(bands: list, cats: set, year_from: int, year_to: int, top: int = 5) -> list[dict]:
    hits = []
    for b in bands:
        if b.get("category") not in cats:
            continue
        ws = str(b.get("window_start", ""))[:10]
        we = str(b.get("window_end", ""))[:10]
        try:
            y0 = int(ws[:4]) if ws else year_from
            y1 = int(we[:4]) if we else year_to
        except ValueError:
            continue
        if y1 < year_from or y0 > year_to:
            continue
        hits.append(b)
    hits.sort(key=lambda x: x.get("max_sev", x.get("severity", 0)), reverse=True)
    out = []
    for b in hits[:top]:
        why = b.get("max_why") or b.get("why") or []
        if isinstance(why, list):
            why = why[:2]
        out.append({
            "event": _clip(b.get("event", ""), 80),
            "window": f"{str(b.get('window_start', ''))[:10]} -> {str(b.get('window_end', ''))[:10]}",
            "severity": b.get("max_sev", b.get("severity")),
            "why": why,
        })
    return out


def agreement_label(books_snip: str, match_status: str, hybrid: str, events: list) -> str:
    has_b = books_snip and books_snip != "—"
    has_m = match_status and "N/A" not in match_status
    has_h = hybrid and hybrid != "—"
    has_e = bool(events)
    n = sum([has_b, has_m, has_h, has_e])
    if n >= 3:
        return "Broad alignment"
    if n == 2:
        return "Partial"
    return "Sparse / divergent"


def dasha_cause(chart: dict, when: dt.datetime) -> str:
    from granular_dasha import build_full_timeline, lookup

    tl = build_full_timeline(chart, levels=4)
    active = lookup(tl, when)
    parts = []
    for lvl in sorted(active):
        rec = active[lvl]
        name = ["", "MD", "AD", "PD", "SD"][lvl]
        lords = "-".join(rec[k] for k in ("md", "ad", "pd", "sd") if k in rec)
        parts.append(f"{name} {lords}")
    return " -> ".join(parts) if parts else "—"


def birth_snapshot_table(chart: dict) -> list[dict]:
    b = chart["birth"]
    rows = [
        {"field": "Name", "value": chart.get("name", "Manoj"), "cause": "chart metadata"},
        {"field": "Birth", "value": f"{b['year']}-{b['month']:02d}-{b['day']:02d} {b['hour']:02d}:{b['min']:02d}", "cause": "canonical fixture"},
        {"field": "Place", "value": f"{b.get('place', 'Coimbatore')} ({b['lat']}, {b['lon']})", "cause": "geocode"},
        {"field": "Lagna", "value": f"{chart['lagna']} (lord {chart.get('lagna_lord')})", "cause": f"lagna_lon={chart.get('lagna_lon', 0):.2f}° ayanamsa={chart.get('ayanamsa')}"},
        {"field": "Janma nak", "value": f"{chart.get('janma_nakshatra')} ({chart.get('janma_nakshatra_lord')})", "cause": "Moon longitude -> nakshatra"},
        {"field": "Moon rasi", "value": chart.get("moon_rasi", ""), "cause": "Moon sign from D1"},
    ]
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        p = chart["positions"][planet]
        rows.append({
            "field": planet,
            "value": f"{p['rasi']} H{p['house']} ({p['nak']})",
            "cause": f"sidereal lon {p.get('lon_abs', p.get('lon', '')):.2f}°" if isinstance(p.get("lon_abs"), (int, float)) else "stored chart",
        })
    return rows


def run():
    chart = json.loads(CHART_PATH.read_text(encoding="utf-8"))
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])

    from engine.corpus import get_corpus
    from engine.comparative_test import execute_corpus_battle_comparison
    from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive
    from engine_pure_hybrid import hybrid_engine_instance

    corpus = get_corpus()
    chart_battle = {
        "house_predictions": build_house_predictions(chart),
        "detected_yogas": [],
        "current_dasha": None,
    }
    battle_full = execute_corpus_battle_comparison(chart_battle)

    # Life-event engine scans
    ev_raw_0_30 = scan_lifetime_v2(chart, b["year"], b["year"] + 30, sample_days=14, min_severity=2)
    ev_bands_0_30 = collapse_consecutive(ev_raw_0_30)
    ev_raw_20_26 = scan_lifetime_v2(chart, 2020, 2026, sample_days=14, min_severity=2)
    ev_bands_20_26 = collapse_consecutive(ev_raw_20_26)
    ev_bands_all = collapse_consecutive(
        scan_lifetime_v2(chart, b["year"], 2026, sample_days=14, min_severity=2)
    )

    hybrid_now = hybrid_engine_instance.scan_hybrid_lifetime(chart, 2020, 2026, sample_days=14, min_severity=2)
    hybrid_child = hybrid_engine_instance.scan_hybrid_lifetime(chart, 1996, 1998, sample_days=14, min_severity=2)
    hybrid_birth = hybrid_engine_instance.scan_hybrid_lifetime(chart, 1996, 1996, sample_days=30, min_severity=1)

    now = dt.datetime(2026, 6, 2)
    dasha_now = dasha_cause(chart, now)
    dasha_1996 = dasha_cause(chart, birth_dt)
    dasha_1997 = dasha_cause(chart, dt.datetime(1997, 6, 1))

    domain_rows = []
    for spec in DOMAIN_SPECS:
        books = pure_books_domain(corpus, spec, chart, top_n=5)
        match = pure_match_domain(corpus, spec, chart)
        books_cell = " // ".join(
            f"{r['placement']}: {_clip(r['text'], 70)} ({', '.join(r['books'][:2])})" for r in books[:3]
        ) or "—"
        match_cell = (
            f"{match['status']} {match['consensus_percent']}% classical consensus ({match['n_rules']} rules)"
            if match.get("consensus_percent") is not None
            else match.get("summary", "—")
        )
        hybrid_cell = summarize_hybrid_bands(
            hybrid_now["hybrid_bands"] + hybrid_now.get("classical_only_bands", []),
            spec["event_cats"],
            2024,
            2026,
        )
        ev_cell = summarize_event_bands(ev_bands_20_26, spec["event_cats"], 2024, 2026, top=3)
        ev_text = " | ".join(f"{e['event']} ({e['window']})" for e in ev_cell) if ev_cell else "—"
        domain_rows.append({
            "domain": spec["label"],
            "pure_books": books_cell,
            "pure_match": match_cell,
            "hybrid": hybrid_cell,
            "life_event": ev_text,
            "agreement": agreement_label(books_cell, match_cell, hybrid_cell, ev_cell),
            "books_detail": books,
            "match_detail": match,
        })

    time_windows = [
        {
            "period": "NOW 2024-2026",
            "chart_cause": dasha_now,
            "years": (2024, 2026),
            "hybrid_src": hybrid_now,
            "ev_bands": ev_bands_20_26,
        },
        {
            "period": "Childhood 1996-1998",
            "chart_cause": dasha_1997,
            "years": (1996, 1998),
            "hybrid_src": hybrid_child,
            "ev_bands": ev_bands_0_30,
        },
        {
            "period": "Birth May 1996",
            "chart_cause": dasha_1996,
            "years": (1996, 1996),
            "hybrid_src": hybrid_birth,
            "ev_bands": ev_bands_0_30,
        },
    ]

    window_rows = []
    for tw in time_windows:
        y0, y1 = tw["years"]
        all_cats = set()
        for spec in DOMAIN_SPECS:
            all_cats |= spec["event_cats"]
        ev_top = summarize_event_bands(tw["ev_bands"], all_cats, y0, y1, top=5)
        ev_str = " | ".join(f"{e['event']} ({e['window']})" for e in ev_top) if ev_top else "—"
        hb = tw["hybrid_src"]["hybrid_bands"] + tw["hybrid_src"].get("classical_only_bands", [])
        hybrid_str = summarize_hybrid_bands(hb, all_cats, y0, y1, top=4)
        # Dasha corpus for active MD at window mid
        mid = dt.datetime((y0 + y1) // 2, 6, 15)
        from granular_dasha import build_full_timeline, lookup

        act = lookup(build_full_timeline(chart, levels=2), mid)
        md = act.get(1, {}).get("md", "")
        dasha_rules = corpus.get_dasha_rules(md, limit=5) if md else []
        books_dasha = " // ".join(_clip(r.text, 60) + f" [{', '.join(r.books[:1])}]" for r in dasha_rules[:2])
        window_rows.append({
            "period": tw["period"],
            "chart_cause": tw["chart_cause"],
            "pure_books": books_dasha or "Natal placements (see Table B)",
            "pure_match": f"MD {md} dasha passages indexed" if md else "—",
            "hybrid": hybrid_str,
            "life_event": ev_str,
            "real_world": "(no known_events in manoj_chart.json)",
        })

    birth_period_rows = []
    for spec in DOMAIN_SPECS[:5]:
        books = pure_books_domain(corpus, spec, chart, top_n=2)
        ev_list = summarize_event_bands(ev_bands_0_30, spec["event_cats"], 1996, 1998, top=1)
        if ev_list:
            le = f"{ev_list[0]['event']} ({ev_list[0]['window']})"
        else:
            le = "—"
        birth_period_rows.append({
            "factor": spec["label"],
            "natal": ", ".join(f"{p} H{h}" for p, h in spec.get("placements", [])),
            "pure_books": books[0]["text"] if books else "—",
            "pure_match": pure_match_domain(corpus, spec, chart).get("status", "—"),
            "hybrid": summarize_hybrid_bands(hybrid_birth["hybrid_bands"], spec["event_cats"], 1996, 1996, top=1),
            "life_event": le,
        })

    payload = {
        "generated_at": dt.datetime.now().isoformat(),
        "root": str(ROOT),
        "chart_path": str(CHART_PATH),
        "canonical_birth": {
            "date": "1996-05-25",
            "time": "20:25",
            "place": "Coimbatore",
            "lat": b["lat"],
            "lon": b["lon"],
        },
        "table_a": birth_snapshot_table(chart),
        "table_b": domain_rows,
        "table_c": window_rows,
        "table_d": birth_period_rows,
        "top_books_global": [],
        "battle_keys_sample": list(battle_full.keys())[:12],
    }

    # Global top 5 cited rules (lagna + key houses)
    global_rules = []
    for planet, house in [("Jupiter", 1), ("Venus", 7), ("Rahu", 10), ("Sun", 6), ("Moon", 9)]:
        for r in corpus.get_planet_in_house(planet, house, limit=2):
            global_rules.append({
                "placement": f"{planet} H{house}",
                "text": _clip(r.text, 180),
                "books": r.books[:3],
            })
    payload["top_books_global"] = global_rules[:5]

    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload)
    write_csv(payload)
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_CSV}")
    return payload


def write_markdown(data: dict) -> None:
    lines = [
        "# Manoj - Multi-Engine Comparison Report",
        "",
        "**Subject:** Manoj · **DOB** 1996-05-25 20:25 · Coimbatore · `charts/manoj_chart.json`",
        f"**Generated:** {data['generated_at']} · **Runtime root:** `{data['root']}`",
        "",
        "## How to read this (plain English)",
        "",
        "1. **Pure books** = verbatim classical passages from the indexed gemma corpus for planet-in-house (and nakshatra); citations only, no life-event scoring.",
        "2. **Pure match** = **classical consensus %** among those book passages (agreement index, not probability of an event).",
        "3. **Hybrid** = modern category engine bands cross-checked with pure classical scripture within ±180 days; boosted when verified.",
        "4. **Life-event engine** = `event_predictor_v2` production rules (dasha + transit + yoga triggers) with severity windows.",
        "5. **Agreement** = rough label when multiple columns point the same way; sparse charts (like Manoj) may lack `known_events` for ground truth.",
        "",
        "---",
        "",
        "### Table A - Birth snapshot (mechanical, all engines agree)",
        "",
        "| Field | Value | Cause (technical) |",
        "|---|---|---|",
    ]
    for r in data["table_a"]:
        lines.append(f"| {r['field']} | {r['value']} | {r['cause']} |")

    lines += [
        "",
        "### Table B - Engine comparison by life domain",
        "",
        "| Domain | Pure books (citation) | Pure match (consensus) | Hybrid | Life-event engine | Agreement? |",
        "|---|---|---|---|---|---|",
    ]
    for r in data["table_b"]:
        lines.append(
            f"| {r['domain']} | {_clip(r['pure_books'], 120)} | {_clip(r['pure_match'], 80)} | "
            f"{_clip(r['hybrid'], 80)} | {_clip(r['life_event'], 80)} | {r['agreement']} |"
        )

    lines += [
        "",
        "### Table C - Time windows (cause -> effect)",
        "",
        "| Period | Chart cause (dasha) | Pure books says | Pure match | Hybrid | Event engine window | Real-world note |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in data["table_c"]:
        lines.append(
            f"| {r['period']} | {r['chart_cause']} | {_clip(r['pure_books'], 70)} | {r['pure_match']} | "
            f"{_clip(r['hybrid'], 70)} | {_clip(r['life_event'], 90)} | {r['real_world']} |"
        )

    lines += [
        "",
        "### Table D - Birth period May 1996 (natal inference)",
        "",
        "| Factor | Natal placement | Pure books | Pure match | Hybrid | Life-event (1996-98) |",
        "|---|---|---|---|---|---|",
    ]
    for r in data["table_d"]:
        lines.append(
            f"| {r['factor']} | {r['natal']} | {_clip(str(r['pure_books']), 70)} | {r['pure_match']} | "
            f"{_clip(str(r['hybrid']), 50)} | {_clip(str(r['life_event']), 60)} |"
        )

    lines += [
        "",
        "### Top 5 global book citations (corpus)",
        "",
    ]
    for i, r in enumerate(data.get("top_books_global", []), 1):
        lines.append(f"{i}. **{r['placement']}** — {r['text']}  \n   Books: {', '.join(r['books'])}")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(data: dict) -> None:
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["table", "domain", "pure_books", "pure_match", "hybrid", "life_event", "agreement"])
        for r in data["table_b"]:
            w.writerow(["B", r["domain"], r["pure_books"], r["pure_match"], r["hybrid"], r["life_event"], r["agreement"]])
        for r in data["table_c"]:
            w.writerow(["C", r["period"], r["pure_books"], r["pure_match"], r["hybrid"], r["life_event"], r["chart_cause"]])


if __name__ == "__main__":
    run()

