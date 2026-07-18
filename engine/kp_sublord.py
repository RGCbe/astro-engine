"""engine.kp_sublord — KP (Krishnamurti Paddhati) sub-lord theory.

Bridges to runtime/kp_paddhati.py.
Exposes: get_kp_chart(), get_kp_position() — the API engine/ modules expect.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))

from kp_paddhati import (
    get_sub_lord,
    get_sub_sub_lord,
    cuspal_sub_lord,
    kp_event_significators,
    kp_summary,
)


def get_kp_position(longitude_deg):
    """For any longitude, return full KP breakdown: nakshatra, sub-lord, sub-sub-lord."""
    sl = get_sub_lord(longitude_deg)
    ssl = get_sub_sub_lord(longitude_deg)
    return {
        "longitude": longitude_deg,
        "nakshatra": sl["nak"],
        "nakshatra_lord": sl["nak_lord"],
        "sub_lord": sl["sub_lord"],
        "sub_sub_lord": ssl["sub_sub_lord"],
    }


def get_kp_chart(natal_chart):
    """Full KP chart analysis: cuspal sub-lords for all 12 houses + significators."""
    return kp_summary(natal_chart)
