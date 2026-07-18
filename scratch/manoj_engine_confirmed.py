#!/usr/bin/env python3
"""Engine-only confirmed predictions (no manoj_life_facts.json)."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.engine_topic_confirm import build_engine_confirmed_report

OUT = (
    ROOT
    / "reports"
    / "jun 2026"
    / "2026-06-02"
    / "report"
    / "manoj"
    / "MANOJ_ENGINE_CONFIRMED.md"
)


def main() -> None:
    chart = json.loads((ROOT / "charts" / "manoj_chart.json").read_text(encoding="utf-8"))
    report = build_engine_confirmed_report(chart, when=datetime(2026, 6, 2))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(report, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
