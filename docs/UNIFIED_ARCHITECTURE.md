# Atro Vedic Engine — Unified Architecture

**Build:** 2026-05-06 | **Engine version:** unified-v15.0

> **See also:** [MODULE_INDEX.md](../runtime/MODULE_INDEX.md) (every module catalogued) · [API_REFERENCE.md](API_REFERENCE.md) (every public function) · [USER_GUIDE.md](USER_GUIDE.md) (end-user manual)

---

## High-Level Diagram

```
                   ┌────────────────────────────────────────────────────┐
                   │                      USER LAYER                     │
                   │ ─────────────────────────────────────────────────── │
                   │  CLI                FastAPI               Frontend  │
                   │  atro_cli.py        main.py               (Vue/HTML)│
                   │  9 modes            POST /api/jathagam               │
                   └────────────┬─────────────┬─────────────┬────────────┘
                                │             │             │
                ┌───────────────┴─────────────┴─────────────┴────┐
                │           UNIFIED ORCHESTRATOR                  │
                │           engine_unified.py                     │
                │           ─────────────────                     │
                │  unified_analysis(chart, when, modes)           │
                │  quick_summary(chart, when)                     │
                │  Combines BOTH engines into one result dict     │
                └─────────────┬──────────────────┬────────────────┘
                              │                  │
        ┌─────────────────────▼──────┐    ┌──────▼───────────────────────┐
        │       runtime/              │    │           engine/             │
        │       61 modules            │    │           84 modules          │
        │  ─────────────────────      │    │  ────────────────────────    │
        │  engine_orchestrator.py     │    │  cli.py / web.py             │
        │   (single entry; 50+        │    │  reading.py (full reading)   │
        │    prediction systems)      │    │  client_report.py            │
        │                             │    │  client_report_ta.py (Tamil) │
        │  • Yogas (45+)              │    │  • Affliction backtest        │
        │  • Dashas (Vimshottari/     │    │  • Blessing backtest          │
        │     Ashtottari/Yogini/Char) │    │  • Cross-validation           │
        │  • Shadbala / Ashtakavarga  │    │  • Severity refit (empirical) │
        │  • Aspects / Conjunctions   │    │  • Tier refit                 │
        │  • Sade Sati / Transits    │    │  • Calibration / Brier scores │
        │  • Event predictor (13)     │    │  • Bhrigu engine root         │
        │  • Spouse / Sibling / KP    │    │  • Bhrigu predictions         │
        │  • Jaimini / Argala         │    │  • Lal Kitab full             │
        │  • Lal Kitab / Nadi /       │    │  • Tajik annual chart         │
        │     Numerology / Medical    │    │  • Kalachakra dasha           │
        │  • Sahams / Upagrahas       │    │  • Raasi dasha (Chara/Sthira) │
        │  • Special lagnas / Doshas  │    │  • Muhurta / Prashna          │
        │  • Varshaphala (Tajik)      │    │  • Yogas extended (50+)       │
        │  • Eclipses / Compatibility │    │  • Yogas Nabhasa (32)         │
        │  • Tier-1 multi-tradition:  │    │  • Chart render (SVG N/S)     │
        │    Palmistry, Vastu,        │    │  • PDF render                 │
        │    Face reading, Moles,     │    │  • Multi-language i18n        │
        │    Omens (Shakuna)          │    │  • Tamil chapters/narrative   │
        └────────┬────────────────────┘    └──────────┬───────────────────┘
                 │                                     │
                 │    ┌────────────────────────────────┘
                 │    │
                 │    │  BRIDGE LAYER (engine/ → runtime/)
                 │    ▼  ─────────────────────────────────
                 │   engine/dasha.py     ──imports──▶  runtime/granular_dasha.py
                 │   engine/vargas.py    ──imports──▶  runtime/divisional_charts.py + extra_vargas.py
                 │   engine/kp_sublord.py──imports──▶  runtime/kp_paddhati.py
                 │   engine/panchanga.py ──imports──▶  runtime/panchanga.py
                 │
                 ▼
        ┌──────────────────────────────────────────────────────┐
        │             BOOK CORPUS LAYER                          │
        │  ──────────────────────────────────────────           │
        │  runtime/book_corpus_indexer.py                       │
        │     → book_corpus_index.json                          │
        │     → 11,692 passages, 72 topics, 38 books            │
        │  runtime/book_citation.py — quality-filtered queries  │
        │  runtime/corpus_upgrade.py — re-extraction utils      │
        │                                                        │
        │  engine/corpus.py + gemma_extractions/                │
        │     → 16,126 deduplicated rules from 19 LLM-extracted │
        │       book digests                                     │
        │  engine/book_rules.py — structured per-chart matcher  │
        │  engine/deep_rules.py — deep semantic matcher         │
        │  engine/verse_locator.py — citation API               │
        │  engine/bhrigu_predictions.py — Bhrigu Samhita        │
        │  engine/kp_predictions.py — KP-specific predictions   │
        │  engine/muhurta_verbatim.py — verbatim muhurta rules  │
        │  engine/remedies_verbatim.py — verbatim remedies      │
        └──────────────────────────────────────────────────────┘
```

