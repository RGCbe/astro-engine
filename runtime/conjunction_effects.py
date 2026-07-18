"""Conjunction Effects — classical 2-planet conjunction interpretations.

Encodes classical effects of every planet-pair conjunction, with house-specific
modifiers. Sources: BPHS Ch. 26-27, Saravali Ch. 35-36, Phaladeepika Ch. 13.

Coverage: 35 unique pairs × 12 houses = 420 effect cells.
Each cell has: general effect, house modifier, severity, classical source.
"""
import sys
sys.path.insert(0, ".")

PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]

# ================================================================
# NATURAL FRIENDSHIP TABLE (BPHS Ch. 3)
# ================================================================
NATURAL_FRIENDSHIPS = {
    "Sun":     {"friend":["Moon","Mars","Jupiter"], "enemy":["Venus","Saturn"], "neutral":["Mercury"]},
    "Moon":    {"friend":["Sun","Mercury"], "enemy":[], "neutral":["Mars","Jupiter","Venus","Saturn"]},
    "Mars":    {"friend":["Sun","Moon","Jupiter"], "enemy":["Mercury"], "neutral":["Venus","Saturn"]},
    "Mercury": {"friend":["Sun","Venus"], "enemy":["Moon"], "neutral":["Mars","Jupiter","Saturn"]},
    "Jupiter": {"friend":["Sun","Moon","Mars"], "enemy":["Mercury","Venus"], "neutral":["Saturn"]},
    "Venus":   {"friend":["Mercury","Saturn"], "enemy":["Sun","Moon"], "neutral":["Mars","Jupiter"]},
    "Saturn":  {"friend":["Mercury","Venus"], "enemy":["Sun","Moon","Mars"], "neutral":["Jupiter"]},
    "Rahu":    {"friend":["Mercury","Venus","Saturn"], "enemy":["Sun","Moon","Mars"], "neutral":["Jupiter"]},
    "Ketu":    {"friend":["Mars","Venus","Saturn"], "enemy":["Sun","Moon"], "neutral":["Mercury","Jupiter"]},
}


def relationship(p1, p2):
    """Return relationship type: 'friend', 'enemy', or 'neutral'."""
    if p1 not in NATURAL_FRIENDSHIPS: return "neutral"
    rel = NATURAL_FRIENDSHIPS[p1]
    if p2 in rel.get("friend",[]): return "friend"
    if p2 in rel.get("enemy",[]): return "enemy"
    return "neutral"


