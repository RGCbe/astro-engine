import fitz, os, sys

folder = r"f:\astro\STRUCTURE BASE"
out_folder = r"f:\astro\STRUCTURE BASE\extracted"
os.makedirs(out_folder, exist_ok=True)

files = sorted(os.listdir(folder))
pdfs = [f for f in files if f.endswith(".pdf")]

print(f"Extracting {len(pdfs)} volumes...\n")

master_text = []
for fname in pdfs:
    path = os.path.join(folder, fname)
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    text = text.strip()

    # Save individual extracted text
    out_name = fname.replace(".pdf", ".txt")
    with open(os.path.join(out_folder, out_name), "w", encoding="utf-8") as f:
        f.write(text)

    vol_name = fname.replace("AstroReport_OS_", "").replace(".pdf", "")
    master_text.append(f"{'='*80}\n{vol_name}\n{'='*80}\n{text}\n")
    print(f"[OK] {vol_name} ({len(text)} chars)")

# Save combined master document
combined_path = r"f:\astro\STRUCTURE BASE\MASTER_STRUCTURE_BASE.txt"
with open(combined_path, "w", encoding="utf-8") as f:
    f.write("\n\n".join(master_text))
print(f"\n[DONE] Combined document saved: {combined_path}")
print(f"Total characters: {sum(len(t) for t in master_text):,}")
