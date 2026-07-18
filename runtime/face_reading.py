"""Face Reading (Mukha Samudrika Shastra) — classical knowledge base + chart cross-validator.

Source: Mukha Samudrika Shastra (Sanskrit), Hindu physiognomy, classical Indian face-reading.
Plus Sariraka Lakshana (body characteristics) for face-specific portions.

Mode 1: Lookup API — query specific feature
Mode 2: Chart cross-validator — predict expected facial features from birth chart
"""
import sys
sys.path.insert(0, ".")
from vedic_core import DIGNITIES, RASIS, RASI_LORDS

# ============================================================
# FOREHEAD — 3-band life-stage map
# ============================================================
FOREHEAD = {
    "shape": {
        "high & broad": "Intellectual, ambitious, success in mental work, good lineage",
        "low & narrow": "Practical, hands-on temperament, may struggle academically",
        "wide & rounded": "Generous, sociable, public-facing career",
        "square": "Logical, structured thinker, suited for engineering/law",
        "tapering at top": "Spiritual, philosophical, often reclusive",
        "bumpy / uneven": "Volatile temperament, unstable mind",
    },
    "lines": {
        "3 horizontal lines (clear)": "Long life, balanced fate, classical sign of dignity",
        "many crossing lines": "Mental restlessness, multiple worries, unstable career",
        "vertical line between brows": "Strong concentration, intensity, possibly irritable",
        "diagonal lines": "Travel-prone, foreign connections, multi-directional life",
        "no lines (smooth)": "Childlike or undeveloped destiny; could be either innocent or shallow",
    },
    "bands": {
        "upper third": "Early life (0-25y) — wisdom from family, education",
        "middle third": "Middle life (25-50y) — career peak, marriage, children",
        "lower third (above brows)": "Later life (50+y) — fortune, reputation, legacy",
    },
}

# ============================================================
# EYES (most-read feature)
# ============================================================
EYES = {
    "size": {
        "large": "Open-hearted, expressive, generous, easily moved",
        "medium": "Balanced, observant, neither secretive nor exhibitionist",
        "small": "Sharp-witted, calculating, secretive, detail-focused",
    },
    "shape": {
        "almond": "Classical beauty, balanced personality, fortunate",
        "round": "Childlike, curious, can be naive",
        "elongated": "Aesthetic sense, artistic, sometimes melancholic",
        "deep-set": "Introverted, philosophical, careful in trust",
        "protruding": "Excessive thyroid energy, may be excitable, talkative",
    },
    "color": {
        "deep brown": "Standard, balanced, traditional family-line",
        "light brown / honey": "Charismatic, attracts opposite sex, mixed lineage often",
        "black/very dark": "Mystical, spiritual, intense karmic line",
        "green/blue (rare)": "Foreign-blood, unconventional fate, artistic",
        "grey/blue (in old age)": "Wisdom, possible vision-loss in late years",
    },
    "lustre": {
        "bright & moist": "Vitality, good health, romantic life active",
        "dull": "Health weakness, depression risk, low vitality",
        "fierce / piercing": "Strong willpower, leadership, intimidates others",
        "soft / dreamy": "Artistic, emotional, possibly indecisive",
    },
    "asymmetry": {
        "right eye larger": "Father-line dominant, more masculine traits, action-oriented",
        "left eye larger": "Mother-line dominant, more feminine traits, intuitive",
        "equal": "Balanced inheritance, equilibrium",
    },
}

# ============================================================
# EYEBROWS
# ============================================================
EYEBROWS = {
    "thick & dense": "Strong willpower, robust health, confident",
    "thin & sparse": "Sensitive, refined, less physical stamina",
    "high-arched": "Pride, distance from others, intellectual",
    "straight": "Stable, logical, reliable",
    "joined / unibrow": "Intense focus or jealousy, possessive nature",
    "very wide apart": "Open-minded, generous, broad horizons",
    "uneven (one higher)": "Inner conflict, dual nature, possibly creative",
    "ending in a sweep": "Aesthetic sensitivity, artistic disposition",
    "thinning toward outer end": "Career fades in later life, retirement at proper time",
}

