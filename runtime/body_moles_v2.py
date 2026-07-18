"""Body Moles v2 — extended Tila Lakshana with rare positions, patterns, and divine references.

Builds on body_moles.py (v1: 55 positions catalogued).

v2 adds:
  - 35 MORE specific rare mole positions (palm finger pads, ear-back, eyelid sub-positions,
    inner forearm, wrist sides, belly-button radius, below-knee, vertebrae-aligned back)
  - MOLE PATTERNS: triangle-of-3, linear-arrangement, cluster — compound meanings
  - read_mole_combination(positions: list) → compound interpretation
  - Mythological / divine mole references (Lord Vishnu's Srivatsa, Lakshmi's mark,
    Shiva's third-eye drop, Hanuman's chest line, etc.)

Source: Sariraka Lakshana, Tila Lakshana, Hanuman Pratima Shastra, Tantric Body Codes,
Brihat Samhita Ch.65-67, Sanskrit Bhumi-grantha references on mythological body marks.
"""
import sys
sys.path.insert(0, ".")
from body_moles import (
    MOLE_POSITIONS, MOLE_COLORS, MOLE_SHAPES, GENDER_RULES,
    lookup_mole, list_all_positions, mole_summary,
)


# ============================================================
# 35 RARE / SPECIFIC MOLE POSITIONS (extending v1's 55)
# ============================================================
RARE_MOLE_POSITIONS = {
    # PALM FINGER PADS (rare, very specific)
    "Right palm — base of thumb (Venus mount)": {
        "general": "Strong romantic life, wealth from spouse or pleasure-related industries",
        "male": "Romantic success, multiple admirers, comforts in life",
        "female": "Beautiful, wealthy partner, blessed marriage",
    },
    "Right palm — base of index finger (Jupiter mount)": {
        "general": "Leadership, dharma, religious authority, teaching career",
        "male": "Government / advisory position",
        "female": "Married into respected family with high status",
    },
    "Right palm — base of middle finger (Saturn mount)": {
        "general": "Hard work, real-estate gains, possible setbacks before success",
        "male": "Self-made wealth through perseverance",
        "female": "Disciplined household manager",
    },
    "Right palm — base of ring finger (Sun mount)": {
        "general": "Fame, public recognition, artistic / political success",
        "male": "Public-figure career, possible writer/artist",
        "female": "Married to famous or recognized figure",
    },
    "Right palm — base of little finger (Mercury mount)": {
        "general": "Business acumen, communication-based wealth, quick mind",
        "male": "Trade, commerce, writing, broker / agent success",
        "female": "Business partner with husband, financial wisdom",
    },
    "Center of palm (Plain of Mars)": {
        "general": "Strategic mind, courage in middle life, possible military or athletic distinction",
    },
    "Right palm — Luna mount (outer edge)": {
        "general": "Foreign travel / settlement, intuition, possibly psychic ability",
        "male": "Career abroad or foreign-related",
        "female": "Marriage may take her abroad or to distant city",
    },
    "Left palm (any prominent position)": {
        "general": "Wealth-spending, generous, possibly philanthropic; left palm = giving hand",
    },

    # FINGERTIP PADS
    "Index finger pad (right)": {"general": "Leadership talent, often visible early in life"},
    "Middle finger pad (right)": {"general": "Patience-marker, late-blooming career"},
    "Ring finger pad (right)": {"general": "Artistic gift, fame potential"},
    "Little finger pad (right)": {"general": "Communication blessing, eloquence"},
    "Thumb tip (right)": {"general": "Strong willpower marker"},

    # EAR DETAILS
    "Behind right ear": {
        "general": "Hidden wisdom, secret knowledge, occult interest, often spiritual practitioner",
    },
    "Behind left ear": {
        "general": "Hidden burdens, keeping secrets for family / spouse",
    },
    "Inside right ear (visible only when ear pulled)": {
        "general": "Auspicious longevity marker, wisdom-receptive",
    },
    "Earlobe (any)": {
        "general": "Long life, hearing-related blessings, ability to receive teachings",
    },

    # EYE DETAILS — eyelid sub-positions
    "Upper eyelid (right)": {"general": "Romantic insights, possibly dreamer-poet"},
    "Upper eyelid (left)": {"general": "Emotional sensitivity, possible eye-related health"},
    "Lower eyelid (right)": {"general": "Tear-marker — emotional / loss in life"},
    "Lower eyelid (left)": {"general": "Past sadness affecting present; needs healing"},
    "Corner of eye (outer, right)": {"general": "Romantic affairs / temptations in life"},

    # FOREARM
    "Inner right forearm": {
        "general": "Self-effort wealth — earned through your own labor, not inherited",
    },
    "Inner left forearm": {
        "general": "Spending hand — generous, may need to budget consciously",
    },
    "Outer right forearm": {
        "general": "Public face of work — visible profession, possibly recognized for craft",
    },
    "Outer left forearm": {
        "general": "Hidden talents, may have second career or hobby with depth",
    },

    # WRIST DETAILS
    "Top of right wrist": {"general": "Career visible in middle life, often promotion-marker"},
    "Bottom of right wrist (palm side)": {"general": "Hidden wealth, secret savings, possibly inheritance"},
    "Top of left wrist": {"general": "Spouse's career affecting yours"},
    "Side of wrist (between thumb-side and pinky-side)": {"general": "Mid-life pivots / changes in profession"},

    # BELLY BUTTON RADIUS (within 2 cm)
    "Just above navel (1-2 cm)": {
        "general": "Strong digestion, food-related career or pleasures, comforts in middle age",
    },
    "Just below navel (1-2 cm)": {
        "general": "Sexual / fertility blessing; possibly large family or dynamic love life",
    },
    "Right of navel (1-2 cm)": {"general": "Wealth flow, prosperity in middle years"},
    "Left of navel (1-2 cm)": {"general": "Family-burden marker, may carry care-taking duties"},

    # KNEE / LEG DETAILS
    "Just below right knee": {"general": "Stability in mid-life, foundation-building career"},
    "Just below left knee": {"general": "Slow but steady progress, may face joint issues old age"},
    "Inside thigh, near knee (right)": {"general": "Romantic intensity, sensual nature"},
    "Inside thigh, near knee (left)": {"general": "Hidden sensual life, possibly clandestine"},

    # SPINAL / VERTEBRAE-ALIGNED BACK
    "Mid-spine (between shoulder blades)": {
        "general": "Strong spinal energy (kundalini-prone), spiritual potential, leadership-bearer",
    },
    "Lower spine (lumbar area)": {
        "general": "Sexual energy strong, possible kidney/lower-back issues",
    },
    "Right of spine (any vertebra-level)": {
        "general": "Active 'masculine channel' (Pingala) — solar energy strong",
    },
    "Left of spine (any vertebra-level)": {
        "general": "Active 'feminine channel' (Ida) — lunar energy strong",
    },

    # MISC RARE
    "Inside the mouth (cheek)": {
        "general": "Secret wealth marker (very rare); also possible speech-related fame",
    },
    "Underside of foot (sole — center)": {
        "general": "Royal-class marker — Padmaja-class blessing, foreign travel + elevation",
    },
    "Top of foot (right)": {"general": "Visible travel destiny, journey-defined life"},
    "Top of foot (left)": {"general": "Spiritual travel, pilgrimage destiny"},
    "Heel": {"general": "Late-life relocation, possible foreign settlement after middle age"},
}


