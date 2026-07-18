"""
Client-facing report generator.

Builds a narrative-first markdown reading using `engine.narrative` —
plain second-person prose, no codes, no severity tags inline,
no jargon. Technical citations live in collapsed footnotes.

Pipeline:
    chart → reading sections → narrative.* → markdown → HTML+CSS → PDF
"""
from __future__ import annotations

from datetime import datetime

from engine.narrative import (
    affliction_narrative, blessing_narrative, forecast_narrative,
    planet_in_house_intro, house_strength_remark, opening_salutation,
    closing_blessing, _ord, PLANET_DOMAINS, HOUSE_DOMAINS,
)


# ─── Section builders ─────────────────────────────────────────────────────
def _cover_mandala_svg() -> str:
    """A minimal Vedic-style mandala/yantra rendered as inline SVG."""
    return (
        "<svg width='220' height='220' viewBox='0 0 220 220' "
        "xmlns='http://www.w3.org/2000/svg' style='display:block;margin:0 auto;'>"
        "<defs>"
        "<radialGradient id='g1' cx='50%' cy='50%' r='50%'>"
        "<stop offset='0%' stop-color='#d4831f' stop-opacity='0.30'/>"
        "<stop offset='80%' stop-color='#2a1e5c' stop-opacity='0.10'/>"
        "<stop offset='100%' stop-color='#fdf8ed' stop-opacity='0'/>"
        "</radialGradient>"
        "</defs>"
        "<circle cx='110' cy='110' r='105' fill='url(#g1)'/>"
        # outer 12-petal lotus
        + "".join(
            f"<path d='M 110 110 L "
            f"{110+85*1*round(0,2)} {110+85*0} Z' "
            "stroke='#b08d57' stroke-width='0.5' fill='none'/>"
            for i in range(0)
        )
        # ring of 12 petals
        + "<g stroke='#b08d57' stroke-width='0.8' fill='none'>"
        + "".join(
            f"<path d='M 110 110 m 0 -85 a 22 28 0 0 1 0 56 a 22 28 0 0 1 0 -56' "
            f"transform='rotate({i*30} 110 110)' />"
            for i in range(12)
        )
        + "</g>"
        # inner star
        + "<polygon points='110,40 130,100 190,100 142,135 160,195 110,160 60,195 78,135 30,100 90,100' "
        "stroke='#2a1e5c' stroke-width='1.2' fill='none' opacity='0.9'/>"
        # central bindu
        "<circle cx='110' cy='110' r='6' fill='#d4831f'/>"
        "<circle cx='110' cy='110' r='14' stroke='#2a1e5c' stroke-width='1.2' fill='none'/>"
        "<circle cx='110' cy='110' r='35' stroke='#7a1f3d' stroke-width='0.8' fill='none'/>"
        "<circle cx='110' cy='110' r='105' stroke='#2a1e5c' stroke-width='1.5' fill='none'/>"
        "</svg>"
    )


def _section_cover(chart) -> str:
    name = getattr(chart, "name", None) or "Friend"
    today = datetime.now().strftime("%d %B %Y")
    return (
        f"<div class='cover'>\n"
        f"<div class='cover-mandala'>{_cover_mandala_svg()}</div>\n"
        f"<div class='cover-title'>Vedic Chart Reading</div>\n"
        f"<div class='cover-name'>for {name}</div>\n"
        f"<div class='cover-divider'>✦ ❖ ✦</div>\n"
        f"<div class='cover-meta'>Prepared {today}</div>\n"
        f"<div class='cover-engine'>Engine v1.5 — 72-trait deep · truth-only · classically cited</div>\n"
        f"</div>\n\n"
    )


