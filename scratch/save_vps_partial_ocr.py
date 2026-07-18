import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOOKS_DIR = ROOT / "Books"
if not BOOKS_DIR.exists():
    BOOKS_DIR = ROOT / "books"

def save_partial_nvidia(book_name: str):
    temp_dir = BOOKS_DIR / f"tmp_{book_name}"
    txt_path = BOOKS_DIR / f"{book_name}_extracted.txt"
    
    if not temp_dir.exists():
        print(f"[-] Temp dir for {book_name} does not exist. Skipping.")
        return False
        
    print(f"[+] Concatenating partial segments for {book_name} ...")
    # Find all page files in temp dir
    pages = []
    for f in temp_dir.iterdir():
        if f.name.startswith("page_") and f.name.endswith(".txt"):
            try:
                page_idx = int(f.name.split("_")[1].split(".")[0])
                pages.append((page_idx, f))
            except:
                pass
                
    if not pages:
        print(f"[-] No completed pages found in {temp_dir}.")
        return False
        
    # Sort by page index
    pages.sort()
    
    all_text = []
    for page_idx, page_file in pages:
        all_text.append(f"\n====== PAGE {page_idx} ======\n")
        all_text.append(page_file.read_text(encoding="utf-8", errors="replace"))
        
    txt_path.write_text("".join(all_text), encoding="utf-8")
    print(f"[OK] Saved {len(pages)} pages to {txt_path}.")
    
    # Clean up temp files
    print("[+] Cleaning up temp files...")
    for _, page_file in pages:
        page_file.unlink()
    try:
        temp_dir.rmdir()
    except Exception as e:
        print(f"[-] Could not delete temp dir: {e}")
    return True

def main():
    # Save Mansagari Sanskrit
    save_partial_nvidia("Mansagari_Sanskrit")
    
    # Run JSON initialization for all completed/partial books so they are ready for rule extraction
    books_to_init = [
        "Dhruva_Nadi_Satyacharya",
        "Jataka_Chandrika_Kalidas",
        "Stree_Jataka_Varahamihira",
        "Bhrigu_Nadi_TMRao",
        "Gochar_Phaladeepika",
        "Jataka_Tattvam_Kadalangudi",
        "Roots_of_Nadi_Naik",
        "Matheseos_Firmicus_Vol2",
        "Matheseos_Firmicus_Vol1",
        "Carmen_Astrologicum_Dorotheus",
        "Mansagari_Sanskrit"
    ]
    
    python_bin = sys.executable
    for book in books_to_init:
        txt_path = BOOKS_DIR / f"{book}_extracted.txt"
        if txt_path.exists() and txt_path.stat().st_size > 100:
            print(f"[*] Initializing JSON for {book}...")
            # Run initialize_deep_json.py inside the project root directory
            import subprocess
            r = subprocess.run([python_bin, "scratch/initialize_deep_json.py", book], cwd=str(ROOT))
            if r.returncode != 0:
                print(f"[-] Failed to initialize JSON for {book}")
                
if __name__ == "__main__":
    main()
