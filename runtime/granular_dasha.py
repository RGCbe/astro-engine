"""Granular Vimshottari Dasha — 4 levels deep (MD/AD/PD/SD).

Builds a complete date-indexed timeline of every sub-period from birth to ~120 years.
Used by event_predictor to map any date in life to its active dasha lords.
"""
import datetime as dt
from pathlib import Path

VIMSHOTTARI_YEARS = {"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
VIMSHOTTARI_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
NAK_LORDS_27 = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"] * 3


def _next_lord(lord):
    return VIMSHOTTARI_ORDER[(VIMSHOTTARI_ORDER.index(lord) + 1) % 9]


def build_full_timeline(chart, levels=4):
    """Build 4-level dasha timeline: MD -> AD -> PD -> SD.

    Returns: list of dicts, each = {start, end, md, ad, pd, sd, level_years}
    Sorted by start date. Covers from birth to ~120 years of age.

    BUG FIX 2026-05-11: Previously the birth MD's antardashas were compressed —
    all 9 ADs squeezed into the REMAINING fraction of the MD instead of running
    the full AD sequence at standard lengths and starting mid-sequence at birth.
    Sachin's birth AD: old code = Venus-Venus, correct = Venus-Mercury.
    Now: treat MD as starting at birth_dt - elapsed_in_md, generate full standard
    timeline, then clip records that ended before birth.
    """
    if not isinstance(chart, dict):
        from dataclasses import asdict, is_dataclass
        if is_dataclass(chart):
            chart = asdict(chart)
            
    moon = chart["positions"]["Moon"]
    if isinstance(moon, (int, float)):
        moon_lon = float(moon)
    else:
        moon_lon = moon.get("lon_abs") or moon.get("lon") or (moon["rasi_idx"]*30 + moon.get("deg",0))
    nak_idx = int(moon_lon // (360/27))
    progress = (moon_lon - nak_idx*(360/27)) / (360/27)
    nak_lord = NAK_LORDS_27[nak_idx]

    if "birth_dt" in chart:
        birth_dt = chart["birth_dt"]
        if isinstance(birth_dt, str):
            birth_dt = dt.datetime.fromisoformat(birth_dt.replace("Z", "+00:00"))
    else:
        b = chart["birth"]
        birth_dt = dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])

    # Birth-MD elapsed: how far into the MD we already are at birth
    md_full_years_birth = VIMSHOTTARI_YEARS[nak_lord]
    elapsed_md_years = md_full_years_birth * progress

    # Anchor: treat the birth MD as if it started this long BEFORE birth
    md_calendar_start = birth_dt - dt.timedelta(days=elapsed_md_years * 365.25)

    timeline = []
    cur_md_lord = nak_lord
    cur_md_start = md_calendar_start

    for _ in range(9):
        md_full_years = VIMSHOTTARI_YEARS[cur_md_lord]
        md_end = cur_md_start + dt.timedelta(days=md_full_years * 365.25)

        # Only emit the MD record if any portion remains after birth
        if md_end > birth_dt:
            md_record_start = max(cur_md_start, birth_dt)
            md_record_years = (md_end - md_record_start).days / 365.25
            timeline.append({
                "start": md_record_start, "end": md_end,
                "years": md_record_years, "level": 1, "md": cur_md_lord
            })

        if levels >= 2:
            # Full standard AD sequence at FULL lengths from MD start
            ad_lord = cur_md_lord
            ad_start = cur_md_start
            for _ in range(9):
                ad_years = md_full_years * VIMSHOTTARI_YEARS[ad_lord] / 120
                ad_end = ad_start + dt.timedelta(days=ad_years * 365.25)

                if ad_end > birth_dt:
                    ad_record_start = max(ad_start, birth_dt)
                    ad_record_years = (ad_end - ad_record_start).days / 365.25
                    timeline.append({
                        "start": ad_record_start, "end": ad_end,
                        "years": ad_record_years, "level": 2,
                        "md": cur_md_lord, "ad": ad_lord
                    })

                if levels >= 3:
                    pd_lord = ad_lord
                    pd_start = ad_start
                    for _ in range(9):
                        pd_years = ad_years * VIMSHOTTARI_YEARS[pd_lord] / 120
                        pd_end = pd_start + dt.timedelta(days=pd_years * 365.25)

                        if pd_end > birth_dt:
                            pd_record_start = max(pd_start, birth_dt)
                            pd_record_years = (pd_end - pd_record_start).days / 365.25
                            timeline.append({
                                "start": pd_record_start, "end": pd_end,
                                "years": pd_record_years, "level": 3,
                                "md": cur_md_lord, "ad": ad_lord, "pd": pd_lord
                            })

                        if levels >= 4:
                            sd_lord = pd_lord
                            sd_start = pd_start
                            for _ in range(9):
                                sd_years = pd_years * VIMSHOTTARI_YEARS[sd_lord] / 120
                                sd_end = sd_start + dt.timedelta(days=sd_years * 365.25)

                                if sd_end > birth_dt:
                                    sd_record_start = max(sd_start, birth_dt)
                                    sd_record_years = (sd_end - sd_record_start).days / 365.25
                                    timeline.append({
                                        "start": sd_record_start, "end": sd_end,
                                        "years": sd_record_years, "level": 4,
                                        "md": cur_md_lord, "ad": ad_lord, "pd": pd_lord, "sd": sd_lord
                                    })
                                sd_start = sd_end
                                sd_lord = _next_lord(sd_lord)
                        pd_start = pd_end
                        pd_lord = _next_lord(pd_lord)
                ad_start = ad_end
                ad_lord = _next_lord(ad_lord)

        cur_md_start = md_end
        cur_md_lord = _next_lord(cur_md_lord)

    # Truncate to ~120 years from birth
    horizon = birth_dt + dt.timedelta(days=120*365.25)
    timeline = [r for r in timeline if r["start"] < horizon]
    return timeline


def lookup(timeline, when_dt):
    """Find all active dasha periods (MD, AD, PD, SD) on a given date."""
    active = {}
    for rec in timeline:
        if rec["start"] <= when_dt <= rec["end"]:
            active[rec["level"]] = rec
    return active


if __name__ == "__main__":
    import json
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    tl = build_full_timeline(chart, levels=3)
    aug_1996 = dt.datetime(1996, 8, 25)
    active = lookup(tl, aug_1996)
    print(f"Active periods for Manoj on {aug_1996.date()}:")
    for level, rec in sorted(active.items()):
        lvl_name = ["", "MD", "AD", "PD", "SD"][level]
        lords = "-".join([rec[k] for k in ["md","ad","pd","sd"] if k in rec])
        print(f"  {lvl_name} {lords:30s}  {rec['start'].date()} -> {rec['end'].date()}  ({rec['years']*365.25:.0f} days)")
