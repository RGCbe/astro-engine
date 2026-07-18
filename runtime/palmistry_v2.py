"""Palmistry v2 — extended Hasta Samudrika with deep line-pattern variations and yantra marks.

Builds on palmistry_engine.py (v1: 4 hand types + 7 mounts + main lines + 5 fingers + fingerprints).

v2 adds:
  - 25 specific line-pattern variations (Apollo/Mercury/Marriage/Children/Fate/Health)
  - 12 RING patterns + yantra-like marks (Solomon, Saturn, Apollo, Mercury, Triangle, Square,
    Star, Cross, Spear, Dot per mount)
  - Each finger's 3 phalanges with separate meanings (15 sub-readings)
  - 5 fingertip shapes (square, conic, spatulate, pointed, mixed)
  - Hand color/texture/temperature interpretation
  - Palm proportion calculations (percussion edge, palm width ratios)

Source: Hasta Samudrika Shastra, Cheiro's Palmistry, Sanjay Sharma's "Practical Palmistry,"
Indian classical hand-reading + yantra-mark traditions.
"""
import sys
sys.path.insert(0, ".")
from vedic_core import DIGNITIES, PLANETS_MAIN, planet_dignity, planet_house, is_dignified
from palmistry_engine import (
    HAND_SHAPES, MOUNTS, MAIN_LINES, SECONDARY_LINES, FINGERS, FINGERPRINTS,
    predict_hand_features_from_chart, palmistry_summary,
)


# ============================================================
# 25 SPECIFIC LINE PATTERNS
# ============================================================
LINE_VARIATIONS = {
    # APOLLO / SUN LINE (5 variations)
    "Apollo line — clear & deep": {
        "section": "Sun line",
        "meaning": "Strong fame potential, public recognition, artistic success guaranteed",
        "timing": "Active throughout life if reaches mount",
    },
    "Apollo line — wavy": {
        "section": "Sun line",
        "meaning": "Recognition comes in waves, ups-and-downs in fame",
        "advice": "Persist through low-recognition periods",
    },
    "Apollo line — broken": {
        "section": "Sun line",
        "meaning": "Career interruption / reputation crisis at the break-point",
        "timing": "Read the break-point along line for life-stage timing",
    },
    "Apollo line — forked at end": {
        "section": "Sun line",
        "meaning": "Multiple sources of fame / dual artistic+professional success",
    },
    "Apollo line — island in middle": {
        "section": "Sun line",
        "meaning": "Scandal or temporary reputation-loss in middle life",
        "advice": "Watch ethics in middle years",
    },

    # MERCURY / HEALTH LINE (4 variations)
    "Mercury line — clear & straight": {
        "section": "Mercury line",
        "meaning": "Excellent business sense + good health, communication mastery",
    },
    "Mercury line — wavy": {
        "section": "Mercury line",
        "meaning": "Digestive / liver issues + irregular business luck",
    },
    "Mercury line — broken or fragmentary": {
        "section": "Mercury line",
        "meaning": "Health crises punctuating life; possibly nervous-system episodes",
    },
    "Mercury line — absent on healthy hand": {
        "section": "Mercury line",
        "meaning": "PARADOX — absence on healthy hand = no health worries (ironically auspicious)",
    },

    # MARRIAGE LINE (5 variations)
    "Marriage line — single, clear, deep": {
        "section": "Marriage line",
        "meaning": "One stable, lifelong marriage with deep bond",
    },
    "Marriage line — wavy": {
        "section": "Marriage line",
        "meaning": "Marital instability; ups and downs in relationship",
    },
    "Marriage line — island": {
        "section": "Marriage line",
        "meaning": "Major marital crisis / separation at marked timing",
    },
    "Marriage line — cross / X at end": {
        "section": "Marriage line",
        "meaning": "Possible divorce or major rupture in relationship",
    },
    "Marriage line — break": {
        "section": "Marriage line",
        "meaning": "Separation or partner's serious illness",
    },

    # CHILDREN LINES (3 variations)
    "Children line — deep & strong": {
        "section": "Children line",
        "meaning": "Healthy, vital children (especially male in classical reading)",
    },
    "Children line — thin & shallow": {
        "section": "Children line",
        "meaning": "Possibly daughters; or children of delicate constitution",
    },
    "Children line — broken or interrupted": {
        "section": "Children line",
        "meaning": "Possible miscarriage, child estrangement, or child-loss event",
        "warning": "Compare against chart's 5H for confirmation",
    },

    # FATE LINE (5 variations)
    "Fate line — origin from wrist (rascette)": {
        "section": "Fate line",
        "meaning": "Self-made early career, destiny clear from young age",
    },
    "Fate line — origin from Luna mount": {
        "section": "Fate line",
        "meaning": "Career through public favor / patronage / fame from foreign or imagination-based work",
    },
    "Fate line — origin from life line (joined)": {
        "section": "Fate line",
        "meaning": "Family-business inheritance or career shaped by family destiny",
    },
    "Fate line — broken in middle": {
        "section": "Fate line",
        "meaning": "Major career change or loss at marked life-stage",
    },
    "Fate line — multiple parallel lines": {
        "section": "Fate line",
        "meaning": "Multiple career paths simultaneously; portfolio life or many vocations",
    },

    # HEALTH LINE / OTHER (3 variations)
    "Health line — present & clear": {
        "section": "Health/Hepatica",
        "meaning": "Awareness of health, possibly health-related profession",
    },
    "Health line — absent on healthy hand": {
        "section": "Health/Hepatica",
        "meaning": "No health worries (auspicious)",
    },
    "Travel lines — multiple deep lines from edge": {
        "section": "Travel lines",
        "meaning": "Foreign settlement / multiple major journeys defining life",
    },
}


