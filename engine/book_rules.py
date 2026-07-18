"""
Book-rules engine — load classical combinations from logic_base/ALL_COMBINATIONS.json
and match them against a live Chart object, returning Predictions with citations.

Source: 1,926 indexed rules across 8 combination types extracted from 19 classical
Vedic texts (BPHS, Phaladeepika, Saravali, Hora Sara, Jataka Parijata, Prashna
Marga, Uttara Kalamrita, Jaimini Sutras, Yavanajataka, Bhrigu Samhita, etc).

Pipeline:
    rules = load_rules()                       # parse + classify per-category
    matched = match_for_chart(chart, rules)    # evaluate triggers against chart
    preds = to_predictions(matched, "marriage")  # turn into Prediction objects
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from engine.engines import Citation, Prediction, SIGNS, SIGN_LORD

# Resolve rules path — project logic_base, then legacy VPS paths
def _resolve_rules_path():
    candidates = [
        Path(__file__).resolve().parent.parent / "logic_base" / "ALL_COMBINATIONS.json",
        Path("/opt/atro/logic_base/ALL_COMBINATIONS.json"),
        Path("/opt/astro/logic_base/ALL_COMBINATIONS.json"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]

RULES_PATH = _resolve_rules_path()

# Topic routing — keyword regexes that classify a rule's "effect" text into
# one of the 15 prediction categories. A rule may belong to multiple.
TOPIC_REGEX: dict[str, re.Pattern] = {
    "marriage":     re.compile(r"\b(marriage|spouse|wife|husband|consort|wedding|marri|partner|conjugal|widow|polyga)\b", re.I),
    "career":       re.compile(r"\b(profession|occupation|career|livelihood|work|service|business|king|minister|ruler|govern|trade|employ|chief|commander|lord)\b", re.I),
    "wealth":       re.compile(r"\b(wealth|riches|money|gain|finan|opulen|treasur|prosper|gold|fortune|inherit|gem|jewel|cattle|land|grain)\b", re.I),
    "children":     re.compile(r"\b(son|daughter|child|progeny|offspring|issue|issueless|adopt)\b", re.I),
    "health":       re.compile(r"\b(disease|illness|fever|sick|wound|injury|eye|stomach|leprosy|cough|consump|diabet|heart|piles|skin|tumour|gout|rheumat|paralys)\b", re.I),
    "longevity":    re.compile(r"\b(longevity|long[- ]lived|short[- ]lived|death|die\b|dies|killed|murder|aayu|ayur|lifespan)\b", re.I),
    "spirituality": re.compile(r"\b(devot|worship|religi|god\b|gods|sage|mantra|meditat|sannyas|pilgrim|temple|sacrifice|ascetic)\b", re.I),
    "education":    re.compile(r"\b(learn|educat|scholar|knowledge|wisdom|study|literat|writ|astrolog|veda|shastra)\b", re.I),
    "foreign":      re.compile(r"\b(foreign|abroad|distant|far[- ]land|traveller|wander|migrat)\b", re.I),
    "family":       re.compile(r"\b(father|mother|brother|sister|parent|relat|kindred|kins)\b", re.I),
    "afflictions":  re.compile(r"\b(misery|grief|sorrow|suffer|loss|poverty|miser\b|sinful|trouble|enem|imprisonment|exile|defeated|disgrac)\b", re.I),
    "yogas":        re.compile(r"\b(raja yoga|dhana yoga|maha yoga|combination yields)\b", re.I),
    "personality":  re.compile(r"\b(temper|disposition|charact|appearance|complex|body|stature|noble|honour|brave|wise|valiant|harsh|cruel|generous|cunning)\b", re.I),
    "remedies":     re.compile(r"\b(remedy|propitiat|chant|donate|fast\b|ritual|gemstone|mantra of)\b", re.I),
    "timeline":     re.compile(r"\b(in the dasha of|antardasha|period of|year|age of|month of)\b", re.I),
}

PLANET_NAMES = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}

# Aspect rules — Vedic full aspects (drishti). Every planet aspects 7th house.
# Mars also aspects 4 & 8; Jupiter 5 & 9; Saturn 3 & 10.
SPECIAL_ASPECTS = {
    "Mars":    (4, 7, 8),
    "Jupiter": (5, 7, 9),
    "Saturn":  (3, 7, 10),
}


# ─── Trigger evaluation ────────────────────────────────────────────────────

def _planet_house(chart, planet: str) -> int | None:
    """Return 1..12 house occupied by planet, or None if unknown."""
    return chart.house_of.get(planet)


def _lord_of_house(chart, h: int) -> str:
    """Sign-lord of the (h)-th house from lagna."""
    sign_idx = (int(chart.lagna_lon // 30) + h - 1) % 12
    return SIGN_LORD[sign_idx]


def _aspects(chart, aspector: str, aspected: str) -> bool:
    """True if `aspector` casts a Vedic aspect onto `aspected`."""
    ha = _planet_house(chart, aspector)
    hb = _planet_house(chart, aspected)
    if ha is None or hb is None:
        return False
    diff = ((hb - ha) % 12) + 1  # houses-from-aspector counted inclusive
    if diff == 7:
        return True
    if aspector in SPECIAL_ASPECTS and diff in SPECIAL_ASPECTS[aspector]:
        return True
    return False


def _conjunct(chart, p1: str, p2: str) -> bool:
    h1 = _planet_house(chart, p1)
    h2 = _planet_house(chart, p2)
    return h1 is not None and h1 == h2


def _from_reference(chart, subject: str, count: int, reference: str) -> bool:
    """True if `subject` planet is `count`-th house from `reference` (Lagna or planet)."""
    ref_house = 1 if reference.lower() in ("ascendant", "lagna") else _planet_house(chart, reference)
    sub_house = _planet_house(chart, subject)
    if ref_house is None or sub_house is None:
        return False
    return ((sub_house - ref_house) % 12) + 1 == count


def _lord_combo(chart, from_h: int, to_h: int) -> bool:
    """True if the lord of house `from_h` is currently sitting in house `to_h`."""
    if not (1 <= from_h <= 12) or not (1 <= to_h <= 12):
        return False
    lord = _lord_of_house(chart, from_h)
    return _planet_house(chart, lord) == to_h


def _parivartana(chart, h1: int, h2: int) -> bool:
    """True if lord of h1 sits in h2 AND lord of h2 sits in h1 (mutual exchange)."""
    return _lord_combo(chart, h1, h2) and _lord_combo(chart, h2, h1)


# ─── Effect cleanup ────────────────────────────────────────────────────────

_OCR_GARBAGE = re.compile(r"[^\x20-\x7E -ɏ]+")  # keep ASCII + Latin-1 ext
_WS = re.compile(r"\s+")
_SLOKA_REF = re.compile(r"\bSloka\s*\d+\b", re.I)


def _clean_effect(raw: str, max_chars: int = 280) -> str:
    """Strip OCR glyphs, collapse whitespace, take first complete sentence(s)."""
    if not raw:
        return ""
    txt = _OCR_GARBAGE.sub(" ", raw)
    txt = _WS.sub(" ", txt).strip(" .,;:")
    # take first 1-2 sentences up to max_chars
    sentences = re.split(r"(?<=[.!?])\s+", txt)
    out = ""
    for s in sentences:
        if len(out) + len(s) > max_chars:
            break
        out = (out + " " + s).strip() if out else s
        if len(out) > 60:
            break
    if not out:
        out = txt[:max_chars]
    out = _SLOKA_REF.sub("", out).strip()
    return out


# ─── Condition tagging (tier-1 resolution) ─────────────────────────────────
# Classical phala usually carries an implicit pre-condition on the subject
# planet's dignity. Two texts that look contradictory for one placement are
# often the two arms of a single conditional ("if strong -> gains" vs "if weak
# -> loss"). We tag each rule with the branch it describes so that, for a given
# chart, only the arm matching the planet's actual strength survives.

_STRONG_MARKERS = re.compile(
    r"\b(exalt\w*|own\s+(?:sign|house|rasi|navamsa)|moola?trikona|strong|"
    r"dig[\s-]?bala|vargottama|benefic\w*|well[\s-]?placed|"
    r"aspected by (?:a |the )?benefic)\b", re.I)
_WEAK_MARKERS = re.compile(
    r"\b(debilit\w*|weak|afflict\w*|combust\w*|malefic\w*|fallen|papakartari|"
    r"enemy\s+(?:sign|house|rasi)|aspected by (?:a |the )?malefic)\b", re.I)


def _classify_condition(text: str) -> str:
    """STRONG | WEAK | NEUTRAL — which dignity branch this rule describes.

    Both markers present (e.g. "exalted but afflicted") or neither → NEUTRAL:
    not a clean single branch, so it is never filtered out.
    """
    if not text:
        return "NEUTRAL"
    strong = bool(_STRONG_MARKERS.search(text))
    weak = bool(_WEAK_MARKERS.search(text))
    if strong and not weak:
        return "STRONG"
    if weak and not strong:
        return "WEAK"
    return "NEUTRAL"


def _condition_applies(condition: str, planet_states: list[str]) -> bool:
    """Keep this rule for a chart whose subject planet has these state(s)?

    Drop only when the rule's branch is *directly contradicted* by a known
    state: a STRONG-branch rule on a planet that is WEAK (and not also STRONG),
    or vice-versa. Unknown/empty state or a NEUTRAL rule is always kept, so the
    filter can only remove genuinely inapplicable arms — never invent a gap.
    """
    if condition == "NEUTRAL" or not planet_states:
        return True
    states = set(planet_states)
    if condition == "STRONG":
        return not ("WEAK" in states and "STRONG" not in states)
    if condition == "WEAK":
        return not ("STRONG" in states and "WEAK" not in states)
    return True


# ─── Loader ────────────────────────────────────────────────────────────────

@dataclass
class BookRule:
    type: str          # lord_combo / conjunction / aspect / from_reference / parivartana
    book: str
    trigger: str       # source-text trigger phrase (for citation)
    effect: str        # cleaned effect text
    raw_effect: str    # original effect string
    params: dict       # type-specific parameters (planets, houses, etc)
    topics: tuple[str, ...]  # routed categories
    condition: str = "NEUTRAL"  # STRONG | WEAK | NEUTRAL dignity branch (tier-1)


def _route_topics(effect: str) -> tuple[str, ...]:
    return tuple(cat for cat, rx in TOPIC_REGEX.items() if rx.search(effect))


@lru_cache(maxsize=1)
def load_rules() -> list[BookRule]:
    """Load + clean + topic-classify all 1,926 rules. Cached."""
    if not RULES_PATH.exists():
        return []
    blob = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    rules: list[BookRule] = []
    for typ, items in blob.get("combinations", {}).items():
        if not isinstance(items, list):
            continue
        for it in items:
            raw = it.get("effect", "") or ""
            clean = _clean_effect(raw)
            if not clean or len(clean) < 30:
                continue
            topics = _route_topics(clean)
            if not topics:
                continue  # skip rules we can't categorise
            params = {k: v for k, v in it.items() if k not in ("type", "book", "trigger", "effect")}
            rules.append(BookRule(
                type=typ,
                book=it.get("book", "Unknown"),
                trigger=str(it.get("trigger", ""))[:200],
                effect=clean,
                raw_effect=raw,
                params=params,
                topics=topics,
                condition=_classify_condition(clean),
            ))
    return rules


# ─── Matchers ──────────────────────────────────────────────────────────────

# Natural benefics / malefics for polarity-based multi_house rules.
_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}


def _polarity_class(polarity: str) -> set[str]:
    pol = (polarity or "").lower()
    if "benefic" in pol:
        return _BENEFICS
    if "malefic" in pol:
        return _MALEFICS
    return PLANET_NAMES  # generic "planets"


def _rule_houses(p: dict) -> set[int]:
    """Parse a multi_house rule's `houses` (list or string) into 1..12 ints."""
    raw = p.get("houses")
    if isinstance(raw, list):
        return {int(h) for h in raw
                if str(h).strip().lstrip("-").isdigit() and 1 <= int(h) <= 12}
    return {int(h) for h in re.findall(r"\d{1,2}", str(raw or "")) if 1 <= int(h) <= 12}


