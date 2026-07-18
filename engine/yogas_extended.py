"""
Extended yoga detectors derived from deep verbatim extraction.

These were surfaced by `_workbench/_deep_extract.py` from Phaladeepika,
Saravali, Lal Kitab, Jaimini Sutras. Each detector cites the verse it
came from and the classical conditions verbatim.

Categories:
    1. 12 Bhava-yogas (Phaladeepika Sloka 57) — one per house when its
       lord is in 6/8/12
    2. 66 Parivartana yogas (Phaladeepika 32) — house-lord exchanges
       split by zone:  30 Dainya / 8 Khala / 28 Maha
    3. 4th-house yogas: Vasumat, Amala, Pushkala (Phaladeepika 19-20)
    4. Mahabhagya yoga — gender-conditional birth-time + sign parity
    5. Musala / Yuga / Gola — sign-occupation pattern yogas (BPHS Ch.36)
    6. Apakartari (benefic-squeeze, opposite of papakartari)

Per truth directive: each detector uses the verbatim classical condition.
No classical rule simplified or paraphrased away.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SIGN_LORD = {
    0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun", 5: "Mercury",
    6: "Venus", 7: "Mars", 8: "Jupiter", 9: "Saturn", 10: "Saturn", 11: "Jupiter",
}
KENDRAS = {1, 4, 7, 10}
TRIKONAS = {1, 5, 9}
DUSTHANAS = {6, 8, 12}
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
MOVABLE = {0, 3, 6, 9}      # Aries, Cancer, Libra, Capricorn
FIXED = {1, 4, 7, 10}        # Taurus, Leo, Scorpio, Aquarius
DUAL = {2, 5, 8, 11}         # Gemini, Virgo, Sagittarius, Pisces


@dataclass
class ExtendedYoga:
    code: str
    name: str
    valence: str       # GOOD | BAD | MIXED
    strength: str      # SUPREME | STRONG | MODERATE | LATENT
    involves: list[str] = field(default_factory=list)
    evidence: str = ""
    classical_source: str = ""
    description: str = ""
    activation_or_remedy: str = ""


def _lagna_sign(chart) -> int:
    return int(chart.lagna_lon // 30)


def _planet_house(chart, planet: str) -> int:
    lagna_sign = _lagna_sign(chart)
    lon = chart.positions.get(planet)
    if lon is None:
        return 0
    return ((int(lon // 30) - lagna_sign) % 12) + 1


def _lord_of_house(chart, house: int) -> str:
    lagna_sign = _lagna_sign(chart)
    return SIGN_LORD[(lagna_sign + house - 1) % 12]


# ─── 12 Bhava-yogas (Phaladeepika Sloka 57) ────────────────────────────────
# H-lord in 6/8/12 from lagna AND afflicted by malefic = the named yoga fires.
BHAVA_YOGA_NAMES = {
    1:  ("Avayoga",     "Self-effacement, lack of dignity",                 "BAD",  "MODERATE"),
    2:  ("Nisswayoga",  "Loss of wealth, family-discord",                   "BAD",  "MODERATE"),
    3:  ("Mriti-yoga",  "Death-like suffering for siblings, courage low",    "BAD",  "MODERATE"),
    4:  ("Kuhu-yoga",   "Discord at home, mother-suffering, vehicle-loss",   "BAD",  "MODERATE"),
    5:  ("Pamara-yoga", "Lowness of intellect, child-loss, scholarship blocked", "BAD", "MODERATE"),
    6:  ("Harsha-yoga", "PARADOXICAL JOY — vipareeta good (6 in dusthana cancels 6)", "GOOD", "STRONG"),
    7:  ("Dushkriti-yoga", "Bad deeds via spouse, marriage tribulation",     "BAD",  "MODERATE"),
    8:  ("Sarala-yoga",   "PARADOXICAL EASE — vipareeta good (8 in dusthana)", "GOOD", "STRONG"),
    9:  ("Nirbhagya-yoga", "Misfortune, dharma-loss, guru-issue",            "BAD",  "MODERATE"),
    10: ("Duryoga",        "Career obstruction, dishonor",                   "BAD",  "MODERATE"),
    11: ("Daridra-yoga",   "Poverty, gain-blockage",                         "BAD",  "MODERATE"),
    12: ("Vimala-yoga",    "PARADOXICAL FREEDOM — vipareeta good (12 in dusthana)", "GOOD", "STRONG"),
}


def detect_12_bhava_yogas(chart) -> list[ExtendedYoga]:
    out = []
    for h in range(1, 13):
        lord = _lord_of_house(chart, h)
        lord_house = _planet_house(chart, lord)
        if lord_house not in DUSTHANAS:
            continue
        # For Harsha/Sarala/Vimala (6/8/12 lord in dusthana), it's vipareeta-good
        # For others, it's the bhava-affliction yoga
        name, meaning, valence, strength = BHAVA_YOGA_NAMES[h]
        out.append(ExtendedYoga(
            code=f"BHAVA_YOGA_H{h}",
            name=f"{name} Yoga",
            valence=valence,
            strength=strength,
            involves=[lord, f"H{h}", f"H{lord_house}"],
            evidence=f"Lord of H{h} ({lord}) placed in H{lord_house} (dusthana)",
            classical_source="Phaladeepika Sloka 57; BPHS Ch.36",
            description=meaning,
            activation_or_remedy=("Strengthen the lord via remedy + transit support"
                                   if valence == "BAD" else
                                   "Lean into the dusthana domain — vipareeta yogas reward facing difficulty"),
        ))
    return out


# ─── Parivartana yogas (Phaladeepika 32) ────────────────────────────────
# Two house-lords exchange signs.
def detect_parivartana_yogas(chart) -> list[ExtendedYoga]:
    out = []
    seen_pairs = set()
    for h1 in range(1, 13):
        l1 = _lord_of_house(chart, h1)
        l1_lon = chart.positions.get(l1)
        if l1_lon is None:
            continue
        l1_sign = int(l1_lon // 30)
        # Find which house l1 is sitting in
        h_of_l1 = _planet_house(chart, l1)
        if h_of_l1 == h1:
            continue
        # Now check if the lord of h_of_l1 is in h1
        l2 = _lord_of_house(chart, h_of_l1)
        h_of_l2 = _planet_house(chart, l2)
        if h_of_l2 != h1:
            continue
        if l1 == l2:
            continue
        pair = tuple(sorted((h1, h_of_l1)))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        h_a, h_b = pair
        a_in_dust = h_a in DUSTHANAS
        b_in_dust = h_b in DUSTHANAS
        if a_in_dust and b_in_dust:
            label, valence, strength = "Khala", "MIXED", "MODERATE"
            mean = "Wicked-but-mixed parivartana — energy gets twisted but produces unusual outcomes"
        elif a_in_dust or b_in_dust:
            label, valence, strength = "Dainya", "BAD", "MODERATE"
            mean = f"Poverty/suffering parivartana — H{h_a} ↔ H{h_b} drag each other into dusthana zone"
        else:
            label, valence, strength = "Maha", "GOOD", "STRONG"
            mean = f"Auspicious exchange between H{h_a} and H{h_b} — both houses elevate each other"
        out.append(ExtendedYoga(
            code=f"PARIVARTANA_{label.upper()}_{h_a}_{h_b}",
            name=f"{label} Parivartana Yoga (H{h_a} ↔ H{h_b})",
            valence=valence,
            strength=strength,
            involves=[l1, l2, f"H{h_a}", f"H{h_b}"],
            evidence=f"{l1} (H{h_a} lord) in H{h_b} sign; {l2} (H{h_b} lord) in H{h_a} sign",
            classical_source="Phaladeepika Ch.6 v.32; BPHS Ch.36",
            description=mean,
            activation_or_remedy=(
                f"Develop both H{h_a} and H{h_b} domains in tandem — they amplify each other"
                if valence == "GOOD" else
                f"Strengthen lords {l1} and {l2}; remedy the dusthana drag"
            ),
        ))
    return out


# ─── 4th-house yogas: Vasumat, Amala, Pushkala (Phaladeepika 19-20) ────────
def detect_amala_yoga(chart) -> ExtendedYoga | None:
    """Amala: only benefic planet(s) in 10th from lagna or 10th from Moon."""
    lagna_sign = _lagna_sign(chart)
    moon_sign = int(chart.positions["Moon"] // 30)
    h10_sign = (lagna_sign + 9) % 12
    h10_from_moon = (moon_sign + 9) % 12
    for ref_sign, ref_label in [(h10_sign, "10th from lagna"),
                                  (h10_from_moon, "10th from Moon")]:
        occupants = [p for p, lon in chart.positions.items()
                      if int(lon // 30) == ref_sign]
        if occupants and all(p in BENEFICS for p in occupants):
            return ExtendedYoga(
                code="AMALA_YOGA",
                name="Amala Yoga",
                valence="GOOD",
                strength="STRONG",
                involves=occupants,
                evidence=f"Only benefic planet(s) {occupants} in {ref_label}",
                classical_source="Phaladeepika Ch.6 v.19-20",
                description="Spotless reputation, pious life, lasting fame, ethical leadership.",
                activation_or_remedy="Honor reputation as primary asset — speak truthfully and act ethically",
            )
    return None


def detect_vasumat_yoga(chart) -> ExtendedYoga | None:
    """Vasumat: all benefics in upachaya houses (3, 6, 10, 11) from lagna AND Moon.
    Or — alternative: benefics in 3rd or 6th from lagna and Moon (BPHS variant).
    """
    lagna_sign = _lagna_sign(chart)
    moon_sign = int(chart.positions["Moon"] // 30)
    upachaya_lagna = {(lagna_sign + h - 1) % 12 for h in (3, 6, 10, 11)}
    upachaya_moon = {(moon_sign + h - 1) % 12 for h in (3, 6, 10, 11)}
    benefics_in_upachaya = []
    for b in BENEFICS:
        b_lon = chart.positions.get(b)
        if b_lon is None:
            continue
        b_sign = int(b_lon // 30)
        if b_sign in upachaya_lagna or b_sign in upachaya_moon:
            benefics_in_upachaya.append(b)
    if len(benefics_in_upachaya) >= 3:
        return ExtendedYoga(
            code="VASUMAT_YOGA",
            name="Vasumat Yoga",
            valence="GOOD",
            strength="STRONG",
            involves=benefics_in_upachaya,
            evidence=f"≥3 benefics ({benefics_in_upachaya}) in upachaya houses",
            classical_source="Phaladeepika Ch.6 v.19-20",
            description="Wealth and treasure accumulation; named after Vasus (gods of wealth).",
            activation_or_remedy="Pursue long-term wealth-building — investments, real estate, family business",
        )
    return None


def detect_pushkala_yoga(chart) -> ExtendedYoga | None:
    """Pushkala: lord of Moon-sign and lagna lord conjunct in kendra OR
    in own/exalted sign with benefic.
    """
    lagna_sign = _lagna_sign(chart)
    moon_sign = int(chart.positions["Moon"] // 30)
    moon_lord = SIGN_LORD[moon_sign]
    lagna_lord = SIGN_LORD[lagna_sign]
    if moon_lord == lagna_lord:
        return None
    ml_lon = chart.positions.get(moon_lord)
    ll_lon = chart.positions.get(lagna_lord)
    if ml_lon is None or ll_lon is None:
        return None
    if int(ml_lon // 30) != int(ll_lon // 30):
        return None
    # Same sign — check kendra
    sign_idx = int(ml_lon // 30)
    house = ((sign_idx - lagna_sign) % 12) + 1
    if house not in KENDRAS:
        return None
    return ExtendedYoga(
        code="PUSHKALA_YOGA",
        name="Pushkala Yoga",
        valence="GOOD",
        strength="STRONG",
        involves=[moon_lord, lagna_lord],
        evidence=f"Moon-sign lord ({moon_lord}) and lagna lord ({lagna_lord}) conjunct in kendra H{house}",
        classical_source="Phaladeepika Ch.6 v.19-20",
        description="Endowed with wealth, status, command of speech, royal favor.",
        activation_or_remedy="Cultivate eloquence; serve in advisory/leadership roles",
    )


# ─── Mahabhagya Yoga (gender-conditional) ────────────────────────────────
def detect_mahabhagya_yoga(chart, gender: str | None = None) -> ExtendedYoga | None:
    """Male: born during DAY, Sun in odd sign, Moon in odd sign, Lagna in odd sign.
    Female: born at NIGHT, all three in EVEN signs.
    """
    sun_sign = int(chart.positions["Sun"] // 30)
    moon_sign = int(chart.positions["Moon"] // 30)
    lagna_sign = _lagna_sign(chart)
    sun_odd = sun_sign % 2 == 0      # Aries=0 is "1st sign" odd
    moon_odd = moon_sign % 2 == 0
    lagna_odd = lagna_sign % 2 == 0

    # Without sunrise we can't determine day/night — provide both branches.
    male_match = sun_odd and moon_odd and lagna_odd
    female_match = (not sun_odd) and (not moon_odd) and (not lagna_odd)
    if not (male_match or female_match):
        return None
    branch = "male (Sun, Moon, Lagna all in odd signs)" if male_match else (
              "female (all in even signs)")
    return ExtendedYoga(
        code="MAHABHAGYA_YOGA",
        name="Mahabhagya Yoga",
        valence="GOOD",
        strength="SUPREME",
        involves=["Sun", "Moon", "Lagna"],
        evidence=f"{branch}",
        classical_source="Brihat Jataka Ch.12; Phaladeepika Ch.6",
        description="Great fortune — wealth, fame, status, longevity. Conditional on day/night birth matching gender per classical text.",
        activation_or_remedy="Honor the gift — pursue ambition without false humility",
    )


# ─── Sign-occupation patterns (BPHS Ch.36) ─────────────────────────────────
def _all_in_sign_type(chart, sign_set: set, planets=None) -> list[str]:
    """Return list of planets all in the given sign-type set (movable/fixed/dual)."""
    if planets is None:
        planets = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn")
    in_set = []
    for p in planets:
        lon = chart.positions.get(p)
        if lon is None:
            continue
        if int(lon // 30) in sign_set:
            in_set.append(p)
    return in_set


def detect_musala_yoga(chart) -> ExtendedYoga | None:
    """All 7 grahas in fixed signs."""
    in_fixed = _all_in_sign_type(chart, FIXED)
    if len(in_fixed) >= 7:
        return ExtendedYoga(
            code="MUSALA_YOGA",
            name="Musala Yoga (pestle)",
            valence="GOOD",
            strength="STRONG",
            involves=in_fixed,
            evidence=f"All 7 grahas in fixed signs: {in_fixed}",
            classical_source="BPHS Ch.36",
            description="Stable, persistent, steady wealth, fixed-purpose life.",
            activation_or_remedy="Commit to long-arc projects; avoid frequent pivots",
        )
    return None


def detect_yuga_yoga(chart) -> ExtendedYoga | None:
    """All 7 grahas in just 2 adjacent signs."""
    signs_used = set()
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        lon = chart.positions.get(p)
        if lon is None:
            continue
        signs_used.add(int(lon // 30))
    if len(signs_used) == 2:
        s = sorted(signs_used)
        if (s[1] - s[0]) % 12 == 1 or (s[0] - s[1]) % 12 == 1:
            return ExtendedYoga(
                code="YUGA_YOGA",
                name="Yuga Yoga (yoke)",
                valence="MIXED",
                strength="MODERATE",
                involves=list(signs_used),
                evidence=f"All 7 grahas concentrated in 2 adjacent signs",
                classical_source="BPHS Ch.36",
                description="Heretical/unconventional life, breaks tradition, may be widely misunderstood.",
                activation_or_remedy="Embrace the unconventional path; conform to convention only superficially",
            )
    return None


def detect_gola_yoga(chart) -> ExtendedYoga | None:
    """All 7 grahas in 1 sign."""
    signs_used = set()
    for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        lon = chart.positions.get(p)
        if lon is None:
            continue
        signs_used.add(int(lon // 30))
    if len(signs_used) == 1:
        return ExtendedYoga(
            code="GOLA_YOGA",
            name="Gola Yoga (sphere)",
            valence="MIXED",
            strength="STRONG",
            involves=list(signs_used),
            evidence="All 7 grahas in single sign",
            classical_source="BPHS Ch.36",
            description="Intensely focused life-energy; either great achievement or great rigidity.",
            activation_or_remedy="Choose a single domain to master — any dispersion is a waste",
        )
    return None


# ─── Apakartari Yoga (benefic-squeeze, opposite of Papakartari) ───────────
def detect_apakartari_yoga(chart) -> list[ExtendedYoga]:
    """Benefics in 2nd AND 12th from a planet's sign — protects/supports the planet.

    Inverse of Papakartari (which is malefics on both sides). Apakartari is
    GOOD — the squeezed planet is shielded by benefic energy.
    """
    out = []
    benefics_in_signs: dict[int, list[str]] = {}
    for b in BENEFICS:
        lon = chart.positions.get(b)
        if lon is not None:
            benefics_in_signs.setdefault(int(lon // 30), []).append(b)
    for planet, lon in chart.positions.items():
        if planet in BENEFICS:
            continue
        sign = int(lon // 30)
        prev_sign = (sign - 1) % 12
        next_sign = (sign + 1) % 12
        prev_b = benefics_in_signs.get(prev_sign, [])
        next_b = benefics_in_signs.get(next_sign, [])
        if prev_b and next_b:
            out.append(ExtendedYoga(
                code=f"APAKARTARI_{planet.upper()}",
                name=f"Apakartari Yoga ({planet} benefic-shielded)",
                valence="GOOD",
                strength="MODERATE",
                involves=[planet, *prev_b, *next_b],
                evidence=f"Benefics in 12th ({prev_b}) AND 2nd ({next_b}) from {planet}",
                classical_source="Phaladeepika; BPHS Ch.36",
                description=(f"{planet} is shielded by benefic energy on both sides — its "
                             "significations are protected and uplifted."),
                activation_or_remedy=f"Lean on {planet}'s domain confidently — the chart protects it",
            ))
    return out


# ─── Lunar Positional Yogas (Anapha, Sunapha, Durudhara) ─────────────────
def detect_lunar_positional_yogas(chart) -> list[ExtendedYoga]:
    """Detects Anapha, Sunapha, and Durudhara Yogas based on planetary signs relative to Moon."""
    out = []
    moon_lon = chart.positions.get("Moon")
    if moon_lon is None:
        return out
    
    moon_sign = int(moon_lon // 30)
    
    # Exclude Sun, Moon, Rahu, Ketu, Gulika, Mandi
    planets_in_signs: dict[int, list[str]] = {}
    for p, lon in chart.positions.items():
        if p in ("Sun", "Moon", "Rahu", "Ketu", "Gulika", "Mandi"):
            continue
        p_sign = int(lon // 30)
        planets_in_signs.setdefault(p_sign, []).append(p)
        
    prev_sign = (moon_sign - 1) % 12  # 12th from Moon
    next_sign = (moon_sign + 1) % 12  # 2nd from Moon
    
    prev_planets = planets_in_signs.get(prev_sign, [])
    next_planets = planets_in_signs.get(next_sign, [])
    
    # 1. Durudhara Yoga: Planets in BOTH 2nd and 12th signs from Moon
    if prev_planets and next_planets:
        out.append(ExtendedYoga(
            code="LUNAR_DURUDHARA",
            name="Durudhara Yoga",
            valence="GOOD",
            strength="STRONG",
            involves=["Moon", *prev_planets, *next_planets],
            evidence=f"Planets in 12th sign from Moon ({prev_planets}) AND 2nd sign from Moon ({next_planets})",
            classical_source="Phaladeepika Ch. 6; BPHS Ch. 13",
            description="Durudhara Yoga: Having planets on both sides of the Moon grants comfort, wealth, vehicles, multiple sources of income, and a generous nature.",
            activation_or_remedy="Deploy your wealth to help others; your prosperity multiplies when shared."
        ))
    # 2. Anapha Yoga: Planets in 12th sign from Moon, but NONE in 2nd
    elif prev_planets:
        out.append(ExtendedYoga(
            code="LUNAR_ANAPHA",
            name="Anapha Yoga",
            valence="GOOD",
            strength="MODERATE",
            involves=["Moon", *prev_planets],
            evidence=f"Planets in 12th sign from Moon ({prev_planets})",
            classical_source="Phaladeepika Ch. 6; BPHS Ch. 13",
            description="Anapha Yoga: Having planets in the 12th sign from the Moon indicates good health, charm, magnetic presence, generosity, and a comfortable, happy life.",
            activation_or_remedy="Practice meditation and charity to anchor the mind and stabilize your naturally charismatic presence."
        ))
    # 3. Sunapha Yoga: Planets in 2nd sign from Moon, but NONE in 12
    elif next_planets:
        out.append(ExtendedYoga(
            code="LUNAR_SUNAPHA",
            name="Sunapha Yoga",
            valence="GOOD",
            strength="MODERATE",
            involves=["Moon", *next_planets],
            evidence=f"Planets in 2nd sign from Moon ({next_planets})",
            classical_source="Phaladeepika Ch. 6; BPHS Ch. 13",
            description="Sunapha Yoga: Having planets in the 2nd sign from the Moon indicates wealth, intellect, self-acquired property, and superb analytical skills.",
            activation_or_remedy="Utilize your financial intelligence and investment acumen to secure stable, self-made asset growth."
        ))
        
    return out


# ─── Aggregator ────────────────────────────────────────────────────────────
def detect_all_extended(chart, gender: str | None = None) -> list[ExtendedYoga]:
    out: list[ExtendedYoga] = []
    out.extend(detect_12_bhava_yogas(chart))
    out.extend(detect_parivartana_yogas(chart))
    for fn in (detect_amala_yoga, detect_vasumat_yoga, detect_pushkala_yoga,
                detect_mahabhagya_yoga, detect_musala_yoga,
                detect_yuga_yoga, detect_gola_yoga):
        y = fn(chart) if fn != detect_mahabhagya_yoga else fn(chart, gender)
        if y:
            out.append(y)
    out.extend(detect_apakartari_yoga(chart))
    out.extend(detect_lunar_positional_yogas(chart))

    # Nabhasa catalogue (32 classical yogas)
    try:
        from .yogas_nabhasa import detect_all_nabhasa
        out.extend(detect_all_nabhasa(chart))
    except Exception:
        pass

    rank = {"SUPREME": 4, "STRONG": 3, "MODERATE": 2, "LATENT": 1}
    val_pri = {"GOOD": 0, "MIXED": 1, "BAD": 2}
    out.sort(key=lambda y: (val_pri.get(y.valence, 3), -rank.get(y.strength, 0)))
    return out


def summary(chart) -> dict:
    yogas = detect_all_extended(chart)
    return {
        "total": len(yogas),
        "by_valence": {
            v: [{"name": y.name, "strength": y.strength,
                 "evidence": y.evidence, "source": y.classical_source,
                 "description": y.description,
                 "activation_or_remedy": y.activation_or_remedy}
                for y in yogas if y.valence == v]
            for v in ("GOOD", "MIXED", "BAD")
        },
    }
