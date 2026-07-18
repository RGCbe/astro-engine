"""
Narrative Configuration & Static Mappings for the Life Intelligence System.
Extracts hardcoded profiles, quotes, tags, and psychological texts out of the main orchestrator.
"""

def get_season_for_age(age: float) -> tuple[int, str, str]:
    if age < 6: return 1, "Birth to Age 5", "The Foundation"
    elif age < 13: return 2, "Age 6-12", "Finding Yourself"
    elif age < 19: return 3, "Age 13-18", "Identity"
    elif age < 26: return 4, "Age 19-25", "Entering the World"
    elif age < 33: return 5, "Age 26-32", "Current Chapter"
    elif age < 45: return 6, "Age 33-44", "Building the Empire"
    elif age < 60: return 7, "Age 45-59", "Mastery"
    else: return 8, "Age 60+", "Wisdom and Legacy"

def get_age_tier(age: float) -> str:
    if age < 13: return "CHILDHOOD"
    elif age < 20: return "ADOLESCENCE"
    elif age < 35: return "EARLY_ADULT"
    elif age < 60: return "MID_ADULT"
    else: return "ELDER"

def evaluate_dimensions(event: str, age: float) -> dict:
    tier = get_age_tier(age)
    scores = {"career": 5, "money": 5, "relationships": 5, "health": 6, "confidence": 5, "opportunity": 5, "pressure": 5}
    
    # Adjust baselines by age
    if tier == "CHILDHOOD":
        scores.update({"career": 1, "money": 2, "opportunity": 4, "relationships": 8})
    elif tier == "ADOLESCENCE":
        scores.update({"career": 3, "money": 3, "opportunity": 7, "pressure": 7, "relationships": 7})
        
    if event in ["CAREER_PEAK", "RECOGNITION", "FOUND_BUSINESS", "POLITICAL_OFFICE"]:
        if tier in ["CHILDHOOD", "ADOLESCENCE"]:
            scores.update({"career": 5, "opportunity": 8, "confidence": 8, "money": 4})
        else:
            scores.update({"career": 9, "money": 8, "confidence": 9, "opportunity": 9, "pressure": 7})
    elif event in ["EDUCATION_PEAK"]:
        scores.update({"career": 7, "opportunity": 9, "confidence": 8, "pressure": 6})
    elif event in ["FINANCIAL_GAIN"]:
        if tier in ["CHILDHOOD", "ADOLESCENCE"]:
            scores.update({"money": 7, "relationships": 7}) # Family gain
        else:
            scores.update({"money": 9, "opportunity": 8, "career": 7})
    elif event in ["MARRIAGE", "CHILDREN_BORN"]:
        if tier not in ["CHILDHOOD"]:
            scores.update({"relationships": 9, "confidence": 8, "pressure": 7, "money": 5})
    elif event in ["FOREIGN_TRAVEL", "SPIRITUAL_TURN"]:
        scores.update({"opportunity": 8, "confidence": 7, "relationships": 5, "pressure": 4})
    elif event in ["HEALTH_CRISIS", "FAMILY_LOSS", "DEATH_RISK", "ACCIDENT_RISK"]:
        scores.update({"health": 3, "relationships": 8, "confidence": 4, "opportunity": 3, "pressure": 9})
        
    return scores

def generate_chapter_quote(event: str, age: float) -> str:
    tier = get_age_tier(age)
    if event in ["CAREER_PEAK", "RECOGNITION", "FOUND_BUSINESS", "POLITICAL_OFFICE"]:
        if tier in ["CHILDHOOD", "ADOLESCENCE"]: return "Early recognition shapes the self-image long before the career begins."
        return "This is the chapter where your decisions begin shaping the rest of your life more than your circumstances."
    elif event == "EDUCATION_PEAK":
        return "Knowledge accumulated now becomes the structural steel of your future."
    elif event in ["MARRIAGE", "CHILDREN_BORN"]:
        if tier == "CHILDHOOD": return "Deep familial bonds form the emotional blueprint for life."
        return "The expansion of the heart requires the reorganization of one's entire life."
    elif event == "FOREIGN_TRAVEL":
        return "Physical distance from the familiar catalyzes internal paradigm shifts."
    elif event == "FINANCIAL_GAIN":
        return "Resources expand, granting the most valuable asset: optionality."
    elif event == "SPIRITUAL_TURN":
        return "When the external world loses its gravity, the internal world reveals its vastness."
    elif event in ["HEALTH_CRISIS", "FAMILY_LOSS", "DEATH_RISK", "ACCIDENT_RISK"]:
        return "A period of profound internal reconstruction, where removing the obsolete makes way for the necessary."
    else:
        return "The foundation is quietly laid in the years when nothing seems to be happening."

