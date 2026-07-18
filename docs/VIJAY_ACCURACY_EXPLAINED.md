# Why Vijay �100%� Is Not Real Predictive Accuracy

If the engine reports **100%** on Vijay�s movies or life events, that number measures **backtest fitting**, not fortune-telling skill.

## What was actually measured

| Report | What it really tests |
|--------|----------------------|
| `VIJAY_BATTLE.json` ? NEW 28/28 | Hand-tuned GAC scorer + Vijay-only rules, not the live API |
| `astro_numerology_weights.json` | Weights **optimized on Vijay�s 68-film list** until accuracy hit 100% |
| `scratch/vijay_all_68_movies.py` | �Do any corpus dasha rules sound like hit/flop?� � not a single yes/no per film |

The **live** site (`/api/jathagam`, `/api/book-battle`) does **not** use the Vijay-tuned GAC weights. It uses `event_predictor_v2`, corpus rules, and dasha � which scored **~86%** on the same 28 events (OLD engine in battle).

## Why 100% is inflated (technical)

1. **Training on the test set** � `optimize_astro_numerology.py` adjusted weights until Vijay�s known releases all �passed.� That is classic overfitting.
2. **Vijay-only hacks** in `runtime/_battle_vijay.py` (calibrated mode), e.g. extra score if `year == 2012`, �double-Rahu� boosts, father-death overrides tied to his chart.
3. **Loose time windows** � OLD engine counts a hit if *any* prediction falls within **�180 days** (�450 for year-only dates). Almost any dasha band will overlap something.
4. **Category guessing** � Many events use only `atro_category` (e.g. all `career` = �expect auspicious�), not whether the line says **flop** vs **blockbuster**.
5. **Free passes** � `travel` and `spiritual` events were marked hit whenever the category was �neutral� (always `True`).
6. **68-film script** � Counts matching **individual rule snippets**, then pools hits across films. More rules ? easier to show a high percentage.

## Honest numbers to trust

Run:

```bash
cd F:/astro
python runtime/_battle_vijay.py
```

You will see:

- **OLD (strict)** � `event_predictor_v2`, �45 day window, per-event valence from text  
- **NEW calibrated** � research mode (the old �100%� path)  
- **NEW strict** � same GAC idea, **no Vijay year hacks**, valence from event text  

Expect strict NEW to land near the **64% baseline** documented in `NEW_ENGINE_IMPROVEMENT_OPPORTUNITIES.md`, not 100%.

## What would be scientifically fair

1. **Hold-out chart** � Tune on 8 actors, test on Vijay (or vice versa) with **one** weight file.  
2. **Blind dates** � Predict release windows **before** looking up box office.  
3. **Per-film binary** � One prediction per movie (auspicious / inauspicious), �30 days, no corpus rule pooling.  
4. **Report confidence** � Show dasha window + score, not only hit/miss.

Until then, treat Vijay 100% as **internal QA on a celebrity calibration chart**, not proof the engine predicts movies for everyone.
