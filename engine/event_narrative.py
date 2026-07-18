# -*- coding: utf-8 -*-
"""Infer wealth/career/marriage source and loss mechanism from chart + why[] + dasha."""
from __future__ import annotations

import re
from typing import Any

SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}


def _t(*codes: int) -> str:
    return "".join(chr(c) for c in codes)


SOURCE_TA = {
    "salary": _t(0xbaa, 0xba9, 0xf, 0xb9a, 0xbbf) + " / " + _t(0xb89, 0xbaf, 0xbb0, 0xbcd, 0xbb5, 0xbc1),
    "business": _t(0xbb5, 0xba3, 0xb95) + " / " + _t(0xba4, 0xbca, 0xbb4, 0xbbf, 0xbb2, 0xbcd),
    "land": _t(0xba8, 0xbbf, 0xbb2, 0xbae, 0xbcd) + " / " + _t(0xb9a, 0xbca, 0xba4, 0xbcd, 0xba4, 0xbc1),
    "rental": _t(0xbb5, 0xbbe, 0xb9f, 0xb95, 0xbc8) + " " + _t(0xbb5, 0xbb0, 0xbc1, 0xbae, 0xbbe, 0xba9, 0xbae, 0xbcd),
    "inheritance": _t(0xbaa, 0xbbe, 0xbb0, 0xb9a, 0xbc1) + " / " + _t(0xb95, 0xbc1, 0xb9f, 0xbc1, 0xbae, 0xbcd, 0xbaa, 0xbae, 0xbcd),
    "spouse": _t(0xb9a, 0xbc1, 0xba4, 0xbbf) + " / " + _t(0xbaa, 0xba4, 0xbcd, 0xba9, 0xbbf),
    "network": _t(0xb8e, 0xba4, 0xbbf, 0xbb0, 0xbcd) + " / " + _t(0xb95, 0xbc1, 0xbb1, 0xbbf, 0xbcd, 0xbaa, 0xbc1),
    "speculation": _t(0xb9a, 0xbc1, 0xbaf, 0xbcd, 0xbaa, 0xbc1, 0xbb1, 0xbc1, 0xbb5, 0xbc1) + " / " + _t(0xbaa, 0xb99, 0xbcd, 0xb95, 0xbc1),
    "father": _t(0xba4, 0xba8, 0xbcd, 0xba4, 0xbc8) + " / " + _t(0xb95, 0xbc1, 0xbb0, 0xbc1),
    "grace": _t(0xb95, 0xbc1, 0xbb0, 0xbc1) + " " + _t(0xb85, 0xba9, 0xbc1, 0xb95, 0xbcd, 0xb95, 0xbbf, 0xbb0, 0xb95, 0xbae, 0xbcd),
    "education": _t(0xbb5, 0xbbf, 0xba4, 0xbcd, 0xba4, 0xbbf, 0xbaf, 0xbbe, 0xb9a, 0xbae, 0xbcd),
    "foreign": _t(0xbb5, 0xbc6, 0xbb3, 0xbbf, 0xba8, 0xbbe, 0xb9f, 0xbc1),
}

