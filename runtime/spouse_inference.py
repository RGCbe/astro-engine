"""Spouse Inference — describe partner from native's D9 + 7H + Venus + DK + Upapada.

Source: BPHS Ch. 80 (Marriage), Saravali Ch. 35-36, Jaimini Sutras.
"""
import sys
sys.path.insert(0, ".")
from vedic_core import DIGNITIES

from divisional_charts import build_divisional_chart, RASIS, RASI_LORDS

SPOUSE_TRAITS_BY_SIGN = {
    "Aries":     "Energetic, independent, pioneering. Likely athletic, action-oriented, sometimes impatient or hot-tempered.",
    "Taurus":    "Steady, sensual, loyal, comfort-loving. Stable provider, values material security, sometimes stubborn.",
    "Gemini":    "Witty, communicative, social, intellectually curious. Versatile, talkative, sometimes scattered.",
    "Cancer":    "Nurturing, emotional, home-loving, protective. Devoted to family, can be moody.",
    "Leo":       "Charismatic, proud, generous, dramatic. Natural leader, attention-loving, warm-hearted.",
    "Virgo":     "Analytical, service-oriented, health-conscious, refined. Careful, detail-focused, sometimes critical.",
    "Libra":     "Charming, diplomatic, artistic, balance-seeking. Beautiful aesthetic sense, partnership-oriented.",
    "Scorpio":   "Intense, loyal, secretive, transformative. Passionate, deep emotional waters, magnetic.",
    "Sagittarius":"Philosophical, adventurous, freedom-loving, direct. Optimistic, knowledge-loving, traveler.",
    "Capricorn": "Ambitious, disciplined, career-focused, reserved. Mature, responsible, sometimes cold.",
    "Aquarius":  "Independent, unconventional, humanitarian, intellectual. Friendly, idealistic, sometimes detached.",
    "Pisces":    "Empathetic, spiritual, creative, sensitive. Romantic, intuitive, sometimes idealistic dreamer.",
}

DK_PLANET_TYPES = {
    "Sun":     "Authoritative, government/leadership type, ego-driven, family of strong father",
    "Moon":    "Nurturing, public/hospitality type, emotional, family of devoted mother",
    "Mars":    "Bold, athletic/military/police type, energetic, possibly competitive",
    "Mercury": "Intellectual, communicative type — teacher/writer/analyst, articulate",
    "Jupiter": "Wise, dharmic, teacher/advisor type, religious or philosophical",
    "Venus":   "Beautiful, artistic, refined, comfort-loving, possibly from cultured family",
    "Saturn":  "Disciplined, mature/elder type, hardworking, may be from a humble background",
    "Rahu":    "Foreign or unconventional partner — different culture/background/religion possible",
    "Ketu":    "Spiritual or detached partner, possibly from unfamiliar/exotic background",
}