# ============================================================
# NOSE — wealth karaka
# ============================================================
NOSE = {
    "shape": {
        "long & straight": "Authority, leadership, family pride, classical wealth",
        "short & flat": "Practical, humble, may struggle for recognition",
        "aquiline / hooked": "Strategic mind, business acumen, sometimes ruthless",
        "rounded tip": "Generous, curious, accumulates moderate wealth",
        "pointed tip": "Sharp intellect, gossip-prone, restless",
        "broad tip": "Stable wealth-building, slow but reliable income",
        "small with high bridge": "Aristocratic, refined, possible foreign connections",
    },
    "nostrils": {
        "small & tight": "Conservative spender, frugal, savings-oriented",
        "wide & open": "Generous spender, philanthropic, may waste money",
        "uneven": "Inconsistent finances, irregular income",
        "flared": "Ambitious, big spender, big earner",
    },
    "wealth_indicator": {
        "fleshy & rounded tip + symmetrical": "Strong wealth potential, money flows naturally",
        "thin & bony": "Wealth comes through hard work, not charm",
        "dark spots / lines": "Financial setbacks at marked-life-stage",
    },
}

# ============================================================
# MOUTH / LIPS
# ============================================================
LIPS = {
    "thick lips": "Sensual, passionate, generous in love and food",
    "thin lips": "Reserved, careful in speech, possibly cold in affection",
    "even thickness": "Balanced communication, fair speech",
    "upper thicker than lower": "Talkative, expressive, dominant in relationships",
    "lower thicker": "Receptive listener, emotional depth, may be exploited",
    "wide mouth": "Eloquent, public-speaker, leadership capacity",
    "small mouth": "Private, careful with words, secretive",
    "drooping corners": "Pessimism, hardships in life, depression-prone",
    "upturned corners": "Optimist, cheerful, attracts good fortune",
    "color: red & moist": "Vitality, romantic activity, good digestion",
    "color: pale / blue": "Health concerns, low vitality, possibly heart-related",
}

# ============================================================
# CHIN — longevity indicator
# ============================================================
CHIN = {
    "strong / square": "Determination, longevity, leadership, willpower",
    "weak / receding": "Indecisive, may be easily influenced, shorter lifespan classical-belief",
    "double chin": "Wealth indicator, comforts in later life, possibly indulgent",
    "pointed": "Sharp intellect, precise nature, possibly aggressive",
    "rounded": "Friendly, sociable, balanced character",
    "cleft chin": "Determined, dramatic, attention-seeking, often charismatic",
    "long chin": "Long lifespan, perseverance, slow to anger",
    "short chin": "Quick reactions, may not preserve resources well",
}

# ============================================================
# EARS — longevity + wisdom
# ============================================================
EARS = {
    "size": {
        "large": "Long life, wisdom-receptive, listens well",
        "small": "Quick decisions, may not retain advice",
        "medium": "Balanced learning capacity",
    },
    "lobes": {
        "long / pendulous": "Buddha-like wisdom, longevity, spiritual receptivity, wealth in old age",
        "attached / no lobe": "Practical, modern, may rebel against tradition",
        "free-hanging": "Independent, free-thinking, generous",
    },
    "position": {
        "high (above eyebrow)": "Intellectual, academic, scholarly",
        "low (below eye line)": "Sensual, instinctive, hands-on professions",
        "average level": "Balanced",
    },
    "shape": {
        "well-formed & rounded": "Harmonious life, fortune",
        "pointed at top": "Sharp instincts, predator-like awareness",
        "deformed / cauliflower": "Past trauma marker, possible head injury",
    },
    "color": {
        "pinkish": "Healthy, vital",
        "white & pale": "Cold constitution, possible thyroid issues",
        "reddish": "Excessive heat, blood pressure risk",
    },
}

# ============================================================
# CHEEKS / FACIAL BONES
# ============================================================
CHEEKS = {
    "high cheekbones": "Authority, presence, may face responsibilities early",
    "flat cheeks": "Modest, humble, may lack initiative",
    "rounded fleshy cheeks": "Comfort-loving, well-fed, prosperous",
    "hollow cheeks": "Hard life, austerity, possible health weakness",
    "dimples": "Charming, playful, romantic appeal",
    "pinkish glow": "Vitality, romance active, good circulation",
    "dark spots/sun damage": "Travel/foreign exposure or specific health markers",
}

