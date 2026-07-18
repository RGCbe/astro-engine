"""Generate ATRO_FULL_CATEGORY_LIST.pdf from the markdown."""
import sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT

_ROOT = Path(__file__).resolve().parent.parent
_OUT = _ROOT / "ATRO_FULL_CATEGORY_LIST.pdf"

INDIGO = colors.HexColor("#1A237E")
GOLD = colors.HexColor("#B8860B")
CREAM = colors.HexColor("#FAF5E8")
GREEN = colors.HexColor("#2E7D32")
RED = colors.HexColor("#8B0000")
ORANGE = colors.HexColor("#E67E22")

styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16, textColor=INDIGO, spaceBefore=10, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=INDIGO, spaceBefore=8, spaceAfter=4, fontName="Helvetica-Bold")
h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontSize=10, textColor=GOLD, spaceBefore=6, spaceAfter=2, fontName="Helvetica-Bold")
body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9, leading=11)
small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=7, leading=9)


def status_color(s):
    if "✅" in s: return GREEN
    if "⚠️" in s: return ORANGE
    return RED


def category_table(rows):
    """rows = [(num, category, status), ...]"""
    data = [["#", "Category", "Engine Status"]]
    table_rows_styles = []
    for i, (num, cat, status) in enumerate(rows, 1):
        data.append([str(num), Paragraph(f"<font size='8'>{cat}</font>", body), Paragraph(f"<font size='8'>{status}</font>", body)])
        table_rows_styles.append(("TEXTCOLOR", (2, i), (2, i), status_color(status)))
    t = Table(data, colWidths=[0.8*cm, 11*cm, 5*cm])
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
        ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CREAM]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ] + table_rows_styles
    t.setStyle(TableStyle(style))
    return t


