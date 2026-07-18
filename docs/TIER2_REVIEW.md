# Tier 2 Module Review — 5 Modules

**Review date**: 2026-05-06
**Reviewer**: Atro Review Agent
**Modules reviewed**:
1. `runtime/dasha_systems_full.py` — 5 advanced Vedic dashas
2. `runtime/muhurta_extended.py` — 14 specialized muhurta types
3. `runtime/tajik_yogas_16.py` — 16 Tajik yogas + 5 Balas
4. `runtime/expanded_yogas.py` — 250+ named classical yogas
5. `runtime/nadi_full.py` — 108 narrative cells + karaka readings

**Reference modules** (gold standard):
- `runtime/comprehensive_yogas.py`
- `runtime/granular_dasha.py`
- `runtime/varshaphala.py`
- `runtime/vedic_core.py`

---

## Executive Summary

| Module | Verdict | BLOCKER | MAJOR | MINOR | NIT |
|--------|---------|---------|-------|-------|-----|
| `dasha_systems_full.py` | NEEDS REVISION | 4 | 5 | 4 | 3 |
| `muhurta_extended.py` | PASS WITH FIXES | 1 | 4 | 5 | 3 |
| `tajik_yogas_16.py` | NEEDS REVISION | 3 | 6 | 4 | 2 |
| `expanded_yogas.py` | NEEDS REVISION | 2 | 7 | 6 | 3 |
| `nadi_full.py` | PASS WITH FIXES | 0 | 3 | 3 | 2 |
| **TOTAL** | | **10** | **25** | **22** | **13** |

**Pass count**: 1 (nadi_full)
**Pass-with-fixes count**: 1 (muhurta_extended)
**Needs-revision count**: 3 (dasha_systems_full, tajik_yogas_16, expanded_yogas)

**Cross-module systemic issues** (all 5 modules affected unless noted):
- (S1) `lon_abs` is referenced for longitude-derived calculations (Kalachakra, Tajik aspects), but `manoj_chart.json` (the only test chart) does NOT contain `lon_abs` — only `lon`. The fallback chains `pd.get("lon_abs") or pd.get("lon") or (pd["rasi_idx"] * 30 + pd["deg"])` work, but the fact that the **first preferred field is missing** means production uses the third fallback, masking subtle bugs in the primary code path that nothing tests.
- (S2) `sys.path.insert(0, ".")` is brittle — only works when CWD is `runtime/`. The orchestrator may invoke from project root.
- (S3) No type hints on any public function across all 5 modules. Reference modules also lack them, but Tier 2 had a chance to lift the bar.
- (S4) `if __name__ == "__main__"` blocks all hard-code `"../charts/manoj_chart.json"` — can't switch test charts without code edit.

---

# Module 1: `dasha_systems_full.py`

## Strengths
- Clean unified API: `all_advanced_dashas(chart)` returns dict-of-timelines.
- `lookup_active(timeline, when_dt)` reusable across all 5 dashas.
- File-level docstring cites BPHS Ch. 50 + Jaimini Sutras Ch. 2.
- All 5 dashas return uniform record shape `{sign, lord, start, end, years, age_from, age_to, notes}`.

## Issues

### BLOCKER

**B1.1 — Kalachakra direction logic is wrong (BPHS Ch. 50 violation)** `dasha_systems_full.py:57-65`
The `_kalachakra_start_sign` function alternates Savya/Apasavya by **pada within nakshatra** (1,3 = Savya; 2,4 = Apasavya). BPHS Ch. 50 actually defines Savya/Apasavya by **nakshatra-group**, where each of 9 nakshatra groups uses a fixed direction depending on whether the Moon falls in the deha (body) or jeeva (life) half. The current encoding is a placeholder — comment line 50 admits "Simplified". This is not Kalachakra dasha; it's a fictitious approximation labeled as Kalachakra.

**B1.2 — Kalachakra start-sign formula is fictitious** `dasha_systems_full.py:64`
`seed_idx = (nak_idx * 4 + (pada - 1)) % 12` is an arithmetic invention with no classical basis. BPHS gives a 9-rashi sequence per (nakshatra, pada) combination derived from the deha/jeeva mapping — not a modulo-12 walk. The 28-pada-by-9-rashi BPHS table is not encoded anywhere in the file.

**B1.3 — Kalachakra year-counts add to 121, not 100** `dasha_systems_full.py:36-40`
`KALACHAKRA_YEARS` sums to `7+16+9+7+21+5+9+16+7+10+4+10 = 121`. Comment line 41 acknowledges this but the loop uses these inflated counts unchanged. Classical Kalachakra is 100 years exactly. Either the per-sign counts are wrong, or the loop must scale them to 100.

**B1.4 — Shoola Dasha period lengths reversed from Jaimini Sutra 2.3.1** `dasha_systems_full.py:130`
`SHOOLA_YEARS_BY_QUALITY = {"movable": 7, "fixed": 8, "dual": 9}`. Per Jaimini Sutra 2.3.1, the canonical mapping is **movable: 9, fixed: 8, dual: 7** (varies by interpretation but 7-movable is non-standard). Same bug applies to Drig (line 235) and Niryana Shoola (line 270). Verify against Sanjay Rath's *Crux of Vedic Astrology* — most modern Jaimini sources use 9/8/7 (movable/fixed/dual).

### MAJOR

**M1.1 — Pada calculation may produce 0 or 5** `dasha_systems_full.py:76-78`
```python
pada = int(((moon_lon - nak_idx * (360 / 27)) // (360 / 108))) + 1
if pada < 1: pada = 1
if pada > 4: pada = 4
```
The clamps are reactive band-aids rather than mathematically correct math. With `lon_abs` semantics, the integer division can produce 4 at boundary, leading to pada=5 before clamp. Boundary-test cases should be validated.

