"""Divisional Charts (Vargas) — D9, D10, D12, D60.

Classical Vedic divisional charts:
  D1  = Rasi chart (main natal — already in chart JSON)
  D9  = Navamsa — marriage, dharma, hidden strengths, planetary final-strength
  D10 = Dashamsa — career, profession, status, public role
  D12 = Dwadashamsa — parents (father from D12 lagna, mother from 4H of D12)
  D60 = Shashtiamsa — past-life karma, finest karmic detail (Parashara: most important)

Source: BPHS Ch. 6 (Shodashavarga), Phaladeepika Ch. 5.

Each varga is computed by dividing each sign into N equal parts.
The classical formulas are:

D9 (Navamsa): each sign / 9 → 3°20' parts
  Movable signs (Ar/Ca/Li/Cp): start at same sign
  Fixed signs (Ta/Le/Sc/Aq):    start at 9th sign from itself
  Dual signs (Ge/Vi/Sg/Pi):     start at 5th sign from itself

D10 (Dashamsa): each sign / 10 → 3° parts
  Odd signs:  start at same sign
  Even signs: start at 9th from same sign

D12 (Dwadashamsa): each sign / 12 → 2°30' parts
  Each part maps starting from same sign

D60 (Shashtiamsa): each sign / 60 → 0°30' parts (CRITICAL Parashari technique)
  Odd signs:  count forward from Aries
  Even signs: count forward from Libra
"""
import sys
sys.path.insert(0, ".")

from vedic_core import RASIS, RASI_LORDS  # canonical 12 signs + lords
MOVABLE = [0, 3, 6, 9]   # Aries, Cancer, Libra, Capricorn (rasi_idx)
FIXED   = [1, 4, 7, 10]  # Taurus, Leo, Scorpio, Aquarius
DUAL    = [2, 5, 8, 11]  # Gemini, Virgo, Sagittarius, Pisces


def _abs_lon(planet_data):
    """Get absolute longitude (0-360°) from planet data."""
    return planet_data.get("lon_abs") or (planet_data["rasi_idx"] * 30 + planet_data.get("deg", 0))


def _navamsa_index(sign_idx, deg_in_sign):
    """Compute D9 index for a planet at given sign and degrees-in-sign."""
    pada = int(deg_in_sign / (30/9))  # 0-8 within the sign
    if sign_idx in MOVABLE:
        start = sign_idx
    elif sign_idx in FIXED:
        start = (sign_idx + 8) % 12  # 9th sign = +8 (0-indexed)
    else:  # DUAL
        start = (sign_idx + 4) % 12  # 5th sign = +4
    return (start + pada) % 12


def _dashamsa_index(sign_idx, deg_in_sign):
    """Compute D10 index."""
    part = int(deg_in_sign / 3)  # 0-9 within the sign
    if sign_idx % 2 == 0:  # odd sign (1st = Aries = idx 0)
        start = sign_idx
    else:  # even sign
        start = (sign_idx + 8) % 12  # 9th from itself
    return (start + part) % 12


def _dwadashamsa_index(sign_idx, deg_in_sign):
    """Compute D12 index."""
    part = int(deg_in_sign / 2.5)  # 0-11 within the sign
    return (sign_idx + part) % 12


def _shashtiamsa_index(sign_idx, deg_in_sign):
    """Compute D60 index per BPHS Ch 7 (Parashari Shashtiamsa).

    Each sign is divided into 60 parts of 0.5° each. The D60 sign progresses
    sequentially from the natal sign: D60_sign = (natal_sign + part) % 12.

    BUG FIX 2026-05-11: Old code returned `part % 12` for odd signs (ignoring
    sign_idx entirely — every odd sign's D60 always started from Aries) and a
    Libra-offset for even signs. Neither matches the classical formula.
    """
    part = int(deg_in_sign * 2)  # 0-59 within the sign (each part = 0.5°)
    return (sign_idx + part) % 12


