"""
REVERSE-DIRECTION AUDIT
=======================
For each verified life event, run a chart-by-chart attribution:
  (1) Identify the classical Vedic rules that should predict this event type
      (BPHS / Phaladeepika / Saravali references)
  (2) Compute which rules ACTUALLY apply in the chart at that date
      (dasha lord, transit, house lord, karaka activation)
  (3) Show what Atro engine returns for that event/date
  (4) Verdict: did our engine fire because the classical rules were present?

This is rigorous bottom-up validation, not outcome-only.
"""
import sys, json
from pathlib import Path
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8")
_RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(_RUNTIME))

from granular_dasha import build_full_timeline
from transit_engine import detect_triggers, transit_positions
from event_predictor_v2 import (scan_year_v2, scan_lifetime_v2, collapse_consecutive,
                                  _lord, _h, _dig, ALL_PATTERNS_V2)
from comprehensive_yogas import detect_all_classical_yogas
from divisional_dasha import build_d9_dasha_timeline, build_d10_dasha_timeline, lookup_d9_dasha, lookup_d10_dasha

CHARTS = _RUNTIME.parent / "charts"
SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]


# ───────────────────────────────────────────────────────────────────
# CLASSICAL RULES PER EVENT-TYPE
# Each tuple: (rule_name, function returning True/False, source_citation)
# ───────────────────────────────────────────────────────────────────

def marriage_rules(chart, ds, tr, when):
    """BPHS Ch.80, Phaladeepika Ch.13, Saravali Ch.39 — marriage timing."""
    pos = chart["positions"]; lagna = chart["lagna_idx"]
    h7_lord = _lord(lagna, 7)
    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad"); pd = ds.get(3,{}).get("pd")
    venus_house = _h(pos, "Venus")
    # D9 navamsa
    try:
        d9_tl = build_d9_dasha_timeline(chart)
        d9_ds = lookup_d9_dasha(d9_tl, when)
        d9_md = d9_ds.get(1,{}).get("md") if d9_ds else None
        d9_ad = d9_ds.get(2,{}).get("ad") if d9_ds else None
    except:
        d9_md = d9_ad = None
    rules = [
        (f"7L ({h7_lord}) in MD/AD/PD", h7_lord in (md, ad, pd),
         "BPHS Ch.80 v.7 — 7L's dasha brings marriage"),
        (f"Venus in MD/AD/PD", "Venus" in (md, ad, pd),
         "Phaladeepika Ch.13 — Venus karaka of marriage"),
        (f"Jupiter in MD/AD/PD", "Jupiter" in (md, ad, pd),
         "Saravali Ch.39 — Jupiter activates for women + auspicious for men"),
        (f"D9 MD={d9_md} or AD={d9_ad} is Venus / 7L / D9-7L",
         d9_md in ("Venus", h7_lord) or d9_ad in ("Venus", h7_lord),
         "BPHS Ch.80 — D9 navamsa dasha for marriage precision"),
        (f"Venus or 7L (Jupiter etc.) transit-trigger (any)",
         any(t.get("transit") in ("Jupiter", "Venus") and t.get("natal") in ("Moon", "Venus", h7_lord)
             and t.get("severity") in ("MEDIUM", "HIGH", "VERY HIGH") for t in tr),
         "Phaladeepika Ch.13 — Jupiter/Venus transit to Moon/Venus/7L = marriage trigger"),
    ]
    return rules


def career_rules(chart, ds, tr, when):
    """BPHS Ch.25 (10H), Ch.30 (Karma), D10 Dashamsa — career timing."""
    pos = chart["positions"]; lagna = chart["lagna_idx"]
    h10_lord = _lord(lagna, 10); h9_lord = _lord(lagna, 9); h11_lord = _lord(lagna, 11)
    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad"); pd = ds.get(3,{}).get("pd")
    try:
        d10_tl = build_d10_dasha_timeline(chart)
        d10_ds = lookup_d10_dasha(d10_tl, when)
        d10_md = d10_ds.get(1,{}).get("md") if d10_ds else None
        d10_ad = d10_ds.get(2,{}).get("ad") if d10_ds else None
    except:
        d10_md = d10_ad = None
    sun_h = _h(pos, "Sun")
    sat_h = _h(pos, "Saturn")
    rules = [
        (f"10L ({h10_lord}) in MD/AD/PD", h10_lord in (md, ad, pd),
         "BPHS Ch.25 — 10L's dasha activates career"),
        (f"9L ({h9_lord}) in MD/AD (fortune)", h9_lord in (md, ad),
         "BPHS Ch.32 — 9L (dharma/luck) supports career rise"),
        (f"11L ({h11_lord}) in MD/AD (gains)", h11_lord in (md, ad),
         "Phaladeepika Ch.6 — 11L delivers gains/achievements"),
        (f"Sun in MD/AD (career karaka)", "Sun" in (md, ad, pd),
         "Saravali — Sun = atmakaraka, fame, authority"),
        (f"D10 MD={d10_md} or AD={d10_ad} matches 10L/Sun/Saturn",
         d10_md in (h10_lord, "Sun", "Saturn") or d10_ad in (h10_lord, "Sun", "Saturn"),
         "BPHS Ch.25 — D10 Dashamsa dasha for career events"),
        (f"Saturn transit over 10H (or Moon)",
         any(t.get("transit") == "Saturn"
             and t.get("severity") in ("MEDIUM", "HIGH", "VERY HIGH") for t in tr),
         "BPHS — Saturn slow transit triggers karma-events"),
    ]
    return rules


