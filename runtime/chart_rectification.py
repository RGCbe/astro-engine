"""Chart Rectification — back-solve birth time from known life events.

Given a chart with approximate birth time and a list of validated events,
test small adjustments to birth time and find the time that best matches events.
"""
import sys, datetime as dt, copy, json
sys.path.insert(0, ".")
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)

from vedic_core import RASIS, RASI_LORDS  # canonical 12 signs + lords


def recompute_chart(chart_template, hour, minute):
    """Recompute lagna for a candidate time."""
    b = chart_template["birth"]
    h_decimal = hour + minute / 60.0
    jd = swe.julday(b["year"], b["month"], b["day"], h_decimal, swe.GREG_CAL)
    flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    cusps, ascmc = swe.houses_ex(jd, b["lat"], b["lon"], b'P', flag)
    asc_lon = ascmc[0] % 360
    lagna_idx = int(asc_lon / 30)

    new_chart = copy.deepcopy(chart_template)
    new_chart["lagna_idx"] = lagna_idx
    new_chart["lagna"] = RASIS[lagna_idx]
    new_chart["lagna_lord"] = RASI_LORDS[RASIS[lagna_idx]]
    new_chart["birth"] = {**b, "hour": hour, "min": minute}

    # Recompute houses for all planets
    for p, pd in new_chart["positions"].items():
        new_h = ((pd["rasi_idx"] - lagna_idx) % 12) + 1
        pd["house"] = new_h

    return new_chart


def score_event_match(chart, event_date, event_type):
    """Score how well a chart explains a given event happening on event_date."""
    from event_predictor_v2 import scan_year_v2

    year = event_date.year
    events = scan_year_v2(chart, year, sample_days=10, min_severity=2)
    score = 0
    for ev_key, ev_data in events.items():
        if event_type.lower() in ev_data["category"].lower():
            # Check if event_date falls in window
            if ev_data["first"] <= event_date <= ev_data["last"]:
                score += ev_data["max_sev"] * 2
            else:
                # Partial credit for nearness
                gap = min(abs((ev_data["first"] - event_date).days),
                          abs((ev_data["last"] - event_date).days))
                if gap < 60:
                    score += max(0, ev_data["max_sev"] - gap // 30)
    return score


def rectify_birth_time(chart, validated_events, search_minutes=60):
    """Search +/- search_minutes around given birth time for best fit.

    validated_events: list of {date, type} dicts
      e.g. [{"date": dt(1996,8,25), "type": "father"}, {"date": dt(1999,...), "type": "sibling"}]
    """
    b = chart["birth"]
    base_hour = b["hour"]
    base_min = b["min"]

    candidates = []
    for delta_min in range(-search_minutes, search_minutes + 1, 4):
        cand_total_min = base_hour * 60 + base_min + delta_min
        cand_h = (cand_total_min // 60) % 24
        cand_m = cand_total_min % 60

        cand_chart = recompute_chart(chart, cand_h, cand_m)
        total_score = 0
        for ev in validated_events:
            total_score += score_event_match(cand_chart, ev["date"], ev["type"])

        candidates.append({
            "birth_time": f"{cand_h:02d}:{cand_m:02d}",
            "delta_min": delta_min,
            "lagna": cand_chart["lagna"],
            "score": total_score,
        })

    candidates.sort(key=lambda c: -c["score"])
    return candidates


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    # Manoj's confirmed events
    validated = [
        {"date": dt.datetime(1996, 8, 25), "type": "father"},
        {"date": dt.datetime(2017, 9, 1), "type": "father"},  # Sun MD start period
        {"date": dt.datetime(2024, 7, 15), "type": "self_accident"},
    ]

    print(f"=== CHART RECTIFICATION for {chart['name']} ===")
    print(f"Original birth time: {chart['birth']['hour']:02d}:{chart['birth']['min']:02d}\n")
    print(f"{'Time':<10}{'Δmin':<6}{'Lagna':<14}{'Score'}")

    candidates = rectify_birth_time(chart, validated, search_minutes=30)
    for c in candidates[:15]:
        print(f"  {c['birth_time']:<10}{c['delta_min']:<+6}{c['lagna']:<14}{c['score']}")

    print(f"\nBest fit: {candidates[0]['birth_time']} ({candidates[0]['lagna']}) score {candidates[0]['score']}")
    print(f"(Original was {chart['birth']['hour']:02d}:{chart['birth']['min']:02d})")
