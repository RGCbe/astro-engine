"""
Chinese Astrology Engine — GAC Standard.
Handles:
    - BaZi (Four Pillars of Destiny) Stem/Branch mapping
    - Five Elements distribution and Day Master evaluation
    - Zi Wei Dou Shu (Purple Star Astrology) Palace & Major Star plotting
"""
import datetime as dt
import math

# Sexagenary Stems and Branches (English and Chinese transliterations)
STEMS = [
    {"name": "Jia", "element": "Wood", "polarity": "Yang", "han": "甲"},
    {"name": "Yi", "element": "Wood", "polarity": "Yin", "han": "乙"},
    {"name": "Bing", "element": "Fire", "polarity": "Yang", "han": "丙"},
    {"name": "Ding", "element": "Fire", "polarity": "Yin", "han": "丁"},
    {"name": "Wu", "element": "Earth", "polarity": "Yang", "han": "戊"},
    {"name": "Ji", "element": "Earth", "polarity": "Yin", "han": "己"},
    {"name": "Geng", "element": "Metal", "polarity": "Yang", "han": "庚"},
    {"name": "Xin", "element": "Metal", "polarity": "Yin", "han": "辛"},
    {"name": "Ren", "element": "Water", "polarity": "Yang", "han": "壬"},
    {"name": "Gui", "element": "Water", "polarity": "Yin", "han": "癸"}
]

BRANCHES = [
    {"name": "Zi", "animal": "Rat", "element": "Water", "polarity": "Yang", "han": "子"},
    {"name": "Chou", "animal": "Ox", "element": "Earth", "polarity": "Yin", "han": "丑"},
    {"name": "Yin", "animal": "Tiger", "element": "Wood", "polarity": "Yang", "han": "寅"},
    {"name": "Mao", "animal": "Rabbit", "element": "Wood", "polarity": "Yin", "han": "卯"},
    {"name": "Chen", "animal": "Dragon", "element": "Earth", "polarity": "Yang", "han": "辰"},
    {"name": "Si", "animal": "Snake", "element": "Fire", "polarity": "Yin", "han": "巳"},
    {"name": "Wu", "animal": "Horse", "element": "Fire", "polarity": "Yang", "han": "午"},
    {"name": "Wei", "animal": "Goat", "element": "Earth", "polarity": "Yin", "han": "未"},
    {"name": "Shen", "animal": "Monkey", "element": "Metal", "polarity": "Yang", "han": "申"},
    {"name": "You", "animal": "Rooster", "element": "Metal", "polarity": "Yin", "han": "酉"},
    {"name": "Xu", "animal": "Dog", "element": "Earth", "polarity": "Yang", "han": "戌"},
    {"name": "Hai", "animal": "Pig", "element": "Water", "polarity": "Yin", "han": "亥"}
]

# BaZi Month boundaries based on Solar Terms (approximate Gregorian dates)
SOLAR_MONTHS = [
    (2, 4),   # Lichun (Spring begins, month of Tiger / Yin)
    (3, 5),   # Jingzhe (month of Rabbit / Mao)
    (4, 4),   # Qingming (month of Dragon / Chen)
    (5, 5),   # Lixia (month of Snake / Si)
    (6, 5),   # Mangzhong (month of Horse / Wu)
    (7, 7),   # Xiaoshu (month of Goat / Wei)
    (8, 7),   # Liqiu (month of Monkey / Shen)
    (9, 7),   # Bailu (month of Rooster / You)
    (10, 8),  # Hanlu (month of Dog / Xu)
    (11, 7),  # Lidong (month of Pig / Hai)
    (12, 7),  # Daxue (month of Rat / Zi)
    (1, 5)    # Xiaohan (month of Ox / Chou)
]

def get_julian_day(year: int, month: int, day: int, hour: int, minute: int) -> float:
    """Standard Julian Day calculation."""
    if month <= 2:
        year -= 1
        month += 12
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5
    jd += (hour + minute / 60.0) / 24.0
    return jd

