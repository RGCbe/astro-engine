"""Tests for engine.muhurta."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.muhurta import score_moment, find_windows, ACTIVITY_RULES


def test_known_activities_have_rules():
    for act in ("marriage", "business_start", "travel", "naming_ceremony",
                "education_start", "general"):
        assert act in ACTIVITY_RULES
        rules = ACTIVITY_RULES[act]
        assert "good_nakshatras" in rules
        assert "bad_nakshatras" in rules


def test_score_moment_returns_object():
    s = score_moment(dt.datetime(2026, 4, 29, 10, 0), 11.01, 76.96, 5.5, "marriage")
    assert 0 <= s.score <= 100
    assert s.verdict in ("EXCELLENT", "GOOD", "ACCEPTABLE", "POOR", "REJECTED")


def test_hard_reject_zeroes_score():
    # Tuesday is forbidden for marriage — should reject
    # Apr 28 2026 is a Tuesday
    s = score_moment(dt.datetime(2026, 4, 28, 10, 0), 11.01, 76.96, 5.5, "marriage")
    if s.rejected_reasons:
        assert s.score == 0
        assert s.verdict == "REJECTED"


def test_find_windows_returns_top_n():
    best = find_windows(
        start=dt.datetime(2026, 4, 27, 6, 0),
        end=dt.datetime(2026, 5, 5, 22, 0),
        lat=11.01, lon=76.96, tz_hours=5.5,
        activity="marriage",
        step_minutes=240,
        top_n=5,
    )
    assert len(best) <= 5
    if best:
        assert all(b.score > 0 for b in best)
        # Sorted descending
        for i in range(len(best) - 1):
            assert best[i].score >= best[i+1].score
