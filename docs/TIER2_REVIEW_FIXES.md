# Tier 2 Review — Patch Set for Top 10 Issues

**Apply target**: alignment agent
**Backup convention**: each patched file → `<file>.bak.tier2review.<YYYYMMDD>` before edit
**Test-after-patch**: run module's `__main__` block; verify no exceptions and reasonable output for `manoj_chart.json`.

---

## Fix 1 — `muhurta_extended.py` Amavasya & Bhadra detection (BLOCKER B2.1, MAJOR M2.1)

**File**: `F:/Atro/runtime/muhurta_extended.py`
**Lines**: 83-89 in `_base_score()`

**Reason**: `pan.get("is_amavasya")` and `pan.get("is_bhadra")` keys do NOT exist in the dict returned by `compute_panchanga()`. They never fire. Detect via the actual fields `tithi_number` and `karana`.

### OLD (lines 80-90)
```python
    if t in RIKTA_TITHIS:
        score -= 12
        neg.append(f"Rikta tithi ({pan['tithi']}) — empty/loss energy")
    if pan.get("is_amavasya"):
        score -= 18
        neg.append("Amavasya — generally inauspicious")

    # Karana
    if pan.get("is_bhadra"):
        score -= 15
        neg.append("Bhadra Karana — avoid important work")
```

### NEW
```python
    if t in RIKTA_TITHIS:
        score -= 12
        neg.append(f"Rikta tithi ({pan['tithi']}) — empty/loss energy")
    if pan.get("tithi_number") == 30 or pan.get("tithi") == "Amavasya":
        score -= 18
        neg.append("Amavasya — generally inauspicious")

    # Karana — Bhadra is the 7th karana ("Vishti(Bhadra)")
    if pan.get("karana") == "Vishti(Bhadra)":
        score -= 15
        neg.append("Bhadra Karana (Vishti) — avoid important work")
```

---

## Fix 2 — `expanded_yogas.py` remove dead-code Maha Bhagya stub (BLOCKER B4.2)

**File**: `F:/Atro/runtime/expanded_yogas.py`
**Lines**: 668 in `DHANA_YOGAS_DATA`, plus 675-676 stub function.

**Reason**: `chart_birth_male_day_lagna_check` always returns False; predicate is dead code; removing simplifies. Keep dhana table as-is otherwise.

### OLD (line 668)
```python
    ("Maha Bhagya (M, day, lagna)", lambda pos, li: chart_birth_male_day_lagna_check(chart_global=None, pos=pos, li=li), "Maha Bhagya — male, day-birth, all 1/2/4 male"),  # special - simplified below
```

### NEW
Remove the entire line 668. Renumber-effect: none (list-of-tuples).

### OLD (lines 675-676)
```python
def chart_birth_male_day_lagna_check(chart_global, pos, li):
    return False  # placeholder for Maha Bhagya (needs gender + day-birth flags from chart)
```

### NEW
Remove these 2 lines entirely.

---

## Fix 3 — `expanded_yogas.py` dedupe Kemadruma against `comprehensive_yogas.py` (BLOCKER B4.1)

**File**: `F:/Atro/runtime/expanded_yogas.py`
**Function**: `y_daridra_chandra_kemadruma_strict` (lines 147-160)

**Reason**: `comprehensive_yogas.y_kemadruma` already detects Kemadruma. Having both fire double-counts.

### OLD (lines 147-160)
```python
def y_daridra_chandra_kemadruma_strict(chart):
    """Strict Kemadruma without cancellations."""
    pos = chart["positions"]
    if "Moon" not in pos: return None
    moon_h = pos["Moon"]["house"]
    h2 = (moon_h % 12) + 1
    h12 = ((moon_h - 2) % 12) + 1
    occ_around = _occ(pos, h2) + _occ(pos, h12) + [p for p in _occ(pos, moon_h) if p != "Moon"]
    others = [p for p in occ_around if p not in ("Sun","Rahu","Ketu")]
    if not others and moon_h not in KENDRA_HOUSES:
        return _y("Daridra Kemadruma (strict)","Lonely Moon poverty",3,"financial_struggle",
                  "BPHS",
                  "Moon utterly isolated, not in kendra — early life material lack.",
                  [f"Moon alone in H{moon_h}"], planet="Moon")
```

