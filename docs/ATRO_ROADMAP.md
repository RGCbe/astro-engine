# ATRO — Path to World-Class Vedic Astrology Engine

**Goal**: surpass Jhora, Parashara's Light, Kala, AstroSage, and individual master astrologers. Become the most rigorous, complete, and predictively accurate Vedic engine ever built.

**Standard**: a senior Jyotish scholar (BV Raman / KN Rao calibre) cannot find a meaningful gap or error in our reading.

---

## Where Atro stands today (Apr 25, 2026)

| Component | Status |
|---|---|
| Books extracted | 23 (regex layer 100%, Gemma layer 12/23 — 11 retrying) |
| Rules catalogued | 13,770 (regex) |
| Compute parity | ✅ 3 ephemeris engines agree to 0.011° |
| Compute layers | 30 (positions, vargas, ashtakavarga, shadbala partial, sphutas, narayana/yogini dasha, sahams) |
| Interpretation engines | 7 (match→reading→combinations→timeline→dna→ultimate→phd→integrated) |
| Cross-check verifier | ✅ built today |
| Test charts | 1 (Manoj — synthetic, no event-history validation) |
| Public benchmark | ❌ none |

**Honest assessment**: we have a strong skeleton. We do NOT yet have:
- Empirical validation against famous charts with known outcomes
- Full coverage of all 11 dasha systems (only Vimshottari + Narayana + Yogini are coded)
- Regional/Tantric traditions (KP, Lal Kitab, Tamil, Kerala Prashna, Tajik annual)
- Scholar disagreement reconciliation rules
- Confidence-tagged predictions
- Synastry / Kuta matching for marriage compatibility
- Prashna (horary) engine
- Muhurta (auspicious timing) engine
- Multi-language output (Sanskrit/Hindi/Tamil)
- Self-correcting feedback loop from real-world outcomes

To be **best in the world**, we need to close every gap above and pass empirical benchmarks.

---

## The Five-Phase Roadmap

### **PHASE I — Corpus Completeness** (the floor)

**Goal**: 50-book corpus, every major school of Jyotish.

#### 1.1 Finish current 23-book extraction
- ✅ Regex layer complete
- 🟡 Gemma retry running (11 books) — finishing today

#### 1.2 Add 27 more flagship books to reach 50-book corpus

| School | Book | Status |
|---|---|---|
| Parashari core | BPHS Vol 3 (R Santhanam) | ❌ |
| Parashari core | Brihat Parashara Hora Shastra (Sharma trans) | ❌ |
| Parashari extended | Vaidyanatha Dikshita — Jataka Parijata (full 8 vols) | partial |
| Phaladeepika family | Mantreswara — Phaladeepika commentary by Vasanthi | ❌ |
| Sara family | Prithuyasas — Hora Sara | partial |
| Jaimini | Jaimini Sutras with Krishnamurti commentary | ❌ |
| Jaimini | Jaimini Upadesa Sutras (Sanjay Rath) | ❌ |
| KP system | Krishnamurti Padhdhati Vol 1-5 | ❌ |
| Lal Kitab | Lal Kitab — original Urdu + Hindi | ❌ |
| Tajik / annual | Tajika Sara | ❌ |
| Tajik / annual | Tajika Neelakanthi | ❌ |
| Bhrigu | Bhrigu Samhita full pages (current is ~800/2000 pages) | partial |
| Bhrigu | Bhrigu Sutras | ❌ |
| Bhrigu | Naadi: Vakya / Devakeralam / Chandra Kala Naadi | ❌ |
| Tamil tradition | Saravali Tamil edition | ❌ |
| Tamil tradition | Tamil Jataka Parijata | ❌ |
| Kerala tradition | Prashna Marga full + Mahaprashna | partial |
| Kerala tradition | Krishneeyam | ❌ |
| Modern Indian | BV Raman — How to Judge a Horoscope V1+V2 | ❌ |
| Modern Indian | BV Raman — 300 Important Combinations | ❌ |
| Modern Indian | KN Rao — Predicting through Jaimini's Chara Dasha | ❌ |
| Modern Indian | KN Rao — Yogis, Destiny and Wheel of Time | ❌ |
| Modern Indian | Sanjay Rath — Crux of Vedic Astrology | ❌ |
| Modern Indian | Sanjay Rath — Vimshottari and Yogini Dashas | ❌ |
| Western Vedic | David Frawley — Astrology of the Seers | ❌ |
| Western Vedic | Hart de Fouw — Light on Life | ❌ |
| Mathematical | Surya Siddhanta full English commentary (Burgess) | partial |
| Computation | Pancha Siddhantika full + commentary | partial |

