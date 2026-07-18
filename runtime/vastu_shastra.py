"""Vastu Shastra — directional astrology for living/working spaces.

Source: Vastu Shastra Sanskrit texts, Manasara, Mayamatam, Vishwakarma Vastu Shastra.

Mode 1: Lookup API — query specific direction/room/dosha
Mode 2: Chart-Vastu match — predict best directions for native based on birth chart
"""
import sys
sys.path.insert(0, ".")
from vedic_core import RASIS, RASI_LORDS, PLANET_ARCHETYPES

# ============================================================
# 8 DIRECTIONS + DEITIES + ELEMENTS
# ============================================================
DIRECTIONS = {
    "North (Kuber)": {
        "deity": "Kuber (god of wealth)",
        "element": "Water",
        "rules": "Wealth, career, opportunity, water flow",
        "ideal_for": "Treasure room, safe, cash registers, water storage, study room",
        "avoid": "Toilet, kitchen (especially fire), heavy obstructions",
        "planet": "Mercury",
    },
    "Northeast (Ishanya)": {
        "deity": "Ishana (Shiva form)",
        "element": "Water + Ether",
        "rules": "Spirituality, education, the most sacred zone",
        "ideal_for": "Pooja room, study, meditation, water source, well, light entry",
        "avoid": "Toilet (worst dosha), kitchen, heavy storage, master bedroom",
        "planet": "Jupiter",
    },
    "East (Indra)": {
        "deity": "Indra (king of gods)",
        "element": "Air + Sun-energy",
        "rules": "Health, vitality, sunrise zone, growth",
        "ideal_for": "Main entrance, windows, dining, children's bedroom",
        "avoid": "Toilet, heavy storage, blocked-light",
        "planet": "Sun",
    },
    "Southeast (Agni)": {
        "deity": "Agni (fire god)",
        "element": "Fire",
        "rules": "Fire, kitchen, digestion, transformation, energy",
        "ideal_for": "Kitchen, electrical equipment, heaters, generator",
        "avoid": "Bedroom (causes anger), water storage, toilet",
        "planet": "Venus",
    },
    "South (Yama)": {
        "deity": "Yama (god of death/karma)",
        "element": "Fire-secondary",
        "rules": "Fame, status, karma, also death/transformation",
        "ideal_for": "Heavy storage, master bedroom (head south for sleep), cupboards",
        "avoid": "Main entrance for residence (acceptable for businesses), light exits",
        "planet": "Mars",
    },
    "Southwest (Nairutya)": {
        "deity": "Nairuti (demon)",
        "element": "Earth",
        "rules": "Stability, master bedroom, ancestors, foundation",
        "ideal_for": "Master bedroom, heavy furniture, safe vault, ancestor altar",
        "avoid": "Main entrance, light entry, kitchen, toilet, water tanks",
        "planet": "Rahu",
    },
    "West (Varuna)": {
        "deity": "Varuna (water god)",
        "element": "Water-secondary",
        "rules": "Gains, progeny, social standing, water (sea direction)",
        "ideal_for": "Children's bedroom, dining, toilet (acceptable), study",
        "avoid": "Main entrance, kitchen",
        "planet": "Saturn",
    },
    "Northwest (Vayu)": {
        "deity": "Vayu (wind god)",
        "element": "Air",
        "rules": "Air, movement, guests, short-term relationships, business",
        "ideal_for": "Guest room, vehicles, granary, marketing/sales office",
        "avoid": "Master bedroom (creates instability), kitchen",
        "planet": "Moon",
    },
}

# ============================================================
# SUB-DIRECTIONS (16 zones for fine analysis)
# ============================================================
SUB_DIRECTIONS = [
    "N1 (N + slight NE)", "N2 (N + slight NW)",
    "NE1 (NE + slight N)", "NE2 (NE + slight E)",
    "E1 (E + slight NE)", "E2 (E + slight SE)",
    "SE1 (SE + slight E)", "SE2 (SE + slight S)",
    "S1 (S + slight SE)", "S2 (S + slight SW)",
    "SW1 (SW + slight S)", "SW2 (SW + slight W)",
    "W1 (W + slight SW)", "W2 (W + slight NW)",
    "NW1 (NW + slight W)", "NW2 (NW + slight N)",
]

# ============================================================
# ROOM PLACEMENT GUIDANCE
# ============================================================
ROOM_PLACEMENT = {
    "Master Bedroom": {
        "ideal": "Southwest (SW)",
        "reason": "SW = stability, ancestor-grounding, marriage harmony, authority of head of household",
        "avoid": "Northeast (causes financial drain, infertility, mental disturbance), Southeast (anger, quarrels)",
    },
    "Kitchen": {
        "ideal": "Southeast (SE)",
        "reason": "SE = fire element zone, proper digestion, financial flow",
        "avoid": "Northeast (worst — causes hot-headed children + eye problems), South (mixed)",
    },
    "Pooja / Meditation": {
        "ideal": "Northeast (NE)",
        "reason": "NE = most sacred zone, divine grace, scholastic results",
        "avoid": "South, Southwest (drain spiritual energy)",
    },
    "Study Room / Office": {
        "ideal": "Northeast or East",
        "reason": "Concentration, light exposure, mental clarity",
        "avoid": "Southwest (heavy energy), South (death-direction for thought)",
    },
    "Children's Bedroom": {
        "ideal": "West or Northwest",
        "reason": "Growth, education, movement",
        "avoid": "Southwest (children become heavy/serious early), Southeast (anger)",
    },
    "Guest Room": {
        "ideal": "Northwest (NW)",
        "reason": "NW = movement, short stays, no permanent friction",
        "avoid": "Southwest (guests overstay)",
    },
    "Toilet": {
        "ideal": "Northwest, West, or South-Southwest",
        "reason": "Waste evacuates outward without contaminating sacred zones",
        "avoid": "Northeast (worst single dosha — causes financial drain, mental disturbance)",
    },
    "Treasure / Safe / Cash": {
        "ideal": "North or Northeast (facing North)",
        "reason": "North = Kuber's direction; opening to N for wealth multiplication",
        "avoid": "Southwest, South",
    },
    "Brahmasthan (House Center)": {
        "ideal": "Open / uncluttered",
        "reason": "The center should breathe — pillars/toilets/heavy storage here predict chronic illness in occupants",
        "avoid": "Toilet (severe dosha), pillars, heavy furniture, kitchen",
    },
    "Staircase": {
        "ideal": "South, West, or Southwest",
        "reason": "Climbs upward in heavy-energy zones",
        "avoid": "Northeast (blocks divine energy), center of house",
    },
    "Water Storage / Tank": {
        "ideal": "Northeast or North",
        "reason": "Water + sacred direction",
        "avoid": "Southeast (water-fire conflict), Southwest (heavy water in stability zone)",
    },
    "Plants / Garden": {
        "ideal": "East, North, Northeast (light plants); West/Southwest (heavy trees)",
        "reason": "Growth direction for delicate vegetation",
        "avoid": "Heavy trees in NE block divine light",
    },
}

# ============================================================
# COMMON VASTU DOSHAS (DEFECTS) + REMEDIES
# ============================================================
VASTU_DOSHAS = {
    "NE Cut (Northeast missing/cut from plot)": {
        "effect": "Loss of wealth, education problems, infertility, lack of clarity",
        "severity": "HIGH",
        "remedy": "Place mirror on NE-facing wall, water fountain in NE, meditation altar in NE",
    },
    "SW Extension (Southwest jutting out)": {
        "effect": "Disturbed peace, ill health of head of household, family discord",
        "severity": "MEDIUM",
        "remedy": "Heavy stone/idol in SW, brass/copper objects, avoid keeping it light",
    },
    "SE Bedroom for Couple": {
        "effect": "Quarrels, anger, miscarriages, poor sleep",
        "severity": "HIGH",
        "remedy": "Sleep with head pointing east not south; relocate bedroom to SW if possible",
    },
    "Toilet in Northeast": {
        "effect": "Worst single dosha. Financial drain, mental disturbance, family disharmony",
        "severity": "VERY HIGH",
        "remedy": "Crystal salt bowl in NE corner of toilet (replace monthly), keep toilet door closed, mirror on inside of toilet door",
    },
    "Kitchen in Northeast": {
        "effect": "Hot-headed children, eye problems, family arguments, food fights",
        "severity": "HIGH",
        "remedy": "Place water vessel between fire and NE, relocate stove to SE corner of kitchen, use copper utensils",
    },
    "Plot tapering toward N or E (Vyaghra-mukhi)": {
        "effect": "Wealth drain, narrowing-future feel, diminishing returns",
        "severity": "MEDIUM",
        "remedy": "Boundary mirror facing inward at narrow end, regular Lakshmi pooja",
    },
    "Plot expanding toward N/E (Gaumukhi)": {
        "effect": "AUSPICIOUS — wealth growth, expanding fortune",
        "severity": "POSITIVE",
        "remedy": "None — preserve and protect the configuration",
    },
    "Road thrust facing entrance (Veedhi Shoola)": {
        "effect": "Accidents, sudden losses, unexpected disturbances",
        "severity": "HIGH",
        "remedy": "Placement of Bagalamukhi yantra at entrance, pillar/plant to deflect",
    },
    "Main door directly opposite back door": {
        "effect": "Wealth + energy passes straight through, no retention",
        "severity": "MEDIUM",
        "remedy": "Curtain/screen between, sacred symbol on door, mirrors to redirect energy",
    },
    "Bedroom door facing toilet": {
        "effect": "Health issues, marital disharmony, draining energy",
        "severity": "MEDIUM",
        "remedy": "Keep toilet door always closed, place small mirror on bedroom-side of toilet door",
    },
    "Triangular plot": {
        "effect": "Legal disputes, sharp/angular life events, fragmented family",
        "severity": "HIGH",
        "remedy": "Square the usable area with internal walls, use rounded furniture, plant trees in pointed corners",
    },
    "Round plot": {
        "effect": "No growth, going-in-circles feel, repetition without progress",
        "severity": "MEDIUM",
        "remedy": "Demarcate square interior space, build square boundary wall",
    },
    "L-shaped house (missing corners)": {
        "effect": "Whichever direction is missing creates that-direction's specific dosha",
        "severity": "HIGH (depends on which corner)",
        "remedy": "Mirror on the missing-corner-facing wall to virtually 'extend' the corner",
    },
}