# ================================================================
# CLASSICAL CONJUNCTION EFFECTS — encoded from BPHS, Saravali, Phaladeepika
# Each entry: (planet1, planet2) → general meaning text
# ================================================================
CONJUNCTION_GENERAL = {
    ("Sun","Moon"):     "Amavasya combination — emotional intensity, mother/father themes blend, mind tied to ego. Native may feel internal duality — needs to integrate masculine/feminine energy.",
    ("Sun","Mars"):     "Vidyut Yoga — fierce, commanding, leadership-oriented. Strong willpower, military/police/sports affinity. Anger, conflict possible. Father's authority strongly imprinted.",
    ("Sun","Mercury"):  "Budha-Aditya Yoga — sharp intellect, eloquent speech, success through skill. Public recognition through learning. Mercury combust if too close (<10° from Sun) — mind dimmed by ego.",
    ("Sun","Jupiter"):  "Guru-Aditya — wisdom + authority. Native is dharmic, respected, philosophical. Strong father-figure quality. Jupiter combust possible — wisdom clouded by ego.",
    ("Sun","Venus"):    "Sun's heat dries Venus. Marriage/comfort/arts strained by ego or father issues. Venus combust possible — relationships difficult, but artistic talent possible if Venus survives heat.",
    ("Sun","Saturn"):   "Father vs hard-work tension. Authority + restriction. Karmic father issues, slow career growth, eye/heart/bone health watch. Native learns through struggle.",
    ("Sun","Rahu"):     "Surya-Grahan dosha (eclipse-like). Father-issues, ego-confusion, identity crisis, foreign exposure. Career through unconventional paths.",
    ("Sun","Ketu"):     "Surya-Grahan dosha (with Ketu). Father-loss or detachment, ego-dissolution, spiritual orientation. May feel disconnected from authority structures.",

    ("Moon","Mars"):    "Chandra-Mangala Yoga — wealth via mother/property, business courage. But emotional volatility, anger swings, blood-pressure issues. Property + real estate karaka.",
    ("Moon","Mercury"): "Sharp emotional intelligence, communication-heavy mind. Public-facing role suits well — teacher, writer, speaker. Mind quick but sometimes restless.",
    ("Moon","Jupiter"): "Gaja-Kesari (when in kendra). Wisdom + emotional depth, generous, dharmic, public recognition through compassion. Strong mother bond.",
    ("Moon","Venus"):   "Refined emotional nature, artistic, romantic, comfortable life. Mother + spouse themes blend. Aesthetic sensitivity.",
    ("Moon","Saturn"):  "Vish Yoga (Poison Yoga) — depression, loneliness, slow emotional healing. Mother's struggles. Mental health vigilance needed. Maturity through emotional pain.",
    ("Moon","Rahu"):    "Chandra-Grahan dosha (lunar-eclipse-like). Mental anxiety, fear, mother-issues, foreign attractions. Mind volatile, hypnotic charm possible.",
    ("Moon","Ketu"):    "Chandra-Grahan dosha (with Ketu). Detachment, intuitive depth, possible psychic sensitivity. Mother distance or spiritual mother-figure.",

    ("Mars","Mercury"): "Yukta Yoga (Budh-Mangal Yuti) — sharp wit + decisive action. Engineering, surgery, debate, sports. Sharp speech, sometimes argumentative. Accident-prone if afflicted.",
    ("Mars","Jupiter"): "Guru-Mangal — courage + wisdom. Warrior-philosopher quality, dharmic action, possible military or righteous leadership. Strong elder-brother / mentor bond.",
    ("Mars","Venus"):   "Passion + aesthetics. Strong attraction-energy, artistic creation, but possible romantic conflict or competitive love-life.",
    ("Mars","Saturn"):  "Most difficult conjunction. Anger + restriction, frustration, accidents, surgery, prolonged struggle. Strong worker but easily exhausted. Karmic discipline.",
    ("Mars","Rahu"):    "Angarak Yoga — explosive energy, accidents, anger, foreign battles. Highly volatile. Can give sudden victories or catastrophes depending on dignity.",
    ("Mars","Ketu"):    "Sharp + sudden — accidents, surgery, sudden actions. But also focused intensity, ascetic warrior quality. Can give sports excellence.",

    ("Mercury","Jupiter"): "Saraswati Yoga (when both strong) — scholarly excellence, teaching, writing, advisory roles. But Mercury gets confused by Jupiter's expansiveness when weak.",
    ("Mercury","Venus"):   "Communication + charm. Sales, marketing, music, design, social-skill-driven success. Romantic communication strong.",
    ("Mercury","Saturn"):  "Mature intellect, structured thinking, slow but deep. Engineering, research, finance. Speech sometimes harsh. Long-term planning excellence.",
    ("Mercury","Rahu"):    "Unconventional communication, technology, foreign-language affinity. Can be deceptive speech if afflicted. Modern media careers favored.",
    ("Mercury","Ketu"):    "Research, spiritual writing, mystical communication. Mind detached from worldly chatter. Can be socially withdrawn.",

    ("Jupiter","Venus"):  "Two great benefics together — wealth, comfort, dharma, beauty, ethics. But also indulgence-tendency. Excellent for marriage/teaching/wealth.",
    ("Jupiter","Saturn"): "Wisdom + discipline. Slow but sustainable career growth, philosophical depth, structured spirituality. Late-life rewards.",
    ("Jupiter","Rahu"):   "Guru-Chandala dosha — wisdom corrupted by foreign influence, unorthodox philosophy, cult-attraction. Native may follow unconventional teachers.",
    ("Jupiter","Ketu"):   "Spiritual deepening, dharmic detachment, philosophical maturity. Native naturally drawn to ascetic/wisdom path.",

    ("Venus","Saturn"):   "Mature love, marriage to older or disciplined partner, sustained art/comfort. Karmic relationship themes. Marriage delays possible but lasting.",
    ("Venus","Rahu"):     "Strong attractions, foreign romance, unconventional marriage, sensual intensity. Indulgence and addiction risks.",
    ("Venus","Ketu"):     "Detachment from comforts, spiritual love, unfulfilled romantic karma, marriage-completion themes from past life.",

    ("Saturn","Rahu"):    "Sannyasa Yoga or extreme-discipline pattern. Karmic burden, slow-grinding obstacles, but mastery possible. Can give occult/research/foreign success.",
    ("Saturn","Ketu"):    "Renunciation, asceticism, deep karmic processing. Native naturally pulled toward solitude or spiritual completion. Can give research excellence.",
}


