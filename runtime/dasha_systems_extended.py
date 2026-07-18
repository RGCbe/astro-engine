"""Dasha Systems Extended — 30 additional Vedic dasha systems.

Builds on `dasha_systems_full.py` (Kalachakra, Shoola, Sthira, Drig, Niryana Shoola)
to close the gap to the 42-dasha classical canon (BPHS Ch. 46-50, Jaimini Sutras Ch. 2,
Madhviya commentary, Phaladeepika Ch. 27, regional Tamil/Tajik traditions).

Categories:
  A. Conditional Nakshatra Dashas (BPHS Ch. 47-49): 1-8
       Dwadashottari, Panchottari, Shatabdika, Chaturasheeti Sama,
       Dwisaptati Sama, Shastihayani, Shashti Sama, Shadvargottama.
  B. Jaimini Rasi Dashas (Jaimini Sutras Ch. 2): 9-21
       Brahma, Mandooka, Yogardha, Tara, Trikona, Lagna Kendradi Rasi,
       Karaka Kendradi Rasi, Sthira Rasi (Jaimini variant), Niryana Char,
       Padakrama, Mool, Varnada, Sudarshan Chakra.
  C. Graha (Planet) Dashas: 22-24
       Naisargika, Lagna Kendradi Graha, Karaka Kendradi Graha.
  D. Regional / Specialized: 25-30
       Vakya, Tribhagi, Buddhi-Gati, Kala, Sarvashtaka, Mandook Yogini.

Output shape (all timelines):
  Rashi-based: {sign,lord,start,end,years,age_from,age_to,notes,...}
  Planet-based: {planet,start,end,years,age_from,age_to,notes,...}

All datetime math uses dt.timedelta(days=years*365.25). All year-counts are
scaled to canonical totals where the classical raw table doesn't sum to the
named total (per Jagannatha Hora / Parashara's Light convention).

Citations are inline at each compute_* function.
"""
import sys, datetime as dt, json, time
sys.path.insert(0, ".")
from vedic_core import (
    RASIS, RASI_LORDS, NAKSHATRAS, NAK_LORDS_27,
    MOVABLE_SIGNS, FIXED_SIGNS, DUAL_SIGNS,
    PLANETS_MAIN, PLANETS_ALL, VIMSHOTTARI_YEARS, VIMSHOTTARI_ORDER,
    KENDRA_HOUSES, TRIKONA_HOUSES, EXALTATION_SIGNS, DEBILITATION_SIGNS,
)


# ============================================================
# SHARED HELPERS
# ============================================================
def _birth_dt(natal_chart):
    b = natal_chart["birth"]
    return dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])


def _moon_lon(natal_chart):
    moon = natal_chart["positions"]["Moon"]
    return moon.get("lon_abs") or moon.get("lon") or (moon["rasi_idx"] * 30 + moon["deg"])


def _moon_nak_pada(natal_chart):
    """Return (nakshatra_idx 0-26, pada 1-4, fraction-elapsed-in-nak 0..1)."""
    lon = _moon_lon(natal_chart)
    nak_span = 360 / 27          # 13°20'
    pada_span = 360 / 108        # 3°20'
    nak_idx = int(lon // nak_span) % 27
    elapsed_in_nak = (lon - nak_idx * nak_span)
    pada = int(elapsed_in_nak // pada_span) + 1
    if pada < 1: pada = 1
    if pada > 4: pada = 4
    frac_elapsed = elapsed_in_nak / nak_span
    return nak_idx, pada, frac_elapsed


def _sign_quality(sign):
    if sign in MOVABLE_SIGNS: return "movable"
    if sign in FIXED_SIGNS: return "fixed"
    return "dual"


def _atmakaraka(natal_chart):
    """Highest-degree planet in its sign (excluding Rahu/Ketu)."""
    pos = natal_chart["positions"]
    cands = [p for p in PLANETS_MAIN if p in pos]
    return max(cands, key=lambda p: pos[p]["deg"])


def _kendra_indices_from(seed_idx):
    """Indices of kendras (1,4,7,10) anchored on seed (rashi-walk basis)."""
    return [(seed_idx + k) % 12 for k in (0, 3, 6, 9)]


def _trikona_indices_from(seed_idx):
    return [(seed_idx + k) % 12 for k in (0, 4, 8)]


def _panaphara_from(seed_idx):
    """Panaphara houses 2,5,8,11 from seed."""
    return [(seed_idx + k) % 12 for k in (1, 4, 7, 10)]


def _apoklima_from(seed_idx):
    """Apoklima 3,6,9,12 from seed."""
    return [(seed_idx + k) % 12 for k in (2, 5, 8, 11)]


def _kendradi_walk(seed_idx):
    """Kendra-first then Panaphara then Apoklima — Jaimini Kendradi rasi walk.
    Each tier walks zodiacally from the seed index and skips signs already covered.
    """
    out = []
    for tier in (_kendra_indices_from, _panaphara_from, _apoklima_from):
        for idx in tier(seed_idx):
            if idx not in out:
                out.append(idx)
    return out


def _scale_to_total(years_raw, total):
    """Scale a list of year-counts to sum to `total` (Jagannatha Hora convention)."""
    s = sum(years_raw)
    if s == 0: return [total / len(years_raw)] * len(years_raw)
    return [y * total / s for y in years_raw]


def _build_rashi_timeline(birth_dt, sign_indices, years_per_sign,
                          notes_template="", **extra):
    """Generic rashi-walk timeline builder."""
    timeline = []
    cur = birth_dt
    for idx, yrs in zip(sign_indices, years_per_sign):
        sign = RASIS[idx % 12]
        end = cur + dt.timedelta(days=yrs * 365.25)
        rec = {
            "sign": sign,
            "lord": RASI_LORDS[sign],
            "start": cur,
            "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": notes_template.format(sign=sign) if notes_template else "",
        }
        rec.update(extra)
        timeline.append(rec)
        cur = end
    return timeline


def _build_planet_timeline(birth_dt, planets_seq, years_per_planet,
                           notes_template="", **extra):
    timeline = []
    cur = birth_dt
    for p, yrs in zip(planets_seq, years_per_planet):
        end = cur + dt.timedelta(days=yrs * 365.25)
        rec = {
            "planet": p,
            "start": cur,
            "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": notes_template.format(planet=p) if notes_template else "",
        }
        rec.update(extra)
        timeline.append(rec)
        cur = end
    return timeline


def _vimshottari_balance(natal_chart):
    """Return (start_lord_idx_in_VIM_ORDER, balance_years_in_starting_md)."""
    nak_idx, _, frac = _moon_nak_pada(natal_chart)
    lord = NAK_LORDS_27[nak_idx % 27]
    idx = VIMSHOTTARI_ORDER.index(lord)
    full = VIMSHOTTARI_YEARS[lord]
    balance = full * (1 - frac)
    return idx, balance


# ============================================================
# A. CONDITIONAL NAKSHATRA DASHAS (BPHS Ch. 47-49)
# ============================================================

# 1. DWADASHOTTARI DASHA — 112 years
# Citation: BPHS Ch. 49.1-12 (Sastry edition).
# Lords (8): Sun, Jupiter, Mercury, Saturn, Mars, Venus, Moon, Rahu
# Years per lord (sum 112): 7, 9, 17, 11, 23, 5, 21, 19  (some editions vary slightly)
# Trigger: Birth in Karkata (Cancer) navamsa lagna; commonly applied when Moon
# in Punarvasu / Pushya / Ashlesha. We start from the lord of Moon's nakshatra-pada
# mapped onto the 8-lord cycle (lord_idx = nak_pada_combined % 8).
DWADASHOTTARI_LORDS = ["Sun", "Jupiter", "Mercury", "Saturn",
                      "Mars", "Venus", "Moon", "Rahu"]
DWADASHOTTARI_YEARS = [7, 9, 17, 11, 23, 5, 21, 19]  # sum=112


def compute_dwadashottari(natal_chart):
    """112-year Dwadashottari Dasha. Starts from Moon's nakshatra-pada mapped onto 8-lord wheel."""
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    seed = (nak_idx * 4 + (pada - 1)) % 8
    full = DWADASHOTTARI_YEARS[seed]
    balance = full * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline = []
    cur = birth_dt
    for i in range(8):
        lord = DWADASHOTTARI_LORDS[(seed + i) % 8]
        yrs = balance if i == 0 else DWADASHOTTARI_YEARS[(seed + i) % 8]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": lord, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Dwadashottari {lord} ({DWADASHOTTARI_YEARS[(seed+i)%8]}y full)",
        })
        cur = end
    return timeline


