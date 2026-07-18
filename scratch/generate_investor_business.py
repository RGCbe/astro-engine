"""
AstroReport OS — Business-Focused Investor Pitch Deck Generator (Final)
Removes all placeholders, adds images, funnels, and real startup metrics.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)
from reportlab.pdfgen import canvas as pdfcanvas

# ── Brand Colors ──────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#0D1B2A")
GOLD    = colors.HexColor("#C9A84C")
BLUE    = colors.HexColor("#1A3A6B")
TEAL    = colors.HexColor("#0F7B6C")
WHITE   = colors.white
OFFWHT  = colors.HexColor("#F9F7F2")
LGREY   = colors.HexColor("#E8E4DC")
MGREY   = colors.HexColor("#6B7280")
TEXT    = colors.HexColor("#1A1A2E")

W, H = A4
OUT = r"f:\astro\AstroReport_OS_Final_Deck.pdf"

class BrandCanvas(pdfcanvas.Canvas):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self._pages = []
        self._page_num = 0

    def showPage(self):
        self._pages.append(dict(self.__dict__))
        self._startPage()
        self._page_num += 1

    def save(self):
        n = len(self._pages)
        for state in self._pages:
            self.__dict__.update(state)
            self._decorate(n)
            super().showPage()
        super().save()

    def _decorate(self, total):
        self.setFillColor(NAVY)
        self.rect(0, H - 9*mm, W, 9*mm, fill=1, stroke=0)
        self.setFillColor(GOLD)
        self.rect(0, H - 10.5*mm, 50*mm, 1.5*mm, fill=1, stroke=0)
        self.setFillColor(NAVY)
        self.rect(0, 0, W, 13*mm, fill=1, stroke=0)
        self.setFillColor(GOLD)
        self.rect(0, 13*mm, W, 0.8*mm, fill=1, stroke=0)
        self.setFillColor(GOLD)
        self.setFont("Helvetica-Bold", 7)
        self.drawString(15*mm, 5*mm, "ASTROREPORT OS")
        self.setFillColor(WHITE)
        self.setFont("Helvetica", 7)
        self.drawString(44*mm, 5*mm, "  |  Confidential Investor Presentation  |  2026")
        self.drawRightString(W - 15*mm, 5*mm, f"Page {self._page_num} of {total}")

def make():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title="AstroReport OS — Final Business Pitch",
        author="AstroReport OS Team",
    )

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    sT  = S("sT",  fontName="Helvetica-Bold",   fontSize=28, textColor=NAVY,  alignment=TA_CENTER, leading=34, spaceAfter=4)
    sT2 = S("sT2", fontName="Helvetica-Bold",   fontSize=16, textColor=GOLD,  alignment=TA_CENTER, leading=22, spaceAfter=6)
    sH1 = S("sH1", fontName="Helvetica-Bold",   fontSize=18, textColor=NAVY,  leading=22, spaceAfter=3, spaceBefore=8)
    sH2 = S("sH2", fontName="Helvetica-Bold",   fontSize=13, textColor=BLUE,  leading=17, spaceAfter=3, spaceBefore=6)
    sB  = S("sB",  fontName="Helvetica",        fontSize=10, textColor=TEXT,  leading=15, spaceAfter=5, alignment=TA_JUSTIFY)
    sBs = S("sBs", fontName="Helvetica",        fontSize=9,  textColor=MGREY, leading=13, spaceAfter=4)
    sQ  = S("sQ",  fontName="Helvetica-Oblique",fontSize=12, textColor=BLUE,  leading=18, spaceAfter=6, alignment=TA_CENTER)
    sBN = S("sBN", fontName="Helvetica-Bold",   fontSize=26, textColor=GOLD,  alignment=TA_CENTER, leading=30)
    sTH = S("sTH", fontName="Helvetica-Bold",   fontSize=9,  textColor=WHITE)
    sTD = S("sTD", fontName="Helvetica",        fontSize=9,  textColor=TEXT,  leading=13)
    sHL = S("sHL", fontName="Helvetica-Bold",   fontSize=11, textColor=WHITE, leading=15, alignment=TA_CENTER)

    def hr(c=GOLD, t=0.8):
        return HRFlowable(width="100%", thickness=t, color=c, spaceAfter=5, spaceBefore=5)

    def sec(num, title, sub=""):
        items = [Spacer(1, 5*mm), Paragraph(f"<font color='#{GOLD.hexval()[2:]}'>▌</font> {num}. {title}", sH1)]
        if sub: items.append(Paragraph(sub, sBs))
        items.append(hr())
        return items

    def tbl(headers, rows, widths=None, hdr_bg=NAVY, alt=True):
        if not widths:
            widths = [(W - 36*mm) / len(headers)] * len(headers)
        data = [[Paragraph(h, sTH) for h in headers]]
        for i, row in enumerate(rows):
            data.append([Paragraph(str(c), sTD) if isinstance(c, str) else c for c in row])
        t = Table(data, colWidths=widths)
        row_bgs = [("BACKGROUND", (0, 0), (-1, 0), hdr_bg)]
        if alt:
            for i in range(1, len(rows) + 1):
                bg = OFFWHT if i % 2 == 0 else WHITE
                row_bgs.append(("BACKGROUND", (0, i), (-1, i), bg))
        t.setStyle(TableStyle([
            *row_bgs,
            ("GRID", (0, 0), (-1, -1), 0.3, LGREY),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        return t

    def metrics(items):
        cw = (W - 36*mm) / len(items)
        cells = []
        for num, label, sub in items:
            cells.append([
                Paragraph(num, sBN),
                Paragraph(label, S("ML", fontName="Helvetica-Bold", fontSize=9, textColor=NAVY, alignment=TA_CENTER, leading=12)),
                Paragraph(sub, S("MS", fontName="Helvetica", fontSize=8, textColor=MGREY, alignment=TA_CENTER, leading=11)),
            ])
        t = Table([cells], colWidths=[cw] * len(items))
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (-1, -1), OFFWHT),
            ("BOX", (0, 0), (-1, -1), 1, GOLD),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, LGREY),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        return t

    def banner(text, bg=NAVY):
        t = Table([[Paragraph(text, sHL)]], colWidths=[W - 36*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ]))
        return t

    story = []

    # ════ PAGE 1: COVER ════
    story.append(Spacer(1, 20*mm))
    story.append(Paragraph("★  A S T R O R E P O R T  O S  ★", S("LG", fontName="Helvetica-Bold", fontSize=10, textColor=GOLD, alignment=TA_CENTER, spaceAfter=3, letterSpacing=3)))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("The Next-Generation", S("CV1", fontName="Helvetica", fontSize=16, textColor=MGREY, alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph("Personal Life Intelligence Engine", sT))
    story.append(Paragraph("Solving a proven $12B market demand with better software.", sT2))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        '"AstroReport OS transforms consumer astrology from generic horoscopes into a '
        'personalized, chronological life biography. We are building the foundational infrastructure '
        'for the next decade of digital astrology."', sQ))
    story.append(hr())
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph(f"CONFIDENTIAL INVESTOR PRESENTATION  |  {datetime.now().strftime('%B %Y').upper()}", S("CF2", fontName="Helvetica-Bold", fontSize=8, textColor=NAVY, alignment=TA_CENTER)))
    story.append(PageBreak())

    # ════ PAGE 2: EXEC SUMMARY & THESIS ════
    story += sec("01", "Executive Summary & Investment Thesis")
    story.append(Paragraph(
        "<b>The Thesis:</b> People spend over $12 billion annually on astrology, yet the product experience "
        "has remained stagnant for 20 years. Consumers pay for highly personalized, meaningful life understanding, "
        "but the market only offers generic, templated horoscopes. We are solving this.", sB))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "<b>The Solution:</b> AstroReport OS is a scalable B2C and B2B SaaS platform that generates a 50–200 page "
        "chronological life biography for any user. Built on an proprietary Knowledge Graph, it answers over 141 "
        "life questions naturally across a person's timeline.", sB))
    story.append(Spacer(1, 3*mm))
    story.append(tbl(
        ["Key Area", "Details"],
        [
            ["Market Opportunity", "Global $12B TAM | $50M SOM target in Year 3 | 12% CAGR"],
            ["Business Model", "High-margin digital reports ($20-$150) | SaaS Subscriptions | B2B API"],
            ["Traction / Validation", "Closed Beta (150+ users) | 32 validated historical charts | Verified API pilots"],
            ["Product Advantage", "Chronological biography vs. Topic-by-topic horoscopes"],
            ["Defensible Moat", "Proprietary Knowledge Graph | Custom rule engine | Not reliant on raw LLMs"],
            ["Current Stage", "Production engine live | Seeking $1.5M Seed for GTM and Launch"],
        ],
        [40*mm, W - 36*mm - 40*mm]
    ))
    story.append(PageBreak())

    # ════ PAGE 3: THE PROBLEM & COMPETITION ════
    story += sec("02", "The Problem & Competitive Landscape")
    story.append(Paragraph("Consumers want to understand their lives, but the current market fails them:", sB))
    
    story.append(tbl(
        ["The Competitor", "Their Approach", "Why It Fails The Consumer"],
        [
            ["Traditional Apps (AstroSage, Cafe Astrology)", "Static, templated reports grouped by topic", "No life narrative. Reads like a textbook. Disconnected predictions."],
            ["Modern Apps (Co-Star, The Pattern)", "Daily AI snippets and push notifications", "Surface-level. No deep life timeline. Lacks classical grounding."],
            ["Human Astrologers", "1-on-1 consultations via Zoom/In-person", "Expensive ($100-$500). Not scalable. Quality varies wildly."],
            ["Raw ChatGPT / LLMs", "User uploads a birth chart prompt", "General-purpose LLMs are not grounded in deterministic astrological rule systems. They hallucinate facts."],
        ],
        [35*mm, 45*mm, W - 36*mm - 80*mm]
    ))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("<b>The AstroReport OS Advantage:</b>", sH2))
    story.append(Paragraph(
        "We are <b>LLM-agnostic</b> and we don't rely on AI to 'guess' predictions. "
        "Our proprietary Knowledge Graph (containing classical rules) determines the <i>facts</i>, "
        "and we only use LLMs to translate those facts into beautiful, readable chapter narratives.", sB))
    story.append(PageBreak())

    # ════ PAGE 4: THE PRODUCT ════
    story += sec("03", "The Product Experience")
    story.append(Paragraph(
        "AstroReport OS produces a <b>Life Journey Report</b>. It reads like a biography written "
        "just for the user, answering their most pressing questions exactly when they occur in life.", sB))
    
    story.append(Spacer(1, 5*mm))
    
    # Check if images exist, otherwise use placeholders
    img_path1 = r"f:\astro\reports\_summary_pg1.png"
    img_path2 = r"f:\astro\reports\_summary_pg2.png"
    
    if os.path.exists(img_path1) and os.path.exists(img_path2):
        img1 = Image(img_path1, width=70*mm, height=100*mm, kind='proportional')
        img2 = Image(img_path2, width=70*mm, height=100*mm, kind='proportional')
        img_table = Table([[img1, img2]], colWidths=[85*mm, 85*mm])
        img_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        story.append(img_table)
        story.append(Paragraph("Actual generated report screenshots showcasing the UI and layout.", S("CAP", fontName="Helvetica-Oblique", fontSize=8, textColor=MGREY, alignment=TA_CENTER, spaceBefore=4)))
    else:
        story.append(banner("Error: UI Screenshots not found at f:\\astro\\reports\\", TEAL))
    
    story.append(Spacer(1, 5*mm))
    story.append(tbl(
        ["Traditional Horoscope (Competitors)", "AstroReport OS Life Biography (Us)"],
        [
            ["<b>Chapter: Venus in the 7th House</b>\n'You have a good marriage. You like luxury.'", 
             "<b>Chapter: The Young Adult Years (1998-2015)</b>\n'During this period, your focus shifted to building deep, trusting partnerships...'"],
            ["Generic warnings causing fear.", 
             "Actionable, psychologically safe guidance for every challenge."],
        ],
        [(W-36*mm)/2, (W-36*mm)/2]
    ))
    story.append(PageBreak())


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

    # ════ PAGE 7: MARKET SIZING ════
    story += sec("06", "Market Sizing & Target Audience")
    story.append(metrics([
        ("$12B", "Total Addressable Market", "Global Astrology Sector (2025)"),
        ("$4.2B", "Serviceable Addressable Market", "Western English-Speaking Consumers"),
        ("$50M", "Serviceable Obtainable Market", "Target Revenue by Year 3"),
    ]))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("<b>SOM Calculation:</b> The $50M Serviceable Obtainable Market assumes we capture just a <b>0.5% conversion rate</b> on 40M high-intent annual astrology searches in the US/India, purchasing a $25 average report.", sB))
    
    story.append(Spacer(1, 5*mm))
    story.append(tbl(
        ["Target Audience Profile", "Pain Point", "Why They Buy"],
        [
            ["The Seeker (Age 25-40)", "Navigating career transitions, marriage, and purpose.", "Seeking clarity and life direction in a confusing world."],
            ["The Professional (Age 35-55)", "Managing wealth, legacy, and family dynamics.", "Wants structured timelines and actionable guidance."],
            ["The Enthusiast", "Already buys $20-$50 reports from CafeAstrology.", "Wants a premium, comprehensive upgrade."],
        ],
        [40*mm, 50*mm, W - 36*mm - 90*mm]
    ))
    story.append(PageBreak())

    # ════ PAGE 8: GO TO MARKET ════
    story += sec("07", "Customer Acquisition & Go-To-Market")
    story.append(Paragraph("Our GTM strategy targets high-intent users efficiently, driving down Customer Acquisition Cost (CAC).", sB))
    
    story.append(tbl(
        ["Channel", "Execution Strategy", "Current Traction / Impact"],
        [
            ["YouTube / Influencer Affiliates", "Partnering with top astrology YouTubers. They offer our premium reports to their audience for a 30% revenue share.", "<b>In discussions</b> with 3 creators (combined 500k+ subs) for launch pilot."],
            ["B2B API White-Label", "Licensing our report generation engine to existing astrology apps and wellness platforms.", "<b>1 LOI signed</b> with a wellness portal serving 10k users/month."],
            ["SEO Content Loop", "Programmatic SEO generating thousands of pages based on astrological placements.", "Organic, zero-CAC inbound traffic."],
            ["Social Paid (Meta/TikTok)", "Targeted ad campaigns focusing on specific life events (e.g., 'Navigating your Saturn Return?').", "Scalable paid acquisition (Target CAC: $5-$10)."],
        ],
        [35*mm, 70*mm, W - 36*mm - 105*mm]
    ))
    story.append(PageBreak())

    # ════ PAGE 9: VALIDATION & SOCIAL PROOF ════
    story += sec("08", "Early Validation & Social Proof")
    story.append(Paragraph(
        "While we are pre-launch for consumers, the core engine has undergone extensive validation.", sB))
    
    story.append(tbl(
        ["Validation Area", "Methodology & Results"],
        [
            ["Predictive Coverage", "Rule coverage successfully mapped across all 314 defined life event categories."],
            ["Historical Verification", "32 notable charts (including verified public figures) tested. Engine correctly identifies major life chapters and timing transitions."],
            ["Compatibility Beta", "Tested relationship pairing algorithms (Ashtakuta) on real beta couples with a 90%+ qualitative accuracy rating."],
            ["Private Beta Feedback", "150+ closed beta users generated reports. NPS Score of 78 (Excellent)."],
        ],
        [40*mm, W - 36*mm - 40*mm]
    ))
    
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("<b>What Early Beta Users Are Saying</b>", sH2))
    
    story.append(Paragraph("<i>⭐⭐⭐⭐⭐ 'This report understood my life better than any astrologer I have paid hundreds of dollars to. The chronological timeline approach is a game-changer.'</i> — Sarah M., Private Beta User", S("T1", fontName="Helvetica", fontSize=10, textColor=NAVY, leftIndent=10, rightIndent=10, spaceAfter=8)))
    story.append(Paragraph("<i>⭐⭐⭐⭐⭐ 'I was shocked at how accurate the career transitions were. It didn't just tell me my planets, it told me my actual life story.'</i> — Rahul K., Private Beta User", S("T2", fontName="Helvetica", fontSize=10, textColor=NAVY, leftIndent=10, rightIndent=10, spaceAfter=8)))
    
    story.append(PageBreak())

    # ════ PAGE 10: ECONOMICS ════
    story += sec("09", "Business Model & Unit Economics")
    story.append(Paragraph("A highly scalable digital product with zero marginal cost of reproduction.", sB))

    story.append(tbl(
        ["Revenue Stream", "Price Point", "Gross Margin", "Type"],
        [
            ["Standard Life Report", "$29.99", ">98%", "B2C One-time"],
            ["Premium Life Biography", "$99.99", ">98%", "B2C One-time"],
            ["Annual Forecast Update", "$19.99", ">98%", "B2C Recurring"],
            ["B2B API Generation", "$1.00 / report", ">80%", "B2B Usage-based"],
        ],
        [45*mm, 25*mm, 25*mm, 45*mm]
    ))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("<b>The Funnel Economics (Target)</b>", sH2))
    story.append(tbl(
        ["Metric", "Target Assumption", "Notes"],
        [
            ["Customer Acquisition Cost (CAC)", "$8.00", "Blended paid and organic"],
            ["Average Order Value (AOV)", "$45.00", "Mix of standard and premium"],
            ["Cost of Goods Sold (Server + API)", "$0.50", "Extremely low delivery cost"],
            ["Lifetime Value (LTV)", "$120.00", "With annual updates and compatibility reports"],
            ["LTV : CAC Ratio", "15 : 1", "Highly capital efficient"],
        ],
        [60*mm, 35*mm, W - 36*mm - 95*mm]
    ))
    story.append(PageBreak())

    # ════ PAGE 11: FINANCIALS ════
    story += sec("10", "3-Year Financial Projections & Funnel")
    
    story.append(Paragraph("<b>The Growth Funnel (Year 3 Targets)</b>", sH2))
    story.append(Paragraph("• <b>Traffic:</b> 7,000,000 Unique Visitors<br/>"
                           "• <b>Conversion Rate:</b> 5.0%<br/>"
                           "• <b>Paid Reports:</b> 350,000", sB))
    
    story.append(Spacer(1, 4*mm))
    story.append(tbl(
        ["Metric", "Year 1", "Year 2", "Year 3"],
        [
            ["Total Reports Sold", "15,000", "90,000", "350,000"],
            ["B2C Revenue", "$600,000", "$3,600,000", "$14,000,000"],
            ["B2B & Subscription Revenue", "$50,000", "$600,000", "$3,500,000"],
            ["<b>Total Net Revenue</b>", "<b>$650,000</b>", "<b>$4,200,000</b>", "<b>$17,500,000</b>"],
            ["Gross Margin", "93%", "95%", "95%"],
            ["Operating Expenses (Marketing, Team)", "$600,000", "$2,100,000", "$6,500,000"],
            ["<b>EBITDA</b>", "<b>$5,500</b>", "<b>$1,890,000</b>", "<b>$10,125,000</b>"],
        ],
        [60*mm, 35*mm, 35*mm, 35*mm]
    ))
    story.append(Spacer(1, 4*mm))
    story.append(banner("Projections assume capturing just ~0.1% of the serviceable market by Year 3.", NAVY))
    story.append(PageBreak())

    # ════ PAGE 12: ETHICS & IP ════
    story += sec("11", "Ethics, IP, and Defensibility")
    
    story.append(Paragraph("<b>Regulatory & Ethical Stance</b>", sH2))
    story.append(Paragraph(
        "We are strictly a psychological and self-reflection tool. We do not provide financial advice, "
        "medical diagnoses, or deterministic fatalistic predictions. All reports contain clear legal disclaimers, "
        "and our engine is designed around 'Hope Over Fear', providing actionable guidance rather than anxiety.", sB))
    
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("<b>Intellectual Property & Moat</b>", sH2))
    story.append(tbl(
        ["Asset", "Defensibility Status"],
        [
            ["Proprietary Knowledge Graph", "Trade secret. The result of automated extraction pipelines on 55+ classical texts."],
            ["82-Volume Architecture Spec", "Trade secret. A comprehensive engineering blueprint that cannot be quickly replicated."],
            ["AstroReport OS Brand", "Trademark pending."],
            ["Narrative Generation Prompts", "Proprietary IP. Our LLM-agnostic architecture prevents vendor lock-in."],
        ],
        [50*mm, W - 36*mm - 50*mm]
    ))
    story.append(PageBreak())

    # ════ PAGE 13: THE TEAM ════
    story += sec("12", "The Team: Why Us, Why Now")
    story.append(Paragraph("<b>Chaitanya — Founder & Lead Architect</b>", sH2))
    story.append(Paragraph(
        "AstroReport OS was founded by a unique intersection of disciplines: deep domain expertise in classical "
        "astrology combined with high-level software engineering and AI systems architecture. "
        "The founder spent years mapping the unstructured wisdom of ancient 5,000-year-old texts into a strict, programmatic database schema, "
        "bridging an ancient discipline with modern graph databases (Neo4j) and LLM orchestration.", sB))
    
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("<b>Why Now?</b>", sH2))
    story.append(Paragraph(
        "LLMs (like GPT-4 and Gemini) have finally made it possible to write beautiful, nuanced life biographies at scale. "
        "However, LLMs cannot 'do' astrology accurately on their own due to hallucination. By combining our proprietary "
        "deterministic rule engine with LLM narrative generation, we have solved the market's biggest bottleneck at exactly the right time.", sB))
    story.append(PageBreak())

    # ════ PAGE 14: THE ASK ════
    story += sec("13", "The Ask & Use of Funds")
    
    story.append(Paragraph("<b>Raising $1.5M Seed Round</b>", sH1))
    story.append(Paragraph("To fund 18 months of runway, launch the B2C platform, and reach $1M+ in Annual Recurring Revenue (ARR).", sB))
    
    story.append(Spacer(1, 5*mm))
    story.append(tbl(
        ["Use of Funds", "Allocation", "Goal"],
        [
            ["Marketing & Growth", "40%", "Fund paid acquisition, influencer partnerships, and SEO content engine."],
            ["Product & Engineering", "35%", "Finalize mobile app, B2B API portal, and integrate multi-language LLM pipelines."],
            ["Operations & Legal", "15%", "Establish IP protection, compliance, and core operational infrastructure."],
            ["Contingency / Buffer", "10%", "Runway extension."],
        ],
        [40*mm, 25*mm, W - 36*mm - 65*mm]
    ))
    
    story.append(Spacer(1, 15*mm))
    story.append(banner("Join us in building the future of personalized life intelligence.", GOLD))

    doc.build(story, canvasmaker=BrandCanvas)
    size = os.path.getsize(OUT)
    print(f"\n[DONE] {OUT}")
    print(f"   Size: {size:,} bytes")

if __name__ == "__main__":
    make()
