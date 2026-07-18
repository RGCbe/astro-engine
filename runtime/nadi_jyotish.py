"""Nadi Jyotish — predictive astrology from Nadi tradition.

Source: Bhrigu Naadi Sangraha, Brighu Naadi, Chandra Kala Nadi.
Nadi tradition focuses on:
  - Specific planetary combinations (yogas at very fine granularity)
  - Bhava-specific predictions (each house/planet/sign cell)
  - Karmic readings — past lives encoded in planetary positions
  - Use of Pada-Nakshatra for finer prediction
"""
import sys
sys.path.insert(0, ".")

# Bhrigu Nadi key principles (simplified from extensive tradition)
BHRIGU_RULES = {
    "Sun_with_Saturn":     "Father had health/career struggle; native learns through paternal trials",
    "Sun_with_Rahu":       "Father non-traditional or absent; native pulled toward foreign authority structures",
    "Sun_with_Ketu":       "Father spiritual or detached; native has karmic father-themes from past life",
    "Moon_with_Saturn":    "Mother had hardship; melancholy emotional pattern, deep maturity through emotion",
    "Moon_with_Rahu":      "Mother foreign/unconventional; emotional anxiety from karmic mother-pattern",
    "Moon_with_Ketu":      "Mother spiritual/detached; intuitive depth, ancestral mother-line karma",
    "Mars_with_Saturn":    "Effort meets resistance; persistent struggle yields late mastery",
    "Mars_with_Rahu":      "Explosive energy; risk of accidents, foreign/unconventional aggression",
    "Venus_with_Saturn":   "Love is mature, sometimes painful; karmic relationship debt",
    "Venus_with_Rahu":     "Foreign/unconventional partner; intense attractions, addiction-risk",
    "Jupiter_with_Saturn": "Wisdom + discipline = late-life mastery; slow but profound dharmic development",
    "Jupiter_with_Rahu":   "Guru-Chandala dosha — unconventional teacher influence, possible cult-attraction",
    "Saturn_with_Rahu":    "Karmic burden multiplied; slow grinding mastery through suffering",
}

# Padma Nadi specific themes per Atmakaraka
ATMAKARAKA_THEMES = {
    "Sun":     "Soul mission: to lead, embody authority, discover the inner sovereign",
    "Moon":    "Soul mission: to nurture, master emotions, become emotionally mature",
    "Mars":    "Soul mission: to act with courage, master action without ego, become a warrior of truth",
    "Mercury": "Soul mission: to communicate, learn, become a teacher/translator/scholar",
    "Jupiter": "Soul mission: to teach dharma, expand wisdom, become a guru figure",
    "Venus":   "Soul mission: to love deeply, master beauty, integrate art and spirit",
    "Saturn":  "Soul mission: to serve through discipline, master patience, become a karmic servant of truth",
    "Rahu":    "Soul mission: to break old karmic patterns, embrace new realities, master the unconventional",
}


def nadi_analysis(chart):
    """Run Nadi-style analysis on chart."""
    pos = chart["positions"]

    # Detect key conjunctions for Nadi reading
    detected = []
    pairs_to_check = [
        ("Sun","Saturn"),("Sun","Rahu"),("Sun","Ketu"),
        ("Moon","Saturn"),("Moon","Rahu"),("Moon","Ketu"),
        ("Mars","Saturn"),("Mars","Rahu"),
        ("Venus","Saturn"),("Venus","Rahu"),
        ("Jupiter","Saturn"),("Jupiter","Rahu"),
        ("Saturn","Rahu"),
    ]
    for p1, p2 in pairs_to_check:
        if p1 in pos and p2 in pos and pos[p1]["rasi_idx"] == pos[p2]["rasi_idx"]:
            key = f"{p1}_with_{p2}"
            detected.append({
                "combination": f"{p1} + {p2} in {pos[p1]['rasi']}",
                "house": pos[p1]["house"],
                "reading": BHRIGU_RULES.get(key, "Significant karmic combination."),
            })

    # Atmakaraka theme
    from jaimini_full import chara_karakas_jaimini
    karakas = chara_karakas_jaimini(chart)
    ak_planet = karakas[0][1] if karakas else None
    ak_theme = ATMAKARAKA_THEMES.get(ak_planet, "Soul direction: explore karaka's archetype.")

    # Karmic verdict
    rahu_h = pos.get("Rahu", {}).get("house")
    ketu_h = pos.get("Ketu", {}).get("house")
    karmic_verdict = (
        f"The soul carries past-life skills in House {ketu_h} ({_house_theme(ketu_h)}), "
        f"is meant to grow through House {rahu_h} ({_house_theme(rahu_h)}) themes in this incarnation."
    )

    return {
        "atmakaraka_planet": ak_planet,
        "soul_mission": ak_theme,
        "karmic_verdict": karmic_verdict,
        "nadi_combinations": detected,
        "interpretation": (
            f"Atmakaraka ({ak_planet}) sets the soul's mission. {len(detected)} significant Nadi-level combinations detected. "
            f"Past karma: H{ketu_h}. Growth: H{rahu_h}."
        ),
    }


def _house_theme(h):
    return {1:"self/identity",2:"wealth/family",3:"siblings/courage",4:"home/mother",
            5:"children/creativity",6:"work/health",7:"spouse/partnership",8:"transformation",
            9:"dharma/father",10:"career/status",11:"gains/network",12:"loss/foreign/spirituality"}.get(h, "?")


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    result = nadi_analysis(chart)
    print(f"=== NADI JYOTISH for {chart['name']} ===\n")
    print(f"Atmakaraka:    {result['atmakaraka_planet']}")
    print(f"Soul Mission:  {result['soul_mission']}\n")
    print(f"Karmic Verdict: {result['karmic_verdict']}\n")
    print(f"NADI COMBINATIONS ({len(result['nadi_combinations'])}):")
    for n in result["nadi_combinations"]:
        print(f"\n  {n['combination']} in House {n['house']}")
        print(f"    Reading: {n['reading']}")
