"""
I-Ching & Feng Shui Kua Astrological Engine.
Calculates Kua numbers (Life Gua) based on birth year and gender, 
and computes Ba Zhai (8 Mansions) compatibility.
"""
from __future__ import annotations

# Kua Number detail database
KUA_DETAILS = {
    1: {
        "trigram": "Kan",
        "element": "Water",
        "group": "East",
        "auspicious_directions": ["Southeast", "East", "South", "North"],
        "han": "坎",
        "description": "Deep water, fluid, adaptable, and intuitive."
    },
    2: {
        "trigram": "Kun",
        "element": "Earth",
        "group": "West",
        "auspicious_directions": ["Northeast", "West", "Northwest", "Southwest"],
        "han": "坤",
        "description": "Nurturing earth, stable, receptive, and supportive."
    },
    3: {
        "trigram": "Zhen",
        "element": "Wood",
        "group": "East",
        "auspicious_directions": ["South", "North", "Southeast", "East"],
        "han": "震",
        "description": "Thunder, active, growth-oriented, and ambitious."
    },
    4: {
        "trigram": "Xun",
        "element": "Wood",
        "group": "East",
        "auspicious_directions": ["North", "South", "East", "Southeast"],
        "han": "巽",
        "description": "Wind, flexible, gentle, and communicative."
    },
    6: {
        "trigram": "Qian",
        "element": "Metal",
        "group": "West",
        "auspicious_directions": ["West", "Northeast", "Southwest", "Northwest"],
        "han": "乾",
        "description": "Heaven, strong, leadership-oriented, and structured."
    },
    7: {
        "trigram": "Dui",
        "element": "Metal",
        "group": "West",
        "auspicious_directions": ["Northwest", "Southwest", "Northeast", "West"],
        "han": "兌",
        "description": "Lake, joyful, communicative, and artistic."
    },
    8: {
        "trigram": "Ken",
        "element": "Earth",
        "group": "West",
        "auspicious_directions": ["Southwest", "Northwest", "West", "Northeast"],
        "han": "艮",
        "description": "Mountain, still, analytical, and grounded."
    },
    9: {
        "trigram": "Li",
        "element": "Fire",
        "group": "East",
        "auspicious_directions": ["East", "Southeast", "North", "South"],
        "han": "離",
        "description": "Fire, expressive, passionate, and bright."
    }
}

# 8 Mansions (Ba Zhai) Kua combination relationship matrix
# Mapped to relationship type and description
KUA_RELATIONS = {
    "Sheng Qi": {"name": "Sheng Qi (Life Force)", "score": 95, "desc": "Highest compatibility. Generates active growth, prosperity, and vital energy."},
    "Tian Yi": {"name": "Tian Yi (Heavenly Doctor)", "score": 90, "desc": "Excellent harmony. Promotes good health, healing, and peace between partners."},
    "Yan Nian": {"name": "Yan Nian (Longevity/Harmony)", "score": 85, "desc": "Very good compatibility. Ensures long-term relationship stability and domestic balance."},
    "Fu Wei": {"name": "Fu Wei (Stability)", "score": 75, "desc": "Supportive connection. Brings personal growth, peace of mind, and quiet stability."},
    "Huo Hai": {"name": "Huo Hai (Mishaps)", "score": 50, "desc": "Challenging connection. May bring minor arguments, obstacles, or small domestic worries."},
    "Liu Sha": {"name": "Liu Sha (Six Killings)", "score": 40, "desc": "Difficult relationship. Leads to emotional coldness, disputes, or lack of mutual understanding."},
    "Wu Gui": {"name": "Wu Gui (Five Ghosts)", "score": 30, "desc": "Inauspicious connection. High potential for constant arguments, instability, and mutual distrust."},
    "Jue Ming": {"name": "Jue Ming (Total Loss)", "score": 10, "desc": "Worst compatibility. Represents complete energetic opposition, severe clashes, and emotional strain."}
}

