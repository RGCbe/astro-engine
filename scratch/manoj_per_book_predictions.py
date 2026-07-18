#!/usr/bin/env python3
"""Generate per-book Part 2 report for Manoj (selected topics)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.per_book_predictions import (
    DEFAULT_SELECTED_BOOKS,
    build_per_book_report,
    build_per_book_table_report,
    list_all_prediction_books,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chart", default=str(ROOT / "charts" / "manoj_chart.json"))
    ap.add_argument("--lang", choices=("en", "ta"), default="en")
    ap.add_argument("--all-books", action="store_true", help="Use every corpus book")
    ap.add_argument(
        "--format",
        choices=("table", "detail", "both", "table_first"),
        default="both",
        help="table=tables only; both=tables+citations; detail=prose only",
    )
    ap.add_argument("-o", "--out", default="")
    args = ap.parse_args()

    chart_path = Path(args.chart)
    chart = json.loads(chart_path.read_text(encoding="utf-8"))
    books = list_all_prediction_books() if args.all_books else DEFAULT_SELECTED_BOOKS

    base_dir = ROOT / "reports" / "jun 2026" / "2026-06-02" / "report" / "manoj"

    if args.format == "table":
        report = build_per_book_table_report(chart, books=books, lang=args.lang)
        default_name = "MANOJ_PER_BOOK_PREDICTIONS_TABLE.md"
    else:
        report = build_per_book_report(
            chart, books=books, lang=args.lang, layout=args.format
        )
        default_name = "MANOJ_PER_BOOK_PREDICTIONS_EN.md"

    out = Path(args.out) if args.out else base_dir / default_name
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"Wrote {out} ({len(report):,} chars, {len(books)} books, format={args.format})")

    if args.format == "both" and not args.out:
        table_path = base_dir / "MANOJ_PER_BOOK_PREDICTIONS_TABLE.md"
        table_report = build_per_book_table_report(chart, books=books, lang=args.lang)
        table_path.write_text(table_report, encoding="utf-8")
        print(f"Wrote {table_path} ({len(table_report):,} chars)")


if __name__ == "__main__":
    main()
