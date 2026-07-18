"""
Engine Bridge — adapts runtime chart dict → engine.engines.* Chart object.

The runtime/ chart format stores positions as nested dicts:
    chart["positions"]["Sun"] = {"lon": 40.8, "rasi": "Taurus", "house": 6, ...}

The engine/engines/* code expects a Chart object with flat attributes:
    chart.positions["Sun"] = 40.8   (raw longitude)
    chart.lagna_lon = 245.23         (single number)
    chart.vargas = {"D9": {"positions": {...}, "lagna_lon": ...}, ...}

This bridge wraps a runtime dict to expose the engine-style attribute interface,
so the rich BPHS-cited typed engines (MarriageEngine, CareerEngine, ChildrenEngine,
WealthEngine, HealthEngine, etc.) can run on existing runtime charts WITHOUT
re-computing the chart from birth data.

Usage:
    from engine_bridge import to_engine_chart, run_engines

    e_chart = to_engine_chart(runtime_chart_dict)
    reports = run_engines(e_chart)  # list of CategoryReport
"""
from __future__ import annotations
import sys, os
from types import SimpleNamespace

# Make engine/ importable
_ATRO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ATRO_ROOT not in sys.path:
    sys.path.insert(0, _ATRO_ROOT)

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}


def _planet_lon(pdata):
    """Extract absolute longitude from a runtime position record."""
    lon = pdata.get("lon_abs") or pdata.get("lon")
    if lon is None and "rasi_idx" in pdata:
        lon = pdata["rasi_idx"] * 30 + pdata.get("deg", 0)
    return float(lon) if lon is not None else None


def _build_vargas(runtime_chart):
    """Compute D9/D10/D12/D60 divisional charts in engine-friendly dict format."""
    out = {}
    # D1 = natal chart (flat positions)
    d1_pos = {}
    for p, pd in runtime_chart["positions"].items():
        lon = _planet_lon(pd)
        if lon is not None:
            d1_pos[p] = lon
    lagna_lon = runtime_chart.get("lagna_lon")
    if lagna_lon is None:
        lagna_lon = runtime_chart["lagna_idx"] * 30 + runtime_chart.get("lagna_deg", 15.0)
    out["D1"] = {"positions": d1_pos, "lagna_lon": float(lagna_lon)}

    # D9, D10, D12, D60 — compute via runtime divisional_charts
    try:
        from divisional_charts import build_divisional_chart
        for v in ("D9", "D10", "D12", "D60"):
            try:
                d = build_divisional_chart(runtime_chart, varga=v)
                d_pos = {p: pd["rasi_idx"] * 30 + 15.0 for p, pd in d["positions"].items()}
                # divisional lagna sits at midpoint of new lagna sign
                d_lagna_lon = d["lagna_idx"] * 30 + 15.0
                out[v] = {"positions": d_pos, "lagna_lon": float(d_lagna_lon),
                          "lagna_sign": SIGNS[d["lagna_idx"]]}
            except Exception:
                pass
    except Exception:
        pass

    return out


