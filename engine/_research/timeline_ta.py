"""Tamil-language timeline narrative."""
from __future__ import annotations

import datetime as dt

from engine.timeline import build_timeline, _sign_mood
from engine.narrative_ta import (
    PLANET_DOMAINS_TA, HOUSE_DOMAINS_TA, PLANETS_TA, _ord_ta,
)

PLANET_BORN_INTO_TA = {
    "Sun":     "உங்கள் சுயம் வடிவம் பெறும் காலம் — யார் நீங்கள் என்பதை நீங்களே கண்டுகொள்வீர்கள்",
    "Moon":    "உணர்ச்சிகள் முக்கியமாகும் காலம் — மென்மை, பாசம், அம்மா மிக முக்கியமாக",
    "Mars":    "சக்தி, தைரியம், சண்டை, விபத்து வாய்ப்பு கூடும் காலம் — சகோதரர்களுடன் உராய்வு வரலாம்",
    "Mercury": "படிப்பு, பேச்சு, புத்திசாலித்தனம் வளரும் காலம் — பள்ளி, நண்பர்கள், புதிய கருத்துகள்",
    "Jupiter": "வளர்ச்சி, கல்வி, அதிர்ஷ்டக் காலம் — ஆசிரியர், தர்மம், நம்பிக்கை வளரும்",
    "Venus":   "சந்தோஷம், அழகு, உறவுகள் காலம் — காதல், சௌகரியம், கலை, பணம்",
    "Saturn":  "உழைப்பு, ஒழுக்கம், கடினமான பாடங்கள் கற்கும் காலம் — மெதுவான ஆனால் உறுதியான வளர்ச்சி",
    "Rahu":    "புதிய பாதை, வெளிநாடு, பெரிய லட்சியம் வரும் காலம் — பழகாத விஷயங்கள் சந்திப்பீர்கள்",
    "Ketu":    "உலக ஆசை குறையும் காலம் — பழைய விஷயங்கள் முடிவு, ஆன்மீகம் கூடும்",
}

PLANET_THEME_SHORT_TA = {
    "Sun":     "சுயம் & அதிகாரம்",
    "Moon":    "மனம் & உணர்ச்சி",
    "Mars":    "தைரியம் & உராய்வு",
    "Mercury": "அறிவு & பேச்சு",
    "Jupiter": "ஞானம் & கருணை",
    "Venus":   "காதல் & சௌகரியம்",
    "Saturn":  "ஒழுக்கம் & கடமை",
    "Rahu":    "லட்சியம் & மாற்றம்",
    "Ketu":    "வைராக்கியம் & ஆன்மீகம்",
}

SIGN_MOOD_TA = {
    "Aries": "வேகம், சூடான, துணிச்சல் சுவை",
    "Taurus": "பொறுமை, சேமிப்பு, பௌதிக சுவை",
    "Gemini": "வாய்ப்பேச்சு, இடம்பெயர்வு, பல வேலை",
    "Cancer": "உணர்ச்சி, குடும்ப அடிப்படை",
    "Leo": "கௌரவம், பொது, ராஜரீகம்",
    "Virgo": "ஆராய்ச்சி, சேவை, துல்லியம்",
    "Libra": "சமரசம், உறவு-நோக்கு",
    "Scorpio": "தீவிரம், மாற்றம், ரகசியம்",
    "Sagittarius": "தத்துவம், நம்பிக்கை, விரிவு",
    "Capricorn": "லட்சியம், மெதுவான வளர்ச்சி, கட்டமைப்பு",
    "Aquarius": "மரபை மீறல், நெட்வொர்க், கொள்கை",
    "Pisces": "கருணை, கனவு, ஆன்மீகம்",
}


