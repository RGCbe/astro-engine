"""Tests for engine.kalachakra."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.kalachakra import (
    KALACHAKRA_RASI_YEARS, PADA_RASI_TABLE, kalachakra,
)


def test_rasi_years_present_for_all_12():
    assert set(KALACHAKRA_RASI_YEARS) == set(range(12))


def test_pada_table_has_108_entries():
    assert len(PADA_RASI_TABLE) == 108


def test_pada_directions_only_savya_or_apasavya():
    for r, d in PADA_RASI_TABLE:
        assert d in ("savya", "apasavya")
        assert 0 <= r <= 11


def test_kalachakra_returns_periods():
    kc = kalachakra(131.184, dt.datetime(1996, 5, 25, 20, 25))
    assert len(kc.periods) == 24
    assert kc.validation_pending is True
    assert "BPHS Ch.49" in kc.tradition or "Parashara" in kc.tradition


def test_kalachakra_unknown_tradition_raises():
    import pytest
    with pytest.raises(NotImplementedError):
        kalachakra(0.0, dt.datetime(2000, 1, 1), tradition="rath")


def test_caveat_present():
    kc = kalachakra(131.184, dt.datetime(1996, 5, 25))
    assert kc.caveat
    assert "validate" in kc.caveat.lower() or "tradition" in kc.caveat.lower()
