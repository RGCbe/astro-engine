"""
Accuracy feedback loop.

Records per-prediction user feedback (right/wrong/maybe) keyed by chart
+ prediction-id. Uses the accumulated feedback to learn weights for
each prediction module (Bhrigu / KP / classical / empirical / structural).

Storage: a single JSON file at /opt/astro/engine/data/feedback.json
        {
          "feedback": [
            {chart_key, prediction_id, module, label, value, ts}, ...
          ],
          "weights": {module: weight, ...}
        }

API:
    record_feedback(chart_key, prediction_id, module, label, value)
    get_module_weights() -> dict[module, weight]
    apply_module_weight(module, score) -> calibrated_score
    summary() -> stats
"""
from __future__ import annotations

import datetime as dt
import json
import os
from pathlib import Path

DATA_FILE = Path("/opt/astro/engine/data/feedback.json")
DATA_FILE.parent.mkdir(parents=True, exist_ok=True)


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.load(open(DATA_FILE))
        except Exception:
            pass
    return {
        "feedback": [],
        "weights": {
            "bhrigu":     1.0,
            "kp":         1.0,
            "classical":  1.0,
            "empirical":  1.0,
            "structural": 1.0,
            "education":  1.0,
            "accident":   1.0,
            "marriage":   1.0,
            "career":     1.0,
        },
    }


def _save(d: dict) -> None:
    json.dump(d, open(DATA_FILE, "w"), indent=2, default=str)


def _chart_key(chart) -> str:
    """Canonical chart identifier — the engine uses birth datetime."""
    return chart.birth_dt.isoformat()[:19]


def record_feedback(chart, prediction_id: str, module: str,
                    label: str, value: bool | str) -> None:
    """Record one piece of feedback.
        chart: the Chart object
        prediction_id: e.g. 'career.industry_primary' or 'marriage.window'
        module: which module owns this prediction
        label: human-readable description
        value: True (right), False (wrong), 'maybe', 'partial'
    """
    d = _load()
    d["feedback"].append({
        "chart": _chart_key(chart),
        "prediction_id": prediction_id,
        "module": module,
        "label": label,
        "value": value,
        "ts": dt.datetime.utcnow().isoformat(),
    })
    _update_weights(d)
    _save(d)


def _update_weights(d: dict) -> None:
    """Recompute per-module weights from feedback.

    Weight = clip(0.3, 1 + (right - wrong) / max(total, 5), 2.0)
    """
    counts: dict[str, dict] = {}
    for f in d["feedback"]:
        m = f["module"]
        counts.setdefault(m, {"right": 0, "wrong": 0, "maybe": 0})
        v = f["value"]
        if v is True or v == "right":
            counts[m]["right"] += 1
        elif v is False or v == "wrong":
            counts[m]["wrong"] += 1
        else:
            counts[m]["maybe"] += 1
    for m, c in counts.items():
        total = c["right"] + c["wrong"] + c["maybe"]
        diff = c["right"] - c["wrong"]
        w = 1.0 + diff / max(total, 5)
        d["weights"][m] = max(0.3, min(2.0, w))


def get_module_weights() -> dict[str, float]:
    return _load()["weights"]


def apply_module_weight(module: str, score: float) -> float:
    """Calibrate a module's score by its accumulated trustworthiness."""
    w = get_module_weights().get(module, 1.0)
    return score * w


def summary() -> dict:
    d = _load()
    by_module: dict[str, dict] = {}
    for f in d["feedback"]:
        m = f["module"]
        by_module.setdefault(m, {"right": 0, "wrong": 0, "maybe": 0})
        v = f["value"]
        if v is True or v == "right":
            by_module[m]["right"] += 1
        elif v is False or v == "wrong":
            by_module[m]["wrong"] += 1
        else:
            by_module[m]["maybe"] += 1
    return {
        "total_feedback": len(d["feedback"]),
        "by_module": by_module,
        "current_weights": d["weights"],
    }