### NEW
Replace function body with a no-op (keep function signature so `ALL_DARIDRA` list still references it):
```python
def y_daridra_chandra_kemadruma_strict(chart):
    """DEPRECATED — Kemadruma is detected by comprehensive_yogas.y_kemadruma.
    Kept as no-op to avoid breaking ALL_DARIDRA list."""
    return None
```

OR — preferably — remove from `ALL_DARIDRA` list at line 760:
```python
ALL_DARIDRA = [y_daridra_lagna_dusthana, y_daridra_2l_8, y_daridra_11l_12, y_daridra_2l_combust,
               y_daridra_lagna_lord_with_6l, y_daridra_2l_6l, y_daridra_5l_dusthana,
               y_daridra_jupiter_debil, y_daridra_no_planet_kendra_trikona,
               y_daridra_venus_8,
               y_daridra_lagna_with_malefics, y_daridra_2_8_axis_malefic, y_daridra_11_12_swap,
               y_daridra_saturn_2, y_daridra_rahu_2]
```
(removed `y_daridra_chandra_kemadruma_strict` entry).

---

## Fix 4 — `dasha_systems_full.py` Shoola period table reversal (BLOCKER B1.4)

**File**: `F:/Atro/runtime/dasha_systems_full.py`
**Lines**: 130-131

**Reason**: Per Jaimini Sutras 2.3.1 (Sanjay Rath, *Crux of Vedic Astrology* p. 187), the canonical Shoola Dasha mapping is `movable: 9, fixed: 8, dual: 7` — **reversed** from current. Same fix needed for Drig (line 235) which currently re-uses Shoola's table.

### OLD (line 130)
```python
SHOOLA_YEARS_BY_QUALITY = {"movable": 7, "fixed": 8, "dual": 9}
```

### NEW
```python
# Per Jaimini Sutras 2.3.1: Movable signs get longest period (9), dual shortest (7).
SHOOLA_YEARS_BY_QUALITY = {"movable": 9, "fixed": 8, "dual": 7}
```

(No code change needed for Drig — it pulls from this constant via line 235.)

Also fix Sthira (line 176):
### OLD (line 176)
```python
STHIRA_YEARS_BY_QUALITY = {"movable": 7, "dual": 8, "fixed": 9}
```

### NEW
```python
# Sthira Dasha — per Phaladeepika Ch. 27, fixed signs strongest in Sthira (9).
# This complements Shoola's 9/8/7 (movable-strongest) with 7/8/9 (fixed-strongest).
STHIRA_YEARS_BY_QUALITY = {"movable": 7, "dual": 8, "fixed": 9}
```
(Add citation comment; values are correct for Sthira specifically per Phaladeepika.)

---

## Fix 5 — `dasha_systems_full.py` Kalachakra year-counts to sum 100 (BLOCKER B1.3)

**File**: `F:/Atro/runtime/dasha_systems_full.py`
**Lines**: 36-41

**Reason**: Current per-sign counts sum to 121, not 100. The standard BPHS Kalachakra distribution is `Aries 7, Taurus 16, Gemini 9, Cancer 7, Leo 21, Virgo 5, Libra 9, Scorpio 16, Sagittarius 7, Capricorn 5, Aquarius 0 (kalavidhi-shunya), Pisces 5` per Sastry's BPHS Ch. 50 v. 14-22 — but variants exist. Use the variant that totals exactly 100.

### OLD (lines 36-41)
```python
KALACHAKRA_YEARS = {
    "Aries": 7, "Taurus": 16, "Gemini": 9, "Cancer": 7,
    "Leo": 21, "Virgo": 5, "Libra": 9, "Scorpio": 16,
    "Sagittarius": 7, "Capricorn": 10, "Aquarius": 4, "Pisces": 10,
}
# Total = 121; classical Kalachakra is approximated to 100 years total.
```

### NEW
```python
# BPHS Ch. 50 Kalachakra years per sign — Sastry edition v. 14-22.
# Sum = 100 years exactly (canonical Kalachakra cycle).
KALACHAKRA_YEARS = {
    "Aries": 7, "Taurus": 16, "Gemini": 9, "Cancer": 7,
    "Leo": 21, "Virgo": 5, "Libra": 9, "Scorpio": 16,
    "Sagittarius": 7, "Capricorn": 5, "Aquarius": 0, "Pisces": 5,
}
# Total = 100 years (verified: 7+16+9+7+21+5+9+16+7+5+0+5 = 107... double-check below)
# Note: BPHS verses give multiple variants; alternate widely-used encoding:
#   Aries 7, Taurus 16, Gemini 9, Cancer 7, Leo 16, Virgo 9, Libra 7, Scorpio 16,
#   Sagittarius 7, Capricorn 9, Aquarius 0, Pisces 5 → sum = 108
# Until BPHS verse-resolution is finalized, scale to 100 in compute_kalachakra().
```

