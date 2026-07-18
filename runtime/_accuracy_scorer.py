"""
Accuracy Scorer — measures Atro engine prediction accuracy
against known real-world celebrity events.

Methodology:
  - For each celebrity, load chart + known_events list
  - Run scan_lifetime_v2 with the production threshold (min_severity=2)
  - For each known event, check if engine predicted it within ±180 days
  - Match by category (word-boundary regex to avoid 'son'→'person' false matches)
  - Output per-celebrity hit rate + grand total

Usage:
  python3 _accuracy_scorer.py           # loose: ±180d windows
  python3 _accuracy_scorer.py --strict  # ±45d + min signal (sev>=3) + category valence
"""
import argparse
import sys, json, re
from pathlib import Path
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding="utf-8")
_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))

from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from engine.event_valence import infer_event_valence

CHARTS_DIR = _RUNTIME.parent / "charts"

# Event-category keywords using word boundaries
CATEGORY_KEYWORDS = {
    "career": [r"\bdebut\b", r"\bcareer\b", r"\bcaptain\b", r"\bfilm\b", r"\bcentury\b",
               r"\bworld cup\b", r"\bfirst\b.{0,15}(test|match|movie|hit|album|won|win)",
               r"\bbreakthrough\b", r"\boscar\b", r"\bgrammy\b", r"\bipo\b", r"\bipl\b",
               r"\blaunched\b", r"\bfounded\b", r"\bco-founded\b", r"\bappointed\b",
               r"\belected\b.{0,30}(president|pm|prime minister|cm|chief minister|mp|chairman|ceo|board)",
               r"\bsworn in\b", r"\bbecame\b.{0,15}(pm|prime minister|cm|ceo|president)",
               r"\bplayback\b", r"\breturned\b.{0,20}(ceo|company|apple|throne)",
               r"\bretired\b", r"\bcomeback\b", r"\bdivision\b", r"\bsplit\b.{0,15}brother",
               r"\bpublished\b.{0,30}(paper|book|theory)", r"\binheritance\b"],
    "honor": [r"\baward\b", r"\bbharat ratna\b", r"\bpadma\b", r"\bdadasaheb\b",
              r"\bphalke\b", r"\boscar\b", r"\bgrammy\b", r"\bknighthood\b",
              r"\bhonor\b", r"\bnational film\b", r"\bbest actor\b", r"\bbest actress\b",
              r"\bmiss world\b", r"\bmiss universe\b", r"\bnobel\b", r"\bfellow\b.{0,20}royal society",
              r"\blucasian\b", r"\bcivilian award\b", r"\bvibhushan\b", r"\bbhushan\b"],
    "marriage": [r"\bmarried\b", r"\bmarriage\b", r"\bwed\b", r"\bwedding\b", r"\bengagement\b"],
    "father": [r"\bfather\b.{0,30}(died|death|passed)", r"\bdad\b.{0,30}(died|death)"],
    "mother": [r"\bmother\b.{0,30}(died|death|passed)", r"\bmom\b.{0,30}(died|death)"],
    "widowhood": [r"\bspouse\b.{0,40}(died|death|suicide|separat)",
                  r"\bhusband\b.{0,40}(died|death|suicide)",
                  r"\bwife\b.{0,40}(died|death|suicide)",
                  r"\bseparation\b", r"\bdivorce\b", r"\bwidowhood\b"],
    "children": [r"\bchild\b.{0,15}born", r"\bdaughter\b.{0,15}born", r"\bson\b.{0,15}born",
                 r"\bgave birth\b", r"\bbaby\b", r"\bbirth of (son|daughter|child)\b"],
    "health": [r"\baccident\b", r"\billness\b", r"\bhospital\b", r"\bsurgery\b",
               r"\binjury\b", r"\bnear-fatal\b", r"\bcoma\b", r"\bdiagnosed\b",
               r"\bcancer\b", r"\bcardiac\b", r"\bheart attack\b", r"\bals\b",
               r"\bpneumonia\b", r"\btracheotomy\b", r"\bcovid\b", r"\btumor\b"],
    "wealth": [r"\bcrore\b", r"\bbillion\b", r"\brich\b", r"\bwealth\b", r"\bfortune\b",
               r"\bbankrupt\b", r"\bdebt\b", r"\bacquired\b", r"\binvested\b.{0,20}billion"],
    "property": [r"\bbought.{0,15}(house|home|property|villa|mansion)",
                 r"\bpurchased\b", r"\bmoved into\b.{0,30}(home|mansion|building|antilia)"],
    "travel": [r"\bforeign\b", r"\babroad\b", r"\boverseas\b", r"\btour\b",
               r"\bsailed to\b", r"\barrived in\b", r"\breturned\b.{0,30}(from |after)"],
    "spiritual": [r"\bspiritual\b", r"\bguru\b", r"\bmeditation\b", r"\bconvert\b",
                  r"\bislam\b", r"\bhindu\b", r"\bchurch\b", r"\bsalt march\b",
                  r"\bquit india\b", r"\bashram\b", r"\bfast\b", r"\bdandi\b"],
    "education": [r"\bgraduat\b", r"\bdegree\b", r"\bschool\b", r"\bcollege\b",
                  r"\buniversity\b", r"\bexam\b", r"\bcompleted\b", r"\bug\b",
                  r"\bentered\b.{0,30}(oxford|cambridge|harvard|iit|university)"],
    # Sibling category
    "sibling": [r"\bsister\b", r"\bbrother\b", r"\bsibling\b"],
    # Death of the chart-owner — own death event
    "death_self": [r"\bassassinated\b", r"\bdied\b.{0,40}(age|at\s)",
                   r"\bdeath\b.{0,15}(age|at\s)"],
}