---

## Data Flow — Chart Input to Output

### 1. Chart Input

A chart is a JSON dict with:
- `birth`: {year, month, day, hour, min, lat, lon, place}
- `lagna`, `lagna_idx`, `lagna_lord`, `ayanamsa`
- `positions`: dict with 9 grahas (Sun…Ketu), each carrying {rasi, rasi_idx, house, degree, nakshatra}
- `moon_rasi`, `janma_nakshatra`, `janma_nakshatra_lord`

The chart can be created by:
1. Hand-writing the JSON (place values calculated externally)
2. Calling `engine.chart.compute_chart(birth_data)` (uses Swiss Ephemeris under the hood)
3. Calling `main.py POST /api/jathagam` (computes from {year, month, day, time, lat, lon})
4. Importing one of the demo `compute_*.py` scripts in `runtime/`

### 2. Orchestration Path

```
chart dict
  │
  ▼
engine_unified.unified_analysis(chart)            ← Top-level entry
  │
  ├──▶ runtime.engine_orchestrator.full_analysis()  ← Runs 50+ runtime modules
  │      │
  │      ├──▶ granular_dasha.build_full_timeline()  (4-level Vimshottari)
  │      ├──▶ comprehensive_yogas.detect_all_classical_yogas()
  │      ├──▶ yoga_library_v2.detect_extra_yogas()
  │      ├──▶ shadbala.compute_shadbala()
  │      ├──▶ shadbala_full.compute_shadbala_full()  (Tier 5)
  │      ├──▶ ashtakavarga.compute_bhinna_ashtakavarga()
  │      ├──▶ ashtakavarga.compute_sarvashtakavarga()
  │      ├──▶ aspects_engine.detect_significant_aspects()
  │      ├──▶ conjunction_effects.detect_conjunctions()
  │      ├──▶ sade_sati.compute_sade_sati_periods()
  │      ├──▶ transit_engine.detect_triggers()
  │      ├──▶ event_predictor_v2.scan_lifetime_v2()
  │      ├──▶ sibling_predictor.predict_siblings()
  │      ├──▶ spouse_inference.infer_spouse()
  │      ├──▶ jaimini_full.jaimini_summary()
  │      ├──▶ argala_jaimini.compute_argala()
  │      ├──▶ kp_paddhati.kp_summary()
  │      ├──▶ longevity_ayurdaya.longevity_analysis()
  │      ├──▶ panchanga.compute_panchanga()  (today's panchanga)
  │      ├──▶ muhurta_engine.muhurta_check()
  │      ├──▶ special_lagnas.all_special_lagnas()
  │      ├──▶ upagrahas.compute_upagrahas()
  │      ├──▶ dosha_cancellations.all_doshas_summary()
  │      ├──▶ varshaphala.varshaphala_timeline()  (5-yr annual chart)
  │      ├──▶ sahams.compute_sahams()
  │      ├──▶ eclipse_impact.upcoming_eclipses_impact()
  │      ├──▶ medical_astrology.medical_analysis()
  │      ├──▶ numerology_vedic.vedic_numerology()
  │      ├──▶ lal_kitab.lal_kitab_summary()
  │      ├──▶ nadi_jyotish.nadi_analysis()
  │      ├──▶ transit_forecast.forecast_period(30 days)
  │      ├──▶ tara_chakra.tara_chakra_summary()
  │      ├──▶ tri_pataki_chakra.tri_pataki()
  │      ├──▶ varshaphala_dashas.annual_dashas_summary()
  │      ├──▶ palmistry_engine.palmistry_summary()       (Tier 1)
  │      ├──▶ vastu_shastra.vastu_summary()              (Tier 1)
  │      ├──▶ face_reading.face_reading_summary()        (Tier 1)
  │      ├──▶ body_moles.mole_summary()                  (Tier 1)
  │      ├──▶ omens_shakuna.omens_summary()              (Tier 1)
  │      ├──▶ present_moment.present_moment_reading()
  │      └──▶ book_citation.citation_for(topic)  × 9 topics
  │
  ├──▶ engine.corpus.get_corpus()                  ← 16,126 rules
  ├──▶ engine.vargas.all_vargas(chart)              ← All 16 divisional charts
  ├──▶ engine.dasha.vimshottari/current/etc.        ← 5 dasha systems
  ├──▶ engine.yogas.detect_all(chart)               ← engine-side yoga aggregator
  └──▶ engine.kp_sublord.get_kp_chart(chart)        ← KP cuspal layer

  │
  ▼
result dict (~50 module entries, each with status + data)
```

