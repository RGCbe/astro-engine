"""Tests for engine.calibration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.calibration import (
    event_priors, forecast_confidence, brier_score,
)


def test_event_priors_cover_main_events():
    p = event_priors()
    for evt in ("DEATH", "MARRIAGE", "AWARD", "CAREER_PEAK"):
        assert evt in p
        assert p[evt].n > 0
        assert 0.0 <= p[evt].weighted_rate <= 1.0


def test_brier_better_than_uniform():
    bs = brier_score()
    # Engineered tier weights should beat always-0.5 baseline
    assert bs["raw_tier_brier"] < bs["reference_brier_uniform_0_5"]


def test_forecast_returns_confidence_band():
    # Marriage in Venus MD-AD → primary tier; band depends on Bayesian LR
    f = forecast_confidence("MARRIAGE", "Venus", "Jupiter")
    assert f["best_tier"] == "primary"
    assert f["confidence_band"] in ("HIGH", "MEDIUM", "LOW")
    # Bayesian posterior must be in unit interval if present
    if f["bayesian_posterior"] is not None:
        assert 0 <= f["bayesian_posterior"] <= 1


def test_forecast_miss_yields_weak():
    # Marriage in Mars MD-AD (not in primary or secondary) → miss
    f = forecast_confidence("MARRIAGE", "Mars", "Mars")
    # Mars is not in Marriage primary/secondary
    assert f["best_tier"] == "miss"
    assert f["confidence_band"] == "WEAK"


def test_unknown_event_returns_error():
    f = forecast_confidence("NOT_AN_EVENT", "Venus", "Jupiter")
    assert "error" in f
