"""
DEEP PDF GENERATOR — plain English with FULL life timeline.

12-15 pages. Same human-readable style as generate_summary_pdf.py but with much
more depth and a complete life chronology.

Structure:
  Page 1  — Cover + What's happening right now
  Page 2  — Your personality (strengths + watch-fors)
  Page 3  — Career & Wealth (extended, decade-by-decade career arc)
  Page 4  — Marriage (all windows, spouse profile, harmony, family)
  Page 5  — Children & family timing
  Page 6  — Health (body + mind + accident risk)
  Page 7  — Spirituality, travel, education
  Page 8-9 — FULL LIFE TIMELINE (9 maha-dasha chapters, birth to ~80)
  Page 10 — Decade-by-decade outlook (20s, 30s, 40s, 50s, 60s, 70s)
  Page 11 — Year-by-year calendar of next 10 years
  Page 12 — Practical action guide (what to focus on RIGHT NOW)
"""
import sys, os, json, datetime as dt, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, PageBreak, KeepTogether,
                                 HRFlowable)

from engine_bridge import to_engine_chart, run_engines
from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from granular_dasha import build_full_timeline, lookup
from comprehensive_yogas import detect_all_classical_yogas
try:
    from sade_sati import compute_sade_sati_periods
except Exception:
    compute_sade_sati_periods = lambda c: []

INDIGO   = HexColor("#312e81")
GOLD     = HexColor("#b88a37")
CREAM    = HexColor("#fef6e4")
GREY_LT  = HexColor("#f3f0e8")
GREY_MD  = HexColor("#6b6b6b")
TEXT     = HexColor("#1f1b14")
ACCENT   = HexColor("#7e3a96")
GREEN    = HexColor("#16a34a")
AMBER    = HexColor("#d97706")
RED      = HexColor("#c0392b")
BLUE     = HexColor("#2563eb")

# ─── Translation maps (same as summary) ──────────────────────────────────────
MD_THEME_PLAIN = {
    "Sun":     "authority + visibility + father themes",
    "Moon":    "emotional growth + family + public visibility",
    "Mars":    "action + competition + courage",
    "Mercury": "communication + business + skill-building",
    "Jupiter": "expansion + wisdom + good fortune",
    "Venus":   "relationships + comforts + creative joy",
    "Saturn":  "discipline + hard work + responsibility",
    "Rahu":    "ambition + unconventional gains + risk",
    "Ketu":    "detachment + spirituality + endings",
}

# Each MD lord — what to EXPECT during this period (plain English, no jargon)
MD_EXPECT = {
    "Sun": [
        "Recognition from authority figures (boss, government, father)",
        "Promotions or new official roles",
        "Increased self-confidence and visibility",
        "Father's situation becomes relevant — either his help or his absence",
    ],
    "Moon": [
        "Emotional growth and deeper connections",
        "Mother becomes important — her health, your bond with her",
        "Public visibility — people start noticing you",
        "Travel and changes in residence are likely",
        "Strong intuitive / artistic / creative phase",
    ],
    "Mars": [
        "High energy and willingness to take risks",
        "Property purchase, real estate dealings",
        "Disputes and confrontations — defending your interests",
        "Brothers / siblings become relevant",
        "Sports, fitness, machinery, surgery may feature",
    ],
    "Mercury": [
        "Communication-driven success (writing, teaching, business, sales)",
        "Sharp learning curve — good for new skills or higher education",
        "Business partnerships and trade deals",
        "Travel for work, networking, contracts",
    ],
    "Jupiter": [
        "Generally the best 16-year period in life",
        "Marriage, children, wealth expansion all possible",
        "Spiritual / philosophical / teaching pulls",
        "Recognition through wisdom or expertise",
        "Foreign travel for learning or work",
    ],
    "Venus": [
        "Relationships flourish — marriage often happens here",
        "Comforts, luxury, beautiful environments",
        "Creative work and artistic recognition",
        "Wealth through partnerships, women, or beauty industries",
    ],
    "Saturn": [
        "Hard work + delays + slow but solid progress",
        "Long-term structures get built (career, house, family roots)",
        "Lessons in patience and responsibility",
        "Health needs more attention; routine + discipline help",
        "Often the toughest period — but ends with mastery",
    ],
    "Rahu": [
        "Ambition spikes — you want more, faster",
        "Unconventional gains (foreign work, tech, speculation)",
        "Sudden rises and sudden falls — guard against arrogance",
        "Foreign lands or foreign people enter your life",
        "Watch for obsessive cravings and shortcut temptations",
    ],
    "Ketu": [
        "Detachment from old identities and goals",
        "Spiritual awakening or philosophical shift",
        "Endings — relationships, jobs, places — that needed to end",
        "Loss can feel heavy; meditation and acceptance are the antidote",
        "Strong intuition; gut feelings are accurate",
    ],
}

# Watch-fors per MD
MD_WATCH = {
    "Sun":     ["ego clashes with authority", "father's health if Sun is weak", "burnout from pushing too hard"],
    "Moon":    ["emotional ups-and-downs", "over-attachment to mother / home", "fluid retention / mind chatter"],
    "Mars":    ["accidents, cuts, surgeries", "anger losing you allies", "blood pressure / inflammation"],
    "Mercury": ["over-thinking analysis paralysis", "speech / nervous-system issues", "shady business contacts"],
    "Jupiter": ["weight gain, liver / pancreas", "over-optimism that misses risks", "complacency stealing momentum"],
    "Venus":   ["relationship triangles", "over-spending on comfort / luxury", "reproductive / kidney issues"],
    "Saturn":  ["depression, chronic pain", "isolation if you don't reach out", "delays that test patience"],
    "Rahu":    ["addictions, obsessions, anxiety", "moral shortcuts", "foreign / unconventional risk gone wrong"],
    "Ketu":    ["loneliness and confusion", "vague illnesses doctors can't pin", "loss of direction"],
}

EVENT_PLAIN = {
    "marriage": "Marriage / serious relationship window",
    "relationship_phase": "Relationship deepening",
    "career": "Career breakthrough / promotion",
    "wealth": "Wealth peak / new income source",
    "children": "Child birth / family expansion",
    "health": "Health flag — watch routines + sleep",
    "self_accident": "Physical-injury risk — drive carefully, avoid risky sports",
    "father": "Father-related event (his health, your bond)",
    "spiritual": "Spiritual awakening / inner shift",
    "travel": "Travel or relocation",
    "education": "New learning or important exam",
    "mother": "Mother-related event",
}


# ─── DEEP per-period guidance (career / health / money / relationships) ──────

MD_ARC_PARAGRAPH = {
    "Sun": "This period puts you in front of authority — bosses, government, fathers, public stage. "
           "Your sense of self is on trial. Energy is steady but not fast. Win recognition by quality, "
           "not by being loudest. Your father's situation often becomes central — either his help is "
           "decisive, or his absence is the lesson.",
    "Moon": "This is the longest steady-emotional-growth period in your life (10 years). The mind "
            "becomes more visible to the public — even introverts attract attention now. Mother / "
            "women in your family become important. Travel and home changes are likely. Mood is "
            "everything: the same week can feel completely different depending on inner weather.",
    "Mars": "This 7-year fire period is your 'do it now' decade. Initiative, courage, and physical "
            "energy spike. Property, real estate, defense, sports, engineering, surgery are all "
            "Mars-favored. Disputes intensify but you defend yourself better. Speed kills here — "
            "go fast on action, slow on words.",
    "Mercury": "17 years of communication-driven life. Speech, writing, teaching, business, sales, "
               "trade — words are your tool. Sharp learning curve. Travel for work increases. New "
               "skills, certifications, partnerships flourish. Stay away from sketchy contacts — "
               "Mercury attracts both honest and dishonest people equally.",
    "Jupiter": "Typically the best 16 years in life. Marriage, children, wealth, recognition all "
               "become easier. Teaching, advising, philosophy, foreign travel are supportive. The "
               "danger is complacency — Jupiter is so generous that you stop pushing. Don't waste "
               "this gift; this period sets up your senior years.",
    "Venus": "20 years of relationships, comfort, art, and pleasure. Marriage often happens here. "
             "Creative recognition, beauty industries, partnerships in business — all bloom. "
             "Wealth flows through women, design, hospitality, fashion. Watch for emotional "
             "triangles and over-spending on luxury.",
    "Saturn": "The hardest 19 years — but the most defining. Slow rise, delays, responsibilities. "
              "Long-term structures get built: career, house, marriage, savings, reputation. "
              "Health needs more care. The lesson is patience and consistency. Whatever you build "
              "during Saturn period LASTS — but it builds slowly.",
    "Rahu": "18 years of ambition. You want more, faster, bigger. Foreign work, technology, "
            "speculation, unconventional gains — all Rahu's territory. Sudden rises are possible "
            "but so are sudden falls. Build emergency reserves. Guard against addictions and "
            "obsessions — Rahu also rules the dark side of desire.",
    "Ketu": "7 years of detachment and dissolution. Old identities, jobs, relationships that have "
            "served their purpose will end. The pain is in resisting; the freedom is in letting go. "
            "Spiritual awakening or philosophical shift is common. Intuition is razor-sharp. Don't "
            "make irreversible decisions — Ketu fog passes.",
}

