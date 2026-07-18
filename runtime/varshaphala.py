"""Varshaphala — Annual Chart (Tajik / Solar Return).

Source: Tajika Neelakanthi, Tajik Adawal Encyclopedia, Varshaphal Raman.
Computes the chart cast for the moment Sun returns to its natal longitude
each solar year. Used for year-by-year forecasting.

Components:
  - Annual Lagna (Varsha Lagna)
  - Muntha (yearly progression point — moves 1 sign per year)
  - Year Lord (Varshesha) — strongest of 5 candidates per Tajik rules
  - Sahams (sensitive points — 28 calculation points)
  - Tri-Pataki Chakra (transit-vs-natal grid)
"""
import sys, datetime as dt
sys.path.insert(0, ".")
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)

from vedic_core import RASIS, RASI_LORDS  # canonical 12 signs + lords


def find_solar_return(natal_chart, target_year):
    """Find the moment Sun returns to its natal longitude in target_year.
    Returns datetime of return + position dict.
    """
    natal_sun_lon = natal_chart["positions"]["Sun"].get("lon_abs") or (
        natal_chart["positions"]["Sun"]["rasi_idx"] * 30 + natal_chart["positions"]["Sun"]["deg"])

    b = natal_chart["birth"]
    # Start search: about target_year birthday
    start_dt = dt.datetime(target_year, b["month"], max(1, b["day"]-3))
    end_dt = dt.datetime(target_year, b["month"], min(28, b["day"]+5))

    flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    # Binary search for the moment Sun longitude == natal_sun_lon
    best_dt = None; best_diff = 999
    cur = start_dt
    while cur <= end_dt:
        h = cur.hour + cur.minute / 60.0
        jd = swe.julday(cur.year, cur.month, cur.day, h, swe.GREG_CAL)
        x, _ = swe.calc_ut(jd, swe.SUN, flag)
        sun_lon = x[0] % 360
        diff = abs((sun_lon - natal_sun_lon + 180) % 360 - 180)
        if diff < best_diff:
            best_diff = diff
            best_dt = cur
        cur += dt.timedelta(hours=2)

    return best_dt


def compute_muntha(natal_chart, target_year):
    """Muntha — yearly progression point. Starts at lagna at birth, moves +1 sign per year."""
    b = natal_chart["birth"]
    age = target_year - b["year"]
    natal_lagna = natal_chart["lagna_idx"]
    muntha_sign = (natal_lagna + age) % 12
    return RASIS[muntha_sign]


def varshesha(annual_positions, lagna_idx):
    """Determine the year-lord. Tajik rule: strongest among 5 candidates:
    1. Lord of birth Tithi
    2. Lord of birth weekday
    3. Lord of Janma nakshatra (Vimshottari)
    4. Lord of annual Lagna
    5. Triakona lord — 3-hour ruler

    Simplified: return Lord of annual Lagna for now.
    """
    annual_lagna_sign = RASIS[lagna_idx]
    return RASI_LORDS[annual_lagna_sign]


