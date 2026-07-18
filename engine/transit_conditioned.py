"""
Transit-conditioned forecasting.

Combine dasha (long-term, year-scale) with transits (short-term, month-scale)
to produce sharper event windows. Hypothesis: events fire when BOTH dasha
signature AND transit signature align — predicting that conjunction should
have a higher LR than either alone.

Transit triggers checked at event moment:
    - Saturn transit: in 12th/1st/2nd from natal Moon (Sade Sati) → events
                      involving struggle / health / loss
    - Saturn transit: aspecting natal Saturn (Saturn return) → ages 29/58/87
                      for life-stage transitions
    - Jupiter transit: in 5th/7th/9th/11th from natal Moon → benefic events
                      (marriage, children, awards)
    - Jupiter transit: through natal 7th sign → marriage triggers
    - Rahu/Ketu transit: aspecting natal lagna or Moon → upheaval / spiritual

Per the truth directive: each transit factor is reported with its own LR
contribution, never bundled into vague "transits favor X" language.
"""
from __future__ import annotations

import datetime as dt
from collections import Counter
from dataclasses import dataclass

from engine.backtest import EVENT_PATTERNS, _classify
from engine.dasha import current_dasha, vimshottari
from engine.known_charts import KNOWN_CHARTS
from engine.negative_backtest import (
    _moon_lon, _birth_dt, _sample_negative_years,
)
from engine.transits import _datetime_to_jd, _sidereal_lon


