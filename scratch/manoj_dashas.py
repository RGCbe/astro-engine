import sys, json
from pathlib import Path
_ROOT = Path("F:/astro")
sys.path.insert(0, str(_ROOT / "runtime"))
sys.path.insert(0, str(_ROOT))

from granular_dasha import build_full_timeline
chart = json.load(open(_ROOT / "charts" / "manoj_chart.json", encoding="utf-8"))
tl = build_full_timeline(chart, levels=1)

print("MANOJ DASHA TIMELINE:")
for d in tl:
    if d['start'].year > 1990 and d['start'].year < 2080:
        print(f"{d['md']} Dasha: {d['start'].date()} to {d['end'].date()}")
