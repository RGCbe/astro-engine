import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from runtime.granular_dasha import build_full_timeline

chart = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'charts', 'thangavel_chart.json'), encoding="utf-8"))
timeline = build_full_timeline(chart, levels=2)

current_year = 2026
current_month = 6

print("--- THANGAVEL DASHA TIMELINE ---")
for md in timeline:
    if md["end"].year > current_year - 5:
        print(f"MD: {md['planet']} ({md['start'].strftime('%Y-%m-%d')} to {md['end'].strftime('%Y-%m-%d')})")
        for ad in md["sub"]:
            ad_start_yr = ad["start"].year
            ad_end_yr = ad["end"].year
            if ad_start_yr <= current_year + 2 and ad_end_yr >= current_year - 1:
                print(f"  -> AD: {ad['planet']} ({ad['start'].strftime('%Y-%m-%d')} to {ad['end'].strftime('%Y-%m-%d')})")
