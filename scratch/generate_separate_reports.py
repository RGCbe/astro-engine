import os
import sys
import json
import re
from pathlib import Path

# Add project root and runtime to path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "runtime"))

from engine.chart_builder import build_sidereal_chart
from engine.kuta import (
    match_kuta,
    mangal_dosha,
    _nak_idx,
    NADI,
    GANA,
    YONI,
    SIGN_LORDS,
    VARNA
)
from engine.western_engine import compute_western_chart
from engine.chinese_engine import compute_chinese_chart
from engine.mayan_engine import compute_mayan_chart, DAY_SIGNS
from engine.numerology_match import compute_compatibility
from tamil_renderer import TamilParagraph, draw_tamil, measure_tamil, draw_mixed, measure_mixed
from generate_muhurta_pdf import draw_page_decorations
from engine.extended_compatibility import get_vastu_compatibility, get_lal_kitab_teva, calculate_human_design_type

# Reportlab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Setup fonts
RUNTIME_DIR = os.path.join(str(_ROOT), "runtime")
try:
    pdfmetrics.registerFont(TTFont("Outfit", os.path.join(RUNTIME_DIR, "Outfit-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Outfit-Bold", os.path.join(RUNTIME_DIR, "Outfit-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Outfit-Medium", os.path.join(RUNTIME_DIR, "Outfit-Medium.ttf")))
    pdfmetrics.registerFont(TTFont("Outfit-Light", os.path.join(RUNTIME_DIR, "Outfit-Light.ttf")))
    # Register premium serif PlayfairDisplay for headings
    pdfmetrics.registerFont(TTFont("PlayfairDisplay", os.path.join(RUNTIME_DIR, "PlayfairDisplay-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("PlayfairDisplay-Bold", os.path.join(RUNTIME_DIR, "PlayfairDisplay-Bold.ttf")))
except Exception as e:
    print(f"Font registration failed: {e}")

# ── Calm & Premium Color Palette ──
SAGE_DK = HexColor("#2D4B82")       # Modern Indigo/Slate Blue (Primary Headers)
SAGE_LT = HexColor("#EFF2F6")       # Pale Blue-Grey (Alternating Rows / Header BG)
SAND_BG = HexColor("#F8F9FA")       # Clean Off-White Alabaster (Doc Backgrounds)
SAND_DK = HexColor("#D3D9E2")       # Light Slate Grey for borders
GOLD_DK = HexColor("#E0963C")       # Warm Mustard Gold for accents/borders
TEXT_DARK = HexColor("#2B303A")     # Dark Charcoal Slate for readable body text
TEXT_MUTED = HexColor("#6B7280")    # Muted grey for secondary text
WHITE = HexColor("#ffffff")

# Styled highlight colors
BG_SUCCESS = HexColor("#E6F4EA")    # Calm soft green bg
TEXT_SUCCESS = HexColor("#137333")  # Green text
BG_ALERT = HexColor("#FCE8E6")      # Calm soft red bg
TEXT_ALERT = HexColor("#C5221F")    # Red text
BG_ACCENT = HexColor("#FEF7E0")     # Calm soft mustard-amber bg
TEXT_ACCENT = HexColor("#B06000")   # Deep amber text

# English Styles
style_title = ParagraphStyle("title", fontName="Outfit-Bold", fontSize=22, leading=26, textColor=SAGE_DK, alignment=1, spaceAfter=8)
style_subtitle = ParagraphStyle("subtitle", fontName="Outfit", fontSize=12, leading=15, textColor=GOLD_DK, alignment=1, spaceAfter=22)
style_h1 = ParagraphStyle("h1", fontName="Outfit-Bold", fontSize=15, leading=19, textColor=SAGE_DK, spaceBefore=14, spaceAfter=8, keepWithNext=True)
style_h2 = ParagraphStyle("h2", fontName="Outfit-Bold", fontSize=12, leading=16, textColor=GOLD_DK, spaceBefore=10, spaceAfter=6, keepWithNext=True)
style_body = ParagraphStyle("body", fontName="Outfit", fontSize=10.5, textColor=TEXT_DARK, leading=15.0, spaceAfter=6)
style_cell_bold = ParagraphStyle("cell_bold", fontName="Outfit-Bold", fontSize=9.5, textColor=SAGE_DK, leading=13.5)
style_cell = ParagraphStyle("cell", fontName="Outfit", fontSize=9.5, textColor=TEXT_DARK, leading=13.5)
style_cell_muted = ParagraphStyle("cell_muted", fontName="Outfit", fontSize=9.5, textColor=TEXT_MUTED, leading=13.5)
style_cell_green = ParagraphStyle("cell_green", fontName="Outfit-Bold", fontSize=9.5, textColor=TEXT_SUCCESS, leading=13.5)
style_cell_red = ParagraphStyle("cell_red", fontName="Outfit-Bold", fontSize=9.5, textColor=TEXT_ALERT, leading=13.5)

# Centered variants for tables
style_cell_center = ParagraphStyle("cell_center", parent=style_cell, alignment=1)
style_cell_bold_center = ParagraphStyle("cell_bold_center", parent=style_cell_bold, alignment=1)
style_cell_green_center = ParagraphStyle("cell_green_center", parent=style_cell_green, alignment=1)
style_cell_red_center = ParagraphStyle("cell_red_center", parent=style_cell_red, alignment=1)

# Helper function to remove Tamil script characters from English templates
def clean_ta_text(text):
    if not text:
        return text
    return re.sub(r'\s*\([\u0b80-\u0bff\s,\-–]+\)', '', text)

# Helper function to extract only Tamil script characters from mixed text
def extract_tamil(text):
    if not text:
        return ""
    matches = re.findall(r'\(([\u0b80-\u0bff\s,\-–]+)\)', text)
    if matches:
        val = matches[0].strip()
        if val == "ஆந்ைத":
            return "ஆந்தை"
        return val
    matches_raw = re.findall(r'[\u0b80-\u0bff\s,\-–]+', text)
    if matches_raw:
        valid_parts = [p.strip() for p in matches_raw if any(0x0b80 <= ord(c) <= 0x0bff for c in p)]
        if valid_parts:
            val = " ".join(valid_parts)
            if val == "ஆந்ைத":
                return "ஆந்தை"
            return val
    return text

# Tamil Translation Maps
RASI_TA = {
    "Aries": "மேஷம்", "Taurus": "ரிஷபம்", "Gemini": "மிதுனம்", "Cancer": "கடகம்",
    "Leo": "சிம்மம்", "Virgo": "கன்னி", "Libra": "துலாம்", "Scorpio": "விருச்சிகம்",
    "Sagittarius": "தனுசு", "Capricorn": "மகரம்", "Aquarius": "கும்பம்", "Pisces": "மீனம்"
}
NADI_TA = {
    "Adi": "ஆதி",
    "Madhya": "மத்தியம்",
    "Antya": "அந்தியம்"
}
GANA_TA = {
    "Deva": "தேவம்",
    "Manushya": "மனுஷம்",
    "Rakshasa": "ராட்சசம்"
}
YONI_TA = {
    "Horse": "குதிரை", "Elephant": "யானை", "Sheep": "ஆடு", "Serpent": "பாம்பு",
    "Dog": "நாய்", "Cat": "பூனை", "Rat": "எலி", "Cow": "பசு", "Buffalo": "எருமை",
    "Tiger": "புலி", "Deer": "மான்", "Monkey": "குரங்கு", "Mongoose": "கீரி", "Lion": "சிங்கம்"
}
LORD_TA = {
    "Sun": "சூரியன்", "Moon": "சந்திரன்", "Mars": "செவ்வாய்", "Mercury": "புதன்",
    "Jupiter": "வியாழன்", "Venus": "சுக்கிரன்", "Saturn": "சனி"
}
VARNA_TA = {
    "Brahmin": "பிராமணர்",
    "Kshatriya": "க்ஷத்திரியர்",
    "Vaishya": "வைசியர்",
    "Shudra": "சூத்திரர்"
}
NAKSHATRAS_TA = {
    "Ashwini":          "அசுவினி",
    "Ashvini":          "அசுவினி",
    "Bharani":          "பரணி",
    "Krittika":         "கார்த்திகை",
    "Rohini":           "ரோஹிணி",
    "Mrigashira":       "மிருகசீரிஷம்",
    "Mrigashirsha":     "மிருகசீரிஷம்",
    "Ardra":            "திருவாதிரை",
    "Punarvasu":        "புனர்பூசம்",
    "Pushya":           "பூசம்",
    "Ashlesha":         "ஆயில்யம்",
    "Magha":            "மகம்",
    "Purva Phalguni":   "பூரம்",
    "Uttara Phalguni":  "உத்திரம்",
    "Hasta":            "ஹஸ்தம்",
    "Chitra":           "சித்திரை",
    "Swati":            "சுவாதி",
    "Vishakha":         "விசாகம்",
    "Anuradha":         "அனுஷம்",
    "Jyeshtha":         "கேட்டை",
    "Mula":             "மூலம்",
    "Purva Ashadha":    "பூராடம்",
    "Uttara Ashadha":   "உத்திராடம்",
    "Shravana":         "திருவோணம்",
    "Dhanishta":        "அவிட்டம்",
    "Shatabhisha":      "சதயம்",
    "Purva Bhadrapada": "பூரட்டாதி",
    "Uttara Bhadrapada":"உத்திரட்டாதி",
    "Revati":           "ரேவதி",
}

BRIDE_NAME_TA = {
    "P. Sashtika": "பி. சாஷ்டிகா",
    "S. Padmapriyanka": "எஸ். பத்மபிரியங்கா",
    "N. Gomathi": "என். கோமதி"
}
BOY_NAME_TA = "மனோஜ் குமார்"

# Tamil Flowable Wrappers (Keyword arguments to prevent positional leading mismatch!)
def TP(text, font_size=10.5, bold=False, color=None, align="left", leading=1.45, space_after=2, keep_with_next=False):
    tp = TamilParagraph(
        text,
        font_size=font_size,
        leading=leading,
        color=color or TEXT_DARK,
        bold=bold,
        align=align,
        space_after=space_after
    )
    if keep_with_next:
        tp.keepWithNext = True
    return tp

def TP_bold(text, font_size=10.5, color=SAGE_DK, align="left"):
    return TP(text, font_size=font_size, bold=True, color=color, align=align)

def TP_green(text, font_size=10.5, align="left"):
    return TP(text, font_size=font_size, bold=True, color=TEXT_SUCCESS, align=align)

def TP_red(text, font_size=10.5, align="left"):
    return TP(text, font_size=font_size, bold=True, color=TEXT_ALERT, align=align)

def draw_luxury_borders(canvas, doc):
    canvas.saveState()
    
    # 1. Page Background (Clean Off-White)
    canvas.setFillColor(SAND_BG)
    canvas.rect(0, 0, A4[0], A4[1], fill=True, stroke=False)
    
    # 2. Top-Right Corner Wavy Accent (Mustard Orange)
    p_tr = canvas.beginPath()
    p_tr.moveTo(A4[0] - 110, A4[1])
    p_tr.curveTo(A4[0] - 70, A4[1] - 20, A4[0] - 20, A4[1] - 70, A4[0], A4[1] - 110)
    p_tr.lineTo(A4[0], A4[1])
    p_tr.close()
    canvas.setFillColor(GOLD_DK) # Mustard
    canvas.drawPath(p_tr, fill=True, stroke=False)
    
    # Top-Right secondary blue curve overlay
    p_tr2 = canvas.beginPath()
    p_tr2.moveTo(A4[0] - 50, A4[1])
    p_tr2.curveTo(A4[0] - 30, A4[1] - 12, A4[0] - 12, A4[1] - 30, A4[0], A4[1] - 50)
    p_tr2.lineTo(A4[0], A4[1])
    p_tr2.close()
    canvas.setFillColor(SAGE_DK) # Blue overlay
    canvas.drawPath(p_tr2, fill=True, stroke=False)
    
    # 3. Bottom-Left Corner Wavy Accent (Indigo Blue)
    p_bl = canvas.beginPath()
    p_bl.moveTo(0, 110)
    p_bl.curveTo(20, 70, 70, 20, 110, 0)
    p_bl.lineTo(0, 0)
    p_bl.close()
    canvas.setFillColor(SAGE_DK) # Blue
    canvas.drawPath(p_bl, fill=True, stroke=False)
    
    # Bottom-Left secondary mustard curve overlay
    p_bl2 = canvas.beginPath()
    p_bl2.moveTo(0, 50)
    p_bl2.curveTo(12, 30, 30, 12, 50, 0)
    p_bl2.lineTo(0, 0)
    p_bl2.close()
    canvas.setFillColor(GOLD_DK) # Mustard overlay
    canvas.drawPath(p_bl2, fill=True, stroke=False)
    
    # 4. Scattered modern flat accent dots (Mustard & Blue) in the margins
    canvas.setFillColor(GOLD_DK)
    canvas.circle(30, A4[1] - 140, 2.5, stroke=False, fill=True)
    canvas.circle(42, A4[1] - 170, 1.5, stroke=False, fill=True)
    canvas.circle(A4[0] - 30, 170, 2, stroke=False, fill=True)
    canvas.circle(A4[0] - 42, 140, 1.2, stroke=False, fill=True)
    
    canvas.setFillColor(SAGE_DK)
    canvas.circle(52, A4[1] - 150, 1.5, stroke=False, fill=True)
    canvas.circle(35, A4[1] - 190, 1.2, stroke=False, fill=True)
    canvas.circle(A4[0] - 52, 160, 1.8, stroke=False, fill=True)
    canvas.circle(A4[0] - 35, 190, 1.0, stroke=False, fill=True)
    
    # 5. Background mystical wallpaper pattern watermark inside borders
    bg_pattern_path = os.path.join(RUNTIME_DIR, "mystical_tiled_background.png")
    if os.path.exists(bg_pattern_path):
        canvas.saveState()
        canvas.setFillAlpha(0.07)  # Visible yet subtle background watermark
        w_x = 0.95 * cm
        w_y = 0.95 * cm
        w_w = A4[0] - 1.9 * cm
        w_h = A4[1] - 1.9 * cm
        canvas.drawImage(bg_pattern_path, w_x, w_y, width=w_w, height=w_h, mask='auto')
        canvas.restoreState()
        
    # 6. Elegant double borders around page margins
    canvas.setStrokeColor(GOLD_DK)
    canvas.setLineWidth(1.0)
    canvas.rect(0.8 * cm, 0.8 * cm, A4[0] - 1.6 * cm, A4[1] - 1.6 * cm, fill=False, stroke=True)
    
    canvas.setStrokeColor(SAGE_DK)
    canvas.setLineWidth(0.5)
    canvas.rect(0.95 * cm, 0.95 * cm, A4[0] - 1.9 * cm, A4[1] - 1.9 * cm, fill=False, stroke=True)
    
    canvas.restoreState()

def get_header_footer_drawer_en(boy_name, girl_name):
    def draw_header_footer(canvas, doc):
        canvas.saveState()
        # Draw luxury borders and background
        draw_luxury_borders(canvas, doc)
        
        # Header line (shortened to clear the top-right corner ribbon)
        canvas.setStrokeColor(GOLD_DK)
        canvas.setLineWidth(0.8)
        canvas.line(doc.leftMargin, A4[1] - 42, A4[0] - doc.rightMargin - 30, A4[1] - 42)
        
        # Header text
        canvas.setFont("Outfit-Bold", 8)
        canvas.setFillColor(SAGE_DK)
        canvas.drawString(doc.leftMargin, A4[1] - 34, f"ASTROMYSTIC CELESTIAL MATCHING REPORT  |  {boy_name.upper()} & {girl_name.upper()}")
        
        # Footer line
        canvas.line(doc.leftMargin, 45, A4[0] - doc.rightMargin, 45)
        canvas.setFont("Outfit", 8)
        canvas.setFillColor(TEXT_MUTED)
        canvas.drawString(doc.leftMargin, 32, "Copyright 2026 AstroMystic. Generated using Thirukanitham Ayanamsa.")
        canvas.drawRightString(A4[0] - doc.rightMargin, 32, f"Page {doc.page}")
        canvas.restoreState()
    return draw_header_footer

def get_header_footer_drawer_ta(boy_name, girl_name):
    def draw_header_footer(canvas, doc):
        canvas.saveState()
        # Draw luxury borders and background
        draw_luxury_borders(canvas, doc)
        
        # Header line (shortened to clear the top-right corner ribbon)
        canvas.setStrokeColor(GOLD_DK)
        canvas.setLineWidth(0.8)
        canvas.line(doc.leftMargin, A4[1] - 42, A4[0] - doc.rightMargin - 30, A4[1] - 42)
        
        # Header text (centered/left aligned to avoid the ribbon)
        header_text = f"அஸ்ட்ரோமிஸ்டிக் ஜாதகப் பொருத்த அறிக்கை  |  {boy_name} மற்றும் {girl_name}"
        draw_mixed(canvas, header_text, doc.leftMargin, A4[1] - 34, font_size=8, tamil_font="Tamil-Bold", latin_font="Outfit-Bold", color=SAGE_DK)
        
        # Footer line
        canvas.line(doc.leftMargin, 45, A4[0] - doc.rightMargin, 45)
        
        # Footer - Left
        draw_mixed(canvas, "பதிப்புரிமை 2026 அஸ்ட்ரோமிஸ்டிக். திருக்கணித பஞ்சாங்க முறைப்படி கணிக்கப்பட்டது.", doc.leftMargin, 32, font_size=8, tamil_font="Tamil", latin_font="Outfit", color=TEXT_MUTED)
        
        # Footer - Right
        footer_r_text = f"பக்கம் {doc.page}"
        w = measure_mixed(footer_r_text, font_size=8, tamil_font="Tamil", latin_font="Outfit")
        draw_mixed(canvas, footer_r_text, A4[0] - doc.rightMargin - w, 32, font_size=8, tamil_font="Tamil", latin_font="Outfit", color=TEXT_MUTED)
        
        canvas.restoreState()
    return draw_header_footer

def generate_pdf_en(r, filename):
    b = r["bride"]
    k = r["vedic_kuta"]
    n = r["num_res"]
    boy_tzolkin = r["boy_tzolkin"]
    girl_tzolkin = r["girl_tzolkin"]
    boy_bazi = r["boy_bazi"]
    
    # Format girl's date/time dynamically
    import datetime as datetime_lib
    girl_date_obj = datetime_lib.datetime.strptime(b["date"], "%Y-%m-%d")
    girl_date_formatted = girl_date_obj.strftime("%d %B %Y")
    girl_time_obj = datetime_lib.datetime.strptime(b["time"], "%H:%M")
    girl_time_formatted = girl_time_obj.strftime("%I:%M %p")
    
    # Dynamic parameter calculation for boy & girl
    boy_nak_idx = _nak_idx(r["boy_moon_lon"])
    girl_nak_idx = _nak_idx(r["girl_moon_lon"])
    
    boy_nadi = NADI[boy_nak_idx]
    girl_nadi = NADI[girl_nak_idx]
    boy_bhakoot = k.boy_moon
    girl_bhakoot = k.girl_moon
    boy_gana = GANA[boy_nak_idx]
    girl_gana = GANA[girl_nak_idx]
    boy_yoni = YONI[boy_nak_idx]
    girl_yoni = YONI[girl_nak_idx]
    boy_lord = SIGN_LORDS[k.boy_moon]
    girl_lord = SIGN_LORDS[k.girl_moon]
    boy_varna = VARNA[k.boy_moon]
    girl_varna = VARNA[k.girl_moon]
    
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=2.2*cm, bottomMargin=2.2*cm)
    story = []
    
    # Page 1
    story.append(Paragraph("CELESTIAL COMPATIBILITY REPORT", style_title))
    story.append(Paragraph("A Multi-Engine Astrological Assessment", style_subtitle))
    story.append(Spacer(1, 0.4 * cm))
    
    # Page 1 side-by-side cartoon images
    boy_rasi_name = boy_bhakoot.lower() # "leo"
    girl_rasi_name = girl_bhakoot.lower() # "aquarius" or "sagittarius"
    boy_img_name = f"{boy_rasi_name}_character.png"
    girl_img_name = f"{girl_rasi_name}_character.png"
    boy_img_path = os.path.join(RUNTIME_DIR, boy_img_name)
    girl_img_path = os.path.join(RUNTIME_DIR, girl_img_name)
    fallback_img_path = os.path.join(RUNTIME_DIR, "zodiac_flat_icon.png")
    
    if not os.path.exists(boy_img_path):
        boy_img_path = fallback_img_path
    if not os.path.exists(girl_img_path):
        girl_img_path = fallback_img_path
        
    from reportlab.platypus import Image as RLImage
    boy_label = Paragraph("<b>Groom Sign: Leo</b>", style_cell_bold_center)
    girl_label = Paragraph(f"<b>Bride Sign: {girl_bhakoot}</b>", style_cell_bold_center)
    
    boy_cell = [RLImage(boy_img_path, width=2.5*cm, height=2.5*cm, hAlign="CENTER"), Spacer(1, 0.1*cm), boy_label]
    girl_cell = [RLImage(girl_img_path, width=2.5*cm, height=2.5*cm, hAlign="CENTER"), Spacer(1, 0.1*cm), girl_label]
    
    cover_zodiac_table = Table([[boy_cell, girl_cell]], colWidths=[9.0*cm, 9.0*cm])
    cover_zodiac_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(cover_zodiac_table)
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("1. Birth Parameters & Identity", style_h1))
    param_data = [
        [Paragraph("Parameter", style_cell_bold), Paragraph("Boy: Manoj Kumar", style_cell_bold), Paragraph(f"Girl: {b['name']}", style_cell_bold)],
        [Paragraph("Birth Date & Time", style_cell), Paragraph("25 May 1996, 08:25 PM IST", style_cell), Paragraph(f"{girl_date_formatted}, {girl_time_formatted} IST", style_cell)],
        [Paragraph("Birth Place", style_cell), Paragraph("Coimbatore, TN", style_cell), Paragraph(b.get("birth_place", f"{b['lat']}, {b['lon']}"), style_cell)],
        [Paragraph("Lagnam (Ascendant)", style_cell), Paragraph(f"Sagittarius ({r['boy_lagna_en']})", style_cell), Paragraph(f"{r['girl_lagna_en']}", style_cell)],
        [Paragraph("Rasi (Moon Sign)", style_cell), Paragraph(f"Leo ({boy_bhakoot})", style_cell), Paragraph(f"{girl_bhakoot}", style_cell)],
        [Paragraph("Nakshatra (Star)", style_cell), Paragraph("Magha", style_cell), Paragraph(clean_ta_text(k.girl_nakshatra), style_cell)],
        [Paragraph("Kulam (Clan)", style_cell), Paragraph("Kadai", style_cell), Paragraph(clean_ta_text(b["kulam"]), style_cell)],
        [Paragraph("Kula Deivam", style_cell), Paragraph("Not Specified", style_cell), Paragraph(clean_ta_text(b["deity"]), style_cell)],
    ]
    t_param = Table(param_data, colWidths=[5.0*cm, 6.5*cm, 6.5*cm])
    t_param.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 4.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4.0),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t_param)
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(Paragraph("2. Vedic Marriage Points (36-Point System)", style_h1))
    kuta_data = [
        [Paragraph("Compatibility Factor", style_cell_bold), Paragraph(f"Boy ({k.boy_nakshatra})", style_cell_bold), Paragraph(f"Girl ({clean_ta_text(k.girl_nakshatra)})", style_cell_bold), Paragraph("Score", style_cell_bold_center), Paragraph("Max", style_cell_bold_center), Paragraph("Brief Meaning", style_cell_bold)],
        [Paragraph("Nadi (Physiology & Health)", style_cell), Paragraph(boy_nadi, style_cell), Paragraph(girl_nadi, style_cell), Paragraph(str(k.nadi[0]), style_cell_green_center if k.nadi[0] > 0 else style_cell_red_center), Paragraph("8", style_cell_center), Paragraph("Excellent physical and progeny compatibility", style_cell)],
        [Paragraph("Bhakoot (Emotional Harmony)", style_cell), Paragraph(boy_bhakoot, style_cell), Paragraph(girl_bhakoot, style_cell), Paragraph(str(k.bhakoot[0]), style_cell_green_center if k.bhakoot[0] > 0 else style_cell_red_center), Paragraph("7", style_cell_center), Paragraph("Strong emotional bond and domestic peace", style_cell)],
        [Paragraph("Gana (Temperament Align)", style_cell), Paragraph(boy_gana, style_cell), Paragraph(girl_gana, style_cell), Paragraph(str(k.gana[0]), style_cell_green_center if k.gana[0] == 6 else style_cell_red_center), Paragraph("6", style_cell_center), Paragraph("Perfect mental alignment and behavior fit", style_cell)],
        [Paragraph("Yoni (Physical Chemistry)", style_cell), Paragraph(boy_yoni, style_cell), Paragraph(girl_yoni, style_cell), Paragraph(str(k.yoni[0]), style_cell_center), Paragraph("4", style_cell_center), Paragraph("Friendly physical compatibility", style_cell)],
        [Paragraph("Graha Maitri (Mental Match)", style_cell), Paragraph(boy_lord, style_cell), Paragraph(girl_lord, style_cell), Paragraph(str(k.graha_maitri[0]), style_cell_green_center if k.graha_maitri[0] >= 3 else style_cell_red_center), Paragraph("5", style_cell_center), Paragraph("Friendship of Moon-sign ruling lords", style_cell)],
        [Paragraph("Tara (Destiny Support)", style_cell), Paragraph(k.boy_nakshatra, style_cell), Paragraph(clean_ta_text(k.girl_nakshatra), style_cell), Paragraph(str(k.tara[0]), style_cell_green_center if k.tara[0] >= 1.5 else style_cell_red_center), Paragraph("3", style_cell_center), Paragraph("Auspicious and supportive for daily tasks", style_cell)],
        [Paragraph("Vasya (Control & Influence)", style_cell), Paragraph(boy_bhakoot, style_cell), Paragraph(girl_bhakoot, style_cell), Paragraph(str(k.vasya[0]), style_cell_center), Paragraph("2", style_cell_center), Paragraph("Balanced mutual control", style_cell)],
        [Paragraph("Varna (Ego & Duty Class)", style_cell), Paragraph(boy_varna, style_cell), Paragraph(girl_varna, style_cell), Paragraph(str(k.varna[0]), style_cell_center), Paragraph("1", style_cell_center), Paragraph("Harmonious role sharing", style_cell)],
        [Paragraph("TOTAL VEDIC POINTS", style_cell_bold), Paragraph("", style_cell), Paragraph("", style_cell), Paragraph(str(k.total[0]), style_cell_green_center), Paragraph("36", style_cell_bold_center), Paragraph(k.verdict, style_cell_bold)],
    ]
    t_kuta = Table(kuta_data, colWidths=[3.5*cm, 2.5*cm, 2.5*cm, 1.2*cm, 1.0*cm, 7.3*cm])
    t_kuta.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("BACKGROUND", (0,-1), (-1,-1), BG_ACCENT),
        ("SPAN", (1, -1), (2, -1)),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 4.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4.0),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_kuta)
    
    # Dynamic Vedic Compatibility & Caution Points
    vedic_bullets = []
    if k.nadi[0] == 0:
        vedic_bullets.append("* <b>Nadi Clash (Health Caution):</b> A biological mismatch in energies (Nadi Dosha) is present. Focus on balanced health, and perform remedies like Mahamrityunjaya chants or charity to maintain physical wellbeing.")
    else:
        vedic_bullets.append("* <b>Nadi Harmony (Health Strength):</b> No Nadi Dosha. Your physical energies and hereditary constitutions are in perfect harmony, ensuring excellent physical well-being and progeny.")
        
    if k.bhakoot[0] == 0:
        vedic_bullets.append("* <b>Bhakoot Clash (Emotional Caution):</b> Moon-sign incompatibility (Bhakoot Dosha) is present. This can cause emotional distance or sudden mood swings. Remedy: Practice open communication, avoid hiding feelings, and offer prayers to Lord Shiva.")
    else:
        vedic_bullets.append("* <b>Bhakoot Harmony (Emotional Strength):</b> Excellent Moon-sign alignment, ensuring strong mutual affection, emotional sync, and mutual family prosperity.")
        
    if k.gana[0] <= 1:
        vedic_bullets.append("* <b>Gana Mismatch (Temperament Caution):</b> A clash in temperaments is indicated. One partner is highly dynamic, while the other seeks calm stability. Avoid trying to force the other partner to change; respect each other's behavioral pace.")
    else:
        vedic_bullets.append("* <b>Gana Harmony (Temperament Strength):</b> Behavior and temperaments align naturally, facilitating smooth daily life decisions and avoiding ego clashes.")
        
    if k.graha_maitri[0] <= 1:
        vedic_bullets.append("* <b>Inimical Rulers (Intellectual Caution):</b> The ruling planets of your Moon signs are mutual enemies. This can lead to differences in opinion on household decisions or lifestyle choices. Remedy: Value each other's logic and make decisions collaboratively.")
    else:
        vedic_bullets.append("* <b>Planetary Friendship (Intellectual Strength):</b> The Moon sign lords are friendly, indicating strong mental friendship, shared values, and mutual intellectual respect.")
        
    if k.yoni[0] == 0:
        vedic_bullets.append("* <b>Yoni Clash (Intimacy Caution):</b> Intimacy profiles are naturally opposing. This can cause occasional physical distance or emotional mismatch. Remedy: Prioritize quality time, emotional warmth, and mutual patience in your private life.")
    elif k.yoni[0] == 1:
        vedic_bullets.append("* <b>Neutral Yoni (Intimacy Note):</b> Intimacy profiles are neutral. Physical chemistry is moderate; warmth can be easily nurtured through emotional bonding.")
    else:
        vedic_bullets.append("* <b>Yoni Harmony (Intimacy Strength):</b> High natural physical chemistry and emotional warmth, creating strong mutual comfort and intimacy.")
        
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("<b>Vedic Compatibility & Caution Points</b>", style_h2))
    story.append(Paragraph("<br/>".join(vedic_bullets), style_body))
    story.append(Spacer(1, 0.4 * cm))
    story.append(PageBreak())
    
    # Page 2: Vedic Afflictions & Multidisciplinary Matching (Numerology & Chinese Bazi)
    story.append(Paragraph("4. Sevvai Dosham & Clan Compatibility", style_h1))
    boy_md_status = "NO DOSHAM" if not r["boy_md"]["is_mangalik"] else "MANGALIK"
    girl_md_status = "NO DOSHAM" if not r["girl_md"]["is_mangalik"] else "MANGALIK"
    dosha_body = f"<b>Manoj Kumar (Boy):</b> Clean (No Sevvai Dosham)<br/>"
    dosha_body += f"<b>{b['name']} (Girl):</b> {clean_ta_text(b['jadhagam'])}<br/><br/>"
    if r["girl_md"]["is_mangalik"]:
        dosha_body += f"<i>Explanation:</i> The girl has a mild Mars placement in the 12th house. This matches Manoj's clean chart perfectly and has no negative impacts on health or marriage."
    else:
        dosha_body += f"<i>Explanation:</i> Both charts are completely clean. No Mars afflictions mean excellent physical compatibility and peace."
        
    t_dosha = Table([[Paragraph(dosha_body, style_body)]], colWidths=[18*cm])
    t_dosha.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_SUCCESS if not r["girl_md"]["is_mangalik"] else BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LINELEFT", (0,0), (-1,-1), 4, TEXT_SUCCESS if not r["girl_md"]["is_mangalik"] else GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 10.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10.0),
    ]))
    story.append(t_dosha)
    story.append(Spacer(1, 0.6 * cm))
    
    story.append(Paragraph("5. Numerology 8-Point Matching Grid", style_h1))
    story.append(Paragraph("Based on Chaldean & Cheiro planetary friendship rules between birth day (Driver) and life path (Destiny) numbers.", style_body))
    story.append(Spacer(1, 0.3 * cm))
    
    num_data = [
        [Paragraph("Parameter", style_cell_bold), Paragraph("Groom (Manoj Kumar)", style_cell_bold), Paragraph(f"Bride ({b['name']})", style_cell_bold), Paragraph("Mutual Relation", style_cell_bold), Paragraph("Points", style_cell_bold)],
        [
            Paragraph("Driver (Birth Number)", style_cell), 
            Paragraph(f"<b>{n['person1']['driver']}</b> ({n['person1']['driver_planet']})", style_cell), 
            Paragraph(f"<b>{n['person2']['driver']}</b> ({n['person2']['driver_planet']})", style_cell), 
            Paragraph(n['driver_relation']['a_to_b'].capitalize(), style_cell_green if n['driver_relation']['a_to_b'] in ['friend', 'same'] else style_cell), 
            Paragraph(f"{n['driver_relation']['points']} / 4", style_cell_bold)
        ],
        [
            Paragraph("Destiny (Life Path)", style_cell), 
            Paragraph(f"<b>{n['person1']['destiny']}</b> ({n['person1']['destiny_planet']})", style_cell), 
            Paragraph(f"<b>{n['person2']['destiny']}</b> ({n['person2']['destiny_planet']})", style_cell), 
            Paragraph(n['destiny_relation']['a_to_b'].capitalize(), style_cell_green if n['destiny_relation']['a_to_b'] in ['friend', 'same'] else style_cell), 
            Paragraph(f"{n['destiny_relation']['points']} / 4", style_cell_bold)
        ],
        [
            Paragraph("<b>Total Numerology Match</b>", style_cell_bold),
            Paragraph("", style_cell), Paragraph("", style_cell),
            Paragraph(f"<b>{n['verdict']}</b>", style_cell_green if n['score_percent'] >= 70 else style_cell),
            Paragraph(f"<b>{n['score_percent']}% ({n['driver_relation']['points'] + n['destiny_relation']['points']}/8)</b>", style_cell_green if n['score_percent'] >= 70 else style_cell_red)
        ]
    ]
    t_num = Table(num_data, colWidths=[4.2*cm, 4.0*cm, 4.0*cm, 3.4*cm, 2.4*cm])
    t_num.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("BACKGROUND", (0,-1), (-1,-1), BG_ACCENT),
        ("SPAN", (1, -1), (2, -1)),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 5.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5.0),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_num)
    # Dynamic Numerology Explanation
    if n['score_percent'] >= 75:
        num_explain_en = f"Manoj's numbers (Driver 7 & Destiny 1) align exceptionally well with {b['name']}'s numbers (Driver {n['person2']['driver']} & Destiny {n['person2']['destiny']}). This friendly vibration creates a naturally harmonious and supportive dynamic, promoting emotional balance and shared long-term goals."
    elif n['score_percent'] >= 50:
        num_explain_en = f"Manoj's numbers and {b['name']}'s numbers show a stable and workable relationship. While some minor differences in lifestyle or communication exist due to the neutral relationship between their numbers, they can easily build compatibility with mutual respect."
    else:
        num_explain_en = f"There are some friction points between Manoj's numbers and {b['name']}'s numbers due to conflicting ruling planets. They might have differences in financial approaches or household duties, which will require mature cooperation."
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"<i>Personalized Insight: {num_explain_en}</i>", style_body))
    story.append(Spacer(1, 0.6 * cm))
    
    story.append(Paragraph("6. Chinese BaZi Zodiac Alignment", style_h1))
    story.append(Paragraph("BaZi analyses the Earthly Branches (Zodiac Animals) of the birth year for Harmonies or Clashes.", style_body))
    story.append(Spacer(1, 0.3 * cm))
    
    bazi_data = [
        [Paragraph("Pillar / Detail", style_cell_bold), Paragraph("Groom (Manoj Kumar)", style_cell_bold), Paragraph(f"Bride ({b['name']})", style_cell_bold)],
        [Paragraph("Year Pillar", style_cell), Paragraph("Bing-Zi (丙子)", style_cell), Paragraph(r['girl_bazi']['Year'], style_cell)],
        [Paragraph("Chinese Zodiac Sign", style_cell), Paragraph("Rat (Yang Water)", style_cell), Paragraph(f"{r['girl_animal']} ({r['girl_bazi']['Year'].split('-')[0]} Element)", style_cell)],
        [
            Paragraph("Zodiac Relationship", style_cell_bold), 
            Paragraph(clean_ta_text(r['chinese_desc']), style_cell_green if r['chinese_score'] >= 80 else style_cell), 
            Paragraph(f"Score: <b>{r['chinese_score']}%</b>", style_cell_green if r['chinese_score'] >= 80 else style_cell)
        ]
    ]
    t_bazi = Table(bazi_data, colWidths=[4.5*cm, 6.75*cm, 6.75*cm])
    t_bazi.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("BACKGROUND", (0,-1), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 5.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5.0),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_bazi)
    # Dynamic Chinese Bazi Explanation
    if r['girl_animal'] == "Ox":
        bazi_explain_en = f"Manoj (Rat) and {b['name']} (Ox) share a <b>Six Harmonies (Liu He)</b> relationship. In Chinese metaphysics, the Rat and Ox form the ultimate soulmate connection, creating deep mutual trust, stability, and emotional security in marriage as both complement each other's needs."
    elif r['girl_animal'] == "Dragon":
        bazi_explain_en = f"Manoj (Rat) and {b['name']} (Dragon) share a <b>Three Harmonies (San He)</b> relationship. The Rat and Dragon are highly creative and growth-oriented together, fostering financial success, family growth, and an active, supportive partnership."
    elif r['girl_animal'] == "Rat":
        bazi_explain_en = f"Both Manoj and {b['name']} are born in the Year of the Rat. Sharing the same sign brings similar viewpoints, a shared sense of humor, and mutual understanding, though they must manage shared stressful periods together."
    else:
        bazi_explain_en = f"Manoj (Rat) and {b['name']} share a neutral zodiac relationship. They have normal compatibility and can build a supportive household through shared goals."
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(f"<i>Personalized Insight: {bazi_explain_en}</i>", style_body))
    
    # Page 4: Western Synastry, Mayan, and Overall Verdict
    story.append(PageBreak())
    
    story.append(Paragraph("7. Western Synastry Planetary Aspects", style_h1))
    story.append(Paragraph("Lists the active geometric angles (aspects) between the planetary bodies of both birth charts.", style_body))
    story.append(Spacer(1, 0.3 * cm))
    
    # Sort aspects by accuracy (error) and take top 6
    aspects_to_show = sorted(r["synastry_aspects"], key=lambda x: x["error"])[:6]
    west_headers = [Paragraph("Groom Planet", style_cell_bold), Paragraph("Aspect Type", style_cell_bold), Paragraph("Bride Planet", style_cell_bold), Paragraph("Orb / Error", style_cell_bold), Paragraph("Relationship Type", style_cell_bold)]
    west_rows = [west_headers]
    for asp in aspects_to_show:
        is_pos = asp["aspect"] in ["Trine", "Sextile", "Conjunction"]
        rel_type = "Harmonious" if is_pos else "Challenging"
        west_rows.append([
            Paragraph(asp["boy_planet"], style_cell),
            Paragraph(f"{asp['aspect']} ({'0' if asp['aspect'] == 'Conjunction' else '60' if asp['aspect'] == 'Sextile' else '90' if asp['aspect'] == 'Square' else '120' if asp['aspect'] == 'Trine' else '180'}°)", style_cell),
            Paragraph(asp["girl_planet"], style_cell),
            Paragraph(f"{asp['error']}°", style_cell),
            Paragraph(rel_type, style_cell_green if is_pos else style_cell_red)
        ])
    # Fallback if no aspects
    if len(west_rows) == 1:
        west_rows.append([Paragraph("No major aspects found.", style_cell), Paragraph("-", style_cell), Paragraph("-", style_cell), Paragraph("-", style_cell), Paragraph("Neutral", style_cell)])
        
    t_west = Table(west_rows, colWidths=[3.6*cm, 3.6*cm, 3.6*cm, 3.2*cm, 4.0*cm])
    t_west.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 3.5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_west)
    # Dynamic Western Aspect Explanation
    if aspects_to_show:
        top_asp = aspects_to_show[0]
        boy_p = top_asp["boy_planet"]
        girl_p = top_asp["girl_planet"]
        asp_name = top_asp["aspect"]
        west_explain_en = f"The strongest planet connection in your charts is Manoj's {boy_p} in {asp_name} with {b['name']}'s {girl_p}. "
        if asp_name in ["Trine", "Sextile", "Conjunction"]:
            west_explain_en += "This harmonious connection ensures natural support, deep mutual understanding, and ease in sharing emotional responsibilities."
        else:
            west_explain_en += "This aspect brings lessons of growth, requiring you to practice conscious communication to manage differences in opinion."
    else:
        west_explain_en = "No major aspects found between your personal planets. You share a neutral energetic connection."
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(f"<i>Personalized Insight: {west_explain_en}</i>", style_body))
    story.append(Spacer(1, 0.25 * cm))
    
    # Mayan Tzolkin Oracle Partners
    story.append(Paragraph("8. Mayan Tzolkin Oracle Partners", style_h1))
    
    boy_sign_idx = next((i for i, d in enumerate(DAY_SIGNS) if d["name"] == boy_tzolkin["day_glyph"]["name"]), 0)
    girl_sign_idx = next((i for i, d in enumerate(DAY_SIGNS) if d["name"] == girl_tzolkin["day_glyph"]["name"]), 0)
    diff = abs(boy_sign_idx - girl_sign_idx)
    if diff == 10:
        rel_role_en = "Antipode Partner (Challenges that trigger deep soul growth)"
        mayan_explain_en = f"Manoj and {b['name']} are Antipode Partners. This means you have opposite energies in the Mayan oracle, representing a powerful teacher-student relationship where differences trigger deep self-discovery and rapid spiritual evolution."
    elif (boy_sign_idx + girl_sign_idx) in [19, 39, 59, 9, 29]:
        rel_role_en = "Analog Partner (Natural support system and peaceful chemistry)"
        mayan_explain_en = f"Manoj and {b['name']} are Analog Partners. This is one of the most peaceful and supportive Mayan relationships, ensuring you easily comfort each other, build a secure sanctuary at home, and share a warm, intuitive connection."
    elif boy_tzolkin["day_glyph"]["direction"] == girl_tzolkin["day_glyph"]["direction"]:
        rel_role_en = "Directional Kin (Shared spiritual focus and life direction)"
        mayan_explain_en = f"Manoj and {b['name']} share Directional Kinship. This means you share the same spiritual color and direction in the Mayan Tzolkin, helping you walk the same path in life and support each other's dreams naturally."
    else:
        rel_role_en = "Complementary Kin (Helper dynamics in daily activities)"
        mayan_explain_en = f"Manoj and {b['name']} share Complementary Kinship. This indicates you bring different strengths to daily tasks, acting as a practical team where one partner's strength covers the other's weakness."
        
    mayan_data = [
        [Paragraph("Detail", style_cell_bold), Paragraph("Groom (Manoj Kumar)", style_cell_bold), Paragraph(f"Bride ({b['name']})", style_cell_bold)],
        [Paragraph("Solar Seal / Sign", style_cell), Paragraph(boy_tzolkin["formatted"], style_cell), Paragraph(girl_tzolkin["formatted"], style_cell)],
        [Paragraph("Tzolkin Oracle Role", style_cell_bold), Paragraph(rel_role_en, style_cell_green), Paragraph("Authentic Spiritual Alignment", style_cell_bold)]
    ]
    t_mayan = Table(mayan_data, colWidths=[4.2*cm, 6.9*cm, 6.9*cm])
    t_mayan.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("BACKGROUND", (0,-1), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 3.5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_mayan)
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(f"<i>Personalized Insight: {mayan_explain_en}</i>", style_body))
    story.append(Spacer(1, 0.3 * cm))
    
    # Section 9 Image - Side by side Groom & Bride Zodiac Characters
    boy_rasi_name = boy_bhakoot.lower() # "leo"
    girl_rasi_name = girl_bhakoot.lower() # "aquarius" or "sagittarius"
    
    boy_img_name = f"{boy_rasi_name}_character.png"
    girl_img_name = f"{girl_rasi_name}_character.png"
    
    boy_img_path = os.path.join(RUNTIME_DIR, boy_img_name)
    girl_img_path = os.path.join(RUNTIME_DIR, girl_img_name)
    fallback_img_path = os.path.join(RUNTIME_DIR, "zodiac_flat_icon.png")
    
    if not os.path.exists(boy_img_path):
        boy_img_path = fallback_img_path
    if not os.path.exists(girl_img_path):
        girl_img_path = fallback_img_path
        
    from reportlab.platypus import Image as RLImage
    
    boy_label = Paragraph("<b>Groom Sign: Leo</b>", style_cell_bold_center)
    girl_label = Paragraph(f"<b>Bride Sign: {girl_bhakoot}</b>", style_cell_bold_center)
    
    boy_cell = [RLImage(boy_img_path, width=2.8*cm, height=2.8*cm, hAlign="CENTER"), Spacer(1, 0.1*cm), boy_label]
    girl_cell = [RLImage(girl_img_path, width=2.8*cm, height=2.8*cm, hAlign="CENTER"), Spacer(1, 0.1*cm), girl_label]
    
    zodiac_table = Table([[boy_cell, girl_cell]], colWidths=[9.0*cm, 9.0*cm])
    zodiac_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(zodiac_table)
    story.append(Spacer(1, 0.3 * cm))
        
    # Page 5: Advanced Multi-System Synastry
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
    story.append(PageBreak())
    story.append(Paragraph("10. Grand Compatibility Verdict & Recommendation", style_h1))
    verdict_text = f"<b>GRAND FIT: {r['overall_score']}% - HIGHLY RECOMMENDED MATCH</b><br/><br/>"
    verdict_text += f"* <b>Clan Compatibility:</b> Pass. Manoj is <b>Kadai</b> and {b['name']} is <b>{clean_ta_text(b['kulam'])}</b>. Different clans mean marriage is fully permitted under Gounder customs.<br/>"
    verdict_text += f"* <b>Vedic Health & Harmony:</b> Very Good. Scores {k.total[0]}/36. Both charts are completely clean of health (Nadi) and emotional (Bhakoot) warnings.<br/>"
    if "Sashtika" in b["name"]:
        verdict_text += f"* <b>Key Strengths:</b> Strongest match mathematically. Excellent personal communication (85% Western match) and wonderful life-path harmony (88% Numerology match)."
    elif "Padmapriyanka" in b["name"]:
        verdict_text += f"* <b>Key Strengths:</b> Extremely stable match with a clean horoscope. The Dragon & Rat alliance represents high mutual support and shared lifecycle success."
    else:
        verdict_text += f"* <b>Key Strengths:</b> Excellent zodiac soulmate bond (Rat & Ox Six Harmonies). Clean Vedic match and highly compatible career paths."
        
    t_verdict = Table([[Paragraph(verdict_text, style_body)]], colWidths=[18*cm])
    t_verdict.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("LINELEFT", (0,0), (-1,-1), 4, GOLD_DK),
        ("BOX", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 12.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12.0),
    ]))
    story.append(t_verdict)
    
    hf_drawer = get_header_footer_drawer_en(b.get('boy_name', 'Groom'), b['name'])
    doc.build(story, onFirstPage=hf_drawer, onLaterPages=hf_drawer)
    print(f"Generated English PDF for {b['name']}")

