"""Unified Book Corpus Indexer — scans all extracted classical texts,
builds a topic-tagged passage index for fast semantic citation.

Approach:
  1. Scan Books/*_extracted.txt under project root
  2. Split each book into ~200-word passages (ignoring OCR-noise headers)
  3. Tag each passage with topics (D9, D10, conjunction, aspect, sade-sati, etc.)
  4. Output `book_corpus_index.json` for fast querying

Each indexed passage = {book, topic_tags, text, char_offset}
"""
import sys, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = ROOT / "books"
RUNTIME_DIR = ROOT / "runtime"

# Topic taxonomy — when these keywords appear in a passage, tag it
TOPIC_KEYWORDS = {
    "navamsa_d9": ["navamsa", "navamsha", "d-9", "d9 ", "9th division", "ninth division", "vargottama"],
    "dashamsa_d10": ["dasamsa", "dashamsa", "d-10", "d10 ", "10th division", "tenth division", "dasamamsa"],
    "dwadasamsa_d12": ["dwadasamsa", "dwadasamsha", "d-12", "d12 ", "twelfth division"],
    "shashtiamsa_d60": ["shashtyamsa", "shashtiamsa", "shashtyamsha", "d-60", "d60 ", "sixtieth division"],
    "drekkana_d3": ["drekkana", "drekana", "decanate", "d-3", "d3 ", "third division"],
    "trimsamsa_d30": ["trimsamsa", "trimsamsha", "d-30", "d30 ", "thirtieth division"],

    "conjunction": ["conjunction", "yuti", "yoga", "combination of", "join", "joins", "conjunct"],
    "aspect": ["aspect", "drishti", "aspecting", "looks at", "casts", "glance"],
    "sade_sati": ["sade sati", "sadhe sati", "sadi sati", "saturn moon", "saturn over moon", "saturn through 12th"],
    "transit": ["transit", "gochara", "gocara", "moving", "moves to"],

    "marriage": ["marriage", "spouse", "wife", "husband", "wedding", "darakaraka", "7th lord", "seventh lord", "venus"],
    "career": ["career", "profession", "job", "vocation", "occupation", "10th lord", "tenth lord", "amatyakaraka"],
    "wealth": ["wealth", "money", "riches", "dhana", "income", "2nd lord", "11th lord", "lakshmi"],
    "father": ["father", "pitru", "pitra", "9th lord", "ninth lord", "ninth house", "sun"],
    "mother": ["mother", "matru", "matra", "4th lord", "4th house", "fourth house", "moon"],
    "siblings": ["sibling", "brother", "sister", "3rd house", "3rd lord", "11th house", "bhratru"],
    "children": ["children", "child", "putra", "5th house", "5th lord", "santana", "progeny"],
    "education": ["education", "learning", "study", "vidya", "knowledge", "schooling"],
    "health": ["health", "disease", "illness", "longevity", "ayurdaya", "6th house", "8th house"],
    "death": ["death", "marana", "maraka", "longevity end", "end of life"],
    "spirituality": ["spiritual", "moksha", "religious", "dharma", "guru", "renunciation"],
    "travel": ["travel", "foreign", "abroad", "journey", "12th house", "12th lord"],
    "property": ["property", "house", "land", "vehicle", "4th house", "real estate"],
    "fame": ["fame", "recognition", "honor", "reputation", "glory"],

    "raja_yoga": ["raja yoga", "rajyoga", "kingly yoga", "royal yoga", "kendra trikona"],
    "dhana_yoga": ["dhana yoga", "wealth yoga", "lakshmi yoga"],
    "neecha_bhanga": ["neecha bhanga", "debilitation cancellation", "neechabhanga"],
    "vipareeta": ["vipareeta", "viparita", "reversal yoga"],
    "panch_mahapurusha": ["panch mahapurusha", "ruchaka", "bhadra", "hamsa", "malavya", "sasa"],
    "kemadruma": ["kemadruma"],
    "gaja_kesari": ["gaja kesari", "gajakesari", "gaja-kesari"],
    "kaal_sarpa": ["kaal sarpa", "kala sarpa", "kalasarpa"],

    "vimshottari": ["vimshottari", "vimsottari", "mahadasha", "antardasha", "antar dasa"],
    "dasha": ["dasa ", "dasha", "period of", "antardasa"],

    "pitra_dosha": ["pitra dosha", "pitru dosha", "pitru shaap", "pitra shaapa"],
    "matra_dosha": ["matra dosha", "matri dosha"],

    "lagna_lord": ["lagna lord", "lagnesh", "1st lord", "ascendant lord"],
    "atmakaraka": ["atmakaraka", "atma karaka"],
    "amatyakaraka": ["amatyakaraka", "amatya karaka"],
}

