"""Book Citation Layer — wraps book_corpus_indexer to provide
classical-source citations for engine modules.

Each engine module calls citation_for(topic, ...) to get a real
verse-level passage from the 23-book corpus to attach to its output.
"""
import sys, json, re
sys.path.insert(0, ".")
from pathlib import Path
from book_corpus_indexer import query_index

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = ROOT / "runtime"


def _is_toc_passage(text):
    """Heuristic: is this a table-of-contents page? (lots of chapter refs, page numbers)."""
    tl = text.lower()
    # ToC indicators: many ".." dotted leaders, "ch." or "chapter" repeated
    dot_runs = text.count("..")
    chapter_refs = tl.count("chapter") + tl.count("ch.") + tl.count("adhyaya")
    page_nums = len(re.findall(r'\b\d{1,3}\b', text))  # short standalone numbers
    if dot_runs > 5: return True
    if chapter_refs > 4 and page_nums > 10: return True
    if page_nums > 25: return True  # very table-like
    return False


def _clean_passage(text, max_len=400):
    """Light cleanup of OCR text — collapse whitespace, trim."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:?!\'"\-()/&]', ' ', text)  # strip OCR garbage chars
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        cut = text[:max_len]
        last_period = cut.rfind('.')
        if last_period > max_len * 0.6:
            cut = cut[:last_period+1]
        text = cut + " [...]"
    return text


def citation_for(topic, secondary_topics=None, books=None, max_results=2, min_quality=0.5):
    """Return list of {book, text, score} for use in engine output.

    Args:
      topic: primary topic (e.g. 'navamsa_d9')
      secondary_topics: list of additional topics; passages matching multiple get higher score
      books: filter to specific books (None = all)
      max_results: how many citations to return
      min_quality: minimum quality score (0.0-1.0) - filters OCR noise
    """
    raw = query_index(topic, max_results=40, books=books, min_text_len=300)
    if not raw:
        return []

    # Filter by quality score (v2 corpus)
    raw = [r for r in raw if r.get("quality", 0.5) >= min_quality]

    if secondary_topics:
        # Boost passages matching multiple topics + quality
        for r in raw:
            r["_score"] = sum(1 for st in secondary_topics if st in r["tags"]) + r.get("quality", 0.5) * 2
        raw.sort(key=lambda r: -r["_score"])
    else:
        raw.sort(key=lambda r: -r.get("quality", 0.5))

    out = []
    seen_books = set()
    for r in raw:
        if r["book"] in seen_books and len(out) >= 1:
            continue
        if _is_toc_passage(r["text"]):
            continue
        cleaned = _clean_passage(r["text"])
        if len(cleaned) < 200:
            continue
        out.append({
            "book": r["book"],
            "text": cleaned,
            "tags": r["tags"],
        })
        seen_books.add(r["book"])
        if len(out) >= max_results:
            break

    return out


def cite_topic_inline(topic, secondary_topics=None, books=None):
    """Return single best citation as a string for inline use.
    Returns: '[Book Name]: "passage text..."' or '' if nothing found.
    """
    cits = citation_for(topic, secondary_topics, books, max_results=1)
    if not cits:
        return ""
    c = cits[0]
    book_pretty = c["book"].replace("_", " ").replace("v2", "").strip()
    return f'[{book_pretty}]: "{c["text"][:300]}..."'


# ================================================================
# ENGINE-MODULE-SPECIFIC CITATION HELPERS
# ================================================================

def cite_for_d9(): return citation_for("navamsa_d9", ["marriage"], max_results=2)
def cite_for_d10(): return citation_for("dashamsa_d10", ["career"], max_results=2)
def cite_for_d60(): return citation_for("shashtiamsa_d60", ["spirituality"], max_results=2)
def cite_for_conjunction(p1=None, p2=None): return citation_for("conjunction", max_results=2)
def cite_for_aspect(): return citation_for("aspect", max_results=2)
def cite_for_sade_sati(): return citation_for("sade_sati", ["transit"], max_results=2)
def cite_for_father(): return citation_for("father", ["pitra_dosha"], max_results=2)
def cite_for_mother(): return citation_for("mother", ["matra_dosha"], max_results=2)
def cite_for_marriage(): return citation_for("marriage", ["navamsa_d9"], max_results=2)
def cite_for_career(): return citation_for("career", ["dashamsa_d10"], max_results=2)
def cite_for_wealth(): return citation_for("wealth", ["dhana_yoga"], max_results=2)
def cite_for_children(): return citation_for("children", max_results=2)
def cite_for_health(): return citation_for("health", max_results=2)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== Sample citations ===\n")

    for topic_name, fn in [
        ("D9 Navamsa + Marriage", cite_for_d9),
        ("D10 Dashamsa + Career", cite_for_d10),
        ("D60 + Spirituality", cite_for_d60),
        ("Marriage", cite_for_marriage),
        ("Father + Pitra Dosha", cite_for_father),
        ("Sade Sati", cite_for_sade_sati),
        ("Career", cite_for_career),
        ("Wealth", cite_for_wealth),
    ]:
        print(f">>> {topic_name}")
        cits = fn()
        if not cits:
            print("    (no citations found)")
        for c in cits:
            print(f"    [{c['book']}]")
            print(f"      {c['text'][:300]}")
        print()
