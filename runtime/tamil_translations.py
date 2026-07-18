"""
Tamil translations of all Vedic astrology terms used in the DEEP PDF.

Used by generate_tamil_pdf.py to produce a fully Tamil version of the report.
"""
import re

# ─── Signs (ராசிகள்) ─────────────────────────────────────────────────────────
RASIS_TA = {
    "Aries":       "மேஷம்",
    "Taurus":      "ரிஷபம்",
    "Gemini":      "மிதுனம்",
    "Cancer":      "கடகம்",
    "Leo":         "சிம்மம்",
    "Virgo":       "கன்னி",
    "Libra":       "துலாம்",
    "Scorpio":     "விருச்சிகம்",
    "Sagittarius": "தனுசு",
    "Capricorn":   "மகரம்",
    "Aquarius":    "கும்பம்",
    "Pisces":      "மீனம்",
}

# ─── Planets (கிரகங்கள்) ────────────────────────────────────────────────────
PLANETS_TA = {
    "Sun":     "சூரியன்",
    "Moon":    "சந்திரன்",
    "Mars":    "செவ்வாய்",
    "Mercury": "புதன்",
    "Jupiter": "குரு",
    "Venus":   "சுக்கிரன்",
    "Saturn":  "சனி",
    "Rahu":    "ராகு",
    "Ketu":    "கேது",
    "Gulika":  "குளிகன்",
    "Mandi":   "மாந்தி",
}

PLANETS_TA_SHORT = {
    "Sun": "சூ", "Moon": "ச", "Mars": "செ", "Mercury": "பு",
    "Jupiter": "கு", "Venus": "சுக்", "Saturn": "சனி", "Rahu": "ரா", "Ketu": "கே",
}

# ─── 27 Nakshatras (நட்சத்திரங்கள்) ─────────────────────────────────────────
NAKSHATRAS_TA = {
    "Ashwini":          "அசுவினி",
    "Bharani":          "பரணி",
    "Krittika":         "கார்த்திகை",
    "Rohini":           "ரோஹிணி",
    "Mrigashira":       "மிருகசீரிஷம்",
    "Mrigashirsha":     "மிருகசீரிஷம்",
    "Ardra":            "திருவாதிரை",
    "Punarvasu":        "புனர்பூசம்",
    "Pushya":           "பூசம்",
    "Ashlesha":         "ஆயில்யம்",
    "Magha":            "மகம்",
    "Purva Phalguni":   "பூரம்",
    "Uttara Phalguni":  "உத்திரம்",
    "Hasta":            "ஹஸ்தம்",
    "Chitra":           "சித்திரை",
    "Swati":            "சுவாதி",
    "Vishakha":         "விசாகம்",
    "Anuradha":         "அனுஷம்",
    "Jyeshtha":         "கேட்டை",
    "Mula":             "மூலம்",
    "Purva Ashadha":    "பூராடம்",
    "Uttara Ashadha":   "உத்திராடம்",
    "Shravana":         "திருவோணம்",
    "Dhanishta":        "அவிட்டம்",
    "Shatabhisha":      "சதயம்",
    "Purva Bhadrapada": "பூரட்டாதி",
    "Uttara Bhadrapada":"உத்திரட்டாதி",
    "Revati":           "ரேவதி",
}

# ─── Weekdays (வாரங்கள்) ───────────────────────────────────────────────────
WEEKDAYS_TA = {
    "Sunday":    "ஞாயிறு",
    "Monday":    "திங்கள்",
    "Tuesday":   "செவ்வாய்",
    "Wednesday": "புதன்",
    "Thursday":  "வியாழன்",
    "Friday":    "வெள்ளி",
    "Saturday":  "சனி",
}

# ─── Tithis (திதிகள்) ─────────────────────────────────────────────────────
TITHIS_TA = {
    "Pratipada":   "பிரதமை",
    "Dwitiya":     "துதியை",
    "Tritiya":     "திரிதியை",
    "Chaturthi":   "சதுர்த்தி",
    "Panchami":    "பஞ்சமி",
    "Shashthi":    "சஷ்டி",
    "Saptami":     "சப்தமி",
    "Ashtami":     "அஷ்டமி",
    "Navami":      "நவமி",
    "Dashami":     "தசமி",
    "Ekadashi":    "ஏகாதசி",
    "Dwadashi":    "துவாதசி",
    "Trayodashi":  "திரயோதசி",
    "Chaturdashi": "சதுர்த்தசி",
    "Purnima":     "பௌர்ணமி",
    "Amavasya":    "அமாவாசை",
}

PAKSHA_TA = {"Shukla": "சுக்லபக்ஷம் (வளர்பிறை)", "Krishna": "கிருஷ்ணபக்ஷம் (தேய்பிறை)"}

KARANAS_TA = {
    "Bava":     "பவ",
    "Balava":   "பாலவ",
    "Kaulava":  "கௌலவ",
    "Taitila":  "தைதிலம்",
    "Garaja":   "கரஜம்",
    "Vanija":   "வணிஜம்",
    "Vishti":   "விஷ்டி",
    "Vishti(Bhadra)": "விஷ்டி (பத்ரா)",
    "Shakuni":  "சகுனி",
    "Chatushpada": "சதுஷ்பாதம்",
    "Naga":     "நாகம்",
    "Kintughna":"கிம்ஸ்துக்னம்",
}

YOGAS_PANCH_TA = {
    "Vishkambha":"விஷ்கம்பம்","Preeti":"ப்ரீதி","Ayushmaan":"ஆயுஷ்மான்","Saubhagya":"செளபாக்யம்",
    "Shobhana":"சோபனம்","Atiganda":"அதிகண்டம்","Sukarmaa":"சுகர்மா","Dhriti":"த்ருதி",
    "Shoola":"சூலம்","Ganda":"கண்டம்","Vriddhi":"விருத்தி","Dhruva":"த்ருவம்",
    "Vyaghata":"வியாகாதம்","Harshana":"ஹர்ஷணம்","Vajra":"வஜ்ரம்","Siddhi":"சித்தி",
    "Vyatipata":"வ்யதீபாதம்","Variyana":"வரியான்","Parigha":"பரிகம்","Shiva":"சிவ",
    "Siddha":"சித்தம்","Saadhya":"சாத்தியம்","Shubha":"சுபம்","Shukla":"சுக்லம்",
    "Brahma":"பிரம்மம்","Indra":"இந்திரம்","Vaidhriti":"வைத்ருதி",
}

