import sys
import re

debug_path = '/opt/astro/runtime/event_predictor_v2_recovered_debug.py'
dest_path = '/opt/astro/runtime/event_predictor_v2.py'

lines = open(debug_path, 'r', encoding='utf-8').read().splitlines()

# Known replacements for lambda expressions
LAMBDA_REPLACEMENTS = {
    "jup_to_sun": 'next((t for t in tr if t.get("transit") == "Jupiter" and t.get("natal") == "Sun"), None)',
    "sade": 'next((t for t in tr if t.get("type") == "sade_sati"), None)',
    "mars_moon": 'next((t for t in tr if t.get("transit") == "Mars" and t.get("natal") == "Moon"), None)',
    "sat_moon": 'next((t for t in tr if t.get("transit") == "Saturn" and t.get("natal") == "Moon"), None)',
    "sat_to_lagna": 'next((t for t in tr if t.get("transit") == "Saturn" and t.get("natal") == "Sun"), None)',
    "eclipse_sun": 'next((t for t in tr if t.get("type") == "eclipse" and t.get("natal") == "Sun"), None)',
    "eclipse_moon": 'next((t for t in tr if t.get("type") == "eclipse" and t.get("natal") == "Moon"), None)',
    "rahu_to_sun": 'next((t for t in tr if t.get("transit") == "Rahu" and t.get("natal") == "Sun"), None)',
    "sret": 'next((t for t in tr if t.get("type") == "saturn_return"), None)',
    "sun_h10": 'next((t for t in tr if t.get("transit") == "Sun" and t.get("natal") == "10H"), None)',
    "mars_to_mars": 'next((t for t in tr if t.get("transit") == "Mars" and t.get("natal") == "Mars"), None)',
    "dyoga": 'next((y for y in yogas if y["name"] == "Dhana Yoga"), None)',
    "hamsa": 'next((y for y in yogas if y["name"] in ("Hamsa Yoga", "Bhadra Yoga", "Ruchaka Yoga", "Malavya Yoga", "Shasha Yoga")), None)',
    "rogayoga": 'next((y for y in yogas if y["name"] == "Roga Yoga"), None)',
    "sat_venus": 'next((t for t in tr if t.get("transit") == "Saturn" and t.get("natal") == "Venus"), None)',
    "raja": 'next((y for y in yogas if y["name"] == "Raja Yoga"), None)',
}

# ----------------------------------------------------
# Apply base function replacements
# ----------------------------------------------------

# 1. event_mother (lines 634 to 681 -> index 633 to 681)
if lines[633].startswith("def event_mother"):
    mother_code = """def event_mother(chart, ds, tr, yogas, age):
    matr = next((y for y in yogas if y["name"]=="Matra Dosha"), None)
    pos = chart["positions"]
    lagna_idx = chart.get("lagna_idx", 0)
    h4_lord = _lord(lagna_idx, 4)
    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad"); pd = ds.get(3,{}).get("pd")
    score = 0; why = []

    if matr:
        score += 2; why.append("Matra Dosha base")

    if md == "Moon" or ad == "Moon" or pd == "Moon":
        score += 2; why.append("Moon period")

    # 4L period
    if md == h4_lord:
        score += 4; why.append(f"4L ({h4_lord}) MD")
    elif ad == h4_lord:
        score += 2; why.append(f"4L ({h4_lord}) AD")
    elif pd == h4_lord:
        score += 1; why.append(f"4L ({h4_lord}) PD")

    # Maraka/Dusthana from Moon or 4H
    moon_pos = pos.get("Moon", {})
    moon_rasi = moon_pos.get("rasi", "Aries")
    rasi_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    mother_marakas = set()
    if moon_rasi in rasi_names:
        moon_rasi_idx = rasi_names.index(moon_rasi)
        moon_maraka = (_lord(moon_rasi_idx, 2), _lord(moon_rasi_idx, 7), _lord(moon_rasi_idx, 12))
        h4_rasi_idx = (lagna_idx + 3) % 12
        h4_maraka = (_lord(h4_rasi_idx, 2), _lord(h4_rasi_idx, 7), _lord(h4_rasi_idx, 12))
        mother_marakas = set(moon_maraka + h4_maraka)
        if ad in mother_marakas:
            score += 2; why.append(f"AD ({ad}) is maraka/dusthana for Mother")
        if pd in mother_marakas:
            score += 1; why.append(f"PD ({pd}) is maraka/dusthana for Mother")

    # Check if MD or AD is in 4H
    if md and md in pos and pos[md]["house"] == 4:
        score += 2; why.append(f"MD ({md}) in 4H")
    elif ad and ad in pos and pos[ad]["house"] == 4:
        score += 2; why.append(f"AD ({ad}) in 4H")

    # Transit triggers
    sat_moon = next((t for t in tr if t["transit"]=="Saturn" and t["natal"]=="Moon"), None)
    if sat_moon:
        score += 3; why.append(f"Saturn over Moon (orb {sat_moon['orb']}°)")
    sade = next((t for t in tr if t["type"]=="sade_sati"), None)
    if sade:
        score += 2; why.append(sade["label"])

    if score < 4: return None
    mother_loss = ad in mother_marakas or md in mother_marakas
    return {
        "event":"Mother health / wellbeing event",
        "category":"mother",
        "severity":max(3, min(5, score//2)),
        "predicted_valence": _pv(inauspicious=mother_loss),
        "yoga":matr["name"] if matr else None,
        "why":why,
        "source":"Moon + 4L + Saturn transits (BPHS Shapit Yogas + Sade Sati)",
    }"""
    lines[633:681] = mother_code.splitlines()

