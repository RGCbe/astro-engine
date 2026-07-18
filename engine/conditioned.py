"""
Affliction- and blessing-conditioned forecast adjustment.

Per audit Tier 2: chart-static signals (Mangal Dosha, Stree Rin, Hamsa
Yoga, vargottama, etc.) currently DON'T influence event LR. This module
adjusts the ensemble LR by chart-static factors empirically calibrated
on the 61-chart corpus.

Adjustment formulas:
    For each event type, identify which afflictions/blessings have empirical
    bad-rate or good-rate lift (from affliction_backtest / blessing_backtest).
    Multiplicatively combine with the ensemble LR:
        adjusted_LR = ensemble_LR × Π (affliction_modifier_i)
                                × Π (blessing_modifier_j)
                                × Π (varga_modifier_k)
                                × Π (rin_modifier_l)

Per truth directive: each modifier is reported transparently, never
folded silently.
"""
from __future__ import annotations

# Empirical event-class ↔ affliction modifiers
# Built from observed correlations on the 61-chart corpus + classical theory.
# A modifier of 0.7 means "this affliction reduces the event LR by 30%".

AFFLICTION_EVENT_MODIFIERS: dict[str, dict[str, float]] = {
    # Affliction code → {event_type: modifier}
    "MANGAL_DOSHA": {
        "MARRIAGE": 0.65, "DIVORCE": 1.4,
    },
    "RIN_STREE_RIN": {
        "MARRIAGE": 0.7, "DIVORCE": 1.3,
    },
    "RIN_PUTRA_RIN": {
        "CHILDREN_BORN": 0.55,
    },
    "RIN_PITRA_RIN": {
        "POLITICAL_OFFICE": 0.85, "AWARD": 0.85, "DEATH": 1.1,
    },
    "RIN_MATRA_RIN": {
        "HEALTH_CRISIS": 1.2,
    },
    "RIN_BHRATRA_RIN": {
        "MAJOR_LOSS": 1.15,
    },
    "KAL_SARP": {
        "CAREER_PEAK": 0.75, "CAREER_START": 0.85,
        "MAJOR_LOSS": 1.25, "EXILE": 1.2,
    },
    "KEMADRUMA": {
        "MARRIAGE": 0.8, "MAJOR_LOSS": 1.15, "HEALTH_CRISIS": 1.15,
    },
    "GRAHAN_DOSHA": {
        "HEALTH_CRISIS": 1.25, "MAJOR_LOSS": 1.15,
    },
    "PITRU_DOSHA": {
        "POLITICAL_OFFICE": 0.85, "DEATH": 1.15,
    },
    "GURU_CHANDALA": {
        "AWARD": 0.85, "SCANDAL": 1.5, "SPIRITUAL_AWAKENING": 1.2,
    },
    "VISH_YOGA": {
        "HEALTH_CRISIS": 1.2, "MARRIAGE": 0.85,
    },
    "DARIDRA_YOGA": {
        "FOUND_BUSINESS": 0.7, "MAJOR_LOSS": 1.3,
    },
    "SHRAPIT_DOSHA": {
        "MAJOR_LOSS": 1.3, "HEALTH_CRISIS": 1.2,
    },
    "BHASMA_YOGA": {
        "POLITICAL_OFFICE": 0.85, "CAREER_PEAK": 0.85,
    },
    # Marana karaka ↔ planet-domain anti-modifiers
    "MARANA_KARAKA_VENUS": {"MARRIAGE": 0.7},
    "MARANA_KARAKA_JUPITER": {"CHILDREN_BORN": 0.65, "AWARD": 0.85},
    "MARANA_KARAKA_MARS": {"DEATH": 1.3, "HEALTH_CRISIS": 1.2},
    "MARANA_KARAKA_SATURN": {"CAREER_PEAK": 0.8},
    "MARANA_KARAKA_SUN": {"POLITICAL_OFFICE": 0.7, "CAREER_PEAK": 0.85},
    "MARANA_KARAKA_MOON": {"MARRIAGE": 0.85},
    "MARANA_KARAKA_MERCURY": {"FOUND_BUSINESS": 0.85},
    # Combust planets reduce their domain
    "COMBUST_MERCURY": {"FOUND_BUSINESS": 0.85},
    "COMBUST_VENUS": {"MARRIAGE": 0.85},
    "COMBUST_JUPITER": {"CHILDREN_BORN": 0.8, "AWARD": 0.85},
    "COMBUST_SATURN": {"CAREER_PEAK": 0.85},
    "COMBUST_MARS": {"FOUND_BUSINESS": 0.9},
    "COMBUST_MOON": {"MARRIAGE": 0.85},
    # Debilitated significators
    "DEBIL_VENUS": {"MARRIAGE": 0.7},
    "DEBIL_JUPITER": {"CHILDREN_BORN": 0.7, "AWARD": 0.8},
    "DEBIL_MERCURY": {"FOUND_BUSINESS": 0.75},
    "DEBIL_MARS": {"DEATH": 1.15},
    "DEBIL_SATURN": {"CAREER_PEAK": 0.7},
    "DEBIL_SUN": {"POLITICAL_OFFICE": 0.7},
    "DEBIL_MOON": {"MARRIAGE": 0.8},
}