def get_bazi_pillars(year: int, month: int, day: int, hour: int, minute: int) -> dict:
    """Calculates the 4 pillars (Year, Month, Day, Hour Stems and Branches)."""
    # 1. Year Pillar
    # Chinese Solar year starts at Lichun (approx Feb 4).
    # If birth is before Feb 4, use the previous year.
    solar_year = year
    if month < 2 or (month == 2 and day < 4):
        solar_year -= 1
        
    year_offset = (solar_year - 4) % 60
    year_stem_idx = year_offset % 10
    year_branch_idx = year_offset % 12
    
    # 2. Month Pillar
    # Determine the solar term month index (0 for Tiger/Yin, 1 for Rabbit/Mao, etc.)
    # Baselines are mapped from Lichun (Feb 4).
    month_idx = 0
    for idx, (m, d) in enumerate(SOLAR_MONTHS):
        next_idx = (idx + 1) % 12
        nm, nd = SOLAR_MONTHS[next_idx]
        
        # Check if between current and next solar term
        if (month == m and day >= d) or (month == nm and day < nd) or (m > nm and (month == m and day >= d or month == nm and day < nd)):
            month_idx = idx
            break
            
    # Derive month stem using the "Five Tiger Rule" (Month stem based on Year stem)
    month_branch_idx = (month_idx + 2) % 12  # Starts with Yin (Tiger, Branch Index 2)
    month_stem_start = (year_stem_idx * 2 + 2) % 10
    month_stem_idx = (month_stem_start + month_idx) % 10
    
    # 3. Day Pillar
    # Calculate JD of birth at local time
    jd = get_julian_day(year, month, day, hour, minute)
    # JD 2440000 (May 23, 1968) corresponds to day 17 (Geng-Chen)
    day_offset = int(math.floor(jd - 2440000 + 17)) % 60
    day_stem_idx = day_offset % 10
    day_branch_idx = day_offset % 12
    
    # 4. Hour Pillar
    # Chinese double hours start from 23:00 - 01:00 (Zi branch)
    h_adj = (hour + 1) % 24
    hour_branch_idx = h_adj // 2
    
    # Five Rat Rule (Hour stem based on Day stem)
    hour_stem_start = (day_stem_idx * 2) % 10
    hour_stem_idx = (hour_stem_start + hour_branch_idx) % 10
    
    return {
        "Year": {"Stem": STEMS[year_stem_idx], "Branch": BRANCHES[year_branch_idx]},
        "Month": {"Stem": STEMS[month_stem_idx], "Branch": BRANCHES[month_branch_idx]},
        "Day": {"Stem": STEMS[day_stem_idx], "Branch": BRANCHES[day_branch_idx]},
        "Hour": {"Stem": STEMS[hour_stem_idx], "Branch": BRANCHES[hour_branch_idx]}
    }

def analyze_elements(pillars: dict) -> dict:
    """Calculates Five Element balances and Day Master strength."""
    elements = {"Wood": 0, "Fire": 0, "Earth": 0, "Metal": 0, "Water": 0}
    
    # Add Stems (weight 1.5 for Day Master, 1.0 for others)
    for p_name, p_val in pillars.items():
        weight = 1.5 if p_name == "Day" else 1.0
        elements[p_val["Stem"]["element"]] += weight
        elements[p_val["Branch"]["element"]] += weight
        
    total = sum(elements.values())
    ratios = {k: round((v / total) * 100, 2) for k, v in elements.items()}
    
    day_master = pillars["Day"]["Stem"]
    dm_element = day_master["element"]
    
    # Self-supportive elements: Self element + nurturing element (e.g. Wood is nurtured by Water)
    nurturing = {
        "Wood": "Water",
        "Fire": "Wood",
        "Earth": "Fire",
        "Metal": "Earth",
        "Water": "Metal"
    }
    
    support = elements[dm_element] + elements[nurturing[dm_element]]
    is_strong = support > (total * 0.45)
    
    return {
        "day_master": {
            "name": day_master["name"],
            "element": dm_element,
            "polarity": day_master["polarity"],
            "han": day_master["han"]
        },
        "elements_distribution": ratios,
        "self_strength": "Strong Self" if is_strong else "Weak Self",
        "favorable_elements": [nurturing[dm_element], dm_element] if not is_strong else [k for k in elements if k != dm_element and k != nurturing[dm_element]]
    }

