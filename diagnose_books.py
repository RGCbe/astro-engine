"""
Deep Per-Book Diagnostic
=========================
For every book in the corpus, identifies the EXACT reason it performs poorly:

  ROOT CAUSE A — No dasha rules at all (zero dasha-tagged rules)
  ROOT CAUSE B — Wrong valence: predicts auspicious when event is negative (or vice versa)
  ROOT CAUSE C — Low coverage: doesn't speak to certain event types at all
  ROOT CAUSE D — Low trigger rate: rules exist but rarely match active dasha lords
  ROOT CAUSE E — OCR / extraction quality: mostly junk / very short rules

Shows specific MISFIRE examples for each bad book.
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

from collections import defaultdict
from engine.corpus import get_corpus
from engine.backtest import _moon_lon, _birth_dt
from engine.dasha import current_dasha
from engine.known_charts import KNOWN_CHARTS

# ── Valence helpers ────────────────────────────────────────────────────────────
POSITIVE_EVENTS = {"AWARD", "MARRIAGE", "CAREER_PEAK", "FOUND_BUSINESS",
                   "POLITICAL_OFFICE", "CAREER_START", "CHILDREN_BORN"}
NEGATIVE_EVENTS = {"DEATH", "IMPRISONMENT", "EXILE", "MAJOR_LOSS",
                   "HEALTH_CRISIS", "SCANDAL", "DIVORCE"}
ALL_EVENT_TYPES = POSITIVE_EVENTS | NEGATIVE_EVENTS | {"SPIRITUAL_AWAKENING"}

AUSPICIOUS_KW  = ["wealth","success","fame","happiness","health","gain","auspicious",
                   "good fortune","rich","king","prosperous","honor","victory","blessed",
                   "excellent","award","rise","promotion","marriage","children","son","progeny"]
INAUSPICIOUS_KW= ["poverty","death","disease","loss","grief","inauspicious","bad","sorrow",
                   "poor","pain","danger","trouble","fear","imprisonment","exile","separation",
                   "divorce","downfall","disgrace","scandal","ill health","accident","misery"]

def rule_valence(text):
    t = text.lower()
    a = sum(1 for k in AUSPICIOUS_KW   if k in t)
    i = sum(1 for k in INAUSPICIOUS_KW if k in t)
    if a > i: return "auspicious"
    if i > a: return "inauspicious"
    return "neutral"

def event_valence(etype):
    if etype in POSITIVE_EVENTS: return "auspicious"
    if etype in NEGATIVE_EVENTS: return "inauspicious"
    return "neutral"

def main():
    print("Loading corpus...")
    corpus = get_corpus()

    # ── Inventory every book ──────────────────────────────────────────────────
    book_all_rules      = defaultdict(list)   # book -> all CorpusRules it appears in
    book_dasha_rules    = defaultdict(list)   # book -> dasha-tagged rules
    book_rule_valences  = defaultdict(list)   # book -> list of ("auspicious"|"inauspicious"|"neutral")
    book_avg_len        = defaultdict(list)   # book -> list of rule text lengths

    for rule in corpus._all:
        for b in rule.books:
            book_all_rules[b].append(rule)
            book_avg_len[b].append(len(rule.text))
            book_rule_valences[b].append(rule_valence(rule.text))
            if rule.rule_type == "dasha":
                book_dasha_rules[b].append(rule)

    all_books = sorted(book_all_rules.keys())
    print(f"{len(all_books)} books found in corpus.\n")

    # ── Run event scoring per book ────────────────────────────────────────────
    # For each event, which books fired, which were right/wrong/neutral
    book_fires          = defaultdict(int)    # total times a book's rules fired
    book_valence_hits   = defaultdict(int)    # rule valence matched event valence
    book_valence_miss   = defaultdict(int)    # rule valence OPPOSED event valence
    book_valence_neutral= defaultdict(int)    # rule was neutral
    book_event_coverage = defaultdict(set)    # event types this book touched
    book_misfires       = defaultdict(list)   # (chart, event, rule) examples of wrong valence

    for chart in KNOWN_CHARTS:
        moon = _moon_lon(chart.birthdata)
        bdt  = _birth_dt(chart.birthdata)
        b    = {"year": bdt.year, "month": bdt.month, "day": bdt.day,
                "hour": bdt.hour, "min": bdt.minute}
        fake = {"positions": {"Moon": {"lon": moon, "lon_abs": moon}}, "birth": b}

        for ev in chart.events:
            if ev.event_type not in ALL_EVENT_TYPES:
                continue
            mo = ev.month or 6
            dy = ev.day   or 15
            active   = current_dasha(fake, dt.datetime(ev.year, mo, dy))
            md_block = active.get("md")
            ad_block = active.get("ad")
            if not md_block:
                continue
            md_lord  = md_block.get("md") or md_block.get("lord") or ""
            ad_lord  = (ad_block.get("ad") or ad_block.get("lord")) if ad_block else ""

            triggered = corpus.get_dasha_rules(md_lord, ad_lord, limit=200)
            ev_val    = event_valence(ev.event_type)

            seen_books_this_event = set()
            for rule in triggered:
                rv = rule_valence(rule.text)
                for bk in rule.books:
                    book_fires[bk] += 1
                    book_event_coverage[bk].add(ev.event_type)
                    if ev_val == "neutral" or rv == "neutral":
                        book_valence_neutral[bk] += 1
                    elif rv == ev_val:
                        book_valence_hits[bk] += 1
                    else:
                        book_valence_miss[bk] += 1
                        # Store one misfire example per book (avoid duplicates)
                        if bk not in seen_books_this_event:
                            book_misfires[bk].append({
                                "chart": chart.name,
                                "event": ev.event_type,
                                "year": ev.year,
                                "event_val": ev_val,
                                "rule_val": rv,
                                "md": md_lord,
                                "ad": ad_lord,
                                "rule_text": rule.text[:120],
                            })
                            seen_books_this_event.add(bk)

    # ── Classify root cause for each book ─────────────────────────────────────
    MAX_EVT = len(ALL_EVENT_TYPES)
    results = []

    for bk in all_books:
        total_rules  = len(book_all_rules[bk])
        dasha_count  = len(book_dasha_rules[bk])
        fires        = book_fires[bk]
        hits         = book_valence_hits[bk]
        misses       = book_valence_miss[bk]
        neutrals     = book_valence_neutral[bk]
        coverage     = len(book_event_coverage[bk])
        avg_len      = sum(book_avg_len[bk]) / max(len(book_avg_len[bk]), 1)

        valence_total = hits + misses + neutrals
        val_acc  = hits / valence_total if valence_total > 0 else 0.0
        miss_rate= misses / valence_total if valence_total > 0 else 0.0
        cov_rate = coverage / MAX_EVT
        trigger_rate = min(fires / max(total_rules, 1), 1.0)
        composite = val_acc * 0.50 + cov_rate * 0.30 + trigger_rate * 0.20

        # ── Root cause classification ──────────────────────────────────────
        causes = []
        if fires == 0:
            causes.append("A: ZERO dasha triggers — no dasha rules match any event period")
        else:
            if dasha_count == 0:
                causes.append("A: No dasha-tagged rules — all rules are planet/house/yoga only")
            if miss_rate > 0.30:
                causes.append(f"B: HIGH WRONG VALENCE ({miss_rate*100:.0f}% misfires) — predicts opposite of real outcome")
            if coverage < 5:
                causes.append(f"C: LOW COVERAGE — only speaks to {coverage}/{MAX_EVT} event types")
            elif coverage < 10:
                causes.append(f"C: PARTIAL COVERAGE — {coverage}/{MAX_EVT} event types")
            if fires > 0 and trigger_rate < 0.10:
                causes.append(f"D: LOW TRIGGER RATE ({trigger_rate*100:.1f}%) — rules too specific / rarely match active dashas")
            if avg_len < 50:
                causes.append(f"E: SHORT RULES (avg {avg_len:.0f} chars) — likely OCR fragments or incomplete extractions")
            if total_rules < 20:
                causes.append(f"E: SPARSE ({total_rules} rules total) — book barely extracted")

        if not causes and composite >= 0.80:
            causes.append("OK: High accuracy — no significant issues")

        results.append({
            "book": bk, "total_rules": total_rules, "dasha_count": dasha_count,
            "fires": fires, "hits": hits, "misses": misses, "neutrals": neutrals,
            "val_acc": val_acc, "miss_rate": miss_rate, "coverage": coverage,
            "avg_len": avg_len, "composite": composite, "causes": causes,
        })

    # Sort: worst composite first
    results.sort(key=lambda x: x["composite"])

    # ── Print ──────────────────────────────────────────────────────────────────
    print("=" * 110)
    print("BOOKS RANKED WORST -> BEST  (showing root-cause diagnosis)")
    print("=" * 110)

    for r in results:
        bk  = r["book"]
        cmp = r["composite"]
        bar = "#" * int(cmp * 30)
        grade = "F" if cmp < 0.30 else "D" if cmp < 0.50 else "C" if cmp < 0.65 else "B" if cmp < 0.80 else "A"

        print(f"\n[{grade}] {bk}")
        print(f"     Score: {cmp*100:.1f}% | Rules: {r['total_rules']} | Dasha rules: {r['dasha_count']} "
              f"| Fires: {r['fires']} | Hits: {r['hits']} | Misfires: {r['misses']} "
              f"| Coverage: {r['coverage']}/{MAX_EVT} | Avg rule len: {r['avg_len']:.0f} chars")
        for c in r["causes"]:
            print(f"     >> {c}")

        # Show 2 misfire examples
        misfires = book_misfires.get(bk, [])[:2]
        for mf in misfires:
            print(f"     MISFIRE: {mf['chart']} ({mf['year']}) | {mf['event']} [{mf['event_val'].upper()}] "
                  f"| MD={mf['md']} AD={mf['ad']}")
            print(f"             Rule ({mf['rule_val'].upper()}): \"{mf['rule_text']}\"")

    # ── Summary table of problem categories ───────────────────────────────────
    print("\n\n" + "=" * 80)
    print("ROOT CAUSE SUMMARY")
    print("=" * 80)
    cat_counts = defaultdict(int)
    for r in results:
        for c in r["causes"]:
            cat_counts[c[0]] += 1
    cats = {
        "A": "No dasha rules / zero triggers",
        "B": "Wrong valence (predicts opposite of real outcome)",
        "C": "Low/partial event coverage",
        "D": "Low trigger rate",
        "E": "Sparse / short OCR rules",
        "O": "OK — no issues",
    }
    for k, label in cats.items():
        print(f"  Root Cause {k} ({label}): {cat_counts[k]} books")

    # ── Books with the worst valence misfires ─────────────────────────────────
    print("\n\nWORST VALENCE MISFIRES (books predicting opposite of reality):")
    worst_val = sorted(results, key=lambda x: -x["miss_rate"])
    for r in worst_val[:10]:
        if r["misses"] > 0:
            print(f"  {r['book']:<50} Miss rate: {r['miss_rate']*100:.1f}%  ({r['misses']} wrong / {r['hits']+r['misses']+r['neutrals']} total)")

    # ── Books with zero coverage ───────────────────────────────────────────────
    zero_fire = [r for r in results if r["fires"] == 0]
    print(f"\n\nBOOKS WITH ZERO DASHA TRIGGERS ({len(zero_fire)} books):")
    for r in zero_fire:
        print(f"  {r['book']:<50} {r['total_rules']} rules, avg len {r['avg_len']:.0f} chars")

if __name__ == "__main__":
    main()
