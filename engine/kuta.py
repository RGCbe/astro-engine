"""
Ashta-Kuta — 8-fold marriage compatibility (36-point system).

Used for Hindu marriage matching (Guna Milan). Each kuta scores
compatibility on a different dimension:

    1. Varna       (1 pt)  — spiritual class compatibility
    2. Vasya       (2 pt)  — mutual control / dominance
    3. Tara        (3 pt)  — fortune / lifespan
    4. Yoni        (4 pt)  — sexual compatibility (animal symbolism)
    5. Graha Maitri(5 pt)  — planetary friendship of moon-sign lords
    6. Gana        (6 pt)  — temperament (Deva/Manushya/Rakshasa)
    7. Bhakoot     (7 pt)  — finance + family
    8. Nadi        (8 pt)  — physiological compatibility

Total: 36 points. Conventional wisdom:
    < 18 → poor match
    18-24 → acceptable
    24-32 → good
    > 32 → excellent

PLUS doshas:
    Mangal Dosha (Mars in 1/2/4/7/8/12 from Lagna or Moon)
    Nadi Dosha (same Nadi for both — strict avoidance)

Source: Brihat Parashara Hora Shastra Ch.74-75, Muhurtha Chintamani.

API:
    score = match_kuta(boy_moon_lon, girl_moon_lon)
    full = full_compatibility(boy_chart, girl_chart)
"""
from __future__ import annotations

from dataclasses import dataclass

from engine.dasha import NAKSHATRA_LORDS_VIMSHOTTARI, _nakshatra_index

NAKSHATRA_NAMES = (
    "Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
)

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# 27 nakshatra → Yoni animal (BPHS Ch.74)
YONI = (
    "Horse", "Elephant", "Sheep", "Serpent", "Serpent", "Dog",
    "Cat", "Sheep", "Cat", "Rat", "Rat", "Cow",
    "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer",
    "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse",
    "Lion", "Cow", "Elephant",
)

# Yoni compatibility matrix (animal x animal): max 4 pts
# Same animal of opposite gender = 4
# Friendly = 3, Neutral = 2, Enemy = 1, Worst (cat-rat etc) = 0
YONI_FRIENDS = {
    "Horse": ["Horse"], "Elephant": ["Elephant"], "Sheep": ["Sheep"],
    "Serpent": ["Serpent"], "Dog": ["Dog"], "Cat": ["Cat"],
    "Rat": ["Rat"], "Cow": ["Cow"], "Buffalo": ["Buffalo"],
    "Tiger": ["Tiger"], "Deer": ["Deer"], "Monkey": ["Monkey"],
    "Mongoose": ["Mongoose"], "Lion": ["Lion"],
}
YONI_ENEMIES = {
    ("Cow", "Tiger"), ("Tiger", "Cow"),
    ("Elephant", "Lion"), ("Lion", "Elephant"),
    ("Horse", "Buffalo"), ("Buffalo", "Horse"),
    ("Dog", "Deer"), ("Deer", "Dog"),
    ("Snake", "Mongoose"), ("Serpent", "Mongoose"), ("Mongoose", "Serpent"),
    ("Cat", "Rat"), ("Rat", "Cat"),
    ("Monkey", "Sheep"), ("Sheep", "Monkey"),
}

# Gana: nakshatra → Deva/Manushya/Rakshasa
GANA = (
    "Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya",
    "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya",
    "Deva", "Rakshasa", "Deva", "Rakshasa", "Deva", "Rakshasa",
    "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Rakshasa",
    "Manushya", "Manushya", "Deva",
)

# Nadi: nakshatra → Adi/Madhya/Antya
NADI = (
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya",
)

# Varna by Moon sign (4 classes)
VARNA = {
    "Cancer": "Brahmin", "Scorpio": "Brahmin", "Pisces": "Brahmin",
    "Leo": "Kshatriya", "Sagittarius": "Kshatriya", "Aries": "Kshatriya",
    "Taurus": "Vaishya", "Virgo": "Vaishya", "Capricorn": "Vaishya",
    "Gemini": "Shudra", "Libra": "Shudra", "Aquarius": "Shudra",
}
VARNA_RANK = {"Brahmin": 4, "Kshatriya": 3, "Vaishya": 2, "Shudra": 1}

