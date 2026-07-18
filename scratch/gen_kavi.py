import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from engine.chart_builder import build_orchestrator_chart_dict

kavi_chart = build_orchestrator_chart_dict(
    year=2001,
    month=10,
    day=19,
    time_str="05:28",
    lat=11.0168,
    lon=76.9558,
    tz_hours=5.5
)

kavi_chart["name"] = "Kavipriya"
kavi_chart["birth"]["place"] = "Coimbatore"
kavi_chart["known_events"] = []

out_path = os.path.join(os.path.dirname(__file__), '..', 'charts', 'kavipriya_chart.json')
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(kavi_chart, f, indent=4, ensure_ascii=False)
    
print("Chart generated successfully at:", out_path)