# ─── Houses (12 பாவங்கள்) ──────────────────────────────────────────────────
HOUSES_TA = {
    1: ("லக்னம்", "தேகம், சுயம், ஆரோக்கியம்"),
    2: ("தனம்", "செல்வம், குடும்பம், பேச்சு"),
    3: ("சகோதரம்", "சகோதரர்கள், தைரியம், சிறுபயணம்"),
    4: ("மாதா", "வீடு, தாய், சுகங்கள்"),
    5: ("புத்ர", "குழந்தைகள், புத்தி, காதல்"),
    6: ("சத்ரு", "வேலை, ஆரோக்கியம், கடன், எதிரிகள்"),
    7: ("களத்திர", "திருமணம், கூட்டாண்மை"),
    8: ("ஆயுள்", "மாற்றம், ஆயுள், மறைபொருள்"),
    9: ("பிதா", "தந்தை, தர்மம், அதிர்ஷ்டம், உயர்கல்வி"),
    10: ("கர்ம", "தொழில், புகழ், வெற்றி"),
    11: ("இலாப", "வருமானம், நண்பர்கள், ஆசைகள்"),
    12: ("விரய", "செலவு, வெளிநாடு, ஆன்மீகம், தூக்கம்"),
}

# ─── Section headers (பகுதி தலைப்புகள்) ─────────────────────────────────────
SECTION_HEADERS = {
    "DEEP_LIFE_READING":          "முழு வாழ்க்கை ஜாதகம் - ஆழ்ந்த பகுப்பாய்வு",
    "BIRTH_DETAILS_PANCHANGA":    "பிறப்பு விவரங்கள் மற்றும் பஞ்சாங்கம்",
    "PLANETARY_POSITIONS":        "கிரக நிலைகள்",
    "YOGAS_DETECTED":             "ஜாதகத்தில் உள்ள யோகங்கள்",
    "RASI_NAVAMSA":               "ராசி (D1) மற்றும் நவாம்சம் (D9) சக்கரங்கள்",
    "DIVISIONAL_CHARTS":          "வர்க்கங்கள் (பிரிவு சக்கரங்கள்)",
    "BHAVA_SPHUTAS":              "பாவ ஸ்புடங்கள் (வீடுகளின் ஆரம்பம், மத்தி, முடிவு)",
    "ASHTAKAVARGA":               "அஷ்டக வர்க்கம்",
    "PERSONALITY":                "உங்கள் சுபாவமும் மனநிலையும்",
    "CAREER_WEALTH":              "தொழில் மற்றும் செல்வம்",
    "MARRIAGE":                   "திருமணம் மற்றும் கூட்டாண்மை",
    "CHILDREN_HEALTH":            "குழந்தைகள், குடும்பம் மற்றும் ஆரோக்கியம்",
    "SPIRITUALITY_TRAVEL":        "ஆன்மீகம், பயணம், வளர்ச்சி",
    "LIFE_TIMELINE":              "உங்கள் வாழ்க்கை காலவரிசை",
    "DECADE_OUTLOOK":             "தசாப்த வாரியான பார்வை",
    "YEAR_BY_YEAR":               "ஆண்டுவாரியான - அடுத்த 10 ஆண்டுகள்",
    "PRACTICAL_GUIDE":            "தற்போதைய நடைமுறை வழிகாட்டி",
    "VIMSHOTTARI_FULL":           "விம்ஷோத்தரி தசை - முழு அட்டவணை",
    "WHERE_NOW":                  "தற்போது நீங்கள் எங்கே இருக்கிறீர்கள்",
    "NEXT_18_MONTHS":             "அடுத்த 18 மாதங்கள்",
    "HOW_OTHERS_SEE":             "மற்றவர்கள் உங்களை எப்படி பார்க்கிறார்கள்",
    "HOW_YOU_FEEL_INSIDE":        "உங்கள் உள் உணர்வுகள்",
    "NATURAL_STRENGTHS":          "உங்கள் இயல்பான பலங்கள்",
    "WATCH_FOR":                  "கவனிக்க வேண்டியவை",
    "MAJOR_CHAPTERS":             "9 பெரிய வாழ்க்கை அத்தியாயங்கள்",
    "LIFE_EVENT_WINDOWS":         "வாழ்க்கை நிகழ்வு காலங்கள்",
    "ACTIVE_DASHA":               "தற்போதைய தசை — காரணம் → விளைவு",
    "DOMAIN_PREDICTIONS":         "துறை வாரியான முன்னறிவிப்புகள்",
    "CHILDHOOD_WINDOWS":          "குழந்தைப் பருவம் (1996–1998)",
    "DECADE_2020_2030":           "2020–2030 முக்கிய காலங்கள்",
    "RULE_ENGINE_NOTE":           "விதி-இயந்திர சாளரங்கள் (உறுதி அல்ல)",
}

