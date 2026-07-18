"""Tests for deep verbatim extraction + verse_locator."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def test_smart_chunks_yields_chunks():
    sys.path.insert(0, "/opt/astro")
    from _workbench._deep_extract import _smart_chunks
    text = "para1 here.\n\npara2 also here.\n\n" + ("X" * 5000) + "\n\nfinal para."
    chunks = list(_smart_chunks(text, target_chars=2000))
    assert len(chunks) >= 2
    # Each chunk has its index
    for idx, c in chunks:
        assert isinstance(idx, int)
        assert isinstance(c, str)
        assert c


def test_verse_id_detection():
    sys.path.insert(0, "/opt/astro")
    from _workbench._deep_extract import _guess_verse_ids
    text = "Chapter 27, verse 45 says that... Also Ch. 6, V. 12. And 17.3."
    ids = _guess_verse_ids(text)
    assert any("27" in i and "45" in i for i in ids)


def test_verse_locator_loads():
    """Verse locator works even with empty corpus (graceful fallback)."""
    from engine.verse_locator import _load_all_deep, stats
    rules = _load_all_deep()
    s = stats()
    # Just verify the API works without crashing
    assert "n_rules_total" in s
    assert s["n_rules_total"] >= 0


def test_verse_locator_cite_exact_id():
    """If Phaladeepika_deep.json exists with verse Phaladeepika.17.1, citing
    that ID should return at least one rule."""
    from engine.verse_locator import cite, _load_all_deep
    rules = _load_all_deep()
    if not rules:
        import pytest
        pytest.skip("No deep extractions yet")
    # Find a verse_id that exists
    sample_verse_id = None
    for r in rules:
        if r.get("verse_id"):
            sample_verse_id = r["verse_id"]
            break
    if not sample_verse_id:
        import pytest
        pytest.skip("No verse_ids in extractions yet")
    results = cite(sample_verse_id)
    assert len(results) >= 1
