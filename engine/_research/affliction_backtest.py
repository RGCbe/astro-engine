"""
Backtest the affliction detector — do detected afflictions actually correlate
with documented bad life events on the 61-chart corpus?

For each chart, we already detect afflictions at birth (static features —
they do not change over time, since they're chart structure). The question
is whether charts WITH a given affliction have more documented bad events
than charts WITHOUT.

Bad events: HEALTH_CRISIS, DEATH, MAJOR_LOSS, DIVORCE, IMPRISONMENT,
            EXILE, SCANDAL.

Per chart, count documented bad events / total events. Compare distribution
between charts that have a given affliction vs those that don't. Report
mean lift + significance proxy (binomial-style).
"""
from __future__ import annotations

from collections import defaultdict
from statistics import mean

BAD_EVENT_TYPES = {"HEALTH_CRISIS", "DEATH", "MAJOR_LOSS", "DIVORCE",
                   "IMPRISONMENT", "EXILE", "SCANDAL"}


def run_affliction_backtest() -> dict:
    """For each affliction code, compare the bad-event rate in charts that
    have it vs charts that don't."""
    from engine.chart import compute_chart
    from engine.known_charts import KNOWN_CHARTS
    from engine.afflictions import detect_all

    # Build per-chart: (set_of_affliction_codes, bad_rate)
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
            afflictions = detect_all(chart)
        except Exception:
            continue
        codes = {a.code for a in afflictions}
        n_events = len(cm.events)
        n_bad = sum(1 for ev in cm.events if ev.event_type in BAD_EVENT_TYPES)
        bad_rate = n_bad / n_events if n_events > 0 else 0
        chart_data.append({
            "name": cm.name, "codes": codes,
            "n_events": n_events, "n_bad": n_bad, "bad_rate": bad_rate,
        })

    # Aggregate by affliction code
    all_codes = set()
    for cd in chart_data:
        all_codes |= cd["codes"]

    overall_bad_rate = mean(cd["bad_rate"] for cd in chart_data) if chart_data else 0

    by_affliction = {}
    for code in all_codes:
        with_aff = [cd for cd in chart_data if code in cd["codes"]]
        without = [cd for cd in chart_data if code not in cd["codes"]]
        if not with_aff or not without:
            continue
        rate_with = mean(cd["bad_rate"] for cd in with_aff)
        rate_without = mean(cd["bad_rate"] for cd in without)
        lift = rate_with - rate_without
        by_affliction[code] = {
            "n_charts_with":    len(with_aff),
            "n_charts_without": len(without),
            "bad_rate_with":    round(rate_with, 4),
            "bad_rate_without": round(rate_without, 4),
            "lift":             round(lift, 4),
            "ratio":            round(rate_with / rate_without, 3) if rate_without > 0 else None,
        }
    return {
        "n_charts_total": len(chart_data),
        "overall_bad_rate": round(overall_bad_rate, 4),
        "by_affliction": by_affliction,
    }


def print_report():
    r = run_affliction_backtest()
    print("=" * 90)
    print(f"AFFLICTION BACKTEST  (n={r['n_charts_total']} charts; overall bad_rate={r['overall_bad_rate']})")
    print("=" * 90)
    print(f"{'affliction':40s} {'n_with':>6s} {'rate_w':>7s} {'rate_wo':>8s}  {'lift':>7s}  {'ratio':>6s}")
    rows = []
    for code, b in r["by_affliction"].items():
        rows.append((b["lift"], code, b))
    rows.sort(reverse=True)
    for lift, code, b in rows[:30]:
        marker = "^" if lift > 0.05 else "v" if lift < -0.05 else "."
        ratio_str = f"{b['ratio']}" if b["ratio"] is not None else "n/a"
        print(f"  {code:38s} {b['n_charts_with']:>6d} "
              f"{b['bad_rate_with']:>7.3f} {b['bad_rate_without']:>8.3f}   "
              f"{marker}{lift:+.3f}  {ratio_str:>6s}")


if __name__ == "__main__":
    print_report()