def generate_intelligence_tags(event: str, age: float) -> dict:
    tags = {"status": "Consolidation Phase", "risk_level": "Medium", "momentum": "Steady", "stability": "High", "next_turning_point": "24 Months"}
    
    if event in ["CAREER_PEAK", "RECOGNITION", "FOUND_BUSINESS", "FINANCIAL_GAIN", "POLITICAL_OFFICE"]:
        tags.update({"status": "Expansion", "momentum": "Increasing", "next_turning_point": "12 Months"})
    elif event in ["EDUCATION_PEAK", "FOREIGN_TRAVEL"]:
        tags.update({"status": "Exploration", "momentum": "Accelerating", "stability": "Medium"})
    elif event in ["MARRIAGE", "CHILDREN_BORN"]:
        tags.update({"status": "Structural Shift", "momentum": "Steady", "stability": "Re-forming"})
    elif event in ["SPIRITUAL_TURN"]:
        tags.update({"status": "Internalization", "momentum": "Decelerating", "stability": "High"})
    elif event in ["HEALTH_CRISIS", "FAMILY_LOSS", "DEATH_RISK", "ACCIDENT_RISK"]:
        tags.update({"status": "Recovery Phase", "risk_level": "Critical", "stability": "Low", "next_turning_point": "6 Months"})
        
    return tags

def evaluate_opportunities_pressures(event: str, age: float) -> dict:
    if event in ["CAREER_PEAK", "FINANCIAL_GAIN", "FOUND_BUSINESS", "POLITICAL_OFFICE"]:
        return {
            "opportunities": ["Enhanced confidence potential", "Stronger earning ability", "Favorable for networking/authority"],
            "pressures": ["Risk of overworking", "Potential neglect of health", "Increased ego friction"]
        }
    elif event in ["EDUCATION_PEAK"]:
        return {
            "opportunities": ["Skill acquisition", "Mentorship", "Future-proofing"],
            "pressures": ["Intellectual fatigue", "High expectations"]
        }
    elif event in ["MARRIAGE", "CHILDREN_BORN"]:
        return {
            "opportunities": ["Deep emotional anchoring", "Building legacy", "Shared resources"],
            "pressures": ["Loss of individual autonomy", "Increased financial/time demands"]
        }
    elif event in ["FOREIGN_TRAVEL", "SPIRITUAL_TURN"]:
        return {
            "opportunities": ["Perspective shifts", "Cultural/spiritual enrichment", "Breaking toxic routines"],
            "pressures": ["Isolation from roots", "Existential confusion"]
        }
    elif event in ["HEALTH_CRISIS", "FAMILY_LOSS", "DEATH_RISK", "ACCIDENT_RISK"]:
        return {
            "opportunities": ["Capacity for deepened empathy", "Forced rest leading to recalibration", "Discovering true support systems"],
            "pressures": ["Physical exhaustion risk", "Financial strain", "Emotional overwhelm"]
        }
    else:
        return {
            "opportunities": ["Steady skill development", "Stable routines"],
            "pressures": ["Feeling of stagnation", "Lack of clear direction"]
        }

def evaluate_psychology(event: str, age: float) -> dict:
    if event in ["CAREER_PEAK", "FOUND_BUSINESS", "RECOGNITION", "POLITICAL_OFFICE"]:
        return {
            "what_you_saw": "A period characterized by likely career expansion and increased responsibilities.",
            "what_was_really_happening": "An internal rebuilding phase where self-confidence was being restored to handle a larger role.",
            "missed_opportunity": "This pattern often brings chances to delegate. Hoarding control may have bottlenecked potential growth.",
            "blind_spot": "A strong tendency to try and control everything.",
            "growth_area": "Trusting others and building scalable systems."
        }
    elif event in ["FINANCIAL_GAIN"]:
        return {
            "what_you_saw": "An increase in material resources or familial support.",
            "what_was_really_happening": "A shift in your relationship with security and abundance.",
            "missed_opportunity": "Strategic reinvestment of resources rather than mere accumulation.",
            "blind_spot": "Equating financial security with emotional safety.",
            "growth_area": "Using resources as leverage for time and freedom."
        }
    elif event in ["MARRIAGE", "CHILDREN_BORN"]:
        return {
            "what_you_saw": "A major expansion of your immediate family circle and obligations.",
            "what_was_really_happening": "A forced dismantling of purely selfish drives to accommodate others.",
            "missed_opportunity": "Maintaining individual identity while merging lives.",
            "blind_spot": "Over-identifying with the role of provider/partner at the expense of the self.",
            "growth_area": "Balancing unconditional support with healthy boundaries."
        }
    elif event in ["EDUCATION_PEAK"]:
        return {
            "what_you_saw": "A time of intense study, learning, or academic achievement.",
            "what_was_really_happening": "The rewiring of your cognitive frameworks.",
            "missed_opportunity": "Applying knowledge practically instead of just collecting it theoretically.",
            "blind_spot": "Intellectual arrogance.",
            "growth_area": "Translating theory into real-world value."
        }
    elif event in ["FOREIGN_TRAVEL", "SPIRITUAL_TURN"]:
        return {
            "what_you_saw": "A departure from normal environments or normal ways of thinking.",
            "what_was_really_happening": "A necessary detachment to gain objective clarity on your life.",
            "missed_opportunity": "Failing to integrate the lessons learned upon returning to normal life.",
            "blind_spot": "Using travel or spirituality as an escape from reality.",
            "growth_area": "Grounded integration of expansive experiences."
        }
    elif event in ["HEALTH_CRISIS", "FAMILY_LOSS", "DEATH_RISK", "ACCIDENT_RISK"]:
        return {
            "what_you_saw": "A phase typically marked by external restriction, loss, or physical limitation.",
            "what_was_really_happening": "The removal of external foundations, forcing the discovery of deep internal resilience.",
            "missed_opportunity": "Opportunities to ask for help were likely present. Pride or fear may have caused unnecessary isolation.",
            "blind_spot": "The belief that you must carry heavy burdens alone.",
            "growth_area": "Learning vulnerability and the necessity of surrender."
        }
    else:
        return {
            "what_you_saw": "A transitional phase primarily focused on daily maintenance.",
            "what_was_really_happening": "A subtle recalibration of core values beneath the surface.",
            "missed_opportunity": "Networking or expansive opportunities may have been overlooked due to a strict focus on routine.",
            "blind_spot": "Potential complacency.",
            "growth_area": "Proactive long-term planning."
        }

