"""Numerology relationship tools — compatibility (marriage/partnership matching)
and a name advisor. Reuses the Cheiro friendship matrix from tamil_numerology so
results stay consistent with the rest of the numerology engine.
"""
from __future__ import annotations
import datetime as dt

from engine.tamil_numerology import (
    PLANET_FRIENDS_BY_NUM, PLANET_ENEMIES_BY_NUM, NUM_PLANET,
    _digit_root, _vidhi_number, _bhagya_number,
)

# Chaldean letter values — used for the name-number (traditional "name luck").
_CHALDEAN = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1, "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3, "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5, "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7, "F": 8, "P": 8,
}
_REL_POINTS = {"same": 2, "friend": 2, "neutral": 1, "enemy": 0}


def _parse_date(date_str: str) -> dt.date:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d", "%d.%m.%Y"):
        try:
            return dt.datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date format: {date_str!r} (use YYYY-MM-DD)")


def _chaldean_number(name: str) -> tuple[int, int]:
    total = sum(_CHALDEAN.get(c, 0) for c in name.upper() if c.isalpha())
    return (_digit_root(total) if total else 0), total


def number_relation(a: int, b: int) -> str:
    """How number b sits relative to a: same / friend / neutral / enemy."""
    if a == b:
        return "same"
    if b in PLANET_FRIENDS_BY_NUM.get(a, []):
        return "friend"
    if b in PLANET_ENEMIES_BY_NUM.get(a, []):
        return "enemy"
    return "neutral"


def compute_compatibility(name1: str, date1: str, name2: str, date2: str) -> dict:
    """Numerology compatibility (marriage / partnership) between two people,
    scored on both the Driver (Vidhi) and Destiny (Bhagya) numbers, both ways."""
    d1, d2 = _parse_date(date1), _parse_date(date2)
    v1, b1 = _vidhi_number(d1), _bhagya_number(d1)
    v2, b2 = _vidhi_number(d2), _bhagya_number(d2)

    def _pair(a: int, b: int) -> dict:
        r1, r2 = number_relation(a, b), number_relation(b, a)
        return {"a_to_b": r1, "b_to_a": r2, "points": _REL_POINTS[r1] + _REL_POINTS[r2]}

    driver = _pair(v1, v2)
    destiny = _pair(b1, b2)
    pct = round((driver["points"] + destiny["points"]) / 8 * 100)   # 0..8 -> %
    if pct >= 80:
        verdict, advice = "Excellent match", "Naturally harmonious — strong long-term bond."
    elif pct >= 62:
        verdict, advice = "Good match", "Compatible; small differences are easy to handle."
    elif pct >= 44:
        verdict, advice = "Workable — needs effort", "Can work with understanding and patience."
    else:
        verdict, advice = "Challenging", "Real friction points — needs maturity / remedies."
    return {
        "person1": {"name": name1, "driver": v1, "driver_planet": NUM_PLANET[v1],
                    "destiny": b1, "destiny_planet": NUM_PLANET[b1]},
        "person2": {"name": name2, "driver": v2, "driver_planet": NUM_PLANET[v2],
                    "destiny": b2, "destiny_planet": NUM_PLANET[b2]},
        "driver_relation": driver,
        "destiny_relation": destiny,
        "score_percent": pct,
        "verdict": verdict,
        "advice": advice,
    }


def name_advisor(proposed_name: str, date: str) -> dict:
    """Score how lucky a proposed name's number is for a person's birth numbers
    (generalises the Vijay film-name method to people / businesses / brands)."""
    d = _parse_date(date)
    v, b = _vidhi_number(d), _bhagya_number(d)
    n_num, n_total = _chaldean_number(proposed_name)
    vs_driver = number_relation(v, n_num)
    vs_destiny = number_relation(b, n_num)
    good = sum(1 for r in (vs_driver, vs_destiny) if r in ("friend", "same"))
    bad = sum(1 for r in (vs_driver, vs_destiny) if r == "enemy")
    if good == 2:
        verdict = "Very lucky name for this person"
    elif good >= 1 and bad == 0:
        verdict = "Lucky / supportive name"
    elif bad == 2:
        verdict = "Unlucky name — better to change/adjust it"
    elif bad == 1:
        verdict = "Mixed — one clash; a small tweak helps"
    else:
        verdict = "Neutral name"
    return {
        "proposed_name": proposed_name,
        "name_number": n_num,
        "name_planet": NUM_PLANET.get(n_num, "?"),
        "raw_total": n_total,
        "birth_driver": v,
        "birth_destiny": b,
        "vs_driver": vs_driver,
        "vs_destiny": vs_destiny,
        "verdict": verdict,
    }


if __name__ == "__main__":
    import sys, json
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== COMPATIBILITY: Manoj Kumar (1996-05-25) x Priya (1998-08-14) ===")
    print(json.dumps(compute_compatibility("Manoj Kumar", "1996-05-25", "Priya", "1998-08-14"), indent=1))
    print("\n=== NAME ADVISOR for Manoj (driver 7 / destiny 1) ===")
    for nm in ["Manoj Kumar", "Vijay", "Surya", "Karthik", "Arjun"]:
        r = name_advisor(nm, "1996-05-25")
        print(f"  {nm:14s} -> number {r['name_number']} ({r['name_planet']}), "
              f"vs-driver {r['vs_driver']}, vs-destiny {r['vs_destiny']}  =>  {r['verdict']}")