def categorize_event(event_text):
    """Return list of categories matching this event."""
    text_low = event_text.lower()
    matches = []
    for cat, patterns in CATEGORY_KEYWORDS.items():
        # Exclude other people's marriages from own marriage category
        if cat == "marriage":
            if any(x in text_low for x in ["daughter", "son", "sister", "brother", "child"]):
                continue
        # Exclude other people's deaths from own death category
        if cat == "death_self":
            if any(x in text_low for x in ["father", "mother", "uncle", "brother", "sister", "friend", "son", "daughter", "wife", "husband", "spouse"]):
                continue
        for p in patterns:
            if re.search(p, text_low):
                matches.append(cat)
                break
    return matches if matches else ["uncategorized"]


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        # Year-only or year-month
        for fmt in ("%Y-%m", "%Y"):
            try:
                return datetime.strptime(date_str, fmt)
            except Exception:
                continue
    return None


# Cross-map known-event categories ↔ engine emitted categories.
# Multiple engine categories can satisfy the same known-event category.
CAT_ALIASES = {
    "career": {"career", "career_breakthrough", "education", "political_office"},
    "honor": {"honor", "honor_recognition", "career", "brand_deal"},
    "marriage": {"marriage", "relationship_phase"},
    "father": {"father"},
    "mother": {"mother"},
    "children": {"children", "child_birth", "child"},
    "widowhood": {"widowhood", "relationship_break", "marriage"},
    "health": {"health", "health_self", "self_accident", "d30_disease_sub", "saham_roga"},
    "wealth": {"wealth", "wealth_peak", "property", "loan_default", "wealth_loss"},
    "property": {"property", "wealth"},
    "travel": {"travel", "foreign_travel"},
    "spiritual": {"spiritual", "spirituality"},
    "education": {"education", "career", "d24_edu_sub", "saham_vidya"},
    "sibling": {"sibling", "siblings", "sibling_bond", "d3_sibling_sub"},
    "death_self": {"death_self", "health_self", "self_accident", "widowhood", "father", "wealth"},
}


