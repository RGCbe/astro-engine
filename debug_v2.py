import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from engine.chart import compute_chart
from engine.client_report_v2 import (
    _section_cover_v2,
    build_jathagam_full,
    build_prediction_section_header,
    _section_life_map,
    _section_defining_yogas,
    _section_chart_at_a_glance,
    _section_planetary_positions,
    _section_chapters_full,
    _section_ten_themes,
    _section_life_arcs,
    _section_remedies,
    _section_classical_appendix,
    _section_closing,
)

def main():
    print("Computing chart...")
    chart = compute_chart(
        name="Manoj Kumar",
        date="1996-05-25",
        time="20:25",
        tz_hours=5.5,
        place="Coimbatore",
        lat=11.25,
        lon=77.12
    )
    
    print("Running _section_cover_v2...")
    _section_cover_v2(chart)
    print("Running build_jathagam_full...")
    build_jathagam_full(chart, "en")
    print("Running build_prediction_section_header...")
    build_prediction_section_header("en")
    print("Running _section_life_map...")
    _section_life_map(chart)
    print("Running _section_defining_yogas...")
    _section_defining_yogas(chart)
    print("Running _section_chart_at_a_glance...")
    _section_chart_at_a_glance(chart)
    print("Running _section_planetary_positions...")
    _section_planetary_positions(chart)
    print("Running _section_chapters_full...")
    _section_chapters_full(chart)
    print("Running _section_ten_themes...")
    _section_ten_themes(chart)
    print("Running _section_life_arcs...")
    _section_life_arcs(chart)
    print("Done!")
        
if __name__ == '__main__':
    main()
