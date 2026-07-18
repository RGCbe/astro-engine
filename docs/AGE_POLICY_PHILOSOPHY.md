# Age policy philosophy

**Related:** [ROOT_CAUSE_MARRIAGE_AT_12.md](./ROOT_CAUSE_MARRIAGE_AT_12.md) � why Venus MD at age 12 fired `event_marriage` (rule semantics, not calc bug).

The engine predicts **what the chart and dasha indicate at a given age** � it does not silently delete astrologically valid but socially unusual timings.

## Wrong vs right

| Wrong | Right |
|-------|-------|
| Hard filter "no marriage before 18" | Typical band 18�45; allow early/late when signal is strong |
| Hide child marriage at 16 because rule says min 18 | Show at 16 with client label if chart + dasha support it |
| Drop band with no explanation | Label: *"Unusual age � strong chart indication; verify with life facts"* |

Child marriage is rare. If the native married at 16 and the chart JSON documents it (`known_events`), that age is **100% correct for that chart** � the engine must **allow**, not **block**.

## Classification (`classify_age_fit`)

Each band gets an `age_fit` tag after `filter_bands_for_age`:

| Tag | Meaning | Client report |
|-----|---------|---------------|
| `typical` | Inside typical_min..typical_max | Normal row |
| `early_exception` | Below typical but allowed (strong signal or early_allow_age) | Prefix `? Early (age X) � strong signal:` |
| `late_exception` | Above typical but allowed | Prefix `? Late (age X) � strong signal:` |
| `unlikely` | Absurd age or weak signal outside typical | **Omitted** from client timeline |

### Marriage examples

| Age | Severity | Result |
|-----|----------|--------|
| 25 | any | `typical` � show normally |
| 16 | any | `early_exception` � **show** with warning prefix |
| 12 | ? 4 (or 3 + multiple why-lines) | `early_exception` � show with prefix |
| 12 | < 4 | `unlikely` � **hide** |
| 4 | any | `unlikely` � **hide** (absurd_min = 12) |
| 52 | ? 4 | `late_exception` � show with prefix |
| 16 + `known_events` marriage | any | `typical` � known_events always win |

### Absurd hard drops (always `unlikely`)

| Category | absurd_min | absurd_max |
|----------|------------|------------|
| marriage*, engagement*, romance | 12 | 85 |
| children*, pregnancy | 10 | 55 |
| career*, fame*, job | 8 | 75 |
| retirement | 25 | 90 |
| father*, mother* | 0 | 99 (no filter) |

## API (`engine/event_age_policy.py`)

```python
from engine.event_age_policy import (
    classify_age_fit,
    filter_bands_for_age,      # annotates age_fit; drops unlikely only
    band_fits_puthi_window,
    client_age_label,
    known_event_at_age,
    CATEGORY_AGE_RULES,
)
```

- **`filter_bands_for_age(chart, bands)`** � sets `band["age_fit"]` and `band["age_at_start"]`; drops only `unlikely`.
- **`band_fits_puthi_window`** � overlap must not be `unlikely` for client Puthi tables.
- **`known_event_at_age`** � chart JSON ground truth overrides classification to `typical`.

## Layers

1. **`event_predictor_v2`** � per-pattern scan-time gates (unchanged; first pass).
2. **`filter_bands_for_age`** � annotate + drop absurd/weak only.
3. **Timeline display** � `client_age_label()` prefixes early/late exceptions.

## Regenerate Manoj timelines

```bash
python F:\astro\scratch\_manoj_dasha_puthi_timeline.py
```

See also `docs/event_age_policy.md` (rule table) and `DEEP_EVENT_NARRATIVE_SPEC.md`.
