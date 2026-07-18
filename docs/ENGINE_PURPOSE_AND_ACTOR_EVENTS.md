# Engine Purpose and Actor Life Events

**Audience:** Product + developers  
**Related:** [PREDICTION_METHODOLOGY.md](./PREDICTION_METHODOLOGY.md), [TEST_SUBJECTS_CANONICAL.md](./TEST_SUBJECTS_CANONICAL.md), [WHY_WE_ARE_NOT_JUST_A_BOOK.md](./WHY_WE_ARE_NOT_JUST_A_BOOK.md), [ASTRO_FULL_EVENT_CATALOG.md](./ASTRO_FULL_EVENT_CATALOG.md)  
**Last reviewed:** 2026-06-02

---

## 1. What this engine is for

The production timing path (`runtime/event_predictor_v2.py`) emits **dated windows** (dasha + transits + yogas) tagged by life category. Success means matching **real documented events** in `charts/<slug>_chart.json` ? `known_events`, not generic book themes.

**Flagship example (actors):** After cataloguing lifetime events (Step 0), predict **next movie release timing** and coarse **outcome** (hit / flop / average) for one chart � then verify against filmography dates.

This is **internal QA + client timing bands**, not guaranteed box office.

---

## 2. Step 0 � Know events before predicting

| Step | Action |
|------|--------|
| 0 | Build **lifetime event list** (releases, debut, awards, marriage, health, politics, family) with **exact or month-level dates** |
| 1 | Tag each: `event_type`, `atro_category`, valence (hit/flop), major vs minor |
| 2 | Run `scan_lifetime_v2` ? compare bands to known_events (loose �180d, strict �45d + valence) |
| 3 | Only then market �predict next release� |

Without Step 0, the engine only matches vague **career** windows � same as reading a textbook.

---

## 3. Actor inventory (charts with `known_events`)

| Slug | Film-focus | `#events` | In 16-celebrity scorer? |
|------|------------|-----------|-------------------------|
| **joseph_vijay** | Highest (releases, hit/flop, politics) | **26** | No (best worked example) |
| **rajinikanth** | ~92% film | 12 | No |
| aamir_khan | ~83% film | 12 | No |
| kamal_haasan | ~82% film | 11 | No |
| salman_khan | releases + legal | 11 | No |
| shah_rukh_khan | ~30% film in 10 events | 10 | Yes |
| amitabh_bachchan | film/TV/ABCL/politics | 9 | Yes |
| rekha | debut/awards/films | 9 | Yes |
| aishwarya_rai | pageant + films | 8 | Yes |

**SSOT:** `charts/*.json` (not coarse rows in `known_charts.py` alone).

**Worked example:** `joseph_vijay` � 26 dated events from child debut through *GOAT* (2024), TVK party, father death.  
**Shortlist pick (your examples):** `rajinikanth` if you want fewer, purer film rows.

---

## 4. Event taxonomy � real life ? engine

| Real-life event | v2 category today | Ground truth in JSON? |
|-----------------|-------------------|------------------------|
| Film debut / lead debut | `career` (breakthrough) | Partial |
| **Movie release date** | **None** � scorer maps `\bfilm\b` ? `career` | Partial (strong for Vijay/Rajini) |
| Blockbuster / hit | `career`, `fame_peak`, `wealth` | Keywords in text |
| Flop | `wealth_loss`, `fame_loss` | Vijay, Salman, etc. |
| National / Filmfare award | `honor` | Yes |
| Set injury | `health_self`, `self_accident` | Amitabh Coolie |
| Marriage / children | `marriage`, `children` | Yes |
| Political party / office | `political_office`, `spirituality` | Kamal, Vijay, Amitabh |
| **Next release (future)** | � | **Not in charts** � prediction target |

**There is no `movie_release` or `film_outcome` category in `event_predictor_v2` today.**

---

## 5. Joseph Vijay � sample lifetime events (Step 0)

Birth: 1974-06-22 12:00, Chennai (Rodden B). Source: `charts/joseph_vijay_chart.json`.

| Date | Event | Cat |
|------|-------|-----|
| 1984-09-21 | Child actor debut *Vetri* | career |
| 1992-12-04 | Lead debut *Naalaiya Theerpu* (flop) | career |
| 1993-12-24 | First hit *Sendhoorapandi* | career |
| 1996-02-15 | Breakthrough *Poove Unakkaga* | career |
| 1999-08-25 | Marriage | marriage |
| 2000-08-01 | Son born | children |
| 2007-04-13 | *Pokkiri* | career |
| 2014-09-15 | Back injury *Kaththi* | health |
| 2021-01-13 | *Master* blockbuster | career |
| 2022-04-13 | *Beast* flop | career / loss |
| 2023-10-19 | *Leo* biggest hit | career |
| 2024-09-05 | *GOAT* release | career |
| 2024-02-02 | Founded TVK party | political |
| 2024-04-05 | Father died | father |

Full list: 26 rows in chart JSON.

---

## 6. What we need for �next release + result�

1. **`movie_release` + `film_outcome`** (or `box_office_peak` / `box_office_flop`) in `event_predictor_v2` + `_accuracy_scorer.py` aliases  
2. **Filmography ingest** � title, release date, collections ? `known_events`  
3. **Expand scorer** to Rajini, Kamal, Vijay, Salman, Aamir, Hrithik  
4. **Film-only eval** � strict �45d + hit/flop valence, separate from generic career  
5. **Entertainment-tuned rules** � D10, Venus, 5H/10H (optional; after categories exist)

---

## 7. P0 backlog (ordered)

1. Step 0 pipeline for all test actors (film + life)  
2. New film categories in predictor + scorer  
3. Add Vijay/Rajini/etc. to `CELEBRITIES` in `_accuracy_scorer.py`  
4. Film-only accuracy report (`reports/accuracy/` dated folder)  
5. Client deliverable: �next release window� only after film hit rate is documented  

---

## 8. Commands

```bash
cd F:\astro\runtime
python _accuracy_scorer.py
python _accuracy_scorer.py --strict
```

After adding slugs to `CELEBRITIES`, score one actor:

```python
from _accuracy_scorer import score_celebrity
print(score_celebrity("joseph_vijay"))
```

Filter film rows: known text matching `released|debut|film` vs predicted `career`, `fame_peak`, `wealth_loss`.
