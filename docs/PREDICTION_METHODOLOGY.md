# Prediction Methodology � Person-Specific Astro Engine

**Audience:** Clients and developers  
**Scope:** `F:\astro` / VPS `/opt/astro`  
**Production life-event path:** `runtime/event_predictor_v2.py` (+ orchestrator/PDF)  
**Related:** [ASTROLOGER_CLIENT_WORKFLOW.md](./ASTROLOGER_CLIENT_WORKFLOW.md), [ASTROLOGER_REPORT_FORMAT_WEB_RESEARCH.md](./ASTROLOGER_REPORT_FORMAT_WEB_RESEARCH.md), [WHY_WE_ARE_NOT_JUST_A_BOOK.md](./WHY_WE_ARE_NOT_JUST_A_BOOK.md), [ENGINE_PURPOSE_AND_ACTOR_EVENTS.md](./ENGINE_PURPOSE_AND_ACTOR_EVENTS.md), [AGE_POLICY_PHILOSOPHY.md](./AGE_POLICY_PHILOSOPHY.md), [MULTI_BOOK_SAME_CHART.md](./MULTI_BOOK_SAME_CHART.md)  
**Last reviewed:** 2026-06-02

---

## 1. Purpose

This document defines **how to predict honestly** for one birth chart: correct order of operations, house linkages, positive vs negative labeling, what �100% related to this person� means, accuracy limits, and known engine gaps.

**We do not guarantee events.** We compute **mechanical windows** from dasha + transits + house lords, optionally cross-checked with classical citations.

---

## 2. Correct order of operations (8 steps)

### Step 1 � Validate birth data (P0)

- Exact **date, time, place**, timezone (`birth.tz`, default IST 5.5).
- Wrong time ? wrong lagna ? all downstream output invalid.
- Flag disputed times (Rodden DD, etc.) in client-facing notes.

### Step 2 � Build mechanical chart

- **Source:** `engine/chart_builder.py`
- Lahiri ayanamsa, Placidus ascendant degree, **whole-sign houses** from lagna.
- Output: `lagna_idx`, `positions`, `janma_nakshatra`, divisionals as needed.

### Step 3 � Natal synthesis (human + future engine)

**Required intellectually; not fully automated today.**

- Lagna lord, Moon sign/house, karakas (Sun=father, Moon=mother, Jupiter=children, Venus=spouse).
- House lords table for **this** lagna (e.g. Sagittarius: 5L=Mars, 7L=Mercury, 9L=Sun, 11L=Venus).
- Yogas/doshas (`comprehensive_yogas`).
- Strength context (shadbala, SAV) � modifies how strong a promise is, not whether dasha runs.

### Step 4 � Dasha timeline

- Vimshottari MD?SD from Moon nakshatra (`granular_dasha.build_full_timeline`).
- Optional: Chara, D9 dasha for marriage (already in `event_marriage`).

### Step 5 � Transit triggers

- `transit_engine.detect_triggers` at sample dates (orb ~2.5�).
- Saturn/Mars/Rahu hits to karakas and house lords tighten windows.

### Step 6 � Category rules (life events)

- `scan_lifetime_v2`: for each sample day, run pattern library; score ? threshold ? candidate.
- `collapse_consecutive`: merge adjacent samples into **bands** (`window_start`, `window_end`).
- `rank_and_consume`: top-N per category for display.

### Step 7 � Classical citations (supporting, not timing)

- `engine/corpus.py` � planet-in-house, dasha, yoga text.
- **Must filter by native lagna** where rules are ascendant-specific (today: often not filtered � see �6).

### Step 8 � Label layer + honesty

- Tag each output: **mechanical** | **cited** | **synthesis** (`ENGINE_TRUTH_POLICY.md`).
- Attach `predicted_valence`: auspicious | inauspicious | neutral.
- State window width and sampling (10-day grid ? weeks�months precision, not days).

---

## 3. House linkage table (native-centric)

Events in **another person�s life** appear in the native�s chart via **derived houses** (count from native lagna). Timing uses **native�s dasha** when that house/lord activates.

