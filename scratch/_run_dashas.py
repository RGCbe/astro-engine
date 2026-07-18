import json
import sys
import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.dasha_compute import calculate_vimshottari

def main():
    # Manoj birth date: 1996-05-25 20:25
    manoj_birth = datetime.datetime(1996, 5, 25, 20, 25)
    manoj_moon_lon = 131.3121
    manoj_dasha = calculate_vimshottari(manoj_moon_lon, manoj_birth)
    
    # Kayalvizhi birth date: 1997-06-26 04:07
    kayalvizhi_birth = datetime.datetime(1997, 6, 26, 4, 7)
    kayalvizhi_moon_lon = 319.7501
    kayalvizhi_dasha = calculate_vimshottari(kayalvizhi_moon_lon, kayalvizhi_birth)
    
    print("=== MANOJ CURRENT DASHA ===")
    curr_m = manoj_dasha["current_maha_dasha"]
    curr_a = manoj_dasha.get("current_antardasha")
    print(f"Maha Dasha: {curr_m['lord']} (From: {curr_m['start']} To: {curr_m['end']})")
    print(f"Antar Dasha: {curr_a['lord']} (From: {curr_a['start']} To: {curr_a['end']})")
    
    print("\n=== KAYALVIZHI CURRENT DASHA ===")
    curr_km = kayalvizhi_dasha["current_maha_dasha"]
    curr_ka = kayalvizhi_dasha.get("current_antardasha")
    print(f"Maha Dasha: {curr_km['lord']} (From: {curr_km['start']} To: {curr_km['end']})")
    print(f"Antar Dasha: {curr_ka['lord']} (From: {curr_ka['start']} To: {curr_ka['end']})")

if __name__ == "__main__":
    main()
