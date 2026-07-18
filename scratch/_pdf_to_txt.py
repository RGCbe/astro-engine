import sys
from pypdf import PdfReader
from pathlib import Path

def convert_pdf_to_txt(pdf_path: str, txt_path: str):
    print(f"Opening PDF: {pdf_path} ...")
    reader = PdfReader(pdf_path)
    print(f"Found {len(reader.pages)} pages. Extracting text...")
    
    lines = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            lines.append(f"\n--- PAGE {i+1} ---\n")
            lines.append(text)
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} pages...")
            
    print(f"Writing to text file: {txt_path} ...")
    Path(txt_path).write_text("\n".join(lines), encoding="utf-8", errors="replace")
    print(f"Successfully converted {pdf_path} to {txt_path}.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python _pdf_to_txt.py <pdf_path> <txt_path>")
        sys.exit(1)
    convert_pdf_to_txt(sys.argv[1], sys.argv[2])
