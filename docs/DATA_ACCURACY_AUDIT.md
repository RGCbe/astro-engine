# Astro Engine � Data Accuracy Audit

**Date:** 2026-06-02  
**Scope:** `F:\astro` (local) and `/opt/astro` (VPS) � **data layers only** (birth JSON, events, ephemeris settings, corpus). Prediction accuracy % is out of scope.  
**Auditor:** Automated + manual spot-check against public biographies (Wikipedia-level).

---

## Executive answer

**Is data 100% correct?** **No.**

| Layer | Sampled | Result |
|-------|---------|--------|
| Birth `charts/*.json` (5 focus celebs) | 5/5 | Dates & places match public records; **3/5** have birth-time conflicts with `engine/known_charts.py` |
| `known_events` in focus charts | ~45 events | **~93%** dates/categories plausible; 1 confirmed off-by-one (Sachin debut) |
| Mechanical lagna/planets vs stored JSON | 5/5 | **100%** match recompute (Swiss Ephemeris, same birth fields) |
| Whole-sign house assignments | 28/28 charts | **0** inconsistencies |
| Ephemeris files | VPS yes / local no | VPS **150** `.se1` files; **local `ephe/` missing** |
| Corpus `gemma_extractions/` | 82 JSON files | **0** load failures; **41** books ? 15,581 deduped rules; noise remains |
| PyJHora cross-check | 5 charts | **Blocked** � PyJHora repo absent on VPS |

**Estimated verification coverage:** ~**68%** of auditable data surface (deep event validation on all 28 charts and all corpus rules not done).

---

## 1. Birth / chart JSON (`charts/*.json`)

### Focus celebrities � biography cross-check

| Slug | Public DOB / place | Chart JSON | Verdict |
|------|-------------------|------------|---------|
| `mukesh_ambani` | 1957-04-19, Aden (Yemen) | Same; `tz: 3.0`, 06:56, lat/lon Aden | **Date/place OK.** `tz=3` is **correct for Aden** (not IST). Time is one of several circulating chart times (06:56 vs 11:30 vs 19:53 in astrology sites). |
| `mahatma_gandhi` | 1869-10-02, Porbandar | Same; `tz: 4.62` (LMT-style), 07:33 | **Date/place OK.** Time 07:33 documented in chart note; Astrodienst often cites 07:11. |
| `indira_gandhi` | 1917-11-19, Allahabad | Same; `tz: 5.5`, 23:11 | **OK** (Rodden B / KP sources). |
| `narendra_modi` | 1950-09-17, Vadnagar | Same; `tz: 5.5`, 11:00 | **Date/place OK.** `rodden_rating: DD` � time disputed (11:00 vs 9:35). Data uncertainty, not a silent bug. |
| `sachin_tendulkar` | 1973-04-24, Mumbai | Same; `tz: 5.5`, 13:00 | **Date/place OK.** Chart documents 13:00 (doctor interview); other sources use 17:25 / 14:25. |

### P0 � Dual source of truth (`charts/*.json` vs `engine/known_charts.py`)

The runtime/API uses **`charts/*_chart.json`**. Backtests and `cross_check_known_charts()` use **`known_charts.py`**. They **diverge** for three focus charts:

| Name | `charts/*.json` time | `known_charts.py` time | Lagna if using `known_charts` time |
|------|---------------------|------------------------|-----------------------------------|
| Sachin Tendulkar | **13:00** | **17:25** | Cancer ? **Virgo** |
| Mukesh Ambani | **06:56** | **11:30** | Aries ? **Gemini** |
| Mahatma Gandhi | **07:33** (tz 4.62) | **07:11** (tz 4.85) | Libra (same sign, ~5� lagna shift) |

Indira and Modi: birth fields **aligned** between both sources.

### Mukesh `tz=3` � not an IST error

Born in **Aden** (then British Aden, UTC+3). Using IST (5.5) would be **wrong** for birthplace. The chart correctly uses **3.0** for local civil time conversion.

### Placeholder birth dates

No `YYYY-01-01` birth dates in `charts/`. (`hrithik_roshan` uses Jan **10**, not Jan 1.)

### Lagna / positions internal consistency