# ============================================================
# MOLE PATTERNS — multiple moles forming shapes
# ============================================================
MOLE_PATTERNS = {
    "Triangle of 3 moles (head/face area)": {
        "meaning": "Strong wisdom-yoga; classical 'Trishula' marker — Shiva-related blessing",
        "indication": "Spiritual leadership, often gurus / teachers / advisors",
        "rarity": "rare",
    },
    "Triangle of 3 moles (chest area)": {
        "meaning": "Auspicious — 'Lakshmi yantra' formation; wealth flows naturally",
        "indication": "Material + spiritual prosperity, blessed marriage",
        "rarity": "very rare",
    },
    "Triangle of 3 moles (belly / navel area)": {
        "meaning": "Strong fertility + family yoga; ancestor-blessing marker",
        "indication": "Multiple progeny, family-centered prosperity",
        "rarity": "very rare",
    },
    "Triangle of 3 moles (back / shoulders)": {
        "meaning": "Burden-bearer who finds glory through service; karmic-strength yoga",
        "indication": "Those who carry family / community on their shoulders, recognized late",
        "rarity": "rare",
    },
    "Linear arrangement of 3+ moles (vertical, on body)": {
        "meaning": "Career-direction marker — straight path destiny",
        "indication": "Clear life-purpose, focused single profession across life",
    },
    "Linear arrangement (horizontal)": {
        "meaning": "Multiple parallel pursuits, lateral thinking, branching life",
        "indication": "Diverse career, side-hustles, multi-talented",
    },
    "Cluster (3+ moles within small area)": {
        "meaning": "Wealth concentration in specific life-domain (per location)",
        "indication": "Blessing focused on the body-area's significance — chest=love, belly=wealth, back=service",
    },
    "Cross / X formation (4 moles)": {
        "meaning": "Karmic crossroads, must choose between 2 paths in life",
        "indication": "Often signifies a major decision point in middle age",
        "rarity": "very rare",
    },
    "Square (4 moles in square arrangement)": {
        "meaning": "Protection-yantra — divine protection in that body-region",
        "indication": "Survives major dangers in that life-area; classical 'rakshana' mark",
        "rarity": "very rare",
    },
    "Star (5+ moles in radial pattern)": {
        "meaning": "Highest auspicious pattern; yoga of fame + recognition + divine grace",
        "indication": "Saintly potential, public recognition, blessing of Sri (auspicious goddess)",
        "rarity": "extremely rare",
    },
    "Crescent / arc (curved line of moles)": {
        "meaning": "Lunar / Soma-related blessing; receptive intuitive nature",
        "indication": "Strong feminine intuition, mystical inclination",
    },
    "Circle / ring (multiple moles forming closed loop)": {
        "meaning": "Sealed karma — completion of major life-cycle",
        "indication": "Karma resolution, often in mid-life; possible spiritual realization",
        "rarity": "extremely rare",
    },
    "Two parallel lines of moles": {
        "meaning": "Twin-path destiny — often dual career or marital + spiritual life",
        "indication": "Balance between worldly and otherworldly",
    },
}


