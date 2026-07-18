"""engine.dasha — Vimshottari dasha computation.

Bridges to runtime/granular_dasha.py. Exposes the API expected by other
engine/ modules: vimshottari(), current_dasha(), NAKSHATRA_LORDS_VIMSHOTTARI, NAKSHATRA_SPAN.
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))

# Import from runtime
from granular_dasha import (
    build_full_timeline as _build_timeline,
    lookup as _lookup,
    VIMSHOTTARI_YEARS,
    VIMSHOTTARI_ORDER,
    NAK_LORDS_27,
)

# Constants in the format engine/ expects
NAKSHATRA_LORDS_VIMSHOTTARI = NAK_LORDS_27[:9]  # 9 lord cycle (Vimshottari)
NAKSHATRA_SPAN = 360 / 27.0  # 13°20'


def _nakshatra_index(longitude: float) -> int:
    """Return nakshatra index (0-26) from sidereal longitude in degrees.
    Used by engine.kuta + other modules that need nakshatra lookup.
    """
    return int((float(longitude) % 360) // NAKSHATRA_SPAN)


def vimshottari(chart_or_moon, birth_dt=None):
    """Compute Vimshottari MD/AD timeline.

    Two signatures supported:
      vimshottari(chart_dict)                — preferred 1-arg form
      vimshottari(moon_longitude, birth_dt) — legacy 2-arg form (engine/backtest etc.)

    Returns list of dicts: {lord, start, end, years, age_from, age_to}.
    """
    if birth_dt is not None:
        # Legacy 2-arg form — synthesize a minimal chart dict
        moon_lon = float(chart_or_moon)
        if hasattr(birth_dt, "year"):
            b = {"year": birth_dt.year, "month": birth_dt.month, "day": birth_dt.day,
                 "hour": getattr(birth_dt, "hour", 12), "min": getattr(birth_dt, "minute", 0)}
        else:
            b = {"year": 2000, "month": 1, "day": 1, "hour": 0, "min": 0}
        chart = {"positions": {"Moon": {"lon": moon_lon, "lon_abs": moon_lon}}, "birth": b}
    else:
        chart = chart_or_moon
    timeline = _build_timeline(chart, levels=2)
    return [r for r in timeline if r.get("level") == 1]


class DasaPeriod(dict):
    @property
    def lord(self) -> str:
        level = self.get("level")
        if level == 1:
            return self.get("md")
        elif level == 2:
            return self.get("ad")
        elif level == 3:
            return self.get("pd")
        elif level == 4:
            return self.get("sd")
        return self.get("lord") or self.get("md") or self.get("ad")

    @property
    def start(self):
        return self.get("start")

    @property
    def end(self):
        return self.get("end")


class DashaResult(dict):
    def __iter__(self):
        yield self.get("md")
        yield self.get("ad")


def current_dasha(chart, when=None):
    """Find currently active MD/AD/PD at given date (default now)."""
    if when is None:
        when = dt.datetime.now()
    if isinstance(chart, list):
        # Fallback for legacy list-of-periods
        md_match = None
        for p in chart:
            if p.get("level") == 1 and p.get("start") <= when <= p.get("end"):
                md_match = p
                break
        if not md_match:
            # Maybe list of dictionaries with start/end but no level (e.g. from older vimshottari)
            for p in chart:
                if p.get("start") <= when <= p.get("end"):
                    md_match = p
                    break
        out = DashaResult()
        if md_match:
            out["md"] = DasaPeriod(md_match)
            # Dynamically construct AD timeline for this MD
            md_lord = md_match.get("md") or md_match.get("lord")
            md_start = md_match.get("start")
            md_end = md_match.get("end")
            if md_lord and md_start and md_end:
                md_duration = md_end - md_start
                try:
                    idx = VIMSHOTTARI_ORDER.index(md_lord)
                    current_start = md_start
                    for i in range(9):
                        ad_lord = VIMSHOTTARI_ORDER[(idx + i) % 9]
                        ad_fraction = VIMSHOTTARI_YEARS[ad_lord] / 120.0
                        ad_duration = md_duration * ad_fraction
                        current_end = current_start + ad_duration
                        if current_start <= when <= current_end:
                            out["ad"] = DasaPeriod({
                                "level": 2,
                                "md": md_lord,
                                "ad": ad_lord,
                                "start": current_start,
                                "end": current_end,
                            })
                            break
                        current_start = current_end
                except ValueError:
                    pass
        if "ad" not in out:
            out["ad"] = None
        return out

    timeline = _build_timeline(chart, levels=3)
    active = _lookup(timeline, when)
    out = DashaResult()
    for level, rec in active.items():
        key = ["", "md", "ad", "pd", "sd"][level]
        out[key] = DasaPeriod(rec) if rec else None
    return out


def full_timeline(chart, levels=4):
    """Full 4-level dasha timeline (passthrough)."""
    return _build_timeline(chart, levels=levels)


def ashtottari(chart):
    """Ashtottari Dasha (108-year alternative to Vimshottari).

    Bridges to runtime/other_dashas.py.
    """
    from other_dashas import compute_ashtottari
    return compute_ashtottari(chart)


def yogini(chart):
    """Yogini Dasha (36-year cycle, 8 yoginis)."""
    from other_dashas import compute_yogini
    return compute_yogini(chart)


def char(chart):
    """Char (Jaimini Rasi) Dasha."""
    from char_dasha import char_dasha
    return char_dasha(chart)


def kalachakra(chart):
    """Kalachakra Dasha (BPHS Ch.49 pada-based rasi dasha)."""
    from engine.kalachakra import kalachakra as compute_kc
    import datetime as dt
    pos = chart["positions"]
    moon = pos["Moon"]
    moon_lon = moon.get("lon_abs") or (moon.get("rasi_idx", 0) * 30 + moon.get("deg", 0))
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    return compute_kc(moon_lon, birth_dt)
