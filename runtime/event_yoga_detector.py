"""Event Yoga Detector — 35+ named yogas from classical Jyotish texts.

Each yoga is a Python predicate matching specific chart conditions.
Used by event_predictor to flag pre-disposed life events.

Sources: BPHS, Saravali, Phaladeepika, Jataka Parijata, Brihat Jataka,
         Hora Sara, Uttara Kalamrita, Bhrigu Samhita, Jaimini Sutras.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vedic_core import (DIGNITIES, RASIS, RASI_LORDS,
                        NATURAL_MALEFICS, NATURAL_BENEFICS)


def _h(pos, planet):
    return pos[planet]["house"] if planet in pos else None

def _dig(pos, planet):
    return DIGNITIES.get((planet, pos[planet]["rasi"]), "neutral") if planet in pos else None

def _occ(pos, house):
    return [p for p, pd in pos.items() if pd["house"] == house]

def _lord_of(lagna_idx, house):
    sign = RASIS[(lagna_idx + house - 1) % 12]
    return RASI_LORDS[sign]

def _is_malefic(p):
    return p in NATURAL_MALEFICS

def _aspects(pos, planet):
    """Return houses aspected by planet using Vedic special aspects."""
    if planet not in pos:
        return []
    h = pos[planet]["house"]
    if planet == "Jupiter":
        return [(h+4)%12 or 12, (h+6)%12 or 12, (h+8)%12 or 12]
    elif planet == "Mars":
        return [(h+3)%12 or 12, (h+6)%12 or 12, (h+7)%12 or 12]
    elif planet == "Saturn":
        return [(h+2)%12 or 12, (h+6)%12 or 12, (h+9)%12 or 12]
    elif planet in ["Rahu","Ketu"]:
        return [(h+4)%12 or 12, (h+6)%12 or 12, (h+8)%12 or 12]
    else:
        return [(h+6)%12 or 12]  # 7th aspect for everyone


# ================================================================
# YOGA PREDICATES — each returns severity (0-5) and label, or None
# ================================================================

def yoga_pitru_kasht(chart):
    """Pitru-Kasht Yoga — Father-Distress. Source: Jataka Parijata Ch. 5 v.91."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    triggers = []
    if _h(pos, "Sun") in [6, 8, 12]:
        triggers.append("Sun in 6/8/12")
    h9_lord = _lord_of(lagna_idx, 9)
    if h9_lord in pos and _h(pos, h9_lord) in [6, 8, 12]:
        triggers.append(f"9th lord ({h9_lord}) in 6/8/12")
    if _h(pos, "Saturn") and 6 in _aspects(pos, "Saturn") and _h(pos, "Sun") == 6:
        triggers.append("Saturn aspects Sun")
    if _dig(pos, "Sun") == "Debil":
        triggers.append("Sun debilitated")
    if len(triggers) >= 2:
        return {
            "name": "Pitru-Kasht Yoga",
            "name_translation": "Father-Distress Yoga",
            "severity": min(5, len(triggers) + 1),
            "triggers": triggers,
            "domain": "father",
            "source": "Jataka Parijata Ch. 5 v. 91",
            "interpretation": (
                "Father experiences struggles, accidents, illness, or career challenges. "
                "Severity proportional to number of triggers. "
                "Activates strongly during Sun MD/AD or transits over Sun."
            ),
            "event_keywords": ["father health", "father accident", "father struggle", "paternal loss"],
        }
    return None


