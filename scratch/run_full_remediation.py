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
LOGS_DIR.mkdir(exist_ok=True)

# 1. Level C Books (Needs OCR + Initialization + LLM Extraction)
LEVEL_C_BOOKS = [
    {"name": "Dhruva_Nadi_Satyacharya", "lang": "eng"}, # Short 10 pages for quick baseline
    {"name": "Jataka_Chandrika_Kalidas", "lang": "eng"},
    {"name": "Stree_Jataka_Varahamihira", "lang": "eng"},
    {"name": "Bhrigu_Nadi_TMRao", "lang": "eng+hin+san"},
    {"name": "Gochar_Phaladeepika", "lang": "eng+hin+san"},
    {"name": "Jataka_Tattvam_Kadalangudi", "lang": "eng+hin+san"},
    {"name": "Roots_of_Nadi_Naik", "lang": "eng"},
    {"name": "Mansagari_Sanskrit", "lang": "eng+hin+san"}
]

# 2. Level B Books (Has OCR, Needs Initialization + LLM Extraction)
LEVEL_B_BOOKS = [
    "Brihat_Jataka_Sastri",
    "Tajik_Adawal_Encyclopedia",
    "Brihat_Jataka",
    "Saravali",
    "Lal_Kitab_Original",
    "Jaimini_Sutras",
    "Phaladeepika",
    "Hora_Sara"
]

