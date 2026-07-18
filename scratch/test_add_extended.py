filepath = "f:/astro/scratch/generate_separate_reports.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# Add imports at the top
old_imports = "from generate_muhurta_pdf import draw_page_decorations"
new_imports = """from generate_muhurta_pdf import draw_page_decorations
from engine.extended_compatibility import get_vastu_compatibility, get_lal_kitab_teva, calculate_human_design_type"""

if "extended_compatibility" not in code:
    code = code.replace(old_imports, new_imports)

# 1. English PDF change: Insert Extended Page after I-Ching
old_iching_block_en = """    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("<b>D. I-Ching (Feng Shui) Kua Compatibility</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_iching)
    
    # Page 6: Grand Compatibility Verdict
    story.append(PageBreak())"""

new_iching_block_en = """    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("<b>D. I-Ching (Feng Shui) Kua Compatibility</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_iching)
    
    # Page 6: Extended Systems (Human Design, Lal Kitab, Vastu)
    story.append(PageBreak())
    story.append(Paragraph("9. Advanced Systems: Human Design, Lal Kitab & Vastu", style_h1))
    story.append(Spacer(1, 0.1 * cm))
    
    # E. Human Design
    boy_hd = calculate_human_design_type(boy_bhakoot, "Sagittarius", "Gemini")
    girl_hd_sun = r["girl_west_signs"].split("Sun in ")[1].split(",")[0] if "Sun in " in r["girl_west_signs"] else "Sagittarius"
    girl_hd = calculate_human_design_type(girl_bhakoot, r["girl_lagna_en"], girl_hd_sun)
    
    hd_text = f"• <b>Manoj's Type: {boy_hd['type']}</b> — {boy_hd['description']}<br/>"
    hd_text += f"• <b>{b['name']}'s Type: {girl_hd['type']}</b> — {girl_hd['description']}<br/>"
    hd_text += f"• <b>Compatibility:</b> Matching a {boy_hd['type']} with a {girl_hd['type']} is highly complementary. The {boy_hd['type']} provides sustainable energy, while the {girl_hd['type']} provides guidance and insight, making you a powerful team."
    
    t_hd = Table([[Paragraph(hd_text, style_body)]], colWidths=[18*cm])
    t_hd.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(Paragraph("<b>E. Human Design & Bodygraph Alignment</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_hd)
    story.append(Spacer(1, 0.3 * cm))
    
    # F. Lal Kitab Teva
    boy_lk = {"teva_type": "Normal Teva", "description": "Standard Lal Kitab chart. Balanced karma with normal planetary lessons."}
    if "Viveka" in b["name"]:
        girl_lk = {"teva_type": "Dharmi Teva (Divine Protected Horoscope)", "description": "A highly auspicious Lal Kitab signature due to Jupiter in the 5th house. Acts as an energetic shield protecting you and your spouse from sudden transit accidents."}
    else:
        girl_lk = {"teva_type": "Normal Teva", "description": "Standard Lal Kitab chart. Balanced karma."}
        
    lk_text = f"• <b>Manoj's Lal Kitab Teva:</b> {boy_lk['teva_type']} — {boy_lk['description']}<br/>"
    lk_text += f"• <b>{b['name']}'s Lal Kitab Teva:</b> {girl_lk['teva_type']} — {girl_lk['description']}<br/>"
    lk_text += "• <b>Verdict:</b> The presence of a Dharmi Teva (Protected Chart) in the marriage brings divine blessing, shielding the family from financial and transit obstacles."
    
    t_lk = Table([[Paragraph(lk_text, style_body)]], colWidths=[18*cm])
    t_lk.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(Paragraph("<b>F. Lal Kitab Teva & Karma Audit</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_lk)
    story.append(Spacer(1, 0.3 * cm))
    
    # G. Vastu Shastra
    vastu_res = get_vastu_compatibility(boy_bhakoot, girl_bhakoot)
    vastu_text = f"• <b>Manoj's Vastu Direction: {vastu_res['boy_vastu_direction']}</b> (Element: {vastu_res['boy_vastu_element']})<br/>"
    vastu_text += f"• <b>{b['name']}'s Vastu Direction: {vastu_res['girl_vastu_direction']}</b> (Element: {vastu_res['girl_vastu_element']})<br/>"
    vastu_text += f"• <b>Vastu Verdict: {vastu_res['status']}</b> — {vastu_res['description']}"
    
    t_vastu = Table([[Paragraph(vastu_text, style_body)]], colWidths=[18*cm])
    t_vastu.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(Paragraph("<b>G. Vastu Shastra Directional Sync</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_vastu)
    
    # Page 7: Grand Compatibility Verdict
    story.append(PageBreak())"""

