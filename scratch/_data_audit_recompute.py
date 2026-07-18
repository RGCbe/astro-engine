"""One-off lagna/planet recompute vs stored charts/*.json"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from engine.chart_builder import build_sidereal_chart

RASIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

charts = [
    ("mukesh_ambani", 1957, 4, 19, "06:56", 12.7855, 45.0187, 3.0),
    ("mahatma_gandhi", 1869, 10, 2, "07:33", 21.6417, 69.6293, 4.62),
    ("indira_gandhi", 1917, 11, 19, "23:11", 25.4358, 81.8463, 5.5),
    ("narendra_modi", 1950, 9, 17, "11:00", 23.7936, 72.6376, 5.5),
    ("sachin_tendulkar", 1973, 4, 24, "13:00", 18.9667, 72.8333, 5.5),
]

for slug, y, m, d, t, lat, lon, tz in charts:
    p = ROOT / "charts" / f"{slug}_chart.json"
    stored = json.loads(p.read_text(encoding="utf-8"))
    core = build_sidereal_chart(y, m, d, t, lat, lon, tz)
    calc_idx = int(core["asc_sid"] / 30) % 12
    stored_idx = stored["lagna_idx"]
    calc_deg = core["asc_sid"] % 30
    stored_deg = stored.get("lagna_deg", 0)
    deg_diff = abs(calc_deg - stored_deg)
    ok = calc_idx == stored_idx and deg_diff < 0.05
    status = "OK" if ok else "MISMATCH"
    print(
        f"{status} {slug}: stored {stored['lagna']} ({stored_deg:.4f}) "
        f"calc {RASIS[calc_idx]} ({calc_deg:.4f}) deg_diff={deg_diff:.4f}"
    )
    for planet in ("Sun", "Moon", "Mars"):
        s_lon = stored["positions"][planet]["lon_abs"]
        c_lon = core["planet_positions"][planet]["longitude"]
        if abs(s_lon - c_lon) > 0.05:
            print(f"  {planet} lon mismatch stored={s_lon:.4f} calc={c_lon:.4f}")
