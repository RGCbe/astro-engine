filepath = "f:/astro/engine/kuta.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# Find def _bhakoot
start_idx = code.find("def _bhakoot(")
if start_idx == -1:
    print("Could not find def _bhakoot")
    exit(1)

# Find the next def, which is def _nadi
end_idx = code.find("def _nadi(", start_idx)
if end_idx == -1:
    print("Could not find def _nadi after def _bhakoot")
    exit(1)

# Extract old block
old_block = code[start_idx:end_idx]

# New function block
new_block = """def _bhakoot(boy_sign: str, girl_sign: str) -> int:
    \"\"\"Distance between Moon signs. 6/8 and 9/5 and 12/2 -> 0; else 7.
    
    Includes classical cancellation rules from Muhurta Chintamani:
    1. Same Rashi Lord (Aries/Scorpio, Taurus/Libra, Capricorn/Aquarius).
    2. Mutual Friendship of Rashi Lords:
       - Leo (Sun) and Cancer (Moon)
       - Cancer (Moon) and Sagittarius (Jupiter)
       - Leo (Sun) and Pisces (Jupiter)
       - Capricorn (Saturn) and Gemini (Mercury)
       - Pisces (Jupiter) and Aries (Mars)
    \"\"\"
    bi = SIGNS.index(boy_sign); gi = SIGNS.index(girl_sign)
    diff = abs(bi - gi)
    if diff > 6:
        diff = 12 - diff
    
    bad_distances = {1, 5}  # 2-12 and 6-8 axes
    if diff not in bad_distances:
        return 7
        
    # Check for Bhakoot Dosha cancellation
    RASHI_LORDS_BH = {
        "Aries": "Mars", "Scorpio": "Mars",
        "Taurus": "Venus", "Libra": "Venus",
        "Gemini": "Mercury", "Virgo": "Mercury",
        "Cancer": "Moon", "Leo": "Sun",
        "Sagittarius": "Jupiter", "Pisces": "Jupiter",
        "Capricorn": "Saturn", "Aquarius": "Saturn"
    }
    
    lord1 = RASHI_LORDS_BH.get(boy_sign)
    lord2 = RASHI_LORDS_BH.get(girl_sign)
    
    # Rule 1: Same Rashi Lord
    if lord1 == lord2 and lord1 is not None:
        return 7
        
    # Rule 2: Mutual friendship of Rashi Lords
    FRIENDS = {
        "Sun": {"Moon", "Mars", "Jupiter"},
        "Moon": {"Sun", "Mercury"},
        "Mars": {"Sun", "Moon", "Jupiter"},
        "Mercury": {"Sun", "Venus"},
        "Jupiter": {"Sun", "Moon", "Mars"},
        "Venus": {"Mercury", "Saturn"},
        "Saturn": {"Mercury", "Venus"}
    }
    
    if lord1 in FRIENDS and lord2 in FRIENDS[lord1] and lord2 in FRIENDS and lord1 in FRIENDS[lord2]:
        return 7
        
    return 0

# Newline to separate from def _nadi
"""

if "RASHI_LORDS_BH" not in code:
    code = code[:start_idx] + new_block + code[end_idx:]
    print("Replaced _bhakoot block successfully.")
else:
    print("_bhakoot already patched.")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch 3 complete.")
