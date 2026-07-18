# Corpus Quality Audit � gemma_extractions + Merged Rules

**Date:** 2026-06-02  
**Scope:** Predictive rule corpus only (excludes birth-chart logic).  
**Claim under review:** *"gemma_extractions + merged rules � extracted text, deduped, can have gaps, duplicates, or mis-quotes vs printed books."*

---

## Verdict

**Yes � the claim is accurate.**

The pipeline is LLM/OCR-extracted JSON ? filtered ? fingerprint-deduped ? indexed. It is useful for cross-book predictive lookup and citation display, but it is **not** a verified, verbatim edition of the classical texts. Gaps, residual duplicates, and mis-quotes are expected and measured below.

---

## Architecture (how merge/dedup works)

Source: `engine/corpus.py`

```
gemma_extractions/*.json
        ?
        ?
  PASS 1 � Collect rules
    � Schemas: flat `rules[]` OR chunked `predictive_rules` / `yogas_named`
    � Skip EXCLUDED_BOOKS (39 stems: astronomy, muhurtha, inferior gemma dupes)
    � Drop: empty text, _is_junk() (OCR/procedural/non-ASCII-heavy)
    � Drop: _is_predictive() failures (no planets/houses/signs/dasha/outcome keywords)
    � Auto-tag dasha for "silent books"
        ?
        ?
  PASS 2 � Fingerprint dedup
    � _fingerprint() = first 40 chars of normalized text (lowercase, strip punctuation)
    � Group by fingerprint; canonical = longest english_translation
    � Merge: books[], verse_ids[], categories, planets, houses, signs
        ?
        ?
  PASS 3 � Index into planet�house, dasha, yoga, transit, compound, nakshatra
```

### Measured corpus stats (local + VPS � identical)

| Metric | Value |
|---|---:|
| JSON files in `gemma_extractions/` | **82** (81 books + `_MASTER_dedup.json`) |
| Books loaded into corpus | **41** |
| Raw rules collected (post-filter) | **17,066** |
| Duplicates merged (fingerprint groups) | **1,485** |
| **Total unique rules** | **15,581** |
| Rules citing 2+ books after merge | **152** |
| Planet�house index slots | 525 |
| Yoga / dasha / transit / compound | 3,996 / 2,896 / 144 / 3,900 |

VPS confirmation (`/opt/astro`, 2026-06-02): `15581 17066 41` � same counts as local.

Integration tests report `corpus_total_rules: 15581` via `main.py` ? `get_corpus()`.

> **Note:** The docstring in `corpus.py` cites "~14,795 rules from 58 books" � stale. Current measured load is **15,581 rules from 41 books**.

---

## What IS reliable

| Property | Evidence |
|---|---|
| **Deterministic dedup count** | Same 15,581 on local Windows and VPS Linux after `Corpus.load()` |
| **Multi-source citation merge** | 152 rules retain 2+ book names in `CorpusRule.books`; longest text wins as canonical |
| **Duplicate-book suppression** | 39 file stems in `EXCLUDED_BOOKS` prevent loading inferior `_gemma` when `_deep` exists (e.g. `BPHS1_gemma` excluded, `BPHS1_deep` loaded) |
| **Junk filtering** | ~1,359 rules dropped by `_is_junk()` (OCR markers, biographical prose, low ASCII ratio) |
| **Lookup indexes** | Planet�house, dasha lord, yoga, transit, compound queries are structurally sound |
| **Citation display structure** | `CorpusRule.source_label`, `books[]`, `verse_ids[]` fields exist for attribution |

---

## What is NOT guaranteed

| Risk | Why |
|---|---|
| **Verbatim scripture accuracy** | Rules are Gemini/Cerebras/Groq **paraphrases** of OCR'd PDF text, not scholar-verified translations |
| **Complete book coverage** | 6 `_deep` extractions marked `is_complete: false`; Bhrigu Samhita only 122/219 chunks |
| **No remaining duplicates** | Dedup uses **first 40 normalized chars only** � near-duplicates with different wording survive (~798 sampled pairs at 75�99% similarity within same book) |
| **Verse traceability** | **70.6%** of merged rules have **empty `verse_ids`** |
| **original_text fidelity** | OCR corruption is often preserved verbatim in `original_text` while `english_translation` is LLM-guesswork |
| **Cross-file duplicate cleanup** | **338** fingerprint-identical rule texts still appear across multiple JSON files in raw scan (mostly `_gemma` variants of books already excluded � but not all) |

