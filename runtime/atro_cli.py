"""Atro Vedic Engine — Command-Line Interface.

Usage:
  python atro_cli.py --chart NAME [--out FILE] [--mode MODE]

Modes:
  pdf       Generate full PDF report (default)
  json      Output full analysis as JSON
  summary   Quick text summary to console
  present   Just the "present moment" synthesis
  forecast  30-day day-by-day forecast
  match     Compatibility match (requires --chart2)
  events    Lifetime events table
  yogas     List active yogas
"""
import sys, json, argparse, datetime as dt
sys.path.insert(0, ".")
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHARTS = Path(__import__("os").environ.get("ATRO_CHARTS", ROOT / "charts"))
REPORTS = Path(__import__("os").environ.get("ATRO_REPORTS", ROOT / "reports"))
REPORTS.mkdir(parents=True, exist_ok=True)


def load_chart(name):
    """Load chart by name — tries name.json, name_chart.json, in charts/ dir."""
    candidates = [
        Path(name),
        CHARTS / name,
        CHARTS / f"{name}.json",
        CHARTS / f"{name}_chart.json",
        CHARTS / f"{name.lower()}.json",
        CHARTS / f"{name.lower()}_chart.json",
    ]
    for c in candidates:
        if c.exists():
            return json.load(open(c, encoding="utf-8"))
    raise FileNotFoundError(f"No chart found for '{name}'. Tried: {[str(c) for c in candidates]}")


def cmd_pdf(args, chart):
    """Generate full PDF report."""
    out = args.out or f"{chart['name'].upper().replace(' ','_')}_FULL_REPORT.pdf"
    from generate_report import generate
    # Find the actual chart file path
    candidates = [Path(args.chart), CHARTS / args.chart, CHARTS / f"{args.chart}.json",
                  CHARTS / f"{args.chart}_chart.json", CHARTS / f"{args.chart.lower()}_chart.json"]
    chart_path = next((c for c in candidates if c.exists()), None)
    if not chart_path:
        print(f"ERROR: chart file not found for {args.chart}")
        return
    generate(chart_path, out)
    print(f"PDF: {REPORTS / out}")


