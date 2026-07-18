import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.chart_builder import build_sidereal_chart, build_orchestrator_chart_dict
from engine.kuta import match_kuta, mangal_dosha

def main():
    # Manoj's chart is already in charts/manoj_chart.json
    with open("charts/manoj_chart.json", "r", encoding="utf-8") as f:
        manoj_chart = json.load(f)
        
    # Build Kayalvizhi's chart
    # 1997-06-26 04:07 AM, Oddanchatram
    # lat=10.4851135, lon=77.7460054, tz=5.5
    kayalvizhi_core = build_sidereal_chart(
        year=1997,
        month=6,
        day=26,
        time_str="04:07",
        lat=10.4851135,
        lon=77.7460054,
        tz_hours=5.5
    )
    
    # Save Kayalvizhi's chart JSON (using convention _anti_ prefix first)
    kayalvizhi_chart_dict = build_orchestrator_chart_dict(
        year=1997,
        month=6,
        day=26,
        time_str="04:07",
        lat=10.4851135,
        lon=77.7460054,
        tz_hours=5.5
    )
    kayalvizhi_chart_dict["name"] = "N. Kayalvizhi"
    kayalvizhi_chart_dict["moon_rasi"] = kayalvizhi_core["janma_rasi"]
    kayalvizhi_chart_dict["janma_nakshatra"] = kayalvizhi_core["janma_nakshatra"]
    
    with open("charts/_anti_kayalvizhi_chart.json", "w", encoding="utf-8") as f:
        json.dump(kayalvizhi_chart_dict, f, indent=2, ensure_ascii=False)
        
    print(f"Manoj Rasi: {manoj_chart['moon_rasi']}, Nakshatra: {manoj_chart['janma_nakshatra']}")
    print(f"Kayalvizhi Rasi: {kayalvizhi_core['janma_rasi']}, Nakshatra: {kayalvizhi_core['janma_nakshatra']}, Lagna: {kayalvizhi_core['lagnam_rasi']}")
    
    # Run Ashtakuta Match
    boy_moon_lon = manoj_chart["positions"]["Moon"]["lon"]
    girl_moon_lon = kayalvizhi_core["planet_positions"]["Moon"]["longitude"]
    
    kuta_res = match_kuta(boy_moon_lon, girl_moon_lon)
    print("\n=== ASHTAKUTA MATCH DETAILS ===")
    print(f"Varna: {kuta_res.varna}")
    print(f"Vasya: {kuta_res.vasya}")
    print(f"Tara: {kuta_res.tara}")
    print(f"Yoni: {kuta_res.yoni}")
    print(f"Graha Maitri: {kuta_res.graha_maitri}")
    print(f"Gana: {kuta_res.gana}")
    print(f"Bhakoot: {kuta_res.bhakoot}")
    print(f"Nadi: {kuta_res.nadi}")
    print(f"Total Score: {kuta_res.total[0]}/36")
    print(f"Verdict: {kuta_res.verdict}")
    print(f"Notes: {kuta_res.notes}")
    
    # Mangal Dosha check
    # We need to construct compatible chart dicts for mangal_dosha
    boy_mangal = {
        "lagna": manoj_chart["lagna_lon"],
        "positions": {
            "Moon": manoj_chart["positions"]["Moon"]["lon"],
            "Mars": manoj_chart["positions"]["Mars"]["lon"]
        }
    }
    girl_mangal = {
        "lagna": kayalvizhi_core["asc_sid"],
        "positions": {
            "Moon": kayalvizhi_core["planet_positions"]["Moon"]["longitude"],
            "Mars": kayalvizhi_core["planet_positions"]["Mars"]["longitude"]
        }
    }
    
    boy_md = mangal_dosha(boy_mangal)
    girl_md = mangal_dosha(girl_mangal)
    
    print("\n=== MANGAL DOSHA / SEVVAI DOSHAM ===")
    print(f"Manoj: {boy_md}")
    print(f"Kayalvizhi: {girl_md}")

if __name__ == "__main__":
    main()
