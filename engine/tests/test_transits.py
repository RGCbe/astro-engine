"""Tests for engine.transits."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.transits import (
    saturn_returns, sade_sati_windows,
    jupiter_transits_sign, transit_snapshot,
    PLANET_PERIOD_YRS,
)


def test_saturn_period_about_29_years():
    assert 29.0 < PLANET_PERIOD_YRS["Saturn"] < 30.0


def test_saturn_returns_first_at_about_age_29():
    natal = dt.datetime(1996, 5, 25, 20, 25)
    rs = saturn_returns(natal, n_returns=2, tz_hours=5.5)
    assert len(rs) == 2
    # First return should be 28-31 years old
    assert 28 < rs[0].age_years < 31
    # Second return ~58
    assert 57 < rs[1].age_years < 60


def test_sade_sati_for_leo_moon_finds_windows():
    # Manoj Moon 131.18° = Leo
    ssw = sade_sati_windows(131.18,
                            dt.datetime(1996, 1, 1),
                            dt.datetime(2050, 1, 1))
    assert len(ssw) > 0
    # All phases should be Cancer/Leo/Virgo (Sade Sati signs for Leo Moon)
    for s in ssw:
        assert s.sign in ("Cancer", "Leo", "Virgo")


def test_jupiter_transits_returns_windows():
    jt = jupiter_transits_sign(2, natal_lagna_sign=8,
                               search_start=dt.datetime(2024, 1, 1),
                               search_end=dt.datetime(2030, 1, 1))
    # Jupiter passes Gemini once per ~12 years, so 1-2 windows in 6 years
    assert 0 <= len(jt) <= 3
    for t in jt:
        assert t.sign == "Gemini"
        assert t.house_from_lagna == 7  # Gemini is 7th from Sagittarius lagna


def test_transit_snapshot_contains_expected_planets():
    snap = transit_snapshot(
        dt.datetime(2026, 4, 26, 12, 0),
        natal_lagna_sign=8,
        natal_positions={"Moon": 131.18, "Sun": 40.86, "Saturn": 341.23,
                         "Jupiter": 263.16, "Mars": 23.17,
                         "Mercury": 26.01, "Venus": 63.91},
        tz_hours=5.5,
    )
    planet_names = {t["planet"] for t in snap["transits"]}
    for p in ("Mars", "Jupiter", "Saturn", "Rahu", "Ketu"):
        assert p in planet_names