def _multi_house_occupants(chart, p: dict) -> list[str]:
    """Polarity planets actually occupying the rule's listed houses."""
    houses = _rule_houses(p)
    cls = _polarity_class(p.get("polarity"))
    return [pl for pl in cls if chart.house_of.get(pl) in houses]


def _multi_house_fires(chart, p: dict) -> bool:
    """Fire when EVERY listed house holds a planet of the polarity class.

    Precise and self-limiting: a vague 7-house list can't be fully tenanted by
    ~4 same-polarity planets, so only specific short-list configurations fire.
    """
    houses = _rule_houses(p)
    if not houses:
        return False
    cls = _polarity_class(p.get("polarity"))
    occupied = {h for pl, h in chart.house_of.items() if pl in cls and h in houses}
    return occupied == houses


def _rule_fires(chart, r: BookRule) -> bool:
    p = r.params
    try:
        if r.type == "lord_combo":
            return _lord_combo(chart, int(p.get("from_house", 0)), int(p.get("to_house", 0)))
        if r.type == "conjunction" or r.type == "conjunction_yoga":
            a, b = p.get("planet_a"), p.get("planet_b")
            if a in PLANET_NAMES and b in PLANET_NAMES:
                return _conjunct(chart, a, b)
        if r.type == "aspect":
            a, b = p.get("aspector"), p.get("aspected")
            if a in PLANET_NAMES and b in PLANET_NAMES:
                return _aspects(chart, a, b)
        if r.type == "from_reference":
            sub = p.get("subject")
            ref = p.get("reference", "")
            cnt = int(p.get("house_count", 0))
            if sub in PLANET_NAMES and (ref in PLANET_NAMES or ref.lower() in ("ascendant", "lagna")) and 1 <= cnt <= 12:
                return _from_reference(chart, sub, cnt, ref)
        if r.type == "parivartana":
            # parivartana entries in the corpus rarely carry house pairs —
            # we surface them as informational only when both houses are present.
            h1, h2 = p.get("house_a"), p.get("house_b")
            if h1 and h2:
                return _parivartana(chart, int(h1), int(h2))
        if r.type == "multi_house":
            return _multi_house_fires(chart, p)
        if r.type == "conditional":
            # Intentionally inert: condition_1/condition_2 are unstructured OCR
            # prose; heuristic parsing yields wrong predicates (verified in
            # scratch/_explore_dead_rules.py). Needs structured re-extraction,
            # not a matcher — so these 1,206 rules stay unfired by design.
            return False
    except (ValueError, TypeError, KeyError):
        return False
    return False


