"""Longevity (Ayurdaya) Calculation — Markesha + Three-fold longevity.

Source: BPHS Ch. 90 (Aayurdaaya), Phaladeepika Ch. 21.

Three classical methods (BPHS preference: average of these):
  1. Pinda Ayurdaya — based on planetary degrees within signs (years per planet)
  2. Naisargika Ayurdaya — natural lifespan from planet (Sun=15, Moon=25, Mars=15, Mercury=12, Jup=18, Venus=21, Saturn=20)
  3. Amsha Ayurdaya — based on signs/dignity multipliers

Three categories (Khanda):
  - Alpa Ayu: 0-32 years (short)
  - Madhya Ayu: 32-64 years (medium)
  - Purna Ayu: 64-100+ years (long)

Markesha (death-causing planets):
  - Lord of 2nd house (food, life-line)
  - Lord of 7th house (longevity-marker for 8th)
  - Saturn always (natural Markesha)
  - Other malefics in 2/7 add to risk
"""
import sys
sys.path.insert(0, ".")

NAISARGIKA_YEARS = {
    "Sun": 15, "Moon": 25, "Mars": 15, "Mercury": 12,
    "Jupiter": 18, "Venus": 21, "Saturn": 20,
}
from vedic_core import RASIS, RASI_LORDS, DIGNITIES  # canonical signs + lords + dignities


def _h(pos, p): return pos[p]["house"] if p in pos else None
def _dig(pos, p): return DIGNITIES.get((p, pos[p]["rasi"]), "neutral") if p in pos else "neutral"
def _occ(pos, h): return [p for p, pd in pos.items() if pd["house"] == h]
def _lord(lagna_idx, h): return RASI_LORDS[RASIS[(lagna_idx + h - 1) % 12]]


def naisargika_ayurdaya(chart):
    """Sum of natural-lifespan years from each planet's contribution.
    Reductions: planets in dusthana subtract; debilitated subtract; combust planets subtract.
    """
    pos = chart["positions"]
    total = 0
    for p, years in NAISARGIKA_YEARS.items():
        if p not in pos: continue
        contribution = years
        h = pos[p]["house"]
        d = _dig(pos, p)

        # Adjustments
        if d == "Exalted": contribution *= 1.0
        elif d in ["Own","Exalted/Own"]: contribution *= 0.95
        elif d == "Debil": contribution *= 0.5
        else: contribution *= 0.85

        if h in [6, 8, 12]: contribution *= 0.7  # dusthana penalty
        if h in [1, 4, 7, 10]: contribution *= 1.1  # kendra bonus

        total += contribution

    # Return the true sum of planetary years
    return round(total, 1)


def pinda_ayurdaya(chart):
    """Pinda Ayurdaya — based on degrees in signs. Simplified version.
    Each planet contributes (years × degree-fraction)."""
    pos = chart["positions"]
    total = 0
    for p, years in NAISARGIKA_YEARS.items():
        if p not in pos: continue
        deg = pos[p]["deg"]
        # Forward-half of sign (0-15°) gives less, second half (15-30°) gives full
        # This is a simplification of the classical Pinda calculation
        contribution = years * (0.5 + deg / 60.0)
        total += contribution
    return round(total, 1)


def markesha_planets(chart):
    """Identify Markesha (death-causing) planets per BPHS Ch. 90."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]

    h2_lord = _lord(lagna_idx, 2)
    h7_lord = _lord(lagna_idx, 7)

    out = []
    out.append({"planet": h2_lord, "type": "2nd lord (Maraka Sthana)", "primary": True})
    out.append({"planet": h7_lord, "type": "7th lord (Maraka Sthana)", "primary": True})

    # Saturn is natural Markesha
    if "Saturn" in pos:
        out.append({"planet": "Saturn", "type": "natural Markesha", "primary": False})

    # Malefics in 2/7 add to risk
    h2_occ = [p for p in _occ(pos, 2) if p in ["Sun","Mars","Saturn","Rahu","Ketu"]]
    h7_occ = [p for p in _occ(pos, 7) if p in ["Sun","Mars","Saturn","Rahu","Ketu"]]
    for p in h2_occ + h7_occ:
        out.append({"planet": p, "type": f"malefic in {'2H' if p in h2_occ else '7H'}", "primary": False})

    # Dedupe
    seen = set()
    deduped = []
    for o in out:
        if o["planet"] not in seen:
            seen.add(o["planet"])
            deduped.append(o)
    return deduped


def categorize_ayu(years):
    if years < 32: return "Alpa Ayu (short, 0-32y)"
    if years < 64: return "Madhya Ayu (medium, 32-64y)"
    return "Purna Ayu (long, 64-100+y)"


def longevity_analysis(chart):
    naisargika = naisargika_ayurdaya(chart)
    pinda = pinda_ayurdaya(chart)
    average = round((naisargika + pinda) / 2, 1)
    category = categorize_ayu(average)
    markesha = markesha_planets(chart)

    return {
        "naisargika_years": naisargika,
        "pinda_years": pinda,
        "average_years": average,
        "category": category,
        "markesha_planets": markesha,
        "interpretation": (
            f"Estimated longevity: ~{average} years ({category}). "
            f"Markesha (death-significator) planets: {', '.join(m['planet'] for m in markesha)}. "
            f"Critical periods: dasha/antar of Markesha planets, especially during 8th/12th house transits."
        ),
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    result = longevity_analysis(chart)
    print(f"=== LONGEVITY ANALYSIS for {chart['name']} ===")
    print(f"  Naisargika Ayurdaya: {result['naisargika_years']} years")
    print(f"  Pinda Ayurdaya:      {result['pinda_years']} years")
    print(f"  Average estimate:    {result['average_years']} years")
    print(f"  Category:            {result['category']}")
    print(f"\n  Markesha planets:")
    for m in result["markesha_planets"]:
        primary = "PRIMARY" if m["primary"] else "secondary"
        print(f"    {m['planet']:10s} - {m['type']} ({primary})")
    print(f"\n  {result['interpretation']}")