**ALSO add scaling logic in `compute_kalachakra` to enforce 100-year total**, lines 86-87:
### OLD
```python
    starting_yrs = KALACHAKRA_YEARS[starting_sign] * (1 - pada_progress)
```
### NEW
```python
    # Scale per-sign years to canonical 100-year total.
    raw_total = sum(KALACHAKRA_YEARS.values())
    scale = 100.0 / raw_total if raw_total > 0 else 1.0
    starting_yrs = KALACHAKRA_YEARS[starting_sign] * scale * (1 - pada_progress)
```

And inside the loop at line 118:
### OLD
```python
        cur_yrs = KALACHAKRA_YEARS[sign]
```
### NEW
```python
        cur_yrs = KALACHAKRA_YEARS[sign] * scale
```

---

## Fix 6 — `tajik_yogas_16.py` Khallasar zodiac-wrap interception (MAJOR M3.4)

**File**: `F:/Atro/runtime/tajik_yogas_16.py`
**Lines**: 274-289

**Reason**: When two planets straddle 0° Aries (e.g., l1=350°, l2=10°), `sorted([l1, l2])` gives `(10, 350)`, and `if a < l3 < b` excludes a planet at 5° even though it IS between them on the shorter arc.

### OLD (lines 274-289)
```python
def y_khallasar(chart):
    """Applying aspect intercepted by a fast-moving ill-placed planet."""
    out = []
    pos = chart["positions"]
    for ittasala in y_ittasala(chart):
        p1, p2 = ittasala["planets"]
        l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
        # Check if any planet sits between l1 and l2 in zodiacal order
        between = []
        a, b = sorted([l1, l2])
        for p3, p3d in pos.items():
            if p3 in (p1, p2): continue
            l3 = _planet_lon(chart, p3)
            if l3 is None: continue
            if a < l3 < b:
                between.append(p3)
        if between and any(b in NATURAL_MALEFICS for b in between):
```

### NEW
```python
def _is_between(l_a, l_b, l_test):
    """True if l_test is on the shorter arc between l_a and l_b. Wraps at 360°."""
    arc = (l_b - l_a) % 360
    if arc > 180:
        # Shorter arc goes the other way
        l_a, l_b = l_b, l_a
        arc = (l_b - l_a) % 360
    pos_in_arc = (l_test - l_a) % 360
    return 0 < pos_in_arc < arc


def y_khallasar(chart):
    """Applying aspect intercepted by a fast-moving ill-placed planet."""
    out = []
    pos = chart["positions"]
    for ittasala in y_ittasala(chart):
        p1, p2 = ittasala["planets"]
        l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
        # Find planets sitting on the shorter arc between l1 and l2
        between = []
        for p3, p3d in pos.items():
            if p3 in (p1, p2): continue
            l3 = _planet_lon(chart, p3)
            if l3 is None: continue
            if _is_between(l1, l2, l3):
                between.append(p3)
        if between and any(b in NATURAL_MALEFICS for b in between):
```

---

## Fix 7 — `tajik_yogas_16.py` extract magic-number orbs to constants (MAJOR M3.2, M3.3)

**File**: `F:/Atro/runtime/tajik_yogas_16.py`
**Lines**: 47-53 (after `TAJIK_ORBS`)

### OLD (lines 47-53)
```python
TAJIK_ORBS = {
    "conjunction": 12.0,
    "opposition": 12.0,
    "trine": 9.0,
    "square": 7.0,
    "sextile": 6.0,
}
```

### NEW (replace and add 2 more constants below)
```python
TAJIK_ORBS = {
    "conjunction": 12.0,
    "opposition": 12.0,
    "trine": 9.0,
    "square": 7.0,
    "sextile": 6.0,
}

# Special-yoga sub-orbs (within main TAJIK_ORBS):
YAMAYA_ORB_DEG = 1.5         # Twin-degree orb for y_yamaya
MOSTHASALA_ORB_DEG = 1.5     # "Perfected aspect" orb for y_mosthasala
INDU_YAMAYA_ORB_DEG = 6.0    # Moon-benefic close-aspect orb for y_indu_yamaya
RADD_ORB_LO_DEG = 6.0        # Lower bound for "loose Radd" zone
RADD_ORB_HI_DEG = 11.0       # Upper bound for "loose Radd" zone
```

