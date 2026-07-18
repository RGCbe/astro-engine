import os
from pathlib import Path

EXCLUDED_BOOKS = {
    "Aryabhatiya_v1_gemma", "Aryabhatiya_v2_gemma", "Surya_Siddhanta_gemma",
    "Vedanga_Jyotisa_gemma", "Pancha_Siddhantika_gemma", "Pancha_Siddhantika_cerebras",
    "Pancha_Siddhantika_nvidia", "Pancha_Siddhantika_sambanova", "Pancha_Siddhantika_google",
    "Pancha_Siddhantika_groq", "BPHS1_gemma", "BPHS_Vol1_gemma", "BPHS2_gemma",
    "Phaladeepika_gemma", "Sarvartha_Chintamani_gemma", "Hora_Sara_gemma",
    "Saravali_gemma", "Bhrigu_Samhita_gemma", "Brihat_Jataka_gemma",
    "Brihat_Jataka_Sastri_gemma", "Jaimini_Sutras_gemma", "Jataka_Parijata_gemma",
    "Bhavartha_Ratnakara_Raman_gemma", "Muhurtha_Chintamani_gemma",
    "BPHS_Sharma_Vol1_gemma", "Lal_Kitab_gemma", "KP_Reader_gemma",
    "Prashna_Marga_gemma", "Surya_Siddhanta_gemma",
}

def main():
    gemma_dir = Path("gemma_extractions")
    files = list(gemma_dir.glob("*.json"))
    
    books = {}
    for f in files:
        stem = f.stem
        if stem.endswith("_deep"):
            base = stem[:-5]
            books.setdefault(base, {})["deep"] = f
        elif stem.endswith("_gemma"):
            base = stem[:-6]
            books.setdefault(base, {})["gemma"] = f
        else:
            books.setdefault(stem, {})["other"] = f

    print("Books with only _gemma (and not excluded):")
    for base, versions in books.items():
        gemma_key = f"{base}_gemma"
        if "gemma" in versions and "deep" not in versions and gemma_key not in EXCLUDED_BOOKS:
            print(f"  - {base} ({versions['gemma'].name})")

if __name__ == "__main__":
    main()
