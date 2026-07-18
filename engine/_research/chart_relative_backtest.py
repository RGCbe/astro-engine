"""
Chart-relative backtest — does per-chart scoring beat universal karaka tables?

Runs the same negative-sample backtest as engine.negative_backtest but uses
engine.chart_relative.score_event_relative instead of EVENT_PATTERNS, then
compares the resulting LRs side-by-side with the universal-karaka LRs.
"""
from __future__ import annotations

import datetime as dt
from collections import Counter
from dataclasses import dataclass

from engine.chart import compute_chart
from engine.chart_relative import score_event_relative
from engine.dasha import current_dasha, vimshottari
from engine.known_charts import KNOWN_CHARTS
from engine.negative_backtest import (
    _moon_lon, _birth_dt, _sample_negative_years,
)
from engine.backtest import EVENT_PATTERNS


def _get_chart_obj(chart):
    bd = chart.birthdata
    return compute_chart(name=chart.name, date=bd["date"], time=bd["time"],
                         tz_hours=bd["tz"], lat=bd.get("lat"), lon=bd.get("lon"))


def _md_ad_at(chart, year, month=6, day=15):
    moon = _moon_lon(chart.birthdata)
    periods = vimshottari(moon, _birth_dt(chart.birthdata))
    md, ad = current_dasha(periods, dt.datetime(year, month, day))
    if md is None:
        return None, None
    return md.lord, ad.lord if ad else None


def run_chart_relative_backtest(n_negative_per_chart: int = 5) -> dict:
    """For each event type, count tier matches under chart-relative scoring,
    on positive vs negative years, and compute LR per tier."""
    pos_pri = Counter(); pos_sec = Counter(); pos_n = Counter()
    neg_pri = Counter(); neg_sec = Counter(); neg_n = Counter()

    for chart_meta in KNOWN_CHARTS:
        try:
            chart_obj = _get_chart_obj(chart_meta)
        except Exception:
            continue

        # Positive samples
        for ev in chart_meta.events:
            if ev.event_type not in EVENT_PATTERNS:
                continue
            mo = ev.month if ev.month else 6
            dy = ev.day if ev.day else 15
            md, ad = _md_ad_at(chart_meta, ev.year, mo, dy)
            if md is None:
                continue
            r = score_event_relative(chart_obj, ev.event_type, md, ad)
            pos_n[ev.event_type] += 1
            if r["best_tier"] == "primary":
                pos_pri[ev.event_type] += 1
            elif r["best_tier"] == "secondary":
                pos_sec[ev.event_type] += 1

        # Negative samples
        for evt in EVENT_PATTERNS.keys():
            negs = _sample_negative_years(chart_meta, evt, n_negative_per_chart)
            for y in negs:
                md, ad = _md_ad_at(chart_meta, y)
                if md is None:
                    continue
                r = score_event_relative(chart_obj, evt, md, ad)
                neg_n[evt] += 1
                if r["best_tier"] == "primary":
                    neg_pri[evt] += 1
                elif r["best_tier"] == "secondary":
                    neg_sec[evt] += 1

    # Compute LRs
    out = {}
    for evt in EVENT_PATTERNS.keys():
        if pos_n[evt] == 0 or neg_n[evt] == 0:
            continue
        p_pri_pos = pos_pri[evt] / pos_n[evt]
        p_pri_neg = neg_pri[evt] / neg_n[evt]
        p_sec_pos = pos_sec[evt] / pos_n[evt]
        p_sec_neg = neg_sec[evt] / neg_n[evt]
        out[evt] = {
            "n_positive": pos_n[evt],
            "n_negative": neg_n[evt],
            "P_primary_given_event":      round(p_pri_pos, 4),
            "P_primary_given_no_event":   round(p_pri_neg, 4),
            "P_secondary_given_event":    round(p_sec_pos, 4),
            "P_secondary_given_no_event": round(p_sec_neg, 4),
            "LR_primary":   round(p_pri_pos / p_pri_neg, 3) if p_pri_neg > 0 else None,
            "LR_secondary": round(p_sec_pos / p_sec_neg, 3) if p_sec_neg > 0 else None,
        }
    return {"by_event_type": out}


def compare_with_universal() -> None:
    """Side-by-side LR comparison: universal karaka vs chart-relative."""
    from engine.negative_backtest import run_negative_backtest

    relative = run_chart_relative_backtest()
    universal = run_negative_backtest()
    print("=" * 95)
    print("CHART-RELATIVE vs UNIVERSAL-KARAKA likelihood ratios (primary tier)")
    print("=" * 95)
    print(f"{'event':22s} {'n+':>3s} {'n-':>3s}  "
          f"{'LR_relative':>11s}  {'LR_universal':>12s}  {'lift':>6s}")
    rows = []
    for evt, b in relative["by_event_type"].items():
        u = universal["by_event_type"].get(evt, {})
        lr_rel = b["LR_primary"]
        lr_uni = u.get("LR_primary")
        if lr_rel is None or lr_uni is None:
            continue
        lift = round(lr_rel - lr_uni, 3)
        rows.append((lift, evt, b["n_positive"], b["n_negative"], lr_rel, lr_uni))
    rows.sort(reverse=True)
    for lift, evt, n_pos, n_neg, lr_rel, lr_uni in rows:
        marker = "↑" if lift > 0.1 else ("↓" if lift < -0.1 else "·")
        print(f"  {evt:20s} {n_pos:3d} {n_neg:3d}   "
              f"{lr_rel:>10.3f}  {lr_uni:>12.3f}   {marker}{lift:+.3f}")
    avg_rel = sum(b["LR_primary"] for b in relative["by_event_type"].values()
                  if b["LR_primary"]) / len([b for b in relative["by_event_type"].values()
                                              if b["LR_primary"]])
    avg_uni = sum(u["LR_primary"] for u in universal["by_event_type"].values()
                  if u["LR_primary"]) / len([u for u in universal["by_event_type"].values()
                                              if u["LR_primary"]])
    print()
    print(f"Mean LR_primary  relative: {avg_rel:.3f}")
    print(f"Mean LR_primary  universal: {avg_uni:.3f}")
    print(f"Lift: {avg_rel - avg_uni:+.3f}")


if __name__ == "__main__":
    compare_with_universal()
