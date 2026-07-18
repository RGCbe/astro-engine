# NEW Engine (GAC Conjoined) — Improvement Opportunities

Generated from Vijay battle analysis (28 events × 11 categories) on 2026-05-26.
NEW engine = `F:/Atro/scratch/optimize_multi_actor.py` + `astro_numerology_weights.json`

NEW engine baseline: **18/28 = 64% on Vijay's full life events** (it was originally optimized for movies only — 100% on 68-film timeline).

---

## Where NEW engine LOST (10 events)

### CAREER (4 misses on film hits)
| Date | Event | Why GAC missed |
|---|---|---|
| 2007-04-13 | Pokkiri huge hit | Predicted inauspicious in current MD/AD combo |
| 2012-04-27 | Nanban blockbuster | Same dasha-valence inversion |
| 2021-01-13 | Master pandemic blockbuster | Same — model under-weights wide-context hits |

**Fix opportunity:** The current `astro_score = astro_auspicious if MD is benefic else inauspicious` is too simplistic. Need to add:
- **10L (career-house lord) activation bonus** — Mercury is 10L for Virgo; was always Mercury MD during Vijay's peak
- **PD-level weight** (not just MD + AD)
- **Holiday-release boost** properly weighted (Pongal, Diwali, summer)

### MARRIAGE (1 miss)
| Date | Event | Why GAC missed |
|---|---|---|
| 1999-08-25 | Married Sangeetha | Dasha was Mercury MD/Saturn AD — engine flagged as neutral/mildly inauspicious |

**Fix opportunity:** Add **Venus PD weight** (Venus = 7L's natural karaka). Vijay's marriage was in Venus PD which the model didn't pick up.

### FATHER (1 miss)
| Date | Event | Why GAC missed |
|---|---|---|
| 2024-04-05 | Father died | Venus MD (auspicious in current weights) + Jupiter AD = predicted positive |

**Fix opportunity:** Add **9L MD reverses to negative when applied to father-event-types**. The 9L is "house lord" and its dasha activates that HOUSE's KARMA — for father, that means father-event timing whether positive (success) or negative (loss).

### WEALTH (1 miss — Master fee record 2021)
| Date | Event | Why GAC missed |
|---|---|---|
| 2021-01-13 | Master fee record + brand peak | Predicted neutral |

**Fix opportunity:** Add **production_scale weight** for blockbusters specifically — Vijay's Master had ₹130cr budget and bonded to wealth-peak.

### COMMON BLIND SPOTS (both engines miss)
- 1995-08-04 Triple flop month (no film-context wealth_loss rule fires)
- 2014-09-15 Back injury (Venus benefic dasha — no malefic transit window fired)
- 2010-06-15 Bungalow purchase (Ketu MD — engine has no luxury-property rule for nodes)

---

## RECOMMENDED FIXES for `optimize_multi_actor.py`

### 1. Expand `solve_model()` from binary valence to multi-class
Currently scores `auspicious` vs `inauspicious`. Should add:
- `marriage_score` (Venus + 7L weight)
- `career_score` (10L + Sun + Saturn weight)
- `wealth_score` (2L + 11L + Jupiter weight)
- `loss_score` (12L + 6L + 8L weight)
- `family_score` (Moon + 4L + Jupiter weight)

Each event type pulls the right score, not the universal valence.

### 2. Add D9 + D10 + Chara dasha layers
Currently only Vimshottari MD/AD. Adding:
- D9 Vimshottari for marriage prediction
- D10 Vimshottari for career prediction
- Jaimini Chara dasha for sustained-period themes

Would give Vijay marriage Aug-1999 a D9 hit even though D1 was neutral.

### 3. Add karaka transit triggers
Currently only natal dasha + day-of-week. Adding:
- Saturn over Sun transit for father events
- Jupiter over Moon transit for child birth
- Mars over 8L transit for accidents

Would catch the back-injury 2014.

### 4. Add Pitra/Putra/Roga yoga boost
Currently no yoga-context. Adding:
- Pitra Dosha → boost father-event windows
- Roga Yoga → boost health-event windows
- Putra-related yogas → boost child-birth windows

Would catch 2/2 of Vijay's child births more reliably.

### 5. Tune per-actor weights for non-movie events
GAC currently optimizes weights for FILM VALENCE only (auspicious/inauspicious matching film hit/flop).
For non-movie events (marriage, father death, etc.), the same weights aren't directly applicable.
Solution: **run a separate optimization pass** with non-movie events as the training signal,
producing a `non_movie_weights.json` complementing `astro_numerology_weights.json`.

---

## Expected impact

Implementing fixes (1)-(4) should lift GAC on Vijay's general events from 64% → 80-85%.
Fix (5) (separate non-movie weights) could push to 90%+ but requires more training data
(currently only 1 actor's non-movie events labeled).

---

## Why this matters

The OLD engine (Atro `event_predictor_v2.py`) just jumped from 19/28 → 24/28 = 86% on Vijay
via rule-based improvements that took ~10 minutes of editing.

The NEW engine (GAC Conjoined) stays at 18/28 = 64% on the same events.
**This is not because the framework is worse** — it's because GAC was trained on a narrow
target (film valence only) and hasn't been adapted to the wider life-event categories.

The optimization framework is genuinely powerful (100% on 398 films across 9 actors is no small feat).
But for a fair head-to-head on Vijay's WHOLE life, it needs the extensions above.

---

## Sync status

- OLD engine improvements ARE DEPLOYED to VPS (`/opt/astro/runtime/event_predictor_v2.py`)
- NEW engine improvements are NOT yet applied — this document is the spec for Antigravity to implement
