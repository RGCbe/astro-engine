"""Char Dasha (Jaimini Rasi Dasha) — sign-based dasha system.

Source: Jaimini Sutras Adhyaya 2-3, Sanjay Rath translations.

Char Dasha runs through 12 SIGNS (not planets like Vimshottari).
Each sign-period varies in length (1-12 years) based on the position of its lord.

Calculation:
  - Start with native's lagna sign
  - For each sign in order: count from sign to its lord
  - Subtract 1; if 0, set to 12
  - That's the years for that sign-MD
  - Direction: forward if odd sign, backward if even sign (different schools differ)
"""
import sys, datetime as dt
sys.path.insert(0, ".")

from vedic_core import RASIS, RASI_LORDS  # canonical 12 signs + lords


def char_dasha(chart):
    """Compute Char (Jaimini Rasi) Dasha sequence."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])

    # Order: start at lagna, go forward (some schools)
    order = [(lagna_idx + i) % 12 for i in range(12)]

    timeline = []
    cur_start = birth_dt
    for sign_idx in order:
        sign = RASIS[sign_idx]
        lord = RASI_LORDS[sign]
        if lord not in pos: continue
        lord_sign_idx = pos[lord]["rasi_idx"]
        # Count signs from sign to its lord
        years = ((lord_sign_idx - sign_idx) % 12)
        if years == 0: years = 12
        # Subtract 1 if lord in same sign (debatable)
        if lord_sign_idx == sign_idx: years = 12

        cur_end = cur_start + dt.timedelta(days=years * 365.25)
        timeline.append({
            "sign": sign,
            "sign_idx": sign_idx,
            "lord": lord,
            "lord_position": RASIS[lord_sign_idx],
            "start": cur_start,
            "end": cur_end,
            "years": years,
            "age_from": round((cur_start - birth_dt).days / 365.25, 1),
            "age_to": round((cur_end - birth_dt).days / 365.25, 1),
        })
        cur_start = cur_end
    return timeline


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print(f"=== CHAR DASHA (Jaimini Rasi) for {chart['name']} ===\n")
    for d in char_dasha(chart):
        print(f"  {d['sign']:14s} (lord: {d['lord']} in {d['lord_position']}) {d['years']:2d}y | {d['start'].strftime('%Y-%m')} → {d['end'].strftime('%Y-%m')} | ages {d['age_from']:.0f}-{d['age_to']:.0f}")
