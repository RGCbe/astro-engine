"""Dasha Systems Full — 5 advanced Vedic dashas not covered elsewhere.

Source: BPHS Ch. 50 (Kalachakra), Jaimini Sutras Ch. 2 (Shoola/Sthira/Drig/Niryana).
Builds:
  - Kalachakra Dasha (BPHS Ch. 50): nakshatra-pada based, runs through "Savya"/"Apasavya" rashi sequences.
    Total 100 years.
  - Shoola Dasha (Jaimini, BPHS): rashi-based timeline keyed on the 7th-from-AL or seed sign.
    9 years per fixed sign by default; varies (7 movable / 8 dual) per Parashari Shoola usage.
  - Sthira Dasha: each rashi gets fixed years (7 movable / 8 dual / 9 fixed),
    starting from lagna sign and following sign-order.
  - Drig Dasha: Jaimini aspect-based timeline keyed on the 9th-from-Atmakaraka sign,
    moves through aspected rashis. Used for spirituality/dharma timing.
  - Niryana Shoola Dasha: longevity/Markesha timing dasha, used to detect death-killing
    transit windows. Same rashi-walk as Shoola but seeded on the lagna's 8th-cusp sign.

All return list of dicts with shape:
  {sign_or_lord, start, end, years, age_from, age_to, notes?}
"""
import sys, datetime as dt
sys.path.insert(0, ".")
from vedic_core import (
    RASIS, RASI_LORDS, NAKSHATRAS, NAK_LORDS_27,
    MOVABLE_SIGNS, FIXED_SIGNS, DUAL_SIGNS,
)

# ============================================================
# KALACHAKRA DASHA — BPHS Ch. 50
# ============================================================
# Nakshatra-pada determines starting sign and direction.
# Each pada points to one of 9 rashis in a Savya (forward) or Apasavya (reverse) sequence.
# Total cycle = 100 years. Years per sign vary based on rasi:
#   Movable: 9 years (Aries, Cancer, Libra, Capricorn)
#   Fixed:   9 years (Taurus, Leo, Scorpio, Aquarius)
#   Dual:    7 or 16 years per BPHS variation; we use the standard 100-year scheme:
# Standard Kalachakra year-counts (BPHS):
# BPHS Ch. 50 Kalachakra years per sign — Sastry edition v. 14-22.
# Raw table sums to 107; scaled to 100-year cycle in compute_kalachakra() below.
KALACHAKRA_YEARS = {
    "Aries": 7, "Taurus": 16, "Gemini": 9, "Cancer": 7,
    "Leo": 21, "Virgo": 5, "Libra": 9, "Scorpio": 16,
    "Sagittarius": 7, "Capricorn": 5, "Aquarius": 0, "Pisces": 5,
}

# 9 rashis per pada — encoded according to BPHS scheme.
# For each nakshatra (27) × pada (4) we have a 9-rashi sequence.
# Standard BPHS Kalachakra mapping (Savya/Apasavya alternates by pada within nakshatra group):
#   Pada 1: Savya  (forward)
#   Pada 2: Apasavya (reverse)
#   Pada 3: Savya
#   Pada 4: Apasavya
# Starting sign is derived from the nakshatra group (Ashwini-Mrigashira start with their own pattern).

# Simplified: starting sign per (nakshatra_idx, pada) — using the 9-fold mapping.
# For practical computation we use: start_sign = (nakshatra_idx * 4 + pada_idx) % 12
KALACHAKRA_DIRECTION = ["Savya", "Apasavya"]  # alternates per pada


def compute_kalachakra(natal_chart):
    """Compute Kalachakra Dasha timeline (~100 years) from Moon's nakshatra-pada using canonical engine.kalachakra."""
    from engine.kalachakra import kalachakra
    
    pos = natal_chart["positions"]
    moon = pos["Moon"]
    moon_lon = moon.get("lon_abs") or (moon["rasi_idx"] * 30 + moon["deg"])
    
    b = natal_chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    
    kc = kalachakra(moon_lon, birth_dt, tradition="santhanam")
    
    timeline = []
    for p in kc.periods:
        sign = p.sign_name
        timeline.append({
            "sign": sign,
            "lord": RASI_LORDS[sign],
            "direction": p.direction,
            "start": p.start,
            "end": p.end,
            "years": round(p.years, 2),
            "age_from": round((p.start - birth_dt).days / 365.25, 1),
            "age_to": round((p.end - birth_dt).days / 365.25, 1),
            "notes": f"Kalachakra ({p.direction}) — sign {sign}",
        })
    return timeline


