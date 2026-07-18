"""Analyze chunk coverage in incomplete _deep extractions."""
import json
from collections import Counter
from pathlib import Path

GEMMA = Path(__file__).resolve().parent.parent / "gemma_extractions"

for f in sorted(GEMMA.glob("*_deep.json")):
    d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
    if d.get("is_complete", True):
        continue
    rules = d.get("rules", [])
    idxs = [r.get("_chunk_idx", -1) for r in rules if isinstance(r.get("_chunk_idx"), int)]
    max_idx = max(idxs) if idxs else -1
    cnt = Counter(idxs)
    tot = d.get("n_chunks_total") or 0
    done = d.get("last_chunk_processed") or 0
    gaps = [i for i in range(done + 1) if i not in cnt and i <= done]
    print(f"\n=== {f.name} ===")
    print(f"  meta: last_chunk={done} total={tot} rules={len(rules)}")
    print(f"  rule chunk_idx: min={min(idxs) if idxs else 'n/a'} max={max_idx} unique={len(cnt)}")
    print(f"  chunks with 0 rules (0..{done}): {sum(1 for i in range(done+1) if cnt.get(i,0)==0)}")
    if tot:
        missing_after = list(range(done + 1, tot))
        print(f"  unprocessed chunks: {len(missing_after)} ({done+1}..{tot-1})")
