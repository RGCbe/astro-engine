"""Convergence-gated life-event fusion (option B).

Motivation (see ACCURACY_DIAGNOSIS.json / HONEST_ACCURACY*.json, 2026-07-15):
the raw event scan emits ~35 predictions per lifespan-year with wide windows, so
its recall barely beats the same predictions shuffled to random dates (+1.9 to
+3.1 pts, 0/16 charts significant). Severity filtering makes it WORSE — volume,
not conviction, drives the headline number.

This layer applies the truth-engine fusion principle to life events:

  * every raw prediction is classified into a METHOD FAMILY;
  * a fused event is emitted only when >= 2 independent, gating-eligible
    families converge on the same TOPIC with overlapping TIGHT windows
    (the `first`..`last` band, not the diffuse `window_start`..`window_end`);
  * the fused window is the true intersection of the overlapping bands and
    is discarded when wider than `max_window_days` — a claim too diffuse to
    verify is not a claim;
  * esoteric families (western/chinese/mayan/numerology/palmistry/iching)
    never satisfy the gate: they may correlate but are not independent
    classical timing evidence.

Pure stdlib; no engine imports — safe from any entry point.
"""
from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Mapping

# ── Method-family classification ────────────────────────────────────────────

# Families allowed to satisfy the convergence gate by default (classical timing).
GATING_FAMILIES = frozenset({
    "parashari", "transit", "jaimini", "kp", "nadi", "tajik", "divisional", "yoga",
})

# Non-classical families. Excluded from the default gate (calendar-driven cycles
# fire on schedule regardless of the chart, so their agreement is coincidence-
# prone) — but ALL_FAMILIES lets experiments measure that assumption.
ESOTERIC_FAMILIES = frozenset({
    "esoteric_mayan", "esoteric_chinese", "esoteric_western",
    "esoteric_numerology", "esoteric_palmistry", "esoteric_iching",
    "esoteric_psychic",
})

ALL_FAMILIES = GATING_FAMILIES | ESOTERIC_FAMILIES

# category-prefix / category-keyword rules, checked in order.
_CATEGORY_FAMILY_RULES: tuple[tuple[str, str], ...] = (
    (r"^saham_", "tajik"),
    (r"^tajik_", "tajik"),
    (r"^(annual_profection|solar_return|varshaphala|muntha)", "tajik"),
    (r"^kp_", "kp"),
    (r"^nadi_", "nadi"),
    (r"^d\d+_", "divisional"),
    (r"^(sade_sati|ashtam_shani|ardha_ashtam|kantaka|saturn_return|eclipse|gochar)", "transit"),
    (r"^(jaimini|chara_|karakamsa|arudha|upapada)", "jaimini"),
    (r"(_yoga|^yoga_|^vipareeta|^kala_sarpa|^kemadruma|^gajakesari)", "yoga"),
    # esoteric (non-gating)
    (r"^(mayan_|tzolkin)", "esoteric_mayan"),
    (r"^(bazi_|ziwei_|chinese_)", "esoteric_chinese"),
    (r"^(pluto_|uranus_|neptune_|progressed_|solar_arc|venus_retro|western_)", "esoteric_western"),
    (r"^(personal_year|pinnacle_|numerology|life_path)", "esoteric_numerology"),
    (r"^(palmistry_|mark_scar|mole_|body_|face_|hasta)", "esoteric_palmistry"),
    (r"^(iching_|kua_|feng_shui)", "esoteric_iching"),
    (r"^(astral_|prophetic_|prophecy|psychic_)", "esoteric_psychic"),
)

_SOURCE_FAMILY_HINTS: tuple[tuple[str, str], ...] = (
    ("jaimini", "jaimini"),
    ("kp reader", "kp"),
    ("krishnamurti", "kp"),
    ("nadi", "nadi"),
    ("tajik", "tajik"),
    ("varshaphala", "tajik"),
    ("sade sati", "transit"),
    ("transit", "transit"),
    ("mayan", "esoteric_mayan"),
    ("bazi", "esoteric_chinese"),
    ("zi wei", "esoteric_chinese"),
    ("numerology", "esoteric_numerology"),
    ("samudrika", "esoteric_palmistry"),
    ("western", "esoteric_western"),
)


