"""Face Reading v2 — extended Mukha Samudrika + Sariraka Lakshana body-appearance engine.

Builds on face_reading.py (v1: 7 face shapes + 8 feature categories).
v2 adds:
  - 12 hair types (curly/straight/thick/thin/bald + classical Vedic categories)
  - 7 skin textures (smooth/rough/oily/dry/etc.)
  - 5 body proportions (lagna-based: head/body, arm-length, leg-length, torso-vs-leg)
  - 9 voice qualities (pitch/tone/resonance) — by 2nd house + Mercury
  - 12 walking gaits (lion/elephant/deer/swan/etc.) — by Lagna sign element
  - 16 body marks/scars/defects predictive (location → meaning)
  - full_body_appearance_prediction(chart) → all 6 categories

Source: Mukha Samudrika Shastra, Sariraka Lakshana, Brihat Samhita Ch.61-64,
Hasta Sanjivana, Tantric Body-Mapping traditions.
"""
import sys
sys.path.insert(0, ".")
from vedic_core import (
    DIGNITIES, RASIS, RASI_LORDS, FIRE_SIGNS, EARTH_SIGNS, AIR_SIGNS, WATER_SIGNS,
    MOVABLE_SIGNS, FIXED_SIGNS, DUAL_SIGNS, planet_dignity, is_dignified,
    is_debilitated, planet_house, house_lord, house_lord_position, house_occupants,
    planets_conjunct, planet_aspects_houses,
)
# v1 imports kept available
from face_reading import (
    FOREHEAD, EYES, EYEBROWS, NOSE, LIPS, CHIN, EARS, CHEEKS, FACE_SHAPES,
    predict_face_features, face_reading_summary,
)


# ============================================================
# HAIR — 12 classical types (Kesha Lakshana)
# ============================================================
HAIR_TYPES = {
    "Straight, fine, glossy black": {
        "predicts": "Refined nature, aristocratic lineage, peaceful temperament, scholarly mind",
        "wealth": "Stable inherited wealth, respect in society",
        "health": "Strong constitution, balanced doshas (sattvic)",
        "matches_chart": "Venus + Moon strong, Pisces/Cancer/Taurus emphasis",
    },
    "Wavy, lustrous, dark-brown": {
        "predicts": "Romantic, artistic, charming presence",
        "wealth": "Earned through arts/relationships/charm",
        "health": "Vata-Pitta balance, aesthetic sensitivity",
        "matches_chart": "Venus dominant, Libra/Taurus emphasis",
    },
    "Tightly curly / kinky": {
        "predicts": "Strong-willed, intense temperament, passionate, possible foreign blood",
        "wealth": "Self-made through struggle, sudden gains possible",
        "health": "Pitta-prominent, hot constitution, ruddy complexion",
        "matches_chart": "Mars + Sun strong, Aries/Scorpio rising, Rahu in 1st",
    },
    "Thick, abundant, coarse black": {
        "predicts": "Robust, vital, possibly stubborn or animal-magnetic, primal energy",
        "wealth": "Hard-working accumulator, slow steady gains",
        "health": "Strong digestion, kapha-pitta robust",
        "matches_chart": "Saturn + Mars strong, fixed signs, Lagna lord well-placed",
    },
    "Thin, sparse, fine": {
        "predicts": "Sensitive, intellectual, possibly nervous, refined refined refined",
        "wealth": "Income through mental work, may have anxiety about money",
        "health": "Vata excess, weak immunity, nervous-system fragile",
        "matches_chart": "Mercury + Saturn weak, Pisces/Virgo Lagna",
    },
    "Receding hairline / early baldness (male)": {
        "predicts": "Strong intellect, ambitious career, may sacrifice domestic life for work",
        "wealth": "Career-built, status through profession",
        "health": "Pitta-excess, hormonal intensity (high testosterone classical)",
        "matches_chart": "Sun in Aries/Leo + 6H/10H, Mars in 1H/10H, Rahu-Sun afflict",
    },
    "Premature greying": {
        "predicts": "Mental burden carried young, philosophical, old-soul wisdom",
        "wealth": "Income through advisory/mentor roles",
        "health": "Stress-induced, possible thyroid imbalance",
        "matches_chart": "Saturn in 1H/2H, Saturn aspecting Moon, Sade-Sati during youth",
    },
    "Reddish / auburn tinge": {
        "predicts": "Fiery temperament, passionate, possible foreign ancestry",
        "wealth": "Quick gains/losses, speculative success",
        "health": "Pitta-dominant, prone to skin issues, hot blood",
        "matches_chart": "Mars in 1H, Sun own/exalt in 1H/2H, fire signs prominent",
    },
    "Light brown / golden": {
        "predicts": "Charming, social, often foreign or mixed-lineage influence",
        "wealth": "Through public-facing work, foreign sources",
        "health": "Vata-Pitta balanced, aesthetic body type",
        "matches_chart": "Venus + Sun strong, Rahu in 1H/9H/12H",
    },
    "Oily, heavy, thick growth": {
        "predicts": "Sensual, comfort-loving, possessive, attached to family",
        "wealth": "Comfortable, often inherited or through marriage",
        "health": "Kapha-dominant, slow metabolism, watch weight",
        "matches_chart": "Moon + Venus strong in earth/water signs, Cancer/Taurus Lagna",
    },
    "Dry, frizzy, brittle": {
        "predicts": "Restless, irritable, may have skin issues, anxious temperament",
        "wealth": "Erratic income, often spends impulsively",
        "health": "Vata-excess, dehydration tendency, joint stiffness in age",
        "matches_chart": "Saturn-afflicted Moon, Rahu+Saturn in 1H/4H, Vata constitution",
    },
    "White from young age (uncommon)": {
        "predicts": "Karmic/old-soul, possibly autoimmune marker, Saturn karma activated early",
        "wealth": "Late-life recognition, often spiritual/teaching career",
        "health": "Watch immune system, B12/melanin imbalance",
        "matches_chart": "Saturn in 1H, Ketu + Saturn conjunction, Sade-Sati at birth",
    },
}


# ============================================================
# SKIN — 7 classical textures (Twak Lakshana)
# ============================================================
SKIN_TEXTURES = {
    "Smooth, soft, glowing (Snigdha)": {
        "predicts": "Refined nature, sattvic disposition, comfortable life, beauty admired",
        "complexion_dosha": "Pitta-Kapha balanced",
        "matches_chart": "Venus + Moon strong, dignified Lagna lord, Taurus/Libra/Pisces Lagna",
        "auspicious": True,
    },
    "Rough, coarse (Kharara)": {
        "predicts": "Hardworking, manual life, may face skin issues, less refinement",
        "complexion_dosha": "Vata-excess",
        "matches_chart": "Saturn in 1H/2H, weak Venus, malefics aspecting Lagna",
        "auspicious": False,
    },
    "Oily, lustrous (Snigdha-medura)": {
        "predicts": "Sensual, comfort-loving, attractive, prone to acne in youth",
        "complexion_dosha": "Pitta + Kapha",
        "matches_chart": "Venus in 1H, Moon strong, water signs",
        "auspicious": True,
    },
    "Dry, scaly (Ruksha)": {
        "predicts": "Anxiety-prone, restless, may have eczema/psoriasis tendency",
        "complexion_dosha": "Vata-excess",
        "matches_chart": "Saturn afflicting Moon, Vata constitution, Rahu in 1H",
        "auspicious": False,
    },
    "Even-toned, clear (Sama-varna)": {
        "predicts": "Balanced karma, steady life, freedom from major skin diseases",
        "complexion_dosha": "Tridosha-balanced",
        "matches_chart": "Lagna lord dignified, no malefic in 1H",
        "auspicious": True,
    },
    "Blotchy / pigmented (Vivarna)": {
        "predicts": "Hormonal imbalance, may face liver issues, irregular karma",
        "complexion_dosha": "Pitta-excess + ama (toxins)",
        "matches_chart": "Sun-Mars affliction, 6H/8H emphasis, Rahu in 6H",
        "auspicious": False,
    },
    "Sensitive / reactive (Sukumara)": {
        "predicts": "Refined nervous system, artistic, allergy-prone, easily affected by environment",
        "complexion_dosha": "Vata-Pitta sensitive",
        "matches_chart": "Moon-Mercury weak, Pisces/Cancer Lagna, 12H emphasis",
        "auspicious": "mixed",
    },
}


