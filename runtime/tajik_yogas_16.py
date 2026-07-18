"""Tajik Yogas (16 Itthasala-family + balas) — Tajik / Persian astrology system.

Source: Tajika Neelakanthi (Neelakantha Daivajna), Varshaphal Raman, Tajik Adawal.
Tajik aspect-orb system DIFFERS from Parashari:
  - Conjunction: 12° orb (sambandha)
  - Opposition (180°): 12° (asthama)
  - Trine (120°): 9°
  - Square (90°): 7°
  - Sextile (60°): 6°
Both planets must be within combined orb of half-each side, applying or separating.

16 Tajik Yogas (Persian "Itthashala" = receiving, "Iisarafa" = separating):
  1.  Ittasala       — applying aspect, fast→slow planet, near-exact
  2.  Iisarafa       — separating aspect (just past exact)
  3.  Manaucha       — exalted planet receives an aspect (special boost)
  4.  Yamaya         — twin planets in sambandha
  5.  Mosthasala     — perfect aspect via mutual reception
  6.  Kambula        — applying aspect with malefic in 4th-house-from
  7.  Khallasar      — applying aspect, but separated by ill-placed planet
  8.  Radd           — refusal/refused aspect (one applying, other separating)
  9.  Naktha         — interrupted aspect via intervening planet
  10. Indu-Yamaya    — Moon's twin-aspect, special romantic/wealth combination
  11. Madabihaza     — slow-to-slow planets in mutual aspect
  12. Ittahad        — friendship aspect (benefic-to-benefic)
  13. Mossatail      — both planets equidistant from 3rd point (combined-yoga)
  14. Naktha-i-Yamaya — "interruption-twin" (rare special)
  15. Tambeer-i-Surah — "frame of the picture" — all aspects culminating
  16. Qutha-i-Nur    — "lamp of light" — chart-defining benefic-to-benefic culmination

Tajik Balas (5 strengths used in Varshaphala):
  - Hadda Bala (terms / decanate-finer)
  - Trirashi Bala (3-sign group strength)
  - Drekkana Bala (decanate strength)
  - Navamsha Bala (D9 dignity-back-projection)
  - Mooladhipati Bala (root-lord strength)
"""
import sys
sys.path.insert(0, ".")
from vedic_core import (
    RASIS, RASI_LORDS, DIGNITIES, NATURAL_BENEFICS, NATURAL_MALEFICS,
    MOVABLE_SIGNS, FIXED_SIGNS, DUAL_SIGNS, EXALTATION_SIGNS, DEBILITATION_SIGNS,
)

# ============================================================
# TAJIK ASPECT ORBS (degrees)
# ============================================================
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

TAJIK_ASPECT_ANGLES = {
    "conjunction": 0,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "opposition": 180,
}

# Planet relative speeds (mean daily motion in degrees) — used to determine fast/slow
PLANET_SPEED = {
    "Moon": 13.18, "Mercury": 1.38, "Venus": 1.20, "Sun": 0.99,
    "Mars": 0.52, "Jupiter": 0.083, "Saturn": 0.034,
    "Rahu": 0.053, "Ketu": 0.053,
}


def _planet_lon(chart, p):
    """Get absolute longitude of planet (rasi_idx*30 + deg)."""
    pos = chart["positions"]
    if p not in pos: return None
    pd = pos[p]
    return pd.get("lon_abs") or pd.get("lon") or (pd["rasi_idx"] * 30 + pd["deg"])


def _angle_between(lon1, lon2):
    """Shortest angular separation (0-180°)."""
    d = abs(lon1 - lon2) % 360
    return min(d, 360 - d)


def _aspect_type(lon1, lon2):
    """Detect Tajik aspect type + orb between two longitudes.
    Returns (aspect_type, orb, exact_diff) or (None, None, None)."""
    sep = _angle_between(lon1, lon2)
    for aspect, target in TAJIK_ASPECT_ANGLES.items():
        diff = abs(sep - target)
        # For 0° (conj): sep is the diff itself; for 180° (opp), target is 180.
        if diff <= TAJIK_ORBS[aspect]:
            return aspect, TAJIK_ORBS[aspect], diff
    return None, None, None


