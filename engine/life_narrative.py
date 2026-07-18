"""
Life-narrative renderer — three modes:

    Mode A  timeline_table(chart)              → readable past/now/future timeline
    Mode B  ask(chart, question_str)            → natural-language Q&A
    Mode C  full_narrative(chart)               → 30-page life report (text)

All three consume the structured outputs of `engine.synth` + `engine.dasa_narrative`
+ `engine.book_rules`. No LLMs, fully deterministic.

Module name `life_narrative` to avoid collision with the v1.5 `narrative.py`
(which is the affliction → English client-text translator).
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass

from engine.dasa_narrative import (
    DasaPrediction, build_timeline, find_for_date, find_window,
)
from engine.engines.orchestrator import run_all
from engine.synth import synthesize


# ─── Mode A — Timeline table ──────────────────────────────────────────────

def timeline_table(chart, *, today: dt.date | None = None,
                    past_n: int = 6, future_n: int = 8) -> str:
    """Pretty timeline with past windows, current row marked ★, and forecast."""
    today = today or dt.date.today()
    tl = build_timeline(chart, today=today)
    past = [d for d in tl if d.is_past][-past_n:]
    cur = [d for d in tl if d.is_current]
    fut = [d for d in tl if d.is_future][:future_n]

    rows: list[str] = []
    rows.append(f"  {'Period':24s} {'Dasha':16s} {'Quality':12s} {'Age':12s} Theme")
    rows.append("  " + "-" * 108)

    def fmt(d: DasaPrediction, marker: str = " ") -> str:
        period = f"{d.period_start} → {d.period_end}"
        dasha = f"{d.md_lord}-{d.ad_lord}"
        age = f"{d.age_start:>4.1f}–{d.age_end:>4.1f}"
        return f"{marker} {period:22s} {dasha:16s} {d.quality:12s} {age:12s} {d.headline}"

    for d in past:    rows.append(fmt(d))
    for d in cur:     rows.append(fmt(d, "★"))
    for d in fut:     rows.append(fmt(d))
    return "\n".join(rows)


# ─── Mode B — Q&A interface ───────────────────────────────────────────────

QUESTION_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b(family business|dad['s ]+|father['s ]+|family.*shop)", re.I), "family_business_window"),
    (re.compile(r"\b(promot|raise\b|salary|increment|upgrade|career upgrade)", re.I), "career_upgrade"),
    (re.compile(r"\b(job change|switch job|new compan|leave job|quit job|change.*compan|new job)\b", re.I), "career_change"),
    (re.compile(r"\b(marri|spouse|wife|husband|wedding|partner)", re.I), "marriage_window"),
    (re.compile(r"\b(child|baby|kid\b|son|daughter|progeny|pregnan)\b", re.I), "children_window"),
    (re.compile(r"\b(foreign|abroad|onsite|relocat|overseas|usa|uk|gulf|dubai|singapore|migrate)\b", re.I), "foreign_window"),
    (re.compile(r"\b(propert|house\b|car\b|vehicle|land\b|home\b|flat\b)\b", re.I), "property_window"),
    (re.compile(r"\b(spirit|loss|withdraw|moksha|monk|temple|pilgrim)\b", re.I), "spiritual_or_loss"),
]
PAST_QUESTION = re.compile(r"\b(did|when did|what happened|was|were|have I|has\b)\b", re.I)
FUTURE_QUESTION = re.compile(r"\b(will|when will|next|going to|upcoming|future)\b", re.I)


@dataclass
class AnswerWindow:
    period_start: dt.date
    period_end: dt.date
    headline: str
    detail: str
    confidence: str
    quality: str
    md_ad: str


@dataclass
class Answer:
    question: str
    found: bool
    summary: str
    windows: list[AnswerWindow]
    note: str = ""


def _to_aw(d: DasaPrediction) -> AnswerWindow:
    return AnswerWindow(
        period_start=d.period_start, period_end=d.period_end,
        headline=d.headline, detail=d.detail,
        confidence=d.confidence, quality=d.quality,
        md_ad=f"{d.md_lord}-{d.ad_lord}",
    )


def _date_in_question(q: str) -> dt.date | None:
    m = re.search(r"\b(19|20|21)\d{2}\b", q)
    if m:
        return dt.date(int(m.group()), 6, 1)
    return None


def ask(chart, question: str, *, today: dt.date | None = None) -> Answer:
    today = today or dt.date.today()
    q = question.strip()

    # Year-anchored
    yr = _date_in_question(q)
    if yr:
        d = find_for_date(chart, yr)
        if d:
            return Answer(
                question=q, found=True,
                summary=(f"In {yr.year} you were in {d.md_lord}-{d.ad_lord} "
                         f"({d.headline}, {d.quality})."),
                windows=[_to_aw(d)],
            )

    matched_event: str | None = None
    for rx, ev in QUESTION_PATTERNS:
        if rx.search(q):
            matched_event = ev
            break
    if not matched_event:
        return Answer(
            question=q, found=False,
            summary=("I can answer about: career change, promotion, marriage, "
                     "children, foreign travel, property, family-business "
                     "windows, or any specific year."),
            windows=[], note="No event keyword detected.",
        )

    windows = find_window(chart, matched_event, today=today)
    direction = "future" if FUTURE_QUESTION.search(q) else (
                 "past" if PAST_QUESTION.search(q) else "any")
    if direction == "future":
        # Strictly upcoming windows; ongoing window is excluded for "will" questions
        windows = [d for d in windows if d.period_start >= today]
    elif direction == "past":
        windows = [d for d in windows if d.period_end < today]

    if not windows:
        return Answer(
            question=q, found=False,
            summary=f"No {matched_event.replace('_', ' ')} window detected ({direction}).",
            windows=[],
        )

    if direction == "future":
        windows.sort(key=lambda d: d.period_start)
    else:
        windows.sort(key=lambda d: d.period_start, reverse=True)
    primary = windows[0]
    return Answer(
        question=q, found=True,
        summary=(f"{matched_event.replace('_', ' ').title()}: "
                 f"{primary.period_start} → {primary.period_end} "
                 f"({primary.md_lord}-{primary.ad_lord}, {primary.quality})."),
        windows=[_to_aw(d) for d in windows[:5]],
    )


# ─── Mode C — Full narrative ──────────────────────────────────────────────

def _domain_section(chart, category: str, title: str) -> list[str]:
    out: list[str] = [f"\n## {title}\n"]
    rep = next(iter(run_all(chart, only=(category,))), None)
    if rep is None:
        return out + ["(no data)\n"]
    for p in rep.predictions:
        v = p.value if isinstance(p.value, str) else str(p.value)
        cit = f"  *[{p.citations[0].book}]*" if p.citations else ""
        out.append(f"- **{p.label}**{cit}\n  {v[:280]}")
    return out


def _summary_header(chart) -> list[str]:
    facts = synthesize(chart)
    out = [f"# Life Reading — {chart.name}\n"]
    out.append(f"Birth: {chart.birth_dt.isoformat()} · {chart.place}\n")
    out.append(f"Lagna: **{chart.lagna_sign}** (lord {chart.lagna_lord}) · "
               f"Moon sign: **{facts['Moon'].sign}** · "
               f"Janma Nakshatra: **{chart.lagna_nakshatra}**\n")
    out.append("\n### Planet placements\n")
    out.append("| Planet | House | Sign | Dignity | Owns | Conjunct |")
    out.append("|---|---|---|---|---|---|")
    for p, f in facts.items():
        owns = "/".join(f"{h}H" for h in f.bhavas_owned) or "—"
        conj = ", ".join(f.conjunctions) or "—"
        out.append(f"| {p} | H{f.house} | {f.sign} | {f.dignity} | {owns} | {conj} |")
    return out


def _timeline_section(chart, today: dt.date) -> list[str]:
    return ["\n## Life Timeline (Vimshottari)\n",
            "```\n" + timeline_table(chart, today=today) + "\n```\n"]


def full_narrative(chart, *, today: dt.date | None = None) -> str:
    today = today or dt.date.today()
    parts: list[str] = []
    parts.extend(_summary_header(chart))
    parts.extend(_timeline_section(chart, today))
    domains = [
        ("personality", "Personality & Body"),
        ("career", "Career & Profession"),
        ("marriage", "Marriage & Partnership"),
        ("children", "Children & Progeny"),
        ("wealth", "Wealth & Finance"),
        ("health", "Health"),
        ("family", "Family — Parents & Siblings"),
        ("foreign", "Foreign & Travel"),
        ("spirituality", "Spirituality & Dharma"),
        ("longevity", "Longevity"),
        ("yogas", "Yogas (Blessings)"),
        ("afflictions", "Afflictions & Doshas"),
        ("remedies", "Remedies"),
    ]
    for cat, title in domains:
        parts.extend(_domain_section(chart, cat, title))
    return "\n".join(parts)