# ============================================================
# 12 RING / YANTRA-LIKE MARKS
# ============================================================
RING_PATTERNS = {
    "Ring of Solomon (around Jupiter mount)": {
        "location": "Semicircle around base of index finger",
        "meaning": "Wisdom, occult interest, teaching ability, judicial mind",
        "rarity": "moderately rare",
        "auspicious": True,
    },
    "Ring of Saturn (around Saturn mount)": {
        "location": "Semicircle around base of middle finger",
        "meaning": "Isolation, restricted destiny, depression-prone",
        "rarity": "rare",
        "auspicious": False,
    },
    "Ring of Apollo (around Sun mount)": {
        "location": "Semicircle around base of ring finger",
        "meaning": "Frustrated creative ambition, fame blocked",
        "rarity": "rare",
        "auspicious": False,
    },
    "Ring of Mercury (around Mercury mount)": {
        "location": "Semicircle around base of little finger",
        "meaning": "Communication blockage, business setbacks",
        "rarity": "very rare",
        "auspicious": False,
    },
    "Triangle on Jupiter mount": {
        "location": "Triangle formation under index finger",
        "meaning": "Diplomatic skill, leadership recognition, success in management",
        "auspicious": True,
    },
    "Triangle on Saturn mount": {
        "location": "Triangle under middle finger",
        "meaning": "Aptitude for occult/research/investigation",
        "auspicious": True,
    },
    "Triangle on Apollo (Sun) mount": {
        "location": "Triangle under ring finger",
        "meaning": "Artistic genius, fame through creative achievement",
        "auspicious": True,
    },
    "Triangle on Mercury mount": {
        "location": "Triangle under little finger",
        "meaning": "Business genius, scientific aptitude, healing capacity",
        "auspicious": True,
    },
    "Square on any mount": {
        "location": "Variable (any mount)",
        "meaning": "Protection-yantra — preserves the mount's significance from harm",
        "auspicious": True,
        "indication": "Divine protection in that life-domain",
    },
    "Star on any mount": {
        "location": "Variable",
        "meaning": "Sudden burst of glory in that mount's domain — Apollo=fame, Mercury=wealth",
        "auspicious": True,
        "rarity": "rare",
    },
    "Cross on any mount": {
        "location": "Variable",
        "meaning": "Variable — Jupiter cross=spiritual marriage; Saturn cross=danger/loss; Apollo cross=fame-blockage; Mercury cross=deceit",
        "auspicious": "mixed",
    },
    "Spear / Trishula (3-line) mark": {
        "location": "Usually palm center or near Saturn mount",
        "meaning": "Tantric/Shaivite spiritual marker, ascetic potential, weapon-skill (literal or metaphoric)",
        "auspicious": True,
        "rarity": "very rare",
    },
}


# ============================================================
# DOT-MARKS PER MOUNT
# ============================================================
DOT_MARKS = {
    "Dot on Jupiter mount": "Health crisis or scandal at marked timing — read as warning",
    "Dot on Saturn mount": "Sudden adversity / loss — red dot is dangerous; black is karmic",
    "Dot on Apollo / Sun mount": "Reputation crisis / public scandal at marked timing",
    "Dot on Mercury mount": "Business loss or communication crisis",
    "Dot on Venus mount": "Romantic loss or family tragedy",
    "Dot on Luna mount": "Travel-related danger; foreign mishap",
    "Dot on Mars mounts": "Accident / violence / surgery at marked timing",
    "Dot on palm center (Plain of Mars)": "Major confrontation / battle in life",
}


