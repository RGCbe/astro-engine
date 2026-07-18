import re
from pathlib import Path
t = Path(r"F:\astro\runtime\event_predictor_v2.py").read_text(encoding="utf-8")
cats = sorted(set(re.findall(r'"category"\s*:\s*"([^"]+)"', t)))
print(len(cats))
for c in cats:
    print(c)
