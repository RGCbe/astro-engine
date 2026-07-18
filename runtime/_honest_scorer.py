"""
Honest Accuracy Scorer — adds the controls the plain recall metric is missing.

The existing _accuracy_scorer.py reports RECALL only: of the known life events we
can categorize, how many did the engine predict within a date window. It never
penalizes volume — the engine emits thousands of predictions per chart, so a high
recall can be a shotgun artifact rather than real skill.

This script answers "is the timing real?" with a permutation null model:

  1. Run the engine ONCE per chart to get its real predictions (category, window,
     severity) — identical to the production scan.
  2. Score real recall with the same check_match used by _accuracy_scorer.
  3. NULL MODEL: keep every predicted event's category, severity and window WIDTH,
     but move each window to a random start inside the lifespan. Re-score. Repeat
     N times. This preserves the engine's prediction volume and category mix and
     only destroys its *timing*.
  4. discrimination = real_recall - mean(null_recall)   (the engine's real edge)
     p_value = fraction of null trials whose recall >= real recall
  5. Report prediction DENSITY (events/year) so volume is visible, and a
     severity-bucketed hit rate as a rough calibration check.

If real_recall is close to null_recall (high p), the headline accuracy is mostly
an artifact of how many predictions the engine fires. If real >> null (low p),
the timing carries genuine signal.

Usage:
  python3 _honest_scorer.py                 # loose windows, 200 null trials
  python3 _honest_scorer.py --strict        # strict windows + valence
  python3 _honest_scorer.py --trials 500    # more null trials
  python3 _honest_scorer.py --charts sachin_tendulkar,narendra_modi   # subset
"""
import argparse
import random
import statistics
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")
_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))

from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
import _accuracy_scorer as base

LIFESPAN_YEARS = 85
_DAY = timedelta(days=1)


def _get_engine_predictions(chart):
    """Run the production scan once; return the same pred_events list the base
    scorer uses (bands + ranked union)."""
    birth_yr = chart["birth"]["year"]
    raw = scan_lifetime_v2(chart, birth_yr, birth_yr + LIFESPAN_YEARS, min_severity=2)
    bands = collapse_consecutive(raw) if raw else []
    ranked = rank_and_consume(bands) if bands else []
    return bands + ranked


def _event_span(ev):
    """Return (start_date, end_date) for a predicted event, or (peak, peak)."""
    ws = base.parse_date(str(ev.get("window_start", ""))[:10])
    we = base.parse_date(str(ev.get("window_end", ""))[:10])
    if ws and we:
        return ws, we
    d = base.parse_date(str(ev.get("date") or ev.get("peak_date") or "")[:10])
    if d:
        return d, d
    return None, None


def _score_recall(known_events, pred_events, strict, tol):
    """Recall = categorized known events matched by at least one prediction."""
    hits = 0
    categorized = 0
    for ke in known_events:
        cats = base.categorize_event(ke["event"])
        if "uncategorized" in cats:
            continue
        categorized += 1
        matched, _, _ = base.check_match(ke, pred_events, tolerance_days=tol, strict=strict)
        if matched:
            hits += 1
    return hits, categorized


def _make_null_predictions(pred_events, birth_yr, rng):
    """Same categories/severities/window-widths, random placement in the lifespan."""
    span_start = datetime(birth_yr, 1, 1)
    span_end = datetime(birth_yr + LIFESPAN_YEARS, 12, 31)
    total_days = (span_end - span_start).days
    shuffled = []
    for ev in pred_events:
        start, end = _event_span(ev)
        if not start:
            shuffled.append(ev)  # undateable — leave as-is (won't match anyway)
            continue
        width = max(0, (end - start).days)
        new_start_offset = rng.randint(0, max(0, total_days - width))
        new_start = span_start + new_start_offset * _DAY
        new_end = new_start + width * _DAY
        clone = dict(ev)
        clone["window_start"] = new_start.strftime("%Y-%m-%d")
        clone["window_end"] = new_end.strftime("%Y-%m-%d")
        clone["date"] = new_start.strftime("%Y-%m-%d")
        clone.pop("peak_date", None)
        shuffled.append(clone)
    return shuffled


def _prediction_density(pred_events):
    """Distinct dateable predictions per lifespan-year (volume signal)."""
    dated = sum(1 for ev in pred_events if _event_span(ev)[0])
    return round(dated / LIFESPAN_YEARS, 1), dated


