#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manoj Tamil predictions report - MD + PDF with event_predictor_v2 windows."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_SCRATCH = Path(__file__).resolve().parent
ROOT = _SCRATCH.parent if sys.platform == "win32" else (Path("/opt/astro") if Path("/opt/astro").exists() else _SCRATCH.parent)
RUNTIME = ROOT / "runtime"
REPORTS = ROOT / "reports"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(_SCRATCH))
sys.path.insert(0, str(RUNTIME))

from _report_out_dir import category_report_dir
from engine.jathagam_template import build_jathagam_full, build_prediction_section_header
from engine.event_age_policy import filter_bands_for_age

MANOJ_REPORTS = category_report_dir("manoj", base=REPORTS)

from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from granular_dasha import build_full_timeline, lookup
from tamil_translations import (
    SECTION_HEADERS,
    DOMAIN_TA,
    RULE_ENGINE_DISCLAIMER_TA,
    CATEGORY_TA,
    RASIS_TA,
    NAKSHATRAS_TA,
    ta_event,
    ta_why,
    ta_dasha_chain,
)

CHART_PATH = ROOT / "charts" / "manoj_chart.json"
OUT_MD_TA = MANOJ_REPORTS / "MANOJ_PREDICTIONS_TA.md"
OUT_PDF_TA = MANOJ_REPORTS / "MANOJ_PREDICTIONS_TA.pdf"
OUT_MD_EN = MANOJ_REPORTS / "MANOJ_PREDICTIONS_EN.md"
OUT_PDF_EN = MANOJ_REPORTS / "MANOJ_PREDICTIONS_EN.pdf"

DOMAIN_CATS = {
    "career": {"career", "promotion", "career_breakthrough", "education", "leadership_emergence"},
    "marriage": {"marriage", "engagement", "relationship_phase", "relationship_break", "saham_kalatra"},
    "wealth": {"wealth", "wealth_peak", "inheritance", "property", "wealth_loss", "lakshmi_yoga", "speculation_gain"},
    "health": {"health", "health_self", "self_accident", "saham_roga"},
    "father": {"father"},
}

# Table header strings (Tamil) - kept in translations module keys where possible
HDR = {
    "level": "\u0ba8\u0bbf\u0bb2\u0bc8",
    "dasha": "\u0ba4\u0b9a\u0bc8",
    "until": "\u0bae\u0bc1\u0b9f\u0bbf\u0bb5\u0bc1",
    "effect": "\u0bb5\u0bbf\u0bb3\u0bc8\u0bb5\u0bc1",
    "domain": "\u0ba4\u0bc1\u0bb1\u0bc8",
    "window": "\u0b95\u0bbe\u0bb2\u0bae\u0bcd",
    "plain": "\u0bb5\u0bbf\u0bb3\u0b95\u0bcd\u0b95\u0bae\u0bcd",
    "cause": "\u0b95\u0bbe\u0bb0\u0ba3\u0bae\u0bcd",
    "num": "#",
    "next5": "\u2014 \u0b85\u0b9f\u0bc1\u0ba4\u0bcd\u0ba4 5 \u0b86\u0ba3\u0bcd\u0b9f\u0bc1\u0b95\u0bb3\u0bcd",
    "top5": "\u2014 \u0bae\u0bc1\u0ba4\u0bb2\u0bcd 5 \u0b9a\u0bbe\u0bb3\u0bb0\u0b99\u0bcd\u0b95\u0bb3\u0bcd",
    "no_domain": "(\u0b87\u0ba8\u0bcd\u0ba4 \u0ba4\u0bc1\u0bb1\u0bc8\u0baf\u0bbf\u0bb2\u0bcd \u0b85\u0b9f\u0bc1\u0ba4\u0bcd\u0ba4 5 \u0b86\u0ba3\u0bcd\u0b9f\u0bc1\u0b95\u0bb3\u0bbf\u0bb2\u0bcd \u0b9a\u0bbe\u0bb3\u0bb0\u0bae\u0bcd \u0b87\u0bb2\u0bcd\u0bb2\u0bc8)",
    "page": "\u0baa\u0b95\u0bcd\u0b95\u0bae\u0bcd",
    "report_title": "\u0bb5\u0bbe\u0bb4\u0bcd\u0b95\u0bcd\u0b95\u0bc8 \u0ba8\u0bbf\u0b95\u0bb4\u0bcd\u0bb5\u0bc1 \u0bae\u0bc1\u0ba9\u0bcd\u0ba9\u0bbf\u0bb1\u0bbf\u0bb5\u0bbf\u0baa\u0bcd\u0baa\u0bc1 \u0b85\u0bb1\u0bbf\u0b95\u0bcd\u0b95\u0bc8",
}

