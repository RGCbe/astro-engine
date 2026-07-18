# Report Revision — Client Feedback (PAUSED 2026-06-13 · resume Mon 2026-06-15)

**Source:** handwritten client feedback on `reports/MANOJ_KUMAR_FULL_REPORT.pdf`
(148-page deep 23-domain booklet from `runtime/generate_report.py`).
**Status:** WAVE 1 DONE (2026-06-15) — 148→134 pages. 10 sections gated OFF via a
`SHOW={}` dict at top of `generate()` in runtime/generate_report.py (each section's
`try:` now starts with `if not SHOW["key"]: raise _Skip(...)`). Helpers untouched;
flip a key to True to restore. Kept: 30-day forecast (HOLD), Present Moment, Doshas.
**WAVE 2 DONE (2026-06-15):** added a reusable `explainer()` story-callout (gold box)
+ plain-language intros on Shadbala, Longevity, Medical, Lal Kitab, Spouse; reformatted
Present Moment → predictions table + "bottom line" box; **FIXED the `&nbsp;/&bull;`
literal-text bug in `to_para()`** that printed on every page (client's mystery note —
to_para now converts those entities to real glyphs before escaping bare `&`).
Report = 134 pages, reports/MANOJ_KUMAR_FULL_REPORT.pdf. All local, no VPS deploy.

**BUGS FIXED (2026-06-15, report QA):** (1) Divisional Charts dumped a raw Python dict
`{'book':…,'tags':[…]}` into the report — its generic "print every field" loop ran `str()`
on the `citations` list (also duplicated them); added `"citations"` to the field skip-list.
(2) Divisional / Aspects / Conjunctions printed garbled OCR corpus quotes verbatim — replaced
with a clean `Verified in classical corpus: <books>` attribution line. Report now **133 pages**,
full scan clean (0 raw dicts, 0 garble, 0 entity/markup/None leaks).

**READABILITY for low-education clients — SOLVED (2026-06-15):** the existing
`runtime/generate_summary_pdf.py` already produces a **6-page plain-English CLIENT version**
→ `reports/<NAME>_SUMMARY.pdf` (0.55% jargon vs 6% in the full report; no Sanskrit/codes;
~10-min read; sections: Right Now / Personality / Career&Wealth / Marriage&Family /
Health&Spirituality&5yr). Fixed its birthplace bug (was rendering the Tamil place as ■■■
boxes → now uses `place_en`). **TWO-TIER delivery:** short SUMMARY for clients + the 133-page
FULL report as a technical appendix. Run:
`python runtime/generate_summary_pdf.py --chart charts/<name>_chart.json`.
ENHANCED 2026-06-15 (visual + plain-language pass on the SUMMARY):
- fixed doubled "Event Event" + redundant " Event" suffix; removed ⭐ emoji boxes.
- added `plain_event()` keyword classifier mapping ALL 167 predictor categories → plain
  life themes; timeline now 0 jargon and skips purely-technical markers (KP/Tajik/Mayan/etc).
- added a VISUAL page 2 "YOUR LIFE — AT A GLANCE": colour-bar meters per life area
  (Personality/Career/Money/Marriage/Health/Mind/Luck) via `seg_meter()`, scored RELATIVELY
  from shadbala (`_area_score` deprecated; page uses relative spread) so it's never all-red —
  readable by a non-literate client from colour alone (green=strong, amber=steady, red=care).
