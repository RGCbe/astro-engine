#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug: why marriage-like signals fire for Manoj at age ~12 (2008 band)."""
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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(RUNTIME))

from granular_dasha import build_full_timeline, lookup
from transit_engine import detect_triggers
from comprehensive_yogas import detect_all_classical_yogas as detect_all_yogas
from event_predictor_v2 import (
    ALL_PATTERNS_V2,
    scan_year_v2,
    collapse_consecutive,
    event_marriage,
    event_marriage_arranged,
    event_marriage_love,
    event_engagement,
)
from engine.event_age_policy import age_at, classify_age_fit

CHART_PATH = ROOT / "charts" / "manoj_chart.json"
MARRIAGE_CATS = {
    "marriage", "marriage_arranged", "marriage_love", "engagement",
    "relationship_phase", "saham_kalatra", "romance", "first_love",
    "relationship_break",
}
MARRIAGE_FNS = {
    "event_marriage": event_marriage,
    "event_marriage_arranged": event_marriage_arranged,
    "event_marriage_love": event_marriage_love,
    "event_engagement": event_engagement,
}

SAMPLE_DATES = [
    dt.datetime(2008, 6, 3),
    dt.datetime(2008, 6, 13),
    dt.datetime(2008, 7, 1),
    dt.datetime(2008, 9, 1),
    dt.datetime(2009, 1, 1),
    dt.datetime(2009, 6, 1),
    dt.datetime(2010, 1, 1),
    dt.datetime(2011, 7, 2),
]


def dasha_str(ds: dict) -> str:
    md = ds.get(1, {}).get("md", "?")
    ad = ds.get(2, {}).get("ad", "?")
    pd = ds.get(3, {}).get("pd", "?")
    return f"{md}/{ad}/{pd}"


def print_sample_dates(chart: dict, timeline) -> None:
    print("=" * 72)
    print("SAMPLE DATES - dasha + marriage-related pattern hits")
    print("=" * 72)
    yogas = detect_all_yogas(chart)
    for when in SAMPLE_DATES:
        age = age_at(chart, when)
        ds = lookup(timeline, when)
        tr = detect_triggers(chart, when, orb=2.5)
        print(f"\n--- {when.date()}  age={age:.2f}  MD/AD/PD={dasha_str(ds)} ---")
        for fn_name, fn in MARRIAGE_FNS.items():
            ev = fn(chart, ds, tr, yogas, age)
            if ev:
                print(f"  [{fn_name}] sev={ev['severity']} cat={ev['category']}")
                for w in ev.get("why", []):
                    print(f"      why: {w}")
            else:
                print(f"  [{fn_name}] None (age gate or threshold)")
        hits = []
        for fn in ALL_PATTERNS_V2:
            ev = fn(chart, ds, tr, yogas, age)
            if ev and ev.get("category") in MARRIAGE_CATS:
                hits.append((fn.__name__, ev))
        if hits:
            print("  ALL_PATTERNS_V2 marriage-domain hits:")
            for fn_name, ev in hits:
                print(f"    {fn_name}: sev={ev['severity']} cat={ev['category']} score~{ev.get('severity')}")
                for w in ev.get("why", []):
                    print(f"      why: {w}")
        else:
            print("  ALL_PATTERNS_V2: no marriage-domain category hits")


def monthly_2008_2009(chart: dict, timeline) -> None:
    print("\n" + "=" * 72)
    print("MONTHLY 2008-2009 - any marriage-domain category (min sev 1)")
    print("=" * 72)
    yogas = detect_all_yogas(chart)
    d = dt.datetime(2008, 1, 1)
    end = dt.datetime(2009, 12, 31)
    while d <= end:
        age = age_at(chart, d)
        ds = lookup(timeline, d)
        tr = detect_triggers(chart, d, orb=2.5)
        for fn in ALL_PATTERNS_V2:
            ev = fn(chart, ds, tr, yogas, age)
            if not ev or ev.get("category") not in MARRIAGE_CATS:
                continue
            if ev["severity"] < 1:
                continue
            fit = classify_age_fit(age, ev["category"], ev["severity"], why_count=len(ev.get("why", [])))
            print(
                f"{d.date()} age={age:.1f} {fn.__name__} "
                f"cat={ev['category']} sev={ev['severity']} age_fit={fit}"
            )
            for w in ev.get("why", []):
                print(f"    {w}")
        # advance ~1 month
        if d.month == 12:
            d = dt.datetime(d.year + 1, 1, 1)
        else:
            d = dt.datetime(d.year, d.month + 1, 1)


def scan_years(chart: dict) -> None:
    print("\n" + "=" * 72)
    print("scan_year_v2 2008-2011 (sample_days=10, min_severity=1)")
    print("=" * 72)
    all_raw = []
    for year in range(2008, 2012):
        raw = scan_year_v2(chart, year, sample_days=10, min_severity=1)
        for k, v in raw.items():
            cat = v.get("category", "")
            if cat in MARRIAGE_CATS or "marriage" in k.lower() or "Marriage" in k:
                v["year"] = year
                all_raw.append(v)
                print(f"  {year}: {k[:60]}")
                print(f"    cat={cat} sev={v.get('max_sev')} first={v['first'].date()} last={v['last'].date()}")
                for w in v.get("max_why", []):
                    print(f"    why: {w}")
    bands = collapse_consecutive(all_raw)
    print("\nCollapsed marriage-domain bands:")
    for b in bands:
        ws, we = b["window_start"], b["window_end"]
        a = age_at(chart, ws)
        fit = classify_age_fit(a, b.get("category", ""), b.get("max_sev", 0), why_count=len(b.get("max_why", [])))
        print(f"  {ws.date()} -> {we.date()}  age={a:.1f}  cat={b.get('category')}  sev={b.get('max_sev')}  fit={fit}")
        print(f"    event: {b.get('event', '')[:70]}")


def main() -> None:
    chart = json.loads(CHART_PATH.read_text(encoding="utf-8"))
    b = chart["birth"]
    print(f"Chart: Manoj  birth={b['year']}-{b['month']:02d}-{b['day']:02d}  lagna={chart['lagna']}")
    print(f"7L from lagna_idx={chart['lagna_idx']}: Mercury (Venus in H7 natal)")
    timeline = build_full_timeline(chart, levels=3)

    print_sample_dates(chart, timeline)
    monthly_2008_2009(chart, timeline)
    scan_years(chart)


if __name__ == "__main__":
    main()