---

## Measured findings

### File-level health

| Check | Result |
|---|---|
| Broken JSON | **0 / 82** |
| Files with raw `0x97` byte (Windows dash encoding) | **26 / 82** |
| Files with U+FFFD replacement character | **1** � `Jataka_Parijata_deep.json` |
| Pancha_Siddhantika duplicate extractions | **6 files** (all excluded: `_gemma`, `_cerebras`, `_google`, `_groq`, `_nvidia`, `_sambanova`) |

### Rule-level quality (all JSON files, pre-corpus)

| Metric | Count | % of raw entries |
|---|---:|---:|
| Total rule entries (incl. excluded books) | 41,583 | 100% |
| Empty `english_translation` | 14,992 | **36.0%** |
| Short rules (<15 chars) | 1,321 | 3.2% |
| OCR junk pattern (`unable to interpret`, `corrupted`, etc.) | 447 | 1.1% |

### Filter pipeline (excluding `_MASTER_dedup`, non-excluded books)

| Stage | Rules removed |
|---|---:|
| In `EXCLUDED_BOOKS` | 5,092 |
| Empty translation | 1,015 |
| Junk (`_is_junk`) | 1,359 |
| Non-predictive (`_is_predictive`) | 5,379 |
| **Passed to dedup** | **~14,788�17,066** |

### Extractor provenance (`_extractor` tags in rules)

| Tag | Rule count |
|---|---:|
| `gemini_cli` | 13,357 |
| `cerebras` | 1,132 |
| `native_parser_v1` | 717 |
| `groq` | 660 |
| `sambanova` | 331 |
| `deep_v1 (verbatim, anti-censor, page-chunked)` | 22 |
| `nvidia` | 16 |
| `gemini_api` | 3 |

Most rules come from automated LLM extraction (`gemini_cli`), not human-verified parsing.

### Incomplete extractions (coverage gaps)

| Book | Progress | Impact |
|---|---|---|
| `Jataka_Bharanam_deep` | 59 / 505 chunks | **~88% missing** |
| `Surya_Siddhanta_deep` | 219 / 320 chunks | excluded (astronomy) but file incomplete |
| `KP_Reader_3_Predictive_deep` | 210 / 378 chunks | ~44% missing |
| `Bhrigu_Samhita_deep` | 122 / 219 chunks | ~44% missing |
| `Sarvartha_Chintamani_deep` | 108 / 130 chunks | excluded (noise) |
| `BPHS1_deep` | 199 / 203 chunks | nearly complete |

### Duplicate examples

**Cross-file (same fingerprint, different JSON files):**

- `"wealth and prosperity"` � 7 files including `Brihat_Jataka_gemma`, `Garga_Hora_Shastra_gemma`, `Sarvartha_Chintamani_gemma`
- `"native will gain wealth through his wife"` � 4 BPHS variants (`BPHS1_gemma`, `BPHS_Sharma_Vol1_gemma`, `BPHS_Vol1_gemma`, `Brihat_Parashara_v2_gemma`)

Most cross-file dupes are `_gemma` files that are excluded at load time; dedup merges them only if both stems are loaded (rare).

**Within-file (survives dedup � different fingerprints):**

- `BPHS1_deep`: 5 exact 80-char prefix duplicates including `"(highly corrupted sanskrit text, untranslatable literally)"` appearing 3�

**Near-duplicate (NOT merged � sampled):**

- `Bhavartha_Ratnakara_Raman_deep`: `"Combinations for wealth"` vs `"Combinations for poverty"` � 75�99% similar, kept as separate rules

### Mis-quote / OCR risk examples

From `Bhrigu_Samhita_deep.json` (loaded, 2,112 raw rules, `is_complete: false`):

```
original_text:  "... su lokastha wailed ..."
english_translation: "In the circle of light (zodiac)... it 'wailed' auspicious..."
```