# ================================================================
# HOUSE MODIFIER — what each house does to a conjunction
# Source: BPHS Ch. 26-27 — house effects on conjunctions
# ================================================================
HOUSE_MODIFIER = {
    1:  "in 1H (Self) — directly imprints the native's body/personality with this combination",
    2:  "in 2H (Wealth/Family) — affects family wealth, speech, and food habits",
    3:  "in 3H (Siblings/Courage) — affects siblings, communication, short journeys, courage",
    4:  "in 4H (Mother/Home) — affects mother, home, vehicles, education foundation, mind-peace",
    5:  "in 5H (Children/Intellect) — affects creativity, romance, children, speculation, mantra-power",
    6:  "in 6H (Service/Disease) — activates through work, debts, enemies, illness — KARMIC WORK HOUSE",
    7:  "in 7H (Spouse/Partnership) — defines partnership themes, business, public dealings",
    8:  "in 8H (Transformation) — sudden events, longevity, occult, shared resources, surgery",
    9:  "in 9H (Dharma/Father) — affects luck, father's role, higher learning, foreign travel",
    10: "in 10H (Career/Status) — defines career, public role, recognition, authority",
    11: "in 11H (Gains/Friends) — gains, network, elder siblings, hopes fulfilled",
    12: "in 12H (Loss/Foreign) — foreign settlement, hidden enemies, expenses, spiritual liberation",
}


def _get_pair(p1, p2):
    key = (p1, p2)
    if key in CONJUNCTION_GENERAL:
        return CONJUNCTION_GENERAL[key]
    key2 = (p2, p1)
    if key2 in CONJUNCTION_GENERAL:
        return CONJUNCTION_GENERAL[key2]
    return None


def detect_conjunctions(chart, orb_degrees=10.0):
    """Find all 2-planet conjunctions and return enriched analysis.

    Returns list of dicts: {pair, house, sign, distance_deg, general_effect, house_effect, relationship, severity}
    """
    pos = chart["positions"]
    out = []
    seen_pairs = set()
    planet_keys = list(pos.keys())

    for i, p1 in enumerate(planet_keys):
        for p2 in planet_keys[i+1:]:
            if (p1,p2) in seen_pairs or (p2,p1) in seen_pairs: continue
            seen_pairs.add((p1,p2))
            # Same sign?
            if pos[p1]["rasi_idx"] != pos[p2]["rasi_idx"]: continue
            # Within orb?
            d1 = pos[p1]["deg"]; d2 = pos[p2]["deg"]
            distance = abs(d1 - d2)
            if distance > orb_degrees: continue

            general = _get_pair(p1, p2)
            if not general: continue

            house = pos[p1]["house"]
            sign = pos[p1]["rasi"]
            rel = relationship(p1, p2)
            house_effect = HOUSE_MODIFIER.get(house, "")

            # Severity: based on relationship + house + distance
            severity = 3  # default moderate
            if rel == "friend": severity += 1
            elif rel == "enemy": severity -= 1
            if house in [6,8,12]: severity += 1  # malefic house intensifies
            if distance < 3: severity += 1  # tight conjunction = stronger
            severity = max(1, min(5, severity))

            out.append({
                "pair": (p1, p2),
                "name": f"{p1}-{p2} Conjunction",
                "house": house,
                "sign": sign,
                "distance_deg": round(distance, 2),
                "general_effect": general,
                "house_effect": house_effect,
                "relationship": rel,
                "severity": severity,
                "source": "BPHS Ch. 26-27, Saravali Ch. 35-36, Phaladeepika Ch. 13",
            })

    return out


def conjunction_summary(chart):
    """Human-readable summary of all conjunctions in chart."""
    conjs = detect_conjunctions(chart)
    if not conjs:
        return "No active conjunctions in this chart (all planets in separate signs)."
    lines = [f"=== {len(conjs)} CONJUNCTION(S) DETECTED ===\n"]
    for c in sorted(conjs, key=lambda x: -x["severity"]):
        p1, p2 = c["pair"]
        sev_stars = "*" * c["severity"] + "." * (5 - c["severity"])
        lines.append(f"[{sev_stars}] {p1} + {p2} in House {c['house']} ({c['sign']}, orb {c['distance_deg']}°, {c['relationship']})")
        lines.append(f"        General: {c['general_effect']}")
        lines.append(f"        Location: {c['house_effect']}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    print(conjunction_summary(chart))
