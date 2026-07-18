"""Ashtakavarga Reductions — Trikona Sodhana + Ekadhipatya Sodhana.

Source: BPHS Ch. 67-68, Phaladeepika Ch. 25.

After computing raw Bhinna Ashtakavarga, two reductions are applied to refine:

1. TRIKONA SODHANA (Trine Reduction):
   - Within each trine of signs (Aries-Leo-Sagittarius / Taurus-Virgo-Capricorn / etc.),
     find the minimum bindu count and subtract it from all 3 signs in that trine.
   - This refines the relative strength.

2. EKADHIPATYA SODHANA (Common-Lord Reduction):
   - For signs ruled by the same lord (e.g., Mars rules Aries+Scorpio),
     reduce based on which sign has more bindus.
   - This eliminates double-counting when one planet rules two signs.

Final result: Sodhita (purified) Ashtakavarga used for advanced predictions.
"""
import sys
sys.path.insert(0, ".")
from vedic_core import RASIS, RASI_LORDS

# Trines: indexed by sign-idx 0=Aries
TRINES = [
    [0, 4, 8],   # Aries-Leo-Sagittarius (fire)
    [1, 5, 9],   # Taurus-Virgo-Capricorn (earth)
    [2, 6, 10],  # Gemini-Libra-Aquarius (air)
    [3, 7, 11],  # Cancer-Scorpio-Pisces (water)
]

# Lord-pair mapping: lord → [sign_idx_a, sign_idx_b]
LORD_PAIRS = {
    "Mars":   [0, 7],   # Aries + Scorpio
    "Venus":  [1, 6],   # Taurus + Libra
    "Mercury":[2, 5],   # Gemini + Virgo
    "Jupiter":[8, 11],  # Sagittarius + Pisces
    "Saturn": [9, 10],  # Capricorn + Aquarius
    # Sun/Moon rule one sign each, no Ekadhipatya reduction
}


def trikona_sodhana(bhinna_av_planet):
    """Apply trine reduction to one planet's Bhinna AV.

    Input: dict {house_1: bindus, ..., house_12: bindus}
    Returns: dict with reduced bindus.
    """
    # Get bindus per sign
    sign_bindus = {}
    for h in range(1, 13):
        sign_bindus[h] = bhinna_av_planet.get(f"house_{h}", 0)

    reduced = sign_bindus.copy()

    for trine in TRINES:
        trine_houses = [h+1 for h in trine]  # convert to 1-indexed
        values = [reduced[h] for h in trine_houses]
        min_val = min(values)
        for h in trine_houses:
            reduced[h] -= min_val

    return {f"house_{h}": reduced[h] for h in range(1, 13)}


def ekadhipatya_sodhana(bhinna_av_planet):
    """Apply common-lord reduction.

    For each pair of signs ruled by the same lord:
    - If both have bindus, reduce smaller to 0 and subtract its value from larger.
    - If exactly one has 0 and other has bindus, larger becomes 0 too.
    """
    sign_bindus = {}
    for h in range(1, 13):
        sign_bindus[h] = bhinna_av_planet.get(f"house_{h}", 0)

    # Map houses to sign indices (we don't have the chart's lagna, so this is approximate)
    # For this function, we treat house_1 as containing sign[0] etc. — adjust if needed
    reduced = sign_bindus.copy()

    for lord, sign_pair in LORD_PAIRS.items():
        h1 = sign_pair[0] + 1
        h2 = sign_pair[1] + 1
        v1 = reduced.get(h1, 0)
        v2 = reduced.get(h2, 0)
        if v1 > 0 and v2 > 0:
            if v1 > v2:
                reduced[h1] -= v2
                reduced[h2] = 0
            elif v2 > v1:
                reduced[h2] -= v1
                reduced[h1] = 0
            else:
                reduced[h1] = 0
                reduced[h2] = 0
        elif v1 > 0 and v2 == 0:
            reduced[h2] = 0
        elif v2 > 0 and v1 == 0:
            reduced[h1] = 0

    return {f"house_{h}": reduced[h] for h in range(1, 13)}


def sodhita_ashtakavarga(chart):
    """Compute fully reduced (Sodhita) Ashtakavarga for all 7 planets."""
    from engine.ashtakavarga import compute_bhinna_ashtakavarga
    bhinna = compute_bhinna_ashtakavarga(chart)
    out = {}
    for planet, av in bhinna.items():
        # First Trikona
        after_trikona = trikona_sodhana(av)
        # Then Ekadhipatya
        after_eka = ekadhipatya_sodhana(after_trikona)
        total = sum(after_eka[f"house_{h}"] for h in range(1, 13))
        out[planet] = {**after_eka, "total": total, "raw_total": av["total"]}
    return out


def kakshya_bala(chart):
    """Kakshya Bala — strength of houses based on Sodhita AV.

    Each planet contributes its Sodhita bindus to its house.
    Used for transit prediction.
    """
    sodh = sodhita_ashtakavarga(chart)
    pos = chart["positions"]

    house_strengths = {f"H{h}": 0 for h in range(1, 13)}
    for p, av in sodh.items():
        if p not in pos: continue
        h = pos[p]["house"]
        house_strengths[f"H{h}"] += av.get(f"house_{h}", 0)
    return house_strengths


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    sodh = sodhita_ashtakavarga(chart)
    print(f"=== SODHITA ASHTAKAVARGA (after Trikona + Ekadhipatya) for {chart['name']} ===\n")
    print(f"{'Planet':<10}" + "".join(f"H{h:<3}" for h in range(1, 13)) + " RawTotal SodhitaTotal")
    for p, av in sodh.items():
        row = f"{p:<10}"
        for h in range(1, 13):
            row += f"{av[f'house_{h}']:<4}"
        row += f" {av['raw_total']}/{av['total']}"
        print(row)

    print(f"\n=== KAKSHYA BALA (house strengths) ===")
    kb = kakshya_bala(chart)
    for h, val in kb.items():
        print(f"  {h}: {val} bindus")
