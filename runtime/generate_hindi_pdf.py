"""
TAMIL DEEP PDF GENERATOR — proper Tamil text shaping via uharfbuzz.

Uses tamil_renderer.TamilParagraph (HarfBuzz-shaped Bezier glyphs) instead of
ReportLab's broken Paragraph for all Tamil text. Mixed Tamil+Latin handled.

Pages:
  1   — Cover + Now
  2   — Birth details + Panchanga + Janma Nakshatra
  3   — Planet positions
  4   — Yogas
  5   — Rasi (D1) + Navamsa (D9)
  6+  — 9 Maha Dasha chapters
"""
import sys, os, json, datetime as dt, argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.stdout.reconfigure(encoding="utf-8")

from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.platypus import (SimpleDocTemplate, Spacer, Table, TableStyle,
                                 PageBreak, HRFlowable)

# Import our HarfBuzz-based Tamil renderer
from tamil_renderer import TamilParagraph, draw_tamil, measure_mixed
from engine_bridge import to_engine_chart, run_engines
from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from granular_dasha import build_full_timeline, lookup
from comprehensive_yogas import detect_all_classical_yogas
from hindi_translations import (
    RASIS_HI, PLANETS_HI, PLANETS_HI_SHORT, NAKSHATRAS_HI, WEEKDAYS_HI,
    TITHIS_HI, PAKSHA_HI, KARANAS_HI, YOGAS_PANCH_HI, HOUSES_HI,
    SECTION_HEADERS_HI, LABELS_HI, MD_THEME_HI, MD_EXPECT_HI, EVENT_PLAIN_HI,
    YOGA_PLAIN_HI,
)

# Colors
INDIGO   = HexColor("#312e81")
GOLD     = HexColor("#b88a37")
CREAM    = HexColor("#fef6e4")
GREY_LT  = HexColor("#f3f0e8")
GREY_MD  = HexColor("#6b6b6b")
TEXT     = HexColor("#1f1b14")
ACCENT   = HexColor("#7e3a96")
GREEN    = HexColor("#16a34a")
RED      = HexColor("#c0392b")


def _hi_planet(p): return PLANETS_HI.get(p, p)
def _hi_rasi(r): return RASIS_HI.get(r, r)
def _hi_nak(n): return NAKSHATRAS_HI.get(n, n)
def _hi_weekday(w): return WEEKDAYS_HI.get(w, w)
def _hi_section(k): return SECTION_HEADERS_HI.get(k, k)
def _hi_label(k): return LABELS_HI.get(k, k)


def _age(birth_dt, target):
    return (target - birth_dt).days / 365.25


def divider(thick=0.6):
    return HRFlowable(width="100%", thickness=thick, color=GOLD,
                       spaceBefore=4, spaceAfter=8)


# ── Hindi month names for date display ───────────────────────────────────────
HINDI_MONTHS = {1:"जनवरी",2:"फरवरी",3:"मार्च",4:"अप्रैल",
                 5:"मई",6:"जून",7:"जुलाई",8:"अगस्त",
                 9:"सितंबर",10:"अक्टूबर",11:"नवंबर",12:"दिसंबर"}

def fmt_my_hi(d):
    """Format date as 'मार्च 2026'."""
    return f"{HINDI_MONTHS.get(d.month, '?')} {d.year}"


def fmt_dmy_hi(d):
    """Format date as '17 मार्च 2026'."""
    return f"{d.day} {HINDI_MONTHS.get(d.month, '?')} {d.year}"


# ── Style presets (font sizes only — TamilParagraph handles rendering) ──────

STYLES = {
    "title":    dict(font_size=24, bold=True, color=INDIGO, align="center", leading=1.4, space_after=2),
    "subtitle": dict(font_size=13, color=GREY_MD, align="center", leading=1.4, space_after=12),
    "h1":       dict(font_size=16, bold=True, color=INDIGO, leading=1.4, space_after=6),
    "h2":       dict(font_size=12.5, bold=True, color=ACCENT, leading=1.5, space_after=4),
    "h3":       dict(font_size=11, bold=True, color=INDIGO, leading=1.4, space_after=3),
    "body":     dict(font_size=10.5, color=TEXT, leading=1.55, space_after=4, align="justify"),
    "bullet":   dict(font_size=10.5, color=TEXT, leading=1.45, space_after=3, indent=12),
    "cell":     dict(font_size=9.5, color=TEXT, leading=1.3, space_after=0),
    "cell_bold":dict(font_size=10, bold=True, color=INDIGO, leading=1.3, space_after=0),
    "cell_small":dict(font_size=8.5, color=TEXT, leading=1.2, space_after=0),
    "small":    dict(font_size=9, color=GREY_MD, leading=1.4, space_after=2),
    "callout":  dict(font_size=11, bold=True, color=INDIGO, leading=1.5, space_after=4),
    "chapter":  dict(font_size=18, bold=True, color=GOLD, leading=1.3, space_after=2),
    "footnote": dict(font_size=8, color=GREY_MD, leading=1.3, space_after=2, align="center"),
}


def TP(text, style_key="body", **overrides):
    """Shortcut: TamilParagraph with named style."""
    s = dict(STYLES.get(style_key, STYLES["body"]))
    s.update(overrides)
    return TamilParagraph(text, **s)


# ════════════════════════════════════════════════════════════════════════════
#  PAGE 1: Cover + Right Now
# ════════════════════════════════════════════════════════════════════════════

