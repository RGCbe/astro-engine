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

async def run_vijay_complete_audit():
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
    
    # Comprehensive granular list of 24 events (both tragic, stressful, and highly successful)
    events = [
        {"date": "1980-08-05", "type": "MAJOR_LOSS", "desc": "Tragic death of his younger sister Vidhya (deeply affected his personality)", "valence": "inauspicious"},
        {"date": "1984-11-09", "type": "CAREER_START", "desc": "Child artist debut in film 'Vetri'", "valence": "auspicious"},
        {"date": "1992-12-04", "type": "CAREER_START", "desc": "Lead actor debut in 'Naalaiya Theerpu'", "valence": "auspicious"},
        {"date": "1996-02-15", "type": "CAREER_PEAK", "desc": "Romantic breakthrough 'Poove Unakkaga' (super hit)", "valence": "auspicious"},
        {"date": "1997-09-05", "type": "AWARD", "desc": "Best Actor State Award for 'Kadhalukku Mariyadhai'", "valence": "auspicious"},
        {"date": "1999-08-25", "type": "MARRIAGE", "desc": "Marriage to Sangeetha Sornalingam", "valence": "auspicious"},
        {"date": "2000-08-26", "type": "CHILDREN_BORN", "desc": "Birth of his son Jason Sanjay", "valence": "auspicious"},
        {"date": "2001-01-14", "type": "CAREER_PEAK", "desc": "Release of cult classic blockbuster 'Friends'", "valence": "auspicious"},
        {"date": "2003-10-24", "type": "CAREER_PEAK", "desc": "Action transition 'Thirumalai'", "valence": "auspicious"},
        {"date": "2004-04-17", "type": "CAREER_PEAK", "desc": "Mega-blockbuster 'Ghilli' (broke Tamil cinema records)", "valence": "auspicious"},
        {"date": "2005-09-09", "type": "CHILDREN_BORN", "desc": "Birth of his daughter Divya Shasha", "valence": "auspicious"},
        {"date": "2007-01-12", "type": "CAREER_PEAK", "desc": "Action blockbuster 'Pokkiri'", "valence": "auspicious"},
        {"date": "2011-01-15", "type": "CAREER_PEAK", "desc": "Release of 'Kaavalan' (overcoming intense political ban attempts to become a hit)", "valence": "auspicious"},
        {"date": "2012-11-13", "type": "CAREER_PEAK", "desc": "Blockbuster 'Thuppakki' (his first 100-crore film)", "valence": "auspicious"},
        {"date": "2014-10-22", "type": "CAREER_PEAK", "desc": "Blockbuster 'Kaththi' (crosses 100 crores amid intense pre-release protests)", "valence": "auspicious"},
        {"date": "2015-09-30", "type": "SCANDAL", "desc": "Stressful Income Tax raids at his residence on the eve of 'Puli' release", "valence": "inauspicious"},
        {"date": "2016-04-14", "type": "CAREER_PEAK", "desc": "Blockbuster 'Theri' (crosses 150 crores)", "valence": "auspicious"},
        {"date": "2017-10-18", "type": "CAREER_PEAK", "desc": "Blockbuster 'Mersal' (crosses 250 crores amid massive political dialogues debate)", "valence": "auspicious"},
        {"date": "2018-11-06", "type": "CAREER_PEAK", "desc": "Blockbuster 'Sarkar' (protests and legal cases by ruling govt due to political themes)", "valence": "auspicious"},
        {"date": "2021-01-13", "type": "CAREER_PEAK", "desc": "Blockbuster 'Master' (theatre-saver release with 50% capacity during COVID)", "valence": "auspicious"},
        {"date": "2023-10-19", "type": "CAREER_PEAK", "desc": "Blockbuster 'Leo' (crosses 600 crores globally)", "valence": "auspicious"},
        {"date": "2024-02-02", "type": "POLITICAL_OFFICE", "desc": "Officially launches TVK political party, declares candidacy for 2026", "valence": "auspicious"},
        {"date": "2024-09-05", "type": "CAREER_PEAK", "desc": "Blockbuster 'GOAT' (Greatest of All Time, his penultimate film)", "valence": "auspicious"},
        {"date": "2024-10-27", "type": "POLITICAL_OFFICE", "desc": " TVK First State Conference in Vikravandi (attracted over 3 lakh people)", "valence": "auspicious"}
    ]

    print("=" * 100)
    print("             THALAPATHY VIJAY: COMPLETE LIFE TIMELINE (24 GRANULAR EVENTS) BACKTEST")
    print("=" * 100)

    chart = await jathagam(vijay_birth)
    pos = chart.get("positions", {})
    lagna_sign = chart.get("lagnam", "Unknown")
    moon_sign = chart.get("janma_rasi", "Unknown")
    moon_star = chart.get("janma_nakshatra", "Unknown")
    print(f"[+] Sidereal Chart: Lagna={lagna_sign} | Moon={moon_sign} | Nakshatra={moon_star}")
    
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

    for idx, ev in enumerate(events):
        dt_obj = datetime.strptime(ev["date"], "%Y-%m-%d")
        active = current_dasha(low_level_chart, dt_obj)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        pd = active.get("pd", {}).get("pd", "Unknown")
        
        print(f"\n[#{idx+1}] Event: {ev['type']} | Date: {ev['date']}")
        print(f"    Description: {ev['desc']}")
        print(f"    Timeline Dasha: {md} Dasa | {ad} Bhukti | {pd} Pratyantar")
        
        # Query rules for active Dasha-Bhukti combo
        rules = corpus.get_dasha_rules(md, ad, limit=15)
        
        hits = 0
        misses = 0
        samples = []
        
        for r in rules:
            val = rule_valence(r.text)
            if val == "neutral":
                continue
            if val == ev["valence"]:
                hits += 1
                if len(samples) < 2:
                    samples.append(f"[HIT] {r.text} ({r.source_label})")
            else:
                misses += 1
                if len(samples) < 2:
                    samples.append(f"[MISFIRE] {r.text} ({r.source_label})")
        
        hits_total += hits
        misses_total += misses
        total = hits + misses
        accuracy = (hits / total * 100) if total > 0 else 0
        print(f"    Backtest Score: {hits} Hits / {misses} Misfires | Accuracy: {accuracy:.1f}%")
        
        for s in samples:
            clean_s = "".join([c for c in s if ord(c) < 128])
            print(f"      * {clean_s[:120]}...")

    grand_total = hits_total + misses_total
    grand_accuracy = (hits_total / grand_total * 100) if grand_total > 0 else 0
    print("\n" + "=" * 100)
    print(f" GRAND PREDICTIVE AUDIT ACCURACY SCORE: {grand_accuracy:.2f}% ({hits_total} Total Hits / {grand_total} Analyzed Rules)")
    print("=" * 100)

if __name__ == "__main__":
    asyncio.run(run_vijay_complete_audit())
