"""
Divisional Vimshottari Dasha — D9 (Navamsa) + D10 (Dashamsa) timelines.

BPHS Ch.80 explicitly says: use D9 Vimshottari to time MARRIAGE.
BPHS Ch.25-30 says: use D10 Vimshottari to time CAREER events.

This module computes Vimshottari dasha based on Moon's nakshatra in the
divisional chart (instead of D1), giving a separate dasha timeline that
matches the divisional life-area more precisely.

Usage:
    d9_tl = build_d9_dasha_timeline(chart)
    d9_active = lookup_d9_dasha(d9_tl, datetime(1995, 5, 24))
    # returns the active D9 MD/AD/PD at that date

    d10_tl = build_d10_dasha_timeline(chart)
"""
import sys, json, datetime as dt
sys.path.insert(0, ".")
from pathlib import Path

from granular_dasha import build_full_timeline, lookup, VIMSHOTTARI_YEARS, NAK_LORDS_27
from divisional_charts import build_divisional_chart


def _moon_lon_from_divisional(d_chart):
    """Get Moon's longitude in divisional chart (degrees 0-360).
    Divisional chart positions are sign-based, so we use sign mid-point as approximation.
    For more precise divisional Moon longitude, we'd need a proper division-degree calc.
    """
    moon = d_chart["positions"].get("Moon")
    if not moon: return None
    # Get rasi_idx + deg in division
    rasi_idx = moon.get("rasi_idx", 0)
    deg_in_sign = moon.get("deg", 15.0)
    return rasi_idx * 30 + deg_in_sign


def _build_dasha_from_moon_lon(moon_lon, birth_dt):
    """Build Vimshottari timeline from a Moon longitude + birth datetime.
    Mirrors granular_dasha.build_full_timeline logic but takes Moon longitude directly.
    """
    # Compute nakshatra remainder
    nak_idx = int(moon_lon // (360 / 27))
    nak_progress = (moon_lon - nak_idx * (360 / 27)) / (360 / 27)  # 0..1 within nakshatra
    nak_lord = NAK_LORDS_27[nak_idx]
    md_full = VIMSHOTTARI_YEARS[nak_lord]
    elapsed_in_md_years = md_full * nak_progress

    # Build a fake chart with this Moon longitude
    fake_chart = {
        "positions": {"Moon": {"lon": moon_lon, "lon_abs": moon_lon}},
        "birth": {
            "year": birth_dt.year, "month": birth_dt.month, "day": birth_dt.day,
            "hour": birth_dt.hour, "min": birth_dt.minute,
        },
    }
    return build_full_timeline(fake_chart, levels=3)


def build_d9_dasha_timeline(chart, levels=3):
    """Compute Vimshottari dasha based on D9 (Navamsa) Moon position.
    Returns same format as granular_dasha.build_full_timeline.
    """
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    d9 = build_divisional_chart(chart, varga="D9")
    d9_moon_lon = _moon_lon_from_divisional(d9)
    if d9_moon_lon is None:
        return []
    return _build_dasha_from_moon_lon(d9_moon_lon, birth_dt)


def build_d10_dasha_timeline(chart, levels=3):
    """Compute Vimshottari dasha based on D10 (Dashamsa) Moon position."""
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    d10 = build_divisional_chart(chart, varga="D10")
    d10_moon_lon = _moon_lon_from_divisional(d10)
    if d10_moon_lon is None:
        return []
    return _build_dasha_from_moon_lon(d10_moon_lon, birth_dt)


def lookup_d9_dasha(d9_timeline, when_dt):
    """Look up active D9 MD/AD/PD at a date."""
    return lookup(d9_timeline, when_dt)


def lookup_d10_dasha(d10_timeline, when_dt):
    """Look up active D10 MD/AD/PD at a date."""
    return lookup(d10_timeline, when_dt)


def get_d9_lords_for_marriage(chart):
    """Return the planets that "activate marriage" in D9:
    D9 lagna lord, D9 7th lord, D9 Venus lord, D9 Moon lord."""
    d9 = build_divisional_chart(chart, varga="D9")
    lagna_idx = d9["lagna_idx"]
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    LORDS = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
             "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
             "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
    activators = set()
    activators.add(LORDS[SIGNS[lagna_idx]])      # D9 lagna lord
    activators.add(LORDS[SIGNS[(lagna_idx + 6) % 12]])  # D9 7H lord
    activators.add("Venus")  # always Venus
    return activators


def get_d10_lords_for_career(chart):
    """Return planets that activate career events in D10:
    D10 lagna lord, D10 10th lord, Sun (career karaka), Saturn (work karaka)."""
    d10 = build_divisional_chart(chart, varga="D10")
    lagna_idx = d10["lagna_idx"]
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
             "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    LORDS = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
             "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
             "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
    activators = set()
    activators.add(LORDS[SIGNS[lagna_idx]])      # D10 lagna lord
    activators.add(LORDS[SIGNS[(lagna_idx + 9) % 12]])  # D10 10H lord
    activators.add("Sun")
    activators.add("Saturn")
    return activators


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open(Path("../charts/sachin_tendulkar_chart.json")))
    print(f"=== {chart['name']} — Divisional Dasha Test ===")
    # Sachin marriage 1995-05-24
    when = dt.datetime(1995, 5, 24)
    d9_tl = build_d9_dasha_timeline(chart)
    d9_ds = lookup_d9_dasha(d9_tl, when)
    print(f"\nMarriage 1995-05-24:")
    print(f"  D1 dasha: see existing")
    print(f"  D9 dasha:")
    for lvl in (1, 2, 3):
        rec = d9_ds.get(lvl, {})
        n = ["", "MD", "AD", "PD"][lvl]
        if rec:
            lord_key = ["", "md", "ad", "pd"][lvl]
            print(f"    {n}: {rec.get(lord_key, '?')}  ({rec['start'].strftime('%Y-%m-%d')} → {rec['end'].strftime('%Y-%m-%d')})")
    d9_activators = get_d9_lords_for_marriage(chart)
    print(f"\n  D9 marriage activators: {d9_activators}")
    d9_md = d9_ds.get(1, {}).get("md")
    d9_ad = d9_ds.get(2, {}).get("ad")
    print(f"  Active D9 MD={d9_md}, AD={d9_ad}")
    if d9_md in d9_activators or d9_ad in d9_activators:
        print(f"  ✓ D9 dasha CONFIRMS marriage timing")
    else:
        print(f"  ✗ D9 dasha does NOT confirm")

    # Career test — Sachin first century 1990-08-14
    when_c = dt.datetime(1990, 8, 14)
    d10_tl = build_d10_dasha_timeline(chart)
    d10_ds = lookup_d10_dasha(d10_tl, when_c)
    print(f"\nFirst Test century 1990-08-14:")
    d10_md = d10_ds.get(1, {}).get("md")
    d10_ad = d10_ds.get(2, {}).get("ad")
    print(f"  D10 dasha: MD={d10_md}, AD={d10_ad}")
    d10_activators = get_d10_lords_for_career(chart)
    print(f"  D10 career activators: {d10_activators}")
    if d10_md in d10_activators or d10_ad in d10_activators:
        print(f"  ✓ D10 dasha CONFIRMS career timing")
    else:
        print(f"  ✗ D10 dasha does NOT confirm")
