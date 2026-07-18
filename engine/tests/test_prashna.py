"""Tests for engine.prashna."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.prashna import answer, cast, ruling_planets, QUESTION_HOUSE


def test_question_house_map_covers_topics():
    for topic in ("career", "marriage", "wealth", "children", "health"):
        assert topic in QUESTION_HOUSE


def test_cast_produces_chart():
    c = cast(dt.datetime(2026, 4, 26, 14, 30), 11.01, 76.96, 5.5)
    assert 0 <= c.lagna_sign <= 11
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        assert p in c.positions


def test_ruling_planets_returns_list():
    c = cast(dt.datetime(2026, 4, 26, 14, 30), 11.01, 76.96, 5.5)
    rps = ruling_planets(c)
    # 6 candidates collapsed via dedup — minimum 3 distinct
    assert len(rps) >= 3
    assert all(isinstance(r, str) for r in rps)


def test_answer_career():
    ans = answer(
        question_dt=dt.datetime(2026, 4, 26, 14, 30),
        lat=11.01, lon=76.96, tz_hours=5.5,
        topic="career",
    )
    assert ans["house_questioned"] == 10
    assert ans["kp_verdict"]["verdict"] in (
        "STRONG YES", "YES", "WEAK YES", "NO", "INDETERMINATE"
    )


def test_answer_unknown_topic_raises():
    import pytest
    with pytest.raises(ValueError):
        answer(
            question_dt=dt.datetime(2026, 4, 26, 14, 30),
            lat=11.01, lon=76.96, tz_hours=5.5,
            topic="will_aliens_invade",
        )
