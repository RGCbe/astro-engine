# -*- coding: utf-8 -*-
"""
Confirm predictions using ENGINE layers only (no client life-facts file).

Layers:
  1. Mechanical chart (lords, karaka houses) - always true if computed
  2. Active dasha touches topic houses/karakas
  3. event_predictor_v2 timing band (severity threshold)
  4. Strict placement-matched corpus rules (count)
  5. Book-battle consensus % for topic houses

Verdict per topic:
  CONFIRMED - 3+ layers agree, no strong contradiction
  MIXED - 2 layers or corpus disagreement
  NOT CONFIRMED - insufficient engine agreement
"""
from __future__ import annotations

import datetime as dt
from typing import Any

from engine.chart_profile import build_chart_profile
from engine.comparative_test import execute_corpus_battle_comparison
from engine.multi_source_synthesis import _confidence_from_battle, _house_predictions
from engine.per_book_predictions import (
    TOPICS,
    _chart_baseline_answer,
    _collect_rules_for_book,
    _timing_bands,
    DEFAULT_SELECTED_BOOKS,
)
from engine.corpus import get_corpus


TOPIC_ENGINE: dict[str, dict] = {
    "education": {
        "houses": [4, 5, 9],
        "karakas": ["Mercury", "Jupiter"],
        "timing_categories": {"education"},
        "battle_houses": [4, 5, 9],
    },
    "work": {
        "houses": [6, 10, 11, 7],
        "karakas": ["Mercury", "Sun", "Rahu"],
        "timing_categories": {"career", "business", "promotion"},
        "battle_houses": [7, 10, 11],
    },
    "health": {
        "houses": [1, 6, 8, 12],
        "karakas": ["Mars", "Saturn"],
        "timing_categories": {"health_self", "self_accident"},
        "battle_houses": [6, 8, 12],
    },
    "marriage": {
        "houses": [2, 7, 11],
        "karakas": ["Venus", "Mercury"],
        "timing_categories": {"marriage", "engagement"},
        "battle_houses": [2, 7, 11],
    },
    "siblings": {
        "houses": [3, 11],
        "karakas": ["Mars", "Moon"],
        "timing_categories": {"siblings", "elder_sibling"},
        "battle_houses": [3, 11],
    },
}


def _current_dasha(chart: dict, when: dt.datetime) -> dict[str, str]:
    import sys
    from pathlib import Path

    rt = Path(__file__).resolve().parents[1] / "runtime"
    if str(rt) not in sys.path:
        sys.path.insert(0, str(rt))
    from granular_dasha import build_full_timeline, lookup

    active = lookup(build_full_timeline(chart, levels=3), when)
    out = {}
    for lvl, rec in active.items():
        key = {1: "md", 2: "ad", 3: "pd"}.get(lvl)
        if key:
            parts = [rec.get("md"), rec.get("ad"), rec.get("pd")]
            out[key] = "-".join(p for p in parts if p)
    return out


def _dasha_touches_topic(chart: dict, when: dt.datetime, spec: dict) -> tuple[bool, str]:
    import sys
    from pathlib import Path

    rt = Path(__file__).resolve().parents[1] / "runtime"
    if str(rt) not in sys.path:
        sys.path.insert(0, str(rt))
    from granular_dasha import build_full_timeline, lookup

    lords = build_chart_profile(chart)["house_lords"]
    topic_lords = {lords[h] for h in spec["houses"] if h in lords}
    karakas = set(spec["karakas"])

    active = lookup(build_full_timeline(chart, levels=3), when)
    planets = set()
    for rec in active.values():
        for k in ("md", "ad", "pd"):
            if rec.get(k):
                planets.add(rec[k])

    hit = bool(planets & (topic_lords | karakas))
    detail = f"Active dasha planets: {', '.join(sorted(planets))}; topic lords: {', '.join(sorted(topic_lords))}"
    return hit, detail


def _placement_rule_count(chart: dict, topic_id: str) -> int:
    corpus = get_corpus()
    spec = TOPICS[topic_id]
    total = 0
    for book_id in DEFAULT_SELECTED_BOOKS[:8]:
        total += len(_collect_rules_for_book(corpus, book_id, chart, spec, limit=6))
    return total


