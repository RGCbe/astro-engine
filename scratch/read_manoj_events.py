import json
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runtime"))

sys.stdout.reconfigure(encoding="utf-8")

from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive

with open(os.path.join(ROOT, "charts", "manoj_chart.json"), "r", encoding="utf-8") as f:
    chart_data = json.load(f)

raw_events = scan_lifetime_v2(chart_data, 1996, 2036, min_severity=2)
bands = collapse_consecutive(raw_events)

print("=== MANOJ EDUCATION EVENTS IN LIFETIME ===")
found_any = False
for b in bands:
    if b["category"] == "education" or "graduat" in b["event"].lower() or "graduat" in b["why"] or "graduat" in b["source"].lower():
        found_any = True
        start_dt = b.get("window_start")
        end_dt = b.get("window_end")
        start_str = start_dt.strftime("%Y-%m-%d") if hasattr(start_dt, "strftime") else str(start_dt)
        end_str = end_dt.strftime("%Y-%m-%d") if hasattr(end_dt, "strftime") else str(end_dt)
        
        print(f"- [{start_str} to {end_str}] {b['event']}")
        print(f"  Category: {b['category']} | Severity: {b['severity']}")
        print(f"  Why: {b['why']}")
        print(f"  Source: {b['source']}")
        print()

if not found_any:
    print("No education events predicted.")
