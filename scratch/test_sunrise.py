import swisseph as swe
import datetime

def get_gulika_mandi(year, month, day, decimal_hour, lat, lon):
    # Local noon UTC to find sunrise/sunset around that day
    jd_noon = swe.julday(year, month, day, 6.0) # Noon IST = 6.5 UT
    
    # Calculate sunrise/sunset on current day
    _, tret_rise = swe.rise_trans(jd_noon, swe.SUN, swe.CALC_RISE, (lon, lat, 0))
    s1 = tret_rise[0]
    
    _, tret_set = swe.rise_trans(jd_noon, swe.SUN, swe.CALC_SET, (lon, lat, 0))
    s2 = tret_set[0]
    
    # Calculate next day's sunrise
    _, tret_rise_next = swe.rise_trans(jd_noon + 1, swe.SUN, swe.CALC_RISE, (lon, lat, 0))
    s3 = tret_rise_next[0]
    
    # Birth JD
    jd_birth = swe.julday(year, month, day, decimal_hour - 5.5) # IST to UT
    
    # Vedic weekday (Sunday=0, Monday=1, ..., Saturday=6)
    # Python weekday(): Monday=0, Tuesday=1...
    # Let's get the civil weekday first
    import datetime
    dt_birth = datetime.date(year, month, day)
    civil_weekday = dt_birth.weekday()
    vedic_weekday = (civil_weekday + 1) % 7
    
    # Adjust for birth before sunrise
    is_before_sunrise = jd_birth < s1
    if is_before_sunrise:
        # Birth belongs to previous Vedic day
        vedic_weekday = (vedic_weekday - 1) % 7
        # Recompute sunrise/sunset relative to previous day
        _, tret_rise_prev = swe.rise_trans(jd_noon - 1, swe.SUN, swe.CALC_RISE, (lon, lat, 0))
        s3 = s2
        s2 = s1
        s1 = tret_rise_prev[0]
        
    is_daytime = s1 <= jd_birth < s2
    
    DAY_SATURN_PART = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 0}
    NIGHT_SATURN_PART = {0: 2, 1: 1, 2: 0, 3: 6, 4: 5, 5: 4, 6: 3}
    
    if is_daytime:
        duration = s2 - s1
        part_dur = duration / 8.0
        part_idx = DAY_SATURN_PART[vedic_weekday]
        jd_gulika = s1 + part_idx * part_dur
        jd_mandi = s1 + (part_idx + 0.5) * part_dur
    else:
        # Nighttime (could be after sunset or before sunrise of next civil day)
        if jd_birth >= s2:
            # After sunset, before next sunrise
            duration = s3 - s2
            part_dur = duration / 8.0
            part_idx = NIGHT_SATURN_PART[vedic_weekday]
            jd_gulika = s2 + part_idx * part_dur
            jd_mandi = s2 + (part_idx + 0.5) * part_dur
        else:
            # Before sunrise (should have been caught by prior-day adjust but let's be robust)
            # Recompute next day sunrise if needed
            duration = s2 - s1 # here s1 is prev day sunrise, s2 is prev day sunset, jd_birth < s1 was handled
            part_dur = (s2 - s1) / 8.0
            part_idx = NIGHT_SATURN_PART[vedic_weekday]
            jd_gulika = s1 + part_idx * part_dur
            jd_mandi = s1 + (part_idx + 0.5) * part_dur
            
    # Calculate Ascendant longitudes at Gulika and Mandi times
    asc_gul = swe.houses_ex(jd_gulika, lat, lon, b"P")[0][0]
    asc_man = swe.houses_ex(jd_mandi, lat, lon, b"P")[0][0]
    
    lon_gul = (asc_gul - swe.get_ayanamsa_ut(jd_gulika)) % 360
    lon_man = (asc_man - swe.get_ayanamsa_ut(jd_mandi)) % 360
    
    return lon_gul, lon_man

# Test with Manoj's chart birthdata: 1980-04-23, 11:30 AM IST (noonish)
lon_g, lon_m = get_gulika_mandi(1980, 4, 23, 11.5, 11.0, 77.0)
print("Gulika Longitude:", lon_g, "Sign:", int(lon_g/30))
print("Mandi Longitude:", lon_m, "Sign:", int(lon_m/30))
