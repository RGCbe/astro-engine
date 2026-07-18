"""
Event feedback — let the engine learn from confirmed life events.

When the user says "I joined dad's shop in 2021" or "I got promoted in 2019",
this module:
  1) Looks up which Antardasha covered that date.
  2) Checks whether the event-trigger predicted by `dasa_narrative` matched.
  3) Logs the (event_label, actual_date, predicted_window, match_score, rules)
     tuple into engine/data/event_feedback.json.
  4) Adjusts confidence weights for the rule-types involved, so future
     predictions on other charts get more accurate.

Storage: /opt/astro/engine/data/event_feedback.json
Schema:
   { "events": [
        { chart_key, event, actual_date, predicted_window:[md,ad,start,end],
          predicted_triggers, match: bool, score: float, ts }
     ],
     "weights": { trigger_event_type: float } }
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from engine.dasa_narrative import find_for_date

DATA = Path("/opt/astro/engine/data/event_feedback.json")
DATA.parent.mkdir(parents=True, exist_ok=True)

# Map natural-language event labels to the trigger-event tag dasa_narrative emits.
EVENT_TAG: dict[str, str] = {
    "promotion": "career_upgrade",
    "raise": "career_upgrade",
    "salary jump": "career_upgrade",
    "job change": "career_change",
    "new job": "career_change",
    "joined company": "career_change",
    "left job": "career_change",
    "marriage": "marriage_window",
    "wedding": "marriage_window",
    "engagement": "marriage_window",
    "first child": "children_window",
    "child born": "children_window",
    "baby": "children_window",
    "foreign": "foreign_window",
    "abroad": "foreign_window",
    "relocation": "foreign_window",
    "bought house": "property_window",
    "bought car": "property_window",
    "bought property": "property_window",
    "family business": "family_business_window",
    "father business": "family_business_window",
    "father shop": "family_business_window",
    "joined father": "family_business_window",
    "joined dad": "family_business_window",
    "spiritual": "spiritual_or_loss",
    "loss": "spiritual_or_loss",
}


@dataclass
class EventLog:
    chart_key: str
    event: str
    actual_date: str
    predicted_md: str
    predicted_ad: str
    predicted_start: str
    predicted_end: str
    predicted_triggers: str
    match: bool
    score: float
    ts: str


def _chart_key(chart) -> str:
    s = f"{chart.name}|{chart.birth_dt.isoformat()}|{chart.lat}|{chart.lon}"
    return hashlib.sha1(s.encode()).hexdigest()[:12]


def _load() -> dict:
    if DATA.exists():
        try:
            return json.loads(DATA.read_text())
        except Exception:
            pass
    return {"events": [], "weights": {}}


def _save(blob: dict) -> None:
    DATA.write_text(json.dumps(blob, indent=2))


def _event_to_tag(event: str) -> str | None:
    e = event.lower()
    for kw, tag in EVENT_TAG.items():
        if kw in e:
            return tag
    return None


def _to_date(x) -> dt.date:
    if isinstance(x, dt.date): return x
    return dt.date.fromisoformat(str(x)[:10])


def confirm_event(chart, event: str, actual_date) -> EventLog:
    """Confirm an event happened. Logs match/mismatch + adjusts weights."""
    when = _to_date(actual_date)
    d = find_for_date(chart, when)
    if d is None:
        raise ValueError(f"No dasha covers {when} (probably out of timeline range)")
    tag = _event_to_tag(event) or ""
    triggers = d.triggers_event or ""
    match = bool(tag and tag in triggers)
    # Score: 1.0 perfect match, 0.5 same life-area family, 0.0 miss
    score = 1.0 if match else (0.5 if tag and any(t.split("_")[0] in triggers for t in tag.split()) else 0.0)

    log = EventLog(
        chart_key=_chart_key(chart),
        event=event,
        actual_date=when.isoformat(),
        predicted_md=d.md_lord,
        predicted_ad=d.ad_lord,
        predicted_start=d.period_start.isoformat(),
        predicted_end=d.period_end.isoformat(),
        predicted_triggers=triggers,
        match=match,
        score=score,
        ts=dt.datetime.now(dt.UTC).isoformat(),
    )
    blob = _load()
    blob["events"].append(asdict(log))
    # Update weight for the trigger-tag — every confirmation moves weight ±0.05
    if tag:
        w = blob["weights"].get(tag, 1.0)
        if match:    w = min(2.0, w + 0.05)
        else:        w = max(0.5, w - 0.03)
        blob["weights"][tag] = round(w, 3)
    _save(blob)
    return log


def get_weights() -> dict[str, float]:
    return _load().get("weights", {})


def apply_weight(trigger_tag: str, base_confidence: str) -> str:
    """Bump or lower a confidence label based on accumulated feedback."""
    w = get_weights().get(trigger_tag, 1.0)
    order = ["LOW", "MEDIUM", "HIGH"]
    idx = order.index(base_confidence) if base_confidence in order else 1
    if w >= 1.3:    idx = min(2, idx + 1)
    elif w <= 0.7:  idx = max(0, idx - 1)
    return order[idx]


def history_for(chart) -> list[dict]:
    key = _chart_key(chart)
    return [e for e in _load().get("events", []) if e["chart_key"] == key]


def summary() -> dict:
    blob = _load()
    events = blob["events"]
    by_tag: dict[str, dict] = {}
    for e in events:
        tag = _event_to_tag(e["event"]) or "other"
        s = by_tag.setdefault(tag, {"count": 0, "matches": 0})
        s["count"] += 1
        if e["match"]:
            s["matches"] += 1
    return {"total_events": len(events),
            "weights": blob["weights"],
            "by_tag": by_tag}