def _is_applying(p1, p2, lon1, lon2):
    """Determine if aspect is APPLYING (faster planet behind slower) or SEPARATING.
    Tajik rule: applying = faster planet has not yet caught up to exact aspect angle.
    """
    s1 = PLANET_SPEED.get(p1, 1.0)
    s2 = PLANET_SPEED.get(p2, 1.0)
    fast = p1 if s1 > s2 else p2
    slow = p2 if s1 > s2 else p1
    fast_lon = lon1 if fast == p1 else lon2
    slow_lon = lon2 if fast == p1 else lon1
    # For zodiacal motion, applying means faster behind (zodiacally later)
    # Simplified: if fast is "behind" slow in zodiac → applying
    rel = (fast_lon - slow_lon) % 360
    return rel > 180  # fast is approaching from behind


# ============================================================
# 16 TAJIK YOGAS — predicate functions
# ============================================================
def _yoga(name, ytype, severity, planets, interp, **kw):
    return {"name": name, "type": ytype, "severity": severity,
            "planets": planets, "interpretation": interp, **kw}


def y_ittasala(chart):
    """Applying aspect between two planets, fast→slow."""
    out = []
    pos = chart["positions"]
    pl = list(pos.keys())
    seen = set()
    for i, p1 in enumerate(pl):
        for p2 in pl[i+1:]:
            if p1 in ("Rahu","Ketu") or p2 in ("Rahu","Ketu"): continue
            l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
            if l1 is None or l2 is None: continue
            aspect, orb, diff = _aspect_type(l1, l2)
            if aspect is None: continue
            if not _is_applying(p1, p2, l1, l2): continue
            key = tuple(sorted([p1, p2]))
            if key in seen: continue
            seen.add(key)
            out.append(_yoga(
                "Ittasala Yoga", "auspicious_applying", 4,
                [p1, p2],
                f"Applying {aspect} between {p1} and {p2} (orb {diff:.1f}°). The planets are reaching each other — events tied to their significations are about to unfold favorably during the year.",
                aspect=aspect, orb_used=orb, exact_diff=round(diff,2),
            ))
    return out


def y_iisarafa(chart):
    """Separating aspect — just past exactness."""
    out = []
    pos = chart["positions"]
    pl = list(pos.keys())
    seen = set()
    for i, p1 in enumerate(pl):
        for p2 in pl[i+1:]:
            if p1 in ("Rahu","Ketu") or p2 in ("Rahu","Ketu"): continue
            l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
            if l1 is None or l2 is None: continue
            aspect, orb, diff = _aspect_type(l1, l2)
            if aspect is None: continue
            if _is_applying(p1, p2, l1, l2): continue
            key = tuple(sorted([p1, p2]))
            if key in seen: continue
            seen.add(key)
            out.append(_yoga(
                "Iisarafa Yoga", "fading_separating", 2,
                [p1, p2],
                f"Separating {aspect} between {p1} and {p2}. The aspect's intensity is waning — themes of this combination are concluding rather than starting.",
                aspect=aspect, orb_used=orb, exact_diff=round(diff,2),
            ))
    return out


def y_manaucha(chart):
    """Exalted planet receives any Tajik aspect — power-boost."""
    out = []
    pos = chart["positions"]
    for p1, exalt_sign in EXALTATION_SIGNS.items():
        if p1 not in pos: continue
        if pos[p1]["rasi"] != exalt_sign: continue
        l1 = _planet_lon(chart, p1)
        for p2, _ in pos.items():
            if p2 == p1 or p2 in ("Rahu","Ketu"): continue
            l2 = _planet_lon(chart, p2)
            if l2 is None: continue
            aspect, orb, diff = _aspect_type(l1, l2)
            if aspect is None: continue
            out.append(_yoga(
                "Manaucha Yoga", "auspicious_exalt_boost", 5,
                [p1, p2],
                f"Exalted {p1} (in {exalt_sign}) receives {aspect} from {p2}. The exaltation power amplifies; year strongly favors {p1}'s significations and {p2}'s domain.",
                aspect=aspect,
            ))
    return out


