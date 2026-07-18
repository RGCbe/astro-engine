import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.chart_builder import build_sidereal_chart
from engine.education import render_education_markdown, predict_subjects

with open("charts/manoj_chart.json", "r", encoding="utf-8") as f:
    chart_data = json.load(f)

# Build a chart object that matches what predict_subjects expects.
# predict_subjects expects:
#   chart.positions -> dict of planet: longitude (0-360)
#   chart.lagna_lon -> longitude of lagna (0-360)
#   chart.vargas -> D24: {planet: sign}

class MockChart:
    def __init__(self, data):
        self.positions = {}
        for p, d in data["positions"].items():
            self.positions[p] = d["lon"]
        self.lagna_lon = data["lagna_lon"]
        
        # Let's get D24 sign placements
        # To compute D24, we would normally calculate vargas. We can do that or mock it.
        # Let's check how F:\astro\engine\vargas.py or runtime/divisional_charts.py computes D24.
        # But we can calculate it manually for D24:
        # D24 division is 30 / 24 = 1.25 degrees per division.
        # If rasi is odd, the count starts from Leo (rasi_idx 4).
        # If rasi is even, the count starts from Cancer (rasi_idx 3).
        # Let's write D24 logic to populate chart.vargas["D24"].
        self.vargas = {"D24": {}}
        SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                 "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        for p, d in data["positions"].items():
            long_val = d["lon"]
            rasi_idx = int(long_val // 30)
            deg_in_rasi = long_val % 30
            d24_div = int(deg_in_rasi // 1.25) # 0 to 23
            
            # odd/even rasi
            is_odd = (rasi_idx % 2 == 0) # Aries=0 (odd), Taurus=1 (even)
            # wait, in python 0-indexed: Aries is 0 (first sign, odd), Taurus is 1 (second, even)
            # wait! Rasi index in BPHS: Aries is 1 (odd), Taurus is 2 (even).
            # So if rasi_idx is even (0, 2, 4, ...), it is Aries (1), Gemini (3), Leo (5)... which are odd signs!
            # If rasi_idx is odd (1, 3, 5, ...), it is Taurus (2), Virgo (6), Scorpio (8)... which are even signs!
            if rasi_idx % 2 == 0:
                # Odd sign: start from Leo (rasi_idx 4)
                d24_sign_idx = (4 + d24_div) % 12
            else:
                # Even sign: start from Cancer (rasi_idx 3)
                d24_sign_idx = (3 + d24_div) % 12
            
            self.vargas["D24"][p] = SIGNS[d24_sign_idx]

mock_chart = MockChart(chart_data)
subjects = predict_subjects(mock_chart, top_n=50)

print("=== EDUCATION PREDICTIONS ===")
for i, s in enumerate(subjects, 1):
    print(f"{i:2d}. {s.field:<30} (score: {s.score:.2f})")
    print(f"    Sources: {s.sources}")

print("\n=== MARKDOWN RENDER ===")
try:
    print(render_education_markdown(mock_chart).replace("✦", "*"))
except Exception as e:
    print(f"Error printing markdown: {e}")