# ─── Field labels ────────────────────────────────────────────────────────────
LABELS = {
    "Name":               "பெயர்",
    "Date of birth":      "பிறந்த தேதி",
    "Time of birth":      "பிறந்த நேரம்",
    "Place":              "பிறந்த ஊர்",
    "Lat/Lon":            "அட்சம் / தீர்க்கம்",
    "Time zone":          "நேர மண்டலம்",
    "Ayanamsa":           "அயனாம்சம்",
    "Lagna":              "லக்னம்",
    "Lagna lord":         "லக்னாதிபதி",
    "Moon Rasi":          "சந்திர ராசி",
    "Janma Nakshatra":    "ஜன்ம நட்சத்திரம்",
    "Nakshatra lord":     "நட்சத்திர அதிபதி",
    "Sunrise":            "சூரிய உதயம்",
    "Sunset":             "சூரிய அஸ்தமனம்",
    "Day duration":       "பகல் காலம்",
    "Tithi":              "திதி",
    "Vara":               "வாரம்",
    "Yoga":               "யோகம்",
    "Karana":             "கரணம்",
    "Paksha":             "பக்ஷம்",
    "Planet":             "கிரகம்",
    "Sign":               "ராசி",
    "House":              "வீடு",
    "Degree":             "பாகை",
    "Nakshatra":          "நட்சத்திரம்",
    "Pada":               "பாதம்",
    "Retrograde":         "வக்ரம்",
    "Lord":               "அதிபதி",
    "Deity":              "தேவதை",
    "Gana":               "கணம்",
    "Yoni":               "யோனி",
    "Nadi":               "நாடி",
    "Direction":          "திக்கு",
    "Symbol":             "சின்னம்",
    "Body Part":          "உடல் பகுதி",
    "Element":            "தத்துவம்",
    "Color":              "நிறம்",
    "Marriage age":       "திருமண வயது",
    "Spouse profile":     "துணைவர் சுபாவம்",
    "Mangal Dosha":       "செவ்வாய் தோஷம்",
    "Harmony":            "ஒற்றுமை",
    "Number of marriages":"திருமணங்களின் எண்ணிக்கை",
    "Family size":        "குடும்ப அளவு",
    "Career fields":      "தொழில் துறைகள்",
    "Work style":         "வேலை முறை",
    "Career peak":        "தொழில் உச்சம்",
    "Wealth peak":        "செல்வ உச்சம்",
    "Income source":      "வருமான ஆதாரம்",
    "Health":             "ஆரோக்கியம்",
    "Foreign settlement": "வெளிநாட்டு குடியேற்றம்",
    "Direction (foreign)":"திசை",
    "Spiritual path":     "ஆன்மீக பாதை",
    "Sub-period":         "உப காலம்",
    "Start date":         "ஆரம்ப தேதி",
    "End date":           "முடிவு தேதி",
    "Years":              "ஆண்டுகள்",
    "Age":                "வயது",
    "What to expect":     "எதிர்பார்க்க வேண்டியவை",
    "Life-area guidance": "வாழ்க்கை துறை வழிகாட்டி",
    "Career":             "தொழில்",
    "Money":              "பணம்",
    "Relationships":      "உறவுகள்",
    "DO during":          "செய்ய வேண்டியவை",
    "AVOID during":       "தவிர்க்க வேண்டியவை",
    "Predicted events":   "முன்னறிவிக்கப்பட்ட நிகழ்வுகள்",
    "Sub-chapters":       "உப அத்தியாயங்கள்",
    "Theme":              "கருப்பொருள்",
    "Period":             "காலம்",
    "NOW":                "தற்போது",
    "PAST":               "கடந்தது",
    "FUTURE":             "எதிர்காலம்",
}

# ─── Mahadasha themes (in Tamil) ─────────────────────────────────────────────
MD_THEME_TA = {
    "Sun":     "அதிகாரம், புகழ், பிதா தொடர்பான விஷயங்கள்",
    "Moon":    "உணர்ச்சி வளர்ச்சி, குடும்பம், பொது அறிமுகம்",
    "Mars":    "செயல்பாடு, துணிவு, சொத்து",
    "Mercury": "தொடர்பாடல், வியாபாரம், திறமை",
    "Jupiter": "விரிவாக்கம், ஞானம், நற்பேறு",
    "Venus":   "உறவுகள், சுகம், கலை",
    "Saturn":  "ஒழுக்கம், கடின உழைப்பு, அமைப்பு",
    "Rahu":    "அளவில்லா ஆசை, வழக்கத்திற்கு மாறான லாபம்",
    "Ketu":    "துறவு, ஆன்மீகம், முடிவுகள்",
}

MD_EXPECT_TA = {
    "Sun": [
        "அதிகாரம் உள்ளவர்களிடம் இருந்து அங்கீகாரம் (முதலாளி, அரசு, தந்தை)",
        "பதவி உயர்வுகள் அல்லது புதிய அதிகாரப்பூர்வ பொறுப்புகள்",
        "சுய நம்பிக்கை மற்றும் தெரிபடுதல் அதிகரிக்கும்",
        "தந்தையின் சூழ்நிலை முக்கியமாகும்",
    ],
    "Moon": [
        "உணர்ச்சி வளர்ச்சி மற்றும் ஆழமான தொடர்புகள்",
        "தாய் முக்கியமாகிறார் - அவரது ஆரோக்கியம், உங்கள் உறவு",
        "பொது அறிமுகம் - மக்கள் உங்களை கவனிக்கத் தொடங்குவார்கள்",
        "பயணம் மற்றும் வீடு மாற்றம் சாத்தியம்",
        "வலுவான உள்ளுணர்வு / கலை / படைப்பாற்றல் கட்டம்",
    ],
    "Mars": [
        "அதிக ஆற்றல் மற்றும் ஆபத்துகளை எடுக்கும் தயார்நிலை",
        "சொத்து வாங்குதல், ரியல் எஸ்டேட் கையாளுதல்",
        "தகராறுகள் மற்றும் மோதல்கள் - உங்கள் நலன்களைப் பாதுகாத்தல்",
        "சகோதரர்கள் முக்கியமாகின்றனர்",
        "விளையாட்டு, உடற்பயிற்சி, இயந்திரம், அறுவை சிகிச்சை",
    ],
    "Mercury": [
        "தொடர்பாடல் சார்ந்த வெற்றி (எழுத்து, கற்பித்தல், வணிகம், விற்பனை)",
        "புதிய திறன்கள் அல்லது உயர்கல்விக்கான கூர்மையான கற்றல்",
        "வணிக கூட்டாண்மைகள் மற்றும் வர்த்தக ஒப்பந்தங்கள்",
        "வேலைக்காக பயணம், தொடர்பு வளர்த்தல், ஒப்பந்தங்கள்",
    ],
    "Jupiter": [
        "வாழ்க்கையில் பொதுவாக சிறந்த 16 ஆண்டு காலம்",
        "திருமணம், குழந்தைகள், செல்வ விரிவாக்கம் சாத்தியம்",
        "ஆன்மீக / தத்துவ / ஆசிரியர் ஈர்ப்பு",
        "ஞானம் அல்லது நிபுணத்துவம் மூலம் அங்கீகாரம்",
        "கற்றல் அல்லது வேலைக்காக வெளிநாட்டு பயணம்",
    ],
    "Venus": [
        "உறவுகள் வளர்கின்றன - இங்கு அடிக்கடி திருமணம் நடக்கிறது",
        "சுகங்கள், சொகுசு, அழகான சூழல்கள்",
        "படைப்பு வேலை மற்றும் கலை அங்கீகாரம்",
        "கூட்டாண்மை, பெண்கள், அழகு துறை மூலம் செல்வம்",
    ],
    "Saturn": [
        "கடின உழைப்பு + தாமதம் + மெதுவான ஆனால் உறுதியான முன்னேற்றம்",
        "நீண்ட கால அமைப்புகள் கட்டப்படும் (தொழில், வீடு, குடும்ப அடித்தளம்)",
        "பொறுமை மற்றும் பொறுப்பின் பாடங்கள்",
        "ஆரோக்கியத்திற்கு கூடுதல் கவனம் தேவை",
        "பெரும்பாலும் கடினமான காலம் - ஆனால் தேர்ச்சியுடன் முடிவடைகிறது",
    ],
    "Rahu": [
        "ஆசை உச்சத்தில் - மேலும் வேண்டும், வேகமாக",
        "வழக்கத்திற்கு மாறான லாபங்கள் (வெளிநாட்டு வேலை, தொழில்நுட்பம், ஊகம்)",
        "திடீர் உயர்வுகள் மற்றும் வீழ்ச்சிகள் - கர்வத்திலிருந்து காத்துக் கொள்ளுங்கள்",
        "வெளிநாடுகள் அல்லது வெளிநாட்டினர் உங்கள் வாழ்க்கையில் நுழைகின்றனர்",
        "வெறி கொண்ட ஆசைகள் மற்றும் குறுக்குவழி சோதனைகளை கவனியுங்கள்",
    ],
    "Ketu": [
        "பழைய அடையாளங்கள் மற்றும் இலக்குகளில் இருந்து விலகுதல்",
        "ஆன்மீக விழிப்பு அல்லது தத்துவ மாற்றம்",
        "முடிவுகள் - முடிய வேண்டியவை - உறவுகள், வேலைகள், இடங்கள்",
        "தியானம் மற்றும் ஏற்றுக்கொள்வது மருந்து",
        "வலுவான உள்ளுணர்வு; உள்ளுணர்வு உணர்வுகள் துல்லியமானவை",
    ],
}