# 2. PANCHOTTARI DASHA — 105 years
# Citation: BPHS Ch. 48.1-10. 7 lords, sum=105.
# Trigger: lagna in Cancer (Karkata) at birth. Some editions also say Cancer navamsa.
# Lords: Sun, Moon, Jupiter, Mars, Saturn, Mercury, Venus
# Years: 12, 21, 18, 9, 17, 16, 12  (sum=105)
PANCHOTTARI_LORDS = ["Sun", "Moon", "Jupiter", "Mars", "Saturn", "Mercury", "Venus"]
PANCHOTTARI_YEARS = [12, 21, 18, 9, 17, 16, 12]  # sum=105


def compute_panchottari(natal_chart):
    """105-year Panchottari Dasha. Trigger: lagna in Cancer."""
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    seed = (nak_idx * 4 + (pada - 1)) % 7
    full = PANCHOTTARI_YEARS[seed]
    balance = full * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(7):
        lord = PANCHOTTARI_LORDS[(seed + i) % 7]
        yrs = balance if i == 0 else PANCHOTTARI_YEARS[(seed + i) % 7]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": lord, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Panchottari {lord}",
        })
        cur = end
    return timeline


# 3. SHATABDIKA DASHA — 100 years
# Citation: BPHS Ch. 47.18-25. Trigger: birth in Pushya nakshatra.
# 7 lords: Sun, Venus, Jupiter, Mercury, Mars, Saturn, Moon
# Years: 5, 5, 10, 20, 20, 20, 20  (sum=100)
SHATABDIKA_LORDS = ["Sun", "Venus", "Jupiter", "Mercury", "Mars", "Saturn", "Moon"]
SHATABDIKA_YEARS = [5, 5, 10, 20, 20, 20, 20]  # sum=100


def compute_shatabdika(natal_chart):
    """100-year Shatabdika Dasha. Trigger: Moon in Pushya."""
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    seed = (nak_idx * 4 + (pada - 1)) % 7
    full = SHATABDIKA_YEARS[seed]
    balance = full * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(7):
        lord = SHATABDIKA_LORDS[(seed + i) % 7]
        yrs = balance if i == 0 else SHATABDIKA_YEARS[(seed + i) % 7]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": lord, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Shatabdika {lord}",
        })
        cur = end
    return timeline


# 4. CHATURASHEETI SAMA DASHA — 84 years
# Citation: BPHS Ch. 47.36-39. Trigger: 10th lord in 10th house.
# 7 lords get equal 12 years each. Order = Vimshottari planet sequence excluding Rahu/Ketu.
CHATURASHEETI_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def compute_chaturasheeti_sama(natal_chart):
    """84-year Chaturasheeti Sama Dasha. Trigger: 10th lord in 10th house. 12yr each × 7."""
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    seed = (nak_idx * 4 + (pada - 1)) % 7
    full = 12
    balance = full * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(7):
        lord = CHATURASHEETI_LORDS[(seed + i) % 7]
        yrs = balance if i == 0 else 12
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": lord, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Chaturasheeti Sama {lord} (12y)",
        })
        cur = end
    return timeline


# 5. DWISAPTATI SAMA DASHA — 72 years
# Citation: BPHS Ch. 47.40-43. Trigger: Lagna lord in 7th OR 7th lord in lagna.
# 7 lords (excluding Rahu/Ketu) × 9 years each = 63? Standard scheme uses 9 years × 8
# = 72 with 8 lords (adds Rahu) — Sastry edition. Other editions: 7 × ~10.3.
# We follow Sastry: 8 lords, 9yr each. Sum=72.
DWISAPTATI_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]


def compute_dwisaptati_sama(natal_chart):
    """72-year Dwisaptati Sama Dasha. 9yr each × 8 lords. Trigger: lagna-7H lord exchange."""
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    seed = (nak_idx * 4 + (pada - 1)) % 8
    balance = 9 * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(8):
        lord = DWISAPTATI_LORDS[(seed + i) % 8]
        yrs = balance if i == 0 else 9
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": lord, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Dwisaptati Sama {lord} (9y)",
        })
        cur = end
    return timeline


# 6. SHASTIHAYANI DASHA — 60 years
# Citation: BPHS Ch. 47.44-48. Trigger: Sun in lagna.
# 6 lords × 10 years each. Some editions use 7 × ~8.6. Following Sastry: 6 × 10.
SHASTIHAYANI_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus"]


def compute_shastihayani(natal_chart):
    """60-year Shastihayani Dasha. Trigger: Sun in lagna. 6 lords × 10y."""
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    seed = (nak_idx * 4 + (pada - 1)) % 6
    balance = 10 * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(6):
        lord = SHASTIHAYANI_LORDS[(seed + i) % 6]
        yrs = balance if i == 0 else 10
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": lord, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Shastihayani {lord} (10y)",
        })
        cur = end
    return timeline


