import sys
import swisseph as swe
from datetime import datetime, timedelta

swe.set_ephe_path('')

def get_planet_lon(jd, planet):
    pos, _ = swe.calc_ut(jd, planet, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    return pos[0]

def analyze_transits(start_year=2026, start_month=6, start_day=30, days_to_scan=365):
    print("--- TRANSIT ANALYSIS FOR ASSET SALE (2026-2027) ---")
    start_jd = swe.julday(start_year, start_month, start_day, 12.0)
    
    # Manoj's key property planets:
    # 4th Lord (Property) = Jupiter
    # Karaka for Land = Mars
    # 11th Lord (Gains) = Venus
    
    for i in range(0, days_to_scan, 5):
        jd = start_jd + i
        date = datetime(start_year, start_month, start_day) + timedelta(days=i)
        
        # Set Ayanamsa (Lahiri)
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        
        jup_lon = get_planet_lon(jd, swe.JUPITER) % 360
        mar_lon = get_planet_lon(jd, swe.MARS) % 360
        ven_lon = get_planet_lon(jd, swe.VENUS) % 360
        
        jup_rasi = int(jup_lon / 30)
        mar_rasi = int(mar_lon / 30)
        ven_rasi = int(ven_lon / 30)
        
        RASIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        # Jupiter enters Cancer (exaltation, 8th house - huge for liquidating assets)
        # Mars transits 4th house (Pisces) or 11th house (Libra)
        # Venus transits 11th house (Libra)
        
        if jup_rasi == 3: # Cancer (Exalted Jupiter in 8th house)
            print(f"{date.strftime('%Y-%m-%d')} - Jupiter in Cancer (EXALTED in 8th House - Liquidation/Gains)")
            break # Just need to know when it hits
            
    # Check Mars transiting his 4th house (Pisces) or 11th house (Libra)
    print("\n--- MARS (Real Estate Karaka) Transits ---")
    for i in range(0, days_to_scan, 10):
        jd = start_jd + i
        date = datetime(start_year, start_month, start_day) + timedelta(days=i)
        mar_lon = get_planet_lon(jd, swe.MARS) % 360
        mar_rasi = int(mar_lon / 30)
        
        if mar_rasi == 11: # Pisces (4th House)
            print(f"{date.strftime('%Y-%m-%d')} - Mars in Pisces (4th House - Activating Property)")
        elif mar_rasi == 6: # Libra (11th House)
            print(f"{date.strftime('%Y-%m-%d')} - Mars in Libra (11th House - High Gains from property)")

    # Check Venus (11th Lord of Gains) transiting 11th House
    print("\n--- VENUS (Lord of Gains) Transits ---")
    for i in range(0, days_to_scan, 5):
        jd = start_jd + i
        date = datetime(start_year, start_month, start_day) + timedelta(days=i)
        ven_lon = get_planet_lon(jd, swe.VENUS) % 360
        ven_rasi = int(ven_lon / 30)
        
        if ven_rasi == 6: # Libra (11th House - Own Sign)
            print(f"{date.strftime('%Y-%m-%d')} - Venus in Libra (11th House - Massive Gains)")

analyze_transits()
