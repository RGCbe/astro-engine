"""Tests for engine.lal_kitab."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.lal_kitab import (
    LAL_KITAB_PAKKA_GHAR,
    LAL_KITAB_ASPECTS,
    RIN_PATTERNS,
    lal_kitab_chart,
    karmic_debts,
    closed_houses,
    _planet_house,
    _aspected_houses,
)


def test_pakka_ghar_covers_all_planets():
    expected = {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                "Venus", "Saturn", "Rahu", "Ketu"}
    assert set(LAL_KITAB_PAKKA_GHAR) == expected


def test_aspects_table_covers_all_planets():
    assert set(LAL_KITAB_ASPECTS) == set(LAL_KITAB_PAKKA_GHAR)
    # Saturn aspects 3, 7, 10 (drishti)
    assert LAL_KITAB_ASPECTS["Saturn"] == {3, 7, 10}
    # Jupiter aspects 5, 7, 9
    assert LAL_KITAB_ASPECTS["Jupiter"] == {5, 7, 9}
    # Mars aspects 4, 7, 8
    assert LAL_KITAB_ASPECTS["Mars"] == {4, 7, 8}


def test_planet_house_aries_one():
    # Aries = sign 0, house 1
    assert _planet_house(0.0) == 1
    assert _planet_house(29.99) == 1
    assert _planet_house(30.0) == 2     # Taurus
    assert _planet_house(180.0) == 7    # Libra
    assert _planet_house(359.99) == 12  # Pisces


def test_aspect_offset_wraps():
    # Saturn in house 12 aspects 3 (offset 3): (12-1+2)%12+1 = 2 — wait
    # offset 3 means count 3 forward, so from H12 → H2, H6, H9
    aspects = _aspected_houses("Saturn", 12)
    assert aspects == {2, 6, 9}


def test_seven_rins_defined():
    assert len(RIN_PATTERNS) == 7
    expected = {"Pitra Rin", "Matra Rin", "Bhratra Rin", "Stree Rin", "Putra Rin", "Nyaya Rin", "Atma Rin"}
    assert {r["rin"] for r in RIN_PATTERNS} == expected


def test_pitra_rin_fires_when_rahu_in_9():
    # Rahu at 240° = Sagittarius = H9
    plon = {"Sun": 0.0, "Moon": 90.0, "Mars": 60.0, "Mercury": 30.0,
            "Jupiter": 120.0, "Venus": 180.0, "Saturn": 300.0,
            "Rahu": 240.0, "Ketu": 60.0}
    lk = lal_kitab_chart(plon)
    rins = [d["rin"] for d in lk.karmic_debts]
    assert "Pitra Rin" in rins


def test_putra_rin_fires_when_rahu_in_5():
    # Rahu at 120° = Leo = H5
    plon = {"Sun": 0.0, "Moon": 90.0, "Mars": 60.0, "Mercury": 30.0,
            "Jupiter": 200.0, "Venus": 180.0, "Saturn": 300.0,
            "Rahu": 120.0, "Ketu": 300.0}
    lk = lal_kitab_chart(plon)
    rins = [d["rin"] for d in lk.karmic_debts]
    assert "Putra Rin" in rins


def test_pakka_ghar_detection():
    # Sun in Aries (H1) is in its pakka ghar
    plon = {"Sun": 15.0, "Moon": 90.0, "Mars": 60.0, "Mercury": 30.0,
            "Jupiter": 30.0, "Venus": 180.0, "Saturn": 270.0,
            "Rahu": 330.0, "Ketu": 150.0}
    lk = lal_kitab_chart(plon)
    sun = next(p for p in lk.placements if p.planet == "Sun")
    assert sun.in_pakka is True
    assert sun.house == 1


def test_remedies_present():
    plon = {"Sun": 15.0, "Moon": 90.0, "Mars": 60.0, "Mercury": 30.0,
            "Jupiter": 200.0, "Venus": 180.0, "Saturn": 300.0,
            "Rahu": 240.0, "Ketu": 60.0}
    lk = lal_kitab_chart(plon)
    # Rahu in 9 fires Pitra Rin → at least one remedy
    assert len(lk.remedies) >= 1
