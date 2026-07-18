# Deep Event Narrative Spec

## Purpose

Client reports must explain **where** money or outcomes come from and **how** setbacks show up � not only category labels like `wealth` or `wealth_loss`.

This layer sits on top of `event_predictor_v2` bands and Vimshottari Puthi windows. It does **not** claim certainty.

## P0 (implemented)

| Component | Path | Role |
|-----------|------|------|
| Narrative inference | `engine/event_narrative.py` | `infer_source_and_mechanism(chart, category, why_list, dasha_ctx)` |
| Puthi rollup | same | `summarize_puthi_narrative`, `aggregate_puthi_summary` |
| Manoj timeline | `scratch/_manoj_dasha_puthi_timeline.py` | Nested structure per Puthi |

### Return shape

```python
{
  "source_tags": ["land", "business"],
  "mechanism_tags": ["legal", "delay"],
  "mechanism_en": "�",
  "client_en": "� Mechanical inference, not guaranteed.",
  "client_ta": "�",
  "houses": [4, 10, 11],
  "confidence": "moderate",
}
```

### House mapping (any lagna)

| House | Gain source | Loss mechanism |
|-------|-------------|----------------|
| 2 | inheritance / savings | � |
| 4 | land / property | � |
| 5 | speculation / creative | � |
| 7 | spouse / contracts | partnership break |
| 9 | father / dharma | � |
| 10 | salary / profession | � |
| 11 | network / gains | � |
| 6 | � | medical / legal |
| 8 | � | sudden shock |
| 12 | � | expense / abroad drain |

Active **MD/AD** lords and `why[]` hints (e.g. `4L`, `12L MD`) refine tags.

### Puthi report structure (mandatory)

```markdown
## Mahadasha (Moon) | dates | age

### Puthi N: Moon-Rahu | start � end | age
**Active lords:** �
**Likely income sources:** �
**How losses may occur:** �
**Career highlights (this Puthi):** � (when bands present)
**Marriage / relationship (this Puthi):** � (when bands present)
**Life events in this Puthi only:**
| dates | event | source/mechanism TA+EN | strength |
**Expect:** �
**Watch:** �
---
```

Event filter: `band.start <= puthi.end AND band.end >= puthi.start`. Life-domain categories are preferred over long generic auxiliary events.

### Age policy (`engine/event_age_policy.py`)

Bands get `age_fit`: `typical`, `early_exception`, `late_exception`, or `unlikely`. `filter_bands_for_age` annotates bands and drops only `unlikely` (absurd ages, e.g. marriage at 4). Early marriage at 16 shows with client warning prefix; `known_events` in chart JSON always win. See `docs/AGE_POLICY_PHILOSOPHY.md` and `docs/event_age_policy.md`.

## P1 (planned)

- Push narrative into `event_predictor_v2` return payload at scan time
- PDF / Tamil client report parity with `client_report_v2`
- Calibrate tags against `known_events` / feedback DB
- Upapada / D9 marriage source refinement

## Honesty policy

- Use **mechanical inference** / **moderate confidence** wording only.
- Never label outputs as 100% guaranteed.
- Verified life events (user-confirmed) may be noted separately in accuracy tooling � not in narrative text.

## Regenerate Manoj timelines

```bash
python F:\astro\scratch\_manoj_dasha_puthi_timeline.py
```

Output: `category_report_dir("manoj")` ? `MANOJ_DASHA_PUTHI_TIMELINE_TA.md`, `MANOJ_DASHA_PUTHI_TIMELINE_EN.md`.

## Smoke test

```bash
python -c "import json; from pathlib import Path; import sys; sys.path.insert(0, r'F:\\astro\\engine'); from event_narrative import infer_source_and_mechanism; c=json.loads(Path(r'F:\\astro\\charts\\manoj_chart.json').read_text(encoding='utf-8')); r=infer_source_and_mechanism(c,'wealth',[],{'md':'Moon','ad':'Rahu'}); print(r['client_en'][:120])"
```