MD_CAREER = {
    "Sun": "Government, leadership, administration, medicine, public-facing roles. Promotions "
           "from formal authority. Father's career sphere may help or hinder. Best months: Apr-May.",
    "Moon": "Public-facing work, media, hospitality, caring professions, food, real estate, "
            "imports. Female colleagues + clients support you. Travel-heavy roles favored.",
    "Mars": "Real estate, defense, engineering, surgery, sports, machinery, manufacturing. "
            "Initiative-based career moves work. Self-employment opportunities open. Best months: "
            "Mar-Apr (Mars exaltation).",
    "Mercury": "IT, writing, teaching, sales, finance, accounting, trade, languages. Side "
               "businesses thrive. Build a brand around your communication ability.",
    "Jupiter": "Teaching, law, finance, advisory, religion, philosophy, foreign trade. The "
               "biggest income jumps usually happen here. Senior promotions and partnerships.",
    "Venus": "Design, arts, fashion, beauty, hospitality, luxury, entertainment, diplomacy. "
             "Partnerships double income. Female mentors / clients are key.",
    "Saturn": "Mining, real estate, government, agriculture, oil, heavy industry, eldercare. "
              "Slow but steady promotion through merit + endurance. Long-term contracts.",
    "Rahu": "Foreign companies, tech, AI, crypto, aviation, speculation, photography, film. "
            "Unconventional career paths open. Sudden jumps possible but volatile.",
    "Ketu": "Research, occult, behind-the-scenes work, healing, software engineering (deep "
            "tech), medicine, spiritual professions. Visibility drops; depth increases.",
}

MD_HEALTH = {
    "Sun": "Heart, eyes, bones, BP. Get annual cardiac checkup. Watch ego-driven overwork.",
    "Moon": "Sleep, hydration, mind, lymph, stomach. Emotional eating risk. Routine is medicine.",
    "Mars": "BP, blood, inflammation, cuts, surgery, fevers. Reduce red meat + alcohol. "
            "Drive carefully — accident risk genuinely elevated.",
    "Mercury": "Nervous system, skin, speech, lungs. Reduce screen time. Pranayama helps.",
    "Jupiter": "Liver, pancreas, weight gain, diabetes risk. Watch diet — Jupiter expands what "
               "it touches, including waistline.",
    "Venus": "Reproductive system, kidneys, throat, diabetes (from sweet excess). Annual "
             "gynae / urology checkup important.",
    "Saturn": "Bones, joints, teeth, chronic conditions, depression. Vitamin D, calcium, "
              "consistent sleep matter MORE than during other periods.",
    "Rahu": "Mysterious ailments doctors can't pin down. Allergies, autoimmune, anxiety, "
            "skin conditions. Detox + reduce environmental toxins.",
    "Ketu": "Hidden ailments, parasites, viral, immune drops. Take rare symptoms seriously "
            "— second opinions worth it.",
}

MD_MONEY = {
    "Sun": "Income: salaried promotions, government raises, awards. Spend: visible status items.",
    "Moon": "Income: public-facing work, hospitality, real-estate flips. Spend: home + family.",
    "Mars": "Income: property, defense, sports, surgery. Spend: vehicles + sudden big-ticket. "
            "Watch impulse-buying.",
    "Mercury": "Income: trade, consulting, writing, speaking fees. Spend: education + tech.",
    "Jupiter": "Income: peak earning years. Multiple income streams open. Spend: wisely "
               "— still save 30%. Investment in property + education favored.",
    "Venus": "Income: partnerships, design, beauty industries. Spend: comfort + luxury "
             "+ relationships. Watch over-spend on appearances.",
    "Saturn": "Income: slow but steady. Long-term contracts. Spend: necessities. Save aggressively "
              "— this is the period to build the safety net.",
    "Rahu": "Income: volatile peaks. Foreign currency, speculation, unconventional. Spend: "
            "splurge cycles. CRITICAL: build emergency reserves before peak ends.",
    "Ketu": "Income: drops or becomes irregular. Spend: minimal — Ketu reduces material desire "
            "naturally. Good for paying off debt.",
}

MD_RELATIONSHIPS = {
    "Sun": "Father / authority figures dominate. Spouse may feel sidelined. Make time for them.",
    "Moon": "Mother / women / public connection. Emotional intimacy deepens. New friendships easy.",
    "Mars": "Sibling bonds intensify. Disputes with partners possible. Speak less, listen more.",
    "Mercury": "Wide social network, business friends. Light, fun connections. Marriage possible.",
    "Jupiter": "Best for marriage + children. Mentors appear. Family expands. Spiritual community.",
    "Venus": "Romance, marriage, partnerships peak. Children grow. Female friendships matter most.",
    "Saturn": "Older friends, mentors, eldercare. Marriage solidifies through tested patience.",
    "Rahu": "Foreigners, unconventional people enter life. Affairs / triangles risk. Be careful.",
    "Ketu": "Old friendships fade naturally. Spiritual community attracts. Time for solitude.",
}

MD_ACTION_DO = {
    "Sun": ["Take visible leadership roles", "Reconcile with father if estranged", "Build self through achievement"],
    "Moon": ["Strengthen mother + family bonds", "Use intuition for big calls", "Take care of sleep + emotional health"],
    "Mars": ["Buy property if planned", "Take initiative on stalled goals", "Physical fitness becomes important"],
    "Mercury": ["Learn new skills + certifications", "Network actively", "Start a side business"],
    "Jupiter": ["Marry / have children if planned", "Higher education / teaching roles", "Major long-term investments"],
    "Venus": ["Marry or deepen committed bond", "Creative + design pursuits", "Business partnerships"],
    "Saturn": ["Build long-term structures", "Stay consistent with health routines", "Serve those below you"],
    "Rahu": ["Take calculated unconventional risks", "Network with foreigners", "Build emergency reserves"],
    "Ketu": ["Let go of what's ended", "Deepen meditation practice", "Research / behind-scenes work"],
}

MD_ACTION_AVOID = {
    "Sun": ["Ego battles with authority", "Pride blinding you to feedback", "Skipping rest for glory"],
    "Moon": ["Emotional decisions in low moods", "Excess comfort attachment", "Isolating when struggling"],
    "Mars": ["Reckless speed (driving, sports)", "Anger in important talks", "Burning bridges"],
    "Mercury": ["Analysis paralysis", "Sketchy business partners", "Things you can't take back"],
    "Jupiter": ["Complacency from success", "Over-eating / over-spending", "Lecturing others"],
    "Venus": ["Romantic complications", "Over-spending on luxury", "Conflict avoidance breeding resentment"],
    "Saturn": ["Despair when delays hit", "Isolating instead of asking help", "Skipping health checks"],
    "Rahu": ["Addictions + obsessions", "Moral shortcuts for fast gains", "Cutting corners on rules"],
    "Ketu": ["Big irreversible decisions", "Withdrawing fully from world", "Self-pity"],
}


from xml.sax.saxutils import escape as _xml_escape

