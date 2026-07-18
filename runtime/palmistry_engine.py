"""Palmistry (Hasta Samudrika Shastra) — classical knowledge base + chart cross-validator.

Source: Hasta Samudrika Shastra (Sanskrit), Cheiro's classical Western adaptation,
Sanjay Sharma's "Practical Palmistry," Indian palm-reading traditions.

Mode 1: Lookup API — query specific feature (mount/line/finger/print) interpretation
Mode 2: Chart cross-validator — predict expected hand features from birth chart
        (Mars in 1H = thick lower Mars mount; Venus strong = full Venus mount, etc.)
"""
import sys
sys.path.insert(0, ".")
from vedic_core import DIGNITIES, PLANETS_MAIN

# ============================================================
# 4 HAND SHAPES — elemental classification
# ============================================================
HAND_SHAPES = {
    "Earth": {
        "description": "Square palm + short fingers",
        "traits": "Practical, grounded, manual professions, stable marriage, strong physical health, steady wealth accumulation",
        "career": "Construction, agriculture, manual trades, traditional crafts",
        "marriage": "Long, stable, traditional",
        "health": "Strong constitution, may struggle with sedentary modern lifestyle",
        "matches_chart": "Saturn-strong, fixed signs in lagna, Mars in earth signs",
    },
    "Air": {
        "description": "Square palm + long fingers",
        "traits": "Intellectual, communicative, teaching/writing/journalism, mental restlessness, multiple relationships possible",
        "career": "Teaching, journalism, writing, communication, IT",
        "marriage": "Companion-based, may experience multiple partnerships",
        "health": "Nervous-system sensitive, anxiety-prone",
        "matches_chart": "Mercury-strong, air signs in lagna, Gemini/Libra/Aquarius emphasis",
    },
    "Fire": {
        "description": "Rectangular palm + short fingers",
        "traits": "Action-oriented, entrepreneurial, leadership, accident-prone, intense romantic life, fame potential",
        "career": "Sports, military, entrepreneurship, leadership",
        "marriage": "Passionate, intense, can be volatile",
        "health": "Accident-prone, blood pressure, fevers",
        "matches_chart": "Mars-strong, Sun in lagna, Aries/Leo/Sagittarius emphasis",
    },
    "Water": {
        "description": "Rectangular palm + long fingers",
        "traits": "Artistic, emotional, intuitive, prone to mood disorders, creative income",
        "career": "Arts, music, healing, psychology, mysticism",
        "marriage": "Emotionally complex partner, depth-based",
        "health": "Mood-related, addiction-prone, fluid imbalances",
        "matches_chart": "Moon-strong, water signs in lagna, Cancer/Scorpio/Pisces",
    },
}

# ============================================================
# 7 PLANETARY MOUNTS — fleshy pads on palm
# ============================================================
MOUNTS = {
    "Jupiter": {
        "location": "Below index finger",
        "rules": "Leadership, ambition, self-respect, religion, dharma",
        "excessive": "Arrogance, dominance, religious zealotry",
        "flat": "Lack of confidence, weak self-belief",
        "ideal": "Healthy ambition, natural authority, dharmic conduct",
        "chart_correlate": "Jupiter strength in chart (own/exalted/Hamsa Yoga)",
    },
    "Saturn": {
        "location": "Below middle finger",
        "rules": "Wisdom, melancholy, research, real-estate, discipline",
        "excessive": "Isolation, depression, severe austerity",
        "flat": "Frivolity, lack of purpose, inability to commit",
        "ideal": "Mature judgment, hard-work ethic, longevity",
        "chart_correlate": "Saturn dignity (Sasa Yoga = prominent); Saturn in lagna",
    },
    "Sun": {
        "location": "Below ring finger (Apollo)",
        "rules": "Fame, art, optimism, recognition, brilliance",
        "excessive": "Vanity, showmanship, ego-inflation",
        "flat": "Obscurity, lack of recognition, dimmed creativity",
        "ideal": "Public success, artistic talent, charismatic presence",
        "chart_correlate": "Sun strong (own/exalted), 5H/10H emphasis",
    },
    "Mercury": {
        "location": "Below little finger",
        "rules": "Commerce, science, oratory, healing, communication",
        "excessive": "Cunning, deceptive speech, restless mind",
        "flat": "Poor communication, slow learning",
        "ideal": "Eloquent, sharp business sense, healing capacity",
        "chart_correlate": "Mercury strong (Bhadra Yoga); 3H/2H emphasis",
    },
    "Venus": {
        "location": "Base of thumb",
        "rules": "Love, vitality, music, sensuality, family love",
        "excessive": "Lust, indulgence, addiction to pleasure",
        "flat": "Coldness, weak marriage, low vitality",
        "ideal": "Warm-hearted, romantic, artistic, healthy libido",
        "chart_correlate": "Venus dignity (Malavya Yoga); 7H Venus",
    },
    "Luna": {
        "location": "Opposite Venus, base outer edge",
        "rules": "Imagination, travel, intuition, foreign connections, psychic ability",
        "excessive": "Fantasy, escapism, lying, delusion",
        "flat": "No creativity, no imagination, no foreign connections",
        "ideal": "Intuitive, well-traveled, imaginative, dreams come true",
        "chart_correlate": "Moon strong; Rahu in 9H/12H (foreign); 12H emphasis",
    },
    "Mars": {
        "location": "Two mounts: Upper Mars (under Mercury) + Lower Mars (under Jupiter)",
        "rules": "Lower=aggression, Upper=resistance/endurance, Plain of Mars=courage center",
        "excessive": "Violent temper, recklessness",
        "flat": "Cowardice, lack of fight",
        "ideal": "Calm courage, defensive strength, strategic action",
        "chart_correlate": "Mars own/exalted (Ruchaka Yoga); 3H Mars; warrior placements",
    },
}

