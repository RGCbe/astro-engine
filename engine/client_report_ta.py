"""
Tamil client report — uses engine.narrative_ta + Tamil signs/planets.

Same section structure as engine.client_report, voiced in தமிழ்.
"""
from __future__ import annotations

from datetime import datetime

from engine.narrative_ta import (
    affliction_narrative_ta, blessing_narrative_ta,
    opening_salutation_ta, closing_blessing_ta,
    PLANET_DOMAINS_TA, HOUSE_DOMAINS_TA, SIGN_TEMPERAMENT_TA,
    SIGNS_TA, PLANETS_TA, _ord_ta,
)
from engine.narrative import house_strength_remark


def _section_cover_ta(chart) -> str:
    from engine.client_report import _cover_mandala_svg
    name = getattr(chart, "name", None) or "நண்பர்"
    today = datetime.now().strftime("%d %B %Y")
    return (
        f"<div class='cover'>\n"
        f"<div class='cover-mandala'>{_cover_mandala_svg()}</div>\n"
        f"<div class='cover-title'>வேத ஜாதக வாசிப்பு</div>\n"
        f"<div class='cover-name'>{name} அவர்களுக்கு</div>\n"
        f"<div class='cover-divider'>✦ ❖ ✦</div>\n"
        f"<div class='cover-meta'>தயாரிக்கப்பட்டது: {today}</div>\n"
        f"<div class='cover-engine'>Engine v1.5 — 72 பண்புகள் · உண்மை மட்டும் · சாஸ்திர மேற்கோள்</div>\n"
        f"</div>\n\n"
    )


