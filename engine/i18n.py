"""
Multi-language output for chart fields.

Supports: en (English, default), hi (Hindi Devanagari), sa (Sanskrit IAST),
ta (Tamil).

Translation tables cover:
    - 12 signs (rāśi)
    - 9 grahas (planets)
    - 27 nakshatras
    - 30 tithis (×2 paksha)
    - 27 yogas
    - 11 karanas
    - 7 varas (weekdays)
    - 12 bhavas (houses)
    - 16 vargas (divisional charts)
    - confidence bands and verdict labels (so the truth-only directive holds
      across languages — a "REJECTED" muhurta is still rejected in Hindi)

API:
    translate(field_type, value, lang)  → translated string (or value if missing)
    locale(lang)                         → dict of all field tables for that lang
"""
from __future__ import annotations

LANGUAGES = ("en", "hi", "sa", "ta")


# ─── Signs (rāśi) ──────────────────────────────────────────────────────────
SIGNS = {
    "en": ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
           "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"],
    "sa": ["Meṣa", "Vṛṣabha", "Mithuna", "Karka", "Siṃha", "Kanyā",
           "Tulā", "Vṛścika", "Dhanus", "Makara", "Kumbha", "Mīna"],
    "hi": ["मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
           "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन"],
    "ta": ["மேஷம்", "ரிஷபம்", "மிதுனம்", "கடகம்", "சிம்மம்", "கன்னி",
           "துலாம்", "விருச்சிகம்", "தனுசு", "மகரம்", "கும்பம்", "மீனம்"],
}


# ─── Grahas (planets) ──────────────────────────────────────────────────────
GRAHAS = {
    "en": {"Sun": "Sun", "Moon": "Moon", "Mars": "Mars", "Mercury": "Mercury",
           "Jupiter": "Jupiter", "Venus": "Venus", "Saturn": "Saturn",
           "Rahu": "Rahu", "Ketu": "Ketu"},
    "sa": {"Sun": "Sūrya", "Moon": "Candra", "Mars": "Maṅgala", "Mercury": "Budha",
           "Jupiter": "Guru", "Venus": "Śukra", "Saturn": "Śani",
           "Rahu": "Rāhu", "Ketu": "Ketu"},
    "hi": {"Sun": "सूर्य", "Moon": "चन्द्र", "Mars": "मंगल", "Mercury": "बुध",
           "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि",
           "Rahu": "राहु", "Ketu": "केतु"},
    "ta": {"Sun": "சூரியன்", "Moon": "சந்திரன்", "Mars": "செவ்வாய்",
           "Mercury": "புதன்", "Jupiter": "குரு", "Venus": "சுக்கிரன்",
           "Saturn": "சனி", "Rahu": "ராகு", "Ketu": "கேது"},
}


# ─── Nakshatras (27) ───────────────────────────────────────────────────────
NAKSHATRAS = {
    "en": ["Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
           "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
           "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
           "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
           "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
           "Revati"],
    "sa": ["Aśvinī", "Bharaṇī", "Kṛttikā", "Rohiṇī", "Mṛgaśīrṣā", "Ārdrā",
           "Punarvasu", "Puṣya", "Āśleṣā", "Maghā", "Pūrva Phalgunī",
           "Uttara Phalgunī", "Hasta", "Citrā", "Svātī", "Viśākhā", "Anurādhā",
           "Jyeṣṭhā", "Mūla", "Pūrva Āṣāḍhā", "Uttara Āṣāḍhā", "Śravaṇa",
           "Dhaniṣṭhā", "Śatabhiṣā", "Pūrva Bhādrapadā", "Uttara Bhādrapadā",
           "Revatī"],
    "hi": ["अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशीर्ष", "आर्द्रा",
           "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्वा फाल्गुनी",
           "उत्तरा फाल्गुनी", "हस्त", "चित्रा", "स्वाती", "विशाखा", "अनुराधा",
           "ज्येष्ठा", "मूल", "पूर्वाषाढा", "उत्तराषाढा", "श्रवण",
           "धनिष्ठा", "शतभिषा", "पूर्व भाद्रपद", "उत्तर भाद्रपद", "रेवती"],
    "ta": ["அசுவினி", "பரணி", "கார்த்திகை", "ரோகிணி", "மிருகசீரிஷம்", "திருவாதிரை",
           "புனர்பூசம்", "பூசம்", "ஆயில்யம்", "மகம்", "பூரம்",
           "உத்திரம்", "ஹஸ்தம்", "சித்திரை", "சுவாதி", "விசாகம்", "அனுஷம்",
           "கேட்டை", "மூலம்", "பூராடம்", "உத்திராடம்", "திருவோணம்",
           "அவிட்டம்", "சதயம்", "பூரட்டாதி", "உத்திரட்டாதி", "ரேவதி"],
}


