import sys
import json
from pathlib import Path

_RUNTIME = Path("f:/Atro/runtime")
sys.path.insert(0, str(_RUNTIME))

# Load extracted catalog
with open("f:/Atro/scratch/extracted_catalog.json", "r", encoding="utf-8") as f:
    extracted = json.load(f)

# Load category_engine catalog
from category_engine import CATEGORIES_CATALOG as cat_eng_catalog

# Load claude_categories catalog
from claude_categories import PHASE_710_CATALOG as claude_catalog

print(f"Loaded: Extracted = {len(extracted)}, CategoryEngine = {len(cat_eng_catalog)}, ClaudeCategories = {len(claude_catalog)}")

# Merge them with priority: extracted (lowest) < claude (medium) < category_engine (highest)
master_catalog = {}
master_catalog.update(extracted)

# For Claude's catalog, some might not have 'auspicious' key. Let's add default or match
for k, v in claude_catalog.items():
    if "auspicious" not in v:
        # Default based on name
        v["auspicious"] = not any(w in v["name"].lower() for w in ["loss", "death", "dispute", "roga", "marana", "clash", "retro", "break", "karz", "rin", "illness", "accident"])
    master_catalog[k] = v

# For CategoryEngine's catalog
for k, v in cat_eng_catalog.items():
    master_catalog[k] = v

print(f"Master merged catalog contains {len(master_catalog)} unique categories!")

# Save master catalog
out_path = Path("f:/Atro/scratch/master_catalog.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(master_catalog, f, indent=2, ensure_ascii=False)

print(f"Saved master catalog to {out_path}")
