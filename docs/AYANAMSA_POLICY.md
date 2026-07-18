# Ayanamsa policy � old tradition, modern engine

## Primary (default for Tamil Nadu jathagam)

**Thirukanitham (????????????)** � pinned to Logic Vision display **23�40?45?** (~23.6792�) for the 1996 Manoj era, applied via Swiss Ephemeris `SIDM_USER` with linear precession.

Auto-selected when birthplace is in:

- Tamil Nadu, Kerala, Puducherry, south AP, Sri Lanka (`engine/ayanamsa_picker.py`)

This matches **printed jathagams** (AstroSign / Logic Vision), not the national Lahiri calendar alone.

## Modern option (explicit override)

**Lahiri** � Government of India / Drik Panchang / JHora / AstroSage standard.

Use when:

- Client asks for �Lahiri only�
- Birth outside TN print tradition
- Cross-check against mainstream apps

```python
build_sidereal_chart(..., tradition_hint="lahiri")
```

## How it is modernized

| Old world | Our implementation |
|-----------|-------------------|
| Fixed tables in desktop software | **Swiss Ephemeris** (JPL DE431) |
| One software�s ayanamsa | **`ayanamsa_picker`** by lat/lon + optional hint |
| Opaque print value | **Pinned degrees** + documented DMS (23:40:45) |
| Mixed Lahiri on charts | **`chart_builder.build_sidereal_chart`** uses picker by default |

## API

- `engine/ayanamsa_picker.pick(lat, lon, tz)` � choose tradition  
- `engine/ayanamsa_picker.configure_swe_ayanamsa(jd, choice)` � apply to swe  
- `engine/chart_builder.build_sidereal_chart(..., tradition_hint=..., ayanamsa_deg=...)`

Chart JSON fields: `ayanamsa`, `ayanamsa_mode`, `ayanamsa_name`.

## Rebuild Manoj fixture

```powershell
cd F:\astro
python scratch/rebuild_client_chart.py charts/manoj_chart.json
```