**Target**: 50 books × Gemma extraction × multi-pass cross-validation = ~30,000 rules.

**Deliverable**: `F:/Atro/gemma_extractions/` with 50 JSON files, each ≥30KB.

---

### **PHASE II — Technique Completeness** (the engine ceiling)

**Goal**: every technique mentioned across all 50 books is **natively computed**, not just rule-matched. The engine should compute results, then compare to book rules — not just look up rules.

#### 2.1 All 11 Dasha systems (currently 3/11)

| Dasha | Status | Source |
|---|---|---|
| Vimshottari | ✅ done | BPHS Ch.46 |
| Ashtottari | ❌ | BPHS Ch.47 + Laghu Parashari |
| Yogini | ✅ done | BPHS Ch.50 |
| Kalachakra | ❌ | BPHS Ch.49 — most complex |
| Chara (Jaimini) | ❌ | Jaimini Sutras |
| Sthira (Jaimini) | ❌ | Jaimini Sutras |
| Kendra (Jaimini) | ❌ | Jaimini Sutras |
| Karaka (Jaimini) | ❌ | Jaimini Sutras |
| Shoola | ❌ | BPHS Ch.50 |
| Narayana | ✅ done | Jaimini |
| Dwadasottari | ❌ | BPHS Ch.47 |
| Shatabdika | ❌ | BPHS Ch.47 |
| Panchottari | ❌ | BPHS Ch.47 |
| Shashtihayani | ❌ | BPHS Ch.47 |

#### 2.2 All 15 Vargas (currently D1, D9, D10 fully)

D2/D3/D4/D7/D12/D16/D20/D24/D27/D30/D40/D45/D60 — all need:
- Computation
- Per-divisional house system
- Per-divisional aspect interpretation
- Vargottama detection (planet in same sign across vargas)
- Karaka role (D60 = past life, D9 = spouse, D10 = career, D24 = education, etc.)

#### 2.3 All 11 Balas (Strengths)

| Bala | Status |
|---|---|
| Sthana Bala (positional) | partial |
| Dig Bala (directional) | ✅ |
| Kala Bala (temporal) | ❌ |
| Cheshta Bala (motional) | ❌ |
| Naisargika Bala (natural) | ✅ |
| Drik Bala (aspectual) | ❌ |
| Bhava Bala (house) | partial |
| Ishta/Kashta Phala | partial |
| Harsha Bala (joy) | ❌ |
| Shad Bala (sum) | needs aggregation |
| Saptavarga Bala | ❌ |

#### 2.4 Ashtakavarga full system

