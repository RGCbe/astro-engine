from runtime.tamil_translations import (
    PLANETS_TA, RASIS_TA, NAKSHATRAS_TA, WEEKDAYS_TA, TITHIS_TA, PAKSHA_TA,
    KARANAS_TA, YOGAS_PANCH_TA, HOUSES_TA, SECTION_HEADERS, LABELS,
    MD_THEME_TA, MD_EXPECT_TA, EVENT_PLAIN_TA, YOGA_PLAIN_TA
)
from runtime.hindi_translations import (
    PLANETS_HI, RASIS_HI, NAKSHATRAS_HI, WEEKDAYS_HI, TITHIS_HI, PAKSHA_HI,
    KARANAS_HI, YOGAS_PANCH_HI, HOUSES_HI, SECTION_HEADERS_HI, LABELS_HI,
    MD_THEME_HI, MD_EXPECT_HI, EVENT_PLAIN_HI, YOGA_PLAIN_HI
)

def translate_response_data(res: dict, lang: str) -> dict:
    if lang not in ("ta", "hi"):
        return res
    
    if lang == "ta":
        planets = PLANETS_TA
        rasis = RASIS_TA
        nakshatras = NAKSHATRAS_TA
        weekdays = WEEKDAYS_TA
        tithis = TITHIS_TA
        pakshas = PAKSHA_TA
        karanas = KARANAS_TA
        yogas_panch = YOGAS_PANCH_TA
        yoga_plain = YOGA_PLAIN_TA
    else:
        planets = PLANETS_HI
        rasis = RASIS_HI
        nakshatras = NAKSHATRAS_HI
        weekdays = WEEKDAYS_HI
        tithis = TITHIS_HI
        pakshas = PAKSHA_HI
        karanas = KARANAS_HI
        yogas_panch = YOGAS_PANCH_HI
        yoga_plain = YOGA_PLAIN_HI

    # Translate lagnam, rasis, nakshatras
    res["lagnam"] = rasis.get(res["lagnam"], res["lagnam"])
    res["navamsa_lagnam"] = rasis.get(res["navamsa_lagnam"], res["navamsa_lagnam"])
    res["arudha_lagna"] = rasis.get(res["arudha_lagna"], res["arudha_lagna"])
    res["janma_rasi"] = rasis.get(res["janma_rasi"], res["janma_rasi"])
    res["janma_rasi_tamil"] = rasis.get(res["janma_rasi"], res["janma_rasi"])
    res["janma_nakshatra"] = nakshatras.get(res["janma_nakshatra"], res["janma_nakshatra"])
    
    # Panchangam
    p = res["panchangam"]
    p["vara"] = weekdays.get(p["vara"], p["vara"])
    p["yoga"] = yogas_panch.get(p["yoga"], p["yoga"])
    p["karana"] = karanas.get(p["karana"], p["karana"])
    p["nakshatra"] = nakshatras.get(p["nakshatra"], p["nakshatra"])
    
    # Translate Tithi
    orig_tithi = p["tithi"]
    for en_tithi, loc_tithi in tithis.items():
        if en_tithi in orig_tithi:
            pak_suffix = ""
            if "Shukla" in orig_tithi:
                pak_suffix = f" ({pakshas.get('Shukla', 'Shukla')})"
            elif "Krishna" in orig_tithi:
                pak_suffix = f" ({pakshas.get('Krishna', 'Krishna')})"
            p["tithi"] = f"{loc_tithi}{pak_suffix}"
            break

    # Dasha
    res["current_dasha"] = planets.get(res["current_dasha"], res["current_dasha"])
    res["current_antardasha"] = planets.get(res["current_antardasha"], res["current_antardasha"])
    res["current_pratyantar_dasha"] = planets.get(res["current_pratyantar_dasha"], res["current_pratyantar_dasha"])
    res["current_yogini_dasha"] = planets.get(res["current_yogini_dasha"], res["current_yogini_dasha"])
    res["current_yogini_lord"] = planets.get(res["current_yogini_lord"], res["current_yogini_lord"])

    # Yogas
    for y in res["detected_yogas"]:
        for en_y, loc_y in yoga_plain.items():
            if en_y in y["name"]:
                y["description"] = loc_y
                break

    # House Predictions
    for hp in res["house_predictions"]:
        hp["planet"] = planets.get(hp["planet"], hp["planet"])
        hp["rasi"] = rasis.get(hp["rasi"], hp["rasi"])
        hp["nakshatra"] = nakshatras.get(hp["nakshatra"], hp["nakshatra"])
        hp["conjunction_with"] = [planets.get(cp, cp) for cp in hp["conjunction_with"]]

    # Synthesis
    dasha_loc = res["current_dasha"]
    antar_loc = res["current_antardasha"]
    if lang == "ta":
        res["synthesis"]["short_summary"] = f"நீங்கள் தற்போது {dasha_loc} மகா தசையில் இருக்கிறீர்கள், இதில் {antar_loc} உப தசை (புத்தி) நடக்கிறது."
        res["synthesis"]["action_advice"] = f"உங்கள் தசை அதிபதி {dasha_loc} ஆகும். இந்த காலகட்டத்திற்கான தகுந்த பயிற்சிகள் மற்றும் ஆலோசனைகளை பின்பற்றவும்."
    else:
        res["synthesis"]["short_summary"] = f"आप वर्तमान में {dasha_loc} की महादशा और {antar_loc} की अन्तर्दशा में हैं।"
        res["synthesis"]["action_advice"] = f"आपके दशा अधिपति {dasha_loc} हैं। सकारात्मक परिणामों के लिए तदनुसार उपाय करें।"

    return res