```
english_translation: "... among the 'raver' Yavanas (foreigners)..."
original_text:  "... Raver hi yavan?ste?u ..."   ? OCR garbage passed through
```

```
english_translation: "... Guru, Som, 'qe', and Shukra ..."
                              ^^^ unresolved OCR token kept in output
```

From `logic_base/rule_engine.json` (separate curated artifact, not the corpus engine):

- Embedded corpus citations contain OCR artifacts: `"ibe native will b.e. exceedingly libidinous"`, `"Vr\"\"t .i\"f\"i\"g o .ut.fi\" in any house"`
- Bhrigu Samhita citations include LLM placeholders: `"sign 'ge'"`, `"means of 'gag'"`, `"likely a typo for an enemy planet's sign"`

These are appended from corpus lookups at build time � confirming mis-quotes propagate to downstream display.

### Sample book audit (10 books)

| Book | Raw rules | Empty | OCR junk | In corpus | Extractor |
|---|---:|---:|---:|---|---|
| `BPHS1_deep` | 3,061 | 112 | 11 | Yes | n/a |
| `Phaladeepika_deep` | 639 | 40 | 0 | Yes | n/a |
| `Laghu_Parashari_deep` | 286 | 0 | 0 | Yes | n/a |
| `Brihat_Jataka_deep` | 62 | 0 | 0 | Yes | n/a |
| `Saravali_deep` | 61 | 1 | 0 | Yes | n/a |
| `KP_Reader_3_Predictive_deep` | 2,560 | 55 | 0 | Yes | n/a |
| `Garga_Hora_Shastra_gemma` | 108 | 1 | 0 | Yes | n/a |
| `Ravana_Samhita_deep` | 246 | 0 | 0 | Yes | n/a |
| `Uttara_Kalamrita_deep` | 182 | 0 | 0 | Yes | n/a |
| `Bhrigu_Samhita_deep` | 2,112 | 78 | 21 | Yes | deep_v1 |

`Tajik_Adawal_Encyclopedia_deep`: 9 rules, mostly empty translations � **0 rules loaded** (all filtered). The `_gemma` version supplies corpus content instead.

---

## rule_engine.json vs corpus

These are **different artifacts**:

| | `engine/corpus.py` | `logic_base/rule_engine.json` |
|---|---|---|
| Purpose | Runtime multi-book rule lookup | Curated BPHS-centric display text for planet�house predictions |
| Rule count | 15,581 unique merged rules | Hand-authored base + appended `[Book]` citation blocks |
| Source | All 41 loaded gemma/deep JSONs | Brihat Parashara (Santhanam) + corpus citation injection |
| Quality | Extraction pipeline | Same corpus mis-quotes can appear inside citation appendices |

Do not treat `rule_engine.json` as ground truth for scripture accuracy � it inherits corpus extraction errors.

---

## Existing tooling reviewed

| Tool | Relevance |
|---|---|
| `runtime/_corpus_quality_audit.py` | Scores **raw book passages** (`book_corpus_index_v2.json`, 11,692 chunks) � parallel quality layer, not the gemma rule corpus |
| `docs/CORPUS_QUALITY_SCORES.md` | Passage-level v3 scores; confirms OCR junk in astronomy books and thin topic coverage (e.g. `sade_sati`: 0 HQ passages) |
| `scratch/verify_native_rules.py` | Validates schema + keyword alignment for 3 deep books only (`Laghu_Parashari`, `Uttara_Kalamrita`, `Ravana_Samhita`); path points to `f:/Atro` (typo) |

---

## Remediation (2026-06-02 session)

Attempted to complete the 6 incomplete `_deep` extractions. **No corpus JSON files were modified** � extraction cannot run without restored tooling.

### Completed this session

| Action | Result |
|---|---|
| Full inventory of `is_complete: false` files | 6 books (see incomplete table above) |
| Source text verification (local + VPS) | All 6 books have `Books/*_extracted.txt` on both |
| Extraction pipeline discovery | `_workbench/_deep_extract.py` referenced but **missing** everywhere |
| API key check | `_workbench/.keys/` missing; VPS `vault.db` is **0 bytes** |
| Corpus stats before/after | **15,581** unique rules � **unchanged** |
| Runbook written | `docs/CORPUS_COMPLETION_RUNBOOK.md` |
| Audit helpers added | `scratch/_inventory_incomplete.py`, `_analyze_chunk_coverage.py`, etc. |