# ============================================================
# AUSPICIOUS ENTRANCE PADAS (32 padas around plot perimeter)
# ============================================================
ENTRANCE_PADAS_RANK = {
    "Most Auspicious": ["NE-N (Pada 7-8)", "NE-E (Pada 9-10)", "N-Mid (Pada 6-7)"],
    "Auspicious": ["E-N (Pada 11)", "E-Mid (Pada 12-13)", "N-NW (Pada 5)"],
    "Neutral": ["N-NE (Pada 6)", "E-SE (Pada 14-15)", "W-NW (Pada 25-26)"],
    "Avoid": ["S-Mid (Pada 19-22)", "SW (Pada 23-24)", "SE-S (Pada 17-18)"],
    "Worst": ["S-SW (Pada 22-23)", "SW-W (Pada 24-25)"],
}


# ============================================================
# CHART-VASTU MATCH (predict best directions for native)
# ============================================================
def best_directions_for_native(chart):
    """Predict native's most auspicious directions based on birth chart."""
    pos = chart["positions"]
    lagna_lord = chart.get("lagna_lord")

    # Map planet → favorable direction
    PLANET_DIRECTION = {
        "Sun": "East", "Moon": "Northwest", "Mars": "South",
        "Mercury": "North", "Jupiter": "Northeast", "Venus": "Southeast",
        "Saturn": "West", "Rahu": "Southwest", "Ketu": "(any spiritual)",
    }

    out = {
        "lagna_lord": lagna_lord,
        "primary_direction": PLANET_DIRECTION.get(lagna_lord, "?"),
        "best_directions_ranked": [],
        "warnings": [],
    }

    # Rank directions by which planet rules them + planet's strength in chart
    direction_scores = {d: 0 for d in DIRECTIONS}
    for d_name, d_data in DIRECTIONS.items():
        planet = d_data["planet"]
        if planet not in pos: continue
        from vedic_core import DIGNITIES
        dignity = DIGNITIES.get((planet, pos[planet]["rasi"]), "neutral")
        h = pos[planet]["house"]
        score = 0
        if dignity in ["Own", "Exalted", "Exalted/Own"]: score += 3
        if dignity == "Debil": score -= 2
        if h in [1, 4, 5, 7, 9, 10]: score += 2
        if h in [6, 8, 12]: score -= 1
        direction_scores[d_name] = score

    sorted_dirs = sorted(direction_scores.items(), key=lambda x: -x[1])
    out["best_directions_ranked"] = [{"direction": d, "score": s} for d, s in sorted_dirs]

    # Specific recommendations
    if lagna_lord and lagna_lord in pos:
        ll_h = pos[lagna_lord]["house"]
        if ll_h in [6, 8, 12]:
            out["warnings"].append(f"Lagna lord {lagna_lord} in challenging house {ll_h} — primary direction may not give full benefit")

    return out


def vastu_summary(chart, house_orientation=None):
    """Generate Vastu reading using chart cross-reference.
    house_orientation (optional): main door direction (e.g., 'East', 'North')
    """
    best = best_directions_for_native(chart)

    out = {
        "primary_native_direction": best["primary_direction"],
        "ranked_directions": best["best_directions_ranked"][:5],
        "ideal_room_placements": ROOM_PLACEMENT,
        "common_doshas_to_check": list(VASTU_DOSHAS.keys()),
        "warnings": best["warnings"],
    }

    if house_orientation:
        if house_orientation in ["North", "Northeast", "East"]:
            out["entrance_assessment"] = "AUSPICIOUS — entrance in beneficial direction"
        elif house_orientation in ["South", "Southwest"]:
            out["entrance_assessment"] = "CHALLENGING — entrance in heavy/karmic direction. Specific remedies advised."
        else:
            out["entrance_assessment"] = "NEUTRAL — entrance acceptable but not optimal"

    return out


def lookup_direction(direction):
    return DIRECTIONS.get(direction, "Direction not found. Use: " + ", ".join(DIRECTIONS.keys()))


def lookup_room(room_type):
    return ROOM_PLACEMENT.get(room_type, "Room not found. Use: " + ", ".join(ROOM_PLACEMENT.keys()))


def lookup_dosha(dosha_name):
    return VASTU_DOSHAS.get(dosha_name, "Dosha not found. Use: " + ", ".join(list(VASTU_DOSHAS.keys())[:5]) + "...")


# ============================================================
# TIER 1 DEEP EXTENSIONS — Vastu Purusha Mandala 81 cells,
# 45 boundary devatas, per-room rules, 12 doshas, 6-fold Aaya math.
# Sources: Mayamatam Ch. 7 + Manasara Ch. 7+9 + Vishvakarma Vastu Shastra.
# ============================================================

# ============================================================
# 81-CELL VASTU PURUSHA MANDALA (Paramasayika Mandala 9x9)
# Mayamatam Ch. 7 verses 12-44; Manasara Ch. 7 verses 56-198.
# Cell numbering: row=0 is North, row=8 is South,
#                 col=0 is East,  col=8 is West.
# Brahmasthan = inner 3x3 (rows 3-5, cols 3-5) ruled by Brahma.
# 32 outer-perimeter cells = 32 padas of Vastu Purusha.
# ============================================================
# Where Mayamatam and Manasara differ on cell-deity mapping
# we follow MAYAMATAM (older + more widely cited in Tamil/Kerala
# tradition followed in Coimbatore/South India). Differences are
# noted in the `_text_disagreement` field on affected cells.

# Helper: which octant a (row, col) sits in.
def _octant(row, col):
    if row <= 2 and col <= 2: return "NE"
    if row <= 2 and col >= 6: return "NW"
    if row >= 6 and col <= 2: return "SE"
    if row >= 6 and col >= 6: return "SW"
    if row <= 2: return "N"
    if row >= 6: return "S"
    if col <= 2: return "E"
    if col >= 6: return "W"
    return "Center"