- fixed birthplace ■■■ boxes (Tamil → `place_en`).
Summary now **7 pages**, scan clean (0 jargon / 0 black-box / 0 dict-leak / 0 None).
**VISUAL QA (do this — text-extraction can't see drawn bars/layout):** PyMuPDF *is* installed —
render with `import fitz; fitz.open(pdf)[i].get_pixmap(dpi=130).save(png)` then Read the PNG.
Caught+fixed by actually looking: (1) score-2 meter bars were red but labelled amber "Developing"
→ bar fill now amber for score≥2; (2) page-1 "next 18 months" showed already-ended windows all
dated "Jan 2026" (scan starts at year boundary) → now drops `window_end < today` and clamps the
shown start to today; (3) duplicate plain-labels (Health ×3) → both timelines dedupe by phrase.
Run: `python runtime/generate_summary_pdf.py --chart charts/<name>_chart.json`.

**Remaining (optional):** deeper VISUAL/graphic restyle ("eye-catching", roll page-20
Doshas look across pages — only readability done so far). Decide 30-day forecast
(still ON via `SHOW["thirty_day"]`) and muhurta windows (OFF). Spouse got a story box
but no graphic redesign yet.

## Regenerate command
```powershell
$env:ATRO_EPHE='F:/astro/ephe'; $env:PYTHONPATH='F:/astro'
python F:\astro\runtime\generate_report.py --chart charts\manoj_chart.json
# verify pages: pypdf PdfReader("reports/MANOJ_KUMAR_FULL_REPORT.pdf"); len(r.pages)
```

## Client's overall direction (their words)
- "Use LESS pages" — report is too long.
- "Need STORY-TYPE explanation that makes client understand easily" — not bare tables/numbers.
- "More visual elements, eye-catching" — **Page 20 (DOSHAS) is the GOOD reference style** to copy.
- Bare tables / lists of years are unreadable → add narrative + explain what each thing means/how to read it.

## WAVE 1 — structural cuts (do first; all blocks in runtime/generate_report.py)
Each section is a `try:`/`if` block appended to `flow`, ending in `PageBreak()`.
Comment out / gate the block — do NOT delete the helper functions.

| PDF pg | Section | Header line | Action |
|---|---|---|---|
| 4 | SAHAMS — 28 Sensitive Points | 2060 | REMOVE |
| 5 | ECLIPSE IMPACT | 2080 | REMOVE |
| 6 | 30-DAY FORECAST | 2101 | **HOLD** ("wait" — leave for now) |
| 7 | TARA CHAKRA | 2124 | REMOVE |
| 8 | FULL SHADBALA (30+ sub) | 2138 | REMOVE |
| 9 | VIMSHOPAKA BALA | 2161 | REMOVE |
| 10 | TRI-PATAKI CHAKRA | 2182 | REMOVE |
| 11 | VARSHAPHALA INTERNAL DASHAS | 2205 | REMOVE |
| 12-13 | JAIMINI DASHA SYSTEMS | 2231 | REMOVE |
| 19 | SPECIAL LAGNAS | 2389 | REMOVE |
| 16-18 | MUHURTA windows (Upanayana/Vehicle/Cremation dates) | 2328 | **OPTIONAL** — gate behind flag, default OFF ("give if they ask only") |

Keep: CHAR DASHA (pg 3, line 2034) and every page not listed.

## WAVE 2 — narrative + visual redesign ("story-type" work; locate by title grep)
| PDF pg | Section | Action |
|---|---|---|
| 14 | PRESENT MOMENT (line 2275) | Predictions ONLY, in TABLE format |
| 20 | DOSHAS | KEEP — target visual style; copy this look to other pages |
| 21 | SPOUSE INFERENCE | More visual, eye-catching, fewer pages |
| 23 | SHADBALA — PLANETARY STRENGTHS | Bare table → add "what is this for" explanation |
| 25 | LONGEVITY (AYURDAYA) | Only years given → add "how to read it" explanation |
| 26 | MEDICAL ASTROLOGY | Add clear narrative explanation |
| 27 | LAL KITAB — Karz | Add clear narrative explanation |
| every page | the recurring "[bullet]" element client couldn't identify | clarify/label what it means |

## Session context (already done, not part of this revision)
- tier-1 condition resolution in `engine/book_rules.py` (built, tested LOCAL, not deployed).
- `multi_house` rule type activated; `conditional` left inert (OCR prose → wrong predicates).
- Fixed `engine/chart.py` geocode (`.lat/.lon`).
- Cleared all old reports except `reports/README.md`.