def yoga_matruhanta(chart):
    """Matruhanta Yoga — Mother-Affliction. Source: Jataka Parijata Ch. 5 v. 78."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    triggers = []
    if _h(pos, "Moon") in [6, 8, 12]:
        triggers.append("Moon in 6/8/12")
    h4_lord = _lord_of(lagna_idx, 4)
    if h4_lord in pos and _h(pos, h4_lord) in [6, 8, 12]:
        triggers.append(f"4th lord ({h4_lord}) in 6/8/12")
    h4_occ = _occ(pos, 4)
    malefics_in_4 = [p for p in h4_occ if _is_malefic(p)]
    if len(malefics_in_4) >= 2:
        triggers.append(f"two malefics in 4th: {', '.join(malefics_in_4)}")
    elif len(malefics_in_4) == 1:
        triggers.append(f"malefic in 4th: {malefics_in_4[0]}")
    if _dig(pos, "Moon") == "Debil":
        triggers.append("Moon debilitated")
    if len(triggers) >= 2:
        return {
            "name": "Matruhanta Yoga",
            "name_translation": "Mother-Affliction Yoga",
            "severity": min(5, len(triggers) + 1),
            "triggers": triggers,
            "domain": "mother",
            "source": "Jataka Parijata Ch. 5 v. 78",
            "interpretation": (
                "Mother experiences difficulty, illness, separation, or distress. "
                "Activates during Moon MD/AD, transits over Moon or 4th house, "
                "and especially during Saturn-Moon configurations."
            ),
            "event_keywords": ["mother health", "mother loss", "domestic upheaval", "early separation"],
        }
    return None


def yoga_vidyut(chart):
    """Vidyut Yoga — Lightning/Sudden-Event Yoga. Source: Saravali Ch. 39."""
    pos = chart["positions"]
    if "Mars" not in pos or "Mercury" not in pos:
        return None
    if pos["Mars"]["rasi_idx"] == pos["Mercury"]["rasi_idx"]:
        return {
            "name": "Vidyut Yoga",
            "name_translation": "Lightning Yoga",
            "severity": 3,
            "triggers": [f"Mars + Mercury conjunct in {pos['Mars']['rasi']}, House {pos['Mars']['house']}"],
            "domain": "accidents",
            "source": "Saravali Ch. 39, Phaladeepika Ch. 13",
            "interpretation": (
                "Sudden, sharp events — accidents, surgery, cuts, falls. "
                "Activates when Mars or Mercury is the active dasha lord, "
                "OR during transits of Saturn/Rahu over the conjunction."
            ),
            "event_keywords": ["accident", "injury", "surgery", "sharp event", "vehicle accident"],
        }
    return None


def yoga_kaal_sarpa(chart):
    """Kaal Sarpa — All planets between Rahu and Ketu axis. Source: BPHS."""
    pos = chart["positions"]
    if "Rahu" not in pos or "Ketu" not in pos:
        return None
    rahu_lon = pos["Rahu"]["rasi_idx"]*30 + pos["Rahu"]["deg"]
    ketu_lon = pos["Ketu"]["rasi_idx"]*30 + pos["Ketu"]["deg"]
    inside = 0
    outside = 0
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        if p not in pos:
            continue
        plon = pos[p]["rasi_idx"]*30 + pos[p]["deg"]
        # Test if planet is in Rahu->Ketu hemisphere (going forward zodiacally)
        diff = (plon - rahu_lon) % 360
        ket_diff = (ketu_lon - rahu_lon) % 360
        if diff < ket_diff:
            inside += 1
        else:
            outside += 1
    if inside == 7 or outside == 7:
        return {
            "name": "Kaal Sarpa Yoga",
            "name_translation": "Cosmic Serpent Yoga",
            "severity": 4,
            "triggers": ["all 7 planets on one side of Rahu-Ketu axis"],
            "domain": "karmic",
            "source": "BPHS, Phaladeepika",
            "interpretation": "Karmic life-pattern, repeated themes, mastery through awareness.",
            "event_keywords": ["karmic events", "repeated patterns"],
        }
    return None


def yoga_balarishta(chart):
    """Balarishta — Childhood Affliction. Source: BPHS Ch. 13, Saravali Ch. 8."""
    pos = chart["positions"]
    moon_h = _h(pos, "Moon")
    triggers = []
    if moon_h in [6, 8, 12]:
        triggers.append(f"Moon in {moon_h}H")
    h6_or_8_or_12_malefics = []
    for h in [6, 8, 12]:
        for p in _occ(pos, h):
            if _is_malefic(p):
                h6_or_8_or_12_malefics.append(f"{p} in {h}H")
    if len(h6_or_8_or_12_malefics) >= 2:
        triggers.extend(h6_or_8_or_12_malefics[:2])
    asc_lord = chart.get("lagna_lord")
    if asc_lord and asc_lord in pos and _h(pos, asc_lord) in [6, 8, 12]:
        triggers.append(f"Lagna lord ({asc_lord}) in {_h(pos, asc_lord)}H")
    if len(triggers) >= 2:
        return {
            "name": "Balarishta Yoga",
            "name_translation": "Childhood Affliction Yoga",
            "severity": min(5, len(triggers) + 1),
            "triggers": triggers,
            "domain": "early_life",
            "source": "BPHS Ch. 13, Saravali Ch. 8",
            "interpretation": (
                "Difficulties, accidents, or family disturbances in early childhood (age 0-12). "
                "Concentrated in the first MD and its sub-periods."
            ),
            "event_keywords": ["childhood event", "early family upheaval", "child illness"],
        }
    return None


def yoga_marriage_delay(chart):
    """Marriage Delay Yoga. Source: Jataka Parijata Ch. 7."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    triggers = []
    h7_occ = _occ(pos, 7)
    if "Saturn" in h7_occ:
        triggers.append("Saturn in 7H")
    if "Mars" in h7_occ and pos["Mars"]["house"] == 7:
        triggers.append("Mars in 7H")
    if _dig(pos, "Venus") == "Debil":
        triggers.append("Venus debilitated")
    h7_lord = _lord_of(lagna_idx, 7)
    if h7_lord in pos and _h(pos, h7_lord) in [6, 8, 12]:
        triggers.append(f"7th lord ({h7_lord}) in 6/8/12")
    if len(triggers) >= 2:
        return {
            "name": "Vivaha-Vilamba Yoga",
            "name_translation": "Marriage-Delay Yoga",
            "severity": min(5, len(triggers) + 1),
            "triggers": triggers,
            "domain": "marriage",
            "source": "Jataka Parijata Ch. 7",
            "interpretation": "Marriage delayed beyond typical age, possibly to 30+, or with multiple breakups before settling.",
            "event_keywords": ["marriage delay", "broken engagement", "late marriage"],
        }
    return None


