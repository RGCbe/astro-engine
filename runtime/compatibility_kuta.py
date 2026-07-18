from vedic_core import RASI_LORDS

"""Ashtakuta (8-Fold) Compatibility Matching — 36-point system.

Source: Muhurta Chintamani, Phaladeepika, Brihat Jataka.
Used for marriage/partner compatibility from two charts.

The 8 Kutas:
  1. Varna   (1 pt)  — spiritual compatibility
  2. Vasya   (2 pts) — mutual control / influence
  3. Tara    (3 pts) — health, longevity
  4. Yoni    (4 pts) — sexual / instinctive
  5. Graha-Maitri (5 pts) — friendship of Moon-lords
  6. Gana    (6 pts) — temperament (deva/manushya/rakshasa)
  7. Bhakoot (7 pts) — emotional compatibility, prosperity
  8. Nadi    (8 pts) — health of progeny
Total: 36 points. >=18 = good match. >=24 = excellent.
"""
import sys
sys.path.insert(0, ".")

NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya",
              "Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
              "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
              "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]

# Varna by Moon Rasi (sign): Brahmin/Kshatriya/Vaishya/Shudra
VARNA_BY_RASI = {"Cancer":"Brahmin","Scorpio":"Brahmin","Pisces":"Brahmin",
                 "Aries":"Kshatriya","Leo":"Kshatriya","Sagittarius":"Kshatriya",
                 "Taurus":"Vaishya","Virgo":"Vaishya","Capricorn":"Vaishya",
                 "Gemini":"Shudra","Libra":"Shudra","Aquarius":"Shudra"}
VARNA_RANK = {"Brahmin":4,"Kshatriya":3,"Vaishya":2,"Shudra":1}

# Yoni (animal type) per nakshatra
YONI = {"Ashwini":"Horse","Shatabhisha":"Horse","Bharani":"Elephant","Revati":"Elephant",
        "Pushya":"Goat","Krittika":"Goat","Rohini":"Snake","Mrigashira":"Snake",
        "Ardra":"Dog","Mula":"Dog","Punarvasu":"Cat","Ashlesha":"Cat",
        "Magha":"Rat","Purva Phalguni":"Rat","Uttara Phalguni":"Cow","Uttara Bhadrapada":"Cow",
        "Hasta":"Buffalo","Swati":"Buffalo","Chitra":"Tiger","Vishakha":"Tiger",
        "Jyeshtha":"Deer","Anuradha":"Deer","Purva Ashadha":"Monkey","Shravana":"Monkey",
        "Dhanishta":"Lion","Uttara Ashadha":"Mongoose","Purva Bhadrapada":"Lion"}

# Yoni enmity matrix (incomplete; full table in classical texts)
YONI_ENEMY = {
    ("Cow","Tiger"),("Tiger","Cow"),("Elephant","Lion"),("Lion","Elephant"),
    ("Horse","Buffalo"),("Buffalo","Horse"),("Dog","Deer"),("Deer","Dog"),
    ("Snake","Mongoose"),("Mongoose","Snake"),("Cat","Rat"),("Rat","Cat"),
    ("Monkey","Goat"),("Goat","Monkey"),
}

# Gana per nakshatra
GANA = {"Ashwini":"Deva","Mrigashira":"Deva","Punarvasu":"Deva","Pushya":"Deva",
        "Hasta":"Deva","Swati":"Deva","Anuradha":"Deva","Shravana":"Deva","Revati":"Deva",
        "Bharani":"Manushya","Rohini":"Manushya","Ardra":"Manushya","Purva Phalguni":"Manushya",
        "Uttara Phalguni":"Manushya","Purva Ashadha":"Manushya","Uttara Ashadha":"Manushya",
        "Purva Bhadrapada":"Manushya","Uttara Bhadrapada":"Manushya",
        "Krittika":"Rakshasa","Ashlesha":"Rakshasa","Magha":"Rakshasa","Chitra":"Rakshasa",
        "Vishakha":"Rakshasa","Jyeshtha":"Rakshasa","Mula":"Rakshasa","Dhanishta":"Rakshasa",
        "Shatabhisha":"Rakshasa"}

# Nadi per nakshatra (Adi/Madhya/Antya)
NADI = {"Ashwini":"Adi","Ardra":"Adi","Punarvasu":"Adi","Uttara Phalguni":"Adi",
        "Hasta":"Adi","Jyeshtha":"Adi","Mula":"Adi","Shatabhisha":"Adi","Purva Bhadrapada":"Adi",
        "Bharani":"Madhya","Mrigashira":"Madhya","Pushya":"Madhya","Purva Phalguni":"Madhya",
        "Chitra":"Madhya","Anuradha":"Madhya","Purva Ashadha":"Madhya","Dhanishta":"Madhya","Uttara Bhadrapada":"Madhya",
        "Krittika":"Antya","Rohini":"Antya","Ashlesha":"Antya","Magha":"Antya","Swati":"Antya",
        "Vishakha":"Antya","Uttara Ashadha":"Antya","Shravana":"Antya","Revati":"Antya"}

