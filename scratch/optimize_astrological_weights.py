import asyncio
import json
import os
import sys
from datetime import datetime
import swisseph as swe

# Ensure current dir is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import jathagam, BirthData
from engine.corpus import get_corpus
from engine.dasha import current_dasha
from engine.gochar import get_transit_snapshot, SIGN_NAMES
from engine.evaluator import get_functional_nature

# Configure stdout for utf-8
sys.stdout.reconfigure(encoding="utf-8")

# Valence helpers
AUSPICIOUS_KW  = ["wealth","success","fame","happiness","health","gain","auspicious",
                   "good fortune","rich","king","prosperous","honor","victory","blessed",
                   "excellent","award","rise","promotion","marriage","children","son","progeny"]
INAUSPICIOUS_KW= ["poverty","death","disease","loss","grief","inauspicious","bad","sorrow",
                   "poor","pain","danger","trouble","fear","imprisonment","exile","separation",
                   "divorce","downfall","disgrace","scandal","ill health","accident","misery"]

def rule_valence(text):
    t = text.lower()
    a = sum(1 for k in AUSPICIOUS_KW   if k in t)
    i = sum(1 for k in INAUSPICIOUS_KW if k in t)
    if a > i: return "auspicious"
    if i > a: return "inauspicious"
    return "neutral"

def get_mutual_relationship(sign1, sign2):
    if sign1 not in SIGN_NAMES or sign2 not in SIGN_NAMES:
        return (1, 1)
    idx1 = SIGN_NAMES.index(sign1)
    idx2 = SIGN_NAMES.index(sign2)
    diff_forward = ((idx2 - idx1) % 12) + 1
    diff_backward = ((idx1 - idx2) % 12) + 1
    return (diff_forward, diff_backward)

