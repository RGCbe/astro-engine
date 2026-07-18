from connection import get_driver

driver = get_driver()
with driver.session() as session:
    print("--- Database Stats ---")
    res = session.run("MATCH (n) RETURN labels(n)[0] AS Label, count(n)")
    for record in res:
        print(f"{record['Label']}: {record['count(n)']}")

    print("\n--- Loaded Persons ---")
    res = session.run("MATCH (p:Person) RETURN p.name, p.birth_date")
    for record in res:
        print(f"Person: {record['p.name']} | Birth Date: {record['p.birth_date']}")

    print("\n--- Placements for Albert Einstein ---")
    res = session.run("""
        MATCH (p:Person {name: "Albert Einstein"})-[r:HAS_PLACEMENT]->(pl:Placement)
        MATCH (pl)-[:IN_HOUSE]->(h:House)
        MATCH (pl)-[:IN_RASI]->(rasi:Rasi)
        RETURN pl.planet AS Planet, h.number AS House, rasi.name AS Rasi
        ORDER BY House
    """)
    for record in res:
        print(f"Planet: {record['Planet']} | House: {record['House']} | Rasi: {record['Rasi']}")

    print("\n--- Matching Scripture Rules ---")
    res = session.run("""
        MATCH (p:Person {name: "Albert Einstein"})-[:HAS_PLACEMENT]->(pl:Placement)
        MATCH (pl)-[:OF_PLANET]->(planet:Planet)
        MATCH (pl)-[:IN_HOUSE]->(house:House)
        MATCH (rule:ScriptureRule)
        WHERE (rule)-[:INVOLVES_PLANET]->(planet) AND (rule)-[:INVOLVES_HOUSE]->(house)
        RETURN planet.name AS Planet, house.number AS House, count(rule) AS MatchCount
    """)
    for record in res:
        print(f"Planet: {record['Planet']} | House: {record['House']} | Rules Matched: {record['MatchCount']}")
