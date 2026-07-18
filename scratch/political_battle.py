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

async def run_candidate_analysis():
    corpus = get_corpus()
    
    candidates = [
        {
            "name": "M. K. Stalin (DMK Leader / Tamil Nadu CM)",
            "birth": BirthData(year=1953, month=3, day=1, time="23:36", lat=13.0827, lon=80.2707, focus="general"),
            "events": [
                {"date": "1976-01-31", "type": "IMPRISONMENT", "desc": "Arrested and jailed under MISA during Emergency", "valence": "inauspicious"},
                {"date": "1996-10-12", "type": "POLITICAL_OFFICE", "desc": "Elected as Mayor of Chennai (turning point)", "valence": "auspicious"},
                {"date": "2021-05-07", "type": "POLITICAL_OFFICE", "desc": "Sworn in as Chief Minister of Tamil Nadu", "valence": "auspicious"}
            ]
        },
        {
            "name": "Edappadi K. Palaniswami (AIADMK Leader / Opposition Leader)",
            "birth": BirthData(year=1954, month=5, day=12, time="12:00", lat=11.6643, lon=78.1460, focus="general"),
            "events": [
                {"date": "2017-02-16", "type": "POLITICAL_OFFICE", "desc": "Sworn in as Chief Minister of Tamil Nadu", "valence": "auspicious"},
                {"date": "2021-05-07", "type": "MAJOR_LOSS", "desc": "Lost 2021 assembly election, resigned as CM", "valence": "inauspicious"}
            ]
        },
        {
            "name": "K. Annamalai (BJP Tamil Nadu President)",
            "birth": BirthData(year=1984, month=6, day=4, time="13:17", lat=10.9601, lon=78.0766, focus="general"),
            "events": [
                {"date": "2011-09-01", "type": "CAREER_START", "desc": "Selected for Indian Police Service (IPS) via UPSC", "valence": "auspicious"},
                {"date": "2021-07-08", "type": "POLITICAL_OFFICE", "desc": "Appointed as President of BJP Tamil Nadu", "valence": "auspicious"}
            ]
        },
        {
            "name": "Thalapathy Vijay (TVK Leader / CM Aspirant 2026)",
            "birth": BirthData(year=1974, month=6, day=22, time="12:00", lat=13.0827, lon=80.2707, focus="general"),
            "events": [
                {"date": "1992-12-04", "type": "CAREER_START", "desc": "Lead actor debut in Naalaiya Theerpu", "valence": "auspicious"},
                {"date": "1996-02-15", "type": "CAREER_PEAK", "desc": "Superstar breakthrough Poove Unakkaga", "valence": "auspicious"},
                {"date": "2024-02-02", "type": "POLITICAL_OFFICE", "desc": "Officially launches TVK political party for 2026 elections", "valence": "auspicious"}
            ]
        }
    ]

    print("=" * 80)
    print("        TAMIL NADU CM CANDIDATES: HISTORICAL TIMELINE BACKTEST REPORT")
    print("=" * 80)

    for cand in candidates:
        print(f"\n[+] Analyzing {cand['name']}...")
        chart = await jathagam(cand["birth"])
        
        # Print basic chart info
        lagna_sign = chart.get("lagnam", "Unknown")
        moon_sign = chart.get("janma_rasi", "Unknown")
        moon_star = chart.get("janma_nakshatra", "Unknown")
        print(f"    Lagna: {lagna_sign} | Moon Sign: {moon_sign} | Nakshatra: {moon_star}")
        
        # Extract Moon longitude and construct low-level dict
        moon_lon = chart["all_planet_positions"]["Moon"]["longitude"]
        birth_data = cand["birth"]
        low_level_chart = {
            "positions": {
                "Moon": {
                    "lon": moon_lon,
                    "lon_abs": moon_lon
                }
            },
            "birth": {
                "year": birth_data.year,
                "month": birth_data.month,
                "day": birth_data.day,
                "hour": int(birth_data.time.split(":")[0]),
                "min": int(birth_data.time.split(":")[1])
            }
        }
        
        for ev in cand["events"]:
            dt_obj = datetime.strptime(ev["date"], "%Y-%m-%d")
            active = current_dasha(low_level_chart, dt_obj)
            md = active.get("md", {}).get("md", "Unknown")
            ad = active.get("ad", {}).get("ad", "Unknown")
            
            print(f"\n    >> Event: {ev['type']} ({ev['date']}) - {ev['desc']}")
            print(f"       Active Dasha: {md} Dasa | {ad} Bhukti")
            
            # Query corpus for active Dasha and Bhukti rules
            md_rules = corpus.get_dasha_rules(md, ad, limit=30)
            
            hits = 0
            misses = 0
            matched_samples = []
            
            for r in md_rules:
                val = rule_valence(r.text)
                if val == "neutral":
                    continue
                
                # Check alignment with real-world event valence
                if val == ev["valence"]:
                    hits += 1
                    if len(matched_samples) < 3:
                        matched_samples.append(f"[HIT - {val.upper()}] {r.text} ({r.source_label})")
                else:
                    misses += 1
                    if len(matched_samples) < 3:
                        matched_samples.append(f"[MISFIRE - {val.upper()}] {r.text} ({r.source_label})")
            
            total = hits + misses
            hit_rate = (hits / total * 100) if total > 0 else 0
            print(f"       Rule Corpus Evaluation: {hits} Hits / {misses} Misfires | Hit Rate: {hit_rate:.1f}%")
            
            for sample in matched_samples:
                # Remove non-ascii characters for terminal safety
                clean_sample = "".join([c for c in sample if ord(c) < 128])
                print(f"         - {clean_sample[:120]}...")

if __name__ == "__main__":
    asyncio.run(run_candidate_analysis())
