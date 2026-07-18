import os
import fitz  # PyMuPDF
import datetime

# Find dated folder
now = datetime.datetime.now()
yr = now.strftime("%Y")
mo = now.strftime("%m")
dy = now.strftime("%d")

pdf_dir = f"f:/astro/reports/{yr}/{mo}/{dy}/pdf"
artifacts_dir = "C:/Users/chive/.gemini/antigravity/brain/667a9de7-343e-423f-9a9b-ba7fe1ceeda7"

os.makedirs(artifacts_dir, exist_ok=True)

reports = [
    ("Manoj_P_Sashtika_Compatibility_Report_EN.pdf", "sashtika_en"),
    ("Manoj_P_Sashtika_Compatibility_Report_TA.pdf", "sashtika_ta"),
    ("Manoj_N_Gomathi_Compatibility_Report_EN.pdf", "gomathi_en"),
    ("Manoj_N_Gomathi_Compatibility_Report_TA.pdf", "gomathi_ta")
]

for filename, prefix in reports:
    pdf_path = os.path.join(pdf_dir, filename)
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} does not exist!")
        continue
        
    doc = fitz.open(pdf_path)
    print(f"Rendering {filename} ({len(doc)} pages)...")
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))  # High quality
        out_path = os.path.join(artifacts_dir, f"{prefix}_page_{page_num + 1}.png")
        pix.save(out_path)
        print(f"Saved {out_path}")
        
print("All pages rendered successfully!")