BLESSING_EVENT_MODIFIERS: dict[str, dict[str, float]] = {
    # Mahapurusha yogas — broad lift on related events
    "MAHAPURUSHA_HAMSA": {     # Jupiter
        "AWARD": 1.3, "CHILDREN_BORN": 1.25, "POLITICAL_OFFICE": 1.2,
        "SPIRITUAL_AWAKENING": 1.2,
    },
    "MAHAPURUSHA_BHADRA": {    # Mercury
        "FOUND_BUSINESS": 1.3, "AWARD": 1.2,
    },
    "MAHAPURUSHA_RUCHAKA": {   # Mars
        "CAREER_PEAK": 1.25, "POLITICAL_OFFICE": 1.2,
    },
    "MAHAPURUSHA_MALAVYA": {   # Venus
        "MARRIAGE": 1.3, "AWARD": 1.2,
    },
    "MAHAPURUSHA_SASA": {      # Saturn
        "POLITICAL_OFFICE": 1.25, "CAREER_PEAK": 1.2,
    },
    "GAJAKESARI": {
        "POLITICAL_OFFICE": 1.2, "AWARD": 1.2, "CAREER_PEAK": 1.15,
    },
    "ADHI_YOGA": {
        "POLITICAL_OFFICE": 1.25, "CAREER_PEAK": 1.2, "AWARD": 1.2,
    },
    "LAKSHMI_YOGA": {
        "MARRIAGE": 1.2, "AWARD": 1.2, "CAREER_PEAK": 1.2, "DEATH": 0.85,
    },
    "SARASWATI_YOGA": {
        "AWARD": 1.25, "CAREER_PEAK": 1.15,
    },
    "SHANKHA_YOGA": {
        "CHILDREN_BORN": 1.2, "MARRIAGE": 1.15,
    },
    "PADMA_YOGA": {
        "AWARD": 1.2, "POLITICAL_OFFICE": 1.15, "MARRIAGE": 1.15,
    },
    # Vipareeta — paradoxical good after dusthana
    "VIPARITA_RAJA_6_IN_8": {
        "CAREER_PEAK": 1.2, "MAJOR_LOSS": 0.8,
    },
    "VIPARITA_RAJA_6_IN_12": {
        "CAREER_PEAK": 1.15, "MAJOR_LOSS": 0.85,
    },
    "VIPARITA_RAJA_8_IN_6": {
        "CAREER_PEAK": 1.15, "MAJOR_LOSS": 0.85,
    },
    "VIPARITA_RAJA_8_IN_12": {
        "CAREER_PEAK": 1.15,
    },
    "VIPARITA_RAJA_12_IN_6": {
        "CAREER_PEAK": 1.15,
    },
    "VIPARITA_RAJA_12_IN_8": {
        "CAREER_PEAK": 1.15,
    },
    # Vargottama / exalted-in-kendra bring broad strength
    "VARGOTTAMA": {
        "CAREER_PEAK": 1.1, "MARRIAGE": 1.1, "AWARD": 1.1,
    },
}


def conditioned_LR(
    chart,
    event_type: str,
    base_LR: float,
    afflictions: list = None,
    blessings: list = None,
) -> dict:
    """Apply chart-static modifiers to a base ensemble LR.

    Returns a dict with breakdown so the truth directive holds:
    every modifier is shown, with its source, never folded silently.
    """
    if afflictions is None:
        from engine.afflictions import detect_all
        afflictions = detect_all(chart)
    if blessings is None:
        from engine.blessings import detect_all
        blessings = detect_all(chart)

    modifiers = []
    adjusted = base_LR

    # Apply affliction modifiers
    for a in afflictions:
        mod = AFFLICTION_EVENT_MODIFIERS.get(a.code, {}).get(event_type)
        if mod is not None and mod != 1.0:
            modifiers.append({
                "source": "affliction", "code": a.code,
                "name": a.name, "modifier": mod,
            })
            adjusted *= mod

    # Apply blessing modifiers
    for b in blessings:
        mod = BLESSING_EVENT_MODIFIERS.get(b.code, {}).get(event_type)
        if mod is not None and mod != 1.0:
            modifiers.append({
                "source": "blessing", "code": b.code,
                "name": b.name, "modifier": mod,
            })
            adjusted *= mod

    return {
        "event_type": event_type,
        "base_LR": round(base_LR, 4),
        "conditioned_LR": round(adjusted, 4),
        "modifiers_applied": modifiers,
        "net_modifier": round(adjusted / base_LR if base_LR > 0 else 1.0, 3),
        "interpretation": _interpret(base_LR, adjusted, modifiers),
    }


def _interpret(base, adj, mods):
    if not mods:
        return "No chart-static modifiers apply — base ensemble LR unchanged."
    lift = adj / base if base > 0 else 1.0
    affs = [m for m in mods if m["source"] == "affliction"]
    blss = [m for m in mods if m["source"] == "blessing"]
    parts = []
    if affs:
        parts.append(f"{len(affs)} affliction(s) reducing/raising LR: {[m['code'] for m in affs]}")
    if blss:
        parts.append(f"{len(blss)} blessing(s) raising/reducing LR: {[m['code'] for m in blss]}")
    parts.append(f"net modifier ×{lift:.2f}")
    return ". ".join(parts) + "."


def conditioned_forecast_for_chart(chart) -> dict:
    """Apply conditioning to all event types for the current MD/AD."""
    from engine.calibration import forecast_confidence
    from engine.afflictions import detect_all as detect_aff
    from engine.blessings import detect_all as detect_bls
    from engine.backtest import EVENT_PATTERNS

    afflictions = detect_aff(chart)
    blessings = detect_bls(chart)

    out = {}
    for evt in EVENT_PATTERNS:
        f = forecast_confidence(evt, chart.current_md, chart.current_ad)
        base = f.get("likelihood_ratio") or 1.0
        adj = conditioned_LR(chart, evt, base,
                             afflictions=afflictions, blessings=blessings)
        out[evt] = {**f, "conditioned": adj}
    return out
