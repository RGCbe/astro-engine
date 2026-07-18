"""
SUMMARY PDF GENERATOR — plain English, no jargon.

Produces a 5-page human-readable PDF.
No Sanskrit. No 'BPHS Ch.80'. No 'MD/AD/PD'. No 'Tara Chakra'.
Just clear English a normal person can read in 10 minutes.

Sections:
  Page 1 — Cover + Right Now (this year)
  Page 2 — Personality & Mind (5 plain bullets)
  Page 3 — Career & Wealth
  Page 4 — Marriage & Family
  Page 5 — Health, Spirituality, Next 5 Years timeline
"""
import sys, os, json, datetime as dt, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                 Table, TableStyle, PageBreak, KeepTogether,
                                 HRFlowable)

# Engine bridge — same data source as full report
from engine_bridge import to_engine_chart, run_engines
from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from granular_dasha import build_full_timeline, lookup
from comprehensive_yogas import detect_all_classical_yogas
try:
    from sade_sati import compute_sade_sati_periods
except Exception:
    compute_sade_sati_periods = lambda c: []

import re
def _clean_event(name):
    """Strip the redundant trailing ' Event' (and accidental doubles) from
    predictor event names for the client-facing summary."""
    s = re.sub(r"(?:\s+Event)+$", "", str(name)).strip()
    return s or "Important window"


# ── Plain-language event classifier — maps any of 167 predictor categories ──
_SKIP_CATS = ("tajik", "kp_", "mayan", "bazi", "ziwei", "_transit", "_retro",
    "progressed", "solar_arc", "personal_year", "profection", "pinnacle",
    "master_number", "karmic_number", "palmistry", "chinese_zodiac", "nadi_108",
    "galactic", "wave_spell", "pillar_change", "_palace", "uranus", "neptune", "pluto")

_THEMES = [
    (("marriage", "kalatra", "spouse", "wedding", "divorce", "partner", "widow", "love", "relationship"),
     "Marriage / relationship chapter"),
    (("child", "putra", "pregnan", "d7_", "progeny"), "Children / family growth"),
    (("father", "pitra", "matri", "matra", "mother", "parent", "sibling", "family", "ancestral", "home", "meal"),
     "Family matter"),
    (("career", "profession", "job", "honor", "royal", "govern", "board", "founder", "leader", "fame",
      "reputation", "media", "charisma", "speaking", "speech", "corporate", "franchise", "business",
      "partnership", "yasas", "karya"),
     "Career / status move"),
    (("wealth", "money", "bank", "asset", "gain", "lakshmi", "dhana", "hoard", "luxury", "comfort",
      "income", "inherit", "speculat", "fortune", "property", "land", "vehicle", "d2_", "d16_"),
     "Money / property change"),
    (("health", "disease", "roga", "eye", "tooth", "dental", "heart", "cardiac", "surger", "accident",
      "vitality", "chest", "scar", "mouth", "lip", "complexion", "beauty", "diet", "fast", "death",
      "longevity", "marana", "pet_loss", "d30_"),
     "Health matter to watch"),
    (("travel", "relocat", "trip", "adventure", "foreign", "journey"), "Travel / relocation"),
    (("educat", "vidya", "learn", "language", "intellect", "study", "knowledge", "email", "saraswati", "d24_"),
     "Learning / skills"),
    (("spiritual", "occult", "punya", "devotion", "guru", "prophecy", "karma", "d20_", "nadi"),
     "Spiritual / inner growth"),
    (("confidence", "courage", "independence", "identity", "assert", "style", "reinvent", "milestone"),
     "Personal growth / confidence"),
    (("debt", "rin", "karz", "loss", "struggle", "kemadruma", "daridra", "dosha", "clash", "challenge",
      "scandal", "betray", "dispute", "judicial", "closure", "chandala", "vish"),
     "A challenge to handle with care"),
    (("yoga", "raja", "mahapadma", "adhi", "vipareeta", "neecha_bhanga", "saham", "sudden_gain", "solar_return"),
     "A favourable period"),
]

def plain_event(category, raw_name=""):
    """Map a predictor category to a plain-English life theme, or None to skip
    (purely-technical markers a normal client doesn't need to see)."""
    c = (category or "").lower()
    if any(s in c for s in _SKIP_CATS):
        return None
    for kws, phrase in _THEMES:
        if any(k in c for k in kws):
            return phrase
    cleaned = _clean_event(raw_name)
    if (not cleaned or cleaned == "Important window"
            or re.search(r"\bd\d+\b|sub-event|amsa|saham|yoga|dosha|\brin\b|tajik|\bkp\b", cleaned, re.I)):
        return None
    return cleaned


# ── Visual "at a glance" meters — readable without literacy ────────────────
def _hx(c):
    return "#" + c.hexval()[2:]

KARAKAS = {
    "Personality & Self": ["Sun", "Moon"],
    "Career & Work": ["Sun", "Saturn", "Mercury"],
    "Money & Wealth": ["Jupiter", "Venus", "Mercury"],
    "Marriage & Love": ["Venus", "Jupiter"],
    "Health & Energy": ["Sun", "Mars"],
    "Mind & Learning": ["Mercury", "Jupiter"],
    "Luck & Blessings": ["Jupiter", "Moon"],
}

