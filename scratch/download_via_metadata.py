import urllib.request, json, os

BOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "books")

# Known Archive.org identifiers to verify and download from
BOOK_IDS = {
    "Matheseos_Firmicus_Vol1.pdf": ("matheseoslibrivi01firmuoft", "matheseoslibrivi01firmuoft.pdf"),
    "Matheseos_Firmicus_Vol2.pdf": ("matheseoslibrivi02firmuoft", "matheseoslibrivi02firmuoft.pdf"),
    "Dhruva_Nadi_Satyacharya.pdf": ("dhruvanadiofsat00satyuoft",  "dhruvanadiofsat00satyuoft.pdf"),
    "Jataka_Desh_Marga.pdf":       ("jatakadeshamarg00unkngoog",  "jatakadeshamarg00unkngoog.pdf"),
}

def get_metadata(identifier):
    url = "https://archive.org/metadata/" + identifier
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def download_file(identifier, filename, out_path):
    url = f"https://archive.org/download/{identifier}/{filename}"
    print(f"  Downloading from: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(out_path, "wb") as f:
        data = r.read()
        f.write(data)
        return len(data)

for out_name, (identifier, filename) in BOOK_IDS.items():
    out_path = os.path.join(BOOKS_DIR, out_name)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        print(f"[SKIP] {out_name} already exists")
        continue

    print(f"\n[CHECKING] {identifier}")
    try:
        meta = get_metadata(identifier)
        files = meta.get("files", [])
        pdfs = [f["name"] for f in files if f["name"].endswith(".pdf")]
        title = meta.get("metadata", {}).get("title", "?")
        print(f"  Title: {title}")
        print(f"  Available PDFs: {pdfs[:5]}")

        # Try exact filename first, then first pdf found
        target_file = filename if filename in pdfs else (pdfs[0] if pdfs else None)
        if not target_file:
            print(f"  [WARN] No PDF found in item")
            continue

        size = download_file(identifier, target_file, out_path)
        if size > 10000:
            print(f"  [OK] {out_name} saved ({size:,} bytes)")
        else:
            print(f"  [WARN] File too small: {size} bytes")
            os.remove(out_path)
    except Exception as e:
        print(f"  [ERROR] {e}")

print("\n--- Done ---")