def y_yamaya(chart):
    """Twin/parallel planets — same degree across houses (sambandha)."""
    out = []
    pos = chart["positions"]
    pl = list(pos.keys())
    seen = set()
    for i, p1 in enumerate(pl):
        for p2 in pl[i+1:]:
            if p1 in ("Rahu","Ketu") or p2 in ("Rahu","Ketu"): continue
            d1 = pos[p1]["deg"]; d2 = pos[p2]["deg"]
            if abs(d1 - d2) <= YAMAYA_ORB_DEG:  # twin-degree
                key = tuple(sorted([p1, p2]))
                if key in seen: continue
                seen.add(key)
                out.append(_yoga(
                    "Yamaya Yoga", "twin_resonance", 3,
                    [p1, p2],
                    f"{p1} and {p2} share nearly identical degree (twin position). Their themes resonate as one — fortunes/struggles in their domains run parallel.",
                ))
    return out


def y_mosthasala(chart):
    """Perfect aspect (orb < 1°) — full ittasala."""
    out = []
    pos = chart["positions"]
    pl = list(pos.keys())
    seen = set()
    for i, p1 in enumerate(pl):
        for p2 in pl[i+1:]:
            if p1 in ("Rahu","Ketu") or p2 in ("Rahu","Ketu"): continue
            l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
            if l1 is None or l2 is None: continue
            aspect, orb, diff = _aspect_type(l1, l2)
            if aspect is None: continue
            if diff >= MOSTHASALA_ORB_DEG: continue
            key = tuple(sorted([p1, p2]))
            if key in seen: continue
            seen.add(key)
            out.append(_yoga(
                "Mosthasala Yoga", "perfect_aspect", 5,
                [p1, p2],
                f"Near-exact {aspect} ({diff:.1f}°) between {p1} and {p2}. Considered a 'perfected' aspect — events of the combined significations manifest powerfully and visibly.",
            ))
    return out


def y_kambula(chart):
    """Ittasala but with malefic in 4th house from one of the participants."""
    out = []
    pos = chart["positions"]
    seen = set()
    for ittasala in y_ittasala(chart):
        p1, p2 = ittasala["planets"]
        for participant in (p1, p2):
            h = pos[participant]["house"]
            target_h = ((h + 3 - 1) % 12) + 1
            for malefic in NATURAL_MALEFICS:
                if malefic in (p1, p2): continue
                if malefic not in pos: continue
                if pos[malefic]["house"] == target_h:
                    key = (p1, p2, malefic)
                    if key in seen: continue
                    seen.add(key)
                    out.append(_yoga(
                        "Kambula Yoga", "afflicted_applying", 3,
                        [p1, p2, malefic],
                        f"Ittasala between {p1} & {p2} but malefic {malefic} sits in 4th-from-{participant}. The applying aspect is partially obstructed; effort meets resistance.",
                    ))
    return out


def _is_between(l_a, l_b, l_test):
    """True if l_test is on the shorter arc between l_a and l_b. Wraps at 360°."""
    arc = (l_b - l_a) % 360
    if arc > 180:
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
        # Find planets sitting on the shorter arc between l1 and l2 (zodiac-wrap safe)
        between = []
        for p3, p3d in pos.items():
            if p3 in (p1, p2): continue
            l3 = _planet_lon(chart, p3)
            if l3 is None: continue
            if _is_between(l1, l2, l3):
                between.append(p3)
        if between and any(b in NATURAL_MALEFICS for b in between):
            out.append(_yoga(
                "Khallasar Yoga", "intercepted_aspect", 3,
                [p1, p2] + between,
                f"Aspect from {p1} to {p2} intercepted by malefic(s) {','.join(between)}. The applying aspect's energy is diverted — partial fruition.",
            ))
    return out