def page_cover(chart, today, st_unused, dasha_now):
    flow = []
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))
    name = chart.get("name", "—")
    age = _age(birth_dt, today)
    weekday_ta = _hi_weekday(b.get("weekday", ""))

    flow.append(TP(name.upper(), "title"))
    flow.append(TP(_hi_section("DEEP_LIFE_READING"), "subtitle"))
    
    # Center the zodiac character illustration
    import os
    from reportlab.platypus import Image as RLImage
    runtime_dir = os.path.dirname(os.path.abspath(__file__))
    rasi_clean = str(chart.get("moon_rasi", "")).strip().lower()
    img_name = f"{rasi_clean}_character.png"
    img_path = os.path.join(runtime_dir, img_name)
    fallback_path = os.path.join(runtime_dir, "zodiac_flat_icon.png")
    
    selected_path = None
    if os.path.exists(img_path):
        selected_path = img_path
    elif os.path.exists(fallback_path):
        selected_path = fallback_path
        
    if selected_path:
        flow.append(RLImage(selected_path, width=2.5*cm, height=2.5*cm, hAlign="CENTER"))
        flow.append(Spacer(1, 0.3*cm))

    flow.append(divider())

    flow.append(TP(f"{_hi_label('Date of birth')}: {b['day']:02d}-{b['month']:02d}-{b['year']} ({weekday_ta})", "body"))
    flow.append(TP(f"{_hi_label('Time of birth')}: {b.get('hour', 0):02d}:{b.get('min', 0):02d} IST", "body"))
    flow.append(TP(f"{_hi_label('Place')}: {b.get('place', '—')}", "body"))
    flow.append(TP(f"आज की तिथि: {fmt_dmy_hi(today)}    वर्तमान आयु: {int(age)} वर्ष", "body"))
    flow.append(Spacer(1, 0.4*cm))

    flow.append(TP(_hi_section("WHERE_NOW"), "h1"))

    md = dasha_now["md"]; md_end = dasha_now["md_end"]
    ad = dasha_now["ad"]; ad_end = dasha_now["ad_end"]

    if md_end:
        years_left = max(0, (md_end - today).days // 365)
        md_ta = _hi_planet(md)
        theme = MD_THEME_HI.get(md, "")
        flow.append(TP(
            f"நீங்கள் वर्तमान में {md_ta} महादशा में हैं, जो "
            f"{fmt_my_hi(md_end)} तक चलेगी (अभी {years_left} ஆண்டுகள்). "
            f"இந்த महादशा का முக்கிய கருப்பொருள்: {theme}.",
            "body"))

    if ad_end:
        ad_ta = _hi_planet(ad)
        flow.append(TP(
            f"இதற்குள், தற்போதைய உப-தசை {fmt_my_hi(ad_end)} வரை — "
            f"{_hi_planet(md)} கருப்பொருளுடன் {ad_ta} தாக்கம் சேர்க்கிறது.",
            "body"))

    flow.append(Spacer(1, 0.3*cm))
    flow.append(TP(_hi_section("NEXT_18_MONTHS"), "h2"))

    raw = scan_lifetime_v2(chart, today.year, today.year + 2, min_severity=3)
    bands = collapse_consecutive(raw) if raw else []
    ranked = rank_and_consume(bands) if bands else []
    horizon = today + dt.timedelta(days=18 * 30)
    near = [b for b in ranked if b.get("window_start") and b["window_start"] <= horizon]
    near.sort(key=lambda b: b["window_start"])

    if near:
        for ev in near[:6]:
            cat = ev.get("category", "")
            plain = EVENT_PLAIN_HI.get(cat, ev.get("event", ""))
            ws = fmt_my_hi(ev["window_start"])
            we = fmt_my_hi(ev["window_end"]) if ev.get("window_end") else ws
            stars = ev.get("stars", "")
            label = f"{ws} - {we}" if ws != we else ws
            flow.append(TP(f"•  {label} — {plain} {stars}", "bullet"))
    else:
        flow.append(TP(
            "அடுத்த 18 மாதங்களில் முக்கிய நிகழ்வுகள் எதுவும் குறிக்கப்படவில்லை. "
            "நிலையான வளர்ச்சி காலம் - நீண்ட கால இலக்குகளில் கவனம் செலுத்துவதற்கு நல்ல நேரம்.",
            "body"))

    return flow


# ════════════════════════════════════════════════════════════════════════════
#  PAGE 2: Birth Details + Panchanga + Janma Nakshatra
# ════════════════════════════════════════════════════════════════════════════

def page_birth_panchanga(chart, st_unused):
    flow = []
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))

    flow.append(TP(_hi_section("BIRTH_DETAILS_PANCHANGA"), "h1"))
    flow.append(divider())

    # Birth + chart essentials as a clean two-column list (using TamilParagraph rows)
    # Get moon pada with fallback to positions.Moon.pada
    moon_pada = chart.get("moon_pada") or chart.get("positions", {}).get("Moon", {}).get("pada", "—")
    rows = [
        (_hi_label("Name"), chart.get("name", "—")),
        (_hi_label("Date of birth"), f"{b['day']:02d}-{b['month']:02d}-{b['year']} ({_hi_weekday(b.get('weekday', ''))})"),
        (_hi_label("Time of birth"), f"{b.get('hour', 0):02d}:{b.get('min', 0):02d} IST"),
        (_hi_label("Place"), b.get("place", "—")),
        (_hi_label("Lat/Lon"), f"{b.get('lat','?')} N, {b.get('lon','?')} E"),
        (_hi_label("Ayanamsa"), f"{chart.get('ayanamsa', '?')} (லாஹிரி)"),
        (_hi_label("Lagna"), f"{_hi_rasi(chart.get('lagna','?'))}  ({chart.get('lagna_deg', 0):.2f} பாகை)"),
        (_hi_label("Lagna lord"), _hi_planet(chart.get("lagna_lord", "?"))),
        (_hi_label("Moon Rasi"), _hi_rasi(chart.get("moon_rasi", "?"))),
        (_hi_label("Janma Nakshatra"), f"{_hi_nak(chart.get('janma_nakshatra', '?'))} ({moon_pada} ஆம் பாதம்)"),
        (_hi_label("Nakshatra lord"), _hi_planet(chart.get("janma_nakshatra_lord", "?"))),
    ]
    # Build table with TamilParagraph cells (compact)
    table_data = [[TP(k, "cell_bold"), TP(v, "cell")] for k, v in rows]
    t = Table(table_data, colWidths=[5*cm, 11*cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("LINEBELOW", (0,6), (-1,6), 0.5, GOLD),  # divider after birth essentials
    ]))
    flow.append(t)

    # Panchanga
    flow.append(Spacer(1, 0.4*cm))
    flow.append(TP("பிறப்பின் போதைய பஞ்சாங்கம்", "h2"))

    panch_rows = []
    try:
        import swisseph as swe
        lat = float(b.get("lat", 0)); lon = float(b.get("lon", 0)); tz = float(b.get("tz", 5.5))
        utc_noon = dt.datetime(b["year"], b["month"], b["day"], 12 - int(tz), 0)
        jd0 = swe.julday(utc_noon.year, utc_noon.month, utc_noon.day, 0)
        sr = swe.rise_trans(jd0 - 0.5, swe.SUN, lon, lat, 0, 0, 0, swe.CALC_RISE)
        ss = swe.rise_trans(jd0 - 0.5, swe.SUN, lon, lat, 0, 0, 0, swe.CALC_SET)
        if sr[0] == 0 and ss[0] == 0:
            sr_jd = sr[1][0]; ss_jd = ss[1][0]
            _, _, _, sr_h = swe.revjul(sr_jd + tz/24)
            _, _, _, ss_h = swe.revjul(ss_jd + tz/24)
            sr_hh = int(sr_h); sr_mm = int((sr_h - sr_hh)*60)
            ss_hh = int(ss_h); ss_mm = int((ss_h - ss_hh)*60)
            day_hours = (ss_jd - sr_jd) * 24
            panch_rows.append((_hi_label("Sunrise"), f"{sr_hh:02d}:{sr_mm:02d} காலை"))
            panch_rows.append((_hi_label("Sunset"), f"{ss_hh:02d}:{ss_mm:02d} மாலை"))
            panch_rows.append((_hi_label("Day duration"), f"{int(day_hours)} மணி {int((day_hours - int(day_hours))*60)} நிமிடம்"))
    except Exception:
        pass

    try:
        from panchanga import compute_panchanga
        p = compute_panchanga(birth_dt)
        panch_rows.extend([
            (_hi_label("Tithi"), f"{TITHIS_HI.get(p.get('tithi', ''), p.get('tithi', '?'))} ({PAKSHA_HI.get(p.get('paksha',''), p.get('paksha','?'))})"),
            (_hi_label("Vara"), _hi_weekday(p.get('vara', '?'))),
            (_hi_label("Yoga"), YOGAS_PANCH_HI.get(p.get('yoga', ''), p.get('yoga', '?'))),
            (_hi_label("Karana"), KARANAS_HI.get(p.get('karana', ''), p.get('karana', '?'))),
        ])
    except Exception:
        pass

    if panch_rows:
        td = [[TP(k, "cell_bold"), TP(v, "cell")] for k, v in panch_rows]
        t = Table(td, colWidths=[5*cm, 11*cm])
        t.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
        ]))
        flow.append(t)

    # Janma Nakshatra
    flow.append(Spacer(1, 0.35*cm))
    flow.append(TP("உங்கள் ஜன்ம நட்சத்திரத்தின் முழு விவரம்", "h2"))

    # Tamil translations for nakshatra detail values
    # Nakshatra deities (all 27)
    DEITY_TA = {
        "Ashvini Kumaras": "அஸ்விணி குமாரர்கள் (தெய்வீக மருத்துவர்கள்)",
        "Yama": "யமன் (மரண தேவன்)", "Agni": "அக்னி (நெருப்புத் தேவன்)",
        "Brahma": "பிரம்மா (படைப்புத் தேவன்)", "Soma": "சோமன் (சந்திரன்)",
        "Rudra": "ருத்திரன் (சிவன்)", "Aditi": "அதிதி (கிரகங்களின் தாய்)",
        "Brihaspati": "பிரகஸ்பதி (குருத் தேவன்)", "Nagas": "நாகங்கள் (சர்ப்பங்கள்)",
        "Pitrs": "பித்ருக்கள் (மூதாதையர்கள்)", "Pitrs (ancestors)": "பித்ருக்கள் (மூதாதையர்கள்)",
        "Bhaga": "பகன் (நல்வாழ்வு தேவன்)", "Aryaman": "ஆர்யமன் (உடன்பிறப்புத் தேவன்)",
        "Savitr": "சவித்ரு (சூரியன்)", "Tvashtr": "த்வஷ்டா (தெய்வீக தச்சர்)",
        "Vayu": "வாயு (காற்றுத் தேவன்)", "Indra-Agni": "இந்திரன்-அக்னி",
        "Mitra": "மித்திரன் (நட்புத் தேவன்)", "Indra": "இந்திரன் (தேவர் தலைவன்)",
        "Nirriti": "நிர்ருதி (அழிவுத் தேவன்)", "Apas": "ஆபஸ் (நீர் தேவதைகள்)",
        "Vishvedevas": "விஷ்வேதேவர்கள் (சர்வ தேவர்கள்)",
        "Vishnu": "விஷ்ணு (பாதுகாப்புத் தேவன்)",
        "Vasus": "வசுக்கள் (செல்வத் தேவர்கள்)", "Varuna": "வருணன் (நீர் தேவன்)",
        "Varuna (cosmic waters)": "வருணன் (பிரபஞ்ச நீர்)",
        "Aja Ekapada": "அஜ ஏகபாதன் (ஒற்றைக்கால் ஆடு)",
        "Ahir Budhnya": "அஹிர் புத்னியா (கடல் அடிநாகம்)",
        "Pushan": "பூஷன் (பேணும் தேவன்)",
    }
    # Common symbols
    SYMBOL_TA = {
        "Horse's head": "குதிரை தலை", "Female reproductive organ": "பெண் இனப்பெருக்க உறுப்பு",
        "Razor / Knife": "கத்தி", "Cart": "வண்டி", "Deer's head": "மான் தலை",
        "Teardrop": "கண்ணீர் துளி", "Quiver of arrows": "அம்புக்கூடு",
        "Cow's udder": "பசு மடி", "Coiled snake": "சுருண்ட பாம்பு",
        "Royal throne": "அரச சிம்மாசனம்", "Front legs of bed": "கட்டில் முன்கால்கள்",
        "Back legs of bed": "கட்டில் பின்கால்கள்", "Hand": "கை",
        "Bright jewel": "பிரகாசமான ரத்தினம்", "Coral": "பவளம்",
        "Decorated gateway": "அலங்காரத் தோரணம்", "Lotus": "தாமரை",
        "Earring / Umbrella": "காதணி / குடை", "Lion's tail": "சிங்கத்தின் வால்",
        "Tusk of elephant": "யானைத் தந்தம்", "Elephant tusk": "யானைத் தந்தம்",
        "Three footprints": "மூன்று கால்தடம்", "Ear": "காது",
        "Drum / Flute": "மிருதங்கம் / புல்லாங்குழல்", "Empty circle": "வெற்று வட்டம்",
        "Sword": "வாள்", "Twin": "இரட்டை", "Fish": "மீன்",
        "Swing": "ஊஞ்சல்", "Lute / Bow": "வீணை / வில்",
    }
    GANA_TA = {"Deva": "தேவ", "Manushya": "மனுஷ்ய", "Rakshasa": "ராக்ஷஸ"}
    NADI_TA = {"Adi": "ஆதி", "Madhya": "மத்திய", "Antya": "அந்த்ய"}
    YONI_TA = {"Horse":"குதிரை","Elephant":"யானை","Sheep":"செம்மறி","Snake":"பாம்பு",
               "Dog":"நாய்","Cat":"பூனை","Rat":"எலி","Cow":"பசு","Buffalo":"எருமை",
               "Tiger":"புலி","Deer":"மான்","Monkey":"குரங்கு","Mongoose":"கீரிப்பிள்ளை","Lion":"சிங்கம்"}
    MUKHA_TA = {"Urdhvamukha":"உர்த்வமுகம் (மேல்நோக்கி)",
                "Adhomukha":"அதோமுகம் (கீழ்நோக்கி)",
                "Tiryangmukha":"திர்யங்முகம் (குறுக்கே)"}
    DIR_TA = {"East":"கிழக்கு","West":"மேற்கு","North":"வடக்கு","South":"தெற்கு",
              "Northeast":"வடகிழக்கு","Northwest":"வடமேற்கு",
              "Southeast":"தென்கிழக்கு","Southwest":"தென்மேற்கு"}
    ELEM_TA = {"Fire":"நெருப்பு","Water":"நீர்","Earth":"பூமி","Air":"காற்று","Ether":"ஆகாயம்"}
    COLOR_TA = {"Red":"சிவப்பு","Blue":"நீலம்","Green":"பச்சை","Yellow":"மஞ்சள்",
                "White":"வெள்ளை","Black":"கருப்பு","Ivory":"தந்தநிறம்","Gold":"தங்க நிறம்",
                "Brown":"பழுப்பு","Pink":"இளஞ்சிவப்பு","Orange":"ஆரஞ்சு","Purple":"ஊதா"}
    BODY_TA = {"Head":"தலை","Eyes":"கண்கள்","Face":"முகம்","Ears":"காதுகள்","Nose":"மூக்கு",
               "Mouth":"வாய்","Throat":"தொண்டை","Neck":"கழுத்து","Shoulders":"தோள்கள்",
               "Chest":"நெஞ்சு","Heart":"இதயம்","Arms":"கைகள்","Hands":"உள்ளங்கைகள்",
               "Stomach":"வயிறு","Hips":"இடுப்பு","Genitals":"பிறப்புறுப்பு","Thighs":"தொடைகள்",
               "Knees":"முழங்கால்கள்","Legs":"கால்கள்","Feet":"பாதங்கள்","Spine":"முதுகெலும்பு"}

    def _trans_nak_val(key, val):
        """Translate English nakshatra-detail values to Tamil."""
        if not val: return val
        v = str(val).strip()
        if key == "gana": return GANA_TA.get(v, v)
        if key == "nadi": return NADI_TA.get(v, v)
        if key == "yoni": return YONI_TA.get(v, v)
        if key == "mukha": return MUKHA_TA.get(v, v)
        if key == "direction": return DIR_TA.get(v, v)
        if key == "element": return ELEM_TA.get(v, v)
        if key == "color": return COLOR_TA.get(v, v)
        if key == "body_part": return BODY_TA.get(v, v)
        if key == "deity": return DEITY_TA.get(v, v)
        if key == "symbol": return SYMBOL_TA.get(v, v)
        return v

    try:
        from tara_chakra import get_nakshatra_full
        nak_data = get_nakshatra_full(chart.get("janma_nakshatra", ""))
        if nak_data:
            label_map = [
                ("name", "பெயர்"), ("number", "எண்"), ("lord", "அதிபதி"),
                ("deity", "தேவதை"), ("gana", "கணம்"), ("yoni", "யோனி"),
                ("nadi", "நாடி"), ("mukha", "முகம்"), ("direction", "திக்கு"),
                ("symbol", "சின்னம்"), ("body_part", "உடல் பகுதி"),
                ("color", "நிறம்"), ("element", "தத்துவம்"),
            ]
            rows = []
            for k, label_ta in label_map:
                v = nak_data.get(k)
                if v:
                    if k == "name": v = _hi_nak(v)
                    elif k == "lord": v = _hi_planet(v)
                    else: v = _trans_nak_val(k, v)
                    rows.append([TP(label_ta, "cell_bold"), TP(str(v), "cell")])
            if rows:
                t = Table(rows, colWidths=[4*cm, 12*cm])
                t.setStyle(TableStyle([
                    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
                    ("TOPPADDING", (0,0), (-1,-1), 4),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                    ("LEFTPADDING", (0,0), (-1,-1), 8),
                ]))
                flow.append(t)
    except Exception:
        pass

    return flow


