"""Tests for the Nabhasa-yoga catalogue (engine/yogas_nabhasa.py)."""
from engine.chart import compute_chart
from engine.yogas_nabhasa import (
    detect_all_nabhasa, detect_sankhya_yogas, detect_kamala_yoga,
    detect_samudra_yoga, detect_gada_yoga, _seven_contiguous_from,
)


def _manoj_chart():
    return compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                         place="Coimbatore")


def test_seven_contiguous():
    assert _seven_contiguous_from(1) == {1, 2, 3, 4, 5, 6, 7}
    assert _seven_contiguous_from(7) == {7, 8, 9, 10, 11, 12, 1}
    assert _seven_contiguous_from(10) == {10, 11, 12, 1, 2, 3, 4}


def test_manoj_damini_fires():
    """Manoj's chart has 7 grahas in 6 distinct signs → Damini."""
    nb = detect_all_nabhasa(_manoj_chart())
    names = [y.name for y in nb]
    assert any("Damini" in n for n in names), f"Expected Damini, got {names}"


def test_sankhya_table_only_3_to_7():
    """Sankhya only fires for 3..7 distinct signs (Gola/Yuga handled in extended)."""
    from engine.yogas_nabhasa import SANKHYA_TABLE
    assert set(SANKHYA_TABLE.keys()) == {3, 4, 5, 6, 7}


def test_no_double_fire():
    """A chart should not get two Sankhya yogas at once."""
    nb = detect_sankhya_yogas(_manoj_chart())
    assert len(nb) <= 1


def test_aggregator_returns_list():
    nb = detect_all_nabhasa(_manoj_chart())
    assert isinstance(nb, list)
    for y in nb:
        assert y.code and y.name and y.valence in ("GOOD", "BAD", "MIXED")
        assert y.classical_source
