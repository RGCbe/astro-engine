import sys
import json
import argparse
from pathlib import Path

_ROOT = Path("/opt/astro")
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "runtime"))

from runtime.event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from runtime._accuracy_scorer import check_match, categorize_event, parse_date

def main():
    parser = argparse.ArgumentParser(description="Analyze a specific celebrity's predictions")
    parser.add_argument("slug", help="Celebrity slug (e.g., ar_rahman, steve_jobs, virat_kohli)")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode (90d tolerance, valence checks)")
    args = parser.parse_args()

    chart_path = _ROOT / "charts" / f"{args.slug}_chart.json"
    if not chart_path.exists():
        print(f"Error: Chart file for {args.slug} does not exist at {chart_path}")
        print("Available slugs are:")
        for f in sorted(list((_ROOT / "charts").glob("*_chart.json"))):
            print(f"  {f.stem.replace('_chart', '')}")
        sys.exit(1)

    chart = json.load(chart_path.open("r", encoding="utf-8"))

    mode_str = "STRICT (90d + valence)" if args.strict else "LOOSE (180d windows)"
    print(f"==========================================================================")
    print(f"DEEP ASTROLOGICAL AUDIT: {chart.get('name', args.slug).upper()}")
    print(f"Birth Details: {chart['birth'].get('place', chart['birth'].get('place_en', 'Unknown'))} | {chart['birth']['year']}-{chart['birth']['month']}-{chart['birth']['day']}")
    print(f"Lagna: {chart['lagna']} | Janma Nakshatra: {chart['janma_nakshatra']}")
    print(f"Mode: {mode_str}")
    print(f"==========================================================================\n")

    birth_yr = chart["birth"]["year"]
    raw = scan_lifetime_v2(chart, birth_yr, birth_yr + 85, min_severity=2)
    bands = collapse_consecutive(raw) if raw else []
    ranked = rank_and_consume(bands) if bands else []
    pred_events = bands + ranked

    known_events = chart.get("known_events", [])
    if not known_events:
        print("No known events recorded for this chart.")
        sys.exit(0)

    print("--- RUNNING PREDICTIONS FOR KNOWN EVENTS ---")
    hits = 0
    total = 0
    for ke in known_events:
        date_str = ke["date"]
        event_text = ke["event"]
        cats = categorize_event(event_text)
        
        print("-" * 80)
        print(f"EVENT: {date_str} | Cats: {cats} | Text: {event_text}")
        
        if "uncategorized" in cats:
            print("STATUS: SKIPPED (Uncategorized category)")
            continue
            
        total += 1
        tol = 90 if args.strict else 180
        matched, ev, reason = check_match(ke, pred_events, tolerance_days=tol, strict=args.strict)
        if matched:
            hits += 1
            print(f"STATUS: HIT | Reason: {reason}")
            print(f"  Event Name: {ev.get('event')}")
            print(f"  Source: {ev.get('source')}")
            print(f"  Severity: {ev.get('max_sev', ev.get('severity'))}")
            print(f"  Fired Rules:")
            why_list = ev.get("max_why", ev.get("why", []))
            for w in why_list:
                print(f"    * {w}")
        else:
            print(f"STATUS: MISS")
            # Diagnostic analysis for the miss
            print("  [DIAGNOSTICS] Analyzing chart on event date...")
            from runtime.event_predictor_v2 import build_full_timeline, lookup, detect_triggers, detect_all_yogas, _age_at
            d = parse_date(date_str)
            if d:
                timeline = build_full_timeline(chart, levels=3)
                yogas = detect_all_yogas(chart)
                ds = lookup(timeline, d)
                tr = detect_triggers(chart, d, orb=2.5)
                age = _age_at(d, chart)
                
                print(f"    * Active Dasha: MD={ds.get(1,{}).get('md')} | AD={ds.get(2,{}).get('ad')} | PD={ds.get(3,{}).get('pd')}")
                print(f"    * Age: {age:.1f}")
                print(f"    * Key Transits on this date:")
                for t in tr:
                    print(f"      - {t.get('transit')} on natal {t.get('natal')} (Severity: {t.get('severity')} | Orb: {t.get('orb')}°)")
                print(f"    * Yogas present: {[y['name'] for y in yogas]}")

    accuracy_pct = (hits / total * 100) if total > 0 else 0.0
    print("\n" + "=" * 80)
    print(f"SUMMARY FOR {chart.get('name', args.slug).upper()}:")
    print(f"  Score: {hits}/{total} hits")
    print(f"  Accuracy: {accuracy_pct:.1f}%")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
