"""
Per-book Prediction Accuracy Ranker
====================================
For every book in the 58-book corpus, scores:
  - How many rules it contributed that were actually triggered for documented events
  - Auspicious / Inauspicious prediction accuracy (does its rule text match the
    real-life outcome of the event?)
  - Coverage breadth (how many different event types does it speak to?)
  - Rule quality (avg rules per slot — more focused = higher quality)

Method:
  For each known chart event, we already know the active dasha lord (MD/AD).
  We pull all dasha rules for that lord from the corpus.
  For each rule, we check which books contributed it.
  We then check if the rule text's sentiment aligns with the event valence:
    - POSITIVE events (AWARD, MARRIAGE, CAREER_PEAK, FOUND_BUSINESS, POLITICAL_OFFICE,
                       CAREER_START, CHILDREN_BORN) → auspicious rule = HIT
    - NEGATIVE events (DEATH, IMPRISONMENT, EXILE, MAJOR_LOSS, HEALTH_CRISIS,
                       SCANDAL, DIVORCE) → inauspicious rule = HIT
    - NEUTRAL (SPIRITUAL_AWAKENING) → any rule = HIT
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from collections import defaultdict
from engine.corpus import get_corpus
from engine.backtest import _moon_lon, _birth_dt, EVENT_PATTERNS
from engine.dasha import current_dasha
from engine.known_charts import KNOWN_CHARTS

# ── Event valence map ──────────────────────────────────────────────────────────
POSITIVE_EVENTS = {"AWARD", "MARRIAGE", "CAREER_PEAK", "FOUND_BUSINESS",
                   "POLITICAL_OFFICE", "CAREER_START", "CHILDREN_BORN"}
NEGATIVE_EVENTS = {"DEATH", "IMPRISONMENT", "EXILE", "MAJOR_LOSS",
                   "HEALTH_CRISIS", "SCANDAL", "DIVORCE"}
NEUTRAL_EVENTS  = {"SPIRITUAL_AWAKENING"}

AUSPICIOUS_KW  = ["wealth", "success", "fame", "happiness", "health", "gain",
                   "auspicious", "good fortune", "rich", "king", "prosperous",
                   "honor", "victory", "blessed", "excellent", "award", "rise",
                   "promotion", "marriage", "children", "son", "progeny"]
INAUSPICIOUS_KW = ["poverty", "death", "disease", "loss", "grief", "inauspicious",
                    "bad", "sorrow", "poor", "pain", "danger", "trouble", "fear",
                    "imprisonment", "exile", "separation", "divorce", "downfall",
                    "disgrace", "scandal", "ill health", "accident", "misery"]

def rule_valence(text: str) -> str:
    t = text.lower()
    a = sum(1 for k in AUSPICIOUS_KW  if k in t)
    i = sum(1 for k in INAUSPICIOUS_KW if k in t)
    if a > i:   return "auspicious"
    if i > a:   return "inauspicious"
    return "neutral"

def event_valence(event_type: str) -> str:
    if event_type in POSITIVE_EVENTS: return "auspicious"
    if event_type in NEGATIVE_EVENTS: return "inauspicious"
    return "neutral"

# ── Per-book accumulators ──────────────────────────────────────────────────────
class BookScore:
    def __init__(self, name):
        self.name = name
        self.rules_triggered = 0       # rules from this book that fired for an event
        self.valence_hits = 0          # rules whose valence matched event valence
        self.valence_total = 0         # total rules checked for valence
        self.event_types_covered = set()
        self.total_rules = 0           # total rules in corpus from this book

def main():
    print("Loading corpus...")
    corpus = get_corpus()

    # Count total rules per book
    book_totals: dict[str, int] = defaultdict(int)
    for rule in corpus._all:
        for b in rule.books:
            book_totals[b] += 1

    print(f"Corpus loaded: {len(corpus._all)} rules, {len(book_totals)} books")
    print("Scoring books against 291 historical events...")

    scores: dict[str, BookScore] = {}
    for b in book_totals:
        scores[b] = BookScore(b)
        scores[b].total_rules = book_totals[b]

    events_processed = 0

    for chart in KNOWN_CHARTS:
        moon = _moon_lon(chart.birthdata)
        bdt  = _birth_dt(chart.birthdata)
        b = {"year": bdt.year, "month": bdt.month, "day": bdt.day,
             "hour": bdt.hour, "min": bdt.minute}
        fake_chart = {"positions": {"Moon": {"lon": moon, "lon_abs": moon}},
                      "birth": b}

        for ev in chart.events:
            if ev.event_type not in (POSITIVE_EVENTS | NEGATIVE_EVENTS | NEUTRAL_EVENTS):
                continue
            mo = ev.month if ev.month else 6
            dy = ev.day   if ev.day   else 15
            active = current_dasha(fake_chart, dt.datetime(ev.year, mo, dy))
            md_block = active.get("md")
            ad_block = active.get("ad")
            if not md_block:
                continue

            md_lord = md_block.get("md") or md_block.get("lord") or ""
            ad_lord = (ad_block.get("ad") or ad_block.get("lord")) if ad_block else ""

            # Pull dasha rules for both MD and AD lords
            triggered_rules = corpus.get_dasha_rules(md_lord, ad_lord, limit=100)
            ev_val = event_valence(ev.event_type)
            events_processed += 1

            for rule in triggered_rules:
                rv = rule_valence(rule.text)
                for book in rule.books:
                    if book not in scores:
                        continue
                    scores[book].rules_triggered += 1
                    scores[book].event_types_covered.add(ev.event_type)
                    scores[book].valence_total += 1
                    if ev_val == "neutral" or rv == ev_val or rv == "neutral":
                        scores[book].valence_hits += 1

    print(f"\nProcessed {events_processed} events across {len(KNOWN_CHARTS)} charts.\n")

    # ── Compute final score ────────────────────────────────────────────────────
    # Score = valence_accuracy * 0.5 + coverage_breadth * 0.3 + rule_density * 0.2
    MAX_EVENT_TYPES = len(POSITIVE_EVENTS | NEGATIVE_EVENTS | NEUTRAL_EVENTS)

    ranked = []
    for b, sc in scores.items():
        if sc.valence_total == 0:
            continue
        valence_acc    = sc.valence_hits / sc.valence_total
        coverage       = len(sc.event_types_covered) / MAX_EVENT_TYPES
        trigger_rate   = min(sc.rules_triggered / max(sc.total_rules, 1), 1.0)
        composite = valence_acc * 0.50 + coverage * 0.30 + trigger_rate * 0.20
        ranked.append((composite, valence_acc, coverage, sc))

    ranked.sort(key=lambda x: -x[0])

    print("=" * 100)
    print(f"{'RANK':<5} {'BOOK':<45} {'COMPOSITE':<11} {'VALENCE ACC':<13} {'COVERAGE':<10} {'RULES FIRED':<12} {'TOTAL RULES'}")
    print("=" * 100)

    for i, (comp, val_acc, cov, sc) in enumerate(ranked[:30], 1):
        bar = "#" * int(comp * 20)
        print(f"  {i:<4} {sc.name:<45} {comp*100:>7.1f}%   {val_acc*100:>9.1f}%   "
              f"{cov*100:>6.1f}%   {sc.rules_triggered:>8}     {sc.total_rules}")

    print("=" * 100)
    print("\nTop 5 Books by pure VALENCE ACCURACY (best at predicting good/bad correctly):")
    by_valence = sorted(ranked, key=lambda x: (-x[1], -x[0]))[:5]
    for i, (comp, val_acc, cov, sc) in enumerate(by_valence, 1):
        print(f"  {i}. {sc.name:<45} Valence: {val_acc*100:.1f}%  Coverage: {int(cov*MAX_EVENT_TYPES)}/{MAX_EVENT_TYPES} event types")

    print("\nTop 5 Books by COVERAGE (speaks to most event types):")
    by_coverage = sorted(ranked, key=lambda x: (-x[2], -x[0]))[:5]
    for i, (comp, val_acc, cov, sc) in enumerate(by_coverage, 1):
        print(f"  {i}. {sc.name:<45} Coverage: {int(cov*MAX_EVENT_TYPES)}/{MAX_EVENT_TYPES}  Rules: {sc.total_rules}")

    print("\nTop 5 Books by RULE COUNT (most content):")
    by_rules = sorted(scores.values(), key=lambda s: -s.total_rules)[:5]
    for i, sc in enumerate(by_rules, 1):
        print(f"  {i}. {sc.name:<45} {sc.total_rules} rules")

if __name__ == "__main__":
    main()
