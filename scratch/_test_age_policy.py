#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for engine/event_age_policy.py (Manoj chart)."""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from engine.event_age_policy import (
    age_at,
    classify_age_fit,
    is_age_appropriate,
    filter_bands_for_age,
    band_fits_puthi_window,
    client_age_label,
)

CHART = json.loads((ROOT / "charts" / "manoj_chart.json").read_text(encoding="utf-8"))


def test_age_at_birth():
    b = CHART["birth"]
    birth = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    assert abs(age_at(CHART, birth)) < 0.01


def test_marriage_age_4_unlikely():
    assert classify_age_fit(4, "marriage", 5) == "unlikely"
    assert not is_age_appropriate("marriage", 4)


def test_marriage_age_16_early_exception():
    assert classify_age_fit(16, "marriage", 2) == "early_exception"
    assert is_age_appropriate("marriage", 16)


def test_marriage_age_12_borderline():
    assert classify_age_fit(12, "marriage", 3) == "unlikely"
    assert classify_age_fit(12, "marriage", 4) == "early_exception"


def test_marriage_age_25_typical():
    assert classify_age_fit(25, "marriage", 2) == "typical"


def test_fake_marriage_band_age_4_filtered():
    b = CHART["birth"]
    birth = dt.datetime(b["year"], b["month"], b["day"])
    fake = {
        "category": "marriage",
        "event": "Marriage / engagement / serious committed relationship",
        "window_start": birth + dt.timedelta(days=int(4 * 365.25)),
        "window_end": birth + dt.timedelta(days=int(5 * 365.25)),
        "severity": 5,
    }
    out = filter_bands_for_age(CHART, [fake])
    assert out == []
    assert fake["age_fit"] == "unlikely"


def test_marriage_band_2008_manoj_early_if_strong():
    ws = dt.datetime(2008, 6, 3)
    we = dt.datetime(2011, 7, 2)
    assert age_at(CHART, ws) < 18
    weak = {
        "category": "marriage",
        "event": "Marriage / engagement / serious committed relationship",
        "window_start": ws,
        "window_end": we,
        "severity": 2,
    }
    assert filter_bands_for_age(CHART, [weak]) == []
    strong = {**weak, "severity": 5, "why": ["7L active", "Venus dasha", "D9 support"]}
    out = filter_bands_for_age(CHART, [strong])
    assert len(out) == 1
    assert out[0]["age_fit"] == "early_exception"


def test_client_age_label_early():
    band = {"age_fit": "early_exception", "age_at_start": 16.0}
    assert "Early (age 16)" in client_age_label(band, "en")
    assert client_age_label({"age_fit": "typical"}, "en") is None


def test_puthi_ketu_saturn_no_marriage_overlap():
    b = CHART["birth"]
    birth = dt.datetime(b["year"], b["month"], b["day"])
    puthi_start = birth
    puthi_end = birth + dt.timedelta(days=50)
    band = {
        "category": "marriage",
        "window_start": dt.datetime(2008, 6, 3),
        "window_end": dt.datetime(2011, 7, 2),
        "severity": 5,
        "age_fit": "early_exception",
    }
    assert not band_fits_puthi_window(CHART, band, puthi_start, puthi_end)


def test_father_ok_in_childhood():
    assert classify_age_fit(0.5, "father", 0) == "typical"
    assert classify_age_fit(4, "father", 0) == "typical"


def test_career_age_4_unlikely():
    assert classify_age_fit(4, "career", 5) == "unlikely"
    assert classify_age_fit(16, "career_breakthrough", 3) == "typical"


def test_retirement_absurd_min():
    assert classify_age_fit(20, "retirement", 5) == "unlikely"
    assert classify_age_fit(50, "retirement", 3) == "typical"


if __name__ == "__main__":
    tests = [
        test_age_at_birth,
        test_marriage_age_4_unlikely,
        test_marriage_age_16_early_exception,
        test_marriage_age_12_borderline,
        test_marriage_age_25_typical,
        test_fake_marriage_band_age_4_filtered,
        test_marriage_band_2008_manoj_early_if_strong,
        test_client_age_label_early,
        test_puthi_ketu_saturn_no_marriage_overlap,
        test_father_ok_in_childhood,
        test_career_age_4_unlikely,
        test_retirement_absurd_min,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"OK  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
    sys.exit(1 if failed else 0)
