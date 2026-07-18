import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from runtime.kp_paddhati import kp_summary

def main():
    chart_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "charts", "manoj_chart.json")
    print(f"Loading test chart: {chart_path}")
    with open(chart_path, "r", encoding="utf-8") as f:
        chart = json.load(f)
        
    print("\n=== KP PRECISE CUSPAL SUB-LORD ANALYSIS ===")
    summary = kp_summary(chart)
    for key, data in summary.items():
        print(f"  {key:30s}")
        print(f"    Precise Cuspal Sub-Lord: {data['cuspal_sub_lord']:10s} (nakshatra: {data['csl_nakshatra']})")
        print(f"    Significators:           {', '.join(data['significators']) if data['significators'] else 'none'}")
        print()

if __name__ == "__main__":
    main()