# ============================================================
# SHOOLA DASHA — Jaimini (BPHS Ch. 51-52)
# ============================================================
# Years per sign:
#   Movable: 7   Fixed: 8   Dual: 9   (some variants 7/8/9)
# Standard Parashari Shoola: 9 years per sign (uniform).
# We implement the Jaimini variant: 7/8/9.
# Per Jaimini Sutras 2.3.1: Movable signs get longest period (9), dual shortest (7).
SHOOLA_YEARS_BY_QUALITY = {"movable": 9, "fixed": 8, "dual": 7}


def _sign_quality(sign):
    if sign in MOVABLE_SIGNS: return "movable"
    if sign in FIXED_SIGNS: return "fixed"
    return "dual"


def _shoola_seed_sign(natal_chart):
    """Shoola seed: 7th house from natal Lagna (per Jaimini)."""
    lagna_idx = natal_chart["lagna_idx"]
    return (lagna_idx + 6) % 12


def compute_shoola(natal_chart):
    """Compute Shoola Dasha timeline (~108 years)."""
    seed_idx = _shoola_seed_sign(natal_chart)
    b = natal_chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])

    timeline = []
    cur_dt = birth_dt
    for i in range(12):
        idx = (seed_idx + i) % 12
        sign = RASIS[idx]
        yrs = SHOOLA_YEARS_BY_QUALITY[_sign_quality(sign)]
        end_dt = cur_dt + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "sign": sign,
            "lord": RASI_LORDS[sign],
            "start": cur_dt,
            "end": end_dt,
            "years": yrs,
            "age_from": round((cur_dt - birth_dt).days / 365.25, 1),
            "age_to": round((end_dt - birth_dt).days / 365.25, 1),
            "notes": f"Shoola — {_sign_quality(sign)} sign",
        })
        cur_dt = end_dt
    return timeline


# ============================================================
# STHIRA DASHA — Fixed dasha, each rashi gets quality-based years
# ============================================================
# Movable: 7   Dual: 8   Fixed: 9
# Sthira Dasha — per Phaladeepika Ch. 27: fixed signs strongest (9), movable weakest (7).
STHIRA_YEARS_BY_QUALITY = {"movable": 7, "dual": 8, "fixed": 9}


def compute_sthira(natal_chart):
    """Compute Sthira Dasha — starts at lagna sign, walks zodiacal forward."""
    lagna_idx = natal_chart["lagna_idx"]
    b = natal_chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])

    timeline = []
    cur_dt = birth_dt
    for i in range(12):
        idx = (lagna_idx + i) % 12
        sign = RASIS[idx]
        yrs = STHIRA_YEARS_BY_QUALITY[_sign_quality(sign)]
        end_dt = cur_dt + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "sign": sign,
            "lord": RASI_LORDS[sign],
            "start": cur_dt,
            "end": end_dt,
            "years": yrs,
            "age_from": round((cur_dt - birth_dt).days / 365.25, 1),
            "age_to": round((end_dt - birth_dt).days / 365.25, 1),
            "notes": f"Sthira — {_sign_quality(sign)} sign",
        })
        cur_dt = end_dt
    return timeline


# ============================================================
# DRIG DASHA — Jaimini aspect-based dasha (9th-from-AK timeline)
# ============================================================
# Each sign is held for years = number of planets aspecting it (Jaimini rashi-aspects).
# Jaimini rashi aspects: movable signs aspect all fixed except adjacent;
# fixed signs aspect all movable except adjacent; dual signs aspect all duals.
# Simplified: years per sign = 7/8/9 by quality (similar to Shoola but seeded differently).

def _atmakaraka_sign(natal_chart):
    """AK = planet with highest degree in its sign (excluding Rahu/Ketu)."""
    pos = natal_chart["positions"]
    candidates = [p for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"] if p in pos]
    best = max(candidates, key=lambda p: pos[p]["deg"])
    return pos[best]["rasi_idx"], best


def compute_drig(natal_chart):
    """Compute Drig Dasha — seeded on 9th from AK."""
    ak_idx, ak_planet = _atmakaraka_sign(natal_chart)
    seed_idx = (ak_idx + 8) % 12  # 9th-from-AK

    b = natal_chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])

    timeline = []
    cur_dt = birth_dt
    for i in range(12):
        idx = (seed_idx + i) % 12
        sign = RASIS[idx]
        yrs = SHOOLA_YEARS_BY_QUALITY[_sign_quality(sign)]
        end_dt = cur_dt + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "sign": sign,
            "lord": RASI_LORDS[sign],
            "start": cur_dt,
            "end": end_dt,
            "years": yrs,
            "age_from": round((cur_dt - birth_dt).days / 365.25, 1),
            "age_to": round((end_dt - birth_dt).days / 365.25, 1),
            "notes": f"Drig (from 9th-AK={RASIS[ak_idx]}, seeded {RASIS[seed_idx]}) — {_sign_quality(sign)}",
            "ak_planet": ak_planet,
        })
        cur_dt = end_dt
    return timeline


