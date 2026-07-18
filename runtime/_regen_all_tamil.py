"""Regenerate all 12 Tamil PDFs with the improved event engine."""
import sys, json, traceback, os
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
_RUNTIME = Path(__file__).resolve().parent
sys.path.insert(0, str(_RUNTIME))

from generate_tamil_pdf import generate

CHARTS = [
    "manoj","sree","krishnan","jayaprakesh","sivadhanya","karnan",
    "sachin_tendulkar","ms_dhoni","amitabh_bachchan","ar_rahman","rekha","narendra_modi",
]
CHARTS_DIR = _RUNTIME.parent / "charts"
REPORTS_DIR = _RUNTIME.parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

def main():
    ok = []; fail = []
    for slug in CHARTS:
        try:
            chart_path = CHARTS_DIR / f"{slug}_chart.json"
            safe = slug.replace(" ", "_").replace(".", "").upper()
            out_path = REPORTS_DIR / f"{safe}_TAMIL.pdf"
            generate(str(chart_path), str(out_path))
            sz = out_path.stat().st_size // 1024
            print(f"  DONE: {out_path.name} ({sz} KB)")
            ok.append(slug)
        except Exception as e:
            print(f"  FAIL: {slug}: {e}")
            traceback.print_exc()
            fail.append((slug, str(e)))

    print(f"\n  {len(ok)} OK, {len(fail)} FAIL")
    if fail:
        for s, e in fail:
            print(f"    ✗ {s}: {e}")

if __name__ == "__main__":
    main()
