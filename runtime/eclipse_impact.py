"""Eclipse Impact — Solar/Lunar eclipse analysis on natal chart.

Source: BPHS, Phaladeepika.
Eclipses occur when Sun/Moon align with Rahu/Ketu axis.
Impact on natal chart depends on:
  - Distance from natal Sun/Moon (smaller = more impact)
  - House the eclipse falls in
  - Aspect to natal points
"""
import sys, datetime as dt
sys.path.insert(0, ".")
import swisseph as swe
from transit_engine import transit_positions

swe.set_sid_mode(swe.SIDM_LAHIRI)

from vedic_core import RASIS  # canonical 12 signs


def find_eclipses(year_from, year_to):
    """Find solar + lunar eclipses in a year range using Swiss Ephemeris."""
    eclipses = []

    # Solar eclipses
    jd_start = swe.julday(year_from, 1, 1, 0, swe.GREG_CAL)
    jd_end = swe.julday(year_to, 12, 31, 23.99, swe.GREG_CAL)
    cur = jd_start

    while cur < jd_end:
        try:
            ret, tret = swe.sol_eclipse_when_glob(cur, 0)
            if ret < 0 or tret[0] > jd_end: break
            ecl_jd = tret[0]
            yr, mo, dy, hr = swe.revjul(ecl_jd, swe.GREG_CAL)
            ecl_dt = dt.datetime(yr, mo, dy, int(hr), int((hr - int(hr)) * 60))
            eclipses.append({"type": "Solar", "datetime": ecl_dt, "jd": ecl_jd})
            cur = ecl_jd + 5
        except Exception:
            break

    # Lunar eclipses
    cur = jd_start
    while cur < jd_end:
        try:
            ret, tret = swe.lun_eclipse_when(cur)
            if ret < 0 or tret[0] > jd_end: break
            ecl_jd = tret[0]
            yr, mo, dy, hr = swe.revjul(ecl_jd, swe.GREG_CAL)
            ecl_dt = dt.datetime(yr, mo, dy, int(hr), int((hr - int(hr)) * 60))
            eclipses.append({"type": "Lunar", "datetime": ecl_dt, "jd": ecl_jd})
            cur = ecl_jd + 5
        except Exception:
            break

    eclipses.sort(key=lambda e: e["datetime"])
    return eclipses


def analyze_eclipse_impact(natal_chart, eclipse_dt):
    """Analyze impact of an eclipse on a natal chart."""
    pos = natal_chart["positions"]
    lagna_idx = natal_chart["lagna_idx"]

    # Get eclipse positions
    h = eclipse_dt.hour + eclipse_dt.minute / 60.0
    jd = swe.julday(eclipse_dt.year, eclipse_dt.month, eclipse_dt.day, h, swe.GREG_CAL)
    flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    sun_x, _ = swe.calc_ut(jd, swe.SUN, flag)
    moon_x, _ = swe.calc_ut(jd, swe.MOON, flag)
    sun_lon = sun_x[0] % 360
    moon_lon = moon_x[0] % 360

    # House where eclipse falls
    eclipse_house_sun = ((int(sun_lon / 30) - lagna_idx) % 12) + 1
    eclipse_house_moon = ((int(moon_lon / 30) - lagna_idx) % 12) + 1

    # Distance from natal Sun/Moon
    natal_sun_lon = pos["Sun"]["rasi_idx"] * 30 + pos["Sun"]["deg"]
    natal_moon_lon = pos["Moon"]["rasi_idx"] * 30 + pos["Moon"]["deg"]

    sun_diff = abs((sun_lon - natal_sun_lon + 180) % 360 - 180)
    moon_diff = abs((moon_lon - natal_moon_lon + 180) % 360 - 180)

    impact = "low"
    if min(sun_diff, moon_diff) < 5:
        impact = "VERY HIGH (within 5°)"
    elif min(sun_diff, moon_diff) < 15:
        impact = "HIGH (within 15°)"
    elif min(sun_diff, moon_diff) < 30:
        impact = "MODERATE (within 30°)"

    HOUSE_THEMES = {1:"self/health",2:"wealth/family",3:"siblings",4:"home/mother",
                    5:"children",6:"work/health",7:"spouse",8:"transformation",
                    9:"father/dharma",10:"career",11:"gains",12:"loss/foreign"}

    return {
        "datetime": eclipse_dt.strftime("%Y-%m-%d %H:%M"),
        "house_sun": eclipse_house_sun,
        "house_sun_theme": HOUSE_THEMES[eclipse_house_sun],
        "house_moon": eclipse_house_moon,
        "house_moon_theme": HOUSE_THEMES[eclipse_house_moon],
        "distance_from_natal_sun": round(sun_diff, 1),
        "distance_from_natal_moon": round(moon_diff, 1),
        "impact_level": impact,
    }


def upcoming_eclipses_impact(natal_chart, years_ahead=3):
    """Find next eclipses + their impact on this chart."""
    today = dt.datetime.now()
    eclipses = find_eclipses(today.year, today.year + years_ahead)
    out = []
    for e in eclipses:
        if e["datetime"] < today: continue
        impact = analyze_eclipse_impact(natal_chart, e["datetime"])
        out.append({**e, **impact})
    return out


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print(f"=== UPCOMING ECLIPSES + IMPACT for {chart['name']} ===\n")
    eclipses = upcoming_eclipses_impact(chart, years_ahead=3)
    for e in eclipses[:10]:
        print(f"  {e['type']:6s} {e['datetime']:<18} | {e['impact_level']:<25}")
        print(f"        house from native: H{e['house_sun']} ({e['house_sun_theme']})")
        print(f"        distance from natal Sun/Moon: {e['distance_from_natal_sun']:.1f}° / {e['distance_from_natal_moon']:.1f}°")
        print()
