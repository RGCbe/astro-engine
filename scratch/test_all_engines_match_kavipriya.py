import os
import sys
import json
from pathlib import Path

# Add project root to path
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from engine.chart_builder import build_sidereal_chart
from engine.kuta import match_kuta, mangal_dosha
from engine.numerology_match import compute_compatibility
from engine.western_engine import compute_western_chart
from engine.chinese_engine import compute_chinese_chart
from engine.mayan_engine import compute_mayan_chart

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    
    # ── Birth Parameters ──
    boy_name = "Manoj Kumar"
    boy_date = "1996-05-25"
    boy_time = "20:25"
    boy_lat = 11.25
    boy_lon = 77.12
    boy_tz = 5.5

    girl_name = "Kavipriya"
    girl_date = "2001-10-19"
    girl_time = "05:28"
    girl_lat = 11.0168
    girl_lon = 76.9558
    girl_tz = 5.5

    print("Casting charts and running calculations across all engines...")

    # ── 1. VEDIC / TAMIL ENGINE ──
    boy_sid = build_sidereal_chart(1996, 5, 25, boy_time, boy_lat, boy_lon, boy_tz)
    girl_sid = build_sidereal_chart(2001, 10, 19, girl_time, girl_lat, girl_lon, girl_tz)
    
    boy_moon_lon = boy_sid["planet_positions"]["Moon"]["longitude"]
    girl_moon_lon = girl_sid["planet_positions"]["Moon"]["longitude"]
    
    vedic_kuta = match_kuta(boy_moon_lon, girl_moon_lon)
    
    boy_mangal_chart = {
        "lagna": boy_sid["asc_sid"],
        "positions": {p: d["longitude"] for p, d in boy_sid["planet_positions"].items()}
    }
    girl_mangal_chart = {
        "lagna": girl_sid["asc_sid"],
        "positions": {p: d["longitude"] for p, d in girl_sid["planet_positions"].items()}
    }
    boy_md = mangal_dosha(boy_mangal_chart)
    girl_md = mangal_dosha(girl_mangal_chart)

    # ── 2. NUMEROLOGY ENGINE ──
    num_res = compute_compatibility(boy_name, boy_date, girl_name, girl_date)

    # ── 3. WESTERN SYNAPSTRY ENGINE ──
    boy_west = compute_western_chart(boy_date, boy_time, boy_tz, boy_lat, boy_lon)
    girl_west = compute_western_chart(girl_date, girl_time, girl_tz, girl_lat, girl_lon)
    
    boy_west_planets = boy_west["calculations"]["planets"]
    girl_west_planets = girl_west["calculations"]["planets"]
    
    # Calculate Synastry Aspects
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

    # ── 4. CHINESE BAZI ENGINE ──
    boy_chinese = compute_chinese_chart(boy_date, boy_time, boy_tz)
    girl_chinese = compute_chinese_chart(girl_date, girl_time, girl_tz)
    
    boy_bazi = boy_chinese["calculations"]["bazi_pillars"]
    girl_bazi = girl_chinese["calculations"]["bazi_pillars"]
    
    # ── 5. MAYAN TZOLKIN ENGINE ──
    boy_mayan = compute_mayan_chart(boy_date)
    girl_mayan = compute_mayan_chart(girl_date)
    
    boy_tzolkin = boy_mayan["calculations"]
    girl_tzolkin = girl_mayan["calculations"]

    # ── GENERATE MARKDOWN REPORT ──
    report = []
    report.append("# Multi-Engine Celestial Compatibility Report")
    report.append(f"### Partners: **{boy_name}** & **{girl_name}**")
    report.append(f"Generated on: 2026-07-14\n")
    
    report.append("---")
    report.append("## 1. Vedic (Tamil Jyotisham) Compatibility")
    report.append(f"**Ashta-Kuta Score:** {vedic_kuta.total[0]} / 36 — **{vedic_kuta.verdict}**")
    report.append(f"- **Boy's Moon Rasi/Nakshatra:** {vedic_kuta.boy_moon} / {vedic_kuta.boy_nakshatra}")
    report.append(f"- **Girl's Moon Rasi/Nakshatra:** {vedic_kuta.girl_moon} / {vedic_kuta.girl_nakshatra}\n")
    
    report.append("| Kuta Factor | Boy | Girl | Score | Max | Indication |")
    report.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    report.append(f"| Nadi (Physiological) | Antya | Antya | {vedic_kuta.nadi[0]} | {vedic_kuta.nadi[1]} | ⚠️ Nadi Dosha (Same Nadi) |")
    report.append(f"| Bhakoot (Emotional) | Leo | Scorpio | {vedic_kuta.bhakoot[0]} | {vedic_kuta.bhakoot[1]} | Clean - 4-10 axis |")
    report.append(f"| Gana (Temperament) | Deva/Rakshasa | Deva/Rakshasa | {vedic_kuta.gana[0]} | {vedic_kuta.gana[1]} | Perfect Gana Alignment |")
    report.append(f"| Yoni (Intimacy) | Rat | Tiger | {vedic_kuta.yoni[0]} | {vedic_kuta.yoni[1]} | Neutral animal affinity |")
    report.append(f"| Graha Maitri (Mental) | Sun | Mars | {vedic_kuta.graha_maitri[0]} | {vedic_kuta.graha_maitri[1]} | Mutual Friends (Sun & Mars) |")
    report.append(f"| Tara (Destiny) | Magha | Vishakha | {vedic_kuta.tara[0]} | {vedic_kuta.tara[1]} | Beneficial Tara match |")
    report.append(f"| Vasya (Control) | Leo | Scorpio | {vedic_kuta.vasya[0]} | {vedic_kuta.vasya[1]} | Leo controls Scorpio (2/2) |")
    report.append(f"| Varna (Ego/Class) | Kshatriya | Brahmin | {vedic_kuta.varna[0]} | {vedic_kuta.varna[1]} | Mismatch (Girl varna > Boy varna) |")
    report.append(f"| **TOTAL** | | | **{vedic_kuta.total[0]}** | **36** | **{vedic_kuta.verdict}** |\n")

    report.append("### Sevvai Dosham (Mangal/Kuja Dosha) Assessment")
    report.append(f"- **{boy_name} (Boy):** " + ("Mangalik" if boy_md["is_mangalik"] else "NO DOSHAM") + f" (Mars in {boy_md.get('house_from_lagna')}th house from Lagna)")
    report.append(f"- **{girl_name} (Girl):** " + ("Mangalik" if girl_md["is_mangalik"] else "NO DOSHAM") + f" (Mars in {girl_md.get('house_from_lagna')}th house from Lagna)\n")
    
    report.append("---")
    report.append("## 2. Chaldean/Cheiro Numerology Compatibility")
    report.append(f"**Numerology Compatibility Score:** {num_res['score_percent']}% — **{num_res['verdict']}**")
    report.append(f"**Advice:** {num_res['advice']}\n")
    report.append(f"- **Boy:** Driver (Vidhi): {num_res['person1']['driver']} ({num_res['person1']['driver_planet']}) | Destiny (Bhagya): {num_res['person1']['destiny']} ({num_res['person1']['destiny_planet']})")
    report.append(f"- **Girl:** Driver (Vidhi): {num_res['person2']['driver']} ({num_res['person2']['driver_planet']}) | Destiny (Bhagya): {num_res['person2']['destiny']} ({num_res['person2']['destiny_planet']})\n")
    
    report.append("| Driver Relationship (Inner Personality) | Destiny Relationship (Life Path) |")
    report.append("| :--- | :--- |")
    report.append(f"| Boy -> Girl: **{num_res['driver_relation']['a_to_b']}** | Boy -> Girl: **{num_res['destiny_relation']['a_to_b']}** |")
    report.append(f"| Girl -> Boy: **{num_res['driver_relation']['b_to_a']}** | Girl -> Boy: **{num_res['destiny_relation']['b_to_a']}** |")
    report.append(f"| Driver Points: **{num_res['driver_relation']['points']} / 4** | Destiny Points: **{num_res['destiny_relation']['points']} / 4** |\n")

    report.append("---")
    report.append("## 3. Western Astrology Synastry")
    report.append(f"- **Boy's Western Signs:** Sun in **{boy_west_planets['Sun']['sign']}**, Moon in **{boy_west_planets['Moon']['sign']}**, Ascendant in **{boy_west['calculations']['ascendant']['sign']}**")
    report.append(f"- **Girl's Western Signs:** Sun in **{girl_west_planets['Sun']['sign']}**, Moon in **{girl_west_planets['Moon']['sign']}**, Ascendant in **{girl_west['calculations']['ascendant']['sign']}**\n")
    
    report.append("### Major Synastry Aspects (Orb <= 6°)")
    if synastry_aspects:
        report.append("| Boy Planet | Aspect | Girl Planet | Separation |")
        report.append("| :--- | :--- | :--- | :--- |")
        for asp in synastry_aspects:
            color = "🟢" if asp["aspect"] in ["Trine", "Sextile"] else ("🔴" if asp["aspect"] in ["Square", "Opposition"] else "🔵")
            report.append(f"| {asp['boy_planet']} | {color} **{asp['aspect']}** | {asp['girl_planet']} | {asp['diff']}° (orb {asp['error']}°) |")
    else:
        report.append("No major aspects found between major inner planets.")
    report.append("\n")

    report.append("---")
    report.append("## 4. Chinese Astrology (Bazi Pillars & Animal Sign Match)")
    report.append(f"- **{boy_name} Year Pillar:** {boy_bazi['Year']} (Year of the **Rat**)")
    report.append(f"- **{girl_name} Year Pillar:** {girl_bazi['Year']} (Year of the **Snake**)\n")
    
    report.append("### Animal Compatibility:")
    report.append("The **Rat** and the **Snake** have a neutral to friendly compatibility in the Chinese zodiac. The Rat's quick-witted nature adapts well to the Snake's deep, quiet wisdom, though communication requires conscious alignment to prevent emotional distance.\n")

    report.append("---")
    report.append("## 5. Mayan Tzolkin Match")
    report.append(f"- **Boy's Mayan Sign:** Tone **{boy_tzolkin['galactic_tone']['tone']}** ({boy_tzolkin['galactic_tone']['name']}) | Day Glyph: **{boy_tzolkin['day_glyph']['name']}** (Translation: {boy_tzolkin['day_glyph']['translation']} | Element: {boy_tzolkin['day_glyph']['element']})")
    report.append(f"- **Girl's Mayan Sign:** Tone **{girl_tzolkin['galactic_tone']['tone']}** ({girl_tzolkin['galactic_tone']['name']}) | Day Glyph: **{girl_tzolkin['day_glyph']['name']}** (Translation: {girl_tzolkin['day_glyph']['translation']} | Element: {girl_tzolkin['day_glyph']['element']})\n")

    report.append("---")
    report.append("## 6. Comprehensive Verdict & Summary")
    
    vedic_score_pct = (vedic_kuta.total[0] / 36) * 100
    num_score_pct = num_res["score_percent"]
    
    # Rat-Snake is neutral (approx 70%)
    chinese_score_pct = 70
    
    positives = sum(1 for a in synastry_aspects if a["aspect"] in ["Trine", "Sextile", "Conjunction"])
    negatives = sum(1 for a in synastry_aspects if a["aspect"] in ["Square", "Opposition"])
    total_aspects = positives + negatives
    if total_aspects > 0:
        western_score_pct = round((positives / total_aspects) * 100)
    else:
        western_score_pct = 70
        
    overall_score = round((vedic_score_pct + num_score_pct + chinese_score_pct + western_score_pct) / 4)
    
    report.append(f"### **GRAND COMPATIBILITY FIT: {overall_score}% — MODERATELY COMPATIBLE (REMEDIES REQUIRED)**")
    report.append("### Summary Breakdown:")
    report.append(f"1. **Vedic Compatibility (Tamil):** **{round(vedic_score_pct)}%** ({vedic_kuta.total[0]}/36 - {vedic_kuta.verdict})")
    report.append(f"2. **Numerology Compatibility:** **{num_score_pct}%** ({num_res['verdict']})")
    report.append(f"3. **Western Synastry:** **{western_score_pct}%** ({positives} positive aspects, {negatives} challenging aspects)")
    report.append(f"4. **Chinese Zodiac Compatibility:** **{chinese_score_pct}%** (Rat & Snake - Neutral Match)")
    report.append("\n**Key Recommendation:** This match has **Nadi Dosha** (Antya-Antya Nadi) which reduces physical compatibility in Vedic tradition and represents a core health concern. Numerology and Western metrics are moderate. Remedies for Nadi Dosha are recommended if you choose to proceed.")
    
    # Save report file
    report_content = "\n".join(report)
    os.makedirs(str(_ROOT / "reports"), exist_ok=True)
    report_path = _ROOT / "reports" / "Manoj_Kavipriya_Ultimate_All_Engine_Report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"\nSuccessfully generated compatibility report at {report_path}")
    print(f"Grand compatibility score calculated: {overall_score}%")

if __name__ == "__main__":
    main()