def y_radd(chart):
    """Refusal — one planet applying, other separating (mismatched intent)."""
    out = []
    pos = chart["positions"]
    # For Tajik radd, check planets near aspect but with opposing motion intent
    pl = list(pos.keys())
    seen = set()
    for i, p1 in enumerate(pl):
        for p2 in pl[i+1:]:
            if p1 in ("Rahu","Ketu") or p2 in ("Rahu","Ketu"): continue
            l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
            if l1 is None or l2 is None: continue
            aspect, orb, diff = _aspect_type(l1, l2)
            if aspect is None: continue
            # Radd: orb between 6-12° (just outside perfect, mid-ground)
            if RADD_ORB_LO_DEG <= diff <= RADD_ORB_HI_DEG:
                key = tuple(sorted([p1, p2]))
                if key in seen: continue
                seen.add(key)
                out.append(_yoga(
                    "Radd Yoga", "refused_aspect", 2,
                    [p1, p2],
                    f"Loose {aspect} between {p1} and {p2} (orb {diff:.1f}°). The connection is half-hearted — effort offered may be refused or returned unfulfilled.",
                ))
    return out


def y_naktha(chart):
    """Aspect interrupted by another planet's intervention."""
    out = []
    pos = chart["positions"]
    for ittasala in y_ittasala(chart):
        p1, p2 = ittasala["planets"]
        l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
        # Check if any planet aspects EITHER and is between them
        for p3 in pos:
            if p3 in (p1, p2): continue
            if p3 in ("Rahu","Ketu"): continue
            l3 = _planet_lon(chart, p3)
            if l3 is None: continue
            asp_to_p1, _, _ = _aspect_type(l3, l1)
            asp_to_p2, _, _ = _aspect_type(l3, l2)
            if asp_to_p1 and asp_to_p2:
                out.append(_yoga(
                    "Naktha Yoga", "intervened_aspect", 3,
                    [p1, p2, p3],
                    f"{p3} aspects both {p1} and {p2} — the Ittasala between {p1}-{p2} flows through {p3}'s mediation; outcomes shaped by {p3}'s nature.",
                ))
                break
    return out


def y_indu_yamaya(chart):
    """Moon-special: Moon in twin-aspect with Venus or Jupiter."""
    pos = chart["positions"]
    if "Moon" not in pos: return []
    out = []
    moon_lon = _planet_lon(chart, "Moon")
    for p2 in ("Venus", "Jupiter"):
        if p2 not in pos: continue
        l2 = _planet_lon(chart, p2)
        aspect, orb, diff = _aspect_type(moon_lon, l2)
        if aspect and diff < INDU_YAMAYA_ORB_DEG:
            out.append(_yoga(
                "Indu-Yamaya Yoga", "lunar_benefic_resonance", 4,
                ["Moon", p2],
                f"Moon in close {aspect} with {p2} (orb {diff:.1f}°). Romantic / wealth / domestic harmony peaks during the year — Tajik tradition associates this with marriages and prosperity.",
            ))
    return out


def y_madabihaza(chart):
    """Two slow planets (Saturn, Jupiter, Mars) in mutual aspect."""
    out = []
    pos = chart["positions"]
    SLOW = ["Mars", "Jupiter", "Saturn"]
    for i, p1 in enumerate(SLOW):
        for p2 in SLOW[i+1:]:
            if p1 not in pos or p2 not in pos: continue
            l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
            aspect, _, diff = _aspect_type(l1, l2)
            if aspect is None: continue
            out.append(_yoga(
                "Madabihaza Yoga", "slow_planet_resonance", 3,
                [p1, p2],
                f"Slow planets {p1} and {p2} in {aspect} (orb {diff:.1f}°). Themes mature slowly throughout the year; lasting structural changes possible.",
            ))
    return out


