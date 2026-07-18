"""
The classical 72-trait personal profile.

Most commercial Vedic reports advertise "72+ details" — this module
generates the full catalogue from the chart, drawing on existing
predictors (life_domains, accident, education, psychology) and adding
the missing ones (lucky numbers, body type, voice, etc.).

Categories:
    A. Body & Physical (10)
    B. Personality & Mind (10)
    C. Education (5)
    D. Career (10)
    E. Wealth (8)
    F. Relationships (10)
    G. Family (5)
    H. Travel & Foreign (3)
    I. Spirituality (5)
    J. Health & Longevity (6)

Total: 72 traits.
"""
from __future__ import annotations

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORD = {0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
             5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter",
             9: "Saturn", 10: "Saturn", 11: "Jupiter"}
SIGN_ELEMENT = {"Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
                "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
                "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
                "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"}
DOSHA_BY_ELEMENT = {"Fire": "Pitta", "Earth": "Kapha-Vata",
                    "Air": "Vata", "Water": "Kapha"}
LUCKY_DAY_BY_RASI = {
    "Aries": "Tuesday", "Scorpio": "Tuesday",
    "Taurus": "Friday", "Libra": "Friday",
    "Gemini": "Wednesday", "Virgo": "Wednesday",
    "Cancer": "Monday",
    "Leo": "Sunday",
    "Sagittarius": "Thursday", "Pisces": "Thursday",
    "Capricorn": "Saturday", "Aquarius": "Saturday",
}
LUCKY_COLOR_BY_LAGNA = {
    "Aries": "red, scarlet", "Taurus": "white, cream",
    "Gemini": "green, parrot-green", "Cancer": "white, silver",
    "Leo": "gold, orange-red", "Virgo": "green, leaf-green",
    "Libra": "white, pastel pink", "Scorpio": "red, maroon",
    "Sagittarius": "yellow, golden", "Capricorn": "blue, black, navy",
    "Aquarius": "blue, slate", "Pisces": "yellow, sea-green",
}
LUCKY_NUMBER_BY_PLANET = {
    "Sun": 1, "Moon": 2, "Jupiter": 3, "Rahu": 4, "Mercury": 5,
    "Venus": 6, "Ketu": 7, "Saturn": 8, "Mars": 9,
}
GEMSTONE_BY_PLANET = {
    "Sun": "Ruby", "Moon": "Pearl", "Mars": "Coral",
    "Mercury": "Emerald", "Jupiter": "Yellow Sapphire",
    "Venus": "Diamond", "Saturn": "Blue Sapphire",
    "Rahu": "Hessonite", "Ketu": "Cat's Eye",
}
DEITY_BY_PLANET = {
    "Sun": "Vishnu / Surya", "Moon": "Shiva / Parvati",
    "Mars": "Subrahmanya / Kartikeya", "Mercury": "Vishnu",
    "Jupiter": "Brihaspati / Indra", "Venus": "Lakshmi / Indrani",
    "Saturn": "Hanuman / Yama", "Rahu": "Durga", "Ketu": "Ganesha",
}