# Vasya
VASYA_BY_SIGN = {
    "Aries":["Leo","Scorpio"],"Taurus":["Cancer","Libra"],"Gemini":["Virgo"],"Cancer":["Scorpio","Sagittarius"],
    "Leo":["Libra"],"Virgo":["Pisces","Gemini"],"Libra":["Capricorn","Virgo"],"Scorpio":["Cancer"],
    "Sagittarius":["Pisces"],"Capricorn":["Aries","Aquarius"],"Aquarius":["Aries"],"Pisces":["Capricorn"],
}

# Friendship table (used for Graha Maitri)

FRIENDSHIPS = {
    "Sun":{"friend":["Moon","Mars","Jupiter"],"enemy":["Venus","Saturn"],"neutral":["Mercury"]},
    "Moon":{"friend":["Sun","Mercury"],"enemy":[],"neutral":["Mars","Jupiter","Venus","Saturn"]},
    "Mars":{"friend":["Sun","Moon","Jupiter"],"enemy":["Mercury"],"neutral":["Venus","Saturn"]},
    "Mercury":{"friend":["Sun","Venus"],"enemy":["Moon"],"neutral":["Mars","Jupiter","Saturn"]},
    "Jupiter":{"friend":["Sun","Moon","Mars"],"enemy":["Mercury","Venus"],"neutral":["Saturn"]},
    "Venus":{"friend":["Mercury","Saturn"],"enemy":["Sun","Moon"],"neutral":["Mars","Jupiter"]},
    "Saturn":{"friend":["Mercury","Venus"],"enemy":["Sun","Moon","Mars"],"neutral":["Jupiter"]},
}


def varna_match(b_rasi, g_rasi):
    """1 pt if boy's varna >= girl's varna."""
    bv = VARNA_BY_RASI.get(b_rasi)
    gv = VARNA_BY_RASI.get(g_rasi)
    if not bv or not gv: return 0
    return 1 if VARNA_RANK[bv] >= VARNA_RANK[gv] else 0


def vasya_match(b_rasi, g_rasi):
    """2 pts if g's sign in b's vasya OR vice versa, 1 pt if friendly, 0 if neither."""
    if g_rasi in VASYA_BY_SIGN.get(b_rasi, []): return 2
    if b_rasi in VASYA_BY_SIGN.get(g_rasi, []): return 1
    return 0


def tara_match(b_nak, g_nak):
    """3 pts if Tara count from boy to girl divides by 9 with 0/3/5/7 remainder."""
    if b_nak not in NAKSHATRAS or g_nak not in NAKSHATRAS: return 0
    bi = NAKSHATRAS.index(b_nak)
    gi = NAKSHATRAS.index(g_nak)
    fwd = ((gi - bi) % 27) + 1
    bwd = ((bi - gi) % 27) + 1
    GOOD = [2, 4, 6, 8, 9]  # Sampat, Kshema, Sadhaka, Mitra, Atimitra
    score = 0
    if fwd % 9 in [GOOD] or fwd in GOOD: score += 1.5
    if bwd in GOOD: score += 1.5
    return min(3, score)


def yoni_match(b_nak, g_nak):
    """4 pts max."""
    by = YONI.get(b_nak); gy = YONI.get(g_nak)
    if not by or not gy: return 0
    if by == gy: return 4
    if (by, gy) in YONI_ENEMY: return 0
    return 2  # neutral / friendly


def graha_maitri_match(b_rasi, g_rasi):
    """5 pts based on Moon-lord friendship."""
    bl = RASI_LORDS.get(b_rasi); gl = RASI_LORDS.get(g_rasi)
    if not bl or not gl: return 0
    if bl == gl: return 5
    bf = FRIENDSHIPS.get(bl, {})
    gf = FRIENDSHIPS.get(gl, {})
    if gl in bf.get("friend", []) and bl in gf.get("friend", []): return 5
    if gl in bf.get("friend", []) or bl in gf.get("friend", []): return 4
    if gl in bf.get("neutral", []) and bl in gf.get("neutral", []): return 3
    if gl in bf.get("enemy", []) and bl in gf.get("enemy", []): return 0
    return 1


