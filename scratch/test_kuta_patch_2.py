import re

filepath = "f:/astro/engine/kuta.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# 2. Replace _bhakoot definition
bhakoot_pattern = r"def _bhakoot\(boy_sign:\s*str,\s*girl_sign:\s*str\)\s*->\s*int:\s*\n\s*\"\"\"Distance[^\"]*\"\"\"\s*\n\s*bi\s*=\s*SIGNS\.index\(boy_sign\);\s*gi\s*=\s*SIGNS\.index\(girl_sign\)\s*\n\s*diff\s*=\s*abs\(bi\s*-\s*gi\)\s*\n\s*if\s*diff\s*>\s*6:\s*\n\s*diff\s*=\s*12\s*-\s*diff\s*\n\s*bad_distances\s*=\s*\{1,\s*5\}\s*\n\s*return\s*0\s*if\s*diff\s*in\s*bad_distances\s*else\s*7"

new_bhakoot_def = """def _bhakoot(boy_sign: str, girl_sign: str) -> int:
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
        
    return 0"""

if "RASHI_LORDS_BH" not in code:
    code, count2 = re.subn(bhakoot_pattern, new_bhakoot_def, code)
    print(f"Patched _bhakoot definition count: {count2}")
else:
    print("_bhakoot definition already patched.")
    count2 = 0

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch 2 fix complete.")
