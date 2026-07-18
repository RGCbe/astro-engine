"""Body Moles (Tila Lakshana / Kalanka Shastra) — classical Indian mole reading.

Source: Sariraka Lakshana (Sanskrit), Tila Lakshana texts, Hindu astro-physiognomy.

Each mole's position, color, shape, and side (left vs right) carries specific meaning.
Right side = better for males; Left side = better for females.
Red/honey-color > black > white in auspiciousness.
"""
import sys
sys.path.insert(0, ".")

# ============================================================
# MOLE POSITION → MEANING (~50 specific positions)
# ============================================================
MOLE_POSITIONS = {
    # HEAD AREA
    "Crown of head (top)": {
        "general": "Spiritual elevation, fame, divine grace",
        "male": "Wealth, leadership, recognition",
        "female": "Marriage to influential family",
    },
    "Forehead (center)": {
        "general": "Wealth, intelligence, royal traits — most auspicious facial mole",
        "male": "Strong career advancement, recognition",
        "female": "Marriage to wealthy/respected family, comforts",
    },
    "Forehead right side": {
        "general": "Quick success, possibly unexpected fortune",
        "male": "Career rise, possibly govt/official position",
        "female": "Influential husband, social respect",
    },
    "Forehead left side": {
        "general": "Mixed luck, struggles before success",
        "male": "Slow career, must work hard for recognition",
        "female": "Family support but partner may have own challenges",
    },
    "Right eyebrow": {
        "general": "Auspicious — wealth, beauty, charm",
        "male": "Romantic success, multiple admirers possible",
        "female": "Beautiful, attracts wealthy partner",
    },
    "Left eyebrow": {
        "general": "Mixed — must control anger",
        "male": "Hot-headed but capable, military/sports affinity",
        "female": "Sharp tongue, may face marital arguments",
    },
    "Eyelids": {
        "general": "Romantic, sensitive, possibly emotional health concerns",
    },
    "Right cheek": {
        "general": "Auspicious — wealth, comfort, recognition",
        "male": "Strong financial line, good food and clothing",
        "female": "Marriage brings comforts, prosperous in-laws",
    },
    "Left cheek": {
        "general": "Mixed — fame possible but with controversies",
        "male": "Reputation may have ups and downs",
        "female": "Social attention but possibly gossip-prone",
    },
    "Right side of nose": {
        "general": "Wealth, business success",
        "male": "Trade/commerce success, real estate gains",
        "female": "Prosperous through business or husband's wealth",
    },
    "Left side of nose": {
        "general": "Possibly afflicted finances, watch spending",
        "male": "Income unstable, multiple sources but volatile",
        "female": "Financial caution needed in spousal matters",
    },
    "Tip of nose": {
        "general": "Vanity, may face public criticism, but charisma",
        "male": "Strong willpower, leadership, but pride issues",
        "female": "Beauty admired but romantic disappointments possible",
    },
    "Lower lip (below)": {
        "general": "Speech-related fame or controversy",
        "male": "Eloquent speaker, may earn through words",
        "female": "Charming speech, persuasive in social settings",
    },
    "Upper lip": {
        "general": "Sensual, romantic, speech can heal or wound",
        "male": "Charm with women, multiple romantic episodes",
        "female": "Loving, attracts attention",
    },
    "Chin": {
        "general": "Determination, wealth in later life, possible status",
        "male": "Authoritative position in old age",
        "female": "Comfortable later life, respected by family",
    },
    "Below chin (jaw)": {
        "general": "Strong willpower, possible legal troubles in life",
    },

    # NECK + SHOULDERS
    "Neck (front)": {
        "general": "Wealth, comforts, possibly throat-related issues to watch",
        "male": "Income through speech/voice/communication",
        "female": "Wealth flows through marriage or family",
    },
    "Neck (back)": {
        "general": "Hard worker, may face spinal issues",
        "male": "Career through manual or labor-intensive work",
        "female": "Burden of family responsibilities",
    },
    "Right shoulder": {
        "general": "Wisdom, leadership, ability to bear responsibility",
    },
    "Left shoulder": {
        "general": "Burden bearer, may sacrifice for family",
    },

    # CHEST AREA
    "Chest (right side, near heart)": {
        "general": "Generous heart, romantic, beloved by many",
        "male": "Charismatic, multiple admirers",
        "female": "Loving partner, blessed with children",
    },
    "Chest (left side)": {
        "general": "Mixed — emotional intensity, possibly heart-related concerns",
        "male": "Romantic but possibly heartbreaks",
        "female": "Emotional volatility in relationships",
    },
    "Chest (center, between)": {
        "general": "Balanced love life, devotional inclination, possibly poetic",
    },
    "Right breast / nipple area": {
        "general": "Auspicious — children, especially sons",
        "female": "First child possibly male, blessed maternity",
    },
    "Left breast / nipple area": {
        "general": "Mixed — possibly daughters, child-care emphasis",
        "female": "Maternal challenges or blessings depending on chart",
    },

    # ABDOMEN
    "Stomach / belly center": {
        "general": "Food-loving, prosperous, comfort-oriented",
        "male": "Wealth, may struggle with weight",
        "female": "Fertility, family-centered",
    },
    "Right side of belly": {
        "general": "Strong digestion, vitality, wealth indicator",
    },
    "Left side of belly": {
        "general": "Possible digestive issues, moderate spending wisdom",
    },
    "Navel (around)": {
        "general": "Karmic mole — past-life carry-over, spiritual marker",
        "male": "Wealth in mid-life, possible spiritual awakening",
        "female": "Strong maternal instinct, possible childbearing blessings",
    },

    # BACK
    "Upper back (right)": {
        "general": "Auspicious — bears responsibilities well, leadership",
    },
    "Upper back (left)": {
        "general": "Hardworker, may face career setbacks",
    },
    "Lower back": {
        "general": "Sensual, possibly fertility-related, watch kidney health",
    },
    "Spine (any vertical line)": {
        "general": "Strong constitution, longevity",
    },

    # ARMS
    "Right arm (above elbow)": {
        "general": "Inherited wealth, family support, success in tradition",
    },
    "Left arm (above elbow)": {
        "general": "Self-made career, possibly hard struggle",
    },
    "Right hand (palm)": {
        "general": "Wealth-attracting, generous earnings (mole on right palm = fortune)",
    },
    "Left hand (palm)": {
        "general": "Wealth-spending, possibly philanthropic, may not retain wealth",
    },
    "Right wrist": {
        "general": "Mid-life success, especially in business",
    },
    "Left wrist": {
        "general": "Mid-life challenges or transitions",
    },
    "Fingers": {
        "general": "Skilled work, craftsmanship, artistic talent",
    },

    # PRIVATE / GENITAL
    "Right thigh (inner)": {
        "general": "Strong sexual nature, multiple romantic experiences",
    },
    "Left thigh (inner)": {
        "general": "Sensual but possibly secretive in romance",
    },
    "Genital area": {
        "general": "Strong sexual appetite, possibly multiple partnerships in life",
        "warning": "Watch for marital fidelity issues",
    },
    "Buttock (right)": {
        "general": "Wealth in old age, comfortable life",
    },
    "Buttock (left)": {
        "general": "Hard work for wealth, may face setbacks",
    },

    # LEGS
    "Right knee": {
        "general": "Career stability, possibly knee issues in old age",
    },
    "Left knee": {
        "general": "Career fluctuations, watch joint health",
    },
    "Right calf": {
        "general": "Travel-prone, foreign connections, success abroad",
    },
    "Left calf": {
        "general": "Domestic-focused, slow but steady progress",
    },
    "Right ankle": {
        "general": "Long-distance travel or settlement abroad",
    },
    "Left ankle": {
        "general": "Travel-related challenges, possible accidents",
    },
    "Right foot sole": {
        "general": "Wealth from travel, foreign income",
    },
    "Left foot sole": {
        "general": "Travel for spiritual/religious purposes",
    },
    "Toes": {
        "general": "Restless nature, much movement in life",
    },

    # TONGUE / MOUTH (rare)
    "Tongue": {
        "general": "Sharp speech, possibly fame as orator/writer; dual-edged blessing",
    },
}