EVENT_PLAIN_TA = {
    "marriage":           "திருமணம் / தீவிர உறவு காலம்",
    "relationship_phase": "உறவு ஆழமாதல்",
    "engagement":         "நிச்சயதார்த்தம் / உறுதியான உறவு",
    "career":             "தொழில் முன்னேற்றம் / பதவி உயர்வு / விருது",
    "promotion":          "பதவி உயர்வு / அதிகாரம் அதிகரிப்பு",
    "career_breakthrough":"தொழில் உச்சம் / புதிய வாய்ப்பு",
    "wealth":             "செல்வ உச்சம் / புதிய வருமான வழி",
    "wealth_peak":        "செல்வம் உச்சம்",
    "wealth_loss":        "நிதி இழப்பு / செலவு அதிகரிப்பு",
    "inheritance":        "சுதந்திரம் / காப்பீடு / திடீர் லாபம்",
    "property":           "சொத்து வாங்குதல் / நிலம்",
    "children":           "குழந்தை பிறப்பு / குடும்ப விரிவாக்கம்",
    "health":             "ஆரோக்கிய எச்சரிக்கை",
    "health_self":        "சுய ஆரோக்கியம் — கவனம் தேவை",
    "self_accident":      "உடல் காயத்தின் ஆபத்து — கவனமாக இருங்கள்",
    "father":             "தந்தை — ஆரோக்கியம் / தொழில் / வாழ்க்கை நிகழ்வு",
    "mother":             "தாய் — ஆரோக்கியம் / குடும்ப நிகழ்வு",
    "spiritual":          "ஆன்மீக விழிப்பு",
    "travel":             "வெளிநாட்டு பயணம் / வெளிநாட்டு வாய்ப்பு / குடியேற்றம்",
    "education":          "புதிய கற்றல் அல்லது முக்கிய தேர்வு",
    "music_composition":  "இசை / படைப்பு மைல்கல்",
    "beauty_peak":        "அழகு / கவர்ச்சி உச்சம்",
    "pet_loss":           "வளர்ப்பு விலங்கு நிகழ்வு",
    "nadi_108_cell":      "நாடி 108-செல் முன்னறிவிப்பு காலம்",
    "leadership_emergence":"தலைமை / பொறுப்பு வருகை",
    "lakshmi_yoga":       "லக்ஷ்மி யோகம் — செல்வம் / நல்வாழ்வு",
    "adhi_yoga":          "அதி யோகம் — நல்ல பலன்கள்",
    "saham_kalatra":      "திருமண சகம் (கலத்திர புள்ளி) செயல்படும் காலம் — திருமண/துணை வாய்ப்பு வலுப்படும்",
    "saham_roga":         "ரோக சகம் (நோய் புள்ளி) செயல்படும் காலம் — ஆரோக்கியம் கவனம் தேவை",
    "nadi_conjunction":   "நாடி இணைவு விதி செயல்படுதல் காலம்",
    "nadi_karaka_shift":  "நாடி காரக கோச்சார மாற்றம்",
    "neecha_bhanga":      "நீச பங்க ராஜ யோகம் செயல்படுதல்",
    "d45_total_life_sub": "D45 அக்ஷவேதாம்சம் — முழு வாழ்க்கை உப நிகழ்வு",
    "d60_karma_sub":      "D60 ஷஷ்டியாம்சம் — கர்ம உப நிகழ்வு",
    "pinnacle_change":    "எண் சாஸ்திரம் — பின்னேகிள் கால மாற்றம்",
    "solar_return_peak":  "சூரிய திரும்பு சக்கரம் — உச்ச செயல்படுதல்",
    "sakata_yoga_low":    "சகட யோகம் (சந்திர-குரு 6/8) — குறைந்த சக்தி காலம்",
    "asset_accumulation": "தங்கம் / இரத்தின சேகரிப்பு காலம்",
    "sudden_gain":        "திடீர் லாபம் / எதிர்பாராத ஆதாயம்",
    "kala_sarpa_peak":    "கால சர்ப்ப யோகம் — உச்ச செயல்படுதல் காலம்",
    "mark_scar_discovery":"பிறப்பு குறி / வடு முக்கியத்துவம்",
    "mouth_lip_issue":    "வாய் / உதட்டு மருத்துவ நிகழ்வு",
    "sibling_health":     "சகோதரர் ஆரோக்கிய நிகழ்வு",
    "relationship_break": "உறவு பிரிவு / சிக்கல்",
    "business":           "வணிக தொடக்கம் / சுயதொழில்",
    "vehicle":            "வாகனம் / ஆடம்பர வாங்குதல்",
    "honor":              "மரியாதை / புகழ்",
    "legal_dispute":      "சட்ட / வழக்கு விஷயம்",
    "speculation_gain":   "முதலீடு / லாட்டரி லாபம்",
    "speculation_loss":   "முதலீடு இழப்பு",
    "widowhood":          "துணைவர் தொடர்பான கடின காலம்",
    "death_self":         "ஆயுள் தொடர்பான எச்சரிக்கை (ஆழமான பார்வை)",
}

