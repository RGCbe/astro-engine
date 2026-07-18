import json

books_to_audit = [
    "Aryabhatiya_v1_gemma",
    "Surya_Siddhanta_gemma", 
    "Pancha_Siddhantika_gemma",
    "Vedanga_Jyotisa_gemma",
    "Prashna_Marga_gemma",
    "Muhurtha_Chintamani_gemma",
    "Yavanajataka_2_gemma",
    "Brighu_Naadi_Sangraha_gemma",
    "Brihat_Parashara_v2_gemma",
    "BPHS1_gemma",
]

for book in books_to_audit:
    try:
        with open(f"gemma_extractions/{book}.json", encoding="utf-8", errors="replace") as f:
            data = json.load(f)
    except FileNotFoundError:
        continue

    rules = data.get("rules", [])
    chunks = data.get("chunks", [])
    chunk_rules = []
    for chunk in chunks:
        chunk_rules.extend(chunk.get("predictive_rules", []))

    total = len(rules) + len(chunk_rules)
    print(f"\n[{book}] flat_rules={len(rules)} chunk_rules={len(chunk_rules)} total={total}")
    
    # Show samples
    samples = list(rules[:2]) + list(chunk_rules[:2])
    for r in samples:
        trigger = str(r.get("trigger", r.get("original_text", "")))[:100]
        effect  = str(r.get("effect", r.get("english_translation", "")))[:150]
        cats    = r.get("categories", [])
        print(f"  cats={cats}")
        print(f"  trigger: {trigger}")
        print(f"  effect:  {effect}")