# Vasya group by Moon sign
VASYA_GROUPS = {
    "Aries": ["Leo", "Scorpio"],
    "Taurus": ["Cancer", "Libra"],
    "Gemini": ["Virgo"],
    "Cancer": ["Scorpio", "Sagittarius"],
    "Leo": ["Libra"],
    "Virgo": ["Pisces", "Gemini"],
    "Libra": ["Capricorn", "Virgo"],
    "Scorpio": ["Cancer"],
    "Sagittarius": ["Pisces"],
    "Capricorn": ["Aries", "Aquarius"],
    "Aquarius": ["Aries"],
    "Pisces": ["Capricorn"],
}

# Planetary friendships (for Graha Maitri)
FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"},
    "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}


@dataclass
class KutaResult:
    boy_moon: str
    girl_moon: str
    boy_nakshatra: str
    girl_nakshatra: str
    varna: tuple[int, int]       # (got, max)
    vasya: tuple[int, int]
    tara: tuple[int, int]
    yoni: tuple[int, int]
    graha_maitri: tuple[int, int]
    gana: tuple[int, int]
    bhakoot: tuple[int, int]
    nadi: tuple[int, int]
    total: tuple[int, int]
    notes: list[str]
    nadi_dosha: bool
    bhakoot_dosha: bool
    verdict: str