- Bhinna Ashtakavarga (each planet's contribution per house) — partial
- Sarva Ashtakavarga (total) — partial
- Kaksha Vibhaga (zone analysis) — ❌
- Shodhana (purification: trikona + ekadhipatya) — ❌
- Phala (point-based fruit prediction) — ❌

#### 2.5 Specialized engines (currently absent)

- **Prashna engine** (horary chart for question-asking) — needs question-time chart compute + Krishneeyam rules
- **Muhurta engine** (auspicious timing) — Muhurtha Chintamani + Lagna Shuddhi rules
- **Synastry / Kuta matching** — 36-guna Ashta-Kuta + Mangal-dosha + Nadi-dosha + KP-style compatibility
- **Tajik / annual horoscope** — Varshaphala, Muntha, 16 Tajik yogas, Sahams
- **Sudarshan Chakra** — three-chart synthesis (Lagna + Sun + Moon as ascendants)
- **KP system** — sub-lord theory, ruling-planets, significators

#### 2.6 Lal Kitab integration

- Different house numbering (12 = enemies, 8 = death — opposite of Parashari!)
- Karmic debts (Pitru-rin, Matru-rin)
- Specific remedies system (artha-prada, dasha-pravesha)
- Need separate logic path — Lal Kitab is incompatible with Parashari aspects

---

### **PHASE III — Verification & Validation** (the credibility layer)

**Goal**: prove the engine is right by testing against charts where outcomes are documented.

#### 3.1 Famous-charts library

Build `F:/Atro/known_charts/` with 100+ charts including life events.

| Tier | Subjects | Why |
|---|---|---|
| Tier 1 — Indian luminaries | Mahatma Gandhi, Indira Gandhi, Modi, Vajpayee, Ratan Tata, Dhirubhai Ambani, Shah Rukh Khan, Sachin Tendulkar, Lata Mangeshkar, Ramana Maharshi, Aurobindo | Birth data verified, life events public |
| Tier 2 — World figures | Einstein, Hitler, JFK, Obama, Putin, Xi, Steve Jobs, Bill Gates, Trump, Elon Musk | Western birth data needs verification |
| Tier 3 — Astrologers' published readings | BV Raman's 300 Combinations charts, KN Rao case studies | Already analyzed by masters |
| Tier 4 — Tragic markers | Charts of those with documented early death, accident, prison, scandal | Test maraka prediction |
| Tier 5 — Success markers | Self-made billionaires, Nobel laureates, Olympic gold | Test raja-yoga prediction |

Each chart annotated with:
- Birth data (verified) + rectified time if needed
- Major life events (year + event type)
- Health milestones
- Career arc
- Marriage/family
- Death (if applicable, exact date and cause)

#### 3.2 Predictive backtest

```
For each known-chart C:
  For each major life event E at age A in C's history:
    Run engine at "C's birth" → predict events in age A window
    Compare predicted events to E
    Score: hit / miss / partial / wrong-direction
```

**Metrics**:
- Career-theme accuracy: did engine predict tech/politics/arts/business?
- Marriage timing: predicted window vs actual ± 2 yrs
- Major life events: count of correctly-predicted events / total events
- False positives: predicted events that didn't happen
- Calibration: when engine says "high confidence," is it actually right more often?

#### 3.3 Scholar agreement test

Compare engine output to BV Raman's published readings of the same chart. Score line-by-line agreement.

**Pass bar**: ≥80% agreement with published master readings.

---

### **PHASE IV — Intelligence Layer** (the differentiator)

**Goal**: from "rule-matcher" to "reasoning engine."

#### 4.1 Disagreement reconciliation rules

When books disagree, encode authority hierarchy:

```
Authority order for Parashari Jyotish:
  1. Brihat Parashara Hora Shastra (Parashara's own words — supreme)
  2. Phaladeepika (Mantreswara, 14th c. — most-cited)
  3. Saravali (Kalyana Varma — comprehensive)
  4. Hora Sara (Prithuyasas)
  5. Jataka Parijata (Vaidyanatha Dikshita)
  6. Brihat Jataka (Varahamihira — concise)
  7. Yavanajataka (Sphujidhvaja — Greek-influenced)

Authority order for Jaimini:
  1. Jaimini Sutras
  2. Sanjay Rath commentary
  3. KN Rao methodology

If BPHS says X and Phaladeepika says Y → BPHS wins, but flag both.
If 5 books say X and 1 says Y → 5-side wins.
If only 1 book has the rule → ANECDOTAL flag in confidence.
```

#### 4.2 Modern ML layer

**Embedding-based semantic search across 50-book corpus**:
- Embed every rule with `sentence-transformers/all-mpnet-base-v2` or similar
- Index in FAISS or Chroma
- Query: "What is the result of Mars-Saturn conjunction in 7th house for Sagittarius lagna?"
- Returns: 30 most-similar rules across all books with citations

**Synthesis with structured reasoning**:
- For any prediction, GPT/Gemini receives:
  - Chart facts
  - Top 30 semantically-relevant rules with book citations
  - Authority weights
  - Disagreement flags
- Produces reading with embedded citations: `"Mars in H5 (Mars in own sign Aries) brings creative-aggressive intelligence [BPHS Ch.27.45][Saravali V.3.12][Phaladeepika Ch.4.7]"`

#### 4.3 Probabilistic prediction

Every prediction tagged:
```json
{
  "event": "Marriage in primary window 2029-2030",
  "confidence": 0.72,
  "supporting_techniques": [
    "Vimshottari Moon-Mercury antar (Mercury rules H7)",
    "Muntha entering Gemini H7 in Jun 2026",
    "Venus karaka activated in 2029 transit",
    "D9 lagna lord Venus dasha period"
  ],
  "dissenting_views": [
    "Some scholars (Phaladeepika Ch.7) flag Mercury in H5 as marriage delay",
    "Saturn aspect on H7 lord adds friction"
  ],
  "calibration_notes": "70% of similar combinations in known-charts library resulted in marriage in this window"
}
```

#### 4.4 Multi-modal output

- Text in 4 languages (English / Hindi Devanagari / Sanskrit IAST / Tamil)
- Visual chart renders (D1, D9, D10, D60 — North Indian + South Indian + East Indian styles)
- Timeline visualization (dasha periods + transit triggers + life events)
- Audio narration (Indian English / Hindi accent)

---

### **PHASE V — Public Benchmark & Release**

**Goal**: undeniable proof of being best in the world.

#### 5.1 Build `astrobench` — a public benchmark

- **1000 known charts** with documented outcomes
- **20 prediction categories**: career field, marriage timing, health crises, major financial events, family events, spiritual events, etc.
- **Closed test set** to prevent training-data leakage

#### 5.2 Public leaderboard

Run engine against the benchmark. Compare to:
- Jhora 8.0 (free, mature)
- Parashara's Light 9.0 (paid, comprehensive)
- AstroSage premium (commercial, mass-market)
- KP Astrologer (commercial)
- ChatGPT/Claude with raw RAG over books (LLM baseline)

**Targets**:
- ≥70% accuracy on career-theme prediction
- ≥60% accuracy on marriage-window timing (±18mo)
- ≥80% scholar agreement on canonical chart features
- Well-calibrated confidence (Brier score < 0.20)

#### 5.3 Productization decisions

| Layer | Open or Closed |
|---|---|
| Compute layer | Open (jyotishganit-style) |
| Rule corpus (extracted) | Closed (legal/copyright) |
| Embeddings + search | Closed (proprietary index) |
| API | Tiered: free / pro / enterprise |
| Consumer app | Mobile + Telegram bot |
| B2B | API for astrologer practices |

---

## Sequence & Dependencies

```
PHASE I (corpus) ───┐
                    ├──▶ PHASE II (techniques) ───▶ PHASE III (validation) ──▶ PHASE IV (intelligence) ──▶ PHASE V (benchmark)
PHASE I depends on Gemma retry finishing today
PHASE II depends on I's rules
PHASE III depends on II being functional
PHASE IV runs in parallel with III (embeddings can be built immediately)
PHASE V is the proof
```

**Realistic time-to-world-class**: 4-6 months of focused work, tracked weekly.

---

## Immediate Next Steps (this week)

| # | Task | Blocker | Output |
|---|---|---|---|
| 1 | Finish Gemma retry on 11 books | Running now | All 23 books complete |
| 2 | Procure 27 missing flagship books (PDFs) | None | `Books/` has 50 PDFs |
| 3 | Build `_known_charts.py` seed library — 20 famous charts | Need birth data | `known_charts/*.json` |
| 4 | Implement Kalachakra dasha (most complex missing) | BPHS Ch.49 needed | `dasha_kalachakra.py` |
| 5 | Build embedding index over current 23 books | Run `text-embedding-3-large` or local | `corpus_embeddings.faiss` |
| 6 | Disagreement rules — encode authority hierarchy | Read 4-5 commentary chapters | `authority_hierarchy.json` |

---

## Decision points the user needs to make

1. **Open source or proprietary?** Affects book licensing, embedding choice, monetization.
2. **Languages prioritization?** English-only (faster to ship) vs full Sanskrit/Hindi/Tamil (true world-class).
3. **Lal Kitab integration?** Separate engine path because it's incompatible with Parashari. Worth the complexity?
4. **KP system separate?** Either deep-integrate (rebuilt sub-lord layer) or keep as add-on.
5. **Benchmark publication?** Going public with `astrobench` invites scrutiny but cements credibility.
6. **Funding model?** Solo project, hire researchers, or open-source community?

---

## What "best in the world" means concretely

Atro is best-in-world when:
1. It scores higher than every public competitor on `astrobench`
2. A senior Jyotish scholar (BV Raman successor / KN Rao successor) reviews 10 readings and finds zero meaningful errors
3. It surfaces canonical rule-confluence that no individual scholar can hold in memory (50-book span)
4. It predicts correctly across decades for ≥70% of major life events on known-charts
5. It admits uncertainty calibratedly (says "low confidence" when actually wrong, "high confidence" when actually right)
6. It explains every prediction with structured citations to verses
7. It handles all 113 techniques + Lal Kitab + KP + Tajik + Prashna + Muhurta + Synastry as first-class
