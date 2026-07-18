"""
Jaimini raasi-based dashas — sign-period dashas distinct from Vimshottari/
Ashtottari (which are nakshatra-graha based).

Implemented:
    chara_dasha   — variable-length per sign, Parashari/KN Rao convention.
                     Total ≈ 144 years.
    sthira_dasha  — fixed lengths per sign (7/8/9 years).
                     Total = 96 years.
    shoola_dasha  — uniform 9 years per sign, fixed starting sign.
                     Total = 108 years (BPHS Ch.50).

NOT implemented here (deferred — requires multi-source textual validation):
    kalachakra_dasha (BPHS Ch.49) — pada-based deha/jeeva traversal. The
        algorithm has multiple sect-specific variations (PVR Narasimha Rao
        differs from Sanjay Rath); we will ship only after we have ≥3 source
        cross-validations on a fixed test chart.

Sign indices: 0 = Aries .. 11 = Pisces.
House-counting follows the conventional zodiacal order.

References:
    - BPHS Ch.55 (Chara), Ch.50 (Shoola)
    - Jaimini Sutras, Adhyaya 2 Pada 3 (Chara/Sthira)
    - KN Rao, "Predicting Through Jaimini's Chara Dasha"
    - Sanjay Rath, "Crux of Vedic Astrology"
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

SIGN_NAMES = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

# ─── Sign lords (Jaimini convention — modern KN Rao with nodal lords) ─────
# In Jaimini, Scorpio is co-lorded by Mars/Ketu and Aquarius by Saturn/Rahu.
# When the node is *stronger* (placed in the sign or aspecting), the node is
# preferred. Default to the traditional planet — caller can override.
SIGN_LORD: dict[int, str] = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}

# ─── Direction rule (Jaimini Chara) ────────────────────────────────────────
# "Savya" (direct/forward) signs vs "apasavya" (reverse) — used to decide the
# direction of counting from sign to its lord.
# Convention (Sanjay Rath / KN Rao):
#   Savya:   Aries, Taurus, Leo, Scorpio, Aquarius, Pisces
#   Apasavya: Gemini, Cancer, Virgo, Libra, Sagittarius, Capricorn
SAVYA_SIGNS = {0, 1, 4, 7, 10, 11}


# ─── Data classes ──────────────────────────────────────────────────────────
@dataclass
class RaasiPeriod:
    sign_idx: int
    sign_name: str
    lord: str
    years: float
    start: dt.datetime
    end: dt.datetime


@dataclass
class RaasiDasha:
    name: str            # "chara" | "sthira" | "shoola"
    total_years: float
    periods: list[RaasiPeriod] = field(default_factory=list)


# ─── Chara dasha ───────────────────────────────────────────────────────────
def _chara_years(sign_idx: int, lord_sign_idx: int) -> int:
    """Standard Parashari Chara period for a sign, given its lord's sign."""
    # Direction: savya counts forward, apasavya counts backward
    if sign_idx in SAVYA_SIGNS:
        diff = (lord_sign_idx - sign_idx) % 12
    else:
        diff = (sign_idx - lord_sign_idx) % 12
    # Years = diff if lord not in same sign, else 12. Subtract 1 if lord in
    # the sign being computed (so a lord-in-its-own-sign gives 0; convention
    # is to treat 0 as 12 so the dasha runs the full cycle).
    yrs = diff
    if yrs == 0:
        yrs = 12
    return yrs


def chara_dasha(
    lagna_sign_idx: int,
    planet_signs: dict[str, int],
    birth_dt: dt.datetime,
    use_node_lords: bool = False,
) -> RaasiDasha:
    """Compute Jaimini Chara dasha starting from lagna sign.

    Args:
        lagna_sign_idx: 0..11
        planet_signs: {"Sun": sign_idx, ...} — the sign each planet occupies
        birth_dt: birth datetime
        use_node_lords: if True, use Ketu for Scorpio and Rahu for Aquarius
    """
    sign_lords = dict(SIGN_LORD)
    if use_node_lords:
        sign_lords[7] = "Ketu"   # Scorpio
        sign_lords[10] = "Rahu"  # Aquarius

    periods: list[RaasiPeriod] = []
    cursor = birth_dt
    total = 0.0
    # Order: from lagna sign onward, savya direction (zodiacal forward)
    for offset in range(12):
        sign = (lagna_sign_idx + offset) % 12
        lord = sign_lords[sign]
        # Lord's sign — may not be in planet_signs (e.g., for Ketu/Rahu if
        # planet_signs is graha-only). Fall back to the lord's own sign.
        lord_sign = planet_signs.get(lord)
        if lord_sign is None:
            lord_sign = sign  # treat as lord in its own sign → 12 yrs
        yrs = _chara_years(sign, lord_sign)
        days = yrs * 365.25
        end = cursor + dt.timedelta(days=days)
        periods.append(RaasiPeriod(
            sign_idx=sign, sign_name=SIGN_NAMES[sign], lord=lord,
            years=yrs, start=cursor, end=end,
        ))
        cursor = end
        total += yrs

    return RaasiDasha(name="chara", total_years=total, periods=periods)


