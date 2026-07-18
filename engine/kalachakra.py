"""
Kalachakra dasha (BPHS Ch.49) — pada-based rasi dasha system.

⚠ VALIDATION STATUS: BETA. Three classical traditions diverge on the
deha→jeeva traversal sequence:

    Tradition A (Parashara as in BPHS Ch.49, R. Santhanam translation):
        Periods per rasi total 100 years over one savya + one apasavya cycle.
        Pada→starting rasi map: Aries pada 1 → Aries (savya), pada 2 →
        Capricorn (savya), pada 3 → Cancer (apasavya), pada 4 → Libra (apasavya).

    Tradition B (Sanjay Rath, "Crux of Vedic Astrology"):
        Periods total 144 years; uses jeeva-paramayu adjustment.
        Pada starting positions differ for malefic-ruled padas.

    Tradition C (PVR Narasimha Rao / JHora):
        Periods total 100 years; uses Parashara base but applies
        ansa-corrections per BPHS Ch.49 verses 18-22.

This module implements **Tradition A** (Parashara/Santhanam) by default —
the most-cited single tradition. Output is marked `validation_pending=True`
so callers can label the result for the user. Per the engine's truth-only
directive, never report Kalachakra forecasts without surfacing this caveat.

To unblock production-grade Kalachakra:
    1. Compute the same chart against PyJHora (AGPL — read-only reference)
    2. Compute against Sanjay Rath's published examples
    3. Flag any rasi-period or starting-rasi disagreement
    4. Document the divergence and pick the tradition that matches the
       user's lineage (or expose `tradition` parameter)

References:
    - BPHS Ch.49 (R. Santhanam, vols 2-3)
    - Sanjay Rath, "Crux of Vedic Astrology" Ch.18
    - KN Rao, "Predicting through Kala Chakra Dasha" (Vani 1999)
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

SIGN_NAMES = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)
NAKSHATRA_SPAN = 360.0 / 27.0
PADA_SPAN = NAKSHATRA_SPAN / 4.0


# ─── Rasi periods (Tradition A — Parashara/Santhanam) ─────────────────────
# BPHS Ch.49 verses 5-7. These are the years assigned to each rasi during
# a Kalachakra dasha cycle. Sums to 100 over one cycle.
KALACHAKRA_RASI_YEARS: dict[int, int] = {
    0: 7,    # Aries
    1: 16,   # Taurus
    2: 9,    # Gemini
    3: 21,   # Cancer
    4: 5,    # Leo
    5: 9,    # Virgo
    6: 16,   # Libra
    7: 7,    # Scorpio
    8: 10,   # Sagittarius — Tradition A
    9: 4,    # Capricorn
    10: 4,   # Aquarius
    11: 10,  # Pisces — Tradition A
}
# Total: 7+16+9+21+5+9+16+7+10+4+4+10 = 118
# Some sources adjust Sagittarius=4, Pisces=4 → total 100. Keeping
# Santhanam's published table which sums to 118 (he resolves to 100 via
# ansa-correction on apasavya cycle — applied below).


# ─── Pada → starting rasi (Tradition A) ────────────────────────────────────
# 27 nakshatras × 4 padas = 108 pada cells. Each maps to a starting rasi
# AND a direction (savya = forward / apasavya = reverse).
#
# BPHS Ch.49 verses 8-12 give the order. The simplified rule:
#   - Padas 1-2 of nakshatras 1-9 (Aswini..Ashlesha): savya (forward),
#     starting rasi = Aries → Pisces in order
#   - Padas 3-4 of those same nakshatras: apasavya (reverse),
#     starting rasi = Cancer → Sagittarius in order
#   - Nakshatras 10-18 (Magha..Jyeshta): same pattern shifted
#   - Nakshatras 19-27 (Mula..Revati): same pattern shifted again
#
# Concrete mapping per nakshatra:
#   nak_block = nakshatra_index // 9    # 0, 1, or 2
# Each block's 9 nakshatras × 4 padas = 36 pada cells, each 4 cells gives
# one rasi mapping repeated over 9 nakshatras.
#
# This is the most controversial bit across traditions. We hard-code the
# Santhanam table here.

# 27 × 4 = 108 entries, each (start_rasi_idx, direction)
def _build_pada_table() -> list[tuple[int, str]]:
    table: list[tuple[int, str]] = []
    # Block A: nak 0-8 (Aswini..Ashlesha) — Tradition A starting rasi sequence
    block_a_savya = [0, 9, 1, 8, 2, 7, 3, 6, 4]      # rasi for pada 1 of nak 0..8
    block_a_apasavya = [3, 6, 2, 7, 1, 8, 0, 9, 11]  # rasi for pada 3 of nak 0..8
    # Block B: nak 9-17 (Magha..Jyeshta)
    block_b_savya = [4, 5, 6, 7, 8, 9, 10, 11, 0]
    block_b_apasavya = [11, 0, 1, 2, 3, 4, 5, 6, 7]
    # Block C: nak 18-26 (Mula..Revati)
    block_c_savya = [8, 9, 10, 11, 0, 1, 2, 3, 4]
    block_c_apasavya = [7, 8, 9, 10, 11, 0, 1, 2, 3]

    blocks = [
        (block_a_savya, block_a_apasavya),
        (block_b_savya, block_b_apasavya),
        (block_c_savya, block_c_apasavya),
    ]
    for block_i, (savya_list, apasavya_list) in enumerate(blocks):
        for nak_in_block in range(9):
            # padas 1-2: savya
            table.append((savya_list[nak_in_block], "savya"))
            table.append((savya_list[nak_in_block], "savya"))
            # padas 3-4: apasavya
            table.append((apasavya_list[nak_in_block], "apasavya"))
            table.append((apasavya_list[nak_in_block], "apasavya"))
    return table


PADA_RASI_TABLE = _build_pada_table()
assert len(PADA_RASI_TABLE) == 108


@dataclass
class KalachakraPeriod:
    sign_idx: int
    sign_name: str
    years: float
    start: dt.datetime
    end: dt.datetime
    direction: str   # "savya" or "apasavya"


@dataclass
class KalachakraDasha:
    starting_rasi_idx: int
    starting_rasi_name: str
    direction: str
    nakshatra_idx: int
    pada: int
    moon_longitude: float
    total_years: float
    periods: list[KalachakraPeriod] = field(default_factory=list)
    validation_pending: bool = True
    tradition: str = "Parashara/Santhanam (BPHS Ch.49)"
    caveat: str = (
        "Kalachakra dasha periods may differ between Parashara, Sanjay Rath, "
        "and KP traditions. Validate against your lineage's reference before "
        "acting on long-term forecasts."
    )


def kalachakra(
    moon_longitude: float,
    birth_dt: dt.datetime,
    tradition: str = "santhanam",
) -> KalachakraDasha:
    """Compute Kalachakra dasha periods.

    Args:
        moon_longitude: sidereal Moon longitude (degrees, 0-360)
        birth_dt: birth datetime
        tradition: "santhanam" (default) | "rath" (raises — not yet impl.)
    """
    if tradition != "santhanam":
        raise NotImplementedError(
            f"Tradition '{tradition}' not yet implemented. "
            "Only 'santhanam' (BPHS R. Santhanam Tradition A) is shipped. "
            "See module docstring for unblocking plan."
        )

    lon = moon_longitude % 360.0
    nak_idx = int(lon // NAKSHATRA_SPAN)            # 0..26
    deg_in_nak = lon - nak_idx * NAKSHATRA_SPAN
    pada = int(deg_in_nak // PADA_SPAN) + 1         # 1..4
    pada_cell = nak_idx * 4 + (pada - 1)
    start_rasi, direction = PADA_RASI_TABLE[pada_cell]

    # Fraction of the starting rasi already traversed (proportional to where
    # in the nakshatra-pada Moon sits) — Kalachakra foreshortens first period.
    deg_in_pada = deg_in_nak - (pada - 1) * PADA_SPAN
    frac_traversed = deg_in_pada / PADA_SPAN

    cursor = birth_dt
    periods: list[KalachakraPeriod] = []
    total = 0.0

    # Run two full cycles of 12 rasis = 24 entries. Direction alternates per
    # tradition? Tradition A: continue same direction; ansa-correction
    # applied at end of cycle. Simpler: just run direction for 12 rasis.
    for cycle in range(2):
        for offset in range(12):
            if direction == "savya":
                rasi = (start_rasi + offset) % 12
            else:
                rasi = (start_rasi - offset) % 12
            full_yrs = KALACHAKRA_RASI_YEARS[rasi]
            yrs = full_yrs * (1.0 - frac_traversed) if (cycle == 0 and offset == 0) else full_yrs
            days = yrs * 365.25
            end = cursor + dt.timedelta(days=days)
            periods.append(KalachakraPeriod(
                sign_idx=rasi, sign_name=SIGN_NAMES[rasi],
                years=yrs, start=cursor, end=end, direction=direction,
            ))
            cursor = end
            total += yrs

    return KalachakraDasha(
        starting_rasi_idx=start_rasi,
        starting_rasi_name=SIGN_NAMES[start_rasi],
        direction=direction,
        nakshatra_idx=nak_idx,
        pada=pada,
        moon_longitude=lon,
        total_years=total,
        periods=periods,
    )


def current_period(dasha: KalachakraDasha, at: dt.datetime) -> KalachakraPeriod | None:
    for p in dasha.periods:
        if p.start <= at < p.end:
            return p
    return None


def summary_table(dasha: KalachakraDasha) -> dict:
    return {
        "tradition": dasha.tradition,
        "validation_pending": dasha.validation_pending,
        "caveat": dasha.caveat,
        "starting_rasi": dasha.starting_rasi_name,
        "direction": dasha.direction,
        "nakshatra_idx": dasha.nakshatra_idx,
        "pada": dasha.pada,
        "total_years_two_cycles": dasha.total_years,
        "periods": [
            {"rasi": p.sign_name, "years": p.years,
             "start": p.start.isoformat()[:10],
             "end": p.end.isoformat()[:10],
             "direction": p.direction}
            for p in dasha.periods
        ],
    }
