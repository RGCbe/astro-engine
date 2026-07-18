import sys, json
sys.path.insert(0, '.')

books_to_check = [
    # Pure astronomy / mathematics
    ("ASTRONOMICAL", [
        "Aryabhatiya_v1_gemma",
        "Aryabhatiya_v2_gemma",
        "Surya_Siddhanta_gemma",
        "Vedanga_Jyotisa_gemma",
        "Pancha_Siddhantika_gemma",
        "Pancha_Siddhantika_cerebras",
        "Pancha_Siddhantika_nvidia",
        "Pancha_Siddhantika_sambanova",
    ]),
    # Muhurtha / Prashna — different domains
    ("MUHURTHA/PRASHNA/HORARY", [
        "Muhurtha_Chintamani_gemma",
        "Prashna_Marga_gemma",
        "Prashna_Marga_deep",
    ]),
    # Other dead books
    ("OTHER DEAD", [
        "Yavanajataka_1_gemma",
        "Yavanajataka_2_gemma",
        "Brighu_Naadi_Sangraha_gemma",
        "Krishneeyam_gemma",
    ]),
]

for category, books in books_to_check:
    print(f"\n{'='*80}")
    print(f"CATEGORY: {category}")
    print(f"{'='*80}")
    for book in books:
        try:
            with open(f"gemma_extractions/{book}.json", encoding="utf-8", errors="replace") as f:
                data = json.load(f)
            rules = data.get("rules", [])
            print(f"\n  [{book}] — {len(rules)} rules")
            for r in rules[:3]:
                cats = r.get("categories", [])
                text = (r.get("english_translation") or "")[:200]
                print(f"    cats={cats}")
                print(f"    text: {text}")
        except FileNotFoundError:
            print(f"  [{book}] NOT FOUND")