### 3. Output Surfaces

| Output | Path | Format |
|---|---|---|
| Console summary | `atro_cli.py --mode summary` | Plain text, ~30 lines |
| JSON dump | `atro_cli.py --mode json` | Full result dict |
| PDF report | `atro_cli.py --mode pdf` (or `generate_report.generate()`) | ~55-page PDF, 977 elements, ReportLab |
| HTTP JSON | `POST /api/jathagam` | FastAPI response with all 8 phases (chart, dashas, houses, yogas, shadbala, ashtakavarga, gochar, KP) |
| Markdown reports | `engine.client_report_v2.generate_client_report_v2()` | Multi-section narrative |
| Tamil reports | `engine.client_report_v2_ta.generate_client_report_v2_ta()` | Tamil-language version |
| SVG chart | `engine.chart_render.render_north()` / `render_south()` | North/South Indian chart styles |

---

## The Bridge Modules — Why They Exist

`engine/` was the original architecture (84 modules, multi-language reports, corpus, FastAPI). `runtime/` was added later (61 prediction-focused modules with cleaner Python). To avoid refactoring all of `engine/`, four **bridge modules** in `engine/` simply re-import from `runtime/` and expose the same API.

| Bridge | What it does | Underlying runtime module |
|---|---|---|
| `engine/dasha.py` | Re-exports `vimshottari()`, `current_dasha()`, `ashtottari()`, `yogini()`, `char()` | `runtime/granular_dasha.py` (+ minor adapter) |
| `engine/vargas.py` | Re-exports `all_vargas()`, `vargottama()` | `runtime/divisional_charts.py` + `extra_vargas.py` |
| `engine/kp_sublord.py` | Re-exports `get_kp_chart()`, `get_kp_position()` | `runtime/kp_paddhati.py` |
| `engine/panchanga.py` | Re-exports `panchanga()` + dataclass | `runtime/panchanga.py` |

Every bridge does:
```python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from runtime_module import the_real_function
```

