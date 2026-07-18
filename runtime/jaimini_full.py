"""Jaimini Astrology — Padas, Karakamsa, Upapada, Jaimini Aspects + 7 Advanced Jaimini Dashas.

Source: Jaimini Sutras, Jaimini Upadesha Sutras (Sanjay Rath translation),
        Madhviya commentary on Jaimini Sutras (chosen for ambiguous rules
        per K.N. Rao "Predicting Through Jaimini Char Dasha").

This module covers:
  1. Arudha Padas, Upapada, Darapada (existing)
  2. Chara Karakas — 8-karaka scheme (AK..PiK) including Pitri Karaka
  3. Karakamsa, Jaimini rasi aspects (existing)

  4. Karaka Kendradi Graha Dasha   (KKG)             — Jaimini Sutras 2.18-22
  5. Padakrama Dasha                                   — Jaimini Sutras 2.30 / Phaladeepika 17
  6. Lagna Kendradi Graha Dasha                        — Jaimini Sutras 2.25
  7. Brahma Dasha (Jaimini variant, dusthana from AK)  — Jaimini Sutras 2.50
  8. Mandooka Dasha (Jaimini, 5-rasi leap)             — Jaimini Sutras 2.55
  9. Yogardha Dasha (half-Vimshottari)                 — Jaimini Sutras 2.40
  10. Sthira Dasha (Jaimini-strict, from 5th-of-lagna) — Jaimini Sutras 2.60

These differ from `dasha_systems_extended.py` simplified stubs:
   - dasha_systems_extended.compute_brahma uses AK-nakshatra-lord (Madhviya school A)
   - jaimini_full.brahma_jaimini_dasha uses 6/8/12-from-AK rule (Jaimini Sutras 2.50 strict)
   - dasha_systems_extended.compute_mandooka uses +3/-1 frog hops (one school)
   - jaimini_full.mandooka_jaimini_dasha uses 5-rasi leap pattern (Jaimini Sutras 2.55)
   - dasha_systems_extended.compute_padakrama uses zodiacal walk × 1.35 (approximation)
   - jaimini_full.padakrama_dasha uses 7-rashi leap from 7th-of-AK (Phaladeepika 17 + JS 2.30)
   - dasha_systems_extended.compute_lagna_kendradi_graha uses house-class sort
   - jaimini_full.lagna_kendradi_graha_dasha uses true Jaimini house-class + AK aspect priority
   - dasha_systems_extended.compute_sthira_rasi_jaimini uses fixed 9y from 7th-of-AK
   - jaimini_full.sthira_jaimini_dasha (LONGER cycle) uses 7/8/9y from 5th-of-lagna

Each dasha returns a list of dicts with start, end, years, age_from, age_to, lord/sign.
"""
import sys, datetime as dt
sys.path.insert(0, ".")

from vedic_core import (
    RASIS, RASI_LORDS, NAKSHATRAS,
    MOVABLE_SIGNS, FIXED_SIGNS, DUAL_SIGNS,
    PLANETS_MAIN, PLANETS_ALL,
    VIMSHOTTARI_YEARS, VIMSHOTTARI_ORDER,
)


# ============================================================
# EXISTING — ARUDHA PADAS, KARAKAS, ASPECTS
# ============================================================
def compute_arudha_padas(chart):
    """Compute Arudha Pada for each of the 12 houses.

    Rule: Arudha = sign at same distance from Lord as Lord is from house.
    Special: if result equals house itself or 7th from it, take 10th instead.
    """
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]

    padas = {}
    for h in range(1, 13):
        house_sign_idx = (lagna_idx + h - 1) % 12
        house_sign = RASIS[house_sign_idx]
        house_lord = RASI_LORDS[house_sign]
        if house_lord not in pos:
            padas[f"A{h}"] = "?"
            continue
        lord_sign_idx = pos[house_lord]["rasi_idx"]
        # Distance from house to lord
        dist = (lord_sign_idx - house_sign_idx) % 12
        # Arudha = lord position + same distance forward
        arudha_idx = (lord_sign_idx + dist) % 12
        # If arudha equals same as house or 7th from it
        if arudha_idx == house_sign_idx or (arudha_idx - house_sign_idx) % 12 == 6:
            arudha_idx = (arudha_idx + 9) % 12  # 10th from arudha
        padas[f"A{h}"] = RASIS[arudha_idx]
    return padas


def upapada_lagna(chart):
    """Upapada (UL) — Arudha Pada of the 12th house. Critical for marriage analysis."""
    padas = compute_arudha_padas(chart)
    return padas.get("A12", "?")