def _safe(s, n=300):
    """Strip control chars, truncate, AND XML-escape for ReportLab Paragraph.
    Engine output may include `<`, `>`, `&` from book corpus that break the parser.
    """
    if not s: return ""
    s = str(s)
    s = "".join(c for c in s if c.isprintable() or c == "\n" or c == " ")
    if len(s) > n: s = s[:n] + "..."
    return _xml_escape(s)


def _strip_jargon(s):
    s = str(s)
    repl = {
        "malefic transits to lagna or 8th house": "difficult planetary periods (Mars/Saturn/Rahu)",
        "malefic transits": "difficult planetary periods",
        "lagna or 8th house": "your sense of self or transformation periods",
        "lagna": "ascendant",
        "8th house": "transformation period",
        "6th house": "work + health zone",
        "dusthana": "stress-zone",
        "Marana Karaka Sthana": "death-position",
        "marana karaka sthana": "death-position",
        "peak_dashas": "main periods to watch",
        "Vimshottari": "main planetary timeline",
        "mahadashas": "main periods",
        "mahadasha": "main period",
        "antardasha": "sub-period",
        "bhakti": "devotional",
        "sadhana": "practice",
        "puja": "ritual worship",
        "mantra": "chanting",
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return s


def _age(birth_dt, target):
    return (target - birth_dt).days / 365.25


# ─── Styles ──────────────────────────────────────────────────────────────────

def styles():
    base = getSampleStyleSheet()
    out = {}
    out["title"] = ParagraphStyle("title", parent=base["Title"],
        fontName="Helvetica-Bold", fontSize=24, textColor=INDIGO,
        alignment=TA_CENTER, spaceAfter=6, leading=28)
    out["subtitle"] = ParagraphStyle("subtitle", parent=base["Normal"],
        fontName="Helvetica", fontSize=11, textColor=GREY_MD,
        alignment=TA_CENTER, spaceAfter=14)
    out["h1"] = ParagraphStyle("h1", parent=base["Heading1"],
        fontName="Helvetica-Bold", fontSize=16, textColor=INDIGO,
        spaceBefore=10, spaceAfter=8, leading=20)
    out["h2"] = ParagraphStyle("h2", parent=base["Heading2"],
        fontName="Helvetica-Bold", fontSize=12, textColor=ACCENT,
        spaceBefore=8, spaceAfter=4, leading=15)
    out["h3"] = ParagraphStyle("h3", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=11, textColor=INDIGO,
        spaceBefore=4, spaceAfter=3, leading=14)
    out["body"] = ParagraphStyle("body", parent=base["Normal"],
        fontName="Helvetica", fontSize=10.5, textColor=TEXT,
        spaceAfter=6, leading=15, alignment=TA_JUSTIFY)
    out["bullet"] = ParagraphStyle("bullet", parent=base["Normal"],
        fontName="Helvetica", fontSize=10.5, textColor=TEXT,
        leftIndent=14, spaceAfter=4, leading=14, bulletIndent=4)
    out["chapter_label"] = ParagraphStyle("chap", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=18, textColor=GOLD,
        spaceAfter=2, alignment=TA_LEFT, leading=22)
    out["callout"] = ParagraphStyle("callout", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=11, textColor=INDIGO,
        spaceBefore=4, spaceAfter=4, leading=14,
        leftIndent=10, rightIndent=10, borderColor=GOLD, borderWidth=0,
        backColor=CREAM)
    out["small"] = ParagraphStyle("small", parent=base["Normal"],
        fontName="Helvetica", fontSize=9, textColor=GREY_MD,
        spaceAfter=3, leading=12)
    return out


def divider(thick=0.6):
    return HRFlowable(width="100%", thickness=thick, color=GOLD,
                       spaceBefore=4, spaceAfter=8)


# ─── Page 1: Cover + Now ─────────────────────────────────────────────────────

def page_cover(chart, today, st, dasha_now):
    flow = []
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    name = chart.get("name", "Native")
    age = _age(birth_dt, today)

    flow.append(Paragraph(name.upper(), st["title"]))
    flow.append(Paragraph("Deep Life Reading — Plain English + Full Timeline", st["subtitle"]))
    flow.append(divider())

    flow.append(Paragraph(
        f"<b>Born</b>: {b['day']:02d} {dt.date(2000, b['month'], 1).strftime('%B')} {b['year']} "
        f"at {b.get('hour', 0):02d}:{b.get('min', 0):02d} in {b.get('place', '—')}",
        st["body"]))
    flow.append(Paragraph(
        f"<b>Reading generated</b>: {today.strftime('%d %B %Y')} &nbsp;·&nbsp; <b>Age now</b>: {age:.0f} years",
        st["body"]))
    flow.append(Spacer(1, 0.4 * cm))

    flow.append(Paragraph("WHERE YOU ARE RIGHT NOW", st["h1"]))

    md = dasha_now["md"]; md_end = dasha_now["md_end"]
    ad = dasha_now["ad"]; ad_end = dasha_now["ad_end"]

    if md_end:
        years_left = max(0, (md_end - today).days // 365)
        flow.append(Paragraph(
            f"You are in your <b>{md} period</b>, which runs until <b>{md_end.strftime('%B %Y')}</b> "
            f"({years_left} more years). The overall life theme right now is "
            f"<b>{MD_THEME_PLAIN.get(md, 'growth')}</b>.",
            st["body"]))

    if ad_end:
        flow.append(Paragraph(
            f"Within this, the current sub-chapter runs until <b>{ad_end.strftime('%B %Y')}</b>, "
            f"adding a {MD_THEME_PLAIN.get(ad, 'mixed').split('+')[0].strip()} flavour to the {md} theme.",
            st["body"]))

    # Sade Sati
    flow.append(Spacer(1, 0.3 * cm))
    sade = compute_sade_sati_periods(chart) if compute_sade_sati_periods else []
    sade_end = None
    if isinstance(sade, list):
        for ph in sade:
            s = ph.get("start"); e = ph.get("end")
            if s and e:
                try:
                    if isinstance(s, dt.datetime) and isinstance(e, dt.datetime) and s <= today <= e:
                        sade_end = e; break
                except Exception:
                    pass
    if sade_end:
        flow.append(Paragraph(
            f"<b>Heads up:</b> You are currently in a 7.5-year Saturn pressure period "
            f"(called Sade Sati) until {sade_end.strftime('%B %Y')}. This typically means hard work, "
            f"slower results, and lessons in patience. Things settle by the end of it.",
            st["callout"]))

    # 18-month outlook
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("THE NEXT 18 MONTHS", st["h2"]))

    raw = scan_lifetime_v2(chart, today.year, today.year + 2, min_severity=3)
    bands = collapse_consecutive(raw) if raw else []
    ranked = rank_and_consume(bands) if bands else []
    horizon = today + dt.timedelta(days=18 * 30)
    near = [b for b in ranked if b.get("window_start") and b["window_start"] <= horizon]
    near.sort(key=lambda b: b["window_start"])

    if near:
        for ev in near[:6]:
            cat = ev.get("category", "")
            plain = EVENT_PLAIN.get(cat, ev.get("event", "important window"))
            ws = ev["window_start"].strftime("%b %Y")
            we = ev["window_end"].strftime("%b %Y") if ev.get("window_end") else ws
            stars = ev.get("stars", "")
            label = f"{ws} - {we}" if ws != we else ws
            flow.append(Paragraph(
                f"&bull; <b>{label}</b> — {plain} {stars}",
                st["bullet"]))
    else:
        flow.append(Paragraph(
            "No major life-event windows flagged in the next 18 months. "
            "A steady building period — good for long-term focus.",
            st["body"]))

    return flow


# ─── Page 2: Personality ─────────────────────────────────────────────────────

def page_personality(chart, reports, st):
    flow = []
    flow.append(Paragraph("YOUR PERSONALITY & MIND", st["h1"]))
    flow.append(divider())

    pos = chart["positions"]
    lagna = chart.get("lagna", "?")
    moon_sign = pos.get("Moon", {}).get("rasi", "?")

    LAGNA_OUTER = {
        "Aries": "energetic, direct, doesn't waste words — people see you as a doer",
        "Taurus": "steady, sensual, practical — people sense reliability and warmth",
        "Gemini": "quick, talkative, mentally restless — people see a sharp mind",
        "Cancer": "warm, protective, emotionally attuned — people feel cared for around you",
        "Leo": "dignified, generous, magnetic — people notice when you walk in",
        "Virgo": "precise, helpful, detail-loving — people trust your competence",
        "Libra": "charming, fair-minded, diplomatic — people enjoy being around you",
        "Scorpio": "intense, private, all-or-nothing — people sense depth they can't read",
        "Sagittarius": "philosophical, generous, optimistic — people see big-picture thinking",
        "Capricorn": "serious, ambitious, mature beyond age — people sense quiet authority",
        "Aquarius": "unconventional, principled, future-focused — people see an original",
        "Pisces": "gentle, intuitive, creative — people feel your sensitivity",
    }
    MOON_INNER = {
        "Aries": "your inner mood runs hot and fast — quick to feel, quick to move on",
        "Taurus": "your inner world is steady and slow-changing — you need stability to feel safe",
        "Gemini": "your mind is restless and curious — boredom is your real enemy",
        "Cancer": "you feel deeply and care about emotional safety — home matters enormously",
        "Leo": "you need recognition and dignity — pride is real for you",
        "Virgo": "you process by analysing — small details affect your mood",
        "Libra": "you need harmony in relationships — conflict drains you",
        "Scorpio": "you feel intensely and privately — emotions run deep, rarely shown",
        "Sagittarius": "you need freedom and meaning — feeling caged is the real pain",
        "Capricorn": "you take feelings seriously — slow to open up but loyal once you do",
        "Aquarius": "you process emotions through ideas — needs space + group connection",
        "Pisces": "highly sensitive — you absorb others' moods, need solitude to reset",
    }

    flow.append(Paragraph("<b>How others see you</b>", st["h2"]))
    flow.append(Paragraph(LAGNA_OUTER.get(lagna, "balanced and adaptive"), st["body"]))
    flow.append(Paragraph("<b>How you actually feel inside</b>", st["h2"]))
    flow.append(Paragraph(MOON_INNER.get(moon_sign, "balanced inner world"), st["body"]))

    # Strengths from yogas (deduped)
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Your natural strengths</b>", st["h2"]))
    yogas_r = next((r for r in reports if getattr(r, "category", "") == "yogas"), None)
    YOGA_PLAIN = {
        "Hamsa Yoga": "natural wisdom-teacher quality — people seek your advice and ethical clarity",
        "Bhadra Yoga": "sharp intellect + good communication — words are your tool",
        "Ruchaka Yoga": "strong courage + leadership — you can take charge",
        "Malavya Yoga": "natural charm + appreciation of beauty + comfort-creating ability",
        "Shasha Yoga": "discipline + capable of long-term achievement under pressure",
        "Raja Yoga": "ability to rise in life — recognition and respect come naturally",
        "Gaja-Kesari Yoga": "intelligence + good speaking ability + people respect you",
        "Budha-Aditya Yoga": "sharp mind + analytical ability + good for learning",
        "Lakshmi Yoga": "natural wealth potential",
        "Vesi Yoga": "good speech and dutiful nature",
        "Vasi Yoga": "charisma + leadership pull",
        "Ubhayachari Yoga": "balanced prosperity + fame + health",
        "Yukta Yoga": "sharp wit combined with decisive action",
        "Chandra-Mangala": "earning power through real estate, food, or hospitality",
    }
    seen = set()
    if yogas_r:
        for y in getattr(yogas_r, "predictions", [])[:12]:
            label = getattr(y, "label", "")
            plain = None
            for k, v in YOGA_PLAIN.items():
                if k.lower() in label.lower():
                    plain = v; break
            if plain and plain not in seen:
                seen.add(plain)
                flow.append(Paragraph(f"&bull; {plain}", st["bullet"]))
                if len(seen) >= 5: break
    if not seen:
        flow.append(Paragraph("&bull; A balanced chart — your strength is consistency, not dramatic peaks.", st["bullet"]))

    # Things to watch for
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Things to watch for</b>", st["h2"]))
    challenges = []
    sun_h = pos.get("Sun", {}).get("house", 0)
    if sun_h in (6, 8, 12):
        challenges.append("difficulty getting recognition from authority figures — work twice as hard for credit")
    mars_h = pos.get("Mars", {}).get("house", 0)
    if mars_h in (1, 4, 7, 8, 12):
        challenges.append("hot temper or impulsive choices — pause before big decisions")
    sat_h = pos.get("Saturn", {}).get("house", 0)
    if sat_h in (6, 8, 12):
        challenges.append("delays and slow progress in certain life areas — patience is your real lesson")
    moon_h = pos.get("Moon", {}).get("house", 0)
    if moon_h in (6, 8, 12):
        challenges.append("ups and downs in mood — emotional stability needs routine (meditation, sleep)")
    rahu_h = pos.get("Rahu", {}).get("house", 0)
    if rahu_h in (1, 4, 7, 10):
        challenges.append("ambition can become obsession — pace yourself, build slowly")
    if not challenges:
        challenges.append("no major built-in challenges — your work is using your strengths consistently")
    for c in challenges[:4]:
        flow.append(Paragraph(f"&bull; {c}", st["bullet"]))

    return flow


# ─── Page 3: Career & Wealth (extended) ──────────────────────────────────────

def page_career(chart, reports, today, st, all_mds):
    flow = []
    flow.append(Paragraph("CAREER & WEALTH", st["h1"]))
    flow.append(divider())

    career = next((r for r in reports if getattr(r, "category", "") == "career"), None)
    wealth = next((r for r in reports if getattr(r, "category", "") == "wealth"), None)
    edu = next((r for r in reports if getattr(r, "category", "") == "education"), None)

    # CAREER FIT
    flow.append(Paragraph("<b>Career — best-fit fields</b>", st["h2"]))
    CT = {"Industries / fields the chart suits": "Best-fit fields",
          "Secondary industries (via 10th-lord placement)": "Also fits",
          "Self-employed vs salaried lean": "Work style",
          "Career peak window": "Your peak years",
          "Authority over others": "Leadership ability"}
    if career:
        for p in career.predictions[:5]:
            val = p.value
            if isinstance(val, dict): val = "; ".join(f"{k}: {v}" for k, v in val.items())
            pl = CT.get(p.label, p.label)
            flow.append(Paragraph(f"&bull; <b>{pl}:</b> {_strip_jargon(_safe(val, 200))}", st["bullet"]))

    # CAREER ARC (decade-by-decade based on MDs)
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Career arc — your professional life decade by decade</b>", st["h2"]))
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))

    # Walk MDs spanning career age (18-65)
    arc_rows = []
    for md_rec in all_mds:
        md_start = md_rec.start
        md_end = md_rec.end
        if md_end < birth_dt + dt.timedelta(days=18*365): continue
        if md_start > birth_dt + dt.timedelta(days=65*365): break
        age_start = max(18, (md_start - birth_dt).days // 365)
        age_end = min(65, (md_end - birth_dt).days // 365)
        if age_start >= age_end: continue
        lord = md_rec.lord
        CAREER_FLAVOR = {
            "Sun": "authority phase — visibility, recognition, leadership opportunities",
            "Moon": "emotional / public-facing phase — fame, relatable work, female colleagues + clients",
            "Mars": "high-energy phase — initiative, property, engineering, sports, defense, surgery",
            "Mercury": "communication phase — writing, teaching, business, sales, IT, finance",
            "Jupiter": "expansion phase — best earnings, teaching, advising, foreign work",
            "Venus": "creative / relationship phase — design, arts, partnerships, beauty industries",
            "Saturn": "structure phase — hard work, slow rise, government, mining, real estate",
            "Rahu": "ambition phase — foreign, tech, speculation, unconventional gains",
            "Ketu": "detachment phase — research, behind-scenes work, spirituality, healing",
        }
        arc_rows.append([
            Paragraph(f"<b>Age {age_start}–{age_end}</b><br/><font size='8' color='#6b6b6b'>{md_start.strftime('%Y')}-{md_end.strftime('%Y')}</font>", st["bullet"]),
            Paragraph(f"<b>{lord} period</b> — {CAREER_FLAVOR.get(lord, 'general growth')}", st["bullet"]),
        ])
    if arc_rows:
        t = Table(arc_rows, colWidths=[2.8*cm, 13.2*cm])
        t.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]))
        flow.append(t)

    # WEALTH
    flow.append(Spacer(1, 0.4 * cm))
    flow.append(Paragraph("<b>Money — how it flows to you</b>", st["h2"]))
    WT = {"Primary wealth-channel (savings axis)": "Main savings source",
          "Gains / income channel": "Main income source",
          "Wealth peak windows": "Years when money flows easily",
          "Asset preference": "Natural asset preference",
          "Saver vs spender": "Spending tendency",
          "Debt tendency": "Debt risk",
          "Property": "Property ownership"}
    if wealth:
        for p in wealth.predictions[:6]:
            val = p.value
            if isinstance(val, dict): val = "; ".join(f"{k}: {v}" for k, v in val.items())
            pl = WT.get(p.label, p.label)
            flow.append(Paragraph(f"&bull; <b>{pl}:</b> {_strip_jargon(_safe(val, 200))}", st["bullet"]))

    # EDUCATION
    if edu and edu.predictions:
        flow.append(Spacer(1, 0.3 * cm))
        flow.append(Paragraph("<b>Subjects you naturally take to</b>", st["h2"]))
        top = edu.predictions[0]
        flow.append(Paragraph(f"&bull; <b>Strongest fit:</b> {_safe(top.value, 100)}", st["bullet"]))
        if len(edu.predictions) > 1:
            alts = [_safe(p.value, 60) for p in edu.predictions[1:4]]
            flow.append(Paragraph(f"&bull; <b>Other fits:</b> {', '.join(alts)}", st["bullet"]))

    return flow


