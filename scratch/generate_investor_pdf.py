"""
AstroReport OS — Complete Investor Package PDF Generator
Generates a professional, full-detail investor document.
"""
import os, json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable
from reportlab.pdfgen import canvas

# ── colour palette ────────────────────────────────────────────────────────────
DEEP_NAVY   = colors.HexColor("#0B1629")
GOLD        = colors.HexColor("#D4AF37")
GOLD_LIGHT  = colors.HexColor("#F5E08A")
ACCENT_BLUE = colors.HexColor("#1A3A6B")
ACCENT_TEAL = colors.HexColor("#1B7A7A")
SOFT_WHITE  = colors.HexColor("#F8F6F0")
MID_GREY    = colors.HexColor("#6B7280")
LIGHT_GREY  = colors.HexColor("#E5E7EB")
SUCCESS     = colors.HexColor("#059669")
TEXT_DARK   = colors.HexColor("#111827")

W, H = A4   # 595.27 x 841.89 pt

OUT = r"f:\astro\AstroReport_OS_Investor_Deck.pdf"


# ── canvas-level page decorations ─────────────────────────────────────────────
class InvestorCanvas(canvas.Canvas):
    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self._saved_page_states = []
        self.page_number = 0

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
        self.page_number += 1

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self._draw_page(num_pages)
            super().showPage()
        super().save()

    def _draw_page(self, total_pages):
        # Top accent bar
        self.setFillColor(DEEP_NAVY)
        self.rect(0, H - 8*mm, W, 8*mm, fill=1, stroke=0)
        self.setFillColor(GOLD)
        self.rect(0, H - 10*mm, 40*mm, 2*mm, fill=1, stroke=0)

        # Bottom bar
        self.setFillColor(DEEP_NAVY)
        self.rect(0, 0, W, 12*mm, fill=1, stroke=0)

        # Footer text
        self.setFillColor(GOLD)
        self.setFont("Helvetica", 7)
        self.drawString(15*mm, 4*mm, "AstroReport OS  |  Confidential Investor Document  |  2026")
        self.setFillColor(colors.white)
        pn = f"Page {self.page_number} of {total_pages}"
        self.drawRightString(W - 15*mm, 4*mm, pn)


