"""Vedic Numerology — Mulanka, Bhagyanka, Lo Shu Grid.

Source: Lal Kitab numerology, Cheiro/Sepharial Vedic adaptations.
"""
import sys
sys.path.insert(0, ".")

PLANET_BY_NUMBER = {1:"Sun",2:"Moon",3:"Jupiter",4:"Rahu",5:"Mercury",6:"Venus",7:"Ketu",8:"Saturn",9:"Mars"}


def mulanka(birth_day):
    """Mulanka (Driver Number) — sum of birth day digits, reduced to 1-9."""
    n = birth_day
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def bhagyanka(birth_day, birth_month, birth_year):
    """Bhagyanka (Destiny Number) — sum of full birth date, reduced to 1-9."""
    full = f"{birth_day}{birth_month:02d}{birth_year}"
    n = sum(int(d) for d in full)
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def name_number(name):
    """Name number — Chaldean letter-to-number sum."""
    CHALDEAN = {
        "A":1,"I":1,"J":1,"Q":1,"Y":1,
        "B":2,"K":2,"R":2,
        "C":3,"G":3,"L":3,"S":3,
        "D":4,"M":4,"T":4,
        "E":5,"H":5,"N":5,"X":5,
        "U":6,"V":6,"W":6,
        "O":7,"Z":7,
        "F":8,"P":8,
    }
    total = sum(CHALDEAN.get(c.upper(), 0) for c in name if c.isalpha())
    while total > 9:
        total = sum(int(d) for d in str(total))
    return total


def vedic_numerology(chart):
    b = chart["birth"]
    m = mulanka(b["day"])
    bg = bhagyanka(b["day"], b["month"], b["year"])
    n = name_number(chart["name"])
    NUMBER_TRAITS = {
        1: "Sun — leader, ambitious, authoritative, ego-strong",
        2: "Moon — sensitive, emotional, nurturing, mood-driven",
        3: "Jupiter — wisdom, dharma, expansion, optimistic teacher",
        4: "Rahu — unconventional, foreign, scientific, restless",
        5: "Mercury — clever, communicative, quick-thinking, witty",
        6: "Venus — beauty, harmony, art, comfort, romantic",
        7: "Ketu — spiritual, mystical, introspective, occult",
        8: "Saturn — disciplined, hard-working, late bloomer, karmic",
        9: "Mars — courageous, energetic, warrior, leadership through action",
    }
    return {
        "mulanka": m,
        "mulanka_planet": PLANET_BY_NUMBER[m],
        "mulanka_traits": NUMBER_TRAITS[m],
        "bhagyanka": bg,
        "bhagyanka_planet": PLANET_BY_NUMBER[bg],
        "bhagyanka_traits": NUMBER_TRAITS[bg],
        "name_number": n,
        "name_planet": PLANET_BY_NUMBER[n],
        "name_traits": NUMBER_TRAITS[n],
        "lucky_dates": [d for d in range(1,32) if d % 9 == m % 9 or d % 9 == bg % 9],
        "lucky_days": [["Sun","Mon","Tue","Wed","Thu","Fri","Sat"][["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"].index(PLANET_BY_NUMBER[m])] if PLANET_BY_NUMBER[m] in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"] else "Sun"],
        "lucky_color": _lucky_color(PLANET_BY_NUMBER[m]),
        "lucky_gemstone": _lucky_gem(PLANET_BY_NUMBER[m]),
    }


def _lucky_color(planet):
    return {"Sun":"orange/gold","Moon":"white/silver","Mars":"red","Mercury":"green",
            "Jupiter":"yellow","Venus":"white/pastel","Saturn":"black/blue",
            "Rahu":"smoke-grey","Ketu":"multicolored"}.get(planet, "neutral")


def _lucky_gem(planet):
    return {"Sun":"Ruby (Manik)","Moon":"Pearl (Moti)","Mars":"Red Coral (Moonga)","Mercury":"Emerald (Panna)",
            "Jupiter":"Yellow Sapphire (Pukhraj)","Venus":"Diamond / White Sapphire","Saturn":"Blue Sapphire (Neelam)",
            "Rahu":"Hessonite (Gomedha)","Ketu":"Cat's Eye (Lehsuniya)"}.get(planet, "?")


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    n = vedic_numerology(chart)
    print(f"=== VEDIC NUMEROLOGY for {chart['name']} ===\n")
    print(f"  MULANKA (Driver):  {n['mulanka']} ({n['mulanka_planet']})")
    print(f"    {n['mulanka_traits']}")
    print(f"  BHAGYANKA (Destiny): {n['bhagyanka']} ({n['bhagyanka_planet']})")
    print(f"    {n['bhagyanka_traits']}")
    print(f"  NAME NUMBER:       {n['name_number']} ({n['name_planet']})")
    print(f"    {n['name_traits']}")
    print(f"\n  LUCKY DATES:    {n['lucky_dates']}")
    print(f"  LUCKY COLOR:    {n['lucky_color']}")
    print(f"  LUCKY GEMSTONE: {n['lucky_gemstone']}")
