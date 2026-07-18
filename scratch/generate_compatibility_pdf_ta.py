import os
import sys
from pathlib import Path

# Add runtime directory to path to import tamil_renderer
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "runtime"))

from tamil_renderer import TamilParagraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak, HRFlowable
from reportlab.lib.styles import ParagraphStyle

# Define Colors
INDIGO = HexColor("#1a1d3a")
GOLD = HexColor("#b88a37")
GOLD_LT = HexColor("#fef6e4")
CREAM = HexColor("#faf6e8")
CREAM_2 = HexColor("#fff8e1")
GREY_DK = HexColor("#2a2a2a")
GREY_MD = HexColor("#6b6b6b")
GREY_LT = HexColor("#f3f0e8")
GREEN = HexColor("#16a34a")
RED = HexColor("#c0392b")
PINK = HexColor("#cc0080")
CYAN = HexColor("#00a2cc")

# Define Styles
def TP(text, font_size=10, bold=False, color=None, align="left", leading=1.4, space_after=2):
    return TamilParagraph(
        text,
        font_size=font_size,
        bold=bold,
        color=color or GREY_DK,
        align=align,
        leading=leading,
        space_after=space_after
    )

def draw_header_footer(canvas, doc):
    canvas.saveState()
    # Header Line
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1)
    canvas.line(doc.leftMargin, A4[1] - 40, A4[0] - doc.rightMargin, A4[1] - 40)
    
    # Header Text
    canvas.setFont("Tamil-Bold", 8)
    canvas.setFillColor(INDIGO)
    canvas.drawString(doc.leftMargin, A4[1] - 32, "அஷ்டகூடப் பொருத்தம் (36 புள்ளிகள்) — திருமணப் பொருத்த அறிக்கை")
    canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 32, "மனோஜ் குமார் & ந.கயல்விழி")
    
    # Footer Line
    canvas.line(doc.leftMargin, 45, A4[0] - doc.rightMargin, 45)
    
    # Footer Text
    canvas.setFont("Tamil", 8)
    canvas.setFillColor(GREY_MD)
    canvas.drawString(doc.leftMargin, 32, "© 2026 AstroMystic. திருக்கணித பஞ்சாங்க முறைப்படி கணிக்கப்பட்டது.")
    canvas.drawRightString(A4[0] - doc.rightMargin, 32, f"பக்கம் {doc.page}")
    canvas.restoreState()