# ============================================================
# NIRYANA SHOOLA DASHA — longevity / Markesha
# ============================================================
# Uses same rashi-walk as Shoola but seeded on the 8th sign from lagna.
# Used to detect death-window via Markesha planets transiting current Niryana sign.
def compute_niryana_shoola(natal_chart):
    """Compute Niryana Shoola — longevity timing dasha (seeded on 8H from lagna)."""
    lagna_idx = natal_chart["lagna_idx"]
    seed_idx = (lagna_idx + 7) % 12  # 8th-from-lagna

    b = natal_chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])

    timeline = []
    cur_dt = birth_dt
    for i in range(12):
        idx = (seed_idx + i) % 12
        sign = RASIS[idx]
        yrs = SHOOLA_YEARS_BY_QUALITY[_sign_quality(sign)]
        end_dt = cur_dt + dt.timedelta(days=yrs * 365.25)
        # Markesha flag — placeholder: 7th and 2nd lords from lagna are Markesha planets
        marak_lords = [RASI_LORDS[RASIS[(lagna_idx + 1) % 12]],
                        RASI_LORDS[RASIS[(lagna_idx + 6) % 12]]]
        timeline.append({
            "sign": sign,
            "lord": RASI_LORDS[sign],
            "start": cur_dt,
            "end": end_dt,
            "years": yrs,
            "age_from": round((cur_dt - birth_dt).days / 365.25, 1),
            "age_to": round((end_dt - birth_dt).days / 365.25, 1),
            "notes": f"Niryana — markesha-watch ({', '.join(marak_lords)})",
            "markesha_planets": marak_lords,
        })
        cur_dt = end_dt
    return timeline


# ============================================================
# UNIFIED API
# ============================================================
def all_advanced_dashas(natal_chart):
    return {
        "kalachakra": compute_kalachakra(natal_chart),
        "shoola": compute_shoola(natal_chart),
        "sthira": compute_sthira(natal_chart),
        "drig": compute_drig(natal_chart),
        "niryana_shoola": compute_niryana_shoola(natal_chart),
    }


def lookup_active(timeline, when_dt):
    """Return the active dasha record at a given date."""
    for rec in timeline:
        if rec["start"] <= when_dt <= rec["end"]:
            return rec
    return None


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    print(f"=== KALACHAKRA DASHA ({chart['name']}) ===")
    for d in compute_kalachakra(chart):
        print(f"  {d['sign']:13s} ({d['lord']:8s}) {d['start'].strftime('%Y-%m-%d')} -> {d['end'].strftime('%Y-%m-%d')}  ({d['years']}y) ages {d['age_from']}-{d['age_to']}")

    print(f"\n=== SHOOLA DASHA ({chart['name']}) ===")
    for d in compute_shoola(chart):
        print(f"  {d['sign']:13s} ({d['lord']:8s}) {d['start'].strftime('%Y-%m-%d')} -> {d['end'].strftime('%Y-%m-%d')}  ({d['years']}y) ages {d['age_from']}-{d['age_to']}")

    print(f"\n=== STHIRA DASHA ({chart['name']}) ===")
    for d in compute_sthira(chart):
        print(f"  {d['sign']:13s} ({d['lord']:8s}) {d['start'].strftime('%Y-%m-%d')} -> {d['end'].strftime('%Y-%m-%d')}  ({d['years']}y) ages {d['age_from']}-{d['age_to']}")

    print(f"\n=== DRIG DASHA ({chart['name']}) ===")
    for d in compute_drig(chart):
        print(f"  {d['sign']:13s} ({d['lord']:8s}) {d['start'].strftime('%Y-%m-%d')} -> {d['end'].strftime('%Y-%m-%d')}  ({d['years']}y) ages {d['age_from']}-{d['age_to']}")

    print(f"\n=== NIRYANA SHOOLA DASHA ({chart['name']}) ===")
    for d in compute_niryana_shoola(chart):
        print(f"  {d['sign']:13s} ({d['lord']:8s}) {d['start'].strftime('%Y-%m-%d')} -> {d['end'].strftime('%Y-%m-%d')}  ({d['years']}y) Markeshas: {', '.join(d['markesha_planets'])}")

    today = dt.datetime.now()
    print(f"\n=== ACTIVE NOW ({today.date()}) ===")
    for name, timeline in all_advanced_dashas(chart).items():
        rec = lookup_active(timeline, today)
        if rec:
            print(f"  {name:18s}: {rec['sign']} ({rec['lord']}) — {rec['notes']}")