def gana_match(b_nak, g_nak):
    """6 pts max. Same gana = 6, deva-manushya = 5, deva-rakshasa = 1, manushya-rakshasa = 0."""
    bg = GANA.get(b_nak); gg = GANA.get(g_nak)
    if not bg or not gg: return 0
    if bg == gg: return 6
    if {bg, gg} == {"Deva", "Manushya"}: return 5
    if {bg, gg} == {"Manushya", "Rakshasa"}: return 0
    return 1  # Deva-Rakshasa


def bhakoot_match(b_rasi, g_rasi):
    """7 pts. Sign distance not 6/8 = 7 pts. 6/8 distance = 0 (Shadashtaka dosha)."""
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    if b_rasi not in SIGNS or g_rasi not in SIGNS: return 0
    bi = SIGNS.index(b_rasi); gi = SIGNS.index(g_rasi)
    diff = (gi - bi) % 12
    bad = [5, 7]  # 6th and 8th from each other (0-indexed, so 5th = 6th)
    if diff in bad or (12 - diff) % 12 in bad: return 0
    return 7


def nadi_match(b_nak, g_nak):
    """8 pts. Same nadi = 0 (Nadi dosha). Different = 8."""
    bn = NADI.get(b_nak); gn = NADI.get(g_nak)
    if not bn or not gn: return 0
    return 0 if bn == gn else 8


def ashtakuta_match(boy_chart, girl_chart):
    """Run all 8 kuta matches. Return scores + interpretation."""
    b_rasi = boy_chart.get("moon_rasi") or boy_chart["positions"]["Moon"]["rasi"]
    g_rasi = girl_chart.get("moon_rasi") or girl_chart["positions"]["Moon"]["rasi"]
    b_nak = boy_chart.get("janma_nakshatra") or boy_chart["positions"]["Moon"].get("nak")
    g_nak = girl_chart.get("janma_nakshatra") or girl_chart["positions"]["Moon"].get("nak")

    RASI_MAP = {
        "mesham": "Aries", "rishabam": "Taurus", "mithunam": "Gemini", "kadagam": "Cancer",
        "simmam": "Leo", "simha": "Leo", "kanni": "Virgo", "thulaam": "Libra", "thula": "Libra",
        "viruchigam": "Scorpio", "dhanusu": "Sagittarius", "makaram": "Capricorn",
        "kumbam": "Aquarius", "meenam": "Pisces"
    }
    
    def normalize_rasi(r):
        if not r: return r
        r_clean = r.strip().lower()
        if r_clean in RASI_MAP:
            return RASI_MAP[r_clean]
        return r.capitalize()

    b_rasi = normalize_rasi(b_rasi)
    g_rasi = normalize_rasi(g_rasi)

    scores = {
        "Varna (1)":         varna_match(b_rasi, g_rasi),
        "Vasya (2)":         vasya_match(b_rasi, g_rasi),
        "Tara (3)":          tara_match(b_nak, g_nak),
        "Yoni (4)":          yoni_match(b_nak, g_nak),
        "Graha Maitri (5)":  graha_maitri_match(b_rasi, g_rasi),
        "Gana (6)":          gana_match(b_nak, g_nak),
        "Bhakoot (7)":       bhakoot_match(b_rasi, g_rasi),
        "Nadi (8)":          nadi_match(b_nak, g_nak),
    }
    total = sum(scores.values())

    # Verdict
    if total >= 28: verdict = "EXCELLENT match (28+/36)"
    elif total >= 24: verdict = "VERY GOOD match (24-27/36)"
    elif total >= 18: verdict = "ACCEPTABLE match (18-23/36)"
    else: verdict = "POOR match (<18/36) — significant compatibility concerns"

    return {
        "boy_rasi": b_rasi, "boy_nakshatra": b_nak,
        "girl_rasi": g_rasi, "girl_nakshatra": g_nak,
        "scores": scores,
        "total": total,
        "max": 36,
        "percentage": round(100 * total / 36, 1),
        "verdict": verdict,
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    # Demo: match Manoj with hypothetical girl with Moon in Rohini (Taurus)
    boy = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    fake_girl = {
        "positions": {"Moon": {"rasi": "Taurus", "nak": "Rohini"}},
        "moon_rasi": "Taurus",
        "janma_nakshatra": "Rohini",
        "name": "Demo Girl",
    }
    result = ashtakuta_match(boy, fake_girl)
    print(f"=== Ashtakuta Match: {boy['name']} (Magha) vs Demo Girl (Rohini) ===")
    print(f"  Boy Rasi/Nakshatra:  {result['boy_rasi']} / {result['boy_nakshatra']}")
    print(f"  Girl Rasi/Nakshatra: {result['girl_rasi']} / {result['girl_nakshatra']}")
    for k, v in result["scores"].items():
        print(f"  {k:25s} {v}")
    print(f"  TOTAL: {result['total']}/{result['max']} ({result['percentage']}%) — {result['verdict']}")
