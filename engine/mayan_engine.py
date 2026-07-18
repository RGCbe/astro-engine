"""
Mayan Astrology Engine — GAC Standard.
Handles:
    - Julian Day to Tzolk'in 260-day calendar cycle calculations
    - Dynamic Day Glyph (20 Signs) and Galactic Tone (13 Numbers) resolver
    - Mayan spiritual and elemental personality descriptions
"""
import datetime as dt
import math

# 20 Tzolk'in Day Signs (Glyphs) in order starting with Imix
DAY_SIGNS = [
    {"name": "Imix", "translation": "Crocodile / Red Dragon", "element": "Earth", "direction": "East",
     "description": "Nurturing, creative, primal energy. Represents the dynamic starting force and initiating projects."},
    {"name": "Ik", "translation": "Wind", "element": "Air", "direction": "North",
     "description": "Communicative, intellectual, agile. Represents breath, spirit, versatility, and the power of speech."},
    {"name": "Akbal", "translation": "Night / House", "element": "Water", "direction": "West",
     "description": "Introspective, intuitive, dreaming. Represents the unconscious mind, sanctuary, and hidden mysteries."},
    {"name": "Kan", "translation": "Seed / Lizard", "element": "Fire", "direction": "South",
     "description": "Growth, potential, fertility. Represents creation, dynamic wealth, manifestation, and deep roots."},
    {"name": "Chicchan", "translation": "Serpent", "element": "Earth", "direction": "East",
     "description": "Vitality, instinct, kundalini energy. Represents physical power, agility, charisma, and transformation."},
    {"name": "Cimi", "translation": "Death / Transformer", "element": "Air", "direction": "North",
     "description": "Rebirth, release, ancestral guidance. Represents wisdom, detachment, transitions, and spiritual change."},
    {"name": "Manik", "translation": "Deer / Hand", "element": "Water", "direction": "West",
     "description": "Healing, service, nobility. Represents boundary-setting, artistic mastery, stability, and animal instincts."},
    {"name": "Lamat", "translation": "Star / Rabbit", "element": "Fire", "direction": "South",
     "description": "Beauty, harmony, dynamic abundance. Represents artistic elegance, clear intuition, and expanding cycles."},
    {"name": "Muluc", "translation": "Water / Jade", "element": "Earth", "direction": "East",
     "description": "Emotion, purification, flow. Represents internal memory, gratitude, dynamic adaptability, and visual arts."},
    {"name": "Oc", "translation": "Dog", "element": "Air", "direction": "North",
     "description": "Loyalty, heart, companionship. Represents emotional depth, devotion, protective leadership, and playfulness."},
    {"name": "Chuen", "translation": "Monkey", "element": "Water", "direction": "West",
     "description": "Artistry, humor, play. Represents curiosity, inventiveness, magic, showmanship, and performance."},
    {"name": "Eb", "translation": "Road / Grass", "element": "Fire", "direction": "South",
     "description": "Destiny, dynamic wisdom, receiver. Represents travel, community networks, and carrying ancestral lineage."},
    {"name": "Ben", "translation": "Reed / Skywalker", "element": "Earth", "direction": "East",
     "description": "Pioneering, authority, connection. Represents spiritual channels, exploration, and domestic stability."},
    {"name": "Ix", "translation": "Jaguar / Wizard", "element": "Air", "direction": "North",
     "description": "Magic, integrity, nocturnal wisdom. Represents high spirituality, patience, healing, and nature connection."},
    {"name": "Men", "translation": "Eagle", "element": "Water", "direction": "West",
     "description": "Vision, perspective, mind. Represents soaring high, high intellect, planning, and global awareness."},
    {"name": "Cib", "translation": "Vulture / Warrior", "element": "Fire", "direction": "South",
     "description": "Wisdom, cosmic trust, integrity. Represents quiet courage, deep karma balancing, and ancestral memory."},
    {"name": "Caban", "translation": "Earth / Earth-keeper", "element": "Earth", "direction": "East",
     "description": "Rhythm, synchronicity, evolution. Represents earth connection, active movement, and scientific curiosity."},
    {"name": "Etznab", "translation": "Flint / Mirror", "element": "Air", "direction": "North",
     "description": "Truth, clarity, reflection. Represents cutting away illusion, deep self-discovery, and visual precision."},
    {"name": "Cauac", "translation": "Storm", "element": "Water", "direction": "West",
     "description": "Cleansing, dynamic energy, renewal. Represents transformation, emotional release, and rapid evolution."},
    {"name": "Ahau", "translation": "Sun / Lord", "element": "Fire", "direction": "South",
     "description": "Enlightenment, master, universal love. Represents spiritual leadership, nobility, beauty, and absolute truth."}
]

