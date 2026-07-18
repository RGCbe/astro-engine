# Test Subjects � Canonical Birth & Event Data

**Date:** 2026-06-02  
**Authority:** `charts/<slug>_chart.json` is the single source of truth for accuracy tests (`runtime/_accuracy_scorer.py`). `engine/known_charts.py` birth blocks are synced from charts for backtest/cross-check parity.

---

## Test subject inventory

| Group | Slug | In accuracy scorer |
|-------|------|-------------------|
| Scorer (16) | sachin_tendulkar, amitabh_bachchan, narendra_modi, ms_dhoni, ar_rahman, rekha, virat_kohli, shah_rukh_khan, sourav_ganguly, aishwarya_rai, indira_gandhi, mahatma_gandhi, steve_jobs, stephen_hawking, lata_mangeshkar, mukesh_ambani | Yes |
| Integration (4) | manoj, sree, krishnan, jayaprakesh | `test_full_integration.py` |
| Battle / misc | joseph_vijay | `_battle_vijay.py`, scratch tests |

---

## Canonical birth data

| slug | name | birth (canonical) | lat | lon | tz | time confidence | Rodden / source |
|------|------|-------------------|-----|-----|-----|-----------------|-----------------|
| sachin_tendulkar | Sachin Tendulkar | 1973-04-24 13:00 | 18.9667 | 72.8333 | 5.5 | **A** � delivering doctor (Dr. Shraddhanand Thakur, 2013) | [Astro-Seek / Scholfield AA](https://www.astro-seek.com/birth-chart/sachin-tendulkar-horoscope) |
| mukesh_ambani | Mukesh Ambani | 1957-04-19 06:56 | 12.7855 | 45.0187 | 3.0 (Aden) | **C** � family astrologer via McDonald bio; ADB time unknown | [Astro-Seek (unknown time)](https://www.astro-seek.com/birth-chart/mukes-ambani-horoscope) |
| mahatma_gandhi | Mahatma Gandhi | 1869-10-02 07:33 | 21.6417 | 69.6293 | 4.62 (LMT) | **A/C** � autobiography 07:33 LMT; ADB often 07:08 LMT | [Astro-Seek 07:08 Rodden C](https://www.astro-seek.com/birth-chart/mahatma-mohandas-gandhi-horoscope) |
| narendra_modi | Narendra Modi | 1950-09-17 11:00 | 23.7936 | 72.6376 | 5.5 | **DD** � 11:00 ADB vs 09:35 brother | Chart note |
| amitabh_bachchan | Amitabh Bachchan | 1942-10-11 03:30 | 25.4358 | 81.8463 | 5.5 | **DD** � autobiography 03:30 vs ~15:00 father bio | Chart note |
| indira_gandhi | Indira Gandhi | 1917-11-19 23:11 | 25.4358 | 81.8463 | 5.5 | **A/B** � KP / Nehru family | Chart note |
| ms_dhoni | MS Dhoni | 1981-07-07 05:10 | 23.3441 | 85.3096 | 5.5 | **A** � family via Seth 2017 | Astrodatabank |
| ar_rahman | A.R. Rahman | 1967-01-06 05:50 | 13.0827 | 80.2707 | 5.5 | **A** � self-reported interview | Astrodatabank |
| rekha | Rekha | 1954-10-10 11:00 | 13.0827 | 80.2707 | 5.5 | **A** � Kundli Sangraha (Bhat); alt 03:00 lower weight | Chart note |
| virat_kohli | Virat Kohli | 1988-11-05 04:08 | 28.6139 | 77.2090 | 5.5 | **A** � widely cited natal data | Chart note |
| shah_rukh_khan | Shah Rukh Khan | 1965-11-02 02:30 | 28.6139 | 77.2090 | 5.5 | **B** � Anupama Chopra biography | Chart note |
| sourav_ganguly | Sourav Ganguly | 1972-07-08 14:15 | 22.5726 | 88.3639 | 5.5 | **A** � family via biographers | Chart note |
| aishwarya_rai | Aishwarya Rai | 1973-11-01 04:55 | 12.9141 | 74.8560 | 5.5 | **A** � mother Vrinda Rai | Astrodatabank |
| lata_mangeshkar | Lata Mangeshkar | 1929-09-28 22:30 | 22.7196 | 75.8577 | 5.5 | **B** � Mishra biography (10:30 PM) | Chart note |
| steve_jobs | Steve Jobs | 1955-02-24 19:15 | 37.7749 | -122.4194 | -8.0 | **A** � adoption records / Isaacson | Astrodienst |
| stephen_hawking | Stephen Hawking | 1942-01-08 01:39 | 51.7520 | -1.2577 | 0.0 | **B** � mother's recall | Astrodienst |
| manoj | Manoj (user) | 1996-05-25 20:25 | 11.01 | 76.57 | 5.5 (assumed IST) | User chart � tz missing in JSON | Integration fixture |
| sree | Sree | 1983-05-18 17:30 | 11.0168 | 76.9558 | 5.5 | Project compute script | `compute_sree.py` |
| krishnan | Krishnan | 2002-07-26 05:52 | 11.0168 | 76.9558 | 5.5 | Project compute script | `compute_krishnan.py` |
| jayaprakesh | Jayaprakesh | 1986-06-24 23:55 | 11.0168 | 76.9558 | 5.5 | Project compute script | `compute_jayaprakesh.py` |
| joseph_vijay | Joseph Vijay | 1974-06-22 12:00 | 13.0827 | 80.2707 | 5.5 | **B** � family / lifeline notes | Chart note |

---

## Disputed birth times � canonical choice

| Subject | Alternatives | **Chosen** | Rationale |
|---------|--------------|------------|-----------|
| **Sachin** | 13:00 (doctor) vs 17:25 (old `known_charts`) | **13:00** | Scholfield/AA on Astro-Seek; 17:25 not supported in public ADB lineage; shifts lagna Cancer?Virgo if wrong |
| **Mukesh** | 06:56 (family) vs 11:30 (old `known_charts`) vs evening rectifications | **06:56** | Only time with biographer-cited family source; Astro-Databank lists **unknown** time |
| **Gandhi** | 07:33 LMT tz 4.62 (chart) vs 07:11 tz 4.85 (`known_charts`) | **07:33 / 4.62** | Documented in autobiography; same Libra lagna sign either way (~5� asc shift) |

---

## Event fixes (placeholder `YYYY-01-01` removed)

| slug | Old ? New | Notes |
|------|-----------|-------|
| sachin_tendulkar | 1989-11-15 ? **1989-11-16** | First Test **batting** day 2 (ESPNcricinfo); match began 15th |
| ar_rahman | 1976-01-01 ? **1976-09-30** | Father R.K. Shekhar death ([Wikipedia](https://en.wikipedia.org/wiki/R._K._Shekhar)) |
| ar_rahman | 1989-01-01 ? **1989-01-01** + `date_precision: year` | Islam conversion year only ([Wikipedia](https://en.wikipedia.org/wiki/A._R._Rahman)) |
| ar_rahman | 1992-01-01 ? **1992-08-15** | Roja release |
| ar_rahman | 1993-01-01 ? **1993-05-04** | 40th National Film Awards presentation |
| ar_rahman | 1997-01-01 ? **1997-08-12** | Vande Mataram album |
| ar_rahman | 2010-01-01 ? **2010-01-31** | 52nd Grammy ceremony |
| rekha | 1980-01-01 ? **1981-07-01** | Filmfare Best Actress Khubsoorat (28th Filmfare 1981) |
| rekha | 1982-01-01 ? **1982-04-15** | National Award Umrao Jaan (29th NFA April 1982) |
| rekha | 1988-01-01 ? **1989-03-15** | Filmfare Khoon Bhari Maang (34th Filmfare 1989) |
| amitabh_bachchan | 1997-01-01 ? **1999-07-09** | BIFR declared ABCL sick ([Rediff](https://www.rediff.com/business/1999/jul/09abcl.htm)) |
| aishwarya_rai | 2018-01-01 ? **2017-03-18** | Father Krishnaraj Rai death |
| virat_kohli | 2018-01-01 ? **2017-03-30** | Padma Shri investiture ([News18](https://www.news18.com/cricketnext/news/virat-kohli-receives-padma-shri-award-at-rashtrapati-bhavan-1366331.html)) |

**Count:** 11 events given exact dates; 1 year-only event tagged with `date_precision`.

---

## Sync & recompute

- `engine/known_charts.py`: birthdata aligned for Gandhi, Indira, Modi, Sachin, Lata, Shah Rukh, Mukesh, Amitabh, Rahman, Aishwarya, Hawking, Jobs (12 entries).
- **Lagna recompute:** Run on VPS with `/opt/astro/ephe` when birth fields change. Current disputed-three charts unchanged in birth JSON ? no lagna recompute required this pass.
- **CI recommendation:** `charts/{slug}_chart.json` birth == `known_charts` for all scorer slugs (see `scratch/apply_canonical_test_subjects.py`).

---

## Maintenance script

```powershell
cd F:\astro
python scratch\apply_canonical_test_subjects.py
python scratch\_compare_known_charts.py
```
