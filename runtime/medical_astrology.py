"""Medical Astrology — body part, disease, surgery timing per chart.

Source: BPHS Ch. 88 (Diseases), Phaladeepika, Hora Sara, Sarvarth Chintamani.
"""
import sys
sys.path.insert(0, ".")

# Body parts per house (Kala Purusha)
HOUSE_BODY = {
    1: "head, face, brain, hair, complexion",
    2: "right eye, throat, neck, voice, teeth, mouth",
    3: "ears (right), shoulders, arms (right), upper chest",
    4: "chest, breasts, lungs, heart (emotional), heart (physical)",
    5: "stomach, upper abdomen, pancreas, liver",
    6: "navel, intestines, large bowel, kidneys, lower abdomen, illness/digestion",
    7: "lower abdomen, lumbar region, kidneys (urinary system), genitals",
    8: "reproductive organs, pelvic area, sexual organs, anus, urethra",
    9: "thighs, hips, sciatic nerves",
    10: "knees, joints, knee caps, bones",
    11: "calves, ankles (right), shin",
    12: "feet, toes, lymphatic system, left eye, sleep",
}

# Disease tendency per planet (BPHS Ch. 88)
PLANET_DISEASES = {
    "Sun":     "fever, heart, eye (right), bones, headaches, blood pressure",
    "Moon":    "mental, fluid imbalances, lung issues, blood, anemia, depression",
    "Mars":    "blood disorders, accidents, fevers, surgery, infections, anger-related",
    "Mercury": "skin, nervous system, speech impediments, mental confusion",
    "Jupiter": "liver, pancreas, diabetes, weight gain, fat-tissue, ear (left)",
    "Venus":   "kidneys, urinary system, reproductive system, throat, diabetes",
    "Saturn":  "chronic conditions, bones, joints, paralysis, slow-healing, dental",
    "Rahu":    "obscure/rare diseases, poison, ulcers, addictions, mental afflictions",
    "Ketu":    "infections, parasites, sudden illness, allergies, cuts/wounds",
}

# Body type per Lagna (Ayurvedic doshas)
LAGNA_DOSHA = {
    "Aries":     "Pitta-dominant — fiery, prone to inflammation, headaches, BP",
    "Taurus":    "Kapha-dominant — sturdy build, prone to weight, throat issues",
    "Gemini":    "Vata-dominant — quick metabolism, nervous-system sensitive",
    "Cancer":    "Kapha-Vata — emotional eating, stomach issues, fluid retention",
    "Leo":       "Pitta-dominant — strong heart, prone to BP, eye issues",
    "Virgo":     "Vata-Pitta — sensitive digestion, anxiety, perfectionist stress",
    "Libra":     "Vata-Kapha — kidney/urinary, balance issues, diabetes-prone",
    "Scorpio":   "Pitta-Kapha — reproductive, intense emotions, hormonal",
    "Sagittarius":"Pitta — liver, hips, sciatica, accidents in sports",
    "Capricorn": "Vata-Kapha — joints, bones, depression, slow metabolism",
    "Aquarius":  "Vata — circulatory, ankles, nervous-system",
    "Pisces":    "Kapha — feet, lymph, edema, sleep disorders",
}


def medical_analysis(chart):
    pos = chart["positions"]
    lagna = chart["lagna"]
    out = {
        "constitution": LAGNA_DOSHA.get(lagna, "?"),
        "vulnerable_houses": [],
        "vulnerable_planets": [],
        "disease_predispositions": [],
        "body_areas_sensitive": [],
    }

    # Find afflicted houses (6/8/12 occupants, malefics, etc.)
    MALEFICS = ["Sun","Mars","Saturn","Rahu","Ketu"]
    for h in [1, 6, 8, 12]:
        occ = [p for p, pd in pos.items() if pd["house"] == h]
        malefics_here = [p for p in occ if p in MALEFICS]
        if malefics_here:
            out["vulnerable_houses"].append({
                "house": h,
                "body_area": HOUSE_BODY[h],
                "malefics": malefics_here,
            })

    # Per-planet predispositions
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        if p not in pos: continue
        h = pos[p]["house"]
        if h in [6, 8, 12]:
            out["disease_predispositions"].append({
                "planet": p,
                "house": h,
                "diseases": PLANET_DISEASES[p],
                "affected_area": HOUSE_BODY[h],
            })

    # Sensitive body areas (overall)
    affected_houses = set(v["house"] for v in out["vulnerable_houses"]) | set(d["house"] for d in out["disease_predispositions"])
    for h in affected_houses:
        out["body_areas_sensitive"].append(HOUSE_BODY[h])

    out["interpretation"] = (
        f"Constitution: {out['constitution']}. "
        f"{len(out['vulnerable_houses'])} vulnerable house(s); "
        f"{len(out['disease_predispositions'])} disease predisposition(s). "
        f"Sensitive areas: {', '.join(set(out['body_areas_sensitive']))[:200]}."
    )
    return out


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    result = medical_analysis(chart)
    print(f"=== MEDICAL ASTROLOGY for {chart['name']} ===\n")
    print(f"Constitution: {result['constitution']}\n")
    print("Vulnerable houses:")
    for v in result["vulnerable_houses"]:
        print(f"  H{v['house']}: {v['body_area']}")
        print(f"        Malefics here: {', '.join(v['malefics'])}")
    print("\nDisease predispositions:")
    for d in result["disease_predispositions"]:
        print(f"  {d['planet']} (in H{d['house']}): {d['diseases']}")
        print(f"        Affects: {d['affected_area']}")
    print(f"\nReading: {result['interpretation']}")
