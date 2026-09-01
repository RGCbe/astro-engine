"""Data-only Tamil jathagam PDF — Thirukanitham print clone (no predictions).

Mirrors the AstroSign / Logic-Vision 13-page booklet order in Tamil:
  1 cover · 2 panchangam · 3 graha positions · 4 rasi+navamsa ·
  5 sripati bhava cusps · 6 bhava chart · 7 vargas · 8 ashtakavarga ·
  9-12 vimshottari dasa · 13 numerology.

Tamil pages reuse generate_tamil_pdf's HarfBuzz-shaped builders. The
number-heavy technical tables (bhava/vargas/ashtakavarga/dasa) reuse the
bug-fixed English builders from traditional_jadhagam_pages for now; their
Tamil-isation is a follow-up.
"""
import os
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (SimpleDocTemplate, PageBreak, Spacer,
                                Table, TableStyle)

from generate_tamil_pdf import (
    page_jathagam_1_cover, page_birth_panchanga, page_planets,
    page_rasi_navamsa_ta, page_lucky_vidhi_ta,
    page1_layout, content_page, TP, divider, GOLD, GREY_LT, INDIGO,
)
from generate_deep_pdf import styles as _en_styles
from traditional_jadhagam_pages import (
    page_bhava_chart, page_all_vargas, page_ashtakavarga, page_vimshottari_full,
)

REPORTS = Path(__file__).resolve().parent.parent / "reports"
REPORTS.mkdir(exist_ok=True)

_BHAVA_TA = ["லக்னம்", "தனம்", "சகோதரர்", "மாதுர்", "புத்திர", "சத்ரு",
             "களத்திர", "ஆயுள்", "பாக்கியம்", "கர்ம", "லாபம்", "விரய"]


def page_sripati_cusps_ta(chart):
    """Page 5/6: Sripati (unequal) bhava cusps + nakshatra reference (Tamil)."""
    te = chart.get("traditional_extras") or {}
    cusps = te.get("bhava_cusps") or []
    nr = te.get("nakshatra_reference") or {}
    flow = [TP("ஸ்ரீபதி பாவ ஸந்தி மற்றும் நட்சத்திர விவரம்", "h1"), divider()]
    if nr.get("known"):
        parts = [f"கணம்: {nr.get('gana','')}", f"யோனி: {nr.get('yoni','')} ({nr.get('yoni_gender','')})",
                 f"நாடி: {nr.get('nadi','')}", f"மரம்: {nr.get('tree','')}"]
        if nr.get("bird"):
            parts.append(f"பட்சி: {nr['bird']}")
        flow.append(TP("  ·  ".join(parts), "body"))
        ch = te.get("chandrashtama_nakshatras") or []
        if ch:
            flow.append(TP("சந்திராஷ்டம நட்சத்திரங்கள்: " + ", ".join(ch), "body"))
        flow.append(Spacer(1, 0.3 * cm))
    if cusps:
        _HDR = HexColor("#312e81"); _CREAM = HexColor("#faf6e8")
        rows = [[TP("பா", "cell_bold"), TP("பாவம்", "cell_bold"), TP("தொடக்கம்", "cell_bold"),
                 TP("மத்தி", "cell_bold"), TP("முடிவு", "cell_bold")]]
        for c in cusps:
            h = c.get("house", 0)
            rows.append([TP(str(h), "cell"), TP(_BHAVA_TA[h - 1] if 1 <= h <= 12 else "", "cell"),
                         TP(c.get("start_dms", ""), "cell"), TP(c.get("mid_dms", ""), "cell"),
                         TP(c.get("end_dms", ""), "cell")])
        t = Table(rows, colWidths=[0.9 * cm, 3.4 * cm, 3.1 * cm, 3.1 * cm, 3.1 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), _HDR), ("TEXTCOLOR", (0, 0), (-1, 0), _CREAM),
            ("GRID", (0, 0), (-1, -1), 0.5, GREY_LT), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
        flow.append(t)
    return flow


def generate(chart_path, out_name):
    with open(chart_path, encoding="utf-8") as f:
        chart = json.load(f)
    st = _en_styles()
    out_path = REPORTS / out_name if not os.path.isabs(out_name) else Path(out_name)

    flow = []
    # Distinctive Tamil pages (print pages 1-4)
    flow.extend(page_jathagam_1_cover(chart)); flow.append(PageBreak())
    flow.extend(page_birth_panchanga(chart, None)); flow.append(PageBreak())
    flow.extend(page_planets(chart, None)); flow.append(PageBreak())
    flow.extend(page_rasi_navamsa_ta(chart)); flow.append(PageBreak())
    # Sripati cusps (Tamil)
    flow.extend(page_sripati_cusps_ta(chart)); flow.append(PageBreak())

    # Technical tables (English interim — Tamil-isation pending)
    for name, fn in (("bhava", page_bhava_chart), ("vargas", page_all_vargas),
                     ("ashtakavarga", page_ashtakavarga), ("vimshottari", page_vimshottari_full)):
        try:
            section = fn(chart, st)
            if section:
                flow.extend(section)
                flow.append(PageBreak())
        except Exception as exc:
            print(f"[{name}] WARNING: {exc}")

    # Numerology (Tamil)
    flow.extend(page_lucky_vidhi_ta(chart))

    doc = SimpleDocTemplate(str(out_path), pagesize=A4,
                            leftMargin=2.0 * cm, rightMargin=2.0 * cm,
                            topMargin=1.8 * cm, bottomMargin=2.0 * cm,
                            title=f"{chart.get('name', '?')} — Jathagam (Tamil, data only)")
    doc.build(flow, onFirstPage=page1_layout, onLaterPages=content_page)
    size_kb = out_path.stat().st_size // 1024
    print(f"DONE: {out_path}  ({size_kb} KB)")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = args.out or f"{Path(args.chart).stem}_JATHAGAM_DATA_TA.pdf"
    generate(Path(args.chart), out)


if __name__ == "__main__":
    main()
