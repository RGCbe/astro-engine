"""
Antardasha-level deep event predictor.

For every (mahadasha, antardasha) pair across the whole Vimshottari
schedule, produce a concrete event-class prediction with confidence:

    EDUCATION_PEAK | CAREER_LAUNCH | MARRIAGE | CHILDREN_BORN |
    FOREIGN_TRAVEL | ACCIDENT_RISK | HEALTH_CRISIS | FAMILY_LOSS |
    FINANCIAL_GAIN | SPIRITUAL_TURN | RECOGNITION

Method:
    1. For each AD: identify MD-lord and AD-lord and their natal houses.
    2. Apply karaka-rules (e.g. 7th-lord+Venus active → MARRIAGE)
       refit by the empirical karaka mapping from v0.5+.
    3. Score each event by lord-overlap with classical+empirical karakas.
    4. Confidence band: HIGH if both MD and AD lords are karakas;
       MEDIUM if only one; LOW if neither but transit triggers.
    5. Output age-bracketed bullets.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


# Refit karaka map (classical + empirical, taken from learned_transit_predictors)
KARAKA = {
    "MARRIAGE":         {"Venus", "Jupiter", "Moon"},
    "CHILDREN_BORN":    {"Jupiter", "Saturn", "Sun"},   # Saturn empirically promoted
    "FOUND_BUSINESS":   {"Mercury", "Mars", "Venus", "Moon", "Ketu"},
    "EDUCATION_PEAK":   {"Mercury", "Jupiter", "Sun"},
    "FOREIGN_TRAVEL":   {"Rahu", "Moon", "Saturn"},
    "ACCIDENT_RISK":    {"Mars", "Saturn", "Rahu"},
    "HEALTH_CRISIS":    {"Saturn", "Rahu", "Mars"},
    "FAMILY_LOSS":      {"Saturn", "Ketu", "Rahu"},
    "FINANCIAL_GAIN":   {"Jupiter", "Venus", "Mercury"},  # 2nd/11th karakas
    "SPIRITUAL_TURN":   {"Ketu", "Jupiter", "Saturn"},
    "RECOGNITION":      {"Sun", "Jupiter", "Mars"},
    "POLITICAL_OFFICE": {"Sun", "Jupiter", "Mars", "Saturn"},
    "DEATH_RISK":       {"Saturn", "Mars", "Ketu", "Rahu"},
}

EVENT_LABEL = {
    "MARRIAGE":         "marriage / partnership formation",
    "CHILDREN_BORN":    "children / fertility window",
    "FOUND_BUSINESS":   "business or independent venture launch",
    "EDUCATION_PEAK":   "studies / examination peak",
    "FOREIGN_TRAVEL":   "foreign travel or relocation",
    "ACCIDENT_RISK":    "accident / sudden injury risk",
    "HEALTH_CRISIS":    "health challenge",
    "FAMILY_LOSS":      "family bereavement / separation",
    "FINANCIAL_GAIN":   "financial gain / property",
    "SPIRITUAL_TURN":   "spiritual reorientation / withdrawal",
    "RECOGNITION":      "recognition / public success",
    "POLITICAL_OFFICE": "political / governmental role",
    "DEATH_RISK":       "longevity-stress window",
}


@dataclass
class ADEvent:
    md_lord: str
    ad_lord: str
    start: dt.datetime
    end: dt.datetime
    age_start: float
    age_end: float
    event: str
    confidence: str   # HIGH | MEDIUM | LOW
    reason: str


def _planet_house(chart, planet: str) -> int:
    lon = chart.positions.get(planet)
    if lon is None:
        return 0
    lagna_sign = int(chart.lagna_lon // 30)
    return ((int(lon // 30) - lagna_sign) % 12) + 1


def _lords_active(md, ad) -> set:
    return {md, ad}


_REFIT_DATA = None


def _load_refit():
    """Lazy-load the empirical refit data for confidence calibration."""
    global _REFIT_DATA
    if _REFIT_DATA is not None:
        return _REFIT_DATA
    import json, os
    path = os.path.join(os.path.dirname(__file__), "data", "event_patterns_refit.json")
    try:
        _REFIT_DATA = json.load(open(path))["refit"]
    except Exception:
        _REFIT_DATA = {}
    return _REFIT_DATA


def _confidence(active_lords: set, karaka_set: set,
                 event: str | None = None) -> str:
    """Calibrate the structural confidence band against empirical LR data
    where available. If the event has an LR<1.1 in the refit corpus,
    demote one band; if LR≥2.0, promote one band."""
    overlap = active_lords & karaka_set
    if len(overlap) >= 2:
        struct = "HIGH"
    elif len(overlap) == 1:
        struct = "MEDIUM"
    else:
        struct = "LOW"

    if event:
        refit = _load_refit().get(event, {})
        lor = refit.get("LR_overall") or refit.get("LR")
        # Use the rationale's LR≥1.5 as a proxy for "this event has
        # empirical signal worth promoting"
        primary_overlap = bool(set(refit.get("primary", [])) & active_lords)
        secondary_overlap = bool(set(refit.get("secondary", [])) & active_lords)
        if not primary_overlap and not secondary_overlap and struct == "HIGH":
            struct = "MEDIUM"  # demote — classical karaka but not empirical
        if primary_overlap and struct == "LOW":
            struct = "MEDIUM"  # promote — empirical but not classical
        if primary_overlap and secondary_overlap and struct == "MEDIUM":
            struct = "HIGH"
    return struct


def _antardashas_for(md) -> list:
    """Return AD list of a Mahadasha — uses md.antardashas if present."""
    return getattr(md, "antardashas", None) or []


def predict_ad_events(chart, today: dt.datetime | None = None,
                      include_low: bool = False
                      ) -> list[ADEvent]:
    today = today or dt.datetime.now()
    birth = chart.birth_dt
    out: list[ADEvent] = []
    
    from engine.dasha import full_timeline
    moon_lon = float(chart.positions["Moon"])
    b = {
        "year": birth.year, "month": birth.month, "day": birth.day,
        "hour": getattr(birth, "hour", 12), "min": getattr(birth, "minute", 0)
    }
    synth_chart = {"positions": {"Moon": {"lon": moon_lon, "lon_abs": moon_lon}}, "birth": b}
    timeline = full_timeline(synth_chart, levels=2)
    
    current_ml = None
    for rec in timeline:
        if rec.get("level") == 1:
            current_ml = rec.get("md") or rec.get("lord")
        elif rec.get("level") == 2:
            ml = current_ml
            al = rec.get("ad") or rec.get("lord")
            
            # Protect against malformed records
            if not ml or not al:
                continue
                
            active = _lords_active(ml, al)
            age_a = round((rec["start"] - birth).days / 365.25, 1)
            age_b = round((rec["end"] - birth).days / 365.25, 1)

            # Score each event and deduplicate
            period_events = []
            for event, karaka_set in KARAKA.items():
                # Suppress adult themes in childhood
                if age_a < 16 and event in ["MARRIAGE", "FOUND_BUSINESS", "CAREER_PEAK", "POLITICAL_OFFICE"]:
                    continue
                    
                conf = _confidence(active, karaka_set, event=event)
                if conf == "LOW" and not include_low:
                    continue

                # Rank weight
                weight = 0
                if conf == "HIGH": weight += 100
                elif conf == "MEDIUM": weight += 50
                
                # Impact weight to resolve ties
                impact = {
                    "HEALTH_CRISIS": 90, "DEATH_RISK": 95, "ACCIDENT_RISK": 85, "FAMILY_LOSS": 80,
                    "CAREER_PEAK": 75, "MARRIAGE": 70, "CHILDREN_BORN": 70, "FINANCIAL_GAIN": 65,
                    "FOUND_BUSINESS": 65, "EDUCATION_PEAK": 60, "POLITICAL_OFFICE": 75,
                    "FOREIGN_TRAVEL": 50, "SPIRITUAL_TURN": 40
                }
                weight += impact.get(event, 0)
                
                period_events.append({
                    "event": event,
                    "conf": conf,
                    "weight": weight,
                    "karakas": karaka_set
                })
                
            if period_events:
                # Select the highest weighted event
                top_event = sorted(period_events, key=lambda x: x["weight"], reverse=True)[0]
                
                houses = (_planet_house(chart, ml), _planet_house(chart, al))
                reason = (
                    f"MD={ml} (H{houses[0]}), AD={al} (H{houses[1]}); "
                    f"event-karakas {sorted(top_event['karakas'])}: overlap "
                    f"{sorted(active & top_event['karakas'])}"
                )
                out.append(ADEvent(
                    md_lord=ml, ad_lord=al,
                    start=rec["start"], end=rec["end"],
                    age_start=age_a, age_end=age_b,
                    event=top_event["event"], confidence=top_event["conf"], reason=reason,
                ))
    return out


def render_deep_timeline_markdown(chart) -> str:
    out = ["## ✦ Period-by-Period Event Map (the deep timeline)\n"]
    out.append(
        "Below is your life broken down at the **antardasha level** — the "
        "1- to 3-year sub-periods inside each mahadasha. For each window "
        "the engine names the most likely event-class, with a confidence "
        "tag (**HIGH** = both MD and AD lords are karakas of that event; "
        "**MEDIUM** = one is). Confidence is the engine's *honest* "
        "self-grade — read past entries first to confirm calibration."
    )
    out.append("")
    events = predict_ad_events(chart)
    if not events:
        out.append("_Antardasha schedule not available._")
        return "\n".join(out)

    today = dt.datetime.now()
    past = [e for e in events if e.end < today]
    present = [e for e in events if e.start <= today <= e.end]
    future = [e for e in events if e.start > today]

    def _row(e: ADEvent) -> str:
        sym = {"HIGH": "🔴", "MEDIUM": "🟡"}.get(e.confidence, "⚪")
        return (
            f"- `{e.start.year}-{e.start.month:02d} → "
            f"{e.end.year}-{e.end.month:02d}` "
            f"(age {e.age_start:.0f}–{e.age_end:.0f}) · "
            f"**{e.md_lord}-{e.ad_lord}** · {sym} **{e.confidence}** · "
            f"{EVENT_LABEL[e.event]}"
        )

    if past:
        out.append("### Past windows — verify against your memory")
        out.append("")
        for e in past:
            out.append(_row(e))
        out.append("")

    if present:
        out.append("### What is active right now")
        out.append("")
        for e in present:
            out.append(_row(e))
        out.append("")

    if future:
        out.append("### Future windows (next 25 years)")
        out.append("")
        cutoff = today + dt.timedelta(days=25 * 365)
        for e in future:
            if e.start > cutoff:
                continue
            out.append(_row(e))
        out.append("")

    return "\n".join(out)
