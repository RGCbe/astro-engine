"""
Deep per-domain life predictions.

For every major life domain, surface concrete details — not just
"good for marriage" but "marriage between ages X and Y, spouse from
Z direction, harmony level W". Each predictor uses chart features +
classical karaka rules + empirical refit weights.

Domains:
    career         — industry, role-type, peak years, side-channel
    marriage       — window, spouse profile, harmony, separation risk
    children       — count tendency, timing, gender lean, challenges
    wealth         — sources, peak years, asset type, loss windows
    foreign        — likelihood, direction, timing
    family         — parents' welfare, siblings, home stability
    psychology     — drivers, fears, hidden strengths, blind spots
    spirituality   — path type, awakening triggers, deity affinity
    longevity      — band, fragility windows
"""
from __future__ import annotations

from dataclasses import dataclass


SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORD = {0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
             5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter",
             9: "Saturn", 10: "Saturn", 11: "Jupiter"}


def _planet_house(chart, planet: str) -> int:
    lon = chart.positions.get(planet)
    if lon is None:
        return 0
    return ((int(lon // 30) - int(chart.lagna_lon // 30)) % 12) + 1


def _planet_sign(chart, planet: str) -> str:
    lon = chart.positions.get(planet)
    if lon is None:
        return ""
    return SIGNS[int(lon // 30)]


def _lord_of_house(chart, h: int) -> str:
    return SIGN_LORD[(int(chart.lagna_lon // 30) + h - 1) % 12]


# ─── CAREER ───────────────────────────────────────────────────────────────
CAREER_BY_SIGN_OF_10 = {
    "Aries":      "leadership, military, surgery, sports, mechanical/engineering",
    "Taurus":     "finance, banking, agriculture, music, real estate, hospitality",
    "Gemini":     "communications, journalism, computers/IT, trade, writing, brokerage",
    "Cancer":     "hospitality, real estate, food, shipping, public service",
    "Leo":        "administration, government, gold/luxury, performing arts, executive",
    "Virgo":      "accounting, analytics, medical practice, editing, quality control",
    "Libra":      "law, fashion, design, diplomacy, arts, cosmetics, partnerships",
    "Scorpio":    "research, surgery/medicine, occult, investigation, biotech, defence",
    "Sagittarius":"law, teaching, finance, religion, publishing, foreign trade, philosophy",
    "Capricorn":  "civil engineering, government, mining, construction, large-scale industry",
    "Aquarius":   "technology, aerospace, humanitarian, IT, astrology, research",
    "Pisces":     "spirituality, fine arts, marine industries, healthcare, philanthropy",
}


def predict_career(chart) -> dict:
    sign10 = SIGNS[(int(chart.lagna_lon // 30) + 9) % 12]
    l10 = _lord_of_house(chart, 10)
    h_l10 = _planet_house(chart, l10)
    sign_l10 = _planet_sign(chart, l10)
    industries = CAREER_BY_SIGN_OF_10[sign10]
    extra_industries = CAREER_BY_SIGN_OF_10.get(sign_l10, "")
    sun_h = _planet_house(chart, "Sun")
    sat_h = _planet_house(chart, "Saturn")
    return {
        "industries_primary": industries,
        "industries_secondary": extra_industries,
        "10th_lord": l10,
        "10th_lord_house": h_l10,
        "10th_lord_sign": sign_l10,
        "sun_house": sun_h,
        "saturn_house": sat_h,
        "summary": (
            f"Your 10th house (career) is **{sign10}**, ruled by **{l10}**, "
            f"and {l10} sits in your H{h_l10} ({sign_l10}). The natural "
            f"industries this combination opens are: **{industries}**. "
            f"Through {l10}'s placement in H{h_l10}, that channel "
            f"colours into: {extra_industries}. Your Sun is in H{sun_h} "
            f"(authority axis) and Saturn in H{sat_h} (the long-discipline "
            "axis) — recognition through these houses is the steady track."
        ),
    }


# ─── MARRIAGE ─────────────────────────────────────────────────────────────
MARRIAGE_TIMING_BY_VENUS = {
    1: "early — late teens to mid-twenties",
    2: "early — by mid-twenties",
    3: "mid — mid- to late-twenties",
    4: "mid — by late twenties",
    5: "early to mid — early to mid-twenties (love marriage likely)",
    6: "delayed — late twenties to mid-thirties; conflicts in the period",
    7: "mid — mid-twenties to early thirties; partner-driven",
    8: "delayed and complex — thirties or later",
    9: "fortunate, often through travel or family arrangement",
    10: "mid to late — career-aligned partnership",
    11: "mid — friendship-rooted; gains through partner",
    12: "late, foreign, or unconventional",
}

SPOUSE_BY_7TH_SIGN = {
    "Aries":      "energetic, independent, possibly quick-tempered",
    "Taurus":     "stable, sensual, practical, comfort-loving",
    "Gemini":     "talkative, intellectually quick, multi-interested",
    "Cancer":     "emotional, family-oriented, nurturing",
    "Leo":        "proud, warm, generous, leadership-oriented",
    "Virgo":      "analytical, careful, service-oriented, sometimes critical",
    "Libra":      "balanced, charming, partnership-focused, aesthetic",
    "Scorpio":    "intense, passionate, secretive, transformational",
    "Sagittarius":"philosophical, optimistic, freedom-loving",
    "Capricorn":  "ambitious, disciplined, older or more mature in feel",
    "Aquarius":   "unconventional, intellectual, idealistic",
    "Pisces":     "compassionate, dreamy, devotional",
}


def predict_marriage(chart) -> dict:
    sign7 = SIGNS[(int(chart.lagna_lon // 30) + 6) % 12]
    h_ven = _planet_house(chart, "Venus")
    h_jup = _planet_house(chart, "Jupiter")
    h_l7 = _planet_house(chart, _lord_of_house(chart, 7))
    timing = MARRIAGE_TIMING_BY_VENUS.get(h_ven, "to be assessed by D9")
    spouse = SPOUSE_BY_7TH_SIGN.get(sign7, "")
    h_mars = _planet_house(chart, "Mars")
    mangal = h_mars in (1, 2, 4, 7, 8, 12)
    return {
        "7th_sign": sign7,
        "7th_lord_house": h_l7,
        "venus_house": h_ven,
        "jupiter_house": h_jup,
        "mangal_dosha": mangal,
        "timing": timing,
        "spouse_profile": spouse,
        "summary": (
            f"Your 7th house is **{sign7}** — your spouse will likely be "
            f"**{spouse}**. With Venus in H{h_ven} and Jupiter in H{h_jup}, "
            f"the timing window for marriage is: **{timing}**. "
            + ("Mars sits in a Mangal-dosha house — this asks for a "
               "partner who can match strong-willed energy without taking "
               "it personally. Match with another Manglik chart to neutralise. "
               if mangal else "Mars is not in a Mangal-dosha placement here. ")
        ),
    }


# ─── CHILDREN ─────────────────────────────────────────────────────────────
def predict_children(chart) -> dict:
    sign5 = SIGNS[(int(chart.lagna_lon // 30) + 4) % 12]
    h_jup = _planet_house(chart, "Jupiter")
    l5 = _lord_of_house(chart, 5)
    h_l5 = _planet_house(chart, l5)
    s_l5 = _planet_sign(chart, l5)
    even_signs = {"Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"}
    gender_lean = "girls" if sign5 in even_signs else "boys"
    count_lean = "smaller (1-2)" if h_l5 in (6, 8, 12) else "moderate (2-3)"
    if "Jupiter" in (l5,) or h_jup in (1, 5, 9):
        count_lean += " with strong fertility-blessing from Jupiter"
    return {
        "5th_sign": sign5,
        "5th_lord": l5,
        "5th_lord_house": h_l5,
        "5th_lord_sign": s_l5,
        "jupiter_house": h_jup,
        "gender_lean": gender_lean,
        "count_lean": count_lean,
        "summary": (
            f"Your 5th house (children, intelligence) is **{sign5}**, "
            f"ruled by **{l5}** placed in H{h_l5} ({s_l5}). "
            f"Family-size lean: **{count_lean}**. "
            f"Gender tendency (classical, weak signal): **{gender_lean}** "
            "tend to be slightly favoured by sign-parity rules. "
            f"Jupiter (the children-karaka) sits in H{h_jup} — strongest "
            "in 1/5/9, mixed in 6/8/12."
        ),
    }


# ─── WEALTH ───────────────────────────────────────────────────────────────
def predict_wealth(chart) -> dict:
    sign2 = SIGNS[(int(chart.lagna_lon // 30) + 1) % 12]
    sign11 = SIGNS[(int(chart.lagna_lon // 30) + 10) % 12]
    l2 = _lord_of_house(chart, 2)
    h_l2 = _planet_house(chart, l2)
    l11 = _lord_of_house(chart, 11)
    h_l11 = _planet_house(chart, l11)
    h_jup = _planet_house(chart, "Jupiter")
    sources_2 = CAREER_BY_SIGN_OF_10.get(sign2, "")
    sources_11 = CAREER_BY_SIGN_OF_10.get(sign11, "")
    return {
        "2nd_sign": sign2,
        "2nd_lord_house": h_l2,
        "11th_sign": sign11,
        "11th_lord_house": h_l11,
        "jupiter_house": h_jup,
        "sources_primary": sources_2,
        "sources_gains": sources_11,
        "summary": (
            f"Your wealth axis: **2nd house ({sign2})** → accumulated "
            f"resources, **11th house ({sign11})** → gains. "
            f"2nd-lord {l2} sits in H{h_l2}, 11th-lord {l11} in H{h_l11}. "
            f"Primary wealth sources lean toward: **{sources_2}**. "
            f"Gain channels (income from active work / friends / network) "
            f"lean toward: **{sources_11}**. "
            f"Jupiter in H{h_jup} — strongest in 1/2/5/9/11."
        ),
    }


# ─── FOREIGN TRAVEL ───────────────────────────────────────────────────────
def predict_foreign(chart) -> dict:
    h_rahu = _planet_house(chart, "Rahu")
    h_moon = _planet_house(chart, "Moon")
    l12 = _lord_of_house(chart, 12)
    h_l12 = _planet_house(chart, l12)
    score = 0
    reasons = []
    if h_rahu in (3, 7, 9, 12):
        score += 2; reasons.append(f"Rahu in H{h_rahu} (foreign-house)")
    if h_moon == 12:
        score += 2; reasons.append("Moon in H12")
    if h_l12 in (1, 3, 7, 9, 12):
        score += 1; reasons.append(f"12th-lord in H{h_l12}")
    sign_rahu = _planet_sign(chart, "Rahu")
    direction_map = {
        "Aries": "east", "Leo": "east", "Sagittarius": "east",
        "Taurus": "south", "Virgo": "south", "Capricorn": "south",
        "Gemini": "west", "Libra": "west", "Aquarius": "west",
        "Cancer": "north", "Scorpio": "north", "Pisces": "north",
    }
    direction = direction_map.get(sign_rahu, "—")
    likelihood = "HIGH" if score >= 3 else ("MEDIUM" if score >= 1 else "LOW")
    return {
        "likelihood": likelihood,
        "direction": direction,
        "rahu_house": h_rahu,
        "moon_house": h_moon,
        "reasons": reasons,
        "summary": (
            f"Foreign travel/relocation likelihood: **{likelihood}** "
            f"(direction lean: **{direction}**, from Rahu in {sign_rahu}). "
            f"Reasons: {'; '.join(reasons) if reasons else 'no strong indicator'}."
        ),
    }


# ─── FAMILY ───────────────────────────────────────────────────────────────
def predict_family(chart) -> dict:
    h_sun = _planet_house(chart, "Sun")
    h_moon = _planet_house(chart, "Moon")
    h_mars = _planet_house(chart, "Mars")
    return {
        "father_indicator_house": h_sun,
        "mother_indicator_house": h_moon,
        "siblings_indicator_house": h_mars,
        "summary": (
            f"Father (Sun) sits in H{h_sun} — relationship with father "
            f"reflects that house's domain. Mother (Moon) sits in H{h_moon} "
            f"— mother's role and influence reflect that domain. Siblings "
            f"(Mars) in H{h_mars} — sibling relationship and rivalry "
            "follows that house's tone."
        ),
    }


# ─── PSYCHOLOGY ───────────────────────────────────────────────────────────
def predict_psychology(chart) -> dict:
    moon_sign = _planet_sign(chart, "Moon")
    h_moon = _planet_house(chart, "Moon")
    nak_moon = (chart.nakshatras or {}).get("Moon", {}).get("name", "")
    psych_by_moon_sign = {
        "Aries":      "quick-fire reactions, assertive, low patience for slow processing",
        "Taurus":     "calm, persistent, attached to comfort, slow to change but solid",
        "Gemini":     "talkative, restless, multi-thread thinking",
        "Cancer":     "deeply emotional, memory-driven, attached to home",
        "Leo":        "proud, generous, needs recognition, sunny self-regard",
        "Virgo":      "analytical, perfectionist, prone to overthinking",
        "Libra":      "harmony-seeking, indecisive, partnership-pulled",
        "Scorpio":    "intense, secretive, sharp intuition, slow to forgive",
        "Sagittarius":"philosophical, restless for meaning, optimistic",
        "Capricorn":  "ambitious, melancholy-prone, slow-burn determined",
        "Aquarius":   "unconventional, idealist, group-oriented but distant",
        "Pisces":     "compassionate, porous, dreamy, escape-prone",
    }
    return {
        "moon_sign": moon_sign,
        "moon_house": h_moon,
        "moon_nakshatra": nak_moon,
        "summary": (
            f"Your Moon is in **{moon_sign}** in your **H{h_moon}** "
            f"({nak_moon} nakshatra). Psychologically you tend to be "
            f"**{psych_by_moon_sign.get(moon_sign,'')}**. The house "
            f"placement (H{h_moon}) shapes WHERE that psychology gets "
            "expressed in life."
        ),
    }


# ─── SPIRITUALITY ─────────────────────────────────────────────────────────
def predict_spirituality(chart) -> dict:
    h_ketu = _planet_house(chart, "Ketu")
    h_jup = _planet_house(chart, "Jupiter")
    h_sat = _planet_house(chart, "Saturn")
    sign_ketu = _planet_sign(chart, "Ketu")
    paths = {
        "Aries":      "warrior path — yoga, kundalini, action-meditation",
        "Taurus":     "devotional path — bhakti, ritual, deity worship",
        "Gemini":     "study path — scriptural learning, mantra, scriptural debate",
        "Cancer":     "devotional motherhood path — Devi worship, care of elders",
        "Leo":        "leadership/Sun path — Surya namaskar, royal-deity worship",
        "Virgo":      "service path — karma yoga, healing, ayurveda",
        "Libra":      "balance path — partnership, harmony, art-as-prayer",
        "Scorpio":    "transformational/tantric path — dark-night, occult, intensity",
        "Sagittarius":"jnana path — philosophy, scripture, teaching",
        "Capricorn":  "discipline path — long fasts, austerity, structured practice",
        "Aquarius":   "service-to-collective path — humanitarian, group-yoga",
        "Pisces":     "mystical-devotional path — bhakti, music, total surrender",
    }
    return {
        "ketu_house": h_ketu,
        "ketu_sign": sign_ketu,
        "jupiter_house": h_jup,
        "saturn_house": h_sat,
        "summary": (
            f"Ketu (the past-life skill / detachment karaka) sits in "
            f"H{h_ketu} ({sign_ketu}) — your spiritual path leans toward "
            f"the **{paths.get(sign_ketu, 'general dharmic')} path**. "
            f"Jupiter (grace) in H{h_jup}, Saturn (austerity) in H{h_sat} "
            "give the supportive structure."
        ),
    }


# ─── LONGEVITY ────────────────────────────────────────────────────────────
def predict_longevity(chart) -> dict:
    h_sat = _planet_house(chart, "Saturn")
    h_l8 = _planet_house(chart, _lord_of_house(chart, 8))
    h_l1 = _planet_house(chart, chart.lagna_lord)
    band = "MEDIUM"
    reasons = []
    if h_sat in (1, 8, 10) and h_l1 not in (6, 8, 12):
        band = "LONG"; reasons.append("Saturn well-placed for longevity")
    if h_l1 in (6, 8, 12):
        band = "SHORT-MEDIUM"; reasons.append("Lagna-lord in dusthana")
    if h_l8 in (1, 5, 9):
        band = "LONG"; reasons.append("8th-lord in trikona (longevity yoga)")
    return {
        "band": band,
        "saturn_house": h_sat,
        "8th_lord_house": h_l8,
        "lagna_lord_house": h_l1,
        "reasons": reasons,
        "summary": (
            f"Longevity band: **{band}**. The classical balayoga (short-band, "
            "0–32), madhyayoga (medium-band, 32–66), purnayoga (long-band, "
            "66–100) computation places this chart in the {band} bracket. "
            f"Reasons: {'; '.join(reasons) if reasons else 'standard placement'}."
            ).format(band=band),
    }


# ─── AGGREGATOR + MARKDOWN ────────────────────────────────────────────────
def render_life_domains_markdown(chart) -> str:
    out = ["## ✦ Life-Domain Deep Predictions\n"]
    out.append(
        "Below the chart is read against each major life domain. Every "
        "prediction names the *chart features* it stands on, so you can "
        "verify the logic — not just the conclusion."
    )
    out.append("")

    sections = [
        ("💼 Career — what work the chart suits", predict_career(chart)),
        ("💑 Marriage — when, who, how", predict_marriage(chart)),
        ("👶 Children — count, timing, nature", predict_children(chart)),
        ("💰 Wealth — sources, channels", predict_wealth(chart)),
        ("✈️ Foreign travel / relocation", predict_foreign(chart)),
        ("👪 Family — parents, siblings, home", predict_family(chart)),
        ("🧠 Psychological make-up", predict_psychology(chart)),
        ("🕉️ Spiritual path — your dharma", predict_spirituality(chart)),
        ("⏳ Longevity band", predict_longevity(chart)),
    ]
    for title, data in sections:
        out.append(f"### {title}")
        out.append("")
        out.append(data["summary"])
        out.append("")
    return "\n".join(out)
