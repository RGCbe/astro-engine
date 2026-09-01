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


_ENG = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
_TA_ROMAN2 = {n: i for i, n in enumerate(
    ["Mesham", "Rishabam", "Mithunam", "Kadagam", "Simmam", "Kanni",
     "Thulaam", "Viruchigam", "Dhanusu", "Makaram", "Kumbam", "Meenam"])}
_PL_TA_ORDER = [("Sun", "சூரியன்"), ("Moon", "சந்திரன்"), ("Mars", "செவ்வாய்"),
                ("Mercury", "புதன்"), ("Jupiter", "குரு"), ("Venus", "சுக்கிரன்"),
                ("Saturn", "சனி"), ("Rahu", "ராகு"), ("Ketu", "கேது")]
_HDR = HexColor("#312e81")
_CREAM = HexColor("#faf6e8")


def _tbl_style(header=True):
    s = [("GRID", (0, 0), (-1, -1), 0.4, GREY_LT), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
         ("ALIGN", (1, 0), (-1, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 3),
         ("BOTTOMPADDING", (0, 0), (-1, -1), 3), ("LEFTPADDING", (0, 0), (-1, -1), 4)]
    if header:
        s += [("BACKGROUND", (0, 0), (-1, 0), _HDR), ("TEXTCOLOR", (0, 0), (-1, 0), _CREAM)]
    return TableStyle(s)


def _ta_sign(idx):
    from tamil_translations import RASIS_TA
    ta = ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
          "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"]
    return ta[idx % 12]


def page_ashtakavarga_ta(chart):
    """சர்வாஷ்டகவர்க்கம் — per-sign bindus + directional strength (Tamil)."""
    flow = [TP("அஷ்டகவர்க்கம் (சர்வாஷ்டகம்)", "h1"), divider()]
    try:
        class C:
            def __init__(s, l, p): s.lagna_lon = l; s.positions = p
        pos = {p: d["lon_abs"] for p, d in chart["positions"].items() if p not in ("Lagna", "Maandi")}
        from engine.ashtakavarga import summary as _sav
        r = _sav(C(chart["positions"]["Lagna"]["lon_abs"], pos))["sarva_ashtakavarga"]
        per = r.get("totals_per_sign")
        if isinstance(per, dict):
            per = [per[k] for k in sorted(per)]
    except Exception as exc:
        flow.append(TP(f"(அஷ்டகவர்க்கம் தோல்வி: {exc})", "small"))
        return flow

    rows = [[TP("ராசி", "cell_bold", color=_CREAM), TP("பிந்து", "cell_bold", color=_CREAM)]]
    for i in range(12):
        rows.append([TP(_ta_sign(i), "cell"), TP(str(per[i]), "cell")])
    rows.append([TP("மொத்தம்", "cell_bold"), TP(str(sum(per)), "cell_bold")])
    t = Table(rows, colWidths=[4 * cm, 3 * cm]); t.setStyle(_tbl_style())
    # Directional strength (4 groups of 3 signs)
    E = per[0] + per[4] + per[8]; S = per[1] + per[5] + per[9]
    W = per[2] + per[6] + per[10]; N = per[3] + per[7] + per[11]
    drows = [[TP("கிழக்கு", "cell_bold", color=_CREAM), TP("தெற்கு", "cell_bold", color=_CREAM), TP("மேற்கு", "cell_bold", color=_CREAM), TP("வடக்கு", "cell_bold", color=_CREAM)],
             [TP(str(E), "cell"), TP(str(S), "cell"), TP(str(W), "cell"), TP(str(N), "cell")]]
    dt = Table(drows, colWidths=[3.4 * cm] * 4); dt.setStyle(_tbl_style())
    flow += [t, Spacer(1, 0.4 * cm), TP("திசை பலம்", "h2"), dt]
    return flow


