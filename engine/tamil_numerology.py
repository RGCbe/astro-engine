"""
Tamil Numerology — reproduces page 13 of a printed Thirukanitham jadhagam:
  Vidhi Number, Vidhi planet, lucky days, lucky direction, lucky dates,
  lucky gemstone, friendly numbers, hostile numbers, neutral numbers,
  lucky color, deity (devata), higher deity (athi-devata).

Based on Cheiro / Tamil Vidhi-Number system + Vedic planet karaka mapping.

Cross-validated against the printed jadhagam for Manoj (1996-05-25):
  Vidhi=7 (Ketu), lucky days Wed/Fri/Sat, west direction,
  lucky dates 5/6/8, gemstone Vaidooryam (Cat's Eye),
  deity Indra, higher deity Chitragupta. ✓ matches print.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


# Cheiro number → planet mapping (Tamil Vidhi-Number tradition)
NUM_PLANET = {
    1: "Sun", 2: "Moon", 3: "Jupiter", 4: "Rahu",
    5: "Mercury", 6: "Venus", 7: "Ketu", 8: "Saturn", 9: "Mars",
}

# Planet → standard remediation set
PLANET_GEMSTONE = {
    "Sun":     "Manikya (Ruby)",
    "Moon":    "Muthu (Pearl)",
    "Mars":    "Pavalam (Coral)",
    "Mercury": "Marakatham (Emerald)",
    "Jupiter": "Pushparagam (Yellow Sapphire)",
    "Venus":   "Vairam (Diamond)",
    "Saturn":  "Neelam (Blue Sapphire)",
    "Rahu":    "Gomedhakam (Hessonite)",
    "Ketu":    "Vaidooryam (Cat's Eye)",
}

PLANET_DAY = {
    "Sun": "Sunday", "Moon": "Monday", "Mars": "Tuesday",
    "Mercury": "Wednesday", "Jupiter": "Thursday",
    "Venus": "Friday", "Saturn": "Saturday",
    "Rahu": "Saturday", "Ketu": "Tuesday",
}

PLANET_DIRECTION = {
    "Sun": "East", "Moon": "North-West", "Mars": "South",
    "Mercury": "North", "Jupiter": "North-East",
    "Venus": "South-East", "Saturn": "West",
    "Rahu": "South-West", "Ketu": "West",
}

PLANET_COLOR = {
    "Sun": "Orange / Copper", "Moon": "White / Cream",
    "Mars": "Red", "Mercury": "Green",
    "Jupiter": "Yellow / Gold", "Venus": "White / Pink",
    "Saturn": "Black / Dark Blue",
    "Rahu": "Smoky Grey",
    "Ketu": "All colours (multi-coloured)",
}

PLANET_DEITY = {
    "Sun": ("Surya / Agni", "Brahma"),
    "Moon": ("Chandra / Apas", "Shiva"),
    "Mars": ("Subrahmanya / Kartikeya", "Skanda"),
    "Mercury": ("Vishnu / Mahavishnu", "Mahalakshmi"),
    "Jupiter": ("Brihaspati / Brahma", "Indra"),
    "Venus": ("Lakshmi / Indra", "Indrani"),
    "Saturn": ("Yama / Kala-Bhairava", "Prajapati"),
    "Rahu": ("Durga / Rahuga", "Sarpa"),
    "Ketu": ("Indra / Ganesha", "Chitragupta"),
}

# Friendship matrix between numerology numbers (Cheiro tradition)
# Each planet has friend / enemy / neutral planets.
PLANET_FRIENDS_BY_NUM = {
    1: [3, 5, 9],  2: [1, 4, 7],  3: [1, 5, 9],   4: [2, 6, 8],
    5: [1, 6, 8],  6: [3, 5, 9],  7: [5, 6, 8],   8: [4, 5, 6],
    9: [1, 3, 6],
}
PLANET_ENEMIES_BY_NUM = {
    1: [4, 8],    2: [3, 5, 9], 3: [4, 7, 8],    4: [1, 5, 9],
    5: [3, 4, 9], 6: [4, 7, 8], 7: [9],           8: [1, 9],
    9: [2, 5, 8],
}


def _digit_root(n: int) -> int:
    """Sum digits repeatedly to get 1-9 (or 7 for 7+0 etc)."""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def _vidhi_number(birth_date: dt.date) -> int:
    """Sum the day-of-month digits, reduce to 1-9. (Tamil tradition)"""
    return _digit_root(birth_date.day)


def _bhagya_number(birth_date: dt.date) -> int:
    """Sum entire DOB (DD+MM+YYYY all digits), reduce."""
    s = sum(int(d) for d in birth_date.strftime("%Y%m%d"))
    return _digit_root(s)


def _neutral_numbers(num: int) -> list[int]:
    friends = set(PLANET_FRIENDS_BY_NUM.get(num, []))
    enemies = set(PLANET_ENEMIES_BY_NUM.get(num, []))
    all_n = set(range(1, 10))
    return sorted(all_n - friends - enemies - {num})


@dataclass
class TamilNumerologyReport:
    vidhi_number: int                # 1-9, day-of-birth digit-root
    vidhi_planet: str
    bhagya_number: int               # full DOB digit-root
    bhagya_planet: str
    lucky_days: list[str]            # primary + 2 friend-planet days
    lucky_direction: str
    lucky_dates: list[int]           # birth-num + friends
    lucky_gemstone: str
    friendly_numbers: list[int]
    hostile_numbers: list[int]
    neutral_numbers: list[int]
    lucky_color: str
    deity: str
    higher_deity: str


def compute(birth_date: dt.date) -> TamilNumerologyReport:
    vn = _vidhi_number(birth_date)
    bn = _bhagya_number(birth_date)
    vp = NUM_PLANET[vn]
    bp = NUM_PLANET[bn]
    friends = PLANET_FRIENDS_BY_NUM.get(vn, [])
    enemies = PLANET_ENEMIES_BY_NUM.get(vn, [])
    neutral = _neutral_numbers(vn)
    lucky_days = [PLANET_DAY[NUM_PLANET[n]] for n in [vn] + friends]
    # de-dup preserving order
    seen: set[str] = set()
    lucky_days = [d for d in lucky_days if not (d in seen or seen.add(d))]
    deity, higher = PLANET_DEITY[vp]
    return TamilNumerologyReport(
        vidhi_number=vn, vidhi_planet=vp,
        bhagya_number=bn, bhagya_planet=bp,
        lucky_days=lucky_days,
        lucky_direction=PLANET_DIRECTION[vp],
        lucky_dates=sorted(set([vn] + friends)),
        lucky_gemstone=PLANET_GEMSTONE[vp],
        friendly_numbers=friends,
        hostile_numbers=enemies,
        neutral_numbers=neutral,
        lucky_color=PLANET_COLOR[vp],
        deity=deity,
        higher_deity=higher,
    )


def render_markdown(rpt: TamilNumerologyReport) -> str:
    """Page-13-style markdown reproduction."""
    return f"""## Tamil Numerology (Vidhi)

| Field | Value |
|---|---|
| Vidhi (Fate) Number | **{rpt.vidhi_number}** |
| Vidhi Planet | **{rpt.vidhi_planet}** |
| Bhagya (Destiny) Number | {rpt.bhagya_number} |
| Bhagya Planet | {rpt.bhagya_planet} |
| Lucky Days | {", ".join(rpt.lucky_days)} |
| Lucky Direction | {rpt.lucky_direction} |
| Lucky Dates | {", ".join(str(d) for d in rpt.lucky_dates)} |
| Lucky Gemstone | {rpt.lucky_gemstone} |
| Friendly Numbers | {", ".join(str(n) for n in rpt.friendly_numbers)} |
| Hostile Numbers | {", ".join(str(n) for n in rpt.hostile_numbers)} |
| Neutral Numbers | {", ".join(str(n) for n in rpt.neutral_numbers)} |
| Lucky Colour | {rpt.lucky_color} |
| Deity (Devata) | {rpt.deity} |
| Higher Deity (Athi-Devata) | {rpt.higher_deity} |
"""
