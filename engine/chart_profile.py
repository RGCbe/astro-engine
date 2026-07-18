"""One coherent chart identity block before timing tables (P0-1)."""
from __future__ import annotations

from typing import Any

RASIS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}


def _house_lords(lagna_idx: int) -> dict[int, str]:
    lords: dict[int, str] = {}
    for h in range(1, 13):
        sign = RASIS[(lagna_idx + h - 1) % 12]
        lords[h] = SIGN_LORD[sign]
    return lords


def build_chart_profile(chart: dict[str, Any]) -> dict[str, Any]:
    """Executive synthesis: lagna, lords, key placements, optional yogas/strength."""
    lagna = chart.get("lagna") or chart.get("lagnam_rasi") or "Unknown"
    lagna_idx = int(chart.get("lagna_idx", 0))
    positions = chart.get("positions") or {}
    lords = _house_lords(lagna_idx)
    lagna_lord = SIGN_LORD.get(lagna, lords.get(1, "?"))

    moon = positions.get("Moon", {})
    key_placements = []
    for planet, pdata in sorted(positions.items()):
        if planet == "Ketu":
            continue
        h = pdata.get("house")
        if h is None:
            continue
        role = ""
        if lords.get(h) == planet:
            role = f" (rules H{h})"
        key_placements.append(
            f"{planet} in H{h} {pdata.get('rasi', '')}{role}"
        )

    top_yogas: list[str] = []
    for y in (chart.get("yogas") or [])[:5]:
        if isinstance(y, dict):
            top_yogas.append(y.get("name") or str(y))
        else:
            top_yogas.append(str(y))

    strength_note = ""
    sb = chart.get("shadbala") or {}
    if isinstance(sb, dict):
        strongest = (sb.get("summary") or {}).get("strongest") or sb.get("strongest")
        if strongest:
            strength_note = f"Strongest influences: {', '.join(strongest[:3])}. "

    ll_house = positions.get(lagna_lord, {}).get("house")
    executive = (
        f"{lagna} rising; lagna lord {lagna_lord} in house {ll_house or '?'}. "
        f"Moon in {moon.get('rasi', '?')} (H{moon.get('house', '?')}). "
        f"{strength_note}"
        f"Functional lords: 7th={lords[7]}, 10th={lords[10]}, 5th={lords[5]}. "
        "This profile anchors all dated windows below; not generic sun-sign text."
    )

    return {
        "name": chart.get("name", "native"),
        "lagna": lagna,
        "lagna_lord": lagna_lord,
        "lagna_lord_house": ll_house,
        "moon_rasi": moon.get("rasi"),
        "moon_house": moon.get("house"),
        "house_lords": lords,
        "key_placements": key_placements,
        "top_yogas": top_yogas,
        "executive_summary_en": executive.strip(),
        "nature": "chart_synthesis",
        "disclaimer": (
            "Mechanical chart summary from birth data; "
            "classical citations follow in topic blocks."
        ),
    }