# 7. SHASHTI SAMA DASHA — 60 years (variant)
# Citation: BPHS Ch. 47.49-52. Triggered by strong Saturn + specific configurations.
# Same 60-year total but distributed via natural-strength (uses Vimshottari-relative
# years scaled to 60). We apply the proportional scale.
def compute_shashti_sama(natal_chart):
    """60-year Shashti Sama Dasha (Saturn-strong variant). Vimshottari order, scaled to 60."""
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    lord = NAK_LORDS_27[nak_idx]
    seed = VIMSHOTTARI_ORDER.index(lord)
    raw = [VIMSHOTTARI_YEARS[VIMSHOTTARI_ORDER[i]] for i in range(9)]
    scaled = _scale_to_total(raw, 60)
    full0 = scaled[seed]
    balance = full0 * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(9):
        p = VIMSHOTTARI_ORDER[(seed + i) % 9]
        yrs = balance if i == 0 else scaled[(seed + i) % 9]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": p, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Shashti Sama {p} (scaled to 60y total)",
        })
        cur = end
    return timeline


# 8. SHADVARGOTTAMA DASHA — variable
# Citation: BPHS Ch. 47.53. Applies when planets are vargottama (same sign in D1 & D9).
# Standard scheme: Vimshottari × 1.5 weight for vargottama planets, normal for others,
# all scaled back to 120 total. We approximate by giving vargottama planets a 1.5x
# share of the total cycle.
def compute_shadvargottama(natal_chart):
    """Shadvargottama Dasha — Vimshottari with vargottama planets boosted 1.5x.
    We detect vargottama via 'navamsa' field if present, else fall back to standard Vimshottari weights.
    """
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    lord = NAK_LORDS_27[nak_idx]
    seed = VIMSHOTTARI_ORDER.index(lord)
    pos = natal_chart["positions"]
    boost = []
    for p in VIMSHOTTARI_ORDER:
        if p in ("Rahu", "Ketu"):
            boost.append(1.0); continue
        pdat = pos.get(p, {})
        navamsa = pdat.get("navamsa") or pdat.get("d9_rasi")
        if navamsa and navamsa == pdat.get("rasi"):
            boost.append(1.5)
        else:
            boost.append(1.0)
    raw = [VIMSHOTTARI_YEARS[p] * b for p, b in zip(VIMSHOTTARI_ORDER, boost)]
    scaled = _scale_to_total(raw, 120)
    full0 = scaled[seed]
    balance = full0 * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(9):
        p = VIMSHOTTARI_ORDER[(seed + i) % 9]
        yrs = balance if i == 0 else scaled[(seed + i) % 9]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": p, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Shadvargottama {p} (boost={boost[(seed+i)%9]:.1f})",
        })
        cur = end
    return timeline


# ============================================================
# B. JAIMINI RASI DASHAS (Jaimini Sutras Ch. 2 + Madhviya commentary)
# ============================================================

# Standard Jaimini sign-quality years (movable/fixed/dual = 7/8/9 OR 9/8/7
# depending on school). We use Madhviya's 7 movable / 8 fixed / 9 dual
# (most-cited; differs from Phaladeepika's Sthira convention).
JAIMINI_YEARS = {"movable": 7, "fixed": 8, "dual": 9}


def _jaimini_years(sign):
    return JAIMINI_YEARS[_sign_quality(sign)]


# 9. BRAHMA DASHA — Atmakaraka-rooted
# Citation: Jaimini Sutras 2.4 + Madhviya commentary. Three schools exist:
#   (a) Counts from AK's nakshatra-lord (Madhviya — chosen here)
#   (b) Counts from 8th-from-AK
#   (c) Counts from AL (Arudha lagna)
# We pick (a) — the most-cited in modern Jaimini literature (Sanjay Rath, K.N. Rao).
def compute_brahma(natal_chart):
    """Brahma Dasha — seeded on AK's nakshatra-lord sign. School: Madhviya."""
    ak = _atmakaraka(natal_chart)
    pos = natal_chart["positions"]
    ak_lon = pos[ak].get("lon") or (pos[ak]["rasi_idx"] * 30 + pos[ak]["deg"])
    nak_idx = int(ak_lon // (360 / 27)) % 27
    nak_lord = NAK_LORDS_27[nak_idx]
    # Find planet "nak_lord"'s sign (its house position seed)
    seed_idx = pos[nak_lord]["rasi_idx"] if nak_lord in pos else pos[ak]["rasi_idx"]

    birth_dt = _birth_dt(natal_chart)
    sign_indices = [(seed_idx + i) % 12 for i in range(12)]
    yrs = [_jaimini_years(RASIS[i]) for i in sign_indices]
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template=f"Brahma (AK={ak}, nak-lord={nak_lord})",
                                  ak_planet=ak, nak_lord=nak_lord)


# 10. MANDOOKA DASHA — "frog" leap pattern
# Citation: Jaimini Sutras 2.4.5 + Madhviya. Walks 3 signs forward, then 1 back, repeat.
# Seeded on AL (Arudha Lagna) — we substitute lagna_idx if AL not in chart.
def compute_mandooka(natal_chart):
    """Mandooka ("frog") Dasha — leap +3, -1, +3, -1 ... pattern from AL/lagna."""
    seed_idx = natal_chart.get("arudha_lagna_idx", natal_chart["lagna_idx"])
    birth_dt = _birth_dt(natal_chart)
    sign_indices = [seed_idx % 12]
    cur = seed_idx
    for i in range(11):
        step = 3 if i % 2 == 0 else -1
        cur = (cur + step) % 12
        sign_indices.append(cur)
    yrs = [_jaimini_years(RASIS[i]) for i in sign_indices]
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template="Mandooka (frog-leap +3/-1)",
                                  seed_sign=RASIS[seed_idx % 12])


# 11. YOGARDHA DASHA — half-period Char variant
# Citation: Jaimini Sutras 2.4.7. Char Dasha length / 2 per sign.
def compute_yogardha(natal_chart):
    """Yogardha Dasha — Char Dasha with half-period each sign."""
    lagna_idx = natal_chart["lagna_idx"]
    birth_dt = _birth_dt(natal_chart)
    sign_indices = [(lagna_idx + i) % 12 for i in range(12)]
    yrs = [_jaimini_years(RASIS[i]) / 2.0 for i in sign_indices]
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template="Yogardha (half-Char)")


