import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Add _workbench to sys.path so we can import _smart_chunks
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "_workbench"))

try:
    from _deep_extract import _smart_chunks, calibrate_target_chars
except ImportError:
    # Fallback to copy paste smart chunks if import fails on some envs
    def _smart_chunks(text: str, target_chars: int = 2500):
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

    def calibrate_target_chars(text: str, n_chunks_total: int) -> int:
        best_tc, best_n = 2500, len(list(_smart_chunks(text, 2500)))
        for tc in range(1500, 8000, 100):
            n = len(list(_smart_chunks(text, tc)))
            if abs(n - n_chunks_total) < abs(best_n - n_chunks_total):
                best_tc, best_n = tc, n
        return best_tc

def initialize_book(book_name: str, target_chars: int = 2500):
    books_dir = ROOT / "books"
    if not books_dir.exists():
        books_dir = ROOT / "Books"
        
    txt_path = books_dir / f"{book_name}_extracted.txt"
    if not txt_path.exists():
        print(f"[-] Error: OCR text file not found for {book_name} at {txt_path}")
        return False
        
    gemma_dir = ROOT / "gemma_extractions"
    json_path = gemma_dir / f"{book_name}_deep.json"
    backup_dir = gemma_dir / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    # 1. Backup if file exists
    if json_path.exists():
        backup_path = backup_dir / f"{book_name}_deep.json.bak"
        print(f"[+] Backing up existing JSON to {backup_path}")
        backup_path.write_bytes(json_path.read_bytes())
        
    # 2. Read text and chunk
    text = txt_path.read_text(encoding="utf-8", errors="replace")
    chunks = list(_smart_chunks(text, target_chars))
    n_chunks = len(chunks)
    print(f"[+] Text chunking: {n_chunks} chunks at target_chars={target_chars}")
    
    # 3. Create fresh JSON header
    header = {
        "book": book_name,
        "source_path": f"/opt/astro/Books/{book_name}_extracted.txt",
        "extracted_at": datetime.utcnow().isoformat(),
        "n_chunks_total": n_chunks,
        "target_chars": target_chars,
        "last_chunk_processed": -1,
        "n_rules_total": 0,
        "is_complete": False,
        "extractor": "deep_v1 (verbatim, anti-censor, page-chunked)",
        "rules": []
    }
    
    json_path.write_text(json.dumps(header, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Initialized {json_path} successfully!")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python initialize_deep_json.py <book_name> [target_chars]")
        sys.exit(1)
    tc = int(sys.argv[2]) if len(sys.argv) > 2 else 2500
    initialize_book(sys.argv[1], tc)