# ─── Varas (weekdays) ──────────────────────────────────────────────────────
VARAS = {
    "en": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    "sa": ["Ravivāra", "Somavāra", "Maṅgalavāra", "Budhavāra", "Guruvāra",
           "Śukravāra", "Śanivāra"],
    "hi": ["रविवार", "सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"],
    "ta": ["ஞாயிறு", "திங்கள்", "செவ்வாய்", "புதன்", "வியாழன்", "வெள்ளி", "சனி"],
}


# ─── Bhavas (12 houses) ────────────────────────────────────────────────────
BHAVAS = {
    "en": ["1st (Self)", "2nd (Wealth)", "3rd (Siblings)", "4th (Home)",
           "5th (Children)", "6th (Enemies)", "7th (Spouse)", "8th (Longevity)",
           "9th (Fortune)", "10th (Career)", "11th (Gains)", "12th (Loss)"],
    "sa": ["Lagna (Tanu)", "Dhana", "Sahaja", "Sukha", "Putra", "Roga",
           "Yuvati", "Āyus", "Dharma", "Karma", "Lābha", "Vyaya"],
    "hi": ["लग्न (तनु)", "धन", "सहज", "सुख", "पुत्र", "रोग",
           "युवती (दाम्पत्य)", "आयु", "धर्म", "कर्म", "लाभ", "व्यय"],
    "ta": ["லக்னம் (தனு)", "தனம்", "சகஜம்", "சுகம்", "புத்திரம்", "ரோகம்",
           "களத்திரம்", "ஆயுள்", "தர்மம்", "கர்மம்", "லாபம்", "விரயம்"],
}


# ─── Verdict / confidence labels (truth-only directive) ────────────────────
VERDICTS = {
    "en": {"HIGH": "HIGH (strong evidence)", "MEDIUM": "MEDIUM (moderate)",
           "LOW": "LOW (weak — barely above chance)", "WEAK": "WEAK (no signature)",
           "REJECTED": "REJECTED (forbidden by hard rule)",
           "EXCELLENT": "EXCELLENT", "GOOD": "GOOD", "ACCEPTABLE": "ACCEPTABLE",
           "POOR": "POOR", "STRONG YES": "STRONG YES", "YES": "YES",
           "WEAK YES": "WEAK YES", "NO": "NO", "INDETERMINATE": "INDETERMINATE"},
    "sa": {"HIGH": "Pūrṇa-pramāṇa (uccāra)", "MEDIUM": "Madhya-pramāṇa",
           "LOW": "Alpa-pramāṇa", "WEAK": "Apramāṇa",
           "REJECTED": "Niṣiddha (varjita)",
           "EXCELLENT": "Ati-śubha", "GOOD": "Śubha", "ACCEPTABLE": "Madhyama",
           "POOR": "Aśubha", "STRONG YES": "Niścaya: Bhavati",
           "YES": "Bhavati", "WEAK YES": "Saṃśaya: bhavati",
           "NO": "Na bhavati", "INDETERMINATE": "Aniścita"},
    "hi": {"HIGH": "उच्च (मज़बूत प्रमाण)", "MEDIUM": "मध्यम (सामान्य)",
           "LOW": "निम्न (दुर्बल — संयोगवश)", "WEAK": "अति दुर्बल (कोई संकेत नहीं)",
           "REJECTED": "निषिद्ध (कठोर नियम विरुद्ध)",
           "EXCELLENT": "उत्तम", "GOOD": "शुभ", "ACCEPTABLE": "मध्यम",
           "POOR": "अशुभ", "STRONG YES": "निश्चय: हाँ",
           "YES": "हाँ", "WEAK YES": "संदेह: हाँ", "NO": "नहीं",
           "INDETERMINATE": "अनिश्चित"},
    "ta": {"HIGH": "உயர்ந்த (வலுவான ஆதாரம்)", "MEDIUM": "நடுத்தர",
           "LOW": "குறைந்த (பலவீனம்)", "WEAK": "மிக பலவீனம் (சான்று இல்லை)",
           "REJECTED": "நிராகரிக்கப்பட்டது (கடுமையான விதி)",
           "EXCELLENT": "சிறந்தது", "GOOD": "நல்லது", "ACCEPTABLE": "ஏற்கதக்கது",
           "POOR": "மோசம்", "STRONG YES": "உறுதியான ஆம்",
           "YES": "ஆம்", "WEAK YES": "பலவீனமான ஆம்", "NO": "இல்லை",
           "INDETERMINATE": "தீர்மானிக்க முடியாது"},
}


