# Engine improvements and how to test (before frontend)

Do **engine QA first**, then UI. Frontend only displays what the API returns; bad math or fake accuracy cannot be fixed in CSS.

---

## What to improve (priority order)

### P0 � Mechanical truth (must be correct)

| Issue | Why it matters | Fix direction |
|-------|----------------|---------------|
| IST hardcoded (`hour - 5.5`) | Wrong chart outside India / DST | Per-birth `tz_hours` on all endpoints |
| Birth time sensitivity | 10 minutes can change lagna | Document + optional rectification note in API |
| Missing `ephe/` locally | Charts fail on Windows dev | Copy from VPS: `/opt/astro/ephe` ? `F:\astro\ephe` |
| Silent module failures | Client sees empty KP/Jaimini | Surface errors in `truth.partial_failures` (started) � extend to all blocks |

**Test:** PyJHora/cross-check sample charts; compare lagna �0.05� if PyJHora path set.

### P1 � Production prediction path (what clients should use)

| Issue | Why it matters | Fix direction |
|-------|----------------|---------------|
| Main API ? research GAC | Vijay 100% weights not in `jathagam` | Keep scratch weights out of `main.py` |
| `event_predictor_v2` only path for life events | This is the real engine | Improve rules; score with `_accuracy_scorer.py` |
| Loose �180d hit window | Inflates accuracy % | Report **strict** �45d + valence match (see `_battle_vijay.py` strict mode) |
| Numerology not in jathagam | Hybrid dream not live | Later: fuse after hold-out tests |

**Test:** `_accuracy_scorer.py` on 16 celebrities; target **honest** grand total, not 100% on one star.

### P2 � Consistency and maintainability

| Issue | Why it matters | Fix direction |
|-------|----------------|---------------|
| Duplicated chart build in `main.py` | Drift between jathagam / hybrid / PDF | **Done:** `engine/chart_builder.py` (`build_sidereal_chart`, `build_orchestrator_chart_dict`) |
| `engine_orchestrator` vs `jathagam` | PDF/tests use orchestrator; UI uses main | Document which is canonical for PDF |
| Category count drift (314 vs 402 in docs) | Confusing | Align docs with `category_catalog.py` |
| `book-battle` double full compute | Timeouts | Cache base chart inside request |

**Test:** `test_full_integration.py` � all 4 personal charts + orchestrator modules.

### P3 � Real hybrid (only after P0�P1 pass)

| Issue | Why it matters | Fix direction |
|-------|----------------|---------------|
| `/api/astrology/hybrid` = astro + astro only | Name misleads | Rename or add true GAC fusion |
| Vijay-tuned numerology weights | Overfit | Train on N?1 celebrities; test on hold-out |
| No per-client accuracy claim | Trust | Show windows + citations, not �100%� |

**Test:** Hold-out protocol (below); never tune on test celebrity.

---

## Test pyramid (run in this order)

```text
Level 1  SMOKE     Imports, API health, numerology formulas
Level 2  MECHANICAL Chart positions, dasha dates, corpus load
Level 3  PIPELINE  Orchestrator, PDF, main.py handlers
Level 4  OUTCOMES  Known events vs predictions (celebrity charts)
Level 5  HOLD-OUT  Predict without tuning on that person
```

Stop and fix engine code if a level fails before running the next.

---

## Commands (local � from `F:\astro`)

Use project venv if you have one:

```powershell
cd F:\astro
$py = ".\venv\Scripts\python.exe"   # or: python
```

### Level 1 � Smoke (5�15 min)

```powershell
# 1a. Full import + bridge + 4 charts + stress
& $py test_full_integration.py

# 1b. Numerology API math (not outcome prediction)
& $py scratch\test_numerology.py

# 1c. Start API (separate terminal), then:
& $py scratch\test_monetization.py
```

**Pass means:** `docs/INTEGRATION_TEST_RESULTS.md` shows imports OK; numerology asserts pass; monetization tier gates behave.

**Does NOT mean:** Life events are predicted correctly.

### Level 2 � Mechanical (10 min)

```powershell
# Ephemeris must exist
Test-Path F:\astro\ephe

# Health + engine metadata
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/engine
```

Optional: run `engine/tests/test_chart_relative.py` or famous chart tests under `engine/tests/`.