# ============================================================
# BODY PROPORTIONS — 5 lagna-based ratios
# ============================================================
BODY_PROPORTIONS = {
    "Head-to-body ratio (1:7 = 'royal'; 1:8 = average; 1:6 = stocky)": {
        "1:7 (royal proportion)": "Aristocratic build, leadership, classical beauty marker",
        "1:8 (tall/slender)": "Intellectual, possibly artistic build",
        "1:6 (stocky/heavy)": "Strong physical presence, manual capability",
        "matches_chart": "Lagna sign + Lagna lord position; fire/fixed = stocky, air = tall, mutable = variable",
    },
    "Arm length (long/medium/short relative to torso)": {
        "long arms (reaching mid-thigh)": "Magnanimous, generous, leadership marker (classical king-sign)",
        "medium": "Standard balanced karma",
        "short arms": "Reserved, careful, may struggle to 'reach' opportunities",
        "matches_chart": "Jupiter strong + 11H = long; Saturn malefic in 1H = short",
    },
    "Leg length (long/medium/short)": {
        "long legs": "Travel-prone, restless, ambitious to move ahead",
        "medium": "Stable journey through life",
        "short legs": "Rooted, family-bound, slow but steady progress",
        "matches_chart": "9H/12H + Sagittarius emphasis = long; Cancer/Taurus = short",
    },
    "Torso (chest+belly) vs leg ratio (50:50 ideal; 60:40 stocky; 40:60 elongated)": {
        "50:50 (balanced)": "Harmonious karma, balanced action",
        "60:40 (long torso, short legs)": "Wealth-storer, family-bound, slow mover",
        "40:60 (short torso, long legs)": "Restless wanderer, travel-fated",
        "matches_chart": "Saturn-Jupiter ratio + 4H/9H balance",
    },
    "Shoulder width vs hip width (V-shape, hourglass, rectangular)": {
        "V-shape (wide shoulders, narrow hips)": "Action-oriented, masculine energy, athletic",
        "Hourglass (balanced shoulders + hips, narrow waist)": "Aesthetic build, classical beauty",
        "Rectangular (equal shoulders/hips)": "Practical, durable build",
        "Pear (narrow shoulders, wide hips)": "Nurturing, family-oriented, kapha-dominant",
        "matches_chart": "Mars-Venus balance; masculine signs = V-shape; feminine signs = hourglass/pear",
    },
}


# ============================================================
# VOICE — 9 qualities by 2nd house + Mercury
# ============================================================
VOICE_QUALITIES = {
    "Deep, resonant, commanding": {
        "predicts": "Authority, public speaker, born leader, voice carries weight",
        "career": "Public speaking, broadcasting, politics, teaching",
        "matches_chart": "Sun in 2H/3H, dignified Jupiter aspect 2H, fire signs in 2H",
    },
    "Sweet, melodious, musical": {
        "predicts": "Singer/artist potential, charming speech, magnetic personality",
        "career": "Music, performance, sales, hospitality",
        "matches_chart": "Venus in 2H/3H, Taurus/Libra in 2H, Moon-Venus aspect",
    },
    "Sharp, precise, clear": {
        "predicts": "Eloquent, fast-thinking, witty, may be cutting in speech",
        "career": "Law, journalism, debate, sales",
        "matches_chart": "Mercury in 2H/3H/own sign, Gemini/Virgo in 2H",
    },
    "Soft, gentle, slightly hesitant": {
        "predicts": "Sensitive, careful with words, may lack assertiveness, poetic",
        "career": "Counseling, arts, healing, spiritual teaching",
        "matches_chart": "Moon in 2H, Pisces/Cancer in 2H, weak Mars",
    },
    "Loud, booming, sometimes harsh": {
        "predicts": "Direct, confrontational, military/sales temperament",
        "career": "Military, sports coaching, sales, manual leadership",
        "matches_chart": "Mars in 2H/3H, Aries/Scorpio in 2H, Sun-Mars conjunction",
    },
    "Slow, deliberate, weighty": {
        "predicts": "Considered speech, philosophical, possibly delayed in expression",
        "career": "Research, judiciary, philosophy, real-estate",
        "matches_chart": "Saturn in 2H/3H, Capricorn/Aquarius in 2H",
    },
    "High-pitched, fast, animated": {
        "predicts": "Excitable, expressive, possibly nervous, gossip-prone",
        "career": "Comedy, fast-talking sales, social media",
        "matches_chart": "Mercury-Mars in 2H/3H, Gemini Lagna with afflicted Mercury",
    },
    "Hoarse, breathy, raspy": {
        "predicts": "Health issue (throat/lungs) or dramatic life-events affecting voice",
        "warning": "Watch thyroid, vocal cord strain, smoking impact",
        "matches_chart": "Saturn aspecting 2H, Rahu in 2H, malefic in 2H",
    },
    "Variable / multilingual capacity": {
        "predicts": "Polyglot, foreign-language ease, communication career",
        "career": "Translation, diplomacy, international communication",
        "matches_chart": "Mercury + Rahu in 2H/3H, Gemini emphasis, 9H foreign-link",
    },
}


# ============================================================
# WALKING GAITS — 12 classical (by Lagna element)
# ============================================================
WALKING_GAITS = {
    "Simha-gati (Lion gait)": {
        "description": "Slow, dignified, head-up, chest-out — aristocratic stride",
        "predicts": "Royal disposition, leadership, fearlessness, public presence",
        "matches_chart": "Leo Lagna or Sun strong in 1H, fire signs",
    },
    "Gaja-gati (Elephant gait)": {
        "description": "Slow, swaying, broad-based, weighty steps",
        "predicts": "Wealth-marker (most auspicious classical), patience, durability, generosity",
        "matches_chart": "Jupiter in 1H/own sign, Cancer/Pisces Lagna with strong Jupiter",
    },
    "Mriga-gati (Deer gait)": {
        "description": "Light, springy, alert, quick-stepping",
        "predicts": "Restless, alert, nervous, sensitive — often artistic",
        "matches_chart": "Moon dominant, Cancer Lagna, Mercury in 1H",
    },
    "Hamsa-gati (Swan gait)": {
        "description": "Graceful, gliding, head-still, smooth-flowing",
        "predicts": "Refined, sattvic, often spiritual, classical beauty walk",
        "matches_chart": "Venus + Moon strong, Pisces/Libra Lagna, Hamsa Mahapurusha Yoga",
    },
    "Vrisha-gati (Bull gait)": {
        "description": "Heavy, planted, slow, broad-step",
        "predicts": "Stubborn, durable, kapha-strong, manual prowess",
        "matches_chart": "Taurus Lagna, Mars in earth signs, fixed-sign emphasis",
    },
    "Ashva-gati (Horse gait)": {
        "description": "Fast, rhythmic, restless, long-stride",
        "predicts": "Travel-prone, action-oriented, possibly martial",
        "matches_chart": "Mars in 1H, Sagittarius Lagna, 9H emphasis",
    },
    "Vyaghra-gati (Tiger gait)": {
        "description": "Stealthy, controlled, predator-like",
        "predicts": "Strategic, dangerous-when-needed, military/intelligence",
        "matches_chart": "Mars + Saturn in 1H, Scorpio Lagna, malefic Lagna lord",
    },
    "Kapota-gati (Pigeon gait)": {
        "description": "Short steps, head-bobbing, hurried",
        "predicts": "Anxious, gossipy, restless, indecisive",
        "matches_chart": "Mercury afflicted, Vata excess, Gemini Lagna with weak Mercury",
    },
    "Mayura-gati (Peacock gait)": {
        "description": "Strutting, ornamental, attention-seeking",
        "predicts": "Vain, artistic, romantic, dramatic",
        "matches_chart": "Venus + Sun in 1H, Leo Lagna with strong Venus",
    },
    "Garuda-gati (Eagle gait)": {
        "description": "Confident, predatory, sweeping",
        "predicts": "Visionary, far-sighted, leadership over distance, foreign success",
        "matches_chart": "Sun + Jupiter in 9H/10H, Sagittarius Lagna",
    },
    "Sarpa-gati (Serpent gait)": {
        "description": "Sinuous, fluid, side-to-side",
        "predicts": "Mystical, occult, mesmerizing, possibly secretive",
        "matches_chart": "Rahu/Ketu in 1H, Scorpio emphasis, 8H prominent",
    },
    "Vanara-gati (Monkey gait)": {
        "description": "Bouncy, agile, playful",
        "predicts": "Restless, intelligent, multitasking, possibly mischievous",
        "matches_chart": "Mercury + Moon in 1H/3H, Mutable signs Lagna",
    },
}