def classify_family(event: Mapping[str, Any]) -> str:
    """Classify a raw prediction into a method family.

    Category rules first (most reliable), then source-text hints, then
    default to parashari (house-lord/dasha logic from the classical corpus).
    """
    category = str(event.get("category", "")).lower()
    for pattern, family in _CATEGORY_FAMILY_RULES:
        if re.search(pattern, category):
            return family
    source = str(event.get("source", "")).lower()
    for needle, family in _SOURCE_FAMILY_HINTS:
        if needle in source:
            return family
    return "parashari"


# ── Topic mapping (aligned with the verified-event categories the scorers use) ──

_TOPIC_MEMBERS: dict[str, frozenset[str]] = {
    "career": frozenset({
        "career", "career_breakthrough", "political_office", "promotion",
        "profession_switch", "ceo_role", "business", "business_closure",
        "kp_career_sub", "d10_career_sub",
        # Tajik: Karya saham is the work/undertakings saham (career, not wealth)
        "saham_karya",
        # career-flavoured Parashari categories (same family, but they widen
        # tight-band coverage so cross-family overlap becomes possible)
        "leadership_emergence", "media_career", "finance_career",
        "medical_career", "singing_career", "acting", "salary_raise",
        "public_speaking_debut",
        # Adhi yoga classically confers authority/ministership
        "adhi_yoga",
    }),
    "honor": frozenset({
        "honor", "honor_recognition", "award_nomination", "royal_favor", "brand_deal",
        # Tajik: Yasas saham is the fame/renown saham
        "saham_yasas",
        "intellectual_fame", "reputation_cycle",
    }),
    "marriage": frozenset({"marriage", "relationship_phase", "second_marriage", "saham_kalatra"}),
    "father": frozenset({"father"}),
    "mother": frozenset({"mother"}),
    "children": frozenset({"children", "child_birth", "child", "pregnancy", "saham_putra"}),
    "widowhood": frozenset({"widowhood", "relationship_break", "partner_betrayal"}),
    "health": frozenset({
        "health", "health_self", "self_accident", "d30_disease_sub", "saham_roga",
        "vehicle_accident", "kp_health_sub",
    }),
    "wealth": frozenset({
        "wealth", "wealth_peak", "wealth_loss", "loan_default", "sudden_gain",
        "speculation_gain", "wealth_inheritance", "d2_wealth_sub", "mahapadma_yoga",
    }),
    "property": frozenset({"property", "property_loss", "property_dispute", "vehicle", "relocation"}),
    "travel": frozenset({"travel", "foreign_travel", "short_trip", "pilgrimage", "adventure_travel"}),
    "spiritual": frozenset({"spiritual", "spirituality", "religious_conversion", "d20_spirit_sub", "saham_punya"}),
    "education": frozenset({"education", "d24_edu_sub", "saham_vidya"}),
    "sibling": frozenset({"sibling", "siblings", "sibling_bond", "sibling_health", "d3_sibling_sub"}),
    "death_self": frozenset({"death_self", "saham_marana"}),
}

# Esoteric categories with defensible topic semantics. These only matter when an
# experiment widens the gate (ALL_FAMILIES); the default gate filters their
# families out before topics are consulted.
_ESOTERIC_TOPIC_MEMBERS: dict[str, frozenset[str]] = {
    "health": frozenset({"palmistry_life_break", "mark_scar_discovery", "bazi_clash_year"}),
    "career": frozenset({"pinnacle_change", "progressed_sun"}),
    "marriage": frozenset({"venus_retro"}),
}
for _topic, _cats in _ESOTERIC_TOPIC_MEMBERS.items():
    _TOPIC_MEMBERS[_topic] = _TOPIC_MEMBERS[_topic] | _cats

_CATEGORY_TO_TOPIC: dict[str, str] = {}
for _topic in sorted(_TOPIC_MEMBERS):
    for _cat in _TOPIC_MEMBERS[_topic]:
        _CATEGORY_TO_TOPIC.setdefault(_cat, _topic)


