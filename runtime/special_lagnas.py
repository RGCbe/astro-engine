"""Special Lagnas — Hora, Ghatika, Bhava, Indu, Pranapada, Sripati.

Source: BPHS Ch. 4-5, Phaladeepika, Jaimini Sutras.
These special ascendants are used alongside the standard birth Lagna for deeper readings.
"""
import sys
sys.path.insert(0, ".")

from vedic_core import RASIS, RASI_LORDS  # canonical 12 signs + lords

# Indu lagna kalas — fixed values per house lord (BPHS Ch. 4)
INDU_KALAS = {"Sun":30,"Moon":16,"Mars":6,"Mercury":8,"Jupiter":10,"Venus":12,"Saturn":1}


def hora_lagna(chart):
    """Hora Lagna — minute-based ascendant. Each Hora = 1 hour ~ 0.5 sign movement.
    HL = Birth Lagna + (Hours from sunrise × 30°/2hours).
    Approximation: HL = Lagna + (1 sign per hour after sunrise).
    """
    b = chart["birth"]
    sunrise_hour = 6  # approximation — proper sunrise needs lat/lon ephemeris
    hours_from_sunrise = (b["hour"] + b["min"]/60) - sunrise_hour
    if hours_from_sunrise < 0: hours_from_sunrise += 24

    natal_lagna_idx = chart["lagna_idx"]
    # HL moves 1 sign per hour
    hl_idx = (natal_lagna_idx + int(hours_from_sunrise)) % 12
    return {
        "name": "Hora Lagna",
        "purpose": "wealth, financial life, daily livelihood",
        "rasi": RASIS[hl_idx],
        "rasi_idx": hl_idx,
        "lord": RASI_LORDS[RASIS[hl_idx]],
    }


def ghatika_lagna(chart):
    """Ghatika Lagna — 1 sign per Ghatika (24 minutes).
    GL = Birth Lagna + (number of ghatikas elapsed × 1 sign).
    """
    b = chart["birth"]
    sunrise_hour = 6
    minutes_from_sunrise = ((b["hour"] - sunrise_hour) * 60 + b["min"])
    if minutes_from_sunrise < 0: minutes_from_sunrise += 24*60
    ghatikas = minutes_from_sunrise / 24  # 1 ghatika = 24 min
    natal_lagna_idx = chart["lagna_idx"]
    gl_idx = (natal_lagna_idx + int(ghatikas)) % 12
    return {
        "name": "Ghatika Lagna",
        "purpose": "status, government recognition, authority",
        "rasi": RASIS[gl_idx],
        "rasi_idx": gl_idx,
        "lord": RASI_LORDS[RASIS[gl_idx]],
    }


def bhava_lagna(chart):
    """Bhava Lagna — 1 sign per 5 ghatikas (2 hours).
    BL = Birth Lagna + (hours after sunrise × 0.5 sign).
    """
    b = chart["birth"]
    sunrise_hour = 6
    hours_from_sunrise = (b["hour"] + b["min"]/60) - sunrise_hour
    if hours_from_sunrise < 0: hours_from_sunrise += 24
    natal_lagna_idx = chart["lagna_idx"]
    bl_idx = (natal_lagna_idx + int(hours_from_sunrise / 2)) % 12
    return {
        "name": "Bhava Lagna",
        "purpose": "general happiness, basic life themes",
        "rasi": RASIS[bl_idx],
        "rasi_idx": bl_idx,
        "lord": RASI_LORDS[RASIS[bl_idx]],
    }


def indu_lagna(chart):
    """Indu Lagna — wealth lagna.
    Calculation: kala of 9th lord + kala of 9th from Moon's sign lord, divided by 12.
    Result added (in signs) from Moon's sign.
    """
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    moon_rasi_idx = pos["Moon"]["rasi_idx"]

    h9_from_lagna_sign = RASIS[(lagna_idx + 8) % 12]
    h9_from_moon_sign = RASIS[(moon_rasi_idx + 8) % 12]
    lord1 = RASI_LORDS[h9_from_lagna_sign]
    lord2 = RASI_LORDS[h9_from_moon_sign]
    kala_sum = INDU_KALAS.get(lord1, 0) + INDU_KALAS.get(lord2, 0)
    signs_to_advance = kala_sum % 12

    indu_idx = (moon_rasi_idx + signs_to_advance) % 12
    return {
        "name": "Indu Lagna",
        "purpose": "wealth specifically (Lakshmi's seat)",
        "rasi": RASIS[indu_idx],
        "rasi_idx": indu_idx,
        "lord": RASI_LORDS[RASIS[indu_idx]],
        "kala_sum": kala_sum,
    }


def pranapada_lagna(chart):
    """Pranapada Lagna — minute-based subtle ascendant.
    Pranapada = (minutes since midnight × 1°) added to natal Sun longitude.
    """
    pos = chart["positions"]
    if "Sun" not in pos: return None
    b = chart["birth"]
    minutes_since_midnight = b["hour"] * 60 + b["min"]
    sun_lon = pos["Sun"].get("lon_abs") or (pos["Sun"]["rasi_idx"] * 30 + pos["Sun"]["deg"])
    # Pranapada = Sun + (minutes / 360) × 360 wrapped = Sun + minutes × 1° (simplified)
    pranapada_lon = (sun_lon + (minutes_since_midnight % 360)) % 360
    pp_idx = int(pranapada_lon / 30)
    return {
        "name": "Pranapada Lagna",
        "purpose": "vitality, life-force, daily energy peaks",
        "rasi": RASIS[pp_idx],
        "rasi_idx": pp_idx,
        "lord": RASI_LORDS[RASIS[pp_idx]],
        "lon": round(pranapada_lon, 2),
    }


def chandra_lagna(chart):
    """Chandra Lagna — read chart from Moon's sign as ascendant."""
    pos = chart["positions"]
    if "Moon" not in pos: return None
    moon_idx = pos["Moon"]["rasi_idx"]
    return {
        "name": "Chandra Lagna",
        "purpose": "emotional life, public role (read chart from Moon)",
        "rasi": RASIS[moon_idx],
        "rasi_idx": moon_idx,
        "lord": RASI_LORDS[RASIS[moon_idx]],
    }


def surya_lagna(chart):
    """Surya Lagna — read chart from Sun's sign as ascendant."""
    pos = chart["positions"]
    if "Sun" not in pos: return None
    sun_idx = pos["Sun"]["rasi_idx"]
    return {
        "name": "Surya Lagna",
        "purpose": "career, authority, ego (read chart from Sun)",
        "rasi": RASIS[sun_idx],
        "rasi_idx": sun_idx,
        "lord": RASI_LORDS[RASIS[sun_idx]],
    }


def all_special_lagnas(chart):
    return {
        "natal_lagna": {"name":"Janma Lagna","purpose":"body, general life","rasi":chart["lagna"],"lord":chart.get("lagna_lord")},
        "hora_lagna": hora_lagna(chart),
        "ghatika_lagna": ghatika_lagna(chart),
        "bhava_lagna": bhava_lagna(chart),
        "indu_lagna": indu_lagna(chart),
        "pranapada_lagna": pranapada_lagna(chart),
        "chandra_lagna": chandra_lagna(chart),
        "surya_lagna": surya_lagna(chart),
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    sl = all_special_lagnas(chart)
    print(f"=== SPECIAL LAGNAS for {chart['name']} ===\n")
    for key, data in sl.items():
        if data:
            print(f"  {data['name']:20s} {data['rasi']:14s} (lord: {data.get('lord','?')})")
            print(f"    Purpose: {data['purpose']}")
            print()
