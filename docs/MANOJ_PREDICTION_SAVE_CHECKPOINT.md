# Manoj prediction work � save checkpoint (2026-06-02)

All files below are on disk under `F:\astro`. Regenerate with the commands listed.

---

## Engine-only confirmation (main flow)

**Module:** `engine/engine_topic_confirm.py`  
**Script:** `scratch/manoj_engine_confirmed.py`  
**Report:** `reports/jun 2026/2026-06-02/report/manoj/MANOJ_ENGINE_CONFIRMED.md`

```powershell
cd F:\astro
python scratch/manoj_engine_confirmed.py
```

5 layers: chart + dasha + timing bands + placement rules + book consensus.  
Verdicts: **CONFIRMED** / **MIXED** / **NOT CONFIRMED** (no "possible/likely").

---

## Per-book + tables

| File | Purpose |
|------|---------|
| `engine/per_book_predictions.py` | Per-book rules, tables, strict placement filter |
| `scratch/manoj_per_book_predictions.py` | Generate EN + TABLE reports |
| `reports/.../MANOJ_PER_BOOK_PREDICTIONS_TABLE.md` | Table view |
| `reports/.../MANOJ_PER_BOOK_PREDICTIONS_EN.md` | Tables + citations |

```powershell
python scratch/manoj_per_book_predictions.py --format both
python scratch/manoj_per_book_predictions.py --format table
```

---

## Summary prediction (narrative)

`reports/.../MANOJ_PREDICTIONS_SUMMARY.md` � age 30 narrative (older style).

---

## Optional life-facts cross-check (not required for engine confirm)

| File | Purpose |
|------|---------|
| `charts/manoj_life_facts.json` | Template for real-life yes/no (optional) |
| `engine/prediction_confirm.py` | Compare engine vs facts |
| `scratch/manoj_confirmed_predictions.py` | `MANOJ_PREDICTIONS_CONFIRMED.md` |

---

## Chart + Part 1 jathagam

| File | Purpose |
|------|---------|
| `charts/manoj_chart.json` | Thirukanitham chart fixture |
| `reports/.../MANOJ_JATHAGAM_GENERATED_TA.md` | 13-page jathagam |
| `engine/lagna_filter.py` | Sanskrit lagna names in corpus filter |

```powershell
python scratch/rebuild_client_chart.py charts/manoj_chart.json
```

---

## Manoj engine CONFIRMED snapshot (2026-06-02)

| Topic | Verdict | Layers |
|-------|---------|--------|
| Education | CONFIRMED | 4/5 |
| Career | CONFIRMED | 4/5 |
| Health | CONFIRMED | 5/5 |
| Marriage | CONFIRMED | 4/5 |
| Siblings | MIXED | 3/5 |

Dasha: Moon MD, Moon-Jupiter AD/PD (Jun 2026).

---

## Git

`F:\astro` is **not** a git repository. To version this work:

```powershell
cd F:\astro
git init
git add engine/engine_topic_confirm.py engine/per_book_predictions.py engine/prediction_confirm.py engine/lagna_filter.py scratch/manoj_engine_confirmed.py scratch/manoj_per_book_predictions.py scratch/manoj_confirmed_predictions.py charts/manoj_life_facts.json docs/MANOJ_PREDICTION_SAVE_CHECKPOINT.md
git commit -m "Add engine-only topic confirmation and per-book prediction reports for Manoj."
```

(Add `reports/` paths if you want reports in git.)