def compute_zi_wei_dou_shu(month: int, hour_branch_idx: int) -> dict:
    """Simple Zi Wei Dou Shu palace and star mapper.
    Plots 12 palaces and computes active star distribution based on Month & Hour.
    """
    # 12 Palaces in standard clockwise order starting from Zi
    palace_names = ["Self", "Siblings", "Spouse", "Children", "Wealth", "Health", 
                    "Travel", "Friends", "Career", "Property", "Happiness", "Parents"]
    
    # Determine the index of the "Self" palace.
    # Standard formula: (1 + Month - Hour_Branch_Idx) % 12
    self_palace_idx = (1 + month - hour_branch_idx) % 12
    
    palaces = {}
    for idx, name in enumerate(palace_names):
        branch_idx = (self_palace_idx + idx) % 12
        palaces[BRANCHES[branch_idx]["name"]] = name
        
    # Place Major Stars (e.g. Zi Wei - Purple Emperor)
    # Zi Wei positioning has high lunar-day complexity. We place it based on month/hour:
    zi_wei_idx = (month + hour_branch_idx) % 12
    tian_fu_idx = (12 - zi_wei_idx) % 12
    
    stars = {
        "Zi Wei (Emperor)": BRANCHES[zi_wei_idx]["name"],
        "Tian Fu (Treasury)": BRANCHES[tian_fu_idx]["name"],
        "Tai Yang (Sun)": BRANCHES[(zi_wei_idx + 3) % 12]["name"],
        "Tai Yin (Moon)": BRANCHES[(tian_fu_idx + 3) % 12]["name"]
    }
    
    return {
        "palaces_mapping": palaces,
        "major_stars_placement": stars
    }

def compute_chinese_chart(date: str, time: str, tz_hours: float) -> dict:
    """Entry point for the GAC Chinese Astrology calculation."""
    y, m, d = (int(x) for x in date.split("-"))
    hh, mm = (int(x) for x in time.split(":"))
    
    # Calculate Pillars
    pillars = get_bazi_pillars(y, m, d, hh, mm)
    
    # Elements Analysis
    elements = analyze_elements(pillars)
    
    # Zi Wei Dou Shu
    h_adj = (hh + 1) % 24
    hour_branch_idx = h_adj // 2
    zi_wei = compute_zi_wei_dou_shu(m, hour_branch_idx)
    
    return {
        "framework": "Chinese BaZi & Zi Wei Dou Shu",
        "calculations": {
            "bazi_pillars": {
                "Year": f"{pillars['Year']['Stem']['name']}-{pillars['Year']['Branch']['name']} ({pillars['Year']['Stem']['han']}{pillars['Year']['Branch']['han']})",
                "Month": f"{pillars['Month']['Stem']['name']}-{pillars['Month']['Branch']['name']} ({pillars['Month']['Stem']['han']}{pillars['Month']['Branch']['han']})",
                "Day": f"{pillars['Day']['Stem']['name']}-{pillars['Day']['Branch']['name']} ({pillars['Day']['Stem']['han']}{pillars['Day']['Branch']['han']})",
                "Hour": f"{pillars['Hour']['Stem']['name']}-{pillars['Hour']['Branch']['name']} ({pillars['Hour']['Stem']['han']}{pillars['Hour']['Branch']['han']})"
            },
            "bazi_details": pillars,
            "elements_analysis": elements,
            "zi_wei_dou_shu": zi_wei
        }
    }