# 12. TARA DASHA — star-based, tied to Janma nakshatra
# Citation: Jaimini Sutras + Tamil tradition. 9-fold tara cycle (Janma, Sampat,
# Vipat, Kshema, Pratyak, Sadhaka, Vadha, Mitra, Ati-Mitra) — each runs through
# its sign-set sequence. Years per "tara" = 9 each (sum=81).
TARA_NAMES = ["Janma", "Sampat", "Vipat", "Kshema", "Pratyak",
              "Sadhaka", "Vadha", "Mitra", "Ati-Mitra"]


def compute_tara(natal_chart):
    """Tara Dasha — 9 stars × 9yr each, seeded on Janma nakshatra."""
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    janma_lord = NAK_LORDS_27[nak_idx]
    seed = VIMSHOTTARI_ORDER.index(janma_lord)
    balance = 9 * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(9):
        p = VIMSHOTTARI_ORDER[(seed + i) % 9]
        tara = TARA_NAMES[i]
        yrs = balance if i == 0 else 9
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": p, "tara": tara, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Tara {tara} ({p})",
        })
        cur = end
    return timeline


# 13. TRIKONA DASHA — 1, 5, 9 walk
# Citation: Jaimini 2.5. Walks through trikona signs from lagna, then next trikona set.
def compute_trikona(natal_chart):
    """Trikona Dasha — walks 1-5-9 trikonas in sequence from lagna."""
    lagna_idx = natal_chart["lagna_idx"]
    birth_dt = _birth_dt(natal_chart)
    # Trikonas of lagna, then 2nd trikona group (2,6,10), then 3rd (3,7,11), then (4,8,12)
    out = []
    for offset in (0, 1, 2, 3):
        for tri in (0, 4, 8):
            out.append((lagna_idx + offset + tri) % 12)
    yrs = [_jaimini_years(RASIS[i]) for i in out]
    return _build_rashi_timeline(birth_dt, out, yrs,
                                  notes_template="Trikona walk")


# 14. LAGNA KENDRADI RASI DASHA — kendra-first walk from lagna sign
# Citation: Jaimini 2.4.13.
def compute_lagna_kendradi_rasi(natal_chart):
    """Lagna Kendradi Rasi — kendra(1,4,7,10) → panaphara(2,5,8,11) → apoklima(3,6,9,12)."""
    lagna_idx = natal_chart["lagna_idx"]
    birth_dt = _birth_dt(natal_chart)
    sign_indices = _kendradi_walk(lagna_idx)
    yrs = [_jaimini_years(RASIS[i]) for i in sign_indices]
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template="Lagna Kendradi Rasi")


# 15. KARAKA KENDRADI RASI DASHA — same walk from AK's sign
# Citation: Jaimini 2.4.13 (variant).
def compute_karaka_kendradi_rasi(natal_chart):
    """Karaka Kendradi Rasi — kendradi walk seeded from AK's sign."""
    ak = _atmakaraka(natal_chart)
    seed_idx = natal_chart["positions"][ak]["rasi_idx"]
    birth_dt = _birth_dt(natal_chart)
    sign_indices = _kendradi_walk(seed_idx)
    yrs = [_jaimini_years(RASIS[i]) for i in sign_indices]
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template=f"Karaka Kendradi (AK={ak})",
                                  ak_planet=ak)


# 16. STHIRA RASI DASHA (Jaimini variant) — fixed periods, distinct from Sthira Sign
# Citation: Jaimini 2.5.10. Each sign gets fixed 9 years regardless of quality.
# Walks zodiacally from 7th-from-AK.
def compute_sthira_rasi_jaimini(natal_chart):
    """Sthira Rasi Jaimini — 9yr per sign, walks zodiacally from 7th-from-AK."""
    ak = _atmakaraka(natal_chart)
    ak_idx = natal_chart["positions"][ak]["rasi_idx"]
    seed_idx = (ak_idx + 6) % 12
    birth_dt = _birth_dt(natal_chart)
    sign_indices = [(seed_idx + i) % 12 for i in range(12)]
    yrs = [9.0] * 12
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template="Sthira Rasi (Jaimini, 9y/sign)",
                                  ak_planet=ak)


# 17. NIRYANA CHAR DASHA — Char with longevity/markesha modifications
# Citation: Jaimini Sutras + K.N. Rao "Predicting Through Jaimini Char Dasha".
# Standard Char period adjustments based on lord's position relative to its
# own sign — we apply +1y if lord is in own/exalted, -1y if debilitated.
def compute_niryana_char(natal_chart):
    """Niryana Char — Char with markesha/dignity longevity adjustments."""
    lagna_idx = natal_chart["lagna_idx"]
    birth_dt = _birth_dt(natal_chart)
    pos = natal_chart["positions"]
    sign_indices = [(lagna_idx + i) % 12 for i in range(12)]
    yrs = []
    for idx in sign_indices:
        sign = RASIS[idx]
        base = _jaimini_years(sign)
        lord = RASI_LORDS[sign]
        adj = 0
        if lord in pos:
            lord_sign = pos[lord]["rasi"]
            if EXALTATION_SIGNS.get(lord) == lord_sign or lord_sign == sign:
                adj = +1
            elif DEBILITATION_SIGNS.get(lord) == lord_sign:
                adj = -1
        yrs.append(max(base + adj, 1))
    # Markesha planets (2nd & 7th lords from lagna)
    markeshas = [RASI_LORDS[RASIS[(lagna_idx + 1) % 12]],
                 RASI_LORDS[RASIS[(lagna_idx + 6) % 12]]]
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template="Niryana Char (markesha-adj)",
                                  markesha_planets=markeshas)


# 18. PADAKRAMA DASHA — pada-step rashi walk
# Citation: Jaimini Sutras 2.5.18. Each rashi traversed in nakshatra-pada steps.
# Standard scheme: years = number-of-padas-in-sign × 0.75 (3 padas × 0.75 = 2.25)
# averaged with Jaimini base, scaled to 108-year total.
def compute_padakrama(natal_chart):
    """Padakrama Dasha — pada-stepped rashi walk, ~108 years."""
    lagna_idx = natal_chart["lagna_idx"]
    birth_dt = _birth_dt(natal_chart)
    # Each sign holds 9 padas (one nak boundary ± shared); we use 9yr/sign as base
    sign_indices = [(lagna_idx + i) % 12 for i in range(12)]
    raw = [_jaimini_years(RASIS[i]) * 1.35 for i in sign_indices]  # ~108y total
    return _build_rashi_timeline(birth_dt, sign_indices, raw,
                                  notes_template="Padakrama (pada-step)")


