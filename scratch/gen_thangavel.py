import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.chart_builder import build_orchestrator_chart_dict

thangavel_chart = build_orchestrator_chart_dict(
    year=1963,
    month=7,
    day=29,
    time_str="05:10",
    lat=11.25, # Andakkapalayam / Govilpalayam area
    lon=77.12,
    tz_hours=5.5
)

thangavel_chart["name"] = "S. Thangavel"
thangavel_chart["birth"]["place"] = "Andakkapalayam"
thangavel_chart["known_events"] = []

out_path = os.path.join(os.path.dirname(__file__), '..', 'charts', 'thangavel_chart.json')
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(thangavel_chart, f, indent=4, ensure_ascii=False)
    
print("Chart generated successfully at:", out_path)
