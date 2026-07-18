import fitz, os, sys

folder = r"f:\astro\STRUCTURE BASE"
files = sorted(os.listdir(folder))
pdfs = [f for f in files if f.endswith(".pdf")]

print(f"Total volumes: {len(pdfs)}\n")

all_text = {}
for fname in pdfs:
    path = os.path.join(folder, fname)
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    all_text[fname] = text.strip()

# Print summary of each volume
for fname, text in all_text.items():
    vol_name = fname.replace("AstroReport_OS_", "").replace(".pdf", "")
    print(f"=== {vol_name} ===")
    print(f"  Size: {len(text)} chars")
    # Print first 300 chars
    print(f"  Preview: {text[:300].strip()}")
    print()
