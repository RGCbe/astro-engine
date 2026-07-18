"""
Traditional Jadhagam (Tamil-style) chart-detail pages for the DEEP PDF.

Adds the technical chart sections that classical jadhagam printouts contain:
  1. Birth Panchanga (Tithi/Paksha/Yoga/Karana/Nakshatra/Sunrise/Sunset/Day)
  2. Planetary Positions Table (full detail per planet)
  3. Rasi (D1) + Navamsa (D9) South-Indian box charts
  4. Yogas detected (classical names + interpretation)
  5. Ashtakavarga Grid (7-planet bindu table + Sarvashtakavarga totals)
  6. Full Vimshottari Dasha-Bhukti-Antara table (4 levels, full lifetime)

All sections kept TECHNICAL but with plain-English short notes alongside the
Sanskrit names, so a normal user can still read it.
"""
import datetime as dt
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle,
                                 PageBreak, HRFlowable)

INDIGO = HexColor("#312e81")
GOLD   = HexColor("#b88a37")
CREAM  = HexColor("#fef6e4")
GREY_LT = HexColor("#f3f0e8")
GREY_MD = HexColor("#6b6b6b")
GREEN  = HexColor("#16a34a")
RED    = HexColor("#c0392b")
AMBER  = HexColor("#d97706")


# ════════════════════════════════════════════════════════════════════════════
#  Page 1: Birth Details + Panchanga
# ════════════════════════════════════════════════════════════════════════════

