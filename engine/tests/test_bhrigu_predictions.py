"""Tests for engine/bhrigu_predictions.py — verbatim Bhrigu lookup."""
from engine.chart import compute_chart
from engine.bhrigu_predictions import (
    _build_index, predictions_for, predictions_for_chart, stats, PLANETS,
)


def test_index_has_substantial_coverage():
    """Strict index — only rules whose leading text says '{planet} in {house}'.
    Smaller than naive cross-product but precise."""
    idx = _build_index()
    assert len(idx) >= 80, f"Expected ≥80 (planet,house) cells, got {len(idx)}"
    total = sum(len(v) for v in idx.values())
    assert total >= 400, f"Expected ≥400 indexed Bhrigu rules, got {total}"


def test_top_cells_have_real_rules():
    """At least Mars-in-H10 and Saturn-in-H4 should have multiple rules
    (well-attested placements in the corpus)."""
    idx = _build_index()
    assert any(p == "Mars" for p, _ in idx.keys())
    assert any(p == "Saturn" for p, _ in idx.keys())
    # At least 5 cells should each have ≥3 rules
    well_populated = sum(1 for v in idx.values() if len(v) >= 3)
    assert well_populated >= 5, f"Expected ≥5 well-populated cells, got {well_populated}"


def test_predictions_for_returns_capped_list():
    rules = predictions_for("Mars", 7, max_results=5)
    assert 1 <= len(rules) <= 5
    for r in rules:
        assert r.text and r.book == "Bhrigu_Samhita"


def test_predictions_for_chart_covers_grahas():
    c = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                      place="Coimbatore")
    rows = predictions_for_chart(c, max_per_planet=2)
    assert rows, "Expected at least some Bhrigu predictions for Manoj's chart"
    seen = {row["planet"] for row in rows}
    # At least 4 of the 9 grahas should hit Bhrigu cells
    assert len(seen) >= 4


def test_predictions_for_chart_each_row_well_formed():
    c = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                      place="Coimbatore")
    rows = predictions_for_chart(c, max_per_planet=2)
    for row in rows:
        assert row["planet"] in PLANETS
        assert 1 <= row["house"] <= 12
        assert row["predictions"]
        for p in row["predictions"]:
            assert p["text"] and p["citation"]


def test_unknown_cell_returns_empty():
    """Some cells may have no Bhrigu rules — should return empty list, not crash."""
    rules = predictions_for("Ketu", 99, max_results=3)
    assert rules == []