**Pass means:** API up; `truth_policy` in `/api/engine`; ephemeris present.

### Level 3 � Pipeline (30�180 min)

Already inside `test_full_integration.py` section 4:

- `engine_orchestrator.full_analysis` per chart (~16s each)
- PDF generation
- Section 6: `main.py` handler smoke

**Pass means:** 4/4 charts orchestrator OK; PDF files created; no import regressions.

### Level 4 � Outcome accuracy (production engine)

This measures **`event_predictor_v2`** against `known_events` in celebrity JSONs.

```powershell
cd F:\astro\runtime
& $py _accuracy_scorer.py
```

Output: `F:\astro\ACCURACY_REPORT.json` + console grand total.

**Current baseline (from last report):** ~**80.3%** on 16 celebrities, 127 events, �180d, `min_severity=2`.

**Also run Vijay battle (internal QA only):**

```powershell
& $py _battle_vijay.py
```

Read **OLD strict** and **NEW strict** � ignore **NEW calibrated** for public claims.

### Level 5 � Hold-out (honest hybrid / numerology)

Protocol:

1. **Train/tune** weights only on celebrities A�H (exclude Vijay).
2. **Test** on Vijay + 2 others with **no** parameter changes.
3. Report: hits / total, �45 days, valence from event text (hit vs flop).

Do **not** use `scratch/optimize_astro_numerology.py` final weights as production until hold-out passes.

---

## VPS (production mirror)

```bash
cd /opt/astro
./venv/bin/python test_full_integration.py
./venv/bin/python runtime/_accuracy_scorer.py
./venv/bin/python runtime/_battle_vijay.py
./venv/bin/python scratch/test_numerology.py
```

After code deploy: `pm2 restart astro-engine` then curl `/health`.

---

## What �good enough for frontend� means

| Gate | Minimum |
|------|---------|
| Level 1 | All integration imports pass |
| Level 2 | `ephe/` present; `/api/jathagam` returns 200 for sample birth |
| Level 3 | 4/4 personal charts orchestrator OK |
| Level 4 | `_accuracy_scorer` grand total **? 75%** (stretch 80%+), no celebrity at 0% |
| Level 4b | Vijay **strict** NEW engine documented (not marketed as 100%) |
| Policy | `truth` block on jathagam; no scratch weights in API |
| Performance | Single jathagam &lt; 180s on VPS (or async job pattern) |

Frontend can ship when **mechanical + pipeline + honest accuracy report** pass � not when Vijay research hits 100%.

---

## Metrics to track every release

Save these files in git or `docs/releases/YYYY-MM-DD/`:

| File | Metric |
|------|--------|
| `ACCURACY_REPORT.json` | Grand %, per-celebrity misses |
| `VIJAY_BATTLE.json` | `metrics_honest` (4 modes) |
| `docs/INTEGRATION_TEST_RESULTS.md` | Import/module/PDF status |
| Manual | jathagam latency (s) for one chart |

**Regression rule:** If grand accuracy drops **>3pp** or any P0 test fails, block release.

---

## What NOT to use as success criteria

- Vijay 68-film 100% after `optimize_astro_numerology.py`
- Book-battle consensus % as probability
- Pooled corpus rule % per film
- `user_tier` spoofing (fixed � use `api_key` only)

---

## Suggested next engine tasks (before UI)

1. Add `tz_hours` to `BirthData` and stop hardcoding IST.
2. Extract `build_chart_dict()` � single chart builder for all endpoints.
3. Add `runtime/_accuracy_scorer.py --strict` flag (�45d, valence).
4. Expand `CELEBRITIES` to include `rajinikanth`, `kamal_haasan`, `joseph_vijay` with **strict** scoring only.
5. Design `engine/gac_fusion.py` with fixed weights; validate hold-out before jathagam merge.

---

## One-page checklist

```
[ ] ephe/ installed locally and on VPS
[ ] test_full_integration.py � pass
[ ] _accuracy_scorer.py � grand ? 75%, review top misses
[ ] _battle_vijay.py � record strict columns in VIJAY_BATTLE.json
[ ] test_numerology.py � pass
[ ] test_monetization.py � pass (API running)
[ ] No import from scratch/ in main.py
[ ] truth block present on jathagam sample
[ ] Decision: tz + chart builder scheduled before frontend sprint
```

When all checked, frontend work is safe to start.