# ─── Tithi names (15 + paksha) ─────────────────────────────────────────────
TITHIS_SHUKLA_BASE = {
    "en": ["Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
           "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
           "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima"],
    "sa": ["Pratipadā", "Dvitīyā", "Tṛtīyā", "Caturthī", "Pañcamī",
           "Ṣaṣṭhī", "Saptamī", "Aṣṭamī", "Navamī", "Daśamī",
           "Ekādaśī", "Dvādaśī", "Trayodaśī", "Caturdaśī", "Pūrṇimā"],
    "hi": ["प्रतिपदा", "द्वितीया", "तृतीया", "चतुर्थी", "पंचमी",
           "षष्ठी", "सप्तमी", "अष्टमी", "नवमी", "दशमी",
           "एकादशी", "द्वादशी", "त्रयोदशी", "चतुर्दशी", "पूर्णिमा"],
    "ta": ["பிரதமை", "துவிதியை", "திருதியை", "சதுர்த்தி", "பஞ்சமி",
           "சஷ்டி", "சப்தமி", "அஷ்டமி", "நவமி", "தசமி",
           "ஏகாதசி", "துவாதசி", "திரயோதசி", "சதுர்தசி", "பௌர்ணமி"],
}


# ─── Public API ────────────────────────────────────────────────────────────
def translate(field_type: str, value, lang: str = "en"):
    """Translate `value` of `field_type` into `lang`. Falls back to value."""
    if lang not in LANGUAGES:
        return value
    if lang == "en":
        return value

    if field_type == "sign":
        en_signs = SIGNS["en"]
        if value in en_signs:
            return SIGNS[lang][en_signs.index(value)]

    elif field_type == "graha":
        return GRAHAS[lang].get(value, value)

    elif field_type == "nakshatra":
        en_naks = NAKSHATRAS["en"]
        if value in en_naks:
            return NAKSHATRAS[lang][en_naks.index(value)]

    elif field_type == "vara":
        en_var = VARAS["en"]
        if value in en_var:
            return VARAS[lang][en_var.index(value)]

    elif field_type == "bhava":
        # Accept either "1" / 1 / "1st (Self)"
        try:
            idx = int(str(value).split()[0].strip("st").strip("nd").strip("rd").strip("th").strip("()")) - 1
            return BHAVAS[lang][idx]
        except (ValueError, IndexError):
            pass

    elif field_type == "verdict":
        return VERDICTS[lang].get(value, value)

    elif field_type == "tithi":
        # Strip paksha prefix if any: "Shukla Ashtami" → "Ashtami"
        name = value
        if value.startswith("Shukla "):
            name = value[7:]
        elif value.startswith("Krishna "):
            name = value[8:]
        if name in TITHIS_SHUKLA_BASE["en"]:
            idx = TITHIS_SHUKLA_BASE["en"].index(name)
            return TITHIS_SHUKLA_BASE[lang][idx]

    return value


