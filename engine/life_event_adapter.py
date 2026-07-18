"""Life-event adapter: run a horizon-limited event scan and fuse it for the API.

Bridges the jathagam service to runtime/event_predictor_v2 + engine.event_fusion:

  1. Build the predictor chart shape from the service's computed positions.
  2. Scan a short horizon around today (a full 85-year scan is backtest-only;
     the client-facing question is "what is coming", and a 5-year scan runs in
     well under a second).
  3. Fuse with the classical convergence gate and return the fused events for
     `build_truth_report(response, life_events=...)`.

Any failure raises to the caller, which reports `life_event` as unavailable —
this adapter must never fabricate output.
"""
from __future__ import annotations

import os
import sys
import datetime as _dt
from typing import Any, Mapping

from engine.event_fusion import fuse_events

_RASIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
          "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
_SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
               "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
_SEVEN = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")


def _ensure_runtime_importable() -> None:
    """runtime/ modules use flat imports; make them resolvable (bridge pattern)."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    runtime_dir = os.path.join(root, "runtime")
    if runtime_dir not in sys.path:
        sys.path.insert(0, runtime_dir)


def build_predictor_chart(
    *,
    birth: Mapping[str, Any],
    planet_positions: Mapping[str, Mapping[str, Any]],
    lagna_idx: int,
    lagna_lord: str = "",
    name: str = "client",
) -> dict[str, Any]:
    """Convert service-computed positions into the event predictor's chart shape."""
    positions: dict[str, dict[str, Any]] = {}
    for planet in _SEVEN:
        data = planet_positions.get(planet)
        if not data:
            continue
        lon_abs = float(data.get("longitude", 0.0)) % 360
        rasi = data.get("rasi") or _RASIS[int(lon_abs // 30) % 12]
        rasi_idx = _RASIS.index(rasi) if rasi in _RASIS else int(lon_abs // 30) % 12
        positions[planet] = {
            "rasi": _RASIS[rasi_idx],
            "rasi_idx": rasi_idx,
            "deg": round(lon_abs % 30, 4),
            "lon_abs": round(lon_abs, 4),
            "house": int(data.get("house") or ((rasi_idx - lagna_idx) % 12) + 1),
            "nak": data.get("nakshatra", ""),
            "nak_lord": data.get("nakshatra_lord", ""),
            "retrograde": bool(data.get("retrograde", False)),
        }
    return {
        "name": name,
        "birth": dict(birth),
        "lagna_idx": int(lagna_idx),
        "lagna": _RASIS[int(lagna_idx) % 12],
        "lagna_lord": lagna_lord or _SIGN_LORDS[int(lagna_idx) % 12],
        "positions": positions,
    }


def fused_life_events_for_horizon(
    chart: Mapping[str, Any],
    *,
    years_back: int = 1,
    years_forward: int = 3,
    min_severity: int = 2,
) -> list[dict[str, Any]]:
    """Scan [today-years_back, today+years_forward] and return fused events."""
    _ensure_runtime_importable()
    from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive

    year_now = _dt.date.today().year
    raw = scan_lifetime_v2(
        chart, year_now - years_back, year_now + years_forward, min_severity=min_severity
    )
    bands = collapse_consecutive(raw) if raw else []
    return fuse_events(bands)
