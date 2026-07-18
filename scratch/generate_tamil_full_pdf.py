import os
import urllib.request
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm

out_path = r"F:\astro\reports\Thangavel_Full_Life_Tamil.pdf"
font_path = r"F:\astro\scratch\NotoSansTamil-Regular.ttf"

# Register Font
pdfmetrics.registerFont(TTFont('Tamil', font_path))

doc = SimpleDocTemplate(out_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

title_style = ParagraphStyle('TitleStyle', fontName='Tamil', fontSize=18, spaceAfter=20, leading=24, alignment=1)
h2_style = ParagraphStyle('H2', fontName='Tamil', fontSize=14, spaceAfter=10, spaceBefore=15, leading=18, textColor="#7d1f3d")
body_style = ParagraphStyle('Body', fontName='Tamil', fontSize=11, spaceAfter=12, leading=16, alignment=0)
bold_body = ParagraphStyle('BoldBody', fontName='Tamil', fontSize=11, spaceAfter=6, leading=16)

story = []

story.append(Paragraph("திரு. S. தங்கவேல் - முழுமையான வாழ்க்கை மற்றும் திசா காலக்கோடு", title_style))
story.append(Spacer(1, 0.5*cm))

# Intro
story.append(Paragraph("ஜாதக குறிப்புகள்: மிதுன லக்னம், துலாம் ராசி, சுவாதி நட்சத்திரம் (3-ம் பாதம்).", body_style))
story.append(Paragraph("உங்கள் தந்தையின் ஜாதகம் மிகவும் வலிமையான கிரக அமைப்புகளைக் கொண்டது. அவரது வாழ்க்கை முழுவதும் பல சிறப்பான கட்டங்களைக் கடந்து வந்துள்ளது. முழுமையான பலன்கள் கீழே கொடுக்கப்பட்டுள்ளன:", body_style))

# Personality
story.append(Paragraph("1. குணாதிசயங்கள் மற்றும் ஆளுமை (Personality)", h2_style))
story.append(Paragraph("மிதுன லக்னத்தில் பிறந்த இவர் இயல்பாகவே அதிக புத்திசாலித்தனம், சிறந்த பேச்சுத்திறன் மற்றும் அனைவரையும் அனுசரித்துச் செல்லும் குணம் கொண்டவர். லக்னத்தில் ராகு இருப்பதால் எதையும் ஆழ்ந்து சிந்தித்து, தைரியமாக முடிவெடுக்கும் ஆற்றல் இவருக்கு உண்டு.", body_style))

# Wealth
story.append(Paragraph("2. செல்வம் மற்றும் குடும்பம் (Wealth & Family)", h2_style))
story.append(Paragraph("இது இவரது ஜாதகத்தின் மிகப்பிரம்மாண்டமான பலமாகும். தன ஸ்தானமான 2-ம் வீட்டில் செல்வத்தின் அதிபதியான சுக்கிரன், புதன் (சொத்து அதிபதி) மற்றும் சூரியன் ஆகியோர் இணைந்துள்ளனர். இவர் தனது சுயமுயற்சியால் பெரும் செல்வத்தையும், ரியல் எஸ்டேட் மற்றும் குடும்ப சொத்துக்களையும் உருவாக்கும் யோகம் பெற்றவர்.", body_style))

# Health & Longevity
story.append(Paragraph("3. ஆரோக்கியம் மற்றும் ஆயுள் (Health & Longevity)", h2_style))
story.append(Paragraph("ஆயுள் ஸ்தானமான 8-ம் வீட்டில், ஆயுள்காரகனான சனி பகவான் தனது சொந்த வீட்டில் ஆட்சி பெற்று அமர்ந்துள்ளார். ஜோதிட சாஸ்திரப்படி 8-ல் சனி இருப்பது 'தீர்க்காயுள்' (மிக நீண்ட ஆயுள்) மற்றும் வயதான காலத்தில் வலுவான ஆரோக்கியத்தைத் தரக்கூடிய மிகச்சிறந்த அமைப்பாகும்.", body_style))

# Career
story.append(Paragraph("4. தொழில் மற்றும் கௌரவம் (Career & Respect)", h2_style))
story.append(Paragraph("தொழில் ஸ்தானமான 10-ம் வீட்டில் குரு பகவான் ஆட்சி பெற்றுள்ளார். இவர் எந்த துறையில் இருந்தாலும் சமூகத்தில் இவருக்கு மிகப்பெரிய மரியாதையும், நற்பெயரும், மற்றவர்களுக்கு வழிகாட்டும் தலைமைப் பண்பும் இருக்கும்.", body_style))

# Timeline
story.append(Paragraph("5. முழுமையான திசா காலக்கோடு (Full Life Timeline)", h2_style))

story.append(Paragraph("• ராகு திசை (பிறப்பு முதல் 1968 வரை):", bold_body))
story.append(Paragraph("குழந்தை பருவம் மற்றும் ஆரம்பகால வாழ்க்கை.", body_style))

story.append(Paragraph("• குரு திசை (1968 - 1984):", bold_body))
story.append(Paragraph("கல்வி, அறிவாற்றல் வளர்ச்சி மற்றும் வாழ்க்கையின் அடித்தளம் அமைக்கப்பட்ட காலம்.", body_style))

story.append(Paragraph("• சனி திசை (1984 - 2003):", bold_body))
story.append(Paragraph("மிகக் கடினமான உழைப்பு, தொழில் தொடக்கம் மற்றும் குடும்ப பொறுப்புகளை ஏற்ற காலகட்டம். சவால்களைத் தாண்டி நிலையான இடத்தைப் பிடித்த நேரம்.", body_style))

story.append(Paragraph("• புதன் திசை (2003 - 2020):", bold_body))
story.append(Paragraph("சொத்துக்கள் சேர்க்கை, குடும்ப வளர்ச்சி, மற்றும் நிதி நிலைமையில் நல்ல முன்னேற்றம் ஏற்பட்ட காலம். புதன் 4-ம் அதிபதியாக இருப்பதால் வீடு/நிலம் சார்ந்த லாபங்கள் அமைந்தன.", body_style))

story.append(Paragraph("• கேது திசை (2020 - 2027) [தற்போதைய காலகட்டம்]:", bold_body))
story.append(Paragraph("இது பழைய விஷயங்களை முடிவுக்குக் கொண்டுவரும் நேரம். குடும்பத்தில் இடமாற்றம், பழைய சொத்துக்களை விற்று புதிய இடத்தை தேடுதல், ஆன்மீக சிந்தனை அதிகரிக்கும் காலம். தற்போது இந்த தசையின் இறுதி பகுதியில் இருப்பதால் காரியங்களில் சில தாமதங்கள் இருக்கும்.", body_style))

story.append(Paragraph("• சுக்கிர திசை (ஜனவரி 2027 - 2047) [எதிர்கால பொற்காலம்]:", bold_body))
story.append(Paragraph("ஜனவரி 2027 முதல் இவருக்கு 20 வருட சுக்கிர திசை தொடங்குகிறது. சுக்கிரன் 2-ம் வீட்டில் வலிமையாக உள்ளதால், இது குடும்பத்திற்கு மிகப்பெரிய அளவிலான பணவரவு, புதிய சொத்து சேர்க்கை, ஆடம்பரமான வாழ்க்கை மற்றும் மன நிம்மதியைத் தரப்போகும் ராஜயோக காலமாகும்.", body_style))

doc.build(story)
print(f"PDF generated successfully at: {out_path}")
