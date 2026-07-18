"""Nadi Full — 108-cell narrative grid + 14 specific 2-planet rules + karaka logic.

Source-style: Bhrigu Nadi, Chandra Kala Nadi, Dhruva Nadi, Saptarishi Nadi, Sukra Nadi.

DISCLOSURE: The 108 cells in NADI_CELLS and the 14 entries in TWO_PLANET_RULES
are NOT literal translations of palm-leaf Nadi manuscripts. They synthesize the
spirit, tone, and signifier-language of the Nadi tradition (especially Bhrigu
and Chandra-Kala styles) for each (planet, house) and (planet1, planet2, sign)
combination. Use them for engine-output flavor, not as scholarly Nadi citations.

Provides:
  - nadi_cell_reading(planet, house) -> short Naadi-style sentence (9×12=108 cells)
  - full_nadi_narrative(chart) -> dict mapping (planet -> placement) for all 9 planets
  - detect_two_planet_rules(chart) -> 14 specific conjunctions (e.g. Sun-Saturn)
  - karaka_readings(chart) -> per-planet karaka context (very_strong/strong/mixed/weak/neutral)
  - complete_nadi_analysis(chart) -> all-of-the-above as one dict
"""
import sys
sys.path.insert(0, ".")
from vedic_core import (
    RASIS, RASI_LORDS, DIGNITIES,
    NATURAL_BENEFICS, NATURAL_MALEFICS,
    HOUSE_THEMES, PLANET_ARCHETYPES,
)