def build_pdf():
    doc = SimpleDocTemplate(
        OUT,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=22*mm, bottomMargin=20*mm,
        title="AstroReport OS — Investor Presentation",
        author="AstroReport OS",
    )

    styles = getSampleStyleSheet()

    def S(name, **kw):
        """Create a named ParagraphStyle."""
        return ParagraphStyle(name, **kw)

    # Custom styles
    H1 = S("H1", fontName="Helvetica-Bold", fontSize=26,
            textColor=DEEP_NAVY, spaceAfter=6, leading=32, alignment=TA_LEFT)
    H2 = S("H2", fontName="Helvetica-Bold", fontSize=16,
            textColor=ACCENT_BLUE, spaceAfter=4, spaceBefore=12, leading=20)
    H3 = S("H3", fontName="Helvetica-Bold", fontSize=12,
            textColor=GOLD, spaceAfter=3, spaceBefore=8, leading=15)
    BODY = S("BODY", fontName="Helvetica", fontSize=10,
             textColor=TEXT_DARK, spaceAfter=5, leading=15, alignment=TA_JUSTIFY)
    BODY_SM = S("BODYSM", fontName="Helvetica", fontSize=9,
                textColor=MID_GREY, spaceAfter=3, leading=13)
    BOLD = S("BOLD", fontName="Helvetica-Bold", fontSize=10,
             textColor=TEXT_DARK, spaceAfter=3, leading=14)
    CAPTION = S("CAPTION", fontName="Helvetica-Oblique", fontSize=8,
                textColor=MID_GREY, alignment=TA_CENTER, spaceAfter=4)
    BIG_NUM = S("BIGNUM", fontName="Helvetica-Bold", fontSize=32,
                textColor=GOLD, alignment=TA_CENTER, leading=36, spaceAfter=0)
    BIG_LBL = S("BIGLBL", fontName="Helvetica", fontSize=9,
                textColor=MID_GREY, alignment=TA_CENTER, spaceAfter=12)
    QUOTE = S("QUOTE", fontName="Helvetica-Oblique", fontSize=12,
              textColor=ACCENT_BLUE, alignment=TA_CENTER, spaceAfter=8, leading=18)
    WHITE_H = S("WHITEH", fontName="Helvetica-Bold", fontSize=13,
                textColor=colors.white, leading=17, spaceAfter=2)
    WHITE_B = S("WHITEB", fontName="Helvetica", fontSize=9,
                textColor=SOFT_WHITE, leading=13, spaceAfter=6)

    def divider():
        return HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=6, spaceBefore=6)

    def section_header(title, subtitle=""):
        els = [
            Spacer(1, 4*mm),
            Paragraph(title, H2),
        ]
        if subtitle:
            els.append(Paragraph(subtitle, BODY_SM))
        els.append(divider())
        return els

    def metric_row(metrics):
        """3-column metric banner."""
        cells = []
        for num, label in metrics:
            cells.append([
                Paragraph(num, BIG_NUM),
                Paragraph(label, BIG_LBL),
            ])
        t = Table([cells], colWidths=[W/3 - 14*mm]*3)
        t.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("BOX", (0,0), (-1,-1), 0.5, LIGHT_GREY),
            ("INNERGRID", (0,0), (-1,-1), 0.5, LIGHT_GREY),
            ("BACKGROUND", (0,0), (-1,-1), SOFT_WHITE),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ]))
        return t

    def dark_table(headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [(W - 40*mm) / len(headers)] * len(headers)
        all_rows = [[Paragraph(h, S("TH", fontName="Helvetica-Bold", fontSize=9,
                                    textColor=colors.white)) for h in headers]]
        for row in rows:
            all_rows.append([Paragraph(str(c), S("TD", fontName="Helvetica", fontSize=9,
                                                  textColor=TEXT_DARK, leading=12)) for c in row])
        t = Table(all_rows, colWidths=col_widths)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), DEEP_NAVY),
            ("BACKGROUND", (0,1), (-1,-1), colors.white),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, SOFT_WHITE]),
            ("GRID", (0,0), (-1,-1), 0.3, LIGHT_GREY),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
        ]))
        return t

    def highlight_box(text, bg=ACCENT_BLUE):
        t = Table([[Paragraph(text, S("HB", fontName="Helvetica-Bold", fontSize=10,
                                      textColor=colors.white, leading=15, alignment=TA_CENTER))]],
                  colWidths=[W - 40*mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), bg),
            ("TOPPADDING", (0,0), (-1,-1), 10),
            ("BOTTOMPADDING", (0,0), (-1,-1), 10),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
        ]))
        return t

    # ── COVER PAGE ──────────────────────────────────────────────────────────────
    story = []

    story.append(Spacer(1, 20*mm))
    story.append(Paragraph("★  ASTRO REPORT OS  ★", S("LOGO", fontName="Helvetica-Bold",
        fontSize=11, textColor=GOLD, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("The World's First", S("Cover1", fontName="Helvetica",
        fontSize=18, textColor=MID_GREY, alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph("AI-Powered Personal Life Report Engine", S("Cover2",
        fontName="Helvetica-Bold", fontSize=28, textColor=DEEP_NAVY,
        alignment=TA_CENTER, spaceAfter=4, leading=34)))
    story.append(Paragraph("Powered by 5,000+ Years of Astrological Wisdom", S("Cover3",
        fontName="Helvetica-Oblique", fontSize=13, textColor=ACCENT_TEAL,
        alignment=TA_CENTER, spaceAfter=16)))

    story.append(divider())

    story.append(Paragraph(
        '"AstroReport OS is not a prediction engine. It is a Life Operating Manual — '
        'a complete, personalized biography of a person\'s journey from birth to legacy, '
        'powered by the most comprehensive astrological knowledge base ever assembled."',
        S("CQ", fontName="Helvetica-Oblique", fontSize=11, textColor=ACCENT_BLUE,
          alignment=TA_CENTER, leading=17, spaceAfter=8)))

    story.append(divider())
    story.append(Spacer(1, 6*mm))

    # Cover metrics
    story.append(metric_row([
        ("20,849", "Classical Rules\nin Knowledge Graph"),
        ("82", "Design Specification\nVolumes"),
        ("141+", "Structured Life\nQuestions Mapped"),
    ]))
    story.append(Spacer(1, 6*mm))
    story.append(metric_row([
        ("22+", "Ancient Books\nDigitised & Indexed"),
        ("5,000+", "Years of Combined\nAstrological Wisdom"),
        ("6", "Prediction Systems\nIntegrated"),
    ]))
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph(
        f"Confidential Investor Presentation  |  {datetime.now().strftime('%B %Y')}",
        S("FOOT", fontName="Helvetica", fontSize=9, textColor=MID_GREY, alignment=TA_CENTER)))

    story.append(PageBreak())

    # ── EXECUTIVE SUMMARY ───────────────────────────────────────────────────────
    story += section_header("01. Executive Summary")
    story.append(Paragraph(
        "AstroReport OS is a proprietary AI-powered life intelligence platform that transforms "
        "a person's birth chart into a complete, personalized Life Operating Manual. Unlike "
        "traditional astrology apps that produce generic horoscopes, AstroReport OS generates "
        "a 50–200 page chronological life biography — answering over 141 structured life "
        "questions across 64 domains including career, marriage, health, wealth, children, "
        "purpose, and legacy.", BODY))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "The engine is built on the world's most comprehensive astrological knowledge base: "
        "20,849 classical rules extracted from 22+ ancient texts spanning Vedic, Hellenistic, "
        "Medieval Western, Chinese, and Numerological traditions — all cross-indexed in a "
        "Neo4j Knowledge Graph and powered by a multi-system AI reasoning engine.", BODY))
    story.append(Spacer(1, 3*mm))

    kp = [
        ["Category", "Detail"],
        ["Product", "AI-Generated Personalized Life Report (PDF/Web)"],
        ["Technology", "Neo4j KG + Multi-System Astrology Engine + LLM Narrative"],
        ["Knowledge Base", "20,849 rules from Vedic, Western, Chinese & Numerology traditions"],
        ["Report Coverage", "Birth → Childhood → Education → Career → Marriage → Legacy"],
        ["Revenue Model", "B2C Report Sales + B2B API White-Label + Subscription"],
        ["Target Market", "Global — 1.2 Billion+ active astrology consumers worldwide"],
        ["Stage", "Operational Engine + KG Live on VPS — Revenue-Ready"],
    ]
    story.append(dark_table(kp[0], kp[1:], [60*mm, 100*mm]))
    story.append(PageBreak())

    # ── THE PROBLEM ─────────────────────────────────────────────────────────────
    story += section_header("02. The Problem", "What the current market fails to deliver")
    story.append(Paragraph(
        "The global astrology market exceeds <b>$12 billion annually</b> and is growing at "
        "12% CAGR. Yet every existing product — from apps to PDF reports to live consultations "
        "— shares the same fundamental failure:", BODY))
    story.append(Spacer(1, 3*mm))

    problems = [
        ["❌ Problem", "Impact on User"],
        ["Generic, templated output — not personalized", "Users don't recognize themselves"],
        ["Topic-by-topic reports (career section, marriage section)", "No coherent life story"],
        ["Single tradition only (Vedic OR Western)", "Incomplete picture"],
        ["Predictions without explanation or guidance", "Fear, confusion, no action"],
        ["No timeline — just static planetary positions", "Can't relate to their actual life"],
        ["Expensive consultations required for depth", "Not scalable, not accessible"],
    ]
    story.append(dark_table(problems[0], problems[1:], [100*mm, 60*mm]))
    story.append(Spacer(1, 4*mm))
    story.append(highlight_box(
        "The world's 1.2 billion astrology consumers deserve a product that actually "
        "explains their life — not just their planets.", ACCENT_TEAL))
    story.append(PageBreak())

    # ── THE SOLUTION ────────────────────────────────────────────────────────────
    story += section_header("03. The Solution — AstroReport OS")
    story.append(Paragraph(
        "AstroReport OS is built on 21 core design principles that transform astrology from "
        "prediction into life understanding. The output is not an astrology report — it is a "
        "<b>Life Journey Report</b> structured as a continuous biography from birth to legacy.", BODY))
    story.append(Spacer(1, 4*mm))

    principles = [
        ["Principle", "What It Means"],
        ["Human First", "Describe the human experience before the astrological reason"],
        ["Timeline Structure", "Organized by Dasha/Bhukti life chapters — not topics"],
        ["Continuous Biography", "Each chapter flows into the next like a novel"],
        ["141+ Life Questions Answered", "Career, wealth, marriage, health, purpose — all covered"],
        ["Hope Over Fear", "Every challenge paired with practical guidance"],
        ["Multi-System Fusion", "Vedic + Western + Chinese + Numerology + Nadi in one report"],
        ["Knowledge Graph Powered", "20,849 rules queried per chart for evidence-based output"],
        ["Explainable AI", "Every interpretation is traceable to specific classical rules"],
    ]
    story.append(dark_table(principles[0], principles[1:], [70*mm, 90*mm]))
    story.append(PageBreak())

    # ── TECHNOLOGY ARCHITECTURE ─────────────────────────────────────────────────
    story += section_header("04. Technology Architecture")
    story.append(Paragraph(
        "AstroReport OS is a full-stack AI system with seven integrated layers:", BODY))
    story.append(Spacer(1, 4*mm))

    arch = [
        ["Layer", "Component", "Technology"],
        ["1 — Data", "Ephemeris + Chart Engine", "Swiss Ephemeris + Python"],
        ["2 — Knowledge", "Neo4j Knowledge Graph", "20,849 rules + 141 Q-nodes"],
        ["3 — Reasoning", "Multi-System Astrology Engine", "Vedic + Western + Chinese + Nadi"],
        ["4 — Evidence", "Evidence Weighting Engine", "Confidence scoring + conflict resolution"],
        ["5 — Timeline", "Dasha/Bhukti Timeline Engine", "Mahadasha → Bhukti → Antardasha"],
        ["6 — Narrative", "LLM Report Generator", "Structured prompt → chapter → biography"],
        ["7 — Output", "Report Rendering Engine", "PDF/HTML/API — multi-format delivery"],
    ]
    story.append(dark_table(arch[0], arch[1:], [35*mm, 70*mm, 55*mm]))

    story.append(Spacer(1, 5*mm))
    story += section_header("Prediction Systems Integrated")

    systems = [
        ["System", "Origin", "Specialization", "Rules in KG"],
        ["Vedic / Parashari", "India (3000+ BCE)", "Houses, Dashas, Yogas, Dignity", "9,800+"],
        ["Jaimini Astrology", "India (1500+ BCE)", "Karakas, Chara Dasha, Arudha", "1,200+"],
        ["KP System", "India (Modern)", "Horary, Cuspal Sub-Lords", "350+"],
        ["Nadi Astrology", "Tamil Nadu (Ancient)", "Degree-specific predictions", "3,200+"],
        ["Hellenistic Western", "Greece/Rome (200 BCE)", "Zodiacal Releasing, Profections", "1,800+"],
        ["Medieval Western", "Europe (1100-1700 CE)", "Considerations, Dignities", "1,400+"],
        ["Numerology", "Global", "Life Path, Name numbers", "370+"],
        ["Chinese BaZi", "China (600+ CE)", "Four Pillars of Destiny", "400+"],
    ]
    story.append(dark_table(systems[0], systems[1:], [40*mm, 40*mm, 55*mm, 25*mm]))
    story.append(PageBreak())

    # ── KNOWLEDGE BASE ──────────────────────────────────────────────────────────
    story += section_header("05. The Knowledge Base — Unmatched Depth")
    story.append(Paragraph(
        "The AstroReport OS Knowledge Base is the most comprehensive machine-readable "
        "astrological corpus ever assembled. Over 22 ancient and classical texts have been "
        "digitised, OCR-processed, rule-extracted and cross-indexed:", BODY))
    story.append(Spacer(1, 4*mm))

    books = [
        ["Text", "Origin", "Rules Extracted", "Specialization"],
        ["Brihat Parashara Hora Sastra", "India, ~600 BCE", "4,200+", "Core Vedic foundation"],
        ["Chandra Kala Nadi (Santhanam)", "Tamil Nadu", "3,129", "Degree-specific Nadi rules"],
        ["Jaimini Sutras", "India, ~1500 BCE", "1,800+", "Chara Dasha, Karakas"],
        ["Tetrabiblos (Ptolemy)", "Alexandria, ~150 CE", "1,059", "Western chart interpretation"],
        ["Vettius Valens (Anthology)", "Rome, ~160 CE", "418", "Zodiacal Releasing, Profections"],
        ["Christian Astrology (Lilly)", "England, 1647", "380", "Horary, Medieval methods"],
        ["Carmen Astrologicum (Dorotheus)", "Sidon, ~75 CE", "41", "Triplicity rulers, Elections"],
        ["Firmicus Maternus (Matheseos)", "Rome, ~330 CE", "56", "Planet delineations"],
        ["Mansagari", "India, Medieval", "24", "D-9 Navamsa, Vimshottari"],
        ["KP Readers 1–6", "India, Modern", "350+", "Cuspal sub-lord system"],
        ["Lal Kitab (1952 Original)", "India, 1952", "280+", "Remedial astrology"],
        ["Cheiro's Book of Numbers", "Western, 1897", "118", "Numerology, Name analysis"],
        ["+ 10 More Classical Texts", "Various", "3,000+", "Cross-validation sources"],
    ]
    story.append(dark_table(books[0], books[1:], [60*mm, 35*mm, 30*mm, 35*mm]))
    story.append(PageBreak())

    # ── PRODUCT ──────────────────────────────────────────────────────────────────
    story += section_header("06. The Product — What Users Receive")
    story.append(Paragraph(
        "Every AstroReport OS report is a complete, personalized life biography structured "
        "chronologically from birth to legacy. Each chapter is powered by the Knowledge Graph "
        "and answers specific life questions within the natural flow of time:", BODY))
    story.append(Spacer(1, 4*mm))

    chapters = [
        ["Report Chapter", "Life Stage", "Life Questions Answered"],
        ["Foundation & Identity", "Birth", "Who am I? What are my strengths? How do people see me?"],
        ["Childhood & Family", "0–12 yrs", "How did family shape me? What patterns began at home?"],
        ["Education & Intelligence", "12–18 yrs", "How do I learn? Which fields suit me best?"],
        ["Career & Purpose", "18–35 yrs", "What career suits me? Will I be self-employed? Will I lead?"],
        ["Love & Marriage", "20–40 yrs", "What qualities suit my partner? When is marriage indicated?"],
        ["Wealth & Business", "25–55 yrs", "How do I build wealth? Is business suitable for me?"],
        ["Children & Family", "28–50 yrs", "What kind of parent will I be? What legacy do I leave?"],
        ["Health & Lifestyle", "All life", "How do I maintain health? How do I manage stress?"],
        ["Purpose & Spirituality", "35+ yrs", "What is my life purpose? What spiritual path suits me?"],
        ["Wisdom & Legacy", "55+ yrs", "How do I mentor others? What is my life contribution?"],
    ]
    story.append(dark_table(chapters[0], chapters[1:], [50*mm, 25*mm, 85*mm]))
    story.append(Spacer(1, 4*mm))
    story.append(highlight_box(
        "Each report answers 141+ structured life questions  |  "
        "Covers all 12 houses + 9 planets + 27 Nakshatras + Dasha timeline  |  "
        "Delivered as a 50–200 page personalized PDF", DEEP_NAVY))
    story.append(PageBreak())

    # ── MARKET OPPORTUNITY ───────────────────────────────────────────────────────
    story += section_header("07. Market Opportunity")
    story.append(Spacer(1, 2*mm))
    story.append(metric_row([
        ("$12B+", "Global Astrology Market\n(2025, growing 12% CAGR)"),
        ("1.2B+", "Active Astrology Consumers\nWorldwide"),
        ("$4.99–$149", "Per-Report Price Range\n(High Margin Digital Product)"),
    ]))
    story.append(Spacer(1, 5*mm))

    segments = [
        ["Market Segment", "Size", "Revenue Model", "Priority"],
        ["India — Vedic Astrology (Tamil, Hindi, English)", "$3.8B", "B2C Reports + Subscription", "Primary"],
        ["Global — Western Astrology (English)", "$4.2B", "B2C + API White-Label", "Primary"],
        ["Chinese — BaZi / Four Pillars", "$1.8B", "B2C + White-Label", "Secondary"],
        ["B2B — Astrologer Software + API", "$850M", "SaaS API Licensing", "Secondary"],
        ["Enterprise — HR, Wellness, Life Coaching", "$750M", "B2B Enterprise API", "Tertiary"],
    ]
    story.append(dark_table(segments[0], segments[1:], [65*mm, 20*mm, 55*mm, 20*mm]))
    story.append(Spacer(1, 4*mm))

    story += section_header("Competitive Landscape")
    comp = [
        ["Competitor", "Offering", "Weakness vs AstroReport OS"],
        ["AstroSage / Jagannatha Hora", "Chart calculation + basic reports", "No KG, no biography, single system"],
        ["Cafe Astrology / Astro.com", "Western chart reports", "Static templates, no timeline, no Vedic"],
        ["Co-Star / The Pattern", "Daily AI horoscopes", "Surface level, no depth, no life questions"],
        ["Nadi Astrologers (manual)", "In-person Nadi leaf readings", "Not scalable, expensive, not digital"],
        ["AstroReport OS", "Complete AI Life Biography", "ALL systems + 20,849 rules + 141 Q-nodes"],
    ]
    story.append(dark_table(comp[0], comp[1:], [55*mm, 55*mm, 50*mm]))
    story.append(PageBreak())

    # ── BUSINESS MODEL ───────────────────────────────────────────────────────────
    story += section_header("08. Business Model & Revenue Streams")

    rev = [
        ["Revenue Stream", "Model", "Price Point", "Target Scale"],
        ["Basic Life Report (PDF)", "One-time purchase", "$4.99 – $19.99", "Mass market"],
        ["Complete Life Biography", "One-time purchase", "$49.99 – $149", "Premium segment"],
        ["Annual Subscription", "Recurring SaaS", "$9.99 – $29.99/mo", "Loyalty + updates"],
        ["Compatibility Report", "One-time purchase", "$29.99 – $79.99", "Couples + families"],
        ["Annual Forecast Report", "Annual purchase", "$19.99 – $49.99", "Returning customers"],
        ["API White-Label (B2B)", "Per-report API fee", "$0.50 – $2.00/report", "Astrology platforms"],
        ["Enterprise License", "Annual SaaS contract", "$5,000 – $50,000/yr", "Corporates, HR, Wellness"],
        ["Astrologer Pro Platform", "Monthly SaaS", "$49 – $199/mo", "Professional astrologers"],
    ]
    story.append(dark_table(rev[0], rev[1:], [55*mm, 35*mm, 35*mm, 35*mm]))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("Unit Economics", H3))
    econ = [
        ["Metric", "Value"],
        ["Cost to generate one complete report (AI + infrastructure)", "< $0.50"],
        ["Gross margin on $49.99 report", ">99%"],
        ["Report generation time", "< 3 minutes"],
        ["Reports per server per day (current capacity)", "500+"],
        ["Customer Acquisition Cost target (digital marketing)", "$2 – $8"],
        ["Estimated LTV per customer (multi-report + subscription)", "$75 – $200"],
    ]
    story.append(dark_table(econ[0], econ[1:], [110*mm, 50*mm]))
    story.append(PageBreak())

    # ── CURRENT STATUS ───────────────────────────────────────────────────────────
    story += section_header("09. Current Status — What Has Been Built")
    story.append(Paragraph(
        "AstroReport OS is not a concept. The core engine, knowledge base, and infrastructure "
        "are fully operational:", BODY))
    story.append(Spacer(1, 4*mm))

    built = [
        ["Component", "Status", "Detail"],
        ["Multi-System Astrology Engine", "✅ LIVE", "Vedic, KP, Western, Chinese, Nadi, Numerology"],
        ["Neo4j Knowledge Graph", "✅ LIVE", "20,849 rules + 141 Q-nodes + 967 categories"],
        ["Book Corpus (22+ Texts)", "✅ COMPLETE", "OCR + rule extraction + deduplication pipeline"],
        ["82-Volume Design Specification", "✅ COMPLETE", "Complete OS architecture documented"],
        ["Timeline / Dasha Engine", "✅ LIVE", "Mahadasha + Bhukti + Antardasha sequencing"],
        ["Chart Calculation Engine", "✅ LIVE", "Swiss Ephemeris, D1-D60 divisional charts"],
        ["Report Generation (PDF)", "✅ LIVE", "Tamil + English reports generating"],
        ["VPS Production Server", "✅ LIVE", "PM2-managed, 24/7 uptime"],
        ["Weight Optimizer (ML)", "✅ BUILT", "Calibrating accuracy against verified charts"],
        ["Compatibility Engine", "✅ BUILT", "Compatibility scoring + narrative reports"],
        ["API Layer", "🔧 IN PROGRESS", "REST API for B2B white-label delivery"],
        ["LLM Narrative Integration", "🔧 IN PROGRESS", "Full chapter biography generation"],
        ["Mobile Frontend", "📋 PLANNED", "iOS + Android apps"],
        ["Multi-Language Support", "📋 PLANNED", "Tamil, Hindi, Malayalam, Arabic, Chinese"],
    ]
    story.append(dark_table(built[0], built[1:], [65*mm, 25*mm, 70*mm]))
    story.append(PageBreak())

    # ── 82-VOLUME BLUEPRINT ──────────────────────────────────────────────────────
    story += section_header("10. The 82-Volume OS Design Specification")
    story.append(Paragraph(
        "One of the most significant assets of AstroReport OS is its <b>82-Volume Design "
        "Specification</b> — a complete engineering blueprint covering every component of "
        "the system. This represents years of architectural work and defines exactly how every "
        "engine, knowledge base, and report component must function:", BODY))
    story.append(Spacer(1, 4*mm))

    vols = [
        ["Volume Series", "Volumes", "Content"],
        ["OS Core Specification (V1)", "1–15, 10A–10Q", "Vision, Life Ontology, Timeline Engine, 1,000+ Q-Catalog, Report Engine Architecture"],
        ["Implementation Series (V2)", "16–25", "Planet/House/Yoga/Dasha/Transit Interpretation Manuals, NLG Writing Guide, QA Manual"],
        ["Knowledge Encyclopedia (V3)", "27–35", "Rashi, Varga, Aspects, Strength, Doshas, Event Prediction, Master Unified Rulebook"],
        ["Data Specification (V4)", "36–53", "Complete DB schemas for Planets, Houses, Nakshatras, Yogas, Dashas, Timeline, Reports"],
        ["Production Platform (V5)", "54–66", "Report Library, Benchmarks, AI Architecture, Security, Multi-Language, Voice, Visual"],
    ]
    story.append(dark_table(vols[0], vols[1:], [50*mm, 30*mm, 80*mm]))
    story.append(Spacer(1, 4*mm))
    story.append(highlight_box(
        "This 82-volume specification is a proprietary, defensible moat — "
        "it took years to build and cannot be replicated quickly by any competitor.", ACCENT_TEAL))
    story.append(PageBreak())

    # ── ROADMAP ──────────────────────────────────────────────────────────────────
    story += section_header("11. Product Roadmap — 18 Months")

    roadmap = [
        ["Phase", "Timeline", "Milestones"],
        ["Phase 1 — LLM Integration", "Q3 2026 (Now)", "Full chapter biography via LLM | English + Tamil reports | API v1 launch"],
        ["Phase 2 — Market Launch", "Q4 2026", "B2C website + payment gateway | 1,000 paid reports | Astrologer Pro platform"],
        ["Phase 3 — Scale", "Q1 2027", "Hindi + Malayalam + Arabic languages | Mobile app | B2B API partnerships"],
        ["Phase 4 — Enterprise", "Q2 2027", "Corporate wellness + HR integration | White-label platform | 10,000 reports/month"],
        ["Phase 5 — Global", "Q3 2027", "Chinese + Spanish markets | Voice reports | Visual timeline infographics"],
    ]
    story.append(dark_table(roadmap[0], roadmap[1:], [35*mm, 30*mm, 95*mm]))
    story.append(PageBreak())

    # ── FINANCIAL PROJECTIONS ───────────────────────────────────────────────────
    story += section_header("12. Financial Projections (3-Year)")
    story.append(Paragraph(
        "Conservative projections based on 1% penetration of addressable market segments:", BODY))
    story.append(Spacer(1, 4*mm))

    fin = [
        ["Metric", "Year 1 (2026–27)", "Year 2 (2027–28)", "Year 3 (2028–29)"],
        ["B2C Reports Sold", "10,000", "80,000", "400,000"],
        ["Average Revenue / Report", "$25", "$30", "$35"],
        ["B2C Revenue", "$250,000", "$2,400,000", "$14,000,000"],
        ["B2B API Revenue", "$50,000", "$500,000", "$3,000,000"],
        ["Subscription Revenue", "$20,000", "$300,000", "$2,000,000"],
        ["Total Revenue", "$320,000", "$3,200,000", "$19,000,000"],
        ["Gross Margin", "90%+", "90%+", "90%+"],
        ["Operating Costs", "$180,000", "$900,000", "$4,500,000"],
        ["EBITDA", "$140,000+", "$2,300,000+", "$14,500,000+"],
    ]
    story.append(dark_table(fin[0], fin[1:], [50*mm, 40*mm, 40*mm, 40*mm]))
    story.append(PageBreak())

    # ── INVESTMENT ASK ───────────────────────────────────────────────────────────
    story += section_header("13. Investment Ask & Use of Funds")
    story.append(Paragraph(
        "We are seeking <b>seed investment</b> to accelerate LLM integration, launch the "
        "B2C platform, and scale to 10,000 reports/month within 12 months:", BODY))
    story.append(Spacer(1, 4*mm))

    funds = [
        ["Use of Funds", "Allocation", "Purpose"],
        ["LLM API + Infrastructure", "30%", "GPT-4/Gemini integration for chapter generation"],
        ["Product Development", "25%", "API, mobile app, multi-language, payment gateway"],
        ["Marketing & Acquisition", "25%", "Digital marketing, SEO, influencer, astrologer partnerships"],
        ["Team Expansion", "15%", "Engineers, content, customer success"],
        ["Operations & Legal", "5%", "Company setup, IP protection, compliance"],
    ]
    story.append(dark_table(funds[0], funds[1:], [60*mm, 25*mm, 75*mm]))
    story.append(Spacer(1, 5*mm))

    story.append(highlight_box(
        "The engine, knowledge base, and 82-volume specification are already built. "
        "Investment accelerates launch — not development of the core product.", GOLD))
    story.append(PageBreak())

    # ── MOAT & IP ────────────────────────────────────────────────────────────────
    story += section_header("14. Defensible Moat & Intellectual Property")

    moat = [
        ["Asset", "Description", "Defensibility"],
        ["20,849-Rule Knowledge Graph", "World's largest machine-readable astrological corpus", "High — years to replicate"],
        ["82-Volume OS Specification", "Complete engineering blueprint for life report AI", "High — proprietary architecture"],
        ["Multi-System Fusion Engine", "6 traditions unified in one reasoning engine", "High — unique integration"],
        ["141+ Question Catalog", "Structured life ontology mapped to astrological evidence", "Medium — expanding continuously"],
        ["OCR + Extraction Pipeline", "Automated classical text digitisation system", "Medium — unique corpus access"],
        ["Optimizer + Calibration System", "Weight calibration against verified historical charts", "High — improves with data"],
        ["Report Design Language", "21-principle life biography narrative standard", "Medium — brand + quality moat"],
    ]
    story.append(dark_table(moat[0], moat[1:], [55*mm, 70*mm, 35*mm]))
    story.append(PageBreak())

    # ── WHY NOW ──────────────────────────────────────────────────────────────────
    story += section_header("15. Why Now — The Perfect Convergence")

    story.append(Paragraph(
        "Three global forces have converged to make AstroReport OS timely, necessary, and "
        "commercially dominant:", BODY))
    story.append(Spacer(1, 3*mm))

    why = [
        ["Force", "Evidence", "Our Advantage"],
        ["AI Maturity (LLMs)", "GPT-4 / Gemini can now write coherent, nuanced life narratives", "Engine + KG already built — just connect LLM"],
        ["Astrology Resurgence", "Co-Star 20M users; $12B market growing at 12% CAGR", "Deepest knowledge base in existence"],
        ["Digital Report Demand", "Personalization economy — consumers pay for meaningful content", "Our reports are genuinely unique per person"],
        ["Knowledge Graph Tech", "Neo4j + graph reasoning now enterprise-grade and fast", "20,849-rule KG already live"],
        ["Classical Text Access", "Archive.org + OCR technology enables ancient text digitization", "22+ books already processed"],
    ]
    story.append(dark_table(why[0], why[1:], [35*mm, 75*mm, 50*mm]))
    story.append(Spacer(1, 5*mm))
    story.append(highlight_box(
        "The timing is perfect. The engine is ready. The knowledge is indexed. "
        "The market is hungry. All that remains is to launch.", DEEP_NAVY))
    story.append(PageBreak())

    # ── CLOSING ──────────────────────────────────────────────────────────────────
    story += section_header("16. Closing Statement")
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph(
        '"For 5,000 years, human beings have looked at the stars to understand their lives. '
        'For the first time in history, we have built the technology to actually answer their '
        'questions — systematically, personally, and at scale. AstroReport OS is not an '
        'astrology app. It is the world\'s first AI-powered life intelligence engine, built on '
        'the world\'s most complete astrological knowledge base, delivering personalized life '
        'understanding to every human being on Earth."',
        S("CLOSE", fontName="Helvetica-Oblique", fontSize=13, textColor=ACCENT_BLUE,
          alignment=TA_CENTER, leading=20, spaceAfter=12)))

    story.append(Spacer(1, 8*mm))
    story.append(divider())
    story.append(Spacer(1, 4*mm))

    story.append(metric_row([
        ("20,849", "Rules in\nKnowledge Graph"),
        ("82", "Design\nVolumes"),
        ("∞", "Lives That Can\nBe Understood"),
    ]))

    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("AstroReport OS", S("CL1", fontName="Helvetica-Bold", fontSize=18,
        textColor=DEEP_NAVY, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph("The World's First AI-Powered Personal Life Report Engine",
        S("CL2", fontName="Helvetica", fontSize=11, textColor=MID_GREY, alignment=TA_CENTER,
          spaceAfter=8)))
    story.append(Paragraph(
        f"Confidential  |  {datetime.now().strftime('%B %Y')}  |  All Rights Reserved",
        S("CL3", fontName="Helvetica", fontSize=8, textColor=MID_GREY, alignment=TA_CENTER)))

    # ── BUILD ───────────────────────────────────────────────────────────────────
    doc.build(story, canvasmaker=InvestorCanvas)
    print(f"[DONE] PDF generated: {OUT}")
    size = os.path.getsize(OUT)
    print(f"File size: {size:,} bytes ({size//1024} KB)")

if __name__ == "__main__":
    build_pdf()
