# -*- coding: utf-8 -*-
"""Central age gates for life-event categories (timeline + predictor sanity).

Philosophy: predict what the chart + dasha says at that age - do not silently
hide astrologically strong early/late signals. Typical bands label normal ages;
early/late exceptions surface rare but chart-valid windows with client labels.
Hard drops only for absurd ages (e.g. marriage at 4).
"""
from __future__ import annotations

import datetime as dt
import fnmatch
import re
from typing import Any, Literal

AgeFit = Literal["typical", "early_exception", "late_exception", "unlikely"]

# First matching pattern wins. fnmatch globs (* suffix) supported.
# typical_* = most natives; absurd_* = hard drop outside; early_allow_age = always
# show as early_exception when below typical_min (e.g. marriage at 16).
CATEGORY_AGE_RULES: list[dict[str, Any]] = [
    {
        "pattern": "marriage*",
        "typical_min": 18, "typical_max": 45,
        "absurd_min": 12, "absurd_max": 85,
        "early_allow_age": 16,
        "notes": "typical 18-45; early 16+ or sev>=4 from 12",
    },
    {
        "pattern": "engagement*",
        "typical_min": 18, "typical_max": 45,
        "absurd_min": 12, "absurd_max": 85,
        "early_allow_age": 16,
        "notes": "",
    },
    {
        "pattern": "relationship_phase",
        "typical_min": 18, "typical_max": 45,
        "absurd_min": 12, "absurd_max": 85,
        "early_allow_age": 16,
        "notes": "post-rank marriage rename",
    },
    {
        "pattern": "*affair*",
        "typical_min": 18, "typical_max": 45,
        "absurd_min": 12, "absurd_max": 85,
        "early_allow_age": 16,
        "notes": "romance / extramarital",
    },
    {
        "pattern": "romance",
        "typical_min": 18, "typical_max": 45,
        "absurd_min": 12, "absurd_max": 85,
        "early_allow_age": 16,
        "notes": "",
    },
    {
        "pattern": "first_love",
        "typical_min": 14, "typical_max": 28,
        "absurd_min": 10, "absurd_max": 35,
        "early_allow_age": 12,
        "notes": "adolescent crush, not marriage",
    },
    {
        "pattern": "children*",
        "typical_min": 18, "typical_max": 45,
        "absurd_min": 10, "absurd_max": 55,
        "early_allow_age": 16,
        "notes": "",
    },
    {
        "pattern": "pregnancy",
        "typical_min": 18, "typical_max": 45,
        "absurd_min": 10, "absurd_max": 55,
        "early_allow_age": 16,
        "notes": "",
    },
    {
        "pattern": "grandchild*",
        "typical_min": 35, "typical_max": 70,
        "absurd_min": 30, "absurd_max": 99,
        "early_allow_age": 32,
        "notes": "",
    },
    {
        "pattern": "career*",
        "typical_min": 14, "typical_max": 65,
        "absurd_min": 8, "absurd_max": 75,
        "early_allow_age": 10,
        "notes": "child-actor debuts optional in predictor",
    },
    {
        "pattern": "job",
        "typical_min": 14, "typical_max": 65,
        "absurd_min": 8, "absurd_max": 75,
        "early_allow_age": 10,
        "notes": "",
    },
    {
        "pattern": "promotion",
        "typical_min": 14, "typical_max": 65,
        "absurd_min": 8, "absurd_max": 75,
        "early_allow_age": 10,
        "notes": "",
    },
    {
        "pattern": "business*",
        "typical_min": 14, "typical_max": 65,
        "absurd_min": 8, "absurd_max": 75,
        "early_allow_age": 10,
        "notes": "",
    },
    {
        "pattern": "fame*",
        "typical_min": 14, "typical_max": 65,
        "absurd_min": 8, "absurd_max": 75,
        "early_allow_age": 10,
        "notes": "",
    },
    {
        "pattern": "honor",
        "typical_min": 14, "typical_max": 65,
        "absurd_min": 8, "absurd_max": 75,
        "early_allow_age": 10,
        "notes": "awards / public recognition",
    },
    {
        "pattern": "leadership_emergence",
        "typical_min": 14, "typical_max": 65,
        "absurd_min": 8, "absurd_max": 75,
        "early_allow_age": 10,
        "notes": "",
    },
    {
        "pattern": "political_office",
        "typical_min": 21, "typical_max": 75,
        "absurd_min": 18, "absurd_max": 80,
        "early_allow_age": 19,
        "notes": "",
    },
    {
        "pattern": "lottery*",
        "typical_min": 18, "typical_max": 65,
        "absurd_min": 16, "absurd_max": 75,
        "early_allow_age": 17,
        "notes": "",
    },
    {
        "pattern": "speculation*",
        "typical_min": 18, "typical_max": 65,
        "absurd_min": 16, "absurd_max": 75,
        "early_allow_age": 17,
        "notes": "",
    },
    {
        "pattern": "father*",
        "typical_min": 0, "typical_max": 99,
        "absurd_min": 0, "absurd_max": 99,
        "early_allow_age": 0,
        "notes": "ok in childhood",
    },
    {
        "pattern": "mother*",
        "typical_min": 0, "typical_max": 99,
        "absurd_min": 0, "absurd_max": 99,
        "early_allow_age": 0,
        "notes": "ok in childhood",
    },
    {
        "pattern": "education*",
        "typical_min": 3, "typical_max": 35,
        "absurd_min": 3, "absurd_max": 40,
        "early_allow_age": 3,
        "notes": "",
    },
    {
        "pattern": "property*",
        "typical_min": 18, "typical_max": 99,
        "absurd_min": 16, "absurd_max": 99,
        "early_allow_age": 17,
        "notes": "",
    },
    {
        "pattern": "vehicle",
        "typical_min": 18, "typical_max": 99,
        "absurd_min": 16, "absurd_max": 99,
        "early_allow_age": 17,
        "notes": "",
    },
    {
        "pattern": "retirement",
        "typical_min": 45, "typical_max": 70,
        "absurd_min": 25, "absurd_max": 90,
        "early_allow_age": 40,
        "notes": "",
    },
]