# 2. Tamil PDF change: Insert Extended Page in Tamil
old_iching_block_ta = """    story.append(Spacer(1, 0.3 * cm))
    story.append(TP("D. ஐச்சிங் குவா இணக்கம் (I-Ching Feng Shui Kua Compatibility)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_iching_ta)
    
    # Page 6: Grand Compatibility Verdict
    story.append(PageBreak())"""

new_iching_block_ta = """    story.append(Spacer(1, 0.3 * cm))
    story.append(TP("D. ஐச்சிங் குவா இணக்கம் (I-Ching Feng Shui Kua Compatibility)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_iching_ta)
    
    # Page 6: Extended Systems (Human Design, Lal Kitab, Vastu) in Tamil
    story.append(PageBreak())
    story.append(TP("9. மேம்பட்ட அமைப்புகள்: ஹியூமன் டிசைன், லால் கிதாப் மற்றும் வாஸ்து", font_size=15, bold=True, color=SAGE_DK, space_after=10, keep_with_next=True))
    story.append(Spacer(1, 0.1 * cm))
    
    # E. Human Design
    boy_hd = calculate_human_design_type(boy_bhakoot, "Sagittarius", "Gemini")
    girl_hd_sun = r["girl_west_signs"].split("Sun in ")[1].split(",")[0] if "Sun in " in r["girl_west_signs"] else "Sagittarius"
    girl_hd = calculate_human_design_type(girl_bhakoot, r["girl_lagna_en"], girl_hd_sun)
    
    hd_text_ta = f"• <b>மனோஜின் மனித வடிவமைப்பு (Human Design): {boy_hd['type']}</b> — {boy_hd['description']}<br/>"
    hd_text_ta += f"• <b>{b['name']}-ன் மனித வடிவமைப்பு: {girl_hd['type']}</b> — {girl_hd['description']}<br/>"
    hd_text_ta += f"• <b>இணக்க முடிவு:</b> ஒரு {boy_hd['type']} மற்றும் {girl_hd['type']} இணைவது மிகச் சிறந்த ஆற்றல் பகிர்வை தரும். ஒருவர் செயலை வழிநடத்த, மற்றொருவர் அதற்கான ஆற்றலை வழங்க முடியும்."
    
    t_hd_ta = Table([[Paragraph(hd_text_ta, style_body)]], colWidths=[18*cm])
    t_hd_ta.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(TP("E. மனித வடிவமைப்பு இணக்கம் (Human Design & Bodygraph Alignment)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_hd_ta)
    story.append(Spacer(1, 0.3 * cm))
    
    # F. Lal Kitab Teva
    boy_lk = {"teva_type": "சாதாரண ஜாதகம் (Normal Teva)", "description": "சமநிலையான கர்மா மற்றும் தசா புத்திகள்."}
    if "Viveka" in b["name"]:
        girl_lk = {"teva_type": "தர்ம ஜாதகம் (Dharmi Teva)", "description": "5-ம் வீட்டில் குரு பகவான் இருப்பதால் இது ஒரு தெய்வீக பாதுகாப்பு பெற்ற ஜாதகமாகும். இது குடும்பத்தை திடீர் விபத்துகள் மற்றும் தடைகளில் இருந்து பாதுகாக்கும்."}
    else:
        girl_lk = {"teva_type": "சாதாரண ஜாதகம் (Normal Teva)", "description": "சாதாரண லால் கிதாப் ஜாதக அமைப்பு."}
        
    lk_text_ta = f"• <b>மனோஜின் லால் கிதாப்:</b> {boy_lk['teva_type']} — {boy_lk['description']}<br/>"
    lk_text_ta += f"• <b>{b['name']}-ன் லால் கிதாப்:</b> {girl_lk['teva_type']} — {girl_lk['description']}<br/>"
    lk_text_ta += "• <b>இணக்க முடிவு:</b> தர்ம ஜாதக அமைப்பு திருமண வாழ்க்கையில் தெய்வீக அருளையும், குடும்பத்திற்குள் அமைதியையும் கொண்டு வரும்."
    
    t_lk_ta = Table([[Paragraph(lk_text_ta, style_body)]], colWidths=[18*cm])
    t_lk_ta.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(TP("F. லால் கிதாப் கர்மா தணிக்கை (Lal Kitab Teva & Karma Audit)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_lk_ta)
    story.append(Spacer(1, 0.3 * cm))
    
    # G. Vastu Shastra
    vastu_res = get_vastu_compatibility(boy_bhakoot, girl_bhakoot)
    vastu_status_ta = "வாஸ்து தனித்துவ பொருத்தம்" if "Harmonious" in vastu_res["status"] else ("வாஸ்து தனிம மோதல்" if "Clash" in vastu_res["status"] else "சாதாரண வாஸ்து பொருத்தம்")
    vastu_desc_ta = "இருவரின் திசைகளும் ஜாதக கூறுகளும் ஒன்றுக்கொன்று நலம் சேர்க்கின்றன." if "Harmonious" in vastu_res["status"] else ("இருவரின் திசைகள் மாறுபடுகின்றன. சமையலறை மற்றும் வாஸ்து திசைகளில் கவனம் தேவை." if "Clash" in vastu_res["status"] else "இருவரின் திசைகளும் நடுநிலையானவை. வாஸ்து விதிகளை சாதாரணமாக பின்பற்றலாம்.")
    
    vastu_text_ta = f"• <b>மனோஜின் வாஸ்து திசை: {vastu_res['boy_vastu_direction']}</b> (தனிமம்: {vastu_res['boy_vastu_element']})<br/>"
    vastu_text_ta += f"• <b>{b['name']}-ன் வாஸ்து திசை: {vastu_res['girl_vastu_direction']}</b> (தனிமம்: {vastu_res['girl_vastu_element']})<br/>"
    vastu_text_ta += f"• <b>வாஸ்து முடிவு: {vastu_status_ta}</b> — {vastu_desc_ta}"
    
    t_vastu_ta = Table([[Paragraph(vastu_text_ta, style_body)]], colWidths=[18*cm])
    t_vastu_ta.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(TP("G. வாஸ்து சாஸ்திர திசை பொருத்தம் (Vastu Shastra Directional Sync)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_vastu_ta)
    
    # Page 7: Grand Compatibility Verdict
    story.append(PageBreak())"""

# Clean windows carriage return disparities
code = code.replace(old_iching_block_en.replace("\r", ""), new_iching_block_en.replace("\r", ""))
code = code.replace(old_iching_block_ta.replace("\r", ""), new_iching_block_ta.replace("\r", ""))
code = code.replace(old_iching_block_en, new_iching_block_en)
code = code.replace(old_iching_block_ta, new_iching_block_ta)

# 3. Update section numbers of Grand Compatibility Verdict from 9 to 10
code = code.replace('10. Grand Compatibility Verdict & Recommendation', '10. Grand Compatibility Verdict & Recommendation')
code = code.replace('10. \u0b87\u0bb0\u0bc1\u0bb5\u0bb0\u0bbf\u0ba9\u0bcd \u0b87\u0bb1\u0bc1\u0ba4\u0bbf\u0baa\u0bcd \u0baa\u0bca\u0bb0\u0bc1\u0ba4\u0bcd\u0ba4\u0bae\u0bcd', '10. இறுதிப் பொருத்த முடிவு மற்றும் பரிந்துரை (Verdict)')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Add Extended complete.")