def _area_score(sb, planets):
    rs = []
    for p in planets:
        d = sb.get(p)
        if isinstance(d, dict) and d.get("total_rupas") is not None:
            thr = d.get("threshold") or 6.0
            rs.append(d["total_rupas"] / (thr or 6.0))
    if not rs:
        return 3
    r = sum(rs) / len(rs)
    return 5 if r >= 1.3 else 4 if r >= 1.05 else 3 if r >= 0.82 else 2 if r >= 0.6 else 1

def _verdict(score):
    return {5: ("Very strong", GREEN), 4: ("Strong", GREEN), 3: ("Steady", AMBER),
            2: ("Developing", AMBER), 1: ("Needs care", RED)}.get(score, ("Steady", AMBER))

def seg_meter(label, score, st):
    """One life-area row: name + a 5-segment colour bar + a one-word verdict."""
    score = max(0, min(5, int(round(score))))
    verdict, vcol = _verdict(score)
    fill = GREEN if score >= 4 else AMBER if score >= 2 else RED
    bar = Table([[""] * 5], colWidths=[0.82 * cm] * 5, rowHeights=[0.42 * cm])
    bstyle = [("BOX", (0, 0), (-1, -1), 0.5, GREY_MD),
              ("INNERGRID", (0, 0), (-1, -1), 2, white)]
    for i in range(5):
        bstyle.append(("BACKGROUND", (i, 0), (i, 0), fill if i < score else GREY_LT))
    bar.setStyle(TableStyle(bstyle))
    row = Table([[Paragraph(f"<b>{label}</b>", st["body"]), bar,
                  Paragraph(f"<b><font color='{_hx(vcol)}'>{verdict}</font></b>", st["body"])]],
                colWidths=[4.8 * cm, 4.7 * cm, 3.5 * cm])
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LEFTPADDING", (0, 0), (0, 0), 0),
                             ("TOPPADDING", (0, 0), (-1, -1), 4),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return row

def page_life_at_a_glance(chart, st):
    flow = [Paragraph("YOUR LIFE — AT A GLANCE", st["h1"]),
            Paragraph("A quick picture you can read without words: more <b>green</b> = a stronger, "
                      "more supportive area of life; <b>amber</b> = mixed; <b>red</b> = needs care. "
                      "The pages after explain each area in simple sentences.", st["small"]),
            Spacer(1, 0.35 * cm)]
    try:
        from engine.shadbala import compute_shadbala
        sb = compute_shadbala(chart)
    except Exception:
        sb = {}
    # relative strength — which areas THIS chart supports most (avoids an all-red
    # picture when the whole chart's absolute shadbala is low)
    raws = {}
    for area, planets in KARAKAS.items():
        vals = [sb[p]["total_rupas"] for p in planets
                if isinstance(sb.get(p), dict) and sb[p].get("total_rupas") is not None]
        raws[area] = (sum(vals) / len(vals)) if vals else None
    have = [v for v in raws.values() if v is not None]
    lo, hi = (min(have), max(have)) if have else (0.0, 1.0)
    span = (hi - lo) or 1.0
    for area in KARAKAS:
        v = raws.get(area)
        score = 3 if v is None else 2 + round(((v - lo) / span) * 3)
        flow.append(seg_meter(area, score, st))
    return flow


_WEEKDAY = {"Sun": "Sunday", "Moon": "Monday", "Mars": "Tuesday", "Mercury": "Wednesday",
            "Jupiter": "Thursday", "Venus": "Friday", "Saturn": "Saturday"}