def score_celebrity_honest(slug, *, strict, trials, rng):
    try:
        chart = json.load(open(base.CHARTS_DIR / f"{slug}_chart.json", encoding="utf-8"))
    except Exception as e:
        return None, f"load_fail: {e}"
    known_events = chart.get("known_events", [])
    if not known_events:
        return None, "no_known_events"

    birth_yr = chart["birth"]["year"]
    try:
        pred_events = _get_engine_predictions(chart)
    except Exception as e:
        return None, f"engine_fail: {e}"

    tol = 90 if strict else 180
    real_hits, categorized = _score_recall(known_events, pred_events, strict, tol)
    if categorized == 0:
        return None, "no_categorized_events"

    # Null model: N random-placement trials.
    null_hits_list = []
    for _ in range(trials):
        null_preds = _make_null_predictions(pred_events, birth_yr, rng)
        nh, _ = _score_recall(known_events, null_preds, strict, tol)
        null_hits_list.append(nh)

    real_recall = 100 * real_hits / categorized
    null_recalls = [100 * h / categorized for h in null_hits_list]
    null_mean = statistics.mean(null_recalls)
    null_p95 = sorted(null_recalls)[min(len(null_recalls) - 1, int(0.95 * len(null_recalls)))]
    # p-value: how often chance matches or beats the engine
    p_value = sum(1 for h in null_hits_list if h >= real_hits) / trials

    density, dated_preds = _prediction_density(pred_events)

    return {
        "name": chart.get("name", slug),
        "slug": slug,
        "categorized_events": categorized,
        "real_hits": real_hits,
        "real_recall_pct": round(real_recall, 1),
        "null_recall_mean_pct": round(null_mean, 1),
        "null_recall_p95_pct": round(null_p95, 1),
        "discrimination_pts": round(real_recall - null_mean, 1),
        "p_value": round(p_value, 3),
        "pred_count": len(pred_events),
        "dated_pred_count": dated_preds,
        "pred_density_per_year": density,
    }, None


def main():
    ap = argparse.ArgumentParser(description="Honest accuracy: engine recall vs random-timing null model")
    ap.add_argument("--strict", action="store_true", help="strict windows + valence")
    ap.add_argument("--trials", type=int, default=200, help="null-model permutation trials (default 200)")
    ap.add_argument("--charts", type=str, default="", help="comma-separated slugs; default = full set")
    ap.add_argument("--seed", type=int, default=1729, help="RNG seed for reproducibility")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    slugs = [s.strip() for s in args.charts.split(",") if s.strip()] or base.CELEBRITIES

    mode = "STRICT (±45-90d + valence)" if args.strict else "LOOSE (±180d windows)"
    print("\n" + "=" * 84)
    print("  ATRO HONEST SCORER — engine recall vs random-timing null model")
    print(f"  mode: {mode} | null trials: {args.trials} | seed: {args.seed}")
    print("=" * 84)

    results = []
    for slug in slugs:
        r, err = score_celebrity_honest(slug, strict=args.strict, trials=args.trials, rng=rng)
        if err:
            print(f"  [SKIP] {slug}: {err}")
            continue
        results.append(r)
        sig = "***" if r["p_value"] < 0.01 else ("**" if r["p_value"] < 0.05 else "   ")
        print(f"  ▸ {r['name']:<24} real {r['real_recall_pct']:>5.1f}%  "
              f"null {r['null_recall_mean_pct']:>5.1f}%  "
              f"edge {r['discrimination_pts']:>+5.1f}pts  "
              f"p={r['p_value']:<5} {sig}  "
              f"| {r['pred_density_per_year']:>4}/yr")

    if not results:
        print("\n  No scorable charts.")
        return

    tot_cat = sum(r["categorized_events"] for r in results)
    tot_real = sum(r["real_hits"] for r in results)
    # pooled null: weight each celeb's null mean by its categorized count
    pooled_null = sum(r["null_recall_mean_pct"] * r["categorized_events"] for r in results) / tot_cat
    pooled_real = 100 * tot_real / tot_cat
    mean_density = round(statistics.mean(r["pred_density_per_year"] for r in results), 1)
    signif = sum(1 for r in results if r["p_value"] < 0.05)

    print("\n" + "─" * 84)
    print("  POOLED RESULT")
    print("─" * 84)
    print(f"  Verified categorized events : {tot_cat}")
    print(f"  Engine real recall          : {round(pooled_real,1)}%   ({tot_real}/{tot_cat})")
    print(f"  Random-timing null recall   : {round(pooled_null,1)}%   <- chance at this prediction volume")
    print(f"  DISCRIMINATION (real-null)  : {round(pooled_real-pooled_null,1)} pts   <- the engine's real edge")
    print(f"  Charts significant (p<0.05) : {signif}/{len(results)}")
    print(f"  Mean prediction density     : {mean_density} predictions/lifespan-year")
    print("─" * 84)
    print("  Reading: if real ≈ null (few significant charts), the headline recall is")
    print("  mostly a volume artifact. If real >> null with many p<0.05, timing is real.")

    out = _ROOT / ("HONEST_ACCURACY_STRICT.json" if args.strict else "HONEST_ACCURACY.json")
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "mode": "strict" if args.strict else "loose",
        "null_trials": args.trials,
        "seed": args.seed,
        "pooled_real_recall_pct": round(pooled_real, 1),
        "pooled_null_recall_pct": round(pooled_null, 1),
        "discrimination_pts": round(pooled_real - pooled_null, 1),
        "charts_significant_p05": signif,
        "charts_total": len(results),
        "mean_pred_density_per_year": mean_density,
        "per_celebrity": results,
    }, open(out, "w", encoding="utf-8"), indent=2, default=str)
    print(f"\n  💾 Saved: {out}\n")


if __name__ == "__main__":
    main()
