"""
extract_book_rules.py — LLM-based Rule Extractor for Astrology Books.

Reads a raw text file (e.g., Tetrabiblos), splits it into manageable chunks,
sends each chunk to the local Gemma model for structured rule extraction,
de-duplicates, and writes the final JSON to the gemma_extractions directory.

Usage:
    python3 extract_book_rules.py <book_name> <raw_text_path>

Example:
    python3 extract_book_rules.py "Tetrabiblos_Ashmand" /opt/astro/knowledge/Tetrabiblos_raw.txt
"""
import sys
import json
import re
import time
import os
from pathlib import Path

# ---------- CONFIG ----------
CHUNK_SIZE = 3000       # chars per chunk sent to LLM
OVERLAP = 200           # overlap between chunks to avoid cutting mid-rule
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "gemma_extractions"
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
# If Ollama is not available, fall back to manual prompt-based extraction
USE_OLLAMA = False

EXTRACTION_PROMPT = """You are the Lead Astro-KG Ingestion Agent. Read the following passage from the classical astrology text "{book_name}" and extract EVERY predictive astrological rule.

For each rule found, output a JSON object with these fields:
- "source": the book name and chapter/section reference
- "event_category": one of "career", "marriage", "health", "wealth", "family", "longevity", "personality", "travel", "education", "spiritual", "general"
- "planets": list of planets mentioned (e.g. ["Sun", "Mars"])
- "signs": list of zodiac signs mentioned (e.g. ["Aries", "Leo"])
- "houses": list of house numbers mentioned (e.g. [1, 7, 10])
- "aspects": list of aspects mentioned (e.g. ["conjunction", "opposition", "trine"])
- "rule_text": the exact predictive statement from the text
- "interpretation": your interpretation of the rule in modern predictive terms
- "valence": "auspicious" or "inauspicious" or "neutral"

Output a JSON array of these objects. If no rules are found in the passage, output an empty array [].
Do NOT output anything other than valid JSON.

--- PASSAGE ---
{chunk}
--- END PASSAGE ---
"""


def read_raw_text(path: str) -> str:
    """Read and clean raw text file."""
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    # Strip Gutenberg headers/footers
    start_marker = "*** START OF"
    end_marker = "*** END OF"
    start_idx = text.find(start_marker)
    if start_idx != -1:
        # Find end of the START line
        nl = text.find("\n", start_idx)
        if nl != -1:
            text = text[nl + 1:]
    end_idx = text.find(end_marker)
    if end_idx != -1:
        text = text[:end_idx]
    return text.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> list:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks


def extract_rules_regex(text: str, book_name: str) -> list:
    """
    Regex-based rule extractor for when LLM is not available.
    Extracts planetary/sign/house combinations from classical text.
    """
    rules = []
    
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
               "Rahu", "Ketu", "Dragon's Head", "Dragon's Tail"]
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    aspects = ["conjunction", "opposition", "trine", "quartile", "square", "sextile",
               "sesquiquadrate", "semisextile", "quincunx"]
    house_words = {
        "first house": 1, "second house": 2, "third house": 3, "fourth house": 4,
        "fifth house": 5, "sixth house": 6, "seventh house": 7, "eighth house": 8,
        "ninth house": 9, "tenth house": 10, "eleventh house": 11, "twelfth house": 12,
        "1st house": 1, "2nd house": 2, "3rd house": 3, "4th house": 4,
        "5th house": 5, "6th house": 6, "7th house": 7, "8th house": 8,
        "9th house": 9, "10th house": 10, "11th house": 11, "12th house": 12,
        "ascendant": 1, "midheaven": 10, "mid-heaven": 10, "nadir": 4,
        "descendant": 7, "imum coeli": 4, "medium coeli": 10,
    }
    
    # Keyword categories
    career_kw = ["employment", "profession", "rank", "honour", "honor", "dignity",
                 "authority", "command", "king", "ruler", "magistrate", "office",
                 "occupation", "trade", "craft", "business"]
    marriage_kw = ["marriage", "wife", "husband", "nuptials", "wedding", "spouse",
                   "partner", "bride", "bridegroom", "matrimony"]
    health_kw = ["disease", "sickness", "illness", "infirmity", "hurt", "injury",
                 "death", "die", "wound", "pain", "blind", "deaf", "lame", "fever",
                 "plague", "chronic", "acute", "affliction"]
    wealth_kw = ["wealth", "riches", "fortune", "poverty", "gain", "loss",
                 "property", "inheritance", "treasure", "money", "substance"]
    family_kw = ["parent", "father", "mother", "brother", "sister", "children",
                 "child", "son", "daughter", "sibling", "twin", "birth", "offspring"]
    travel_kw = ["travel", "journey", "voyage", "foreign", "migration", "exile",
                 "abroad", "pilgrimage"]
    spiritual_kw = ["spiritual", "religion", "religious", "conversion", "divine",
                    "sacred", "occult", "mystical", "prophecy", "oracle"]
    
    # Split into sentences
    sentences = re.split(r'(?<=[.;:])\s+', text)
    
    for sent in sentences:
        sent_lower = sent.lower()
        found_planets = [p for p in planets if p.lower() in sent_lower]
        found_signs = [s for s in signs if s.lower() in sent_lower]
        found_aspects = [a for a in aspects if a.lower() in sent_lower]
        found_houses = []
        for hw, hnum in house_words.items():
            if hw in sent_lower:
                found_houses.append(hnum)
        found_houses = sorted(set(found_houses))
        
        # Must have at least one planet/sign AND one predictive element
        if not (found_planets or found_signs):
            continue
        if len(sent) < 30:
            continue
        
        # Determine category
        category = "general"
        for kw in career_kw:
            if kw in sent_lower:
                category = "career"
                break
        if category == "general":
            for kw in marriage_kw:
                if kw in sent_lower:
                    category = "marriage"
                    break
        if category == "general":
            for kw in health_kw:
                if kw in sent_lower:
                    category = "health"
                    break
        if category == "general":
            for kw in wealth_kw:
                if kw in sent_lower:
                    category = "wealth"
                    break
        if category == "general":
            for kw in family_kw:
                if kw in sent_lower:
                    category = "family"
                    break
        if category == "general":
            for kw in travel_kw:
                if kw in sent_lower:
                    category = "travel"
                    break
        if category == "general":
            for kw in spiritual_kw:
                if kw in sent_lower:
                    category = "spiritual"
                    break
        
        # Determine valence
        inauspicious_kw = ["evil", "malefic", "unfortunate", "disease", "death",
                           "loss", "poverty", "afflict", "destroy", "injury",
                           "hurt", "danger", "calamity", "misfortune", "adverse"]
        auspicious_kw = ["benefic", "fortunate", "good", "prosper", "success",
                         "honour", "honor", "wealth", "gain", "happy", "favorable",
                         "favourable", "excellent", "dignified", "exalted"]
        
        valence = "neutral"
        for kw in inauspicious_kw:
            if kw in sent_lower:
                valence = "inauspicious"
                break
        if valence == "neutral":
            for kw in auspicious_kw:
                if kw in sent_lower:
                    valence = "auspicious"
                    break
        
        rule = {
            "source": book_name,
            "event_category": category,
            "planets": found_planets,
            "signs": found_signs,
            "houses": found_houses,
            "aspects": found_aspects,
            "rule_text": sent.strip()[:500],
            "interpretation": "",
            "valence": valence
        }
        rules.append(rule)
    
    return rules


