"""
Unified Multi-Paradigm Numerology Engine — GAC Standard.
Integrates:
    - Tamil/Chaldæan Vidhi & Bhagya Systems (from engine/tamil_numerology.py)
    - Pythagorean Triad Calculations (Expression, Soul Urge, Personality)
    - Master Number (11, 22, 33) Vibrations
    - Lo Shu Grid Plane Matrices & Missing Numbers
    - Temporal Personal Cycles (Personal Year, Month, Day)
"""
import datetime as dt
import re
from engine.tamil_numerology import compute as compute_tamil_numerology

PYTHAGOREAN_VALUES = {
    'A': 1, 'J': 1, 'S': 1,
    'B': 2, 'K': 2, 'T': 2,
    'C': 3, 'L': 3, 'U': 3,
    'D': 4, 'M': 4, 'V': 4,
    'E': 5, 'N': 5, 'W': 5,
    'F': 6, 'O': 6, 'X': 6,
    'G': 7, 'P': 7, 'Y': 7,
    'H': 8, 'Q': 8, 'Z': 8,
    'I': 9, 'R': 9
}

VOWELS = {'A', 'E', 'I', 'O', 'U'}

def _digit_root(n: int) -> int:
    """Standard digital root reduction. Sums digits until a single digit is reached."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n

def reduce_pythagorean(n: int) -> int:
    """Reduces value to a single digit but preserves Master Numbers (11, 22, 33)."""
    if n in {11, 22, 33}:
        return n
    while n > 9:
        temp = sum(int(d) for d in str(n))
        if temp in {11, 22, 33}:
            return temp
        n = temp
    return n

def normalize_name(name: str) -> str:
    """Sanitizes name string into uppercase A-Z characters."""
    return re.sub(r'[^A-Z]', '', name.upper())

def classify_letters(name: str) -> tuple[str, str]:
    """Classifies letters in a normalized name into vowels and consonants.
    Applies contextual rules for 'Y'.
    """
    normalized = normalize_name(name)
    vowels_str = []
    consonants_str = []
    
    n_chars = len(normalized)
    for i, char in enumerate(normalized):
        prev_char = normalized[i - 1] if i > 0 else None
        next_char = normalized[i + 1] if i < n_chars - 1 else None
        
        # Check standard vowels
        if char in VOWELS:
            vowels_str.append(char)
        # Check Y vowel rule: Y is a vowel if surrounded by consonants or at boundaries with consonants
        elif char == 'Y':
            prev_is_consonant = prev_char is None or (prev_char.isalpha() and prev_char not in VOWELS)
            next_is_consonant = next_char is None or (next_char.isalpha() and next_char not in VOWELS)
            if prev_is_consonant and next_is_consonant:
                vowels_str.append(char)
            else:
                consonants_str.append(char)
        else:
            consonants_str.append(char)
            
    return "".join(vowels_str), "".join(consonants_str)

def compute_pythagorean_triad(name: str) -> dict:
    """Calculates the Pythagorean Expression, Soul Urge, and Personality Numbers.
    Detects Master Numbers.
    """
    normalized = normalize_name(name)
    vowels_str, consonants_str = classify_letters(name)
    
    # 1. Expression Number (vowels + consonants)
    expr_sum = sum(PYTHAGOREAN_VALUES[c] for c in normalized)
    expression_num = reduce_pythagorean(expr_sum)
    
    # 2. Soul Urge Number (vowels only)
    soul_sum = sum(PYTHAGOREAN_VALUES[c] for c in vowels_str) if vowels_str else 0
    soul_urge_num = reduce_pythagorean(soul_sum)
    
    # 3. Personality Number (consonants only)
    pers_sum = sum(PYTHAGOREAN_VALUES[c] for c in consonants_str) if consonants_str else 0
    personality_num = reduce_pythagorean(pers_sum)
    
    master_desc = {
        11: "Master Number 11: The Visionary, high-vibrational spiritual channel, intuitive leader.",
        22: "Master Number 22: The Master Builder, capable of manifesting massive structural realities.",
        33: "Master Number 33: The Master Teacher, focusing on universal love, healing, and service."
    }
    
    return {
        "sanitized_name": normalized,
        "expression_number": expression_num,
        "expression_note": master_desc.get(expression_num, f"Expression Number {expression_num}."),
        "soul_urge_number": soul_urge_num,
        "soul_urge_note": master_desc.get(soul_urge_num, f"Soul Urge Number {soul_urge_num}."),
        "personality_number": personality_num,
        "personality_note": master_desc.get(personality_num, f"Personality Number {personality_num}.")
    }

def compute_lo_shu_grid(birth_date_str: str) -> dict:
    """Maps birth date digits into the 3x3 Lo Shu grid and evaluates active planes."""
    # Extract digits, ignore zeros and non-digits
    digits = [int(c) for c in birth_date_str if c.isdigit() and c != '0']
    
    # Counts of each digit 1-9
    counts = {i: digits.count(i) for i in range(1, 10)}
    
    # Construct Lo Shu grid representation
    # Standard Lo Shu layout:
    # 4  9  2
    # 3  5  7
    # 8  1  6
    grid = [
        [counts[4], counts[9], counts[2]],
        [counts[3], counts[5], counts[7]],
        [counts[8], counts[1], counts[6]]
    ]
    
    # Define Planes of Destiny
    planes = {
        "Mental Plane (4-9-2)": {"digits": [4, 9, 2], "score": sum(1 for x in [4, 9, 2] if counts[x] > 0)},
        "Emotional Plane (3-5-7)": {"digits": [3, 5, 7], "score": sum(1 for x in [3, 5, 7] if counts[x] > 0)},
        "Physical Plane (8-1-6)": {"digits": [8, 1, 6], "score": sum(1 for x in [8, 1, 6] if counts[x] > 0)},
        "Will Power Line (9-5-1)": {"digits": [9, 5, 1], "score": sum(1 for x in [9, 5, 1] if counts[x] > 0)},
        "Action Line (2-7-6)": {"digits": [2, 7, 6], "score": sum(1 for x in [2, 7, 6] if counts[x] > 0)},
        "Thought Line (4-3-8)": {"digits": [4, 3, 8], "score": sum(1 for x in [4, 3, 8] if counts[x] > 0)},
        "Spiritual Diagonal (4-5-6)": {"digits": [4, 5, 6], "score": sum(1 for x in [4, 5, 6] if counts[x] > 0)},
        "Creative Diagonal (2-5-8)": {"digits": [2, 5, 8], "score": sum(1 for x in [2, 5, 8] if counts[x] > 0)}
    }
    
    active_planes = {}
    for name, data in planes.items():
        if data["score"] == 3:
            active_planes[name] = "Fully Active (Peak Plane Strength)"
        elif data["score"] == 2:
            active_planes[name] = "Partially Active (Moderate Plane Strength)"
            
    missing_numbers = [i for i in range(1, 10) if counts[i] == 0]
    
    return {
        "grid": grid,
        "digit_counts": counts,
        "active_planes": active_planes,
        "missing_numbers": missing_numbers
    }

def compute_personal_cycles(birth_date_str: str, target_date_str: str | None = None) -> dict:
    """Calculates Personal Year, Personal Month, and Personal Day for a given target date."""
    b_y, b_m, b_d = (int(x) for x in birth_date_str.split("-"))
    
    if target_date_str:
        t_y, t_m, t_d = (int(x) for x in target_date_str.split("-"))
    else:
        today = dt.date.today()
        t_y, t_m, t_d = today.year, today.month, today.day
        
    personal_year = _digit_root(b_d + b_m + t_y)
    personal_month = _digit_root(personal_year + t_m)
    personal_day = _digit_root(personal_month + t_d)
    
    year_meanings = {
        1: "Beginnings, initiation, independence, and taking bold action.",
        2: "Cooperation, balance, waiting, partnerships, and sensitivity.",
        3: "Creativity, social expansion, expression, communication, and play.",
        4: "Structure, hard work, boundaries, building foundations, and discipline.",
        5: "Change, freedom, travel, versatility, and sudden opportunities.",
        6: "Family responsibility, home life, harmony, service, and healing.",
        7: "Introspection, study, spiritual development, research, and rest.",
        8: "Business, material success, authority, personal power, and financial gains.",
        9: "Completion, closure, letting go of old patterns, and universal love."
    }
    
    return {
        "target_date": f"{t_y:04d}-{t_m:02d}-{t_d:02d}",
        "personal_year": personal_year,
        "personal_year_meaning": year_meanings[personal_year],
        "personal_month": personal_month,
        "personal_day": personal_day
    }

def compute_numerology_report(name: str, birth_date_str: str, target_date_str: str | None = None) -> dict:
    """Entry point for the GAC Unified Numerology Engine."""
    y, m, d = (int(x) for x in birth_date_str.split("-"))
    b_date = dt.date(y, m, d)
    
    # 1. Tamil Chaldæan Calculations
    tamil_rpt = compute_tamil_numerology(b_date)
    tamil_details = {
        "vidhi_number": tamil_rpt.vidhi_number,
        "vidhi_planet": tamil_rpt.vidhi_planet,
        "bhagya_number": tamil_rpt.bhagya_number,
        "bhagya_planet": tamil_rpt.bhagya_planet,
        "lucky_days": tamil_rpt.lucky_days,
        "lucky_direction": tamil_rpt.lucky_direction,
        "lucky_dates": tamil_rpt.lucky_dates,
        "lucky_gemstone": tamil_rpt.lucky_gemstone,
        "friendly_numbers": tamil_rpt.friendly_numbers,
        "hostile_numbers": tamil_rpt.hostile_numbers,
        "neutral_numbers": tamil_rpt.neutral_numbers,
        "lucky_color": tamil_rpt.lucky_color,
        "deity": tamil_rpt.deity,
        "higher_deity": tamil_rpt.higher_deity
    }
    
    # 2. Pythagorean Triad & Vowel Check
    pythagorean = compute_pythagorean_triad(name)
    
    # 3. Lo Shu Grid Magic Square
    lo_shu = compute_lo_shu_grid(birth_date_str)
    
    # 4. Temporal Personal Cycles
    cycles = compute_personal_cycles(birth_date_str, target_date_str)
    
    return {
        "framework": "GAC Unified Multi-Paradigm Numerology Engine",
        "calculations": {
            "tamil_chaldean": tamil_details,
            "pythagorean_triad": pythagorean,
            "lo_shu_grid": lo_shu,
            "temporal_cycles": cycles
        }
    }