# ============================================================
# MYTHOLOGICAL / DIVINE MOLE REFERENCES
# ============================================================
DIVINE_MOLE_REFERENCES = {
    "Srivatsa (chest center)": {
        "deity": "Lord Vishnu",
        "description": "Curl of hair / lotus-shape mark on chest center, slightly to right of sternum",
        "significance": "Highest auspicious mark — 'Lakshmi-vasa' (Lakshmi's residence). Wealth, fame, divine protection",
        "rarity": "Said to be born once in millions; classical mark of avatars and great souls",
    },
    "Padmavati / Lotus mark": {
        "deity": "Goddess Lakshmi",
        "description": "Lotus-petal-shaped pattern on palm, sole, or chest",
        "significance": "Wealth + beauty + grace combined. Particularly auspicious for women — marriage to king-class person",
    },
    "Trishula / Trident on forehead or hand": {
        "deity": "Lord Shiva",
        "description": "Three vertical lines or 3-mole triangle on forehead or palm",
        "significance": "Spiritual authority, ascetic potential, strong tapasya power",
    },
    "Chakra (wheel) on palm": {
        "deity": "Lord Vishnu / Sudarshana",
        "description": "Circular pattern with internal radial lines on palm",
        "significance": "Royal status marker — classical sign of king or emperor in scriptures",
    },
    "Hanuman chest-line": {
        "deity": "Lord Hanuman",
        "description": "Single vertical line / mole-streak down center of chest",
        "significance": "Devotional intensity, courage, service to higher cause; classical bhakta marker",
    },
    "Shiva's third-eye drop": {
        "deity": "Lord Shiva",
        "description": "Mole between eyebrows (bindu position)",
        "significance": "Inner sight, intuition, possibly clairvoyance; meditation-natural",
    },
    "Lakshmi's foot-mark": {
        "deity": "Goddess Lakshmi",
        "description": "Mole on right sole, especially center or near big toe",
        "significance": "Wealth follows you — 'Lakshmi treads where you walk'. Prosperity-attractor",
    },
    "Saraswati's tongue-mark": {
        "deity": "Goddess Saraswati",
        "description": "Mole on tongue (especially center or tip)",
        "significance": "Eloquence, wisdom, words-have-power; classical orator/scholar marker",
    },
    "Ganesha's curl (forehead-side)": {
        "deity": "Lord Ganesha",
        "description": "Curved mole / curl pattern on forehead corner",
        "significance": "Obstacle-removing energy, success in undertakings",
    },
    "Vishnu's foot-mark": {
        "deity": "Lord Vishnu",
        "description": "Three-pointed mark on right sole (representing Vishnu's stride)",
        "significance": "Travel-destiny + dharmic protection; 'protected wanderer'",
    },
    "Krishna's flute-mark": {
        "deity": "Lord Krishna",
        "description": "Long horizontal mole or scar on right palm or chest",
        "significance": "Charm, charisma, attract devotees / followers / lovers; performer-marker",
    },
    "Durga's protection mark": {
        "deity": "Goddess Durga",
        "description": "Mole on left shoulder or upper back",
        "significance": "Protection against enemies, victory in struggles, warrior-blessing",
    },
}