# ============================================================
# 108 NADI CELLS (9 planets × 12 houses)
# Each cell = one Bhrigu-Nadi style sentence describing that placement
# ============================================================
NADI_CELLS = {
    # =========== SUN (father, soul, authority) ===========
    "Sun": {
        1:  "The native carries the father's pride in his very body — soul-presence visible in face and posture; ego strong but soft when honored.",
        2:  "Wealth comes through the father or through commanding speech; harsh words can wound family. Sun in 2H gives status-money rather than savings.",
        3:  "The native himself is the shining elder among siblings — hands carry ancestral fire; courage sometimes flares as anger.",
        4:  "Father shines distant rather than close — heart-house holds inherited honor but emotional intimacy is hard. Mother dimmed by father's authority.",
        5:  "Children carry father's name; native's intellect is regal. Speculation favors gold/leadership ventures, not subtle play.",
        6:  "Native serves under royal-grade authority — government, defense, hospital — and his own ego becomes his enemy if not refined.",
        7:  "Marriage brings authority-figure as partner; spouse may be older or higher-status. Public-facing life: native is seen.",
        8:  "Father's longevity carries karma — son inherits transformation through father's struggle. Native dies famously or invisibly, never quietly.",
        9:  "Father is the dharmic guru of the native; native carries forward family's spiritual lineage; foreign travel for higher dharma possible.",
        10: "Native rises to king-level role; profession aligns with leadership, government, medicine, or solar-craft like gold/jewelry.",
        11: "Income via authority, government, or father's networks; eldest siblings prosper. Status-money flows.",
        12: "Native's self is partly hidden — meditative or foreign; father is distant geographically or emotionally. Solitude polishes the soul.",
    },

    # =========== MOON (mother, mind, emotion) ===========
    "Moon": {
        1:  "Mind shapes the body — moods read on the face. Native is sensitive, charming, emotionally fluent; moonlight in his presence.",
        2:  "Wealth flows like water — comes and goes; family is the mother's circle; speech soft and persuasive.",
        3:  "Younger sibling close to native; courage is emotional rather than aggressive; native writes/sings what he feels.",
        4:  "Mother is the central anchor of life; home is sanctuary; comforts gather around the native; mid-life property abundance possible.",
        5:  "Romantic, fertile mind; children come gently; creativity flows through the heart. Affection-driven life.",
        6:  "Mother's health worry-mark; native serves through caretaking, hospitality, food. Anxious mind unless trained.",
        7:  "Beautiful, emotional partner; marriage is heart-bonded but moody. Public is the native's stage.",
        8:  "Emotional transformation through losses; inherited emotional patterns; deep sea of subconscious to navigate.",
        9:  "Soft devotional dharma; mother is the spiritual root; pilgrimages with family bring blessing.",
        10: "Career involves public, hospitality, food, or fluid-things; native rises by emotional connection with people.",
        11: "Income via women, public, food, or maternal-line networks; many friends, fluctuating gains.",
        12: "Native sleeps deeply or restlessly; mother's energy distant in some way; foreign land soothes the mind.",
    },

    # =========== MARS (brother, courage, action) ===========
    "Mars": {
        1:  "The body is fast, aggressive, athletic; native walks with edge. Tongue sharp; heat in blood. Mars-lagna gives commander-energy.",
        2:  "Sharp speech — can wound or persuade; family disputes possible; wealth via force-of-action like real estate, defense, surgery.",
        3:  "Strongest sibling-action; native is the bold one; warrior-mind; younger siblings successful or in conflict.",
        4:  "Mother experiences hardness; home environment intense; property gained through effort or struggle.",
        5:  "Children are bold, sometimes accident-prone; speculation goes hot/cold; sharp intellect, military-grade focus.",
        6:  "Mars in own karma-house — native defeats enemies, debt, disease; surgical recovery; competitive professions favored.",
        7:  "Manglik signature — passionate but contentious marriage; partner intense or difficult; possible delays.",
        8:  "Risk of accidents, surgeries, or violent transformations; inherited property fights; deep transformation through Mars-pain.",
        9:  "Adventurous father; native travels with risk; sports/military pilgrimage. Dharma fought for, not received.",
        10: "Action-career — military, surgery, sports, real estate, engineering. Native climbs by determination and conflict.",
        11: "Gains through younger brothers, action, sports, real estate; income through battles won.",
        12: "Hidden enemies, hospital expense, military-foreign service. Mars in 12 secretly drains energy; sleep affected.",
    },

    # =========== MERCURY (intellect, speech, siblings) ===========
    "Mercury": {
        1:  "Quick mind in body; youthful appearance; native speaks well, writes well, learns fast. The thinker.",
        2:  "Wealth via communication — writing, teaching, sales, commerce. Family-language gift; many tongues possible.",
        3:  "Many siblings, communicative network; native is the messenger; writer-traveler-trader.",
        4:  "Educated mother; native loves books and study; home filled with conversations. Property paperwork-related.",
        5:  "Brilliant intellect; multiple children; speculation through analysis; teaching/writing/coding gift.",
        6:  "Sharp at solving disputes; legal-medical-IT service career; analytical mind for problems; nervous health if stressed.",
        7:  "Younger or intellectual spouse; partnership-driven business; communication-based marriage.",
        8:  "Hidden intellect; research, occult, investigation, mathematics, esoteric knowledge; secret communications.",
        9:  "Sharp dharmic mind; teacher-of-philosophy; foreign-travel for learning; multilingual.",
        10: "Career in commerce, communication, media, IT, journalism, accounting, teaching.",
        11: "Income via writing, technology, commerce, broker-work; many friends through ideas.",
        12: "Dreams and inner-mind active; foreign-language work; journalism abroad; hospital-administration possible.",
    },

    # =========== JUPITER (wisdom, children, dharma) ===========
    "Jupiter": {
        1:  "Wisdom in the body — round, dignified, hopeful; the natural teacher. Lagna-Jupiter is born guru.",
        2:  "Wealth, family, scholar-speech; native is the family's voice of dharma; rich foods and traditional richness.",
        3:  "Wise siblings; native is the elder-counselor; courage tempered by wisdom; teaching-writing skill.",
        4:  "Educated mother; spiritual home; vehicles, comforts, mid-life abundance; native's home is a refuge.",
        5:  "Children blessed; dharmic mind; wise advisor; speculation through long-term wisdom; teaching profession favored.",
        6:  "Wisdom defeats enemies; but some wisdom-significations strained — challenges in advisory roles.",
        7:  "Wise dharmic spouse; marriage is a temple; partner of higher status; dharma in partnership.",
        8:  "Hidden wisdom; occult-research, ayurveda, kundalini studies; transformation through knowledge.",
        9:  "Strong dharma — natural teacher of higher truths; pilgrimages, gurus, foreign-spiritual travel; auspicious father.",
        10: "Profession: teacher, judge, advisor, financier, religious leader; native carries wisdom into world.",
        11: "Wisdom converts to wealth; income from advisory, education, finance; many helpful elders/teachers.",
        12: "Spiritual liberation in this life; ashram-leaning; foreign-pilgrimage; donation-driven life.",
    },

    # =========== VENUS (spouse, beauty, comfort) ===========
    "Venus": {
        1:  "Beauty in the body; charm, symmetry, art-loving; native draws others; appearance-focused life.",
        2:  "Sweet voice; wealth in arts/luxury/jewelry; family is gentle; speech persuasive and pleasant.",
        3:  "Artistic siblings; native is the creative one; courage in creative ventures.",
        4:  "Beautiful home, mother, vehicles; comfortable life; arts decorate the inner sanctum.",
        5:  "Romantic life rich; gifted children; speculation in arts; love-marriage possible.",
        6:  "Service in beauty/arts/luxury industry; debts via women or pleasure; reproductive-health watchpoint.",
        7:  "Beautiful, devoted spouse; love-marriage; partnership business in arts/luxury; venerated public partner.",
        8:  "Sensual transformation; secret romance; reproductive-occult themes; possible inheritance of art/jewels.",
        9:  "Dharmic beauty; pilgrimage with spouse; foreign-arts study; spouse from afar possible.",
        10: "Career in arts, fashion, beauty, luxury, hospitality, design, music, film.",
        11: "Income via women, arts, luxury; gains through partnerships and elegant networks.",
        12: "Foreign romance; comforts in hidden/private life; bedroom-pleasure; sleep with luxury.",
    },

    # =========== SATURN (karma, longevity, discipline) ===========
    "Saturn": {
        1:  "Body weighed down with karma; serious face; old soul; slow but steady; disciplined posture.",
        2:  "Slow accumulation of wealth; harsh family-words possible; chronic family-pattern karma.",
        3:  "Karmic siblings; effort-courage rather than impulsive; disciplined writing; younger sibling's karma.",
        4:  "Heavy heart in early life; mother distant or austere; old or inherited home; property after struggle.",
        5:  "Late children, disciplined intellect, austere creativity; speculation requires patience; teaching favored.",
        6:  "Long-fought victories; disciplined service; native overcomes enemies, debt, disease through endurance.",
        7:  "Late marriage; mature/older partner; karmic partnership; serious bond.",
        8:  "Long longevity through karmic mastery; chronic transformation; ayurveda/yoga aids.",
        9:  "Severe father-karma; dharma earned through trial; pilgrimages with austerity; disciplined spirituality.",
        10: "Long, structured career; engineering, mining, justice, judiciary, bureaucracy, large institutions.",
        11: "Income through long-effort; eldest sibling has Saturn karma; gains slowly accumulate.",
        12: "Hospital, ashram, foreign-prison-or-monastery; long sleep-quality concern; spiritual discipline in solitude.",
    },

    # =========== RAHU (foreign, technology, sudden) ===========
    "Rahu": {
        1:  "Identity shifts; foreign or unconventional self; smoke around the body; mysterious charisma; risky body karma.",
        2:  "Foreign wealth; smoke in family; speech non-traditional; food-restrictions or addictions possible.",
        3:  "Step- or distant siblings; courage to break norms; communication crosses cultures.",
        4:  "Foreign home; mother-line karma; vehicles imported; emotional intensity; possible mother-distance.",
        5:  "Unconventional intellect; speculative-tech; adoption/IVF for children; karmic-romance.",
        6:  "Native defeats foreign enemies; legal-immigration cases; sudden-illness with unknown cause; service in foreign sector.",
        7:  "Foreign or inter-cultural partner; sudden marriage; obsessive love; partnership crosses borders.",
        8:  "Sudden transformations; chronic mysterious health; foreign-property; deep occult attraction.",
        9:  "Foreign dharma; non-traditional teacher; pilgrimage abroad; father non-traditional or distant.",
        10: "Tech-career, foreign-career, films, aviation, drugs/chemicals, modern unconventional industry.",
        11: "Foreign-income, online-business, technology gains; eldest brother abroad; sudden gains and sudden losses.",
        12: "Foreign settlement; eccentric sleep; mystical experiences; possible psychiatric karma; mature liberation through solitude.",
    },

    # =========== KETU (detachment, past karma, moksha) ===========
    "Ketu": {
        1:  "Self-detached body; spiritual aura; native lives lightly; past-life karmic intensity in early years.",
        2:  "Detached from family wealth; speech terse or silent; food-discipline or fasting possible.",
        3:  "Detached siblings or sibling-loss; courage of the renunciate; spiritual writing possible.",
        4:  "Detached from home; mother's spiritual karma; foreign or simple home; emotional withdrawals.",
        5:  "Children spiritual or distant; intellect detached from mainstream; mantra/yantra/jyotish gifts.",
        6:  "Defeats hidden enemies; spiritual healing; karmic disease patterns dissolve through awareness.",
        7:  "Spiritual partnership or separation; partner detached, ascetic, or business-only; possible widow-pattern.",
        8:  "Past-life-karma directly accessible; psychic gifts; transformation through Ketu's fire; ayurveda mastery.",
        9:  "Ketu-dharma — the renunciate guru-line; past-life dharmic skill; teacher of inner truths; foreign-pilgrim.",
        10: "Career behind-scenes; research, occult, healing, energy-work; reluctant fame.",
        11: "Detached from gains; income unstable or spiritual; eldest sibling renunciate or distant.",
        12: "Moksha-karma directly active; deep meditation; foreign ashram; sleep merges with samadhi; bedroom-spirit-life.",
    },
}


