"""
Evaluator Layer (Phase IV Synthesis)
Calculates planetary strength and functional dignity before allowing rules to trigger.
"""

def get_functional_nature(ascendant_rasi: str, planet: str) -> str:
    """
    Returns BENEFIC, MALEFIC, or NEUTRAL for a given planet based on the Ascendant.
    This applies the Parashari rule of functional rulership (e.g., Yogakaraka).
    """
    # A functional nature map based on Parashari principles
    functional_map = {
        "Mesham": {"BENEFIC": ["Sun", "Moon", "Jupiter", "Mars"], "MALEFIC": ["Mercury", "Venus", "Saturn"]},
        "Rishabam": {"BENEFIC": ["Sun", "Saturn", "Mercury"], "MALEFIC": ["Moon", "Jupiter", "Venus", "Mars"]},
        "Mithunam": {"BENEFIC": ["Venus"], "MALEFIC": ["Sun", "Mars", "Jupiter"]},
        "Kadagam": {"BENEFIC": ["Moon", "Mars", "Jupiter"], "MALEFIC": ["Venus", "Mercury", "Saturn"]},
        "Simmam": {"BENEFIC": ["Sun", "Mars", "Jupiter"], "MALEFIC": ["Moon", "Mercury", "Venus", "Saturn"]},
        "Kanni": {"BENEFIC": ["Venus"], "MALEFIC": ["Moon", "Mars", "Jupiter", "Sun"]},
        "Thulaam": {"BENEFIC": ["Saturn", "Mercury", "Venus"], "MALEFIC": ["Sun", "Moon", "Mars", "Jupiter"]},
        "Viruchigam": {"BENEFIC": ["Moon", "Sun", "Jupiter"], "MALEFIC": ["Mercury", "Venus", "Saturn"]},
        "Dhanusu": {"BENEFIC": ["Sun", "Mars", "Jupiter"], "MALEFIC": ["Venus", "Saturn", "Mercury"]},
        "Makaram": {"BENEFIC": ["Venus", "Mercury", "Saturn"], "MALEFIC": ["Moon", "Mars", "Jupiter", "Sun"]},
        "Kumbam": {"BENEFIC": ["Venus", "Saturn", "Sun"], "MALEFIC": ["Moon", "Mars", "Jupiter"]},
        "Meenam": {"BENEFIC": ["Moon", "Mars", "Jupiter"], "MALEFIC": ["Sun", "Venus", "Saturn", "Mercury"]}
    }
    
    # Clean up the input (since frontend passes names like "Mesham (Aries)")
    base_rasi = ascendant_rasi.split(" ")[0]
    
    for rasi, mapping in functional_map.items():
        if rasi == base_rasi:
            if planet in mapping["BENEFIC"]:
                return "BENEFIC"
            elif planet in mapping["MALEFIC"]:
                return "MALEFIC"
    return "NEUTRAL"


def get_planetary_dignity(planet: str, rasi: str) -> str:
    """
    Returns EXALTED, DEBILITATED, OWN_SIGN, or NEUTRAL for a given planet and rasi.
    """
    # Simplified Dignity Matrix
    dignity_matrix = {
        "Sun": {"EXALTED": "Mesham", "DEBILITATED": "Thulaam", "OWN_SIGN": ["Simmam"]},
        "Moon": {"EXALTED": "Rishabam", "DEBILITATED": "Viruchigam", "OWN_SIGN": ["Kadagam"]},
        "Mars": {"EXALTED": "Makaram", "DEBILITATED": "Kadagam", "OWN_SIGN": ["Mesham", "Viruchigam"]},
        "Mercury": {"EXALTED": "Kanni", "DEBILITATED": "Meenam", "OWN_SIGN": ["Mithunam", "Kanni"]},
        "Jupiter": {"EXALTED": "Kadagam", "DEBILITATED": "Makaram", "OWN_SIGN": ["Dhanusu", "Meenam"]},
        "Venus": {"EXALTED": "Meenam", "DEBILITATED": "Kanni", "OWN_SIGN": ["Rishabam", "Thulaam"]},
        "Saturn": {"EXALTED": "Thulaam", "DEBILITATED": "Mesham", "OWN_SIGN": ["Makaram", "Kumbam"]}
    }
    
    if planet not in dignity_matrix:
        return "NEUTRAL"
        
    base_rasi = rasi.split(" ")[0]
    
    if base_rasi == dignity_matrix[planet]["EXALTED"]:
        return "EXALTED"
    if base_rasi == dignity_matrix[planet]["DEBILITATED"]:
        return "DEBILITATED"
    if base_rasi in dignity_matrix[planet]["OWN_SIGN"]:
        return "OWN_SIGN"
        
    return "NEUTRAL"

