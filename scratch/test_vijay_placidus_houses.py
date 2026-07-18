import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

import swisseph as swe
from main import jathagam, BirthData

async def main():
    # Vijay's Birth Data
    vijay_birth = BirthData(year=1974, month=6, day=22, time="12:00", lat=13.0827, lon=80.2707, focus="general")
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    
    # Calculate Julian Day
    decimal_hour = 12.0
    jd = swe.julday(1974, 6, 22, decimal_hour - 5.5)  # IST to UT
    ayan = swe.get_ayanamsa_ut(jd)
    
    # Placidus cusps
    cusps_trop, ascmc = swe.houses_ex(jd, 13.0827, 80.2707, b"P")
    cusps_sid = [(c - ayan) % 360 for c in cusps_trop]
    
    print("=" * 80)
    print("      COMPARING WHOLE-SIGN HOUSES VS PLACIDUS HOUSES FOR THALAPATHY VIJAY")
    print("=" * 80)
    print("Placidus House Cusps (Sidereal):")
    for h in range(1, 13):
        print(f"  House {h:<2}: {cusps_sid[h-1]:.4f} deg ({int(cusps_sid[h-1]/30)} rasi idx)")
        
    # Get planet longitudes
    chart = await jathagam(vijay_birth)
    pos = chart.get("all_planet_positions", {})
    
    print("\nPlanet House Comparison:")
    print(f"{'Planet':<10} | {'Longitude':<10} | {'Whole-Sign House':<18} | {'Placidus House':<18}")
    print("-" * 70)
    
    # For each planet, check house placement in Placidus vs Whole-Sign
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    for p in planets:
        lon = pos[p]["longitude"]
        
        # Whole-sign: rasi-based difference from Lagna
        # Lagna is Kanni (Virgo), rasi idx = 5
        lagna_rasi_idx = 5
        p_rasi_idx = int(lon / 30)
        ws_house = ((p_rasi_idx - lagna_rasi_idx) % 12) + 1
        
        # Placidus: find which cusp interval the planet falls into
        pl_house = 12
        for h in range(1, 12):
            c_curr = cusps_sid[h-1]
            c_next = cusps_sid[h]
            if c_curr <= c_next:
                if c_curr <= lon < c_next:
                    pl_house = h
                    break
            else: # spans 360 boundary
                if lon >= c_curr or lon < c_next:
                    pl_house = h
                    break
                    
        print(f"{p:<10} | {lon:<10.4f} | House {ws_house:<12} | House {pl_house:<12}")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
