"""
Nabhasa Yogas — the classical 32-yoga catalogue (Brihat Jataka Ch.10,
Saravali Ch.39, Phaladeepika Ch.6, Raman's 300 Combinations Ch.7).

Mined verbatim from the deep-extracted corpus (Raman_300Combinations,
Bhavartha_Ratnakara_Raman, Phaladeepika). The 7 grahas considered are
Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn (Rahu/Ketu excluded
by classical convention).

Three classes:
    - Asraya  (3): sign-mode based   — Rajju (mov), Nala (dual)
                   [Musala (fixed) already in yogas_extended]
    - Dala    (2): benefic/malefic placement — Mala, Sarpa
    - Sankhya (7): count of distinct signs — Sula(3) Kedara(4) Pasha(5)
                   Damini(6) Veena(7)  [Gola(1) Yuga(2) in extended]
    - Akriti (20+): planetary 'shape' patterns — Gada, Sakata, Vihaga,
                   Sringataka, Hala, Vajra, Yava, Kamala, Vapi, Yupa,
                   Shara, Shakti, Danda, Naukha (Nau), Kuta, Chatra,
                   Chapa, Ardha-Chandra, Samudra
    + Bonus: Bharathi (Bhavartha_Ratnakara) — navamsa-lord based
"""
from __future__ import annotations

from .yogas_extended import (
    ExtendedYoga, BENEFICS, MALEFICS, KENDRAS, TRIKONAS, DUSTHANAS,
    MOVABLE, FIXED, DUAL, _planet_house, _lord_of_house, _lagna_sign,
)

NABHASA_GRAHAS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
SRC_RAMAN = "Raman, Three Hundred Important Combinations, Ch.7 (Nabhasa Yogas)"
SRC_BHAVARTHA = "Bhavartha Ratnakara (Raman commentary)"


