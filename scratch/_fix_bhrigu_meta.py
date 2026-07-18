#!/usr/bin/env python3
"""Undo mistaken Bhrigu reconcile (133 chunks); restore meta 219."""
import json
from pathlib import Path

p = Path("/opt/astro/gemma_extractions/Bhrigu_Samhita_deep.json")
d = json.loads(p.read_text(encoding="utf-8"))
d["n_chunks_total"] = 219
d["is_complete"] = False
d.pop("target_chars", None)
p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
print("fixed", d["last_chunk_processed"], d["n_chunks_total"], d["is_complete"])