def numerology_block(chart, st):
    """Plain-language lucky-numbers block — the most client-friendly section."""
    try:
        from numerology_vedic import vedic_numerology
        n = vedic_numerology(chart)
    except Exception:
        return []

    def _t(s):
        s = str(s)
        return s.split("—", 1)[-1].strip() if "—" in s else s

    flow = [Spacer(1, 0.7 * cm),
            Paragraph("YOUR NUMBERS &amp; LUCKY THINGS", st["h1"]),
            Paragraph("From the numbers in your birth date and name — simple, personal, "
                      "and easy to use day to day.", st["small"]),
            Spacer(1, 0.25 * cm)]
    flow.append(Paragraph(
        f"<b>Driver number {n['mulanka']}</b> ({n.get('mulanka_planet','')}) — your everyday "
        f"nature: {_t(n.get('mulanka_traits',''))}.", st["body"]))
    flow.append(Paragraph(
        f"<b>Destiny number {n['bhagyanka']}</b> ({n.get('bhagyanka_planet','')}) — where life "
        f"leads you: {_t(n.get('bhagyanka_traits',''))}.", st["body"]))
    flow.append(Paragraph(
        f"<b>Name number {n['name_number']}</b> ({n.get('name_planet','')}) — the feel of your "
        f"name: {_t(n.get('name_traits',''))}.", st["body"]))
    flow.append(Spacer(1, 0.3 * cm))
    lucky = [
        ("Lucky dates (any month)", ", ".join(str(d) for d in n.get('lucky_dates', [])) or "—"),
        ("Lucky day", ", ".join(_WEEKDAY.get(d, d) for d in n.get('lucky_days', [])) or "—"),
        ("Lucky colour", str(n.get('lucky_color', '') or "—")),
        ("Lucky gemstone", str(n.get('lucky_gemstone', '') or "—")),
    ]
    t = Table([[Paragraph(f"<b>{k}</b>", st["bullet"]), Paragraph(v, st["bullet"])]
               for k, v in lucky],
              colWidths=[5.5 * cm, 8.0 * cm])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CREAM, white]),
        ("BOX", (0, 0), (-1, -1), 0.6, GOLD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    flow.append(t)
    return flow


def page_numerology(chart, st):
    """Rich numerology page (advanced engine) — Lo Shu grid visual, master
    numbers, Personal-Year forecast, lucky things. Falls back to the simple
    block if the advanced engine is unavailable."""
    import os
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _root not in sys.path:
        sys.path.insert(0, _root)
    name = chart.get("name", "")
    b = chart["birth"]
    date_iso = f"{b['year']:04d}-{b['month']:02d}-{b['day']:02d}"
    try:
        from engine.numerology_engine import compute_numerology_report
        c = compute_numerology_report(name, date_iso, dt.date.today().isoformat())["calculations"]
        tc, py, ls, cyc = (c["tamil_chaldean"], c["pythagorean_triad"],
                           c["lo_shu_grid"], c["temporal_cycles"])
    except Exception:
        return numerology_block(chart, st)

    flow = [Paragraph("YOUR NUMBERS &amp; LUCKY THINGS", st["h1"]),
            Paragraph("From the numbers in your birth date and name — simple, personal, easy to use.",
                      st["small"]), Spacer(1, 0.25 * cm)]
    flow.append(Paragraph(f"<b>Driver number {tc['vidhi_number']}</b> ({tc['vidhi_planet']}) — "
                          f"your everyday personality.", st["body"]))
    flow.append(Paragraph(f"<b>Destiny number {tc['bhagya_number']}</b> ({tc['bhagya_planet']}) — "
                          f"where your life is heading.", st["body"]))
    flow.append(Paragraph(f"<b>Heart's-desire number {py.get('soul_urge_number')}</b> — what you "
                          f"most want inside. {py.get('soul_urge_note','')}", st["body"]))
    flow.append(Spacer(1, 0.45 * cm))

    flow.append(Paragraph("YOUR YEAR AHEAD", st["h2"]))
    flow.append(Paragraph(f"You are in a <b>Personal Year {cyc['personal_year']}</b> "
                          f"({str(cyc.get('target_date',''))[:4]}): {cyc.get('personal_year_meaning','')}",
                          st["body"]))
    flow.append(Spacer(1, 0.45 * cm))

    flow.append(Paragraph("YOUR NUMBER MAP", st["h2"]))
    flow.append(Paragraph("Each box is a number from your birth date. <b>Gold</b> = you have it "
                          "(more digits = stronger); <b>grey</b> = missing, a quality to grow.",
                          st["small"]))
    flow.append(Spacer(1, 0.15 * cm))
    counts = {int(k): int(v) for k, v in (ls.get("digit_counts", {}) or {}).items()}
    LAYOUT = [[4, 9, 2], [3, 5, 7], [8, 1, 6]]
    grid_rows = [[Paragraph(f"<b>{str(num) * counts.get(num, 0) if counts.get(num, 0) else num}</b>",
                            st["body"]) for num in row] for row in LAYOUT]
    g = Table(grid_rows, colWidths=[2.3 * cm] * 3, rowHeights=[1.5 * cm] * 3, hAlign="LEFT")
    gstyle = [("GRID", (0, 0), (-1, -1), 1, GOLD), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
    for ri, row in enumerate(LAYOUT):
        for ci, num in enumerate(row):
            present = counts.get(num, 0) > 0
            gstyle.append(("BACKGROUND", (ci, ri), (ci, ri), CREAM if present else white))
            gstyle.append(("TEXTCOLOR", (ci, ri), (ci, ri), TEXT if present else GREY_LT))
    g.setStyle(TableStyle(gstyle))
    flow.append(g)
    flow.append(Spacer(1, 0.45 * cm))

    flow.append(Paragraph("YOUR LUCKY THINGS", st["h2"]))
    lucky = [
        ("Lucky dates (any month)", ", ".join(str(d) for d in tc.get("lucky_dates", [])) or "—"),
        ("Lucky days", ", ".join(tc.get("lucky_days", [])) or "—"),
        ("Lucky direction", str(tc.get("lucky_direction", "") or "—")),
        ("Lucky colour", str(tc.get("lucky_color", "") or "—")),
        ("Lucky gemstone", str(tc.get("lucky_gemstone", "") or "—")),
    ]
    t = Table([[Paragraph(f"<b>{k}</b>", st["bullet"]), Paragraph(v, st["bullet"])] for k, v in lucky],
              colWidths=[5.2 * cm, 8.3 * cm])
    t.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CREAM, white]),
        ("BOX", (0, 0), (-1, -1), 0.6, GOLD),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    flow.append(t)
    return flow

# Colors — warm calming palette
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


# ─────────────────────────────────────────────────────────────────────────────
#  TRANSLATION DICTIONARIES — convert Sanskrit → plain English
# ─────────────────────────────────────────────────────────────────────────────

# Maha-dasha lord → plain-English life theme
MD_THEME_PLAIN = {
    "Sun":     "authority + visibility + father themes",
    "Moon":    "emotional growth + family + public visibility",
    "Mars":    "action + competition + courage themes",
    "Mercury": "communication + business + skill-building",
    "Jupiter": "expansion + wisdom + good fortune",
    "Venus":   "relationships + comforts + creative joy",
    "Saturn":  "discipline + hard work + responsibility",
    "Rahu":    "ambition + unconventional gains + risk",
    "Ketu":    "detachment + spirituality + endings",
}

