import os
import re

def migrate():
    source_path = "runtime/generate_tamil_pdf.py"
    target_path = "runtime/generate_hindi_pdf.py"
    
    print(f"Reading {source_path}...")
    with open(source_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace translation module imports
    content = content.replace("from tamil_translations import (", "from hindi_translations import (")
    content = content.replace(
        """    RASIS_TA, PLANETS_TA, PLANETS_TA_SHORT, NAKSHATRAS_TA, WEEKDAYS_TA,
    TITHIS_TA, PAKSHA_TA, KARANAS_TA, YOGAS_PANCH_TA, HOUSES_TA,
    SECTION_HEADERS, LABELS, MD_THEME_TA, MD_EXPECT_TA, EVENT_PLAIN_TA,
    YOGA_PLAIN_TA,""",
        """    RASIS_HI, PLANETS_HI, PLANETS_HI_SHORT, NAKSHATRAS_HI, WEEKDAYS_HI,
    TITHIS_HI, PAKSHA_HI, KARANAS_HI, YOGAS_PANCH_HI, HOUSES_HI,
    SECTION_HEADERS_HI, LABELS_HI, MD_THEME_HI, MD_EXPECT_HI, EVENT_PLAIN_HI,
    YOGA_PLAIN_HI,"""
    )

    # 2. Replace helper functions and maps
    content = content.replace("def _ta_planet(p): return PLANETS_TA.get(p, p)", "def _hi_planet(p): return PLANETS_HI.get(p, p)")
    content = content.replace("def _ta_rasi(r): return RASIS_TA.get(r, r)", "def _hi_rasi(r): return RASIS_HI.get(r, r)")
    content = content.replace("def _ta_nak(n): return NAKSHATRAS_TA.get(n, n)", "def _hi_nak(n): return NAKSHATRAS_HI.get(n, n)")
    content = content.replace("def _ta_weekday(w): return WEEKDAYS_TA.get(w, w)", "def _hi_weekday(w): return WEEKDAYS_HI.get(w, w)")
    content = content.replace("def _ta_section(k): return SECTION_HEADERS.get(k, k)", "def _hi_section(k): return SECTION_HEADERS_HI.get(k, k)")
    content = content.replace("def _ta_label(k): return LABELS.get(k, k)", "def _hi_label(k): return LABELS_HI.get(k, k)")

    # 3. Replace mapping dictionaries and function calls
    content = content.replace("_ta_planet", "_hi_planet")
    content = content.replace("_ta_rasi", "_hi_rasi")
    content = content.replace("_ta_nak", "_hi_nak")
    content = content.replace("_ta_weekday", "_hi_weekday")
    content = content.replace("_ta_section", "_hi_section")
    content = content.replace("_ta_label", "_hi_label")

    content = content.replace("PLANETS_TA", "PLANETS_HI")
    content = content.replace("PLANETS_TA_SHORT", "PLANETS_HI_SHORT")
    content = content.replace("RASIS_TA", "RASIS_HI")
    content = content.replace("NAKSHATRAS_TA", "NAKSHATRAS_HI")
    content = content.replace("WEEKDAYS_TA", "WEEKDAYS_HI")
    content = content.replace("TITHIS_TA", "TITHIS_HI")
    content = content.replace("PAKSHA_TA", "PAKSHA_HI")
    content = content.replace("KARANAS_TA", "KARANAS_HI")
    content = content.replace("YOGAS_PANCH_TA", "YOGAS_PANCH_HI")
    content = content.replace("HOUSES_TA", "HOUSES_HI")
    content = content.replace("SECTION_HEADERS", "SECTION_HEADERS_HI")
    content = content.replace("LABELS", "LABELS_HI")
    content = content.replace("MD_THEME_TA", "MD_THEME_HI")
    content = content.replace("MD_EXPECT_TA", "MD_EXPECT_HI")
    content = content.replace("EVENT_PLAIN_TA", "EVENT_PLAIN_HI")
    content = content.replace("YOGA_PLAIN_TA", "YOGA_PLAIN_HI")

    # 4. Replace Month name block
    tamil_months_block = """# ── Tamil month names for date display ───────────────────────────────────────
TAMIL_MONTHS = {1:"ஜனவரி",2:"பிப்ரவரி",3:"மார்ச்",4:"ஏப்ரல்",
                 5:"மே",6:"ஜூன்",7:"ஜூலை",8:"ஆகஸ்ட்",
                 9:"செப்டம்பர்",10:"அக்டோபர்",11:"நவம்பர்",12:"டிசம்பர்"}

def fmt_my_ta(d):
    \"\"\"Format date as 'மார்ச் 2026'.\"\"\"
    return f"{TAMIL_MONTHS.get(d.month, '?')} {d.year}"


def fmt_dmy_ta(d):
    \"\"\"Format date as '17 மார்ச் 2026'.\"\"\"
    return f"{d.day} {TAMIL_MONTHS.get(d.month, '?')} {d.year}\""""
    
    hindi_months_block = """# ── Hindi month names for date display ───────────────────────────────────────
HINDI_MONTHS = {1:"जनवरी",2:"फरवरी",3:"मार्च",4:"अप्रैल",
                 5:"मई",6:"जून",7:"जुलाई",8:"अगस्त",
                 9:"सितंबर",10:"अक्टूबर",11:"नवंबर",12:"दिसंबर"}

def fmt_my_hi(d):
    \"\"\"Format date as 'मार्च 2026'.\"\"\"
    return f"{HINDI_MONTHS.get(d.month, '?')} {d.year}"


def fmt_dmy_hi(d):
    \"\"\"Format date as '17 मार्च 2026'.\"\"\"
    return f"{d.day} {HINDI_MONTHS.get(d.month, '?')} {d.year}\""""

    content = content.replace(tamil_months_block, hindi_months_block)
    content = content.replace("fmt_my_ta", "fmt_my_hi")
    content = content.replace("fmt_dmy_ta", "fmt_dmy_hi")

    # 5. Font replacements
    content = content.replace('font_name="Tamil"', 'font_name="Devanagari"')
    content = content.replace('font_name="Tamil-Bold"', 'font_name="Devanagari-Bold"')
    content = content.replace('tamil_font="Tamil"', 'tamil_font="Devanagari"')
    content = content.replace('tamil_font="Tamil-Bold"', 'tamil_font="Devanagari-Bold"')
    content = content.replace('self.tamil_font = "Tamil-Bold" if bold else "Tamil"', 'self.tamil_font = "Devanagari-Bold" if bold else "Devanagari"')

    # 6. Planet Karakas block (line 745-755)
    planet_karakas_ta = """    PLANET_KARAKAS_TA = {
        "Sun": "சுயம், அதிகாரம், தந்தை, ஆரோக்கியம், மரியாதை",
        "Moon": "மனம், உணர்வுகள், தாய், மனநிலை, பிரபலம்",
        "Mars": "தைரியம், ஆற்றல், சகோதரர், போட்டி, சொத்து",
        "Mercury": "புத்தி, பேச்சு, வணிகம், கல்வி, கணித திறன்",
        "Jupiter": "ஞானம், அதிர்ஷ்டம், ஆசிரியர், செல்வம், குழந்தைகள், தர்மம்",
        "Venus": "காதல், கலை, அழகு, கூட்டாண்மை, சுகம், பிரியம்",
        "Saturn": "ஒழுக்கம், கடின உழைப்பு, ஆயுள், தாமதம், பொறுப்பு",
        "Rahu": "ஆசை, வெளிநாடு, தொழில்நுட்பம், திடீர் உயர்வு",
        "Ketu": "ஆன்மீகம், விடுதலை, ஆராய்ச்சி, பழைய கர்மம்",
    }"""
    
    planet_karakas_hi = """    PLANET_KARAKAS_HI = {
        "Sun": "अधिकार, प्रसिद्धि, पिता, आत्म-सम्मान, नेतृत्व",
        "Moon": "मन, भावनाएं, माता, मानसिक शांति, लोकप्रियता",
        "Mars": "साहस, ऊर्जा, भाई-बहन, प्रतिस्पर्धा, संपत्ति",
        "Mercury": "बुद्धि, वाणी, व्यापार, शिक्षा, गणितीय कौशल",
        "Jupiter": "ज्ञान, भाग्य, गुरु, धन, संतान, धर्म",
        "Venus": "प्रेम, कला, सौंदर्य, साझेदारी, सुख, विलासिता",
        "Saturn": "अनुशासन, कठिन परिश्रम, आयु, देरी, जिम्मेदारी",
        "Rahu": "महत्वाकांक्षा, विदेश, प्रौद्योगिकी, अचानक प्रगति",
        "Ketu": "अध्यात्म, मोक्ष, अनुसंधान, पुराना कर्म",
    }"""
    
    content = content.replace(planet_karakas_ta, planet_karakas_hi)
    content = content.replace("PLANET_KARAKAS_TA", "PLANET_KARAKAS_HI")
    content = content.replace("HOUSE_NAMES_TA_FULL", "HOUSE_NAMES_HI_FULL")

    # 7. Interpretation string inside _ta_interp (which is now _hi_interp)
    old_ta_interp_body = """        kar = PLANET_KARAKAS_HI.get(planet, "")
        h_name = HOUSES_TA.get(house, ("?", "?"))[0]
        h_mean = HOUSES_TA.get(house, ("?", "?"))[1]
        return (f"{_ta_planet(planet)} இந்த {h_name} வீட்டில் இருப்பதால், "
                f"இவ்வீட்டின் ({h_mean}) விஷயங்களில் "
                f"{kar.split(',')[0]} சம்பந்தமான பலன்கள் கிடைக்கும்.")"""
                
    new_hi_interp_body = """        kar = PLANET_KARAKAS_HI.get(planet, "")
        h_name = HOUSES_HI.get(house, ("?", "?"))[0]
        h_mean = HOUSES_HI.get(house, ("?", "?"))[1]
        return (f"{_hi_planet(planet)} इस {h_name} भाव में होने के कारण, "
                f"इस भाव ({h_mean}) के मामलों में "
                f"{kar.split(',')[0]} से संबंधित फल प्रदान करेगा।")"""
                
    content = content.replace(old_ta_interp_body, new_hi_interp_body)
    content = content.replace("_ta_interp", "_hi_interp")

    # 8. Main prediction loop strings
    content = content.replace(
        'f"▸ {planet_ta} — {rasi_ta} ராசியில் (வீடு {h})"',
        'f"▸ {planet_ta} — {rasi_ta} राशि में (भाव {h})"'
    )
    
    old_dignity_class_ta = """            DIGNITY_TA = {
                "exalted":"உச்சம் (exalted)","debilitated":"நீசம் (debilitated)",
                "own":"சுவக்ஷேத்திரம் (own sign)","mooltrikona":"மூலத்திரிகோணம்",
                "friend":"நட்பு (friend)","enemy":"எதிரி (enemy)","neutral":"சம (neutral)",
            }
            CLASS_TA = {"kendra":"கேந்திரம்","trikona":"த்ரிகோணம்","upachaya":"உபசயம்",
                         "dusthana":"துஸ்தானம்","maraka":"மாரகம்","panaphara":"பணபரம்","apoklima":"அபோகலிமம்"}"""
                         
    new_dignity_class_hi = """            DIGNITY_HI = {
                "exalted":"उच्च (exalted)","debilitated":"नीच (debilitated)",
                "own":"स्वराशि (own sign)","mooltrikona":"मूलत्रिकोण",
                "friend":"मित्र (friend)","enemy":"शत्रु (enemy)","neutral":"सम (neutral)",
            }
            CLASS_HI = {"kendra":"केंद्र","trikona":"त्रिकोण","upachaya":"उपचय",
                         "dusthana":"दुस्थान","maraka":"मारक","panaphara":"पणफर","apoklima":"अपोक्लिम"}"""
                         
    content = content.replace(old_dignity_class_ta, new_dignity_class_hi)
    content = content.replace("DIGNITY_TA", "DIGNITY_HI")
    content = content.replace("CLASS_TA", "CLASS_HI")
    content = content.replace("dignity_ta", "dignity_hi")
    content = content.replace("class_ta", "class_hi")
    content = content.replace('f"நிலை: {dignity_hi}  |  வீட்டு வகை: {class_hi}"', 'f"स्थिति: {dignity_hi}  |  भाव प्रकार: {class_hi}"')
    content = content.replace('f"முக்கிய விளைவு: {outcome}"', 'f"मुख्य प्रभाव: {outcome}"')
    content = content.replace('"(விரிவான விளக்கம் ப்ருகு பத்திரிகா மூல ஹிந்தி நூலில் உள்ளது)"', '"(विस्तृत विवरण भृगु संहिता मूल संस्कृत ग्रंथ में उपलब्ध है)"')
    content = content.replace('f"({lagna_en} லக்னத்திற்கு ப்ருகு பத்திரிகா விதிகள் கிடைக்கவில்லை — "', 'f"({lagna_en} लग्न के लिए भृगु संहिता नियम नहीं मिले — "')
    content = content.replace('"உங்கள் சில கிரக அமைப்புகள் வழக்கத்திற்கு மாறானவை)"', '"आपकी कुछ ग्रह स्थितियां सामान्य से भिन्न हैं)"')

    # 9. Chart and table labels
    content = content.replace(
        '"ராசி சக்கரம் (D1) உங்கள் முக்கிய பிறப்பு ஜாதகம் — இந்த வாழ்க்கையை காட்டுகிறது. "',
        '"राशि चक्र (D1) आपकी मुख्य जन्म कुंडली है — यह आपके जीवन को दर्शाता है। "'
    )
    content = content.replace(
        '"நவாம்சம் (D9) என்பது திருமணம், தர்மம் மற்றும் உள் வலிமைகளுக்கான பிரிவு சக்கரம். "',
        '"नवमांश (D9) विवाह, धर्म और आंतरिक शक्ति का विभाग चक्र है। "'
    )
    content = content.replace(
        '"தென்னிந்திய பெட்டி அமைப்பு. ★ = லக்னம்."',
        '"दक्षिण भारतीय बॉक्स लेआउट। ★ = लग्न।"'
    )
    content = content.replace(
        '"கிரக சுருக்கம்: சூ=சூரியன், ச=சந்திரன், செ=செவ்வாய், "',
        '"ग्रह संक्षेप: सू=सूर्य, च=चन्द्र, मं=मंगल, "'
    )
    content = content.replace(
        '"பு=புதன், கு=குரு, சுக்=சுக்கிரன், சனி=சனி, ரா=ராகு, கே=கேது"',
        '"बु=बुध, गु=गुरु, शु=शुक्र, श=शनि, रा=राहु, के=केतु"'
    )
    
    # 10. Chart titles
    content = content.replace('f"ராசி (D1)  லக்.: {_hi_rasi(lagna_rasi)}"', 'f"राशि चक्र (D1)  लग्न: {_hi_rasi(lagna_rasi)}"')
    content = content.replace('f"நவாம்சம் (D9)  லக்.: {_hi_rasi(d9_lagna)}"', 'f"नवमांश (D9)  लग्न: {_hi_rasi(d9_lagna)}"')
    content = content.replace('"(நவாம்சம் கணக்கீடு தோல்வி)"', '"(नवमांश गणना विफल)"')
    
    # 11. 12 Houses Definitions
    content = content.replace('"12 பாவங்கள் (வீடுகள்) — அர்த்தம்"', '"12 भाव (घर) — अर्थ"')
    content = content.replace('TP(f"{r1}. {name1} — {mean1}", "cell_bold")', 'TP(f"{r1}. {name1} — {mean1}", "cell_bold")')
    content = content.replace('TP(f"{r2}. {name2} — {mean2}", "cell_bold")', 'TP(f"{r2}. {name2} — {mean2}", "cell_bold")')

    # 12. Vimshottari Timeline headers and markers
    content = content.replace(
        '"உங்கள் வாழ்க்கை 9 பெரிய அத்தியாயங்களாக விம்ஷோத்தரி கிரக கடிகாரத்தால் பிரிக்கப்பட்டுள்ளது. "',
        '"आपका जीवन विम्शोत्तरी ग्रह घड़ी द्वारा 9 प्रमुख अध्यायों में विभाजित है। "'
    )
    content = content.replace(
        '"ஒவ்வொரு அத்தியாயத்திற்கும் தனித்துவமான கருப்பொருள், உப-காலங்கள் மற்றும் "',
        '"प्रत्येक अध्याय का एक अनूठा विषय, उप-काल और "'
    )
    content = content.replace(
        '"செய்ய வேண்டியவை / தவிர்க்க வேண்டியவை ஆலோசனைகள் உள்ளன. "',
        '"क्या करें / क्या न करें सलाह है। "'
    )
    content = content.replace(
        '"முதலில் உங்கள் தற்போதைய அத்தியாயத்தைப் படியுங்கள்."',
        '"सबसे पहले अपना वर्तमान अध्याय पढ़ें।"'
    )
    content = content.replace(
        'marker = "▶ தற்போது" if is_current else ("✓ கடந்தது" if is_past else "→ எதிர்காலம்")',
        'marker = "▶ वर्तमान" if is_current else ("✓ अतीत" if is_past else "→ भविष्य")'
    )
    content = content.replace('f"அத்தியாயம் {idx}: {lord_hi} தசை"', 'f"अध्याय {idx}: {lord_hi} महादशा"')
    content = content.replace(
        'f"{fmt_my_hi(s)} → {fmt_my_hi(e)}    வயது {age_s} முதல் {age_e}    "',
        'f"{fmt_my_hi(s)} → {fmt_my_hi(e)}    आयु {age_s} से {age_e}    "'
    )
    content = content.replace('f"{(e-s).days // 365} ஆண்டுகள்    {marker}"', 'f"{(e-s).days // 365} वर्ष    {marker}"')
    content = content.replace('f"கருப்பொருள்: {MD_THEME_HI.get(lord, \'\')}"', 'f"मूल विषय: {MD_THEME_HI.get(lord, \'\')}"')
    content = content.replace('"இந்த அத்தியாயத்தில் எதிர்பார்க்க வேண்டியவை"', '"इस अध्याय में क्या उम्मीद करें"')
    content = content.replace('"கவனிக்க வேண்டியவை:"', '"सावधानी बरतने योग्य बातें:"')
    content = content.replace('"இந்த அத்தியாயத்தில் முன்னறிவிக்கப்பட்ட நிகழ்வுகள்"', '"इस अध्याय में पूर्व-संकेतित घटनाक्रम"')
    content = content.replace(
        'flow.append(TP(f"•  வயது {age_ev} ({label}) — {text} {stars}", "bullet"))',
        'flow.append(TP(f"•  आयु {age_ev} ({label}) — {text} {stars}", "bullet"))'
    )
    content = content.replace('"உப அத்தியாயங்கள் (Antardashas)"', '"उप अध्याय (अंतर्दशा)"')
    content = content.replace('f"{lord_hi} தசையில் செய்ய வேண்டியவை"', 'f"{lord_hi} महादशा में क्या करें"')
    content = content.replace('f"{lord_hi} தசையில் தவிர்க்க வேண்டியவை"', 'f"{lord_hi} महादशा में क्या न करें"')
    
    # 13. Canvas footer and page numbering
    content = content.replace(
        'draw_tamil(canvas, f"பக்கம் {doc.page}", A4[0]/2 - 30, 0.8*cm,',
        'draw_tamil(canvas, f"पृष्ठ {doc.page}", A4[0]/2 - 30, 0.8*cm,'
    )
    content = content.replace('font_name="Tamil", font_size=9, color=GREY_MD)', 'font_name="Devanagari", font_size=9, color=GREY_MD)')
    
    # 14. Report printing and output naming
    content = content.replace('Building TAMIL DEEP PDF', 'Building HINDI DEEP PDF')
    content = content.replace('Tamil Life Reading', 'Hindi Life Reading')
    content = content.replace('_TAMIL.pdf', '_HINDI.pdf')

    # 15. Standard cover translation strings
    content = content.replace('இன்றைய தேதி:', 'आज की तिथि:')
    content = content.replace('தற்போதைய வயது:', 'वर्तमान आयु:')
    content = content.replace('வயது', 'वर्ष')
    content = content.replace('தற்போது நீங்கள் ', 'आप वर्तमान में ')
    content = content.replace(' தசையில் இருக்கிறீர்கள், இது ', ' महादशा में हैं, जो ')
    content = content.replace(' வரை நீடிக்கும் (இன்னும் ', ' तक चलेगी (अभी ')
    content = content.replace(' ஆண்டுகள்). இந்த தசையின் முக்கிய கருப்பொருள்: ', ' वर्ष शेष)। इस महादशा का मूल विषय: ')
    content = content.replace('தற்போது', 'वर्तमान में')
    content = content.replace('தசையின்', 'महादशा का')
    
    # 16. South Indian box chart names mapping for Hindi
    south_indian_planets_ta = """        planets_ta = "".join(PLANETS_TA_SHORT.get(p, p[:2]) for p in cell_planets)"""
    south_indian_planets_hi = """        planets_ta = "".join(PLANETS_HI_SHORT.get(p, p[:2]) for p in cell_planets)"""
    content = content.replace(south_indian_planets_ta, south_indian_planets_hi)
    
    # 17. Clean up double-replacement suffixes to avoid _HI_HI
    content = content.replace("SECTION_HEADERS_HI_HI", "SECTION_HEADERS_HI")
    content = content.replace("LABELS_HI_HI", "LABELS_HI")
    content = content.replace("PLANETS_HI_HI", "PLANETS_HI")
    content = content.replace("PLANETS_HI_SHORT_HI", "PLANETS_HI_SHORT")
    content = content.replace("RASIS_HI_HI", "RASIS_HI")
    content = content.replace("NAKSHATRAS_HI_HI", "NAKSHATRAS_HI")
    content = content.replace("WEEKDAYS_HI_HI", "WEEKDAYS_HI")
    content = content.replace("TITHIS_HI_HI", "TITHIS_HI")
    content = content.replace("PAKSHA_HI_HI", "PAKSHA_HI")
    content = content.replace("KARANAS_HI_HI", "KARANAS_HI")
    content = content.replace("YOGAS_PANCH_HI_HI", "YOGAS_PANCH_HI")
    content = content.replace("HOUSES_HI_HI", "HOUSES_HI")
    content = content.replace("MD_THEME_HI_HI", "MD_THEME_HI")
    content = content.replace("MD_EXPECT_HI_HI", "MD_EXPECT_HI")
    content = content.replace("EVENT_PLAIN_HI_HI", "EVENT_PLAIN_HI")
    content = content.replace("YOGA_PLAIN_HI_HI", "YOGA_PLAIN_HI")
    content = content.replace("PLANET_KARAKAS_HI_HI", "PLANET_KARAKAS_HI")
    content = content.replace("HOUSE_NAMES_HI_FULL_HI", "HOUSE_NAMES_HI_FULL")
    content = content.replace("HOUSES_HI_HI", "HOUSES_HI")

    # Write the target file
    print(f"Writing {target_path}...")
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
