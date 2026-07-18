#!/usr/bin/env python3
"""Find target_chars that matches n_chunks_total for a book."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_workbench"))
from _deep_extract import _smart_chunks, calibrate_target_chars  # noqa: E402

book = sys.argv[1] if len(sys.argv) > 1 else "Jataka_Bharanam"
text = (ROOT / "Books" / f"{book}_extracted.txt").read_text(encoding="utf-8", errors="replace")
deep = json.loads((ROOT / "gemma_extractions" / f"{book}_deep.json").read_text(encoding="utf-8"))
n_meta = int(deep.get("n_chunks_total") or 0)
last = int(deep.get("last_chunk_processed", -1))
print(f"meta n_total={n_meta} last_done={last}")

best = []
for tc in range(400, 12000, 25):
    n = len(list(_smart_chunks(text, tc)))
    best.append((abs(n - n_meta), n, tc))
best.sort(key=lambda x: x[0])
print("top matches to meta:")
for d, n, tc in best[:8]:
    print(f"  tc={tc} n={n} delta={d}")

tc_cal = calibrate_target_chars(text, n_meta)
n_cal = len(list(_smart_chunks(text, tc_cal)))
print(f"calibrate_target_chars -> tc={tc_cal} n={n_cal}")

# chunk indices in rules
idxs = [r.get("_chunk_idx") for r in deep.get("rules", []) if isinstance(r.get("_chunk_idx"), int)]
if idxs:
    print(f"rules _chunk_idx: min={min(idxs)} max={max(idxs)} unique={len(set(idxs))}")