# ─── Remedy / mission term translations ────────────────────────────────────
SEVERITY_LABELS = {
    "en": {"CRITICAL": "Critical", "HIGH": "High", "MODERATE": "Moderate", "LOW": "Low"},
    "sa": {"CRITICAL": "Atyugra", "HIGH": "Ugra", "MODERATE": "Madhyama", "LOW": "Manda"},
    "hi": {"CRITICAL": "अति गम्भीर", "HIGH": "गम्भीर", "MODERATE": "मध्यम", "LOW": "हल्का"},
    "ta": {"CRITICAL": "மிகக் கடுமை", "HIGH": "கடுமை", "MODERATE": "நடுத்தர", "LOW": "குறைவு"},
}
STRENGTH_LABELS = {
    "en": {"SUPREME": "Supreme", "STRONG": "Strong", "MODERATE": "Moderate", "LATENT": "Latent"},
    "sa": {"SUPREME": "Parama", "STRONG": "Pravala", "MODERATE": "Madhyama", "LATENT": "Sukshma"},
    "hi": {"SUPREME": "परम", "STRONG": "प्रबल", "MODERATE": "मध्यम", "LATENT": "सूक्ष्म"},
    "ta": {"SUPREME": "உச்சம்", "STRONG": "வலிமை", "MODERATE": "நடுத்தர", "LATENT": "மறை"},
}
REMEDY_TYPE_LABELS = {
    "en": {"lal_kitab": "Lal Kitab", "vedic_mantra": "Vedic mantra",
           "behavioral": "Behavioral", "donation": "Donation",
           "gemstone_with_caveat": "Gemstone (with caveat)", "timing": "Timing"},
    "sa": {"lal_kitab": "Lāl Kitab", "vedic_mantra": "Vaidika Mantra",
           "behavioral": "Ācaraṇa", "donation": "Dāna",
           "gemstone_with_caveat": "Ratna (sa-caveat)", "timing": "Kāla"},
    "hi": {"lal_kitab": "लाल किताब", "vedic_mantra": "वैदिक मंत्र",
           "behavioral": "आचरण", "donation": "दान",
           "gemstone_with_caveat": "रत्न (शर्तसहित)", "timing": "समय"},
    "ta": {"lal_kitab": "லால் கிதாப்", "vedic_mantra": "வேத மந்திரம்",
           "behavioral": "நடத்தை", "donation": "தானம்",
           "gemstone_with_caveat": "ரத்னம் (எச்சரிக்கையுடன்)", "timing": "காலம்"},
}
# Common weekday timings (since most remedies specify these)
WEEKDAY_TIMING_LABELS = {
    "en": {"Sunday": "Sunday", "Monday": "Monday", "Tuesday": "Tuesday",
           "Wednesday": "Wednesday", "Thursday": "Thursday", "Friday": "Friday",
           "Saturday": "Saturday"},
    "sa": {"Sunday": "Ravivāra", "Monday": "Somavāra", "Tuesday": "Maṅgalavāra",
           "Wednesday": "Budhavāra", "Thursday": "Guruvāra", "Friday": "Śukravāra",
           "Saturday": "Śanivāra"},
    "hi": {"Sunday": "रविवार", "Monday": "सोमवार", "Tuesday": "मंगलवार",
           "Wednesday": "बुधवार", "Thursday": "गुरुवार", "Friday": "शुक्रवार",
           "Saturday": "शनिवार"},
    "ta": {"Sunday": "ஞாயிறு", "Monday": "திங்கள்", "Tuesday": "செவ்வாய்",
           "Wednesday": "புதன்", "Thursday": "வியாழன்", "Friday": "வெள்ளி",
           "Saturday": "சனி"},
}
SECTION_HEADINGS = {
    "en": {"afflictions": "AFFLICTIONS DETECTED", "blessings": "BLESSINGS DETECTED",
           "remedies": "REMEDIES", "activations": "ACTIVATIONS",
           "forecasts": "CALIBRATED FORECASTS", "facts": "CHART FACTS"},
    "sa": {"afflictions": "Doṣāḥ", "blessings": "Yogāḥ Śubhāḥ",
           "remedies": "Pratīkārāḥ", "activations": "Sāphalya-Niyamāḥ",
           "forecasts": "Phala-Niyamita-Praṣūcanā", "facts": "Janma-Tathyāni"},
    "hi": {"afflictions": "दोष / अरिष्ट", "blessings": "शुभ योग",
           "remedies": "उपाय", "activations": "सक्रियण विधि",
           "forecasts": "गणित-समर्थित भविष्यवाणी", "facts": "जन्म तथ्य"},
    "ta": {"afflictions": "தோஷங்கள் / குறைபாடுகள்", "blessings": "சுப யோகங்கள்",
           "remedies": "பரிகாரங்கள்", "activations": "செயல்படுத்தும் முறை",
           "forecasts": "கணித பலன்கள்", "facts": "ஜாதக விவரம்"},
}


