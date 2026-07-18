import sys
import json
import datetime as dt
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "engine"))

from runtime.category_engine import category_engine_instance

def generate_v2_report():
    chart_path = _ROOT / "charts" / "manoj_chart.json"
    with open(chart_path, "r", encoding="utf-8") as f:
        chart = json.load(f)
        
    name = chart.get("name", "Manoj Kumar")
    
    # We will scan from birth (1996) to present (2026)
    start_year = 1996
    end_year = 2026
    
    print(f"Scanning {name}'s chart from {start_year} to {end_year} using V2 Engine...")
    
    events = category_engine_instance.scan_lifetime(
        chart, 
        start_year, 
        end_year, 
        sample_days=14, 
        min_probability=0.6 # Only keep Strong events to avoid overwhelming the 30-year report
    )
    
    # Group events by year and sort by probability
    report_data = {}
    for ev in events:
        year = ev["year"]
        if year not in report_data:
            report_data[year] = []
        report_data[year].append(ev)
        
    for year in report_data:
        # Sort by probability descending
        report_data[year].sort(key=lambda x: x["probability"], reverse=True)
        # Deduplicate similar events in the same year (keep highest probability)
        seen_categories = set()
        deduped = []
        for ev in report_data[year]:
            if ev["category"] not in seen_categories:
                deduped.append(ev)
                seen_categories.add(ev["category"])
        report_data[year] = deduped
        
    # Build Markdown Output
    md = [
        f"# AstroReport OS V2 — Probabilistic Life Report",
        f"**Subject:** {name}",
        f"**Scan Period:** {start_year} - {end_year}",
        f"**Engine Version:** V2 Meta-Reasoner (RLHF Enabled)\n",
        f"> [!TIP]",
        f"> This report uses our new Bayesian probabilistic engine. It provides a Confidence Band (Moderate/Strong) and an Explainability Trace for every prediction, ensuring 100% transparency.\n"
    ]
    
    for year in sorted(report_data.keys()):
        md.append(f"## Year {year}")
        if not report_data[year]:
            md.append("*No major planetary triggers detected above the confidence threshold for this year.*")
            continue
            
        for ev in report_data[year]:
            prob_percent = int(ev["probability"] * 100)
            band = ev["confidence_band"]
            icon = "🟢" if band == "Strong" else "🟡"
            
            md.append(f"### {icon} {ev['event']}")
            md.append(f"- **Confidence:** {prob_percent}% ({band})")
            md.append(f"- **Peak Window:** {ev['window_start']} to {ev['window_end']}")
            if ev.get("contradictions"):
                md.append(f"- **Contradictions Flagged:** ⚠️ Yes (Resolved via Meta-Reasoner)")
            
            md.append(f"- **Astrological Evidence Trace:**")
            for why in ev["why"]:
                md.append(f"  - {why}")
            md.append("")
            
    out_path = _ROOT / "scratch" / "manoj_past_report.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
        
    print(f"Successfully generated V2 Markdown Report at {out_path}")

if __name__ == "__main__":
    generate_v2_report()