def _corpus_consensus(chart: dict, battle_houses: list[int]) -> dict:
    lagna = chart.get("lagna", "")
    chart_data = {
        "lagnam_rasi": lagna,
        "lagna_sign": lagna,
        "house_predictions": _house_predictions(chart),
    }
    lords = build_chart_profile(chart)["house_lords"]
    focus = [lords[h] for h in battle_houses if h in lords]
    battle = execute_corpus_battle_comparison(chart_data, focus_lords=focus)
    return _confidence_from_battle(battle)


def _best_timing_band(chart: dict, categories: set[str], when: dt.datetime) -> dict | None:
    bands = _timing_bands(chart, categories, top=8)
    if not bands:
        return None
    today = when.date()
    future = []
    past = []
    for b in bands:
        ws = b.get("window_start")
        if not hasattr(ws, "strftime"):
            continue
        rec = {
            "from": ws.strftime("%Y-%m-%d"),
            "to": (b.get("window_end") or ws).strftime("%Y-%m-%d"),
            "event": b.get("event", b.get("category", "")),
            "severity": b.get("severity", 0),
        }
        if ws.date() >= today:
            future.append(rec)
        else:
            past.append(rec)
    pool = future or past
    pool.sort(key=lambda x: -x["severity"])
    return pool[0] if pool else None


def _chart_signal_ok(chart: dict, topic_id: str) -> tuple[bool, str]:
    """Structural chart read supports this topic (from chart baseline)."""
    base = _chart_baseline_answer(TOPICS[topic_id], chart)
    neg_words = ("denied", "invalidity", "few", "delay", "guard", "caution", "conflict")
    text = base["answer"].lower()
    if topic_id == "health" and "no lifelong invalidity" in text:
        return True, base["answer"]
    if topic_id == "marriage" and "not denied" in text:
        return True, base["answer"]
    if any(w in text for w in ("strong", "completes", "supported", "not denied")):
        return True, base["answer"]
    if topic_id == "siblings":
        return True, base["answer"]
    if not any(w in text for w in neg_words):
        return True, base["answer"]
    return False, base["answer"]


def confirm_topic(
    chart: dict,
    topic_id: str,
    *,
    when: dt.datetime | None = None,
    min_severity: int = 3,
    min_rules: int = 3,
    min_consensus_pct: float = 55.0,
) -> dict[str, Any]:
    when = when or dt.datetime.now()
    spec = TOPIC_ENGINE[topic_id]
    topic = TOPICS[topic_id]

    layers: dict[str, Any] = {}

    ok_chart, chart_txt = _chart_signal_ok(chart, topic_id)
    layers["chart_structure"] = {"pass": ok_chart, "detail": chart_txt}

    ok_dasha, dasha_txt = _dasha_touches_topic(chart, when, spec)
    layers["dasha_active"] = {"pass": ok_dasha, "detail": dasha_txt}

    band = _best_timing_band(chart, spec["timing_categories"], when)
    ok_time = bool(band and band["severity"] >= min_severity)
    layers["timing_band"] = {
        "pass": ok_time,
        "detail": band or "No band in engine sample",
    }

    n_rules = _placement_rule_count(chart, topic_id)
    ok_rules = n_rules >= min_rules
    layers["placement_rules"] = {
        "pass": ok_rules,
        "detail": f"{n_rules} strict placement-matched rules (sample 8 books)",
    }

    consensus = _corpus_consensus(chart, spec["battle_houses"])
    ok_cons = (
        consensus["confidence_pct"] >= min_consensus_pct
        and consensus.get("status") != "Strong Contradiction"
    )
    layers["corpus_consensus"] = {
        "pass": ok_cons,
        "detail": (
            f"{consensus['confidence_pct']}% agreement, status={consensus['status']}, "
            f"{consensus['rules_analyzed']} rules"
        ),
    }

    passes = sum(1 for v in layers.values() if v["pass"])
    if passes >= 4 and ok_chart:
        verdict = "CONFIRMED"
    elif passes >= 2:
        verdict = "MIXED"
    else:
        verdict = "NOT CONFIRMED"

    dasha = _current_dasha(chart, when)

    return {
        "topic_id": topic_id,
        "title": topic.title_en,
        "verdict": verdict,
        "layers_pass": passes,
        "layers_total": len(layers),
        "layers": layers,
        "dasha_now": dasha,
        "confirmed_statement": _build_statement(topic_id, verdict, layers, chart, band),
    }