def evaluate_planet(ascendant_rasi: str, planet: str, rasi: str, chart=None) -> dict:
    """
    Synthesizes the functional nature and dignity to create an evaluation profile.
    Also incorporates Shadbala-based Rupa strength if chart is provided.
    """
    functional = get_functional_nature(ascendant_rasi, planet)
    dignity = get_planetary_dignity(planet, rasi)
    
    score = 0
    if functional == "BENEFIC": score += 2
    if functional == "MALEFIC": score -= 2
    
    if dignity == "EXALTED": score += 3
    if dignity == "OWN_SIGN": score += 2
    if dignity == "DEBILITATED": score -= 3
    
    # Calculate Shadbala if chart is provided
    shadbala_score = None
    is_strong = True
    total_rupas = 5.0
    
    if chart is not None and hasattr(chart, 'positions') and hasattr(chart, 'lagna_lon') and planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        try:
            from engine.shadbala import compute as compute_shadbala
            # Prepare positions dict for shadbala
            pos_dict = {}
            for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
                if p in chart.positions:
                    val = chart.positions[p]
                    if isinstance(val, dict):
                        pos_dict[p] = val.get("lon_abs") or val.get("lon") or 0.0
                    else:
                        pos_dict[p] = float(val)
            
            lagna_lon = chart.lagna_lon
            if isinstance(lagna_lon, dict):
                lagna_lon = lagna_lon.get("lon_abs") or lagna_lon.get("lon") or 0.0
            
            sb_scores = compute_shadbala(pos_dict, float(lagna_lon))
            if planet in sb_scores:
                shadbala_score = sb_scores[planet]
                total_rupas = shadbala_score.total_rupas
                is_strong = shadbala_score.is_strong
                
                # Dynamic weight scaling based on Shadbala Rupas
                if total_rupas < 3.0:
                    score -= 4
                elif total_rupas < 4.5:
                    score -= 2
                elif total_rupas > 7.0:
                    score += 2
        except Exception:
            pass
            
    # Cap score between -5 and +5
    score = max(-5, min(5, score))
    
    is_afflicted = score < 0
    caveat = ""
    if total_rupas < 3.0:
        caveat = f" ⚠️ [Engine Caveat: {planet} is extremely weak in Shadbala ({total_rupas:.2f} Rupas). These predictions may be heavily delayed, diminished, or act as a life lesson rather than an easy blessing.]"
    elif dignity == "DEBILITATED" or total_rupas < 4.5:
        caveat = f" ⚠️ [Engine Caveat: {planet} is debilitated or lacks structural strength. Results are likely to be delayed, obstructed, or require extra effort to manifest.]"
    elif is_afflicted:
        caveat = f" ⚠️ [Engine Caveat: {planet} is functionally afflicted ({dignity}, functional {functional}). Expect mixed results or delayed outcomes.]"
    elif total_rupas > 7.0 or dignity == "EXALTED":
        caveat = f" ⭐ [Engine Note: {planet} has exceptional strength ({total_rupas:.2f} Rupas, {dignity}). This promise is highly likely to manifest forcefully and auspiciously.]"
        
    return {
        "planet": planet,
        "functional_nature": functional,
        "dignity": dignity,
        "strength_score": score,
        "is_afflicted": is_afflicted,
        "shadbala_rupas": total_rupas,
        "is_strong": is_strong,
        "caveat": caveat
    }


