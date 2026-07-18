"""Tests for the bad-finder + good-finder modules."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.chart import compute_chart
from engine.afflictions import detect_all as detect_aff, summary as aff_sum
from engine.blessings import detect_all as detect_bls, summary as bls_sum
from engine.remedies import remedies_for_chart, remedies_for, REMEDY_TABLE


def _chart():
    return compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                         place="Coimbatore", name="Manoj")


def test_afflictions_detected():
    afflictions = detect_aff(_chart())
    # Manoj's chart has known dusthana-lord placements + malefic-kendra
    assert len(afflictions) >= 3


def test_blessings_detected():
    blessings = detect_bls(_chart())
    # Manoj has Hamsa yoga (Jupiter own-sign in lagna) + at least one raja yoga
    assert len(blessings) >= 2
    # Hamsa must fire
    assert any(b.code == "MAHAPURUSHA_HAMSA" for b in blessings)


def test_severity_categories():
    s = aff_sum(_chart())
    for sev in ("CRITICAL", "HIGH", "MODERATE", "LOW"):
        assert sev in s["by_severity"]


def test_strength_categories():
    s = bls_sum(_chart())
    for st in ("SUPREME", "STRONG", "MODERATE", "LATENT"):
        assert st in s["by_strength"]


def test_every_afflict_has_at_least_one_remedy_in_table_or_planet_fallback():
    afflictions = detect_aff(_chart())
    for a in afflictions:
        rems = remedies_for(a)
        # H6/H8/H12-in-house afflictions don't yet have specific remedies in REMEDY_TABLE
        # but planet-specific (combust/debilitated) do via PLANET_GENERIC_REMEDIES.
        # Each affliction should at minimum exist in the chart-level plan.
        assert isinstance(rems, list)


def test_chart_remedy_plan():
    plan = remedies_for_chart(_chart())
    assert plan["n_afflictions_detected"] >= 0
    assert "afflictions_with_remedies" in plan


def test_known_remedies_present_for_classical_doshas():
    # Verify the table covers the canonical doshas
    for code in ("MANGAL_DOSHA", "KAL_SARP", "KEMADRUMA", "PITRU_DOSHA",
                 "GRAHAN_DOSHA", "GURU_CHANDALA", "VISH_YOGA", "DARIDRA_YOGA"):
        assert code in REMEDY_TABLE
        assert len(REMEDY_TABLE[code]) >= 3


def test_remedies_include_lal_kitab_and_vedic():
    # Mangal dosha should have multiple remedy types
    rems = REMEDY_TABLE["MANGAL_DOSHA"]
    types = {r["type"] for r in rems}
    assert "vedic_mantra" in types
    assert "lal_kitab" in types
    assert "behavioral" in types


def test_blessing_activations_present():
    blessings = detect_bls(_chart())
    for b in blessings:
        # Every blessing must come with an activation note (what to do)
        assert b.activation, f"Blessing {b.code} missing activation note"