def _section_birth_facts_ta(chart) -> str:
    out = ["## ✦ உங்கள் ஜனன முத்திரை\n"]
    out.append(opening_salutation_ta(getattr(chart, "name", None)))
    out.append("")
    SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    lagna_en = SIGN_NAMES[int(chart.lagna_lon // 30)]
    moon_en = SIGN_NAMES[int(chart.positions["Moon"] // 30)]
    sun_en = SIGN_NAMES[int(chart.positions["Sun"] // 30)]
    out.append("### உங்கள் மூன்று தூண்கள்")
    out.append(f"- **லக்னம் (உதயராசி):** {SIGNS_TA[lagna_en]}")
    out.append(f"- **ஜன்ம ராசி (சந்திரராசி):** {SIGNS_TA[moon_en]}")
    out.append(f"- **சூரிய ராசி:** {SIGNS_TA[sun_en]}")
    out.append("")
    return "\n".join(out)


def _section_personality_ta(chart) -> str:
    out = ["## ✦ நீங்கள் யார் (உங்கள் ஜாதகம் வடிவமைக்கும் ஆளுமை)\n"]
    SIGN_NAMES = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    lagna_en = SIGN_NAMES[int(chart.lagna_lon // 30)]
    out.append(
        f"உங்கள் லக்னம் **{SIGNS_TA[lagna_en]}** — இதுதான் உலகம் "
        "உங்களைச் சந்திக்கும் கதவு. நீங்கள் "
        f"{SIGN_TEMPERAMENT_TA.get(lagna_en, 'தனித்துவம் வாய்ந்தவர்')}. "
        "இது உங்கள் முழு வாழ்வும் அல்ல, ஆனால் உங்கள் ஆத்மா முதலில் "
        "காலடி எடுத்து வைக்கும் அறை."
    )
    out.append("")

    bs = getattr(chart, "bala_summary", {})
    if bs.get("strongest"):
        ps = ", ".join(PLANETS_TA.get(p, p) for p in bs["strongest"][:3])
        out.append(
            f"**உங்கள் ஜாதகத்தைச் சுமக்கும் கிரகங்கள்** {ps}. "
            "இவைதான் உங்கள் முயற்சிக்கு பலனளிக்கும் வழிகள். "
            "இவற்றின் ஆட்சிப் பகுதிகளில் ஆழமாக ஈடுபடுங்கள்."
        )
    if bs.get("weakest"):
        pw = ", ".join(PLANETS_TA.get(p, p) for p in bs["weakest"][:3])
        out.append(
            f"**உங்களின் ஆதரவு தேவைப்படும் கிரகங்கள்** {pw}. "
            "இந்தப் பகுதிகளில் தடைகள், தாமதங்கள் ஏற்படக்கூடும். "
            "பயிற்சி, ஒழுக்கம், மற்றும் இந்த அறிக்கையில் கொடுக்கப்பட்டுள்ள "
            "சாஸ்திர பரிகாரங்கள் மூலம் இவற்றை வலுப்படுத்துங்கள்."
        )
    out.append("")
    return "\n".join(out)


def _section_difficulties_ta(chart) -> str:
    from engine.afflictions import detect_all
    afflictions = detect_all(chart)
    out = ["## ✦ உங்கள் ஜாதகத்தில் உள்ள சவால்கள்\n"]
    if not afflictions:
        out.append(
            "உங்கள் ஜாதகத்தில் முக்கியமான கிளாசிக்கல் ரிண-தோஷ அமைப்புகள் "
            "எதுவும் இல்லை. இது உராய்வே இல்லாத வாழ்க்கை என்று அர்த்தமல்ல — "
            "ஆனால் கிடைக்கும் உராய்வு பரிச்சயமான வேத அமைப்புகளால் "
            "பெருகவில்லை. அதை ஒரு முன்னேற்றமாக எடுத்துக்கொள்ளுங்கள்."
        )
        return "\n".join(out)

    out.append(
        f"உங்கள் ஜாதகத்தில் **{len(afflictions)} கிளாசிக்கல் சவால் அமைப்புகள்** "
        "காணப்படுகின்றன. அமைதியாக வாசியுங்கள்: வேத ஜோதிடத்தில் இவை "
        "*குறிப்புகள்-தீர்ப்புகள் அல்ல*. ஒவ்வொன்றுக்கும் சாஸ்திரப் பரிகாரம் "
        "உள்ளது, நவீன வாழ்க்கையில் சமாளிக்கும் வழியும் உள்ளது. இவற்றை "
        "சொல்லும் நோக்கம் — பாரம் ஏற்றுவதற்காக அல்ல, கவனத்தை எங்கே "
        "செலுத்த வேண்டும் என்பதை நீங்கள் அறிவதற்காக. வேத விதியை நினைவில் "
        "வையுங்கள்: **ஜாதகம் களத்தைக் காட்டுகிறது, ஆட்டத்தை உங்கள் "
        "முயற்சியே ஆடுகிறது.**"
    )
    out.append("")

    order = ["CRITICAL", "HIGH", "MODERATE", "LOW"]
    grouped: dict = {k: [] for k in order}
    for a in afflictions:
        grouped.setdefault(a.severity, []).append(a)

    for sev in order:
        if not grouped[sev]:
            continue
        sev_label = {"CRITICAL": "தொடர்ந்த கவனம் கேட்கும் அமைப்புகள்",
                     "HIGH":     "ஆழ்ந்த விழிப்புணர்வு தேவைப்படும் அமைப்புகள்",
                     "MODERATE": "கவனத்தில் வைத்துக்கொள்ள வேண்டிய அமைப்புகள்",
                     "LOW":      "சிறிய குறிப்புகள்"}[sev]
        out.append(f"### {sev_label}")
        out.append("")
        for a in grouped[sev]:
            planets = list(getattr(a, "affected", []))
            paragraph = affliction_narrative_ta(
                code=a.code, name=a.name, severity=a.severity,
                description=a.description, evidence=a.evidence,
                source=a.classical_source, planets=planets,
            )
            out.append(paragraph)
            out.append("")
    return "\n".join(out)


def _section_strengths_ta(chart) -> str:
    from engine.blessings import detect_all as detect_all_blessings
    from engine.yogas_extended import detect_all_extended
    blessings = detect_all_blessings(chart)
    extended = [y for y in detect_all_extended(chart, gender=None)
                if y.valence == "GOOD"]

    out = ["## ✦ உங்கள் ஜாதகம் கொடுக்கும் பலங்கள்\n"]
    total = len(blessings) + len(extended)
    if total == 0:
        out.append(
            "உங்கள் ஜாதகத்தில் வழக்கமான ஆசீர்வாத யோகங்கள் குறைவு — "
            "உங்கள் சாதனைகள் முயற்சியால் கிடைப்பவை, பாரம்பரியமாக "
            "வரக்கூடியவை அல்ல."
        )
        return "\n".join(out)
    out.append(
        f"உங்கள் ஜாதகத்தில் **{total} கிளாசிக்கல் ஆசீர்வாத அமைப்புகள்** "
        "உள்ளன. இவற்றைப் பயன்படுத்துங்கள். "
        "இவையே குறைவான தடை கொண்ட கதவுகள், உங்கள் முயற்சிக்கு வாழ்க்கை "
        "பலனளிக்கும் வழிகள்."
    )
    out.append("")

    rank = {"SUPREME": 0, "STRONG": 1, "MODERATE": 2, "LATENT": 3}
    sorted_b = sorted(blessings, key=lambda b: rank.get(b.strength, 4))
    sorted_e = sorted(extended, key=lambda b: rank.get(b.strength, 4))
    all_b = sorted_b + sorted_e

    if any(b.strength == "SUPREME" for b in all_b):
        out.append("### ⭐ உச்ச ஆசீர்வாதங்கள் (அரிதான மேலிட யோகங்கள்)")
        out.append("")
        for b in all_b:
            if b.strength == "SUPREME":
                out.append(blessing_narrative_ta(
                    name=b.name, strength=b.strength,
                    description=b.description,
                    evidence=getattr(b, "evidence", ""),
                    source=getattr(b, "classical_source", ""),
                    activation=getattr(b, "activation_or_remedy", ""),
                ))
                out.append("")
    if any(b.strength == "STRONG" for b in all_b):
        out.append("### ✨ வலுவான ஆசீர்வாதங்கள்")
        out.append("")
        for b in all_b:
            if b.strength == "STRONG":
                out.append(blessing_narrative_ta(
                    name=b.name, strength=b.strength,
                    description=b.description,
                    evidence=getattr(b, "evidence", ""),
                    source=getattr(b, "classical_source", ""),
                    activation=getattr(b, "activation_or_remedy", ""),
                ))
                out.append("")
    if any(b.strength in ("MODERATE", "LATENT") for b in all_b):
        out.append("### குறிப்பிடத்தக்க ஆசீர்வாதங்கள்")
        out.append("")
        for b in all_b:
            if b.strength in ("MODERATE", "LATENT"):
                out.append(blessing_narrative_ta(
                    name=b.name, strength=b.strength,
                    description=b.description,
                    evidence=getattr(b, "evidence", ""),
                    source=getattr(b, "classical_source", ""),
                    activation=getattr(b, "activation_or_remedy", ""),
                ))
                out.append("")
    return "\n".join(out)


def _section_period_ta(chart) -> str:
    out = ["## ✦ நீங்கள் வாழும் காலகட்டம்\n"]
    md = getattr(chart, "current_md", None)
    ad = getattr(chart, "current_ad", None)
    if not md:
        out.append("தசை விவரம் கிடைக்கவில்லை.")
        return "\n".join(out)
    md_ta = PLANETS_TA.get(md, md)
    ad_ta = PLANETS_TA.get(ad, ad)
    out.append(
        f"தற்போது நீங்கள் ஓடும் தசை: **{md_ta} மஹாதசை**, "
        f"**{ad_ta} புக்தி** உப-காலம். "
        "வரும் சில ஆண்டுகள் இந்த வண்ணக்கண்ணாடி வழியே வடிவமைகின்றன."
    )
    out.append("")
    if hasattr(chart, "vimshottari_schedule"):
        out.append("### உங்கள் மீதமுள்ள மஹாதசைகள்")
        out.append("")
        out.append("| தசை | தொடக்கம் | முடிவு | கருப்பொருள் |")
        out.append("|---|---|---|---|")
        for entry in chart.vimshottari_schedule[:7]:
            md_name = entry.get("planet") or entry.get("md")
            sd = entry.get("start_year") or (entry.get("start").year if entry.get("start") else "—")
            ed = entry.get("end_year") or (entry.get("end").year if entry.get("end") else "—")
            theme = PLANET_DOMAINS_TA.get(md_name, "")
            theme_short = theme.split(",")[0]
            out.append(f"| **{PLANETS_TA.get(md_name, md_name)}** | {sd} | {ed} | {theme_short} |")
        out.append("")
    return "\n".join(out)


def _section_planets_table_ta(chart) -> str:
    out = ["## ✦ வீடு வீடாக (வாழ்வின் பன்னிரண்டு பகுதிகள்)\n"]
    out.append(
        "கீழே உள்ள ஒவ்வொரு வரிசையும் ஜாதகத்தின் ஒரு வீடு, அது "
        "ஆளும் பகுதி, அதன் வலிமை குறித்த எளிய தமிழ் கருத்து."
    )
    out.append("")
    out.append("| வீடு | பகுதி | கருத்து |")
    out.append("|---:|---|:---|")
    bb = {}
    if hasattr(chart, "bhava_bala") and isinstance(chart.bhava_bala, dict):
        bb = chart.bhava_bala
    REMARK_TA = {"Strong": "வலுவானது", "Good": "நல்லது",
                 "Average": "நடுத்தரம்", "Challenging": "சவாலானது"}
    for h in range(1, 13):
        score = bb.get(h, bb.get(str(h), 0))
        try:
            remark_en = house_strength_remark(float(score)) if score else ""
            remark = REMARK_TA.get(remark_en, "—")
        except (TypeError, ValueError):
            remark = "—"
        domain = HOUSE_DOMAINS_TA[h].split(",")[0]
        out.append(f"| {_ord_ta(h)} | {domain} | **{remark}** |")
    out.append("")
    return "\n".join(out)


def _section_remedies_ta(chart) -> str:
    out = ["## ✦ சாஸ்திர பரிகாரங்கள்\n"]
    out.append(
        "கீழே ஒவ்வொரு சவாலுக்கும் கிளாசிக்கல் சாஸ்திரம் கூறும் "
        "பரிகாரங்கள். ஒவ்வொரு பரிகாரமும் அதன் மூல நூலிலிருந்து "
        "*அப்படியே* (ப்ரிகு சம்ஹிதை, பலதீபிகா, லால் கிதாப், "
        "முகூர்த்த சிந்தாமணி) மேற்கோள் காட்டப்படுகிறது — "
        "நீங்களே உறுதிப்படுத்திக் கொள்ளலாம்."
    )
    out.append("")
    try:
        from engine.remedies import remedies_for_chart
        from engine.remedies_verbatim import remedies_for_affliction_code
        plan = remedies_for_chart(chart)
        for entry in plan["afflictions_with_remedies"][:8]:
            a = entry["affliction"]
            out.append(f"**சவால்:** {a['name'].split('—')[0].strip()}")
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
            out.append("")
    except Exception as e:
        out.append(f"_(பிழை: {e})_")
    return "\n".join(out)


def _section_bhrigu_ta(chart) -> str:
    from engine.bhrigu_predictions import predictions_for_chart
    rows = predictions_for_chart(chart, max_per_planet=3)
    out = ["## ✦ ப்ரிகு நாடி — அப்படியே மேற்கோள் காட்டப்பட்ட பாடல்கள்\n"]
    if not rows:
        out.append("_பொருந்தும் ப்ரிகு பாடல்கள் கிடைக்கவில்லை._")
        return "\n".join(out)
    out.append(
        "ப்ரிகு நாடி என்பது புள்ளி-கணிப்பு ஜோதிடத்தின் மிகப் பழைய அடுக்கு. "
        "கீழே உள்ள ஒவ்வொரு வரியும் ப்ரிகு சம்ஹிதையில் இருந்து "
        "*நேரடியாகப்* பெறப்பட்டது."
    )
    out.append("")
    for row in rows:
        planet_ta = PLANETS_TA.get(row['planet'], row['planet'])
        out.append(
            f"**{planet_ta}** உங்கள் {_ord_ta(row['house'])} வீட்டில் — "
            f"{HOUSE_DOMAINS_TA[row['house']].split(',')[0]}."
        )
        out.append("")
        for pred in row["predictions"]:
            txt = pred["text"].replace("\n", " ").strip()
            out.append(f"> *{pred['citation']}:* {txt}")
            out.append("")
    return "\n".join(out)


def _section_kp_ta(chart) -> str:
    from engine.kp_predictions import predictions_for_chart
    rows = predictions_for_chart(chart, max_per_house=2)
    out = ["## ✦ KP (கிருஷ்ணமூர்த்தி பத்ததி)\n"]
    if not rows:
        out.append("_KP பாடல்கள் கிடைக்கவில்லை._")
        return "\n".join(out)
    out.append(
        "KP ஜோதிடம் ஒவ்வொரு கஸ்பையும் அதன் சப்-லார்ட் வழியாக படிக்கிறது. "
        "கீழே உள்ள மேற்கோள்கள் கிருஷ்ணமூர்த்தியின் *Reader 3 Predictive "
        "Stellar Astrology* நூலிலிருந்து நேரடியாகப் பெறப்பட்டவை."
    )
    out.append("")
    for row in rows:
        sl = f" · சப்-லார்ட்: **{PLANETS_TA.get(row['sub_lord'], row['sub_lord'])}**" if row.get("sub_lord") else ""
        out.append(f"### {_ord_ta(row['house'])} வீடு — {HOUSE_DOMAINS_TA[row['house']].split(',')[0]}{sl}")
        out.append("")
        for pred in row["predictions"]:
            txt = pred["text"].replace("\n", " ").strip()
            if len(txt) > 320:
                txt = txt[:317] + "…"
            out.append(f"> *{pred['citation']}:* {txt}")
            out.append("")
    return "\n".join(out)


def _section_closing_ta(chart) -> str:
    return closing_blessing_ta()


def _section_timeline_ta(chart) -> str:
    from engine.timeline_ta import render_timeline_markdown_ta
    return render_timeline_markdown_ta(chart)


def _section_life_domains_ta(chart) -> str:
    """Life-domain predictions — keep English domain text (technical) but
    add a Tamil header and lead-in. Future work: full Tamil translation."""
    from engine.life_domains import render_life_domains_markdown
    md = render_life_domains_markdown(chart)
    # Replace English heading with Tamil
    md = md.replace(
        "## ✦ Life-Domain Deep Predictions\n",
        "## ✦ வாழ்க்கைப் பகுதிகள் — ஆழமான கணிப்புகள்\n\n"
        "*(விரிவான கணிப்புகள் தொழில்நுட்ப ஆங்கிலத்தில் — அடுத்த "
        "பதிப்பில் முழுமையாக தமிழாக்கப்படும்.)*\n",
        1,
    )
    return md


def _section_education_ta(chart) -> str:
    from engine.education import render_education_markdown
    md = render_education_markdown(chart)
    md = md.replace(
        "## ✦ Your Natural Subjects (what your chart says you should study)\n",
        "## ✦ உங்கள் இயல்பான பாடம்/துறை\n\n"
        "*(விரிவான பகுப்பாய்வு ஆங்கிலத்தில் — அடுத்த பதிப்பில் தமிழ்.)*\n",
        1,
    )
    return md


def _section_accident_ta(chart) -> str:
    from engine.accident import render_accident_markdown
    md = render_accident_markdown(chart)
    md = md.replace(
        "## ✦ Health & Accident Signatures (with peak windows)\n",
        "## ✦ உடல்நலம் & விபத்து குறியீடுகள் (உச்ச காலகட்டங்களுடன்)\n\n"
        "*(விரிவான பகுப்பாய்வு ஆங்கிலத்தில் — அடுத்த பதிப்பில் தமிழ்.)*\n",
        1,
    )
    return md


def _section_timeline_deep_ta(chart) -> str:
    from engine.timeline_deep import render_deep_timeline_markdown
    md = render_deep_timeline_markdown(chart)
    md = md.replace(
        "## ✦ Period-by-Period Event Map (the deep timeline)\n",
        "## ✦ காலம்-வாரியான நிகழ்வு வரைபடம் (ஆழமான காலவரிசை)\n\n"
        "*(விரிவான கணிப்புகள் ஆங்கிலத்தில் — அடுத்த பதிப்பில் தமிழ்.)*\n",
        1,
    )
    return md


def _section_72_traits_ta(chart) -> str:
    from engine.traits_72 import render_72_traits_markdown
    md = render_72_traits_markdown(chart)
    md = md.replace(
        "## ✦ The 72-Trait Personal Profile\n",
        "## ✦ 72 பண்புகள் — முழு ஆளுமை சுயவிவரம்\n\n"
        "*(விரிவான பகுப்பாய்வு ஆங்கிலத்தில் — அடுத்த பதிப்பில் தமிழ்.)*\n",
        1,
    )
    return md


def _section_cross_validate_ta(chart) -> str:
    from engine.cross_validate import render_cross_validation_markdown
    md = render_cross_validation_markdown(chart)
    md = md.replace(
        "## ✦ Multi-Layer Consistency Check (engine self-audit)\n",
        "## ✦ பல-அடுக்கு ஒத்திசைவு சரிபார்ப்பு (என்ஜின் சுய-தணிக்கை)\n\n"
        "*(பகுப்பாய்வு ஆங்கிலத்தில் — அடுத்த பதிப்பில் தமிழ்.)*\n",
        1,
    )
    return md


def generate_client_report_ta(chart) -> str:
    sections = [
        _section_cover_ta(chart),
        _section_birth_facts_ta(chart),
        _section_personality_ta(chart),
        _section_72_traits_ta(chart),
        _section_timeline_ta(chart),
        _section_timeline_deep_ta(chart),
        _section_life_domains_ta(chart),
        _section_education_ta(chart),
        _section_accident_ta(chart),
        _section_difficulties_ta(chart),
        _section_strengths_ta(chart),
        _section_period_ta(chart),
        _section_planets_table_ta(chart),
        _section_remedies_ta(chart),
        _section_cross_validate_ta(chart),
        _section_closing_ta(chart),
    ]
    return "\n\n".join(sections)