def render_timeline_markdown_ta(chart) -> str:
    out = ["## ✦ உங்கள் வாழ்க்கைக் கதை — காலவரிசையாக\n"]
    out.append(
        "கீழே உங்கள் வாழ்க்கை பல காலங்களாக — ஒவ்வொரு காலத்தையும் "
        "எந்த மஹாதசை வடிவமைத்தது என்பதை வைத்து சொல்கிறோம். "
        "**கடந்த காலத்தை கடந்த கால வாக்கியத்தில் சொல்கிறோம் — "
        "உங்களுக்கு நடந்தது அதோடு பொருந்துகிறதா பாருங்கள்.** "
        "சரியாக பொருந்தினால், அதே ஜாதகம் சொல்லும் "
        "எதிர்காலத்தையும் நீங்கள் நம்பலாம்."
    )
    out.append("")
    entries = build_timeline(chart)
    if not entries:
        out.append("_விம்சோத்திரி தரவு கிடைக்கவில்லை._")
        return "\n".join(out)

    past = [e for e in entries if e.relationship == "past"]
    present = [e for e in entries if e.relationship == "present"]
    future = [e for e in entries if e.relationship == "future"]

    def _format_entry(e) -> str:
        planet_ta = PLANETS_TA.get(e.md_lord, e.md_lord)
        domain = HOUSE_DOMAINS_TA[e.house].split(",")[0]
        opener = (
            f"உங்களுக்கு வயது {e.age_start} முதல் {e.age_end} வரை "
            f"**{planet_ta} மஹாதசை** ஓடியது. {planet_ta} கிரகம் "
            f"உங்கள் ஜாதகத்தில் {_ord_ta(e.house)} வீட்டில் இருக்கிறார் — "
            f"அந்த வீடு {domain} வீடு. அதனால் இந்தக் காலகட்டத்தில் "
            f"உங்கள் வாழ்க்கை **{domain}** என்ற பாடத்தில் ஈடுபட்டிருந்தது: "
        )
        body = PLANET_BORN_INTO_TA.get(e.md_lord, "")
        sign_clause = (
            f" {planet_ta} கிரகம் {e.sign} ராசியில் இருந்ததால், "
            f"இந்தக் காலத்தில் சக்தி {SIGN_MOOD_TA.get(e.sign, 'தனிச் சுவையோடு')} "
            "வெளிப்பட்டது."
            if e.sign else ""
        )
        return opener + body + "." + sign_clause

    if past:
        out.append("### கடந்த காலம் — ஜாதகம் என்ன சொன்னது (உங்களுக்கு நினைவு வருமா பாருங்கள்)")
        out.append("")
        for e in past:
            yr_a = e.start.year
            yr_b = e.end.year
            planet_ta = PLANETS_TA.get(e.md_lord, e.md_lord)
            theme = PLANET_THEME_SHORT_TA.get(e.md_lord, "")
            out.append(
                f"**வயது {e.age_start}–{e.age_end} ({yr_a}–{yr_b}) · "
                f"{planet_ta} மஹாதசை — {theme}**"
            )
            out.append("")
            out.append(_format_entry(e))
            out.append("")

    if present:
        out.append("### உங்கள் தற்போதைய காலம்")
        out.append("")
        for e in present:
            yr_a = e.start.year
            yr_b = e.end.year
            planet_ta = PLANETS_TA.get(e.md_lord, e.md_lord)
            theme = PLANET_THEME_SHORT_TA.get(e.md_lord, "")
            out.append(
                f"**வயது {e.age_start}–{e.age_end} ({yr_a}–{yr_b}) · "
                f"{planet_ta} மஹாதசை — {theme}**"
            )
            out.append("")
            out.append(_format_entry(e))
            out.append("")

    if future:
        out.append("### உங்கள் எதிர்காலம்")
        out.append("")
        for e in future[:5]:
            yr_a = e.start.year
            yr_b = e.end.year
            planet_ta = PLANETS_TA.get(e.md_lord, e.md_lord)
            theme = PLANET_THEME_SHORT_TA.get(e.md_lord, "")
            out.append(
                f"**வயது {e.age_start}–{e.age_end} ({yr_a}–{yr_b}) · "
                f"{planet_ta} மஹாதசை — {theme}**"
            )
            out.append("")
            out.append(_format_entry(e))
            out.append("")

    out.append(
        "*மேலே கடந்த கால விவரங்கள் உங்களுக்கு நடந்தது போல் "
        "சரியாக பொருந்தினால் — அதுவே இந்த ஜாதக சோதனை. "
        "கடந்ததை சரியாக சொன்ன அதே ஜாதகம் தான் "
        "உங்கள் எதிர்காலத்தையும் சொல்கிறது. "
        "உத்தரவாதம் இல்லை — ஆனால் நம்பிக்கைக்கு போதுமான ஆதாரம்.*"
    )
    return "\n".join(out)
