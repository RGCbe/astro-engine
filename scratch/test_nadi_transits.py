import asyncio
import os
import sys
from datetime import datetime
import swisseph as swe

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from main import jathagam, BirthData
from engine.nadi_jyotish import get_nadi_analysis

from scratch.optimize_ultimate_conjoined import FILMS

async def main():
    vijay_birth = BirthData(year=1974, month=6, day=22, time="12:00", lat=13.0827, lon=80.2707, focus="general")
    chart = await jathagam(vijay_birth)
    pos = chart.get("all_planet_positions", {})
    asc_sid = (swe.houses_ex(swe.julday(1974, 6, 22, 12.0 - 5.5), 13.0827, 80.2707, b"P")[0][0] - swe.get_ayanamsa_ut(swe.julday(1974, 6, 22, 12.0 - 5.5))) % 360
    
    print("Evaluating Bhrigu Nandi Nadi live transit alignments for Vijay's films:")
    print("-" * 140)
    print(f"{'No.':<4} | {'Movie Name':<28} | {'Date':<10} | {'Status':<11} | {'Alignments':<80}")
    print("-" * 140)
    
    for f in FILMS:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        
        # Calculate Nadi analysis for transit date
        res = get_nadi_analysis(
            year=1974, month=6, day=22, decimal_hour=12.0, lat=13.0827, lon=80.2707,
            planet_positions=pos, asc_sid=asc_sid, transit_dt=dt_obj
        )
        
        aligns = []
        if res.get("status") == "success":
            for al in res["transits"]["alignments"]:
                tp = al["transit_planet"]
                np = al["natal_planet"]
                asp = al["aspect"]
                asp_type = "conj" if "Conjunction" in asp else "trine" if "Trine" in asp else "opp"
                aligns.append(f"{tp}-{asp_type}-{np} (orb {al['orb_degrees']}°)")
        
        align_str = ", ".join(aligns[:4]) if aligns else "None"
        print(f"{f['num']:<4} | {f['name']:<28} | {f['date']:<10} | {f['status']:<11} | {align_str}")

if __name__ == "__main__":
    asyncio.run(main())
