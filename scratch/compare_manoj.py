import sys
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Setup paths
_ROOT = Path("F:/astro")
sys.path.insert(0, str(_ROOT / "runtime"))
sys.path.insert(0, str(_ROOT))

from runtime.event_predictor_v2 import scan_lifetime_v2, collapse_consecutive as coll_old, rank_and_consume
from runtime.category_engine import category_engine_instance

def main():
    chart_path = _ROOT / "charts" / "manoj_chart.json"
    with open(chart_path, "r", encoding="utf-8") as f:
        chart = json.load(f)

    print("Running OLD engine...")
    raw_old = scan_lifetime_v2(chart, 2026, 2030, min_severity=2)
    bands_old = coll_old(raw_old) if raw_old else []
    ranked_old = rank_and_consume(bands_old) if bands_old else []
    pred_old = bands_old + ranked_old

    print("Running NEW engine...")
    raw_new = category_engine_instance.scan_lifetime(chart, 2026, 2030, min_severity=2)
    pred_new = category_engine_instance.collapse_consecutive(raw_new) if raw_new else []

    # Group by Year-Month
    # dict of "YYYY-MM" -> {"old": [], "new": []}
    timeline = defaultdict(lambda: {"old": set(), "new": set()})

    for ev in pred_old:
        date_obj = ev.get("window_start") or ev.get("peak_date") or ev.get("date")
        if not date_obj: continue
        if isinstance(date_obj, datetime):
            dt = date_obj
        else:
            dt = datetime.strptime(str(date_obj)[:10], "%Y-%m-%d")
        ym = dt.strftime("%Y-%m")
        cat = ev.get("category", "")
        if cat:
            timeline[ym]["old"].add(cat)

    for ev in pred_new:
        date_obj = ev.get("window_start") or ev.get("peak_date")
        if not date_obj: continue
        if isinstance(date_obj, datetime):
            dt = date_obj
        else:
            dt = datetime.strptime(str(date_obj)[:10], "%Y-%m-%d")
        ym = dt.strftime("%Y-%m")
        cat = ev.get("category", "")
        if cat:
            timeline[ym]["new"].add(cat)

    print("\n--- COMPARISON ---")
    print(f"{'Sl No':<6} | {'Index (Month)':<15} | {'OLD Engine':<40} | {'NEW Engine'}")
    print("-" * 100)
    
    sl = 1
    for ym in sorted(timeline.keys()):
        old_str = ", ".join(sorted(timeline[ym]["old"])) or "-"
        new_str = ", ".join(sorted(timeline[ym]["new"])) or "-"
        
        # Break long strings to avoid messing up console, though simple print is fine
        print(f"{sl:<6} | {ym:<15} | {old_str:<40} | {new_str}")
        sl += 1

if __name__ == "__main__":
    main()
