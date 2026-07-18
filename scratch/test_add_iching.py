filepath = "f:/astro/scratch/generate_separate_reports.py"
with open(filepath, "r", encoding="utf-8") as f:
    code = f.read()

# 1. English PDF change: Insert I-Ching after Numerology Bridge
old_num_block_en = """    story.append(Paragraph("<b>C. Numerology Bridge Numbers</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_num_bridge)
    
    # Page 6: Grand Compatibility Verdict
    story.append(PageBreak())"""

new_num_block_en = """    story.append(Paragraph("<b>C. Numerology Bridge Numbers</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_num_bridge)
    
    # D. I-Ching (Feng Shui) Kua Compatibility
    iching_text = "• <b>Manoj's Life Gua: 4 (Xun - Wind/Small Wood)</b> [East Group]<br/>"
    iching_text += f"• <b>{b['name']}'s Life Gua: 6 (Qian - Heaven/Big Metal)</b> [West Group]<br/>"
    iching_text += "• <b>Compatibility Verdict:</b> Mismatch of Groups (East vs West) & destructive element cycle (Metal controls Wood). This suggests different spatial energy needs (opposite sleeping/working directions) and potential for the Kua 6 partner to be overly controlling. Balancing the home environment with Water elements can bridge this gap."
    
    t_iching = Table([[Paragraph(iching_text, style_body)]], colWidths=[18*cm])
    t_iching.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("<b>D. I-Ching (Feng Shui) Kua Compatibility</b>", style_cell_bold))
    story.append(Spacer(1, 0.15 * cm))
    story.append(t_iching)
    
    # Page 6: Grand Compatibility Verdict
    story.append(PageBreak())"""

# 2. Tamil PDF change: Insert I-Ching after Numerology Bridge in Tamil
old_num_block_ta = """    story.append(TP("C. எண் கணித இணைப்பு எண்கள் (Numerology Bridge Numbers)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_num_bridge_ta)
    
    # Page 6: Grand Compatibility Verdict
    story.append(PageBreak())"""

new_num_block_ta = """    story.append(TP("C. எண் கணித இணைப்பு எண்கள் (Numerology Bridge Numbers)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_num_bridge_ta)
    
    # D. I-Ching (Feng Shui) Kua Compatibility (Tamil)
    iching_text_ta = f"• <b>மனோஜின் குவா எண் (Kua): 4 (காற்று/மரம் - Xun)</b> [கிழக்கு குழு]<br/>"
    iching_text_ta += f"• <b>{b['name']} குவா எண் (Kua): 6 (வானம்/உலோகம் - Qian)</b> [மேற்கு குழு]<br/>"
    iching_text_ta += "• <b>இணக்க முடிவு:</b> திசைகள் மாறுபடுதல் (கிழக்கு vs மேற்கு) மற்றும் உலோக-மர கட்டுப்பாடு. இது இருவரின் தூங்கும்/வேலை செய்யும் திசைகளில் மாறுபாட்டையும், குவா 6 நபர் சற்று ஆதிக்கம் செலுத்தக்கூடிய தன்மையையும் குறிக்கிறது. வீட்டில் தண்ணீர் கூறுகளை (Water elements) பயன்படுத்துவது இந்த வேறுபாட்டை சமநிலைப்படுத்தும்."
    
    t_iching_ta = Table([[Paragraph(iching_text_ta, style_body)]], colWidths=[18*cm])
    t_iching_ta.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(TP("D. ஐச்சிங் குவா இணக்கம் (I-Ching Feng Shui Kua Compatibility)", bold=True, color=SAGE_DK, space_after=6))
    story.append(t_iching_ta)
    
    # Page 6: Grand Compatibility Verdict
    story.append(PageBreak())"""

# Clean windows carriage return disparities
code = code.replace(old_num_block_en.replace("\r", ""), new_num_block_en.replace("\r", ""))
code = code.replace(old_num_block_ta.replace("\r", ""), new_num_block_ta.replace("\r", ""))
code = code.replace(old_num_block_en, new_num_block_en)
code = code.replace(old_num_block_ta, new_num_block_ta)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(code)

print("Add I-Ching complete.")