# Life-domain section titles
DOMAIN_TA = {
    "career":   "💼 தொழில்",
    "marriage": "💍 திருமணம் / உறவு",
    "wealth":   "💰 செல்வம்",
    "health":   "🏥 ஆரோக்கியம்",
    "father":   "👨 தந்தை",
}

# Dasha level labels
DASHA_LEVEL_TA = {1: "மகா தசை (MD)", 2: "உப தசை (AD)", 3: "பிரத்தியந்தர் (PD)", 4: "சூக்ஷ்ம (SD)"}

# Active dasha → plain Tamil effect (cause → effect one-liners)
DASHA_EFFECT_TA = {
    "Moon":    "உணர்ச்சி, தாய்/குடும்பம், பொது அறிமுகம் — 9வது வீட்டு சந்திரன் செயல்படுதல்",
    "Rahu":    "வழக்கத்திற்கு மாறான பாதை, தொழில்/வெளிநாடு, திடீர் மாற்றம் — 10வது வீட்டு ராகு",
    "Mars":    "செயல், போட்டி, 5வது வீட்டில் புத்தி+தைரியம் — குறுகிய கால துரித முடிவுகள்",
    "Ketu":    "விட்டுவிடுதல், ஆன்மீகம், தெளிவற்ற உணர்வுகள் — 4வது வீட்டு கேது தொடர்பு",
    "Sun":     "அதிகாரம், தந்தை, 6வது வீட்டில் சேவை/பணி அழுத்தம்",
    "Mercury": "தொடர்பாடல், வணிகம், கற்றல் — புதன்+செவ்வாய் 5வது வீடு",
    "Jupiter": "விரிவாக்கம், ஞானம், லக்னாதிபதி குரு — நல்ல பலன்கள்",
    "Venus":   "உறவு, திருமணம், 7வது வீட்டில் சுக்கிரன் — கூட்டாண்மை கவனம்",
    "Saturn":  "கடின உழைப்பு, தாமதம், 4வது வீட்டில் சனி+கேது — பொறுமை தேவை",
}

RULE_ENGINE_DISCLAIMER_TA = (
    "இந்த அட்டவணைகள் விதி-இயந்திரம் (event_predictor_v2) மூலம் கணக்கிடப்பட்ட "
    "சாளரங்கள் — உறுதியான முன்னறிவிப்பு அல்ல. ஜாதகம் + தசை + நேரம் சேர்த்து "
    "எந்த நிகழ்வும் நடக்கலாம் அல்லது நடக்காமலும் போகலாம். "
    "உங்கள் வாழ்க்கை நிகழ்வுகளுடன் ஒப்பிட்டு பயன்படுத்துங்கள்."
)

# Category slug → short Tamil label (domain column)
CATEGORY_TA = {
    "career": "தொழில்",
    "marriage": "திருமணம்",
    "wealth": "செல்வம்",
    "health": "ஆரோக்கியம்",
    "father": "தந்தை",
    "travel": "பயணம்",
    "education": "கல்வி",
    "children": "குழந்தை",
    "spiritual": "ஆன்மீகம்",
    "mother": "தாய்",
    "music_composition": "இசை",
    "inheritance": "சுதந்திரம்",
    "relationship_phase": "உறவு",
    "leadership_emergence": "தலைமை",
    "nadi_108_cell": "நாடி",
    "lakshmi_yoga": "லக்ஷ்மி யோகம்",
    "adhi_yoga": "அதி யோகம்",
    "saham_kalatra": "சகம் கலத்திரம்",
    "saham_roga": "சகம் ரோகம்",
    "nadi_conjunction": "நாடி இணைவு",
    "nadi_karaka_shift": "நாடி காரக மாற்றம்",
    "neecha_bhanga": "நீச பங்க ராஜ யோகம்",
    "d45_total_life_sub": "D45 உப நிகழ்வு",
    "d60_karma_sub": "D60 கர்ம உப நிகழ்வு",
    "pinnacle_change": "பின்னேகிள் மாற்றம்",
    "solar_return_peak": "சூரிய திரும்பு உச்சம்",
    "sakata_yoga_low": "சகட யோகம்",
    "asset_accumulation": "சொத்து சேகரிப்பு",
    "sudden_gain": "திடீர் லாபம்",
    "kala_sarpa_peak": "கால சர்ப்ப யோகம்",
    "mark_scar_discovery": "பிறப்பு குறி",
    "mouth_lip_issue": "வாய்/உதடு",
    "sibling_health": "சகோதரர் ஆரோக்கியம்",
    "promotion": "பதவி உயர்வு",
    "career_breakthrough": "தொழில் உச்சம்",
    "engagement": "நிச்சயதார்த்தம்",
    "relationship_break": "உறவு பிரிவு",
    "wealth_peak": "செல்வ உச்சம்",
    "wealth_loss": "நிதி இழப்பு",
    "property": "சொத்து",
    "speculation_gain": "முதலீடு லாபம்",
    "health_self": "சுய ஆரோக்கியம்",
    "self_accident": "உடல் காயம்",
}

