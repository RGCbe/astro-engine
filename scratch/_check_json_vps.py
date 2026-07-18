import glob
import json

for f in glob.glob("/opt/astro/gemma_extractions/*.json"):
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as file:
            data = json.load(file)
            if isinstance(data, list):
                print(f"JSON LIST: {f}")
    except Exception as e:
        print(f"ERROR: {f} -> {e}")