# 2. event_career_breakthrough (lines 164 to 172 -> index 163 to 172)
if lines[163].startswith("def event_career_breakthrough"):
    career_code = """def event_career_breakthrough(chart, ds, tr, yogas, age):
    \"\"\"Career breakthrough — modern + classical rules.
    Catches: traditional 10L activations + Rahu/Saturn rules for modern careers
    (tech/foreign/govt/sports/film) when those planets are in career-significant houses.
    \"\"\"
    if age < 8 or age > 75: return None  # child-stars (Vijay Vetri age 10, Kamal Haasan age 4-6 debuts)
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    h10_lord = _lord(lagna_idx, 10)
    h11_lord = _lord(lagna_idx, 11)
    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad"); pd = ds.get(3,{}).get("pd")
    score = 0; why = []

    # ── Lagna Lord and Yogakaraka triggers ──
    lagna_lords = {
        "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
        "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
        "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
    }
    rasi_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    if 0 <= lagna_idx < 12:
        lagna_name = rasi_names[lagna_idx]
        lagna_lord = lagna_lords.get(lagna_name)
        yogakarakas = {
            "Taurus": "Saturn", "Cancer": "Mars", "Leo": "Mars", "Libra": "Saturn",
            "Capricorn": "Venus", "Aquarius": "Venus"
        }
        yk = yogakarakas.get(lagna_name)
        if md == lagna_lord:
            score += 2; why.append(f"Lagna Lord ({lagna_lord}) MD — rise & self-actualization")
        elif ad == lagna_lord:
            score += 1; why.append(f"Lagna Lord ({lagna_lord}) AD")
        if yk and md == yk:
            score += 3; why.append(f"Yogakaraka ({yk}) MD — luck and career rise")
        elif yk and ad == yk:
            score += 2; why.append(f"Yogakaraka ({yk}) AD — career surge")

    # ── Classical: 10L activation ──
    if md == h10_lord:
        score += 3; why.append(f"10L ({h10_lord}) MD")
    elif ad == h10_lord:
        score += 2; why.append(f"10L ({h10_lord}) AD")
    elif pd == h10_lord:
        score += 1; why.append(f"10L ({h10_lord}) PD")

    # ── Classical: 11L (gains) activation — career often shows as income peak ──
    if md == h11_lord and h11_lord != h10_lord:
        score += 2; why.append(f"11L ({h11_lord}) MD — gains/income peak")
    elif ad == h11_lord and h11_lord != h10_lord:
        score += 1; why.append(f"11L ({h11_lord}) AD — income surge")

    # ── Sun activation (authority karaka) ──
    if md == "Sun":
        score += 2; why.append("Sun MD (authority karaka)")
    elif ad == "Sun":
        score += 1; why.append("Sun AD")

    # ── MODERN: Rahu MD as career-active when placed strongly ──
    # Rahu in 10H/11H/2H = unconventional career rise (tech/film/foreign/speculation)
    rahu_h = pos.get("Rahu", {}).get("house", 0)
    if md == "Rahu" and rahu_h in (1, 2, 3, 6, 10, 11):
        score += 3; why.append(f"Rahu MD with Rahu in H{rahu_h} (unconventional career rise)")
    elif ad == "Rahu" and rahu_h in (1, 2, 3, 6, 10, 11):
        score += 2; why.append(f"Rahu AD with Rahu in H{rahu_h}")
    # Rahu over 10H/lord activates modern career
    elif md in ("Rahu", "Ketu") and rahu_h in (10, 11):
        score += 2; why.append(f"{md} MD activates Rahu in career-house")

    # ── MODERN: Saturn MD = career when Saturn aspects 10H or placed strongly ──
    saturn_h = pos.get("Saturn", {}).get("house", 0)
    # Saturn aspects 3rd, 7th, 10th from itself
    saturn_aspects_10h = saturn_h in (1, 4, 8)  # houses from which Saturn's 3/7/10 aspect hits 10H
    if md == "Saturn" and (saturn_h in (2, 10, 11) or saturn_aspects_10h):
        score += 3; why.append(f"Saturn MD (in H{saturn_h}) activates career")
    elif ad == "Saturn" and (saturn_h in (2, 10, 11) or saturn_aspects_10h):
        score += 2; why.append(f"Saturn AD activates career")

    # ── MODERN: Mercury MD = business / writing / communication career ──
    merc_h = pos.get("Mercury", {}).get("house", 0)
    if md == "Mercury" and merc_h in (1, 2, 5, 10, 11):
        score += 2; why.append(f"Mercury MD (in H{merc_h}) — business/communication career")

    # ── Raja Yoga activation ──
    raja = next((y for y in yogas if y["name"] == "Raja Yoga"), None)
    if raja and (md in ["Mercury", "Mars", "Jupiter"] or ad in ["Mercury", "Mars", "Jupiter"]):
        score += 1; why.append("Raja Yoga lord activates")

    # ── Jupiter MD natural expansion ──
    if md == "Jupiter":
        if 18 <= age <= 35:
            score += 2; why.append("Jupiter MD — career expansion + first major roles")
        else:
            score += 1; why.append("Jupiter MD — late-career expansion")

    # ── Transit boost: Jupiter or Saturn transit over 10L ──
    jup_to_10l = next((t for t in tr if t.get("transit") == "Jupiter"
                       and t.get("natal") == h10_lord
                       and t.get("severity") in ("HIGH", "MEDIUM")), None)
    if jup_to_10l:
        score += 2; why.append(f"Jupiter transits 10L ({h10_lord})")

    sat_to_10h = next((t for t in tr if t.get("transit") == "Saturn"
                       and t.get("natal") == h10_lord
                       and t.get("severity") in ("HIGH", "MEDIUM")), None)
    if sat_to_10h:
        score += 1; why.append(f"Saturn transits 10L (career-test)")

    # ── JAIMINI CHARA DASHA CONFLUENCE (Tier 1.3 for career) ──────────────
    try:
        from char_dasha import char_dasha
        import datetime as _dt
        if "_char_dasha_periods" not in chart:
            chart["_char_dasha_periods"] = char_dasha(chart)
        bd = chart["birth"]
        when_dt = _dt.datetime(bd["year"], bd["month"], bd["day"]) + _dt.timedelta(days=int(age * 365.25))
        active_char = next((p for p in chart["_char_dasha_periods"]
                            if p["start"] <= when_dt <= p["end"]), None)
        if active_char:
            char_lord = active_char.get("lord")
            char_sign_idx = active_char.get("sign_idx")
            tenth_from_lagna = (lagna_idx + 9) % 12
            sun_rasi_idx = pos.get("Sun", {}).get("rasi_idx", -1)
            char_active_career = (
                char_lord in ("Sun", "Saturn", "Mercury")
                or char_sign_idx == tenth_from_lagna
                or char_sign_idx == sun_rasi_idx
                or char_lord == h10_lord
            )
            if char_active_career:
                score += 2; why.append(f"Chara Dasha {active_char['sign']} ({char_lord}) — career confluence")
    except Exception:
        pass

    # ── KARKA RULE: Sun + Saturn transit timing (Tier 1.5) ───────────────
    # Career manifests when Sun karaka activates AND Jupiter transits the 10L
    sun_in_md_ad = (md == "Sun" or ad == "Sun" or pd == "Sun")
    if sun_in_md_ad:
        jup_to_sun = next((t for t in tr if t.get("transit") == "Jupiter"
                           and t.get("natal") == "Sun"
                           and t.get("severity") in ("HIGH", "MEDIUM")), None)
        if jup_to_sun:
            score += 2; why.append("Sun-karaka + Jupiter transit = strong career trigger")

    # ── SATURN TRANSIT to 10H/10L (Tier 2) ────────────────────────────────
    sat_to_10l = next((t for t in tr if t.get("transit") == "Saturn"
                       and t.get("natal") == h10_lord
                       and t.get("severity") in ("HIGH", "MEDIUM")), None)
    if sat_to_10l:
        score += 1; why.append(f"Saturn transit 10L ({h10_lord}) — career change")

    # ── D10 DASHAMSA DASHA CONFLUENCE (BPHS Ch.25-30) ─────────────────────
    # BPHS explicitly says use D10 Vimshottari for career timing.
    try:
        from divisional_dasha import build_d10_dasha_timeline, lookup_d10_dasha, get_d10_lords_for_career
        import datetime as _dt
        if "_d10_dasha_tl" not in chart:
            chart["_d10_dasha_tl"] = build_d10_dasha_timeline(chart)
            chart["_d10_career_activators"] = get_d10_lords_for_career(chart)
        bd = chart["birth"]
        when_dt = _dt.datetime(bd["year"], bd["month"], bd["day"]) + _dt.timedelta(days=int(age * 365.25))
        d10_ds = lookup_d10_dasha(chart["_d10_dasha_tl"], when_dt)
        d10_md = d10_ds.get(1, {}).get("md")
        d10_ad = d10_ds.get(2, {}).get("ad")
        d10_pd = d10_ds.get(3, {}).get("pd")
        d10_activators = chart["_d10_career_activators"]
        if d10_md in d10_activators:
            score += 3; why.append(f"D10 MD ({d10_md}) is career-activator")
        elif d10_ad in d10_activators:
            score += 2; why.append(f"D10 AD ({d10_ad}) is career-activator")
        elif d10_pd in d10_activators:
            score += 1; why.append(f"D10 PD ({d10_pd}) is career-activator")
    except Exception:
        pass

    # Lower threshold (was 4) to catch more career events given expanded rules
    if score < 3: return None
    return {
        "event":"Career breakthrough / promotion / public recognition / award",
        "category":"career",
        "severity":max(3, min(5, score // 2 + 1)),
        "yoga":raja["name"] if raja else None,
        "why":why,
        "source":"BPHS Ch.25-30 (10L/11L) + D10 Dashamsa dasha + Modern career rules",
    }"""
    lines[163:172] = career_code.splitlines()

