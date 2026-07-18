"""Tamil chapter-spine client report (parallel to client_report_v2)."""
from __future__ import annotations

from datetime import datetime

from engine.client_report import _cover_mandala_svg
from engine.chapters_ta import render_chapters_markdown_ta
from engine.client_report_v2 import (
    _section_life_map, _section_planetary_positions,
)
from engine.client_report_ta import (
    _section_birth_facts_ta, _section_personality_ta,
    _section_difficulties_ta, _section_strengths_ta,
    _section_planets_table_ta, _section_remedies_ta,
    _section_closing_ta,
)
from engine.narrative_ta import SIGNS_TA
from engine.jathagam_template import build_jathagam_full, build_prediction_section_header


def _section_cover_v2_ta(chart) -> str:
    name = (getattr(chart, "name", None) or "நண்பர்").upper()
    today = datetime.now().strftime("%d %B %Y")
    birth_dt = chart.birth_dt
    birth_str = birth_dt.strftime("%d %B %Y · %A · %-I:%M %p")
    place = getattr(chart, "place", "") or ""
    SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    lagna = SIGNS[int(chart.lagna_lon // 30)]
    moon = SIGNS[int(chart.positions["Moon"] // 30)]
    return (
        f"<div class='cover'>\n"
        f"<div class='cover-mandala'>{_cover_mandala_svg()}</div>\n"
        f"<div class='cover-title'>வேத ஜாதக வாசிப்பு</div>\n"
        f"<div class='cover-name'>{name}</div>\n"
        f"<div class='cover-divider'>✦ ❖ ✦</div>\n"
        f"<div class='cover-subtitle'>முழு வாழ்க்கை காலவரிசை</div>\n"
        f"<div class='cover-tagline'>— பிறப்பு முதல் வயது 100 வரை —</div>\n"
        f"<div class='cover-birth'>"
        f"<strong>பிறப்பு</strong><br/>{birth_str}<br/>{place}<br/><br/>"
        f"<span style='color:#7a1f3d'>லக்னம் · {SIGNS_TA.get(lagna, lagna)}</span>"
        f" &nbsp;|&nbsp; "
        f"<span style='color:#7a1f3d'>சந்திர ராசி · {SIGNS_TA.get(moon, moon)}</span>"
        f"</div>\n"
        f"<div class='cover-meta' style='margin-top:1.5cm'>தயாரிக்கப்பட்டது {today}</div>\n"
        f"<div class='cover-engine'>Engine v1.9 · 20 நூல்கள் · 14,795 சூத்திரங்கள் · எளிய தமிழ்</div>\n"
        f"</div>\n\n"
    )


def generate_client_report_v2_ta(chart) -> str:
    sections = [
        _section_cover_v2_ta(chart),
        build_jathagam_full(chart, "ta"),
        build_prediction_section_header("ta"),
        _section_life_map(chart),       # SVG dasha bar — language-neutral
        render_chapters_markdown_ta(chart),
        _section_difficulties_ta(chart),
        _section_strengths_ta(chart),
        _section_planets_table_ta(chart),
        _section_remedies_ta(chart),
        _section_closing_ta(chart),
    ]
    return "\n\n".join(sections)