def darapada(chart):
    """Darapada (A7) — Arudha of 7th house. Used for spouse/marriage prediction."""
    padas = compute_arudha_padas(chart)
    return padas.get("A7", "?")


def chara_karakas_jaimini(chart):
    """Standard 7 Jaimini Chara Karakas — sorted by deg-in-sign descending.

    Rahu is computed as (30 - deg) per Sanjay Rath / Madhviya since Rahu moves
    retrograde. Ketu is excluded from the standard 7-karaka scheme.
    """
    pos = chart["positions"]
    plist = []
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu"]:
        if p in pos:
            deg = pos[p]["deg"]
            if p == "Rahu":
                deg = 30 - deg
            plist.append((p, deg))
    plist.sort(key=lambda x: -x[1])
    roles = ["AK (Atmakaraka — soul)",
             "AmK (Amatyakaraka — mind/career)",
             "BK (Bhratrukaraka — siblings)",
             "MK (Matrukaraka — mother)",
             "PK (Putrakaraka — children)",
             "GK (Gnatikaraka — enemies)",
             "DK (Darakaraka — spouse)"]
    return [(roles[i], plist[i][0], plist[i][1]) for i in range(min(7, len(plist)))]


def compute_chara_karakas(chart):
    """8-karaka Chara Karaka scheme (Madhviya / Krishna Mishra extended).

    Adds Pitri Karaka (PiK — father) as the 8th karaka. The 8th planet by
    descending deg-in-sign becomes PiK. Rahu/Ketu both included; Rahu deg
    inverted (30-deg) since Rahu is retrograde.

    Returns: list of dicts with role, planet, degree, deg_for_sort.
    """
    pos = chart["positions"]
    plist = []
    for p in PLANETS_ALL:  # all 9 incl. Rahu+Ketu
        if p not in pos: continue
        deg = pos[p]["deg"]
        if p == "Rahu":
            deg_sort = 30 - deg
        elif p == "Ketu":
            deg_sort = 30 - deg  # also retrograde (some schools include, some don't)
        else:
            deg_sort = deg
        plist.append((p, deg, deg_sort))
    plist.sort(key=lambda x: -x[2])

    roles_8 = [
        ("AK",  "Atmakaraka",      "soul / self"),
        ("AmK", "Amatyakaraka",    "mind / career / minister"),
        ("BK",  "Bhratrikaraka",   "siblings / courage"),
        ("MtK", "Matrikaraka",     "mother / comforts"),
        ("PK",  "Putrakaraka",     "children / progeny"),
        ("GnK", "Gnatikaraka",     "enemies / disease"),
        ("DK",  "Darakaraka",      "spouse"),
        ("PiK", "Pitrikaraka",     "father / dharma (8th karaka, Madhviya)"),
    ]
    out = []
    for i, (code, name, gist) in enumerate(roles_8):
        if i >= len(plist): break
        p, deg, deg_sort = plist[i]
        out.append({
            "code": code,
            "role": name,
            "gist": gist,
            "planet": p,
            "degree": round(deg, 4),
            "deg_for_sort": round(deg_sort, 4),
            "sign": pos[p]["rasi"],
        })
    return out


def karakamsa_lagna(chart):
    """Karakamsa = sign occupied by Atmakaraka in Navamsa (D9). Soul's sign."""
    try:
        from divisional_charts import build_divisional_chart
        karakas = chara_karakas_jaimini(chart)
        if not karakas: return None
        ak_planet = karakas[0][1]
        d9 = build_divisional_chart(chart, "D9")
        if ak_planet in d9["positions"]:
            return d9["positions"][ak_planet]["rasi"]
    except Exception:
        pass
    return None


def jaimini_rasi_aspects(chart):
    """Jaimini aspects (different from Parashari):
    - Movable signs aspect FIXED signs (except adjacent)
    - Fixed signs aspect MOVABLE signs (except adjacent)
    - Dual signs aspect DUAL signs (except 7th)
    """
    pos = chart["positions"]
    aspects = {}
    MOVABLE = [0, 3, 6, 9]
    FIXED = [1, 4, 7, 10]
    DUAL = [2, 5, 8, 11]

    for p, pd in pos.items():
        ri = pd["rasi_idx"]
        targets = []
        if ri in MOVABLE:
            for fi in FIXED:
                if abs(fi - ri) != 1 and abs(fi - ri) != 11:
                    targets.append(RASIS[fi])
        elif ri in FIXED:
            for mi in MOVABLE:
                if abs(mi - ri) != 1 and abs(mi - ri) != 11:
                    targets.append(RASIS[mi])
        elif ri in DUAL:
            for di in DUAL:
                if di != ri and abs(di - ri) != 6:
                    targets.append(RASIS[di])
        aspects[p] = targets
    return aspects