# Catalog event name (without trailing " Event") → Tamil description
EVENT_NAME_TA = {
    "Saham Kalatra (spouse point) activation": (
        "திருமண சகம் (கலத்திர புள்ளி) செயல்படும் காலம் — திருமண/துணை வாய்ப்பு வலுப்படும்"
    ),
    "Saham Roga (disease point) activation": (
        "ரோக சகம் (நோய் புள்ளி) செயல்படும் காலம் — ஆரோக்கியம் கவனம் தேவை"
    ),
    "Nadi conjunction-rule activation": "நாடி இணைவு விதி செயல்படுதல் காலம்",
    "Nadi karaka transit shift": "நாடி காரக கோச்சார மாற்றம்",
    "Neecha-Bhanga Raja Yoga activation": "நீச பங்க ராஜ யோகம் செயல்படுதல்",
    "D45 Akshavedamsa total-life sub-event": "D45 அக்ஷவேதாம்சம் — முழு வாழ்க்கை உப நிகழ்வு",
    "D60 Shashtiamsa karmic sub-event": "D60 ஷஷ்டியாம்சம் — கர்ம உப நிகழ்வு",
    "Numerology Pinnacle period change": "எண் சாஸ்திரம் — பின்னேகிள் கால மாற்றம்",
    "Solar Return chart peak activation": "சூரிய திரும்பு சக்கரம் — உச்ச செயல்படுதல்",
    "Sakata yoga (Moon-Jupiter 6/8) low-tide": "சகட யோகம் (சந்திர-குரு 6/8) — குறைந்த சக்தி காலம்",
    "Gold / Gem Accumulation": "தங்கம் / இரத்தின சேகரிப்பு காலம்",
    "Sudden Windfall / Gain": "திடீர் லாபம் / எதிர்பாராத ஆதாயம்",
    "Kala Sarpa Yoga active period peak": "கால சர்ப்ப யோகம் — உச்ச செயல்படுதல் காலம்",
    "Birth-mark / Scar Significance": "பிறப்பு குறி / வடு முக்கியத்துவம்",
    "Mouth / Lip Medical Event": "வாய் / உதட்டு மருத்துவ நிகழ்வு",
}

DASHA_ABBR_TA = {
    "MD": "மகா தசை",
    "AD": "உப தசை",
    "PD": "பிரத்தியந்தர் தசை",
    "SD": "சூக்ஷ்ம தசை",
}

_PLANET_NAMES = "|".join(re.escape(p) for p in PLANETS_TA)
_HOUSE_LORD_RE = rf"(\d+)L(?: \(({_PLANET_NAMES})\))?"

# Common English "why" fragments → Tamil (exact-match shortcuts)
WHY_TA = {
    "Pitra Dosha base": "பித்ர தோஷம் அடிப்படை",
    "Ketu MD": "கேது மகா தசை",
    "Moon MD": "சந்திரன் மகா தசை",
    "Rahu AD": "ராகு உப தசை",
    "Mars PD": "செவ்வாய் பிரத்தியந்தர் தசை",
    "Sun activated as AD": "சூரியன் உப தசையில் செயலில்",
    "Sun activated as PD": "சூரியன் பிரத்தியந்தர் தசையில் செயலில்",
    "Sun activated as MD": "சூரியன் மகா தசையில் செயலில்",
    "9L (Sun) AD": "9ம் வீட்டு அதிபதி (சூரியன்) உப தசை",
    "9L (Sun) PD": "9ம் வீட்டு அதிபதி (சூரியன்) பிரத்தியந்தர் தசை",
    "7L dasha activation": "7ம் வீட்டு அதிபதி தசை செயல்படுதல்",
    "10L/11L active": "10/11 அதிபதிகள் செயலில்",
    "Venus in 7H": "7ம் வீட்டில் சுக்கிரன்",
    "Rahu in 10H": "10ம் வீட்டில் ராகு",
    "Jupiter lagna lord": "லக்னாதிபதி குரு",
    "D9 dasha lord in marriage set": "D9 தசை திருமண செயல்படுத்தி",
    "D10 dasha lord in career set": "D10 தசை தொழில் செயல்படுத்தி",
    "transit Saturn active": "சனி கோச்சாரம் செயலில்",
    "Mars well-placed in H5": "5ம் வீட்டில் செவ்வாய் நன்றாக அமைந்துள்ளது",
    "Jupiter MD (karaka)": "குரு மகா தசை (காரக)",
    "Jupiter AD (karaka)": "குரு உப தசை (காரக)",
    "Venus MD": "சுக்கிரன் மகா தசை",
    "Venus AD": "சுக்கிர உப தசை",
    "Venus PD": "சுக்கிர பிரத்தியந்தர் தசை",
    "Jupiter AD": "குரு உப தசை",
    "Jupiter PD": "குரு பிரத்தியந்தர் தசை",
    "Saturn AD": "சனி உப தசை",
    "Mercury AD": "புதன் உப தசை",
    "7L AD": "7ம் வீட்டு அதிபதி உப தசை",
    "7L PD": "7ம் வீட்டு அதிபதி பிரத்தியந்தர் தசை",
    "1L AD": "1ம் வீட்டு அதிபதி உப தசை",
    "1L PD": "1ம் வீட்டு அதிபதி பிரத்தியந்தர் தசை",
    "3L AD": "3ம் வீட்டு அதிபதி உப தசை",
    "9L PD": "9ம் வீட்டு அதிபதி பிரத்தியந்தர் தசை",
}


def _dasha_ta(abbr: str) -> str:
    return DASHA_ABBR_TA.get(abbr, abbr)


def _pt(planet: str) -> str:
    return PLANETS_TA.get(planet, planet)