# ════════════════════════════════════════════════════════════════════════════
#  PAGE 3: Planet Positions
# ════════════════════════════════════════════════════════════════════════════

def page_planets(chart, st_unused):
    flow = []
    flow.append(TP(_hi_section("PLANETARY_POSITIONS"), "h1"))
    flow.append(divider())
    flow.append(TP(
        "உங்கள் ஜாதகத்தில் கிரகங்கள் எந்த ராசியில், எந்த வீட்டில், என்ன பாகையில் "
        "மற்றும் எந்த நட்சத்திரத்தில் அமர்ந்துள்ளன என்பதைக் காட்டுகிறது.",
        "small"))
    flow.append(Spacer(1, 0.15*cm))

    pos = chart["positions"]
    PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    def _dms(deg):
        try:
            d = int(deg); rest = (deg - d) * 60
            m = int(rest); s = int((rest - m) * 60)
            return f"{d:02d}° {m:02d}' {s:02d}\""
        except Exception:
            return "—"

    # Header cells need WHITE text on INDIGO bg (cell_bold uses INDIGO text which is invisible)
    header = [
        TP("கிரகம்", "cell_bold", color=CREAM),
        TP("ராசி", "cell_bold", color=CREAM),
        TP("வீடு", "cell_bold", color=CREAM),
        TP("பாகை", "cell_bold", color=CREAM),
        TP("நட்சத்திரம்", "cell_bold", color=CREAM),
        TP("பாதம்", "cell_bold", color=CREAM),
        TP("வக்.", "cell_bold", color=CREAM),
    ]
    rows = [header]
    for p in PLANET_ORDER:
        if p not in pos: continue
        pd = pos[p]
        retro = "வக்ரம்" if pd.get("retrograde") else ""
        rows.append([
            TP(_hi_planet(p), "cell_bold"),
            TP(_hi_rasi(pd.get("rasi", "—")), "cell"),
            TP(f"{pd.get('house', '?')}", "cell", align="center"),
            TP(_dms(pd.get("deg", 0)), "cell_small"),
            TP(_hi_nak(pd.get("nak", "—")), "cell"),
            TP(str(pd.get("pada", "—")), "cell", align="center"),
            TP(retro, "cell_small", color=RED, align="center"),
        ])
    # Lagna row — read lagna_deg with explicit fallback
    lagna_deg = chart.get("lagna_deg")
    if lagna_deg is None or lagna_deg == 0:
        # Try lagna_lon - sign_offset
        lagna_lon = chart.get("lagna_lon")
        if lagna_lon is not None:
            lagna_deg = float(lagna_lon) % 30.0
        else:
            lagna_deg = 0
    rows.append([
        TP("லக்னம்", "cell_bold", color=INDIGO),
        TP(_hi_rasi(chart.get("lagna", "—")), "cell"),
        TP("1", "cell", align="center"),
        TP(_dms(lagna_deg), "cell_small"),
        TP("—", "cell", align="center"),
        TP("—", "cell", align="center"),
        TP("", "cell"),
    ])
    try:
        from upagrahas import compute_upagrahas
        upg = compute_upagrahas(chart)
        for upg_name in ["Mandi", "Gulika"]:
            if upg_name in upg:
                u = upg[upg_name]
                rows.append([
                    TP(_hi_planet(upg_name), "cell_bold", color=ACCENT),
                    TP(_hi_rasi(u.get("rasi", "—")), "cell"),
                    TP(f"{u.get('house', '?')}", "cell", align="center"),
                    TP(_dms(u.get("deg", 0)), "cell_small"),
                    TP("—", "cell", align="center"),
                    TP("—", "cell", align="center"),
                    TP("", "cell"),
                ])
    except Exception:
        pass

    # Wider column for planet name (allows long names), narrow for house # only
    t = Table(rows, colWidths=[2.4*cm, 2.5*cm, 1.0*cm, 2.5*cm, 4.2*cm, 1.0*cm, 1.4*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), INDIGO),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("LINEBELOW", (0,0), (-1,0), 1.2, GOLD),
        ("LINEABOVE", (0,-2), (-1,-2), 0.5, GOLD),  # accent line above Lagna/upagrahas
    ]))
    flow.append(t)

    # Quick interpretation note
    flow.append(Spacer(1, 0.3*cm))
    flow.append(TP("சுருக்கம்:", "h3"))
    # Get moon pada from positions if not in top level
    moon_pada = chart.get("moon_pada") or pos.get("Moon", {}).get("pada", "—")
    flow.append(TP(
        f"உங்கள் லக்னம் {_hi_rasi(chart.get('lagna','?'))} ஆகும், இதன் அதிபதி "
        f"{_hi_planet(chart.get('lagna_lord','?'))}. சந்திரன் "
        f"{_hi_rasi(chart.get('moon_rasi','?'))} ராசியில் இருப்பதால் இது உங்கள் ஜன்ம ராசி. "
        f"ஜன்ம நட்சத்திரம் {_hi_nak(chart.get('janma_nakshatra','?'))} "
        f"({moon_pada} ஆம் பாதம்), நட்சத்திர அதிபதி "
        f"{_hi_planet(chart.get('janma_nakshatra_lord','?'))}. "
        f"ஆரம்ப விம்ஷோத்தரி தசை {_hi_planet(chart.get('janma_nakshatra_lord','?'))} தசை.",
        "body"))
    return flow


# ════════════════════════════════════════════════════════════════════════════
#  PAGE 4: Yogas
# ════════════════════════════════════════════════════════════════════════════

def page_yogas(chart, st_unused):
    flow = []
    flow.append(TP(_hi_section("YOGAS_DETECTED"), "h1"))
    flow.append(divider())
    flow.append(TP(
        "யோகங்கள் என்பவை குறிப்பிட்ட வாழ்க்கை பலன்களை தரும் சிறப்பு கிரக சேர்க்கைகள். "
        "உங்கள் ஜாதகத்திலிருந்து BPHS / பலதீபிகா விதிகளின் அடிப்படையில் கண்டறியப்பட்டது.",
        "small"))
    flow.append(Spacer(1, 0.2*cm))

    try:
        yogas = detect_all_classical_yogas(chart)
        if yogas:
            for y in yogas[:10]:
                name = y.get("name", "?")
                sev = y.get("severity", 0)
                # Use ASCII-safe stars (Helvetica has * and o)
                filled = min(5, max(1, sev))
                stars = "*" * filled + "." * (5 - filled)
                interp_ta = None
                for k, v in YOGA_PLAIN_HI.items():
                    if k in name:
                        interp_ta = v; break
                interp = interp_ta or (y.get("interpretation", "") or "")[:160]
                flow.append(TP(f"•  {name}    {stars}", "bullet", bold=True, color=GOLD))
                flow.append(TP(f"   {interp}", "bullet", color=ACCENT, font_size=10))
                flow.append(Spacer(1, 0.1*cm))
        else:
            flow.append(TP("(எந்த முக்கிய யோகங்களும் கண்டறியப்படவில்லை)", "body"))
    except Exception as exc:
        flow.append(TP(f"(யோக கண்டறிதல் தோல்வி: {exc})", "body"))

    return flow