| Life event (native perspective) | Primary houses | Karaka / lord | Derived / family logic |
|----------------------------------|----------------|---------------|-------------------------|
| **Own child born** | 5, 9 (putra), 11 (gains) | Jupiter, 5L | 7H spouse co-theme; 2H family line |
| **Spouse�s event** | 7, 7th-from-7th (1), 8 from 7 (2) | Venus, 7L | Marriage/partnership axis |
| **Father event / death** | 9, 10 (pitru), 8 (loss) | Sun, 9L, 8L | 9L MD + 8L/Saturn/Ketu AD ? loss bias |
| **Mother event / death** | 4, 8 from 4 (11) | Moon, 4L | Matra dosha + Moon/Sade Sati |
| **Marriage** | 7, 2 (family), 11 | Venus, 7L | D9, Upapada (Jaimini) |
| **Sibling born** (natal hint) | 3, 11 (elder) | Mars, 3L | Elder: 11H natal; timing: 3L/11L dasha |
| **Sibling marriage/death** | 3, 8 from 3 (10), 11 | 3L, 10L, 11L | `event_elder_sibling_*` |
| **Grandchild** | 9 (5th from 5th) | Jupiter, 9L | `event_grandchildren_birth` |
| **Father-in-law** | 3 (9th from 7) | 3L, Sun | `event_father_in_law_event` |
| **Mother-in-law** | 10 (4th from 7) | 10L, Moon | `event_mother_in_law_event` |
| **Maternal uncle** | 6 (3rd from 4) | 6L, 4L | Count from 4H |
| **Paternal uncle** | 11 (3rd from 9) | 11L, 9L | Count from 9H |
| **Wealth gain** | 2, 11 | 2L, 11L, Jupiter | |
| **Career peak** | 10, 11 | 10L, Sun | |
| **Health / accident** | 1, 6, 8 | Mars, Saturn, 6L/8L | |
| **Foreign travel** | 9, 12 | Rahu, 9L/12L | |

**Family ripple (correct methodology, not fully implemented):** When a **new baby** joins the family, the native�s chart should show **concurrent activation** of 5H (children theme), often 7H (spouse as co-parent), 11H (gains/fulfillment), sometimes 2H (family line) � **in the native�s dasha/transit window**, not as a generic `children` tag alone. **Vice versa** requires **linked charts** (spouse/child JSON) � not in engine today.

---

## 4. Positive vs negative labeling (valence rules)

### A. Production scorer (`runtime/_accuracy_scorer.py` + `engine/event_valence.py`)

**Strict mode** requires:

- Date within **�45 days** (�120 for year-only events)
- Severity ? 3
- **Valence match** when known event is clearly good/bad

**Valence inference:**

1. Explicit `predicted_valence` on band (preferred)
2. Category defaults: `marriage`, `children`, `wealth` ? auspicious; `health`, `wealth_loss`, `self_accident` ? inauspicious
3. Text keywords in known events (`died`, `award`, `married`, etc.)

### B. Pattern-level rules (`event_predictor_v2._pv`)

| Pattern behavior | Valence |
|------------------|---------|
| `event_child_birth` | Always **auspicious** |
| `event_marriage` (gates pass) | **auspicious** |
| `event_wealth_loss`, `event_self_accident` | **inauspicious** |
| `event_father` | **inauspicious** only if `9L MD + 8L/Saturn/Ketu/Mars AD`; else **neutral** |
| Most other ~191 patterns | **Unset** ? scorer uses category default or neutral |

### C. Client-facing rule

- Every period should offer **both lenses** when astrology allows: e.g. Ketu MD childhood ? spiritual sensitivity (**positive**) AND detachment/anxiety (**negative**), tied to **specific houses** (4H Ketu+Saturn for home stress).
- Do **not** label severity as good/bad � severity = **signal strength**.

---

## 5. �100% related to this person� vs misleading corpus

