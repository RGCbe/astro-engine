"""Deep Property Analysis Module.
V2 Engine specific logic for analyzing property, real estate, land, and vehicle acquisition.
Distinguishes between commercial (Mars/Saturn) and residential (Venus/Moon) property.
"""
from vedic_core import RASI_LORDS, RASIS

def _lord(lagna_idx, h):
    return RASI_LORDS[RASIS[(lagna_idx + h - 1) % 12]]

def event_property_deep(chart, ds, tr, yogas, age):
    """Deep property analysis event logic for V2 MetaReasoner."""
    if age < 21 or age > 80:
        return None
        
    lagna_idx = chart.get("lagna_idx", 0)
    h4_lord = _lord(lagna_idx, 4)
    h11_lord = _lord(lagna_idx, 11)
    h2_lord = _lord(lagna_idx, 2)
    h9_lord = _lord(lagna_idx, 9)
    
    md = ds.get(1, {}).get("md")
    ad = ds.get(2, {}).get("ad")
    pd = ds.get(3, {}).get("pd")
    
    score = 0
    why = []
    
    # Base 4th house logic (home/land)
    if md == h4_lord:
        score += 3
        why.append(f"4L ({h4_lord}) MD — primary property window")
    elif ad == h4_lord:
        score += 2
        why.append(f"4L ({h4_lord}) AD — property window")
        
    if md == h11_lord or ad == h11_lord:
        score += 1
        why.append(f"11L ({h11_lord}) active — financial gain for investment")
        
    # Karaka specific logic
    if md == "Mars" or ad == "Mars":
        score += 2
        why.append("Mars active — favorable for land, commercial property, or construction")
        
    if md == "Venus" or ad == "Venus":
        score += 1
        why.append("Venus active — favorable for residential property, luxury, or vehicles")
        
    if md == "Saturn" or ad == "Saturn":
        score += 1
        why.append("Saturn active — favorable for agricultural land, older properties, or long-term building")
        
    # Confluence
    if md == h4_lord and ad == h11_lord:
        score += 3
        why.append("4L MD + 11L AD — massive gain of property/real estate")
    if md == h11_lord and ad == h4_lord:
        score += 3
        why.append("11L MD + 4L AD — massive gain of property/real estate")
        
    if md == h9_lord and ad == h4_lord:
        score += 2
        why.append("9L (fortune) + 4L (property) — lucky/auspicious property acquisition")
        
    if md == "Mars" and ad == h4_lord:
        score += 2
        why.append("Mars (Land Karaka) + 4L — strong trigger for buying land/plots")
        
    # Transits
    jup_to_4l = next((t for t in tr if t.get("transit") == "Jupiter" and t.get("natal") == h4_lord), None)
    if jup_to_4l:
        score += 2
        why.append(f"Jupiter transit over 4L ({h4_lord})")
        
    sat_to_4l = next((t for t in tr if t.get("transit") == "Saturn" and t.get("natal") == h4_lord), None)
    if sat_to_4l:
        score += 1
        why.append(f"Saturn transit over 4L ({h4_lord}) — property materialization/construction")

    if score < 4:
        return None
        
    # Differentiate Commercial vs Residential based on active planets
    property_type = "Property / Real Estate"
    if "Mars active" in "".join(why) or "Saturn active" in "".join(why):
        property_type += " (Commercial/Land focus)"
    elif "Venus active" in "".join(why):
        property_type += " (Residential/Luxury focus)"

    return {
        "event": property_type,
        "category": "property",
        "severity": min(5, score // 2),
        "predicted_valence": "auspicious",
        "yoga": None,
        "why": why,
        "source": "BPHS Ch. 24 (4th House) + Mars/Venus Karaka Rules"
    }
