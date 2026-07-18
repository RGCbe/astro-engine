"""
Wrong-chart control — the decisive test for the "demographic ghost" trap.

Hypothesis to kill: the fusion signal (+13.5 pts over random timing) is not
chart-specific astrology but life-stage demographics (methods fire at typical
ages for typical events, which beats a uniform-timing null for ANY human).

Design: for each subject A, score A's verified events against
  (a) A's own fused predictions            -> right-chart recall
  (b) every other subject B's fused predictions, AGE-ALIGNED by shifting B's
      windows by (A.birth_year - B.birth_year) years -> wrong-chart recall
If (a) ~ (b): agreement encodes demographics; chart-specific claim collapses.
If (a) >> (b): the signal genuinely lives in the individual chart.

Usage: python3 _wrongchart_control.py
"""
import json
import re
import statistics
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))

import _accuracy_scorer as base
import _honest_scorer as honest
from engine.event_fusion import fuse_events

_DATE = re.compile(r"^(\d{4})(-\d{2}-\d{2})")


def _shift_years(date_str, delta):
    m = _DATE.match(str(date_str))
    if not m:
        return date_str
    tail = m.group(2)
    if tail == "-02-29":
        tail = "-02-28"
    return f"{int(m.group(1)) + delta}{tail}"


def _shift_events(fused, delta_years):
    out = []
    for ev in fused:
        c = dict(ev)
        for key in ("window_start", "window_end", "date"):
            if c.get(key):
                c[key] = _shift_years(c[key], delta_years)
        out.append(c)
    return out


def main():
    slugs = base.CELEBRITIES
    subjects = []
    print("computing fused predictions per chart (engine scan each)...")
    for slug in slugs:
        try:
            chart = json.load(open(base.CHARTS_DIR / f"{slug}_chart.json", encoding="utf-8"))
            known = chart.get("known_events", [])
            if not known:
                continue
            fused = fuse_events(honest._get_engine_predictions(chart))
            subjects.append({
                "slug": slug, "name": chart.get("name", slug),
                "birth_year": chart["birth"]["year"],
                "known": known, "fused": fused,
            })
            print(f"  {slug}: fused={len(fused)}")
        except Exception as e:
            print(f"  [SKIP] {slug}: {e}")

    print("\n" + "=" * 88)
    print("  WRONG-CHART CONTROL — own chart vs age-aligned other charts (loose ±180d)")
    print("=" * 88)

    rows = []
    for a in subjects:
        own_hits, categorized = honest._score_recall(a["known"], a["fused"], strict=False, tol=180)
        if categorized == 0:
            continue
        own = 100 * own_hits / categorized
        wrong_recalls = []
        for b in subjects:
            if b["slug"] == a["slug"]:
                continue
            delta = a["birth_year"] - b["birth_year"]
            shifted = _shift_events(b["fused"], delta)
            wh, _ = honest._score_recall(a["known"], shifted, strict=False, tol=180)
            wrong_recalls.append(100 * wh / categorized)
        wrong_mean = statistics.mean(wrong_recalls)
        # rank of own chart among all charts for predicting A's life (1 = best)
        rank = 1 + sum(1 for w in wrong_recalls if w > own)
        rows.append({
            "name": a["name"], "categorized": categorized, "own_hits": own_hits,
            "own_pct": round(own, 1), "wrong_mean_pct": round(wrong_mean, 1),
            "own_minus_wrong": round(own - wrong_mean, 1),
            "own_rank_of_16": rank,
        })
        print(f"  ▸ {a['name']:<22} own {own:>5.1f}%  wrong-mean {wrong_mean:>5.1f}%  "
              f"edge {own - wrong_mean:>+6.1f}  own-chart rank {rank}/{len(subjects)}")

    tot_cat = sum(r["categorized"] for r in rows)
    pooled_own = 100 * sum(r["own_hits"] for r in rows) / tot_cat
    pooled_wrong = sum(r["wrong_mean_pct"] * r["categorized"] for r in rows) / tot_cat
    better = sum(1 for r in rows if r["own_minus_wrong"] > 0)
    mean_rank = statistics.mean(r["own_rank_of_16"] for r in rows)

    print("\n" + "─" * 88)
    print("  VERDICT")
    print("─" * 88)
    print(f"  Pooled OWN-chart recall     : {round(pooled_own,1)}%")
    print(f"  Pooled WRONG-chart recall   : {round(pooled_wrong,1)}%   <- demographics-only baseline")
    print(f"  CHART-SPECIFIC EDGE         : {round(pooled_own-pooled_wrong,1):+} pts")
    print(f"  Subjects where own > wrong  : {better}/{len(rows)}")
    print(f"  Mean rank of own chart      : {round(mean_rank,1)} of {len(subjects)} (chance = {round((len(subjects)+1)/2,1)})")
    print("─" * 88)
    print("  own ~ wrong  -> the fusion signal is life-stage demographics (trap confirmed)")
    print("  own >> wrong -> the signal is genuinely chart-specific astrology")

    out = _ROOT / "WRONGCHART_CONTROL.json"
    json.dump({"pooled_own_pct": round(pooled_own, 1),
               "pooled_wrong_pct": round(pooled_wrong, 1),
               "chart_specific_edge_pts": round(pooled_own - pooled_wrong, 1),
               "subjects_own_beats_wrong": better, "subjects_total": len(rows),
               "mean_own_rank": round(mean_rank, 2),
               "per_subject": rows}, open(out, "w", encoding="utf-8"), indent=1)
    print(f"\n  💾 Saved: {out}\n")


if __name__ == "__main__":
    main()
