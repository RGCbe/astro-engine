# Why We Are Not Just a Book � Honest Client + Dev Brief

**Audience:** Manoj (client complaint), product, developers  
**Project:** `F:\astro` � Vedic engine  
**Date:** 2026-06-02  
**Related:** [PREDICTION_METHODOLOGY.md](./PREDICTION_METHODOLOGY.md), [ASTROLOGER_CLIENT_WORKFLOW.md](./ASTROLOGER_CLIENT_WORKFLOW.md), [WHY_TAMIL_PDF_WAS_BASIC.md](./WHY_TAMIL_PDF_WAS_BASIC.md), [BACKEND_FOCUS.md](./BACKEND_FOCUS.md)

---

## Executive honesty (read this first)

Manoj�s complaint is **partly fair**. The deliverables he saw (`MANOJ_TAMIL.pdf`, and even parts of `MANOJ_PREDICTIONS_TA.pdf`) **sound like a book** because they use the same vocabulary every Jyotish text uses: �marriage period,� �Jupiter is good,� �7th lord dasha.� That vocabulary is not wrong � it is **generic without chart-specific synthesis**.

What we actually run under the hood is **not** a human astrologer session. It is a **rule engine** that scores dated windows from **this birth time�s** lagna, house lords, dasha chain, and transit triggers � then prints bands. The gap is **presentation and synthesis**, not absence of machinery.

This document separates: (1) what the PDF really is, (2) what is genuinely different from apps and DIY book reading, (3) what books still beat us at, and (4) what to build so Manoj�s next report is **non-basic**.

---

## 1. What the current Manoj PDF actually is

### 1.1 Product types Manoj received

| Deliverable | Generator | What it is |
|-------------|-----------|------------|
| `MANOJ_TAMIL.pdf` | `runtime/generate_tamil_pdf.py` | Chart booklet: panchanga, D1/D9 boxes, yoga names, **9 generic Mahadasha chapters** (`MD_THEME_TA`), ~6 near-term events on cover |
| `MANOJ_PREDICTIONS_TA.pdf` | `scratch/_manoj_tamil_predictions_report.py` | Tamil tables of **ranked date bands** from `event_predictor_v2` |
| English deep batch | `scratch/run_manoj_deep_report.py` + `runtime/engine_orchestrator.py` | 77-module JSON run; mostly **not narrated** in one client PDF |

See [WHY_TAMIL_PDF_WAS_BASIC.md](./WHY_TAMIL_PDF_WAS_BASIC.md) for the product split.

### 1.2 The prediction pipeline (not �AI astrologer prose�)

Production life-event path:

```
charts/manoj_chart.json
  ? engine/chart_builder.py (sidereal D1, whole-sign houses)
  ? runtime/granular_dasha.py (Vimshottari MD/AD/PD)
  ? runtime/transit_engine.py (snapshot triggers, ~2.5� orb)
  ? runtime/event_predictor_v2.py
       scan_lifetime_v2 (10�14 day sample grid)
       ? ~197 hand-written event_* patterns (+ optional catalog patterns)
       ? collapse_consecutive (merge adjacent samples into bands)
       ? rank_and_consume (top-N per category)
  ? PDF / MD table render
```

**What each band contains mechanically:**

- `window_start` / `window_end` (months to years wide � **not** day-precision)
- `category` (marriage, career, father, �)
- `severity` (signal strength 1�5, **not** good/bad)
- `why` (cause chain: e.g. �7L Mercury AD � Jupiter transits 7L�)
- Optional `predicted_valence` (only some patterns set this; many default to category neutral)

**What it does NOT contain today:**

- A spoken �who you are� story before timing
- Bhava-by-bhava life reading
- Reconciliation when BPHS and Lal Kitab disagree
- Remedies with conditions
- Guaranteed outcomes

### 1.3 Why it *feels* like book-level reading

