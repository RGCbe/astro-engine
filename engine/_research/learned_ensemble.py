"""
Learned ensemble weights — replace naive Bayes (independent product) with
logistic-regression-fit weights per signal × event type.

Per audit Tier 2: signals (universal-karaka, chart-relative, transit) are
correlated since they all derive from the same chart. Naive product
double-counts shared variance. This module fits per-event weights on the
299-event corpus to correct that.

Model:
    log-odds(event) = β₀ + β₁·log(LR_universal) + β₂·log(LR_chart_relative) + β₃·log(LR_transit)

If signals were independent, β₁=β₂=β₃=1. In practice, fitted β's < 1
indicate the signal shares variance with another. The model produces a
calibrated combined probability that is honest about correlation.

Implementation: pure-Python logistic regression via SGD (no sklearn dep).
"""
from __future__ import annotations

import datetime as dt
import json
import math
from collections import Counter
from pathlib import Path

CACHE = Path("/opt/astro/engine/data/ensemble_weights.json")
if not Path("/opt/astro").exists():
    CACHE = Path(__file__).resolve().parents[1] / "data" / "ensemble_weights.json"


def _logistic(z: float) -> float:
    if z >= 0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    ez = math.exp(z)
    return ez / (1.0 + ez)


def _fit_logistic(features: list[list[float]], labels: list[int],
                   n_iter: int = 1000, lr: float = 0.05) -> list[float]:
    """Plain SGD logistic regression. Returns weight vector w including bias.
    features rows are [x1, x2, x3]; we prepend 1.0 for bias."""
    if not features:
        return [0.0, 0.0, 0.0, 0.0]
    n_feat = len(features[0]) + 1   # +1 for bias
    w = [0.0] * n_feat
    for it in range(n_iter):
        for x_no_bias, y in zip(features, labels):
            x = [1.0] + list(x_no_bias)
            z = sum(wi * xi for wi, xi in zip(w, x))
            p = _logistic(z)
            err = y - p
            for j in range(n_feat):
                w[j] += lr * err * x[j]
    return w