def y_ittahad(chart):
    """Two benefics (Jupiter, Venus, Mercury, Moon) in mutual aspect — 'friendship'."""
    out = []
    pos = chart["positions"]
    seen = set()
    BEN = ["Moon", "Mercury", "Jupiter", "Venus"]
    for i, p1 in enumerate(BEN):
        for p2 in BEN[i+1:]:
            if p1 not in pos or p2 not in pos: continue
            l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
            aspect, _, diff = _aspect_type(l1, l2)
            if aspect is None: continue
            key = tuple(sorted([p1, p2]))
            if key in seen: continue
            seen.add(key)
            out.append(_yoga(
                "Ittahad Yoga", "benefic_friendship", 5,
                [p1, p2],
                f"Benefics {p1} and {p2} in {aspect} — true Tajik 'friendship'. Joy, prosperity, expansion in their combined themes during the year.",
            ))
    return out


def y_mossatail(chart):
    """Three planets equidistant from a third point — combined-yoga."""
    out = []
    pos = chart["positions"]
    pl = [p for p in pos if p not in ("Rahu","Ketu")]
    for i, p1 in enumerate(pl):
        l1 = _planet_lon(chart, p1)
        for j, p2 in enumerate(pl[i+1:], start=i+1):
            l2 = _planet_lon(chart, p2)
            for k, p3 in enumerate(pl[j+1:], start=j+1):
                l3 = _planet_lon(chart, p3)
                if l1 is None or l2 is None or l3 is None: continue
                # midpoint of p1, p2 should equal p3 (or be aspected by p3)
                mid = ((l1 + l2) / 2) % 360
                diff = _angle_between(mid, l3)
                if diff < 3.0:
                    out.append(_yoga(
                        "Mossatail Yoga", "midpoint_combined", 4,
                        [p1, p2, p3],
                        f"{p3} sits at the midpoint of {p1} and {p2} — combined Tajik yoga. The three planets' significations fuse into a single life-theme.",
                    ))
                    return out  # report one
    return out


def y_naktha_yamaya(chart):
    """Naktha + Yamaya hybrid — twin planets whose aspect is interrupted."""
    out = []
    yam = y_yamaya(chart)
    pos = chart["positions"]
    for y in yam:
        p1, p2 = y["planets"]
        l1 = _planet_lon(chart, p1); l2 = _planet_lon(chart, p2)
        for p3 in pos:
            if p3 in (p1, p2) or p3 in ("Rahu","Ketu"): continue
            l3 = _planet_lon(chart, p3)
            if l3 is None: continue
            a, _, _ = _aspect_type(l3, l1)
            b, _, _ = _aspect_type(l3, l2)
            if a and b:
                out.append(_yoga(
                    "Naktha-i-Yamaya Yoga", "interrupted_twin", 3,
                    [p1, p2, p3],
                    f"Twin {p1}-{p2} both aspected by {p3}. The twin-resonance is mediated through {p3} — a third party shapes the conjoined fate.",
                ))
                break
    return out


def y_tambeer_i_surah(chart):
    """'Frame of the picture' — multiple Itthasalas culminating into one chart-defining pattern."""
    itts = y_ittasala(chart)
    if len(itts) >= 3:
        all_planets = set()
        for it in itts:
            all_planets.update(it["planets"])
        return [_yoga(
            "Tambeer-i-Surah Yoga", "chart_defining_frame", 5,
            sorted(all_planets),
            f"Three or more Itthasalas active simultaneously ({len(itts)}). The year carries a defining frame — many themes ripen together; can be transformative.",
        )]
    return []


def y_qutha_i_nur(chart):
    """'Lamp of light' — multiple Ittahads creating chart-defining luminance."""
    itts = y_ittahad(chart)
    if len(itts) >= 2:
        all_planets = set()
        for it in itts:
            all_planets.update(it["planets"])
        return [_yoga(
            "Qutha-i-Nur Yoga", "chart_defining_luminance", 5,
            sorted(all_planets),
            f"Two or more Ittahads (benefic friendships) active. The year is illumined — joy, dharma, prosperity, recognition.",
        )]
    return []