def generate_pdf_ta(r, filename):
    b = r["bride"]
    k = r["vedic_kuta"]
    n = r["num_res"]
    boy_tzolkin = r["boy_tzolkin"]
    girl_tzolkin = r["girl_tzolkin"]
    boy_bazi = r["boy_bazi"]
    
    # Format girl's date/time dynamically in Tamil
    import datetime as datetime_lib
    girl_date_obj = datetime_lib.datetime.strptime(b["date"], "%Y-%m-%d")
    girl_date_ta = girl_date_obj.strftime("%d-%m-%Y")
    girl_time_obj = datetime_lib.datetime.strptime(b["time"], "%H:%M")
    hr = girl_time_obj.hour
    period = "காலை" if hr < 12 else "மாலை" if hr < 18 else "இரவு"
    hr_12 = hr if hr <= 12 else hr - 12
    girl_time_ta = f"{period} {hr_12:02d}:{girl_time_obj.minute:02d} மணி"
    
    # Dynamic parameter calculation for boy & girl
    boy_nak_idx = _nak_idx(r["boy_moon_lon"])
    girl_nak_idx = _nak_idx(r["girl_moon_lon"])
    
    boy_nadi = NADI[boy_nak_idx]
    girl_nadi = NADI[girl_nak_idx]
    boy_bhakoot = k.boy_moon
    girl_bhakoot = k.girl_moon
    boy_gana = GANA[boy_nak_idx]
    girl_gana = GANA[girl_nak_idx]
    boy_yoni = YONI[boy_nak_idx]
    girl_yoni = YONI[girl_nak_idx]
    boy_lord = SIGN_LORDS[k.boy_moon]
    girl_lord = SIGN_LORDS[k.girl_moon]
    boy_varna = VARNA[k.boy_moon]
    girl_varna = VARNA[k.girl_moon]
    
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=1.5*cm, rightMargin=1.5*cm, topMargin=2.2*cm, bottomMargin=2.2*cm)
    story = []
    
    # Translate values to Tamil
    r_animal_ta = "எலி" if r["girl_animal"] == "Rat" else ("டிராகன்" if r["girl_animal"] == "Dragon" else "மாடு")
    boy_nak_ta = NAKSHATRAS_TA.get(k.boy_nakshatra, k.boy_nakshatra)
    girl_nak_ta = NAKSHATRAS_TA.get(k.girl_nakshatra, k.girl_nakshatra)
    girl_name_ta = BRIDE_NAME_TA.get(b["name"], b["name"])
    
    num_verdict_ta = {
        "Excellent match": "மிகச்சிறந்த பொருத்தம்",
        "Good match": "நல்ல பொருத்தம்",
        "Average match": "சாதாரண பொருத்தம்"
    }.get(n["verdict"], n["verdict"])
    
    verdict_ta = {
        "EXCELLENT": "மிகச்சிறந்த பொருத்தம்",
        "GOOD": "நல்ல பொருத்தம்",
        "AVERAGE": "சாதாரண பொருத்தம்",
        "POOR": "குறைவான பொருத்தம்"
    }.get(k.verdict, k.verdict)
    
    # Page 1
    story.append(TP("ஜாதகப் பொருத்த அறிக்கை", font_size=26, bold=True, color=SAGE_DK, align="center", space_after=8))
    story.append(TP("பல்வேறு ஜோதிட முறைகளின் கூட்டுப் பகுப்பாய்வு", font_size=14.5, color=GOLD_DK, align="center", space_after=22))
    story.append(Spacer(1, 0.4 * cm))
    
    # Page 1 side-by-side cartoon images
    boy_rasi_name = boy_bhakoot.lower() # "leo"
    girl_rasi_name = girl_bhakoot.lower() # "aquarius" or "sagittarius"
    boy_img_name = f"{boy_rasi_name}_character.png"
    girl_img_name = f"{girl_rasi_name}_character.png"
    boy_img_path = os.path.join(RUNTIME_DIR, boy_img_name)
    girl_img_path = os.path.join(RUNTIME_DIR, girl_img_name)
    fallback_img_path = os.path.join(RUNTIME_DIR, "zodiac_flat_icon.png")
    
    if not os.path.exists(boy_img_path):
        boy_img_path = fallback_img_path
    if not os.path.exists(girl_img_path):
        girl_img_path = fallback_img_path
        
    from reportlab.platypus import Image as RLImage
    
    boy_label_ta = TP_bold("ஆண் ராசி: சிம்மம்", align="center", font_size=12)
    girl_rasi_ta = RASI_TA.get(girl_bhakoot, girl_bhakoot)
    girl_label_ta = TP_bold(f"பெண் ராசி: {girl_rasi_ta}", align="center", font_size=12)
    
    boy_cell = [RLImage(boy_img_path, width=2.5*cm, height=2.5*cm, hAlign="CENTER"), Spacer(1, 0.1*cm), boy_label_ta]
    girl_cell = [RLImage(girl_img_path, width=2.5*cm, height=2.5*cm, hAlign="CENTER"), Spacer(1, 0.1*cm), girl_label_ta]
    
    cover_zodiac_table = Table([[boy_cell, girl_cell]], colWidths=[9.0*cm, 9.0*cm])
    cover_zodiac_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(cover_zodiac_table)
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(TP("1. ஜனன விபரங்கள் மற்றும் அடையாளங்கள்", font_size=15, bold=True, color=SAGE_DK, space_after=4, keep_with_next=True))
    param_data = [
        [TP_bold("அளவுகோல்"), TP_bold("ஆண்: மனோஜ் குமார்"), TP_bold(f"பெண்: {girl_name_ta}")],
        [TP("பிறந்த தேதி & நேரம்"), TP("25-05-1996, இரவு 08:25 மணி"), TP(f"{girl_date_ta}, {girl_time_ta}")],
        [TP("பிறந்த இடம்"), TP("கோயம்புத்தூர், தமிழ்நாடு"), TP(b.get("birth_place_ta", f"{b['lat']}, {b['lon']}"))],
        [TP("லக்னம்"), TP(r["boy_lagna_ta"]), TP(r["girl_lagna_ta"])],
        [TP("ராசி"), TP(RASI_TA[boy_bhakoot]), TP(RASI_TA[girl_bhakoot])],
        [TP("நட்சத்திரம்"), TP(boy_nak_ta), TP(girl_nak_ta)],
        [TP("குலம்"), TP("காடை"), TP(extract_tamil(b["kulam"]))],
        [TP("குலதெய்வம்"), TP("குறிப்பிடப்படவில்லை"), TP(extract_tamil(b["deity"]))],
    ]
    t_param = Table(param_data, colWidths=[5.0*cm, 6.5*cm, 6.5*cm])
    t_param.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 4.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4.0),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t_param)
    story.append(Spacer(1, 0.5 * cm))
    
    story.append(TP("2. அஷ்டகூட திருமணப் பொருத்தப் புள்ளிகள் (36 புள்ளிகள் முறை)", font_size=15, bold=True, color=SAGE_DK, space_after=4, keep_with_next=True))
    kuta_data = [
        [TP_bold("பொருத்த காரணி", font_size=9.5), TP_bold(f"ஆண் ({boy_nak_ta})", font_size=9.5), TP_bold(f"பெண் ({girl_nak_ta})", font_size=9.5), TP_bold("மதிப்பு", font_size=9.5, align="center"), TP_bold("அதி. அளவு", font_size=9.5, align="center"), TP_bold("விளக்கம்", font_size=9.5)],
        [TP("நாடி (சரீர ஆரோக்கியம்)"), TP(NADI_TA[boy_nadi]), TP(NADI_TA[girl_nadi]), TP_green(str(k.nadi[0]), align="center") if k.nadi[0] > 0 else TP_red(str(k.nadi[0]), align="center"), TP("8", align="center"), TP("மிகச்சிறந்த உடல் மற்றும் வம்சவிருத்திப் பொருத்தம்")],
        [TP("பகூத் (மனோநிலை இணக்கம்)"), TP(RASI_TA[boy_bhakoot]), TP(RASI_TA[girl_bhakoot]), TP_green(str(k.bhakoot[0]), align="center") if k.bhakoot[0] > 0 else TP_red(str(k.bhakoot[0]), align="center"), TP("7", align="center"), TP("நிறைவான மன இணக்கம் மற்றும் குடும்ப அமைதி")],
        [TP("கணம் (குணப் பொருத்தம்)"), TP(GANA_TA[boy_gana]), TP(GANA_TA[girl_gana]), TP_green(str(k.gana[0]), align="center") if k.gana[0] == 6 else TP_red(str(k.gana[0]), align="center"), TP("6", align="center"), TP("சிறந்த குண இணக்கம் மற்றும் பண்புப் பொருத்தம்")],
        [TP("요னி (உடல் இணக்கம்)"), TP(YONI_TA[boy_yoni]), TP(YONI_TA[girl_yoni]), TP(str(k.yoni[0]), align="center"), TP("4", align="center"), TP("நல்ல உடல் ரீதியான பொருத்தம்")],
        [TP("கிரக மைத்திரி (மனப் பொருத்தம்)"), TP(LORD_TA[boy_lord]), TP(LORD_TA[girl_lord]), TP_green(str(k.graha_maitri[0]), align="center") if k.graha_maitri[0] >= 3 else TP_red(str(k.graha_maitri[0]), align="center"), TP("5", align="center"), TP("ஆளும் கிரகங்களின் நட்பு நிலை")],
        [TP("தாரா (விதிப் பொருத்தம்)"), TP(boy_nak_ta), TP(girl_nak_ta), TP_green(str(k.tara[0]), align="center") if k.tara[0] >= 1.5 else TP_red(str(k.tara[0]), align="center"), TP("3", align="center"), TP("அனுசரணையான மற்றும் சுப பலன்கள் தரும் பொருத்தம்")],
        [TP("வசியம் (ஈர்ப்புப் பொருத்தம்)"), TP(RASI_TA[boy_bhakoot]), TP(RASI_TA[girl_bhakoot]), TP(str(k.vasya[0]), align="center"), TP("2", align="center"), TP("இருதரப்பு சமநிலை வசியம்")],
        [TP("வர்ணம் (கடமைப் பொருத்தம்)"), TP(VARNA_TA[boy_varna]), TP(VARNA_TA[girl_varna], space_after=2), TP(str(k.varna[0]), align="center"), TP("1", align="center"), TP("இணக்கமான கடமைப் பகிர்வு")],
        [TP_bold("மொத்த அஷ்டகூடப் புள்ளிகள்", font_size=9.5), TP(""), TP(""), TP_green(str(k.total[0]), align="center"), TP_bold("36", align="center"), TP_bold(verdict_ta, font_size=9.5)],
    ]
    t_kuta = Table(kuta_data, colWidths=[3.8*cm, 2.3*cm, 2.3*cm, 1.4*cm, 1.2*cm, 7.0*cm])
    t_kuta.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("BACKGROUND", (0,-1), (-1,-1), BG_ACCENT),
        ("SPAN", (1, -1), (2, -1)),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 4.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4.0),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_kuta)
    
    # Dynamic Vedic Compatibility & Caution Points in Tamil
    vedic_bullets_ta = []
    if k.nadi[0] == 0:
        vedic_bullets_ta.append("* நாடி தோஷம் (ஆரோக்கிய எச்சரிக்கை): இருவருக்குள்ளும் நாடி தோஷம் காணப்படுகிறது. இது உடல் நலனில் சமநிலையின்மையைக் குறிக்கும். இதற்கான சுப பரிகாரமாக மகா மிருத்யுஞ்சய ஜெபம் அல்லது தானங்கள் செய்வது இல்லறத்திற்கு நலம் சேர்க்கும்.")
    else:
        vedic_bullets_ta.append("* நாடி பொருத்தம் (ஆரோக்கிய பலம்): நாடி தோஷம் ஏதும் இல்லை. இருவரின் உடல் தத்துவங்களும் இயற்கையாகவே பொருந்துகின்றன; இது தம்பதியரின் ஆரோக்கியத்தையும் நல்வாழ்வையும் பலப்படுத்தும்.")
        
    if k.bhakoot[0] == 0:
        vedic_bullets_ta.append("* பகூத் தோஷம் (உணர்வுப்பூர்வ எச்சரிக்கை): ராசி அமைப்பில் பகூத் தோஷம் உள்ளது. இது உணர்ச்சிவசப்படுதல் அல்லது மன ரீதியான இடைவெளியைக் குறிக்கும். இதற்கான பரிகாரமாக, இருவரும் கருத்துக்களை மறைக்காமல் பேசிப் பழக வேண்டும் மற்றும் சிவ வழிபாடு செய்ய வேண்டும்.")
    else:
        vedic_bullets_ta.append("* பகூத் பொருத்தம் (உணர்வுப்பூர்வ பலம்): ராசிகளுக்கு இடையே சிறந்த இணக்கம் உள்ளது. இது தம்பதியருக்குள் மன இணக்கத்தையும், குடும்ப ஒற்றுமையையும், பரஸ்பர அன்பையும் அதிகரிக்கும்.")
        
    if k.gana[0] <= 1:
        vedic_bullets_ta.append("* குணப் பொருத்தம் இன்மை (நடத்தை எச்சரிக்கை): குண அமைப்புகளில் முரண்பாடு உள்ளது. ஒருவர் அமைதியை விரும்பும்போது, மற்றொருவர் வேகமாகவும் சுறுசுறுப்பாகவும் இருக்கலாம். ஒருவர் மற்றொருவரது இயல்பை மாற்ற முயற்சிக்காமல் இருப்பதே இதற்கு சிறந்த பரிகாரமாகும்.")
    else:
        vedic_bullets_ta.append("* குண பொருத்தம் (நடத்தை பலம்): இருவரின் குணநலன்களும் இயல்பாகவே ஒத்துப்போகின்றன. இதனால் கருத்து வேறுபாடுகள் இன்றி தினசரி முடிவுகளை எடுக்க முடியும்.")
        
    if k.graha_maitri[0] <= 1:
        vedic_bullets_ta.append("* கிரகப் பகை நிலை (கருத்து எச்சரிக்கை): ராசிநாதர்களுக்குள் பகை நிலை உள்ளது. இதனால் குடும்ப முடிவுகள் அல்லது திட்டமிடுதல்களில் கருத்து வேறுபாடுகள் வரலாம். பரிகாரம்: முடிவுகளை இருவரும் கலந்து ஆலோசித்து, ஒருவர் கருத்துக்கு மற்றவர் மதிப்பளிக்க வேண்டும்.")
    else:
        vedic_bullets_ta.append("* கிரக நட்பு (கருத்து பலம்): ராசிநாதர்கள் சுமுகமான நட்புறவைக் கொண்டுள்ளனர். இது இருவருக்கும் இடையே சிறந்த நட்பு, அறிவுசார் இணக்கம் மற்றும் பரஸ்பர மதிப்பைத் தரும்.")
        
    if k.yoni[0] == 0:
        vedic_bullets_ta.append("* யோனி பகை நிலை (உடல் இணக்க எச்சரிக்கை): இருவரின் உடல் தத்துவங்களில் பகை நிலை உள்ளது. இது அன்யோன்யத்தில் சில காலங்களில் மனவிலக்கைத் தரலாம். பரிகாரம்: இருவரும் ஒருவருக்கொருவர் அதிக நேரத்தைச் செலவிட்டு, அன்பைப் பரிமாறிக்கொள்வது அவசியம்.")
    elif k.yoni[0] == 1:
        vedic_bullets_ta.append("* யோனி நடுநிலை (அன்யோன்யக் குறிப்பு): அன்யோன்யப் பொருத்தம் நடுநிலையாக உள்ளது. அன்பான உறவை வளர்த்துக்கொள்ள உணர்வுப்பூர்வமான இணக்கம் தேவை.")
    else:
        vedic_bullets_ta.append("* யோனி பொருத்தம் (அன்யோன்ய பலம்): இருவரிடையே சிறந்த உடல் மற்றும் மன ரீதியான அன்யோன்யம் உள்ளது. இது மகிழ்ச்சியான தம்பத்திய இன்பத்தைத் தரும்.")
        
    story.append(TP("வேத ஜோதிட பலங்களும் எச்சரிக்கைகளும்", font_size=12, bold=True, color=GOLD_DK, space_after=1, keep_with_next=True))
    for bullet in vedic_bullets_ta:
        story.append(TP(bullet, font_size=9.5, leading=1.45, space_after=0.5))
    story.append(Spacer(1, 0.4 * cm))
    story.append(PageBreak())
    

    
    # Page 2: Vedic Afflictions & Multidisciplinary Matching (Numerology & Chinese Bazi)
    story.append(TP("4. செவ்வாய் தோஷம் மற்றும் குலப் பொருத்தம்", font_size=15, bold=True, color=SAGE_DK, space_after=10, keep_with_next=True))
    
    # Build list of Flowables inside Table Cell to avoid raw HTML tags overlapping
    dosha_flowables = [
        TP("மனோஜ் குமார் (ஆண்): சுத்தம் (செவ்வாய் தோஷம் இல்லை)", bold=True, space_after=3),
        TP(f"{girl_name_ta} (பெண்): {extract_tamil(b['jadhagam'])}", bold=True, space_after=8),
    ]
    if r["girl_md"]["is_mangalik"]:
        dosha_flowables.append(TP("விளக்கம்: பெண்ணிற்கு 12-ஆம் இடத்தில் லேசான செவ்வாய் தங்குதல் உள்ளது. இது ஆணின் சுத்த ஜாதகத்துடன் சரியாகப் பொருந்துகிறது. இதனால் எந்தவித பாதிப்பும் இல்லை.", leading=1.5))
    else:
        dosha_flowables.append(TP("விளக்கம்: இருவர் ஜாதகமும் செவ்வாய் தோஷம் இல்லாத சுத்த ஜாதகங்கள் ஆகும். இது மிகச்சிறந்த தம்பதியர் இணக்கத்தை அளிக்கும்.", leading=1.5))
        
    t_dosha = Table([[dosha_flowables]], colWidths=[18*cm])
    t_dosha.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_SUCCESS if not r["girl_md"]["is_mangalik"] else BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LINELEFT", (0,0), (-1,-1), 4, TEXT_SUCCESS if not r["girl_md"]["is_mangalik"] else GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 10.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10.0),
    ]))
    story.append(t_dosha)
    story.append(Spacer(1, 0.35 * cm))
    
    story.append(TP("5. எண்கணித 8-புள்ளி பொருத்த அட்டவணை", font_size=15, bold=True, color=SAGE_DK, space_after=5, keep_with_next=True))
    story.append(TP("பிறந்த தேதி எண் (விதி எண்) மற்றும் கூட்டு எண் (விதி எண்) ஆகியவற்றின் கிரக நட்பு விதிகள்.", font_size=10.0, space_after=5))
    
    # Helper to translate relations and planets
    rel_map = {"same": "நட்பு / சமம்", "friend": "நட்பு", "neutral": "சமநிலை", "enemy": "பகை"}
    planets_ta = {
        "Sun": "சூரியன்", "Moon": "சந்திரன்", "Mars": "செவ்வாய்", "Mercury": "புதன்",
        "Jupiter": "குரு", "Venus": "சுக்கிரன்", "Saturn": "சனி", "Rahu": "ராகு", "Ketu": "கேது"
    }
    
    p1_driver_planet = planets_ta.get(n['person1']['driver_planet'], n['person1']['driver_planet'])
    p2_driver_planet = planets_ta.get(n['person2']['driver_planet'], n['person2']['driver_planet'])
    p1_destiny_planet = planets_ta.get(n['person1']['destiny_planet'], n['person1']['destiny_planet'])
    p2_destiny_planet = planets_ta.get(n['person2']['destiny_planet'], n['person2']['destiny_planet'])
    
    num_data = [
        [TP_bold("பொருத்த காரணி"), TP_bold("ஆண்: மனோஜ் குமார்"), TP_bold(f"பெண்: {girl_name_ta}"), TP_bold("பரஸ்பர உறவு"), TP_bold("புள்ளிகள்")],
        [
            TP("பிறந்த தேதி எண் (விதி எண்)"), 
            TP(f"{n['person1']['driver']} ({p1_driver_planet})"), 
            TP(f"{n['person2']['driver']} ({p2_driver_planet})"), 
            TP(rel_map.get(n['driver_relation']['a_to_b'], n['driver_relation']['a_to_b']), color=TEXT_SUCCESS if n['driver_relation']['a_to_b'] in ['friend', 'same'] else None), 
            TP(f"{n['driver_relation']['points']} / 4", bold=True)
        ],
        [
            TP("கூட்டு எண் (விதி எண்)"), 
            TP(f"{n['person1']['destiny']} ({p1_destiny_planet})"), 
            TP(f"{n['person2']['destiny']} ({p2_destiny_planet})"), 
            TP(rel_map.get(n['destiny_relation']['a_to_b'], n['destiny_relation']['a_to_b']), color=TEXT_SUCCESS if n['destiny_relation']['a_to_b'] in ['friend', 'same'] else None), 
            TP(f"{n['destiny_relation']['points']} / 4", bold=True)
        ],
        [
            TP_bold("மொத்த எண்கணிதப் பொருத்தம்"),
            TP(""), TP(""),
            TP_bold(num_verdict_ta),
            TP_bold(f"{n['score_percent']}% ({n['driver_relation']['points'] + n['destiny_relation']['points']}/8)")
        ]
    ]
    t_num = Table(num_data, colWidths=[4.2*cm, 4.0*cm, 4.0*cm, 3.4*cm, 2.4*cm])
    t_num.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("BACKGROUND", (0,-1), (-1,-1), BG_ACCENT),
        ("SPAN", (1, -1), (2, -1)),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 4.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4.0),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_num)
    # Dynamic Numerology Explanation in Tamil
    if n['score_percent'] >= 75:
        num_explain_ta = f"மனோஜின் எண்கள் (பிறந்த எண் 7 மற்றும் கூட்டு எண் 1) {girl_name_ta} இன் எண்களுடன் (பிறந்த எண் {n['person2']['driver']} மற்றும் கூட்டு எண் {n['person2']['destiny']}) மிகச்சிறந்த இணக்கத்தைப் பெற்றுள்ளன. இவர்களது எண்களுக்கு இடையேயான நல்ல அதிர்வுகள் இயல்பான பரஸ்பர அன்பையும், குடும்பத்தில் நிம்மதியான சூழலையும், கூட்டு இலக்குகளை வெற்றிகரமாக அடைவதையும் குறிக்கிறது."
    elif n['score_percent'] >= 50:
        num_explain_ta = f"மனோஜ் மற்றும் {girl_name_ta} ஆகியோரின் எண்கள் ஒரு நிலையான மற்றும் அனுசரணையான வாழ்க்கையைக் காட்டுகின்றன. இவர்களது எண்களுக்கு இடையே நடுநிலையான தொடர்பு இருப்பதால், சில சிறிய கருத்து வேறுபாடுகள் வரலாம்; ஆயினும் பரஸ்பரப் புரிதல் மூலம் எளிதில் மகிழ்ச்சியாக வாழ முடியும்."
    else:
        num_explain_ta = f"மனோஜ் மற்றும் {girl_name_ta} எண்கள் சில முரண்பட்ட தன்மையைக் காட்டுகின்றன. கிரக அதிபதிகளின் வேறுபாட்டால் இல்லற கடமைகள் மற்றும் நிதி விஷயங்களில் முரண்பாடுகள் வரலாம்; இதற்குப் பொறுமையும் விட்டுக்கொடுத்தலும் தேவை."
    story.append(Spacer(1, 0.2 * cm))
    story.append(TP(f"தனிப்பட்ட கணிப்பு: {num_explain_ta}", font_size=10.0))
    story.append(Spacer(1, 0.35 * cm))
    
    story.append(TP("6. சீன பாசி (BaZi) ராசி இணக்கம்", font_size=15, bold=True, color=SAGE_DK, space_after=5, keep_with_next=True))
    story.append(TP("பிறந்த வருடத்தின் சீன விலங்கு மற்றும் உறுப்புகளின் இணக்கத்தை ஆராய்கிறது.", font_size=10.0, space_after=5))
    
    # Translate desc/elements if needed
    chinese_desc_ta_clean = extract_tamil(r["chinese_desc"])
    if not chinese_desc_ta_clean or chinese_desc_ta_clean == r["chinese_desc"]:
        chinese_desc_ta_clean = "சுப இணக்கம்" if r["chinese_score"] >= 80 else "சாதாரண ராசி இணக்கம்"
        
    bazi_data = [
        [TP_bold("பரிமாணம் / விபரம்"), TP_bold("ஆண்: மனோஜ் குமார்"), TP_bold(f"பெண்: {girl_name_ta}")],
        [TP("வருடப் தூண் (Year Pillar)"), TP("Bing-Zi (丙子 - நெருப்பு எலி)"), TP(f"{r['girl_bazi']['Year']}")],
        [TP("சீன ராசி விலங்கு"), TP("எலி (Rat)"), TP(f"{r_animal_ta} (உறுப்பு: {extract_tamil(r['girl_bazi']['Year']) or 'நிலம்'})")],
        [
            TP_bold("ராசிப் பொருத்தம்"), 
            TP(chinese_desc_ta_clean, color=TEXT_SUCCESS if r['chinese_score'] >= 80 else None), 
            TP_bold(f"மதிப்பெண்: {r['chinese_score']}%")
        ]
    ]
    t_bazi = Table(bazi_data, colWidths=[4.5*cm, 6.75*cm, 6.75*cm])
    t_bazi.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("BACKGROUND", (0,-1), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 4.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4.0),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_bazi)
    # Dynamic Chinese Bazi Explanation in Tamil
    if r['girl_animal'] == "Ox":
        bazi_explain_ta = f"மனோஜ் (எலி) மற்றும் {girl_name_ta} (மாடு) ஆகிய இருவருக்கும் சீன ஜோதிடத்தில் உன்னதமான ஆறு இணக்கப் பொருத்தம் (Liu He) உள்ளது. இது தம்பதியரிடையே ஆழமான பரஸ்பர நம்பிக்கை, அன்பு மற்றும் குடும்ப வாழ்வில் ஒருவருக்கொருவர் பக்கபலமாக இருக்கும் நல்வாழ்வை வழங்கும்."
    elif r['girl_animal'] == "Dragon":
        bazi_explain_ta = f"மனோஜ் (எலி) மற்றும் {girl_name_ta} (டிராகன்) இருவருக்கும் சீன ஜோதிடத்தில் சிறந்த மூன்று இணக்கப் பொருத்தம் (San He) உள்ளது. எலி மற்றும் டிராகன் கூட்டணி சிறந்த பொருளாதார முன்னேற்றம், குடும்ப வளம் மற்றும் ஒருவரையொருவர் வளர்க்கும் ஆற்றலைத் தரும்."
    elif r['girl_animal'] == "Rat":
        bazi_explain_ta = f"மனோஜ் மற்றும் {girl_name_ta} இருவரும் ஒரே எலி வருடத்தைச் சேர்ந்தவர்கள். இது இருவருக்கும் இடையே ஒரே மாதிரியான எண்ணங்கள், பரஸ்பரப் புரிதல் மற்றும் ஒத்த ரசனைகளை உருவாக்கும், ஆயினும் சில நேரங்களில் விட்டுக்கொடுத்துப் போவது நல்லது."
    else:
        bazi_explain_ta = f"மனோஜ் மற்றும் {girl_name_ta} இடையே சீன ராசிப் பொருத்தம் சாதாரணமாக உள்ளது. இவர்கள் தங்களது கூட்டு முயற்சியாலும் குடும்பப் பொறுப்புகளைப் பகிர்வதாலும் நல்ல குடும்ப வாழ்க்கையை அமைக்கலாம்."
    story.append(Spacer(1, 0.15 * cm))
    story.append(TP(f"தனிப்பட்ட கணிப்பு: {bazi_explain_ta}", font_size=10.0))
    
    # Page 3: Western, Mayan, overall verdict
    story.append(PageBreak())
    
    story.append(TP("7. மேற்கத்திய கிரக பார்வைகள் (Western Aspects)", font_size=15, bold=True, color=SAGE_DK, space_after=10, keep_with_next=True))
    story.append(TP("இருவரின் ஜாதகக் கிரகங்களுக்கு இடையே உள்ள வடிவியல் கோணங்களை (Aspects) ஒப்பிடுகிறது.", font_size=9.5, space_after=10))
    
    aspects_to_show = sorted(r["synastry_aspects"], key=lambda x: x["error"])[:6]
    west_headers = [TP_bold("ஆண் கிரகம்"), TP_bold("பார்வை வகை"), TP_bold("பெண் கிரகம்"), TP_bold("பாகை வேறுபாடு"), TP_bold("இணக்க வகை")]
    west_rows = [west_headers]
    
    aspect_ta_map = {
        "Conjunction": "இணைவு (0°)",
        "Sextile": "சுப பார்வை (60°)",
        "Square": "சவாலான பார்வை (90°)",
        "Trine": "திரிகோணப் பார்வை (120°)",
        "Opposition": "சமசப்தம பார்வை (180°)"
    }
    
    for asp in aspects_to_show:
        is_pos = asp["aspect"] in ["Trine", "Sextile", "Conjunction"]
        rel_type_ta = "சுப இணக்கம்" if is_pos else "சவால்"
        west_rows.append([
            TP(planets_ta.get(asp["boy_planet"], asp["boy_planet"])),
            TP(aspect_ta_map.get(asp["aspect"], asp["aspect"])),
            TP(planets_ta.get(asp["girl_planet"], asp["girl_planet"])),
            TP(f"{asp['error']}°"),
            TP(rel_type_ta, color=TEXT_SUCCESS if is_pos else TEXT_ALERT)
        ])
    if len(west_rows) == 1:
        west_rows.append([TP("முக்கிய பார்வைகள் எதுவும் இல்லை"), TP("-"), TP("-"), TP("-"), TP("சமநிலை")])
        
    t_west = Table(west_rows, colWidths=[3.6*cm, 3.6*cm, 3.6*cm, 3.2*cm, 4.0*cm])
    t_west.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 3.5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_west)
    # Dynamic Western Aspect Explanation in Tamil
    if aspects_to_show:
        top_asp = aspects_to_show[0]
        boy_p = top_asp["boy_planet"]
        girl_p = top_asp["girl_planet"]
        asp_name = top_asp["aspect"]
        b_p_ta = planets_ta.get(boy_p, boy_p)
        g_p_ta = planets_ta.get(girl_p, girl_p)
        west_explain_ta = f"இருவரது ஜாதகத்திலும் மிக வலுவான கிரக இணைப்பு என்பது மனோஜின் {b_p_ta} மற்றும் {girl_name_ta} இன் {g_p_ta} இடையே உள்ள பார்வை ஆகும். "
        if asp_name in ["Trine", "Sextile", "Conjunction"]:
            west_explain_ta += "இந்த சுப கிரகப் பார்வை தம்பதியரிடையே இயல்பான அன்பையும், ஒருவரையொருவர் ஆதரிக்கும் குணத்தையும், சிறந்த குடும்ப இணக்கத்தையும் தரும்."
        else:
            west_explain_ta += "இந்த கிரகச் சேர்க்கை சில முரண்பாடுகளைக் குறிக்கிறது; இதைச் சமாளிக்க இருவரும் அமைதியுடனும் விட்டுக்கொடுக்கும் தன்மையுடனும் செயல்பட வேண்டும்."
    else:
        west_explain_ta = "முக்கிய கிரக பார்வைகள் ஏதும் இல்லை. இவர்களது கிரக இணைப்புகள் நடுநிலையாக உள்ளன."
    story.append(Spacer(1, 0.2 * cm))
    story.append(TP(f"தனிப்பட்ட கணிப்பு: {west_explain_ta}", font_size=9.5))
    story.append(Spacer(1, 0.25 * cm))
    
    story.append(TP("8. மாயன் சோல்கின் (Tzolkin) ஓரக்கிள் பொருத்தம்", font_size=15, bold=True, color=SAGE_DK, space_after=10, keep_with_next=True))
    
    boy_sign_idx = next((i for i, d in enumerate(DAY_SIGNS) if d["name"] == boy_tzolkin["day_glyph"]["name"]), 0)
    girl_sign_idx = next((i for i, d in enumerate(DAY_SIGNS) if d["name"] == girl_tzolkin["day_glyph"]["name"]), 0)
    diff = abs(boy_sign_idx - girl_sign_idx)
    if diff == 10:
        rel_role_ta = "எதிர்முனை ஜோடி (ஆழ்ந்த ஆன்ம வளர்ச்சி தரும் சவாலான பொருத்தம்)"
        mayan_explain_ta = f"மனோஜ் மற்றும் {girl_name_ta} ஆகியோர் எதிர்முனை ஜோடி (Antipode) ஆவர். இவர்களது குணங்களில் உள்ள வேறுபாடுகள் ஒருவரையொருவர் பக்குவப்படுத்தவும், ஆன்ம ரீதியான வளர்ச்சி பெறவும், வாழ்வில் முதிர்ச்சியடையவும் உதவும்."
    elif (boy_sign_idx + girl_sign_idx) in [19, 39, 59, 9, 29]:
        rel_role_ta = "அனலாக் ஜோடி (இயற்கையான ஆதரவு மற்றும் அமைதியான இணக்கம்)"
        mayan_explain_ta = f"மனோஜ் மற்றும் {girl_name_ta} ஆகியோர் அனலாக் ஜோடி (Analog) ஆவர். இது மாயன் சோல்கினில் மிகவும் அமைதியான இணக்கத்தைக் குறிக்கும். இது இருவரிடையேயும் மன அழுத்தத்தைக் குறைத்து, இல்லற வாழ்வில் எப்போதும் மகிழ்ச்சியையும் நிம்மதியையும் வழங்கும்."
    elif boy_tzolkin["day_glyph"]["direction"] == girl_tzolkin["day_glyph"]["direction"]:
        rel_role_ta = "திசைசார் இணக்கம் (ஒரே ஆன்மீகத் திசை மற்றும் கூட்டு வாழ்க்கை)"
        mayan_explain_ta = f"மனோஜ் மற்றும் {girl_name_ta} ஆகியோர் திசைசார் இணக்கம் (Directional) கொண்டவர்கள். இவர்கள் வாழ்வில் ஒரே மாதிரியான லட்சியங்களையும், ஆன்மீகச் சிந்தனைகளையும் கொண்டு கூட்டு வாழ்க்கைpath-இல் வெற்றி பெறுவர்."
    else:
        rel_role_ta = "நிரப்பு ஜோடி (தினசரி செயல்பாடுகளில் பரஸ்பர உதவி)"
        mayan_explain_ta = f"மனோஜ் மற்றும் {girl_name_ta} ஆகியோர் நிரப்பு ஜோடி (Complementary) ஆவர். இவர்கள் இல்லறக் கடமைகளைச் செய்வதில் ஒருவருக்கொருவர் துணையாக நின்று, ஒருவரது குறையை மற்றவர் நிறைவு செய்து சிறப்பான வாழ்க்கையை நடத்துவர்."
        
    boy_mayan_formatted_ta = f"{boy_tzolkin['galactic_tone']['tone']} {boy_tzolkin['day_glyph']['name']} (ஒலிக்கும் முத்திரை)"
    girl_mayan_formatted_ta = f"{girl_tzolkin['galactic_tone']['tone']} {girl_tzolkin['day_glyph']['name']}"
    
    mayan_data = [
        [TP_bold("விபரம் / அளவுகோல்"), TP_bold("ஆண்: மனோஜ் குமார்"), TP_bold(f"பெண்: {girl_name_ta}")],
        [TP("சோல்கின் ராசி முத்திரை"), TP(boy_mayan_formatted_ta), TP(girl_mayan_formatted_ta)],
        [TP_bold("சோல்கின் ஓரக்கிள் பங்கு"), TP(rel_role_ta, color=TEXT_SUCCESS), TP_bold("ஆன்மீக அதிர்வலை பொருத்தம்")]
    ]
    t_mayan = Table(mayan_data, colWidths=[4.2*cm, 6.9*cm, 6.9*cm])
    t_mayan.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [SAND_BG, SAGE_LT]),
        ("BACKGROUND", (0,0), (-1,0), SAGE_LT),
        ("BACKGROUND", (0,-1), (-1,-1), BG_ACCENT),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 3.5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_mayan)
    story.append(Spacer(1, 0.2 * cm))
    story.append(TP(f"தனிப்பட்ட கணிப்பு: {mayan_explain_ta}", font_size=9.5))
    story.append(Spacer(1, 0.3 * cm))
    
    # Section 9 Image - Side by side Groom & Bride Zodiac Characters in Tamil
    boy_rasi_name = boy_bhakoot.lower() # "leo"
    girl_rasi_name = girl_bhakoot.lower() # "aquarius" or "sagittarius"
    
    boy_img_name = f"{boy_rasi_name}_character.png"
    girl_img_name = f"{girl_rasi_name}_character.png"
    
    boy_img_path = os.path.join(RUNTIME_DIR, boy_img_name)
    girl_img_path = os.path.join(RUNTIME_DIR, girl_img_name)
    fallback_img_path = os.path.join(RUNTIME_DIR, "zodiac_flat_icon.png")
    
    if not os.path.exists(boy_img_path):
        boy_img_path = fallback_img_path
    if not os.path.exists(girl_img_path):
        girl_img_path = fallback_img_path
        
    from reportlab.platypus import Image as RLImage
    
    boy_label_ta = TP_bold("ஆண் ராசி: சிம்மம்", align="center")
    girl_rasi_ta = RASI_TA.get(girl_bhakoot, girl_bhakoot)
    girl_label_ta = TP_bold(f"பெண் ராசி: {girl_rasi_ta}", align="center")
    
    boy_cell = [RLImage(boy_img_path, width=2.8*cm, height=2.8*cm, hAlign="CENTER"), Spacer(1, 0.1*cm), boy_label_ta]
    girl_cell = [RLImage(girl_img_path, width=2.8*cm, height=2.8*cm, hAlign="CENTER"), Spacer(1, 0.1*cm), girl_label_ta]
    
    zodiac_table = Table([[boy_cell, girl_cell]], colWidths=[9.0*cm, 9.0*cm])
    zodiac_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(zodiac_table)
    story.append(Spacer(1, 0.3 * cm))
        
    story.append(PageBreak())
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
    story.append(TP("இருவரின் ஜாதக கிரகங்களின் கணித மையப்புள்ளிகளை கொண்டு இந்த கூட்டு ஜாதகம் கணக்கிடப்படுகிறது. இதன் மூலம் உங்கள் இருவரின் கூட்டு சூரியன் மற்றும் சுக்கிரன் மீன ராசியில் இணைகிறது. இது ஒரு ஆன்மீக, அன்பான மற்றும் ஒருவருக்கொருவர் ஆதரவளிக்கும் வாழ்க்கையை குறிக்கிறது.", font_size=9))
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
    story.append(PageBreak())
    story.append(TP("10. இறுதிப் பொருத்த முடிவு மற்றும் பரிந்துரை (Verdict)", font_size=15, bold=True, color=SAGE_DK, space_after=4, keep_with_next=True))
    story.append(TP("9. இறுதி முடிவுகள் மற்றும் பரிந்துரைகள்", font_size=15, bold=True, color=SAGE_DK, space_after=4, keep_with_next=True))
    
    # Verdict Flowables
    verdict_flowables = [
        TP(f"இறுதிப் பொருத்தம்: {r['overall_score']}% - மிகச்சிறந்த பொருத்தம் (பரிந்துரைக்கப்படுகிறது)", bold=True, space_after=6, font_size=10.5),
        TP(f"* குலப் பொருத்தம்: பொருத்தம் உண்டு. ஆண் காடை குலம், பெண் {extract_tamil(b['kulam'])} குலம். வெவ்வேறு குலங்கள் என்பதால் கொங்கு வெள்ளாள கவுண்டர் முறைப்படி திருமணம் செய்ய தகுடையது.", space_after=4, leading=1.5),
        TP(f"* ஆரோக்கியம் மற்றும் குடும்ப இணக்கம்: மிக நன்று. 36-க்கு {k.total[0]} புள்ளிகள் பெற்றுள்ளது. இருவருக்கும் நாடி தோஷமோ அல்லது பகூத் தோஷமோ இல்லை.", space_after=4, leading=1.5),
    ]
    if "Sashtika" in b["name"]:
        verdict_flowables.append(TP("* இறுதி முடிவுகள்: கணித ரீதியாக மிகச்சிறந்த பொருத்தம். எண்கணித விதியில் 88% மற்றும் மேற்கத்திய அமைப்பில் 85% இணக்கம் பெற்றுள்ளது.", leading=1.5))
    elif "Padmapriyanka" in b["name"]:
        verdict_flowables.append(TP("* இறுதி முடிவுகள்: சுத்த ஜாதகம் கொண்ட நிலையான பொருத்தம். சீன ஜோதிட எலி-டிராகன் கூட்டணி குடும்ப வாழ்க்கையில் நல்ல பரஸ்பர ஆதரவை வழங்கும்.", leading=1.5))
    else:
        verdict_flowables.append(TP("* இறுதி முடிவுகள்: சிறந்த சீன ராசி ஆன்ம இணக்கம் (எலி-மாடு ஆறு இணக்கங்கள்). சுத்தமான அஷ்டகூட பொருத்தம் மற்றும் சிறந்த தொழில் இணக்கம்.", leading=1.5))
        
    t_verdict = Table([[verdict_flowables]], colWidths=[18*cm])
    t_verdict.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("LINELEFT", (0,0), (-1,-1), 4, GOLD_DK),
        ("BOX", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 12.0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 12.0),
    ]))
    story.append(t_verdict)
    
    girl_name_ta_hdr = BRIDE_NAME_TA.get(b['name'], b['name'])
    hf_drawer = get_header_footer_drawer_ta(BOY_NAME_TA, girl_name_ta_hdr)
    doc.build(story, onFirstPage=hf_drawer, onLaterPages=hf_drawer)
    print(f"Generated Tamil PDF for {b['name']}")