# 3. event_father (lines 48 to 143 -> index 47 to 143)
if lines[47].startswith("def event_father"):
    father_code = """def event_father(chart, ds, tr, yogas, age):
    \"\"\"Father health/career event. Pitra Dosha boosts but is not required.
    Catches childhood losses (Rahman age 9 1976) via Sun + 9H affliction alone.
    \"\"\"
    pyoga = next((y for y in yogas if y["name"] == "Pitra Dosha"), None)
    pos = chart["positions"]
    lagna_idx = chart.get("lagna_idx", 0)
    h9_lord = _lord(lagna_idx, 9)
    score = 0; why = []

    md = ds.get(1,{}).get("md"); ad = ds.get(2,{}).get("ad"); pd = ds.get(3,{}).get("pd")

    # Pitra Dosha boosts score
    if pyoga:
        score += 2; why.append("Pitra Dosha base")

    # Strong activator: Sun MD/AD/PD or 9th lord MD/AD/PD
    sun_periods = [md=="Sun", ad=="Sun", pd=="Sun"]
    if any(sun_periods):
        score += 3; why.append(f"Sun activated as {'MD' if sun_periods[0] else 'AD' if sun_periods[1] else 'PD'}")

    # 9H lord (father karaka) in MD/AD/PD
    if md == h9_lord:
        score += 4; why.append(f"9L ({h9_lord}) MD — father-house fully activated")
    elif ad == h9_lord:
        score += 2; why.append(f"9L ({h9_lord}) AD")
    elif pd == h9_lord:
        score += 1; why.append(f"9L ({h9_lord}) PD")

    # Maraka/Dusthana from Sun or 9H
    sun_pos = pos.get("Sun", {})
    sun_rasi = sun_pos.get("rasi", "Aries")
    rasi_names = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    father_marakas = set()
    if sun_rasi in rasi_names:
        sun_rasi_idx = rasi_names.index(sun_rasi)
        sun_maraka = (_lord(sun_rasi_idx, 2), _lord(sun_rasi_idx, 7), _lord(sun_rasi_idx, 12))
        h9_rasi_idx = (lagna_idx + 8) % 12
        h9_maraka = (_lord(h9_rasi_idx, 2), _lord(h9_rasi_idx, 7), _lord(h9_rasi_idx, 12))
        father_marakas = set(sun_maraka + h9_maraka)
        if ad in father_marakas:
            score += 2; why.append(f"AD ({ad}) is maraka/dusthana for Father")
        if pd in father_marakas:
            score += 1; why.append(f"PD ({pd}) is maraka/dusthana for Father")

    # Jupiter (secondary father karaka per Bhrigu + naisargika)
    if ad == "Jupiter" and md == h9_lord:
        score += 2; why.append("9L MD + Jupiter AD — father-karaka double activation")
    elif md == "Jupiter" and age > 40:
        score += 1; why.append("Jupiter MD — father-life-cycle (mature)")

    # Ketu MD specifically activates the 4-house karma
    if md == "Ketu":
        score += 2; why.append("Ketu MD — activates H4 karma")
    # Childhood father-loss often triggered by Saturn MD
    if md == "Saturn" and age < 15:
        score += 2; why.append("Saturn MD in childhood — paternal stress")

    # Sun debilitated
    sun_dig = _dig(pos, "Sun") if pos.get("Sun") else None
    if sun_dig == "Debil":
        score += 2; why.append("Sun debilitated natally")

    # Transit triggers
    sret = next((t for t in tr if t["type"] == "saturn_return"), None)
    if sret:
        score += 4; why.append(f"Saturn Return (orb {sret['orb']}°)")

    sat_sun = next((t for t in tr if t["transit"]=="Saturn" and t["natal"]=="Sun"), None)
    if sat_sun:
        score += 3; why.append(f"Saturn over Sun (orb {sat_sun['orb']}°)")

    mars_sun = next((t for t in tr if t["transit"]=="Mars" and t["natal"]=="Sun"), None)
    if mars_sun:
        score += 2; why.append(f"Mars on Sun (orb {mars_sun['orb']}°)")

    rahu_on_sun = next((t for t in tr if t["transit"]=="Rahu" and t["natal"]=="Sun"), None)
    if rahu_on_sun:
        score += 2; why.append("Rahu on natal Sun")

    h8_lord = _lord(lagna_idx, 8)
    if md == h9_lord and ad in (h8_lord, "Saturn", "Ketu", "Mars"):
        score += 3; why.append(f"9L MD + {ad} AD — father-life / loss of father window")
    if ad == h8_lord and md in ("Sun", h9_lord, "Saturn"):
        score += 2; why.append(f"8L ({h8_lord}) AD — father transition")

    if score < 4: return None
    father_loss = md == h9_lord and ad in (h8_lord, "Saturn", "Ketu", "Mars") or ad in father_marakas or md in father_marakas
    return {
        "event":"Father — health / career / life event",
        "category":"father",
        "severity":max(3, min(5, score//2)),
        "predicted_valence": _pv(inauspicious=father_loss),
        "yoga":pyoga["name"] if pyoga else None,
        "why":why,
        "source":"Sun + 9L + Saturn transits (BPHS Shapit Yogas + Phaladeepika Ch.13)",
    }"""
    lines[47:143] = father_code.splitlines()