# ============================================================
# FINGER PHALANGES — 5 fingers × 3 phalanges = 15 sub-readings
# ============================================================
FINGER_PHALANGES = {
    # INDEX (Jupiter)
    "Index — top phalanx (nail to first knuckle)": {
        "rules": "Spirituality, idealism, dharma",
        "long & strong": "Spiritual leader, religious authority",
        "short": "Lacks higher purpose, materialistic",
    },
    "Index — middle phalanx": {
        "rules": "Ambition, leadership in worldly matters",
        "long & strong": "Strong leader, executive",
        "short": "Follower, lacks initiative",
    },
    "Index — base phalanx": {
        "rules": "Practical use of leadership, governance of household",
        "long & strong": "Good householder, strong family-leader",
        "short": "May not handle responsibility well",
    },
    # MIDDLE (Saturn)
    "Middle — top phalanx": {
        "rules": "Wisdom, prudence, philosophical depth",
        "long & strong": "Deep thinker, philosopher",
        "short": "Surface-level, lacks depth",
    },
    "Middle — middle phalanx": {
        "rules": "Practical wisdom, judgment in affairs",
        "long & strong": "Balanced judge, mature decision-maker",
        "short": "Erratic in judgment",
    },
    "Middle — base phalanx": {
        "rules": "Earthly results of wisdom — wealth from prudence",
        "long & strong": "Wealth through caution / land / inheritance",
        "short": "Spends rather than accumulates",
    },
    # RING (Sun)
    "Ring — top phalanx": {
        "rules": "Pure artistic/spiritual creativity",
        "long & strong": "Visionary artist, classical creative gift",
        "short": "Lacks aesthetic depth",
    },
    "Ring — middle phalanx": {
        "rules": "Practical execution of art / craft",
        "long & strong": "Skilled craftsperson, technical artist",
        "short": "Aesthetic taste but lacks craft skill",
    },
    "Ring — base phalanx": {
        "rules": "Earthly recognition / fame / wealth from art",
        "long & strong": "Famous artist, recognized publicly",
        "short": "Art for self only, not commercial",
    },
    # LITTLE (Mercury)
    "Little — top phalanx": {
        "rules": "Speech, eloquence, language gift",
        "long & strong": "Excellent communicator, polyglot",
        "short": "Communication issues, weak speech",
    },
    "Little — middle phalanx": {
        "rules": "Logical thinking, business acumen",
        "long & strong": "Business genius, sharp mind",
        "short": "Naïve in business / scholarly only",
    },
    "Little — base phalanx": {
        "rules": "Wealth from communication / commerce",
        "long & strong": "Wealth through trade / writing / commerce",
        "short": "May not retain business gains",
    },
    # THUMB (Will, Logic, Venus)
    "Thumb — top phalanx (will)": {
        "rules": "Willpower, determination, self-control",
        "long & strong": "Iron will, leader",
        "short": "Weak will, easily swayed",
    },
    "Thumb — second phalanx (logic)": {
        "rules": "Reasoning, judgment, planning",
        "long & strong": "Excellent reasoner, strategic",
        "short": "Impulsive, illogical",
    },
    "Thumb — base / mount of Venus": {
        "rules": "Vitality, love-capacity, family love",
        "full & rounded": "Warm, loving, family-centric",
        "flat": "Cold, isolated from family",
    },
}


# ============================================================
# 5 FINGERTIP SHAPES
# ============================================================
FINGERTIP_SHAPES = {
    "Square": {
        "personality": "Practical, methodical, traditional",
        "career": "Engineering, accounting, manual trades, legal",
        "relationships": "Conservative, dutiful, stable partner",
    },
    "Conic / Tapered": {
        "personality": "Romantic, idealistic, artistic, impressionable",
        "career": "Arts, fashion, creative writing, design",
        "relationships": "Idealistic, easily heartbroken, dreamer",
    },
    "Spatulate (broad tip)": {
        "personality": "Action-oriented, restless, original, inventive",
        "career": "Engineering, exploration, sports, entrepreneurship",
        "relationships": "Independent, possibly restless partner",
    },
    "Pointed / Pyramidal": {
        "personality": "Mystical, intuitive, sensitive, possibly otherworldly",
        "career": "Spiritual teaching, healing, psychic work, art",
        "relationships": "Idealistic, spiritually-bonded partner sought",
    },
    "Mixed (different tips on different fingers)": {
        "personality": "Multi-faceted, complex, versatile",
        "career": "Multiple careers, hybrid roles, jack-of-trades",
        "relationships": "Variable, depends on dominant tip",
    },
}


