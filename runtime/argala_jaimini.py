"""Argala — Jaimini concept of intervention/blockage.

Source: Jaimini Sutras (Adhyaya 1, Pada 2 onwards), Sanjay Rath translations.

Argala = "bolt/lock/intervention" — planets in 2nd, 4th, 5th, 8th, 11th from a sign
intervene in matters of that sign.
  - Primary Argalas: from 2H, 4H, 11H (subhha — auspicious)
  - Secondary Argalas: from 5H (good), from 8H (variable), from 12H (Virodha — obstruction)

Virodha Argala = "obstruction Argala" — counter to primary Argalas:
  - 12H from sign blocks 2H Argala
  - 10H from sign blocks 4H Argala
  - 3H from sign blocks 11H Argala
"""
import sys
sys.path.insert(0, ".")

from vedic_core import RASIS  # canonical 12 signs


def compute_argala(chart, target_house=None):
    """Compute Argala on a target sign/house from native's lagna."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    out = {}

    if target_house is None:
        target_houses = list(range(1, 13))
    else:
        target_houses = [target_house]

    for h in target_houses:
        # Sign in this house
        target_sign_idx = (lagna_idx + h - 1) % 12

        # Argala houses (2, 4, 5, 8, 11 from target)
        argala_pos = {
            "2H_Argala_Subha":  (target_sign_idx + 1) % 12,
            "4H_Argala_Subha":  (target_sign_idx + 3) % 12,
            "5H_Argala":        (target_sign_idx + 4) % 12,
            "8H_Argala":        (target_sign_idx + 7) % 12,
            "11H_Argala_Subha": (target_sign_idx + 10) % 12,
        }

        # Virodha Argala houses
        virodha_pos = {
            "12H_Virodha_to_2H":  (target_sign_idx - 1) % 12,
            "10H_Virodha_to_4H":  (target_sign_idx - 3) % 12,
            "3H_Virodha_to_11H":  (target_sign_idx - 11) % 12,
        }

        argala_planets = {}
        for label, sign_idx in argala_pos.items():
            occupants = [p for p, pd in pos.items() if pd["rasi_idx"] == sign_idx]
            argala_planets[label] = {"sign": RASIS[sign_idx], "planets": occupants}

        virodha_planets = {}
        for label, sign_idx in virodha_pos.items():
            occupants = [p for p, pd in pos.items() if pd["rasi_idx"] == sign_idx]
            virodha_planets[label] = {"sign": RASIS[sign_idx], "planets": occupants}

        out[f"H{h}"] = {
            "target_sign": RASIS[target_sign_idx],
            "argala": argala_planets,
            "virodha_argala": virodha_planets,
        }

    return out


def argala_summary(chart):
    """Generate readable Argala summary for key houses."""
    arg = compute_argala(chart)
    lines = ["=== ARGALA ANALYSIS (Jaimini intervention) ==="]

    KEY_HOUSES = {1:"Self",4:"Home",7:"Spouse",10:"Career",11:"Gains"}
    for h, label in KEY_HOUSES.items():
        data = arg[f"H{h}"]
        lines.append(f"\n  H{h} ({label}, sign: {data['target_sign']})")
        for argname, argd in data["argala"].items():
            if argd["planets"]:
                lines.append(f"    [{argname}] in {argd['sign']}: {', '.join(argd['planets'])}")
        # Virodha
        for vname, vd in data["virodha_argala"].items():
            if vd["planets"]:
                lines.append(f"    [{vname}] in {vd['sign']}: {', '.join(vd['planets'])} — obstruction")
    return "\n".join(lines)


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print(argala_summary(chart))
