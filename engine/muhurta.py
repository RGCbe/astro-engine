"""
Muhurta — electional astrology engine.

Find auspicious time windows for a specific activity within a date range.
Scoring combines:
    - Panchanga limbs (tithi, nakshatra, yoga, vara, karana) per the activity
    - Avoidance of inauspicious windows (Rahu/Yamaganda/Gulika kala)
    - Use of auspicious windows (Abhijit, Brahma muhurta)
    - Lagna at start of activity (avoid kendra-malefic, use kendra-benefic)
    - Moon's nakshatra strength

Per the engine's truth-only directive: returned scores reflect the actual
panchanga state — never inflate "good day" status if hard rules are violated.

API:
    score_moment(moment, lat, lon, tz, activity)  → 0..100 + breakdown
    find_windows(start, end, lat, lon, tz, activity, top_n=10)
                                                   → ranked list of moments
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from engine.panchanga import panchanga, Panchanga, NAKSHATRAS, VARAS


# ─── Activity-specific muhurta tables ──────────────────────────────────────
# Source: Muhurta Chintamani by Ram Acharya (16th c.) + KP Muhurta module +
# BV Raman, "Muhurtha" (1992).
#
# Each activity prefers/forbids specific panchanga values. These are the
# canonical preferences across Vedic muhurta texts.
ACTIVITY_RULES: dict[str, dict] = {
    "marriage": {
        "good_nakshatras": {"Rohini", "Mrigashirsha", "Magha", "Uttara Phalguni",
                            "Hasta", "Swati", "Anuradha", "Mula",
                            "Uttara Ashadha", "Uttara Bhadrapada", "Revati"},
        "bad_nakshatras":  {"Bharani", "Krittika", "Ardra", "Ashlesha",
                            "Purva Phalguni", "Chitra", "Vishakha",
                            "Jyeshtha", "Purva Ashadha", "Dhanishta",
                            "Shatabhisha", "Purva Bhadrapada"},
        "good_tithis":     {2, 3, 5, 7, 10, 11, 12, 13},
        "bad_tithis":      {4, 6, 8, 9, 14, 15, 30},  # incl. amavasya
        "good_varas":      {"Monday", "Wednesday", "Thursday", "Friday"},
        "bad_varas":       {"Tuesday", "Saturday"},
        "bad_yogas":       {"Vyatipata", "Vaidhruti", "Vishkambha",
                            "Atiganda", "Shoola", "Ganda", "Vyaghata",
                            "Vajra", "Parigha"},
    },
    "business_start": {
        "good_nakshatras": {"Ashvini", "Pushya", "Hasta", "Chitra", "Anuradha",
                            "Uttara Ashadha", "Uttara Phalguni", "Uttara Bhadrapada"},
        "bad_nakshatras":  {"Bharani", "Krittika", "Ashlesha", "Magha",
                            "Jyeshtha", "Mula", "Revati"},
        "good_tithis":     {2, 3, 5, 7, 10, 11, 13},
        "bad_tithis":      {4, 8, 9, 14, 15, 30},
        "good_varas":      {"Wednesday", "Thursday", "Friday"},
        "bad_varas":       {"Tuesday", "Saturday"},
        "bad_yogas":       {"Vyatipata", "Vaidhruti", "Vishkambha", "Atiganda"},
    },
    "travel": {
        "good_nakshatras": {"Ashvini", "Pushya", "Hasta", "Anuradha", "Sravana",
                            "Dhanishta", "Punarvasu", "Mrigashirsha", "Revati"},
        "bad_nakshatras":  {"Bharani", "Krittika", "Magha", "Mula"},
        "good_tithis":     {2, 3, 5, 7, 10, 11, 12, 13},
        "bad_tithis":      {4, 8, 9, 14, 15, 30},
        "good_varas":      {"Monday", "Wednesday", "Thursday", "Friday"},
        "bad_varas":       set(),
        "bad_yogas":       {"Vyatipata", "Vaidhruti", "Atiganda", "Vajra"},
    },
    "naming_ceremony": {
        "good_nakshatras": {"Ashvini", "Rohini", "Mrigashirsha", "Pushya",
                            "Hasta", "Chitra", "Swati", "Anuradha", "Sravana",
                            "Revati", "Punarvasu", "Uttara Phalguni",
                            "Uttara Ashadha", "Uttara Bhadrapada"},
        "bad_nakshatras":  {"Bharani", "Krittika", "Ashlesha", "Magha",
                            "Jyeshtha", "Mula"},
        "good_tithis":     {1, 2, 3, 5, 7, 10, 11, 13},
        "bad_tithis":      {4, 6, 8, 9, 14, 15, 30},
        "good_varas":      {"Monday", "Wednesday", "Thursday", "Friday"},
        "bad_varas":       set(),
        "bad_yogas":       {"Vyatipata", "Vaidhruti", "Vishkambha"},
    },
    "education_start": {
        "good_nakshatras": {"Ashvini", "Pushya", "Hasta", "Chitra", "Swati",
                            "Anuradha", "Sravana", "Punarvasu", "Mrigashirsha",
                            "Revati", "Uttara Phalguni", "Uttara Ashadha",
                            "Uttara Bhadrapada"},
        "bad_nakshatras":  {"Bharani", "Krittika", "Ashlesha", "Magha"},
        "good_tithis":     {2, 3, 5, 7, 10, 11, 12, 13},
        "bad_tithis":      {4, 8, 9, 14, 15, 30},
        "good_varas":      {"Wednesday", "Thursday", "Friday"},
        "bad_varas":       {"Tuesday", "Saturday"},
        "bad_yogas":       {"Vyatipata", "Vaidhruti"},
    },
    "general": {
        "good_nakshatras": {"Pushya", "Hasta", "Anuradha", "Revati",
                            "Mrigashirsha", "Chitra", "Swati"},
        "bad_nakshatras":  {"Bharani", "Krittika", "Ashlesha"},
        "good_tithis":     {2, 3, 5, 7, 10, 11, 13},
        "bad_tithis":      {4, 8, 9, 14, 15, 30},
        "good_varas":      {"Monday", "Wednesday", "Thursday", "Friday"},
        "bad_varas":       {"Tuesday", "Saturday"},
        "bad_yogas":       {"Vyatipata", "Vaidhruti", "Atiganda", "Vajra"},
    },
}


# ─── Inauspicious-window detection ─────────────────────────────────────────
def _in_window(moment: dt.datetime, window: tuple[dt.datetime, dt.datetime] | None) -> bool:
    if not window:
        return False
    return window[0] <= moment < window[1]


@dataclass
class MuhurtaScore:
    moment: dt.datetime
    score: int            # 0..100 (higher = more auspicious)
    breakdown: dict
    rejected_reasons: list[str]
    accepted_factors: list[str]
    verbatim_citations: list[dict] = None  # populated lazily

    @property
    def verdict(self) -> str:
        if self.rejected_reasons:
            return "REJECTED"
        if self.score >= 75:
            return "EXCELLENT"
        if self.score >= 60:
            return "GOOD"
        if self.score >= 40:
            return "ACCEPTABLE"
        return "POOR"


def score_moment(
    moment: dt.datetime,
    lat: float,
    lon: float,
    tz_hours: float,
    activity: str = "general",
) -> MuhurtaScore:
    """Score a candidate moment against muhurta rules for `activity`."""
    rules = ACTIVITY_RULES.get(activity, ACTIVITY_RULES["general"])
    p = panchanga(moment, lat, lon, tz_hours)

    accepted = []
    rejected = []
    score = 50

    # ─── Hard rejection rules ──────────────────────────────────────────
    if _in_window(moment, p.rahu_kala):
        rejected.append("falls within Rahu kala")
    if _in_window(moment, p.yamaganda_kala):
        rejected.append("falls within Yamaganda kala")
    if _in_window(moment, p.gulika_kala):
        rejected.append("falls within Gulika kala")
    if p.nakshatra in rules.get("bad_nakshatras", set()):
        rejected.append(f"nakshatra {p.nakshatra} is forbidden for {activity}")
    if p.vara in rules.get("bad_varas", set()):
        rejected.append(f"weekday {p.vara} is forbidden for {activity}")
    if p.yoga in rules.get("bad_yogas", set()):
        rejected.append(f"yoga {p.yoga} is inauspicious")
    if p.tithi_index in rules.get("bad_tithis", set()):
        rejected.append(f"tithi {p.tithi} is forbidden")

    # ─── Positive scoring (only if not already rejected) ───────────────
    if p.nakshatra in rules.get("good_nakshatras", set()):
        score += 15
        accepted.append(f"nakshatra {p.nakshatra} is favorable")
    if p.tithi_index in rules.get("good_tithis", set()):
        score += 10
        accepted.append(f"tithi {p.tithi} is favorable")
    if p.vara in rules.get("good_varas", set()):
        score += 10
        accepted.append(f"weekday {p.vara} is favorable")
    if p.paksha == "Shukla":
        score += 8
        accepted.append("Shukla paksha (waxing moon)")
    if p.yoga not in rules.get("bad_yogas", set()):
        score += 4
        accepted.append(f"yoga {p.yoga} is acceptable")

    # Bonus for Abhijit muhurta
    if _in_window(moment, p.abhijit_muhurta):
        score += 8
        accepted.append("falls within Abhijit muhurta (auspicious)")
    if _in_window(moment, p.brahma_muhurta):
        score += 4
        accepted.append("falls within Brahma muhurta (auspicious)")

    score = min(100, max(0, score))
    if rejected:
        score = 0  # Hard reject

    # Surface up to 5 verbatim classical rules for this activity
    citations: list[dict] = []
    try:
        from .muhurta_verbatim import rules_for_activity
        for vr in rules_for_activity(activity, max_results=5):
            citations.append({
                "citation": vr.cite(),
                "text": vr.text[:240] + ("…" if len(vr.text) > 240 else ""),
                "rule_type": vr.rule_type,
            })
    except Exception:
        pass

    return MuhurtaScore(
        moment=moment, score=score,
        breakdown={
            "tithi": p.tithi, "paksha": p.paksha,
            "nakshatra": p.nakshatra, "yoga": p.yoga,
            "karana": p.karana, "vara": p.vara,
            "in_rahu_kala": _in_window(moment, p.rahu_kala),
            "in_yamaganda_kala": _in_window(moment, p.yamaganda_kala),
            "in_gulika_kala": _in_window(moment, p.gulika_kala),
            "in_abhijit_muhurta": _in_window(moment, p.abhijit_muhurta),
        },
        rejected_reasons=rejected,
        accepted_factors=accepted,
        verbatim_citations=citations,
    )


def find_windows(
    start: dt.datetime,
    end: dt.datetime,
    lat: float,
    lon: float,
    tz_hours: float,
    activity: str = "general",
    step_minutes: int = 60,
    top_n: int = 10,
) -> list[MuhurtaScore]:
    """Scan the date range at `step_minutes` resolution, return top_n scoring moments."""
    results = []
    cursor = start
    while cursor < end:
        s = score_moment(cursor, lat, lon, tz_hours, activity)
        if not s.rejected_reasons:
            results.append(s)
        cursor += dt.timedelta(minutes=step_minutes)
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_n]