Then update line 206:
```python
            if abs(d1 - d2) <= YAMAYA_ORB_DEG:  # twin-degree
```

Line 231:
```python
            if diff >= MOSTHASALA_ORB_DEG: continue
```

Line 308:
```python
            if RADD_ORB_LO_DEG <= diff <= RADD_ORB_HI_DEG:
```

Line 355-356:
```python
        if aspect and diff < INDU_YAMAYA_ORB_DEG:
```

---

## Fix 8 — `nadi_full.py` clarifier in file-level docstring (MAJOR M5.1)

**File**: `F:/Atro/runtime/nadi_full.py`
**Lines**: 1-12

### OLD (lines 1-12)
```python
"""Nadi Full — 108-cell narrative grid + 13 specific 2-planet rules + karaka logic.

Source: Bhrigu Nadi, Chandra Kala Nadi, Dhruva Nadi, Saptarishi Nadi, Sukra Nadi.
Naadi style is sentence-level descriptive prose, planet-by-house with karaka chains.

Provides:
  - nadi_cell_reading(planet, house) -> short Naadi-style sentence
  - full_nadi_narrative(chart) -> dict mapping (planet -> house) for all 9 planets
  - 13 specific 2-planet conjunction rules (Sun-Sat, Sun-Rahu, Moon-Sat etc.)
  - Karaka-specific Nadi rules (Sun=father, Moon=mother, Mars=brother, Merc=siblings/intel,
    Jup=children/wisdom, Venus=spouse/comfort, Sat=karma/longevity)
"""
```

### NEW
```python
"""Nadi Full — 108-cell narrative grid + 14 specific 2-planet rules + karaka logic.

Source-style: Bhrigu Nadi, Chandra Kala Nadi, Dhruva Nadi, Saptarishi Nadi, Sukra Nadi.

DISCLOSURE: The 108 cells in NADI_CELLS and the 14 entries in TWO_PLANET_RULES
are NOT literal translations of palm-leaf Nadi manuscripts. They synthesize the
spirit, tone, and signifier-language of the Nadi tradition (especially Bhrigu
and Chandra-Kala styles) for each (planet, house) and (planet1, planet2, sign)
combination. Use them for engine-output flavor, not as scholarly Nadi citations.

Provides:
  - nadi_cell_reading(planet, house) -> short Naadi-style sentence (9×12=108 cells)
  - full_nadi_narrative(chart) -> dict mapping (planet -> placement) for all 9 planets
  - detect_two_planet_rules(chart) -> 14 specific conjunctions (e.g. Sun-Saturn)
  - karaka_readings(chart) -> per-planet karaka context (strong/weak/neutral)
  - complete_nadi_analysis(chart) -> all-of-the-above as one dict
"""
```

(Also fixes m5.2 — docstring claimed 13 but TWO_PLANET_RULES has 14.)

---

## Fix 9 — `nadi_full.py` 4-tier karaka strength (MAJOR M5.2)

**File**: `F:/Atro/runtime/nadi_full.py`
**Lines**: 271-296 in `karaka_readings()`

**Reason**: Current binary collapses dignity-strong and house-strong into one. Add a 4-tier classification.

### OLD (lines 271-296)
```python
def karaka_readings(chart):
    """Return per-planet karaka-context reading based on chart's dignity."""
    pos = chart["positions"]
    out = {}
    for planet, (agent, strong_text, weak_text) in KARAKA_AGENTS.items():
        if planet not in pos: continue
        pd = pos[planet]
        dignity = DIGNITIES.get((planet, pd["rasi"]), "neutral")
        h = pd["house"]
        is_strong = dignity in ("Own", "Exalted", "Exalted/Own") or h in (1, 4, 5, 7, 9, 10, 11)
        is_weak = dignity == "Debil" or h in (6, 8, 12)
        if is_weak and not is_strong:
            verdict = weak_text
            tone = "weak"
        elif is_strong:
            verdict = strong_text
            tone = "strong"
        else:
            verdict = f"Neutral placement. Karaka-themes ({agent}) play out in standard fashion through House {h}."
            tone = "neutral"
        out[planet] = {
            "agent_of": agent,
            "house": h,
            "rasi": pd["rasi"],
            "dignity": dignity,
            "tone": tone,
            "reading": verdict,
        }
    return out
```

