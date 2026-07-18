#!/usr/bin/env python3
"""
Astro engine CLI — produce a full Vedic chart + reading from birth data.

Usage:
    python -m engine.cli --name "Manoj Kumar T" --date 1996-05-25 \\
        --time 20:25 --place "Coimbatore" --tz 5.5

    python -m engine.cli --name X --date YYYY-MM-DD --time HH:MM \\
        --lat 11.25 --lon 77.117 --tz 5.5

    python -m engine.cli --name X --date Y --time Z --place P --json
        # JSON output instead of Markdown
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, "/opt/astro")

from engine.chart import compute_chart
from engine.reading import generate_reading
from engine.panchanga import panchanga
from engine.i18n import (
    LANGUAGES, translate, localize_chart, GRAHAS, SIGNS, NAKSHATRAS, VARAS,
)


def _localize_reading_md(md: str, lang: str) -> str:
    """Token-replace English chart-field words in markdown with localized ones.
    Conservative: only replaces words found in the i18n tables (full word match)."""
    import re
    en_signs = SIGNS["en"]
    en_naks = NAKSHATRAS["en"]
    en_varas = VARAS["en"]
    en_grahas = list(GRAHAS["en"].keys())

    pairs = []
    for w in en_signs:
        pairs.append((w, translate("sign", w, lang)))
    for w in en_naks:
        pairs.append((w, translate("nakshatra", w, lang)))
    for w in en_varas:
        pairs.append((w, translate("vara", w, lang)))
    for w in en_grahas:
        pairs.append((w, translate("graha", w, lang)))
    # Verdict labels too — preserve truth directive
    for w in ("HIGH", "MEDIUM", "LOW", "WEAK", "REJECTED",
              "STRONG YES", "YES", "WEAK YES", "NO", "INDETERMINATE"):
        pairs.append((w, translate("verdict", w, lang)))

    # Sort longest first to avoid prefix collisions
    pairs.sort(key=lambda p: -len(p[0]))
    for src, tgt in pairs:
        if src == tgt or not tgt:
            continue
        md = re.sub(rf"\b{re.escape(src)}\b", tgt, md)
    return md


def main():
    ap = argparse.ArgumentParser(
        description="Compute a full Vedic jadhagam + cited reading.",
    )
    ap.add_argument("--name", default="(unnamed)")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--time", required=True, help="HH:MM (24h, local)")
    ap.add_argument("--tz", type=float, default=5.5,
                    help="Timezone offset hours (default 5.5 = IST)")
    ap.add_argument("--place")
    ap.add_argument("--lat", type=float)
    ap.add_argument("--lon", type=float)
    ap.add_argument("--json", action="store_true",
                    help="Output JSON instead of Markdown")
    ap.add_argument("--save", metavar="DIR",
                    help="Write chart + reading to files in DIR")
    ap.add_argument("--lang", choices=LANGUAGES, default="en",
                    help="Output language: en | sa (Sanskrit IAST) | "
                         "hi (Hindi Devanagari) | ta (Tamil)")
    ap.add_argument("--mode", choices=("reading", "timeline", "narrative", "ask"),
                    default="reading",
                    help="reading=v1.5 narrative, timeline=Vimshottari table, "
                         "narrative=full life report, ask=Q&A")
    ap.add_argument("--question", help="Used with --mode=ask")
    args = ap.parse_args()

    if not args.place and (args.lat is None or args.lon is None):
        ap.error("Provide --place OR (--lat AND --lon)")

    # Compute chart
    chart = compute_chart(
        name=args.name,
        date=args.date, time=args.time, tz_hours=args.tz,
        place=args.place, lat=args.lat, lon=args.lon,
    )

    # Compute panchanga at birth
    birth_dt = dt.datetime.strptime(f"{args.date} {args.time}", "%Y-%m-%d %H:%M")
    p = panchanga(birth_dt, chart.lat, chart.lon, args.tz)

    # Mode dispatch — alternate outputs from the same chart
    if args.mode == "timeline":
        from engine.life_narrative import timeline_table
        print(timeline_table(chart))
        return
    if args.mode == "narrative":
        from engine.life_narrative import full_narrative
        print(full_narrative(chart))
        return
    if args.mode == "ask":
        if not args.question:
            ap.error("--mode=ask requires --question")
        from engine.life_narrative import ask
        a = ask(chart, args.question)
        print(f"Q: {a.question}\n→ {a.summary}")
        for w in a.windows:
            print(f"   • {w.period_start} → {w.period_end}  {w.md_ad}  [{w.quality}]  {w.headline}")
        return

    # Generate reading
    reading = generate_reading(chart)

    # Build summary
    summary = chart.summary()
    summary["panchanga"] = {
        "tithi": p.tithi, "paksha": p.paksha,
        "nakshatra": p.nakshatra, "nakshatra_pada": p.nakshatra_pada,
        "yoga": p.yoga, "karana": p.karana, "vara": p.vara,
        "vara_lord": p.vara_lord,
        "sunrise": p.sunrise.isoformat() if p.sunrise else None,
        "sunset": p.sunset.isoformat() if p.sunset else None,
    }
    reading_md = reading.to_markdown()

    # Apply locale to summary if --lang != en
    if args.lang != "en":
        summary = localize_chart(summary, args.lang)
        # Translate the chart-fact lines used in the prose summary
        reading_md = _localize_reading_md(reading_md, args.lang)

    if args.json:
        print(json.dumps(
            {"chart": summary, "reading_markdown": reading_md},
            indent=2, default=str,
        ))
    else:
        L = args.lang
        def t_sign(v): return translate("sign", v, L)
        def t_nak(v):  return translate("nakshatra", v, L)
        def t_grh(v):  return translate("graha", v, L)
        def t_var(v):  return translate("vara", v, L)
        def t_tit(v):  return translate("tithi", v, L)

        print("=" * 70)
        print(f"  {chart.name or '(unnamed)'} — Vedic Jadhagam")
        print("=" * 70)
        print(f"\nBirth:  {chart.birth_dt}  ({chart.place})")
        print(f"Coords: {chart.lat:.4f}°, {chart.lon:.4f}° ({args.tz:+.1f}h)")
        print(f"Ayanamsa (Lahiri): {chart.ayanamsa:.4f}°\n")

        print(f"Lagna:  {t_sign(chart.lagna_sign)} {chart.lagna_lon:.2f}° "
              f"({t_nak(chart.lagna_nakshatra)})")
        print(f"Lagna lord: {t_grh(chart.lagna_lord)}")
        print(f"Moon (Janma rasi): {t_sign(chart.nakshatras['Moon']['sign'])}")
        print(f"Janma nakshatra: {t_nak(p.nakshatra)} pada {p.nakshatra_pada}\n")

        print("Panchanga at birth:")
        print(f"  Tithi:     {t_tit(p.tithi)} ({p.paksha} paksha)")
        print(f"  Yoga:      {p.yoga}")
        print(f"  Karana:    {p.karana}")
        print(f"  Vara:      {t_var(p.vara)} ({t_grh(p.vara_lord)} hora-day)\n")

        print(f"Currently running:  {t_grh(chart.current_md)} mahadasha "
              f"(ends {chart.current_md_end})  /  {t_grh(chart.current_ad)} antardasha\n")

        if chart.yogas:
            print("Auto-detected yogas:")
            for y in chart.yogas:
                mark = "⭐" if y.is_strong else "⚠️"
                print(f"  {mark} {y.name}")
            print()

        print(reading_md)

    if args.save:
        out = Path(args.save).expanduser()
        out.mkdir(parents=True, exist_ok=True)
        slug = (args.name or "chart").replace(" ", "_")
        json.dump(summary, open(out / f"{slug}_chart.json", "w"),
                  indent=2, default=str)
        (out / f"{slug}_reading.md").write_text(reading_md, encoding="utf-8")
        print(f"\n✅ Saved chart to {out}/{slug}_chart.json", file=sys.stderr)
        print(f"✅ Saved reading to {out}/{slug}_reading.md", file=sys.stderr)


if __name__ == "__main__":
    main()