TAMIL_MONTHS = {
    1: "\u0b9c\u0ba9", 2: "\u0baa\u0bbf\u0baa\u0bcd", 3: "\u0bae\u0bbe\u0bb0\u0bcd", 4: "\u0b8f\u0baa\u0bcd",
    5: "\u0bae\u0bc7", 6: "\u0b9c\u0bc2\u0ba9\u0bcd", 7: "\u0b9c\u0bc2\u0bb2\u0bc8", 8: "\u0b86\u0b95",
    9: "\u0b9a\u0bc6\u0baa\u0bcd", 10: "\u0b85\u0b95\u0bcd", 11: "\u0ba8\u0bb5", 12: "\u0b9f\u0bbf\u0b9a",
}

CAT_TA = CATEGORY_TA

_PLACES_TA = {"Coimbatore": "\u0b95\u0bcb\u0baf\u0bae\u0bcd\u0baa\u0bc1\u0ba4\u0bcd\u0ba4\u0bc2\u0bb0\u0bcd"}
_NAK_HEADER_TA = {"Magha": "\u0bae\u0b95"}


def fmt_birth_line(chart) -> str:
    b = chart["birth"]
    dt_s = f"{b['day']:02d}-{b['month']:02d}-{b['year']}"
    tm_s = f"{b.get('hour', 12):02d}:{b.get('min', 0):02d}"
    place = _PLACES_TA.get(b.get("place", ""), b.get("place", ""))
    lagna_ta = f"{RASIS_TA.get(chart.get('lagna', ''), chart.get('lagna', ''))} \u0bb2\u0b95\u0bcd\u0ba9\u0bae\u0bcd"
    nak_en = chart.get("janma_nakshatra") or chart.get("positions", {}).get("Moon", {}).get("nak", "")
    nak_ta = _NAK_HEADER_TA.get(nak_en) or NAKSHATRAS_TA.get(nak_en, nak_en)
    return (
        f"\u0baa\u0bbf\u0bb1\u0baa\u0bcd\u0baa\u0bc1: {dt_s} {tm_s} \u00b7 {place} \u00b7 "
        f"{lagna_ta} \u00b7 {nak_ta} \u0ba8\u0b9f\u0bcd\u0b9a\u0ba4\u0bcd\u0ba4\u0bbf\u0bb0\u0bae\u0bcd"
    )


def fmt_win(d0, d1=None, lang="ta"):
    if not d0:
        return "\u2014"
    if lang == "ta":
        s = f"{d0.day} {TAMIL_MONTHS.get(d0.month, '?')} {d0.year}"
        if d1 and d1 != d0:
            s += f" \u2013 {d1.day} {TAMIL_MONTHS.get(d1.month, '?')} {d1.year}"
        return s
    s = d0.strftime("%Y-%m-%d")
    if d1 and d1 != d0:
        s += f" -> {d1.strftime('%Y-%m-%d')}"
    return s


def filter_bands(bands, y0, y1):
    out = []
    for b in bands:
        ws = b.get("window_start")
        if not ws:
            continue
        we = b.get("window_end") or ws
        if we.year < y0 or ws.year > y1:
            continue
        out.append(b)
    return out


def top_bands(bands, cats=None, limit=5):
    hits = bands
    if cats:
        hits = [b for b in hits if b.get("category") in cats]
    hits = sorted(
        hits,
        key=lambda x: (
            -x.get("score", 0),
            -x.get("max_sev", x.get("severity", 0)),
            x.get("window_start") or dt.datetime.min,
        ),
    )
    return hits[:limit]


def row_dict(b, lang="ta"):
    cat = b.get("category", "")
    ws, we = b.get("window_start"), b.get("window_end")
    why = b.get("max_why") or b.get("why") or []
    sev = b.get("max_sev", b.get("severity", 0))
    stars = b.get("stars", "")
    if lang == "ta":
        return {
            "category": CAT_TA.get(cat, cat),
            "window": fmt_win(ws, we, "ta"),
            "plain": ta_event(cat, b.get("event", "")),
            "cause": ta_why(why),
            "severity": sev,
            "stars": stars,
        }
    return {
        "category": cat,
        "window": fmt_win(ws, we, "en"),
        "plain": b.get("event", cat),
        "cause": " | ".join(str(x) for x in (why if isinstance(why, list) else [why])[:3]),
        "severity": sev,
        "stars": stars,
    }