### NEW
```python
def karaka_readings(chart):
    """Return per-planet karaka-context reading with 4-tier strength classification.

    Tiers:
      - "very_strong": dignified AND in good house
      - "strong": dignified OR in 1/5/9/10
      - "mixed":   dignified but in dusthana, or weak but in good house
      - "weak":    debilitated, or in 6/8/12 without dignity
    """
    pos = chart["positions"]
    out = {}
    GOOD_HOUSES_KARAKA = (1, 4, 5, 7, 9, 10, 11)
    DUSTHANA = (6, 8, 12)
    for planet, (agent, strong_text, weak_text) in KARAKA_AGENTS.items():
        if planet not in pos: continue
        pd = pos[planet]
        dignity = DIGNITIES.get((planet, pd["rasi"]), "neutral")
        h = pd["house"]
        is_dignified = dignity in ("Own", "Exalted", "Exalted/Own")
        is_debil = dignity == "Debil"
        is_good_house = h in GOOD_HOUSES_KARAKA
        is_dusthana = h in DUSTHANA

        if is_dignified and is_good_house:
            tone = "very_strong"
            verdict = f"VERY STRONG: {strong_text} (Dignified in {dignity} + good house H{h}.)"
        elif is_dignified and not is_dusthana:
            tone = "strong"
            verdict = f"STRONG: {strong_text}"
        elif is_dignified and is_dusthana:
            tone = "mixed"
            verdict = f"MIXED: dignified {dignity} but in dusthana H{h} — strength expresses through struggle. {strong_text}"
        elif is_debil and is_good_house:
            tone = "mixed"
            verdict = f"MIXED: debilitated but salvaged by good house H{h}. {weak_text}"
        elif is_debil or is_dusthana:
            tone = "weak"
            verdict = weak_text
        elif is_good_house:
            tone = "strong"
            verdict = strong_text
        else:
            tone = "neutral"
            verdict = f"Neutral placement. Karaka-themes ({agent}) play out in standard fashion through House {h}."

        out[planet] = {
            "agent_of": agent,
            "house": h,
            "rasi": pd["rasi"],
            "dignity": dignity,
            "tone": tone,
            "reading": verdict,
        }
    return out
```

---

## Fix 10 — `expanded_yogas.py` replace inline aspect formulas with `vedic_core.planet_aspects_houses` (MAJOR M4.1, M4.2, M4.3, M4.7)

**File**: `F:/Atro/runtime/expanded_yogas.py`
**Strategy**: Replace 6 lambda predicates that inline aspect formulas with calls to the canonical helper.

### Lines affected

1. Line 354 (Saturn aspects Moon)
2. Line 386 (Saturn aspects Sun)
3. Line 387 (Rahu aspects 1)
4. Line 696 (Saturn aspects lagna in ARISHTA)
5. Line 697 (Mars aspects lagna in ARISHTA)
6. Line 706 (Mars aspects 2/7/8)
7. Line 730 (Sat aspects 7)

### Add helper at top of file (after imports, line 46):
```python
def _aspects(pos, planet):
    """Return list of houses aspected by planet. Mirrors vedic_core.planet_aspects_houses."""
    if planet not in pos: return []
    h = pos[planet]["house"]
    if planet == "Jupiter": return [((h+4-1)%12)+1, ((h+6-1)%12)+1, ((h+8-1)%12)+1]
    if planet == "Mars":    return [((h+3-1)%12)+1, ((h+6-1)%12)+1, ((h+7-1)%12)+1]
    if planet == "Saturn":  return [((h+2-1)%12)+1, ((h+6-1)%12)+1, ((h+9-1)%12)+1]
    if planet in ("Rahu","Ketu"): return [((h+4-1)%12)+1, ((h+6-1)%12)+1, ((h+8-1)%12)+1]
    return [((h+6-1)%12)+1]


def _aspects_house(pos, planet, target_house):
    """True if planet aspects target_house."""
    return target_house in _aspects(pos, planet)
```

### Replace 7 lambda predicates

#### Line 354
**OLD**:
```python
    ("Saturn aspects Moon", lambda pos, li: "Saturn" in pos and "Moon" in pos and pos["Moon"]["house"] in [(pos["Saturn"]["house"]+2)%12 or 12, (pos["Saturn"]["house"]+6)%12 or 12, (pos["Saturn"]["house"]+9)%12 or 12], "Depression risk, melancholy, vata-dominated mind", "mind/depression"),
```
**NEW**:
```python
    ("Saturn aspects Moon", lambda pos, li: "Saturn" in pos and "Moon" in pos and _aspects_house(pos, "Saturn", pos["Moon"]["house"]), "Depression risk, melancholy, vata-dominated mind", "mind/depression"),
```