def infer_spouse(natal_chart):
    """Comprehensive spouse description from multiple chart points."""
    pos = natal_chart["positions"]
    lagna_idx = natal_chart["lagna_idx"]

    # 1. 7th house sign + lord
    h7_sign = RASIS[(lagna_idx + 6) % 12]
    h7_lord = RASI_LORDS[h7_sign]
    h7_lord_house = pos[h7_lord]["house"] if h7_lord in pos else None

    # 2. 7th house occupants
    h7_occ = [p for p, pd in pos.items() if pd["house"] == 7]

    # 3. Venus position
    venus_h = pos["Venus"]["house"] if "Venus" in pos else None
    venus_sign = pos["Venus"]["rasi"] if "Venus" in pos else None

    # 4. Darakaraka (DK from Jaimini)
    from jaimini_full import chara_karakas_jaimini
    karakas = chara_karakas_jaimini(natal_chart)
    dk = karakas[6][1] if len(karakas) > 6 else None

    # 5. D9 7th house
    try:
        d9 = build_divisional_chart(natal_chart, "D9")
        d9_pos = d9["positions"]
        d9_h7_sign = RASIS[(d9["lagna_idx"] + 6) % 12]
        d9_h7_lord = RASI_LORDS[d9_h7_sign]
        d9_h7_lord_house = d9_pos[d9_h7_lord]["house"] if d9_h7_lord in d9_pos else None

        # Where DK sits in D9
        dk_in_d9 = d9_pos[dk]["rasi"] if dk and dk in d9_pos else None
    except:
        d9_h7_sign = None
        dk_in_d9 = None

    # 6. Upapada Lagna (Jaimini spouse indicator)
    from jaimini_full import upapada_lagna
    ul = upapada_lagna(natal_chart)

    # Compose description
    primary_sign = h7_sign  # natal 7H sign is primary
    primary_traits = SPOUSE_TRAITS_BY_SIGN.get(primary_sign, "")

    # DK influence
    dk_traits = DK_PLANET_TYPES.get(dk, "")

    # Background
    if h7_lord_house in [9, 12]:
        background = "Spouse may come from a different region, culture, or religious background than you."
    elif h7_lord_house in [1, 4]:
        background = "Spouse comes from a familiar background — same region, language, or culture."
    elif h7_lord_house in [10, 11]:
        background = "Spouse comes from a professionally established or socially respected family."
    else:
        background = "Spouse background is moderately known/familiar."

    # Beauty / nature
    venus_str = "neutral"
    
    if "Venus" in pos:
        d = DIGNITIES.get(("Venus", pos["Venus"]["rasi"]), "neutral")
        if d in ["Own","Exalted"]:
            venus_str = "Spouse will be physically attractive, charming, well-groomed, with refined aesthetic taste."
        elif d == "Debil":
            venus_str = "Spouse may carry past struggles or unconventional beauty; love grows through deeper qualities than surface."
        else:
            venus_str = "Spouse will be pleasant in appearance, balanced demeanor."

    # Career
    h7_lord_career_map = {
        "Sun":"government, administration, leadership",
        "Moon":"public service, hospitality, nursing, real estate",
        "Mars":"engineering, military, sports, surgery",
        "Mercury":"IT, finance, teaching, writing, business",
        "Jupiter":"education, law, banking, advisory roles",
        "Venus":"arts, design, fashion, luxury, beauty",
        "Saturn":"construction, labor management, research, agriculture",
    }
    spouse_career = h7_lord_career_map.get(h7_lord, "various fields")

    # Marriage timing window
    from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive
    try:
        birth_year = natal_chart.get("birth", {}).get("year", 1996)
        events = scan_lifetime_v2(natal_chart, birth_year, birth_year + 60, sample_days=30, min_severity=3)
        marriage_bands = [e for e in events if "Marriage" in e["event"] and e["first"].year >= (birth_year + 21)]
        if marriage_bands:
            top = sorted(marriage_bands, key=lambda e:-e["max_sev"])[0]
            marriage_window = f"{top['first'].strftime('%b %Y')} - {top['last'].strftime('%b %Y')}"
        else:
            marriage_window = "see Varshaphala for year-by-year"
    except Exception:
        marriage_window = "see life events table"

    return {
        "h7_sign": h7_sign,
        "h7_lord": h7_lord,
        "h7_lord_house": h7_lord_house,
        "h7_occupants": h7_occ,
        "venus_sign": venus_sign,
        "venus_house": venus_h,
        "darakaraka": dk,
        "darakaraka_in_d9": dk_in_d9,
        "d9_7th_sign": d9_h7_sign,
        "upapada_lagna": ul,

        "personality": primary_traits,
        "dk_archetype": dk_traits,
        "appearance": venus_str,
        "background": background,
        "career_field": spouse_career,
        "marriage_window": marriage_window,

        "summary": (
            f"Your spouse is most likely a {primary_sign}-quality person: {primary_traits[:100]}... "
            f"Likely working in: {spouse_career}. {background} {venus_str}"
        ),
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    result = infer_spouse(chart)
    print(f"=== SPOUSE INFERENCE for {chart['name']} ===\n")
    print(f"  7H sign:           {result['h7_sign']}")
    print(f"  7H lord:           {result['h7_lord']} (in H{result['h7_lord_house']})")
    print(f"  Darakaraka:        {result['darakaraka']}")
    print(f"  DK in D9:          {result['darakaraka_in_d9']}")
    print(f"  D9 7H sign:        {result['d9_7th_sign']}")
    print(f"  Upapada Lagna:     {result['upapada_lagna']}")
    print(f"\n  PERSONALITY:  {result['personality']}")
    print(f"  DK archetype: {result['dk_archetype']}")
    print(f"  Appearance:   {result['appearance']}")
    print(f"  Background:   {result['background']}")
    print(f"  Career field: {result['career_field']}")
    print(f"  Marriage window: {result['marriage_window']}")
    print(f"\n  SUMMARY: {result['summary']}")
