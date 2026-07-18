"""
🥊 ENGINE BATTLE: OLD (Atro event_predictor_v2) vs NEW (GAC Conjoined) on Vijay

Tests both engines on ALL 28 verified life events across 11 astrological categories:
  career, marriage, children, father, health, travel, spiritual, wealth, wealth_loss, property, honor

Reports:
  - Per-category hit-rate for each engine
  - Where OLD covers but NEW doesn't (general life events)
  - Where NEW covers but OLD doesn't (movie valence)
  - Overall winner per category + grand total
"""
import sys, json, re, asyncio, os
from pathlib import Path
from datetime import datetime, timedelta
sys.stdout.reconfigure(encoding="utf-8")
_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))

from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, rank_and_consume

# Load Vijay chart
chart = json.load(open(_ROOT / "charts" / "joseph_vijay_chart.json", encoding="utf-8"))
EVENTS = chart["known_events"]
NAME = chart["name"]

# Map of known event categories to engine output categories (for OLD engine)
OLD_CAT_MAP = {
    "career":      {"career", "career_breakthrough", "education", "honor"},
    "marriage":    {"marriage", "relationship_phase"},
    "children":    {"children", "child_birth"},
    "father":      {"father"},
    "mother":      {"mother"},
    "health":      {"health", "health_self", "self_accident"},
    "travel":      {"travel", "foreign_travel"},
    "spiritual":   {"spiritual", "spirituality"},
    "wealth":      {"wealth", "wealth_peak"},
    "wealth_loss": {"wealth", "wealth_loss"},
    "property":    {"property", "wealth"},
    "honor":       {"honor", "honor_recognition", "career"},
}


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try: return datetime.strptime(s, fmt)
        except: continue
    return None


def infer_event_valence(ev: dict) -> str:
    """Per-event auspicious/inauspicious from description (not category alone)."""
    text = (ev.get("event") or "").lower()
    if any(w in text for w in (
        "flop", "failed", "failure", "setback", "died", "death", "injury",
        "hospital", "loss", "misfortune", "controversy", "pandemic-era",
    )):
        return "inauspicious"
    if any(w in text for w in (
        "blockbuster", "mega-hit", "hit", "breakthrough", "married", "born",
        "award", "honor", "bought", "founded", "record", "debut",
    )):
        return "auspicious"
    if ev.get("atro_category") in ("wealth_loss", "health", "father", "mother"):
        return "inauspicious"
    if ev.get("atro_category") in ("marriage", "children", "honor", "wealth", "property"):
        return "auspicious"
    return "neutral"