def _moon_sign(lon: float) -> str:
    return SIGNS[int(lon % 360 // 30)]


def _nak_idx(lon: float) -> int:
    return _nakshatra_index(lon)


# ─── individual kutas ──────────────────────────────────────────────────────
def _varna(boy_sign: str, girl_sign: str) -> int:
    bv = VARNA[boy_sign]; gv = VARNA[girl_sign]
    return 1 if VARNA_RANK[bv] >= VARNA_RANK[gv] else 0


def _vasya(boy_sign: str, girl_sign: str) -> int:
    if girl_sign in VASYA_GROUPS.get(boy_sign, []):
        return 2
    if boy_sign in VASYA_GROUPS.get(girl_sign, []):
        return 1
    return 0


def _tara(boy_nak_idx: int, girl_nak_idx: int) -> int:
    """Calculated as (girl_nak - boy_nak) % 9 — auspicious if remainder is even."""
    diff = (girl_nak_idx - boy_nak_idx) % 9
    auspicious_remainders = {2, 4, 6, 8, 0}      # 0 means 9 (multiple)
    return 3 if diff in auspicious_remainders else 0


def _yoni(boy_nak_idx: int, girl_nak_idx: int) -> int:
    by = YONI[boy_nak_idx]; gy = YONI[girl_nak_idx]
    if by == gy:
        return 4
    if (by, gy) in YONI_ENEMIES:
        return 0
    return 2


def _graha_maitri(boy_sign: str, girl_sign: str) -> int:
    bl = SIGN_LORDS[boy_sign]; gl = SIGN_LORDS[girl_sign]
    if bl == gl:
        return 5
    if gl in FRIENDS.get(bl, set()) and bl in FRIENDS.get(gl, set()):
        return 5
    if gl in FRIENDS.get(bl, set()) or bl in FRIENDS.get(gl, set()):
        return 4
    return 1


def _gana(boy_nak_idx: int, girl_nak_idx: int, boy_sign: str = "", girl_sign: str = "") -> int:
    bg = GANA[boy_nak_idx]; gg = GANA[girl_nak_idx]
    if bg == gg:
        return 6
        
    # Check for Gana Dosha cancellation (same Rashi Lord or mutual friendship)
    if boy_sign and girl_sign and boy_sign in SIGNS and girl_sign in SIGNS:
        RASHI_LORDS = {
            "Aries": "Mars", "Scorpio": "Mars",
            "Taurus": "Venus", "Libra": "Venus",
            "Gemini": "Mercury", "Virgo": "Mercury",
            "Cancer": "Moon", "Leo": "Sun",
            "Sagittarius": "Jupiter", "Pisces": "Jupiter",
            "Capricorn": "Saturn", "Aquarius": "Saturn"
        }
        lord1 = RASHI_LORDS.get(boy_sign)
        lord2 = RASHI_LORDS.get(girl_sign)
        
        # Rule 1: Same Rashi Lord
        if lord1 == lord2 and lord1 is not None:
            return 6
            
        # Rule 2: Mutual friendship of Rashi Lords
        FRIENDS = {
            "Sun": {"Moon", "Mars", "Jupiter"},
            "Moon": {"Sun", "Mercury"},
            "Mars": {"Sun", "Moon", "Jupiter"},
            "Mercury": {"Sun", "Venus"},
            "Jupiter": {"Sun", "Moon", "Mars"},
            "Venus": {"Mercury", "Saturn"},
            "Saturn": {"Mercury", "Venus"}
        }
        if lord1 in FRIENDS and lord2 in FRIENDS[lord1] and lord2 in FRIENDS and lord1 in FRIENDS[lord2]:
            return 6

    pair = {bg, gg}
    if pair == {"Deva", "Manushya"}:
        return 5
    if pair == {"Manushya", "Rakshasa"}:
        return 1
    return 0     # Deva-Rakshasa


def _bhakoot(boy_sign: str, girl_sign: str) -> int:
    """Distance between Moon signs. 6/8 and 9/5 and 12/2 -> 0; else 7.
    
    Includes classical cancellation rules from Muhurta Chintamani:
    1. Same Rashi Lord (Aries/Scorpio, Taurus/Libra, Capricorn/Aquarius).
    2. Mutual Friendship of Rashi Lords:
       - Leo (Sun) and Cancer (Moon)
       - Cancer (Moon) and Sagittarius (Jupiter)
       - Leo (Sun) and Pisces (Jupiter)
       - Capricorn (Saturn) and Gemini (Mercury)
       - Pisces (Jupiter) and Aries (Mars)
    """
    bi = SIGNS.index(boy_sign); gi = SIGNS.index(girl_sign)
    diff = abs(bi - gi)
    if diff > 6:
        diff = 12 - diff
    
    bad_distances = {1, 5}  # 2-12 and 6-8 axes
    if diff not in bad_distances:
        return 7
        
    # Check for Bhakoot Dosha cancellation
    RASHI_LORDS_BH = {
        "Aries": "Mars", "Scorpio": "Mars",
        "Taurus": "Venus", "Libra": "Venus",
        "Gemini": "Mercury", "Virgo": "Mercury",
        "Cancer": "Moon", "Leo": "Sun",
        "Sagittarius": "Jupiter", "Pisces": "Jupiter",
        "Capricorn": "Saturn", "Aquarius": "Saturn"
    }
    
    lord1 = RASHI_LORDS_BH.get(boy_sign)
    lord2 = RASHI_LORDS_BH.get(girl_sign)
    
    # Rule 1: Same Rashi Lord
    if lord1 == lord2 and lord1 is not None:
        return 7
        
    # Rule 2: Mutual friendship of Rashi Lords
    FRIENDS = {
        "Sun": {"Moon", "Mars", "Jupiter"},
        "Moon": {"Sun", "Mercury"},
        "Mars": {"Sun", "Moon", "Jupiter"},
        "Mercury": {"Sun", "Venus"},
        "Jupiter": {"Sun", "Moon", "Mars"},
        "Venus": {"Mercury", "Saturn"},
        "Saturn": {"Mercury", "Venus"}
    }
    
    if lord1 in FRIENDS and lord2 in FRIENDS[lord1] and lord2 in FRIENDS and lord1 in FRIENDS[lord2]:
        return 7
        
    return 0

# Newline to separate from def _nadi
def _nadi(boy_nak_idx: int, girl_nak_idx: int, boy_sign: str = "", girl_sign: str = "") -> int:
    """Same nadi -> 0 (Nadi Dosha). Different -> 8.
    
    Includes classical cancellation rules from Muhurta Chintamani:
    1. If either Nakshatra is Rohini, Mrigashira, Ardra, Pushya, Krittika, Jyeshtha, Shravana, Uttara Bhadrapada, or Revati.
    2. Same Rasi, different Nakshatras.
    3. Same Nakshatra, different Rasis.
    """
    # 1. Exempted Nakshatras (Krittika, Rohini, Mrigashira, Ardra, Pushya, Jyeshtha, Shravana, Uttara Bhadrapada, Revati)
    exempted_nak = {2, 3, 4, 5, 7, 17, 21, 25, 26}
    if boy_nak_idx in exempted_nak or girl_nak_idx in exempted_nak:
        return 8
        
    # Look up rasi indices if signs are provided
    if boy_sign and girl_sign and boy_sign in SIGNS and girl_sign in SIGNS:
        bi = SIGNS.index(boy_sign)
        gi = SIGNS.index(girl_sign)
        # 2. Same Rasi, different Nakshatras
        if bi == gi and boy_nak_idx != girl_nak_idx:
            return 8
        # 3. Same Nakshatra, different Rasis
        if boy_nak_idx == girl_nak_idx and bi != gi:
            return 8

    return 0 if NADI[boy_nak_idx] == NADI[girl_nak_idx] else 8


# ─── Public API ───────────────────────────────────────────────────────────
def match_kuta(boy_moon_lon: float, girl_moon_lon: float) -> KutaResult:
    boy_sign = _moon_sign(boy_moon_lon)
    girl_sign = _moon_sign(girl_moon_lon)
    boy_nak = _nak_idx(boy_moon_lon)
    girl_nak = _nak_idx(girl_moon_lon)

    var = _varna(boy_sign, girl_sign)
    vas = _vasya(boy_sign, girl_sign)
    tar = _tara(boy_nak, girl_nak)
    yon = _yoni(boy_nak, girl_nak)
    grh = _graha_maitri(boy_sign, girl_sign)
    gan = _gana(boy_nak, girl_nak, boy_sign, girl_sign)
    bha = _bhakoot(boy_sign, girl_sign)
    nad = _nadi(boy_nak, girl_nak, boy_sign, girl_sign)

    total = var + vas + tar + yon + grh + gan + bha + nad
    notes = []
    nadi_dosha = nad == 0
    bhakoot_dosha = bha == 0

    if nadi_dosha:
        notes.append("⚠️ Nadi Dosha — same Nadi (physiological incompatibility)")
    if bhakoot_dosha:
        notes.append("⚠️ Bhakoot Dosha — adverse Moon-sign distance")
    if gan == 0:
        notes.append("⚠️ Gana mismatch — Deva-Rakshasa (temperament clash)")
    if yon == 0:
        notes.append("⚠️ Yoni enemies — sexual incompatibility")

    if total < 18:
        verdict = "POOR (avoid)"
    elif total < 24:
        verdict = "ACCEPTABLE (with remedies)"
    elif total < 32:
        verdict = "GOOD"
    else:
        verdict = "EXCELLENT"

    return KutaResult(
        boy_moon=boy_sign, girl_moon=girl_sign,
        boy_nakshatra=NAKSHATRA_NAMES[boy_nak],
        girl_nakshatra=NAKSHATRA_NAMES[girl_nak],
        varna=(var, 1), vasya=(vas, 2), tara=(tar, 3), yoni=(yon, 4),
        graha_maitri=(grh, 5), gana=(gan, 6), bhakoot=(bha, 7), nadi=(nad, 8),
        total=(total, 36),
        notes=notes,
        nadi_dosha=nadi_dosha, bhakoot_dosha=bhakoot_dosha,
        verdict=verdict,
    )


def mangal_dosha(chart: dict) -> dict:
    """Mars in 1, 2, 4, 7, 8, or 12 from Lagna or Moon = Mangal Dosha.

    chart: {"lagna": longitude, "positions": {"Mars": lon, "Moon": lon, ...}}
    """
    if "Mars" not in chart["positions"]:
        return {"is_mangalik": False, "from": []}
    lag_idx = int(chart["lagna"] // 30)
    moon_idx = int(chart["positions"]["Moon"] // 30)
    mars_idx = int(chart["positions"]["Mars"] // 30)
    bad_houses = {1, 2, 4, 7, 8, 12}
    house_from_lagna = ((mars_idx - lag_idx) % 12) + 1
    house_from_moon = ((mars_idx - moon_idx) % 12) + 1
    flags = []
    if house_from_lagna in bad_houses:
        flags.append(f"from Lagna (Mars in {house_from_lagna}th)")
    if house_from_moon in bad_houses:
        flags.append(f"from Moon (Mars in {house_from_moon}th)")
    return {
        "is_mangalik": bool(flags),
        "from": flags,
        "house_from_lagna": house_from_lagna,
        "house_from_moon": house_from_moon,
    }
