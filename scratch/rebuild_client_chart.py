# -*- coding: utf-8 -*-
"""Rebuild charts/*.json positions from chart_builder (Thirukanitham default for TN)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.chart_builder import RULES, RASIS, build_sidereal_chart  # noqa: E402

RASI_EN = {k: v.get("english", k) for k, v in RULES["rasi_descriptions"].items()}


def rebuild(path: Path) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    b = data["birth"]
    tz = float(b.get("tz", b.get("tz_hours", 5.5)))
    core = build_sidereal_chart(
        b["year"],
        b["month"],
        b["day"],
        f"{b['hour']:02d}:{b['min']:02d}",
        float(b["lat"]),
        float(b["lon"]),
        tz,
    )
    pp = core["planet_positions"]
    data["ayanamsa"] = core["ayanamsa"]
    data["ayanamsa_mode"] = core["ayanamsa_mode"]
    data["ayanamsa_name"] = core["ayanamsa_name"]
    data["lagna"] = RASI_EN.get(core["lagnam_rasi"], core["lagnam_rasi"])
    data["lagna_idx"] = int(core["asc_sid"] / 30) % 12
    data["lagna_lon"] = round(core["asc_sid"], 4)
    data["lagna_deg"] = round(core["asc_sid"] % 30, 4)
    if data.get("janma_nakshatra") is None:
        data["janma_nakshatra"] = core["janma_nakshatra"]
    if data.get("moon_rasi") is None:
        data["moon_rasi"] = core["janma_rasi"]

    positions = {}
    for pname, pd in pp.items():
        if pname == "Lagna":
            continue
        lon = pd["longitude"]
        rasi_idx = int(lon / 30) % 12
        nav_en = RASI_EN.get(pd.get("navamsa_rasi", ""), pd.get("navamsa_rasi", ""))
        positions[pname] = {
            "lon": round(lon, 4),
            "lon_abs": round(lon, 4),
            "rasi": RASI_EN.get(pd["rasi"], pd["rasi"]),
            "rasi_idx": rasi_idx,
            "nak": pd.get("nakshatra", ""),
            "nak_lord": pd.get("nakshatra_lord", ""),
            "pada": pd.get("nakshatra_pada", 1),
            "house": pd["house"],
            "deg": round(lon % 30, 4),
            "navamsa_rasi": nav_en,
        }
    data["positions"] = positions
    data["upagrahas"] = {
        k: positions[k] for k in ("Mandi", "Gulika") if k in positions
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK {path.name} ayanamsa={core['ayanamsa']} mode={core['ayanamsa_mode']} lagna={core['lagnam_rasi']}")


if __name__ == "__main__":
    targets = [Path(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else [ROOT / "charts" / "manoj_chart.json"]
    for p in targets:
        rebuild(p.resolve())
