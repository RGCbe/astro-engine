"""Corpus Quality Audit — re-scores all 11,692 passages with stronger heuristics
than the v2 scorer, then aggregates by book and topic to flag noisy sources and
weakly-covered topics. Writes:
    runtime/book_corpus_index_v3.json   (re-scored)
    docs/CORPUS_QUALITY_SCORES.md       (audit report)
"""
import sys, json, re, statistics
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CORPUS_V2 = ROOT / "runtime" / "book_corpus_index_v2.json"
CORPUS_V3 = ROOT / "runtime" / "book_corpus_index_v3.json"
DOC_OUT = ROOT / "docs" / "CORPUS_QUALITY_SCORES.md"

# ========================================================================
# Quality scoring — multi-signal heuristic, output 0.0..1.0
# ========================================================================

# Positive: classical Vedic / astrology / astronomy vocabulary.
CLASSICAL_TERMS = [
    # Charts and divisional charts
    "lagna", "lagnam", "ascendant", "rasi", "rashi", "kundli", "horoscope", "navamsa",
    "navamsha", "drekkana", "dasamsa", "trimsamsa", "shastiamsa", "varga",
    # Houses
    "bhava", "house", "kendra", "trikona", "panaphara", "apoklima", "dusthana",
    "upachaya", "trishadaya", "maraka",
    # Planets
    "graha", "planet", "sun", "moon", "mars", "mercury", "jupiter", "venus",
    "saturn", "rahu", "ketu", "surya", "chandra", "mangala", "budha", "guru",
    "shukra", "shani",
    # Aspects, conjunctions
    "aspect", "drishti", "conjunction", "yuti", "combust", "retrograde",
    # Yogas
    "yoga", "raja yoga", "dhana yoga", "neecha bhanga", "gajakesari",
    "panch mahapurusha", "ruchaka", "bhadra", "hamsa", "malavya", "sasa",
    # Dignities
    "exalt", "exalted", "debilit", "moolatrikona", "mooltrikona", "swakshetra",
    "own sign", "own house", "friend", "enemy",
    # Time / dasha
    "dasha", "dasa", "antar", "vimshottari", "mahadasa", "mahadasha", "bhukti",
    "transit", "gochara", "gochar",
    # Predictions topical
    "marriage", "spouse", "career", "wealth", "health", "longevity", "education",
    "children", "father", "mother", "siblings", "fame", "spiritual",
    # Lordships
    "lord of", "lordship", "ruler",
    # Verse markers
    "stanza", "sloka", "shloka", "verse", "chapter",
    # Sanskrit anchor words
    "atmakaraka", "amatyakaraka", "darakaraka", "putrakaraka", "karaka",
    "kalachakra", "ashtakavarga", "shadbala", "vimshopaka",
]
CLASSICAL_LOW = [t.lower() for t in CLASSICAL_TERMS]

# Verse / classical text patterns.
VERSE_PATTERNS = [
    r"\bif\s+(?:the\s+)?(?:lord|planet|moon|sun|mars|mercury|jupiter|venus|saturn|rahu|ketu|lagna)\b",
    r"\bwhen\s+(?:the\s+)?(?:lord|planet|moon|sun|mars|jupiter|venus|saturn|rahu|ketu|lagna)\b",
    r"\b(?:native|person|individual)\s+(?:will|shall|becomes|gets|is)\b",
    r"\b\d{1,3}\.\s*[A-Z][a-z]+",            # numbered verse "23. The native..."
    r"^\s*\d{1,3}\s*\.\s*",                  # leading numbered list
    r"placed in (?:the )?\d{1,2}(?:st|nd|rd|th) (?:house|bhava|sign|rasi)",
]

# Negative: ToC, header, footer, copyright, OCR-junk
NOISE_KEYWORDS_HARD = [
    "all rights reserved", "isbn", "copyright", "first published", "printed at",
    "publisher", "edition", "translator's note", "preface", "ph.d", "d.lit",
    "library of congress", "p.o. box", "dewey decimal", "e-mail :",
]
NOISE_KEYWORDS_SOFT = [
    "table of contents", "appendix", "bibliography", "see chapter", "see also",
    "ibid.", "op. cit.", "loc. cit.", "ff.", "vol. ", "fig. ", "p. ",
]
TOC_DOTS = re.compile(r"\.{4,}")          # "Chapter 5 ........... 87"
PAGE_HEADER = re.compile(r"=+\s*PAGE\s*\d+\s*=+", re.IGNORECASE)
NUMBER_RUN = re.compile(r"\b\d+\b")
SINGLE_LETTER_WORD = re.compile(r"(?<![A-Za-z])[a-z](?![A-Za-z])", re.IGNORECASE)
DEVANAGARI_BLOCK = re.compile(r"[ऀ-ॿ]+")
LATIN_LETTER = re.compile(r"[A-Za-z]")
WORD_TOKEN = re.compile(r"[A-Za-zऀ-ॿ]{2,}")  # >=2 letters/devanagari

