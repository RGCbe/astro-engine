"""Apply canonical birth sync (known_charts <- charts) and event date fixes."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS = ROOT / "charts"
KNOWN = ROOT / "engine" / "known_charts.py"

NAME_TO_SLUG = {
    "Mahatma Gandhi": "mahatma_gandhi",
    "Indira Gandhi": "indira_gandhi",
    "Narendra Modi": "narendra_modi",
    "Sachin Tendulkar": "sachin_tendulkar",
    "Lata Mangeshkar": "lata_mangeshkar",
    "Shah Rukh Khan": "shah_rukh_khan",
    "Mukesh Ambani": "mukesh_ambani",
    "Amitabh Bachchan": "amitabh_bachchan",
    "A R Rahman": "ar_rahman",
    "Aishwarya Rai": "aishwarya_rai",
    "Stephen Hawking": "stephen_hawking",
    "Steve Jobs": "steve_jobs",
}

EVENT_FIXES: dict[str, list[tuple[str, str, dict | None]]] = {
    # slug -> [(old_date, new_date, optional extra fields)]
    "sachin_tendulkar": [
        ("1989-11-15", "1989-11-16", None),
    ],
    "ar_rahman": [
        ("1976-01-01", "1976-09-30", None),
        ("1989-01-01", "1989-01-01", {"date_precision": "year"}),
        ("1992-01-01", "1992-08-15", None),
        ("1993-01-01", "1993-05-04", None),
        ("1997-01-01", "1997-08-12", None),
        ("2010-01-01", "2010-01-31", None),
    ],
    "rekha": [
        ("1980-01-01", "1981-07-01", None),
        ("1982-01-01", "1982-04-15", None),
        ("1988-01-01", "1989-03-15", None),
    ],
    "amitabh_bachchan": [
        ("1997-01-01", "1999-07-09", None),
    ],
    "aishwarya_rai": [
        ("2018-01-01", "2017-03-18", None),
    ],
    "virat_kohli": [
        ("2018-01-01", "2017-03-30", None),
    ],
}


def chart_birth_to_known(slug: str) -> dict:
    c = json.loads((CHARTS / f"{slug}_chart.json").read_text(encoding="utf-8"))
    b = c["birth"]
    return {
        "date": f"{b['year']}-{b['month']:02d}-{b['day']:02d}",
        "time": f"{b['hour']:02d}:{b['min']:02d}",
        "tz": b["tz"],
        "place": b.get("place", ""),
        "lat": b["lat"],
        "lon": b["lon"],
    }


def patch_chart_events(slug: str) -> int:
    path = CHARTS / f"{slug}_chart.json"
    chart = json.loads(path.read_text(encoding="utf-8"))
    fixes = EVENT_FIXES.get(slug, [])
    if not fixes:
        return 0
    fix_map = {old: (new, extra) for old, new, extra in fixes}
    n = 0
    for ev in chart.get("known_events", []):
        old = ev.get("date")
        if old in fix_map:
            new, extra = fix_map[old]
            ev["date"] = new
            if extra:
                ev.update(extra)
            if slug == "virat_kohli" and new == "2017-03-30":
                ev["event"] = "Awarded Padma Shri at Rashtrapati Bhavan investiture ceremony"
            n += 1
    path.write_text(json.dumps(chart, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return n


def sync_known_charts_py() -> int:
    text = KNOWN.read_text(encoding="utf-8")
    updated = 0
    for name, slug in NAME_TO_SLUG.items():
        bd = chart_birth_to_known(slug)
        pattern = (
            rf'(name="{re.escape(name)}",\s*birthdata=\{{)'
            rf'"date": "[^"]+", "time": "[^"]+", "tz": [^,]+,\s*'
            rf'"place": "[^"]*", "lat": [^,]+, "lon": [^,]+'
            rf'(\}})'
        )
        repl = (
            rf'\1"date": "{bd["date"]}", "time": "{bd["time"]}", "tz": {bd["tz"]}, '
            rf'"place": "{bd["place"]}", "lat": {bd["lat"]}, "lon": {bd["lon"]}\2'
        )
        new_text, n = re.subn(pattern, repl, text, count=1)
        if n:
            text = new_text
            updated += 1
        else:
            print(f"WARN: no known_charts birthdata match for {name}")
    KNOWN.write_text(text, encoding="utf-8")
    return updated


def main():
    ev_total = sum(patch_chart_events(slug) for slug in EVENT_FIXES)
    kc = sync_known_charts_py()
    print(f"Patched {ev_total} placeholder events across charts")
    print(f"Synced {kc} known_charts birthdata blocks from charts/*.json")


if __name__ == "__main__":
    main()
