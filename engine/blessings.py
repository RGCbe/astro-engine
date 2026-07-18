"""
Blessing detector — symmetric counterpart to afflictions.

Per user directive 2026-04-26: "good things as best as bad thing — engine is
best at everything." This module finds EVERY classical positive yoga / strong
combination in a chart, with the same rigor as the affliction detector.

Categories:
    1. Pancha Mahapurusha yogas (Hamsa, Bhadra, Malavya, Sasa, Ruchaka)
    2. Raja yogas (lord-of-kendra + lord-of-trikona conjunctions / aspects)
    3. Dhana yogas (wealth combinations: 2nd-5th-9th-11th lord links)
    4. Vipareeta Raja Yoga (dusthana lords in dusthana = unexpected gain)
    5. Neecha Bhanga Raja Yoga (debilitation cancellation)
    6. Lakshmi, Kubera, Saraswati, Adhi yogas
    7. Gajakesari yoga (Jupiter-Moon kendra)
    8. Sunapha / Anapha / Durudhura / Vasi / Vesi / Ubhayachari yogas
       (planets in 2nd/12th from Sun and Moon)
    9. Chandra-Mangal yoga (wealth-prosperity)
    10. Saraswati yoga (learning/wisdom)
    11. Amshavatara yoga (incarnation of partial avatar)
    12. Specific classical exceptions (Mahabhagya, Bhasma yoga, etc.)
"""
from __future__ import annotations

from dataclasses import dataclass, field

SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}
EXALTATION_SIGN = {
    "Sun": 0, "Moon": 1, "Mars": 9, "Mercury": 5,
    "Jupiter": 3, "Venus": 11, "Saturn": 6,
}
DEBILITATION_SIGN = {
    "Sun": 6, "Moon": 7, "Mars": 3, "Mercury": 11,
    "Jupiter": 9, "Venus": 5, "Saturn": 0,
}
OWN_SIGNS = {
    "Sun": [4], "Moon": [3], "Mars": [0, 7], "Mercury": [2, 5],
    "Jupiter": [8, 11], "Venus": [1, 6], "Saturn": [9, 10],
}
KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANAS = {6, 8, 12}
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}


@dataclass
class Blessing:
    code: str
    name: str
    strength: str       # SUPREME | STRONG | MODERATE | LATENT
    category: str       # mahapurusha | raja | dhana | viparita | neecha_bhanga |
                        # adhi | gajakesari | sunapha_etc | sankha | classical
    involves: list[str] = field(default_factory=list)
    evidence: str = ""
    classical_source: str = ""
    description: str = ""
    activation: str = ""   # how to fully express this yoga's potential