SECTIONS = [
    {
        "title": "PART 1 — VEDIC: 12 HOUSES (BHAVAS)",
        "subsections": [
            ("1H — TANU (Self / Body / Personality / Longevity)", [
                (1, "Birth circumstances (premature / C-section / natural)", "❌ Missing"),
                (2, "Body type and complexion", "⚠️ Partial (PDF narrative)"),
                (3, "Personality formation in childhood", "⚠️ Partial"),
                (4, "General health throughout life", "✅ event_health_self"),
                (5, "Longevity span (full Ayurdaya)", "⚠️ Partial (longevity_ayurdaya.py)"),
                (6, "Major identity shifts / reinventions", "❌ Missing"),
                (7, "Public image / reputation cycles", "⚠️ Partial"),
                (8, "Self-confidence peaks and lows", "❌ Missing"),
                (9, "Beauty / attractiveness peaks", "❌ Missing"),
                (10, "Vitality / energy cycles", "❌ Missing"),
                (11, "Charisma activation periods", "❌ Missing"),
                (12, "Leadership emergence", "❌ Missing"),
                (13, "Style / dress signature shifts", "❌ Missing"),
                (14, "Birth-mark / scar significance", "⚠️ via body_moles.py"),
                (15, "Self-death timing", "✅ event_self_death"),
            ]),
            ("2H — DHANA (Wealth / Family / Speech / Food)", [
                (16, "Earnings cycles", "✅ event_wealth_peak"),
                (17, "Family wealth inheritance", "❌ Missing"),
                (18, "Speech mastery / oratorical career", "❌ Missing"),
                (19, "Voice quality issues (laryngitis, throat surgery)", "❌ Missing"),
                (20, "Food preferences / eating disorders", "❌ Missing"),
                (21, "Right eye health", "❌ Missing"),
                (22, "Hoarding tendencies", "❌ Missing"),
                (23, "Bank account / cash-flow fluctuations", "⚠️ Partial"),
                (24, "Asset accumulation peaks", "⚠️ Partial"),
                (25, "Family meal traditions / dining shifts", "❌ Missing"),
                (26, "Tooth loss / dental events", "❌ Missing"),
                (27, "Mouth / lip issues", "❌ Missing"),
                (28, "Singing career milestones", "❌ Missing"),
                (29, "Vocabulary / language acquisition", "❌ Missing"),
                (30, "Diet changes / fasting cycles", "❌ Missing"),
            ]),
            ("3H — SAHAJA (Siblings / Courage / Communication)", [
                (31, "Sibling birth dates", "❌ Missing"),
                (32, "Sibling marriages", "❌ Missing"),
                (33, "Sibling health issues", "❌ Missing"),
                (34, "Sibling deaths", "❌ Missing"),
                (35, "Elder vs younger sibling relationships", "❌ Missing"),
                (36, "Self-courage milestones", "❌ Missing"),
                (37, "Writing career milestones", "❌ Missing"),
                (38, "Email / communication mastery", "❌ Missing"),
                (39, "Short business trips", "❌ Missing"),
                (40, "Hands / arms injuries", "❌ Missing"),
                (41, "Hobby cultivation cycles", "❌ Missing"),
                (42, "Hearing issues (right ear)", "❌ Missing"),
                (43, "Newspaper / blog / podcast career", "❌ Missing"),
                (44, "Sports / athletics milestones", "❌ Missing"),
                (45, "Independence assertion", "❌ Missing"),
                (46, "Music creation (composing)", "❌ Missing"),
                (47, "First-time risk-taking", "❌ Missing"),
                (48, "Adventure / extreme travel", "❌ Missing"),
                (49, "Public speaking debut", "❌ Missing"),
            ]),
            ("4H — SUKHA (Mother / Home / Vehicles / Comforts)", [
                (50, "Mother's birth / nature", "⚠️ chart"),
                (51, "Mother's marriage day", "❌ Missing"),
                (52, "Mother's first child date", "❌ Missing"),
                (53, "Mother's death", "✅ event_mother"),
                (54, "Mother's health crises", "⚠️ Partial"),
                (55, "Home purchase", "✅ event_property"),
                (56, "Home renovations", "❌ Missing"),
                (57, "Land acquisitions", "⚠️ Partial"),
                (58, "Vehicle purchases", "❌ Missing"),
                (59, "Vehicle accidents", "❌ Missing"),
                (60, "Ancestral home shifts", "❌ Missing"),
                (61, "School admissions (childhood)", "⚠️ event_education_milestone"),
                (62, "Comfort peak / luxury peak", "❌ Missing"),
                (63, "Chronic chest issues", "❌ Missing"),
                (64, "Heart / cardiac events", "❌ Missing"),
                (65, "Real estate disputes", "❌ Missing"),
                (66, "Inheritance of land", "❌ Missing"),
                (67, "Move to new city", "❌ Missing"),
                (68, "House construction", "❌ Missing"),
                (69, "Plot sale", "❌ Missing"),
            ]),
            ("5H — PUTRA (Children / Creativity / Romance / Merit)", [
                (70, "Pregnancy timing", "⚠️ proxy"),
                (71, "Child birth", "✅ event_child_birth"),
                (72, "Children's first-words / milestones", "❌ Missing"),
                (73, "Children's school admission", "❌ Missing"),
                (74, "Children's marriages", "❌ Missing"),
                (75, "Children's deaths", "❌ Missing"),
                (76, "Romance affairs", "❌ Missing"),
                (77, "First love", "❌ Missing"),
                (78, "Mantra siddhi", "⚠️ Partial"),
                (79, "Speculation gains (stocks, lottery)", "❌ Missing"),
                (80, "Speculation losses", "❌ Missing"),
                (81, "Creative breakthroughs", "❌ Missing"),
                (82, "Academic excellence (own)", "⚠️ Partial"),
                (83, "Higher mental function peaks", "❌ Missing"),
                (84, "Yoga / meditation depth shifts", "⚠️ event_spiritual"),
                (85, "Devotion-to-deity intensification", "❌ Missing"),
                (86, "Past-life merit surfacing", "❌ Missing"),
                (87, "Royal / authority favor", "❌ Missing"),
            ]),
            ("6H — RIPU (Enemies / Disease / Service / Debt)", [
                (88, "Acute illness onset", "⚠️ event_health_self"),
                (89, "Chronic condition onset", "⚠️ Partial"),
                (90, "Surgery dates", "⚠️ Partial"),
                (91, "Hospitalization episodes", "⚠️ Partial"),
                (92, "Court cases filed (own)", "❌ Missing"),
                (93, "Lawsuits won / lost", "❌ Missing"),
                (94, "Debt cycles", "⚠️ in wealth_loss"),
                (95, "Loan approvals", "❌ Missing"),
                (96, "Loan defaults", "❌ Missing"),
                (97, "Enemy attacks", "❌ Missing"),
                (98, "Service-line career start", "❌ Missing"),
                (99, "Promotion within service", "❌ Missing"),
                (100, "Pet acquisitions", "❌ Missing"),
                (101, "Pet illnesses / deaths", "❌ Missing"),
                (102, "Theft / robbery victim", "❌ Missing"),
                (103, "Workplace conflicts", "❌ Missing"),
                (104, "Office politics escalations", "❌ Missing"),
                (105, "Daily routine disruptions", "❌ Missing"),
                (106, "Maternal uncle events", "❌ Missing"),
                (107, "Tax disputes / IT raids", "❌ Missing"),
                (108, "Government investigations on self", "❌ Missing"),
            ]),
            ("7H — KALATRA (Spouse / Partnerships / Public)", [
                (109, "Engagement", "⚠️ in marriage"),
                (110, "Marriage", "✅ event_marriage"),
                (111, "Marriage type (love / arranged / inter-caste)", "❌ Missing"),
                (112, "Spouse occupation revealed", "❌ Missing"),
                (113, "Spouse health crisis", "❌ Missing"),
                (114, "Spouse family relations", "❌ Missing"),
                (115, "Business partnership formation", "❌ Missing"),
                (116, "Business partnership dissolution", "❌ Missing"),
                (117, "Public contracts signed", "❌ Missing"),
                (118, "Trade negotiations", "❌ Missing"),
                (119, "Open enemies emerging", "❌ Missing"),
                (120, "Divorce / separation", "⚠️ relationship_break"),
                (121, "Second marriage", "⚠️ Partial"),
                (122, "Death of spouse", "✅ event_widowhood"),
                (123, "In-law issues", "❌ Missing"),
                (124, "Customer disputes", "❌ Missing"),
                (125, "Diplomatic missions", "❌ Missing"),
            ]),
            ("8H — AYUR (Longevity / Occult / Sudden Events)", [
                (126, "Sudden gains", "❌ Missing"),
                (127, "Sudden losses", "⚠️ Partial"),
                (128, "Inheritance receipt", "❌ Missing"),
                (129, "Insurance claims", "❌ Missing"),
                (130, "Lottery / gambling wins", "❌ Missing"),
                (131, "Major surgery", "⚠️ Partial"),
                (132, "Near-death experiences", "❌ Missing"),
                (133, "Occult / mystical experiences", "❌ Missing"),
                (134, "Research career", "❌ Missing"),
                (135, "Investigation work", "❌ Missing"),
                (136, "Spy / intelligence career", "❌ Missing"),
                (137, "Scandals (own)", "❌ Missing"),
                (138, "Hidden enemies attacks", "❌ Missing"),
                (139, "Sexual matters", "❌ Missing"),
                (140, "Genital / excretory health", "❌ Missing"),
                (141, "Karmic debts surfacing", "❌ Missing"),
                (142, "Past-life trauma resurfacing", "❌ Missing"),
                (143, "Spouse's wealth gains", "❌ Missing"),
            ]),
            ("9H — DHARMA (Father / Higher Learning / Fortune)", [
                (144, "Father's birth / nature", "⚠️ Partial"),
                (145, "Father's marriage", "❌ Missing"),
                (146, "Father's career milestones", "❌ Missing"),
                (147, "Father's death", "✅ event_father"),
                (148, "Higher education enrollment", "⚠️ Partial"),
                (149, "PhD / research degree", "❌ Missing"),
                (150, "Foreign travel for study", "⚠️ Partial"),
                (151, "Pilgrimage trips", "❌ Missing"),
                (152, "Guru initiation", "❌ Missing"),
                (153, "Religion change / conversion", "⚠️ event_spiritual"),
                (154, "Religious teaching career", "❌ Missing"),
                (155, "Publication of books", "❌ Missing"),
                (156, "Philosophical interest deepening", "❌ Missing"),
                (157, "Long-distance travel", "✅ event_foreign_travel"),
                (158, "Visa for foreign country", "❌ Missing"),
                (159, "Foreign residency", "❌ Missing"),
                (160, "Grandfather events", "❌ Missing"),
                (161, "Lucky breaks / divine grace", "❌ Missing"),
            ]),
            ("10H — KARMA (Career / Status / Authority)", [
                (162, "First job", "⚠️ event_career_breakthrough"),
                (163, "Promotion dates", "⚠️ Partial"),
                (164, "Job change dates", "❌ Missing"),
                (165, "Salary raises", "❌ Missing"),
                (166, "Salary cuts", "❌ Missing"),
                (167, "Profession change", "❌ Missing"),
                (168, "Business launch", "❌ Missing"),
                (169, "Business expansion", "❌ Missing"),
                (170, "Business closure", "❌ Missing"),
                (171, "Political career start", "⚠️ Partial"),
                (172, "Political party founding", "⚠️ Partial"),
                (173, "Political office win / loss", "❌ Missing"),
                (174, "Public office appointment", "❌ Missing"),
                (175, "Authority position", "⚠️ Partial"),
                (176, "Fame peak", "⚠️ Partial"),
                (177, "Fame loss / scandal", "❌ Missing"),
                (178, "Awards reception", "✅ event_honor_recognition"),
                (179, "Retirement", "❌ Missing"),
                (180, "Founder / CEO role", "❌ Missing"),
                (181, "Government recognition", "⚠️ Partial"),
                (182, "Civilian awards (Padma etc.)", "✅ Partial"),
            ]),
            ("11H — LABHA (Gains / Friends / Elder Siblings)", [
                (183, "Friend acquisition cycles", "❌ Missing"),
                (184, "Major friend losses", "❌ Missing"),
                (185, "Elder sibling birth", "❌ Missing"),
                (186, "Elder sibling marriage", "❌ Missing"),
                (187, "Elder sibling death", "❌ Missing"),
                (188, "Network gains", "❌ Missing"),
                (189, "Investment gains", "⚠️ Partial"),
                (190, "Bonus / windfall", "❌ Missing"),
                (191, "Long-cherished goal achievement", "❌ Missing"),
                (192, "Income breakthrough", "⚠️ Partial"),
                (193, "Social club memberships", "❌ Missing"),
                (194, "Award nominations", "⚠️ Partial"),
                (195, "Subscriber / follower milestones", "❌ Missing"),
                (196, "Brand deals", "❌ Missing"),
                (197, "Sponsorship deals", "❌ Missing"),
                (198, "Royalty payments", "❌ Missing"),
                (199, "Patent grants", "❌ Missing"),
                (200, "Recognition from peers", "❌ Missing"),
            ]),
            ("12H — VYAYA (Loss / Foreign / Spirituality / Confinement)", [
                (201, "Foreign settlement", "⚠️ Partial"),
                (202, "Emigration date", "❌ Missing"),
                (203, "Visa rejections", "❌ Missing"),
                (204, "Extended hospital stays", "❌ Missing"),
                (205, "Jail / confinement", "❌ Missing"),
                (206, "Charitable donations", "❌ Missing"),
                (207, "Major expenses", "❌ Missing"),
                (208, "Foreign business deals", "❌ Missing"),
                (209, "Spiritual retreat / ashram", "❌ Missing"),
                (210, "Sleep disorders", "❌ Missing"),
                (211, "Left eye health", "❌ Missing"),
                (212, "Bedroom pleasures peak / loss", "❌ Missing"),
                (213, "Loss of position", "❌ Missing"),
                (214, "Secret enemies (hidden)", "❌ Missing"),
                (215, "Past-life trauma processing", "❌ Missing"),
                (216, "Moksha preparation", "❌ Missing"),
                (217, "Loss of articles / valuables", "❌ Missing"),
            ]),
        ]
    },
    {
        "title": "PART 2 — VEDIC: SPECIAL YOGAS (~26 activations)",
        "subsections": [
            ("Auspicious Yogas — Dasha-Activation", [
                (218, "Mahapurusha (Ruchaka/Bhadra/Hamsa/Malavya/Shasha)", "✅ comprehensive_yogas"),
                (219, "Gaja-Kesari", "✅"),
                (220, "Budha-Aditya", "✅"),
                (221, "Chandra-Mangala", "✅"),
                (222, "Lakshmi yoga", "✅"),
                (223, "Saraswati yoga", "⚠️"),
                (224, "Adhi yoga", "⚠️"),
                (225, "Raja yoga periods", "✅"),
                (226, "Dhana yoga periods", "✅"),
                (227, "Neecha Bhanga Raja Yoga", "✅"),
                (228, "Vipareeta Raja Yoga", "✅"),
                (229, "Mahapadma yoga", "❌ Missing"),
                (230, "Pakshobhani yoga", "❌ Missing"),
            ]),
            ("Inauspicious Yogas", [
                (231, "Kemadruma yoga struggles", "⚠️"),
                (232, "Kaal Sarpa periods", "⚠️"),
                (233, "Sakata yoga low-tide", "❌ Missing"),
                (234, "Daridra yoga (poverty)", "❌ Missing"),
                (235, "Roga yoga flare-ups", "✅"),
                (236, "Pitra dosha activations", "✅"),
                (237, "Matri dosha activations", "❌ Missing"),
                (238, "Putra dosha activations", "❌ Missing"),
                (239, "Sade Sati phases (3)", "✅ sade_sati.py"),
                (240, "Ashtam Shani", "⚠️"),
                (241, "Mangal dosha activations", "⚠️"),
                (242, "Guru Chandala yoga", "❌ Missing"),
                (243, "Vish yoga (Moon-Saturn)", "❌ Missing"),
            ]),
        ]
    },
    {
        "title": "PART 3 — VEDIC: DIVISIONAL CHARTS (D1-D60)",
        "subsections": [
            ("Divisional Vargas", [
                (244, "D2 Hora — wealth", "❌ Missing"),
                (245, "D3 Drekkana — siblings", "❌ Missing"),
                (246, "D4 Chaturthamsa — fortune/home", "❌ Missing"),
                (247, "D7 Saptamsa — children", "❌ Missing"),
                (248, "D9 Navamsa — marriage", "✅ divisional_dasha"),
                (249, "D10 Dashamsa — career", "✅"),
                (250, "D12 Dwadasamsa — parents", "❌ Missing"),
                (251, "D16 Shodasamsa — vehicles", "❌ Missing"),
                (252, "D20 Vimsamsa — spirituality", "❌ Missing"),
                (253, "D24 Chaturvimsamsa — education", "❌ Missing"),
                (254, "D27 Bhamsa — strength", "❌ Missing"),
                (255, "D30 Trimsamsa — disease", "❌ Missing"),
                (256, "D40 Khavedamsa — boons", "❌ Missing"),
                (257, "D45 Akshavedamsa — total life", "❌ Missing"),
                (258, "D60 Shashtiamsa — most subtle", "❌ Missing"),
            ]),
        ]
    },
    {
        "title": "PART 4 — VEDIC: DASHA SYSTEMS",
        "subsections": [
            ("11 Major Dasha Systems", [
                (259, "Vimshottari (120 yr standard)", "✅ granular_dasha"),
                (260, "Yogini (36 yr)", "❌ Missing"),
                (261, "Kalachakra (sign-cycle)", "❌ Missing"),
                (262, "Chara Jaimini (sign-cycle)", "✅"),
                (263, "Sthira Jaimini (fixed)", "❌ Missing"),
                (264, "Ashtottari (108 yr)", "❌ Missing"),
                (265, "Drig Jaimini (aspectual)", "❌ Missing"),
                (266, "Niryana Shoola (death-timing)", "❌ Missing"),
                (267, "Mandooka (sign-jumping)", "❌ Missing"),
                (268, "Shoola (obstacles)", "❌ Missing"),
                (269, "Brahma (spiritual)", "❌ Missing"),
            ]),
        ]
    },
    {
        "title": "PART 5 — VEDIC: TRANSIT-SPECIFIC EVENTS",
        "subsections": [
            ("Saturn / Jupiter / Rahu-Ketu / Mars / Eclipse Cycles", [
                (270, "Sade Sati Phase 1 (Rising 2.5 yr)", "✅"),
                (271, "Sade Sati Phase 2 (Peak 2.5 yr)", "✅"),
                (272, "Sade Sati Phase 3 (Setting 2.5 yr)", "✅"),
                (273, "Ashtam Shani (8th from Moon)", "⚠️"),
                (274, "Ardha Ashtam (4th from Moon)", "⚠️"),
                (275, "Saturn Return (28-30 yr)", "✅"),
                (276, "Saturn over natal Sun", "✅"),
                (277, "Saturn over natal Moon (Janma Shani)", "⚠️"),
                (278, "Saturn over natal Lagna", "⚠️"),
                (279, "Jupiter Return (~12 yr)", "❌ Missing"),
                (280, "Jupiter over natal Moon", "❌ Missing"),
                (281, "Jupiter over natal Lagna", "❌ Missing"),
                (282, "Jupiter over 5H (children)", "❌ Missing"),
                (283, "Jupiter over 9H (fortune)", "❌ Missing"),
                (284, "Jupiter over 11H (gains)", "❌ Missing"),
                (285, "Rahu Return (18 yr)", "❌ Missing"),
                (286, "Ketu Return (18 yr)", "❌ Missing"),
                (287, "Rahu over natal Sun", "⚠️"),
                (288, "Rahu over natal Moon", "❌ Missing"),
                (289, "Ketu over natal Moon (detachment)", "❌ Missing"),
                (290, "Solar eclipse over natal Sun", "❌ Missing"),
                (291, "Lunar eclipse over natal Moon", "❌ Missing"),
                (292, "Eclipse over Lagna", "❌ Missing"),
                (293, "Eclipse over 7H (spouse)", "❌ Missing"),
                (294, "Eclipse over 10H (career)", "❌ Missing"),
                (295, "Mars Return (~22 mo)", "❌ Missing"),
                (296, "Mars over natal Mars (Mangala return)", "❌ Missing"),
                (297, "Mars over Saturn (conflict)", "⚠️"),
                (298, "Mars over Sun (anger / father)", "✅"),
                (299, "Mars over Moon (mother / mind)", "⚠️"),
            ]),
        ]
    },
    {
        "title": "PART 6-9 — VEDIC: TAJIK / LAL KITAB / NADI / KP",
        "subsections": [
            ("Tajik Varshaphala (Annual)", [
                (300, "Year Lord (Varsh-Lagna)", "⚠️ engine/tajik.py"),
                (301, "Munta position", "❌ Missing"),
                (302, "Saham Punya (virtue)", "❌ Missing"),
                (303, "Saham Vidya (knowledge)", "❌ Missing"),
                (304, "Saham Yasas (fame)", "❌ Missing"),
                (305, "Saham Marana (death)", "❌ Missing"),
                (306, "Saham Roga (disease)", "❌ Missing"),
                (307, "Saham Karya (action)", "❌ Missing"),
                (308, "Tajik yoga Ithasala", "❌ Missing"),
                (309, "Tajik yoga Isarapha", "❌ Missing"),
                (310, "Tajik yoga Nakta", "❌ Missing"),
                (311, "Tajik yoga Yamaya", "❌ Missing"),
                (312, "Tajik yoga Manaau", "❌ Missing"),
                (313, "Solar Return chart", "⚠️"),
                (314, "Annual Profections", "❌ Missing"),
            ]),
            ("Lal Kitab", [
                (315, "Karz cycles per house", "⚠️ engine/lal_kitab.py"),
                (316, "Pitra rin (paternal debt)", "⚠️"),
                (317, "Matra rin (maternal debt)", "⚠️"),
                (318, "Stree rin (female debt)", "❌ Missing"),
                (319, "Lal Kitab upay activation", "❌ Missing"),
                (320, "House-by-house predictions", "❌ Missing"),
                (321, "Special Lal Kitab yogas", "❌ Missing"),
            ]),
            ("Nadi Jyotish", [
                (322, "Bhrigu Nandi Nadi windows", "⚠️ engine/nadi_jyotish.py"),
                (323, "108-cell rules", "⚠️"),
                (324, "Conjunction-rule predictions", "⚠️"),
                (325, "Karaka transit predictions", "⚠️"),
                (326, "Past-life karma surfacing", "⚠️"),
            ]),
            ("KP Krishnamurti Paddhati", [
                (327, "Sub-lord precise timing", "✅ kp_paddhati.py"),
                (328, "Significator analysis per house", "❌ Missing"),
                (329, "Promise / Fructification / Antara", "❌ Missing"),
                (330, "Ruling Planet method", "❌ Missing"),
            ]),
        ]
    },
    {
        "title": "PART 10-17 — CROSS-TRADITION SYSTEMS",
        "subsections": [
            ("Chinese (BaZi + Zi Wei)", [
                (331, "BaZi Day Master strength shifts", "⚠️ engine/chinese_engine.py"),
                (332, "Five Elements cycles", "⚠️"),
                (333, "Branch-clash years", "⚠️"),
                (334, "Pillar transformations", "⚠️"),
                (335, "Five Elements luck pillar", "⚠️"),
                (336, "Zi Wei Dou Shu palaces", "⚠️"),
                (337, "Chinese zodiac yearly", "❌ Missing"),
                (338, "Element favorability yearly", "❌ Missing"),
            ]),
            ("Western Astrology", [
                (339, "Tropical Sun-sign monthly", "⚠️ engine/western_engine.py"),
                (340, "Saturn return (Western)", "❌ Missing"),
                (341, "Pluto generational transit", "❌ Missing"),
                (342, "Uranus transit to natal", "❌ Missing"),
                (343, "Neptune transit to natal", "❌ Missing"),
                (344, "Progressed Sun changes", "❌ Missing"),
                (345, "Solar arc directions", "❌ Missing"),
                (346, "Hellenistic profections", "⚠️"),
                (347, "Lots / Arabic Parts", "⚠️"),
                (348, "Mercury/Venus retrograde", "❌ Missing"),
            ]),
            ("Numerology", [
                (349, "Personal Year (1-9 cycle)", "⚠️ engine/numerology_engine.py"),
                (350, "Personal Month cycles", "⚠️"),
                (351, "Personal Day cycles", "⚠️"),
                (352, "Pinnacle period changes", "⚠️"),
                (353, "Challenge cycle activations", "⚠️"),
                (354, "Karmic number activations", "⚠️"),
                (355, "Master Numbers (11, 22, 33)", "⚠️"),
                (356, "Chaldean Vidhi & Bhagya", "⚠️"),
                (357, "Pythagorean Triad", "⚠️"),
                (358, "Lo Shu Grid missing numbers", "⚠️"),
                (359, "Name expression shifts", "⚠️"),
            ]),
            ("Mayan (Tzolk'in)", [
                (360, "260-day cycle phases", "⚠️ engine/mayan_engine.py"),
                (361, "Day Glyph activations", "⚠️"),
                (362, "Galactic Tone manifestations", "⚠️"),
                (363, "Wave-spell beginnings", "⚠️"),
                (364, "Color/element cycles", "⚠️"),
            ]),
            ("Palmistry (Hasta Samudrika)", [
                (365, "Life Line major breaks", "⚠️ palmistry_engine.py"),
                (366, "Heart Line changes (love)", "⚠️"),
                (367, "Head Line changes (intellect)", "⚠️"),
                (368, "Fate Line breakthrough/disruption", "⚠️"),
                (369, "Sun Line activation (fame)", "⚠️"),
                (370, "Marriage Line additions", "⚠️"),
                (371, "Children Lines", "⚠️"),
                (372, "Travel Lines", "⚠️"),
                (373, "Mount of Venus", "⚠️"),
                (374, "Mount of Jupiter", "⚠️"),
                (375, "Mount of Saturn", "⚠️"),
                (376, "Mount of Mars", "⚠️"),
            ]),
            ("Vastu (Space)", [
                (377, "Vastu defects per direction", "⚠️ vastu_shastra.py"),
                (378, "Sleeping direction impact", "⚠️"),
                (379, "Kitchen / bathroom placement", "⚠️"),
                (380, "Auspicious construction timing", "❌ Missing"),
                (381, "Vastu remedy effects", "⚠️"),
            ]),
            ("Muhurta (Electional)", [
                (382, "Auspicious wedding muhurta", "❌ Missing"),
                (383, "Business launch muhurta", "❌ Missing"),
                (384, "Travel start muhurta", "❌ Missing"),
                (385, "Vehicle purchase muhurta", "❌ Missing"),
                (386, "Surgery muhurta", "❌ Missing"),
                (387, "Education start muhurta", "❌ Missing"),
                (388, "Tarabala / Chandrabala", "❌ Missing"),
                (389, "Panchaka / Bhadra avoidance", "❌ Missing"),
            ]),
            ("Matchmaking (Guna Milan)", [
                (390, "Ashtakoot Milan (36 points)", "⚠️"),
                (391, "Nadi Dosha check", "⚠️"),
                (392, "Bhakoot Dosha check", "⚠️"),
                (393, "Mangal Dosha matching", "⚠️"),
                (394, "Mahendra match", "❌ Missing"),
                (395, "Vashya match", "❌ Missing"),
                (396, "Tara / Yoni match", "❌ Missing"),
                (397, "Graha Maitri", "❌ Missing"),
                (398, "Gana match", "❌ Missing"),
            ]),
        ]
    },
]


