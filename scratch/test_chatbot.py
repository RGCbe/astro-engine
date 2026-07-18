import sys
from pathlib import Path
sys.path.insert(0, str(Path(r"f:\astro")))
import json
from scripts.chat_bot import parse_intent, parse_year
from runtime.category_engine import category_engine_instance

chart_path = r"f:\astro\charts\joseph_vijay_chart.json"
with open(chart_path, "r", encoding="utf-8") as f:
    chart = json.load(f)

# Mock a user query
user_input = "Will I get married in 1999?"
print(f"User: {user_input}")

intent = parse_intent(user_input)
year = parse_year(user_input, 1999)
print(f"Parsed Intent: {intent}, Year: {year}")

events = category_engine_instance.scan_year(chart, year, min_probability=0.2)
matched = [ev for ev in events.values() if intent in ev["category"].lower() or intent in ev["event"].lower()]

print(f"Matched Events: {len(matched)}")
for ev in matched:
    print(f"  Event: {ev['event']}")
    print(f"  Confidence: {ev['probability']*100:.0f}%")
