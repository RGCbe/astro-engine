"""Tests for engine/muhurta_verbatim.py and citation surfacing in muhurta.py."""
import datetime as dt

from engine.muhurta_verbatim import (
    _all_muhurta_rules, rules_for_activity, rules_for_dosha, stats,
)
from engine.muhurta import score_moment


def test_loads_substantial_corpus():
    rules = _all_muhurta_rules()
    assert len(rules) >= 400, f"Expected ≥400 muhurta rules, got {len(rules)}"


def test_marriage_rules_routed():
    rs = rules_for_activity("marriage", max_results=5)
    assert rs, "Expected marriage muhurta rules"
    # At least one should come from Muhurtha_Chintamani
    assert any(r.book == "Muhurtha_Chintamani" for r in rs)
    assert all("marriage" in r.categories for r in rs)


def test_travel_rules_routed():
    rs = rules_for_activity("travel", max_results=3)
    assert rs, "Expected travel muhurta rules"
    assert all("travel" in r.categories for r in rs)


def test_dosha_lookup_bana():
    """Bana dosha is mentioned in Muhurtha Chintamani 6.74 — should retrieve."""
    rs = rules_for_dosha("Bana", max_results=3)
    assert rs, "Expected at least one Bana-dosha rule"
    assert any("dosha" in r.categories for r in rs)


def test_score_moment_carries_citations():
    """score_moment should now attach verbatim citations to its result."""
    moment = dt.datetime(2026, 5, 1, 9, 30)
    s = score_moment(moment, lat=11.0, lon=77.0, tz_hours=5.5, activity="marriage")
    assert s.verbatim_citations is not None
    assert len(s.verbatim_citations) > 0
    for c in s.verbatim_citations:
        assert c["citation"] and c["text"]


def test_stats_shape():
    s = stats()
    assert s["total"] >= 400
    assert "Muhurtha_Chintamani" in s["by_book"]
    assert "marriage" in s["by_subcategory"]
