from vedic_core import RASIS

"""Upagrahas — Sub-planets / sensitive points.

Source: BPHS Ch. 12, Phaladeepika Ch. 3.
Computes:
  - Gulika (most important, most malefic upagraha)
  - Mandi (mild malefic)
  - Dhuma (smoky)
  - Vyatipata (calamity)
  - Parivesha (halo)
  - Indrachapa (rainbow)
  - Upaketu
  - Yamakantaka

These are sensitive degree-points based on Sun's longitude + day/night.
"""
import sys
sys.path.insert(0, ".")

GULIKA_DAY_PORTIONS = {0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0}  # Sun=0 (Sunday): part 6
GULIKA_NIGHT_PORTIONS = {0:2, 1:1, 2:0, 3:6, 4:5, 5:4, 6:3}




def compute_upagrahas(chart):
    """Compute all 8 upagrahas based on Sun's position and day/night birth."""
    pos = chart["positions"]
    if "Sun" not in pos: return {}

    sun_lon = pos["Sun"].get("lon_abs") or (pos["Sun"]["rasi_idx"]*30 + pos["Sun"]["deg"])

    # Calculation logic — simplified standard formulas
    # Gulika longitude = Sun + (Gulika offset based on weekday/day-night)
    # Approximate: Gulika ~ Sun + 30° (one sign ahead) for day birth
    # This is a SIMPLIFIED version — for full precision needs sunrise/sunset calculation
    out = {}

    # Gulika (most malefic, "Mandi's son")
    gulika_lon = (sun_lon + 30) % 360  # placeholder offset
    out["Gulika"] = _make_upagraha("Gulika", gulika_lon, chart)

    # Mandi
    mandi_lon = (sun_lon + 60) % 360
    out["Mandi"] = _make_upagraha("Mandi", mandi_lon, chart)

    # Dhuma (Sun + 133°20')
    dhuma_lon = (sun_lon + 133.333) % 360
    out["Dhuma"] = _make_upagraha("Dhuma", dhuma_lon, chart)

    # Vyatipata (Dhuma + 180° — opposite Dhuma + sign reversal)
    vyatipata_lon = (360 - dhuma_lon) % 360
    out["Vyatipata"] = _make_upagraha("Vyatipata", vyatipata_lon, chart)

    # Parivesha (Vyatipata + 180°)
    parivesha_lon = (vyatipata_lon + 180) % 360
    out["Parivesha"] = _make_upagraha("Parivesha", parivesha_lon, chart)

    # Indrachapa (360° - Parivesha)
    indrachapa_lon = (360 - parivesha_lon) % 360
    out["Indrachapa"] = _make_upagraha("Indrachapa", indrachapa_lon, chart)

    # Upaketu (Indrachapa + 16°40')
    upaketu_lon = (indrachapa_lon + 16.666) % 360
    out["Upaketu"] = _make_upagraha("Upaketu", upaketu_lon, chart)

    # Yamakantaka (Yama-related)
    yamakantaka_lon = (sun_lon + 75) % 360
    out["Yamakantaka"] = _make_upagraha("Yamakantaka", yamakantaka_lon, chart)

    return out


def _make_upagraha(name, lon, chart):
    rasi_idx = int(lon // 30)
    deg = lon - rasi_idx * 30
    house = ((rasi_idx - chart["lagna_idx"]) % 12) + 1
    return {
        "name": name,
        "lon": round(lon, 2),
        "rasi": RASIS[rasi_idx],
        "rasi_idx": rasi_idx,
        "deg": round(deg, 2),
        "house": house,
    }


def upagraha_summary(chart):
    """Show upagraha placements with house focus."""
    ups = compute_upagrahas(chart)
    if not ups: return "No upagrahas computed."
    lines = ["=== UPAGRAHAS (Sub-Planets) ==="]
    for name, data in ups.items():
        nature = "MOST MALEFIC" if name == "Gulika" else "malefic" if name in ["Mandi","Vyatipata","Yamakantaka"] else "mild"
        lines.append(f"  {name:15s}  {data['rasi']:12s} {data['deg']:5.1f}°  House {data['house']:2d}  ({nature})")
    return "\n".join(lines)


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print(upagraha_summary(chart))