| Surface text | Why it sounds generic | Under the hood (if shown) |
|--------------|----------------------|---------------------------|
| �Marriage window 2026�2031� | Every book says Venus/7L periods marry | **Mercury** is Manoj�s 7L (Gemini 7H); band fires because **his** 7L is in AD + Jupiter transit to **his** 7L � not sun-sign Venus transit |
| �Jupiter good / wealth yoga� | Lal Kitab lists Jupiter in 1st as strong | True for **Sagittarius lagna** with Jupiter H1; engine also scores **Lakshmi Yoga** only when dasha sub-periods align |
| �Father event childhood� | Pitra/ketu childhood chapters in any text | Band = Ketu MD + Pitra Dosha + Saturn return + Mars on **his** Sun (H6) � scored, not narrated |
| Nine dasha �life chapters� in Tamil PDF | `MD_THEME_TA` / `MD_EXPECT_TA` are **template strings per planet** | Same copy for every Sagittarius native in Ketu MD � **not** Manoj-specific synthesis |

**Root cause of �basic� feel:** We surface **timing labels + template dasha themes** before we surface **�here is your chart�s unique promise and conflict map.�** A reader who finished Lal Kitab recognizes the words; they do not yet see **why this window is yours**.

### 1.4 Corpus citations in PDF (supporting, often misleading)

`generate_tamil_pdf.py` and book-battle paths pull `engine/corpus.py` via `get_planet_in_house(planet, house)` � **indexed by placement only, not filtered by lagna**. A line written for �Scorpio lagna� can appear for Manoj�s Sagittarius chart. See [PREDICTION_METHODOLOGY.md �5](./PREDICTION_METHODOLOGY.md).

Corpus rules carry `verse_ids` and `books[]`, but client PDFs rarely show **page-level** citations.

---

## 2. What IS different today (real, verifiable)

These are **not** marketing claims � each has a file path and a test or fixture.

### 2.1 Mechanical chart from exact birth time (not sun-sign)

| Fact | Source |
|------|--------|
| Manoj: 1996-05-25 20:25 Coimbatore ? **Sagittarius lagna**, Magha Moon, Ketu MD at birth | `charts/manoj_chart.json` |
| Lahiri ayanamsa, Swiss Ephemeris, whole-sign houses from computed lagna | `engine/chart_builder.py` |
| House lords are **lagna-relative** (e.g. Manoj 5L=Mars, 7L=Mercury, 9L=Sun) | `event_predictor_v2._lord(lagna_idx, h)` |

**Competitors / typical apps:** Sun-sign dailies, generic �Venus in 7th� blurbs without birth time, or tropical Western charts. Even Brihat-style PDFs often use **template paragraphs** keyed only by planet-in-sign, not full lordship table for **this** ascendant.

### 2.2 ~197 pattern library + ranked windows with cause chains

| Fact | Source |
|------|--------|
| **197** hand-written `event_*` functions in `ALL_PATTERNS_V2` (Phases 0�6) | `runtime/event_predictor_v2.py` ~L3757�3821 |
| Optional +80 declarative catalog patterns | `claude_categories.ALL_CATALOG_PATTERNS` (when import succeeds) |
| Sample grid ? merge ? rank pipeline | `scan_lifetime_v2`, `collapse_consecutive`, `rank_and_consume` |
| Each hit can include `why[]` cause list | Pattern return dicts (e.g. `event_father` ~L46�118) |

**Example (Manoj, verifiable):** `MANOJ_PREDICTIONS_TA.md` shows marriage band **2026-06-18 ? 2031-12-31** with causes: 7L Mercury AD, Jupiter transit to natal 7L, benefic stack � not a static �age 28�32� book table.

### 2.3 ~15.6k corpus, multi-book (when filtered responsibly)

| Fact | Source |
|------|--------|
| **15,581** unique deduplicated rules from **41** loaded books | [CORPUS_QUALITY_AUDIT.md](./CORPUS_QUALITY_AUDIT.md) |
| Top sources: BPHS, KP Reader 3, Sarvartha Chintamani, Bhrigu Samhita, Phaladeepika, Jaimini Sutras, Lal Kitab Original, Jataka Parijata, Raman variants | Same audit |
| Query API: planet�house, dasha lord, nakshatra, yoga text | `engine/corpus.py` |
| **Caveat:** OCR/LLM extraction � not verbatim press editions; ~44% Bhrigu extraction complete per workflow doc | [CORPUS_QUALITY_AUDIT.md](./CORPUS_QUALITY_AUDIT.md), [ASTROLOGER_CLIENT_WORKFLOW.md](./ASTROLOGER_CLIENT_WORKFLOW.md) |

