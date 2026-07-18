"""
Bhava Bala (house strength) + Ishta-Kashta Phala (joy/suffering scoring).

BPHS Ch.32-34. House strength is computed independently of planet strength,
combining:
    1. Adhipati Bala  — strength of the house lord
    2. Dig Bala        — direction (already in shadbala)
    3. Kala Bala       — temporal (paksha + day/night)
    4. Drik Bala       — sum of benefic vs malefic aspects on the cusp
    5. Bhavadhipati B. — derived from sthana + dig + kala bala of house lord

Ishta-Kashta Phala (BPHS Ch.31): per planet, ratio of "joy-giving"
(uchcha bala × cheshta bala) to "suffering" (60 - that). Used for
nuanced result interpretation in dasha periods.

API:
    bhava_bala(chart) → {house: {total, components}}
    ishta_kashta(chart) → {planet: {ishta, kashta, ratio}}
"""
from __future__ import annotations

import math

SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


def _aspect_houses(planet: str, planet_house: int) -> set[int]:
    """Houses aspected by `planet` (Parashari aspect rules)."""
    aspects = {
        "Sun": [7], "Moon": [7], "Mercury": [7], "Venus": [7],
        "Mars": [4, 7, 8], "Jupiter": [5, 7, 9], "Saturn": [3, 7, 10],
        "Rahu": [5, 7, 9], "Ketu": [5, 7, 9],
    }
    return {((planet_house + off - 1 - 1) % 12) + 1 for off in aspects.get(planet, [7])}


def _planet_house(longitude: float, lagna_sign: int) -> int:
    sign = int(longitude // 30)
    return ((sign - lagna_sign) % 12) + 1


# ─── Bhava Bala ────────────────────────────────────────────────────────────
def bhava_bala(chart) -> dict[int, dict]:
    """House strength, in Virupas, per BPHS Ch.32."""
    lagna_sign = int(chart.lagna_lon // 30)
    out: dict[int, dict] = {}

    # Adhipati bala = sthana+dig+kala+drig of house lord
    sb = chart.shadbala if hasattr(chart, "shadbala") else {}

    for h in range(1, 13):
        lord_sign = (lagna_sign + h - 1) % 12
        lord = SIGN_LORD[lord_sign]
        lord_score = sb.get(lord, {})
        # Adhipati bala — sum of all balas of the house lord (already V)
        adhipati = lord_score.get("total_virupas", 0.0)

        # Bhava Drik bala — benefic aspects ON this house's cusp minus malefic
        drik = 30.0    # baseline neutral
        for p, lon in chart.positions.items():
            if p in ("Rahu", "Ketu"):
                continue
            p_sign = int(lon // 30)
            p_house = ((p_sign - lagna_sign) % 12) + 1
            if h in _aspect_houses(p, p_house):
                if p in BENEFICS:
                    drik += 10.0
                elif p in MALEFICS:
                    drik -= 10.0
        drik = max(0.0, min(60.0, drik))

        # Bhava Dig bala — kendra/panapara/apoklima
        dig = 60.0 if h in (1, 4, 7, 10) else (
            30.0 if h in (2, 5, 8, 11) else 15.0
        )

        # Total bhava bala (simplified)
        total = adhipati / 10 + drik + dig
        out[h] = {
            "total_virupas": round(total, 2),
            "rupas":         round(total / 60, 2),
            "components": {
                "lord": lord,
                "adhipati_bala_scaled": round(adhipati / 10, 2),
                "drik_bala": round(drik, 2),
                "dig_bala": round(dig, 2),
            },
            "is_strong": total >= 60,    # 1 rupa threshold
        }
    return out


# ─── Ishta-Kashta Phala ────────────────────────────────────────────────────
def ishta_kashta(chart) -> dict[str, dict]:
    """Per-planet Ishta (joy-giving) and Kashta (suffering) scores.

    Formula (BPHS Ch.31, Phaladeepika Ch.5):
        Ishta phala = sqrt(uchcha-bala × cheshta-bala)
        Kashta phala = 60 - Ishta phala  (clamped)

    Range 0-60 V each.
    """
    sb = chart.shadbala if hasattr(chart, "shadbala") else {}
    out: dict[str, dict] = {}
    for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        score = sb.get(planet, {})
        comps = score.get("components", {})
        uchcha = comps.get("uchcha", 30.0)
        cheshta = comps.get("cheshta", 30.0)
        ishta = math.sqrt(uchcha * cheshta)
        kashta = max(0.0, 60.0 - ishta)
        ratio = ishta / (ishta + kashta) if (ishta + kashta) > 0 else 0.5
        out[planet] = {
            "ishta_virupas":  round(ishta, 2),
            "kashta_virupas": round(kashta, 2),
            "ratio_ishta":    round(ratio, 3),
            "interpretation": _interpret_ratio(ratio),
        }
    return out


def _interpret_ratio(r: float) -> str:
    if r >= 0.75:
        return "predominantly joy-giving — dasha period brings positive results"
    if r >= 0.55:
        return "moderately joy-giving — mixed but tilted positive"
    if r >= 0.45:
        return "balanced — equal joy and suffering during dasha"
    if r >= 0.25:
        return "moderately suffering — dasha brings difficulty"
    return "predominantly suffering — dasha brings hardship"


def summary(chart) -> dict:
    bb = bhava_bala(chart)
    ik = ishta_kashta(chart)
    return {
        "bhava_bala": {
            f"H{h}": {**v, "house_meaning": _house_meaning(h)}
            for h, v in bb.items()
        },
        "weakest_houses": sorted(
            [(b["total_virupas"], h) for h, b in bb.items()]
        )[:3],
        "strongest_houses": sorted(
            [(b["total_virupas"], h) for h, b in bb.items()],
            reverse=True
        )[:3],
        "ishta_kashta": ik,
        "joy_planets": [p for p, v in ik.items() if v["ratio_ishta"] >= 0.55],
        "suffering_planets": [p for p, v in ik.items() if v["ratio_ishta"] < 0.45],
    }


def _house_meaning(h: int) -> str:
    return {
        1: "self/health", 2: "wealth/family", 3: "siblings/courage",
        4: "home/mother", 5: "children/intelligence", 6: "enemies/disease",
        7: "spouse/partnership", 8: "longevity/secrets", 9: "fortune/dharma",
        10: "career/status", 11: "gains/desires", 12: "loss/moksha",
    }.get(h, "")
