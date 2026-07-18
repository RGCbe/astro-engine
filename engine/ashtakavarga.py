"""
Ashtakavarga — 8-fold strength map per planet across 12 signs.

The most important Vedic predictive technique not in the engine until now.
Each of 7 grahas (excluding nodes) gets a 8x12 grid: from each contributor
(Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna), record which
signs (counted from contributor) "give" a bindu (auspicious dot).

Total per sign across all 8 contributors = bhinna ashtakavarga (BAV).
Sum of all 7 BAVs per sign = sarva ashtakavarga (SAV).
Then Shodhana (purification): trikona shodhana removes columns whose
trine totals are below threshold; ekadhipatya shodhana removes one of
two-signs-by-same-lord when one is empty.

Reference: BPHS Ch.49-50 (Santhanam translation), Phaladeepika Ch.18,
Saravali Ch.42, Sanjay Rath "Crux" Ch.13.

API:
    bhinna_ashtakavarga(chart) → {planet: [bindus per sign 0-11]}
    sarva_ashtakavarga(chart) → [total bindus per sign 0-11]
    transit_strength(chart, transit_planet, at_dt) → bindu count in transit sign
    auspicious_houses(chart, planet) → list of houses where SAV > threshold

The bindu thresholds (BPHS standard):
    SAV total >= 30 in a sign = strong; >= 25 = above-average; <= 20 = weak.
    BAV total per planet:
       Sun: ≥4 strong; Moon: ≥4; Mars: ≥4; Mercury: ≥5; Jupiter: ≥5;
       Venus: ≥5; Saturn: ≥3.
"""
from __future__ import annotations

# Bindu rules per contributor for each "from-this-contributor count house":
# Each row: contributor → set of houses (1-12, counted from contributor's
# sign) where the *target planet* gets a bindu.
#
# Source: BPHS Ch.49 verse 4-29. Tabulated faithfully from Santhanam.

BINDU_RULES: dict[str, dict[str, set[int]]] = {
    "Sun": {
        "Sun":     {1, 2, 4, 7, 8, 9, 10, 11},
        "Moon":    {3, 6, 10, 11},
        "Mars":    {1, 2, 4, 7, 8, 9, 10, 11},
        "Mercury": {3, 5, 6, 9, 10, 11, 12},
        "Jupiter": {5, 6, 9, 11},
        "Venus":   {6, 7, 12},
        "Saturn":  {1, 2, 4, 7, 8, 9, 10, 11},
        "Lagna":   {3, 4, 6, 10, 11, 12},
    },
    "Moon": {
        "Sun":     {3, 6, 7, 8, 10, 11},
        "Moon":    {1, 3, 6, 7, 10, 11},
        "Mars":    {2, 3, 5, 6, 9, 10, 11},
        "Mercury": {1, 3, 4, 5, 7, 8, 10, 11},
        "Jupiter": {1, 4, 7, 8, 10, 11, 12},
        "Venus":   {3, 4, 5, 7, 9, 10, 11},
        "Saturn":  {3, 5, 6, 11},
        "Lagna":   {3, 6, 10, 11},
    },
    "Mars": {
        "Sun":     {3, 5, 6, 10, 11},
        "Moon":    {3, 6, 11},
        "Mars":    {1, 2, 4, 7, 8, 10, 11},
        "Mercury": {3, 5, 6, 11},
        "Jupiter": {6, 10, 11, 12},
        "Venus":   {6, 8, 11, 12},
        "Saturn":  {1, 4, 7, 8, 9, 10, 11},
        "Lagna":   {1, 3, 6, 10, 11},
    },
    "Mercury": {
        "Sun":     {5, 6, 9, 11, 12},
        "Moon":    {2, 4, 6, 8, 10, 11},
        "Mars":    {1, 2, 4, 7, 8, 9, 10, 11},
        "Mercury": {1, 3, 5, 6, 9, 10, 11, 12},
        "Jupiter": {6, 8, 11, 12},
        "Venus":   {1, 2, 3, 4, 5, 8, 9, 11},
        "Saturn":  {1, 2, 4, 7, 8, 9, 10, 11},
        "Lagna":   {1, 2, 4, 6, 8, 10, 11},
    },
    "Jupiter": {
        "Sun":     {1, 2, 3, 4, 7, 8, 9, 10, 11},
        "Moon":    {2, 5, 7, 9, 11},
        "Mars":    {1, 2, 4, 7, 8, 10, 11},
        "Mercury": {1, 2, 4, 5, 6, 9, 10, 11},
        "Jupiter": {1, 2, 3, 4, 7, 8, 10, 11},
        "Venus":   {2, 5, 6, 9, 10, 11},
        "Saturn":  {3, 5, 6, 12},
        "Lagna":   {1, 2, 4, 5, 6, 7, 9, 10, 11},
    },
    "Venus": {
        "Sun":     {8, 11, 12},
        "Moon":    {1, 2, 3, 4, 5, 8, 9, 11, 12},
        "Mars":    {3, 4, 6, 9, 11, 12},
        "Mercury": {3, 5, 6, 9, 11},
        "Jupiter": {5, 8, 9, 10, 11},
        "Venus":   {1, 2, 3, 4, 5, 8, 9, 10, 11},
        "Saturn":  {3, 4, 5, 8, 9, 10, 11},
        "Lagna":   {1, 2, 3, 4, 5, 8, 9, 11},
    },
    "Saturn": {
        "Sun":     {1, 2, 4, 7, 8, 10, 11},
        "Moon":    {3, 6, 11},
        "Mars":    {3, 5, 6, 10, 11, 12},
        "Mercury": {6, 8, 9, 10, 11, 12},
        "Jupiter": {5, 6, 11, 12},
        "Venus":   {6, 11, 12},
        "Saturn":  {3, 5, 6, 11},
        "Lagna":   {1, 3, 4, 6, 10, 11},
    },
}

