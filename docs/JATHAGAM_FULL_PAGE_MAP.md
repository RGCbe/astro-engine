# Manoj jathagam � all 13 pages + what we add beyond

Source: `jadhagam/Manoj_jadagam_ocr.txt` (Logic Vision / AstroSign style printout).

## Full page inventory

| Page | Traditional content | We have today | Gap to close |
|------|---------------------|---------------|--------------|
| **1** | Cover: name, father, mother, DOB, time, **Tamil calendar date**, **udayadi / ghati / vinazhigai**, place, lat/lon | PDF page 1 + MD page 1 | Tamil date, udayadi/ghati not computed |
| **2** | Panchanga: sunrise, sunset, ayanamsa, nakshatra duration, Moon rasi, lagna, janma nakshatra, yoga, karana, tithi, paksha, **ayanam**, **rasi direction (vastu)**, chandrashtama nakshatras, deity/temple, gana, animal, tree, bird | PDF page 2 (strong); MD page 2 (summary only) | Rasi direction, chandrashtama list, deity/place, gana�rakshasa�tree�bird block |
| **3** | **Graha spudangal** table: deg, kalai, vikai, nakshatra, pada, rasi, **navamsa column** per planet; Rahu, Ketu, **Maandi**, Lagna | PDF page 3 + MD tables | Navamsa column in one table; Maandi not in chart |
| **4** | Rasi + Navamsa box charts; **disha iruppu** (e.g. Ketu direction); note on running dasha | PDF page 4 | Disha iruppu line; dasha-on-cover note |
| **5** | Rasi chart only (large), house labels | PDF page 5 | Match print layout (house names on chart) |
| **6** | **12 bhava cusps** (lagna, wealth, siblings�): start / middle / end degrees (Nirayana) | Not in Tamil PDF / MD | Need bhava chart page (exists in `generate_report.py` BHAVA chart) |
| **7** | **Dasavarga / strength**: subha/papa groups, rasi strength, durgauna, friendship, samabala, uchcha, etc. | Engine: `shadbala`, `shadbala_full` | Not in `generate_tamil_pdf` order |
| **8** | **Sarvashtakavarga** grid + directional bindus (north/south/east scores) | Engine: `ashtakavarga.py` | Not in Tamil PDF front matter |
| **9** | Vimshottari **MD�AD master table** (all mahadashas with start/end) | `granular_dasha` / timeline | Printed table format (pages 9�12), not only narrative chapters |
| **10�12** | Continuation: **AD�bhukti tables** per MD (years, months, days, end dates, age) | Dasha�Puthi MD report (event-focused) | Classic 3-page dasha booklet layout |
| **13** | Vidhi, lucky planet, **lucky weekdays**, **lucky directions**, dates, gems, **friend / enemy / neutral numbers**, color, **devata / adidevata** | PDF page 13 + numerology | Weekdays, directions, friend/enemy numbers, deities |

## Target report order (all Manoj pages, then our extras)

```
1  Cover biodata
2  Panchanga + identity
3  Planet table (+ navamsa column, Maandi if computed)
4  Rasi + Navamsa charts
5  Rasi (D1) large
6  Bhava cusps (12 houses)
7  Shadbala / planetary strength
8  Sarvashtakavarga
9  Vimshottari MD list
10�12  AD tables (life)
13  Vidhi + lucky elements (full)
--- beyond printed jathagam ---
14+ Yogas (classical)
15+ Life domains + book citations
16+ Bhrigu Patrika (lagna-filtered corpus)
17+ Chart synthesis (chart_profile + topic confidence)
18+ Where you are now + 18-month windows
19+ Dasha chapters / Dasha�Puthi (marriage, career, wealth, health per antardasha)
20+ Optional: D10 career, transits, remedies, vastu summary
```

## Prediction report (the real product � not jathagam)

These are **not** part of the 13-page reference booklet. This is what clients pay for:

| Extra block | Why it helps the client |
|-------------|-------------------------|
| **Classical yogas** | Named combinations (Raja, Dhana, etc.) with plain Tamil explanation |
| **Life-domain predictions** | Marriage, career, wealth, health with **book citations** from corpus |
| **Bhrigu Patrika** | Per-planet, per-house rules from extracted Bhrigu (~3.4k rules) |
| **Executive chart synthesis** | `chart_profile` � lagna lord, dusthana load, marriage/career hooks |
| **Multi-source confidence** | `topic_synthesis` � agreement across engines for marriage/career/wealth/health |
| **Event windows** | `event_predictor_v2` � dated bands, severity, 18-month horizon |
| **Dasha�Puthi timeline** | Per-MD/AD: income, loss, career, marriage, life events (not just dates) |
| **Lagna-filtered corpus** | Drop �other lagna only� lines so text matches **this** chart |
| **Full vargas** | D10 (career), D7 (children), etc. via `divisional_charts` |
| **Vastu hints** | Direction from chart + `vastu_shastra` module (orchestrator) |
| **Transits / Sade Sati** | Current Saturn/Jupiter impact (if wired to report) |
| **Remedies** | Gemstone/mantra from weak planets + numerology (extend page 13) |
| **Strict accuracy / known events** | Backtest hooks for celebrity or user-confirmed dates |

## Implementation priority (to match �all pages�)

**P0 � complete the 13-page booklet**

1. Page 1: Tamil calendar + ghati/vinazhigai (`panchanga` / Tamil calendar lib).
2. Page 2: chandrashtama, rasi direction, nakshatra deity block (partially in PDF nakshatra section).
3. Page 3: single table with D9 column; add Maandi to chart builder.
4. Pages 6�8: port from `generate_report.py` (bhava chart, shadbala, SAV) into `generate_tamil_pdf.py`.
5. Pages 9�12: dasha tables export from `build_full_timeline` (same data as printout).
6. Page 13: extend `numerology_vedic` + page � weekdays, directions, friend/enemy numbers, devata.

**P1 � keep differentiation after page 13**

- Yogas ? domains ? Bhrigu ? synthesis ? where-now ? Dasha�Puthi (current PDF tail).

## Modules already in codebase (reuse, do not rebuild)

| Page | Module / file |
|------|----------------|
| 3, 4, 5 | `generate_tamil_pdf.py`, `divisional_charts.py` |
| 6 | `generate_report.py` (BHAVA South Indian chart) |
| 7 | `runtime/shadbala.py`, `shadbala_full.py` |
| 8 | `engine/ashtakavarga.py` |
| 9�12 | `granular_dasha.py`, `scratch/_manoj_dasha_puthi_timeline.py` |
| 13 | `runtime/numerology_vedic.py` |
| Extras | `comprehensive_yogas.py`, `engine_orchestrator.py`, `event_predictor_v2.py`, `chart_profile.py`, `multi_source_synthesis.py` |