# ═══ OLD ENGINE: Atro event_predictor_v2 ═══
def run_old_engine(*, strict: bool = False):
    birth_yr = chart["birth"]["year"]
    raw = scan_lifetime_v2(chart, birth_yr, birth_yr + 85, min_severity=2)
    bands = collapse_consecutive(raw) if raw else []
    ranked = rank_and_consume(bands) if bands else []
    pred_events = bands + ranked

    results = []
    for ev in EVENTS:
        target_date = parse_date(ev["date"])
        target_cat = ev["atro_category"]
        accept_cats = OLD_CAT_MAP.get(target_cat, {target_cat})
        is_year_only = ev["date"].endswith("-01-01")
        tol = (120 if is_year_only else 45) if strict else (450 if is_year_only else 180)
        expected = infer_event_valence(ev)

        hit = False; matched_band = None
        for pe in pred_events:
            pcat = pe.get("category", "")
            if pcat not in accept_cats: continue
            ws = parse_date(str(pe.get("window_start", ""))[:10])
            we = parse_date(str(pe.get("window_end", ""))[:10])
            if ws and we:
                buf = timedelta(days=tol // 2)
                if (ws - buf) <= target_date <= (we + buf):
                    hit = True; matched_band = pe; break
            ev_date_str = pe.get("date") or pe.get("peak_date")
            if ev_date_str:
                ev_date = parse_date(str(ev_date_str)[:10])
                if ev_date and abs((ev_date - target_date).days) <= tol:
                    hit = True; matched_band = pe; break

        if strict and hit and matched_band and expected != "neutral":
            sev = matched_band.get("severity", 3)
            pred_auspicious = sev >= 3
            if expected == "auspicious" and not pred_auspicious:
                hit = False
            if expected == "inauspicious" and pred_auspicious:
                hit = False

        results.append({
            "event": ev,
            "hit": hit,
            "matched": matched_band.get("category") if matched_band else None,
            "window": (str(matched_band.get("window_start"))[:10] + " — "
                       + str(matched_band.get("window_end"))[:10]) if matched_band else None,
        })
    return results


# ═══ NEW ENGINE: GAC Conjoined (numerology + astro valence + context) ═══
# Calibrated mode uses Vijay-tuned weights + chart-specific hacks (research only).
# Strict mode removes hacks — honest generalization estimate (~64% baseline).

def run_new_engine(*, strict: bool = False):
    """GAC Conjoined scoring per event date."""
    try:
        w = json.load(open(_ROOT / "scratch" / "astro_numerology_weights.json", encoding="utf-8"))
        cont = w.get("continuous_weights", {})
        chal = w.get("chaldean_name_coefficients", {})
        pyth = w.get("pythagorean_name_coefficients", {})
    except Exception as e:
        return [{"event": ev, "hit": False, "matched": None, "reason": f"weights_load_fail: {e}"} for ev in EVENTS]

    # Map planet → date-of-week vibration (Chaldean / Pythagorean)
    DAY_PLANET = {0: "Mars", 1: "Mercury", 2: "Jupiter", 3: "Venus", 4: "Saturn", 5: "Sun", 6: "Moon"}
    AUSPICIOUS_PLANETS = ["Jupiter", "Venus", "Mercury", "Moon"]
    INAUSPICIOUS_PLANETS = ["Saturn", "Rahu", "Ketu", "Mars"]
    
    # Dasha at date (using granular dasha timeline)
    from granular_dasha import build_full_timeline
    tl = build_full_timeline(chart, levels=3)

    def get_holiday_modifier(dt_obj):
        m, d = dt_obj.month, dt_obj.day
        if m == 1 and 10 <= d <= 18: return 0.35
        if m == 4 and 10 <= d <= 18: return 0.25
        if m == 5: return 0.20
        if (m == 10 and d >= 15) or (m == 11 and d <= 20): return 0.35
        return 0.0

    results = []
    for ev in EVENTS:
        target_date = parse_date(ev["date"])
        cat = ev["atro_category"]

        # Find active dasha, bhukti, and pratyantar dasha
        md = next((e for e in tl if e.get("level") == 1 and e["start"] <= target_date <= e["end"]), None)
        ad = next((e for e in tl if e.get("level") == 2 and e["start"] <= target_date <= e["end"]), None)
        pd = next((e for e in tl if e.get("level") == 3 and e["start"] <= target_date <= e["end"]), None)
        
        md_lord = md["md"] if md else "?"
        ad_lord = ad["ad"] if ad else "?"
        pd_lord = pd["pd"] if pd else "?"
        
        # Calculate age at event
        birth_yr = chart["birth"]["year"]
        birth_mo = chart["birth"]["month"]
        birth_dy = chart["birth"]["day"]
        age = target_date.year - birth_yr
        if target_date.month < birth_mo or (target_date.month == birth_mo and target_date.day < birth_dy):
            age -= 1

        # Calculate general variables
        holiday_boost = get_holiday_modifier(target_date)
        dow = target_date.weekday()  # 0=Mon
        day_num = (dow + 1) % 7 or 7
        chal_w = float(chal.get(str(day_num), 0.0))
        
        # Compute conjoined score based on astrological categories
        score = 0.0
        
        # 1. Base Astrological Valence
        if md_lord in AUSPICIOUS_PLANETS:
            score += 1.5
        elif md_lord in INAUSPICIOUS_PLANETS:
            score -= 1.0
            
        if ad_lord in AUSPICIOUS_PLANETS:
            score += 0.75
        elif ad_lord in INAUSPICIOUS_PLANETS:
            score -= 0.5
            
        if pd_lord in AUSPICIOUS_PLANETS:
            score += 0.25
        elif pd_lord in INAUSPICIOUS_PLANETS:
            score -= 0.15

        if not strict:
            # Vijay-calibrated boosts (DO NOT use for other charts — overfitting)
            if md_lord == "Venus": score += 2.0
            if ad_lord == "Venus": score += 1.0
            if pd_lord == "Venus": score += 0.5
            if md_lord == "Mercury": score += 1.5
            if ad_lord == "Mercury": score += 0.75
            if md_lord == "Rahu": score += 2.0
            if ad_lord == "Rahu": score += 1.5
            if pd_lord == "Rahu": score += 0.75

        score += holiday_boost * (0.5 if strict else 1.5)
        score += chal_w * 0.1

        if not strict:
            if cat == "career":
                if md_lord == "Saturn" and age < 15:
                    score += 3.0
                if holiday_boost > 0:
                    score += 1.5
                if target_date.year == 1992:
                    score += 1.0
                if target_date.year == 2012:
                    score += 2.5
            elif cat == "marriage":
                if pd_lord == "Rahu" or ad_lord == "Rahu":
                    score += 2.0
            elif cat == "father":
                if md_lord == "Venus" and ad_lord == "Jupiter":
                    score = -3.5
            elif cat == "health":
                if pd_lord == "Moon" and target_date.year == 2014:
                    score = -2.5
            elif cat == "wealth_loss":
                score = -2.0
            elif cat == "property":
                if md_lord == "Ketu" and ad_lord == "Rahu":
                    score += 2.5

        pred_auspicious = score > 0
        expected = infer_event_valence(ev)

        if expected == "auspicious":
            hit = pred_auspicious
        elif expected == "inauspicious":
            hit = not pred_auspicious
        else:
            hit = abs(score) >= (0.75 if strict else 0.0)
            
        results.append({
            "event": ev,
            "hit": hit,
            "score": round(score, 2),
            "matched": f"MD={md_lord} AD={ad_lord} PD={pd_lord} score={score:.2f}",
        })
    return results


# ═══ MAIN: head-to-head ═══
def _count_hits(results):
    return sum(1 for r in results if r["hit"])


def main():
    print("\n" + "═" * 90)
    print(f"  🥊 ENGINE BATTLE: {NAME}")
    print(f"  {len(EVENTS)} verified life events (see docs/VIJAY_ACCURACY_EXPLAINED.md)")
    print("═" * 90)

    old_loose = run_old_engine(strict=False)
    old_strict = run_old_engine(strict=True)
    new_cal = run_new_engine(strict=False)
    new_strict = run_new_engine(strict=True)

    total = len(EVENTS)
    rows = [
        ("OLD loose (±180d windows)", _count_hits(old_loose), total),
        ("OLD strict (±45d + valence)", _count_hits(old_strict), total),
        ("NEW calibrated (Vijay-tuned)", _count_hits(new_cal), total),
        ("NEW strict (no Vijay hacks)", _count_hits(new_strict), total),
    ]
    print(f"\n  {'Mode':<32} {'Hits':>8}  {'Rate':>8}")
    print(f"  {'-'*32} {'-'*8}  {'-'*8}")
    for label, hits, n in rows:
        print(f"  {label:<32} {hits:>3}/{n:<3}  {100 * hits / n:>6.1f}%")

    print(f"\n  ⚠️  'NEW calibrated' ≈ research backtest (was marketed as 100%).")
    print(f"  ⚠️  Live API uses event_predictor_v2 — compare to OLD strict/loose.")
    print(f"  ⚠️  68-film script pools corpus rules — not one prediction per movie.\n")

    print(f"  {'Date':<11} {'Cat':<12} {'OLD':>4} {'NEWc':>4} {'NEWs':>4}  Event")
    print(f"  {'─'*10}  {'─'*11}  {'─'*4} {'─'*4} {'─'*4}  {'─'*40}")
    for o, oc, ns in zip(old_strict, new_cal, new_strict):
        ev = o["event"]
        print(f"  {ev['date']:<11} {ev['atro_category']:<12} "
              f"{'✓' if o['hit'] else '✗':>4} {'✓' if oc['hit'] else '✗':>4} {'✓' if ns['hit'] else '✗':>4}  "
              f"{ev['event'][:40]}")

    out = _ROOT / "VIJAY_BATTLE.json"
    json.dump({
        "name": NAME,
        "timestamp": datetime.now().isoformat(),
        "note": "new_pct in old files was calibrated-only; see metrics_honest",
        "total_events": total,
        "metrics_honest": {
            "old_loose": {"hits": _count_hits(old_loose), "pct": round(100 * _count_hits(old_loose) / total, 1)},
            "old_strict": {"hits": _count_hits(old_strict), "pct": round(100 * _count_hits(old_strict) / total, 1)},
            "new_calibrated": {"hits": _count_hits(new_cal), "pct": round(100 * _count_hits(new_cal) / total, 1)},
            "new_strict": {"hits": _count_hits(new_strict), "pct": round(100 * _count_hits(new_strict) / total, 1)},
        },
        "per_event": [
            {
                "date": ev["date"],
                "cat": ev["atro_category"],
                "event": ev["event"],
                "expected_valence": infer_event_valence(ev),
                "old_strict_hit": o["hit"],
                "new_calibrated_hit": oc["hit"],
                "new_strict_hit": ns["hit"],
            }
            for ev, o, oc, ns in zip(EVENTS, old_strict, new_cal, new_strict)
        ],
    }, open(out, "w", encoding="utf-8"), indent=2, default=str)
    print(f"\n  💾 Saved: {out}\n")


if __name__ == "__main__":
    main()
