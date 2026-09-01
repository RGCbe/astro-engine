"""
Dasha Compute Engine — Vimshottari + Yogini Dasha systems.

Implements:
  - Vimshottari Maha Dasha (120-year cycle) with exact birth balance
  - Vimshottari Antardasha (sub-periods) for ALL Maha Dasha periods
  - Yogini Dasha (36-year cycle) with birth balance
  - Current Dasha/Antardasha identification at any given moment

Classical source: BPHS Ch.46-53; Phala Deepika Ch.20.
"""
import datetime

# ─── Constants ────────────────────────────────────────────────────────────────

VIMSHOTTARI_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}
VIMSHOTTARI_TOTAL = 120  # sum of all years

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

YOGINI_ORDER = ["Mangala", "Pingala", "Dhanya", "Bhramari", "Bhadrika", "Ulka", "Siddha", "Sankata"]
YOGINI_LORDS = {
    "Mangala": "Moon", "Pingala": "Sun", "Dhanya": "Jupiter", "Bhramari": "Mars",
    "Bhadrika": "Mercury", "Ulka": "Saturn", "Siddha": "Venus", "Sankata": "Rahu"
}
YOGINI_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]  # Total 36 years


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _days(years: float) -> float:
    """Convert fractional years to days (Julian year = 365.25 days)."""
    return years * 365.25


def _antardasha_years(maha_lord: str, antar_lord: str) -> float:
    """
    Compute Antardasha (sub-period) duration in years.
    Formula: (Maha_years * Antar_years) / 120
    """
    return (VIMSHOTTARI_YEARS[maha_lord] * VIMSHOTTARI_YEARS[antar_lord]) / VIMSHOTTARI_TOTAL


def _fmt(dt_obj: datetime.datetime) -> str:
    return dt_obj.strftime("%Y-%m-%d")


# ─── Vimshottari ─────────────────────────────────────────────────────────────

def calculate_vimshottari(moon_longitude: float, birth_date: datetime.datetime) -> dict:
    """
    Full Vimshottari Dasha computation with Antardashas.

    Returns:
        periods       : List of all Maha Dasha periods (with nested antardashas)
        current_maha_dasha  : The running Maha Dasha right now
        current_antardasha  : The running Antardasha (sub-period) right now
    """
    # 1. Nakshatra balance at birth
    nakshatra_idx = int(moon_longitude / (360 / 27))
    nak_start_deg = nakshatra_idx * (360 / 27)
    nak_length = 360 / 27

    degrees_passed = moon_longitude - nak_start_deg
    degrees_remaining = nak_length - degrees_passed

    start_lord = NAKSHATRA_LORDS[nakshatra_idx]
    total_maha_years = VIMSHOTTARI_YEARS[start_lord]
    fraction_remaining = degrees_remaining / nak_length
    balance_years = total_maha_years * fraction_remaining

    start_idx = VIMSHOTTARI_ORDER.index(start_lord)

    # 2. Build Maha Dasha periods — generate enough cycles to cover today
    # For historical charts (>120 years old) we need multiple cycles
    periods = []
    current_date = birth_date
    now = datetime.datetime.now()

    # Keep cycling until we have covered at least 5 years past today
    cycle_num = 0
    while current_date < now + datetime.timedelta(days=5 * 365):
        for cycle_i in range(9):
            lord_idx = (start_idx + cycle_i) % 9
            maha_lord = VIMSHOTTARI_ORDER[lord_idx]

            if cycle_num == 0 and cycle_i == 0:
                maha_years = balance_years   # partial first period
                is_balance = True
                antar_scale = fraction_remaining
            else:
                maha_years = VIMSHOTTARI_YEARS[maha_lord]
                is_balance = False
                antar_scale = 1.0

            maha_end = current_date + datetime.timedelta(days=_days(maha_years))

            # Build Antardashas inside this Maha Dasha.
            antar_start_idx = lord_idx
            antardashas = []

            if is_balance:
                # Balance dasha = the TAIL of a full maha dasha already running
                # at birth. Antardashas run at FULL length from the notional
                # (pre-birth) dasha start; only those still active after birth
                # appear, the first one clipped to the birth moment. (Fixes the
                # old bug that restarted the bukti sequence at birth and
                # compressed all 9 into the balance window.)
                elapsed_years = total_maha_years - balance_years
                notional_start = current_date - datetime.timedelta(days=_days(elapsed_years))
                antar_date = notional_start
                for antar_i in range(9):
                    antar_lord = VIMSHOTTARI_ORDER[(antar_start_idx + antar_i) % 9]
                    antar_years = _antardasha_years(maha_lord, antar_lord)  # full
                    antar_end = antar_date + datetime.timedelta(days=_days(antar_years))
                    if antar_end > current_date:
                        disp_start = max(antar_date, current_date)
                        antardashas.append({
                            "lord": antar_lord,
                            "start": _fmt(disp_start),
                            "end": _fmt(antar_end),
                            "duration_days": round((antar_end - disp_start).days),
                        })
                    antar_date = antar_end
            else:
                antar_date = current_date
                for antar_i in range(9):
                    antar_lord = VIMSHOTTARI_ORDER[(antar_start_idx + antar_i) % 9]
                    antar_years = _antardasha_years(maha_lord, antar_lord)
                    antar_end = antar_date + datetime.timedelta(days=_days(antar_years))
                    antardashas.append({
                        "lord": antar_lord,
                        "start": _fmt(antar_date),
                        "end": _fmt(antar_end),
                        "duration_days": round(_days(antar_years)),
                    })
                    antar_date = antar_end

            periods.append({
                "lord": maha_lord,
                "start": _fmt(current_date),
                "end": _fmt(maha_end),
                "duration_years": round(maha_years, 2),
                "is_balance": is_balance,
                "antardashas": antardashas,
            })
            current_date = maha_end

            if current_date >= now + datetime.timedelta(days=5 * 365):
                break  # Enough periods generated
        cycle_num += 1

    # 4. Find currently running Maha + Antardasha
    current_maha = None
    current_antar = None
    current_pratyantar = None

    for p in periods:
        p_start = datetime.datetime.strptime(p["start"], "%Y-%m-%d")
        p_end   = datetime.datetime.strptime(p["end"],   "%Y-%m-%d")
        if p_start <= now < p_end:
            current_maha = {k: v for k, v in p.items() if k != "antardashas"}
            for a in p["antardashas"]:
                a_start = datetime.datetime.strptime(a["start"], "%Y-%m-%d")
                a_end   = datetime.datetime.strptime(a["end"],   "%Y-%m-%d")
                if a_start <= now < a_end:
                    current_antar = a
                    # ── Pratyantardasha (sub-sub-period) inside this Antardasha ──
                    # Formula: (Maha * Antar * Pratyantar) / 120² × total days
                    # Simplified: Antar_days * (Pratyantar_years / Maha_years)
                    maha_lord  = p["lord"]
                    antar_lord = a["lord"]
                    antar_total_days = _days(_antardasha_years(maha_lord, antar_lord))
                    if antar_total_days > 0:
                        pratyantar_periods = []
                        antar_lord_idx = VIMSHOTTARI_ORDER.index(antar_lord)
                        pt_date = a_start
                        for pt_i in range(9):
                            pt_lord_idx = (antar_lord_idx + pt_i) % 9
                            pt_lord = VIMSHOTTARI_ORDER[pt_lord_idx]
                            # Pratyantar years = Antar_years * Pratyantar_years / 120
                            pt_years = _antardasha_years(antar_lord, pt_lord)
                            # Scale to antar scale (if antar was scaled, propagate)
                            pt_days  = a.get("duration_days", antar_total_days) * (pt_years / _antardasha_years(maha_lord, antar_lord)) if _antardasha_years(maha_lord, antar_lord) > 0 else _days(pt_years)
                            pt_end_dt = pt_date + datetime.timedelta(days=pt_days)
                            pratyantar_periods.append({
                                "lord": pt_lord,
                                "start": _fmt(pt_date),
                                "end": _fmt(pt_end_dt),
                                "duration_days": round(pt_days),
                            })
                            if pt_date <= now < pt_end_dt:
                                current_pratyantar = pratyantar_periods[-1]
                            pt_date = pt_end_dt
                    break
            break

    if not current_maha:
        current_maha = periods[-1]

    return {
        "periods": periods,
        "current_maha_dasha": current_maha,
        "current_antardasha": current_antar,
        "current_pratyantar_dasha": current_pratyantar,
    }