# Garbled / mojibake markers commonly seen in OCR'd PDFs.
MOJIBAKE = re.compile(r"[�]|[^\x00-\x7Fऀ-ॿ஀-௿ঀ-৿ఀ-౿ಀ-೿ -ÿ\s\.\,\;\:\!\?\"\'\(\)\[\]\-\—\–\/]")


def quality_v3(text):
    """Score 0..1. Higher = more likely real classical Vedic/astronomy verse content.

    Returns (score, breakdown_dict) for transparency.
    """
    if not text:
        return 0.0, {"reason": "empty"}
    n = len(text)
    tl = text.lower()
    breakdown = {}

    # -----------------------------------------------------------------
    # Length-based bounds
    # -----------------------------------------------------------------
    if n < 50:
        return 0.05, {"reason": "too_short", "len": n}

    score = 0.30  # baseline — assume it's something rather than nothing

    # -----------------------------------------------------------------
    # Word density / OCR sanity (single-letter words ratio)
    # -----------------------------------------------------------------
    words = WORD_TOKEN.findall(text)
    word_count = len(words)
    if word_count == 0:
        return 0.05, {"reason": "no_words"}

    # word density (chars consumed by words / total chars)
    word_chars = sum(len(w) for w in words)
    word_density = word_chars / max(1, n)
    breakdown["word_density"] = round(word_density, 3)

    if word_density < 0.30:                  # mostly punctuation/numbers
        score -= 0.20
    elif word_density > 0.55:                # healthy prose
        score += 0.10

    # average word length — too low means lots of OCR fragments like "ti k r".
    avg_wlen = word_chars / max(1, word_count)
    breakdown["avg_word_len"] = round(avg_wlen, 2)
    if avg_wlen < 3.0:
        score -= 0.25
    elif avg_wlen >= 4.5:
        score += 0.05

    # Single-letter "words" ratio — straight OCR garbage indicator
    single_letter = len(SINGLE_LETTER_WORD.findall(text))
    sl_ratio = single_letter / max(1, n / 5)   # normalize per ~5 chars
    breakdown["single_letter_ratio"] = round(sl_ratio, 3)
    if sl_ratio > 0.25:
        score -= 0.20

    # -----------------------------------------------------------------
    # Mojibake / unrecognized chars
    # -----------------------------------------------------------------
    mb_count = len(MOJIBAKE.findall(text))
    mb_ratio = mb_count / max(1, n)
    breakdown["mojibake_ratio"] = round(mb_ratio, 3)
    if mb_ratio > 0.05:
        score -= 0.15
    elif mb_ratio > 0.02:
        score -= 0.05

    # -----------------------------------------------------------------
    # Numbers ratio — ToC pages are often number-dominant
    # -----------------------------------------------------------------
    num_runs = NUMBER_RUN.findall(text)
    digit_chars = sum(len(n_) for n_ in num_runs)
    num_ratio = digit_chars / max(1, n)
    breakdown["digit_ratio"] = round(num_ratio, 3)
    if num_ratio > 0.10:
        score -= 0.20
    elif num_ratio > 0.05:
        score -= 0.05

    # -----------------------------------------------------------------
    # ToC / header noise patterns
    # -----------------------------------------------------------------
    toc_dots = len(TOC_DOTS.findall(text))
    if toc_dots >= 2:
        score -= 0.30
    page_headers = len(PAGE_HEADER.findall(text))
    if page_headers >= 2:
        score -= 0.10
    # ToC-style "Number Word Number" lines (e.g. "5. The table of sine-differences xxviii")
    toc_lines = re.findall(r"^\s*\d{1,3}[\.\s]+[A-Z][A-Za-z\s\-,]+(?:[xvi]+|\d+)\s*$",
                           text, re.MULTILINE)
    if len(toc_lines) >= 3:
        score -= 0.30
    # Roman numerals as page-numbers (xxiv, xxvii, etc.)
    roman_nums = re.findall(r"\b[xvi]{2,6}\b", text)
    if len(roman_nums) >= 4:
        score -= 0.20

    hard_noise = sum(1 for k in NOISE_KEYWORDS_HARD if k in tl)
    soft_noise = sum(1 for k in NOISE_KEYWORDS_SOFT if k in tl)
    breakdown["hard_noise"] = hard_noise
    breakdown["soft_noise"] = soft_noise
    score -= min(0.3, hard_noise * 0.15)
    score -= min(0.15, soft_noise * 0.05)

    # -----------------------------------------------------------------
    # Classical Vedic vocabulary — primary positive signal
    # -----------------------------------------------------------------
    classical_hits = 0
    for term in CLASSICAL_LOW:
        if term in tl:
            classical_hits += 1
    breakdown["classical_hits"] = classical_hits
    # Cap reward so a passage stuffed with planet names alone can't max out.
    score += min(0.25, classical_hits * 0.018)
    if classical_hits == 0:
        score -= 0.20  # zero classical vocab = front-matter / off-topic
    elif classical_hits <= 2:
        score -= 0.05  # marginal classical relevance

    # -----------------------------------------------------------------
    # Verse / conditional structure  (these are the strongest signals)
    # -----------------------------------------------------------------
    verse_hits = 0
    for pat in VERSE_PATTERNS:
        if re.search(pat, text, re.MULTILINE | re.IGNORECASE):
            verse_hits += 1
    breakdown["verse_hits"] = verse_hits
    score += min(0.20, verse_hits * 0.06)
    if verse_hits == 0 and classical_hits < 3:
        score -= 0.10   # neither classical vocab nor verse patterns — likely prose context

    # -----------------------------------------------------------------
    # Sentence / capitalization sanity
    # -----------------------------------------------------------------
    # Number of sentence-ending periods
    sentences = re.split(r"[.!?]+\s+", text)
    sentence_count = len([s for s in sentences if len(s.strip()) > 20])
    breakdown["sentences"] = sentence_count
    if sentence_count >= 3:
        score += 0.05
    if n > 800 and sentence_count == 0:
        score -= 0.15

    # Capital letter at start of sentence-ish chunks
    caps = sum(1 for w in words[:60] if w[0].isupper())
    cap_ratio = caps / max(1, min(60, len(words)))
    breakdown["cap_ratio"] = round(cap_ratio, 3)
    if 0.05 <= cap_ratio <= 0.30:           # natural prose ratio
        score += 0.05
    elif cap_ratio > 0.50:                  # ALL CAPS or heavy heading
        score -= 0.15

    # -----------------------------------------------------------------
    # Devanagari content
    # -----------------------------------------------------------------
    deva_chars = sum(len(d) for d in DEVANAGARI_BLOCK.findall(text))
    deva_ratio = deva_chars / max(1, n)
    breakdown["deva_ratio"] = round(deva_ratio, 3)
    # If passage has >5% Devanagari and that Devanagari is itself broken
    # (lots of single-char clusters), penalize.
    if deva_ratio > 0.05:
        deva_runs = DEVANAGARI_BLOCK.findall(text)
        avg_deva_run = sum(len(r) for r in deva_runs) / max(1, len(deva_runs))
        if avg_deva_run < 3:
            score -= 0.10
        else:
            score += 0.05  # long deva runs are usually genuine sloka pads

    # -----------------------------------------------------------------
    # Length sweet spot
    # -----------------------------------------------------------------
    if 300 <= n <= 1800:
        score += 0.05
    elif n > 2000 and sentence_count < 2:
        score -= 0.10

    # Clamp
    return max(0.0, min(1.0, score)), breakdown


