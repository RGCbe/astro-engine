from vedic_core import RASIS, RASI_LORDS

"""Compute G. Krishnan natal chart.

Birth: 26 July 2002, 5:52 AM IST, Coimbatore (11.0168 N, 76.9558 E), Sunday
"""
import json, sys, datetime as dt
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import swisseph as swe

ATRO = Path(__import__("os").environ.get("ATRO_ROOT", Path(__file__).resolve().parent.parent))

NAME = "G. Krishnan"
BIRTH = {
    "year": 2002, "month": 7, "day": 26,
    "hour": 5, "min": 52,
    "lat": 11.0168, "lon": 76.9558,
    "place": "Coimbatore",
    "tz": 5.5,
    "weekday": "Friday",  # 26 Jul 2002 was a Friday actually — but image says Sunday
}
# Verify weekday
import calendar
day_idx = calendar.weekday(BIRTH["year"], BIRTH["month"], BIRTH["day"])
BIRTH["weekday"] = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][day_idx]


NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
              "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
              "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
              "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
              "Purva Bhadrapada","Uttara Bhadrapada","Revati"]
NAK_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
             "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury",
             "Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]



def compute():
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    yr = BIRTH["year"]; mo = BIRTH["month"]; dy = BIRTH["day"]
    hr = BIRTH["hour"]; mn = BIRTH["min"]; tz = BIRTH["tz"]
    ut_hour = hr + mn/60 - tz
    jd = swe.julday(yr, mo, dy, ut_hour)

    PLANETS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
               "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,
               "Rahu":swe.MEAN_NODE}
    positions = {}
    for name, pid in PLANETS.items():
        pos = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED)
        lon = pos[0][0]; speed = pos[0][3]
        ri = int(lon // 30); dis = lon - ri*30
        ni = int(lon // (360/27))
        pada = int((lon % (360/27)) // (360/108)) + 1
        positions[name] = {"rasi": RASIS[ri], "rasi_idx": ri,
                           "deg": round(dis,4), "lon_abs": round(lon,4),
                           "nak": NAKSHATRAS[ni], "nak_idx": ni,
                           "nak_lord": NAK_LORDS[ni], "pada": pada,
                           "retrograde": speed<0, "speed": round(speed,4)}
    rahu_lon = positions["Rahu"]["lon_abs"]
    ketu_lon = (rahu_lon + 180) % 360
    kr = int(ketu_lon // 30); kn = int(ketu_lon // (360/27))
    kp = int((ketu_lon % (360/27)) // (360/108)) + 1
    positions["Ketu"] = {"rasi": RASIS[kr], "rasi_idx": kr,
                         "deg": round(ketu_lon-kr*30,4), "lon_abs": round(ketu_lon,4),
                         "nak": NAKSHATRAS[kn], "nak_idx": kn,
                         "nak_lord": NAK_LORDS[kn], "pada": kp,
                         "retrograde": True, "speed": -0.053}

    asc_data = swe.houses_ex(jd, BIRTH["lat"], BIRTH["lon"], b'P', swe.FLG_SIDEREAL)
    asc_lon = asc_data[0][0]
    lri = int(asc_lon // 30); lagna = RASIS[lri]; ldeg = asc_lon - lri*30
    for p, pd in positions.items():
        positions[p]["house"] = (pd["rasi_idx"] - lri) % 12 + 1
    moon = positions["Moon"]

    return {
        "name": NAME, "birth": BIRTH,
        "lagna": lagna, "lagna_idx": lri,
        "lagna_deg": round(ldeg,4),
        "lagna_lord": RASI_LORDS[lagna],
        "ayanamsa": round(swe.get_ayanamsa(jd), 6),
        "positions": positions,
        "janma_nakshatra": moon["nak"],
        "janma_nakshatra_lord": moon["nak_lord"],
        "moon_rasi": moon["rasi"],
        "moon_pada": moon["pada"],
    }


def main():
    chart = compute()
    out = ATRO / "krishnan_chart.json"
    json.dump(chart, open(out, "w", encoding="utf-8"), indent=2, default=str)
    b = chart["birth"]
    print(f"\n=== {chart['name']} ===")
    print(f"Birth: {b['day']:02d}-{b['month']:02d}-{b['year']} {b['hour']:02d}:{b['min']:02d} IST ({b['weekday']})")
    print(f"Place: {b['place']} ({b['lat']} N, {b['lon']} E)")
    print(f"Lagna: {chart['lagna']} {chart['lagna_deg']:.2f}° (lord: {chart['lagna_lord']})")
    print(f"Moon: {chart['moon_rasi']} (Janma Nakshatra: {chart['janma_nakshatra']} pada {chart['moon_pada']}, lord: {chart['janma_nakshatra_lord']})")
    print(f"Ayanamsa: {chart['ayanamsa']:.4f}° (Lahiri)")
    print()
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        pd = chart["positions"][p]
        retro = " R" if pd.get("retrograde") else "  "
        print(f"  {p:<8} {pd['rasi']:<13} H{pd['house']:>2}  {pd['deg']:>6.2f}°  {pd['nak']:<18} pada {pd['pada']}{retro}")
    print(f"\nSaved: {out}")


if __name__ == "__main__":
    main()