# ════════════════════════════════════════════════════════════════════════════
#  PAGE 5: 9 Maha Dasha chapters (one per page)
# ════════════════════════════════════════════════════════════════════════════

MD_WATCH_TA = {
    "Sun":     ["அதிகாரத்துடன் கர்வ மோதல்", "சூரியன் பலவீனமாக இருந்தால் தந்தையின் ஆரோக்கியம்", "அதிக உழைப்பால் சோர்வு"],
    "Moon":    ["உணர்ச்சி ஏற்ற இறக்கங்கள்", "தாய் / வீட்டில் அதிக பற்று", "திரவ தேக்கம்"],
    "Mars":    ["விபத்துகள், வெட்டுக்கள், அறுவை சிகிச்சைகள்", "கோபம் நண்பர்களை இழக்கச் செய்யும்", "இரத்த அழுத்தம்"],
    "Mercury": ["அதிக சிந்தனை செயலிழக்கச் செய்யும்", "பேச்சு / நரம்பு பிரச்சினைகள்", "சந்தேகத்திற்குரிய வணிக தொடர்புகள்"],
    "Jupiter": ["எடை அதிகரிப்பு, கல்லீரல்", "அதிக நம்பிக்கையால் ஆபத்துகளை தவறவிடல்", "திருப்தி வேக இழப்பு"],
    "Venus":   ["உறவில் சிக்கல்கள்", "சொகுசு / வசதியில் அதிக செலவு", "இனப்பெருக்க / சிறுநீரக பிரச்சினைகள்"],
    "Saturn":  ["மனச்சோர்வு, நாள்பட்ட வலி", "தனிமை", "பொறுமையை சோதிக்கும் தாமதங்கள்"],
    "Rahu":    ["போதைகள், வெறி கொண்ட ஆசைகள், கவலை", "தார்மீக குறுக்குவழிகள்", "வெளிநாட்டு ஆபத்து"],
    "Ketu":    ["தனிமை மற்றும் குழப்பம்", "தெளிவற்ற நோய்கள்", "திசை இழப்பு"],
}

MD_DO_TA = {
    "Sun":     ["தலைமை பொறுப்புகளை ஏற்றுக்கொள்ளுங்கள்", "தந்தையுடன் சமாதானம் செய்யுங்கள்", "பொது பேச்சு"],
    "Moon":    ["தாய் + குடும்ப பெண்களுடன் உறவை வலுப்படுத்துங்கள்", "உள்ளுணர்வை நம்புங்கள்", "தூக்கம், உணர்ச்சியை கவனியுங்கள்"],
    "Mars":    ["சொத்து வாங்குங்கள்", "தொய்வுற்ற இலக்குகளில் முன்னெடுப்பு எடுங்கள்", "உடற்பயிற்சி முக்கியம்"],
    "Mercury": ["புதிய திறன்கள் கற்றுக்கொள்ளுங்கள்", "தீவிர தொடர்பு வளர்க்கவும்", "சிறு வணிகம் தொடங்குங்கள்"],
    "Jupiter": ["திருமணம் / குழந்தை திட்டமிட்டிருந்தால்", "உயர்கல்வி / ஆசிரியர் பணி", "முக்கிய நீண்ட கால முதலீடுகள்"],
    "Venus":   ["திருமணம் அல்லது உறவை ஆழப்படுத்துங்கள்", "படைப்பு + வடிவமைப்பு பணிகள்", "வணிக கூட்டாண்மை"],
    "Saturn":  ["நீண்ட கால அமைப்புகளை கட்டுங்கள்", "ஆரோக்கிய வழக்கங்களில் தொடர்ந்து இருங்கள்", "கீழே உள்ளவர்களுக்கு உதவுங்கள்"],
    "Rahu":    ["கணக்கிட்ட ஆபத்துகளை எடுக்கவும்", "வெளிநாட்டினருடன் தொடர்பு", "அவசர காப்பு நிதி கட்டவும்"],
    "Ketu":    ["முடிந்தவற்றை விட்டுவிடுங்கள்", "தியான பயிற்சியை ஆழப்படுத்துங்கள்", "திரைக்குப் பின்னால் வேலை"],
}

MD_AVOID_TA = {
    "Sun":     ["அதிகாரத்துடன் கர்வ போர்", "தற்பெருமை கருத்துகளை கேட்க தடை", "புகழுக்காக ஓய்வை தவிர்த்தல்"],
    "Moon":    ["குறைவான மனநிலையில் முடிவுகள்", "வசதியில் அதிக பற்று", "கஷ்டப்படும்போது தனிமைப்படுதல்"],
    "Mars":    ["பொறுப்பற்ற வேகம் (ஓட்டுதல்)", "முக்கிய பேச்சுகளில் கோபம்", "பாலங்களை எரிப்பது"],
    "Mercury": ["அதிக ஆராய்ச்சியால் முடிவெடுக்க முடியாமை", "சந்தேகத்திற்குரிய கூட்டாளர்கள்", "திரும்ப எடுக்க முடியாதவற்றை சொல்வது"],
    "Jupiter": ["வெற்றியால் திருப்தி", "அதிக உண்ணுதல் / அதிக செலவு", "பாடம் சொல்வது"],
    "Venus":   ["காதல் சிக்கல்கள்", "சொகுசில் அதிக செலவு", "மோதலை தவிர்த்தல்"],
    "Saturn":  ["தாமதங்களின் போது விரக்தி", "உதவி கேட்காமல் தனிமை", "ஆரோக்கிய சோதனைகள் தவிர்த்தல்"],
    "Rahu":    ["அடிமைத்தனங்கள்", "வேக லாபங்களுக்கான குறுக்குவழிகள்", "விதிகளை மீறுதல்"],
    "Ketu":    ["பெரிய திரும்ப முடியாத முடிவுகள்", "உலகிலிருந்து விலகுதல்", "சுய பரிதாபம்"],
}


# ════════════════════════════════════════════════════════════════════════════
#  Book Citations & Bhrigu Patrika — 970 BPHS/Phaladeepika/Saravali rules
# ════════════════════════════════════════════════════════════════════════════

# Tamil names for source books — for friendly display
BOOK_TA = {
    "BPHS_Vol1": "ப்ரிஹத் பராசர ஹோர சாஸ்திரம் (BPHS Vol.1)",
    "BPHS_Vol2": "ப்ரிஹத் பராசர ஹோர சாஸ்திரம் (BPHS Vol.2)",
    "Brihat_Parashara_v2": "ப்ரிஹத் பராசர ஹோர சாஸ்திரம் (Vol.2)",
    "Phaladeepika": "பலதீபிகா",
    "Saravali": "சாரவளி",
    "Brihat_Jataka": "ப்ரிஹத் ஜாதகம் (வராஹமிஹிரர்)",
    "Hora_Sara": "ஹோர சாரம்",
    "Jataka_Parijata": "ஜாதக பாரிஜாதம்",
    "Sarvartha_Chintamani": "சர்வார்த்த சிந்தாமணி",
    "Jaimini_Sutras": "ஜைமினி சூத்திரம்",
    "Uttara_Kalamrita": "உத்தர காலாம்ருதம்",
    "Prashna_Marga": "ப்ரஸ்ன மார்க்கம்",
    "Muhurtha_Chintamani": "முகூர்த்த சிந்தாமணி",
    "Laghu_Parashari": "லகு பராசரி",
    "Yavanajataka_1": "யவன ஜாதகம் (Vol.1)",
    "Yavanajataka_2": "யவன ஜாதகம் (Vol.2)",
    "Bhrigu_Samhita": "ப்ருகு சம்ஹிதை",
    "Bhrigu_Naadi_Sangraha": "ப்ருகு நாடி சங்கிரகம்",
    "Bhavartha_Ratnakara_Raman": "பாவார்த்த ரத்னாகரம்",
    "Chamatkar_Chintamani": "சமத்கார சிந்தாமணி",
}


def _book_ta(book_en):
    """Translate book name to Tamil + English fallback."""
    return BOOK_TA.get(book_en, book_en.replace("_", " "))


def _render_book_citations(e_chart, category, st_unused=None, max_items=4):
    """Build flowables for book-cited predictions for a category.
    Returns list of TamilParagraph flowables.
    """
    flow = []
    try:
        from engine import book_rules
        preds = book_rules.predictions_for(e_chart, category, max_per_category=max_items)
        if not preds: return flow
        flow.append(Spacer(1, 0.2*cm))
        flow.append(TP("📜 பாரம்பரிய நூல்களின் வாக்கியங்கள்", "h3"))
        flow.append(TP(
            "உங்கள் ஜாதகத்தில் உள்ள கிரக சேர்க்கைகளுக்கு கீழ்க்கண்ட "
            "பாரம்பரிய நூல்கள் இவ்வாறு கூறுகின்றன:",
            "small"))
        for p in preds[:max_items]:
            label = p.label or "—"
            value = str(p.value) if p.value else ""
            cits = ", ".join(_book_ta(c.book) for c in (p.citations or []) if c.book)
            # Show: combination → prediction (English) → citation
            flow.append(Spacer(1, 0.1*cm))
            flow.append(TP(f"▸ {label}", "cell_bold", color=INDIGO))
            if value:
                # Truncate to keep readable
                v = value[:250].strip()
                if len(value) > 250: v += "..."
                flow.append(TP(v, "cell"))
            if cits:
                flow.append(TP(f"நூல்: {cits}", "small", color=ACCENT))
    except Exception as exc:
        flow.append(TP(f"(book_rules பிழை: {exc})", "small"))
    return flow