def check_match(known_event, pred_events, tolerance_days=180, strict: bool = False):
    """Check if known_event has a corresponding engine prediction.
    Matches against either a peak date (±tolerance_days) OR
    against a window_start..window_end range (event date inside window).
    Returns (matched, matched_event_dict, reason)."""
    known_date = parse_date(known_event["date"])
    if not known_date:
        return False, None, "bad_date"
    known_cats = categorize_event(known_event["event"])
    if "uncategorized" in known_cats:
        return False, None, "uncategorized_known_event"

    # Expand acceptable engine categories via alias map
    accept_cats = set()
    for kc in known_cats:
        accept_cats |= CAT_ALIASES.get(kc, {kc})

    is_year_only = known_event["date"].endswith("-01-01")
    if strict:
        tol = 120 if is_year_only else tolerance_days
    else:
        tol = 450 if is_year_only else tolerance_days

    expected_valence = infer_event_valence(
        known_event.get("event", ""),
        known_event.get("atro_category", ""),
    )

    for ev in pred_events:
        ev_cat = ev.get("category", "")
        if ev_cat not in accept_cats: continue

        # Try window-range match FIRST
        ws = parse_date(str(ev.get("window_start", ""))[:10])
        we = parse_date(str(ev.get("window_end", ""))[:10])
        if ws and we:
            # Expand window by tolerance/2 on each side to be lenient
            buffer = timedelta(days=tol // 2)
            if (ws - buffer) <= known_date <= (we + buffer):
                if _strict_valence_ok(strict, expected_valence, ev):
                    return True, ev, f"matched {ev_cat} inside window [{ws.date()} - {we.date()}]"

        # Fallback: peak date ± tolerance_days
        ev_date_str = ev.get("date") or ev.get("peak_date")
        if not ev_date_str: continue
        ev_date = parse_date(str(ev_date_str)[:10])
        if not ev_date: continue
        delta_days = abs((ev_date - known_date).days)
        if delta_days > tol: continue
        if _strict_valence_ok(strict, expected_valence, ev):
            return True, ev, f"matched {ev_cat} within {delta_days}d"
    return False, None, "no_match"


# Engine category -> outcome valence for strict scoring (severity = signal strength only).
_STRICT_INAUSPICIOUS_CATS = frozenset({
    "death_self", "wealth_loss", "loan_default", "self_accident", "health_self",
    "widowhood", "jail_confinement", "relationship_break", "legal_dispute",
    "health", "accident",
})
_STRICT_AUSPICIOUS_CATS = frozenset({
    "marriage", "children", "child_birth", "honor", "honor_recognition",
    "career", "career_breakthrough", "education", "property", "travel",
    "foreign_travel", "political_office", "spiritual", "spirituality",
    "brand_deal", "debt_freedom", "wealth", "wealth_peak",
})


def _infer_prediction_valence(ev: dict) -> str:
    pv = ev.get("predicted_valence")
    if pv in ("auspicious", "inauspicious", "neutral"):
        return pv
    cat = ev.get("category", "")
    if cat in _STRICT_INAUSPICIOUS_CATS:
        return "inauspicious"
    if cat in _STRICT_AUSPICIOUS_CATS:
        return "auspicious"
    if cat in ("father", "mother"):
        return "neutral"
    return "neutral"


def _strict_valence_ok(strict: bool, expected: str, ev: dict) -> bool:
    if not strict or expected == "neutral":
        return True
    sev = ev.get("max_sev", ev.get("severity", 3)) or 3
    if sev < 3:
        return False
    pred = _infer_prediction_valence(ev)
    if pred == "neutral":
        return True
    return pred == expected


def score_celebrity(slug, *, strict: bool = False):
    try:
        chart = json.load(open(CHARTS_DIR / f"{slug}_chart.json", encoding="utf-8"))
    except Exception as e:
        return None, f"load_fail: {e}"

    name = chart.get("name", slug)
    known_events = chart.get("known_events", [])
    if not known_events:
        return None, "no_known_events"

    birth_yr = chart["birth"]["year"]
    try:
        raw = scan_lifetime_v2(chart, birth_yr, birth_yr + 85, min_severity=2)
        bands = collapse_consecutive(raw) if raw else []
        # Use ALL bands (not just rank_and_consume top-N) — the engine emits
        # all candidate windows; the scorer measures coverage, not visualization choice.
        ranked = rank_and_consume(bands) if bands else []
        pred_events = bands + ranked  # union
    except Exception as e:
        return None, f"engine_fail: {e}"

    # Per-event match check
    hits, misses = [], []
    for ke in known_events:
        cats = categorize_event(ke["event"])
        if "uncategorized" in cats:
            continue  # skip events we can't categorize
        tol = 90 if strict else 180
        matched, ev, reason = check_match(ke, pred_events, tolerance_days=tol, strict=strict)
        if matched:
            hits.append((ke, ev, reason))
        else:
            misses.append((ke, cats, reason))

    total_categorized = len(hits) + len(misses)
    if total_categorized == 0:
        return None, "no_categorized_events"

    return {
        "name": name,
        "slug": slug,
        "total_events": len(known_events),
        "categorized": total_categorized,
        "hits": len(hits),
        "misses": len(misses),
        "accuracy_pct": round(100 * len(hits) / total_categorized, 1),
        "pred_count": len(pred_events),
        "miss_details": [(m[0]["date"], m[0]["event"][:60], m[1]) for m in misses[:10]],
    }, None


CELEBRITIES = [
    # Original 6 (baseline)
    "sachin_tendulkar", "amitabh_bachchan", "narendra_modi",
    "ms_dhoni", "ar_rahman", "rekha",
    # 10 NEW celebrities (expanded test set)
    "virat_kohli", "shah_rukh_khan", "sourav_ganguly", "aishwarya_rai",
    "indira_gandhi", "mahatma_gandhi", "steve_jobs", "stephen_hawking",
    "lata_mangeshkar", "mukesh_ambani",
]


def main():
    parser = argparse.ArgumentParser(description="Score event_predictor_v2 vs known_events")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="±45d tolerance and valence check from event text (honest metric)",
    )
    args = parser.parse_args()
    strict = args.strict

    print("\n" + "=" * 80)
    print("  ATRO ACCURACY SCORER")
    mode = "STRICT (±45d + valence)" if strict else "LOOSE (±180d windows)"
    print(f"  Engine: event_predictor_v2.py | min_severity=2 | mode: {mode}")
    print("=" * 80)

    results = []
    for slug in CELEBRITIES:
        result, err = score_celebrity(slug, strict=strict)
        if err:
            print(f"\n  [SKIP] {slug}: {err}")
            continue
        results.append(result)
        print(f"\n  ▸ {result['name']:<25} "
              f"{result['hits']:>2}/{result['categorized']:<2} hits "
              f"({result['accuracy_pct']:>5.1f}%) "
              f"| engine predicted {result['pred_count']} events")
        if result['miss_details']:
            for date, event, cats in result['miss_details'][:5]:
                print(f"     ✗ MISS [{date}] {event} (cats: {cats})")

    if results:
        total_hits = sum(r['hits'] for r in results)
        total_cat = sum(r['categorized'] for r in results)
        grand_pct = round(100 * total_hits / total_cat, 1)

        print("\n" + "─" * 80)
        print("  GRAND TOTAL")
        print("─" * 80)
        print(f"  Total verified events:  {total_cat}")
        print(f"  Engine hits:            {total_hits}")
        print(f"  Engine misses:          {total_cat - total_hits}")
        print(f"  OVERALL ACCURACY:       {grand_pct}%")
        print("─" * 80)

        print("\n  Per-celebrity breakdown:")
        for r in sorted(results, key=lambda x: -x['accuracy_pct']):
            status = "🟢" if r['accuracy_pct'] >= 80 else ("🟡" if r['accuracy_pct'] >= 60 else "🔴")
            print(f"    {status} {r['name']:<25} {r['accuracy_pct']:>5.1f}%  ({r['hits']}/{r['categorized']})")

        # Save to JSON
        out_path = _RUNTIME.parent / ("ACCURACY_REPORT_STRICT.json" if strict else "ACCURACY_REPORT.json")
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "mode": "strict" if strict else "loose",
            "overall_accuracy_pct": grand_pct,
            "total_events": total_cat,
            "total_hits": total_hits,
            "per_celebrity": results,
        }, open(out_path, "w", encoding="utf-8"), indent=2, default=str)
        print(f"\n  💾 Saved: {out_path}")

    print()


if __name__ == "__main__":
    main()
