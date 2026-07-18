"""Tests for engine.transit_conditioned."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.transit_conditioned import (
    _transit_factors_at, EVENT_TRANSIT_PREDICTORS,
    transit_conditioned_backtest,
)


def test_transit_factors_returns_all_keys():
    tf = _transit_factors_at(
        dt.datetime(2026, 4, 26),
        natal_moon_lon=131.18,
        natal_lagna_lon=245.6,
        natal_saturn_lon=341.23,
        natal_jupiter_lon=263.16,
        natal_seventh_sign=2,
    )
    expected = {"sade_sati", "saturn_return", "jupiter_in_7th_sign",
                "jupiter_trikona_from_moon", "rahu_on_lagna", "rahu_on_moon",
                "ketu_on_lagna", "ketu_on_moon"}
    assert set(tf) == expected
    for v in tf.values():
        assert isinstance(v, bool)


def test_event_predictors_cover_known_events():
    for e in ("MARRIAGE", "CHILDREN_BORN", "DEATH", "DIVORCE"):
        assert e in EVENT_TRANSIT_PREDICTORS
        assert EVENT_TRANSIT_PREDICTORS[e]


def test_transit_conditioned_backtest_runs():
    # Use small n_negative to keep test fast
    r = transit_conditioned_backtest(n_negative_per_chart=2)
    assert "MARRIAGE" in r["by_event_type"]
    b = r["by_event_type"]["MARRIAGE"]
    assert "LR_dasha_only" in b
    assert "LR_dasha_AND_transit" in b
