# Backend-only sprint (until engine max)

**Paused:** Frontend, marketing UI, numerology fusion in jathagam, Vijay calibrated weights in API.

**Active:** Mechanical truth, `event_predictor_v2`, integration + accuracy gates, VPS deploy after each batch.

---

## Current scorecard (VPS 2026-06-02, Wave B2 deploy)

| Metric | Value | Target |
|--------|-------|--------|
| Integration | PASS (262s, 4/4 charts) | Always PASS |
| Accuracy loose (+/-180d) | **82.7%** (105/127) | >= 80%, no regression |
| Accuracy strict (+/-45d + valence) | **75.6%** (96/127) | >= 72% (met) then >= 78% |
| Weakest strict | Mukesh 38%, Gandhi 56%, Lata 56% | Each >= 50% |
| Weakest loose | Gandhi 56%, Mukesh 50% | Each >= 60% |

### Focus celebrities (loose / strict)

| Celebrity | Loose | Strict (was 67.7% grand) |
|-----------|-------|--------------------------|
| Indira Gandhi | 71.4% (5/7) | **71.4%** (was 29%) |
| Mahatma Gandhi | 55.6% (5/9) | **55.6%** (was 33%) |
| Mukesh Ambani | 50.0% (4/8) | 37.5% (3/8) |

---

## Work order (do not skip levels)

### Wave A - Scoring and data honesty (done)

- max_sev strict scoring, political_office, CAT_ALIASES, valence keywords.

**Result:** strict 65.4% -> 67.7%; Modi strict 100%.

### Wave B - Rule gaps (done)

- Father, travel, children, death, wealth/property rules.

### Wave B2 - Strict valence fix (done)

- Severity = signal strength (>=3), not good/bad.
- Category-based `predicted_valence`; `wealth_loss` category split.
- Deployed VPS 2026-06-02.

**Result:** strict **67.7% -> 75.6%** (+7.9pp); loose **80.3% -> 82.7%**.

**Exit:** strict >= 72% � **PASSED**.

### Wave: Data audit (2026-06-02)

Full report: [DATA_ACCURACY_AUDIT.md](./DATA_ACCURACY_AUDIT.md)

**Verdict:** Data is **not** 100% correct (~68% of layers spot-audited).

| Priority | Issue |
|----------|-------|
| P0 | `charts/*.json` vs `engine/known_charts.py` birth-time drift (Sachin 13:00 vs 17:25, Mukesh 06:56 vs 11:30, Gandhi 07:33 vs 07:11) |
| P1 | Placeholder event dates `YYYY-01-01` in Rahman/Rekha/Amitabh/Aishwarya/Virat charts |
| P1 | Local `ephe/` missing; VPS has 150 ephemeris files |
| P1 | Sachin test debut off by one day (1989-11-15 vs 16) |
| P2 | PyJHora absent on VPS; corpus OCR stubs |

**Mechanical:** Stored lagna matches recompute from JSON birth fields (5/5 focus charts). Mukesh `tz=3` for Aden is **correct** (not IST).

### Wave C - Next

- **Data:** Sync `known_charts.py` to `charts/*.json`; CI birth parity test.
- Gandhi travel windows (1888, 1893, 1915) strict timing.
- Mukesh marriage/wealth strict (37.5%).
- Indira children 1944/1946 strict.
- `truth.partial_failures`, jathagam latency, PyJHora cross-check (or document recompute-only).

### Wave D - Hold-out only

- No Vijay weights in `main.py`.

---

## Commands every backend batch

```bash
cd /opt/astro
./venv/bin/python test_full_integration.py
./venv/bin/python runtime/_accuracy_scorer.py
./venv/bin/python runtime/_accuracy_scorer.py --strict
pm2 restart astro-engine
```

Local: `powershell -File F:\astro\run_engine_tests.ps1` (needs `ephe/`).

---

## Regression rule

Block deploy if integration fails OR loose accuracy drops **>3pp** OR strict drops **>2pp** after a rules change.

**Reports layout:** Generated PDFs/JSON live under `reports/` subfolders (`manoj/`, `accuracy/`, `clients/`, �). Mirror the same tree on VPS at `/opt/astro/reports/` on next deploy � see `reports/README.md`.

---

## Not in scope (backend sprint)

- Frontend pages, Stripe, ads
- `scratch/optimize_*` in production API
- Public accuracy percentage marketing