def page_birth_details(chart, st):
    """Traditional jadhagam first page — birth details + panchanga at moment of birth."""
    flow = []
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))

    flow.append(Paragraph("BIRTH DETAILS &amp; PANCHANGA", st["h1"]))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8))

    # Birth essentials
    flow.append(Paragraph("<b>Birth essentials</b>", st["h2"]))
    rows = [
        ["Name", chart.get("name", "—")],
        ["Date of birth", f"{b['day']:02d} {dt.date(2000, b['month'], 1).strftime('%B')} {b['year']} ({b.get('weekday','?')})"],
        ["Time of birth", f"{b.get('hour',0):02d}:{b.get('min',0):02d} IST"],
        ["Place", b.get("place", "—")],
        ["Latitude / Longitude", f"{b.get('lat','?')}° N,  {b.get('lon','?')}° E"],
        ["Time Zone", f"+{b.get('tz', 5.5)} hours from GMT"],
        ["Ayanamsa (Lahiri)", f"{chart.get('ayanamsa', '?')}°"],
        ["Rodden rating", chart.get("rodden_rating", "—")],
    ]
    t = Table(rows, colWidths=[5*cm, 11*cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("LINEBELOW", (0,0), (-1,0), 0.5, GOLD),
    ]))
    flow.append(t)

    # Lagna / Rasi / Nakshatra essentials
    flow.append(Spacer(1, 0.4*cm))
    flow.append(Paragraph("<b>Vedic chart essentials</b>", st["h2"]))
    moon_pada = chart.get("moon_pada") or chart.get("positions", {}).get("Moon", {}).get("pada", "?")
    rows = [
        ["Lagna (Rising sign)", f"{chart.get('lagna','?')}  ({chart.get('lagna_deg', 0):.2f}°)"],
        ["Lagna lord (ruler)", f"{chart.get('lagna_lord','?')}"],
        ["Moon Rasi (Birth sign)", f"{chart.get('moon_rasi','?')}"],
        ["Janma Nakshatra", f"{chart.get('janma_nakshatra','?')}  pada {moon_pada}"],
        ["Nakshatra lord", f"{chart.get('janma_nakshatra_lord','?')}  (this is your starting Vimshottari Mahadasha)"],
    ]
    t = Table(rows, colWidths=[5*cm, 11*cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("LINEBELOW", (0,0), (-1,0), 0.5, GOLD),
    ]))
    flow.append(t)

    # Panchanga + sunrise/sunset
    flow.append(Spacer(1, 0.4*cm))
    flow.append(Paragraph("<b>Panchanga at the moment of birth</b>", st["h2"]))
    flow.append(Paragraph(
        "<i>The 5-fold time reading: lunar day, weekday, nakshatra, yoga, karana — used in classical "
        "muhurta and almanac (panchanga) analysis. Plus sunrise/sunset and other almanac details.</i>",
        st["small"]))

    panch_rows = []
    # Sunrise / Sunset / Day length using swisseph
    try:
        import swisseph as swe
        lat = float(b.get("lat", 0))
        lon = float(b.get("lon", 0))
        tz = float(b.get("tz", 5.5))
        # Use noon UT of birth date for sunrise/sunset computation
        utc_noon = dt.datetime(b["year"], b["month"], b["day"], 12 - int(tz), 0)
        jd0 = swe.julday(utc_noon.year, utc_noon.month, utc_noon.day, 0)
        # Find sunrise
        try:
            sr = swe.rise_trans(jd0 - 0.5, swe.SUN, lon, lat, 0, 0, 0, swe.CALC_RISE)
            ss = swe.rise_trans(jd0 - 0.5, swe.SUN, lon, lat, 0, 0, 0, swe.CALC_SET)
            if sr[0] == 0 and ss[0] == 0:
                sr_jd = sr[1][0]; ss_jd = ss[1][0]
                # Convert JD back to local time
                sr_y, sr_m, sr_d, sr_h = swe.revjul(sr_jd + tz/24)
                ss_y, ss_m, ss_d, ss_h = swe.revjul(ss_jd + tz/24)
                sr_hh = int(sr_h); sr_mm = int((sr_h - sr_hh)*60); sr_ss_ = int(((sr_h - sr_hh)*60 - sr_mm)*60)
                ss_hh = int(ss_h); ss_mm = int((ss_h - ss_hh)*60); ss_ss_ = int(((ss_h - ss_hh)*60 - ss_mm)*60)
                day_hours = (ss_jd - sr_jd) * 24
                panch_rows.append(["Sunrise (local)", f"{sr_hh:02d}:{sr_mm:02d}:{sr_ss_:02d} AM"])
                panch_rows.append(["Sunset (local)", f"{ss_hh:02d}:{ss_mm:02d}:{ss_ss_:02d} PM"])
                panch_rows.append(["Day duration", f"{int(day_hours)} hours {int((day_hours - int(day_hours))*60)} minutes"])
        except Exception:
            pass
    except Exception:
        pass

    try:
        from panchanga import compute_panchanga
        p = compute_panchanga(birth_dt)
        panch_rows.extend([
            ["Tithi (Lunar day)", f"{p.get('tithi','?')}  ({p.get('paksha','?')} paksha)"],
            ["Vara (Weekday)", f"{p.get('vara','?')}  (ruled by {p.get('vara_lord','?')})"],
            ["Nakshatra (transit-time)", f"{p.get('nakshatra','?')}  pada {p.get('pada','?')}"],
            ["Yoga", f"{p.get('yoga','?')}"],
            ["Karana", f"{p.get('karana','?')}"],
        ])
    except Exception as exc:
        panch_rows.append(["Panchanga", f"(computation failed: {exc})"])

    t = Table(panch_rows, colWidths=[5*cm, 11*cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("LINEBELOW", (0,0), (-1,0), 0.5, GOLD),
    ]))
    flow.append(t)

    # JANMA NAKSHATRA — full classical details (deity, gana, yoni, nadi, etc.)
    flow.append(Spacer(1, 0.4*cm))
    flow.append(Paragraph("<b>Your Janma Nakshatra — full classical details</b>", st["h2"]))
    flow.append(Paragraph(
        "<i>The Moon's nakshatra at birth defines your deepest personality layer, deity worship, "
        "ritual gana, animal yoni (sexual/instinctive type), physiological nadi, body part, "
        "associated tree, bird, and element. Used in muhurta + compatibility matching.</i>",
        st["small"]))
    try:
        from tara_chakra import get_nakshatra_full
        nak_data = get_nakshatra_full(chart.get('janma_nakshatra', ''))
        nak_rows = []
        if nak_data:
            for k in ['name', 'number', 'lord', 'deity', 'gana', 'yoni', 'nadi',
                      'mukha', 'direction', 'symbol', 'body_part', 'color', 'element']:
                v = nak_data.get(k)
                if v: nak_rows.append([k.replace('_', ' ').title(), str(v)])
        if nak_rows:
            t = Table(nak_rows, colWidths=[4*cm, 12*cm])
            t.setStyle(TableStyle([
                ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 10),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
                ("TOPPADDING", (0,0), (-1,-1), 3),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                ("LEFTPADDING", (0,0), (-1,-1), 8),
            ]))
            flow.append(t)
    except Exception:
        pass

    return flow


# ════════════════════════════════════════════════════════════════════════════
#  Page 2: Planetary Positions Table + Yogas
# ════════════════════════════════════════════════════════════════════════════