# 4. Fix helper functions _occ and _pv
if lines[30].startswith("def _occ"):
    lines[30:33] = [
        "def _occ(pos, h):",
        '    return [p for p, pd in pos.items() if pd["house"] == h]',
        ""
    ]

for j in range(35, 45):
    if lines[j].startswith("def _pv"):
        lines[j:j+6] = [
            "def _pv(auspicious = False, inauspicious = False):",
            "    if inauspicious:",
            "        return 'inauspicious'",
            "    if auspicious:",
            "        return 'auspicious'",
            "    return 'neutral'",
            ""
        ]
        break

# ----------------------------------------------------
# Parse functions list from raw subscript line
# ----------------------------------------------------

func_list = []
first_subscript_idx = -1
for idx, line in enumerate(lines):
    if "ALL_PATTERNS_V2 = [][" in line or "_e = [][event_father]" in line or "_e = [][" in line:
        first_subscript_idx = idx
        func_list = re.findall(r'\[(\w+)\]', line)
        func_list = [f for f in func_list if f != ""]
        print(f"Reconstructed {len(func_list)} event function references from first subscript line at index {idx}!")
        break

if first_subscript_idx == -1:
    print("WARNING: Subscript line not found!")
    sys.exit(1)

# ----------------------------------------------------
# Global search and replace for decompiled lambdas
# ----------------------------------------------------

