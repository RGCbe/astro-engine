# Atro Architecture Layers

**Generated from the 2026-07-18 restructure. Machine-readable manifest: [layers.json](layers.json).
Enforced by `engine/tests/test_layer_purity.py` — the foundation cannot silently grow upward dependencies.**

Every Python file belongs to exactly one layer. Lower layers must never import
from higher layers at module level (lazy imports inside functions are allowed
for interpretation helpers).

## The layers, bottom to top

| Layer | Files | What it is | Trust level |
|---|---|---|---|
| **L0_foundation** | 12 | Pure astronomy + math: planet positions (Swiss Ephemeris), divisional chart formulas, panchanga, ayanamsa, geocoding, shared constants (`vedic_core`) | **Verified against reality** — eclipses, published ayanamsa, hand-computed BPHS formulas (`test_foundation_astronomy.py`) |
| **L1_time** | 23 | When things happen: all dasha systems, transits, sade sati, eclipses | Mechanical, reproducible |
| **L2_methods** | 55 | The classical method engines: Parashari pipeline, Jaimini, KP, Nadi, Tajik, yogas, strength systems (shadbala/ashtakavarga), kuta | Classical rules, citable |
| **L3_topics** | 29 | Life-area mini engines: career, marriage, children, health, longevity, remedies… | Interpretation |
| **L4_prediction** | 54 | Event predictors (3 generations), orchestrators, **event_fusion** (convergence gate), **truth engine** (knowledge graph) | Only fusion+truth claims are validated (1.62× chance, p=3.7e-04) |
| **L5_services** | 14 | Client services: muhurta, prashna, compatibility matching, birth-time rectification | Product features |
| **L6_esoteric** | 15 | Western, Chinese, Mayan, numerology, palmistry, I-Ching, vastu, omens | Report color only — **measured: dilutes timing skill, never gates claims** |
| **L7_corpus** | 17 | Book corpus: ~15,000 extracted rules, citations, Bhrigu | 89% single-book; citations explain, never prove |
| **L8_output** | 42 | PDFs (EN/TA/HI), translations, chart rendering, narratives | Presentation |
| **L9_api** | 9 | FastAPI service, tier auth, entry points (`src/`, `main.py`) | Deployment |
| **research** | 50 | Backtests, scorers, audits, battle scripts, scratch | Never ships to clients |

## The two load-bearing rules

1. **L0 purity** (enforced by test): foundation files import only stdlib,
   `swisseph`, or other L0 files at module level. If a foundation file needs a
   book citation or a yoga, that call goes in a lazy import inside the
   function that needs it — or the file doesn't belong in L0.
2. **Claims flow through L4's gate**: anything client-facing that asserts a
   *timing* must come from `event_fusion` (≥2 independent classical families,
   tight window) via the truth engine's claim contract. L6 and L7 can decorate,
   never certify.

## Notable classification decisions

- `engine/chart.py` is **L2, not L0** — it's the full-chart pipeline
  orchestrator (imports dasha, yogas, shadbala). The pure compute twin is
  `engine/chart_builder.py` (L0). Parity between them is tested to 0.00004°.
- `engine/panchanga.py` and `engine/vargas.py` are L0 *bridges* to their
  runtime implementations.
- `event_predictor_v2.py` (L4) is the raw generator: ~35 predictions/yr,
  recall-only. It is an input to fusion, never a client surface by itself.

## How to keep this honest

- Adding a file? Add it to `layers.json` (the purity test fails on missing
  foundation files but new files elsewhere should be classified promptly).
- Moving a dependency into L0? The purity test will fail — that's the system
  working. Either the dependency is genuinely foundation math (reclassify it)
  or your code belongs higher up.
- Physical directory moves (a real `foundation/` package) are a future,
  git-protected step; the manifest is the source of truth until then.
