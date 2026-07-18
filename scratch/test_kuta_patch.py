import re

filepath = "f:/astro/engine/kuta.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Replace _nadi definition
old_nadi_def = """def _nadi(boy_nak_idx: int, girl_nak_idx: int) -> int:
    \"\"\"Same nadi  0 (Nadi Dosha). Different  8.\"\"\"
    return 0 if NADI[boy_nak_idx] == NADI[girl_nak_idx] else 8"""

# Let's search with regex to handle whitespace or minor spelling/OCR variances
nadi_pattern = r"def _nadi\(boy_nak_idx: int,\s*girl_nak_idx: int\)\s*->\s*int:\s*\n\s*\"\"\"[^\"]*\"\"\"\s*\n\s*return\s*0\s*if\s*NADI\[boy_nak_idx\]\s*==\s*NADI\[girl_nak_idx\]\s*else\s*8"

new_nadi_def = """def _nadi(boy_nak_idx: int, girl_nak_idx: int, boy_sign: str = "", girl_sign: str = "") -> int:
    \"\"\"Same nadi -> 0 (Nadi Dosha). Different -> 8.
    
    Includes classical cancellation rules from Muhurta Chintamani:
    1. If either Nakshatra is Rohini, Mrigashira, Ardra, Pushya, Krittika, Jyeshtha, Shravana, Uttara Bhadrapada, or Revati.
    2. Same Rasi, different Nakshatras.
    3. Same Nakshatra, different Rasis.
    \"\"\"
    # 1. Exempted Nakshatras (Krittika, Rohini, Mrigashira, Ardra, Pushya, Jyeshtha, Shravana, Uttara Bhadrapada, Revati)
    exempted_nak = {2, 3, 4, 5, 7, 17, 21, 25, 26}
    if boy_nak_idx in exempted_nak or girl_nak_idx in exempted_nak:
        return 8
        
    # Look up rasi indices if signs are provided
    if boy_sign and girl_sign and boy_sign in SIGNS and girl_sign in SIGNS:
        bi = SIGNS.index(boy_sign)
        gi = SIGNS.index(girl_sign)
        # 2. Same Rasi, different Nakshatras
        if bi == gi and boy_nak_idx != girl_nak_idx:
            return 8
        # 3. Same Nakshatra, different Rasis
        if boy_nak_idx == girl_nak_idx and bi != gi:
            return 8

    return 0 if NADI[boy_nak_idx] == NADI[girl_nak_idx] else 8"""

if "exempted_nak" not in code:
    # Use re.sub to perform the replace
    code, count = re.subn(nadi_pattern, new_nadi_def, code)
    print(f"Patched _nadi definition count: {count}")
else:
    print("_nadi definition already patched.")

# 2. Replace _nadi call in match_kuta
old_nadi_call = "nad = _nadi(boy_nak, girl_nak)"
new_nadi_call = "nad = _nadi(boy_nak, girl_nak, boy_sign, girl_sign)"

if new_nadi_call not in code:
    code = code.replace(old_nadi_call, new_nadi_call)
    print("Patched _nadi call in match_kuta.")
else:
    print("_nadi call already patched.")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Patch complete.")
