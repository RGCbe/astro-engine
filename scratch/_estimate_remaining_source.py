"""Estimate unprocessed source text for incomplete _deep books."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BOOKS = Path(__file__).resolve().parent.parent / "Books"
GEMMA = Path(__file__).resolve().parent.parent / "gemma_extractions"


def smart_chunks(text: str, target_chars: int = 2500):
    """Line-aware chunking matching deep_v1 resume."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if text.count("\n\n") >= 3:
        paras = text.split("\n\n")
        buf, idx = "", 0
        for p in paras:
            p = p.strip()
            if not p:
                continue
            if buf and len(buf) + len(p) + 2 > target_chars:
                yield idx, buf
                idx += 1
                buf = p
            else:
                buf = (buf + "\n\n" + p).strip() if buf else p
        if buf:
            yield idx, buf
        return
    buf, idx = "", 0
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if buf and len(buf) + len(line) + 1 > target_chars:
            yield idx, buf
            idx += 1
            buf = line
        else:
            buf = (buf + "\n" + line) if buf else line
    if buf:
        yield idx, buf


for f in sorted(GEMMA.glob("*_deep.json")):
    d = json.loads(f.read_text(encoding="utf-8", errors="replace"))
    if d.get("is_complete", True):
        continue
    book = d["book"]
    tot = d["n_chunks_total"]
    done = d["last_chunk_processed"]
    src = BOOKS / f"{book}_extracted.txt"
    if not src.exists():
        print(f"{book}: NO local source")
        continue
    text = src.read_text(encoding="utf-8", errors="replace")
    chunks = list(smart_chunks(text))
    actual = len(chunks)
    target = tot
    # pick target_chars that best matches n_chunks_total
    best_tc, best_n = 2500, actual
    for tc in range(1500, 6000, 100):
        n = len(list(smart_chunks(text, tc)))
        if abs(n - target) < abs(best_n - target):
            best_tc, best_n = tc, n
    chunks = list(smart_chunks(text, best_tc))
    print(f"\n=== {book} ===")
    print(f"  source={src.stat().st_size:,}B chunks_meta={done}/{tot} sim={len(chunks)} tc={best_tc}")
    remaining = chunks[done + 1 :]
    rem_chars = sum(len(c) for _, c in remaining)
    print(f"  unprocessed chunks: {len(remaining)} chars={rem_chars:,}")
    if remaining:
        preview = remaining[0][1][:200].replace("\n", " ")
        print(f"  first unprocessed preview: {preview!r}...")
    if len(chunks) <= done:
        print("  NOTE: simulated chunks <= last_chunk_processed (may be complete)")