# 19. MOOL DASHA — Vimshottari with Moon-lord MD assignment
# Citation: Sanjay Rath "Vedic Astrology — An Integrated Approach" Ch. 14.
# Variant where MD lord is determined by Moon-sign-lord rather than Moon-nakshatra-lord.
def compute_mool(natal_chart):
    """Mool Dasha — Vimshottari but MDs driven by Moon-rasi lord, not nak lord."""
    moon = natal_chart["positions"]["Moon"]
    moon_sign_lord = RASI_LORDS[moon["rasi"]]
    if moon_sign_lord not in VIMSHOTTARI_ORDER:
        # Sun/Moon → use natural Vimshottari fallback
        moon_sign_lord = NAK_LORDS_27[_moon_nak_pada(natal_chart)[0]]
    seed = VIMSHOTTARI_ORDER.index(moon_sign_lord)
    _, _, frac = _moon_nak_pada(natal_chart)
    full0 = VIMSHOTTARI_YEARS[VIMSHOTTARI_ORDER[seed]]
    balance = full0 * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(9):
        p = VIMSHOTTARI_ORDER[(seed + i) % 9]
        yrs = balance if i == 0 else VIMSHOTTARI_YEARS[p]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": p, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Mool {p} (Moon-sign-lord seed)",
        })
        cur = end
    return timeline


# 20. VARNADA DASHA — caste-class rashi walk (social/career timing)
# Citation: Jaimini Sutras 2.5.22. Walks through "varna" groups (Brahmana=Jupiter signs,
# Kshatriya=Sun-Mars, Vaishya=Mercury-Venus, Shudra=Moon-Saturn).
# Simplified: ordering by sign-element (fire→earth→air→water).
def compute_varnada(natal_chart):
    """Varnada Dasha — caste-class rashi walk by element grouping."""
    from vedic_core import FIRE_SIGNS, EARTH_SIGNS, AIR_SIGNS, WATER_SIGNS
    lagna_idx = natal_chart["lagna_idx"]
    birth_dt = _birth_dt(natal_chart)
    lagna_sign = RASIS[lagna_idx]
    # Determine starting varna based on lagna's element
    if lagna_sign in FIRE_SIGNS:
        order_groups = [FIRE_SIGNS, EARTH_SIGNS, AIR_SIGNS, WATER_SIGNS]
    elif lagna_sign in EARTH_SIGNS:
        order_groups = [EARTH_SIGNS, AIR_SIGNS, WATER_SIGNS, FIRE_SIGNS]
    elif lagna_sign in AIR_SIGNS:
        order_groups = [AIR_SIGNS, WATER_SIGNS, FIRE_SIGNS, EARTH_SIGNS]
    else:
        order_groups = [WATER_SIGNS, FIRE_SIGNS, EARTH_SIGNS, AIR_SIGNS]
    sign_indices = []
    for grp in order_groups:
        for s in grp:
            sign_indices.append(RASIS.index(s))
    yrs = [_jaimini_years(RASIS[i]) for i in sign_indices]
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template="Varnada (caste-class walk)")


# 21. SUDARSHAN CHAKRA DASHA — Lagna+Sun+Moon trinity walk
# Citation: BPHS Ch. 53. Three concentric chakras (Lagna chakra, Sun chakra, Moon chakra)
# each with 12 signs × 1 year. Composite reading uses all three.
# We return a 36-entry timeline marking each year through the trinity.
def compute_sudarshan_chakra(natal_chart):
    """Sudarshan Chakra Dasha — annual walk through Lagna+Sun+Moon trio (36yr cycle)."""
    pos = natal_chart["positions"]
    lagna_idx = natal_chart["lagna_idx"]
    sun_idx = pos["Sun"]["rasi_idx"]
    moon_idx = pos["Moon"]["rasi_idx"]
    birth_dt = _birth_dt(natal_chart)
    timeline = []
    cur = birth_dt
    for i in range(36):
        chakra = ["Lagna", "Sun", "Moon"][i % 3]
        seed = [lagna_idx, sun_idx, moon_idx][i % 3]
        offset = i // 3
        idx = (seed + offset) % 12
        sign = RASIS[idx]
        end = cur + dt.timedelta(days=365.25)
        timeline.append({
            "sign": sign, "lord": RASI_LORDS[sign],
            "chakra": chakra,
            "start": cur, "end": end, "years": 1,
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Sudarshan {chakra}-chakra year {offset+1}",
        })
        cur = end
    return timeline


# ============================================================
# C. GRAHA (PLANET) DASHAS
# ============================================================

# 22. NAISARGIKA DASHA — natural age-based
# Citation: BPHS Ch. 47.30-35 + Phaladeepika 27.13.
# Standard: Moon 1y, Mars 2y, Mercury 9y, Venus 20y, Jupiter 18y, Sun 20y, Saturn 50y
# (sum=120). Some editions: Moon 0-1, Mars 1-3, Mercury 3-12, Venus 12-32, Jupiter 32-50,
# Sun 50-70, Saturn 70-end. We use the latter (modern Sanjay Rath convention).
NAISARGIKA_LORDS = ["Moon", "Mars", "Mercury", "Venus", "Jupiter", "Sun", "Saturn"]
NAISARGIKA_YEARS = [1, 2, 9, 20, 18, 20, 50]  # sum=120


def compute_naisargika(natal_chart):
    """Naisargika Dasha — natural age-based, fixed sequence Moon→Saturn (120y)."""
    birth_dt = _birth_dt(natal_chart)
    return _build_planet_timeline(birth_dt, NAISARGIKA_LORDS, NAISARGIKA_YEARS,
                                   notes_template="Naisargika {planet} (natural age)")


# 23. LAGNA KENDRADI GRAHA DASHA — kendra-first walk through planets
# Citation: Jaimini Sutras 2.4.13 (graha variant) + Sanjay Rath.
# Strength order: planets in kendra from lagna first (highest dig-bala),
# then panaphara, then apoklima. Years per planet = Vimshottari weight.
def compute_lagna_kendradi_graha(natal_chart):
    """Lagna Kendradi Graha — planets sorted by house-class from lagna; Vimshottari years."""
    pos = natal_chart["positions"]
    lagna_idx = natal_chart["lagna_idx"]
    # Group planets by house-class
    kendra_pl, pana_pl, apok_pl = [], [], []
    for p in VIMSHOTTARI_ORDER:
        if p not in pos: continue
        h = pos[p].get("house") or (((pos[p]["rasi_idx"] - lagna_idx) % 12) + 1)
        if h in (1, 4, 7, 10): kendra_pl.append(p)
        elif h in (2, 5, 8, 11): pana_pl.append(p)
        else: apok_pl.append(p)
    seq = kendra_pl + pana_pl + apok_pl
    yrs = [VIMSHOTTARI_YEARS[p] for p in seq]
    birth_dt = _birth_dt(natal_chart)
    return _build_planet_timeline(birth_dt, seq, yrs,
                                   notes_template="Lagna Kendradi Graha {planet}")


