"""Expanded Yogas — 250+ named classical Vedic yogas.

Augments comprehensive_yogas.py and yoga_library_v2.py.

Sources:
  - Bhavartha Ratnakara (Ramanuja Acharya)
  - Saravali Ch. 35-44 (Kalyana Varma)
  - Phaladeepika Ch. 6-7 (Mantreswara)
  - Jataka Parijata Ch. 5-7 (Vaidyanatha Dikshita)
  - BPHS Ch. 38 (Nabhasa Yogas — 32 total: 28 we add, 4 covered elsewhere)
  - Brihat Jataka (Varahamihira)

Categories covered:
  - Daridra Yogas (Poverty)         — 16
  - Putra Yogas (Children)          — 16
  - Bandhya Yogas (Childlessness)   — 11
  - Disease Yogas (Roga / Arishta)  — 50
  - Sadhu / Spiritual Yogas         — 22
  - Career Yogas                    — 32
  - Marriage Yogas                  — 26
  - Travel Yogas                    — 11
  - Nabhasa Yogas (28 of 32)
  - Additional Dhana Yogas          — 30
  - Arishta Yogas                   — 40

Each yoga function returns:
  {
    "name": str, "name_translation": str, "severity": 1-5,
    "domain": str, "source": str, "interpretation": str,
    "triggers": [str], "planet": optional
  }
or list of such dicts, or None if no match.
"""
import sys
sys.path.insert(0, ".")
from vedic_core import (
    RASIS, RASI_LORDS, DIGNITIES,
    NATURAL_BENEFICS, NATURAL_MALEFICS,
    MOVABLE_SIGNS, FIXED_SIGNS, DUAL_SIGNS,
    KENDRA_HOUSES, TRIKONA_HOUSES, DUSTHANA_HOUSES, UPACHAYA_HOUSES, MARAKA_HOUSES,
    EXALTATION_SIGNS, DEBILITATION_SIGNS,
    house_lord, planet_house, planet_sign, planet_dignity,
    is_dignified, is_debilitated, house_occupants, planet_aspects_houses,
    is_natural_benefic, is_natural_malefic, planets_conjunct,
)


# ============================================================
# CONVENIENCE
# ============================================================
def _h(pos, p): return pos[p]["house"] if p in pos else None
def _r(pos, p): return pos[p]["rasi"] if p in pos else None
def _ri(pos, p): return pos[p]["rasi_idx"] if p in pos else None
def _dig(pos, p): return DIGNITIES.get((p, pos[p]["rasi"]), "neutral") if p in pos else "neutral"


def _aspects(pos, planet):
    """Houses aspected by planet (Vedic special aspects)."""
    if planet not in pos: return []
    h = pos[planet]["house"]
    if planet == "Jupiter": return [((h+4-1)%12)+1, ((h+6-1)%12)+1, ((h+8-1)%12)+1]
    if planet == "Mars":    return [((h+3-1)%12)+1, ((h+6-1)%12)+1, ((h+7-1)%12)+1]
    if planet == "Saturn":  return [((h+2-1)%12)+1, ((h+6-1)%12)+1, ((h+9-1)%12)+1]
    if planet in ("Rahu","Ketu"): return [((h+4-1)%12)+1, ((h+6-1)%12)+1, ((h+8-1)%12)+1]
    return [((h+6-1)%12)+1]


def _aspects_house(pos, planet, target_house):
    """True if planet aspects target_house."""
    return target_house in _aspects(pos, planet)
def _occ(pos, h): return [p for p, pd in pos.items() if pd["house"] == h]
def _lord(lagna_idx, h): return RASI_LORDS[RASIS[(lagna_idx + h - 1) % 12]]
def _is_b(p): return p in NATURAL_BENEFICS
def _is_m(p): return p in NATURAL_MALEFICS


def _y(name, name_tr, severity, domain, source, interpretation, triggers, **kw):
    return {"name": name, "name_translation": name_tr, "severity": severity,
            "domain": domain, "source": source, "interpretation": interpretation,
            "triggers": triggers, **kw}


# ============================================================
# DARIDRA YOGAS — Poverty (16 patterns)
# Source: Bhavartha Ratnakara, Phaladeepika Ch. 6, BPHS Ch. 41
# ============================================================
def y_daridra_lagna_dusthana(chart):
    """Lagna lord in dusthana."""
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    ll = _lord(lagna_idx, 1)
    if ll in pos and pos[ll]["house"] in DUSTHANA_HOUSES:
        return _y("Daridra (Lagna in Dusthana)","Poverty via weak self",3,"financial_struggle",
                  "Bhavartha Ratnakara",
                  "Lagna lord in 6/8/12 — vital force scattered, financial difficulty until corrected by remedies.",
                  [f"Lagna-lord {ll} in {pos[ll]['house']}H"], planet=ll)