# Antardasha sub-period flavour
AD_FLAVOR = {
    "Sun": "with new authority", "Moon": "with emotional shifts",
    "Mars": "with decisive action", "Mercury": "with new ideas",
    "Jupiter": "with blessings", "Venus": "with relational joy",
    "Saturn": "with serious responsibility", "Rahu": "with sudden change",
    "Ketu": "with letting go",
}

# House numbers → plain English meaning
HOUSE_PLAIN = {
    1: "yourself / personality / body",
    2: "money, family, speech",
    3: "siblings, courage, communication",
    4: "home, mother, comforts",
    5: "children, creativity, romance",
    6: "work, health, daily routine",
    7: "marriage, partnerships, public",
    8: "transformation, hidden matters, longevity",
    9: "father, dharma, higher learning, luck",
    10: "career, public role, achievement",
    11: "income, friends, big goals",
    12: "expenses, foreign lands, spirituality, sleep",
}

# Planet → simple essence
PLANET_ESSENCE = {
    "Sun":     "self-confidence and authority",
    "Moon":    "emotions and mind",
    "Mars":    "energy and courage",
    "Mercury": "thinking and speech",
    "Jupiter": "wisdom and blessings",
    "Venus":   "love and beauty",
    "Saturn":  "discipline and patience",
    "Rahu":   "obsessive desire",
    "Ketu":   "letting go and spiritual insight",
}


def _safe(s, n=300):
    """Strip junk + truncate. Engine outputs may have OCR garbage."""
    if not s: return ""
    s = str(s)
    s = "".join(c for c in s if c.isprintable() or c == "\n" or c == " ")
    if len(s) > n: s = s[:n] + "..."
    return s


def _age(birth_dt, target):
    return (target - birth_dt).days / 365.25


# ─────────────────────────────────────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────────────────────────────────────

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
    out["body"] = ParagraphStyle("body", parent=base["Normal"],
        fontName="Helvetica", fontSize=10.5, textColor=TEXT,
        spaceAfter=6, leading=15, alignment=TA_JUSTIFY)
    out["bullet"] = ParagraphStyle("bullet", parent=base["Normal"],
        fontName="Helvetica", fontSize=10.5, textColor=TEXT,
        leftIndent=14, spaceAfter=5, leading=14, bulletIndent=4)
    out["callout"] = ParagraphStyle("callout", parent=base["Normal"],
        fontName="Helvetica-Bold", fontSize=11, textColor=INDIGO,
        spaceBefore=4, spaceAfter=4, leading=14,
        leftIndent=10, rightIndent=10, borderColor=GOLD, borderWidth=0,
        backColor=CREAM)
    out["small"] = ParagraphStyle("small", parent=base["Normal"],
        fontName="Helvetica", fontSize=9, textColor=GREY_MD,
        spaceAfter=3, leading=12)
    return out


def divider():
    return HRFlowable(width="100%", thickness=0.6, color=GOLD,
                       spaceBefore=4, spaceAfter=8)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 1 — Cover + Right Now
# ─────────────────────────────────────────────────────────────────────────────

