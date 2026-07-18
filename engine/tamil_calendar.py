# -*- coding: utf-8 -*-
"""Tamil solar calendar labels for jathagam page 1."""
from __future__ import annotations

import datetime as dt

TAMIL_YEAR_AT_PUTHANDU = {1996: "\u0ba4\u0bbe\u0ba4\u0bc1", 1997: "\u0ba4\u0bbe\u0ba4\u0bc1"}

TAMIL_MONTHS = [
    "\u0b9a\u0bbf\u0ba4\u0bcd\u0ba4\u0bbf\u0bb0\u0bc8",
    "\u0bb5\u0bc8\u0b95\u0bbe\u0b9a\u0bbf",
    "\u0b86\u0ba9\u0bbf",
    "\u0b86\u0b9f\u0bbf",
    "\u0b86\u0bb5\u0ba3\u0bbf",
    "\u0baa\u0bc1\u0bb0\u0b9f\u0bcd\u0b9f\u0bbe\u0b9a\u0bbf",
    "\u0b90\u0baa\u0bcd\u0baa\u0b9a\u0bbf",
    "\u0b95\u0bbe\u0bb0\u0bcd\u0ba4\u0bcd\u0ba4\u0bbf\u0b95\u0bc8",
    "\u0bae\u0bbe\u0bb0\u0bcd\u0b95\u0bb4\u0bbf",
    "\u0ba4\u0bc8",
    "\u0bae\u0bbe\u0b9a\u0bbf",
    "\u0baa\u0b99\u0bcd\u0b95\u0bc1\u0ba9\u0bbf",
]

PUTHANDU_DAY = (4, 14)


def _puthandu_start(d: dt.date) -> dt.date:
    y = d.year
    p = dt.date(y, PUTHANDU_DAY[0], PUTHANDU_DAY[1])
    if d < p:
        p = dt.date(y - 1, PUTHANDU_DAY[0], PUTHANDU_DAY[1])
    return p


def tamil_solar_date(d: dt.date) -> dict[str, str | int]:
    p = _puthandu_start(d)
    days = (d - p).days
    month_idx = min(max(days // 30, 0), 11)
    day_in_month = (days % 30) + 1
    ty = TAMIL_YEAR_AT_PUTHANDU.get(p.year, str(p.year))
    month = TAMIL_MONTHS[month_idx]
    return {
        "year_name": ty,
        "month_name": month,
        "day": day_in_month,
        "label_ta": f"{ty} \u0bb5\u0bb0\u0bc1\u0b9f\u0bae\u0bcd {month} \u0bae\u0bbe\u0ba4\u0bae\u0bcd {day_in_month} \u0b86\u0bae\u0bcd \u0ba4\u0bc7\u0ba4\u0bbf",
        "label_en": f"{ty} year, {month} month, day {day_in_month}",
    }
