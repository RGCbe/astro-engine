import json
from pathlib import Path
from datetime import datetime
import sys

_ROOT = Path("f:/Atro")
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "runtime"))

from granular_dasha import build_full_timeline

chart = json.load(open(_ROOT / "charts" / "joseph_vijay_chart.json", encoding="utf-8"))
EVENTS = chart["known_events"]

tl = build_full_timeline(chart, levels=3)

def parse_date(s):
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try: return datetime.strptime(s, fmt)
        except: continue
    return None

print(f"{'Date':<11} | {'Category':<12} | {'MD':<8} | {'AD':<8} | {'PD':<8} | {'Event'}")
print("-" * 100)

for ev in EVENTS:
    target_date = parse_date(ev["date"])
    md = next((e for e in tl if e.get("level") == 1 and e["start"] <= target_date <= e["end"]), None)
    ad = next((e for e in tl if e.get("level") == 2 and e["start"] <= target_date <= e["end"]), None)
    pd = next((e for e in tl if e.get("level") == 3 and e["start"] <= target_date <= e["end"]), None)
    
    md_l = md["md"] if md else "?"
    ad_l = ad["ad"] if ad else "?"
    pd_l = pd["pd"] if pd else "?"
    
    clean_event = ev["event"].encode("ascii", "ignore").decode("ascii")
    print(f"{ev['date']:<11} | {ev['atro_category']:<12} | {md_l:<8} | {ad_l:<8} | {pd_l:<8} | {clean_event[:50]}")