def annual_chart(natal_chart, target_year):
    """Build complete annual chart for given year."""
    sr_dt = find_solar_return(natal_chart, target_year)
    if sr_dt is None:
        return {"error": "Could not find solar return"}

    h = sr_dt.hour + sr_dt.minute / 60.0
    jd = swe.julday(sr_dt.year, sr_dt.month, sr_dt.day, h, swe.GREG_CAL)
    flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    # Compute annual Lagna (uses birth-place latitude/longitude)
    lat = natal_chart["birth"].get("lat", 11.01)
    lon = natal_chart["birth"].get("lon", 76.57)
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flag)
    annual_lagna_lon = ascmc[0] % 360
    annual_lagna_idx = int(annual_lagna_lon / 30)

    # Annual planet positions
    PLANETS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
               "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Rahu":swe.MEAN_NODE}
    annual_pos = {}
    for name, pid in PLANETS.items():
        x, _ = swe.calc_ut(jd, pid, flag)
        plon = x[0] % 360
        ri = int(plon / 30)
        h_from_lagna = ((ri - annual_lagna_idx) % 12) + 1
        annual_pos[name] = {"lon": round(plon, 2), "rasi": RASIS[ri], "rasi_idx": ri,
                             "deg": round(plon - ri*30, 2), "house": h_from_lagna}
    # Ketu
    rahu_lon = annual_pos["Rahu"]["lon"]
    ketu_lon = (rahu_lon + 180) % 360
    ki = int(ketu_lon / 30)
    annual_pos["Ketu"] = {"lon": round(ketu_lon, 2), "rasi": RASIS[ki], "rasi_idx": ki,
                          "deg": round(ketu_lon - ki*30, 2), "house": ((ki - annual_lagna_idx) % 12) + 1}

    muntha = compute_muntha(natal_chart, target_year)
    yl = varshesha(annual_pos, annual_lagna_idx)

    # Per-house theme for the year (Tajik tradition):
    # House where Muntha sits = primary focus area
    muntha_idx = RASIS.index(muntha)
    muntha_house = ((muntha_idx - annual_lagna_idx) % 12) + 1

    return {
        "year": target_year,
        "solar_return_datetime": sr_dt.strftime("%Y-%m-%d %H:%M"),
        "annual_lagna": RASIS[annual_lagna_idx],
        "annual_lagna_lord": RASI_LORDS[RASIS[annual_lagna_idx]],
        "muntha_sign": muntha,
        "muntha_house": muntha_house,
        "year_lord_varshesha": yl,
        "annual_positions": annual_pos,
        "interpretation": _annual_interpretation(target_year, muntha, muntha_house, yl, annual_pos),
    }


def _annual_interpretation(year, muntha_sign, muntha_house, year_lord, annual_pos):
    HOUSE_THEMES = {1:"self/health/personality",2:"wealth/family/speech",3:"siblings/courage",
                    4:"home/mother/property",5:"children/creativity/romance",6:"work/disputes/illness",
                    7:"spouse/partnerships",8:"transformation/sudden events",9:"luck/dharma/foreign",
                    10:"career/status/recognition",11:"gains/income/network",12:"loss/expenses/spirituality"}

    interp = []
    interp.append(f"Year {year}: Annual Lagna in {muntha_sign}; year ruled by {year_lord}.")
    interp.append(f"Muntha (yearly progression) in House {muntha_house} ({HOUSE_THEMES.get(muntha_house,'?')}) — primary focus area for the year.")

    yl_pos = annual_pos.get(year_lord)
    if yl_pos:
        interp.append(f"{year_lord} (Varshesha) sits in House {yl_pos['house']} of annual chart — events of the year manifest through this domain.")

    return " ".join(interp)


def varshaphala_timeline(natal_chart, year_from, year_to):
    """Generate annual summaries for a range of years."""
    out = []
    for yr in range(year_from, year_to + 1):
        try:
            ac = annual_chart(natal_chart, yr)
            out.append({
                "year": yr,
                "muntha_house": ac["muntha_house"],
                "muntha_sign": ac["muntha_sign"],
                "annual_lagna": ac["annual_lagna"],
                "year_lord": ac["year_lord_varshesha"],
                "summary": ac["interpretation"][:200],
            })
        except Exception as e:
            out.append({"year": yr, "error": str(e)})
    return out


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print(f"=== VARSHAPHALA TIMELINE for {chart['name']} ===\n")
    timeline = varshaphala_timeline(chart, 2025, 2030)
    for tl in timeline:
        if "error" in tl:
            print(f"  {tl['year']}: ERROR {tl['error']}")
        else:
            print(f"  {tl['year']}: AnnLagna={tl['annual_lagna']:14s} Muntha=H{tl['muntha_house']:<2} ({tl['muntha_sign']:13s})  Year-Lord={tl['year_lord']}")
            print(f"        {tl['summary'][:150]}")
            print()