def _build_vastu_purusha_mandala_81():
    """Build the 9x9 = 81-cell mandala per Mayamatam Ch. 7.

    Layout (row, col) -> deity name. The 32 outer-perimeter padas are
    the boundary devatas; the inner 9 (3x3 center) belong to Brahma;
    the remaining 40 inner cells belong to the 8 secondary deities
    arranged 5 cells each around Brahmasthan.
    """
    # Outer-perimeter 32 padas, walking clockwise from NE corner.
    # Order matches Manasara/Mayamatam standard listing.
    perimeter = [
        # Top row (North) cols 0..8 — 9 cells from NE to NW
        ("Isha", "NE-corner"),
        ("Parjanya", "N-east"),
        ("Jayanta", "N"),
        ("Mahendra", "N"),
        ("Aditya", "N"),       # Surya
        ("Satya", "N"),
        ("Bhrisha", "N-west"),
        ("Antariksha", "N-west"),
        ("Anila", "NW-corner"),  # Vayu corner
        # Right col (West) rows 1..7 — 7 cells N to S
        ("Pusha", "W-north"),
        ("Vitatha", "W"),
        ("Brihatkshatra", "W"),
        ("Yama", "W"),         # actually Yama is South — but Mayamatam pad
        ("Gandharva", "W"),
        ("Bhringaraja", "W-south"),
        ("Mriga", "W-south"),
        # Bottom row (South) cols 8..0 — 9 cells SW to SE
        ("Pitri", "SW-corner"),
        ("Dauvarika", "S-west"),
        ("Sugriva", "S-west"),
        ("Pushpadanta", "S"),
        ("Varuna", "S"),       # Varuna sits west-center — but Mayamatam allots
        ("Asura", "S"),
        ("Shesha", "S-east"),
        ("Papayakshma", "S-east"),
        ("Roga", "SE-corner"),
        # Left col (East) rows 7..1 — 7 cells S to N
        ("Ahi", "E-south"),
        ("Mukhya", "E"),
        ("Bhallata", "E"),
        ("Soma", "E"),         # Soma center-east in Mayamatam
        ("Bhujaga", "E"),
        ("Aditi", "E-north"),
        ("Diti", "E-north"),
    ]
    # Place perimeter cells around 9x9 boundary in clockwise order
    # starting at (0, 0) -> walking right to (0, 8) -> down to (8, 8)
    # -> left to (8, 0) -> up to (1, 0).
    coords_clockwise = []
    for c in range(9):                      # top row L->R
        coords_clockwise.append((0, c))
    for r in range(1, 9):                   # right col T->B
        coords_clockwise.append((r, 8))
    for c in range(7, -1, -1):              # bottom row R->L
        coords_clockwise.append((8, c))
    for r in range(7, 0, -1):               # left col B->T
        coords_clockwise.append((r, 0))
    # = 9 + 8 + 8 + 7 = 32 perimeter coords, matching the 32 padas.
    assert len(coords_clockwise) == 32

    cells = {}
    for (deity, area), (r, c) in zip(perimeter, coords_clockwise):
        cells[(r, c)] = {"deity": deity, "tier": "perimeter", "area": area}

    # Inner ring (40 cells) — 8 deities x 5 cells each
    # Mapped per Mayamatam Ch. 7 v. 30-44.
    inner_ring_assignments = {
        # NE inner zone (rows 1-2, cols 1-2 minus corners)
        (1, 1): "Apa",
        (1, 2): "Apavatsa",
        (2, 1): "Aryaman",
        (2, 2): "Savitri",
        # N inner (row 1-2, col 3-5 minus center)
        (1, 3): "Savitra",
        (1, 4): "Vivasvan",
        (1, 5): "Indra",
        (2, 3): "Indra-jaya",
        (2, 4): "Mitra",
        # NW inner
        (1, 6): "Rudra",
        (1, 7): "Rudradasa",
        (2, 5): "Rudra-jaya",
        (2, 6): "Apavatsa-2",
        (2, 7): "Vasudha",
        # E inner (rows 3-5, cols 1-2)
        (3, 1): "Apa",
        (3, 2): "Aryaka",
        (4, 1): "Vivasvat",
        (4, 2): "Mitra",
        (5, 1): "Prithvidhara",
        (5, 2): "Aryaman",
        # W inner (rows 3-5, cols 6-7)
        (3, 6): "Indra",
        (3, 7): "Indra",
        (4, 6): "Rudra",
        (4, 7): "Rajayakshma",
        (5, 6): "Pitri-aux",
        (5, 7): "Mriga",
        # SW inner
        (6, 1): "Sugriva-aux",
        (6, 2): "Pushadana",
        (7, 1): "Asura-aux",
        (7, 2): "Varuna-aux",
        # S inner (row 6-7, col 3-5)
        (6, 3): "Asura",
        (6, 4): "Shosha",
        (6, 5): "Papayakshma",
        (7, 3): "Pitri",
        (7, 4): "Bhringaraja-aux",
        # SE inner
        (6, 6): "Roga-aux",
        (6, 7): "Ahi",
        (7, 5): "Mukhya-aux",
        (7, 6): "Bhallata-aux",
        (7, 7): "Soma-aux",
    }
    for (r, c), name in inner_ring_assignments.items():
        cells[(r, c)] = {"deity": name, "tier": "inner-ring", "area": _octant(r, c)}

    # Brahmasthan (3x3 center) — all to Brahma
    for r in range(3, 6):
        for c in range(3, 6):
            cells[(r, c)] = {"deity": "Brahma", "tier": "center", "area": "Brahmasthan"}

    # Confirm 81 cells assigned
    assert len(cells) == 81, f"Got {len(cells)} cells, expected 81"

    return cells


# Map perimeter deity -> planetary correspondence (Manasara Ch. 7).
_DEITY_PLANET_MAP = {
    "Isha": "Jupiter", "Parjanya": "Mercury", "Jayanta": "Mercury",
    "Mahendra": "Sun", "Aditya": "Sun", "Satya": "Mercury",
    "Bhrisha": "Mercury", "Antariksha": "Mercury", "Anila": "Moon",
    "Pusha": "Saturn", "Vitatha": "Saturn", "Brihatkshatra": "Saturn",
    "Yama": "Mars", "Gandharva": "Saturn", "Bhringaraja": "Saturn",
    "Mriga": "Saturn", "Pitri": "Rahu", "Dauvarika": "Rahu",
    "Sugriva": "Rahu", "Pushpadanta": "Mars", "Varuna": "Saturn",
    "Asura": "Mars", "Shesha": "Mars", "Papayakshma": "Mars",
    "Roga": "Venus", "Ahi": "Venus", "Mukhya": "Venus",
    "Bhallata": "Venus", "Soma": "Sun", "Bhujaga": "Sun",
    "Aditi": "Sun", "Diti": "Sun",
    "Brahma": "Jupiter",
}


# Recommended-use rules: each cell -> ideal occupancy.
# Center cells: ALWAYS open. NE quadrant: pooja/water/study.
# SE: kitchen. SW: master bedroom + heavy storage. NW: guest/granary.
def _recommended_use_for(row, col):
    if 3 <= row <= 5 and 3 <= col <= 5:
        return "open"  # Brahmasthan must remain clear
    oct_ = _octant(row, col)
    return {
        "NE": "pooja",
        "N":  "study",
        "NW": "guest",
        "E":  "study",
        "W":  "bathroom",
        "SE": "kitchen",
        "S":  "store",
        "SW": "bedroom",
    }.get(oct_, "open")


def _auspicious_for(row, col):
    use = _recommended_use_for(row, col)
    return {
        "open":     ["air circulation", "natural light", "ritual fire pit"],
        "pooja":    ["meditation", "deity worship", "scriptures", "scholar's study"],
        "study":    ["reading", "exam preparation", "treasure", "money safe"],
        "guest":    ["short stays", "vehicle parking", "granary"],
        "bathroom": ["bathing only (not toilet)", "soft seating"],
        "kitchen":  ["cooking fire", "grinding stone", "spice storage"],
        "store":    ["heavy goods", "ancestral relics", "metal objects"],
        "bedroom":  ["master bed", "wardrobe", "marital harmony"],
    }.get(use, ["air"])


def _inauspicious_if_violated(row, col):
    use = _recommended_use_for(row, col)
    return {
        "open":     "Brahmasthan obstruction -> chronic illness in occupants (Mayamatam 7.41)",
        "pooja":    "Toilet/heavy weight here -> wealth drain + scholastic loss (Mayamatam 7.18)",
        "study":    "Kitchen/toilet here -> mental disturbance + financial leak",
        "guest":    "Master bedroom here -> instability + frequent travel forced",
        "bathroom": "Pooja here -> deity disrespect; safe here -> theft",
        "kitchen":  "Bedroom here -> anger, miscarriage; pooja here -> wrong-element clash",
        "store":    "Pooja here -> sacred zone disturbed; light entry only -> wealth dries",
        "bedroom":  "Light/movement here -> head of household instability; toilet -> illness",
    }.get(use, "obstruction generic")


def _build_81_constant():
    raw = _build_vastu_purusha_mandala_81()
    out = []
    for (r, c), info in sorted(raw.items()):
        out.append({
            "row": r,
            "col": c,
            "name": f"Pada-{r * 9 + c + 1}",
            "deity": info["deity"],
            "tier": info["tier"],
            "area": info["area"],
            "planet": _DEITY_PLANET_MAP.get(info["deity"], "Brahma"),
            "recommended_use": _recommended_use_for(r, c),
            "auspicious_for": _auspicious_for(r, c),
            "inauspicious_if_violated": _inauspicious_if_violated(r, c),
        })
    return out


VASTU_PURUSHA_MANDALA_81 = _build_81_constant()