def page_cover_and_now(chart, e_chart, today, st):
    flow = []
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    name = chart.get("name", "Native")
    age = _age(birth_dt, today)

    # Title
    flow.append(Paragraph(name.upper(), st["title"]))
    flow.append(Paragraph("Your Life Reading — Simple English", st["subtitle"]))
    flow.append(divider())

    # Birth info
    flow.append(Paragraph(
        f"<b>Born</b>: {b['day']:02d} {dt.date(2000, b['month'], 1).strftime('%B')} {b['year']} "
        f"at {b.get('hour', 0):02d}:{b.get('min', 0):02d} in {b.get('place_en') or b.get('place', '—')}",
        st["body"]))
    flow.append(Paragraph(
        f"<b>Today</b>: {today.strftime('%d %B %Y')} &nbsp;·&nbsp; <b>Age</b>: {age:.0f} years",
        st["body"]))
    flow.append(Spacer(1, 0.5 * cm))

    # ── RIGHT NOW BOX ──
    flow.append(Paragraph("WHERE YOU ARE RIGHT NOW", st["h1"]))

    # Current MD
    tl = build_full_timeline(chart, levels=2)
    ds = lookup(tl, today)
    md_rec = ds.get(1, {})
    ad_rec = ds.get(2, {})
    md = md_rec.get("md", "?")
    ad = ad_rec.get("ad", "?")
    md_end = md_rec.get("end")
    ad_end = ad_rec.get("end")
    md_theme = MD_THEME_PLAIN.get(md, "growth")
    ad_flav = AD_FLAVOR.get(ad, "")

    if md_end:
        years_left_md = max(0, (md_end - today).days // 365)
        flow.append(Paragraph(
            f"You are in a long <b>{md} period</b> until <b>{md_end.strftime('%B %Y')}</b> "
            f"(about <b>{years_left_md} more years</b>). The big life theme during this period is "
            f"<b>{md_theme}</b>.",
            st["body"]))

    if ad_end:
        flow.append(Paragraph(
            f"Inside this, the next sub-chapter lasts until <b>{ad_end.strftime('%B %Y')}</b> — "
            f"it brings the {md} themes <b>{ad_flav}</b>.",
            st["body"]))

    # Sade Sati / heads-up
    flow.append(Spacer(1, 0.3 * cm))
    sade = compute_sade_sati_periods(chart) if compute_sade_sati_periods else []
    in_sade = False
    if isinstance(sade, list):
        for ph in sade:
            s = ph.get("start"); e = ph.get("end")
            if s and e:
                try:
                    if (isinstance(s, dt.datetime) and isinstance(e, dt.datetime) and s <= today <= e):
                        in_sade = True; sade_end = e; break
                except Exception:
                    pass
    if in_sade:
        flow.append(Paragraph(
            f"<b>Heads up:</b> You are currently in a 7.5-year Saturn pressure cycle "
            f"(called <i>Sade Sati</i>) until {sade_end.strftime('%B %Y')}. This usually means "
            f"hard work, slower results, and lessons in patience. Things solidify by the end of it.",
            st["callout"]))
    flow.append(Spacer(1, 0.4 * cm))

    # 18-month outlook
    flow.append(Paragraph("THE NEXT 18 MONTHS", st["h2"]))

    raw = scan_lifetime_v2(chart, today.year, today.year + 2, min_severity=3)
    bands = collapse_consecutive(raw) if raw else []
    ranked = rank_and_consume(bands) if bands else []
    # Filter to events starting within 18 months
    horizon = today + dt.timedelta(days=18 * 30)
    near = [b for b in ranked
            if b.get("window_start") and b["window_start"] <= horizon
            and (b.get("window_end") is None or b["window_end"] >= today)]
    near.sort(key=lambda b: b["window_start"])

    EVENT_PLAIN = {
        "marriage": "a marriage / serious relationship window",
        "relationship_phase": "a relationship deepening period",
        "career": "a career breakthrough or promotion",
        "wealth": "a wealth peak or new income source",
        "children": "a child / family expansion event",
        "health": "a health flag — watch your routines",
        "self_accident": "physical-injury risk — drive carefully, avoid risky sports",
        "father": "a father-related event (his health, your relationship with him)",
        "spiritual": "a spiritual awakening / life-reorientation moment",
        "travel": "travel or relocation",
        "education": "new learning or major exam",
    }

    near = [e for e in near if plain_event(e.get("category", ""), e.get("event", ""))]
    if near:
        seen = set(); shown = 0
        for ev in near:
            plain = plain_event(ev.get("category", ""), ev.get("event", ""))
            if plain in seen:
                continue
            seen.add(plain)
            start = max(ev["window_start"], today)
            ws = start.strftime("%b %Y")
            we = ev["window_end"].strftime("%b %Y") if ev.get("window_end") else ws
            label = f"{ws} - {we}" if ws != we else ws
            flow.append(Paragraph(f"&bull; <b>{label}</b> — {plain}", st["bullet"]))
            shown += 1
            if shown >= 5:
                break
    else:
        flow.append(Paragraph(
            "No major life-event windows flagged in the next 18 months. "
            "A steady, building period — good time to focus on long-term goals.",
            st["body"]))

    return flow


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 2 — Personality
# ─────────────────────────────────────────────────────────────────────────────

def page_personality(reports, chart, st):
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

    # Strengths — dedupe by plain-English text so 3 Raja Yoga lines don't repeat
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
        "Chandra-Mangala": "earning power through real-estate, food, or hospitality",
    }
    seen_plain = set()
    if yogas_r:
        for y in getattr(yogas_r, "predictions", [])[:12]:
            label = getattr(y, "label", "")
            plain = None
            for k, v in YOGA_PLAIN.items():
                if k.lower() in label.lower():
                    plain = v; break
            if plain and plain not in seen_plain:
                seen_plain.add(plain)
                flow.append(Paragraph(f"&bull; {plain}", st["bullet"]))
                if len(seen_plain) >= 4: break

    if not seen_plain:
        flow.append(Paragraph(
            "&bull; A balanced chart — your strength is steady consistency rather than dramatic peaks.",
            st["bullet"]))

    # Challenges / things to watch (counter-balance to strengths)
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Things to watch for</b>", st["h2"]))
    pos = chart["positions"]
    challenges = []
    # Sun in dusthana
    sun_h = pos.get("Sun", {}).get("house", 0)
    if sun_h in (6, 8, 12):
        challenges.append("difficulty getting recognition from authority figures — work twice as hard for credit")
    # Mars in dosha houses (already classical "manglik")
    mars_h = pos.get("Mars", {}).get("house", 0)
    if mars_h in (1, 4, 7, 8, 12):
        challenges.append("hot temper or impulsive choices — slow down before big decisions")
    # Saturn in dusthana
    sat_h = pos.get("Saturn", {}).get("house", 0)
    if sat_h in (6, 8, 12):
        challenges.append("delays and slow progress in certain life areas — patience is your real lesson")
    # Mercury combust
    moon_h = pos.get("Moon", {}).get("house", 0)
    if moon_h in (6, 8, 12):
        challenges.append("ups and downs in mood — emotional stability needs active management (meditation, routine)")
    if not challenges:
        challenges.append("no major built-in challenges — your work is to use your strengths consistently")
    for c in challenges[:3]:
        flow.append(Paragraph(f"&bull; {c}", st["bullet"]))

    return flow


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 3 — Career & Wealth
# ─────────────────────────────────────────────────────────────────────────────

