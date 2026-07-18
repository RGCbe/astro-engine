"""
Probabilistic confidence calibration for dasha-based event forecasts.

Given the tiered backtest in `engine.backtest`, each event-type has empirical
hit rates per tier (primary / secondary / miss). This module:

    1. Computes per-event-type tier priors from the backtest
    2. Provides `forecast_confidence(event_type, md_lord, ad_lord)` →
       calibrated probability that the engine should attach to a forecast
       of `event_type` for someone currently in MD/AD = (md_lord, ad_lord).
    3. Reports Brier score (mean squared deviation from observed outcome=1)
       for the backtest predictions — lower is better-calibrated.

This is the foundation for moving the engine from rule-matcher to
probability-aware forecaster. The probabilities are conditional on the
documented event happening at all (we have only positive outcomes in the
known-charts library); they should be read as "given that the engine
flagged this event, here is the strength of the dasha-lord signature
behind that flag."
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.backtest import (
    EVENT_PATTERNS,
    TIER_WEIGHT,
    _classify,
    run_full_backtest,
)


@dataclass
class TierPrior:
    event_type: str
    n: int
    primary_rate: float    # fraction where best tier was primary
    secondary_rate: float  # fraction where best tier was secondary
    miss_rate: float       # fraction with no match
    weighted_rate: float   # mean(best_weight) — overall calibrated strength


_PRIOR_CACHE = {}

def event_priors(backtest_result: dict | None = None) -> dict[str, TierPrior]:
    """Build per-event-type empirical priors from the backtest."""
    if backtest_result is None and "data" in _PRIOR_CACHE:
        return _PRIOR_CACHE["data"]
    r = backtest_result if backtest_result is not None else run_full_backtest()
    priors: dict[str, TierPrior] = {}
    for evt, b in r["by_event_type"].items():
        n = b["n"]
        if n == 0:
            continue
        priors[evt] = TierPrior(
            event_type=evt,
            n=n,
            primary_rate=b["primary_hits"] / n,
            secondary_rate=b["secondary_hits"] / n,
            miss_rate=1.0 - b["primary_hits"] / n - b["secondary_hits"] / n,
            weighted_rate=b["weighted_sum"] / n,
        )
    if backtest_result is None:
        _PRIOR_CACHE["data"] = priors
    return priors


_NEG_CACHE = {}


def _bayesian_posteriors() -> dict:
    """Run negative_backtest once and cache the posterior table."""
    if "data" in _NEG_CACHE:
        return _NEG_CACHE["data"]
    from engine.negative_backtest import run_negative_backtest
    _NEG_CACHE["data"] = run_negative_backtest()["by_event_type"]
    return _NEG_CACHE["data"]


def forecast_confidence(
    event_type: str,
    md_lord: str | None,
    ad_lord: str | None,
    priors: dict[str, TierPrior] | None = None,
) -> dict:
    """Calibrated forecast for `event_type` given the active MD/AD.

    Returns:
        {
          "event_type": str,
          "md_tier":    "primary" | "secondary" | "miss",
          "ad_tier":    same,
          "best_tier":  same,
          "raw_weight": 1.0 / 0.5 / 0.0  (engineered prior),
          "empirical_strength": float in [0, 1],
              # historical mean weight when event happened — i.e.,
              # how often events of this type fall in primary vs secondary
              # signatures. High = strong classical signature on this event.
          "confidence_band": "HIGH" | "MEDIUM" | "LOW" | "WEAK",
          "rationale": str,
          "n_training": int,  # how many backtest events back this prior
        }
    """
    pattern = EVENT_PATTERNS.get(event_type)
    if not pattern:
        return {"event_type": event_type, "error": "unknown event type"}
    primary, secondary = pattern["primary"], pattern["secondary"]

    md_tier = _classify(md_lord, primary, secondary)
    ad_tier = _classify(ad_lord, primary, secondary)
    rank = {"primary": 2, "secondary": 1, "miss": 0}
    best_tier = md_tier if rank[md_tier] >= rank[ad_tier] else ad_tier
    raw_weight = TIER_WEIGHT[best_tier]

    p = (priors or event_priors()).get(event_type)
    empirical = p.weighted_rate if p else raw_weight

    # Bayesian posterior from negative_backtest (P(event | tier) using
    # likelihood ratio against non-event-year base rate). This is the
    # honest probability — recall-only `empirical` overstates because
    # primary lords also fire in non-event years.
    bayes = _bayesian_posteriors().get(event_type, {})
    posterior = (bayes.get("posterior_event_given_primary") if best_tier == "primary"
                 else bayes.get("posterior_event_given_secondary") if best_tier == "secondary"
                 else None)
    lr = (bayes.get("LR_primary") if best_tier == "primary"
          else bayes.get("LR_secondary") if best_tier == "secondary"
          else None)

    # Confidence band uses the LR (informativeness) — only HIGH if the
    # tier is genuinely discriminative, not just a recall match.
    if best_tier == "primary" and lr is not None and lr >= 1.5:
        band = "HIGH"
    elif best_tier == "primary" and lr is not None and lr >= 1.1:
        band = "MEDIUM"
    elif best_tier == "primary":
        band = "LOW"           # primary tier but uninformative — recall-only signal
    elif best_tier == "secondary" and lr is not None and lr >= 1.5:
        band = "MEDIUM"
    elif best_tier == "secondary":
        band = "LOW"
    else:
        band = "WEAK"

    return {
        "event_type": event_type,
        "md_lord": md_lord, "ad_lord": ad_lord,
        "md_tier": md_tier, "ad_tier": ad_tier, "best_tier": best_tier,
        "raw_weight": raw_weight,
        "empirical_recall": round(empirical, 3),    # P(tier | event happened)
        "likelihood_ratio": lr,                      # P(tier|+)/P(tier|-)
        "bayesian_posterior": round(posterior, 4) if posterior is not None else None,
        "confidence_band": band,
        "rationale": pattern["rationale"],
        "n_training": p.n if p else 0,
        "interpretation": _band_interpretation(band, lr),
    }


def _band_interpretation(band: str, lr: float | None) -> str:
    if band == "HIGH":
        return f"Strong dasha signature (LR={lr}); event genuinely more likely than chance."
    if band == "MEDIUM":
        return f"Moderate signature (LR={lr}); modest lift over base rate."
    if band == "LOW":
        return ("Weak/uninformative signature — primary lord matches by recall but "
                "is not discriminative against non-event years.")
    if band == "WEAK":
        return "No classical karaka signature; engine has no reason to flag this."
    return ""


# ─── Brier score & reliability ─────────────────────────────────────────────
def brier_score(backtest_result: dict | None = None) -> dict:
    """Mean squared deviation of tier weight from documented outcome (=1).

    Brier of always-1 = 0. Brier of always-0 = 1. Lower is better.
    Tier weights of {primary:1.0, secondary:0.5, miss:0.0} produce per-prediction
    error of {0, 0.25, 1.0} for documented events.
    """
    r = backtest_result if backtest_result is not None else run_full_backtest()
    results = r["results"]
    if not results:
        return {"brier": None, "n": 0}

    # Brier using raw tier weights (engineered prior)
    raw_se = [(1.0 - rr.best_weight) ** 2 for rr in results]
    raw_brier = sum(raw_se) / len(raw_se)

    # Brier using empirically-blended calibrated score
    priors = event_priors(r)
    cal_se = []
    for rr in results:
        p = priors.get(rr.event_type)
        emp = p.weighted_rate if p else rr.best_weight
        cal = rr.best_weight * (0.5 + 0.5 * emp)
        cal_se.append((1.0 - cal) ** 2)
    cal_brier = sum(cal_se) / len(cal_se)

    # Per-tier reliability (n in tier, mean error)
    by_tier = {"primary": [], "secondary": [], "miss": []}
    for rr in results:
        by_tier[rr.best_tier].append((1.0 - rr.best_weight) ** 2)
    reliability = {
        t: {"n": len(v), "mean_brier": round(sum(v) / len(v), 4) if v else None}
        for t, v in by_tier.items()
    }

    return {
        "n": len(results),
        "raw_tier_brier": round(raw_brier, 4),
        "calibrated_brier": round(cal_brier, 4),
        "reference_brier_uniform_0_5": 0.25,   # always-predict-0.5
        "reference_brier_always_0": 1.0,
        "reference_brier_always_1": 0.0,
        "by_tier": reliability,
        "interpretation": (
            "Lower brier is better. Always-1 = 0.0 (perfect), Always-0.5 = 0.25, "
            "Always-0 = 1.0. Our tier weights and calibrated scores compared "
            "above. Per-tier 'mean_brier' is the average squared error within "
            "predictions of that tier."
        ),
    }


# ─── Convenience: print a calibration report ───────────────────────────────
def print_report() -> None:
    r = run_full_backtest()
    priors = event_priors(r)
    bs = brier_score(r)

    print("=" * 70)
    print("CALIBRATION REPORT")
    print("=" * 70)
    print(f"Backtest events:               {r['n_events_scored']}")
    print(f"Overall STRICT (primary):      {r['overall_strict_match_pct']}%")
    print(f"Overall EITHER (primary+sec):  {r['overall_either_match_pct']}%")
    print(f"Overall WEIGHTED (1.0/0.5):    {r['overall_weighted_pct']}%")
    print()
    print(f"Raw-tier Brier:        {bs['raw_tier_brier']}")
    print(f"Calibrated Brier:      {bs['calibrated_brier']}")
    print(f"Reference (always 0.5): {bs['reference_brier_uniform_0_5']}")
    print()
    print(f"{'event_type':22s} {'n':>3s} {'pri%':>6s} {'sec%':>6s} {'miss%':>6s}  empirical")
    for evt in sorted(priors, key=lambda k: -priors[k].weighted_rate):
        p = priors[evt]
        print(f"  {evt:20s} {p.n:3d} {p.primary_rate*100:5.1f}% "
              f"{p.secondary_rate*100:5.1f}% {p.miss_rate*100:5.1f}%   "
              f"{p.weighted_rate:.3f}")
    print()
    print("Per-tier reliability:")
    for tier, info in bs["by_tier"].items():
        print(f"  {tier:10s} n={info['n']:3d}  mean_brier={info['mean_brier']}")


if __name__ == "__main__":
    print_report()
