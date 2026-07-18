"""
Blessing backtest — symmetric to affliction_backtest.

Per truth directive (audit Tier 2): we validated bad-finder empirically
(1.5-1.9× lift on bad events). Blessings need the same rigor.

For each blessing code, compare GOOD_RATE in charts that have it vs charts
that don't. Good events: AWARD, CAREER_PEAK, MARRIAGE, CHILDREN_BORN,
POLITICAL_OFFICE, FOUND_BUSINESS, CAREER_START, SPIRITUAL_AWAKENING.

Reports per-blessing lift + ratio so we can trust which blessings are
genuinely predictive.
"""
from __future__ import annotations

from collections import Counter
from statistics import mean

GOOD_EVENT_TYPES = {"AWARD", "CAREER_PEAK", "MARRIAGE", "CHILDREN_BORN",
                    "POLITICAL_OFFICE", "FOUND_BUSINESS", "CAREER_START",
                    "SPIRITUAL_AWAKENING"}


def run_blessing_backtest() -> dict:
    from engine.chart import compute_chart
    from engine.known_charts import KNOWN_CHARTS
    from engine.blessings import detect_all

    chart_data = []
    for cm in KNOWN_CHARTS:
        try:
            bd = cm.birthdata
            chart = compute_chart(name=cm.name, date=bd["date"], time=bd["time"],
                                  tz_hours=bd["tz"],
                                  lat=bd.get("lat"), lon=bd.get("lon"))
        except Exception:
            continue
        try:
            blessings = detect_all(chart)
        except Exception:
            continue
        codes = {b.code for b in blessings}
        n_events = len(cm.events)
        n_good = sum(1 for ev in cm.events if ev.event_type in GOOD_EVENT_TYPES)
        good_rate = n_good / n_events if n_events > 0 else 0
        chart_data.append({
            "name": cm.name, "codes": codes,
            "n_events": n_events, "n_good": n_good, "good_rate": good_rate,
        })

    all_codes = set()
    for cd in chart_data:
        all_codes |= cd["codes"]

    overall_good_rate = mean(cd["good_rate"] for cd in chart_data) if chart_data else 0

    by_blessing = {}
    for code in all_codes:
        with_b = [cd for cd in chart_data if code in cd["codes"]]
        without = [cd for cd in chart_data if code not in cd["codes"]]
        if not with_b or not without:
            continue
        rate_with = mean(cd["good_rate"] for cd in with_b)
        rate_without = mean(cd["good_rate"] for cd in without)
        lift = rate_with - rate_without
        by_blessing[code] = {
            "n_charts_with":    len(with_b),
            "n_charts_without": len(without),
            "good_rate_with":    round(rate_with, 4),
            "good_rate_without": round(rate_without, 4),
            "lift":             round(lift, 4),
            "ratio":            round(rate_with / rate_without, 3) if rate_without > 0 else None,
        }
    return {
        "n_charts_total": len(chart_data),
        "overall_good_rate": round(overall_good_rate, 4),
        "by_blessing": by_blessing,
    }


def print_report():
    r = run_blessing_backtest()
    print("=" * 90)
    print(f"BLESSING BACKTEST  (n={r['n_charts_total']} charts; overall good_rate={r['overall_good_rate']})")
    print("=" * 90)
    print(f"{'blessing':40s} {'n_with':>6s} {'rate_w':>7s} {'rate_wo':>8s}  {'lift':>7s}  {'ratio':>6s}")
    rows = []
    for code, b in r["by_blessing"].items():
        rows.append((b["lift"], code, b))
    rows.sort(reverse=True)
    for lift, code, b in rows[:30]:
        marker = "↑" if lift > 0.05 else "↓" if lift < -0.05 else "·"
        ratio_str = f"{b['ratio']}" if b["ratio"] is not None else "n/a"
        print(f"  {code:38s} {b['n_charts_with']:>6d} "
              f"{b['good_rate_with']:>7.3f} {b['good_rate_without']:>8.3f}   "
              f"{marker}{lift:+.3f}  {ratio_str:>6s}")


if __name__ == "__main__":
    print_report()
