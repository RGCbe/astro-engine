from __future__ import annotations

# English signs & nakshatras (as used in engine/chart.py)
SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")

NAKSHATRAS = ("Ashvini", "Bharani", "Krittika", "Rohini", "Mrigashirsha",
              "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
              "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
              "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
              "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
              "Purva Bhadrapada", "Uttara Bhadrapada", "Revati")

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Tamil signs (as used in engine/yogas.py and engine/shadbala.py)
SIGNS_TAMIL = [
    "Mesham", "Rishabam", "Mithunam", "Kadagam", "Simmam", "Kanni",
    "Thulaam", "Viruchigam", "Dhanusu", "Makaram", "Kumbam", "Meenam"
]

SIGN_LORDS_TAMIL = {
    "Mesham":    "Mars",
    "Rishabam":  "Venus",
    "Mithunam":  "Mercury",
    "Kadagam":   "Moon",
    "Simmam":    "Sun",
    "Kanni":     "Mercury",
    "Thulaam":   "Venus",
    "Viruchigam":"Mars",
    "Dhanusu":   "Jupiter",
    "Makaram":   "Saturn",
    "Kumbam":    "Saturn",
    "Meenam":    "Jupiter",
}

EXALTATION_TAMIL = {
    "Sun":     "Mesham",        # 10° Aries
    "Moon":    "Rishabam",      # 3° Taurus
    "Mars":    "Makaram",       # 28° Capricorn
    "Mercury": "Kanni",         # 15° Virgo
    "Jupiter": "Kadagam",       # 5° Cancer
    "Venus":   "Meenam",        # 27° Pisces
    "Saturn":  "Thulaam",       # 20° Libra
}

DEBILITATION_TAMIL = {
    "Sun":     "Thulaam",
    "Moon":    "Viruchigam",
    "Mars":    "Kadagam",
    "Mercury": "Meenam",
    "Jupiter": "Makaram",
    "Venus":   "Kanni",
    "Saturn":  "Mesham",
}

OWN_SIGNS_TAMIL = {
    "Sun":     ["Simmam"],
    "Moon":    ["Kadagam"],
    "Mars":    ["Mesham", "Viruchigam"],
    "Mercury": ["Mithunam", "Kanni"],
    "Jupiter": ["Dhanusu", "Meenam"],
    "Venus":   ["Rishabam", "Thulaam"],
    "Saturn":  ["Makaram", "Kumbam"],
}