MECHANISM_TA = {
    "legal": _t(0xb9a, 0xb9f, 0xbcd, 0xb9f, 0xbc1) + " / " + _t(0xbb5, 0xbb0, 0xbbf, 0xbb5, 0xbb4, 0xb95, 0xbcd, 0xb95, 0xbc1),
    "medical": _t(0xb86, 0xbb0, 0xbcb, 0xb95) + " " + _t(0xb9a, 0xbc6, 0xbb2, 0xbb5, 0xbc1),
    "job_loss": _t(0xbb5, 0xbc7, 0xbb2, 0xbc8) + " " + _t(0xb87, 0xbb4, 0xbcd, 0xbaa, 0xbc1),
    "partnership": _t(0xb95, 0xbc2, 0xb9f, 0xbcd, 0xb9f, 0xbc1) + " " + _t(0xb89, 0xb9f, 0xbc8, 0xbb5, 0xbc1),
    "fraud": _t(0xb8e, 0xbb0, 0xbbf) + " / " + _t(0xbb0, 0xbbe, 0xb95, 0xbc1),
    "family_expense": _t(0xb95, 0xbc1, 0xb9f, 0xbc1, 0xbae, 0xbcd, 0xbaa) + " " + _t(0xb9a, 0xbc6, 0xbb2, 0xbb5, 0xbc1),
    "market": _t(0xb9a, 0xba8, 0xbcd, 0xba4, 0xbc8) + " " + _t(0xb87, 0xbb4, 0xbcd, 0xbaa, 0xbc1),
    "delay": _t(0xb9a, 0xba9, 0xbbf) + " " + _t(0xba4, 0xbbe, 0xbae, 0xba4, 0xbae, 0xbcd),
    "sudden": "8" + _t(0xbb5, 0xba4, 0xbc1) + " " + _t(0xba4, 0xbbf, 0xb9f, 0xbc0, 0xbb0, 0xbcd) + " " + _t(0xb87, 0xbb4, 0xbcd, 0xbaa, 0xbc1),
    "abroad_drain": "12" + _t(0xbb5, 0xba4, 0xbc1) + " " + _t(0xbb5, 0xbc6, 0xbb3, 0xbbf, 0xba8, 0xbbe, 0xb9f, 0xbc1) + " " + _t(0xb9a, 0xbc6, 0xbb2, 0xbb5, 0xbc1),
}

DISCLAIMER_EN = "Mechanical inference, not guaranteed."
DISCLAIMER_TA = _t(0xb95, 0xba3, 0xbbf, 0xba4, 0xbcd, 0xba4) + " " + _t(0xb85, 0xba9, 0xbc1, 0xbae, 0xbbe, 0xba9, 0xbae, 0xbcd) + " \u2014 " + _t(0xb89, 0xbb1, 0xbc1, 0xba4, 0xbbf) + " " + _t(0xb87, 0xbb2, 0xbcd, 0xbb2, 0xbc8) + "."

LABEL_LOSS_TA = _t(0xb87, 0xbb4, 0xbcd, 0xbaa, 0xbc1) + ":"
LABEL_GAIN_TA = _t(0xbb5, 0xbb0, 0xbc1, 0xbae, 0xbbe, 0xba9, 0xbae, 0xbcd) + ":"

HOUSE_GAIN = {
    2: ("inheritance", "family savings / ancestral line"),
    4: ("land", "property / home / land"),
    5: ("speculation", "creative income / trading / children-linked gains"),
    7: ("spouse", "partner / contracts / client income"),
    9: ("father", "father / dharma / higher support"),
    10: ("salary", "job / profession / authority role"),
    11: ("network", "gains / friends / corporate inflow"),
}

HOUSE_LOSS = {
    6: ("medical", "medical bills / legal dispute / enemies"),
    8: ("sudden", "sudden shock / tax / inheritance dispute"),
    12: ("abroad_drain", "expenses / abroad drain / hospital"),
}

PLANET_SOURCE = {
    "Jupiter": ("grace", "Jupiter grace / expansion"),
    "Venus": ("spouse", "Venus comfort, spouse, arts contracts"),
    "Mercury": ("business", "Mercury trade, communication, contracts"),
    "Mars": ("land", "Mars property sale / competitive earn"),
    "Moon": ("network", "Moon public / fluctuating income"),
    "Sun": ("salary", "Sun authority salary / government"),
    "Saturn": ("delay", "Saturn slow gain or delayed payout"),
    "Rahu": ("speculation", "Rahu unconventional / market risk"),
    "Ketu": ("family_expense", "Ketu sudden cut / detachment cost"),
}

