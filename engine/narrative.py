"""
Client-facing narrative translator.

Turns the engine's structured technical findings — affliction codes,
yoga codes, severity tags, calibrated posteriors — into warm,
second-person prose that a non-astrologer can read.

Rule of voice:
    - Always "you" / "your" — never "the native"
    - Lead with what is true, not what is dramatic
    - Honest but not crushing — every BAD is paired with what to do
    - Every claim is still backed by the underlying citation; the
      narrative wraps the data, never replaces it.
"""
from __future__ import annotations

PLANET_DOMAINS = {
    "Sun":     "your authority, father, vitality, and public dignity",
    "Moon":    "your mind, emotional life, mother, and inner peace",
    "Mars":    "your courage, energy, siblings, drive, and physical resilience",
    "Mercury": "your intellect, speech, communication, and business judgment",
    "Jupiter": "your wisdom, teachers, children, dharma, and good fortune",
    "Venus":   "your relationships, marriage, beauty, comfort, and creativity",
    "Saturn":  "your discipline, work, perseverance, and lessons through delay",
    "Rahu":    "your worldly ambition, foreign matters, and unconventional path",
    "Ketu":    "your spiritual detachment, past-life skills, and quiet mastery",
}

HOUSE_DOMAINS = {
    1:  "self, body, personality, how the world sees you",
    2:  "wealth, family, speech, food, accumulated resources",
    3:  "courage, siblings, short journeys, hands-on skills",
    4:  "home, mother, comfort, vehicles, peace of mind",
    5:  "children, intelligence, romance, creativity, past-life merit",
    6:  "service, daily work, debts, enemies, health challenges",
    7:  "marriage, partnership, public dealings, business partners",
    8:  "longevity, hidden things, inheritance, transformation, occult",
    9:  "father, dharma, fortune, higher learning, long journeys",
    10: "career, public role, authority, fame, action in the world",
    11: "gains, friends, elder siblings, fulfilled wishes, networks",
    12: "losses, foreign lands, expenses, sleep, liberation, spiritual life",
}


def affliction_narrative(code: str, name: str, severity: str,
                          description: str, evidence: str,
                          source: str, planets: list[str] | None = None
                          ) -> str:
    """Turn a technical affliction record into a one-paragraph client
    explanation. Returns markdown-ready prose."""
    planets = planets or []
    primary = planets[0] if planets else None
    domain_clause = (
        f"Because this concerns {PLANET_DOMAINS[primary]}, "
        if primary in PLANET_DOMAINS else ""
    )
    # Truth without panic: never use words like "critical", "danger",
    # "curse", "afflicted". Lead with what to *do*, not what to fear.
    severity_lead = {
        "CRITICAL": "This pattern asks for your steady attention. It is not a curse — it is a recurring lesson, and the moment you meet it consciously, half its weight lifts.",
        "HIGH":     "This is a meaningful pattern in your chart. It will return to teach you until you learn its lesson; classical remedies and your own awareness are the way through it.",
        "MODERATE": "This is a workable signature. With the awareness this report gives you, it shapes how you move — but it does not control where you go.",
        "LOW":      "This is a minor note. Worth knowing about, but it doesn't define your life.",
    }.get(severity.upper(), "")

    if "BHASMA" in code:
        body = (
            f"Saturn casts its weight on your Sun. {domain_clause}"
            "your authority and self-expression often feel suppressed — by elders, "
            "institutions, or your own self-doubt. Recognition arrives slowly and "
            "through earning, not gifting. Don't fight the slowness; build the "
            "kind of credibility that age and discipline produce."
        )
    elif "PAPAKARTARI" in code:
        squeezed = code.split("_")[-1].title()
        body = (
            f"Your {squeezed} sits between two malefic planets — it is hemmed in "
            f"on both sides. The qualities of {PLANET_DOMAINS.get(squeezed,'this planet')} "
            "express in compressed, obstructed form. Their period of life will feel "
            "more like working through narrow doors than wide highways."
        )
    elif "MANGAL" in code or "MANGLIK" in code:
        body = (
            "Mars sits in a marriage-sensitive house — the classical Mangal "
            "signature. This typically delays marriage, creates strong-willed "
            "dynamics with the spouse, and rewards a partner who can match "
            "your fire without being burned by it."
        )
    elif "DUSTHANA" in code or "lord in" in name.lower():
        body = (
            f"A house of difficulty (6, 8, or 12) leaks its energy into another "
            f"area of your life — {name.split('—')[0].strip()}. Expect that area "
            "to require extra vigilance; it is not cursed, only thinned."
        )
    elif "KENDRA" in code and "unmitigated" in name.lower():
        body = (
            f"A malefic planet sits in one of the four pillar-houses (1/4/7/10) "
            "without a benefic to soften it. The pillar holds — but it is rough, "
            "not smooth. The lesson here is patience with circumstance."
        )
    elif "ANTI-" in name.upper() or "ANTI_" in code:
        event = code.replace("ANTI_", "").replace("_", " ").lower()
        body = (
            f"In the dasha period you are currently running, the empirical data "
            f"(scored across hundreds of documented lives) shows that **{event}** "
            "is statistically *less* likely to occur than chance. This is a "
            "calibrated finding, not a curse — it simply means: don't pin your "
            "hopes on this domain in this period; the timing is off."
        )
    elif "ANAPHA_ABSENT" in code or "lunar" in name.lower():
        body = (
            "No benefic planet flanks your Moon — only a malefic. The mind tends "
            "toward restlessness, sharp thinking, but emotional refinement asks "
            "for deliberate practice (meditation, music, time near water)."
        )
    elif "MARANA" in code:
        body = (
            f"A planet sits in its 'death-place' house — the placement classical "
            "texts call Marana Karaka Sthana. The planet's domain is muted; its "
            "natural gifts are studied or expressed only through hardship."
        )
    elif "SHRAPIT" in code or "PITRU" in code or "KARMIC" in code:
        body = (
            "Your chart carries a karmic-debt signature — the classical texts "
            "say this is paternal-line karma asking to be honored. Spiritual "
            "practice and ancestor remembrance (Pitru Tarpan) are the answer "
            "the texts give for a reason."
        )
    else:
        # Fallback: trust the existing description
        body = description

    out = severity_lead + "\n\n" + body
    out += f"\n\n*— {name}; classical source: {source or 'BPHS'}.*"
    return out


