"""
Chronological life-timeline narrative.

Walks through every Vimshottari mahadasha from birth onwards. For each
period, generates a narrative paragraph that combines:
    - The mahadasha lord's natural meaning
    - The lord's house placement in the chart (its life-domain)
    - The lord's sign placement (its mood)
    - Active afflictions/blessings amplified or muted in this period
    - Whether this was past, present, or future at report time
    - The age band (age-X to age-Y)

The resulting "Life Timeline" section makes the client feel:
    "Yes — between ages 7 and 16 our family DID go through that.
     This engine is reading me correctly."

That is the trust-anchor: when past hits true, the future predictions
become believable. Truth-without-panic is preserved.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass

from engine.narrative import (
    PLANET_DOMAINS, HOUSE_DOMAINS, _ord,
)


@dataclass
class TimelineEntry:
    md_lord: str
    start: dt.datetime
    end: dt.datetime
    age_start: int
    age_end: int
    house: int
    sign: str
    relationship: str   # "past" | "present" | "future"
    paragraph: str


PLANET_BORN_INTO = {
    "Sun":     "the period of self-emergence — your sense of self crystallises",
    "Moon":    "the period of emotional-mind formation — sensitivity, attachment, mother dominate",
    "Mars":    "the period of force and friction — courage, accidents, sibling-energy intensify",
    "Mercury": "the period of speech, study and intellect — schooling, friendships, ideas form",
    "Jupiter": "the period of expansion, learning and grace — teachers, dharma, optimism",
    "Venus":   "the period of pleasure, beauty and partnership — relationships, comforts, art",
    "Saturn":  "the period of structure, work and limit — slow burn, discipline, real responsibility",
    "Rahu":    "the period of unconventional pull — foreign matters, ambition, hunger to break out",
    "Ketu":    "the period of detachment and inwardness — endings, spiritual reorientation",
}

PLANET_THEME_SHORT = {
    "Sun":     "self & authority",
    "Moon":    "mind & emotion",
    "Mars":    "courage & friction",
    "Mercury": "intellect & speech",
    "Jupiter": "wisdom & grace",
    "Venus":   "love & comfort",
    "Saturn":  "discipline & duty",
    "Rahu":    "ambition & change",
    "Ketu":    "detachment & spirit",
}


def _classify(now: dt.datetime, start: dt.datetime, end: dt.datetime) -> str:
    if end < now:
        return "past"
    if start > now:
        return "future"
    return "present"


def _planet_house(chart, planet: str) -> int:
    lon = chart.positions.get(planet)
    if lon is None:
        return 0
    lagna_sign = int(chart.lagna_lon // 30)
    return ((int(lon // 30) - lagna_sign) % 12) + 1


def _planet_sign(chart, planet: str) -> str:
    lon = chart.positions.get(planet)
    if lon is None:
        return ""
    SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    return SIGNS[int(lon // 30)]


def _phrase_past(planet: str, house: int, age_a: int, age_b: int) -> str:
    domain = HOUSE_DOMAINS[house].split(",")[0]
    return (
        f"From age **{age_a} to {age_b}** you were running the **{planet} "
        f"mahadasha**. {planet} sits in your {_ord(house)} house — the "
        f"house of {domain}. So this was **the period your life used "
        f"{domain} as the main classroom**: "
    )


def _phrase_present(planet: str, house: int, age_a: int, age_b: int) -> str:
    domain = HOUSE_DOMAINS[house].split(",")[0]
    return (
        f"**Right now (age {age_a} to {age_b})** you are in the **{planet} "
        f"mahadasha**. Because {planet} sits in your {_ord(house)} house "
        f"({domain}), this period asks you to engage that domain consciously: "
    )


def _phrase_future(planet: str, house: int, age_a: int, age_b: int) -> str:
    domain = HOUSE_DOMAINS[house].split(",")[0]
    return (
        f"**From age {age_a} to {age_b}** you will enter the **{planet} "
        f"mahadasha**. Because {planet} sits in your {_ord(house)} house "
        f"({domain}), expect this period to bring "
        f"{domain}-themed openings, decisions, and lessons: "
    )


def _affliction_modifier(chart, planet: str) -> str:
    """If this MD-lord is involved in known afflictions, add a softer note."""
    try:
        from engine.afflictions import detect_all
        afflictions = detect_all(chart)
        relevant = [a for a in afflictions
                    if planet in (getattr(a, "affected", []) or [])]
        if relevant:
            names = ", ".join(a.name.split("(")[0].strip() for a in relevant[:2])
            return (
                f" Note: {planet} carries a chart-level pattern ({names}) — "
                "the dasha's themes will lean toward the harder edge of that "
                "pattern unless you actively use the remedies given earlier."
            )
    except Exception:
        pass
    return ""


def _blessing_modifier(chart, planet: str) -> str:
    try:
        from engine.blessings import detect_all
        blessings = detect_all(chart)
        relevant = [b for b in blessings
                    if planet.lower() in (b.name + " " + str(getattr(b, "evidence", ""))).lower()]
        if relevant:
            names = ", ".join(b.name.split("(")[0].strip() for b in relevant[:2])
            return (
                f" The good news: {planet} is also lifted by {names} in your "
                "chart — the dasha's reward potential is real if you act."
            )
    except Exception:
        pass
    return ""


def build_timeline(chart, today: dt.datetime | None = None
                   ) -> list[TimelineEntry]:
    """Build the timeline for the entire Vimshottari schedule (~120 yrs)."""
    today = today or dt.datetime.now()
    birth = chart.birth_dt
    entries = []
    if not getattr(chart, "vimshottari_periods", None):
        return entries

    for md in chart.vimshottari_periods:
        planet = md.lord
        start = md.start
        end = md.end
        age_a = max(0, (start - birth).days // 365)
        age_b = (end - birth).days // 365
        rel = _classify(today, start, end)
        h = _planet_house(chart, planet)
        s = _planet_sign(chart, planet)

        if rel == "past":
            opener = _phrase_past(planet, h, age_a, age_b)
        elif rel == "present":
            opener = _phrase_present(planet, h, age_a, age_b)
        else:
            opener = _phrase_future(planet, h, age_a, age_b)

        body = PLANET_BORN_INTO.get(planet, "")
        sign_clause = (
            f" In sign {s}, the energy expressed with {_sign_mood(s)}." if s else ""
        )
        modifier = _affliction_modifier(chart, planet) + _blessing_modifier(chart, planet)

        para = opener + body + "." + sign_clause + modifier
        entries.append(TimelineEntry(
            md_lord=planet, start=start, end=end,
            age_start=age_a, age_end=age_b,
            house=h, sign=s, relationship=rel, paragraph=para,
        ))
    return entries


SIGN_MOOD = {
    "Aries":      "fast, hot, decisive flavour",
    "Taurus":     "patient, sensual, materialistic flavour",
    "Gemini":     "verbal, mobile, multi-tasked flavour",
    "Cancer":     "emotional, family-anchored flavour",
    "Leo":        "proud, public, dignified flavour",
    "Virgo":      "analytical, service-oriented, perfectionist flavour",
    "Libra":      "diplomatic, relationship-driven flavour",
    "Scorpio":    "intense, transformational, secretive flavour",
    "Sagittarius": "philosophical, hopeful, expansive flavour",
    "Capricorn":  "ambitious, slow-burn, structured flavour",
    "Aquarius":   "unconventional, networked, principled flavour",
    "Pisces":     "compassionate, dreamy, spiritually porous flavour",
}


def _sign_mood(sign: str) -> str:
    return SIGN_MOOD.get(sign, "its own colouring")


def render_timeline_markdown(chart) -> str:
    out = ["## ✦ The Story Your Chart Has Been Telling (timeline)\n"]
    out.append(
        "Below is your life decade by decade — each period framed by the "
        "Vimshottari mahadasha that shaped it. **Past periods are "
        "described in past tense — read them and check whether they "
        "match your memory of those years.** When they do, you can trust "
        "the same engine for what it says about the future."
    )
    out.append("")
    entries = build_timeline(chart)
    if not entries:
        out.append("_Vimshottari schedule unavailable for this chart._")
        return "\n".join(out)

    # Group: past, present, future
    past = [e for e in entries if e.relationship == "past"]
    present = [e for e in entries if e.relationship == "present"]
    future = [e for e in entries if e.relationship == "future"]

    if past:
        out.append("### Your past — what your chart said would happen")
        out.append("")
        for e in past:
            yr_a = e.start.year
            yr_b = e.end.year
            out.append(
                f"**Age {e.age_start}–{e.age_end} ({yr_a}–{yr_b}) · "
                f"{e.md_lord} mahadasha — {PLANET_THEME_SHORT.get(e.md_lord,'')}**"
            )
            out.append("")
            out.append(e.paragraph)
            out.append("")

    if present:
        out.append("### Your present — what is happening now")
        out.append("")
        for e in present:
            yr_a = e.start.year
            yr_b = e.end.year
            out.append(
                f"**Age {e.age_start}–{e.age_end} ({yr_a}–{yr_b}) · "
                f"{e.md_lord} mahadasha — {PLANET_THEME_SHORT.get(e.md_lord,'')}**"
            )
            out.append("")
            out.append(e.paragraph)
            out.append("")

    if future:
        out.append("### Your future — what your chart is preparing")
        out.append("")
        for e in future[:5]:
            yr_a = e.start.year
            yr_b = e.end.year
            out.append(
                f"**Age {e.age_start}–{e.age_end} ({yr_a}–{yr_b}) · "
                f"{e.md_lord} mahadasha — {PLANET_THEME_SHORT.get(e.md_lord,'')}**"
            )
            out.append("")
            out.append(e.paragraph)
            out.append("")

    out.append(
        "*If the past entries above feel accurate, that is the engine's "
        "pulse-check: this same chart that read your past correctly is "
        "the one reading your future. Not a guarantee — but a "
        "calibration. Trust accordingly.*"
    )
    return "\n".join(out)
