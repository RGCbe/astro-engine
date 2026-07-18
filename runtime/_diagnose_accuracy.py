"""
Accuracy-gap diagnosis: is the engine's weak discrimination (real ≈ random-timing)
a VOLUME problem that conviction-gating can fix, or a LOGIC problem?

Method:
  For a representative subset of charts, run the engine ONCE and cache predictions.
  Then, without re-running the engine, sweep a conviction filter (minimum severity)
  and at each level recompute:
     - prediction density (predictions / lifespan-year)
     - real recall           (engine timing)
     - null recall           (same predictions shuffled to random dates)
     - discrimination = real - null
  If discrimination RISES as we keep only higher-severity predictions, the signal is
  real but drowned by over-prediction -> fix = conviction-gate the production scan.
  If discrimination stays ~0 at every level, the core timing logic lacks signal.

Also dumps where the volume comes from: category and window-width distribution.

Usage:
  python3 _diagnose_accuracy.py                      # default subset, sweep sev 2..5
  python3 _diagnose_accuracy.py --charts modi,rekha  # custom subset
"""
import argparse
import statistics
import sys
import json
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))

import random
import _accuracy_scorer as base
import _honest_scorer as honest

# Representative spread across the observed accuracy range (loose recall):
# Modi 100, Sachin 89, Rekha 71, Mukesh 67, Gandhi 50.
DEFAULT_SUBSET = ["narendra_modi", "sachin_tendulkar", "rekha", "mukesh_ambani", "mahatma_gandhi"]


def _sev(ev):
    return ev.get("max_sev", ev.get("severity", 3)) or 3


def _filter_by_sev(pred_events, min_sev):
    return [ev for ev in pred_events if _sev(ev) >= min_sev]


def diagnose(slug, sev_levels, trials, rng):
    try:
        chart = json.load(open(base.CHARTS_DIR / f"{slug}_chart.json", encoding="utf-8"))
    except Exception as e:
        return None, f"load_fail: {e}"
    known = chart.get("known_events", [])
    if not known:
        return None, "no_known_events"
    birth_yr = chart["birth"]["year"]
    try:
        preds = honest._get_engine_predictions(chart)
    except Exception as e:
        return None, f"engine_fail: {e}"

    # Volume characterization (unfiltered)
    cats = Counter(ev.get("category", "?") for ev in preds)
    widths = []
    for ev in preds:
        s, e = honest._event_span(ev)
        if s and e:
            widths.append((e - s).days)
    sev_dist = Counter(_sev(ev) for ev in preds)

    rows = []
    for msev in sev_levels:
        fp = _filter_by_sev(preds, msev)
        density, dated = honest._prediction_density(fp)
        tol = 180  # loose windows
        real_hits, categorized = honest._score_recall(known, fp, strict=False, tol=tol)
        if categorized == 0:
            continue
        null_hits = []
        for _ in range(trials):
            nh, _c = honest._score_recall(known, honest._make_null_predictions(fp, birth_yr, rng), strict=False, tol=tol)
            null_hits.append(nh)
        real = 100 * real_hits / categorized
        null = statistics.mean(100 * h / categorized for h in null_hits)
        p = sum(1 for h in null_hits if h >= real_hits) / trials
        rows.append({
            "min_sev": msev, "n_pred": len(fp), "density": density,
            "real": round(real, 1), "null": round(null, 1),
            "disc": round(real - null, 1), "p": round(p, 3),
            "hits": real_hits, "cat": categorized,
        })
    return {
        "name": chart.get("name", slug), "slug": slug,
        "total_pred": len(preds),
        "median_window_days": int(statistics.median(widths)) if widths else None,
        "sev_dist": dict(sorted(sev_dist.items())),
        "top_cats": cats.most_common(6),
        "sweep": rows,
    }, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--charts", type=str, default="")
    ap.add_argument("--trials", type=int, default=200)
    ap.add_argument("--sev", type=str, default="2,3,4,5")
    ap.add_argument("--seed", type=int, default=1729)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    slugs = [s.strip() for s in args.charts.split(",") if s.strip()] or DEFAULT_SUBSET
    sev_levels = [int(x) for x in args.sev.split(",")]

    print("\n" + "=" * 88)
    print("  ACCURACY-GAP DIAGNOSIS — does conviction-gating recover discrimination?")
    print(f"  charts: {len(slugs)} | null trials: {args.trials} | severity sweep: {sev_levels}")
    print("=" * 88)

    all_rows_by_sev = {s: {"real": [], "null": [], "cat": [], "hits": [], "dens": []} for s in sev_levels}
    results = []
    for slug in slugs:
        r, err = diagnose(slug, sev_levels, args.trials, rng)
        if err:
            print(f"  [SKIP] {slug}: {err}")
            continue
        results.append(r)
        print(f"\n  ▸ {r['name']}  (total predictions: {r['total_pred']}, "
              f"median window: {r['median_window_days']}d)")
        print(f"     severity distribution: {r['sev_dist']}")
        print(f"     top categories: {', '.join(f'{c}×{n}' for c,n in r['top_cats'])}")
        print(f"     {'min_sev':>7} {'#pred':>6} {'pred/yr':>7} {'real%':>6} {'null%':>6} {'edge':>6} {'p':>6}")
        for row in r["sweep"]:
            sig = "*" if row["p"] < 0.05 else " "
            print(f"     {row['min_sev']:>7} {row['n_pred']:>6} {row['density']:>7} "
                  f"{row['real']:>6} {row['null']:>6} {row['disc']:>+6}{sig} {row['p']:>6}")
            agg = all_rows_by_sev[row["min_sev"]]
            agg["real"].append(row["real"]); agg["null"].append(row["null"])
            agg["cat"].append(row["cat"]); agg["hits"].append(row["hits"]); agg["dens"].append(row["density"])

    print("\n" + "─" * 88)
    print("  POOLED SWEEP (across subset) — the key table")
    print("─" * 88)
    print(f"  {'min_sev':>7} {'pooled_real%':>12} {'pooled_null%':>12} {'discrimination':>15} {'mean pred/yr':>13}")
    for s in sev_levels:
        agg = all_rows_by_sev[s]
        if not agg["cat"]:
            continue
        tot_cat = sum(agg["cat"]); tot_hits = sum(agg["hits"])
        pooled_real = 100 * tot_hits / tot_cat
        pooled_null = sum(n * c for n, c in zip(agg["null"], agg["cat"])) / tot_cat
        mean_dens = statistics.mean(agg["dens"])
        print(f"  {s:>7} {round(pooled_real,1):>12} {round(pooled_null,1):>12} "
              f"{round(pooled_real-pooled_null,1):>+15} {round(mean_dens,1):>13}")
    print("─" * 88)
    print("  If 'discrimination' grows as min_sev rises -> signal is real, drowned by volume")
    print("  (fix = conviction-gate). If it stays flat/near-0 -> core timing logic is weak.")

    out = _ROOT / "ACCURACY_DIAGNOSIS.json"
    json.dump({"charts": results}, open(out, "w", encoding="utf-8"), indent=2, default=str)
    print(f"\n  💾 Saved: {out}\n")


if __name__ == "__main__":
    main()
