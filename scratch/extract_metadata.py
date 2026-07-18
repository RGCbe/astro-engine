import sys
import inspect
import re
import json
from pathlib import Path

_RUNTIME = Path("f:/Atro/runtime")
sys.path.insert(0, str(_RUNTIME))

import event_predictor_v2

# Planet constants
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# Categorize suspicious words for inauspicious events
INAUSPICIOUS_WORDS = [
    "accident", "loss", "death", "dispute", "disruption", "confinement", "scandal",
    "illness", "default", "conflict", "break", "dispute", "lost", "crisis", "cut",
    "crash", "betrayal", "persecution"
]

def extract_metadata(name, obj):
    source_code = inspect.getsource(obj)
    docstring = obj.__doc__ or ""
    
    # 1. Extract name
    event_name = name.replace("event_", "").replace("_", " ").title()
    # Try to find return dict "event": "..."
    m_ev = re.search(r'["\']event["\']\s*:\s*[fr]?["\']([^"\']+)["\']', source_code)
    if m_ev:
        event_name = m_ev.group(1)
    elif docstring:
        first_line = docstring.strip().split("\n")[0]
        if len(first_line) < 60:
            event_name = first_line
            
    # 2. Extract bhava
    bhava = None
    # Try searching for _lord(lagna_idx, N)
    m_bh = re.search(r'_lord\(\s*lagna_idx\s*,\s*(\d+)\s*\)', source_code)
    if m_bh:
        bhava = int(m_bh.group(1))
    else:
        # Fallback: search for h1_lord, h2_lord, etc. E.g. h9_lord
        m_bh2 = re.search(r'h(\d+)_lord', source_code)
        if m_bh2:
            bhava = int(m_bh2.group(1))
            
    # 3. Extract karakas
    karakas = []
    # Find all strings like "Sun", "Moon", etc. that are matched in conditions
    # e.g., == "Sun", == 'Moon', in ("Sun", "Moon"), or similar
    matches = re.findall(r'==\s*["\'](' + '|'.join(PLANETS) + r')["\']', source_code)
    for m in matches:
        if m not in karakas:
            karakas.append(m)
    # Check other references
    for p in PLANETS:
        if p not in karakas and re.search(r'\b' + p + r'\b', source_code):
            karakas.append(p)
            
    # 4. Extract age guard
    min_age = 0
    max_age = 99
    # e.g. age < 15 or age > 85
    m_age_lt = re.search(r'age\s*<\s*(\d+)', source_code)
    if m_age_lt:
        min_age = int(m_age_lt.group(1))
    m_age_gt = re.search(r'age\s*>\s*(\d+)', source_code)
    if m_age_gt:
        max_age = int(m_age_gt.group(1))
        
    # Check if there is an combined statement like age < 18 or age > 75
    # or age_guard or similar
    
    # 5. Extract auspiciousness
    auspicious = True
    combined_text = (name + " " + event_name).lower()
    if any(w in combined_text for w in INAUSPICIOUS_WORDS):
        auspicious = False
        
    # 6. Extract source
    source = "Vedic Astrology classic"
    m_src = re.search(r'["\']source["\']\s*:\s*["\']([^"\']+)["\']', source_code)
    if m_src:
        source = m_src.group(1)
    elif docstring:
        # search for something like "Source: BPHS" in docstring
        m_doc_src = re.search(r'Source:\s*([^\n\.]+)', docstring, re.IGNORECASE)
        if m_doc_src:
            source = m_doc_src.group(1).strip()
            
    return {
        "name": event_name,
        "bhava": bhava,
        "karakas": karakas,
        "age_guard": (min_age, max_age),
        "auspicious": auspicious,
        "source": source
    }

# Run extraction on all 190 functions
catalog = {}
for name, obj in inspect.getmembers(event_predictor_v2):
    if name.startswith("event_") and inspect.isfunction(obj):
        if obj.__module__ == "event_predictor_v2":
            catalog[name] = extract_metadata(name, obj)

print(f"Extracted {len(catalog)} category configs.")

# Write a preview of first 5
for k, v in list(catalog.items())[:5]:
    print(f"\n{k}: {v}")

# Save the full extracted catalog to a file
out_path = Path("f:/Atro/scratch/extracted_catalog.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(catalog, f, indent=2, ensure_ascii=False)

print(f"Saved complete catalog to {out_path}")