MATCH_MATRIX = {
    1: {1: "Fu Wei", 2: "Jue Ming", 3: "Tian Yi", 4: "Sheng Qi", 6: "Liu Sha", 7: "Huo Hai", 8: "Wu Gui", 9: "Yan Nian"},
    2: {1: "Jue Ming", 2: "Fu Wei", 3: "Huo Hai", 4: "Wu Gui", 6: "Yan Nian", 7: "Tian Yi", 8: "Sheng Qi", 9: "Liu Sha"},
    3: {1: "Tian Yi", 2: "Huo Hai", 3: "Fu Wei", 4: "Yan Nian", 6: "Wu Gui", 7: "Jue Ming", 8: "Liu Sha", 9: "Sheng Qi"},
    4: {1: "Sheng Qi", 2: "Wu Gui", 3: "Yan Nian", 4: "Fu Wei", 6: "Huo Hai", 7: "Liu Sha", 8: "Jue Ming", 9: "Tian Yi"},
    6: {1: "Liu Sha", 2: "Yan Nian", 3: "Wu Gui", 4: "Huo Hai", 6: "Fu Wei", 7: "Sheng Qi", 8: "Tian Yi", 9: "Jue Ming"},
    7: {1: "Huo Hai", 2: "Tian Yi", 3: "Jue Ming", 4: "Liu Sha", 6: "Sheng Qi", 7: "Fu Wei", 8: "Yan Nian", 9: "Wu Gui"},
    8: {1: "Wu Gui", 2: "Sheng Qi", 3: "Liu Sha", 4: "Jue Ming", 6: "Tian Yi", 7: "Yan Nian", 8: "Fu Wei", 9: "Huo Hai"},
    9: {1: "Yan Nian", 2: "Liu Sha", 3: "Sheng Qi", 4: "Tian Yi", 6: "Jue Ming", 7: "Wu Gui", 8: "Huo Hai", 9: "Fu Wei"}
}

def get_kua_number(birth_year: int, gender: str) -> int:
    """Calculates Life Gua (Kua Number) based on birth year and gender.
    
    gender: 'male' / 'female' / 'boy' / 'girl' / 'M' / 'F'
    """
    g = gender.strip().lower()
    
    # Single digit reduction of birth year digits
    temp_yr = birth_year
    while temp_yr > 9:
        temp_yr = sum(int(d) for d in str(temp_yr))
    
    if g in ("male", "boy", "m"):
        kua = 11 - temp_yr
        if kua == 5:
            kua = 2  # Male Gua 5 maps to 2 (Kun)
    else:
        kua = temp_yr + 4
        if kua > 9:
            kua = sum(int(d) for d in str(kua))
        if kua == 5:
            kua = 8  # Female Gua 5 maps to 8 (Ken)
            
    return kua

def compute_kua_compatibility(kua1: int, kua2: int) -> dict:
    """Calculates compatibility between two Kua numbers."""
    if kua1 not in KUA_DETAILS or kua2 not in KUA_DETAILS:
        raise ValueError("Invalid Kua number(s). Must be 1, 2, 3, 4, 6, 7, 8, or 9.")
        
    d1 = KUA_DETAILS[kua1]
    d2 = KUA_DETAILS[kua2]
    
    # 1. Group check
    group_match = d1["group"] == d2["group"]
    
    # 2. Element relationship
    # Sheng (Generating): Water->Wood->Fire->Earth->Metal->Water
    # Ke (Controlling): Metal->Wood->Earth->Water->Fire->Metal
    sheng_pairs = {
        ("Water", "Wood"), ("Wood", "Fire"), ("Fire", "Earth"), ("Earth", "Metal"), ("Metal", "Water")
    }
    ke_pairs = {
        ("Metal", "Wood"), ("Wood", "Earth"), ("Earth", "Water"), ("Water", "Fire"), ("Fire", "Metal")
    }
    
    el1, el2 = d1["element"], d2["element"]
    if el1 == el2:
        element_relation = "Same Element (Supportive)"
    elif (el1, el2) in sheng_pairs:
        element_relation = f"{el1} generates {el2} (Nurturing)"
    elif (el2, el1) in sheng_pairs:
        element_relation = f"{el2} generates {el1} (Nurturing)"
    elif (el1, el2) in ke_pairs:
        element_relation = f"{el1} controls {el2} (Controlling)"
    elif (el2, el1) in ke_pairs:
        element_relation = f"{el2} controls {el1} (Controlling)"
    else:
        element_relation = "Neutral Element interaction"
        
    # 3. Ba Zhai Relation
    rel_key = MATCH_MATRIX[kua1][kua2]
    rel_details = KUA_RELATIONS[rel_key]
    
    return {
        "kua1": kua1,
        "kua2": kua2,
        "kua1_details": d1,
        "kua2_details": d2,
        "group_compatibility": "High" if group_match else "Low (East vs West Group Mismatch)",
        "element_compatibility": element_relation,
        "relationship_type": rel_details["name"],
        "relationship_description": rel_details["desc"],
        "score_percent": rel_details["score"]
    }

if __name__ == "__main__":
    # Test for Manoj (1996 Male) and Viveka (2000 Female)
    k1 = get_kua_number(1996, "male")
    k2 = get_kua_number(2000, "female")
    print(f"Manoj Kua: {k1} ({KUA_DETAILS[k1]['trigram']})")
    print(f"Viveka Kua: {k2} ({KUA_DETAILS[k2]['trigram']})")
    
    res = compute_kua_compatibility(k1, k2)
    import json
    print(json.dumps(res, indent=2))
