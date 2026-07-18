"""Tests for engine.cross_check vs PyJHora."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.cross_check import cross_check_chart, _try_import_pyjhora


def test_pyjhora_importable():
    pyj, err = _try_import_pyjhora()
    if pyj is None:
        # PyJHora deps may be missing in CI — skip rather than fail
        import pytest
        pytest.skip(f"PyJHora unavailable: {err}")
    assert pyj is not None


def test_cross_check_passes_on_manoj():
    pyj, err = _try_import_pyjhora()
    if pyj is None:
        import pytest
        pytest.skip(f"PyJHora unavailable: {err}")
    r = cross_check_chart(
        name="Manoj", date="1996-05-25", time="20:25", tz_hours=5.5,
        lat=11.0055, lon=76.9661,
    )
    # All 10 fields (lagna + 9 planets) should pass
    assert r.passed, f"Cross-check failed: {r.summary()}"


def test_lagna_within_001_tolerance():
    pyj, err = _try_import_pyjhora()
    if pyj is None:
        import pytest
        pytest.skip(f"PyJHora unavailable: {err}")
    r = cross_check_chart(
        name="Indira", date="1917-11-19", time="23:11", tz_hours=5.5,
        lat=25.435, lon=81.846,
    )
    lagna_field = next(f for f in r.fields if f.field == "lagna_lon")
    assert lagna_field.delta < 0.01