# Category keyword hints for known_events text matching.
_CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "marriage": ("marriage", "married", "wed", "wedding", "kalatra"),
    "engagement": ("engagement", "engaged", "betrothal"),
    "relationship_phase": ("relationship", "partner", "love"),
    "children": ("child", "born", "birth", "son", "daughter", "pregnancy"),
    "pregnancy": ("pregnant", "pregnancy", "expecting"),
    "career": ("debut", "career", "job", "appointed", "promoted", "captain"),
    "retirement": ("retire", "retirement"),
    "father": ("father", "dad", "paternal"),
    "mother": ("mother", "mom", "maternal"),
    "education": ("school", "college", "degree", "graduat", "exam"),
}


def _birth_dt(chart: dict) -> dt.datetime:
    b = chart["birth"]
    return dt.datetime(b["year"], b["month"], b["day"], b.get("hour", 12), b.get("min", 0))


def age_at(chart: dict, when: dt.datetime) -> float:
    """Age in years at `when` from chart birth."""
    return (when - _birth_dt(chart)).days / 365.25


def get_age_rules(category: str) -> dict[str, Any] | None:
    cat = (category or "").lower()
    for rule in CATEGORY_AGE_RULES:
        if fnmatch.fnmatch(cat, rule["pattern"].lower()):
            return rule
    return None


def _strong_signal(severity: float, why_count: int) -> bool:
    """Severity 4-5 or multiple why-lines at sev 3+."""
    sev = int(severity or 0)
    return sev >= 4 or (sev >= 3 and why_count >= 2)


def _parse_known_date(raw: str) -> dt.datetime | None:
    raw = (raw or "").strip()
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return dt.datetime.strptime(raw[:10], fmt)
        except ValueError:
            continue
    return None


def _category_from_known_event(text: str) -> str | None:
    low = (text or "").lower()
    for cat, kws in _CATEGORY_KEYWORDS.items():
        if any(kw in low for kw in kws):
            return cat
    return None


def _categories_match(band_category: str, known_category: str | None) -> bool:
    if not known_category:
        return False
    bc = (band_category or "").lower()
    kc = known_category.lower()
    if bc == kc or bc.startswith(kc) or kc.startswith(bc):
        return True
    if fnmatch.fnmatch(bc, f"{kc}*") or fnmatch.fnmatch(kc, f"{bc}*"):
        return True
    # marriage band vs engagement known event, etc.
    romance = {"marriage", "engagement", "relationship_phase", "romance"}
    if bc in romance and kc in romance:
        return True
    return False


def known_event_at_age(chart: dict, category: str, age: float, tolerance_years: float = 1.5) -> bool:
    """True when chart JSON documents this category near `age` (known_events always win)."""
    for ke in chart.get("known_events") or []:
        when = _parse_known_date(ke.get("date", ""))
        if when is None:
            continue
        ke_cat = _category_from_known_event(ke.get("event", ""))
        if not _categories_match(category, ke_cat):
            continue
        ke_age = age_at(chart, when)
        if abs(ke_age - age) <= tolerance_years:
            return True
    return False


