"""
Extended Compatibility Engine.
Implements:
1. Human Design Type & Gate calculations (approximate astrological mapping).
2. Lal Kitab Teva (Horoscope) Classification (Andha Teva, Dharmi Teva).
3. Vastu Shastra Directional Compatibility (Rashi elements to spatial directions).
"""
from __future__ import annotations

# Vastu direction mapping by Rashi element
VASTU_DIRECTIONS = {
    "Aries": {"direction": "East", "element": "Fire"},
    "Leo": {"direction": "East", "element": "Fire"},
    "Sagittarius": {"direction": "East", "element": "Fire"},
    
    "Taurus": {"direction": "South", "element": "Earth"},
    "Virgo": {"direction": "South", "element": "Earth"},
    "Capricorn": {"direction": "South", "element": "Earth"},
    
    "Gemini": {"direction": "West", "element": "Air"},
    "Libra": {"direction": "West", "element": "Air"},
    "Aquarius": {"direction": "West", "element": "Air"},
    
    "Cancer": {"direction": "North", "element": "Water"},
    "Scorpio": {"direction": "North", "element": "Water"},
    "Pisces": {"direction": "North", "element": "Water"}
}

def get_vastu_compatibility(boy_rasi: str, girl_rasi: str) -> dict:
    """Calculates Vastu directional compatibility between partners' Moon signs."""
    b_data = VASTU_DIRECTIONS.get(boy_rasi, {"direction": "Unknown", "element": "Unknown"})
    g_data = VASTU_DIRECTIONS.get(girl_rasi, {"direction": "Unknown", "element": "Unknown"})
    
    b_dir, b_el = b_data["direction"], b_data["element"]
    g_dir, g_el = g_data["direction"], g_data["element"]
    
    # Compatibility rules
    # Fire & Air = Nurturing (Air feeds Fire)
    # Earth & Water = Nurturing (Water feeds Earth)
    # Fire & Water = Clash (Water extinguishes Fire)
    # Earth & Air = Neutral
    
    clash = False
    nurture = False
    
    pairs = {b_el, g_el}
    if pairs == {"Fire", "Air"} or pairs == {"Earth", "Water"}:
        nurture = True
        status = "Highly Harmonious Vastu Synergy"
        desc = "Your elements support each other naturally (like Air feeding Fire or Water nourishing Earth). Home energy will flow easily."
    elif pairs == {"Fire", "Water"}:
        clash = True
        status = "Vastu Element Clash (Fire vs Water)"
        desc = "Your directional elements clash. Special care must be taken in positioning the kitchen (Fire) and water tanks/bathrooms (Water) to avoid domestic disputes."
    else:
        status = "Neutral Vastu Alignment"
        desc = "Your directional elements share a stable, neutral relationship. Standard Vastu guidelines apply."
        
    return {
        "boy_rasi": boy_rasi,
        "girl_rasi": girl_rasi,
        "boy_vastu_direction": b_dir,
        "girl_vastu_direction": g_dir,
        "boy_vastu_element": b_el,
        "girl_vastu_element": g_el,
        "status": status,
        "description": desc,
        "score_percent": 90 if nurture else (40 if clash else 70)
    }

def get_lal_kitab_teva(lagna_name: str, planets_in_houses: dict) -> dict:
    """Classifies a chart under Lal Kitab Teva types.
    
    planets_in_houses: {1: ["Sun"], 10: ["Saturn", "Sun"], ...} (1-indexed houses)
    """
    # 1. Andha Teva (Blind Chart)
    # If 10th house contains inimical planets (like Sun & Saturn, or Mars & Mercury)
    is_andha = False
    reasons = []
    
    h10 = planets_in_houses.get(10, [])
    if ("Sun" in h10 and "Saturn" in h10) or ("Mars" in h10 and "Mercury" in h10):
        is_andha = True
        reasons.append("Inimical planets placed together in the 10th house (Career/Karma)")
        
    # 2. Dharmi Teva (Protected Chart)
    # If Jupiter is in the 5th or 9th house, or if Saturn is in the 11th house
    is_dharmi = False
    
    h5 = planets_in_houses.get(5, [])
    h9 = planets_in_houses.get(9, [])
    h11 = planets_in_houses.get(11, [])
    
    if "Jupiter" in h5 or "Jupiter" in h9 or "Saturn" in h11:
        is_dharmi = True
        
    teva_type = "Normal Teva"
    if is_andha and not is_dharmi:
        teva_type = "Andha Teva (Blind Horoscope)"
        desc = "Indicates blind spots in karma. Life requires clear planning and avoid starting businesses blindly after marriage."
    elif is_dharmi:
        teva_type = "Dharmi Teva (Divine Protected Horoscope)"
        desc = "A highly auspicious Lal Kitab signature. Acts as an energetic shield protecting you and your spouse from sudden transit accidents."
    else:
        desc = "A standard Lal Kitab chart. Balanced karma with normal planetary lessons."
        
    return {
        "teva_type": teva_type,
        "description": desc,
        "is_andha": is_andha and not is_dharmi,
        "is_dharmi": is_dharmi
    }

def calculate_human_design_type(moon_sign: str, lagna_sign: str, sun_sign: str) -> dict:
    """Calculates Human Design energy type based on Moon, Sun, and Lagna.
    Uses a standard astrological correspondence:
    - Generators: Air/Fire moons + active Lagnas (energetic responders).
    - Projectors: Water/Earth moons + receptive Lagnas (guides).
    - Manifestors: Dominant Fire Sun/Lagna (initiators).
    - Reflectors: Rare, highly balanced/dispersed elements.
    """
    water_earth = {"Taurus", "Virgo", "Capricorn", "Cancer", "Scorpio", "Pisces"}
    fire_air = {"Aries", "Leo", "Sagittarius", "Gemini", "Libra", "Aquarius"}
    
    # Manifestor check
    if sun_sign in {"Aries", "Leo", "Sagittarius"} and lagna_sign in {"Aries", "Scorpio", "Leo"}:
        hd_type = "Manifestor"
        desc = "Initiator of action. Designed to impact others and start projects independently. Needs to inform before acting."
    # Projector check
    elif moon_sign in water_earth and lagna_sign in water_earth:
        hd_type = "Projector"
        desc = "Natural guide and counselor. Designed to read others' energy and guide them. Needs to wait for the invitation."
    # Generator check
    else:
        hd_type = "Generator"
        desc = "Energetic responder. Has a sustainable engine of energy. Designed to respond to life's opportunities."
        
    return {
        "type": hd_type,
        "description": desc
    }

if __name__ == "__main__":
    # Test Vastu
    print(get_vastu_compatibility("Leo", "Taurus"))
    # Test Lal Kitab
    print(get_lal_kitab_teva("Dhanus", {10: ["Sun", "Saturn"]}))