def father_rules(chart, ds, tr, when):
    """Sun + 9H — father karaka rules."""
    pos = chart["positions"]; lagna = chart["lagna_idx"]
    h9_lord = _lord(lagna, 9)
    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad"); pd = ds.get(3,{}).get("pd")
    sun_dig = _dig(pos, "Sun") if pos.get("Sun") else None
    pyoga_present = False  # would need yoga detection
    rules = [
        (f"Sun in MD/AD/PD (karaka)", "Sun" in (md, ad, pd),
         "Saravali — Sun = father karaka, its dasha activates father events"),
        (f"9L ({h9_lord}) in MD/AD", h9_lord in (md, ad),
         "BPHS — 9H is father's house; its lord's dasha = father events"),
        (f"Sun is debilitated/combust at birth", sun_dig == "Debil",
         "Phaladeepika Ch.13 — afflicted Sun signals early/difficult father karma"),
        (f"Saturn transit over Sun",
         any(t.get("transit")=="Saturn" and t.get("natal")=="Sun"
             and t.get("severity") in ("MEDIUM","HIGH","VERY HIGH") for t in tr),
         "BPHS — Saturn slow transit over natal Sun = father stress trigger"),
        (f"Rahu/Ketu transit over Sun",
         any(t.get("transit") in ("Rahu","Ketu") and t.get("natal")=="Sun" for t in tr),
         "Hora Sara — node-affliction of Sun = father-loss timing"),
    ]
    return rules


def honor_rules(chart, ds, tr, when):
    """State honor / Padma / Bharat Ratna — Jupiter, Sun, strong dignity rules."""
    pos = chart["positions"]; lagna = chart["lagna_idx"]
    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad"); pd = ds.get(3,{}).get("pd")
    h11_lord = _lord(lagna, 11); h5_lord = _lord(lagna, 5)
    sun_dig = _dig(pos, "Sun") if pos.get("Sun") else None
    jup_dig = _dig(pos, "Jupiter") if pos.get("Jupiter") else None
    rules = [
        (f"Jupiter in MD/AD/PD (auspicious)", "Jupiter" in (md, ad, pd),
         "Saravali — Jupiter = guru, brings recognition + state honor"),
        (f"Sun in MD/AD (state-recognition karaka)", "Sun" in (md, ad),
         "BPHS — Sun = king, government honor, top awards"),
        (f"11L ({h11_lord}) MD/AD — gains/achievements", h11_lord in (md, ad),
         "Phaladeepika Ch.6 — 11H = labha (gains, honors received)"),
        (f"5L ({h5_lord}) MD/AD — Poorva Punya / fame",
         h5_lord in (md, ad),
         "Saravali — 5H = past-life merit, surfaces as recognition"),
        (f"Sun or Jupiter strong (not debilitated/combust)",
         sun_dig in ("Own","Exalted","Friend") or jup_dig in ("Own","Exalted","Friend"),
         "BPHS — strong Sun/Jupiter delivers their results during dasha"),
    ]
    return rules


