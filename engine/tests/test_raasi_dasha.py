"""Tests for engine.raasi_dasha — Jaimini Chara/Sthira/Shoola."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.raasi_dasha import (
    chara_dasha, sthira_dasha, shoola_dasha,
    SIGN_LORD, SIGN_NAMES, STHIRA_YEARS,
    current_period, kalachakra_dasha,
)


BD = dt.datetime(2000, 1, 1)


def test_sign_lord_table_covers_12():
    assert len(SIGN_LORD) == 12
    assert SIGN_LORD[0] == "Mars"      # Aries
    assert SIGN_LORD[8] == "Jupiter"   # Sagittarius
    assert SIGN_LORD[11] == "Jupiter"  # Pisces


def test_sthira_total_96_years():
    assert sum(STHIRA_YEARS.values()) == 96
    d = sthira_dasha(0, BD)
    assert sum(p.years for p in d.periods) == 96


def test_sthira_movable_signs_seven_yrs():
    # Aries(0), Cancer(3), Libra(6), Capricorn(9) all 7 yrs
    for s in (0, 3, 6, 9):
        assert STHIRA_YEARS[s] == 7


def test_shoola_total_108_years():
    d = shoola_dasha(0, birth_dt=BD)
    assert sum(p.years for p in d.periods) == 108
    assert all(p.years == 9 for p in d.periods)


def test_chara_starts_at_lagna_sign():
    d = chara_dasha(8, {  # Sagittarius lagna
        "Sun": 1, "Moon": 4, "Mars": 0, "Mercury": 0, "Jupiter": 8,
        "Venus": 2, "Saturn": 11, "Rahu": 5, "Ketu": 11,
    }, BD)
    assert d.periods[0].sign_idx == 8
    assert d.periods[0].sign_name == "Sagittarius"
    # Jupiter (Sagittarius lord) is in Sagittarius itself → 12 yrs
    assert d.periods[0].years == 12


def test_chara_savya_apasavya_directions():
    # Aries (savya) — Mars in Taurus (sign 1)
    # Forward count: 1 - 0 = 1 yr
    d = chara_dasha(0, {
        "Sun": 0, "Moon": 0, "Mars": 1, "Mercury": 0, "Jupiter": 0,
        "Venus": 0, "Saturn": 0, "Rahu": 0, "Ketu": 0,
    }, BD)
    aries = next(p for p in d.periods if p.sign_idx == 0)
    assert aries.years == 1


def test_current_period_lookup():
    d = sthira_dasha(0, BD)  # Aries lagna
    # Aries → 7 yrs, ending 2007
    p = current_period(d, dt.datetime(2003, 6, 1))
    assert p is not None
    assert p.sign_idx == 0


def test_periods_are_contiguous():
    d = sthira_dasha(8, BD)
    for i in range(len(d.periods) - 1):
        assert d.periods[i].end == d.periods[i + 1].start


def test_kalachakra_raises_not_implemented():
    import pytest
    with pytest.raises(NotImplementedError):
        kalachakra_dasha()
