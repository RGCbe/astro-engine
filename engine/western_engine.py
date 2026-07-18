"""
Western Astrology Engine — GAC Standard.
Handles:
    - High-precision Tropical planetary longitudes (Sun to Pluto + Nodes)
    - Essential Dignities (Domicile, Detriment, Exaltation, Fall)
    - Aspect Matrix (Conjunction, Sextile, Square, Trine, Opposition)
    - Hellenistic Annual Profections & Year Lord
    - Lot calculations (Part of Fortune & Part of Spirit)
    - Zodiacal Releasing Chapter Generator
"""
import datetime as dt
from pathlib import Path
import swisseph as swe

# Set ephemeris path
EPHE_PATH = str(Path(__file__).parent.parent / "ephe")
swe.set_ephe_path(EPHE_PATH)

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Essential Dignities Matrix (Domicile, Detriment, Exaltation, Fall)
EXALTATIONS = {
    "Sun": ("Aries", 19),
    "Moon": ("Taurus", 3),
    "Mercury": ("Virgo", 15),
    "Venus": ("Pisces", 27),
    "Mars": ("Capricorn", 28),
    "Jupiter": ("Cancer", 15),
    "Saturn": ("Libra", 21)
}

BODIES = [
    ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN), ("Uranus", swe.URANUS), ("Neptune", swe.NEPTUNE),
    ("Pluto", swe.PLUTO), ("North Node", swe.MEAN_NODE)
]

# Zodiacal Releasing standard sign periods (in years)
ZR_PERIODS = {
    "Aries": 15, "Taurus": 8, "Gemini": 20, "Cancer": 25,
    "Leo": 19, "Virgo": 20, "Libra": 8, "Scorpio": 15,
    "Sagittarius": 12, "Capricorn": 27, "Aquarius": 30, "Pisces": 12
}