**What DIY book reading does NOT do:** Cross-index 41 texts for **one** placement in seconds. **What we still do wrong:** Serve citations without lagna filter ? can sound like a book **and** be the wrong book paragraph.

### 2.4 Internal QA: 82.7% loose / 75.6% strict (16 celebrities)

| Metric | Value | Definition |
|--------|-------|------------|
| Loose hit rate | **82.7%** (105/127 events) | Predicted band within **�180 days** of known event |
| Strict hit rate | **75.6%** (96/127) | �45 days **and** valence match when event is clearly good/bad |
| Subjects | 16 celebrities with `known_events` in chart JSON | `runtime/_accuracy_scorer.py`, [BACKEND_FOCUS.md](./BACKEND_FOCUS.md) |
| Manoj | **No score** � `manoj_chart.json` has no `known_events` | Cannot calibrate or claim verified accuracy for private clients |

This is **internal regression QA**, not a client guarantee. Weak spots remain (e.g. Mukesh strict 37.5%, Gandhi loose 56%).

### 2.5 Orchestrator: 77 modules vs single technique

| Fact | Source |
|------|--------|
| `full_analysis(chart)` runs **77/77 modules OK** on Manoj integration test (~18s) | `runtime/engine_orchestrator.py`, [INTEGRATION_TEST_RESULTS.md](./INTEGRATION_TEST_RESULTS.md) |
| Includes: granular dasha, char/yogini/ashtottari, 16+ vargas, shadbala, ashtakavarga, Jaimini, KP summary, sade sati, muhurta, nadi, longevity, sibling/spouse inference, **both** `event_predictor_v2` and declarative category engine | Module list in orchestrator |
| **Gap:** Manoj PDF speaks **one** module family (life-event bands + template dasha). The other 75 modules are **computed but not narrated**. |

### 2.6 Four-engine comparison (books vs match vs hybrid vs life-event)

Regenerate: `python scratch/_manoj_engine_comparison.py`  
Output: `reports/jun 2026/2026-06-02/report/manoj/MANOJ_ENGINE_COMPARISON.md`

| Engine | What it does | Manoj example |
|--------|--------------|---------------|
| **Pure books** | Verbatim corpus pull for planet-in-house / nakshatra | Jupiter H1, Venus H7 passages from BPHS, Lal Kitab, etc. |
| **Pure match** | `consensus_percent` = **agreement index** among those passages � **not** event probability | `engine/comparative_test.synthesize_consensus` |
| **Hybrid** | Declarative categories + classical cross-check within �180 days | `engine_pure_hybrid.hybrid_engine_instance` |
| **Life-event (production)** | Scored dasha+transit+yoga windows | `event_predictor_v2` bands in `MANOJ_PREDICTIONS_TA.md` |

**Agreement column** in comparison report is often �Partial� or �Sparse� � engines **diverge**, as real astrologers would. We rarely **explain** that divergence to the client.

### 2.7 What competitors / apps typically do NOT do

| Capability | Us | Typical market |
|------------|-----|----------------|
| 197+ life-event scorers with native house lords | Yes | 5�20 event types or yearly prose |
| Multi-book corpus index (15.6k) | Yes (with lagna-filter gap) | Single-text templates or no citations |
| Strict valence-aware backtest loop | Yes (celebrities) | None public |
| 77-module batch on one chart | Yes | Single dasha + transit |
| Honest �mechanical / cited / synthesis� policy | Documented ([ENGINE_TRUTH_POLICY.md](./ENGINE_TRUTH_POLICY.md)) | Often presented as certainty |
| Linked family charts (spouse/child JSON ripple) | **No** | Rare everywhere |
| Human synthesis + conflict reconciliation | **No** (partial templates) | Human astrologer only |

---

## 3. What readers get from books that we still DON�T automate

A skilled reader with Lal Kitab + BPHS still delivers these **better than our current PDF**:

