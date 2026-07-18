# Atro Vedic Engine — API Reference

**Build:** 2026-05-06 | **Engine version:** unified-v15.0

> **See also:** [MODULE_INDEX.md](../runtime/MODULE_INDEX.md) (every module catalogued) · [UNIFIED_ARCHITECTURE.md](UNIFIED_ARCHITECTURE.md) (how engines fit together) · [USER_GUIDE.md](USER_GUIDE.md) (end-user manual)

This document lists every public function across both engines, grouped by capability. All functions accept a `chart` dict (see [MODULE_INDEX](../runtime/MODULE_INDEX.md#adding-a-new-chart) for shape) unless noted.

**Convention:**
- Functions starting with `_` are internal — not listed here.
- Each entry: `function_name(args)` — short description — Returns: type
- File path is shown as either `runtime/file.py:line` or `engine/file.py:line`.

---

## Table of Contents

1. [Top-Level Entry Points](#top-level-entry-points)
2. [FastAPI HTTP Endpoints](#fastapi-http-endpoints)
3. [CLI Commands](#cli-commands)
4. [Chart Construction](#chart-construction)
5. [Dasha Systems](#dasha-systems)
6. [Divisional Charts (Vargas)](#divisional-charts-vargas)
7. [Yogas](#yogas)
8. [Strength Calculations](#strength-calculations)
9. [Aspects & Conjunctions](#aspects--conjunctions)
10. [Transits & Forecasting](#transits--forecasting)
11. [Event Prediction](#event-prediction)
12. [Compatibility & Doshas](#compatibility--doshas)
13. [Specialty Traditions](#specialty-traditions)
14. [Tier 1 Multi-Tradition](#tier-1-multi-tradition)
15. [Annual Charts (Varshaphala / Tajik)](#annual-charts-varshaphala--tajik)
16. [Auxiliary & Timing](#auxiliary--timing)
17. [Vedic Core Helpers](#vedic-core-helpers)
18. [Book Corpus](#book-corpus)
19. [Reading Generation](#reading-generation)
20. [Calibration & Backtesting (engine/)](#calibration--backtesting-engine)
21. [Localization & Rendering](#localization--rendering)

---

## Top-Level Entry Points

### `engine_unified.py`

| Function | Purpose | Returns |
|---|---|---|
| `unified_analysis(chart, when=None, modes=["all"])` | Run the full combined engine. `modes` filter: `engine_main`, `runtime`, `present`, `all_yogas`, `all_dashas`, `all_vargas`, `tier1`, `tier2`, `tier3`, `panchanga`, `kp`, `render` | `dict` with `engine_version`, `as_of`, `chart_name`, `modules` (per-module result), `summary` |
| `quick_summary(chart, when=None)` | Lightweight summary — only present, all_yogas, panchanga | Same shape as `unified_analysis` |

### `runtime/engine_orchestrator.py`

| Function | Purpose | Returns |
|---|---|---|
| `full_analysis(chart, when=None)` | Run every runtime module (50+) | `dict` with `engine_version`, `as_of`, `chart_name`, `modules`, `summary` |
| `integrity_check(chart)` | Run all modules and print which work/fail | `dict` (same as full_analysis) + console output |
| `safe_run(name, fn, *args, **kwargs)` | Internal — wraps a module call with error capture | `dict` `{status, data}` or `{status, error, traceback}` |

---

## FastAPI HTTP Endpoints

Defined in `main.py`. Run with `uvicorn main:app --reload --port 8000`.

| Method | Path | Body | Returns |
|---|---|---|---|
| GET | `/` | — | Engine status + corpus stats (total rules, books loaded, planet-house slots, yoga rules, dasha rules) |
| POST | `/api/jathagam` | `BirthData` (year, month, day, time, lat, lon, focus) | Full chart analysis: lagnam, navamsa lagna, arudha lagna, panchangam, all planet positions (with D9/D10/D60), 3-tier dasha (Maha/Antar/Pratyantar), Yogini, house predictions (multi-book corpus), detected yogas, Shadbala, Ashtakavarga, gochar (transits), KP analysis, advanced reading HTML, synthesis |
| POST | `/api/book-battle` | `BirthData` | Same as `/api/jathagam` plus `battle_results` — comparative analysis across books |

`BirthData` schema (Pydantic model, defined in `main.py:69`):
```python
class BirthData(BaseModel):
    year: int
    month: int
    day: int
    time: str           # "HH:MM"
    lat: float = 11.0   # default Coimbatore
    lon: float = 77.0
    focus: str = "general"
```

---

## CLI Commands

Defined in `runtime/atro_cli.py`. Run via:
```bash
python runtime/atro_cli.py --chart NAME --mode MODE [--out FILE] [--chart2 NAME] [--days N]
```

| Mode | Function | Purpose |
|---|---|---|
| `pdf` | `cmd_pdf()` | Generate full PDF report (delegates to `generate_report.generate()`) |
| `json` | `cmd_json()` | Dump full analysis as JSON (delegates to `full_analysis()`) |
| `summary` | `cmd_summary()` | Quick text summary (default mode) |
| `present` | `cmd_present()` | Present-moment synthesis (delegates to `present_moment_reading()`) |
| `forecast` | `cmd_forecast()` | N-day forecast (delegates to `forecast_period()`) |
| `events` | `cmd_events()` | Lifetime events table (delegates to `scan_lifetime_v2()`) |
| `yogas` | `cmd_yogas()` | List all active yogas |
| `match` | `cmd_match()` | Compatibility match (requires `--chart2`) |
| `check` | `cmd_check()` | Engine integrity check (delegates to `integrity_check()`) |

`load_chart(name)` — looks for the chart JSON in `F:/Atro/charts/` (or path override via `ATRO_CHARTS` env var).

---

## Chart Construction

### `engine/chart.py`

| Function | Args | Returns |
|---|---|---|
| `compute_chart(birth, lat, lon, tz_hours, ayanamsa="lahiri")` | Full Swiss Ephemeris chart compute | Chart dict (positions, lagna, vargas, etc.) |

### `engine/bhrigu_chart_root.py`

| Function | Args | Returns |
|---|---|---|
| `calc_chart(dt_local, lat, lon, tz_offset_hours, ayanamsha="lahiri")` | Swiss Ephemeris calculation, Bhrigu-style normalization | Chart dict |
| `print_chart(chart)` | Pretty-print chart to console | None |
| `parse_dt(s)` | Parse "YYYY-MM-DD HH:MM" string | `datetime` |

### `engine/ayanamsa_picker.py`

| Function | Purpose | Returns |
|---|---|---|
| `pick(lat, lon, tz_hours, traditions, default="lahiri")` | Choose appropriate ayanamsha for region | `AyanamsaChoice` dataclass |
| `methodology_footer(choice)` | Human-readable rationale | `str` |

### `engine/geocode.py`

| Function | Args | Returns |
|---|---|---|
| `geocode(place, country=None)` | Resolve place to lat/lon/timezone | `Geo` dataclass or None |
| `lookup(place)` | Cached lookup | `Geo` or None |

---

## Dasha Systems

### `runtime/granular_dasha.py`

| Function | Args | Returns |
|---|---|---|
| `build_full_timeline(chart, levels=4)` | 4-level Vimshottari MD/AD/PD/SD | `list[dict]` with `{lord, start, end, years, sub_periods}` |
| `lookup(timeline, when_dt)` | Find active dasha at given datetime | `dict` with active MD/AD/PD/SD lords |

### `runtime/other_dashas.py`

| Function | Args | Returns |
|---|---|---|
| `compute_ashtottari(natal_chart)` | 108-year Ashtottari dasha | `list[dict]` |
| `compute_yogini(natal_chart)` | 8-Yogini × 36-year cycle | `list[dict]` |
| `all_dashas_summary(natal_chart)` | Summary of multiple dasha systems | `dict` |

### `runtime/char_dasha.py`

| Function | Args | Returns |
|---|---|---|
| `char_dasha(chart)` | Jaimini Char (Rasi) Dasha — 9 sign periods | `list[dict]` with `{sign, lord, start, end, years}` |

### `runtime/varshaphala_dashas.py`

| Function | Args | Returns |
|---|---|---|
| `mudda_dasha(annual_lagna_lord, year_start_dt)` | Mudda dasha for the year | `list[dict]` |
| `patyayini_dasha(planet_strengths, year_start_dt)` | Patyayini sub-dasha | `list[dict]` |
| `annual_dashas_summary(natal_chart, target_year)` | Both annual dashas | `dict` |

### `engine/dasha.py` (bridge → runtime)

| Function | Args | Returns |
|---|---|---|
| `vimshottari(chart)` | MD-only Vimshottari timeline | `list[dict]` |
| `current_dasha(chart, when=None)` | Active MD/AD at moment | `dict` |
| `full_timeline(chart, levels=4)` | Full 4-level timeline | `list[dict]` |
| `ashtottari(chart)` | Ashtottari MD timeline | `list[dict]` |
| `yogini(chart)` | Yogini dasha | `list[dict]` |
| `char(chart)` | Char dasha | `list[dict]` |

### `engine/dasha_compute.py` (low-level)

| Function | Args | Returns |
|---|---|---|
| `calculate_vimshottari(moon_longitude, birth_date)` | Compute from Moon's longitude | `dict` with periods, current MD/AD/PD |
| `calculate_yogini(moon_longitude, birth_date)` | Yogini computation | `dict` |

### `engine/raasi_dasha.py`

| Function | Args | Returns |
|---|---|---|
| `chara_dasha(...)` | Jaimini Chara dasha | `RaasiDasha` |
| `sthira_dasha(lagna_sign_idx, birth_dt)` | Sthira dasha (fixed) | `RaasiDasha` |
| `shoola_dasha(...)` | Shoola dasha | `RaasiDasha` |
| `current_period(dasha, at)` | Active period at moment | `RaasiPeriod` or None |
| `summary_table(dasha)` | Table format | `list[dict]` |
| `kalachakra_dasha(*args, **kwargs)` | Wrapper for Kalachakra | `KalachakraDasha` |

### `engine/kalachakra.py`

| Function | Args | Returns |
|---|---|---|
| `kalachakra(...)` | Compute Kalachakra dasha | `KalachakraDasha` |
| `current_period(dasha, at)` | Active sub-period | `KalachakraPeriod` or None |
| `summary_table(dasha)` | Tabular form | `dict` |

### `engine/dasa_narrative.py`

| Function | Args | Returns |
|---|---|---|
| `build_timeline(chart, today=None)` | Narrative dasha timeline | `list[DasaPrediction]` |
| `upcoming(chart, n=6, today=None)` | Upcoming N predictions | `list[DasaPrediction]` |
| `find_window(chart, event_keyword, ...)` | Find dasha window for event | `list` |
| `find_for_date(chart, when)` | Active prediction at date | `DasaPrediction` or None |

---

## Divisional Charts (Vargas)

### `runtime/divisional_charts.py`

| Function | Args | Returns |
|---|---|---|
| `build_divisional_chart(natal_chart, varga="D9")` | Build single varga | Chart dict for that varga |
| `analyze_d9_marriage(natal_chart)` | D9 marriage analysis | `dict` |
| `analyze_d10_career(natal_chart)` | D10 career analysis | `dict` |
| `analyze_d60_karma(natal_chart)` | D60 karmic analysis | `dict` |
| `full_varga_analysis(natal_chart, with_citations=True)` | All 4 primary vargas + analysis | `dict` |

### `runtime/extra_vargas.py`

| Function | Args | Returns |
|---|---|---|
| `build_extra_varga(natal_chart, varga)` | Build any of D2/D3/D4/D7/D12/D16/D20/D24/D27/D30/D40/D45 | Chart dict |
| `all_vargas_summary(natal_chart)` | All 12 extra vargas | `dict` |

### `engine/vargas.py` (bridge)

| Function | Args | Returns |
|---|---|---|
| `all_vargas(chart)` | All 16 divisional charts (Shodashvarga) | `dict` keyed by varga name |
| `vargottama(chart)` | Planets in same sign in D1 + D9 | `list[str]` |
| `varga_summary(chart)` | Summary table | `dict` |

### `engine/varga_weighted.py`

| Function | Args | Returns |
|---|---|---|
| `varga_modifier(chart, planet, event_type)` | Varga-weighted modifier | `dict` |
| `varga_conditioned(chart, event_type, base_LR)` | LR adjusted by varga strength | `dict` |

---

## Yogas

### `runtime/comprehensive_yogas.py`

Each `y_*` function detects one yoga and returns `dict` (or empty list if not present).

| Function | Yoga |
|---|---|
| `y_mahapurusha(chart)` | Pancha Mahapurusha — Ruchaka/Bhadra/Hamsa/Malavya/Shasha |
| `y_sunapha(chart)` | Sunapha (planet in 2nd from Moon) |
| `y_anapha(chart)` | Anapha (planet in 12th from Moon) |
| `y_durdhara(chart)` | Durdhara (Sunapha + Anapha) |
| `y_kemadruma(chart)` | Kemadruma (no planet around Moon) |
| `y_vesi(chart)` | Vesi (planet 2nd from Sun) |
| `y_vasi(chart)` | Vasi (planet 12th from Sun) |
| `y_ubhayachari(chart)` | Ubhayachari |
| `y_gaja_kesari(chart)` | Gaja-Kesari (Jupiter kendra from Moon) |
| `y_budha_aditya(chart)` | Budha-Aditya |
| `y_chandra_mangala(chart)` | Chandra-Mangala |
| `y_yukta(chart)` | Yukta yoga |
| `y_vidyut(chart)` | Vidyut |
| `y_lakshmi(chart)` | Lakshmi |
| `y_neecha_bhanga(chart)` | Neecha-Bhanga (debilitation cancellation) |
| `y_raja_kendra_trikona(chart)` | Kendra-Trikona Raja Yoga |
| `y_vipareeta_raja(chart)` | Vipareeta Raja Yoga |
| `y_dhana_2_11(chart)` | 2-11 Dhana yoga |
| `y_dhana_5_9(chart)` | 5-9 Dhana yoga |
| `y_kuber(chart)` | Kuber yoga |
| `y_daridra(chart)` | Daridra yoga |
| `y_pitra_dosha(chart)` | Pitra Dosha |
| `y_matra_dosha(chart)` | Matra Dosha |
| `y_bhratra_dosha(chart)` | Bhratra Dosha |
| `y_putra_dosha(chart)` | Putra Dosha |
| `y_kaal_sarpa(chart)` | Kaal Sarpa |
| `y_nabhasa(chart)` | Nabhasa yoga family |
| `y_parivartana(chart)` | Parivartana exchange |
| `detect_all_classical_yogas(chart)` | Run all detectors and aggregate | `list[dict]` |

### `runtime/yoga_library_v2.py`

| Function | Yoga |
|---|---|
| `y_adhi(chart)` | Adhi yoga |
| `y_amala(chart)` | Amala |
| `y_akhanda_samrajya(chart)` | Akhanda Samrajya |
| `y_maha_bhagya(chart)` | Maha Bhagya (gendered) |
| `y_saraswati(chart)` | Saraswati |
| `y_lakshmi_yoga_full(chart)` | Lakshmi (full strict) |
| `y_kuldeepak(chart)` | Kuldeepak |
| `y_pushkala(chart)` | Pushkala |
| `y_nabhasa_extended(chart)` | Extended Nabhasa family |
| `y_kemadruma_full(chart)` | Strict Kemadruma |
| `y_daridra_strict(chart)` | Strict Daridra |
| `y_kapata_yoga(chart)` | Kapata |
| `y_paap_kartari(chart)` | Paap Kartari (planet hemmed by malefics) |
| `y_shubha_kartari(chart)` | Shubha Kartari (planet hemmed by benefics) |
| `y_pravrajya(chart)` | Pravrajya (renunciation) |
| `detect_extra_yogas(chart)` | Run all and aggregate | `list[dict]` |
| `detect_all_yogas_combined(chart)` | Combine with comprehensive_yogas | `list[dict]` |

### `runtime/event_yoga_detector.py` (legacy)

`yoga_pitru_kasht`, `yoga_matruhanta`, `yoga_vidyut`, `yoga_kaal_sarpa`, `yoga_balarishta`, `yoga_marriage_delay`, `yoga_dhana`, `yoga_raja`, `yoga_health_chronic`, `yoga_career_breakthrough`, `detect_all_yogas`

### `engine/yogas.py`

| Function | Args | Returns |
|---|---|---|
| `detect_all(chart)` | Aggregator across all engine-side yogas | `list` |

### `engine/yogas_extended.py`

`detect_12_bhava_yogas`, `detect_parivartana_yogas`, `detect_amala_yoga`, `detect_vasumat_yoga`, `detect_pushkala_yoga`, `detect_mahabhagya_yoga(chart, gender=None)`, `detect_musala_yoga`, `detect_yuga_yoga`, `detect_gola_yoga`, `detect_apakartari_yoga`, `detect_all_extended(chart, gender=None)`, `summary(chart)`

### `engine/yogas_nabhasa.py`

32 Nabhasa yogas — `detect_rajju_yoga`, `detect_nala_yoga`, `detect_mala_yoga`, `detect_sarpa_nabhasa_yoga`, `detect_sankhya_yogas`, `detect_gada_yoga`, `detect_sakata_nabhasa_yoga`, `detect_vihaga_yoga`, `detect_sringataka_yoga`, `detect_hala_yoga`, `detect_vajra_yoga`, `detect_yava_yoga`, `detect_kamala_yoga`, `detect_vapi_yoga`, `detect_yupa_yoga`, `detect_shara_yoga`, `detect_shakti_yoga`, `detect_danda_yoga`, `detect_naukha_yoga`, `detect_kuta_yoga`, `detect_chatra_yoga`, `detect_chapa_yoga`, `detect_ardha_chandra_yoga`, `detect_samudra_yoga`, `detect_bharathi_yoga`, `detect_all_nabhasa(chart)`

### `engine/blessings.py`

| Function | Yoga |
|---|---|
| `detect_pancha_mahapurusha(chart)` | List of 5 Mahapurusha checks |
| `detect_raja_yogas(chart)` | All Raja Yoga variants |
| `detect_dhana_yogas(chart)` | All wealth combinations |
| `detect_vipareeta_raja_yoga(chart)` | Vipareeta variants |
| `detect_neecha_bhanga(chart)` | Debilitation cancellation |
| `detect_gajakesari(chart)` | Single check |
| `detect_lunar_yogas(chart)` | Sunapha/Anapha/Durdhara/Kemadruma |
| `detect_chandra_mangal(chart)` | Single check |
| `detect_adhi_yoga(chart)` | Single check |
| `detect_lakshmi_yoga(chart)` | Single check |
| `detect_saraswati_yoga(chart)` | Single check |
| `detect_solar_yogas(chart)` | Vesi/Vasi/Ubhayachari |
| `detect_shankha_yoga(chart)` | Single check |
| `detect_padma_yoga(chart)` | Single check |
| `detect_kahala_yoga(chart)` | Single check |
| `detect_pancha_instrument_yogas(chart)` | Pancha Vadya |
| `detect_vargottama_blessing(chart)` | Vargottama planets |
| `detect_exalted_in_kendra(chart)` | Kendra exaltations |
| `detect_all(chart)` | Aggregator | `list[Blessing]` |
| `summary(chart)` | Summary | `dict` |

### `engine/afflictions.py`

20+ detectors: `detect_mangal_dosha`, `detect_kal_sarp`, `detect_kemadruma`, `detect_pitru_dosha`, `detect_grahan_dosha`, `detect_guru_chandala`, `detect_vish_yoga`, `detect_daridra_yoga`, `detect_combust_planets`, `detect_debilitated_planets`, `detect_dusthana_lords`, `detect_kendra_dushta`, `detect_shrapit_dosha`, `detect_marana_karaka_sthana`, `detect_papakartari`, `detect_retrograde_malefic`, `detect_enemy_sign_placements`, `detect_anapha_absent`, `detect_bhasma_yoga`, `detect_dasha_anti_events`, `detect_shadbala_weak`, `detect_all(chart)`, `summary(chart)`

---

## Strength Calculations

### `runtime/shadbala.py`

| Function | Returns |
|---|---|
| `compute_shadbala(chart)` | 6-fold strength per planet — basic version |

### `runtime/shadbala_full.py`

| Function | Sub-component |
|---|---|
| `uchcha_bala(planet, planet_lon)` | Exaltation strength |
| `ojayugma_bala(planet, sign_idx, navamsa_idx)` | Odd-even sign strength |
| `kendradi_bala(planet, house)` | Angle strength |
| `drekkana_bala(planet, deg_in_sign, sign_idx)` | Decanate strength |
| `saptavargaja_bala(chart, planet)` | 7-varga strength |
| `nathonnatha_bala(planet, hour)` | Day/night strength |
| `paksha_bala(planet, sun_lon, moon_lon)` | Lunar phase strength |
| `tribhaga_bala(planet, hour)` | Tri-third strength |
| `vara_bala(planet, weekday)` | Weekday strength |
| `hora_bala(planet, hour, weekday)` | Hora strength |
| `ayana_bala(planet, sun_lon)` | Ayana (declination) |
| `drik_bala_full(chart, planet)` | Full aspect-based strength |
| `cheshta_bala_full(chart, planet)` | Motion-based strength |
| `compute_shadbala_full(chart)` | Aggregate all 13 sub-balas | `dict` |

### `runtime/ashtakavarga.py`

| Function | Returns |
|---|---|
| `compute_bhinna_ashtakavarga(chart)` | Per-planet bindus per sign |
| `compute_sarvashtakavarga(bhinna)` | Combined bindus across all planets |
| `interpret_house_bindus(house, bindu_count)` | Interpretation string |
| `ashtakavarga_summary(chart)` | Full summary dict |

### `runtime/ashtakavarga_reductions.py`

| Function | Returns |
|---|---|
| `trikona_sodhana(bhinna_av_planet)` | Trikona reduction |
| `ekadhipatya_sodhana(bhinna_av_planet)` | Ekadhipatya reduction |
| `sodhita_ashtakavarga(chart)` | Both reductions combined |
| `kakshya_bala(chart)` | Kakshya bala from refined AV |

### `runtime/vimshopaka_bala.py`

| Function | Returns |
|---|---|
| `planet_dignity_in_varga(chart, planet, varga)` | Dignity per varga |
| `compute_vimshopaka(chart)` | 20-unit varga strength |

### `engine/shadbala.py`

| Function | Returns |
|---|---|
| `compute(positions, lagna_lon, jd_ut=None)` | Engine-side shadbala — returns `dict[planet → BalaScore]` |
| `summary(scores)` | Aggregate report `dict` |

### `engine/ashtakavarga.py`

| Function | Returns |
|---|---|
| `bhinna_ashtakavarga(chart)` | Per-planet bindus |
| `sarva_ashtakavarga(chart)` | Sarva total |
| `trikona_shodhana(bav)` | Reduction step 1 |
| `ekadhipatya_shodhana(bav_after_trikona)` | Reduction step 2 |
| `shodhana(bav)` | Both reductions |
| `bav_strength_label(planet, bindus_in_sign)` | Human label |
| `sav_strength_label(total)` | Human label |
| `transit_strength(chart, transit_planet, transit_lon)` | AV strength of a transit |
| `kaksha_vibhaga(chart, planet)` | Kaksha breakdown |
| `summary(chart)` | Full summary |

### `engine/bhava_bala.py`

| Function | Returns |
|---|---|
| `bhava_bala(chart)` | House strength `dict[house → dict]` |
| `ishta_kashta(chart)` | Beneficence/maleficence per planet |
| `summary(chart)` | Combined report |

---

## Aspects & Conjunctions

### `runtime/aspects_engine.py`

| Function | Returns |
|---|---|
| `aspects_from(pos, planet)` | Houses aspected by a planet |
| `planets_aspecting_house(pos, target_house)` | Reverse lookup |
| `planets_aspecting_planet(pos, target_planet)` | Planet-on-planet aspects |
| `detect_significant_aspects(chart, severity_min=3)` | Filtered aspect list |
| `aspect_summary(chart)` | Full aspect graph |

### `runtime/conjunction_effects.py`

| Function | Returns |
|---|---|
| `relationship(p1, p2)` | Friend/neutral/enemy |
| `detect_conjunctions(chart, orb_degrees=10.0)` | Active conjunctions with effects per house |
| `conjunction_summary(chart)` | Summary report |

### `engine/argala.py`

| Function | Returns |
|---|---|
| `argala_for_sign(chart, target_sign)` | Argala/Virodha for a sign |
| `argala_for_house(chart, house_num)` | Same, by house |
| `activated_houses(chart)` | Houses with active argala |
| `summary(chart)` | Report |

### `runtime/argala_jaimini.py`

| Function | Returns |
|---|---|
| `compute_argala(chart, target_house=None)` | Jaimini argala for any/all houses |
| `argala_summary(chart)` | Summary |

---

## Transits & Forecasting

### `runtime/transit_engine.py`

| Function | Returns |
|---|---|
| `jd_from_dt(when_dt)` | Julian Day from datetime |
| `transit_positions(when_dt)` | Live planet positions |
| `detect_triggers(natal_chart, when_dt, orb=2.0)` | Active transits hitting natal points |

### `runtime/transit_forecast.py`

| Function | Returns |
|---|---|
| `daily_forecast(chart, target_date)` | One-day forecast `dict` |
| `forecast_period(chart, start_date, num_days)` | N-day forecast `list` |
| `find_best_days(chart, start_date, num_days=30)` | Top scoring days |
| `find_difficult_days(chart, start_date, num_days=30)` | Lowest scoring days |

### `engine/gochar.py`

| Function | Returns |
|---|---|
| `get_transit_snapshot(natal_moon_sign_idx, natal_lagna_sign_idx, natal_pos_map, today_jd)` | Snapshot of all transits today |

### `engine/transits.py`

| Function | Returns |
|---|---|
| `saturn_returns(natal_dt, n_returns=3, ...)` | Saturn return dates |
| `sade_sati_windows(...)` | Sade Sati windows |
| `jupiter_transits_sign(...)` | Jupiter sign-by-sign timeline |
| `transit_snapshot(...)` | Engine-side snapshot |

### `engine/forecast.py`

| Function | Returns |
|---|---|
| `forecast_windows(...)` | Predicted future event windows |
| `next_high_LR(...)` | Next high-likelihood window |
| `forecast_summary(chart, months_ahead=24)` | Long-range forecast |

### `engine/conditioned.py`

| Function | Returns |
|---|---|
| `conditioned_LR(...)` | Likelihood ratio with conditions |
| `conditioned_forecast_for_chart(chart)` | LR-adjusted forecast |

### `engine/transit_conditioned.py`

| Function | Returns |
|---|---|
| `transit_conditioned_backtest(n_negative_per_chart=5, ...)` | Backtest the transit-conditioned model |
| `print_report()` | Console report |

### `engine/transit_learn.py`

| Function | Returns |
|---|---|
| `per_factor_lr(counts)` | LR per transit factor |
| `learn_predictors(min_pos_support=3, ...)` | Learn predictors from history |
| `cache_learned(force=False)` | Cache to disk |
| `load_learned()` | Load cached |
| `print_report()` | Report |

---

## Event Prediction

### `runtime/event_predictor_v2.py`

13 event detectors, each takes `(chart, dasha_state, transits, yogas, age)`:

`event_father`, `event_self_accident`, `event_marriage`, `event_career_breakthrough`, `event_education_milestone`, `event_foreign_travel`, `event_wealth_peak`, `event_property`, `event_child_birth`, `event_spiritual`, `event_health_self`, `event_relationship_break`, `event_mother`

Plus:
| Function | Returns |
|---|---|
| `scan_year_v2(chart, year, sample_days=10, min_severity=4)` | Year scan |
| `scan_lifetime_v2(chart, year_from, year_to, sample_days=10, min_severity=4)` | Full life scan |
| `collapse_consecutive(events)` | Smooth same-event runs into bands |

### `runtime/event_predictor.py` (legacy)

`event_father_accident`, `event_mother_event`, `event_accident`, `event_marriage`, `event_career_breakthrough`, `scan_year`, `scan_lifetime`

### `runtime/sade_sati.py`

| Function | Returns |
|---|---|
| `compute_sade_sati_periods(chart, years_horizon=80)` | Saturn 7.5-year cycles |
| `sade_sati_summary(chart)` | Current phase + timeline |

### `runtime/eclipse_impact.py`

| Function | Returns |
|---|---|
| `find_eclipses(year_from, year_to)` | All eclipses in range |
| `analyze_eclipse_impact(natal_chart, eclipse_dt)` | Impact on chart |
| `upcoming_eclipses_impact(natal_chart, years_ahead=3)` | Future eclipses ranked |

### `runtime/chart_rectification.py`

| Function | Returns |
|---|---|
| `recompute_chart(chart_template, hour, minute)` | Re-cast at different time |
| `score_event_match(chart, event_date, event_type)` | Score how well chart predicts event |
| `rectify_birth_time(chart, validated_events, search_minutes=60)` | Back-solve birth time |

### `engine/timeline.py` & `engine/timeline_deep.py`

| Function | Returns |
|---|---|
| `build_timeline(chart, today=None)` | Multi-tier timeline |
| `render_timeline_markdown(chart)` | Markdown rendering |
| `predict_ad_events(chart, today=None, ...)` | AD-level event predictions |

### `engine/timeline_consensus.py`

| Function | Returns |
|---|---|
| `generate_deep_timeline(full_chart)` | Consensus timeline across systems |
| `render_deep_timeline_markdown(native_name, timeline_blocks)` | Markdown |

### `engine/accident.py` / `engine/education.py`

| Function | Returns |
|---|---|
| `detect_accident_patterns(chart)` | List `AccidentPattern` |
| `render_accident_markdown(chart)` | Narrative |
| `predict_subjects(chart, top_n=5)` | Top subject affinities |
| `render_education_markdown(chart)` | Narrative |

---

## Compatibility & Doshas

### `runtime/compatibility_kuta.py`

8 individual kuta scorers:

| Function | Kuta |
|---|---|
| `varna_match(b_rasi, g_rasi)` | Varna (1 point) |
| `vasya_match(b_rasi, g_rasi)` | Vasya (2) |
| `tara_match(b_nak, g_nak)` | Tara (3) |
| `yoni_match(b_nak, g_nak)` | Yoni (4) |
| `graha_maitri_match(b_rasi, g_rasi)` | Graha-Maitri (5) |
| `gana_match(b_nak, g_nak)` | Gana (6) |
| `bhakoot_match(b_rasi, g_rasi)` | Bhakoot (7) |
| `nadi_match(b_nak, g_nak)` | Nadi (8) |
| `ashtakuta_match(boy_chart, girl_chart)` | Aggregate 36-point match |

### `runtime/dosha_cancellations.py`

| Function | Returns |
|---|---|
| `detect_manglik_dosha(chart)` | Manglik with classical exceptions |
| `detect_kaal_sarpa(chart)` | Kaal-Sarpa types |
| `detect_nadi_dosha_full(boy_chart, girl_chart)` | Nadi between two charts |
| `detect_bhakoot_dosha_full(boy_chart, girl_chart)` | Bhakoot between two charts |
| `all_doshas_summary(chart, partner_chart=None)` | All doshas |

---

## Specialty Traditions

### `runtime/jaimini_full.py`

| Function | Returns |
|---|---|
| `compute_arudha_padas(chart)` | All 12 arudhas |
| `upapada_lagna(chart)` | Upapada |
| `darapada(chart)` | Darapada |
| `chara_karakas_jaimini(chart)` | 8 chara karakas with degrees |
| `karakamsa_lagna(chart)` | Karakamsa |
| `jaimini_rasi_aspects(chart)` | Sign-based aspects |
| `jaimini_summary(chart)` | Full Jaimini analysis |

### `runtime/kp_paddhati.py`

| Function | Returns |
|---|---|
| `get_sub_lord(longitude_deg)` | KP sub-lord at longitude |
| `get_sub_sub_lord(longitude_deg)` | Sub-sub lord |
| `cuspal_sub_lord(natal_chart, house_number)` | Sub-lord of any cusp |
| `kp_event_significators(natal_chart, target_house)` | Event significators |
| `kp_summary(natal_chart)` | KP analysis |

### `engine/kp_predictions.py`

| Function | Returns |
|---|---|
| `predictions_for_house(house, max_results=5)` | KP per-house predictions |
| `predictions_for_planet(planet, max_results=5)` | KP per-planet predictions |
| `predictions_for_sublord(sublord_planet, max_results=5)` | Per sub-lord |
| `predictions_for_chart(chart, max_per_house=2)` | All-chart predictions |
| `stats()` | Library size |

### `runtime/lal_kitab.py`

| Function | Returns |
|---|---|
| `detect_lal_kitab_karz(chart)` | 7 karmic debts |
| `asleep_planets(chart)` | Asleep planets |
| `lal_kitab_summary(chart)` | Full summary |

### `engine/lal_kitab.py` (richer)

| Function | Returns |
|---|---|
| `lal_kitab_chart(planet_longitudes)` | Build LK chart |
| `karmic_debts(chart)` | Detect debts |
| `closed_houses(chart)` | Detect closed houses |
| `remedies_for(...)` | Remedies |
| `chart_summary(lk)` | Summary |

### `runtime/nadi_jyotish.py`

| Function | Returns |
|---|---|
| `nadi_analysis(chart)` | Bhrigu Nadi rules + Atmakaraka mission |

### `runtime/medical_astrology.py`

| Function | Returns |
|---|---|
| `medical_analysis(chart)` | Body × planet × house disease prediction |

### `runtime/numerology_vedic.py`

| Function | Returns |
|---|---|
| `mulanka(birth_day)` | Driver number |
| `bhagyanka(birth_day, birth_month, birth_year)` | Destiny number |
| `name_number(name)` | Cheiro name number |
| `vedic_numerology(chart)` | Combined report |

### `engine/tamil_numerology.py`

| Function | Returns |
|---|---|
| `compute(birth_date)` | Tamil numerology report |
| `render_markdown(rpt)` | Tamil markdown |

### `runtime/special_lagnas.py`

| Function | Returns |
|---|---|
| `hora_lagna(chart)` | Hora |
| `ghatika_lagna(chart)` | Ghatika |
| `bhava_lagna(chart)` | Bhava |
| `indu_lagna(chart)` | Indu |
| `pranapada_lagna(chart)` | Pranapada |
| `chandra_lagna(chart)` | Chandra |
| `surya_lagna(chart)` | Surya |
| `all_special_lagnas(chart)` | All 7 |

### `runtime/sahams.py`

| Function | Returns |
|---|---|
| `compute_sahams(chart)` | All 28 Tajik sensitive points |

### `runtime/upagrahas.py`

| Function | Returns |
|---|---|
| `compute_upagrahas(chart)` | 8 upagrahas: Gulika, Mandi, etc. |
| `upagraha_summary(chart)` | Summary |

### `runtime/sibling_predictor.py`

| Function | Returns |
|---|---|
| `predict_siblings(chart)` | Younger/elder count + gender + window |

### `runtime/spouse_inference.py`

| Function | Returns |
|---|---|
| `infer_spouse(natal_chart)` | Full partner description from D1+D9+DK+UL |

### `engine/synth.py`

| Function | Returns |
|---|---|
| `synthesize(chart)` | Full chart synthesis |
| `fact(chart, planet)` | Planet's complete fact dict |
| `planets_for_area(chart, area)` | Relevant planets per life area |
| `lord_of(chart, house)` | House lord |

### `engine/life_domains.py`

| Function | Returns |
|---|---|
| `predict_career(chart)` | Career analysis |
| `predict_marriage(chart)` | Marriage |
| `predict_children(chart)` | Children |
| `predict_wealth(chart)` | Wealth |
| `predict_foreign(chart)` | Foreign travel |
| `predict_family(chart)` | Family |
| `predict_psychology(chart)` | Psychology |
| `predict_spirituality(chart)` | Spirituality |
| `predict_longevity(chart)` | Longevity |
| `render_life_domains_markdown(chart)` | Markdown rendering |

### `runtime/longevity_ayurdaya.py`

| Function | Returns |
|---|---|
| `naisargika_ayurdaya(chart)` | Natural lifespan |
| `pinda_ayurdaya(chart)` | Pinda lifespan |
| `markesha_planets(chart)` | Death-causing planets |
| `categorize_ayu(years)` | Short/Medium/Long category |
| `longevity_analysis(chart)` | Full analysis |

---

## Tier 1 Multi-Tradition

### `runtime/palmistry_engine.py`

| Function | Returns |
|---|---|
| `predict_hand_features_from_chart(chart)` | Predict expected hand features |
| `palmistry_summary(chart)` | Full palmistry analysis |
| `lookup_feature(feature_type, feature_name)` | Direct feature lookup |

### `runtime/vastu_shastra.py`

| Function | Returns |
|---|---|
| `best_directions_for_native(chart)` | Best directions for the native |
| `vastu_summary(chart, house_orientation=None)` | Full Vastu reading |
| `lookup_direction(direction)` | Per-direction details |
| `lookup_room(room_type)` | Room placement rules |
| `lookup_dosha(dosha_name)` | Dosha details |

### `runtime/face_reading.py`

| Function | Returns |
|---|---|
| `predict_face_features(chart)` | Expected facial features from chart |
| `face_reading_summary(chart)` | Full face analysis |
| `lookup_feature(feature_type, feature_name)` | Direct lookup |

### `runtime/body_moles.py`

| Function | Returns |
|---|---|
| `lookup_mole(position, color="Black", side=None, shape="Round", gender="any")` | Specific mole interpretation |
| `list_all_positions()` | All known positions |
| `mole_summary()` | Library overview |

### `runtime/omens_shakuna.py`

| Function | Returns |
|---|---|
| `check_disha_shoola(travel_date, direction)` | Forbidden direction check |
| `lookup_omen(category, omen_name)` | Specific omen |
| `omens_summary()` | Library overview |

---

## Annual Charts (Varshaphala / Tajik)

### `runtime/varshaphala.py`

| Function | Returns |
|---|---|
| `find_solar_return(natal_chart, target_year)` | Solar return moment |
| `compute_muntha(natal_chart, target_year)` | Muntha sign |
| `varshesha(annual_positions, lagna_idx)` | Year-lord |
| `annual_chart(natal_chart, target_year)` | Full annual chart |
| `varshaphala_timeline(natal_chart, year_from, year_to)` | Multi-year timeline |

### `engine/tajik.py` (richer)

| Function | Returns |
|---|---|
| `solar_return_jd(natal_jd, age_years, tol_seconds=30)` | Precise SR JD |
| `muntha(natal_lagna_sign, age_years)` | Muntha details |
| `annual_chart(...)` | Full Tajik chart |
| `varshesha_candidates(chart)` | Candidates for year-lord |
| `select_varshesha(chart)` | Selected year-lord |
| `tajik_yogas(chart)` | Tajik yogas |
| `sahams(chart)` | 28+ sahams |
| `summary(chart)` | Aggregate summary |

---

## Auxiliary & Timing

### `runtime/panchanga.py`

| Function | Returns |
|---|---|
| `jd(when_dt)` | Julian Day |
| `compute_panchanga(when_dt)` | Tithi/Vara/Yoga/Karana/Nakshatra |

### `engine/panchanga.py` (bridge)

| Function | Returns |
|---|---|
| `panchanga(when=None)` | Same as runtime, returns `Panchanga` dataclass |

### `runtime/muhurta_engine.py`

| Function | Returns |
|---|---|
| `tara_bala(natal_nakshatra, date_dt)` | Star strength |
| `chandra_bala(natal_moon_rasi, date_dt)` | Moon strength |
| `muhurta_check(natal_chart, event_dt, event_type="generic")` | Check moment |
| `find_auspicious_dates(natal_chart, year, month, event_type="generic", days=30)` | Find good dates |

### `engine/muhurta.py`

| Function | Returns |
|---|---|
| `score_moment(...)` | Numeric score for an instant |
| `find_windows(...)` | Search good windows |

### `engine/muhurta_verbatim.py`

| Function | Returns |
|---|---|
| `rules_for_activity(activity, max_results=10)` | Verbatim rules |
| `rules_for_dosha(dosha_name, max_results=5)` | Dosha rules |
| `stats()` | Library stats |

### `runtime/prashna_horary.py`

| Function | Returns |
|---|---|
| `cast_prashna_chart(question_dt, lat, lon)` | Cast horary chart |
| `answer_prashna(prashna_chart, question_type, simple=True)` | YES/NO/MAYBE verdict |

### `engine/prashna.py`

| Function | Returns |
|---|---|
| `kp_sublord_at(longitude_degrees)` | KP sub-lord at longitude |
| `cast(question_dt, lat, lon, tz_hours)` | Full PrashnaChart |
| `significators(chart, house)` | Event significators |
| `kp_verdict(chart, house)` | KP verdict |
| `ruling_planets(chart)` | Active rulers |
| `answer(...)` | Full answer with rationale |

### `runtime/tara_chakra.py`

| Function | Returns |
|---|---|
| `get_nakshatra_full(nak_name)` | Nakshatra full info |
| `tara_chakra_summary(chart)` | 9-tara cycle summary |

### `runtime/tri_pataki_chakra.py`

| Function | Returns |
|---|---|
| `tri_pataki(natal_chart, target_dt=None)` | 3-flag verdict for date |
| `annual_tri_pataki_summary(natal_chart, year)` | Full year |

---

## Vedic Core Helpers

### `runtime/vedic_core.py`

Constants: `RASIS`, `RASI_LORDS`, `MOVABLE_SIGNS`, `FIXED_SIGNS`, `DUAL_SIGNS`, `FIRE_SIGNS`/`EARTH`/`AIR`/`WATER`, `PLANETS_MAIN`, `PLANETS_ALL`, `NATURAL_BENEFICS`, `NATURAL_MALEFICS`, `DIGNITIES`, `NAKSHATRAS` (27 + Abhijit).

Helper functions:

| Function | Returns |
|---|---|
| `planet_house(chart, planet)` | House number |
| `planet_sign(chart, planet)` | Sign |
| `planet_dignity(chart, planet)` | "Exalted", "Own", "Friend", "Neutral", "Enemy", "Debil" |
| `is_dignified(chart, planet)` | bool |
| `is_debilitated(chart, planet)` | bool |
| `house_lord(chart, house)` | Planet ruling that house |
| `house_lord_position(chart, house)` | Where house lord sits |
| `house_occupants(chart, house)` | Planets in house |
| `house_sign(chart, house)` | Sign of that house |
| `planet_aspects_houses(chart, planet)` | Houses aspected |
| `is_natural_benefic(planet)` | bool |
| `is_natural_malefic(planet)` | bool |
| `planets_conjunct(chart, p1, p2)` | bool |
| `degree_distance(deg1, deg2)` | Angular distance |

### `engine/evaluator.py`

| Function | Returns |
|---|---|
| `get_functional_nature(ascendant_rasi, planet)` | "Yogakaraka", "Benefic", "Malefic", etc. |
| `get_planetary_dignity(planet, rasi)` | Dignity classification |
| `evaluate_planet(ascendant_rasi, planet, rasi)` | Full evaluation `dict` |

---

## Book Corpus

### `runtime/book_corpus_indexer.py`

| Function | Returns |
|---|---|
| `chunk_book(filepath, book_key, passage_len, overlap)` | Split book into passages |
| `build_index()` | Index all 38 books → JSON |
| `query_index(topic, max_results=5, books=None, min_text_len=200)` | Topic-filtered query |

### `runtime/book_citation.py`

`citation_for(topic, max_results=N)` — quality-filtered citation lookup.

### `runtime/corpus_upgrade.py`

| Function | Returns |
|---|---|
| `extract_missing_pdfs()` | Find and re-extract missing PDF books |
| `verse_quality_score(text)` | Quality 0.0-1.0 |
| `detect_scripts(text)` | Devanagari/Tamil/English detection |
| `build_cross_reference_matrix(index)` | Source × topic matrix |
| `rebuild_corpus_index_v2()` | Full rebuild |
| `report_stats(index, matrix)` | Index report |

### `engine/corpus.py`

| Function | Returns |
|---|---|
| `get_corpus(gemma_dir=None)` | Singleton corpus instance |

`Corpus` class methods:
- `get_planet_in_house(planet, house, limit)`
- `get_planet_in_sign(planet, sign, limit)`
- `get_nakshatra_rules(nakshatra, limit)`
- `get_compound_rules(planets, houses, limit)`
- `get_yoga_rules(yoga_name, limit)`
- `get_dasha_rules(lord, antar_lord=None, limit)`
- `get_transit_rules(planet, limit)`
- `stats` — `dict` with total_unique_rules, books_loaded, etc.

### `engine/book_rules.py`

| Function | Returns |
|---|---|
| `load_rules()` | All BookRule objects |
| `match_for_chart(chart, rules=None)` | Rules that match the chart |
| `to_predictions(matched, category, ...)` | Convert to Prediction objects |
| `predictions_for(chart, category, max_per_category=8)` | Direct chart→predictions |

### `engine/deep_rules.py`

| Function | Returns |
|---|---|
| `load_deep_rules()` | All DeepRule objects |
| `match_for_chart(chart, rules=None)` | Matched rules |
| `predictions_for(chart, category, ...)` | Predictions |

### `engine/bhrigu_predictions.py`

| Function | Returns |
|---|---|
| `predictions_for(planet, house, max_results=5)` | Bhrigu Samhita predictions |
| `predictions_for_chart(chart, max_per_planet=3)` | Full chart predictions |
| `stats()` | Library size |

### `engine/verse_locator.py`

| Function | Returns |
|---|---|
| `cite(query, max_results=20)` | Citation query |
| `rules_about(planet=None, house=None, ...)` | Rules-by-component query |
| `stats()` | Library stats |

### `engine/remedies.py` & `engine/remedies_verbatim.py`

| Function | Returns |
|---|---|
| `remedies_for(affliction)` | Remedies for one affliction |
| `remedies_for_chart(chart)` | Per-chart remedies |
| `remedies_for_planet(planet)` | Verbatim per planet |
| `remedies_in_category(category)` | Per category |
| `remedies_for_affliction_code(code, involved_planets)` | Code-based |

---

## Reading Generation

### `runtime/generate_report.py`

| Function | Returns |
|---|---|
| `generate(chart_path, out_name)` | Full PDF report (~55 pages, 977 elements) |
| `vimshottari(chart)` | Internal — dasha extraction for report |
| `detect_yogas(chart)` | Internal — yoga aggregation for report |
| `chara_karakas(chart)` | Internal — karakas for report |
| `all_predictions(chart)` | Internal — all 18 domain pages |
| `chapter_with_narrative(num, planet, dates, ages, theme, chart, sub_dashas, today, is_current)` | Per-chapter narrative |
| `domain_page(icon, number, title, subtitle, items, intro_paragraph=None)` | Per-domain page |
| `build_expect_watch(planet, chart)` | EXPECT/WATCH tables for a dasha |
| `expect_watch_table(expect_rows, watch_rows)` | Render the table |
| `snapshot_card(facts)` | Snapshot card for chapter |
| `build_page1(chart, mds, cur_ad)` | Cover page |

### `engine/reading.py`

| Function | Returns |
|---|---|
| `generate_reading(chart)` | Full Reading object |

### `engine/client_report.py` / `_v2.py` / `_ta.py` / `_v2_ta.py`

| Function | Returns |
|---|---|
| `generate_client_report(chart)` | English client-facing report (markdown) |
| `generate_client_report_v2(chart)` | V2 English |
| `generate_client_report_ta(chart)` | Tamil V1 |
| `generate_client_report_v2_ta(chart)` | Tamil V2 |

### `engine/chapters.py` / `engine/chapters_ta.py`

| Function | Returns |
|---|---|
| `build_chapters(chart, today=None, ...)` | Chapter list |
| `render_chapters_markdown(chart)` | English markdown |
| `render_chapters_markdown_ta(chart)` | Tamil markdown |

### `engine/narrative.py` / `engine/narrative_ta.py`

| Function | Returns |
|---|---|
| `affliction_narrative(code, name, severity, ...)` | English narrative for an affliction |
| `blessing_narrative(name, strength, description, ...)` | Blessing narrative |
| `forecast_narrative(event, posterior, lr, ...)` | Forecast narrative |
| `planet_in_house_intro(planet, house)` | Per-planet intro |
| `house_strength_remark(score)` | Strength comment |
| `dasha_age_phrase(start_year, birth_year, mahadasha)` | Age phrase |
| `opening_salutation(name)` / `closing_blessing()` | Frame text |
| `*_ta(...)` | Tamil variants |

### `engine/timeline_consensus.py` / `engine/timeline_deep.py` / `engine/timeline_ta.py`

| Function | Returns |
|---|---|
| `generate_deep_timeline(full_chart)` | Cross-system timeline |
| `render_deep_timeline_markdown(...)` | Markdown |
| `render_timeline_markdown_ta(chart)` | Tamil |

### `engine/cli.py` & `engine/web.py`

| Function | Returns |
|---|---|
| `engine.cli.main()` | Engine-side CLI entry |
| `engine.web.index/chart/api_chart/health/main` | Flask routes |

### `engine/comparative_test.py`

| Function | Returns |
|---|---|
| `synthesize_consensus(rules)` | Cross-book consensus |
| `get_aspected_houses(planet, current_house)` | Aspect houses |
| `execute_corpus_battle_comparison(chart_data, focus_lords=None)` | Multi-book battle report |

### `engine/consensus_report.py`

| Function | Returns |
|---|---|
| `render_consensus_meter(consensus_data)` | Meter widget |
| `render_client_narrative(subject, consensus_data)` | Client text |
| `generate_consensus_report_markdown(battle_results)` | Full markdown |

### `engine/synthesis.py`

| Function | Returns |
|---|---|
| `generate_synthesis(data)` | Final integrated synthesis text |

---

## Calibration & Backtesting (engine/)

### `engine/calibration.py`

| Function | Returns |
|---|---|
| `event_priors(backtest_result=None)` | Per-event base rates |
| `forecast_confidence(...)` | Bayesian confidence |
| `brier_score(backtest_result=None)` | Brier score |
| `print_report()` | Console report |

### `engine/backtest.py`

| Function | Returns |
|---|---|
| `score_chart(chart)` | Score a known chart |
| `run_full_backtest()` | Run backtest across all known charts |

### `engine/affliction_backtest.py` / `blessing_backtest.py` / `negative_backtest.py` / `chart_relative_backtest.py`

| Function | Returns |
|---|---|
| `run_*_backtest(...)` | Run specific backtest |
| `print_report(...)` | Report |
| `compare_with_universal()` | Comparison |

### `engine/severity_refit.py`

| Function | Returns |
|---|---|
| `refit_severities(min_n=2)` | Empirical refit |
| `cache_refit(force=False)` | Cache to disk |
| `load_refit()` | Load |
| `empirical_severity(code, fallback)` | Get refit severity |

### `engine/tier_refit.py`

| Function | Returns |
|---|---|
| `per_lord_lr(event_type, n_negative_per_chart=5)` | LR per lord |
| `refit_event_patterns(...)` | Refit patterns |
| `load_refit()` / `compare(event_type)` / `build_and_cache(force=False)` / `print_comparison()` | Refit utilities |

### `engine/learned_ensemble.py`

| Function | Returns |
|---|---|
| `fit_all(n_iter=1000)` | Train ensemble |
| `cache_weights(force=False)` | Cache weights |
| `predict_proba(event_type, ...)` | Predict probability |

### `engine/ensemble.py`

| Function | Returns |
|---|---|
| `ensemble_score(...)` | Ensemble combination |
| `backtest_ensemble(n_negative_per_chart=5)` | Backtest |
| `print_ensemble_report()` | Report |

### `engine/cross_check.py` / `engine/cross_validate.py`

| Function | Returns |
|---|---|
| `cross_check_chart(...)` | Cross-check single chart |
| `cross_check_known_charts(top_n=5)` | Cross-check across library |
| `cross_check_domain(chart, domain)` | Per-domain check |
| `render_cross_validation_markdown(chart)` | Markdown |

### `engine/feedback.py` / `engine/event_feedback.py`

| Function | Returns |
|---|---|
| `record_feedback(chart, prediction_id, module, ...)` | Log feedback |
| `confirm_event(chart, event, actual_date)` | Confirm event happened |
| `get_module_weights()` / `apply_module_weight(...)` / `get_weights()` / `apply_weight(...)` / `history_for(chart)` / `summary()` | Feedback queries |

### `engine/known_charts.py`

| Function | Returns |
|---|---|
| `all_charts()` | All known charts |
| `by_quality(min_quality="A")` | Filter by quality |
| `by_event_type(event_type)` | Charts with given event |
| `stats()` | Library stats |

---

## Localization & Rendering

### `engine/i18n.py`

| Function | Returns |
|---|---|
| `translate(field_type, value, lang="en")` | Translate any field |
| `translate_severity(value, lang)` | Severity translation |
| `translate_strength(value, lang)` | Strength translation |
| `translate_remedy_type(value, lang)` | Remedy type |
| `translate_section(value, lang)` | Section header |
| `translate_weekday(value, lang)` | Weekday |
| `localize_when(when, lang)` | Localize date phrase |
| `locale(lang="en")` | Locale dict |
| `localize_chart(chart_summary, lang="en")` | Localize entire chart summary |

### `engine/chart_render.py`

| Function | Returns |
|---|---|
| `render_south(chart, lang="en", size=480)` | South Indian SVG |
| `render_north(chart, lang="en", size=480)` | North Indian SVG |
| `save(svg_str, path)` | Save SVG to file |

### `engine/pdf_render.py`

| Function | Returns |
|---|---|
| `render_pdf(markdown_text, output_path)` | Markdown → PDF |

### `engine/traits_72.py`

| Function | Returns |
|---|---|
| `all_traits(chart)` | 72 archetypal traits |
| `render_72_traits_markdown(chart)` | Markdown |

### `engine/life_narrative.py`

| Function | Returns |
|---|---|
| `timeline_table(chart, today=None, ...)` | Tabular timeline |
| `ask(chart, question, today=None)` | Q&A — natural-language `Answer` |
| `full_narrative(chart, today=None)` | Full narrative text |

---

## Notes on Stability

- `runtime/` is **the modern API**. New work goes here. Modules listed under `runtime/` are stable.
- `engine/` is **the original API**. Some modules (those with bridges) are thin shims; others (afflictions, blessings, traits_72, learned_ensemble, calibration) are richer than the runtime equivalents and should keep being used directly.
- `runtime/event_predictor.py` (v1) is **legacy** — use `event_predictor_v2.py` for new code.
- `runtime/dasha_systems_full.py` is **uncalled by orchestrator** — its `compute_kalachakra/shoola/sthira/drig/niryana_shoola` functions are accessible but not in the standard run.
- `runtime/_patch_predictions.py` is a monkey-patch utility, not a public API.
- The two **PDF generators** (`runtime/generate_report.py` and `engine/pdf_render.py`) are not interchangeable — the former is the deep-narrative ReportLab version, the latter is markdown→PDF.

When in doubt, call `engine_unified.unified_analysis(chart)` — it picks the correct entry point for every capability and returns a single merged result.