def get_sign(lon: float) -> str:
    return SIGNS[int((lon % 360) // 30)]

def get_dignity(body: str, lon: float) -> str:
    sign = get_sign(lon)
    # Check Domicile & Detriment
    domicile = [k for k, v in SIGN_LORDS.items() if v == body]
    if sign in domicile:
        return "Domicile"
    
    detriments = []
    for d in domicile:
        idx = (SIGNS.index(d) + 6) % 12
        detriments.append(SIGNS[idx])
    if sign in detriments:
        return "Detriment"
    
    # Check Exaltation & Fall
    if body in EXALTATIONS:
        ex_sign, _ = EXALTATIONS[body]
        fall_idx = (SIGNS.index(ex_sign) + 6) % 12
        fall_sign = SIGNS[fall_idx]
        if sign == ex_sign:
            return "Exaltation"
        if sign == fall_sign:
            return "Fall"
            
    return "Peregrine"

def compute_aspects(positions: dict[str, float]) -> list[dict]:
    aspects = []
    bodies = list(positions.keys())
    
    # Orbs definition
    orbs = {
        0: 8.0,   # Conjunction
        60: 6.0,  # Sextile
        90: 8.0,  # Square
        120: 8.0, # Trine
        180: 8.0  # Opposition
    }
    
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            b1, b2 = bodies[i], bodies[j]
            lon1, lon2 = positions[b1], positions[b2]
            
            diff = abs(lon1 - lon2) % 360
            if diff > 180:
                diff = 360 - diff
                
            for angle, orb in orbs.items():
                if abs(diff - angle) <= orb:
                    aspects.append({
                        "body1": b1,
                        "body2": b2,
                        "type": {0: "Conjunction", 60: "Sextile", 90: "Square", 120: "Trine", 180: "Opposition"}[angle],
                        "angle": round(diff, 2),
                        "exactness": round(1 - (abs(diff - angle) / orb), 4)
                    })
    return aspects

def compute_lots(positions: dict[str, float], lagna_lon: float) -> dict[str, float]:
    """Calculate Part of Fortune and Part of Spirit.
    Formula changes based on Day vs. Night chart (Sun position relative to Horizon).
    """
    sun = positions["Sun"]
    moon = positions["Moon"]
    
    # Ascendant whole sign house determines Day/Night
    # Standard: Sun in houses 7 to 12 = Day chart. Sun in houses 1 to 6 = Night chart.
    # We can also compute based on absolute houses.
    lagna_sign_idx = int(lagna_lon // 30)
    sun_sign_idx = int(sun // 30)
    sun_house = ((sun_sign_idx - lagna_sign_idx) % 12) + 1
    
    is_day = 7 <= sun_house <= 12
    
    if is_day:
        fortune = (lagna_lon + moon - sun) % 360
        spirit = (lagna_lon + sun - moon) % 360
    else:
        fortune = (lagna_lon + sun - moon) % 360
        spirit = (lagna_lon + moon - sun) % 360
        
    return {
        "Part of Fortune": round(fortune, 4),
        "Part of Spirit": round(spirit, 4),
        "Sect": "Day" if is_day else "Night"
    }

def compute_profections(lagna_lon: float, age: int) -> dict:
    """Calculate Annual Profection Sign and Year Lord for a given age."""
    lagna_sign_idx = int(lagna_lon // 30)
    profected_idx = (lagna_sign_idx + age) % 12
    profected_sign = SIGNS[profected_idx]
    year_lord = SIGN_LORDS[profected_sign]
    
    return {
        "Age": age,
        "Profected Sign": profected_sign,
        "Lord of the Year": year_lord
    }

def compute_zodiacal_releasing(start_lon: float, birth_year: int, max_chapters: int = 5) -> list[dict]:
    """Generates Level 1 Zodiacal Releasing Chapters from a starting Lot longitude."""
    start_sign = get_sign(start_lon)
    chapters = []
    
    current_sign_idx = SIGNS.index(start_sign)
    current_year = float(birth_year)
    
    for i in range(max_chapters):
        sign = SIGNS[current_sign_idx]
        duration = ZR_PERIODS[sign]
        
        chapters.append({
            "Chapter": i + 1,
            "Sign": sign,
            "Duration (Years)": duration,
            "Start Year": round(current_year, 1),
            "End Year": round(current_year + duration, 1)
        })
        
        current_year += duration
        current_sign_idx = (current_sign_idx + 1) % 12
        
    return chapters

def compute_western_chart(date: str, time: str, tz_hours: float, lat: float, lon: float, age: int = 30) -> dict:
    """Entry point for the GAC Western Astrology calculation."""
    y, m, d = (int(x) for x in date.split("-"))
    hh, mm = (int(x) for x in time.split(":"))
    
    hour_ut = (hh + mm / 60.0) - tz_hours
    jd_ut = swe.julday(y, m, d, hour_ut)
    
    # Calculate positions under TROPICAL coordinate framework (no FLG_SIDEREAL)
    positions = {}
    for name, code in BODIES:
        pos, _ = swe.calc_ut(jd_ut, code, swe.FLG_SWIEPH)
        positions[name] = pos[0]
        
    positions["South Node"] = (positions["North Node"] + 180.0) % 360
    
    # Calculate Ascendant (AscMC)
    houses, ascmc = swe.houses_ex(jd_ut, lat, lon, b"P", swe.FLG_SWIEPH)
    lagna_lon = ascmc[0]
    
    # Detailed planetary details
    planetary_details = {}
    for body, longitude in positions.items():
        planetary_details[body] = {
            "longitude": round(longitude, 4),
            "sign": get_sign(longitude),
            "dignity": get_dignity(body, longitude)
        }
        
    # Lots
    lots = compute_lots(positions, lagna_lon)
    
    # Profections
    profections = compute_profections(lagna_lon, age)
    
    # Zodiacal Releasing
    fortune_releasing = compute_zodiacal_releasing(lots["Part of Fortune"], y)
    spirit_releasing = compute_zodiacal_releasing(lots["Part of Spirit"], y)
    
    # Whole Sign Houses Mapping
    lagna_sign_idx = int(lagna_lon // 30)
    whole_sign_houses = {}
    for h in range(12):
        house_sign = SIGNS[(lagna_sign_idx + h) % 12]
        whole_sign_houses[h + 1] = house_sign
        
    return {
        "framework": "Western Tropical",
        "calculations": {
            "julian_day": round(jd_ut, 4),
            "ascendant": {
                "longitude": round(lagna_lon, 4),
                "sign": get_sign(lagna_lon)
            },
            "houses": whole_sign_houses,
            "planets": planetary_details,
            "aspects": compute_aspects(positions),
            "lots": lots,
            "annual_profection": profections,
            "zodiacal_releasing_fortune": fortune_releasing,
            "zodiacal_releasing_spirit": spirit_releasing
        }
    }
