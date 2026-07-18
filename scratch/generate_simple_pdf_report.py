import os
import urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from reportlab.lib import colors

out_path = r"F:\astro\reports\S_THANGAVEL_SIMPLE_REPORT.pdf"
font_path = r"F:\astro\scratch\NotoSansTamil-Regular.ttf"

# Download Tamil Font if not exists
if not os.path.exists(font_path):
    url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTamil/NotoSansTamil-Regular.ttf"
    urllib.request.urlretrieve(url, font_path)

# Register Font
pdfmetrics.registerFont(TTFont('Tamil', font_path))

# Page setup - 1.5 cm margins for clean layout
doc = SimpleDocTemplate(
    out_path, 
    pagesize=A4, 
    rightMargin=1.5*cm, 
    leftMargin=1.5*cm, 
    topMargin=1.5*cm, 
    bottomMargin=1.5*cm
)

# Custom Styles
title_style = ParagraphStyle(
    'TitleStyle', 
    fontName='Tamil', 
    fontSize=20, 
    spaceAfter=15, 
    leading=24, 
    textColor=colors.HexColor("#1a1d3a"),
    alignment=1
)
subtitle_style = ParagraphStyle(
    'SubTitleStyle', 
    fontName='Tamil', 
    fontSize=11, 
    spaceAfter=20, 
    leading=16, 
    textColor=colors.HexColor("#5a5a5a"),
    alignment=1
)
h2_style = ParagraphStyle(
    'H2', 
    fontName='Tamil', 
    fontSize=13, 
    spaceAfter=8, 
    spaceBefore=14, 
    leading=16, 
    textColor=colors.HexColor("#7d1f3d")
)
body_style = ParagraphStyle(
    'Body', 
    fontName='Tamil', 
    fontSize=10, 
    spaceAfter=8, 
    leading=14, 
    textColor=colors.HexColor("#2a2a2a")
)
bullet_style = ParagraphStyle(
    'Bullet', 
    fontName='Tamil', 
    fontSize=9.5, 
    leftIndent=15, 
    firstLineIndent=-10, 
    spaceAfter=4, 
    leading=13, 
    textColor=colors.HexColor("#2a2a2a")
)

story = []

# Header
story.append(Paragraph("S. Thangavel — Life Story & Timeline (Simplified)", title_style))
story.append(Paragraph("A clear, simple, and easy-to-read personal astrological analysis.", subtitle_style))
story.append(Spacer(1, 0.2*cm))

# 1. Key Details
story.append(Paragraph("📊 Important Astrological Details", h2_style))
details_text = (
    "• <b>Lagna (Ascendant):</b> Gemini (மிதுனம்) — <i>Defines his personality and body.</i><br/>"
    "• <b>Rasi (Moon Sign):</b> Libra (துலாம்) — <i>Defines his mind and emotions.</i><br/>"
    "• <b>Nakshatram (Birth Star):</b> Swathi (சுவாதி - 3rd Padam) — <i>Defines his inner character.</i><br/>"
    "• <b>Star Lord:</b> Rahu (ராகு) — <i>The planet that ruled his early childhood.</i>"
)
story.append(Paragraph(details_text, body_style))
story.append(Spacer(1, 0.3*cm))

# 2. Rasi Chart Table
story.append(Paragraph("🗺️ Birth Chart (ராசி கட்டம்)", h2_style))

chart_data = [
    [
        Paragraph("<b>Meenam (Pisces)</b><br/>Jupiter (Guru)<br/><i>(Own House)</i>", body_style),
        Paragraph("<b>Mesham (Aries)</b>", body_style),
        Paragraph("<b>Rishabam (Taurus)</b>", body_style),
        Paragraph("<b>Mithunam (Gemini)</b><br/><b>Lagna</b><br/>Rahu", body_style)
    ],
    [
        Paragraph("<b>Kumbam (Aquarius)</b>", body_style),
        Paragraph("<b>RASI CHART</b><br/>S. Thangavel", title_style),
        "", # Spanned
        Paragraph("<b>Kadagam (Cancer)</b><br/>Sun (Suriyan)<br/>Mercury (Budhan)<br/>Venus (Sukran)", body_style)
    ],
    [
        Paragraph("<b>Makaram (Capricorn)</b><br/>Saturn (Sani)<br/><i>(Own House)</i>", body_style),
        "", # Spanned
        "", # Spanned
        Paragraph("<b>Simmam (Leo)</b>", body_style)
    ],
    [
        Paragraph("<b>Dhanusu (Sagittarius)</b><br/>Ketu", body_style),
        Paragraph("<b>Viruchigam (Scorpio)</b>", body_style),
        Paragraph("<b>Thulaam (Libra)</b><br/>Moon (Chandran)", body_style),
        Paragraph("<b>Kanni (Virgo)</b><br/>Mars (Sevvai)", body_style)
    ]
]

# Configure table styling
t = Table(chart_data, colWidths=[4.3*cm, 4.3*cm, 4.3*cm, 4.3*cm], rowHeights=[2.2*cm, 1.2*cm, 1.2*cm, 2.2*cm])
t.setStyle(TableStyle([
    ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#c9a032")),
    ('SPAN', (1,1), (2,2)), # Span middle 2x2
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BACKGROUND', (1,1), (2,2), colors.HexColor("#faf6e8")),
]))