def death_rules(chart, ds, tr, when, age):
    """Maraka 2L/7L + 8H Ayur + node-induced exit (BPHS Ch.45-46)."""
    pos = chart["positions"]; lagna = chart["lagna_idx"]
    h2_lord = _lord(lagna, 2); h7_lord = _lord(lagna, 7); h8_lord = _lord(lagna, 8)
    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad"); pd = ds.get(3,{}).get("pd")
    rules = [
        (f"2L ({h2_lord}) Maraka in MD/AD", h2_lord in (md, ad),
         "BPHS Ch.45 — 2L = Maraka (death-inflicter)"),
        (f"7L ({h7_lord}) Maraka in MD/AD", h7_lord in (md, ad),
         "BPHS Ch.45 — 7L = Maraka"),
        (f"8L ({h8_lord}) MD with malefic AD",
         md == h8_lord and ad in ("Saturn","Rahu","Ketu","Mars"),
         "BPHS Ch.46 — 8L's dasha is Ayur-exhaustion period"),
        (f"Rahu/Ketu MD at advanced age (50+)",
         md in ("Rahu","Ketu") and age >= 50,
         "Hora Sara — node-MDs at older age trigger exit"),
        (f"Saturn MD at advanced age (70+)",
         md == "Saturn" and age >= 70,
         "BPHS — Saturn natural endpoint of life"),
        (f"Sade Sati active",
         any(t.get("type")=="sade_sati" for t in tr),
         "Phaladeepika — Sade Sati's peak = critical health"),
    ]
    return rules


def health_rules(chart, ds, tr, when, age):
    """Health crisis / accident / surgery — BPHS Ch.40 Roga."""
    pos = chart["positions"]; lagna = chart["lagna_idx"]
    h6_lord = _lord(lagna, 6); h8_lord = _lord(lagna, 8); h12_lord = _lord(lagna, 12)
    asc_lord = chart.get("lagna_lord")
    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad")
    asc_dig = _dig(pos, asc_lord) if asc_lord and pos.get(asc_lord) else None
    rules = [
        (f"Mars in MD/AD (accident karaka)", "Mars" in (md, ad),
         "BPHS Ch.40 — Mars is the natural accident-and-injury karaka"),
        (f"Saturn in MD/AD (chronic illness)", "Saturn" in (md, ad),
         "Phaladeepika Ch.13 — Saturn's dasha = chronic flares + slow accidents"),
        (f"Ketu in MD/AD (viral/mysterious illness)", "Ketu" in (md, ad),
         "BPHS — Ketu causes fevers, viruses, mysterious illnesses"),
        (f"6L/8L/12L (dusthana) in MD",
         md in (h6_lord, h8_lord, h12_lord),
         "BPHS Ch.40 — dusthana lords' dasha = disease/loss/hospitalization"),
        (f"Weak lagna lord ({asc_lord}) MD when debilitated",
         md == asc_lord and asc_dig == "Debil",
         "Saravali — weak ascendant lord's dasha = body weakness"),
        (f"Saturn transit over Moon",
         any(t.get("transit")=="Saturn" and t.get("natal")=="Moon"
             and t.get("severity") in ("MEDIUM","HIGH","VERY HIGH") for t in tr),
         "Phaladeepika — Saturn over Moon = vital-force exhaustion"),
    ]
    return rules


# ─── EVENT-TO-RULE MAPPING ────────────────────────────────────────
TEST_EVENTS = [
    {"slug": "sachin_tendulkar", "date": "1995-05-24", "name": "Sachin Tendulkar",
     "event": "Marriage to Anjali Mehta", "rule_fn": marriage_rules, "category": "marriage"},
    {"slug": "sachin_tendulkar", "date": "2014-02-04", "name": "Sachin Tendulkar",
     "event": "Bharat Ratna (1st sportsperson)", "rule_fn": honor_rules, "category": "honor"},
    {"slug": "ms_dhoni", "date": "2010-07-04", "name": "MS Dhoni",
     "event": "Married Sakshi", "rule_fn": marriage_rules, "category": "marriage"},
    {"slug": "narendra_modi", "date": "2014-05-26", "name": "Narendra Modi",
     "event": "Sworn in as PM India", "rule_fn": career_rules, "category": "career_breakthrough"},
    {"slug": "ar_rahman", "date": "2009-02-22", "name": "A.R. Rahman",
     "event": "Won 2 Oscars (Slumdog)", "rule_fn": honor_rules, "category": "honor"},
    {"slug": "indira_gandhi", "date": "1984-10-31", "name": "Indira Gandhi",
     "event": "Assassinated at age 66", "rule_fn": death_rules, "category": "death_self"},
    {"slug": "steve_jobs", "date": "2003-10-01", "name": "Steve Jobs",
     "event": "Pancreatic cancer dx (age 48)", "rule_fn": health_rules, "category": "health_self"},
    {"slug": "mukesh_ambani", "date": "2002-07-06", "name": "Mukesh Ambani",
     "event": "Father Dhirubhai died", "rule_fn": father_rules, "category": "father"},
]


