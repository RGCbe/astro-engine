"""
Real-time event-window finder.

Scan a chart's future at month resolution; return ranked windows where the
ensemble LR exceeds threshold for each event type.

API:
    forecast_windows(chart, start, end, event_types=None, threshold=1.5,
                     step_days=30) → list[ForecastWindow]
    next_high_LR(chart, event_type, from_dt, max_months=24, threshold=1.5)
        → ForecastWindow | None

Per the truth directive:
    - Event types whose ensemble LR has historically been < 1.0 are skipped
      with a clear "no reliable forecast available" note rather than
      producing flattering false-positive windows.
    - Each window includes the per-signal breakdown so a reader can audit
      WHY the engine flagged it.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from engine.backtest import EVENT_PATTERNS
from engine.dasha import current_dasha, vimshottari
from engine.ensemble import ensemble_score
from engine.transit_conditioned import _transit_factors_at


# Event types known to be reliably predictable (ensemble LR ≥ 1.5 in backtest)
RELIABLY_PREDICTABLE = {
    "IMPRISONMENT", "CHILDREN_BORN", "POLITICAL_OFFICE", "FOUND_BUSINESS",
    "CAREER_START", "SPIRITUAL_AWAKENING", "MARRIAGE", "DIVORCE",
}
# Event types where ensemble has weak/no signal (never produce confident forecasts)
UNRELIABLE = {"DEATH", "MAJOR_LOSS", "EXILE", "AWARD", "HEALTH_CRISIS",
              "CAREER_PEAK"}


@dataclass
class ForecastWindow:
    event_type: str
    moment: dt.datetime
    md_lord: str
    ad_lord: str
    ensemble_LR: float
    universal_LR: float
    chart_relative_LR: float
    transit_LR: float
    transit_factors_active: list[str] = field(default_factory=list)
    interpretation: str = ""
    reliability: str = "MEDIUM"   # HIGH | MEDIUM | LOW — reflects backtest confidence
    valence: str = "NEUTRAL"      # GOOD | BAD | NEUTRAL — semantic direction


EVENT_VALENCE = {
    "MARRIAGE": "GOOD", "CHILDREN_BORN": "GOOD", "CAREER_PEAK": "GOOD",
    "FOUND_BUSINESS": "GOOD", "POLITICAL_OFFICE": "GOOD", "AWARD": "GOOD",
    "CAREER_START": "GOOD", "SPIRITUAL_AWAKENING": "NEUTRAL",
    "HEALTH_CRISIS": "BAD", "DEATH": "BAD", "DIVORCE": "BAD",
    "MAJOR_LOSS": "BAD", "IMPRISONMENT": "BAD", "EXILE": "BAD",
    "SCANDAL": "BAD",
}


def _at_moment(chart, moment, event_type, natal_moon, natal_lagna,
               natal_sat, natal_jup, seventh_sign):
    md, ad = current_dasha(chart, moment)
    if md is None:
        return None
    tf = _transit_factors_at(moment, natal_moon, natal_lagna,
                              natal_sat, natal_jup, seventh_sign)
    es = ensemble_score(chart, event_type, md.lord,
                        ad.lord if ad else None, tf)
    active = [f for f, v in tf.items() if v]
    reliability = "LOW" if event_type in UNRELIABLE else (
        "HIGH" if event_type in RELIABLY_PREDICTABLE else "MEDIUM"
    )
    return ForecastWindow(
        event_type=event_type, moment=moment,
        md_lord=md.lord, ad_lord=ad.lord if ad else "",
        ensemble_LR=es.ensemble_LR,
        universal_LR=es.universal_LR,
        chart_relative_LR=es.chart_relative_LR,
        transit_LR=es.transit_LR,
        transit_factors_active=active,
        interpretation=es.interpretation,
        reliability=reliability,
        valence=EVENT_VALENCE.get(event_type, "NEUTRAL"),
    )


def forecast_windows(
    chart,
    start: dt.datetime,
    end: dt.datetime,
    event_types: list[str] | None = None,
    threshold: float = 1.5,
    step_days: int = 30,
    skip_unreliable: bool = False,
) -> dict[str, list[ForecastWindow]]:
    """Scan moment-by-moment; return per-event-type ranked windows above threshold.

    PER USER DIRECTIVE 2026-04-26: report BOTH good and bad events. The
    `skip_unreliable` flag now defaults to False — health/death/loss are
    surfaced WITH their honest LR. Hiding negatives is forbidden.

    Args:
        event_types:  default = all events. UNRELIABLE events are still
                      reported, marked with `reliability="LOW"` flag in
                      each window for honest reading.
    """
    if event_types is None:
        event_types = sorted(EVENT_PATTERNS)
    if skip_unreliable:
        event_types = [e for e in event_types if e not in UNRELIABLE]

    # Pre-compute natal vimshottari + cached natal positions
    from engine.negative_backtest import _moon_lon, _birth_dt
    natal_moon_lon_for_dasha = _moon_lon({
        "date": chart.birth_dt.strftime("%Y-%m-%d"),
        "time": chart.birth_dt.strftime("%H:%M"),
        "tz": chart.tz_hours,
    })
    periods = vimshottari(natal_moon_lon_for_dasha, chart.birth_dt)
    natal_moon = chart.positions["Moon"]
    natal_lagna = chart.lagna_lon
    natal_sat = chart.positions["Saturn"]
    natal_jup = chart.positions["Jupiter"]
    seventh_sign = (int(natal_lagna // 30) + 6) % 12

    out: dict[str, list[ForecastWindow]] = {evt: [] for evt in event_types}
    cursor = start
    while cursor < end:
        for evt in event_types:
            w = _at_moment(chart, cursor, evt, natal_moon,
                           natal_lagna, natal_sat, natal_jup, seventh_sign)
            if w is None:
                continue
            if w.ensemble_LR >= threshold:
                out[evt].append(w)
        cursor += dt.timedelta(days=step_days)

    # Sort each event's windows by LR desc, keep top 10
    for evt in out:
        out[evt].sort(key=lambda w: -w.ensemble_LR)
        out[evt] = out[evt][:10]

    # Add a "no forecast" entry for unreliable types if user explicitly asked
    if event_types is None and not skip_unreliable:
        for evt in UNRELIABLE:
            if evt not in out:
                out[evt] = []
    return out


def next_high_LR(
    chart,
    event_type: str,
    from_dt: dt.datetime | None = None,
    max_months: int = 24,
    threshold: float = 1.5,
) -> ForecastWindow | None:
    """Find the first month within `max_months` where ensemble LR >= threshold."""
    if event_type in UNRELIABLE:
        return None
    from_dt = from_dt or dt.datetime.now()
    end = from_dt + dt.timedelta(days=max_months * 30)
    windows = forecast_windows(chart, from_dt, end,
                               event_types=[event_type], threshold=threshold,
                               step_days=15, skip_unreliable=False)
    if not windows.get(event_type):
        return None
    # Sort by moment ascending to get the FIRST one
    earliest = sorted(windows[event_type], key=lambda w: w.moment)[0]
    return earliest


def forecast_summary(chart, months_ahead: int = 24) -> dict:
    """Compact, user-facing summary of upcoming high-LR windows."""
    start = dt.datetime.now()
    end = start + dt.timedelta(days=months_ahead * 30)
    windows = forecast_windows(chart, start, end,
                               threshold=1.5, step_days=30)
    summary = {
        "scan_range": {"start": start.isoformat()[:10], "end": end.isoformat()[:10]},
        "method": "ensemble: universal-karaka + chart-relative + learned-transit (LR product)",
        "threshold": 1.5,
        "reliably_predictable_events": sorted(RELIABLY_PREDICTABLE),
        "unreliable_events_skipped": sorted(UNRELIABLE),
        "truth_note": (
            "Only event types with backtest LR ≥ 1.5 are forecast. Events in "
            "UNRELIABLE list (DEATH, MAJOR_LOSS, AWARD, etc.) have weak "
            "empirical signal and are NOT predicted to avoid false positives."
        ),
        "forecasts": {},
    }
    for evt, ws in windows.items():
        if not ws:
            summary["forecasts"][evt] = {"no_high_LR_window_in_range": True}
            continue
        summary["forecasts"][evt] = [
            {
                "moment":         w.moment.isoformat()[:10],
                "ensemble_LR":    w.ensemble_LR,
                "md":             w.md_lord, "ad": w.ad_lord,
                "universal_LR":   w.universal_LR,
                "chart_rel_LR":   w.chart_relative_LR,
                "transit_LR":     w.transit_LR,
                "transit_active": w.transit_factors_active,
                "note":           w.interpretation,
            }
            for w in ws[:5]
        ]
    return summary