# ============================================================
# 4 MAIN LINES + 12 SECONDARY LINES
# ============================================================
MAIN_LINES = {
    "Life Line": {
        "location": "Curves around Venus mount",
        "predicts": "Vitality, constitution, major life upheavals (NOT death-date)",
        "breaks": "Illness or relocation events",
        "chained": "Weak immunity, recurring illness",
        "doubled (Mars line alongside)": "Strong recovery, military protection, double-vitality",
        "length": "Vitality (NOT lifespan — common myth)",
        "starts joined to head line": "Cautious upbringing, dependent early life",
        "starts separate from head": "Independent, early self-reliance",
    },
    "Heart Line": {
        "location": "Across upper palm",
        "starts under Jupiter": "Idealistic love, romantic high standards",
        "starts under Saturn": "Lustful or practical love",
        "chained": "Multiple heartbreaks, emotional turbulence",
        "forked end": "Balanced love, multiple love-channels",
        "islands": "Emotional crises at specific life-points",
        "deep & clear": "Faithful marriage, strong emotional commitments",
        "broken": "Heartbreak with timing-mark",
    },
    "Head Line": {
        "location": "Across middle palm",
        "long & straight": "Analytical, systematic thinker",
        "sloped to Luna": "Imaginative, creative writer, artist",
        "forked (writer's fork)": "Versatile, multi-faceted intellect",
        "short": "Quick, impulsive thinker",
        "broken": "Head injury or major mental crisis at marked-point",
        "joined to life line at start": "Cautious, family-influenced thinking",
        "doubled": "Two career paths or dual mental capacity",
    },
    "Fate Line (Saturn line)": {
        "location": "Vertical, base to middle finger",
        "origin from wrist": "Self-made early career",
        "origin from Luna": "Career via others' patronage / public",
        "origin from life line": "Family business inheritance",
        "broken": "Career changes at marked points",
        "absent": "Freelance/unstructured career, no fixed destiny path",
        "ending at heart line": "Career-vs-love conflict in middle age",
        "ending at head line": "Career limited by mental ability or choice",
    },
}

SECONDARY_LINES = {
    "Sun/Apollo Line": "Vertical to ring finger. Presence + clarity = fame, public recognition, artistic success",
    "Mercury/Health Line": "Base to little finger. Clear = good business; wavy = digestive issues; absent on healthy hand = good (no health worries)",
    "Ring of Solomon": "Semicircle around Jupiter mount. Wisdom, occult interest, teaching ability, judicial mind",
    "Ring of Saturn": "Semicircle around Saturn mount (NEGATIVE). Isolation, depression, restricted destiny",
    "Girdle of Venus": "Semicircle above heart line. Heightened sensuality; if broken = emotional volatility",
    "Marriage Lines": "Short horizontal lines on outer edge below little finger. Count = significant unions. Length = duration. Forked = separation. Drooping into heart line = widowhood/partner illness",
    "Children Lines": "Vertical lines rising from marriage lines. Strong/deep = sons; thin = daughters; broken = miscarriage/estrangement",
    "Travel Lines": "Horizontal lines from edge of palm into Luna mount. Each significant line = major foreign journey or relocation",
    "Money/Wealth Triangle": "Formed by head, life, and Mercury lines. Closed and clear = wealth retention; open = leakage",
    "Bracelet Lines (Rascettes)": "At wrist. Three clear unbroken bracelets = long life (each ~25 years). Topmost most important; chained topmost = early-life difficulty",
    "Via Lasciva": "Sister line below Mercury — indulgences/addictions",
    "Intuition Line": "Curves on Luna mount — psychic ability, mediumship",
}

