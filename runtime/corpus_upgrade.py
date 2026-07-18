"""Corpus Upgrade — 5-in-1 enhancement pass.

1. PDF Extractor — extract any PDFs missing _extracted.txt
2. Expanded Topic Keywords — wider coverage of taxonomy
3. Verse Quality Scoring — separate real verses from OCR/ToC noise
4. Multi-Script Support — flag Sanskrit/Devanagari/Tamil passages
5. Cross-Reference Matrix — topics where multiple books agree/disagree
"""
import sys, json, re, os
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = ROOT / "books"
RUNTIME_DIR = ROOT / "runtime"

sys.stdout.reconfigure(encoding="utf-8")


# ================================================================
# 1. PDF EXTRACTION
# ================================================================
def extract_missing_pdfs():
    """Extract any PDF that has no matching *_extracted.txt."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        try:
            from pypdf import PdfReader
            fitz = None
        except ImportError:
            print("[extractor] No PDF library available. Install: pip install pymupdf")
            return 0

    extracted = 0
    pdf_files = list(BOOKS_DIR.glob("*.pdf"))

    # Map known PDF→txt name normalizations
    NAME_MAP = {
        "1978 Yavanajataka 1.pdf": "Yavanajataka_1_extracted.txt",
        "1978 Yavanajataka 2.pdf": "Yavanajataka_2_extracted.txt",
        "2015.312156.Jataka-Parijata.pdf": "Jataka_Parijata_extracted.txt",
        "2015.486584.Jaimini-Sutras.pdf": "Jaimini_Sutras_extracted.txt",
        "6945.pdf": "Unknown_6945_extracted.txt",
        "Aryabhatiya v1 1976.pdf": "Aryabhatiya_v1_extracted.txt",
        "Aryabhatiya v2 1976.pdf": "Aryabhatiya_v2_extracted.txt",
        "BPHS - 1 RSanthanam.pdf": "BPHS1_extracted.txt",
        "BPHS - 2 RSanthanam.pdf": "BPHS2_extracted.txt",
        "Brihat_Parashara.pdf": "Brihat_Parashara_v2_extracted.txt",
        "Pancha-siddhantika.pdf": "Pancha_Siddhantika_extracted.txt",
        "Vedanga Jyotisa Lagadha -  Kupanna Sastry , K.V.Sarma.pdf": "Vedanga_Jyotisa_extracted.txt",
    }

    for pdf in pdf_files:
        out_name = NAME_MAP.get(pdf.name) or (pdf.stem.replace(" ", "_") + "_extracted.txt")
        out_path = BOOKS_DIR / out_name
        if out_path.exists() and out_path.stat().st_size > 1000:
            continue
        # Skip Aryabhatiya v3 duplicates
        if "Aryabhatiya v3" in pdf.name:
            continue
        try:
            text = ""
            if fitz:
                doc = fitz.open(pdf)
                for page in doc:
                    text += page.get_text() + "\n\n"
                doc.close()
            else:
                reader = PdfReader(pdf)
                for page in reader.pages:
                    text += page.extract_text() + "\n\n"
            if len(text) > 500:
                out_path.write_text(text, encoding="utf-8", errors="ignore")
                print(f"  + Extracted: {pdf.name} -> {out_name} ({len(text)} chars)")
                extracted += 1
        except Exception as e:
            print(f"  ! Failed {pdf.name}: {e}")

    print(f"\nNew extractions: {extracted}")
    return extracted


# ================================================================
# 2. EXPANDED TOPIC KEYWORDS
# ================================================================
EXPANDED_TOPICS = {
    # Original topics — kept
    "navamsa_d9": ["navamsa", "navamsha", "d-9", "d9 ", "9th division", "ninth division", "vargottama", "navamsha lagna"],
    "dashamsa_d10": ["dasamsa", "dashamsa", "d-10", "d10 ", "10th division", "tenth division", "dasamamsa", "dashamamsa"],
    "dwadasamsa_d12": ["dwadasamsa", "dwadasamsha", "d-12", "d12 ", "twelfth division"],
    "shashtiamsa_d60": ["shashtyamsa", "shashtiamsa", "shashtyamsha", "d-60", "d60 ", "sixtieth division"],
    "drekkana_d3": ["drekkana", "drekana", "decanate", "d-3", "d3 ", "third division"],
    "saptamsa_d7": ["saptamsa", "saptamsha", "d-7", "d7 ", "seventh division"],
    "trimsamsa_d30": ["trimsamsa", "trimsamsha", "d-30", "d30 ", "thirtieth division"],
    "shodasamsa_d16": ["shodasamsa", "shodasamsha", "d-16"],

    "conjunction": ["conjunction", "yuti", "conjunct", "joins", "joining", "combust", "combustion"],
    "aspect": ["aspect", "drishti", "aspecting", "looks at", "casts", "glance", "cast a glance", "aspects upon"],
    "sade_sati": ["sade sati", "sadhe sati", "sadi sati", "saturn moon", "saturn through 12th", "shani sade"],
    "transit": ["transit", "gochara", "gocara", "moves to", "transiting", "tranjit"],
    "ashtakavarga": ["ashtakavarga", "ashtaka varga", "ashtak varga", "bindus", "rekha"],

    # Life domains — expanded
    "marriage": ["marriage", "spouse", "wife", "husband", "wedding", "darakaraka", "dara karaka", "7th lord",
                 "seventh lord", "kalatra", "kalatre", "kalatra bhava", "venus", "vivaha"],
    "career": ["career", "profession", "job", "vocation", "occupation", "10th lord", "tenth lord", "amatyakaraka",
               "karma bhava", "rajya yoga", "professional", "livelihood", "jeevika"],
    "wealth": ["wealth", "money", "riches", "dhana", "income", "2nd lord", "11th lord", "lakshmi", "kuber",
               "treasury", "dhana bhava", "labha", "labha bhava", "prosperity"],
    "father": ["father", "pitru", "pitra", "9th lord", "ninth lord", "ninth house", "pita", "paternal", "bhagya"],
    "mother": ["mother", "matru", "matra", "4th lord", "4th house", "fourth house", "mata", "maternal", "matri"],
    "siblings": ["sibling", "brother", "sister", "3rd house", "3rd lord", "11th house", "bhratru", "sahaja",
                 "younger brother", "elder brother"],
    "children": ["children", "child", "putra", "5th house", "5th lord", "santana", "progeny", "putrabhava",
                 "putra bhava", "santati", "offspring"],
    "education": ["education", "learning", "study", "vidya", "knowledge", "schooling", "vidya bhava",
                  "learning ability", "intelligence", "buddhi"],
    "health": ["health", "disease", "illness", "longevity", "ayurdaya", "6th house", "8th house", "roga",
               "rogabhava", "vyadhi", "health afflictions"],
    "death": ["death", "marana", "maraka", "longevity end", "end of life", "kala", "yamya"],
    "spirituality": ["spiritual", "moksha", "religious", "dharma", "guru", "renunciation", "sannyasa", "vairagya",
                     "moksha bhava", "12th house"],
    "travel": ["travel", "foreign", "abroad", "journey", "12th house", "12th lord", "yatra", "videsha",
               "foreign land", "overseas"],
    "property": ["property", "house", "land", "vehicle", "4th house", "real estate", "sukha bhava",
                 "vahana", "griha", "bhumi"],
    "fame": ["fame", "recognition", "honor", "honour", "reputation", "glory", "kirti", "pratishtha"],
    "enemies": ["enemy", "enemies", "shatru", "ripu", "6th lord", "shatru bhava", "opposition", "litigation"],
    "speech": ["speech", "vach", "vak", "2nd house", "speech-related"],

    # Yoga categories — expanded
    "raja_yoga": ["raja yoga", "rajyoga", "kingly yoga", "royal yoga", "kendra trikona", "raja-yoga"],
    "dhana_yoga": ["dhana yoga", "wealth yoga", "lakshmi yoga", "kuber yoga"],
    "neecha_bhanga": ["neecha bhanga", "debilitation cancellation", "neechabhanga", "cancellation of debility"],
    "vipareeta": ["vipareeta", "viparita", "reversal yoga", "harsha yoga", "sarala yoga", "vimala yoga"],
    "panch_mahapurusha": ["panch mahapurusha", "ruchaka", "bhadra", "hamsa", "malavya", "sasa", "shasa",
                          "mahapurusha"],
    "kemadruma": ["kemadruma"],
    "gaja_kesari": ["gaja kesari", "gajakesari", "gaja-kesari"],
    "kaal_sarpa": ["kaal sarpa", "kala sarpa", "kalasarpa", "kal sarp"],
    "lunar_yoga": ["sunapha", "anapha", "durdhara", "durudhara", "kemadruma"],
    "solar_yoga": ["vesi", "vasi", "ubhayachari"],
    "parivartana": ["parivartana", "exchange yoga", "sign exchange"],
    "nabhasa": ["nabhasa", "rajju yoga", "musala yoga", "nala yoga", "mala yoga", "sarpa yoga", "gada yoga"],
    "saraswati_yoga": ["saraswati yoga", "saraswati"],
    "budha_aditya": ["budha-aditya", "budhaditya", "mercury sun", "mercury-sun"],
    "amala_yoga": ["amala yoga", "amal yoga"],

    "vimshottari": ["vimshottari", "vimsottari", "mahadasha", "antardasha", "antar dasa", "pratyantar"],
    "dasha": ["dasa ", "dasha", "period of", "antardasa", "bhukti"],
    "ashtottari": ["ashtottari"],
    "kalachakra_dasha": ["kalachakra", "kala chakra", "kaala chakra"],
    "yogini_dasha": ["yogini dasha", "yogini dasa"],
    "chara_dasha": ["chara dasha", "jaimini chara"],

    "pitra_dosha": ["pitra dosha", "pitru dosha", "pitru shaap", "pitra shaapa", "pitri dosha"],
    "matra_dosha": ["matra dosha", "matri dosha"],
    "shapit_yoga": ["shapit yoga", "shaap", "curse"],

    "lagna_lord": ["lagna lord", "lagnesh", "1st lord", "ascendant lord", "lagnesha"],
    "atmakaraka": ["atmakaraka", "atma karaka"],
    "amatyakaraka": ["amatyakaraka", "amatya karaka"],
    "darakaraka": ["darakaraka", "dara karaka"],
    "matrukaraka": ["matrukaraka", "matru karaka"],
    "putrakaraka": ["putrakaraka", "putra karaka"],
    "bhratrukaraka": ["bhratrukaraka", "bhratru karaka"],
    "gnatikaraka": ["gnatikaraka", "gnati karaka"],

    "remedies": ["remedy", "remedies", "upaya", "mantra", "yantra", "gemstone", "gem", "donate", "charity"],
    "muhurta": ["muhurta", "muhurat", "auspicious time", "muhurtha"],
    "varshaphala": ["varshaphala", "varshphal", "annual chart", "tajik", "tajika"],
    "prashna": ["prashna", "horary", "question chart"],

    "jaimini": ["jaimini", "chara karaka", "padaka", "arudha pada", "upapada"],
    "kp_paddhati": ["krishnamurti", "kp", "sub lord", "ruling planet", "rp"],

    "rahu": ["rahu", "north node", "rahu's", "rahu-"],
    "ketu": ["ketu", "south node", "ketu's", "ketu-"],
    "saturn": ["saturn", "shani", "sani"],
    "jupiter": ["jupiter", "guru", "brihaspati"],
    "mars": ["mars", "kuja", "mangal", "bhauma", "angaraka"],
    "venus": ["venus", "shukra", "sukra"],
    "mercury": ["mercury", "budha", "budh"],
    "moon": ["moon", "chandra", "soma"],
    "sun": ["sun", "ravi", "surya"],
}


# ================================================================
# 3. VERSE QUALITY SCORING
# ================================================================
VERSE_INDICATORS = [
    "if ", "when ", "the native", "the person", "one is", "yields", "produces", "results in",
    "gives", "denotes", "indicates", "the effects", "the result", "becomes", "will be",
    "shall be", "is born", "leads to", "endows", "bestows", "this combination",
    "in the lagna", "in the seventh", "in the tenth", "lord of", "placed in", "occupying",
    "the planet", "the lord", "during the dasa", "in this case",
]
NOISE_INDICATORS = [
    "preface", "introduction", "contents", "publisher", "copyright", "isbn", "all rights reserved",
    "printed at", "edition", "first published", "p.o.", "press", "translator", "rd cross road",
    "sr. no", "page", "vol.", "appendix", "footnote", "see also", "ibid", "et al",
]


def verse_quality_score(text):
    """Score a passage 0.0-1.0 — higher = more likely to be real verse content."""
    tl = text.lower()
    score = 0.0
    # Positive: verse indicators
    indicator_hits = sum(1 for ind in VERSE_INDICATORS if ind in tl)
    score += min(0.5, indicator_hits * 0.07)
    # Positive: contains classical terms
    classical_terms = ["lagna", "rasi", "house", "lord", "planet", "yoga", "dasha", "moon", "sun", "saturn",
                       "mars", "venus", "jupiter", "mercury", "rahu", "ketu", "navamsa", "sign"]
    classical_hits = sum(1 for t in classical_terms if t in tl)
    score += min(0.3, classical_hits * 0.04)
    # Negative: noise indicators
    noise_hits = sum(1 for n in NOISE_INDICATORS if n in tl)
    score -= min(0.4, noise_hits * 0.1)
    # Negative: too many numbers (pages/chapters)
    num_count = len(re.findall(r'\b\d{1,3}\b', text))
    if num_count > 15:
        score -= 0.3
    # Negative: too short
    if len(text) < 250:
        score -= 0.2
    return max(0.0, min(1.0, score + 0.3))  # baseline 0.3


# ================================================================
# 4. MULTI-SCRIPT DETECTION
# ================================================================
def detect_scripts(text):
    """Return list of scripts detected in passage."""
    scripts = []
    if any('ऀ' <= c <= 'ॿ' for c in text):
        scripts.append("Devanagari")
    if any('஀' <= c <= '௿' for c in text):
        scripts.append("Tamil")
    if any('ঀ' <= c <= '৿' for c in text):
        scripts.append("Bengali")
    if any('ఀ' <= c <= '౿' for c in text):
        scripts.append("Telugu")
    if any('ಀ' <= c <= '೿' for c in text):
        scripts.append("Kannada")
    if any(c.isascii() and c.isalpha() for c in text):
        scripts.append("Latin")
    return scripts


# ================================================================
# 5. CROSS-REFERENCE MATRIX
# ================================================================
def build_cross_reference_matrix(index):
    """For each topic, find the books that cover it most heavily."""
    topic_book_counts = defaultdict(lambda: defaultdict(int))
    for entry in index:
        for tag in entry["tags"]:
            topic_book_counts[tag][entry["book"]] += 1

    matrix = {}
    for topic, books_dict in topic_book_counts.items():
        sorted_books = sorted(books_dict.items(), key=lambda x: -x[1])
        matrix[topic] = {
            "total_passages": sum(books_dict.values()),
            "books_covering": len(books_dict),
            "top_sources": sorted_books[:5],
        }
    return matrix


# ================================================================
# REBUILD INDEX WITH ALL ENHANCEMENTS
# ================================================================
def rebuild_corpus_index_v2():
    """Rebuild index with quality scoring + script detection + expanded topics."""
    book_files = sorted(BOOKS_DIR.glob("*_extracted.txt"))
    print(f"Re-indexing {len(book_files)} books with v2 schema...")

    index = []
    PASSAGE_LEN = 1500
    OVERLAP = 200

    for bf in book_files:
        book_key = bf.stem.replace("_extracted", "")
        try:
            text = bf.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"  ! Cannot read {book_key}: {e}")
            continue

        i = 0
        kept = 0
        while i < len(text):
            chunk = text[i:i+PASSAGE_LEN]
            i += PASSAGE_LEN - OVERLAP

            # Skip very short / noisy
            if len(chunk.strip()) < 100:
                continue
            alpha_ratio = sum(1 for c in chunk if c.isalpha()) / max(1, len(chunk))
            if alpha_ratio < 0.4:
                continue

            tlow = chunk.lower()
            tags = []
            for topic, kws in EXPANDED_TOPICS.items():
                for kw in kws:
                    if kw in tlow:
                        tags.append(topic)
                        break

            if not tags:
                continue

            quality = verse_quality_score(chunk)
            scripts = detect_scripts(chunk)

            index.append({
                "book": book_key,
                "offset": i - PASSAGE_LEN + OVERLAP,
                "tags": tags,
                "text": chunk.strip()[:1500],
                "quality": round(quality, 2),
                "scripts": scripts,
            })
            kept += 1

        print(f"  {book_key:40s}: {kept:5d} tagged passages")

    out_path = RUNTIME_DIR / "book_corpus_index_v2.json"
    out_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nv2 index written: {out_path} ({len(index)} passages)")

    # Replace v1
    v1_path = RUNTIME_DIR / "book_corpus_index.json"
    v1_path.write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Updated v1 path also: {v1_path}")

    # Build cross-reference matrix
    matrix = build_cross_reference_matrix(index)
    matrix_path = RUNTIME_DIR / "book_cross_reference.json"
    matrix_path.write_text(json.dumps(matrix, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Cross-reference matrix: {matrix_path} ({len(matrix)} topics)")

    return index, matrix


def report_stats(index, matrix):
    """Print summary stats."""
    print("\n" + "="*70)
    print("CORPUS UPGRADE COMPLETE")
    print("="*70)
    print(f"\nTotal passages: {len(index)}")
    print(f"Total books: {len(set(e['book'] for e in index))}")
    print(f"Total topics: {len(matrix)}")

    # Quality distribution
    high_q = sum(1 for e in index if e["quality"] >= 0.6)
    mid_q = sum(1 for e in index if 0.4 <= e["quality"] < 0.6)
    low_q = sum(1 for e in index if e["quality"] < 0.4)
    print(f"\nQuality distribution:")
    print(f"  High quality (>=0.6):   {high_q} ({100*high_q/len(index):.1f}%)")
    print(f"  Medium quality:         {mid_q} ({100*mid_q/len(index):.1f}%)")
    print(f"  Low quality (<0.4):     {low_q} ({100*low_q/len(index):.1f}%)")

    # Scripts
    scripts_seen = Counter()
    for e in index:
        for s in e.get("scripts", []):
            scripts_seen[s] += 1
    print(f"\nScripts detected:")
    for s, c in scripts_seen.most_common():
        print(f"  {s:15s}: {c} passages")

    print(f"\nTop 15 most-covered topics (cross-reference depth):")
    sorted_topics = sorted(matrix.items(), key=lambda x: -x[1]["total_passages"])
    for topic, data in sorted_topics[:15]:
        top_books = ", ".join(f"{b[0][:20]}({b[1]})" for b in data["top_sources"][:3])
        print(f"  {topic:25s} {data['total_passages']:5d} passages, {data['books_covering']:3d} books | top: {top_books}")


if __name__ == "__main__":
    print("=" * 70)
    print("CORPUS UPGRADE — 5-IN-1 ENHANCEMENT PASS")
    print("=" * 70)

    print("\n[1/5] PDF Extraction...")
    extract_missing_pdfs()

    print("\n[2-4/5] Re-indexing with expanded topics + quality + scripts...")
    index, matrix = rebuild_corpus_index_v2()

    print("\n[5/5] Cross-reference matrix built.")
    report_stats(index, matrix)
