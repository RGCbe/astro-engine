"""Extra Divisional Charts — D2, D3, D4, D7, D12, D16, D20, D24, D27, D30, D40, D45.

Combined with existing D9/D10/D60 in divisional_charts.py, this gives full Shodashvarga.

Each varga formula from BPHS Ch. 6 (Shodashavarga).
"""
import sys
sys.path.insert(0, ".")
from divisional_charts import build_divisional_chart, RASIS, RASI_LORDS

# Shodashvarga purposes (Phaladeepika Ch. 5)
VARGA_PURPOSE = {
    "D1":  ("Rasi", "body, general life"),
    "D2":  ("Hora", "wealth, money, family lineage"),
    "D3":  ("Drekkana", "siblings, courage, communication"),
    "D4":  ("Chaturthamsa", "fortune, fixed assets, mother"),
    "D7":  ("Saptamsa", "children, progeny"),
    "D9":  ("Navamsa", "marriage, dharma, hidden strength"),
    "D10": ("Dashamsa", "career, profession, fame"),
    "D12": ("Dwadashamsa", "parents (lineage)"),
    "D16": ("Shodashamsa", "vehicles, comforts, accidents"),
    "D20": ("Vimshamsa", "spiritual progress, worship"),
    "D24": ("Chaturvimshamsa", "education, learning, knowledge"),
    "D27": ("Bhamsa/Saptavimshamsa", "physical strength, weakness"),
    "D30": ("Trimshamsa", "evils, misfortunes, defects"),
    "D40": ("Khavedamsa", "auspicious, inauspicious effects"),
    "D45": ("Akshavedamsa", "general final results"),
    "D60": ("Shashtiamsa", "past-life karma, finest detail"),
}


def _hora_d2(sign_idx, deg_in_sign):
    """D2 Hora — split each sign into 2 halves of 15°.
    Odd signs: first half = Sun (Leo idx=4), second half = Moon (Cancer idx=3)
    Even signs: first half = Moon, second half = Sun"""
    if sign_idx % 2 == 0:  # odd sign
        return 4 if deg_in_sign < 15 else 3  # Leo or Cancer
    else:
        return 3 if deg_in_sign < 15 else 4


def _drekkana_d3(sign_idx, deg_in_sign):
    """D3 — sign / 3 = 10° parts. Each part = same sign, 5th sign, 9th sign."""
    part = int(deg_in_sign / 10)
    return (sign_idx + part * 4) % 12


def _chaturthamsa_d4(sign_idx, deg_in_sign):
    """D4 — sign / 4 = 7.5° parts. Each part = lagna of 1st/4th/7th/10th from sign."""
    part = int(deg_in_sign / 7.5)
    return (sign_idx + part * 3) % 12


def _saptamsa_d7(sign_idx, deg_in_sign):
    """D7 — sign / 7 = 4°17.14' parts.
    Odd signs: start at same sign. Even signs: start at 7th from sign."""
    part = int(deg_in_sign / (30/7))
    if sign_idx % 2 == 0:
        return (sign_idx + part) % 12
    else:
        return (sign_idx + 6 + part) % 12


def _shodashamsa_d16(sign_idx, deg_in_sign):
    """D16 — sign / 16 = 1°52.5' parts."""
    part = int(deg_in_sign / (30/16))
    if sign_idx in [0, 3, 6, 9]:  # movable
        start = 0  # Aries
    elif sign_idx in [1, 4, 7, 10]:  # fixed
        start = 4  # Leo
    else:  # dual
        start = 8  # Sagittarius
    return (start + part) % 12


def _vimshamsa_d20(sign_idx, deg_in_sign):
    """D20 — sign / 20 = 1°30' parts."""
    part = int(deg_in_sign / 1.5)
    if sign_idx in [0, 3, 6, 9]:
        start = 0
    elif sign_idx in [1, 4, 7, 10]:
        start = 8
    else:
        start = 4
    return (start + part) % 12


def _chaturvimshamsa_d24(sign_idx, deg_in_sign):
    """D24 — sign / 24 = 1°15' parts."""
    part = int(deg_in_sign / 1.25)
    if sign_idx % 2 == 0:
        start = 4  # Leo for odd
    else:
        start = 3  # Cancer for even
    return (start + part) % 12


def _saptavimshamsa_d27(sign_idx, deg_in_sign):
    """D27 — sign / 27 = 1°6.67' parts (Nakshatra-amsha)."""
    part = int(deg_in_sign / (30/27))
    sign_type = sign_idx % 4
    starts = [0, 3, 6, 9]  # Aries, Cancer, Libra, Capricorn for fire/earth/air/water
    return (starts[sign_type] + part) % 12