def page_career_wealth(reports, chart, today, st):
    flow = []
    flow.append(Paragraph("CAREER & WEALTH", st["h1"]))
    flow.append(divider())

    career = next((r for r in reports if getattr(r, "category", "") == "career"), None)
    wealth = next((r for r in reports if getattr(r, "category", "") == "wealth"), None)
    edu = next((r for r in reports if getattr(r, "category", "") == "education"), None)

    # CAREER
    flow.append(Paragraph("<b>Career — what fits you</b>", st["h2"]))
    if career:
        for p in career.predictions[:5]:
            label = p.label
            val = p.value
            if isinstance(val, dict):
                val = "; ".join(f"{k}: {v}" for k, v in val.items())
            # Skip overly technical labels
            CAREER_TRANSLATE = {
                "Industries / fields the chart suits": "Best-fit fields",
                "Secondary industries (via 10th-lord placement)": "Also fits",
                "Self-employed vs salaried lean": "Work style",
                "Career peak window": "Your peak years will be",
                "Authority over others": "Leadership ability",
                "Government / public-sector pull": "Public-sector pull",
            }
            plain_label = CAREER_TRANSLATE.get(label, label)
            flow.append(Paragraph(
                f"&bull; <b>{plain_label}:</b> {_safe(val, 200)}",
                st["bullet"]))

    # WEALTH
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Money — how it comes to you</b>", st["h2"]))
    if wealth:
        for p in wealth.predictions[:5]:
            label = p.label
            val = p.value
            if isinstance(val, dict):
                val = "; ".join(f"{k}: {v}" for k, v in val.items())
            WEALTH_TRANSLATE = {
                "Primary wealth-channel (savings axis)": "Main savings source",
                "Gains / income channel": "Main income source",
                "Wealth peak windows": "Years when money will flow",
                "Asset preference": "What you'll naturally accumulate",
                "Saver vs spender": "Spending tendency",
                "Debt tendency": "Debt risk",
                "Property": "Property ownership",
            }
            plain_label = WEALTH_TRANSLATE.get(label, label)
            # Translate "mahadashas" → "periods"
            val_clean = str(val).replace("mahadashas", "periods").replace("mahadasha", "period")
            flow.append(Paragraph(
                f"&bull; <b>{plain_label}:</b> {_safe(val_clean, 200)}",
                st["bullet"]))

    # EDUCATION (brief)
    if edu and edu.predictions:
        flow.append(Spacer(1, 0.3 * cm))
        flow.append(Paragraph("<b>Subjects you naturally take to</b>", st["h2"]))
        top = edu.predictions[0]
        flow.append(Paragraph(
            f"&bull; {_safe(top.value, 200)}",
            st["bullet"]))
        if len(edu.predictions) > 1:
            alts = [_safe(p.value, 50) for p in edu.predictions[1:4]]
            flow.append(Paragraph(
                f"&bull; Other fits: {', '.join(alts)}",
                st["bullet"]))

    return flow


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 4 — Marriage & Family
# ─────────────────────────────────────────────────────────────────────────────

def page_marriage_family(reports, chart, today, st):
    flow = []
    flow.append(Paragraph("MARRIAGE & FAMILY", st["h1"]))
    flow.append(divider())

    marr = next((r for r in reports if getattr(r, "category", "") == "marriage"), None)
    children = next((r for r in reports if getattr(r, "category", "") == "children"), None)
    family = next((r for r in reports if getattr(r, "category", "") == "family"), None)

    # MARRIAGE
    flow.append(Paragraph("<b>Marriage</b>", st["h2"]))
    if marr:
        MARRIAGE_TRANSLATE = {
            "Probable marriage age window": "Most likely marriage age",
            "Spouse profile (from 7th sign)": "Spouse's nature",
            "Mangal Dosha": "Mars-warning for marriage match",
            "Marriage harmony tendency": "Overall harmony in marriage",
            "Number-of-marriages signal": "Number of marriages indicated",
            "Spouse community / background lean": "Spouse may come from",
            "Children's success potential": "Children's success",
        }
        for p in marr.predictions[:6]:
            label = p.label
            val = p.value
            if isinstance(val, dict):
                val = ", ".join(f"{k}={v}" for k, v in val.items() if k in ("verdict","conf"))
            val_str = str(val)
            # Translate "Mangal Dosha" answers
            if "Mangal" in label:
                if val_str.startswith("yes"):
                    val_str = "Yes — Mars sits in a marriage-friction position. Best matched with another Mars-affected chart, or has standard cancellations."
                elif val_str == "no":
                    val_str = "No — no Mars issue for matching."
            # Translate "STRONG/MODERATE — cross-community"
            if "STRONG" in val_str or "MODERATE" in val_str:
                if "MODERATE" in val_str:
                    val_str = "moderate lean toward a partner from a different community / background"
                elif "STRONG" in val_str:
                    val_str = "strong indicators that partner comes from a different community / region / background"
                elif "NO cross" in val_str:
                    val_str = "spouse most likely from your own community"
            plain_label = MARRIAGE_TRANSLATE.get(label, label)
            flow.append(Paragraph(
                f"&bull; <b>{plain_label}:</b> {_safe(val_str, 220)}",
                st["bullet"]))

    # CHILDREN
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Children</b>", st["h2"]))
    if children:
        CHILD_TRANSLATE = {
            "Family-size lean": "Family size likely",
            "Gender tendency (classical, weak)": "Gender lean (weak signal)",
            "Children's success potential": "How your children will do",
            "Fertility blessing": "Fertility indicator",
        }
        for p in children.predictions[:4]:
            val = p.value
            if isinstance(val, dict):
                val = "; ".join(f"{k}: {v}" for k, v in val.items())
            plain_label = CHILD_TRANSLATE.get(p.label, p.label)
            flow.append(Paragraph(
                f"&bull; <b>{plain_label}:</b> {_safe(val, 200)}",
                st["bullet"]))

    # FAMILY
    if family and family.predictions:
        flow.append(Spacer(1, 0.3 * cm))
        flow.append(Paragraph("<b>Parents & siblings</b>", st["h2"]))
        FAMILY_TRANSLATE = {
            "Father — status & relationship": "Father",
            "Mother — status & relationship": "Mother",
            "Sibling — relationship": "Siblings",
            "Inheritance prospects": "Inheritance",
        }
        for p in family.predictions[:4]:
            val = p.value
            if isinstance(val, dict):
                val = "; ".join(f"{k}: {v}" for k, v in val.items())
            plain_label = FAMILY_TRANSLATE.get(p.label, p.label)
            flow.append(Paragraph(
                f"&bull; <b>{plain_label}:</b> {_safe(val, 200)}",
                st["bullet"]))

    return flow


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 5 — Health, Spirituality, Next 5 Years
# ─────────────────────────────────────────────────────────────────────────────