# ============================================================
# OVERALL FACE SHAPE — major life-pattern indicator
# ============================================================
FACE_SHAPES = {
    "Oval": {
        "traits": "Balanced, harmonious, classical beauty, diplomatic",
        "career": "Public-facing, advisory, communications",
        "marriage": "Stable, often arranged-style, smooth partnership",
        "longevity": "Standard 70-80 range",
    },
    "Round": {
        "traits": "Sociable, optimistic, comfort-loving, family-oriented",
        "career": "Hospitality, sales, customer-service, food industry",
        "marriage": "Family-centered, child-friendly partner",
        "longevity": "Long if healthy lifestyle maintained",
    },
    "Square": {
        "traits": "Disciplined, structured, traditional, reliable",
        "career": "Engineering, military, construction, traditional trades",
        "marriage": "Conventional, dutiful, partner of similar background",
        "longevity": "Long, robust constitution",
    },
    "Heart-shaped (wide forehead, narrow chin)": {
        "traits": "Creative, intuitive, sensitive, expressive",
        "career": "Arts, design, healing, creative writing",
        "marriage": "Romantic, deep emotional bond",
        "longevity": "Standard, watch nervous-system health",
    },
    "Long / oblong": {
        "traits": "Intellectual, analytical, academic, possibly austere",
        "career": "Research, academia, philosophy, judiciary",
        "marriage": "Intellectual partner, may marry late",
        "longevity": "Long, but watch digestive health",
    },
    "Triangular (wide jaw, narrow forehead)": {
        "traits": "Practical, physical, sensual, action-oriented",
        "career": "Sports, manual trades, military, practical industry",
        "marriage": "Passionate, partner of strong physical presence",
        "longevity": "Strong constitution but accident-prone",
    },
    "Diamond (narrow forehead+chin, wide cheeks)": {
        "traits": "Unique destiny, unconventional, may be artistic genius",
        "career": "Arts, performance, niche professions",
        "marriage": "Late or unusual marriage, foreign partner possible",
        "longevity": "Variable, depends on lifestyle",
    },
}

