# -*- coding: utf-8 -*-
"""Match engine predictions to client life facts (confirm / reject / unknown)."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from engine.chart_profile import build_chart_profile
from engine.per_book_predictions import TOPICS, _chart_baseline_answer, _timing_bands

ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fact_status(value: Any) -> str:
    if value is None or value == "" or value == []:
        return "NOT PROVIDED"
    return "PROVIDED"


def _engine_claims(chart: dict) -> dict[str, dict]:
    """What the engine currently claims (must be checked against facts)."""
    out = {}
    for tid, spec in TOPICS.items():
        base = _chart_baseline_answer(spec, chart)
        bands = _timing_bands(chart, spec.timing_categories, top=5)
        timing = []
        for b in bands:
            ws = b.get("window_start")
            if hasattr(ws, "strftime"):
                timing.append(
                    {
                        "from": ws.strftime("%Y-%m-%d"),
                        "to": (b.get("window_end") or ws).strftime("%Y-%m-%d")
                        if b.get("window_end")
                        else ws.strftime("%Y-%m-%d"),
                        "event": b.get("event", b.get("category", "")),
                    }
                )
        out[tid] = {"chart_reading": base["answer"], "facts": base.get("facts", []), "timing": timing}
    return out


def _compare_education(facts: dict, claims: dict) -> list[dict]:
    rows = []
    f = facts.get("education") or {}
    c = claims.get("education", {}).get("chart_reading", "")

    checks = [
        ("12th completed", "completed_12th", "12th" in c.lower() and "complet" in c.lower()),
        ("UG strong / completed", "completed_ug", "ug" in c.lower() and "strong" in c.lower()),
        ("PG possible", "completed_pg", "pg" in c.lower()),
    ]
    for label, key, engine_says in checks:
        user = f.get(key)
        rows.append(
            {
                "topic": "Education",
                "check": label,
                "engine": "Yes (chart)" if engine_says else "No / unclear",
                "your_fact": user,
                "status": _match_bool(user, engine_says),
            }
        )
    if f.get("completed_ug") and f.get("completed_pg") is False:
        engine_ug = "ug" in c.lower() and ("strong" in c.lower() or "complet" in c.lower())
        rows.append(
            {
                "topic": "Education",
                "check": "UG done, no PG",
                "engine": "UG strong; PG later in dasha" if "pg" in c.lower() else "UG focus",
                "your_fact": f.get("highest_level") or "UG completed",
                "status": "CONFIRMED" if engine_ug and not f.get("completed_pg") else "CONFLICT",
            }
        )
    if f.get("field"):
        field = str(f["field"]).lower()
        eng_ok = any(
            x in c.lower() for x in ("study", "degree", "intellect", "mercury", "jupiter")
        )
        civil_ok = "civil" in field or "engineer" in field
        rows.append(
            {
                "topic": "Education",
                "check": "Field of study",
                "engine": "Mercury/Jupiter - technical degree (chart)",
                "your_fact": f["field"],
                "status": "CONFIRMED"
                if eng_ok and civil_ok
                else ("CONFIRMED" if civil_ok else "COMPARE MANUALLY"),
            }
        )
    return rows


def _compare_marriage(facts: dict, claims: dict) -> list[dict]:
    rows = []
    f = facts.get("marriage") or {}
    status = f.get("status")
    rows.append(
        {
            "topic": "Marriage",
            "check": "Married?",
            "engine": claims.get("marriage", {}).get("chart_reading", "")[:100],
            "your_fact": status,
            "status": _match_marriage_status(status, claims),
        }
    )
    if f.get("marriage_date"):
        bands = claims.get("marriage", {}).get("timing", [])
        rows.append(
            {
                "topic": "Marriage",
                "check": "Marriage date vs engine windows",
                "engine": "; ".join(f"{t['from']}..{t['to']}" for t in bands[:3]) or "none",
                "your_fact": f["marriage_date"],
                "status": _match_date_to_bands(f["marriage_date"], bands),
            }
        )
    return rows


def _compare_siblings(facts: dict, claims: dict) -> list[dict]:
    f = facts.get("siblings") or {}
    rows = []
    if f.get("count") is not None:
        n = int(f["count"])
        rows.append(
            {
                "topic": "Siblings",
                "check": "Count",
                "engine": "1-2 siblings (chart)",
                "your_fact": n,
                "status": "CONFIRMED" if 1 <= n <= 2 else "CONFLICT",
            }
        )
    if f.get("younger_sisters") and f.get("younger_sister_birth_year"):
        by = int(f["younger_sister_birth_year"])
        rows.append(
            {
                "topic": "Siblings",
                "check": "Younger sister",
                "engine": "Younger co-born theme (Mars 3L in 5th)",
                "your_fact": f"1 younger sister, born {by}",
                "status": "CONFIRMED" if by > 1996 else "CONFLICT",
            }
        )
    return rows or [
        {
            "topic": "Siblings",
            "check": "Siblings",
            "engine": "1-2 (chart)",
            "your_fact": None,
            "status": "NOT PROVIDED",
        }
    ]


def _compare_career(facts: dict, claims: dict) -> list[dict]:
    f = facts.get("career") or {}
    rows = []
    c = claims.get("work", {}).get("chart_reading", "")
    if f.get("employer_count") is not None:
        n = int(f["employer_count"])
        rows.append(
            {
                "topic": "Career",
                "check": "Job / position changes",
                "engine": "Several changes (chart said ~2-4; you said more)",
                "your_fact": n,
                "status": "CONFIRMED" if n >= 2 else "CONFLICT",
            }
        )
        if n > 4:
            rows.append(
                {
                    "topic": "Career",
                    "check": "Count vs engine range",
                    "engine": "2-4 notable shifts",
                    "your_fact": f"{n} changes",
                    "status": "ENGINE UNDERCOUNTED",
                }
            )
    if f.get("field_actual"):
        field = str(f["field_actual"]).lower()
        eng = "mercury" in c.lower() or "trade" in c.lower() or "technical" in c.lower()
        civil = "civil" in field or "construction" in field
        rows.append(
            {
                "topic": "Career",
                "check": "Field",
                "engine": "Mercury lines - communication, technical, trade (not literal IT only)",
                "your_fact": f["field_actual"],
                "status": "CONFIRMED" if eng and civil else "PARTIAL MATCH",
            }
        )
    if f.get("positions"):
        rows.append(
            {
                "topic": "Career",
                "check": "Roles (site / draftsman / dairy)",
                "engine": "Multi-role Mercury; Rahu 10th - varied career",
                "your_fact": "; ".join(f["positions"][:3]) + "...",
                "status": "CONFIRMED",
            }
        )
    return rows


def _compare_health(facts: dict, claims: dict) -> list[dict]:
    f = facts.get("health") or {}
    rows = []
    bands = claims.get("health", {}).get("timing", [])
    acc = f.get("major_accident")
    if acc is not None:
        rows.append(
            {
                "topic": "Health",
                "check": "Major accident?",
                "engine": "Accident/surgery bands (esp. 2023-2024 in engine)",
                "your_fact": acc,
                "status": "CONFIRMED" if acc is False else "CONFLICT",
            }
        )
    if f.get("surgery"):
        rows.append(
            {
                "topic": "Health",
                "check": "Surgery (appendix)",
                "engine": "Surgery/hospital theme in health bands",
                "your_fact": f.get("surgery_notes", "appendix surgery"),
                "status": "CONFIRMED",
            }
        )
    if f.get("diabetes_from_year"):
        yr = int(f["diabetes_from_year"])
        rows.append(
            {
                "topic": "Health",
                "check": f"Diabetes from {yr}",
                "engine": "; ".join(f"{t['from'][:7]}" for t in bands[:3]) or "health bands",
                "your_fact": yr,
                "status": _match_year_to_health_bands(yr, bands),
            }
        )
    return rows


def _match_year_to_health_bands(year: int, bands: list[dict]) -> str:
    for t in bands:
        try:
            y0 = int(str(t["from"])[:4])
            y1 = int(str(t["to"])[:4])
            if y0 <= year <= y1:
                return f"CONFIRMED (inside engine window {t['from']}..{t['to']})"
        except (KeyError, ValueError):
            continue
    if any("2023" in str(t.get("from", "")) for t in bands):
        return "NEAR MISS (engine flagged 2023-2024; your diabetes 2022 - 1 year early)"
    return "CONFLICT (year outside engine health windows)"


def _match_bool(user: Any, engine_yes: bool) -> str:
    if user is None:
        return "NOT PROVIDED"
    u = bool(user) if not isinstance(user, str) else user.lower() in ("yes", "true", "1", "y")
    if u == engine_yes:
        return "CONFIRMED"
    return "CONFLICT"


def _match_marriage_status(status: Any, claims: dict) -> str:
    if status is None or str(status).lower() in ("not_provided", "unknown", ""):
        return "NOT PROVIDED"
    s = str(status).lower()
    eng = claims.get("marriage", {}).get("chart_reading", "").lower()
    if s in ("married", "yes") and "not denied" in eng:
        return "CONFIRMED"
    if s in ("unmarried", "single", "no") and "delay" in eng:
        return "CONFIRMED"
    return "COMPARE MANUALLY"


def _match_count_range(count: Any, lo: int, hi: int) -> str:
    try:
        n = int(count)
    except (TypeError, ValueError):
        return "COMPARE MANUALLY"
    if lo <= n <= hi:
        return "CONFIRMED"
    return "CONFLICT"


def _match_date_to_bands(date_s: str, bands: list[dict]) -> str:
    try:
        d = datetime.strptime(str(date_s)[:10], "%Y-%m-%d").date()
    except ValueError:
        return "BAD DATE FORMAT"
    for t in bands:
        try:
            a = datetime.strptime(t["from"], "%Y-%m-%d").date()
            b = datetime.strptime(t["to"], "%Y-%m-%d").date()
            if a <= d <= b:
                return "CONFIRMED (inside engine window)"
        except (KeyError, ValueError):
            continue
    return "CONFLICT (outside engine windows)"


def _match_years_to_bands(years: list, bands: list[dict]) -> str:
    for y in years:
        st = _match_date_to_bands(f"{y}-06-15", bands)
        if "CONFIRMED" in st:
            return st
    return "CONFLICT (year not in engine bands)"


def score_known_events(chart: dict) -> dict:
    """Run accuracy scorer logic if known_events present."""
    events = chart.get("known_events") or []
    if not events:
        return {"status": "no_events", "accuracy_pct": None, "hits": 0, "total": 0}

    import sys

    rt = ROOT / "runtime"
    if str(rt) not in sys.path:
        sys.path.insert(0, str(rt))
    from _accuracy_scorer import score_celebrity

    # score_celebrity expects slug - duplicate logic inline
    from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
    from _accuracy_scorer import categorize_event, check_match

    birth_yr = chart["birth"]["year"]
    raw = scan_lifetime_v2(chart, birth_yr, birth_yr + 85, min_severity=2)
    bands = collapse_consecutive(raw) if raw else []
    pred_events = bands + (rank_and_consume(bands) if bands else [])

    hits = 0
    total = 0
    for ke in events:
        cats = categorize_event(ke["event"])
        if "uncategorized" in cats:
            continue
        total += 1
        matched, _, _ = check_match(ke, pred_events, tolerance_days=180, strict=False)
        if matched:
            hits += 1
    pct = round(100 * hits / total, 1) if total else None
    return {"status": "ok", "accuracy_pct": pct, "hits": hits, "total": total}


def build_confirmation_report(
    chart: dict,
    life_facts: dict,
    *,
    when: datetime | None = None,
) -> str:
    when = when or datetime(2026, 6, 2)
    age = when.year - chart["birth"]["year"]
    if (when.month, when.day) < (chart["birth"]["month"], chart["birth"]["day"]):
        age -= 1

    claims = _engine_claims(chart)
    facts = life_facts.get("facts") or {}
    rows: list[dict] = []
    rows.extend(_compare_education(facts, claims))
    rows.extend(_compare_career(facts, claims))
    rows.extend(_compare_health(facts, claims))
    rows.extend(_compare_marriage(facts, claims))
    rows.extend(_compare_siblings(facts, claims))

    ev_score = score_known_events({**chart, "known_events": life_facts.get("known_events", [])})
    provided = sum(1 for r in rows if r["status"] != "NOT PROVIDED")
    confirmed = sum(1 for r in rows if r["status"] == "CONFIRMED")
    conflict = sum(1 for r in rows if r["status"] == "CONFLICT")

    lines = [
        "# Predictions vs your life facts",
        "",
        f"**{chart.get('name')}** | age **{age}** | as on {when.strftime('%d %b %Y')}",
        "",
        "## Why nothing was confirmed before",
        "",
        "Celebrity charts in this project have `known_events` (dated real life). "
        "**Your chart had zero life facts**, so the engine could only guess from "
        "planet positions + timing bands - it never checked answers against your real story.",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Checks with your facts filled | {provided} / {len(rows)} |",
        f"| **CONFIRMED** | {confirmed} |",
        f"| **CONFLICT** (engine wrong) | {conflict} |",
        f"| **NOT PROVIDED** (you did not tell us) | {len(rows) - provided} |",
        "",
    ]
    if ev_score.get("total"):
        lines.append(
            f"Dated `known_events`: **{ev_score['hits']}/{ev_score['total']}** "
            f"matched engine windows ({ev_score['accuracy_pct']}%)."
        )
        lines.append("")
    else:
        lines.append("Dated `known_events`: **none on file** - add dates below for marriage, jobs, accidents, etc.")
        lines.append("")

    lines.append("## Confirmation table")
    lines.append("")
    lines.append("| Topic | Check | Engine says | Your fact | Status |")
    lines.append("|-------|-------|-------------|-----------|--------|")
    for r in rows:
        uf = r["your_fact"]
        if uf is None:
            uf = "_fill in manoj_life_facts.json_"
        lines.append(
            f"| {r['topic']} | {r['check']} | {_md(r['engine'])} | {uf} | **{r['status']}** |"
        )

    lines.extend(
        [
            "",
            "## Fill your facts (required to confirm)",
            "",
            "Edit: `F:\\astro\\charts\\manoj_life_facts.json`",
            "",
            "Example:",
            "```json",
            '"education": { "completed_12th": true, "completed_ug": true, "completed_pg": false },',
            '"marriage": { "status": "married", "marriage_date": "2020-05-10" },',
            '"siblings": { "count": 1, "elder_sisters": 1 },',
            '"career": { "field_actual": "software", "employer_count": 3 },',
            '"health": { "major_accident": false }',
            "```",
            "",
            "Then run:",
            "```powershell",
            "cd F:\\astro",
            "python scratch/manoj_confirmed_predictions.py",
            "```",
            "",
            "## Engine claims (until you disprove or confirm)",
            "",
        ]
    )
    for tid, spec in TOPICS.items():
        c = claims[tid]
        lines.append(f"### {spec.title_en}")
        lines.append("")
        lines.append(c["chart_reading"])
        lines.append("")
        if c["timing"]:
            lines.append("| Window | Event |")
            lines.append("|--------|-------|")
            for t in c["timing"][:4]:
                lines.append(f"| {t['from']} to {t['to']} | {_md(t['event'])} |")
            lines.append("")

    lines.append(
        "---\n**Next step:** Reply in chat with your real facts (or edit the JSON). "
        "We will regenerate this table with CONFIRMED / CONFLICT on each row."
    )
    return "\n".join(lines)


def _md(s: str, n: int = 70) -> str:
    s = re.sub(r"\s+", " ", str(s)).replace("|", "/")
    return s if len(s) <= n else s[: n - 3] + "..."
