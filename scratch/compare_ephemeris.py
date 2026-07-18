# -*- coding: utf-8 -*-
"""Compare Swiss Ephemeris vs NASA JPL Horizons (DE) at one birth instant.

Uses Horizons VECTORS, Earth geocenter (500@399), ecliptic J2000 XYZ -> longitude.
Swiss uses apparent geocentric ecliptic of date (small frame difference possible).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import swisseph as swe  # noqa: E402

HORIZONS_BODIES = {
    "Sun": "10",
    "Moon": "301",
    "Mercury": "199",
    "Venus": "299",
    "Mars": "499",
    "Jupiter": "599",
    "Saturn": "699",
}

SWE_BODIES = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
}


def birth_jd(chart: dict) -> tuple[float, str]:
    b = chart["birth"]
    tz = float(b.get("tz", 5.5))
    ut_hours = b["hour"] + b["min"] / 60.0 - tz
    jd = swe.julday(b["year"], b["month"], b["day"], ut_hours)
    y, m, d, h = swe.revjul(jd)
    hh = int(h)
    mm = int((h % 1) * 60)
    ss = int(round(((h % 1) * 60 - mm) * 60))
    if ss >= 60:
        ss, mm = 0, mm + 1
    if mm >= 60:
        mm, hh = 0, hh + 1
    utc_str = f"{y:04d}-{m:02d}-{d:02d} {hh:02d}:{mm:02d}:{ss:02d}"
    return jd, utc_str


def swiss_tropical_lons(jd: float) -> dict[str, float]:
    out = {}
    for name, pid in SWE_BODIES.items():
        xx, _ = swe.calc_ut(jd, pid)
        out[name] = float(xx[0]) % 360.0
    return out


def _xyz_line_to_lon(line: str) -> float | None:
    if " X =" not in line and " X=" not in line:
        return None
    x = y = None
    for token in line.replace("=", " ").split():
        try:
            v = float(token)
        except ValueError:
            continue
        if x is None:
            x = v
        elif y is None:
            y = v
            break
    if x is None or y is None:
        return None
    return math.degrees(math.atan2(y, x)) % 360.0


def horizons_ecliptic_lon(jd: float, cmd: str) -> float:
    params = {
        "format": "text",
        "COMMAND": cmd,
        "EPHEM_TYPE": "VECTORS",
        "CENTER": "500@399",
        "START_TIME": f"'JD {jd}'",
        "STOP_TIME": f"'JD {jd + 0.001}'",
        "STEP_SIZE": "'1 m'",
        "REF_PLANE": "ECLIPTIC",
        "REF_SYSTEM": "J2000",
        "QUANTITIES": "'1'",
        "OUT_UNITS": "'AU-D'",
    }
    url = "https://ssd.jpl.nasa.gov/api/horizons.api?" + urlencode(params)
    with urlopen(url, timeout=120) as resp:
        text = resp.read().decode("utf-8", errors="replace")
    if "$$SOE" not in text:
        raise RuntimeError(text[-600:])
    block = text.split("$$SOE")[1].split("$$EOE")[0]
    for line in block.splitlines():
        lon = _xyz_line_to_lon(line)
        if lon is not None:
            return lon
    raise RuntimeError(f"No XYZ in Horizons block for cmd={cmd}")


def horizons_tropical_lons(jd: float) -> dict[str, float]:
    out = {}
    for name, cmd in HORIZONS_BODIES.items():
        out[name] = horizons_ecliptic_lon(jd, cmd)
    return out


def arcmin_diff(a: float, b: float) -> float:
    d = (a - b + 180) % 360 - 180
    return abs(d) * 60.0


def main() -> None:
    chart_path = ROOT / "charts" / "manoj_chart.json"
    if len(sys.argv) > 1:
        chart_path = Path(sys.argv[1])
    chart = json.loads(chart_path.read_text(encoding="utf-8"))
    b = chart["birth"]
    jd, utc_str = birth_jd(chart)
    print(f"Chart: {chart.get('name', chart_path.name)}")
    print(
        f"Birth local: {b['year']}-{b['month']:02d}-{b['day']:02d} "
        f"{b['hour']:02d}:{b['min']:02d} IST (tz={b.get('tz', 5.5)})"
    )
    print(f"UTC (UT): {utc_str}  |  JD = {jd:.10f}")
    print("Swiss: geocentric apparent ecliptic (of date)")
    print("Horizons: Earth-centered vector, ecliptic J2000 (NASA DE)")
    print()
    sw = swiss_tropical_lons(jd)
    print("Fetching JPL Horizons (7 bodies, ~1 API call each)...")
    hz = horizons_tropical_lons(jd)
    print()
    hdr = f"{'Body':<10} {'Swiss_deg':>12} {'JPL_deg':>12} {'diff_arcmin':>12}"
    print(hdr)
    print("-" * len(hdr))
    max_diff = 0.0
    for name in HORIZONS_BODIES:
        dmin = arcmin_diff(sw[name], hz[name])
        max_diff = max(max_diff, dmin)
        print(f"{name:<10} {sw[name]:12.6f} {hz[name]:12.6f} {dmin:12.4f}")
    print("-" * len(hdr))
    print(f"Max abs diff = {max_diff:.4f} arcmin ({max_diff / 60:.6f} deg)")
    print()
    if max_diff < 1.0:
        print("Verdict: Swiss matches JPL DE to sub-degree; no gain from replacing Swiss.")
    elif max_diff < 5.0:
        print("Verdict: Tiny frame/light-time differences only; still far below ayanamsa/birth-time effects.")
    else:
        print("Verdict: Investigate frame (J2000 vs of-date) or time scale (UT vs TDB).")


if __name__ == "__main__":
    main()
