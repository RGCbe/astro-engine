"""
Empirical learning of per-event transit predictors.

Replaces hand-coded EVENT_TRANSIT_PREDICTORS with a data-driven set: for each
event type, compute LR per individual transit factor on positive vs negative
samples; greedy-select the subset whose OR-conjunction maximizes LR while
maintaining minimum support.

Per truth directive: when classical-coded predictors disagree with the
learned set, both are reported.
"""
from __future__ import annotations

import datetime as dt
import json
from collections import Counter
from pathlib import Path

from engine.backtest import EVENT_PATTERNS
from engine.dasha import current_dasha, vimshottari
from engine.known_charts import KNOWN_CHARTS
from engine.negative_backtest import (
    _moon_lon, _birth_dt, _sample_negative_years,
)
from engine.transit_conditioned import (
    _transit_factors_at, EVENT_TRANSIT_PREDICTORS,
)

ALL_TRANSIT_FACTORS = (
    "sade_sati", "saturn_return", "jupiter_in_7th_sign",
    "jupiter_trikona_from_moon", "rahu_on_lagna", "rahu_on_moon",
    "ketu_on_lagna", "ketu_on_moon",
)

CACHE_PATH = Path("/opt/astro/engine/data/learned_transit_predictors.json")
if not Path("/opt/astro").exists():
    CACHE_PATH = Path(__file__).resolve().parents[1] / "data" / "learned_transit_predictors.json"


def _gather_factor_counts(n_negative_per_chart: int = 5) -> dict:
    """For every event type and every transit factor, count positive vs
    negative-year occurrences."""
    pos: dict = {evt: {f: 0 for f in ALL_TRANSIT_FACTORS} for evt in EVENT_PATTERNS}
    pos_n: dict = {evt: 0 for evt in EVENT_PATTERNS}
    neg: dict = {evt: {f: 0 for f in ALL_TRANSIT_FACTORS} for evt in EVENT_PATTERNS}
    neg_n: dict = {evt: 0 for evt in EVENT_PATTERNS}

    for chart_meta in KNOWN_CHARTS:
        try:
            from engine.chart import compute_chart
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

        # Positive
        for ev in chart_meta.events:
            if ev.event_type not in EVENT_PATTERNS:
                continue
            mo = ev.month if ev.month else 6
            dy = ev.day if ev.day else 15
            moment = dt.datetime(ev.year, mo, dy)
            tf = _transit_factors_at(moment, natal_moon, natal_lagna,
                                      natal_sat, natal_jup, seventh_sign)
            pos_n[ev.event_type] += 1
            for f in ALL_TRANSIT_FACTORS:
                if tf[f]:
                    pos[ev.event_type][f] += 1

        # Negative
        for evt in EVENT_PATTERNS.keys():
            negs = _sample_negative_years(chart_meta, evt, n_negative_per_chart)
            for y in negs:
                moment = dt.datetime(y, 6, 15)
                tf = _transit_factors_at(moment, natal_moon, natal_lagna,
                                          natal_sat, natal_jup, seventh_sign)
                neg_n[evt] += 1
                for f in ALL_TRANSIT_FACTORS:
                    if tf[f]:
                        neg[evt][f] += 1

    return {"pos": pos, "neg": neg, "pos_n": pos_n, "neg_n": neg_n}


def per_factor_lr(counts: dict) -> dict:
    """LR per individual transit factor per event type."""
    out = {}
    for evt in EVENT_PATTERNS.keys():
        n_pos = counts["pos_n"][evt]
        n_neg = counts["neg_n"][evt]
        if n_pos == 0 or n_neg == 0:
            continue
        out[evt] = {}
        for f in ALL_TRANSIT_FACTORS:
            p_pos = counts["pos"][evt][f] / n_pos
            p_neg = counts["neg"][evt][f] / n_neg
            lr = (p_pos / p_neg) if p_neg > 0 else (float("inf") if p_pos > 0 else None)
            out[evt][f] = {
                "P_pos": round(p_pos, 4),
                "P_neg": round(p_neg, 4),
                "LR": round(lr, 3) if lr not in (None, float("inf")) else lr,
                "n_pos_hits": counts["pos"][evt][f],
                "n_neg_hits": counts["neg"][evt][f],
            }
    return out


def _or_conjunction_lr(counts: dict, evt: str, factor_set: list[str]) -> tuple[float, float, float]:
    """Compute OR-conjunction LR: P(any factor in set fires | event) / P(any | non-event).

    Per-event: read the precomputed counts. For OR we need joint counts which
    aren't precomputed here — recompute by re-iterating.
    """
    # Recompute joint OR fires across the corpus
    if not factor_set:
        return 0.0, 0.0, 0.0
    n_pos = counts["pos_n"][evt]
    n_neg = counts["neg_n"][evt]
    if n_pos == 0 or n_neg == 0:
        return 0.0, 0.0, 0.0
    # We only have per-factor counts. To compute OR-counts we'd need to
    # re-iterate. Use Bonferroni upper-bound: count = sum(per-factor) - intersections.
    # Simpler: recompute by iterating (cached as JSON).
    raise NotImplementedError("Use _or_conjunction_lr_full")