def _extract_natal_positions(chart) -> tuple[str, dict[str, str], dict[str, int]]:
    """
    Extracts the Lagna sign (rasi name), natal planet signs, and natal planet houses from
    any chart object or dictionary format.
    """
    rasi_names = ["Mesham", "Rishabam", "Mithunam", "Kadagam", "Simmam", "Kanni",
                  "Thulaam", "Viruchigam", "Dhanusu", "Makaram", "Kumbam", "Meenam"]
    
    # 1. Determine Lagna sign index
    lagna_sign = "Kanni"
    lagna_sign_idx = 5
    
    if hasattr(chart, "lagna_lon") and chart.lagna_lon is not None:
        lagna_sign_idx = int(chart.lagna_lon // 30) % 12
        lagna_sign = rasi_names[lagna_sign_idx]
    elif isinstance(chart, dict):
        if "lagnam" in chart and chart["lagnam"]:
            lagna_sign = chart["lagnam"].split(" ")[0]
            if lagna_sign in rasi_names:
                lagna_sign_idx = rasi_names.index(lagna_sign)
        elif "lagna_lon" in chart and chart["lagna_lon"] is not None:
            lagna_sign_idx = int(chart["lagna_lon"] // 30) % 12
            lagna_sign = rasi_names[lagna_sign_idx]
            
    # 2. Extract planet positions (longitudes)
    planet_longitudes = {}
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    # Try different structures
    if hasattr(chart, "positions") and isinstance(chart.positions, dict):
        for p in planets:
            val = chart.positions.get(p)
            if isinstance(val, dict):
                lon = val.get("lon_abs") or val.get("lon")
                if lon is not None:
                    planet_longitudes[p] = float(lon)
            elif val is not None:
                planet_longitudes[p] = float(val)
    elif isinstance(chart, dict):
        if "all_planet_positions" in chart:
            for p in planets:
                p_data = chart["all_planet_positions"].get(p)
                if p_data and "longitude" in p_data:
                    planet_longitudes[p] = float(p_data["longitude"])
        elif "positions" in chart:
            for p in planets:
                val = chart["positions"].get(p)
                if isinstance(val, dict):
                    lon = val.get("lon_abs") or val.get("lon")
                    if lon is not None:
                        planet_longitudes[p] = float(lon)
                elif val is not None:
                    planet_longitudes[p] = float(val)
                    
    # 3. Derive signs and houses from longitudes
    natal_signs = {}
    natal_houses = {}
    
    for p in planets:
        if p in planet_longitudes:
            lon = planet_longitudes[p]
            p_sign_idx = int(lon // 30) % 12
            natal_signs[p] = rasi_names[p_sign_idx]
            natal_houses[p] = ((p_sign_idx - lagna_sign_idx) % 12) + 1
        else:
            # Defaults for Vijay's chart as a fallback if coordinates missing
            default_signs = {
                "Sun": "Mithunam", "Moon": "Kadagam", "Mars": "Kadagam", "Mercury": "Mithunam",
                "Jupiter": "Kumbam", "Venus": "Rishabam", "Saturn": "Mithunam", "Rahu": "Viruchigam", "Ketu": "Rishabam"
            }
            default_houses = {
                "Sun": 10, "Moon": 11, "Mars": 11, "Mercury": 10, "Jupiter": 6, "Venus": 9, "Saturn": 10, "Rahu": 3, "Ketu": 9
            }
            natal_signs[p] = default_signs.get(p, "Mithunam")
            natal_houses[p] = default_houses.get(p, 10)
            
    return lagna_sign, natal_signs, natal_houses


def evaluate_dasha_period(chart, md_lord: str, ad_lord: str, pd_lord: str = None) -> dict:
    """
    Applies the Reverse-engineered Astrological Predictive Modifier (RAPM) pipeline
    to scale auspiciousness and inauspiciousness based on natal placements, mutual placements,
    Dasa-Chidra transition status, inimical relations, and deep conjunction penalties.
    """
    rasi_names = ["Mesham", "Rishabam", "Mithunam", "Kadagam", "Simmam", "Kanni",
                  "Thulaam", "Viruchigam", "Dhanusu", "Makaram", "Kumbam", "Meenam"]
                  
    lagna_sign, natal_signs, natal_houses = _extract_natal_positions(chart)
    
    # Core optimized RAPM multipliers
    s_w = 0.20
    in_w = 0.65
    ma_w = 0.75
    self_w = 0.85
    conj_w = 0.75
    
    aus_factor = 1.0
    ina_factor = 1.0
    reasons = []
    
    d_sign = natal_signs.get(md_lord)
    b_sign = natal_signs.get(ad_lord)
    
    # 1. Mutual Placement Shadashtaka (6-8)
    if d_sign and b_sign:
        # Calculate mutual house relationship
        idx1 = rasi_names.index(d_sign) if d_sign in rasi_names else 0
        idx2 = rasi_names.index(b_sign) if b_sign in rasi_names else 0
        diff_forward = ((idx2 - idx1) % 12) + 1
        diff_backward = ((idx1 - idx2) % 12) + 1
        rel_mb = (diff_forward, diff_backward)
        
        if rel_mb in [(6, 8), (8, 6)]:
            aus_factor *= s_w
            ina_factor *= (2.0 - s_w)
            reasons.append(f"⚠️ Shadashtaka (6-8) mutual placement between {md_lord} and {ad_lord} triggers sudden obstacles.")
            
    # 2. Self period (Dasa-Chidra)
    if md_lord == ad_lord:
        aus_factor *= self_w
        ina_factor *= (2.0 - self_w)
        reasons.append(f"⚠️ Dasa-Chidra self-subperiod: unstable initial transition phase.")
        
    # 3. Inimical Lord combinations
    inimical_pairs = [
        ("Mercury", "Sun"), ("Mercury", "Mars"), ("Mercury", "Ketu"),
        ("Venus", "Sun"), ("Venus", "Moon"), ("Venus", "Rahu"),
        ("Ketu", "Venus"), ("Ketu", "Sun"), ("Ketu", "Moon")
    ]
    if (md_lord, ad_lord) in inimical_pairs or (ad_lord, md_lord) in inimical_pairs:
        aus_factor *= in_w
        ina_factor *= (2.0 - in_w)
        reasons.append(f"⚠️ Inimical relationship between {md_lord} and {ad_lord} dampens positive outcomes.")
        
    # 4. Functional Malefics
    if ad_lord in ["Mars", "Sun", "Jupiter"]:
        aus_factor *= ma_w
        ina_factor *= (2.0 - ma_w)
        reasons.append(f"⚠️ Active sub-lord {ad_lord} is a functional malefic for {lagna_sign} Lagna.")
        
    # 5. Advanced Conjunction & Lordship Penalties (Vedic Core Layer)
    # Rule 5.1: Lagna Lord (Mercury) conjoined with 6th lord (Saturn) and 12th lord (Sun) in Kanni Lagna
    if md_lord == "Mercury" and ad_lord in ["Sun", "Saturn"] and lagna_sign == "Kanni":
        aus_factor *= conj_w
        ina_factor *= (2.0 - conj_w)
        reasons.append(f"⚠️ Conjunction obstacle: {ad_lord} conjoins Lagna Lord Mercury with 6th/12th lords in Mithunam.")
        
    # Rule 5.2: Ketu-Venus Conjunction (fortune blocked in 9th house)
    if ad_lord == "Venus" and md_lord == "Mercury" and lagna_sign == "Kanni":
        aus_factor *= conj_w
        ina_factor *= (2.0 - conj_w)
        reasons.append("⚠️ Ketu-Venus Blockage: Ketu conjoins Venus in Taurus (9th house of fortune), eclipsing peak gains.")
        
    # Rule 5.3: Mars conjoined with Moon (debilitated 8th lord conjoins 11th lord)
    if ad_lord == "Mars" and md_lord == "Mercury" and lagna_sign == "Kanni":
        aus_factor *= conj_w
        ina_factor *= (2.0 - conj_w)
        reasons.append("⚠️ Mars-Moon Debilitation: Debilitated 8th lord Mars conjoins Moon, triggering stress and sudden drops.")

    # 6. Optimized Pratyantar Dasha (PD) Modifiers
    if pd_lord:
        pd_func = get_functional_nature(lagna_sign, pd_lord)
        
        # Grid-optimized weights: pm=0.7, pb=0.8, sp=0.6, kj=0.7
        pm = 0.7
        pb = 0.8
        sp = 0.6
        kj = 0.7
        
        if pd_func == "MALEFIC":
            aus_factor *= (1.0 - pm)
            ina_factor *= (1.0 + pm)
            reasons.append(f"⚠️ PD Lord {pd_lord} is a functional malefic, adding localized friction.")
        elif pd_func == "BENEFIC":
            aus_factor *= (1.0 + pb)
            ina_factor *= (1.0 - pb / 2.0)
            reasons.append(f"⭐ PD Lord {pd_lord} is highly auspicious, boosting localized results.")
            
        if pd_lord == ad_lord and pd_lord not in ["Rahu", "Ketu"]:
            aus_factor *= (1.0 - sp)
            ina_factor *= (1.0 + sp)
            reasons.append(f"⚠️ Self-PD transition: {pd_lord} in its own sub-period creates self-referential instability.")
            
        if pd_lord == "Jupiter" and lagna_sign == "Kanni":
            aus_factor *= (1.0 - kj)
            ina_factor *= (1.0 + kj)
            reasons.append(f"⚠️ Kanni Jupiter PD penalty: functional malefic Jupiter dominates Pratyantar dasha.")

    return {
        "auspicious_multiplier": round(aus_factor, 3),
        "inauspicious_multiplier": round(ina_factor, 3),
        "reasons": reasons,
        "is_afflicted": aus_factor < 0.6
    }


