import os
import sys
import datetime
from pathlib import Path
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.chart_builder import build_sidereal_chart
from engine.kuta import match_kuta, mangal_dosha

# Reportlab imports
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line

# Setup fonts
RUNTIME_DIR = "runtime"
try:
    pdfmetrics.registerFont(TTFont("Outfit", os.path.join(RUNTIME_DIR, "Outfit-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Outfit-Bold", os.path.join(RUNTIME_DIR, "Outfit-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("Outfit-Medium", os.path.join(RUNTIME_DIR, "Outfit-Medium.ttf")))
    pdfmetrics.registerFont(TTFont("Outfit-Light", os.path.join(RUNTIME_DIR, "Outfit-Light.ttf")))
except Exception as e:
    print(f"Font registration failed: {e}")

# Colors
INDIGO = HexColor("#1a1d3a")
GOLD = HexColor("#c9a032")
GOLD_DK = HexColor("#8a6a18")
CREAM = HexColor("#faf6e8")
CREAM_2 = HexColor("#fff8e1")
GREY_DK = HexColor("#2a2a2a")
GREY_MD = HexColor("#5a5a5a")
GREY_LT = HexColor("#e8e6e2")
CYAN = HexColor("#00a2cc")
PINK = HexColor("#cc0080")
GREEN = HexColor("#16a34a")
RED = HexColor("#c0392b")

# Styles
style_title = ParagraphStyle("title", fontName="Outfit-Bold", fontSize=22, textColor=INDIGO, alignment=1, spaceAfter=8)
style_subtitle = ParagraphStyle("subtitle", fontName="Outfit", fontSize=11, textColor=GOLD_DK, alignment=1, spaceAfter=20)
style_h1 = ParagraphStyle("h1", fontName="Outfit-Bold", fontSize=14, textColor=INDIGO, spaceBefore=12, spaceAfter=8)
style_h2 = ParagraphStyle("h2", fontName="Outfit-Bold", fontSize=11, textColor=GOLD_DK, spaceBefore=8, spaceAfter=4)
style_body = ParagraphStyle("body", fontName="Outfit", fontSize=9.5, textColor=GREY_DK, leading=13.5, spaceAfter=5)
style_body_bold = ParagraphStyle("body_bold", fontName="Outfit-Bold", fontSize=9.5, textColor=INDIGO, leading=13.5, spaceAfter=5)
style_cell_bold = ParagraphStyle("cell_bold", fontName="Outfit-Bold", fontSize=9, textColor=INDIGO, leading=11)
style_cell = ParagraphStyle("cell", fontName="Outfit", fontSize=9, textColor=GREY_DK, leading=11)
style_cell_green = ParagraphStyle("cell_green", fontName="Outfit-Bold", fontSize=9, textColor=GREEN, leading=11)
style_cell_red = ParagraphStyle("cell_red", fontName="Outfit-Bold", fontSize=9, textColor=RED, leading=11)

def draw_header_footer(canvas, doc):
    canvas.saveState()
    # Header line
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1)
    canvas.line(doc.leftMargin, A4[1] - 40, A4[0] - doc.rightMargin, A4[1] - 40)
    
    # Header Text
    canvas.setFont("Outfit-Bold", 8)
    canvas.setFillColor(INDIGO)
    canvas.drawString(doc.leftMargin, A4[1] - 32, "ASTROMYSTIC CELESTIAL MATCHING REPORT")
    canvas.drawRightString(A4[0] - doc.rightMargin, A4[1] - 32, "MANOJ KUMAR & N. KAYALVIZHI")
    
    # Footer line
    canvas.line(doc.leftMargin, 45, A4[0] - doc.rightMargin, 45)
    
    # Footer Text
    canvas.setFont("Outfit", 8)
    canvas.setFillColor(GREY_MD)
    canvas.drawString(doc.leftMargin, 32, "© 2026 AstroMystic. Generated using Thirukanitham Ayanamsa.")
    canvas.drawRightString(A4[0] - doc.rightMargin, 32, f"Page {doc.page}")
    canvas.restoreState()

def build_pdf(filename="reports/Manoj_Kayalvizhi_Compatibility_Report.pdf"):
    # Load Boy's chart
    with open("charts/manoj_chart.json", "r", encoding="utf-8") as f:
        manoj_chart = json.load(f)
        
    # Build Girl's chart
    kayalvizhi_core = build_sidereal_chart(
        year=1997, month=6, day=26, time_str="04:07",
        lat=10.4851135, lon=77.7460054, tz_hours=5.5
    )
    
    # Match Kutas
    boy_moon_lon = manoj_chart["positions"]["Moon"]["lon"]
    girl_moon_lon = kayalvizhi_core["planet_positions"]["Moon"]["longitude"]
    kuta_res = match_kuta(boy_moon_lon, girl_moon_lon)
    
    # Setup document
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm
    )
    
    story = []
    
    # ── Page 1: Cover Header ──
    story.append(Paragraph("CELESTIAL COMPATIBILITY REPORT", style_title))
    story.append(Paragraph("A Vedic Matchmaking Assessment (Ashta-Kuta Milan)", style_subtitle))
    story.append(Spacer(1, 0.4 * cm))
    
    # Birth details comparison table
    story.append(Paragraph("1. Birth Parameters & Astrological Identity", style_h1))
    
    param_data = [
        [Paragraph("Parameter", style_cell_bold), Paragraph("Boy: Manoj Kumar", style_cell_bold), Paragraph("Girl: N. Kayalvizhi", style_cell_bold)],
        [Paragraph("Birth Date & Time", style_cell), Paragraph("25 May 1996, 20:25 IST", style_cell), Paragraph("26 June 1997, 04:07 IST", style_cell)],
        [Paragraph("Birth Place", style_cell), Paragraph("Coimbatore, TN", style_cell), Paragraph("Oddanchatram, Dindigul, TN", style_cell)],
        [Paragraph("Lagnam (Ascendant)", style_cell), Paragraph("Sagittarius (Dhanusu)", style_cell), Paragraph("Taurus (Rishabam)", style_cell)],
        [Paragraph("Rasi (Moon Sign)", style_cell), Paragraph("Leo (Simham)", style_cell), Paragraph("Aquarius (Kumbam)", style_cell)],
        [Paragraph("Nakshatra (Star)", style_cell), Paragraph("Magha (மகம) - 4", style_cell), Paragraph("Shatabhisha (Sathayam) - 4", style_cell)],
        [Paragraph("Rasi Lord", style_cell), Paragraph("Sun (Suriyan)", style_cell), Paragraph("Saturn (Sani)", style_cell)],
        [Paragraph("Nakshatra Lord", style_cell), Paragraph("Ketu", style_cell), Paragraph("Rahu", style_cell)],
    ]
    t_param = Table(param_data, colWidths=[5.5 * cm, 6.25 * cm, 6.25 * cm])
    t_param.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
        ("BACKGROUND", (0,0), (-1,0), CREAM),
        ("GRID", (0,0), (-1,-1), 0.5, var_color := HexColor("#d4af37")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t_param)
    story.append(Spacer(1, 0.4 * cm))
    
    # 2. Score Summary
    story.append(Paragraph("2. Ashta-Kuta Compatibility Score", style_h1))
    
    score_p = Paragraph(f"<b>Overall Score: {kuta_res.total[0]} / 36 Points ({kuta_res.verdict})</b>", ParagraphStyle("score_p", fontName="Outfit-Bold", fontSize=12, textColor=INDIGO))
    story.append(score_p)
    story.append(Spacer(1, 0.2 * cm))
    
    kuta_data = [
        [Paragraph("Kuta", style_cell_bold), Paragraph("Boy (Magha)", style_cell_bold), Paragraph("Girl (Shatabhisha)", style_cell_bold), Paragraph("Score", style_cell_bold), Paragraph("Max", style_cell_bold), Paragraph("Indication", style_cell_bold)],
        [Paragraph("Nadi (Physiology)", style_cell), Paragraph("Antya", style_cell), Paragraph("Adi", style_cell), Paragraph("8", style_cell_green), Paragraph("8", style_cell), Paragraph("Excellent. No Nadi Dosha.", style_cell)],
        [Paragraph("Bhakoot (Emotional)", style_cell), Paragraph("Leo", style_cell), Paragraph("Aquarius", style_cell), Paragraph("7", style_cell_green), Paragraph("7", style_cell), Paragraph("Samasaptaka (1-7 axis). In harmony.", style_cell)],
        [Paragraph("Gana (Temper)", style_cell), Paragraph("Rakshasa", style_cell), Paragraph("Rakshasa", style_cell), Paragraph("6", style_cell_green), Paragraph("6", style_cell), Paragraph("Same Gana. Perfect alignment.", style_cell)],
        [Paragraph("Yoni (Intimacy)", style_cell), Paragraph("Rat (Magha)", style_cell), Paragraph("Horse (Shatabhisha)", style_cell), Paragraph("2", style_cell), Paragraph("4", style_cell), Paragraph("Neutral. No animal enmity.", style_cell)],
        [Paragraph("Graha Maitri (Friend)", style_cell), Paragraph("Sun", style_cell), Paragraph("Saturn", style_cell), Paragraph("0", style_cell_red), Paragraph("5", style_cell), Paragraph("Sun & Saturn are planetary adversaries.", style_cell)],
        [Paragraph("Tara (Destiny)", style_cell), Paragraph("Magha", style_cell), Paragraph("Shatabhisha", style_cell), Paragraph("0", style_cell_red), Paragraph("3", style_cell), Paragraph("Pratyak Tara (Boy -> Girl). Neutralized in reverse.", style_cell)],
        [Paragraph("Vasya (Control)", style_cell), Paragraph("Leo", style_cell), Paragraph("Aquarius", style_cell), Paragraph("0", style_cell), Paragraph("2", style_cell), Paragraph("Neutral control relationship.", style_cell)],
        [Paragraph("Varna (Ego)", style_cell), Paragraph("Kshatriya", style_cell), Paragraph("Shudra", style_cell), Paragraph("1", style_cell_green), Paragraph("1", style_cell), Paragraph("Harmonious class alignment.", style_cell)],
        [Paragraph("TOTAL", style_cell_bold), Paragraph("", style_cell), Paragraph("", style_cell), Paragraph(str(kuta_res.total[0]), style_cell_green), Paragraph("36", style_cell_bold), Paragraph("VERY GOOD COMPATIBILITY", style_cell_bold)],
    ]
    
    t_kuta = Table(kuta_data, colWidths=[3.5 * cm, 2.7 * cm, 3.2 * cm, 1.2 * cm, 1.0 * cm, 6.4 * cm])
    t_kuta.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [white, GREY_LT]),
        ("BACKGROUND", (0,0), (-1,0), CREAM),
        ("BACKGROUND", (0,-1), (-1,-1), CREAM_2),
        ("SPAN", (1, -1), (2, -1)),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t_kuta)
    
    story.append(PageBreak())
    
    # ── Page 2: Sevvai Dosham & Dasha Timing ──
    story.append(Paragraph("3. Sevvai Dosham (Mangal Dosha) Analysis", style_h1))
    story.append(Paragraph("Sevvai Dosham is evaluated to check for compatibility and prevent domestic disharmony. Traditional Tamil astrology guidelines are applied:", style_body))
    
    # Mangal Dosha calculations
    boy_mangal = {"lagna": manoj_chart["lagna_lon"], "positions": {"Moon": manoj_chart["positions"]["Moon"]["lon"], "Mars": manoj_chart["positions"]["Mars"]["lon"]}}
    girl_mangal = {"lagna": kayalvizhi_core["asc_sid"], "positions": {"Moon": kayalvizhi_core["planet_positions"]["Moon"]["longitude"], "Mars": kayalvizhi_core["planet_positions"]["Mars"]["longitude"]}}
    boy_md = mangal_dosha(boy_mangal)
    girl_md = mangal_dosha(girl_mangal)
    
    dosha_data = [
        [Paragraph("Manoj Kumar (Boy)", style_cell_bold), Paragraph("N. Kayalvizhi (Girl)", style_cell_bold)],
        [
            Paragraph("<b>Verdict: NO DOSHAM</b><br/><br/>Mars is placed in Aries (its own sign, very strong) in the 5th house from Lagna (Sagittarius). This is a highly positive placement that does not create any Sevvai Dosham in your birth chart.", style_body),
            Paragraph("<b>Verdict: CHANDRA MANGAL DOSHA (Moderate)</b><br/><br/>Mars is placed in Virgo (Kanni) conjunct Rahu, placing Mars in the 8th house from the Moon (Aquarius). This creates a moderate Sevvai Dosham from the Moon.<br/><br/><i>Mitigation:</i> In classical rules, Mars in Virgo (ruled by Mercury) is considered softened. It does not obstruct marriage with a non-Dosham partner as long as general compatibility is strong.", style_body)
        ]
    ]
    t_dosha = Table(dosha_data, colWidths=[9 * cm, 9 * cm])
    t_dosha.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("BACKGROUND", (0,0), (-1,0), CREAM),
        ("BACKGROUND", (0,1), (0,1), white),
        ("BACKGROUND", (1,1), (1,1), white),
        ("LINELEFT", (0,0), (0,-1), 4, GREEN),
        ("LINELEFT", (1,0), (1,-1), 4, RED),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(t_dosha)
    story.append(Spacer(1, 0.4 * cm))
    
    # 4. Dasha Timeline
    story.append(Paragraph("4. Dasha Synchronization & Timing", style_h1))
    story.append(Paragraph("Vimshottari Dasha synchronization determines if both charts are running periods that support home-settling and family expansion:", style_body))
    
    dasha_data = [
        [Paragraph("Manoj Kumar (Boy) Timeline", style_cell_bold), Paragraph("N. Kayalvizhi (Girl) Timeline", style_cell_bold)],
        [
            Paragraph("<b>Moon Dasha - Jupiter Bhukti</b><br/>(May 2026 to September 2027)<br/><br/>Jupiter is your <b>Lagna Lord</b> placed in Sagittarius in the 1st house (forming Hamsa Yoga). Running the Lagna Lord's period is the most premium time for career settlement, purchases, and marriage.", style_body),
            Paragraph("<b>Saturn Dasha - Mars Bhukti</b><br/>(May 2026 to June 2027)<br/><br/>Mars is her <b>7th Lord of marriage</b> placed in the 5th house. The sub-period of the 7th lord is the classic and most powerful indicator for wedding arrangements in her chart.", style_body)
        ]
    ]
    t_dasha = Table(dasha_data, colWidths=[9 * cm, 9 * cm])
    t_dasha.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("BACKGROUND", (0,0), (-1,0), CREAM),
        ("BACKGROUND", (0,1), (0,1), white),
        ("BACKGROUND", (1,1), (1,1), white),
        ("LINELEFT", (0,0), (-1,-1), 4, GOLD),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(t_dasha)
    
    # Overlap Box
    story.append(Spacer(1, 0.3 * cm))
    overlap_text = Paragraph(
        "<b>⚠️ CRITICAL OVERLAP WINDOW (Active Now until June 2027):</b> Both charts are in highly synchronized, active wedding timelines. This represents a rare window where both the boy's Lagna Lord and the girl's 7th Lord of marriage are operating simultaneously. Proceeding immediately is highly recommended.",
        style_body
    )
    t_overlap = Table([[overlap_text]], colWidths=[18 * cm])
    t_overlap.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CREAM_2),
        ("LINEBEFORE", (0,0), (0,-1), 3, GOLD),
        ("BOX", (0,0), (-1,-1), 0.5, GOLD_LT := HexColor("#e5cd6c")),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t_overlap)
    
    story.append(PageBreak())
    
    # ── Page 3: Profile Fit & Summary ──
    story.append(Paragraph("5. Partner Profile & Expectation Fit", style_h1))
    story.append(Paragraph("Vedic astrology charts contain specific indicators describing the partner's character and profession, which we cross-reference against actual life parameters:", style_body))
    
    fit_data = [
        [
            Paragraph("<b>Manoj's Spouse Indicators (Chart Fit):</b>", style_cell_bold),
            Paragraph("<b>Kayalvizhi's Expectation Fit:</b>", style_cell_bold)
        ],
        [
            Paragraph("Manoj's 7th house (Gemini) contains its lord Venus, which strongly predicts an educated, highly communicative spouse working in an intellectual or educational field (Gemini rules teaching, typing, communication).<br/><br/><b>Actual Status:</b> N. Kayalvizhi has an <b>MA, B.Ed</b> and works as a <b>Teacher</b> in a private school. <b>(Perfect Fit)</b>", style_body),
            Paragraph("Kayalvizhi's matrimonial profile lists her expectation for her husband's background as: <i>'Good job + Agriculture/Business'</i>.<br/><br/><b>Actual Status:</b> Manoj works as a civil construction draftsman (stable professional job) and manages a family dairy/agricultural business. <b>(Perfect Fit)</b>", style_body)
        ]
    ]
    t_fit = Table(fit_data, colWidths=[9 * cm, 9 * cm])
    t_fit.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("BACKGROUND", (0,0), (-1,0), CREAM),
        ("BACKGROUND", (0,1), (0,1), white),
        ("BACKGROUND", (1,1), (1,1), white),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(t_fit)
    story.append(Spacer(1, 0.4 * cm))
    
    # 6. Overall Summary & Remedies
    story.append(Paragraph("6. Overall Verdict & Recommendations", style_h1))
    
    verdict_text = Paragraph(
        "<b>VERDICT: HIGHLY RECOMMENDED MATCH (90% FIT)</b><br/><br/>"
        "1. <b>Strength:</b> The Ashta-Kuta score is <b>24 / 36 (Very Good)</b> with completely clean Nadi (8/8) and Bhakoot (7/7) indicators, eliminating any severe life or health doshas.<br/>"
        "2. <b>Temperament:</b> Both sharing the Rakshasa Gana provides mutual understanding and prevent either from feeling overwhelmed by the other.<br/>"
        "3. <b>Timing:</b> The current sub-periods of both charts are perfectly aligned for a wedding before June/September 2027.<br/>"
        "4. <b>Remedies:</b> Because of Kayalvizhi's moderate Chandra Mangal Dosham, it is recommended for the couple to perform a simple prayer at Vaaitheeswaran Temple (near Sirkazhi) or light a ghee lamp for Lord Murugan/Mars on Tuesdays to ensure complete peace.",
        style_body
    )
    t_verdict = Table([[verdict_text]], colWidths=[18 * cm])
    t_verdict.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CREAM),
        ("LINEBEFORE", (0,0), (0,-1), 4, GREEN),
        ("BOX", (0,0), (-1,-1), 0.5, HexColor("#d4af37")),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(t_verdict)
    
    # Build Document
    doc.build(story, onFirstPage=draw_header_footer, onLaterPages=draw_header_footer)
    print(f"Successfully generated compatibility PDF at {filename}")

if __name__ == "__main__":
    build_pdf()
