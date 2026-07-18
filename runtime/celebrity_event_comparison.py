"""
Celebrity Event Comparison — Vedic Engine Predictions vs Known Real Events.
Runs event_predictor_v2, dasha timeline, and yoga detection for each celebrity,
then compares against their known real events.
"""
import sys, json
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")
# Make imports work regardless of CWD
_RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(_RUNTIME))

from granular_dasha import build_full_timeline
from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume
from comprehensive_yogas import detect_all_classical_yogas
from sade_sati import compute_sade_sati_periods

CHARTS_DIR = _RUNTIME.parent / "charts"
SEP = "=" * 80


def load(slug):
    return json.load(open(CHARTS_DIR / f"{slug}_chart.json", encoding="utf-8"))


def dasha_at(timeline_flat, date_str):
    """Find active MD/AD at a given date from flat timeline (level-2 entries)."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        return "?"
    # Level-2 entries have both md and ad
    l2 = [e for e in timeline_flat if e.get("level") == 2]
    for e in l2:
        if e["start"] <= dt <= e["end"]:
            return f"{e['md']}/{e['ad']}"
    # Fallback: level-1
    l1 = [e for e in timeline_flat if e.get("level") == 1]
    for e in l1:
        if e["start"] <= dt <= e["end"]:
            return f"{e['md']}/?"
    return "Outside timeline"


def analyse_chart(slug, chart):
    name = chart["name"]
    known_events = chart.get("known_events", [])
    rodden = chart.get("rodden_rating", "?")
    note = chart.get("birth_time_note", "")

    print(f"\n{SEP}")
    print(f"  {name.upper()}  |  Lagna: {chart['lagna']}  |  Rodden: {rodden}")
    print(f"  Note: {note}")
    print(SEP)

    # Dasha timeline (Vimshottari at MD+AD level)
    timeline = build_full_timeline(chart, levels=2)
    # Build MD summary list for display
    vimsh = []
    seen_md = {}
    for entry in timeline:
        md_p = entry["md"]
        if md_p not in seen_md:
            seen_md[md_p] = {"planet": md_p, "start": entry["start"],
                              "end": entry["end"], "years": entry["years"],
                              "antardashas": []}
            vimsh.append(seen_md[md_p])
        if entry.get("level") == 2 and "ad" in entry:
            seen_md[md_p]["antardashas"].append(
                {"planet": entry["ad"], "start": entry["start"], "end": entry["end"]}
            )
            seen_md[md_p]["end"] = entry["end"]  # extend to last AD

    birth_yr = chart["birth"]["year"]
    # Predicted events across lifetime
    try:
        raw = scan_lifetime_v2(chart, birth_yr, birth_yr + 80, min_severity=3)
        all_bands = collapse_consecutive(raw) if raw else []
        pred_events = rank_and_consume(all_bands) if all_bands else []
    except Exception as e:
        pred_events = []
        all_bands = []

    # Yogas
    yogas = detect_all_classical_yogas(chart)

    # Sade sati
    sade = compute_sade_sati_periods(chart)

    # ── 1. CHART SNAPSHOT ──────────────────────────────────────────────────────
    print(f"\n{'─'*40}  PLANETARY POSITIONS  {'─'*17}")
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        pd = chart["positions"][p]
        retro = "R" if pd.get("retrograde") else " "
        print(f"  {p:<8} {pd['rasi']:<13} H{pd['house']:>2}  {pd['deg']:>6.2f}°  "
              f"{pd['nak']:<20} pada {pd['pada']}  {retro}")

    # ── 2. KEY YOGAS ─────────────────────────────────────────────────────────
    print(f"\n{'─'*40}  KEY YOGAS DETECTED  {'─'*19}")
    if yogas:
        for y in yogas[:15]:
            print(f"  ✦ {y['name']:<35} → {y.get('interpretation','')[:60]}")
    else:
        print("  (No yogas detected)")

    # ── 3. PREDICTED EVENTS ──────────────────────────────────────────────────
    print(f"\n{'─'*40}  ENGINE PREDICTED EVENTS  {'─'*14}")
    if pred_events:
        for ev in pred_events[:20]:
            date = str(ev.get("date") or ev.get("peak_date") or ev.get("window_start") or "?")
            etype = str(ev.get("type") or ev.get("event_type") or ev.get("category") or "")
            desc = str(ev.get("description") or ev.get("interpretation") or ev.get("summary") or "")
            dasha_s = str(ev.get("dasha") or "")
            print(f"  [{date[:10]}]  {etype:<22} {desc[:55]}  {dasha_s}")
    else:
        print("  (No events predicted)")

    # ── 4. DASHA TIMELINE (relevant years) ───────────────────────────────────
    print(f"\n{'─'*40}  VIMSHOTTARI DASHA TIMELINE  {'─'*11}")
    birth_year = chart["birth"]["year"]
    for md in vimsh:
        md_start_yr = int(str(md["start"])[:4])
        md_end_yr = int(str(md["end"])[:4])
        if md_end_yr < birth_year + 10:
            continue  # skip early childhood
        if md_start_yr > birth_year + 80:
            break
        ads = md.get("antardashas", [])
        ad_str = ", ".join(f"{a['planet']}({str(a['start'])[:4]}–{str(a['end'])[:4]})" for a in ads[:4])
        print(f"  {md['planet']:<8} {str(md['start'])[:10]} → {str(md['end'])[:10]}  "
              f"({md.get('years',0):.1f} yrs)  |  AD: {ad_str}")

    # ── 5. KNOWN EVENTS vs DASHA COMPARISON ──────────────────────────────────
    print(f"\n{'─'*40}  KNOWN EVENTS vs ENGINE PREDICTIONS  {'─'*5}")
    print(f"  {'DATE':<12} {'DASHA (MD/AD)':<18} {'ACTUAL EVENT'}")
    print(f"  {'─'*11} {'─'*17} {'─'*50}")

    for ev in known_events:
        date = ev["date"]
        actual = ev["event"]
        dasha_str = dasha_at(timeline, date)
        print(f"  {date:<12} {dasha_str:<18} {actual[:70]}")

    # ── 6. PATTERN MATCH ANALYSIS ────────────────────────────────────────────
    print(f"\n{'─'*40}  PATTERN ANALYSIS  {'─'*22}")

    # Check sade sati periods vs events
    sade_periods = []
    if isinstance(sade, list):
        for phase in sade:
            sade_periods.append((
                str(phase.get("start",""))[:10],
                str(phase.get("end",""))[:10],
                phase.get("phase", phase.get("type",""))
            ))
    elif isinstance(sade, dict):
        for phase in sade.get("phases", sade.get("periods", [])):
            sade_periods.append((
                str(phase.get("start",""))[:10],
                str(phase.get("end",""))[:10],
                phase.get("phase", phase.get("type",""))
            ))

    # Find which known events fall during Sade Sati
    sade_hits = []
    for ev in known_events:
        date = ev["date"]
        for (s, e, ph) in sade_periods:
            if s and e and s <= date <= e:
                sade_hits.append((date, ev["event"][:60], ph))
                break

    if sade_periods:
        print(f"\n  Sade Sati Periods:")
        for s, e, ph in sade_periods:
            print(f"    {ph:<10} {s} → {e}")

    if sade_hits:
        print(f"\n  Events during Sade Sati (expected hardship/transformation):")
        for date, ev, ph in sade_hits:
            print(f"    ⚠  {date}  [{ph}]  {ev}")
    else:
        print(f"\n  No known events overlap with Sade Sati periods (or Sade Sati not computed)")

    # Marriage/relationship events (ranked)
    marry_pred = [e for e in pred_events if e.get("category") in ("marriage", "relationship_phase")]
    marry_actual = [e for e in known_events if "married" in e["event"].lower() or "marriage" in e["event"].lower() or "wed" in e["event"].lower()]

    print(f"\n  Marriage windows (ranked): {len(marry_pred)} engine | {len(marry_actual)} actual")
    for e in sorted(marry_pred, key=lambda b: -b.get("score",0))[:5]:
        stars = e.get("stars","⭐"); score = e.get("score",0)
        ws = str(e.get("window_start",""))[:10]; we = str(e.get("window_end",""))[:10]
        evt = e.get("event","?")[:35]
        print(f"    {stars:<4} score={score:>2}  [{ws} - {we}]  {evt}")
    for e in marry_actual:
        dasha_str = dasha_at(timeline, e["date"])
        print(f"    Actual: {e['date']}  [{dasha_str}]  {e['event'][:65]}")

    # Career peak predictions
    career_pred = [e for e in pred_events if "career" in str(e).lower() or "breakthrough" in str(e).lower()]
    career_actual = [e for e in known_events if any(w in e["event"].lower() for w in ["won","award","debut","captain","pm","cm","oscar","grammy","bharat","century","world cup","national film"])]

    print(f"\n  Career/achievement events: {len(career_pred)} engine | {len(career_actual)} actual")
    for e in career_actual[:6]:
        dasha_str = dasha_at(timeline, e["date"])
        print(f"    Actual: {e['date']}  [{dasha_str}]  {e['event'][:65]}")

    print(f"\n{'─'*80}")


CELEBRITIES = [
    ("sachin_tendulkar", "Sachin — Cricket legend (Rodden A, birth time reliable)"),
    ("amitabh_bachchan", "Amitabh — Bollywood (Rodden DD, birth time disputed)"),
    ("narendra_modi",    "Modi — PM India (Rodden DD, birth time disputed)"),
    ("ms_dhoni",         "Dhoni — Cricket captain (Rodden A, birth time reliable)"),
    ("ar_rahman",        "A.R. Rahman — Music composer (Rodden A, self-reported)"),
    ("rekha",            "Rekha — Actress (Rodden A, almanac source)"),
]

if __name__ == "__main__":
    print(f"\n{'#'*80}")
    print(f"  ATRO VEDIC ENGINE — CELEBRITY EVENT COMPARISON  (6 charts)")
    print(f"  Engine predictions vs verified real-world events")
    print(f"{'#'*80}")

    for slug, desc in CELEBRITIES:
        try:
            chart = load(slug)
            analyse_chart(slug, chart)
        except Exception as e:
            print(f"\n[ERROR] {slug}: {e}")
            import traceback; traceback.print_exc()

    print(f"\n{'#'*80}")
    print(f"  DONE — Review dasha periods vs events for prediction accuracy")
    print(f"{'#'*80}\n")
