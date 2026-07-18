"""Tara Chakra — Full 27-Nakshatra deity & gana analysis.

Source: BPHS Ch. 21 (Nakshatra effects), Sarvarth Chintamani.

Each nakshatra has:
  - Devata (presiding deity)
  - Gana (Deva/Manushya/Rakshasa temperament)
  - Yoni (animal type — 14 types)
  - Nadi (Adi/Madhya/Antya)
  - Mukha (Adhomukha/Tiryangmukha/Urdhwamukha — facing)
  - Symbols, body part, direction, color, gemstone

Used for:
  - Daily Muhurta selection (Tarabala from native's Janma nakshatra)
  - Compatibility (Yoni, Gana, Nadi for Kuta matching)
  - Deeper personality readings beyond pada-level
"""
import sys
sys.path.insert(0, ".")
from vedic_core import NAKSHATRAS, NAK_LORDS_27

NAKSHATRA_DETAILS = {
    "Ashwini":          {"deity":"Ashwini Kumaras (twin healers)","gana":"Deva","yoni":"Horse","nadi":"Adi","mukha":"Adhomukha","direction":"South","symbol":"Horse's head","body_part":"Knees, top of feet","color":"Red","element":"Earth"},
    "Bharani":          {"deity":"Yama (god of death)","gana":"Manushya","yoni":"Elephant","nadi":"Madhya","mukha":"Adhomukha","direction":"West","symbol":"Yoni","body_part":"Soles of feet","color":"Blood-red","element":"Fire"},
    "Krittika":         {"deity":"Agni (fire)","gana":"Rakshasa","yoni":"Goat","nadi":"Antya","mukha":"Tiryangmukha","direction":"North","symbol":"Razor/flame","body_part":"Eyebrows, hair","color":"White","element":"Fire"},
    "Rohini":           {"deity":"Brahma (creator)","gana":"Manushya","yoni":"Snake","nadi":"Antya","mukha":"Urdhwamukha","direction":"East","symbol":"Chariot/cart","body_part":"Forehead, ankles","color":"White","element":"Earth"},
    "Mrigashira":       {"deity":"Soma/Chandra (Moon)","gana":"Deva","yoni":"Snake","nadi":"Madhya","mukha":"Tiryangmukha","direction":"South","symbol":"Deer's head","body_part":"Eyes","color":"Silver-grey","element":"Air"},
    "Ardra":            {"deity":"Rudra (storm god)","gana":"Manushya","yoni":"Dog","nadi":"Madhya","mukha":"Adhomukha","direction":"North","symbol":"Teardrop, diamond","body_part":"Hair","color":"Green","element":"Water"},
    "Punarvasu":        {"deity":"Aditi (mother of gods)","gana":"Deva","yoni":"Cat","nadi":"Adi","mukha":"Tiryangmukha","direction":"North","symbol":"Bow & quiver","body_part":"Fingers, nose","color":"Lead","element":"Water"},
    "Pushya":           {"deity":"Brihaspati (Jupiter)","gana":"Deva","yoni":"Goat","nadi":"Madhya","mukha":"Urdhwamukha","direction":"East","symbol":"Cow's udder, lotus","body_part":"Mouth","color":"Reddish-brown","element":"Water"},
    "Ashlesha":         {"deity":"Naga (serpents)","gana":"Rakshasa","yoni":"Cat","nadi":"Antya","mukha":"Adhomukha","direction":"South","symbol":"Coiled serpent","body_part":"Joints, nails","color":"Red-brown","element":"Water"},
    "Magha":            {"deity":"Pitrs (ancestors)","gana":"Rakshasa","yoni":"Rat","nadi":"Antya","mukha":"Adhomukha","direction":"West","symbol":"Royal throne","body_part":"Nose","color":"Ivory","element":"Fire"},
    "Purva Phalguni":   {"deity":"Bhaga (luck)","gana":"Manushya","yoni":"Rat","nadi":"Madhya","mukha":"Adhomukha","direction":"North","symbol":"Front legs of bed","body_part":"Genitals","color":"Light brown","element":"Fire"},
    "Uttara Phalguni":  {"deity":"Aryaman (patronage)","gana":"Manushya","yoni":"Cow","nadi":"Adi","mukha":"Urdhwamukha","direction":"East","symbol":"Back legs of bed","body_part":"Lips","color":"Bright copper","element":"Fire"},
    "Hasta":            {"deity":"Savitar (Sun-creator)","gana":"Deva","yoni":"Buffalo","nadi":"Adi","mukha":"Urdhwamukha","direction":"North","symbol":"Hand, fist","body_part":"Hands","color":"Deep green","element":"Earth"},
    "Chitra":           {"deity":"Tvashtar (cosmic architect)","gana":"Rakshasa","yoni":"Tiger","nadi":"Madhya","mukha":"Urdhwamukha","direction":"East","symbol":"Bright jewel/pearl","body_part":"Forehead","color":"Black","element":"Fire"},
    "Swati":            {"deity":"Vayu (wind)","gana":"Deva","yoni":"Buffalo","nadi":"Antya","mukha":"Urdhwamukha","direction":"South","symbol":"Coral, sapphire","body_part":"Teeth","color":"Black","element":"Air"},
    "Vishakha":         {"deity":"Indragni (Indra+Agni)","gana":"Rakshasa","yoni":"Tiger","nadi":"Antya","mukha":"Adhomukha","direction":"East","symbol":"Forked branch","body_part":"Lower arms","color":"Golden","element":"Fire"},
    "Anuradha":         {"deity":"Mitra (friendship)","gana":"Deva","yoni":"Deer","nadi":"Madhya","mukha":"Tiryangmukha","direction":"South","symbol":"Lotus","body_part":"Heart, breast","color":"Red-brown","element":"Fire"},
    "Jyeshtha":         {"deity":"Indra (king of gods)","gana":"Rakshasa","yoni":"Deer","nadi":"Adi","mukha":"Adhomukha","direction":"West","symbol":"Earring, umbrella","body_part":"Right side of body","color":"Cream/light brown","element":"Air"},
    "Mula":             {"deity":"Nirriti (destruction)","gana":"Rakshasa","yoni":"Dog","nadi":"Adi","mukha":"Adhomukha","direction":"South","symbol":"Tied roots","body_part":"Feet","color":"Brownish-yellow","element":"Air"},
    "Purva Ashadha":    {"deity":"Apas (waters)","gana":"Manushya","yoni":"Monkey","nadi":"Madhya","mukha":"Adhomukha","direction":"East","symbol":"Fan, winnowing basket","body_part":"Thighs, behind","color":"Black","element":"Water"},
    "Uttara Ashadha":   {"deity":"Vishvedevas (universal gods)","gana":"Manushya","yoni":"Mongoose","nadi":"Antya","mukha":"Urdhwamukha","direction":"South","symbol":"Elephant tusk","body_part":"Calves","color":"Copper","element":"Earth"},
    "Shravana":         {"deity":"Vishnu (preserver)","gana":"Deva","yoni":"Monkey","nadi":"Antya","mukha":"Urdhwamukha","direction":"North","symbol":"Three footprints, ear","body_part":"Ears","color":"Light blue","element":"Air"},
    "Dhanishta":        {"deity":"Vasus (8 sky gods)","gana":"Rakshasa","yoni":"Lion","nadi":"Madhya","mukha":"Adhomukha","direction":"East","symbol":"Drum, flute","body_part":"Spine, dorsal area","color":"Silver-grey","element":"Ether"},
    "Shatabhisha":      {"deity":"Varuna (cosmic waters)","gana":"Rakshasa","yoni":"Horse","nadi":"Adi","mukha":"Adhomukha","direction":"West","symbol":"Empty circle, 100 stars","body_part":"Jaw, chin","color":"Blue-green","element":"Ether"},
    "Purva Bhadrapada": {"deity":"Aja Ekapada (one-footed serpent)","gana":"Manushya","yoni":"Lion","nadi":"Adi","mukha":"Urdhwamukha","direction":"East","symbol":"Front legs of cot","body_part":"Sides of body","color":"Silvery-grey","element":"Ether"},
    "Uttara Bhadrapada":{"deity":"Ahir Budhnya (cosmic serpent)","gana":"Manushya","yoni":"Cow","nadi":"Madhya","mukha":"Urdhwamukha","direction":"South","symbol":"Back legs of cot, twin serpent","body_part":"Sides of legs","color":"Purple","element":"Ether"},
    "Revati":           {"deity":"Pushan (nourisher)","gana":"Deva","yoni":"Elephant","nadi":"Antya","mukha":"Tiryangmukha","direction":"North","symbol":"Fish, drum","body_part":"Feet, abdomen","color":"Brown","element":"Earth"},
}