# ─── Page 4: Marriage + Family ──────────────────────────────────────────────

def page_marriage(chart, reports, ranked_events, today, st):
    flow = []
    flow.append(Paragraph("MARRIAGE & PARTNERSHIPS", st["h1"]))
    flow.append(divider())

    marr = next((r for r in reports if getattr(r, "category", "") == "marriage"), None)

    flow.append(Paragraph("<b>Your marriage profile</b>", st["h2"]))
    if marr:
        MT = {"Probable marriage age window": "Most likely marriage age",
              "Spouse profile (from 7th sign)": "Spouse's nature",
              "Mangal Dosha": "Mars-warning for matching",
              "Marriage harmony tendency": "Overall harmony in marriage",
              "Number-of-marriages signal": "Number of marriages indicated",
              "Spouse community / background lean": "Spouse likely comes from"}
        for p in marr.predictions[:6]:
            val = p.value
            if isinstance(val, dict):
                val = ", ".join(f"{k}={v}" for k, v in val.items() if k in ("verdict","conf"))
            val_str = str(val)
            if "Mangal" in p.label:
                if val_str.startswith("yes"):
                    val_str = "Yes — Mars sits in a marriage-friction position. Match with another Mars-affected chart, or check classical cancellations."
                elif val_str == "no":
                    val_str = "No — no Mars issue for matching."
            if "MODERATE" in val_str:
                val_str = "moderate lean — partner from a different community / background"
            elif "STRONG" in val_str:
                val_str = "strong indicators — partner from a different community / region / faith"
            elif "NO cross" in val_str:
                val_str = "spouse most likely from your own community"
            pl = MT.get(p.label, p.label)
            flow.append(Paragraph(f"&bull; <b>{pl}:</b> {_safe(val_str, 220)}", st["bullet"]))

    # All marriage windows over lifetime
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Marriage / relationship windows across your life</b>", st["h2"]))
    marriage_evs = [e for e in ranked_events if e.get("category") in ("marriage", "relationship_phase")]
    marriage_evs.sort(key=lambda e: e["window_start"])
    if marriage_evs:
        b = chart["birth"]
        birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
        rows = [["Age", "When", "What", "Strength"]]
        for ev in marriage_evs[:8]:
            ws = ev["window_start"].strftime("%b %Y")
            we = ev["window_end"].strftime("%b %Y") if ev.get("window_end") else ws
            age = int((ev["window_start"] - birth_dt).days / 365.25)
            cat = ev.get("category", "")
            text = "Marriage window" if cat == "marriage" else "Relationship phase"
            stars = ev.get("stars", "⭐")
            rows.append([
                Paragraph(f"<b>{age}</b>", st["bullet"]),
                Paragraph(f"{ws}<br/><font size='8' color='#6b6b6b'>{we}</font>", st["bullet"]),
                Paragraph(text, st["bullet"]),
                Paragraph(stars, st["bullet"]),
            ])
        t = Table(rows, colWidths=[1.5*cm, 3.5*cm, 8.5*cm, 2.5*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), INDIGO),
            ("TEXTCOLOR", (0,0), (-1,0), CREAM),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,0), 9),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("LINEBELOW", (0,0), (-1,0), 1.2, GOLD),
        ]))
        flow.append(t)

    return flow