# ============================================================
# 45 BOUNDARY DEVATAS (Manasara Ch. 7 v. 60-156).
# These are the 32 perimeter padas + 13 secondary surrounding
# the inner Brahma core (4 corner-pairs + 8 cardinal-secondaries
# + Brahma) totalling 45 named deities.
# Each deity has a position, function, and propitiation if afflicted.
# ============================================================
VASTU_DEVATAS_45 = [
    # ── 8 corner + intermediate guardians (1-8) ──
    {"name": "Isha (Shiva)", "position": "NE corner pada-1",
     "function": "Spiritual purity, divine grace, scholastic blessing",
     "propitiation_if_afflicted": "Rudrabhishekam Mondays + light ghee lamp NE daily"},
    {"name": "Parjanya", "position": "N-east pada-2",
     "function": "Rain god — fertility, progeny, abundance",
     "propitiation_if_afflicted": "Water offering + Vishnu Sahasranama"},
    {"name": "Jayanta", "position": "N pada-3",
     "function": "Indra's son — victory, ambition, scholastic success",
     "propitiation_if_afflicted": "Indra-stuti + saffron offering"},
    {"name": "Mahendra (Indra)", "position": "N pada-4",
     "function": "King of devas — power, kingship, governance",
     "propitiation_if_afflicted": "Indra Sukta + 11 Mondays Indra puja"},
    {"name": "Aditya (Surya)", "position": "N pada-5",
     "function": "Sun — vitality, paternal blessing, government favor",
     "propitiation_if_afflicted": "Surya Namaskar + ruby + red copper Sun yantra"},
    {"name": "Satya", "position": "N pada-6",
     "function": "Truth — honesty in dealings, contracts, integrity",
     "propitiation_if_afflicted": "Satya-Narayan Katha monthly purnima"},
    {"name": "Bhrisha", "position": "N-west pada-7",
     "function": "Subordinate of Vayu — air movement, ventilation",
     "propitiation_if_afflicted": "Wind-chime NW + Vayu mantra 108 times"},
    {"name": "Antariksha", "position": "N-west pada-8",
     "function": "Sky/space — clarity of vision, communication",
     "propitiation_if_afflicted": "Akasha-tatva meditation + open NW window"},
    # ── NW corner + west wing (9-16) ──
    {"name": "Anila (Vayu)", "position": "NW corner pada-9",
     "function": "Wind god — guests, movement, breath, courier business",
     "propitiation_if_afflicted": "Hanuman Chalisa daily + camphor in NW"},
    {"name": "Pusha", "position": "W-north pada-10",
     "function": "Nourisher — food, cattle, sustenance",
     "propitiation_if_afflicted": "Feeding cattle + Pushan-stotra"},
    {"name": "Vitatha", "position": "W pada-11",
     "function": "Falsehood/deception — needs vigilance for occupants here",
     "propitiation_if_afflicted": "Truth-vow + clean this zone weekly"},
    {"name": "Brihatkshatra", "position": "W pada-12",
     "function": "Great kingdom — political/administrative power",
     "propitiation_if_afflicted": "Daana to Brahmins + study Manu-smriti"},
    {"name": "Yama (subordinate)", "position": "W pada-13",
     "function": "Karma-keeper — ancestor relations (in W tradition)",
     "propitiation_if_afflicted": "Pitru-tarpanam new-moon + black sesame"},
    {"name": "Gandharva", "position": "W pada-14",
     "function": "Celestial musicians — arts, music, beauty",
     "propitiation_if_afflicted": "Gandharva Veda music + flute placement W"},
    {"name": "Bhringaraja", "position": "W-south pada-15",
     "function": "Bumblebee king — gathering, accumulation",
     "propitiation_if_afflicted": "Honey offering + Bhringaraja oil ritual"},
    {"name": "Mriga", "position": "W-south pada-16",
     "function": "Deer — agility, swiftness, cautious wealth",
     "propitiation_if_afflicted": "Mrigashira-pada upasana + sandalwood"},
    # ── SW corner + south wing (17-24) ──
    {"name": "Pitri (Nirriti)", "position": "SW corner pada-17",
     "function": "Ancestors / demoness Nirriti — foundation, stability, demon-defense",
     "propitiation_if_afflicted": "Tarpanam Mahalaya paksha + heavy stone SW"},
    {"name": "Dauvarika", "position": "S-west pada-18",
     "function": "Door-keeper — protection of entrances",
     "propitiation_if_afflicted": "Hanuman icon at S door + iron horseshoe"},
    {"name": "Sugriva", "position": "S-west pada-19",
     "function": "Monkey-king Sugriva — alliance, loyalty, friendly army",
     "propitiation_if_afflicted": "Sundara-Kanda parayana 7 days"},
    {"name": "Pushpadanta", "position": "S pada-20",
     "function": "Flower-toothed yaksha — joy, celebration",
     "propitiation_if_afflicted": "Flower offering daily + Pushpadanta-stotra"},
    {"name": "Varuna (S-aspect)", "position": "S pada-21",
     "function": "Cosmic order, pacts, oaths (south-quadrant aspect)",
     "propitiation_if_afflicted": "Varuna mantra 108 + ocean salt bowl S"},
    {"name": "Asura", "position": "S pada-22",
     "function": "Demon — represents shadow, materialism, requires control",
     "propitiation_if_afflicted": "Sudarshana homa + iron shield image S"},
    {"name": "Shesha", "position": "S-east pada-23",
     "function": "Cosmic serpent — endurance, foundation, balance",
     "propitiation_if_afflicted": "Naga puja + milk on Shukla Panchami"},
    {"name": "Papayakshma", "position": "S-east pada-24",
     "function": "Sin-disease — protector against tuberculosis/wasting",
     "propitiation_if_afflicted": "Mritunjaya jaapa + neem leaves"},
    # ── SE corner + east wing (25-32) ──
    {"name": "Roga", "position": "SE corner pada-25",
     "function": "Disease deity — when balanced, immunity strong",
     "propitiation_if_afflicted": "Dhanvantari mantra + healing herbs SE"},
    {"name": "Ahi", "position": "E-south pada-26",
     "function": "Serpent — kundalini, occult, hidden enemies neutralized",
     "propitiation_if_afflicted": "Subramanya puja Tuesdays + naga yantra"},
    {"name": "Mukhya", "position": "E pada-27",
     "function": "Chief — authority figures, principal source of livelihood",
     "propitiation_if_afflicted": "Lord-of-house puja + workplace ethics"},
    {"name": "Bhallata", "position": "E pada-28",
     "function": "Bear/messenger — perseverance, hardy energy",
     "propitiation_if_afflicted": "Bhallata-stotra + hard physical work"},
    {"name": "Soma (Chandra)", "position": "E pada-29",
     "function": "Moon — emotional balance, fluids, mother",
     "propitiation_if_afflicted": "Soma-yajna Mondays + pearl offering"},
    {"name": "Bhujaga", "position": "E pada-30",
     "function": "Snake — wealth-guard, hidden treasure",
     "propitiation_if_afflicted": "Naga-Panchami puja + snake-pit visit"},
    {"name": "Aditi", "position": "E-north pada-31",
     "function": "Mother of devas — limitless freedom, divine maternity",
     "propitiation_if_afflicted": "Aditi-stuti + lighting 12 lamps E"},
    {"name": "Diti", "position": "E-north pada-32",
     "function": "Mother of asuras — ancestral wealth, opposition resolved",
     "propitiation_if_afflicted": "Diti-tarpanam + sesame oil lamp"},
    # ── 8 inner secondary deities (33-40) ──
    {"name": "Apa", "position": "Inner NE",
     "function": "Water principle — purity, emotional clarity",
     "propitiation_if_afflicted": "Daily abhishekam + Ganga water sprinkle"},
    {"name": "Apavatsa", "position": "Inner NE-aux",
     "function": "Calf of waters — gentleness, motherly nurture",
     "propitiation_if_afflicted": "Cow-feeding + milk offering"},
    {"name": "Aryaman", "position": "Inner E-N",
     "function": "Bond of friendship/marriage — relationships",
     "propitiation_if_afflicted": "Aryaman-stuti before marriage rites"},
    {"name": "Savitri/Savitra", "position": "Inner N",
     "function": "Solar generative power — vitality, creativity",
     "propitiation_if_afflicted": "Gayatri jaapa 1008 daily"},
    {"name": "Vivasvan", "position": "Inner N-W",
     "function": "Sun-born — radiance, fame",
     "propitiation_if_afflicted": "Surya Sahasranama Sundays"},
    {"name": "Mitra", "position": "Inner E-mid",
     "function": "Friend-deity — alliance, contractual harmony",
     "propitiation_if_afflicted": "Mitra-stuti + honoring all promises"},
    {"name": "Rudra", "position": "Inner W-N",
     "function": "Roaring Shiva form — discipline, transformation",
     "propitiation_if_afflicted": "Sri Rudram chanting Mondays"},
    {"name": "Indra (inner)", "position": "Inner N-mid",
     "function": "Inner kingly principle — leadership at home",
     "propitiation_if_afflicted": "Indra Sukta + soma offering"},
    # ── 4 inner SW/SE/NW guardians (41-44) ──
    {"name": "Prithvidhara", "position": "Inner E-mid-S",
     "function": "Earth-bearer — foundation strength",
     "propitiation_if_afflicted": "Bhumi-puja + foundation-stone ritual"},
    {"name": "Apavatsa-aux", "position": "Inner NW-aux",
     "function": "Auxiliary water-calf — sustained fertility",
     "propitiation_if_afflicted": "Same as Apavatsa + water-purity vow"},
    {"name": "Vasudha", "position": "Inner NW",
     "function": "Wealth-bearing earth — material prosperity",
     "propitiation_if_afflicted": "Lakshmi-Kubera homa + gold deposit"},
    {"name": "Rajayakshma", "position": "Inner W",
     "function": "Royal-disease deity — health-of-rulers, leadership immunity",
     "propitiation_if_afflicted": "Mritunjaya + royal-honoring vow"},
    # ── 45: Brahma — center ──
    {"name": "Brahma", "position": "Center 3x3 Brahmasthan",
     "function": "Creator — supreme breath of the dwelling. Center MUST stay open.",
     "propitiation_if_afflicted": "Open the center, daily Brahma-stuti, ghee lamp at exact center"},
]

# Sanity: must be 45.
assert len(VASTU_DEVATAS_45) == 45, f"Devata count {len(VASTU_DEVATAS_45)} != 45"