def _planet_signs(chart) -> dict[str, int]:
    """Map planet → sign index (0-11) for the 7 grahas."""
    out = {}
    for p in NABHASA_GRAHAS:
        lon = chart.positions.get(p)
        if lon is None:
            continue
        out[p] = int(lon // 30)
    return out


def _planet_houses(chart) -> dict[str, int]:
    return {p: _planet_house(chart, p) for p in NABHASA_GRAHAS
            if chart.positions.get(p) is not None}


def _all_in_signs(chart, sign_set: set) -> list[str]:
    return [p for p, s in _planet_signs(chart).items() if s in sign_set]


def _all_in_houses(chart, house_set: set) -> list[str]:
    return [p for p, h in _planet_houses(chart).items() if h in house_set]


# ─── ASRAYA YOGAS (sign-mode) ─────────────────────────────────────────────
def detect_rajju_yoga(chart) -> ExtendedYoga | None:
    """All 7 grahas in movable signs (Aries, Cancer, Libra, Capricorn)."""
    occ = _all_in_signs(chart, MOVABLE)
    if len(occ) >= 7:
        return ExtendedYoga(
            code="RAJJU_YOGA",
            name="Rajju Yoga (rope)",
            valence="MIXED",
            strength="STRONG",
            involves=occ,
            evidence="All 7 grahas in movable signs",
            classical_source=SRC_RAMAN,
            description=("Native fond of travel, wandering, change. Engaged "
                         "in foreign trades. Restless, ambitious, energetic."),
            activation_or_remedy="Channel restlessness into movement-based career; avoid sedentary roles",
        )
    return None


def detect_nala_yoga(chart) -> ExtendedYoga | None:
    """All 7 grahas in dual signs (Gemini, Virgo, Sagittarius, Pisces)."""
    occ = _all_in_signs(chart, DUAL)
    if len(occ) >= 7:
        return ExtendedYoga(
            code="NALA_YOGA",
            name="Nala Yoga (reed)",
            valence="MIXED",
            strength="STRONG",
            involves=occ,
            evidence="All 7 grahas in dual/common signs",
            classical_source=SRC_RAMAN,
            description=("Skilful, well-cultured, learned. Often clever but "
                         "lacks fixed conviction; bends like a reed."),
            activation_or_remedy="Use adaptability as a strength but commit to one principal goal",
        )
    return None


# ─── DALA YOGAS (benefic/malefic placement) ───────────────────────────────
def detect_mala_yoga(chart) -> ExtendedYoga | None:
    """All 3 natural benefics (Jupiter/Venus/Mercury — excluding Moon
    in classical Nabhasa) in 3 different kendras → Mala (Garland) Yoga.
    """
    benefic_houses = {p: _planet_house(chart, p)
                      for p in ("Jupiter", "Venus", "Mercury")
                      if chart.positions.get(p) is not None}
    in_kendra = {p: h for p, h in benefic_houses.items() if h in KENDRAS}
    distinct_kendras = set(in_kendra.values())
    if len(in_kendra) == 3 and len(distinct_kendras) == 3:
        return ExtendedYoga(
            code="MALA_YOGA_NABHASA",
            name="Mala Yoga (garland)",
            valence="GOOD",
            strength="SUPREME",
            involves=list(in_kendra.keys()),
            evidence=f"All 3 benefics in 3 distinct kendras: {in_kendra}",
            classical_source=SRC_RAMAN,
            description=("'Wears luxuries always like a garland.' Native enjoys "
                         "every comfort — food, vehicles, status, women."),
            activation_or_remedy="Lean into Jupiter/Venus/Mercury domains — wisdom, art, communication",
        )
    return None


def detect_sarpa_nabhasa_yoga(chart) -> ExtendedYoga | None:
    """All 3 malefics (Sun/Mars/Saturn — Moon excluded by Nabhasa rule)
    in 3 different kendras → Sarpa (Serpent) Yoga.
    """
    mal_houses = {p: _planet_house(chart, p)
                  for p in ("Sun", "Mars", "Saturn")
                  if chart.positions.get(p) is not None}
    in_kendra = {p: h for p, h in mal_houses.items() if h in KENDRAS}
    distinct = set(in_kendra.values())
    if len(in_kendra) == 3 and len(distinct) == 3:
        return ExtendedYoga(
            code="SARPA_NABHASA_YOGA",
            name="Sarpa Yoga (serpent, Nabhasa)",
            valence="BAD",
            strength="STRONG",
            involves=list(in_kendra.keys()),
            evidence=f"All 3 malefics in 3 distinct kendras: {in_kendra}",
            classical_source=SRC_RAMAN,
            description=("Miserable, cruel, disliked. Dependent on others' "
                         "mercy. Distinct from the Rahu-Ketu Sarpa-dosha."),
            activation_or_remedy=("Cultivate Vishnu/Subrahmanya worship; serve "
                                  "elders to soften malefic burden"),
        )
    return None


# ─── SANKHYA YOGAS (count of distinct signs) ─────────────────────────────
SANKHYA_TABLE = {
    3: ("SULA_YOGA",   "Sula Yoga (trident)",
        "BAD", "STRONG",
        "Cruel, fond of weapons, soldier-like temperament. Suffers losses, lacks comforts."),
    4: ("KEDARA_YOGA", "Kedara Yoga (field)",
        "GOOD", "MODERATE",
        "Helpful to many, agriculturist, truthful. Good for leadership over land/people."),
    5: ("PASHA_YOGA",  "Pasha Yoga (noose)",
        "BAD", "MODERATE",
        "Hot-tempered, has many servants, bound by debts/imprisonment risk."),
    6: ("DAMINI_YOGA", "Damini Yoga (string of pearls)",
        "GOOD", "STRONG",
        "Charitable, wealthy, fond of others' wives, famous in his clan."),
    7: ("VEENA_YOGA",  "Veena Yoga (lute)",
        "GOOD", "MODERATE",
        "Fond of music, dance, women. Expert in arts. Wealth from talent, not labour."),
}


def detect_sankhya_yogas(chart) -> list[ExtendedYoga]:
    """Sankhya yoga fires when all 7 grahas occupy exactly N distinct signs.
    N=1 → Gola, N=2 (adjacent) → Yuga (both in yogas_extended already).
    Here we cover N=3..7.
    """
    signs = set(_planet_signs(chart).values())
    n = len(signs)
    if n in SANKHYA_TABLE:
        code, name, valence, strength, desc = SANKHYA_TABLE[n]
        return [ExtendedYoga(
            code=code, name=name, valence=valence, strength=strength,
            involves=list(NABHASA_GRAHAS),
            evidence=f"7 grahas occupy exactly {n} distinct signs: {sorted(signs)}",
            classical_source=SRC_RAMAN,
            description=desc,
            activation_or_remedy=(
                "Honor the dispersion pattern — your life is shaped by this signature"
            ),
        )]
    return []


# ─── AKRITI YOGAS (shape/pattern) ─────────────────────────────────────────
def _planets_in_house_set(chart, hset: set) -> list[str]:
    return [p for p, h in _planet_houses(chart).items() if h in hset]


def _planets_in_houses_only(chart, hset: set) -> list[str] | None:
    """All 7 grahas in ONLY the given houses (and nowhere else). Return list
    of grahas if condition holds, else None."""
    in_set = _planets_in_house_set(chart, hset)
    if len(in_set) >= 7:
        return in_set
    return None


def detect_gada_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 2 adjacent kendras (1+4, 4+7, 7+10, 10+1)."""
    pairs = [({1, 4}, "1st & 4th"), ({4, 7}, "4th & 7th"),
             ({7, 10}, "7th & 10th"), ({10, 1}, "10th & 1st")]
    for hset, label in pairs:
        occ = _planets_in_houses_only(chart, hset)
        if occ:
            return ExtendedYoga(
                code="GADA_YOGA",
                name="Gada Yoga (mace)",
                valence="GOOD",
                strength="STRONG",
                involves=occ,
                evidence=f"All 7 grahas in {label} (adjacent kendras)",
                classical_source=SRC_RAMAN,
                description=("Highly religious, wealthy, attached to Vedic "
                             "lore. Earns through righteous means."),
                activation_or_remedy="Strengthen dharma practice; wealth follows",
            )
    return None


def detect_sakata_nabhasa_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 1st & 7th houses only (Nabhasa Sakata — distinct from
    Moon-Jupiter Sakata in lunar yogas)."""
    occ = _planets_in_houses_only(chart, {1, 7})
    if occ:
        return ExtendedYoga(
            code="SAKATA_NABHASA_YOGA",
            name="Sakata Yoga (cart, Nabhasa)",
            valence="BAD",
            strength="STRONG",
            involves=occ,
            evidence="All 7 grahas in 1st & 7th",
            classical_source=SRC_RAMAN,
            description=("Poor, unhappy in domestic life, cart-puller-like "
                         "labour. Distinct from Moon-12-from-Jupiter Sakata."),
            activation_or_remedy="Sun-worship and dharmic vows recommended",
        )
    return None


def detect_vihaga_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 4th & 10th houses only."""
    occ = _planets_in_houses_only(chart, {4, 10})
    if occ:
        return ExtendedYoga(
            code="VIHAGA_YOGA",
            name="Vihaga Yoga (bird)",
            valence="MIXED",
            strength="MODERATE",
            involves=occ,
            evidence="All 7 grahas in 4th & 10th",
            classical_source=SRC_RAMAN,
            description="Roams place to place; messenger-like; news-bearer; restless career.",
            activation_or_remedy="Travel-based or media career fits the pattern",
        )
    return None


def detect_sringataka_yoga(chart) -> ExtendedYoga | None:
    """All 7 in trikonas 1, 5, 9."""
    occ = _planets_in_houses_only(chart, TRIKONAS)
    if occ:
        return ExtendedYoga(
            code="SRINGATAKA_YOGA",
            name="Sringataka Yoga (caltrop)",
            valence="GOOD",
            strength="STRONG",
            involves=occ,
            evidence="All 7 grahas in trikonas (1/5/9)",
            classical_source=SRC_RAMAN,
            description="Devoted to wife, fond of fights and weapons, attached to king.",
            activation_or_remedy="Focused dharmic ambition rewarded",
        )
    return None


def detect_hala_yoga(chart) -> ExtendedYoga | None:
    """All 7 in trikonas counted from 2/3/4 — i.e. {2,6,10}, {3,7,11}, {4,8,12}."""
    triples = [({2, 6, 10}, "2-6-10"), ({3, 7, 11}, "3-7-11"), ({4, 8, 12}, "4-8-12")]
    for hset, label in triples:
        occ = _planets_in_houses_only(chart, hset)
        if occ:
            return ExtendedYoga(
                code="HALA_YOGA",
                name="Hala Yoga (plough)",
                valence="MIXED",
                strength="MODERATE",
                involves=occ,
                evidence=f"All 7 grahas in trikonas {label}",
                classical_source=SRC_RAMAN,
                description=("Agriculturist, hard-working, accustomed to toil. "
                             "Wealth gathered slowly through labour."),
                activation_or_remedy="Land/agriculture/manual-craft career fits",
            )
    return None


def detect_vajra_yoga(chart) -> ExtendedYoga | None:
    """Benefics in 1+7, malefics in 4+10."""
    in_1_7 = _planets_in_house_set(chart, {1, 7})
    in_4_10 = _planets_in_house_set(chart, {4, 10})
    if (in_1_7 and all(p in BENEFICS for p in in_1_7)
            and in_4_10 and all(p in MALEFICS for p in in_4_10)
            and len(in_1_7) + len(in_4_10) >= 4):
        return ExtendedYoga(
            code="VAJRA_YOGA",
            name="Vajra Yoga (diamond)",
            valence="GOOD",
            strength="STRONG",
            involves=in_1_7 + in_4_10,
            evidence=f"Benefics in 1/7 ({in_1_7}), malefics in 4/10 ({in_4_10})",
            classical_source=SRC_RAMAN,
            description="Happy in early & late life, brave, attractive, wealthy.",
            activation_or_remedy="First and last decades of life are strongest",
        )
    return None


def detect_yava_yoga(chart) -> ExtendedYoga | None:
    """Malefics in 1+7, benefics in 4+10 — middle of life is best."""
    in_1_7 = _planets_in_house_set(chart, {1, 7})
    in_4_10 = _planets_in_house_set(chart, {4, 10})
    if (in_1_7 and all(p in MALEFICS for p in in_1_7)
            and in_4_10 and all(p in BENEFICS for p in in_4_10)
            and len(in_1_7) + len(in_4_10) >= 4):
        return ExtendedYoga(
            code="YAVA_YOGA",
            name="Yava Yoga (barley)",
            valence="MIXED",
            strength="MODERATE",
            involves=in_1_7 + in_4_10,
            evidence=f"Malefics in 1/7 ({in_1_7}), benefics in 4/10 ({in_4_10})",
            classical_source=SRC_RAMAN,
            description="Middle of life is most prosperous; childhood and old age bear hardship.",
            activation_or_remedy="Aim for middle-aged peak; conserve energy in youth and old age",
        )
    return None


def detect_kamala_yoga(chart) -> ExtendedYoga | None:
    """All 7 in the four kendras."""
    occ = _planets_in_houses_only(chart, KENDRAS)
    if occ:
        return ExtendedYoga(
            code="KAMALA_YOGA",
            name="Kamala Yoga (lotus)",
            valence="GOOD",
            strength="SUPREME",
            involves=occ,
            evidence="All 7 grahas distributed across 4 kendras",
            classical_source=SRC_RAMAN,
            description="Long-lived, famous, virtuous, kingly. Among the strongest Akritis.",
            activation_or_remedy="Public-leadership, statecraft, dharma-pillar role",
        )
    return None


def detect_vapi_yoga(chart) -> ExtendedYoga | None:
    """All 7 in the panaparas (2,5,8,11) OR all in apoklimas (3,6,9,12)."""
    for hset, kind in (({2, 5, 8, 11}, "panaparas"), ({3, 6, 9, 12}, "apoklimas")):
        occ = _planets_in_houses_only(chart, hset)
        if occ:
            return ExtendedYoga(
                code="VAPI_YOGA",
                name="Vapi Yoga (well)",
                valence="GOOD",
                strength="MODERATE",
                involves=occ,
                evidence=f"All 7 grahas in {kind}",
                classical_source=SRC_RAMAN,
                description="Saver, accumulator, treasury-builder. Wealth grows quietly.",
                activation_or_remedy="Long-horizon saving and asset accumulation",
            )
    return None


def detect_yupa_yoga(chart) -> ExtendedYoga | None:
    """All 7 in houses 1, 2, 3, 4."""
    occ = _planets_in_houses_only(chart, {1, 2, 3, 4})
    if occ:
        return ExtendedYoga(
            code="YUPA_YOGA",
            name="Yupa Yoga (sacrificial post)",
            valence="GOOD",
            strength="STRONG",
            involves=occ,
            evidence="All 7 grahas in 1-2-3-4",
            classical_source=SRC_RAMAN,
            description="Performs Vedic sacrifices, devoted to family, wealthy and respected.",
            activation_or_remedy="Family/dharma-led path; rituals empower",
        )
    return None


def detect_shara_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 4-5-6-7."""
    occ = _planets_in_houses_only(chart, {4, 5, 6, 7})
    if occ:
        return ExtendedYoga(
            code="SHARA_YOGA",
            name="Shara Yoga (arrow)",
            valence="MIXED",
            strength="MODERATE",
            involves=occ,
            evidence="All 7 grahas in 4-5-6-7",
            classical_source=SRC_RAMAN,
            description="Arrow-maker, hunter, prison-keeper, archer. Sharp profession.",
            activation_or_remedy="Sharp/precise crafts (engineering, surgery, archery)",
        )
    return None


def detect_shakti_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 7-8-9-10."""
    occ = _planets_in_houses_only(chart, {7, 8, 9, 10})
    if occ:
        return ExtendedYoga(
            code="SHAKTI_YOGA",
            name="Shakti Yoga (lance)",
            valence="MIXED",
            strength="MODERATE",
            involves=occ,
            evidence="All 7 grahas in 7-8-9-10",
            classical_source=SRC_RAMAN,
            description="Penurious in early life, lazy, defeated; later bears suffering with patience.",
            activation_or_remedy="Build resilience; later half of life redeems early hardship",
        )
    return None


def detect_danda_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 10-11-12-1."""
    occ = _planets_in_houses_only(chart, {10, 11, 12, 1})
    if occ:
        return ExtendedYoga(
            code="DANDA_YOGA",
            name="Danda Yoga (staff)",
            valence="BAD",
            strength="MODERATE",
            involves=occ,
            evidence="All 7 grahas in 10-11-12-1",
            classical_source=SRC_RAMAN,
            description="Forsaken by relatives, wife, children. Servile career, sufferer.",
            activation_or_remedy="Saturn/Shani propitiation; serve elders",
        )
    return None


def _seven_contiguous_from(start_house: int) -> set:
    """Return houses {start, start+1, ..., start+6} mod 12 (1-indexed)."""
    return {((start_house - 1 + i) % 12) + 1 for i in range(7)}


def detect_naukha_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 7 contiguous houses starting from 1st."""
    occ = _planets_in_houses_only(chart, _seven_contiguous_from(1))
    if occ:
        return ExtendedYoga(
            code="NAUKHA_YOGA",
            name="Naukha (boat) Yoga",
            valence="MIXED",
            strength="MODERATE",
            involves=occ,
            evidence="All 7 grahas in houses 1..7",
            classical_source=SRC_RAMAN,
            description="Sailor, traveller across waters; earns through movement.",
            activation_or_remedy="Marine, shipping, maritime trades favored",
        )
    return None


def detect_kuta_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 7 contiguous houses starting from 4th."""
    occ = _planets_in_houses_only(chart, _seven_contiguous_from(4))
    if occ:
        return ExtendedYoga(
            code="KUTA_YOGA",
            name="Kuta (peak) Yoga",
            valence="BAD",
            strength="MODERATE",
            involves=occ,
            evidence="All 7 grahas in houses 4..10",
            classical_source=SRC_RAMAN,
            description="Liar, prison-keeper, mountain-dweller, harsh-natured.",
            activation_or_remedy="Truthfulness vow + Brihaspati worship counter the pattern",
        )
    return None


def detect_chatra_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 7 contiguous houses starting from 7th."""
    occ = _planets_in_houses_only(chart, _seven_contiguous_from(7))
    if occ:
        return ExtendedYoga(
            code="CHATRA_YOGA",
            name="Chatra (umbrella) Yoga",
            valence="GOOD",
            strength="STRONG",
            involves=occ,
            evidence="All 7 grahas in houses 7..1",
            classical_source=SRC_RAMAN,
            description="Loved by king, long-lived, wealthy, lord of many.",
            activation_or_remedy="Patronage from authority is the chart's natural channel",
        )
    return None


def detect_chapa_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 7 contiguous houses starting from 10th."""
    occ = _planets_in_houses_only(chart, _seven_contiguous_from(10))
    if occ:
        return ExtendedYoga(
            code="CHAPA_YOGA",
            name="Chapa (bow) Yoga",
            valence="MIXED",
            strength="MODERATE",
            involves=occ,
            evidence="All 7 grahas in houses 10..4",
            classical_source=SRC_RAMAN,
            description="Liar, prison-keeper, fond of forests, rich at end of life.",
            activation_or_remedy="Late-life gains; first half tests integrity",
        )
    return None


def detect_ardha_chandra_yoga(chart) -> ExtendedYoga | None:
    """All 7 in 7 contiguous houses starting from a Panapara (2,5,8,11)
    or an Apoklima (3,6,9,12). Eight variants total."""
    for start in (2, 3, 5, 6, 8, 9, 11, 12):
        occ = _planets_in_houses_only(chart, _seven_contiguous_from(start))
        if occ:
            return ExtendedYoga(
                code=f"ARDHA_CHANDRA_YOGA_{start}",
                name=f"Ardha-Chandra Yoga (half-moon, from H{start})",
                valence="GOOD",
                strength="STRONG",
                involves=occ,
                evidence=f"All 7 grahas in 7 contiguous houses starting at H{start}",
                classical_source=SRC_RAMAN,
                description="Fair-featured, happy throughout life, commander, king's favorite.",
                activation_or_remedy="Aesthetic, military or court-favor career succeeds",
            )
    return None


def detect_samudra_yoga(chart) -> ExtendedYoga | None:
    """All 7 in even houses 2/4/6/8/10/12 only."""
    occ = _planets_in_houses_only(chart, {2, 4, 6, 8, 10, 12})
    if occ:
        return ExtendedYoga(
            code="SAMUDRA_YOGA",
            name="Samudra (ocean) Yoga",
            valence="GOOD",
            strength="SUPREME",
            involves=occ,
            evidence="All 7 grahas in even houses (2/4/6/8/10/12)",
            classical_source=SRC_RAMAN,
            description="King or equal to a king. Vast wealth, fame, oceanic abundance.",
            activation_or_remedy="Embrace public scale — small life is mis-fitted",
        )
    return None


# ─── BHARATHI YOGA (Bhavartha Ratnakara) ─────────────────────────────────
def detect_bharathi_yoga(chart) -> ExtendedYoga | None:
    """Lords of the navamsas occupied by lords of 2/5/11 are exalted and
    combined with the 9th lord. Approximation: 9th-lord conjunct ANY of
    2nd/5th/11th lords AND that conjunction sign's lord exalted.
    """
    l9 = _lord_of_house(chart, 9)
    if not chart.positions.get(l9):
        return None
    l9_house = _planet_house(chart, l9)
    others = [_lord_of_house(chart, h) for h in (2, 5, 11)]
    conjuncts = [p for p in others
                 if p != l9 and chart.positions.get(p) is not None
                 and _planet_house(chart, p) == l9_house]
    if not conjuncts:
        return None
    # Crude exaltation check using sign indices
    EXALT = {"Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5, "Jupiter": 3,
             "Venus": 11, "Saturn": 6}
    l9_sign = int(chart.positions[l9] // 30)
    exalted = (EXALT.get(l9) == l9_sign) or any(
        EXALT.get(p) == int(chart.positions[p] // 30) for p in conjuncts)
    if exalted:
        return ExtendedYoga(
            code="BHARATHI_YOGA",
            name="Bharathi Yoga",
            valence="GOOD",
            strength="STRONG",
            involves=[l9] + conjuncts,
            evidence=f"9th-lord {l9} conjunct {conjuncts} with exalted dignity",
            classical_source=SRC_BHAVARTHA,
            description=("World-famous, reputed scholar, fond of music, "
                         "romantic, religiously inclined."),
            activation_or_remedy="Saraswati upasana; pursue scholarly fame",
        )
    return None


# ─── AGGREGATOR ──────────────────────────────────────────────────────────
def detect_all_nabhasa(chart) -> list[ExtendedYoga]:
    out: list[ExtendedYoga] = []
    for fn in (detect_rajju_yoga, detect_nala_yoga,
               detect_mala_yoga, detect_sarpa_nabhasa_yoga,
               detect_gada_yoga, detect_sakata_nabhasa_yoga, detect_vihaga_yoga,
               detect_sringataka_yoga, detect_hala_yoga,
               detect_vajra_yoga, detect_yava_yoga,
               detect_kamala_yoga, detect_vapi_yoga,
               detect_yupa_yoga, detect_shara_yoga, detect_shakti_yoga,
               detect_danda_yoga, detect_naukha_yoga, detect_kuta_yoga,
               detect_chatra_yoga, detect_chapa_yoga,
               detect_ardha_chandra_yoga, detect_samudra_yoga,
               detect_bharathi_yoga):
        y = fn(chart)
        if y:
            out.append(y)
    out.extend(detect_sankhya_yogas(chart))
    return out
