import sys
import json
from pathlib import Path
from datetime import datetime

_ROOT = Path("/opt/astro")
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "runtime"))

from runtime.event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from runtime._accuracy_scorer import check_match, categorize_event, parse_date, CAT_ALIASES
from engine.event_valence import infer_event_valence

# Load Rahman chart
chart_path = _ROOT / "charts" / "ar_rahman_chart.json"
chart = json.load(chart_path.open("r", encoding="utf-8"))

print(f"==========================================================================")
print(f"DEEP ASTROLOGICAL AUDIT: A.R. RAHMAN")
print(f"Birth Details: {chart['birth']['place']} | {chart['birth']['year']}-{chart['birth']['month']}-{chart['birth']['day']}")
print(f"Lagna: {chart['lagna']} | Janma Nakshatra: {chart['janma_nakshatra']}")
print(f"==========================================================================\n")

birth_yr = chart["birth"]["year"]
raw = scan_lifetime_v2(chart, birth_yr, birth_yr + 85, min_severity=2)
bands = collapse_consecutive(raw) if raw else []
ranked = rank_and_consume(bands) if bands else []
pred_events = bands + ranked

known_events = chart.get("known_events", [])

print("--- RUNNING PREDICTIONS FOR KNOWN EVENTS ---")
for ke in known_events:
    date_str = ke["date"]
    event_text = ke["event"]
    cats = categorize_event(event_text)
    
    print("-" * 80)
    print(f"EVENT: {date_str} | Cats: {cats} | Text: {event_text}")
    
    if "uncategorized" in cats:
        print("STATUS: SKIPPED (Uncategorized category)")
        continue
        
    matched, ev, reason = check_match(ke, pred_events, tolerance_days=180, strict=False)
    if matched:
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
