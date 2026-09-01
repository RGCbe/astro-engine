"""Data-only jathagam PDF — the AstroSign / Logic-Vision style chart booklet.

Details ONLY (positions, panchanga, charts, cusps, vargas, ashtakavarga,
dasa-bukti, numerology). NO predictions or interpretation. Mirrors the
13-page structure of a traditional Tamil print.

Usage:
    python runtime/generate_jathagam_data.py --chart chart.json --out out.pdf

`chart.json` is the same payload the API writes for the PDF endpoint
(name, birth{}, positions{}, lagna/lagna_idx, ayanamsa, moon_rasi,
janma_nakshatra, traditional_extras, identity).
"""
import os
import sys
import json
import argparse
import datetime as dt
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, HRFlowable)

from generate_deep_pdf import styles, INDIGO, GOLD, GREY_LT
from traditional_jadhagam_pages import (
    page_birth_details, page_rasi_navamsa,
    page_bhava_chart, page_all_vargas, page_ashtakavarga, page_vimshottari_full,
)

RASIS = ["Mesham", "Rishabam", "Mithunam", "Kadagam", "Simmam", "Kanni",
         "Thulaam", "Viruchigam", "Dhanusu", "Makaram", "Kumbam", "Meenam"]


def _dms(deg_in_sign):
    d = int(deg_in_sign)
    rest = (deg_in_sign - d) * 60
    m = int(rest)
    s = int(round((rest - m) * 60))
    return f"{d:02d}° {m:02d}' {s:02d}\""


def page_positions_table(chart, st):
    """AstroSign page-3 style graha table: rasi, degree, nakshatra/pada,
    nakshatra lord, navamsa, retrograde. Data only — no yogas, no readings."""
    flow = [Paragraph("PLANETARY POSITIONS (NIRAYANA)", st["h1"]),
            HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8)]
    pos = chart.get("positions", {})
    order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    header = ["#", "Planet", "Rasi", "Degree", "Nakshatra", "Pada", "Nak Lord", "Navamsa"]
    rows = [header]
    for i, p in enumerate(order, 1):
        d = pos.get(p)
        if not d:
            continue
        lon_abs = d.get("lon_abs", d.get("lon", 0.0))
        nav = RASIS[int(lon_abs / (10 / 3)) % 12]
        rows.append([str(i), p, d.get("rasi", ""), _dms(lon_abs % 30),
                     d.get("nak", ""), str(d.get("pada", "")),
                     d.get("nak_lord", ""), nav])
    # Maandi (Gulika) row — engine day-part computation
    md = pos.get("Mandi")
    if md:
        md_lon = md.get("lon_abs", md.get("lon", 0.0))
        rows.append(["", "Mandi", md.get("rasi", ""), _dms(md_lon % 30),
                     md.get("nak", ""), str(md.get("pada", "")), md.get("nak_lord", ""),
                     RASIS[int(md_lon / (10 / 3)) % 12]])
    # Lagna row
    if "Lagna" in pos or chart.get("lagna"):
        lg = pos.get("Lagna", {})
        lg_lon = lg.get("lon_abs", chart.get("lagna_lon", 0.0))
        rows.append(["", "Lagna", chart.get("lagna", ""), _dms(lg_lon % 30),
                     lg.get("nak", ""), str(lg.get("pada", "")), lg.get("nak_lord", ""),
                     RASIS[int(lg_lon / (10 / 3)) % 12]])
    t = Table(rows, colWidths=[0.8*cm, 2.1*cm, 2.3*cm, 2.6*cm, 3.0*cm, 1.0*cm, 2.0*cm, 2.3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INDIGO), ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, GREY_LT]), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]))
    flow.append(t)
    return flow

REPORTS = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "reports"
REPORTS.mkdir(exist_ok=True)

