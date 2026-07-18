import os
import io
import fitz
import pytesseract
from PIL import Image

# Configure Tesseract cmd path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

PDF_PATH = "books/Chandra_Kala_Nadi_Santhanam.pdf"
TXT_PATH = "books/Chandra_Kala_Nadi_Santhanam_raw_ocr.txt"

def ocr_pdf():
    print(f"Opening scanned PDF: {PDF_PATH} ...")
    doc = fitz.open(PDF_PATH)
    total_pages = len(doc)
    print(f"Total pages: {total_pages}. Starting OCR pipeline...")
    
    all_text = []
    # Start OCR from page 8 to 290 (skipping introduction/index to save time)
    start_page = 8
    end_page = min(total_pages - 5, 290)
    
    print(f"Running OCR on pages {start_page} to {end_page}...")
    for page_num in range(start_page, end_page):
        page = doc[page_num]
        
        # Render page at 150 DPI for good OCR quality
        pix = page.get_pixmap(dpi=150)
        img_data = pix.tobytes("png")
        
        # Load image into PIL
        img = Image.open(io.BytesIO(img_data))
        
        # Run Tesseract OCR in English
        text = pytesseract.image_to_string(img, lang="eng")
        
        all_text.append(f"\n--- PAGE {page_num + 1} ---\n")
        all_text.append(text)
        
        if (page_num - start_page + 1) % 10 == 0:
            print(f"OCR processed {page_num - start_page + 1} pages...")
            
    print(f"Writing clean OCR text to {TXT_PATH} ...")
    with open(TXT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))
    print("OCR Pipeline completed successfully!")

if __name__ == "__main__":
    ocr_pdf()
