import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine import known_charts

slug_map = {
    "Mahatma Gandhi": "mahatma_gandhi",
    "Indira Gandhi": "indira_gandhi",
    "Narendra Modi": "narendra_modi",
    "Sachin Tendulkar": "sachin_tendulkar",
    "Mukesh Ambani": "mukesh_ambani",
}

for kc in known_charts.KNOWN_CHARTS:
    if kc.name not in slug_map:
        continue
    slug = slug_map[kc.name]
    stored = json.loads((ROOT / "charts" / f"{slug}_chart.json").read_text(encoding="utf-8"))
    b = stored["birth"]
    bd = kc.birthdata
    diffs = []
    chart_date = f"{b['year']}-{b['month']:02d}-{b['day']:02d}"
    if bd["date"] != chart_date:
        diffs.append(f"date {chart_date} vs {bd['date']}")
    chart_time = f"{b['hour']:02d}:{b['min']:02d}"
    if bd["time"] != chart_time:
        diffs.append(f"time {chart_time} vs {bd['time']}")
    if abs(bd["tz"] - b["tz"]) > 0.01:
        diffs.append(f"tz {b['tz']} vs {bd['tz']}")
    print(kc.name, "MISMATCH" if diffs else "date/tz OK", diffs)