def nadi_cell_reading(planet, house):
    """Return the Nadi-cell sentence for given (planet, house)."""
    pt = NADI_CELLS.get(planet, {})
    return pt.get(house, f"{planet} in House {house} — placement noted, no specific Naadi sentence available.")


def full_nadi_narrative(chart):
    """Generate full 9-planet narrative for a given chart.
    Returns: dict {planet: {"house": h, "rasi": r, "reading": str}}"""
    pos = chart["positions"]
    out = {}
    for planet, pd in pos.items():
        h = pd.get("house"); r = pd.get("rasi")
        out[planet] = {
            "house": h,
            "rasi": r,
            "reading": nadi_cell_reading(planet, h),
            "archetype": PLANET_ARCHETYPES.get(planet, ""),
            "house_theme": HOUSE_THEMES.get(h, ""),
        }
    return out


# ============================================================
# 13 SPECIFIC 2-PLANET CONJUNCTION RULES
# ============================================================
TWO_PLANET_RULES = {
    "Sun_Saturn": "Father carries hardship that becomes the native's life-lesson. Authority is gained slowly. Bones, spine, eyesight — all watched. Naadi: 'The king walks with cane.'",
    "Sun_Rahu": "Father absent, foreign, or non-traditional. Native chases unconventional authority. Eyes weak. Identity blends with shadow. Naadi: 'The king's crown is foreign-made.'",
    "Sun_Ketu": "Father spiritual or detached; soul carries past-life ego-loss. Native is humble despite leadership-aspect. Naadi: 'The king's throne is empty by choice.'",
    "Sun_Mars": "Sharp authority, commanding presence; aggression on behalf of dharma. Possible father-conflict. Naadi: 'The king carries a sword.'",
    "Moon_Saturn": "Mother carries grief, depression possible in family-line. Mind disciplined by hardship. Slow emotional maturity. Naadi: 'The mother weeps in winter.'",
    "Moon_Rahu": "Mother foreign/unconventional/distant. Anxiety, hallucination potential, addiction. Karmic mother-bond. Naadi: 'The mother walks in mist.'",
    "Moon_Ketu": "Mother spiritual or detached; mind naturally detaches; psychic gifts. Naadi: 'The mother holds a beggar's bowl.'",
    "Mars_Saturn": "Effort meets resistance; persistent struggle yields late mastery. Iron-meets-stone. Naadi: 'The blacksmith strikes cold iron.'",
    "Mars_Rahu": "Explosive risk-taking; accidents, foreign aggression, military or surgical karma. Naadi: 'Lightning strikes iron.'",
    "Venus_Saturn": "Love is mature, sometimes painful; karmic relationship debt; older or restrictive partner. Naadi: 'Beauty walks with the elder.'",
    "Venus_Rahu": "Foreign or unconventional partner; obsessive attraction; addiction-risk in relationships. Naadi: 'Beauty drinks foreign wine.'",
    "Jupiter_Saturn": "Wisdom + discipline = late-life mastery; slow but profound dharmic development. Naadi: 'The teacher tills the field.'",
    "Jupiter_Rahu": "Guru-Chandala dosha — unconventional teacher, possible cult-attraction; dharmic confusion. Naadi: 'The teacher's robe has a tear.'",
    "Saturn_Rahu": "Karmic burden multiplied; slow grinding mastery through suffering; exposure to large impersonal systems. Naadi: 'Stone wears stone.'",
}