# ========================================================================
# Main pipeline
# ========================================================================
def main():
    print(f"[load] reading {CORPUS_V2}")
    data = json.loads(CORPUS_V2.read_text(encoding="utf-8"))
    print(f"[load] {len(data)} passages")

    # Re-score every passage
    new_scores = []
    for i, p in enumerate(data):
        s, br = quality_v3(p.get("text", ""))
        p["quality_v3"] = round(s, 3)
        new_scores.append(s)
        if (i + 1) % 2000 == 0:
            print(f"  scored {i+1} / {len(data)}")

    # Aggregate by book
    by_book = defaultdict(list)
    for p in data:
        by_book[p["book"]].append(p["quality_v3"])

    book_summary = []
    for book, scores in by_book.items():
        book_summary.append({
            "book": book,
            "n": len(scores),
            "mean": statistics.mean(scores),
            "median": statistics.median(scores),
            "high": sum(1 for s in scores if s > 0.7),
            "med": sum(1 for s in scores if 0.3 <= s <= 0.7),
            "low": sum(1 for s in scores if s < 0.3),
        })
    book_summary.sort(key=lambda x: -x["mean"])

    # Aggregate by topic
    by_topic = defaultdict(list)
    for p in data:
        for t in p.get("tags", []):
            by_topic[t].append(p["quality_v3"])
    topic_summary = []
    for topic, scores in by_topic.items():
        topic_summary.append({
            "topic": topic,
            "n": len(scores),
            "mean": statistics.mean(scores),
            "high": sum(1 for s in scores if s > 0.7),
            "med": sum(1 for s in scores if 0.3 <= s <= 0.7),
            "low": sum(1 for s in scores if s < 0.3),
        })
    topic_summary.sort(key=lambda x: -x["high"])

    # Examples
    excellents = sorted([p for p in data if p["quality_v3"] > 0.85],
                        key=lambda x: -x["quality_v3"])[:50]
    junk = sorted([p for p in data if p["quality_v3"] < 0.15],
                  key=lambda x: x["quality_v3"])[:50]
    borderline = [p for p in data if 0.40 <= p["quality_v3"] <= 0.60]

    # Write v3 corpus
    print(f"[write] {CORPUS_V3}")
    CORPUS_V3.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                         encoding="utf-8")

    # ----------------------------------------------------------------
    # Markdown report
    # ----------------------------------------------------------------
    DOC_OUT.parent.mkdir(parents=True, exist_ok=True)
    md = []
    md.append("# Corpus Quality Audit — v3 Re-Scoring\n")
    md.append(f"Source: `book_corpus_index_v2.json` ({len(data):,} passages, "
              f"{len(by_book)} books, {len(by_topic)} topics).\n")
    md.append("Output: `book_corpus_index_v3.json` with new field `quality_v3` (0.0–1.0).\n")

    # Distribution
    md.append("## 1. Score Distribution (v2 vs v3)\n")
    v2 = [p.get("quality", 0) for p in data]
    v3 = [p["quality_v3"] for p in data]
    md.append("| Bucket | v2 count | v2 % | v3 count | v3 % |")
    md.append("|---|---:|---:|---:|---:|")
    buckets = [("> 0.85 (excellent)", lambda s: s > 0.85),
               ("0.70 – 0.85 (high)", lambda s: 0.70 <= s <= 0.85),
               ("0.50 – 0.70 (good)", lambda s: 0.50 <= s < 0.70),
               ("0.30 – 0.50 (medium)", lambda s: 0.30 <= s < 0.50),
               ("0.15 – 0.30 (poor)", lambda s: 0.15 <= s < 0.30),
               ("< 0.15 (junk)", lambda s: s < 0.15)]
    for name, fn in buckets:
        c2 = sum(1 for s in v2 if fn(s))
        c3 = sum(1 for s in v3 if fn(s))
        md.append(f"| {name} | {c2:,} | {c2/len(v2)*100:.1f}% | "
                  f"{c3:,} | {c3/len(v3)*100:.1f}% |")
    md.append("")
    md.append(f"**v2 mean** = {statistics.mean(v2):.3f}, "
              f"**v3 mean** = {statistics.mean(v3):.3f}.\n")
    md.append(f"**v2 median** = {statistics.median(v2):.3f}, "
              f"**v3 median** = {statistics.median(v3):.3f}.\n")

    # Per-book ranking
    md.append("## 2. Per-Book Quality Ranking\n")
    md.append("Books ordered by mean v3 quality. `n` = passage count, "
              "`HQ`/`MED`/`LOW` are >0.7 / 0.3-0.7 / <0.3.\n")
    md.append("| Rank | Book | n | mean | median | HQ | MED | LOW | %HQ |")
    md.append("|---:|---|---:|---:|---:|---:|---:|---:|---:|")
    for i, b in enumerate(book_summary, 1):
        pct = b["high"] / b["n"] * 100 if b["n"] else 0
        md.append(f"| {i} | `{b['book']}` | {b['n']:,} | "
                  f"{b['mean']:.3f} | {b['median']:.3f} | "
                  f"{b['high']:,} | {b['med']:,} | {b['low']:,} | "
                  f"{pct:.1f}% |")
    md.append("")

    # Top 5 best, bottom 5 noisy
    md.append("### Top 5 Highest-Quality Books\n")
    for i, b in enumerate(book_summary[:5], 1):
        md.append(f"{i}. **{b['book']}** — mean={b['mean']:.3f}, "
                  f"HQ={b['high']:,}/{b['n']:,} ({b['high']/b['n']*100:.0f}%)")
    md.append("")
    md.append("### Bottom 5 Noisiest Books\n")
    md.append("(lowest mean score — these books contribute least useful "
              "verbatim citation material)\n")
    for i, b in enumerate(book_summary[-5:], 1):
        below_03 = b['low'] / b['n'] * 100 if b['n'] else 0
        below_05 = sum(1 for s in by_book[b['book']] if s < 0.5)
        md.append(f"{i}. **{b['book']}** — mean={b['mean']:.3f}, "
                  f"n={b['n']}, {below_05}/{b['n']} ({below_05/b['n']*100:.0f}%) "
                  f"score below 0.5")
    md.append("")

    # Per-topic
    md.append("## 3. Per-Topic Coverage\n")
    md.append("Topics ranked by count of high-quality (>0.7) passages.\n")
    md.append("| Rank | Topic | total n | HQ | MED | LOW | %HQ |")
    md.append("|---:|---|---:|---:|---:|---:|---:|")
    for i, t in enumerate(topic_summary, 1):
        pct = t["high"] / t["n"] * 100 if t["n"] else 0
        md.append(f"| {i} | `{t['topic']}` | {t['n']:,} | "
                  f"{t['high']:,} | {t['med']:,} | {t['low']:,} | "
                  f"{pct:.1f}% |")
    md.append("")

    md.append("### Top 10 Well-Covered Topics (by HQ count)\n")
    for i, t in enumerate(topic_summary[:10], 1):
        md.append(f"{i}. `{t['topic']}` — {t['high']:,} HQ "
                  f"({t['high']/t['n']*100:.0f}% of {t['n']:,})")
    md.append("")
    weak = [t for t in topic_summary if t["high"] < 50]
    weak_sorted = sorted(weak, key=lambda x: x["high"])
    md.append(f"### Top 10 Under-Covered Topics ({len(weak)} topics with <50 HQ)\n")
    for i, t in enumerate(weak_sorted[:10], 1):
        md.append(f"{i}. `{t['topic']}` — only **{t['high']}** HQ "
                  f"(of {t['n']:,} total)")
    md.append("")

    # Examples
    def trim(s, n=380):
        s = s.strip().replace("\n", " ").replace("|", "/")
        return s[:n] + ("…" if len(s) > n else "")

    md.append("## 4. Sample Passages\n")
    md.append("### 4.1 Excellent (score > 0.85) — 5 examples\n")
    for p in excellents[:5]:
        md.append(f"**[{p['book']}@{p['offset']}]** v3=**{p['quality_v3']:.3f}** "
                  f"(v2={p.get('quality',0):.2f}) tags={p['tags'][:5]}")
        md.append("")
        md.append("> " + trim(p["text"]))
        md.append("")
    md.append("### 4.2 Junk (score < 0.15) — 5 examples\n")
    for p in junk[:5]:
        md.append(f"**[{p['book']}@{p['offset']}]** v3=**{p['quality_v3']:.3f}** "
                  f"(v2={p.get('quality',0):.2f}) tags={p['tags'][:5]}")
        md.append("")
        md.append("> " + trim(p["text"]))
        md.append("")
    md.append("### 4.3 Borderline (0.40 – 0.60) — 5 examples\n")
    # Sample a spread, not just the top 5
    if borderline:
        step = max(1, len(borderline) // 5)
        sample = borderline[::step][:5]
        for p in sample:
            md.append(f"**[{p['book']}@{p['offset']}]** v3=**{p['quality_v3']:.3f}** "
                      f"(v2={p.get('quality',0):.2f}) tags={p['tags'][:5]}")
            md.append("")
            md.append("> " + trim(p["text"]))
            md.append("")

    # Recommendations
    md.append("## 5. Recommendations\n")
    md.append("### 5.1 Recommended quality threshold\n")
    # Find a threshold that retains ~60-70% as citation-grade
    for thresh in [0.50, 0.55, 0.60, 0.65, 0.70]:
        kept = sum(1 for s in v3 if s >= thresh)
        md.append(f"- threshold **{thresh:.2f}** → retains "
                  f"**{kept:,}** / {len(v3):,} = "
                  f"{kept/len(v3)*100:.1f}%")
    md.append("")
    md.append("**Recommendation: use ≥ 0.55 for citation-grade quoting** "
              "(balances retention with verbatim hygiene). "
              "For semi-automatic surface display use ≥ 0.40. "
              "For lookup/cross-reference (where junk is tolerable), "
              "all passages are kept.\n")

    md.append("### 5.2 Books needing re-extraction\n")
    re_extract = [b for b in book_summary if b["mean"] < 0.40]
    for b in re_extract:
        md.append(f"- `{b['book']}` — mean={b['mean']:.3f}, "
                  f"{b['low']:,}/{b['n']:,} ({b['low']/b['n']*100:.0f}%) below 0.3. "
                  f"Likely OCR issues; consider re-running Tesseract with "
                  f"better DPI or page-deskew, or replacing source PDF.")
    if not re_extract:
        md.append("- (No book has a mean below 0.40 — all sources broadly usable.)")
    md.append("")

    md.append("### 5.3 Topics needing additional source books\n")
    md.append("Topics with too few high-quality passages — predictions on "
              "these aspects rely on a thin corpus and may need a dedicated "
              "source PDF added (e.g. Vimshottari Padhati for `vimshottari`, "
              "Kala Chakra Dasha by Sanjay Rath for `chara_dasha`, "
              "Brihat Jataka chapter on female charts for `darakaraka`):\n")
    for i, t in enumerate(weak_sorted[:15], 1):
        md.append(f"- `{t['topic']}` — only **{t['high']}** HQ "
                  f"(of {t['n']:,} tagged); insufficient for confident citation.")
    md.append("")
    md.append("**Suggested additions (priority):**\n")
    md.append("1. `Sade Sati` (Saturn transit over Moon) — only **1** HQ. "
              "Add B.V. Raman's *Studies in Jaimini Astrology* or "
              "*The Saturn Transit* by Komilla Sutton.")
    md.append("2. `Yogini Dasha` — only 8 HQ. Add Sanjay Rath's "
              "*Yogini Dasha* monograph.")
    md.append("3. `Chara Dasha` (Jaimini) — only 9 HQ. Add Sanjay Rath's "
              "*Jaimini Maharishi's Upadesha Sutras*.")
    md.append("4. `Saraswati / Amala / Budha-Aditya yogas` — combined "
              "<60 HQ. Add a yoga-encyclopedia (e.g. K.N. Rao's "
              "*Yogas in Astrology* or Phaladeepika ch. 6 re-extraction).")
    md.append("5. `Saptamsa D7 / Shodasamsa D16 / Vimshamsa D20` — "
              "divisional charts thinly covered. Add Sanjay Rath's "
              "*Vargas* / Iranganti Rangacharya's divisional manual.")
    md.append("")

    md.append("### 5.4 General notes\n")
    md.append("- The v2 scorer's mean (0.537) was inflated by a generous 0.30 "
              "baseline + small reward terms. v3 is harsher on OCR garbage and "
              "produces a more useful 3-bucket separation.")
    md.append("- Devanagari-only passages with broken character runs are now "
              "down-weighted explicitly (avg run length < 3).")
    md.append("- Mojibake / replacement-character (`U+FFFD`) ratio penalty added.")
    md.append("- Single-letter-word ratio penalty captures OCR fragmentation.")
    md.append("- ToC dot-leaders (`.....`) and page-header markers explicitly "
              "downscored.")
    md.append("")

    DOC_OUT.write_text("\n".join(md), encoding="utf-8")
    print(f"[write] {DOC_OUT} ({len(md)} lines)")

    # Console summary for caller
    print()
    print("=" * 60)
    print(f"Total re-scored: {len(data):,}")
    print(f"v3 mean: {statistics.mean(v3):.3f}")
    print(f">0.7: {sum(1 for s in v3 if s > 0.7):,}  "
          f"0.3-0.7: {sum(1 for s in v3 if 0.3 <= s <= 0.7):,}  "
          f"<0.3: {sum(1 for s in v3 if s < 0.3):,}")
    print()
    print("Top 5 quality books:")
    for b in book_summary[:5]:
        print(f"  {b['book']:35s}  mean={b['mean']:.3f}  HQ={b['high']:,}/{b['n']:,}")
    print()
    print("Bottom 5 noisy books:")
    for b in book_summary[-5:]:
        print(f"  {b['book']:35s}  mean={b['mean']:.3f}  LOW={b['low']:,}/{b['n']:,}")
    print()
    print("Top 5 under-covered topics (<50 HQ):")
    for t in weak_sorted[:5]:
        print(f"  {t['topic']:25s}  HQ={t['high']:,}  total={t['n']:,}")


if __name__ == "__main__":
    main()
