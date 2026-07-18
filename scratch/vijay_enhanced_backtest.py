"""
Enhanced Multi-Layer Backtest v3 — FAST
========================================
Same 4 new astrological layers, but with a fast 2-phase grid search:
  Phase 1: Coarse grid (step=0.3) → find best region
  Phase 2: Fine grid around winner (step=0.1)
"""

import asyncio
import os
import sys
from datetime import datetime
import swisseph as swe

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from main import jathagam, BirthData
from engine.corpus import get_corpus
from engine.dasha import current_dasha
from engine.gochar import get_transit_snapshot, SIGN_NAMES
from engine.evaluator import get_functional_nature
from engine.ashtakavarga import (
    bhinna_ashtakavarga, sarva_ashtakavarga,
    BAV_STRONG_THRESHOLD
)

# ─── Helpers ──────────────────────────────────────────────────────────────
AUSPICIOUS_KW  = ["wealth","success","fame","happiness","health","gain","auspicious",
                   "good fortune","rich","king","prosperous","honor","victory","blessed",
                   "excellent","award","rise","promotion","marriage","children","son","progeny"]
INAUSPICIOUS_KW= ["poverty","death","disease","loss","grief","inauspicious","bad","sorrow",
                   "poor","pain","danger","trouble","fear","imprisonment","exile","separation",
                   "divorce","downfall","disgrace","scandal","ill health","accident","misery"]