def detect_two_planet_rules(chart):
    """Detect each of the 13 specific 2-planet conjunctions."""
    pos = chart["positions"]
    out = []
    for key, rule in TWO_PLANET_RULES.items():
        p1, p2 = key.split("_")
        if p1 in pos and p2 in pos and pos[p1]["rasi_idx"] == pos[p2]["rasi_idx"]:
            out.append({
                "combination": f"{p1} + {p2} in {pos[p1]['rasi']}",
                "house": pos[p1]["house"],
                "key": key,
                "reading": rule,
            })
    return out


# ============================================================
# KARAKA-SPECIFIC NADI RULES
# ============================================================
KARAKA_AGENTS = {
    "Sun":     ("father, soul, ego",
                "When Sun is strong: father-blessing in life; native carries paternal pride and authority.",
                "When Sun is weak/dusthana: father struggles; native's authority hard-won; soul carries ego-purification karma."),
    "Moon":    ("mother, mind, emotion",
                "When Moon is strong: mother-blessing; emotional clarity; public love.",
                "When Moon is weak: mother distant or struggling; emotional turbulence; dependence on others' moods."),
    "Mars":    ("siblings (esp. brother), courage, blood, surgery",
                "When Mars is strong: bold, athletic, victorious; supportive brother.",
                "When Mars is weak: brother-conflict; accident/surgery karma; aggression hard to channel."),
    "Mercury": ("siblings (younger), intellect, speech",
                "When Mercury is strong: sharp intellect; many friends; communication-rich life.",
                "When Mercury is weak: speech defects; nervous mind; education delayed."),
    "Jupiter": ("children, wisdom, husband (for women), wealth-grace",
                "When Jupiter is strong: wisdom, dharmic life, blessed children, financial grace.",
                "When Jupiter is weak: dharmic struggle; children-difficulty; wisdom learned hard."),
    "Venus":   ("spouse (for men), comfort, arts, vehicles",
                "When Venus is strong: beautiful spouse; comforts; arts and luxury.",
                "When Venus is weak: marital trouble; comforts elusive; relationship-karma."),
    "Saturn":  ("longevity, discipline, servants, sorrow, profession",
                "When Saturn is strong: long life; mastered profession; lasting structures.",
                "When Saturn is weak: chronic struggle; profession-blocks; loneliness or melancholy."),
    "Rahu":    ("foreign, technology, addiction, sudden, in-laws",
                "When Rahu is strong: foreign opportunity; tech-career; sudden gains.",
                "When Rahu is weak: addiction; deception; sudden losses."),
    "Ketu":    ("liberation, past-karma, spirituality, isolation",
                "When Ketu is strong: spiritual gifts; past-life skill; mature detachment.",
                "When Ketu is weak: confusion; isolation; karmic-disease patterns."),
}


