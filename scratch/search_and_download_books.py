import urllib.request, json, os

BOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "books")

# Search Archive.org for specific items using metadata API
def search_archive(query, rows=5):
    url = "https://archive.org/advancedsearch.php"
    params = f"?q={urllib.request.quote(query)}&fl[]=identifier&fl[]=title&rows={rows}&output=json&mediatype=texts"
    req = urllib.request.Request(url + params, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read())
        return data.get("response", {}).get("docs", [])

def get_pdfs(identifier):
    url = "https://archive.org/metadata/" + identifier
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
    files = data.get("files", [])
    meta = data.get("metadata", {})
    pdfs = [f["name"] for f in files if f["name"].lower().endswith(".pdf")]
    return pdfs, meta.get("title", "?")

def download(identifier, filename, out_path):
    fname_enc = urllib.request.quote(filename)
    url = f"https://archive.org/download/{identifier}/{fname_enc}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(out_path, "wb") as f:
        data = r.read()
        f.write(data)
        return len(data)

# Books to find
searches = [
    ("Jataka_Desh_Marga.pdf",    ["jataka desh marga astrology hindi", "jataka desha marga vedic", "jatakadesh marga"]),
    ("Liber_Astronomiae_Bonatti.pdf", ["bonatti liber astronomiae 146 considerations", "guido bonatti astronomy medieval", "bonatti astrology 13th century"]),
    ("Di_Tian_Sui_BaZi_English.pdf",  ["di tian sui english bazi", "dripping heaven marrow chinese astrology", "bazi classics english translation"]),
]

for out_name, queries in searches:
    out_path = os.path.join(BOOKS_DIR, out_name)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        print(f"[SKIP] {out_name}")
        continue

    print(f"\n[SEARCHING] {out_name}")
    found = False
    for q in queries:
        try:
            results = search_archive(q)
            for doc in results:
                ident = doc["identifier"]
                title = doc.get("title", "?")
                print(f"  Found: {ident} | {title}")
                try:
                    pdfs, full_title = get_pdfs(ident)
                    if pdfs:
                        print(f"    PDFs: {pdfs[:3]}")
                        size = download(ident, pdfs[0], out_path)
                        if size > 10000:
                            print(f"    [OK] Saved {out_name} ({size:,} bytes)")
                            found = True
                            break
                        else:
                            if os.path.exists(out_path): os.remove(out_path)
                except Exception as e:
                    print(f"    Download error: {e}")
            if found:
                break
        except Exception as e:
            print(f"  Search error for '{q}': {e}")

    if not found:
        print(f"  [FAILED] Could not find {out_name}")

print("\n--- Done ---")
