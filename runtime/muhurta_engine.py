"""Muhurta Engine — Auspicious timing for events.

Source: Muhurta Chintamani by Ramacharya, Phaladeepika Ch. 26.
Computes:
  - Tara Bala for any date relative to natal nakshatra
  - Chandra Bala for any date relative to natal Moon
  - Auspicious / inauspicious yogas of the day
  - Best muhurta windows for marriage / travel / business / surgery
"""
import sys, datetime as dt
sys.path.insert(0, ".")
from vedic_core import RASIS

from panchanga import compute_panchanga, NAKSHATRAS

# Tara classification (1-9): 1=Janma (mixed), 2=Sampat (good), 3=Vipat (bad),
# 4=Kshema (good), 5=Pratyari (mixed), 6=Sadhaka (good), 7=Vadha (bad),
# 8=Mitra (good), 9=Atimitra (excellent)
TARA_TYPES = {1:"Janma (mixed)", 2:"Sampat (good)", 3:"Vipat (bad)", 4:"Kshema (good)",
              5:"Pratyari (mixed)", 6:"Sadhaka (good)", 7:"Vadha (bad)",
              8:"Mitra (good)", 9:"Atimitra (excellent)"}
TARA_GOOD = [2, 4, 6, 8, 9]


def tara_bala(natal_nakshatra, date_dt):
    """Compute Tara on given date relative to native's natal nakshatra."""
    if natal_nakshatra not in NAKSHATRAS: return None
    pan = compute_panchanga(date_dt)
    today_nak = pan["nakshatra"]
    if today_nak not in NAKSHATRAS: return None
    natal_idx = NAKSHATRAS.index(natal_nakshatra)
    today_idx = NAKSHATRAS.index(today_nak)
    tara_num = ((today_idx - natal_idx) % 27) + 1
    cycle_pos = ((tara_num - 1) % 9) + 1
    return {
        "tara_number_27": tara_num,
        "tara_cycle_1to9": cycle_pos,
        "type": TARA_TYPES[cycle_pos],
        "is_good": cycle_pos in TARA_GOOD,
    }


def chandra_bala(natal_moon_rasi, date_dt):
    """Compute Chandra Bala (Moon strength from natal Moon)."""
    
    pan = compute_panchanga(date_dt)
    today_nak = pan["nakshatra"]
    if today_nak not in NAKSHATRAS: return None
    nak_idx = NAKSHATRAS.index(today_nak)
    today_moon_sign_idx = (nak_idx * 30 // 27) % 12
    natal_moon_idx = RASIS.index(natal_moon_rasi) if natal_moon_rasi in RASIS else 0
    pos_from_natal = ((today_moon_sign_idx - natal_moon_idx) % 12) + 1

    GOOD_POSITIONS = [1, 3, 6, 7, 10, 11]
    BAD_POSITIONS = [4, 8, 12]
    is_good = pos_from_natal in GOOD_POSITIONS
    is_bad = pos_from_natal in BAD_POSITIONS
    return {
        "moon_position_from_natal": pos_from_natal,
        "is_good": is_good,
        "is_bad": is_bad,
        "verdict": "Strong" if is_good else "Weak" if is_bad else "Neutral",
    }


def muhurta_check(natal_chart, event_dt, event_type="generic"):
    """Comprehensive muhurta check for a given date and event type."""
    natal_nak = natal_chart.get("janma_nakshatra")
    natal_moon = natal_chart.get("moon_rasi")

    pan = compute_panchanga(event_dt)
    tara = tara_bala(natal_nak, event_dt) if natal_nak else None
    cb = chandra_bala(natal_moon, event_dt) if natal_moon else None

    # General red flags
    red_flags = []
    if pan["is_bhadra"]: red_flags.append("Bhadra Karana active — avoid auspicious work")
    if pan["is_amavasya"]: red_flags.append("Amavasya — avoid celebrations")
    if tara and not tara["is_good"]: red_flags.append(f"Tara: {tara['type']} — not favorable")
    if cb and cb["is_bad"]: red_flags.append(f"Chandra Bala: {cb['verdict']}")

    # Event-specific
    event_advice = []
    if event_type == "marriage":
        if pan["vara"] in ["Tuesday", "Saturday"]: red_flags.append("Tuesday/Saturday not ideal for marriage")
        if pan["tithi_number"] in [4, 9, 14, 30]: red_flags.append(f"Rikta tithi {pan['tithi']} not ideal")
        if pan["paksha"] == "Krishna" and pan["tithi_number"] > 24: red_flags.append("Late Krishna paksha not ideal for marriage")
    elif event_type == "travel":
        if pan["vara"] in ["Tuesday", "Saturday"]: red_flags.append("Avoid distant travel on Tuesday/Saturday")
    elif event_type == "business":
        if pan["vara"] not in ["Wednesday", "Thursday"]: event_advice.append("Wednesday/Thursday preferred for business start")
    elif event_type == "surgery":
        if pan["paksha"] == "Shukla": red_flags.append("Shukla paksha — surgery less ideal (waxing Moon = swelling)")

    is_auspicious = len(red_flags) == 0

    return {
        "date": event_dt.strftime("%Y-%m-%d %H:%M"),
        "event_type": event_type,
        "panchanga": pan,
        "tara": tara,
        "chandra_bala": cb,
        "red_flags": red_flags,
        "event_advice": event_advice,
        "is_auspicious": is_auspicious,
        "verdict": "AUSPICIOUS" if is_auspicious else "NOT AUSPICIOUS — see flags",
    }


def find_auspicious_dates(natal_chart, year, month, event_type="generic", days=30):
    """Find auspicious dates within a given month."""
    out = []
    start = dt.datetime(year, month, 1)
    for i in range(days):
        d = start + dt.timedelta(days=i)
        if d.month != month: break
        result = muhurta_check(natal_chart, d.replace(hour=10), event_type)
        if result["is_auspicious"]:
            out.append({
                "date": d.strftime("%Y-%m-%d (%a)"),
                "tithi": result["panchanga"]["tithi"],
                "nakshatra": result["panchanga"]["nakshatra"],
            })
    return out


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    today = dt.datetime.now()
    print(f"=== MUHURTA CHECK for today ({today.date()}) ===")
    result = muhurta_check(chart, today, "generic")
    print(f"  Verdict: {result['verdict']}")
    print(f"  Panchanga: tithi={result['panchanga']['tithi']}, nak={result['panchanga']['nakshatra']}, vara={result['panchanga']['vara']}")
    if result["tara"]:
        print(f"  Tara: {result['tara']['type']}")
    if result["chandra_bala"]:
        print(f"  Chandra Bala: {result['chandra_bala']['verdict']}")
    if result["red_flags"]:
        print("  Red flags:")
        for f in result["red_flags"]:
            print(f"    - {f}")
    print(f"\n=== AUSPICIOUS DATES IN {today.year}-{today.month:02d} for marriage ===")
    auspicious = find_auspicious_dates(chart, today.year, today.month, "marriage")
    for a in auspicious[:5]:
        print(f"  {a['date']} - {a['tithi']}, {a['nakshatra']}")