def build_divisional_chart(natal_chart, varga="D9"):
    """Build a divisional chart from natal chart.

    Returns a chart dict structurally similar to natal chart, but with positions
    re-computed for the divisional chart.
    """
    natal_pos = natal_chart["positions"]
    natal_lagna_idx = natal_chart["lagna_idx"]

    # Lagna degree within its sign — REQUIRED for correct D9/D10/D12/D60 lagna computation.
    # Most modern charts include "lagna_deg" (0-30°). If missing, fall back to midpoint
    # (this fallback breaks ~90% of D-chart lagnas — newer compute_*.py scripts always set it).
    # BUG FIX 2026-05-11: was unconditionally 15.0, ignoring real lagna_deg even when present.
    lagna_deg_in_sign = natal_chart.get("lagna_deg")
    if lagna_deg_in_sign is None:
        # Try to back-out from lagna_lon if present
        lagna_lon = natal_chart.get("lagna_lon")
        if lagna_lon is not None:
            lagna_deg_in_sign = float(lagna_lon) % 30.0
        else:
            lagna_deg_in_sign = 15.0  # last-resort fallback (degrades D-chart accuracy)

    INDEX_FN = {
        "D9": _navamsa_index,
        "D10": _dashamsa_index,
        "D12": _dwadashamsa_index,
        "D60": _shashtiamsa_index,
    }
    fn = INDEX_FN.get(varga)
    if not fn:
        raise ValueError(f"Unknown varga: {varga}")

    # Compute new lagna in this varga
    new_lagna_idx = fn(natal_lagna_idx, lagna_deg_in_sign)

    # Compute each planet's new sign in this varga
    new_positions = {}
    for p, pd in natal_pos.items():
        sign_idx = pd["rasi_idx"]
        deg_in_sign = pd["deg"]
        new_sign_idx = fn(sign_idx, deg_in_sign)
        # New house = (new_sign_idx - new_lagna_idx) + 1
        new_house = ((new_sign_idx - new_lagna_idx) % 12) + 1
        new_positions[p] = {
            "rasi_idx": new_sign_idx,
            "rasi": RASIS[new_sign_idx],
            "house": new_house,
            "deg": deg_in_sign,  # keep natal deg for reference
            "nak": pd.get("nak"),
            "nak_lord": pd.get("nak_lord"),
            "pada": pd.get("pada"),
            "lon": pd.get("lon"),
        }

    new_chart = {
        "name": f"{natal_chart['name']} — {varga}",
        "birth": natal_chart["birth"],
        "lagna": RASIS[new_lagna_idx],
        "lagna_idx": new_lagna_idx,
        "lagna_lord": RASI_LORDS[RASIS[new_lagna_idx]],
        "positions": new_positions,
        "moon_rasi": new_positions["Moon"]["rasi"],
        "janma_nakshatra": natal_chart.get("janma_nakshatra"),
        "janma_nakshatra_lord": natal_chart.get("janma_nakshatra_lord"),
        "_varga": varga,
        "_natal": natal_chart,
    }
    return new_chart


# ================================================================
# DIVISIONAL CHART INTERPRETATION
# ================================================================

