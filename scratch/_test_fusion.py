#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "runtime"))

from engine.chart_profile import build_chart_profile
from engine.multi_source_synthesis import synthesize_life_topics

chart = json.loads((ROOT / "charts" / "manoj_chart.json").read_text(encoding="utf-8"))
chart["name"] = "Manoj"
prof = build_chart_profile(chart)
print("PROFILE:", prof["executive_summary_en"][:200], "...")
syn = synthesize_life_topics(chart)
for k, v in syn["topics"].items():
    print(k, v["confidence_pct"], v["status"], v["disagreement"])
print("fusion OK")
