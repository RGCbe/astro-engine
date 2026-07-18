"""
Comparative Test Engine — Generates side-by-side predictions for every book in the corpus.
Supports 'Consensus Battle' and 'Surgical Dasha Focus'.
"""
from engine.corpus import get_corpus
import json

RASIS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

def synthesize_consensus(rules):
    """Analyzes a list of CorpusRules to determine the consensus and flag contradictions."""
    auspicious_keywords = ["wealth", "success", "fame", "happiness", "health", "gain", "auspicious", "good", "rich", "king"]
    inauspicious_keywords = ["poverty", "death", "disease", "loss", "grief", "inauspicious", "bad", "sorrow", "poor", "pain"]
    
    auspicious_count = 0
    inauspicious_count = 0
    
    for r in rules:
        text_lower = r.text.lower()
        if any(k in text_lower for k in auspicious_keywords):
            auspicious_count += 1
        if any(k in text_lower for k in inauspicious_keywords):
            inauspicious_count += 1
            
    total = auspicious_count + inauspicious_count
    consensus_score = (auspicious_count / total * 100) if total > 0 else 50
    
    status = "Mixed"
    if consensus_score > 65: status = "Auspicious Consensus"
    elif consensus_score < 35: status = "Inauspicious Consensus"
    elif total > 0: status = "Strong Contradiction"
    
    return {
        "status": status,
        "auspicious_weight": auspicious_count,
        "inauspicious_weight": inauspicious_count,
        "consensus_percent": round(consensus_score, 2),
        "total_rules_analyzed": len(rules),
        "nature": "corpus_agreement_index",
        "disclaimer": (
            "Consensus % measures agreement among indexed book passages for this placement — "
            "not probability that an event will occur."
        ),
    }

def get_aspected_houses(planet: str, current_house: int) -> list[int]:
    """Calculates Parashari Aspects (Drishti)."""
    aspects = [(current_house + 6) % 12 + 1] # 7th aspect
    if planet == "Mars":
        aspects.extend([(current_house + 3) % 12 + 1, (current_house + 7) % 12 + 1]) # 4th and 8th
    elif planet in ["Jupiter", "Rahu"]:
        aspects.extend([(current_house + 4) % 12 + 1, (current_house + 8) % 12 + 1]) # 5th and 9th
    elif planet == "Saturn":
        aspects.extend([(current_house + 2) % 12 + 1, (current_house + 9) % 12 + 1]) # 3rd and 10th
    return list(set(aspects))

def execute_corpus_battle_comparison(chart_data: dict, focus_lords: list = None):
    corpus = get_corpus()
    battle_report = {}
    lagna_sign = chart_data.get("lagnam_rasi") or chart_data.get("lagna_sign")
    house_data = chart_data.get("house_predictions", [])
    shadbala = chart_data.get("shadbala", {}).get("planets", {})
    sav_bindus = chart_data.get("ashtakavarga", {}).get("sarva_ashtakavarga", [])
    
    # 1. Evaluate Planet in House & Aspects
    for h_info in house_data:
        h_num = h_info.get("house")
        # Handle both singular 'planet' and plural 'planets' from different engine versions
        planets = h_info.get("planets", [])
        if not planets and "planet" in h_info:
            planets = [h_info["planet"]]
        
        # If focus_lords provided, we focus on those houses but include all planets there
        is_relevant_house = True
        if focus_lords:
            is_relevant_house = any(lord in planets for lord in focus_lords)
            
        if not is_relevant_house:
            continue
            
        for p in planets:
            # Strength Context
            p_rupas = shadbala.get(p, {}).get("total_rupas", 1.0)
            h_bindus = sav_bindus.get(str(h_num - 1), 28) if isinstance(sav_bindus, dict) else (sav_bindus[h_num - 1] if len(sav_bindus) >= h_num else 28)
            
            # Subject 1: Planet in House
            subject_key = f"{p} in House {h_num}"
            all_rules = corpus.get_planet_in_house(p, h_num, limit=50, lagna_sign=lagna_sign)
            if all_rules:
                consensus = synthesize_consensus(all_rules)
                if p_rupas < 1.0: consensus["status"] += " [Weak]"
                battle_report[subject_key] = {
                    "type": "Planet in House",
                    "consensus": consensus,
                    "top_rules": [{"books": r.books, "text": r.text} for r in all_rules[:3]]
                }
            
            # Subject 2: Aspect (Drishti)
            # We only analyze aspects FROM the focus lords to other houses
            if focus_lords and p not in focus_lords:
                continue
                
            aspect_targets = get_aspected_houses(p, h_num)
            for target_h in aspect_targets:
                aspect_key = f"{p} aspecting House {target_h}"
                aspect_rules = [
                    r
                    for r in corpus.get_planet_in_house(
                        "_general", target_h, limit=50, lagna_sign=lagna_sign
                    )
                    if p.lower() in r.text.lower()
                ]
                if aspect_rules:
                    battle_report[aspect_key] = {
                        "type": "Planetary Aspect",
                        "consensus": synthesize_consensus(aspect_rules),
                        "top_rules": [{"books": r.books, "text": r.text} for r in aspect_rules[:2]]
                    }

    # 2. Conjunctions (Yutis)
    for h_info in house_data:
        h_num = h_info.get("house")
        planets = h_info.get("planets", [])
        if len(planets) > 1:
            if focus_lords and not any(l in planets for l in focus_lords):
                continue
            conj_key = f"{' & '.join(planets)} in House {h_num}"
            conj_rules = corpus.get_compound_rules(planets, [h_num], limit=30)
            if conj_rules:
                battle_report[conj_key] = {
                    "type": "Conjunction",
                    "consensus": synthesize_consensus(conj_rules),
                    "top_rules": [{"books": r.books, "text": r.text} for r in conj_rules[:2]]
                }

    # 3. Yogas & Dashas
    all_other = []
    all_other.extend([(y["name"], "Yoga") for y in chart_data.get("detected_yogas", [])])
    
    dasha_schedule = chart_data.get("dasha_schedule", [])
    if dasha_schedule:
        for md in dasha_schedule:
            md_lord = md.get("lord")
            if not md_lord: continue
            all_other.append((f"Maha Dasha: {md_lord}", "Dasha Timing"))
            
            # Analyze Antardashas if available
            sub_periods = md.get("sub_periods", [])
            for ad in sub_periods:
                ad_lord = ad.get("lord")
                if ad_lord:
                    all_other.append((f"Antardasha: {md_lord}-{ad_lord}", "Antardasha Timing"))
    else:
        # Fallback to current dasha if schedule is not available
        dasha_lord = chart_data.get("current_dasha")
        if dasha_lord:
            all_other.append((f"Dasha Lord: {dasha_lord}", "Dasha Timing"))

    for subject, type_val in all_other:
        if focus_lords and not any(lord in subject for lord in focus_lords):
            continue
            
        rules = []
        if type_val == "Yoga":
            rules = corpus.get_yoga_rules(subject.split()[0], limit=20)
        elif type_val == "Dasha Timing":
            lord = subject.split(": ")[1]
            rules = corpus.get_dasha_rules(lord, limit=50)
        elif type_val == "Antardasha Timing":
            lords = subject.split(": ")[1].split("-")
            if len(lords) == 2:
                rules = corpus.get_dasha_rules(lords[0], lords[1], limit=50)
            
        if rules:
            battle_report[subject] = {
                "type": type_val,
                "consensus": synthesize_consensus(rules),
                "top_rules": [{"books": r.books, "text": r.text} for r in rules[:2]]
            }

    return battle_report
