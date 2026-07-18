"""
Transit Engine (Gochar) — Production wrapper for transits.py.

Uses the existing swisseph instance already running in main.py to avoid
path-conflict issues with the legacy EPHE_PATH in transits.py.
Returns a clean snapshot of where the slow planets are TODAY relative
to the natal chart.
"""
from __future__ import annotations

import datetime
import swisseph as swe

SLOW_PLANETS = {
    "Saturn": swe.SATURN,
    "Jupiter": swe.JUPITER,
    "Mars": swe.MARS,
    "Rahu": swe.MEAN_NODE,
}

SIGN_NAMES = [
    "Mesham", "Rishabam", "Mithunam", "Kadagam", "Simmam", "Kanni",
    "Thulaam", "Viruchigam", "Dhanusu", "Makaram", "Kumbam", "Meenam"
]

# Classical Gochar result table (simplified) — what each slow planet's transit
# through each house from natal Moon means.
# Source: BPHS Ch.26; Phaladeepika Ch.26.
GOCHAR_FROM_MOON = {
    "Saturn": {
        1: ("Sade Sati Peak", "BAD", "Health stress, mental burden, financial obstacles. Most intense phase of Sade Sati."),
        2: ("Sade Sati Setting", "MIXED", "Expenses rise, family disputes. Relief building — final phase of Sade Sati."),
        3: ("Auspicious Transit", "GOOD", "Courage, gains, victory over enemies. Good for action and enterprise."),
        4: ("Home-stress", "BAD", "Unhappiness at home, vehicle/property trouble, mother's health."),
        5: ("Children/intelligence strain", "BAD", "Troubles with children, speculation losses, mental pressure."),
        6: ("Enemy-vanquishing", "GOOD", "Excellent — overcomes all enemies, good health, financial gain."),
        7: ("Partnership friction", "BAD", "Marital strain, partnership disputes, travel fatigue."),
        8: ("Crisis / longevity challenge", "BAD", "Health crises, unexpected obstacles, financial loss. Exercise caution."),
        9: ("Fortune setback", "BAD", "Dharma weakened, father's health, financial contraction."),
        10: ("Career breakthrough", "GOOD", "Power, fame, career gains, government favor. High-achievement window."),
        11: ("Gains galore", "GOOD", "Financial gains, fulfilment of desires, social expansion."),
        12: ("Sade Sati Rising", "BAD", "Hidden expenses, sleep disruption, spiritual calling intensifies."),
    },
    "Jupiter": {
        1: ("Lagna transit", "GOOD", "Health, wisdom, new beginnings. Auspicious for all activities."),
        2: ("Wealth transit", "GOOD", "Financial gains, family harmony, eloquence."),
        3: ("3rd house", "BAD", "Bravery tested, sibling issues, minor financial loss."),
        4: ("4th house", "GOOD", "Home happiness, property gains, mother's wellbeing."),
        5: ("5th house", "GOOD", "Children prosper, intelligence heightened, speculation gains."),
        6: ("6th house", "BAD", "Enemies rise, health issues, service stress."),
        7: ("7th house", "BAD", "Marital tension, partnership conflicts, foreign travel."),
        8: ("8th house", "BAD", "Hidden obstacles, longevity question, sudden changes."),
        9: ("9th house", "GOOD", "Dharma flourishes, father's blessings, fortune rises. Peak Jupiter transit."),
        10: ("10th house", "GOOD", "Career peak, promotions, government favor."),
        11: ("11th house", "GOOD", "Maximum gains, all desires fulfilled, social recognition."),
        12: ("12th house", "MIXED", "Spiritual growth, foreign travel, meditation benefit. Worldly loss possible."),
    },
    "Mars": {
        1: ("Lagna Mars", "BAD", "Aggression, accidents, fever risk. Be cautious with fire/sharp objects."),
        2: ("2nd house Mars", "BAD", "Family quarrels, financial arguments, speech conflicts."),
        3: ("3rd house Mars", "GOOD", "Courage, energy, victory. Best Mars transit."),
        4: ("4th house Mars", "BAD", "Home disputes, property issues, mother's health."),
        5: ("5th house Mars", "BAD", "Children's health, speculation loss, emotional volatility."),
        6: ("6th house Mars", "GOOD", "Enemies conquered, recovery from illness, athletic strength."),
        7: ("7th house Mars", "BAD", "Manglik tension, partner conflicts, legal disputes."),
        8: ("8th house Mars", "BAD", "Accidents, surgery risk, secret enemies. Exercise extreme caution."),
        9: ("9th house Mars", "BAD", "Father's health, dharma conflicts, travel obstacles."),
        10: ("10th house Mars", "GOOD", "Career drive, professional victory, leadership."),
        11: ("11th house Mars", "GOOD", "Financial gains, desire fulfillment, new connections."),
        12: ("12th house Mars", "BAD", "Hidden enemies, hospital visits, financial drain."),
    },
    "Rahu": {
        1: ("Rahu on Moon", "BAD", "Mental confusion, identity crisis, foreign influences. Watch health."),
        2: ("2nd house Rahu", "MIXED", "Unconventional income, family disruption, speech oddities."),
        3: ("3rd house Rahu", "GOOD", "Unconventional courage, tech/media gains, sibling connections."),
        4: ("4th house Rahu", "BAD", "Home unrest, property disputes, maternal health."),
        5: ("5th house Rahu", "MIXED", "Speculation ups/downs, children's unusual circumstances, creativity."),
        6: ("6th house Rahu", "GOOD", "Enemies subdued through clever strategy, gains from foreign sources."),
        7: ("7th house Rahu", "MIXED", "Unconventional partnership or foreign spouse situation."),
        8: ("8th house Rahu", "BAD", "Hidden crises, occult involvements, sudden disruptions."),
        9: ("9th house Rahu", "MIXED", "Unconventional dharma, foreign guru, philosophical upheaval."),
        10: ("10th house Rahu", "GOOD", "Ambition peak, fame through unconventional means, tech/media career."),
        11: ("11th house Rahu", "GOOD", "Major gains, foreign income, social expansion. Favorable Rahu transit."),
        12: ("12th house Rahu", "BAD", "Hidden losses, foreign travels, spiritual confusion."),
    }
}


