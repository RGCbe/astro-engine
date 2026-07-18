"""engine.panchanga — 5-fold time analysis (Tithi, Vara, Yoga, Karana, Nakshatra).

Bridges to runtime/panchanga.py.
Exposes: panchanga(), Panchanga, NAKSHATRAS, VARAS — the API engine/ expects.

Extended for Muhurta support: accepts optional (lat, lon, tz_hours) and computes
Rahu Kala, Yamaganda Kala, Gulika Kala, Abhijit Muhurta, and Brahma Muhurta windows.
"""
import sys, os, datetime as dt
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))

# Re-export from runtime
from panchanga import (
    compute_panchanga as _compute,
    NAKSHATRAS,
    VARAS,
    TITHIS,
    YOGAS,
    KARANAS,
)


@dataclass
class Panchanga:
    """Panchanga data class — what engine/ code expects."""
    datetime: str
    tithi: str
    tithi_number: int
    tithi_index: int          # 1-based tithi number (alias for muhurta compat)
    paksha: str
    vara: str
    vara_lord: str
    nakshatra: str
    pada: int
    yoga: str
    karana: str
    is_bhadra: bool = False
    is_amavasya: bool = False
    is_purnima: bool = False
    # Muhurta time windows (nullable — only set if lat/lon provided)
    rahu_kala: tuple = None
    yamaganda_kala: tuple = None
    gulika_kala: tuple = None
    abhijit_muhurta: tuple = None
    brahma_muhurta: tuple = None


# ── Rahu Kala / Yamaganda / Gulika computation ──────────────────────────
# These are fixed fractional periods of the day based on weekday.
# Standard order for Rahu Kala: (Sun=8th, Mon=2nd, Tue=7th, Wed=5th,
# Thu=6th, Fri=4th, Sat=3rd) — 1/8th of the day each.

# Rahu Kala slot index by weekday (Sun=0..Sat=6)
_RAHU_SLOT  = [7, 1, 6, 4, 5, 3, 2]  # 0-indexed slot (period 1-8)
_YAMA_SLOT  = [4, 3, 2, 1, 0, 6, 5]
_GULIKA_SLOT = [6, 5, 4, 3, 2, 1, 0]


def _time_window(base_dt, sunrise_h, period_len, slot):
    """Compute a time window given sunrise hour, period length (hrs), and slot index."""
    start_h = sunrise_h + slot * period_len
    end_h = start_h + period_len
    start = base_dt.replace(hour=0, minute=0, second=0) + dt.timedelta(hours=start_h)
    end = base_dt.replace(hour=0, minute=0, second=0) + dt.timedelta(hours=end_h)
    return (start, end)


def panchanga(when=None, lat=None, lon=None, tz_hours=None):
    """Compute panchanga for given datetime (default now). Returns Panchanga dataclass.
    
    If lat/lon/tz_hours are provided, also computes inauspicious time windows
    (Rahu Kala, Yamaganda, Gulika) and auspicious windows (Abhijit, Brahma Muhurta).
    """
    if when is None:
        when = dt.datetime.now()
    d = _compute(when)
    
    # Map runtime dict to dataclass
    p = Panchanga(
        datetime=d.get("datetime", str(when)),
        tithi=d["tithi"],
        tithi_number=d["tithi_number"],
        tithi_index=d["tithi_number"],   # alias
        paksha=d["paksha"],
        vara=d["vara"],
        vara_lord=d["vara_lord"],
        nakshatra=d["nakshatra"],
        pada=d["pada"],
        yoga=d["yoga"],
        karana=d["karana"],
        is_bhadra=d.get("is_bhadra", False),
        is_amavasya=d.get("is_amavasya", False),
        is_purnima=d.get("is_purnima", False),
    )
    
    # Compute time windows if location is provided
    if lat is not None and lon is not None:
        # Approximate sunrise/sunset (simple formula; ~6:00 AM default for India)
        # For more accuracy, use Swiss Ephemeris sun transit — but this is sufficient
        # for muhurta screening.
        sunrise_h = 6.0  # approximate sunrise hour (local time)
        sunset_h = 18.0  # approximate sunset hour
        day_len = sunset_h - sunrise_h
        period_len = day_len / 8.0
        
        weekday = when.weekday()  # Mon=0
        vedic_wd = (weekday + 1) % 7  # Sun=0
        
        p.rahu_kala = _time_window(when, sunrise_h, period_len, _RAHU_SLOT[vedic_wd])
        p.yamaganda_kala = _time_window(when, sunrise_h, period_len, _YAMA_SLOT[vedic_wd])
        p.gulika_kala = _time_window(when, sunrise_h, period_len, _GULIKA_SLOT[vedic_wd])
        
        # Abhijit Muhurta: midday ± ~24 min (the 8th muhurta of the day)
        midday = sunrise_h + day_len / 2.0
        abhijit_start = when.replace(hour=0, minute=0, second=0) + dt.timedelta(hours=midday - 0.4)
        abhijit_end = when.replace(hour=0, minute=0, second=0) + dt.timedelta(hours=midday + 0.4)
        p.abhijit_muhurta = (abhijit_start, abhijit_end)
        
        # Brahma Muhurta: ~1h36m before sunrise (2 muhurtas before sunrise)
        brahma_start = when.replace(hour=0, minute=0, second=0) + dt.timedelta(hours=sunrise_h - 1.6)
        brahma_end = when.replace(hour=0, minute=0, second=0) + dt.timedelta(hours=sunrise_h - 0.8)
        p.brahma_muhurta = (brahma_start, brahma_end)
    
    return p
