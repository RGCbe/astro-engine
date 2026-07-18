"""
Dasa-narrative engine — converts every Antardasha into a dated, life-area-tagged
DasaPrediction by joining synth.ChartFact with the Vimshottari schedule.

This is the module that turns "Sun-Mercury AD 2021-04→2022-03" into
"likely father-business / family-trade activation window".
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from engine.engines import Citation
from engine.synth import ChartFact, KARAKA, BHAVA_AREAS, fact, synthesize, lord_of


# Map a planet's role-set onto a coarse "headline life-area" so the
# narrative is readable rather than a soup of tags.
ROLE_TO_HEADLINE: list[tuple[set[str], str]] = [
    ({"father"}, "Father / family-elder activation"),
    ({"mother"}, "Mother / home-front activation"),
    ({"spouse"}, "Spouse / partnership activation"),
    ({"children"}, "Children / progeny activation"),
    ({"siblings_younger"}, "Siblings / peers activation"),
    ({"foreign_lands"}, "Foreign / distant-land activation"),
    ({"career_authority", "career"}, "Career / public-status activation"),
    ({"wealth", "gains", "income"}, "Wealth / income activation"),
    ({"service_employer", "service"}, "Service / employment activation"),
    ({"discipline", "responsibility"}, "Responsibility / discipline period"),
    ({"spirituality", "moksha"}, "Spirituality / detachment phase"),
    ({"property", "land_property", "vehicles"}, "Property / vehicle activation"),
    ({"loss", "expense"}, "Loss / expenditure phase"),
    ({"longevity"}, "Health / longevity check phase"),
]

# Confidence baseline by dignity of the AD-lord (better dignity = clearer outcome)
DIGNITY_CONFIDENCE = {
    "exalted": "HIGH",
    "own": "HIGH",
    "neutral": "MEDIUM",
    "debilitated": "LOW",
}

# House-strength buckets used for "good vs bad" tilt
KENDRA = (1, 4, 7, 10)
TRIKONA = (1, 5, 9)
DUSTHANA = (6, 8, 12)
UPACHAYA = (3, 6, 10, 11)


@dataclass
class DasaPrediction:
    period_start: dt.date
    period_end: dt.date
    md_lord: str
    ad_lord: str
    age_start: float            # age in years at period_start
    age_end: float
    life_areas: list[str]       # merged areas activated during this AD
    headline: str               # one-line summary
    detail: str                 # 2-4 sentence narrative
    confidence: str             # HIGH / MEDIUM / LOW
    quality: str                # FAVOURABLE / MIXED / CHALLENGING
    triggers_event: str         # promotion / marriage / relocation / "" etc
    citations: list[Citation] = field(default_factory=list)
    is_current: bool = False
    is_past: bool = False
    is_future: bool = False


# ─── Period quality scoring ───────────────────────────────────────────────

def _quality_for(md_fact: ChartFact, ad_fact: ChartFact) -> str:
    score = 0
    for f in (md_fact, ad_fact):
        if f.dignity == "exalted":  score += 2
        elif f.dignity == "own":    score += 1
        elif f.dignity == "debilitated": score -= 2
        if f.house in TRIKONA:      score += 1
        if f.house in KENDRA:       score += 1
        if f.house in DUSTHANA:     score -= 1
        if f.is_combust:            score -= 1
    if score >= 3:  return "FAVOURABLE"
    if score <= -2: return "CHALLENGING"
    return "MIXED"


# ─── Headline + life-area picker ──────────────────────────────────────────

def _life_areas(md_fact: ChartFact, ad_fact: ChartFact) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for area in (md_fact.life_areas + ad_fact.life_areas):
        if area not in seen:
            seen.add(area); out.append(area)
    return out


EVENT_HEADLINES = {
    "family_business_window": "Family-business / father-collaboration window",
    "marriage_window":       "Marriage / spouse-event window",
    "career_upgrade":        "Career upgrade / promotion window",
    "career_change":         "Career change / job-shift window",
    "children_window":       "Children / progeny event window",
    "foreign_window":        "Foreign / distant-land window",
    "property_window":       "Property / vehicle / home window",
    "spiritual_or_loss":     "Spiritual / loss / withdrawal window",
}


def _headline(md_fact: ChartFact, ad_fact: ChartFact, triggers: str) -> str:
    """Headline priority: explicit event > AD karaka role > MD theme."""
    # 1) Use the most-specific event trigger
    for ev in triggers.split(","):
        if ev in EVENT_HEADLINES:
            return EVENT_HEADLINES[ev]
    # 2) Use AD-lord first karaka that matches a marker set
    for area in ad_fact.karaka_roles + ad_fact.bhava_areas:
        for marker, head in ROLE_TO_HEADLINE:
            if area in marker:
                return head
    # 3) Use MD-lord first karaka
    for area in md_fact.karaka_roles:
        for marker, head in ROLE_TO_HEADLINE:
            if area in marker:
                return head
    return f"{md_fact.planet} – {ad_fact.planet} period"


# ─── Event triggers (promotion / marriage / etc) ─────────────────────────

def _event_triggers(chart, md_fact: ChartFact, ad_fact: ChartFact) -> str:
    """Detect specific dated events when the AD-lord activates a key bhava."""
    events: list[str] = []

    # Career events: AD-lord owns or sits in 10H, with MD-lord supporting
    if 10 in ad_fact.bhavas_owned or ad_fact.house == 10:
        if ad_fact.dignity in ("exalted", "own") or ad_fact.house in KENDRA + TRIKONA:
            events.append("career_upgrade")
        else:
            events.append("career_change")

    # Marriage: 7L active or Venus active + 7H lit
    venus_h = chart.house_of.get("Venus", 0)
    if (7 in ad_fact.bhavas_owned or ad_fact.planet == "Venus" or ad_fact.house == 7
            or 7 in md_fact.bhavas_owned):
        if md_fact.dignity != "debilitated" and venus_h not in DUSTHANA:
            events.append("marriage_window")

    # Children: 5L + Jupiter
    if (5 in ad_fact.bhavas_owned or ad_fact.planet == "Jupiter") and "children" in ad_fact.life_areas:
        events.append("children_window")

    # Foreign: Rahu / 12L / 9L active
    if ad_fact.planet == "Rahu" or 12 in ad_fact.bhavas_owned or ad_fact.house == 12:
        events.append("foreign_window")

    # Property: 4L / Mars / Venus active in 4H
    if 4 in ad_fact.bhavas_owned or (ad_fact.planet in ("Mars", "Venus") and ad_fact.house == 4):
        events.append("property_window")

    # Spiritual / loss: Ketu or 12L active
    if ad_fact.planet == "Ketu" or 12 in ad_fact.bhavas_owned:
        events.append("spiritual_or_loss")

    # Family-business: father-karaka active AND career-lord activated together
    sun_md = md_fact.planet == "Sun"
    career_lord_active = ad_fact.planet == lord_of(chart, 10) or 10 in ad_fact.bhavas_owned
    if sun_md and career_lord_active:
        events.insert(0, "family_business_window")

    return ",".join(events)


# ─── Detail composer ──────────────────────────────────────────────────────

def _detail(md_fact: ChartFact, ad_fact: ChartFact) -> str:
    md_areas = ", ".join(md_fact.life_areas[:4])
    ad_areas = ", ".join(ad_fact.life_areas[:4])
    md_dig = f" ({md_fact.dignity})" if md_fact.dignity != "neutral" else ""
    ad_dig = f" ({ad_fact.dignity})" if ad_fact.dignity != "neutral" else ""
    own_md = ", owns " + "/".join(f"{h}H" for h in md_fact.bhavas_owned) if md_fact.bhavas_owned else ""
    own_ad = ", owns " + "/".join(f"{h}H" for h in ad_fact.bhavas_owned) if ad_fact.bhavas_owned else ""
    return (
        f"MD lord {md_fact.planet} sits in H{md_fact.house}{md_dig}{own_md} — themes: {md_areas}. "
        f"AD lord {ad_fact.planet} sits in H{ad_fact.house}{ad_dig}{own_ad} — themes: {ad_areas}."
    )


# ─── Main builder ─────────────────────────────────────────────────────────

def _to_date(x) -> dt.date:
    if isinstance(x, dt.datetime): return x.date()
    if isinstance(x, dt.date): return x
    return dt.date.fromisoformat(str(x)[:10])


def _age(birth: dt.datetime, when: dt.date) -> float:
    return round((when - birth.date()).days / 365.25, 1)


def build_timeline(chart, *, today: dt.date | None = None) -> list[DasaPrediction]:
    """Walk every AD in Vimshottari, emit a DasaPrediction each."""
    today = today or dt.date.today()
    facts = synthesize(chart)
    out: list[DasaPrediction] = []
    
    from engine.dasha import full_timeline
    timeline = full_timeline(chart, levels=2)
    ads = [r for r in timeline if r.get("level") == 2]
    
    for ad in ads:
        md_lord = ad["md"]
        ad_lord = ad["ad"]
        md_fact = facts.get(md_lord) or fact(chart, md_lord)
        ad_fact = facts.get(ad_lord) or fact(chart, ad_lord)
        ps, pe = _to_date(ad["start"]), _to_date(ad["end"])
        areas = _life_areas(md_fact, ad_fact)
        quality = _quality_for(md_fact, ad_fact)
        confidence = DIGNITY_CONFIDENCE.get(ad_fact.dignity, "MEDIUM")
        triggers = _event_triggers(chart, md_fact, ad_fact)
        head = _headline(md_fact, ad_fact, triggers)
        out.append(DasaPrediction(
            period_start=ps, period_end=pe,
            md_lord=md_lord, ad_lord=ad_lord,
            age_start=_age(chart.birth_dt, ps),
            age_end=_age(chart.birth_dt, pe),
            life_areas=areas,
            headline=head,
            detail=_detail(md_fact, ad_fact),
            confidence=confidence,
            quality=quality,
            triggers_event=triggers,
            citations=[Citation(book="BPHS Ch.46 (Vimshottari)"),
                       Citation(book="Phaladeepika Ch.18")],
            is_current=ps <= today <= pe,
            is_past=pe < today,
            is_future=ps > today,
        ))
    return out


# ─── Filtered views ───────────────────────────────────────────────────────

def upcoming(chart, *, n: int = 6, today: dt.date | None = None) -> list[DasaPrediction]:
    today = today or dt.date.today()
    tl = build_timeline(chart, today=today)
    fut = [d for d in tl if d.period_end >= today]
    return fut[:n]


def find_window(chart, event_keyword: str,
                today: dt.date | None = None) -> list[DasaPrediction]:
    """Return all ADs whose triggers_event contains the keyword (e.g. 'marriage')."""
    return [d for d in build_timeline(chart, today=today)
            if event_keyword.lower() in d.triggers_event.lower()]


def find_for_date(chart, when: dt.date) -> DasaPrediction | None:
    """Which DasaPrediction covers a given calendar date."""
    for d in build_timeline(chart):
        if d.period_start <= when <= d.period_end:
            return d
    return None