def match_for_chart(chart, rules: list[BookRule] | None = None) -> list[BookRule]:
    """Return only the rules whose triggers fire on this chart."""
    if rules is None:
        rules = load_rules()
    return [r for r in rules if _rule_fires(chart, r)]


# ─── Chart-state resolution (tier-1) ───────────────────────────────────────

_GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
           "Rahu", "Ketu")


def _subject_planets(r: BookRule, chart) -> list[str]:
    """Planet(s) whose dignity a rule's condition refers to (for state lookup)."""
    p = r.params
    try:
        if r.type == "lord_combo":
            fh = int(p.get("from_house", 0) or 0)
            if 1 <= fh <= 12:
                return [_lord_of_house(chart, fh)]
        elif r.type in ("conjunction", "conjunction_yoga"):
            return [x for x in (p.get("planet_a"), p.get("planet_b"))
                    if x in PLANET_NAMES]
        elif r.type == "aspect":
            a = p.get("aspector")
            return [a] if a in PLANET_NAMES else []
        elif r.type == "from_reference":
            s = p.get("subject")
            return [s] if s in PLANET_NAMES else []
        elif r.type == "multi_house":
            return _multi_house_occupants(chart, p)
    except (ValueError, TypeError, KeyError):
        return []
    return []


def chart_state_map(chart) -> dict[str, str]:
    """Per-planet dignity state {STRONG|WEAK|NEUTRAL} for this chart.

    WEAK if the planet is afflicted or below its shadbala threshold; STRONG if
    above threshold and unafflicted; NEUTRAL when strength can't be determined.
    """
    afflicted: set[str] = set()
    try:
        from engine import afflictions
        for a in afflictions.detect_all(chart):
            for name in (getattr(a, "affected", None) or []):
                if name in PLANET_NAMES:
                    afflicted.add(name)
    except Exception:
        pass
    sb = getattr(chart, "shadbala", None)
    sb = sb if isinstance(sb, dict) else {}
    out: dict[str, str] = {}
    for p in _GRAHAS:
        info = sb.get(p)
        is_strong = info.get("is_strong") if isinstance(info, dict) else None
        if p in afflicted:
            out[p] = "WEAK"
        elif is_strong is True:
            out[p] = "STRONG"
        elif is_strong is False:
            out[p] = "WEAK"
        else:
            out[p] = "NEUTRAL"
    return out


