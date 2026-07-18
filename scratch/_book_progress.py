#!/usr/bin/env python3
import json
from pathlib import Path

books = [
    "Sarvartha_Chintamani",
    "KP_Reader_3_Predictive",
    "Bhrigu_Samhita",
    "Jataka_Bharanam",
    "BPHS1",
]
root = Path("/opt/astro/gemma_extractions")
for book in books:
    p = root / f"{book}_deep.json"
    if not p.exists():
        print(f"{book}: MISSING")
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    last = int(d.get("last_chunk_processed", -1))
    total = int(d.get("n_chunks_total") or 0)
    done = last + 1
    miss = 100 * (total - done) / total if total else 0
    print(
        f"{book}: {done}/{total} missing={miss:.1f}% "
        f"rules={d.get('n_rules_total')} complete={d.get('is_complete')}"
    )