def get_nakshatra_full(nak_name):
    """Get all classical attributes of a nakshatra."""
    if nak_name not in NAKSHATRA_DETAILS:
        return None
    base = NAKSHATRA_DETAILS[nak_name]
    nak_idx = NAKSHATRAS.index(nak_name)
    return {
        "name": nak_name,
        "number": nak_idx + 1,
        "lord": NAK_LORDS_27[nak_idx],
        **base,
    }


def tara_chakra_summary(chart):
    """Full Tara Chakra reading from native's Janma Nakshatra."""
    nak = chart.get("janma_nakshatra")
    if not nak:
        return None
    full = get_nakshatra_full(nak)
    if not full:
        return None
    moon = chart["positions"]["Moon"]
    pada = moon.get("pada", 1)

    return {
        **full,
        "pada": pada,
        "interpretation": (
            f"Janma Nakshatra: {full['name']} (Pada {pada}). "
            f"Deity: {full['deity']}. "
            f"Gana: {full['gana']} (temperament). "
            f"Yoni: {full['yoni']} (sexual/instinctive type). "
            f"Nadi: {full['nadi']}. "
            f"Body part: {full['body_part']}. "
            f"Element: {full['element']}. "
            f"This is the deepest layer of the personality — operates below conscious thought."
        ),
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    tc = tara_chakra_summary(chart)
    print(f"=== TARA CHAKRA — Full Nakshatra Reading for {chart['name']} ===\n")
    if tc:
        for k, v in tc.items():
            if k == "interpretation":
                continue
            print(f"  {k:18s}: {v}")
        print(f"\n  {tc['interpretation']}")