def _section_birth_facts(chart) -> str:
    out = ["## ✦ Your Birth Imprint\n"]
    out.append(opening_salutation(getattr(chart, "name", None)))
    out.append("")
    lagna_sign = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn",
                  "Aquarius", "Pisces"][int(chart.lagna_lon // 30)]
    out.append("### Your three pillars")
    out.append(f"- **Ascendant (Lagna):** {lagna_sign}")
    moon_sign = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn",
                 "Aquarius", "Pisces"][int(chart.positions["Moon"] // 30)]
    out.append(f"- **Moon sign (Janma rasi):** {moon_sign}")
    sun_sign = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                "Libra", "Scorpio", "Sagittarius", "Capricorn",
                "Aquarius", "Pisces"][int(chart.positions["Sun"] // 30)]
    out.append(f"- **Sun sign:** {sun_sign}")
    nak = getattr(chart, "janma_nakshatra", None)
    if nak:
        out.append(f"- **Birth nakshatra:** {nak}")
    out.append("")
    return "\n".join(out)


def _section_personality(chart) -> str:
    """Narrative personality reading: Lagna sign + Lagna lord."""
    out = ["## ✦ Who You Are (the personality your chart shapes)\n"]
    lagna_sign = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn",
                  "Aquarius", "Pisces"][int(chart.lagna_lon // 30)]

    sign_temperament = {
        "Aries":      "fiery, direct, courageous, quick to act, slow to forgive being underestimated",
        "Taurus":     "steady, sensual, patient, attached to comfort and built reality",
        "Gemini":     "quick-minded, communicative, restless, multi-skilled",
        "Cancer":     "emotional, nurturing, deeply attached to home and memory",
        "Leo":        "regal, generous, dignified, in need of being seen for what you give",
        "Virgo":      "analytical, careful, service-oriented, with high inner standards",
        "Libra":      "diplomatic, aesthetic, partnership-driven, allergic to crudeness",
        "Scorpio":    "intense, secretive, transformational, fearless under the surface",
        "Sagittarius": "philosophical, ethical, expansive, hungry for meaning more than things",
        "Capricorn":  "ambitious, disciplined, slow-burn — you build the structure others stand on",
        "Aquarius":   "principled, unconventional, networked, future-leaning",
        "Pisces":     "compassionate, dreamy, spiritually attuned, porous to others' feelings",
    }
    out.append(
        f"Your Lagna is **{lagna_sign}** — this is the lens through which "
        f"the world meets you. You are {sign_temperament.get(lagna_sign, 'distinctive')}. "
        "It is not the whole of you, but it is the room your soul walks into first."
    )
    out.append("")

    # Strongest planets quick narrative
    bs = getattr(chart, "bala_summary", {})
    if bs.get("strongest"):
        ps = ", ".join(bs["strongest"][:3])
        out.append(
            f"**The planets that carry your chart** are {ps}. "
            "These are the channels life uses to reward your effort. "
            "Lean into the domains they govern."
        )
    if bs.get("weakest"):
        pw = ", ".join(bs["weakest"][:3])
        out.append(
            f"**The planets that need your support** are {pw}. "
            "These are the domains where you'll feel resistance, delay, or "
            "disappointment unless you actively strengthen them through "
            "practice, discipline, and the remedies given later in this report."
        )
    out.append("")
    return "\n".join(out)


def _section_difficulties(chart) -> str:
    """Client-facing affliction narrative — paragraphs, not bullets."""
    from engine.afflictions import detect_all
    afflictions = detect_all(chart)
    out = ["## ✦ The Difficulties Your Chart Carries\n"]
    if not afflictions:
        out.append(
            "Your chart shows no major classical difficulty signatures. "
            "This does not mean a frictionless life — it means the friction "
            "you do face is not amplified by the standard Vedic *rin* or "
            "*dosha* patterns. Use that as a head-start."
        )
        return "\n".join(out)

    out.append(
        f"Your chart shows **{len(afflictions)} classical patterns of "
        "difficulty**. Read these calmly: in Vedic astrology these are "
        "*indications, not verdicts*. Every one of them has a remedy in "
        "the texts and a workable response in modern life. The point of "
        "naming them is so you know where to put your attention — not to "
        "burden you. Remember the Vedic rule: **the chart shows the field, "
        "your effort plays the game.**"
    )
    out.append("")

    # Group by severity
    order = ["CRITICAL", "HIGH", "MODERATE", "LOW"]
    grouped: dict = {k: [] for k in order}
    for a in afflictions:
        grouped.setdefault(a.severity, []).append(a)

    for sev in order:
        if not grouped[sev]:
            continue
        sev_label = {"CRITICAL": "Patterns asking for steady attention",
                     "HIGH":     "Patterns worth your focused awareness",
                     "MODERATE": "Patterns to be mindful of",
                     "LOW":      "Minor notes"}[sev]
        out.append(f"### {sev_label}")
        out.append("")
        for a in grouped[sev]:
            planets = list(getattr(a, "affected", []))
            paragraph = affliction_narrative(
                code=a.code, name=a.name, severity=a.severity,
                description=a.description, evidence=a.evidence,
                source=a.classical_source, planets=planets,
            )
            out.append(paragraph)
            out.append("")
    return "\n".join(out)


def _section_strengths(chart) -> str:
    from engine.blessings import detect_all as detect_all_blessings
    from engine.yogas_extended import detect_all_extended
    blessings = detect_all_blessings(chart)
    extended = [y for y in detect_all_extended(chart, gender=None)
                if y.valence == "GOOD"]

    out = ["## ✦ The Strengths Your Chart Gives You\n"]
    total = len(blessings) + len(extended)
    if total == 0:
        out.append(
            "Your chart shows few standard blessing yogas — your gifts are "
            "earned rather than inherited. The engine still finds traction "
            "for you in the planets and houses listed in your strengths section."
        )
        return "\n".join(out)
    out.append(
        f"The engine has surfaced **{total} classical blessing signatures** in "
        "your chart. Use them. They are the doors that open with less "
        "resistance, the channels through which life rewards your effort."
    )
    out.append("")

    rank = {"SUPREME": 0, "STRONG": 1, "MODERATE": 2, "LATENT": 3}
    sorted_b = sorted(blessings, key=lambda b: rank.get(b.strength, 4))
    sorted_e = sorted(extended, key=lambda b: rank.get(b.strength, 4))

    if any(b.strength == "SUPREME" for b in sorted_b + sorted_e):
        out.append("### ⭐ Supreme blessings (rare top-tier yogas)")
        out.append("")
        for b in sorted_b + sorted_e:
            if b.strength == "SUPREME":
                out.append(blessing_narrative(
                    name=b.name, strength=b.strength,
                    description=b.description,
                    evidence=getattr(b, "evidence", ""),
                    source=getattr(b, "classical_source", ""),
                    activation=getattr(b, "activation_or_remedy", ""),
                ))
                out.append("")

    if any(b.strength == "STRONG" for b in sorted_b + sorted_e):
        out.append("### ✨ Strong blessings")
        out.append("")
        for b in sorted_b + sorted_e:
            if b.strength == "STRONG":
                out.append(blessing_narrative(
                    name=b.name, strength=b.strength,
                    description=b.description,
                    evidence=getattr(b, "evidence", ""),
                    source=getattr(b, "classical_source", ""),
                    activation=getattr(b, "activation_or_remedy", ""),
                ))
                out.append("")

    if any(b.strength in ("MODERATE", "LATENT") for b in sorted_b + sorted_e):
        out.append("### Notable blessings")
        out.append("")
        for b in sorted_b + sorted_e:
            if b.strength in ("MODERATE", "LATENT"):
                out.append(blessing_narrative(
                    name=b.name, strength=b.strength,
                    description=b.description,
                    evidence=getattr(b, "evidence", ""),
                    source=getattr(b, "classical_source", ""),
                    activation=getattr(b, "activation_or_remedy", ""),
                ))
                out.append("")
    return "\n".join(out)


def _section_period(chart) -> str:
    """Current dasha period — narrative with calibrated forecasts."""
    out = ["## ✦ The Period You Are Living In\n"]
    md = getattr(chart, "current_md", None)
    ad = getattr(chart, "current_ad", None)
    if not md:
        out.append("Dasha schedule not computed for this chart.")
        return "\n".join(out)
    out.append(
        f"You are currently running the **{md} mahadasha**, with "
        f"**{ad} antardasha** as the sub-period. This is the lens through "
        "which the next several years will be filtered."
    )
    out.append("")

    # Calibrated forecast narrative
    try:
        from engine.calibration import calibrated_forecasts
        fc = calibrated_forecasts(chart)
        if fc:
            out.append("### What this period leans toward")
            out.append("")
            high = [f for f in fc if f.get("band") == "HIGH"]
            med = [f for f in fc if f.get("band") == "MEDIUM"]
            low = [f for f in fc if f.get("band") == "LOW"]
            for f in high + med:
                out.append("- " + forecast_narrative(
                    event=f["event"], posterior=f["posterior"],
                    lr=f["LR"], band=f["band"]))
            if low:
                out.append("")
                out.append("### What this period does NOT favour")
                out.append("")
                for f in low:
                    if f["LR"] < 0.85:
                        out.append("- " + forecast_narrative(
                            event=f["event"], posterior=f["posterior"],
                            lr=f["LR"], band=f["band"]))
            out.append("")
    except Exception:
        pass

    # Dasha schedule with ages
    birth_year = None
    try:
        bd = getattr(chart, "birth_datetime", None)
        if bd:
            birth_year = bd.year
    except Exception:
        pass
    if hasattr(chart, "vimshottari_schedule"):
        out.append("### Your remaining mahadashas")
        out.append("")
        out.append("| From age | To age | Mahadasha | Theme |")
        out.append("|---:|---:|---|---|")
        for entry in chart.vimshottari_schedule[:7]:
            md_name = entry.get("planet") or entry.get("md")
            start_y = entry.get("start_year") or entry.get("start").year
            end_y = entry.get("end_year") or entry.get("end").year
            if birth_year:
                age_a = start_y - birth_year
                age_b = end_y - birth_year
            else:
                age_a, age_b = "—", "—"
            theme = PLANET_DOMAINS.get(md_name, "")
            theme_short = theme.split(",")[0]
            out.append(f"| {age_a} | {age_b} | **{md_name}** | {theme_short} |")
        out.append("")
    return "\n".join(out)


def _section_planets_table(chart) -> str:
    """Plain-English remark per house — like commercial reports."""
    out = ["## ✦ House by House (your life's twelve domains)\n"]
    out.append(
        "Each row below is one of the twelve houses of your chart, the "
        "domain it rules, and a plain-English remark on its strength."
    )
    out.append("")
    out.append("| House | Domain | Remark |")
    out.append("|---:|---|:---|")
    bb = {}
    if hasattr(chart, "bhava_bala") and isinstance(chart.bhava_bala, dict):
        bb = chart.bhava_bala
    for h in range(1, 13):
        score = bb.get(h, bb.get(str(h), 0))
        try:
            remark = house_strength_remark(float(score)) if score else "—"
        except (TypeError, ValueError):
            remark = "—"
        domain = HOUSE_DOMAINS[h].split(",")[0]
        out.append(f"| {_ord(h)} | {domain} | **{remark}** |")
    out.append("")
    return "\n".join(out)


def _section_remedies(chart) -> str:
    """Verbatim remedies wrapped in narrative."""
    out = ["## ✦ What the Texts Recommend (your remedies)\n"]
    out.append(
        "Below are the remedies the classical texts prescribe for each "
        "difficulty in your chart. Each remedy is quoted *verbatim* from "
        "its source — Bhrigu Samhita, Phaladeepika, Lal Kitab, Muhurtha "
        "Chintamani — so you can verify it independently."
    )
    out.append("")
    try:
        from engine.remedies import remedies_for_chart
        from engine.remedies_verbatim import remedies_for_affliction_code
        plan = remedies_for_chart(chart)
        for entry in plan["afflictions_with_remedies"][:8]:
            a = entry["affliction"]
            out.append(f"**For:** {a['name'].split('—')[0].strip()}")
            affected = a.get("affected") or []
            planet_names = {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                            "Venus", "Saturn", "Rahu", "Ketu"}
            planets = [x for x in affected if x in planet_names]
            verbatim = remedies_for_affliction_code(a["code"], planets)
            if verbatim:
                for vr in verbatim[:2]:
                    txt = vr.text.replace("\n", " ").strip()
                    if len(txt) > 240:
                        txt = txt[:237] + "…"
                    out.append(f"  > *{vr.cite()}:* {txt}")
            else:
                # Fallback to engine.remedies actions
                for r in entry["remedies"][:3]:
                    out.append(f"  - {r['type']}: {r['action']}")
            out.append("")
    except Exception as e:
        out.append(f"_(remedy section error: {e})_")
    return "\n".join(out)


def _section_career(chart) -> str:
    out = ["## ✦ Career & Public Role"]
    sun_h = ((int(chart.positions["Sun"] // 30) - int(chart.lagna_lon // 30)) % 12) + 1
    sat_h = ((int(chart.positions["Saturn"] // 30) - int(chart.lagna_lon // 30)) % 12) + 1
    out.append("")
    out.append(
        f"Your Sun (the karaka of authority) sits in your **{_ord(sun_h)} house** — "
        f"the house of {HOUSE_DOMAINS[sun_h].split(',')[0]}. "
        f"Saturn (the karaka of professional discipline) sits in your **{_ord(sat_h)} house**. "
        "Together these two anchor where your public role wants to express."
    )
    out.append("")
    return "\n".join(out)


def _section_marriage(chart) -> str:
    out = ["## ✦ Marriage & Partnership"]
    ven_h = ((int(chart.positions["Venus"] // 30) - int(chart.lagna_lon // 30)) % 12) + 1
    out.append("")
    out.append(
        f"Venus (the karaka of marriage) sits in your **{_ord(ven_h)} house**. "
        "This shapes how relationships feel and where they are most likely to flourish "
        "or face friction. The 7th house and its lord, plus the navamsa (D9), give the "
        "fuller picture covered in the divisional charts further on."
    )
    out.append("")
    return "\n".join(out)


def _section_bhrigu_full(chart) -> str:
    """Full Bhrigu Nadi planet-by-planet narrative."""
    from engine.bhrigu_predictions import predictions_for_chart
    rows = predictions_for_chart(chart, max_per_planet=3)
    out = ["## ✦ Bhrigu Nadi — verbatim point predictions\n"]
    if not rows:
        out.append("_No Bhrigu Samhita rules matched this chart's placements._")
        return "\n".join(out)
    out.append(
        "Bhrigu Nadi is the oldest layer of point-prediction astrology. "
        "Each verse below is a *direct quote* from Bhrigu Samhita for the "
        "exact (planet, house) cell your chart places these planets in. "
        "These are not paraphrases."
    )
    out.append("")
    for row in rows:
        out.append(planet_in_house_intro(row["planet"], row["house"]))
        out.append("")
        for pred in row["predictions"]:
            txt = pred["text"].replace("\n", " ").strip()
            out.append(f"> *{pred['citation']}:* {txt}")
            out.append("")
    return "\n".join(out)


def _section_kp_full(chart) -> str:
    """Full KP house-by-house verbatim prediction layer."""
    from engine.kp_predictions import predictions_for_chart
    rows = predictions_for_chart(chart, max_per_house=2)
    out = ["## ✦ KP (Krishnamurti Paddhati) — house-by-house\n"]
    if not rows:
        out.append("_No KP rules matched._")
        return "\n".join(out)
    out.append(
        "KP astrology reads each cusp through its sub-lord. The verses "
        "below are quoted verbatim from K. S. Krishnamurti's *Reader 3 "
        "Predictive Stellar Astrology* for the matching house-themes in "
        "your chart."
    )
    out.append("")
    for row in rows:
        sl = f" · sub-lord: **{row['sub_lord']}**" if row.get("sub_lord") else ""
        out.append(f"### {_ord(row['house'])} house — {HOUSE_DOMAINS[row['house']].split(',')[0]}{sl}")
        out.append("")
        for pred in row["predictions"]:
            txt = pred["text"].replace("\n", " ").strip()
            if len(txt) > 320:
                txt = txt[:317] + "…"
            out.append(f"> *{pred['citation']}:* {txt}")
            out.append("")
    return "\n".join(out)


def _section_vargas_full(chart) -> str:
    """Divisional charts with explanation."""
    out = ["## ✦ Divisional Charts (the deeper lenses)\n"]
    out.append(
        "The classical texts split your birth chart into sub-charts, each "
        "magnifying a specific theme. The most important are:\n\n"
        "- **D9 (Navamsa)** — your spouse, your dharma, the latent strength "
        "of every planet.\n"
        "- **D10 (Dasamsa)** — your career, public role, the work life will "
        "ask of you.\n"
        "- **D24 (Chaturvimshamsa)** — your education, learning capacity.\n"
        "- **D60 (Shashtiamsa)** — past-life karma, the finest-grained "
        "reading the texts allow."
    )
    out.append("")
    vargas = getattr(chart, "vargas", None) or {}
    for div_name, label in (("D9", "Navamsa — spouse / dharma"),
                              ("D10", "Dasamsa — career / public"),
                              ("D24", "Chaturvimshamsa — education"),
                              ("D60", "Shashtiamsa — past-life karma")):
        d = vargas.get(div_name) or {}
        if not d:
            continue
        out.append(f"### {label}")
        out.append("")
        out.append("| Planet | Sign in " + div_name + " |")
        out.append("|---|---|")
        for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                  "Saturn", "Rahu", "Ketu"):
            sign = d.get(p) or "—"
            out.append(f"| {p} | {sign} |")
        out.append("")
    if hasattr(chart, "vargottama") and chart.vargottama:
        out.append(
            f"**Vargottama planets** (planets that hold the same sign in "
            f"D1 and D9 — extra strong): **{', '.join(chart.vargottama)}**"
        )
    elif hasattr(chart, "vargottama"):
        out.append(
            "*No vargottama planets — your D1 strengths do not double in D9.*"
        )
    out.append("")
    return "\n".join(out)


def _section_classical_appendix(chart) -> str:
    """Tucked at the end: the rule-matched canonical sources for each
    section, for the reader who wants to cross-check."""
    out = ["## ✦ Classical Sources (appendix)\n"]
    out.append(
        "*This appendix lists the matched canonical rules behind your "
        "reading, with their book and authority weight. Most readers can "
        "skip this section — it exists for those who want to verify each "
        "claim against the source.*"
    )
    out.append("")
    try:
        from engine.reading import _section_lagna, _section_career, _section_marriage
        for builder, label in ((_section_lagna, "Lagna / Personality"),
                                (_section_career, "Career"),
                                (_section_marriage, "Marriage")):
            sec = builder(chart)
            mr = getattr(sec, "matched_rules", None) or []
            if not mr:
                continue
            out.append(f"### {label}")
            out.append("")
            for r in mr[:8]:
                strength = getattr(r, "strength", "—")
                rule = getattr(r, "rule", None)
                if isinstance(rule, dict):
                    rule_txt = rule.get("rule_text") or rule.get("text") or rule.get("name") or "?"
                    book = (rule.get("schools") or [rule.get("school", "?")])[0]
                else:
                    rule_txt, book = str(rule), "?"
                out.append(f"- *[{strength}]* {str(rule_txt)[:200]} *(from {book})*")
            out.append("")
    except Exception as e:
        out.append(f"_appendix error: {e}_")
    return "\n".join(out)


def _section_closing(chart) -> str:
    return closing_blessing()


# ─── Public API ───────────────────────────────────────────────────────────
def _section_timeline(chart) -> str:
    from engine.timeline import render_timeline_markdown
    return render_timeline_markdown(chart)


def _section_timeline_deep(chart) -> str:
    from engine.timeline_deep import render_deep_timeline_markdown
    return render_deep_timeline_markdown(chart)


def _section_life_domains(chart) -> str:
    from engine.life_domains import render_life_domains_markdown
    return render_life_domains_markdown(chart)


def _section_education(chart) -> str:
    from engine.education import render_education_markdown
    return render_education_markdown(chart)


def _section_accident(chart) -> str:
    from engine.accident import render_accident_markdown
    return render_accident_markdown(chart)


def _section_cross_validate(chart) -> str:
    from engine.cross_validate import render_cross_validation_markdown
    return render_cross_validation_markdown(chart)


def _section_72_traits(chart) -> str:
    from engine.traits_72 import render_72_traits_markdown
    return render_72_traits_markdown(chart)


def generate_client_report(chart) -> str:
    sections = [
        _section_cover(chart),
        _section_birth_facts(chart),
        _section_personality(chart),
        _section_72_traits(chart),
        _section_timeline(chart),
        _section_timeline_deep(chart),
        _section_life_domains(chart),
        _section_education(chart),
        _section_accident(chart),
        _section_difficulties(chart),
        _section_strengths(chart),
        _section_period(chart),
        _section_planets_table(chart),
        _section_career(chart),
        _section_marriage(chart),
        _section_remedies(chart),
        _section_cross_validate(chart),
        _section_vargas_full(chart),
        _section_closing(chart),
    ]
    return "\n\n".join(sections)
