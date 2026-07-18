import re

with open(r'f:\astro\scratch\generate_investor_business.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_section = """
    # ════ PAGE 6: REPORT STRUCTURE ════
    story += sec("05", "The Product — Report Structure")
    story.append(Paragraph(
        "Unlike generic horoscopes, the AstroReport OS generates a comprehensive 50-200 page personalized "
        "Life Biography. The report is structured to answer exactly what the user needs, when they need it.", sB))
    
    story.append(Spacer(1, 4*mm))
    story.append(tbl(
        ["Chapter", "Core Focus", "Details Included"],
        [
            ["1. The Natal Foundation", "Core personality, psychological blueprint, and life purpose.", "Ascendant analysis, dominant elements, core strengths & weaknesses."],
            ["2. Wealth & Career", "Professional trajectory, financial stability, and business acumen.", "D10 (Dasamsa) career mapping, wealth yogas, best industries."],
            ["3. Love & Partnerships", "Marriage timing, spouse characteristics, and relationship dynamics.", "D9 (Navamsa) analysis, Venus/Jupiter placements, 7th house rules."],
            ["4. Health & Vitality", "Physical constitution and potential physiological vulnerabilities.", "6th/8th house analysis, medical astrology indicators."],
            ["5. The Early Years", "Childhood development, education, and family environment.", "D24 (Siddhamsha) education, early Dasha periods."],
            ["6. The Adult Chapters", "Chronological breakdown of major life phases (Age 25-60).", "Saturn Returns, major Mahadasha shifts, transits of Jupiter/Saturn."],
            ["7. Current Year Forecast", "Deep dive into the next 12 months.", "Monthly Bhukti analysis, actionable guidance for the present."],
            ["8. The Question Catalog", "Direct answers to the 141 most common life questions.", "e.g., 'Will I settle abroad?', 'Should I start a business?'"],
        ],
        [38*mm, 60*mm, W - 36*mm - 98*mm]
    ))
    story.append(Spacer(1, 5*mm))
    story.append(banner("A premium, beautifully rendered PDF that users refer back to for decades.", GOLD))
    story.append(PageBreak())

"""

parts = content.split('    # ════ PAGE 6: MARKET SIZING ════')

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
    
    new_content = parts[0] + new_section + '    # ════ PAGE 7: MARKET SIZING ════' + part2
    
    with open(r'f:\astro\scratch\generate_investor_business.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("SUCCESS")
else:
    print("FAILED TO SPLIT")