# ─── Page 5: Children + Health combined ──────────────────────────────────────

def page_children_health(chart, reports, st):
    flow = []
    flow.append(Paragraph("CHILDREN, FAMILY & HEALTH", st["h1"]))
    flow.append(divider())

    children = next((r for r in reports if getattr(r, "category", "") == "children"), None)
    family = next((r for r in reports if getattr(r, "category", "") == "family"), None)
    health = next((r for r in reports if getattr(r, "category", "") == "health"), None)

    # CHILDREN
    flow.append(Paragraph("<b>Children</b>", st["h2"]))
    if children:
        CT = {"Family-size lean": "Family size likely",
              "Gender tendency (classical, weak)": "Gender tendency (weak signal)",
              "Children's success potential": "How children will do in life",
              "Fertility blessing": "Fertility indicator"}
        for p in children.predictions[:4]:
            val = p.value
            if isinstance(val, dict): val = "; ".join(f"{k}: {v}" for k, v in val.items())
            pl = CT.get(p.label, p.label)
            flow.append(Paragraph(f"&bull; <b>{pl}:</b> {_strip_jargon(_safe(val, 200))}", st["bullet"]))

    # FAMILY
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Parents & siblings</b>", st["h2"]))
    if family:
        FT = {"Father — status & relationship": "Father",
              "Mother — status & relationship": "Mother",
              "Sibling — relationship": "Siblings",
              "Inheritance prospects": "Inheritance"}
        for p in family.predictions[:4]:
            val = p.value
            if isinstance(val, dict): val = "; ".join(f"{k}: {v}" for k, v in val.items())
            pl = FT.get(p.label, p.label)
            flow.append(Paragraph(f"&bull; <b>{pl}:</b> {_strip_jargon(_safe(val, 200))}", st["bullet"]))

    # HEALTH
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Health</b>", st["h2"]))
    if health and health.predictions:
        for p in health.predictions[:4]:
            val = p.value
            if isinstance(val, dict):
                nature = val.get("nature", "")
                body = val.get("body_part", "")
                peaks = val.get("peak_dashas", [])
                vp = []
                if nature: vp.append(nature)
                if body: vp.append(f"(affects: {body})")
                if peaks: vp.append(f"More cautious during {', '.join(peaks)} periods.")
                val = " ".join(vp)
            flow.append(Paragraph(f"&bull; {_strip_jargon(_safe(val, 280))}", st["bullet"]))
    else:
        flow.append(Paragraph(
            "&bull; No major built-in health risks. Standard healthy-lifestyle care applies — "
            "sleep, diet, regular checkups, exercise.", st["bullet"]))

    return flow


# ─── Page 6: Spirituality + Travel + Education extras ────────────────────────

