"""Tests for engine.tajik."""
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.tajik import (
    annual_chart, datetime_to_jd, muntha, sahams,
)


def test_muntha_progresses_one_sign_per_year():
    # Sagittarius lagna (sign 8), age 30 → Gemini (8+30=38, %12=2)
    m = muntha(8, 30)
    assert m["sign_idx"] == 2
    assert m["sign_name"] == "Gemini"


def test_annual_chart_basic():
    natal_dt = dt.datetime(1996, 5, 25, 20, 25)
    natal_jd = datetime_to_jd(natal_dt, tz_hours=5.5)
    ac = annual_chart(natal_jd, natal_lagna_sign=8, age_years=30,
                      lat=11.01, lon=76.96, tz_hours=5.5)
    assert ac.age_years == 30
    assert ac.muntha_sign == 2  # Gemini at age 30 from Sagittarius lagna
    assert ac.varshesha in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                            "Venus", "Saturn", "Mercury")
    # Solar return is within 1 day of birthday in target year
    assert abs((ac.return_dt - dt.datetime(2026, 5, 26)).days) <= 1


def test_sahams_present():
    natal_dt = dt.datetime(1996, 5, 25, 20, 25)
    natal_jd = datetime_to_jd(natal_dt, tz_hours=5.5)
    ac = annual_chart(natal_jd, 8, 30, 11.01, 76.96, 5.5)
    s = ac.sahams
    for required in ("Punya", "Vidya", "Yashas", "Vivaha", "Putra"):
        assert required in s
        assert 0 <= s[required]["longitude"] < 360
