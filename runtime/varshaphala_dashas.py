"""Varshaphala Internal Dashas — Mudda Dasha + Patyayini Dasha.

Source: Tajika Neelakanthi, Varshaphal Raman.

Within an annual (Tajik) chart, two sub-dashas operate:

  MUDDA DASHA:
    Vimshottari-style sub-dasha system applied to the annual chart.
    Each planetary period scaled to fit 1 year (360 days).
    Sequence based on year-lord (Varshesha).

  PATYAYINI DASHA:
    Calculated from Tajik aspect strengths.
    Each planet gets days proportional to its strength in the annual chart.
    Most-strong planet gets longest period.
"""
import sys, datetime as dt
sys.path.insert(0, ".")
from vedic_core import VIMSHOTTARI_ORDER, VIMSHOTTARI_YEARS

VIMSHOTTARI_TOTAL = 120  # years


def mudda_dasha(annual_lagna_lord, year_start_dt):
    """Compute Mudda Dasha periods for the year.

    Periods within 1 year: Vimshottari proportions / 120, scaled to 360 days.
    """
    if annual_lagna_lord not in VIMSHOTTARI_ORDER:
        return []

    # Sequence starts from annual lagna lord
    start_idx = VIMSHOTTARI_ORDER.index(annual_lagna_lord)

    timeline = []
    cur_start = year_start_dt
    for i in range(9):
        lord = VIMSHOTTARI_ORDER[(start_idx + i) % 9]
        days = VIMSHOTTARI_YEARS[lord] / VIMSHOTTARI_TOTAL * 365.25
        cur_end = cur_start + dt.timedelta(days=days)
        timeline.append({
            "lord": lord,
            "start": cur_start,
            "end": cur_end,
            "days": round(days, 1),
        })
        cur_start = cur_end
    return timeline


def patyayini_dasha(planet_strengths, year_start_dt):
    """Compute Patyayini Dasha — planets get days proportional to strength.

    Input: planet_strengths = {planet: strength_value} (0-60 range)
    Output: list of period dicts, sorted by strength descending.
    """
    total_strength = sum(planet_strengths.values()) or 1
    timeline = []
    cur_start = year_start_dt

    sorted_planets = sorted(planet_strengths.items(), key=lambda x: -x[1])
    for planet, strength in sorted_planets:
        # Allocation: proportion of 360 days
        days = (strength / total_strength) * 365.25
        cur_end = cur_start + dt.timedelta(days=days)
        timeline.append({
            "planet": planet,
            "strength": round(strength, 1),
            "start": cur_start,
            "end": cur_end,
            "days": round(days, 1),
        })
        cur_start = cur_end
    return timeline


def annual_dashas_summary(natal_chart, target_year):
    """Compute both Mudda + Patyayini for given year."""
    from varshaphala import annual_chart
    ac = annual_chart(natal_chart, target_year)
    if "error" in ac:
        return {"error": ac["error"]}

    annual_lagna_lord = ac["annual_lagna_lord"]
    sr_dt = dt.datetime.strptime(ac["solar_return_datetime"], "%Y-%m-%d %H:%M")

    md = mudda_dasha(annual_lagna_lord, sr_dt)

    # Quick strength approximation for Patyayini: planet's house strength
    annual_pos = ac["annual_positions"]
    KENDRA = [1, 4, 7, 10]
    TRIKONA = [1, 5, 9]
    DUSTHANA = [6, 8, 12]
    strengths = {}
    for p, pd in annual_pos.items():
        s = 30
        if pd["house"] in KENDRA: s += 15
        if pd["house"] in TRIKONA: s += 10
        if pd["house"] in DUSTHANA: s -= 15
        strengths[p] = max(5, s)

    pd_dasha = patyayini_dasha(strengths, sr_dt)

    return {
        "year": target_year,
        "annual_lagna_lord": annual_lagna_lord,
        "solar_return": ac["solar_return_datetime"],
        "mudda_dasha": md,
        "patyayini_dasha": pd_dasha,
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    res = annual_dashas_summary(chart, 2026)
    print(f"=== VARSHAPHALA DASHAS for {chart['name']}, year {res['year']} ===")
    print(f"Annual Lagna Lord: {res['annual_lagna_lord']}")
    print(f"Solar Return: {res['solar_return']}\n")

    print("MUDDA DASHA (Vimshottari-style sub-dasha within the year):")
    for d in res["mudda_dasha"]:
        print(f"  {d['lord']:10s}  {d['start'].strftime('%Y-%m-%d')} → {d['end'].strftime('%Y-%m-%d')}  ({d['days']} days)")

    print(f"\nPATYAYINI DASHA (strength-proportional):")
    for d in res["patyayini_dasha"]:
        print(f"  {d['planet']:10s} (str={d['strength']:>4})  {d['start'].strftime('%Y-%m-%d')} → {d['end'].strftime('%Y-%m-%d')}  ({d['days']} days)")