# ============================================================
# 5 FINGERS — planetary attributions
# ============================================================
FINGERS = {
    "Index (Jupiter)": {
        "long": "Leadership, ambition, dominant nature",
        "short": "Self-doubt, follower tendency",
        "bent": "Manipulator, scheming",
        "ideal": "Equal to ring finger = balanced ambition",
    },
    "Middle (Saturn)": {
        "straight": "Balanced discipline, patient nature",
        "bent": "Melancholy, brooding, anti-social",
        "very long": "Excessive seriousness, isolation",
        "short": "Frivolity, lack of depth",
    },
    "Ring (Sun)": {
        "long & straight": "Artistic recognition, fame potential",
        "short": "Obscurity, lack of recognition",
        "longer than index": "Risk-taker, gambler",
        "bent": "Frustrated creativity",
    },
    "Little (Mercury)": {
        "long": "Eloquence, business acumen, communication mastery",
        "short": "Communication issues, business struggles",
        "bent": "Dishonesty risk, manipulation",
        "reaches first knuckle of ring finger": "Excellent communicator",
    },
    "Thumb": {
        "first phalanx (willpower)": "Long = strong will; short = weak resolve",
        "second phalanx (logic)": "Long = strong reasoning; short = impulsive",
        "stiff": "Inflexible, rigid",
        "flexible": "Adaptable, easy-going",
        "thumb angle wide": "Generous, expansive personality",
        "thumb angle narrow": "Reserved, cautious",
    },
}

# ============================================================
# FINGERPRINT TYPES (Vedic Sankha-Padma-Chakra-Dhwaja)
# ============================================================
FINGERPRINTS = {
    "Chakra (whorl)": {
        "shape": "Concentric circles forming a vortex",
        "meaning": "Strong individualism, leadership, often spiritual seekers",
        "career": "Independent professional, founder, spiritual path",
        "personality": "Self-driven, original thinker, sometimes isolated",
    },
    "Padma (loop)": {
        "shape": "Curved loop opening to one side",
        "meaning": "Adaptable, social, balanced — most common",
        "career": "Team-player, versatile, social profession",
        "personality": "Flexible, friendly, accommodating",
    },
    "Sankha (conch / arch)": {
        "shape": "Wave-like arch",
        "meaning": "Practical, stoic, workmanlike, sometimes stubborn",
        "career": "Skilled worker, traditional craftsman, reliable employee",
        "personality": "Steady, practical, low drama",
    },
    "Dhwaja (composite/tented arch)": {
        "shape": "Tented arch with central column",
        "meaning": "Unusual destiny, mixed influences, transformative life path",
        "career": "Reformer, hybrid-field professional, change-maker",
        "personality": "Complex, multi-layered, unconventional",
    },
}