### Blocked � requires user action

| Book | Gap | Blocker |
|---|---|---|
| `Jataka_Bharanam_deep` | 59/505 (88% missing) | No `_deep_extract.py`; no API keys; 202 rules in live corpus |
| `Bhrigu_Samhita_deep` | 122/219 (44% missing) | Same � ~353 KB source unprocessed |
| `KP_Reader_3_Predictive_deep` | 210/378 (44% missing) | Same � ~445 KB source unprocessed |
| `Sarvartha_Chintamani_deep` | 108/130 (17% missing) | Same � loaded into corpus |
| `BPHS1_deep` | 199/203 (2% missing) | Same � do **not** set `is_complete: true` until last 4 chunks extracted |
| `Surya_Siddhanta_deep` | 219/320 (32% missing) | Same � excluded from corpus (`EXCLUDED_BOOKS`) |

**Why gemma merge was rejected:** `engine/corpus.py` deliberately excludes `*_gemma.json` when `*_deep.json` exists. Shallow gemma variants hold 45�1,107 non-overlapping rules per book but a different schema; merging would bypass the exclusion policy without fixing chunk coverage.

**Next user step:** Restore `F:/Atro/_workbench/` (per `scratch/diff_report.md`) to VPS, add API keys via vault, then follow `docs/CORPUS_COMPLETION_RUNBOOK.md`.

---

## Recommended fixes (priority)

### P0 � Data completeness blockers

1. **Finish incomplete deep extractions** � especially `Jataka_Bharanam_deep` (59/505) and `Bhrigu_Samhita_deep` (122/219). These are loaded into the live corpus with partial coverage. **Blocked 2026-06-02:** restore `_workbench/_deep_extract.py` + API keys (see runbook).
2. **Fix encoding in `Jataka_Parijata_deep.json`** � only file with U+FFFD replacement characters; re-OCR or re-extract from source PDF.

### P1 � Dedup and provenance

3. **Strengthen dedup fingerprint** � current 40-char prefix merges `"Combinations for wealth"` and `"Combinations for poverty"` incorrectly when prefixes align, but misses near-duplicates when they differ. Use full normalized text hash + fuzzy merge threshold.
4. **Backfill or require `verse_id`** � 70.6% of rules lack verse IDs; add page/chunk offset from `_chunk_idx` as minimum provenance when verse unknown.
5. **Move `_MASTER_dedup.json` out of `gemma_extractions/`** � prevents accidental double-processing; glob currently loads all `*.json`.

### P2 � Verification layer

6. **Extend `verify_native_rules.py` to all `_deep` books** � schema + keyword overlap against `Books/*_extracted.txt`; flag rules with placeholder tokens (`'ge'`, `'qe'`, `'wailed'`).
7. **Add extraction confidence score to `CorpusRule`** � propagate `quality_v3` from passage index or inline heuristics; suppress citations below threshold 0.55 in user-facing output.
8. **Document `EXCLUDED_BOOKS` in a manifest** � 39 excluded stems are invisible at runtime; a `corpus_manifest.json` would make gaps auditable without reading source code.

---

## Summary table

| User claim element | Confirmed? | Key evidence |
|---|---|---|
| Extracted text (not original books) | **Yes** | LLM `_extractor: gemini_cli` on 13,357 rules; OCR in `original_text` |
| Deduped | **Yes** | 17,066 ? 15,581 (1,485 merged); fingerprint-based |
| Can have gaps | **Yes** | 6 incomplete extractions; 36% empty translations in raw JSON; 39 books excluded |
| Can have duplicates | **Yes** | 338 cross-file fingerprint dupes in raw; ~798 near-dup pairs survive dedup |
| Can mis-quote printed books | **Yes** | OCR tokens in output; LLM paraphrase without source verification; examples in Bhrigu Samhita + rule_engine.json |

**Bottom line:** Use the corpus for **cross-book predictive evidence and attribution hints**, not as a **canonical scripture reference**. Treat every quoted rule as *extracted and unverified* unless manually checked against the printed source.