def generate_cause_effect(event: str, age: float, next_event: str = None) -> dict:
    tier = get_age_tier(age)
    
    built = "A foundation of quiet resilience and steady routine."
    if event in ["CAREER_PEAK", "FOUND_BUSINESS", "RECOGNITION", "POLITICAL_OFFICE"]:
        built = "A robust network and a high-leverage professional reputation." if tier != "CHILDHOOD" else "Early confidence and recognition of innate talents."
    elif event in ["EDUCATION_PEAK"]:
        built = "A deep reservoir of specialized knowledge and cognitive discipline."
    elif event in ["FINANCIAL_GAIN"]:
        built = "Increased material security and resource flexibility."
    elif event in ["MARRIAGE", "CHILDREN_BORN"]:
        built = "A complex emotional support system and long-term familial bonds." if tier != "CHILDHOOD" else "Deep emotional attachments and familial reliance."
    elif event in ["FOREIGN_TRAVEL", "SPIRITUAL_TURN"]:
        built = "A broadened worldview and detachment from trivial concerns."
    elif event in ["HEALTH_CRISIS", "FAMILY_LOSS", "DEATH_RISK", "ACCIDENT_RISK"]:
        built = "Raw psychological endurance and a realignment of true priorities."
        
    created = "A subtle shift in how you process the world around you."
    if event in ["CAREER_PEAK", "FOUND_BUSINESS", "RECOGNITION", "POLITICAL_OFFICE"]:
        created = "The ability to dictate terms rather than accept them." if tier != "CHILDHOOD" else "A strong sense of self-worth."
    elif event in ["EDUCATION_PEAK"]:
        created = "New ways to solve complex problems independently."
    elif event in ["FINANCIAL_GAIN"]:
        created = "The option to take calculated risks without existential fear."
    elif event in ["MARRIAGE", "CHILDREN_BORN"]:
        created = "A shift from purely individual goals to collective legacy building."
    elif event in ["FOREIGN_TRAVEL", "SPIRITUAL_TURN"]:
        created = "An intolerance for superficiality and stagnant environments."
    elif event in ["HEALTH_CRISIS", "FAMILY_LOSS", "DEATH_RISK", "ACCIDENT_RISK"]:
        created = "A drastic reduction in tolerance for what is unimportant."

    therefore = "You became prepared for the next phase of development."
    if event in ["CAREER_PEAK", "FOUND_BUSINESS", "RECOGNITION", "POLITICAL_OFFICE"]:
        therefore = "You began attracting opportunities instead of chasing them."
    elif event in ["EDUCATION_PEAK"]:
        therefore = "Your value in the marketplace of ideas significantly increased."
    elif event in ["FINANCIAL_GAIN"]:
        therefore = "You gained the leverage to optimize your time."
    elif event in ["MARRIAGE", "CHILDREN_BORN"]:
        therefore = "Your decision-making timeline expanded to include future generations."
    elif event in ["FOREIGN_TRAVEL", "SPIRITUAL_TURN"]:
        therefore = "You began seeking purpose over mere progression."
    elif event in ["HEALTH_CRISIS", "FAMILY_LOSS", "DEATH_RISK", "ACCIDENT_RISK"]:
        therefore = "You emerged with clarified boundaries and hardened resolve."

    return {
        "what_this_built": built,
        "this_created": created,
        "therefore": therefore,
        "next_chapter": next_event.replace("_", " ").title() if next_event else "Unknown Horizon"
    }