def get_transit_snapshot(
    natal_moon_sign_idx: int,    # 0-11 index
    natal_lagna_sign_idx: int,   # 0-11 index
    natal_positions: dict,       # {planet: longitude}
    jd_ut: float,                # Julian Day for today
) -> dict:
    """
    Compute today's Gochar (transit) snapshot.
    Returns impact of slow planets relative to natal Moon sign and Lagna.
    """
    snapshot = {
        "computed_at": datetime.datetime.now().strftime("%Y-%m-%d"),
        "transit_planets": [],
    }

    for planet_name, planet_id in SLOW_PLANETS.items():
        try:
            pos, _ = swe.calc_ut(jd_ut, planet_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
            transit_lon = pos[0] % 360
        except Exception:
            continue

        transit_sign_idx = int(transit_lon / 30)
        transit_sign = SIGN_NAMES[transit_sign_idx]

        # House from natal Moon
        house_from_moon = ((transit_sign_idx - natal_moon_sign_idx) % 12) + 1
        # House from natal Lagna
        house_from_lagna = ((transit_sign_idx - natal_lagna_sign_idx) % 12) + 1

        # Get Gochar result
        gochar = GOCHAR_FROM_MOON.get(planet_name, {}).get(house_from_moon, ("Transit", "MIXED", "No detailed rule available."))
        gochar_title, gochar_valence, gochar_meaning = gochar

        # Check for tight orb to natal planet positions
        tight_aspects = []
        for nat_planet, nat_lon in natal_positions.items():
            diff = abs((transit_lon - nat_lon + 540) % 360 - 180)
            if diff <= 2.0:  # within 2° = tight conjunction
                tight_aspects.append({"planet": nat_planet, "orb": round(diff, 2), "type": "conjunction"})

        snapshot["transit_planets"].append({
            "planet": planet_name,
            "transit_sign": transit_sign,
            "transit_longitude": round(transit_lon, 2),
            "house_from_moon": house_from_moon,
            "house_from_lagna": house_from_lagna,
            "gochar_title": gochar_title,
            "gochar_valence": gochar_valence,
            "gochar_meaning": gochar_meaning,
            "tight_natal_aspects": tight_aspects,
        })

    return snapshot