- Recomputed lagna for all 5 focus charts from stored `birth` fields: **all match** `lagna_idx` / `lagna_deg` within 0.01�.
- All **28** charts: whole-sign `house` = f(`rasi_idx`, `lagna_idx`) � **0** mismatches.

---

## 2. `known_events` in chart JSONs

### Focus charts � spot-check (Wikipedia-level)

| Chart | Spot-check result |
|-------|-------------------|
| Gandhi | Salt March 1930-03-12, independence 1947-08-15, assassination 1948-01-30 � **OK** |
| Indira | PM 1966-01-24, Emergency 1975-06-25, assassination 1984-10-31 � **OK** |
| Modi | PM 2014-05-26, 2019-05-30, 2024-06-09 � **OK** |
| Mukesh | Marriage 1985-03-08, father death 2002-07-06, Jio 2016-09-05 � **OK** |
| Sachin | Marriage 1995-05-24, World Cup 2011-04-02, Bharat Ratna 2014-02-04 � **OK** |

### P1 � Confirmed / likely event issues

| Severity | Chart | Issue |
|----------|-------|-------|
| P1 | `sachin_tendulkar` | Test debut listed **1989-11-15**; widely recorded as **1989-11-16** (Karachi) |
| P1 | Multiple (non-focus) | **Placeholder month/day**: `ar_rahman` (6�), `rekha` (3�), `amitabh_bachchan`, `aishwarya_rai`, `virat_kohli` use `YYYY-01-01` for events |
| P2 | `narendra_modi` | Godhra 2002-02-27 event text mixes fact with interpretive framing � categorization/tone for ML, not wrong date |
| P2 | Focus set | Events lack structured `event_type` (free-text only) � harder to validate vs `known_charts.LifeEvent` vocabulary |

---

## 3. Ephemeris / settings

| Setting | Location | Value |
|---------|----------|-------|
| **Ayanamsa** | `chart_builder.py`, `main.py`, `engine/chart.py` | **Lahiri** (`swe.SIDM_LAHIRI`) for chart JSON pipeline |
| **Ayanamsa (full engine)** | `engine/chart.py` + `ayanamsa_picker` | Auto-pick; default Lahiri; LMT option for India |
| **House system** | `chart_builder.build_sidereal_chart` | Placidus (`b"P"`) for **ascendant degree only**; **whole-sign** houses from lagna |
| **Default TZ** | `chart_builder.DEFAULT_TZ_HOURS` | **5.5** (IST); per-chart `birth.tz` overrides |

### Ephemeris directory

| Environment | `ephe/` | Notes |
|-------------|---------|-------|
| **VPS** `/opt/astro/ephe` | **Present** (~150 `.se1` files) | Swiss Ephemeris usable in production |
| **Local** `F:\astro\ephe` | **Missing** | `run_engine_tests.ps1` notes need for `ephe/`; dev parity gap |

### PyJHora mechanical cross-check

```
PYTHONPATH=/opt/astro ./venv/bin/python engine/cross_check.py --n 5
? PyJHora not found at /opt/astro/_research/repos/PyJHora/src
```

Independent recompute (local, `chart_builder`) vs stored JSON: **5/5 PASS**.

---

## 4. Corpus (`gemma_extractions/`, `engine/corpus.py`)

| Metric | Value |
|--------|-------|
| JSON files | 82 |
| JSON parse failures | **0** |
| Empty `rules` / no chunks (filename list) | **54** shallow `*_gemma.json` stubs (excluded or empty) |
| Loaded books (after `EXCLUDED_BOOKS`) | **41** |
| Raw rules collected | 17,066 |
| Junk filtered at load | 0 (filter runs on text patterns) |
| Duplicates merged | 1,485 |
| **Unique rules** | **15,581** |
| Raw OCR-ish phrases (pre-dedup scan) | ~608 hits on "unable to interpret" / "corrupted" |
| Very short rules (<20 chars, raw scan) | ~1,912 |

**Health:** Corpus **loads and indexes**; dedup works. **P2** quality debt: empty stub files, OCR fragments in source JSONs (corpus filters some at query time via `_OCR_JUNK`), uneven book depth (`Brihat_Jataka_deep`: 24 rules vs `KP_Reader_3_Predictive_deep`: 2,166).