def _trimshamsa_d30(sign_idx, deg_in_sign):
    """D30 — sign / 30 unevenly: Mars 5°, Saturn 5°, Jupiter 8°, Mercury 7°, Venus 5°.
    For odd signs: order Mars/Saturn/Jupiter/Mercury/Venus.
    For even signs: order Venus/Mercury/Jupiter/Saturn/Mars."""
    if sign_idx % 2 == 0:  # odd
        if deg_in_sign < 5:    return 0   # Aries (Mars)
        elif deg_in_sign < 10: return 10  # Aquarius (Saturn)
        elif deg_in_sign < 18: return 8   # Sagittarius (Jupiter)
        elif deg_in_sign < 25: return 5   # Virgo (Mercury)
        else:                  return 6   # Libra (Venus)
    else:  # even
        if deg_in_sign < 5:    return 1   # Taurus (Venus)
        elif deg_in_sign < 12: return 5   # Virgo (Mercury)
        elif deg_in_sign < 20: return 11  # Pisces (Jupiter)
        elif deg_in_sign < 25: return 9   # Capricorn (Saturn)
        else:                  return 7   # Scorpio (Mars)


def _khavedamsa_d40(sign_idx, deg_in_sign):
    """D40 — sign / 40 = 0°45' parts."""
    part = int(deg_in_sign / 0.75)
    if sign_idx % 2 == 0:  # odd
        start = 0  # Aries
    else:
        start = 6  # Libra
    return (start + part) % 12


def _akshavedamsa_d45(sign_idx, deg_in_sign):
    """D45 — sign / 45 = 0°40' parts."""
    part = int(deg_in_sign / (30/45))
    if sign_idx in [0, 3, 6, 9]:
        start = 0
    elif sign_idx in [1, 4, 7, 10]:
        start = 4
    else:
        start = 8
    return (start + part) % 12


# Register varga functions
EXTRA_VARGA_FNS = {
    "D2":  _hora_d2,
    "D3":  _drekkana_d3,
    "D4":  _chaturthamsa_d4,
    "D7":  _saptamsa_d7,
    "D16": _shodashamsa_d16,
    "D20": _vimshamsa_d20,
    "D24": _chaturvimshamsa_d24,
    "D27": _saptavimshamsa_d27,
    "D30": _trimshamsa_d30,
    "D40": _khavedamsa_d40,
    "D45": _akshavedamsa_d45,
}


def build_extra_varga(natal_chart, varga):
    """Build a non-standard varga chart using the extended formulas."""
    if varga in EXTRA_VARGA_FNS:
        # Patch the divisional_charts module's INDEX_FN by manually building
        natal_pos = natal_chart["positions"]
        natal_lagna_idx = natal_chart["lagna_idx"]
        fn = EXTRA_VARGA_FNS[varga]
        new_lagna_idx = fn(natal_lagna_idx, 15.0)  # midpoint approx
        new_positions = {}
        for p, pd in natal_pos.items():
            new_sign_idx = fn(pd["rasi_idx"], pd["deg"])
            new_house = ((new_sign_idx - new_lagna_idx) % 12) + 1
            new_positions[p] = {
                "rasi_idx": new_sign_idx,
                "rasi": RASIS[new_sign_idx],
                "house": new_house,
                "deg": pd["deg"],
                "nak": pd.get("nak"),
                "nak_lord": pd.get("nak_lord"),
                "pada": pd.get("pada"),
            }
        return {
            "name": f"{natal_chart['name']} — {varga}",
            "lagna": RASIS[new_lagna_idx],
            "lagna_idx": new_lagna_idx,
            "lagna_lord": RASI_LORDS[RASIS[new_lagna_idx]],
            "positions": new_positions,
            "_varga": varga,
            "_purpose": VARGA_PURPOSE.get(varga, ("?", "?"))[1],
        }
    else:
        # Use existing D9/D10/D12/D60 from divisional_charts
        return build_divisional_chart(natal_chart, varga)


def all_vargas_summary(natal_chart):
    """Compute all 16 vargas, return placement summary."""
    out = {}
    for v in ["D1","D2","D3","D4","D7","D9","D10","D12","D16","D20","D24","D27","D30","D40","D45","D60"]:
        if v == "D1":
            out[v] = {"name":"Rasi","lagna":natal_chart["lagna"],"purpose":VARGA_PURPOSE["D1"][1]}
            continue
        try:
            c = build_extra_varga(natal_chart, v) if v in EXTRA_VARGA_FNS else build_divisional_chart(natal_chart, v)
            out[v] = {
                "name": VARGA_PURPOSE[v][0],
                "lagna": c["lagna"],
                "lagna_lord": c.get("lagna_lord","?"),
                "purpose": VARGA_PURPOSE[v][1],
            }
        except Exception as e:
            out[v] = {"error": str(e)}
    return out


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    summary = all_vargas_summary(chart)
    print(f"=== ALL 16 VARGAS FOR {chart['name']} ===")
    print(f"{'Varga':<7}{'Name':<22}{'Lagna':<14}{'Lord':<10}{'Purpose'}")
    for v, data in summary.items():
        if "error" in data:
            print(f"  {v}: ERROR {data['error']}")
        else:
            print(f"  {v:<5}{data['name']:<22}{data['lagna']:<14}{data.get('lagna_lord','-'):<10}{data['purpose']}")