| Book / human capability | Why it feels deeper | Our gap |
|-------------------------|---------------------|---------|
| **Chart synthesis story** | �You are Sagittarius rising, Jupiter in 1st anchors identity, but Saturn-Ketu in 4th pulls home life� � one coherent paragraph | No `chart_profile` object passed to PDF; dasha chapters use planet templates |
| **Bhava-by-bhava life reading** | 12 houses walked in order with occupants, lords, aspects | `generate_report.py` has 23 domains, not strict 12-bhava Tamil narrative |
| **Conflict reconciliation** | �BPHS promises marriage early; KP 7th cusp SL denies until 2028� ? mixed indication | Modules exist separately; no `multi_source_synthesis.py` |
| **Linked family charts** | Child born ? native�s 5+7+11 together; spouse chart vice versa | Derived-house rules in patterns only; no linked JSON |
| **Remedies with conditions** | Gem/mantra only when lord weak **and** dasha supports | Scattered modules; no conditional remedy block in Manoj PDF |
| **Intuition / client context** | Questions, tone, what **not** to say | Not automatable; should be disclosed as limit |
| **Divisional deep dive per question** | D9 for marriage quality, D10 for career **before** dates | Vargas computed in orchestrator; Manoj Tamil path mostly D1 |
| **Both lenses on same period** | Ketu MD: spiritual gain **and** detachment stress, tied to 4H | Valence partial; bands often single-label |
| **Calibration feedback loop** | �You married 2023 � tighten time� | No `known_events` on private charts |

**Honest line for Manoj:** The engine knows **when** mechanical signals stack for **your** lagna; it does not yet tell **who you are** the way a senior astrologer would **before** opening the timing chapter.

---

## 4. P0 product roadmap � what would make Manoj�s report NON-basic

Each item: **concrete behavior**, **extend this file**.

| # | Feature | Client-visible outcome | Extend |
|---|---------|------------------------|--------|
| **P0-1** | **`chart_profile` narrative before timing** | 1�2 page �who you are�: lagna lord, Moon, lords table, top 3 yogas, strength summary, **then** date tables | Build once in `scan_lifetime_v2` or `engine_orchestrator.full_analysis`; consume in `scratch/_manoj_tamil_predictions_report.py`, `runtime/generate_report.py`, `runtime/generate_tamil_pdf.py` |
| **P0-2** | **Lagna-applicable corpus lines only** | No Scorpio-lagna quote on Sagittarius chart; tag universal vs ascendant-specific | `engine/corpus.py` � filter `get_planet_in_house` / `get_planet_in_sign` by `chart["lagna"]` and rule metadata |
| **P0-3** | **`multi_source_synthesis` confidence per topic** | �Marriage: Parashari strong, KP mixed, Jaimini agrees ? **confidence 72%**� with disagreement notes | **New** `engine/multi_source_synthesis.py` consuming `jaimini_full`, `kp_paddhati`, `corpus`, `event_predictor_v2`, `comparative_test` |
| **P0-4** | **Cross-house bundles** | Childbirth block cites **5+7+9+11** together, one narrative | Add `house_links: list[int]` on every `event_*` return; bundle renderer in report generators; spec in [PREDICTION_METHODOLOGY.md �9](./PREDICTION_METHODOLOGY.md) |
| **P0-5** | **Positive AND negative paired for same dasha period** | �Moon�Rahu AD: career visibility (+) **and** emotional volatility (?)� same date band | Extend `engine/event_valence.py`; dual-lens paragraph template in `engine/synthesis.py` |
| **P0-6** | **`known_events` calibration for client** | Manoj supplies marriage/job dates ? scorer tightens windows, report shows before/after | `charts/manoj_chart.json` schema + `runtime/_accuracy_scorer.py` + `runtime/chart_rectification.py` |
| **P0-7** | **Verse-level citations with book + page** | �Phaladeepika Ch.13 � verse_id � � p. 214� under each major claim | `CorpusRule.verse_ids`, extraction metadata in `gemma_extractions/`; PDF footnote layer in `generate_report.py` |
| **P0-8** | **Strict dated windows with peak month inside band** | �2028-01-15 ? 2031-12-31, **peak: Aug 2029** (Jupiter exact on 7L)� | Peak detection inside `collapse_consecutive` / finer `sample_days` in `scan_year_v2`; optional KP sub-lord narrowing via `runtime/kp_paddhati.py` |