def page_planet_positions(chart, st):
    flow = []
    flow.append(Paragraph("PLANETARY POSITIONS", st["h1"]))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8))

    pos = chart["positions"]
    PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    lagna_idx = chart.get("lagna_idx", 0)

    def _dms(deg):
        """Convert decimal degrees to D° M' S'' format."""
        d = int(deg); rest = (deg - d) * 60
        m = int(rest); s = int((rest - m) * 60)
        return f"{d:02d}° {m:02d}' {s:02d}\""

    rows = [["Planet", "Sign", "House", "Degree (D° M' S\")", "Nakshatra", "Pada", "R"]]
    for p in PLANET_ORDER:
        if p not in pos: continue
        pd = pos[p]
        retro = "R" if pd.get("retrograde") else ""
        rows.append([
            Paragraph(f"<b>{p}</b>", st["bullet"]),
            Paragraph(pd.get("rasi", "—"), st["bullet"]),
            Paragraph(f"H{pd.get('house', '?')}", st["bullet"]),
            Paragraph(f"<font size='9'>{_dms(pd.get('deg', 0))}</font>", st["bullet"]),
            Paragraph(pd.get("nak", "—"), st["bullet"]),
            Paragraph(str(pd.get("pada", "—")), st["bullet"]),
            Paragraph(f"<font color='#c0392b'>{retro}</font>", st["bullet"]),
        ])
    # Add Lagna row
    rows.append([
        Paragraph(f"<b>Lagna</b>", st["bullet"]),
        Paragraph(chart.get("lagna", "—"), st["bullet"]),
        Paragraph("H1", st["bullet"]),
        Paragraph(f"<font size='9'>{_dms(chart.get('lagna_deg', 0))}</font>", st["bullet"]),
        Paragraph("—", st["bullet"]), Paragraph("—", st["bullet"]), Paragraph("", st["bullet"]),
    ])
    # Add Upagrahas (Mandi, Gulika) if available
    try:
        from upagrahas import compute_upagrahas
        upg = compute_upagrahas(chart)
        for upg_name in ["Mandi", "Gulika"]:
            if upg_name in upg:
                u = upg[upg_name]
                rows.append([
                    Paragraph(f"<b><font color='#7e3a96'>{upg_name}</font></b>", st["bullet"]),
                    Paragraph(u.get("rasi", "—"), st["bullet"]),
                    Paragraph(f"H{u.get('house', '?')}", st["bullet"]),
                    Paragraph(f"<font size='9'>{_dms(u.get('deg', 0))}</font>", st["bullet"]),
                    Paragraph("—", st["bullet"]), Paragraph("—", st["bullet"]), Paragraph("", st["bullet"]),
                ])
    except Exception:
        pass

    t = Table(rows, colWidths=[2.2*cm, 2.5*cm, 1.4*cm, 2.3*cm, 4.0*cm, 1.0*cm, 0.8*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), INDIGO),
        ("TEXTCOLOR", (0,0), (-1,0), CREAM),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 10),
        ("FONTSIZE", (0,1), (-1,-1), 10),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("LINEBELOW", (0,0), (-1,0), 1.0, GOLD),
        ("ALIGN", (2,1), (3,-1), "CENTER"),
        ("ALIGN", (5,1), (6,-1), "CENTER"),
    ]))
    flow.append(t)

    # Yogas detected
    flow.append(Spacer(1, 0.4*cm))
    flow.append(Paragraph("YOGAS DETECTED", st["h1"]))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8))
    flow.append(Paragraph(
        "<i>Yogas are special planetary combinations that produce specific life-results. "
        "Detected from your chart using classical BPHS / Phaladeepika rules.</i>",
        st["small"]))
    flow.append(Spacer(1, 0.2*cm))

    try:
        from comprehensive_yogas import detect_all_classical_yogas
        yogas = detect_all_classical_yogas(chart)
        if yogas:
            for y in yogas[:12]:
                name = y.get("name", "?")
                sev = y.get("severity", 0)
                interp = (y.get("interpretation", "") or "")[:200]
                stars = "★" * min(5, max(1, sev)) + "☆" * (5 - min(5, max(1, sev)))
                flow.append(Paragraph(
                    f"&bull; <b>{name}</b>  <font color='#b88a37'>{stars}</font>",
                    st["bullet"]))
                flow.append(Paragraph(
                    f"&nbsp;&nbsp;&nbsp;<font color='#5d2e8c' size='9'><i>{interp}</i></font>",
                    st["bullet"]))
        else:
            flow.append(Paragraph("(No major classical yogas detected)", st["body"]))
    except Exception as exc:
        flow.append(Paragraph(f"(Yoga detection failed: {exc})", st["body"]))

    return flow


# ════════════════════════════════════════════════════════════════════════════
#  Page 3: Rasi (D1) + Navamsa (D9) South-Indian box charts
# ════════════════════════════════════════════════════════════════════════════

# South Indian box layout — each rasi has a fixed grid cell.
# Order: top row Pis/Ari/Tau/Gem, right col Can/Leo, bottom row Vir/Lib/Sco/Sag, left col Cap/Aqu
# Returns dict: rasi_name → (row, col) in a 4x4 grid
SI_LAYOUT = {
    "Pisces":    (0, 0), "Aries":     (0, 1), "Taurus":    (0, 2), "Gemini":    (0, 3),
    "Aquarius":  (1, 0),                                                "Cancer":    (1, 3),
    "Capricorn": (2, 0),                                                "Leo":       (2, 3),
    "Sagittarius":(3, 0),"Scorpio":   (3, 1), "Libra":     (3, 2), "Virgo":     (3, 3),
}

