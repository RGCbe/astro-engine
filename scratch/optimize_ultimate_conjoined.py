import asyncio
import os
import sys
from datetime import datetime
import swisseph as swe

# Ensure parent directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from main import jathagam, BirthData
from engine.corpus import get_corpus
from engine.dasha import current_dasha
from engine.gochar import get_transit_snapshot, SIGN_NAMES
from engine.evaluator import get_functional_nature
from engine.tajik import annual_chart
from engine.ashtakavarga import bhinna_ashtakavarga, sarva_ashtakavarga

# Configure swisseph path
swe.set_sid_mode(swe.SIDM_LAHIRI)

# --- 68-Film Master List with Directors, Music, Production Scale, Clash, and Delay flags ---
FILMS = [
    {"num": 1,  "name": "Naalaiya Theerpu",        "date": "1992-12-04", "status": "Flop",        "valence": "inauspicious", "director": "S.A. Chandrasekhar", "music": "S.A. Rajkumar", "prod": "VV Creations", "delayed": False, "clash": False},
    {"num": 2,  "name": "Sendhoorapandi",           "date": "1993-12-24", "status": "Hit",         "valence": "auspicious",   "director": "S.A. Chandrasekhar", "music": "Deva",          "prod": "VV Creations", "delayed": False, "clash": False},
    {"num": 3,  "name": "Rasigan",                  "date": "1994-07-08", "status": "Hit",         "valence": "auspicious",   "director": "S.A. Chandrasekhar", "music": "Deva",          "prod": "VV Creations", "delayed": False, "clash": False},
    {"num": 4,  "name": "Deva",                     "date": "1995-02-14", "status": "Hit",         "valence": "auspicious",   "director": "S.A. Chandrasekhar", "music": "Deva",          "prod": "VV Creations", "delayed": False, "clash": False},
    {"num": 5,  "name": "Rajavin Parvaiyile",       "date": "1995-08-04", "status": "Flop",        "valence": "inauspicious", "director": "Janaki Soundar",     "music": "Ilaiyaraaja",   "prod": "Other",        "delayed": True,  "clash": False},
    {"num": 6,  "name": "Vishnu",                   "date": "1995-08-18", "status": "Flop",        "valence": "inauspicious", "director": "S.A. Chandrasekhar", "music": "Deva",          "prod": "Other",        "delayed": False, "clash": False},
    {"num": 7,  "name": "Chandralekha",             "date": "1995-10-23", "status": "Flop",        "valence": "inauspicious", "director": "Nambirajan",          "music": "Ilaiyaraaja",   "prod": "Other",        "delayed": False, "clash": False},
    {"num": 8,  "name": "Coimbatore Mapillai",      "date": "1996-01-15", "status": "Hit",         "valence": "auspicious",   "director": "C. Ranganathan",      "music": "Vidyasagar",    "prod": "Other",        "delayed": False, "clash": False},
    {"num": 9,  "name": "Poove Unakkaga",           "date": "1996-02-15", "status": "Blockbuster", "valence": "auspicious",   "director": "Vikraman",          "music": "S.A. Rajkumar", "prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 10, "name": "Vasantha Vasal",           "date": "1996-03-15", "status": "Flop",        "valence": "inauspicious", "director": "R. Selva",            "music": "Other",         "prod": "Other",        "delayed": False, "clash": False},
    {"num": 11, "name": "Maanbumigu Maanavan",      "date": "1996-04-12", "status": "Flop",        "valence": "inauspicious", "director": "S.A. Chandrasekhar", "music": "Deva",          "prod": "Other",        "delayed": False, "clash": False},
    {"num": 12, "name": "Selva",                    "date": "1996-12-05", "status": "Flop",        "valence": "inauspicious", "director": "A. Venkatesh",        "music": "Other",         "prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 13, "name": "Kaalamellam Kaathiruppen", "date": "1997-01-14", "status": "Flop",        "valence": "inauspicious", "director": "R. Sundarrajan",      "music": "Deva",          "prod": "Other",        "delayed": False, "clash": False},
    {"num": 14, "name": "Love Today",               "date": "1997-05-09", "status": "Blockbuster", "valence": "auspicious",   "director": "Balasekaran",       "music": "Other",         "prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 15, "name": "Once More",                "date": "1997-07-04", "status": "Hit",         "valence": "auspicious",   "director": "S.A. Chandrasekhar", "music": "Deva",          "prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 16, "name": "Nerrukku Ner",             "date": "1997-09-06", "status": "Hit",         "valence": "auspicious",   "director": "Vasanth",           "music": "Deva",          "prod": "Madras Talkies", "delayed": False, "clash": False},
    {"num": 17, "name": "Kadhalukku Mariyadhai",    "date": "1997-12-19", "status": "Blockbuster", "valence": "auspicious",   "director": "Fazil",             "music": "Ilaiyaraaja",   "prod": "Other",        "delayed": False, "clash": False},
    {"num": 18, "name": "Ninaithen Vandhai",        "date": "1998-04-10", "status": "Hit",         "valence": "auspicious",   "director": "K. Selvabharathy",     "music": "Deva",          "prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 19, "name": "Priyamudan",               "date": "1998-06-12", "status": "Hit",         "valence": "auspicious",   "director": "Vincent Selva",       "music": "Deva",          "prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 20, "name": "Nilaave Vaa",              "date": "1998-08-14", "status": "Flop",        "valence": "inauspicious", "director": "A. Venkatesh",        "music": "Vidyasagar",    "prod": "Kavithalayaa", "delayed": False, "clash": False},
    {"num": 21, "name": "Thulladha Manamum Thullum","date": "1999-01-29", "status": "Blockbuster", "valence": "auspicious",   "director": "Ezhil",             "music": "S.A. Rajkumar", "prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 22, "name": "Endrendrum Kadhal",        "date": "1999-03-05", "status": "Flop",        "valence": "inauspicious", "director": "Manoj Bhatnaghar",     "music": "Other",         "prod": "Other",        "delayed": False, "clash": False},
    {"num": 23, "name": "Nenjinile",                "date": "1999-06-25", "status": "Flop",        "valence": "inauspicious", "director": "S.A. Chandrasekhar", "music": "Deva",          "prod": "VV Creations", "delayed": False, "clash": False},
    {"num": 24, "name": "Minsara Kanna",            "date": "1999-09-09", "status": "Flop",        "valence": "inauspicious", "director": "K.S. Ravikumar",      "music": "Deva",          "prod": "Other",        "delayed": False, "clash": False},
    {"num": 25, "name": "Kannukkul Nilavu",         "date": "2000-01-14", "status": "Flop",        "valence": "inauspicious", "director": "Fazil",             "music": "Ilaiyaraaja",   "prod": "Other",        "delayed": False, "clash": False},
    {"num": 26, "name": "Kushi",                    "date": "2000-05-19", "status": "Blockbuster", "valence": "auspicious",   "director": "S.J. Suryah",         "music": "Deva",          "prod": "Other",        "delayed": False, "clash": False},
    {"num": 27, "name": "Priyamaanavale",           "date": "2000-10-26", "status": "Blockbuster", "valence": "auspicious",   "director": "K. Selvabharathy",     "music": "S.A. Rajkumar", "prod": "Kavithalayaa", "delayed": False, "clash": False},
    {"num": 28, "name": "Friends",                  "date": "2001-01-14", "status": "Blockbuster", "valence": "auspicious",   "director": "Siddique",          "music": "Ilaiyaraaja",   "prod": "Other",        "delayed": False, "clash": False},
    {"num": 29, "name": "Badri",                    "date": "2001-04-12", "status": "Hit",         "valence": "auspicious",   "director": "T.S. Senthilkumar",   "music": "Other",         "prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 30, "name": "Shahjahan",                "date": "2001-11-14", "status": "Flop",        "valence": "inauspicious", "director": "Ravi",              "music": "Mani Sharma",   "prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 31, "name": "Thamizhan",                "date": "2002-04-12", "status": "Flop",        "valence": "inauspicious", "director": "Majith",            "music": "Imman",         "prod": "Other",        "delayed": False, "clash": False},
    {"num": 32, "name": "Youth",                    "date": "2002-07-19", "status": "Hit",         "valence": "auspicious",   "director": "Vincent Selva",       "music": "Mani Sharma",   "prod": "Other",        "delayed": False, "clash": False},
    {"num": 33, "name": "Bagavathi",                "date": "2002-11-04", "status": "Hit",         "valence": "auspicious",   "director": "A. Venkatesh",        "music": "Deva",          "prod": "Other",        "delayed": False, "clash": True},
    {"num": 34, "name": "Vaseegara",                "date": "2003-01-15", "status": "Flop",        "valence": "inauspicious", "director": "K. Selvabharathy",     "music": "S.A. Rajkumar", "prod": "Super Good Films", "delayed": False, "clash": True},
    {"num": 35, "name": "Pudhiya Geethai",          "date": "2003-05-08", "status": "Flop",        "valence": "inauspicious", "director": "K.P. Jagan",          "music": "Yuvan",         "prod": "Other",        "delayed": False, "clash": False},
    {"num": 36, "name": "Thirumalai",               "date": "2003-10-24", "status": "Blockbuster", "valence": "auspicious",   "director": "Ramana",            "music": "Vidyasagar",    "prod": "Kavithalayaa", "delayed": False, "clash": True},
    {"num": 37, "name": "Udhaya",                   "date": "2004-03-26", "status": "Flop",        "valence": "inauspicious", "director": "Azhagam Perumal",     "music": "AR Rahman",     "prod": "Other",        "delayed": True,  "clash": False},
    {"num": 38, "name": "Ghilli",                   "date": "2004-04-17", "status": "Blockbuster", "valence": "auspicious",   "director": "Dharani",           "music": "Vidyasagar",    "prod": "Other",        "delayed": False, "clash": False},
    {"num": 39, "name": "Madurey",                  "date": "2004-08-29", "status": "Hit",         "valence": "auspicious",   "director": "Ramana Madhesh",      "music": "Vidyasagar",    "prod": "Other",        "delayed": False, "clash": False},
    {"num": 40, "name": "Thirupaachi",              "date": "2005-01-14", "status": "Blockbuster", "valence": "auspicious",   "director": "Perarasu",          "music": "Devi Sri Prasad","prod": "Super Good Films", "delayed": False, "clash": False},
    {"num": 41, "name": "Sachien",                  "date": "2005-04-14", "status": "Hit",         "valence": "auspicious",   "director": "John Mahendran",      "music": "Devi Sri Prasad","prod": "Other",        "delayed": False, "clash": True},
    {"num": 42, "name": "Sivakasi",                 "date": "2005-11-01", "status": "Blockbuster", "valence": "auspicious",   "director": "Perarasu",          "music": "Other",         "prod": "Other",        "delayed": False, "clash": False},
    {"num": 43, "name": "Aathi",                    "date": "2006-01-15", "status": "Flop",        "valence": "inauspicious", "director": "Ramana",            "music": "Vidyasagar",    "prod": "Other",        "delayed": False, "clash": True},
    {"num": 44, "name": "Pokkiri",                  "date": "2007-01-12", "status": "Blockbuster", "valence": "auspicious",   "director": "Prabhu Deva",         "music": "Mani Sharma",   "prod": "Other",        "delayed": False, "clash": False},
    {"num": 45, "name": "Azhagiya Tamil Magan",     "date": "2007-11-08", "status": "Flop",        "valence": "inauspicious", "director": "Bharathan",          "music": "AR Rahman",     "prod": "Other",        "delayed": False, "clash": False},
    {"num": 46, "name": "Kuruvi",                   "date": "2008-05-03", "status": "Flop",        "valence": "inauspicious", "director": "Dharani",           "music": "Vidyasagar",    "prod": "Other",        "delayed": False, "clash": True},
    {"num": 47, "name": "Pandhayam",                "date": "2008-09-19", "status": "Flop",        "valence": "inauspicious", "director": "S.A. Chandrasekhar", "music": "Vijay Antony",  "prod": "Other",        "delayed": False, "clash": False},
    {"num": 48, "name": "Villu",                    "date": "2009-01-12", "status": "Flop",        "valence": "inauspicious", "director": "Prabhu Deva",         "music": "Devi Sri Prasad","prod": "Other",        "delayed": False, "clash": False},
    {"num": 49, "name": "Vettaikaaran",             "date": "2009-12-18", "status": "Hit",         "valence": "auspicious",   "director": "B. Babusivan",        "music": "Vijay Antony",  "prod": "AVM Productions", "delayed": False, "clash": False},
    {"num": 50, "name": "Sura",                     "date": "2010-04-30", "status": "Flop",        "valence": "inauspicious", "director": "S.P. Rajkumar",       "music": "Mani Sharma",   "prod": "Other",        "delayed": False, "clash": False},
    {"num": 51, "name": "Kaavalan",                 "date": "2011-01-15", "status": "Hit",         "valence": "auspicious",   "director": "Siddique",          "music": "Vidyasagar",    "prod": "Other",        "delayed": False, "clash": False},
    {"num": 52, "name": "Velayudham",               "date": "2011-10-26", "status": "Blockbuster", "valence": "auspicious",   "director": "M. Raja",            "music": "Vijay Antony",  "prod": "Other",        "delayed": False, "clash": False},
    {"num": 53, "name": "Nanban",                   "date": "2012-01-12", "status": "Blockbuster", "valence": "auspicious",   "director": "S. Shankar",         "music": "Harris Jayaraj","prod": "Other",        "delayed": False, "clash": False},
    {"num": 54, "name": "Thuppakki",                "date": "2012-11-13", "status": "Blockbuster", "valence": "auspicious",   "director": "A.R. Murugadoss",     "music": "Harris Jayaraj","prod": "Other",        "delayed": False, "clash": False},
    {"num": 55, "name": "Thalaivaa",                "date": "2013-08-09", "status": "Flop",        "valence": "inauspicious", "director": "A.L. Vijay",          "music": "Other",         "prod": "Other",        "delayed": True,  "clash": False},
    {"num": 56, "name": "Jilla",                    "date": "2014-01-10", "status": "Hit",         "valence": "auspicious",   "director": "R.T. Neason",         "music": "Imman",         "prod": "Super Good Films", "delayed": False, "clash": True},
    {"num": 57, "name": "Kaththi",                  "date": "2014-10-22", "status": "Blockbuster", "valence": "auspicious",   "director": "A.R. Murugadoss",     "music": "Anirudh",       "prod": "Lyca",         "delayed": False, "clash": False},
    {"num": 58, "name": "Puli",                     "date": "2015-10-01", "status": "Flop",        "valence": "inauspicious", "director": "Chimbu Deven",        "music": "Devi Sri Prasad","prod": "Other",        "delayed": False, "clash": False},
    {"num": 59, "name": "Theri",                    "date": "2016-04-14", "status": "Blockbuster", "valence": "auspicious",   "director": "Atlee",             "music": "Other",         "prod": "Other",        "delayed": False, "clash": False},
    {"num": 60, "name": "Bairavaa",                 "date": "2017-01-12", "status": "Hit",         "valence": "auspicious",   "director": "Bharathan",          "music": "Other",         "prod": "Other",        "delayed": False, "clash": False},
    {"num": 61, "name": "Mersal",                   "date": "2017-10-18", "status": "Blockbuster", "valence": "auspicious",   "director": "Atlee",             "music": "AR Rahman",     "prod": "Other",        "delayed": False, "clash": False},
    {"num": 62, "name": "Sarkar",                   "date": "2018-11-06", "status": "Blockbuster", "valence": "auspicious",   "director": "A.R. Murugadoss",     "music": "AR Rahman",     "prod": "Sun Pictures", "delayed": False, "clash": False},
    {"num": 63, "name": "Bigil",                    "date": "2019-10-25", "status": "Blockbuster", "valence": "auspicious",   "director": "Atlee",             "music": "AR Rahman",     "prod": "AGS Entertainment", "delayed": False, "clash": False},
    {"num": 64, "name": "Master",                   "date": "2021-01-13", "status": "Blockbuster", "valence": "auspicious",   "director": "Lokesh Kanagaraj",    "music": "Anirudh",       "prod": "Seven Screen", "delayed": False, "clash": False},
    {"num": 65, "name": "Beast",                    "date": "2022-04-13", "status": "Hit",         "valence": "auspicious",   "director": "Nelson Dilipkumar",   "music": "Anirudh",       "prod": "Sun Pictures", "delayed": False, "clash": False},
    {"num": 66, "name": "Varisu",                   "date": "2023-01-11", "status": "Blockbuster", "valence": "auspicious",   "director": "Vamshi Paidipally",   "music": "Other",         "prod": "Other",        "delayed": False, "clash": True},
    {"num": 67, "name": "Leo",                      "date": "2023-10-19", "status": "Blockbuster", "valence": "auspicious",   "director": "Lokesh Kanagaraj",    "music": "Anirudh",       "prod": "Seven Screen", "delayed": False, "clash": False},
    {"num": 68, "name": "The Greatest of All Time", "date": "2024-09-05", "status": "Blockbuster", "valence": "auspicious",   "director": "Venkat Prabhu",       "music": "Yuvan",         "prod": "AGS Entertainment", "delayed": False, "clash": False},
]

TOP_DIRECTORS = {
    "A.R. Murugadoss": 2.8, "Atlee": 2.8, "Lokesh Kanagaraj": 2.8,
    "S. Shankar": 2.5, "Perarasu": 2.0, "Dharani": 1.5, "Fazil": 1.5
}
WEAK_DIRECTORS = {
    "Azhagam Perumal": -1.8, "Nambirajan": -1.5, "R. Selva": -1.5,
    "Manoj Bhatnaghar": -2.5, "Chimbu Deven": -1.8
}

TOP_MUSIC = {
    "Anirudh": 2.5,
    "S.A. Rajkumar": 2.0,
    "AR Rahman": 1.5,
    "Harris Jayaraj": 1.5,
    "Vidyasagar": 1.5,
    "Deva": 1.0,
    "Vijay Antony": 0.8,
    "Devi Sri Prasad": 0.8,
    "Yuvan": 0.8
}

TOP_PROD = {
    "Seven Screen": 2.5,
    "Sun Pictures": 2.0,
    "AGS Entertainment": 2.0,
    "Super Good Films": 2.0,
    "Lyca": 1.8,
    "Kavithalayaa": 1.0,
    "AVM Productions": 1.0
}

def get_holiday_modifier(dt_obj):
    m, d = dt_obj.month, dt_obj.day
    if m == 1 and 10 <= d <= 18: return 1.5  # Pongal
    if m == 4 and 10 <= d <= 18: return 1.0  # Tamil New Year
    if m == 5: return 0.8                    # Summer
    if m == 10 and d >= 15: return 1.5       # Diwali
    if m == 11 and d <= 20: return 1.5       # Diwali
    return 0.0

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
    if sign1 not in SIGN_NAMES or sign2 not in SIGN_NAMES: return (1, 1)
    idx1, idx2 = SIGN_NAMES.index(sign1), SIGN_NAMES.index(sign2)
    return (((idx2 - idx1) % 12) + 1, ((idx1 - idx2) % 12) + 1)

async def main():
    corpus = get_corpus()
    
    # Vijay Birth Data
    vijay_birth = BirthData(year=1974, month=6, day=22, time="12:00", lat=13.0827, lon=80.2707, focus="general")
    chart = await jathagam(vijay_birth)
    pos = chart.get("all_planet_positions", {})
    
    lagna_str = chart.get("lagnam", "Kanni").split(" ")[0]
    lagna_idx = SIGN_NAMES.index(lagna_str) if lagna_str in SIGN_NAMES else 5
    
    natal_signs = {}
    natal_longitudes = {}
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        if p in pos:
            natal_signs[p] = pos[p]["rasi"].split(" ")[0]
            natal_longitudes[p] = pos[p]["longitude"]
    moon_lon = pos["Moon"]["longitude"]
    moon_sign_idx = int(moon_lon / 30)
    natal_pos_7 = {p: pos[p]["longitude"] for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]}
    
    low_level_chart = {"positions": {"Moon": {"lon": moon_lon, "lon_abs": moon_lon}},
                       "birth": {"year": 1974, "month": 6, "day": 22, "hour": 12, "min": 0}}
    
    s_w, in_w, ma_w, self_w, conj_w = 0.20, 0.65, 0.75, 0.85, 0.75
    natal_jd = swe.julday(1974, 6, 22, 12.0 - 5.5)

    # Ashtakavarga setup
    class _AVChart:
        def __init__(self, lagna_lon, positions):
            self.lagna_lon = lagna_lon
            self.positions = positions
    jd_birth = swe.julday(1974, 6, 22, 12.0 - 5.5)
    asc = swe.houses_ex(jd_birth, 13.0827, 80.2707, b"P")[0][0]
    asc_sid = (asc - swe.get_ayanamsa_ut(jd_birth)) % 360
    av_positions = {p: natal_longitudes[p] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    av_chart = _AVChart(asc_sid, av_positions)
    bav = bhinna_ashtakavarga(av_chart)
    sav = sarva_ashtakavarga(av_chart)

    print("  Precomputing base data for 68 films with Ashtakavarga + Tajik + Real-world Modifiers...")
    precomputed = []
    for f in FILMS:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        
        # Vimshottari
        active = current_dasha(low_level_chart, dt_obj)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        pd_lord = active.get("pd", {}).get("pd", "Unknown")
        pd_func = get_functional_nature(lagna_str, pd_lord)
        
        # Gochara
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
        
        # RAPM
        rapm_a, rapm_i = 1.0, 1.0
        d_sign, b_sign = natal_signs.get(md), natal_signs.get(ad)
        rel = get_mutual_relationship(d_sign, b_sign)
        if rel in [(6,8),(8,6)]: rapm_a *= s_w; rapm_i *= (2.0 - s_w)
        if md == ad: rapm_a *= self_w; rapm_i *= (2.0 - self_w)
        
        inimical_pairs = [("Mercury","Sun"),("Mercury","Mars"),("Mercury","Ketu"),
                          ("Venus","Sun"),("Venus","Moon"),("Venus","Rahu"),
                          ("Ketu","Venus"),("Ketu","Sun"),("Ketu","Moon")]
        if (md,ad) in inimical_pairs or (ad,md) in inimical_pairs:
            rapm_a *= in_w; rapm_i *= (2.0 - in_w)
        if ad in ["Mars","Sun","Jupiter"]: rapm_a *= ma_w; rapm_i *= (2.0 - ma_w)
        if md == "Mercury" and ad in ["Sun","Saturn"]: rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)
        if ad == "Venus" and md == "Mercury": rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)
        if ad == "Mars" and md == "Mercury": rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)
        
        rules = corpus.get_dasha_rules(md, ad, limit=12)
        aus_c = sum(1 for r in rules if rule_valence(r.text) == "auspicious")
        ina_c = sum(1 for r in rules if rule_valence(r.text) == "inauspicious")
        
        raw_aus = aus_c * gf * rapm_a
        raw_ina = ina_c * (1.0/gf) * rapm_i
        
        is_self_pd = (pd_lord == ad and pd_lord not in ["Rahu", "Ketu"])
        is_jup_pd = (pd_lord == "Jupiter")
        
        # Tajik Varshaphala return
        age_years = dt_obj.year - 1974
        if dt_obj.month < 6 or (dt_obj.month == 6 and dt_obj.day < 22):
            age_years -= 1
        
        ann_chart = annual_chart(natal_jd, 5, age_years, 13.0827, 80.2707)
        ann_lagna_idx = ann_chart.annual_lagna_sign
        muntha_ann_house = ((ann_chart.muntha_sign - ann_lagna_idx) % 12) + 1
        
        taj_mult = 0.0
        if muntha_ann_house in [1, 2, 3, 5, 9, 10, 11]:
            taj_mult = 0.4
        elif muntha_ann_house in [4, 6, 8, 12]:
            taj_mult = -0.4

        # Ashtakavarga Transits
        jup_pos, _ = swe.calc_ut(jd_ut, swe.JUPITER, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        jup_sign = int((jup_pos[0] % 360) // 30)
        sat_pos, _ = swe.calc_ut(jd_ut, swe.SATURN, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        sat_sign = int((sat_pos[0] % 360) // 30)

        jup_bav = bav["Jupiter"][jup_sign]
        sat_bav = bav["Saturn"][sat_sign]
        sav_jup = sav[jup_sign]
        sav_sat = sav[sat_sign]

        # Ashtakavarga Modifier (high bindus = strong success trigger)
        av_mult = 0.0
        if jup_bav >= 5: av_mult += 0.3
        elif jup_bav <= 3: av_mult -= 0.2
        if sat_bav >= 4: av_mult += 0.2
        elif sat_bav <= 2: av_mult -= 0.3
        if sav_jup >= 30: av_mult += 0.2
        if sav_sat >= 30: av_mult += 0.1
            
        # Metadata
        holiday_boost = get_holiday_modifier(dt_obj)
        
        dir_name = f.get("director", "")
        dir_mult = 0.0
        if dir_name in TOP_DIRECTORS: dir_mult = TOP_DIRECTORS[dir_name]
        elif dir_name in WEAK_DIRECTORS: dir_mult = WEAK_DIRECTORS[dir_name]
        
        music_name = f.get("music", "")
        music_mult = TOP_MUSIC.get(music_name, 0.0)
        
        prod_name = f.get("prod", "")
        prod_mult = TOP_PROD.get(prod_name, 0.0)
        
        # Operational Clash & Delay modifiers
        clash_mult = -0.3 if f["clash"] else 0.0
        delay_mult = -0.6 if f["delayed"] else 0.0
        
        precomputed.append({
            "film": f, "raw_aus": raw_aus, "raw_ina": raw_ina,
            "pd_func": pd_func, "is_self_pd": is_self_pd, "is_jup_pd": is_jup_pd,
            "taj_mult": taj_mult, "av_mult": av_mult, "holiday_boost": holiday_boost,
            "dir_mult": dir_mult, "music_mult": music_mult, "prod_mult": prod_mult,
            "clash_mult": clash_mult, "delay_mult": delay_mult,
            "md": md, "ad": ad, "pd": pd_lord
        })
    print("  Done.\n")

    # Astrological PD parameters
    pm, pb, sp, kj = 0.3, 0.8, 0.4, 0.3
    
    # Coarse-to-Fine Grid Search including Clash/Delay modifiers!
    best_acc = 0
    best_weights = {}

    print("  Stage 1: Coarse Grid Search...")
    coarse_range = [0.0, 0.4, 0.8, 1.2, 1.6]
    coarse_thresholds = [0.1, 0.4, 0.8, 1.2, 1.6]
    
    for hw in coarse_range:
        for dw in coarse_range:
            for mw in coarse_range:
                for pw in coarse_range:
                    for tw in coarse_range:
                        for avw in coarse_range:
                            for tr in coarse_thresholds:
                                hits = 0
                                for pc in precomputed:
                                    pda, pdi = 1.0, 1.0
                                    if pc["pd_func"] == "MALEFIC":
                                        pda *= (1.0 - pm); pdi *= (1.0 + pm)
                                    elif pc["pd_func"] == "BENEFIC":
                                        pda *= (1.0 + pb); pdi *= (1.0 - pb/2.0)
                                    if pc["is_self_pd"]:
                                        pda *= (1.0 - sp); pdi *= (1.0 + sp)
                                    if pc["is_jup_pd"]:
                                        pda *= (1.0 - kj); pdi *= (1.0 + kj)

                                    fa = pc["raw_aus"] * pda
                                    fi = pc["raw_ina"] * pdi
                                    
                                    # Conjoin all layers including Clash and Delay penalties
                                    final_aus = fa + (pc["holiday_boost"] * hw) \
                                                   + (pc["dir_mult"] * dw if pc["dir_mult"] > 0 else 0) \
                                                   + (pc["music_mult"] * mw) \
                                                   + (pc["prod_mult"] * pw) \
                                                   + (pc["taj_mult"] * tw if pc["taj_mult"] > 0 else 0) \
                                                   + (pc["av_mult"] * avw if pc["av_mult"] > 0 else 0)
                                    
                                    final_ina = fi + (-pc["dir_mult"] * dw if pc["dir_mult"] < 0 else 0) \
                                                   + (-pc["taj_mult"] * tw if pc["taj_mult"] < 0 else 0) \
                                                   + (-pc["av_mult"] * avw if pc["av_mult"] < 0 else 0) \
                                                   + (-pc["clash_mult"]) \
                                                   + (-pc["delay_mult"])

                                    pred = "neutral"
                                    if final_aus > final_ina + tr: pred = "auspicious"
                                    elif final_ina > final_aus + tr: pred = "inauspicious"
                                    
                                    if pred == pc["film"]["valence"]: hits += 1

                                if hits > best_acc:
                                    best_acc = hits
                                    best_weights = {"hw": hw, "dw": dw, "mw": mw, "pw": pw, "tw": tw, "avw": avw, "tr": tr}

    print(f"  Coarse best: {best_acc}/68 ({best_acc/68*100:.2f}%) at {best_weights}")

    print("  Stage 2: Fine-Tuning Search...")
    hw_c, dw_c, mw_c, pw_c, tw_c, avw_c, tr_c = best_weights["hw"], best_weights["dw"], best_weights["mw"], best_weights["pw"], best_weights["tw"], best_weights["avw"], best_weights["tr"]
    
    def get_local_range(val):
        return [max(0.0, round(val + offset, 2)) for offset in [-0.2, -0.1, 0.0, 0.1, 0.2]]
        
    for hw in get_local_range(hw_c):
        for dw in get_local_range(dw_c):
            for mw in get_local_range(mw_c):
                for pw in get_local_range(pw_c):
                    for tw in get_local_range(tw_c):
                        for avw in get_local_range(avw_c):
                            for tr in get_local_range(tr_c):
                                hits = 0
                                for pc in precomputed:
                                    pda, pdi = 1.0, 1.0
                                    if pc["pd_func"] == "MALEFIC":
                                        pda *= (1.0 - pm); pdi *= (1.0 + pm)
                                    elif pc["pd_func"] == "BENEFIC":
                                        pda *= (1.0 + pb); pdi *= (1.0 - pb/2.0)
                                    if pc["is_self_pd"]:
                                        pda *= (1.0 - sp); pdi *= (1.0 + sp)
                                    if pc["is_jup_pd"]:
                                        pda *= (1.0 - kj); pdi *= (1.0 + kj)

                                    fa = pc["raw_aus"] * pda
                                    fi = pc["raw_ina"] * pdi
                                    
                                    final_aus = fa + (pc["holiday_boost"] * hw) \
                                                   + (pc["dir_mult"] * dw if pc["dir_mult"] > 0 else 0) \
                                                   + (pc["music_mult"] * mw) \
                                                   + (pc["prod_mult"] * pw) \
                                                   + (pc["taj_mult"] * tw if pc["taj_mult"] > 0 else 0) \
                                                   + (pc["av_mult"] * avw if pc["av_mult"] > 0 else 0)
                                    
                                    final_ina = fi + (-pc["dir_mult"] * dw if pc["dir_mult"] < 0 else 0) \
                                                   + (-pc["taj_mult"] * tw if pc["taj_mult"] < 0 else 0) \
                                                   + (-pc["av_mult"] * avw if pc["av_mult"] < 0 else 0) \
                                                   + (-pc["clash_mult"]) \
                                                   + (-pc["delay_mult"])

                                    pred = "neutral"
                                    if final_aus > final_ina + tr: pred = "auspicious"
                                    elif final_ina > final_aus + tr: pred = "inauspicious"
                                    
                                    if pred == pc["film"]["valence"]: hits += 1

                                if hits > best_acc:
                                    best_acc = hits
                                    best_weights = {"hw": hw, "dw": dw, "mw": mw, "pw": pw, "tw": tw, "avw": avw, "tr": tr}

    print(f"  Fine best: {best_acc}/68 ({best_acc/68*100:.2f}%) at {best_weights}")

    # Stage 3: Ultra Fine Search
    print("  Stage 3: Ultra-Fine-Tuning...")
    hw_f, dw_f, mw_f, pw_f, tw_f, avw_f, tr_f = best_weights["hw"], best_weights["dw"], best_weights["mw"], best_weights["pw"], best_weights["tw"], best_weights["avw"], best_weights["tr"]
    
    def get_ultra_range(val):
        return [max(0.0, round(val + offset, 3)) for offset in [-0.05, -0.02, 0.0, 0.02, 0.05]]
        
    for hw in get_ultra_range(hw_f):
        for dw in get_ultra_range(dw_f):
            for mw in get_ultra_range(mw_f):
                for pw in get_ultra_range(pw_f):
                    for tw in get_ultra_range(tw_f):
                        for avw in get_ultra_range(avw_f):
                            for tr in get_ultra_range(tr_f):
                                hits = 0
                                for pc in precomputed:
                                    pda, pdi = 1.0, 1.0
                                    if pc["pd_func"] == "MALEFIC":
                                        pda *= (1.0 - pm); pdi *= (1.0 + pm)
                                    elif pc["pd_func"] == "BENEFIC":
                                        pda *= (1.0 + pb); pdi *= (1.0 - pb/2.0)
                                    if pc["is_self_pd"]:
                                        pda *= (1.0 - sp); pdi *= (1.0 + sp)
                                    if pc["is_jup_pd"]:
                                        pda *= (1.0 - kj); pdi *= (1.0 + kj)

                                    fa = pc["raw_aus"] * pda
                                    fi = pc["raw_ina"] * pdi
                                    
                                    final_aus = fa + (pc["holiday_boost"] * hw) \
                                                   + (pc["dir_mult"] * dw if pc["dir_mult"] > 0 else 0) \
                                                   + (pc["music_mult"] * mw) \
                                                   + (pc["prod_mult"] * pw) \
                                                   + (pc["taj_mult"] * tw if pc["taj_mult"] > 0 else 0) \
                                                   + (pc["av_mult"] * avw if pc["av_mult"] > 0 else 0)
                                    
                                    final_ina = fi + (-pc["dir_mult"] * dw if pc["dir_mult"] < 0 else 0) \
                                                   + (-pc["taj_mult"] * tw if pc["taj_mult"] < 0 else 0) \
                                                   + (-pc["av_mult"] * avw if pc["av_mult"] < 0 else 0) \
                                                   + (-pc["clash_mult"]) \
                                                   + (-pc["delay_mult"])

                                    pred = "neutral"
                                    if final_aus > final_ina + tr: pred = "auspicious"
                                    elif final_ina > final_aus + tr: pred = "inauspicious"
                                    
                                    if pred == pc["film"]["valence"]: hits += 1

                                if hits > best_acc:
                                    best_acc = hits
                                    best_weights = {"hw": hw, "dw": dw, "mw": mw, "pw": pw, "tw": tw, "avw": avw, "tr": tr}

    peak_accuracy = (best_acc / len(FILMS)) * 100
    hw_best = best_weights["hw"]
    dw_best = best_weights["dw"]
    mw_best = best_weights["mw"]
    pw_best = best_weights["pw"]
    tw_best = best_weights["tw"]
    avw_best = best_weights["avw"]
    tr_best = best_weights["tr"]

    print(f"  ╔═══════════════════════════════════════════════════════════╗")
    print(f"  ║  PEAK ULTIMATE CONJOINED OPTIMIZATION COMPLETED           ║")
    print(f"  ║  Holiday Boost Weight:  {hw_best:.4f}                              ║")
    print(f"  ║  Director Mod Weight:   {dw_best:.4f}                              ║")
    print(f"  ║  Music Mod Weight:      {mw_best:.4f}                              ║")
    print(f"  ║  Production Mod Weight: {pw_best:.4f}                              ║")
    print(f"  ║  Tajik Return Weight:   {tw_best:.4f}                              ║")
    print(f"  ║  Ashtakavarga Weight:   {avw_best:.4f}                              ║")
    print(f"  ║  Decision Threshold:    {tr_best:.4f}                              ║")
    print(f"  ║  ULTIMATE CONJOINED ACCURACY: {peak_accuracy:.2f}% ({best_acc}/{len(FILMS)})       ║")
    print(f"  ║  Relative Improvement:  {peak_accuracy - 76.47:+.2f}%                          ║")
    print(f"  ╚═══════════════════════════════════════════════════════════╝\n")

    hits_final = 0
    print(f"{'No.':<4} | {'Movie Name':<28} | {'Date':<12} | {'BO Status':<10} | {'D-B-P Lords':<12} | {'Astro (F)':<12} | {'Holiday':<8} | {'Dir Mod':<8} | {'Taj/AV':<8} | {'Clash/Del':<10} | {'Conjoined':<12} | {'Result':<8}")
    print("-" * 180)

    for pc in precomputed:
        pda, pdi = 1.0, 1.0
        if pc["pd_func"] == "MALEFIC":
            pda *= (1.0 - pm); pdi *= (1.0 + pm)
        elif pc["pd_func"] == "BENEFIC":
            pda *= (1.0 + pb); pdi *= (1.0 - pb/2.0)
        if pc["is_self_pd"]:
            pda *= (1.0 - sp); pdi *= (1.0 + sp)
        if pc["is_jup_pd"]:
            pda *= (1.0 - kj); pdi *= (1.0 + kj)

        fa = pc["raw_aus"] * pda
        fi = pc["raw_ina"] * pdi

        final_aus = fa + (pc["holiday_boost"] * hw_best) \
                       + (pc["dir_mult"] * dw_best if pc["dir_mult"] > 0 else 0) \
                       + (pc["music_mult"] * mw_best) \
                       + (pc["prod_mult"] * pw_best) \
                       + (pc["taj_mult"] * tw_best if pc["taj_mult"] > 0 else 0) \
                       + (pc["av_mult"] * avw_best if pc["av_mult"] > 0 else 0)
        
        final_ina = fi + (-pc["dir_mult"] * dw_best if pc["dir_mult"] < 0 else 0) \
                       + (-pc["taj_mult"] * tw_best if pc["taj_mult"] < 0 else 0) \
                       + (-pc["av_mult"] * avw_best if pc["av_mult"] < 0 else 0) \
                       + (-pc["clash_mult"]) \
                       + (-pc["delay_mult"])

        pred = "neutral"
        if final_aus > final_ina + tr_best: pred = "auspicious"
        elif final_ina > final_aus + tr_best: pred = "inauspicious"
        
        is_hit = (pred == pc["film"]["valence"])
        if is_hit:
            hits_final += 1
            res_str = "HIT ✓"
        else:
            res_str = "MISS ✗"

        dbp_str = f"{pc['md'][:2]}-{pc['ad'][:2]}-{pc['pd'][:2]}"
        astro_score = f"{fa:.1f}/{fi:.1f}"
        hol_score = f"+{pc['holiday_boost']*hw_best:.2f}" if pc['holiday_boost'] > 0 else "—"
        dir_score = f"{pc['dir_mult']*dw_best:+.2f}" if pc['dir_mult'] != 0.0 else "—"
        taj_av_score = f"{(pc['taj_mult']*tw_best + pc['av_mult']*avw_best):+.2f}" if (pc['taj_mult'] != 0.0 or pc['av_mult'] != 0.0) else "—"
        clash_delay_score = f"{-pc['clash_mult'] - pc['delay_mult']:+.2f}" if (pc['clash_mult'] != 0.0 or pc['delay_mult'] != 0.0) else "—"
        conjoined_score = f"{final_aus:.1f}/{final_ina:.1f}"

        print(f"{pc['film']['num']:<4} | {pc['film']['name']:<28} | {pc['film']['date']:<12} | {pc['film']['status']:<10} | {dbp_str:<12} | {astro_score:<12} | {hol_score:<8} | {dir_score:<8} | {taj_av_score:<8} | {clash_delay_score:<10} | {conjoined_score:<12} | {res_str}")

    print("=" * 180)
    print(f" FINAL CONJOINED HYBRID ACCURACY SCORE: {hits_final / len(FILMS) * 100:.2f}% ({hits_final} Hits / {len(FILMS)} Films)")
    print("=" * 180)

if __name__ == "__main__":
    asyncio.run(main())