print("Applying global lambda search and replace...")
i = 0
while i < len(lines):
    line = lines[i]
    # Check for lambda decompyle warning
    if "= (lambda" in line and "pass# WARNING: Decompyle incomplete" in line:
        # We need to extract the variable name
        match = re.search(r'^\s*(\w+)\s*=\s*\(lambda', line)
        if match:
            var_name = match.group(1)
            # Find the next line which has the argument call
            next_idx = i + 1
            while next_idx < len(lines) and lines[next_idx].strip() == "":
                next_idx += 1
            
            if next_idx < len(lines) and ")(" in lines[next_idx]:
                # Extract argument name
                arg_match = re.search(r'\)\((\w+)', lines[next_idx])
                arg_name = arg_match.group(1) if arg_match else ""
                
                # Check if we have a replacement rule for this variable
                if var_name in LAMBDA_REPLACEMENTS:
                    lines[i] = re.sub(r'(\s*)\w+\s*=\s*\(lambda.*$', r'\1' + f"{var_name} = {LAMBDA_REPLACEMENTS[var_name]}", line)
                    lines[next_idx] = ""
                    print(f"  -> Globally fixed '{var_name}' at line {i+1} using {arg_name}")
                else:
                    print(f"  [WARN] Unknown lambda variable '{var_name}' at line {i+1}")

    # Handle chart.get('lagna_idx', 0) = None if md == 'Venus' else score += 1
    if "chart.get('lagna_idx'" in line:
        # Preserve indentation
        indent = re.match(r'^(\s*)', line).group(1)
        lines[i] = f"{indent}lagna_idx = chart.get('lagna_idx', 0)\n{indent}if md == 'Venus' or ad == 'Venus':\n{indent}    score += 1\n{indent}    why.append('Venus period')"
        print(f"  -> Fixed chart.get('lagna_idx') at line {i+1}")
        
    i += 1