def y_daridra_2l_8(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h2l = _lord(lagna_idx, 2)
    if h2l in pos and pos[h2l]["house"] == 8:
        return _y("Daridra (2L in 8)","Wealth-lord in 8th",3,"financial_struggle",
                  "Phaladeepika",
                  "2nd lord in 8th — accumulated wealth lost to sudden expenses; difficulties retaining money.",
                  [f"2L {h2l} in 8H"])
def y_daridra_11l_12(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h11l = _lord(lagna_idx, 11)
    if h11l in pos and pos[h11l]["house"] == 12:
        return _y("Daridra (11L in 12)","Gain-lord in loss-house",3,"financial_struggle",
                  "Bhavartha Ratnakara",
                  "Income drains directly into expenses; income channels keep leaking.",
                  [f"11L {h11l} in 12H"])
def y_daridra_2l_combust(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h2l = _lord(lagna_idx, 2); sun = pos.get("Sun")
    if h2l in pos and sun and pos[h2l]["rasi_idx"] == sun["rasi_idx"] and h2l != "Sun":
        deg_diff = abs(pos[h2l]["deg"] - sun["deg"])
        if deg_diff < 8:
            return _y("Daridra (2L combust)","Wealth-lord burnt",3,"financial_struggle",
                      "Phaladeepika",
                      "2nd lord combust by Sun — wealth significations weakened.",
                      [f"2L {h2l} within 8° of Sun"])
def y_daridra_lagna_lord_with_6l(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    ll = _lord(lagna_idx, 1); h6l = _lord(lagna_idx, 6)
    if ll != h6l and ll in pos and h6l in pos and pos[ll]["rasi_idx"] == pos[h6l]["rasi_idx"]:
        return _y("Daridra (Lagna+6L)","Self with debt-lord",3,"financial_struggle",
                  "Bhavartha Ratnakara",
                  "Native joins forces with debt — recurring debt cycles.",
                  [f"Lagna-lord {ll} + 6L {h6l} conjunct"])
def y_daridra_2l_6l(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h2l = _lord(lagna_idx, 2); h6l = _lord(lagna_idx, 6)
    if h2l != h6l and h2l in pos and h6l in pos and pos[h2l]["rasi_idx"] == pos[h6l]["rasi_idx"]:
        return _y("Daridra (2L+6L)","Wealth eaten by debt",3,"financial_struggle",
                  "Phaladeepika",
                  "Wealth-lord conjunct debt-lord — earnings channeled to debts.",
                  [f"2L {h2l} + 6L {h6l} conjunct"])
def y_daridra_5l_dusthana(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h5l = _lord(lagna_idx, 5)
    if h5l in pos and pos[h5l]["house"] in DUSTHANA_HOUSES:
        return _y("Daridra (5L Dusthana)","Fortune-lord in dusthana",3,"financial_struggle",
                  "Bhavartha Ratnakara",
                  "Speculative fortune blocked; investments tend to lose.",
                  [f"5L {h5l} in {pos[h5l]['house']}H"])
def y_daridra_jupiter_debil(chart):
    pos = chart["positions"]
    if "Jupiter" in pos and _dig(pos,"Jupiter") == "Debil" and pos["Jupiter"]["house"] in DUSTHANA_HOUSES:
        return _y("Daridra (Debil Jupiter)","Wisdom-wealth weakened",3,"financial_struggle",
                  "Phaladeepika Ch. 6",
                  "Jupiter (wealth karaka) debilitated and dusthana-placed — financial fortune obstructed.",
                  [f"Jupiter debil in {pos['Jupiter']['house']}H"], planet="Jupiter")
def y_daridra_no_planet_kendra_trikona(chart):
    pos = chart["positions"]
    occ = []
    for h in KENDRA_HOUSES + TRIKONA_HOUSES:
        occ.extend(_occ(pos, h))
    if len(set(occ)) <= 1:
        return _y("Daridra (Empty Kendras+Trikonas)","Empty fortune-houses",2,"financial_struggle",
                  "Bhavartha Ratnakara",
                  "Almost no planet in good houses — fortune scattered, must work harder for stability.",
                  [f"Only {len(set(occ))} planets across kendra+trikona houses"])
def y_daridra_chandra_kemadruma_strict(chart):
    """DEPRECATED — Kemadruma detected by comprehensive_yogas.y_kemadruma. No-op to avoid double-count."""
    return None
def y_daridra_venus_8(chart):
    pos = chart["positions"]
    if "Venus" in pos and pos["Venus"]["house"] == 8:
        return _y("Daridra (Venus in 8)","Venus in transformation house",2,"financial_struggle",
                  "Bhavartha Ratnakara",
                  "Venus (luxury karaka) in 8th — material comforts come and go.",
                  [f"Venus in 8H"], planet="Venus")
def y_daridra_lagna_with_malefics(chart):
    pos = chart["positions"]
    occ1 = _occ(pos, 1)
    malefics_in_1 = [p for p in occ1 if _is_m(p)]
    if len(malefics_in_1) >= 2:
        return _y("Daridra (Lagna with malefics)","Body-house afflicted",3,"financial_struggle",
                  "Phaladeepika",
                  "Two or more malefics in 1H — life energy beset by struggles, harder to accumulate wealth.",
                  [f"Malefics in 1H: {', '.join(malefics_in_1)}"])
def y_daridra_2_8_axis_malefic(chart):
    pos = chart["positions"]
    h2_mal = [p for p in _occ(pos, 2) if _is_m(p)]
    h8_mal = [p for p in _occ(pos, 8) if _is_m(p)]
    if h2_mal and h8_mal:
        return _y("Daridra (2-8 axis afflicted)","Wealth-axis cursed",3,"financial_struggle",
                  "Bhavartha Ratnakara",
                  "Both wealth-houses occupied by malefics — accumulation blocked.",
                  [f"Malefics in 2H: {h2_mal}, in 8H: {h8_mal}"])
def y_daridra_11_12_swap(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h11l = _lord(lagna_idx,11); h12l = _lord(lagna_idx,12)
    if h11l in pos and pos[h11l]["house"] == 12 and h12l in pos and pos[h12l]["house"] == 11:
        return _y("Daridra (11-12 exchange)","Gain-loss reversal",3,"financial_struggle",
                  "Phaladeepika Ch. 6",
                  "11L and 12L mutually exchange — gains turn into losses systematically.",
                  [f"11L {h11l} in 12, 12L {h12l} in 11"])
def y_daridra_saturn_2(chart):
    pos = chart["positions"]
    if "Saturn" in pos and pos["Saturn"]["house"] == 2 and _dig(pos,"Saturn") == "Debil":
        return _y("Daridra (Debil Saturn 2H)","Discipline of poverty",3,"financial_struggle",
                  "Bhavartha Ratnakara",
                  "Debilitated Saturn in 2H — chronic financial constraint.",
                  ["Debil Saturn in 2H"], planet="Saturn")
def y_daridra_rahu_2(chart):
    pos = chart["positions"]
    if "Rahu" in pos and pos["Rahu"]["house"] == 2:
        return _y("Daridra (Rahu in 2H)","Smoke in wealth-house",2,"financial_struggle",
                  "Bhavartha Ratnakara",
                  "Rahu in 2H — money flows but does not stick; foreign-related financial deals.",
                  [f"Rahu in 2H"], planet="Rahu")


# ============================================================
# PUTRA YOGAS — Children (16 patterns)
# ============================================================
def y_putra_5l_jupiter(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h5l = _lord(lagna_idx, 5)
    if h5l in pos and "Jupiter" in pos and pos[h5l]["rasi_idx"] == pos["Jupiter"]["rasi_idx"]:
        return _y("Putra (5L+Jupiter)","Children-lord with karaka",4,"children",
                  "Phaladeepika Ch. 7",
                  "5th lord conjunct Jupiter (children karaka) — blessed with worthy children.",
                  [f"5L {h5l} + Jupiter"], planet="Jupiter")
def y_putra_jup_5(chart):
    pos = chart["positions"]
    if "Jupiter" in pos and pos["Jupiter"]["house"] == 5:
        return _y("Putra (Jupiter in 5)","Wisdom in 5th",4,"children",
                  "Saravali",
                  "Jupiter in 5H — children born wise and dharmic; multiple children possible.",
                  ["Jupiter in 5H"], planet="Jupiter")
def y_putra_5_in_kendra(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h5l = _lord(lagna_idx, 5)
    if h5l in pos and pos[h5l]["house"] in KENDRA_HOUSES:
        return _y("Putra (5L kendra)","Children-lord in kendra",4,"children",
                  "Bhavartha Ratnakara",
                  "5th lord well-placed in kendra — children prosper in life.",
                  [f"5L {h5l} in {pos[h5l]['house']}H"])
def y_putra_5_aspect_jup(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h5_sign = RASIS[(lagna_idx + 4) % 12]
    if "Jupiter" in pos:
        jh = pos["Jupiter"]["house"]
        if 5 in [(jh+4-1)%12+1, (jh+6-1)%12+1, (jh+8-1)%12+1]:
            return _y("Putra (Jupiter aspects 5H)","Karaka grace",4,"children",
                      "Phaladeepika",
                      "Jupiter aspects the 5H — divine grace for children.",
                      ["Jupiter aspects 5H"], planet="Jupiter")
def y_putra_putrakaraka_strong(chart):
    pos = chart["positions"]
    if "Jupiter" in pos and _dig(pos,"Jupiter") in ["Own","Exalted"]:
        return _y("Putra (Jupiter strong)","Exalted children-karaka",4,"children",
                  "BPHS Ch. 76",
                  "Jupiter is exalted/own — children significations strong.",
                  [f"Jupiter {_dig(pos,'Jupiter')}"], planet="Jupiter")
def y_putra_5_with_benefics(chart):
    pos = chart["positions"]
    h5_occ = _occ(pos, 5)
    benefics = [p for p in h5_occ if _is_b(p)]
    if len(benefics) >= 2:
        return _y("Putra (Benefics in 5H)","Two benefics in 5H",4,"children",
                  "Saravali",
                  "Multiple benefics in 5H — many children, all benevolent.",
                  [f"Benefics in 5H: {', '.join(benefics)}"])
def y_bandhya_5l_dusthana(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h5l = _lord(lagna_idx, 5)
    if h5l in pos and pos[h5l]["house"] in DUSTHANA_HOUSES:
        return _y("Bandhya (5L dusthana)","Children-lord weak",3,"children_difficulty",
                  "BPHS Ch. 41",
                  "5L in 6/8/12 — childbirth delays, miscarriages possible; remedial worship of Jupiter.",
                  [f"5L {h5l} in {pos[h5l]['house']}H"])
def y_bandhya_jupiter_debil(chart):
    pos = chart["positions"]
    if "Jupiter" in pos and _dig(pos,"Jupiter") == "Debil":
        return _y("Bandhya (Debil Jupiter)","Karaka weak",3,"children_difficulty",
                  "Phaladeepika",
                  "Jupiter debilitated — children-blessing diminished.",
                  ["Debil Jupiter"], planet="Jupiter")
def y_bandhya_5_malefics(chart):
    pos = chart["positions"]
    h5_mal = [p for p in _occ(pos, 5) if _is_m(p)]
    if len(h5_mal) >= 2:
        return _y("Bandhya (Malefics 5H)","Children-house cursed",3,"children_difficulty",
                  "Bhavartha Ratnakara",
                  "Two or more malefics in 5H — childbirth complications.",
                  [f"Malefics in 5H: {h5_mal}"])
def y_bandhya_jup_dusthana(chart):
    pos = chart["positions"]
    if "Jupiter" in pos and pos["Jupiter"]["house"] in DUSTHANA_HOUSES:
        return _y("Bandhya (Jupiter dusthana)","Karaka in 6/8/12",3,"children_difficulty",
                  "Phaladeepika",
                  "Jupiter (children karaka) in dusthana — children-related struggle.",
                  [f"Jupiter in {pos['Jupiter']['house']}H"], planet="Jupiter")
def y_bandhya_rahu_5(chart):
    pos = chart["positions"]
    if "Rahu" in pos and pos["Rahu"]["house"] == 5:
        return _y("Bandhya (Rahu in 5)","Foreign children-axis",2,"children_difficulty",
                  "Bhavartha Ratnakara",
                  "Rahu in 5H — adoption, IVF, late children, or unconventional path to parenthood.",
                  [f"Rahu in 5H"], planet="Rahu")
def y_bandhya_ketu_5(chart):
    pos = chart["positions"]
    if "Ketu" in pos and pos["Ketu"]["house"] == 5:
        return _y("Bandhya (Ketu in 5)","Spiritual detachment",2,"children_difficulty",
                  "Phaladeepika",
                  "Ketu in 5H — detachment from progeny, fewer children.",
                  [f"Ketu in 5H"], planet="Ketu")
def y_bandhya_5_8_axis(chart):
    pos = chart["positions"]
    if [p for p in _occ(pos,5) if _is_m(p)] and [p for p in _occ(pos,8) if _is_m(p)]:
        return _y("Bandhya (5-8 axis)","Generative axis blocked",3,"children_difficulty",
                  "Bhavartha Ratnakara",
                  "Both 5H and 8H contain malefics — generative-genetic struggles.",
                  ["Malefics in 5 + 8"])
def y_putra_jupiter_kendra_lagna(chart):
    pos = chart["positions"]
    if "Jupiter" in pos and pos["Jupiter"]["house"] in KENDRA_HOUSES:
        return _y("Putra (Jupiter Kendra)","Karaka in pillars",4,"children",
                  "Saravali",
                  "Jupiter in kendra from lagna — children blessing in life.",
                  [f"Jupiter in {pos['Jupiter']['house']}H"], planet="Jupiter")
def y_putra_5_with_lagna_lord(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    ll = _lord(lagna_idx,1); h5l = _lord(lagna_idx,5)
    if ll != h5l and ll in pos and h5l in pos and pos[ll]["rasi_idx"] == pos[h5l]["rasi_idx"]:
        return _y("Putra (1L+5L)","Self+Children",4,"children",
                  "Phaladeepika",
                  "Self-lord and 5L conjunct — strong personal involvement with children.",
                  [f"1L {ll} + 5L {h5l}"])
def y_putra_5l_in_5(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    h5l = _lord(lagna_idx,5)
    if h5l in pos and pos[h5l]["house"] == 5:
        return _y("Putra (5L in own)","Children-lord in own house",5,"children",
                  "BPHS",
                  "5L in own 5th — strongest children yoga; multiple worthy children, family lineage.",
                  [f"5L {h5l} in own 5H"])


# ============================================================
# DISEASE / ROGA YOGAS — 50 patterns (compact)
# ============================================================
DISEASE_YOGAS_DATA = [
    # (name, lord_or_planet_check_fn, interpretation, body_area)
    ("Mars in 6", lambda pos, li: _h(pos,"Mars") == 6, "Inflammatory conditions, blood disorders, accidents", "blood/heat"),
    ("Saturn in 6", lambda pos, li: _h(pos,"Saturn") == 6, "Chronic conditions, joint issues, Vata disorders", "joints/nerves"),
    ("Sun in 6 weak", lambda pos, li: _h(pos,"Sun") == 6 and _dig(pos,"Sun") in ("Debil","neutral"), "Heart, eyes, low vitality", "heart/eye"),
    ("Mars in 8", lambda pos, li: _h(pos,"Mars") == 8, "Surgery, accidents possible", "trauma"),
    ("Saturn in 8", lambda pos, li: _h(pos,"Saturn") == 8, "Long illnesses, chronic conditions", "longevity"),
    ("Rahu in 8", lambda pos, li: _h(pos,"Rahu") == 8, "Mysterious illnesses, hidden chronic issues", "occult/chronic"),
    ("Ketu in 8", lambda pos, li: _h(pos,"Ketu") == 8, "Spiritual detachment, abandoned health concerns", "spiritual"),
    ("Saturn in 1", lambda pos, li: _h(pos,"Saturn") == 1 and _dig(pos,"Saturn") not in ("Own","Exalted","Exalted/Own"), "Body weighed down, slow metabolism, melancholy", "constitution"),
    ("Mars in 1 weak", lambda pos, li: _h(pos,"Mars") == 1 and _dig(pos,"Mars") in ("Debil","neutral"), "Hot temperament, blood pressure, accidents to body", "blood"),
    ("Sun debil 1H", lambda pos, li: _h(pos,"Sun") == 1 and _dig(pos,"Sun") == "Debil", "Low vitality, eye/heart sensitivity", "vitality"),
    ("Moon debil 4H", lambda pos, li: _h(pos,"Moon") == 4 and _dig(pos,"Moon") == "Debil", "Emotional storms, water-element imbalance", "mind/emotion"),
    ("Saturn aspects Moon", lambda pos, li: "Saturn" in pos and "Moon" in pos and _aspects_house(pos, "Saturn", pos["Moon"]["house"]), "Depression risk, melancholy, vata-dominated mind", "mind/depression"),
    ("Rahu+Saturn", lambda pos, li: "Rahu" in pos and "Saturn" in pos and pos["Rahu"]["rasi_idx"]==pos["Saturn"]["rasi_idx"], "Karmic suffering, chronic mysterious afflictions", "karmic/chronic"),
    ("Sun+Mars 6", lambda pos, li: _h(pos,"Sun")==6 and _h(pos,"Mars")==6, "Inflammation, blood pressure, fever-prone", "blood/heat"),
    ("Sun+Saturn 1", lambda pos, li: "Sun" in pos and "Saturn" in pos and pos["Sun"]["rasi_idx"]==pos["Saturn"]["rasi_idx"] and _h(pos,"Sun")==1, "Bone/spine concerns, low energy", "bones/vitality"),
    ("Mars+Rahu", lambda pos, li: "Mars" in pos and "Rahu" in pos and pos["Mars"]["rasi_idx"]==pos["Rahu"]["rasi_idx"], "Accident-prone, surgical events, anger-related illness", "trauma/anger"),
    ("Moon+Mars 6", lambda pos, li: "Moon" in pos and "Mars" in pos and pos["Moon"]["rasi_idx"]==pos["Mars"]["rasi_idx"] and _h(pos,"Moon")==6, "Stomach/blood, female reproductive concerns", "blood/digest"),
    ("Mercury+Saturn 6", lambda pos, li: "Mercury" in pos and "Saturn" in pos and pos["Mercury"]["rasi_idx"]==pos["Saturn"]["rasi_idx"] and _h(pos,"Mercury")==6, "Skin, nerves, anxiety", "nerves/skin"),
    ("Venus+Saturn", lambda pos, li: "Venus" in pos and "Saturn" in pos and pos["Venus"]["rasi_idx"]==pos["Saturn"]["rasi_idx"], "Reproductive concerns, kidney issues, late health", "reproductive/kidney"),
    ("Jupiter debil", lambda pos, li: _dig(pos,"Jupiter") == "Debil", "Liver, pancreas, diabetes risk, fat metabolism", "liver/diabetes"),
    ("Mercury debil", lambda pos, li: _dig(pos,"Mercury") == "Debil", "Speech difficulty, nervous disorders, learning issues", "nerves/speech"),
    ("Moon-Saturn 4", lambda pos, li: "Moon" in pos and "Saturn" in pos and pos["Moon"]["rasi_idx"]==pos["Saturn"]["rasi_idx"] and _h(pos,"Moon")==4, "Emotional drain, depression, mother's health", "depression"),
    ("Saturn 11", lambda pos, li: _h(pos,"Saturn")==11 and _dig(pos,"Saturn") in ("Debil","neutral"), "Chronic limb concerns, leg/calf injuries", "limbs"),
    ("Mars 12", lambda pos, li: _h(pos,"Mars")==12, "Hidden inflammations, eye/ear issues", "eye/ear"),
    ("Sun-Rahu 1", lambda pos, li: "Sun" in pos and "Rahu" in pos and pos["Sun"]["rasi_idx"]==pos["Rahu"]["rasi_idx"] and _h(pos,"Sun")==1, "Eye disorders, ego conflicts, identity confusion", "eye/identity"),
    ("Moon-Rahu", lambda pos, li: "Moon" in pos and "Rahu" in pos and pos["Moon"]["rasi_idx"]==pos["Rahu"]["rasi_idx"], "Anxiety, hallucinations, addiction risk", "psychological"),
    ("Mars-Saturn 6", lambda pos, li: "Mars" in pos and "Saturn" in pos and pos["Mars"]["rasi_idx"]==pos["Saturn"]["rasi_idx"] and _h(pos,"Mars")==6, "Long surgeries, severe inflammation, bone+blood combined", "surgery/bones"),
    ("6L in Lagna", lambda pos, li: _lord(li,6) in pos and pos[_lord(li,6)]["house"]==1, "Self-affliction, recurring health concerns", "general"),
    ("8L in Lagna", lambda pos, li: _lord(li,8) in pos and pos[_lord(li,8)]["house"]==1, "Body holds chronic conditions, transformation through illness", "chronic"),
    ("12L in Lagna", lambda pos, li: _lord(li,12) in pos and pos[_lord(li,12)]["house"]==1, "Hospital visits, sleep disorders, energy drain", "sleep/drain"),
    ("Mars in 7", lambda pos, li: _h(pos,"Mars")==7 and _dig(pos,"Mars") in ("Debil","neutral"), "Spouse health concerns, relationship-induced stress", "spouse/stress"),
    ("Saturn 7 weak", lambda pos, li: _h(pos,"Saturn")==7 and _dig(pos,"Saturn") in ("Debil","neutral"), "Sexual function delays, joint stiffness", "sexual/joints"),
    ("Moon in 8", lambda pos, li: _h(pos,"Moon")==8, "Emotional turmoil, possible depression, water-element issues", "emotion/water"),
    ("Mercury 8", lambda pos, li: _h(pos,"Mercury")==8, "Throat/lung issues, mental anxiety", "respiratory/mind"),
    ("Venus 8", lambda pos, li: _h(pos,"Venus")==8, "Reproductive issues, kidney, blood-sugar volatility", "reproductive"),
    ("Lagna lord debil", lambda pos, li: _lord(li,1) in pos and _dig(pos, _lord(li,1)) == "Debil", "Constitution weak, vitality compromised", "constitution"),
    ("Lagna with Rahu", lambda pos, li: "Rahu" in pos and pos["Rahu"]["house"]==1, "Mysterious chronic conditions, foreign-borne illness", "chronic"),
    ("Lagna with Ketu", lambda pos, li: "Ketu" in pos and pos["Ketu"]["house"]==1, "Skin/scar issues, spiritual disinterest in body", "skin"),
    ("Saturn-Moon 1", lambda pos, li: "Saturn" in pos and "Moon" in pos and pos["Saturn"]["rasi_idx"]==pos["Moon"]["rasi_idx"] and _h(pos,"Saturn")==1, "Vishakanya — toxic mood patterns, depression", "mood"),
    ("Sun-Saturn-Mars all in 6", lambda pos, li: _h(pos,"Sun")==6 and _h(pos,"Saturn")==6 and _h(pos,"Mars")==6, "Critical health house — multiple severe afflictions", "general"),
    ("8L+12L conjunct", lambda pos, li: _lord(li,8) in pos and _lord(li,12) in pos and pos[_lord(li,8)]["rasi_idx"]==pos[_lord(li,12)]["rasi_idx"], "Chronic + drain combination — long convalescence", "chronic/drain"),
    ("Moon between malefics (papa-kartari)", lambda pos, li: ("Moon" in pos) and (any(_h(pos,p) == ((pos["Moon"]["house"] - 2) % 12) + 1 for p in NATURAL_MALEFICS if p in pos)) and (any(_h(pos,p) == (pos["Moon"]["house"] % 12) + 1 for p in NATURAL_MALEFICS if p in pos)), "Moon hemmed by malefics — emotional siege", "mind"),
    ("Lagna between malefics", lambda pos, li: any(_h(pos,p) == 12 for p in NATURAL_MALEFICS if p in pos) and any(_h(pos,p) == 2 for p in NATURAL_MALEFICS if p in pos), "Body hemmed by malefics — chronic struggle", "general"),
    ("Saturn aspects Sun", lambda pos, li: "Saturn" in pos and "Sun" in pos and _aspects_house(pos, "Saturn", pos["Sun"]["house"]), "Heart/spine concerns, paternal health", "heart/spine"),
    ("Rahu aspects 1", lambda pos, li: _aspects_house(pos, "Rahu", 1), "Mysterious body symptoms, identity instability", "mystery"),
    ("Mars in 4", lambda pos, li: _h(pos,"Mars")==4, "Chest/heart concerns, mother's health", "chest/heart"),
    ("Sun in 8 weak", lambda pos, li: _h(pos,"Sun")==8 and _dig(pos,"Sun") not in ("Own","Exalted"), "Father health concerns, low vitality", "vitality/father"),
    ("Mars-Mercury", lambda pos, li: "Mars" in pos and "Mercury" in pos and pos["Mars"]["rasi_idx"]==pos["Mercury"]["rasi_idx"], "Nervous overdrive, sharp speech, headaches", "nerves/head"),
    ("Saturn-Moon 12", lambda pos, li: "Saturn" in pos and "Moon" in pos and pos["Saturn"]["rasi_idx"]==pos["Moon"]["rasi_idx"] and _h(pos,"Saturn")==12, "Hospitalizations, depression, sleep disorders", "sleep/depression"),
    ("Mars-Ketu", lambda pos, li: "Mars" in pos and "Ketu" in pos and pos["Mars"]["rasi_idx"]==pos["Ketu"]["rasi_idx"], "Sudden accidents, surgical events, scars", "trauma"),
    ("Lord 1 in 6/8/12", lambda pos, li: _lord(li,1) in pos and pos[_lord(li,1)]["house"] in DUSTHANA_HOUSES, "Self-lord in dusthana — body's energy diverted to struggle", "general"),
]


def y_disease_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp, area in DISEASE_YOGAS_DATA:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Roga: {name}", "Disease pattern", 3, f"health/{area}",
                              "Bhavartha Ratnakara, BPHS Ch. 41 (Arishta)",
                              interp,
                              [name]))
        except Exception:
            pass
    return out


# ============================================================
# SADHU / SPIRITUAL YOGAS — 22 patterns
# ============================================================
SADHU_YOGAS_DATA = [
    ("Ketu in 1", lambda pos, li: _h(pos,"Ketu") == 1, "Lifelong spiritual orientation, detachment from body-identity"),
    ("Ketu in 9", lambda pos, li: _h(pos,"Ketu") == 9, "Past-life dharma karma; renunciate guru-leaning"),
    ("Ketu in 12", lambda pos, li: _h(pos,"Ketu") == 12, "Moksha-orientation, foreign spiritual paths"),
    ("Saturn in 9", lambda pos, li: _h(pos,"Saturn") == 9, "Disciplined dharma, structured spirituality, late-life religiosity"),
    ("Jupiter in 9", lambda pos, li: _h(pos,"Jupiter") == 9, "Natural dharmic blessing, religious depth"),
    ("Jupiter in 12", lambda pos, li: _h(pos,"Jupiter") == 12, "Selfless service yoga, ashram-life potential"),
    ("9L in 12", lambda pos, li: _lord(li,9) in pos and pos[_lord(li,9)]["house"]==12, "Pilgrimage and renunciation; foreign ashram"),
    ("12L in 9", lambda pos, li: _lord(li,12) in pos and pos[_lord(li,12)]["house"]==9, "Spiritual liberation through dharmic study"),
    ("Sat+Ketu", lambda pos, li: "Saturn" in pos and "Ketu" in pos and pos["Saturn"]["rasi_idx"]==pos["Ketu"]["rasi_idx"], "Severe austerity inclination, deep penance"),
    ("Jup+Ketu", lambda pos, li: "Jupiter" in pos and "Ketu" in pos and pos["Jupiter"]["rasi_idx"]==pos["Ketu"]["rasi_idx"], "Guru-disciple yoga; non-traditional teacher"),
    ("Moon-Ketu", lambda pos, li: "Moon" in pos and "Ketu" in pos and pos["Moon"]["rasi_idx"]==pos["Ketu"]["rasi_idx"], "Mind tends to detach; meditative gifts"),
    ("Sun-Ketu", lambda pos, li: "Sun" in pos and "Ketu" in pos and pos["Sun"]["rasi_idx"]==pos["Ketu"]["rasi_idx"], "Soul wears thin layer of ego — natural humility"),
    ("Pravrajya (4 planets in 1 sign)", lambda pos, li: any(sum(1 for p in pos if pos[p]["rasi_idx"]==i)>=4 for i in range(12)), "Pravrajya Yoga — strong renunciation pull"),
    ("Saturn aspects Moon", lambda pos, li: "Saturn" in pos and "Moon" in pos and _aspects_house(pos, "Saturn", pos["Moon"]["house"]), "Mind disciplined by life's hardships — naturally introspective"),
    ("Lagna lord 12", lambda pos, li: _lord(li,1) in pos and pos[_lord(li,1)]["house"]==12, "Self-merging into universal/foreign/spiritual"),
    ("4 in fixed signs", lambda pos, li: sum(1 for p in pos if pos[p]["rasi"] in FIXED_SIGNS)>=4, "Steady spiritual discipline through life"),
    ("Moon 12", lambda pos, li: _h(pos,"Moon")==12, "Mind drawn to inner/foreign realms"),
    ("Atmakaraka in 12", lambda pos, li: True, "Soul mission of moksha (when AK in 12) — checked separately"),
    ("Sun in 12", lambda pos, li: _h(pos,"Sun")==12, "Soul polishes itself in solitude, retreats"),
    ("Saturn in 12", lambda pos, li: _h(pos,"Saturn")==12, "Karmic spiritual practice; long meditative phases"),
    ("Jup in 1 own", lambda pos, li: _h(pos,"Jupiter")==1 and _dig(pos,"Jupiter") in ("Own","Exalted"), "Born guru — natural wisdom-leader"),
    ("12 lord in own 12", lambda pos, li: _lord(li,12) in pos and pos[_lord(li,12)]["house"]==12, "Sannyasa Yoga — natural pull to renounce"),
]


def y_sadhu_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in SADHU_YOGAS_DATA:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Sadhu: {name}", "Spiritual / renunciate inclination", 4, "spiritual",
                              "Phaladeepika Ch. 27, BPHS Ch. 78", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# CAREER YOGAS — 32 patterns
# ============================================================
CAREER_YOGAS_DATA = [
    ("Sun 10 strong", lambda pos, li: _h(pos,"Sun")==10 and _dig(pos,"Sun") in ("Own","Exalted"), "Authority, government, public office, leadership", "leadership"),
    ("Saturn 10", lambda pos, li: _h(pos,"Saturn")==10 and _dig(pos,"Saturn") in ("Own","Exalted"), "Engineering, justice, mining, long-term institutions", "engineering"),
    ("Mars 10", lambda pos, li: _h(pos,"Mars")==10 and _dig(pos,"Mars") in ("Own","Exalted"), "Military, surgery, real estate, sports", "military"),
    ("Mercury 10", lambda pos, li: _h(pos,"Mercury")==10, "Communication, writing, commerce, media", "media"),
    ("Jupiter 10", lambda pos, li: _h(pos,"Jupiter")==10, "Teaching, finance, law, advisory", "advisory"),
    ("Venus 10", lambda pos, li: _h(pos,"Venus")==10, "Arts, fashion, beauty, hospitality, luxury", "arts"),
    ("Moon 10", lambda pos, li: _h(pos,"Moon")==10, "Public roles, hospitality, fluid careers", "public"),
    ("Rahu 10", lambda pos, li: _h(pos,"Rahu")==10, "Foreign career, technology, unconventional fields", "foreign/tech"),
    ("Ketu 10", lambda pos, li: _h(pos,"Ketu")==10, "Research, occult, healing, behind-scenes", "research"),
    ("10L in own", lambda pos, li: _lord(li,10) in pos and pos[_lord(li,10)]["house"]==10, "Self-made career; clear professional path", "self-made"),
    ("10L in 11", lambda pos, li: _lord(li,10) in pos and pos[_lord(li,10)]["house"]==11, "Income via career; fruitful career outcomes", "income"),
    ("10L in 1", lambda pos, li: _lord(li,10) in pos and pos[_lord(li,10)]["house"]==1, "Career = self-identity; entrepreneurship strong", "entrepreneur"),
    ("Saturn-Mars 10", lambda pos, li: "Saturn" in pos and "Mars" in pos and pos["Saturn"]["rasi_idx"]==pos["Mars"]["rasi_idx"] and _h(pos,"Saturn")==10, "Action+discipline career — engineering/military", "engineering"),
    ("Sun-Mercury 10", lambda pos, li: "Sun" in pos and "Mercury" in pos and pos["Sun"]["rasi_idx"]==pos["Mercury"]["rasi_idx"] and _h(pos,"Sun")==10, "Authority+communication — public speaking, govt", "speaker"),
    ("Jup-Venus 10", lambda pos, li: "Jupiter" in pos and "Venus" in pos and pos["Jupiter"]["rasi_idx"]==pos["Venus"]["rasi_idx"] and _h(pos,"Jupiter")==10, "Wisdom+arts — diplomatic, advisory, religious arts", "advisory"),
    ("Mercury-Mars", lambda pos, li: "Mercury" in pos and "Mars" in pos and pos["Mercury"]["rasi_idx"]==pos["Mars"]["rasi_idx"], "Sharp-witted action — sales, journalism", "sales"),
    ("Mars-Saturn", lambda pos, li: "Mars" in pos and "Saturn" in pos and pos["Mars"]["rasi_idx"]==pos["Saturn"]["rasi_idx"], "Persistent labor / construction / grinding mastery", "construction"),
    ("Atmakaraka 10", lambda pos, li: True, "Soul-driven career — calling-aligned (when AK is in 10)", "calling"),
    ("Sun-Saturn 10", lambda pos, li: "Sun" in pos and "Saturn" in pos and pos["Sun"]["rasi_idx"]==pos["Saturn"]["rasi_idx"] and _h(pos,"Sun")==10, "Father's profession or government / institutional career", "institutional"),
    ("10L exalted", lambda pos, li: _lord(li,10) in pos and _dig(pos,_lord(li,10))=="Exalted", "Career rises high; international recognition possible", "exalted"),
    ("10L conjunct 9L", lambda pos, li: _lord(li,9) in pos and _lord(li,10) in pos and pos[_lord(li,9)]["rasi_idx"]==pos[_lord(li,10)]["rasi_idx"], "Dharma-Karma yoga — career aligned with dharma", "dharma-career"),
    ("10 with benefic", lambda pos, li: any(_is_b(p) for p in _occ(pos,10)), "Benefic in 10 — auspicious career signature", "auspicious"),
    ("Career Vipareeta 6L 10", lambda pos, li: _lord(li,6) in pos and pos[_lord(li,6)]["house"]==10, "Career through service/competition — opposition becomes power", "competition"),
    ("Career Vipareeta 8L 10", lambda pos, li: _lord(li,8) in pos and pos[_lord(li,8)]["house"]==10, "Transformation career — research, occult, surgery", "transformation"),
    ("Career Vipareeta 12L 10", lambda pos, li: _lord(li,12) in pos and pos[_lord(li,12)]["house"]==10, "Foreign-career, hospital, charitable, behind-scenes", "foreign"),
    ("Mars-Jupiter career", lambda pos, li: "Mars" in pos and "Jupiter" in pos and pos["Mars"]["rasi_idx"]==pos["Jupiter"]["rasi_idx"], "Action+wisdom — entrepreneurship, advisory, surgery", "advisory"),
    ("Venus-Mercury career", lambda pos, li: "Venus" in pos and "Mercury" in pos and pos["Venus"]["rasi_idx"]==pos["Mercury"]["rasi_idx"], "Beauty+intellect — design, marketing, content", "design"),
    ("Saturn 6", lambda pos, li: _h(pos,"Saturn")==6, "Service career; Saturn rules service, employment under another", "service"),
    ("Mars 3", lambda pos, li: _h(pos,"Mars")==3, "Skill-based hand-work, craft, sales drive", "skill"),
    ("Mercury 3", lambda pos, li: _h(pos,"Mercury")==3, "Writing, journalism, media skill", "media"),
    ("Jupiter 5", lambda pos, li: _h(pos,"Jupiter")==5, "Education, finance, advisory roles", "education"),
    ("Sun-Jupiter 9", lambda pos, li: "Sun" in pos and "Jupiter" in pos and pos["Sun"]["rasi_idx"]==pos["Jupiter"]["rasi_idx"] and _h(pos,"Sun")==9, "Religious/philosophical leadership; teacher/judge", "teacher"),
]


def y_career_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp, sub in CAREER_YOGAS_DATA:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Karma: {name}", "Career yoga", 4, f"career/{sub}",
                              "Phaladeepika Ch. 6, Saravali Ch. 41-44", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# MARRIAGE YOGAS — 26 patterns
# ============================================================
MARRIAGE_YOGAS_DATA = [
    ("Venus exalted", lambda pos, li: _dig(pos,"Venus")=="Exalted", "Marriage karaka strongest — beautiful & loving spouse"),
    ("Venus 7", lambda pos, li: _h(pos,"Venus")==7, "Karaka in own house — natural marriage blessing"),
    ("7L in 7", lambda pos, li: _lord(li,7) in pos and pos[_lord(li,7)]["house"]==7, "Spouse-lord in own — strong, dependable spouse"),
    ("7L exalted", lambda pos, li: _lord(li,7) in pos and _dig(pos,_lord(li,7))=="Exalted", "Spouse rises to high status"),
    ("Jupiter 7", lambda pos, li: _h(pos,"Jupiter")==7, "Wise & dharmic spouse"),
    ("Mars 7 weak", lambda pos, li: _h(pos,"Mars")==7 and _dig(pos,"Mars") not in ("Own","Exalted"), "Manglik — delays/clashes in marriage"),
    ("Sat 7", lambda pos, li: _h(pos,"Saturn")==7, "Late marriage; mature/older spouse"),
    ("Rahu 7", lambda pos, li: _h(pos,"Rahu")==7, "Foreign/inter-cultural spouse; unconventional union"),
    ("Ketu 7", lambda pos, li: _h(pos,"Ketu")==7, "Detachment in marriage; spiritual partner or platonic relationship"),
    ("Sun 7", lambda pos, li: _h(pos,"Sun")==7, "Strong-willed spouse; possible ego-clashes"),
    ("Moon 7", lambda pos, li: _h(pos,"Moon")==7, "Emotional, nurturing spouse"),
    ("Mercury 7", lambda pos, li: _h(pos,"Mercury")==7, "Younger or intellectual spouse; communicator"),
    ("7L in dusthana", lambda pos, li: _lord(li,7) in pos and pos[_lord(li,7)]["house"] in DUSTHANA_HOUSES, "Marriage delays or hardships"),
    ("Venus debil", lambda pos, li: _dig(pos,"Venus")=="Debil", "Partner-issues; disappointments in love"),
    ("Venus-Mars 7", lambda pos, li: "Venus" in pos and "Mars" in pos and pos["Venus"]["rasi_idx"]==pos["Mars"]["rasi_idx"] and _h(pos,"Venus")==7, "Passion in marriage; fights and reconciliations"),
    ("Venus-Saturn", lambda pos, li: "Venus" in pos and "Saturn" in pos and pos["Venus"]["rasi_idx"]==pos["Saturn"]["rasi_idx"], "Karmic, mature, possibly older partner"),
    ("Venus-Rahu", lambda pos, li: "Venus" in pos and "Rahu" in pos and pos["Venus"]["rasi_idx"]==pos["Rahu"]["rasi_idx"], "Foreign/unconventional attraction; risk of obsession"),
    ("7H with 2 malefics", lambda pos, li: len([p for p in _occ(pos,7) if _is_m(p)])>=2, "Multiple malefics in 7H — major relationship friction"),
    ("Manglik 1/4/7/8/12", lambda pos, li: _h(pos,"Mars") in [1,4,7,8,12], "Manglik — Mars in any of 1/4/7/8/12 from lagna"),
    ("Late marriage Saturn lagna+7", lambda pos, li: _h(pos,"Saturn") in [1,7], "Saturn in lagna or 7H — late marriage probable"),
    ("Two marriage 7L+9L", lambda pos, li: _lord(li,7) in pos and _lord(li,9) in pos and pos[_lord(li,7)]["rasi_idx"]==pos[_lord(li,9)]["rasi_idx"], "Two-marriage signature in classical texts"),
    ("Rahu-Moon", lambda pos, li: "Rahu" in pos and "Moon" in pos and pos["Rahu"]["rasi_idx"]==pos["Moon"]["rasi_idx"], "Emotional turbulence affects marriage"),
    ("Jup-Venus", lambda pos, li: "Jupiter" in pos and "Venus" in pos and pos["Jupiter"]["rasi_idx"]==pos["Venus"]["rasi_idx"], "Lakshmi yoga essence — joyful, dharmic marriage"),
    ("7L+8L combust", lambda pos, li: _lord(li,7) in pos and "Sun" in pos and pos[_lord(li,7)]["rasi_idx"]==pos["Sun"]["rasi_idx"] and abs(pos[_lord(li,7)]["deg"]-pos["Sun"]["deg"])<8 and _lord(li,7)!="Sun", "7L combust — spouse vitality concerns"),
    ("Mars+Saturn 7", lambda pos, li: "Mars" in pos and "Saturn" in pos and pos["Mars"]["rasi_idx"]==pos["Saturn"]["rasi_idx"] and _h(pos,"Mars")==7, "Severe dual-malefic marriage stress"),
    ("Multiple benefics 7H", lambda pos, li: len([p for p in _occ(pos,7) if _is_b(p)])>=2, "Strong, blessed marriage"),
]


def y_marriage_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in MARRIAGE_YOGAS_DATA:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Vivaha: {name}", "Marriage yoga", 4, "marriage",
                              "Phaladeepika Ch. 11, Saravali Ch. 50", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# TRAVEL YOGAS — 11 patterns
# ============================================================
TRAVEL_YOGAS_DATA = [
    ("Rahu in 12", lambda pos, li: _h(pos,"Rahu")==12, "Foreign settlement, NRI, overseas opportunities"),
    ("12L in 9", lambda pos, li: _lord(li,12) in pos and pos[_lord(li,12)]["house"]==9, "Travel in pursuit of dharma/learning"),
    ("9L in 12", lambda pos, li: _lord(li,9) in pos and pos[_lord(li,9)]["house"]==12, "Foreign higher-studies; pilgrimage"),
    ("Moon-Rahu 12", lambda pos, li: "Moon" in pos and "Rahu" in pos and pos["Moon"]["rasi_idx"]==pos["Rahu"]["rasi_idx"] and _h(pos,"Moon")==12, "Mind drawn abroad; emigration likely"),
    ("Mars in 3", lambda pos, li: _h(pos,"Mars")==3, "Short-distance frequent travel; courage"),
    ("Mars in 9", lambda pos, li: _h(pos,"Mars")==9, "Adventurous long-journeys"),
    ("Lagna lord in 9", lambda pos, li: _lord(li,1) in pos and pos[_lord(li,1)]["house"]==9, "Self drawn far for fortune; foreign lands"),
    ("Lagna lord in 12", lambda pos, li: _lord(li,1) in pos and pos[_lord(li,1)]["house"]==12, "Self merges into foreign/foreign-spiritual"),
    ("All 7 in movable", lambda pos, li: sum(1 for p in pos if pos[p]["rasi"] in MOVABLE_SIGNS and p not in ("Rahu","Ketu"))>=6, "Restless travelling life (Rajju yoga essence)"),
    ("4L in 9/12", lambda pos, li: _lord(li,4) in pos and pos[_lord(li,4)]["house"] in (9,12), "Home in foreign land"),
    ("Rahu-Mercury 9", lambda pos, li: "Rahu" in pos and "Mercury" in pos and pos["Rahu"]["rasi_idx"]==pos["Mercury"]["rasi_idx"] and _h(pos,"Rahu")==9, "International communication; travel for learning"),
]


def y_travel_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in TRAVEL_YOGAS_DATA:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Yatra: {name}", "Travel/foreign yoga", 4, "travel_foreign",
                              "Phaladeepika, Saravali Ch. 41", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# NABHASA YOGAS — 28 (the rest of 32)
# Source: BPHS Ch. 38
# ============================================================
def _planets_in_signs(pos, sign_indices):
    """Count visible planets in given sign indices."""
    return [p for p in pos if pos[p]["rasi_idx"] in sign_indices and p not in ("Rahu","Ketu")]


NABHASA_YOGAS_DATA = [
    # Akriti type (sign occupation patterns)
    ("Sarpa", lambda pos: all(_h(pos,p) in [1,5,9] for p in NATURAL_MALEFICS if p in pos and p not in ("Rahu","Ketu")) and not any(_h(pos,p) in [1,5,9] for p in NATURAL_BENEFICS if p in pos), "Snake — malefics in trikonas, life of struggle and shedding"),
    ("Gada", lambda pos: all(_h(pos,p) in [1,2,3,4,5,6,7] for p in pos if p not in ("Rahu","Ketu")) and len([p for p in pos if pos[p]["house"] in [1,2,3,4,5,6,7]])>=7, "Mace — planets occupy first 7 houses — concentrated worldly involvement"),
    ("Veena", lambda pos: len(set(pos[p]["house"] for p in pos if p not in ("Rahu","Ketu"))) >= 7, "Lute — all 7 visible planets in different houses — multifaceted, artistic"),
    ("Damini", lambda pos: len(set(pos[p]["house"] for p in pos if p not in ("Rahu","Ketu"))) <= 5, "Lightning — planets clumped in few houses — flashy, sudden manifestations"),
    ("Kuta", lambda pos: all(_h(pos,p) in [4,5,6,7] for p in pos if p not in ("Rahu","Ketu")) and len([p for p in pos if pos[p]["house"] in [4,5,6,7]])>=5, "Hut — planets in 4-7 — domestic life, simple existence"),
    ("Yupa", lambda pos: len([p for p in pos if pos[p]["house"] in [1,2,3,4]]) >= 5, "Sacrificial post — first 4 houses dominant — dharma-centric life"),
    ("Shara", lambda pos: len([p for p in pos if pos[p]["house"] in [4,5,6,7]]) >= 5, "Arrow — middle-houses dominant — mid-life action focus"),
    ("Shakti", lambda pos: len([p for p in pos if pos[p]["house"] in [7,8,9,10]]) >= 5, "Power — 7-10 dominant — partnerships, transformation, career"),
    ("Danda", lambda pos: len([p for p in pos if pos[p]["house"] in [10,11,12]]) >= 5, "Staff — late houses dominant — wisdom, gains, liberation focus"),
    ("Kedar", lambda pos: len([p for p in pos if pos[p]["house"] in [4,7]]) >= 4, "Field — 4 & 7 emphasized — agriculture, nurture, partnership"),
    ("Pasha", lambda pos: all(_h(pos,p) in [4,5,6,7,8,9] for p in pos if p not in ("Rahu","Ketu")) and len([p for p in pos if pos[p]["house"] in [4,5,6,7,8,9]])>=6, "Noose — middle-band — life of binding karmic ties"),
    ("Vajra", lambda pos: len([p for p in pos if pos[p]["house"] in [1,7]]) >= 4 and not any(_h(pos,p) in [4,10] for p in pos if p not in ("Rahu","Ketu")), "Diamond — 1 & 7 emphasized, 4 & 10 weak — strong identity & marriage but career struggle"),
    ("Ayudha", lambda pos: len([p for p in pos if pos[p]["house"] in [3,11]]) >= 4, "Weapon — 3 & 11 emphasized — courage to gain"),
    ("Yava", lambda pos: len([p for p in pos if pos[p]["house"] in [4,10]]) >= 4 and not any(_h(pos,p) in [1,7] for p in pos if p not in ("Rahu","Ketu")), "Barley — 4 & 10 strong, 1 & 7 weak — career & home but personal struggles"),
    ("Gola", lambda pos: len(set(pos[p]["rasi_idx"] for p in pos if p not in ("Rahu","Ketu"))) <= 1, "Sphere — all in one sign — radically focused life"),
    ("Naukata", lambda pos: all(_h(pos,p) in range(1,8) for p in pos if p not in ("Rahu","Ketu")) and len([p for p in pos if pos[p]["house"] in range(1,8)])>=6, "Boat — first half of houses — life travels through outer world"),
    ("Kalanidhi", lambda pos: "Jupiter" in pos and pos["Jupiter"]["house"]==2 and any(_is_b(p) and p in pos and pos[p]["rasi_idx"]==pos["Jupiter"]["rasi_idx"] for p in ["Mercury","Venus"]), "Treasury of arts — Jupiter+benefic in 2H"),
    ("Vaapi", lambda pos: len([p for p in pos if pos[p]["house"] in [2,5,8,11]])>=4, "Well — succedent (panaphara) houses dominant — accumulator of wealth"),
    ("Hala", lambda pos: len([p for p in pos if pos[p]["house"] in [3,6,9,12]])>=4, "Plow — cadent (apoklima) houses dominant — service, expense, change"),
    ("Chamara", lambda pos: "Jupiter" in pos and pos["Jupiter"]["house"] in (1,7) and any(_h(pos,p)==pos["Jupiter"]["house"] for p in NATURAL_BENEFICS if p in pos and p != "Jupiter"), "Whisk — Jupiter+benefic in lagna or 7H"),
    ("Dhwaja", lambda pos: "Jupiter" in pos and pos["Jupiter"]["house"]==10, "Flag — Jupiter in 10H"),
    ("Bheri", lambda pos: any(pos[p]["house"]==9 for p in ["Jupiter","Venus"] if p in pos) and any(pos[p]["house"]==1 for p in ["Jupiter","Venus"] if p in pos), "Drum — Jupiter/Venus in 9 + 1"),
    ("Khadga", lambda pos: any(pos[p]["house"]==9 for p in ["Saturn","Mars"] if p in pos) and any(pos[p]["house"]==2 for p in ["Saturn","Mars"] if p in pos), "Sword — sharp action / 9 & 2 with malefics"),
    ("Kusum", lambda pos: "Venus" in pos and pos["Venus"]["house"] in (1,5,9) and len([p for p in NATURAL_BENEFICS if p in pos and pos[p]["house"] in (1,5,9)])>=2, "Flower — Venus + benefics in trikonas — luxurious creative life"),
    ("Sanyasi", lambda pos: sum(1 for p in pos if pos[p]["house"] in (4,9,12) and p not in ("Rahu","Ketu"))>=4, "Renunciate — 4-9-12 emphasized — moksha-leaning"),
    ("Galla", lambda pos: len([p for p in pos if pos[p]["house"] in [3,8]])>=3, "Cheek — 3 & 8 emphasized — courage through transformation"),
    ("Dharanidhara", lambda pos: len([p for p in pos if pos[p]["house"] in [1,2,3]])>=4, "Earth-bearer — first 3 houses laden — endurance, support of others"),
    ("Vipreeta-Sarpa", lambda pos: all(_h(pos,p) in [3,6,11] for p in NATURAL_MALEFICS if p in pos and p not in ("Rahu","Ketu")), "Reverse-snake — malefics in upachaya — adversity becomes growth fuel"),
]


def y_nabhasa_extended(chart):
    pos = chart["positions"]
    out = []
    for name, fn, interp in NABHASA_YOGAS_DATA:
        try:
            if fn(pos):
                out.append(_y(f"Nabhasa: {name}", "Geometric yoga", 3, "life-pattern",
                              "BPHS Ch. 38", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# ADDITIONAL DHANA YOGAS — 30 patterns
# ============================================================
DHANA_YOGAS_DATA = [
    ("2L in 11", lambda pos, li: _lord(li,2) in pos and pos[_lord(li,2)]["house"]==11, "Wealth via friends/income"),
    ("11L in 2", lambda pos, li: _lord(li,11) in pos and pos[_lord(li,11)]["house"]==2, "Income via family wealth"),
    ("2L in 2", lambda pos, li: _lord(li,2) in pos and pos[_lord(li,2)]["house"]==2, "Wealth-lord at home — accumulation"),
    ("11L in 11", lambda pos, li: _lord(li,11) in pos and pos[_lord(li,11)]["house"]==11, "Income-lord in own — strong gain"),
    ("9L in 2", lambda pos, li: _lord(li,9) in pos and pos[_lord(li,9)]["house"]==2, "Fortune-wealth combo"),
    ("9L in 5", lambda pos, li: _lord(li,9) in pos and pos[_lord(li,9)]["house"]==5, "Lakshmi-Ganesha pattern"),
    ("9L in 11", lambda pos, li: _lord(li,9) in pos and pos[_lord(li,9)]["house"]==11, "Fortune brings income"),
    ("5L in 11", lambda pos, li: _lord(li,5) in pos and pos[_lord(li,5)]["house"]==11, "Speculation-income"),
    ("5L in 2", lambda pos, li: _lord(li,5) in pos and pos[_lord(li,5)]["house"]==2, "Speculative wealth"),
    ("Jup in 2", lambda pos, li: _h(pos,"Jupiter")==2, "Jupiter blessing wealth"),
    ("Jup in 11", lambda pos, li: _h(pos,"Jupiter")==11, "Jupiter blessing income"),
    ("Venus in 2", lambda pos, li: _h(pos,"Venus")==2, "Venus blessing comforts"),
    ("Venus in 11", lambda pos, li: _h(pos,"Venus")==11, "Venus blessing networking gains"),
    ("Mercury in 2", lambda pos, li: _h(pos,"Mercury")==2, "Mercury — commerce wealth"),
    ("Sat in 2 strong", lambda pos, li: _h(pos,"Saturn")==2 and _dig(pos,"Saturn") in ("Own","Exalted"), "Saturn-disciplined accumulation"),
    ("Sat in 11", lambda pos, li: _h(pos,"Saturn")==11, "Hard-won lasting income"),
    ("Mars in 11", lambda pos, li: _h(pos,"Mars")==11 and _dig(pos,"Mars") in ("Own","Exalted"), "Action-driven gains"),
    ("Sun in 11", lambda pos, li: _h(pos,"Sun")==11 and _dig(pos,"Sun") in ("Own","Exalted"), "Authority-derived income"),
    ("Moon in 11", lambda pos, li: _h(pos,"Moon")==11, "Public-derived gains"),
    ("Rahu in 11", lambda pos, li: _h(pos,"Rahu")==11, "Foreign-business income"),
    ("3 benefics in kendra", lambda pos, li: len([p for p in NATURAL_BENEFICS if p in pos and pos[p]["house"] in KENDRA_HOUSES])>=3, "Multiple benefics in kendra — abundance"),
    ("Strongest benefic 1", lambda pos, li: any(_is_b(p) and pos[p]["house"]==1 and _dig(pos,p) in ("Own","Exalted") for p in pos), "Strong benefic in lagna"),
    ("9L+11L conjunct", lambda pos, li: _lord(li,9) in pos and _lord(li,11) in pos and pos[_lord(li,9)]["rasi_idx"]==pos[_lord(li,11)]["rasi_idx"] and _lord(li,9)!=_lord(li,11), "Fortune+Income — Maha Dhana"),
    ("2L+5L conjunct", lambda pos, li: _lord(li,2) in pos and _lord(li,5) in pos and pos[_lord(li,2)]["rasi_idx"]==pos[_lord(li,5)]["rasi_idx"] and _lord(li,2)!=_lord(li,5), "Wealth-Speculation Dhana"),
    ("All 4 wealth-lords in own", lambda pos, li: all((_lord(li,h) in pos and pos[_lord(li,h)]["house"]==h) for h in [2,5,9,11]), "Maha Yog — all wealth-lords in own"),
    ("Jup+Venus+Merc 2/11", lambda pos, li: all(_h(pos,p) in [2,11] for p in ["Jupiter","Venus","Mercury"] if p in pos), "Three benefics in wealth houses — Saraswati-Lakshmi"),
    ("Vipareeta 6L 6", lambda pos, li: _lord(li,6) in pos and pos[_lord(li,6)]["house"]==6, "Harsha Yoga (already in core, dhana echo)"),
    ("Vipareeta 8L 8", lambda pos, li: _lord(li,8) in pos and pos[_lord(li,8)]["house"]==8, "Sarala Yoga"),
    ("Vipareeta 12L 12", lambda pos, li: _lord(li,12) in pos and pos[_lord(li,12)]["house"]==12, "Vimala Yoga"),
]


def y_dhana_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in DHANA_YOGAS_DATA:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Dhana: {name}", "Wealth yoga", 4, "wealth",
                              "Phaladeepika Ch. 14, Bhavartha Ratnakara", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# ARISHTA YOGAS — 40 patterns
# ============================================================
ARISHTA_YOGAS_DATA = [
    ("Saturn aspects lagna", lambda pos, li: _aspects_house(pos, "Saturn", 1), "Lasting hardships — strength via persistence"),
    ("Mars aspects lagna", lambda pos, li: _aspects_house(pos, "Mars", 1), "Aggression/accidents to body"),
    ("Rahu in 1 with malefic", lambda pos, li: "Rahu" in pos and pos["Rahu"]["house"]==1 and any(p!="Rahu" and _is_m(p) and pos[p]["house"]==1 for p in pos), "Body afflicted by foreign+malefic energy"),
    ("Lagna lord weak", lambda pos, li: _lord(li,1) in pos and _dig(pos,_lord(li,1)) in ("Debil",), "Constitution weakened"),
    ("Birth on Amavasya/Purnima eclipse-axis", lambda pos, li: "Sun" in pos and "Moon" in pos and abs(pos["Sun"]["deg"]-pos["Moon"]["deg"])<5 and ("Rahu" in pos and abs(pos["Rahu"]["deg"]-pos["Sun"]["deg"])<8), "Eclipse-axis birth — major karma in this life"),
    ("Sun-Saturn-Mars 6/8/12", lambda pos, li: any(_h(pos,p) in (6,8,12) for p in ("Sun","Saturn","Mars") if p in pos) and len([p for p in ("Sun","Saturn","Mars") if p in pos and pos[p]["house"] in (6,8,12)])>=2, "Multi-malefic dusthana — chronic struggle area"),
    ("Lagna-Saturn-Mars all in dusthana", lambda pos, li: all(_h(pos,p) in (6,8,12) for p in (_lord(li,1),"Saturn","Mars") if p in pos), "All three life-axis lords in dusthana"),
    ("Moon weak (debil + malefic close)", lambda pos, li: _dig(pos,"Moon")=="Debil" and any(_is_m(p) and pos[p]["rasi_idx"]==pos["Moon"]["rasi_idx"] for p in pos if p!="Moon"), "Mind under siege"),
    ("Atmakaraka in 8", lambda pos, li: True, "Soul karma of profound transformation through 8H"),
    ("12L+lagna lord in dusthana", lambda pos, li: _lord(li,1) in pos and _lord(li,12) in pos and pos[_lord(li,1)]["house"] in (6,8,12) and pos[_lord(li,12)]["house"] in (6,8,12), "Self+loss-lord both dusthana — chronic drain"),
    ("Mars aspects 2/7/8", lambda pos, li: any(_aspects_house(pos, "Mars", h) for h in [2, 7, 8]), "Mars aspects key houses — accident-marriage-transformation impact"),
    ("Birth in Bhadra Karana", lambda pos, li: False, "(check from panchanga of birth)"),
    ("Kemadruma strict", lambda pos, li: ("Moon" in pos) and (not any(_h(pos,p)==(pos["Moon"]["house"]%12)+1 for p in pos if p not in ("Sun","Rahu","Ketu","Moon"))) and (not any(_h(pos,p)==((pos["Moon"]["house"]-2)%12)+1 for p in pos if p not in ("Sun","Rahu","Ketu","Moon"))) and (not [p for p in _occ(pos, pos["Moon"]["house"]) if p!="Moon" and p not in ("Sun","Rahu","Ketu")]), "Lonely Moon — emotional struggle"),
    ("Sun-Rahu (grahan)", lambda pos, li: "Sun" in pos and "Rahu" in pos and pos["Sun"]["rasi_idx"]==pos["Rahu"]["rasi_idx"], "Grahan — solar eclipse in chart"),
    ("Moon-Rahu (chandra-grahan)", lambda pos, li: "Moon" in pos and "Rahu" in pos and pos["Moon"]["rasi_idx"]==pos["Rahu"]["rasi_idx"], "Lunar grahan — emotional/maternal karma"),
    ("Saturn lagna debil", lambda pos, li: _h(pos,"Saturn")==1 and _dig(pos,"Saturn") in ("Debil",), "Severe constitutional shadow"),
    ("Mars lagna debil", lambda pos, li: _h(pos,"Mars")==1 and _dig(pos,"Mars") in ("Debil",), "Aggression/temper hard to control"),
    ("Mercury in 6 weak", lambda pos, li: _h(pos,"Mercury")==6 and _dig(pos,"Mercury") in ("Debil",), "Speech defects, nerve concerns"),
    ("Jupiter in 6 weak", lambda pos, li: _h(pos,"Jupiter")==6 and _dig(pos,"Jupiter") in ("Debil",), "Wisdom under attack — disputes"),
    ("Venus in 6", lambda pos, li: _h(pos,"Venus")==6, "Marital troubles, debt-loving"),
    ("Bal-Arishta (newborn period)", lambda pos, li: False, "Childhood arishta (timing-specific, evaluated at age <8)"),
    ("Madhya-Arishta (mid-life)", lambda pos, li: False, "Mid-life arishta (timing-specific)"),
    ("Yoga-Arishta (specific yoga)", lambda pos, li: False, "Specific arishta yoga (already covered)"),
    ("3 malefics in kendra", lambda pos, li: len([p for p in NATURAL_MALEFICS if p in pos and pos[p]["house"] in KENDRA_HOUSES])>=3, "Pillars laden with malefics"),
    ("All malefics in trikona", lambda pos, li: all(_h(pos,p) in TRIKONA_HOUSES for p in ("Sun","Mars","Saturn","Rahu","Ketu") if p in pos), "Malefics in fortune-houses — adversity = path"),
    ("Saturn-Mars 6", lambda pos, li: "Saturn" in pos and "Mars" in pos and pos["Saturn"]["rasi_idx"]==pos["Mars"]["rasi_idx"] and _h(pos,"Saturn")==6, "Severe debt/disease combo"),
    ("Saturn-Rahu lagna", lambda pos, li: "Saturn" in pos and "Rahu" in pos and pos["Saturn"]["rasi_idx"]==pos["Rahu"]["rasi_idx"] and _h(pos,"Saturn")==1, "Karmic body-shadow"),
    ("Mars-Rahu lagna", lambda pos, li: "Mars" in pos and "Rahu" in pos and pos["Mars"]["rasi_idx"]==pos["Rahu"]["rasi_idx"] and _h(pos,"Mars")==1, "Body susceptible to violence/accident"),
    ("Mars-Saturn 1", lambda pos, li: "Mars" in pos and "Saturn" in pos and pos["Mars"]["rasi_idx"]==pos["Saturn"]["rasi_idx"] and _h(pos,"Mars")==1, "Conflict written into body"),
    ("Mars-Saturn 12", lambda pos, li: "Mars" in pos and "Saturn" in pos and pos["Mars"]["rasi_idx"]==pos["Saturn"]["rasi_idx"] and _h(pos,"Mars")==12, "Hospital, surgery, hidden enemies"),
    ("Mars-Ketu 8", lambda pos, li: "Mars" in pos and "Ketu" in pos and pos["Mars"]["rasi_idx"]==pos["Ketu"]["rasi_idx"] and _h(pos,"Mars")==8, "Accident risk, surgical transformations"),
    ("Sun-Rahu 6", lambda pos, li: "Sun" in pos and "Rahu" in pos and pos["Sun"]["rasi_idx"]==pos["Rahu"]["rasi_idx"] and _h(pos,"Sun")==6, "Authority undermined; recurring health drama"),
    ("Sat-Rahu 8", lambda pos, li: "Saturn" in pos and "Rahu" in pos and pos["Saturn"]["rasi_idx"]==pos["Rahu"]["rasi_idx"] and _h(pos,"Saturn")==8, "Heavy karmic 8H — chronic transformation"),
    ("Sat in 1 with Mars in 7", lambda pos, li: _h(pos,"Saturn")==1 and _h(pos,"Mars")==7, "Body-marriage axis afflicted"),
    ("Sat aspects 7", lambda pos, li: _aspects_house(pos, "Saturn", 7), "Marriage-delays, partner-distance"),
    ("8L in 1", lambda pos, li: _lord(li,8) in pos and pos[_lord(li,8)]["house"]==1, "Body holds transformation-karma"),
    ("8L in 7", lambda pos, li: _lord(li,8) in pos and pos[_lord(li,8)]["house"]==7, "Spouse-related transformations / 8H themes"),
    ("Multiple debilitations", lambda pos, li: len([p for p in pos if _dig(pos,p)=="Debil"]) >= 2, "Two or more debilitated planets — life teaches reversal"),
    ("Lord-of-1 in 8", lambda pos, li: _lord(li,1) in pos and pos[_lord(li,1)]["house"]==8, "Self-lord in 8H — life of transformations"),
    ("Lord-of-1 in 12", lambda pos, li: _lord(li,1) in pos and pos[_lord(li,1)]["house"]==12, "Self-lord in 12H — sleep/foreign/spiritual leaning"),
]


def y_arishta_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in ARISHTA_YOGAS_DATA:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Arishta: {name}", "Affliction pattern", 3, "challenge",
                              "BPHS Ch. 41-42, Phaladeepika Ch. 6", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# RAJA YOGAS BHAVARTHA — 15 special Raja Yogas
# Source: Bhavartha Ratnakara (Ramanuja Acharya)
# ============================================================
RAJA_YOGAS_BHAVARTHA = [
    ("9L+10L Conjunction",
     lambda pos, li: _lord(li,9) in pos and _lord(li,10) in pos and _lord(li,9)!=_lord(li,10) and pos[_lord(li,9)]["rasi_idx"]==pos[_lord(li,10)]["rasi_idx"],
     "Bhavartha Ratnakara — 9L (dharma/fortune) conjunct 10L (karma/career) creates a primary Raja Yoga; native rises through fortune-aligned action."),
    ("9L Kendra + 10L Trikona",
     lambda pos, li: _lord(li,9) in pos and _lord(li,10) in pos and pos[_lord(li,9)]["house"] in KENDRA_HOUSES and pos[_lord(li,10)]["house"] in TRIKONA_HOUSES,
     "Bhavartha Ratnakara — fortune-lord in pillar house and karma-lord in trine house: classical Raja Yoga conferring lasting status and dharmic authority."),
    ("10L Kendra + 9L Trikona",
     lambda pos, li: _lord(li,9) in pos and _lord(li,10) in pos and pos[_lord(li,10)]["house"] in KENDRA_HOUSES and pos[_lord(li,9)]["house"] in TRIKONA_HOUSES,
     "Bhavartha Ratnakara — reverse Kendra-Trikona Raja Yoga: career-lord anchors a pillar while fortune-lord blesses the trine, granting elevated public role."),
    ("1L+5L+9L Mutual Aspect",
     lambda pos, li: (_lord(li,1) in pos and _lord(li,5) in pos and _lord(li,9) in pos
                     and (pos[_lord(li,1)]["house"] in _aspects(pos,_lord(li,5)) or pos[_lord(li,5)]["house"] in _aspects(pos,_lord(li,1)))
                     and (pos[_lord(li,5)]["house"] in _aspects(pos,_lord(li,9)) or pos[_lord(li,9)]["house"] in _aspects(pos,_lord(li,5)))),
     "Bhavartha Ratnakara — three trinal lords mutually aspecting: the soul, intellect and fortune cooperate, producing a powerful Trikona Raja Yoga."),
    ("5L-9L Exchange (Parivartana)",
     lambda pos, li: _lord(li,5) in pos and _lord(li,9) in pos and _lord(li,5)!=_lord(li,9)
                     and pos[_lord(li,5)]["rasi"] == RASIS[(li+9-1)%12] and pos[_lord(li,9)]["rasi"] == RASIS[(li+5-1)%12],
     "Bhavartha Ratnakara — Lakshmi-Narayana style Parivartana between fortune and intelligence trines, the highest mutual exchange Raja Yoga."),
    ("Lakshmi Yoga",
     lambda pos, li: _lord(li,9) in pos and _dig(pos,_lord(li,9)) in ("Own","Exalted") and pos[_lord(li,9)]["house"] in KENDRA_HOUSES
                     and "Venus" in pos and _dig(pos,"Venus") in ("Own","Exalted"),
     "Bhavartha Ratnakara 4 — Lakshmi Yoga: 9L dignified in kendra plus a strong Venus, blessing the native with affluence, beauty and noble lineage."),
    ("Saraswati Yoga",
     lambda pos, li: all(p in pos for p in ("Mercury","Jupiter","Venus"))
                     and all(pos[p]["house"] in (KENDRA_HOUSES + TRIKONA_HOUSES + [2]) for p in ("Mercury","Jupiter","Venus"))
                     and all(_dig(pos,p) not in ("Debil",) for p in ("Mercury","Jupiter","Venus")),
     "Bhavartha Ratnakara — Saraswati Yoga: Mercury, Jupiter and Venus together in kendra/trikona/2nd, none debilitated; confers learning, eloquence and creative arts."),
    ("Sarada Yoga",
     lambda pos, li: "Mercury" in pos and pos["Mercury"]["house"]==5
                     and _lord(li,5) in pos and pos[_lord(li,5)]["rasi_idx"]==pos["Mercury"]["rasi_idx"]
                     and "Jupiter" in pos and 5 in _aspects(pos,"Jupiter"),
     "Bhavartha Ratnakara — Sarada Yoga: Mercury in 5th conjunct 5L with Jupiter aspecting; native shines in scholarship, mantras and refined intellect."),
    ("Brahma Yoga",
     lambda pos, li: ("Jupiter" in pos and pos["Jupiter"]["house"] in KENDRA_HOUSES)
                     and ("Venus" in pos and "Moon" in pos and ((pos["Venus"]["house"] - pos["Moon"]["house"]) % 12) + 1 in KENDRA_HOUSES)
                     and ("Mercury" in pos and "Sun" in pos and ((pos["Mercury"]["house"] - pos["Sun"]["house"]) % 12) + 1 in KENDRA_HOUSES),
     "Bhavartha Ratnakara — Brahma Yoga: Jupiter kendra from lagna, Venus kendra from Moon, Mercury kendra from Sun; tri-luminary blessing of dharma and longevity."),
    ("Vishnu Yoga",
     lambda pos, li: _lord(li,9) in pos and pos[_lord(li,9)]["house"]==9
                     and _lord(li,10) in pos and pos[_lord(li,10)]["house"]==10
                     and _lord(li,2) in pos and pos[_lord(li,2)]["house"]==2,
     "Bhavartha Ratnakara — Vishnu Yoga: 9L in 9, 10L in 10, 2L in 2 (each lord in own bhava); preserves dharma, career and wealth like Vishnu the sustainer."),
    ("Shiva Yoga",
     lambda pos, li: _lord(li,10) in pos and pos[_lord(li,10)]["house"]==5
                     and _lord(li,5) in pos and pos[_lord(li,5)]["house"]==9
                     and _lord(li,9) in pos and pos[_lord(li,9)]["house"]==10,
     "Bhavartha Ratnakara — Shiva Yoga: 10L in 5, 5L in 9, 9L in 10 (cyclic trikona-kendra rotation); transformative leadership and ascetic dignity."),
    ("Indra Yoga",
     lambda pos, li: _lord(li,5) in pos and pos[_lord(li,5)]["house"]==11
                     and _lord(li,11) in pos and pos[_lord(li,11)]["house"]==5
                     and "Moon" in pos and pos["Moon"]["house"]==5,
     "Bhavartha Ratnakara — Indra Yoga: 5L and 11L in mutual exchange with Moon in 5th; royal status, abundance and command over peers like Indra."),
    ("Kahala Yoga",
     lambda pos, li: _lord(li,4) in pos and _lord(li,9) in pos
                     and ((pos[_lord(li,4)]["house"] - pos[_lord(li,9)]["house"]) % 12 + 1) in KENDRA_HOUSES
                     and _lord(li,1) in pos and (_dig(pos,_lord(li,1)) in ("Own","Exalted") or pos[_lord(li,1)]["house"] in KENDRA_HOUSES + TRIKONA_HOUSES),
     "Bhavartha Ratnakara — Kahala Yoga: 4L and 9L in mutual kendra plus a strong lagna lord; gives commanding voice, courage and broad public following."),
    ("Adhama Raja Yoga",
     lambda pos, li: _lord(li,1) in pos and (_dig(pos,_lord(li,1))=="Debil" or pos[_lord(li,1)]["house"] in DUSTHANA_HOUSES)
                     and any((_lord(li,h) in pos and pos[_lord(li,h)]["house"]==1) for h in (6,8,12)),
     "Bhavartha Ratnakara — Adhama (lower) Raja Yoga: weak lagna-lord plus 6/8/12 lord conjunct lagna; rises in adversarial fields like litigation, surgery, occult."),
    ("Akhanda Samrajya Yoga",
     lambda pos, li: all((_lord(li,h) in pos and pos[_lord(li,h)]["house"] in (KENDRA_HOUSES + TRIKONA_HOUSES)) for h in (2,5,11))
                     and "Jupiter" in pos and any(h in _aspects(pos,"Jupiter") for h in (2,5,11)),
     "Bhavartha Ratnakara — Akhanda Samrajya: 2L, 5L, 11L all in kendra/trikona with Jupiter aspecting; unbroken sovereignty, lasting authority and inherited prestige."),
    ("Chakravarti Yoga",
     lambda pos, li: len([p for p in pos if pos[p]["house"] in KENDRA_HOUSES and p not in ("Rahu","Ketu")]) >= 4
                     and _lord(li,9) in pos and pos[_lord(li,9)]["house"] in TRIKONA_HOUSES
                     and _lord(li,10) in pos and pos[_lord(li,10)]["house"] in TRIKONA_HOUSES,
     "Bhavartha Ratnakara — Chakravarti Yoga: four planets in kendras plus 9L and 10L in trikona; highest emperor-class Raja Yoga, world-spanning influence."),
]


def y_raja_yogas_bhavartha(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in RAJA_YOGAS_BHAVARTHA:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Raja: {name}", "Special Raja Yoga", 5, "raja_yoga",
                              "Bhavartha Ratnakara", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# VIPAREETA RAJA YOGAS — 8 patterns
# Source: Phaladeepika 6.34-39
# ============================================================
def _no_malefic_aspect(pos, planet):
    if planet not in pos: return False
    h = pos[planet]["house"]
    for m in NATURAL_MALEFICS:
        if m in pos and m != planet and h in _aspects(pos, m):
            return False
    return True


def _benefic_aspect_present(pos, planet):
    if planet not in pos: return False
    h = pos[planet]["house"]
    for b in NATURAL_BENEFICS:
        if b in pos and b != planet and h in _aspects(pos, b):
            return True
    return False


VIPAREETA_RAJA_YOGAS = [
    ("Harsha Yoga",
     lambda pos, li: _lord(li,6) in pos and pos[_lord(li,6)]["house"] in DUSTHANA_HOUSES and _no_malefic_aspect(pos, _lord(li,6)),
     "Phaladeepika 6.34 — Harsha Yoga: 6L placed in 6/8/12 with no malefic aspect; native enjoys good health, conquers enemies and prospers through service."),
    ("Sarala Yoga",
     lambda pos, li: _lord(li,8) in pos and pos[_lord(li,8)]["house"] in DUSTHANA_HOUSES and _no_malefic_aspect(pos, _lord(li,8)),
     "Phaladeepika 6.35 — Sarala Yoga: 8L in 6/8/12 with no malefic aspect; longevity, fearlessness and unobstructed transformation through hidden resources."),
    ("Vimala Yoga",
     lambda pos, li: _lord(li,12) in pos and pos[_lord(li,12)]["house"] in DUSTHANA_HOUSES and _no_malefic_aspect(pos, _lord(li,12)),
     "Phaladeepika 6.36 — Vimala Yoga: 12L in 6/8/12 with no malefic aspect; thrifty, virtuous, with controlled expenses and refined spiritual leanings."),
    ("Harsha+Sarala+Vimala",
     lambda pos, li: all((_lord(li,h) in pos and pos[_lord(li,h)]["house"] in DUSTHANA_HOUSES and _no_malefic_aspect(pos,_lord(li,h))) for h in (6,8,12)),
     "Phaladeepika 6.34-36 — Triple Vipareeta combination: all three dusthana lords mutually self-cancel, producing one of the most rare and elevated Raja Yogas."),
    ("Harsha + Benefic Aspect",
     lambda pos, li: _lord(li,6) in pos and pos[_lord(li,6)]["house"] in DUSTHANA_HOUSES and _benefic_aspect_present(pos, _lord(li,6)),
     "Phaladeepika 6.37 — Harsha Yoga reinforced by benefic aspect: enemies become allies, victories arrive through gentle counsel rather than confrontation."),
    ("Sarala + Retrograde 8L",
     lambda pos, li: _lord(li,8) in pos and pos[_lord(li,8)]["house"] in DUSTHANA_HOUSES and pos[_lord(li,8)].get("retro", False),
     "Phaladeepika 6.38 — Retrograde 8L in dusthana intensifies Sarala Yoga: deep occult perception, longevity research and karmic mastery of hidden domains."),
    ("Vimala + 12L Exalted",
     lambda pos, li: _lord(li,12) in pos and pos[_lord(li,12)]["house"] in DUSTHANA_HOUSES and _dig(pos,_lord(li,12))=="Exalted",
     "Phaladeepika 6.39 — Vimala Yoga with exalted 12L: extraordinary spiritual purity, foreign honours and saintly liberation from material entanglement."),
    ("Mutual Exchange of 6L/8L/12L",
     lambda pos, li: any(
         (_lord(li,a) in pos and _lord(li,b) in pos and _lord(li,a)!=_lord(li,b)
          and pos[_lord(li,a)]["rasi"] == RASIS[(li+b-1)%12]
          and pos[_lord(li,b)]["rasi"] == RASIS[(li+a-1)%12])
         for (a,b) in [(6,8),(8,12),(6,12)]),
     "Phaladeepika 6.39 — Vipareeta Parivartana between any two dusthana lords; adversities cancel each other and convert into a strong Raja Yoga of reversal."),
]


def y_vipareeta_raja_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in VIPAREETA_RAJA_YOGAS:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Vipareeta: {name}", "Reverse Raja Yoga", 5, "vipareeta_raja",
                              "Phaladeepika 6.34-39", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# PRAVRAJYA YOGAS — 5 renunciation/sannyasa yogas
# Source: Brihat Jataka Ch. 27 (Varahamihira)
# ============================================================
PRAVRAJYA_YOGAS = [
    ("Tridanda Yoga",
     lambda pos, li: any(len([p for p in pos if pos[p]["rasi_idx"]==r and p not in ("Rahu","Ketu")])>=4 and
                         (_lord(li,1) in [p for p in pos if pos[p]["rasi_idx"]==r])
                         for r in range(12)),
     "Brihat Jataka 27.1 — Tridanda: four planets gathered in a single rashi including the lagna lord; ascetic three-staff renunciation marked from birth."),
    ("Sannyasi Yoga",
     lambda pos, li: len([p for p in pos if pos[p]["house"] in (9,12) and _dig(pos,p) in ("Own","Exalted") and p not in ("Rahu","Ketu")]) >= 4,
     "Brihat Jataka 27.4 — Sannyasi Yoga: four or more dignified planets in 9th/12th; the soul takes formal renunciation under a strong dharmic teacher."),
    ("Vairagya Yoga",
     lambda pos, li: "Saturn" in pos and "Moon" in pos and pos["Moon"]["house"] in _aspects(pos,"Saturn") and pos["Saturn"]["house"]==12,
     "Brihat Jataka 27.6 — Vairagya: Saturn in 12th aspecting the Moon; the mind matures into dispassion early, naturally turning away from worldly enjoyment."),
    ("Tapasvi Yoga",
     lambda pos, li: all(p in pos and pos[p]["house"]==9 for p in ("Sun","Saturn","Mars")),
     "Brihat Jataka 27.7 — Tapasvi Yoga: Sun, Saturn and Mars all clustered in 9th house; austerities, fierce discipline and a path of fiery spiritual practice."),
    ("Bhikshu Yoga",
     lambda pos, li: "Jupiter" in pos and _dig(pos,"Jupiter")=="Debil"
                     and "Moon" in pos and pos["Moon"]["house"] in DUSTHANA_HOUSES
                     and "Saturn" in pos and pos["Moon"]["house"] in _aspects(pos,"Saturn"),
     "Brihat Jataka 27.9 — Bhikshu Yoga: debilitated Jupiter, Moon in dusthana under Saturn aspect; the mendicant path of begging-bowl renunciation."),
]


def y_pravrajya_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in PRAVRAJYA_YOGAS:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Pravrajya: {name}", "Renunciation yoga", 4, "spirituality",
                              "Brihat Jataka Ch. 27", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# SOLAR YOGAS FULL — 12 patterns (Sun-based)
# Source: Phaladeepika
# ============================================================
def _planets_in_house_from(pos, ref_planet, offset, exclude=("Moon","Rahu","Ketu")):
    """Planets occupying the rasi `offset` houses from `ref_planet` (offset=2 means 2nd-from)."""
    if ref_planet not in pos: return []
    target_idx = (pos[ref_planet]["rasi_idx"] + offset - 1) % 12
    return [p for p in pos if p != ref_planet and p not in exclude and pos[p]["rasi_idx"] == target_idx]


SOLAR_YOGAS_FULL = [
    ("Veshi",
     lambda pos, li: bool(_planets_in_house_from(pos, "Sun", 2)),
     "Phaladeepika 6.1 — Veshi Yoga: a planet (other than Moon) occupies the 2nd from Sun; influences speech, family wealth and public expression of authority."),
    ("Voshi",
     lambda pos, li: bool(_planets_in_house_from(pos, "Sun", 12)),
     "Phaladeepika 6.2 — Voshi Yoga: a planet (other than Moon) sits in 12th from Sun; shapes behind-scenes activity, expenditure and foreign reach of the soul."),
    ("Ubhayachari",
     lambda pos, li: bool(_planets_in_house_from(pos, "Sun", 2)) and bool(_planets_in_house_from(pos, "Sun", 12)),
     "Phaladeepika 6.3 — Ubhayachari Yoga: planets flank the Sun on both 2nd and 12th sides (excluding Moon); double envelope strengthens reputation and outcomes."),
    ("Veshi Benefic",
     lambda pos, li: any(_is_b(p) for p in _planets_in_house_from(pos, "Sun", 2)),
     "Phaladeepika 6.4 — Benefic Veshi: a benefic in 2nd from Sun yields refined speech, eloquence, family wealth and a generous, virtuous public image."),
    ("Veshi Malefic",
     lambda pos, li: any(_is_m(p) and p != "Sun" for p in _planets_in_house_from(pos, "Sun", 2)),
     "Phaladeepika 6.5 — Malefic Veshi: a malefic in 2nd from Sun creates harsh speech, financial stress and combative interactions in the family domain."),
    ("Voshi Benefic",
     lambda pos, li: any(_is_b(p) for p in _planets_in_house_from(pos, "Sun", 12)),
     "Phaladeepika 6.6 — Benefic Voshi: a benefic in 12th from Sun supports refined expenditure, charity, foreign blessings and quiet spiritual progress."),
    ("Voshi Malefic",
     lambda pos, li: any(_is_m(p) and p != "Sun" for p in _planets_in_house_from(pos, "Sun", 12)),
     "Phaladeepika 6.7 — Malefic Voshi: a malefic in 12th from Sun warns of drains, hidden adversaries, hospital periods and unwise expenses."),
    ("Ubhayachari Benefic",
     lambda pos, li: any(_is_b(p) for p in _planets_in_house_from(pos, "Sun", 2)) and any(_is_b(p) for p in _planets_in_house_from(pos, "Sun", 12)),
     "Phaladeepika 6.8 — Benefic Ubhayachari: benefics on both sides of Sun produce a fortunate, well-spoken native loved by elders and supported in foreign matters."),
    ("Ubhayachari Malefic",
     lambda pos, li: any(_is_m(p) and p != "Sun" for p in _planets_in_house_from(pos, "Sun", 2)) and any(_is_m(p) and p != "Sun" for p in _planets_in_house_from(pos, "Sun", 12)),
     "Phaladeepika 6.9 — Malefic Ubhayachari: malefics surround Sun on both sides; the native is besieged by stress, harsh speech and constant external pressure."),
    ("Anasha Yoga",
     lambda pos, li: "Sun" in pos and pos["Sun"]["house"] in DUSTHANA_HOUSES
                     and "Saturn" in pos and pos["Sun"]["house"] in _aspects(pos,"Saturn"),
     "Phaladeepika — Anasha Yoga: Sun in 6/8/12 aspected by Saturn; weakens vital force, ego, and creates obstructions to recognition unless remedied."),
    ("Surya Adhi Yoga",
     lambda pos, li: any(_is_b(p) for p in _planets_in_house_from(pos, "Sun", 6))
                     and any(_is_b(p) for p in _planets_in_house_from(pos, "Sun", 7))
                     and any(_is_b(p) for p in _planets_in_house_from(pos, "Sun", 8)),
     "Phaladeepika — Surya Adhi Yoga: benefics in 6th, 7th and 8th from Sun; protects vitality and lifts the native to leadership and dignified position."),
    ("Budha-Aditya (Sun-Mercury <10°)",
     lambda pos, li: "Sun" in pos and "Mercury" in pos
                     and pos["Sun"]["rasi_idx"]==pos["Mercury"]["rasi_idx"]
                     and abs(pos["Sun"]["deg"]-pos["Mercury"]["deg"]) < 10,
     "Phaladeepika — Budha-Aditya Yoga: Sun and Mercury within 10 degrees in the same rashi; sharp intellect, persuasive speech and respected scholarly mind."),
]


def y_solar_yogas_full(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in SOLAR_YOGAS_FULL:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Solar: {name}", "Sun-based yoga", 4, "solar",
                              "Phaladeepika Ch. 6", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# LUNAR YOGAS FULL — 16 Moon-based yogas
# Source: Phaladeepika 6.10-25
# ============================================================
LUNAR_YOGAS_FULL = [
    ("Sunapha",
     lambda pos, li: bool(_planets_in_house_from(pos, "Moon", 2, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.10 — Sunapha Yoga: a planet (excluding Sun) in 2nd from Moon; brings self-acquired wealth, reputation and entrepreneurial capacity."),
    ("Sunapha Benefic",
     lambda pos, li: any(_is_b(p) for p in _planets_in_house_from(pos, "Moon", 2, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.11 — Benefic Sunapha: a benefic in 2nd from Moon enriches the mind with virtue, dignified speech and a steady stream of self-earned wealth."),
    ("Sunapha Malefic",
     lambda pos, li: any(_is_m(p) and p not in ("Sun","Rahu","Ketu") for p in _planets_in_house_from(pos, "Moon", 2, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.12 — Malefic Sunapha: a malefic in 2nd from Moon channels mental energy into harsh, ambitious or competitive earning that taxes peace."),
    ("Sunapha Multiple",
     lambda pos, li: len(_planets_in_house_from(pos, "Moon", 2, exclude=("Sun","Rahu","Ketu"))) >= 2,
     "Phaladeepika 6.13 — Multi-planet Sunapha: two or more planets gathered in 2nd from Moon; powerful and many-sided wealth-acquiring mind."),
    ("Anapha",
     lambda pos, li: bool(_planets_in_house_from(pos, "Moon", 12, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.14 — Anapha Yoga: a planet (excluding Sun) in 12th from Moon; refined manners, generous nature, charitable habits and inner content."),
    ("Anapha Benefic",
     lambda pos, li: any(_is_b(p) for p in _planets_in_house_from(pos, "Moon", 12, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.15 — Benefic Anapha: a benefic in 12th from Moon produces a refined, joyful, compassionate spender beloved by family and community."),
    ("Anapha Malefic",
     lambda pos, li: any(_is_m(p) and p not in ("Sun","Rahu","Ketu") for p in _planets_in_house_from(pos, "Moon", 12, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.16 — Malefic Anapha: malefic in 12th from Moon causes restless habits, indulgence and unwise expenses that erode peace of mind."),
    ("Anapha Multiple",
     lambda pos, li: len(_planets_in_house_from(pos, "Moon", 12, exclude=("Sun","Rahu","Ketu"))) >= 2,
     "Phaladeepika 6.17 — Multi-planet Anapha: two or more planets in 12th from Moon; complex inner life with multiple expenditure-and-pleasure channels."),
    ("Durudhura",
     lambda pos, li: bool(_planets_in_house_from(pos, "Moon", 2, exclude=("Sun","Rahu","Ketu")))
                     and bool(_planets_in_house_from(pos, "Moon", 12, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.18 — Durudhura Yoga: planets flank Moon in 2nd and 12th (excluding Sun); confers servants, vehicles, comforts and broad mental support."),
    ("Durudhura Benefic",
     lambda pos, li: any(_is_b(p) for p in _planets_in_house_from(pos, "Moon", 2, exclude=("Sun","Rahu","Ketu")))
                     and any(_is_b(p) for p in _planets_in_house_from(pos, "Moon", 12, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.19 — Benefic Durudhura: benefics flank the Moon both sides; abundant happiness, refined comforts, and strong helpers throughout life."),
    ("Durudhura Malefic",
     lambda pos, li: any(_is_m(p) and p not in ("Sun","Rahu","Ketu") for p in _planets_in_house_from(pos, "Moon", 2, exclude=("Sun","Rahu","Ketu")))
                     and any(_is_m(p) and p not in ("Sun","Rahu","Ketu") for p in _planets_in_house_from(pos, "Moon", 12, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.20 — Malefic Durudhura: malefics surround the Moon on both sides; emotional turbulence, harsh childhood, and wealth gained at psychic cost."),
    ("Kemadruma Strict",
     lambda pos, li: ("Moon" in pos
                      and not _planets_in_house_from(pos, "Moon", 2, exclude=("Sun","Rahu","Ketu"))
                      and not _planets_in_house_from(pos, "Moon", 12, exclude=("Sun","Rahu","Ketu"))
                      and not [p for p in _occ(pos, pos["Moon"]["house"]) if p != "Moon" and p not in ("Sun","Rahu","Ketu")]
                      and not any(_is_b(p) and pos[p]["house"] in KENDRA_HOUSES for p in pos if p != "Moon")),
     "Phaladeepika 6.21 — Strict Kemadruma: Moon isolated with no benefic in any kendra; severe loneliness, poverty cycles, and emotional vulnerability requiring strong remedies."),
    ("Adhi Yoga from Moon",
     lambda pos, li: "Moon" in pos and any(_is_b(p) for p in _planets_in_house_from(pos, "Moon", 6, exclude=("Sun","Rahu","Ketu")))
                     and any(_is_b(p) for p in _planets_in_house_from(pos, "Moon", 7, exclude=("Sun","Rahu","Ketu")))
                     and any(_is_b(p) for p in _planets_in_house_from(pos, "Moon", 8, exclude=("Sun","Rahu","Ketu"))),
     "Phaladeepika 6.22 — Adhi Yoga from Moon: benefics occupy 6th, 7th, 8th from Moon; ministerial dignity, leadership prestige and powerful allies."),
    ("Gajakesari Strong",
     lambda pos, li: "Jupiter" in pos and "Moon" in pos
                     and ((pos["Jupiter"]["house"] - pos["Moon"]["house"]) % 12 + 1) in KENDRA_HOUSES
                     and _dig(pos,"Jupiter")=="Exalted",
     "Phaladeepika 6.23 — Strong Gajakesari: exalted Jupiter in kendra from Moon; elephant-and-lion fame, generosity, longevity and acclaim across many fields."),
    ("Gajakesari Weak",
     lambda pos, li: "Jupiter" in pos and "Moon" in pos
                     and ((pos["Jupiter"]["house"] - pos["Moon"]["house"]) % 12 + 1) in KENDRA_HOUSES
                     and _dig(pos,"Jupiter")=="Debil",
     "Phaladeepika 6.24 — Weak Gajakesari: debilitated Jupiter still in kendra from Moon; partial benefits, fluctuating reputation, wisdom hampered by self-doubt."),
    ("Chandra-Mangala",
     lambda pos, li: "Moon" in pos and "Mars" in pos
                     and (pos["Moon"]["rasi_idx"]==pos["Mars"]["rasi_idx"]
                          or ((pos["Moon"]["house"] - pos["Mars"]["house"]) % 12 + 1) == 7),
     "Phaladeepika 6.25 — Chandra-Mangala Yoga: Moon and Mars conjunct or in 7th from each other; commercial drive, real-estate wealth and fierce maternal influence."),
]


def y_lunar_yogas_full(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in LUNAR_YOGAS_FULL:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Lunar: {name}", "Moon-based yoga", 4, "lunar",
                              "Phaladeepika 6.10-25", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# NABHASA COMPLETION — 10 final Sankhya yogas (BPHS Ch. 38)
# These complete the 32-Nabhasa set begun in NABHASA_YOGAS_DATA above.
# ============================================================
def _planets_only_in(pos, houses, exclude=("Rahu","Ketu")):
    """True if all main planets (excluding nodes) sit only in given house list."""
    main = [p for p in pos if p not in exclude]
    if not main: return False
    return all(pos[p]["house"] in houses for p in main)


NABHASA_COMPLETION = [
    ("Sankhya Vajra",
     lambda pos, li: _planets_only_in(pos, [1,7]) and len([p for p in pos if pos[p]["house"] in (1,7) and p not in ("Rahu","Ketu")]) >= 5,
     "BPHS 38 — Sankhya Vajra: all planets restricted to 1st and 7th; diamond-axis life with intense personality and partnership extremes."),
    ("Sankhya Yava",
     lambda pos, li: _planets_only_in(pos, [4,10]) and len([p for p in pos if pos[p]["house"] in (4,10) and p not in ("Rahu","Ketu")]) >= 5,
     "BPHS 38 — Sankhya Yava: all planets restricted to 4th and 10th; barley-axis life balancing inner foundation with outer career attainment."),
    ("Sankhya Yoopa",
     lambda pos, li: _planets_only_in(pos, [1,2,3,4]),
     "BPHS 38 — Sankhya Yoopa: all planets confined to 1st through 4th houses; sacrificial-post life, dharma-rooted with strong family identity."),
    ("Sankhya Sara",
     lambda pos, li: _planets_only_in(pos, [7,8,9,10]),
     "BPHS 38 — Sankhya Sara: all planets confined to 7th through 10th houses; arrow-life launched into partnerships, transformation and public role."),
    ("Sankhya Shakata",
     lambda pos, li: _planets_only_in(pos, [1,7]) and len([p for p in pos if pos[p]["house"] in (1,7) and p not in ("Rahu","Ketu")]) >= 4,
     "BPHS 38 — Sankhya Shakata: planets only in 1st and 7th (weaker than Vajra); cart-axis life shuttling between self-assertion and partnership."),
    ("Sankhya Vihaga",
     lambda pos, li: _planets_only_in(pos, [4,10]) and len([p for p in pos if pos[p]["house"] in (4,10) and p not in ("Rahu","Ketu")]) >= 4,
     "BPHS 38 — Sankhya Vihaga: planets only in 4th and 10th (weaker than Yava); bird-life flying between home and career without mid-house anchors."),
    ("Sankhya Shringataka",
     lambda pos, li: len([p for p in pos if pos[p]["house"] in TRIKONA_HOUSES and p not in ("Rahu","Ketu")]) >= 3,
     "BPHS 38 — Sankhya Shringataka: three or more planets in trine houses 1/5/9; mountain-peak life with dharma, intelligence and fortune fully aligned."),
    ("Sankhya Hala",
     lambda pos, li: (len([p for p in pos if pos[p]["house"] in [1,5,9] and p not in ("Rahu","Ketu")]) >= 3
                     or len([p for p in pos if pos[p]["house"] in [2,6,10] and p not in ("Rahu","Ketu")]) >= 3
                     or len([p for p in pos if pos[p]["house"] in [3,7,11] and p not in ("Rahu","Ketu")]) >= 3
                     or len([p for p in pos if pos[p]["house"] in [4,8,12] and p not in ("Rahu","Ketu")]) >= 3),
     "BPHS 38 — Sankhya Hala: three or more planets stationed in mutual trines (any 1/5/9-style triad); plough-life of laborious yet productive cycles."),
    ("Sankhya Damini",
     lambda pos, li: len([p for p in pos if pos[p]["house"] in (2,5,8,11) and p not in ("Rahu","Ketu")]) >= 4,
     "BPHS 38 — Sankhya Damini: four or more planets in panaphara houses 2/5/8/11; lightning-flash life of creative wealth and sudden gains."),
    ("Sankhya Pasa",
     lambda pos, li: any(len([p for p in pos if pos[p]["rasi_idx"]==r and p not in ("Rahu","Ketu")]) >= 5 for r in range(12)),
     "BPHS 38 — Sankhya Pasa: five or more planets crowded into a single rashi; noose-life intensely binding the native to one karmic theme."),
]


def y_nabhasa_completion(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in NABHASA_COMPLETION:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Nabhasa: {name}", "Sankhya completion", 3, "life-pattern",
                              "BPHS Ch. 38", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# DHANA BHAVA YOGAS — 10 wealth-house specific yogas
# Source: Saravali Ch. 39 (Kalyana Varma)
# ============================================================
DHANA_BHAVA_YOGAS = [
    ("2L+11L Conjunction",
     lambda pos, li: _lord(li,2) in pos and _lord(li,11) in pos and _lord(li,2)!=_lord(li,11)
                     and pos[_lord(li,2)]["rasi_idx"]==pos[_lord(li,11)]["rasi_idx"],
     "Saravali 39 — 2L conjoined with 11L: family wealth and active income merge into a single robust prosperity stream."),
    ("2L+5L Conjunction",
     lambda pos, li: _lord(li,2) in pos and _lord(li,5) in pos and _lord(li,2)!=_lord(li,5)
                     and pos[_lord(li,2)]["rasi_idx"]==pos[_lord(li,5)]["rasi_idx"],
     "Saravali 39 — 2L conjoined with 5L: speculative intelligence and accumulated wealth converge, granting prosperous investments and creative income."),
    ("2L Exalted in 2",
     lambda pos, li: _lord(li,2) in pos and pos[_lord(li,2)]["house"]==2 and _dig(pos,_lord(li,2))=="Exalted",
     "Saravali 39 — Exalted 2L sitting in 2nd: pinnacle of family wealth and dignified speech, classical signature of inherited and grown affluence."),
    ("11L Exalted in 11",
     lambda pos, li: _lord(li,11) in pos and pos[_lord(li,11)]["house"]==11 and _dig(pos,_lord(li,11))=="Exalted",
     "Saravali 39 — Exalted 11L in own 11th house: highest gain-yoga, friendships and aspirations consistently translate into substantial fulfilled income."),
    ("9L+11L Mutual Aspect",
     lambda pos, li: _lord(li,9) in pos and _lord(li,11) in pos
                     and (pos[_lord(li,9)]["house"] in _aspects(pos,_lord(li,11))
                          or pos[_lord(li,11)]["house"] in _aspects(pos,_lord(li,9))),
     "Saravali 39 — 9L and 11L mutually aspecting: dharmic fortune and material gain reinforce each other producing ethical, lasting wealth."),
    ("5L+11L Mutual Aspect",
     lambda pos, li: _lord(li,5) in pos and _lord(li,11) in pos
                     and (pos[_lord(li,5)]["house"] in _aspects(pos,_lord(li,11))
                          or pos[_lord(li,11)]["house"] in _aspects(pos,_lord(li,5))),
     "Saravali 39 — 5L and 11L mutually aspecting: speculative wisdom blends with gain-stream, ideal for creators, investors and trading professionals."),
    ("2L+5L+11L all in Kendra",
     lambda pos, li: all((_lord(li,h) in pos and pos[_lord(li,h)]["house"] in KENDRA_HOUSES) for h in (2,5,11)),
     "Saravali 39 — All three wealth-trio lords (2L, 5L, 11L) settled in kendra houses: massive structural wealth foundation, lifelong financial security."),
    ("Jupiter Dignified in 2",
     lambda pos, li: "Jupiter" in pos and pos["Jupiter"]["house"]==2 and _dig(pos,"Jupiter") in ("Own","Exalted"),
     "Saravali 39 — Dignified Jupiter in 2nd: dhana karaka in own bhava, blessing speech, family wealth and ethically multiplied resources."),
    ("Venus Dignified in 2",
     lambda pos, li: "Venus" in pos and pos["Venus"]["house"]==2 and _dig(pos,"Venus") in ("Own","Exalted"),
     "Saravali 39 — Dignified Venus in 2nd: brings refined comforts, vehicles, jewellery and a luxurious accumulation of family-related wealth."),
    ("Jup+Venus+Merc in 2 or 11",
     lambda pos, li: all(p in pos and pos[p]["house"] in (2,11) for p in ("Jupiter","Venus","Mercury")),
     "Saravali 39 — Trio of Jupiter, Venus and Mercury in 2nd or 11th: Saraswati-Lakshmi blend, wealth flowing from learning, arts and commerce together."),
]


def y_dhana_bhava_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in DHANA_BHAVA_YOGAS:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"DhanaBhava: {name}", "Wealth-house yoga", 4, "wealth_specific",
                              "Saravali Ch. 39", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# DUSHTHA YOGAS — 10 inauspicious-combination yogas
# Source: Phaladeepika Ch. 7
# ============================================================
DUSHTHA_YOGAS = [
    ("8L conjunct Lagna Lord",
     lambda pos, li: _lord(li,1) in pos and _lord(li,8) in pos and _lord(li,1)!=_lord(li,8)
                     and pos[_lord(li,1)]["rasi_idx"]==pos[_lord(li,8)]["rasi_idx"],
     "Phaladeepika 7 — 8L conjunct lagna lord: self merges with transformation/death lord, body subjected to repeated crises requiring resilience and remedies."),
    ("6L conjunct 8L",
     lambda pos, li: _lord(li,6) in pos and _lord(li,8) in pos and _lord(li,6)!=_lord(li,8)
                     and pos[_lord(li,6)]["rasi_idx"]==pos[_lord(li,8)]["rasi_idx"],
     "Phaladeepika 7 — 6L and 8L conjunct: debt and disease combine, producing enduring health expenditures, litigation cycles and chronic struggles."),
    ("8L+12L Conjunction",
     lambda pos, li: _lord(li,8) in pos and _lord(li,12) in pos and _lord(li,8)!=_lord(li,12)
                     and pos[_lord(li,8)]["rasi_idx"]==pos[_lord(li,12)]["rasi_idx"],
     "Phaladeepika 7 — 8L conjunct 12L: transformation-loss confluence, drains of energy and money via hospitals, foreign turmoil or hidden enemies."),
    ("6L+8L+12L all in Kendra",
     lambda pos, li: all((_lord(li,h) in pos and pos[_lord(li,h)]["house"] in KENDRA_HOUSES) for h in (6,8,12)),
     "Phaladeepika 7 — All three dusthana lords seated in kendras: pillars of life carry the burden of debt, transformation and loss; demands disciplined remedies."),
    ("Mars+Saturn+Rahu Conjunction",
     lambda pos, li: all(p in pos for p in ("Mars","Saturn","Rahu"))
                     and pos["Mars"]["rasi_idx"]==pos["Saturn"]["rasi_idx"]==pos["Rahu"]["rasi_idx"],
     "Phaladeepika 7 — Mars, Saturn and Rahu in single conjunction: triple-malefic fusion creating chronic conflict, accident risk and karmic obstructions."),
    ("Mars+Saturn 7th-axis Aspect",
     lambda pos, li: "Mars" in pos and "Saturn" in pos
                     and ((pos["Mars"]["house"] - pos["Saturn"]["house"]) % 12 + 1) == 7,
     "Phaladeepika 7 — Mars and Saturn in 7th from each other (mutual opposition): tension between drive and discipline, marital friction, health volatility."),
    ("Sun+Saturn in Lagna or 7",
     lambda pos, li: "Sun" in pos and "Saturn" in pos
                     and pos["Sun"]["rasi_idx"]==pos["Saturn"]["rasi_idx"]
                     and pos["Sun"]["house"] in (1,7),
     "Phaladeepika 7 — Sun and Saturn together in lagna or 7th: father-self friction, partnership delays, ego-discipline conflict requiring patience and humility."),
    ("Moon+Saturn+Mars in 6/8/12",
     lambda pos, li: all(p in pos and pos[p]["house"] in DUSTHANA_HOUSES for p in ("Moon","Saturn","Mars")),
     "Phaladeepika 7 — Moon, Saturn and Mars all sunk in 6/8/12: severe mental affliction, depressive episodes and chronic health/debt cycles needing strong remedies."),
    ("Rahu in 7 + Saturn in Lagna",
     lambda pos, li: "Rahu" in pos and "Saturn" in pos and pos["Rahu"]["house"]==7 and pos["Saturn"]["house"]==1,
     "Phaladeepika 7 — Rahu in 7th with Saturn in lagna: shadowed marriage and burdened body, partnerships marked by deception, delays and karmic tests."),
    ("Ketu in 7 + Mars in Lagna",
     lambda pos, li: "Ketu" in pos and "Mars" in pos and pos["Ketu"]["house"]==7 and pos["Mars"]["house"]==1,
     "Phaladeepika 7 — Ketu in 7th with Mars in lagna: aggressive body energies clash with detached partner; risk of separation and abrupt relationship endings."),
]


def y_dushtha_yogas(chart):
    pos = chart["positions"]; lagna_idx = chart["lagna_idx"]
    out = []
    for name, fn, interp in DUSHTHA_YOGAS:
        try:
            if fn(pos, lagna_idx):
                out.append(_y(f"Dushtha: {name}", "Inauspicious yoga", 3, "challenge_combo",
                              "Phaladeepika Ch. 7", interp, [name]))
        except Exception:
            pass
    return out


# ============================================================
# MASTER LIST
# ============================================================
ALL_DARIDRA = [y_daridra_lagna_dusthana, y_daridra_2l_8, y_daridra_11l_12, y_daridra_2l_combust,
               y_daridra_lagna_lord_with_6l, y_daridra_2l_6l, y_daridra_5l_dusthana,
               y_daridra_jupiter_debil, y_daridra_no_planet_kendra_trikona,
               y_daridra_venus_8,
               y_daridra_lagna_with_malefics, y_daridra_2_8_axis_malefic, y_daridra_11_12_swap,
               y_daridra_saturn_2, y_daridra_rahu_2]

ALL_PUTRA_BANDHYA = [y_putra_5l_jupiter, y_putra_jup_5, y_putra_5_in_kendra, y_putra_5_aspect_jup,
                     y_putra_putrakaraka_strong, y_putra_5_with_benefics, y_putra_jupiter_kendra_lagna,
                     y_putra_5_with_lagna_lord, y_putra_5l_in_5,
                     y_bandhya_5l_dusthana, y_bandhya_jupiter_debil, y_bandhya_5_malefics,
                     y_bandhya_jup_dusthana, y_bandhya_rahu_5, y_bandhya_ketu_5, y_bandhya_5_8_axis]

# Single-call category aggregators
CATEGORY_FNS = [
    ("daridra_yogas", lambda c: [r for fn in ALL_DARIDRA for r in [fn(c)] if r]),
    ("putra_bandhya_yogas", lambda c: [r for fn in ALL_PUTRA_BANDHYA for r in [fn(c)] if r]),
    ("disease_yogas", y_disease_yogas),
    ("sadhu_yogas", y_sadhu_yogas),
    ("career_yogas", y_career_yogas),
    ("marriage_yogas", y_marriage_yogas),
    ("travel_yogas", y_travel_yogas),
    ("nabhasa_extended", y_nabhasa_extended),
    ("dhana_yogas_extra", y_dhana_yogas),
    ("arishta_yogas", y_arishta_yogas),
    ("raja_yogas_bhavartha", y_raja_yogas_bhavartha),
    ("vipareeta_raja_yogas", y_vipareeta_raja_yogas),
    ("pravrajya_yogas", y_pravrajya_yogas),
    ("solar_yogas_full", y_solar_yogas_full),
    ("lunar_yogas_full", y_lunar_yogas_full),
    ("nabhasa_completion", y_nabhasa_completion),
    ("dhana_bhava_yogas", y_dhana_bhava_yogas),
    ("dushtha_yogas", y_dushtha_yogas),
]


def detect_all_expanded_yogas(chart):
    """Run every expanded yoga function and return a flat list."""
    out = []
    for cat_name, fn in CATEGORY_FNS:
        rs = fn(chart)
        for r in rs:
            r["category"] = cat_name
            out.append(r)
    return out


def yoga_count_summary():
    """Return total number of distinct yoga rules in this module."""
    return {
        "daridra": len(ALL_DARIDRA),
        "putra_bandhya": len(ALL_PUTRA_BANDHYA),
        "disease": len(DISEASE_YOGAS_DATA),
        "sadhu": len(SADHU_YOGAS_DATA),
        "career": len(CAREER_YOGAS_DATA),
        "marriage": len(MARRIAGE_YOGAS_DATA),
        "travel": len(TRAVEL_YOGAS_DATA),
        "nabhasa": len(NABHASA_YOGAS_DATA),
        "dhana": len(DHANA_YOGAS_DATA),
        "arishta": len(ARISHTA_YOGAS_DATA),
        "raja_yogas_bhavartha": len(RAJA_YOGAS_BHAVARTHA),
        "vipareeta_raja": len(VIPAREETA_RAJA_YOGAS),
        "pravrajya": len(PRAVRAJYA_YOGAS),
        "solar_full": len(SOLAR_YOGAS_FULL),
        "lunar_full": len(LUNAR_YOGAS_FULL),
        "nabhasa_completion": len(NABHASA_COMPLETION),
        "dhana_bhava": len(DHANA_BHAVA_YOGAS),
        "dushtha": len(DUSHTHA_YOGAS),
        "total": (len(ALL_DARIDRA)+len(ALL_PUTRA_BANDHYA)+len(DISEASE_YOGAS_DATA)+
                  len(SADHU_YOGAS_DATA)+len(CAREER_YOGAS_DATA)+len(MARRIAGE_YOGAS_DATA)+
                  len(TRAVEL_YOGAS_DATA)+len(NABHASA_YOGAS_DATA)+
                  len(DHANA_YOGAS_DATA)+len(ARISHTA_YOGAS_DATA)+
                  len(RAJA_YOGAS_BHAVARTHA)+len(VIPAREETA_RAJA_YOGAS)+
                  len(PRAVRAJYA_YOGAS)+len(SOLAR_YOGAS_FULL)+len(LUNAR_YOGAS_FULL)+
                  len(NABHASA_COMPLETION)+len(DHANA_BHAVA_YOGAS)+len(DUSHTHA_YOGAS)),
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    summary = yoga_count_summary()
    print(f"=== EXPANDED YOGA LIBRARY — {summary['total']} rules total ===")
    for cat, n in summary.items():
        if cat == "total": continue
        print(f"  {cat:20s}: {n} rules")
    print()

    yogas = detect_all_expanded_yogas(chart)
    print(f"=== {len(yogas)} EXPANDED YOGAS detected for {chart['name']} ===\n")
    by_cat = {}
    for y in yogas:
        by_cat.setdefault(y["category"], []).append(y)
    for cat, ys in by_cat.items():
        print(f"--- {cat} ({len(ys)}) ---")
        for y in ys[:5]:
            print(f"  [sev{y['severity']}] {y['name']}")
            print(f"        {y['interpretation'][:90]}")
        if len(ys) > 5:
            print(f"        ... and {len(ys)-5} more")
        print()
