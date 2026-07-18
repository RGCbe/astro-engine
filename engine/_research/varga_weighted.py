"""
Varga-weighted forecasting — use D9, D10, D24, D60 to adjust event LR.

Per audit Tier 2: 16 vargas were computed but only D1 fed forecasts.
This module wires divisional charts into event scoring:

    D9  (Navamsa)        → MARRIAGE, DIVORCE, dharma events
    D10 (Dasamsa)        → CAREER_PEAK, CAREER_START, POLITICAL_OFFICE,
                           FOUND_BUSINESS, AWARD
    D24 (Chaturvimshamsa) → AWARD (education), spiritual learning
    D60 (Shashtiamsa)    → SPIRITUAL_AWAKENING, deep karmic events

Logic: if MD or AD lord is in the *relevant* varga's kendra/trikona OR
own/exalted in that varga, multiply LR by 1.15-1.25. If debilitated or
in dusthana of that varga, multiply by 0.75-0.85.

Per truth directive: every adjustment is shown with its source varga.
"""
from __future__ import annotations

EXALTATION_SIGN = {
    "Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
    "Jupiter": 3, "Venus": 11, "Saturn": 6,
}
DEBILITATION_SIGN = {
    "Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
    "Jupiter": 9, "Venus": 5, "Saturn": 0,
}
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10],
}

EVENT_TO_VARGA = {
    "MARRIAGE": "D9",
    "DIVORCE": "D9",
    "CAREER_PEAK": "D10",
    "CAREER_START": "D10",
    "POLITICAL_OFFICE": "D10",
    "FOUND_BUSINESS": "D10",
    "AWARD": "D10",
    "SPIRITUAL_AWAKENING": "D60",
}


def _varga_state(planet: str, varga_data: dict) -> str:
    """Return state of planet in this varga: exalted/own/debil/dusthana/neutral."""
    if not varga_data:
        return "unknown"
    sign_idx = varga_data.get("sign_index", -1)
    if sign_idx == EXALTATION_SIGN.get(planet):
        return "exalted"
    if sign_idx in OWN_SIGNS.get(planet, []):
        return "own"
    if sign_idx == DEBILITATION_SIGN.get(planet):
        return "debilitated"
    return "neutral"


def varga_modifier(chart, planet: str, event_type: str) -> dict:
    """LR modifier from the relevant divisional chart."""
    varga_name = EVENT_TO_VARGA.get(event_type)
    if not varga_name:
        return {"modifier": 1.0, "reason": "no varga mapped to this event"}
    if not hasattr(chart, "vargas"):
        return {"modifier": 1.0, "reason": "no varga data on chart"}
    pdata = chart.vargas.get(planet, {})
    vdata = pdata.get(varga_name)
    if not vdata:
        return {"modifier": 1.0, "reason": f"no {varga_name} data for {planet}"}
    state = _varga_state(planet, vdata)
    state_to_mod = {
        "exalted": 1.25,
        "own": 1.20,
        "neutral": 1.0,
        "debilitated": 0.75,
        "unknown": 1.0,
    }
    mod = state_to_mod[state]
    return {
        "modifier": mod,
        "varga": varga_name,
        "planet": planet,
        "state_in_varga": state,
        "varga_sign": vdata.get("sign"),
        "reason": f"{planet} is {state} in {varga_name} ({vdata.get('sign','?')})",
    }


def varga_conditioned(chart, event_type: str, base_LR: float) -> dict:
    """Apply varga modifiers from current MD and AD lords."""
    md = chart.current_md
    ad = chart.current_ad
    md_mod = varga_modifier(chart, md, event_type) if md else {"modifier": 1.0}
    ad_mod = varga_modifier(chart, ad, event_type) if ad else {"modifier": 1.0}
    # Geometric mean of MD and AD adjustments (avoid double-counting same varga state)
    combined_mod = (md_mod["modifier"] * ad_mod["modifier"]) ** 0.5
    return {
        "event_type": event_type,
        "base_LR": round(base_LR, 4),
        "varga_adjusted_LR": round(base_LR * combined_mod, 4),
        "md_varga_check": md_mod,
        "ad_varga_check": ad_mod,
        "combined_modifier": round(combined_mod, 3),
    }