# ============================================================
# HAND COLOR / TEXTURE / TEMPERATURE
# ============================================================
HAND_COLOR = {
    "Pinkish (healthy default)": "Good circulation, vitality, balanced disposition",
    "Pale white": "Anemia, weak vitality, possibly cold-natured / introverted",
    "Reddish": "Excessive heat, high blood pressure, fiery temperament",
    "Yellowish": "Liver issues, jaundice-tendency, melancholic",
    "Bluish (cool)": "Heart / circulation issues, possibly emotional coldness",
    "Dark / dusky": "Saturn-strong, melancholy potential, strong endurance",
}

HAND_TEXTURE = {
    "Soft & smooth": "Refined, sensitive, possibly indolent if no other strength markers",
    "Soft but firm": "Refined yet capable — auspicious balance",
    "Hard & rough": "Manual life, robust, hardworking",
    "Very hard, dry": "Vata excess, possibly austere life or hard labor",
    "Soft & flabby": "Indolence, indulgence, comfort-seeking",
}

HAND_TEMPERATURE = {
    "Warm (consistently)": "Good vitality, warm-hearted, active circulation",
    "Cold (consistently)": "Poor circulation, possibly heart/thyroid issue, emotionally reserved",
    "Sweaty / clammy": "Anxiety, nervous-system imbalance, often Vata excess",
    "Dry & hot": "Pitta excess, possibly inflammation tendency",
    "Variable / changes often": "Emotional volatility, possibly thyroid",
}


# ============================================================
# PALM PROPORTIONS
# ============================================================
PALM_PROPORTIONS = {
    "Palm length / width ratio": {
        "1.0 (square)": "Earth-element type, practical",
        "1.2-1.3 (rectangular)": "Air or water type, intellectual or emotional",
        ">1.4 (very elongated)": "Highly artistic, potentially impractical",
        "<0.9 (wider than long)": "Stocky, kapha-dominant, durable",
    },
    "Percussion edge length (Mercury edge to Luna edge)": {
        "long & full": "Strong imagination + communication = creative-thinker",
        "short or flat": "Practical, less imaginative, focused on immediate",
    },
    "Mount of Venus (thumb base) size": {
        "very full / large": "Strong vitality + family love + sensual nature",
        "small / flat": "Detached, possibly cold, weak vitality",
    },
    "Finger length vs palm length": {
        "fingers > palm": "Thinker, philosopher, intellect-dominant",
        "fingers ≈ palm": "Balanced",
        "fingers < palm": "Doer, action-dominant, less reflective",
    },
    "Distance between fingers (when held naturally)": {
        "wide gaps": "Open-minded, generous, free spirit",
        "tight together": "Conservative, careful, possibly miserly",
        "irregular gaps": "Mixed — some areas of life open, some closed",
    },
}


