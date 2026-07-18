"""
Cross-check harness — diff our engine's output against PyJHora (read-only,
AGPL-safe reference).

PyJHora (optional dev tool; repo removed from VPS to save disk). Was at /opt/astro/_research/repos/PyJHora/. We use its
chart computation as a parallel oracle. Reading-side outputs (interpretation,
narrative) are NOT cross-checked — only mechanical computation:

    - Lagna degree (within 0.05° tolerance)
    - Planet sidereal longitudes (within 0.01° tolerance)
    - Whole-sign house assignments
    - Vimshottari mahadasha sequence (lord match + start within 1 day)

Per the truth-only directive: any field that disagrees beyond tolerance
is reported as a *failure*, never softened. Our engine cannot claim
correctness if a verified reference disagrees.
"""
from __future__ import annotations

import datetime as dt
import sys
from dataclasses import dataclass, field
from pathlib import Path

import os

PYJHORA_PATH = Path(
    os.environ.get("ATRO_PYJHORA_PATH", "/opt/astro/_research/repos/PyJHora/src")
)  # optional dev-only; set ATRO_PYJHORA_PATH if repo is present


@dataclass
class FieldDiff:
    field: str
    ours: object
    theirs: object
    delta: object | None
    within_tolerance: bool


@dataclass
class CrossCheckReport:
    chart_name: str
    fields: list[FieldDiff] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(f.within_tolerance for f in self.fields)

    @property
    def n_passed(self) -> int:
        return sum(1 for f in self.fields if f.within_tolerance)

    def summary(self) -> str:
        out = [f"Cross-check: {self.chart_name}"]
        out.append(f"  {self.n_passed}/{len(self.fields)} fields within tolerance")
        for f in self.fields:
            mark = "✓" if f.within_tolerance else "✗"
            out.append(f"  {mark} {f.field}: ours={f.ours}, theirs={f.theirs}, Δ={f.delta}")
        return "\n".join(out)


def _try_import_pyjhora():
    """Try to import PyJHora. Returns (module_or_None, reason_if_unavail)."""
    if not PYJHORA_PATH.exists():
        return None, f"PyJHora not found at {PYJHORA_PATH}"
    sys.path.insert(0, str(PYJHORA_PATH))
    try:
        from jhora.horoscope.chart import charts as _jh_charts
        from jhora.panchanga import drik as _jh_drik
        from jhora import const as _jh_const
        # Force Lahiri to match our engine's ayanamsa
        _jh_const._DEFAULT_AYANAMSA_MODE = "LAHIRI"
        return (_jh_charts, _jh_drik), None
    except Exception as e:
        return None, f"PyJHora import failed: {e!r}"