def page_life_domains_ta(chart, e_chart):
    """One page per life-domain (marriage, career, wealth, children, health,
    foreign, spirituality, personality) with book-cited predictions.
    """
    flow = []
    flow.append(TP("வாழ்க்கை துறை முன்னறிவிப்புகள்", "h1"))
    flow.append(divider())
    flow.append(TP(
        "உங்கள் ஜாதகத்தில் உள்ள கிரக சேர்க்கைகளுக்கு பிஹசெ்பிஎஸ், பலதீபிகா, "
        "சாரவளி, ஜைமினி சூத்திரம், ப்ரஸ்ன மார்க்கம் போன்ற 22 பாரம்பரிய நூல்களில் "
        "இருந்து பொருந்தும் வாக்கியங்கள் கீழே:",
        "body"))
    flow.append(Spacer(1, 0.3*cm))

    DOMAIN_MAP = [
        ("marriage", "💍 திருமணம் மற்றும் கூட்டாண்மை"),
        ("career", "💼 தொழில் மற்றும் வேலை"),
        ("wealth", "💰 செல்வம் மற்றும் பணம்"),
        ("children", "👶 குழந்தைகள் மற்றும் சந்ததி"),
        ("health", "🏥 ஆரோக்கியம்"),
        ("foreign", "🌏 வெளிநாட்டு பயணம்"),
        ("spirituality", "🕉 ஆன்மீகம் மற்றும் தர்மம்"),
        ("personality", "🎭 சுபாவம்"),
    ]
    for cat, title in DOMAIN_MAP:
        try:
            from engine import book_rules
            preds = book_rules.predictions_for(e_chart, cat, max_per_category=4)
        except Exception:
            preds = []
        if not preds:
            continue
        flow.append(Spacer(1, 0.3*cm))
        flow.append(TP(title, "h2"))
        for p in preds[:4]:
            label = p.label or ""
            value = (str(p.value) if p.value else "").strip()
            if len(value) > 280:
                value = value[:280] + "..."
            cits = ", ".join(_book_ta(c.book) for c in (p.citations or []) if c.book)
            flow.append(Spacer(1, 0.1*cm))
            flow.append(TP(f"▸ {label}", "cell_bold", color=INDIGO))
            if value:
                flow.append(TP(value, "cell"))
            if cits:
                flow.append(TP(f"நூல்: {cits}", "small", color=ACCENT))
    return flow


def page_bhrigu_patrika_ta(chart, e_chart):
    """Bhrigu Patrika predictions — uses English synthesized cells (skips Hindi raw text)."""
    flow = []
    flow.append(TP("ப்ருகு பத்திரிகா முன்னறிவிப்பு", "h1"))
    flow.append(divider())
    flow.append(TP(
        "ப்ருகு பத்திரிகா (Bhrigu Patrika) என்பது ப்ருகு முனிவரால் தொகுக்கப்பட்ட "
        "1042 கல லட்சண நூல். ஒவ்வொரு லக்னத்திற்கும், ஒவ்வொரு வீட்டிற்கும், "
        "ஒவ்வொரு கிரகத்திற்கும் தனித்தனி பலன்கள் கூறப்பட்டுள்ளன.",
        "body"))
    flow.append(Spacer(1, 0.2*cm))
    flow.append(TP(
        f"உங்கள் லக்னம் {_hi_rasi(chart.get('lagna','?'))} — உங்கள் ஜாதகத்தில் "
        f"உள்ள ஒவ்வொரு கிரகத்திற்கும் ப்ருகு பத்திரிகா கூறும் பலன்கள் கீழே:",
        "small", color=ACCENT))
    flow.append(Spacer(1, 0.3*cm))

    # Load BOTH: synthesized cells (English text) + raw Hindi rules (English structure)
    try:
        from pathlib import Path
        sc_path = Path(__file__).resolve().parent.parent / "logic_base" / "bhrigu_synthesized_cells.json"
        bp_path = Path(__file__).resolve().parent.parent / "logic_base" / "bhrigu_rules.json"
        cells = json.load(open(sc_path, encoding="utf-8")).get("synthesized_cells", [])
        bp_rules = json.load(open(bp_path, encoding="utf-8"))
    except Exception as e:
        flow.append(TP(f"(ப்ருகு தரவு கிடைக்கவில்லை: {e})", "small"))
        return flow

    # Lookup uses lowercase Sanskrit lagna name
    lagna_en = chart.get("lagna", "")
    lagna_lookup = {
        "Aries":"mesha","Taurus":"vrishabha","Gemini":"mithuna","Cancer":"karka",
        "Leo":"simha","Virgo":"kanya","Libra":"tula","Scorpio":"vrishchika",
        "Sagittarius":"dhanu","Capricorn":"makara","Aquarius":"kumbha","Pisces":"meena",
    }
    lagna_key = lagna_lookup.get(lagna_en, "")

    matched = [c for c in cells if c.get("lagna", "").lower() == lagna_key]
    # Also build a lookup from raw Hindi rules (English structure)
    bp_matched = [r for r in bp_rules
                   if r.get("lagna_en_common", "").lower() == lagna_en.lower()]

    # Tamil interpretation generator from structured fields (when only Hindi text exists)
    PLANET_KARAKAS_HI = {
        "Sun": "अधिकार, प्रसिद्धि, पिता, आत्म-सम्मान, नेतृत्व",
        "Moon": "मन, भावनाएं, माता, मानसिक शांति, लोकप्रियता",
        "Mars": "साहस, ऊर्जा, भाई-बहन, प्रतिस्पर्धा, संपत्ति",
        "Mercury": "बुद्धि, वाणी, व्यापार, शिक्षा, गणितीय कौशल",
        "Jupiter": "ज्ञान, भाग्य, गुरु, धन, संतान, धर्म",
        "Venus": "प्रेम, कला, सौंदर्य, साझेदारी, सुख, विलासिता",
        "Saturn": "अनुशासन, कठिन परिश्रम, आयु, देरी, जिम्मेदारी",
        "Rahu": "महत्वाकांक्षा, विदेश, प्रौद्योगिकी, अचानक प्रगति",
        "Ketu": "अध्यात्म, मोक्ष, अनुसंधान, पुराना कर्म",
    }
    HOUSE_NAMES_HI_FULL = {h: HOUSES_HI[h][0] + " — " + HOUSES_HI[h][1] for h in range(1, 13)}

    def _hi_interp(planet, house, dignity=None):
        """Generate a brief Tamil interpretation from structured info."""
        kar = PLANET_KARAKAS_HI.get(planet, "")
        h_name = HOUSES_HI.get(house, ("?", "?"))[0]
        h_mean = HOUSES_HI.get(house, ("?", "?"))[1]
        return (f"{_hi_planet(planet)} இந்த {h_name} வீட்டில் இருப்பதால், "
                f"இவ்வீட்டின் ({h_mean}) விஷயங்களில் "
                f"{kar.split(',')[0]} சம்பந்தமான பலன்கள் கிடைக்கும்.")

    pos = chart["positions"]
    PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    shown = 0
    for planet in PLANET_ORDER:
        if planet not in pos: continue
        pd = pos[planet]
        h = pd.get("house", 0)
        # Prefer synthesized cell (English) for richer text
        cell = next((c for c in matched
                      if c.get("house") == h and c.get("planet") == planet), None)
        bp_rule = next((r for r in bp_matched
                         if r.get("house") == h and r.get("planet") == planet), None)
        if cell or bp_rule:
            planet_ta = _hi_planet(planet)
            rasi_ta = _hi_rasi(pd.get("rasi", ""))
            dignity = (cell or {}).get("dignity", "") if cell else ""
            classes = (cell or {}).get("classes", []) if cell else []
            flow.append(Spacer(1, 0.15*cm))
            flow.append(TP(
                f"▸ {planet_ta} — {rasi_ta} राशि में (भाव {h})",
                "cell_bold", color=INDIGO))
            DIGNITY_HI = {
                "exalted":"உச்சம் (exalted)","debilitated":"நீசம் (debilitated)",
                "own":"சுவக்ஷேத்திரம் (own sign)","mooltrikona":"மூலத்திரிகோணம்",
                "friend":"நட்பு (friend)","enemy":"எதிரி (enemy)","neutral":"சம (neutral)",
            }
            CLASS_HI = {"kendra":"கேந்திரம்","trikona":"த்ரிகோணம்","upachaya":"உபசயம்",
                         "dusthana":"துஸ்தானம்","maraka":"மாரகம்","panaphara":"பணபரம்","apoklima":"அபோக்லிமம்"}
            if dignity or classes:
                dignity_hi = DIGNITY_HI.get(dignity.lower(), dignity)
                class_hi = " + ".join(CLASS_HI.get(c, c) for c in classes) if classes else ""
                flow.append(TP(
                    f"स्थिति: {dignity_hi}  |  भाव प्रकार: {class_hi}",
                    "small", color=ACCENT))
            # English content from synthesized cell (preferred)
            if cell and cell.get("text"):
                text = cell.get("text", "")
                if len(text) > 300: text = text[:300] + "..."
                flow.append(TP(text, "cell"))
                outcome = cell.get("outcome", "")
                if outcome and outcome != text:
                    flow.append(TP(f"मुख्य प्रभाव: {outcome}", "small", color=GREEN))
            else:
                # Fallback: auto-generated Tamil interpretation from structured data
                flow.append(TP(_hi_interp(planet, h), "cell"))
                if bp_rule:
                    flow.append(TP(
                        "(विस्तृत विवरण भृगु संहिता मूल संस्कृत ग्रंथ में उपलब्ध है)",
                        "small", color=GREY_MD))
            shown += 1
    if not shown:
        flow.append(TP(
            f"({lagna_en} लग्न के लिए भृगु संहिता नियम नहीं मिले — "
            "आपकी कुछ ग्रह स्थितियां सामान्य से भिन्न हैं)",
            "small"))
    return flow