# ============================================================
# BODY MARKS / SCARS / DEFECTS — 16 predictive categories
# ============================================================
BODY_MARKS = {
    "Birthmark on right side of chest": {
        "predicts": "Strong heart-line karma, romantic blessings, possibly inherited wealth",
        "house_indication": "5H + 7H positive activation",
    },
    "Birthmark on left side of chest": {
        "predicts": "Emotional sensitivity, possibly past-life heartbreak echoing",
        "house_indication": "4H + 8H emphasis",
    },
    "Birthmark on forehead (any position)": {
        "predicts": "Karmic mark — strong destiny activation, fame or scandal depending on chart",
        "house_indication": "9H/10H — dharmic destiny stamp",
    },
    "Scar from childhood accident on head/face": {
        "predicts": "Mars activation early in life, possible Sade-Sati birth-time impact",
        "house_indication": "1H + 8H — early karmic event",
    },
    "Surgical scar on abdomen": {
        "predicts": "8H activation, possible past-life karmic settlement, longevity test",
        "house_indication": "8H + 6H — health karma",
    },
    "Burn scar (any location)": {
        "predicts": "Mars-Sun episode, pitta excess in past, fire-related event in life",
        "house_indication": "Varies by body part — face=ego, hands=karma, feet=journey",
    },
    "Mole-cluster on right side of body": {
        "predicts": "Auspicious karma activation, blessings concentrated (males especially)",
        "house_indication": "1H/5H/9H positive trinity",
    },
    "Mole-cluster on left side of body": {
        "predicts": "Hidden karmic burdens, sacrifice for family/spouse (females especially)",
        "house_indication": "4H/8H/12H emphasis",
    },
    "Cleft chin / cleft lip": {
        "predicts": "Dramatic temperament, attention-seeker, charismatic OR controversial",
        "house_indication": "Saturn-Mars affliction in 1H/2H",
    },
    "Asymmetrical face (one side larger)": {
        "predicts": "Inner duality, possibly conflicted dual-nature life-path",
        "house_indication": "Lagna-7H axis afflicted, dual personality risk",
    },
    "Visible body defect from birth (limp, weak limb, etc.)": {
        "predicts": "Strong past-life karma, often results in compensatory genius elsewhere",
        "house_indication": "6H + Saturn karma; classical 'deficit-becomes-gift' pattern",
    },
    "Six fingers / extra digits (rare)": {
        "predicts": "Extra-karmic mark, often spiritual or unusual destiny — sometimes Royal sign",
        "house_indication": "Rahu in 1H, unusual placements, Ketu giving 'mark of the unusual'",
    },
    "Webbed toes (rare)": {
        "predicts": "Water-element karma, possibly martial-water past-life, swimming/sea affinity",
        "house_indication": "Pisces/Cancer Lagna, 12H emphasis",
    },
    "Mole / mark on tongue": {
        "predicts": "Power of speech — orator, writer, OR sharp-tongued famous; spiritually loaded",
        "house_indication": "Saraswati blessing — 2H + Mercury + 3H positive trinity",
    },
    "Visible birth-related mark (lotus / wheel / triangle pattern)": {
        "predicts": "Highly auspicious — divine mark (Srivatsa-class), saintly potential",
        "house_indication": "9H Jupiter blessed, Atmakaraka strong",
    },
    "Acquired tattoo / piercing in classical position": {
        "predicts": "Self-chosen karmic activation — varies by location, but indicates 'taking destiny in hand'",
        "house_indication": "Rahu-driven choice, often 1H/8H activation by free-will",
    },
}


# ============================================================
# PREDICTION FUNCTIONS
# ============================================================
def predict_hair_type(chart):
    """Predict hair type from Venus, Moon, Mars, Saturn."""
    pos = chart["positions"]
    lagna = chart["lagna"]

    venus_dignity = planet_dignity(chart, "Venus")
    moon_dignity = planet_dignity(chart, "Moon")
    saturn_dignity = planet_dignity(chart, "Saturn")
    mars_dignity = planet_dignity(chart, "Mars")
    rahu_h = planet_house(chart, "Rahu")

    if venus_dignity in ["Own", "Exalted"] and moon_dignity in ["Own", "Exalted"]:
        return "Straight, fine, glossy black"
    if mars_dignity in ["Own", "Exalted"] and lagna in ["Aries", "Scorpio"]:
        return "Tightly curly / kinky"
    if saturn_dignity == "Debil" and "Saturn" in pos and pos["Saturn"]["house"] in [1, 2]:
        return "Premature greying"
    if rahu_h in [1, 9, 12]:
        return "Light brown / golden"
    if moon_dignity in ["Own", "Exalted"] and lagna in ["Cancer", "Taurus"]:
        return "Oily, heavy, thick growth"
    if saturn_dignity in ["Debil", "neutral"] and "Saturn" in pos and pos["Saturn"]["house"] == 1:
        return "Thin, sparse, fine"
    if "Sun" in pos and pos["Sun"]["house"] in [1, 10] and lagna in ["Aries", "Leo"]:
        return "Receding hairline / early baldness (male)"
    if mars_dignity in ["Own", "Exalted"] and lagna in FIRE_SIGNS:
        return "Reddish / auburn tinge"
    if venus_dignity in ["Own", "Exalted"]:
        return "Wavy, lustrous, dark-brown"
    return "Thick, abundant, coarse black"


def predict_skin_texture(chart):
    """Predict skin texture from Venus, Moon, Saturn, Mars dignity."""
    venus_dignity = planet_dignity(chart, "Venus")
    moon_dignity = planet_dignity(chart, "Moon")
    saturn_dignity = planet_dignity(chart, "Saturn")
    sun_h = planet_house(chart, "Sun")
    mars_h = planet_house(chart, "Mars")

    if venus_dignity in ["Own", "Exalted"] and moon_dignity in ["Own", "Exalted"]:
        return "Smooth, soft, glowing (Snigdha)"
    if saturn_dignity in ["Debil", "neutral"] and "Saturn" in chart["positions"] and chart["positions"]["Saturn"]["house"] in [1, 2]:
        return "Rough, coarse (Kharara)"
    if venus_dignity in ["Own", "Exalted"]:
        return "Oily, lustrous (Snigdha-medura)"
    if sun_h in [6, 8] or mars_h in [6, 8]:
        return "Blotchy / pigmented (Vivarna)"
    if chart["lagna"] in ["Pisces", "Cancer"]:
        return "Sensitive / reactive (Sukumara)"
    if chart["lagna"] in ["Aquarius", "Capricorn"] and saturn_dignity != "Own":
        return "Dry, scaly (Ruksha)"
    return "Even-toned, clear (Sama-varna)"


def predict_body_proportions(chart):
    """Predict 5 body proportion details from Lagna sign and key planets."""
    lagna = chart["lagna"]
    pos = chart["positions"]

    # Head-to-body ratio
    if lagna in FIRE_SIGNS or lagna in FIXED_SIGNS:
        head_body = "1:6 (stocky/heavy) — strong physical presence"
    elif lagna in AIR_SIGNS:
        head_body = "1:8 (tall/slender) — intellectual"
    else:
        head_body = "1:7 (royal proportion) — balanced"

    # Arm length
    jupiter_dignity = planet_dignity(chart, "Jupiter")
    saturn_h = planet_house(chart, "Saturn")
    if jupiter_dignity in ["Own", "Exalted"] and "Jupiter" in pos and pos["Jupiter"]["house"] in [1, 11]:
        arm = "Long arms (reaching mid-thigh) — magnanimous, leadership-marker"
    elif saturn_h == 1:
        arm = "Short arms — reserved, careful"
    else:
        arm = "Medium — balanced karma"

    # Leg length
    if lagna == "Sagittarius" or planet_house(chart, "Jupiter") == 9:
        leg = "Long legs — travel-prone, restless ambition"
    elif lagna in ["Cancer", "Taurus"]:
        leg = "Short legs — rooted, family-bound"
    else:
        leg = "Medium — stable journey"

    # Torso vs leg
    if lagna in EARTH_SIGNS:
        torso = "60:40 (long torso, short legs) — wealth-storer"
    elif lagna == "Sagittarius":
        torso = "40:60 (short torso, long legs) — restless wanderer"
    else:
        torso = "50:50 (balanced)"

    # Shoulder vs hip
    mars_dignity = planet_dignity(chart, "Mars")
    venus_dignity = planet_dignity(chart, "Venus")
    if mars_dignity in ["Own", "Exalted"] and lagna in FIRE_SIGNS:
        shoulder_hip = "V-shape (wide shoulders, narrow hips) — athletic, action-oriented"
    elif venus_dignity in ["Own", "Exalted"] and lagna in WATER_SIGNS:
        shoulder_hip = "Hourglass — aesthetic, classical beauty"
    elif lagna in WATER_SIGNS:
        shoulder_hip = "Pear (narrow shoulders, wide hips) — nurturing, kapha-dominant"
    else:
        shoulder_hip = "Rectangular — practical, durable"

    return {
        "head_to_body": head_body,
        "arm_length": arm,
        "leg_length": leg,
        "torso_vs_leg": torso,
        "shoulder_vs_hip": shoulder_hip,
    }


def predict_voice_quality(chart):
    """Predict voice quality from 2H sign + 2H occupants + Mercury."""
    pos = chart["positions"]

    # 2H sign
    lagna_idx = chart["lagna_idx"]
    h2_sign = RASIS[(lagna_idx + 1) % 12]
    h2_occupants = house_occupants(chart, 2)
    h2_lord = RASI_LORDS[h2_sign]

    # Sun in 2H or 3H = commanding
    if "Sun" in h2_occupants or planet_house(chart, "Sun") == 3:
        return "Deep, resonant, commanding"
    # Venus in 2H/3H = melodious
    if "Venus" in h2_occupants or planet_house(chart, "Venus") == 3:
        return "Sweet, melodious, musical"
    # Mercury strong in 2H/3H = sharp clear
    merc_dignity = planet_dignity(chart, "Mercury")
    if "Mercury" in h2_occupants and merc_dignity in ["Own", "Exalted/Own"]:
        return "Sharp, precise, clear"
    # Moon in 2H = soft
    if "Moon" in h2_occupants:
        return "Soft, gentle, slightly hesitant"
    # Mars in 2H/3H = loud
    if "Mars" in h2_occupants or planet_house(chart, "Mars") == 3:
        return "Loud, booming, sometimes harsh"
    # Saturn in 2H/3H = slow
    if "Saturn" in h2_occupants or planet_house(chart, "Saturn") == 3:
        return "Slow, deliberate, weighty"
    # Mercury+Mars in 2H/3H = high-pitched
    if "Mercury" in h2_occupants and planet_house(chart, "Mars") in [2, 3]:
        return "High-pitched, fast, animated"
    # Saturn aspecting 2H or Rahu in 2H
    if "Rahu" in h2_occupants:
        return "Variable / multilingual capacity"
    # default by lagna element
    if chart["lagna"] in FIRE_SIGNS:
        return "Deep, resonant, commanding"
    if chart["lagna"] in WATER_SIGNS:
        return "Soft, gentle, slightly hesitant"
    if chart["lagna"] in AIR_SIGNS:
        return "Sharp, precise, clear"
    return "Sweet, melodious, musical"


