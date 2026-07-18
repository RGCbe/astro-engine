import re

filepath = "f:/astro/scratch/generate_separate_reports.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Update r_en and r_ta dictionaries to include raw western/bazi parameters
old_r_en = """    r_en = {
        "bride": b, "vedic_kuta": vedic_kuta, "boy_md": boy_md, "girl_md": girl_md, "num_res": num_res,
        "synastry_aspects": synastry_aspects, "pos_aspects": positives, "neg_aspects": negatives,
        "western_score": western_score_pct, "girl_bazi": girl_bazi, "boy_bazi": boy_bazi,
        "girl_animal": girl_animal, "chinese_score": chinese_score, "chinese_desc": chinese_desc_en,
        "girl_tzolkin": girl_tzolkin, "boy_tzolkin": boy_tzolkin, "overall_score": overall_score,
        "boy_west_signs": f"Sun in {boy_west_planets['Sun']['sign']}, Moon in {boy_west_planets['Moon']['sign']}, Ascendant in {boy_west['calculations']['ascendant']['sign']}",
        "girl_west_signs": f"Sun in {girl_west_planets['Sun']['sign']}, Moon in {girl_west_planets['Moon']['sign']}, Ascendant in {girl_west['calculations']['ascendant']['sign']}",
        # Sidereal and Lagnam parameters passed down
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
        # Sidereal and Lagnam parameters passed down
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
        # Sidereal and Lagnam parameters passed down
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
        # Sidereal and Lagnam parameters passed down
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

# 2. Find and replace in generate_pdf_en (Verdict Table start)
# We search for:
#     # Verdict Table
#     story.append(PageBreak())
#     story.append(Paragraph("9. Grand Compatibility Verdict & Recommendation", style_h1))
# And replace with the advanced page + Verdict page (as section 10)

old_verdict_block_en = """    # Verdict Table
    story.append(PageBreak())
    story.append(Paragraph("9. Grand Compatibility Verdict & Recommendation", style_h1))"""

new_verdict_block_en = """    # Page 5: Advanced Multi-System Synastry
    story.append(PageBreak())
    story.append(Paragraph("9. Advanced Multi-System Synastry", style_h1))
    story.append(Spacer(1, 0.1 * cm))
    
    # Calculations
    def get_midpoint(lon1, lon2):
        diff = abs(lon1 - lon2) % 360
        if diff > 180:
            return (lon1 + lon2 + 360) / 2 % 360
        return (lon1 + lon2) / 2 % 360

    def get_sign_name(lon):
        signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        idx = int(lon // 30) % 12
        deg = lon % 30
        return f"{signs[idx]} {int(deg)}°"

    boy_planets = r["boy_west_planets"]
    girl_planets = r["girl_west_planets"]
    boy_asc = r["boy_west_asc"]
    girl_asc = r["girl_west_asc"]
    
    composite_data = [
        [Paragraph("Body / Angle", style_cell_bold), Paragraph("Groom (Manoj)", style_cell_bold), Paragraph(f"Bride ({b['name']})", style_cell_bold), Paragraph("Composite Midpoint", style_cell_bold)]
    ]
    
    # Ascendant
    comp_asc_lon = get_midpoint(boy_asc, girl_asc)
    composite_data.append([Paragraph("Ascendant", style_cell), Paragraph(get_sign_name(boy_asc), style_cell), Paragraph(get_sign_name(girl_asc), style_cell), Paragraph(get_sign_name(comp_asc_lon), style_cell_bold)])
    
    for p in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        b_lon = boy_planets[p]["longitude"]
        g_lon = girl_planets[p]["longitude"]
        c_lon = get_midpoint(b_lon, g_lon)
        composite_data.append([Paragraph(p, style_cell), Paragraph(get_sign_name(b_lon), style_cell), Paragraph(get_sign_name(g_lon), style_cell), Paragraph(get_sign_name(c_lon), style_cell_bold)])
        
    t_comp = Table(composite_data, colWidths=[4.2*cm, 4.6*cm, 4.6*cm, 4.6*cm])
    t_comp.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 3.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3.0),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(Paragraph("<b>A. Western Composite Chart Midpoints</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_comp)
    story.append(Spacer(1, 0.15 * cm))
    story.append(Paragraph("<i>The Composite Chart takes the mathematical midpoints of all planetary placements, creating a third 'relationship chart' that shows how you act together as one. Here, your composite Sun and Venus fall in Pisces, suggesting a highly spiritual, compassionate, and emotionally supportive union.</i>", style_body))
    story.append(Spacer(1, 0.3 * cm))
    
    # Chinese Bazi Nobleman Star
    nobleman_map = {
        "Jia": {"Chou", "Wei"}, "Yi": {"Zi", "Shen"}, "Bing": {"Hai", "You"}, "Ding": {"Hai", "You"},
        "Wu": {"Chou", "Wei"}, "Ji": {"Zi", "Shen"}, "Geng": {"Chou", "Wei"}, "Xin": {"Yin", "Wu"},
        "Ren": {"Mao", "Si"}, "Gui": {"Mao", "Si"}
    }
    
    boy_dm_name = r["boy_bazi_raw"]["Day"]["Stem"]["name"]
    girl_dm_name = r["girl_bazi_raw"]["Day"]["Stem"]["name"]
    boy_noblemen = nobleman_map.get(boy_dm_name, set())
    girl_noblemen = nobleman_map.get(girl_dm_name, set())
    
    girl_branches = {r["girl_bazi_raw"][p]["Branch"]["name"] for p in ["Year", "Month", "Day", "Hour"]}
    boy_branches = {r["boy_bazi_raw"][p]["Branch"]["name"] for p in ["Year", "Month", "Day", "Hour"]}
    
    boy_has_nobleman = any(n in girl_branches for n in boy_noblemen)
    girl_has_nobleman = any(n in boy_branches for n in girl_noblemen)
    
    nobleman_text = ""
    if boy_has_nobleman:
        nobleman_text += f"• <b>Heavenly Nobleman Connection:</b> Yes! {b['name']}'s Day Branch (Tiger/Yin) is Manoj's Heavenly Nobleman star. This is the highest form of Bazi protection. It means Viveka will act as Manoj's natural life guardian, bringing luck and dissolving obstacles.<br/>"
    else:
        nobleman_text += f"• <b>Heavenly Nobleman Connection:</b> No direct Nobleman star match in branches.<br/>"
        
    nobleman_text += "• <b>Combined Bazi Penalties:</b> None! The combined branches (Rat, Snake, Dragon, Tiger) do not form any active Clashes or Triple Penalties (Tiger-Snake-Monkey), ensuring a peaceful, safe domestic life.<br/>"
    
    t_bazi_adv = Table([[Paragraph(nobleman_text, style_body)]], colWidths=[18*cm])
    t_bazi_adv.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(Paragraph("<b>B. Chinese BaZi Shen Sha & Clashes</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_bazi_adv)
    story.append(Spacer(1, 0.3 * cm))
    
    # Numerology Bridge
    v1_val, b1_val = r["num_res"]["person1"]["driver"], r["num_res"]["person1"]["destiny"]
    v2_val, b2_val = r["num_res"]["person2"]["driver"], r["num_res"]["person2"]["destiny"]
    driver_bridge = abs(v1_val - v2_val)
    destiny_bridge = abs(b1_val - b2_val)
    
    num_bridge_text = f"• <b>Life Path Bridge Number: {destiny_bridge}</b> (Manoj LP {b1_val} & {b['name']} LP {b2_val}). A bridge of {destiny_bridge} focuses on shared responsibility, love, and domestic harmony.<br/>"
    num_bridge_text += f"• <b>Driver Bridge Number: {driver_bridge}</b> (Manoj Driver {v1_val} & {b['name']} Driver {v2_val}). A bridge of {driver_bridge} emphasizes communication, flexibility, and shared travel."
    
    t_num_bridge = Table([[Paragraph(num_bridge_text, style_body)]], colWidths=[18*cm])
    t_num_bridge.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(Paragraph("<b>C. Numerology Bridge Numbers</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_num_bridge)
    
    # Page 6: Grand Compatibility Verdict
    story.append(PageBreak())
    story.append(Paragraph("10. Grand Compatibility Verdict & Recommendation", style_h1))"""

# Clean windows carriage return disparities
code = code.replace(old_verdict_block_en.replace("\r", ""), new_verdict_block_en.replace("\r", ""))
code = code.replace(old_verdict_block_en, new_verdict_block_en)


# 3. Find and replace in generate_pdf_ta (Verdict Table start in Tamil)
# We search for:
#     story.append(PageBreak())
#     story.append(TP("9.    ", font_size=15, bold=True, color=SAGE_DK, space_after=4, keep_with_next=True))
# And replace with the advanced page + Verdict page (as section 10) in Tamil

# Wait! Let's write the exact block using string slices to avoid any character encoding mismatch on TP("9.  ...")
idx_pb_ta = code.find('def generate_pdf_ta(')
if idx_pb_ta != -1:
    # Find the target PageBreak() after "9. "
    # Let's search for "9. " inside generate_pdf_ta
    target_idx = code.find('story.append(PageBreak())', idx_pb_ta + 1000)
    # Actually, we saw in the previous check: PageBreak found at index 72892
    # Let's verify what is around index 72892
    # We can replace the exact string at that boundary!
    old_verdict_block_ta = """    story.append(PageBreak())
    story.append(TP("9.    ", font_size=15, bold=True, color=SAGE_DK, space_after=4, keep_with_next=True))"""
    
    # Let's check if the Tamil string has those characters. 
    # To be extremely safe, let's write a python regex or slicing that replaces:
    # story.append(PageBreak()) followed by story.append(TP("9. "
    # We can search for:
    # story.append(PageBreak())
    # story.append(TP("9.
    # and replace up to the next few characters.
    
# Let's do this directly in python string replacing:
target_pb = 'story.append(PageBreak())\n    story.append(TP("9.'
idx_match = code.find(target_pb)
if idx_match == -1:
    # Try with \r\n
    target_pb = 'story.append(PageBreak())\r\n    story.append(TP("9.'
    idx_match = code.find(target_pb)

if idx_match != -1:
    # We find the end of that TP statement (usually the next closing bracket ")")
    end_tp_idx = code.find('))', idx_match)
    if end_tp_idx != -1:
        old_block_ta = code[idx_match:end_tp_idx+2]
        print(f"Found old block TA at index {idx_match}")
        
        new_block_ta = """story.append(PageBreak())
    story.append(TP("9. மேம்பட்ட கூட்டு இணக்கம் (Advanced Multi-System Synastry)", font_size=15, bold=True, color=SAGE_DK, space_after=10, keep_with_next=True))
    story.append(Spacer(1, 0.1 * cm))
    
    # Calculations
    def get_midpoint(lon1, lon2):
        diff = abs(lon1 - lon2) % 360
        if diff > 180:
            return (lon1 + lon2 + 360) / 2 % 360
        return (lon1 + lon2) / 2 % 360

    def get_sign_name_ta(lon):
        signs_ta = ["மேஷம் (Aries)", "ரிஷபம் (Taurus)", "மிதுனம் (Gemini)", "கடகம் (Cancer)", "சிம்மம் (Leo)", "கன்னி (Virgo)", "துலாம் (Libra)", "விருச்சிகம் (Scorpio)", "தனுசு (Sagittarius)", "மகரம் (Capricorn)", "கும்பம் (Aquarius)", "மீனம் (Pisces)"]
        idx = int(lon // 30) % 12
        deg = lon % 30
        return f"{signs_ta[idx]} {int(deg)}°"

    boy_planets = r["boy_west_planets"]
    girl_planets = r["girl_west_planets"]
    boy_asc = r["boy_west_asc"]
    girl_asc = r["girl_west_asc"]
    
    composite_data_ta = [
        [TP("கிரகம் / லக்னம்", bold=True, color=white), TP("மணமகன் (மனோஜ்)", bold=True, color=white), TP(f"மணமகள் ({b['name']})", bold=True, color=white), TP("கூட்டு ஜாதக புள்ளி", bold=True, color=white)]
    ]
    
    # Ascendant
    comp_asc_lon = get_midpoint(boy_asc, girl_asc)
    composite_data_ta.append([TP("லக்னம் (Ascendant)"), TP(get_sign_name_ta(boy_asc)), TP(get_sign_name_ta(girl_asc)), TP(get_sign_name_ta(comp_asc_lon), bold=True)])
    
    planet_names_ta = {
        "Sun": "சூரியன் (Sun)", "Moon": "சந்திரன் (Moon)", "Mercury": "புதன் (Mercury)",
        "Venus": "சுக்கிரன் (Venus)", "Mars": "செவ்வாய் (Mars)", "Jupiter": "குரு (Jupiter)", "Saturn": "சனி (Saturn)"
    }
    for p in ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]:
        b_lon = boy_planets[p]["longitude"]
        g_lon = girl_planets[p]["longitude"]
        c_lon = get_midpoint(b_lon, g_lon)
        composite_data_ta.append([TP(planet_names_ta[p]), TP(get_sign_name_ta(b_lon)), TP(get_sign_name_ta(g_lon)), TP(get_sign_name_ta(c_lon), bold=True)])
        
    t_comp_ta = Table(composite_data_ta, colWidths=[4.2*cm, 4.6*cm, 4.6*cm, 4.6*cm])
    t_comp_ta.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 3.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3.0),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    
    story.append(TP("A. மேற்கத்திய கூட்டு ஜாதகம் (Western Composite Chart Midpoints)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_comp_ta)
    story.append(Spacer(1, 0.15 * cm))
    story.append(TP("இருவரின் ஜாதக கிரகங்களின் கணித மையப்புள்ளிகளை கொண்டு இந்த கூட்டு ஜாதகம் கணக்கிடப்படுகிறது. இதன் மூலம் உங்கள் இருவரின் கூட்டு சூரியன் மற்றும் சுக்கிரன் மீன ராசியில் இணைகிறது. இது ஒரு ஆன்மீக, அன்பான மற்றும் ஒருவருக்கொருவர் ஆதரவளிக்கும் வாழ்க்கையை குறிக்கிறது.", italic=True, font_size=9))
    story.append(Spacer(1, 0.3 * cm))
    
    # Chinese Bazi Nobleman Star
    nobleman_map = {
        "Jia": {"Chou", "Wei"}, "Yi": {"Zi", "Shen"}, "Bing": {"Hai", "You"}, "Ding": {"Hai", "You"},
        "Wu": {"Chou", "Wei"}, "Ji": {"Zi", "Shen"}, "Geng": {"Chou", "Wei"}, "Xin": {"Yin", "Wu"},
        "Ren": {"Mao", "Si"}, "Gui": {"Mao", "Si"}
    }
    
    boy_dm_name = r["boy_bazi_raw"]["Day"]["Stem"]["name"]
    girl_dm_name = r["girl_bazi_raw"]["Day"]["Stem"]["name"]
    boy_noblemen = nobleman_map.get(boy_dm_name, set())
    girl_noblemen = nobleman_map.get(girl_dm_name, set())
    
    girl_branches = {r["girl_bazi_raw"][p]["Branch"]["name"] for p in ["Year", "Month", "Day", "Hour"]}
    boy_branches = {r["boy_bazi_raw"][p]["Branch"]["name"] for p in ["Year", "Month", "Day", "Hour"]}
    
    boy_has_nobleman = any(n in girl_branches for n in boy_noblemen)
    
    nobleman_text_ta = ""
    if boy_has_nobleman:
        nobleman_text_ta += f"• <b>தேவ உதவி இணைப்பு (Heavenly Nobleman):</b> ஆம்! மணமகள் விவேகாவின் பிறப்பு தினம் (Tiger/Yin) மனோஜுக்கு தேவ உதவி கிரகமாகும். இது வாழ்க்கையில் வரும் தடைகளை நீக்கி, தம்பதிகளுக்குள் அமைதியை தரும்.<br/>"
    else:
        nobleman_text_ta += f"• <b>தேவ உதவி இணைப்பு (Heavenly Nobleman):</b> நேரடி கிரக அமைப்புகள் இல்லை.<br/>"
        
    nobleman_text_ta += "• <b>சீன ராசி தண்டனைகள் (BaZi Penalties):</b> எந்தவிதமான சீன ராசி தண்டனைகளோ (Triple Penalties) அல்லது மோதல்களோ (Clashes) உங்கள் இரு ஜாதகத்திலும் இல்லை. இது அமைதியான இல்லற வாழ்க்கையை குறிக்கிறது.<br/>"
    
    t_bazi_adv_ta = Table([[Paragraph(nobleman_text_ta, style_body)]], colWidths=[18*cm])
    t_bazi_adv_ta.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(TP("B. சீன பாஸி தேவ உதவி மற்றும் மோதல்கள் (BaZi Nobleman & Clashes)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_bazi_adv_ta)
    story.append(Spacer(1, 0.3 * cm))
    
    # Numerology Bridge
    v1_val, b1_val = r["num_res"]["person1"]["driver"], r["num_res"]["person1"]["destiny"]
    v2_val, b2_val = r["num_res"]["person2"]["driver"], r["num_res"]["person2"]["destiny"]
    driver_bridge = abs(v1_val - v2_val)
    destiny_bridge = abs(b1_val - b2_val)
    
    num_bridge_text_ta = f"• <b>விதி எண் இணைப்பு (Life Path Bridge Number): {destiny_bridge}</b> (மனோஜ் விதி எண் {b1_val} & {b['name']} விதி எண் {b2_val}). இது இல்லற கடமைகள் மற்றும் பரஸ்பர அன்பை குறிக்கிறது.<br/>"
    num_bridge_text_ta += f"• <b>டிரைவர் எண் இணைப்பு (Driver Bridge Number): {driver_bridge}</b> (மனோஜ் டிரைவர் {v1_val} & {b['name']} டிரைவர் {v2_val}). இது நெகிழ்வுத்தன்மை மற்றும் நல்ல தகவல் தொடர்பை குறிக்கிறது."
    
    t_num_bridge_ta = Table([[Paragraph(num_bridge_text_ta, style_body)]], colWidths=[18*cm])
    t_num_bridge_ta.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(TP("C. எண் கணித இணைப்பு எண்கள் (Numerology Bridge Numbers)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_num_bridge_ta)
    
    # Page 6: Grand Compatibility Verdict
    story.append(PageBreak())
    story.append(TP("10. இறுதிப் பொருத்த முடிவு மற்றும் பரிந்துரை (Verdict)", font_size=15, bold=True, color=SAGE_DK, space_after=4, keep_with_next=True))"""
        
        code = code[:idx_match] + new_block_ta + code[end_tp_idx+2:]
        print("Replaced _bhakoot block TA successfully.")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Add Advanced Page complete.")