def _build_statement(
    topic_id: str,
    verdict: str,
    layers: dict,
    chart: dict,
    band: dict | None,
) -> str:
    base = (
        layers["chart_structure"]["detail"]
        .replace("possible", "supported when dasha runs")
        .replace("Possible", "Supported when dasha runs")
        .replace("Likely", "Chart indicates")
    )
    if verdict == "NOT CONFIRMED":
        return (
            f"Engine does NOT confirm {topic_id}: only {sum(1 for v in layers.values() if v['pass'])}/5 "
            f"layers agree. Do not treat as a firm prediction."
        )
    if verdict == "MIXED":
        return (
            f"Engine MIXED on {topic_id}: chart says: {base[:120]}. "
            f"Some layers disagree - see table."
        )

    parts = [f"Engine CONFIRMS {topic_id}:"]
    parts.append(base[:200])
    if layers["dasha_active"]["pass"]:
        parts.append(f"Dasha supports topic ({layers['dasha_active']['detail'][:80]}).")
    if band:
        parts.append(
            f"Timing band {band['from']} to {band['to']} (severity {band['severity']}): {band['event'][:60]}."
        )
    parts.append(
        f"Corpus: {layers['corpus_consensus']['detail']}."
    )
    return " ".join(parts)


def build_engine_confirmed_report(
    chart: dict,
    *,
    when: dt.datetime | None = None,
    topic_ids: list[str] | None = None,
) -> str:
    when = when or dt.datetime(2026, 6, 2)
    age = when.year - chart["birth"]["year"]
    b = chart["birth"]
    if (when.month, when.day) < (b["month"], b["day"]):
        age -= 1

    topic_ids = topic_ids or list(TOPIC_ENGINE.keys())
    results = [confirm_topic(chart, tid, when=when) for tid in topic_ids]

    lines = [
        "# Engine-confirmed predictions (no manual life facts)",
        "",
        f"**{chart.get('name')}** | age **{age}** | {when.strftime('%d %b %Y')}",
        "",
        "Confirmation = **your engine only**: chart + dasha + timing bands + placement rules + book consensus.",
        "",
        "Verdict meanings:",
        "- **CONFIRMED** = 4+ of 5 engine layers agree",
        "- **MIXED** = 2-3 layers agree",
        "- **NOT CONFIRMED** = engine does not agree with itself on this topic",
        "",
        "This is **not** 'possible/likely' language - it is pass/fail from internal engine checks.",
        "",
        "## Summary table",
        "",
        "| Topic | Engine verdict | Layers pass | Confirmed statement |",
        "|-------|----------------|-------------|---------------------|",
    ]
    for r in results:
        stmt = r["confirmed_statement"].replace("|", "/")
        if len(stmt) > 100:
            stmt = stmt[:97] + "..."
        lines.append(
            f"| {r['title']} | **{r['verdict']}** | {r['layers_pass']}/5 | {stmt} |"
        )

    d0 = results[0]["dasha_now"] if results else {}
    lines.extend(
        [
            "",
            f"**Dasha now:** MD {d0.get('md','?')} | AD {d0.get('ad','?')} | PD {d0.get('pd','?')}",
            "",
            "## Layer detail per topic",
            "",
        ]
    )

    for r in results:
        lines.append(f"### {r['title']} - **{r['verdict']}**")
        lines.append("")
        lines.append(r["confirmed_statement"])
        lines.append("")
        lines.append("| Layer | Pass? | Detail |")
        lines.append("|-------|-------|--------|")
        for name, data in r["layers"].items():
            lines.append(
                f"| {name} | {'YES' if data['pass'] else 'NO'} | {str(data['detail'])[:90]} |"
            )
        lines.append("")

    lines.append(
        "---\n**Note:** CONFIRMED here means the **engine's own modules agree**, "
        "not that a human verified the event in real life. "
        "Celebrity charts use `known_events` for that second step; private clients use this engine agreement until you add life facts."
    )
    return "\n".join(lines)