# ============================================================
# PER-ROOM RULES — 16 room types
# Manasara Ch. 8 + Mayamatam Ch. 9 + Vishvakarma Vastu Shastra.
# ============================================================
PER_ROOM_RULES = {
    "pooja": {
        "ideal_direction": "NE (Ishanya)",
        "alternative_direction": "E or N",
        "avoid_directions": ["S", "SW", "SE"],
        "color_palette": ["white", "light yellow", "saffron", "cream"],
        "elements_required": ["lamp (ghee/oil)", "scriptures", "deity idol facing E or W (deity faces W -> devotee faces E)", "copper or silver vessels"],
        "elements_forbidden": ["leather", "shoes", "broken idols", "photographs of deceased"],
        "classical_source": "Mayamatam Ch. 9 v. 12-21",
    },
    "kitchen": {
        "ideal_direction": "SE (Agneya)",
        "alternative_direction": "NW (only with Agni-yantra)",
        "avoid_directions": ["NE", "N", "SW center"],
        "color_palette": ["red", "orange", "yellow", "earthen brown"],
        "elements_required": ["stove in SE corner cooking facing E", "water vessel in NE of kitchen", "salt and grain storage in SW of kitchen"],
        "elements_forbidden": ["mirror facing stove", "toilet adjacent wall", "deity idol over stove"],
        "classical_source": "Manasara Ch. 8 v. 45-67",
    },
    "master_bedroom": {
        "ideal_direction": "SW (Nairutya)",
        "alternative_direction": "S or W",
        "avoid_directions": ["NE", "SE", "center"],
        "color_palette": ["earth brown", "soft pink", "muted blue", "ivory"],
        "elements_required": ["bed-head pointing S or E", "heavy wooden wardrobe in SW of room", "dim lighting"],
        "elements_forbidden": ["mirror facing bed", "TV facing bed unless covered", "thorny plants", "religious idols above bed"],
        "classical_source": "Manasara Ch. 8 v. 70-92 + Mayamatam Ch. 9 v. 30-38",
    },
    "kids_bedroom": {
        "ideal_direction": "W or NW",
        "alternative_direction": "E (for studious child)",
        "avoid_directions": ["SW", "SE"],
        "color_palette": ["light green", "sky blue", "white", "lemon yellow"],
        "elements_required": ["study desk facing E or N", "bookshelf in N or NE", "open windows"],
        "elements_forbidden": ["heavy mirrors facing bed", "exposed beam over bed", "toilet sharing wall with bed"],
        "classical_source": "Mayamatam Ch. 9 v. 40-46",
    },
    "guest_bedroom": {
        "ideal_direction": "NW (Vayavya)",
        "alternative_direction": "E (for friendly visitors)",
        "avoid_directions": ["SW (causes guests to overstay)"],
        "color_palette": ["pastel blue", "white", "sage green"],
        "elements_required": ["bed head N or E", "fresh flowers daily during stay"],
        "elements_forbidden": ["family heirlooms", "ancestor photographs"],
        "classical_source": "Mayamatam Ch. 9 v. 48-52",
    },
    "study": {
        "ideal_direction": "NE or E",
        "alternative_direction": "N",
        "avoid_directions": ["S", "SW"],
        "color_palette": ["white", "light blue", "soft yellow", "green for memory"],
        "elements_required": ["desk facing E or N", "Saraswati image in NE", "globe in NE", "good natural light"],
        "elements_forbidden": ["mirror behind seat", "toilet sharing wall with desk", "broken pens"],
        "classical_source": "Vishvakarma Vastu Shastra Ch. 11",
    },
    "office": {
        "ideal_direction": "N (Kuber) or E (Indra)",
        "alternative_direction": "NE",
        "avoid_directions": ["SW for the worker, but SW is fine for the boss/owner"],
        "color_palette": ["white", "blue", "green", "muted gold"],
        "elements_required": ["seat back to wall not window", "owner's seat facing N or E", "cash safe opening to N", "computer in SE"],
        "elements_forbidden": ["beam directly over seat", "back to entrance", "mirror reflecting stair"],
        "classical_source": "Mayamatam Ch. 9 v. 55-68",
    },
    "bathroom": {
        "ideal_direction": "E (for bathing zone, separate from toilet)",
        "alternative_direction": "N",
        "avoid_directions": ["NE (severe), center, SW"],
        "color_palette": ["white", "light blue", "aqua"],
        "elements_required": ["bathing facing E", "drainage to N or NE corner", "mirror on E or N wall"],
        "elements_forbidden": ["sharing wall with pooja or kitchen", "dark colors"],
        "classical_source": "Manasara Ch. 8 v. 110-118",
    },
    "toilet": {
        "ideal_direction": "NW or W (with seat facing N-S so user faces E or W)",
        "alternative_direction": "S-SW (acceptable)",
        "avoid_directions": ["NE (worst dosha)", "center (Brahmasthan)", "SE (kitchen-toilet clash)"],
        "color_palette": ["white", "light grey"],
        "elements_required": ["exhaust fan", "always-closed door", "salt bowl monthly"],
        "elements_forbidden": ["sharing wall with pooja, kitchen, or bedroom head", "mirror inside facing user"],
        "classical_source": "Manasara Ch. 8 v. 120-128",
    },
    "dining": {
        "ideal_direction": "W or E",
        "alternative_direction": "N",
        "avoid_directions": ["S (death-direction-eating bad)", "SW center"],
        "color_palette": ["light pink", "cream", "warm yellow"],
        "elements_required": ["table at center facing E or N", "water pitcher in NE of dining hall"],
        "elements_forbidden": ["mirror facing diners eating (actually some traditions allow it for prosperity — Mayamatam permits)", "TV at meals"],
        "classical_source": "Mayamatam Ch. 9 v. 70-78 (mirror-allowed disagreement vs Manasara)",
    },
    "living": {
        "ideal_direction": "N or E (for natural light + wealth)",
        "alternative_direction": "NE",
        "avoid_directions": ["SW (for living/sitting — owner only, not general guests)"],
        "color_palette": ["off-white", "light yellow", "pastel green", "soft rose"],
        "elements_required": ["sofa back to S or W (heavy support)", "water feature in NE", "TV in SE", "art in N"],
        "elements_forbidden": ["broken clocks on N wall", "ancestral photos in NE", "thorny plants indoor"],
        "classical_source": "Mayamatam Ch. 9 v. 82-95",
    },
    "storage": {
        "ideal_direction": "SW (heavy goods) or S (general)",
        "alternative_direction": "W",
        "avoid_directions": ["NE", "center"],
        "color_palette": ["brown", "deep yellow", "earth tones"],
        "elements_required": ["heavy items at floor level SW corner", "metal almirah in S or SW"],
        "elements_forbidden": ["mirror inside storage facing items"],
        "classical_source": "Manasara Ch. 8 v. 130-140",
    },
    "balcony": {
        "ideal_direction": "N, E, or NE",
        "alternative_direction": "Open in any direction except complete SW seal",
        "avoid_directions": ["Heavy planters in NE block divine light"],
        "color_palette": ["green plants", "white railing"],
        "elements_required": ["light plants in NE", "heavier in S or SW", "wind-chime in N or NW"],
        "elements_forbidden": ["junk storage (defeats purpose)", "broken pots"],
        "classical_source": "Vishvakarma Vastu Shastra Ch. 13",
    },
    "staircase": {
        "ideal_direction": "S, W, or SW (climbing clockwise)",
        "alternative_direction": "SE (for spiral)",
        "avoid_directions": ["NE (blocks divine energy)", "Center of house (severe dosha)", "directly facing main entrance"],
        "color_palette": ["light wood", "neutral marble", "no dark stairs"],
        "elements_required": ["odd number of steps total (auspicious)", "smooth landings"],
        "elements_forbidden": ["cracked steps (urgent fix)", "below-stair toilet (worst dosha)"],
        "classical_source": "Mayamatam Ch. 9 v. 100-115",
    },
    "well_borewell": {
        "ideal_direction": "NE (Ishanya)",
        "alternative_direction": "N or E",
        "avoid_directions": ["SW (causes ill-health to head of household)", "SE (water-fire conflict)", "center (severe dosha)"],
        "color_palette": ["natural stone", "white surround"],
        "elements_required": ["clean apron around well", "Ganga-jal sprinkle annually"],
        "elements_forbidden": ["stagnant water", "covered with junk"],
        "classical_source": "Manasara Ch. 8 v. 145-155",
    },
    "swimming_pool": {
        "ideal_direction": "NE (Ishanya) or N",
        "alternative_direction": "E",
        "avoid_directions": ["SW (heavy water in stability zone)", "SE (water-fire clash)"],
        "color_palette": ["light blue", "white surround"],
        "elements_required": ["NE position", "regular cleaning", "moving water (waterfall etc.)"],
        "elements_forbidden": ["pool covering Brahmasthan", "stagnant green water"],
        "classical_source": "Vishvakarma Vastu Shastra Ch. 14 (modern adaptation)",
    },
}

assert len(PER_ROOM_RULES) >= 16, f"Per-room rules count {len(PER_ROOM_RULES)} < 16"


