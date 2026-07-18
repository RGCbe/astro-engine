"""
load_methods_to_kg.py — Integrates all 13 prediction methods in Atro Vedic Engine
with their respective categories and rules in the Neo4j Knowledge Graph.
If Neo4j is offline, it gracefully writes Cypher seed scripts and a JSON representation.
"""
import os
import sys
import json
from pathlib import Path

# Add parent directory to sys.path to find connection.py
KNOWLEDGE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(KNOWLEDGE_DIR))

try:
    from connection import get_driver
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False

METHODS_DATA = [
    {
        "name": "Classical Yogas",
        "type": "Yoga Engine",
        "categories": ["yoga", "general", "fame", "wealth", "career", "marriage", "progeny"],
        "rules": ["Gaja Kesari Yoga", "Ruchaka Yoga (Pancha Mahapurusha)", "Bhadra Yoga (Pancha Mahapurusha)", 
                  "Hamsa Yoga (Pancha Mahapurusha)", "Malavya Yoga (Pancha Mahapurusha)", "Sasa Yoga (Pancha Mahapurusha)",
                  "Harsha Vipareeta Raja Yoga", "Sarala Vipareeta Raja Yoga", "Vimala Vipareeta Raja Yoga"],
        "description": "Predicts life milestones via classical combinations from BPHS, Phaladeepika, and Saravali."
    },
    {
        "name": "Book-Based Rules",
        "type": "Declarative Rules Engine",
        "categories": ["general", "wealth", "health", "career", "marriage", "travel", "siblings", "children", "father", "mother", "property", "education"],
        "rules": ["Planet in House Placements", "Planet in Sign Placements", "Lagna Lord Placements"],
        "description": "Evaluates raw house and sign placement effects directly from textbook translations."
    },
    {
        "name": "Deep AI-Extracted Rules",
        "type": "Semantic Extraction Engine",
        "categories": ["general", "wealth", "health", "career", "marriage", "travel", "siblings", "children", "father", "mother", "property", "education", "spirituality"],
        "rules": ["Verse-Precise Placement Rules", "Deep Scriptural Citations"],
        "description": "Surfaces verse-precise predictions using over 14,795 AI-structured extractions."
    },
    {
        "name": "Lal Kitab System",
        "type": "Alternative Urdu/Punjabi Engine",
        "categories": ["remedies", "health", "wealth", "property", "siblings", "progeny", "father", "mother"],
        "rules": ["Pakka Ghar Rules", "Lal Kitab Aspects", "Closed/Asleep House Rules", "7 Karmic Debts (Rins)", "Lal Kitab Upayas (Remedies)"],
        "description": "Computes Pakka Ghar aspects, sleeping planets, and suggests specific karmic remedies."
    },
    {
        "name": "KP Stellar System",
        "type": "Stellar Astrology Engine",
        "categories": ["career", "marriage", "health", "wealth", "travel", "children", "education"],
        "rules": ["Cuspal Sublord Significators", "Star Lord Activations", "1-12 Cuspal Placements"],
        "description": "Calculates event significators based on Cuspal Sublord and Star Lord relationships."
    },
    {
        "name": "Tajik Solar Return",
        "type": "Annual Horoscopy Engine",
        "categories": ["career", "wealth", "health", "travel", "general"],
        "rules": ["Muntha Placement Rule", "Tajik Yogas (16 classical yogas)", "Year Lord Strength (Pancha Vargiya Bala)"],
        "description": "Annual predictions based on Solar Return charts, Tajik aspects, and Muntha progressions."
    },
    {
        "name": "Prashna Horary",
        "type": "Question-Based Engine",
        "categories": ["general", "marriage", "career", "wealth", "health", "travel"],
        "rules": ["Momentary Lagna Sign", "Query Time Planetary Aspects", "Query Lord Strength"],
        "description": "Predicts YES/NO/MAYBE outcomes for specific questions based on the moment of the query."
    },
    {
        "name": "Bhrigu Samhita Rules",
        "type": "Nadi/Placements Engine",
        "categories": ["general", "career", "wealth", "marriage", "children"],
        "rules": ["Bhrigu House Progression Rules", "Natal Planetary Degrees"],
        "description": "Applies Bhrigu Samhita rules using planetary degrees and house progressions."
    },
    {
        "name": "Nadi Jyotish",
        "type": "Trinal Aspect Engine",
        "categories": ["spirituality", "career", "marriage", "general"],
        "rules": ["Trinal Planetary Conjunctions (1-5-9)", "Soul Mission (Atmakaraka) Direction"],
        "description": "Trinal transit and aspect analysis following Nadi principles (Chandra Kala Nadi, etc.)."
    },
    {
        "name": "Numerology & Tamil Numerology",
        "type": "Vibrational/Numerology Engine",
        "categories": ["general", "compatibility", "remedies"],
        "rules": ["Janma/Vidhi (Birth/Destiny) Numbers", "Name Number vibrations", "Friendly/Hostile number pairs", "Gemstone & Direction remedies"],
        "description": "Vedic numerology analyzing birth dates, name spelling vibrations, and friendly numbers."
    },
    {
        "name": "Western Tropical System",
        "type": "Aspects & Placements Engine",
        "categories": ["general", "personality"],
        "rules": ["Tropical House Placements", "Western Aspects (Trine, Square, Opposition, Sextile, Conjunction)"],
        "description": "Tropical zodiac placements and aspects to provide personality and behavioral readings."
    },
    {
        "name": "Alternate Cultural Systems",
        "type": "Calendar/Zodiac Engine",
        "categories": ["general", "personality"],
        "rules": ["Chinese Stem & Branch Clashes", "Chinese Zodiac Animal Sign", "Mayan Tzolk'in Day Sign"],
        "description": "Integrates BaZi (Four Pillars) clashes and Mayan Tzolk'in calendar calculations."
    },
    {
        "name": "Ensemble & Transit Calibration",
        "type": "Data-Driven Calibration Engine",
        "categories": ["general", "wealth", "health", "career", "marriage", "travel", "siblings", "children", "father", "mother", "property", "education"],
        "rules": ["Calibrated Likelihood Ratios (LRs)", "Learned Transit OR-Conjunctions", "V2 Probabilistic Meta-Reasoning", "Maraka Dasha Rule"],
        "description": "Fuses classical rules, transit triggers, and dasha periods with empirical likelihood ratios."
    }
]