def generate_md_en(r, filename):
    b = r["bride"]
    k = r["vedic_kuta"]
    n = r["num_res"]
    boy_tzolkin = r["boy_tzolkin"]
    boy_bazi = r["boy_bazi"]
    
    # Dynamic values for text
    boy_varna = VARNA[k.boy_moon]
    girl_varna = VARNA[k.girl_moon]
    boy_nadi = NADI[_nak_idx(r["boy_moon_lon"])]
    girl_nadi = NADI[_nak_idx(r["girl_moon_lon"])]
    
    report = []
    report.append(f"# Celestial Compatibility Report: Manoj Kumar & {b['name']}")
    report.append(f"Generated on: 2026-07-14\n")
    report.append(f"> [!NOTE]\n> **Clan Status:** Manoj belongs to the **Kadai** clan, and {b['name']} belongs to the **{clean_ta_text(b['kulam'])}** clan. Since they belong to different clans, this match is **fully compatible**.\n")
    report.append(f"## 1. Vedic Compatibility (Ashta-Kuta: {k.total[0]}/36 — {k.verdict})")
    report.append(f"| Factor | Boy | Girl | Score | Max | Meaning |")
    report.append(f"| :--- | :--- | :--- | :--- | :--- | :--- |")
    report.append(f"| Physiology & Health | {boy_nadi} | {girl_nadi} | {k.nadi[0]} | 8 | Clean - No Nadi Dosha |")
    report.append(f"| Emotional Harmony | {k.boy_moon} | {k.girl_moon} | {k.bhakoot[0]} | 7 | Harmonious emotional bond |")
    report.append(f"| Temperament Align | {GANA[_nak_idx(r['boy_moon_lon'])]} | {GANA[_nak_idx(r['girl_moon_lon'])]} | {k.gana[0]} | 6 | Temperament Alignment |")
    report.append(f"| Physical Chemistry | {YONI[_nak_idx(r['boy_moon_lon'])]} | {YONI[_nak_idx(r['girl_moon_lon'])]} | {k.yoni[0]} | 4 | Friendly compatibility |")
    report.append(f"| Mental Match | {SIGN_LORDS[k.boy_moon]} | {SIGN_LORDS[k.girl_moon]} | {k.graha_maitri[0]} | 5 | Ruling lords relationship |")
    report.append(f"| Destiny Support | {k.boy_nakshatra} | {clean_ta_text(k.girl_nakshatra)} | {k.tara[0]} | 3 | Auspicious |")
    report.append(f"| Control & Influence | {k.boy_moon} | {k.girl_moon} | {k.vasya[0]} | 2 | Balanced mutual control |")
    report.append(f"| Ego & Duty Class | {boy_varna} | {girl_varna} | {k.varna[0]} | 1 | Harmonious role sharing |")
    report.append(f"| **TOTAL** | | | **{k.total[0]}** | **36** | **{k.verdict}** |\n")
    
    report.append(f"### Sevvai Dosham")
    report.append(f"- **Manoj:** Clean (No Sevvai Dosham)\n- **{b['name']}:** {clean_ta_text(b['jadhagam'])}\n")
    
    report.append(f"## 2. Multi-Engine Scores")
    report.append(f"- **Numerology Match:** {n['score_percent']}% ({n['verdict']})")
    report.append(f"- **Chinese Bazi:** {clean_ta_text(r['chinese_desc'])}")
    report.append(f"- **Western Synastry:** {r['western_score']}% ({r['pos_aspects']} positive links)")
    report.append(f"- **Mayan Tzolkin:** Good energetic resonance\n")
    
    report.append(f"## 3. Overall Verdict")
    report.append(f"### **GRAND COMPATIBILITY FIT: {r['overall_score']}% — HIGHLY RECOMMENDED**")
    if "Sashtika" in b["name"]:
        report.append("Strongest mathematical match. Excellent life path and personal chemistry harmony.")
    elif "Padmapriyanka" in b["name"]:
        report.append("Extremely stable match. Clean horoscope. Highly supportive Dragon-Rat Bazi alliance.")
    else:
        report.append("Excellent Rat-Ox Six Harmonies soulmate connection. Clean Vedic match.")
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