# Clean up empty lines
lines = [l for l in lines if l != ""]

# Fix event_saturn_return specifically
for idx, line in enumerate(lines[:first_subscript_idx]):
    if "def event_saturn_return" in line:
        saturn_return_code = """def event_saturn_return(chart, ds, tr, yogas, age):
    \"\"\"Saturn return — 28-30, 56-60, 84-90 year cycles.\"\"\"
    if not (27 <= age <= 31 or 55 <= age <= 61 or 83 <= age <= 91):
        return None
    score = 4
    why = ["Saturn return age-window — maturity inflection point"]
    sret = next((t for t in tr if t.get("type") == "saturn_return"), None)
    if sret:
        score += 2
        why.append(f"Saturn return active (orb {sret.get('orb', '?')}°)")
    return {
        'event': 'Saturn return — major maturity / responsibility inflection',
        'category': 'saturn_return',
        'severity': min(5, score // 2 + 1),
        'yoga': None,
        'why': why,
        'source': "Saturn's 29.5-year orbital cycle (BPHS Ch.45 Ayur)"
    }"""
        jup_idx = idx
        while jup_idx < len(lines) and "def event_jupiter_return" not in lines[jup_idx]:
            jup_idx += 1
        lines[idx:jup_idx] = saturn_return_code.splitlines()
        print("Fixed event_saturn_return inside lines!")
        break

# Find first_subscript_idx again because saturn_return lines changed
first_subscript_idx = -1
for idx, line in enumerate(lines):
    if "ALL_PATTERNS_V2 = [][" in line or "_e = [][event_father]" in line or "_e = [][" in line:
        first_subscript_idx = idx
        break

