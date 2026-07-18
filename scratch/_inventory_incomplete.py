#!/usr/bin/env python3
"""Inventory incomplete _deep extractions."""
import json
from pathlib import Path

GEMMA = Path(__file__).resolve().parent.parent / "gemma_extractions"
BOOKS = Path(__file__).resolve().parent.parent / "Books"

rows = []
for f in sorted(GEMMA.glob("*_deep.json")):
    d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
    if d.get("is_complete", True):
        continue
    tot = d.get("n_chunks_total") or 0
    done = d.get("last_chunk_processed") or 0
    miss = 100 * (1 - done / tot) if tot else 0
    book = d.get("book", f.stem.replace("_deep", ""))
    src = d.get("source_path", "")
    local_txt = BOOKS / f"{book}_extracted.txt"
    rows.append(
        {
            "file": f.name,
            "book": book,
            "done": done,
            "total": tot,
            "missing_pct": round(miss, 1),
            "rules": d.get("n_rules_total", len(d.get("rules", []))),
            "source_path": src,
            "local_txt_exists": local_txt.exists(),
            "local_txt_bytes": local_txt.stat().st_size if local_txt.exists() else 0,
        }
    )

print(f"{'file':<35} {'progress':>12} {'miss%':>6} {'rules':>6} {'local_txt':>10}")
print("-" * 80)
for r in rows:
    print(
        f"{r['file']:<35} {r['done']:>4}/{r['total']:<6} {r['missing_pct']:>5.1f}% "
        f"{r['rules']:>6} {'YES' if r['local_txt_exists'] else 'NO':>10}"
    )