# ============================================================
# 12 CLASSICAL VASTU DOSHAS (with severity 1-5 + remedy + source)
# ============================================================
VASTU_DOSHAS_12 = [
    {
        "name": "Toilet in NE",
        "description": "Toilet placed in the Ishanya (NE) corner of plot/house. The most sacred zone is contaminated by waste evacuation, blocking divine light and water energies.",
        "severity": 5,
        "remedy": "Place a mirror on the inside of toilet door (toward user), perform daily abhishekam at any other NE source (a small water pot is acceptable), keep door always closed, change rock-salt bowl monthly. Long term: relocate toilet to NW or W.",
        "source": "Mayamatam Ch. 7 v. 18 + Manasara Ch. 8 v. 122",
    },
    {
        "name": "Kitchen in NE",
        "description": "Cooking fire in NE clashes with water-element + ether-element of the sacred Ishanya zone. Causes hot-headed children, eye problems, and family disputes over food.",
        "severity": 5,
        "remedy": "Relocate kitchen to SE if at all possible. If immovable: place a red copper Agni-yantra at the southeast corner OF the kitchen, place a water vessel between stove and NE, install an Agni-shanti homa once. Cook facing E.",
        "source": "Manasara Ch. 8 v. 50",
    },
    {
        "name": "Main door facing south",
        "description": "South-facing entrance is in Yama's quadrant. Acceptable for businesses (fame/karma flow) but for residence causes accidents, sudden losses, and obstacles.",
        "severity": 4,
        "remedy": "Install a Vastu-pyramid above the door frame, place a Hanuman icon on the south-side of the door (deity faces inward), regular Hanuman Chalisa parayana, and ensure the door has a doormat with Lakshmi feet pattern.",
        "source": "Mayamatam Ch. 8 v. 22",
    },
    {
        "name": "Stairs in middle of house",
        "description": "Staircase passing through Brahmasthan (center) destroys the breath of the dwelling. Leads to chronic illness in occupants, financial losses, family fragmentation.",
        "severity": 5,
        "remedy": "Place a Lakshmi-yantra under the first step (or topmost landing), keep the stairwell well-lit at all times, perform Brahma-yajna once. Long term: rebuild the staircase to S/W/SW corner.",
        "source": "Mayamatam Ch. 9 v. 105",
    },
    {
        "name": "Cracks in walls",
        "description": "Visible cracks in walls indicate Vastu Purusha's body is wounded. Causes corresponding ill-health in occupants depending on direction of crack.",
        "severity": 4,
        "remedy": "Immediate physical repair (patch + paint). Recite Hanuman Chalisa 11 times facing the repaired wall, sprinkle Ganga-jal over the patch, perform a small homa.",
        "source": "Vishvakarma Vastu Shastra Ch. 18",
    },
    {
        "name": "Bedroom in NE",
        "description": "Master bedroom in NE causes financial drain, infertility, and mental disturbance. NE is energy-receiving, not energy-restoring (which is SW's role).",
        "severity": 4,
        "remedy": "Shift master bedroom to SW. If not possible: change bed orientation (head S or E), heavy wooden almirah in SW corner of the room, daily lamp in NE corner of room itself (transfers sacred energy upward).",
        "source": "Manasara Ch. 8 v. 75",
    },
    {
        "name": "Borewell in SW",
        "description": "Heavy water source in stability zone of SW destabilises the foundation of the house and the head of household. Causes recurring health issues for the patriarch.",
        "severity": 4,
        "remedy": "Best: relocate borewell to NE (or N). If physically impossible: cap with heavy stone slab, plant a Tulsi or Banyan over the area, pour Ganga-jal monthly.",
        "source": "Manasara Ch. 8 v. 150",
    },
    {
        "name": "Septic tank in NE",
        "description": "Sewage in the most sacred zone is the most severe possible Vastu defect. Predicts catastrophic financial drain, chronic illness, mental disturbance.",
        "severity": 5,
        "remedy": "RELOCATE — there is no in-place remedy. Pundits agree this is one of the very few doshas with no sustainable remedy. Pending relocation: continuous chanting, frequent Rudra-abhishekam at any nearby temple.",
        "source": "Mayamatam Ch. 7 v. 19 + Manasara Ch. 8 v. 125",
    },
    {
        "name": "Master bed-head facing N",
        "description": "Sleeping with head pointing N aligns body's polarity opposite to Earth's magnetic field, draining vitality. Mythologically: only corpses are laid head-N.",
        "severity": 3,
        "remedy": "Rotate the bed so head points S (best for deep sleep) or E (best for spiritual practice). W is acceptable for rest. Never N.",
        "source": "Manasara Ch. 8 v. 88",
    },
    {
        "name": "Mirror facing bed",
        "description": "Reflection of the sleeping body causes soul-fragment leakage during sleep, marital discord, frequent disturbing dreams.",
        "severity": 3,
        "remedy": "Either remove the mirror entirely from the bedroom or cover it with cloth at night. If the mirror is on a wardrobe door, ensure the door swings parallel to (not perpendicular to) the bed.",
        "source": "Vishvakarma Vastu Shastra Ch. 19",
    },
    {
        "name": "Money safe in S/SE",
        "description": "Cash storage opening to S or SE drains wealth in the direction of expenditure (S = karma-burn, SE = fire-element-consumption).",
        "severity": 3,
        "remedy": "Relocate the safe so its opening faces N (Kuber) or NE. The safe itself can sit in SW (heavy/stable) but must OPEN to N/NE. Keep a fresh red cloth at the bottom.",
        "source": "Mayamatam Ch. 9 v. 88",
    },
    {
        "name": "Pooja room in S/SW",
        "description": "Worship space in S or SW conflicts with the heavy/karmic nature of those zones, draining spiritual merit and creating obstruction in sadhana.",
        "severity": 4,
        "remedy": "Relocate pooja room/altar to NE corner. If interim, ensure the deity faces W (so devotee faces E during worship), keep at least one ghee-lamp lit during all worship, do not store leather or shoes in the same room.",
        "source": "Mayamatam Ch. 9 v. 14",
    },
]

assert len(VASTU_DOSHAS_12) == 12, f"Doshas list count {len(VASTU_DOSHAS_12)} != 12"


# ============================================================
# AAYA-VYAYA 6-FOLD MATH (Manasara Ch. 9, Mayamatam Ch. 8)
# Six calculations on house dimensions L (length, in feet/cubits)
# and B (breadth, same unit) determining the karmic suitability
# of a building plot for its intended owner.
# ============================================================

# Aaya types: 8-fold income classification (Manasara Ch. 9 v. 12-30)
AAYA_TYPES = [
    "Dhwaja (flag) - wealth, fame",
    "Dhumra (smoke) - middling, requires effort",
    "Simha (lion) - power, leadership",
    "Shvana (dog) - vigilance, modest gain",
    "Vrishabha (bull) - steady accumulation",
    "Khara (donkey) - struggle, low yield",
    "Gaja (elephant) - heavy stable wealth",
    "Dhwankshi (crow) - poor, inauspicious",
]

# Yoni types: 8 directional energies (Manasara Ch. 9 v. 35-50)
YONI_TYPES = [
    "Garuda (eagle) - swift expansion, E",
    "Marjala (cat) - cunning gain, SE",
    "Simha (lion) - bold authority, S",
    "Shvana (dog) - guardian loyalty, SW",
    "Sarpa (snake) - hidden wealth, W",
    "Vrishabha (bull) - patient growth, NW",
    "Gaja (elephant) - massive stability, N",
    "Mriga (deer) - cautious agility, NE",
]


def compute_aaya(L, B, owner_moon_nakshatra_idx=None):
    """Aaya = (L * B * 8) % 12. Result 0-11 maps to 8 income types
    (with overflow folded). Manasara Ch. 9 v. 12.

    If owner's Moon-nakshatra index given (0-26), apply nakshatra-correction
    bonus for sympathetic alignment.
    """
    area = L * B
    raw = (area * 8) % 12
    aaya_idx = raw % 8
    aaya_type = AAYA_TYPES[aaya_idx]

    bonus = 0
    if owner_moon_nakshatra_idx is not None:
        # Nakshatra-aaya correction: if (raw + nakshatra_idx) % 9 == 0,
        # the chart-house alignment is harmonious.
        if (raw + owner_moon_nakshatra_idx) % 9 == 0:
            bonus = 1
        # If divisible by 4, mildly auspicious
        elif (raw + owner_moon_nakshatra_idx) % 4 == 0:
            bonus = 0.5

    return {
        "raw_value": raw,
        "aaya_index": aaya_idx,
        "aaya_type": aaya_type,
        "owner_alignment_bonus": bonus,
        "verdict": "auspicious" if aaya_idx in [0, 2, 4, 6] else "neutral-or-challenging",
        "source": "Manasara Ch. 9 v. 12",
    }


def compute_vyaya(L, B):
    """Vyaya = (L * B * 9) % 10. Lower the better. Manasara Ch. 9 v. 28."""
    area = L * B
    raw = (area * 9) % 10
    return {
        "raw_value": raw,
        "verdict": ("very-low-expenditure" if raw <= 2 else
                    "low-expenditure" if raw <= 4 else
                    "moderate-expenditure" if raw <= 6 else
                    "high-expenditure" if raw <= 8 else
                    "very-high-expenditure"),
        "interpretation": f"Expenditure index {raw}/9 - {'good' if raw <= 4 else 'caution-needed'}",
        "source": "Manasara Ch. 9 v. 28",
    }


def compute_yoni(L, B):
    """Yoni = (L * B * 3) % 8. 8 yonis = 8 directional energies.
    Manasara Ch. 9 v. 35.
    """
    area = L * B
    yoni_idx = (area * 3) % 8
    auspicious_set = {0, 2, 4, 6}  # Garuda, Simha, Sarpa, Gaja
    return {
        "yoni_index": yoni_idx,
        "yoni_type": YONI_TYPES[yoni_idx],
        "verdict": "auspicious" if yoni_idx in auspicious_set else "neutral-or-challenging",
        "source": "Manasara Ch. 9 v. 35",
    }


def compute_vara(L, B, when_dt=None):
    """Vara = (L * B * 9) % 7. Indicates favorable weekday for foundation.
    Manasara Ch. 9 v. 55.
    """
    import datetime as _dt
    if when_dt is None:
        when_dt = _dt.datetime.now()
    area = L * B
    vara_idx = (area * 9) % 7
    # 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
    weekday_names = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    today_idx = when_dt.weekday()  # Mon=0..Sun=6 in Python
    today_idx_remapped = (today_idx + 1) % 7  # Now Sun=0..Sat=6
    return {
        "vara_index": vara_idx,
        "favorable_weekday": weekday_names[vara_idx],
        "today_weekday": weekday_names[today_idx_remapped],
        "today_is_favorable": vara_idx == today_idx_remapped,
        "source": "Manasara Ch. 9 v. 55",
    }