# ----------------------------------------------------
# Reconstruct execution layer from first_subscript_idx to end of file
# ----------------------------------------------------

execution_layer_code = """ALL_PATTERNS_V2 = [
    """ + ", ".join(func_list) + """
]

try:
    from claude_categories import ALL_CATALOG_PATTERNS
    ALL_PATTERNS_V2 = ALL_PATTERNS_V2 + ALL_CATALOG_PATTERNS
except ImportError:
    pass


def _age_at(d, chart):
    b = chart["birth"]
    return (d - dt.datetime(b["year"], b["month"], b["day"])).days / 365.25


def scan_year_v2(chart, year, sample_days=10, min_severity=2):
    timeline = build_full_timeline(chart, levels=3)
    yogas = detect_all_yogas(chart)
    events_by_window = {}
    d = dt.datetime(year, 1, 1)
    end = dt.datetime(year, 12, 31)
    while d <= end:
        age = _age_at(d, chart)
        ds = lookup(timeline, d)
        tr = detect_triggers(chart, d, orb=2.5)
        for fn in ALL_PATTERNS_V2:
            ev = fn(chart, ds, tr, yogas, age)
            if not ev: continue
            if ev["severity"] < min_severity: continue
            key = ev["event"]
            if key not in events_by_window:
                events_by_window[key] = {**ev, "first":d, "last":d, "max_sev":ev["severity"], "max_why":ev["why"], "age":age}
            else:
                events_by_window[key]["last"] = d
                if ev["severity"] > events_by_window[key]["max_sev"]:
                    events_by_window[key]["max_sev"] = ev["severity"]
                    events_by_window[key]["max_why"] = ev["why"]
        d += dt.timedelta(days=sample_days)
    return events_by_window


def scan_lifetime_v2(chart, year_from, year_to, sample_days=10, min_severity=2):
    all_events = []
    for year in range(year_from, year_to + 1):
        ev = scan_year_v2(chart, year, sample_days=sample_days, min_severity=min_severity)
        for k, v in ev.items():
            v["year"] = year
            all_events.append(v)
    return all_events


def collapse_consecutive(events):
    \"\"\"Merge consecutive-year same-event windows into single lifecycle bands.\"\"\"
    by_event = {}
    for ev in events:
        by_event.setdefault(ev["event"], []).append(ev)
    bands = []
    for event_name, lst in by_event.items():
        lst.sort(key=lambda e: e["first"])
        cur = None
        for e in lst:
            if cur is None:
                cur = dict(e); cur["window_start"] = e["first"]; cur["window_end"] = e["last"]
            else:
                # gap < 6 months = same band
                gap = (e["first"] - cur["window_end"]).days
                if gap < 180:
                    cur["window_end"] = max(cur["window_end"], e["last"])
                    cur["max_sev"] = max(cur["max_sev"], e["max_sev"])
                    cur["max_why"] = e["max_why"] if e["max_sev"] >= cur["max_sev"] else cur["max_why"]
                else:
                    bands.append(cur)
                    cur = dict(e); cur["window_start"] = e["first"]; cur["window_end"] = e["last"]
        if cur:
            bands.append(cur)
    return sorted(bands, key=lambda b: b["window_start"])


_PRIMARY_KEYWORDS = (
    "7L (", "Venus MD", "10L (", "Jupiter transits natal 7L",
    "as AD", "benefic-stack", "Moon MD +", "Saturn MD",
)

_SECONDARY_KEYWORDS = (
    "Venus AD", "Venus PD", "Jupiter MD", "Jupiter AD",
    "Venus dispositor", "Jupiter transit", "Venus transit",
    "Sun activates", "MD + Venus PD",
)

_RANK_CONFIG = {
    "marriage": {
        "keep_top":      3,
        "rename_after":  "Relationship deepening / second-marriage potential",
        "rename_cat":    "relationship_phase",
    },
    "career":   {"keep_top": 8, "rename_after": None, "rename_cat": None},
    "honor":    {"keep_top": 6, "rename_after": None, "rename_cat": None},
    "wealth":   {"keep_top": 5, "rename_after": None, "rename_cat": None},
    "health":   {"keep_top": 4, "rename_after": None, "rename_cat": None},
    "death":    {"keep_top": 3, "rename_after": None, "rename_cat": None},
    "accident": {"keep_top": 4, "rename_after": None, "rename_cat": None},
    "children": {"keep_top": 3, "rename_after": None, "rename_cat": None},
    "spiritual":{"keep_top": 3, "rename_after": None, "rename_cat": None},
    "travel":   {"keep_top": 4, "rename_after": None, "rename_cat": None},
    "education":{"keep_top": 4, "rename_after": None, "rename_cat": None},
    "_default": {"keep_top": 4, "rename_after": None, "rename_cat": None},
}


def _score_window(band):
    why = band.get("max_why") or band.get("why") or []
    if isinstance(why, str):
        why = [why]

    primaries = sum(1 for w in why if any(k in w for k in _PRIMARY_KEYWORDS))
    secondaries = sum(1 for w in why if any(k in w for k in _SECONDARY_KEYWORDS)
                                       and not any(k in w for k in _PRIMARY_KEYWORDS))
    transit_boost = 1 if any("transit" in w.lower() for w in why) else 0
    sev = band.get("max_sev", band.get("severity", 3)) or 3

    ws = band.get("window_start"); we = band.get("window_end")
    try:
        duration_months = max((we - ws).days / 30.0, 1.0)
    except Exception:
        duration_months = 12.0
    density_factor = min(1.0, 18.0 / duration_months)

    base = primaries * 3 + secondaries + transit_boost
    return round(base * density_factor + sev, 1)


def _stars(score):
    if score >= 9: return "⭐⭐⭐", "STRONG"
    if score >= 6: return "⭐⭐",   "MODERATE"
    return "⭐", "POSSIBLE"


def rank_and_consume(bands):
    if not bands: return []
    by_cat = {}
    for b in bands:
        cat = b.get("category") or "_default"
        by_cat.setdefault(cat, []).append(b)

    ranked_all = []
    for cat, lst in by_cat.items():
        cfg = _RANK_CONFIG.get(cat, _RANK_CONFIG["_default"])
        for b in lst:
            b["score"] = _score_window(b)
            b["stars"], b["confidence"] = _stars(b["score"])

        lst.sort(key=lambda b: (-b["score"], b["window_start"]))
        kept = lst[: cfg["keep_top"]]

        if cfg["rename_after"] and len(kept) > 1:
            top = kept[0]
            top_peak = top["window_start"]
            for i, b in enumerate(kept[1:], start=2):
                if b["window_start"] > top_peak:
                    b["event"] = cfg["rename_after"]
                    b["category"] = cfg["rename_cat"]

        for i, b in enumerate(kept, start=1):
            b["rank"] = i

        ranked_all.extend(kept)
    return sorted(ranked_all, key=lambda b: b["window_start"])


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print("Scanning Manoj 1996-2050 with v2 predictor...")
    events = scan_lifetime_v2(chart, 1996, 2050, sample_days=10, min_severity=4)
    bands = collapse_consecutive(events)
    print(f"\\n{len(bands)} life-event bands detected (severity 4+ only):\\n")
    print(f"{'AGE':<5}{'WINDOW':<22}{'SEV':<7}{'CATEGORY':<14}{'EVENT':<50}")
    print("-"*98)
    for b in bands:
        age = _age_at(b["window_start"], chart)
        wf = b["window_start"].strftime("%b %Y")
        wt = b["window_end"].strftime("%b %Y")
        win = f"{wf} - {wt}" if wf != wt else wf
        sev = "*" * b["max_sev"]
        print(f"{age:<5.0f}{win:<22}{sev:<7}{b['category']:<14}{b['event'][:48]}")
"""

# Replace from first_subscript_idx to end of file
lines[first_subscript_idx:] = execution_layer_code.splitlines()

# Clean up empty lines
lines = [l for l in lines if l != ""]

# Verify compilation
content_str = "\n".join(lines) + "\n"
try:
    compile(content_str, '<string>', 'exec')
    print("SUCCESS: Code compiles cleanly!")
    open(dest_path, 'w', encoding='utf-8').write(content_str)
    print(f"Saved working engine to {dest_path}")
except SyntaxError as e:
    import traceback
    print("COMPILE ERROR:")
    traceback.print_exc()
    # Save the debug file to see where it failed
    open(dest_path, 'w', encoding='utf-8').write(content_str)
    print("Saved current state to destination anyway for further debugging.")
