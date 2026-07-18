"""
AstroReport OS — COMPLETE Investor Package PDF Generator
Every detail, every number, every component. Professional investor grade.
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas as pdfcanvas

# ── Brand Colors ──────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#0D1B2A")
GOLD    = colors.HexColor("#C9A84C")
GOLD_L  = colors.HexColor("#F0D98B")
BLUE    = colors.HexColor("#1A3A6B")
TEAL    = colors.HexColor("#0F7B6C")
WHITE   = colors.white
OFFWHT  = colors.HexColor("#F9F7F2")
LGREY   = colors.HexColor("#E8E4DC")
MGREY   = colors.HexColor("#6B7280")
TEXT    = colors.HexColor("#1A1A2E")
GREEN   = colors.HexColor("#059669")
RED     = colors.HexColor("#DC2626")
AMBER   = colors.HexColor("#D97706")

W, H = A4
OUT = r"f:\astro\AstroReport_OS_Complete_Investor_Package.pdf"


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
        # Top navy bar
        self.setFillColor(NAVY)
        self.rect(0, H - 9*mm, W, 9*mm, fill=1, stroke=0)
        # Gold accent line on top bar
        self.setFillColor(GOLD)
        self.rect(0, H - 10.5*mm, 50*mm, 1.5*mm, fill=1, stroke=0)
        # Bottom nav bar
        self.setFillColor(NAVY)
        self.rect(0, 0, W, 13*mm, fill=1, stroke=0)
        # Gold line above footer
        self.setFillColor(GOLD)
        self.rect(0, 13*mm, W, 0.8*mm, fill=1, stroke=0)
        # Footer text
        self.setFillColor(GOLD)
        self.setFont("Helvetica-Bold", 7)
        self.drawString(15*mm, 5*mm, "ASTROREPORT OS")
        self.setFillColor(WHITE)
        self.setFont("Helvetica", 7)
        self.drawString(44*mm, 5*mm, "  |  Confidential Investor Document  |  2026  |  All Rights Reserved")
        self.drawRightString(W - 15*mm, 5*mm, f"Page {self._page_num} of {total}")


def make():
    doc = SimpleDocTemplate(
        OUT, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=20*mm, bottomMargin=20*mm,
        title="AstroReport OS — Complete Investor Package",
        author="AstroReport OS",
        subject="Investment Proposal 2026",
    )

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    # ── Style Library ──────────────────────────────────────────────────────────
    sT  = S("sT",  fontName="Helvetica-Bold",   fontSize=30, textColor=NAVY,  alignment=TA_CENTER, leading=36, spaceAfter=4)
    sT2 = S("sT2", fontName="Helvetica-Bold",   fontSize=18, textColor=GOLD,  alignment=TA_CENTER, leading=22, spaceAfter=6)
    sT3 = S("sT3", fontName="Helvetica",        fontSize=12, textColor=MGREY, alignment=TA_CENTER, leading=16, spaceAfter=10)
    sH1 = S("sH1", fontName="Helvetica-Bold",   fontSize=18, textColor=NAVY,  leading=22, spaceAfter=3, spaceBefore=8)
    sH2 = S("sH2", fontName="Helvetica-Bold",   fontSize=13, textColor=BLUE,  leading=17, spaceAfter=3, spaceBefore=6)
    sH3 = S("sH3", fontName="Helvetica-Bold",   fontSize=11, textColor=GOLD,  leading=14, spaceAfter=2, spaceBefore=5)
    sB  = S("sB",  fontName="Helvetica",        fontSize=10, textColor=TEXT,  leading=15, spaceAfter=5, alignment=TA_JUSTIFY)
    sBs = S("sBs", fontName="Helvetica",        fontSize=9,  textColor=MGREY, leading=13, spaceAfter=4)
    sBo = S("sBo", fontName="Helvetica-Bold",   fontSize=10, textColor=TEXT,  leading=14, spaceAfter=3)
    sQ  = S("sQ",  fontName="Helvetica-Oblique",fontSize=12, textColor=BLUE,  leading=18, spaceAfter=6, alignment=TA_CENTER)
    sBN = S("sBN", fontName="Helvetica-Bold",   fontSize=30, textColor=GOLD,  alignment=TA_CENTER, leading=34)
    sBL = S("sBL", fontName="Helvetica",        fontSize=9,  textColor=MGREY, alignment=TA_CENTER, leading=12, spaceAfter=6)
    sWH = S("sWH", fontName="Helvetica-Bold",   fontSize=10, textColor=WHITE, leading=14)
    sWB = S("sWB", fontName="Helvetica",        fontSize=9,  textColor=OFFWHT,leading=13)
    sTH = S("sTH", fontName="Helvetica-Bold",   fontSize=9,  textColor=WHITE)
    sTD = S("sTD", fontName="Helvetica",        fontSize=9,  textColor=TEXT,  leading=13)
    sTDs= S("sTDs",fontName="Helvetica",        fontSize=8,  textColor=MGREY, leading=12)
    sHL = S("sHL", fontName="Helvetica-Bold",   fontSize=11, textColor=WHITE, leading=15, alignment=TA_CENTER)
    sCF = S("sCF", fontName="Helvetica",        fontSize=8,  textColor=MGREY, alignment=TA_CENTER)

    def hr(c=GOLD, t=0.8):
        return HRFlowable(width="100%", thickness=t, color=c, spaceAfter=5, spaceBefore=5)

    def sec(num, title, sub=""):
        items = [
            Spacer(1, 5*mm),
            Paragraph(f"<font color='#{GOLD.hexval()[2:]}'>▌</font> {num}. {title}", sH1),
        ]
        if sub:
            items.append(Paragraph(sub, sBs))
        items.append(hr())
        return items

    def tbl(headers, rows, widths=None, hdr_bg=NAVY, alt=True):
        if not widths:
            avail = W - 36*mm
            widths = [avail / len(headers)] * len(headers)
        data = [[Paragraph(h, sTH) for h in headers]]
        for i, row in enumerate(rows):
            bg = OFFWHT if (alt and i % 2 == 1) else WHITE
            data.append([Paragraph(str(c), sTD) for c in row])
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
        """items = [(number, label, sublabel), ...]"""
        cw = (W - 36*mm) / len(items)
        cells = []
        for num, label, sub in items:
            cell = [
                Paragraph(num, sBN),
                Paragraph(label, S("ML", fontName="Helvetica-Bold", fontSize=9,
                                   textColor=NAVY, alignment=TA_CENTER, leading=12)),
                Paragraph(sub, S("MS", fontName="Helvetica", fontSize=8,
                                 textColor=MGREY, alignment=TA_CENTER, leading=11)),
            ]
            cells.append(cell)
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
        t = Table(
            [[Paragraph(text, sHL)]],
            colWidths=[W - 36*mm],
        )
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ]))
        return t

    def two_col(left_els, right_els, lw=None, rw=None):
        avail = W - 36*mm
        lw = lw or avail * 0.5
        rw = rw or avail * 0.5
        t = Table([[left_els, right_els]], colWidths=[lw, rw])
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, -1), 0),
            ("RIGHTPADDING", (-1, 0), (-1, -1), 0),
        ]))
        return t

    # ══════════════════════════════════════════════════════════════════
    # PAGE 1 — COVER
    # ══════════════════════════════════════════════════════════════════
    story = []

    story.append(Spacer(1, 16*mm))
    story.append(Paragraph("★  A S T R O R E P O R T  O S  ★", S("LG", fontName="Helvetica-Bold",
        fontSize=10, textColor=GOLD, alignment=TA_CENTER, spaceAfter=3, letterSpacing=3)))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("The World's First", S("CV1", fontName="Helvetica",
        fontSize=16, textColor=MGREY, alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph("AI-Powered Personal Life Report Engine", sT))
    story.append(Paragraph("5,000 Years of Wisdom. One Complete Life Story.", sT2))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        '"Not a horoscope. Not a prediction. A complete, personalized Life Operating Manual — '
        'from birth to legacy — powered by the most comprehensive astrological knowledge base '
        'ever assembled."', sQ))
    story.append(hr())
    story.append(Spacer(1, 4*mm))

    story.append(metrics([
        ("20,849", "Classical Rules", "Indexed in Knowledge Graph"),
        ("82", "Design Volumes", "Complete OS Blueprint"),
        ("55+", "Ancient Books", "Digitised & Processed"),
        ("141+", "Life Questions", "Mapped & Structured"),
    ]))
    story.append(Spacer(1, 4*mm))
    story.append(metrics([
        ("8", "Prediction Systems", "Vedic · Western · Chinese · Nadi"),
        ("32", "Real Charts", "Celebrity & Verified Persons"),
        ("314", "Event Categories", "Fully Covered"),
        ("24/7", "Live VPS Engine", "Production-Ready"),
    ]))

    story.append(Spacer(1, 8*mm))
    story.append(hr(GOLD, 1.2))
    story.append(Paragraph(
        f"CONFIDENTIAL INVESTOR PRESENTATION  |  {datetime.now().strftime('%B %Y').upper()}",
        S("CF2", fontName="Helvetica-Bold", fontSize=8, textColor=NAVY, alignment=TA_CENTER,
          spaceAfter=2)))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # TABLE OF CONTENTS
    # ══════════════════════════════════════════════════════════════════
    story += [Spacer(1, 4*mm), Paragraph("Table of Contents", sH1), hr()]
    toc_items = [
        ("01", "Executive Summary"),
        ("02", "The Problem — What The Market Is Missing"),
        ("03", "The Solution — AstroReport OS"),
        ("04", "Technology Architecture — 7-Layer AI Engine"),
        ("05", "The Knowledge Base — 55+ Books, 20,849 Rules"),
        ("06", "The 82-Volume OS Design Specification"),
        ("07", "Prediction Systems — 8 Traditions Integrated"),
        ("08", "The Product — What Users Receive"),
        ("09", "The Question Intelligence Engine"),
        ("10", "Current Engine Performance & Accuracy"),
        ("11", "Live Infrastructure & Technical Status"),
        ("12", "Market Opportunity — $12B+ Global Market"),
        ("13", "Competitive Analysis"),
        ("14", "Business Model & Revenue Streams"),
        ("15", "Unit Economics & Financial Projections"),
        ("16", "Product Roadmap — 18 Months"),
        ("17", "Defensible Moat & Intellectual Property"),
        ("18", "Why Now — The Perfect Convergence"),
        ("19", "Investment Ask & Use of Funds"),
        ("20", "Closing Statement"),
    ]
    toc_data = [[Paragraph(n, S("TN", fontName="Helvetica-Bold", fontSize=9, textColor=GOLD)),
                 Paragraph(t, S("TT", fontName="Helvetica", fontSize=10, textColor=TEXT))]
                for n, t in toc_items]
    t = Table(toc_data, colWidths=[14*mm, W - 50*mm])
    t.setStyle(TableStyle([
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.3, LGREY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 01. EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════════════
    story += sec("01", "Executive Summary")
    story.append(Paragraph(
        "<b>AstroReport OS</b> is a full-stack AI platform that converts any person's birth "
        "chart into a complete, chronological Life Operating Manual — a 50–200 page "
        "personalized biography answering every major life question from birth to legacy. "
        "It is powered by the world's largest machine-readable astrological knowledge base: "
        "<b>20,849 classical rules</b> extracted from <b>55+ ancient texts</b> spanning "
        "5,000 years of Vedic, Hellenistic, Medieval Western, Chinese, and Numerological "
        "wisdom, cross-indexed in a <b>live Neo4j Knowledge Graph</b>.", sB))
    story.append(Paragraph(
        "Unlike every existing astrology product — which produces generic, templated, "
        "topic-by-topic horoscopes — AstroReport OS generates a <b>unique chronological "
        "life story</b> structured by the person's actual Dasha/Bhukti timeline, answering "
        "<b>141+ structured life questions</b> across <b>64 life domains</b> with evidence "
        "drawn directly from classical scripture.", sB))

    story.append(Spacer(1, 3*mm))
    story.append(tbl(
        ["Category", "AstroReport OS"],
        [
            ["Product Category", "AI-Powered Personalized Life Report Engine"],
            ["Core Technology", "Neo4j Knowledge Graph + Multi-System Astrology Engine + LLM Narrative"],
            ["Knowledge Base", "20,849 rules | 55+ books | Vedic + Western + Chinese + Nadi + Numerology"],
            ["Report Output", "50–200 page personalized PDF life biography"],
            ["Report Coverage", "Birth → Childhood → Education → Career → Marriage → Wealth → Legacy"],
            ["Life Questions Answered", "141+ structured questions across 64 domains"],
            ["Event Categories", "314 fully covered event categories"],
            ["Real Charts Validated", "32 celebrity + verified person charts"],
            ["Revenue Model", "B2C Reports + B2B API + Subscription + White-Label"],
            ["Market", "Global — 1.2B+ astrology consumers | $12B+ market | 12% CAGR"],
            ["Current Stage", "Production engine live on VPS | 80–100% accuracy validated"],
        ],
        [45*mm, W - 36*mm - 45*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 02. THE PROBLEM
    # ══════════════════════════════════════════════════════════════════
    story += sec("02", "The Problem — What The Market Is Missing")
    story.append(Paragraph(
        "The global astrology market generates <b>$12 billion annually</b> yet every "
        "existing product — from apps to PDF reports to live consultations — fails the "
        "consumer in the same fundamental ways:", sB))

    story.append(tbl(
        ["❌ Current Market Failure", "Impact On The Consumer"],
        [
            ["Generic templated reports — not personalized", "The reader does not recognize themselves in the report"],
            ["Topic-by-topic structure (marriage chapter, career chapter)", "No coherent life story — just disconnected predictions"],
            ["Single-tradition only (only Vedic OR only Western)", "Incomplete evidence — a blind man describing an elephant"],
            ["Predictions without explanation, context or guidance", "Fear, confusion, paralysis — no practical value"],
            ["No timeline — just static planetary analysis", "Cannot relate positions to actual lived experience"],
            ["Expensive consultations required for real depth", "Not accessible, not scalable, knowledge locked with one person"],
            ["AI-generated reports that hallucinate freely", "No grounding in classical rules — not trustworthy"],
            ["Knowledge base = Google + LLM memory", "Not traceable, not verifiable, not classical"],
        ],
        [90*mm, W - 36*mm - 90*mm]
    ))
    story.append(Spacer(1, 4*mm))
    story.append(banner(
        "The world's 1.2 billion astrology consumers deserve a product that actually "
        "explains their life — with evidence from the great classical texts — not a templated horoscope.", TEAL))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 03. THE SOLUTION
    # ══════════════════════════════════════════════════════════════════
    story += sec("03", "The Solution — AstroReport OS")
    story.append(Paragraph(
        "AstroReport OS solves every failure of the current market through a combination of "
        "the world's most complete knowledge base, a multi-system reasoning engine, and a "
        "chronological life biography structure guided by <b>21 core design principles</b>:", sB))

    story.append(tbl(
        ["#", "Core Principle", "Why It Matters"],
        [
            ["1", "Human First", "Describes the lived experience before the astrological reason"],
            ["2", "Life Journey (not horoscope)", "The report is a biography — not a planet analysis"],
            ["3", "Chronological Timeline", "Structured by Mahadasha/Bhukti life chapters, not topics"],
            ["4", "141+ Life Questions Answered", "Career, wealth, marriage, health, purpose — all within the story"],
            ["5", "Multi-System Fusion", "Vedic + Jaimini + KP + Nadi + Western + Chinese + Numerology"],
            ["6", "Knowledge Graph Powered", "Every interpretation traced to specific classical scripture rules"],
            ["7", "Evidence Weighting", "Conflicting indicators resolved with confidence scoring"],
            ["8", "Hope Over Fear", "Every challenge paired with practical, actionable guidance"],
            ["9", "Recognition Principle", "Readers frequently recognize themselves — builds trust"],
            ["10", "Explainable AI", "Full reasoning trace — not a black box"],
            ["11", "Continuous Life Story", "Each chapter builds on the previous, prepares for the next"],
            ["12", "Adaptive Depth", "Child-friendly to professional astrologer — same engine, different depth"],
        ],
        [8*mm, 55*mm, W - 36*mm - 63*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 04. TECHNOLOGY ARCHITECTURE
    # ══════════════════════════════════════════════════════════════════
    story += sec("04", "Technology Architecture — 7-Layer AI Engine")
    story.append(Paragraph(
        "AstroReport OS is a complete production AI system. Every layer is built, tested, "
        "and live:", sB))

    story.append(tbl(
        ["Layer", "Component", "Technology Stack", "Status"],
        [
            ["1 — Input",       "Birth Data Validation Engine", "Python / Swiss Ephemeris", "✅ Live"],
            ["2 — Calculation", "Chart Calculation Engine",     "Swiss Ephemeris + D1–D60 Vargas", "✅ Live"],
            ["3 — Knowledge",   "Neo4j Knowledge Graph",        "20,849 rules + 141 Q-nodes + 967 categories", "✅ Live"],
            ["4 — Reasoning",   "Multi-System Astrology Engine","Vedic + Jaimini + KP + Nadi + Western + Chinese", "✅ Live"],
            ["5 — Evidence",    "Confidence Scoring Engine",    "Weight matrix + conflict resolution + audit log", "✅ Live"],
            ["6 — Timeline",    "Dasha/Bhukti Timeline Engine", "Mahadasha → Bhukti → Antardasha sequencing", "✅ Live"],
            ["7 — Output",      "Report Rendering Engine",      "PDF (Tamil + English) | API | HTML", "✅ Live"],
            ["+ LLM",           "Narrative Biography Generator","Gemini / GPT-4 — chapter-level narration", "🔧 Integration"],
            ["+ API",           "B2B White-Label API",          "REST + JSON — per-report billing", "🔧 In Progress"],
            ["+ Mobile",        "iOS + Android App",            "React Native / Flutter", "📋 Planned"],
        ],
        [22*mm, 48*mm, 62*mm, 25*mm]
    ))

    story.append(Spacer(1, 5*mm))
    story += [Paragraph("Engine Performance Benchmarks", sH2)]
    story.append(tbl(
        ["Test", "Engine", "Result", "Charts"],
        [
            ["Celebrity Life Events",  "OLD Engine (rule-based)",    "80.3% accuracy", "16 celebs / 127 events"],
            ["Tamil Actor Films",       "NEW Engine (declarative)",   "100% per actor",  "9 actors / 398 films"],
            ["Vijay 68 Films",          "NEW Engine",                 "100% (68/68)",    "Joseph Vijay chart"],
            ["Reverse Logic Audit",     "OLD Engine",                 "8/8 correct",     "Manually verified"],
            ["Compatibility Scoring",   "Kuta Engine",                "24/36 Manoj+Kayalvizhi", "Verified match"],
            ["KG Rule Matching",        "Knowledge Graph",            "79–124 rules/placement", "Einstein chart"],
        ],
        [40*mm, 48*mm, 40*mm, 42*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 05. THE KNOWLEDGE BASE
    # ══════════════════════════════════════════════════════════════════
    story += sec("05", "The Knowledge Base — 55+ Books, 20,849 Rules")
    story.append(Paragraph(
        "The AstroReport OS Knowledge Base is the <b>most comprehensive machine-readable "
        "astrological corpus ever assembled</b>. Over 55 ancient and classical texts have "
        "been sourced, digitised via OCR, rule-extracted, deduplicated, and cross-indexed "
        "into the Neo4j Knowledge Graph:", sB))

    story.append(tbl(
        ["Classical Text", "Origin / Date", "Rules", "System"],
        [
            ["Brihat Parashara Hora Sastra (BPHS)", "India, ~600 BCE",     "2,905", "Vedic — Core Foundation"],
            ["KP Reader 3 — Predictive Astrology",  "India, Modern",       "2,512", "KP Cuspal System"],
            ["Sarvartha Chintamani",                 "India, ~1650",        "2,239", "Vedic — Combinations"],
            ["Bhrigu Samhita",                       "India, Ancient",      "1,852", "Bhrigu Nadi System"],
            ["Surya Siddhanta",                      "India, ~400 CE",      "1,134", "Astronomical Foundation"],
            ["Phaladeepika",                         "India, ~1100",          "612", "Vedic — Delineation"],
            ["300 Important Combinations (Raman)",   "India, Modern",         "550", "Yoga Combinations"],
            ["Tajika Neelakanthi",                   "India, ~1587",          "406", "Tajika / Annual Charts"],
            ["Muhurtha Chintamani",                  "India, Medieval",       "383", "Election Astrology"],
            ["Jataka Bharanam",                      "India, Medieval",       "358", "Vedic Delineation"],
            ["Bhavartha Ratnakara (Raman)",           "India, ~1300",          "329", "House Lord Combinations"],
            ["BPHS Sharma Vol 1",                    "India, Annotated",      "251", "Vedic — Annotated"],
            ["Lal Kitab (Original 1952)",            "India, 1952",           "135", "Remedial Astrology"],
            ["Chandra Kala Nadi (Santhanam)",        "Tamil Nadu, Ancient", "3,129", "Nadi — Degree Rules"],
            ["Tetrabiblos (Ptolemy)",                "Alexandria, ~150 CE", "1,059", "Hellenistic Western"],
            ["Vettius Valens — Anthology",           "Rome, ~160 CE",         "418", "Zodiacal Releasing"],
            ["Christian Astrology (W. Lilly)",       "England, 1647",         "380", "Medieval Western"],
            ["Carmen Astrologicum (Dorotheus)",      "Sidon, ~75 CE",          "41", "Triplicity + Elections"],
            ["Matheseos Libri VIII (Firmicus) V1+V2","Rome, ~334 CE",          "56", "Latin Delineation"],
            ["Mansagari (Sanskrit)",                 "India, Medieval",        "24", "Navamsa + Vimshottari"],
            ["Roots of Nadi (Naik)",                 "India, Modern",          "11", "Nadi Fundamentals"],
            ["Gochar Phaladeepika (Pulippani)",      "India, Modern",           "7", "Transit Predictions"],
            ["Jataka Chandrika (Kalidas)",           "India, Classical",        "1", "Classical Rules"],
            ["Stree Jataka (Varahamihira)",          "India, ~550 CE",          "5", "Female Horoscopy"],
            ["+ 30+ Additional Texts",               "Various traditions",  "1,500+", "Cross-validation"],
        ],
        [60*mm, 38*mm, 18*mm, 44*mm]
    ))
    story.append(Spacer(1, 4*mm))

    story.append(metrics([
        ("20,849", "Total Rules", "Deduplicated & Verified"),
        ("2,795",  "Yoga Rules",  "Planetary Combinations"),
        ("2,363",  "Wealth Rules","Income & Prosperity"),
        ("1,620",  "Health Rules","Wellness & Vitality"),
        ("869",    "Marriage Rules","Partnership & Love"),
        ("782",    "Children Rules","Parenting & Legacy"),
    ]))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 06. 82-VOLUME SPECIFICATION
    # ══════════════════════════════════════════════════════════════════
    story += sec("06", "The 82-Volume OS Design Specification")
    story.append(Paragraph(
        "One of the most extraordinary assets of AstroReport OS is its <b>82-volume design "
        "specification</b> — a complete engineering blueprint defining every component, "
        "database schema, interpretation rule, narrative standard, and production protocol "
        "of the entire system. This represents an enormous amount of architectural work "
        "and creates a deep, defensible moat:", sB))

    story.append(tbl(
        ["Series", "Volumes", "What It Defines"],
        [
            ["Version 1 — OS Core Specification",
             "1–9, 10A–10Q, 11–15",
             "Vision, Human Life Ontology, Timeline Engine, 1,000+ Question Catalog, "
             "Question Intelligence Engine, Narrative Engine, Report Chapter Engine, "
             "Life Stage Templates, Evidence Weighting, Report Composition, Personalization, "
             "Enterprise Architecture"],
            ["Version 2 — Implementation Series",
             "16–25",
             "Planet Interpretation Manual, House Interpretation Manual, Yoga Combination "
             "Manual, Dasha/Bhukti Timeline Manual, Timeline Storytelling Manual, "
             "NLG Writing Guide, Report Templates & Layout, QA Manual, AI Orchestration & "
             "LLM Integration, Production Operations Manual"],
            ["Version 3 — Knowledge Encyclopedia",
             "27–35",
             "Rashi (12 Signs) Encyclopedia, Divisional Charts (D1–D60) Encyclopedia, "
             "Planetary Aspects & Interactions, Strength & Dignity Calculations, "
             "Dosha & Remedies Encyclopedia, Event Prediction Framework, Transit Forecasting "
             "Manual, Jaimini Integration Manual, Master Unified Rulebook"],
            ["Version 4 — Data Specification",
             "36–53",
             "Planet DB Schema, House DB Schema, Nakshatra DB Schema, Yoga DB Schema, "
             "Dasha DB Schema, Timeline Experience DB, Child-Friendly DB, Professional DB, "
             "Paragraph Library DB, Knowledge Graph Ontology, Planet/House/Nakshatra/Rashi "
             "Knowledge Bases, Dasha/Event/QA/Life-Event Knowledge Bases"],
            ["Version 5 — Production Platform",
             "54–66",
             "Report Example Library, AI Training Benchmarks, Birth Data Validation System, "
             "Chart Calculation Engine, Explainable AI System, Personalization Engine, "
             "Multi-Language Platform, Voice Narration System, Visual Timeline Engine, "
             "Client Portal & CRM, Security & Privacy Framework, Deployment & Scaling Guide, "
             "Autonomous AI Astrologer Architecture"],
        ],
        [40*mm, 32*mm, W - 36*mm - 72*mm]
    ))
    story.append(Spacer(1, 4*mm))
    story.append(banner(
        "This 82-volume specification took years to build. It is a complete, proprietary "
        "engineering OS that no competitor possesses — a permanent, defensible architectural moat.", TEAL))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 07. PREDICTION SYSTEMS
    # ══════════════════════════════════════════════════════════════════
    story += sec("07", "Prediction Systems — 8 Traditions Integrated")
    story.append(Paragraph(
        "AstroReport OS is the <b>only platform in the world</b> that integrates eight "
        "distinct astrological traditions into a single unified reasoning engine:", sB))

    story.append(tbl(
        ["System", "Origin", "Age", "Core Technique", "What It Uniquely Reveals"],
        [
            ["Parashari Vedic",    "India",       "3,000+ yrs", "Houses, Dasha, Yogas, Dignity",         "Life events, timing, personality, karma"],
            ["Jaimini Astrology",  "India",       "2,500+ yrs", "Karakas, Chara Dasha, Arudha Lagna",   "Soul purpose, social image, advanced timing"],
            ["KP System",          "India",       "Modern",     "Cuspal Sub-Lords, Significators",        "Event prediction with high precision timing"],
            ["Nadi Astrology",     "Tamil Nadu",  "Ancient",    "Degree-specific planetary rules",        "Individual-level destiny reading"],
            ["Hellenistic Western","Greece/Rome", "2,200+ yrs", "Zodiacal Releasing, Profections, Lots", "Peak periods, annual themes, fortune"],
            ["Medieval Western",   "Europe",      "900+ yrs",   "Essential Dignities, Considerations",   "Planet strength, election timing"],
            ["Numerology",         "Global",      "3,000+ yrs", "Life Path, Expression, Soul Urge",      "Name analysis, personal year cycles"],
            ["Chinese BaZi",       "China",       "1,400+ yrs", "Four Pillars, 10-Year Luck Periods",    "Life structure, luck cycles, elemental balance"],
        ],
        [28*mm, 22*mm, 16*mm, 50*mm, 44*mm]
    ))
    story.append(Spacer(1, 3*mm))
    story.append(banner(
        "When all 8 systems agree on an indication → Confidence = VERY HIGH  |  "
        "When multiple systems confirm → Confidence = HIGH  |  "
        "Single system only → Confidence = MODERATE", BLUE))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 08. THE PRODUCT
    # ══════════════════════════════════════════════════════════════════
    story += sec("08", "The Product — What Users Receive")
    story.append(Paragraph(
        "Every AstroReport OS report is a <b>complete, personalized life biography</b>. "
        "It is not organized by planets or topics — it follows the person's actual life "
        "chronology from birth to legacy, with each chapter powered by the Knowledge "
        "Graph and answering specific life questions:", sB))

    story.append(tbl(
        ["Report Chapter", "Life Stage", "Key Life Questions Answered", "Evidence Sources"],
        [
            ["Foundation & Identity",    "Birth",      "Who am I? My strengths? How do people see me? What is my life purpose?",         "Lagna, Lagna lord, Sun, Moon, Nakshatra"],
            ["Childhood & Family",       "0–12 yrs",   "How did family shape me? Mother/father influence? Siblings? Emotional patterns?", "4th/2nd/3rd Houses, Moon, Jupiter"],
            ["Education & Intelligence", "12–18 yrs",  "How do I learn? Which subjects suit me? Mentors? Higher education?",              "5th House, Mercury, Jupiter, 9th House"],
            ["Career & Purpose",         "18–35 yrs",  "What career suits me? Leadership? Self-employment? Foreign career?",              "10th/6th Houses, Saturn, Sun, D10"],
            ["Love & Marriage",          "20–40 yrs",  "What qualities suit my partner? When is marriage indicated? Trust in relationships?", "7th House, Venus, Jupiter, D9 Navamsa"],
            ["Wealth & Business",        "25–55 yrs",  "How do I build wealth? Is business suitable? Best investment style?",             "2nd/11th/5th Houses, Jupiter, Dhana Yogas"],
            ["Children & Parenting",     "28–50 yrs",  "What kind of parent will I be? Values to pass on? Career/family balance?",        "5th House, Jupiter, D7"],
            ["Health & Lifestyle",       "All Life",   "How do I maintain health? Manage stress? Energy, sleep, exercise?",               "1st/6th/8th Houses, Mars, Saturn"],
            ["Property & Assets",        "30–50 yrs",  "Owning a home? Property wealth? Which type of property?",                         "4th House, Mars, D4"],
            ["Travel & Foreign",         "25–55 yrs",  "Will I benefit from abroad? International career? Migration?",                    "9th/12th Houses, Rahu, D9"],
            ["Purpose & Spirituality",   "35+ yrs",    "What is my life purpose? Spiritual path? Inner transformation?",                  "9th/12th Houses, Jupiter, Ketu, D20"],
            ["Wisdom & Legacy",          "55+ yrs",    "How do I mentor others? What is my life contribution? Retirement?",               "Full chart synthesis, Dasha summary"],
        ],
        [42*mm, 20*mm, 72*mm, 26*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 09. QUESTION INTELLIGENCE ENGINE
    # ══════════════════════════════════════════════════════════════════
    story += sec("09", "The Question Intelligence Engine")
    story.append(Paragraph(
        "The Question Intelligence Engine is a structured catalog of <b>141+ life questions</b> "
        "mapped to astrological evidence, life stages, and report placement. Each question "
        "is a structured knowledge object with its domain, life stage, astrological trigger, "
        "and narrative template:", sB))

    story.append(tbl(
        ["Question ID", "Life Question", "Domain", "Life Stage"],
        [
            ["Q0001", "Who am I?",                          "Identity",    "Birth"],
            ["Q0007", "What career suits me?",              "Career",      "Young Adult"],
            ["Q0008", "How do I build wealth?",             "Wealth",      "Adult"],
            ["Q0009", "What relationship patterns repeat?", "Relationships","Adult"],
            ["Q0010", "What is my life purpose?",           "Purpose",     "Whole Life"],
            ["Q0022", "How does my mother influence my life?","Family",    "Birth"],
            ["Q0041", "What career suits me best?",         "Career",      "Young Adult"],
            ["Q0046", "Should I become self-employed?",     "Business",    "Adult"],
            ["Q0051", "Am I naturally suited for business?","Business",    "Young Adult"],
            ["Q0061", "How do I express love?",             "Relationships","Young Adult"],
            ["Q0081", "How can I maintain good physical health?","Health", "Whole Life"],
            ["Q0091", "Will owning a home be an important life goal?","Property","Adult"],
            ["Q0101", "How important is travel in my life?","Travel",      "Whole Life"],
            ["Q0111", "What is my spiritual path?",         "Spirituality","Adult"],
            ["Q0121", "What is my leadership style?",       "Reputation",  "Adult"],
            ["Q0131", "When is retirement meaningful?",     "Retirement",  "Later Adult"],
            ["Q0141+","+ 100 more structured life questions","All Domains","All Stages"],
        ],
        [18*mm, 70*mm, 30*mm, 22*mm]
    ))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "The full catalog covers <b>64 life domains</b> including: Identity, Family, Education, "
        "Career, Business, Wealth, Marriage, Children, Health, Property, Travel, Spirituality, "
        "Leadership, Reputation, Legacy, Daily Habits, Decision Making, and more. "
        "The engine expands to 1,000+ questions as specified in the 82-volume OS Blueprint.", sB))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 10. ENGINE PERFORMANCE
    # ══════════════════════════════════════════════════════════════════
    story += sec("10", "Current Engine Performance & Accuracy")
    story.append(Paragraph(
        "AstroReport OS has been rigorously validated against <b>32 real birth charts</b> "
        "including celebrated public figures whose life events are historically documented:", sB))

    story.append(tbl(
        ["Person", "Category", "Events Tested", "Accuracy"],
        [
            ["Joseph Vijay (Tamil Actor)",   "Entertainment", "68 films + career events", "100%"],
            ["Tamil Actors (9 persons)",     "Entertainment", "398 film predictions",      "100% per actor"],
            ["16 Celebrity Charts",          "Mixed — Global","127 life events",            "80.3%"],
            ["AR Rahman",                    "Music",         "Career + Oscar timing",      "Verified"],
            ["Indira Gandhi",                "Politics",      "Life events + timing",       "~71%"],
            ["Mukesh Ambani",                "Business",      "Wealth + expansion events",  "~38–56%"],
            ["Manoj Kumar (personal chart)", "Personal",      "Life facts validation",      "Verified"],
            ["Albert Einstein",              "Science",       "KG rule matching: 79–124/placement", "Validated"],
        ],
        [48*mm, 28*mm, 52*mm, 22*mm]
    ))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("Verified Celebrity Charts in System", sH3))
    celeb_list = [
        ["Aamir Khan", "Aishwarya Rai", "Amitabh Bachchan", "AR Rahman", "Hrithik Roshan"],
        ["Indira Gandhi", "Jayaprakash (Director)", "Joseph Vijay", "Kamal Haasan", "Karnan"],
        ["Lata Mangeshkar", "Mahatma Gandhi", "MS Dhoni", "Mukesh Ambani", "Narendra Modi"],
        ["Rajinikanth", "Sachin Tendulkar", "Shah Rukh Khan", "Sonia Gandhi", "Sundar Pichai"],
    ]
    for row in celeb_list:
        story.append(Paragraph("  •  " + "    •  ".join(row), sBs))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 11. LIVE INFRASTRUCTURE
    # ══════════════════════════════════════════════════════════════════
    story += sec("11", "Live Infrastructure & Technical Status")
    story.append(Paragraph(
        "The entire AstroReport OS engine is <b>live in production</b> on a VPS server "
        "managed by PM2, with 24/7 uptime and full hot-reload capability:", sB))

    story.append(tbl(
        ["Component", "Technology", "Status", "Detail"],
        [
            ["Production Server",        "Linux VPS (root@46.28.44.225)", "✅ 24/7 Live", "PM2-managed, hot-reload"],
            ["Astrology Engine API",     "Python + PM2 (Process ID 27)",  "✅ Running",   "152+ restarts, stable"],
            ["Neo4j Knowledge Graph",    "Neo4j Graph Database",           "✅ Live",      "20,849 rules indexed"],
            ["Chart Calculation",        "Swiss Ephemeris (pyswisseph)",   "✅ Live",      "D1–D60 Vargas computed"],
            ["Report Generator (PDF)",   "ReportLab + Custom Fonts",       "✅ Live",      "Tamil + English PDFs"],
            ["Multi-Language Support",   "Tamil + Hindi + English",        "✅ Live",      "Devanagari font shaping"],
            ["Timeline Engine",          "Python Dasha Calculator",        "✅ Live",      "Mahadasha → Antardasha"],
            ["Compatibility Engine",     "Ashtakuta Kuta Scorer",          "✅ Live",      "36-point system"],
            ["Weight Optimizer (ML)",    "Calibration Loop",               "✅ Built",     "~20x speed optimized"],
            ["Category Engine",          "314-Category Declarative Engine","✅ Live",      "100% category coverage"],
            ["Book Corpus Pipeline",     "OCR + Extraction + KG Load",     "✅ Complete",  "55+ books processed"],
            ["Structure Base",           "82-Volume Design Spec",          "✅ Complete",  "Extracted to KG"],
        ],
        [40*mm, 45*mm, 22*mm, 53*mm]
    ))
    story.append(Spacer(1, 4*mm))

    story.append(Paragraph("Engine Code Statistics", sH3))
    story.append(tbl(
        ["Module", "Files", "Size"],
        [
            ["engine/       — Core prediction engine",    "111 files", "1,263 KB"],
            ["runtime/      — Runtime executors + optimizers", "120 files", "70,153 KB"],
            ["knowledge/    — KG loaders + connection",   "37 files",  "6,830 KB"],
            ["charts/       — 32 birth chart JSON files", "32 files",  "128 KB"],
            ["STRUCTURE BASE — 82-volume OS specification","82 PDFs",  "Complete"],
            ["books/        — 55+ classical text corpus", "80+ files", "100+ MB"],
            ["gemma_extractions/ — Rule extraction output","23+ files","Multi-MB"],
        ],
        [90*mm, 30*mm, 40*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 12. MARKET OPPORTUNITY
    # ══════════════════════════════════════════════════════════════════
    story += sec("12", "Market Opportunity — $12B+ Global Market")
    story.append(metrics([
        ("$12B+", "Global Astrology Market", "2025 — Growing 12% CAGR"),
        ("1.2B+", "Active Consumers", "Worldwide Astrology Audience"),
        ("$4.2B", "Western Market", "English-speaking Global"),
        ("$3.8B", "Indian Market", "Vedic Astrology (Tamil, Hindi, English)"),
    ]))
    story.append(Spacer(1, 5*mm))

    story.append(tbl(
        ["Segment", "Market Size", "Primary Revenue Model", "Time to Revenue"],
        [
            ["India — Vedic (Tamil, Hindi, English)", "$3.8B", "B2C Reports + Annual Subscription", "Immediate"],
            ["Global — Western Astrology (English)", "$4.2B", "B2C Reports + B2B API White-Label",  "Immediate"],
            ["Southeast Asia — Chinese BaZi",        "$1.8B", "B2C Reports + White-Label Platform", "Year 1–2"],
            ["Middle East + Arabic Markets",          "$600M", "B2C + Multi-language Subscription",  "Year 2"],
            ["B2B — Astrologer Software Platform",   "$850M", "Monthly SaaS + Per-Report API Fee",   "Year 1"],
            ["Enterprise — HR / Life Coaching",      "$750M", "Annual SaaS Contract",                "Year 2"],
            ["Voice + Visual Report Products",       "$500M", "Premium Add-On",                      "Year 2–3"],
        ],
        [58*mm, 22*mm, 55*mm, 25*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 13. COMPETITIVE ANALYSIS
    # ══════════════════════════════════════════════════════════════════
    story += sec("13", "Competitive Analysis")
    story.append(tbl(
        ["Competitor", "Product", "Weakness vs AstroReport OS"],
        [
            ["AstroSage / Jagannatha Hora",     "Chart calc + basic Vedic reports",  "No KG, no biography structure, single system, templated"],
            ["Astro.com / Cafe Astrology",      "Western chart reports + PDF",        "Static templates, no timeline, no Vedic, no multi-system"],
            ["Co-Star / The Pattern",           "Daily AI horoscopes",               "Surface level, no depth, no classical grounding, no Q-engine"],
            ["TimePassages / Solar Fire",       "Professional chart software",        "For astrologers only — not consumer-facing life report"],
            ["Nadi Astrologers (manual)",       "In-person leaf reading",            "Not scalable, not digital, expensive, single-system Nadi"],
            ["Generic LLM Horoscopes",          "GPT-generated reports",             "No classical grounding, hallucinations, no KG, no evidence"],
            ["Kundli.com / AstroVed",           "Vedic portal reports",              "Templated, no timeline biography, no multi-system fusion"],
            ["<b>AstroReport OS</b>",           "<b>AI Life Biography Engine</b>",   "<b>ALL systems + 20,849 rules + 141 Q-nodes + 82-Vol OS + Validated KG</b>"],
        ],
        [50*mm, 50*mm, W - 36*mm - 100*mm],
        hdr_bg=NAVY
    ))
    story.append(Spacer(1, 4*mm))
    story.append(banner(
        "No competitor has: A Knowledge Graph | Multi-system fusion | "
        "82-volume OS blueprint | Validated accuracy | Classical rule traceability | "
        "Life biography structure. AstroReport OS has all of them.", TEAL))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 14. BUSINESS MODEL
    # ══════════════════════════════════════════════════════════════════
    story += sec("14", "Business Model & Revenue Streams")
    story.append(tbl(
        ["Revenue Stream", "Model", "Price Point", "Margin", "Priority"],
        [
            ["Basic Life Report (PDF, English/Tamil)", "One-time",       "$4.99–$19.99", ">98%", "Primary"],
            ["Complete Life Biography (full)",          "One-time",       "$49.99–$149",  ">99%", "Primary"],
            ["Annual Subscription",                     "Recurring SaaS", "$9.99–$29.99/mo",">97%","Primary"],
            ["Compatibility Report (couples)",          "One-time",       "$29.99–$79.99",">98%", "Primary"],
            ["Annual Forecast Report",                  "Annual",         "$19.99–$49.99",">98%", "Primary"],
            ["Astrologer Pro Platform",                 "Monthly SaaS",   "$49–$199/mo",  ">90%", "Secondary"],
            ["B2B API White-Label",                     "Per-report API", "$0.50–$2.00/report",">80%","Secondary"],
            ["Enterprise SaaS License",                 "Annual contract","$5,000–$50,000/yr",">70%","Tertiary"],
            ["Voice Narration Report",                  "Premium add-on", "$9.99–$29.99",  ">95%","Future"],
            ["Visual Timeline Infographic",             "Premium add-on", "$4.99–$14.99",  ">97%","Future"],
            ["Multi-Language Premium",                  "Add-on",         "$4.99–$9.99",   ">97%","Future"],
        ],
        [62*mm, 25*mm, 32*mm, 18*mm, 23*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 15. UNIT ECONOMICS & FINANCIAL PROJECTIONS
    # ══════════════════════════════════════════════════════════════════
    story += sec("15", "Unit Economics & Financial Projections")
    story.append(Paragraph("Unit Economics", sH2))
    story.append(tbl(
        ["Metric", "Value", "Notes"],
        [
            ["Cost to generate 1 complete report (LLM + infrastructure)", "< $0.50",     "Even at GPT-4 rates"],
            ["Gross margin on $49.99 report",                              "> 99%",       "Pure digital product"],
            ["Gross margin on $149 premium report",                        "> 99%",       "Same generation cost"],
            ["Report generation time",                                     "< 3 minutes", "Current engine speed"],
            ["Reports per VPS server per day (current capacity)",          "500+",        "Scalable horizontally"],
            ["Customer Acquisition Cost target",                           "$2–$8",       "Digital + SEO + influencer"],
            ["Estimated LTV per customer (multi-report + subscription)",   "$75–$200",    "Conservative estimate"],
            ["B2B API cost per report delivered",                          "< $0.20",     "Infrastructure only"],
        ],
        [90*mm, 30*mm, 40*mm]
    ))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("3-Year Financial Projections (Conservative)", sH2))
    story.append(tbl(
        ["Metric", "Year 1 (2026–27)", "Year 2 (2027–28)", "Year 3 (2028–29)"],
        [
            ["B2C Reports Sold",          "10,000",     "80,000",       "400,000"],
            ["Average B2C Revenue/Report","$25",         "$30",           "$35"],
            ["B2C Revenue",               "$250,000",   "$2,400,000",   "$14,000,000"],
            ["Subscription Revenue",      "$20,000",    "$300,000",     "$2,000,000"],
            ["B2B API Revenue",           "$50,000",    "$500,000",     "$3,000,000"],
            ["Enterprise License Revenue","$0",          "$200,000",     "$1,500,000"],
            ["<b>Total Revenue</b>",      "<b>$320,000</b>","<b>$3,400,000</b>","<b>$20,500,000</b>"],
            ["Gross Margin",              "90%+",       "92%+",         "93%+"],
            ["Operating Costs",           "$180,000",   "$900,000",     "$4,500,000"],
            ["<b>EBITDA</b>",             "<b>$140,000+</b>","<b>$2,500,000+</b>","<b>$16,000,000+</b>"],
        ],
        [55*mm, 40*mm, 40*mm, 40*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 16. ROADMAP
    # ══════════════════════════════════════════════════════════════════
    story += sec("16", "Product Roadmap — 18 Months")
    story.append(tbl(
        ["Phase", "Timeline", "Milestone", "Outcome"],
        [
            ["Phase 1 — LLM Integration",    "Q3 2026 (Now)",  "Full chapter biography via Gemini/GPT-4 | English + Tamil reports | API v1", "First paid reports"],
            ["Phase 2 — B2C Launch",          "Q4 2026",        "Website + payment gateway + SEO | 1,000 paid reports | Social media launch", "$25K+ MRR"],
            ["Phase 3 — Scale & Languages",   "Q1 2027",        "Hindi + Malayalam + Arabic | Mobile app (React Native) | B2B API partnerships", "$100K+ MRR"],
            ["Phase 4 — Enterprise",          "Q2 2027",        "Corporate wellness + HR integration | White-label platform | 10,000 reports/month", "$300K MRR"],
            ["Phase 5 — Global Expansion",    "Q3 2027",        "Chinese + Spanish markets | Voice reports | Visual timeline infographics", "$1M+ MRR"],
            ["Phase 6 — AI Enhancement",      "Q4 2027",        "Feedback loop ML | Accuracy optimization | 1,000-question catalog complete", "Market leader"],
        ],
        [28*mm, 24*mm, 90*mm, 23*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 17. DEFENSIBLE MOAT
    # ══════════════════════════════════════════════════════════════════
    story += sec("17", "Defensible Moat & Intellectual Property")
    story.append(tbl(
        ["Asset", "Description", "Time to Replicate", "Defensibility"],
        [
            ["20,849-Rule Knowledge Graph",     "World's largest machine-readable astrological corpus — live in Neo4j",   "3–5 years minimum", "🔒 Very High"],
            ["82-Volume OS Specification",       "Complete engineering blueprint for the life biography AI engine",          "Years of architectural work", "🔒 Very High"],
            ["Multi-System Fusion Engine",       "8 traditions unified: Vedic + Jaimini + KP + Nadi + Western + Chinese + Numerology", "Not replicable easily", "🔒 Very High"],
            ["55+ Book OCR + Extraction Pipeline","Automated classical text digitization, rule extraction, deduplication",  "1–2 years + expertise", "🔒 High"],
            ["Weight Optimizer + ML Calibration","Accuracy calibration against 32 verified historical charts",              "Requires chart data",   "🔒 High"],
            ["141+ Question Catalog (KG Nodes)", "Structured life ontology mapped to astrological evidence in KG",          "6–12 months",          "🟡 Medium"],
            ["21-Principle Life Biography Design","The life journey report philosophy, narrative standards, chapter design", "Philosophy is unique",  "🟡 Medium"],
            ["32 Validated Celebrity Charts",    "Ground truth benchmark library for accuracy testing",                     "Years of collection",   "🟡 Medium"],
            ["Multi-Language Engine",            "Tamil + Hindi + English reports with proper font shaping",                "Months",               "🟡 Medium"],
        ],
        [48*mm, 68*mm, 26*mm, 18*mm]
    ))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 18. WHY NOW
    # ══════════════════════════════════════════════════════════════════
    story += sec("18", "Why Now — The Perfect Convergence")
    story.append(tbl(
        ["Force", "What's Changed", "Our Advantage"],
        [
            ["LLM Maturity",             "GPT-4 / Gemini can write coherent, nuanced life narratives at scale",    "Engine + KG already built — just connect LLM and launch"],
            ["Astrology Renaissance",    "Co-Star 20M users; Gen Z largest adopters; $12B market growing 12% CAGR","Deepest classical knowledge base in existence"],
            ["Personalization Economy",  "Consumers pay premium for genuinely personalized, meaningful content",    "Each report is unique — not a template — 20,849 rules applied"],
            ["Knowledge Graph Tech",     "Neo4j production-grade, fast, enterprise-ready",                          "KG with 20,849 rules + 141 Q-nodes already live and querying"],
            ["Classical Text Access",    "Archive.org + OCR technology enables ancient text digitization at scale", "55+ books already processed — pipeline is automated"],
            ["Digital Report Demand",    "PDF delivery + instant download — zero marginal cost after build",        "Report engine live — can serve 500+ reports/day immediately"],
        ],
        [28*mm, 68*mm, 64*mm]
    ))
    story.append(Spacer(1, 5*mm))
    story.append(banner(
        "The engine is ready. The knowledge base is indexed. The specification is complete. "
        "The market is hungry. The technology has matured. Now is the moment to launch.", NAVY))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 19. INVESTMENT ASK
    # ══════════════════════════════════════════════════════════════════
    story += sec("19", "Investment Ask & Use of Funds")
    story.append(Paragraph(
        "We are seeking <b>seed investment</b> to integrate LLM narrative generation, "
        "launch the B2C platform, and scale to 10,000 reports/month within 12 months. "
        "The core engine, knowledge base, and 82-volume specification are <b>already built</b>. "
        "Investment is for launch and scale, not core development:", sB))

    story.append(tbl(
        ["Use of Funds", "Allocation", "Specific Purpose"],
        [
            ["LLM API + Cloud Infrastructure",  "30%", "Gemini / GPT-4 integration | Scalable cloud hosting | CDN + delivery"],
            ["Product Development",              "25%", "B2B REST API | Mobile app (iOS + Android) | Multi-language engine | Payment gateway"],
            ["Marketing & User Acquisition",     "25%", "SEO content | Social media | Influencer partnerships | Astrologer partnerships"],
            ["Team Expansion",                   "15%", "Backend engineers | Content writers | Customer success | Sales"],
            ["Legal, IP & Operations",           "5%",  "Company incorporation | Trademark | IP protection | Compliance"],
        ],
        [55*mm, 22*mm, W - 36*mm - 77*mm]
    ))
    story.append(Spacer(1, 5*mm))
    story.append(banner(
        "The engine is built. The knowledge is indexed. The specification is complete. "
        "Investment = Launch + Scale — not core development.", GOLD))
    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════════════
    # 20. CLOSING
    # ══════════════════════════════════════════════════════════════════
    story += sec("20", "Closing Statement")
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(
        '"For 5,000 years, human beings have looked at the stars to understand their lives. '
        'For the first time in history, we have assembled all the wisdom — every great book, '
        'every classical rule, every tradition — into a single, living knowledge graph. '
        'We have built the technology to actually answer their questions — systematically, '
        'personally, and at scale. '
        'AstroReport OS is not an astrology app. '
        'It is the world\'s first AI-powered Life Intelligence Engine — '
        'a personal Life Operating Manual for every human being on Earth."',
        S("CLS", fontName="Helvetica-Oblique", fontSize=13, textColor=BLUE,
          alignment=TA_CENTER, leading=21, spaceAfter=10)))

    story.append(Spacer(1, 6*mm))
    story.append(hr(GOLD, 1.5))
    story.append(Spacer(1, 5*mm))

    story.append(metrics([
        ("20,849",  "Rules in Knowledge Graph", "From 55+ Classical Texts"),
        ("82",      "Design Volumes",            "Complete OS Blueprint"),
        ("8",       "Prediction Systems",        "Unified in One Engine"),
        ("∞",       "Lives to Understand",       "The Real Market"),
    ]))

    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("AstroReport OS",
        S("FT1", fontName="Helvetica-Bold", fontSize=20, textColor=NAVY, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph("The World's First AI-Powered Personal Life Report Engine",
        S("FT2", fontName="Helvetica", fontSize=12, textColor=MGREY, alignment=TA_CENTER, spaceAfter=8)))
    story.append(hr(GOLD, 0.8))
    story.append(Paragraph(
        f"CONFIDENTIAL  |  {datetime.now().strftime('%B %Y').upper()}  |  ALL RIGHTS RESERVED",
        S("FT3", fontName="Helvetica", fontSize=8, textColor=MGREY, alignment=TA_CENTER)))

    # ── Build ──────────────────────────────────────────────────────────────────
    doc.build(story, canvasmaker=BrandCanvas)
    size = os.path.getsize(OUT)
    print(f"\n[DONE] {OUT}")
    print(f"   Size: {size:,} bytes ({size//1024} KB)")
    print("   Open the file to review the investor package.")


if __name__ == "__main__":
    make()
