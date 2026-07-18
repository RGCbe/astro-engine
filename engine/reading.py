"""
Auto-narrative reading layer.

Takes a Chart object (engine.chart.compute_chart) and produces a structured
prose reading by matching computed conditions to the canonical rule corpus
(rules_canonical_v5.json), preserving citations.

API:
    reading = generate_reading(chart, top_n=20)
    print(reading.to_markdown())
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from engine.evaluator import evaluate_planet

ROOT = Path(__file__).parent.parent
RULES_PATH = ROOT / "_workbench" / "_dedup_canonical.json"

# Tier ordering — higher = preferred
TIER_RANK = {"CANONICAL": 4, "STRONG": 3, "MODERATE": 2, "ANECDOTAL": 1}


@dataclass
class MatchedRule:
    cluster_id: int
    canonical_text: str
    tier: str
    school: str
    authority_score: float
    n_books: int
    books: list[str]
    bucket: str
    matched_keywords: list[str]


@dataclass
class ReadingSection:
    title: str
    chart_facts: list[str]
    matched_rules: list[MatchedRule]


@dataclass
class Reading:
    chart_name: str
    sections: list[ReadingSection]

    def to_markdown(self) -> str:
        out = [f"# Reading for {self.chart_name or '(unnamed)'}\n"]
        for s in self.sections:
            out.append(f"## {s.title}\n")
            if s.chart_facts:
                for fact in s.chart_facts:
                    out.append(f"- {fact}")
                out.append("")
            if s.matched_rules:
                out.append(f"**Classical sources:**\n")
                for r in s.matched_rules[:8]:
                    cite = ", ".join(r.books[:4])
                    out.append(f"- *[{r.tier}]* {r.canonical_text}  \n"
                               f"  └ {cite} (auth={r.authority_score})")
                out.append("")
            else:
                out.append("_No matching canonical rules found._\n")
        return "\n".join(out)


@lru_cache(maxsize=1)
def _load_rules() -> list[dict]:
    data = json.load(open(RULES_PATH, encoding="utf-8"))
    
    # Check if this is the flat array from _dedup_canonical.json
    if isinstance(data, list):
        out = []
        for i, c in enumerate(data):
            # Transform to the format expected by reading.py
            text = f"{c.get('trigger', '')} => {c.get('effect', '')}"
            out.append({
                "id": i,
                "canonical_text": text,
                "tier": c.get("confidence", "ANECDOTAL"),
                "school": c.get("canonical_book", "Unknown"),
                "authority_score": c.get("authority_score", 0.0),
                "n_books": c.get("n_books", 1),
                "books": c.get("books", []),
                "bucket": ""
            })
        return out
        
    return data.get("canonical", [])


_PLANET_ALIASES = {
    "Sun":     ["sun", "surya", "ravi", "aditya"],
    "Moon":    ["moon", "chandra", "soma"],
    "Mars":    ["mars", "mangal", "kuja", "angaraka"],
    "Mercury": ["mercury", "budha", "buddha"],
    "Jupiter": ["jupiter", "guru", "brihaspati", "bṛhaspati"],
    "Venus":   ["venus", "shukra", "śukra"],
    "Saturn":  ["saturn", "shani", "śani"],
    "Rahu":    ["rahu", "rāhu"],
    "Ketu":    ["ketu", "ketu"],
}
_HOUSE_ORDS = ("1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th",
                "9th", "10th", "11th", "12th")
_HOUSE_NUM = {o: i + 1 for i, o in enumerate(_HOUSE_ORDS)}


def _rule_applies_to_chart(text: str, chart) -> bool | None:
    """Cheap applicability gate. Returns False if the rule clearly
    references a planet-in-house placement that contradicts this chart;
    True if it's a known match; None if ambiguous."""
    lo = text.lower()
    decided = None
    for canon, aliases in _PLANET_ALIASES.items():
        for alias in aliases:
            if alias not in lo:
                continue
            for ord_str in _HOUSE_ORDS:
                claimed_house = _HOUSE_NUM[ord_str]
                num = str(claimed_house)
                # Match: "Mars in 5th [house]" / "Mars in the 5th" / "Mars in house 5" /
                # "Mars in 5th, 7th, 9th" / "Venus in house 2, 5, or 11"
                patterns = [
                    rf"\b{re.escape(alias)}\b[^.]{{0,40}}?\bin (?:the )?{ord_str}\b",
                    rf"\b{re.escape(alias)}\b[^.]{{0,40}}?\bin house {num}\b",
                    rf"\b{re.escape(alias)}\b[^.]{{0,40}}?\bin houses?\b[^.]{{0,40}}?\b{num}\b",
                ]
                if any(re.search(p, lo) for p in patterns):
                    actual_lon = chart.positions.get(canon)
                    if actual_lon is None:
                        continue
                    actual_house = ((int(actual_lon // 30) -
                                     int(chart.lagna_lon // 30)) % 12) + 1
                    if actual_house == claimed_house:
                        decided = True
                    else:
                        # Any contradiction → fail closed
                        return False
    return decided


# Keyword denylist — rules containing these come from non-natal contexts
# (Prashna/Muhurta/horary) or Western astrology and should NOT surface in
# a natal reading.
_DENY_KEYWORDS = (
    # Prashna / horary — query-time, not natal
    "prasna", "prashna", "questioner", "horary", "the question",
    "annual chart", "tajik", "muntha", "varshaphal",
    # Muhurta — electional, not natal
    "muhurta", "muhurtha", "electional", "haircutting",
    # Military / political horary
    "invader", "war", "battle of", "victorious in", "chora prasna",
    "theft", "lost article",
    # Imprisonment / extreme judicial
    "imprisonment", "prisoner",
    # Western astrology
    "neptune", "uranus", "pluto",
    # Triplet / specialised birth-prediction
    "triplets", "twins", "stillborn",
    # Death-finality without conditioning
    "rigorous imprisonment",
)


def _passes_denylist(text: str) -> bool:
    """True if rule text doesn't trip any deny-keyword."""
    lo = text.lower()
    return not any(k in lo for k in _DENY_KEYWORDS)


def _is_garbled_transliteration(text: str) -> bool:
    """Drop rules with broken Sanskrit ITRANS like 'n¨u¨a tqnk' or
    rules that are mostly Devanagari without English translation."""
    # If text has unicode replacement chars or 30%+ non-ASCII, drop
    if "¨" in text or "©" in text:
        return True
    non_ascii = sum(1 for ch in text if ord(ch) > 127)
    return non_ascii > len(text) * 0.30


def _match(query_keywords: list[str], school: str | None = None,
           limit: int = 8, min_tier: str = "ANECDOTAL",
           chart=None,
           require_natal: bool = True,
           extra_deny: list[str] | None = None) -> list[MatchedRule]:
    """Find canonical clusters whose text contains ALL query_keywords.

    Filters applied (in order):
        1. Tier ≥ min_tier
        2. School (if given)
        3. ALL query_keywords present
        4. (if require_natal) deny-list — drops Prashna/Muhurta/Western/garbled
        5. (if chart given) applicability gate — drops contradicting placements
        6. (extra_deny) per-section additional denied keywords
    """
    rules = _load_rules()
    min_rank = TIER_RANK[min_tier]
    out: list[MatchedRule] = []
    pat_list = [re.compile(re.escape(k), re.IGNORECASE) for k in query_keywords]
    extra_deny_lc = [k.lower() for k in (extra_deny or [])]
    for c in rules:
        if school and c.get("school") != school:
            continue
        if TIER_RANK.get(c.get("tier", "ANECDOTAL"), 1) < min_rank:
            continue
        text = c["canonical_text"]
        if not all(p.search(text) for p in pat_list):
            continue
        if require_natal:
            if not _passes_denylist(text):
                continue
            if _is_garbled_transliteration(text):
                continue
        if extra_deny_lc:
            lo = text.lower()
            if any(k in lo for k in extra_deny_lc):
                continue
        if chart is not None and _rule_applies_to_chart(text, chart) is False:
            continue
        out.append(MatchedRule(
            cluster_id=c["id"],
            canonical_text=text,
            tier=c["tier"],
            school=c.get("school", ""),
            authority_score=c.get("authority_score", 0.0),
            n_books=c["n_books"],
            books=c["books"],
            bucket=c.get("bucket", ""),
            matched_keywords=query_keywords,
        ))
        
        if len(text) < 50:
            out[-1].canonical_text += " ⚠️ [Engine Warning: Potential OCR fragment/short rule (<50 chars). Verify context.]"
        
        # Phase IV Evaluator Layer
        if chart is not None and hasattr(chart, 'lagna_lon') and hasattr(chart, 'positions'):
            for canon, aliases in _PLANET_ALIASES.items():
                if any(alias in text.lower() for alias in aliases) and canon in chart.positions:
                    rasi_names = ["Mesham", "Rishabam", "Mithunam", "Kadagam", "Simmam", "Kanni", "Thulaam", "Viruchigam", "Dhanusu", "Makaram", "Kumbam", "Meenam"]
                    
                    actual_lon = chart.positions[canon]
                    p_rasi = rasi_names[int(actual_lon // 30) % 12]
                    asc_rasi = rasi_names[int(chart.lagna_lon // 30) % 12]
                    
                    eval_res = evaluate_planet(asc_rasi, canon, p_rasi, chart)
                    if eval_res["caveat"]:
                        out[-1].canonical_text += eval_res["caveat"]
                    break # Only evaluate the primary planet mentioned
                    
    if chart is not None:
        out.sort(key=lambda r: (
            0 if _rule_applies_to_chart(r.canonical_text, chart) is True else 1,
            -TIER_RANK[r.tier], -r.authority_score, -r.n_books,
        ))
    else:
        out.sort(key=lambda r: (-TIER_RANK[r.tier], -r.authority_score,
                                 -r.n_books))
    return out[:limit]


# ─── Section builders ─────────────────────────────────────────────────────
def _section_lagna(chart) -> ReadingSection:
    facts = [
        f"Lagna (Ascendant): **{chart.lagna_sign}** at {chart.lagna_lon:.2f}°",
        f"Lagna lord: **{chart.lagna_lord}** "
        f"(placed in {chart.house_of[chart.lagna_lord]}th house, "
        f"in sign {chart.nakshatras[chart.lagna_lord]['sign']})",
        f"Lagna nakshatra: **{chart.lagna_nakshatra}**",
    ]
    # Personality-only: drop horary/election (already in deny-list) plus
    # event-specific rules (marriage, career, death) — keep nature/body rules.
    DENY_LAGNA = ["spouse", "wife", "husband", "marriage will",
                  "career and profession", "stillborn",
                  "abortive", "loss of mother", "loss of father"]
    rules = _match([chart.lagna_sign, "ascendant"], min_tier="MODERATE",
                   chart=chart, extra_deny=DENY_LAGNA)
    rules += _match([chart.lagna_lord, "lagna"], min_tier="MODERATE",
                    chart=chart, extra_deny=DENY_LAGNA)[:3]
    return ReadingSection("🧬 Self & Personality (Lagna)", facts, rules)


def _section_moon(chart) -> ReadingSection:
    moon_sign = chart.nakshatras["Moon"]["sign"]
    moon_nak = chart.nakshatras["Moon"]["name"]
    facts = [
        f"Moon (Janma rasi): **{moon_sign}**",
        f"Janma nakshatra: **{moon_nak}** pada {chart.nakshatras['Moon']['pada']}",
        f"Nakshatra lord: **{chart.nakshatras['Moon']['lord']}**",
        f"Moon house: **{chart.house_of['Moon']}**",
    ]
    DENY_MOON = ["marriage", "spouse", "career", "profession",
                  "death", "danger to life", "run over",
                  "diseases:", "cuspal", "sub-lord", "sub lord"]
    rules = _match(["Moon", moon_sign], min_tier="STRONG",
                   chart=chart, extra_deny=DENY_MOON)
    rules += _match([moon_nak], min_tier="MODERATE",
                    chart=chart, extra_deny=DENY_MOON)[:3]
    return ReadingSection("🌙 Mind & Emotions (Moon)", facts, rules)


def _section_career(chart) -> ReadingSection:
    sign_idx = int(chart.lagna_lon // 30)
    h10_sign = ("Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio "
                "Sagittarius Capricorn Aquarius Pisces").split()[(sign_idx + 9) % 12]
    facts = [
        f"10th house sign: **{h10_sign}**",
        f"Sun house: **{chart.house_of['Sun']}** (career visibility)",
        f"Saturn house: **{chart.house_of['Saturn']}** (work discipline)",
    ]
    DENY_CAREER = ["marriage", "spouse", "wife", "husband",
                   "child", "stillborn", "abortive"]
    rules = _match(["10th house"], min_tier="STRONG",
                   chart=chart, extra_deny=DENY_CAREER)[:5]
    rules += _match(["career"], min_tier="MODERATE",
                    chart=chart, extra_deny=DENY_CAREER)[:3]
    return ReadingSection("💼 Career (10th)", facts, rules)


def _section_marriage(chart) -> ReadingSection:
    sign_idx = int(chart.lagna_lon // 30)
    h7_sign = ("Aries Taurus Gemini Cancer Leo Virgo Libra Scorpio "
               "Sagittarius Capricorn Aquarius Pisces").split()[(sign_idx + 6) % 12]
    facts = [
        f"7th house sign: **{h7_sign}**",
        f"Venus (kalatra-karaka) house: **{chart.house_of['Venus']}**",
        f"Jupiter (for women) house: **{chart.house_of['Jupiter']}**",
    ]
    DENY_MARRIAGE = ["career", "profession", "10th house",
                     "career and profession", "stillborn"]
    rules = _match(["spouse"], min_tier="STRONG",
                   chart=chart, extra_deny=DENY_MARRIAGE)[:5]
    rules += _match(["marriage"], min_tier="STRONG",
                    chart=chart, extra_deny=DENY_MARRIAGE)[:3]
    return ReadingSection("💑 Marriage (7th, D9)", facts, rules)


def _section_yogas(chart) -> ReadingSection:
    facts = []
    if not chart.yogas:
        facts.append("No major named yogas auto-detected.")
    else:
        for y in chart.yogas[:10]:
            mark = "⭐" if y.is_strong else "⚠️"
            facts.append(f"{mark} **{y.name}** — {y.description}")
    return ReadingSection("✨ Yogas Detected", facts, [])


def _section_afflictions(chart) -> ReadingSection:
    """Per mission directive: surface ALL detected bad. No softening."""
    from engine.afflictions import detect_all
    afflictions = detect_all(chart)
    facts = [f"**Total afflictions detected: {len(afflictions)}**", ""]
    if not afflictions:
        facts.append("_No major classical afflictions detected — but reader should still verify dasha-anti-event signals below._")
        return ReadingSection("⚠️ Afflictions (the Bad — fully surfaced)", facts, [])
    by_severity: dict[str, list] = {}
    for a in afflictions:
        by_severity.setdefault(a.severity, []).append(a)
    for sev in ("CRITICAL", "HIGH", "MODERATE", "LOW"):
        items = by_severity.get(sev, [])
        if not items:
            continue
        facts.append(f"**[{sev}]**")
        for a in items:
            facts.append(f"- **{a.name}** — {a.description}")
            facts.append(f"  *Evidence:* {a.evidence}  ·  *Source:* {a.classical_source}")
        facts.append("")
    return ReadingSection("⚠️ Afflictions (the Bad — fully surfaced)", facts, [])


def _section_extended_yogas(chart) -> ReadingSection:
    """Phaladeepika/BPHS extended yogas — Bhava-yogas, Parivartana, Apakartari etc."""
    from engine.yogas_extended import detect_all_extended
    yogas = detect_all_extended(chart)
    facts = [f"**{len(yogas)} extended classical yogas detected** (Phaladeepika + BPHS Ch.36):", ""]
    if not yogas:
        facts.append("_No extended yogas detected._")
        return ReadingSection("📜 Extended Classical Yogas (Phaladeepika/BPHS)", facts, [])
    by_valence: dict[str, list] = {}
    for y in yogas:
        by_valence.setdefault(y.valence, []).append(y)
    for valence, label in (("GOOD", "✨ GOOD"), ("MIXED", "🔄 MIXED"), ("BAD", "⚠️ BAD")):
        items = by_valence.get(valence, [])
        if not items:
            continue
        facts.append(f"**{label}**")
        for y in items:
            facts.append(f"- **{y.name}** [{y.strength}] — {y.description}")
            facts.append(f"  *Evidence:* {y.evidence}  ·  *Source:* {y.classical_source}")
            if y.activation_or_remedy:
                facts.append(f"  *Action:* {y.activation_or_remedy}")
        facts.append("")
    return ReadingSection("📜 Extended Classical Yogas (Phaladeepika/BPHS)", facts, [])


def _section_blessings(chart) -> ReadingSection:
    """Symmetric to afflictions — surface ALL detected good with equal rigor."""
    from engine.blessings import detect_all
    blessings = detect_all(chart)
    facts = [f"**Total blessings detected: {len(blessings)}**", ""]
    if not blessings:
        facts.append("_No major classical positive yogas detected._")
        return ReadingSection("✨ Blessings (the Good — equally surfaced)", facts, [])
    by_strength: dict[str, list] = {}
    for b in blessings:
        by_strength.setdefault(b.strength, []).append(b)
    for s in ("SUPREME", "STRONG", "MODERATE", "LATENT"):
        items = by_strength.get(s, [])
        if not items:
            continue
        facts.append(f"**[{s}]**")
        for b in items:
            facts.append(f"- **{b.name}** — {b.description}")
            facts.append(f"  *Evidence:* {b.evidence}  ·  *Source:* {b.classical_source}")
            if b.activation:
                facts.append(f"  *Activation:* {b.activation}")
        facts.append("")
    return ReadingSection("✨ Blessings (the Good — equally surfaced)", facts, [])


def _section_remedies(chart) -> ReadingSection:
    """Concrete remedies for each detected affliction."""
    from engine.remedies import remedies_for_chart
    from engine.remedies_verbatim import remedies_for_affliction_code
    plan = remedies_for_chart(chart)
    facts = []
    if plan["n_afflictions_detected"] == 0:
        facts.append("_No remedies needed — engine detected no qualifying afflictions._")
        return ReadingSection("🔧 Remedies (paired to each affliction)", facts, [])
    for entry in plan["afflictions_with_remedies"]:
        a = entry["affliction"]
        facts.append(f"**[{a['severity']}] {a['name']}** — {a['description']}")
        if entry["remedies"]:
            for r in entry["remedies"]:
                when_str = f" ({r['when']})" if r["when"] else ""
                duration_str = f" · {r['duration']}" if r["duration"] else ""
                caveat_str = f"  ⚠️ *{r['caveat']}*" if r["caveat"] else ""
                facts.append(f"  - **{r['type']}**: {r['action']}{when_str}{duration_str}{caveat_str}")
        else:
            facts.append("  *(No specific remedy table entry for this affliction; consult astrologer.)*")
        # Append verbatim classical citations where available
        affected = a.get("affected") or a.get("involves") or []
        # Keep only planet names (filter out house numbers, signs, etc.)
        planet_names = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                        "Saturn", "Rahu", "Ketu"}
        planets = [x for x in affected if x in planet_names]
        verbatim = remedies_for_affliction_code(a["code"], planets)
        for vr in verbatim[:3]:
            snippet = vr.text.replace("\n", " ").strip()
            if len(snippet) > 220:
                snippet = snippet[:217] + "…"
            facts.append(f"  - 📜 *Verbatim — {vr.cite()}:* {snippet}")
        facts.append("")
    if plan.get("weakest_planets_generic_remedies"):
        facts.append("**Weakest-planet remedies (auxiliary):**")
        for entry in plan["weakest_planets_generic_remedies"]:
            facts.append(f"- *{entry['planet']}*: " + "; ".join(r["action"] for r in entry["remedies"][:3]))
    return ReadingSection("🔧 Remedies (paired to each affliction)", facts, [])


def _section_dasha(chart) -> ReadingSection:
    facts = [
        f"Currently running: **{chart.current_md} mahadasha** "
        f"(ends {chart.current_md_end})",
        f"Antardasha: **{chart.current_ad}**",
        "",
        "Vimshottari sequence (next 5 mahadashas):",
    ]
    for md in chart.vimshottari_periods[:5]:
        yrs = md.duration_days / 365.25
        facts.append(f"  - **{md.lord}** {md.start.date()} → {md.end.date()} ({yrs:.2f} yrs)")
    rules = _match([f"{chart.current_md} dasha"], min_tier="ANECDOTAL", chart=chart)[:5]
    return ReadingSection("⏳ Current Dasha & Timing", facts, rules)


def _section_vargas(chart) -> ReadingSection:
    """Divisional-chart readings — D9 (spouse), D10 (career), D24 (education),
    D60 (past life). Each varga shows planet → sign and lagna placement.

    Truth-only: vargottama planets (same sign in D1 and D9) get a confidence
    boost; planets that change sign drastically (e.g. exalted in D1 but
    debilitated in D9) get a downgrade flag.
    """
    facts = []
    varga_meanings = {
        "D9":  "Spouse / dharma / latent strength (Navamsa)",
        "D10": "Career / public role (Dasamsa)",
        "D24": "Education / learning (Chaturvimshamsa)",
        "D60": "Past karma / fine-grained reading (Shashtiamsa)",
    }
    for varga, label in varga_meanings.items():
        facts.append(f"\n**{varga} — {label}:**")
        for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                       "Venus", "Saturn", "Rahu", "Ketu"):
            d1_sign = chart.vargas.get(planet, {}).get("D1", {}).get("sign")
            v_sign = chart.vargas.get(planet, {}).get(varga, {}).get("sign")
            if not v_sign:
                continue
            flag = ""
            if varga == "D9" and d1_sign and d1_sign == v_sign:
                flag = " ⭐ vargottama"
            facts.append(f"  - {planet}: {v_sign}{flag}")

    # Vargottama summary
    if chart.vargottama:
        facts.append("")
        facts.append(f"**Vargottama planets (D1=D9):** {', '.join(chart.vargottama)} — "
                     f"these planets carry their D1 strength fully into the navamsa.")
    else:
        facts.append("")
        facts.append("No vargottama planets — D1 strengths do not double in D9.")

    rules = _match(["Navamsa", "spouse"], min_tier="MODERATE", chart=chart)[:5]
    return ReadingSection("🔢 Divisional Charts (D9 / D10 / D24 / D60)", facts, rules)


def _section_calibrated_forecasts(chart) -> ReadingSection:
    """LR-calibrated forecasts for major event types in the current MD-AD.

    Per the truth-only directive: every event type is reported with its
    Bayesian posterior + likelihood ratio. LOW/WEAK bands are surfaced
    as plainly as HIGH bands. No flattering language hides weak signals.
    Where classical karaka theory disagrees with the data, both are shown.
    """
    from engine.calibration import forecast_confidence
    from engine.tier_refit import compare as compare_classical

    md, ad = chart.current_md, chart.current_ad
    facts = [
        f"Forecasts below are Bayesian-calibrated against 92 documented events "
        f"across 20 famous charts.",
        f"Active period: **{md}** mahadasha / **{ad}** antardasha.",
        "",
        "**Per-event signature in current MD-AD:**",
    ]

    event_types = [
        "MARRIAGE", "CHILDREN_BORN", "CAREER_PEAK", "FOUND_BUSINESS",
        "POLITICAL_OFFICE", "AWARD", "HEALTH_CRISIS", "MAJOR_LOSS",
        "DIVORCE", "DEATH",
    ]
    for evt in event_types:
        f = forecast_confidence(evt, md, ad)
        band = f["confidence_band"]
        post = f.get("bayesian_posterior")
        lr = f.get("likelihood_ratio")
        post_str = f"{post:.3f}" if post is not None else "n/a"
        lr_str = f"{lr}" if lr is not None else "n/a"
        # Truth-only formatting — no euphemisms
        emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "⚪", "WEAK": "⚫"}.get(band, "•")
        facts.append(
            f"{emoji} **{evt}**: band={band}, "
            f"posterior=**{post_str}**, LR={lr_str}  \n"
            f"  └ {f.get('interpretation','')}"
        )

    # Where classical theory disagrees with data — surface both
    facts.append("")
    facts.append("**Where the data contradicts classical karaka theory** "
                 "(empirical refit from negative-sample backtest):")
    surprises = ["DEATH", "CHILDREN_BORN", "POLITICAL_OFFICE", "FOUND_BUSINESS"]
    for evt in surprises:
        c = compare_classical(evt)
        if "error" in c:
            continue
        if c["newly_dropped"] or c["promoted_to_primary"]:
            facts.append(
                f"- **{evt}**: classical primary={c['classical_primary']}; "
                f"empirical primary={c['empirical_primary']}. "
                f"{c['interpretation']}"
            )

    return ReadingSection("🎯 Calibrated Forecasts (truth-only)", facts, [])


def _section_kp(chart) -> ReadingSection:
    """Verbatim KP_Reader_3_Predictive rules per house."""
    from engine.kp_predictions import predictions_for_chart
    rows = predictions_for_chart(chart, max_per_house=2)
    facts = []
    if not rows:
        facts.append("_No KP rules indexed for this chart's placements._")
        return ReadingSection("🔮 KP House Predictions (Krishnamurti Paddhati)", facts, [])
    for row in rows:
        sl = f" · sub-lord: {row['sub_lord']}" if row.get("sub_lord") else ""
        facts.append(f"**House {row['house']}**{sl}:")
        for pred in row["predictions"]:
            txt = pred["text"].replace("\n", " ").strip()
            if len(txt) > 220:
                txt = txt[:217] + "…"
            facts.append(f"  - 🔮 *{pred['citation']}* — {txt}")
        facts.append("")
    return ReadingSection("🔮 KP House Predictions (Krishnamurti Paddhati)", facts, [])


def _section_bhrigu(chart) -> ReadingSection:
    """Verbatim Bhrigu_Samhita planet-in-house outcome verses."""
    from engine.bhrigu_predictions import predictions_for_chart
    rows = predictions_for_chart(chart, max_per_planet=3)
    facts = []
    if not rows:
        facts.append("_No Bhrigu rules indexed for this chart's placements._")
        return ReadingSection("📜 Bhrigu Nadi point predictions", facts, [])
    for row in rows:
        facts.append(f"**{row['planet']} in H{row['house']}**:")
        for pred in row["predictions"]:
            txt = pred["text"].replace("\n", " ").strip()
            if len(txt) > 240:
                txt = txt[:237] + "…"
            facts.append(f"  - 📜 *{pred['citation']}* — {txt}")
        facts.append("")
    return ReadingSection("📜 Bhrigu Nadi point predictions", facts, [])


def _section_strength(chart) -> ReadingSection:
    facts = [
        f"Strongest planets: **{', '.join(chart.bala_summary['strongest'])}**",
        f"Weakest planets: **{', '.join(chart.bala_summary['weakest'])}**",
    ]
    if chart.vargottama:
        facts.append(f"Vargottama (extra strong): **{', '.join(chart.vargottama)}**")
    return ReadingSection("💪 Planetary Strength", facts, [])


# ─── Public API ───────────────────────────────────────────────────────────
def generate_reading(chart) -> Reading:
    """Mission-aligned section ordering:
    1-2. Foundation: lagna + moon
    3.   Strength
    4.   AFFLICTIONS (bad — fully surfaced)
    5.   BLESSINGS (good — equally surfaced, symmetric)
    6.   FORECASTS (calibrated, all events)
    7.   REMEDIES (paired to afflictions)
    8.   Career, marriage, vargas, dasha (specific domain readings)
    9.   Yogas index (legacy summary)
    """
    sections = [
        _section_lagna(chart),
        _section_moon(chart),
        _section_strength(chart),
        _section_afflictions(chart),
        _section_blessings(chart),
        _section_extended_yogas(chart),
        _section_calibrated_forecasts(chart),
        _section_remedies(chart),
        _section_bhrigu(chart),
        _section_kp(chart),
        _section_career(chart),
        _section_marriage(chart),
        _section_vargas(chart),
        _section_dasha(chart),
        _section_yogas(chart),
    ]
    return Reading(chart_name=chart.name, sections=sections)