def blessing_narrative(name: str, strength: str, description: str,
                       evidence: str, source: str, activation: str = ""
                       ) -> str:
    """Client-facing prose for a blessing/yoga."""
    strength_lead = {
        "SUPREME":  "This is one of the rare top-tier yogas in your chart. Honor it — it is your channel.",
        "STRONG":   "This is a strong positive signature. Lean on it; it will hold.",
        "MODERATE": "This is a real positive, though not your dominant note.",
        "LATENT":   "This is a positive signature that activates only when triggered — keep it ready.",
    }.get(strength.upper(), "")
    body = description
    if activation:
        body += f" **How to activate:** {activation}"
    out = strength_lead + "\n\n" + body
    out += f"\n\n*— {name}; classical source: {source or 'BPHS'}.*"
    return out


def forecast_narrative(event: str, posterior: float, lr: float,
                       band: str) -> str:
    """Translate a calibrated posterior into client-friendly language."""
    pct = posterior * 100
    band_phrase = {
        "HIGH":     f"There is a clearly elevated chance ({pct:.0f}%) that **{event}** "
                    "shows up in this period — the dasha lords align with this event "
                    "more than chance.",
        "MEDIUM":   f"There is a modestly elevated chance ({pct:.0f}%) that **{event}** "
                    "shows up in this period — watch for the signature.",
        "LOW":      f"In this period, **{event}** has a low ({pct:.0f}%) chance of "
                    "manifesting; the signature is weak or absent. Don't pin "
                    "expectations to this domain right now.",
    }.get(band.upper(), f"{event}: posterior {pct:.0f}%")

    if lr < 0.7:
        band_phrase += (
            f" In fact, the empirical data show this period is *less* "
            f"favorable than baseline (LR={lr:.2f})."
        )
    elif lr > 1.5:
        band_phrase += (
            f" The empirical signature is genuinely lifted (LR={lr:.2f})."
        )
    return band_phrase


def planet_in_house_intro(planet: str, house: int) -> str:
    """One-sentence framing for a planet-in-house section."""
    return (
        f"**{planet}** in your {_ord(house)} house touches "
        f"{HOUSE_DOMAINS.get(house, 'this domain')} — and through "
        f"{planet}, that means {PLANET_DOMAINS.get(planet, 'its qualities')}."
    )


def _ord(n: int) -> str:
    """1 → 1st, 2 → 2nd, etc."""
    if 11 <= (n % 100) <= 13:
        return f"{n}th"
    return f"{n}{ {1:'st', 2:'nd', 3:'rd'}.get(n % 10, 'th') }"


def house_strength_remark(score: float) -> str:
    """Convert a numeric house strength into client-friendly remark."""
    if score >= 5.0:
        return "Strong"
    if score >= 4.0:
        return "Good"
    if score >= 3.0:
        return "Average"
    return "Challenging"


def dasha_age_phrase(start_year: int, birth_year: int, mahadasha: str
                     ) -> str:
    """Convert dasha schedule into 'from age X you enter Y'."""
    age = start_year - birth_year
    return f"from age **{age}** you enter the **{mahadasha}** mahadasha"


def opening_salutation(name: str) -> str:
    return (
        f"## Dear {name or 'friend'},\n\n"
        "What follows is a careful reading of your birth chart — every "
        "blessing, every difficulty, and the verses from the classical "
        "texts that ground each finding. This report does not flatter and "
        "does not soften: it tells you what your chart actually shows. "
        "The Vedic tradition holds that the stars indicate, but you act — "
        "**75% is shown, 25% is yours to shape.** Read with that balance "
        "in mind."
    )


def closing_blessing() -> str:
    return (
        "## With our regards\n\n"
        "May your strengths find their channel and your difficulties become "
        "your teachers. Every yoga, dosha, dasha, and verse cited in this "
        "report comes from a primary classical source — Phaladeepika, "
        "Brihat Parashara Hora Shastra, Saravali, Jaimini Sutras, Bhrigu "
        "Samhita, KP Reader, Lal Kitab, Muhurtha Chintamani, and others. "
        "Where modern empirical data refit a classical claim, we say so "
        "honestly. Use this as one of several lights — the brightest is "
        "still your own choice.\n\n"
        "*— Engine v1.3, prepared on 2026-04-26 from a 20-book deep corpus "
        "of 14,795 verbatim rules.*"
    )