# ============================================================
# COMBINED INTERPRETATION ENGINE
# ============================================================
def read_mole_combination(positions: list, color="Black", gender="any"):
    """Read compound meaning from a LIST of mole positions on a single body.

    Args:
        positions: list of position-name strings (matching v1 + v2 catalogs)
        color: dominant color of moles
        gender: 'male', 'female', or 'any'

    Returns:
        dict with individual readings + pattern detection + compound interpretation.
    """
    individual_readings = []
    matched_positions = []

    for p in positions:
        # Try v1 first
        if p in MOLE_POSITIONS:
            individual_readings.append({
                "position": p,
                "reading": lookup_mole(p, color=color, gender=gender),
                "source": "v1",
            })
            matched_positions.append(p)
            continue
        # Try v2 rare positions
        if p in RARE_MOLE_POSITIONS:
            data = RARE_MOLE_POSITIONS[p]
            base = data.get("general", "")
            if gender.lower() == "male" and "male" in data:
                base += " " + data["male"]
            elif gender.lower() == "female" and "female" in data:
                base += " " + data["female"]
            individual_readings.append({
                "position": p,
                "reading": {"general_meaning": data.get("general", ""), "summary": base},
                "source": "v2_rare",
            })
            matched_positions.append(p)
            continue
        # Fuzzy match
        found = False
        for k in {**MOLE_POSITIONS, **RARE_MOLE_POSITIONS}:
            if p.lower() in k.lower() or k.lower() in p.lower():
                individual_readings.append({
                    "position": k,
                    "reading": "Fuzzy-matched: " + str(MOLE_POSITIONS.get(k) or RARE_MOLE_POSITIONS.get(k, "?")),
                    "source": "fuzzy",
                })
                matched_positions.append(k)
                found = True
                break
        if not found:
            individual_readings.append({
                "position": p,
                "reading": "Position not in catalog (try fuzzy variants)",
                "source": "unmatched",
            })

    # Pattern detection
    patterns_detected = []

    # Same-region cluster
    head_face_count = sum(1 for p in matched_positions
                          if any(w in p.lower() for w in ["head","forehead","brow","eye","cheek","nose","lip","chin","ear"]))
    chest_count = sum(1 for p in matched_positions if "chest" in p.lower() or "breast" in p.lower())
    belly_count = sum(1 for p in matched_positions if any(w in p.lower() for w in ["belly","stomach","navel"]))
    back_count = sum(1 for p in matched_positions if "back" in p.lower() or "spine" in p.lower())
    palm_count = sum(1 for p in matched_positions if "palm" in p.lower() or "mount" in p.lower())

    if head_face_count >= 3:
        patterns_detected.append("Head/face cluster — wisdom + leadership concentration")
    if chest_count >= 3:
        patterns_detected.append("Chest cluster — heart-yoga (love/devotion concentration); possible Lakshmi/Vishnu blessing")
    if belly_count >= 3:
        patterns_detected.append("Belly cluster — wealth/fertility concentration")
    if back_count >= 3:
        patterns_detected.append("Back cluster — burden-bearer with karmic glory")
    if palm_count >= 3:
        patterns_detected.append("Palm cluster — destiny visible in hand; consult palmistry deeply")

    # Bilateral asymmetry
    right_count = sum(1 for p in matched_positions if "right" in p.lower())
    left_count = sum(1 for p in matched_positions if "left" in p.lower())
    if right_count >= 3 * max(1, left_count):
        patterns_detected.append("Right-side dominant — masculine/active karma (auspicious for males)")
    elif left_count >= 3 * max(1, right_count):
        patterns_detected.append("Left-side dominant — feminine/receptive karma (auspicious for females)")

    # Triangle / linear / cluster checks (positional heuristics)
    if 3 <= len(matched_positions) <= 4 and chest_count == len(matched_positions):
        patterns_detected.append("Possible Triangle on chest — Lakshmi yantra; classical wealth-marker")
    if len(matched_positions) >= 5:
        patterns_detected.append("Multi-mole composition — strong karmic stamp; consult full pattern catalog")

    # Compound interpretation
    compound = []
    if head_face_count >= 1 and palm_count >= 1:
        compound.append("Wisdom + destiny visible in hand — potential teacher/advisor")
    if chest_count >= 1 and belly_count >= 1:
        compound.append("Love + wealth balance — comfortable family life")
    if back_count >= 1 and any("foot" in p.lower() for p in matched_positions):
        compound.append("Service-life with travel — possibly missionary or service-traveler destiny")

    return {
        "input_positions": positions,
        "matched_count": len(matched_positions),
        "unmatched_count": len(positions) - len(matched_positions),
        "individual_readings": individual_readings,
        "patterns_detected": patterns_detected,
        "compound_interpretation": compound or ["Each mole reading stands individually; no compound pattern detected"],
        "notes": (
            "Combine with chart cross-validation: a mole's meaning aligns with the "
            "house/planet symbolism it falls under. Strong matches confirm karmic stamp; "
            "mismatches suggest chart-rectification or alternative life-path."
        ),
    }