def page_dasavarga_ta(chart):
    """தசவர்க்கம் — 10 divisional charts, sign per planet (Tamil)."""
    flow = [TP("தசவர்க்கம் (10 வர்க்கங்கள்)", "h1"), divider()]
    vargas = [("D1", "ராசி"), ("D2", "ஹோரை"), ("D3", "திரேக்காணம்"), ("D7", "சப்தாம்சம்"),
              ("D9", "நவாம்சம்"), ("D12", "துவாதசாம்சம்"), ("D10", "தசாம்சம்"),
              ("D16", "ஷோடசாம்சம்"), ("D30", "திரிம்சாம்சம்"), ("D60", "ஷஷ்டியாம்சம்")]
    try:
        from engine.vargas import all_vargas
        av = all_vargas(chart)
    except Exception:
        av = {}
    _SHORT = {"Sun": "சூ", "Moon": "சந்", "Mars": "செ", "Mercury": "பு", "Jupiter": "கு",
              "Venus": "சுக்", "Saturn": "சனி", "Rahu": "ரா", "Ketu": "கே"}
    header = [TP("வர்க்கம்", "cell_bold", color=_CREAM)] + [TP(_SHORT[p], "cell_bold", color=_CREAM) for p, _ in _PL_TA_ORDER]
    rows = [header]
    for vg, vta in vargas:
        signmap = {}
        dv = av.get(vg)
        if dv and dv.get("positions"):
            for p, _ in _PL_TA_ORDER:
                pr = dv["positions"].get(p, {}).get("rasi", "")
                signmap[p] = _ENG.index(pr) if pr in _ENG else (_TA_ROMAN2.get(pr) if pr in _TA_ROMAN2 else None)
        row = [TP(vta, "cell_small")]
        for p, _ in _PL_TA_ORDER:
            idx = signmap.get(p)
            row.append(TP(_ta_sign(idx)[:4] if idx is not None else "-", "cell_small"))
        rows.append(row)
    t = Table(rows, colWidths=[2.4 * cm] + [1.35 * cm] * 9); t.setStyle(_tbl_style())
    flow.append(t)
    return flow


def page_vimshottari_ta(chart):
    """விம்சோத்தரி தசா-புக்தி — MD list + running-MD buktis (Tamil)."""
    flow = [TP("விம்சோத்தரி தசா புக்தி", "h1"), divider()]
    _PLTA = dict(_PL_TA_ORDER)
    try:
        from granular_dasha import build_full_timeline
        tl = build_full_timeline(chart, levels=2)
    except Exception as exc:
        flow.append(TP(f"(தசா தோல்வி: {exc})", "small")); return flow
    mds = [r for r in tl if r.get("level") == 1]
    rows = [[TP("#", "cell_bold", color=_CREAM), TP("தசா", "cell_bold", color=_CREAM), TP("தொடக்கம்", "cell_bold", color=_CREAM), TP("முடிவு", "cell_bold", color=_CREAM)]]
    for i, m in enumerate(mds, 1):
        rows.append([TP(str(i), "cell"), TP(_PLTA.get(m.get("md"), m.get("md")), "cell"),
                     TP(str(m.get("start"))[:10], "cell"), TP(str(m.get("end"))[:10], "cell")])
    t = Table(rows, colWidths=[0.9 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]); t.setStyle(_tbl_style())
    flow += [TP("மகா தசா வரிசை (120 ஆண்டு)", "h2"), t, Spacer(1, 0.4 * cm)]
    # buktis of the first (running-at-birth) MD
    ads = [r for r in tl if r.get("level") == 2 and r.get("md") == mds[0].get("md")]
    if ads:
        brows = [[TP("புக்தி", "cell_bold", color=_CREAM), TP("தொடக்கம்", "cell_bold", color=_CREAM), TP("முடிவு", "cell_bold", color=_CREAM)]]
        for a in ads:
            brows.append([TP(_PLTA.get(a.get("ad"), a.get("ad")), "cell"),
                          TP(str(a.get("start"))[:10], "cell"), TP(str(a.get("end"))[:10], "cell")])
        bt = Table(brows, colWidths=[3.5 * cm, 3.5 * cm, 3.5 * cm]); bt.setStyle(_tbl_style())
        flow += [TP(f"{_PLTA.get(mds[0].get('md'), mds[0].get('md'))} தசா — புக்திகள்", "h2"), bt]
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

    # Tamil technical tables (dasavarga, ashtakavarga, vimshottari)
    for name, fn in (("dasavarga_ta", page_dasavarga_ta),
                     ("ashtakavarga_ta", page_ashtakavarga_ta),
                     ("vimshottari_ta", page_vimshottari_ta)):
        try:
            section = fn(chart)
            if section:
                flow.extend(section)
                flow.append(PageBreak())
        except Exception as exc:
            print(f"[{name}] WARNING: {exc}")

    # Bhava cusp chart — English builder (Tamil-isation pending)
    try:
        flow.extend(page_bhava_chart(chart, st))
        flow.append(PageBreak())
    except Exception as exc:
        print(f"[bhava] WARNING: {exc}")

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
