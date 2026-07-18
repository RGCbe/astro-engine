"""KP (Krishnamurti Paddhati) — Sub-lord theory.

Source: KP Reader Volumes 2, 3, 6 by K.S. Krishnamurti.
The most precise event-timing system in Vedic astrology.

KP Methodology:
  1. Each Nakshatra (13°20') is divided into 9 sub-divisions per Vimshottari proportions
  2. Each sub-division is ruled by a planet (the "sub-lord")
  3. Each sub is further divided into "sub-sub" levels (3-4 deep)
  4. The cuspal sub-lord predicts the events of that house
  5. Significators of houses determine when events occur via dasha

KP Cuspal Sub-Lord (CSL) Rules:
  - 7th cusp sub-lord = marriage timing
  - 10th cusp sub-lord = career events
  - 11th cusp sub-lord = gains/wishes fulfilled
  - 6th cusp sub-lord = enemies/disputes
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya",
              "Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
              "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
              "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
NAK_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
VIMS_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
VIMS_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]

NAK_SIZE = 360 / 27.0  # 13.333°


def get_sub_lord(longitude_deg):
    """Get KP sub-lord for any longitude.
    Each nakshatra is divided into 9 sub-divisions in Vimshottari proportions.
    """
    # Position within nakshatra
    nak_idx = int(longitude_deg / NAK_SIZE)
    pos_in_nak = longitude_deg - nak_idx * NAK_SIZE
    nak_lord = NAK_LORDS[nak_idx % 9]
    nak_name = NAKSHATRAS[nak_idx]

    # Sub-divisions: each sub size = (lord's vims years / 120) * NAK_SIZE
    sub_lord_idx = VIMS_ORDER.index(nak_lord)
    cumulative = 0
    sub_lord = nak_lord
    sub_index = 0
    for k in range(9):
        cur_lord = VIMS_ORDER[(sub_lord_idx + k) % 9]
        sub_size = NAK_SIZE * VIMS_YEARS[cur_lord] / 120.0
        if cumulative + sub_size >= pos_in_nak:
            sub_lord = cur_lord
            sub_index = k
            break
        cumulative += sub_size

    return {
        "nak": nak_name,
        "nak_lord": nak_lord,
        "sub_lord": sub_lord,
        "sub_index": sub_index,
    }


def get_sub_sub_lord(longitude_deg):
    """Get KP sub-sub-lord — finer granularity for event prediction."""
    nak_idx = int(longitude_deg / NAK_SIZE)
    pos_in_nak = longitude_deg - nak_idx * NAK_SIZE
    nak_lord = NAK_LORDS[nak_idx % 9]

    # Find sub-lord first
    sub_lord_idx = VIMS_ORDER.index(nak_lord)
    cumulative = 0
    sub_lord = nak_lord
    sub_start = 0
    for k in range(9):
        cur_lord = VIMS_ORDER[(sub_lord_idx + k) % 9]
        sub_size = NAK_SIZE * VIMS_YEARS[cur_lord] / 120.0
        if cumulative + sub_size >= pos_in_nak:
            sub_lord = cur_lord
            sub_start = cumulative
            break
        cumulative += sub_size

    # Position within sub
    pos_in_sub = pos_in_nak - sub_start
    sub_size = NAK_SIZE * VIMS_YEARS[sub_lord] / 120.0
    sub_lord_idx2 = VIMS_ORDER.index(sub_lord)
    cumulative2 = 0
    sub_sub_lord = sub_lord
    for k in range(9):
        cur_lord2 = VIMS_ORDER[(sub_lord_idx2 + k) % 9]
        ss_size = sub_size * VIMS_YEARS[cur_lord2] / 120.0
        if cumulative2 + ss_size >= pos_in_sub:
            sub_sub_lord = cur_lord2
            break
        cumulative2 += ss_size

    return {
        "sub_lord": sub_lord,
        "sub_sub_lord": sub_sub_lord,
    }


import swisseph as swe

def cuspal_sub_lord(natal_chart, house_number):
    """Get the precise sub-lord of a house's cusp using Placidus house calculations.
    
    If birth data is available in the chart, it computes precise Placidus cusps
    using Swiss Ephemeris. Otherwise, it falls back to the sign-start approximation.
    """
    if "birth" in natal_chart and isinstance(natal_chart["birth"], dict):
        b = natal_chart["birth"]
        hrs = b.get("hour", 12)
        mins = b.get("min", 0)
        decimal_hour = hrs + mins / 60.0
        jd = swe.julday(b["year"], b["month"], b["day"], decimal_hour - 5.5)  # IST to UT
        
        # Placidus house cusps (cusps[1] = 1st house cusp, etc.)
        cusps, ascmc = swe.houses_ex(jd, b["lat"], b["lon"], b"P")
        ayan = swe.get_ayanamsa_ut(jd)
        
        # Sidereal longitude of the house cusp
        cusp_lon = (cusps[house_number] - ayan) % 360
        return get_sub_lord(cusp_lon)
    else:
        # Fallback to sign-start approximation if birth data is missing
        lagna_idx = natal_chart.get("lagna_idx", 5)
        house_sign_idx = (lagna_idx + house_number - 1) % 12
        cusp_lon = house_sign_idx * 30 + 0.0
        return get_sub_lord(cusp_lon)



def kp_event_significators(natal_chart, target_house):
    """Find KP significators (planets that signify a house).

    A planet signifies a house if:
      A. It is in that house
      B. Its star-lord is in that house OR signifies it
      C. It rules that house (lord of)
    """
    pos = natal_chart["positions"]
    lagna_idx = natal_chart["lagna_idx"]
    target_sign_idx = (lagna_idx + target_house - 1) % 12

    significators = []
    for p, pd in pos.items():
        signifies = False
        # A: planet in target house
        if pd["house"] == target_house:
            signifies = True
        # C: planet rules the sign (= lord of house)
        if pd.get("rasi_idx") == target_sign_idx:
            pass  # already counted
        # Check rules-house (more general)
        from divisional_charts import RASI_LORDS, RASIS
        target_lord = RASI_LORDS[RASIS[target_sign_idx]]
        if p == target_lord:
            signifies = True

        # B: star-lord (nakshatra-lord) in target house
        nak_lord = pd.get("nak_lord")
        if nak_lord and nak_lord in pos and pos[nak_lord]["house"] == target_house:
            signifies = True

        if signifies:
            significators.append(p)
    return significators


def kp_summary(natal_chart):
    """KP-style summary for marriage/career/gains predictions."""
    out = {}
    for h, label in [(7, "marriage"), (10, "career"), (11, "gains/wishes"),
                     (5, "children"), (4, "home/comforts"), (2, "wealth"),
                     (6, "service/disputes"), (9, "fortune/dharma")]:
        csl = cuspal_sub_lord(natal_chart, h)
        sigs = kp_event_significators(natal_chart, h)
        out[f"H{h}_{label}"] = {
            "cuspal_sub_lord": csl["sub_lord"],
            "csl_nakshatra": csl["nak"],
            "significators": sigs,
        }
    return out


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print(f"=== KP CUSPAL SUB-LORD ANALYSIS for {chart['name']} ===\n")

    summary = kp_summary(chart)
    for key, data in summary.items():
        print(f"  {key:30s}")
        print(f"    Cuspal Sub-Lord: {data['cuspal_sub_lord']:10s} (nakshatra: {data['csl_nakshatra']})")
        print(f"    Significators:   {', '.join(data['significators']) if data['significators'] else 'none'}")
        print()