def resolve_conditions(matched: list[BookRule], chart) -> list[BookRule]:
    """Drop rules whose dignity branch is contradicted by the chart (tier-1).

    Keeps every NEUTRAL rule and every rule whose subject planet's strength is
    unknown — only genuinely inapplicable arms are removed.
    """
    state_map = chart_state_map(chart)
    kept: list[BookRule] = []
    for r in matched:
        states = [state_map.get(pl, "NEUTRAL")
                  for pl in _subject_planets(r, chart)]
        if _condition_applies(getattr(r, "condition", "NEUTRAL"), states):
            kept.append(r)
    return kept


def to_predictions(matched: list[BookRule], category: str, *,
                   chart=None, max_per_category: int = 8) -> list[Prediction]:
    """Filter matched rules to those tagged with `category` and convert to Predictions.

    When `chart` is given, contradicted dignity arms are dropped first (tier-1
    condition resolution) so a placement's results reflect the subject planet's
    actual strength in this chart rather than every book's branch at once.
    """
    if chart is not None:
        matched = resolve_conditions(matched, chart)
    cat_rules = [r for r in matched if category in r.topics]
    # Deduplicate by trigger+book to avoid near-identical entries
    seen: set[tuple[str, str]] = set()
    unique: list[BookRule] = []
    for r in cat_rules:
        key = (r.book, r.trigger[:80])
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    # Score: prefer rules with cleaner effect text and richer trigger context
    unique.sort(key=lambda r: (len(r.effect), -len(r.trigger)), reverse=True)
    out: list[Prediction] = []
    for i, r in enumerate(unique[:max_per_category]):
        out.append(Prediction(
            key=f"book_rule_{category}_{i+1}",
            label=_label_for(r),
            value=r.effect,
            confidence="MEDIUM",
            chart_evidence=r.trigger.strip() or r.type,
            citations=[Citation(book=r.book, text=r.trigger[:120])],
        ))
    return out


def _label_for(r: BookRule) -> str:
    """Human label for a matched rule."""
    p = r.params
    if r.type == "lord_combo":
        return f"Lord of {p.get('from_house')}H in {p.get('to_house')}H"
    if r.type in ("conjunction", "conjunction_yoga"):
        return f"{p.get('planet_a')} + {p.get('planet_b')} conjunction"
    if r.type == "aspect":
        return f"{p.get('aspector')} aspects {p.get('aspected')}"
    if r.type == "from_reference":
        return f"{p.get('subject')} in {p.get('house_count')}H from {p.get('reference')}"
    if r.type == "parivartana":
        return f"Parivartana between {p.get('house_a')}H and {p.get('house_b')}H"
    return r.type.replace("_", " ").title()


# ─── Public convenience ────────────────────────────────────────────────────

def predictions_for(chart, category: str, max_per_category: int = 8) -> list[Prediction]:
    """One-shot: load + match + convert for one category (chart-aware filtering)."""
    return to_predictions(match_for_chart(chart), category, chart=chart,
                          max_per_category=max_per_category)
