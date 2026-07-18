import os
import io
import sys
import time
import base64
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import fitz
from PIL import Image
from openai import OpenAI

# Add vault path to import key decryptor
vault_root = "/root/api-expense-manager"
if os.path.exists(vault_root) and vault_root not in sys.path:
    sys.path.insert(0, vault_root)

def get_nvidia_key():
    # If run on Windows local, read from env
    if os.name == "nt":
        return os.environ.get("NVIDIA_API_KEY"), "https://integrate.api.nvidia.com/v1"
        
    # If run on VPS, read from decrypted vault database
    try:
        import models
        import crypto
        env_file = Path(vault_root) / ".env"
        pwd = ""
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("VAULT_MASTER_PASSWORD="):
                    pwd = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
        models.init_db()
        salt_hex = models.get_meta("vault_salt")
        if not pwd or not salt_hex:
            return None, None
        crypto.unlock_vault(pwd, bytes.fromhex(salt_hex))
        
        for k in models.get_all_keys():
            if k.get("provider") == "nvidia" and k.get("status") == "active":
                api_key = crypto.decrypt_secret(k["api_key_encrypted"])
                base_url = k.get("base_url", "https://integrate.api.nvidia.com/v1")
                return api_key, base_url
    except Exception as e:
        print(f"[-] Vault unlock fail: {e}")
    return None, None

def process_page(page_idx, pdf_path, temp_dir, api_key, base_url, dpi):
    out_file = temp_dir / f"page_{page_idx}.txt"
    if out_file.exists() and out_file.stat().st_size > 10:
        return page_idx, True # Already processed
        
    client = OpenAI(api_key=api_key, base_url=base_url)
    model_name = "meta/llama-3.2-11b-vision-instruct"
    
    # Open PDF page-by-page in-thread to avoid PyMuPDF thread sharing issues
    doc = fitz.open(pdf_path)
    page = doc[page_idx - 1]
    
    # Render page to PNG
    pix = page.get_pixmap(dpi=dpi)
    img_data = pix.tobytes("png")
    base64_image = base64.b64encode(img_data).decode("utf-8")
    
    prompt = (
        "Transcribe the text in this image page verbatim. "
        "Keep any tables, verses, or formatting clean. "
        "If the page is bilingual (e.g. Sanskrit/Hindi and English), transcribe both. "
        "Output ONLY the transcribed text and nothing else."
    )
    
    # Retry loop with exponential backoff for rate limits (HTTP 429)
    delay = 1.0
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                                }
                            ]
                        }
                    ],
                max_tokens=2500,
                temperature=0.1
            )
            text = resp.choices[0].message.content.strip()
            out_file.write_text(text, encoding="utf-8")
            return page_idx, False
        except Exception as e:
            err_s = str(e)
            is_rate_limit = "429" in err_s or "rate_limit" in err_s.lower() or "too many requests" in err_s.lower()
            if is_rate_limit:
                print(f"  [!] Page {page_idx} hit rate limit. Retrying in {delay:.1f}s...")
                time.sleep(delay)
                delay *= 2.0
            else:
                print(f"  [-] Page {page_idx} error: {err_s[:150]}")
                time.sleep(2.0)
                
    # Fallback / failure write
    out_file.write_text(f"[ERROR: OCR API failed on page {page_idx}]", encoding="utf-8")
    return page_idx, False

def ocr_pdf_parallel(pdf_path: Path, txt_path: Path, max_workers: int = 5, dpi: int = 150):
    api_key, base_url = get_nvidia_key()
    if not api_key:
        print("[-] Error: Active NVIDIA API key not found.")
        sys.exit(1)
        
    print(f"[+] Connected to NVIDIA NIM API. Base URL: {base_url}")
    print(f"[+] PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    doc.close()
    
    # Create temp folder for page segments
    temp_dir = pdf_path.parent / f"tmp_{pdf_path.stem}"
    temp_dir.mkdir(exist_ok=True)
    
    print(f"[+] Starting Parallel OCR with {max_workers} workers for {total_pages} pages...")
    print(f"[+] Temp directory for segments: {temp_dir}")
    
    start_time = time.time()
    
    # Execute thread pool
    completed_count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_page, idx, pdf_path, temp_dir, api_key, base_url, dpi): idx
            for idx in range(1, total_pages + 1)
        }
        
        for future in as_completed(futures):
            page_idx = futures[future]
            try:
                page_idx, skipped = future.result()
                completed_count += 1
                if not skipped:
                    pct = (completed_count / total_pages) * 100
                    print(f"[+] Page {page_idx}/{total_pages} done ({pct:.1f}%)")
            except Exception as exc:
                print(f"[-] Page {page_idx} generated an exception: {exc}")
                
    # Concatenate all files in order
    print("[+] Concatenating pages into final output...")
    all_text = []
    for idx in range(1, total_pages + 1):
        page_file = temp_dir / f"page_{idx}.txt"
        if page_file.exists():
            all_text.append(f"\n====== PAGE {idx} ======\n")
            all_text.append(page_file.read_text(encoding="utf-8", errors="replace"))
        else:
            all_text.append(f"\n====== PAGE {idx} ======\n")
            all_text.append(f"[ERROR: Page {idx} file missing]")
            
    txt_path.write_text("".join(all_text), encoding="utf-8")
    
    # Clean up temp files
    print("[+] Cleaning up temp files...")
    for idx in range(1, total_pages + 1):
        page_file = temp_dir / f"page_{idx}.txt"
        if page_file.exists():
            page_file.unlink()
    try:
        temp_dir.rmdir()
    except:
        pass
        
    elapsed = time.time() - start_time
    print(f"[OK] Completed OCR. Output saved to {txt_path} in {elapsed/60:.2f} minutes.")

def main():
    ap = argparse.ArgumentParser(description="OCR scanned astrology PDFs using NVIDIA NIM Vision API in Parallel")
    ap.add_argument("--pdf", required=True, help="Filename of the PDF under books/")
    ap.add_argument("--workers", type=int, default=5, help="Number of parallel workers")
    ap.add_argument("--dpi", type=int, default=150, help="Rendering DPI (default 150)")
    args = ap.parse_args()
    
    root = Path(__file__).resolve().parents[1]
    books_dir = root / "books"
    if not books_dir.exists():
        books_dir = root / "Books"
        
    pdf_path = books_dir / args.pdf
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)
        
    base_name = pdf_path.stem
    txt_path = books_dir / f"{base_name}_extracted.txt"
    
    ocr_pdf_parallel(pdf_path, txt_path, max_workers=args.workers, dpi=args.dpi)

if __name__ == "__main__":
    main()
