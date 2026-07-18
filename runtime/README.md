# Atro Vedic Engine — Runtime

Generates 30+ page deep-narrative Vedic astrology PDF reports from a chart JSON.

## Layout
- `runtime/` — code (this folder)
  - `generate_report.py` — PDF generator
  - `compute_*.py` — chart computation per person
- `charts/` — chart JSON files (input)
- `reports/` — generated PDFs (output)

## Install
```
pip install -r requirements.txt
```

## Generate a report
```
python generate_report.py --chart manoj_chart.json
# → writes to ../reports/<mon yyyy>/<today>/report/manoj/ via ATRO_REPORTS (see reports/README.md)
```

`--chart` accepts a bare filename (looked up in `../charts/` then `../`) or an absolute path.

## Compute a new chart from birth data
Copy one of the `compute_*.py` files, edit the `BIRTH` dict (year/month/day/hour/min/lat/lon/tz/place),
run it; it writes `<name>_chart.json` to the parent folder. Then run `generate_report.py` against it.

## Env overrides
- `ATRO_ROOT` — project root (default: parent of this folder)
- `ATRO_CHARTS` — chart JSON folder (default: `$ATRO_ROOT/charts`)
- `ATRO_REPORTS` — output folder (default: `$ATRO_ROOT/reports`)

## What the report contains
Page 1: Traditional South-Indian jadhagam (RASI + BHAVA chart, dasha tables, marriage windows).
Pages 2-30+: Life timeline, 18 domain pages (career/marriage/wealth/health/etc.), 9 Maha-Dasha
chapter pages with EXPECT/WATCH columns + sub-period tables, yogas, chara karakas, nakshatra
detail, all-houses dive, remedies, muhurta, lifetime karmic themes.

Each prediction is chart-specific (not template) — derived from house lordships, planetary
dignities, nakshatra placement, and dasha timing.