# ============================================================
# CHART CROSS-VALIDATION
# ============================================================
def predict_hand_features_from_chart(chart):
    """Predict expected hand features from birth chart.

    Cross-validates: planetary strengths in chart should manifest as
    specific mount development, line clarity, fingerprint dominance.
    """
    pos = chart["positions"]
    out = {
        "predicted_dominant_mount": [],
        "predicted_dominant_lines": [],
        "predicted_fingerprint_pattern": "",
        "predicted_hand_shape": "",
        "predicted_marriage_line_count": 0,
        "predicted_children_line_count": 0,
    }

    # Dominant mounts based on planetary strength
    for p in PLANETS_MAIN:
        if p not in pos: continue
        dignity = DIGNITIES.get((p, pos[p]["rasi"]), "neutral")
        h = pos[p]["house"]
        if dignity in ["Own", "Exalted", "Exalted/Own"] and h in [1, 4, 5, 7, 9, 10]:
            out["predicted_dominant_mount"].append(p)

    # Hand shape from Lagna element
    lagna = chart["lagna"]
    if lagna in ["Aries", "Leo", "Sagittarius"]:
        out["predicted_hand_shape"] = "Fire (rectangular palm + short fingers)"
    elif lagna in ["Taurus", "Virgo", "Capricorn"]:
        out["predicted_hand_shape"] = "Earth (square palm + short fingers)"
    elif lagna in ["Gemini", "Libra", "Aquarius"]:
        out["predicted_hand_shape"] = "Air (square palm + long fingers)"
    else:  # water signs
        out["predicted_hand_shape"] = "Water (rectangular palm + long fingers)"

    # Marriage line count from 7H planets count
    h7_occupants = [p for p, pd in pos.items() if pd["house"] == 7]
    out["predicted_marriage_line_count"] = max(1, len(h7_occupants))

    # Children line count from 5H
    h5_occupants = [p for p, pd in pos.items() if pd["house"] == 5]
    out["predicted_children_line_count"] = max(0, len(h5_occupants))

    # Fingerprint dominance from Atmakaraka
    try:
        from jaimini_full import chara_karakas_jaimini
        karakas = chara_karakas_jaimini(chart)
        ak = karakas[0][1] if karakas else None
        if ak in ["Sun", "Mars"]:
            out["predicted_fingerprint_pattern"] = "Chakra (whorl) — strong individualism"
        elif ak in ["Moon", "Venus"]:
            out["predicted_fingerprint_pattern"] = "Padma (loop) — adaptable, social"
        elif ak in ["Saturn"]:
            out["predicted_fingerprint_pattern"] = "Sankha (conch) — practical, stoic"
        elif ak in ["Rahu", "Ketu"]:
            out["predicted_fingerprint_pattern"] = "Dhwaja (composite) — unusual destiny"
        else:
            out["predicted_fingerprint_pattern"] = "Padma (loop) — most common"
    except Exception:
        pass

    # Dominant line predictions
    if "Jupiter" in pos and pos["Jupiter"]["house"] == 1:
        out["predicted_dominant_lines"].append("Strong life line + Ring of Solomon (wisdom)")
    if "Saturn" in pos and pos["Saturn"]["house"] in [10, 11]:
        out["predicted_dominant_lines"].append("Strong fate line from wrist")
    if "Sun" in pos and pos["Sun"]["house"] in [1, 5, 10]:
        out["predicted_dominant_lines"].append("Clear Apollo line (fame)")
    if "Mercury" in pos and pos["Mercury"]["house"] in [1, 2, 3, 10]:
        out["predicted_dominant_lines"].append("Strong Mercury/health line")

    return out


def palmistry_summary(chart):
    """Generate full palmistry reading using chart cross-validation."""
    cross = predict_hand_features_from_chart(chart)
    return {
        "expected_hand_shape": cross["predicted_hand_shape"],
        "dominant_mounts_predicted": cross["predicted_dominant_mount"],
        "dominant_lines_predicted": cross["predicted_dominant_lines"],
        "fingerprint_pattern_predicted": cross["predicted_fingerprint_pattern"],
        "marriage_lines_count_expected": cross["predicted_marriage_line_count"],
        "children_lines_count_expected": cross["predicted_children_line_count"],
        "interpretation": (
            f"Based on the chart, you should have a {cross['predicted_hand_shape']} hand. "
            f"Dominant mounts (developed/raised): {', '.join(cross['predicted_dominant_mount']) if cross['predicted_dominant_mount'] else 'balanced'}. "
            f"Expected fingerprint pattern dominance: {cross['predicted_fingerprint_pattern']}. "
            f"Marriage lines: ~{cross['predicted_marriage_line_count']} significant. "
            f"Children lines: ~{cross['predicted_children_line_count']} expected."
        ),
        "verification_tip": (
            "Photograph your right palm in good lighting. Compare against the predictions above — "
            "matches confirm chart accuracy; major mismatches may indicate birth-time inaccuracy."
        ),
    }


def lookup_feature(feature_type, feature_name):
    """Lookup interpretation of any palmistry feature."""
    feature_type = feature_type.lower()
    if feature_type == "mount":
        return MOUNTS.get(feature_name, "Mount not found")
    elif feature_type == "line":
        return MAIN_LINES.get(feature_name) or SECONDARY_LINES.get(feature_name, "Line not found")
    elif feature_type == "finger":
        return FINGERS.get(feature_name, "Finger not found")
    elif feature_type == "fingerprint":
        return FINGERPRINTS.get(feature_name, "Fingerprint type not found")
    elif feature_type == "shape":
        return HAND_SHAPES.get(feature_name, "Hand shape not found")
    return None


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    result = palmistry_summary(chart)
    print(f"=== PALMISTRY READING (chart-predicted) for {chart['name']} ===\n")
    for k, v in result.items():
        if k == "interpretation":
            continue
        print(f"  {k}: {v}")
    print(f"\n  READING:")
    print(f"  {result['interpretation']}")
    print(f"\n  TIP: {result['verification_tip']}")
