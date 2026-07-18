"""
Data-driven refit of EVENT_PATTERNS primary/secondary lord sets.

Method: for each event type and each of the 9 lords, compute the per-lord
likelihood ratio:

    LR_lord = P(MD or AD = lord | event happened)
            / P(MD or AD = lord | random non-event year)

Then sort lords descending by LR and bucket:
    primary    : LR ≥ 1.5 (genuinely discriminative)
    secondary  : 1.1 ≤ LR < 1.5 (mildly informative)
    excluded   : LR < 1.1 (uninformative)

Output: a refitted EVENT_PATTERNS dict + a comparison table vs the
classical karaka set.

This refit is the engine's empirical correction to classical karaka theory
for modern documented outcomes. The classical sets remain in
`engine.backtest.EVENT_PATTERNS` as the *theoretical* baseline; the refit
is loaded as `EVENT_PATTERNS_REFIT` so callers can compare both.

Per the truth-only directive: when classical theory and data disagree,
the engine MUST surface both views. Don't silently replace one with the
other.
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

LORDS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")


def _gather_lords_per_year(chart, year_int):
    """Return set of {md_lord, ad_lord} active at midyear of `year_int`."""
    moon = _moon_lon(chart.birthdata)
    bdt = _birth_dt(chart.birthdata)
    b = {"year": bdt.year, "month": bdt.month, "day": bdt.day, "hour": bdt.hour, "min": bdt.minute}
    fake_chart = {"positions": {"Moon": {"lon": moon, "lon_abs": moon}}, "birth": b}
    active = current_dasha(fake_chart, dt.datetime(year_int, 6, 15))
    md = active.get("md")
    ad = active.get("ad")
    if md is None:
        return set()
    md_lord = md.get("md") or md.get("lord")
    ad_lord = ad.get("ad") or ad.get("lord") if ad else None
    out = {md_lord}
    if ad_lord:
        out.add(ad_lord)
    return out


def per_lord_lr(event_type: str, n_negative_per_chart: int = 5) -> dict:
    """Compute LR per lord for a given event type."""
    pos_count = Counter()
    neg_count = Counter()
    n_pos = 0
    n_neg = 0

    for chart in KNOWN_CHARTS:
        # Positives
        for ev in chart.events:
            if ev.event_type != event_type:
                continue
            lords = _gather_lords_per_year(chart, ev.year)
            for l in lords:
                pos_count[l] += 1
            n_pos += 1
        # Negatives
        neg_years = _sample_negative_years(chart, event_type, n_negative_per_chart)
        for y in neg_years:
            lords = _gather_lords_per_year(chart, y)
            for l in lords:
                neg_count[l] += 1
            n_neg += 1

    if n_pos == 0 or n_neg == 0:
        return {}

    out = {}
    for lord in LORDS:
        p_pos = pos_count[lord] / n_pos
        p_neg = neg_count[lord] / n_neg
        lr = round(p_pos / p_neg, 3) if p_neg > 0 else float("inf")
        out[lord] = {
            "p_in_event_year": round(p_pos, 3),
            "p_in_non_event_year": round(p_neg, 3),
            "LR": lr,
        }
    return {"n_positive": n_pos, "n_negative": n_neg, "by_lord": out}


def refit_event_patterns(
    primary_threshold: float = 1.5,
    secondary_threshold: float = 1.1,
) -> dict:
    """Refit primary/secondary sets per event type from per-lord LRs."""
    refit = {}
    comparison = {}
    for evt in EVENT_PATTERNS:
        data = per_lord_lr(evt)
        if not data:
            continue
        primary = set()
        secondary = set()
        for lord, info in data["by_lord"].items():
            lr = info["LR"]
            if lr == float("inf"):
                primary.add(lord)
            elif lr >= primary_threshold:
                primary.add(lord)
            elif lr >= secondary_threshold:
                secondary.add(lord)
        refit[evt] = {
            "primary": primary,
            "secondary": secondary,
            "rationale": (
                f"Empirical refit from negative-sample backtest "
                f"({data['n_positive']} pos / {data['n_negative']} neg). "
                f"Primary = LR≥{primary_threshold}; Secondary = "
                f"{secondary_threshold}≤LR<{primary_threshold}."
            ),
            "lords_with_lr": data["by_lord"],
        }
        # Comparison vs classical
        cls = EVENT_PATTERNS[evt]
        comparison[evt] = {
            "classical_primary":   sorted(cls["primary"]),
            "empirical_primary":   sorted(primary),
            "classical_secondary": sorted(cls["secondary"]),
            "empirical_secondary": sorted(secondary),
            "promoted_to_primary": sorted(primary - cls["primary"]),
            "demoted_from_primary": sorted(cls["primary"] - primary - secondary),
            "newly_dropped": sorted((cls["primary"] | cls["secondary"]) - primary - secondary),
        }
    return {"refit": refit, "comparison": comparison}


# ─── Build the refitted patterns once and cache to disk ────────────────────
REFIT_CACHE = Path("/opt/astro/engine/data/event_patterns_refit.json")
if not Path("/opt/astro").exists():
    REFIT_CACHE = Path(__file__).resolve().parent / "data" / "event_patterns_refit.json"


def load_refit() -> dict:
    """Load cached refit; rebuild if missing."""
    if not REFIT_CACHE.exists():
        return build_and_cache(force=True)
    with open(REFIT_CACHE) as f:
        cached = json.load(f)
    for evt, data in cached["refit"].items():
        if isinstance(data["primary"], list):
            data["primary"] = set(data["primary"])
            data["secondary"] = set(data["secondary"])
    return cached


def compare(event_type: str) -> dict:
    """Return a side-by-side classical vs empirical comparison for one event."""
    cached = load_refit()
    cmp = cached.get("comparison", {}).get(event_type)
    refit = cached.get("refit", {}).get(event_type)
    if cmp is None or refit is None:
        return {"error": f"no refit data for {event_type}"}
    return {
        "event_type": event_type,
        "classical_primary": cmp["classical_primary"],
        "empirical_primary": cmp["empirical_primary"],
        "classical_secondary": cmp["classical_secondary"],
        "empirical_secondary": cmp["empirical_secondary"],
        "lords_with_lr": refit["lords_with_lr"],
        "promoted_to_primary": cmp["promoted_to_primary"],
        "demoted_from_primary": cmp["demoted_from_primary"],
        "newly_dropped": cmp["newly_dropped"],
        "interpretation": _interpret(cmp),
    }


def _interpret(cmp: dict) -> str:
    parts = []
    if cmp["promoted_to_primary"]:
        parts.append(
            f"Empirically PROMOTED (LR≥1.5, no classical authority): "
            f"{', '.join(cmp['promoted_to_primary'])}."
        )
    if cmp["newly_dropped"]:
        parts.append(
            f"Classical karakas DROPPED (LR<1.1, statistically inert): "
            f"{', '.join(cmp['newly_dropped'])}."
        )
    if not parts:
        parts.append("Classical karaka theory matches the data for this event.")
    return " ".join(parts)


def build_and_cache(force: bool = False) -> dict:
    """Build the refit and cache to disk."""
    if REFIT_CACHE.exists() and not force:
        with open(REFIT_CACHE) as f:
            cached = json.load(f)
        # Convert lists back to sets for primary/secondary
        for evt, data in cached["refit"].items():
            data["primary"] = set(data["primary"])
            data["secondary"] = set(data["secondary"])
        return cached
    result = refit_event_patterns()
    # Serialize sets as sorted lists for JSON
    serialized = {"refit": {}, "comparison": result["comparison"]}
    for evt, data in result["refit"].items():
        serialized["refit"][evt] = {
            "primary": sorted(data["primary"]),
            "secondary": sorted(data["secondary"]),
            "rationale": data["rationale"],
            "lords_with_lr": data["lords_with_lr"],
        }
    REFIT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(REFIT_CACHE, "w") as f:
        json.dump(serialized, f, indent=2)
    return result


def print_comparison() -> None:
    r = refit_event_patterns()
    print("=" * 80)
    print("EVENT_PATTERNS — Classical karaka set vs Empirical LR-based refit")
    print("=" * 80)
    for evt, c in r["comparison"].items():
        print(f"\n{evt}")
        print(f"  Classical primary:   {c['classical_primary']}")
        print(f"  Empirical  primary:  {c['empirical_primary']}")
        if c["promoted_to_primary"]:
            print(f"  → PROMOTED to primary (data-driven): {c['promoted_to_primary']}")
        if c["demoted_from_primary"]:
            print(f"  → DEMOTED from primary (LR < 1.1):   {c['demoted_from_primary']}")
        if c["newly_dropped"]:
            print(f"  → DROPPED entirely (LR < 1.1):        {c['newly_dropped']}")


if __name__ == "__main__":
    print_comparison()
    print("\n\nWriting refit cache...")
    build_and_cache(force=True)
    print(f"Cached to {REFIT_CACHE}")
