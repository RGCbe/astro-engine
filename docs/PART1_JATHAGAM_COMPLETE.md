# Part 1 jathagam � complete (one client)

Manoj Kumar is the reference fixture. Part 1 = pages 1�13 + chart synthesis appendix.

## Generate

```powershell
cd F:\astro
python scratch/rebuild_client_chart.py charts/manoj_chart.json
python -c "import json; from datetime import datetime; from pathlib import Path; from engine.jathagam_template import build_jathagam_full; c=json.load(open('charts/manoj_chart.json',encoding='utf-8')); Path('reports/jun 2026/2026-06-02/report/manoj/MANOJ_JATHAGAM_GENERATED_TA.md').write_text(build_jathagam_full(c,'ta',when=datetime(2026,6,2)),encoding='utf-8')"
```

## Page coverage

| Page | Content | Module |
|------|---------|--------|
| 1 | Cover, Tamil date, udayadi | `jathagam_extras`, `jathagam_template` |
| 2 | Panchanga + identity block | `jathagam_extras` |
| 3 | Graha table + navamsa | `jathagam_template` |
| 4 | Rasi houses + disha iruppu | `jathagam_template`, `jathagam_extras` |
| 5 | D1 planet list | `jathagam_template` |
| 6 | Bhava cusps (start/mid/end DMS) | `jathagam_pages_advanced` |
| 7 | Shadbala table | `jathagam_pages_advanced` |
| 8 | Bhinna + Sarvashtakavarga | `jathagam_pages_advanced` |
| 9 | Mahadasha list | `jathagam_pages_advanced` |
| 10�12 | Antardasha tables (3 slices) | `jathagam_pages_advanced` |
| 13 | Vidhi + lucky elements | `jathagam_extras` |

Appendix: `build_chart_details_markdown` (synthesis, current dasha).

## Not in Part 1 (by design)

- Logic Vision print theme / footer
- South-Indian wheel PNG layout (markdown tables only)

## Next: Part 2

Prediction report from the same `manoj_chart.json` � marriage, career, dasha windows, event bands.
