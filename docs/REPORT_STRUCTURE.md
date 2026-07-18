# Report structure � every client report

## Two parts (fixed order)

```
PART 1  JATHAGAM     Full chart details (Manoj booklet pages 1-13 + tables + synthesis + current dasha)
        ---
PART 2  PREDICTIONS  Everything else � grounded in the jathagam above
```

- **Jathagam** = complete birth chart for this person (not a prediction).
- **Predictions** = timelines, event windows, domains, Bhrigu, Expect/Watch � **start only after** Part 1.

## Part 1 � Jathagam (full)

Module: `engine/jathagam_template.py`

| Function | Role |
|----------|------|
| `build_jathagam_full(chart, lang, when=...)` | Part 1 body |
| `build_prediction_section_header(lang)` | Part 2 title + note |

Content order inside Part 1:

1. Cover (page 1)
2. Panchanga / identity (page 2)
3. Graha table (page 3)
4. Rasi + Navamsa (page 4)
5. Rasi D1 (page 5)
6. Twelve bhavas (page 6)
7. Shadbala (page 7)
8. Sarvashtakavarga (page 8)
9. Vimshottari MD/AD tables (pages 9-12)
10. Vidhi + lucky (page 13)
11. Full chart details markdown (planets, houses, functional lords, synthesis, current dasha)

Layout reference: `jadhagam/Manoj_jadagam_ocr.txt`

## Part 2 � Prediction report

| Block | Source |
|-------|--------|
| Dasha-Puthi timeline | `scratch/_manoj_dasha_puthi_timeline.py` |
| Life-event windows | `event_predictor_v2` |
| Tamil / English predictions | `_manoj_tamil_predictions_report.py`, `client_report_v2` |
| Domains + citations | `client_report_v2`, corpus, Bhrigu |
| Deep PDF (23 domains) | `generate_report.py` |

Methodology: `PREDICTION_METHODOLOGY.md`

## Wired generators

| Generator | Part 1 | Part 2 header |
|-----------|--------|----------------|
| `_manoj_dasha_puthi_timeline.py` | `build_jathagam_full` | `build_prediction_section_header` |
| `_manoj_tamil_predictions_report.py` | yes | yes |
| `client_report_v2.py` / `_ta.py` | yes | yes |
| `generate_tamil_pdf.py` | PDF pages 1-13 + chart block | yogas, domains, timeline |

## Regenerate Manoj

```powershell
python F:\astro\scratch\_manoj_dasha_puthi_timeline.py
python F:\astro\scratch\_manoj_tamil_predictions_report.py
```