This means **runtime/** is the source of truth for the four bridged areas (dasha, vargas, KP, panchanga). All of `engine/`'s downstream code calls the bridges, and ends up calling runtime/ underneath.

---

## Why This Architecture Works

### Separation of Concerns
- **`runtime/`** owns *pure prediction* — single-purpose modules that take a chart and return a result. Easy to test, easy to add. Example: `palmistry_engine.py` has no I/O, no FastAPI, no Tamil — it's just chart-in, palmistry-out.
- **`engine/`** owns *reading-craft* — multi-language narrative, PDF/SVG rendering, corpus matching, backtesting, calibration, learned ensembles. The hard "make it sound like a real astrologer" stuff.
- **The bridge layer** lets us evolve `runtime/` (add new dasha levels, fix bugs, add Tier 1 modules) without breaking the dozens of `engine/` consumers that depend on the old API.

### Single Entry Point
`engine_unified.py` is the one function call that gives you everything:
```python
from engine_unified import unified_analysis
result = unified_analysis(chart)
```
You don't have to know which engine owns which capability. The orchestrator routes calls to runtime/ for predictions and engine/ for reading-craft, then merges results.

### Mode Filtering
`unified_analysis(chart, modes=["tier1"])` lets you skip the 60+ modules you don't need. Useful when:
- You only want palmistry/vastu/face for a "personal report" tab
- You only want dashas for a "timing finder" tool
- You're benchmarking and want minimal output

### Corpus Layer is Independent
Both engines can query the corpus, but neither *depends* on it for compute. If the corpus is missing or corrupted, the engines still produce predictions — they just lose the verbatim citations.

---

## Trade-Offs

### Duplicates
Some areas exist in both engines:
- **Yogas**: `runtime/comprehensive_yogas.py` + `runtime/yoga_library_v2.py` (~45 yogas) AND `engine/yogas.py` + `engine/yogas_extended.py` + `engine/yogas_nabhasa.py` (~50+ yogas, including 32 Nabhasa)
- **Lal Kitab**: `runtime/lal_kitab.py` (3 functions, light) AND `engine/lal_kitab.py` (5 functions including `karmic_debts()`, `closed_houses()`, `remedies_for()`, full LalKitabChart class)
- **Ashtakavarga**: `runtime/ashtakavarga.py` (basic Bhinna+Sarva) AND `engine/ashtakavarga.py` (with shodhana, kaksha vibhaga, transit_strength)
- **Shadbala**: `runtime/shadbala.py` (basic) + `runtime/shadbala_full.py` (research-grade) AND `engine/shadbala.py` (with `BalaScore` dataclass + summary)

Why we keep both:
- `engine/` versions have richer narrative output and Tamil bindings
- `runtime/` versions are the modern API used by `engine_orchestrator.py` and the PDF report
- Users/consumers may have already integrated against the older `engine/` API
- Removing one would break either the FastAPI server or the PDF report

### Bridge Complexity
The `sys.path.insert` pattern in bridges is brittle:
- If `runtime/` is renamed or moved, every bridge breaks.
- IDE jump-to-definition can't always follow the bridge.
- Circular imports are possible if a `runtime/` module ever needs something from `engine/`.

Mitigation: bridges are tiny (≤30 lines each), fully tested by the orchestrator, and changes to bridge surface require updating the bridge file only.

### Two PDF Generators
- `runtime/generate_report.py` — modern, deep-narrative PDF (used by CLI default `--mode pdf`)
- `engine/pdf_render.py` — older Markdown→PDF pipeline (used by some `engine/client_report_*.py` paths)

The older one survives because it integrates Tamil narrative and the verbose chapter system. New work goes into `runtime/generate_report.py`.

### Coverage Gaps
- `runtime/event_predictor.py` (legacy) and `runtime/event_predictor_v2.py` (current) — both still importable. v2 is the one called by orchestrator. v1 is kept for older test scripts.
- `runtime/dasha_systems_full.py` exists but is **not imported by orchestrator**. Functions inside (`compute_kalachakra`, `compute_shoola`, etc.) are accessible but uncalled in standard flow. They're effectively in the "future Tier 2 work" bucket.
- `runtime/_patch_predictions.py` is a monkey-patch utility from an earlier refactor — not part of any public API.

### Performance
A full `unified_analysis(chart)` call runs **~50 prediction modules + ~10 engine helpers + corpus loads**. On a modern laptop this is 2-4 seconds. Hot path optimizations possible:
- Lazy-load corpus (currently eager-loaded at module import)
- Cache ephemeris calls (currently recomputes per module)
- Skip unused tiers via `modes=` parameter

---

## Module Counts

| Layer | Count | Lines (approx) |
|---|---|---|
| `runtime/` | 61 .py modules | ~16,000 |
| `engine/` | 84 .py modules | ~22,000 |
| Bridge modules (subset of engine/) | 4 | <100 each |
| FastAPI surface (`main.py`) | 1 | ~660 |
| Unified orchestrator (`engine_unified.py`) | 1 | ~230 |
| Total Python | 147 modules | ~38,000 lines |

Plus:
- Book corpus: 38 classical texts, 11,692 indexed passages
- Gemma extractions: 19 LLM-digested book summaries → 16,126 rules
- Charts on file: 4 fully-validated test charts

---

## What to Edit When

| If you want to… | Edit this |
|---|---|
| Add a new yoga | `runtime/comprehensive_yogas.py` or `runtime/yoga_library_v2.py` |
| Add a new dasha system | `runtime/other_dashas.py` (or a new file + register in `engine_orchestrator.py`) |
| Add a new prediction tradition (e.g. Kerala Prashna) | New file in `runtime/`, register in `engine_orchestrator.py` and `engine_unified.py` |
| Add a new PDF section | `runtime/generate_report.py` `all_predictions()` function or `chapter_with_narrative()` |
| Add an HTTP endpoint | `main.py` (or a new `engine/web.py` route if Flask is preferred) |
| Add a new chart | Drop JSON in `F:/Atro/charts/` (no code change needed) |
| Add a new book to the corpus | Place txt in `F:/Atro/books/`, run `runtime/book_corpus_indexer.py` |
| Add Tamil/Hindi translation | `engine/i18n.py` + `engine/narrative_ta.py` for narrative |
| Improve calibration | `engine/calibration.py` + `engine/severity_refit.py` + `engine/learned_ensemble.py` |