def _gather_signals_and_labels(n_neg_per_chart: int = 5) -> dict:
    """For each event type, collect (LR_universal, LR_chart_rel, LR_transit, label)
    rows from positive (label=1) events and negative (label=0) sampled non-event years."""
    from engine.chart import compute_chart
    from engine.dasha import current_dasha, vimshottari
    from engine.known_charts import KNOWN_CHARTS
    from engine.backtest import EVENT_PATTERNS, _classify
    from engine.calibration import event_priors
    from engine.chart_relative import score_event_relative
    from engine.transit_conditioned import _transit_factors_at, _resolve_predictors
    from engine._research.transit_learn import load_learned
    from engine.negative_backtest import (
        _moon_lon, _birth_dt, _sample_negative_years,
    )

    learned_t = load_learned()
    universal_priors = event_priors()

    by_event: dict[str, dict] = {evt: {"X": [], "y": []} for evt in EVENT_PATTERNS}

    for cm in KNOWN_CHARTS:
        try:
            bd = cm.birthdata
            chart = compute_chart(name=cm.name, date=bd["date"], time=bd["time"],
                                   tz_hours=bd["tz"],
                                   lat=bd.get("lat"), lon=bd.get("lon"))
        except Exception:
            continue
        moon = _moon_lon(cm.birthdata)
        periods = vimshottari(moon, _birth_dt(cm.birthdata))
        natal_moon = chart.positions["Moon"]
        natal_lagna = chart.lagna_lon
        natal_sat = chart.positions["Saturn"]
        natal_jup = chart.positions["Jupiter"]
        seventh = (int(natal_lagna // 30) + 6) % 12

        def signals_at(moment, evt):
            active = current_dasha(chart, moment)
            md = active.get("md")
            ad = active.get("ad")
            if md is None:
                return None
            md_lord = md.get("md") or md.get("lord")
            ad_lord = ad.get("ad") or ad.get("lord") if ad else None
            pattern = EVENT_PATTERNS[evt]
            md_t = _classify(md_lord, pattern["primary"], pattern["secondary"])
            ad_t = _classify(ad_lord, pattern["primary"], pattern["secondary"])
            best_u = "primary" if "primary" in (md_t, ad_t) else (
                     "secondary" if "secondary" in (md_t, ad_t) else "miss")
            up = universal_priors.get(evt)
            tier_w = {"primary": 1.0, "secondary": 0.5, "miss": 0.0}[best_u]
            lr_universal = max(0.5, tier_w * 2)    # avoid log(0)
            r = score_event_relative(chart, evt, md_lord, ad_lord)
            best_cr = r["best_tier"]
            tier_w_cr = {"primary": 1.0, "secondary": 0.5, "miss": 0.0}[best_cr]
            lr_cr = max(0.5, tier_w_cr * 2)
            tf = _transit_factors_at(moment, natal_moon, natal_lagna,
                                      natal_sat, natal_jup, seventh)
            preds = _resolve_predictors(evt, use_learned=True)
            transit_match = any(tf.get(k) for k in preds)
            lr_t = learned_t.get(evt, {}).get("or_conjunction_LR") or 1.0
            lr_t_used = lr_t if transit_match else 1.0
            return [
                math.log(lr_universal), math.log(lr_cr), math.log(max(0.1, lr_t_used)),
            ]

        # Positive
        for ev in cm.events:
            if ev.event_type not in EVENT_PATTERNS:
                continue
            mo = ev.month if ev.month else 6
            dy = ev.day if ev.day else 15
            sig = signals_at(dt.datetime(ev.year, mo, dy), ev.event_type)
            if sig:
                by_event[ev.event_type]["X"].append(sig)
                by_event[ev.event_type]["y"].append(1)
        # Negative
        for evt in EVENT_PATTERNS.keys():
            negs = _sample_negative_years(cm, evt, n_neg_per_chart)
            for y in negs:
                sig = signals_at(dt.datetime(y, 6, 15), evt)
                if sig:
                    by_event[evt]["X"].append(sig)
                    by_event[evt]["y"].append(0)
    return by_event


def fit_all(n_iter: int = 1000) -> dict:
    """Fit per-event-type logistic models. Returns weight table."""
    data = _gather_signals_and_labels()
    out = {}
    for evt, d in data.items():
        if len(d["X"]) < 10 or sum(d["y"]) < 3:
            out[evt] = {"insufficient_data": True, "n": len(d["X"]),
                        "n_positive": sum(d["y"])}
            continue
        w = _fit_logistic(d["X"], d["y"], n_iter=n_iter)
        out[evt] = {
            "bias":               round(w[0], 4),
            "beta_universal":     round(w[1], 4),
            "beta_chart_rel":     round(w[2], 4),
            "beta_transit":       round(w[3], 4),
            "n_total":            len(d["X"]),
            "n_positive":         sum(d["y"]),
            "interpretation": _interpret(w),
        }
    return out


def _interpret(w):
    parts = []
    for name, val in zip(("universal", "chart_rel", "transit"), w[1:]):
        if val > 0.7:
            parts.append(f"{name} strong (β={val:.2f})")
        elif val > 0.2:
            parts.append(f"{name} moderate (β={val:.2f})")
        elif val > -0.2:
            parts.append(f"{name} ~uninformative (β={val:.2f})")
        else:
            parts.append(f"{name} ANTI-informative (β={val:.2f})")
    return "; ".join(parts)


def cache_weights(force: bool = False) -> dict:
    if CACHE.exists() and not force:
        return json.load(open(CACHE))
    weights = fit_all()
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    json.dump(weights, open(CACHE, "w"), indent=2)
    return weights


def predict_proba(event_type: str,
                   lr_universal: float, lr_chart_rel: float,
                   lr_transit: float) -> dict:
    weights = cache_weights()
    info = weights.get(event_type)
    if not info or info.get("insufficient_data"):
        return {"event_type": event_type, "error": "no fitted model"}
    z = (info["bias"]
         + info["beta_universal"] * math.log(max(0.1, lr_universal))
         + info["beta_chart_rel"] * math.log(max(0.1, lr_chart_rel))
         + info["beta_transit"] * math.log(max(0.1, lr_transit)))
    p = _logistic(z)
    return {
        "event_type": event_type,
        "probability_calibrated": round(p, 4),
        "log_odds": round(z, 4),
        "weights_used": {
            "bias": info["bias"], "universal": info["beta_universal"],
            "chart_rel": info["beta_chart_rel"], "transit": info["beta_transit"],
        },
        "interpretation": info["interpretation"],
    }


if __name__ == "__main__":
    weights = fit_all()
    print("=" * 90)
    print("LEARNED ENSEMBLE WEIGHTS  (logistic regression per event)")
    print("=" * 90)
    print(f"{'event':22s} {'n':>4s} {'n+':>3s} {'bias':>7s} {'β_uni':>7s} {'β_chart':>8s} {'β_trans':>8s}")
    for evt, info in sorted(weights.items()):
        if info.get("insufficient_data"):
            print(f"  {evt:20s}  insufficient data (n={info['n']}, n+={info['n_positive']})")
            continue
        print(f"  {evt:20s} {info['n_total']:>4d} {info['n_positive']:>3d} "
              f"{info['bias']:>7.3f} {info['beta_universal']:>7.3f} "
              f"{info['beta_chart_rel']:>8.3f} {info['beta_transit']:>8.3f}")
    print()
    cache_weights(force=True)
    print(f"Saved to {CACHE}")