PLANET_ABBR = {"Sun":"Su", "Moon":"Mo", "Mars":"Ma", "Mercury":"Me",
               "Jupiter":"Ju", "Venus":"Ve", "Saturn":"Sa", "Rahu":"Ra", "Ketu":"Ke"}


def _build_chart_box(positions_by_rasi, lagna_rasi, title, st):
    """Build a 4x4 South-Indian style chart with planets shown in each rasi.
    positions_by_rasi: dict {rasi_name: [planet_abbr_list]}
    lagna_rasi: highlight this rasi.
    """
    grid = [[None]*4 for _ in range(4)]
    # Fill rasi labels + planets
    for rasi, (r, c) in SI_LAYOUT.items():
        planets = positions_by_rasi.get(rasi, [])
        plist = " ".join(planets) if planets else ""
        marker = " (Lag)" if rasi == lagna_rasi else ""
        cell_html = (f"<font size='6' color='#6b6b6b'>{rasi[:3]}{marker}</font><br/>"
                     f"<font size='8'><b>{plist}</b></font>")
        grid[r][c] = Paragraph(cell_html, st["bullet"])
    # Center cells: chart title
    title_html = f"<para align='center'><font size='10' color='#312e81'><b>{title}</b></font></para>"
    grid[1][1] = Paragraph(title_html, st["bullet"])
    grid[1][2] = Paragraph("", st["bullet"])
    grid[2][1] = Paragraph("", st["bullet"])
    grid[2][2] = Paragraph("", st["bullet"])

    t = Table(grid, colWidths=[2.0*cm]*4, rowHeights=[2.0*cm]*4)
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, INDIGO),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        # Merge center 2x2 cells
        ("SPAN", (1,1), (2,2)),
        ("ALIGN", (1,1), (2,2), "CENTER"),
        ("VALIGN", (1,1), (2,2), "MIDDLE"),
        ("BACKGROUND", (1,1), (2,2), GREY_LT),
    ]))
    return t