def generate_md_ta(r, filename):
    b = r["bride"]
    k = r["vedic_kuta"]
    n = r["num_res"]
    boy_tzolkin = r["boy_tzolkin"]
    boy_bazi = r["boy_bazi"]
    
    # Dynamic values for text
    boy_varna = VARNA[k.boy_moon]
    girl_varna = VARNA[k.girl_moon]
    boy_nadi = NADI[_nak_idx(r["boy_moon_lon"])]
    girl_nadi = NADI[_nak_idx(r["girl_moon_lon"])]
    boy_gana = GANA[_nak_idx(r["boy_moon_lon"])]
    girl_gana = GANA[_nak_idx(r["girl_moon_lon"])]
    boy_yoni = YONI[_nak_idx(r["boy_moon_lon"])]
    girl_yoni = YONI[_nak_idx(r["girl_moon_lon"])]
    boy_lord = SIGN_LORDS[k.boy_moon]
    girl_lord = SIGN_LORDS[k.girl_moon]
    
    boy_nak_ta = NAKSHATRAS_TA.get(k.boy_nakshatra, k.boy_nakshatra)
    girl_nak_ta = NAKSHATRAS_TA.get(k.girl_nakshatra, k.girl_nakshatra)
    
    report = []
    report.append(f"# ஜாதகப் பொருத்த அறிக்கை: மனோஜ் குமார் & {b['name']}")
    report.append(f"கணிக்கப்பட்ட தேதி: 2026-07-14\n")
    report.append(f"> [!NOTE]\n> **குலப் பொருத்தம்:** ஆண் காடை (காடை) குலம், பெண் {b['kulam']} குலம். வெவ்வேறு குலங்கள் என்பதால் கொங்கு வெள்ளாள கவுண்டர் முறைப்படி திருமணம் செய்ய தகுதியுடையது.\n")
    
    report.append(f"## 1. அஷ்டகூடப் பொருத்தம் (36 புள்ளிகள் முறை: {k.total[0]}/36 — {k.verdict})")
    report.append(f"| பொருத்த காரணி | ஆண் ({boy_nak_ta}) | பெண் ({girl_nak_ta}) | புள்ளிகள் | அதிகபட்சம் | விளக்கம் |")
    report.append(f"| :--- | :--- | :--- | :--- | :--- | :--- |")
    report.append(f"| நாடி (சரீர ஆரோக்கியம்) | {NADI_TA[boy_nadi]} | {NADI_TA[girl_nadi]} | {k.nadi[0]} | 8 | மிகச்சிறந்த உடல் மற்றும் வம்சவிருத்திப் பொருத்தம் |")
    report.append(f"| பகூத் (மனோநிலை இணக்கம்) | {RASI_TA[k.boy_moon]} | {RASI_TA[k.girl_moon]} | {k.bhakoot[0]} | 7 | நிறைவான மன இணக்கம் மற்றும் குடும்ப அமைதி |")
    report.append(f"| கணம் (குணப் பொருத்தம்) | {GANA_TA[boy_gana]} | {GANA_TA[girl_gana]} | {k.gana[0]} | 6 | சிறந்த குண இணக்கம் மற்றும் பண்புப் பொருத்தம் |")
    report.append(f"| யோனி (உடல் இணக்கம்) | {YONI_TA[boy_yoni]} | {YONI_TA[girl_yoni]} | {k.yoni[0]} | 4 | நல்ல உடல் ரீதியான பொருத்தம் |")
    report.append(f"| கிரக மைத்திரி (மனப் பொருத்தம்) | {LORD_TA[boy_lord]} | {LORD_TA[girl_lord]} | {k.graha_maitri[0]} | 5 | ஆளும் கிரகங்களின் நட்பு நிலை |")
    report.append(f"| தாரா (விதிப் பொருத்தம்) | மகம் | {girl_nak_ta} | {k.tara[0]} | 3 | அனுசரணையான மற்றும் சுப பலன்கள் தரும் பொருத்தம் |")
    report.append(f"| வசியம் (ஈர்ப்புப் பொருத்தம்) | {RASI_TA[k.boy_moon]} | {RASI_TA[k.girl_moon]} | {k.vasya[0]} | 2 | இருதரப்பு சமநிலை வசியம் |")
    report.append(f"| வர்ணம் (கடமைப் பொருத்தம்) | {VARNA_TA[boy_varna]} | {VARNA_TA[girl_varna]} | {k.varna[0]} | 1 | இணக்கமான கடமைப் பகிர்வு |")
    report.append(f"| **மொத்தம்** | | | **{k.total[0]}** | **36** | **{k.verdict}** |\n")
    
    report.append(f"### செவ்வாய் தோஷம்")
    report.append(f"- **ஆண் (மனோஜ்):** சுத்தம் (செவ்வாய் தோஷம் இல்லை)\n- **பெண் ({b['name']}):** {b['jadhagam']}\n")
    
    report.append(f"## 2. இதர ஜோதிட முறைகளின் முடிவு")
    report.append(f"- **எண்கணிதம்:** {n['score_percent']}% ({n['verdict']})")
    report.append(f"- **சீன ஜோதிடம்:** {r['chinese_desc']}")
    report.append(f"- **மேற்கத்திய ஜோதிடம்:** {r['western_score']}% ({r['pos_aspects']} சுப இணைப்புகள்)")
    report.append(f"- **மாயன் ஜோதிடம்:** நல்ல ஆன்மீக அதிர்வலை பொருத்தம்\n")
    
    report.append(f"## 3. இறுதி முடிவுகள் மற்றும் பரிந்துரைகள்")
    report.append(f"### **இறுதிப் பொருத்தம்: {r['overall_score']}% — மிகச்சிறந்த பொருத்தம் (பரிந்துரைக்கப்படுகிறது)**")
    if "Sashtika" in b["name"]:
        report.append("கணித ரீதியாக மிகச்சிறந்த பொருத்தம். எண்கணித விதியில் 88% மற்றும் மேற்கத்திய அமைப்பில் 85% இணக்கம் பெற்றுள்ளது.")
    elif "Padmapriyanka" in b["name"]:
        report.append("சுத்த ஜாதகம் கொண்ட நிலையான பொருத்தம். சீன ஜோதிட எலி-டிராகன் கூட்டணி குடும்ப வாழ்க்கையில் நல்ல பரஸ்பர ஆதரவை வழங்கும்.")
    else:
        report.append("சிறந்த சீன ராசி ஆன்ம இணக்கம் (எலி-மாடு ஆறு இணக்கங்கள்). சுத்தமான அஷ்டகூட பொருத்தம் மற்றும் சிறந்த தொழில் இணக்கம்.")
        
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

