import os
import io
import sys
import time
import base64
import argparse
from pathlib import Path
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

def ocr_pdf_via_nvidia(pdf_path: Path, txt_path: Path, start_page: int = 1, end_page: int = None, dpi: int = 150):
    api_key, base_url = get_nvidia_key()
    if not api_key:
        print("[-] Error: Active NVIDIA API key not found.")
        sys.exit(1)
        
    print(f"[+] Connected to NVIDIA NIM API. Base URL: {base_url}")
    client = OpenAI(api_key=api_key, base_url=base_url)
    model_name = "meta/llama-3.2-11b-vision-instruct"
    
    print(f"[+] Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    
    last_page = end_page if end_page is not None else total_pages
    last_page = min(last_page, total_pages)
    
    print(f"[+] Total pages: {total_pages}. Processing pages {start_page} to {last_page}...")
    
    # Load existing checkpoint
    existing_pages = {}
    if txt_path.exists():
        content = txt_path.read_text(encoding="utf-8", errors="replace")
        parts = content.split("====== PAGE ")
        for part in parts:
            if not part.strip():
                continue
            lines = part.splitlines()
            try:
                page_num = int(lines[0].split(" ======")[0].strip())
                text = "\n".join(lines[1:])
                existing_pages[page_num] = text
            except:
                pass
        print(f"[+] Found checkpoint with {len(existing_pages)} already OCR'd pages.")

    all_text_blocks = []
    
    for page_num in range(total_pages):
        page_idx = page_num + 1
        
        # Keep pages outside of start/end range intact from old file if checkpointing
        if page_idx < start_page or page_idx > last_page:
            if page_idx in existing_pages:
                all_text_blocks.append(f"\n====== PAGE {page_idx} ======\n")
                all_text_blocks.append(existing_pages[page_idx])
            continue
            
        if page_idx in existing_pages and existing_pages[page_idx].strip():
            all_text_blocks.append(f"\n====== PAGE {page_idx} ======\n")
            all_text_blocks.append(existing_pages[page_idx])
            continue
            
        print(f"[*] OCR Processing page {page_idx}/{total_pages} via NVIDIA NIM ({model_name}) ...")
        page = doc[page_num]
        
        # Render page to high-quality image bytes
        pix = page.get_pixmap(dpi=dpi)
        img_data = pix.tobytes("png")
        
        # Encode image to base64
        base64_image = base64.b64encode(img_data).decode("utf-8")
        
        # Query NVIDIA Vision Model
        prompt = (
            "Transcribe the text in this image page verbatim. "
            "Keep any tables, verses, or formatting clean. "
            "If the page is bilingual (e.g. Sanskrit/Hindi and English), transcribe both. "
            "Output ONLY the transcribed text and nothing else."
        )
        
        start_time = time.time()
        retries = 3
        text = ""
        for attempt in range(retries):
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
                break
            except Exception as e:
                print(f"  [-] Attempt {attempt+1} failed: {e}")
                if attempt == retries - 1:
                    print("  [-] Skipping page due to persistent API errors.")
                    text = f"[ERROR: OCR API failed on page {page_idx}]"
                time.sleep(3)
                
        all_text_blocks.append(f"\n====== PAGE {page_idx} ======\n")
        all_text_blocks.append(text)
        
        # Save progress page-by-page
        current_content = "".join(all_text_blocks)
        txt_path.write_text(current_content, encoding="utf-8")
        
        latency = time.time() - start_time
        print(f"  [+] Page {page_idx} completed in {latency:.1f}s ({len(text)} chars)")
        time.sleep(1.0) # Rate limit cooling

def main():
    ap = argparse.ArgumentParser(description="OCR scanned astrology PDFs using NVIDIA NIM Vision API")
    ap.add_argument("--pdf", required=True, help="Filename of the PDF under books/")
    ap.add_argument("--start", type=int, default=1, help="Start page")
    ap.add_argument("--end", type=int, default=None, help="End page")
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
    
    ocr_pdf_via_nvidia(pdf_path, txt_path, start_page=args.start, end_page=args.end, dpi=args.dpi)

if __name__ == "__main__":
    main()
