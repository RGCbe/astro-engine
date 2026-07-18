import os
import sys
import datetime as dt
from pathlib import Path

# Add project root and runtime to path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "runtime"))

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
    # Register serif PlayfairDisplay for premium headings
    pdfmetrics.registerFont(TTFont("PlayfairDisplay", os.path.join(RUNTIME_DIR, "PlayfairDisplay-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("PlayfairDisplay-Bold", os.path.join(RUNTIME_DIR, "PlayfairDisplay-Bold.ttf")))
except Exception as e:
    print(f"Font registration failed: {e}")

# Color Palette
SAGE_DK = HexColor("#1b4332")       # Deep Luxury Forest/Sage Green
SAGE_LT = HexColor("#f0f4f1")       # Soft light sage green
SAND_BG = HexColor("#fbf9f4")       # Premium warm sand off-white background panel
SAND_DK = HexColor("#e6dfd3")       # Darker sand for borders
GOLD_DK = HexColor("#a88a58")       # Champagne Gold for accents/borders
TEXT_DARK = HexColor("#1e293b")     # Charcoal for body text
TEXT_MUTED = HexColor("#64748b")    # Slate-500 for secondary text
INDIGO_DK = HexColor("#1e1b4b")      # Deep indigo for premium feel
INDIGO_LT = HexColor("#3b3a78")      # Light indigo for gradients
WHITE = HexColor("#ffffff")

# Styled status colors
BG_SUCCESS = HexColor("#f0fdf4")    # Calm soft green bg
TEXT_SUCCESS = HexColor("#15803d")  # Deep green text
BG_ALERT = HexColor("#fef2f2")      # Calm soft red bg
TEXT_ALERT = HexColor("#b91c1c")    # Deep red text
BG_ACCENT = HexColor("#fffbeb")     # Calm soft amber bg
TEXT_ACCENT = HexColor("#b45309")   # Deep amber text

# Custom Typography Hierarchy
# Cover styles now use indigo background and PlayfairDisplay for title
style_cover_brand = ParagraphStyle("cover_brand", fontName="Outfit-Bold", fontSize=26, leading=32, textColor=GOLD_DK, alignment=1, spaceAfter=2)
style_cover_sub = ParagraphStyle("cover_sub", fontName="Outfit", fontSize=9, leading=12, textColor=TEXT_MUTED, alignment=1, spaceAfter=80)
style_cover_title = ParagraphStyle("cover_title", fontName="PlayfairDisplay-Bold", fontSize=34, leading=44, textColor=INDIGO_DK, alignment=1, spaceAfter=8)
style_cover_subtitle = ParagraphStyle("cover_subtitle", fontName="Outfit", fontSize=14, leading=20, textColor=GOLD_DK, alignment=1, spaceAfter=140)
style_cover_meta = ParagraphStyle("cover_meta", fontName="Outfit", fontSize=10, textColor=TEXT_DARK, alignment=1, leading=16)

# Section headings use PlayfairDisplay for premium feel
style_h1 = ParagraphStyle("h1", fontName="PlayfairDisplay-Bold", fontSize=18, textColor=INDIGO_DK, spaceBefore=18, spaceAfter=8, leading=24)
style_h2 = ParagraphStyle("h2", fontName="PlayfairDisplay-Bold", fontSize=13, textColor=GOLD_DK, spaceBefore=10, spaceAfter=4, leading=18)
style_body = ParagraphStyle("body", fontName="Outfit", fontSize=9.5, textColor=TEXT_DARK, leading=14.5, spaceAfter=6)
style_body_center = ParagraphStyle("body_center", fontName="Outfit", fontSize=9.5, textColor=TEXT_DARK, leading=14.5, alignment=1)

style_badge = ParagraphStyle("badge", fontName="Outfit-Bold", fontSize=9, textColor=white, alignment=1)
style_card_title = ParagraphStyle("card_title", fontName="Outfit-Bold", fontSize=11, textColor=SAGE_DK, spaceAfter=4)
style_card_meta = ParagraphStyle("card_meta", fontName="Outfit", fontSize=8.5, textColor=TEXT_MUTED, leading=11)
style_card_val_green = ParagraphStyle("card_val_green", fontName="Outfit-Bold", fontSize=9.5, textColor=TEXT_SUCCESS, leading=12)
style_card_val_red = ParagraphStyle("card_val_red", fontName="Outfit-Bold", fontSize=9.5, textColor=TEXT_ALERT, leading=12)
style_card_val_neutral = ParagraphStyle("card_val_neutral", fontName="Outfit-Bold", fontSize=9.5, textColor=TEXT_DARK, leading=12)

style_timeline_time = ParagraphStyle("t_time", fontName="Outfit-Bold", fontSize=10, textColor=GOLD_DK, alignment=2)
style_timeline_label = ParagraphStyle("t_label", fontName="Outfit-Bold", fontSize=10, textColor=SAGE_DK)
style_timeline_desc = ParagraphStyle("t_desc", fontName="Outfit", fontSize=9, textColor=TEXT_DARK, leading=12)

style_blessing_title = ParagraphStyle("blessing_title", fontName="Outfit-Bold", fontSize=14, textColor=GOLD_DK, alignment=1, spaceAfter=10)
style_blessing_body = ParagraphStyle("blessing_body", fontName="Outfit-Light", fontSize=11, textColor=WHITE, leading=18, alignment=1)

def draw_page_decorations(canvas, doc):
    canvas.saveState()
    # Skip decorations on the cover page (Page 1)
    if doc.page == 1:
        # Fill page with subtle indigo gradient (simulated with solid indigo_lt)
        canvas.setFillColor(SAND_BG)
        canvas.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
        # Draw mandala overlay (transparent PNG) centered
        mandala_path = r"C:\Users\chive\.gemini\antigravity\brain\667a9de7-343e-423f-9a9b-ba7fe1ceeda7\cover_mandala_1784016161279.png"
        try:
            canvas.drawImage(mandala_path, (A4[0]-200)/2, (A4[1]-200)/2, width=200, height=200, mask='auto')
        except Exception as e:
            print(f"Mandala image load failed: {e}")
        # Draw luxury cover double border
        canvas.setStrokeColor(GOLD_DK)
        canvas.setLineWidth(1.5)
        canvas.rect(20, 20, A4[0] - 40, A4[1] - 40)
        canvas.setLineWidth(0.5)
        canvas.rect(25, 25, A4[0] - 50, A4[1] - 50)
        
        # Corner dots
        for x in [25, A4[0] - 25]:
            for y in [25, A4[1] - 25]:
                canvas.circle(x, y, 2.5, stroke=1, fill=1)
                
        # Concentric faint background Mandala
        center_x = A4[0] / 2
        center_y = A4[1] / 2 - 20
        canvas.setStrokeColor(HexColor("#f5f1e6"))
        canvas.setFillColor(white)
        for r in [40, 85, 130, 175, 220]:
            canvas.circle(center_x, center_y, r, stroke=1, fill=0)
    else:
        # Running header line
        canvas.setStrokeColor(GOLD_DK)
        canvas.setLineWidth(0.8)
        canvas.line(doc.leftMargin, A4[1] - 40, A4[0] - doc.rightMargin, A4[1] - 40)
        
        # Header text
        canvas.setFont("Outfit-Bold", 8)
        canvas.setFillColor(SAGE_DK)
        canvas.drawString(doc.leftMargin, A4[1] - 32, "ASTROMYSTIC PREMIUM MUHURTHA CONSULTATION")
        
        # Footer line
        canvas.line(doc.leftMargin, 45, A4[0] - doc.rightMargin, 45)
        
        # Footer text
        canvas.setFont("Outfit", 8)
        canvas.setFillColor(TEXT_MUTED)
        canvas.drawString(doc.leftMargin, 32, "Copyright 2026 AstroMystic. Prepared using Lahiri Ayanamsa.")
        
        page_str = f"Page {doc.page}"
        canvas.drawRightString(A4[0] - doc.rightMargin, 32, page_str)
        
    canvas.restoreState()

def make_comparison_card(element_name, date_1_desc, date_2_desc, val_1_style, val_2_style):
    """Create a styled side-by-side comparison card."""
    card_content = [
        [Paragraph(element_name, style_card_title), ""],
        [Paragraph("July 16 (Thu)", style_card_meta), Paragraph("July 17 (Fri)", style_card_meta)],
        [Paragraph(date_1_desc, val_1_style), Paragraph(date_2_desc, val_2_style)]
    ]
    t = Table(card_content, colWidths=[4.1*cm, 4.1*cm])
    t.setStyle(TableStyle([
        ("SPAN", (0,0), (1,0)),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BACKGROUND", (0,0), (-1,-1), SAND_BG),
        ("BOX", (0,0), (-1,-1), 0.5, SAND_DK),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    return t

def generate_pdf_report(pdf_path):
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    story = []
    
    # ────────────────────────────────────────────────────────────
    # PAGE 1: COVER PAGE
    # ────────────────────────────────────────────────────────────
    story.append(Spacer(1, 2.5*cm))
    story.append(Paragraph("ASTROMYSTIC", style_cover_brand))
    story.append(Paragraph("VEDIC ASTROLOGY SERVICES", style_cover_sub))
    
    story.append(Paragraph("MUHURTHA REPORT", style_cover_title))
    story.append(Paragraph("House Shifting (Griha Pravesh) Timing Analysis", style_cover_subtitle))
    
    meta_text = (
        "<b>Prepared For:</b> Mr. Manoj Kumar's Friend<br/>"
        "<b>Dates Analyzed:</b> 16 July 2026 & 17 July 2026<br/>"
        "<b>System:</b> Lahiri Ayanamsa | Vedic Panchanga Core<br/>"
        "<b>Status:</b> Completed Consultation Booklet"
    )
    story.append(Paragraph(meta_text, style_cover_meta))
    story.append(PageBreak())
    
    # ────────────────────────────────────────────────────────────
    # PAGE 2: SUMMARY & INFOGRAPHICS
    # ────────────────────────────────────────────────────────────
    story.append(Paragraph("Executive Muhurtha Summary", style_h1))
    
    summary_intro = (
        "Below is the core electional breakdown for your friend's house shifting. Thursday, July 16, 2026 "
        "is the selected day. Friday, July 17, 2026 carries critical malefic doshas and is not recommended."
    )
    story.append(Paragraph(summary_intro, style_body))
    story.append(Spacer(1, 0.2*cm))
    
    # Hero Recommendation Card
    hero_content = [
        [Paragraph("RECOMMENDED DATE", style_badge), ""],
        [Paragraph("Thursday, July 16, 2026", ParagraphStyle("hero_date", fontName="Outfit-Bold", fontSize=15, textColor=SAGE_DK)), ""],
        [Paragraph("<b>Muhurtha Score:</b> 63 / 100", style_body), Paragraph("<b>Verdict:</b> AUSPICIOUS / ACCEPTABLE", ParagraphStyle("h_ver", fontName="Outfit-Bold", fontSize=9.5, textColor=TEXT_SUCCESS))]
    ]
    t_hero = Table(hero_content, colWidths=[9.0*cm, 9.0*cm])
    t_hero.setStyle(TableStyle([
        ("SPAN", (0,0), (1,0)),
        ("SPAN", (0,1), (1,1)),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,-1), BG_SUCCESS),
        ("BACKGROUND", (0,0), (-1,0), SAGE_DK),
        ("BOX", (0,0), (-1,-1), 1, SAGE_DK),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    story.append(t_hero)
    story.append(Spacer(1, 0.4*cm))
    
    # Side-by-Side Comparison Cards (2x2 Grid)
    story.append(Paragraph("Panchanga Elements Comparison", style_h2))
    
    card_tithi = make_comparison_card("Tithi (Lunar Day)", "Tritiya (3rd Day)<br/>Jaya Tithi - Favorable", "Chaturthi (4th Day)<br/>Rikta Tithi - Avoid", style_card_val_green, style_card_val_red)
    card_nak = make_comparison_card("Nakshatra (Moon Star)", "Ashlesha<br/>Neutral", "Magha<br/>Fierce - Avoid", style_card_val_neutral, style_card_val_red)
    card_yoga = make_comparison_card("Yoga (Solar-Lunar)", "Siddhi<br/>Auspicious - Good", "Vyatipata<br/>Malefic - Avoid", style_card_val_green, style_card_val_red)
    card_vara = make_comparison_card("Vara (Weekday)", "Thursday (Guru)<br/>Auspicious (Jupiter)", "Friday (Shukra)<br/>Auspicious (Venus)", style_card_val_green, style_card_val_green)
    
    grid_data = [
        [card_tithi, card_nak],
        [card_yoga, card_vara]
    ]
    t_grid = Table(grid_data, colWidths=[9.0*cm, 9.0*cm])
    t_grid.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    story.append(t_grid)
    story.append(Spacer(1, 0.4*cm))
    
    # Timeline
    story.append(Paragraph("Visual Shifting Timeline (Thursday, July 16)", style_h2))
    
    timeline_data = [
        [Paragraph("04:24 AM - 05:12 AM", style_timeline_time), 
         Paragraph("Brahma Muhurta", style_timeline_label), 
         Paragraph("Early morning prayers. Highly recommended for spiritual start.", style_timeline_desc)],
         
        [Paragraph("09:00 AM - 10:30 AM", style_timeline_time), 
         Paragraph("Gulika Kala (Avoid)", style_timeline_label), 
         Paragraph("Minor/packing tasks are fine; do not initiate the main threshold puja.", style_timeline_desc)],
         
        [Paragraph("11:36 AM - 12:24 PM", style_timeline_time), 
         Paragraph("Abhijit Muhurta (Best Time)", style_timeline_label), 
         Paragraph("The peak auspicious hour of the day. Cross the threshold and start puja.", style_timeline_desc)],
         
        [Paragraph("01:30 PM - 03:00 PM", style_timeline_time), 
         Paragraph("Rahu Kala (Avoid)", style_timeline_label), 
         Paragraph("Highly malefic window. Strictly avoid moving items or entering.", style_timeline_desc)]
    ]
    
    t_time = Table(timeline_data, colWidths=[4.2*cm, 4.8*cm, 9.0*cm])
    t_time.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.5, SAND_DK),
        ("BACKGROUND", (0,0), (-1,-1), SAND_BG),
        ("BACKGROUND", (0,2), (1,2), BG_SUCCESS), # highlight Abhijit
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t_time)
    story.append(PageBreak())
    
    # ────────────────────────────────────────────────────────────
    # PAGE 3: DETAILED ANALYSIS & CLOSING BLESSING
    # ────────────────────────────────────────────────────────────
    story.append(Paragraph("Classical Astrological Rationale", style_h1))
    
    rationale_text = (
        "The selection of Thursday, July 16, 2026, over Friday, July 17, 2026, is based on two core "
        "rules of Vedic Electional Astrology:<br/><br/>"
        "<b>1. The Tithi Rule (Why July 17 must be avoided):</b><br/>"
        "In Vedic Astrology, Tithis are categorized by their energetic nature. Chaturthi (4th lunar day) "
        "is a <i>Rikta (empty) Tithi</i>. The classical text <i>Muhurtha Chintamani</i> explicitly advises "
        "against entering a new home or beginning a new residence on a Rikta Tithi (4th, 9th, 14th) as it represents "
        "empty or waning energy. Conversely, Tritiya (3rd day) is a <i>Jaya (victory) Tithi</i>, which brings "
        "growth and prosperity to new beginnings.<br/><br/>"
        "<b>2. The Yoga Rule:</b><br/>"
        "July 17 suffers from <i>Vyatipata Yoga</i>, which is classified as highly malefic. Any auspicious "
        "work initiated during this Yoga leads to conflicts and wastage of effort. July 16 is blessed by "
        "<i>Siddhi Yoga</i>, which brings success and fulfillment."
    )
    story.append(Paragraph(rationale_text, style_body))
    story.append(Spacer(1, 0.4*cm))
    
    # Callout box
    callout_content = [
        [Paragraph("<b>💡 IMPORTANT ADVICE</b>", style_card_title)],
        [Paragraph(
            "For a complete 100% confirmation, your friend can provide their **Birth Star (Janma Nakshatra)** "
            "and **Moon Sign (Rasi)**. This will allow us to evaluate their natal **Chandra Bala** and **Tara Bala** "
            "to ensure the day has no personal astrological warnings.", style_body
        )]
    ]
    t_callout = Table(callout_content, colWidths=[18.0*cm])
    t_callout.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), BG_ACCENT),
        ("BOX", (0,0), (-1,-1), 0.5, GOLD_DK),
        ("LINELEFT", (0,0), (-1,-1), 4, GOLD_DK),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(t_callout)
    story.append(Spacer(1, 1.0*cm))
    
    # Final Blessing Page Card (at bottom of Page 3)
    blessing_content = [
        [Paragraph("════ ✦ A BLESSING FOR YOUR NEW HOME ✦ ════", style_blessing_title)],
        [Paragraph(
            "May this auspicious Muhurtha bring health, harmony,<br/>"
            "prosperity, and peace to your friend's new residence.<br/>"
            "May the threshold be crossed with joy and abundance.<br/><br/>"
            "<b>Best Wishes,<br/>AstroMystic Vedic Consulting</b>", style_blessing_body
        )]
    ]
    t_bless = Table(blessing_content, colWidths=[18.0*cm])
    t_bless.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), SAGE_DK),
        ("BOX", (0,0), (-1,-1), 1.5, GOLD_DK),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 22),
        ("BOTTOMPADDING", (0,0), (-1,-1), 22),
        ("LEFTPADDING", (0,0), (-1,-1), 15),
        ("RIGHTPADDING", (0,0), (-1,-1), 15),
    ]))
    story.append(t_bless)
    
    doc.build(story, onFirstPage=draw_page_decorations, onLaterPages=draw_page_decorations)
    print(f"Generated Luxury Muhurtha PDF at: {pdf_path}")

