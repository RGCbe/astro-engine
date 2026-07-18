import sys
import json
from pathlib import Path

# Reconfigure stdout to support unicode/utf-8
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_RUNTIME = Path("f:/Atro/runtime")
sys.path.insert(0, str(_RUNTIME))

print("==================================================")
print("RUNNING CROSS-ENGINE BALANCING VERIFICATION SUITE")
print("==================================================")

# 1. Import Category Engine
try:
    from category_engine import category_engine_instance
    print("[OK] Successfully imported category_engine_instance.")
except Exception as e:
    print(f"[FAIL] Failed to import category_engine_instance: {e}")
    sys.exit(1)

# 2. Import Event Predictor V2
try:
    import event_predictor_v2
    print("[OK] Successfully imported event_predictor_v2.")
except Exception as e:
    print(f"[FAIL] Failed to import event_predictor_v2: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Check Category Counts
new_catalog = category_engine_instance.catalog
old_patterns = event_predictor_v2.ALL_PATTERNS_V2

print(f"\nNEW Engine Category Catalog Count: {len(new_catalog)}")
print(f"OLD Engine Event Functions Count:   {len(old_patterns)}")

# 4. Check Set Parity
new_cats = set(new_catalog.keys())
old_cats = set(fn.__name__ for fn in old_patterns)

# Map category names to function names
new_fn_names = set(cat_id if cat_id.startswith("event_") else f"event_{cat_id}" for cat_id in new_cats)

print(f"\nComparing Sets:")
print(f"  Mapped NEW Function Names: {len(new_fn_names)}")
print(f"  OLD Function Names:        {len(old_cats)}")

missing_in_old = new_fn_names - old_cats
missing_in_new = old_cats - new_fn_names

if missing_in_old:
    print(f"[FAIL] Missing in OLD: {missing_in_old}")
if missing_in_new:
    print(f"[FAIL] Missing in NEW: {missing_in_new}")

if len(new_fn_names) == 314 and len(old_cats) == 314 and len(missing_in_old) == 0 and len(missing_in_new) == 0:
    print("\n[SUCCESS] PERFECT BALANCE ACHIEVED! Both engines support exactly the same 314 categories!")
else:
    print("\n[FAIL] ENGINES ARE NOT BALANCED. Please verify the merge logic.")
    sys.exit(1)

# 5. Run Live Scan Test (Sanity Verification)
try:
    chart_path = Path("f:/Atro/charts/joseph_vijay_chart.json")
    if not chart_path.exists():
        chart_path = Path("f:/Atro/charts/manoj_chart.json")
        
    chart = json.load(open(chart_path, "r", encoding="utf-8"))
    print(f"\nRunning test scan on chart: {chart.get('name', 'Manoj')} ({chart_path.name})...")
    
    # NEW engine scan
    new_events = category_engine_instance.scan_lifetime(chart, 1996, 2026, sample_days=14, min_severity=3)
    new_bands = category_engine_instance.collapse_consecutive(new_events)
    print(f"  NEW Engine Scan: Successfully generated {len(new_bands)} lifecycle bands.")
    
    # OLD engine scan
    old_events = event_predictor_v2.scan_lifetime_v2(chart, 1996, 2026, sample_days=14, min_severity=3)
    old_bands = event_predictor_v2.collapse_consecutive(old_events)
    print(f"  OLD Engine Scan: Successfully generated {len(old_bands)} lifecycle bands.")
    
    print("\n[SUCCESS] Verification Test Passed 100%! Dynamic engine execution is completely stable.")
except Exception as e:
    print(f"[FAIL] Live scan test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