def _planet_house(chart, planet: str) -> int:
    lon = chart.positions.get(planet)
    if lon is None:
        return 0
    return ((int(lon // 30) - int(chart.lagna_lon // 30)) % 12) + 1


def _planet_sign(chart, planet: str) -> str:
    lon = chart.positions.get(planet)
    if lon is None:
        return ""
    return SIGNS[int(lon // 30)]


def _lord_of_house(chart, h: int) -> str:
    return SIGN_LORD[(int(chart.lagna_lon // 30) + h - 1) % 12]


def all_traits(chart) -> list[dict]:
    lagna = SIGNS[int(chart.lagna_lon // 30)]
    moon_sign = _planet_sign(chart, "Moon")
    sun_sign = _planet_sign(chart, "Sun")
    lagna_lord = chart.lagna_lord
    nak_moon = (chart.nakshatras or {}).get("Moon", {}).get("name", "")
    bs = getattr(chart, "bala_summary", {}) or {}
    strongest = (bs.get("strongest") or [None])[0]

    # Pre-compute domain predictions
    from engine import life_domains, education, accident, timeline
    career = life_domains.predict_career(chart)
    marriage = life_domains.predict_marriage(chart)
    children = life_domains.predict_children(chart)
    wealth = life_domains.predict_wealth(chart)
    foreign = life_domains.predict_foreign(chart)
    family = life_domains.predict_family(chart)
    psych = life_domains.predict_psychology(chart)
    spirit = life_domains.predict_spirituality(chart)
    longevity = life_domains.predict_longevity(chart)
    subjects = education.predict_subjects(chart, top_n=3)
    accidents = accident.detect_accident_patterns(chart)

    LAGNA_BUILD = {
        "Aries": "lean-muscular, athletic", "Taurus": "stocky, robust, plump-tendency",
        "Gemini": "tall, slender, expressive face",
        "Cancer": "round face, fair skin, soft body",
        "Leo": "broad shoulders, dignified bearing",
        "Virgo": "medium height, sharp features",
        "Libra": "graceful, well-proportioned, attractive",
        "Scorpio": "intense gaze, muscular, magnetic",
        "Sagittarius": "tall, athletic, large forehead",
        "Capricorn": "lean-bony, weathered look as ages",
        "Aquarius": "tall, distinctive features",
        "Pisces": "soft features, dreamy eyes, medium build",
    }
    LAGNA_VOICE = {
        "Aries": "loud, commanding", "Taurus": "deep, melodious",
        "Gemini": "fast, articulate", "Cancer": "soft, emotional",
        "Leo": "deep, authoritative", "Virgo": "clear, precise",
        "Libra": "smooth, pleasant", "Scorpio": "intense, hypnotic",
        "Sagittarius": "loud, philosophical", "Capricorn": "slow, deliberate",
        "Aquarius": "unconventional cadence", "Pisces": "soft, dreamy",
    }

    traits: list[dict] = []

    # ─── A. Body & Physical (10) ─────────────────────────────────────────
    traits.append({"n": 1, "cat": "Body & Physical", "trait": "Body type",
                   "value": LAGNA_BUILD.get(lagna, "—"), "source": f"Lagna {lagna}"})
    elem = SIGN_ELEMENT.get(lagna, "—")
    traits.append({"n": 2, "cat": "Body & Physical", "trait": "Constitution (Ayurvedic dosha)",
                   "value": DOSHA_BY_ELEMENT.get(elem, "—"),
                   "source": f"{lagna} → {elem} element"})
    traits.append({"n": 3, "cat": "Body & Physical", "trait": "Voice quality",
                   "value": LAGNA_VOICE.get(lagna, "—"),
                   "source": f"Lagna {lagna}"})
    sign_l1 = _planet_sign(chart, lagna_lord)
    traits.append({"n": 4, "cat": "Body & Physical", "trait": "Complexion",
                   "value": "fair-warm" if sign_l1 in ("Cancer", "Pisces", "Libra") else "wheatish to brown",
                   "source": f"Lagna-lord {lagna_lord} in {sign_l1}"})
    traits.append({"n": 5, "cat": "Body & Physical", "trait": "Walking gait",
                   "value": "steady" if elem in ("Earth", "Water") else "quick",
                   "source": f"Lagna element {elem}"})
    traits.append({"n": 6, "cat": "Body & Physical", "trait": "Sleep pattern",
                   "value": "deep / long" if "Moon" in (lagna_lord,) or moon_sign in ("Cancer", "Pisces", "Taurus") else "light / short",
                   "source": f"Moon in {moon_sign}"})
    traits.append({"n": 7, "cat": "Body & Physical", "trait": "Eating preference",
                   "value": "warm/spicy" if elem == "Fire" else ("sweet/dairy" if elem == "Water" else ("light/varied" if elem == "Air" else "heavy/grounding")),
                   "source": f"Lagna element {elem}"})
    traits.append({"n": 8, "cat": "Body & Physical", "trait": "Lucky colour",
                   "value": LUCKY_COLOR_BY_LAGNA.get(lagna, "—"),
                   "source": f"Lagna {lagna}"})
    traits.append({"n": 9, "cat": "Body & Physical", "trait": "Lucky number",
                   "value": LUCKY_NUMBER_BY_PLANET.get(lagna_lord, "—"),
                   "source": f"Lagna-lord {lagna_lord}"})
    traits.append({"n": 10, "cat": "Body & Physical", "trait": "Lucky day",
                   "value": LUCKY_DAY_BY_RASI.get(moon_sign, "—"),
                   "source": f"Moon-sign {moon_sign}"})

    # ─── B. Personality & Mind (10) ──────────────────────────────────────
    traits.append({"n": 11, "cat": "Personality & Mind", "trait": "Core temperament",
                   "value": psych["summary"].split(".")[0],
                   "source": f"Moon in {moon_sign}"})
    traits.append({"n": 12, "cat": "Personality & Mind", "trait": "Strongest planet",
                   "value": strongest or "—",
                   "source": "Shadbala summary"})
    traits.append({"n": 13, "cat": "Personality & Mind", "trait": "Weakest planet",
                   "value": (bs.get("weakest") or [None])[0] or "—",
                   "source": "Shadbala summary"})
    traits.append({"n": 14, "cat": "Personality & Mind", "trait": "Communication style",
                   "value": "fast & verbal" if _planet_sign(chart, "Mercury") in ("Gemini", "Virgo", "Aquarius") else ("careful & deliberate" if _planet_sign(chart, "Mercury") in ("Taurus", "Capricorn") else "moderate"),
                   "source": f"Mercury in {_planet_sign(chart, 'Mercury')}"})
    traits.append({"n": 15, "cat": "Personality & Mind", "trait": "Decision-making",
                   "value": "intuitive" if elem == "Water" else ("logical" if elem == "Air" else ("driven" if elem == "Fire" else "cautious")),
                   "source": f"Lagna {elem}"})
    traits.append({"n": 16, "cat": "Personality & Mind", "trait": "Anger pattern",
                   "value": "quick-fire" if _planet_sign(chart, "Mars") in ("Aries", "Scorpio") else ("slow-burn" if _planet_sign(chart, "Mars") in ("Capricorn", "Taurus") else "moderate"),
                   "source": f"Mars in {_planet_sign(chart, 'Mars')}"})
    traits.append({"n": 17, "cat": "Personality & Mind", "trait": "Fear pattern",
                   "value": "loss/abandonment" if _planet_house(chart, "Saturn") in (1, 4, 8, 12) else "social/judgement",
                   "source": f"Saturn in H{_planet_house(chart, 'Saturn')}"})
    traits.append({"n": 18, "cat": "Personality & Mind", "trait": "Hidden strength",
                   "value": f"{strongest} domain" if strongest else "—",
                   "source": "shadbala"})
    traits.append({"n": 19, "cat": "Personality & Mind", "trait": "Friendship pattern",
                   "value": "loyal-deep" if _planet_house(chart, "Venus") in (1, 5, 11) else "selective",
                   "source": f"Venus in H{_planet_house(chart, 'Venus')}"})
    traits.append({"n": 20, "cat": "Personality & Mind", "trait": "Enemy pattern",
                   "value": "open-confrontational" if _planet_house(chart, "Mars") in (3, 6, 11) else "subtle/unseen",
                   "source": f"Mars in H{_planet_house(chart, 'Mars')}"})

    # ─── C. Education (5) ────────────────────────────────────────────────
    traits.append({"n": 21, "cat": "Education", "trait": "Primary subject area",
                   "value": subjects[0].field if subjects else "—",
                   "source": f"D24 + 5L + Mercury convergence (score {subjects[0].score:.1f})" if subjects else "—"})
    traits.append({"n": 22, "cat": "Education", "trait": "Secondary subject lean",
                   "value": subjects[1].field if len(subjects) > 1 else "—",
                   "source": "second-strongest"})
    traits.append({"n": 23, "cat": "Education", "trait": "Higher studies abroad?",
                   "value": foreign["likelihood"],
                   "source": f"Rahu in H{foreign['rahu_house']}"})
    traits.append({"n": 24, "cat": "Education", "trait": "Competitive exam success",
                   "value": "favoured" if _planet_house(chart, "Mercury") in (1, 5, 9, 10, 11) else "needs effort",
                   "source": f"Mercury in H{_planet_house(chart, 'Mercury')}"})
    traits.append({"n": 25, "cat": "Education", "trait": "Teacher / guru bond",
                   "value": "strong" if _planet_house(chart, "Jupiter") in (1, 5, 9, 4, 10) else "moderate",
                   "source": f"Jupiter in H{_planet_house(chart, 'Jupiter')}"})

    # ─── D. Career (10) ──────────────────────────────────────────────────
    traits.append({"n": 26, "cat": "Career", "trait": "Primary industry lean",
                   "value": career["industries_primary"],
                   "source": f"10th sign {SIGNS[(int(chart.lagna_lon//30)+9)%12]}"})
    traits.append({"n": 27, "cat": "Career", "trait": "Secondary industry",
                   "value": career["industries_secondary"],
                   "source": f"10th-lord placement"})
    h_sat = _planet_house(chart, "Saturn")
    traits.append({"n": 28, "cat": "Career", "trait": "Self-employed vs salaried",
                   "value": "self-employed lean" if h_sat in (3, 6, 11) else "salaried/structured lean",
                   "source": f"Saturn in H{h_sat}"})
    traits.append({"n": 29, "cat": "Career", "trait": "Manager vs maker",
                   "value": "manager/leader" if _planet_house(chart, "Sun") in (1, 10, 11) else "maker/specialist",
                   "source": f"Sun in H{_planet_house(chart, 'Sun')}"})
    traits.append({"n": 30, "cat": "Career", "trait": "Career peak window",
                   "value": "30s-40s" if h_sat in (10, 11, 1) else "40s-50s",
                   "source": f"Saturn"})
    traits.append({"n": 31, "cat": "Career", "trait": "Job-change frequency",
                   "value": "frequent" if _planet_house(chart, "Rahu") in (10, 11, 3) else "stable",
                   "source": f"Rahu in H{_planet_house(chart, 'Rahu')}"})
    traits.append({"n": 32, "cat": "Career", "trait": "Government vs private",
                   "value": "government / authority" if _planet_house(chart, "Sun") in (10, 11) else "private / corporate",
                   "source": f"Sun in H{_planet_house(chart, 'Sun')}"})
    traits.append({"n": 33, "cat": "Career", "trait": "Side income / second source",
                   "value": "yes" if _planet_house(chart, "Mercury") in (2, 11) else "primary only",
                   "source": f"Mercury in H{_planet_house(chart, 'Mercury')}"})
    traits.append({"n": 34, "cat": "Career", "trait": "Recognition timing",
                   "value": "during Sun/Jupiter mahadashas",
                   "source": "lord-of-recognition"})
    traits.append({"n": 35, "cat": "Career", "trait": "Authority over others",
                   "value": "strong" if _planet_house(chart, "Sun") in (1, 10) else "moderate",
                   "source": f"Sun in H{_planet_house(chart, 'Sun')}"})

    # ─── E. Wealth (8) ───────────────────────────────────────────────────
    # De-dup: split career-style industries from "savings/inheritance/gift" wealth sources
    WEALTH_TRANSLATE = {
        "civil engineering, government, mining, construction, large-scale industry":
            "savings + property + family inheritance (Saturn-domain assets)",
        "leadership, military, surgery, sports, mechanical/engineering":
            "earned income from active career (Mars/Sun-domain)",
        "finance, banking, agriculture, music, real estate, hospitality":
            "savings + property accumulation (Venus/Taurus-domain)",
        "communications, journalism, computers/IT, trade, writing, brokerage":
            "income from communication + small trade (Mercury-domain)",
        "hospitality, real estate, food, shipping, public service":
            "family/property/water-related wealth (Moon-domain)",
        "administration, government, gold/luxury, performing arts, executive":
            "authority-derived wealth (Sun-domain)",
        "accounting, analytics, medical practice, editing, quality control":
            "professional fees + analytical work (Mercury-domain)",
        "law, fashion, design, diplomacy, arts, cosmetics, partnerships":
            "partnership + creative work (Venus-domain)",
        "research, surgery/medicine, occult, investigation, biotech, defence":
            "research/surgery fees + hidden sources (Scorpio-domain)",
        "law, teaching, finance, religion, publishing, foreign trade, philosophy":
            "advisory/teaching fees + foreign income (Jupiter-domain)",
        "civil engineering, government, mining, construction, large-scale industry":
            "savings + long-term assets (Saturn-domain)",
        "technology, aerospace, humanitarian, IT, astrology, research":
            "technology + futuristic income (Aquarius-domain)",
        "spirituality, fine arts, marine industries, healthcare, philanthropy":
            "spiritual/artistic + hidden wealth (Pisces-domain)",
    }
    wealth_label = WEALTH_TRANSLATE.get(
        wealth["sources_primary"],
        f"savings via 2nd-house ({wealth['2nd_sign']}) lord activity"
    )
    gain_label = WEALTH_TRANSLATE.get(
        wealth["sources_gains"],
        f"gains via 11th-house ({wealth['11th_sign']}) lord activity"
    )
    traits.append({"n": 36, "cat": "Wealth", "trait": "Wealth-channel (savings axis)",
                   "value": wealth_label,
                   "source": f"2nd-sign {wealth['2nd_sign']}"})
    traits.append({"n": 37, "cat": "Wealth", "trait": "Wealth-channel (gains axis)",
                   "value": gain_label,
                   "source": f"11th-sign {wealth['11th_sign']}"})
    traits.append({"n": 38, "cat": "Wealth", "trait": "Wealth peak years",
                   "value": "Jupiter / Venus / Mercury mahadashas",
                   "source": "wealth karakas"})
    traits.append({"n": 39, "cat": "Wealth", "trait": "Asset preference",
                   "value": "real estate" if _planet_house(chart, "Mars") in (4,) else ("gold/jewellery" if _planet_house(chart, "Sun") in (2, 4) else "diversified financial"),
                   "source": "Mars/Sun house"})
    traits.append({"n": 40, "cat": "Wealth", "trait": "Saver vs spender",
                   "value": "saver" if _planet_sign(chart, "Saturn") in ("Capricorn", "Aquarius", "Taurus") else "balanced",
                   "source": f"Saturn in {_planet_sign(chart, 'Saturn')}"})
    traits.append({"n": 41, "cat": "Wealth", "trait": "Loan / debt tendency",
                   "value": "elevated" if _planet_house(chart, "Saturn") == 6 or _planet_house(chart, "Rahu") == 6 else "moderate",
                   "source": "6H lord/occupants"})
    traits.append({"n": 42, "cat": "Wealth", "trait": "Speculation / market",
                   "value": "favoured" if _planet_house(chart, "Mercury") in (5, 11) else "caution",
                   "source": f"Mercury in H{_planet_house(chart, 'Mercury')}"})
    traits.append({"n": 43, "cat": "Wealth", "trait": "Property/real-estate",
                   "value": "yes" if _planet_house(chart, "Mars") == 4 or _planet_house(chart, "Saturn") == 4 else "moderate",
                   "source": "4H occupants"})

    # ─── F. Relationships (10) ──────────────────────────────────────────
    traits.append({"n": 44, "cat": "Relationships", "trait": "Marriage age window",
                   "value": marriage["timing"],
                   "source": f"Venus in H{marriage['venus_house']}"})
    traits.append({"n": 45, "cat": "Relationships", "trait": "Spouse profile",
                   "value": marriage["spouse_profile"],
                   "source": f"7th sign {marriage['7th_sign']}"})
    traits.append({"n": 46, "cat": "Relationships", "trait": "Love vs arranged",
                   "value": "love-marriage lean" if _planet_house(chart, "Venus") == 5 or _planet_house(chart, "Mars") == 5 else "arranged or mixed",
                   "source": "5H occupants"})
    traits.append({"n": 47, "cat": "Relationships", "trait": "Mangal-dosha",
                   "value": "yes" if marriage["mangal_dosha"] else "no",
                   "source": f"Mars in H{_planet_house(chart, 'Mars')}"})
    traits.append({"n": 48, "cat": "Relationships", "trait": "Marriage harmony",
                   "value": "smooth" if _planet_house(chart, "Jupiter") in (1, 5, 7, 9) else "needs work",
                   "source": f"Jupiter in H{_planet_house(chart, 'Jupiter')}"})
    traits.append({"n": 49, "cat": "Relationships", "trait": "Number of marriages",
                   "value": "two-marriage signal" if _planet_house(chart, "Venus") in (7, 8) and _planet_house(chart, "Saturn") == 7 else "one",
                   "source": "Venus/Saturn 7H"})
    traits.append({"n": 50, "cat": "Relationships", "trait": "Children count tendency",
                   "value": children["count_lean"],
                   "source": f"5L in H{children['5th_lord_house']}"})
    traits.append({"n": 51, "cat": "Relationships", "trait": "Children gender lean",
                   "value": children["gender_lean"],
                   "source": f"5th sign {children['5th_sign']}"})
    traits.append({"n": 52, "cat": "Relationships", "trait": "Children's success",
                   "value": "favoured" if _planet_house(chart, "Jupiter") in (1, 5, 9) else "moderate",
                   "source": "Jupiter house"})
    traits.append({"n": 53, "cat": "Relationships", "trait": "Sexual / romantic life",
                   "value": "warm/active" if _planet_house(chart, "Venus") in (1, 5, 7, 11) else "moderate",
                   "source": f"Venus in H{_planet_house(chart, 'Venus')}"})

    # ─── G. Family (5) ────────────────────────────────────────────────────
    traits.append({"n": 54, "cat": "Family", "trait": "Father's status",
                   "value": "strong/elevated" if _planet_house(chart, "Sun") in (1, 9, 10) else "moderate or strained",
                   "source": f"Sun in H{family['father_indicator_house']}"})
    traits.append({"n": 55, "cat": "Family", "trait": "Mother's status",
                   "value": "strong" if _planet_house(chart, "Moon") in (1, 4, 9, 10) else "moderate",
                   "source": f"Moon in H{family['mother_indicator_house']}"})
    traits.append({"n": 56, "cat": "Family", "trait": "Sibling relationship",
                   "value": "close" if _planet_house(chart, "Mars") in (3, 11) else "distant or rival",
                   "source": f"Mars in H{family['siblings_indicator_house']}"})
    traits.append({"n": 57, "cat": "Family", "trait": "Inheritance",
                   "value": "favoured" if _planet_house(chart, "Jupiter") in (2, 4, 8, 11) else "limited",
                   "source": f"Jupiter in H{_planet_house(chart, 'Jupiter')}"})
    traits.append({"n": 58, "cat": "Family", "trait": "Family disputes",
                   "value": "elevated" if _planet_house(chart, "Mars") in (2, 4) or _planet_house(chart, "Rahu") in (2, 4) else "low",
                   "source": "2H/4H malefics"})

    # ─── H. Travel & Foreign (3) ─────────────────────────────────────────
    traits.append({"n": 59, "cat": "Travel & Foreign", "trait": "Foreign settlement",
                   "value": foreign["likelihood"],
                   "source": "; ".join(foreign["reasons"]) or "no strong indicator"})
    traits.append({"n": 60, "cat": "Travel & Foreign", "trait": "Foreign direction lean",
                   "value": foreign["direction"],
                   "source": f"Rahu sign"})
    traits.append({"n": 61, "cat": "Travel & Foreign", "trait": "Pilgrimage tendency",
                   "value": "strong" if _planet_house(chart, "Jupiter") in (9, 12) or _planet_house(chart, "Ketu") in (9, 12) else "moderate",
                   "source": "9H/12H spirituality"})

    # ─── I. Spirituality (5) ─────────────────────────────────────────────
    traits.append({"n": 62, "cat": "Spirituality", "trait": "Spiritual path",
                   "value": spirit["summary"].split("**")[1] if "**" in spirit["summary"] else "general dharmic",
                   "source": f"Ketu in {spirit['ketu_sign']}"})
    traits.append({"n": 63, "cat": "Spirituality", "trait": "Primary deity affinity",
                   "value": DEITY_BY_PLANET.get(strongest or chart.lagna_lord, "Vishnu"),
                   "source": f"strongest = {strongest}"})
    traits.append({"n": 64, "cat": "Spirituality", "trait": "Mantra/sadhana inclination",
                   "value": "strong" if _planet_house(chart, "Ketu") in (8, 12) else "moderate",
                   "source": f"Ketu in H{_planet_house(chart, 'Ketu')}"})
    traits.append({"n": 65, "cat": "Spirituality", "trait": "Guru relationship",
                   "value": "favoured" if _planet_house(chart, "Jupiter") in (5, 9) else "needs cultivation",
                   "source": f"Jupiter in H{_planet_house(chart, 'Jupiter')}"})
    traits.append({"n": 66, "cat": "Spirituality", "trait": "Religious participation",
                   "value": "regular" if _planet_house(chart, "Jupiter") in (1, 4, 9, 10) else "occasional",
                   "source": f"Jupiter house"})

    # ─── J. Health & Longevity (6) ───────────────────────────────────────
    traits.append({"n": 67, "cat": "Health & Longevity", "trait": "Vulnerable body parts",
                   "value": "; ".join(p.body_part for p in accidents[:2]) or "general healthy",
                   "source": "accident-pattern detector"})
    traits.append({"n": 68, "cat": "Health & Longevity", "trait": "Chronic illness tendency",
                   "value": "elevated" if any("chronic" in p.nature.lower() for p in accidents) else "low",
                   "source": "6H/8H lord pattern"})
    traits.append({"n": 69, "cat": "Health & Longevity", "trait": "Accident windows",
                   "value": "; ".join(set(d for p in accidents for d in p.peak_dashas)) or "—",
                   "source": "Mars/Saturn/Rahu dashas"})
    traits.append({"n": 70, "cat": "Health & Longevity", "trait": "Surgery likelihood",
                   "value": "elevated" if any("surger" in p.nature.lower() for p in accidents) else "low",
                   "source": "Mars-Saturn pattern"})
    traits.append({"n": 71, "cat": "Health & Longevity", "trait": "Mental health",
                   "value": "stable" if _planet_house(chart, "Moon") in (1, 4, 5, 9, 10, 11) else "needs care",
                   "source": f"Moon in H{_planet_house(chart, 'Moon')}"})
    traits.append({"n": 72, "cat": "Health & Longevity", "trait": "Longevity band",
                   "value": longevity["band"],
                   "source": "; ".join(longevity["reasons"]) or "standard"})

    return traits


def render_72_traits_markdown(chart) -> str:
    out = ["## ✦ The 72-Trait Personal Profile\n"]
    out.append(
        "Below is the classical 72-attribute checklist that a complete "
        "Vedic chart can describe — every trait is derived from a "
        "specific chart feature, with the source named so you can verify."
    )
    out.append("")
    traits = all_traits(chart)
    cats: dict[str, list] = {}
    for t in traits:
        cats.setdefault(t["cat"], []).append(t)
    for cat, items in cats.items():
        out.append(f"### {cat}")
        out.append("")
        out.append("| # | Trait | Your chart says | Source |")
        out.append("|---:|---|---|---|")
        for t in items:
            val = str(t["value"])
            if len(val) > 80:
                val = val[:77] + "…"
            src = str(t["source"])
            if len(src) > 60:
                src = src[:57] + "…"
            out.append(f"| {t['n']} | **{t['trait']}** | {val} | *{src}* |")
        out.append("")
    out.append(
        f"**Total traits surfaced:** {len(traits)} of 72."
    )
    return "\n".join(out)
