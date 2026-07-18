"""
Verse-locator + citation index.

Given a query like "BPHS Ch.27.45" or a topic ("marriage", "Mars in 7th"),
return the EXACT verses + book + chapter + page from the deep extractions.

Indexes all `*_deep.json` files in `gemma_extractions/`. Builds:
    - by_verse_id:   {"BPHS.27.45": [rule_dict, ...]}
    - by_planet:     {"Mars": [rule_dicts]}
    - by_category:   {"yoga": [...], "marriage": [...], ...}
    - by_book:       {"Phaladeepika": [rule_dicts]}

API:
    cite(verse_id_or_phrase) → list of matching rules
    rules_about(planet=None, house=None, category=None, book=None) → list
    full_index() → dict (cached on disk)
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

DEEP_DIR = Path("/opt/astro/gemma_extractions")
if not DEEP_DIR.exists():
    DEEP_DIR = Path(__file__).resolve().parents[1] / "gemma_extractions"


@lru_cache(maxsize=1)
def _load_all_deep() -> list[dict]:
    """Load every *_deep.json file's rules into one flat list."""
    out = []
    for f in sorted(DEEP_DIR.glob("*_deep.json")):
        try:
            data = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(data, list):
            rules_list = data
            book_name = f.stem.replace("_deep", "")
        else:
            rules_list = data.get("rules", [])
            book_name = data.get("book") or f.stem.replace("_deep", "")
            
        for r in rules_list:
            if isinstance(r, dict):
                r.setdefault("_book", book_name)
                out.append(r)
    return out


@lru_cache(maxsize=1)
def _build_index() -> dict:
    rules = _load_all_deep()
    idx = {
        "by_verse_id": defaultdict(list),
        "by_planet":   defaultdict(list),
        "by_house":    defaultdict(list),
        "by_sign":     defaultdict(list),
        "by_category": defaultdict(list),
        "by_book":     defaultdict(list),
        "by_type":     defaultdict(list),
    }
    for r in rules:
        vid = r.get("verse_id", "")
        if vid:
            idx["by_verse_id"][vid].append(r)
        for p in r.get("involves_planets") or []:
            idx["by_planet"][p].append(r)
        for h in r.get("involves_houses") or []:
            idx["by_house"][int(h) if str(h).isdigit() else h].append(r)
        for s in r.get("involves_signs") or []:
            idx["by_sign"][s].append(r)
        for c in r.get("categories") or []:
            idx["by_category"][c].append(r)
        idx["by_book"][r.get("_book", "")].append(r)
        idx["by_type"][r.get("type", "")].append(r)
    return {k: dict(v) for k, v in idx.items()}


def cite(query: str, max_results: int = 20) -> list[dict]:
    """Lookup by verse_id or fuzzy text match.
    Examples:
        cite("BPHS.27.45")       — exact verse
        cite("Mars in 7th")      — fuzzy text match
        cite("Mangal Dosha")     — category + text match
    """
    idx = _build_index()
    rules = _load_all_deep()
    out: list[dict] = []

    # Exact verse_id
    if query in idx["by_verse_id"]:
        out.extend(idx["by_verse_id"][query])

    # Partial verse_id
    for vid, rule_list in idx["by_verse_id"].items():
        if query.lower() in vid.lower() and vid != query:
            out.extend(rule_list)

    # Fuzzy text match in original / translation
    pat = re.compile(re.escape(query), re.IGNORECASE)
    for r in rules:
        if any(pat.search(r.get(field, "") or "")
               for field in ("original_text", "english_translation",
                              "sanskrit_iast", "verse_id")):
            if r not in out:
                out.append(r)
    return out[:max_results]


def rules_about(planet: str | None = None, house: int | None = None,
                  sign: str | None = None, category: str | None = None,
                  book: str | None = None, max_results: int = 50) -> list[dict]:
    """Filter rules by structured criteria."""
    idx = _build_index()
    candidates: list[dict] | None = None
    for d, key in [(planet, "by_planet"), (house, "by_house"),
                    (sign, "by_sign"), (category, "by_category"),
                    (book, "by_book")]:
        if d is None:
            continue
        bucket = idx[key].get(d, [])
        candidates = bucket if candidates is None else [
            r for r in candidates if r in bucket
        ]
    return (candidates or [])[:max_results]


def stats() -> dict:
    rules = _load_all_deep()
    idx = _build_index()
    return {
        "n_rules_total":      len(rules),
        "n_books_indexed":    len(idx["by_book"]),
        "n_unique_verse_ids": len(idx["by_verse_id"]),
        "n_categories":       len(idx["by_category"]),
        "rules_by_book":      {b: len(v) for b, v in idx["by_book"].items()},
        "rules_by_type":      {t: len(v) for t, v in idx["by_type"].items()},
        "top_categories":     sorted(
            ((c, len(v)) for c, v in idx["by_category"].items()),
            key=lambda x: -x[1])[:15],
    }


def _cli():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", help="verse_id or search phrase")
    ap.add_argument("--planet", help="filter by planet")
    ap.add_argument("--house", type=int, help="filter by house")
    ap.add_argument("--book", help="filter by book")
    ap.add_argument("--category", help="filter by category")
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args()

    if args.stats:
        s = stats()
        print(json.dumps(s, indent=2, default=str))
        return

    if args.query:
        results = cite(args.query)
    else:
        results = rules_about(planet=args.planet, house=args.house,
                                book=args.book, category=args.category)

    print(f"Found {len(results)} rule(s):")
    for r in results[:10]:
        print(f"\n[{r.get('_book','?')}] {r.get('verse_id','?')}  "
               f"({r.get('type','?')}, {r.get('categories', [])})")
        print(f"  Original: {r.get('original_text','')[:300]}")
        if r.get('english_translation') and r['english_translation'] != r.get('original_text'):
            print(f"  Translation: {r['english_translation'][:300]}")


if __name__ == "__main__":
    _cli()