# ════════════════════════════════════════════════════════════════════════════
#  Rasi (D1) + Navamsa (D9) South-Indian box charts (TAMIL)
# ════════════════════════════════════════════════════════════════════════════

# South-Indian 4x4 grid layout — each sign occupies a fixed cell
SI_LAYOUT_TA = {
    "Pisces":    (0, 0), "Aries":     (0, 1), "Taurus":    (0, 2), "Gemini":    (0, 3),
    "Aquarius":  (1, 0),                                            "Cancer":    (1, 3),
    "Capricorn": (2, 0),                                            "Leo":       (2, 3),
    "Sagittarius":(3, 0),"Scorpio":   (3, 1), "Libra":     (3, 2), "Virgo":     (3, 3),
}


def _make_cell(sign_ta, planets_ta, is_lagna, cell_size=1.9):
    """Build one inner cell for the chart — 2-row nested table: sign label + planets."""
    sign_text = sign_ta + (" ★" if is_lagna else "")
    sign_color = ACCENT if is_lagna else GREY_MD
    sign_p = TamilParagraph(sign_text, font_size=7,
                              color=sign_color, leading=1.1,
                              bold=is_lagna)
    planet_p = TamilParagraph(planets_ta if planets_ta else "",
                                font_size=9, color=INDIGO,
                                leading=1.2, bold=True, align="center")
    inner = Table([[sign_p], [planet_p]],
                   colWidths=[(cell_size - 0.1)*cm],
                   rowHeights=[0.45*cm, (cell_size - 0.55)*cm])
    inner_style = [
        ("VALIGN", (0,0), (0,0), "TOP"),
        ("VALIGN", (0,1), (0,1), "MIDDLE"),
        ("ALIGN", (0,1), (0,1), "CENTER"),
        ("TOPPADDING", (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
        ("LEFTPADDING", (0,0), (-1,-1), 3),
        ("RIGHTPADDING", (0,0), (-1,-1), 3),
    ]
    if is_lagna:
        inner_style.append(("BACKGROUND", (0,0), (-1,-1), HexColor("#fef9e8")))
    inner.setStyle(TableStyle(inner_style))
    return inner


def _build_si_chart_ta(positions_by_rasi, lagna_rasi, title_ta, cell_size=2.0):
    """South-Indian 4x4 chart with planets in cells. Lagna highlighted."""
    grid = [[None]*4 for _ in range(4)]
    for rasi, (r, c) in SI_LAYOUT_TA.items():
        planets = positions_by_rasi.get(rasi, [])
        planets_ta = " ".join(PLANETS_HI_SHORT.get(p, p[:2]) for p in planets) if planets else ""
        rasi_short = RASIS_HI.get(rasi, rasi)[:5]
        is_lagna = (rasi == lagna_rasi)
        grid[r][c] = _make_cell(rasi_short, planets_ta, is_lagna, cell_size)

    # Center 2x2: title
    title_p = TamilParagraph(title_ta, font_size=10,
                              color=INDIGO, leading=1.3,
                              bold=True, align="center")
    grid[1][1] = title_p
    grid[1][2] = TamilParagraph("", font_size=8)
    grid[2][1] = TamilParagraph("", font_size=8)
    grid[2][2] = TamilParagraph("", font_size=8)

    t = Table(grid, colWidths=[cell_size*cm]*4, rowHeights=[cell_size*cm]*4)
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.6, INDIGO),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("SPAN", (1,1), (2,2)),
        ("BACKGROUND", (1,1), (2,2), CREAM),
    ]))
    return t


def page_rasi_navamsa_ta(chart):
    """Page with Rasi (D1) + Navamsa (D9) South-Indian box charts side by side."""
    flow = []
    flow.append(TP(_hi_section("RASI_NAVAMSA"), "h1"))
    flow.append(divider())
    flow.append(TP(
        "राशि चक्र (D1) आपकी मुख्य जन्म कुंडली है — यह आपके जीवन को दर्शाता है। "
        "நவாம்சம் (D9) என்பது திருமணம், தர்மம் மற்றும் உள் வலிமைக்கான பிரிவு சக்கரம். "
        "दक्षिण भारतीय बॉक्स लेआउट। ★ = लग्न।",
        "small"))
    flow.append(TP(
        "ग्रह संक्षेप: सू=सूर्य, च=चन्द्र, मं=मंगल, "
        "बु=बुध, गु=गुरु, शु=शुक्र, श=शनि, रा=राहु, के=केतु",
        "small", color=ACCENT))
    flow.append(Spacer(1, 0.3*cm))

    pos = chart["positions"]
    d1_by_rasi = {}
    for p, pd in pos.items():
        rasi = pd.get("rasi", "")
        d1_by_rasi.setdefault(rasi, []).append(p)
    lagna_rasi = chart.get("lagna", "")
    d1_chart = _build_si_chart_ta(d1_by_rasi, lagna_rasi,
                                    f"राशि चक्र (D1)  लग्न: {_hi_rasi(lagna_rasi)}",
                                    cell_size=2.0)

    # D9 Navamsa
    try:
        from divisional_charts import build_divisional_chart
        d9 = build_divisional_chart(chart, varga="D9")
        d9_by_rasi = {}
        for p, pd in d9["positions"].items():
            rasi = pd.get("rasi", "")
            d9_by_rasi.setdefault(rasi, []).append(p)
        SIGNS_EN = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                     "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        d9_lagna = SIGNS_EN[d9["lagna_idx"]]
        d9_chart = _build_si_chart_ta(d9_by_rasi, d9_lagna,
                                        f"नवमांश (D9)  लग्न: {_hi_rasi(d9_lagna)}",
                                        cell_size=2.0)
    except Exception:
        d9_chart = TP("(नवमांश गणना विफल)", "small")

    # Side-by-side
    side_by_side = Table([[d1_chart, d9_chart]], colWidths=[8.5*cm, 8.5*cm])
    side_by_side.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    flow.append(side_by_side)

    # 12 houses reference card
    flow.append(Spacer(1, 0.5*cm))
    flow.append(TP("12 भाव (घर) — अर्थ", "h2"))
    h_rows = []
    for r1, r2 in [(1, 7), (2, 8), (3, 9), (4, 10), (5, 11), (6, 12)]:
        name1, mean1 = HOUSES_HI[r1]
        name2, mean2 = HOUSES_HI[r2]
        h_rows.append([
            TP(f"{r1}. {name1} — {mean1}", "cell_bold"),
            TP(f"{r2}. {name2} — {mean2}", "cell_bold"),
        ])
    t = Table(h_rows, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
    ]))
    flow.append(t)
    return flow


def page_life_timeline(chart, all_mds, today, ranked_events, all_ads_by_md):
    """First flowable returned is the section intro; subsequent chapters start on new pages."""
    flow = []
    # Intro is added INLINE — no page break — it flows after Yogas on whatever page is open.
    # Then each chapter starts on its own page.
    flow.append(Spacer(1, 0.4*cm))
    flow.append(TP(_hi_section("LIFE_TIMELINE"), "h1"))
    flow.append(TP(
        "आपका जीवन विम्शोत्तरी ग्रह घड़ी द्वारा 9 प्रमुख अध्यायों में विभाजित है। "
        "प्रत्येक अध्याय का एक अनूठा विषय, उप-काल और "
        "क्या करें / क्या न करें सलाह है। "
        "सबसे पहले अपना वर्तमान अध्याय पढ़ें।",
        "body"))
    # First chapter starts on next page

    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))

    for idx, md_rec in enumerate(all_mds[:9], 1):
        lord = md_rec.lord
        lord_ta = _hi_planet(lord)
        s = md_rec.start; e = md_rec.end
        age_s = max(0, (s - birth_dt).days // 365)
        age_e = (e - birth_dt).days // 365
        is_current = s <= today <= e
        is_past = e < today

        marker = "▶ वर्तमान" if is_current else ("✓ अतीत" if is_past else "→ भविष्य")

        # Each chapter on its own page
        flow.append(PageBreak())
        flow.append(TP(f"அத்தியாயம் {idx}: {lord_ta} தசை", "chapter"))
        flow.append(TP(
            f"{fmt_my_hi(s)} → {fmt_my_hi(e)}    आयु {age_s} से {age_e}    "
            f"{(e-s).days // 365} वर्ष    {marker}",
            "small"))
        flow.append(Spacer(1, 0.2*cm))

        flow.append(TP(f"मूल विषय: {MD_THEME_HI.get(lord, '')}", "body"))
        flow.append(Spacer(1, 0.2*cm))

        # What to expect
        flow.append(TP("इस अध्याय में क्या उम्मीद करें", "h3"))
        for line in MD_EXPECT_HI.get(lord, [])[:5]:
            flow.append(TP(f"•  {line}", "bullet"))

        # Watch for
        flow.append(TP("सावधानी बरतने योग्य बातें:", "h3"))
        for line in MD_WATCH_TA.get(lord, [])[:3]:
            flow.append(TP(f"•  {line}", "bullet"))

        # Predicted events
        period_events = [
            ev for ev in ranked_events
            if ev.get("window_start") and ev.get("window_end")
               and ev["window_start"] >= s and ev["window_start"] < e
        ]
        period_events.sort(key=lambda x: x["window_start"])
        if period_events:
            flow.append(Spacer(1, 0.2*cm))
            flow.append(TP("इस अध्याय में पूर्व-संकेतित घटनाक्रम", "h3"))
            for ev in period_events[:6]:
                ws = fmt_my_hi(ev["window_start"])
                we = fmt_my_hi(ev["window_end"]) if ev["window_end"] else ws
                age_ev = int((ev["window_start"] - birth_dt).days / 365.25)
                cat = ev.get("category", "")
                text = EVENT_PLAIN_HI.get(cat, ev.get("event", ""))
                stars = ev.get("stars", "")
                label = f"{ws}" if ws == we else f"{ws} - {we}"
                flow.append(TP(f"•  आयु {age_ev} ({label}) — {text} {stars}", "bullet"))

        # Sub-chapters
        ad_list = all_ads_by_md.get(lord, [])
        ads_for_this_md = [a for a in ad_list if s <= a.start < e]
        if ads_for_this_md:
            flow.append(Spacer(1, 0.2*cm))
            flow.append(TP("उप अध्याय (अंतर्दशा)", "h3"))
            rows = [[
                TP(_hi_label("Sub-period"), "cell_bold", color=CREAM),
                TP(_hi_label("Start date"), "cell_bold", color=CREAM),
                TP(_hi_label("End date"), "cell_bold", color=CREAM),
                TP(_hi_label("Age"), "cell_bold", color=CREAM),
            ]]
            for ad in ads_for_this_md:
                ad_age = int((ad.start - birth_dt).days / 365.25)
                ad_now = ad.start <= today <= ad.end
                prefix = "▶ " if ad_now else ""
                ad_lord_ta = _hi_planet(ad.ad)
                rows.append([
                    TP(f"{prefix}{lord_ta}-{ad_lord_ta}", "bullet", bold=True),
                    TP(fmt_my_hi(ad.start), "bullet"),
                    TP(fmt_my_hi(ad.end), "bullet"),
                    TP(str(ad_age), "bullet"),
                ])
            ad_t = Table(rows, colWidths=[5.5*cm, 4.0*cm, 4.0*cm, 2.0*cm])
            ad_t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), INDIGO),
                ("TEXTCOLOR", (0,0), (-1,0), CREAM),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
                ("LEFTPADDING", (0,0), (-1,-1), 6),
                ("LINEBELOW", (0,0), (-1,0), 0.8, GOLD),
            ]))
            flow.append(ad_t)

        # DO + AVOID
        flow.append(Spacer(1, 0.2*cm))
        do_rows = [[
            TP(f"{lord_ta} தசையில் செய்ய வேண்டியவை", "bullet", bold=True, color=GREEN),
            TP(f"{lord_ta} தசையில் தவிர்க்க வேண்டியவை", "bullet", bold=True, color=RED),
        ]]
        do = MD_DO_TA.get(lord, [])[:3]; avoid = MD_AVOID_TA.get(lord, [])[:3]
        for i in range(max(len(do), len(avoid))):
            do_rows.append([
                TP(f"•  {do[i]}" if i < len(do) else "", "bullet"),
                TP(f"•  {avoid[i]}" if i < len(avoid) else "", "bullet"),
            ])
        dt2 = Table(do_rows, colWidths=[8*cm, 8*cm])
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

        # PageBreak now happens at the START of each chapter (above), so no need here

    return flow