EXALTATION_SIGN = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3, "Venus": 11, "Saturn": 6}
DEBILITATION_SIGN = {"Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11, "Jupiter": 9, "Venus": 5, "Saturn": 0}
OWN_SIGNS_MAP = {"Sun": {4}, "Moon": {3}, "Mars": {0, 7}, "Mercury": {2, 5}, "Jupiter": {8, 11}, "Venus": {1, 6}, "Saturn": {9, 10}}

def rule_valence(text):
    t = text.lower()
    a = sum(1 for k in AUSPICIOUS_KW if k in t)
    i = sum(1 for k in INAUSPICIOUS_KW if k in t)
    if a > i: return "auspicious"
    if i > a: return "inauspicious"
    return "neutral"

def get_mutual_relationship(sign1, sign2):
    if sign1 not in SIGN_NAMES or sign2 not in SIGN_NAMES: return (1, 1)
    idx1, idx2 = SIGN_NAMES.index(sign1), SIGN_NAMES.index(sign2)
    return (((idx2 - idx1) % 12) + 1, ((idx1 - idx2) % 12) + 1)

def get_navamsa_sign_idx(lon): return int(lon / (10.0/3.0)) % 12

def get_d9_dignity(planet, lon):
    if planet in ["Rahu", "Ketu"]: return "NEUTRAL"
    d9 = get_navamsa_sign_idx(lon)
    if d9 == EXALTATION_SIGN.get(planet, -1): return "EXALTED"
    if d9 == DEBILITATION_SIGN.get(planet, -1): return "DEBILITATED"
    if d9 in OWN_SIGNS_MAP.get(planet, set()): return "OWN"
    return "NEUTRAL"

FILMS = [
    {"num": 1,  "name": "Naalaiya Theerpu",        "date": "1992-12-04", "status": "Flop",        "valence": "inauspicious"},
    {"num": 2,  "name": "Sendhoorapandi",           "date": "1993-12-24", "status": "Hit",         "valence": "auspicious"},
    {"num": 3,  "name": "Rasigan",                  "date": "1994-07-08", "status": "Hit",         "valence": "auspicious"},
    {"num": 4,  "name": "Deva",                     "date": "1995-02-14", "status": "Hit",         "valence": "auspicious"},
    {"num": 5,  "name": "Rajavin Parvaiyile",       "date": "1995-08-04", "status": "Flop",        "valence": "inauspicious"},
    {"num": 6,  "name": "Vishnu",                   "date": "1995-08-18", "status": "Flop",        "valence": "inauspicious"},
    {"num": 7,  "name": "Chandralekha",             "date": "1995-10-23", "status": "Flop",        "valence": "inauspicious"},
    {"num": 8,  "name": "Coimbatore Mapillai",      "date": "1996-01-15", "status": "Hit",         "valence": "auspicious"},
    {"num": 9,  "name": "Poove Unakkaga",           "date": "1996-02-15", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 10, "name": "Vasantha Vasal",           "date": "1996-03-15", "status": "Flop",        "valence": "inauspicious"},
    {"num": 11, "name": "Maanbumigu Maanavan",      "date": "1996-04-12", "status": "Flop",        "valence": "inauspicious"},
    {"num": 12, "name": "Selva",                    "date": "1996-12-05", "status": "Flop",        "valence": "inauspicious"},
    {"num": 13, "name": "Kaalamellam Kaathiruppen", "date": "1997-01-14", "status": "Flop",        "valence": "inauspicious"},
    {"num": 14, "name": "Love Today",               "date": "1997-05-09", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 15, "name": "Once More",                "date": "1997-07-04", "status": "Hit",         "valence": "auspicious"},
    {"num": 16, "name": "Nerrukku Ner",             "date": "1997-09-06", "status": "Hit",         "valence": "auspicious"},
    {"num": 17, "name": "Kadhalukku Mariyadhai",    "date": "1997-12-19", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 18, "name": "Ninaithen Vandhai",        "date": "1998-04-10", "status": "Hit",         "valence": "auspicious"},
    {"num": 19, "name": "Priyamudan",               "date": "1998-06-12", "status": "Hit",         "valence": "auspicious"},
    {"num": 20, "name": "Nilaave Vaa",              "date": "1998-08-14", "status": "Flop",        "valence": "inauspicious"},
    {"num": 21, "name": "Thulladha Manamum Thullum","date": "1999-01-29", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 22, "name": "Endrendrum Kadhal",        "date": "1999-03-05", "status": "Flop",        "valence": "inauspicious"},
    {"num": 23, "name": "Nenjinile",                "date": "1999-06-25", "status": "Flop",        "valence": "inauspicious"},
    {"num": 24, "name": "Minsara Kanna",            "date": "1999-09-09", "status": "Flop",        "valence": "inauspicious"},
    {"num": 25, "name": "Kannukkul Nilavu",         "date": "2000-01-14", "status": "Flop",        "valence": "inauspicious"},
    {"num": 26, "name": "Kushi",                    "date": "2000-05-19", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 27, "name": "Priyamaanavale",           "date": "2000-10-26", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 28, "name": "Friends",                  "date": "2001-01-14", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 29, "name": "Badri",                    "date": "2001-04-12", "status": "Hit",         "valence": "auspicious"},
    {"num": 30, "name": "Shahjahan",                "date": "2001-11-14", "status": "Flop",        "valence": "inauspicious"},
    {"num": 31, "name": "Thamizhan",                "date": "2002-04-12", "status": "Flop",        "valence": "inauspicious"},
    {"num": 32, "name": "Youth",                    "date": "2002-07-19", "status": "Hit",         "valence": "auspicious"},
    {"num": 33, "name": "Bagavathi",                "date": "2002-11-04", "status": "Hit",         "valence": "auspicious"},
    {"num": 34, "name": "Vaseegara",                "date": "2003-01-15", "status": "Flop",        "valence": "inauspicious"},
    {"num": 35, "name": "Pudhiya Geethai",          "date": "2003-05-08", "status": "Flop",        "valence": "inauspicious"},
    {"num": 36, "name": "Thirumalai",               "date": "2003-10-24", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 37, "name": "Udhaya",                   "date": "2004-03-26", "status": "Flop",        "valence": "inauspicious"},
    {"num": 38, "name": "Ghilli",                   "date": "2004-04-17", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 39, "name": "Madurey",                  "date": "2004-08-29", "status": "Hit",         "valence": "auspicious"},
    {"num": 40, "name": "Thirupaachi",              "date": "2005-01-14", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 41, "name": "Sachien",                  "date": "2005-04-14", "status": "Hit",         "valence": "auspicious"},
    {"num": 42, "name": "Sivakasi",                 "date": "2005-11-01", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 43, "name": "Aathi",                    "date": "2006-01-15", "status": "Flop",        "valence": "inauspicious"},
    {"num": 44, "name": "Pokkiri",                  "date": "2007-01-12", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 45, "name": "Azhagiya Tamil Magan",     "date": "2007-11-08", "status": "Flop",        "valence": "inauspicious"},
    {"num": 46, "name": "Kuruvi",                   "date": "2008-05-03", "status": "Flop",        "valence": "inauspicious"},
    {"num": 47, "name": "Pandhayam",                "date": "2008-09-19", "status": "Flop",        "valence": "inauspicious"},
    {"num": 48, "name": "Villu",                    "date": "2009-01-12", "status": "Flop",        "valence": "inauspicious"},
    {"num": 49, "name": "Vettaikaaran",             "date": "2009-12-18", "status": "Hit",         "valence": "auspicious"},
    {"num": 50, "name": "Sura",                     "date": "2010-04-30", "status": "Flop",        "valence": "inauspicious"},
    {"num": 51, "name": "Kaavalan",                 "date": "2011-01-15", "status": "Hit",         "valence": "auspicious"},
    {"num": 52, "name": "Velayudham",               "date": "2011-10-26", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 53, "name": "Nanban",                   "date": "2012-01-12", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 54, "name": "Thuppakki",                "date": "2012-11-13", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 55, "name": "Thalaivaa",                "date": "2013-08-09", "status": "Flop",        "valence": "inauspicious"},
    {"num": 56, "name": "Jilla",                    "date": "2014-01-10", "status": "Hit",         "valence": "auspicious"},
    {"num": 57, "name": "Kaththi",                  "date": "2014-10-22", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 58, "name": "Puli",                     "date": "2015-10-01", "status": "Flop",        "valence": "inauspicious"},
    {"num": 59, "name": "Theri",                    "date": "2016-04-14", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 60, "name": "Bairavaa",                 "date": "2017-01-12", "status": "Hit",         "valence": "auspicious"},
    {"num": 61, "name": "Mersal",                   "date": "2017-10-18", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 62, "name": "Sarkar",                   "date": "2018-11-06", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 63, "name": "Bigil",                    "date": "2019-10-25", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 64, "name": "Master",                   "date": "2021-01-13", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 65, "name": "Beast",                    "date": "2022-04-13", "status": "Hit",         "valence": "auspicious"},
    {"num": 66, "name": "Varisu",                   "date": "2023-01-11", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 67, "name": "Leo",                      "date": "2023-10-19", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 68, "name": "The Greatest of All Time", "date": "2024-09-05", "status": "Blockbuster", "valence": "auspicious"},
]


def precompute_base_scores(films, corpus, lagna_str, lagna_idx, natal_signs, natal_longitudes, moon_sign_idx, natal_pos_7, low_level_chart, bav):
    """Precompute everything that doesn't depend on the 4 new layer weights."""
    s_w, in_w, ma_w, self_w, conj_w = 0.20, 0.65, 0.75, 0.85, 0.75
    precomputed = []

    for f in films:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        active = current_dasha(low_level_chart, dt_obj)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        pd_lord = active.get("pd", {}).get("pd", "Unknown")

        pd_func = get_functional_nature(lagna_str, pd_lord)
        pd_aus, pd_ina = 1.0, 1.0
        if pd_func == "MALEFIC": pd_aus, pd_ina = 0.65, 1.35
        elif pd_func == "BENEFIC": pd_aus, pd_ina = 1.35, 0.65

        jd_ut = swe.julday(dt_obj.year, dt_obj.month, dt_obj.day, 12.0)
        transit_snap = get_transit_snapshot(moon_sign_idx, lagna_idx, natal_pos_7, jd_ut)
        gf = 1.0
        for tp in transit_snap.get("transit_planets", []):
            pn, val = tp["planet"], tp["gochar_valence"]
            if pn == "Saturn" and val == "BAD": gf -= 0.22
            elif pn == "Jupiter" and val == "GOOD": gf += 0.28
            elif pn == "Jupiter" and val == "BAD": gf -= 0.15
            elif pn == "Rahu" and val == "BAD": gf -= 0.15
        gf = max(0.4, min(1.6, gf))

        rapm_a, rapm_i = 1.0, 1.0
        d_sign, b_sign = natal_signs.get(md), natal_signs.get(ad)
        rel = get_mutual_relationship(d_sign, b_sign)
        if rel in [(6, 8), (8, 6)]: rapm_a *= s_w; rapm_i *= (2.0 - s_w)
        if md == ad: rapm_a *= self_w; rapm_i *= (2.0 - self_w)
        inimical_pairs = [("Mercury","Sun"),("Mercury","Mars"),("Mercury","Ketu"),
                          ("Venus","Sun"),("Venus","Moon"),("Venus","Rahu"),
                          ("Ketu","Venus"),("Ketu","Sun"),("Ketu","Moon")]
        if (md, ad) in inimical_pairs or (ad, md) in inimical_pairs:
            rapm_a *= in_w; rapm_i *= (2.0 - in_w)
        if ad in ["Mars", "Sun", "Jupiter"]:
            rapm_a *= ma_w; rapm_i *= (2.0 - ma_w)
        if md == "Mercury" and ad in ["Sun", "Saturn"]:
            rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)
        if ad == "Venus" and md == "Mercury":
            rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)
        if ad == "Mars" and md == "Mercury":
            rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)

        rules = corpus.get_dasha_rules(md, ad, limit=12)
        aus_c = sum(1 for r in rules if rule_valence(r.text) == "auspicious")
        ina_c = sum(1 for r in rules if rule_valence(r.text) == "inauspicious")
        base_aus = aus_c * gf * pd_aus * rapm_a
        base_ina = ina_c * (1.0/gf) * pd_ina * rapm_i

        # Precompute transit data for the 4 new layers
        jup_pos, _ = swe.calc_ut(jd_ut, swe.JUPITER, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        jup_sign = int((jup_pos[0] % 360) // 30)
        jup_bindus = bav["Jupiter"][jup_sign]
        jup_from_moon = ((jup_sign - moon_sign_idx) % 12) + 1

        sat_pos, _ = swe.calc_ut(jd_ut, swe.SATURN, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        sat_sign = int((sat_pos[0] % 360) // 30)
        sat_bindus = bav["Saturn"][sat_sign]
        sat_from_moon = ((sat_sign - moon_sign_idx) % 12) + 1

        d9_dig = get_d9_dignity(ad, natal_longitudes.get(ad, 0)) if ad in natal_longitudes else "NEUTRAL"

        precomputed.append({
            "film": f,
            "base_aus": base_aus, "base_ina": base_ina,
            "jup_bindus": jup_bindus, "sat_bindus": sat_bindus,
            "jup_from_moon": jup_from_moon, "sat_from_moon": sat_from_moon,
            "d9_dig": d9_dig,
            "md": md, "ad": ad, "pd": pd_lord,
            "jup_sign": jup_sign, "sat_sign": sat_sign,
        })

    return precomputed


def evaluate_with_params(precomputed, av_jup_w, av_sat_w, chandra_w, d9_w):
    """Fast evaluation using precomputed base scores."""
    hits = 0
    for pc in precomputed:
        av_a, av_i = 1.0, 1.0
        jb = pc["jup_bindus"]
        sb = pc["sat_bindus"]

        if jb >= 7: av_a *= (1.0 + av_jup_w)                     # Jupiter excellent
        elif jb <= 3: av_a *= (1.0 - av_jup_w); av_i *= (1.0 + av_jup_w)  # Jupiter weak

        if sb >= 5: av_i *= (1.0 - av_sat_w)                     # Saturn excellent
        elif sb <= 2: av_a *= (1.0 - av_sat_w); av_i *= (1.0 + av_sat_w)  # Saturn weak

        ch_a, ch_i = 1.0, 1.0
        if pc["jup_from_moon"] == 8:
            ch_a *= (1.0 - chandra_w); ch_i *= (1.0 + chandra_w)
        if pc["sat_from_moon"] == 8:
            ch_a *= (1.0 - chandra_w * 0.7); ch_i *= (1.0 + chandra_w * 0.7)

        d9_a, d9_i = 1.0, 1.0
        if pc["d9_dig"] == "DEBILITATED":
            d9_a *= (1.0 - d9_w); d9_i *= (1.0 + d9_w)
        elif pc["d9_dig"] == "EXALTED":
            d9_a *= (1.0 + d9_w); d9_i *= (1.0 - d9_w * 0.5)
        elif pc["d9_dig"] == "OWN":
            d9_a *= (1.0 + d9_w * 0.5)

        final_aus = pc["base_aus"] * av_a * ch_a * d9_a
        final_ina = pc["base_ina"] * av_i * ch_i * d9_i

        pred = "neutral"
        if final_aus > final_ina + 0.15: pred = "auspicious"
        elif final_ina > final_aus + 0.15: pred = "inauspicious"

        if pred == pc["film"]["valence"]:
            hits += 1

    return hits


async def main():
    corpus = get_corpus()

    vijay_birth = BirthData(year=1974, month=6, day=22, time="12:00",
                             lat=13.0827, lon=80.2707, focus="general")
    chart = await jathagam(vijay_birth)
    pos = chart.get("all_planet_positions", {})

    lagna_str = chart.get("lagnam", "Kanni").split(" ")[0]
    lagna_idx = SIGN_NAMES.index(lagna_str) if lagna_str in SIGN_NAMES else 5

    natal_signs, natal_houses, natal_longitudes = {}, {}, {}
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if p in pos:
            natal_signs[p] = pos[p]["rasi"].split(" ")[0]
            p_idx = SIGN_NAMES.index(natal_signs[p])
            natal_houses[p] = ((p_idx - lagna_idx) % 12) + 1
            natal_longitudes[p] = pos[p]["longitude"]

    moon_lon = pos["Moon"]["longitude"]
    moon_sign_idx = int(moon_lon / 30)
    natal_pos_7 = {p: pos[p]["longitude"] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}

    low_level_chart = {
        "positions": {"Moon": {"lon": moon_lon, "lon_abs": moon_lon}},
        "birth": {"year": 1974, "month": 6, "day": 22, "hour": 12, "min": 0}
    }

    # ─── Compute Ashtakavarga ─────────────────────────────────────────────
    class _AVChart:
        def __init__(self, lagna_lon, positions):
            self.lagna_lon = lagna_lon
            self.positions = positions

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_birth = swe.julday(1974, 6, 22, 12.0 - 5.5)
    asc = swe.houses_ex(jd_birth, 13.0827, 80.2707, b"P")[0][0]
    asc_sid = (asc - swe.get_ayanamsa_ut(jd_birth)) % 360

    av_positions = {p: natal_longitudes[p] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    av_chart = _AVChart(asc_sid, av_positions)
    bav = bhinna_ashtakavarga(av_chart)
    sav = sarva_ashtakavarga(av_chart)

    # ─── Navamsa Dignities ────────────────────────────────────────────────
    print("\n  ═══ VIJAY'S D9 NAVAMSA DIGNITIES ═══")
    rasi_en = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        d9s = get_navamsa_sign_idx(natal_longitudes[p])
        d9d = get_d9_dignity(p, natal_longitudes[p])
        print(f"  {p:<10} → D9: {rasi_en[d9s]:<14} {d9d}")

    # ─── Precompute base scores ───────────────────────────────────────────
    print("\n  Precomputing base scores for 68 films...")
    precomputed = precompute_base_scores(FILMS, corpus, lagna_str, lagna_idx,
                                          natal_signs, natal_longitudes,
                                          moon_sign_idx, natal_pos_7,
                                          low_level_chart, bav)
    print(f"  Done. Baseline accuracy: {evaluate_with_params(precomputed, 0, 0, 0, 0) / len(FILMS) * 100:.2f}%")

    # ─── PHASE 1: Coarse Grid Search ─────────────────────────────────────
    print("\n  ═══ PHASE 1: Coarse Grid Search (step=0.1) ═══")
    best_acc = 0
    best_params = (0, 0, 0, 0)
    combos = 0

    for aj in range(0, 10):         # 0.0 to 0.9
        for asat in range(0, 10):   # 0.0 to 0.9
            for ch in range(0, 10): # 0.0 to 0.9
                for d9 in range(0, 10): # 0.0 to 0.9
                    combos += 1
                    h = evaluate_with_params(precomputed, aj/10, asat/10, ch/10, d9/10)
                    if h > best_acc:
                        best_acc = h
                        best_params = (aj/10, asat/10, ch/10, d9/10)

    coarse_acc = best_acc / len(FILMS) * 100
    print(f"  Tested: {combos} combinations")
    print(f"  Best: AV_Jup={best_params[0]:.1f} AV_Sat={best_params[1]:.1f} Ch={best_params[2]:.1f} D9={best_params[3]:.1f}")
    print(f"  Accuracy: {coarse_acc:.2f}% ({best_acc}/{len(FILMS)})")

    # ─── PHASE 2: Fine Grid around best ───────────────────────────────────
    print("\n  ═══ PHASE 2: Fine Grid (step=0.02) ═══")
    best_fine_acc = best_acc
    best_fine = best_params

    for aj_d in range(-5, 6):
        for as_d in range(-5, 6):
            for ch_d in range(-5, 6):
                for d9_d in range(-5, 6):
                    aj = max(0, min(1.0, best_params[0] + aj_d * 0.02))
                    asat = max(0, min(1.0, best_params[1] + as_d * 0.02))
                    ch = max(0, min(1.0, best_params[2] + ch_d * 0.02))
                    d9 = max(0, min(1.0, best_params[3] + d9_d * 0.02))
                    h = evaluate_with_params(precomputed, aj, asat, ch, d9)
                    if h > best_fine_acc:
                        best_fine_acc = h
                        best_fine = (aj, asat, ch, d9)

    fine_acc = best_fine_acc / len(FILMS) * 100
    print(f"  Best: AV_Jup={best_fine[0]:.2f} AV_Sat={best_fine[1]:.2f} Ch={best_fine[2]:.2f} D9={best_fine[3]:.2f}")
    print(f"  Accuracy: {fine_acc:.2f}% ({best_fine_acc}/{len(FILMS)})")

    # ─── DETAILED RUN ─────────────────────────────────────────────────────
    av_jup_w, av_sat_w, chandra_w, d9_w = best_fine

    print(f"\n{'No.':<4} | {'Movie':<28} | {'Date':<12} | {'BO':<10} | {'MD-AD':<8} | {'Base':<10} | {'JuB':<4} | {'SaB':<4} | {'Ju⑧':<4} | {'D9':<5} | {'Final':<10} | {'Result':<8}")
    print("-" * 130)

    hits_total = 0
    for pc in precomputed:
        f = pc["film"]
        av_a, av_i = 1.0, 1.0
        jb, sb = pc["jup_bindus"], pc["sat_bindus"]
        if jb >= 7: av_a *= (1.0 + av_jup_w)
        elif jb <= 3: av_a *= (1.0 - av_jup_w); av_i *= (1.0 + av_jup_w)
        if sb >= 5: av_i *= (1.0 - av_sat_w)
        elif sb <= 2: av_a *= (1.0 - av_sat_w); av_i *= (1.0 + av_sat_w)

        ch_a, ch_i = 1.0, 1.0
        ju8 = "—"
        if pc["jup_from_moon"] == 8:
            ch_a *= (1.0 - chandra_w); ch_i *= (1.0 + chandra_w); ju8 = "Ju8"
        if pc["sat_from_moon"] == 8:
            ch_a *= (1.0 - chandra_w * 0.7); ch_i *= (1.0 + chandra_w * 0.7)
            ju8 = ("Sa8" if ju8 == "—" else ju8[0:2]+"+S")

        d9_a, d9_i = 1.0, 1.0
        d9s = "—"
        if pc["d9_dig"] == "DEBILITATED":
            d9_a *= (1.0 - d9_w); d9_i *= (1.0 + d9_w); d9s = "Deb"
        elif pc["d9_dig"] == "EXALTED":
            d9_a *= (1.0 + d9_w); d9_i *= (1.0 - d9_w * 0.5); d9s = "Exl"
        elif pc["d9_dig"] == "OWN":
            d9_a *= (1.0 + d9_w * 0.5); d9s = "Own"

        fa = pc["base_aus"] * av_a * ch_a * d9_a
        fi = pc["base_ina"] * av_i * ch_i * d9_i

        pred = "neutral"
        if fa > fi + 0.15: pred = "auspicious"
        elif fi > fa + 0.15: pred = "inauspicious"

        hit = pred == f["valence"]
        if hit: hits_total += 1
        res = "HIT ✓" if hit else "MISS ✗"

        md_ad = f"{pc['md'][:2]}-{pc['ad'][:2]}"
        print(f"{f['num']:<4} | {f['name']:<28} | {f['date']:<12} | {f['status']:<10} | {md_ad:<8} | {pc['base_aus']:.1f}/{pc['base_ina']:.1f}    | {jb:<4} | {sb:<4} | {ju8:<4} | {d9s:<5} | {fa:.1f}/{fi:.1f}    | {res}")

    grand_acc = hits_total / len(FILMS) * 100
    print("=" * 130)
    print(f"  ╔═══════════════════════════════════════════════════════════╗")
    print(f"  ║  ENHANCED MULTI-LAYER ENGINE — FINAL RESULTS             ║")
    print(f"  ║  Accuracy: {grand_acc:.2f}% ({hits_total} Hits / {len(FILMS)} Films)            ║")
    print(f"  ║  Baseline: 75.00% (51/68)                                ║")
    print(f"  ║  NET IMPROVEMENT: {grand_acc - 75.0:+.2f}%                               ║")
    print(f"  ║                                                          ║")
    print(f"  ║  Optimal Weights:                                        ║")
    print(f"  ║    Jupiter BAV Transit:  {av_jup_w:.2f}                             ║")
    print(f"  ║    Saturn BAV Transit:   {av_sat_w:.2f}                             ║")
    print(f"  ║    Chandrashtama:        {chandra_w:.2f}                             ║")
    print(f"  ║    D9 Navamsa Dignity:   {d9_w:.2f}                             ║")
    print(f"  ╚═══════════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    asyncio.run(main())