# ============================================================
# TAJIK BALAS (5 strengths)
# ============================================================
HADDA_BOUNDARIES = {
    # Each rasi has 5 hadda terms — simplified as Egyptian/Tajik bounds.
    # Standard Tajik egyptian hadda (degrees within sign, lord)
    "Aries": [(6,"Jupiter"),(12,"Venus"),(20,"Mercury"),(25,"Mars"),(30,"Saturn")],
    "Taurus": [(8,"Venus"),(14,"Mercury"),(22,"Jupiter"),(27,"Saturn"),(30,"Mars")],
    "Gemini": [(6,"Mercury"),(12,"Jupiter"),(17,"Venus"),(24,"Mars"),(30,"Saturn")],
    "Cancer": [(7,"Mars"),(13,"Venus"),(19,"Mercury"),(26,"Jupiter"),(30,"Saturn")],
    "Leo": [(6,"Jupiter"),(11,"Venus"),(18,"Saturn"),(24,"Mercury"),(30,"Mars")],
    "Virgo": [(7,"Mercury"),(17,"Venus"),(21,"Jupiter"),(28,"Mars"),(30,"Saturn")],
    "Libra": [(6,"Saturn"),(14,"Mercury"),(21,"Jupiter"),(28,"Venus"),(30,"Mars")],
    "Scorpio": [(7,"Mars"),(11,"Venus"),(19,"Mercury"),(24,"Jupiter"),(30,"Saturn")],
    "Sagittarius": [(12,"Jupiter"),(17,"Venus"),(21,"Mercury"),(26,"Saturn"),(30,"Mars")],
    "Capricorn": [(7,"Mercury"),(14,"Jupiter"),(22,"Venus"),(26,"Saturn"),(30,"Mars")],
    "Aquarius": [(7,"Mercury"),(13,"Venus"),(20,"Jupiter"),(25,"Mars"),(30,"Saturn")],
    "Pisces": [(12,"Venus"),(16,"Jupiter"),(19,"Mercury"),(28,"Mars"),(30,"Saturn")],
}


def hadda_lord(rasi, deg):
    """Find Hadda (term) lord for given degree within a sign."""
    bounds = HADDA_BOUNDARIES.get(rasi, [])
    for upper, lord in bounds:
        if deg < upper:
            return lord
    return bounds[-1][1] if bounds else None


def hadda_bala(chart, planet):
    """Hadda Bala — does planet sit in its own hadda?"""
    pos = chart["positions"]
    if planet not in pos: return 0
    pd = pos[planet]
    lord = hadda_lord(pd["rasi"], pd["deg"])
    if lord == planet: return 15
    if lord in NATURAL_BENEFICS and planet in NATURAL_BENEFICS: return 7
    return 3


def trirashi_bala(chart, planet):
    """Trirashi (3-sign group) Bala — planet in its 3-sign element family scores."""
    pos = chart["positions"]
    if planet not in pos: return 0
    rasi = pos[planet]["rasi"]
    PLANET_TRIRASHI = {
        "Sun":"Aries","Moon":"Cancer","Mars":"Aries","Mercury":"Gemini",
        "Jupiter":"Sagittarius","Venus":"Taurus","Saturn":"Aquarius"
    }
    own_3 = PLANET_TRIRASHI.get(planet)
    if own_3 is None: return 0
    own_idx = RASIS.index(own_3)
    cur_idx = RASIS.index(rasi)
    if (cur_idx - own_idx) % 4 == 0: return 12
    return 3


def drekkana_bala(chart, planet):
    """Drekkana (D3) — planet's strength based on 1st/2nd/3rd third of sign."""
    pos = chart["positions"]
    if planet not in pos: return 0
    deg = pos[planet]["deg"]
    if deg < 10: dec = 1
    elif deg < 20: dec = 2
    else: dec = 3
    rasi = pos[planet]["rasi"]
    rasi_idx = RASIS.index(rasi)
    # Drekkana lords: 1st = sign-lord, 2nd = 5th-sign-lord, 3rd = 9th-sign-lord
    drek_sign_idx = (rasi_idx + (dec - 1) * 4) % 12
    drek_sign = RASIS[drek_sign_idx]
    drek_lord = RASI_LORDS[drek_sign]
    if drek_lord == planet: return 10
    return 3