def classify_age_fit(
    age: float,
    category: str,
    severity: float = 0,
    *,
    why_count: int = 0,
    chart: dict | None = None,
) -> AgeFit:
    """Classify how well `age` fits `category` given signal strength.

    Returns:
        typical - inside typical_min..typical_max
        early_exception - below typical but chart-strong or early_allow_age
        late_exception - above typical but chart-strong or mildly late
        unlikely - absurd age or weak signal outside typical band
    """
    if chart and known_event_at_age(chart, category, age):
        return "typical"

    rule = get_age_rules(category)
    if rule is None:
        return "typical"

    absurd_min = rule["absurd_min"]
    absurd_max = rule["absurd_max"]
    typical_min = rule["typical_min"]
    typical_max = rule["typical_max"]
    early_allow = rule.get("early_allow_age", typical_min)

    if age < absurd_min or age > absurd_max:
        return "unlikely"

    if typical_min <= age <= typical_max:
        return "typical"

    if age < typical_min:
        if age >= early_allow:
            return "early_exception"
        if _strong_signal(severity, why_count):
            return "early_exception"
        return "unlikely"

    # age > typical_max
    if _strong_signal(severity, why_count):
        return "late_exception"
    if age <= typical_max + 15:
        return "late_exception"
    return "unlikely"


def _band_severity(band: dict) -> float:
    return float(band.get("max_sev") or band.get("severity") or 0)


def _band_why_count(band: dict) -> int:
    why = band.get("why") or band.get("why_lines") or []
    if isinstance(why, list):
        return len(why)
    if isinstance(why, str) and why.strip():
        return len(re.split(r"[;\n|]", why))
    return 0


def _band_reference_age(chart: dict, band: dict) -> float:
    ws = band.get("window_start")
    if ws:
        return age_at(chart, ws)
    return 0.0


def annotate_band_age_fit(chart: dict, band: dict) -> AgeFit:
    """Compute and set band['age_fit'] + band['age_at_start']."""
    cat = band.get("category", "")
    ref_age = _band_reference_age(chart, band)
    fit = classify_age_fit(
        ref_age,
        cat,
        _band_severity(band),
        why_count=_band_why_count(band),
        chart=chart,
    )
    band["age_at_start"] = round(ref_age, 1)
    band["age_fit"] = fit
    return fit


def is_age_appropriate(category: str, age: float, severity: float = 0) -> bool:
    """Backward-compatible: True when age is not absurd/weak-outside-typical."""
    return classify_age_fit(age, category, severity) != "unlikely"


def filter_bands_for_age(chart: dict, bands: list[dict]) -> list[dict]:
    """Annotate bands with age_fit; drop only 'unlikely' (absurd or weak early/late)."""
    out: list[dict] = []
    for band in bands:
        fit = annotate_band_age_fit(chart, band)
        if fit != "unlikely":
            out.append(band)
    return out


def band_fits_puthi_window(
    chart: dict,
    band: dict,
    puthi_start: dt.datetime,
    puthi_end: dt.datetime,
) -> bool:
    """Puthi gate: overlapping portion must not be 'unlikely' for client display."""
    ws = band.get("window_start")
    if not ws:
        return True
    we = band.get("window_end") or ws
    overlap_start = max(puthi_start, ws)
    overlap_end = min(puthi_end, we)
    if overlap_start > overlap_end:
        return False

    ref_age = age_at(chart, overlap_start)
    fit = band.get("age_fit")
    if fit is None:
        fit = classify_age_fit(
            ref_age,
            band.get("category", ""),
            _band_severity(band),
            why_count=_band_why_count(band),
            chart=chart,
        )
    return fit != "unlikely"


def client_age_label(band: dict, lang: str = "en") -> str | None:
    """Prefix for client-facing event text; None for typical (no prefix)."""
    fit = band.get("age_fit", "typical")
    age = band.get("age_at_start")
    if age is None:
        age_s = "?"
    elif age == int(age):
        age_s = int(age)
    else:
        age_s = age
    if fit == "early_exception":
        if lang == "ta":
            return f"\u26a0 \u0b86\u0b95\u0b95\u0bcd\u0b95\u0bbe\u0b95\u0bcd\u0b95\u0bae\u0bcd (\u0bb5\u0baf\u0ba4\u0bc1 {age_s}) \u2014 \u0bb5\u0bb2\u0bc1\u0bae\u0bbe\u0ba9 \u0b9a\u0bc1\u0bb1\u0bc1\u0b95\u0bcd\u0b95\u0bc1: "
        return f"\u26a0 Early (age {age_s}) \u2014 strong signal: "
    if fit == "late_exception":
        if lang == "ta":
            return f"\u26a0 \u0b87\u0bb1\u0bc1\u0b95\u0bcd\u0b95\u0bc8\u0baf \u0bb5\u0baf\u0ba4\u0bc1 ({age_s}) \u2014 \u0bb5\u0bb2\u0bc1\u0bae\u0bbe\u0ba9 \u0b9a\u0bc1\u0bb1\u0bc1\u0b95\u0bcd\u0b95\u0bc1: "
        return f"\u26a0 Late (age {age_s}) \u2014 strong signal: "
    return None
