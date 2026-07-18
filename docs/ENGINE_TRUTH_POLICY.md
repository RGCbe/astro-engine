# Making the Engine True for Clients

Your goal: **every field the client sees is honest about what it is** � not marketing accuracy, not celebrity backtests, not fake certainty.

## The three layers clients should see

| Layer | What it is | Client label | Example |
|-------|------------|--------------|---------|
| **Mechanical** | Swiss Ephemeris + dasha math | �Calculated chart� | Moon in Pushya, Venus MD until 2028 |
| **Cited** | Text from your Books index | �Classical citation� | BPHS � �When Venus is in the 7th�� |
| **Synthesis** | Your code summarizing signals | �Summary (interpretive)� | �High-potential phase�� |

Never present **synthesis** or **book-battle consensus %** as �the stars guarantee this will happen.�

## What must NOT run in production

These are **research only** (Vijay 100% came from here):

- `scratch/astro_numerology_weights.json`
- `scratch/optimize_*.py`, `scratch/vijay_*.py`
- `runtime/_battle_vijay.py` calibrated mode (year-specific hacks)

Live API (`main.py`) already uses:

- `event_predictor_v2` (rule-based life events)
- `engine/corpus.py` (book passages)
- `engine/dasha_compute.py`, shadbala, yogas

**Rule:** No `import` from `scratch/` in `main.py` or `engine_orchestrator.py`.

## How to act (operating rules)

### 1. Birth data first

Wrong time or place ? wrong chart ? every �prediction� is wrong.

- Ask clients for **exact birth time** (not �around noon�).
- Store `place`, `lat`, `lon`, and document timezone (today: IST +5.5 in core `jathagam`).
- Show `truth.computation.timezone_note` in API responses.

### 2. Separate �calculation� from �meaning�

**Always show:**

1. Raw positions and dasha dates (mechanical)
2. Book quotes with `source` (cited)
3. Summary last, labeled as interpretive (synthesis)

### 3. Book-battle honesty

`consensus_percent` = �how many indexed rules sound auspicious vs inauspicious� � **not** �chance this will happen.�

UI/API should say: *�Agreement among classical texts for this placement.�*

### 4. No accuracy claims to clients

Do not advertise Vijay 100%, 68-film pooled %, or internal battle scores.

Internal QA only: `python runtime/_battle_vijay.py` (see `docs/VIJAY_ACCURACY_EXPLAINED.md`).

### 5. Validation before each release

```bash
cd F:/astro
python runtime/_battle_vijay.py          # internal QA only
python test_full_integration.py          # imports + 4 charts
python scratch/test_monetization.py      # tier gates (server up)
```

Add hold-out charts (not Vijay) before claiming �accurate engine.�

### 6. When a module fails, say so

Partial failures are hidden today (`except: pass`). Truth policy adds `truth.partial_failures` when modules error � clients should see �KP unavailable� not silence.

### 7. Monetization without lying

- Free tier = fewer **citations** and shorter dasha, not fake locked data that looks real.
- Pro tier = full corpus + PDF, not �more true� � same math, more depth.

## API: `truth` block

Every `jathagam` and `book-battle` response includes:

```json
"truth": {
  "policy_version": "1.0",
  "disclaimer": "...",
  "layers": { "mechanical": {...}, "cited": {...}, ... },
  "not_guaranteed": [...],
  "computation": { "ephemeris": "Swiss Ephemeris", ... }
}
```

Frontend should show the disclaimer once per session.

## Roadmap (truth improvements)

| Priority | Work | Why |
|----------|------|-----|
| P0 | Done: truth block in API | Clients know what they read |
| P1 | Timezone per birth place (not only IST) | Mechanical truth |
| P2 | Surface module errors in response | No silent wrong charts |
| P3 | Hold-out celebrity tests (no tuning on test set) | Honest accuracy |
| P4 | Confidence on life events (severity + window width) | No binary �100%� feel |

## One sentence for your website

*�We compute your Vedic chart with Swiss Ephemeris and show matching passages from classical texts; summaries are interpretive guides, not guarantees.�*

That is a **true** engine clients can trust.