def page_rasi_navamsa(chart, st):
    flow = []
    flow.append(Paragraph("RASI CHART (D1) + NAVAMSA (D9)", st["h1"]))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8))
    flow.append(Paragraph(
        "<i>RASI (D1) is your main birth chart — current life. NAVAMSA (D9) is the divisional "
        "chart for marriage, dharma, and inner strength. South-Indian box format (planet "
        "abbreviations: Su=Sun, Mo=Moon, Ma=Mars, Me=Mercury, Ju=Jupiter, Ve=Venus, Sa=Saturn, "
        "Ra=Rahu, Ke=Ketu).</i>",
        st["small"]))
    flow.append(Spacer(1, 0.3*cm))

    # Build D1 positions_by_rasi
    pos = chart["positions"]
    d1_by_rasi = {}
    for p, pd in pos.items():
        rasi = pd.get("rasi", "")
        abbr = PLANET_ABBR.get(p, p[:2])
        d1_by_rasi.setdefault(rasi, []).append(abbr)
    lagna_rasi = chart.get("lagna", "")

    d1_chart = _build_chart_box(d1_by_rasi, lagna_rasi, f"RASI (D1)<br/>Lagna: {lagna_rasi}", st)

    # Build D9 positions_by_rasi
    try:
        from divisional_charts import build_divisional_chart
        d9 = build_divisional_chart(chart, varga="D9")
        d9_by_rasi = {}
        for p, pd in d9["positions"].items():
            rasi = pd.get("rasi", "")
            abbr = PLANET_ABBR.get(p, p[:2])
            d9_by_rasi.setdefault(rasi, []).append(abbr)
        d9_lagna = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
                    "Sagittarius","Capricorn","Aquarius","Pisces"][d9["lagna_idx"]]
        d9_chart = _build_chart_box(d9_by_rasi, d9_lagna, f"NAVAMSA (D9)<br/>Lagna: {d9_lagna}", st)
    except Exception:
        d9_chart = Paragraph("(D9 chart computation failed)", st["body"])

    # Side-by-side layout
    side_by_side = Table([[d1_chart, d9_chart]], colWidths=[8.5*cm, 8.5*cm])
    side_by_side.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
    ]))
    flow.append(side_by_side)

    # Sign-house meaning reference (mini)
    flow.append(Spacer(1, 0.5*cm))
    flow.append(Paragraph("<b>What each house represents</b>", st["h3"]))
    HOUSE_MEAN = {
        1: "self, body, personality",
        2: "wealth, family, speech",
        3: "siblings, courage, short trips",
        4: "home, mother, comforts",
        5: "children, creativity, romance, intellect",
        6: "work, health, daily routine, debts",
        7: "marriage, partnerships",
        8: "transformation, longevity, hidden matters",
        9: "father, dharma, fortune, higher learning",
        10: "career, public role, achievement",
        11: "income, gains, friends, big goals",
        12: "expenses, foreign lands, spirituality, sleep",
    }
    h_rows = []
    for r1, r2 in [(1, 7), (2, 8), (3, 9), (4, 10), (5, 11), (6, 12)]:
        h_rows.append([
            Paragraph(f"<b>H{r1}</b> {HOUSE_MEAN[r1]}", st["bullet"]),
            Paragraph(f"<b>H{r2}</b> {HOUSE_MEAN[r2]}", st["bullet"]),
        ])
    t = Table(h_rows, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    flow.append(t)
    return flow


# ════════════════════════════════════════════════════════════════════════════
#  Page 4: Ashtakavarga Grid
# ════════════════════════════════════════════════════════════════════════════

def page_ashtakavarga(chart, st):
    flow = []
    flow.append(Paragraph("ASHTAKAVARGA GRID", st["h1"]))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8))
    flow.append(Paragraph(
        "<i>Ashtakavarga is a points-based strength system. Each planet awards 'bindus' (points) "
        "to each house from 1 to 8. The total per house (Sarvashtakavarga) shows how supported "
        "that house is. Houses with high total bindus give good results; low totals indicate "
        "struggle. Norms: 30+ strong, 25-29 average, below 25 weak.</i>",
        st["small"]))
    flow.append(Spacer(1, 0.2*cm))

    try:
        from engine.ashtakavarga import compute_bhinna_ashtakavarga
        bav = compute_bhinna_ashtakavarga(chart)
    except Exception as exc:
        flow.append(Paragraph(f"(Ashtakavarga computation failed: {exc})", st["body"]))
        return flow

    PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    HOUSE_COLS = list(range(1, 13))

    # Header
    rows = [["Planet"] + [f"H{h}" for h in HOUSE_COLS] + ["Total"]]

    # Bindu per planet per house
    sarva = [0] * 12
    for p in PLANET_ORDER:
        if p not in bav: continue
        scores = bav[p]
        row = [Paragraph(f"<b>{p}</b>", st["bullet"])]
        planet_total = 0
        for h in HOUSE_COLS:
            v = scores.get(f"house_{h}", 0)
            sarva[h-1] += v
            planet_total += v
            row.append(Paragraph(f"<font size='9'>{v}</font>", st["bullet"]))
        row.append(Paragraph(f"<b>{planet_total}</b>", st["bullet"]))
        rows.append(row)

    # Sarva total row
    sarva_row = [Paragraph("<b>SARVA</b>", st["bullet"])]
    for h_idx, total in enumerate(sarva):
        color = "#16a34a" if total >= 30 else ("#d97706" if total >= 25 else "#c0392b")
        sarva_row.append(Paragraph(
            f"<font size='9' color='{color}'><b>{total}</b></font>",
            st["bullet"]))
    sarva_row.append(Paragraph(f"<b>{sum(sarva)}</b>", st["bullet"]))
    rows.append(sarva_row)

    col_widths = [1.6*cm] + [1.1*cm]*12 + [1.2*cm]
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), INDIGO),
        ("TEXTCOLOR", (0,0), (-1,0), CREAM),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),
        ("FONTSIZE", (0,1), (-1,-1), 9),
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-2), [white, GREY_LT]),
        ("BACKGROUND", (0,-1), (-1,-1), CREAM),
        ("FONTNAME", (0,-1), (-1,-1), "Helvetica-Bold"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("GRID", (0,0), (-1,-1), 0.3, GREY_MD),
        ("LINEBELOW", (0,0), (-1,0), 1.0, GOLD),
        ("LINEABOVE", (0,-1), (-1,-1), 1.0, GOLD),
    ]))
    flow.append(t)

    # Interpretation of strong / weak houses
    flow.append(Spacer(1, 0.4*cm))
    flow.append(Paragraph("<b>Your strong &amp; weak houses</b>", st["h3"]))
    strong = sorted([(h, sarva[h-1]) for h in HOUSE_COLS if sarva[h-1] >= 30],
                     key=lambda x: -x[1])[:3]
    weak = sorted([(h, sarva[h-1]) for h in HOUSE_COLS if sarva[h-1] < 25],
                   key=lambda x: x[1])[:3]

    HOUSE_MEAN = {
        1: "self & body", 2: "wealth & family", 3: "siblings & courage",
        4: "home & mother", 5: "children & creativity", 6: "work & health",
        7: "marriage & partnerships", 8: "transformation & hidden",
        9: "father & fortune", 10: "career & public role",
        11: "gains & big goals", 12: "expenses & spirituality"
    }
    if strong:
        flow.append(Paragraph("<b><font color='#16a34a'>Strong houses (well-supported):</font></b>", st["bullet"]))
        for h, t in strong:
            flow.append(Paragraph(f"&nbsp;&nbsp;&bull; H{h} ({HOUSE_MEAN[h]}) — {t} bindus", st["bullet"]))
    if weak:
        flow.append(Paragraph("<b><font color='#c0392b'>Weak houses (need extra effort):</font></b>", st["bullet"]))
        for h, t in weak:
            flow.append(Paragraph(f"&nbsp;&nbsp;&bull; H{h} ({HOUSE_MEAN[h]}) — {t} bindus", st["bullet"]))

    return flow


