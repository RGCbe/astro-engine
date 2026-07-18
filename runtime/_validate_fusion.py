"""
Fusion-layer validation — does convergence gating produce real timing skill?

For each chart: run the engine once, fuse with engine.event_fusion, then score
the FUSED set exactly like _honest_scorer scores the raw set:
    real recall  vs  null recall (fused windows shuffled to random dates)
and compare against the raw-baseline discrimination (+3.1 pts loose, 0/16 sig).

A fused prediction set is tiny (~1/yr, ~40d windows), so recall WILL drop.
The success criterion is NOT recall — it is discrimination and significance:
    PASS  = pooled real - null clearly positive with several charts p < 0.05
    FAIL  = discrimination still ~0  -> convergence of current methods carries
            no timing signal either, and the honest claim is descriptive-only.

Usage:
  python3 _validate_fusion.py [--trials 500] [--charts a,b,c]
"""
import argparse
import random
import statistics
import sys
import json
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))

import _accuracy_scorer as base
import _honest_scorer as honest
from engine.event_fusion import fuse_events, GATING_FAMILIES, ALL_FAMILIES


def validate_chart(slug, trials, rng, gating=GATING_FAMILIES):
    try:
        chart = json.load(open(base.CHARTS_DIR / f"{slug}_chart.json", encoding="utf-8"))
    except Exception as e:
        return None, f"load_fail: {e}"
    known = chart.get("known_events", [])
    if not known:
        return None, "no_known_events"
    birth_yr = chart["birth"]["year"]
    try:
        raw = honest._get_engine_predictions(chart)
    except Exception as e:
        return None, f"engine_fail: {e}"

    fused = fuse_events(raw, gating_families=gating)
    density, _ = honest._prediction_density(fused)

    tol = 180
    real_hits, categorized = honest._score_recall(known, fused, strict=False, tol=tol)
    if categorized == 0:
        return None, "no_categorized_events"

    null_hits = []
    for _ in range(trials):
        nulls = honest._make_null_predictions(fused, birth_yr, rng)
        nh, _c = honest._score_recall(known, nulls, strict=False, tol=tol)
        null_hits.append(nh)

    real = 100 * real_hits / categorized
    null_mean = statistics.mean(100 * h / categorized for h in null_hits)
    p = sum(1 for h in null_hits if h >= real_hits) / trials

    return {
        "name": chart.get("name", slug), "slug": slug,
        "raw_pred": len(raw), "fused_pred": len(fused),
        "fused_per_year": density,
        "categorized_events": categorized,
        "real_hits": real_hits,
        "real_recall_pct": round(real, 1),
        "null_recall_pct": round(null_mean, 1),
        "discrimination_pts": round(real - null_mean, 1),
        "p_value": round(p, 3),
    }, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=500)
    ap.add_argument("--charts", type=str, default="")
    ap.add_argument("--seed", type=int, default=1729)
    ap.add_argument("--include-esoteric", action="store_true",
                    help="let western/chinese/mayan/numerology/palmistry families satisfy the gate")
    args = ap.parse_args()
    rng = random.Random(args.seed)
    slugs = [s.strip() for s in args.charts.split(",") if s.strip()] or base.CELEBRITIES
    gating = ALL_FAMILIES if args.include_esoteric else GATING_FAMILIES

    print("\n" + "=" * 92)
    print("  FUSION VALIDATION — convergence-gated events vs random-timing null (loose ±180d)")
    print(f"  gate: {'ALL families incl. esoteric' if args.include_esoteric else 'classical families only'}")
    print(f"  charts: {len(slugs)} | null trials: {args.trials} | seed: {args.seed}")
    print("  raw baseline for reference: real 78.4% vs null 75.3% -> +3.1 pts, 0/16 significant")
    print("=" * 92)

    results = []
    for slug in slugs:
        r, err = validate_chart(slug, args.trials, rng, gating=gating)
        if err:
            print(f"  [SKIP] {slug}: {err}")
            continue
        results.append(r)
        sig = "***" if r["p_value"] < 0.01 else ("**" if r["p_value"] < 0.05 else "   ")
        print(f"  ▸ {r['name']:<22} fused {r['fused_pred']:>4} ({r['fused_per_year']:>4}/yr)  "
              f"real {r['real_recall_pct']:>5.1f}%  null {r['null_recall_pct']:>5.1f}%  "
              f"edge {r['discrimination_pts']:>+6.1f}  p={r['p_value']:<6}{sig}")

    if not results:
        print("  no results"); return

    tot_cat = sum(r["categorized_events"] for r in results)
    tot_hits = sum(r["real_hits"] for r in results)
    pooled_real = 100 * tot_hits / tot_cat
    pooled_null = sum(r["null_recall_pct"] * r["categorized_events"] for r in results) / tot_cat
    signif = sum(1 for r in results if r["p_value"] < 0.05)
    mean_density = round(statistics.mean(r["fused_per_year"] for r in results), 2)

    print("\n" + "─" * 92)
    print("  POOLED FUSION RESULT")
    print("─" * 92)
    print(f"  Verified events             : {tot_cat}")
    print(f"  Fused real recall           : {round(pooled_real,1)}%  ({tot_hits}/{tot_cat})")
    print(f"  Fused null recall           : {round(pooled_null,1)}%")
    print(f"  DISCRIMINATION              : {round(pooled_real-pooled_null,1):+} pts   (raw baseline: +3.1)")
    print(f"  Charts significant (p<0.05) : {signif}/{len(results)}   (raw baseline: 0/16)")
    print(f"  Mean fused density          : {mean_density}/yr        (raw: ~35/yr)")
    print("─" * 92)

    out = _ROOT / ("FUSION_VALIDATION_ESOTERIC.json" if args.include_esoteric else "FUSION_VALIDATION.json")
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "null_trials": args.trials, "seed": args.seed,
        "pooled_real_recall_pct": round(pooled_real, 1),
        "pooled_null_recall_pct": round(pooled_null, 1),
        "discrimination_pts": round(pooled_real - pooled_null, 1),
        "charts_significant_p05": signif, "charts_total": len(results),
        "mean_fused_density_per_year": mean_density,
        "per_celebrity": results,
    }, open(out, "w", encoding="utf-8"), indent=2, default=str)
    print(f"\n  💾 Saved: {out}\n")


if __name__ == "__main__":
    main()