def build_pdf(filename="reports/Manoj_Kayalvizhi_Compatibility_Report_Tamil_v2.pdf"):
    # Ensure directories exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )
    
    story = []
    
    # ── Page 1: Title ──
    story.append(TP("அஷ்டகூட ஜாதகப் பொருத்தம்", font_size=24, bold=True, color=INDIGO, align="center", space_after=10))
    story.append(TP("நமது என்ஜின் கணிப்பின்படி 36 புள்ளிகள் அஷ்டகூடப் பொருத்த அறிக்கை", font_size=12, color=GOLD, align="center", space_after=15))
    story.append(HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceBefore=4, spaceAfter=15))
    
    # Birth Details Section
    story.append(TP("1. ஜனன விபரங்கள் (Birth Parameters)", font_size=14, bold=True, color=INDIGO, space_after=10))
    
    # Girl Table Data (Kayalvizhi)
    girl_rows = [
        ("பெயர்", "N. Kayalvizhi (ந.கயல்விழி)"),
        ("பிறந்த தேதி", "26-06-1997"),
        ("பிறந்த நேரம்", "04:07 AM"),
        ("பிறந்த இடம்", "Oddanchatram (ஒட்டன்சத்திரம்)"),
        ("ராசி", "கும்பம் (Aquarius)"),
        ("நட்சத்திரம்", "சதயம் (Shatabhisha)"),
        ("நட்சத்திர பாதம்", "4"),
        ("லக்னம்", "ரிஷபம் (Taurus)"),
        ("நடப்பு திசை", "சனி (Saturn)"),
        ("நடப்பு புத்தி", "செவ்வாய் (Mars)"),
        ("திசை முடியும் தேதி", "27-10-2032"),
        ("பட்சி", "மயில் (Peacock)"),
    ]
    
    # Boy Table Data (Manoj)
    boy_rows = [
        ("பெயர்", "Manoj Kumar (மனோஜ் குமார்)"),
        ("பிறந்த தேதி", "25-05-1996"),
        ("பிறந்த நேரம்", "08:25 PM"),
        ("பிறந்த இடம்", "Coimbatore (கோயம்புத்தூர்)"),
        ("ராசி", "சிம்மம் (Leo)"),
        ("நட்சத்திரம்", "மகம் (Magha)"),
        ("நட்சத்திர பாதம்", "4"),
        ("லக்னம்", "தனுசு (Sagittarius)"),
        ("நடப்பு திசை", "சந்திரன் (Moon)"),
        ("நடப்பு புத்தி", "குரு (Jupiter)"),
        ("திசை முடியும் தேதி", "12-07-2033"),
        ("பட்சி", "ஆண் கழுகு (Aan Kazhugu)"),
    ]
    
    # Formatting tables
    t_girl_data = [[TP("பெண் ஜனன விபரம்", font_size=11, bold=True, color=white), ""]]
    for k, v in girl_rows:
        t_girl_data.append([TP(k, font_size=9, bold=True, color=INDIGO), TP(v, font_size=9)])
        
    t_boy_data = [[TP("ஆண் ஜனன விபரம்", font_size=11, bold=True, color=white), ""]]
    for k, v in boy_rows:
        t_boy_data.append([TP(k, font_size=9, bold=True, color=INDIGO), TP(v, font_size=9)])
        
    t_girl = Table(t_girl_data, colWidths=[3.2 * cm, 5.0 * cm])
    t_girl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,0), PINK),
        ("SPAN", (0,0), (1,0)),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    
    t_boy = Table(t_boy_data, colWidths=[3.2 * cm, 5.0 * cm])
    t_boy.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,0), CYAN),
        ("SPAN", (0,0), (1,0)),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    
    # Put both tables side by side
    side_table = Table([[t_girl, "", t_boy]], colWidths=[8.2 * cm, 1.6 * cm, 8.2 * cm])
    side_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    
    story.append(side_table)
    story.append(PageBreak())
    
    # ── Page 2: Ashta-Kuta 36-Point Table ──
    story.append(TP("2. அஷ்டகூடப் பொருத்தப் புள்ளிகள் (36 புள்ளிகள்)", font_size=14, bold=True, color=INDIGO, space_after=10))
    story.append(TP("அஷ்டகூட பொருத்த முறை என்பது 8 முக்கிய அம்சங்களை ஆராய்ந்து 36 புள்ளிகள் அடிப்படையில் கணக்கிடப்படும் வேத ஜோதிட முறையாகும். மனோஜ் மற்றும் கயல்விழி ஜாதக இணக்கம் 36-க்கு 24 புள்ளிகள் பெற்று மிகச் சிறந்த பொருத்தமாக அமைந்துள்ளது.", font_size=10, space_after=12))
    
    kutas_list = [
        ("பொருத்தம் (கூடம்)", "விளக்கம் / பலன்", "ஆண் (மகம்)", "பெண் (சதயம்)", "புள்ளிகள்", "அதிகபட்சம்"),
        ("வர்ணம் (Varna)", "மனோநிலை மற்றும் வாழ்வியல் தகுதி", "சத்திரியர்", "சூத்திரர்", "1", "1"),
        ("வசியம் (Vasya)", "பரஸ்பர ஈர்ப்பு மற்றும் அன்பு", "சிம்மம்", "கும்பம்", "0", "2"),
        ("தாரா (Tara)", "விதி மற்றும் நற்பலன்கள் (தாரா பலம்)", "மகம்", "சதயம்", "0", "3"),
        ("யோனி (Yoni)", "தாம்பத்திய உடலியல் இணக்கம்", "எலி", "குதிரை", "2", "4"),
        ("கிரக மைத்திரி (Graha Maitri)", "ராசி அதிபதிகளின் நட்பு பலம்", "சூரியன்", "சனி", "0", "5"),
        ("கணம் (Gana)", "குணாதிசயம் மற்றும் மன ஒற்றுமை", "ராட்சச", "ராட்சச", "6", "6"),
        ("பகூட் (Bhakoot)", "ராசிகளுக்கு இடையிலான விலகல் நிலை", "சிம்மம்", "கும்பம்", "7", "7"),
        ("நாடி (Nadi)", "உடல் தாதுக்கள் மற்றும் ஆரோக்கியம்", "அந்த்ய", "ஆதி", "8", "8"),
        ("மொத்தம் (Total)", "ஒட்டுமொத்த அஷ்டகூட பொருத்த மதிப்பெண்", "", "", "24", "36"),
    ]
    
    t_match_data = []
    for i, row in enumerate(kutas_list):
        if i == 0:
            t_match_data.append([TP(cell, font_size=9, bold=True, color=white) for cell in row])
        elif i == len(kutas_list) - 1:
            t_match_data.append([
                TP(row[0], font_size=9, bold=True, color=INDIGO),
                TP(row[1], font_size=8.5, color=GREY_MD),
                TP(row[2], font_size=9),
                TP(row[3], font_size=9),
                TP(row[4], font_size=9, bold=True, color=GREEN),
                TP(row[5], font_size=9, bold=True, color=INDIGO)
            ])
        else:
            name, desc, boy, girl, score, max_val = row
            score_cell = TP(score, font_size=9, bold=True, color=GREEN) if score != "0" else TP(score, font_size=9, bold=True, color=RED)
            t_match_data.append([
                TP(name, font_size=9, bold=True, color=INDIGO),
                TP(desc, font_size=8.5, color=GREY_MD),
                TP(boy, font_size=9),
                TP(girl, font_size=9),
                score_cell,
                TP(max_val, font_size=9)
            ])
            
    t_match = Table(t_match_data, colWidths=[4.2 * cm, 5.5 * cm, 2.5 * cm, 2.5 * cm, 1.8 * cm, 1.5 * cm])
    t_match.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,0), INDIGO),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [white, GREY_LT]),
        ("BACKGROUND", (0,-1), (-1,-1), CREAM_2),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    
    story.append(t_match)
    
    # ── Summary box at the bottom ──
    story.append(Spacer(1, 0.4 * cm))
    summary_text = TP(
        "பொருத்தச் சுருக்கம்: அஷ்டகூட பொருத்த கணிப்பின்படி 36-க்கு 24 புள்ளிகள் அமைந்துள்ளன (18-க்கும் அதிகமான புள்ளிகள் பெற்றால் திருமணம் செய்யலாம்). நாடிப் பொருத்தம் (8/8 புள்ளிகள்), கணப் பொருத்தம் (6/6 புள்ளிகள்), பகூட் பொருத்தம் (7/7 புள்ளிகள்) மற்றும் வர்ணப் பொருத்தம் (1/1 புள்ளிகள்) மிகச் சிறப்பாகப் பொருந்தியுள்ளன. இது மிகவும் சிறந்த மற்றும் மகிழ்ச்சியான திருமண வாழ்வை உறுதி செய்கிறது.",
        font_size=10, leading=1.4
    )
    t_sum = Table([[summary_text]], colWidths=[18 * cm])
    t_sum.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CREAM_2),
        ("LINEBEFORE", (0,0), (0,-1), 4, GOLD),
        ("BOX", (0,0), (-1,-1), 0.5, GOLD),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t_sum)
    
    story.append(PageBreak())
    
    # ── Page 3: Dosha Analysis & Timing ──
    story.append(TP("3. செவ்வாய் மற்றும் தசா சந்திப்பு பொருத்தங்கள்", font_size=14, bold=True, color=INDIGO, space_after=10))
    
    # Sevvai Section
    story.append(TP("செவ்வாய் தோஷப் பொருத்தம்:", font_size=10.5, bold=True, color=INDIGO))
    story.append(Spacer(1, 0.1 * cm))
    
    sev_body = TP(
        "தம்பதிகள் இருவரின் ஜாதகத்திலும் செவ்வாய் கிரகம் அமைந்துள்ள வீடுகள் ஆராயப்பட்டன.\n"
        "• பெண் ஜாதகம்: செவ்வாய் 5-ஆம் இடத்தில் (கன்னி ராசியில்) உள்ளது. இது லக்னத்திற்கு 5-ல் உள்ளதால் தோஷமில்லை.\n"
        "• ஆண் ஜாதகம்: செவ்வாய் 5-ஆம் இடத்தில் (மேஷ ராசியில்) உள்ளது. இது லக்னத்திற்கு 5-ல் உள்ளதால் தோஷமில்லை.\n"
        "தம்பதிகள் இருவர் ஜாதகத்திலும் செவ்வாய் தோஷம் இல்லை என்பதால், செவ்வாய் தோஷப் பொருத்தம் சிறப்பாக அமைந்துள்ளது.",
        font_size=9.5, leading=1.4, space_after=10
    )
    t_sev = Table([[sev_body]], colWidths=[18 * cm])
    t_sev.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), white),
        ("BOX", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("LINELEFT", (0,0), (-1,-1), 4, GREEN),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t_sev)
    story.append(Spacer(1, 0.4 * cm))
    
    # Dasha Sandhi Section
    story.append(TP("தசா சந்திப்பு பொருத்தம்:", font_size=10.5, bold=True, color=INDIGO))
    story.append(Spacer(1, 0.1 * cm))
    
    dasha_body = TP(
        "திருமணத்தின் போது இருவருக்கும் ஒரே நேரத்தில் தசா மாற்றம் ஏற்படக்கூடாது (இதனை தசா சந்திப்பு என்பர்).\n"
        "• பெண்: தற்போதைய தசை சனி தசை (செவ்வாய் புத்தி நடக்கிறது, முடிவு 2032).\n"
        "• ஆண்: தற்போதைய தசை சந்திரன் தசை (குரு புத்தி நடக்கிறது, முடிவு 2033).\n"
        "இருவருக்கும் வெவ்வேறு காலகட்டங்களில் தசா மாற்றம் ஏற்படுவதால் தசா சந்திப்பு தோஷம் ஏதும் இல்லை. பொருத்தம் உத்தமம்.",
        font_size=9.5, leading=1.4, space_after=10
    )
    t_dash = Table([[dasha_body]], colWidths=[18 * cm])
    t_dash.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), white),
        ("BOX", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("LINELEFT", (0,0), (-1,-1), 4, GREEN),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t_dash)
    story.append(Spacer(1, 0.4 * cm))
    
    # Rahu Ketu Section
    story.append(TP("ராகு கேது தோஷப் பொருத்தம்:", font_size=10.5, bold=True, color=INDIGO))
    story.append(Spacer(1, 0.1 * cm))
    
    rahu_body = TP(
        "பெண்ணுக்கு ராகு 5-ஆம் வீட்டிலும், கேது 11-ஆம் வீட்டிலும் உள்ளனர்.\n"
        "ஆணுக்கு ராகு 10-ஆம் வீட்டிலும், கேது 4-ஆம் வீட்டிலும் உள்ளனர்.\n"
        "இருவர் ஜாதகத்திலும் தீவிர சர்ப்ப தோஷம் (ராகு-கேது தோஷம்) இல்லை என்பதால், ராகு கேது தோஷப் பொருத்தம் உத்தமமாக உள்ளது.",
        font_size=9.5, leading=1.4, space_after=10
    )
    t_rahu = Table([[rahu_body]], colWidths=[18 * cm])
    t_rahu.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), white),
        ("BOX", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("LINELEFT", (0,0), (-1,-1), 4, GREEN),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t_rahu)
    story.append(Spacer(1, 0.4 * cm))
    
    # ── Final Recommendation ──
    story.append(TP("4. பொருத்தத்தின் விளக்கமும் சிபாரிசும்", font_size=14, bold=True, color=INDIGO, space_after=10))
    
    rec_body = TP(
        "பொருத்தம் சிபாரிசு செய்யப்படுகிறது (RECOMMENDED MATCH)\n\n"
        "• ஜாதக பொருத்தம்: நமது அஷ்டகூட என்ஜின் கணிப்பின்படி 36-க்கு 24 புள்ளிகள் பெற்றுள்ளது (மிக நன்று).\n"
        "• தோஷப் பொருத்தம்: செவ்வாய் தோஷம், தசா சந்திப்பு, மற்றும் ராகு-கேது தோஷங்கள் எதுவும் இல்லை.\n"
        "• பரிகாரம்: எந்தவித தோஷங்களும் இல்லாததால், எளிய குலதெய்வ வழிபாட்டுடன் தாராளமாகத் திருமணப் பேச்சுவார்த்தைகளைத் தொடங்கலாம்.",
        font_size=10, leading=1.4, color=white
    )
    t_rec = Table([[rec_body]], colWidths=[18 * cm])
    t_rec.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GREEN),
        ("BOX", (0,0), (-1,-1), 0.5, HexColor("#0f763e")),
        ("LEFTPADDING", (0,0), (-1,-1), 15),
        ("RIGHTPADDING", (0,0), (-1,-1), 15),
        ("TOPPADDING", (0,0), (-1,-1), 12),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12),
    ]))
    story.append(t_rec)
    
    # Build Document
    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    print(f"Successfully generated 36-point Ashta-Kuta PDF in Tamil at {filename}")

if __name__ == "__main__":
    build_pdf()
