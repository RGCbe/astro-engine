"""
Ensemble scorer — combine three scoring approaches per event.

Three independent signals per (chart, event_type, MD_lord, AD_lord):
    1. universal_karaka  — engine.backtest.EVENT_PATTERNS (classical)
    2. chart_relative    — engine.chart_relative (per-chart 10th lord, AmK, etc.)
    3. transit           — learned transit predictors at the moment

Each emits a tier (primary/secondary/miss). The ensemble combines them via
log-LR addition (assuming approximate independence — this is the standard
"naive Bayes" combination).

Per-signal LRs are sourced from the three backtest harnesses
(engine.negative_backtest, engine.chart_relative_backtest,
engine.transit_learn). When a signal's LR is unavailable, it contributes
0 to the log-LR sum.

The output `ensemble_LR` is the product of per-signal LRs (or sum of
log-LRs); calibrated posterior assumes the same base rate as the
calibration module uses.

Per the truth directive:
    - Each signal's contribution is shown separately.
    - When signals disagree (one says primary, another miss), both are
      reported, not averaged silently.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache

from engine.backtest import EVENT_PATTERNS, _classify
from engine.chart_relative import score_event_relative


# ─── Cached LR tables ──────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _universal_lrs() -> dict:
    """LR per event type for universal-karaka primary tier."""
    from engine.negative_backtest import run_negative_backtest
    r = run_negative_backtest(n_samples_per_event=5)
    out = {}
    for evt, b in r["by_event_type"].items():
        out[evt] = {
            "LR_primary":   b.get("LR_primary"),
            "LR_secondary": b.get("LR_secondary"),
        }
    return out


@lru_cache(maxsize=1)
def _chart_relative_lrs() -> dict:
    """LR per event type for chart-relative primary tier."""
    from engine.chart_relative_backtest import run_chart_relative_backtest
    r = run_chart_relative_backtest(n_negative_per_chart=5)
    return {evt: {"LR_primary":   b.get("LR_primary"),
                  "LR_secondary": b.get("LR_secondary")}
            for evt, b in r["by_event_type"].items()}


@lru_cache(maxsize=1)
def _transit_lrs() -> dict:
    """LR per event type for the learned transit predictor set (OR-LR)."""
    from engine.transit_learn import load_learned
    learned = load_learned()
    return {evt: {"LR_or_conjunction": data.get("or_conjunction_LR"),
                  "predictors":        data.get("learned_predictors", [])}
            for evt, data in learned.items()}


# ─── Per-signal scoring (returns LR contribution) ──────────────────────────
def _universal_signal_lr(event_type: str, md_lord: str | None,
                          ad_lord: str | None) -> float | None:
    """LR contribution from universal-karaka tier match."""
    pattern = EVENT_PATTERNS.get(event_type)
    if not pattern:
        return None
    md_t = _classify(md_lord, pattern["primary"], pattern["secondary"])
    ad_t = _classify(ad_lord, pattern["primary"], pattern["secondary"])
    rank = {"primary": 2, "secondary": 1, "miss": 0}
    best = md_t if rank[md_t] >= rank[ad_t] else ad_t
    lrs = _universal_lrs().get(event_type, {})
    if best == "primary":
        return lrs.get("LR_primary")
    if best == "secondary":
        return lrs.get("LR_secondary")
    return 1.0   # miss → no signal, neutral


def _chart_relative_signal_lr(chart, event_type: str,
                               md_lord: str | None,
                               ad_lord: str | None) -> float | None:
    """LR contribution from chart-relative tier match."""
    r = score_event_relative(chart, event_type, md_lord, ad_lord)
    best = r["best_tier"]
    lrs = _chart_relative_lrs().get(event_type, {})
    if best == "primary":
        return lrs.get("LR_primary")
    if best == "secondary":
        return lrs.get("LR_secondary")
    return 1.0


def _transit_signal_lr(event_type: str, transit_factors: dict) -> float | None:
    """LR contribution from learned-transit OR-conjunction match."""
    from engine.transit_learn import load_learned
    learned = load_learned().get(event_type, {})
    predictors = learned.get("learned_predictors", [])
    if not predictors:
        return 1.0
    if any(transit_factors.get(p) for p in predictors):
        return learned.get("or_conjunction_LR") or 1.0
    return 1.0


# ─── Ensemble ──────────────────────────────────────────────────────────────
@dataclass
class EnsembleScore:
    event_type: str
    md_lord: str
    ad_lord: str
    universal_LR: float | None
    chart_relative_LR: float | None
    transit_LR: float | None
    ensemble_LR: float
    ensemble_log_lr: float
    interpretation: str


def ensemble_score(
    chart,
    event_type: str,
    md_lord: str | None,
    ad_lord: str | None,
    transit_factors: dict | None = None,
) -> EnsembleScore:
    """Combine all three signals via log-LR addition (naive Bayes).

    transit_factors: dict from engine.transit_conditioned._transit_factors_at
                     If None, transit signal is neutral (LR=1).
    """
    u_lr = _universal_signal_lr(event_type, md_lord, ad_lord) or 1.0
    cr_lr = _chart_relative_signal_lr(chart, event_type, md_lord, ad_lord) or 1.0
    t_lr = _transit_signal_lr(event_type, transit_factors or {}) or 1.0

    # Naive-Bayes combination: log-LR sum
    log_lr = math.log(u_lr) + math.log(cr_lr) + math.log(t_lr)
    ens_lr = u_lr * cr_lr * t_lr

    # Interpretation
    parts = []
    if u_lr > 1.1: parts.append(f"universal-karaka tier informative (LR={u_lr:.2f})")
    elif u_lr < 0.9: parts.append(f"universal-karaka tier ANTI-informative (LR={u_lr:.2f})")
    if cr_lr > 1.1: parts.append(f"chart-relative tier informative (LR={cr_lr:.2f})")
    elif cr_lr < 0.9: parts.append(f"chart-relative tier ANTI-informative (LR={cr_lr:.2f})")
    if t_lr > 1.1: parts.append(f"transit predictor fired (LR={t_lr:.2f})")
    elif t_lr < 0.9: parts.append(f"transit predictor MISSED (LR={t_lr:.2f})")
    if not parts:
        interp = "All three signals neutral (~chance level). No reason to flag this event."
    else:
        interp = "; ".join(parts)
        if ens_lr > 2.0:
            interp = "STRONG combined signal. " + interp
        elif ens_lr > 1.3:
            interp = "Moderate combined signal. " + interp
        elif ens_lr < 0.7:
            interp = "Combined signal AGAINST this event. " + interp
        else:
            interp = "Weak combined signal. " + interp

    return EnsembleScore(
        event_type=event_type, md_lord=md_lord or "", ad_lord=ad_lord or "",
        universal_LR=round(u_lr, 3), chart_relative_LR=round(cr_lr, 3),
        transit_LR=round(t_lr, 3),
        ensemble_LR=round(ens_lr, 3),
        ensemble_log_lr=round(log_lr, 3),
        interpretation=interp,
    )


# ─── Backtest the ensemble itself ──────────────────────────────────────────
def backtest_ensemble(n_negative_per_chart: int = 5) -> dict:
    """Compute the LR for the ensemble's "elevated" verdict (ensemble_LR > 1.5)
    on positive vs negative samples — does the ensemble actually discriminate?
    """
    import datetime as dt
    from engine.chart import compute_chart
    from engine.dasha import current_dasha, vimshottari
    from engine.known_charts import KNOWN_CHARTS
    from engine.negative_backtest import (
        _moon_lon, _birth_dt, _sample_negative_years,
    )
    from engine.transit_conditioned import _transit_factors_at

    pos_n = {evt: 0 for evt in EVENT_PATTERNS}
    pos_hi = {evt: 0 for evt in EVENT_PATTERNS}
    neg_n = {evt: 0 for evt in EVENT_PATTERNS}
    neg_hi = {evt: 0 for evt in EVENT_PATTERNS}

    for chart_meta in KNOWN_CHARTS:
        try:
            bd = chart_meta.birthdata
            chart = compute_chart(name=chart_meta.name, date=bd["date"],
                                  time=bd["time"], tz_hours=bd["tz"],
                                  lat=bd.get("lat"), lon=bd.get("lon"))
        except Exception:
            continue
        natal_moon = chart.positions["Moon"]
        natal_lagna = chart.lagna_lon
        natal_sat = chart.positions["Saturn"]
        natal_jup = chart.positions["Jupiter"]
        seventh_sign = (int(natal_lagna // 30) + 6) % 12
        moon_for_dasha = _moon_lon(chart_meta.birthdata)
        periods = vimshottari(moon_for_dasha, _birth_dt(chart_meta.birthdata))

        for ev in chart_meta.events:
            if ev.event_type not in EVENT_PATTERNS:
                continue
            mo = ev.month if ev.month else 6
            dy = ev.day if ev.day else 15
            moment = dt.datetime(ev.year, mo, dy)
            md, ad = current_dasha(chart, moment)
            if md is None:
                continue
            tf = _transit_factors_at(moment, natal_moon, natal_lagna,
                                      natal_sat, natal_jup, seventh_sign)
            es = ensemble_score(chart, ev.event_type,
                                md.lord, ad.lord if ad else None, tf)
            pos_n[ev.event_type] += 1
            if es.ensemble_LR >= 1.5:
                pos_hi[ev.event_type] += 1

        for evt in EVENT_PATTERNS.keys():
            negs = _sample_negative_years(chart_meta, evt, n_negative_per_chart)
            for y in negs:
                moment = dt.datetime(y, 6, 15)
                md, ad = current_dasha(chart, moment)
                if md is None:
                    continue
                tf = _transit_factors_at(moment, natal_moon, natal_lagna,
                                          natal_sat, natal_jup, seventh_sign)
                es = ensemble_score(chart, evt, md.lord,
                                     ad.lord if ad else None, tf)
                neg_n[evt] += 1
                if es.ensemble_LR >= 1.5:
                    neg_hi[evt] += 1

    out = {}
    for evt in EVENT_PATTERNS.keys():
        if pos_n[evt] == 0 or neg_n[evt] == 0:
            continue
        p_pos = pos_hi[evt] / pos_n[evt]
        p_neg = neg_hi[evt] / neg_n[evt]
        lr = (p_pos / p_neg) if p_neg > 0 else (float("inf") if p_pos > 0 else None)
        out[evt] = {
            "n_positive": pos_n[evt],
            "n_negative": neg_n[evt],
            "P_ensemble_high_pos": round(p_pos, 4),
            "P_ensemble_high_neg": round(p_neg, 4),
            "LR_ensemble_threshold_1.5": round(lr, 3) if lr not in (None, float("inf")) else lr,
        }
    return {"by_event_type": out}


def print_ensemble_report():
    r = backtest_ensemble()
    print("=" * 75)
    print("ENSEMBLE LR (signals: universal-karaka + chart-relative + transit)")
    print("=" * 75)
    print(f"{'event':22s} {'n+':>3s} {'n-':>3s}  {'P_hi+':>7s} {'P_hi-':>7s}  {'LR':>7s}")
    rows = []
    for evt, b in r["by_event_type"].items():
        rows.append((b["LR_ensemble_threshold_1.5"] or 0, evt, b))
    rows.sort(reverse=True)
    for lr, evt, b in rows:
        lr_s = f"{lr:.3f}" if isinstance(lr, (int, float)) and lr != float("inf") else "inf"
        print(f"  {evt:20s} {b['n_positive']:3d} {b['n_negative']:3d}   "
              f"{b['P_ensemble_high_pos']:.3f}   {b['P_ensemble_high_neg']:.3f}   {lr_s:>7s}")


if __name__ == "__main__":
    print_ensemble_report()