# BAV thresholds (BPHS) — bindu count per sign for "strong" classification
BAV_STRONG_THRESHOLD = {
    "Sun": 4, "Moon": 4, "Mars": 4, "Mercury": 5,
    "Jupiter": 5, "Venus": 5, "Saturn": 3,
}

# SAV total per sign (sum across all 7 planets)
SAV_STRONG_TOTAL = 30
SAV_WEAK_TOTAL = 20

PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
SIGN_NAMES = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)


def _planet_sign(chart, planet: str) -> int:
    """0-indexed sign of a planet (or 'Lagna')."""
    if planet == "Lagna":
        return int(chart.lagna_lon // 30)
    return int(chart.positions[planet] // 30)


def bhinna_ashtakavarga(chart) -> dict[str, list[int]]:
    """Per-planet 12-element bindu list (one entry per sign, 0=Aries .. 11=Pisces)."""
    out: dict[str, list[int]] = {}
    for target in PLANETS:
        bindus = [0] * 12
        rules = BINDU_RULES[target]
        for contributor, good_houses in rules.items():
            con_sign = _planet_sign(chart, contributor)
            for h in good_houses:
                target_sign = (con_sign + h - 1) % 12
                bindus[target_sign] += 1
        out[target] = bindus
    return out


def sarva_ashtakavarga(chart) -> list[int]:
    """SAV: sum of all 7 BAVs per sign."""
    bav = bhinna_ashtakavarga(chart)
    sav = [0] * 12
    for planet, bindus in bav.items():
        for i, b in enumerate(bindus):
            sav[i] += b
    return sav


def trikona_shodhana(bav: list[int]) -> list[int]:
    """Trikona shodhana: for each set of 3 trines (1/5/9, 2/6/10, etc.),
    keep min and zero the rest. Output: purified BAV.
    """
    out = list(bav)
    # Trines: (0,4,8), (1,5,9), (2,6,10), (3,7,11)
    for trine in [(0, 4, 8), (1, 5, 9), (2, 6, 10), (3, 7, 11)]:
        triple = [bav[i] for i in trine]
        m = min(triple)
        for i in trine:
            out[i] = bav[i] - m if bav[i] > m else 0
    return out


# Ekadhipatya shodhana — pairs of signs by same lord
EKADHIPATYA_PAIRS = {
    "Mars":    (0, 7),    # Aries / Scorpio
    "Venus":   (1, 6),    # Taurus / Libra
    "Mercury": (2, 5),    # Gemini / Virgo
    "Jupiter": (8, 11),   # Sagittarius / Pisces
    "Saturn":  (9, 10),   # Capricorn / Aquarius
}


def ekadhipatya_shodhana(bav_after_trikona: list[int]) -> list[int]:
    """For each lord-pair, if one sign is empty (0) zero the other; else
    subtract the smaller from the larger and keep difference."""
    out = list(bav_after_trikona)
    for lord, (a, b) in EKADHIPATYA_PAIRS.items():
        if out[a] == 0 or out[b] == 0:
            out[a] = out[b] = 0
        else:
            mn = min(out[a], out[b])
            out[a] -= mn
            out[b] -= mn
    return out


def shodhana(bav: list[int]) -> list[int]:
    """Apply trikona then ekadhipatya purification."""
    return ekadhipatya_shodhana(trikona_shodhana(bav))


def bav_strength_label(planet: str, bindus_in_sign: int) -> str:
    threshold = BAV_STRONG_THRESHOLD.get(planet, 4)
    if bindus_in_sign >= threshold + 2:
        return "EXCELLENT"
    if bindus_in_sign >= threshold:
        return "STRONG"
    if bindus_in_sign >= threshold - 1:
        return "AVERAGE"
    return "WEAK"


def sav_strength_label(total: int) -> str:
    if total >= SAV_STRONG_TOTAL + 5:
        return "EXCELLENT"
    if total >= SAV_STRONG_TOTAL:
        return "STRONG"
    if total >= SAV_WEAK_TOTAL:
        return "AVERAGE"
    return "WEAK"


def transit_strength(chart, transit_planet: str, transit_lon: float) -> dict:
    """When `transit_planet` enters a sign, look up its BAV for that sign.
    A planet transiting through a sign with high own-BAV gives strong results."""
    bav = bhinna_ashtakavarga(chart)
    sign = int(transit_lon // 30)
    own_bindus = bav[transit_planet][sign]
    sav = sarva_ashtakavarga(chart)
    sav_in_sign = sav[sign]
    return {
        "transit_planet": transit_planet,
        "transit_sign": SIGN_NAMES[sign],
        "BAV_bindus_for_self": own_bindus,
        "BAV_strength":  bav_strength_label(transit_planet, own_bindus),
        "SAV_total": sav_in_sign,
        "SAV_strength": sav_strength_label(sav_in_sign),
        "interpretation": (
            f"{transit_planet} transits {SIGN_NAMES[sign]} with own-BAV "
            f"{own_bindus} bindus ({bav_strength_label(transit_planet, own_bindus)}) "
            f"and SAV {sav_in_sign} ({sav_strength_label(sav_in_sign)})."
        ),
    }


def kaksha_vibhaga(chart, planet: str) -> dict[str, list[int]]:
    """Kaksha analysis: for each of 8 contributors, which signs give bindu
    to `planet`. Returns per-contributor 12-list."""
    out = {}
    rules = BINDU_RULES[planet]
    for contributor, good_houses in rules.items():
        con_sign = _planet_sign(chart, contributor)
        contribs = [0] * 12
        for h in good_houses:
            target_sign = (con_sign + h - 1) % 12
            contribs[target_sign] = 1
        out[contributor] = contribs
    return out


def summary(chart) -> dict:
    """Full ashtakavarga summary."""
    bav = bhinna_ashtakavarga(chart)
    sav = sarva_ashtakavarga(chart)
    lagna_sign = int(chart.lagna_lon // 30)
    out = {
        "bhinna_ashtakavarga": {
            p: {
                "bindus": bav[p],
                "by_house_from_lagna": [
                    {"house": ((sign - lagna_sign) % 12) + 1,
                     "sign": SIGN_NAMES[sign], "bindus": bav[p][sign],
                     "strength": bav_strength_label(p, bav[p][sign])}
                    for sign in range(12)
                ],
                "total": sum(bav[p]),
                "strongest_signs":
                    sorted(((bav[p][s], SIGN_NAMES[s]) for s in range(12)),
                           reverse=True)[:3],
            }
            for p in PLANETS
        },
        "sarva_ashtakavarga": {
            "totals_per_sign": sav,
            "by_house_from_lagna": [
                {"house": ((sign - lagna_sign) % 12) + 1,
                 "sign": SIGN_NAMES[sign], "total": sav[sign],
                 "strength": sav_strength_label(sav[sign])}
                for sign in range(12)
            ],
            "grand_total": sum(sav),    # always 337 (28x12+1)
            "expected_grand_total": 337,
        },
        "shodhana": {
            p: {
                "after_trikona":      trikona_shodhana(bav[p]),
                "after_ekadhipatya":  shodhana(bav[p]),
            }
            for p in PLANETS
        },
    }
    return out


# ─── Runtime dict-chart API (consolidated from runtime/ashtakavarga.py) ────
# These functions accept the JSON dict-based chart format used by
# runtime/engine_orchestrator.py and runtime/generate_report.py.
# Chart format: chart["positions"][planet] = {"house": int, "rasi": str,
#               "rasi_idx": int, "lon": float}, chart["lagna_idx"] = int.

# Alias for runtime API parity — same data as BINDU_RULES (frozenset → list).
BINDU_TABLES = {
    src: {ref: sorted(houses) for ref, houses in refs.items()}
    for src, refs in BINDU_RULES.items()
}


def compute_bhinna_ashtakavarga(chart):
    """Per-planet bhinna ashtakavarga computed from a dict-based chart.

    chart: {"positions": {planet: {"rasi_idx": int, "house": int}, ...},
            "lagna_idx": int}
    Returns: {planet: {"house_1": bindu, ..., "house_12": bindu, "total": N}}
    """
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    out: dict[str, dict] = {}

    for source in PLANETS:
        if source not in pos:
            continue
        bindus_per_house = [0] * 12
        contributions = BINDU_TABLES.get(source, {})

        for ref_planet, ref_houses in contributions.items():
            if ref_planet == "Lagna":
                ref_position = lagna_idx + 1
            elif ref_planet in pos:
                ref_position = pos[ref_planet]["rasi_idx"] + 1
            else:
                continue

            for h_offset in ref_houses:
                target_sign = ((ref_position - 1 + h_offset - 1) % 12) + 1
                house_from_lagna = ((target_sign - lagna_idx - 1) % 12) + 1
                bindus_per_house[house_from_lagna - 1] += 1

        total = sum(bindus_per_house)
        out[source] = {f"house_{i+1}": bindus_per_house[i] for i in range(12)}
        out[source]["total"] = total

    return out


def compute_sarvashtakavarga(bhinna):
    """Sum all 7 bhinna AVs into Sarvashtakavarga (combined).

    bhinna: output of compute_bhinna_ashtakavarga()
    Returns: {"house_1": total, ..., "house_12": total, "grand_total": N}
    """
    out = {f"house_{i}": 0 for i in range(1, 13)}
    for planet, av in bhinna.items():
        for h in range(1, 13):
            out[f"house_{h}"] += av.get(f"house_{h}", 0)
    out["grand_total"] = sum(out[f"house_{h}"] for h in range(1, 13))
    return out


def interpret_house_bindus(house, bindu_count):
    """Verdict string for a sarvashtakavarga house total."""
    if bindu_count >= 30:
        return "excellent — themes thrive"
    if bindu_count >= 25:
        return "good — supportive house"
    if bindu_count >= 20:
        return "neutral — average results"
    if bindu_count >= 15:
        return "weak — challenges in this domain"
    return "very weak — significant obstacles"


def ashtakavarga_summary(chart):
    """Text summary of bhinna + sarvashtakavarga for a dict-based chart."""
    bhinna = compute_bhinna_ashtakavarga(chart)
    sarva = compute_sarvashtakavarga(bhinna)

    lines = ["=== BHINNA ASHTAKAVARGA (per planet) ==="]
    lines.append(f"{'Planet':<10}" + "".join(f"H{h:<3}" for h in range(1, 13)) + " Total")
    for p, av in bhinna.items():
        row = f"{p:<10}"
        for h in range(1, 13):
            row += f"{av[f'house_{h}']:<4}"
        row += f" {av['total']}"
        lines.append(row)

    lines.append("\n=== SARVASHTAKAVARGA (combined) ===")
    lines.append(f"{'House':<8}{'Bindus':<10}Verdict")
    for h in range(1, 13):
        b = sarva[f"house_{h}"]
        lines.append(f"H{h:<7}{b:<10}{interpret_house_bindus(h, b)}")
    lines.append(f"\nGrand Total: {sarva['grand_total']} (BPHS standard = 337)")
    return "\n".join(lines)
