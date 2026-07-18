# Event age policy

Life-event bands use **typical age bands** plus **early/late exceptions** � not hard min/max deletion. Central rules live in `engine/event_age_policy.py`. Philosophy: `docs/AGE_POLICY_PHILOSOPHY.md`.

## Usage

```python
from engine.event_age_policy import (
    age_at,
    classify_age_fit,
    is_age_appropriate,
    filter_bands_for_age,
    band_fits_puthi_window,
    client_age_label,
    CATEGORY_AGE_RULES,
)
```

- **`classify_age_fit(age, category, severity)`** ? `typical` | `early_exception` | `late_exception` | `unlikely`
- **`filter_bands_for_age(chart, bands)`** � annotates `age_fit` on each band; drops only `unlikely` (e.g. marriage age 4).
- **`band_fits_puthi_window(chart, band, puthi_start, puthi_end)`** � overlap age must not be `unlikely`.
- **`client_age_label(band, lang)`** � warning prefix for early/late exceptions in reports.

## Rules (typical / absurd)

| Pattern | Typical | Absurd (hard drop) | early_allow |
|---------|---------|-------------------|-------------|
| marriage*, engagement*, affair, romance | 18�45 | 12�85 | 16 |
| children, pregnancy | 18�45 | 10�55 | 16 |
| career*, job, promotion, business*, fame* | 14�65 | 8�75 | 10 |
| political_office | 21�75 | 18�80 | 19 |
| lottery*, speculation* | 18�65 | 16�75 | 17 |
| father*, mother* | 0�99 | 0�99 | 0 |
| education* | 3�35 | 3�40 | 3 |
| property*, vehicle | 18�99 | 16�99 | 17 |
| retirement | 45�70 | 25�90 | 40 |

Unmatched categories are not age-filtered (implicit typical 0�99).

**Early exception below typical:** age ? `early_allow_age`, OR severity ? 4 (or sev ? 3 with multiple why-lines).

**Late exception above typical:** strong signal, OR age within typical_max + 15 years.

**known_events** in chart JSON always classify as `typical` at matching age.

## Layers

1. **`event_predictor_v2`** � per-pattern `if age < N: return None` at scan time.
2. **`filter_bands_for_age`** � after `collapse_consecutive` / `rank_and_consume`.
3. **`band_fits_puthi_window`** + **`client_age_label`** � Puthi timeline client display.

See also `DEEP_EVENT_NARRATIVE_SPEC.md` � Age policy.
