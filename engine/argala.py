"""
Argala / Virodhargala — Jaimini intervention/obstruction analysis.

Argala = "intervention" — planets in 2nd/4th/5th/8th/11th from a target sign
intervene in (modify, support, complete) that sign's events.

Virodhargala = "obstruction" — planets in 12th/10th/9th/6th/3rd from the
target sign obstruct or cancel the argala from those respective houses.

Argala houses:
    2nd  argala — sustenance, family, accumulation
    4th  argala — comfort, completion of efforts
    5th  argala — intelligence, breakthrough
    8th  argala — sudden upheaval (obstacle to the SIGN, often)
    11th argala — gains, fulfillment

Each argala house has a counter-house (virodhargala):
    Argala from   2nd   ←  Obstructed by  12th
    Argala from   4th   ←  Obstructed by  10th
    Argala from   5th   ←  Obstructed by   9th
    Argala from  11th   ←  Obstructed by   3rd
    Argala from   8th   ←  Obstructed by   6th    (some traditions reverse)

A planet at the argala house "fires" if there are MORE planets there than
in the corresponding virodhargala house.

Source: Jaimini Sutras, Adhyaya 1 Pada 1; Sanjay Rath, Crux Ch.7.

API:
    argala_for_sign(chart, sign_idx) → {arg_house: {fires, planets, virodha_planets}}
    argala_for_house(chart, house_num) → same but specifying chart house
    activated_houses(chart) → houses with strongest net argala
"""
from __future__ import annotations

ARGALA_HOUSES = {
    2: 12,    # 2nd argala obstructed by 12th
    4: 10,
    5: 9,
    11: 3,
    8: 6,
}


def _planets_in_sign(chart, sign_idx: int) -> list[str]:
    out = []
    for p, lon in chart.positions.items():
        if int(lon // 30) == sign_idx:
            out.append(p)
    return out


def argala_for_sign(chart, target_sign: int) -> dict:
    """Compute argala/virodhargala from each argala-house relative to target."""
    out = {}
    for arg_off, vir_off in ARGALA_HOUSES.items():
        arg_sign = (target_sign + arg_off - 1) % 12
        vir_sign = (target_sign + vir_off - 1) % 12
        arg_planets = _planets_in_sign(chart, arg_sign)
        vir_planets = _planets_in_sign(chart, vir_sign)
        n_arg = len(arg_planets)
        n_vir = len(vir_planets)
        # Argala "fires" only if argala-planets > virodha-planets
        fires = n_arg > n_vir
        out[f"{arg_off}th"] = {
            "argala_sign":         arg_sign,
            "virodha_sign":        vir_sign,
            "argala_planets":      arg_planets,
            "virodha_planets":     vir_planets,
            "fires":               fires,
            "net_strength":        n_arg - n_vir,
        }
    return out


def argala_for_house(chart, house_num: int) -> dict:
    """Argala for a specific natal house (1-12)."""
    lagna_sign = int(chart.lagna_lon // 30)
    target_sign = (lagna_sign + house_num - 1) % 12
    return argala_for_sign(chart, target_sign)


def activated_houses(chart) -> dict:
    """Return houses where net argala is strongest (most positive net_strength)."""
    out = {}
    for h in range(1, 13):
        arg = argala_for_house(chart, h)
        total_net = sum(a["net_strength"] for a in arg.values())
        n_fires = sum(1 for a in arg.values() if a["fires"])
        out[f"H{h}"] = {
            "total_net_argala_strength": total_net,
            "n_argalas_firing":         n_fires,
            "details":                  arg,
        }
    return out


def summary(chart) -> dict:
    activations = activated_houses(chart)
    sorted_houses = sorted(activations.items(),
                            key=lambda kv: -kv[1]["total_net_argala_strength"])
    return {
        "strongest_activated_houses": [
            {"house": h, "net_strength": v["total_net_argala_strength"],
             "n_argalas_firing": v["n_argalas_firing"]}
            for h, v in sorted_houses[:5]
        ],
        "weakest_activated_houses": [
            {"house": h, "net_strength": v["total_net_argala_strength"],
             "n_argalas_firing": v["n_argalas_firing"]}
            for h, v in sorted_houses[-5:]
        ],
        "by_house": activations,
    }