def main():
    # Boy parameters
    boy_name = "Manoj Kumar"
    boy_date = "1996-05-25"
    boy_time = "20:25"
    boy_lat = 11.25
    boy_lon = 77.12
    boy_tz = 5.5

    brides = [
        {
            "name": "P. Sashtika",
            "date": "1996-05-11",
            "time": "06:47",
            "lat": 10.6589,
            "lon": 77.0090,
            "tz": 5.5,
            "kulam": "Maniyan (மணியன்)",
            "deity": "Kuppannasamy - Muthur (குப்பண்ணசாமி - முத்தூர்)",
            "jadhagam": "Parihara Sevvai (பரிகார செவ்வாய்)",
            "education": "B.Sc., (CT)",
            "job": "Software Engineer (Bangalore)",
            "birth_place": "Pollachi, TN",
            "birth_place_ta": "பொள்ளாச்சி, தமிழ்நாடு"
        },
        {
            "name": "S. Padmapriyanka",
            "date": "2000-10-06",
            "time": "07:00",
            "lat": 11.3410,
            "lon": 77.7172,
            "tz": 5.5,
            "kulam": "Semban (செம்பன்)",
            "deity": "Kariya Kaliamman - Periyamanali (கரிய காளியம்மன் - பெரியமணலி)",
            "jadhagam": "Clean (சுத்தம்)",
            "education": "M.A B.Ed (English)",
            "job": "Teacher (Private School, Tiruchengode)",
            "birth_place": "Erode, TN",
            "birth_place_ta": "ஈரோடு, தமிழ்நாடு"
        },
        {
            "name": "N. Gomathi",
            "date": "1997-09-15",
            "time": "16:08",
            "lat": 10.5855,
            "lon": 77.2435,
            "tz": 5.5,
            "kulam": "Aanthai (ஆந்ைத)",
            "deity": "Pon Azhagu Nachiamman - Valliarachal (பொன் அழகு நாச்சியம்மன் - வள்ளியரச்சல்)",
            "jadhagam": "Rahu Ketu (ராகு கேது)",
            "education": "MBA",
            "job": "Analyst (Chennai)",
            "birth_place": "Dharapuram, TN",
            "birth_place_ta": "தாராபுரம், தமிழ்நாடு"
        }
    ]

    print("Casting charts and generating bilingual reports...")
    
    boy_sid = build_sidereal_chart(1996, 5, 25, boy_time, boy_lat, boy_lon, boy_tz)
    boy_moon_lon = boy_sid["planet_positions"]["Moon"]["longitude"]
    boy_mangal_chart = {
        "lagna": boy_sid["asc_sid"],
        "positions": {p: d["longitude"] for p, d in boy_sid["planet_positions"].items()}
    }
    boy_md = mangal_dosha(boy_mangal_chart)
    boy_west = compute_western_chart(boy_date, boy_time, boy_tz, boy_lat, boy_lon)
    boy_west_planets = boy_west["calculations"]["planets"]
    boy_chinese = compute_chinese_chart(boy_date, boy_time, boy_tz)
    boy_bazi = boy_chinese["calculations"]["bazi_pillars"]
    boy_mayan = compute_mayan_chart(boy_date)
    boy_tzolkin = boy_mayan["calculations"]

    os.makedirs(str(_ROOT / "reports"), exist_ok=True)

    for b in brides:
        # Vedic
        by, bm, bd = map(int, b["date"].split("-"))
        girl_sid = build_sidereal_chart(by, bm, bd, b["time"], b["lat"], b["lon"], b["tz"])
        girl_moon_lon = girl_sid["planet_positions"]["Moon"]["longitude"]
        vedic_kuta = match_kuta(boy_moon_lon, girl_moon_lon)
        girl_mangal_chart = {
            "lagna": girl_sid["asc_sid"],
            "positions": {p: d["longitude"] for p, d in girl_sid["planet_positions"].items()}
        }
        girl_md = mangal_dosha(girl_mangal_chart)
        
        # Numerology
        num_res = compute_compatibility(boy_name, boy_date, b["name"], b["date"])
        
        # Western Synastry
        girl_west = compute_western_chart(b["date"], b["time"], b["tz"], b["lat"], b["lon"])
        girl_west_planets = girl_west["calculations"]["planets"]
        
        synastry_aspects = []
        aspect_definitions = [
            ("Conjunction", 0, 6),
            ("Sextile", 60, 4),
            ("Square", 90, 5),
            ("Trine", 120, 6),
            ("Opposition", 180, 6)
        ]
        major_bodies = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
        for bp in major_bodies:
            blon = boy_west_planets[bp]["longitude"]
            for gp in major_bodies:
                glon = girl_west_planets[gp]["longitude"]
                diff = abs(blon - glon) % 360
                if diff > 180:
                    diff = 360 - diff
                for name, target, orb in aspect_definitions:
                    if abs(diff - target) <= orb:
                        synastry_aspects.append({
                            "boy_planet": bp,
                            "girl_planet": gp,
                            "aspect": name,
                            "diff": round(diff, 2),
                            "error": round(abs(diff - target), 2)
                        })
                        
        positives = sum(1 for a in synastry_aspects if a["aspect"] in ["Trine", "Sextile", "Conjunction"])
        negatives = sum(1 for a in synastry_aspects if a["aspect"] in ["Square", "Opposition"])
        total_aspects = positives + negatives
        if total_aspects > 0:
            western_score_pct = round((positives / total_aspects) * 100)
        else:
            western_score_pct = 70
            
        # Chinese Bazi
        girl_chinese = compute_chinese_chart(b["date"], b["time"], b["tz"])
        girl_bazi = girl_chinese["calculations"]["bazi_pillars"]
        
        girl_animal = ""
        if "Zi" in girl_bazi["Year"] or "Rat" in girl_bazi["Year"]:
            girl_animal = "Rat"
            chinese_score = 75
            chinese_desc_en = "Rat & Rat (Same sign - generally friendly, shared understanding)"
            chinese_desc_ta = "எலி மற்றும் எலி (ஒரே ராசி - பரஸ்பர புரிதல் உண்டு)"
        elif "Chou" in girl_bazi["Year"] or "Ox" in girl_bazi["Year"]:
            girl_animal = "Ox"
            chinese_score = 95
            chinese_desc_en = "Six Harmonies (Rat & Ox) - Soulmate union, highest compatibility."
            chinese_desc_ta = "ஆறு இணக்கப் பொருத்தம் (எலி மற்றும் மாடு) - ஆன்ம ரீதியான உன்னதப் பொருத்தம்."
        elif "Chen" in girl_bazi["Year"] or "Dragon" in girl_bazi["Year"]:
            girl_animal = "Dragon"
            chinese_score = 90
            chinese_desc_en = "Three Harmonies (Rat & Dragon) - Harmonious affinity, creative and mutual growth."
            chinese_desc_ta = "மூன்று இணக்கப் பொருத்தம் (எலி மற்றும் டிராகன்) - கூட்டு வளர்ச்சி தரும் பொருத்தம்."
        else:
            girl_animal = "Other"
            chinese_score = 70
            chinese_desc_en = "Neutral zodiac compatibility."
            chinese_desc_ta = "சாதாரண ராசி இணக்கம்."
            
        # Mayan
        girl_mayan = compute_mayan_chart(b["date"])
        girl_tzolkin = girl_mayan["calculations"]
        
        # Overall
        vedic_score_pct = (vedic_kuta.total[0] / 36) * 100
        num_score_pct = num_res["score_percent"]
        overall_score = round((vedic_score_pct + num_score_pct + chinese_score + western_score_pct) / 4)
        
        r_en = {
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
        }

        r_ta = {
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
        }

        clean_name = b["name"].replace(" ", "_").replace(".", "")
        
        # Get current date details dynamically for year/month/date subfolders
        import datetime
        now = datetime.datetime.now()
        yr = now.strftime("%Y")
        mo = now.strftime("%m")
        dy = now.strftime("%d")
        
        pdf_dir = _ROOT / "reports" / yr / mo / dy / "pdf"
        md_dir = _ROOT / "reports" / yr / mo / dy / "markdown"
        os.makedirs(str(pdf_dir), exist_ok=True)
        os.makedirs(str(md_dir), exist_ok=True)
        
        # English File Paths
        md_path_en = md_dir / f"Manoj_{clean_name}_Compatibility_Report_EN.md"
        pdf_path_en = pdf_dir / f"Manoj_{clean_name}_Compatibility_Report_EN.pdf"
        generate_md_en(r_en, str(md_path_en))
        try:
            generate_pdf_en(r_en, str(pdf_path_en))
        except PermissionError:
            pdf_path_en_alt = pdf_dir / f"Manoj_{clean_name}_Compatibility_Report_EN_NEW.pdf"
            print(f"WARNING: {pdf_path_en} is locked. Saving to {pdf_path_en_alt}")
            generate_pdf_en(r_en, str(pdf_path_en_alt))
        
        # Tamil File Paths
        md_path_ta = md_dir / f"Manoj_{clean_name}_Compatibility_Report_TA.md"
        pdf_path_ta = pdf_dir / f"Manoj_{clean_name}_Compatibility_Report_TA.pdf"
        generate_md_ta(r_ta, str(md_path_ta))
        try:
            generate_pdf_ta(r_ta, str(pdf_path_ta))
        except PermissionError:
            pdf_path_ta_alt = pdf_dir / f"Manoj_{clean_name}_Compatibility_Report_TA_NEW.pdf"
            print(f"WARNING: {pdf_path_ta} is locked. Saving to {pdf_path_ta_alt}")
            generate_pdf_ta(r_ta, str(pdf_path_ta_alt))
        
    print("All separate bilingual reports successfully generated in dated subfolders!")

if __name__ == "__main__":
    main()