WEALTH_CATS = frozenset({
    "wealth", "wealth_peak", "property", "inheritance", "lakshmi_yoga",
    "speculation_gain", "plot_sale", "land_acquisition", "wealth_gain",
})
LOSS_CATS = frozenset({"wealth_loss", "property_loss", "debt", "financial_scandal"})
CAREER_CATS = frozenset({
    "career", "promotion", "career_breakthrough", "leadership_emergence", "education",
})
MARRIAGE_CATS = frozenset({
    "marriage", "engagement", "relationship_phase", "saham_kalatra", "relationship_break",
})

GENERIC_EVENT_CATS = frozenset({
    "d60_event", "kala_sarpa", "birth_mark", "bazi", "mayan", "kp_event",
    "ziwei", "numerology", "mouth_medical", "sibling_health", "ardha_ashtama",
    "trimshamsa", "roga_saham",
})


def build_house_lord_map(lagna_idx: int) -> dict[int, str]:
    return {h: SIGN_LORD[(lagna_idx + h - 1) % 12] for h in range(1, 13)}


def houses_ruled_by_lagna(lagna_idx: int, planet: str) -> list[int]:
    return [h for h in range(1, 13) if SIGN_LORD[(lagna_idx + h - 1) % 12] == planet]


def _lagna_idx(chart: dict) -> int:
    return chart.get("lagna_idx", int(chart.get("lagna_lon", 0) // 30))


def lord_of_house(chart: dict, house: int) -> str:
    return SIGN_LORD[(_lagna_idx(chart) + house - 1) % 12]


def houses_ruled_by(chart: dict, planet: str) -> list[int]:
    return [h for h in range(1, 13) if lord_of_house(chart, h) == planet]


def _parse_houses_from_why(why_list: list[Any]) -> list[int]:
    houses: list[int] = []
    for item in why_list or []:
        text = str(item)
        for m in re.finditer(r"\b(\d{1,2})H\b", text, re.I):
            h = int(m.group(1))
            if 1 <= h <= 12:
                houses.append(h)
        for m in re.finditer(r"\bH(\d{1,2})\b", text, re.I):
            h = int(m.group(1))
            if 1 <= h <= 12:
                houses.append(h)
        for m in re.finditer(r"(\d{1,2})L", text):
            h = int(m.group(1))
            if 1 <= h <= 12:
                houses.append(h)
    return sorted(set(houses))


def _confidence(score: int, n_tags: int) -> str:
    if score >= 4 and n_tags >= 2:
        return "moderate-high"
    if score >= 2 or n_tags >= 1:
        return "moderate"
    return "low"


def _tags_line(tags: list[str], lang: str) -> str:
    if not tags:
        return ""
    if lang == "ta":
        return ", ".join(SOURCE_TA.get(t, MECHANISM_TA.get(t, t)) for t in tags[:4])
    return ", ".join(tags[:4])


def infer_source_and_mechanism(
    chart: dict,
    category: str,
    why_list: list[Any] | None = None,
    dasha_ctx: dict | None = None,
) -> dict:
    why_list = list(why_list or [])
    dasha_ctx = dasha_ctx or {}
    md = dasha_ctx.get("md")
    ad = dasha_ctx.get("ad")
    houses = _parse_houses_from_why(why_list)
    source_tags: list[str] = []
    mechanism_tags: list[str] = []
    mechanism_bits: list[str] = []
    score = 0
    cat = (category or "").lower()

    def add_source(tag: str, reason: str, pts: int = 1):
        nonlocal score
        if tag not in source_tags:
            source_tags.append(tag)
        if reason not in mechanism_bits:
            mechanism_bits.append(reason)
        score += pts

    def add_mech(tag: str, reason: str, pts: int = 1):
        nonlocal score
        if tag not in mechanism_tags:
            mechanism_tags.append(tag)
        if reason not in mechanism_bits:
            mechanism_bits.append(reason)
        score += pts

    for planet in (ad, md):
        if not planet:
            continue
        for h in houses_ruled_by(chart, planet):
            houses.append(h)
            if cat in WEALTH_CATS or cat in CAREER_CATS:
                if h in HOUSE_GAIN:
                    tag, _ = HOUSE_GAIN[h]
                    add_source(tag, f"{planet} rules {h}H active in dasha", 2)
            if cat in LOSS_CATS or cat == "wealth":
                if h in HOUSE_LOSS:
                    tag, _ = HOUSE_LOSS[h]
                    add_mech(tag, f"{planet} activates {h}H loss axis", 2)
        pos = chart.get("positions", {}).get(planet, {})
        ph = pos.get("house")
        if ph:
            houses.append(ph)
            if ph in HOUSE_GAIN and cat in WEALTH_CATS | CAREER_CATS:
                tag, _ = HOUSE_GAIN[ph]
                add_source(tag, f"{planet} in H{ph}", 1)
            if ph in HOUSE_LOSS and cat in LOSS_CATS:
                tag, _ = HOUSE_LOSS[ph]
                add_mech(tag, f"{planet} placed in H{ph}", 2)
        if planet in PLANET_SOURCE:
            tag, reason = PLANET_SOURCE[planet]
            if cat in WEALTH_CATS | CAREER_CATS:
                add_source(tag, reason, 1)
            elif cat in LOSS_CATS and planet in ("Rahu", "Ketu", "Saturn"):
                add_mech(tag if tag in MECHANISM_TA else "delay", reason, 1)

    for h in houses:
        if cat in WEALTH_CATS | CAREER_CATS and h in HOUSE_GAIN:
            tag, reason = HOUSE_GAIN[h]
            add_source(tag, reason, 1)
        if cat in LOSS_CATS and h in HOUSE_LOSS:
            tag, reason = HOUSE_LOSS[h]
            add_mech(tag, reason, 2)
        if cat in MARRIAGE_CATS and h == 7:
            add_source("spouse", "7th house / partnership axis", 2)

    if cat in WEALTH_CATS:
        for h in (2, 11):
            if lord_of_house(chart, h) in (md, ad):
                tag, _ = HOUSE_GAIN[h]
                add_source(tag, f"{h}L ({lord_of_house(chart, h)}) dasha", 2)
        if chart.get("positions", {}).get("Mars", {}).get("house") in (4, 5):
            add_source("land", "Mars 4th/5th property-creative axis", 1)
        if chart.get("positions", {}).get("Mercury", {}).get("house") == 5:
            add_source("business", "Mercury in 5th trade / communication earn", 1)
    elif cat in LOSS_CATS:
        for h in (6, 8, 12):
            if lord_of_house(chart, h) in (md, ad):
                tag, _ = HOUSE_LOSS[h]
                add_mech(tag, f"{h}L ({lord_of_house(chart, h)}) period", 2)
        if md == "Rahu" or ad == "Rahu":
            add_mech("fraud", "Rahu speculation / over-leverage risk", 2)
        if md == "Saturn" or ad == "Saturn":
            add_mech("delay", "Saturn delayed payment / blocked liquidity", 1)
    elif cat in CAREER_CATS:
        l10 = lord_of_house(chart, 10)
        add_source("salary", f"10L {l10} profession channel", 1)
        h10l = chart.get("positions", {}).get(l10, {}).get("house")
        if h10l in HOUSE_GAIN:
            tag, _ = HOUSE_GAIN[h10l]
            add_source(tag, f"10th lord {l10} in H{h10l}", 2)
        if l10 == "Mercury":
            add_source("business", "Mercury 10L IT / writing / contracts", 2)
    elif cat in MARRIAGE_CATS:
        add_source("spouse", "7th house / Venus partnership", 2)
        if chart.get("positions", {}).get("Venus", {}).get("house") == 7:
            add_source("spouse", "Venus in 7th partner-led union", 2)
    elif cat == "father":
        add_mech("family_expense", "9th / Sun father-life event", 1)
        if md == "Ketu" or ad in ("Saturn", "Ketu"):
            add_mech("delay", "Ketu-Saturn 4th paternal / home stress", 1)

    why_text = " ".join(str(w) for w in why_list).lower()
    if "legal" in why_text or "6l" in why_text:
        add_mech("legal", "6th-house legal / dispute", 1)
    if "debt" in why_text or "12l" in why_text:
        add_mech("abroad_drain", "12th-house leakage", 1)
    if "specul" in why_text or "rahu" in why_text:
        add_mech("market", "speculative / Rahu channel", 1)
    if "property" in why_text or "4l" in why_text:
        add_source("land", "4th-house property activation", 2)
    if "jupiter" in why_text:
        add_source("grace", "Jupiter expansion", 1)

    houses = sorted(set(houses))
    conf = _confidence(score, len(source_tags) + len(mechanism_tags))

    mech_ta = "; ".join(MECHANISM_TA.get(t, SOURCE_TA.get(t, t)) for t in mechanism_tags[:3])

    if cat == "father":
        client_en = (
            f"Father-life window: {_tags_line(mechanism_tags, 'en') or '9th house / Sun axis'} "
            f"({'; '.join(mechanism_bits[:2])}). {DISCLAIMER_EN}"
        )
        client_ta = (
            f"{_t(0xba4, 0xba8, 0xbcd, 0xba4, 0xbc8)}: {_tags_line(mechanism_tags, 'ta') or _t(0xb95, 0xbc1, 0xbb0, 0xbc1)} "
            f"({'; '.join(mechanism_bits[:2])[:50]}). {DISCLAIMER_TA}"
        )
        return {
            "source_tags": source_tags,
            "mechanism_tags": mechanism_tags,
            "mechanism_en": "; ".join(mechanism_bits[:4]),
            "client_en": client_en,
            "client_ta": client_ta,
            "houses": houses,
            "confidence": conf,
        }

    if cat in LOSS_CATS:
        mech_line = "; ".join(mechanism_bits[:3]) or "dusthana lord activation"
        client_en = (
            f"Likely loss channel: {_tags_line(mechanism_tags, 'en') or 'general drain'} "
            f"({mech_line}). {DISCLAIMER_EN}"
        )
        client_ta = (
            f"{LABEL_LOSS_TA} {_tags_line(mechanism_tags, 'ta') or _t(0xb9a, 0xbc6, 0xbb2, 0xbb5, 0xbc1)} "
            f"({mech_line[:50]}). {DISCLAIMER_TA}"
        )
    else:
        src_line = "; ".join(mechanism_bits[:3]) or "house-lord + dasha"
        client_en = (
            f"Likely source: {_tags_line(source_tags, 'en') or 'mixed channels'} "
            f"({src_line}). {DISCLAIMER_EN}"
        )
        client_ta = (
            f"{LABEL_GAIN_TA} {_tags_line(source_tags, 'ta') or _t(0xb9a, 0xbc6, 0xbb2, 0xbcd, 0xbb5, 0xbae, 0xbcd)} "
            f"({src_line[:50]}). {DISCLAIMER_TA}"
        )

    return {
        "source_tags": source_tags,
        "mechanism_tags": mechanism_tags,
        "mechanism_en": "; ".join(mechanism_bits[:4]),
        "mechanism_ta": mech_ta,
        "client_en": client_en,
        "client_ta": client_ta,
        "houses": houses,
        "confidence": conf,
    }


def narrative_for_band(chart: dict, band: dict, dasha_ctx: dict | None = None) -> dict:
    cat = band.get("category", "")
    why = band.get("max_why") or band.get("why") or []
    return infer_source_and_mechanism(chart, cat, why, dasha_ctx)


def format_source_mechanism_cell(narr: dict) -> str:
    en = (narr.get("client_en") or "")[:100]
    ta = (narr.get("client_ta") or "")[:100]
    return f"{ta} | {en}"


def is_life_event_band(band: dict) -> bool:
    """Prefer life-domain bands over long generic auxiliary events in puthi tables."""
    cat = (band.get("category") or "").lower()
    ev = (band.get("event") or "").lower()
    if cat in CAT_PRIORITY_LIFE:
        return True
    if "event" in ev and cat not in CAT_PRIORITY_LIFE:
        if any(x in ev for x in ("bazi", "d60", "d30", "mayan", "zi wei", "numerology", "kala sarpa", "mouth / lip", "birth-mark", "sibling health", "ardha ashtam")):
            return False
    return cat not in {"", "general"}


CAT_PRIORITY_LIFE = frozenset({
    "father", "mother", "health", "health_self", "self_accident", "saham_roga",
    "marriage", "engagement", "relationship_phase", "saham_kalatra",
    "career", "promotion", "career_breakthrough", "leadership_emergence",
    "wealth", "wealth_peak", "wealth_loss", "education", "travel", "children", "property",
})


def aggregate_puthi_summary(
    chart: dict,
    bands: list[dict],
    md: str,
    ad: str,
    lang: str,
) -> dict[str, list[str]]:
    ctx = {"md": md, "ad": ad}
    income: list[str] = []
    losses: list[str] = []
    career: list[str] = []
    marriage: list[str] = []
    seen: set[str] = set()

    def _add(bucket: list[str], line: str):
        if line and line not in seen:
            seen.add(line)
            bucket.append(line)

    for b in bands:
        cat = b.get("category", "")
        narr = narrative_for_band(chart, b, ctx)
        if cat in WEALTH_CATS:
            _add(income, narr["client_ta"] if lang == "ta" else narr["client_en"])
        elif cat in LOSS_CATS:
            _add(losses, narr["client_ta"] if lang == "ta" else narr["client_en"])
        elif cat in CAREER_CATS:
            _add(career, narr["client_ta"] if lang == "ta" else narr["client_en"])
        elif cat in MARRIAGE_CATS:
            _add(marriage, narr["client_ta"] if lang == "ta" else narr["client_en"])

    if not income:
        base = infer_source_and_mechanism(chart, "wealth", [], ctx)
        _add(income, base["client_ta"] if lang == "ta" else base["client_en"])
    if not losses:
        base = infer_source_and_mechanism(chart, "wealth_loss", [], ctx)
        _add(losses, base["client_ta"] if lang == "ta" else base["client_en"])

    return {
        "income": income[:4],
        "losses": losses[:4],
        "career": career[:3],
        "marriage": marriage[:3],
    }


def summarize_puthi_narrative(
    chart: dict,
    md: str,
    ad: str,
    event_bands: list[dict] | None = None,
) -> dict[str, str]:
    """Single-line TA/EN summaries for puthi header blocks."""
    bands = event_bands or []
    agg = aggregate_puthi_summary(chart, bands, md, ad, "en")
    agg_ta = aggregate_puthi_summary(chart, bands, md, ad, "ta")
    ctx = {"md": md, "ad": ad}
    base_w = infer_source_and_mechanism(chart, "wealth", [], ctx)
    base_l = infer_source_and_mechanism(chart, "wealth_loss", [], ctx)

    def _join(lines: list[str], fallback: str) -> str:
        return "; ".join(lines[:3]) if lines else fallback

    has_career = any((b.get("category") or "") in CAREER_CATS for b in bands)
    has_marriage = any((b.get("category") or "") in MARRIAGE_CATS for b in bands)

    return {
        "income_en": _join(agg["income"], base_w["client_en"]),
        "income_ta": _join(agg_ta["income"], base_w["client_ta"]),
        "loss_en": _join(agg["losses"], base_l["client_en"]),
        "loss_ta": _join(agg_ta["losses"], base_l["client_ta"]),
        "career_en": _join(agg["career"], "") if has_career else "",
        "career_ta": _join(agg_ta["career"], "") if has_career else "",
        "marriage_en": _join(agg["marriage"], "") if has_marriage else "",
        "marriage_ta": _join(agg_ta["marriage"], "") if has_marriage else "",
        "has_career": has_career,
        "has_marriage": has_marriage,
    }