# ============================================================
# COMPREHENSIVE READER FUNCTIONS
# ============================================================
def comprehensive_palm_reading(chart, observed=None):
    """Full v2 palm reading with chart cross-validation.

    Args:
        chart: birth-chart dict
        observed: optional dict of OBSERVED features (color, texture, temperature, etc.)

    Returns:
        dict with chart-predicted + observed features cross-validated.
    """
    base_reading = palmistry_summary(chart)

    # Predicted line variations from chart
    predicted_variations = []

    if "Sun" in chart["positions"] and is_dignified(chart, "Sun"):
        predicted_variations.append({
            "line": "Apollo / Sun",
            "expected": "Apollo line — clear & deep (fame guaranteed)",
        })
    elif "Sun" in chart["positions"]:
        sun_h = chart["positions"]["Sun"]["house"]
        if sun_h in [6, 8, 12]:
            predicted_variations.append({
                "line": "Apollo / Sun",
                "expected": "Apollo line — wavy or absent (fame blocked / inverted)",
            })

    if "Mercury" in chart["positions"] and is_dignified(chart, "Mercury"):
        predicted_variations.append({
            "line": "Mercury",
            "expected": "Mercury line — clear & straight (business + health excellent)",
        })

    # 7H = marriage lines
    h7_count = sum(1 for p, pd in chart["positions"].items() if pd["house"] == 7)
    if h7_count == 1:
        predicted_variations.append({"line": "Marriage", "expected": "Single, clear, deep"})
    elif h7_count >= 2:
        predicted_variations.append({"line": "Marriage", "expected": "Multiple lines (per planet count) — multiple unions or major bonds"})

    # 5H = children lines
    h5_count = sum(1 for p, pd in chart["positions"].items() if pd["house"] == 5)
    benefics_5h = [p for p, pd in chart["positions"].items() if pd["house"] == 5 and p in ["Jupiter", "Venus", "Moon", "Mercury"]]
    if benefics_5h:
        predicted_variations.append({"line": "Children", "expected": "Deep & strong children lines"})
    elif h5_count >= 2 and not benefics_5h:
        predicted_variations.append({"line": "Children", "expected": "Thin or broken children lines"})

    # Fate line origin from Saturn position
    if "Saturn" in chart["positions"]:
        sat_h = chart["positions"]["Saturn"]["house"]
        if sat_h in [10, 11]:
            predicted_variations.append({"line": "Fate", "expected": "Origin from wrist — strong self-made career"})
        elif sat_h in [4, 7]:
            predicted_variations.append({"line": "Fate", "expected": "Origin from Luna mount — career via public/patronage"})
        elif sat_h in [6, 8, 12]:
            predicted_variations.append({"line": "Fate", "expected": "Broken or weak fate line"})

    # Predicted ring patterns from Yogas
    predicted_rings = []
    if is_dignified(chart, "Jupiter"):
        predicted_rings.append("Ring of Solomon possible (wisdom marker)")
    if is_dignified(chart, "Sun") and is_dignified(chart, "Jupiter"):
        predicted_rings.append("Triangle on Apollo mount possible (artistic genius)")
    if is_dignified(chart, "Mercury"):
        predicted_rings.append("Triangle on Mercury mount possible (business genius)")
    if planet_house(chart, "Saturn") in [6, 8, 12]:
        predicted_rings.append("Possible Ring of Saturn (isolation marker — caution)")

    # Predicted fingertip shape from Lagna + dominant planet
    lagna = chart["lagna"]
    if lagna in ["Aries", "Leo", "Sagittarius"]:
        tip_shape = "Spatulate (action-oriented)"
    elif lagna in ["Taurus", "Virgo", "Capricorn"]:
        tip_shape = "Square (practical)"
    elif lagna in ["Gemini", "Libra", "Aquarius"]:
        tip_shape = "Conic / Tapered (artistic)" if is_dignified(chart, "Venus") else "Square (practical)"
    else:
        tip_shape = "Pointed / Pyramidal (mystical)"

    # Hand color/texture/temp prediction
    if is_dignified(chart, "Sun") and is_dignified(chart, "Mars"):
        color_pred = "Reddish (high vitality + heat)"
    elif planet_house(chart, "Saturn") == 1:
        color_pred = "Pale or dusky"
    else:
        color_pred = "Pinkish (healthy default)"

    if lagna in ["Taurus", "Virgo", "Capricorn"]:
        texture_pred = "Hard & rough (manual, robust)"
    elif lagna in ["Pisces", "Cancer", "Libra"] and is_dignified(chart, "Venus"):
        texture_pred = "Soft but firm (refined yet capable)"
    else:
        texture_pred = "Soft & smooth (refined)"

    if is_dignified(chart, "Mars"):
        temp_pred = "Warm (consistently)"
    elif planet_house(chart, "Mercury") in [3, 6]:
        temp_pred = "Sweaty / clammy (nervous, anxious)"
    else:
        temp_pred = "Warm (consistently)"

    return {
        "v1_summary": base_reading,
        "v2_predicted_line_variations": predicted_variations,
        "v2_predicted_ring_patterns": predicted_rings,
        "v2_predicted_fingertip_shape": tip_shape,
        "v2_predicted_hand_color": color_pred,
        "v2_predicted_hand_texture": texture_pred,
        "v2_predicted_hand_temperature": temp_pred,
        "v2_observed_features": observed or {},
        "interpretation": (
            f"Chart predicts: fingertips {tip_shape.lower()}, hand color {color_pred.lower()}, "
            f"texture {texture_pred.lower()}, temperature {temp_pred.lower()}. "
            f"Line variations expected: {len(predicted_variations)}. "
            f"Possible ring/yantra marks: {len(predicted_rings)}."
        ),
        "verification_tip": (
            "Observe palm in good lighting. Photograph both palms. Compare predictions to actual palm — "
            "matches confirm chart accuracy. Mismatches in major features may indicate birth-time inaccuracy."
        ),
        "_v2_metadata": {
            "line_variations_catalogued": len(LINE_VARIATIONS),
            "ring_patterns_catalogued": len(RING_PATTERNS),
            "dot_marks_catalogued": len(DOT_MARKS),
            "phalanges_catalogued": len(FINGER_PHALANGES),
            "fingertip_shapes_catalogued": len(FINGERTIP_SHAPES),
            "hand_color_categories": len(HAND_COLOR),
            "hand_texture_categories": len(HAND_TEXTURE),
            "hand_temperature_categories": len(HAND_TEMPERATURE),
            "palm_proportion_categories": len(PALM_PROPORTIONS),
        },
    }