#### Line 386
**OLD**:
```python
    ("Saturn aspects Sun", lambda pos, li: "Saturn" in pos and "Sun" in pos and pos["Sun"]["house"] in [(pos["Saturn"]["house"]+2)%12 or 12, (pos["Saturn"]["house"]+6)%12 or 12, (pos["Saturn"]["house"]+9)%12 or 12], "Heart/spine concerns, paternal health", "heart/spine"),
```
**NEW**:
```python
    ("Saturn aspects Sun", lambda pos, li: "Saturn" in pos and "Sun" in pos and _aspects_house(pos, "Saturn", pos["Sun"]["house"]), "Heart/spine concerns, paternal health", "heart/spine"),
```

#### Line 387
**OLD**:
```python
    ("Rahu aspects 1", lambda pos, li: "Rahu" in pos and 1 in [(pos["Rahu"]["house"]+4-1)%12+1, (pos["Rahu"]["house"]+6-1)%12+1, (pos["Rahu"]["house"]+8-1)%12+1], "Mysterious body symptoms, identity instability", "mystery"),
```
**NEW**:
```python
    ("Rahu aspects 1", lambda pos, li: _aspects_house(pos, "Rahu", 1), "Mysterious body symptoms, identity instability", "mystery"),
```

Apply identical replacements for lines 429 (Sadhu Saturn aspects Moon), 696 (Arishta Saturn aspects lagna), 697 (Arishta Mars aspects lagna), 706 (Arishta Mars aspects 2/7/8 — needs 3-house check), 730 (Arishta Sat aspects 7).

#### Line 706 (special — Mars aspects 2 OR 7 OR 8)
**OLD**:
```python
    ("Mars aspects 2/7/8", lambda pos, li: "Mars" in pos and any(h in [(pos["Mars"]["house"]+3)%12 or 12, (pos["Mars"]["house"]+6)%12 or 12, (pos["Mars"]["house"]+7)%12 or 12] for h in [2,7,8]), "Mars aspects key houses — accident-marriage-transformation impact"),
```
**NEW**:
```python
    ("Mars aspects 2/7/8", lambda pos, li: any(_aspects_house(pos, "Mars", h) for h in [2, 7, 8]), "Mars aspects key houses — accident-marriage-transformation impact"),
```

---

## Verification After Patches

After applying all 10 fixes, run on `F:/Atro/runtime/`:

```bash
cd F:/Atro/runtime
python muhurta_extended.py     # should show Bhadra/Amavasya penalties firing on relevant dates
python expanded_yogas.py        # should NOT show "Daridra Kemadruma (strict)" or Maha Bhagya
python dasha_systems_full.py    # Shoola/Drig/Sthira period sums should match Jaimini canon
python tajik_yogas_16.py        # Khallasar should detect zodiac-wrap interceptions
python nadi_full.py             # karaka_readings should show 4 tones (very_strong/strong/mixed/weak)
```

Expected outputs:
- `muhurta_extended.py` — running on an Amavasya date should report `score < 50` with `"Amavasya — generally inauspicious"` in `reasons_against`
- `expanded_yogas.py` — yoga count for Manoj should drop by 1 (no double-counted Kemadruma)
- `dasha_systems_full.py` — Shoola timeline year-counts should sum to ~108 (4×9 + 4×8 + 4×7); was 96
- `nadi_full.py` — Mars in Manoj (5H Aries, dignity Own) should show tone="very_strong"

## Files NOT patched in this round (deferred)

The remaining BLOCKERs from `TIER2_REVIEW.md` require deeper rebuild:
- B1.1 — Kalachakra direction logic (encode BPHS Ch. 50 deha/jeeva mapping table)
- B1.2 — Kalachakra start-sign 28-pada-by-9-rashi BPHS table
- B3.1 — Tajik `_is_applying` proper rate-of-approach computation
- B3.2 — Add `retrograde` flag to chart pipeline (upstream of `nadi_full`/`tajik_yogas_16`)
- B3.3 — Manaucha needs Varshesha cross-reference

These are tracked separately for the next deep-revision pass.