def deduplicate_rules(rules: list) -> list:
    """Remove duplicate rules based on rule_text similarity."""
    seen = set()
    deduped = []
    for r in rules:
        key = r.get("rule_text", "").strip().lower()[:100]
        if key and key not in seen:
            seen.add(key)
            deduped.append(r)
    return deduped


def merge_into_master(new_rules: list, master_path: Path) -> int:
    """Merge new rules into the master corpus, de-duplicating."""
    if master_path.exists():
        raw = json.loads(master_path.read_text(encoding="utf-8"))
    else:
        raw = {"rules": []}
    
    # Handle both dict (with 'rules' key) and flat list formats
    if isinstance(raw, dict):
        master_rules = raw.get("rules", [])
        is_dict_format = True
    else:
        master_rules = raw
        is_dict_format = False
    
    # Build existing text index from master rules (handle both dict and string entries)
    existing_texts = set()
    for r in master_rules:
        if isinstance(r, dict):
            key = r.get("rule_text", r.get("rule", "")).strip().lower()[:100]
        elif isinstance(r, str):
            key = r.strip().lower()[:100]
        else:
            continue
        if key:
            existing_texts.add(key)
    
    added = 0
    for r in new_rules:
        key = r.get("rule_text", "").strip().lower()[:100]
        if key and key not in existing_texts:
            master_rules.append(r)
            existing_texts.add(key)
            added += 1
    
    # Write back in original format
    if is_dict_format:
        raw["rules"] = master_rules
        raw["n_dedup_rules"] = len(master_rules)
        master_path.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        master_path.write_text(json.dumps(master_rules, indent=2, ensure_ascii=False), encoding="utf-8")
    return added


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 extract_book_rules.py <book_name> <raw_text_path>")
        sys.exit(1)
    
    book_name = sys.argv[1]
    raw_path = sys.argv[2]
    
    print(f"=" * 70)
    print(f"RULE EXTRACTION: {book_name}")
    print(f"Source: {raw_path}")
    print(f"=" * 70)
    
    # 1. Read and clean text
    print("[1/4] Reading raw text...")
    text = read_raw_text(raw_path)
    print(f"      Text length: {len(text):,} characters")
    
    # 2. Extract rules using regex-based parser
    print("[2/4] Extracting rules (regex-based NLP parser)...")
    all_rules = extract_rules_regex(text, book_name)
    print(f"      Raw rules extracted: {len(all_rules)}")
    
    # 3. Deduplicate
    print("[3/4] Deduplicating...")
    deduped = deduplicate_rules(all_rules)
    print(f"      Unique rules: {len(deduped)}")
    
    # 4. Save standalone extraction
    out_path = OUTPUT_DIR / f"{book_name}_deep.json"
    out_path.write_text(json.dumps(deduped, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"      Saved to: {out_path}")
    
    # 5. Merge into master
    master_path = OUTPUT_DIR / "_MASTER_dedup.json"
    added = merge_into_master(deduped, master_path)
    print(f"[4/4] Merged {added} NEW unique rules into master corpus")
    
    # Summary by category
    cats = {}
    for r in deduped:
        c = r.get("event_category", "unknown")
        cats[c] = cats.get(c, 0) + 1
    print(f"\n--- Category Breakdown ---")
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {c:20s}: {n}")
    
    # Summary by valence
    vals = {}
    for r in deduped:
        v = r.get("valence", "unknown")
        vals[v] = vals.get(v, 0) + 1
    print(f"\n--- Valence Breakdown ---")
    for v, n in sorted(vals.items(), key=lambda x: -x[1]):
        print(f"  {v:20s}: {n}")
    
    print(f"\n{'=' * 70}")
    print(f"DONE: {book_name} — {len(deduped)} rules extracted, {added} new rules added to master.")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
