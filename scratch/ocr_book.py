import os
import io
import sys
import argparse
from pathlib import Path
import fitz
from PIL import Image
import pytesseract

# Configure Tesseract path for Windows
WIN_TESS_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.name == "nt" and os.path.exists(WIN_TESS_PATH):
    pytesseract.pytesseract.tesseract_cmd = WIN_TESS_PATH

def ocr_pdf(pdf_path: Path, txt_path: Path, lang: str = "eng", dpi: int = 150):
    print(f"[+] Opening PDF: {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"[+] Total pages: {total_pages}. Language config: {lang}. DPI: {dpi}")
    
    # Read existing text if checkpointing
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
        if page_idx in existing_pages:
            all_text_blocks.append(f"\n====== PAGE {page_idx} ======\n")
            all_text_blocks.append(existing_pages[page_idx])
            continue
            
        print(f"[*] OCR Processing page {page_idx}/{total_pages} ...")
        page = doc[page_num]
        
        # Render page to image at specified DPI
        pix = page.get_pixmap(dpi=dpi)
        img_data = pix.tobytes("png")
        
        # Load image into PIL and run OCR
        img = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(img, lang=lang)
        
        all_text_blocks.append(f"\n====== PAGE {page_idx} ======\n")
        all_text_blocks.append(text)
        
        # Write checkpoint every page to prevent data loss on crash/timeout
        # We rewrite the file with current progress
        current_content = "".join(all_text_blocks)
        txt_path.write_text(current_content, encoding="utf-8")
        
    print(f"[OK] Completed OCR. Output saved to {txt_path}")

def main():
    ap = argparse.ArgumentParser(description="OCR scanned astrology PDFs using Tesseract")
    ap.add_argument("--pdf", required=True, help="Filename of the PDF under books/")
    ap.add_argument("--lang", default="eng", help="Tesseract language code (e.g. eng, eng+hin+san)")
    ap.add_argument("--dpi", type=int, default=150, help="Rendering DPI (default 150)")
    args = ap.parse_args()
    
    # Locate files in books/
    root = Path(__file__).resolve().parents[1]
    books_dir = root / "books"
    if not books_dir.exists():
        books_dir = root / "Books" # Case fallback
        
    pdf_path = books_dir / args.pdf
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)
        
    base_name = pdf_path.stem
    txt_path = books_dir / f"{base_name}_extracted.txt"
    
    ocr_pdf(pdf_path, txt_path, lang=args.lang, dpi=args.dpi)

if __name__ == "__main__":
    main()