# ════════════════════════════════════════════════════════════════════════════
#  Footer
# ════════════════════════════════════════════════════════════════════════════

def page_footer(canvas, doc):
    canvas.saveState()
    # Use Tamil rendering for "பக்கம்" + page number
    draw_tamil(canvas, f"पृष्ठ {doc.page}", A4[0]/2 - 30, 0.8*cm,
                font_name="Devanagari", font_size=9, color=GREY_MD)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY_MD)
    canvas.drawRightString(A4[0] - 1.5*cm, 0.8*cm, "Atro Vedic Engine")
    canvas.restoreState()


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════


def page1_layout(c, doc):
    c.saveState()
    # Sheet background cream
    c.setFillColor(HexColor("#fdfaf2")); c.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Draw background watermark
    import os
    bg_pattern_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mystical_tiled_background.png")
    if os.path.exists(bg_pattern_path):
        c.saveState()
        c.setFillAlpha(0.07)  # Visible yet subtle background watermark
        w_x = 2.0 * cm
        w_y = 2.0 * cm
        w_w = A4[0] - 4.0 * cm
        w_h = A4[1] - 4.0 * cm
        c.drawImage(bg_pattern_path, w_x, w_y, width=w_w, height=w_h, mask='auto')
        c.restoreState()

    c.setStrokeColor(GOLD); c.setLineWidth(2)
    c.rect(20, 20, A4[0]-40, A4[1]-40, fill=0, stroke=1)
    c.setStrokeColor(HexColor("#e5cd6c")); c.setLineWidth(0.5)
    c.rect(28, 28, A4[0]-56, A4[1]-56, fill=0, stroke=1)
    c.setFillColor(HexColor("#8a6a18")); c.setFont("Helvetica-Oblique", 7)
    c.drawCentredString(A4[0]/2, 28,
        "Generated by Atro Vedic Engine · 34 classical books · 8,239 rules · 3-engine ephemeris parity")
    c.restoreState()


def content_page(c, doc):
    c.saveState()
    c.setFillColor(HexColor("#fdfaf2")); c.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    
    # Draw background watermark
    import os
    bg_pattern_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mystical_tiled_background.png")
    if os.path.exists(bg_pattern_path):
        c.saveState()
        c.setFillAlpha(0.07)  # Visible yet subtle background watermark
        w_x = 0.95 * cm
        w_y = 0.95 * cm
        w_w = A4[0] - 1.9 * cm
        w_h = A4[1] - 1.9 * cm
        c.drawImage(bg_pattern_path, w_x, w_y, width=w_w, height=w_h, mask='auto')
        c.restoreState()

    # Draw borders on content pages
    c.setStrokeColor(GOLD); c.setLineWidth(1.0)
    c.rect(0.8 * cm, 0.8 * cm, A4[0] - 1.6 * cm, A4[1] - 1.6 * cm, fill=False, stroke=True)
    c.setStrokeColor(INDIGO); c.setLineWidth(0.5)
    c.rect(0.95 * cm, 0.95 * cm, A4[0] - 1.9 * cm, A4[1] - 1.9 * cm, fill=False, stroke=True)

    # Footnote/Header info
    draw_tamil(c, f"पृष्ठ {doc.page}", A4[0]/2 - 30, 0.8*cm,
                font_name="Devanagari", font_size=9, color=GREY_MD)
    c.setFont("Helvetica", 8)
    c.setFillColor(GREY_MD)
    c.drawRightString(A4[0] - 1.5*cm, 0.8*cm, "Atro Vedic Engine")
    c.restoreState()


def build_truth_report_section_hi(chart):
    flow = []
    tr = chart.get("truth_report")
    if not tr:
        return flow
    
    flow.append(PageBreak())
    flow.append(TP("सत्य और साक्ष्य रिपोर्ट", "h1"))
    flow.append(TP("साक्ष्य-आधारित संश्लेषण और प्रमाण ऑडिट (Evidence Trail)", "subtitle"))
    flow.append(divider())
    
    # Metadata summary table
    state = tr.get("report_state", "unknown").upper()
    state_hi = "पूर्ण" if state == "COMPLETE" else "आंशिक"
    g_sum = tr.get("graph_summary", {})
    nodes = g_sum.get("nodes", 0)
    edges = g_sum.get("edges", 0)
    claims_count = g_sum.get("claims", 0)
    
    meta_rows = [
        [TP("रिपोर्ट की स्थिति:", "cell_bold"), TP(state_hi, "cell"),
         TP("ग्राफ का आकार:", "cell_bold"), TP(f"{nodes} नोड्स, {edges} किनारे", "cell")],
        [TP("सत्यापन स्तर:", "cell_bold"), TP("ग्रंथ क्रॉस-रेफरेंस (ट्रेस करने योग्य)", "cell"),
         TP("सक्रिय दावे:", "cell_bold"), TP(str(claims_count), "cell")]
    ]
    t_meta = Table(meta_rows, colWidths=[3.5*cm, 4.5*cm, 3.5*cm, 4.5*cm])
    t_meta.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, GREY_LT),
        ("BACKGROUND", (0,0), (-1,-1), SHEET_BG if 'SHEET_BG' in globals() else HexColor("#fdfaf2")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    flow.append(t_meta)
    flow.append(Spacer(1, 0.4*cm))
    
    # 1. Chart Facts
    flow.append(TP("गणना किए गए कुंडली तथ्य (सत्यापन योग्य):", "h2"))
    facts = tr.get("chart_facts", [])
    if facts:
        for f in facts:
            lbl = f.get("label", "")
            lbl_hi = lbl.replace("Lagna is", "लग्न:").replace("Moon sign is", "राशि:").replace("Birth nakshatra is", "नक्षत्र:")
            flow.append(TP(f"•  {lbl_hi}", "body"))
    else:
        flow.append(TP("ग्राफ में कोई तथ्य दर्ज नहीं किया गया है।", "body"))
    flow.append(Spacer(1, 0.4*cm))
    
    # 2. Active Claims
    flow.append(TP("संश्लेषित दावे और साक्ष्य निशान (Evidence Trail):", "h2"))
    claims = tr.get("claims", [])
    if claims:
        for c in claims:
            topic = c.get("topic", "").replace("_", " ").upper()
            topic_hi = "वर्तमान महादशा काल" if topic == "CURRENT PERIOD" else topic
            status = c.get("status", "").upper()
            status_hi = "समर्थित (Supported)" if status == "SUPPORTED" else ("अस्थायी" if status == "TENTATIVE" else ("मिश्रित" if status == "MIXED" else "अपुष्ट"))
            band = c.get("confidence_band", "").upper()
            band_hi = "पुष्टि की गई (Corroborated)" if band == "CORROBORATED" else ("एकल विधि" if band == "SINGLE_METHOD" else ("चुनौतीपूर्ण" if band == "CONTESTED" else "अपुष्ट"))
            statement = c.get("statement", "")
            
            if "corroborate" in statement:
                statement_hi = "विभिन्न ज्योतिषीय प्रणालियाँ इस समय अवधि के फल की पुष्टि करती हैं।"
            elif "mixed" in statement or "disagree" in statement:
                statement_hi = "अलग-अलग ज्योतिषीय प्रणालियाँ इस समय अवधि के फल में भिन्नता दिखाती हैं।"
            else:
                statement_hi = statement
                
            color = "#0a7a3a" if status == "SUPPORTED" else ("#d97706" if status in ("TENTATIVE", "MIXED") else "#c0392b")
            
            flow.append(TP(f"विषय: {topic_hi}   [{status_hi} / {band_hi}]", "h3", color=HexColor(color)))
            flow.append(TP(statement_hi, "body"))
            
            why = c.get("why", {})
            supports = why.get("supports", [])
            contradictions = why.get("contradictions", [])
            citations = why.get("citations", [])
            
            if supports:
                flow.append(TP("  साक्ष्य (Supports):", "cell_bold"))
                for s in supports:
                    clean_s = s.replace("fact:", "तथ्य: ").replace("method_finding:", "निष्कर्ष: ").replace("method:", "पद्धति: ")
                    flow.append(TP(f"    •  {clean_s}", "bullet"))
            
            if contradictions:
                flow.append(TP("  विरोधाभास (Contradictions):", "cell_bold", color=HexColor("#c0392b")))
                for ct in contradictions:
                    clean_ct = ct.replace("fact:", "तथ्य: ").replace("method_finding:", "निष्कर्ष: ").replace("method:", "पद्धति: ")
                    flow.append(TP(f"    •  {clean_ct}", "bullet", color=HexColor("#c0392b")))
            
            if citations:
                flow.append(TP("  ग्रंथ उद्धरण (Citations):", "cell_bold", color=HexColor("#7e3a96")))
                for cit in citations:
                    clean_cit = cit.replace("citation:", "").replace("excerpt", "उद्धरण")
                    flow.append(TP(f"    •  {clean_cit}", "bullet", color=HexColor("#7e3a96")))
            flow.append(Spacer(1, 0.3*cm))
    else:
        flow.append(TP("इस कुंडली के लिए कोई सक्रिय दावे नहीं बनाए गए हैं।", "body"))
    flow.append(Spacer(1, 0.4*cm))
    
    # 3. Method Coverage
    flow.append(TP("ज्योतिषीय पद्धतियों का कवरेज (Method Coverage):", "h2"))
    cov = tr.get("method_coverage", {})
    if cov:
        cov_rows = [[TP("ज्योतिषीय पद्धति", "cell_bold", color=white), TP("स्थिति", "cell_bold", color=white), TP("सुरक्षा कोड", "cell_bold", color=white)]]
        for method, info in sorted(cov.items()):
            state = info.get("state", "").upper()
            state_hi = "उपलब्ध" if state == "AVAILABLE" else "अनुपलब्ध"
            code = info.get("safe_code", "ठीक")
            color = "#0a7a3a" if state == "AVAILABLE" else "#c0392b"
            cov_rows.append([
                TP(method.upper(), "cell_bold"),
                TP(state_hi, "cell_bold", color=HexColor(color)),
                TP(code, "cell")
            ])
        t_cov = Table(cov_rows, colWidths=[5.0*cm, 4.0*cm, 5.0*cm])
        t_cov.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), INDIGO),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("GRID", (0,0), (-1,-1), 0.5, GREY_LT),
        ]))
        flow.append(t_cov)

    return flow