def compute_atro_engine_for_date(chart, when_dt, target_category):
    """Run Atro engine for the date and return matching predictions.
    scan_year_v2 returns a dict {event_label: event_dict}; filter by category.
    """
    yr = when_dt.year
    raw = scan_year_v2(chart, yr, sample_days=15, min_severity=1)
    if not raw: return []
    matches = []
    if isinstance(raw, dict):
        for label, ev in raw.items():
            if isinstance(ev, dict) and ev.get("category") == target_category:
                matches.append(ev)
    elif isinstance(raw, list):
        for ev in raw:
            if isinstance(ev, dict) and ev.get("category") == target_category:
                matches.append(ev)
    return matches


def audit_event(test):
    """Run the full attribution audit for one event."""
    print(f"\n{'═' * 80}")
    print(f"  EVENT:    {test['name']} — {test['event']}")
    print(f"  DATE:     {test['date']}")
    print(f"{'═' * 80}")

    chart = json.load(open(CHARTS / f"{test['slug']}_chart.json", encoding="utf-8"))
    when = datetime.strptime(test["date"], "%Y-%m-%d")
    age = when.year - chart["birth"]["year"]

    # Get dasha + transits
    tl = build_full_timeline(chart, levels=3)
    md = next((e for e in tl if e.get("level")==1 and e["start"]<=when<=e["end"]), None)
    ad = next((e for e in tl if e.get("level")==2 and e["start"]<=when<=e["end"]), None)
    pd = next((e for e in tl if e.get("level")==3 and e["start"]<=when<=e["end"]), None)
    ds = {1: {"md": md["md"] if md else "?"},
          2: {"ad": ad["ad"] if ad else "?"},
          3: {"pd": pd["pd"] if pd else "?"}}

    # Compute transits
    try:
        tpos = transit_positions(when)
        tr = detect_triggers(chart, tpos, when)
    except Exception as e:
        tr = []

    print(f"  Lagna: {chart['lagna']}  ({chart['lagna_lord']})   Age: {age}")
    print(f"  Dasha: MD={ds[1]['md']}  AD={ds[2]['ad']}  PD={ds[3]['pd']}")

    # ── Classical rules check ──
    if test["rule_fn"] == death_rules:
        rules = test["rule_fn"](chart, ds, tr, when, age)
    elif test["rule_fn"] == health_rules:
        rules = test["rule_fn"](chart, ds, tr, when, age)
    else:
        rules = test["rule_fn"](chart, ds, tr, when)

    print(f"\n  ── CLASSICAL VEDIC RULES (BPHS / Phaladeepika / Saravali) ──")
    print(f"  {'Rule':<60}  {'Status':<7}  Source")
    print(f"  {'-'*60}  {'-'*7}  {'-'*40}")
    hits, misses = 0, 0
    for rule_name, fires, source in rules:
        status = "✓ FIRES" if fires else "✗ DOES NOT"
        if fires: hits += 1
        else: misses += 1
        print(f"  {rule_name[:60]:<60}  {status:<7}  {source[:40]}")
    print(f"\n  Classical rules fired: {hits}/{len(rules)} ({100*hits//len(rules)}%)")

    # ── Atro engine output ──
    atro_preds = compute_atro_engine_for_date(chart, when, test["category"])
    if atro_preds:
        print(f"\n  ── ATRO ENGINE OUTPUT for category '{test['category']}' ──")
        for p in atro_preds[:3]:
            print(f"    severity={p.get('severity',0)}  scored")
            for w in p.get("why", [])[:6]:
                print(f"      • {w}")
            src = p.get("source", "?")
            print(f"    source: {src[:80]}")
        verdict = "✓ ENGINE FIRED" if hits >= 2 else "~ ENGINE FIRED but classical rules weak"
        print(f"\n  ▶ VERDICT: {verdict}  (engine fired={len(atro_preds)>0}, classical rules satisfied={hits}/{len(rules)})")
    else:
        if hits >= 2:
            print(f"\n  ▶ VERDICT: ✗ ENGINE MISS — classical rules satisfied ({hits}/{len(rules)}) but engine didn't fire")
        else:
            print(f"\n  ▶ VERDICT: ✓ CORRECTLY SILENT — classical rules weak ({hits}/{len(rules)}), engine correctly didn't fire")


def main():
    print("\n" + "█" * 80)
    print("  REVERSE-DIRECTION AUDIT — Classical Rules vs Atro Engine")
    print("  For each REAL event: check which BPHS rules apply and whether Atro fires")
    print("█" * 80)
    for test in TEST_EVENTS:
        try:
            audit_event(test)
        except Exception as e:
            print(f"\n  ERROR on {test['name']}: {e}")
            import traceback; traceback.print_exc()
    print()


if __name__ == "__main__":
    main()
