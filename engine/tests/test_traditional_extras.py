"""Validate traditional_extras against the AstroSign print for Manoj
(birth 1996-05-25 20:25, Coimbatore 11.25N 77.1167E, tz 5.5).

Ground truth from the 2003 Logic-Vision booklet:
  - Sunrise 6:00:56, Sunset 6:35:54
  - Janma nakshatra Magha -> gana Rakshasa, yoni Rat (Male)
  - Chandrashtama: Purva Bhadrapada, Uttara Bhadrapada, Revati
  - Sripati bhava-1: start 231°38', mid 245°45', end 261°38'
"""
import pytest

from engine.chart_builder import build_sidereal_chart
from engine.traditional_extras import (
    nakshatra_reference,
    chandrashtama_nakshatras,
    sripati_bhava_cusps,
    compute_mc_sidereal,
    traditional_extras,
)


@pytest.fixture(scope="module")
def manoj_core():
    return build_sidereal_chart(1996, 5, 25, "20:25", 11.25, 77.1167, 5.5)


def test_nakshatra_reference_magha():
    ref = nakshatra_reference("Magha")
    assert ref["gana"] == "Rakshasa"
    assert ref["yoni"] == "Rat"
    assert ref["yoni_gender"] == "Male"
    assert ref["tree"] and "Banyan" in ref["tree"]


def test_chandrashtama_magha():
    got = chandrashtama_nakshatras("Magha")
    assert got == ["Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]


def test_sripati_cusps_match_print(manoj_core):
    mc = compute_mc_sidereal(manoj_core["jd"], 11.25, 77.1167)
    cusps = sripati_bhava_cusps(manoj_core["asc_sid"], mc)
    h1 = cusps[0]
    # AstroSign print: 231°38' / 245°45' / 261°38' (allow 0.2° for MC/ayanamsa)
    assert abs((h1["start"] - 231.64)) < 0.2
    assert abs((h1["mid"] - 245.76)) < 0.2
    assert abs((h1["end"] - 261.64)) < 0.2
    # 12 houses, monotonic wrap, each ~unequal
    assert len(cusps) == 12
    assert cusps[6]["mid_dms"].startswith("Mithunam")  # 7th mid ~65.7 (Gemini)


def test_traditional_extras_block(manoj_core):
    manoj_core.setdefault("birth", {"lat": 11.25, "lon": 77.1167, "tz": 5.5,
                                     "year": 1996, "month": 5, "day": 25})
    block = traditional_extras(manoj_core)
    assert block["nakshatra_reference"]["gana"] == "Rakshasa"
    assert len(block["bhava_cusps"]) == 12
    st = block.get("sun_times", {})
    assert st.get("sunrise", "").startswith("6:0") or st.get("sunrise", "").startswith("06:0")
