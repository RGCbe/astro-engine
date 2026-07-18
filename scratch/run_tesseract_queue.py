import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS_DIR = ROOT / "Books"
GEMMA_DIR = ROOT / "gemma_extractions"
LOGS_DIR = ROOT / "logs"

# Pure English books to process with local Tesseract CPU OCR
TESSERACT_BOOKS = [
    "Matheseos_Firmicus_Vol2",
    "Matheseos_Firmicus_Vol1",
    "Carmen_Astrologicum_Dorotheus",
    "Chandra_Kala_Nadi_Santhanam"
]

def run_cmd(cmd):
    print(f"[+] Executing: {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0:
        print(f"[-] Command failed with return code {r.returncode}")
        print(f"[-] Stdout: {r.stdout}")
        print(f"[-] Stderr: {r.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return r.returncode

def main():
    log_file = LOGS_DIR / f"tesseract_queue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    sys.stdout = open(log_file, "w", encoding="utf-8")
    sys.stderr = sys.stdout
    
    print("=" * 80)
    print(f"  ASTRO ENGINE TESSERACT OCR PARALLEL QUEUE")
    print(f"  Start Time: {datetime.now().isoformat()}")
    print("=" * 80)
    
    python_bin = str(ROOT / "venv" / "bin" / "python")
    
    for name in TESSERACT_BOOKS:
        txt_path = BOOKS_DIR / f"{name}_extracted.txt"
        pdf_path = BOOKS_DIR / f"{name}.pdf"
        
        # 1. Tesseract OCR (skip if already exists)
        if not txt_path.exists() or txt_path.stat().st_size < 100:
            if not pdf_path.exists():
                print(f"[-] Warning: PDF {pdf_path} not found. Skipping.")
                continue
            print(f"\n[*] Running Tesseract OCR for {name}...")
            # We use 'eng' since these are English translation books
            run_cmd([python_bin, "scratch/ocr_book.py", "--pdf", f"{name}.pdf", "--lang", "eng"])
        else:
            print(f"[+] OCR text file already exists for {name} ({txt_path.stat().st_size / 1024:.1f} KB). Skipping OCR.")
            
        # 2. JSON Initialization
        json_path = GEMMA_DIR / f"{name}_deep.json"
        needs_init = True
        if json_path.exists():
            try:
                import json
                content = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
                if content.get("is_complete") and content.get("n_rules_total", 0) > 41:
                    needs_init = False
                    print(f"[+] {name} already complete. Skipping init.")
            except:
                pass
                
        if needs_init:
            print(f"[*] Initializing {name}_deep.json for extraction...")
            run_cmd([python_bin, "scratch/initialize_deep_json.py", name])
            
    print(f"\n[+] Tesseract OCR Queue finished at {datetime.now().isoformat()}!")

if __name__ == "__main__":
    main()
