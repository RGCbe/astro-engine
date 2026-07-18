import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path

# Setup paths
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from src.services.jathagam_service import jathagam
from src.models.schemas import BirthData
from src.api.main import RASIS

async def fetch_chart():
    # Manoj birth details
    data = BirthData(
        year=1996, month=5, day=25, time="20:25",
        lat=11.0168, lon=76.9558, focus="general", lang="en"
    )
    res = await jathagam(data)
    
    pos_map = {}
    for p, d in res["all_planet_positions"].items():
        pos_map[p] = {
            "rasi": d["rasi"],
            "rasi_idx": RASIS.index(d["rasi"]),
            "nak": d["nakshatra"],
            "nak_lord": d["nakshatra_lord"],
            "pada": d["nakshatra_pada"],
            "house": d["house"],
            "deg": d["longitude"] % 30,
            "lon_abs": d["longitude"]
        }
    
    chart_dict = {
        "birth": {
            "year": data.year,
            "month": data.month,
            "day": data.day,
            "hour": int(data.time.split(":")[0]),
            "min": int(data.time.split(":")[1]),
            "lat": data.lat,
            "lon": data.lon,
            "place": "Coimbatore, TN",
            "weekday": res["panchangam"]["vara"]
        },
        "lagna": res["lagnam"],
        "lagna_idx": RASIS.index(res["lagnam"]),
        "ayanamsa": 23.8068,
        "positions": pos_map,
        "janma_nakshatra": res["janma_nakshatra"],
        "janma_nakshatra_lord": res["all_planet_positions"]["Moon"]["nakshatra_lord"],
        "moon_rasi": res["janma_rasi"],
        "name": "Manoj Kumar",
        "lagna_lord": res["rasi_lord"],
        "lagna_deg": res["all_planet_positions"]["Lagna"]["longitude"] % 30,
        "lagna_lon": res["all_planet_positions"]["Lagna"]["longitude"],
        "truth_report": res.get("truth_report"),
    }
    
    chart_file = os.path.join(_ROOT, "scratch", "test_manoj_chart.json")
    with open(chart_file, "w", encoding="utf-8") as f:
        json.dump(chart_dict, f, ensure_ascii=False, indent=2)
    print(f"Test chart written to {chart_file}")
    return chart_file

def run_generators(chart_file):
    generators = [
        ("generate_report.py", "MANOJ_TEST_EN.pdf"),
        ("generate_tamil_pdf.py", "MANOJ_TEST_TA.pdf"),
        ("generate_hindi_pdf.py", "MANOJ_TEST_HI.pdf")
    ]
    
    python_exe = sys.executable
    for script, out_name in generators:
        script_path = os.path.join(_ROOT, "runtime", script)
        out_path = os.path.join(_ROOT, "reports", out_name)
        cmd = [python_exe, script_path, "--chart", chart_file, "--out", out_path]
        print(f"Running: {' '.join(cmd)}")
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"  SUCCESS: Generated {out_path}")
        else:
            print(f"  FAIL: {script}\nStdout:\n{res.stdout}\nStderr:\n{res.stderr}")

async def main():
    chart_file = await fetch_chart()
    run_generators(chart_file)

if __name__ == "__main__":
    asyncio.run(main())
