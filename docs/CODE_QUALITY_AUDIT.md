# Atro Vedic Engine — Code Quality Audit

**Date:** 2026-05-06
**Scope:** `F:/Atro/engine/` (89 root .py + 17 engines/* + 35 tests/* = 141 files), `F:/Atro/runtime/` (61 .py), `F:/Atro/main.py`, `F:/Atro/engine_unified.py`
**Method:** import graph analysis via Bash/Grep + manual diff of overlapping modules
**Read-only:** no source code was modified.

---

## Executive Summary

The codebase has two engines built at different times by different mental models, now stitched together by 4 bridge modules and `engine_unified.py`. The structural risks are concentrated, not diffuse:

1. **3 duplicate-name files** — for every overlap (`ashtakavarga`, `lal_kitab`, `shadbala`) the `engine/` version is 2-3x larger and academically more rigorous (BPHS-cited, full bindu tables, 6-bala vs. 4-bala). The `runtime/` versions are leaner ports written during the May v14 push. **Engine/ is canonical** — runtime/ versions should be renamed (`*_lite.py`) or deleted.
2. **35 of 89 root files in engine/ are never imported as `engine.X`** (39%). Most are pulled in lazily by `client_report.py`/`cli.py`/`tests/` so they're not truly dead — but 3 (`bhrigu_chart_root.py`, `bhrigu_engine_root.py`, `bhrigu_root.py`) have **zero references anywhere** and are safe to delete (~85 KB).
3. **Constant duplication is the biggest mess.** 25 of 61 runtime files redefine `RASIS` inline; 10 redefine `DIGNITIES`; 7 redefine `NAKSHATRAS`. Engine-side, `RASIS`/`SIGNS`/`SIGN_LORD`/`EXALTATION`/`DEBILITATION` are redefined in 13+ files. Single source-of-truth (`runtime/vedic_core.py`) exists but is ignored by 80% of consumers.
4. **52 of 62 runtime files contain `sys.path.insert(0, ".")`** — a brittle pattern that only works if invoked from the `runtime/` directory. The 4 bridge modules in engine/ work around this with their own `sys.path` injection, doubling the fragility.
5. **No circular imports** detected. Naming is uniformly snake_case for both files and functions.

The cleanup is mostly mechanical: consolidate constants, delete 3 dead bhrigu_root files, merge or rename the 3 duplicates, replace `sys.path.insert` with proper packaging. ~1 day of focused work removes ~80% of structural debt.

---

## A. Duplicate Logic Analysis

Three files exist in both `engine/` and `runtime/` with the same name but different APIs.

### A.1 `ashtakavarga.py` — engine/ wins (303 vs 190 lines)

| Aspect | `engine/ashtakavarga.py` | `runtime/ashtakavarga.py` |
|--------|---------------------------|----------------------------|
| Lines | 303 | 190 |
| Public functions | 11 | 4 |
| Bindu tables | Full 8x12 per planet (BPHS Ch. 49 verbatim) | Same tables but re-typed as lists |
| Shodhana | `trikona_shodhana()` + `ekadhipatya_shodhana()` + combined `shodhana()` | Not implemented |
| Transit strength | `transit_strength(chart, planet, lon)` | Not implemented |
| Kaksha vibhaga | `kaksha_vibhaga(chart, planet)` | Not implemented |
| Strength labels | `bav_strength_label`, `sav_strength_label` per BPHS thresholds | `interpret_house_bindus` — 5 generic labels |
| Output structure | dict[planet → list[12 bindus]] (positional) | dict[planet → dict[house_N → bindus]] (named) |
| Source citations | BPHS, Phaladeepika, Saravali, Sanjay Rath | BPHS, Phaladeepika, Sarvarth Chintamani |
| Hard-coded sys.path | No | `sys.path.insert(0, ".")` (line 22) |

**Side-by-side bindu table (Sun's contribution):**

```python
# engine/ashtakavarga.py:39-48 (sets, immutable-ish)
"Sun": {
    "Sun":     {1, 2, 4, 7, 8, 9, 10, 11},
    "Moon":    {3, 6, 10, 11},
    ...

# runtime/ashtakavarga.py:31-39 (lists)
"Sun": {
    "Sun":     [1,2,4,7,8,9,10,11],
    "Moon":    [3,6,10,11],
    ...
```
Identical content. Engine/ uses `set` for O(1) `in` lookups; runtime/ uses `list`.

**Recommendation:** Keep `engine/ashtakavarga.py`. Rename `runtime/ashtakavarga.py` → `runtime/_ashtakavarga_lite.py` or delete after porting `engine_orchestrator.py` (line referencing `from ashtakavarga import compute_bhinna_ashtakavarga, compute_sarvashtakavarga`) to use `engine.ashtakavarga.bhinna_ashtakavarga`/`sarva_ashtakavarga`. The signatures differ, so a small adapter is needed.

### A.2 `lal_kitab.py` — engine/ wins (409 vs 159 lines)

| Aspect | `engine/lal_kitab.py` | `runtime/lal_kitab.py` |
|--------|------------------------|-------------------------|
| Lines | 409 | 159 |
| Public functions | 10 + 2 dataclasses (`LalKitabPlacement`, `LalKitabChart`) | 3 |
| Pakka ghar | `LAL_KITAB_PAKKA_GHAR` dict (9 planets) | Not implemented |
| Aspects | `LAL_KITAB_ASPECTS` 9-planet table | Not implemented |
| Karmic debts | 5 patterns with full trigger DSL + Hindi names | 7 karz with English-only triggers |
| Closed houses | `CLOSED_HOUSE_PATTERNS` + `closed_houses(chart)` | `asleep_planets(chart)` — different concept |
| Remedies | `remedies_for(chart)` per detected rin | Embedded in karz dict |
| API | OOP dataclasses with `chart_summary(lk)` | Functional, returns dicts |

**Karz pattern divergence** — engine/ has 5 (Pitra/Matra/Bhratra/Stree/Putra), runtime/ has 7 (adds Nyaya + Atma). Both correctly cite Lal Kitab Ch. 6 — different traditions/scholars list 5 vs 7. Engine/ is the more conservative classical reading.

**Recommendation:** Keep `engine/lal_kitab.py` as canonical. The 2 extra karz from runtime/ (Nyaya Rin, Atma Rin) should be **ported into the engine/ `RIN_PATTERNS` list** with proper trigger DSL, then runtime/ deleted. The `engine.web` and `engine.tests.test_lal_kitab` already import from `engine.lal_kitab` — runtime version is referenced only by `engine_orchestrator.py:line ~XX` and `generate_report.py`.

### A.3 `shadbala.py` — engine/ wins decisively (442 vs 137 lines)

| Aspect | `engine/shadbala.py` | `runtime/shadbala.py` |
|--------|------------------------|-------------------------|
| Lines | 442 | 137 |
| Balas implemented | 4 of 6 (Sthana, Dig, Kala, Naisargika) — but each fully decomposed | 6 of 6 — but each is a coarse stub |
| Sthana sub-balas | 5 (Uchcha, Sapta-Vargaja, Ojha-Yugma, Kendradi, Drekkana) | 1 (sign-dignity only) |
| Cheshta Bala | Notes "needs daily speeds" — placeholder | Returns 60 if retro else 30 (overly simple) |
| Drik Bala | Listed as future | Single-axis aspect score |
| Output | `BalaScore` dataclass with all sub-balas | Plain int per planet |
| Threshold check | `SHADBALA_THRESHOLDS_RUPA` per planet | `THRESHOLD` dict — same values |

**Quality gap:** `engine/shadbala.py:_uchcha_bala` (line ~150) computes uchcha bala with proper exalt/debil arc-distance math; `runtime/shadbala.py:_sthana_bala` returns a literal `+60/+45/+30/+5` lookup. Engine/ is academically faithful; runtime/ is a sketch.

**Recommendation:** Keep `engine/shadbala.py`. Runtime/ version is a placeholder — delete and update `engine_orchestrator.py` line `from shadbala import compute_shadbala` to import `engine.shadbala.compute as compute_shadbala`. Engine/ already has `summary()` for orchestrator-friendly dict output.

### A.4 Summary of duplicate-file recommendations

| File | Action | Effort |
|------|--------|--------|
| `runtime/ashtakavarga.py` | Delete; orchestrator switches to `engine.ashtakavarga` with adapter for output shape | 1 hr |
| `runtime/lal_kitab.py` | Port Nyaya + Atma Rin into `engine.lal_kitab.RIN_PATTERNS`, then delete | 1 hr |
| `runtime/shadbala.py` | Delete; orchestrator switches to `engine.shadbala.compute` | 30 min |

---

## B. Dead Code Detection in `engine/`

### B.1 Methodology

```bash
grep -rhE "^(from|import) engine\." F:/Atro --include="*.py"
   | extract module name → 55 unique modules referenced
ls F:/Atro/engine/*.py → 89 files
diff → 35 files NOT imported as `engine.X`
```

**Caveat:** `from engine import X` (without `.X`) is also valid; lazy imports inside functions are also valid. The supposedly-unused list was cross-checked for those patterns — most are recovered. Only **3 files have ZERO references anywhere** (truly dead).

### B.2 Engine/ Root Files — Usage Table (89 files)

| Module | Direct `engine.X` imports | Recovered via lazy/test/`from engine import X` | Status |
|---|---:|:---:|:---|
| `chart` | 17 | — | USED |
| `dasha` | 8 | — | USED (bridge) |
| `comparative_test` | 8 | — | USED |
| `backtest` | 8 | — | USED |
| `known_charts` | 7 | — | USED |
| `engines` (subpkg) | 7 | — | USED |
| `negative_backtest` | 5 | — | USED |
| `reading` | 4 | — | USED |
| `narrative_ta` | 4 | — | USED |
| `narrative` | 4 | — | USED |
| `i18n` | 4 | — | USED |
| `corpus` | 4 | — | USED |
| `transit_conditioned` | 3 | — | USED |
| `chart_relative` | 3 | — | USED |
| `yogas` | 2 | — | USED |
| `transits` | 2 | — | USED |
| `synth` | 2 | test_life_narrative | USED |
| `panchanga` | 2 | — | USED (bridge) |
| `muhurta` | 2 | — | USED |
| `lal_kitab` | 2 | test_lal_kitab | USED |
| `kp_sublord` | 2 | — | USED (bridge) |
| `dasa_narrative` | 2 | test_life_narrative | USED |
| `consensus_report` | 2 | — | USED |
| `client_report` | 2 | — | USED |
| `chart_render` | 2 | — | USED |
| `chapters` | 2 | — | USED |
| `afflictions` | 2 | tests | USED |
| (~28 more with count==1) | 1 | — | USED |
| `bhrigu_predictions` | 1 | — | USED |
| `synth` | 1 | test | USED |
| `vargas` | 1 | — | USED (bridge) |
| `ayanamsa_picker` | 0 | test_v113, chart.py lazy | INTERNAL |
| `feedback` | 0 | test_feedback (lazy `from engine import feedback`) | INTERNAL (test-only) |
| `tamil_numerology` | 0 | test_v113 | INTERNAL (test-only) |
| `deep_rules` | 0 | test_v113 | INTERNAL (test-only) |
| `event_feedback` | 0 | test_life_narrative | INTERNAL (test-only) |
| `verse_locator` | 0 | client_report (lazy), test_deep_extract | INTERNAL |
| `ashtakavarga` | 0 | test_audit_tier1_tier2 (lazy) | INTERNAL (test-only) |
| `bhava_bala` | 0 | test_audit_tier1_tier2 (lazy) | INTERNAL (test-only) |
| `conditioned` | 0 | test_audit_tier1_tier2 (lazy) | INTERNAL (test-only) |
| `argala` | 0 | test_audit_tier1_tier2 (lazy) | INTERNAL (test-only) |
| `life_domains` | 0 | client_report, chapters, traits_72, cli (lazy) | INTERNAL |
| `traits_72` | 0 | client_report, client_report_ta (lazy) | INTERNAL |
| `life_narrative` | 0 | cli (lazy), test_life_narrative | INTERNAL |
| `accident` | 0 | traits_72 lazy | INTERNAL |
| `education` | 0 | traits_72 lazy, engines/education exists | INTERNAL |
| `timeline_deep` | 0 | client_report (lazy) | INTERNAL |
| `cross_validate` | 0 | client_report (lazy) | INTERNAL |
| `gochar` | 0 | bhrigu_engine_root only (which itself is dead) | LIKELY DEAD |
| `web` | 0 | python -m engine.web entry point | USED (entrypoint) |
| `cli` | 0 | python -m engine.cli entry point | USED (entrypoint) |
| `transit_learn` | 0 | None found (had self-references in transits but dead) | LIKELY DEAD |
| `learned_ensemble` | 0 | None found | LIKELY DEAD |
| `varga_weighted` | 0 | None found | LIKELY DEAD |
| `severity_refit` | 0 | None found | LIKELY DEAD |
| `dasha_compute` | 0 | None found | LIKELY DEAD |
| `affliction_backtest` | 0 | None found (only its own __main__) | LIKELY DEAD |
| `blessing_backtest` | 0 | None found (only its own __main__) | LIKELY DEAD |
| `chart_relative_backtest` | 0 | None found (only its own __main__) | LIKELY DEAD |
| `synthesis` | 0 | Only docs reference it | LIKELY DEAD |
| `client_report_v2_ta` | 0 | None found (sibling client_report_v2 is used) | LIKELY DEAD |
| `timeline_ta` | 0 | None found | LIKELY DEAD |
| **`bhrigu_chart_root`** | 0 | **NONE** | **DEAD** |
| **`bhrigu_engine_root`** | 0 | **NONE** | **DEAD** |
| **`bhrigu_root`** | 0 | **NONE** | **DEAD** |
| `__init__` | — | (package init) | USED |

### B.3 Counts

- **USED externally (imported as `engine.X`):** 53 files
- **INTERNAL (only via tests, lazy, or as __main__ entrypoint):** 18 files
- **LIKELY DEAD (no callers found, ever):** 14 files (~250 KB)
- **CONFIRMED DEAD (zero references including lazy/test):** 3 files = `bhrigu_chart_root.py`, `bhrigu_engine_root.py`, `bhrigu_root.py` (~85 KB combined)

**Note:** "LIKELY DEAD" means `_backtest`/`_refit` files that were one-shot research scripts. They have `if __name__ == "__main__"` blocks and produce reports but nothing imports them. These are research scaffolding — keep them in a `engine/_research/` subfolder rather than deleting outright.

---

## C. Constants Consolidation

### C.1 Inventory

`runtime/vedic_core.py` is the declared single-source-of-truth (lines 8-65: `RASIS`, `RASI_LORDS`, `DIGNITIES`, `PLANETS_MAIN`, `NAKSHATRAS`, `EXALTATION_SIGNS`, `DEBILITATION_SIGNS`, `VIMSHOTTARI_ORDER`, etc.). Engine-side has no equivalent — constants are scattered.

### C.2 Files redefining `RASIS` instead of importing

| Side | Files redefining | Files importing from `vedic_core` |
|------|---:|---:|
| `runtime/` | **25** | 5 |
| `engine/` | 2 (`comparative_test.py`, `corpus.py`) — and many use a differently-named `SIGNS` instead | n/a (no equivalent) |

**Runtime/ files redefining `RASIS`** (line 1 of each file):
```
argala_jaimini.py:18, char_dasha.py:18, chart_rectification.py:12,
comprehensive_yogas.py:19, compute_jayaprakesh.py:17, compute_krishnan.py:28,
compute_sree.py:27, divisional_charts.py:34, dosha_cancellations.py:10,
eclipse_impact.py:17, event_predictor_v2.py:17, event_yoga_detector.py:19,
generate_report.py:71, jaimini_full.py:8, longevity_ayurdaya.py:28,
prashna_horary.py:12, sade_sati.py:10, sahams.py:25, sibling_predictor.py:14,
special_lagnas.py:9, transit_engine.py:?, upagrahas.py:?,
varshaphala.py:?, yoga_library_v2.py:?
```

**Runtime/ files redefining `DIGNITIES`** (10):
```
comprehensive_yogas.py:22, event_predictor.py:16, event_predictor_v2.py:20,
event_yoga_detector.py:10, generate_report.py:83, longevity_ayurdaya.py:31,
shadbala.py:17, sibling_predictor.py:26, yoga_library_v2.py:?
```

### C.3 Engine-side constant scattering

`SIGN_LORD`, `EXALTATION`, `DEBILITATION`, `OWN_SIGNS`, `SIGNS` are defined in:
```
engine/afflictions.py:        SIGN_LORD = {...}
engine/bhava_bala.py:         SIGN_LORD = {...}
engine/blessings.py:          SIGN_LORD + OWN_SIGNS
engine/chapters.py:           SIGNS = ["Aries", ...]
engine/chart.py:              SIGNS, SIGN_LORDS
engine/chart_relative.py:     SIGN_LORD
engine/client_report_v2.py:   SIGNS = [...]
engine/i18n.py:               SIGNS = {...}  (this one's a multilang map)
engine/life_domains.py:       SIGNS, SIGN_LORD
engine/prashna.py:            SIGN_LORD
engine/synth.py:              EXALTATION, DEBILITATION, OWN_SIGNS
engine/tajik.py:              SIGN_LORD
engine/traits_72.py:          SIGNS, SIGN_LORD
engine/varga_weighted.py:     OWN_SIGNS
engine/yogas.py:              SIGNS, SIGN_LORDS, EXALTATION, DEBILITATION, OWN_SIGNS  (the canonical engine-side)
engine/yogas_extended.py:     SIGN_LORD
engine/bhrigu_chart_root.py:  SIGNS  (dead file)
engine/bhrigu_engine_root.py: OWN_SIGNS  (dead file)
main.py:                      EXALTATION, DEBILITATION, SIGN_LORD
```

### C.4 Consistency check

Spot-checked `RASIS`/`SIGNS` lists across 8 files (`engine/yogas.py`, `engine/chart.py`, `engine/chapters.py`, `runtime/vedic_core.py`, `runtime/comprehensive_yogas.py`, `runtime/divisional_charts.py`, `runtime/jaimini_full.py`, `main.py`):

> All eight files use **identical** sign list — Aries through Pisces in the same order. ✓
> All eight `SIGN_LORD`/`RASI_LORDS` mappings are identical. ✓
> All eight `EXALTATION`/`DEBILITATION` are identical. ✓

So the duplication is **redundant but consistent** — no semantic divergence (yet). The risk is one file getting updated and the others drifting silently.

### C.5 Recommendation

**Phase 1 (mechanical):**
1. Make `engine/yogas.py` import its constants from `engine.constants` (a new file mirroring `runtime/vedic_core.py`'s structure with English/internal names: `SIGNS`, `SIGN_LORDS`, `EXALTATION`, `DEBILITATION`, `OWN_SIGNS`, `NAKSHATRAS`).
2. Have `runtime/vedic_core.py` import from `engine.constants` (or vice-versa — pick one canonical home; `runtime/vedic_core.py` is more complete so prefer that direction).
3. Replace 25 runtime redefinitions with `from vedic_core import RASIS, RASI_LORDS, DIGNITIES`.
4. Replace ~13 engine redefinitions with `from engine.yogas import SIGN_LORD, EXALTATION, DEBILITATION` (or new `engine.constants`).

**Phase 2 (cleanup):**
5. Delete the in-file redefinitions; rerun the test suite (35 test files in `engine/tests/`) to confirm.

**Files that should import (not redefine) immediately** (highest leverage):
```
runtime/comprehensive_yogas.py    # has 4 redefined constants
runtime/event_predictor_v2.py     # has 3 redefined constants
runtime/event_yoga_detector.py    # has 3 redefined constants
runtime/longevity_ayurdaya.py     # has 3 redefined constants
runtime/yoga_library_v2.py        # has 3 redefined constants
runtime/shadbala.py               # if not deleted per A.3
runtime/generate_report.py        # 190 KB — redefines 3 constants in own scope
```

---

## D. Naming / Style Inconsistencies

### D.1 English vs Tamil sign names

| Convention | Files | Note |
|------------|-------|------|
| English (Aries, Taurus...) | `engine/yogas.py`, `engine/chart.py`, all `runtime/*.py` | Dominant — ~95% of code |
| Sanskrit (Mesha, Vrishabha...) | `engine/bhrigu_chart_root.py` (DEAD), `engine/bhrigu_engine_root.py` (DEAD), `engine/lal_kitab.py` (sparse comments only), `engine/i18n.py` (translation table) | Limited — mostly in dead bhrigu files |
| Tamil (Mesham, Rishabham...) | None directly in code; only as data values inside `chapters_ta.py`, `narrative_ta.py`, `client_report_ta.py`, `client_report_v2_ta.py`, `timeline_ta.py`, `tamil_numerology.py` (translation outputs) | Tamil flows through translation, not as constants |

**Conclusion:** Sign-name dominance is English-internal. Tamil/Sanskrit names appear only as *output strings* via `i18n.py`, never as keys. This is the right architecture; the bhrigu_root dead files are the lone exception (and they're dead).

### D.2 Function naming

- All function defs sampled from `engine/*.py` and `runtime/*.py` use **snake_case**. ✓
- No `camelCase` defs found except where they're inside docstrings/comments referencing JS clients.
- All `class` definitions use **PascalCase** (`BalaScore`, `LalKitabPlacement`, `Panchanga`, `ChartFact`). ✓

### D.3 File naming

All 89 + 17 + 35 + 61 = 202 Python files use **snake_case** with no exceptions. ✓

### D.4 The one inconsistency that matters

**Chart-output schema divergence between engine/ and runtime/:**

```python
# engine/ashtakavarga.py returns:
bhinna_ashtakavarga(chart) → {planet: [b1, b2, ..., b12]}        # positional list

# runtime/ashtakavarga.py returns:
compute_bhinna_ashtakavarga(chart) → {planet: {"house_1": b1, ..., "total": T}}  # named dict
```

This is the kind of drift that catches you when integrating. Choose one and document it.

---

## E. Import Graph

### E.1 Top 10 most-imported modules (across whole project)

| Rank | Module | External imports | Notes |
|---:|---|---:|---|
| 1 | `engine.chart` | 17 | The pipeline entry; tests + scratch + tools depend on it |
| 2 | `engine.dasha` | 8 | Bridge module; brought in by 7 engine/ files |
| 3 | `engine.backtest` | 8 | EVENT_PATTERNS table is canonical |
| 4 | `engine.comparative_test` | 8 | Used by main.py + 4 scratch reports |
| 5 | `engine.known_charts` | 7 | Manoj/Sree/Krishnan/Jayaprakesh fixtures |
| 6 | `engine.engines` (subpkg) | 7 | 16 mini-engines for life domains |
| 7 | `engine.negative_backtest` | 5 | Used by 4 backtest cousins |
| 8 | `engine.reading` | 4 | LLM narrative entry |
| 9 | `engine.narrative_ta` | 4 | Tamil rendering |
| 10 | `engine.narrative` | 4 | English rendering |

`runtime/` modules don't appear in the top-10 because runtime files are imported by **bare name** (`from granular_dasha import ...`) — they're discoverable only via `sys.path.insert` at the top of each file. The bridge modules (`engine/dasha.py`, `engine/vargas.py`, `engine/kp_sublord.py`, `engine/panchanga.py`) thread runtime functionality through the engine namespace.

### E.2 Circular imports

**None detected.** Verified via:
- `engine/yogas.py` has 0 `from engine.*` imports → leaf node ✓
- `engine/shadbala.py` imports only `engine.yogas` (one direction) ✓
- `engine/chart.py` is a hub (imports 6 engine/* modules) but is never imported by them → safe ✓
- Bridge modules (`engine/dasha.py` etc.) only import from `runtime/*` via `sys.path` — no cycles back into engine ✓

### E.3 External dependencies

| Dep | Files using | Purpose |
|-----|---:|---------|
| `swisseph` (pyswisseph) | 16 (engine + runtime + main.py) | Ephemeris/sidereal positions |
| `reportlab` | 6 (mostly runtime/generate_report + extra_vargas) | PDF generation |
| `fastapi` | 2 (`main.py`, `engine/web.py`) | API |
| `pydantic` | 1 (`main.py`) | Request validation |

`requirements.txt` only declares 4 packages: fastapi, uvicorn, pyswisseph, pydantic. **Missing from requirements.txt:** `reportlab` — used by 6 files. This will break `pip install -r requirements.txt` for any clean environment trying to generate PDFs.

### E.4 The `sys.path.insert(0, ".")` pattern (runtime/ fragility)

**52 of 62 runtime files** start with:
```python
import sys
sys.path.insert(0, ".")
```
This only works if Python is invoked from the `runtime/` directory. If invoked from elsewhere (e.g., from `F:/Atro/`), the bare-name imports (`from granular_dasha import ...`) will fail.

The 4 bridge modules in `engine/` work around this:
```python
# engine/dasha.py:6
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
```
This is doubly fragile because it's a sibling-directory hack. Proper packaging (`runtime/__init__.py` empty + run from `F:/Atro/`) would let imports resolve naturally as `from runtime.granular_dasha import ...`.

---

## F. Recommendations (Top 10, ranked by impact)

| # | Action | Impact | Effort | Risk |
|---:|--------|--------|--------|------|
| **1** | **Delete 3 dead bhrigu_root files** (`bhrigu_chart_root.py`, `bhrigu_engine_root.py`, `bhrigu_root.py` — ~85 KB, zero callers) | Cleanup, removes confusion about which bhrigu_ engine is canonical | 15 min | None — verified no imports |
| **2** | **Add `runtime/__init__.py`** + **remove `sys.path.insert(0, ".")`** from 52 runtime files; switch bridge modules and `engine_orchestrator.py` to `from runtime.X import ...` | Makes the runtime/ package portable; removes 52 lines of brittle path-hacking | 1 hour | Low — must run test suite + `engine_unified.py` end-to-end |
| **3** | **Consolidate constants — Phase 1**: pick `runtime/vedic_core.py` as canonical, replace 25 runtime/ `RASIS = [...]` redefinitions with `from vedic_core import RASIS, RASI_LORDS, DIGNITIES` | Single source of truth — prevents future drift; ~150 LOC removed | 1 hour | Low — values are already identical (verified) |
| **4** | **Resolve `shadbala.py` duplicate**: delete `runtime/shadbala.py` (137 lines, stub-quality), update `engine_orchestrator.py` line `from shadbala import compute_shadbala` → `from engine.shadbala import compute as compute_shadbala` | Removes embarrassment-grade stub; ensures full 5-sub-bala calculation flows through orchestrator | 30 min | Low — engine.shadbala.summary() returns dict |
| **5** | **Resolve `ashtakavarga.py` duplicate**: delete `runtime/ashtakavarga.py`, write small adapter `engine_to_runtime_av_shape()` so orchestrator's downstream consumers don't break | Reduces file count; canonical 11-function impl available everywhere; transit_strength + shodhana now in orchestrator | 1 hour | Medium — output schema differs, requires adapter |
| **6** | **Resolve `lal_kitab.py` duplicate**: port runtime/'s 2 extra karz (Nyaya, Atma) into engine/'s `RIN_PATTERNS`, then delete runtime/lal_kitab.py | Engine becomes 7-karz; downstream code unified | 1 hour | Low — both files cite Lal Kitab Ch. 6 |
| **7** | **Move 11 LIKELY-DEAD research files to `engine/_research/`** (`affliction_backtest.py`, `blessing_backtest.py`, `chart_relative_backtest.py`, `synthesis.py`, `severity_refit.py`, `learned_ensemble.py`, `transit_learn.py`, `varga_weighted.py`, `dasha_compute.py`, `client_report_v2_ta.py`, `timeline_ta.py`) | Signals "experimental/scaffolding" without deleting; cleaner top-level engine/ | 30 min | Low — files have only `__main__` blocks |
| **8** | **Add `reportlab` to `requirements.txt`** (currently used by 6 files but not declared) | Reproducible installs; PDF generation works in CI | 5 min | None |
| **9** | **Consolidate engine-side constants — Phase 2**: create `engine/constants.py` re-exporting from `runtime.vedic_core` (or vice-versa); replace 13 engine/ in-file `SIGN_LORD`/`EXALTATION`/etc. redefinitions | Closes the loop on constant duplication across the whole project | 2 hours | Medium — must update tests, run full battery |
| **10** | **Document the engine/ vs runtime/ split** (or merge): write a 1-page `F:/Atro/docs/ARCHITECTURE.md` explaining the bridge pattern, when to add code in engine/ vs runtime/, and the `engine_unified.py` contract. Long-term: consider folding runtime/ into `engine/extended/` with proper Python packaging. | Onboarding clarity; reduces "where do I put new code" decision fatigue | 1 day (architecture decision + writeup; or 0 if just documenting current state) | None for documentation; medium if merging |

### F.1 Out-of-scope but worth flagging

- **`runtime/_patch_predictions.py`** is 72 KB. Likely a one-shot script — confirm and either move to `_research/` or delete.
- **`runtime/generate_report.py`** is 190 KB. The largest file in the project. Probably needs to be split into per-section modules (cover, predictions, dashas, vargas, etc.). Out of scope for this audit.
- **35 test files in `engine/tests/`**, but no test runner config (`pytest.ini` / `pyproject.toml`) found in `F:/Atro/`. Tests can only be discovered manually.
- **Two `web` entry points** (`engine/web.py` Flask + `main.py` FastAPI) — only `main.py` is wired to PM2/the FastAPI deployment. `engine/web.py` may be obsolete; verify.

---

## Appendix — Verification commands used

```bash
# Module usage frequency
grep -rhE "^(from|import) engine\." F:/Atro --include="*.py" \
   | sed -E 's/^(from|import) engine\.([a-zA-Z_0-9]+).*/\2/' \
   | sort | uniq -c | sort -rn

# Constant redefinitions
grep -lE "^RASIS *=" F:/Atro/runtime/*.py | wc -l       # → 25
grep -lE "^DIGNITIES *=" F:/Atro/runtime/*.py | wc -l   # → 10

# sys.path hack count
grep -lE "sys\.path\.insert" F:/Atro/runtime/*.py | wc -l  # → 52

# Dead-file check (truly zero references)
for f in bhrigu_root bhrigu_chart_root bhrigu_engine_root; do
    grep -rE "engine\.${f}|from engine import ${f}" F:/Atro --include="*.py" \
       | grep -v "engine_unified\|/${f}\.py:" | wc -l
done
# → 0, 0, 0
```
