"""
Synthesis Engine — Aggregates all backend signals into a coherent forecast.
"""

def generate_synthesis(data: dict) -> dict:
    """
    Analyzes the full Jathagam response and generates a high-level summary.
    """
    lagnam = data.get("lagnam")
    rasi = data.get("janma_rasi")
    dasha = data.get("current_dasha")
    antar = data.get("current_antardasha")
    
    # 1. Dasha Analysis
    dasha_summary = f"You are currently in the major period (Maha Dasha) of {dasha} "
    if antar:
        dasha_summary += f"and the sub-period (Antar Dasha) of {antar}. "
    
    # 2. Strength Check
    strong_planets = data.get("shadbala", {}).get("summary", {}).get("strongest", [])
    strength_note = ""
    if strong_planets:
        strength_note = f"Your strongest planetary influences currently come from {', '.join(strong_planets)}. "
    
    # 3. Gochar (Transit) Highlights
    gochar = data.get("gochar", {}).get("transit_planets", [])
    transit_highlights = []
    for t in gochar:
        if t["gochar_valence"] == "GOOD":
            transit_highlights.append(f"{t['planet']} in your {t['house_from_moon']}th house from Moon is bringing {t['gochar_title']}")
        elif t["gochar_valence"] == "BAD":
            # Only highlight major ones like Saturn/Rahu
            if t["planet"] in ("Saturn", "Rahu"):
                transit_highlights.append(f"{t['planet']} transit is currently challenging ({t['gochar_title']})")
    
    gochar_note = ""
    if transit_highlights:
        gochar_note = "Key transits: " + "; ".join(transit_highlights) + ". "
    
    # 4. Divisional Insights (D9/D10)
    all_pos = data.get("all_planet_positions", {})
    sun_d10 = all_pos.get("Sun", {}).get("dasamsa_rasi", "Unknown")
    moon_d9 = all_pos.get("Moon", {}).get("navamsa_rasi", "Unknown")
    
    divisional_note = f"Your Navamsa (D9) Moon in {moon_d9} suggests your inner strength is well-aligned. "
    if sun_d10:
        divisional_note += f"In your career chart (D10), the Sun's placement in {sun_d10} will play a key role in professional growth."

    # 5. Overall Forecast
    is_dasha_strong = dasha in strong_planets
    
    if is_dasha_strong:
        overall = f"This is a high-potential phase. Since your Dasha lord {dasha} is strong in your chart, you can expect significant progress. {divisional_note}"
    else:
        overall = f"This is a period for steady work and careful planning. Focus on strengthening the areas ruled by {dasha}. {divisional_note}"

    return {
        "nature": "algorithmic_summary",
        "disclaimer": "Interpretive summary from dasha, shadbala, and transits — not a direct scripture quotation.",
        "short_summary": f"{dasha_summary}{strength_note}{gochar_note}",
        "action_advice": overall,
        "lucky_factors": {
            "strongest_planet": strong_planets[0] if strong_planets else "N/A",
            "favorable_transit": next((t["planet"] for t in gochar if t["gochar_valence"] == "GOOD"), "None")
        }
    }
