"""Tests for engine/remedies_verbatim.py — the verbatim-citation remedy layer."""
from engine.remedies_verbatim import (
    _all_remedies, remedies_for_planet, remedies_in_category,
    remedies_for_affliction_code, stats,
)


def test_loads_30_remedies():
    rems = _all_remedies()
    assert len(rems) >= 25, f"Expected ~30 remedies, got {len(rems)}"


def test_planet_lookups_have_bhrigu_donations():
    """All 9 grahas should have at least one verbatim donation remedy."""
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"):
        rs = remedies_for_planet(p)
        assert rs, f"No verbatim remedy found for {p}"
        assert any("Bhrigu" in r.book for r in rs), f"No Bhrigu remedy for {p}"


def test_category_marriage_lookup():
    rs = remedies_in_category("marriage")
    assert rs, "No marriage-category remedies indexed"
    assert any("Muhurtha_Chintamani" in r.book or "Phaladeepika" in r.book for r in rs)


def test_affliction_routing_combust_planet():
    """COMBUST_SATURN should surface Saturn-tagged remedies."""
    rs = remedies_for_affliction_code("COMBUST_SATURN", ["Saturn"])
    assert rs, "Expected at least one Saturn remedy"
    assert all("Saturn" in r.planets or "remedy" in [c.lower() for c in r.categories]
               for r in rs)


def test_affliction_routing_marriage_dosha():
    """MANGAL_DOSHA should pull marriage-category remedies even with no planet."""
    rs = remedies_for_affliction_code("MANGAL_DOSHA", [])
    cats = {c for r in rs for c in r.categories}
    assert "marriage" in cats, f"Expected marriage category, got {cats}"


def test_dedup_no_duplicates():
    """Affliction routing must not return the same remedy twice."""
    rs = remedies_for_affliction_code("COMBUST_SUN", ["Sun"])
    seen = {(r.book, r.verse_id, r.text[:60]) for r in rs}
    assert len(seen) == len(rs)


def test_stats_shape():
    s = stats()
    assert s["total"] >= 25
    assert "Bhrigu_Samhita" in s["by_book"]
    assert all(p in s["by_planet"] for p in ("Sun", "Moon", "Saturn"))


def test_cite_format():
    rs = remedies_for_planet("Saturn")
    phaladeepika_remedies = [r for r in rs if r.book == "Phaladeepika"]
    if phaladeepika_remedies:
        cite = phaladeepika_remedies[0].cite()
        assert cite.startswith("Phaladeepika")