_BHAVA_HI = ["लग्न", "धन", "सहज", "मातृ", "पुत्र", "शत्रु",
             "कलत्र", "आयु", "भाग्य", "कर्म", "लाभ", "व्यय"]


def build_traditional_extras_section_hi(chart):
    """पारंपरिक थिरुकणितम विवरण — सूर्योदय/सूर्यास्त, नक्षत्र संदर्भ,
    चंद्राष्टम, श्रीपति भाव संधि।"""
    _HDR = HexColor("#1a1d3a"); _CREAM = HexColor("#faf6e8")
    flow = []
    te = chart.get("traditional_extras") or {}
    ident = chart.get("identity") or {}
    if not te and not ident:
        return flow

    flow.append(PageBreak())
    flow.append(TP("पारंपरिक थिरुकणितम विवरण", "h1"))
    flow.append(TP("पंचांग · नक्षत्र संदर्भ · श्रीपति भाव संधि", "subtitle"))
    flow.append(divider())

    st = te.get("sun_times", {}) or {}
    rows = []
    if ident.get("father_name"):
        rows.append([TP("पिता", "cell_bold"), TP(str(ident["father_name"]), "cell")])
    if ident.get("mother_name"):
        rows.append([TP("माता", "cell_bold"), TP(str(ident["mother_name"]), "cell")])
    if ident.get("birth_place"):
        rows.append([TP("जन्म स्थान", "cell_bold"), TP(str(ident["birth_place"]), "cell")])
    if st.get("sunrise"):
        rows.append([TP("सूर्योदय", "cell_bold"), TP(str(st["sunrise"]), "cell")])
    if st.get("sunset"):
        rows.append([TP("सूर्यास्त", "cell_bold"), TP(str(st["sunset"]), "cell")])
    if rows:
        t = Table(rows, colWidths=[3.5*cm, 10.0*cm])
        t.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.5, GREY_LT),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4), ("LEFTPADDING", (0,0), (-1,-1), 6)]))
        flow.append(t)
        flow.append(Spacer(1, 0.4*cm))

    nr = te.get("nakshatra_reference") or {}
    if nr.get("known"):
        flow.append(TP("जन्म नक्षत्र संदर्भ:", "h2"))
        parts = [f"गण: {nr.get('gana','')}", f"योनि: {nr.get('yoni','')} ({nr.get('yoni_gender','')})",
                 f"नाडी: {nr.get('nadi','')}", f"वृक्ष: {nr.get('tree','')}"]
        if nr.get("bird"):
            parts.append(f"पक्षी: {nr['bird']}")
        flow.append(TP("  ·  ".join(parts), "body"))
        flow.append(Spacer(1, 0.3*cm))

    ch = te.get("chandrashtama_nakshatras") or []
    if ch:
        flow.append(TP("चंद्राष्टम नक्षत्र: " + ", ".join(ch), "body"))
        flow.append(Spacer(1, 0.4*cm))

    cusps = te.get("bhava_cusps") or []
    if cusps:
        flow.append(TP("श्रीपति भाव संधि (असमान भाव):", "h2"))
        trows = [[TP("भा", "cell_bold"), TP("भाव", "cell_bold"), TP("आरंभ", "cell_bold"),
                  TP("मध्य", "cell_bold"), TP("अंत", "cell_bold")]]
        for c in cusps:
            h = c.get("house", 0)
            trows.append([TP(str(h), "cell"), TP(_BHAVA_HI[h-1] if 1 <= h <= 12 else "", "cell"),
                          TP(c.get("start_dms",""), "cell"), TP(c.get("mid_dms",""), "cell"),
                          TP(c.get("end_dms",""), "cell")])
        t = Table(trows, colWidths=[0.9*cm, 3.4*cm, 3.1*cm, 3.1*cm, 3.1*cm])
        t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), _HDR), ("TEXTCOLOR", (0,0), (-1,0), _CREAM),
            ("GRID", (0,0), (-1,-1), 0.5, GREY_LT), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6)]))
        flow.append(t)
    return flow


def generate(chart_path, out_path):
    with open(chart_path, encoding="utf-8") as f:
        chart = json.load(f)
    today = dt.datetime.now()

    print(f"Building HINDI DEEP PDF (HarfBuzz-shaped) for {chart.get('name', '?')}...")
    try:
        e_chart = to_engine_chart(chart)
        reports = run_engines(e_chart)
    except Exception as exc:
        print(f"  WARN: engine_bridge failed: {exc}")
        reports = []

    b = chart["birth"]
    raw = scan_lifetime_v2(chart, b["year"], b["year"] + 80, min_severity=3)
    bands = collapse_consecutive(raw) if raw else []
    ranked_events = rank_and_consume(bands) if bands else []

    all_mds = e_chart.vimshottari_periods or []
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

    ds = lookup(tl, today)
    dasha_now = {
        "md": ds.get(1, {}).get("md", "?"),
        "md_end": ds.get(1, {}).get("end"),
        "ad": ds.get(2, {}).get("ad", "?"),
        "ad_end": ds.get(2, {}).get("end"),
    }

    flow = []
    flow.extend(page_cover(chart, today, None, dasha_now))
    flow.append(PageBreak())
    flow.extend(page_birth_panchanga(chart, None))
    flow.append(PageBreak())
    flow.extend(page_planets(chart, None))
    flow.append(PageBreak())
    flow.extend(page_yogas(chart, None))
    flow.append(PageBreak())
    # ── RASI (D1) + NAVAMSA (D9) box charts ──
    flow.extend(page_rasi_navamsa_ta(chart))
    flow.append(PageBreak())
    # ── LIFE DOMAIN PREDICTIONS with book citations (NEW) ──
    flow.extend(page_life_domains_ta(chart, e_chart))
    flow.append(PageBreak())
    # ── BHRIGU PATRIKA per-planet predictions (NEW) ──
    flow.extend(page_bhrigu_patrika_ta(chart, e_chart))
    # No PageBreak — let timeline section flow naturally
    flow.extend(page_life_timeline(chart, all_mds, today, ranked_events, all_ads_by_md))

    doc = SimpleDocTemplate(
        str(out_path), pagesize=A4,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=1.8*cm, bottomMargin=2.0*cm,
        title=f"{chart.get('name', '?')} — Hindi Life Reading",
    )
    # Append Truth Report section
    try:
        flow.extend(build_traditional_extras_section_hi(chart))
    except Exception as exc:
        print(f"  WARN: build_traditional_extras_hi failed: {exc}")
    try:
        truth_flow = build_truth_report_section_hi(chart)
        flow.extend(truth_flow)
    except Exception as exc:
        print(f"  WARN: build_truth_report_hi failed: {exc}")

    doc.build(flow, onFirstPage=page1_layout, onLaterPages=content_page)
    import os as _os
    size_kb = _os.path.getsize(str(out_path)) // 1024
    print(f"DONE: {out_path}  ({size_kb} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True)
    ap.add_argument("--out", help="output PDF path")
    args = ap.parse_args()

    cp = Path(args.chart)
    if args.out:
        out = Path(args.out)
    else:
        name = cp.stem.replace("_chart", "").upper()
        out = cp.parent.parent / "reports" / f"{name}_HINDI.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    generate(cp, out)


if __name__ == "__main__":
    main()
