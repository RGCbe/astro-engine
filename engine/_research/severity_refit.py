"""
Empirical severity refit — auto-promote affliction severity from backtest lift.

Per audit: PAPAKARTARI_RAHU has 1.92× empirical bad-rate lift but engine
ships it as MODERATE. Truth directive demands the engine reflect empirical
reality. This module re-grades each affliction's severity based on its
ratio in `affliction_backtest`.

Promotion rules:
    ratio ≥ 1.7  → CRITICAL  (50%+ more bad events)
    ratio ≥ 1.4  → HIGH
    ratio ≥ 1.15 → MODERATE
    ratio < 1.15 → LOW (regardless of classical "severity")
    ratio < 0.95 → NO_LIFT (consider deprecating or marking as
                            statistically-non-discriminative)

Output is a refit table consumed by `engine.afflictions.detect_all` to
override the hand-coded severity per affliction.
"""
from __future__ import annotations

import json
from pathlib import Path

REFIT_CACHE = Path("/opt/astro/engine/data/affliction_severity_refit.json")
if not Path("/opt/astro").exists():
    REFIT_CACHE = Path(__file__).resolve().parents[1] / "data" / "affliction_severity_refit.json"


def refit_severities(min_n: int = 2) -> dict:
    """Recompute severity per affliction code from backtest ratio."""
    from engine._research.affliction_backtest import run_affliction_backtest
    r = run_affliction_backtest()
    out = {}
    for code, b in r["by_affliction"].items():
        ratio = b.get("ratio")
        n = b.get("n_charts_with", 0)
        if n < min_n or ratio is None:
            continue
        if ratio >= 1.7:
            new_sev = "CRITICAL"
        elif ratio >= 1.4:
            new_sev = "HIGH"
        elif ratio >= 1.15:
            new_sev = "MODERATE"
        elif ratio >= 0.95:
            new_sev = "LOW"
        else:
            new_sev = "NO_LIFT"    # actually anti-informative
        out[code] = {
            "empirical_severity": new_sev,
            "lift_ratio": ratio,
            "n_charts_with": n,
            "lift": b.get("lift"),
        }
    return out


def cache_refit(force: bool = False) -> dict:
    if REFIT_CACHE.exists() and not force:
        return json.load(open(REFIT_CACHE))
    refit = refit_severities()
    REFIT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    json.dump(refit, open(REFIT_CACHE, "w"), indent=2)
    return refit


def load_refit() -> dict:
    return cache_refit(force=False)


def empirical_severity(code: str, fallback: str) -> str:
    """Return empirical-refit severity for an affliction code, else fallback."""
    refit = load_refit()
    info = refit.get(code)
    if info is None:
        return fallback
    return info["empirical_severity"]


if __name__ == "__main__":
    refit = refit_severities()
    print("=" * 80)
    print("AFFLICTION SEVERITY REFIT (empirical from 61-chart backtest)")
    print("=" * 80)
    rows = []
    for code, info in refit.items():
        rows.append((info["lift_ratio"], code, info))
    rows.sort(reverse=True)
    print(f"{'affliction':40s} {'classical':>10s}  {'empirical':>10s}  {'ratio':>6s}  {'n':>3s}")
    for lift, code, info in rows[:30]:
        print(f"  {code:38s} {'(table)':>10s}  {info['empirical_severity']:>10s}  "
              f"{info['lift_ratio']:>6.2f}  {info['n_charts_with']:>3d}")
    cache_refit(force=True)
    print(f"\nSaved to {REFIT_CACHE}")