def page_spiritual_travel(chart, reports, st):
    flow = []
    flow.append(Paragraph("SPIRITUALITY, TRAVEL & GROWTH", st["h1"]))
    flow.append(divider())

    spirit = next((r for r in reports if getattr(r, "category", "") == "spirituality"), None)
    foreign = next((r for r in reports if getattr(r, "category", "") == "foreign"), None)
    longev = next((r for r in reports if getattr(r, "category", "") == "longevity"), None)

    flow.append(Paragraph("<b>Spirituality</b>", st["h2"]))
    if spirit:
        ST = {"Spiritual path lean": "Best spiritual path for you",
              "Guru / teacher bond": "Teacher / mentor connection",
              "Religious participation tendency": "Religious participation style",
              "Mantra / sadhana inclination": "Inclination toward chanting / practice"}
        for p in spirit.predictions[:4]:
            val = p.value
            if isinstance(val, dict): val = "; ".join(f"{k}: {v}" for k, v in val.items())
            pl = ST.get(p.label, p.label)
            flow.append(Paragraph(f"&bull; <b>{pl}:</b> {_strip_jargon(_safe(val, 200))}", st["bullet"]))

    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Foreign travel & relocation</b>", st["h2"]))
    if foreign:
        FT = {"Foreign-settlement likelihood": "Chance of foreign settlement",
              "Foreign-direction lean": "Direction (compass)",
              "Most likely trigger window": "Most likely when"}
        for p in foreign.predictions[:3]:
            val = p.value
            if isinstance(val, dict): val = "; ".join(f"{k}: {v}" for k, v in val.items())
            pl = FT.get(p.label, p.label)
            flow.append(Paragraph(f"&bull; <b>{pl}:</b> {_strip_jargon(_safe(str(val), 200))}", st["bullet"]))

    if longev and longev.predictions:
        flow.append(Spacer(1, 0.3 * cm))
        flow.append(Paragraph("<b>Longevity indicator</b>", st["h2"]))
        for p in longev.predictions[:2]:
            val = p.value
            if isinstance(val, dict): val = "; ".join(f"{k}: {v}" for k, v in val.items())
            LONG_PLAIN = {
                "SHORT": "shorter band (under 50) — focus on health discipline early",
                "MEDIUM": "medium band (50-70)",
                "LONG": "long band (70+) — built-in vitality",
                "VERY LONG": "very long band (80+)",
            }
            val_str = str(val).strip()
            for k, v in LONG_PLAIN.items():
                if k in val_str.upper(): val_str = v; break
            flow.append(Paragraph(f"&bull; {_safe(val_str, 200)}", st["bullet"]))

    return flow


# ─── Pages 7+: FULL LIFE TIMELINE — DEEP per-chapter (1 page each MD) ─────────

def page_life_timeline(chart, all_mds, today, st, ranked_events, all_ads_by_md):
    flow = []
    flow.append(Paragraph("YOUR LIFE TIMELINE", st["h1"]))
    flow.append(Paragraph(
        "Your life is divided into 9 major chapters by the Vimshottari planetary clock. "
        "Each chapter has its own theme, sub-periods, and specific advice. "
        "Read your CURRENT chapter first, then future ones in order.",
        st["body"]))
    flow.append(PageBreak())

    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))

    for idx, md_rec in enumerate(all_mds[:9], 1):
        lord = md_rec.lord
        s = md_rec.start; e = md_rec.end
        age_s = max(0, (s - birth_dt).days // 365)
        age_e = (e - birth_dt).days // 365
        is_current = s <= today <= e
        is_past = e < today

        marker = "▶ NOW" if is_current else ("✓ PAST" if is_past else "→ FUTURE")
        marker_color = "#16a34a" if is_current else ("#6b6b6b" if is_past else "#7e3a96")
        bg_color = CREAM if is_current else white

        # ─── Chapter header ───
        flow.append(Paragraph(
            f"<font size='20' color='#b88a37'><b>Chapter {idx}: {lord} Period</b></font>",
            st["chapter_label"]))
        flow.append(Paragraph(
            f"<b>{s.strftime('%B %Y')} → {e.strftime('%B %Y')}</b> &nbsp;·&nbsp; "
            f"<b>age {age_s} to {age_e}</b> &nbsp;·&nbsp; "
            f"<b>{(e-s).days // 365} years long</b> &nbsp;·&nbsp; "
            f"<font color='{marker_color}'><b>{marker}</b></font>",
            st["small"]))
        flow.append(Spacer(1, 0.2*cm))

        # ─── Arc paragraph (personalized overview) ───
        flow.append(Paragraph(MD_ARC_PARAGRAPH.get(lord, MD_THEME_PLAIN.get(lord, "growth period")), st["body"]))
        flow.append(Spacer(1, 0.2*cm))

        # ─── What to expect ───
        flow.append(Paragraph("<b>What to expect during this chapter</b>", st["h3"]))
        for line in MD_EXPECT.get(lord, [])[:5]:
            flow.append(Paragraph(f"&bull; {line}", st["bullet"]))

        # ─── What to watch for ───
        flow.append(Paragraph("<b>Watch for:</b>", st["h3"]))
        for line in MD_WATCH.get(lord, [])[:3]:
            flow.append(Paragraph(f"&bull; {line}", st["bullet"]))

        # ─── 4-panel guidance (Career / Health / Money / Relationships) ───
        flow.append(Spacer(1, 0.2*cm))
        flow.append(Paragraph("<b>Life-area guidance for this period</b>", st["h3"]))
        guide_rows = [[
            Paragraph(f"<b>Career</b>", st["bullet"]),
            Paragraph(MD_CAREER.get(lord, ""), st["bullet"]),
        ], [
            Paragraph(f"<b>Health</b>", st["bullet"]),
            Paragraph(MD_HEALTH.get(lord, ""), st["bullet"]),
        ], [
            Paragraph(f"<b>Money</b>", st["bullet"]),
            Paragraph(MD_MONEY.get(lord, ""), st["bullet"]),
        ], [
            Paragraph(f"<b>Relationships</b>", st["bullet"]),
            Paragraph(MD_RELATIONSHIPS.get(lord, ""), st["bullet"]),
        ]]
        gt = Table(guide_rows, colWidths=[2.5*cm, 13.5*cm])
        gt.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("LINEBEFORE", (1,0), (1,-1), 0.5, GOLD),
        ]))
        flow.append(gt)

        # ─── Predicted events in this chapter ───
        period_events = [
            ev for ev in ranked_events
            if ev.get("window_start") and ev.get("window_end")
               and ev["window_start"] >= s and ev["window_start"] < e
        ]
        period_events.sort(key=lambda x: x["window_start"])
        if period_events:
            flow.append(Spacer(1, 0.2*cm))
            flow.append(Paragraph("<b>Predicted life events in this chapter</b>", st["h3"]))
            for ev in period_events[:6]:
                ws = ev["window_start"].strftime("%b %Y")
                we = ev["window_end"].strftime("%b %Y") if ev["window_end"] else ws
                age_ev = int((ev["window_start"] - birth_dt).days / 365.25)
                cat = ev.get("category", "")
                text = EVENT_PLAIN.get(cat, ev.get("event", ""))
                stars = ev.get("stars", "")
                label = f"{ws}" if ws == we else f"{ws} - {we}"
                flow.append(Paragraph(
                    f"&bull; <b>Age {age_ev} ({label})</b> — {text} {stars}",
                    st["bullet"]))

        # ─── Sub-chapters table (9 antardashas) ───
        ad_list = all_ads_by_md.get(lord)
        # Get the specific MD instance's ADs (multiple MDs of same lord possible but in 120y rare)
        ads_for_this_md = [a for a in ad_list if s <= a.start < e] if ad_list else []
        if ads_for_this_md:
            flow.append(Spacer(1, 0.2*cm))
            flow.append(Paragraph("<b>Sub-chapters (each lasts months to years)</b>", st["h3"]))
            rows = [["Sub-period", "Dates", "Age", "Flavor"]]
            AD_FLAVOR_PLAIN = {
                "Sun": "authority, recognition push",
                "Moon": "emotional shifts, public visibility",
                "Mars": "action burst, conflict, energy",
                "Mercury": "communication, learning, deals",
                "Jupiter": "expansion, wisdom, good fortune",
                "Venus": "relationships, comfort, creative",
                "Saturn": "slowdown, responsibility, structure",
                "Rahu": "sudden change, ambition, risk",
                "Ketu": "endings, detachment, spiritual",
            }
            for ad in ads_for_this_md:
                ad_ws = ad.start.strftime("%b %Y")
                ad_we = ad.end.strftime("%b %Y")
                ad_age = int((ad.start - birth_dt).days / 365.25)
                ad_now = ad.start <= today <= ad.end
                prefix = "▶ " if ad_now else ""
                # Combined flavor: MD theme stays, AD modifies
                ad_lord = ad.ad
                flavor = AD_FLAVOR_PLAIN.get(ad_lord, "mixed")
                rows.append([
                    Paragraph(f"<b>{prefix}{lord}-{ad_lord}</b>", st["bullet"]),
                    Paragraph(f"{ad_ws} → {ad_we}", st["bullet"]),
                    Paragraph(str(ad_age), st["bullet"]),
                    Paragraph(flavor, st["bullet"]),
                ])
            ad_t = Table(rows, colWidths=[3.2*cm, 4.8*cm, 1.4*cm, 6.6*cm])
            ad_t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), INDIGO),
                ("TEXTCOLOR", (0,0), (-1,0), CREAM),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,0), 9),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("LEFTPADDING", (0,0), (-1,-1), 6),
                ("LINEBELOW", (0,0), (-1,0), 1.0, GOLD),
            ]))
            flow.append(ad_t)

        # ─── Action guide for this chapter (DO + AVOID) ───
        flow.append(Spacer(1, 0.2*cm))
        do_avoid = [[
            Paragraph(f"<b><font color='#16a34a'>DO during {lord} period</font></b>", st["bullet"]),
            Paragraph(f"<b><font color='#c0392b'>AVOID during {lord} period</font></b>", st["bullet"]),
        ]]
        do = MD_ACTION_DO.get(lord, [])[:3]
        avoid = MD_ACTION_AVOID.get(lord, [])[:3]
        for i in range(max(len(do), len(avoid))):
            do_avoid.append([
                Paragraph(f"&bull; {do[i]}" if i < len(do) else "", st["bullet"]),
                Paragraph(f"&bull; {avoid[i]}" if i < len(avoid) else "", st["bullet"]),
            ])
        dt2 = Table(do_avoid, colWidths=[8*cm, 8*cm])
        dt2.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("BACKGROUND", (0,0), (-1,0), GREY_LT),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("LINEBETWEEN", (0,0), (-1,-1), 0.5, GOLD),
            ("BOX", (0,0), (-1,-1), 0.5, GOLD),
        ]))
        flow.append(dt2)

        # Page break after each chapter (except last)
        if idx < 9:
            flow.append(PageBreak())

    return flow


