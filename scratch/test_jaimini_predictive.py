import asyncio
import os
import sys
from datetime import datetime
import swisseph as swe

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from main import jathagam, BirthData
from engine.jaimini_full import get_jaimini_analysis
from runtime.jaimini_full import _lookup_active, all_jaimini_dashas_full

from scratch.optimize_ultimate_conjoined import FILMS

async def main():
    vijay_birth = BirthData(year=1974, month=6, day=22, time="12:00", lat=13.0827, lon=80.2707, focus="general")
    chart = await jathagam(vijay_birth)
    
    pos = chart.get("all_planet_positions", {})
    asc_sid = (swe.houses_ex(swe.julday(1974, 6, 22, 12.0 - 5.5), 13.0827, 80.2707, b"P")[0][0] - swe.get_ayanamsa_ut(swe.julday(1974, 6, 22, 12.0 - 5.5))) % 360
    
    # Format compatible chart dictionary
    from jaimini_full import jaimini_summary, all_jaimini_dashas_full
    SIGN_NAMES = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    chart_dict = {
        "lagna_idx": int(asc_sid / 30) % 12,
        "positions": {},
        "birth": {
            "year": 1974,
            "month": 6,
            "day": 22,
            "hour": 12,
            "min": 0
        }
    }
    for p, pdata in pos.items():
        if p in ["Gulika", "Mandi"]: continue
        lon = pdata["longitude"]
        rasi_idx = int(lon / 30) % 12
        chart_dict["positions"][p] = {
            "deg": lon % 30,
            "rasi_idx": rasi_idx,
            "rasi": SIGN_NAMES[rasi_idx],
            "lon": lon,
            "lon_abs": lon
        }

    dashas = all_jaimini_dashas_full(chart_dict)
    
    print("Evaluating Jaimini Dashas active signs/planets for 68 movies:")
    print("-" * 120)
    print(f"{'No.':<4} | {'Movie Name':<28} | {'Status':<10} | {'Sthira':<12} | {'Mandooka':<12} | {'Padakrama':<12} | {'KKG':<12} | {'LKG':<12} | {'Brahma':<12}")
    print("-" * 120)
    
    for f in FILMS:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        
        sthira_act = _lookup_active(dashas["sthira_jaimini"], dt_obj)
        mandooka_act = _lookup_active(dashas["mandooka_jaimini"], dt_obj)
        padakrama_act = _lookup_active(dashas["padakrama"], dt_obj)
        kkg_act = _lookup_active(dashas["karaka_kendradi"], dt_obj)
        lkg_act = _lookup_active(dashas["lagna_kendradi"], dt_obj)
        brahma_act = _lookup_active(dashas["brahma_jaimini"], dt_obj)
        
        sthira_sign = sthira_act["sign"] if sthira_act else "—"
        mandooka_sign = mandooka_act["sign"] if mandooka_act else "—"
        padakrama_sign = padakrama_act["sign"] if padakrama_act else "—"
        kkg_pl = kkg_act["planet"] if kkg_act else "—"
        lkg_pl = lkg_act["planet"] if lkg_act else "—"
        brahma_sign = brahma_act["sign"] if brahma_act else "—"
        
        print(f"{f['num']:<4} | {f['name']:<28} | {f['status']:<10} | {sthira_sign:<12} | {mandooka_sign:<12} | {padakrama_sign:<12} | {kkg_pl:<12} | {lkg_pl:<12} | {brahma_sign:<12}")

if __name__ == "__main__":
    asyncio.run(main())