# ============================================================
# COLOR INTERPRETATION (modifies position meaning)
# ============================================================
MOLE_COLORS = {
    "Red / Honey": {
        "auspiciousness": "Most auspicious — strong positive amplification of position-meaning",
        "indication": "Past-life merit, strong vitality, positive karma activated",
    },
    "Black": {
        "auspiciousness": "Standard — preserves position-meaning",
        "indication": "Karmic mark, neither bonus nor curse; reflects native's actions",
    },
    "Brown": {
        "auspiciousness": "Mild auspiciousness",
        "indication": "Earthly results, manifests through effort",
    },
    "White / Pale": {
        "auspiciousness": "Inauspicious — weakens/reverses position-meaning",
        "indication": "Spiritual sign in some traditions, but generally caution-marker",
    },
    "Multi-color / Spotted": {
        "auspiciousness": "Mixed — variable results",
        "indication": "Complex life-events tied to position-house",
    },
}

# ============================================================
# SHAPE & SIZE
# ============================================================
MOLE_SHAPES = {
    "Round / circular": "Smooth karmic flow, gentle results",
    "Oval / elongated": "Extended impact, long-lasting effects",
    "Irregular / star-shape": "Sudden events, unusual life-twists",
    "Triangle (3 corners)": "Strong fortune (especially upward-pointing) OR strong challenges (downward-pointing)",
    "Hair growing on mole": "Extra-strong amplification of meaning (rare, very significant)",
    "Raised / convex": "Active manifestation, events visible",
    "Flat": "Latent influence, may not always activate",
    "Large (>5mm)": "Dominant life-theme",
    "Small (<2mm)": "Minor influence, side-themes",
}