# ─── Page 10: Decade-by-decade outlook ────────────────────────────────────────

def page_decade_outlook(chart, all_mds, ranked_events, today, st):
    flow = []
    flow.append(Paragraph("DECADE-BY-DECADE OUTLOOK", st["h1"]))
    flow.append(divider())

    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))

    decades = [(20, 30), (30, 40), (40, 50), (50, 60), (60, 70), (70, 80)]
    current_age = (today - birth_dt).days / 365.25

    DECADE_THEME = {
        (20, 30): "Building decade — career direction + marriage + identity",
        (30, 40): "Establishment decade — settled career, family, leadership emerging",
        (40, 50): "Peak decade — maximum earning + influence + responsibility",
        (50, 60): "Consolidation decade — wisdom-sharing + mentor role + legacy",
        (60, 70): "Reflection decade — succession planning + spiritual deepening",
        (70, 80): "Wisdom decade — teaching, family elder, inner work",
    }

    rows = [["Age band", "Active periods", "What to expect", "Key events"]]
    for (a1, a2) in decades:
        d_start = birth_dt + dt.timedelta(days=a1*365.25)
        d_end = birth_dt + dt.timedelta(days=a2*365.25)
        # Find MDs active in this decade
        active_lords = []
        for md in all_mds:
            if md.end < d_start or md.start > d_end: continue
            active_lords.append(md.lord)
        active_lords = list(dict.fromkeys(active_lords))  # dedupe preserving order

        # Find events in this decade
        ev_in = [e for e in ranked_events
                 if e.get("window_start") and d_start <= e["window_start"] <= d_end]
        ev_in.sort(key=lambda e: e["window_start"])
        ev_summary = "; ".join(
            EVENT_PLAIN.get(e.get("category",""), e.get("event","event"))[:30]
            for e in ev_in[:3])
        if not ev_summary: ev_summary = "(steady period)"

        theme_text = DECADE_THEME.get((a1, a2), "")
        is_current = a1 <= current_age < a2
        prefix = "▶ " if is_current else ""

        rows.append([
            Paragraph(f"<b>{prefix}{a1}s</b>", st["bullet"]),
            Paragraph(", ".join(active_lords) if active_lords else "—", st["bullet"]),
            Paragraph(theme_text, st["bullet"]),
            Paragraph(ev_summary, st["bullet"]),
        ])

    t = Table(rows, colWidths=[1.6*cm, 3.5*cm, 6.5*cm, 4.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), INDIGO),
        ("TEXTCOLOR", (0,0), (-1,0), CREAM),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("LINEBELOW", (0,0), (-1,0), 1.2, GOLD),
    ]))
    flow.append(t)
    return flow


# ─── Page 11: Year-by-year calendar of next 10 years ─────────────────────────

def page_year_calendar(chart, ranked_events, today, st):
    flow = []
    flow.append(Paragraph("YEAR-BY-YEAR — NEXT 10 YEARS", st["h1"]))
    flow.append(divider())

    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))

    rows = [["Year", "Age", "What to watch for"]]
    for offset in range(0, 11):
        yr = today.year + offset
        yr_start = dt.datetime(yr, 1, 1)
        yr_end = dt.datetime(yr, 12, 31)
        age = int((yr_start - birth_dt).days / 365.25)
        ev_in = [e for e in ranked_events
                 if e.get("window_start") and not (e["window_end"] < yr_start or e["window_start"] > yr_end)]
        ev_in.sort(key=lambda e: -e.get("score", 0))
        if ev_in:
            lines = []
            for e in ev_in[:3]:
                cat = e.get("category", "")
                txt = EVENT_PLAIN.get(cat, e.get("event", "event"))[:55]
                stars = e.get("stars", "")
                lines.append(f"{txt} {stars}".strip())
            ev_text = "<br/>".join(lines)
        else:
            ev_text = "<i>steady period — focus on continuing efforts</i>"
        marker = "▶ " if yr == today.year else ""
        rows.append([
            Paragraph(f"<b>{marker}{yr}</b>", st["bullet"]),
            Paragraph(f"{age}", st["bullet"]),
            Paragraph(ev_text, st["bullet"]),
        ])

    t = Table(rows, colWidths=[2.0*cm, 1.5*cm, 12.5*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), INDIGO),
        ("TEXTCOLOR", (0,0), (-1,0), CREAM),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("LINEBELOW", (0,0), (-1,0), 1.2, GOLD),
    ]))
    flow.append(t)
    return flow


# ─── Page 12: Practical action guide ─────────────────────────────────────────