def to_engine_chart(runtime_chart):
    """Convert runtime chart dict into an engine-compatible Chart-like object.

    Returns a SimpleNamespace with attributes the engine.engines.* modules expect:
        .name, .positions (flat dict), .lagna_lon, .lagna_sign, .lagna_lord,
        .vargas, .house_of, .vimshottari_periods (best-effort)
    """
    # Flat positions: {planet: longitude}
    positions = {}
    for p, pd in runtime_chart["positions"].items():
        lon = _planet_lon(pd)
        if lon is not None:
            positions[p] = lon

    # Lagna
    lagna_lon = runtime_chart.get("lagna_lon")
    if lagna_lon is None:
        lagna_lon = runtime_chart["lagna_idx"] * 30 + runtime_chart.get("lagna_deg", 15.0)
    lagna_lon = float(lagna_lon)
    lagna_idx = int(lagna_lon // 30)
    lagna_sign = SIGNS[lagna_idx]
    lagna_lord = SIGN_LORDS[lagna_sign]

    # House of each planet (whole-sign from lagna)
    house_of = {}
    for p, lon in positions.items():
        house_of[p] = ((int(lon // 30) - lagna_idx) % 12) + 1

    # Vargas
    vargas = _build_vargas(runtime_chart)

    # Vimshottari periods — engine/chapters expects objects with .lord/.start/.end attrs (not dicts)
    vimshottari_periods = []
    current_md = None
    current_ad = None
    current_md_end = None
    try:
        import datetime as _dt
        from granular_dasha import build_full_timeline, lookup
        tl = build_full_timeline(runtime_chart, levels=2)
        for r in tl:
            if r.get("level") == 1:
                vimshottari_periods.append(SimpleNamespace(
                    lord=r["md"], start=r["start"], end=r["end"],
                    years=r["years"],
                ))
        # Look up active dasha NOW
        ds = lookup(tl, _dt.datetime.now())
        if 1 in ds:
            current_md = ds[1].get("md")
            current_md_end = ds[1]["end"]
        if 2 in ds:
            current_ad = ds[2].get("ad")
    except Exception:
        pass

    # Nakshatras dict — {planet: {nakshatra, lord, pada}} — needed by personality + health engines
    nakshatras = {}
    for p, pd in runtime_chart["positions"].items():
        nak = pd.get("nak") or pd.get("nakshatra")
        nak_lord = pd.get("nak_lord")
        pada = pd.get("pada")
        if nak:
            nakshatras[p] = {"nakshatra": nak, "lord": nak_lord, "pada": pada}

    # Birth datetime — needed by timeline engine
    birth_dt = None
    try:
        import datetime as _dt
        b = runtime_chart["birth"]
        birth_dt = _dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    except Exception:
        pass

    e_chart = SimpleNamespace(
        name=runtime_chart.get("name", "unknown"),
        positions=positions,
        lagna_lon=lagna_lon,
        lagna_sign=lagna_sign,
        lagna_lord=lagna_lord,
        vargas=vargas,
        house_of=house_of,
        nakshatras=nakshatras,
        vimshottari_periods=vimshottari_periods,
        current_md=current_md,
        current_ad=current_ad,
        current_md_end=current_md_end,
        birth_dt=birth_dt,
        # Add raw runtime reference for engines that may peek
        _runtime=runtime_chart,
    )
    return e_chart


def run_engines(e_chart, only=None):
    """Run engine.engines.orchestrator.run_all() and return CategoryReport list."""
    try:
        from engine.engines.orchestrator import run_all
        return run_all(e_chart, only=only)
    except Exception as e:
        return [SimpleNamespace(category="error", title="Engine error",
                                 predictions=[], notes=[f"engine.engines.run_all failed: {e}"])]


def reports_to_dict(reports):
    """Convert CategoryReport list → dict keyed by category, predictions flattened."""
    out = {}
    for r in reports:
        cat = getattr(r, "category", "unknown")
        preds = []
        for p in getattr(r, "predictions", []):
            preds.append({
                "key": getattr(p, "key", ""),
                "label": getattr(p, "label", ""),
                "value": getattr(p, "value", None),
                "confidence": getattr(p, "confidence", "MEDIUM"),
                "evidence": getattr(p, "chart_evidence", ""),
                "citations": [
                    {"book": getattr(c, "book", ""), "verse_id": getattr(c, "verse_id", ""),
                     "text": getattr(c, "text", "")}
                    for c in getattr(p, "citations", [])
                ],
            })
        out[cat] = {
            "title": getattr(r, "title", cat),
            "predictions": preds,
            "notes": getattr(r, "notes", []),
        }
    return out


if __name__ == "__main__":
    import json, sys
    sys.stdout.reconfigure(encoding="utf-8")
    from pathlib import Path
    chart = json.load(open(Path("../charts/sachin_tendulkar_chart.json")))
    e = to_engine_chart(chart)
    print(f"Adapted chart for {e.name}")
    print(f"  lagna_lon = {e.lagna_lon}  lagna_sign = {e.lagna_sign}")
    print(f"  positions: {len(e.positions)} planets")
    print(f"  vargas computed: {list(e.vargas.keys())}")
    print(f"  vimshottari periods: {len(e.vimshottari_periods)}")
    print()
    reports = run_engines(e)
    print(f"Engines ran: {len(reports)} CategoryReports")
    for r in reports:
        cat = getattr(r, "category", "?")
        title = getattr(r, "title", "?")
        preds = getattr(r, "predictions", [])
        notes = getattr(r, "notes", [])
        print(f"  [{cat:<15}] {title:<35}  predictions={len(preds)}  notes={len(notes)}")
        if notes and "error" in str(notes[0]).lower():
            print(f"      ERROR: {notes[0][:120]}")
