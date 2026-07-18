"""Daily/Weekly/Monthly Transit Forecast — short-term predictions.

Combines transit_engine + dasha + panchanga to give day-by-day forecasts
for any chart over a 30/90/365 day window.
"""
import sys, datetime as dt
sys.path.insert(0, ".")
from transit_engine import detect_triggers
from granular_dasha import build_full_timeline, lookup
from panchanga import compute_panchanga
from muhurta_engine import tara_bala, chandra_bala


def daily_forecast(chart, target_date):
    """Forecast for a single day."""
    triggers = detect_triggers(chart, target_date, orb=2.0)
    tl = build_full_timeline(chart, levels=3)
    active = lookup(tl, target_date)
    pan = compute_panchanga(target_date)
    natal_nak = chart.get("janma_nakshatra")
    natal_moon = chart.get("moon_rasi")
    tb = tara_bala(natal_nak, target_date) if natal_nak else None
    cb = chandra_bala(natal_moon, target_date) if natal_moon else None

    # Score the day
    score = 0
    notes = []

    # Transit triggers
    high_triggers = [t for t in triggers if t["severity"] in ["VERY HIGH","HIGH"]]
    for t in high_triggers:
        if t["transit"] in ["Saturn","Mars","Rahu","Ketu"]:
            score -= 1
            notes.append(f"⚠ {t['label']}")
        elif t["transit"] in ["Jupiter","Venus","Moon","Mercury"]:
            score += 1
            notes.append(f"✓ {t['label']}")

    # Tara
    if tb:
        if tb["is_good"]: score += 1
        else: score -= 1
        notes.append(f"Tara: {tb['type']}")

    # Chandra Bala
    if cb:
        if cb["is_good"]: score += 1
        elif cb["is_bad"]: score -= 1
        notes.append(f"Chandra Bala: {cb['verdict']}")

    # Panchanga warnings
    if pan["is_bhadra"]: score -= 1; notes.append("⚠ Bhadra karana")
    if pan["is_amavasya"]: score -= 1; notes.append("⚠ Amavasya")

    # Verdict
    if score >= 3: verdict = "EXCELLENT day"
    elif score >= 1: verdict = "GOOD day"
    elif score >= -1: verdict = "NEUTRAL day"
    elif score >= -3: verdict = "CHALLENGING day"
    else: verdict = "DIFFICULT day — defer important matters"

    md_lord = active.get(1, {}).get("md", "?")
    ad_rec = active.get(2, {})
    ad_lord = ad_rec.get("ad", "?")

    return {
        "date": target_date.strftime("%Y-%m-%d (%a)"),
        "score": score,
        "verdict": verdict,
        "md_ad": f"{md_lord}-{ad_lord}",
        "notes": notes,
        "panchanga": {
            "tithi": pan["tithi"],
            "nakshatra": pan["nakshatra"],
            "yoga": pan["yoga"],
            "vara": pan["vara"],
        },
    }


def forecast_period(chart, start_date, num_days):
    """Forecast for a range of days."""
    out = []
    for i in range(num_days):
        d = start_date + dt.timedelta(days=i)
        f = daily_forecast(chart, d)
        out.append(f)
    return out


def find_best_days(chart, start_date, num_days=30):
    """Return only EXCELLENT and GOOD days in the period."""
    fc = forecast_period(chart, start_date, num_days)
    return [d for d in fc if d["score"] >= 1]


def find_difficult_days(chart, start_date, num_days=30):
    """Return CHALLENGING and DIFFICULT days."""
    fc = forecast_period(chart, start_date, num_days)
    return [d for d in fc if d["score"] <= -2]


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    today = dt.datetime.now()

    print(f"=== 30-DAY FORECAST for {chart['name']} (starting {today.date()}) ===\n")
    fc = forecast_period(chart, today, 30)
    print(f"{'Date':<20}{'Score':<7}{'Verdict':<25}{'MD-AD'}")
    for f in fc:
        print(f"  {f['date']:<20}{f['score']:<+7}{f['verdict']:<25}{f['md_ad']}")

    print(f"\n=== BEST DAYS (next 30 days) ===")
    best = find_best_days(chart, today, 30)
    for d in best[:10]:
        print(f"  {d['date']:<22}({d['verdict']}) — {', '.join(d['notes'][:2])}")

    print(f"\n=== CHALLENGING DAYS (next 30 days) ===")
    diff = find_difficult_days(chart, today, 30)
    for d in diff[:10]:
        print(f"  {d['date']:<22}({d['verdict']}) — {', '.join(d['notes'][:2])}")