def page_health_spiritual_timeline(reports, chart, today, st):
    flow = []
    flow.append(Paragraph("HEALTH, SPIRITUALITY & THE NEXT 5 YEARS", st["h1"]))
    flow.append(divider())

    health = next((r for r in reports if getattr(r, "category", "") == "health"), None)
    spirit = next((r for r in reports if getattr(r, "category", "") == "spirituality"), None)
    foreign = next((r for r in reports if getattr(r, "category", "") == "foreign"), None)

    # HEALTH — strip jargon ("malefic transits to lagna or 8th house" etc.)
    def _strip_jargon(s):
        s = str(s)
        replacements = {
            "malefic transits to lagna or 8th house": "difficult planetary periods (Mars/Saturn/Rahu)",
            "malefic transits": "difficult planetary periods",
            "lagna or 8th house": "your sense of self or transformation periods",
            "lagna": "your body / sense of self",
            "8th house": "transformation periods",
            "6th house": "work + health routine",
            "dusthana": "stress zone",
            "Marana Karaka Sthana": "death-position",
            "marana karaka sthana": "death-position",
            "peak_dashas": "main periods to watch",
            "Vimshottari": "main planetary timeline",
            "mahadasha": "main period",
            "antardasha": "sub-period",
            "bhakti": "devotional",
            "sadhana": "practice",
            "puja": "ritual worship",
            "mantra": "chanting",
        }
        for k, v in replacements.items():
            s = s.replace(k, v)
        return s

    flow.append(Paragraph("<b>Health</b>", st["h2"]))
    if health and health.predictions:
        for p in health.predictions[:3]:
            val = p.value
            if isinstance(val, dict):
                nature = val.get("nature", "")
                body = val.get("body_part", "")
                peaks = val.get("peak_dashas", [])
                v_parts = []
                if nature: v_parts.append(nature)
                if body: v_parts.append(f"(affects: {body})")
                if peaks: v_parts.append(f"Be more careful during {', '.join(peaks)} planetary periods.")
                val = " ".join(v_parts)
            flow.append(Paragraph(f"&bull; {_strip_jargon(_safe(val, 280))}", st["bullet"]))
    else:
        flow.append(Paragraph(
            "&bull; No major built-in health risks. Standard healthy-lifestyle care applies — sleep, diet, regular checkups.",
            st["bullet"]))

    # SPIRITUALITY — also strip jargon
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph("<b>Spirituality</b>", st["h2"]))
    if spirit and spirit.predictions:
        SPIRIT_TRANSLATE = {
            "Spiritual path lean": "Best spiritual path for you",
            "Guru / teacher bond": "Teacher / mentor connection",
            "Religious participation tendency": "Religious participation style",
            "Mantra / sadhana inclination": "Inclination toward chanting / spiritual practice",
        }
        for p in spirit.predictions[:4]:
            val = p.value
            if isinstance(val, dict):
                val = "; ".join(f"{k}: {v}" for k, v in val.items())
            val_str = _strip_jargon(str(val))
            plain_label = SPIRIT_TRANSLATE.get(p.label, p.label)
            flow.append(Paragraph(
                f"&bull; <b>{plain_label}:</b> {_safe(val_str, 200)}",
                st["bullet"]))

    # FOREIGN
    if foreign and foreign.predictions:
        flow.append(Spacer(1, 0.3 * cm))
        flow.append(Paragraph("<b>Travel & foreign lands</b>", st["h2"]))
        FOREIGN_TRANSLATE = {
            "Foreign-settlement likelihood": "Chance of foreign settlement",
            "Foreign-direction lean": "Direction (geographic)",
            "Most likely trigger window": "When it's most likely",
        }
        for p in foreign.predictions[:3]:
            val = p.value
            if isinstance(val, dict):
                val = "; ".join(f"{k}: {v}" for k, v in val.items())
            val_str = str(val)
            # Translate "Rahu mahadasha + 12th-lord activations" -> human
            val_str = val_str.replace("mahadasha", "period").replace("12th-lord activations", "foreign-house activation")
            plain_label = FOREIGN_TRANSLATE.get(p.label, p.label)
            flow.append(Paragraph(
                f"&bull; <b>{plain_label}:</b> {_safe(val_str, 200)}",
                st["bullet"]))

    # ── NEXT 5 YEARS TIMELINE ──
    flow.append(Spacer(1, 0.5 * cm))
    flow.append(Paragraph("WHAT TO EXPECT — NEXT 5 YEARS", st["h2"]))

    raw = scan_lifetime_v2(chart, today.year, today.year + 5, min_severity=3)
    bands = collapse_consecutive(raw) if raw else []
    ranked = rank_and_consume(bands) if bands else []
    horizon = today + dt.timedelta(days=5 * 365)
    near = [b for b in ranked if b.get("window_start") and today <= b["window_start"] <= horizon]
    near.sort(key=lambda b: b["window_start"])

    EVENT_PLAIN = {
        "marriage": "Marriage / serious-relationship window",
        "relationship_phase": "Relationship deepening",
        "career": "Career breakthrough / promotion",
        "wealth": "Wealth peak / new income",
        "children": "Child / family expansion",
        "health": "Health flag — watch routines",
        "self_accident": "Physical-injury risk — drive carefully",
        "father": "Father-related event",
        "spiritual": "Spiritual awakening / life shift",
    }

    near = [e for e in near if plain_event(e.get("category", ""), e.get("event", ""))]
    if near:
        rows = [["When", "What"]]
        seen = set()
        for ev in near:
            text = plain_event(ev.get("category", ""), ev.get("event", ""))
            if text in seen:
                continue
            seen.add(text)
            ws = ev["window_start"].strftime("%b %Y")
            we = ev["window_end"].strftime("%b %Y") if ev.get("window_end") else ws
            label = f"{ws}" if ws == we else f"{ws} - {we}"
            rows.append([
                Paragraph(f"<b>{label}</b>", st["bullet"]),
                Paragraph(text, st["bullet"]),
            ])
            if len(rows) > 10:
                break
        t = Table(rows, colWidths=[3.6 * cm, 12.4 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
            ("TEXTCOLOR", (0, 0), (-1, 0), CREAM),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, GREY_LT]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("LINEBELOW", (0, 0), (-1, 0), 1.2, GOLD),
        ]))
        flow.append(t)
    else:
        flow.append(Paragraph(
            "No major flagged events in the next 5 years. This is a steady building period — "
            "ideal for focused long-term work.",
            st["body"]))

    flow.append(Spacer(1, 0.6 * cm))
    flow.append(Paragraph(
        "<i>This is a starting guide based on your birth chart. Astrology shows tendencies, not "
        "fixed outcomes. Your choices still shape your life — the chart shows the "
        "weather, you decide how to dress.</i>",
        st["small"]))

    return flow


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE NUMBER
# ─────────────────────────────────────────────────────────────────────────────