def collect_data(chart, today=None):
    today = today or dt.datetime.now()
    b = chart["birth"]
    birth = dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))

    tl = build_full_timeline(chart, levels=4)
    active = lookup(tl, today)
    dasha_rows = ta_dasha_chain(active)

    y_end = today.year + 5
    raw_5y = scan_lifetime_v2(chart, today.year, y_end, sample_days=14, min_severity=2)
    bands_5y = filter_bands_for_age(chart, rank_and_consume(collapse_consecutive(raw_5y)))

    raw_decade = scan_lifetime_v2(chart, 2020, 2030, sample_days=14, min_severity=3)
    bands_decade = filter_bands_for_age(chart, rank_and_consume(collapse_consecutive(raw_decade)))

    raw_child = scan_lifetime_v2(chart, 1996, 1998, sample_days=14, min_severity=2)
    bands_child = filter_bands_for_age(chart, rank_and_consume(collapse_consecutive(raw_child)))

    by_domain = {dom: top_bands(bands_5y, cats=cats, limit=5) for dom, cats in DOMAIN_CATS.items()}

    return {
        "name": chart.get("name", "Manoj"),
        "birth": birth,
        "birth_line": fmt_birth_line(chart),
        "today": today,
        "dasha_rows": dasha_rows,
        "top15": top_bands(bands_5y, limit=15),
        "decade": top_bands(filter_bands(bands_decade, 2020, 2030), limit=12),
        "childhood": top_bands(filter_bands(bands_child, 1996, 1998), limit=8),
        "by_domain": by_domain,
    }


def write_md(data, path: Path, lang="ta", chart=None):
    name = data["name"]
    lines = []
    chart_block = ""
    if chart is not None:
        chart_block = build_jathagam_full(chart, lang, when=data["today"])
        pred_header = build_prediction_section_header(lang)
    if lang == "ta":
        lines += [
            f"# {name} - {HDR['report_title']}",
            "",
        ]
        if chart_block:
            lines.append(chart_block)
            lines.append(pred_header)
        lines += [
            f"**Generated:** {data['today'].strftime('%Y-%m-%d')} | event_predictor_v2",
            "",
            f"> {RULE_ENGINE_DISCLAIMER_TA}",
            "",
            f"## {SECTION_HEADERS['ACTIVE_DASHA']}",
            "",
            f"| {HDR['level']} | {HDR['dasha']} | {HDR['until']} | {HDR['effect']} |",
            "|---|---|---|---|",
        ]
        for r in data["dasha_rows"]:
            lines.append(f"| {r['level']} | {r['lords']} | {r['until']} | {r['effect']} |")

        sec = SECTION_HEADERS["LIFE_EVENT_WINDOWS"]
        lines += [
            "", f"## {sec} {HDR['next5']}", "",
            f"| {HDR['num']} | {HDR['domain']} | {HDR['window']} | {HDR['plain']} | {HDR['cause']} |",
            "|---:|---|---|---|---|",
        ]
        for i, b in enumerate(data["top15"], 1):
            r = row_dict(b, "ta")
            lines.append(f"| {i} | {r['category']} | {r['window']} | {r['plain']} {r['stars']} | {r['cause']} |")

        lines += [
            "", f"## {SECTION_HEADERS['DECADE_2020_2030']}", "",
            f"| {HDR['num']} | {HDR['domain']} | {HDR['window']} | {HDR['plain']} |",
            "|---:|---|---|---|",
        ]
        for i, b in enumerate(data["decade"], 1):
            r = row_dict(b, "ta")
            lines.append(f"| {i} | {r['category']} | {r['window']} | {r['plain']} |")

        lines += [
            "", f"## {SECTION_HEADERS['CHILDHOOD_WINDOWS']}", "",
            f"| {HDR['num']} | {HDR['domain']} | {HDR['window']} | {HDR['plain']} |",
            "|---:|---|---|---|",
        ]
        for i, b in enumerate(data["childhood"], 1):
            r = row_dict(b, "ta")
            lines.append(f"| {i} | {r['category']} | {r['window']} | {r['plain']} |")

        for dom, bands in data["by_domain"].items():
            title = DOMAIN_TA.get(dom, dom)
            lines += [
                "", f"### {title} {HDR['top5']}", "",
                f"| {HDR['num']} | {HDR['window']} | {HDR['plain']} | {HDR['cause']} |",
                "|---:|---|---|---|",
            ]
            for i, b in enumerate(bands, 1):
                r = row_dict(b, "ta")
                lines.append(f"| {i} | {r['window']} | {r['plain']} | {r['cause']} |")
    else:
        lines += [
            f"# {name} - Life Event Prediction Report (rule-engine windows)",
            "",
        ]
        if chart_block:
            lines.append(chart_block)
        lines += [
            f"**Generated:** {data['today'].strftime('%Y-%m-%d')}",
            "",
            "> Mechanical windows from event_predictor_v2 - not guaranteed predictions.",
            "",
            "## Active dasha (cause -> effect)",
            "",
            "| Level | Dasha | Until | Effect |",
            "|---|---|---|---|",
        ]
        for r in data["dasha_rows"]:
            lines.append(f"| {r['level']} | {r['lords']} | {r['until']} | {r['effect']} |")
        lines += ["", "## Top 15 windows - next 5 years", ""]
        for i, b in enumerate(data["top15"], 1):
            r = row_dict(b, "en")
            lines.append(f"{i}. **{r['category']}** {r['window']} - {r['plain']} ({r['cause']})")
        for dom, bands in data["by_domain"].items():
            lines += ["", f"### {dom.title()} - top 5", ""]
            for i, b in enumerate(bands, 1):
                r = row_dict(b, "en")
                lines.append(f"{i}. {r['window']} - {r['plain']}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {path}")


