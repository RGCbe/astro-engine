filepath = "f:/astro/scratch/match_viveka.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

old_r_en = """    r_en = {
        "bride": b, "vedic_kuta": vedic_kuta, "boy_md": boy_md, "girl_md": girl_md, "num_res": num_res,
        "synastry_aspects": synastry_aspects, "pos_aspects": positives, "neg_aspects": negatives,
        "western_score": western_score_pct, "girl_bazi": girl_bazi, "boy_bazi": boy_bazi,
        "girl_animal": girl_animal, "chinese_score": chinese_score, "chinese_desc": chinese_desc_en,
        "girl_tzolkin": girl_tzolkin, "boy_tzolkin": boy_tzolkin, "overall_score": overall_score,
        "boy_west_signs": f"Sun in {boy_west_planets['Sun']['sign']}, Moon in {boy_west_planets['Moon']['sign']}, Ascendant in {boy_west['calculations']['ascendant']['sign']}",
        "girl_west_signs": f"Sun in {girl_west_planets['Sun']['sign']}, Moon in {girl_west_planets['Moon']['sign']}, Ascendant in {girl_west['calculations']['ascendant']['sign']}",
        "boy_moon_lon": boy_moon_lon,
        "girl_moon_lon": girl_moon_lon,
        "boy_lagna_en": boy_sid["planet_positions"]["Lagna"]["rasi"],
        "boy_lagna_ta": boy_sid["planet_positions"]["Lagna"]["rasi_tamil"],
        "girl_lagna_en": girl_sid["planet_positions"]["Lagna"]["rasi"],
        "girl_lagna_ta": girl_sid["planet_positions"]["Lagna"]["rasi_tamil"],
    }"""

new_r_en = """    r_en = {
        "bride": b, "vedic_kuta": vedic_kuta, "boy_md": boy_md, "girl_md": girl_md, "num_res": num_res,
        "synastry_aspects": synastry_aspects, "pos_aspects": positives, "neg_aspects": negatives,
        "western_score": western_score_pct, "girl_bazi": girl_bazi, "boy_bazi": boy_bazi,
        "boy_bazi_raw": boy_chinese["calculations"]["bazi_details"], "girl_bazi_raw": girl_chinese["calculations"]["bazi_details"],
        "boy_west_planets": boy_west_planets, "girl_west_planets": girl_west_planets,
        "boy_west_asc": boy_west["calculations"]["ascendant"]["longitude"], "girl_west_asc": girl_west["calculations"]["ascendant"]["longitude"],
        "girl_animal": girl_animal, "chinese_score": chinese_score, "chinese_desc": chinese_desc_en,
        "girl_tzolkin": girl_tzolkin, "boy_tzolkin": boy_tzolkin, "overall_score": overall_score,
        "boy_west_signs": f"Sun in {boy_west_planets['Sun']['sign']}, Moon in {boy_west_planets['Moon']['sign']}, Ascendant in {boy_west['calculations']['ascendant']['sign']}",
        "girl_west_signs": f"Sun in {girl_west_planets['Sun']['sign']}, Moon in {girl_west_planets['Moon']['sign']}, Ascendant in {girl_west['calculations']['ascendant']['sign']}",
        "boy_moon_lon": boy_moon_lon,
        "girl_moon_lon": girl_moon_lon,
        "boy_lagna_en": boy_sid["planet_positions"]["Lagna"]["rasi"],
        "boy_lagna_ta": boy_sid["planet_positions"]["Lagna"]["rasi_tamil"],
        "girl_lagna_en": girl_sid["planet_positions"]["Lagna"]["rasi"],
        "girl_lagna_ta": girl_sid["planet_positions"]["Lagna"]["rasi_tamil"],
    }"""

old_r_ta = """    r_ta = {
        "bride": b, "vedic_kuta": vedic_kuta, "boy_md": boy_md, "girl_md": girl_md, "num_res": num_res,
        "synastry_aspects": synastry_aspects, "pos_aspects": positives, "neg_aspects": negatives,
        "western_score": western_score_pct, "girl_bazi": girl_bazi, "boy_bazi": boy_bazi,
        "girl_animal": girl_animal, "chinese_score": chinese_score, "chinese_desc": chinese_desc_ta,
        "girl_tzolkin": girl_tzolkin, "boy_tzolkin": boy_tzolkin, "overall_score": overall_score,
        "boy_west_signs": f"Sun in {boy_west_planets['Sun']['sign']}, Moon in {boy_west_planets['Moon']['sign']}, Ascendant in {boy_west['calculations']['ascendant']['sign']}",
        "girl_west_signs": f"Sun in {girl_west_planets['Sun']['sign']}, Moon in {girl_west_planets['Moon']['sign']}, Ascendant in {girl_west['calculations']['ascendant']['sign']}",
        "boy_moon_lon": boy_moon_lon,
        "girl_moon_lon": girl_moon_lon,
        "boy_lagna_en": boy_sid["planet_positions"]["Lagna"]["rasi"],
        "boy_lagna_ta": boy_sid["planet_positions"]["Lagna"]["rasi_tamil"],
        "girl_lagna_en": girl_sid["planet_positions"]["Lagna"]["rasi"],
        "girl_lagna_ta": girl_sid["planet_positions"]["Lagna"]["rasi_tamil"],
    }"""

new_r_ta = """    r_ta = {
        "bride": b, "vedic_kuta": vedic_kuta, "boy_md": boy_md, "girl_md": girl_md, "num_res": num_res,
        "synastry_aspects": synastry_aspects, "pos_aspects": positives, "neg_aspects": negatives,
        "western_score": western_score_pct, "girl_bazi": girl_bazi, "boy_bazi": boy_bazi,
        "boy_bazi_raw": boy_chinese["calculations"]["bazi_details"], "girl_bazi_raw": girl_chinese["calculations"]["bazi_details"],
        "boy_west_planets": boy_west_planets, "girl_west_planets": girl_west_planets,
        "boy_west_asc": boy_west["calculations"]["ascendant"]["longitude"], "girl_west_asc": girl_west["calculations"]["ascendant"]["longitude"],
        "girl_animal": girl_animal, "chinese_score": chinese_score, "chinese_desc": chinese_desc_ta,
        "girl_tzolkin": girl_tzolkin, "boy_tzolkin": boy_tzolkin, "overall_score": overall_score,
        "boy_west_signs": f"Sun in {boy_west_planets['Sun']['sign']}, Moon in {boy_west_planets['Moon']['sign']}, Ascendant in {boy_west['calculations']['ascendant']['sign']}",
        "girl_west_signs": f"Sun in {girl_west_planets['Sun']['sign']}, Moon in {girl_west_planets['Moon']['sign']}, Ascendant in {girl_west['calculations']['ascendant']['sign']}",
        "boy_moon_lon": boy_moon_lon,
        "girl_moon_lon": girl_moon_lon,
        "boy_lagna_en": boy_sid["planet_positions"]["Lagna"]["rasi"],
        "boy_lagna_ta": boy_sid["planet_positions"]["Lagna"]["rasi_tamil"],
        "girl_lagna_en": girl_sid["planet_positions"]["Lagna"]["rasi"],
        "girl_lagna_ta": girl_sid["planet_positions"]["Lagna"]["rasi_tamil"],
    }"""

# Clean windows carriage return disparities
code = code.replace(old_r_en.replace("\r", ""), new_r_en.replace("\r", ""))
code = code.replace(old_r_ta.replace("\r", ""), new_r_ta.replace("\r", ""))
code = code.replace(old_r_en, new_r_en)
code = code.replace(old_r_ta, new_r_ta)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Match Viveka raw parameter patching complete.")