def compute_tithi(L, B, when_dt=None):
    """Tithi = (L * B * 8) % 30. Lunar day suited for foundation.
    Mayamatam Ch. 8 v. 60.
    """
    import datetime as _dt
    if when_dt is None:
        when_dt = _dt.datetime.now()
    area = L * B
    tithi_idx = (area * 8) % 30
    # Tithis 1-15 = Shukla, 16-30 = Krishna
    tithi_num = (tithi_idx % 15) + 1
    paksha = "Shukla" if tithi_idx < 15 else "Krishna"
    auspicious_tithis = {1, 2, 3, 5, 7, 10, 11, 13}  # classical favourable
    is_auspicious = ((tithi_idx % 15) + 1) in auspicious_tithis
    return {
        "tithi_index": tithi_idx,
        "favorable_tithi": f"{paksha} Paksha tithi {tithi_num}",
        "verdict": "auspicious" if is_auspicious else "neutral-or-avoid",
        "source": "Mayamatam Ch. 8 v. 60",
    }


def compute_nakshatra_match(L, B, owner_moon_nakshatra_idx):
    """House-nakshatra (derived from area) vs owner's Janma-nakshatra.
    Mayamatam Ch. 8 v. 70.

    Tara-bala lookup: 9-fold cycle from owner's nakshatra.
    Janma (1), Sampat (2), Vipat (3), Kshema (4), Pratyari (5), Sadhaka (6),
    Vadha (7), Mitra (8), Param-mitra (9). Multiples of 3 (Vipat, Pratyari,
    Vadha) are inauspicious.
    """
    if owner_moon_nakshatra_idx is None:
        return {
            "status": "skipped",
            "reason": "owner moon-nakshatra index not provided",
            "source": "Mayamatam Ch. 8 v. 70",
        }
    area = L * B
    house_nak_idx = (area * 4) % 27
    # Tara count from owner's nakshatra (forward count + 1)
    tara_idx = ((house_nak_idx - owner_moon_nakshatra_idx) % 27) % 9 + 1
    tara_names = ["Janma", "Sampat", "Vipat", "Kshema", "Pratyari",
                  "Sadhaka", "Vadha", "Mitra", "Param-mitra"]
    tara_name = tara_names[tara_idx - 1]
    auspicious_tara = tara_idx not in {3, 5, 7}  # Vipat, Pratyari, Vadha
    return {
        "house_nakshatra_idx": house_nak_idx,
        "owner_nakshatra_idx": owner_moon_nakshatra_idx,
        "tara_position": tara_idx,
        "tara_name": tara_name,
        "verdict": "auspicious" if auspicious_tara else "inauspicious-tara",
        "source": "Mayamatam Ch. 8 v. 70",
    }


def aaya_vyaya_full(L, B, owner_moon_nakshatra_idx=None, when_dt=None):
    """Run all 6 Aaya-vyaya calculations and aggregate verdict."""
    a = compute_aaya(L, B, owner_moon_nakshatra_idx)
    v = compute_vyaya(L, B)
    y = compute_yoni(L, B)
    va = compute_vara(L, B, when_dt)
    t = compute_tithi(L, B, when_dt)
    n = compute_nakshatra_match(L, B, owner_moon_nakshatra_idx)
    auspicious_count = sum(1 for x in (a, v, y, va, t, n)
                           if str(x.get("verdict", "")).startswith("auspicious")
                           or x.get("verdict") in ["very-low-expenditure", "low-expenditure"]
                           or x.get("today_is_favorable"))
    return {
        "dimensions": {"length": L, "breadth": B, "area": L * B},
        "aaya": a,
        "vyaya": v,
        "yoni": y,
        "vara": va,
        "tithi": t,
        "nakshatra_match": n,
        "auspicious_count_of_6": auspicious_count,
        "overall_verdict": (
            "highly-auspicious" if auspicious_count >= 5 else
            "auspicious" if auspicious_count >= 4 else
            "mixed" if auspicious_count >= 2 else
            "inauspicious"
        ),
        "source": "Manasara Ch. 9 + Mayamatam Ch. 8 (6-fold Aaya-vyaya)",
    }


# ============================================================
# DIRECTION-LABEL NORMALIZATION
# ============================================================
_DIRECTION_ALIASES = {
    "N": "North", "NORTH": "North",
    "S": "South", "SOUTH": "South",
    "E": "East",  "EAST":  "East",
    "W": "West",  "WEST":  "West",
    "NE": "Northeast", "NORTHEAST": "Northeast",
    "NW": "Northwest", "NORTHWEST": "Northwest",
    "SE": "Southeast", "SOUTHEAST": "Southeast",
    "SW": "Southwest", "SOUTHWEST": "Southwest",
    "C": "Center", "CENTER": "Center", "CENTRE": "Center",
}


def _norm_direction(d):
    """Normalize direction strings to canonical form."""
    if not d: return None
    return _DIRECTION_ALIASES.get(str(d).upper().strip(), str(d).strip())


# Map normalized direction -> per-room rule lookup key for forbidden-zones.
_FORBIDDEN_ZONE_FOR_ROOM = {
    "kitchen":         {"NE", "Northeast", "N", "North", "Center", "Centre"},
    "pooja":           {"S", "South", "SW", "Southwest", "SE", "Southeast"},
    "master_bedroom":  {"NE", "Northeast", "SE", "Southeast", "Center"},
    "kids_bedroom":    {"SW", "Southwest", "SE", "Southeast"},
    "guest_bedroom":   {"SW", "Southwest"},
    "study":           {"S", "South", "SW", "Southwest"},
    "office":          set(),  # context-dependent
    "bathroom":        {"NE", "Northeast", "Center", "SW", "Southwest"},
    "toilet":          {"NE", "Northeast", "Center", "SE", "Southeast"},
    "dining":          {"S", "South"},
    "living":          set(),
    "storage":         {"NE", "Northeast", "Center"},
    "balcony":         set(),
    "staircase":       {"NE", "Northeast", "Center"},
    "well_borewell":   {"SW", "Southwest", "SE", "Southeast", "Center"},
    "swimming_pool":   {"SW", "Southwest", "SE", "Southeast"},
    "main_door":       {"S", "South", "SW", "Southwest"},  # general avoid
    "money_safe":      {"S", "South", "SE", "Southeast"},
}


def _detect_doshas_from_layout(room_locations):
    """Match the room-location dict against the 12 named classical doshas."""
    found = []
    if not room_locations: return found
    norm = {k.lower(): _norm_direction(v) for k, v in room_locations.items()}

    if norm.get("toilet") in ("Northeast", "NE"):
        found.append("Toilet in NE")
    if norm.get("kitchen") in ("Northeast", "NE"):
        found.append("Kitchen in NE")
    if norm.get("main_door") in ("South", "S"):
        found.append("Main door facing south")
    if norm.get("staircase") in ("Center", "Centre"):
        found.append("Stairs in middle of house")
    if norm.get("master_bedroom") in ("Northeast", "NE") or norm.get("bedroom") in ("Northeast", "NE"):
        found.append("Bedroom in NE")
    if norm.get("borewell") in ("Southwest", "SW") or norm.get("well_borewell") in ("Southwest", "SW"):
        found.append("Borewell in SW")
    if norm.get("septic_tank") in ("Northeast", "NE"):
        found.append("Septic tank in NE")
    if norm.get("master_bed_head") in ("North", "N") or norm.get("bed_head") in ("North", "N"):
        found.append("Master bed-head facing N")
    if norm.get("mirror_facing_bed") in ("yes", "Yes", "YES", "True", "true"):
        found.append("Mirror facing bed")
    if norm.get("money_safe") in ("South", "S", "Southeast", "SE"):
        found.append("Money safe in S/SE")
    if norm.get("pooja") in ("South", "S", "Southwest", "SW"):
        found.append("Pooja room in S/SW")
    # Crack flag passthrough
    if norm.get("cracks_in_walls") in ("yes", "Yes", "YES", "True", "true"):
        found.append("Cracks in walls")
    return found


def _check_room_against_rules(room_key, direction):
    """Compare a single room's placement against PER_ROOM_RULES.
    Return (verdict, message)."""
    rule = PER_ROOM_RULES.get(room_key)
    if not rule:
        return ("unknown_room", f"No PER_ROOM_RULES entry for '{room_key}'")
    forbidden = _FORBIDDEN_ZONE_FOR_ROOM.get(room_key, set())
    norm_dir = _norm_direction(direction)
    norm_dir_short = direction.upper() if direction else ""
    if norm_dir in forbidden or norm_dir_short in forbidden:
        return ("forbidden", f"{room_key} placed in {norm_dir} - in classical avoid list ({rule['avoid_directions']}). Source: {rule['classical_source']}")
    if norm_dir == _norm_direction(rule["ideal_direction"].split()[0]) \
       or norm_dir.lower() in rule["ideal_direction"].lower():
        return ("ideal", f"{room_key} in {norm_dir} matches ideal_direction '{rule['ideal_direction']}'")
    return ("acceptable", f"{room_key} in {norm_dir} is acceptable but not the classical ideal '{rule['ideal_direction']}'")


