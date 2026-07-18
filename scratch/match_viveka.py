import os
import sys
import json
from pathlib import Path

# Add project root and runtime to path
_ROOT = Path("f:/astro")
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "scratch"))
sys.path.insert(0, str(_ROOT / "runtime"))

from generate_separate_reports import (
    build_sidereal_chart,
    match_kuta,
    mangal_dosha,
    compute_western_chart,
    compute_chinese_chart,
    compute_mayan_chart,
    compute_compatibility,
    generate_md_en,
    generate_pdf_en,
    generate_md_ta,
    generate_pdf_ta,
    HexColor
)

def main():
    boy_name = "Manoj Kumar"
    boy_date = "1996-05-25"
    boy_time = "20:25"
    boy_lat = 11.25
    boy_lon = 77.12
    boy_tz = 5.5

    b = {
        "name": "P. Viveka",
        "date": "2000-12-11",
        "time": "09:57",
        "lat": 11.0833,
        "lon": 77.3333,
        "tz": 5.5,
        "kulam": "Vellode (வெள்ளோடு)",
        "deity": "Rasasamy - Nallamangai Amman (ராசாசாமி - நல்லமங்கை அம்மன்)",
        "jadhagam": "Clean (சுத்தம்)",
        "education": "B.Com",
        "job": "Not Specified",
        "birth_place": "Tiruppur, TN",
        "birth_place_ta": "திருப்பூர், தமிழ்நாடு"
    }

    print(f"Casting charts and generating compatibility reports for Manoj Kumar & {b['name']}...")

    # Boy charts
    boy_sid = build_sidereal_chart(1996, 5, 25, boy_time, boy_lat, boy_lon, boy_tz)
    boy_moon_lon = boy_sid["planet_positions"]["Moon"]["longitude"]
    boy_mangal_chart = {
        "lagna": boy_sid["asc_sid"],
        "positions": {p: d["longitude"] for p, d in boy_sid["planet_positions"].items()}
    }
    boy_md = mangal_dosha(boy_mangal_chart)
    boy_west = compute_western_chart(boy_date, boy_time, boy_tz, boy_lat, boy_lon)
    boy_west_planets = boy_west["calculations"]["planets"]
    boy_chinese = compute_chinese_chart(boy_date, boy_time, boy_tz)
    boy_bazi = boy_chinese["calculations"]["bazi_pillars"]
    boy_mayan = compute_mayan_chart(boy_date)
    boy_tzolkin = boy_mayan["calculations"]

    # Girl charts
    by, bm, bd = map(int, b["date"].split("-"))
    girl_sid = build_sidereal_chart(by, bm, bd, b["time"], b["lat"], b["lon"], b["tz"])
    girl_moon_lon = girl_sid["planet_positions"]["Moon"]["longitude"]
    vedic_kuta = match_kuta(boy_moon_lon, girl_moon_lon)
    girl_mangal_chart = {
        "lagna": girl_sid["asc_sid"],
        "positions": {p: d["longitude"] for p, d in girl_sid["planet_positions"].items()}
    }
    girl_md = mangal_dosha(girl_mangal_chart)

    # Numerology
    num_res = compute_compatibility(boy_name, boy_date, b["name"], b["date"])

    # Western Synastry
    girl_west = compute_western_chart(b["date"], b["time"], b["tz"], b["lat"], b["lon"])
    girl_west_planets = girl_west["calculations"]["planets"]

    synastry_aspects = []
    aspect_definitions = [
        ("Conjunction", 0, 6),
        ("Sextile", 60, 4),
        ("Square", 90, 5),
        ("Trine", 120, 6),
        ("Opposition", 180, 6)
    ]
    major_bodies = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    for bp in major_bodies:
        blon = boy_west_planets[bp]["longitude"]
        for gp in major_bodies:
            glon = girl_west_planets[gp]["longitude"]
            diff = abs(blon - glon) % 360
            if diff > 180:
                diff = 360 - diff
            for name, target, orb in aspect_definitions:
                if abs(diff - target) <= orb:
                    synastry_aspects.append({
                        "boy_planet": bp,
                        "girl_planet": gp,
                        "aspect": name,
                        "diff": round(diff, 2),
                        "error": round(abs(diff - target), 2)
                    })

    positives = sum(1 for a in synastry_aspects if a["aspect"] in ["Trine", "Sextile", "Conjunction"])
    negatives = sum(1 for a in synastry_aspects if a["aspect"] in ["Square", "Opposition"])
    total_aspects = positives + negatives
    if total_aspects > 0:
        western_score_pct = round((positives / total_aspects) * 100)
    else:
        western_score_pct = 70

    # Chinese Bazi
    girl_chinese = compute_chinese_chart(b["date"], b["time"], b["tz"])
    girl_bazi = girl_chinese["calculations"]["bazi_pillars"]

    girl_animal = ""
    if "Zi" in girl_bazi["Year"] or "Rat" in girl_bazi["Year"]:
        girl_animal = "Rat"
        chinese_score = 75
        chinese_desc_en = "Rat & Rat (Same sign - generally friendly, shared understanding)"
        chinese_desc_ta = "எலி & எலி (ஒரே ராசி - பொதுவான இணக்கம்)"
    elif "Chou" in girl_bazi["Year"] or "Ox" in girl_bazi["Year"]:
        girl_animal = "Ox"
        chinese_score = 95
        chinese_desc_en = "Six Harmonies (Rat & Ox) - Soulmate union, highest compatibility."
        chinese_desc_ta = "ஆறு இணக்கங்கள் (எலி & எருது) - மிக உயர்ந்த இணக்கம்"
    elif "Chen" in girl_bazi["Year"] or "Dragon" in girl_bazi["Year"]:
        girl_animal = "Dragon"
        chinese_score = 90
        chinese_desc_en = "Three Harmonies (Rat & Dragon) - Harmonious affinity, creative and mutual growth."
        chinese_desc_ta = "மூன்று இணக்கங்கள் (எலி & டிராகன்) - பரஸ்பர வளர்ச்சி"
    else:
        girl_animal = "Other"
        chinese_score = 70
        chinese_desc_en = "Neutral zodiac compatibility."
        chinese_desc_ta = "சாதாரண சீன ராசி இணக்கம்."

    # Mayan
    girl_mayan = compute_mayan_chart(b["date"])
    girl_tzolkin = girl_mayan["calculations"]

    # Scores
    vedic_score_pct = (vedic_kuta.total[0] / 36) * 100
    num_score_pct = num_res["score_percent"]
    overall_score = round((vedic_score_pct + num_score_pct + chinese_score + western_score_pct) / 4)

    r_en = {
        "bride": b, "vedic_kuta": vedic_kuta, "boy_md": boy_md, "girl_md": girl_md, "num_res": num_res,
        "synastry_aspects": synastry_aspects, "pos_aspects": positives, "neg_aspects": negatives,
        "western_score": western_score_pct, "girl_bazi": girl_bazi, "boy_bazi": boy_bazi,
        "boy_bazi_raw": boy_chinese["calculations"]["bazi_details"], "girl_bazi_raw": girl_chinese["calculations"]["bazi_details"],
        "boy_west_planets": boy_west_planets, "girl_west_planets": girl_west_planets,
        "boy_west_asc": boy_west["calculations"]["ascendant"]["longitude"], "girl_west_asc": girl_west["calculations"]["ascendant"]["longitude"],
        "girl_animal": girl_animal, "chinese_score": chinese_score, "chinese_desc": chinese_desc_en,
        "girl_tzolkin": girl_tzolkin, "boy_tzolkin": boy_tzolkin, "overall_score": overall_score,
        "boy_west_signs": f"Sun in {boy_west_planets['Sun']['sign']}, Moon in {boy_west_planets['Moon']['sign']}, Ascendant in {boy_west['calculations']['ascendant']['sign']}",
        "girl_west_signs": f"Sun in {girl_west_planets['Sun']['sign']}, Moon in {girl_west_planets['Moon']['sign']}, Ascendant in {girl_west['calculations']['ascendant']['sign']}",
        "boy_moon_lon": boy_moon_lon,
        "girl_moon_lon": girl_moon_lon,
        "boy_lagna_en": boy_sid["planet_positions"]["Lagna"]["rasi"],
        "boy_lagna_ta": boy_sid["planet_positions"]["Lagna"]["rasi_tamil"],
        "girl_lagna_en": girl_sid["planet_positions"]["Lagna"]["rasi"],
        "girl_lagna_ta": girl_sid["planet_positions"]["Lagna"]["rasi_tamil"],
    }

    r_ta = {
        "bride": b, "vedic_kuta": vedic_kuta, "boy_md": boy_md, "girl_md": girl_md, "num_res": num_res,
        "synastry_aspects": synastry_aspects, "pos_aspects": positives, "neg_aspects": negatives,
        "western_score": western_score_pct, "girl_bazi": girl_bazi, "boy_bazi": boy_bazi,
        "boy_bazi_raw": boy_chinese["calculations"]["bazi_details"], "girl_bazi_raw": girl_chinese["calculations"]["bazi_details"],
        "boy_west_planets": boy_west_planets, "girl_west_planets": girl_west_planets,
        "boy_west_asc": boy_west["calculations"]["ascendant"]["longitude"], "girl_west_asc": girl_west["calculations"]["ascendant"]["longitude"],
        "girl_animal": girl_animal, "chinese_score": chinese_score, "chinese_desc": chinese_desc_ta,
        "girl_tzolkin": girl_tzolkin, "boy_tzolkin": boy_tzolkin, "overall_score": overall_score,
        "boy_west_signs": f"Sun in {boy_west_planets['Sun']['sign']}, Moon in {boy_west_planets['Moon']['sign']}, Ascendant in {boy_west['calculations']['ascendant']['sign']}",
        "girl_west_signs": f"Sun in {girl_west_planets['Sun']['sign']}, Moon in {girl_west_planets['Moon']['sign']}, Ascendant in {girl_west['calculations']['ascendant']['sign']}",
        "boy_moon_lon": boy_moon_lon,
        "girl_moon_lon": girl_moon_lon,
        "boy_lagna_en": boy_sid["planet_positions"]["Lagna"]["rasi"],
        "boy_lagna_ta": boy_sid["planet_positions"]["Lagna"]["rasi_tamil"],
        "girl_lagna_en": girl_sid["planet_positions"]["Lagna"]["rasi"],
        "girl_lagna_ta": girl_sid["planet_positions"]["Lagna"]["rasi_tamil"],
    }

    # Ensure output dirs
    os.makedirs(str(_ROOT / "reports"), exist_ok=True)
    
    # Save reports in workspace reports/
    pdf_path_en = _ROOT / "reports" / "Manoj_P_Viveka_Compatibility_Report_EN.pdf"
    pdf_path_ta = _ROOT / "reports" / "Manoj_P_Viveka_Compatibility_Report_TA.pdf"
    
    generate_pdf_en(r_en, str(pdf_path_en))
    print(f"Generated English PDF report: {pdf_path_en}")
    
    generate_pdf_ta(r_ta, str(pdf_path_ta))
    print(f"Generated Tamil PDF report: {pdf_path_ta}")

    print("\n--- COMPATIBILITY RESULTS ---")
    print(f"Vedic Kuta Score: {vedic_kuta.total[0]}/36")
    print(f"Vedic Kuta Match Status: {vedic_kuta.total[1]}")
    print(f"Numerology Match Score: {num_score_pct}%")
    print(f"Western Synastry Score: {western_score_pct}%")
    print(f"Chinese Zodiac Score: {chinese_score}% ({girl_animal})")
    print(f"OVERALL COMPATIBILITY SCORE: {overall_score}%")
    print("-----------------------------\n")

if __name__ == "__main__":
    main()