**Recommended build order for Manoj v2 deliverable:** P0-1 ? P0-2 ? P0-8 ? P0-5 ? P0-3 (narrative foundation, then trust, then precision, then depth).

---

## 5. Elevator answer for Manoj � why use this engine vs reading Lal Kitab yourself

If you read Lal Kitab cover to cover, you will learn **general rules** � Jupiter in the first house, Venus periods for marriage, Ketu�s detachment. Those apply to **millions** of charts. They do not, by themselves, tell you **which months** **your** seventh lord (Mercury, not a generic Venus) activates **your** tenth-house Rahu career arc, backed by **15,000+ cross-book lines** indexed to **your** 1996 Coimbatore birth time, scored against **127 real celebrity life events** at 75%+ strict accuracy internally. This engine is a **mechanical clock + multi-book index** for **one chart**; it is not a replacement for a guru�s synthesis � yet � but it **does** compute and rank dated windows and cause chains no human reader holds in working memory. Your PDF felt basic because we showed you **the same words as the book** without first showing **your chart�s unique setup** and **why these dates follow from it** � that is a product gap we are closing, not proof the engine is only sun-sign fluff.

---

## 6. Optional next deliverable � `MANOJ_DEEP_NARRATIVE_TA.md`

**Purpose:** Prototype **astrologer-style 12-house chapter** in Tamil (structure only; full generation is a separate sprint).

**Suggested outline:**

1. **Cover + birth verification** � time source disclaimer; lagna sensitivity note  
2. **?????????? 0 � ????????? (Executive synthesis)** � 3 paragraphs from `chart_profile` (P0-1)  
3. **?????????? 1 � ??? ?? ?????? (1st)** � Jupiter H1, lagna lord dignity, Shadbala snippet  
4. **?????????? 2 � ??????? / ?????? (2nd)** � 2L Saturn placement, dhana yoga yes/no  
5. **?????????? 3 � ????? / ??????? (3rd)** � siblings theme  
6. **?????????? 4 � ???? / ???? (4th)** � Saturn+Ketu H4, both lenses  
7. **?????????? 5 � ??????? / ????? (5th)** � Mars+Mercury H5  
8. **?????????? 6 � ????? / ?????????? (6th)** � Sun H6, preventive framing  
9. **?????????? 7 � ?????? / ???? (7th)** � Venus H7, D9 note, **then** top 3 marriage bands  
10. **?????????? 8 � ????? / ????? (8th)** � caution language per ethics policy  
11. **?????????? 9 � ????? / ??????? (9th)** � Moon H9, Sun as 9L in H6  
12. **?????????? 10 � ?????? (10th)** � Rahu H10, D10 dasha note, career bands  
13. **?????????? 11 � ??? / ?????? (11th)** � gains theme  
14. **?????????? 12 � ???????? / ??????? (12th)** � foreign/spiritual  
15. **?????????? 13 � ???????? ??? ???** � Moon�Rahu with paired +/- (P0-5)  
16. **?????????? 14 � ??? ??????? ??????** � ranked windows only **after** houses 1�12  
17. **?????????? 15 � ?Classic footnotes** � lagna-filtered corpus (P0-2), verse IDs (P0-7)  
18. **Closing** � limits, invite `known_events` for calibration (P0-6)

**Generator stub (future):** `scratch/_manoj_deep_narrative_ta.py` reading `chart_profile` + orchestrator JSON + filtered corpus.

---

## References (repo)

| File | Role |
|------|------|
| `runtime/event_predictor_v2.py` | Production life-event bands |
| `runtime/generate_tamil_pdf.py` | Original Tamil booklet (template dasha) |
| `scratch/_manoj_tamil_predictions_report.py` | Tamil band tables |
| `scratch/_manoj_engine_comparison.py` | Four-engine comparison |
| `runtime/engine_orchestrator.py` | 77-module batch |
| `engine/corpus.py` | Multi-book index |
| `runtime/_accuracy_scorer.py` | Celebrity QA |
| `engine/synthesis.py` | High-level API summary (needs deepening) |
| `engine/truth_policy.py` | mechanical / cited / synthesis tags |
| `charts/manoj_chart.json` | Manoj fixture |

---

*This document is intentionally non-marketing. If a sentence cannot be traced to a file or measured metric, it should not appear in client-facing copy.*