# ============================================================
# GENDER RULES
# ============================================================
GENDER_RULES = {
    "Right side moles": "Auspicious for MALES, less so for females",
    "Left side moles": "Auspicious for FEMALES, less so for males",
    "Center (chest/forehead/etc)": "Equally auspicious for both genders",
    "Hidden moles (covered by clothing)": "Generally MORE auspicious — hidden destiny, secret wealth",
    "Visible moles": "Public destiny, fame/notoriety depending on position",
}


def lookup_mole(position, color="Black", side=None, shape="Round", gender="any"):
    """Lookup mole interpretation."""
    pos_data = MOLE_POSITIONS.get(position)
    if not pos_data:
        # Try fuzzy match
        for k in MOLE_POSITIONS:
            if position.lower() in k.lower():
                pos_data = MOLE_POSITIONS[k]
                position = k
                break

    if not pos_data:
        return f"Position not in classical catalog. Try: {list(MOLE_POSITIONS.keys())[:10]}..."

    color_data = MOLE_COLORS.get(color, MOLE_COLORS["Black"])
    shape_data = MOLE_SHAPES.get(shape, "Standard")

    base = pos_data.get("general", "")
    if gender.lower() == "male" and "male" in pos_data:
        base += " " + pos_data["male"]
    elif gender.lower() == "female" and "female" in pos_data:
        base += " " + pos_data["female"]

    return {
        "position": position,
        "general_meaning": pos_data.get("general", ""),
        "gendered_meaning": pos_data.get(gender.lower()) if gender.lower() in ["male", "female"] else None,
        "warning": pos_data.get("warning"),
        "color_modifier": color_data["auspiciousness"] + " — " + color_data["indication"],
        "shape_modifier": shape_data,
        "summary": (
            f"{base} "
            f"Color ({color}): {color_data['auspiciousness']}. "
            f"Shape ({shape}): {shape_data}."
        ),
    }


def list_all_positions():
    """Return categorized list of all 50+ classical mole positions."""
    return {
        "Head & Face": [k for k in MOLE_POSITIONS if any(w in k for w in ["head","Forehead","brow","Eye","cheek","nose","lip","Chin","jaw"])],
        "Neck & Shoulders": [k for k in MOLE_POSITIONS if any(w in k for w in ["Neck","shoulder"])],
        "Chest": [k for k in MOLE_POSITIONS if any(w in k for w in ["Chest","breast"])],
        "Abdomen": [k for k in MOLE_POSITIONS if any(w in k for w in ["belly","Stomach","Navel"])],
        "Back": [k for k in MOLE_POSITIONS if any(w in k for w in ["back","Spine"])],
        "Arms & Hands": [k for k in MOLE_POSITIONS if any(w in k for w in ["arm","hand","wrist","Finger"])],
        "Private/Pelvic": [k for k in MOLE_POSITIONS if any(w in k for w in ["thigh","Genital","Buttock"])],
        "Legs & Feet": [k for k in MOLE_POSITIONS if any(w in k for w in ["knee","calf","ankle","foot","Toes"])],
        "Other": [k for k in MOLE_POSITIONS if "Tongue" in k],
    }


def mole_summary():
    """Return classical knowledge framework."""
    return {
        "total_positions_catalogued": len(MOLE_POSITIONS),
        "color_categories": len(MOLE_COLORS),
        "shape_categories": len(MOLE_SHAPES),
        "categorized_positions": list_all_positions(),
        "interpretation_layers": [
            "1. Position (gives base theme — wealth/health/marriage/career/etc.)",
            "2. Color (red/honey amplifies; white reverses)",
            "3. Shape (round=smooth, irregular=sudden events)",
            "4. Side (right=auspicious for males, left=for females)",
            "5. Visibility (hidden=secret destiny, visible=public destiny)",
            "6. Hair-on-mole = extra-strong amplification",
        ],
        "usage": "Call lookup_mole(position, color, shape, gender) for specific interpretation",
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== TILA LAKSHANA (Body Mole Reading) ===\n")
    summary = mole_summary()
    print(f"  Positions catalogued: {summary['total_positions_catalogued']}")
    print(f"  Color categories: {summary['color_categories']}")
    print(f"  Shape categories: {summary['shape_categories']}")

    print("\n  --- Categorized positions ---")
    for cat, positions in summary["categorized_positions"].items():
        print(f"\n  {cat}: {len(positions)}")
        for p in positions[:5]:
            print(f"    • {p}")

    print("\n=== EXAMPLE LOOKUP: Mole on right cheek, red color ===")
    result = lookup_mole("Right cheek", color="Red / Honey", gender="male")
    print(f"  General: {result['general_meaning']}")
    print(f"  Male: {result.get('gendered_meaning','')}")
    print(f"  Color modifier: {result['color_modifier']}")
    print(f"\n  SUMMARY: {result['summary']}")
