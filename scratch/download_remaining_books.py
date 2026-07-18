import urllib.request, json, os

BOOKS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "books")

# Alternative Archive.org identifiers for remaining books
BOOK_IDS = {
    # Dhruva Nadi alternatives
    "Dhruva_Nadi_Satyacharya.pdf": [
        ("satyajatakamdhruvanadiramans.k.astrology_202003_357_T", None),
        ("Dhruva_Nadi", None),
        ("dhruva-nadi", None),
    ],
    # Jataka Desh Marga alternatives
    "Jataka_Desh_Marga.pdf": [
        ("in.ernet.dli.2015.35428", None),
        ("in.ernet.dli.2015.405285", None),
        ("JatakaDeshMarga", None),
    ],
    # Liber Astronomiae Bonatti
    "Liber_Astronomiae_Bonatti.pdf": [
        ("liberastronomiae00bona", None),
        ("bonatti00bona", None),
        ("guido-bonatti-liber-astronomiae", None),
    ],
    # Di Tian Sui BaZi
    "Di_Tian_Sui_BaZi.pdf": [
        ("di-tian-sui-english", None),
        ("ditiansuibazi", None),
        ("di_tian_sui", None),
    ],
}

def get_metadata(identifier):
    url = "https://archive.org/metadata/" + identifier
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def download_file(identifier, filename, out_path):
    url = f"https://archive.org/download/{identifier}/{filename}"
    print(f"    Downloading: {url[:80]}...")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r, open(out_path, "wb") as f:
        data = r.read()
        f.write(data)
        return len(data)

for out_name, id_list in BOOK_IDS.items():
    out_path = os.path.join(BOOKS_DIR, out_name)
    if os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
        print(f"[SKIP] {out_name} already exists")
        continue

    print(f"\n[TRYING] {out_name}")
    found = False
    for identifier, hint_filename in id_list:
        try:
            meta = get_metadata(identifier)
            files_list = meta.get("files", [])
            title = meta.get("metadata", {}).get("title", "?")
            pdfs = [f["name"] for f in files_list if f["name"].lower().endswith(".pdf")]
            print(f"  ID: {identifier} | Title: {title}")
            print(f"  PDFs found: {pdfs[:4]}")

            if not pdfs:
                print(f"  No PDFs in this item.")
                continue

            target = hint_filename if hint_filename and hint_filename in pdfs else pdfs[0]
            size = download_file(identifier, target, out_path)
            if size > 10000:
                print(f"  [OK] Saved {out_name} ({size:,} bytes)")
                found = True
                break
            else:
                print(f"  [WARN] File too small: {size} bytes")
                if os.path.exists(out_path):
                    os.remove(out_path)
        except Exception as e:
            print(f"  [ERROR] {identifier}: {e}")

    if not found:
        print(f"  [FAILED] All alternatives exhausted for {out_name}")

print("\n--- Done ---")
