"""Tests for engine.tier_refit."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.tier_refit import compare, per_lord_lr, LORDS


def test_compare_returns_classical_and_empirical():
    c = compare("MARRIAGE")
    assert "classical_primary" in c
    assert "empirical_primary" in c
    assert "lords_with_lr" in c
    assert all(l in c["lords_with_lr"] for l in LORDS)


def test_per_lord_lr_for_marriage():
    data = per_lord_lr("MARRIAGE", n_negative_per_chart=3)
    assert data["n_positive"] > 0
    assert data["n_negative"] > 0
    for lord in LORDS:
        info = data["by_lord"][lord]
        assert "p_in_event_year" in info
        assert "p_in_non_event_year" in info
        assert "LR" in info


def test_known_classical_disagreement():
    # CHILDREN_BORN: classical primary set is largely uninformative per our
    # 92-event corpus. Jupiter (the putra-karaka!) gets demoted from primary.
    c = compare("CHILDREN_BORN")
    assert "Jupiter" in c["classical_primary"]
    assert "Jupiter" not in c["empirical_primary"]
    # Saturn is not empirically promoted to primary
    assert "Saturn" not in c["empirical_primary"]
    assert "Saturn" not in c["classical_primary"]