def analyze_d9_marriage(natal_chart):
    """D9 (Navamsa) — marriage, spouse, dharma analysis.

    Key signals from D9:
      - Position of 7th house and 7th lord in D9
      - Position of Venus in D9 (especially for men)
      - Position of Jupiter in D9 (especially for women)
      - Strength of D9 lagna lord
      - Same planet in same sign in D1 and D9 = "Vargottama" (very strong)
    """
    d9 = build_divisional_chart(natal_chart, "D9")
    natal_pos = natal_chart["positions"]
    d9_pos = d9["positions"]

    out = {"varga": "D9 (Navamsa)", "purpose": "Marriage, spouse, dharma, hidden strength"}

    # Vargottama planets (same sign in D1 and D9)
    vargottama = []
    for p in d9_pos:
        if p in natal_pos and natal_pos[p]["rasi_idx"] == d9_pos[p]["rasi_idx"]:
            vargottama.append(p)
    out["vargottama_planets"] = vargottama

    # 7th house in D9
    h7_sign = RASIS[(d9["lagna_idx"] + 6) % 12]
    h7_lord = RASI_LORDS[h7_sign]
    h7_lord_house_in_d9 = d9_pos[h7_lord]["house"] if h7_lord in d9_pos else None
    out["d9_7th_sign"] = h7_sign
    out["d9_7th_lord"] = h7_lord
    out["d9_7th_lord_house"] = h7_lord_house_in_d9

    # Venus in D9
    venus_h_d9 = d9_pos["Venus"]["house"] if "Venus" in d9_pos else None
    venus_sign_d9 = d9_pos["Venus"]["rasi"] if "Venus" in d9_pos else None
    out["venus_d9_house"] = venus_h_d9
    out["venus_d9_sign"] = venus_sign_d9

    # Jupiter in D9
    jup_h_d9 = d9_pos["Jupiter"]["house"] if "Jupiter" in d9_pos else None
    jup_sign_d9 = d9_pos["Jupiter"]["rasi"] if "Jupiter" in d9_pos else None
    out["jupiter_d9_house"] = jup_h_d9
    out["jupiter_d9_sign"] = jup_sign_d9

    # D9 lagna lord placement
    d9_lagna_lord = d9["lagna_lord"]
    d9_lagna_lord_house = d9_pos[d9_lagna_lord]["house"] if d9_lagna_lord in d9_pos else None
    out["d9_lagna"] = d9["lagna"]
    out["d9_lagna_lord"] = d9_lagna_lord
    out["d9_lagna_lord_house"] = d9_lagna_lord_house

    # Marriage assessment narrative
    notes = []
    if vargottama:
        notes.append(f"Vargottama planets ({', '.join(vargottama)}) — these are extra-strong, their themes manifest powerfully in marriage and dharma.")
    if h7_lord_house_in_d9 in [1, 4, 5, 7, 9, 10, 11]:
        notes.append(f"D9 7th lord ({h7_lord}) in good house {h7_lord_house_in_d9} — supportive marriage.")
    elif h7_lord_house_in_d9 in [6, 8, 12]:
        notes.append(f"D9 7th lord ({h7_lord}) in difficult house {h7_lord_house_in_d9} — marriage requires conscious effort.")
    if venus_h_d9 in [1, 4, 5, 7, 11]:
        notes.append(f"Venus in D9 House {venus_h_d9} — favorable for love, comfort in partnership.")
    elif venus_h_d9 in [6, 8, 12]:
        notes.append(f"Venus in D9 House {venus_h_d9} — partner-related challenges, karmic relationship themes.")
    if jup_h_d9 in [1, 5, 9]:
        notes.append(f"Jupiter in D9 House {jup_h_d9} — dharmic blessing on marriage.")
    out["interpretation"] = notes
    return out


def analyze_d10_career(natal_chart):
    """D10 (Dashamsa) — career, profession, status, public role."""
    d10 = build_divisional_chart(natal_chart, "D10")
    d10_pos = d10["positions"]
    natal_pos = natal_chart["positions"]

    out = {"varga": "D10 (Dashamsa)", "purpose": "Career, profession, status, public role"}

    # 10th house in D10
    h10_sign = RASIS[(d10["lagna_idx"] + 9) % 12]
    h10_lord = RASI_LORDS[h10_sign]
    h10_lord_house_d10 = d10_pos[h10_lord]["house"] if h10_lord in d10_pos else None
    out["d10_10th_sign"] = h10_sign
    out["d10_10th_lord"] = h10_lord
    out["d10_10th_lord_house"] = h10_lord_house_d10

    # Sun in D10 (career karaka)
    sun_h_d10 = d10_pos["Sun"]["house"] if "Sun" in d10_pos else None
    sun_sign_d10 = d10_pos["Sun"]["rasi"] if "Sun" in d10_pos else None
    out["sun_d10_house"] = sun_h_d10
    out["sun_d10_sign"] = sun_sign_d10

    # Saturn in D10 (work, persistence)
    sat_h_d10 = d10_pos["Saturn"]["house"] if "Saturn" in d10_pos else None
    out["saturn_d10_house"] = sat_h_d10

    # Vargottama check
    vargottama = []
    for p in d10_pos:
        if p in natal_pos and natal_pos[p]["rasi_idx"] == d10_pos[p]["rasi_idx"]:
            vargottama.append(p)
    out["vargottama_planets"] = vargottama

    # D10 lagna info
    d10_lagna_lord = d10["lagna_lord"]
    d10_lagna_lord_house = d10_pos[d10_lagna_lord]["house"] if d10_lagna_lord in d10_pos else None
    out["d10_lagna"] = d10["lagna"]
    out["d10_lagna_lord"] = d10_lagna_lord
    out["d10_lagna_lord_house"] = d10_lagna_lord_house

    notes = []
    if vargottama:
        notes.append(f"Vargottama in D10 ({', '.join(vargottama)}) — these planets give amplified career results.")
    if h10_lord_house_d10 in [1, 5, 9, 10, 11]:
        notes.append(f"D10 10th lord ({h10_lord}) in {h10_lord_house_d10}H — strong career trajectory.")
    elif h10_lord_house_d10 in [6, 8, 12]:
        notes.append(f"D10 10th lord ({h10_lord}) in {h10_lord_house_d10}H — career has karmic struggles, non-linear path.")
    if sun_h_d10 in [1, 10]:
        notes.append(f"Sun in D10 House {sun_h_d10} — strong authority/leadership signal.")
    if sat_h_d10 in [3, 6, 10, 11]:
        notes.append(f"Saturn in D10 House {sat_h_d10} — discipline-driven career success.")
    elif sat_h_d10 in [1, 4, 5, 7, 8, 12]:
        notes.append(f"Saturn in D10 House {sat_h_d10} — slow career progress, late-bloomer pattern.")
    out["interpretation"] = notes
    return out


