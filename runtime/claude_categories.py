"""
Dynamic Declarative Category Compiler — Unifies predictive coverage across OLD and NEW engines.
Identifies all missing categories in the OLD engine (event_predictor_v2.py) and automatically
compiles them from category_catalog.py into dynamic event_* functions at runtime.
"""
import sys
import inspect
import json
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(_RUNTIME))

from category_catalog import CATEGORIES_CATALOG
from vedic_core import RASIS, RASI_LORDS, DIGNITIES

# Helper core functions
def _h(pos, p): return pos[p]["house"] if p in pos else None
def _dig(pos, p): return DIGNITIES.get((p, pos[p]["rasi"]), "neutral") if p in pos else "neutral"
def _lord(lagna_idx, h): return RASI_LORDS[RASIS[(lagna_idx + h - 1) % 12]]

def _build_event_fn(cat_id, cfg):
    """Generate an event_* callable from config — same signature as hand-written ones."""
    bhava = cfg["bhava"]
    karakas = cfg["karakas"]
    min_age, max_age = cfg["age_guard"]
    name = cfg["name"]
    source = cfg["source"]
    auspicious = cfg["auspicious"]

    def event_fn(chart, ds, tr, yogas, age):
        if age < min_age or age > max_age:
            return None
        pos = chart["positions"]
        lagna_idx = chart.get("lagna_idx", 0)
        h_lord = _lord(lagna_idx, bhava) if bhava else None
        md = ds.get(1, {}).get("md")
        ad = ds.get(2, {}).get("ad")
        pd = ds.get(3, {}).get("pd")
        score = 0.0
        why = []

        # 1. House lord activation
        if h_lord:
            if md == h_lord:
                score += 3; why.append(f"{bhava}L ({h_lord}) MD")
            elif ad == h_lord:
                score += 2; why.append(f"{bhava}L AD")
            elif pd == h_lord:
                score += 1; why.append(f"{bhava}L PD")

        # 2. Karaka activation
        for k in karakas:
            if md == k: score += 2; why.append(f"{k} (karaka) MD")
            elif ad == k: score += 1.5; why.append(f"{k} AD")
            elif pd == k: score += 0.5; why.append(f"{k} PD")

        # 3. Natal placement booster
        for k in karakas:
            kh = _h(pos, k)
            if kh in [1, 5, 9, 10, 11]:
                score += 1.0; why.append(f"{k} well-placed in H{kh}")
            elif kh in [6, 8, 12]:
                if not auspicious:
                    score += 1.5; why.append(f"{k} in dusthana H{kh}")

        # 4. Transit booster
        for k in karakas:
            t = next((t for t in tr if t.get("transit") == k
                      and t.get("severity") in ("MEDIUM", "HIGH", "VERY HIGH")), None)
            if t:
                score += 1.5; why.append(f"transit {k} active")

        # 5. Threshold gate
        threshold = 4.0 if auspicious is not None else 3.0
        if score < threshold:
            return None

        return {
            "event": f"{name} Event",
            "category": cat_id.replace("event_", ""),
            "severity": min(5, int(score // 2 + 1)),
            "yoga": None,
            "why": why,
            "source": source,
        }

    event_fn.__name__ = cat_id
    event_fn.__doc__ = f"{name} (auto-generated declarative). Source: {source}"
    return event_fn

# Compile dynamic patterns
def compile_dynamic_patterns():
    """Reads all categories and compiles only the ones missing in event_predictor_v2."""
    import event_predictor_v2
    
    # Get all hand-written event_* functions in event_predictor_v2
    existing_fns = set(name for name, obj in inspect.getmembers(event_predictor_v2) if name.startswith("event_"))
    
    patterns = []
    for cat_id, cfg in CATEGORIES_CATALOG.items():
        full_id = cat_id if cat_id.startswith("event_") else f"event_{cat_id}"
        
        # If already implemented imperatively, do not overwrite it
        if full_id in existing_fns:
            continue
            
        # Dynamically compile declarative configuration
        fn = _build_event_fn(full_id, cfg)
        globals()[full_id] = fn
        patterns.append(fn)
        
    return patterns

# This is loaded at the end of event_predictor_v2.py
ALL_CATALOG_PATTERNS = compile_dynamic_patterns()
