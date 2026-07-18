import os
import urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm

out_path = r"F:\astro\reports\Thangavel_Tamil_Timeline.pdf"
font_path = r"F:\astro\scratch\NotoSansTamil-Regular.ttf"

# Download Tamil Font if not exists
if not os.path.exists(font_path):
    url = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansTamil/NotoSansTamil-Regular.ttf"
    urllib.request.urlretrieve(url, font_path)

# Register Font
pdfmetrics.registerFont(TTFont('Tamil', font_path))

# Create PDF
doc = SimpleDocTemplate(out_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
styles = getSampleStyleSheet()

# Custom Styles
title_style = ParagraphStyle(
    'TitleStyle',
    fontName='Tamil',
    fontSize=16,
    spaceAfter=20,
    leading=20
)

body_style = ParagraphStyle(
    'BodyStyle',
    fontName='Tamil',
    fontSize=12,
    spaceAfter=15,
    leading=18
)

bold_style = ParagraphStyle(
    'BoldStyle',
    fontName='Tamil',
    fontSize=13,
    spaceAfter=8,
    leading=18
)

story = []

# Title
story.append(Paragraph("குடும்ப சொத்து மற்றும் இடமாற்ற காலக்கோடு (2026 - 2028)", title_style))
story.append(Spacer(1, 0.5*cm))

# Point 1
story.append(Paragraph("1. தற்போதைய நிலை (திருப்பூர் சொத்து விற்பனை ஏன் தாமதமாகிறது?):", bold_style))
story.append(Paragraph("உங்கள் தந்தை தற்போது தனது கேது தசையின் மிகக் கடைசி கட்டத்தில் உள்ளார் (இது ஜனவரி 2027-ல் முடிகிறது). ஜோதிட ரீதியாக கேது என்பது 'பழையதை விட்டு விலகுவதைக்' குறிக்கும். இதனால்தான் நீங்கள் திருப்பூரிலிருந்து மாற முடிவு செய்துள்ளீர்கள். ஆனால் ஒரு தசை முடியப்போகும் காலகட்டம் (தசா சந்தி) எப்போதுமே மந்தமாக இருக்கும். அதே நேரத்தில், நீங்கள் (மனோஜ்) 8-ம் அதிபதியான சந்திர திசையில் உள்ளீர்கள் (திடீர் மாற்றம் / சொத்து விற்பனை). இருவரின் ஜாதகமும் ஒரே நேரத்தில் 'இடமாற்றத்தை' சுட்டிக்காட்டுகின்றன.", body_style))

# Point 2
story.append(Paragraph("2. சொத்து விற்க சரியான நேரம் (செப்டம்பர் - நவம்பர் 2026):", bold_style))
story.append(Paragraph("ஜூலை அல்லது ஆகஸ்ட் மாதங்களில் நல்ல விலை கிடைக்காது. ஆனால், செப்டம்பர் 2026 முதல் நவம்பர் 2026 வரை உங்களுடைய லாப ஸ்தான அதிபதியான சுக்கிரன் மிகவும் பலம் பெறுகிறார். இந்த காலகட்டத்தில் நீங்கள் எதிர்பார்த்த நல்ல விலைக்கு சொத்து நிச்சயமாக விற்பனையாகும். எனவே செப்டம்பர் வரை பொறுமையாக இருந்து பேரத்தை முடிக்கவும்.", body_style))

# Point 3
story.append(Paragraph("3. குடும்பத்தின் பொற்காலம் (ஜனவரி 2027 முதல்):", bold_style))
story.append(Paragraph("ஜனவரி 2027-ல் உங்கள் தந்தைக்கு சுக்கிர திசை (20 வருடங்கள்) ஆரம்பமாகிறது. அவரது ஜாதகத்தில் சுக்கிரன் 2-ம் வீட்டில் (தன ஸ்தானம் - Family Wealth) அமர்ந்துள்ளார். அதுமட்டுமின்றி, 4-ம் அதிபதியான புதனும் (Real Estate Lord) அங்கேயே சுக்கிரனுடன் இணைந்துள்ளார். இந்த 20 வருட காலகட்டம் உங்கள் குடும்பத்திற்கு மிகப்பெரிய பணவரவு, புதிய சொத்து சேர்க்கை, மற்றும் ஆடம்பரமான நிதி நிலையான வாழ்க்கையைத் தரும் மிகச்சிறந்த பொற்காலமாகும்.", body_style))

doc.build(story)
print(f"PDF generated successfully at: {out_path}")