def karaka_readings(chart):
    """Return per-planet karaka-context reading with 4-tier strength classification.

    Tiers: very_strong (dignified + good house), strong (dignified or in 1/5/9/10),
           mixed (dignified but dusthana, or debil but good house), weak (debil or dusthana).
    """
    pos = chart["positions"]
    out = {}
    GOOD_HOUSES_KARAKA = (1, 4, 5, 7, 9, 10, 11)
    DUSTHANA = (6, 8, 12)
    for planet, (agent, strong_text, weak_text) in KARAKA_AGENTS.items():
        if planet not in pos: continue
        pd = pos[planet]
        dignity = DIGNITIES.get((planet, pd["rasi"]), "neutral")
        h = pd["house"]
        is_dignified = dignity in ("Own", "Exalted", "Exalted/Own")
        is_debil = dignity == "Debil"
        is_good_house = h in GOOD_HOUSES_KARAKA
        is_dusthana = h in DUSTHANA

        if is_dignified and is_good_house:
            tone = "very_strong"
            verdict = f"VERY STRONG: {strong_text} (Dignified in {dignity} + good house H{h}.)"
        elif is_dignified and not is_dusthana:
            tone = "strong"
            verdict = f"STRONG: {strong_text}"
        elif is_dignified and is_dusthana:
            tone = "mixed"
            verdict = f"MIXED: dignified {dignity} but in dusthana H{h} — strength expresses through struggle. {strong_text}"
        elif is_debil and is_good_house:
            tone = "mixed"
            verdict = f"MIXED: debilitated but salvaged by good house H{h}. {weak_text}"
        elif is_debil or is_dusthana:
            tone = "weak"
            verdict = weak_text
        elif is_good_house:
            tone = "strong"
            verdict = strong_text
        else:
            tone = "neutral"
            verdict = f"Neutral placement. Karaka-themes ({agent}) play out in standard fashion through House {h}."

        out[planet] = {
            "agent_of": agent,
            "house": h,
            "rasi": pd["rasi"],
            "dignity": dignity,
            "tone": tone,
            "reading": verdict,
        }
    return out