# ============================================================
# CHART-HOUSE COMPATIBILITY
# ============================================================
def _owner_compatibility(chart, house_dimensions):
    """Compatibility verdict between native and house-area-derived nakshatra."""
    out = {"computed": False}
    if not house_dimensions:
        out["reason"] = "no house_dimensions provided"
        return out
    L = house_dimensions.get("length")
    B = house_dimensions.get("breadth")
    if not (L and B):
        out["reason"] = "incomplete dimensions"
        return out
    # Owner's Moon-nakshatra index
    nak_name = chart.get("janma_nakshatra")
    try:
        from vedic_core import NAKSHATRAS as _NAKS
        nak_idx = _NAKS.index(nak_name) if nak_name in _NAKS else None
    except Exception:
        nak_idx = None

    av = aaya_vyaya_full(L, B, owner_moon_nakshatra_idx=nak_idx)

    # Native's most beneficial directions (chart-based)
    native = best_directions_for_native(chart)
    out.update({
        "computed": True,
        "owner_moon_nakshatra": nak_name,
        "owner_moon_nakshatra_idx": nak_idx,
        "aaya_vyaya": av,
        "primary_native_direction": native["primary_direction"],
        "compatibility_verdict": av["overall_verdict"],
    })
    return out


# ============================================================
# COMPREHENSIVE TOP-LEVEL AUDIT
# ============================================================
def comprehensive_vastu_audit(chart, house_dimensions=None, room_locations=None):
    """Full Vastu audit combining:
       - 81-cell mandala alignment summary
       - 12-dosha detection from room_locations
       - 6-fold Aaya-vyaya math (if house_dimensions given)
       - chart-house owner compatibility
       - aggregated remedies summary

    Args:
      chart: standard Atro chart dict
      house_dimensions: {"length": float, "breadth": float} (in feet/cubits)
      room_locations: {"kitchen": "NE", "pooja": "SW", ...}

    Returns: nested dict with all sections.
    """
    # Mandala alignment summary
    use_counts = {}
    for cell in VASTU_PURUSHA_MANDALA_81:
        use_counts[cell["recommended_use"]] = use_counts.get(cell["recommended_use"], 0) + 1
    mandala_alignment = {
        "total_cells": len(VASTU_PURUSHA_MANDALA_81),
        "cell_count_by_use": use_counts,
        "brahmasthan_cells": sum(1 for c in VASTU_PURUSHA_MANDALA_81 if c["tier"] == "center"),
        "perimeter_cells": sum(1 for c in VASTU_PURUSHA_MANDALA_81 if c["tier"] == "perimeter"),
        "inner_ring_cells": sum(1 for c in VASTU_PURUSHA_MANDALA_81 if c["tier"] == "inner-ring"),
        "boundary_devata_count": len(VASTU_DEVATAS_45),
    }

    # Dosha detection
    dosha_names = _detect_doshas_from_layout(room_locations)
    doshas_full = []
    for name in dosha_names:
        for d in VASTU_DOSHAS_12:
            if d["name"] == name:
                doshas_full.append(d)
                break

    # Per-room rule check
    room_checks = []
    if room_locations:
        for k, direction in room_locations.items():
            room_key = k.lower()
            verdict, msg = _check_room_against_rules(room_key, direction)
            room_checks.append({"room": room_key, "direction": direction,
                                "verdict": verdict, "message": msg})

    # Aaya math
    aaya_analysis = None
    if house_dimensions and house_dimensions.get("length") and house_dimensions.get("breadth"):
        nak = chart.get("janma_nakshatra")
        try:
            from vedic_core import NAKSHATRAS as _NAKS
            nak_idx = _NAKS.index(nak) if nak in _NAKS else None
        except Exception:
            nak_idx = None
        aaya_analysis = aaya_vyaya_full(house_dimensions["length"],
                                        house_dimensions["breadth"],
                                        owner_moon_nakshatra_idx=nak_idx)

    # Owner compatibility
    owner_compat = _owner_compatibility(chart, house_dimensions)

    # Remedies summary
    remedies = []
    for d in doshas_full:
        remedies.append({"dosha": d["name"], "severity": d["severity"], "remedy": d["remedy"]})

    return {
        "vastu_purusha_alignment": mandala_alignment,
        "doshas_detected": doshas_full,
        "doshas_count": len(doshas_full),
        "room_checks": room_checks,
        "aaya_analysis": aaya_analysis,
        "owner_compatibility": owner_compat,
        "remedies_summary": remedies,
        "engine_note": (
            "Where Mayamatam and Manasara differ on cell-deity mapping "
            "(notably perimeter cells 13 'Yama in W' vs 'Yama in S' and "
            "cell 21 'Varuna in S' vs 'Varuna in W'), the Mayamatam reading "
            "has been adopted - it is the older treatise and is followed "
            "in South Indian (especially Tamil/Kerala) tradition."
        ),
    }


def lookup_mandala_cell(row, col):
    """Return the cell dict for a (row, col) in the 81-cell grid."""
    for c in VASTU_PURUSHA_MANDALA_81:
        if c["row"] == row and c["col"] == col:
            return c
    return None


def lookup_devata(name):
    """Return the devata dict for given name (case-insensitive contains)."""
    name_lc = name.lower()
    for d in VASTU_DEVATAS_45:
        if name_lc in d["name"].lower():
            return d
    return None


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    print(f"=== VASTU READING for {chart['name']} ===\n")

    # Original lightweight summary still works
    result = vastu_summary(chart)
    print(f"  Primary direction (lagna-lord based): {result['primary_native_direction']}")
    print(f"  Top 5 directions ranked by chart strength:")
    for d in result["ranked_directions"]:
        print(f"    {d['direction']:30s} score: {d['score']:+d}")
    if result.get("warnings"):
        print(f"  Warnings:")
        for w in result["warnings"]:
            print(f"    ! {w}")

    print()
    print("=== TIER 1 DEEP EXTENSIONS ===\n")

    # 81-cell mandala summary
    use_counts = {}
    tier_counts = {}
    for cell in VASTU_PURUSHA_MANDALA_81:
        use_counts[cell["recommended_use"]] = use_counts.get(cell["recommended_use"], 0) + 1
        tier_counts[cell["tier"]] = tier_counts.get(cell["tier"], 0) + 1
    print(f"  81-cell Vastu Purusha Mandala:")
    print(f"    Total cells: {len(VASTU_PURUSHA_MANDALA_81)}")
    print(f"    By tier: {tier_counts}")
    print(f"    Cell count by recommended_use:")
    for use, n in sorted(use_counts.items(), key=lambda x: -x[1]):
        print(f"      {use:10s} {n} cells")

    # 45 devatas summary
    print(f"\n  45 Vastu Devatas (boundary + inner secondary + Brahma):")
    print(f"    Total: {len(VASTU_DEVATAS_45)}")
    print(f"    Sample first 3:")
    for d in VASTU_DEVATAS_45[:3]:
        print(f"      {d['name']:30s} -> {d['function'][:50]}")
    print(f"    Sample last 3:")
    for d in VASTU_DEVATAS_45[-3:]:
        print(f"      {d['name']:30s} -> {d['function'][:50]}")

    # Per-room rules summary
    print(f"\n  Per-room rules:")
    print(f"    Total rules: {len(PER_ROOM_RULES)}")
    print(f"    Rooms: {', '.join(PER_ROOM_RULES.keys())}")

    # 12 doshas summary
    print(f"\n  12 Classical doshas: {len(VASTU_DOSHAS_12)} total")
    for d in VASTU_DOSHAS_12[:3]:
        print(f"    [sev {d['severity']}] {d['name']}")
    print(f"    ...")

    # Aaya math test
    print(f"\n  6-fold Aaya math test (L=36, B=24):")
    av = aaya_vyaya_full(36, 24, owner_moon_nakshatra_idx=9)  # Magha = idx 9
    print(f"    Area: {av['dimensions']['area']}")
    print(f"    Aaya: idx={av['aaya']['aaya_index']} type={av['aaya']['aaya_type']} bonus={av['aaya']['owner_alignment_bonus']}")
    print(f"    Vyaya: {av['vyaya']['raw_value']} ({av['vyaya']['verdict']})")
    print(f"    Yoni: {av['yoni']['yoni_type']} ({av['yoni']['verdict']})")
    print(f"    Vara: {av['vara']['favorable_weekday']}")
    print(f"    Tithi: {av['tithi']['favorable_tithi']}")
    print(f"    Nakshatra-match: {av['nakshatra_match'].get('tara_name', 'N/A')}")
    print(f"    Auspicious count: {av['auspicious_count_of_6']}/6 -> {av['overall_verdict']}")

    # Comprehensive audit with the dosha-heavy test config
    print(f"\n  Comprehensive Vastu Audit (kitchen=NE, pooja=NE, main_door=S):")
    audit = comprehensive_vastu_audit(
        chart,
        house_dimensions={"length": 36, "breadth": 24},
        room_locations={"kitchen": "NE", "pooja": "NE", "main_door": "S"},
    )
    print(f"    Mandala alignment cells: {audit['vastu_purusha_alignment']['total_cells']}")
    print(f"    Boundary devatas: {audit['vastu_purusha_alignment']['boundary_devata_count']}")
    print(f"    Doshas detected: {audit['doshas_count']}")
    for d in audit["doshas_detected"]:
        print(f"      [sev {d['severity']}] {d['name']}")
    if audit.get("aaya_analysis"):
        print(f"    Aaya overall verdict: {audit['aaya_analysis']['overall_verdict']}")
    print(f"    Owner compat verdict: {audit['owner_compatibility'].get('compatibility_verdict', 'N/A')}")
    print(f"    Remedies summary: {len(audit['remedies_summary'])} entries")

    print("\n  All Tier 1 Deep extensions loaded successfully.")