# ════════════════════════════════════════════════════════════════════════════
#  Page 5+: Full Vimshottari Dasha-Bhukti-Antara Table
# ════════════════════════════════════════════════════════════════════════════

def page_vimshottari_full(chart, st):
    """Full 3-level Vimshottari table: 9 MDs × 9 ADs × 9 PDs with dates spanning ~120 years."""
    flow = []
    flow.append(Paragraph("VIMSHOTTARI DASHA — FULL TABLE", st["h1"]))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8))
    flow.append(Paragraph(
        "<i>Vimshottari is the 120-year planetary clock. Your life is divided into 9 Mahadashas "
        "(MD = main period), each containing 9 Antardashas (AD = sub-period), each containing "
        "9 Pratyantar Dashas (PD = sub-sub period). Use this to look up which planet rules any "
        "date in your life. ▶ = currently active.</i>",
        st["small"]))
    flow.append(Spacer(1, 0.3*cm))

    try:
        from granular_dasha import build_full_timeline
    except Exception as exc:
        flow.append(Paragraph(f"(Dasha computation failed: {exc})", st["body"]))
        return flow

    today = dt.datetime.now()
    timeline = build_full_timeline(chart, levels=3)

    md_records = [r for r in timeline if r.get("level") == 1]
    ad_by_md_idx = {}  # md_record_id → list of ad records
    pd_by_ad = {}      # (md_lord, ad_lord, ad_start) → list of pd records

    for r in timeline:
        if r.get("level") == 2:
            key = r["md"]
            ad_by_md_idx.setdefault(key, []).append(r)
        elif r.get("level") == 3:
            key = (r["md"], r["ad"], r["start"].strftime("%Y%m%d"))
            pd_by_ad.setdefault(key, []).append(r)

    # Build a compact table per MD: header row = MD info, then AD rows (each lists its PDs as short text)
    for md_idx, md in enumerate(md_records[:9], 1):
        md_lord = md["md"]
        md_start = md["start"]; md_end = md["end"]
        is_md_now = md_start <= today <= md_end
        md_marker = "▶ NOW" if is_md_now else ("✓ past" if md_end < today else "→ future")
        md_color = "#16a34a" if is_md_now else ("#6b6b6b" if md_end < today else "#7e3a96")

        # MD header
        flow.append(Paragraph(
            f"<font size='12' color='#b88a37'><b>Mahadasha {md_idx}: {md_lord}</b></font> &nbsp;·&nbsp; "
            f"<b>{md_start.strftime('%d-%b-%Y')} → {md_end.strftime('%d-%b-%Y')}</b> &nbsp;·&nbsp; "
            f"<font color='{md_color}'><b>{md_marker}</b></font>",
            st["h3"]))

        # Antardasha table
        ad_rows = [["Sub-period (AD)", "Start date", "End date", "Years", "PDs (short)"]]
        ads = sorted([a for a in ad_by_md_idx.get(md_lord, []) if md_start <= a["start"] < md_end],
                      key=lambda x: x["start"])
        for ad in ads:
            ad_lord = ad["ad"]
            is_ad_now = ad["start"] <= today <= ad["end"]
            prefix = "▶ " if is_ad_now else ""
            # Compact PD summary: just lord names with start month
            pds = pd_by_ad.get((ad["md"], ad["ad"], ad["start"].strftime("%Y%m%d")), [])
            pds = sorted(pds, key=lambda x: x["start"])
            pd_summary = ", ".join(
                f"{p['pd'][:2]}({p['start'].strftime('%b%y')})" for p in pds[:9]
            )
            ad_rows.append([
                Paragraph(f"<b>{prefix}{md_lord}-{ad_lord}</b>", st["bullet"]),
                Paragraph(ad["start"].strftime("%d-%b-%Y"), st["bullet"]),
                Paragraph(ad["end"].strftime("%d-%b-%Y"), st["bullet"]),
                Paragraph(f"{ad.get('years', 0):.2f}", st["bullet"]),
                Paragraph(f"<font size='7'>{pd_summary}</font>", st["bullet"]),
            ])
        if len(ad_rows) > 1:
            t = Table(ad_rows, colWidths=[2.6*cm, 2.4*cm, 2.4*cm, 1.4*cm, 7.2*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), INDIGO),
                ("TEXTCOLOR", (0,0), (-1,0), CREAM),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,0), 9),
                ("FONTSIZE", (0,1), (-1,-1), 8),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
                ("TOPPADDING", (0,0), (-1,-1), 3),
                ("BOTTOMPADDING", (0,0), (-1,-1), 3),
                ("LEFTPADDING", (0,0), (-1,-1), 5),
                ("LINEBELOW", (0,0), (-1,0), 0.8, GOLD),
            ]))
            flow.append(t)
        flow.append(Spacer(1, 0.3*cm))

        # Page break every 2 MDs to keep pages readable
        if md_idx % 2 == 0 and md_idx < 9:
            flow.append(PageBreak())

    return flow


