"""Aspects Engine — Vedic special aspects (Drishti).

Vedic aspects (different from Western):
  - All planets aspect 7th house (180°)
  - MARS:    additional 4th + 8th aspects (90°, 210°)
  - JUPITER: additional 5th + 9th aspects (120°, 240°)
  - SATURN:  additional 3rd + 10th aspects (60°, 270°)
  - RAHU/KETU: 5th + 9th (some traditions also give 7th)

Source: BPHS Ch. 26 (Drishti chapter), Saravali Ch. 36.
"""
import sys
sys.path.insert(0, ".")

PLANETS_REGULAR = ["Sun","Moon","Mercury","Venus"]  # only 7th aspect
SPECIAL_ASPECT_PLANETS = {
    "Mars":    [4, 7, 8],     # 4th, 7th, 8th houses from itself
    "Jupiter": [5, 7, 9],
    "Saturn":  [3, 7, 10],
    "Rahu":    [5, 7, 9],
    "Ketu":    [5, 7, 9],
}


def _h(pos, p): return pos[p]["house"] if p in pos else None
def _occ(pos, h): return [p for p, pd in pos.items() if pd["house"] == h]


def aspects_from(pos, planet):
    """Return list of houses aspected by `planet`."""
    h = _h(pos, planet)
    if h is None: return []
    if planet in SPECIAL_ASPECT_PLANETS:
        offsets = SPECIAL_ASPECT_PLANETS[planet]
    elif planet in PLANETS_REGULAR:
        offsets = [7]
    else:
        offsets = [7]
    return [((h + offset - 2) % 12) + 1 for offset in offsets]


def planets_aspecting_house(pos, target_house):
    """Return list of planets that aspect `target_house`."""
    out = []
    for p in pos:
        aspected = aspects_from(pos, p)
        if target_house in aspected:
            out.append(p)
    return out


def planets_aspecting_planet(pos, target_planet):
    """Return list of planets aspecting another planet (i.e. the house it sits in)."""
    if target_planet not in pos: return []
    target_house = pos[target_planet]["house"]
    aspecting = planets_aspecting_house(pos, target_house)
    return [p for p in aspecting if p != target_planet]