def run_cmd(cmd, check=True):
    print(f"[+] Executing: {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if r.returncode != 0 and check:
        print(f"[-] Command failed with return code {r.returncode}")
        print(f"[-] Stdout: {r.stdout}")
        print(f"[-] Stderr: {r.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return r.returncode, r.stdout, r.stderr

def main():
    log_file = LOGS_DIR / f"remediation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    sys.stdout = open(log_file, "w", encoding="utf-8")
    sys.stderr = sys.stdout
    
    print("=" * 80)
    print(f"  ASTRO ENGINE EXTRACTION REMEDIATION MASTER PIPELINE")
    print(f"  Start Time: {datetime.now().isoformat()}")
    print("=" * 80)
    
    # Verify VPS Environment
    if not (ROOT / "venv").exists():
        print("[-] Error: virtual env venv/ not found. Exiting.")
        sys.exit(1)
        
    python_bin = str(ROOT / "venv" / "bin" / "python")
    
    # PHASE 1: OCR & JSON Initialization for Level C
    print("\n" + "=" * 50)
    print("  PHASE 1: OCR & INITIALIZATION FOR LEVEL C")
    print("=" * 50)
    
    for book in LEVEL_C_BOOKS:
        name = book["name"]
        lang = book["lang"]
        txt_path = BOOKS_DIR / f"{name}_extracted.txt"
        pdf_path = BOOKS_DIR / f"{name}.pdf"
        
        # 1. OCR (if text file doesn't exist or is empty)
        if not txt_path.exists() or txt_path.stat().st_size < 100:
            if not pdf_path.exists():
                print(f"[-] Warning: PDF {pdf_path} not found. Skipping OCR.")
                continue
            print(f"\n[*] Running Parallel NVIDIA NIM OCR for {name}...")
            # We use 3 parallel workers to safely run near the 40 RPM limit
            run_cmd([python_bin, "scratch/ocr_nvidia_parallel.py", "--pdf", f"{name}.pdf", "--workers", "3"])
        else:
            print(f"[+] OCR text file already exists for {name} ({txt_path.stat().st_size / 1024:.1f} KB). Skipping OCR.")
            
        # 2. JSON Initialization (if rules are currently corrupted/missing)
        json_path = GEMMA_DIR / f"{name}_deep.json"
        # We initialize if is_complete is false and rules are empty, or if we want a fresh start
        # Wait, since they were 100% corrupted, we definitely want to initialize them
        import json
        needs_init = True
        if json_path.exists():
            try:
                content = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
                # If it already has rules and is_complete is true, skip
                if content.get("is_complete") and content.get("n_rules_total", 0) > 41:
                    needs_init = False
                    print(f"[+] {name} already has complete healthy extractions. Skipping init.")
            except:
                pass
                
        if needs_init:
            print(f"[*] Initializing {name}_deep.json for extraction...")
            run_cmd([python_bin, "scratch/initialize_deep_json.py", name])
            
    # PHASE 2: JSON Initialization for Level B (Resetting cut-off books)
    print("\n" + "=" * 50)
    print("  PHASE 2: INITIALIZATION FOR LEVEL B (RESETTING)")
    print("=" * 50)
    
    for name in LEVEL_B_BOOKS:
        json_path = GEMMA_DIR / f"{name}_deep.json"
        needs_init = True
        if json_path.exists():
            try:
                content = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
                # Level B books currently have <15% chunk coverage. We check if coverage is low.
                # If coverage is already 100% (e.g. from a prior run), we skip resetting
                n_total = content.get("n_chunks_total", 0)
                last_ch = content.get("last_chunk_processed", -1)
                is_comp = content.get("is_complete", False)
                rules_cnt = content.get("n_rules_total", 0)
                
                # If chunk coverage is > 80% or it has complete rules, skip resetting
                if n_total > 0 and (last_ch + 1) / n_total > 0.80 and is_comp and rules_cnt > 100:
                    needs_init = False
                    print(f"[+] {name} already has high chunk coverage ({last_ch+1}/{n_total}). Skipping reset.")
            except Exception as e:
                print(f"[-] Warning reading {name} json: {e}")
                
        if needs_init:
            print(f"[*] Resetting {name}_deep.json for clean full extraction...")
            run_cmd([python_bin, "scratch/initialize_deep_json.py", name])
            
    # PHASE 3: Run Sequential Background Extraction Queue
    print("\n" + "=" * 50)
    print("  PHASE 3: RUN SEQUENTIAL EXTRACTION QUEUE")
    print("=" * 50)
    
    all_target_books = [
        "Dhruva_Nadi_Satyacharya",
        "Jataka_Chandrika_Kalidas",
        "Stree_Jataka_Varahamihira",
        "Bhrigu_Nadi_TMRao",
        "Gochar_Phaladeepika",
        "Jataka_Tattvam_Kadalangudi",
        "Roots_of_Nadi_Naik",
        "Carmen_Astrologicum_Dorotheus",
        "Matheseos_Firmicus_Vol1",
        "Matheseos_Firmicus_Vol2",
        "Mansagari_Sanskrit",
        "Chandra_Kala_Nadi_Santhanam"
    ] + LEVEL_B_BOOKS
    
    for name in all_target_books:
        json_path = GEMMA_DIR / f"{name}_deep.json"
        if not json_path.exists():
            print(f"[-] Skipped {name}: initialized JSON does not exist.")
            continue
            
        import json
        try:
            content = json.loads(json_path.read_text(encoding="utf-8", errors="replace"))
            if content.get("is_complete"):
                print(f"[+] {name} is already complete. Skipping extraction.")
                continue
        except Exception as e:
            print(f"[-] Error reading {name} json before extraction: {e}")
            continue
            
        print(f"\n[*] Starting LLM Extraction for {name} ...")
        # Run _deep_extract.py with --resume and --vault-direct
        # Note: we use --vault-direct to unlock keys directly in-process
        ret, stdout, stderr = run_cmd([python_bin, "_workbench/_deep_extract.py", "--book", name, "--resume", "--vault-direct"], check=False)
        if ret == 0:
            print(f"[OK] Completed LLM extraction for {name}.")
        else:
            print(f"[FAIL] LLM extraction failed or hit quota limits for {name}. Continuing to next book.")
            
    print("\n" + "=" * 50)
    print("  PHASE 4: FINAL RESTART & VERIFY")
    print("=" * 50)
    
    # Restart astro-engine
    print("[*] Restarting PM2 astro-engine service...")
    run_cmd(["pm2", "restart", "astro-engine"], check=False)
    time.sleep(5)
    run_cmd(["pm2", "status"], check=False)
    
    print(f"\n[+] Master Remediation Pipeline finished at {datetime.now().isoformat()}!")

if __name__ == "__main__":
    main()