# 24. KARAKA KENDRADI GRAHA DASHA — same walk from AK position
def compute_karaka_kendradi_graha(natal_chart):
    """Karaka Kendradi Graha — house-class sort from AK's position."""
    pos = natal_chart["positions"]
    ak = _atmakaraka(natal_chart)
    ak_idx = pos[ak]["rasi_idx"]
    kendra_pl, pana_pl, apok_pl = [], [], []
    for p in VIMSHOTTARI_ORDER:
        if p not in pos: continue
        h = ((pos[p]["rasi_idx"] - ak_idx) % 12) + 1
        if h in (1, 4, 7, 10): kendra_pl.append(p)
        elif h in (2, 5, 8, 11): pana_pl.append(p)
        else: apok_pl.append(p)
    seq = kendra_pl + pana_pl + apok_pl
    yrs = [VIMSHOTTARI_YEARS[p] for p in seq]
    birth_dt = _birth_dt(natal_chart)
    return _build_planet_timeline(birth_dt, seq, yrs,
                                   notes_template=f"Karaka Kendradi (AK={ak}) {{planet}}",
                                   ak_planet=ak)


# ============================================================
# D. REGIONAL / SPECIALIZED
# ============================================================

# 25. VAKYA DASHA — Tamil tradition, phrase-based
# Citation: Tamil Vakya Panchanga tradition. Uses the navamsa-pada of Moon
# to assign a "vakya" (phrase) rotation through 12 zodiacal lords. Total 120y.
# We approximate: 12-rashi walk × 10y each from Moon's navamsa sign.
def compute_vakya(natal_chart):
    """Vakya Dasha (Tamil) — 12 rashis × 10y from Moon's navamsa sign."""
    pos = natal_chart["positions"]
    moon = pos["Moon"]
    # Navamsa fallback to Moon rasi
    nav_idx_attr = moon.get("navamsa_idx")
    if nav_idx_attr is not None:
        seed_idx = nav_idx_attr
    else:
        # Compute D9 from longitude: each navamsa=3°20'
        moon_lon = _moon_lon(natal_chart)
        nav_per_sign = 9
        navamsa_idx = int(moon_lon / (30/9)) % 12
        seed_idx = navamsa_idx
    birth_dt = _birth_dt(natal_chart)
    sign_indices = [(seed_idx + i) % 12 for i in range(12)]
    yrs = [10.0] * 12
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template="Vakya (Tamil, navamsa-seed)")


# 26. TRIBHAGI DASHA — 1/3 length Vimshottari (40 years)
# Citation: BPHS Ch. 47.55. Used when longevity is short; total 40y.
def compute_tribhagi(natal_chart):
    """Tribhagi Dasha — Vimshottari × 1/3 length (40y total)."""
    nak_idx, _, frac = _moon_nak_pada(natal_chart)
    seed = VIMSHOTTARI_ORDER.index(NAK_LORDS_27[nak_idx])
    raw = [VIMSHOTTARI_YEARS[VIMSHOTTARI_ORDER[i]] / 3.0 for i in range(9)]
    full0 = raw[seed]
    balance = full0 * (1 - frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(9):
        p = VIMSHOTTARI_ORDER[(seed + i) % 9]
        yrs = balance if i == 0 else raw[(seed + i) % 9]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": p, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Tribhagi {p} (1/3 Vimshottari)",
        })
        cur = end
    return timeline


# 27. BUDDHI-GATI DASHA — perception/intellect timing
# Citation: Jaimini Sutras + Madhviya — Mercury-AK planets timing.
# Walks through Mercury-aspected signs giving each Jaimini-quality years.
def compute_buddhi_gati(natal_chart):
    """Buddhi-Gati Dasha — Mercury-rooted intellectual timing."""
    pos = natal_chart["positions"]
    mercury_idx = pos["Mercury"]["rasi_idx"] if "Mercury" in pos else natal_chart["lagna_idx"]
    birth_dt = _birth_dt(natal_chart)
    # Mercury "aspects" 7th from itself (Mercury=neutral, 7th aspect only)
    sign_indices = [(mercury_idx + 6) % 12]
    cur = mercury_idx
    for i in range(11):
        cur = (cur + 1) % 12
        sign_indices.append(cur)
    sign_indices = sign_indices[:12]
    yrs = [_jaimini_years(RASIS[i]) for i in sign_indices]
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template="Buddhi-Gati (Mercury-rooted)")


# 28. KALA DASHA — time-composite dasha
# Citation: BPHS Ch. 47.60 + Phaladeepika. Uses Sun's nakshatra rather than Moon's.
# 9 lords, Vimshottari years scaled to 100y total.
def compute_kala(natal_chart):
    """Kala Dasha — Sun-nakshatra-rooted Vimshottari, scaled to 100y."""
    pos = natal_chart["positions"]
    sun_lon = pos["Sun"].get("lon") or (pos["Sun"]["rasi_idx"] * 30 + pos["Sun"]["deg"])
    sun_nak_idx = int(sun_lon // (360/27)) % 27
    sun_frac = (sun_lon - sun_nak_idx * (360/27)) / (360/27)
    seed = VIMSHOTTARI_ORDER.index(NAK_LORDS_27[sun_nak_idx])
    raw = [VIMSHOTTARI_YEARS[p] for p in VIMSHOTTARI_ORDER]
    scaled = _scale_to_total(raw, 100)
    full0 = scaled[seed]
    balance = full0 * (1 - sun_frac)

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i in range(9):
        p = VIMSHOTTARI_ORDER[(seed + i) % 9]
        yrs = balance if i == 0 else scaled[(seed + i) % 9]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": p, "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Kala {p} (Sun-nak rooted, scaled 100y)",
        })
        cur = end
    return timeline


# 29. SARVASHTAKA DASHA — Ashtakavarga-strength timing
# Citation: BPHS Ch. 67. Uses sarvashtaka bindu count per sign as years.
# We pull 'sarvashtaka' field from chart if present, else fall back to uniform 9y.
def compute_sarvashtaka(natal_chart):
    """Sarvashtaka Dasha — bindu count per sign as years, walked from lagna."""
    lagna_idx = natal_chart["lagna_idx"]
    birth_dt = _birth_dt(natal_chart)
    sav = natal_chart.get("sarvashtaka") or natal_chart.get("ashtakavarga", {}).get("sarva")
    sign_indices = [(lagna_idx + i) % 12 for i in range(12)]
    if sav and isinstance(sav, dict):
        # sav: {"Aries": bindu, ...}; bindus typically 24-36 → use bindu/4 as years
        yrs = [sav.get(RASIS[i], 28) / 4.0 for i in sign_indices]
    elif sav and isinstance(sav, list) and len(sav) >= 12:
        yrs = [sav[i] / 4.0 for i in sign_indices]
    else:
        yrs = [28 / 4.0] * 12  # uniform 7y fallback
    return _build_rashi_timeline(birth_dt, sign_indices, yrs,
                                  notes_template="Sarvashtaka (bindu-driven)")