# ════════════════════════════════════════════════════════════════════════════
#  Additional Vargas (Divisional Charts) — D1 through D60 in grid layout
# ════════════════════════════════════════════════════════════════════════════

def _build_mini_chart_box(positions_by_rasi, lagna_rasi, title, st, cell_size=1.1):
    """Smaller version of the South-Indian chart for grid layout (3 per row)."""
    grid = [[None]*4 for _ in range(4)]
    for rasi, (r, c) in SI_LAYOUT.items():
        planets = positions_by_rasi.get(rasi, [])
        plist = " ".join(planets) if planets else ""
        marker = "*" if rasi == lagna_rasi else ""
        cell_html = (f"<font size='5' color='#6b6b6b'>{rasi[:3]}{marker}</font><br/>"
                     f"<font size='6'><b>{plist}</b></font>")
        grid[r][c] = Paragraph(cell_html, st["bullet"])
    title_html = f"<para align='center'><font size='7' color='#312e81'><b>{title}</b></font></para>"
    grid[1][1] = Paragraph(title_html, st["bullet"])
    grid[1][2] = Paragraph("", st["bullet"])
    grid[2][1] = Paragraph("", st["bullet"])
    grid[2][2] = Paragraph("", st["bullet"])
    t = Table(grid, colWidths=[cell_size*cm]*4, rowHeights=[cell_size*cm]*4)
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.4, INDIGO),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("LEFTPADDING", (0,0), (-1,-1), 2),
        ("RIGHTPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 2),
        ("SPAN", (1,1), (2,2)),
        ("BACKGROUND", (1,1), (2,2), GREY_LT),
    ]))
    return t


def page_all_vargas(chart, st):
    """All 10+ divisional charts (vargas) in a 3-per-row grid."""
    flow = []
    flow.append(Paragraph("DIVISIONAL CHARTS (VARGAS)", st["h1"]))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8))
    flow.append(Paragraph(
        "<i>Each Varga is a divisional chart focused on a specific life area. Planet positions "
        "across multiple vargas show consistency (vargottama = same sign in D1 and D9 = very "
        "strong). Star (*) marks the Lagna.</i>",
        st["small"]))
    flow.append(Spacer(1, 0.3*cm))

    VARGAS_INFO = [
        ("D1", "Rasi", "main life chart"),
        ("D2", "Hora", "wealth + family"),
        ("D3", "Drekkana", "siblings + courage"),
        ("D7", "Saptamsa", "children"),
        ("D9", "Navamsa", "marriage + dharma"),
        ("D10", "Dashamsa", "career + public role"),
        ("D12", "Dwadashamsa", "parents"),
        ("D24", "Chaturvimsamsa", "education"),
        ("D30", "Trimshamsa", "misfortunes"),
        ("D60", "Shashtiamsa", "past karma"),
    ]

    try:
        from divisional_charts import build_divisional_chart
    except Exception:
        flow.append(Paragraph("(divisional_charts module unavailable)", st["body"]))
        return flow

    SIGNS_LOCAL = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

    chart_boxes = []
    pos = chart["positions"]
    d1_by_rasi = {}
    for p, pd in pos.items():
        rasi = pd.get("rasi", "")
        abbr = PLANET_ABBR.get(p, p[:2])
        d1_by_rasi.setdefault(rasi, []).append(abbr)
    d1_box = _build_mini_chart_box(d1_by_rasi, chart.get("lagna", ""),
                                     f"D1 Rasi<br/>Lag: {chart.get('lagna', '?')[:3]}", st)
    chart_boxes.append((d1_box, "D1 - Rasi (main)"))

    for varga_code, name, purpose in VARGAS_INFO[1:]:
        try:
            d = build_divisional_chart(chart, varga=varga_code)
            d_by_rasi = {}
            for p, pd in d["positions"].items():
                rasi = pd.get("rasi", "")
                abbr = PLANET_ABBR.get(p, p[:2])
                d_by_rasi.setdefault(rasi, []).append(abbr)
            d_lagna = SIGNS_LOCAL[d["lagna_idx"]] if d.get("lagna_idx") is not None else ""
            box = _build_mini_chart_box(d_by_rasi, d_lagna,
                                          f"{varga_code} {name}<br/>Lag: {d_lagna[:3]}", st)
            chart_boxes.append((box, f"{varga_code} - {name} ({purpose})"))
        except Exception:
            pass

    # Lay out 3 per row with caption underneath each
    layout_rows = []
    for i in range(0, len(chart_boxes), 3):
        row = [b[0] for b in chart_boxes[i:i+3]]
        while len(row) < 3:
            row.append(Paragraph("", st["bullet"]))
        layout_rows.append(row)
        cap_row = [Paragraph(f"<font size='7' color='#6b6b6b'>{b[1]}</font>", st["bullet"])
                   for b in chart_boxes[i:i+3]]
        while len(cap_row) < 3:
            cap_row.append(Paragraph("", st["bullet"]))
        layout_rows.append(cap_row)

    grid_t = Table(layout_rows, colWidths=[5.5*cm, 5.5*cm, 5.5*cm])
    grid_t.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("LEFTPADDING", (0,0), (-1,-1), 2),
        ("RIGHTPADDING", (0,0), (-1,-1), 2),
        ("TOPPADDING", (0,0), (-1,-1), 2),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ]))
    flow.append(grid_t)
    return flow