def why_to_tamil(why: str) -> str:
    """Translate English cause/why strings to Tamil via lookup + regex."""
    if not why:
        return ""
    w = why.strip()
    if w in WHY_TA:
        return WHY_TA[w]

    # Jupiter transits natal 7L (Mercury)
    m = re.match(
        rf"Jupiter transits natal (\d+)L \(({_PLANET_NAMES})\)", w
    )
    if m:
        h, p = m.group(1), m.group(2)
        return f"குரு நாட்டிய {h}ம் வீட்டு அதிபதி ({_pt(p)})-ஐ கடந்து செல்கிறது"

    # Jupiter transits 10L (Mercury)
    m = re.match(rf"Jupiter transits (\d+)L \(({_PLANET_NAMES})\)", w)
    if m:
        h, p = m.group(1), m.group(2)
        return f"குரு {h}ம் வீட்டு அதிபதி ({_pt(p)})-ஐ கடந்து செல்கிறது"

    # Saturn transits 10L (career-test)
    m = re.match(r"Saturn transits (\d+)L \(([^)]+)\)", w)
    if m:
        h, qual = m.group(1), m.group(2)
        qual_ta = {"career-test": "தொழில் சோதனை"}.get(qual, qual)
        return f"சனி {h}ம் வீட்டு அதிபதி ({qual_ta})-ஐ கடந்து செல்கிறது"

    # benefic-stack Moon/Mercury/Moon
    m = re.match(r"benefic-stack (.+)", w)
    if m:
        parts = [_pt(p.strip()) for p in m.group(1).split("/")]
        return "நல கிரக குவியல் " + "/".join(parts)

    # {Planet} well-placed in H{n}
    m = re.match(rf"({_PLANET_NAMES}) well-placed in H(\d+)", w)
    if m:
        p, h = m.group(1), m.group(2)
        return f"{_pt(p)} {h}ம் வீட்டில் நன்றாக அமைந்துள்ளது"

    # {Planet} in dusthana H{n}
    m = re.match(rf"({_PLANET_NAMES}) in dusthana H(\d+)", w)
    if m:
        p, h = m.group(1), m.group(2)
        return f"{_pt(p)} {h}ம் வீட்டில் (துர்ம வீடு)"

    # transit {Planet} active
    m = re.match(rf"transit ({_PLANET_NAMES}) active", w)
    if m:
        return f"{_pt(m.group(1))} கோச்சாரம் செயலில்"

    # Sun activated as MD/AD/PD
    m = re.match(r"Sun activated as (MD|AD|PD)", w)
    if m:
        return f"சூரியன் {_dasha_ta(m.group(1))}யில் செயலில்"

    # {n}L ({Planet}) MD/AD/PD — full house lord + planet
    m = re.match(rf"(\d+)L \(({_PLANET_NAMES})\) (MD|AD|PD)", w)
    if m:
        h, p, d = m.group(1), m.group(2), m.group(3)
        suffix = {"MD": " — முழு மகா தசை", "AD": "", "PD": ""}.get(d, "")
        extra = f" ({suffix.strip(' —')})" if suffix and d == "MD" else ""
        if d == "MD" and "fully activated" not in w:
            return f"{h}ம் வீட்டு அதிபதி ({_pt(p)}) {_dasha_ta(d)}"
        return f"{h}ம் வீட்டு அதிபதி ({_pt(p)}) {_dasha_ta(d)}{extra}"

    # {n}L ({Planet}) active — health-test period
    m = re.match(rf"(\d+)L \(({_PLANET_NAMES})\) active — health-test period", w)
    if m:
        h, p = m.group(1), m.group(2)
        return f"{h}ம் வீட்டு அதிபதி ({_pt(p)}) செயலில் — ஆரோக்கிய சோதனை காலம்"

    # {n}L MD/AD/PD (without planet name)
    m = re.match(r"(\d+)L (MD|AD|PD)", w)
    if m:
        h, d = m.group(1), m.group(2)
        return f"{h}ம் வீட்டு அதிபதி {_dasha_ta(d)}"

    # {Planet} (karaka) MD/AD/PD
    m = re.match(rf"({_PLANET_NAMES}) \(karaka\) (MD|AD|PD)", w)
    if m:
        return f"{_pt(m.group(1))} (காரக) {_dasha_ta(m.group(2))}"

    # {Planet} MD/AD/PD
    m = re.match(rf"^({_PLANET_NAMES}) (MD|AD|PD)$", w)
    if m:
        return f"{_pt(m.group(1))} {_dasha_ta(m.group(2))}"

    # {Planet} (H{n}) as AD
    m = re.match(rf"({_PLANET_NAMES}) \(H(\d+)\) as AD", w)
    if m:
        p, h = m.group(1), m.group(2)
        return f"{_pt(p)} ({h}ம் வீடு) உப தசையில்"

    # Moon MD + Rahu AD — unconventional travel
    m = re.match(rf"Moon MD \+ ({_PLANET_NAMES}) AD — (.+)", w)
    if m:
        p, note = m.group(1), m.group(2)
        note_ta = {
            "unconventional travel": "வழக்கத்திற்கு மாறான பயணம்",
        }.get(note, note)
        return f"சந்திரன் மகா தசை + {_pt(p)} உப தசை — {note_ta}"

    # {md} MD + {ad} AD
    m = re.match(rf"({_PLANET_NAMES}) MD \+ ({_PLANET_NAMES}) AD", w)
    if m:
        return f"{_pt(m.group(1))} மகா தசை + {_pt(m.group(2))} உப தசை"

    # {n}L MD + Jupiter AD — inheritance combo
    m = re.match(r"(\d+)L MD \+ Jupiter AD — inheritance combo", w)
    if m:
        return f"{m.group(1)}ம் வீட்டு அதிபதி மகா தசை + குரு உப தசை — சுதந்திரம் கூட்டு"

    # {yoga name} activated
    m = re.match(r"(.+) activated$", w)
    if m:
        name = m.group(1)
        return f"{YOGA_PLAIN_TA.get(name, name)} செயல்படுதல்"

    # transit Mars on natal Moon (orb 1.7°)
    m = re.match(rf"transit Mars on natal ({_PLANET_NAMES}) \(orb ([\d.]+)°\)", w)
    if m:
        return f"கோச்சார செவ்வாய் நாட்டிய {_pt(m.group(1))}-ஐ கடந்து (ஆர்ப் {m.group(2)}°)"

    # Mars transit dusthana lord (Moon) — accident-trigger
    m = re.match(rf"Mars transit dusthana lord \(({_PLANET_NAMES})\) — accident-trigger", w)
    if m:
        return f"செவ்வாய் கோச்சாரம் துர்ம அதிபதி ({_pt(m.group(1))}) — விபத்து தூண்டி"

    # Saturn transit to natal Sun
    m = re.match(rf"Saturn transit to natal ({_PLANET_NAMES})", w)
    if m:
        return f"சனி கோச்சாரம் நாட்டிய {_pt(m.group(1))}-ஐ கடந்து"

    # Fallback: replace remaining planet names
    out = w
    for en, ta in sorted(PLANETS_TA.items(), key=lambda x: -len(x[0])):
        out = re.sub(rf"\b{re.escape(en)}\b", ta, out)
    for abbr, ta in DASHA_ABBR_TA.items():
        out = re.sub(rf"\b{abbr}\b", ta, out)
    return out