def _planet_house(longitude: float, lagna_sign: int) -> int:
    sign = int(longitude // 30)
    return ((sign - lagna_sign) % 12) + 1


def _lord_of_house(h: int, lagna_sign: int) -> str:
    sign = (lagna_sign + h - 1) % 12
    return SIGN_LORD[sign]


def _is_in_own_or_exalted(planet: str, lon: float) -> bool:
    sign = int(lon // 30)
    return sign == EXALTATION_SIGN.get(planet) or sign in OWN_SIGNS.get(planet, [])


# ─── Pancha Mahapurusha (5 great-being yogas) ──────────────────────────────
def detect_pancha_mahapurusha(chart) -> list[Blessing]:
    """Mars/Mercury/Jupiter/Venus/Saturn in own or exalted sign in kendra."""
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    yoga_names = {
        "Mars": ("Ruchaka", "warrior, brave commander, outstanding physical achievements"),
        "Mercury": ("Bhadra", "intelligent communicator, scholar, business success"),
        "Jupiter": ("Hamsa", "wise teacher, religious eminence, virtuous nature"),
        "Venus": ("Malavya", "wealthy, beautiful, refined, luxurious life"),
        "Saturn": ("Sasa", "leader of organizations, mass leader, longevity"),
    }
    for planet, (yoga, mean) in yoga_names.items():
        lon = chart.positions.get(planet)
        if lon is None:
            continue
        h = _planet_house(lon, lagna_sign)
        if h in KENDRAS and _is_in_own_or_exalted(planet, lon):
            out.append(Blessing(
                code=f"MAHAPURUSHA_{yoga.upper()}",
                name=f"{yoga} Yoga (Pancha Mahapurusha)",
                strength="SUPREME",
                category="mahapurusha",
                involves=[planet, f"H{h}"],
                evidence=f"{planet} in own/exalted sign in kendra H{h}",
                classical_source="BPHS Ch.27; Phaladeepika Ch.6; Saravali Ch.32",
                description=f"{yoga}: {mean}.",
                activation=(f"Maximize {planet}'s expression — for {yoga}: "
                            f"{ {'Ruchaka':'lead disciplined initiative', 'Bhadra':'pursue advanced study or commerce', 'Hamsa':'serve as teacher/guide, deepen ethics', 'Malavya':'cultivate art, partnerships, refinement', 'Sasa':'work for mass causes, organize systems'}[yoga] }."),
            ))
    return out


# ─── Raja Yogas (kendra-trikona lord links) ────────────────────────────────
def detect_raja_yogas(chart) -> list[Blessing]:
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    kendra_lords = {_lord_of_house(h, lagna_sign) for h in KENDRAS}
    trikona_lords = {_lord_of_house(h, lagna_sign) for h in TRIKONAS}
    overlap = kendra_lords & trikona_lords    # planets that lord both
    pure_kendra = kendra_lords - overlap
    pure_trikona = trikona_lords - overlap

    # 1. Conjunction of kendra lord + trikona lord
    for k in pure_kendra:
        for t in pure_trikona:
            k_lon = chart.positions.get(k)
            t_lon = chart.positions.get(t)
            if k_lon is None or t_lon is None:
                continue
            if int(k_lon // 30) == int(t_lon // 30):  # same sign
                out.append(Blessing(
                    code=f"RAJA_YOGA_{k}_{t}",
                    name="Raja Yoga",
                    strength="STRONG",
                    category="raja",
                    involves=[k, t],
                    evidence=f"{k} (kendra-lord) conjunct {t} (trikona-lord) in same sign",
                    classical_source="BPHS Ch.34; Phaladeepika Ch.6",
                    description="Power, dignity, success, recognition through joined kendra-trikona effort.",
                    activation=(f"Activate {k}'s and {t}'s significations together. "
                                "Pursue achievement that fuses authority (kendra) with wisdom (trikona)."),
                ))

    # 2. Trikona lord placed in kendra OR kendra lord in trikona
    for k_house in KENDRAS:
        k_lord = _lord_of_house(k_house, lagna_sign)
        k_lord_lon = chart.positions.get(k_lord)
        if k_lord_lon is None:
            continue
        h_in = _planet_house(k_lord_lon, lagna_sign)
        if h_in in TRIKONAS:
            out.append(Blessing(
                code=f"RAJA_YOGA_K{k_house}_IN_T{h_in}",
                name=f"Raja Yoga: H{k_house} lord in H{h_in}",
                strength="STRONG",
                category="raja",
                involves=[k_lord, f"H{k_house}", f"H{h_in}"],
                evidence=f"{k_lord} (lord of kendra H{k_house}) placed in trikona H{h_in}",
                classical_source="BPHS Ch.34",
                description="Authority + dharma combined → achievement and respect.",
                activation=f"Pursue {k_lord}'s natural significations with dharmic intent.",
            ))
    return out


# ─── Dhana Yogas (wealth combinations) ─────────────────────────────────────
def detect_dhana_yogas(chart) -> list[Blessing]:
    """2nd, 5th, 9th, 11th lord links → wealth."""
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    wealth_houses = (2, 5, 9, 11)
    wealth_lords = {h: _lord_of_house(h, lagna_sign) for h in wealth_houses}

    pairs_seen = set()
    for h1 in wealth_houses:
        for h2 in wealth_houses:
            if h1 >= h2:
                continue
            l1 = wealth_lords[h1]; l2 = wealth_lords[h2]
            if l1 == l2:
                continue
            l1_lon = chart.positions.get(l1)
            l2_lon = chart.positions.get(l2)
            if l1_lon is None or l2_lon is None:
                continue
            if int(l1_lon // 30) == int(l2_lon // 30):
                key = tuple(sorted((l1, l2)))
                if key in pairs_seen:
                    continue
                pairs_seen.add(key)
                out.append(Blessing(
                    code=f"DHANA_YOGA_H{h1}H{h2}",
                    name=f"Dhana Yoga (H{h1}-H{h2} lord conjunction)",
                    strength="STRONG",
                    category="dhana",
                    involves=[l1, l2, f"H{h1}", f"H{h2}"],
                    evidence=f"{l1} (H{h1} lord) conjunct {l2} (H{h2} lord)",
                    classical_source="BPHS Ch.35; Phaladeepika Ch.5",
                    description=f"Wealth combination: links {h1}th house with {h2}th house significations.",
                    activation=f"Pursue income through {l1} and {l2} significations jointly.",
                ))
    return out


# ─── Vipareeta Raja Yoga (paradoxical gain from dusthanas) ─────────────────
def detect_vipareeta_raja_yoga(chart) -> list[Blessing]:
    """Dusthana lord (6, 8, 12) placed in another dusthana = unexpected gain."""
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    for h_dust in DUSTHANAS:
        l = _lord_of_house(h_dust, lagna_sign)
        l_lon = chart.positions.get(l)
        if l_lon is None:
            continue
        h_in = _planet_house(l_lon, lagna_sign)
        if h_in in DUSTHANAS and h_in != h_dust:
            out.append(Blessing(
                code=f"VIPARITA_RAJA_{h_dust}_IN_{h_in}",
                name=f"Vipareeta Raja Yoga (Harsha if {h_dust}=6, Sarala if 8, Vimala if 12)",
                strength="STRONG",
                category="viparita",
                involves=[l, f"H{h_dust}", f"H{h_in}"],
                evidence=f"{l} (dusthana H{h_dust} lord) in dusthana H{h_in}",
                classical_source="Saravali Ch.40; Phaladeepika Ch.6",
                description=("Paradoxical gain: harm cancels harm. Unexpected "
                             "victory over enemies/disease/loss, often via crisis."),
                activation=("Lean into challenges — this yoga rewards facing "
                            "difficulty head-on, not avoiding it."),
            ))
    return out


# ─── Neecha Bhanga Raja Yoga (debilitation cancellation) ───────────────────
def detect_neecha_bhanga(chart) -> list[Blessing]:
    """Debilitated planet whose dispositor or exaltation-lord is in kendra."""
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    for planet, deb_sign in DEBILITATION_SIGN.items():
        lon = chart.positions.get(planet)
        if lon is None or int(lon // 30) != deb_sign:
            continue
        # Cancellation conditions:
        # a) The lord of the debilitation sign is in kendra from lagna or Moon
        deb_sign_lord = SIGN_LORD[deb_sign]
        deb_lord_lon = chart.positions.get(deb_sign_lord)
        if deb_lord_lon is None:
            continue
        deb_lord_house = _planet_house(deb_lord_lon, lagna_sign)
        # b) The planet's exaltation-sign lord is in kendra
        exalt_sign = EXALTATION_SIGN.get(planet)
        exalt_lord = SIGN_LORD[exalt_sign] if exalt_sign is not None else None
        exalt_lord_lon = chart.positions.get(exalt_lord) if exalt_lord else None
        exalt_lord_house = _planet_house(exalt_lord_lon, lagna_sign) if exalt_lord_lon else None

        cancelled = False
        cause = ""
        if deb_lord_house in KENDRAS:
            cancelled = True
            cause = f"sign-lord {deb_sign_lord} in kendra H{deb_lord_house}"
        elif exalt_lord_house and exalt_lord_house in KENDRAS:
            cancelled = True
            cause = f"exaltation-sign-lord {exalt_lord} in kendra H{exalt_lord_house}"

        if cancelled:
            out.append(Blessing(
                code=f"NEECHA_BHANGA_{planet.upper()}",
                name=f"Neecha Bhanga Raja Yoga ({planet})",
                strength="STRONG",
                category="neecha_bhanga",
                involves=[planet],
                evidence=f"{planet} debilitated, but cancellation: {cause}",
                classical_source="BPHS Ch.7; Phaladeepika Ch.6",
                description=("Rags-to-riches dynamic. Early struggle in this "
                             "planet's significations followed by mid-life rise."),
                activation=("Accept the early struggle — the yoga matures with "
                            "time. Don't abandon the planet's domain when it seems weak."),
            ))
    return out


# ─── Gajakesari Yoga ───────────────────────────────────────────────────────
def detect_gajakesari(chart) -> Blessing | None:
    moon = chart.positions.get("Moon")
    jup = chart.positions.get("Jupiter")
    if moon is None or jup is None:
        return None
    moon_sign = int(moon // 30)
    jup_sign = int(jup // 30)
    diff = (jup_sign - moon_sign) % 12
    if diff in (0, 3, 6, 9):  # kendra from Moon
        return Blessing(
            code="GAJAKESARI",
            name="Gajakesari Yoga",
            strength="STRONG",
            category="gajakesari",
            involves=["Moon", "Jupiter"],
            evidence=f"Jupiter in kendra from Moon (Moon sign {moon_sign}, Jupiter sign {jup_sign})",
            classical_source="BPHS Ch.35; Phaladeepika Ch.6",
            description=("Strength of an elephant + boldness of a lion. "
                         "Public popularity, intelligence, eloquence, lasting fame."),
            activation="Pursue public-facing work — speaking, teaching, leadership.",
        )
    return None


# ─── Sunapha / Anapha / Durudhura ──────────────────────────────────────────
def detect_lunar_yogas(chart) -> list[Blessing]:
    out = []
    moon = chart.positions["Moon"]
    moon_sign = int(moon // 30)
    second_from_moon = (moon_sign + 1) % 12
    twelfth_from_moon = (moon_sign - 1) % 12

    grahas = {p: int(chart.positions[p] // 30)
              for p in ("Sun", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")}

    in_2 = [p for p, s in grahas.items() if s == second_from_moon]
    in_12 = [p for p, s in grahas.items() if s == twelfth_from_moon]

    if in_2 and not in_12:
        out.append(Blessing(
            code="SUNAPHA",
            name="Sunapha Yoga",
            strength="MODERATE",
            category="sunapha_etc",
            involves=["Moon"] + in_2,
            evidence=f"Planet(s) {in_2} in 2nd from Moon (no planets in 12th)",
            classical_source="BPHS Ch.35",
            description="Self-acquired wealth, intelligent earning, fame in chosen field.",
            activation="Develop independent earning capacity; trust your own initiative.",
        ))
    if in_12 and not in_2:
        out.append(Blessing(
            code="ANAPHA",
            name="Anapha Yoga",
            strength="MODERATE",
            category="sunapha_etc",
            involves=["Moon"] + in_12,
            evidence=f"Planet(s) {in_12} in 12th from Moon (no planets in 2nd)",
            classical_source="BPHS Ch.35",
            description="Refined character, generous nature, comfort, charm.",
            activation="Cultivate aesthetic and refined pursuits; live with grace.",
        ))
    if in_2 and in_12:
        out.append(Blessing(
            code="DURUDHURA",
            name="Durudhura Yoga",
            strength="STRONG",
            category="sunapha_etc",
            involves=["Moon"] + in_2 + in_12,
            evidence=f"Planets in BOTH 2nd ({in_2}) and 12th ({in_12}) from Moon",
            classical_source="BPHS Ch.35",
            description=("Rich friends, generous lifestyle, attended by retainers, "
                         "wealth and recognition."),
            activation="Build community around you; you are supported on all sides.",
        ))
    return out


# ─── Chandra-Mangal Yoga (Moon-Mars) ───────────────────────────────────────
def detect_chandra_mangal(chart) -> Blessing | None:
    moon = chart.positions["Moon"]
    mars = chart.positions["Mars"]
    moon_sign = int(moon // 30)
    mars_sign = int(mars // 30)
    if moon_sign == mars_sign:
        return Blessing(
            code="CHANDRA_MANGAL",
            name="Chandra-Mangal Yoga (Moon-Mars conjunction)",
            strength="MODERATE",
            category="dhana",
            involves=["Moon", "Mars"],
            evidence="Moon and Mars in same sign",
            classical_source="Phaladeepika Ch.6",
            description="Strong drive paired with emotional intelligence — wealth through enterprise.",
            activation="Pursue entrepreneurial / sales / real-estate ventures with emotional courage.",
        )
    return None


# ─── Adhi Yoga (benefics in 6/7/8 from Moon) ───────────────────────────────
def detect_adhi_yoga(chart) -> Blessing | None:
    moon = chart.positions["Moon"]
    moon_sign = int(moon // 30)
    target_signs = [(moon_sign + i) % 12 for i in (5, 6, 7)]
    benefics_present = []
    for b in ("Jupiter", "Venus", "Mercury"):
        b_lon = chart.positions.get(b)
        if b_lon and int(b_lon // 30) in target_signs:
            benefics_present.append(b)
    if len(benefics_present) >= 2:
        return Blessing(
            code="ADHI_YOGA",
            name="Adhi Yoga",
            strength="STRONG",
            category="adhi",
            involves=["Moon"] + benefics_present,
            evidence=f"{benefics_present} in 6th/7th/8th from Moon",
            classical_source="BPHS Ch.36; Phaladeepika Ch.6",
            description=("Influential, blessed by superiors, victorious over enemies, "
                         "wealth + comforts in mid-late life."),
            activation="Cultivate relationships with mentors and superiors actively.",
        )
    return None


# ─── Lakshmi Yoga ──────────────────────────────────────────────────────────
def detect_lakshmi_yoga(chart) -> Blessing | None:
    """9th lord in own/exalted sign in kendra/trikona, AND lagna lord strong."""
    lagna_sign = int(chart.lagna_lon // 30)
    h9_lord = _lord_of_house(9, lagna_sign)
    h9_lord_lon = chart.positions.get(h9_lord)
    if h9_lord_lon is None:
        return None
    if not _is_in_own_or_exalted(h9_lord, h9_lord_lon):
        return None
    h_in = _planet_house(h9_lord_lon, lagna_sign)
    if h_in not in (KENDRAS | TRIKONAS):
        return None
    # Lagna lord must be strong (in own or exalted) — soft check
    lagna_lord = _lord_of_house(1, lagna_sign)
    lagna_lord_lon = chart.positions.get(lagna_lord)
    lagna_lord_strong = lagna_lord_lon is not None and _is_in_own_or_exalted(lagna_lord, lagna_lord_lon)
    if lagna_lord_strong:
        return Blessing(
            code="LAKSHMI_YOGA",
            name="Lakshmi Yoga",
            strength="SUPREME",
            category="classical",
            involves=[h9_lord, lagna_lord],
            evidence=(f"H9 lord {h9_lord} in own/exalted sign in H{h_in}; "
                      f"lagna lord {lagna_lord} also strong"),
            classical_source="Phaladeepika Ch.6; Saravali Ch.40",
            description=("Wealth, beauty, fame, social grace, longevity. "
                         "One of the most prized classical yogas."),
            activation="Develop dharmic income; honor parents and elders; cultivate generosity.",
        )
    return None


# ─── Saraswati Yoga (Mercury, Jupiter, Venus together / strong) ────────────
def detect_saraswati_yoga(chart) -> Blessing | None:
    me = chart.positions.get("Mercury")
    ju = chart.positions.get("Jupiter")
    ve = chart.positions.get("Venus")
    lagna_sign = int(chart.lagna_lon // 30)
    if not all(x is not None for x in (me, ju, ve)):
        return None
    me_h = _planet_house(me, lagna_sign)
    ju_h = _planet_house(ju, lagna_sign)
    ve_h = _planet_house(ve, lagna_sign)
    # All in kendra/trikona/2nd?
    target = KENDRAS | TRIKONAS | {2}
    if me_h in target and ju_h in target and ve_h in target:
        # Must also be strong (in own/exalted) — soft check: at least 2 of 3
        strengths = sum(1 for p, lon in [("Mercury", me), ("Jupiter", ju), ("Venus", ve)]
                        if _is_in_own_or_exalted(p, lon))
        if strengths >= 2:
            return Blessing(
                code="SARASWATI_YOGA",
                name="Saraswati Yoga",
                strength="STRONG",
                category="classical",
                involves=["Mercury", "Jupiter", "Venus"],
                evidence=f"Me in H{me_h}, Ju in H{ju_h}, Ve in H{ve_h} (all favorable, ≥2 strong)",
                classical_source="Phaladeepika Ch.6",
                description="Outstanding learning, eloquence, scholarship, artistic mastery.",
                activation="Pursue advanced education, writing, teaching, performing arts.",
            )
    return None


# ─── Solar yogas (Vesi/Vasi/Ubhayachari — planets near Sun) ────────────────
def detect_solar_yogas(chart) -> list[Blessing]:
    """Planets in 2nd and 12th from Sun (excluding Moon)."""
    out = []
    sun = chart.positions["Sun"]
    sun_sign = int(sun // 30)
    second = (sun_sign + 1) % 12
    twelfth = (sun_sign - 1) % 12
    in_2 = []
    in_12 = []
    for p in ("Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        lon = chart.positions.get(p)
        if lon is None:
            continue
        s = int(lon // 30)
        if s == second:
            in_2.append(p)
        elif s == twelfth:
            in_12.append(p)
    if in_2 and not in_12:
        out.append(Blessing(
            code="VASI_YOGA",
            name="Vasi Yoga",
            strength="MODERATE",
            category="sunapha_etc",
            involves=["Sun"] + in_2,
            evidence=f"Planet(s) {in_2} in 2nd from Sun",
            classical_source="BPHS Ch.35",
            description="Industrious, charitable, well-spoken, orderly conduct.",
            activation="Pursue ethical leadership; fund charitable work.",
        ))
    if in_12 and not in_2:
        out.append(Blessing(
            code="VESI_YOGA",
            name="Vesi Yoga",
            strength="MODERATE",
            category="sunapha_etc",
            involves=["Sun"] + in_12,
            evidence=f"Planet(s) {in_12} in 12th from Sun",
            classical_source="BPHS Ch.35",
            description="Honest, religious, fortunate, dignified character.",
            activation="Cultivate principled service to family and community.",
        ))
    if in_2 and in_12:
        out.append(Blessing(
            code="UBHAYACHARI_YOGA",
            name="Ubhayachari Yoga",
            strength="STRONG",
            category="sunapha_etc",
            involves=["Sun"] + in_2 + in_12,
            evidence=f"Planets in BOTH 2nd ({in_2}) and 12th ({in_12}) from Sun",
            classical_source="BPHS Ch.35",
            description="Wealth, beauty, dignity, all-round success.",
            activation="Pursue both material excellence and spiritual depth in parallel.",
        ))
    return out


# ─── Shankha Yoga (5/6 lord conjunction with lagna lord, lagna lord strong) ──
def detect_shankha_yoga(chart) -> Blessing | None:
    lagna_sign = int(chart.lagna_lon // 30)
    h5_lord = _lord_of_house(5, lagna_sign)
    h6_lord = _lord_of_house(6, lagna_sign)
    h1_lord = _lord_of_house(1, lagna_sign)
    h5_lon = chart.positions.get(h5_lord)
    h6_lon = chart.positions.get(h6_lord)
    h1_lon = chart.positions.get(h1_lord)
    if not all(x is not None for x in (h5_lon, h6_lon, h1_lon)):
        return None
    # 5th and 6th lord linked, lagna lord strong
    if int(h5_lon // 30) == int(h6_lon // 30) and _is_in_own_or_exalted(h1_lord, h1_lon):
        return Blessing(
            code="SHANKHA_YOGA",
            name="Shankha Yoga",
            strength="STRONG",
            category="classical",
            involves=[h5_lord, h6_lord, h1_lord],
            evidence=f"H5 lord {h5_lord} conjunct H6 lord {h6_lord}; H1 lord {h1_lord} strong",
            classical_source="Phaladeepika Ch.6",
            description="Long life, virtuous deeds, wealth from agriculture/land/family business.",
            activation="Build longevity-supporting habits early; invest in land/long-term assets.",
        )
    return None


# ─── Padma Yoga (4 benefics in 1, 4, 7, 10) ────────────────────────────────
def detect_padma_yoga(chart) -> Blessing | None:
    lagna_sign = int(chart.lagna_lon // 30)
    benefics_in_kendra = []
    for b in BENEFICS:
        lon = chart.positions.get(b)
        if lon is None:
            continue
        h = _planet_house(lon, lagna_sign)
        if h in KENDRAS:
            benefics_in_kendra.append((b, h))
    if len(benefics_in_kendra) >= 3:
        return Blessing(
            code="PADMA_YOGA",
            name="Padma Yoga (lotus)",
            strength="STRONG",
            category="classical",
            involves=[b for b, _ in benefics_in_kendra],
            evidence=f"≥3 benefics in kendras: {benefics_in_kendra}",
            classical_source="Phaladeepika Ch.6; Saravali Ch.40",
            description="Wealth, fame, dignity, long life, happy family.",
            activation="Express through public-facing service that requires multiple talents.",
        )
    return None


# ─── Kahala Yoga (4th & 9th lord exchange/conjunction, lagna lord strong) ──
def detect_kahala_yoga(chart) -> Blessing | None:
    lagna_sign = int(chart.lagna_lon // 30)
    h4_lord = _lord_of_house(4, lagna_sign)
    h9_lord = _lord_of_house(9, lagna_sign)
    h1_lord = _lord_of_house(1, lagna_sign)
    h4_lon = chart.positions.get(h4_lord)
    h9_lon = chart.positions.get(h9_lord)
    h1_lon = chart.positions.get(h1_lord)
    if not all(x is not None for x in (h4_lon, h9_lon, h1_lon)):
        return None
    if int(h4_lon // 30) == int(h9_lon // 30) and _is_in_own_or_exalted(h1_lord, h1_lon):
        return Blessing(
            code="KAHALA_YOGA",
            name="Kahala Yoga",
            strength="STRONG",
            category="classical",
            involves=[h4_lord, h9_lord, h1_lord],
            evidence=f"H4 lord {h4_lord} conjunct H9 lord {h9_lord}; H1 lord {h1_lord} strong",
            classical_source="Phaladeepika Ch.6",
            description="Commands respect, wealth via lineage, learned, prosperous.",
            activation="Honor family tradition; build career bridging dharma and home.",
        )
    return None


# ─── Veena, Bheri, Mridanga — based on count of strong planets ─────────────
def detect_pancha_instrument_yogas(chart) -> list[Blessing]:
    """Counts how many planets are in own/exalted in kendra/trikona — based on
    classical 7 planets (excluding nodes)."""
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    n_strong_in_good_house = 0
    strong_list = []
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        lon = chart.positions.get(p)
        if lon is None:
            continue
        h = _planet_house(lon, lagna_sign)
        if (h in KENDRAS or h in TRIKONAS) and _is_in_own_or_exalted(p, lon):
            n_strong_in_good_house += 1
            strong_list.append(p)
    yogas = {
        7: ("Veena", "musical/artistic gift, wealth, fame in art or culture"),
        6: ("Damaru", "fame and prosperity"),
        5: ("Pasha", "wealth from many sources, longevity"),
        4: ("Kedara", "wealth from agriculture/land, prosperity"),
        3: ("Sula", "courage, valor, athletic prowess"),
        2: ("Yuga", "harmony"),
        1: ("Gola", "single-pointed pursuit"),
    }
    if n_strong_in_good_house >= 3:
        name, mean = yogas.get(n_strong_in_good_house, ("Multi-graha yoga", ""))
        out.append(Blessing(
            code=f"INSTRUMENT_YOGA_{n_strong_in_good_house}",
            name=f"{name} Yoga ({n_strong_in_good_house} strong planets in kendra/trikona)",
            strength="SUPREME" if n_strong_in_good_house >= 5 else "STRONG",
            category="classical",
            involves=strong_list,
            evidence=f"{n_strong_in_good_house} planets ({strong_list}) in own/exalted in kendra/trikona",
            classical_source="Phaladeepika Ch.6",
            description=mean,
            activation="Cultivate the qualities of all involved planets; multiple talents converge.",
        ))
    return out


# ─── Vargottama-as-blessing ────────────────────────────────────────────────
def detect_vargottama_blessing(chart) -> Blessing | None:
    if not getattr(chart, "vargottama", None):
        return None
    return Blessing(
        code="VARGOTTAMA",
        name="Vargottama planet(s)",
        strength="MODERATE",
        category="classical",
        involves=chart.vargottama,
        evidence=f"Vargottama: {chart.vargottama} (same sign in D1 and D9)",
        classical_source="BPHS Ch.7",
        description=("Vargottama planets carry their D1 strength fully into "
                     "the navamsa — doubled stability and reliability."),
        activation=f"Lean on {chart.vargottama} significations as the most "
                   "consistent assets across all life domains.",
    )


# ─── Exalted planet in kendra ──────────────────────────────────────────────
def detect_exalted_in_kendra(chart) -> list[Blessing]:
    out = []
    lagna_sign = int(chart.lagna_lon // 30)
    for planet, exalt_sign in EXALTATION_SIGN.items():
        lon = chart.positions.get(planet)
        if lon is None:
            continue
        if int(lon // 30) != exalt_sign:
            continue
        h = _planet_house(lon, lagna_sign)
        if h in KENDRAS:
            out.append(Blessing(
                code=f"EXALTED_KENDRA_{planet.upper()}",
                name=f"{planet} exalted in kendra H{h}",
                strength="STRONG",
                category="classical",
                involves=[planet, f"H{h}"],
                evidence=f"{planet} exalted in {SIGN_NAMES[exalt_sign]} (H{h})",
                classical_source="BPHS Ch.7; Phaladeepika Ch.6",
                description=(f"{planet} produces full positive results — lifelong "
                             "asset and reliable strength in its dasha periods."),
                activation=f"Build life around {planet}'s significations; this is your strongest leverage.",
            ))
    return out


# ─── Aggregator ────────────────────────────────────────────────────────────
def detect_all(chart) -> list[Blessing]:
    out: list[Blessing] = []
    out.extend(detect_pancha_mahapurusha(chart))
    out.extend(detect_raja_yogas(chart))
    out.extend(detect_dhana_yogas(chart))
    out.extend(detect_vipareeta_raja_yoga(chart))
    out.extend(detect_neecha_bhanga(chart))
    g = detect_gajakesari(chart)
    if g: out.append(g)
    out.extend(detect_lunar_yogas(chart))
    cm = detect_chandra_mangal(chart)
    if cm: out.append(cm)
    a = detect_adhi_yoga(chart)
    if a: out.append(a)
    lak = detect_lakshmi_yoga(chart)
    if lak: out.append(lak)
    sar = detect_saraswati_yoga(chart)
    if sar: out.append(sar)
    out.extend(detect_solar_yogas(chart))
    sh = detect_shankha_yoga(chart)
    if sh: out.append(sh)
    pad = detect_padma_yoga(chart)
    if pad: out.append(pad)
    kah = detect_kahala_yoga(chart)
    if kah: out.append(kah)
    out.extend(detect_pancha_instrument_yogas(chart))
    vg = detect_vargottama_blessing(chart)
    if vg: out.append(vg)
    out.extend(detect_exalted_in_kendra(chart))

    # Sort: SUPREME → STRONG → MODERATE → LATENT
    rank = {"SUPREME": 4, "STRONG": 3, "MODERATE": 2, "LATENT": 1}
    out.sort(key=lambda b: -rank.get(b.strength, 0))
    return out


def summary(chart) -> dict:
    blessings = detect_all(chart)
    by_strength = {"SUPREME": [], "STRONG": [], "MODERATE": [], "LATENT": []}
    for b in blessings:
        by_strength[b.strength].append({
            "code": b.code, "name": b.name, "category": b.category,
            "involves": b.involves, "evidence": b.evidence,
            "source": b.classical_source, "description": b.description,
            "activation": b.activation,
        })
    return {
        "total_blessings": len(blessings),
        "by_strength": by_strength,
        "category_counts": {
            cat: sum(1 for b in blessings if b.category == cat)
            for cat in ("mahapurusha", "raja", "dhana", "viparita",
                        "neecha_bhanga", "adhi", "gajakesari", "sunapha_etc",
                        "classical")
        },
    }