# ============================================================
# COMPLETE NADI ANALYSIS
# ============================================================
def complete_nadi_analysis(chart):
    """Complete analysis: 9-planet narrative + 13-rule conjunctions + karaka readings."""
    return {
        "narrative_108_cells": full_nadi_narrative(chart),
        "two_planet_rules_detected": detect_two_planet_rules(chart),
        "karaka_readings": karaka_readings(chart),
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    result = complete_nadi_analysis(chart)

    print(f"=== NADI FULL — 108-Cell Narrative ({chart['name']}) ===\n")
    print("--- Per-Planet Naadi Reading ---")
    for planet, info in result["narrative_108_cells"].items():
        print(f"\n  {planet} in House {info['house']} ({info['rasi']}):")
        print(f"    Theme: {info['archetype']}")
        print(f"    {info['reading']}")

    print(f"\n--- 13 Specific 2-Planet Conjunction Rules ---")
    if not result["two_planet_rules_detected"]:
        print("  None detected.")
    else:
        for r in result["two_planet_rules_detected"]:
            print(f"\n  {r['combination']} (House {r['house']}):")
            print(f"    {r['reading']}")

    print(f"\n--- Karaka-Specific Readings ---")
    for p, info in result["karaka_readings"].items():
        print(f"\n  {p} ({info['agent_of']}) — H{info['house']}, {info['rasi']}, {info['dignity']} [{info['tone']}]:")
        print(f"    {info['reading']}")