def analyze_d60_karma(natal_chart):
    """D60 (Shashtiamsa) — past-life karma, finest karmic detail.
    Parashari rule: D60 outcome can override all other vargas."""
    d60 = build_divisional_chart(natal_chart, "D60")
    d60_pos = d60["positions"]
    natal_pos = natal_chart["positions"]

    out = {"varga": "D60 (Shashtiamsa)", "purpose": "Past-life karma, finest spiritual detail"}

    # D60 lagna and lord
    out["d60_lagna"] = d60["lagna"]
    out["d60_lagna_lord"] = d60["lagna_lord"]
    out["d60_lagna_lord_house"] = d60_pos.get(d60["lagna_lord"], {}).get("house")

    # Vargottama in D60 = highest possible strength
    vargottama = []
    for p in d60_pos:
        if p in natal_pos and natal_pos[p]["rasi_idx"] == d60_pos[p]["rasi_idx"]:
            vargottama.append(p)
    out["vargottama_planets"] = vargottama

    # Benefics vs malefics in D60 lagna and trines (1, 5, 9)
    BENEFICS = ["Moon", "Mercury", "Jupiter", "Venus"]
    MALEFICS = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]
    benefics_in_trines = []
    malefics_in_trines = []
    for p, pd in d60_pos.items():
        if pd["house"] in [1, 5, 9]:
            if p in BENEFICS:
                benefics_in_trines.append(p)
            elif p in MALEFICS:
                malefics_in_trines.append(p)
    out["benefics_in_d60_trines"] = benefics_in_trines
    out["malefics_in_d60_trines"] = malefics_in_trines

    notes = []
    if benefics_in_trines:
        notes.append(f"Benefics in D60 trines ({', '.join(benefics_in_trines)}) — favorable past-life merit; the soul carries karmic blessing into this life.")
    if malefics_in_trines:
        notes.append(f"Malefics in D60 trines ({', '.join(malefics_in_trines)}) — karmic challenges to work through; this incarnation has specific karmic lessons.")
    if vargottama:
        notes.append(f"Vargottama in D60 ({', '.join(vargottama)}) — these planets carry MAXIMUM strength across all vargas; their themes are central to the soul's journey.")

    out["interpretation"] = notes
    return out


def full_varga_analysis(natal_chart, with_citations=True):
    """Run D9, D10, and D60 analysis on a natal chart with optional book citations."""
    result = {
        "D9": analyze_d9_marriage(natal_chart),
        "D10": analyze_d10_career(natal_chart),
        "D60": analyze_d60_karma(natal_chart),
    }
    if with_citations:
        try:
            from book_citation import cite_for_d9, cite_for_d10, cite_for_d60
            result["D9"]["citations"] = cite_for_d9()
            result["D10"]["citations"] = cite_for_d10()
            result["D60"]["citations"] = cite_for_d60()
        except Exception as e:
            print(f"[citation warning] {e}")
    return result


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    print("=" * 70)
    print(f"  DIVISIONAL CHART ANALYSIS — {chart['name']}")
    print("=" * 70)

    analysis = full_varga_analysis(chart)
    for varga_key, data in analysis.items():
        print(f"\n>>> {data['varga']}")
        print(f"    Purpose: {data['purpose']}")
        for k, v in data.items():
            if k in ("varga", "purpose", "interpretation"): continue
            if v is None or v == []: continue
            print(f"    {k}: {v}")
        if data.get("interpretation"):
            print(f"    INTERPRETATION:")
            for n in data["interpretation"]:
                print(f"      - {n}")