def cmd_json(args, chart):
    """Full analysis as JSON."""
    from engine_orchestrator import full_analysis
    result = full_analysis(chart)
    out_path = args.out or f"{chart['name']}_analysis.json"
    out_full = REPORTS / out_path
    # Convert datetimes for JSON
    def stringify(obj):
        if isinstance(obj, dt.datetime): return obj.isoformat()
        if isinstance(obj, dt.date): return obj.isoformat()
        if isinstance(obj, dict): return {k: stringify(v) for k, v in obj.items()}
        if isinstance(obj, list): return [stringify(x) for x in obj]
        return obj
    out_full.write_text(json.dumps(stringify(result), ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"JSON: {out_full}")


def cmd_summary(args, chart):
    """Quick text summary."""
    from engine_orchestrator import full_analysis
    result = full_analysis(chart)

    print(f"╔══════════════════════════════════════════════════════════════")
    print(f"║  {chart['name'].upper()} — VEDIC ENGINE SUMMARY  (engine v{result['engine_version']})")
    print(f"╚══════════════════════════════════════════════════════════════")
    print(f"  As of: {result['as_of']}")
    b = chart["birth"]
    print(f"  Born:  {b['day']:02d}-{b['month']:02d}-{b['year']} {b['hour']:02d}:{b['min']:02d} | {b['place']}")
    print(f"  Lagna: {chart['lagna']} | Moon: {chart.get('moon_rasi')} | Nakshatra: {chart.get('janma_nakshatra')}")
    print()

    # Yogas
    yogas = result["modules"]["classical_yogas"]["data"]
    extra = result["modules"].get("extra_yogas", {}).get("data", [])
    all_yogas = yogas + extra
    print(f"  ★ {len(all_yogas)} ACTIVE YOGAS")
    for y in sorted(all_yogas, key=lambda x:-x["severity"])[:5]:
        print(f"      {'★'*y['severity']} {y['name']}")

    # Dasha
    pm = result["modules"]["present_moment"]["data"]
    dashas = pm.get("dashas", {})
    if "MD" in dashas:
        print(f"  ⊙ CURRENT DASHA: {dashas['MD']['lords']} (until {dashas['MD']['to']})")
        if "AD" in dashas:
            print(f"    └ AD: {dashas['AD']['lords']}")

    # Sade Sati
    print(f"  ⏳ Sade Sati: {pm.get('sade_sati', '?')}")

    # Life events count
    events = result["modules"].get("life_events", {}).get("data", [])
    print(f"  📅 Life events flagged: {len(events)} bands")

    # Compatibility hint
    spouse = result["modules"]["spouse_inference"]["data"]
    print(f"  💍 Spouse type: {spouse.get('h7_sign','?')}-quality, {spouse.get('career_field','?')}")
    print(f"     Marriage window: {spouse.get('marriage_window','?')}")

    # Numerology
    n = result["modules"]["numerology"]["data"]
    print(f"  🔢 Mulanka: {n['mulanka']} ({n['mulanka_planet']}) | Bhagyanka: {n['bhagyanka']}")

    print()
    print(f"  Modules ok: {result['summary']['modules_ok']}/{result['summary']['modules_total']}")


def cmd_present(args, chart):
    """Present moment only."""
    from present_moment import present_moment_reading
    pm = present_moment_reading(chart)
    print(f"╔ PRESENT MOMENT: {chart['name']} ({pm['as_of']}) ╗")
    print(f"  Age: {pm['age']}\n")
    if "dashas" in pm and isinstance(pm["dashas"], dict):
        for lvl, d in pm["dashas"].items():
            if isinstance(d, dict):
                print(f"  {lvl}: {d['lords']:30s} ({d['from']} → {d['to']})")
    print(f"\n  Sade Sati: {pm.get('sade_sati')}")
    print(f"\n  SYNTHESIS: {pm['synthesis']}")


def cmd_forecast(args, chart):
    """30-day forecast."""
    from transit_forecast import forecast_period
    today = dt.datetime.now()
    fc = forecast_period(chart, today, args.days or 30)
    print(f"=== {args.days or 30}-DAY FORECAST for {chart['name']} ===\n")
    for f in fc:
        marker = "★" if f["score"] >= 2 else "▼" if f["score"] <= -2 else " "
        print(f"  {marker} {f['date']:<22}{f['score']:+3d}  {f['verdict']:<25}{f['md_ad']}")


def cmd_events(args, chart):
    """Lifetime events table."""
    from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive, _age_at
    b = chart["birth"]
    events = scan_lifetime_v2(chart, b["year"], b["year"] + 80, sample_days=14, min_severity=3)
    bands = collapse_consecutive(events)
    print(f"=== LIFETIME EVENTS for {chart['name']} ({len(bands)} bands) ===\n")
    print(f"{'AGE':<5}{'WINDOW':<22}{'SEV':<7}{'EVENT'}")
    for ev in bands:
        age = _age_at(ev["window_start"], chart)
        wf = ev["window_start"].strftime("%b %Y")
        wt = ev["window_end"].strftime("%b %Y")
        win = f"{wf} - {wt}" if wf != wt else wf
        sev = "★" * ev["max_sev"]
        print(f"  {age:<5.0f}{win:<22}{sev:<7}{ev['event']}")


def cmd_yogas(args, chart):
    """List active yogas."""
    from comprehensive_yogas import detect_all_classical_yogas
    from yoga_library_v2 import detect_extra_yogas
    yogas = detect_all_classical_yogas(chart) + detect_extra_yogas(chart)
    print(f"=== {len(yogas)} ACTIVE YOGAS for {chart['name']} ===\n")
    for y in sorted(yogas, key=lambda x:-x["severity"]):
        stars = "★"*y["severity"] + "☆"*(5-y["severity"])
        print(f"  {stars} {y['name']:42s} ({y['domain']})")
        print(f"        Source: {y['source']}")


def cmd_match(args, chart):
    """Compatibility match between two charts."""
    if not args.chart2:
        print("ERROR: --chart2 required for match mode")
        return
    chart2 = load_chart(args.chart2)
    from compatibility_kuta import ashtakuta_match
    result = ashtakuta_match(chart, chart2)
    print(f"=== ASHTAKUTA MATCH ===\n")
    print(f"  Boy:  {chart['name']} ({result['boy_rasi']}/{result['boy_nakshatra']})")
    print(f"  Girl: {chart2['name']} ({result['girl_rasi']}/{result['girl_nakshatra']})\n")
    for kuta, score in result["scores"].items():
        bar = "█" * score + "·" * (int(kuta.split("(")[1].split(")")[0]) - score)
        print(f"  {kuta:25s} {bar} {score}")
    print(f"\n  TOTAL: {result['total']}/{result['max']} ({result['percentage']}%) — {result['verdict']}")


def cmd_check(args, chart):
    """Engine integrity check."""
    from engine_orchestrator import integrity_check
    integrity_check(chart)


COMMANDS = {
    "pdf": cmd_pdf,
    "json": cmd_json,
    "summary": cmd_summary,
    "present": cmd_present,
    "forecast": cmd_forecast,
    "events": cmd_events,
    "yogas": cmd_yogas,
    "match": cmd_match,
    "check": cmd_check,
}


def main():
    p = argparse.ArgumentParser(description="Atro Vedic Engine CLI v13.0")
    p.add_argument("--chart", required=True, help="Chart name or path (e.g. 'manoj' or 'manoj_chart.json')")
    p.add_argument("--mode", default="summary", choices=list(COMMANDS.keys()),
                   help="Output mode (default: summary)")
    p.add_argument("--out", default=None, help="Output file path")
    p.add_argument("--chart2", default=None, help="Second chart for match mode")
    p.add_argument("--days", type=int, default=None, help="Days for forecast mode")
    args = p.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    chart = load_chart(args.chart)
    COMMANDS[args.mode](args, chart)


if __name__ == "__main__":
    main()