def ta_event(category, event_en=""):
    """Plain Tamil label for an event band."""
    if category and category in EVENT_PLAIN_TA:
        return EVENT_PLAIN_TA[category]
    ev = (event_en or "").strip()
    if ev.endswith(" Event"):
        base = ev[:-6].strip()
        if base in EVENT_NAME_TA:
            return EVENT_NAME_TA[base]
    ev_lower = ev.lower()
    for key, ta in EVENT_PLAIN_TA.items():
        if key.replace("_", " ") in ev_lower or key in ev_lower:
            return ta
    return event_en or category or "—"


def ta_why(why_list):
    """Translate dasha cause strings to Tamil where possible."""
    if not why_list:
        return ""
    if isinstance(why_list, str):
        why_list = [why_list]
    parts = [why_to_tamil(str(w).strip()) for w in why_list[:3]]
    return " · ".join(parts)


def ta_dasha_chain(active_lookup):
    """Format active dasha levels as Tamil cause chain."""
    rows = []
    for lvl in sorted(active_lookup):
        rec = active_lookup[lvl]
        lords = "-".join(PLANETS_TA.get(rec[k], rec[k]) for k in ("md", "ad", "pd", "sd") if k in rec)
        end = rec.get("end")
        end_s = end.strftime("%d-%m-%Y") if end else "—"
        effect_lord = rec.get("sd") or rec.get("pd") or rec.get("ad") or rec.get("md")
        effect = DASHA_EFFECT_TA.get(effect_lord, MD_THEME_TA.get(effect_lord, ""))
        rows.append({
            "level": DASHA_LEVEL_TA.get(lvl, str(lvl)),
            "lords": lords,
            "until": end_s,
            "effect": effect,
        })
    return rows

# ─── Yoga interpretations in Tamil ──────────────────────────────────────────
YOGA_PLAIN_TA = {
    "Hamsa Yoga":       "இயல்பான ஞான-ஆசிரியர் பண்பு - மக்கள் உங்கள் ஆலோசனை கேட்கிறார்கள்",
    "Bhadra Yoga":      "கூர்மையான அறிவு + நல்ல தொடர்பாடல் - வார்த்தைகள் உங்கள் கருவி",
    "Ruchaka Yoga":     "வலுவான தைரியம் + தலைமை - நீங்கள் பொறுப்பேற்க முடியும்",
    "Malavya Yoga":     "இயல்பான கவர்ச்சி + அழகை ரசிக்கும் திறன்",
    "Shasha Yoga":      "ஒழுக்கம் + நீண்ட கால சாதனைக்கான திறன்",
    "Raja Yoga":        "வாழ்க்கையில் உயர்த்தும் திறன் - மரியாதையும் அங்கீகாரமும்",
    "Gaja-Kesari Yoga": "புத்திசாலித்தனம் + நல்ல பேச்சு + மரியாதை",
    "Budha-Aditya Yoga":"கூர்மையான மனம் + பகுப்பாய்வு திறன் + கற்றல்",
    "Lakshmi Yoga":     "இயல்பான செல்வ ஆற்றல்",
    "Vesi Yoga":        "நல்ல பேச்சு மற்றும் கடமை உணர்வு",
    "Vasi Yoga":        "கவர்ச்சி + தலைமை",
    "Ubhayachari Yoga": "சமநிலையான செழிப்பு + புகழ் + ஆரோக்கியம்",
    "Yukta Yoga":       "கூர்மையான அறிவு + உறுதியான செயல்",
    "Yukta Yoga (Budh-Mangal Yuti)": "கூர்மையான அறிவு + உறுதியான செயல் (புத-செவ்வ யுதி)",
    "Pitra Dosha":      "தந்தைவழி வம்சத்துடன் கர்ம பந்தம் - தர்ப்பணம் / சிராத்தம் நற்பயன் தரும்",
    "Kaal Sarpa":       "வாழ்க்கையில் தாமதங்கள் - தீவிர முயற்சி தேவை",
}


def tamil(en_term, default=None):
    """Look up Tamil translation; fall back to English or default."""
    for d in [PLANETS_TA, RASIS_TA, NAKSHATRAS_TA, WEEKDAYS_TA,
               TITHIS_TA, KARANAS_TA, YOGAS_PANCH_TA, LABELS, SECTION_HEADERS]:
        if en_term in d:
            v = d[en_term]
            return v if isinstance(v, str) else v[0]
    return default if default is not None else en_term


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("Tamil translation dictionaries loaded:")
    print(f"  Rasis: {len(RASIS_TA)}  Planets: {len(PLANETS_TA)}  Nakshatras: {len(NAKSHATRAS_TA)}")
    print(f"  Weekdays: {len(WEEKDAYS_TA)}  Tithis: {len(TITHIS_TA)}  Karanas: {len(KARANAS_TA)}")
    print(f"  Yogas (panch): {len(YOGAS_PANCH_TA)}  Houses: {len(HOUSES_TA)}")
    print(f"  Labels: {len(LABELS)}  Section headers: {len(SECTION_HEADERS)}")
    print(f"  MD Themes: {len(MD_THEME_TA)}  MD Expect lists: {len(MD_EXPECT_TA)}")
    print(f"  Event types: {len(EVENT_PLAIN_TA)}  Yoga interpretations: {len(YOGA_PLAIN_TA)}")
    print()
    print("Sample:")
    print(f"  Aries → {RASIS_TA['Aries']}")
    print(f"  Jupiter → {PLANETS_TA['Jupiter']}")
    print(f"  Magha → {NAKSHATRAS_TA['Magha']}")
    print(f"  House 7 → {HOUSES_TA[7]}")