# ─── Yogini ───────────────────────────────────────────────────────────────────

def calculate_yogini(moon_longitude: float, birth_date: datetime.datetime) -> dict:
    """
    Calculates Yogini Dasha periods (36-year cycle) with balance at birth.
    """
    nakshatra_idx = int(moon_longitude / (360 / 27))
    nak_start_deg = nakshatra_idx * (360 / 27)
    nak_length = 360 / 27
    degrees_remaining = nak_length - (moon_longitude - nak_start_deg)
    fraction = degrees_remaining / nak_length

    yogini_idx = ((nakshatra_idx + 1) + 3) % 8
    if yogini_idx == 0:
        yogini_idx = 8

    start_idx = yogini_idx - 1
    start_yogini = YOGINI_ORDER[start_idx]
    total_years = YOGINI_YEARS[start_idx]
    balance_days = (total_years * fraction) * 365.25

    periods = []
    current_date = birth_date
    first_end = current_date + datetime.timedelta(days=balance_days)

    periods.append({
        "yogini": start_yogini,
        "lord": YOGINI_LORDS[start_yogini],
        "start": _fmt(current_date),
        "end": _fmt(first_end),
        "is_balance": True
    })
    current_date = first_end

    # Generate 3 full cycles (~108 years coverage)
    for _ in range(3):
        for i in range(1, 9):
            idx = (start_idx + i) % 8
            y_name = YOGINI_ORDER[idx]
            years = YOGINI_YEARS[idx]
            end_date = current_date + datetime.timedelta(days=years * 365.25)
            periods.append({
                "yogini": y_name,
                "lord": YOGINI_LORDS[y_name],
                "start": _fmt(current_date),
                "end": _fmt(end_date),
                "is_balance": False
            })
            current_date = end_date

    now = datetime.datetime.now()
    current_dasha = None
    for p in periods:
        p_start = datetime.datetime.strptime(p["start"], "%Y-%m-%d")
        p_end = datetime.datetime.strptime(p["end"], "%Y-%m-%d")
        if p_start <= now < p_end:
            current_dasha = p
            break

    return {
        "periods": periods,
        "current_yogini_dasha": current_dasha
    }