PASSAGE_LEN = 1500  # chars per passage chunk
PASSAGE_OVERLAP = 200  # overlap to keep context intact


def _is_noise(text):
    """Skip headers, page numbers, copyright text, OCR garbage."""
    if len(text.strip()) < 50:
        return True
    # Skip if mostly digits/punctuation
    alpha = sum(1 for c in text if c.isalpha())
    if alpha / max(1, len(text)) < 0.45:
        return True
    return False


def _tag_passage(text):
    """Return list of topic tags whose keywords appear in this passage."""
    tlow = text.lower()
    tags = []
    for topic, kws in TOPIC_KEYWORDS.items():
        for kw in kws:
            if kw in tlow:
                tags.append(topic)
                break
    return tags


def chunk_book(filepath, book_key, passage_len=PASSAGE_LEN, overlap=PASSAGE_OVERLAP):
    """Split book into overlapping passages, return list of (offset, text) tuples."""
    text = Path(filepath).read_text(encoding="utf-8", errors="ignore")
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i+passage_len]
        if not _is_noise(chunk):
            chunks.append((i, chunk))
        i += passage_len - overlap
    return chunks


def build_index():
    """Scan all *_extracted.txt files, tag passages, write JSON index."""
    index = []
    book_files = sorted(BOOKS_DIR.glob("*_extracted.txt"))
    print(f"Indexing {len(book_files)} books from {BOOKS_DIR}...")

    for bf in book_files:
        book_key = bf.stem.replace("_extracted", "")
        chunks = chunk_book(bf, book_key)
        tagged_count = 0
        for offset, text in chunks:
            tags = _tag_passage(text)
            if tags:  # only keep tagged passages (saves space)
                index.append({
                    "book": book_key,
                    "offset": offset,
                    "tags": tags,
                    "text": text.strip()[:1200]  # cap stored length
                })
                tagged_count += 1
        print(f"  {book_key:35s}: {len(chunks):4d} chunks -> {tagged_count:4d} tagged")

    out_path = RUNTIME_DIR / "book_corpus_index.json"
    out_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nIndex written to {out_path}")
    print(f"Total passages indexed: {len(index)}")
    return index


def query_index(topic, max_results=5, books=None, min_text_len=200):
    """Query the index for passages matching a topic.

    Args:
      topic: topic_keyword (e.g. 'navamsa_d9')
      max_results: how many to return
      books: list of book_keys to filter (None = all)
      min_text_len: minimum passage length to include
    """
    idx_path = RUNTIME_DIR / "book_corpus_index.json"
    if not idx_path.exists():
        return []
    index = json.loads(idx_path.read_text(encoding="utf-8"))
    matches = []
    for entry in index:
        if topic not in entry["tags"]:
            continue
        if books and entry["book"] not in books:
            continue
        if len(entry["text"]) < min_text_len:
            continue
        matches.append(entry)
    # Prefer entries from authoritative books first
    BOOK_RANK = {
        "Brihat_Parashara_v2": 1, "BPHS1": 1, "BPHS2": 1,
        "Phaladeepika": 2, "Saravali": 2, "Brihat_Jataka": 3,
        "Hora_Sara": 3, "Jataka_Parijata": 3, "Uttara_Kalamrita": 3,
        "Sarvartha_Chintamani": 3, "Laghu_Parashari": 4,
    }
    matches.sort(key=lambda e: BOOK_RANK.get(e["book"], 99))
    return matches[:max_results]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) > 1 and sys.argv[1] == "query":
        topic = sys.argv[2] if len(sys.argv) > 2 else "navamsa_d9"
        results = query_index(topic, max_results=3)
        print(f"=== {len(results)} passages tagged '{topic}' ===\n")
        for r in results:
            print(f"--- {r['book']} (offset {r['offset']}) ---")
            print(r["text"][:600])
            print()
    else:
        build_index()