def navamsha_bala(chart, planet):
    """Navamsha (D9) Bala — planet's dignity in D9."""
    pos = chart["positions"]
    if planet not in pos: return 0
    deg = pos[planet]["deg"]; rasi_idx = pos[planet]["rasi_idx"]
    nav_idx = int(deg / (30/9))
    is_movable = rasi_idx in (0,3,6,9)
    is_fixed = rasi_idx in (1,4,7,10)
    if is_movable: nav_start = rasi_idx
    elif is_fixed: nav_start = (rasi_idx + 8) % 12
    else: nav_start = (rasi_idx + 4) % 12
    nav_sign_idx = (nav_start + nav_idx) % 12
    nav_sign = RASIS[nav_sign_idx]
    if (planet, nav_sign) in DIGNITIES and DIGNITIES[(planet, nav_sign)] in ("Own","Exalted","Exalted/Own"):
        return 14
    if DIGNITIES.get((planet, nav_sign)) == "Debil":
        return -8
    return 5


def mooladhipati_bala(chart, planet):
    """Mooladhipati Bala — strength of own-sign-lord vs current placement."""
    pos = chart["positions"]
    if planet not in pos: return 0
    rasi = pos[planet]["rasi"]
    rasi_lord = RASI_LORDS[rasi]
    if rasi_lord == planet: return 12
    if rasi_lord in pos:
        h_lord = pos[rasi_lord]["house"]
        if h_lord in (1,4,7,10): return 8
        if h_lord in (6,8,12): return 1
    return 4


def all_balas(chart):
    """Compute all 5 Tajik Balas for all planets."""
    out = {}
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        if p not in chart["positions"]: continue
        out[p] = {
            "hadda": hadda_bala(chart, p),
            "trirashi": trirashi_bala(chart, p),
            "drekkana": drekkana_bala(chart, p),
            "navamsha": navamsha_bala(chart, p),
            "mooladhipati": mooladhipati_bala(chart, p),
        }
        out[p]["total"] = sum(out[p].values())
    return out


# ============================================================
# MASTER DETECTOR
# ============================================================
ALL_TAJIK_YOGA_FNS = [
    y_ittasala, y_iisarafa, y_manaucha, y_yamaya, y_mosthasala,
    y_kambula, y_khallasar, y_radd, y_naktha, y_indu_yamaya,
    y_madabihaza, y_ittahad, y_mossatail, y_naktha_yamaya,
    y_tambeer_i_surah, y_qutha_i_nur,
]


def detect_all_tajik_yogas(chart):
    """Run all 16 Tajik yoga detectors."""
    results = []
    for fn in ALL_TAJIK_YOGA_FNS:
        r = fn(chart)
        if isinstance(r, list):
            results.extend(r)
        elif r:
            results.append(r)
    return results


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    yogas = detect_all_tajik_yogas(chart)
    print(f"=== {len(yogas)} TAJIK YOGAS for {chart['name']} ===\n")
    for y in yogas:
        sev_stars = "*" * y["severity"]
        print(f"  [{sev_stars:5s}] {y['name']:30s} {y['type']}")
        print(f"        Planets: {', '.join(y['planets'])}")
        print(f"        {y['interpretation'][:130]}")
        print()

    print(f"\n=== TAJIK BALAS for {chart['name']} ===")
    balas = all_balas(chart)
    print(f"  {'Planet':10s} {'Hadda':>6s} {'Tri':>5s} {'Drek':>5s} {'Nav':>5s} {'Mool':>5s} {'Total':>7s}")
    for p, bs in balas.items():
        print(f"  {p:10s} {bs['hadda']:6d} {bs['trirashi']:5d} {bs['drekkana']:5d} {bs['navamsha']:5d} {bs['mooladhipati']:5d} {bs['total']:7d}")
