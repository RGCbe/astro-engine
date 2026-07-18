"""Sahams — 28+ sensitive points used in Tajik (Annual chart) astrology.

Source: Tajika Neelakanthi, Yavan Jataka.
Each Saham is a calculated longitude indicating a specific life theme.
Major Sahams:
  - Punya (merit) — Moon - Sun + Lagna
  - Vidya (learning) — Moon + Mercury - Sun
  - Yasas (fame) — Mars + Jupiter - Saturn
  - Karya (action) — Saturn - Mars + Lagna
  - Bandhu (relations) — Mercury + Moon - Saturn
  - Mrityu (death) — 8th cusp + Moon - Saturn
  - Vivaha (marriage) — Venus - Sun + Lagna
  - Putra (children) — Jupiter - Sun + Lagna
  - Bhratru (siblings) — Mars + Mercury - Saturn
  - Pitru (father) — Sun + Saturn - Mercury
  - Matru (mother) — Moon + Saturn - Mars
  - Roga (disease) — Saturn - Sun + Lagna
  - Shatru (enemies) — Sun + Mars - Saturn
  - Karma (career) — Mercury + Saturn - Mars (or 10th + Moon - Sun)
  - And many more...
"""
import sys
sys.path.insert(0, ".")

from vedic_core import RASIS, RASI_LORDS  # canonical 12 signs + lords


def _lon(pos, p):
    """Get absolute longitude of planet."""
    return pos[p].get("lon_abs") or (pos[p]["rasi_idx"] * 30 + pos[p]["deg"])


def _normalize(lon):
    """Normalize to 0-360°."""
    return lon % 360


def compute_sahams(chart):
    """Compute all major Sahams. Each Saham returns longitude + sign + house."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    lagna_lon = lagna_idx * 30  # using sign-cusp approximation

    if not all(p in pos for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]):
        return {}

    sun = _lon(pos, "Sun"); moon = _lon(pos, "Moon")
    mars = _lon(pos, "Mars"); merc = _lon(pos, "Mercury")
    jup = _lon(pos, "Jupiter"); ven = _lon(pos, "Venus")
    sat = _lon(pos, "Saturn")
    asc = lagna_lon

    SAHAMS_FORMULAS = {
        "Punya (merit)":          (moon - sun + asc),
        "Vidya (learning)":       (moon + merc - sun),
        "Yasas (fame)":           (mars + jup - sat),
        "Karya (action)":         (sat - mars + asc),
        "Bandhu (relations)":     (merc + moon - sat),
        "Mrityu (death-time)":    (asc + moon - sat),
        "Vivaha (marriage)":      (ven - sun + asc),
        "Putra (children)":       (jup - sun + asc),
        "Bhratru (siblings)":     (mars + merc - sat),
        "Pitru (father)":         (sun + sat - merc),
        "Matru (mother)":         (moon + sat - mars),
        "Roga (disease)":         (sat - sun + asc),
        "Shatru (enemies)":       (sun + mars - sat),
        "Karma (career)":         (merc + sat - mars),
        "Artha (wealth)":         (jup + ven + sun),
        "Saha (assistant)":       (jup - sat + asc),
        "Gaurava (honor)":        (jup + sun + sat),
        "Vyapara (business)":     (ven + sat - mars),
        "Jnana (wisdom)":         (jup - asc + moon),
        "Daya (compassion)":      (ven + jup - moon),
        "Krodha (anger)":         (mars - sat + asc),
        "Lutha (theft-risk)":     (sat - mars + sun),
        "Bhagya (fortune)":       (jup + sat - sun),
        "Vaibhava (prosperity)":  (jup - moon + asc),
        "Pravasa (foreign)":      (asc + 12*30 - sat),  # 12th from lagna lord etc.
        "Yatra (travel)":         (sat - moon + asc),
        "Shubha (auspicious)":    (asc + jup - sat),
        "Ashubha (inauspicious)": (asc + sat - jup),
    }

    out = {}
    for name, lon in SAHAMS_FORMULAS.items():
        l = _normalize(lon)
        ri = int(l / 30)
        deg = l - ri * 30
        h_from_lagna = ((ri - lagna_idx) % 12) + 1
        out[name] = {
            "lon": round(l, 2),
            "sign": RASIS[ri],
            "deg": round(deg, 2),
            "house": h_from_lagna,
            "lord": RASI_LORDS[RASIS[ri]],
        }
    return out


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    s = compute_sahams(chart)
    print(f"=== SAHAMS for {chart['name']} ===\n")
    print(f"{'Saham':<25}{'Sign':<13}{'Deg':<7}{'House':<7}{'Lord'}")
    for name, data in s.items():
        print(f"  {name:<25}{data['sign']:<13}{data['deg']:<7.2f}H{data['house']:<6}{data['lord']}")