story.append(t)
story.append(Spacer(1, 0.4*cm))

# 3. Core Insights
story.append(Paragraph("✨ Core Pillars of His Life", h2_style))
story.append(Paragraph("<b>1. His Personality:</b> Your father has an exceptionally sharp brain. He is excellent at communicating, negotiating, and figuring things out quickly. He is brave, stands his ground, and commands natural respect from others.", body_style))
story.append(Paragraph("<b>2. His Wealth & Property:</b> He has a highly auspicious combination for wealth. The planet of cash (Venus) and property (Mercury) sit together in his house of wealth. This gives him a natural ability to build and accumulate land, buildings, and assets.", body_style))
story.append(Paragraph("<b>3. His Health:</b> Saturn is in its own house in the 8th house, which acts as a powerful shield. This guarantees him a very long, resilient life and protects him from major physical dangers.", body_style))

# 4. Timelines
story.append(Paragraph("📅 Life Chapters & Timeline (Dasha Analysis)", h2_style))

# Chapter 1
story.append(Paragraph("<b>Chapter 1: Childhood & The Rahu Period (1963 to 1968)</b>", body_style))
story.append(Paragraph("• <b>About:</b> Born during the final years of the Rahu cycle. Rahu sat directly in his body's house (1st House).", bullet_style))
story.append(Paragraph("• <b>🟢 The Good (நன்மை):</b> Developed an incredibly sharp, fast-learning mind. He was a highly charming baby who drew sudden luck to his father.", bullet_style))
story.append(Paragraph("• <b>🔴 The Bad (தீமை):</b> Suffered from childhood fears (nightmares) and sudden, unexplained fevers that cured quickly. The family faced financial instability.", bullet_style))

# Chapter 2
story.append(Paragraph("<b>Chapter 2: Building the Brain & The Jupiter Period (1968 to 1984)</b>", body_style))
story.append(Paragraph("• <b>About:</b> A period of education and setting up life's foundation. Jupiter was very strong in his 10th House of career.", bullet_style))
story.append(Paragraph("• <b>🟢 The Good (நன்மை):</b> Excelled in learning, gained deep wisdom, and earned high respect and leadership qualities early in life.", bullet_style))
story.append(Paragraph("• <b>🔴 The Bad (தீமை):</b> Had to take on mature mental responsibilities early and faced high pressure to perform.", bullet_style))

# Chapter 3
story.append(Paragraph("<b>Chapter 3: The Hard Work Era & The Saturn Period (1984 to 2003)</b>", body_style))
story.append(Paragraph("• <b>About:</b> 19 years of intense hard work and heavy family responsibilities. Saturn was in his 8th House.", bullet_style))
story.append(Paragraph("• <b>🟢 The Good (நன்மை):</b> Built unbreakable mental and physical strength. The placement guaranteed long life and protected him from major crises.", bullet_style))
story.append(Paragraph("• <b>🔴 The Bad (தீமை):</b> The toughest phase of his life. Had to work twice as hard for basic results, facing sudden financial blocks and high stress.", bullet_style))

# Chapter 4
story.append(Paragraph("<b>Chapter 4: The Property & Wealth Era & The Mercury Period (2003 to 2020)</b>", body_style))
story.append(Paragraph("• <b>About:</b> Financial growth and establishing family security. Mercury (property lord) was in his house of wealth.", bullet_style))
story.append(Paragraph("• <b>🟢 The Good (நன்மை):</b> His golden era for acquiring land, houses, and vehicles. Great success in business and commercial activities.", bullet_style))
story.append(Paragraph("• <b>🔴 The Bad (தீமை):</b> Experienced constant overthinking and anxiety about family future, along with minor paperwork/documentation headaches.", bullet_style))

# Chapter 5
story.append(Paragraph("<b>Chapter 5: The Winding Down Era & The Ketu Period (2020 to January 2027) [Current Period]</b>", body_style))
story.append(Paragraph("• <b>About:</b> Detachment, letting go of old assets (like the Tiruppur property), and preparing for relocation. Ketu is in his 7th House.", bullet_style))
story.append(Paragraph("• <b>🟢 The Good (நன்மை):</b> Deep spiritual growth, clearing old family liabilities, and learning to let go of material worries.", bullet_style))
story.append(Paragraph("• <b>🔴 The Bad (தீமை):</b> Causes the current feeling of being 'stuck' and property sale delays. Lowball offers from buyers and a feeling of isolation.", bullet_style))

# Chapter 6
story.append(Paragraph("<b>Chapter 6: The Golden Retirement & The Venus Period (January 2027 to 2047) [Future Period]</b>", body_style))
story.append(Paragraph("• <b>About:</b> 20 years of luxury, massive wealth, family happiness, and a peaceful lifestyle. Venus is in his house of wealth.", bullet_style))
story.append(Paragraph("• <b>🟢 The Good (நன்மை):</b> Extreme financial upgrade. The assets sold will multiply. He will enjoy immense pride through your success and live in royal comfort.", bullet_style))
story.append(Paragraph("• <b>🔴 The Bad (தீமை):</b> High expenses on luxury and family events. Needs to watch his diet (sugar, throat, and rich food intake).", bullet_style))

doc.build(story)
print(f"PDF successfully overwritten at: {out_path}")