---

## 5. Issues table (severity)

| ID | Sev | Layer | Issue |
|----|-----|-------|-------|
| D-01 | **P0** | Birth | `known_charts.py` birth **times** disagree with `charts/*.json` for Sachin, Mukesh, Gandhi ? backtest/cross-check use wrong chart |
| D-02 | **P0** | Governance | Two canonical birth sources with no sync test in CI |
| D-03 | **P1** | Events | `YYYY-01-01` placeholder dates in 5 chart JSONs (Rahman, Rekha, Amitabh, Aishwarya, Virat) |
| D-04 | **P1** | Events | Sachin test debut date off by one day |
| D-05 | **P1** | Infra | Local `ephe/` missing � local Swiss Ephemeris parity unverified |
| D-06 | **P1** | Validation | PyJHora removed from VPS � external mechanical oracle unavailable |
| D-07 | **P2** | Birth | Modi Rodden **DD** � birth time disputed; must stay flagged in API/docs |
| D-08 | **P2** | Corpus | 54 empty/stub gemma files; ~608 OCR-junk strings in raw extractions |
| D-09 | **P2** | Events | Free-text `known_events` vs typed `LifeEvent` in `known_charts.py` � schema drift |

**Not issues:** Mukesh `tz=3` for Aden; Gandhi/Indira dates; house math on stored charts.

---

## 6. Recommended fixes (priority)

1. **P0 � Single source of truth:** Pick `charts/*.json` OR `known_charts.py`; generate the other at build time. Immediate: align Sachin (13:00 vs 17:25), Mukesh (06:56 vs 11:30), Gandhi (07:33/4.62 vs 07:11/4.85).
2. **P0 � CI guard:** Test that `known_charts` birthdata matches `charts/{slug}_chart.json` for every slug in accuracy scorer list.
3. **P1 � Events:** Replace `YYYY-01-01` with researched dates or drop events; fix Sachin debut to 1989-11-16.
4. **P1 � Local dev:** Copy or symlink VPS `ephe/` to `F:\astro\ephe` (document in README).
5. **P1 � Optional:** Restore PyJHora under `ATRO_PYJHORA_PATH` or document recompute-only validation.
6. **P2 � Corpus:** Re-extract or exclude empty `*_gemma.json` stubs; tighten OCR junk filter counts in CI.

---

## 7. Mechanical cross-check summary

| Method | Result |
|--------|--------|
| Recompute lagna/planets from `birth` (local `chart_builder`) | **5/5 match** stored JSON |
| Whole-sign houses | **28/28 consistent** |
| PyJHora (VPS) | **Not run** (repo missing) |

**Conclusion:** Stored chart **positions are internally consistent** with the birth fields in each JSON file. Uncertainty is **which birth time is canonical**, not broken ephemeris math on the stored values.

---

## Resolved (2026-06-02)

Canonical test-subject dataset established. See **[TEST_SUBJECTS_CANONICAL.md](./TEST_SUBJECTS_CANONICAL.md)** for full tables.

| Issue ID | Resolution |
|----------|------------|
| D-01 | **Fixed** � `known_charts.py` synced to `charts/*.json` for 12 overlapping celebrities; disputed trio kept chart values (Sachin 13:00, Mukesh 06:56, Gandhi 07:33/4.62) |
| D-02 | **Mitigated** � `scratch/apply_canonical_test_subjects.py` + compare script; CI guard still recommended |
| D-03 | **Fixed** � 11 placeholder event dates replaced; Rahman Islam conversion tagged `date_precision: year` |
| D-04 | **Fixed** � Sachin Test debut ? 1989-11-16 (first batting day) |

---

## Appendix � Commands used

```powershell
cd F:\astro
python scratch\_data_audit_recompute.py
python scratch\_compare_known_charts.py
```

```bash
ssh root@46.28.44.225 "ls /opt/astro/ephe/*.se1 | wc -l"
ssh root@46.28.44.225 "cd /opt/astro && PYTHONPATH=/opt/astro ./venv/bin/python engine/cross_check.py --n 5"
```