def _or_lr_full(evt: str, factor_set: list[str], n_neg_per_chart: int = 5) -> tuple[float, int, int]:
    """Re-iterate corpus and compute OR-conjunction LR for `factor_set`."""
    n_pos_total = 0; n_pos_hit = 0
    n_neg_total = 0; n_neg_hit = 0

    for chart_meta in KNOWN_CHARTS:
        try:
            from engine.chart import compute_chart
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

        for ev in chart_meta.events:
            if ev.event_type != evt:
                continue
            mo = ev.month if ev.month else 6
            dy = ev.day if ev.day else 15
            tf = _transit_factors_at(dt.datetime(ev.year, mo, dy),
                                      natal_moon, natal_lagna,
                                      natal_sat, natal_jup, seventh_sign)
            n_pos_total += 1
            if any(tf.get(f) for f in factor_set):
                n_pos_hit += 1

        negs = _sample_negative_years(chart_meta, evt, n_neg_per_chart)
        for y in negs:
            tf = _transit_factors_at(dt.datetime(y, 6, 15),
                                      natal_moon, natal_lagna,
                                      natal_sat, natal_jup, seventh_sign)
            n_neg_total += 1
            if any(tf.get(f) for f in factor_set):
                n_neg_hit += 1

    if n_pos_total == 0 or n_neg_total == 0:
        return 0.0, n_pos_hit, n_neg_hit
    p_pos = n_pos_hit / n_pos_total
    p_neg = n_neg_hit / n_neg_total
    if p_neg == 0:
        return float("inf") if p_pos > 0 else 0.0, n_pos_hit, n_neg_hit
    return p_pos / p_neg, n_pos_hit, n_neg_hit


def learn_predictors(min_pos_support: int = 3, min_pos_coverage_frac: float = 0.15) -> dict:
    """For each event type, greedy-select factors that maximize OR-conjunction
    LR. Start empty; add the factor whose addition most increases LR; stop
    when no factor improves it.

    Filters (truth directive: don't ship LR estimates from 2-event samples):
        - factor must fire in ≥ max(min_pos_support, 0.15 × n_positive) events
        - this prevents single-coincidence "predictors" with LR=15 from 2 hits
    """
    counts = _gather_factor_counts()
    factor_lrs = per_factor_lr(counts)
    out = {}
    for evt, by_f in factor_lrs.items():
        n_pos = counts["pos_n"][evt]
        threshold = max(min_pos_support, int(n_pos * min_pos_coverage_frac))
        eligible = [f for f in ALL_TRANSIT_FACTORS
                    if by_f[f]["n_pos_hits"] >= threshold]
        selected: list[str] = []
        best_lr = 1.0   # start at chance
        best_pos = 0; best_neg = 0
        improved = True
        while improved and eligible:
            improved = False
            best_candidate = None
            best_candidate_lr = best_lr
            best_candidate_pos = best_pos
            best_candidate_neg = best_neg
            for f in eligible:
                trial = selected + [f]
                lr, pos_hit, neg_hit = _or_lr_full(evt, trial)
                if lr == float("inf"):
                    lr = 999  # treat infinity as huge
                if lr > best_candidate_lr + 0.05:   # require meaningful lift
                    best_candidate = f
                    best_candidate_lr = lr
                    best_candidate_pos = pos_hit
                    best_candidate_neg = neg_hit
            if best_candidate is not None:
                selected.append(best_candidate)
                eligible.remove(best_candidate)
                best_lr = best_candidate_lr
                best_pos = best_candidate_pos
                best_neg = best_candidate_neg
                improved = True

        out[evt] = {
            "learned_predictors": selected,
            "or_conjunction_LR": round(best_lr, 3),
            "n_pos_or_hits": best_pos,
            "n_neg_or_hits": best_neg,
            "factor_LRs": {f: info["LR"] for f, info in by_f.items()},
            "factor_support_pos": {f: info["n_pos_hits"] for f, info in by_f.items()},
            "factor_support_neg": {f: info["n_neg_hits"] for f, info in by_f.items()},
            "n_pos": counts["pos_n"][evt],
            "n_neg": counts["neg_n"][evt],
            "hand_coded_predictors": EVENT_TRANSIT_PREDICTORS.get(evt, []),
        }
    return out


def cache_learned(force: bool = False) -> dict:
    if CACHE_PATH.exists() and not force:
        return json.load(open(CACHE_PATH))
    learned = learn_predictors()
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    json.dump(learned, open(CACHE_PATH, "w"), indent=2)
    return learned


def load_learned() -> dict:
    return cache_learned(force=False)


def print_report():
    learned = learn_predictors()
    print("=" * 95)
    print("LEARNED TRANSIT PREDICTORS vs HAND-CODED")
    print("=" * 95)
    for evt, data in learned.items():
        learned_set = data["learned_predictors"]
        hand = data["hand_coded_predictors"]
        added = [f for f in learned_set if f not in hand]
        dropped = [f for f in hand if f not in learned_set]
        print(f"\n{evt}  (n+={data['n_pos']}, n-={data['n_neg']})")
        print(f"  hand-coded:  {hand}")
        print(f"  learned:     {learned_set}")
        if added:
            print(f"  → ADDED (data-discovered): {added}")
        if dropped:
            print(f"  → DROPPED (hand-coded but uninformative): {dropped}")
        # Show top-3 LRs per factor
        top = sorted(data["factor_LRs"].items(),
                     key=lambda x: -(x[1] if isinstance(x[1], (int, float)) else 0))[:3]
        print(f"  top factor LRs: {top}")


if __name__ == "__main__":
    print_report()
    print()
    print("Caching to disk...")
    cache_learned(force=True)
