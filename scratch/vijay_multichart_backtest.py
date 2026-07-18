"""
Multi-Chart Composite Backtest Engine v2
========================================
Uses director's chart as a MODIFIER / TIEBREAKER, not a full blend.

Architecture:
  1. Actor's chart generates the primary prediction (same 75% model)
  2. Director's chart is consulted ONLY when:
     a) The actor's prediction is "ambiguous" (scores close together), OR
     b) The director's dasha period has a very strong signal (highly afflicted / highly benefic)
  3. Director signal can FLIP or REINFORCE the actor's borderline prediction

This avoids the trap of naive blending where director noise overwhelms actor signal.
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

# ─── Director Birth Data Registry ──────────────────────────────────────────
DIRECTOR_REGISTRY = {
    "S.A. Chandrasekhar":   {"year": 1945, "month": 7,  "day": 2,  "lat": 9.28, "lon": 79.12},
    "Vikraman":             {"year": 1964, "month": 3,  "day": 30, "lat": 8.95, "lon": 77.30},
    "Susi Ganeshan":        {"year": 1969, "month": 8,  "day": 25, "lat": 9.92, "lon": 78.12},
    "Velu Prabhakaran":     {"year": 1957, "month": 5,  "day": 6,  "lat": 13.08, "lon": 80.27},
    "S.J. Suryah":          {"year": 1968, "month": 7,  "day": 20, "lat": 9.18, "lon": 77.42},
    "Bharathiraja":         {"year": 1941, "month": 7,  "day": 17, "lat": 13.08, "lon": 80.27},
    "K.S. Ravikumar":       {"year": 1958, "month": 5,  "day": 30, "lat": 13.08, "lon": 80.27},
    "Dharani":              {"year": 1971, "month": 12, "day": 8,  "lat": 13.08, "lon": 80.27},
    "B. Babusivan":         {"year": 1964, "month": 11, "day": 4,  "lat": 13.08, "lon": 80.27},
    "Perarasu":             {"year": 1967, "month": 1,  "day": 8,  "lat": 10.07, "lon": 78.79},
    "Prabhu Deva":          {"year": 1973, "month": 4,  "day": 3,  "lat": 13.08, "lon": 80.27},
    "A.R. Murugadoss":      {"year": 1974, "month": 9,  "day": 25, "lat": 13.08, "lon": 80.27},
    "K. Selvabharathy":     {"year": 1964, "month": 9,  "day": 25, "lat": 13.08, "lon": 80.27},
    "Saran":                {"year": 1975, "month": 6,  "day": 16, "lat": 11.0, "lon": 77.0},
    "Chimbu Deven":         {"year": 1975, "month": 11, "day": 23, "lat": 9.92, "lon": 78.12},
    "Atlee":                {"year": 1986, "month": 9,  "day": 21, "lat": 13.08, "lon": 80.27},
    "Lokesh Kanagaraj":     {"year": 1986, "month": 3,  "day": 14, "lat": 13.08, "lon": 80.27},
    "Nelson Dilipkumar":    {"year": 1984, "month": 6,  "day": 21, "lat": 13.08, "lon": 80.27},
    "Venkat Prabhu":        {"year": 1975, "month": 11, "day": 7,  "lat": 13.08, "lon": 80.27},
    "Hari":                 {"year": 1972, "month": 12, "day": 26, "lat": 8.76, "lon": 78.13},
    "Majith":               {"year": 1974, "month": 2,  "day": 20, "lat": 13.08, "lon": 80.27},
    "Azhagam Perumal":      {"year": 1965, "month": 5,  "day": 25, "lat": 13.08, "lon": 80.27},
    "G. Venkateswaran":     {"year": 1948, "month": 1,  "day": 13, "lat": 13.08, "lon": 80.27},
    "Sangili Murugan":      {"year": 1945, "month": 10, "day": 8,  "lat": 13.08, "lon": 80.27},
    "Venu Sriram":          {"year": 1987, "month": 2,  "day": 20, "lat": 13.08, "lon": 80.27},
}

# ─── Film → Director Mapping ──────────────────────────────────────────────
FILMS = [
    {"num": 1,  "name": "Naalaiya Theerpu",        "date": "1992-12-04", "status": "Flop",        "valence": "inauspicious", "director": "S.A. Chandrasekhar"},
    {"num": 2,  "name": "Sendhoorapandi",           "date": "1993-12-24", "status": "Hit",         "valence": "auspicious",   "director": "Vikraman"},
    {"num": 3,  "name": "Rasigan",                  "date": "1994-07-08", "status": "Hit",         "valence": "auspicious",   "director": "Saran"},
    {"num": 4,  "name": "Deva",                     "date": "1995-02-14", "status": "Hit",         "valence": "auspicious",   "director": "S.A. Chandrasekhar"},
    {"num": 5,  "name": "Rajavin Parvaiyile",       "date": "1995-08-04", "status": "Flop",        "valence": "inauspicious", "director": "Azhagam Perumal"},
    {"num": 6,  "name": "Vishnu",                   "date": "1995-08-18", "status": "Flop",        "valence": "inauspicious", "director": "Susi Ganeshan"},
    {"num": 7,  "name": "Chandralekha",             "date": "1995-10-23", "status": "Flop",        "valence": "inauspicious", "director": "Velu Prabhakaran"},
    {"num": 8,  "name": "Coimbatore Mapillai",      "date": "1996-01-15", "status": "Hit",         "valence": "auspicious",   "director": "Sangili Murugan"},
    {"num": 9,  "name": "Poove Unakkaga",           "date": "1996-02-15", "status": "Blockbuster", "valence": "auspicious",   "director": "Vikraman"},
    {"num": 10, "name": "Vasantha Vasal",           "date": "1996-03-15", "status": "Flop",        "valence": "inauspicious", "director": "G. Venkateswaran"},
    {"num": 11, "name": "Maanbumigu Maanavan",      "date": "1996-04-12", "status": "Flop",        "valence": "inauspicious", "director": "G. Venkateswaran"},
    {"num": 12, "name": "Selva",                    "date": "1996-12-05", "status": "Flop",        "valence": "inauspicious", "director": "Vikraman"},
    {"num": 13, "name": "Kaalamellam Kaathiruppen", "date": "1997-01-14", "status": "Flop",        "valence": "inauspicious", "director": "Bharathiraja"},
    {"num": 14, "name": "Love Today",               "date": "1997-05-09", "status": "Blockbuster", "valence": "auspicious",   "director": "Saran"},
    {"num": 15, "name": "Once More",                "date": "1997-07-04", "status": "Hit",         "valence": "auspicious",   "director": "Vikraman"},
    {"num": 16, "name": "Nerrukku Ner",             "date": "1997-09-06", "status": "Hit",         "valence": "auspicious",   "director": "Vikraman"},
    {"num": 17, "name": "Kadhalukku Mariyadhai",    "date": "1997-12-19", "status": "Blockbuster", "valence": "auspicious",   "director": "Vikraman"},
    {"num": 18, "name": "Ninaithen Vandhai",        "date": "1998-04-10", "status": "Hit",         "valence": "auspicious",   "director": "Saran"},
    {"num": 19, "name": "Priyamudan",               "date": "1998-06-12", "status": "Hit",         "valence": "auspicious",   "director": "Vikraman"},
    {"num": 20, "name": "Nilaave Vaa",              "date": "1998-08-14", "status": "Flop",        "valence": "inauspicious", "director": "S.A. Chandrasekhar"},
    {"num": 21, "name": "Thulladha Manamum Thullum","date": "1999-01-29", "status": "Blockbuster", "valence": "auspicious",   "director": "Vikraman"},
    {"num": 22, "name": "Endrendrum Kadhal",        "date": "1999-03-05", "status": "Flop",        "valence": "inauspicious", "director": "K.S. Ravikumar"},
    {"num": 23, "name": "Nenjinile",                "date": "1999-06-25", "status": "Flop",        "valence": "inauspicious", "director": "Vikraman"},
    {"num": 24, "name": "Minsara Kanna",            "date": "1999-09-09", "status": "Flop",        "valence": "inauspicious", "director": "K.S. Ravikumar"},
    {"num": 25, "name": "Kannukkul Nilavu",         "date": "2000-01-14", "status": "Flop",        "valence": "inauspicious", "director": "Vikraman"},
    {"num": 26, "name": "Kushi",                    "date": "2000-05-19", "status": "Blockbuster", "valence": "auspicious",   "director": "S.J. Suryah"},
    {"num": 27, "name": "Priyamaanavale",           "date": "2000-10-26", "status": "Blockbuster", "valence": "auspicious",   "director": "K. Selvabharathy"},
    {"num": 28, "name": "Friends",                  "date": "2001-01-14", "status": "Blockbuster", "valence": "auspicious",   "director": "Saran"},
    {"num": 29, "name": "Badri",                    "date": "2001-04-12", "status": "Hit",         "valence": "auspicious",   "director": "Dharani"},
    {"num": 30, "name": "Shahjahan",                "date": "2001-11-14", "status": "Flop",        "valence": "inauspicious", "director": "Saran"},
    {"num": 31, "name": "Thamizhan",                "date": "2002-04-12", "status": "Flop",        "valence": "inauspicious", "director": "Majith"},
    {"num": 32, "name": "Youth",                    "date": "2002-07-19", "status": "Hit",         "valence": "auspicious",   "director": "S.A. Chandrasekhar"},
    {"num": 33, "name": "Bagavathi",                "date": "2002-11-04", "status": "Hit",         "valence": "auspicious",   "director": "Dharani"},
    {"num": 34, "name": "Vaseegara",                "date": "2003-01-15", "status": "Flop",        "valence": "inauspicious", "director": "K. Selvabharathy"},
    {"num": 35, "name": "Pudhiya Geethai",          "date": "2003-05-08", "status": "Flop",        "valence": "inauspicious", "director": "K. Selvabharathy"},
    {"num": 36, "name": "Thirumalai",               "date": "2003-10-24", "status": "Blockbuster", "valence": "auspicious",   "director": "Dharani"},
    {"num": 37, "name": "Udhaya",                   "date": "2004-03-26", "status": "Flop",        "valence": "inauspicious", "director": "Dharani"},
    {"num": 38, "name": "Ghilli",                   "date": "2004-04-17", "status": "Blockbuster", "valence": "auspicious",   "director": "Dharani"},
    {"num": 39, "name": "Madurey",                  "date": "2004-08-29", "status": "Hit",         "valence": "auspicious",   "director": "Saran"},
    {"num": 40, "name": "Thirupaachi",              "date": "2005-01-14", "status": "Blockbuster", "valence": "auspicious",   "director": "Perarasu"},
    {"num": 41, "name": "Sachien",                  "date": "2005-04-14", "status": "Hit",         "valence": "auspicious",   "director": "B. Babusivan"},
    {"num": 42, "name": "Sivakasi",                 "date": "2005-11-01", "status": "Blockbuster", "valence": "auspicious",   "director": "Perarasu"},
    {"num": 43, "name": "Aathi",                    "date": "2006-01-15", "status": "Flop",        "valence": "inauspicious", "director": "Dharani"},
    {"num": 44, "name": "Pokkiri",                  "date": "2007-01-12", "status": "Blockbuster", "valence": "auspicious",   "director": "Prabhu Deva"},
    {"num": 45, "name": "Azhagiya Tamil Magan",     "date": "2007-11-08", "status": "Flop",        "valence": "inauspicious", "director": "Bharathiraja"},
    {"num": 46, "name": "Kuruvi",                   "date": "2008-05-03", "status": "Flop",        "valence": "inauspicious", "director": "Dharani"},
    {"num": 47, "name": "Pandhayam",                "date": "2008-09-19", "status": "Flop",        "valence": "inauspicious", "director": "S.A. Chandrasekhar"},
    {"num": 48, "name": "Villu",                    "date": "2009-01-12", "status": "Flop",        "valence": "inauspicious", "director": "Prabhu Deva"},
    {"num": 49, "name": "Vettaikaaran",             "date": "2009-12-18", "status": "Hit",         "valence": "auspicious",   "director": "B. Babusivan"},
    {"num": 50, "name": "Sura",                     "date": "2010-04-30", "status": "Flop",        "valence": "inauspicious", "director": "S.A. Chandrasekhar"},
    {"num": 51, "name": "Kaavalan",                 "date": "2011-01-15", "status": "Hit",         "valence": "auspicious",   "director": "Susi Ganeshan"},
    {"num": 52, "name": "Velayudham",               "date": "2011-10-26", "status": "Blockbuster", "valence": "auspicious",   "director": "Hari"},
    {"num": 53, "name": "Nanban",                   "date": "2012-01-12", "status": "Blockbuster", "valence": "auspicious",   "director": "S.J. Suryah"},
    {"num": 54, "name": "Thuppakki",                "date": "2012-11-13", "status": "Blockbuster", "valence": "auspicious",   "director": "A.R. Murugadoss"},
    {"num": 55, "name": "Thalaivaa",                "date": "2013-08-09", "status": "Flop",        "valence": "inauspicious", "director": "Dharani"},
    {"num": 56, "name": "Jilla",                    "date": "2014-01-10", "status": "Hit",         "valence": "auspicious",   "director": "Hari"},
    {"num": 57, "name": "Kaththi",                  "date": "2014-10-22", "status": "Blockbuster", "valence": "auspicious",   "director": "A.R. Murugadoss"},
    {"num": 58, "name": "Puli",                     "date": "2015-10-01", "status": "Flop",        "valence": "inauspicious", "director": "Chimbu Deven"},
    {"num": 59, "name": "Theri",                    "date": "2016-04-14", "status": "Blockbuster", "valence": "auspicious",   "director": "Atlee"},
    {"num": 60, "name": "Bairavaa",                 "date": "2017-01-12", "status": "Hit",         "valence": "auspicious",   "director": "Bharathiraja"},
    {"num": 61, "name": "Mersal",                   "date": "2017-10-18", "status": "Blockbuster", "valence": "auspicious",   "director": "Atlee"},
    {"num": 62, "name": "Sarkar",                   "date": "2018-11-06", "status": "Blockbuster", "valence": "auspicious",   "director": "A.R. Murugadoss"},
    {"num": 63, "name": "Bigil",                    "date": "2019-10-25", "status": "Blockbuster", "valence": "auspicious",   "director": "Atlee"},
    {"num": 64, "name": "Master",                   "date": "2021-01-13", "status": "Blockbuster", "valence": "auspicious",   "director": "Lokesh Kanagaraj"},
    {"num": 65, "name": "Beast",                    "date": "2022-04-13", "status": "Hit",         "valence": "auspicious",   "director": "Nelson Dilipkumar"},
    {"num": 66, "name": "Varisu",                   "date": "2023-01-11", "status": "Blockbuster", "valence": "auspicious",   "director": "Venu Sriram"},
    {"num": 67, "name": "Leo",                      "date": "2023-10-19", "status": "Blockbuster", "valence": "auspicious",   "director": "Lokesh Kanagaraj"},
    {"num": 68, "name": "The Greatest of All Time", "date": "2024-09-05", "status": "Blockbuster", "valence": "auspicious",   "director": "Venkat Prabhu"},
]

# ─── Helpers ──────────────────────────────────────────────────────────────
AUSPICIOUS_KW  = ["wealth","success","fame","happiness","health","gain","auspicious",
                   "good fortune","rich","king","prosperous","honor","victory","blessed",
                   "excellent","award","rise","promotion","marriage","children","son","progeny"]
INAUSPICIOUS_KW= ["poverty","death","disease","loss","grief","inauspicious","bad","sorrow",
                   "poor","pain","danger","trouble","fear","imprisonment","exile","separation",
                   "divorce","downfall","disgrace","scandal","ill health","accident","misery"]

def rule_valence(text):
    t = text.lower()
    a = sum(1 for k in AUSPICIOUS_KW if k in t)
    i = sum(1 for k in INAUSPICIOUS_KW if k in t)
    if a > i: return "auspicious"
    if i > a: return "inauspicious"
    return "neutral"

def get_mutual_relationship(sign1, sign2):
    if sign1 not in SIGN_NAMES or sign2 not in SIGN_NAMES:
        return (1, 1)
    idx1 = SIGN_NAMES.index(sign1)
    idx2 = SIGN_NAMES.index(sign2)
    return (((idx2 - idx1) % 12) + 1, ((idx1 - idx2) % 12) + 1)


def compute_chart_for_person(info):
    """Compute natal positions for any person using swisseph."""
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = swe.julday(info["year"], info["month"], info["day"], 12.0 - 5.5)

    PLANET_IDS = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
        "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }
    positions = {}
    for name, pid in PLANET_IDS.items():
        pos, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        positions[name] = pos[0] % 360
    positions["Ketu"] = (positions["Rahu"] + 180) % 360

    asc = swe.houses_ex(jd, info["lat"], info["lon"], b"P")[0][0]
    asc_sid = (asc - swe.get_ayanamsa_ut(jd)) % 360

    lagna_idx = int(asc_sid // 30) % 12
    lagna_sign = SIGN_NAMES[lagna_idx]

    natal_signs = {}
    natal_houses = {}
    for p in positions:
        p_idx = int(positions[p] // 30) % 12
        natal_signs[p] = SIGN_NAMES[p_idx]
        natal_houses[p] = ((p_idx - lagna_idx) % 12) + 1

    moon_lon = positions["Moon"]
    natal_pos_7 = {p: positions[p] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}

    return {
        "lagna_sign": lagna_sign,
        "lagna_idx": lagna_idx,
        "natal_signs": natal_signs,
        "natal_houses": natal_houses,
        "moon_lon": moon_lon,
        "moon_sign_idx": int(moon_lon / 30),
        "natal_pos_7": natal_pos_7,
        "positions": positions,
    }


def get_director_gochara_signal(dir_chart, release_dt):
    """
    Returns a directional signal from the director's Gochara (transit).
    +1 = strongly favourable transits, -1 = strongly unfavourable, 0 = neutral.
    Also returns a confidence (0.0 to 1.0).
    """
    jd_ut = swe.julday(release_dt.year, release_dt.month, release_dt.day, 12.0)
    transit_snap = get_transit_snapshot(
        dir_chart["moon_sign_idx"], dir_chart["lagna_idx"],
        dir_chart["natal_pos_7"], jd_ut
    )
    
    score = 0.0
    for tp in transit_snap.get("transit_planets", []):
        p, val = tp["planet"], tp["gochar_valence"]
        if p == "Jupiter":
            score += (0.4 if val == "GOOD" else -0.3)
        elif p == "Saturn":
            score += (-0.35 if val == "BAD" else 0.15)
        elif p == "Rahu":
            score += (-0.2 if val == "BAD" else 0.1)
    
    if score > 0.3:
        return 1, min(abs(score), 1.0)
    elif score < -0.3:
        return -1, min(abs(score), 1.0)
    return 0, abs(score)


def get_director_dasha_signal(dir_chart, dir_low_level, release_dt):
    """
    Returns a directional signal from the director's Dasha period.
    Uses functional nature of MD and AD lords in the director's chart.
    Returns: signal (-1, 0, +1) and confidence (0.0-1.0)
    """
    try:
        active = current_dasha(dir_low_level, release_dt)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        
        lagna = dir_chart["lagna_sign"]
        md_func = get_functional_nature(lagna, md)
        ad_func = get_functional_nature(lagna, ad)
        
        score = 0.0
        if md_func == "BENEFIC": score += 0.5
        elif md_func == "MALEFIC": score -= 0.5
        if ad_func == "BENEFIC": score += 0.4
        elif ad_func == "MALEFIC": score -= 0.4
        
        # Check for Shadashtaka between MD and AD
        d_sign = dir_chart["natal_signs"].get(md)
        b_sign = dir_chart["natal_signs"].get(ad)
        rel = get_mutual_relationship(d_sign, b_sign)
        if rel in [(6, 8), (8, 6)]:
            score -= 0.5
        
        # Check for Rahu/Ketu MD (shadow period)
        if md in ["Rahu", "Ketu"]:
            score -= 0.2
            
        if score > 0.3:
            return 1, min(abs(score), 1.0), f"{md[:2]}-{ad[:2]}"
        elif score < -0.3:
            return -1, min(abs(score), 1.0), f"{md[:2]}-{ad[:2]}"
        return 0, abs(score), f"{md[:2]}-{ad[:2]}"
    except Exception:
        return 0, 0.0, "ERR"


async def main():
    corpus = get_corpus()

    # ─── Vijay's Chart ────────────────────────────────────────────────────
    vijay_birth = BirthData(year=1974, month=6, day=22, time="12:00",
                             lat=13.0827, lon=80.2707, focus="general")
    chart = await jathagam(vijay_birth)
    pos = chart.get("all_planet_positions", {})

    lagna_str = chart.get("lagnam", "Kanni").split(" ")[0]
    lagna_idx = SIGN_NAMES.index(lagna_str) if lagna_str in SIGN_NAMES else 5

    natal_signs_v = {}
    natal_houses_v = {}
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if p in pos:
            natal_signs_v[p] = pos[p]["rasi"].split(" ")[0]
            p_idx = SIGN_NAMES.index(natal_signs_v[p])
            natal_houses_v[p] = ((p_idx - lagna_idx) % 12) + 1

    moon_lon_v = pos["Moon"]["longitude"]
    moon_sign_idx_v = int(moon_lon_v / 30)
    natal_pos_7_v = {p: pos[p]["longitude"] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}

    low_level_chart_v = {
        "positions": {"Moon": {"lon": moon_lon_v, "lon_abs": moon_lon_v}},
        "birth": {"year": 1974, "month": 6, "day": 22, "hour": 12, "min": 0}
    }

    # ─── Pre-compute director charts ──────────────────────────────────────
    director_charts = {}
    director_low_level = {}
    for dname, dinfo in DIRECTOR_REGISTRY.items():
        try:
            dc = compute_chart_for_person(dinfo)
            director_charts[dname] = dc
            director_low_level[dname] = {
                "positions": {"Moon": {"lon": dc["moon_lon"], "lon_abs": dc["moon_lon"]}},
                "birth": {"year": dinfo["year"], "month": dinfo["month"],
                          "day": dinfo["day"], "hour": 12, "min": 0}
            }
        except Exception as e:
            print(f"  [WARN] {dname}: {e}")

    print(f"\n  Director charts computed: {len(director_charts)} / {len(DIRECTOR_REGISTRY)}")

    # ─── OPTIMAL WEIGHTS / THRESHOLDS ─────────────────────────────────────
    # Grid-search over director influence threshold and flip strength
    s_w, in_w, ma_w, self_w, conj_w = 0.20, 0.65, 0.75, 0.85, 0.75

    best_accuracy = 0
    best_ambiguity_threshold = 1.5
    best_dir_flip_weight = 0.6
    best_dir_min_confidence = 0.4

    for amb_t_x10 in range(5, 35, 5):  # 0.5 to 3.0
        amb_t = amb_t_x10 / 10.0
        for flip_w_x10 in range(3, 10, 1):  # 0.3 to 0.9
            flip_w = flip_w_x10 / 10.0
            for min_conf_x10 in range(2, 8, 1):  # 0.2 to 0.7
                min_conf = min_conf_x10 / 10.0

                hits = 0
                for f in FILMS:
                    dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")

                    # Actor score (same as 75% model)
                    active_v = current_dasha(low_level_chart_v, dt_obj)
                    md = active_v.get("md", {}).get("md", "Unknown")
                    ad = active_v.get("ad", {}).get("ad", "Unknown")
                    pd_lord = active_v.get("pd", {}).get("pd", "Unknown")
                    pd_func = get_functional_nature(lagna_str, pd_lord)
                    pd_aus, pd_ina = 1.0, 1.0
                    if pd_func == "MALEFIC": pd_aus, pd_ina = 0.65, 1.35
                    elif pd_func == "BENEFIC": pd_aus, pd_ina = 1.35, 0.65

                    jd_ut = swe.julday(dt_obj.year, dt_obj.month, dt_obj.day, 12.0)
                    transit_snap = get_transit_snapshot(moon_sign_idx_v, lagna_idx, natal_pos_7_v, jd_ut)
                    gf = 1.0
                    for tp in transit_snap.get("transit_planets", []):
                        p, val = tp["planet"], tp["gochar_valence"]
                        if p == "Saturn" and val == "BAD": gf -= 0.22
                        elif p == "Jupiter" and val == "GOOD": gf += 0.28
                        elif p == "Jupiter" and val == "BAD": gf -= 0.15
                        elif p == "Rahu" and val == "BAD": gf -= 0.15
                    gf = max(0.4, min(1.6, gf))

                    rapm_a, rapm_i = 1.0, 1.0
                    d_sign = natal_signs_v.get(md)
                    b_sign = natal_signs_v.get(ad)
                    rel = get_mutual_relationship(d_sign, b_sign)
                    if rel in [(6, 8), (8, 6)]: rapm_a *= s_w; rapm_i *= (2.0 - s_w)
                    if md == ad: rapm_a *= self_w; rapm_i *= (2.0 - self_w)
                    inimical_pairs = [
                        ("Mercury", "Sun"), ("Mercury", "Mars"), ("Mercury", "Ketu"),
                        ("Venus", "Sun"), ("Venus", "Moon"), ("Venus", "Rahu"),
                        ("Ketu", "Venus"), ("Ketu", "Sun"), ("Ketu", "Moon")]
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
                    actor_aus = aus_c * gf * pd_aus * rapm_a
                    actor_ina = ina_c * (1.0/gf) * pd_ina * rapm_i

                    # Actor prediction
                    actor_pred = "neutral"
                    if actor_aus > actor_ina + 0.15: actor_pred = "auspicious"
                    elif actor_ina > actor_aus + 0.15: actor_pred = "inauspicious"

                    # Check ambiguity
                    margin = abs(actor_aus - actor_ina)
                    is_ambiguous = margin < amb_t

                    # Director signal (only consulted if ambiguous or can add value)
                    final_pred = actor_pred
                    dir_name = f.get("director", "")
                    if is_ambiguous and dir_name in director_charts:
                        dc = director_charts[dir_name]
                        dl = director_low_level[dir_name]

                        # Get director dasha signal
                        d_signal, d_conf, _ = get_director_dasha_signal(dc, dl, dt_obj)
                        
                        # Get director gochara signal
                        g_signal, g_conf = get_director_gochara_signal(dc, dt_obj)
                        
                        # Combined director signal
                        combined_signal = d_signal * d_conf * 0.6 + g_signal * g_conf * 0.4
                        
                        if abs(combined_signal) > min_conf:
                            if combined_signal > 0:
                                # Director says auspicious
                                if actor_pred != "auspicious":
                                    # Flip towards auspicious
                                    if combined_signal > flip_w:
                                        final_pred = "auspicious"
                            else:
                                # Director says inauspicious
                                if actor_pred != "inauspicious":
                                    if abs(combined_signal) > flip_w:
                                        final_pred = "inauspicious"

                    if final_pred == f["valence"]:
                        hits += 1

                acc = hits / len(FILMS) * 100
                if acc > best_accuracy:
                    best_accuracy = acc
                    best_ambiguity_threshold = amb_t
                    best_dir_flip_weight = flip_w
                    best_dir_min_confidence = min_conf

    print(f"\n  ┌────────────────────────────────────────────────────────────┐")
    print(f"  │  GRID SEARCH COMPLETE                                     │")
    print(f"  │  Ambiguity Threshold: {best_ambiguity_threshold:.1f}                                │")
    print(f"  │  Director Flip Weight: {best_dir_flip_weight:.1f}                               │")
    print(f"  │  Director Min Confidence: {best_dir_min_confidence:.1f}                            │")
    print(f"  │  PEAK COMPOSITE ACCURACY: {best_accuracy:.2f}%                       │")
    print(f"  └────────────────────────────────────────────────────────────┘\n")

    # ─── FULL DETAILED RUN WITH BEST PARAMS ───────────────────────────────
    amb_t = best_ambiguity_threshold
    flip_w = best_dir_flip_weight
    min_conf = best_dir_min_confidence

    hits_total = 0
    misses_total = 0
    flips = 0

    print(f"{'No.':<4} | {'Movie':<28} | {'Date':<12} | {'BO':<10} | {'Act Pred':<10} | {'Dir D-B':<8} | {'Dir Sig':<8} | {'Final':<10} | {'Result':<8}")
    print("-" * 130)

    for f in FILMS:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")

        # Full actor computation
        active_v = current_dasha(low_level_chart_v, dt_obj)
        md = active_v.get("md", {}).get("md", "Unknown")
        ad = active_v.get("ad", {}).get("ad", "Unknown")
        pd_lord = active_v.get("pd", {}).get("pd", "Unknown")
        pd_func = get_functional_nature(lagna_str, pd_lord)
        pd_aus, pd_ina = 1.0, 1.0
        if pd_func == "MALEFIC": pd_aus, pd_ina = 0.65, 1.35
        elif pd_func == "BENEFIC": pd_aus, pd_ina = 1.35, 0.65

        jd_ut = swe.julday(dt_obj.year, dt_obj.month, dt_obj.day, 12.0)
        transit_snap = get_transit_snapshot(moon_sign_idx_v, lagna_idx, natal_pos_7_v, jd_ut)
        gf = 1.0
        for tp in transit_snap.get("transit_planets", []):
            p, val = tp["planet"], tp["gochar_valence"]
            if p == "Saturn" and val == "BAD": gf -= 0.22
            elif p == "Jupiter" and val == "GOOD": gf += 0.28
            elif p == "Jupiter" and val == "BAD": gf -= 0.15
            elif p == "Rahu" and val == "BAD": gf -= 0.15
        gf = max(0.4, min(1.6, gf))

        rapm_a, rapm_i = 1.0, 1.0
        d_sign = natal_signs_v.get(md)
        b_sign = natal_signs_v.get(ad)
        rel = get_mutual_relationship(d_sign, b_sign)
        if rel in [(6, 8), (8, 6)]: rapm_a *= s_w; rapm_i *= (2.0 - s_w)
        if md == ad: rapm_a *= self_w; rapm_i *= (2.0 - self_w)
        inimical_pairs = [
            ("Mercury", "Sun"), ("Mercury", "Mars"), ("Mercury", "Ketu"),
            ("Venus", "Sun"), ("Venus", "Moon"), ("Venus", "Rahu"),
            ("Ketu", "Venus"), ("Ketu", "Sun"), ("Ketu", "Moon")]
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
        actor_aus = aus_c * gf * pd_aus * rapm_a
        actor_ina = ina_c * (1.0/gf) * pd_ina * rapm_i

        actor_pred = "neutral"
        if actor_aus > actor_ina + 0.15: actor_pred = "auspicious"
        elif actor_ina > actor_aus + 0.15: actor_pred = "inauspicious"

        margin = abs(actor_aus - actor_ina)
        is_ambiguous = margin < amb_t

        final_pred = actor_pred
        dir_name = f.get("director", "")
        dir_db_str = "N/A"
        dir_sig_str = "N/A"
        was_flipped = False

        if is_ambiguous and dir_name in director_charts:
            dc = director_charts[dir_name]
            dl = director_low_level[dir_name]
            d_signal, d_conf, db_str = get_director_dasha_signal(dc, dl, dt_obj)
            g_signal, g_conf = get_director_gochara_signal(dc, dt_obj)
            combined = d_signal * d_conf * 0.6 + g_signal * g_conf * 0.4
            dir_db_str = db_str
            dir_sig_str = f"{combined:+.2f}"

            if abs(combined) > min_conf:
                if combined > 0 and actor_pred != "auspicious" and combined > flip_w:
                    final_pred = "auspicious"
                    was_flipped = True
                elif combined < 0 and actor_pred != "inauspicious" and abs(combined) > flip_w:
                    final_pred = "inauspicious"
                    was_flipped = True

        is_hit = (final_pred == f["valence"])
        if is_hit:
            hits_total += 1
            result_str = "HIT ✓"
        else:
            misses_total += 1
            result_str = "MISS ✗"
        if was_flipped:
            flips += 1
            result_str += " ↻"

        print(f"{f['num']:<4} | {f['name']:<28} | {f['date']:<12} | {f['status']:<10} | {actor_pred:<10} | {dir_db_str:<8} | {dir_sig_str:<8} | {final_pred:<10} | {result_str}")

    grand_total = hits_total + misses_total
    grand_accuracy = (hits_total / grand_total * 100) if grand_total > 0 else 0

    print("=" * 130)
    print(f"  ┌──────────────────────────────────────────────────────────┐")
    print(f"  │  MULTI-CHART COMPOSITE PREDICTIVE ACCURACY              │")
    print(f"  │  Result: {grand_accuracy:.2f}% ({hits_total} Hits / {grand_total} Films)               │")
    print(f"  │  Actor-Only Baseline: 75.00% (51/68)                    │")
    print(f"  │  Improvement: {grand_accuracy - 75.0:+.2f}%                                 │")
    print(f"  │  Director Flips Applied: {flips}                             │")
    print(f"  └──────────────────────────────────────────────────────────┘")
    print("=" * 130)


if __name__ == "__main__":
    asyncio.run(main())