**M1.2 — Sthira period lengths conflict with Shoola** `dasha_systems_full.py:176`
`STHIRA_YEARS_BY_QUALITY = {"movable": 7, "dual": 8, "fixed": 9}` while Shoola uses `{"movable": 7, "fixed": 8, "dual": 9}`. Different period systems give different semantic meanings to fixed vs dual, but the file gives no source citation for this mapping. Sthira Dasha per Phaladeepika gives **7/8/9 by quality** — but the canonical mapping per K.N. Rao's *Predicting through Jaimini's Chara Dasha* is movable:9, fixed:8, dual:7 (matching Jaimini). At minimum, both Shoola and Sthira should match the source they cite.

**M1.3 — Atmakaraka calculation excludes Rahu but Jaimini disagrees** `dasha_systems_full.py:214-219`
```python
candidates = [p for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"] if p in pos]
best = max(candidates, key=lambda p: pos[p]["deg"])
```
Two issues:
- (a) Some Jaimini schools include Rahu (with reverse degree calculation: `30 - deg`); the file silently picks the Parashari-Jaimini view without documenting the choice.
- (b) `max(candidates, key=...)` finds highest degree but does NOT check whether multiple planets have equal degrees (rare, but classical text gives a tie-breaker via Pushkara navamsha).

**M1.4 — Drig Dasha period lengths use Shoola's table** `dasha_systems_full.py:235`
`yrs = SHOOLA_YEARS_BY_QUALITY[_sign_quality(sign)]` — Drig Dasha is a separate Jaimini system with its own period rules per BPHS Ch. 51 (and per Sanjay Rath's commentaries). Using Shoola's table is a placeholder; no source supports this conflation.

**M1.5 — Markesha planets calculation is incorrect** `dasha_systems_full.py:273-274`
```python
marak_lords = [RASI_LORDS[RASIS[(lagna_idx + 1) % 12]],     # 2nd-from-lagna lord
                RASI_LORDS[RASIS[(lagna_idx + 6) % 12]]]    # 7th-from-lagna lord
```
Classically, **maraka = lords of 2 and 7**, but more rigorous interpretation per BPHS includes:
- Planets occupying the 2H or 7H (often more powerful as marakas than lords)
- Lord of the 12th-from-Moon as additional maraka via Bhrigu Sutra
- Saturn or Mars in 2/7 trumps lord-based maraka.

The simplification is acceptable for first pass but should be flagged in `notes`.

### MINOR

**m1.1 — Shoola seed says "7th from lagna" but the comment at line 140 says "7th house from natal Lagna (per Jaimini)"** — actually some sources use 7th-from-AL (Arudha Lagna), not lagna. Document choice.

**m1.2 — `cur_yrs` reassignment in Kalachakra loop has dead-code path** `dasha_systems_full.py:117`
The inner reassignment `sign = RASIS[cur_idx % 12]` immediately after `cur_idx = (cur_idx + step) % 12` is fine, but the local-variable `sign` is unused (only `cur_yrs` matters). Confusing.

**m1.3 — `compute_drig` ignores `step` direction** `dasha_systems_full.py:222-249`
Drig Dasha is supposed to walk by **Jaimini rashi-aspects** from the seed sign — not a simple +1 sequence. The `for i in range(12): idx = (seed_idx + i) % 12` is just zodiacal-forward.

**m1.4 — No clamp on `years` to 120 horizon** — Vimshottari uses 120-year horizon (`granular_dasha.py:88-89`). These advanced dashas walk 12 signs. If movable=9/fixed=8/dual=7 sums to 4×9+4×8+4×7 = 96 years, they don't reach 120. Niryana Shoola for longevity readings should explicitly note the horizon.

### NIT

**n1.1 — Magic numbers**: `(360 / 27)`, `(360 / 108)` repeated; should be constants `NAK_ARC = 360/27`, `PADA_ARC = 360/108`.

**n1.2 — `KALACHAKRA_DIRECTION` list defined but never used** (line 54).

**n1.3 — Print formatting hardcodes column widths** without using `f-string` `{:>13s}` reusable formatter.

---

# Module 2: `muhurta_extended.py`

## Strengths
- Clean uniform return shape — `{event, date, verdict, score, reasons_supportive, reasons_against, panchanga, better_dates}`.
- Leverages existing `compute_panchanga`, `tara_bala`, `chandra_bala` — no duplicated panchanga computation.
- `_base_score(pan, chart)` factors out common scoring pattern across all 14 muhurtas.
- `find_better=True` + 30-day search auto-suggests alternatives — UX-friendly.
- All 14 entry-points have consistent signature `(chart, target_dt, _suppress_better=False)`.

## Issues

### BLOCKER

**B2.1 — Tithi-30 (Amavasya) handled inconsistently** `muhurta_extended.py:208`
```python
if pan["tithi_number"] in [4, 9, 14, 30]:
```
But `panchanga.py:48` shows `tithi_num` ranges 1-30 with `tithi_num == 30` being Amavasya. However, the `_base_score` function on line 84 uses `pan.get("is_amavasya")` — which doesn't exist in the panchanga return shape. So the Amavasya score-penalty (-18) at line 84 NEVER fires. Cross-checking 14 muhurtas: griha-pravesh, chudakarana, rajyabhisheka, dahana all check `[..., 30]` directly but the centralized `_base_score` doesn't. The result: griha-pravesh on Amavasya gets penalized -10 (correct), but namakarana on Amavasya gets penalized 0 (BUG — should be ≥-15).

### MAJOR

**M2.1 — Bhadra Karana check uses non-existent panchanga key** `muhurta_extended.py:88-89`
```python
if pan.get("is_bhadra"):
```
`compute_panchanga` returns `karana` as a string (e.g., "Vishti(Bhadra)"). It does NOT return `is_bhadra`. So the -15 penalty NEVER fires. Should be `if pan.get("karana") == "Vishti(Bhadra)"`.

**M2.2 — `_base_score` assumes `tara_bala` and `chandra_bala` return shape that may not exist** `muhurta_extended.py:104-117`
```python
tara = tara_bala(natal_nak, when_dt)
if tara:
    if tara["is_good"]:
```
Need to verify `tara_bala()` from `muhurta_engine.py` actually returns `{"is_good": bool, "type": str}` shape — not just an integer or `None`. Same for `chandra_bala` (`{"is_good"`, `"is_bad"`, `"verdict"}`). If shape is different, every muhurta silently fails-open with score=50 and no Tara/Chandra adjustment.

**M2.3 — `_quick_score` infinite-recursion risk** `muhurta_extended.py:150-171`
`_wrap` calls `_quick_score`, which calls `fn(chart, cand_dt, _suppress_better=True)`. Each candidate-date call is full-Panchanga-compute. For a "NOT IDEAL" verdict with 30-day search × 14 muhurtas → up to 420 panchanga computations per chart-day. No memoization — can be slow when orchestrator runs all-muhurtas-by-month report.

**M2.4 — Vidyarambha "education-start" misses Mercury hora rule** `muhurta_extended.py:305-316`
Classical vidyarambha texts (Muhurta Chintamani Ch. 5) give heavy weight to **Mercury hora** (24-minute slice when Mercury rules), and **Wednesday + Hasta or Pushya** is ideal. The current rule only checks vara + nakshatra, missing the hora dimension.

### MINOR

**m2.1 — `score = 50` baseline + cumulative additions can exceed 100 silently** before clamp on line 132. A muhurta scoring `+8 + 12 + 10 + 8 + 12 + 15 = +65` from base 50 = 115 — clamped to 100, but the relative rank between two excellent muhurtas is lost (both clamp to 100).

**m2.2 — `find_better` only searches forward 30 days** — should also search backward 7 days (sometimes a "yesterday" muhurta beats today).

**m2.3 — Garbhadhana excludes "Bharani, Krittika, Ardra, Ashlesha, Magha, Mula, Jyeshtha, Vishakha"** `muhurta_extended.py:220` but classical texts add **Pushya, Uttara Ashadha, Uttara Phalguni** as best-for-conception which IS in `GARB_GOOD`. However, **Tuesday + Saturday + Krishna Paksha** are also avoided per Sushruta Samhita Sharirasthana — not encoded.

**m2.4 — Rina (loan-taking) Krishna paksha logic** `muhurta_extended.py:400-403`
Penalty `-4` for Shukla is too soft; classical rule is "Krishna paksha required" — should be `score -= 12, neg.append("Shukla paksha — debt grows (avoid)")`.

**m2.5 — Dahana "Triphala" definition is non-standard** `muhurta_extended.py:421`
`TRIPHALA_BAD = ["Magha","Mula","Revati","Ashlesha","Jyeshtha"]` — classical "Tri-Phala" nakshatras are usually **Magha, Mula, Revati only** (the 3 connection-points of nakshatra cycles). Adding Ashlesha & Jyeshtha is an extension; should cite source.

### NIT

**n2.1 — `find_better` returns dates as string `"YYYY-MM-DD (Day)"` but `score` as int** — should be ISO 8601 + numeric for orchestrator JSON.

**n2.2 — Verdict thresholds magic numbers**: `>=75=AUSPICIOUS, >=55=ACCEPTABLE, >=35=NOT IDEAL` — extract to module constants.

**n2.3 — File-level docstring lists 14 muhurtas but `ALL_MUHURTAS` has 14** — match. (Good.)

---

# Module 3: `tajik_yogas_16.py`

## Strengths
- Clean separation: 16 yoga predicates + 5 Bala calculations.
- File-level docstring cites Tajika Neelakanthi, Varshaphal Raman, Tajik Adawal.
- Tajik orb table at line 47-53 is correct (12/12/9/7/6° per Tajika Neelakanthi 2.4-2.7).
- Hadda boundary table at line 488-503 is the standard Egyptian/Ptolemaic terms (verified — these match Vettius Valens *Anthology* Book III).

## Issues

### BLOCKER

**B3.1 — `_is_applying` direction logic is wrong** `tajik_yogas_16.py:97-110`
```python
def _is_applying(p1, p2, lon1, lon2):
    s1 = PLANET_SPEED.get(p1, 1.0)
    s2 = PLANET_SPEED.get(p2, 1.0)
    fast = p1 if s1 > s2 else p2
    slow = p2 if s1 > s2 else p1
    fast_lon = lon1 if fast == p1 else lon2
    slow_lon = lon2 if fast == p1 else lon1
    rel = (fast_lon - slow_lon) % 360
    return rel > 180  # fast is approaching from behind
```
Tajik definition: **applying = the angular difference between the two planets is decreasing toward the exact aspect angle** (i.e., the faster planet is moving toward the slower planet's longitude that-would-form-exact-aspect). The current implementation computes raw angular position relative to slow, not the rate-of-approach to the aspect target. Specifically:
- For an `aspect_type` to be `trine` (120°), applying means `|sep - 120°|` is **decreasing**, not that `fast_lon - slow_lon mod 360 > 180`.
- The `rel > 180` test is the test for "fast is currently zodiacally behind slow" which is **insufficient** — it doesn't account for which exact aspect is forming.

This single function is the foundation of Ittasala vs Iisarafa — a fictitious split between yogas 1 and 2. Should be redone: compute current sep, predict sep one day later (using `swe.calc_ut(jd+1)` or simulated +∆speeds), classify applying iff `|sep_tomorrow - target| < |sep_today - target|`.

**B3.2 — Missing retrograde handling** `tajik_yogas_16.py:64-68`
```python
PLANET_SPEED = {
    "Moon": 13.18, "Mercury": 1.38, "Venus": 1.20, "Sun": 0.99,
    "Mars": 0.52, "Jupiter": 0.083, "Saturn": 0.034,
    "Rahu": 0.053, "Ketu": 0.053,
}
```
Mean speeds are positive, but actual planets retrograde. A retrograde Mars moves backward at ~0.3°/day. Tajik tradition explicitly handles retrograde — a retrograde planet "applies in reverse" or refuses aspects ("Khallasar" or "Radd" yogas can fire on retrograde). The chart's `pos[planet]` should carry a `retrograde` flag; if it does, `_is_applying` should invert.

The natal `chart["positions"]["Mars"]` does NOT carry retrograde flag (verified in `manoj_chart.json`). So this code can never detect retrograde-conditioned yogas → Tajik tradition violation.

**B3.3 — Manaucha exalted-receives definition wrong** `tajik_yogas_16.py:173-193`
Classical Manaucha = **planet in own exaltation (uccha)** AND that planet is in the annual chart's **annual lagna or dignified placement** AND receives aspect from year-lord. The current code:
```python
for p1, exalt_sign in EXALTATION_SIGNS.items():
    if pos[p1]["rasi"] != exalt_sign: continue
```
fires for any exalted planet receiving any aspect — which is just "exalted-aspect" not Manaucha. Manaucha specifically requires that the **other** participant be the Varshesha (year-lord), not just any planet. Without `chart["varshesha"]` field, this can't be detected accurately.

### MAJOR

**M3.1 — Aspect detection iterates dict in arbitrary order** `tajik_yogas_16.py:85-94`
```python
for aspect, target in TAJIK_ASPECT_ANGLES.items():
    diff = abs(sep - target)
    if diff <= TAJIK_ORBS[aspect]:
        return aspect, TAJIK_ORBS[aspect], diff
```
For two planets at separation 75°, this matches **either** `square (90°, orb 7°)` IF dict-order hits square first OR `sextile (60°, orb 6°)` IF sextile first. Python 3.7+ preserves insertion order, so the actual order is: conj, sextile, square, trine, opp. So a 75° separation matches `sextile` first (75-60=15° > orb 6°, no match), then `square` (75-90=15° > 7°, no match) — no match. Correct in this case BUT for 117° separation, `trine (120°, 9°)` matches first AND `opposition (180°, 12°)` doesn't match — correct. Edge-case at 92° separation: square (90°+2°<7°) matches first; trine (120°-92°=28°>9°) doesn't — correct. **However**, conj at 12° matches conj first AND opp at 168° matches opp ... wait, sep is 0-180 so opp at 168° means sep=168, 180-168=12 ≤ 12 orb → matches opp. OK.

But **subtle bug**: for sep=12° (conj orb 12°), it returns `("conjunction", 12, 12)` — which is **at-the-orb-edge** but classically Tajik orbs are **half on each side** (so combined orb = 12° conj means each planet contributes 6° approach orb). This is Tajik tradition, not Ptolemaic — verify.

**M3.2 — Yamaya same-degree threshold magic number** `tajik_yogas_16.py:206`
```python
if abs(d1 - d2) <= 1.5:  # same degree
```
Why 1.5°? Tajik Yamaya tradition gives ~1° to 2° depending on text. Should be a documented constant `YAMAYA_ORB_DEG = 1.5`.

**M3.3 — Mosthasala threshold magic number** `tajik_yogas_16.py:231`
```python
if diff >= 1.5: continue
```
Same — extract `MOSTHASALA_ORB_DEG = 1.5`.

**M3.4 — Khallasar `between` interception logic broken at zodiac wrap** `tajik_yogas_16.py:281-283`
```python
a, b = sorted([l1, l2])
for p3, p3d in pos.items():
    ...
    if a < l3 < b:
        between.append(p3)
```
Fails when `l1=350, l2=10` (sep=20°, conjunction orb). `sorted` gives `(10, 350)`, and a planet at 0° is NOT between 10 and 350 by simple comparison. Should compute "between" via shorter arc.

**M3.5 — Indu-Yamaya doesn't check Moon-degree threshold** `tajik_yogas_16.py:355-356`
```python
if aspect and diff < 6.0:
```
The 6° cutoff is undocumented. Tajik Indu-Yamaya per Neelakanthi 4.12 is "Moon close to benefic by 1° or less" — much tighter. The 6° threshold is probably too lax.

**M3.6 — Drekkana lord formula** `tajik_yogas_16.py:553-554`
```python
drek_sign_idx = (rasi_idx + (dec - 1) * 4) % 12
```
First decanate = sign-lord (correct: 0×4=0 offset).
Second decanate per Parashari = lord of 5th sign (should be `+4` offset, gives index `rasi_idx+4` — but that's the **5th sign from itself**, e.g., Aries 2nd decan = Leo, lord Sun. Wait, Aries=0, +4=4=Leo, Leo lord = Sun. Correct.).
Third decanate = lord of 9th sign (offset +8), e.g., Aries 3rd decan = Sagittarius, lord Jupiter.

Actually the formula `(dec-1) * 4` gives 0, 4, 8 — correct. **However**, this is the **Parashari Drekkana**, not the **Tajik Drekkana**. Tajik tradition (per *Tajik Adawal*) uses **Egyptian decans** with face-rulers Mars/Sun/Venus/Mercury/Moon/Saturn/Jupiter rotating across signs, not the Parashari "+4 offset" rule. Citation needed; this is a Parashari approximation labeled as Tajik.

### MINOR

**m3.1 — `_yoga` helper accepts `**kw` but nothing validates extra keys** — risk of typos like `aspecet=` silently swallowed.

**m3.2 — `y_kambula` 4th-house-from logic uses house, not sign** `tajik_yogas_16.py:252`
4th-from-planet should follow **whole-sign** convention (just sign-step), not house numbering — but in `manoj_chart.json` the chart uses whole-sign houses (rasi_idx aligned with house), so happens to be equivalent. Should document.

**m3.3 — `y_madabihaza` doesn't check the slow planets are actually in mutual aspect with each other** — wait, it does via `_aspect_type(l1, l2)`. OK.

**m3.4 — `y_qutha_i_nur` requires `>= 2 Ittahads` but Tajik tradition requires `>= 3`** — verify with Tajika Neelakanthi 4.20.

### NIT

**n3.1 — Variables `_, _, _ = _aspect_type(...)` triple-underscore pattern** is unconventional Python; typical idiom is `aspect, _, _`.

**n3.2 — `ALL_TAJIK_YOGA_FNS` list is good but `detect_all_tajik_yogas` could collect by name**.

---

# Module 4: `expanded_yogas.py`

## Strengths
- Extensive coverage: 250+ yoga rules across 11 categories.
- Lambda-based predicate tables (DISEASE_YOGAS_DATA, SADHU_YOGAS_DATA, etc.) compact and easy to add new rules.
- Cites multiple classical sources at file-level (Bhavartha Ratnakara, Saravali, Phaladeepika, Jataka Parijata, BPHS).
- Proper try/except in detector loops to prevent one broken predicate from killing the whole detection pass.
- Clear separation: detectors → category aggregators → master list.

## Issues

### BLOCKER

**B4.1 — Duplicate yogas with `comprehensive_yogas.py` not deduplicated** `expanded_yogas.py` (multiple)
Cross-checking against `comprehensive_yogas.py`:

| In expanded_yogas.py | Already in comprehensive_yogas.py | Severity |
|---|---|---|
| `y_putra_jupiter_kendra_lagna` | (not exact dup but related) Mahapurusha — Jupiter Hamsa | ok |
| `y_putra_5_with_lagna_lord` (1L+5L conjunct) | `y_raja_kendra_trikona` (kendra+trikona lord conj) | **partial dup** — fires together |
| `y_daridra_chandra_kemadruma_strict` | `y_kemadruma` (lines 134-150 in comprehensive) | **DUPLICATE** — both fire on same chart, double-counted |
| `Pravrajya 4-in-1-sign` | Already in `comprehensive_yogas.py:y_nabhasa` at sign-cluster | possible overlap |
| `Vipareeta` rules in `DHANA_YOGAS_DATA` (`Vipareeta 6L 6` etc.) | `y_vipareeta_raja` in comprehensive | **DUPLICATE** — Harsha/Sarala/Vimala fire twice |
| `Manglik 1/4/7/8/12` | (not in comprehensive — new, OK) | ok |
| `Kalanidhi`, `Bheri`, `Khadga`, `Kusum`, `Sanyasi` | `comprehensive_yogas.py:y_nabhasa` lists 4 only — these 5 are new | mostly OK |

**Action**: Verify with explicit dedup test — run both modules against Manoj's chart, count yogas, ensure no name-clashes. Currently `Kemadruma` will appear twice in `engine_orchestrator.py`'s output (BPHS Ch. 13 cited in both).

**B4.2 — `chart_birth_male_day_lagna_check` is a stub returning False** `expanded_yogas.py:675-676`
```python
def chart_birth_male_day_lagna_check(chart_global, pos, li):
    return False  # placeholder for Maha Bhagya
```
Maha Bhagya Yoga predicate is referenced at line 668 in `DHANA_YOGAS_DATA` — predicate calls this stub, always returns False. So Maha Bhagya is dead code in the lambda table. Either remove the row or implement. Worse: the lambda passes `chart_global=None` which would crash if the function were complete (it expects the chart object).

### MAJOR

**M4.1 — Aspect detection in DISEASE_YOGAS_DATA is wrong for Saturn**
Line 354:
```python
("Saturn aspects Moon", lambda pos, li: ... pos["Moon"]["house"] in [(pos["Saturn"]["house"]+2)%12 or 12, (pos["Saturn"]["house"]+6)%12 or 12, (pos["Saturn"]["house"]+9)%12 or 12], ...)
```
Saturn's aspects in Vedic astrology: **3rd, 7th, 10th from itself** = `+2, +6, +9` houses-zero-based. The formula `(pos["Saturn"]["house"]+2)%12 or 12` for Saturn-in-1H gives `(1+2)%12 or 12 = 3 or 12 = 3` (correct). For Saturn-in-10H: `(10+2)%12 or 12 = 0 or 12 = 12` (correct).

But the formula has a subtle bug: the `or 12` short-circuits only when the modulo is 0. For Saturn-in-12H: `(12+2)%12 or 12 = 2 or 12 = 2` (correct). However, the formula should add `+1` to convert 0-indexed-mod to 1-indexed-house. The current `(h + 2) % 12 or 12` is not standard.

Compare to `vedic_core.planet_aspects_houses`:
```python
return [((h+2-1)%12)+1, ((h+6-1)%12)+1, ((h+9-1)%12)+1]
```
This is the correct formula. The lambda-table forms are different and may produce wrong results for boundary houses. Audit all `[..., 11], [..., 12]` boundary cases.

**M4.2 — Mars aspects** Line 696-697:
```python
("Mars aspects lagna", lambda pos, li: "Mars" in pos and 1 in [(pos["Mars"]["house"]+3)%12 or 12, (pos["Mars"]["house"]+6)%12 or 12, (pos["Mars"]["house"]+7)%12 or 12], "...")
```
Mars aspects: 4th, 7th, 8th = `+3, +6, +7`. Formula matches but same off-by-one risk as M4.1.

**M4.3 — Rahu aspects** Line 387:
```python
("Rahu aspects 1", lambda pos, li: "Rahu" in pos and 1 in [(pos["Rahu"]["house"]+4-1)%12+1, (pos["Rahu"]["house"]+6-1)%12+1, (pos["Rahu"]["house"]+8-1)%12+1], "...")
```
Rahu/Ketu aspects (Jaimini-style): 5, 7, 9 from self. **But traditional Parashari does NOT give Rahu special aspects** — Rahu aspects 7th-from-self only by default. Some schools (KP, modern) give 5/7/9 like Jupiter. File doesn't document which school, mixes traditions.

**M4.4 — Disease yogas use sign-conjunction (rasi_idx) ≠ same house** Multiple lines.
```python
("Sun-Saturn 1", lambda pos, li: ... pos["Sun"]["rasi_idx"]==pos["Saturn"]["rasi_idx"] and _h(pos,"Sun")==1, ...)
```
The check `rasi_idx ==` AND `house==1` is correct (whole-sign aligned) but if a future chart system uses Placidus or Bhava Chalit, sign-conj and house-conj diverge. Not a current bug but documentation owe.

**M4.5 — Several Career Yogas fire trivially without dignity check** Line 461:
```python
("Mercury 10", lambda pos, li: _h(pos,"Mercury")==10, "Communication, writing, commerce, media", "media"),
```
Mercury debilitated in Pisces 10H is still flagged as "Communication, writing, commerce" career — but it should be downgraded. No dignity gate. Compare line 458:
```python
("Sun 10 strong", lambda pos, li: _h(pos,"Sun")==10 and _dig(pos,"Sun") in ("Own","Exalted"), ...)
```
Sun has dignity gate, Mercury/Venus/Moon don't. Inconsistent.

**M4.6 — Manglik definition simplified** Line 528:
```python
("Manglik 1/4/7/8/12", lambda pos, li: _h(pos,"Mars") in [1,4,7,8,12], ...)
```
Classical Manglik has **5 grades** (high/medium/low + cancellation rules) — Mars in 12H is mild, Mars in 7H is severe. Single-line lambda misses cancellation (Mars in own/exalted, Mars + Moon in 7H, etc.). Phaladeepika Ch. 26 lists 11 cancellation rules.

**M4.7 — Saturn aspects in ARISHTA_YOGAS_DATA wrong formula again** Line 696, 730:
```python
("Sat aspects 7", lambda pos, li: "Saturn" in pos and 7 in [(pos["Saturn"]["house"]+2)%12 or 12, (pos["Saturn"]["house"]+6)%12 or 12, (pos["Saturn"]["house"]+9)%12 or 12], ...)
```
Same `(h+n) % 12 or 12` pattern as M4.1. For Saturn in 5H: `5+2=7%12=7`, `5+6=11%12=11`, `5+9=14%12=2`. The `or 12` only kicks in when `(h+n) % 12 == 0`, e.g., Saturn-in-10H aspects: `10+2=0 or 12 = 12`. Result: 12H. Correct.

But Saturn-in-3H aspects: `3+2=5`, `3+6=9`, `3+9=0 or 12 = 12`. Result: 5, 9, 12. Correct (Saturn aspects 5, 9, 12 from 3H). So formula DOES work by coincidence — `(h + N) % 12 or 12` is equivalent to `((h + N - 1) % 12) + 1` only when N is divisible by such that the boundary lines up. For Mars aspects (N=3, 6, 7) and Rahu (N=4, 6, 8) the formula is also lucky. **Audit recommendation**: replace all inline aspect formulas with `vedic_core.planet_aspects_houses(chart, planet)` calls. Eliminates inconsistency.

### MINOR

**m4.1 — `y_putra_putrakaraka_strong` doesn't check Jupiter-house** Line 246-252.
Jupiter exalted in Cancer can be in 6H (debilitated by house, not dignity) — should probably also gate on "not in dusthana" for full Putrakaraka.

**m4.2 — 50 disease yogas with placeholder commit-rates ("Speech defects, nerve concerns")** — narratives are very brief. Compare Saravali Ch. 35-44 which gives 2-3 sentence prognoses per pattern. Acceptable for compact, but PDF rendering will be repetitive.

**m4.3 — Sadhu yoga "Atmakaraka in 12" is `True` always-fires** Line 433:
```python
("Atmakaraka in 12", lambda pos, li: True, "Soul mission of moksha (when AK in 12) — checked separately"),
```
Predicate is hardcoded True — this fires for every chart unconditionally. Either implement (call `_atmakaraka_sign` and check house==12) or remove.

**m4.4 — Travel "All 7 in movable" requires `>=6 of 7`** Line 564:
```python
sum(1 for p in pos if pos[p]["rasi"] in MOVABLE_SIGNS and p not in ("Rahu","Ketu"))>=6
```
Comment says "All 7 in movable" but threshold is 6. Mismatch.

**m4.5 — Arishta "Atmakaraka in 8" hardcoded True** Line 704. Same as m4.3.

**m4.6 — `chart_birth_male_day_lagna_check` invocation** Line 668:
The lambda passes `chart_global=None`. If anyone implements this stub and uses `chart_global`, they'll crash. Better: pass `chart` object (from outer scope via closure) — but lambdas in DATA tables are defined outside any chart context, so chart is unavailable until predicate-time. Pattern needs fix.

### NIT

**n4.1 — Each yoga in DATA tables uses 3-tuple `(name, fn, interp)` or 4-tuple `(name, fn, interp, sub)`** — inconsistent. Mostly 3-tuple but career uses 4. Standardize.

**n4.2 — Citations vary per row**: `"BPHS Ch. 41"` vs `"Bhavartha Ratnakara"` vs `"Phaladeepika Ch. 6"`. Some rows have no citation. Adding citation column to DATA tuples would normalize.

**n4.3 — Module total count claim**: file-level docstring says "250+ named classical yogas" but `yoga_count_summary()` shows: daridra=16, putra_bandhya=16, disease=50, sadhu=22, career=32, marriage=26, travel=11, nabhasa=28, dhana=30, arishta=40 = **271**. Match the docstring number.

---

# Module 5: `nadi_full.py`

## Strengths
- 108 hand-written narrative cells (9 planets × 12 houses) — each cell is unique, dignified-tone-aware, classically grounded.
- Sentences carry **specific signifier-language** ("father's pride", "mother weeps in winter") — not generic templates.
- Two-planet conjunction rules (13) include actual Naadi-style "kavya" couplets ("The blacksmith strikes cold iron").
- Karaka logic correctly distinguishes strong (own/exalted/kendra/trikona) from weak (debil/dusthana).
- Clean public API: `nadi_cell_reading()`, `full_nadi_narrative()`, `detect_two_planet_rules()`, `karaka_readings()`, `complete_nadi_analysis()`.

## Issues

### MAJOR

**M5.1 — Cells are AI-generated paraphrases, not direct Nadi-text translations** (file-level concern)
The cell sentences are stylistically Naadi-like ("The mother weeps in winter") but are **not literal translations** from Bhrigu Nadi or Chandra Kala Nadi source manuscripts. A reader expecting literal palm-leaf Naadi reading will be misled. Mitigation: file-level docstring should add a clarifier like "Cells synthesize the spirit of Bhrigu/Chandra Kala Nadi tradition; not literal translations" OR cite specific source verses per cell where possible.

**M5.2 — Karaka logic conflates "Own" with "kendra" placement** `nadi_full.py:276`
```python
is_strong = dignity in ("Own", "Exalted", "Exalted/Own") or h in (1, 4, 5, 7, 9, 10, 11)
```
This says "Mars in 11H neutral" = strong (because 11H ∈ list). But Mars in 11H non-dignified is MERELY "well-placed by house" — classical Naadi distinguishes **house-strength** (sthana bala) from **dignity-strength** (uchcha-svakshetra). Should produce 4 categories:
- Both dignity AND good house → very strong
- Dignity only → moderately strong
- Good house only → mildly favorable
- Neither → weak

Current binary collapse loses nuance.

**M5.3 — `house_themes` import not in vedic_core for House 0/13** — chart house values 1-12 only. Defensive code missing for malformed chart with `house: 13`. Same applies to invalid `rasi`. Lines 184-192.

### MINOR

**m5.1 — `complete_nadi_analysis` returns dict but no schema documented** — orchestrator may expect specific keys. Document return shape.

**m5.2 — TWO_PLANET_RULES has 14 entries but file docstring says "13 specific 2-planet conjunction rules"** — actual count: Sun_Sat, Sun_Rahu, Sun_Ketu, Sun_Mars, Moon_Sat, Moon_Rahu, Moon_Ketu, Mars_Sat, Mars_Rahu, Venus_Sat, Venus_Rahu, Jup_Sat, Jup_Rahu, Sat_Rahu = **14**. Docstring off by one.

**m5.3 — Conjunction detection uses sign-only (`rasi_idx`)** — not degree-tightness. Two planets in same sign 28° apart are still flagged as conjunct. Classical Nadi typically requires same nakshatra (within ~13°), not same sign (30°). Should add `degree_distance(p1, p2) < 8°` gate.

### NIT

**n5.1 — `nadi_cell_reading` falls back to `f"{planet} in House {house} — placement noted, no specific Naadi sentence available."` for missing keys** — better default phrasing or raise KeyError.

**n5.2 — 108-cell English uses some inconsistent capitalization**: "ayurveda" lowercase but "Vedic" capitalized. Minor.

---

# Cross-Module Observations

## Consistency between modules

1. **Aspect formula inconsistency** — Disease/Arishta yogas in `expanded_yogas.py` use inline `(h+N)%12 or 12` formulas, while `vedic_core.planet_aspects_houses` uses `((h+N-1)%12)+1`. Fix: replace ALL inline aspect formulas across `expanded_yogas.py` with `planet_aspects_houses(chart, planet)` calls.

2. **Speed table inconsistency** — `tajik_yogas_16.py` defines `PLANET_SPEED` locally; `dasha_systems_full.py` uses no speed; `varshaphala.py` uses `swe.calc_ut` real speeds. Centralize: add `PLANET_MEAN_SPEED` to `vedic_core.py`.

3. **`lon_abs` field** — Referenced by `dasha_systems_full.py:71`, `tajik_yogas_16.py:76`, but **not present** in `manoj_chart.json`. Both files have a fallback chain, but the chart pipeline should canonicalize to `lon_abs` (zodiacal degrees 0-360). Either:
   - Add `lon_abs` to chart computation (recommended), OR
   - Document that fallback `pd["rasi_idx"]*30 + pd["deg"]` is the canonical computation.

4. **Atmakaraka logic** — Defined locally in `dasha_systems_full.py:_atmakaraka_sign` (excludes Rahu) and elsewhere via comments. Centralize into `vedic_core.py:atmakaraka(chart, include_rahu=False)`.

5. **Chart loading boilerplate** — Every `__main__` block hardcodes `"../charts/manoj_chart.json"`. Add a helper `load_test_chart(name="manoj")` to `vedic_core.py` to enable easy multi-chart testing.

6. **Citations** — Some modules cite chapter+verse (`"BPHS Ch. 13"`), others just text-name (`"Bhavartha Ratnakara"`). Adopt convention: `<TextName> [<Chapter>.<Verse>]`.

## Integration readiness verdict

| Module | API clean? | Returns dict? | Takes chart consistent? | Status |
|--------|---|---|---|---|
| dasha_systems_full | Yes | Yes (timeline list-of-dicts) | Yes (chart dict) | INTEGRATION-READY but logic-flawed |
| muhurta_extended | Yes | Yes (verdict dict) | Yes (chart, target_dt) | INTEGRATION-READY but Bhadra/Amavasya bugs |
| tajik_yogas_16 | Yes | Yes (yoga list-of-dicts) | Yes (chart) | NEEDS REVISION before integration (applying logic broken) |
| expanded_yogas | Yes | Yes (yoga list) | Yes (chart) | INTEGRATION-READY with dedup pass + aspect-formula fix |
| nadi_full | Yes | Yes (analysis dict) | Yes (chart) | INTEGRATION-READY |

## Testability

- All 5 modules have `__main__` smoke tests (good).
- All test against Manoj's chart only — no edge case coverage (empty chart, retrograde, no Moon, missing AK, etc.).
- No `pytest`-style assertions — outputs are visual.
- Recommend adding `tests/test_tier2.py` with assertion-based tests for each module's main API.

## Citation quality

- File-level docstrings cite sources (good).
- Per-rule citations vary from full ("BPHS Ch. 75") to vague ("Saravali") to none (multiple rules in `expanded_yogas.py`).
- No verse-level citations anywhere.

---

# Priority-Ordered Fix List (Top 20)

| Priority | Severity | Module | Issue | Effort |
|---|---|---|---|---|
| 1 | BLOCKER | tajik_yogas_16 | B3.1: `_is_applying` direction logic wrong — re-implement | High |
| 2 | BLOCKER | dasha_systems_full | B1.1: Kalachakra direction logic — encode BPHS Ch. 50 deha/jeeva mapping | High |
| 3 | BLOCKER | dasha_systems_full | B1.2: Kalachakra start-sign formula fictitious — encode 28-pada-by-9-rashi BPHS table | High |
| 4 | BLOCKER | dasha_systems_full | B1.3: Kalachakra year-counts sum to 121 not 100 — fix counts to standard values | Med |
| 5 | BLOCKER | dasha_systems_full | B1.4: Shoola period lengths reversed (canonically 9/8/7) | Low |
| 6 | BLOCKER | tajik_yogas_16 | B3.2: Missing retrograde flag in chart positions; Tajik tradition needs it | Med |
| 7 | BLOCKER | tajik_yogas_16 | B3.3: Manaucha definition wrong — needs Varshesha cross-ref | Med |
| 8 | BLOCKER | muhurta_extended | B2.1: Amavasya `is_amavasya` key never fires (panchanga returns name string) | Low |
| 9 | BLOCKER | expanded_yogas | B4.1: Multiple duplicate yogas with comprehensive_yogas.py — dedupe | Med |
| 10 | BLOCKER | expanded_yogas | B4.2: `chart_birth_male_day_lagna_check` is dead-code stub | Low |
| 11 | MAJOR | muhurta_extended | M2.1: Bhadra Karana `is_bhadra` key never exists in panchanga | Low |
| 12 | MAJOR | muhurta_extended | M2.2: Tara/Chandra return shape may not match `_base_score` assumptions | Low |
| 13 | MAJOR | dasha_systems_full | M1.5: Markesha planets list incomplete (planets-in-2H/7H stronger than lords) | Med |
| 14 | MAJOR | tajik_yogas_16 | M3.4: Khallasar `between` interception breaks at zodiac wrap | Low |
| 15 | MAJOR | expanded_yogas | M4.1-M4.7: Aspect formula `(h+N)%12 or 12` should use `vedic_core.planet_aspects_houses` | Med |
| 16 | MAJOR | dasha_systems_full | M1.4: Drig Dasha uses Shoola's table — needs own source-cited table | Med |
| 17 | MAJOR | nadi_full | M5.1: AI-generated cells need clarifier in docstring or cite source verses | Low |
| 18 | MAJOR | nadi_full | M5.2: Karaka logic conflates own/kendra — split to 4 strength tiers | Low |
| 19 | MAJOR | tajik_yogas_16 | M3.1: Aspect orb-cone iteration — replace with strict-best-match | Low |
| 20 | MAJOR | expanded_yogas | M4.5: Inconsistent dignity-gating in Career Yogas (Sun has, Mercury/Venus don't) | Med |

---

# Summary

**Top 3 BLOCKERs**:
1. Kalachakra dasha entirely fictitious (3 BLOCKERs combined: B1.1, B1.2, B1.3) — cannot be deployed as "BPHS Kalachakra"
2. Tajik `_is_applying` direction logic wrong — invalidates all 16 Tajik yoga splits between applying/separating
3. `expanded_yogas.py` has dead-code `chart_birth_male_day_lagna_check` and duplicate Kemadruma/Vipareeta/Pravrajya with `comprehensive_yogas.py`

**Top 5 MAJORs**:
1. Aspect formula inconsistency across `expanded_yogas.py` — replace with `planet_aspects_houses()`
2. `muhurta_extended.py` Bhadra and Amavasya never fire (panchanga key mismatch)
3. Missing retrograde flag in chart pipeline blocks Tajik traditional reading
4. Markesha logic incomplete in Niryana Shoola
5. Karaka strength binary in `nadi_full.py` — needs 4 tiers

**Classical-accuracy verdict per module**:
- `dasha_systems_full.py`: **HIGH RISK** — Kalachakra and Shoola period tables wrong; Drig uses Shoola's table without source.
- `muhurta_extended.py`: **MEDIUM RISK** — Two integration bugs where centralized score-effects never fire; 14 muhurta classifications themselves are reasonable.
- `tajik_yogas_16.py`: **HIGH RISK** — Foundational `_is_applying` is wrong; Manaucha definition wrong; retrograde unhandled.
- `expanded_yogas.py`: **MEDIUM RISK** — Many predicates correct, but 5+ duplicates with comprehensive_yogas + 2 dead-code stubs + aspect formula inconsistency.
- `nadi_full.py`: **LOW RISK** — Cells are AI-generated paraphrases (acceptable if disclosed); 108 cells well-crafted; karaka logic needs nuance pass; conjunction detection ignores degree-tightness.

**Recommendation**: Block deployment of `dasha_systems_full.py` (Kalachakra) and `tajik_yogas_16.py` (Itthasala family) until BLOCKERS B1.1-B1.3, B3.1, B3.3 are addressed. The other 3 modules can ship with the MINOR fixes after the alignment agent applies the patches in `TIER2_REVIEW_FIXES.md`.