def write_pdf(data, path: Path, lang="ta"):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor, white
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak, HRFlowable
    from tamil_renderer import TamilParagraph, draw_tamil

    INDIGO = HexColor("#312e81")
    GOLD = HexColor("#b88a37")
    CREAM = HexColor("#fef6e4")
    GREY_LT = HexColor("#f3f0e8")
    GREY_MD = HexColor("#6b6b6b")
    TEXT = HexColor("#1f1b14")
    ACCENT = HexColor("#7e3a96")

    def TP(text, **kw):
        defaults = dict(font_size=10.5, color=TEXT, leading=1.5, space_after=3)
        defaults.update(kw)
        return TamilParagraph(text, **defaults)

    def divider():
        return HRFlowable(width="100%", thickness=0.6, color=GOLD, spaceBefore=4, spaceAfter=8)

    def table_from_rows(headers, rows, col_widths):
        hdr = [TP(h, font_size=9.5, bold=True, color=CREAM) for h in headers]
        body = [[TP(str(c), font_size=9, color=TEXT) for c in row] for row in rows]
        t = Table([hdr] + body, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, GREY_LT]),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, 0), (-1, 0), 1, GOLD),
        ]))
        return t

    flow = []
    name = data["name"]
    if lang == "ta":
        flow.append(TP(name.upper(), font_size=22, bold=True, color=INDIGO, align="center"))
        flow.append(TP(SECTION_HEADERS["LIFE_EVENT_WINDOWS"], font_size=14, color=GREY_MD, align="center", space_after=10))
        flow.append(divider())
        flow.append(TP(data["birth_line"], font_size=10, color=TEXT))
        flow.append(TP(RULE_ENGINE_DISCLAIMER_TA, font_size=9, color=ACCENT, space_after=8))
        flow.append(Spacer(1, 0.2 * cm))

        flow.append(TP(SECTION_HEADERS["ACTIVE_DASHA"], font_size=14, bold=True, color=INDIGO))
        flow.append(table_from_rows(
            [HDR["level"], HDR["dasha"], HDR["until"], HDR["effect"]],
            [[r["level"], r["lords"], r["until"], r["effect"]] for r in data["dasha_rows"]],
            [3.2 * cm, 4.5 * cm, 2.8 * cm, 5 * cm],
        ))
        flow.append(PageBreak())

        flow.append(TP(f"{SECTION_HEADERS['LIFE_EVENT_WINDOWS']}{HDR['next5']}", font_size=14, bold=True, color=INDIGO))
        rows15 = []
        for i, b in enumerate(data["top15"], 1):
            r = row_dict(b, "ta")
            rows15.append([str(i), r["category"], r["window"], f"{r['plain']} {r['stars']}", r["cause"][:80]])
        flow.append(table_from_rows(
            [HDR["num"], HDR["domain"], HDR["window"], HDR["plain"], HDR["cause"]],
            rows15, [0.8 * cm, 2.2 * cm, 3.5 * cm, 4.5 * cm, 4.5 * cm],
        ))
        flow.append(Spacer(1, 0.4 * cm))

        flow.append(TP(SECTION_HEADERS["DECADE_2020_2030"], font_size=13, bold=True, color=ACCENT))
        dec_rows = [[str(i), row_dict(b, "ta")["category"], row_dict(b, "ta")["window"], row_dict(b, "ta")["plain"]]
                    for i, b in enumerate(data["decade"], 1)]
        flow.append(table_from_rows(
            [HDR["num"], HDR["domain"], HDR["window"], HDR["plain"]],
            dec_rows, [0.8 * cm, 2.5 * cm, 4 * cm, 8.2 * cm],
        ))

        flow.append(Spacer(1, 0.3 * cm))
        flow.append(TP(SECTION_HEADERS["CHILDHOOD_WINDOWS"], font_size=13, bold=True, color=ACCENT))
        ch_rows = [[str(i), row_dict(b, "ta")["category"], row_dict(b, "ta")["window"], row_dict(b, "ta")["plain"]]
                   for i, b in enumerate(data["childhood"], 1)]
        flow.append(table_from_rows(
            [HDR["num"], HDR["domain"], HDR["window"], HDR["plain"]],
            ch_rows, [0.8 * cm, 2.5 * cm, 4 * cm, 8.2 * cm],
        ))
        flow.append(PageBreak())

        flow.append(TP(SECTION_HEADERS["DOMAIN_PREDICTIONS"], font_size=14, bold=True, color=INDIGO))
        for dom, bands in data["by_domain"].items():
            flow.append(Spacer(1, 0.25 * cm))
            flow.append(TP(DOMAIN_TA.get(dom, dom), font_size=12, bold=True, color=ACCENT))
            drows = [[str(i), row_dict(b, "ta")["window"], row_dict(b, "ta")["plain"], row_dict(b, "ta")["cause"][:70]]
                     for i, b in enumerate(bands, 1)]
            if drows:
                flow.append(table_from_rows(
                    [HDR["num"], HDR["window"], HDR["plain"], HDR["cause"]],
                    drows, [0.8 * cm, 3.5 * cm, 5 * cm, 6.2 * cm],
                ))
            else:
                flow.append(TP(HDR["no_domain"], font_size=9, color=GREY_MD))
    else:
        flow.append(TP(f"{name} - Rule-Engine Life Windows", font_size=18, bold=True, color=INDIGO, align="center"))
        flow.append(TP("Not guaranteed - event_predictor_v2 mechanical bands", font_size=10, color=GREY_MD, align="center"))
        for i, b in enumerate(data["top15"], 1):
            r = row_dict(b, "en")
            flow.append(TP(f"{i}. [{r['category']}] {r['window']} - {r['plain']}", font_size=10))

    def footer(canvas, doc):
        canvas.saveState()
        draw_tamil(canvas, f"{HDR['page']} {doc.page}", A4[0] / 2 - 30, 0.8 * cm, font_size=9, color=GREY_MD)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GREY_MD)
        canvas.drawRightString(A4[0] - 1.5 * cm, 0.8 * cm, "Atro Vedic Engine | rule-engine windows")
        canvas.restoreState()

    path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(path), pagesize=A4, leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=1.6 * cm, bottomMargin=2 * cm, title=f"{name} predictions",
    )
    doc.build(flow, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {path} ({path.stat().st_size // 1024} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", default=str(CHART_PATH))
    ap.add_argument("--en", action="store_true", help="Also write EN md/pdf")
    args = ap.parse_args()

    chart = json.loads(Path(args.chart).read_text(encoding="utf-8"))
    data = collect_data(chart)
    write_md(data, OUT_MD_TA, "ta", chart=chart)
    write_pdf(data, OUT_PDF_TA, "ta")
    if args.en:
        write_md(data, OUT_MD_EN, "en", chart=chart)
        write_pdf(data, OUT_PDF_EN, "en")


if __name__ == "__main__":
    main()
