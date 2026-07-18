"""Tri-Pataki Chakra — Tajik annual transit grid.

Source: Tajika Neelakanthi, Tajik Adawal Encyclopedia.

Tri-Pataki Chakra = "three-banner grid" — used in Varshaphala (annual chart)
to map transit positions of all 9 planets relative to natal Moon's nakshatra.
The grid has 27 nakshatras × 9 planets, marked with bindus.
Bindus indicate auspicious/inauspicious days for that planet's matters in the year.
"""
import sys, datetime as dt
sys.path.insert(0, ".")
from vedic_core import NAKSHATRAS, NAK_LORDS_27

PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]


def tri_pataki(natal_chart, target_dt=None):
    """Compute Tri-Pataki Chakra grid for given date.

    Returns: 27 × 9 grid showing if each planet is favorably/unfavorably placed
    relative to native's natal Moon nakshatra.
    """
    if target_dt is None: target_dt = dt.datetime.now()
    from transit_engine import transit_positions

    natal_moon_nak = natal_chart.get("janma_nakshatra")
    if natal_moon_nak not in NAKSHATRAS:
        return None
    natal_nak_idx = NAKSHATRAS.index(natal_moon_nak)

    transits = transit_positions(target_dt)

    grid = {}
    for p in PLANETS:
        if p not in transits: continue
        plon = transits[p]["lon"]
        nak_idx = int(plon / (360/27))
        nak_name = NAKSHATRAS[nak_idx]

        # Position relative to natal Moon nakshatra
        offset = (nak_idx - natal_nak_idx) % 27

        # Tara classification (1-9 cycling)
        tara_num = (offset % 9) + 1
        TARA_TYPES = {1:"Janma",2:"Sampat",3:"Vipat",4:"Kshema",5:"Pratyari",6:"Sadhaka",7:"Vadha",8:"Mitra",9:"Atimitra"}
        GOOD_TARAS = [2, 4, 6, 8, 9]

        verdict = "good" if tara_num in GOOD_TARAS else "challenging"

        grid[p] = {
            "current_nak": nak_name,
            "current_nak_lord": NAK_LORDS_27[nak_idx],
            "offset_from_natal_moon": offset,
            "tara_number": tara_num,
            "tara_type": TARA_TYPES[tara_num],
            "verdict": verdict,
            "is_favorable": tara_num in GOOD_TARAS,
        }
    return grid


def annual_tri_pataki_summary(natal_chart, year):
    """Summarize Tri-Pataki for the year — sample dates."""
    summary = {"year": year, "samples": []}
    for month in [1, 4, 7, 10]:  # quarterly
        d = dt.datetime(year, month, 15)
        grid = tri_pataki(natal_chart, d)
        if grid:
            favorable = [p for p, g in grid.items() if g["is_favorable"]]
            challenging = [p for p, g in grid.items() if not g["is_favorable"]]
            summary["samples"].append({
                "date": d.strftime("%Y-%m-%d"),
                "favorable_planets": favorable,
                "challenging_planets": challenging,
            })
    return summary


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    grid = tri_pataki(chart)
    print(f"=== TRI-PATAKI CHAKRA for {chart['name']} (today) ===\n")
    print(f"Natal Moon Nakshatra: {chart.get('janma_nakshatra')}\n")
    print(f"{'Planet':<10}{'Current Nak':<22}{'Offset':<8}{'Tara':<10}{'Verdict'}")
    for p, g in grid.items():
        print(f"  {p:<10}{g['current_nak']:<22}{g['offset_from_natal_moon']:<8}{g['tara_type']:<10}{g['verdict']}")

    print(f"\n=== ANNUAL TRI-PATAKI SUMMARY for {dt.datetime.now().year} ===")
    sm = annual_tri_pataki_summary(chart, dt.datetime.now().year)
    for s in sm["samples"]:
        print(f"\n  {s['date']}:")
        print(f"    Favorable: {', '.join(s['favorable_planets'])}")
        print(f"    Challenging: {', '.join(s['challenging_planets'])}")