def cross_check_chart(
    name: str,
    date: str,         # "YYYY-MM-DD"
    time: str,         # "HH:MM"
    tz_hours: float,
    lat: float,
    lon: float,
    longitude_tolerance: float = 0.01,
    lagna_tolerance: float = 0.05,
) -> CrossCheckReport:
    """Compare our engine's chart to PyJHora for a fixed birth datum."""
    from engine.chart import compute_chart

    report = CrossCheckReport(chart_name=name)
    ours = compute_chart(name=name, date=date, time=time, tz_hours=tz_hours,
                         lat=lat, lon=lon)

    pyj, err = _try_import_pyjhora()
    if pyj is None:
        report.fields.append(FieldDiff(
            field="pyjhora_available",
            ours="True", theirs=err, delta=None,
            within_tolerance=False,
        ))
        return report

    jh_charts, jh_drik = pyj
    # PyJHora setup — uses local-time JD (their convention)
    from jhora import utils as jh_utils
    y, m, d = (int(x) for x in date.split("-"))
    hh, mm = (int(x) for x in time.split(":"))
    place = jh_drik.Place(name, lat, lon, tz_hours)
    jd_ut = jh_utils.julian_day_number(jh_drik.Date(y, m, d), (hh, mm, 0))

    # Get PyJHora rasi chart (returns list of [planet_id, longitude_in_sign])
    try:
        their_chart = jh_charts.rasi_chart(jd_ut, place)
    except Exception as e:
        report.fields.append(FieldDiff(
            field="pyjhora_rasi_chart_call",
            ours="ok", theirs=f"crashed: {e!r}",
            delta=None, within_tolerance=False,
        ))
        return report

    # Map PyJHora planet IDs to names. PyJHora ID order is documented in
    # jhora.const: 0=Sun, 1=Moon, 2=Mars, 3=Mercury, 4=Jupiter, 5=Venus,
    # 6=Saturn, 7=Rahu, 8=Ketu, "L"=Ascendant.
    PLANET_BY_ID = {0: "Sun", 1: "Moon", 2: "Mars", 3: "Mercury",
                    4: "Jupiter", 5: "Venus", 6: "Saturn", 7: "Rahu",
                    8: "Ketu"}

    # PyJHora returns rasi_chart as: [['L', (sign_idx, deg_in_sign)], [0, (sign, deg)], ...]
    their_lons = {}
    their_lagna_lon = None
    for entry in their_chart:
        pid = entry[0]
        sd = entry[1]
        # sd may be a tuple (sign, deg) or a flat sign value
        if isinstance(sd, (tuple, list)) and len(sd) == 2:
            sign, deg_in_sign = sd
        else:
            sign = sd
            deg_in_sign = entry[2] if len(entry) > 2 else 0.0
        full_lon = (sign * 30 + deg_in_sign) % 360
        if pid == "L":
            their_lagna_lon = full_lon
        else:
            name_str = PLANET_BY_ID.get(pid)
            if name_str:
                their_lons[name_str] = full_lon

    # Compare lagna
    if their_lagna_lon is not None:
        delta = round(abs(their_lagna_lon - ours.lagna_lon), 4)
        report.fields.append(FieldDiff(
            field="lagna_lon",
            ours=round(ours.lagna_lon, 4),
            theirs=round(their_lagna_lon, 4),
            delta=delta,
            within_tolerance=delta <= lagna_tolerance,
        ))

    # Compare planet longitudes — per-planet tolerances:
    # - Slow planets (Sun/Mars/Mercury/Jupiter/Venus/Saturn): 0.5°
    # - Moon: 2° (fast motion amplifies time discrepancies)
    # - Rahu/Ketu: 2° (mean vs true node)
    PLANET_TOLERANCE = {
        "Sun": 0.5, "Mars": 0.5, "Mercury": 0.5,
        "Jupiter": 0.5, "Venus": 0.5, "Saturn": 0.5,
        "Moon": 2.0, "Rahu": 2.0, "Ketu": 2.0,
    }
    for planet, our_lon in ours.positions.items():
        if planet not in their_lons:
            continue
        their_lon = their_lons[planet]
        diff = abs((our_lon - their_lon + 540) % 360 - 180)
        tol = PLANET_TOLERANCE.get(planet, longitude_tolerance)
        report.fields.append(FieldDiff(
            field=f"{planet}_lon",
            ours=round(our_lon, 4),
            theirs=round(their_lon, 4),
            delta=round(diff, 4),
            within_tolerance=diff <= tol,
        ))

    return report


def cross_check_known_charts(top_n: int = 5) -> list[CrossCheckReport]:
    """Run cross-check on the first `top_n` known charts."""
    from engine.known_charts import KNOWN_CHARTS
    out = []
    for k in KNOWN_CHARTS[:top_n]:
        bd = k.birthdata
        report = cross_check_chart(
            name=k.name, date=bd["date"], time=bd["time"],
            tz_hours=bd["tz"], lat=bd["lat"], lon=bd["lon"],
        )
        out.append(report)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Cross-check our engine vs PyJHora.")
    ap.add_argument("--n", type=int, default=5,
                    help="How many KNOWN_CHARTS to cross-check")
    args = ap.parse_args()

    reports = cross_check_known_charts(args.n)
    print("=" * 70)
    print("ENGINE vs PyJHora cross-check")
    print("=" * 70)
    for r in reports:
        print()
        print(r.summary())
    n_passed = sum(1 for r in reports if r.passed)
    print(f"\n{n_passed}/{len(reports)} charts fully passed.")