def topic_for_category(category: str) -> str | None:
    """Map an engine category to a verifiable life-event topic (or None)."""
    return _CATEGORY_TO_TOPIC.get(str(category).lower())


# ── Fusion ──────────────────────────────────────────────────────────────────

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def _parse_date(value: Any) -> datetime | None:
    text = str(value or "")[:10]
    if not _DATE_RE.match(text):
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        return None


def _tight_interval(event: Mapping[str, Any]) -> tuple[datetime, datetime] | None:
    """The event's tight band: first..last, else its single peak date.

    The diffuse window_start..window_end is deliberately NOT used — the
    diagnosis showed those windows reach a decade wide and carry no timing
    discrimination.
    """
    start = _parse_date(event.get("first"))
    end = _parse_date(event.get("last"))
    if start and end and end >= start:
        return start, end
    peak = _parse_date(event.get("date") or event.get("peak_date"))
    if peak:
        return peak, peak
    return None


def fuse_events(
    pred_events: list[Mapping[str, Any]],
    *,
    min_families: int = 2,
    max_window_days: int = 540,
    slack_days: int = 30,
    gating_families: frozenset[str] = GATING_FAMILIES,
) -> list[dict[str, Any]]:
    """Emit convergence-gated events from a raw prediction list.

    For each topic, sweep the tight bands in start order maintaining a running
    intersection (each member must overlap the current intersection, expanded
    by `slack_days`). A cluster yields a fused event only if it contains
    >= `min_families` distinct gating families and its intersection is at most
    `max_window_days` wide.
    """
    slack = timedelta(days=slack_days)

    by_topic: dict[str, list[tuple[datetime, datetime, str, Mapping[str, Any]]]] = {}
    for ev in pred_events:
        topic = topic_for_category(str(ev.get("category", "")))
        if topic is None:
            continue
        family = classify_family(ev)
        if family not in gating_families:
            continue
        interval = _tight_interval(ev)
        if interval is None:
            continue
        by_topic.setdefault(topic, []).append((interval[0], interval[1], family, ev))

    fused: list[dict[str, Any]] = []
    for topic in sorted(by_topic):
        members = sorted(by_topic[topic], key=lambda item: (item[0], item[1], item[2]))
        cluster: list[tuple[datetime, datetime, str, Mapping[str, Any]]] = []
        cur_start: datetime | None = None
        cur_end: datetime | None = None

        def _flush() -> None:
            if not cluster or cur_start is None or cur_end is None:
                return
            families = sorted({m[2] for m in cluster})
            if len(families) < min_families:
                return
            if (cur_end - cur_start).days > max_window_days:
                return
            midpoint = cur_start + (cur_end - cur_start) / 2
            valences = Counter(
                str(m[3].get("predicted_valence"))
                for m in cluster
                if m[3].get("predicted_valence")
            )
            fused.append({
                "event": f"Converged {topic.replace('_', ' ')} indication "
                         f"({len(families)} independent methods)",
                "category": topic,
                "window_start": cur_start.strftime("%Y-%m-%d"),
                "window_end": cur_end.strftime("%Y-%m-%d"),
                "date": midpoint.strftime("%Y-%m-%d"),
                "max_sev": max(int(m[3].get("max_sev", m[3].get("severity", 3)) or 3) for m in cluster),
                "families": families,
                "contributors": len(cluster),
                "predicted_valence": valences.most_common(1)[0][0] if valences else None,
            })

        for start, end, family, ev in members:
            if cur_start is None:
                cluster = [(start, end, family, ev)]
                cur_start, cur_end = start, end
                continue
            if start <= (cur_end + slack) and end >= (cur_start - slack):
                cluster.append((start, end, family, ev))
                cur_start = max(cur_start, start)
                cur_end = min(cur_end, end) if end < cur_end else cur_end
                if cur_end < cur_start:  # degenerate after slack-admitted member
                    cur_end = cur_start
            else:
                _flush()
                cluster = [(start, end, family, ev)]
                cur_start, cur_end = start, end
        _flush()

    fused.sort(key=lambda f: (f["window_start"], f["category"]))
    return fused