def predict_walking_gait(chart):
    """Predict walking gait — 12 classical types."""
    lagna = chart["lagna"]
    pos = chart["positions"]

    jupiter_dignity = planet_dignity(chart, "Jupiter")
    venus_dignity = planet_dignity(chart, "Venus")
    mars_dignity = planet_dignity(chart, "Mars")
    sun_dignity = planet_dignity(chart, "Sun")
    rahu_h = planet_house(chart, "Rahu")
    ketu_h = planet_house(chart, "Ketu")

    # Gaja-gati — Jupiter own/exalt in 1H
    if jupiter_dignity in ["Own", "Exalted"] and "Jupiter" in pos and pos["Jupiter"]["house"] == 1:
        return "Gaja-gati (Elephant gait)"
    # Hamsa — Pisces/Libra Lagna with strong Venus
    if lagna in ["Pisces", "Libra"] and venus_dignity in ["Own", "Exalted"]:
        return "Hamsa-gati (Swan gait)"
    # Simha — Leo lagna
    if lagna == "Leo" or (sun_dignity in ["Own", "Exalted"] and planet_house(chart, "Sun") == 1):
        return "Simha-gati (Lion gait)"
    # Vyaghra — Mars+Saturn in 1H, Scorpio Lagna
    if lagna == "Scorpio" or ("Mars" in pos and pos["Mars"]["house"] == 1 and "Saturn" in pos and pos["Saturn"]["house"] == 1):
        return "Vyaghra-gati (Tiger gait)"
    # Vrisha — Taurus
    if lagna == "Taurus":
        return "Vrisha-gati (Bull gait)"
    # Ashva — Sagittarius or Mars in 1H
    if lagna == "Sagittarius" or ("Mars" in pos and pos["Mars"]["house"] == 1):
        return "Ashva-gati (Horse gait)"
    # Mriga — Cancer
    if lagna == "Cancer":
        return "Mriga-gati (Deer gait)"
    # Sarpa — Rahu/Ketu in 1H
    if rahu_h == 1 or ketu_h == 1:
        return "Sarpa-gati (Serpent gait)"
    # Mayura — Venus+Sun in 1H
    if "Venus" in pos and pos["Venus"]["house"] == 1 and "Sun" in pos and pos["Sun"]["house"] == 1:
        return "Mayura-gati (Peacock gait)"
    # Garuda — Jupiter+Sun in 9H/10H
    if planet_house(chart, "Jupiter") in [9, 10] and planet_house(chart, "Sun") in [9, 10]:
        return "Garuda-gati (Eagle gait)"
    # Vanara — mutable lagna with Mercury+Moon strong
    if lagna in DUAL_SIGNS:
        return "Vanara-gati (Monkey gait)"
    # Kapota — default for weak Mercury / anxious
    return "Kapota-gati (Pigeon gait)"


def predict_body_marks(chart):
    """Predict likely body marks, scars, defects from chart."""
    pos = chart["positions"]
    marks = []

    # Strong Mars in 1H + Sun = childhood accident scar
    if "Mars" in pos and pos["Mars"]["house"] == 1:
        marks.append("Possible scar from childhood accident on head/face")

    # Saturn aspecting 1H + 8H emphasis = surgical scar
    saturn_h = planet_house(chart, "Saturn")
    if saturn_h in [1, 8] or len(house_occupants(chart, 8)) >= 2:
        marks.append("Surgical scar on abdomen (8H activation)")

    # Venus or Sun in 1H = chest birthmark
    if "Venus" in pos and pos["Venus"]["house"] in [4, 5]:
        marks.append("Birthmark on right side of chest")
    if "Moon" in pos and pos["Moon"]["house"] in [4, 8]:
        marks.append("Birthmark on left side of chest")

    # Jupiter in 9H = forehead mark
    if planet_house(chart, "Jupiter") in [9, 10]:
        marks.append("Birthmark/auspicious mark on forehead")

    # Rahu in 1H = unusual marks/extra-karmic
    if planet_house(chart, "Rahu") == 1:
        marks.append("Acquired tattoo/piercing or unusual visible mark (Rahu signature)")

    # Mercury + 2H + Saraswati pattern = mark on tongue
    h2_occupants = house_occupants(chart, 2)
    if "Mercury" in h2_occupants and "Jupiter" in chart["positions"] and is_dignified(chart, "Jupiter"):
        marks.append("Mole / mark on tongue (Saraswati blessing)")

    # Mole cluster prediction
    lagna = chart["lagna"]
    if lagna in MOVABLE_SIGNS:
        marks.append("Mole-cluster on right side of body (auspicious activation)")
    elif lagna in FIXED_SIGNS:
        marks.append("Mole-cluster on left side of body (karmic burdens)")

    # Default
    if not marks:
        marks.append("Standard body — no major karmic marks predicted from chart")

    return marks


def full_body_appearance_prediction(chart):
    """Full 6-category body appearance prediction.

    Returns dict with: hair, skin, body_proportions, voice, walking_gait, body_marks.
    """
    return {
        "name": chart.get("name", "subject"),
        "lagna": chart.get("lagna"),
        "hair": {
            "predicted_type": predict_hair_type(chart),
            "details": HAIR_TYPES.get(predict_hair_type(chart), {}),
        },
        "skin": {
            "predicted_texture": predict_skin_texture(chart),
            "details": SKIN_TEXTURES.get(predict_skin_texture(chart), {}),
        },
        "body_proportions": predict_body_proportions(chart),
        "voice": {
            "predicted_quality": predict_voice_quality(chart),
            "details": VOICE_QUALITIES.get(predict_voice_quality(chart), {}),
        },
        "walking_gait": {
            "predicted_gait": predict_walking_gait(chart),
            "details": WALKING_GAITS.get(predict_walking_gait(chart), {}),
        },
        "body_marks": predict_body_marks(chart),
        "interpretation": (
            f"Based on chart: {predict_hair_type(chart)} hair, "
            f"{predict_skin_texture(chart)} skin, "
            f"{predict_voice_quality(chart).lower()} voice, "
            f"{predict_walking_gait(chart)}. "
            f"Body marks: {len(predict_body_marks(chart))} predicted."
        ),
        "verification_tip": (
            "Compare against actual physical observation. Hair texture, skin quality, "
            "voice resonance, walking style — strong matches confirm chart precision; "
            "major mismatches suggest birth-time rectification needed."
        ),
        "_v2_metadata": {
            "hair_types_catalogued": len(HAIR_TYPES),
            "skin_textures_catalogued": len(SKIN_TEXTURES),
            "body_proportions_catalogued": len(BODY_PROPORTIONS),
            "voice_qualities_catalogued": len(VOICE_QUALITIES),
            "walking_gaits_catalogued": len(WALKING_GAITS),
            "body_marks_catalogued": len(BODY_MARKS),
        },
    }


def lookup_v2(category, name=None):
    """Lookup in v2 categories."""
    DB = {
        "hair": HAIR_TYPES,
        "skin": SKIN_TEXTURES,
        "proportions": BODY_PROPORTIONS,
        "voice": VOICE_QUALITIES,
        "gait": WALKING_GAITS,
        "marks": BODY_MARKS,
    }
    section = DB.get(category.lower())
    if not section:
        return f"Unknown category. Available: {list(DB.keys())}"
    if name and name in section:
        return section[name]
    return section


# ============================================================
# TIER-1 DEEP EXTENSION -- Samudrika Lakshana classical coverage
# ============================================================
# Adds:
#   - SAMUDRIKA_LAKSHANAS  (32 auspicious classical bodily marks)
#   - MUKHA_LAKSHANA       (face-feature dictionary, 30+ entries across 8 categories)
#   - PLANET_BODY_PARTS    (9-planet -> body-part rulership map per BPHS Ch.4)
#   - samudrika_lakshanas(chart)
#   - face_features_from_chart(chart)
#   - body_part_health_check(chart)
# Sources: Samudrika Lakshana Shastra, Brihat Samhita Ch.70 (Varahamihira),
# Manasagari, Hastasanjivani, Brihat Parashara Hora Shastra (BPHS) Ch.4.
# ============================================================

