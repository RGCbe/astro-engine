"""
Astro unified engine.

Layered architecture (see /opt/astro/UNIFIED_ENGINE_PLAN.md):
  Layer 0 - Resolve (geocode, ayanamsa, ephemeris)
  Layer 1 - Compute (positions, vargas, dashas, balas, KP, Lal Kitab)
  Layer 2 - Match (canonical clusters + authority hierarchy)
  Layer 3 - Synthesize (LLM + citations)
  Layer 4 - Validate (known charts, marriage dataset, Jhora cross-check)

Submodules:
  kp_sublord         - KP sub-lord lookup (Layer 1, KP school)
  vargas             - All 16 divisional charts D1-D60 (Layer 1)
  dasha              - Vimshottari (120yr) + Ashtottari (108yr) periods (Layer 1)
  raasi_dasha        - Jaimini Chara / Sthira / Shoola raasi dashas (Layer 1)
  kalachakra         - Kalachakra dasha (BPHS Ch.49) — BETA, Tradition A only
  panchanga          - Tithi/Nakshatra/Yoga/Karana/Vara + auspicious windows (Layer 0+1)
  yogas              - 12 classical yoga detectors (Pancha Mahapurusha, Raja, Dhana, etc)
  shadbala           - Planetary strength (4 of 6 balas)
  kuta               - 36-point Ashta-Kuta marriage compatibility + Mangal Dosha
  lal_kitab          - Lal Kitab fixed-zodiac engine: pakka ghar, karmic debts, remedies
  tajik              - Annual horoscope (solar return + Muntha + Varshesha + sahams)
  prashna            - Horary engine (KP cusp sub-lord verdict + Krishneeyam significators)
  muhurta            - Electional engine (auspicious-time finder for activities)
  geocode            - Worldwide city → (lat, lon, tz) (Layer 0)
  marriage_outcomes  - 689 documented marriages for empirical validation (Layer 4)
  chart              - Single-call full pipeline wrapper
  reading            - Auto-narrative reading w/ tier-weighted citations from v6 corpus
  backtest           - Tiered classical-pattern backtest (primary/secondary/miss)
  negative_backtest  - Bayesian likelihood ratios via non-event-year sampling
  tier_refit         - Empirical (LR-based) tier refit; surfaces classical-vs-data disagreements
  calibration        - Probabilistic confidence + Brier score + Bayesian posteriors
  transits           - Gochara: Saturn returns, Sade Sati, Jupiter transits, snapshot
  chart_render       - SVG renderers for North & South Indian style D1 charts
  cross_check        - PyJHora cross-validation harness (5/5 charts pass on Manoj corpus)
  chart_relative     - Per-chart-relative event scoring (10th lord, AmK, Putrakaraka, etc.)
  chart_relative_backtest - LR comparison: chart-relative vs universal-karaka
  transit_conditioned - Dasha+transit conjunction LRs (CHILDREN_BORN 1.12→2.15, etc.)
  transit_learn      - Empirically-learned transit predictors per event
  ensemble           - Combined LR (universal + chart-relative + transit) per Bayes
  forecast           - Real-time event-window finder (next 24mo) with valence flag
  afflictions        - Detect EVERY classical bad: 5 rins, 8 doshas, debilitation,
                        combust, dusthana lords, malefic kendras (mission-critical)
  blessings          - Symmetric counterpart: Pancha Mahapurusha, Raja, Dhana,
                        Vipareeta Raja, Neecha Bhanga, Gajakesari, Sunapha/Anapha,
                        Lakshmi, Saraswati, Adhi yogas
  remedies           - Concrete remedy table per affliction (Lal Kitab + Vedic
                        mantra + behavioral + donation + gemstone-with-caveat)
  synthesis          - LLM synthesis chain (Cerebras / OpenRouter free / Gemini
                        / Groq) — bad-finder + good-finder + remedy + activation
  web                - Flask UI + JSON API (/, /chart, /api/chart, /api/health)
  i18n               - Multi-language output (en/sa/hi/ta) with truth-directive intact
  cli                - Command-line entry point: python -m engine.cli ... [--lang en|sa|hi|ta]
"""

__version__ = "1.1.0"

# v0.9 audit-resolved modules:
#   ashtakavarga      - Bhinna + Sarva + Trikona/Ekadhipatya shodhana (BPHS Ch.49)
#   bhava_bala        - 12-house strength + Ishta-Kashta Phala (BPHS Ch.31-32)
#   conditioned       - Affliction/blessing modifiers applied to ensemble LR
#   varga_weighted    - D9/D10/D24/D60 used to adjust event LR
#   blessing_backtest - Symmetric to affliction_backtest (truth-directive)
#   severity_refit    - Empirical severity from backtest lift (auto-promote)
#   argala            - Jaimini intervention/obstruction analysis
#   learned_ensemble  - Logistic regression replaces naive-Bayes product
#   shadbala (full)   - All 6 balas + 5 Sthana sub-balas (was 4 of 6)