# Standard single-digit numerology table (psychic/day number → attributes).
NUM_PLANET = {1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu", 5: "Mercury",
              6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars"}
NUM_GEM = {1: "Ruby", 2: "Pearl", 3: "Yellow Sapphire", 4: "Gomedh (Hessonite)",
           5: "Emerald", 6: "Diamond", 7: "Cat's Eye (Vaiduriyam)",
           8: "Blue Sapphire", 9: "Red Coral"}
NUM_LUCKY_DAYS = {1: "Sunday, Monday", 2: "Monday, Friday",
                  3: "Thursday, Friday, Tuesday", 4: "Saturday, Sunday",
                  5: "Wednesday, Friday", 6: "Friday, Wednesday, Tuesday",
                  7: "Wednesday, Friday, Saturday", 8: "Saturday, Sunday",
                  9: "Tuesday, Thursday"}
NUM_FRIENDLY = {1: "1,2,3,9", 2: "1,2,7", 3: "3,6,9", 4: "1,5,6,7",
                5: "1,5,6", 6: "5,6,8", 7: "5,6,8", 8: "3,5,6", 9: "1,3,6,9"}


def _reduce(n: int) -> int:
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def page_numerology(chart, st):
    flow = [Paragraph("NUMEROLOGY (EN KANITHAM)", st["h1"]),
            HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8)]
    b = chart["birth"]
    day = int(b["day"])
    psychic = _reduce(day)
    destiny = _reduce(sum(int(d) for d in f"{b['day']:02d}{b['month']:02d}{b['year']}"))
    planet = NUM_PLANET.get(psychic, "?")
    rows = [
        ["Fate / Psychic number (from day)", f"{psychic}  (day {day})"],
        ["Ruling planet", planet],
        ["Destiny number (full date)", str(destiny)],
        ["Lucky days", NUM_LUCKY_DAYS.get(psychic, "-")],
        ["Lucky dates", ", ".join(str((psychic + 9 * k)) for k in range(3))],
        ["Lucky gem", NUM_GEM.get(psychic, "-")],
        ["Friendly numbers", NUM_FRIENDLY.get(psychic, "-")],
    ]
    t = Table(rows, colWidths=[6 * cm, 10 * cm])
    t.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [white, GREY_LT]),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    flow.append(t)
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph(
        "<i>Psychic number is the day of birth reduced to a single digit; it fixes the "
        "ruling planet and its lucky day/gem associations (classical convention).</i>",
        st["small"]))
    return flow


def page_traditional_cusps(chart, st):
    """Sripati (unequal) bhava cusps + nakshatra reference from the API block."""
    te = chart.get("traditional_extras") or {}
    cusps = te.get("bhava_cusps") or []
    nr = te.get("nakshatra_reference") or {}
    if not cusps and not nr:
        return []
    flow = [Paragraph("SRIPATI BHAVA CUSPS &amp; NAKSHATRA REFERENCE", st["h1"]),
            HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceAfter=8)]
    if nr.get("known"):
        parts = [f"Gana: {nr.get('gana','')}", f"Yoni: {nr.get('yoni','')} ({nr.get('yoni_gender','')})",
                 f"Nadi: {nr.get('nadi','')}", f"Tree: {nr.get('tree','')}"]
        if nr.get("bird"):
            parts.append(f"Bird: {nr['bird']}")
        flow.append(Paragraph("  ·  ".join(parts), st["body"]))
        ch = te.get("chandrashtama_nakshatras") or []
        if ch:
            flow.append(Paragraph("<b>Chandrashtama (avoid) nakshatras:</b> " + ", ".join(ch), st["body"]))
        flow.append(Spacer(1, 0.3 * cm))
    if cusps:
        rows = [["H", "Signification", "Start", "Middle", "End"]]
        for c in cusps:
            rows.append([str(c.get("house", "")), c.get("name", ""),
                         c.get("start_dms", ""), c.get("mid_dms", ""), c.get("end_dms", "")])
        t = Table(rows, colWidths=[0.8 * cm, 4.6 * cm, 3.2 * cm, 3.2 * cm, 3.2 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INDIGO), ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, GREY_LT]), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ]))
        flow.append(t)
    return flow


def generate(chart_path, out_name):
    with open(chart_path, encoding="utf-8") as f:
        chart = json.load(f)
    st = styles()
    out_path = REPORTS / out_name if not os.path.isabs(out_name) else Path(out_name)

    doc = SimpleDocTemplate(str(out_path), pagesize=A4,
                            leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm)

    # Cover line
    flow = [Paragraph(chart.get("name", "Jathagam").upper(), st["title"]),
            Paragraph("Birth Chart — Details Only (no predictions)", st["subtitle"]),
            HRFlowable(width="100%", thickness=1, color=GOLD, spaceAfter=10)]

    # Data pages in traditional order. Each guarded so one failure can't
    # sink the whole booklet.
    builders = [
        ("birth_details", page_birth_details),
        ("planet_positions", page_positions_table),
        ("rasi_navamsa", page_rasi_navamsa),
        ("bhava_chart", page_bhava_chart),
        ("sripati_cusps", page_traditional_cusps),
        ("vargas", page_all_vargas),
        ("ashtakavarga", page_ashtakavarga),
        ("vimshottari", page_vimshottari_full),
        ("numerology", page_numerology),
    ]
    for name, fn in builders:
        try:
            section = fn(chart, st)
            if section:
                flow.extend(section)
                flow.append(PageBreak())
        except Exception as exc:
            print(f"[{name}] WARNING: {exc}")

    doc.build(flow)
    size_kb = out_path.stat().st_size // 1024
    print(f"DONE: {out_path}  ({size_kb} KB)")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cp = Path(args.chart)
    out = args.out or f"{Path(args.chart).stem}_JATHAGAM_DATA.pdf"
    generate(cp, out)


if __name__ == "__main__":
    main()