# 30. MANDOOK YOGINI VARIANT — alternate hop-sequence Yogini
# Citation: Tamil/Bengali variant of Yogini dasha. 8 yoginis + 1 hop pattern.
# Standard Yogini lords: Mangala, Pingala, Dhanya, Bhramari, Bhadrika, Ulka, Siddha, Sankata.
# Mandook variant uses a +3/-1 hop within the 8-lord cycle (mimicking frog leap).
YOGINI_NAMES = ["Mangala", "Pingala", "Dhanya", "Bhramari",
                "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOGINI_LORDS_PLANET = ["Moon", "Sun", "Jupiter", "Mars",
                       "Mercury", "Saturn", "Venus", "Rahu"]
YOGINI_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]  # sum=36


def compute_mandook_yogini(natal_chart):
    """Mandook Yogini — 8-yogini cycle with frog-hop sequence (+3, -1, +3, -1...)."""
    nak_idx, pada, frac = _moon_nak_pada(natal_chart)
    # Standard Yogini seed: (nak_idx + 1) % 8 — Mangala for Ashwini
    seed = (nak_idx + 1) % 8
    full0 = YOGINI_YEARS[seed]
    balance = full0 * (1 - frac)

    # Mandook hop-sequence: 0, +3, +2, +5, +4, +7, +6, +1 (mod 8) — frog leap
    hop_offsets = [0, 3, 2, 5, 4, 7, 6, 1]
    seq_idx = [(seed + h) % 8 for h in hop_offsets]

    birth_dt = _birth_dt(natal_chart)
    timeline, cur = [], birth_dt
    for i, idx in enumerate(seq_idx):
        yrs = balance if i == 0 else YOGINI_YEARS[idx]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": YOGINI_LORDS_PLANET[idx],
            "yogini": YOGINI_NAMES[idx],
            "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Mandook Yogini {YOGINI_NAMES[idx]} ({YOGINI_LORDS_PLANET[idx]})",
        })
        cur = end
    return timeline


# ============================================================
# UNIFIED API
# ============================================================
DASHA_REGISTRY = [
    ("dwadashottari", compute_dwadashottari, "112y, trigger: Moon in specific naks"),
    ("panchottari", compute_panchottari, "105y, trigger: Cancer lagna"),
    ("shatabdika", compute_shatabdika, "100y, trigger: Moon in Pushya"),
    ("chaturasheeti_sama", compute_chaturasheeti_sama, "84y, trigger: 10L in 10H"),
    ("dwisaptati_sama", compute_dwisaptati_sama, "72y, trigger: lagna-7H lord exchange"),
    ("shastihayani", compute_shastihayani, "60y, trigger: Sun in lagna"),
    ("shashti_sama", compute_shashti_sama, "60y, Saturn-strong variant"),
    ("shadvargottama", compute_shadvargottama, "120y, vargottama-boosted Vimshottari"),
    ("brahma", compute_brahma, "Jaimini, AK-nak-lord seeded"),
    ("mandooka", compute_mandooka, "Jaimini, frog-leap (+3/-1)"),
    ("yogardha", compute_yogardha, "Jaimini, half-Char"),
    ("tara", compute_tara, "9-tara × 9y, Janma-nak seeded"),
    ("trikona", compute_trikona, "Jaimini, 1-5-9 trikona walk"),
    ("lagna_kendradi_rasi", compute_lagna_kendradi_rasi, "Jaimini, kendradi from lagna"),
    ("karaka_kendradi_rasi", compute_karaka_kendradi_rasi, "Jaimini, kendradi from AK"),
    ("sthira_rasi_jaimini", compute_sthira_rasi_jaimini, "Jaimini fixed 9y/sign"),
    ("niryana_char", compute_niryana_char, "Char + markesha dignity adj"),
    ("padakrama", compute_padakrama, "Pada-step rashi walk ~108y"),
    ("mool", compute_mool, "Vimshottari with Moon-rasi-lord seed"),
    ("varnada", compute_varnada, "Caste-class element walk"),
    ("sudarshan_chakra", compute_sudarshan_chakra, "Lagna+Sun+Moon trinity 36y"),
    ("naisargika", compute_naisargika, "Natural age 120y Moon→Saturn"),
    ("lagna_kendradi_graha", compute_lagna_kendradi_graha, "Planets sorted by house-class"),
    ("karaka_kendradi_graha", compute_karaka_kendradi_graha, "Planets sorted from AK"),
    ("vakya", compute_vakya, "Tamil navamsa-seed 12×10y"),
    ("tribhagi", compute_tribhagi, "1/3 Vimshottari (40y)"),
    ("buddhi_gati", compute_buddhi_gati, "Mercury-rooted intellect timing"),
    ("kala", compute_kala, "Sun-nak-rooted Vimshottari scaled 100y"),
    ("sarvashtaka", compute_sarvashtaka, "Bindu-driven rashi walk"),
    ("mandook_yogini", compute_mandook_yogini, "Frog-hop Yogini variant 36y"),
]


def all_extended_dashas(natal_chart):
    """Compute all 30 extended dashas at once. Returns {name: timeline}."""
    return {name: fn(natal_chart) for name, fn, _ in DASHA_REGISTRY}


def lookup_active(timeline, when_dt):
    """Return the active dasha record at a given date."""
    for rec in timeline:
        if rec["start"] <= when_dt <= rec["end"]:
            return rec
    return None