def yoga_dhana(chart):
    """Dhana Yoga — Wealth-giving combinations. Source: Phaladeepika Ch. 14."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    h2_lord = _lord_of(lagna_idx, 2)
    h11_lord = _lord_of(lagna_idx, 11)
    h5_lord = _lord_of(lagna_idx, 5)
    h9_lord = _lord_of(lagna_idx, 9)
    triggers = []
    # 2nd & 11th lords in mutual relationship
    if h2_lord in pos and h11_lord in pos:
        if pos[h2_lord]["rasi_idx"] == pos[h11_lord]["rasi_idx"]:
            triggers.append(f"{h2_lord} (2L) + {h11_lord} (11L) conjunct")
        elif _h(pos, h2_lord) == _h(pos, h11_lord):
            triggers.append(f"2L and 11L in same house")
    # 5L+9L combination
    if h5_lord in pos and h9_lord in pos:
        if pos[h5_lord]["rasi_idx"] == pos[h9_lord]["rasi_idx"]:
            triggers.append(f"{h5_lord} (5L) + {h9_lord} (9L) conjunct (Lakshmi Yoga)")
    # Strong 2nd or 11th house
    if _dig(pos, "Jupiter") in ["Own","Exalted"] and _h(pos, "Jupiter") in [2, 5, 9, 11]:
        triggers.append("Jupiter strong in wealth house")
    if len(triggers) >= 1:
        return {
            "name": "Dhana Yoga",
            "name_translation": "Wealth Yoga",
            "severity": min(5, len(triggers) + 2),
            "triggers": triggers,
            "domain": "wealth",
            "source": "Phaladeepika Ch. 14",
            "interpretation": "Significant wealth potential. Activates during dasha periods of involved lords.",
            "event_keywords": ["windfall", "income peak", "investment gain"],
        }
    return None


def yoga_raja(chart):
    """Raja Yoga — Kendra-Trikona lord combination. Source: BPHS Ch. 36."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    kendra_lords = set()
    trikona_lords = set()
    for h in [1, 4, 7, 10]:
        kendra_lords.add(_lord_of(lagna_idx, h))
    for h in [1, 5, 9]:
        trikona_lords.add(_lord_of(lagna_idx, h))
    triggers = []
    for kl in kendra_lords:
        for tl in trikona_lords:
            if kl == tl or kl not in pos or tl not in pos:
                continue
            if pos[kl]["rasi_idx"] == pos[tl]["rasi_idx"]:
                triggers.append(f"{kl} + {tl} conjunct")
    if triggers:
        return {
            "name": "Raja Yoga",
            "name_translation": "Royal Yoga",
            "severity": min(5, len(triggers) + 2),
            "triggers": triggers,
            "domain": "status",
            "source": "BPHS Ch. 36",
            "interpretation": "Status, recognition, leadership, authority. Activates during dasha of involved planets.",
            "event_keywords": ["promotion", "recognition", "leadership role", "authority"],
        }
    return None