# ============================================================
# CHART → EXPECTED FACE FEATURES
# ============================================================
def predict_face_features(chart):
    """Predict expected facial features from birth chart."""
    pos = chart["positions"]
    lagna = chart["lagna"]

    out = {
        "predicted_face_shape": "",
        "predicted_eye_size": "",
        "predicted_nose_type": "",
        "predicted_lip_type": "",
        "predicted_chin_strength": "",
        "predicted_complexion": "",
        "dominant_feature": "",
    }

    # Face shape from Lagna element
    if lagna in ["Aries", "Leo", "Sagittarius"]:  # fire
        out["predicted_face_shape"] = "Triangular or square (wider jaw, fiery presence)"
    elif lagna in ["Taurus", "Virgo", "Capricorn"]:  # earth
        out["predicted_face_shape"] = "Square or oval (sturdy, grounded look)"
    elif lagna in ["Gemini", "Libra", "Aquarius"]:  # air
        out["predicted_face_shape"] = "Long/oblong or oval (intellectual look)"
    else:  # water
        out["predicted_face_shape"] = "Round or heart-shaped (soft, dreamy)"

    # Eyes from Sun + Moon
    if "Sun" in pos and "Moon" in pos:
        sun_dignity = DIGNITIES.get(("Sun", pos["Sun"]["rasi"]), "neutral")
        moon_dignity = DIGNITIES.get(("Moon", pos["Moon"]["rasi"]), "neutral")
        if sun_dignity in ["Own", "Exalted"] and moon_dignity in ["Own", "Exalted"]:
            out["predicted_eye_size"] = "Large, bright, magnetic"
        elif sun_dignity == "Debil" or moon_dignity == "Debil":
            out["predicted_eye_size"] = "Smaller or dull, possibly health-marker"
        else:
            out["predicted_eye_size"] = "Medium, balanced"

    # Nose from Mercury (for sharpness) + Saturn (for length)
    if "Mercury" in pos:
        merc_h = pos["Mercury"]["house"]
        if merc_h in [1, 5, 10]:
            out["predicted_nose_type"] = "Long & straight, classical aristocratic look"
        elif merc_h in [6, 8, 12]:
            out["predicted_nose_type"] = "Short or possibly irregular shape"
        else:
            out["predicted_nose_type"] = "Standard, well-formed"

    # Lips from Venus
    if "Venus" in pos:
        ven_dignity = DIGNITIES.get(("Venus", pos["Venus"]["rasi"]), "neutral")
        if ven_dignity in ["Own", "Exalted"]:
            out["predicted_lip_type"] = "Full, rosy, well-shaped (sensual + expressive)"
        elif ven_dignity == "Debil":
            out["predicted_lip_type"] = "Thinner or paler (reserved expression)"
        else:
            out["predicted_lip_type"] = "Even, balanced"

    # Chin from Saturn (longevity) + Mars (firmness)
    if "Saturn" in pos and "Mars" in pos:
        sat_h = pos["Saturn"]["house"]
        mars_h = pos["Mars"]["house"]
        if sat_h in [1, 4, 10] and mars_h in [1, 3, 10]:
            out["predicted_chin_strength"] = "Strong, square (longevity + determination)"
        elif sat_h in [6, 8, 12]:
            out["predicted_chin_strength"] = "Receding or weak (possible early-life health concern)"
        else:
            out["predicted_chin_strength"] = "Average"

    # Complexion from Lagna lord + Moon
    LAGNA_COMPLEXION = {
        "Aries":"Reddish/fair", "Taurus":"Fair", "Gemini":"Wheat/medium",
        "Cancer":"Pale fair", "Leo":"Honey/golden", "Virgo":"Wheat",
        "Libra":"Fair pinkish", "Scorpio":"Dusky", "Sagittarius":"Fair",
        "Capricorn":"Dark/dusky", "Aquarius":"Mixed/medium", "Pisces":"Fair to wheat",
    }
    out["predicted_complexion"] = LAGNA_COMPLEXION.get(lagna, "?")

    # Dominant feature
    strongest = []
    for p, name in [("Sun","Eyes"),("Moon","Eyes"),("Mercury","Nose"),("Venus","Lips"),("Saturn","Chin"),("Mars","Cheekbones"),("Jupiter","Forehead")]:
        if p in pos:
            d = DIGNITIES.get((p, pos[p]["rasi"]), "neutral")
            if d in ["Own", "Exalted"]:
                strongest.append(name)
    out["dominant_feature"] = ", ".join(set(strongest)) if strongest else "Balanced"

    return out


def face_reading_summary(chart):
    """Generate full face-reading prediction with chart cross-validation."""
    pred = predict_face_features(chart)
    return {
        **pred,
        "interpretation": (
            f"Based on your chart, you should have: {pred['predicted_face_shape']} face shape, "
            f"{pred['predicted_eye_size'].lower()}, {pred['predicted_nose_type'].lower()}, "
            f"{pred['predicted_lip_type'].lower()}, {pred['predicted_chin_strength'].lower()} chin, "
            f"and {pred['predicted_complexion']} complexion. "
            f"Most prominent feature: {pred['dominant_feature']}."
        ),
        "verification_tip": (
            "Compare with a clear front-facing photo. Accurate matches confirm chart precision; "
            "major mismatches may indicate birth-time inaccuracy worth rectifying."
        ),
    }


def lookup_feature(feature_type, feature_name):
    """Lookup interpretation of any face feature."""
    DB = {
        "forehead": FOREHEAD,
        "eyes": EYES,
        "eyebrows": EYEBROWS,
        "nose": NOSE,
        "lips": LIPS,
        "chin": CHIN,
        "ears": EARS,
        "cheeks": CHEEKS,
        "face_shape": FACE_SHAPES,
    }
    section = DB.get(feature_type.lower())
    if not section:
        return f"Unknown feature_type. Available: {list(DB.keys())}"
    if feature_name and feature_name in section:
        return section[feature_name]
    return section


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    result = face_reading_summary(chart)
    print(f"=== FACE READING (chart-predicted) for {chart['name']} ===\n")
    for k, v in result.items():
        if k in ("interpretation", "verification_tip"): continue
        print(f"  {k}: {v}")
    print(f"\n  READING:")
    print(f"  {result['interpretation']}")
    print(f"\n  TIP: {result['verification_tip']}")
