#!/usr/bin/env python3
"""Prediction report with CONFIRMED / CONFLICT / NOT PROVIDED vs life facts."""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.prediction_confirm import build_confirmation_report

CHART = ROOT / "charts" / "manoj_chart.json"
FACTS = ROOT / "charts" / "manoj_life_facts.json"
OUT = (
    ROOT
    / "reports"
    / "jun 2026"
    / "2026-06-02"
    / "report"
    / "manoj"
    / "MANOJ_PREDICTIONS_CONFIRMED.md"
)


def main() -> None:
    chart = json.loads(CHART.read_text(encoding="utf-8"))
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    report = build_confirmation_report(chart, facts, when=datetime(2026, 6, 2))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(report, encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