def lookup_divine_mark(name):
    """Lookup a mythological / divine mole reference."""
    return DIVINE_MOLE_REFERENCES.get(name)


def list_all_v2_positions():
    """List rare-position categories."""
    return {
        "Palm — Mounts / Pads": [k for k in RARE_MOLE_POSITIONS if "palm" in k.lower() or "mount" in k.lower()],
        "Fingertips": [k for k in RARE_MOLE_POSITIONS if "finger" in k.lower() or "thumb" in k.lower()],
        "Ears (rare)": [k for k in RARE_MOLE_POSITIONS if "ear" in k.lower()],
        "Eyes (sub-positions)": [k for k in RARE_MOLE_POSITIONS if "eye" in k.lower()],
        "Forearm / Wrist (rare)": [k for k in RARE_MOLE_POSITIONS if "forearm" in k.lower() or "wrist" in k.lower()],
        "Belly-button radius": [k for k in RARE_MOLE_POSITIONS if "navel" in k.lower()],
        "Knee / Lower-leg (rare)": [k for k in RARE_MOLE_POSITIONS if "knee" in k.lower() or "thigh" in k.lower()],
        "Spinal alignment": [k for k in RARE_MOLE_POSITIONS if "spine" in k.lower()],
        "Foot details": [k for k in RARE_MOLE_POSITIONS if "foot" in k.lower() or "heel" in k.lower() or "sole" in k.lower()],
        "Misc rare": [k for k in RARE_MOLE_POSITIONS if "mouth" in k.lower()],
    }


def mole_summary_v2():
    """Combined v1 + v2 summary."""
    v1 = mole_summary()
    return {
        "v1_positions": v1["total_positions_catalogued"],
        "v2_rare_positions": len(RARE_MOLE_POSITIONS),
        "total_positions": v1["total_positions_catalogued"] + len(RARE_MOLE_POSITIONS),
        "mole_patterns_catalogued": len(MOLE_PATTERNS),
        "divine_references": len(DIVINE_MOLE_REFERENCES),
        "v2_categorized_positions": list_all_v2_positions(),
        "interpretation_layers": v1["interpretation_layers"] + [
            "7. Pattern formation (triangle/linear/cluster/star) — strong amplification",
            "8. Mythological match (Srivatsa, Trishula, etc.) — divine-class blessing",
            "9. Multi-mole compound interpretation via read_mole_combination()",
        ],
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("=== TILA LAKSHANA v2 (Body Mole Reading — Extended) ===\n")
    summary = mole_summary_v2()
    print(f"  v1 positions:  {summary['v1_positions']}")
    print(f"  v2 rare positions: {summary['v2_rare_positions']}")
    print(f"  TOTAL positions: {summary['total_positions']}")
    print(f"  Mole patterns: {summary['mole_patterns_catalogued']}")
    print(f"  Divine references: {summary['divine_references']}")

    print("\n  --- v2 Rare Position Categories ---")
    for cat, positions in summary["v2_categorized_positions"].items():
        print(f"\n  {cat}: {len(positions)}")
        for p in positions[:3]:
            print(f"    • {p}")

    print("\n=== EXAMPLE: read_mole_combination ===")
    sample = [
        "Right cheek",
        "Right palm — base of thumb (Venus mount)",
        "Just above navel (1-2 cm)",
        "Mid-spine (between shoulder blades)",
    ]
    result = read_mole_combination(sample, color="Red / Honey", gender="male")
    print(f"  Input ({len(sample)} positions):")
    for p in sample:
        print(f"    • {p}")
    print(f"\n  Matched: {result['matched_count']}/{len(sample)}")
    print(f"\n  Patterns detected ({len(result['patterns_detected'])}):")
    for pat in result["patterns_detected"]:
        print(f"    • {pat}")
    print(f"\n  Compound interpretation:")
    for c in result["compound_interpretation"]:
        print(f"    • {c}")

    print("\n=== EXAMPLE: divine reference lookup ===")
    div = lookup_divine_mark("Srivatsa (chest center)")
    if div:
        print(f"  Deity: {div['deity']}")
        print(f"  Description: {div['description']}")
        print(f"  Significance: {div['significance']}")
        print(f"  Rarity: {div.get('rarity', 'standard')}")
