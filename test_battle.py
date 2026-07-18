import asyncio
import json
import os
import sys

# Ensure current dir is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import jathagam, BirthData
from engine.comparative_test import execute_corpus_battle_comparison

async def test():
    print("Initializing chart analysis...")
    data = BirthData(
        year=1996,
        month=5,
        day=25,
        time="20:25",
        lat=11.01,
        lon=76.57,
        focus="general"
    )
    
    # Run the full Jathagam generator to get the rich chart object
    full_data = await jathagam(data)
    
    print("Running Council of Masters comparison...")
    battle_report = execute_corpus_battle_comparison(full_data)
    
    keys = list(battle_report.keys())
    print(f"\nKeys in Battle Report ({len(keys)} items):")
    for k in keys:
        print(" -", k)
        
    print("\n--- Snippet of Dasha Rules found ---")
    dasha_keys = [k for k in keys if "Dasha" in k or "Antardasha" in k]
    for k in dasha_keys[:3]:
        print(f"\n{k}:")
        print(json.dumps(battle_report[k], indent=2))

if __name__ == "__main__":
    asyncio.run(test())
