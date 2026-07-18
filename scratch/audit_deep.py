import json, os

# List all deep extraction files
deep_dir = "f:/Atro/gemma_extractions"
books_dir = "f:/Atro/Books"

deep_files = [f for f in os.listdir(deep_dir) if f.endswith("_deep.json")]
deep_books = [f.replace("_deep.json", "") for f in deep_files]
deep_books.sort()

# List all source books
book_files = [f for f in os.listdir(books_dir) if f.endswith("_extracted.txt")]
all_books = [f.replace("_extracted.txt", "") for f in book_files]
all_books.sort()

print("=== Books WITH deep extraction ===")
for b in deep_books:
    fpath = os.path.join(deep_dir, b + "_deep.json")
    size = os.path.getsize(fpath)
    try:
        data = json.load(open(fpath, "r", encoding="utf-8"))
        rules = data.get("rules", [])
        n_rules = len(rules) if isinstance(rules, list) else "N/A"
    except:
        n_rules = "ERROR"
    print(f"  {b}: {size:,} bytes, {n_rules} rules")

print(f"\nTotal deep files: {len(deep_books)}")

missing = [b for b in all_books if b not in deep_books]
missing.sort()
print(f"\n=== Books WITHOUT deep extraction ({len(missing)}) ===")
for b in missing:
    src = os.path.join(books_dir, b + "_extracted.txt")
    sz = os.path.getsize(src)
    print(f"  {b}: {sz:,} bytes source")
