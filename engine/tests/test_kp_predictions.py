"""Tests for engine/kp_predictions.py — verbatim KP retrieval."""
from engine.chart import compute_chart
from engine.kp_predictions import (
    _all_kp_rules, predictions_for_house, predictions_for_planet,
    predictions_for_sublord, predictions_for_chart, stats,
)


def test_loads_substantial_kp_corpus():
    rules = _all_kp_rules()
    assert len(rules) >= 1500, f"Expected ≥1500 KP rules, got {len(rules)}"


def test_house_routing_career():
    rs = predictions_for_house(10, max_results=5)
    assert rs, "Expected H10 KP predictions"
    cats = {c.lower() for r in rs for c in r.categories}
    assert "career" in cats


def test_house_routing_marriage():
    rs = predictions_for_house(7, max_results=3)
    assert rs
    cats = {c.lower() for r in rs for c in r.categories}
    assert "marriage" in cats


def test_house_routing_dusthana_8():
    rs = predictions_for_house(8, max_results=3)
    assert rs
    cats = {c.lower() for r in rs for c in r.categories}
    assert any(c in cats for c in ("longevity", "death", "karmic"))


def test_planet_lookup_saturn():
    rs = predictions_for_planet("Saturn", max_results=3)
    assert rs
    assert all("Saturn" in r.planets for r in rs)


def test_sublord_lookup():
    rs = predictions_for_sublord("Jupiter", max_results=3)
    assert rs, "Expected at least one sub-lord rule mentioning Jupiter"


def test_chart_predictions_cover_houses():
    c = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                      place="Coimbatore")
    rows = predictions_for_chart(c, max_per_house=1)
    assert rows
    houses_seen = {row["house"] for row in rows}
    # Every cusp 1..12 should pull at least one rule from its domain
    assert houses_seen == set(range(1, 13))


def test_stats_shape():
    s = stats()
    assert s["total"] >= 1500
    assert "rule" in s["by_type"]