# ─── Sthira dasha ──────────────────────────────────────────────────────────
# Movable signs: 7 yrs | Fixed signs: 8 yrs | Dual signs: 9 yrs
# Movable: Aries(0), Cancer(3), Libra(6), Capricorn(9)
# Fixed:   Taurus(1), Leo(4), Scorpio(7), Aquarius(10)
# Dual:    Gemini(2), Virgo(5), Sagittarius(8), Pisces(11)
STHIRA_YEARS = {
    0: 7, 3: 7, 6: 7, 9: 7,
    1: 8, 4: 8, 7: 8, 10: 8,
    2: 9, 5: 9, 8: 9, 11: 9,
}


def sthira_dasha(lagna_sign_idx: int, birth_dt: dt.datetime) -> RaasiDasha:
    """Jaimini Sthira dasha — fixed period per sign, total 96 yrs."""
    periods: list[RaasiPeriod] = []
    cursor = birth_dt
    total = 0.0
    for offset in range(12):
        sign = (lagna_sign_idx + offset) % 12
        yrs = STHIRA_YEARS[sign]
        days = yrs * 365.25
        end = cursor + dt.timedelta(days=days)
        periods.append(RaasiPeriod(
            sign_idx=sign, sign_name=SIGN_NAMES[sign], lord=SIGN_LORD[sign],
            years=yrs, start=cursor, end=end,
        ))
        cursor = end
        total += yrs
    return RaasiDasha(name="sthira", total_years=total, periods=periods)


# ─── Shoola dasha (BPHS Ch.50) ─────────────────────────────────────────────
# Uniform 9 yrs per sign, total 108 yrs. Starting sign:
#   - From lagna if lagna lord is in lagna or 7th
#   - From 7th if 7th lord is stronger
#   - Otherwise from lagna
# Direction: zodiacal forward.
def shoola_dasha(
    lagna_sign_idx: int,
    seventh_lord_strength: float | None = None,
    lagna_lord_strength: float | None = None,
    birth_dt: dt.datetime | None = None,
) -> RaasiDasha:
    """Jaimini Shoola dasha. 9 yrs per sign × 12 = 108 yrs."""
    if birth_dt is None:
        birth_dt = dt.datetime(2000, 1, 1)
    # Pick starting sign — lagna by default; switch to 7th if 7th-lord stronger
    start = lagna_sign_idx
    if (seventh_lord_strength is not None and lagna_lord_strength is not None
            and seventh_lord_strength > lagna_lord_strength):
        start = (lagna_sign_idx + 6) % 12

    periods: list[RaasiPeriod] = []
    cursor = birth_dt
    total = 0.0
    for offset in range(12):
        sign = (start + offset) % 12
        yrs = 9.0
        days = yrs * 365.25
        end = cursor + dt.timedelta(days=days)
        periods.append(RaasiPeriod(
            sign_idx=sign, sign_name=SIGN_NAMES[sign], lord=SIGN_LORD[sign],
            years=yrs, start=cursor, end=end,
        ))
        cursor = end
        total += yrs
    return RaasiDasha(name="shoola", total_years=total, periods=periods)


# ─── Lookup helper ─────────────────────────────────────────────────────────
def current_period(dasha: RaasiDasha, at: dt.datetime) -> RaasiPeriod | None:
    for p in dasha.periods:
        if p.start <= at < p.end:
            return p
    return None


def summary_table(dasha: RaasiDasha) -> list[dict]:
    return [
        {
            "sign": p.sign_name,
            "lord": p.lord,
            "years": p.years,
            "start": p.start.isoformat()[:10],
            "end": p.end.isoformat()[:10],
        }
        for p in dasha.periods
    ]


# ─── Kalachakra — deferred ─────────────────────────────────────────────────
def kalachakra_dasha(*args, **kwargs):
    """NOT IMPLEMENTED. Kalachakra dasha (BPHS Ch.49) is deferred until we
    have ≥3 multi-source cross-validations on a fixed test chart. The
    algorithm has well-known sect-specific variations (Parashara vs KP vs
    Sanjay Rath traditions diverge on deha/jeeva traversal and ansa scoring).

    To unblock: read BPHS Ch.49 carefully + Sanjay Rath's "Vimshottari and
    Yogini Dashas" + PVR Narasimha Rao's notes, then implement against a
    test chart with all three references producing identical periods.
    """
    raise NotImplementedError(
        "Kalachakra dasha requires multi-source textual validation. "
        "See engine/raasi_dasha.py docstring for the unblocking plan."
    )
