# Why the Original Tamil PDF Felt "Basic"

**For:** Manoj (DOB 1996-05-25 20:25, Coimbatore)  
**Date:** 2026-06-02

## What you received before

The file `MANOJ_TAMIL.pdf` (from `runtime/generate_tamil_pdf.py`) is a **Tamil-formatted birth chart booklet**, not the same product as `MANOJ_FULL_DEEP_REPORT.pdf`.

It includes:

- Cover with current Mahadasha summary and **only the next ~6 events in 18 months** (from `event_predictor_v2`)
- Birth details, panchanga, planet table, yoga names
- Rasi / Navamsa box charts
- **Book-citation pages** (`book_rules`) � prediction *text is still mostly English* from the classical corpus
- **Bhrigu Patrika** pages � synthesized English paragraphs per planet
- Nine Vimshottari Mahadasha "life chapters" with generic Tamil themes (expect / watch / do / avoid)

## What was missing (and why it felt like "only basic things")

| Expectation | Old Tamil PDF | Full English deep report |
|---|---|---|
| Dated life-event windows (career, marriage, wealth�) | Only 6 bullets near-term on cover; rest buried in dasha chapters | `event_predictor_v2` bands + 23 narrative domains |
| Top windows 2020�2030 | Not a dedicated section | In `MANOJ_FULL_DEEP_REPORT.md` �8 |
| Active dasha **cause ? effect** in plain language | One paragraph on cover | Table C in `MANOJ_ENGINE_COMPARISON.md` |
| Domain tables (career / marriage / wealth / health / father) | Book citations in English | Comparison report Table B |
| Mostly Tamil prose | Planet/sign names Tamil; **yoga names, book quotes, Bhrigu text = English** | English throughout |

**Root cause:** `generate_tamil_pdf.py` was built for **layout + translation of chart facts**, with prediction engines wired lightly (short horizon on page 1, generic dasha copy). The heavy prediction pipeline (`event_predictor_v2` ranked bands, hybrid engine, 23-domain `generate_report.py`) was run for the **English** deliverable only.

## What we added now

New files (Tamil-first, rule-engine labelled):

- `reports/jun 2026/2026-06-02/report/manoj/MANOJ_PREDICTIONS_TA.md`
- `reports/jun 2026/2026-06-02/report/manoj/MANOJ_PREDICTIONS_TA.pdf`

Contents:

1. **???????? ??? � ?????? ? ??????** (4-level vimshottari, Tamil)
2. **Top 15 life-event windows** � next 5 years (category, date window, Tamil explanation, cause)
3. **2020�2030** and **childhood 1996�1998** band tables
4. **Top 5 per domain:** career, marriage, wealth, health, father
5. Disclaimer: **????-??????? ????????? � ????? ????** (not a guarantee)

Generator: `scratch/_manoj_tamil_predictions_report.py`

## What may still appear in English

- Untranslated **"why"** cause strings from the engine when no Tamil mapping exists
- Severity stars and technical tokens (MD/AD abbreviations in table headers)
- Optional EN twin: `MANOJ_PREDICTIONS_EN.pdf`

## Recommended reading order for Manoj

1. **MANOJ_PREDICTIONS_TA.pdf** � dated windows in Tamil (this fix)
2. **MANOJ_FULL_DEEP_REPORT.pdf** � full English narrative + all engines
3. **MANOJ_TAMIL.pdf** � traditional chart booklet (reference, not primary predictions)

---

*Honest summary: the old PDF was not broken � it was the wrong product for "where are my predictions?" The new PDF pulls the same event engine used in the English deep report, with Tamil labels and explicit non-guarantee wording.*