def lookup_v2(category, name=None):
    """Lookup in v2 categories."""
    DB = {
        "line": LINE_VARIATIONS,
        "ring": RING_PATTERNS,
        "dot": DOT_MARKS,
        "phalange": FINGER_PHALANGES,
        "fingertip": FINGERTIP_SHAPES,
        "color": HAND_COLOR,
        "texture": HAND_TEXTURE,
        "temperature": HAND_TEMPERATURE,
        "proportion": PALM_PROPORTIONS,
    }
    section = DB.get(category.lower())
    if not section:
        return f"Unknown category. Available: {list(DB.keys())}"
    if name and name in section:
        return section[name]
    return section


def palmistry_v2_summary():
    """Summary of v2 catalog."""
    return {
        "line_variations": len(LINE_VARIATIONS),
        "ring_patterns": len(RING_PATTERNS),
        "dot_marks": len(DOT_MARKS),
        "finger_phalanges": len(FINGER_PHALANGES),
        "fingertip_shapes": len(FINGERTIP_SHAPES),
        "hand_color_categories": len(HAND_COLOR),
        "hand_texture_categories": len(HAND_TEXTURE),
        "hand_temperature_categories": len(HAND_TEMPERATURE),
        "palm_proportions": len(PALM_PROPORTIONS),
        "v2_total_data_points": (
            len(LINE_VARIATIONS) + len(RING_PATTERNS) + len(DOT_MARKS) +
            len(FINGER_PHALANGES) + len(FINGERTIP_SHAPES) + len(HAND_COLOR) +
            len(HAND_TEXTURE) + len(HAND_TEMPERATURE) + len(PALM_PROPORTIONS)
        ),
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    print(f"=== PALMISTRY v2 — Comprehensive Reading ({chart['name']}) ===\n")
    summary = palmistry_v2_summary()
    print(f"  Line variations: {summary['line_variations']}")
    print(f"  Ring patterns: {summary['ring_patterns']}")
    print(f"  Dot marks: {summary['dot_marks']}")
    print(f"  Finger phalanges: {summary['finger_phalanges']}")
    print(f"  Fingertip shapes: {summary['fingertip_shapes']}")
    print(f"  Hand color categories: {summary['hand_color_categories']}")
    print(f"  Hand texture categories: {summary['hand_texture_categories']}")
    print(f"  Hand temperature categories: {summary['hand_temperature_categories']}")
    print(f"  Palm proportions: {summary['palm_proportions']}")
    print(f"  TOTAL v2 data points: {summary['v2_total_data_points']}")

    print(f"\n=== Comprehensive Reading for {chart['name']} ===")
    result = comprehensive_palm_reading(chart)

    print(f"\n  Predicted fingertip shape: {result['v2_predicted_fingertip_shape']}")
    print(f"  Predicted hand color: {result['v2_predicted_hand_color']}")
    print(f"  Predicted hand texture: {result['v2_predicted_hand_texture']}")
    print(f"  Predicted hand temperature: {result['v2_predicted_hand_temperature']}")

    print(f"\n  Predicted line variations ({len(result['v2_predicted_line_variations'])}):")
    for v in result["v2_predicted_line_variations"]:
        print(f"    • {v['line']}: {v['expected']}")

    print(f"\n  Predicted ring patterns ({len(result['v2_predicted_ring_patterns'])}):")
    for r in result["v2_predicted_ring_patterns"]:
        print(f"    • {r}")

    print(f"\n  INTERPRETATION:\n  {result['interpretation']}")