# 13 Galactic Tones (Numbers) in order
GALACTIC_TONES = [
    {"tone": 1, "name": "Magnetic", "keyword": "Unity", "action": "Attract", "description": "Initiating, starting, unifying energy. The center of starting point."},
    {"tone": 2, "name": "Lunar", "keyword": "Duality", "action": "Stabilize", "description": "Polarity, choosing path, balancing dynamic opposites."},
    {"tone": 3, "name": "Electric", "keyword": "Creativity", "action": "Flow", "description": "Movement, activation, creative expression, and dynamic change."},
    {"tone": 4, "name": "Self-Existing", "keyword": "Form", "action": "Define", "description": "Stability, structural order, boundary limits, and grounded focus."},
    {"tone": 5, "name": "Overtone", "keyword": "Radiance", "action": "Command", "description": "Gathering strength, leadership authority, and central power."},
    {"tone": 6, "name": "Rhythmic", "keyword": "Equality", "action": "Balance", "description": "Rhythm, flow, organic adaptation, and structural balance."},
    {"tone": 7, "name": "Resonant", "keyword": "Attunement", "action": "Inspire", "description": "Spiritual connection, channel, absolute trust, and clarity."},
    {"tone": 8, "name": "Galactic", "keyword": "Integrity", "action": "Model", "description": "Harmony, ethical boundaries, modeling truth, and reliability."},
    {"tone": 9, "name": "Solar", "keyword": "Expansion", "action": "Realize", "description": "Action orientation, dynamic growth, purpose, and visual realization."},
    {"tone": 10, "name": "Planetary", "keyword": "Manifestation", "action": "Perfect", "description": "Grounding ideas into physical form, completion, and success."},
    {"tone": 11, "name": "Spectral", "keyword": "Liberation", "action": "Release", "description": "Dispersing energy, letting go of limitations, and absolute freedom."},
    {"tone": 12, "name": "Crystal", "keyword": "Cooperation", "action": "Dedicate", "description": "Community focus, sharing, collaborative design, and structural synthesis."},
    {"tone": 13, "name": "Cosmic", "keyword": "Transcendence", "action": "Endure", "description": "Ultimate synthesis, magic, transitions, and timeless presence."}
]

def get_julian_day_int(year: int, month: int, day: int) -> int:
    """Standard Gregorian calendar to JDN (integer) conversion."""
    if month <= 2:
        year -= 1
        month += 12
    a = math.floor(year / 100)
    b = 2 - a + math.floor(a / 4)
    jdn = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524
    return int(jdn)

def compute_tzolkin(year: int, month: int, day: int) -> dict:
    """Aligns Gregorian date to the Tzolk'in 260-day cycle using GMT correlation constant 584283."""
    jdn = get_julian_day_int(year, month, day)
    
    # JDN 584283 corresponds to 4 Ahau (Ahau = index 19, Tone = 4)
    # Day Sign Index calculation
    sign_idx = (jdn - 584283 + 19) % 20
    
    # Galactic Tone calculation (1 to 13)
    tone_idx = (jdn - 584283 + 3) % 13
    
    glyph = DAY_SIGNS[sign_idx]
    tone = GALACTIC_TONES[tone_idx]
    
    return {
        "julian_day_number": jdn,
        "tzolkin_day_index": (jdn - 584283) % 260,
        "galactic_tone": tone,
        "day_glyph": glyph,
        "formatted": f"{tone['tone']} {glyph['name']} ({tone['name']} {glyph['translation']})"
    }

def compute_mayan_chart(date: str) -> dict:
    """Entry point for the GAC Mayan Astrology calculation."""
    y, m, d = (int(x) for x in date.split("-"))
    tzolkin = compute_tzolkin(y, m, d)
    
    return {
        "framework": "Mayan Tzolk'in Calendar (GMT 584283 Correlation)",
        "calculations": {
            "julian_day_number": tzolkin["julian_day_number"],
            "tzolkin_day_index": tzolkin["tzolkin_day_index"],
            "formatted": tzolkin["formatted"],
            "galactic_tone": tzolkin["galactic_tone"],
            "day_glyph": tzolkin["day_glyph"]
        }
    }
