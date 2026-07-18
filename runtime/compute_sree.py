"""Compute Sree Ranganathan L. natal chart using swisseph.

Birth: 18 May 1983, 17:30 IST, Coimbatore (11.0168 N, 76.9558 E)
"""
import json
import sys
import datetime as dt
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

import swisseph as swe

ATRO = Path(__import__("os").environ.get("ATRO_ROOT", Path(__file__).resolve().parent.parent))

# Birth details
NAME = "Sree Ranganathan L"
BIRTH = {
    "year": 1983, "month": 5, "day": 18,
    "hour": 17, "min": 30,
    "lat": 11.0168, "lon": 76.9558,
    "place": "Coimbatore",
    "tz": 5.5,
    "weekday": "Wednesday",
}

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vedic_core import RASIS, NAKSHATRAS, NAK_LORDS_27 as NAK_LORDS


def compute():
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    yr = BIRTH["year"]; mo = BIRTH["month"]; dy = BIRTH["day"]
    hr = BIRTH["hour"]; mn = BIRTH["min"]
    tz = BIRTH["tz"]
    ut_hour = hr + mn/60 - tz
    jd = swe.julday(yr, mo, dy, ut_hour)

    PLANETS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
               "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,
               "Rahu":swe.MEAN_NODE}

    positions = {}
    for name, pid in PLANETS.items():
        pos = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED)
        lon = pos[0][0]
        speed = pos[0][3]
        rasi_idx = int(lon // 30)
        deg_in_sign = lon - rasi_idx * 30
        nak_idx = int(lon // (360/27))
        pada = int((lon % (360/27)) // (360/108)) + 1
        positions[name] = {
            "rasi": RASIS[rasi_idx], "rasi_idx": rasi_idx,
            "deg": round(deg_in_sign, 4), "lon_abs": round(lon, 4),
            "nak": NAKSHATRAS[nak_idx], "nak_idx": nak_idx,
            "nak_lord": NAK_LORDS[nak_idx], "pada": pada,
            "retrograde": speed < 0, "speed": round(speed, 4),
        }
    # Ketu
    rahu_lon = positions["Rahu"]["lon_abs"]
    ketu_lon = (rahu_lon + 180) % 360
    krasi = int(ketu_lon // 30)
    knak = int(ketu_lon // (360/27))
    kpada = int((ketu_lon % (360/27)) // (360/108)) + 1
    positions["Ketu"] = {
        "rasi": RASIS[krasi], "rasi_idx": krasi,
        "deg": round(ketu_lon - krasi*30, 4), "lon_abs": round(ketu_lon, 4),
        "nak": NAKSHATRAS[knak], "nak_idx": knak,
        "nak_lord": NAK_LORDS[knak], "pada": kpada,
        "retrograde": True, "speed": -0.053,
    }

    # Compute Lagna
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    asc_data = swe.houses_ex(jd, BIRTH["lat"], BIRTH["lon"], b'P', swe.FLG_SIDEREAL)
    asc_lon = asc_data[0][0]
    lagna_rasi_idx = int(asc_lon // 30)
    lagna_rasi = RASIS[lagna_rasi_idx]
    lagna_deg = asc_lon - lagna_rasi_idx*30

    # Houses (whole-sign system per Vedic tradition)
    for p, pd in positions.items():
        # House from lagna
        house = (pd["rasi_idx"] - lagna_rasi_idx) % 12 + 1
        positions[p]["house"] = house

    moon = positions["Moon"]
    janma_nak = moon["nak"]
    janma_nak_lord = moon["nak_lord"]

    chart = {
        "name": NAME,
        "birth": BIRTH,
        "lagna": lagna_rasi,
        "lagna_idx": lagna_rasi_idx,
        "lagna_deg": round(lagna_deg, 4),
        "lagna_lord": {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
                        "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
                        "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn",
                        "Pisces":"Jupiter"}[lagna_rasi],
        "ayanamsa": round(swe.get_ayanamsa(jd), 6),
        "positions": positions,
        "janma_nakshatra": janma_nak,
        "janma_nakshatra_lord": janma_nak_lord,
        "moon_rasi": moon["rasi"],
        "_generated": dt.datetime.now().isoformat(),
    }
    return chart


def display_chart(chart):
    print(f"\n{'='*70}")
    print(f"  CHART: {chart['name']}")
    print(f"{'='*70}")
    b = chart["birth"]
    print(f"  Birth: {b['day']:02d}-{b['month']:02d}-{b['year']} {b['hour']:02d}:{b['min']:02d} IST ({b['weekday']})")
    print(f"  Place: {b['place']} ({b['lat']:.4f} N, {b['lon']:.4f} E)")
    print(f"  Ayanamsa: {chart['ayanamsa']:.4f}° (Lahiri)")
    print()
    print(f"  LAGNA: {chart['lagna']} {chart['lagna_deg']:.2f}° (lord: {chart['lagna_lord']})")
    print(f"  MOON RASI: {chart['moon_rasi']}")
    print(f"  JANMA NAKSHATRA: {chart['janma_nakshatra']} (lord: {chart['janma_nakshatra_lord']})")
    print()
    print(f"  {'PLANET':<8} {'RASI':<14} {'H':>3}  {'DEG':>7}  {'NAKSHATRA':<18} pada  retro")
    print(f"  {'-'*70}")
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        pd = chart["positions"][p]
        retro = " R" if pd.get("retrograde") else "  "
        print(f"  {p:<8} {pd['rasi']:<14} {pd['house']:>3}  {pd['deg']:>6.2f}°  {pd['nak']:<18}  {pd['pada']}{retro}")


def main():
    chart = compute()
    out_path = ATRO / "sree_chart.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(chart, f, indent=2, default=str)
    display_chart(chart)
    print(f"\n  Saved: {out_path}")


if __name__ == "__main__":
    main()