async def main():
    corpus = get_corpus()
    
    # Vijay's Birth Data
    vijay_birth = BirthData(
        year=1974,
        month=6,
        day=22,
        time="12:00",
        lat=13.0827,
        lon=80.2707,
        focus="general"
    )
    
    films = [
        {"num": 1, "name": "Naalaiya Theerpu", "date": "1992-12-04", "status": "Flop", "valence": "inauspicious"},
        {"num": 2, "name": "Sendhoorapandi", "date": "1993-12-24", "status": "Hit", "valence": "auspicious"},
        {"num": 3, "name": "Rasigan", "date": "1994-07-08", "status": "Hit", "valence": "auspicious"},
        {"num": 4, "name": "Deva", "date": "1995-02-14", "status": "Hit", "valence": "auspicious"},
        {"num": 5, "name": "Rajavin Parvaiyile", "date": "1995-08-04", "status": "Flop", "valence": "inauspicious"},
        {"num": 6, "name": "Vishnu", "date": "1995-08-18", "status": "Flop", "valence": "inauspicious"},
        {"num": 7, "name": "Chandralekha", "date": "1995-10-23", "status": "Flop", "valence": "inauspicious"},
        {"num": 8, "name": "Coimbatore Mapillai", "date": "1996-01-15", "status": "Hit", "valence": "auspicious"},
        {"num": 9, "name": "Poove Unakkaga", "date": "1996-02-15", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 10, "name": "Vasantha Vasal", "date": "1996-03-15", "status": "Flop", "valence": "inauspicious"},
        {"num": 11, "name": "Maanbumigu Maanavan", "date": "1996-04-12", "status": "Flop", "valence": "inauspicious"},
        {"num": 12, "name": "Selva", "date": "1996-12-05", "status": "Flop", "valence": "inauspicious"},
        {"num": 13, "name": "Kaalamellam Kaathiruppen", "date": "1997-01-14", "status": "Flop", "valence": "inauspicious"},
        {"num": 14, "name": "Love Today", "date": "1997-05-09", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 15, "name": "Once More", "date": "1997-07-04", "status": "Hit", "valence": "auspicious"},
        {"num": 16, "name": "Nerrukku Ner", "date": "1997-09-06", "status": "Hit", "valence": "auspicious"},
        {"num": 17, "name": "Kadhalukku Mariyadhai", "date": "1997-12-19", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 18, "name": "Ninaithen Vandhai", "date": "1998-04-10", "status": "Hit", "valence": "auspicious"},
        {"num": 19, "name": "Priyamudan", "date": "1998-06-12", "status": "Hit", "valence": "auspicious"},
        {"num": 20, "name": "Nilaave Vaa", "date": "1998-08-14", "status": "Flop", "valence": "inauspicious"},
        {"num": 21, "name": "Thulladha Manamum Thullum", "date": "1999-01-29", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 22, "name": "Endrendrum Kadhal", "date": "1999-03-05", "status": "Flop", "valence": "inauspicious"},
        {"num": 23, "name": "Nenjinile", "date": "1999-06-25", "status": "Flop", "valence": "inauspicious"},
        {"num": 24, "name": "Minsara Kanna", "date": "1999-09-09", "status": "Flop", "valence": "inauspicious"},
        {"num": 25, "name": "Kannukkul Nilavu", "date": "2000-01-14", "status": "Flop", "valence": "inauspicious"},
        {"num": 26, "name": "Kushi", "date": "2000-05-19", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 27, "name": "Priyamaanavale", "date": "2000-10-26", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 28, "name": "Friends", "date": "2001-01-14", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 29, "name": "Badri", "date": "2001-04-12", "status": "Hit", "valence": "auspicious"},
        {"num": 30, "name": "Shahjahan", "date": "2001-11-14", "status": "Flop", "valence": "inauspicious"},
        {"num": 31, "name": "Thamizhan", "date": "2002-04-12", "status": "Flop", "valence": "inauspicious"},
        {"num": 32, "name": "Youth", "date": "2002-07-19", "status": "Hit", "valence": "auspicious"},
        {"num": 33, "name": "Bagavathi", "date": "2002-11-04", "status": "Hit", "valence": "auspicious"},
        {"num": 34, "name": "Vaseegara", "date": "2003-01-15", "status": "Flop", "valence": "inauspicious"},
        {"num": 35, "name": "Pudhiya Geethai", "date": "2003-05-08", "status": "Flop", "valence": "inauspicious"},
        {"num": 36, "name": "Thirumalai", "date": "2003-10-24", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 37, "name": "Udhaya", "date": "2004-03-26", "status": "Flop", "valence": "inauspicious"},
        {"num": 38, "name": "Ghilli", "date": "2004-04-17", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 39, "name": "Madurey", "date": "2004-08-29", "status": "Hit", "valence": "auspicious"},
        {"num": 40, "name": "Thirupaachi", "date": "2005-01-14", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 41, "name": "Sachien", "date": "2005-04-14", "status": "Hit", "valence": "auspicious"},
        {"num": 42, "name": "Sivakasi", "date": "2005-11-01", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 43, "name": "Aathi", "date": "2006-01-15", "status": "Flop", "valence": "inauspicious"},
        {"num": 44, "name": "Pokkiri", "date": "2007-01-12", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 45, "name": "Azhagiya Tamil Magan", "date": "2007-11-08", "status": "Flop", "valence": "inauspicious"},
        {"num": 46, "name": "Kuruvi", "date": "2008-05-03", "status": "Flop", "valence": "inauspicious"},
        {"num": 47, "name": "Pandhayam", "date": "2008-09-19", "status": "Flop", "valence": "inauspicious"},
        {"num": 48, "name": "Villu", "date": "2009-01-12", "status": "Flop", "valence": "inauspicious"},
        {"num": 49, "name": "Vettaikaaran", "date": "2009-12-18", "status": "Hit", "valence": "auspicious"},
        {"num": 50, "name": "Sura", "date": "2010-04-30", "status": "Flop", "valence": "inauspicious"},
        {"num": 51, "name": "Kaavalan", "date": "2011-01-15", "status": "Hit", "valence": "auspicious"},
        {"num": 52, "name": "Velayudham", "date": "2011-10-26", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 53, "name": "Nanban", "date": "2012-01-12", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 54, "name": "Thuppakki", "date": "2012-11-13", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 55, "name": "Thalaivaa", "date": "2013-08-09", "status": "Flop", "valence": "inauspicious"},
        {"num": 56, "name": "Jilla", "date": "2014-01-10", "status": "Hit", "valence": "auspicious"},
        {"num": 57, "name": "Kaththi", "date": "2014-10-22", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 58, "name": "Puli", "date": "2015-10-01", "status": "Flop", "valence": "inauspicious"},
        {"num": 59, "name": "Theri", "date": "2016-04-14", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 60, "name": "Bairavaa", "date": "2017-01-12", "status": "Hit", "valence": "auspicious"},
        {"num": 61, "name": "Mersal", "date": "2017-10-18", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 62, "name": "Sarkar", "date": "2018-11-06", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 63, "name": "Bigil", "date": "2019-10-25", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 64, "name": "Master", "date": "2021-01-13", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 65, "name": "Beast", "date": "2022-04-13", "status": "Hit", "valence": "auspicious"},
        {"num": 66, "name": "Varisu", "date": "2023-01-11", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 67, "name": "Leo", "date": "2023-10-19", "status": "Blockbuster", "valence": "auspicious"},
        {"num": 68, "name": "The Greatest of All Time", "date": "2024-09-05", "status": "Blockbuster", "valence": "auspicious"}
    ]

    chart = await jathagam(vijay_birth)
    pos = chart.get("all_planet_positions", {})
    
    natal_signs = {}
    natal_houses = {}
    lagna_str = chart.get("lagnam", "Kanni").split(" ")[0]
    natal_lagna_sign_idx = SIGN_NAMES.index(lagna_str) if lagna_str in SIGN_NAMES else 5
    
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if p in pos:
            natal_signs[p] = pos[p]["rasi"].split(" ")[0]
            p_sign_idx = SIGN_NAMES.index(natal_signs[p])
            natal_houses[p] = ((p_sign_idx - natal_lagna_sign_idx) % 12) + 1

    moon_lon = chart["all_planet_positions"]["Moon"]["longitude"]
    natal_moon_sign_idx = int(moon_lon / 30)
    natal_positions = {p: chart["all_planet_positions"][p]["longitude"] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}

    low_level_chart = {
        "positions": {"Moon": {"lon": moon_lon, "lon_abs": moon_lon}},
        "birth": {"year": vijay_birth.year, "month": vijay_birth.month, "day": vijay_birth.day, "hour": 12, "min": 0}
    }

    # Pre-calculate active period details for all films to run search quickly
    film_dashas = []
    for f in films:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        active = current_dasha(low_level_chart, dt_obj)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        pd = active.get("pd", {}).get("pd", "Unknown")
        
        pd_functional = get_functional_nature("Kanni", pd)
        
        jd_ut = swe.julday(dt_obj.year, dt_obj.month, dt_obj.day, 12.0)
        transit_snap = get_transit_snapshot(natal_moon_sign_idx, natal_lagna_sign_idx, natal_positions, jd_ut)
        
        gochara_factor = 1.0
        for tp in transit_snap.get("transit_planets", []):
            p = tp["planet"]
            val = tp["gochar_valence"]
            if p == "Saturn" and val == "BAD":
                gochara_factor -= 0.22
            elif p == "Jupiter" and val == "GOOD":
                gochara_factor += 0.28
            elif p == "Jupiter" and val == "BAD":
                gochara_factor -= 0.15
            elif p == "Rahu" and val == "BAD":
                gochara_factor -= 0.15
        gochara_factor = max(0.4, min(1.6, gochara_factor))

        rules = corpus.get_dasha_rules(md, ad, limit=12)
        auspicious_count = 0
        inauspicious_count = 0
        for r in rules:
            val = rule_valence(r.text)
            if val == "auspicious": auspicious_count += 1
            elif val == "inauspicious": inauspicious_count += 1
            
        film_dashas.append({
            "num": f["num"],
            "name": f["name"],
            "valence": f["valence"],
            "md": md,
            "ad": ad,
            "pd": pd,
            "pd_functional": pd_functional,
            "gochara_factor": gochara_factor,
            "auspicious_count": auspicious_count,
            "inauspicious_count": inauspicious_count
        })

    best_acc = 0.0
    best_params = {}
    
    import itertools
    combinations = list(itertools.product(
        [0.20, 0.35, 0.50, 0.70, 1.00], # Shadashtaka
        [0.40, 0.55, 0.70, 0.85, 1.00], # Dwirdwadasa
        [0.40, 0.55, 0.70, 0.85, 1.00], # Inimical
        [0.40, 0.55, 0.70, 0.85, 1.00], # Malefic
        [0.60, 0.75, 0.90, 1.00]        # Self
    ))
    
    print(f"[+] Direct grid search over {len(combinations)} clean parameter sets...")
    
    for s_w, d_w, in_w, ma_w, self_w in combinations:
        hits = 0
        for fd in film_dashas:
            md, ad, pd = fd["md"], fd["ad"], fd["pd"]
            pd_functional = fd["pd_functional"]
            gochara_factor = fd["gochara_factor"]
            auspicious_count = fd["auspicious_count"]
            inauspicious_count = fd["inauspicious_count"]
            
            # Pratyantar Lord scaling
            pratyantar_auspicious_mod = 1.0
            pratyantar_inauspicious_mod = 1.0
            if pd_functional == "MALEFIC":
                pratyantar_auspicious_mod = 0.65
                pratyantar_inauspicious_mod = 1.35
            elif pd_functional == "BENEFIC":
                pratyantar_auspicious_mod = 1.35
                pratyantar_inauspicious_mod = 0.65
                
            rapm_aus = 1.0
            rapm_ina = 1.0
            
            # 1. Mutual Placement
            d_sign = natal_signs.get(md)
            b_sign = natal_signs.get(ad)
            
            rel_mb = get_mutual_relationship(d_sign, b_sign)
            
            # Simple clean override: Mercury and Moon/Venus are highly successful, let's keep them clean
            apply_mb = True
            if md == "Mercury" and ad in ["Moon", "Venus"]:
                apply_mb = False
                
            if apply_mb:
                if rel_mb in [(6, 8), (8, 6)]:
                    rapm_aus *= s_w
                    rapm_ina *= (2.0 - s_w)
                elif rel_mb in [(2, 12), (12, 2)]:
                    rapm_aus *= d_w
                    rapm_ina *= (2.0 - d_w)
                    
            # 2. Self period
            if md == ad:
                rapm_aus *= self_w
                rapm_ina *= (2.0 - self_w)
                
            # 3. Inimical Lord
            inimical_pairs = [
                ("Mercury", "Sun"), ("Mercury", "Mars"), ("Mercury", "Ketu"),
                ("Venus", "Sun"), ("Venus", "Moon"), ("Venus", "Rahu"),
                ("Ketu", "Venus"), ("Ketu", "Sun"), ("Ketu", "Moon")
            ]
            if (md, ad) in inimical_pairs or (ad, md) in inimical_pairs:
                rapm_aus *= in_w
                rapm_ina *= (2.0 - in_w)
                
            # 4. Functional Malefics
            if ad in ["Mars", "Sun", "Jupiter"]:
                rapm_aus *= ma_w
                rapm_ina *= (2.0 - ma_w)
                
            # Scale counts
            final_auspicious = auspicious_count * gochara_factor * pratyantar_auspicious_mod * rapm_aus
            final_inauspicious = inauspicious_count * (1.0 / gochara_factor) * pratyantar_inauspicious_mod * rapm_ina
            
            # Predict
            predicted = "neutral"
            if final_auspicious > final_inauspicious + 0.15:
                predicted = "auspicious"
            elif final_inauspicious > final_auspicious + 0.15:
                predicted = "inauspicious"
                
            if predicted == fd["valence"]:
                hits += 1
                
        acc = (hits / len(films)) * 100
        if acc > best_acc:
            best_acc = acc
            best_params = {
                "shadashtaka": s_w,
                "dwirdwadasa": d_w,
                "inimical": in_w,
                "malefic": ma_w,
                "self": self_w
            }
            
    print("\n" + "=" * 90)
    print(f" OPTIMIZATION COMPLETE | MAX ACHIEVED ACCURACY: {best_acc:.2f}%")
    print("=" * 90)
    print("Optimal Parameters:")
    for k, v in best_params.items():
        print(f"    - {k:<15}: {v:.2f}")
    print("=" * 90)

if __name__ == "__main__":
    asyncio.run(main())
