"""
Load the Question Catalog into the Neo4j Knowledge Graph.
Creates LifeQuestion nodes linked to Domain, LifeStage and Volume nodes.
"""
import os, sys, json
from pathlib import Path

knowledge_dir = Path(__file__).resolve().parent.parent / "knowledge"
sys.path.insert(0, str(knowledge_dir))
from connection import get_driver

CATALOG_PATH = Path(__file__).resolve().parent.parent / "gemma_extractions" / "question_catalog.json"

def load_questions():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    questions = data["questions"]
    total = data["total"]
    print(f"Loading {total} questions into Neo4j KG...")

    driver = get_driver()
    with driver.session() as session:
        # Create constraints
        session.run("CREATE CONSTRAINT life_question_id IF NOT EXISTS FOR (q:LifeQuestion) REQUIRE q.id IS UNIQUE")
        session.run("CREATE CONSTRAINT domain_name IF NOT EXISTS FOR (d:LifeDomain) REQUIRE d.name IS UNIQUE")
        session.run("CREATE CONSTRAINT lifestage_name IF NOT EXISTS FOR (s:LifeStage) REQUIRE s.name IS UNIQUE")

        # Batch insert
        batch = []
        for q in questions:
            batch.append({
                "id": q["id"],
                "question": q["question"],
                "domain": q["domain"] or "General",
                "life_stage": q["life_stage"] or "Whole Life",
                "placement": q["placement"] or "Timeline",
                "volume": q["volume"],
            })
            if len(batch) >= 50:
                _write_batch(session, batch)
                batch = []
        if batch:
            _write_batch(session, batch)

    print(f"[DONE] {total} LifeQuestion nodes loaded into Neo4j.")

def _write_batch(session, batch):
    session.run("""
        UNWIND $rows AS q
        MERGE (lq:LifeQuestion {id: q.id})
        SET lq.question = q.question,
            lq.placement = q.placement,
            lq.volume = q.volume

        MERGE (dom:LifeDomain {name: q.domain})
        MERGE (lq)-[:IN_DOMAIN]->(dom)

        MERGE (stg:LifeStage {name: q.life_stage})
        MERGE (lq)-[:IN_LIFE_STAGE]->(stg)
    """, rows=batch)

if __name__ == "__main__":
    load_questions()
