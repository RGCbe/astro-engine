"""Scripture Rules Knowledge Graph Loader (Astro-KG).
Loads 13,950+ classical rules from gemma_extractions/_MASTER_dedup.json into Neo4j.
"""
import os
import sys
import json
from pathlib import Path

# Add knowledge directory to sys.path to resolve sibling connection.py
knowledge_dir = Path(__file__).resolve().parent
if str(knowledge_dir) not in sys.path:
    sys.path.insert(0, str(knowledge_dir))

from connection import get_driver


def load_scripture_rules(reset=False):
    # Path to master rules file (check locally and relative to opt/astro)
    master_path = Path("/opt/astro/gemma_extractions/_MASTER_dedup.json")
    if not master_path.exists():
        master_path = Path(__file__).resolve().parent.parent / "gemma_extractions" / "_MASTER_dedup.json"
    
    if not master_path.exists():
        print(f"Error: Could not find master rules file at {master_path}")
        sys.exit(1)

    print(f"Reading rules from {master_path}...")
    with open(master_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    rules = data.get("rules", [])
    print(f"Found {len(rules)} deduplicated scripture rules.")

    driver = get_driver()
    with driver.session() as session:
        if reset:
            print("Wiping ScriptureRule, Book, and Category nodes...")
            session.run("MATCH (r:ScriptureRule) DETACH DELETE r")
            session.run("MATCH (b:Book) DETACH DELETE b")
            session.run("MATCH (c:Category) DETACH DELETE c")

        # 1. Create Constraints & Indexes
        print("Applying schema constraints...")
        session.run("CREATE CONSTRAINT scripture_rule_id IF NOT EXISTS FOR (r:ScriptureRule) REQUIRE r.id IS UNIQUE")
        session.run("CREATE CONSTRAINT book_name         IF NOT EXISTS FOR (b:Book)          REQUIRE b.name IS UNIQUE")
        session.run("CREATE CONSTRAINT cat_name          IF NOT EXISTS FOR (c:Category)      REQUIRE c.name IS UNIQUE")

        # 2. Batch upload rules
        batch = []
        total_loaded = 0
        print("Loading scripture rules into Neo4j in batches of 1000...")
        
        for idx, r in enumerate(rules):
            # Clean up involves types
            involves_planets = [p.strip().capitalize() for p in r.get("involves_planets", []) if p]
            involves_houses = [int(h) for h in r.get("involves_houses", []) if h]
            
            # Map sign names (ensure capitalized, handle ints or string digits)
            SIGN_NAMES = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
                          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
            involves_signs = []
            for s in r.get("involves_signs", []):
                if isinstance(s, int):
                    if 0 <= s < 12:
                        involves_signs.append(SIGN_NAMES[s])
                elif isinstance(s, str) and s:
                    if s.isdigit():
                        idx = int(s)
                        if 0 <= idx < 12:
                            involves_signs.append(SIGN_NAMES[idx])
                    else:
                        involves_signs.append(s.strip().capitalize())

            batch.append({
                "id": idx,
                "text": r.get("text", ""),
                "sanskrit": r.get("sanskrit_iast", ""),
                "books": r.get("books", []),
                "categories": r.get("categories", []),
                "planets": involves_planets,
                "houses": involves_houses,
                "signs": involves_signs
            })

            if len(batch) >= 1000:
                write_batch(session, batch)
                total_loaded += len(batch)
                print(f"Loaded {total_loaded}/{len(rules)} rules...")
                batch = []

        if batch:
            write_batch(session, batch)
            total_loaded += len(batch)
            print(f"Loaded {total_loaded}/{len(rules)} rules...")

    print("Scripture rules loaded successfully!")


def write_batch(session, batch):
    session.run("""
        UNWIND $rows AS r
        MERGE (rule:ScriptureRule {id: r.id})
        SET rule.text = r.text, rule.sanskrit = r.sanskrit
        
        // Connect to Books
        FOREACH (bName in r.books |
            MERGE (b:Book {name: bName})
            MERGE (rule)-[:ATTESTED_IN]->(b)
        )
        
        // Connect to Categories
        FOREACH (cName in r.categories |
            MERGE (c:Category {name: cName})
            MERGE (rule)-[:IN_CATEGORY]->(c)
        )
        
        // Connect to Planets
        FOREACH (pName in r.planets |
            MERGE (p:Planet {name: pName})
            MERGE (rule)-[:INVOLVES_PLANET]->(p)
        )
        
        // Connect to Houses
        FOREACH (hNum in r.houses |
            MERGE (h:House {number: toInteger(hNum)})
            MERGE (rule)-[:INVOLVES_HOUSE]->(h)
        )
        
        // Connect to Signs
        FOREACH (sName in r.signs |
            MERGE (s:Rasi {name: sName})
            MERGE (rule)-[:INVOLVES_SIGN]->(s)
        )
    """, rows=batch)


if __name__ == "__main__":
    reset_db = "--reset" in sys.argv
    load_scripture_rules(reset=reset_db)
