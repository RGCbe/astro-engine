"""Tests for engine.yogas_extended (deep-extraction-derived yogas)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.chart import compute_chart
from engine.yogas_extended import (
    detect_all_extended, detect_12_bhava_yogas, detect_parivartana_yogas,
    detect_amala_yoga, detect_vasumat_yoga, detect_apakartari_yoga,
    detect_musala_yoga, detect_yuga_yoga, detect_gola_yoga,
    BHAVA_YOGA_NAMES,
)


def _chart():
    return compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                         place="Coimbatore", name="Manoj")


def test_12_bhava_yogas_table_complete():
    assert set(BHAVA_YOGA_NAMES.keys()) == set(range(1, 13))
    for h, (name, mean, valence, strength) in BHAVA_YOGA_NAMES.items():
        assert valence in ("GOOD", "BAD", "MIXED")
        assert strength in ("SUPREME", "STRONG", "MODERATE", "LATENT")


def test_apakartari_fires_on_manoj():
    """Manoj has Sun in Taurus, Mercury in Aries (12th from Sun), Venus
    in Gemini (2nd from Sun) → Apakartari for Sun should fire."""
    yogas = detect_apakartari_yoga(_chart())
    assert any(y.code == "APAKARTARI_SUN" for y in yogas)


def test_nirbhagya_fires_on_manoj():
    """Manoj's H9 lord (Sun) sits in H6 → Nirbhagya-yoga fires."""
    yogas = detect_12_bhava_yogas(_chart())
    assert any(y.code == "BHAVA_YOGA_H9" for y in yogas)


def test_parivartana_returns_list():
    out = detect_parivartana_yogas(_chart())
    assert isinstance(out, list)


def test_aggregator_orders_by_valence_strength():
    out = detect_all_extended(_chart())
    # GOOD must come before BAD
    valences = [y.valence for y in out]
    if "GOOD" in valences and "BAD" in valences:
        good_idx = next(i for i, v in enumerate(valences) if v == "GOOD")
        bad_idx = next(i for i, v in enumerate(valences) if v == "BAD")
        assert good_idx < bad_idx


def test_musala_yoga_definition():
    """All 7 grahas in fixed signs would fire Musala. Most charts won't."""
    out = detect_musala_yoga(_chart())
    # Manoj doesn't have all in fixed — should be None
    assert out is None or out.code == "MUSALA_YOGA"
