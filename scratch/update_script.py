import re

with open(r'f:\astro\scratch\generate_investor_business.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_section = """
    # ════ PAGE 5: ENGINE STRUCTURE ════
    story += sec("04", "Engine Architecture — How It Works")
    story.append(Paragraph(
        "AstroReport OS is powered by a 7-layer deterministic pipeline. Data flows from raw birth coordinates "
        "through our Knowledge Graph, resolving into a personalized narrative.", sB))
    
    story.append(Spacer(1, 4*mm))
    story.append(tbl(
        ["Layer", "Process", "Technology / Engine"],
        [
            ["1. Input & Calculation", "Calculates 16 divisional charts (D1-D60), planetary dignities, and precise house cusps.", "Swiss Ephemeris / C-Core"],
            ["2. Knowledge Retrieval", "Queries the Neo4j Graph to match the birth chart against 20,849 classical rules.", "Neo4j Knowledge Graph"],
            ["3. Multi-System Logic", "Evaluates evidence across 8 traditions (Vedic, KP, Western, Chinese, Numerology).", "Declarative Category Engine"],
            ["4. Evidence Weighting", "Resolves contradictions using a confidence scoring matrix (e.g., Cancellation Yogas).", "Algorithmic Optimizer"],
            ["5. Timeline Generation", "Maps active rules to the Mahadasha/Bhukti timeline to create chronological life chapters.", "Timeline Intelligence Engine"],
            ["6. Narrative Generation", "Passes the structured astrological facts to an LLM to write a human-readable biography.", "Gemini / GPT-4 API"],
            ["7. Final Output", "Compiles chapters into a beautifully formatted 50+ page PDF or web dashboard.", "ReportLab Render Engine"],
        ],
        [38*mm, 85*mm, W - 36*mm - 123*mm]
    ))
    story.append(Spacer(1, 6*mm))
    
    story.append(Paragraph("<b>The Engine Pipeline Flow:</b>", sH2))
    flow = [
        ["Birth Data (Date, Time, Location)"],
        ["↓"],
        ["Chart Calculation (Swiss Ephemeris)"],
        ["↓"],
        ["Knowledge Graph Query (20,849 Rules)"],
        ["↓"],
        ["Logic & Conflict Resolution (Multi-System Engine)"],
        ["↓"],
        ["Timeline Mapping (Dasha/Bhukti Chapters)"],
        ["↓"],
        ["Narrative Translation (LLM / Gemini)"],
        ["↓"],
        ["Personalized Life Biography Report (PDF / Web)"]
    ]
    t_flow = Table(flow, colWidths=[W-36*mm])
    t_flow.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), NAVY),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_flow)

    story.append(Spacer(1, 5*mm))
    story.append(banner("This deterministic pipeline ensures the AI never hallucinates astrological facts.", TEAL))
    story.append(PageBreak())

"""

parts = content.split('    # ════ PAGE 5: MARKET SIZING ════')

if len(parts) == 2:
    part2 = parts[1]
    
    def replace_sec(match):
        num = int(match.group(1))
        new_num = num + 1
        return f'sec("{new_num:02d}"'

    part2 = re.sub(r'sec\("(\d{2})"', replace_sec, part2)
    
    def replace_page(match):
        num = int(match.group(1))
        new_num = num + 1
        return f'# ════ PAGE {new_num}:'
        
    part2 = re.sub(r'# ════ PAGE (\d+):', replace_page, part2)
    
    new_content = parts[0] + new_section + '    # ════ PAGE 6: MARKET SIZING ════' + part2
    
    with open(r'f:\astro\scratch\generate_investor_business.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS")
else:
    print("FAILED TO SPLIT")
