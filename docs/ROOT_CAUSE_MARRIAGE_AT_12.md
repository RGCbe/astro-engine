# Root Cause: Marriage Band at Age ~12 (Manoj Chart)

**Chart:** `charts/manoj_chart.json` � birth 1996-05-25 20:25 Coimbatore, Sagittarius lagna  
**Bad band (pre age-policy filter):** 2008-06-03 ? 2011-07-02, category `marriage`, age ~12�15  
**Debug script:** `scratch/_debug_marriage_2008.py`  
**Run output:** `scratch/_debug_marriage_2008_out.txt`

---

## Executive verdict

**Not a calculation bug (A).** Dasha dates, house lords, and transits are correct.  
**Primary cause: B + C � rule correctly fires, product mislabels childhood Venus dasha as marriage.**

`event_marriage` scores Venus MD + Jupiter AD (valid BPHS Ch. 80 marriage karaka stack). During Manoj�s **Venus mahadasha (1997-07-11 ? 2017-07-11)**, Jupiter antardasha (~2008�2011) triggers that stack continuously. At age 12 this is astrologically �kalatra karaka activation,� not literal marriage. The bad band appears when the marriage age gate allows scoring below 18; the age-policy filter is a second-line defense, not a substitute for the rule gate.

**Not D (saham false positive)** for the 2008 band � `event_saham_kalatra` fires from age 15+ only (2011-05-31+), separate window.

---

## Exact function that fired (simulated with age gate ?12)

| Field | Value at **2008-06-03** |
|-------|-------------------------|
| Age | 12.02 |
| MD / AD / PD | **Venus / Jupiter / Saturn** |
| Function | `event_marriage` (`event_predictor_v2.py` ~210�458) |
| Category | `marriage` |
| Severity | 3 |
| Score drivers | Venus MD (primary +2), Jupiter AD karaka (secondary +1) |
| Gates | 1 gate fail ? D9 7L (Mars) in dusthana H6 (severity not reduced to None) |

### `why[]` at 2008-06-03

```
Venus MD
Jupiter AD (karaka)
? D9 7L (Mars) in dusthana H6
```

### Collapsed band (age gate ?12 simulation)

Re-running `scan_year_v2` with `event_marriage` allowed from age 12 reproduces:

```
2008-05-30 ? 2011-04-21  age 12.0  sev 3  cat=marriage
  why: Venus MD, Jupiter AD (karaka), ? D9 7L (Mars) in dusthana H6
```

Matches reported band **2008-06-03 ? 2011-07-02** within sampling/collapse tolerance (`sample_days=10`, Jupiter AD ? Saturn AD handoff mid-2011).

---

## What does **not** fire (current code, age 12)

With **current** `if age < 18: return None` at line 217:

| Function | 2008-06-03 | Notes |
|----------|------------|-------|
| `event_marriage` | **None** | Blocked by age gate |
| `event_marriage_arranged` | None | `age < 18` |
| `event_marriage_love` | None | `age < 18` |
| `event_engagement` | None | `age < 18` |
| `event_saham_kalatra` | None | `age_guard (15, 75)` in catalog |
| `event_first_love` | None | `age < 14` |

No `marriage`-category hits in `ALL_PATTERNS_V2` at age 12 with current gates.

---

## Dasha context (calculation verified)

| Period | Span | Manoj age |
|--------|------|-----------|
| Venus MD | 1997-07-11 ? 2017-07-11 | 1.1 ? 21.1 |
| Jupiter AD (within Venus MD) | ~2008 ? ~2011 | ~12 ? ~15 |
| Saturn AD (within Venus MD) | ~2011-07 ? ~2014 | ~15 ? ~18 |

7L = **Mercury** (Gemini = 7th from Sagittarius). Natal **Venus in H7** � strong promise gate, so classical gates do not suppress the signal.

---

## Classification matrix

| Option | Verdict | Evidence |
|--------|---------|----------|
| **A Calculation bug** | ? No | `granular_dasha` Venus MD / Jupiter AD dates align with birth; 7L = Mercury correct for Sag lagna |
| **B Rule too loose** | ? Yes | Venus MD + Jupiter AD alone reach threshold 3 with primary; no age-aware scoring split |
| **C Correct rule, wrong product** | ? Yes | Same stack = �social/kalatra ripening� in childhood Venus MD, not marriage event |
| **D Saham false positive** | ? No (for 2008 band) | `saham_kalatra` starts 2011-05-31 at age 15; different mechanism |

---

## Recommended fix (specific)

### 1. Rule layer � **keep age gate 18** (already in code)

```python
# event_predictor_v2.py line 217
if age < 18 or age > 75: return None
```

Docstring updated to match (was incorrectly �Age 12-75�). Do **not** rely on filter-only removal.

### 2. Age policy layer � **keep as-is**

`engine/event_age_policy.py`:

- `marriage*`: `absurd_min=12`, `early_allow_age=16`, `typical_min=18`
- Age 12 + sev 3 ? `unlikely` (filtered)
- Age 16+ ? `early_exception` even at sev 2

Filter is backup for any pattern that slips through (e.g. declarative catalog slugs, future refactors).

### 3. Optional product split (future, not required for this fix)

For ages 14�17 during Venus MD, consider routing to `first_love` / `social_attraction` instead of `marriage` � aligns with category catalog `event_first_love` (`age_guard (13, 28)`).

### 4. Report domain mapping

`saham_kalatra` and `first_love` are grouped under marriage **domain** in timeline reports (`DOMAIN_MAP`) but are not `category=marriage`. Do not treat domain grouping as proof that `event_marriage` fired.

---

## Code references

| Item | Location |
|------|----------|
| Marriage scorer + age gate | `runtime/event_predictor_v2.py` `event_marriage` L210�458 |
| Age policy | `engine/event_age_policy.py` `CATEGORY_AGE_RULES` marriage* |
| Saham kalatra (declarative) | `runtime/category_catalog.py` `event_saham_kalatra` age_guard `(15, 75)` |
| Domain ? marriage bucket | `scratch/_manoj_timeline_gen.py` `DOMAIN_MAP["marriage"]` |

---

## Reproduce

```powershell
cd F:\astro\scratch
python _debug_marriage_2008.py
```

Age-gate simulation (shows historical bad band):

```python
# Patch event_marriage age check to >= 12, re-run scan_year_v2 2008-2011
# ? band 2008-05-30 ? 2011-04-21, cat=marriage, why=Venus MD + Jupiter AD
```

---

## Final recommendation

| Layer | Action |
|-------|--------|
| **Verdict** | Fix **rule + product labeling**, not calculation |
| **Rule** | Keep `age < 18` hard return in `event_marriage` (and siblings `event_engagement`, `event_marriage_*`) |
| **Filter** | Keep `filter_bands_for_age` as safety net |
| **Docs** | Docstring aligned 2026-06-02 |

No ephemeris or dasha recalculation required.