# ════════════════════════════════════════════════════════════════════════════
#  Bhava Sphutas (house cusps) — start, middle, end longitudes per house
# ════════════════════════════════════════════════════════════════════════════

def page_bhava_chart(chart, st):
    flow = []
    flow.append(Paragraph("BHAVA SPHUTAS (House Cusps)", st["h1"]))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8))
    flow.append(Paragraph(
        "<i>Bhava Sphutas are the start, middle (cusp), and end longitudes of each of the 12 houses. "
        "Used for fine-grained house-strength analysis (Bhava Bala). In Whole-Sign / Equal-House "
        "system, the lagna degree is the cusp of house 1, and each subsequent house cusp is 30 deg further.</i>",
        st["small"]))
    flow.append(Spacer(1, 0.3*cm))

    lagna_lon = float(chart.get("lagna_lon", chart.get("lagna_idx", 0)*30 + chart.get("lagna_deg", 15)))
    lagna_idx = int(lagna_lon // 30)

    SIGNS_BH = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                 "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

    def _dms2(deg):
        d = int(deg); rest = (deg - d) * 60
        m = int(rest); s = int((rest - m) * 60)
        return f"{d:02d}d {m:02d}m {s:02d}s"

    HOUSE_LABELS = {
        1: "Lagna (Self)", 2: "Dhana (Wealth)", 3: "Sahaja (Sibling)",
        4: "Sukha (Home)", 5: "Putra (Children)", 6: "Ari (Health)",
        7: "Yuvati (Spouse)", 8: "Randhra (Longevity)", 9: "Dharma (Father)",
        10: "Karma (Career)", 11: "Labha (Gains)", 12: "Vyaya (Expenses)",
    }
    rows = [["H#", "Bhava", "Start", "Middle (cusp)", "End", "Sign"]]
    for h in range(1, 13):
        sign_idx = (lagna_idx + h - 1) % 12
        mid_lon = lagna_lon + (h - 1) * 30
        start_lon = mid_lon - 15
        end_lon = mid_lon + 15
        start_deg = (start_lon % 30); mid_deg = (mid_lon % 30); end_deg = (end_lon % 30)
        rows.append([
            Paragraph(f"<b>{h}</b>", st["bullet"]),
            Paragraph(HOUSE_LABELS[h], st["bullet"]),
            Paragraph(f"<font size='8'>{_dms2(start_deg)}</font>", st["bullet"]),
            Paragraph(f"<font size='8'><b>{_dms2(mid_deg)}</b></font>", st["bullet"]),
            Paragraph(f"<font size='8'>{_dms2(end_deg)}</font>", st["bullet"]),
            Paragraph(SIGNS_BH[sign_idx], st["bullet"]),
        ])
    t = Table(rows, colWidths=[0.8*cm, 4.5*cm, 2.8*cm, 3.0*cm, 2.8*cm, 2.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), INDIGO),
        ("TEXTCOLOR", (0,0), (-1,0), CREAM),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 9),
        ("FONTSIZE", (0,1), (-1,-1), 9),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [white, GREY_LT]),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
        ("LINEBELOW", (0,0), (-1,0), 1.0, GOLD),
    ]))
    flow.append(t)
    return flow