| Source | Person-specific? | Risk |
|--------|------------------|------|
| Lagna, houses, dasha dates | **Yes** � computed from birth | Low if birth data correct |
| `event_predictor_v2` house lords | **Yes** � `_lord(lagna_idx, h)` | Low |
| `engine/book_rules.py` triggers | **Yes** � evaluated on live chart | Medium � coverage gaps |
| `corpus.get_planet_in_house` | **Partial** � planet+house only | **High** � wrong-lagna quotes |
| `consensus_percent` (book battle) | **Placement agreement index** | **Misleading if called �probability�** |
| Declarative 402-category engine | Mixed � some generic templates | Medium |

**Rule for clients:** Never quote a corpus line without confirming it applies to **this lagna** or is universal.

---

## 6. Honest accuracy limits

| Metric | Value | Notes |
|--------|-------|-------|
| Loose hit rate | **82.7%** | �180 days, 16 celebrities |
| Strict hit rate | **75.6%** | �45 days + valence |
| Data audit | ~**68%** layers verified | Birth time conflicts in focus charts |
| Private clients (e.g. Manoj) | **No ground truth** | No `known_events` in chart JSON |

**Not promises:** Windows are **candidates**; many bands overlap; ranking hides lower windows.

---

## 7. Gap list (P0 / P1 / P2)

### P0

- Chart-profile synthesis step before timeline emission
- Corpus lagna / lordship filter
- Multi-chart family linking (ripple + vice versa)
- Single canonical birth source (`charts/*.json` vs `known_charts.py` drift)

### P1

- `house_links` + structured `cause_chain` on every event
- Full `predicted_valence` coverage; split ambiguous categories (`father_gain` / `father_loss`)
- Cross-house bundles for childbirth, marriage, death in family
- Add `known_events` + valence for private clients

### P2

- Align hybrid API with `event_predictor_v2` (or document two paths)
- Finer sampling / peak detection inside bands
- PyJHora cross-check on VPS

---

## 8. Worked example � Manoj (1996-05-25 20:25 Coimbatore)

### Natal snapshot

- **Lagna:** Sagittarius (Jupiter H1)
- **5L:** Mars (with Mercury in H5)
- **7L:** Mercury (Venus in H7)
- **9L / father:** Sun (H6)
- **4H:** Saturn+Ketu
- **Starting MD:** Ketu (Magha)

### Childhood 1996�1998

| Window | Category | Cause (summary) | Valence |
|--------|----------|-----------------|---------|
| 1996-05-06 ? 1997-07-02 | father | Pitra Dosha; Ketu MD?H4; Saturn return; Mars on Sun | neutral (not loss sub-rule) |
| ~1996-06 (hybrid) | health | General health sensitivity | inauspicious-leaning |
| ~1997 (hybrid) | wealth | Mahadhana Yoga | auspicious-leaning |

**Family-style:** `children` patterns do not fire before age 18. Elder-sibling natal signal needs Jupiter in 11H/3H � Manoj has Jupiter H1, so no elder-sibling natal hit.

---

## 9. Recommended code changes

1. **`house_links: list[int]`** on every `event_*` return (e.g. `children` ? `[5, 7, 9, 11]`).
2. **Corpus lagna filter** in `get_planet_in_house`.
3. **Default `predicted_valence`** via shared helper for all patterns.
4. **`chart_profile` dict** built once in `scan_lifetime_v2` and passed into patterns.
5. **Family ripple (design):** optional linked charts JSON + `derived_from_house` metadata.

---

## 10. References

| File | Role |
|------|------|
| `runtime/event_predictor_v2.py` | Life-event patterns |
| `runtime/_accuracy_scorer.py` | Loose/strict QA |
| `engine/event_valence.py` | Valence from text/category |
| `engine/chart_builder.py` | Sidereal chart |
| `docs/BACKEND_FOCUS.md` | Accuracy scorecard |
| `docs/DATA_ACCURACY_AUDIT.md` | Data honesty |
| `reports/jun 2026/2026-06-02/report/manoj/MANOJ_ENGINE_COMPARISON.md` | Manoj multi-engine |
| `charts/manoj_chart.json` | Canonical Manoj fixture |