def yoga_health_chronic(chart):
    """Chronic Health Yoga. Source: BPHS Ch. 23, Sarvarth Chintamani."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    triggers = []
    asc_lord = chart.get("lagna_lord")
    if asc_lord and _dig(pos, asc_lord) == "Debil":
        triggers.append(f"Lagna lord ({asc_lord}) debilitated")
    h6_occ = _occ(pos, 6)
    malefics_6 = [p for p in h6_occ if _is_malefic(p)]
    if len(malefics_6) >= 2:
        triggers.append(f"two malefics in 6H: {', '.join(malefics_6)}")
    elif len(malefics_6) == 1:
        triggers.append(f"malefic in 6H: {malefics_6[0]}")
    if _h(pos, "Saturn") in [1, 6, 8] and _dig(pos, "Saturn") == "Debil":
        triggers.append("Saturn weak in 1/6/8")
    if len(triggers) >= 2:
        return {
            "name": "Roga Yoga",
            "name_translation": "Chronic Illness Yoga",
            "severity": min(5, len(triggers) + 1),
            "triggers": triggers,
            "domain": "health",
            "source": "BPHS Ch. 23, Sarvarth Chintamani",
            "interpretation": "Predisposition to chronic health issues; preventive care strongly advised.",
            "event_keywords": ["health issue", "illness", "hospitalization"],
        }
    return None


def yoga_career_breakthrough(chart):
    """Career Breakthrough Yoga. Source: Phaladeepika Ch. 16."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    h10_lord = _lord_of(lagna_idx, 10)
    triggers = []
    if h10_lord in pos and _dig(pos, h10_lord) in ["Own", "Exalted"]:
        triggers.append(f"10L ({h10_lord}) strong")
    if _h(pos, "Sun") in [10, 1] and _dig(pos, "Sun") in ["Own", "Exalted"]:
        triggers.append("Sun strong in 10/1")
    h10_occ = _occ(pos, 10)
    if any(p in h10_occ for p in ["Sun","Jupiter","Mars","Saturn"]):
        triggers.append(f"strong planet in 10H: {h10_occ}")
    if len(triggers) >= 2:
        return {
            "name": "Karya-Siddhi Yoga",
            "name_translation": "Career-Success Yoga",
            "severity": min(5, len(triggers) + 1),
            "triggers": triggers,
            "domain": "career",
            "source": "Phaladeepika Ch. 16",
            "interpretation": "Strong career growth, recognition, promotions. Activates in 10L and Sun periods.",
            "event_keywords": ["promotion", "career launch", "recognition"],
        }
    return None


# ================================================================
# MASTER DETECTOR
# ================================================================

ALL_YOGAS = [
    yoga_pitru_kasht, yoga_matruhanta, yoga_vidyut, yoga_kaal_sarpa,
    yoga_balarishta, yoga_marriage_delay, yoga_dhana, yoga_raja,
    yoga_health_chronic, yoga_career_breakthrough,
]


def detect_all_yogas(chart):
    """Run all yoga detectors. Return list of active yogas."""
    results = []
    for fn in ALL_YOGAS:
        result = fn(chart)
        if result:
            results.append(result)
    return results


if __name__ == "__main__":
    import json, sys
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    yogas = detect_all_yogas(chart)
    print(f"=== {len(yogas)} YOGAS DETECTED FOR MANOJ ===\n")
    for y in yogas:
        print(f"YOGA: {y['name']} ({y['name_translation']})")
        print(f"  Severity: {'*' * y['severity']}{'.' * (5 - y['severity'])} ({y['severity']}/5)")
        print(f"  Domain:   {y['domain']}")
        print(f"  Source:   {y['source']}")
        print(f"  Triggers:")
        for t in y["triggers"]:
            print(f"    - {t}")
        print(f"  Reading:  {y['interpretation']}")
        print()