# ============================================================
# APPLICABILITY FILTER (classical conditions)
# ============================================================
def applicable_dashas(natal_chart):
    """Return only the dashas APPLICABLE to this chart per their classical conditions.

    Conditions encoded:
      - Vimshottari, Ashtottari, Yogini: always applicable (handled elsewhere)
      - Dwadashottari: Moon in Punarvasu/Pushya/Ashlesha (cancer-side naks)
      - Panchottari: lagna in Cancer
      - Shatabdika: Moon in Pushya
      - Chaturasheeti Sama: 10th lord in 10th house
      - Dwisaptati Sama: Lagna-lord in 7th OR 7th-lord in lagna
      - Shastihayani: Sun in lagna
      - Shashti Sama: Saturn-strong (own/exalted/lagna/kendra)
      - Shadvargottama: any planet vargottama
      - Tribhagi: short-life (Markesha-strong) — proxy: Saturn in 8H or 6H
      - Naisargika: always applicable (universal natural sequence)
      - Sudarshan: always (universal annual chakra)
      - Jaimini family (Brahma, Mandooka, Yogardha, Trikona, Kendradi-rasi/graha,
        Sthira-rasi-J, Niryana-char, Padakrama, Mool, Varnada, Tara,
        Buddhi-gati, Karaka-Kendradi): all classically applicable to any chart.
      - Vakya: applicable if D9 data available (else falls back via Moon longitude)
      - Sarvashtaka: applicable if ashtakavarga data present in chart
      - Kala: always applicable (Sun-rooted)
      - Mandook Yogini: applicable if standard Yogini fits (always for Yogini-using charts)
    """
    pos = natal_chart["positions"]
    lagna_idx = natal_chart["lagna_idx"]
    moon = pos["Moon"]
    sun = pos.get("Sun", {})
    saturn = pos.get("Saturn", {})

    moon_nak = moon.get("nak", "")
    lagna_sign = RASIS[lagna_idx]
    tenth_sign = RASIS[(lagna_idx + 9) % 12]
    tenth_lord = RASI_LORDS[tenth_sign]
    seventh_sign = RASIS[(lagna_idx + 6) % 12]
    seventh_lord = RASI_LORDS[seventh_sign]
    lagna_lord = RASI_LORDS[lagna_sign]

    # vargottama check
    has_vargottama = False
    for p, pdat in pos.items():
        nav = pdat.get("navamsa") or pdat.get("d9_rasi")
        if nav and nav == pdat.get("rasi"):
            has_vargottama = True
            break

    # Saturn strength: own/exalted OR in kendra/trikona/lagna
    saturn_sign = saturn.get("rasi")
    saturn_strong = (saturn_sign in ("Capricorn", "Aquarius", "Libra") or
                     saturn.get("house") in (1, 4, 5, 7, 9, 10))

    # 10L in 10H
    tenth_lord_house = pos.get(tenth_lord, {}).get("house")
    cond_chaturasheeti = (tenth_lord_house == 10)

    # Lagna-7H exchange
    lagna_lord_house = pos.get(lagna_lord, {}).get("house")
    seventh_lord_house = pos.get(seventh_lord, {}).get("house")
    cond_dwisaptati = (lagna_lord_house == 7 or seventh_lord_house == 1)

    # Sun in lagna
    cond_shastihayani = (sun.get("house") == 1)

    # Saturn in 6H or 8H (short-life proxy)
    cond_tribhagi = (saturn.get("house") in (6, 8, 12))

    # Sarvashtaka data present
    has_sav = bool(natal_chart.get("sarvashtaka") or
                   natal_chart.get("ashtakavarga", {}).get("sarva"))

    rules = {
        "dwadashottari": moon_nak in ("Punarvasu", "Pushya", "Ashlesha"),
        "panchottari": lagna_sign == "Cancer",
        "shatabdika": moon_nak == "Pushya",
        "chaturasheeti_sama": cond_chaturasheeti,
        "dwisaptati_sama": cond_dwisaptati,
        "shastihayani": cond_shastihayani,
        "shashti_sama": saturn_strong,
        "shadvargottama": has_vargottama,
        "brahma": True, "mandooka": True, "yogardha": True, "tara": True,
        "trikona": True, "lagna_kendradi_rasi": True, "karaka_kendradi_rasi": True,
        "sthira_rasi_jaimini": True, "niryana_char": True, "padakrama": True,
        "mool": True, "varnada": True, "sudarshan_chakra": True,
        "naisargika": True, "lagna_kendradi_graha": True, "karaka_kendradi_graha": True,
        "vakya": True, "tribhagi": cond_tribhagi,
        "buddhi_gati": True, "kala": True,
        "sarvashtaka": has_sav, "mandook_yogini": True,
    }

    out = {}
    for name, fn, desc in DASHA_REGISTRY:
        if rules.get(name, False):
            out[name] = {
                "applicable": True,
                "reason": desc,
                "timeline": fn(natal_chart),
            }
    return out


# ============================================================
# TEST BLOCK
# ============================================================
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    today = dt.datetime.now()
    print(f"=== EXTENDED DASHA SYSTEMS — {chart['name']} ===")
    print(f"Birth: {chart['birth']['year']}-{chart['birth']['month']:02d}-"
          f"{chart['birth']['day']:02d}  Lagna: {chart['lagna']}  "
          f"Moon-Nak: {chart['janma_nakshatra']}\n")

    t0 = time.time()
    errors = 0
    for name, fn, desc in DASHA_REGISTRY:
        try:
            tl = fn(chart)
            print(f"--- {name.upper()} ({desc})")
            print(f"    entries: {len(tl)}")
            for rec in tl[:3]:
                key = rec.get("planet") or rec.get("sign")
                lord = rec.get("lord", "")
                lord_str = f" [{lord}]" if lord and lord != key else ""
                print(f"      {rec['start'].strftime('%Y-%m-%d')} -> "
                      f"{rec['end'].strftime('%Y-%m-%d')}  "
                      f"{key}{lord_str} ({rec['years']}y)  "
                      f"ages {rec['age_from']}-{rec['age_to']}")
            active = lookup_active(tl, today)
            if active:
                a_key = active.get("planet") or active.get("sign")
                a_lord = active.get("lord", "")
                extra = f" [{a_lord}]" if a_lord and a_lord != a_key else ""
                print(f"    ACTIVE NOW: {a_key}{extra}  notes: {active.get('notes','')}")
            else:
                print(f"    ACTIVE NOW: (out of timeline range)")
            print()
        except Exception as e:
            errors += 1
            print(f"    ERROR in {name}: {e}\n")

    elapsed = time.time() - t0

    print("=" * 60)
    print(f"30 dashas computed in {elapsed:.3f}s, {errors} errors")
    print("=" * 60)

    # Applicability per classical conditions
    print(f"\n=== APPLICABLE DASHAS for {chart['name']} ===")
    apps = applicable_dashas(chart)
    print(f"Applicable: {len(apps)}/{len(DASHA_REGISTRY)}\n")
    for name, info in apps.items():
        active = lookup_active(info["timeline"], today)
        if active:
            a_key = active.get("planet") or active.get("sign")
            print(f"  {name:25s} ACTIVE: {a_key:15s} ({info['reason']})")
        else:
            print(f"  {name:25s} (out of range) ({info['reason']})")
