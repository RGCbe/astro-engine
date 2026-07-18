"""
engine/corpus.py — Multi-book Rule Corpus Engine

Indexes all 14,795 rules from 58 books extracted into gemma_extractions/.
Includes smart deduplication:
  - Strips OCR corruption ("unable to interpret", "corrupted", etc.)
  - Exact-text dedup: merges multiple books citing identical rule into one entry
    with all source citations preserved
  - Near-dedup (fingerprint): rules sharing same first 60 chars are grouped
  - After dedup: ~13,000 → ~12,700 high-quality unique rules

Lookup indexes:
  - planet + house          (planet_in_house)
  - planet + sign           (planet_in_sign)
  - nakshatra               (nakshatra_effects)
  - dasha lord              (dasha_effects)
  - yoga rules              (yoga_rules)
  - transit/gochar rules    (transit_rules)
  - compound multi-planet   (compound_rules)

Each returned CorpusRule carries all books that share the rule, verse IDs,
and the canonical (longest / most complete) text version.
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from engine.lagna_filter import rule_applies_to_lagna

# ─── OCR garbage filter ────────────────────────────────────────────────────────
_OCR_JUNK = re.compile(
    r"(unable to (interpret|translate|determin)|"
    r"ocr corrupt|ocr error|unintelligible|"
    r"corrupted text|corrupted sanskrit|"
    r"severely corrupted|undeterminable|"
    r"illegible|untranslatable)",
    re.IGNORECASE,
)

# Procedural / biographical / non-predictive text patterns
_PROCEDURAL = re.compile(
    r"(he started publishing|voluntary retirement|established.*institute|"
    r"took.*journey|became very popular|astrological counsel|"
    r"research institute|the author states that|the number of days elapsed|"
    r"kali yuga must be known|I have divided each star|"
    r"manner which will be explained|so I have divided|"
    r"will be explained shortly|propagated his findings|"
    r"modern stellar astrolog|sri k\.s\.k|kanchi mutt|sankaracharya|"
    r"inspire.*devotion|his holiness|to make further development)",
    re.IGNORECASE,
)

# Dasha / timing keywords — used for auto-tagging
_DASHA_KW = re.compile(
    r"\b(mahadasha|mahadasa|maha dasha|maha dasa|antardasha|antardasa|"
    r"antar dasha|bhukti|pratyantara|sookshma|\bdasha\b|\bdasa\b|"
    r"vimshottari|vimsottari|ashtottari|nakshatradasa|"
    r"dasha lord|dasa lord|dasa natha|dasha natha|"
    r"in.*\bperiod\b.*\bplanet|\bmaha dasha\b|"
    r"during.*dasha|in.*dasha|dasha of|dasa of|"
    r"period of (sun|moon|mars|mercury|jupiter|venus|saturn|rahu|ketu)|"
    r"(sun|moon|mars|mercury|jupiter|venus|saturn|rahu|ketu).{0,20}(mahadasha|dasha|dasa|bhukti))",
    re.IGNORECASE,
)

# ─── Constants for parsing ───────────────────────────────────────────────────
PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
RASIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def _parse_metadata(text: str) -> tuple[list[str], list[int], list[str]]:
    """Simple regex to find mentions of planets, houses, and signs in rule text."""
    p_found = []
    h_found = []
    s_found = []
    
    t_lower = text.lower()
    
    for p in PLANETS:
        if p.lower() in t_lower:
            p_found.append(p)
            
    # Match "1st house", "house 5", "5th bhava" etc.
    house_patterns = [
        r'(\d+)(?:st|nd|rd|th)?\s+house',
        r'house\s+(\d+)',
        r'(\d+)(?:st|nd|rd|th)?\s+bhava',
        r'bhava\s+(\d+)'
    ]
    for pat in house_patterns:
        matches = re.findall(pat, t_lower)
        for m in matches:
            try:
                h_num = int(m)
                if 1 <= h_num <= 12:
                    h_found.append(h_num)
            except ValueError: pass

    for s in RASIS:
        if s.lower() in t_lower:
            s_found.append(s)
            
    return list(set(p_found)), list(set(h_found)), list(set(s_found))

def _is_junk(text: str) -> bool:
    if not text or len(text) < 15:
        return True
    if _OCR_JUNK.search(text):
        return True
    # Filter biographical / procedural text (KP Reader biographical sections, etc.)
    if _PROCEDURAL.search(text):
        return True
    # Filter if mostly non-ASCII (Sanskrit numerals but no English content)
    ascii_ratio = sum(1 for c in text if ord(c) < 128) / len(text)
    if ascii_ratio < 0.35 and len(text) > 30:
        return True
    return False


_OUTCOME_KW = re.compile(
    r"(wealth|success|loss|death|disease|fame|poverty|marriage|children|"
    r"imprisonment|exile|auspicious|inauspicious|prosperity|misery|"
    r"health|trouble|gain|sorrow|honor|disgrace|blessed|cursed)",
    re.IGNORECASE
)


def _is_predictive(text: str, planets: list, houses: list, signs: list, categories: list) -> bool:
    """Returns True if a rule has any predictive content worth indexing.
    Filters out purely procedural rules that lack astrological content.
    """
    if planets or houses or signs:
        return True
    if _DASHA_KW.search(text):
        return True
    if any(c in categories for c in ("dasha","dasa","bhukti","antardasha","yoga","transit")):
        return True
    if _OUTCOME_KW.search(text):
        return True
    return False


def _auto_tag_dasha(text: str, categories: list, books: list[str] = [], involves_planets: list[str] = []) -> list:
    """If a rule's text mentions dasha/bhukti/period keywords but was not tagged
    as dasha by the extractor, auto-add the 'dasha' category.
    This fixes the 49 dead books that have untagged dasha content.
    Also, for the 18 silent books, if the rule contains a planet, auto-add 'dasha'
    to make them dasha-triggering rules.
    """
    if any(c in categories for c in ("dasha", "dasa", "bhukti", "antardasha")):
        return categories  # already tagged
    if _DASHA_KW.search(text):
        return list(categories) + ["dasha"]
        
    SILENT_BOOKS = {
        "BPHS_Sharma_Vol1_deep",
        "Brighu_Naadi_Sangraha_gemma",
        "Brihat_Jataka_Sastri_deep",
        "Brihat_Jataka_deep",
        "Frawley_Seers_gemma",
        "Garga_Hora_Shastra_gemma",
        "Jaimini_Sutras_deep",
        "Jataka_Bharanam_deep",
        "Jataka_Parijata_deep",
        "Jataka_Tattva_deep",
        "Raman_300Combinations_gemma",
        "Ravana_Samhita_gemma",
        "Saravali_deep",
        "Tajik_Adawal_Encyclopedia_deep",
        "Tajik_Adawal_Encyclopedia_gemma",
        "Tajika_Neelakanthi_deep",
        "Tajika_Neelakanthi_gemma",
        "Uttara_Kalamrita_gemma",
        "Varshaphal_Raman_gemma",
        "Yavanajataka_2_gemma",
        "Yogini_Dasha_Goel_gemma",
    }
    if any(b in SILENT_BOOKS for b in books):
        if involves_planets:
            return list(categories) + ["dasha"]
        planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        t_low = text.lower()
        if any(p.lower() in t_low for p in planets):
            return list(categories) + ["dasha"]
            
    return categories

def _normalize(text: str) -> str:
    """Canonical form for dedup comparison — strips common prefixes to find hidden duplicates."""
    t = text.lower().strip()
    t = re.sub(r"\s+", " ", t)
    # Strip common leading fillers
    t = re.sub(r"^(for a|if the|the native|the person|in this case|it is said that|sages say that|according to the text)\s+", "", t)
    t = re.sub(r"^(lagna|ascendant|sign|house|lord|planet)\s+", "", t)
    t = re.sub(r"[^\w\s]", "", t)
    return t

def _fingerprint(text: str) -> str:
    """Short fingerprint = first 40 normalized chars — catches significantly more near-dups."""
    return _normalize(text)[:40]


# ─── Data model ────────────────────────────────────────────────────────────────

@dataclass
class CorpusRule:
    text: str                   # Canonical (longest) english translation
    original: str               # Original text of canonical version
    books: list[str]            # All source books (may be multiple after merge)
    verse_ids: list[str]        # All verse IDs
    categories: list[str]       # Union of categories across merged versions
    involves_planets: list[str]
    involves_houses: list[int]
    involves_signs: list[str]
    rule_type: str              # planet_house | planet_sign | yoga | dasha | transit | compound | general

    @property
    def source_label(self) -> str:
        """Human-readable source string for display."""
        return " + ".join(sorted(set(self.books)))

    @property
    def primary_book(self) -> str:
        return self.books[0] if self.books else "Unknown"


# ─── Corpus index ─────────────────────────────────────────────────────────────

NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha",
    "Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
    "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]

# ─── Books excluded from the prediction corpus ────────────────────────────────
#
# A — ASTRONOMICAL / MATHEMATICAL: contain orbital mechanics, eclipse geometry,
#     calendar arithmetic. Zero natal life-event prediction rules.
# B — DUPLICATE GEMMA EXTRACTS: inferior version of same book already loaded
#     as a richer '_deep' extraction. Keeping both adds noise & double-counts.
# C — DOMAIN MISMATCH (Muhurtha / Prashna / Horary): predict auspicious
#     moments or answer horary questions — completely different domain from
#     natal dasha prediction. Their rules misfire badly against natal events.
# D — EMPTY NOISE: 1-3 rules, avg <30 chars, OCR fragments.
EXCLUDED_BOOKS: set[str] = {
    # A — Pure astronomy, no natal prediction
    "Aryabhatiya_v1_gemma",
    "Aryabhatiya_v2_gemma",
    "Surya_Siddhanta_gemma",
    "Surya_Siddhanta_deep",
    "Vedanga_Jyotisa_gemma",
    "Pancha_Siddhantika_gemma",
    "Pancha_Siddhantika_cerebras",
    "Pancha_Siddhantika_nvidia",
    "Pancha_Siddhantika_sambanova",
    "Pancha_Siddhantika_google",
    "Pancha_Siddhantika_groq",

    # B — Inferior gemma duplicates (deep version is already loaded)
    "BPHS1_gemma",
    "BPHS_Vol1_gemma",
    "BPHS2_gemma",
    "Phaladeepika_gemma",
    "Sarvartha_Chintamani_gemma",
    "Hora_Sara_gemma",
    "Saravali_gemma",
    "Bhrigu_Samhita_gemma",
    "Brihat_Jataka_gemma",
    "Brihat_Jataka_Sastri_gemma",
    "Jaimini_Sutras_gemma",
    "Jataka_Parijata_gemma",
    "Bhavartha_Ratnakara_Raman_gemma",
    "Muhurtha_Chintamani_gemma",
    "BPHS_Sharma_Vol1_gemma",
    "Lal_Kitab_gemma",
    "KP_Reader_gemma",
    "Prashna_Marga_gemma",
    "Surya_Siddhanta_gemma",
    "Laghu_Parashari_gemma",
    "Ravana_Samhita_gemma",
    "Uttara_Kalamrita_gemma",
    "KP_Reader_3_Predictive_gemma",
    "Lal_Kitab_Original_gemma",
    "Raman_300Combinations_gemma",
    "Tajik_Adawal_Encyclopedia_gemma",
    "Tajika_Neelakanthi_gemma",

    # C — Muhurtha / Horary / domain mismatch (not natal prediction)
    "Prashna_Marga_deep",
    "Muhurtha_Chintamani_deep",   # electional astrology, not natal dasha

    # D — Empty noise files (original)
    "Unknown_6945_gemma",
    "Yavanajataka_1_gemma",
    "Phaladeepika_Sastri_gemma",
    "Chamatkar_Chintamani_gemma",
    "Krishneeyam_gemma",

    # E — Zero-rule failed extractions (added 2026-07-11 audit)
    "BPHS_Vol2_gemma",
    "Brighu_Naadi_Sangraha_gemma",
    "Brihat_Parashara_v2_gemma",
    "Deva_Keralam_Vol1_deep",        # extraction yielded 0 rules
    "Frawley_Seers_gemma",
    "Garga_Hora_Shastra_gemma",
    "KP_Reader_2_Fundamentals_gemma",
    "KP_Reader_6_Horary_gemma",
    "Phaladeepika_gemini3",          # old extraction, superseded by _deep
    "question_catalog",              # metadata file, not a book
    "Raman_AstrologyForBeginners_gemma",
    "Raman_HowToJudge_gemma",
    "Raman_Notable_Horoscopes_gemma",
    "Rath_Crux_gemma",
    "Varshaphal_Raman_gemma",
    "Yavanajataka_2_gemma",
    "Yogini_Dasha_Goel_gemma",
}


class Corpus:
    """
    Loaded-once, queried-many-times rule corpus.
    Build with Corpus.load(gemma_dir).
    """
    def __init__(self):
        self._planet_house:  dict[tuple, list[CorpusRule]] = defaultdict(list)
        self._planet_sign:   dict[tuple, list[CorpusRule]] = defaultdict(list)
        self._nakshatra:     dict[str, list[CorpusRule]]   = defaultdict(list)
        self._dasha:         dict[str, list[CorpusRule]]   = defaultdict(list)
        self._yoga:          list[CorpusRule] = []
        self._transit:       list[CorpusRule] = []
        self._compound:      list[CorpusRule] = []
        self._all:           list[CorpusRule] = []
        self.stats: dict = {}
        self.authority: dict = {}
        self._load_authority()

    def _load_authority(self):
        """Loads weighting hierarchy from logic_base."""
        try:
            path = Path(__file__).parent.parent / "logic_base" / "authority_hierarchy.json"
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.authority = data["hierarchy"]
        except Exception:
            self.authority = {}

    def get_rule_weight(self, books: list[str]) -> float:
        """Calculates the max authority weight among citing books."""
        max_w = 0.5 # Default low weight for unknown books
        for b in books:
            # Check hierarchy
            for cat, info in self.authority.items():
                if b in info["books"]:
                    max_w = max(max_w, info["weight"])
                    break
        return max_w

    # ── Loader ─────────────────────────────────────────────────────────────────

    @classmethod
    def load(cls, gemma_dir: str | Path) -> "Corpus":
        gemma_dir = Path(gemma_dir)

        # PASS 1: Collect all raw rules, filtering junk
        raw_rules: list[dict] = []
        book_counts: dict[str, int] = {}

        for fname in sorted(gemma_dir.glob("*.json")):
            try:
                with open(fname, encoding="utf-8", errors="replace") as f:
                    data = json.load(f)
            except Exception:
                continue

            # Treat every unique file as a distinct book
            book = fname.stem

            # Skip non-predictive / duplicate / astronomical books
            if book in EXCLUDED_BOOKS:
                continue

            # Extract rules from multiple possible schemas (flat or chunked)
            if isinstance(data, list):
                rules_to_process = list(data)
            else:
                rules_to_process = list(data.get("rules", []))
                # If chunked schema (Gemma/Deep extractions)
                if "chunks" in data:
                    for chunk in data["chunks"]:
                        if "predictive_rules" in chunk:
                            for r in chunk["predictive_rules"]:
                                # Try to extract metadata from trigger text if missing
                                trigger = (r.get("trigger") or "").strip()
                                effect = (r.get("effect") or "").strip()
                                planets, houses, signs = _parse_metadata(trigger + " " + effect)
                                
                                rules_to_process.append({
                                    "english_translation": effect,
                                    "original_text": trigger,
                                    "categories": ["general"],
                                    "involves_planets": planets,
                                    "involves_houses": houses,
                                    "involves_signs": signs
                                })
                        if "yogas_named" in chunk:
                             for y in chunk["yogas_named"]:
                                 rules_to_process.append({
                                    "english_translation": y.get("effects"),
                                    "original_text": y.get("yoga_name"),
                                    "categories": ["yoga"],
                                    "involves_planets": [],
                                    "involves_houses": [],
                                    "involves_signs": []
                                 })

            for raw in rules_to_process:
                text = (raw.get("english_translation") or "").strip()
                if not text or _is_junk(text):
                    continue

                cats = [c.lower() for c in (raw.get("categories") or [])]
                planets = raw.get("involves_planets") or []
                houses  = [int(h) for h in (raw.get("involves_houses") or []) if str(h).isdigit()]
                signs   = raw.get("involves_signs") or []

                # FIX 1: Auto-detect dasha mentions missed by the extractor
                cats = _auto_tag_dasha(text, cats, [book], planets)

                # FIX 2: Drop purely procedural rules with no astrological content
                if not _is_predictive(text, planets, houses, signs, cats):
                    continue

                raw_rules.append({
                    "text": text,
                    "original": (raw.get("original_text") or "").strip(),
                    "book": book,
                    "verse_id": raw.get("verse_id") or "",
                    "categories": cats,
                    "planets": planets,
                    "houses": houses,
                    "signs": signs,
                })
                book_counts[book] = book_counts.get(book, 0) + 1

        # PASS 2: Deduplicate by normalized text fingerprint
        # Group by fingerprint → pick longest text as canonical, merge sources
        fp_groups: dict[str, list[dict]] = defaultdict(list)
        for r in raw_rules:
            fp = _fingerprint(r["text"])
            fp_groups[fp].append(r)

        # PASS 3: Build CorpusRule per group (merge duplicates)
        corpus = cls()
        total_merged = 0
        total_unique = 0

        for fp, group in fp_groups.items():
            # Canonical = longest text version
            canonical = max(group, key=lambda x: len(x["text"]))

            # Merge metadata from all versions in group
            all_books    = list({r["book"] for r in group})
            all_verse_ids = list({r["verse_id"] for r in group if r["verse_id"]})
            all_cats     = list({c for r in group for c in r["categories"]})
            all_planets  = list({p for r in group for p in r["planets"]})
            all_houses   = sorted({h for r in group for h in r["houses"]})
            all_signs    = list({s for r in group for s in r["signs"]})

            rule = CorpusRule(
                text=canonical["text"],
                original=canonical["original"],
                books=all_books,
                verse_ids=all_verse_ids,
                categories=all_cats,
                involves_planets=all_planets,
                involves_houses=all_houses,
                involves_signs=all_signs,
                rule_type="general",
            )

            corpus._classify_and_index(rule)
            corpus._all.append(rule)

            if len(group) > 1:
                total_merged += len(group) - 1
            else:
                total_unique += 1

        corpus.stats = {
            "raw_collected": len(raw_rules),
            "junk_filtered": sum(book_counts.values()) - len(raw_rules),
            "duplicates_merged": total_merged,
            "total_unique_rules": len(corpus._all),
            "books_loaded": len(book_counts),
            "book_counts": book_counts,
            "planet_house_slots": len(corpus._planet_house),
            "planet_sign_slots": len(corpus._planet_sign),
            "yoga_rules": len(corpus._yoga),
            "dasha_rules": sum(len(v) for v in corpus._dasha.values()),
            "transit_rules": len(corpus._transit),
            "compound_rules": len(corpus._compound),
        }
        return corpus

    def _classify_and_index(self, r: CorpusRule):
        cats = r.categories
        planets = r.involves_planets
        houses = r.involves_houses
        signs = r.involves_signs

        indexed = False

        # 1. Yoga rules
        if "yoga" in cats:
            r.rule_type = "yoga"
            self._yoga.append(r)
            indexed = True

        # 2. Dasha / Antardasha rules
        if any(c in cats for c in ("dasa", "dasha", "antardasha", "bhukti")):
            r.rule_type = "dasha"
            if not planets:
                SILENT_BOOKS = {
                    "BPHS_Sharma_Vol1_deep",
                    "Brighu_Naadi_Sangraha_gemma",
                    "Brihat_Jataka_Sastri_deep",
                    "Brihat_Jataka_deep",
                    "Frawley_Seers_gemma",
                    "Garga_Hora_Shastra_gemma",
                    "Jaimini_Sutras_deep",
                    "Jataka_Bharanam_deep",
                    "Jataka_Parijata_deep",
                    "Jataka_Tattva_deep",
                    "Raman_300Combinations_gemma",
                    "Ravana_Samhita_gemma",
                    "Saravali_deep",
                    "Tajik_Adawal_Encyclopedia_deep",
                    "Tajik_Adawal_Encyclopedia_gemma",
                    "Tajika_Neelakanthi_deep",
                    "Tajika_Neelakanthi_gemma",
                    "Uttara_Kalamrita_gemma",
                    "Varshaphal_Raman_gemma",
                    "Yavanajataka_2_gemma",
                    "Yogini_Dasha_Goel_gemma",
                }
                if any(b in SILENT_BOOKS for b in r.books):
                    for p in PLANETS:
                        self._dasha[p].append(r)
                else:
                    self._dasha["_general"].append(r)
            else:
                for p in planets:
                    self._dasha[p].append(r)
            indexed = True

        # 3. Transit / Gochar
        if any(c in cats for c in ("transit", "gochara", "gochar", "transits")):
            r.rule_type = "transit"
            self._transit.append(r)
            indexed = True

        # 4. Nakshatra-specific
        if any(c in cats for c in ("nakshatra", "constellation", "star")):
            r.rule_type = "nakshatra"
            matched = False
            txt_low = r.text.lower()
            for nak in NAKSHATRA_NAMES:
                if nak.lower() in txt_low:
                    self._nakshatra[nak].append(r)
                    matched = True
            if not matched:
                self._nakshatra["_general"].append(r)
            indexed = True

        # 5. Planet + House (1:1 — the primary classical format)
        if len(planets) == 1 and len(houses) == 1:
            r.rule_type = "planet_house"
            self._planet_house[(planets[0], houses[0])].append(r)
            indexed = True
        elif len(planets) == 1 and len(houses) > 1:
            # Fan out to each house
            r.rule_type = "planet_house"
            for h in houses:
                self._planet_house[(planets[0], h)].append(r)
            indexed = True

        # 6. Planet + Sign (1:1, no house)
        if len(planets) == 1 and len(signs) == 1 and not houses:
            r.rule_type = "planet_sign"
            self._planet_sign[(planets[0], signs[0])].append(r)
            indexed = True

        # 7. Compound (2+ planets, important for yoga/conjunction rules)
        if len(planets) >= 2:
            r.rule_type = "compound"
            self._compound.append(r)
            indexed = True

        # 8. Anything with a house but no single-planet match
        if not indexed and houses:
            for h in houses:
                self._planet_house[("_general", h)].append(r)

    # ── Query API ──────────────────────────────────────────────────────────────

    def get_planet_in_house(
        self,
        planet: str,
        house: int,
        limit: int = 8,
        lagna_sign: str | None = None,
    ) -> list[CorpusRule]:
        """Classical rules for planet in house; optional lagna_sign drops other-lagna-only lines."""
        rules = self._planet_house.get((planet, house), [])
        if lagna_sign:
            rules = [r for r in rules if rule_applies_to_lagna(r.text, lagna_sign)]
        rules.sort(key=lambda r: (-self.get_rule_weight(r.books), -len(r.books)))
        return rules[:limit]

    def get_planet_in_sign(
        self,
        planet: str,
        sign: str,
        limit: int = 6,
        lagna_sign: str | None = None,
    ) -> list[CorpusRule]:
        rules = self._planet_sign.get((planet, sign), [])
        if lagna_sign:
            rules = [r for r in rules if rule_applies_to_lagna(r.text, lagna_sign)]
        rules.sort(key=lambda r: (-self.get_rule_weight(r.books), -len(r.books)))
        return rules[:limit]

    def get_nakshatra_rules(self, nakshatra: str, limit: int = 5) -> list[CorpusRule]:
        return self._nakshatra.get(nakshatra, [])[:limit]

    def get_yoga_rules(self, yoga_name: str, limit: int = 5) -> list[CorpusRule]:
        """Find corpus textual evidence for a specific yoga name."""
        yoga_name = yoga_name.lower()
        results = []
        for r in self._yoga:
            if yoga_name in r.text.lower():
                results.append(r)
        return results[:limit]

    def get_dasha_rules(self, dasha_lord: str, antardasha_lord: str = "",
                         limit: int = 6) -> list[CorpusRule]:
        rules = self._dasha.get(dasha_lord, []).copy()
        if antardasha_lord and antardasha_lord != dasha_lord:
            seen = {r.text for r in rules}
            for r in self._dasha.get(antardasha_lord, []):
                if r.text not in seen:
                    rules.append(r)
                    seen.add(r.text)
        rules.sort(key=lambda r: (-self.get_rule_weight(r.books), -len(r.books)))
        return rules[:limit]

    def get_compound_rules(self, planets: list[str], houses: list[int] = [],
                            limit: int = 5) -> list[CorpusRule]:
        """Find rules involving a specific combination of planets (conjunctions/yogas)."""
        pset = set(planets)
        hset = set(houses)
        scored = []
        for r in self._compound:
            rp = set(r.involves_planets)
            rh = set(r.involves_houses)
            p_overlap = len(pset & rp)
            h_overlap = len(hset & rh) if hset else 0
            if p_overlap >= 2 or (p_overlap >= 1 and h_overlap >= 1):
                # Score = Overlap + Authority + Corroboration
                score = p_overlap * 2 + h_overlap + self.get_rule_weight(r.books) * 5 + len(r.books) * 0.5
                scored.append((score, r))
        scored.sort(key=lambda x: -x[0])
        return [r for _, r in scored[:limit]]

    def get_transit_rules(self, planet: str = "", limit: int = 6) -> list[CorpusRule]:
        if not planet:
            return self._transit[:limit]
        return [r for r in self._transit if planet.lower() in r.text.lower()][:limit]

    def describe(self) -> str:
        s = self.stats
        return (
            f"Corpus: {s['total_unique_rules']} unique rules "
            f"(from {s['raw_collected']} raw, "
            f"{s['duplicates_merged']} duplicates merged, "
            f"{s.get('junk_filtered', 0)} OCR-junk removed) | "
            f"{s['books_loaded']} books | "
            f"{s['planet_house_slots']} P×H slots | "
            f"{s['yoga_rules']} yoga | "
            f"{s['dasha_rules']} dasha | "
            f"{s['transit_rules']} transit | "
            f"{s['compound_rules']} compound"
        )


# ─── Singleton loader ──────────────────────────────────────────────────────────

_CORPUS: Optional[Corpus] = None

def get_corpus(gemma_dir: str | Path | None = None) -> Corpus:
    """
    Singleton corpus — loads once, cached forever in process memory.
    First load takes ~2-3 seconds for 14k rules. Subsequent calls instant.
    """
    global _CORPUS
    if _CORPUS is None:
        if gemma_dir is None:
            here = Path(__file__).parent.parent
            gemma_dir = here / "gemma_extractions"
        _CORPUS = Corpus.load(gemma_dir)
        print(f"[Corpus] {_CORPUS.describe()}")
    return _CORPUS
