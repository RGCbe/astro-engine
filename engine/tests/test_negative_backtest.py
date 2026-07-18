"""Tests for engine.negative_backtest."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.negative_backtest import run_negative_backtest, _deterministic_seed


def test_deterministic_seed_stable():
    assert _deterministic_seed("hello") == _deterministic_seed("hello")
    assert _deterministic_seed("hello") != _deterministic_seed("world")


def test_negative_backtest_produces_lr():
    r = run_negative_backtest(n_samples_per_event=3)
    assert r["n_charts"] >= 20
    by_evt = r["by_event_type"]
    assert "MARRIAGE" in by_evt
    assert by_evt["MARRIAGE"]["LR_primary"] is not None
    assert by_evt["MARRIAGE"]["P_primary_given_event"] >= 0
    assert by_evt["MARRIAGE"]["P_primary_given_no_event"] >= 0


def test_posterior_in_unit_interval():
    r = run_negative_backtest(n_samples_per_event=3)
    for evt, b in r["by_event_type"].items():
        post = b["posterior_event_given_primary"]
        if post is not None:
            assert 0 <= post <= 1, f"{evt} posterior {post} out of [0,1]"
