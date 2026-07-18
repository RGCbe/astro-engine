"""Tests for engine.chart_relative."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.chart import compute_chart
from engine.chart_relative import (
    chart_factors, chart_relative_lords, score_event_relative,
)


def _chart():
    return compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                         place="Coimbatore", name="Manoj")


def test_chart_factors_built():
    f = chart_factors(_chart())
    # Sagittarius lagna → Jupiter
    assert f.lagna_lord == "Jupiter"
    # 7th from Sagittarius is Gemini → Mercury
    assert f.h7_lord == "Mercury"
    # 10th from Sagittarius is Virgo → Mercury
    assert f.h10_lord == "Mercury"
    # Karakas should be assigned
    assert f.AK in {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                    "Venus", "Saturn", "Rahu"}


def test_chart_relative_lords_known_event():
    sets = chart_relative_lords(_chart(), "MARRIAGE")
    assert "Venus" in sets["primary"]
    assert sets["primary"]   # non-empty
    assert sets["secondary"]


def test_score_event_returns_tier():
    r = score_event_relative(_chart(), "MARRIAGE", "Venus", "Jupiter")
    assert r["best_tier"] in ("primary", "secondary", "miss")
    assert r["primary_set"]
    assert r["secondary_set"]