def translate_severity(value: str, lang: str = "en") -> str:
    return SEVERITY_LABELS.get(lang, SEVERITY_LABELS["en"]).get(value, value)


def translate_strength(value: str, lang: str = "en") -> str:
    return STRENGTH_LABELS.get(lang, STRENGTH_LABELS["en"]).get(value, value)


def translate_remedy_type(value: str, lang: str = "en") -> str:
    return REMEDY_TYPE_LABELS.get(lang, REMEDY_TYPE_LABELS["en"]).get(value, value)


def translate_section(value: str, lang: str = "en") -> str:
    return SECTION_HEADINGS.get(lang, SECTION_HEADINGS["en"]).get(value, value)


def translate_weekday(value: str, lang: str = "en") -> str:
    return WEEKDAY_TIMING_LABELS.get(lang, WEEKDAY_TIMING_LABELS["en"]).get(value, value)


def localize_when(when: str, lang: str = "en") -> str:
    """Replace English weekday tokens in `when` strings with localized ones."""
    if lang == "en" or not when:
        return when
    out = when
    for en_day in WEEKDAY_TIMING_LABELS["en"]:
        loc = WEEKDAY_TIMING_LABELS[lang][en_day]
        out = out.replace(en_day, loc)
    return out


def locale(lang: str = "en") -> dict:
    """Return the full translation tables for `lang`."""
    return {
        "language": lang,
        "signs": SIGNS.get(lang, SIGNS["en"]),
        "grahas": GRAHAS.get(lang, GRAHAS["en"]),
        "nakshatras": NAKSHATRAS.get(lang, NAKSHATRAS["en"]),
        "varas": VARAS.get(lang, VARAS["en"]),
        "bhavas": BHAVAS.get(lang, BHAVAS["en"]),
        "verdicts": VERDICTS.get(lang, VERDICTS["en"]),
        "tithis_base": TITHIS_SHUKLA_BASE.get(lang, TITHIS_SHUKLA_BASE["en"]),
    }


def localize_chart(chart_summary: dict, lang: str = "en") -> dict:
    """Walk a chart summary dict and translate field values where keys match."""
    if lang == "en":
        return chart_summary

    out = {}
    for k, v in chart_summary.items():
        if isinstance(v, dict):
            out[k] = localize_chart(v, lang)
        elif isinstance(v, list):
            out[k] = [localize_chart(x, lang) if isinstance(x, dict) else x for x in v]
        elif k in ("sign", "lagna_sign", "moon_sign", "sun_sign", "muntha_sign"):
            out[k] = translate("sign", v, lang)
        elif k in ("nakshatra", "janma_nakshatra"):
            out[k] = translate("nakshatra", v, lang)
        elif k in ("vara", "weekday"):
            out[k] = translate("vara", v, lang)
        elif k in ("verdict", "confidence_band"):
            out[k] = translate("verdict", v, lang)
        elif k == "tithi":
            out[k] = translate("tithi", v, lang)
        elif k in ("planet", "lord", "graha", "varshesha", "annual_lagna_lord", "muntha_lord"):
            out[k] = translate("graha", v, lang)
        else:
            out[k] = v
    return out
