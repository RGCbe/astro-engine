import sys
from pathlib import Path
sys.path.insert(0, str(Path(r"f:\astro")))
sys.path.insert(0, str(Path(r"f:\astro\engine")))
import json

from runtime.category_engine import category_engine_instance

def run_test():
    chart_path = r"f:\astro\charts\joseph_vijay_chart.json"
    with open(chart_path, "r", encoding="utf-8") as f:
        chart = json.load(f)
        
    print(f"Loaded chart for {chart['name']}...")
    
    # Let's scan a specific year, e.g., 2004 (Ghilli release year for Vijay)
    year = 2004
    print(f"\nScanning Year {year} using V2 Probabilistic Meta-Reasoner...")
    
    events = category_engine_instance.scan_year(chart, year, min_probability=0.2) # lower threshold to see what fires
    
    if not events:
        print("No events fired.")
        return
        
    for k, v in events.items():
        print(f"\n[+] {v['event']}")
        print(f"    Probability: {v['probability']:.2f} ({v['confidence_band']})")
        print(f"    Date Window: {v['window_start']} to {v['window_end']}")
        if v.get('contradictions'):
            print("    Contradictions Flagged: YES")
        print("    Explainability Trace:")
        for why in v['why']:
            print(f"      - {why}")
            
if __name__ == "__main__":
    run_test()