def build_pdf():
    flow = []
    # ── COVER ──
    flow.append(Paragraph("ATRO VEDIC ENGINE", h1))
    flow.append(Paragraph("Complete Category Reference — All ~398 Distinct Prediction Categories", h2))
    flow.append(Spacer(1, 4*mm))
    flow.append(Paragraph(
        "Every event-type or prediction category that Vedic + Western + Chinese + Mayan + "
        "Numerology + Palmistry can produce, mapped to current engine coverage.<br/><br/>"
        "<b>Legend:</b> "
        "<font color='#2E7D32'>✅ Fully covered (event_* function emits dated prediction)</font><br/>"
        "<font color='#E67E22'>⚠️ Partially covered (in engine but not as dated event)</font><br/>"
        "<font color='#8B0000'>❌ Missing entirely</font>",
        body))
    flow.append(Spacer(1, 6*mm))

    # Summary table
    summary_data = [
        ["Tradition", "Total", "✅ Full", "⚠️ Partial", "❌ Missing"],
        ["Vedic 12 Bhavas", "217", "12", "40", "165"],
        ["Special Yogas", "26", "12", "6", "8"],
        ["Divisional Charts", "15", "2", "0", "13"],
        ["Dasha Systems", "11", "2", "0", "9"],
        ["Transits", "30", "4", "8", "18"],
        ["Tajik/Varshaphala", "15", "0", "3", "12"],
        ["Lal Kitab", "7", "0", "3", "4"],
        ["Nadi Jyotish", "5", "0", "5", "0"],
        ["KP Paddhati", "4", "1", "0", "3"],
        ["Chinese", "8", "0", "6", "2"],
        ["Western", "10", "0", "4", "6"],
        ["Numerology", "11", "0", "11", "0"],
        ["Mayan", "5", "0", "5", "0"],
        ["Palmistry", "12", "0", "12", "0"],
        ["Vastu", "5", "0", "4", "1"],
        ["Muhurta", "8", "0", "0", "8"],
        ["Matchmaking", "9", "0", "4", "5"],
        ["", "", "", "", ""],
        ["GRAND TOTAL", "398", "33 (8%)", "111 (28%)", "254 (64%)"],
    ]
    t = Table(summary_data, colWidths=[5*cm, 1.6*cm, 2*cm, 2*cm, 2.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
        ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, -1), (-1, -1), GOLD),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.white),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, CREAM]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))
    flow.append(t)
    flow.append(PageBreak())

    # ── BODY ──
    for section in SECTIONS:
        flow.append(Paragraph(section["title"], h1))
        for sub_title, rows in section["subsections"]:
            flow.append(Spacer(1, 2*mm))
            flow.append(Paragraph(sub_title, h3))
            flow.append(category_table(rows))
            flow.append(Spacer(1, 3*mm))
        flow.append(PageBreak())

    # ── FOOTER ──
    flow.append(Paragraph("Vijay Test was only 11 categories — out of ~398 possible", h2))
    flow.append(Paragraph(
        "The recent Vijay battle tested 28 events across just <b>11 categories</b> "
        "(career / wealth_loss / honor / children / travel / wealth / marriage / father / "
        "health / spiritual / property). That's <b>2.7% of astrology's full prediction scope</b>.<br/><br/>"
        "Even at maximum stretch, a single chart with 100+ verified events would only cover "
        "20-30 categories. The remaining 370+ require <b>specialized event functions</b> the engine doesn't yet have.<br/><br/>"
        "<b>Bottom line:</b> The engine is ~8% complete by category-count. "
        "The accuracy numbers (79.5%, 80.3%) are accurate within the 33 fully-covered categories — "
        "but those represent only the most common life events. The full Vedic + cross-tradition "
        "scope is ~12× larger than what's currently built.",
        body))
    flow.append(Spacer(1, 6*mm))
    flow.append(Paragraph("Top 30 Missing Functions to Build Next", h2))
    priorities = [
        ["#", "Function", "Why"],
        ["1", "event_siblings", "3H — every chart has siblings"],
        ["2", "event_vehicle_purchase", "4H — common modern event"],
        ["3", "event_business_start", "10H — common professional event"],
        ["4", "event_promotion", "10H — measurable career event"],
        ["5", "event_legal_dispute", "6H — IT raids, court cases"],
        ["6", "event_inheritance", "8H — common late-life event"],
        ["7", "event_speculation_gain", "5H/11H — stocks, crypto, lottery"],
        ["8", "event_speculation_loss", "5H — losses"],
        ["9", "event_in_law_event", "7H/2H — common family"],
        ["10", "event_friend_loss", "11H — emotional milestone"],
        ["11", "event_partnership_formation", "7H — business common"],
        ["12", "event_partnership_break", "7H — modern common"],
        ["13", "event_pet_acquisition", "6H — modern common"],
        ["14", "event_charity_donation", "12H — wealth-life event"],
        ["15", "event_visa_grant", "9H/12H — modern foreign"],
        ["16", "event_eclipse_impact", "Transit — predictable date"],
        ["17", "event_saturn_return", "Transit — well-known cycle"],
        ["18", "event_jupiter_return", "Transit — 12-year cycle"],
        ["19", "event_pregnancy", "5H — separate from birth"],
        ["20", "event_engagement", "7H — separate from marriage"],
        ["21", "event_book_publication", "9H/3H — modern publishing"],
        ["22", "event_award_nomination", "11H — vs win"],
        ["23", "event_share_purchase", "5H — investment"],
        ["24", "event_house_construction", "4H — vs purchase"],
        ["25", "event_grandchildren_birth", "9H from 5H"],
        ["26", "event_brand_endorsement", "11H — modern"],
        ["27", "event_political_office", "10H — separate from spiritual"],
        ["28", "event_jail_confinement", "12H — major event"],
        ["29", "event_tax_dispute", "6H — government issues"],
        ["30", "event_voice_loss", "2H — for singers/actors"],
    ]
    t = Table(priorities, colWidths=[1*cm, 5*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
        ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CREAM]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 4*mm))
    flow.append(Paragraph(
        "<i>Each new function: ~30 mins to write + test. Total to cover all 254 missing categories: ~150 hours.</i>",
        small))

    doc = SimpleDocTemplate(
        str(_OUT), pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title="Atro Engine — Complete Category Reference"
    )
    doc.build(flow)
    sz_kb = os.path.getsize(str(_OUT)) // 1024
    print(f"DONE: {_OUT.name} ({sz_kb} KB)")


if __name__ == "__main__":
    build_pdf()
