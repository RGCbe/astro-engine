# One Chart Math, Many Book Opinions

**Audience:** Clients and developers  
**Related:** [CORPUS_QUALITY_AUDIT.md](./CORPUS_QUALITY_AUDIT.md), [WHY_WE_ARE_NOT_JUST_A_BOOK.md](./WHY_WE_ARE_NOT_JUST_A_BOOK.md), [ROOT_CAUSE_MARRIAGE_AT_12.md](./ROOT_CAUSE_MARRIAGE_AT_12.md)

---

## Short answer

| Question | Answer |
|----------|--------|
| Same lord / sub-lord **calculation** in all 40+ books? | **Yes** � one chart from birth time (ephemeris + lagna + dasha + KP sub-lord at degree). |
| Same **prediction text** for that placement? | **No** � each book gives its own classical reading; often **contradicts** another book. |
| Does our engine merge them into one truth? | **No** � it shows **mechanical chart** + **cited lines** + **agreement index** (book battle), with conflicts visible. |

---

## One chart math (universal)

Computed once per person:

- Planet longitudes, **lagna**, whole-sign houses  
- **House lords** from *this* lagna (Manoj: Sagittarius ? 7L and 10L = **Mercury**, 5L = **Mars**)  
- Vimshottari MD / AD / PD  
- KP **sub-lord** at planet degree and cusps (mechanical, not �voted� by books)

**Modules:** `engine/chart_builder.py`, `runtime/granular_dasha.py`, `runtime/kp_paddhati.py`

Books do **not** recalculate the sky differently.

---

## Many interpretations (book-specific)

Corpus (~**15.6k** unique rules, **41** books) is mostly indexed by:

| Key | Used in `corpus.get_planet_in_house` |
|-----|--------------------------------------|
| Planet + house | **Primary** |
| Planet + sign, dasha lord, yoga, nakshatra | Secondary |
| **This lagna only** | Only if the **text** says so (not automatic) |
| KP cuspal sub-lord | Separate KP rules; not same key as `(Mercury, 5)` |

**`book_rules.py`** (~1,926 combos) evaluates **lord_combo on the live chart** � closer to how a human uses functional lords.

---

## Example � Manoj: Mars in 5th (5L Mars in 5H)

Same placement, **opposite emphasis** in corpus:

| Source | Theme |
|--------|--------|
| **Phaladeepika** | Mars in 5th ? unhappiness, **without children**, reverses |
| **Laghu Parashari** | **For Sagittarius lagna** ? Mars as **5th lord is auspicious** |

Only one line is written for **your** ascendant. Bulk lookup can still show the other.

**Mercury in 5th** (your 7L + 10L): lines may mix career gain (10L in 5H) with classical �Mercury in 5th� avastha wording � human must filter by lagna and lordship.

---

## BPHS vs KP vs Lal Kitab (same chart?)

| System | What it adds |
|--------|-------------|
| **Parashari (BPHS, Phaladeepika, Saravali)** | House, lord, dasha, varga |
| **KP** | Star lord, **sub-lord at cusp**, event denial when SL afflicted |
| **Nadi** | Sign-based karmic bundles |
| **Lal Kitab** | Remedial / house-line themes (thin in generic planet+house index) |

Same **positions**; **different rules** for timing and outcome.

---

## How the engine handles conflict

1. **Book battle** (`engine/comparative_test.py`) � auspicious vs inauspicious keyword hits ? **consensus %** (agreement index, **not** probability).  
2. **Truth policy** � labels mechanical vs cited vs synthesis; no guaranteed outcome.  
3. **Reading filter** (`engine/reading.py`) � drops rules that contradict **planet in house** placement; **does not** yet drop �for Scorpio lagna� when native is Sagittarius (P0: lagna filter).  
4. **Life events** (`event_predictor_v2`) � timing from dasha/transits; **not** a vote across 41 books.

**What a senior astrologer does:** pick 2�3 classics that **agree for this lagna**, add strength (shadbala, yoga), use KP to **deny** an event when sub-lord blocks � say openly when books disagree.

---

## Manoj � one placement, many lines

- **Mercury** = 7th + 10th lord, placed in **5th** with Mars.  
- Corpus may return: partnership intelligence, progeny stress, career-through-creativity, KP 5th-cusp SL themes � **not one sentence**.  
- Client report should cite **lagna-applicable** lines only (roadmap in `PREDICTION_METHODOLOGY.md`).

---

## Regenerate book comparison (Manoj)

```powershell
cd F:\astro
python scratch\_manoj_engine_comparison.py
```

Output: dated `reports/.../manoj/MANOJ_ENGINE_COMPARISON.md`