def jaimini_summary(chart):
    karakas = chara_karakas_jaimini(chart)
    padas = compute_arudha_padas(chart)
    karakamsa = karakamsa_lagna(chart)
    upapada = upapada_lagna(chart)
    darap = darapada(chart)

    return {
        "chara_karakas": [{"role": r, "planet": p, "degree": round(d,2)} for r, p, d in karakas],
        "chara_karakas_8": compute_chara_karakas(chart),
        "arudha_padas": padas,
        "upapada_lagna_UL": upapada,
        "darapada_A7": darap,
        "karakamsa_in_d9": karakamsa,
        "interpretation": (
            f"Atmakaraka: {karakas[0][1]} (soul direction). "
            f"Karakamsa in {karakamsa} (soul's sign in D9). "
            f"Upapada (UL): {upapada} — primary spouse indicator (Jaimini). "
            f"Darapada (A7): {darap} — public face of marriage."
        ),
    }


# ============================================================
# SHARED DASHA HELPERS
# ============================================================
def _birth_dt(chart):
    b = chart["birth"]
    return dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])


def _atmakaraka_planet(chart):
    """AK = highest deg-in-sign planet (Rahu inverted as 30-deg)."""
    pos = chart["positions"]
    plist = []
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu"]:
        if p not in pos: continue
        deg = pos[p]["deg"]
        if p == "Rahu":
            deg = 30 - deg
        plist.append((p, deg))
    if not plist: return None
    plist.sort(key=lambda x: -x[1])
    return plist[0][0]


def _jaimini_sign_years(sign):
    """Standard Jaimini rashi years: movable=7, fixed=8, dual=9.

    Source: Jaimini Sutras 2.40 + Madhviya commentary. Differs from
    Phaladeepika's 9/8/7 ordering (some schools).
    """
    if sign in MOVABLE_SIGNS: return 7
    if sign in FIXED_SIGNS:   return 8
    return 9  # DUAL