# ---------- 32 classical lakshanas (Samudrika Shastra)
SAMUDRIKA_LAKSHANAS = [
    {"name": "Ajanu Bahu",           "location": "arms",          "meaning": "Arms reaching to the knees -- kingship, generosity, leadership across realms",                       "gender": "any",    "rarity_score": 5, "source": "Samudrika Lakshana Shastra Ch. 2",  "ruling_planet": "Jupiter"},
    {"name": "Maha Vaksha",          "location": "chest",         "meaning": "Broad, full chest -- courage, valor, abundant prana, protector type",                              "gender": "male",   "rarity_score": 4, "source": "Samudrika Lakshana Shastra Ch. 3",  "ruling_planet": "Sun"},
    {"name": "Trivali Greeva",       "location": "neck",          "meaning": "Three conch-shaped lines on the neck -- long life, dignity, royal blessings",                       "gender": "any",    "rarity_score": 4, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Jupiter"},
    {"name": "Chakra (sole-mark)",   "location": "right sole",    "meaning": "Wheel pattern on the sole -- chakravartin / world-leader marker, supreme dharmic stamp",            "gender": "any",    "rarity_score": 5, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Sun"},
    {"name": "Padma (palm-lotus)",   "location": "right palm",    "meaning": "Lotus-petal pattern on palm -- Lakshmi blessing, wealth, refined consort and offspring",            "gender": "any",    "rarity_score": 5, "source": "Hastasanjivani Ch. 4",              "ruling_planet": "Venus"},
    {"name": "Matsya (forehead)",    "location": "forehead",      "meaning": "Fish-shaped line/mark on forehead -- fortune, foreign honors, sea-trade success",                  "gender": "any",    "rarity_score": 4, "source": "Samudrika Lakshana Shastra Ch. 5",  "ruling_planet": "Moon"},
    {"name": "Chatra (umbrella)",    "location": "right palm",    "meaning": "Umbrella-shaped line on the palm -- protection from danger, leadership, royal patronage",          "gender": "any",    "rarity_score": 4, "source": "Hastasanjivani Ch. 5",              "ruling_planet": "Jupiter"},
    {"name": "Shankha (conch)",      "location": "right palm",    "meaning": "Conch pattern on palm -- eloquence, fame, victory in disputes",                                   "gender": "any",    "rarity_score": 4, "source": "Hastasanjivani Ch. 6",              "ruling_planet": "Mercury"},
    {"name": "Dhwaja (flag)",        "location": "palm/forehead", "meaning": "Flag-shaped line -- recognition, public victory, name-and-fame",                                  "gender": "any",    "rarity_score": 4, "source": "Hastasanjivani Ch. 7",              "ruling_planet": "Sun"},
    {"name": "Vajra (thunderbolt)",  "location": "right palm",    "meaning": "Vajra-shaped line -- invincible determination, warrior temperament, unbreakable will",            "gender": "male",   "rarity_score": 5, "source": "Hastasanjivani Ch. 8",              "ruling_planet": "Mars"},
    {"name": "Ankusha (goad)",       "location": "right palm",    "meaning": "Elephant-goad pattern -- control over elephants/wealth, mastery, restraint of senses",            "gender": "any",    "rarity_score": 4, "source": "Hastasanjivani Ch. 9",              "ruling_planet": "Jupiter"},
    {"name": "Yava (barley-grain)",  "location": "thumb-base",    "meaning": "Barley-grain shape on thumb -- abundance of food, blessings of Annapurna",                       "gender": "any",    "rarity_score": 3, "source": "Hastasanjivani Ch. 10",             "ruling_planet": "Moon"},
    {"name": "Mina (twin fish)",     "location": "palm/sole",     "meaning": "Twin-fish pattern -- twin blessings, dual prosperity (worldly + spiritual)",                      "gender": "any",    "rarity_score": 4, "source": "Samudrika Lakshana Shastra Ch. 6",  "ruling_planet": "Jupiter"},
    {"name": "Kalasha (pot)",        "location": "right palm",    "meaning": "Sacred-pot pattern -- Purna Kumbha, fullness of life, ritual leadership",                          "gender": "any",    "rarity_score": 4, "source": "Hastasanjivani Ch. 11",             "ruling_planet": "Jupiter"},
    {"name": "Trishula (trident)",   "location": "palm/forehead", "meaning": "Trident-mark -- Shiva-bhakta, ascetic power, victory over ego-mind-and-senses",                    "gender": "any",    "rarity_score": 4, "source": "Samudrika Lakshana Shastra Ch. 7",  "ruling_planet": "Saturn"},
    {"name": "Tilaka (third-eye)",   "location": "between brows", "meaning": "Natural mark/dot at the bindu point -- spiritual elevation, intuitive faculty",                   "gender": "any",    "rarity_score": 4, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Jupiter"},
    {"name": "Shrivatsa",            "location": "chest center",  "meaning": "Curl/whorl on the chest -- Vishnu mark, divine protection, beloved of Lakshmi",                    "gender": "any",    "rarity_score": 5, "source": "Samudrika Lakshana Shastra Ch. 8",  "ruling_planet": "Jupiter"},
    {"name": "Urna (forehead-curl)", "location": "between brows", "meaning": "Single hair-curl between brows -- sage-mark, deep wisdom, classical Buddha-lakshana",             "gender": "any",    "rarity_score": 5, "source": "Samudrika Lakshana Shastra Ch. 9",  "ruling_planet": "Jupiter"},
    {"name": "Tamra-Nakha",          "location": "fingernails",   "meaning": "Copper-tinged smooth nails -- refined nervous-system, aesthetic prosperity",                       "gender": "any",    "rarity_score": 3, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Venus"},
    {"name": "Snigdha-Tvak",         "location": "skin overall",  "meaning": "Smooth, soft, glowing skin -- sattvic constitution, beloved of fortune",                          "gender": "any",    "rarity_score": 3, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Venus"},
    {"name": "Simha-Skandha",        "location": "shoulders",     "meaning": "Lion-shoulders -- broad and slightly raised -- leadership presence, valor",                        "gender": "male",   "rarity_score": 4, "source": "Samudrika Lakshana Shastra Ch. 10", "ruling_planet": "Sun"},
    {"name": "Gaja-Gati",            "location": "walking gait",  "meaning": "Elephant-gait -- slow, dignified, swaying -- wealth & longevity (most-auspicious gait)",            "gender": "any",    "rarity_score": 5, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Jupiter"},
    {"name": "Hamsa-Gati",           "location": "walking gait",  "meaning": "Swan-gait -- graceful, gliding, head-still -- spiritual refinement, sattvic karma",                "gender": "any",    "rarity_score": 4, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Venus"},
    {"name": "Madhu-Pingal-Akshi",   "location": "eye color",     "meaning": "Honey-amber colored eyes -- divine intelligence, prophetic ability",                              "gender": "any",    "rarity_score": 5, "source": "Samudrika Lakshana Shastra Ch. 11", "ruling_planet": "Jupiter"},
    {"name": "Ghana-Bhruva",         "location": "eyebrows",      "meaning": "Dense, well-arched eyebrows that meet -- strong willpower, magnetic charisma",                    "gender": "any",    "rarity_score": 3, "source": "Manasagari Ch. 4",                  "ruling_planet": "Mars"},
    {"name": "Bhraja-Mukha",         "location": "face overall",  "meaning": "Radiant, lustrous face -- like the full moon -- divine blessing, public favor",                    "gender": "any",    "rarity_score": 4, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Moon"},
    {"name": "Sushira-Karna",        "location": "ears",          "meaning": "Long earlobes touching the shoulders -- longevity, wisdom, royal ancestry (Buddha-lakshana)",     "gender": "any",    "rarity_score": 5, "source": "Samudrika Lakshana Shastra Ch. 12", "ruling_planet": "Jupiter"},
    {"name": "Sama-Danta",           "location": "teeth",         "meaning": "Even, white, well-set teeth without gaps -- dharmic speech, abundance of food",                   "gender": "any",    "rarity_score": 3, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Venus"},
    {"name": "Madhura-Vacha",        "location": "voice",         "meaning": "Sweet, melodious voice -- Saraswati blessing, success in speech-based career",                    "gender": "any",    "rarity_score": 4, "source": "Manasagari Ch. 5",                  "ruling_planet": "Mercury"},
    {"name": "Rakta-Adhara",         "location": "lips",          "meaning": "Naturally red, full lips -- vitality, passion, affectionate nature",                              "gender": "any",    "rarity_score": 3, "source": "Brihat Samhita Ch. 70",             "ruling_planet": "Venus"},
    {"name": "Padma-Pada",           "location": "feet",          "meaning": "Lotus-shaped feet -- soft, well-formed soles -- pilgrim/yatra blessings, dharmic walk",            "gender": "any",    "rarity_score": 4, "source": "Samudrika Lakshana Shastra Ch. 13", "ruling_planet": "Venus"},
    {"name": "Romaraji",             "location": "navel-line",    "meaning": "Single fine hair-line from navel rising upward -- vital prana, courage, classical hero-mark",   "gender": "male",   "rarity_score": 4, "source": "Samudrika Lakshana Shastra Ch. 14", "ruling_planet": "Mars"},
]


# ---------- Mukha Lakshana -- face features dictionary
# Each top-level key is a feature category; sub-entries describe shape/type -> interpretation.
MUKHA_LAKSHANA = {
    "forehead_lines": [
        {"feature": "forehead", "type": "Three clear horizontal lines",                     "interpretation": "Long life, dharmic destiny, success in middle age (Trivali-rekha)",     "source": "Brihat Samhita Ch. 70"},
        {"feature": "forehead", "type": "Two horizontal lines",                             "interpretation": "Moderate life span, balanced karma, steady progress",                   "source": "Brihat Samhita Ch. 70"},
        {"feature": "forehead", "type": "Single deep horizontal line",                      "interpretation": "Concentration, scholarly mind, possible struggle in youth",             "source": "Manasagari Ch. 3"},
        {"feature": "forehead", "type": "Vertical lines (between brows)",                   "interpretation": "Worry, intense focus, possible Saturn-pressure in adolescence",         "source": "Manasagari Ch. 3"},
        {"feature": "forehead", "type": "M-shaped pattern (3 lines branching)",             "interpretation": "Royal mark -- recognition, leadership, classical raja-rekha",            "source": "Hastasanjivani Ch. 14"},
    ],
    "eyebrows": [
        {"feature": "eyebrows", "type": "Thick and well-arched (Ghana-Bhruva)",             "interpretation": "Strong willpower, leadership, masculine energy",                       "source": "Manasagari Ch. 4"},
        {"feature": "eyebrows", "type": "Thin and curved (Sukshma-Bhruva)",                 "interpretation": "Refined sensibility, artistic mind, possibly nervous temperament",      "source": "Manasagari Ch. 4"},
        {"feature": "eyebrows", "type": "Bushy and meeting in the middle (Sangama)",        "interpretation": "Magnetic charisma, but possible jealousy or possessive nature",         "source": "Brihat Samhita Ch. 70"},
        {"feature": "eyebrows", "type": "Sparse, broken pattern",                           "interpretation": "Weak vitality in youth, indecision, may strengthen with age",            "source": "Brihat Samhita Ch. 70"},
        {"feature": "eyebrows", "type": "Highly arched (peaked center)",                    "interpretation": "Dramatic temperament, surprises in life, performer/artist potential",    "source": "Samudrika Lakshana Shastra Ch. 11"},
    ],
    "eyes": [
        {"feature": "eyes", "type": "Dark-brown almond eyes",                                "interpretation": "Sattvic intelligence, calm temperament, classical refined beauty",       "source": "Brihat Samhita Ch. 70"},
        {"feature": "eyes", "type": "Honey-amber large eyes (Madhu-Pingal)",                 "interpretation": "Divine intelligence, prophetic ability, magnetic gaze",                "source": "Samudrika Lakshana Shastra Ch. 11"},
        {"feature": "eyes", "type": "Sharp, small, piercing eyes",                           "interpretation": "Strategic mind, suspicious by nature, capable observer",                "source": "Manasagari Ch. 5"},
        {"feature": "eyes", "type": "Reddish-tinged or fiery eyes",                          "interpretation": "Pitta-excess, passionate, intense temperament, Mars-marker",            "source": "Brihat Samhita Ch. 70"},
        {"feature": "eyes", "type": "Bluish-grey eyes (rare in Indian birth)",               "interpretation": "Foreign-blood karma, cold intellect, detached observer",                "source": "Samudrika Lakshana Shastra Ch. 11"},
        {"feature": "eyes", "type": "Watery, soft, expressive eyes",                         "interpretation": "Emotionally sensitive, artistic, kapha+vata constitution",              "source": "Manasagari Ch. 5"},
    ],
    "nose": [
        {"feature": "nose", "type": "Straight, well-proportioned (Sama-Nasa)",               "interpretation": "Dharmic life, balanced karma, refined taste",                          "source": "Brihat Samhita Ch. 70"},
        {"feature": "nose", "type": "Aquiline / slightly hooked (Eagle-nose)",               "interpretation": "Strategic, ambitious, leadership-prone, royal mark in classical texts",  "source": "Samudrika Lakshana Shastra Ch. 12"},
        {"feature": "nose", "type": "Small, snub nose",                                       "interpretation": "Childlike charm but volatile temperament, may struggle for recognition", "source": "Manasagari Ch. 5"},
        {"feature": "nose", "type": "Wide-tipped, fleshy nose",                               "interpretation": "Earthy, sensual, comfort-loving, kapha-dominant",                       "source": "Brihat Samhita Ch. 70"},
        {"feature": "nose", "type": "Long, thin nose (sage-nose)",                            "interpretation": "Inquisitive intellect, scholarly, may have sinus weakness",            "source": "Manasagari Ch. 5"},
    ],
    "lips": [
        {"feature": "lips", "type": "Full, well-formed, slightly red (Rakta-Adhara)",        "interpretation": "Vitality, affection, beloved of family, refined speech",               "source": "Brihat Samhita Ch. 70"},
        {"feature": "lips", "type": "Thin, tight lips",                                       "interpretation": "Discipline, secrecy, guarded affection, watch for harshness in speech",  "source": "Manasagari Ch. 6"},
        {"feature": "lips", "type": "Pale or bluish lips",                                    "interpretation": "Weak vitality, possible heart/circulation issue, vata-excess",          "source": "Samudrika Lakshana Shastra Ch. 13"},
        {"feature": "lips", "type": "Asymmetrical lips (one side fuller)",                    "interpretation": "Inner duality, possibly conflicted speech-vs-thought",                 "source": "Manasagari Ch. 6"},
    ],
    "ears": [
        {"feature": "ears", "type": "Long earlobes touching shoulders (Sushira-Karna)",      "interpretation": "Longevity, wisdom, royal ancestry, classical Buddha-lakshana",          "source": "Samudrika Lakshana Shastra Ch. 12"},
        {"feature": "ears", "type": "Medium-sized symmetric ears",                            "interpretation": "Balanced karma, good listener, dharmic life",                          "source": "Brihat Samhita Ch. 70"},
        {"feature": "ears", "type": "Small, close-set ears",                                  "interpretation": "Reserved listener, possible difficulty in receiving advice",            "source": "Manasagari Ch. 7"},
        {"feature": "ears", "type": "Pointed or elf-shaped ears",                             "interpretation": "Sharp intuition, occasionally restless, possibly artistic-mystical",    "source": "Samudrika Lakshana Shastra Ch. 12"},
    ],
    "chin": [
        {"feature": "chin", "type": "Round, soft chin",                                       "interpretation": "Affectionate, family-oriented, classical kapha grace",                  "source": "Brihat Samhita Ch. 70"},
        {"feature": "chin", "type": "Square, prominent chin",                                 "interpretation": "Determined, leadership, possibly stubborn",                            "source": "Manasagari Ch. 7"},
        {"feature": "chin", "type": "Pointed, narrow chin",                                   "interpretation": "Intellectual, refined, possibly delicate constitution",                "source": "Samudrika Lakshana Shastra Ch. 13"},
        {"feature": "chin", "type": "Cleft / dimpled chin",                                   "interpretation": "Charismatic, attention-attracting, dramatic temperament",              "source": "Brihat Samhita Ch. 70"},
    ],
    "teeth": [
        {"feature": "teeth", "type": "Even, white, well-set (Sama-Danta)",                    "interpretation": "Dharmic speech, abundance of food, social grace",                      "source": "Brihat Samhita Ch. 70"},
        {"feature": "teeth", "type": "Gapped teeth (especially front)",                       "interpretation": "Speech-power, public-facing career, but possible indiscretion",         "source": "Samudrika Lakshana Shastra Ch. 14"},
        {"feature": "teeth", "type": "Crooked or overlapping teeth",                          "interpretation": "Karmic speech-burden, possibly sharp-tongued, watch for misunderstanding", "source": "Manasagari Ch. 8"},
    ],
}


# ---------- Planet -> body parts (BPHS Ch. 4)
PLANET_BODY_PARTS = {
    "Sun":     {"parts": ["heart", "eyes (especially right)", "right side of body", "head", "bones (general vitality)"],          "diseases": ["heart issues", "weak vision", "fevers", "headaches"],                "source": "BPHS Ch. 4 (Surya-prakaranam)"},
    "Moon":    {"parts": ["face", "chest", "blood (plasma/rasa)", "lungs", "left eye", "stomach lining"],                          "diseases": ["mental imbalance", "anaemia", "lung issues", "menstrual irregularity"], "source": "BPHS Ch. 4 (Chandra-prakaranam)"},
    "Mars":    {"parts": ["blood (raktha)", "marrow", "forehead", "genitals (male)", "muscles"],                                   "diseases": ["accidents", "blood disorders", "fevers", "cuts/burns", "hypertension"], "source": "BPHS Ch. 4 (Mangala-prakaranam)"},
    "Mercury": {"parts": ["skin", "nervous system", "tongue", "lungs (alveoli)", "intellect / memory"],                            "diseases": ["skin allergies", "nervous disorders", "speech issues", "respiratory"], "source": "BPHS Ch. 4 (Budha-prakaranam)"},
    "Jupiter": {"parts": ["liver", "thighs", "fat tissue (medas)", "ears", "hips"],                                                "diseases": ["liver disorders", "diabetes (medas-imbalance)", "ear issues", "obesity"],"source": "BPHS Ch. 4 (Guru-prakaranam)"},
    "Venus":   {"parts": ["reproductive organs", "cheeks", "throat", "kidneys", "semen / shukra dhatu"],                            "diseases": ["reproductive issues", "throat infections", "kidney problems", "diabetes (sweet-imbalance)"], "source": "BPHS Ch. 4 (Shukra-prakaranam)"},
    "Saturn":  {"parts": ["teeth", "bones", "legs", "joints", "hair (greying)", "skin (drying)"],                                  "diseases": ["arthritis", "bone fractures", "chronic fatigue", "depression", "deafness in age"], "source": "BPHS Ch. 4 (Shani-prakaranam)"},
    "Rahu":    {"parts": ["feet", "intestines", "lower abdomen", "skin (especially mysterious patches)", "lymphatic"],             "diseases": ["poisoning / toxicity", "digestive disorders", "skin patches", "phobias"], "source": "BPHS Ch. 4 (Rahu-prakaranam)"},
    "Ketu":    {"parts": ["spine", "abdomen", "spiritual nerves (sushumna)", "extremities (hands/feet tips)", "subtle body"],      "diseases": ["spinal issues", "infections of unknown origin", "psychic disturbances", "wasting"], "source": "BPHS Ch. 4 (Ketu-prakaranam)"},
}


# ============================================================
# DEEP-EXTENSION FUNCTIONS
# ============================================================

def _planet_strong(chart, planet):
    """Planet 'producing' the lakshana is well-placed: own/exalted/swakshetra in kendra/trikona AND not severely afflicted."""
    pos = chart.get("positions", {})
    if planet not in pos:
        return False
    dignity = planet_dignity(chart, planet)
    house = planet_house(chart, planet)
    well_dignified = dignity in ["Own", "Exalted", "Exalted/Own"]
    in_good_house = house in [1, 4, 5, 7, 9, 10]
    in_dusthana = house in [6, 8, 12]
    if dignity == "Debil":
        return False
    if in_dusthana:
        return False
    return well_dignified or in_good_house


def _planet_afflicted(chart, planet):
    """Planet is afflicted enough to indicate the lakshana is absent."""
    pos = chart.get("positions", {})
    if planet not in pos:
        return False
    dignity = planet_dignity(chart, planet)
    house = planet_house(chart, planet)
    if dignity == "Debil":
        return True
    if house in [6, 8, 12]:
        return True
    for malefic in ["Saturn", "Mars", "Rahu", "Ketu"]:
        if malefic == planet:
            continue
        try:
            if planets_conjunct(chart, planet, malefic) and planet_house(chart, malefic) in [6, 8, 12]:
                return True
        except Exception:
            pass
    return False


def samudrika_lakshanas(chart):
    """For each of 32 classical lakshanas, infer likely presence/absence from natal positions.

    Returns dict with likely_present/likely_absent/ambiguous keyed lists, plus
    a lagna_specific_features summary string.
    """
    likely_present = []
    likely_absent = []
    ambiguous = []

    for lak in SAMUDRIKA_LAKSHANAS:
        ruler = lak.get("ruling_planet")
        score = 3
        verdict = "ambiguous"
        if ruler:
            if _planet_strong(chart, ruler):
                dignity = planet_dignity(chart, ruler)
                house = planet_house(chart, ruler)
                if dignity in ["Own", "Exalted", "Exalted/Own"] and house in [1, 4, 5, 7, 9, 10]:
                    score = 5
                else:
                    score = 4
                verdict = "likely_present"
            elif _planet_afflicted(chart, ruler):
                dignity = planet_dignity(chart, ruler)
                house = planet_house(chart, ruler)
                if dignity == "Debil" and house in [6, 8, 12]:
                    score = 1
                else:
                    score = 2
                verdict = "likely_absent"

        record = {
            "name": lak["name"],
            "location": lak["location"],
            "meaning": lak["meaning"],
            "gender": lak["gender"],
            "rarity_score": lak["rarity_score"],
            "source": lak["source"],
            "ruling_planet": ruler,
            "score": score,
            "verdict": verdict,
        }
        if verdict == "likely_present":
            likely_present.append(record)
        elif verdict == "likely_absent":
            likely_absent.append(record)
        else:
            ambiguous.append(record)

    lagna = chart.get("lagna", "")
    lagna_lord = RASI_LORDS.get(lagna, "")
    lagna_lord_dignity = planet_dignity(chart, lagna_lord) if lagna_lord else "-"
    lagna_lord_house = planet_house(chart, lagna_lord) if lagna_lord else 0

    if lagna in FIRE_SIGNS:
        lagna_summary = f"{lagna} Lagna: ruddy/fiery complexion, athletic build, prominent forehead, Mars-stamped vitality"
    elif lagna in EARTH_SIGNS:
        lagna_summary = f"{lagna} Lagna: stocky frame, full features, kapha-stable, ear/voice-marked"
    elif lagna in AIR_SIGNS:
        lagna_summary = f"{lagna} Lagna: tall/slender, refined features, intellectual face, Mercury/Venus-stamped"
    else:
        lagna_summary = f"{lagna} Lagna: soft features, watery eyes, Moon/Venus-graced face, sensitive build"

    body_strength = (
        "strong" if _planet_strong(chart, lagna_lord)
        else "compromised" if _planet_afflicted(chart, lagna_lord)
        else "moderate"
    )
    lagna_specific_features = (
        f"{lagna_summary}. Lagna-lord ({lagna_lord}) is {lagna_lord_dignity} "
        f"in house {lagna_lord_house} -- body-strength {body_strength}."
    )

    return {
        "total_lakshanas": len(SAMUDRIKA_LAKSHANAS),
        "likely_present": likely_present,
        "likely_absent": likely_absent,
        "ambiguous": ambiguous,
        "counts": {
            "present": len(likely_present),
            "absent": len(likely_absent),
            "ambiguous": len(ambiguous),
        },
        "lagna_specific_features": lagna_specific_features,
        "interpretation": (
            f"Of 32 classical Samudrika lakshanas, {len(likely_present)} are likely present, "
            f"{len(likely_absent)} likely absent, {len(ambiguous)} ambiguous. "
            "Verify physically; strong-match lakshanas confirm chart precision."
        ),
        "source": "Samudrika Lakshana Shastra + Brihat Samhita Ch. 70 + Hastasanjivani",
    }


def face_features_from_chart(chart):
    """Predict the 8 face features (forehead, eyebrows, eyes, nose, lips, ears, chin, teeth)
    from lagna lord + Moon sign + Sun sign + ascendant degree.
    """
    lagna = chart.get("lagna", "")
    lagna_lord = RASI_LORDS.get(lagna, "")
    pos = chart.get("positions", {})
    moon_sign = pos.get("Moon", {}).get("rasi", "")
    sun_sign = pos.get("Sun", {}).get("rasi", "")
    asc_deg = 0.0
    try:
        asc_deg = float(chart.get("lagna_deg", 0.0))
    except Exception:
        asc_deg = 0.0

    venus_dignity = planet_dignity(chart, "Venus")
    mars_dignity = planet_dignity(chart, "Mars")
    saturn_h = planet_house(chart, "Saturn")
    jupiter_h = planet_house(chart, "Jupiter")
    mercury_dignity = planet_dignity(chart, "Mercury")

    # Forehead lines
    if _planet_strong(chart, lagna_lord) and _planet_strong(chart, "Jupiter"):
        forehead = MUKHA_LAKSHANA["forehead_lines"][0]
    elif _planet_strong(chart, "Jupiter"):
        forehead = MUKHA_LAKSHANA["forehead_lines"][1]
    elif saturn_h in [1, 2]:
        forehead = MUKHA_LAKSHANA["forehead_lines"][3]
    elif jupiter_h in [9, 10] and _planet_strong(chart, "Sun"):
        forehead = MUKHA_LAKSHANA["forehead_lines"][4]
    else:
        forehead = MUKHA_LAKSHANA["forehead_lines"][2]

    # Eyebrows
    if mars_dignity in ["Own", "Exalted"]:
        eyebrows = MUKHA_LAKSHANA["eyebrows"][0]
    elif lagna in ["Pisces", "Cancer"] and venus_dignity in ["Own", "Exalted"]:
        eyebrows = MUKHA_LAKSHANA["eyebrows"][1]
    elif planet_house(chart, "Rahu") == 1 or planet_house(chart, "Ketu") == 1:
        eyebrows = MUKHA_LAKSHANA["eyebrows"][2]
    elif _planet_afflicted(chart, "Mars"):
        eyebrows = MUKHA_LAKSHANA["eyebrows"][3]
    else:
        eyebrows = MUKHA_LAKSHANA["eyebrows"][4]

    # Eyes
    if _planet_strong(chart, "Jupiter") and moon_sign in ["Cancer", "Pisces"]:
        eyes = MUKHA_LAKSHANA["eyes"][1]
    elif venus_dignity in ["Own", "Exalted"] and moon_sign in ["Taurus", "Libra"]:
        eyes = MUKHA_LAKSHANA["eyes"][0]
    elif mars_dignity in ["Own", "Exalted"] and (sun_sign in FIRE_SIGNS):
        eyes = MUKHA_LAKSHANA["eyes"][3]
    elif planet_house(chart, "Rahu") == 1 and lagna in AIR_SIGNS:
        eyes = MUKHA_LAKSHANA["eyes"][4]
    elif moon_sign in WATER_SIGNS and _planet_strong(chart, "Moon"):
        eyes = MUKHA_LAKSHANA["eyes"][5]
    else:
        eyes = MUKHA_LAKSHANA["eyes"][2]

    # Nose
    if lagna_lord == "Mars" or (sun_sign in ["Aries", "Leo"] and _planet_strong(chart, "Sun")):
        nose = MUKHA_LAKSHANA["nose"][1]
    elif mercury_dignity in ["Own", "Exalted/Own"]:
        nose = MUKHA_LAKSHANA["nose"][4]
    elif lagna in EARTH_SIGNS:
        nose = MUKHA_LAKSHANA["nose"][3]
    elif lagna == "Cancer":
        nose = MUKHA_LAKSHANA["nose"][2]
    else:
        nose = MUKHA_LAKSHANA["nose"][0]

    # Lips
    if venus_dignity in ["Own", "Exalted"]:
        lips = MUKHA_LAKSHANA["lips"][0]
    elif saturn_h in [1, 2]:
        lips = MUKHA_LAKSHANA["lips"][1]
    elif _planet_afflicted(chart, "Moon"):
        lips = MUKHA_LAKSHANA["lips"][2]
    else:
        lips = MUKHA_LAKSHANA["lips"][3]

    # Ears
    if _planet_strong(chart, "Jupiter") and jupiter_h in [1, 4, 9, 10]:
        ears = MUKHA_LAKSHANA["ears"][0]
    elif mercury_dignity in ["Own", "Exalted"]:
        ears = MUKHA_LAKSHANA["ears"][1]
    elif planet_house(chart, "Ketu") == 1:
        ears = MUKHA_LAKSHANA["ears"][3]
    else:
        ears = MUKHA_LAKSHANA["ears"][2]

    # Chin
    if lagna in EARTH_SIGNS and venus_dignity in ["Own", "Exalted"]:
        chin = MUKHA_LAKSHANA["chin"][0]
    elif mars_dignity in ["Own", "Exalted"] or lagna == "Capricorn":
        chin = MUKHA_LAKSHANA["chin"][1]
    elif lagna in AIR_SIGNS:
        chin = MUKHA_LAKSHANA["chin"][2]
    else:
        chin = MUKHA_LAKSHANA["chin"][3]

    # Teeth
    if venus_dignity in ["Own", "Exalted"] and _planet_strong(chart, "Mercury"):
        teeth = MUKHA_LAKSHANA["teeth"][0]
    elif "Mercury" in pos and pos["Mercury"]["house"] in [2, 3]:
        teeth = MUKHA_LAKSHANA["teeth"][1]
    else:
        teeth = MUKHA_LAKSHANA["teeth"][2]

    return {
        "lagna": lagna,
        "lagna_lord": lagna_lord,
        "moon_sign": moon_sign,
        "sun_sign": sun_sign,
        "ascendant_degree": asc_deg,
        "forehead_lines": forehead,
        "eyebrows": eyebrows,
        "eyes": eyes,
        "nose": nose,
        "lips": lips,
        "ears": ears,
        "chin": chin,
        "teeth": teeth,
        "interpretation": (
            f"Face profile derived from {lagna} Lagna (lord {lagna_lord}), "
            f"Moon in {moon_sign}, Sun in {sun_sign}. "
            f"Key features: {eyes['type']} eyes, {nose['type']} nose, {lips['type']} lips."
        ),
        "source": "Brihat Samhita Ch. 70 + Manasagari + Hastasanjivani (cross-referenced)",
    }


def body_part_health_check(chart):
    """For each of 9 planets, examine affliction and report which body parts are predisposed to weakness.

    Returns list of records sorted by descending affliction_score.
    """
    results = []
    pos = chart.get("positions", {})
    natural_malefics = ["Saturn", "Mars", "Rahu", "Ketu"]

    for planet, parts_info in PLANET_BODY_PARTS.items():
        if planet not in pos:
            continue
        score = 0
        flags = []

        dignity = planet_dignity(chart, planet)
        house = planet_house(chart, planet)
        retro = pos[planet].get("retrograde") or pos[planet].get("retro") or False

        if dignity == "Debil":
            score += 3
            flags.append("debilitated")
        elif dignity == "Enemy":
            score += 1
            flags.append("in enemy sign")

        if house in [6, 8, 12]:
            score += 2
            flags.append(f"in dusthana {house}H")

        if retro:
            score += 1
            flags.append("retrograde")

        for malefic in natural_malefics:
            if malefic == planet or malefic not in pos:
                continue
            try:
                if planets_conjunct(chart, planet, malefic):
                    score += 1
                    flags.append(f"conjunct {malefic}")
                    break
            except Exception:
                pass

        try:
            for malefic in ["Saturn", "Mars"]:
                if malefic == planet or malefic not in pos:
                    continue
                houses_aspected = planet_aspects_houses(chart, malefic)
                if house in houses_aspected:
                    score += 1
                    flags.append(f"aspected by {malefic}")
                    break
        except Exception:
            pass

        if score == 0:
            recommendation = "No significant affliction; body parts under this planet's domain are well-supported."
            severity = "healthy"
        elif score <= 2:
            recommendation = f"Mild care for {', '.join(parts_info['parts'][:2])}. Lifestyle vigilance, no urgency."
            severity = "mild"
        elif score <= 4:
            recommendation = f"Moderate predisposition. Watch {', '.join(parts_info['parts'][:3])}. Periodic check-ups recommended."
            severity = "moderate"
        else:
            recommendation = f"Significant karmic affliction. Strong predisposition to {', '.join(parts_info['diseases'])}. Preventive care + remedial measures advised."
            severity = "high"

        results.append({
            "planet": planet,
            "body_parts": parts_info["parts"],
            "predisposed_diseases": parts_info["diseases"],
            "affliction_score": score,
            "severity": severity,
            "flags": flags,
            "house": house,
            "dignity": dignity,
            "recommendation": recommendation,
            "source": parts_info["source"],
        })

    results.sort(key=lambda r: r["affliction_score"], reverse=True)
    return results


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    result = full_body_appearance_prediction(chart)
    print(f"=== FACE READING v2 -- Full Body Appearance ({chart['name']}) ===\n")
    print(f"  Hair:        {result['hair']['predicted_type']}")
    print(f"  Skin:        {result['skin']['predicted_texture']}")
    print(f"  Voice:       {result['voice']['predicted_quality']}")
    print(f"  Gait:        {result['walking_gait']['predicted_gait']}")
    print(f"\n  Body proportions:")
    for k, v in result["body_proportions"].items():
        print(f"    * {k}: {v}")
    print(f"\n  Body marks predicted ({len(result['body_marks'])}):")
    for m in result["body_marks"]:
        print(f"    * {m}")
    print(f"\n  Catalog stats:")
    for k, v in result["_v2_metadata"].items():
        print(f"    {k}: {v}")
    print(f"\n  INTERPRETATION:\n  {result['interpretation']}")

    # ---- TIER-1 deep extension demo
    print("\n\n=== TIER-1 DEEP -- Samudrika Lakshanas ===")
    sl = samudrika_lakshanas(chart)
    print(f"  Total catalogued: {sl['total_lakshanas']}")
    print(f"  Likely present : {sl['counts']['present']}")
    print(f"  Likely absent  : {sl['counts']['absent']}")
    print(f"  Ambiguous      : {sl['counts']['ambiguous']}")
    print(f"  Lagna-specific : {sl['lagna_specific_features']}")
    print(f"  Top-5 likely-present examples:")
    for lak in sl["likely_present"][:5]:
        print(f"    * {lak['name']} ({lak['location']}) -- score {lak['score']} -- {lak['meaning'][:60]}...")

    print("\n=== TIER-1 DEEP -- Face Features from Chart ===")
    ff = face_features_from_chart(chart)
    for key in ["forehead_lines", "eyebrows", "eyes", "nose", "lips", "ears", "chin", "teeth"]:
        entry = ff[key]
        print(f"  {key:>16}: {entry['type']}")

    print("\n=== TIER-1 DEEP -- Body-Part Health Check ===")
    bh = body_part_health_check(chart)
    print(f"  9 planets analysed. Top-3 weakness areas:")
    for rec in bh[:3]:
        print(f"    * {rec['planet']:>8} (score {rec['affliction_score']}, {rec['severity']}): {', '.join(rec['body_parts'][:3])}")
        print(f"           flags: {', '.join(rec['flags']) if rec['flags'] else 'none'}")
        print(f"           recommendation: {rec['recommendation']}")

    print("\n=== Tier-1 deep extension complete -- 0 exceptions ===")