def _transit_factors_at(at_dt: dt.datetime, natal_moon_lon: float,
                        natal_lagna_lon: float, natal_saturn_lon: float,
                        natal_jupiter_lon: float, natal_seventh_sign: int) -> dict:
    """Compute boolean transit factors at a moment."""
    jd = _datetime_to_jd(at_dt)
    sat_lon = _sidereal_lon(jd, "Saturn")
    jup_lon = _sidereal_lon(jd, "Jupiter")
    rahu_lon = _sidereal_lon(jd, "Rahu")
    ketu_lon = (rahu_lon + 180) % 360
    mars_lon = _sidereal_lon(jd, "Mars")

    moon_sign = int(natal_moon_lon // 30)
    lagna_sign = int(natal_lagna_lon // 30)
    sat_sign = int(sat_lon // 30)
    jup_sign = int(jup_lon // 30)

    # Sade Sati: Saturn in 12th, 1st, or 2nd from natal Moon
    sade_sati = (sat_sign - moon_sign) % 12 in (11, 0, 1)
    # Saturn return: Saturn within ±3° of natal Saturn
    sat_return = abs((sat_lon - natal_saturn_lon + 540) % 360 - 180) < 3.0
    # Jupiter through natal 7th (marriage trigger)
    jup_in_7th = jup_sign == natal_seventh_sign
    # Jupiter trine/sextile to Moon (kendra/trikona from Moon: 5/7/9/11)
    jup_trikona_from_moon = (jup_sign - moon_sign) % 12 in (4, 6, 8, 10)
    # Rahu/Ketu within 3° of natal lagna or Moon
    rahu_on_lagna = abs((rahu_lon - natal_lagna_lon + 540) % 360 - 180) < 3.0
    rahu_on_moon = abs((rahu_lon - natal_moon_lon + 540) % 360 - 180) < 3.0
    ketu_on_lagna = abs((ketu_lon - natal_lagna_lon + 540) % 360 - 180) < 3.0
    ketu_on_moon = abs((ketu_lon - natal_moon_lon + 540) % 360 - 180) < 3.0

    return {
        "sade_sati": sade_sati,
        "saturn_return": sat_return,
        "jupiter_in_7th_sign": jup_in_7th,
        "jupiter_trikona_from_moon": jup_trikona_from_moon,
        "rahu_on_lagna": rahu_on_lagna,
        "rahu_on_moon": rahu_on_moon,
        "ketu_on_lagna": ketu_on_lagna,
        "ketu_on_moon": ketu_on_moon,
    }


# Which transit factors are *expected* to predict each event type
EVENT_TRANSIT_PREDICTORS = {
    "MARRIAGE":            ["jupiter_in_7th_sign", "jupiter_trikona_from_moon"],
    "CHILDREN_BORN":       ["jupiter_trikona_from_moon"],
    "DEATH":               ["sade_sati", "ketu_on_moon", "rahu_on_lagna"],
    "HEALTH_CRISIS":       ["sade_sati", "ketu_on_moon"],
    "MAJOR_LOSS":          ["sade_sati", "rahu_on_lagna"],
    "DIVORCE":             ["sade_sati", "rahu_on_lagna"],
    "EXILE":               ["rahu_on_lagna", "ketu_on_lagna"],
    "SPIRITUAL_AWAKENING": ["ketu_on_moon", "ketu_on_lagna"],
    "CAREER_PEAK":         ["jupiter_trikona_from_moon", "saturn_return"],
    "POLITICAL_OFFICE":    ["jupiter_trikona_from_moon"],
    "AWARD":               ["jupiter_trikona_from_moon"],
    "FOUND_BUSINESS":      ["jupiter_trikona_from_moon"],
    "CAREER_START":        ["saturn_return"],
    "IMPRISONMENT":        ["sade_sati", "rahu_on_lagna"],
    "SCANDAL":             ["rahu_on_lagna", "rahu_on_moon"],
}


def _resolve_predictors(event_type: str, use_learned: bool = True) -> list[str]:
    """Pick the predictor set: learned (if cached) or hand-coded fallback."""
    if use_learned:
        try:
            from engine.transit_learn import load_learned
            learned = load_learned()
            sel = learned.get(event_type, {}).get("learned_predictors")
            if sel:
                return sel
        except Exception:
            pass
    return EVENT_TRANSIT_PREDICTORS.get(event_type, [])


def transit_conditioned_backtest(n_negative_per_chart: int = 5,
                                  use_learned: bool = False) -> dict:
    """For each event type, compute LR conditional on (a) dasha tier match
    AND (b) at least one expected transit factor firing.

    The hypothesis: P(event | dasha_primary AND transit_match) is much
    higher than P(event | dasha_primary alone).
    """
    # Counters: positive (event) and negative (non-event year)
    # buckets: dasha_primary_only, dasha_AND_transit, dasha_with_no_transit
    pos = {evt: Counter() for evt in EVENT_PATTERNS}
    neg = {evt: Counter() for evt in EVENT_PATTERNS}

    # Cache natal-position lookups
    for chart_meta in KNOWN_CHARTS:
        try:
            from engine.chart import compute_chart
            bd = chart_meta.birthdata
            chart = compute_chart(name=chart_meta.name, date=bd["date"],
                                  time=bd["time"], tz_hours=bd["tz"],
                                  lat=bd.get("lat"), lon=bd.get("lon"))
        except Exception:
            continue
        natal_moon = chart.positions["Moon"]
        natal_lagna = chart.lagna_lon
        natal_sat = chart.positions["Saturn"]
        natal_jup = chart.positions["Jupiter"]
        seventh_sign = (int(natal_lagna // 30) + 6) % 12

        moon_lon_for_dasha = _moon_lon(chart_meta.birthdata)
        periods = vimshottari(moon_lon_for_dasha, _birth_dt(chart_meta.birthdata))

        # Positive
        for ev in chart_meta.events:
            if ev.event_type not in EVENT_PATTERNS:
                continue
            mo = ev.month if ev.month else 6
            dy = ev.day if ev.day else 15
            moment = dt.datetime(ev.year, mo, dy)
            md, ad = current_dasha(chart, moment)
            if md is None:
                continue
            pattern = EVENT_PATTERNS[ev.event_type]
            md_t = _classify(md.lord, pattern["primary"], pattern["secondary"])
            ad_t = _classify(ad.lord if ad else None,
                             pattern["primary"], pattern["secondary"])
            dasha_match = "primary" in (md_t, ad_t)
            tf = _transit_factors_at(moment, natal_moon, natal_lagna,
                                      natal_sat, natal_jup, seventh_sign)
            transit_match = any(tf.get(k) for k in _resolve_predictors(ev.event_type, use_learned))
            pos[ev.event_type]["total"] += 1
            if dasha_match and transit_match:
                pos[ev.event_type]["dasha_AND_transit"] += 1
            elif dasha_match:
                pos[ev.event_type]["dasha_only"] += 1
            elif transit_match:
                pos[ev.event_type]["transit_only"] += 1
            else:
                pos[ev.event_type]["neither"] += 1

        # Negative
        for evt in EVENT_PATTERNS.keys():
            negs = _sample_negative_years(chart_meta, evt, n_negative_per_chart)
            for y in negs:
                moment = dt.datetime(y, 6, 15)
                md, ad = current_dasha(chart, moment)
                if md is None:
                    continue
                pattern = EVENT_PATTERNS[evt]
                md_t = _classify(md.lord, pattern["primary"], pattern["secondary"])
                ad_t = _classify(ad.lord if ad else None,
                                 pattern["primary"], pattern["secondary"])
                dasha_match = "primary" in (md_t, ad_t)
                tf = _transit_factors_at(moment, natal_moon, natal_lagna,
                                          natal_sat, natal_jup, seventh_sign)
                transit_match = any(tf.get(k) for k in _resolve_predictors(evt, use_learned))
                neg[evt]["total"] += 1
                if dasha_match and transit_match:
                    neg[evt]["dasha_AND_transit"] += 1
                elif dasha_match:
                    neg[evt]["dasha_only"] += 1
                elif transit_match:
                    neg[evt]["transit_only"] += 1
                else:
                    neg[evt]["neither"] += 1

    # Compute LRs for the conjunction
    out = {}
    for evt in EVENT_PATTERNS.keys():
        if pos[evt]["total"] == 0 or neg[evt]["total"] == 0:
            continue
        p_both_pos = pos[evt]["dasha_AND_transit"] / pos[evt]["total"]
        p_both_neg = neg[evt]["dasha_AND_transit"] / neg[evt]["total"]
        p_dasha_pos = (pos[evt]["dasha_AND_transit"] + pos[evt]["dasha_only"]) / pos[evt]["total"]
        p_dasha_neg = (neg[evt]["dasha_AND_transit"] + neg[evt]["dasha_only"]) / neg[evt]["total"]

        out[evt] = {
            "n_positive": pos[evt]["total"],
            "n_negative": neg[evt]["total"],
            "P_dasha_AND_transit_pos": round(p_both_pos, 4),
            "P_dasha_AND_transit_neg": round(p_both_neg, 4),
            "P_dasha_only_pos":        round(p_dasha_pos, 4),
            "P_dasha_only_neg":        round(p_dasha_neg, 4),
            "LR_dasha_only":   round(p_dasha_pos / p_dasha_neg, 3) if p_dasha_neg > 0 else None,
            "LR_dasha_AND_transit": round(p_both_pos / p_both_neg, 3) if p_both_neg > 0 else None,
            "lift_from_transit_conditioning":
                round((p_both_pos / p_both_neg if p_both_neg > 0 else 0)
                      - (p_dasha_pos / p_dasha_neg if p_dasha_neg > 0 else 0), 3),
        }
    return {"by_event_type": out}


def print_report():
    r = transit_conditioned_backtest()
    print("=" * 95)
    print("DASHA-ONLY vs DASHA+TRANSIT likelihood ratios")
    print("=" * 95)
    print(f"{'event':22s} {'n+':>3s} {'n-':>3s}  "
          f"{'LR_dasha':>9s}  {'LR_d+t':>8s}  {'lift':>7s}")
    rows = []
    for evt, b in r["by_event_type"].items():
        rows.append((b["lift_from_transit_conditioning"] or 0, evt, b))
    rows.sort(reverse=True)
    for lift, evt, b in rows:
        marker = "↑" if lift > 0.2 else ("↓" if lift < -0.2 else "·")
        lr_d = b["LR_dasha_only"]
        lr_dt = b["LR_dasha_AND_transit"]
        print(f"  {evt:20s} {b['n_positive']:3d} {b['n_negative']:3d}   "
              f"{lr_d if lr_d is not None else 'inf':>8}  "
              f"{lr_dt if lr_dt is not None else 'inf':>8}   "
              f"{marker}{lift:+.3f}")


if __name__ == "__main__":
    print_report()
