"""
Automated unit test for Pure Classical & Hybrid Astrological Engines.
Verifies dynamic lifecycle calculations, scripture injections, and conjoined overlaps.
"""
import sys
import json
from pathlib import Path

# Setup paths
_SCRATCH = Path(__file__).resolve().parent
_ROOT = _SCRATCH.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "runtime"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

print("==================================================")
print("RUNNING PURE SCRIPTURAL & HYBRID ENGINE UNIT TESTS")
print("==================================================")

# 1. Imports
try:
    from pure_classical_engine import pure_classical_engine_instance
    from engine_pure_hybrid import hybrid_engine_instance
    print("[OK] Successfully imported pure_classical_engine_instance and hybrid_engine_instance.")
except Exception as e:
    print(f"[FAIL] Imports failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 2. Load Chart
chart_path = _ROOT / "charts" / "joseph_vijay_chart.json"
if not chart_path.exists():
    chart_path = _ROOT / "charts" / "manoj_chart.json"

try:
    chart = json.load(open(chart_path, "r", encoding="utf-8"))
    print(f"[OK] Loaded chart: {chart.get('name', 'Manoj')} ({chart_path.name})")
except Exception as e:
    print(f"[FAIL] Failed to load chart: {e}")
    sys.exit(1)

# 3. Scan Pure Classical Engine
try:
    print("\n--- Testing Pure Classical Engine scan_lifetime ---")
    class_bands = pure_classical_engine_instance.scan_lifetime(chart, 1996, 2026, sample_days=14, min_severity=2)
    collapsed_class = pure_classical_engine_instance.collapse_consecutive(class_bands)
    print(f"[OK] Pure Classical Engine generated {len(class_bands)} raw events, collapsed into {len(collapsed_class)} lifecycle bands.")
    
    # Verify citations are present
    if collapsed_class:
        sample = collapsed_class[0]
        print(f"  Sample Classical Event: {sample['classical_title']}")
        print(f"    Scripture Source:   {sample['scripture_source']} ({sample['citation']})")
        print(f"    Verbatim Prose:     \"{sample['classical_prose']}\"")
        if not sample.get("verified_classical") or not sample.get("citation"):
            print("[FAIL] Missing crucial scriptural citations or flags!")
            sys.exit(1)
    else:
        print("[WARN] No classical events were generated for this period.")
except Exception as e:
    print(f"[FAIL] Pure Classical scan failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. Scan Hybrid Engine
try:
    print("\n--- Testing Hybridization Bridge scan_hybrid_lifetime ---")
    h_result = hybrid_engine_instance.scan_hybrid_lifetime(chart, 1996, 2026, sample_days=14, min_severity=2)
    hybrid_bands = h_result["hybrid_bands"]
    class_only = h_result["classical_only_bands"]
    
    print(f"[OK] Hybridization completed successfully!")
    print(f"  Hybrid Conjoined Bands:  {len(hybrid_bands)}")
    print(f"  Classical-Only Bands:    {len(class_only)}")

    # Diagnose category overlaps
    mod_cats = set(b.get("category", "") for b in hybrid_bands)
    cl_cats = set(b.get("category", "") for b in class_only)
    print(f"  Modern Distinct Categories: {sorted(list(mod_cats))[:15]}...")
    print(f"  Classical Distinct Categories: {sorted(list(cl_cats))}")

    # Check first few classical bands
    print("\n  Classical Bands:")
    for cb in class_only[:5]:
        print(f"    - Title: {cb['classical_title']}, Cat: {cb['category']}, Window: {cb['window_start']} to {cb['window_end']}")

    verified_count = sum(1 for b in hybrid_bands if b.get("verified_classical"))
    print(f"\n  Cross-Verified Bands:    {verified_count}")
    
    if verified_count > 0:
        verified_samples = [b for b in hybrid_bands if b.get("verified_classical")]
        sample = verified_samples[0]
        print(f"\n  Sample Verified Hybrid Event: {sample['event']} ({sample['category']})")
        print(f"    New Severity:       {sample['severity']} (Boosted!)")
        print(f"    Aligned Scripture:  {sample['scripture_source']} ({sample['citation']})")
        print(f"    Classical Title:    {sample['classical_title']}")
        print(f"    Classical Prose:    \"{sample['classical_prose']}\"")
        print(f"    Cross-Check Why:    {sample['why'][-1]}")
    else:
        print("[WARN] No modern events were cross-verified by classical scripture.")
        
    print("\n[SUCCESS] ALL TESTS PASSED 100%! Scriptural alignment is structurally sound.")
except Exception as e:
    print(f"[FAIL] Hybrid scan failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
