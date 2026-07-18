import json
from pathlib import Path

# Load master catalog JSON
with open("f:/Atro/scratch/master_catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

# Format as python dict
out_lines = [
    '"""',
    'Unified Master Category Catalog — 314 Astrological Prediction Categories.',
    'This is the single source of truth for both the OLD and NEW timeline engines.',
    '"""',
    "",
    "CATEGORIES_CATALOG = {"
]

for cat_id, cfg in sorted(catalog.items()):
    out_lines.append(f'    "{cat_id}": {{')
    out_lines.append(f'        "name": {json.dumps(cfg["name"], ensure_ascii=False)},')
    out_lines.append(f'        "bhava": {cfg["bhava"]},')
    
    # Karakas formatting
    karakas_str = ", ".join(f'"{k}"' for k in cfg["karakas"])
    out_lines.append(f'        "karakas": [{karakas_str}],')
    
    # Age guard formatting
    out_lines.append(f'        "age_guard": ({cfg["age_guard"][0]}, {cfg["age_guard"][1]}),')
    
    # Auspicious formatting
    out_lines.append(f'        "auspicious": {cfg["auspicious"]},')
    
    # Source formatting
    out_lines.append(f'        "source": {json.dumps(cfg["source"], ensure_ascii=False)},')
    
    out_lines.append("    },")

out_lines.append("}")
out_lines.append("")

# Write to file
target_path = Path("f:/Atro/runtime/category_catalog.py")
target_path.write_text("\n".join(out_lines), encoding="utf-8")

print(f"Successfully wrote {len(catalog)} categories to {target_path}")
