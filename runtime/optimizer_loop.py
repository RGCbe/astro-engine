import os
import sys
import json
import random
import copy
from pathlib import Path
from datetime import datetime, timedelta

_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))

from category_engine import category_engine_instance, DEFAULT_WEIGHTS, WEIGHTS_PATH
from _battle_vijay import infer_event_valence, parse_date

def load_verified_charts():
    charts_dir = _ROOT / "charts"
    target_names = ["manoj_life_facts.json", "ar_rahman_chart.json", "indira_gandhi_chart.json"]
    verified = []
    for name in target_names:
        f = charts_dir / name
        if f.exists():
            try:
                c = json.load(open(f, "r", encoding="utf-8"))
                if "known_events" in c and len(c["known_events"]) > 0:
                    if name == "manoj_life_facts.json":
                        manoj_birth = charts_dir / "manoj_chart.json"
                        if manoj_birth.exists():
                            birth_data = json.load(open(manoj_birth, "r", encoding="utf-8"))
                            for k, v in birth_data.items():
                                if k != "known_events":
                                    c[k] = v
                    verified.append(c)
            except Exception as e:
                print(f"Skipping {name}: {e}")
    return verified

def evaluate_accuracy(weights, precalculated_charts):
    with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=4)
        
    total_events = 0
    total_hits = 0

    for chart, timeline, yogas, years_to_scan, events in precalculated_charts:
        if "birth" not in chart or "year" not in chart["birth"]:
            continue
            
        raw_preds = []
        for y in years_to_scan:
            year_preds = category_engine_instance.scan_year(chart, y, timeline=timeline, yogas=yogas, sample_days=15)
            for k, v in year_preds.items():
                raw_preds.append(v)
                
        preds = category_engine_instance.collapse_consecutive(raw_preds) if raw_preds else []
        
        # Check hits
        for ev in events:
            total_events += 1
            target_date = parse_date(ev["date"])
            target_cat = ev.get("atro_category", "")
            expected = infer_event_valence(ev)
            
            is_year_only = ev["date"].endswith("-01-01")
            tol = 180 if is_year_only else 60
            
            hit = False
            for pe in preds:
                pred_cat = pe.get("category", "")
                pred_event = pe.get("event", "").lower()
                
                is_match = False
                if target_cat and (target_cat in pred_cat or target_cat in pred_event):
                    is_match = True
                elif not target_cat and any(word in ev["event"].lower() for word in pred_cat.split("_")):
                    is_match = True
                    
                if is_match:
                    ws = parse_date(str(pe.get("window_start", ""))[:10])
                    we = parse_date(str(pe.get("window_end", ""))[:10])
                    if ws and we:
                        buf = timedelta(days=tol)
                        if (ws - buf) <= target_date <= (we + buf):
                            sev = pe.get("severity", 3)
                            is_auspicious = sev >= 3
                            if expected == "auspicious" and not is_auspicious:
                                continue
                            if expected == "inauspicious" and is_auspicious:
                                continue
                            hit = True
                            break
            if hit:
                total_hits += 1

    if total_events == 0: return 0.0
    return total_hits / total_events

def run_optimizer(iterations=3):
    print("Loading verified charts...")
    charts = load_verified_charts()
    print(f"Found {len(charts)} charts with verifiable events.")
    
    print("Pre-calculating dasha timelines and classical yogas...")
    from granular_dasha import build_full_timeline
    from comprehensive_yogas import detect_all_classical_yogas
    
    precalculated = []
    for chart in charts:
        if "birth" not in chart or "year" not in chart["birth"]:
            continue
        events = chart["known_events"]
        years_to_scan = set()
        for ev in events:
            td = parse_date(ev["date"])
            if td:
                years_to_scan.add(td.year)
                
        try:
            timeline = build_full_timeline(chart, levels=3)
            yogas = detect_all_classical_yogas(chart)
            precalculated.append((chart, timeline, yogas, list(years_to_scan), events))
        except Exception as e:
            print(f"Failed precalculating chart: {e}")
            
    # Load base weights
    if WEIGHTS_PATH.exists():
        best_weights = json.load(open(WEIGHTS_PATH, "r", encoding="utf-8"))
    else:
        best_weights = copy.deepcopy(DEFAULT_WEIGHTS)
        
    print("Evaluating baseline accuracy...")
    best_accuracy = evaluate_accuracy(best_weights, precalculated)
    print(f"Baseline Accuracy: {best_accuracy*100:.2f}%")
    
    keys = list(best_weights.keys())
    
    for i in range(iterations):
        # Mutate
        new_weights = copy.deepcopy(best_weights)
        k_to_mutate = random.choice(keys)
        delta = random.choice([-0.5, -0.25, 0.25, 0.5])
        
        # Don't let weights go below 0 for core things unless intended
        new_weights[k_to_mutate] += delta
        if new_weights[k_to_mutate] < 0.5:
            new_weights[k_to_mutate] = 0.5
            
        acc = evaluate_accuracy(new_weights, precalculated)
        
        print(f"Iteration {i+1}/{iterations}: Mutated {k_to_mutate} by {delta:+f} -> Accuracy: {acc*100:.2f}%")
        
        if acc > best_accuracy:
            print(f"*** NEW BEST WEIGHTS FOUND: {acc*100:.2f}% ***")
            best_accuracy = acc
            best_weights = new_weights
            
    # Re-save best
    with open(WEIGHTS_PATH, "w", encoding="utf-8") as f:
        json.dump(best_weights, f, indent=4)
        
    print(f"\nOptimization complete. Final best accuracy: {best_accuracy*100:.2f}%")
    return best_weights

if __name__ == "__main__":
    run_optimizer(iterations=3)