# ================================================================
# CLASSICAL ASPECT INTERPRETATIONS
# ================================================================
ASPECT_EFFECTS = {
    # Saturn aspects (most malefic generally)
    ("Saturn", "Sun"):     ("Father affliction, ego-restriction, slow career, eye/heart watch", 4, "BPHS Ch. 26"),
    ("Saturn", "Moon"):    ("Vish Yoga (poison), depression-tendency, mother-stress, mental heaviness", 5, "Saravali, classical Vish Yoga"),
    ("Saturn", "Mars"):    ("Conflict with discipline, accidents, surgery, frustration, blood-pressure", 4, "BPHS Ch. 26"),
    ("Saturn", "Mercury"): ("Mature thinking, sometimes harsh speech, careful planning, slow but deep", 3, "BPHS Ch. 26"),
    ("Saturn", "Jupiter"): ("Wisdom + restriction — slow dharmic development, late-life rewards", 3, "BPHS"),
    ("Saturn", "Venus"):   ("Marriage delays, mature love, karmic relationships, tasteful but reserved life", 3, "BPHS"),

    # Mars aspects (energizing/conflicting)
    ("Mars", "Sun"):     ("Strong willpower, aggression, leadership, ego-aggression", 3, "BPHS Ch. 26"),
    ("Mars", "Moon"):    ("Emotional intensity, anger, courage, possible bleeding/blood-pressure", 3, "BPHS"),
    ("Mars", "Mercury"): ("Sharp speech, debate skill, aggressive intelligence, possible accidents", 3, "Saravali"),
    ("Mars", "Jupiter"): ("Dharmic warrior, ethical action, military/leadership-philosophy", 3, "BPHS"),
    ("Mars", "Venus"):   ("Passion, attraction, possible relationship friction or competitive love", 3, "BPHS"),
    ("Mars", "Saturn"):  ("Compounded difficulty — anger meets restriction; surgery, accidents", 4, "BPHS"),

    # Jupiter aspects (most benefic generally)
    ("Jupiter", "Sun"):     ("Authority + wisdom, dharmic leadership, respected father quality", 4, "BPHS Ch. 26"),
    ("Jupiter", "Moon"):    ("Gaja-Kesari-like emotional wisdom, mother grace, generous mind", 5, "Phaladeepika"),
    ("Jupiter", "Mars"):    ("Righteous courage, ethical warrior, leadership with wisdom", 4, "BPHS"),
    ("Jupiter", "Mercury"): ("Saraswati-like learning + speech, scholarly excellence, advisor quality", 4, "BPHS"),
    ("Jupiter", "Venus"):   ("Wisdom + comfort, dharmic love, balanced marriage, ethical aesthetics", 4, "BPHS"),
    ("Jupiter", "Saturn"):  ("Mature dharma, structured spirituality, late-life wisdom", 3, "BPHS"),

    # Rahu aspects (foreign/unconventional)
    ("Rahu", "Sun"):     ("Father confusion, ego-issues, foreign authority, eclipse-like effect on identity", 4, "Phaladeepika"),
    ("Rahu", "Moon"):    ("Mental anxiety, mother-issues, foreign attractions, hypnotic charm", 4, "Phaladeepika"),
    ("Rahu", "Mars"):    ("Angarak-like effect, explosive energy, foreign battles, addictive risk-taking", 4, "Phaladeepika"),
    ("Rahu", "Mercury"): ("Foreign-language, technology, deception-risk, unconventional communication", 3, "Phaladeepika"),
    ("Rahu", "Jupiter"): ("Guru-Chandala — wisdom corrupted by unorthodox influence, cult-attraction-risk", 3, "Phaladeepika"),
    ("Rahu", "Venus"):   ("Foreign romance, intense attractions, unconventional marriage, sensuality", 3, "Phaladeepika"),
    ("Rahu", "Saturn"):  ("Karmic burden, slow grinding, occult-research success", 3, "Phaladeepika"),

    # Ketu aspects (detachment/spiritual)
    ("Ketu", "Sun"):     ("Detachment from authority, ego-dissolution, spiritual identity-quest", 3, "Phaladeepika"),
    ("Ketu", "Moon"):    ("Emotional detachment, intuitive depth, mother-distance, psychic openings", 3, "Phaladeepika"),
    ("Ketu", "Mars"):    ("Asceticism + intensity, spiritual warrior, sudden energy-shifts", 3, "Phaladeepika"),
    ("Ketu", "Mercury"): ("Withdrawn from chatter, mystical writing, research-orientation", 3, "Phaladeepika"),
    ("Ketu", "Jupiter"): ("Spiritual maturity, dharmic detachment, naturally philosophical", 3, "Phaladeepika"),
    ("Ketu", "Venus"):   ("Detachment from comforts, spiritual love, marriage-completion karma", 3, "Phaladeepika"),
}


def detect_significant_aspects(chart, severity_min=3):
    """Detect all significant Vedic aspects between planets."""
    pos = chart["positions"]
    out = []
    for aspecting, target in ASPECT_EFFECTS:
        if aspecting not in pos or target not in pos: continue
        target_h = pos[target]["house"]
        aspected_houses = aspects_from(pos, aspecting)
        if target_h not in aspected_houses: continue
        # Don't count conjunction as aspect
        if pos[aspecting]["house"] == target_h: continue
        effect, severity, source = ASPECT_EFFECTS[(aspecting, target)]
        if severity < severity_min: continue
        out.append({
            "aspecting": aspecting,
            "target": target,
            "aspecting_house": pos[aspecting]["house"],
            "target_house": target_h,
            "effect": effect,
            "severity": severity,
            "source": source,
        })
    return out


def aspect_summary(chart):
    aspects = detect_significant_aspects(chart, severity_min=3)
    if not aspects:
        return "No significant aspects detected."
    lines = [f"=== {len(aspects)} SIGNIFICANT ASPECTS ===\n"]
    for a in sorted(aspects, key=lambda x: -x["severity"]):
        sev = "*" * a["severity"] + "." * (5 - a["severity"])
        lines.append(f"[{sev}] {a['aspecting']} (H{a['aspecting_house']}) aspects {a['target']} (H{a['target_house']})")
        lines.append(f"        {a['effect']}")
        lines.append(f"        Source: {a['source']}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print(aspect_summary(chart))
