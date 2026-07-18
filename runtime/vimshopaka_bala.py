"""Vimshopaka Bala — Varga-based combined strength (out of 20 points).

Source: BPHS Ch. 7-9 (Shodashvarga), Phaladeepika Ch. 5.

Vimshopaka = "out of 20" — gives composite strength based on each planet's
dignity across multiple vargas. Three classes:

  Shadvarga (6 vargas):  D1 + D2 + D3 + D9 + D12 + D30  (max 20 pts)
  Saptavarga (7 vargas): D1 + D2 + D3 + D7 + D9 + D12 + D30  (max 20 pts)
  Dasavarga (10 vargas): D1 + D2 + D3 + D7 + D9 + D10 + D12 + D16 + D30 + D60 (max 20 pts)
  Shodasavarga (16 vargas): all 16 vargas (max 20 pts)

Higher Vimshopaka = stronger in vargas → results manifest more strongly.
"""
import sys
sys.path.insert(0, ".")
from vedic_core import DIGNITIES, RASIS, RASI_LORDS

# Weighting per varga (BPHS standard for Dasavarga)
DASAVARGA_WEIGHTS = {
    "D1":  3.0,   # Rasi
    "D2":  1.5,   # Hora
    "D3":  1.5,   # Drekkana
    "D7":  1.5,   # Saptamsa
    "D9":  1.5,   # Navamsa
    "D10": 1.5,   # Dashamsa
    "D12": 1.5,   # Dwadashamsa
    "D16": 2.0,   # Shodashamsa
    "D30": 2.0,   # Trimshamsa
    "D60": 4.0,   # Shashtiamsa (highest weight per Parashara)
}

# Dignity points (out of varga's weight)
DIGNITY_FRACTIONS = {
    "Exalted": 1.0,
    "Own": 0.85, "Exalted/Own": 0.85,
    "Friend": 0.6,
    "Neutral": 0.4,
    "Enemy": 0.2,
    "Debil": 0.0,
}


def planet_dignity_in_varga(chart, planet, varga):
    """Get planet's dignity in given varga."""
    from divisional_charts import build_divisional_chart
    from extra_vargas import build_extra_varga, EXTRA_VARGA_FNS
    try:
        if varga == "D1":
            sign = chart["positions"][planet]["rasi"]
        elif varga in EXTRA_VARGA_FNS:
            v = build_extra_varga(chart, varga)
            sign = v["positions"][planet]["rasi"]
        else:
            v = build_divisional_chart(chart, varga)
            sign = v["positions"][planet]["rasi"]
        return DIGNITIES.get((planet, sign), "neutral").capitalize()
    except Exception:
        return "Neutral"


def compute_vimshopaka(chart):
    """Compute Dasavarga Vimshopaka Bala for each planet (max 20)."""
    out = {}
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        if p not in chart["positions"]: continue
        total = 0
        per_varga = {}
        for varga, weight in DASAVARGA_WEIGHTS.items():
            d = planet_dignity_in_varga(chart, p, varga)
            frac = DIGNITY_FRACTIONS.get(d, 0.4)
            pts = weight * frac
            per_varga[varga] = {"dignity": d, "weight": weight, "points": round(pts, 2)}
            total += pts

        out[p] = {
            "total_vimshopaka": round(total, 2),
            "max_possible": 20.0,
            "ratio": round(total / 20.0, 2),
            "verdict": _verdict(total),
            "per_varga": per_varga,
        }
    return out


def _verdict(score):
    if score >= 16: return "EXCELLENT (very strong vargas)"
    if score >= 12: return "GOOD (strong vargas)"
    if score >= 8: return "AVERAGE"
    if score >= 5: return "WEAK"
    return "VERY WEAK"


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    v = compute_vimshopaka(chart)
    print(f"=== VIMSHOPAKA BALA (Dasavarga) for {chart['name']} ===\n")
    print(f"{'Planet':<10}{'Total /20':<12}{'Ratio':<8}{'Verdict'}")
    for p, b in v.items():
        print(f"  {p:<10}{b['total_vimshopaka']:<12.2f}{b['ratio']:<8.2f}{b['verdict']}")
