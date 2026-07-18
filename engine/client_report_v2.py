"""
Timeline-first client report (sree.pdf-style).

Spine of the report = the 9 Vimshottari maha-dasha chapters. Each
chapter is self-contained: 3-column header → narrative intro →
EXPECT (events with time) → WATCH (risks with time) → antardasha
sub-period bullets with concrete date windows.

Front matter: cover, life-map, defining yogas, planetary positions,
chart at a glance.
Back matter: ten life themes (karmic patterns), life arcs (wealth /
health / marriage at a glance), classical sources appendix, closing.
"""
from __future__ import annotations

from datetime import datetime

from engine.client_report import (
    _section_birth_facts, _section_personality, _section_planets_table,
    _section_classical_appendix, _section_closing, _section_remedies,
    _cover_mandala_svg,
)
from engine.chapters import build_chapters
from engine.jathagam_template import build_jathagam_full, build_prediction_section_header


SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]


def _section_cover_v2(chart) -> str:
    name = (getattr(chart, "name", None) or "Friend").upper()
    today = datetime.now().strftime("%d %B %Y")
    birth_dt = chart.birth_dt
    birth_str = birth_dt.strftime("%d %B %Y · %A · %I:%M %p")
    place = getattr(chart, "place", "") or ""
    lagna = SIGNS[int(chart.lagna_lon // 30)]
    moon = SIGNS[int(chart.positions["Moon"] // 30)]
    return (
        f"<div class='cover'>\n"
        f"<div class='cover-mandala'>{_cover_mandala_svg()}</div>\n"
        f"<div class='cover-title'>VEDIC LIFE READING</div>\n"
        f"<div class='cover-name'>{name}</div>\n"
        f"<div class='cover-divider'>✦ ❖ ✦</div>\n"
        f"<div class='cover-subtitle'>Complete Life Timeline</div>\n"
        f"<div class='cover-tagline'>— from birth to centenarian potential —</div>\n"
        f"<div class='cover-birth'>"
        f"<strong>BIRTH</strong><br/>{birth_str}<br/>{place}<br/><br/>"
        f"<span style='color:#7a1f3d'>Lagna · {lagna.upper()}</span>"
        f" &nbsp;|&nbsp; "
        f"<span style='color:#7a1f3d'>Moon · {moon.upper()}</span>"
        f"</div>\n"
        f"<div class='cover-meta' style='margin-top:1.5cm'>Prepared {today}</div>\n"
        f"<div class='cover-engine'>Atro Engine v1.7 · 20 books · 14,795 rules · timeline-first format</div>\n"
        f"</div>\n\n"
    )


def _section_life_map(chart) -> str:
    """SVG horizontal life map showing all 9 dashas + current marker."""
    chapters = build_chapters(chart)
    if not chapters:
        return ""
    total_years = chapters[-1].age_end - chapters[0].age_start
    if total_years <= 0:
        total_years = 117
    out = ["## ✦ THE LIFE MAP\n"]
    out.append(
        f"*Nine periods · ~{total_years} years projected · current "
        "position marked.*"
    )
    out.append("")
    # Build SVG bar
    width = 700; height = 70
    parts = ["<svg viewBox='0 0 {w} {h}' xmlns='http://www.w3.org/2000/svg' "
             "style='width:100%;max-width:18cm;display:block;margin:0 auto;'>".format(w=width, h=height)]
    PLANET_COLORS = {
        "Sun": "#d4831f", "Moon": "#9aa9c2", "Mars": "#a82a2a",
        "Mercury": "#1f7a4d", "Jupiter": "#c8a13a",
        "Venus": "#cc6f9b", "Saturn": "#3a3a4a",
        "Rahu": "#5a3d8a", "Ketu": "#7a4a3a",
    }
    x0 = 0
    for ch in chapters:
        span = (ch.age_end - ch.age_start) / total_years * width
        color = PLANET_COLORS.get(ch.planet, "#888")
        parts.append(
            f"<rect x='{x0:.1f}' y='15' width='{span:.1f}' height='30' "
            f"fill='{color}' stroke='#fdf8ed' stroke-width='1'/>"
        )
        # planet label inside
        parts.append(
            f"<text x='{x0+span/2:.1f}' y='35' text-anchor='middle' "
            f"font-size='10' fill='#fff' font-family='Cinzel, serif'>"
            f"{ch.planet[:3]}</text>"
        )
        # age tick
        parts.append(
            f"<text x='{x0:.1f}' y='62' font-size='9' fill='#7a1f3d' "
            f"font-family='Lora, serif'>{ch.age_start}</text>"
        )
        if ch.is_current:
            cx = x0 + span / 2
            parts.append(
                f"<polygon points='{cx:.1f},6 {cx-5:.1f},14 {cx+5:.1f},14' "
                f"fill='#7a1f3d'/>"
                f"<text x='{cx:.1f}' y='4' text-anchor='middle' "
                f"font-size='8' font-weight='bold' fill='#7a1f3d'>NOW</text>"
            )
        x0 += span
    parts.append(
        f"<text x='{width:.1f}' y='62' text-anchor='end' font-size='9' "
        f"fill='#7a1f3d'>{chapters[-1].age_end}</text>"
    )
    parts.append("</svg>")
    out.append("".join(parts))
    out.append("")
    return "\n".join(out)


def _section_defining_yogas(chart) -> str:
    out = ["## ✦ THE YOGAS THAT DEFINE THIS LIFE\n"]
    out.append("*Special configurations active across every period.*")
    out.append("")
    seen = set()
    try:
        from engine.blessings import detect_all
        for b in detect_all(chart)[:6]:
            if b.name in seen:
                continue
            seen.add(b.name)
            badge = "**CANONICAL**" if b.strength == "SUPREME" else "**STRONG**"
            out.append(f"### {b.name}")
            out.append(f"{badge}  ·  *{b.evidence}*")
            out.append("")
            out.append(b.description)
            out.append("")
    except Exception:
        pass
    try:
        from engine.yogas_extended import detect_all_extended
        for b in detect_all_extended(chart)[:3]:
            if b.valence != "GOOD" or b.name in seen:
                continue
            seen.add(b.name)
            out.append(f"### {b.name}")
            out.append(f"**STRONG**  ·  *{b.evidence}*")
            out.append("")
            out.append(b.description)
            out.append("")
    except Exception:
        pass
    return "\n".join(out)


def _section_chart_at_a_glance(chart) -> str:
    out = ["## ✦ CHART AT A GLANCE\n"]
    out.append("*The five placements that shape every life event.*")
    out.append("")
    lagna = SIGNS[int(chart.lagna_lon // 30)]
    moon = SIGNS[int(chart.positions["Moon"] // 30)]
    nak_moon = (chart.nakshatras or {}).get("Moon", {}).get("name", "")
    pada = (chart.nakshatras or {}).get("Moon", {}).get("pada", "")
    weekday = chart.birth_dt.strftime("%A")
    DAY_LORD = {"Sunday": "Sun", "Monday": "Moon", "Tuesday": "Mars",
                "Wednesday": "Mercury", "Thursday": "Jupiter",
                "Friday": "Venus", "Saturday": "Saturn"}
    day_lord = DAY_LORD.get(weekday, "")
    bs = getattr(chart, "bala_summary", {}) or {}
    strongest = (bs.get("strongest") or [None])[0] or "—"

    out.append("| Placement | Detail |")
    out.append("|---|---|")
    out.append(f"| **LAGNA** | {lagna} · Lord: {chart.lagna_lord} |")
    out.append(f"| **MOON SIGN** | {moon} (House {((int(chart.positions['Moon']//30)-int(chart.lagna_lon//30))%12)+1}) |")
    out.append(f"| **JANMA NAKSHATRA** | {nak_moon} pada {pada} |")
    out.append(f"| **DAY LORD** | {day_lord} ({weekday}) |")
    out.append(f"| **STRONGEST GRAHA** | {strongest} |")
    out.append("")
    return "\n".join(out)


def _section_planetary_positions(chart) -> str:
    out = ["## ✦ PLANETARY POSITIONS\n"]
    out.append("*Where each planet sits and what it's doing.*")
    out.append("")
    out.append("| Planet | Rasi | H | Deg | Nakshatra | Signature |")
    out.append("|---|---|---:|---:|---|---|")
    SIGNATURE = {
        "Sun":     "father, authority, vitality",
        "Moon":    "mother, mind, public role",
        "Mars":    "courage, force, surgery, siblings",
        "Mercury": "intellect, speech, business",
        "Jupiter": "wisdom, dharma, wealth-grace",
        "Venus":   "marriage, art, comfort",
        "Saturn":  "discipline, work, longevity",
        "Rahu":    "foreign, ambition, unconventional",
        "Ketu":    "detachment, mystic skill",
    }
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
              "Saturn", "Rahu", "Ketu"):
        lon = chart.positions.get(p)
        if lon is None:
            continue
        sign = SIGNS[int(lon // 30)]
        deg = lon - int(lon // 30) * 30
        h = ((int(lon // 30) - int(chart.lagna_lon // 30)) % 12) + 1
        nak = (chart.nakshatras or {}).get(p, {}).get("name", "")
        out.append(f"| {p} | {sign} | {h} | {deg:.2f}° | {nak} | {SIGNATURE.get(p,'')} |")
    out.append("")
    return "\n".join(out)


def _section_chapters_full(chart) -> str:
    out = ["# ✦ THE LIFE TIMELINE — VIMSHOTTARI MAHA DASHA SEQUENCE\n"]
    out.append(
        "Each chapter below is one Maha Dasha — a major life-period of "
        "6 to 20 years. Inside each chapter you will find: the period's "
        "dominant theme, what to **expect**, what to **watch**, and the "
        "antardasha sub-period detail with concrete date windows."
    )
    out.append("")
    chapters = build_chapters(chart)
    for ch in chapters:
        title_line = f"## CHAPTER {ch.n} — {ch.planet.upper()} PERIOD"
        if ch.is_current:
            title_line += "  **★ NOW**"
        out.append(title_line)
        out.append("")
        out.append(
            f"**{ch.year_start} – {ch.year_end} · Age {ch.age_start}–"
            f"{ch.age_end} · {ch.theme}**"
        )
        out.append("")
        # 3-column header table
        out.append(f"| {ch.subheads[0]} | {ch.subheads[1]} | {ch.subheads[2]} |")
        out.append("|---|---|---|")
        out.append(f"| {ch.subhead_values[0]} | {ch.subhead_values[1]} | {ch.subhead_values[2]} |")
        out.append("")
        out.append(ch.intro)
        out.append("")
        # EXPECT
        out.append("**✦ EXPECT**")
        out.append("")
        for b in ch.expect:
            out.append(f"- {b}")
        out.append("")
        # WATCH
        out.append("**⚠ WATCH**")
        out.append("")
        for b in ch.watch:
            out.append(f"- {b}")
        out.append("")
        # Antardasha detail
        if ch.antardasha_detail:
            out.append("**Sub-period detail (antardashas with concrete date windows):**")
            out.append("")
            for line in ch.antardasha_detail:
                out.append(f"- {line}")
            out.append("")
        out.append("---")
        out.append("")
    return "\n".join(out)


def _section_ten_themes(chart) -> str:
    """Karmic patterns running through every chapter."""
    out = ["## ✦ THE TEN LIFE THEMES\n"]
    out.append("*Karmic patterns running through every chapter.*")
    out.append("")
    themes = []
    try:
        from engine.blessings import detect_all
        for b in detect_all(chart)[:5]:
            themes.append((b.name, "CANONICAL", b.description))
    except Exception:
        pass
    try:
        from engine.afflictions import detect_all
        for a in detect_all(chart)[:5]:
            themes.append((a.name, "PATTERN", a.description))
    except Exception:
        pass
    for i, (name, badge, desc) in enumerate(themes[:10], 1):
        out.append(f"### {i}. {name}")
        out.append(f"**{badge}**")
        out.append("")
        out.append(desc)
        out.append("")
    return "\n".join(out)


def _section_life_arcs(chart) -> str:
    """Wealth / Health / Marriage / Career arcs across all periods."""
    out = ["## ✦ LIFE ARCS AT A GLANCE\n"]
    out.append("*Wealth · Health · Marriage · Career by period.*")
    out.append("")
    chapters = build_chapters(chart)
    if not chapters:
        return "\n".join(out)

    # Wealth arc
    out.append("### Financial Arc")
    out.append("")
    out.append("| Age | Period | Wealth Signature |")
    out.append("|---|---|---|")
    WEALTH = {
        "Sun": "modest gains via authority", "Moon": "steady, family-supported",
        "Mars": "via inheritance / property / surgery",
        "Mercury": "study/foundation phase",
        "Jupiter": "stable, traditional, grace-supported",
        "Venus": "foundation laid, comfort and assets",
        "Saturn": "settled, slow but solid",
        "Rahu": "foreign / unconventional channels",
        "Ketu": "detachment from material gain",
    }
    for ch in chapters:
        out.append(f"| {ch.age_start}–{ch.age_end} | {ch.planet} | {WEALTH.get(ch.planet,'')} |")
    out.append("")

    # Health arc
    out.append("### Health Arc")
    out.append("")
    out.append("| Age | Period | Health Signature |")
    out.append("|---|---|---|")
    HEALTH = {
        "Sun": "BP / heart / eyes — watch", "Moon": "emotional / digestive — strong if Moon strong",
        "Mars": "accident / surgery window",
        "Mercury": "nervous / speech focus",
        "Jupiter": "stable, weight gain risk late",
        "Venus": "reproductive / aesthetic — generally stable",
        "Saturn": "joints / bones — slow decline",
        "Rahu": "skin / unusual ailments",
        "Ketu": "detachment / mystery illness possible",
    }
    for ch in chapters:
        out.append(f"| {ch.age_start}–{ch.age_end} | {ch.planet} | {HEALTH.get(ch.planet,'')} |")
    out.append("")

    # Marriage arc
    out.append("### Relationship Arc")
    out.append("")
    out.append("| Age | Period | Relationship Signature |")
    out.append("|---|---|---|")
    REL = {
        "Sun": "authority/father-axis tested",
        "Moon": "emotional bonding peak", "Mars": "passion / friction",
        "Mercury": "communication-led friendship",
        "Jupiter": "family-elder phase",
        "Venus": "marriage window if eligible age",
        "Saturn": "loyalty / endurance tested",
        "Rahu": "unconventional / foreign partner",
        "Ketu": "detachment / withdrawal phase",
    }
    for ch in chapters:
        out.append(f"| {ch.age_start}–{ch.age_end} | {ch.planet} | {REL.get(ch.planet,'')} |")
    out.append("")
    return "\n".join(out)


# ─── Public API ───────────────────────────────────────────────────────────
def generate_client_report_v2(chart) -> str:
    sections = [
        _section_cover_v2(chart),
        build_jathagam_full(chart, "en"),
        build_prediction_section_header("en"),
        _section_life_map(chart),
        _section_defining_yogas(chart),
        _section_chart_at_a_glance(chart),
        _section_planetary_positions(chart),
        _section_chapters_full(chart),
        _section_ten_themes(chart),
        _section_life_arcs(chart),
        _section_remedies(chart),
        _section_classical_appendix(chart),
        _section_closing(chart),
    ]
    return "\n\n".join(sections)
