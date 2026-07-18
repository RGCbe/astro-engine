"""Dated report output paths under reports/<mon yyyy>/<YYYY-MM-DD>/report/."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

_MONTHS = (
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec",
)


def month_folder(when: dt.date) -> str:
    """Return folder name like ``jun 2026`` (lowercase month, space, year)."""
    return f"{_MONTHS[when.month - 1]} {when.year}"


def dated_report_dir(base: Path | None = None, when: dt.date | None = None) -> Path:
    """Return ``reports/<mon yyyy>/<YYYY-MM-DD>/report`` (creates parents)."""
    if base is None:
        base = Path(__file__).resolve().parent.parent / "reports"
    if when is None:
        when = dt.date.today()
    out = base / month_folder(when) / when.isoformat() / "report"
    out.mkdir(parents=True, exist_ok=True)
    return out


def category_report_dir(
    category: str,
    base: Path | None = None,
    when: dt.date | None = None,
) -> Path:
    """Return ``.../report/<category>/`` (creates parents)."""
    out = dated_report_dir(base, when) / category
    out.mkdir(parents=True, exist_ok=True)
    return out
