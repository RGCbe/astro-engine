import asyncio
import json
import os
import sys
from datetime import datetime

# Ensure current dir is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import jathagam, BirthData
from engine.corpus import get_corpus
from engine.dasha import current_dasha

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

async def run_vijay_full_filmography():
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
    
    # The complete 68-film filmography of Thalapathy Vijay as lead actor (1992-2024)
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

    print("=" * 110)
    print("     VIJAY 68-FILM BACKTEST (corpus rule valence vs known hit/flop — NOT live API)")
    print("     See docs/VIJAY_ACCURACY_EXPLAINED.md — pooled rule % is NOT per-movie prediction")
    print("=" * 110)

    chart = await jathagam(vijay_birth)
    
    # Construct low-level dict
    moon_lon = chart["all_planet_positions"]["Moon"]["longitude"]
    low_level_chart = {
        "positions": {
            "Moon": {
                "lon": moon_lon,
                "lon_abs": moon_lon
            }
        },
        "birth": {
            "year": vijay_birth.year,
            "month": vijay_birth.month,
            "day": vijay_birth.day,
            "hour": 12,
            "min": 0
        }
    }

    hits_total = 0
    misses_total = 0
    films_correct = 0
    films_with_rules = 0

    print(f"{'No.':<4} | {'Movie Name':<28} | {'Release Date':<12} | {'Box Office':<11} | {'Active Dasa-Bhukti':<24} | {'Rule%':<8} | {'Film OK':<7}")
    print("-" * 118)

    for f in films:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        active = current_dasha(low_level_chart, dt_obj)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        
        # Query rules for active Dasa-Bhukti
        rules = corpus.get_dasha_rules(md, ad, limit=10)
        
        hits = 0
        misses = 0
        
        for r in rules:
            val = rule_valence(r.text)
            if val == "neutral":
                continue
            if val == f["valence"]:
                hits += 1
            else:
                misses += 1
                
        hits_total += hits
        misses_total += misses
        total = hits + misses
        accuracy_str = "N/A"
        film_ok = "—"
        if total > 0:
            accuracy_str = f"{(hits / total * 100):.1f}%"
            films_with_rules += 1
            majority_auspicious = hits > misses
            majority_inauspicious = misses > hits
            expected_auspicious = f["valence"] == "auspicious"
            if (expected_auspicious and majority_auspicious) or (not expected_auspicious and majority_inauspicious):
                films_correct += 1
                film_ok = "YES"
            else:
                film_ok = "NO"

        dasha_str = f"{md}-{ad}"
        print(f"{f['num']:<4} | {f['name']:<28} | {f['date']:<12} | {f['status']:<11} | {dasha_str:<24} | {accuracy_str:<8} | {film_ok:<7}")

    grand_total = hits_total + misses_total
    grand_accuracy = (hits_total / grand_total * 100) if grand_total > 0 else 0
    film_pct = (100 * films_correct / films_with_rules) if films_with_rules else 0
    print("=" * 118)
    print(f" POOLED CORPUS RULE MATCH: {grand_accuracy:.2f}% ({hits_total}/{grand_total} rule snippets)")
    print(f" PER-FILM MAJORITY VALENCE:  {film_pct:.1f}% ({films_correct}/{films_with_rules} films)")
    print(" (Per-film = majority of dasha rules match hit/flop — honest binary metric)")
    print("=" * 118)

if __name__ == "__main__":
    asyncio.run(run_vijay_full_filmography())