def load_methods():
    # 1. Output files first (always generated for local caching and manual loading)
    data_dir = KNOWLEDGE_DIR.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    json_path = data_dir / "engine_kg.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"methods": METHODS_DATA}, f, indent=2)
    print(f"Generated local JSON KG cache at: {json_path}")

    cypher_path = KNOWLEDGE_DIR / "seed_methods.cypher"
    with open(cypher_path, "w", encoding="utf-8") as f:
        f.write("// ============================================================================\n")
        f.write("// Astrology & Dasha Knowledge Graph (Astro-KG) — Methods & Categories Seeder\n")
        f.write("// ============================================================================\n\n")
        f.write("CREATE CONSTRAINT prediction_method_name IF NOT EXISTS FOR (m:PredictionMethod) REQUIRE m.name IS UNIQUE;\n\n")
        
        for m in METHODS_DATA:
            f.write(f"MERGE (m:PredictionMethod {{name: \"{m['name']}\"}})\n")
            f.write(f"SET m.type = \"{m['type']}\", m.description = \"{m['description']}\";\n\n")
            
            for cat in m["categories"]:
                f.write(f"MERGE (c:Category {{name: \"{cat}\"}})\n")
                f.write(f"WITH c\n")
                f.write(f"MATCH (m:PredictionMethod {{name: \"{m['name']}\"}})\n")
                f.write(f"MERGE (m)-[:PREDICTS]->(c);\n\n")
                
            for rule in m["rules"]:
                f.write(f"MERGE (r:Rule {{name: \"{rule}\"}})\n")
                f.write(f"WITH r\n")
                f.write(f"MATCH (m:PredictionMethod {{name: \"{m['name']}\"}})\n")
                f.write(f"MERGE (m)-[:USES_RULE]->(r);\n\n")
                
    print(f"Generated Cypher script at: {cypher_path}")

    # 2. Try loading into active Neo4j graph db
    if not HAS_NEO4J:
        print("Neo4j python driver is not installed. Skipping Neo4j batch seed.")
        return
        
    try:
        driver = get_driver()
        with driver.session() as session:
            print("Applying schema constraints for methods...")
            session.run("CREATE CONSTRAINT prediction_method_name IF NOT EXISTS FOR (m:PredictionMethod) REQUIRE m.name IS UNIQUE")
            
            print("Loading prediction methods and linking categories/rules...")
            for m in METHODS_DATA:
                # Merge PredictionMethod
                session.run("""
                    MERGE (m:PredictionMethod {name: $name})
                    SET m.type = $type, m.description = $desc
                """, name=m["name"], type=m["type"], desc=m["description"])
                
                # Link Categories
                for cat in m["categories"]:
                    session.run("""
                        MATCH (m:PredictionMethod {name: $mName})
                        MERGE (c:Category {name: $catName})
                        MERGE (m)-[:PREDICTS]->(c)
                    """, mName=m["name"], catName=cat)
                    
                # Link Rules
                for rule in m["rules"]:
                    session.run("""
                        MATCH (m:PredictionMethod {name: $mName})
                        MERGE (r:Rule {name: $rName})
                        MERGE (m)-[:USES_RULE]->(r)
                    """, mName=m["name"], rName=rule)
                    
        print("[SUCCESS] Loaded all prediction methods and relationships into Neo4j.")
    except Exception as e:
        print(f"\n[WARNING] Could not connect to Neo4j instance to seed (Offline). Details: {e}")
        print("You can manually seed this data later using the generated Cypher script.")

if __name__ == "__main__":
    load_methods()