def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY_MD)
    canvas.drawCentredString(A4[0] / 2, 1.0 * cm, f"Page {doc.page}")
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.0 * cm, "Atro · Plain-English Reading")
    canvas.restoreState()


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────

def generate(chart_path, out_path):
    with open(chart_path, encoding="utf-8") as f:
        chart = json.load(f)
    today = dt.datetime.now()
    st = styles()

    # Build engine reports once
    print(f"Building summary PDF for {chart.get('name', 'Native')}...")
    try:
        e_chart = to_engine_chart(chart)
        reports = run_engines(e_chart)
    except Exception as exc:
        print(f"  WARN: engine_bridge failed — {exc}")
        reports = []

    flow = []
    flow.extend(page_cover_and_now(chart, None, today, st))
    flow.append(PageBreak())
    flow.extend(page_life_at_a_glance(chart, st))
    flow.append(PageBreak())
    flow.extend(page_numerology(chart, st))
    flow.append(PageBreak())
    flow.extend(page_personality(reports, chart, st))
    flow.append(PageBreak())
    flow.extend(page_career_wealth(reports, chart, today, st))
    flow.append(PageBreak())
    flow.extend(page_marriage_family(reports, chart, today, st))
    flow.append(PageBreak())
    flow.extend(page_health_spiritual_timeline(reports, chart, today, st))

    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=2.0 * cm, rightMargin=2.0 * cm,
        topMargin=1.8 * cm, bottomMargin=2.0 * cm,
        title=f"{chart.get('name', 'Native')} — Life Reading",
    )
    doc.build(flow, onFirstPage=page_footer, onLaterPages=page_footer)
    size_kb = out_path.stat().st_size // 1024
    print(f"DONE: {out_path}  ({size_kb} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True, help="path to chart JSON")
    ap.add_argument("--out", help="output PDF path (default: ../reports/<NAME>_SUMMARY.pdf)")
    args = ap.parse_args()

    chart_path = Path(args.chart)
    if args.out:
        out = Path(args.out)
    else:
        name = chart_path.stem.replace("_chart", "").upper()
        out = chart_path.parent.parent / "reports" / f"{name}_SUMMARY.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    generate(chart_path, out)


if __name__ == "__main__":
    main()