def page_action_guide(chart, reports, dasha_now, st):
    flow = []
    flow.append(Paragraph("PRACTICAL GUIDE — WHAT TO FOCUS ON RIGHT NOW", st["h1"]))
    flow.append(divider())

    md = dasha_now["md"]
    md_end = dasha_now["md_end"]

    flow.append(Paragraph(
        f"You are in <b>{md} period</b> until {md_end.strftime('%B %Y') if md_end else 'further notice'}. "
        f"This is the dominant life-energy for the next several years. Working WITH it produces "
        f"results faster than fighting it.",
        st["body"]))
    flow.append(Spacer(1, 0.3 * cm))

    # Action guide per MD
    flow.append(Paragraph(f"<b>What to DO during your {md} period:</b>", st["h2"]))
    DO_GUIDE = {
        "Sun":     ["Take on visible leadership roles, even uncomfortable ones",
                    "Reconcile with father or father-figures",
                    "Public speaking, presentations, formal authority",
                    "Build self-confidence through achievement, not approval"],
        "Moon":    ["Strengthen your relationship with mother + women in family",
                    "Use intuition; trust gut feelings on important calls",
                    "Public-facing work (media, hospitality, caring professions)",
                    "Take care of your sleep, emotional regulation, hydration"],
        "Mars":    ["Take initiative on stalled goals",
                    "Real estate, property, defense industries are favored",
                    "Physical fitness, sports, surgery (if needed) — auspicious",
                    "Stand up for yourself in disputes — but stay strategic"],
        "Mercury": ["Learn new skills, languages, certifications",
                    "Writing, teaching, presenting, sales — leverage your words",
                    "Start a small side business or trading activity",
                    "Network actively — new contacts open doors"],
        "Jupiter": ["Marry, have children, start the family if not already",
                    "Pursue higher education or teaching roles",
                    "Foreign travel for learning or work — supportive",
                    "Major investments, property, philanthropy all favored"],
        "Venus":   ["Marry or deepen committed relationships",
                    "Creative pursuits, design, arts, music — well-supported",
                    "Partnerships in business — Venus loves collaboration",
                    "Reward yourself with beauty, comfort, good food"],
        "Saturn":  ["Build long-term structures — career, house, savings",
                    "Stay consistent with health routines + early sleep",
                    "Be patient with delays — they're teaching you something",
                    "Serve those below you — Saturn rewards humility"],
        "Rahu":    ["Take a calculated risk on the unconventional",
                    "Foreign work, tech, AI, speculation — Rahu's domain",
                    "Network with foreigners or people outside your usual circle",
                    "Build emergency reserves — Rahu peaks have sharp falls"],
        "Ketu":    ["Let go of attachments that have ended their purpose",
                    "Deepen spiritual / meditation practice",
                    "Research, behind-scenes work, healing professions",
                    "Don't make irreversible decisions — wait for Ketu period to end"],
    }
    for line in DO_GUIDE.get(md, ["Continue what's working, observe what's not."]):
        flow.append(Paragraph(f"&bull; {line}", st["bullet"]))

    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph(f"<b>What to AVOID during your {md} period:</b>", st["h2"]))
    AVOID_GUIDE = {
        "Sun":     ["Ego battles with authority", "Pride blinding you to feedback", "Skipping rest in pursuit of glory"],
        "Moon":    ["Emotional decisions made in low moods", "Excess attachment to comfort", "Isolating yourself when struggling"],
        "Mars":    ["Reckless speed (driving, sport, surgery decisions)", "Anger in important conversations", "Burning bridges"],
        "Mercury": ["Over-thinking until paralysis", "Sketchy business partners", "Saying things you can't take back"],
        "Jupiter": ["Complacency from things going well", "Over-eating, over-spending", "Lecturing others"],
        "Venus":   ["Romantic complications outside marriage", "Over-spending on luxuries", "Conflict avoidance turning into resentment"],
        "Saturn":  ["Despair when delays hit", "Isolating instead of asking for help", "Skipping health checks"],
        "Rahu":    ["Addictions (substance, screens, gambling)", "Moral shortcuts for fast gains", "Cutting corners on the rules"],
        "Ketu":    ["Big irreversible decisions (marriage, divorce, major purchase)", "Withdrawing fully from the world", "Self-pity"],
    }
    for line in AVOID_GUIDE.get(md, ["Reckless decisions"]):
        flow.append(Paragraph(f"&bull; {line}", st["bullet"]))

    # Closing
    flow.append(Spacer(1, 0.6 * cm))
    flow.append(Paragraph(
        "<i>Astrology shows patterns and tendencies — not fixed outcomes. Your choices, effort, "
        "and relationships still shape your life. The chart is the weather forecast; you decide "
        "how to dress and where to travel.</i>",
        st["small"]))

    return flow


# ─── Footer ──────────────────────────────────────────────────────────────────

def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY_MD)
    canvas.drawCentredString(A4[0] / 2, 1.0 * cm, f"Page {doc.page}")
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, "Atro · Deep Life Reading")
    canvas.restoreState()


# ─── Main ─────────────────────────────────────────────────────────────────────

def generate(chart_path, out_path):
    with open(chart_path, encoding="utf-8") as f:
        chart = json.load(f)
    today = dt.datetime.now()
    st = styles()

    print(f"Building DEEP PDF for {chart.get('name', 'Native')}...")
    try:
        e_chart = to_engine_chart(chart)
        reports = run_engines(e_chart)
    except Exception as exc:
        print(f"  WARN: engine_bridge failed — {exc}")
        reports = []

    # Build life event timeline (full lifetime)
    b = chart["birth"]
    raw = scan_lifetime_v2(chart, b["year"], b["year"] + 80, min_severity=3)
    bands = collapse_consecutive(raw) if raw else []
    ranked_events = rank_and_consume(bands) if bands else []

    # Vimshottari MD list (returned by to_engine_chart already)
    all_mds = e_chart.vimshottari_periods or []

    # Build antardasha list per MD lord (for deep per-chapter sub-period tables)
    tl = build_full_timeline(chart, levels=2)
    from types import SimpleNamespace as _NS
    all_ads_by_md = {}
    for r in tl:
        if r.get("level") == 2:
            md_lord = r.get("md")
            all_ads_by_md.setdefault(md_lord, []).append(_NS(
                md=md_lord, ad=r.get("ad"),
                start=r["start"], end=r["end"], years=r.get("years", 0),
            ))

    # Current dasha
    ds = lookup(tl, today)
    dasha_now = {
        "md": ds.get(1, {}).get("md", "?"),
        "md_end": ds.get(1, {}).get("end"),
        "ad": ds.get(2, {}).get("ad", "?"),
        "ad_end": ds.get(2, {}).get("end"),
    }

    # Import traditional jadhagam pages
    from traditional_jadhagam_pages import (
        page_birth_details, page_planet_positions, page_rasi_navamsa,
        page_ashtakavarga, page_vimshottari_full,
        page_all_vargas, page_bhava_chart,
    )

    flow = []
    flow.extend(page_cover(chart, today, st, dasha_now))
    flow.append(PageBreak())
    # ─── TRADITIONAL JADHAGAM CHART DETAIL PAGES ───
    flow.extend(page_birth_details(chart, st))
    flow.append(PageBreak())
    flow.extend(page_planet_positions(chart, st))
    flow.append(PageBreak())
    flow.extend(page_rasi_navamsa(chart, st))
    flow.append(PageBreak())
    flow.extend(page_all_vargas(chart, st))
    flow.append(PageBreak())
    flow.extend(page_bhava_chart(chart, st))
    flow.append(PageBreak())
    flow.extend(page_ashtakavarga(chart, st))
    flow.append(PageBreak())
    # ─── HUMAN-READABLE LIFE READING PAGES ───
    flow.extend(page_personality(chart, reports, st))
    flow.append(PageBreak())
    flow.extend(page_career(chart, reports, today, st, all_mds))
    flow.append(PageBreak())
    flow.extend(page_marriage(chart, reports, ranked_events, today, st))
    flow.append(PageBreak())
    flow.extend(page_children_health(chart, reports, st))
    flow.append(PageBreak())
    flow.extend(page_spiritual_travel(chart, reports, st))
    flow.append(PageBreak())
    flow.extend(page_life_timeline(chart, all_mds, today, st, ranked_events, all_ads_by_md))
    flow.append(PageBreak())
    flow.extend(page_decade_outlook(chart, all_mds, ranked_events, today, st))
    flow.append(PageBreak())
    flow.extend(page_year_calendar(chart, ranked_events, today, st))
    flow.append(PageBreak())
    flow.extend(page_action_guide(chart, reports, dasha_now, st))
    flow.append(PageBreak())
    # ─── FULL VIMSHOTTARI TABLE AT END ───
    flow.extend(page_vimshottari_full(chart, st))

    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=2.0 * cm, rightMargin=2.0 * cm,
        topMargin=1.8 * cm, bottomMargin=2.0 * cm,
        title=f"{chart.get('name', 'Native')} — Deep Life Reading",
    )
    doc.build(flow, onFirstPage=page_footer, onLaterPages=page_footer)
    size_kb = out_path.stat().st_size // 1024
    print(f"DONE: {out_path}  ({size_kb} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True)
    ap.add_argument("--out", help="output PDF path (default: ../reports/<NAME>_DEEP.pdf)")
    args = ap.parse_args()

    chart_path = Path(args.chart)
    if args.out:
        out = Path(args.out)
    else:
        name = chart_path.stem.replace("_chart", "").upper()
        out = chart_path.parent.parent / "reports" / f"{name}_DEEP.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    generate(chart_path, out)


if __name__ == "__main__":
    main()