def generate_md_report(md_path):
    report = []
    report.append("# House Shifting (Griha Pravesh) Muhurtha Report\n")
    report.append("> **Analysis Date:** 2026-07-14\n")
    report.append("## 🏆 Overall Verdict")
    report.append("* **July 16, 2026 (Thursday):** **AUSPICIOUS / ACCEPTABLE (Score: 63/100)** — **Recommended Day**")
    report.append("* **July 17, 2026 (Friday):** **AVOID / NOT IDEAL (Score: 41/100)** — **Not Recommended**\n")
    
    report.append("## 1. Side-by-Side Comparison Table\n")
    report.append("| Element | July 16, 2026 (Thursday) | July 17, 2026 (Friday) | Analysis & Impact |")
    report.append("| :--- | :--- | :--- | :--- |")
    report.append("| **Verdict** | **AUSPICIOUS / ACCEPTABLE** 🟢 | **AVOID / NOT IDEAL** 🔴 | Thursday is highly favored. |")
    report.append("| **Muhurtha Score** | **63 / 100** | **41 / 100** | July 16 is much stronger. |")
    report.append("| **Tithi (Lunar Day)** | **Tritiya** (Jaya Tithi) 🟢 | **Chaturthi** (Rikta Tithi) 🔴 | Chaturthi brings empty/loss energy (avoid). |")
    report.append("| **Vara (Weekday)** | **Thursday** (ruled by Jupiter) 🟢 | **Friday** (ruled by Venus) 🟢 | Both weekdays are generally positive. |")
    report.append("| **Nakshatra** | **Ashlesha** (Neutral) | **Magha** (Fierce) 🔴 | Magha is not ideal for housewarming. |")
    report.append("| **Yoga** | **Siddhi** (Auspicious) 🟢 | **Vyatipata** (Malefic) 🔴 | Vyatipata is heavily malefic. |")
    report.append("| **Karana** | **Taitila** (Auspicious) | **Vanija** (Acceptable) | Taitila is stable and supportive. |\n")
    
    report.append("## 2. Auspicious Windows for July 16, 2026 (Recommended Day)\n")
    report.append("* ✨ **Abhijit Muhurta (Best Time): 11:36 AM to 12:24 PM** — **Highly recommended window** to cross the threshold and begin the housewarming puja.")
    report.append("* 🚫 **Rahu Kala (Avoid): 01:30 PM to 03:00 PM** — Do not start shifting or crossing the threshold during this time.")
    report.append("* 🚫 **Gulika Kala (Avoid): 09:00 AM to 10:30 AM** — Avoid starting primary house warming rituals.")
    report.append("* 🌅 **Brahma Muhurta: 04:24 AM to 05:12 AM** — Ideal for early morning spiritual prayers.\n")
    
    report.append("## 3. Astrological Rationale")
    report.append("> [!IMPORTANT]\n"
                  "> **Why July 17 must be avoided:**\n"
                  "> 1. **Chaturthi Tithi (Rikta):** Entering a home on Chaturthi represents void/loss energy in classical texts.\n"
                  "> 2. **Vyatipata Yoga:** Heavily malefic planetary angle that brings obstacles, arguments, and waste of effort.\n"
                  "> 3. **Magha Nakshatra:** Ruled by ancestors (Pitrus) and possesses a fierce energy unsuitable for starting a new residence.\n")
                  
    report.append("> [!TIP]\n"
                  "> **Personalize this report:**\n"
                  "> To calculate their personal Tara Bala and Chandra Bala, ask your friend for their **Birth Star (Janma Nakshatra)** and **Moon Sign (Rasi)**.")
                  
    Path(md_path).write_text("\n".join(report), encoding="utf-8")
    print(f"Generated Muhurtha MD at: {md_path}")

if __name__ == "__main__":
    pdf_out = os.path.join(str(_ROOT), "reports", "2026", "07", "14", "pdf", "House_Shifting_Muhurtha_Report.pdf")
    md_out = os.path.join(str(_ROOT), "reports", "2026", "07", "14", "markdown", "House_Shifting_Muhurtha_Report.md")
    
    os.makedirs(os.path.dirname(pdf_out), exist_ok=True)
    os.makedirs(os.path.dirname(md_out), exist_ok=True)
    
    generate_pdf_report(pdf_out)
    generate_md_report(md_out)