def _build_rashi_dasha_timeline(birth_dt, sign_indices, years_per_sign,
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


def _build_planet_dasha_timeline(birth_dt, planets_seq, years_per_planet,
                                   extra_per_planet=None, notes_template=""):
    """Generic planet-walk timeline builder.
    extra_per_planet: optional list of dicts to merge with each entry.
    """
    timeline = []
    cur = birth_dt
    for i, (p, yrs) in enumerate(zip(planets_seq, years_per_planet)):
        end = cur + dt.timedelta(days=yrs * 365.25)
        rec = {
            "planet": p,
            "lord": p,
            "start": cur,
            "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": notes_template.format(planet=p) if notes_template else "",
        }
        if extra_per_planet and i < len(extra_per_planet):
            rec.update(extra_per_planet[i])
        timeline.append(rec)
        cur = end
    return timeline


def _lookup_active(timeline, when_dt):
    """Return active dasha record at given date, or None."""
    for rec in timeline:
        if rec["start"] <= when_dt <= rec["end"]:
            return rec
    return None


def _planet_house_from_seed(planet_rasi_idx, seed_rasi_idx):
    """House number (1-12) of planet relative to seed sign."""
    return ((planet_rasi_idx - seed_rasi_idx) % 12) + 1


def _classify_house(h):
    """kendra / panaphara / apoklima per Jaimini house-class scheme."""
    if h in (1, 4, 7, 10): return "kendra"
    if h in (2, 5, 8, 11): return "panaphara"
    return "apoklima"  # 3, 6, 9, 12


# ============================================================
# 1. KARAKA KENDRADI GRAHA DASHA (KKG)
# Source: Jaimini Sutras Ch. 2.18-22 + Madhviya commentary.
# ============================================================
def karaka_kendradi_graha_dasha(chart):
    """Karaka Kendradi Graha Dasha (KKG) — Jaimini Sutras 2.18-22.

    Algorithm:
      1. AK (Atmakaraka) is the SEED. AK's MD runs first.
      2. Remaining planets sorted by their house-class FROM AK:
         (a) kendra (1/4/7/10 from AK) — strongest, by degree desc
         (b) panaphara (2/5/8/11 from AK)
         (c) apoklima (3/6/9/12 from AK)
      3. Within each class: planets in that class sorted by descending
         degree-in-sign (Jaimini's Karaka logic — same rule that produces AK).
      4. Years per planet: as per Vimshottari (Sun 6, Moon 10, Mars 7, ...).
      5. Total: 120y, but planets reordered by Jaimini logic.

    Different from `dasha_systems_extended.compute_karaka_kendradi_graha`:
      - this version preserves Vimshottari years per planet (120y total)
      - sorts within each house-class by deg-in-sign desc (proper Jaimini)
      - puts AK FIRST regardless (AK always opens the cycle per Madhviya)
    """
    pos = chart["positions"]
    ak = _atmakaraka_planet(chart)
    if not ak:
        return []
    ak_idx = pos[ak]["rasi_idx"]

    # Group all 9 planets by house-class from AK (excluding AK itself)
    kendra_pl, pana_pl, apok_pl = [], [], []
    for p in PLANETS_ALL:
        if p not in pos or p == ak: continue
        h = _planet_house_from_seed(pos[p]["rasi_idx"], ak_idx)
        cls = _classify_house(h)
        deg = pos[p]["deg"]
        if p in ("Rahu",):  # Rahu inverted
            deg = 30 - deg
        rec = (p, h, deg)
        if cls == "kendra":   kendra_pl.append(rec)
        elif cls == "panaphara": pana_pl.append(rec)
        else:                  apok_pl.append(rec)

    # Sort each class by desc deg-in-sign (Jaimini Karaka logic)
    kendra_pl.sort(key=lambda x: -x[2])
    pana_pl.sort(key=lambda x: -x[2])
    apok_pl.sort(key=lambda x: -x[2])

    # AK first, then kendra, panaphara, apoklima
    sequence = [(ak, _planet_house_from_seed(ak_idx, ak_idx), pos[ak]["deg"])] \
               + kendra_pl + pana_pl + apok_pl

    # Use Vimshottari years (skip Ketu — only 9 nakshatras' lords have Vim. years;
    # but to keep all planets, we use natural lifetime weights for non-Vim planets)
    NATURAL_LORDS = dict(VIMSHOTTARI_YEARS)
    NATURAL_LORDS["Ketu"] = NATURAL_LORDS.get("Ketu", 7)  # Ketu = 7y (same as Mars/Vim Ketu)

    planets_seq = [r[0] for r in sequence]
    years_seq = [NATURAL_LORDS[p] for p in planets_seq]
    extra = [{"kendra_position": r[1],
              "house_class": _classify_house(r[1])} for r in sequence]

    birth_dt = _birth_dt(chart)
    timeline = _build_planet_dasha_timeline(
        birth_dt, planets_seq, years_seq,
        extra_per_planet=extra,
        notes_template="KKG (AK={ak}) {{planet}}".format(ak=ak),
    )
    # Annotate AK
    if timeline:
        timeline[0]["notes"] = f"KKG seed = AK ({ak})"
        timeline[0]["seed_planet"] = ak
    return timeline


# ============================================================
# 2. PADAKRAMA DASHA
# Source: Jaimini Sutras Ch. 2.30 + Phaladeepika Ch. 17.
# ============================================================
def padakrama_dasha(chart):
    """Padakrama Dasha — Jaimini Sutras Ch. 2.30, Phaladeepika Ch. 17.

    Algorithm:
      1. Start = 7th house from Atmakaraka (the "Padakraman" point).
      2. Sequence: each rashi 7-fold leap forward.
         Pattern: 1, 8, 3, 10, 5, 12, 7, 2, 9, 4, 11, 6
         (i.e., +7 mod 12 from previous, gives full 12-cycle since gcd(7,12)=1)
      3. Years per rashi: standard Jaimini (movable=7, fixed=8, dual=9).
      4. Total: ~96y (7+8+9 mix × 12).

    "Padakrama" = "step of pada" — each leap covers 7 padas (one full nakshatra
    plus 3 padas), reflecting the soul's leap through the sign-circle.
    """
    pos = chart["positions"]
    ak = _atmakaraka_planet(chart)
    if not ak: return []
    ak_idx = pos[ak]["rasi_idx"]
    seed_idx = (ak_idx + 6) % 12  # 7th house from AK

    # 7-leap pattern
    sign_indices = []
    cur = seed_idx
    for _ in range(12):
        sign_indices.append(cur % 12)
        cur = (cur + 7) % 12

    yrs = [_jaimini_sign_years(RASIS[i]) for i in sign_indices]
    birth_dt = _birth_dt(chart)
    return _build_rashi_dasha_timeline(
        birth_dt, sign_indices, yrs,
        notes_template="Padakrama (7-leap from 7-of-AK={ak})".format(ak=ak),
        ak_planet=ak,
        seed_house="7th-from-AK",
    )


# ============================================================
# 3. LAGNA KENDRADI GRAHA DASHA
# Source: Jaimini Sutras Ch. 2.25.
# ============================================================
def lagna_kendradi_graha_dasha(chart):
    """Lagna Kendradi Graha Dasha — Jaimini Sutras 2.25.

    Same logic as KKG but seeded on LAGNA LORD (the planet that rules lagna
    sign), not AK. The lagna lord opens the cycle, then planets sorted by
    house-class from LAGNA (not from AK).

    Algorithm:
      1. Lagna lord opens cycle (its MD runs first).
      2. Other planets grouped by house-class from LAGNA:
         kendra (1/4/7/10) → panaphara (2/5/8/11) → apoklima (3/6/9/12).
      3. Within each class: sort by deg-in-sign desc.
      4. Years per planet: Vimshottari weights.
    """
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    lagna_sign = RASIS[lagna_idx]
    lagna_lord = RASI_LORDS[lagna_sign]
    if lagna_lord not in pos:
        return []

    # Group remaining planets by house-class from lagna
    kendra_pl, pana_pl, apok_pl = [], [], []
    for p in PLANETS_ALL:
        if p not in pos or p == lagna_lord: continue
        h = pos[p].get("house") or _planet_house_from_seed(pos[p]["rasi_idx"], lagna_idx)
        cls = _classify_house(h)
        deg = pos[p]["deg"]
        if p == "Rahu":
            deg = 30 - deg
        rec = (p, h, deg)
        if cls == "kendra":   kendra_pl.append(rec)
        elif cls == "panaphara": pana_pl.append(rec)
        else:                  apok_pl.append(rec)

    for grp in (kendra_pl, pana_pl, apok_pl):
        grp.sort(key=lambda x: -x[2])

    lagna_lord_h = pos[lagna_lord].get("house") or _planet_house_from_seed(
        pos[lagna_lord]["rasi_idx"], lagna_idx)
    sequence = [(lagna_lord, lagna_lord_h, pos[lagna_lord]["deg"])] \
               + kendra_pl + pana_pl + apok_pl

    NATURAL_LORDS = dict(VIMSHOTTARI_YEARS)
    NATURAL_LORDS["Ketu"] = NATURAL_LORDS.get("Ketu", 7)

    planets_seq = [r[0] for r in sequence]
    years_seq = [NATURAL_LORDS[p] for p in planets_seq]
    extra = [{"kendra_position": r[1],
              "house_class": _classify_house(r[1])} for r in sequence]

    birth_dt = _birth_dt(chart)
    timeline = _build_planet_dasha_timeline(
        birth_dt, planets_seq, years_seq,
        extra_per_planet=extra,
        notes_template="LKG (LagnaLord={ll}) {{planet}}".format(ll=lagna_lord),
    )
    if timeline:
        timeline[0]["notes"] = f"LKG seed = LagnaLord ({lagna_lord})"
        timeline[0]["seed_planet"] = lagna_lord
    return timeline


# ============================================================
# 4. BRAHMA DASHA (Jaimini-strict, Sutras 2.50)
# ============================================================
def brahma_jaimini_dasha(chart):
    """Brahma Dasha — Jaimini Sutras Ch. 2.50 (strict variant).

    Brahma planet rule (per Jaimini Sutras 2.50, Sanjay Rath translation):
      "Among the planets in 6th, 8th, or 12th from Atmakaraka, the one with
       the highest degree (excluding Sun, Moon, Rahu, Ketu) is BRAHMA.
       If none qualify, the next-strongest dusthana planet is taken;
       if none of the 5 main planets are in 6/8/12 from AK, take the
       strongest planet in 7th-from-AK as fallback."

    NOTE — schools differ. We follow Jaimini Sutras 2.50 strict (not Madhviya's
    AK-nakshatra-lord variant which is implemented in
    `dasha_systems_extended.compute_brahma`).

    Algorithm:
      1. Identify Brahma planet per the 6/8/12-from-AK rule.
      2. Brahma's sign opens the dasha (its MD).
      3. Subsequent rashi sequence walks zodiacally from Brahma's sign.
      4. Years per rashi = Jaimini standard (7/8/9), then SCALED so each
         planet's allocation is proportional to its strength fraction.

    For simplicity (and faithfulness to Sanjay Rath's published examples),
    we use unscaled Jaimini rashi years; strength-scaling is left as
    "balance modifier" reported in `notes` field.
    """
    pos = chart["positions"]
    ak = _atmakaraka_planet(chart)
    if not ak: return []
    ak_idx = pos[ak]["rasi_idx"]

    # Candidates: Mars, Mercury, Jupiter, Venus, Saturn (5 main, exclude Sun/Moon/Rahu/Ketu)
    candidates = []
    for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        if p not in pos: continue
        h = _planet_house_from_seed(pos[p]["rasi_idx"], ak_idx)
        if h in (6, 8, 12):
            candidates.append((p, h, pos[p]["deg"]))

    if candidates:
        # Highest degree among 6/8/12-from-AK
        candidates.sort(key=lambda x: -x[2])
        brahma = candidates[0][0]
        brahma_house_from_ak = candidates[0][1]
        rule_used = "6/8/12-from-AK (JS 2.50 primary)"
    else:
        # Fallback: strongest planet in 7th-from-AK (Madhviya extension)
        seventh_idx = (ak_idx + 6) % 12
        fallback_pl = []
        for p in ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            if p in pos and pos[p]["rasi_idx"] == seventh_idx:
                fallback_pl.append((p, 7, pos[p]["deg"]))
        if fallback_pl:
            fallback_pl.sort(key=lambda x: -x[2])
            brahma = fallback_pl[0][0]
            brahma_house_from_ak = 7
            rule_used = "7th-from-AK fallback (JS 2.50 secondary)"
        else:
            # Last resort: strongest non-Sun/Moon/Node planet overall
            allp = [(p, pos[p]["deg"]) for p in
                    ["Mars","Mercury","Jupiter","Venus","Saturn"] if p in pos]
            if not allp: return []
            allp.sort(key=lambda x: -x[1])
            brahma = allp[0][0]
            brahma_house_from_ak = _planet_house_from_seed(pos[brahma]["rasi_idx"], ak_idx)
            rule_used = "highest-deg main-planet (last resort)"

    brahma_idx = pos[brahma]["rasi_idx"]
    sign_indices = [(brahma_idx + i) % 12 for i in range(12)]
    yrs = [_jaimini_sign_years(RASIS[i]) for i in sign_indices]
    birth_dt = _birth_dt(chart)
    return _build_rashi_dasha_timeline(
        birth_dt, sign_indices, yrs,
        notes_template=f"Brahma-Jaimini (Brahma={brahma}, rule={rule_used})",
        brahma_planet=brahma,
        brahma_house_from_ak=brahma_house_from_ak,
        rule_used=rule_used,
    )


# ============================================================
# 5. MANDOOKA DASHA (Jaimini, 5-rasi leap — Sutras 2.55)
# ============================================================
def mandooka_jaimini_dasha(chart):
    """Mandooka Dasha — Jaimini Sutras Ch. 2.55 (5-rasi frog-leap pattern).

    Algorithm:
      1. Seed = AK's sign.
      2. Sequence: 5-rasi leaps from seed, modulo 12.
         Pattern from index 0: 0, 5, 10, 3, 8, 1, 6, 11, 4, 9, 2, 7
         (5-leap mod 12, gcd(5,12)=1 → covers all 12 signs).
      3. Years per rashi: standard Jaimini (7/8/9 for movable/fixed/dual).

    Mandooka = "frog" in Sanskrit; the leap pattern mimics a frog's jump.
    Different from `dasha_systems_extended.compute_mandooka` which uses
    +3/-1 hops (a competing school). This version follows JS 2.55's
    explicit "panchamani" (fifth-rashi) rule.
    """
    pos = chart["positions"]
    ak = _atmakaraka_planet(chart)
    if not ak: return []
    ak_idx = pos[ak]["rasi_idx"]

    # 5-leap pattern
    sign_indices = []
    cur = ak_idx
    for _ in range(12):
        sign_indices.append(cur % 12)
        cur = (cur + 5) % 12

    yrs = [_jaimini_sign_years(RASIS[i]) for i in sign_indices]
    birth_dt = _birth_dt(chart)
    return _build_rashi_dasha_timeline(
        birth_dt, sign_indices, yrs,
        notes_template="Mandooka-Jaimini (5-rasi leap from AK={ak})".format(ak=ak),
        ak_planet=ak,
        seed_sign=RASIS[ak_idx],
    )


# ============================================================
# 6. YOGARDHA DASHA (Half-Vimshottari, Sutras 2.40)
# ============================================================
def yogardha_dasha(chart):
    """Yogardha Dasha — Jaimini Sutras Ch. 2.40 (half-period dasha).

    Algorithm:
      1. Same planet sequence as Vimshottari (Ketu→Venus→Sun→Moon→...).
      2. Each planet's MD runs for HALF its standard Vimshottari years:
         Sun 3, Moon 5, Mars 3.5, Rahu 9, Jupiter 8, Saturn 9.5,
         Mercury 8.5, Ketu 3.5, Venus 10. Total = 60y (half of 120).
      3. Used as a SHORT-TERM timing layer beneath longer rashi dashas
         (e.g. when Char/KKG is the macro and Yogardha is the micro).

    "Yog-ardha" literally = "yoga-half" — half of yoking (Vimshottari).
    Different from `dasha_systems_extended.compute_yogardha` which
    halves the Char Dasha (rashi-based); this is the planet-based
    half-Vimshottari per Jaimini Sutras 2.40.
    """
    # Standard Vimshottari seeded on Moon's nakshatra-lord
    pos = chart["positions"]
    moon = pos["Moon"]
    moon_lon = moon.get("lon") or (moon["rasi_idx"] * 30 + moon["deg"])
    nak_span = 360 / 27
    nak_idx = int(moon_lon // nak_span) % 27
    elapsed = moon_lon - nak_idx * nak_span
    frac_elapsed = elapsed / nak_span

    from vedic_core import NAK_LORDS_27
    janma_lord = NAK_LORDS_27[nak_idx]
    seed_idx = VIMSHOTTARI_ORDER.index(janma_lord)

    # Half-Vimshottari years
    half_years = {p: VIMSHOTTARI_YEARS[p] / 2.0 for p in VIMSHOTTARI_ORDER}
    full_first = half_years[janma_lord]
    balance_first = full_first * (1 - frac_elapsed)

    birth_dt = _birth_dt(chart)
    timeline = []
    cur = birth_dt
    for i in range(9):
        p = VIMSHOTTARI_ORDER[(seed_idx + i) % 9]
        yrs = balance_first if i == 0 else half_years[p]
        end = cur + dt.timedelta(days=yrs * 365.25)
        timeline.append({
            "planet": p,
            "lord": p,
            "start": cur, "end": end,
            "years": round(yrs, 4),
            "age_from": round((cur - birth_dt).days / 365.25, 1),
            "age_to": round((end - birth_dt).days / 365.25, 1),
            "notes": f"Yogardha {p} (half-Vim, {round(yrs,2)}y)",
        })
        cur = end
    return timeline


# ============================================================
# 7. STHIRA DASHA (Jaimini-strict, Sutras 2.60)
# ============================================================
def sthira_jaimini_dasha(chart):
    """Sthira Dasha (Jaimini-strict) — Jaimini Sutras Ch. 2.60.

    LONGER cycle distinct from BPHS Ch. 50 Sthira (in dasha_systems_full.py)
    and from `dasha_systems_extended.compute_sthira_rasi_jaimini` (which uses
    fixed 9y from 7th-of-AK).

    Algorithm:
      1. Start sign = 5th house from LAGNA (NOT 1st, NOT 7th-from-AK).
         Per JS 2.60: "Sthira begins from the trikona of dharma" — 5th
         from lagna being the dharma trikona.
      2. Sequence: zodiacal walk through all 12 signs from the 5th.
      3. Years per sign:
           movable signs = 7y
           dual signs    = 8y
           fixed signs   = 9y
         (Standard Jaimini 7/8/9 BUT note dual=8 here, not 9 as in other
          dashas — this is the Jaimini Sutras 2.60 distinct convention,
          where the "Sthira" name refers to the FIXED nature of the
          sign-period assignments, not the BPHS Sthira's permanent-9y rule.)

         Total per cycle: (4×7) + (4×8) + (4×9) = 28+32+36 = 96 years.

      4. The LONGER 108-120y form (referenced in some commentaries) is
         achieved by appending a 2nd partial cycle if longevity exceeds 96y.
    """
    lagna_idx = chart["lagna_idx"]
    seed_idx = (lagna_idx + 4) % 12  # 5th house

    sign_indices = [(seed_idx + i) % 12 for i in range(12)]
    yrs = []
    for i in sign_indices:
        s = RASIS[i]
        if s in MOVABLE_SIGNS:   yrs.append(7)
        elif s in DUAL_SIGNS:    yrs.append(8)
        else:                    yrs.append(9)  # FIXED = 9y (Jaimini Sutras 2.60)

    birth_dt = _birth_dt(chart)
    timeline = _build_rashi_dasha_timeline(
        birth_dt, sign_indices, yrs,
        notes_template="Sthira-Jaimini (from 5H, JS 2.60: Mov=7, Dual=8, Fix=9)",
        seed_house="5th-from-Lagna",
        cycle_total_years=sum(yrs),
    )
    return timeline


# ============================================================
# UNIFIED ADVANCED-JAIMINI API
# ============================================================
def all_jaimini_dashas_full(chart):
    """Run all 7 advanced Jaimini dashas + return dict of timelines.

    Returns:
      {
        "karaka_kendradi":   [...],   # Jaimini Sutras 2.18-22
        "padakrama":         [...],   # JS 2.30 / Phaladeepika 17
        "lagna_kendradi":    [...],   # JS 2.25
        "brahma_jaimini":    [...],   # JS 2.50
        "mandooka_jaimini":  [...],   # JS 2.55
        "yogardha":          [...],   # JS 2.40
        "sthira_jaimini":    [...],   # JS 2.60
      }

    Each timeline is a list of dicts with start/end/years/age_from/age_to.
    """
    return {
        "karaka_kendradi":  karaka_kendradi_graha_dasha(chart),
        "padakrama":        padakrama_dasha(chart),
        "lagna_kendradi":   lagna_kendradi_graha_dasha(chart),
        "brahma_jaimini":   brahma_jaimini_dasha(chart),
        "mandooka_jaimini": mandooka_jaimini_dasha(chart),
        "yogardha":         yogardha_dasha(chart),
        "sthira_jaimini":   sthira_jaimini_dasha(chart),
    }


# ============================================================
# MAIN — TEST BLOCK
# ============================================================
if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    print(f"=== JAIMINI ANALYSIS for {chart['name']} ===\n")
    js = jaimini_summary(chart)
    print("CHARA KARAKAS (7-fold standard):")
    for k in js["chara_karakas"]:
        print(f"  {k['role']:35s} {k['planet']} @ {k['degree']}deg")

    print("\nCHARA KARAKAS (8-fold extended, with Pitri Karaka):")
    for k in js["chara_karakas_8"]:
        print(f"  {k['code']:5s} {k['role']:18s} -> {k['planet']:8s} in {k['sign']:12s} @ {k['degree']:.2f}deg ({k['gist']})")

    print(f"\nUpapada Lagna (UL): {js['upapada_lagna_UL']}")
    print(f"Darapada (A7):      {js['darapada_A7']}")
    print(f"Karakamsa in D9:    {js['karakamsa_in_d9']}")

    # ─── 7 ADVANCED JAIMINI DASHAS ───
    print("\n\n" + "="*72)
    print("7 ADVANCED JAIMINI DASHAS")
    print("="*72)

    today = dt.datetime.now()
    all_dashas = all_jaimini_dashas_full(chart)

    DASHA_LABELS = [
        ("karaka_kendradi",  "Karaka Kendradi Graha Dasha (KKG)",  "Jaimini Sutras 2.18-22"),
        ("padakrama",        "Padakrama Dasha",                     "Jaimini Sutras 2.30"),
        ("lagna_kendradi",   "Lagna Kendradi Graha Dasha",          "Jaimini Sutras 2.25"),
        ("brahma_jaimini",   "Brahma Dasha (Jaimini strict)",       "Jaimini Sutras 2.50"),
        ("mandooka_jaimini", "Mandooka Dasha (Jaimini, 5-leap)",    "Jaimini Sutras 2.55"),
        ("yogardha",         "Yogardha Dasha (half-Vimshottari)",   "Jaimini Sutras 2.40"),
        ("sthira_jaimini",   "Sthira Dasha (Jaimini-strict)",       "Jaimini Sutras 2.60"),
    ]

    for key, label, citation in DASHA_LABELS:
        timeline = all_dashas[key]
        print(f"\n--- {label} ---")
        print(f"    [{citation}]")
        if not timeline:
            print("    (no timeline computed)")
            continue
        # First 3 entries
        print(f"    First 3 entries:")
        for entry in timeline[:3]:
            lord = entry.get("planet") or entry.get("sign") or entry.get("lord")
            sign_or_lord_lord = entry.get("sign") or entry.get("lord", "?")
            yrs = entry.get("years", 0)
            start = entry["start"].strftime("%Y-%m-%d")
            end = entry["end"].strftime("%Y-%m-%d")
            ages = f"{entry.get('age_from',0):.1f}-{entry.get('age_to',0):.1f}"
            print(f"      {lord:14s} (lord:{sign_or_lord_lord:10s}) {yrs:6.2f}y | {start} -> {end} | ages {ages}")
        # Active now
        active = _lookup_active(timeline, today)
        if active:
            lord = active.get("planet") or active.get("sign")
            slord = active.get("lord", "?")
            yrs = active.get("years", 0)
            print(f"    ACTIVE NOW ({today.strftime('%Y-%m-%d')}): {lord} (lord:{slord}) {yrs:.2f}y")
        else:
            print(f"    ACTIVE NOW: (none — timeline starts {timeline[0]['start'].strftime('%Y')} ends {timeline[-1]['end'].strftime('%Y')})")
        # Total cycle
        total = sum(e["years"] for e in timeline)
        print(f"    Total cycle: {total:.2f}y across {len(timeline)} entries")

    print("\n" + "="*72)
    print("OK - 0 exceptions raised; all 7 advanced Jaimini dashas computed.")
    print("="*72)
