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
        
    # Build Kavipriya's chart
    # 2001-10-19 05:28 AM, Coimbatore
    # lat=11.0168, lon=76.9558, tz=5.5
    kavipriya_core = build_sidereal_chart(
        year=2001,
        month=10,
        day=19,
        time_str="05:28",
        lat=11.0168,
        lon=76.9558,
        tz_hours=5.5
    )
    
    # Save Kavipriya's chart JSON (using convention _anti_ prefix first)
    kavipriya_chart_dict = build_orchestrator_chart_dict(
        year=2001,
        month=10,
        day=19,
        time_str="05:28",
        lat=11.0168,
        lon=76.9558,
        tz_hours=5.5
    )
    kavipriya_chart_dict["name"] = "Kavipriya"
    kavipriya_chart_dict["moon_rasi"] = kavipriya_core["janma_rasi"]
    kavipriya_chart_dict["janma_nakshatra"] = kavipriya_core["janma_nakshatra"]
    
    with open("charts/_anti_kavipriya_chart.json", "w", encoding="utf-8") as f:
        json.dump(kavipriya_chart_dict, f, indent=2, ensure_ascii=False)
        
    print(f"Manoj Rasi: {manoj_chart['moon_rasi']}, Nakshatra: {manoj_chart['janma_nakshatra']}, Lagna: {manoj_chart['lagna']}")
    print(f"Kavipriya Rasi: {kavipriya_core['janma_rasi']}, Nakshatra: {kavipriya_core['janma_nakshatra']}, Lagna: {kavipriya_core['lagnam_rasi']}")
    
    # Run Ashtakuta Match
    boy_moon_lon = manoj_chart["positions"]["Moon"]["lon"]
    girl_moon_lon = kavipriya_core["planet_positions"]["Moon"]["longitude"]
    
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
    boy_mangal = {
        "lagna": manoj_chart["lagna_lon"],
        "positions": {
            "Moon": manoj_chart["positions"]["Moon"]["lon"],
            "Mars": manoj_chart["positions"]["Mars"]["lon"]
        }
    }
    girl_mangal = {
        "lagna": kavipriya_core["asc_sid"],
        "positions": {
            "Moon": kavipriya_core["planet_positions"]["Moon"]["longitude"],
            "Mars": kavipriya_core["planet_positions"]["Mars"]["longitude"]
        }
    }
    
    boy_md = mangal_dosha(boy_mangal)
    girl_md = mangal_dosha(girl_mangal)
    
    print("\n=== MANGAL DOSHA / SEVVAI DOSHAM ===")
    print(f"Manoj: {boy_md}")
    print(f"Kavipriya: {girl_md}")

if __name__ == "__main__":
    main()
