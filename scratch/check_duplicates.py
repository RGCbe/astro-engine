import sys
import os
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.corpus import EXCLUDED_BOOKS

def main():
    print("=" * 80)
    print("        CROSS-CHECKING DUPLICATE EXTRACTIONS & EXCLUSIONS")
    print("=" * 80)
    
    gemma_dir = Path("gemma_extractions")
    if not gemma_dir.exists():
        print("Error: gemma_extractions directory not found.")
        return
        
    all_files = [f.stem for f in gemma_dir.glob("*.json")]
    
    # Identify deep, gemma, and other versions
    deep_versions = {f[:-5] for f in all_files if f.endswith("_deep")}
    gemma_versions = {f[:-6] for f in all_files if f.endswith("_gemma")}
    
    overlap = sorted(list(deep_versions & gemma_versions))
    print(f"Found {len(overlap)} books that have both '_deep' and '_gemma' versions:\n")
    
    unhandled_duplicates = []
    
    for book in overlap:
        deep_file = f"{book}_deep"
        gemma_file = f"{book}_gemma"
        
        deep_ex = deep_file in EXCLUDED_BOOKS
        gemma_ex = gemma_file in EXCLUDED_BOOKS
        
        status = "OK"
        if not deep_ex and not gemma_ex:
            status = "WARNING: Neither version is excluded! (Loading duplicates)"
            unhandled_duplicates.append(book)
        elif deep_ex and gemma_ex:
            status = "NOTE: Both versions are excluded."
        else:
            preferred = deep_file if not deep_ex else gemma_file
            status = f"OK (Preferred version loaded: {preferred})"
            
        print(f"  * {book}:")
        print(f"    - {deep_file} (excluded={deep_ex})")
        print(f"    - {gemma_file} (excluded={gemma_ex})")
        print(f"    - Status: {status}\n")
        
    print("=" * 80)
    if unhandled_duplicates:
        print(f"FOUND {len(unhandled_duplicates)} UNHANDLED DUPLICATES (Both versions loaded):")
        for d in unhandled_duplicates:
            print(f"  - {d}")
    else:
        print("No unhandled duplicates found! The corpus filters out all redundant runs.")
    print("=" * 80)

if __name__ == "__main__":
    main()
