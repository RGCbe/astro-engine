"""Fuse corpus consensus per life topic (P0-3): confidence + disagreement note."""
from __future__ import annotations

from typing import Any

from engine.chart_profile import build_chart_profile
from engine.comparative_test import execute_corpus_battle_comparison

TOPICS: dict[str, dict[str, Any]] = {
    "marriage": {"label": "Marriage / partnership", "houses": [7]},
    "career": {"label": "Career / profession", "houses": [10]},
    "wealth": {"label": "Wealth / gains", "houses": [2, 11]},
    "health": {"label": "Health / vitality", "houses": [6, 8]},
}


def _house_predictions(chart: dict[str, Any]) -> list[dict[str, Any]]:
    by_house: dict[int, list[str]] = {h: [] for h in range(1, 13)}
    for planet, pdata in (chart.get("positions") or {}).items():
        if planet == "Ketu":
            continue
        h = pdata.get("house")
        if isinstance(h, int) and 1 <= h <= 12:
            by_house[h].append(planet)
    return [{"house": h, "planets": ps} for h, ps in by_house.items() if ps]


def _topic_focus_lords(chart: dict[str, Any], houses: list[int]) -> list[str]:
    lords = build_chart_profile(chart)["house_lords"]
    return [lords[h] for h in houses if h in lords]


def _confidence_from_battle(battle: dict[str, Any]) -> dict[str, Any]:
    if not battle:
        return {
            "confidence_pct": 50,
            "status": "No corpus hits",
            "rules_analyzed": 0,
            "disagreement": False,
        }
    scores = []
    statuses = []
    total_rules = 0
    for data in battle.values():
        c = data.get("consensus") or {}
        scores.append(float(c.get("consensus_percent", 50)))
        statuses.append(c.get("status", "Mixed"))
        total_rules += int(c.get("total_rules_analyzed", 0))
    avg = sum(scores) / len(scores) if scores else 50.0
    disagreement = any(s == "Strong Contradiction" for s in statuses) or (
        min(scores) < 40 and max(scores) > 60
    ) if scores else False
    dominant = max(set(statuses), key=statuses.count) if statuses else "Mixed"
    return {
        "confidence_pct": round(avg, 1),
        "status": dominant,
        "rules_analyzed": total_rules,
        "disagreement": disagreement,
        "subjects": list(battle.keys())[:6],
    }


def synthesize_life_topics(chart: dict[str, Any]) -> dict[str, Any]:
    """Per-topic fusion from lagna-filtered corpus battle (KP/Jaimini hooks later)."""
    lagna = chart.get("lagna") or chart.get("lagnam_rasi")
    chart_data = {
        "lagnam_rasi": lagna,
        "lagna_sign": lagna,
        "house_predictions": _house_predictions(chart),
        "shadbala": chart.get("shadbala", {}),
        "ashtakavarga": chart.get("ashtakavarga", {}),
    }

    topics_out: dict[str, Any] = {}
    for key, spec in TOPICS.items():
        focus = _topic_focus_lords(chart, spec["houses"])
        battle = execute_corpus_battle_comparison(chart_data, focus_lords=focus)
        filtered = {
            k: v
            for k, v in battle.items()
            if any(f"House {h}" in k or f"H{h}" in k for h in spec["houses"])
        }
        conf = _confidence_from_battle(filtered or battle)
        note = (
            f"{spec['label']}: {conf['status']} "
            f"(corpus agreement index {conf['confidence_pct']}%, "
            f"{conf['rules_analyzed']} rules). "
        )
        if conf["disagreement"]:
            note += "Books disagree; treat as mixed indication, not a single verdict."
        else:
            note += "Classical lines mostly align on valence for this topic."
        topics_out[key] = {
            "label": spec["label"],
            "confidence_pct": conf["confidence_pct"],
            "status": conf["status"],
            "disagreement": conf["disagreement"],
            "rules_analyzed": conf["rules_analyzed"],
            "summary_en": note,
            "battle_sample": {
                k: {
                    "consensus": v.get("consensus"),
                    "top_rule": (v.get("top_rules") or [None])[0],
                }
                for k, v in list((filtered or battle).items())[:3]
            },
            "nature": "corpus_agreement_index",
            "disclaimer": (
                "Agreement among indexed passages; not probability of the event."
            ),
        }

    return {
        "chart_profile_ref": build_chart_profile(chart)["executive_summary_en"],
        "topics": topics_out,
    }
