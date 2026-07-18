// ============================================================================
// Astrology & Dasha Knowledge Graph (Astro-KG) — Query & Inference Library
// ============================================================================

// ============================================================================
// SECTION 1: Rule Evaluation & Graph Inference
// Run these commands in the Neo4j Browser to dynamically analyze charts,
// evaluate classical rules, and draw link edges to Rule nodes.
// ============================================================================

// 1. Evaluate Gaja Kesari Yoga (Jupiter in 1, 4, 7, 10 from Moon)
MATCH (p:Person)-[:HAS_PLACEMENT]->(jup:Placement {planet: "Jupiter"})-[:IN_HOUSE]->(hj:House)
MATCH (p)-[:HAS_PLACEMENT]->(moon:Placement {planet: "Moon"})-[:IN_HOUSE]->(hm:House)
WITH p, jup, moon, (hj.number - hm.number + 12) % 12 + 1 AS rel_house
WHERE rel_house IN [1, 4, 7, 10]
MATCH (rule:Rule {name: "Gaja Kesari Yoga"})
MERGE (p)-[:FORMED_YOGA {details: "Jupiter occupies house " + rel_house + " from Moon"}]->(rule);

// 2. Evaluate Harsha Vipareeta Raja Yoga (6th Lord in 6, 8, or 12)
MATCH (p:Person)-[:HAS_PLACEMENT]->(l6:Placement)-[:LORD_OF]->(h6:House {number: 6})
MATCH (l6)-[:IN_HOUSE]->(hTarget:House)
WHERE hTarget.number IN [6, 8, 12]
MATCH (rule:Rule {name: "Harsha Vipareeta Raja Yoga"})
MERGE (p)-[:FORMED_YOGA {details: "6th Lord " + l6.planet + " occupies house " + hTarget.number}]->(rule);

// 3. Evaluate Sarala Vipareeta Raja Yoga (8th Lord in 6, 8, or 12)
MATCH (p:Person)-[:HAS_PLACEMENT]->(l8:Placement)-[:LORD_OF]->(h8:House {number: 8})
MATCH (l8)-[:IN_HOUSE]->(hTarget:House)
WHERE hTarget.number IN [6, 8, 12]
MATCH (rule:Rule {name: "Sarala Vipareeta Raja Yoga"})
MERGE (p)-[:FORMED_YOGA {details: "8th Lord " + l8.planet + " occupies house " + hTarget.number}]->(rule);

// 4. Evaluate Vimala Vipareeta Raja Yoga (12th Lord in 6, 8, or 12)
MATCH (p:Person)-[:HAS_PLACEMENT]->(l12:Placement)-[:LORD_OF]->(h12:House {number: 12})
MATCH (l12)-[:IN_HOUSE]->(hTarget:House)
WHERE hTarget.number IN [6, 8, 12]
MATCH (rule:Rule {name: "Vimala Vipareeta Raja Yoga"})
MERGE (p)-[:FORMED_YOGA {details: "12th Lord " + l12.planet + " occupies house " + hTarget.number}]->(rule);

// 5. Evaluate Pancha Mahapurusha Yogas (Planet in own/exalted sign in kendra houses)
// Mars (Ruchaka)
MATCH (p:Person)-[:HAS_PLACEMENT]->(pl:Placement {planet: "Mars"})-[:IN_HOUSE]->(h:House)
MATCH (pl)-[:IN_RASI]->(r:Rasi)
WHERE h.number IN [1, 4, 7, 10] AND (r.name IN ["Aries", "Scorpio", "Capricorn"])
MATCH (rule:Rule {name: "Ruchaka Yoga (Pancha Mahapurusha)"})
MERGE (p)-[:FORMED_YOGA {details: "Mars in own/exalted sign " + r.name + " in house " + h.number}]->(rule);

// Mercury (Bhadra)
MATCH (p:Person)-[:HAS_PLACEMENT]->(pl:Placement {planet: "Mercury"})-[:IN_HOUSE]->(h:House)
MATCH (pl)-[:IN_RASI]->(r:Rasi)
WHERE h.number IN [1, 4, 7, 10] AND (r.name IN ["Gemini", "Virgo"])
MATCH (rule:Rule {name: "Bhadra Yoga (Pancha Mahapurusha)"})
MERGE (p)-[:FORMED_YOGA {details: "Mercury in own/exalted sign " + r.name + " in house " + h.number}]->(rule);

// Jupiter (Hamsa)
MATCH (p:Person)-[:HAS_PLACEMENT]->(pl:Placement {planet: "Jupiter"})-[:IN_HOUSE]->(h:House)
MATCH (pl)-[:IN_RASI]->(r:Rasi)
WHERE h.number IN [1, 4, 7, 10] AND (r.name IN ["Sagittarius", "Pisces", "Cancer"])
MATCH (rule:Rule {name: "Hamsa Yoga (Pancha Mahapurusha)"})
MERGE (p)-[:FORMED_YOGA {details: "Jupiter in own/exalted sign " + r.name + " in house " + h.number}]->(rule);

// Venus (Malavya)
MATCH (p:Person)-[:HAS_PLACEMENT]->(pl:Placement {planet: "Venus"})-[:IN_HOUSE]->(h:House)
MATCH (pl)-[:IN_RASI]->(r:Rasi)
WHERE h.number IN [1, 4, 7, 10] AND (r.name IN ["Taurus", "Libra", "Pisces"])
MATCH (rule:Rule {name: "Malavya Yoga (Pancha Mahapurusha)"})
MERGE (p)-[:FORMED_YOGA {details: "Venus in own/exalted sign " + r.name + " in house " + h.number}]->(rule);

// Saturn (Sasa)
MATCH (p:Person)-[:HAS_PLACEMENT]->(pl:Placement {planet: "Saturn"})-[:IN_HOUSE]->(h:House)
MATCH (pl)-[:IN_RASI]->(r:Rasi)
WHERE h.number IN [1, 4, 7, 10] AND (r.name IN ["Capricorn", "Aquarius", "Libra"])
MATCH (rule:Rule {name: "Sasa Yoga (Pancha Mahapurusha)"})
MERGE (p)-[:FORMED_YOGA {details: "Saturn in own/exalted sign " + r.name + " in house " + h.number}]->(rule);

// 6. Evaluate Maraka Dashas active during events
MATCH (p:Person)-[:EXPERIENCED]->(e:Event)
MATCH (e)-[:DURING_MD|DURING_AD]->(planet:Planet)
MATCH (p)-[:HAS_PLACEMENT]->(pl:Placement)-[:OF_PLANET]->(planet)
MATCH (pl)-[:LORD_OF]->(h:House)
WHERE h.number IN [2, 7]
MATCH (rule:Rule {name: "Maraka Dasha Rule"})
MERGE (e)-[:TRIGGERS_RULE {details: "Dasha lord " + planet.name + " is the lord of house " + h.number}]->(rule);


// ============================================================================
// SECTION 2: Graph Analysis & Research Queries
// Use these queries to study the results and find correlations.
// ============================================================================

// Query A: Show all formed Yogas across all loaded charts
MATCH (p:Person)-[rel:FORMED_YOGA]->(r:Rule)
RETURN p.name AS Subject, r.name AS YogaName, rel.details AS FormulaProof, r.summary AS Summary
ORDER BY YogaName, Subject;


// Query B: Get a complete chart breakdown for a Person (including aspects, conjunctions, and lordships)
MATCH (p:Person {name: "Steve Jobs"})-[:HAS_PLACEMENT]->(pl:Placement)
MATCH (pl)-[:OF_PLANET]->(planet:Planet)
MATCH (pl)-[:IN_HOUSE]->(h:House)
MATCH (pl)-[:IN_RASI]->(rasi:Rasi)
MATCH (pl)-[:IN_NAKSHATRA]->(n:Nakshatra)
OPTIONAL MATCH (pl)-[:LORD_OF]->(lordOfHouse:House)
OPTIONAL MATCH (pl)-[c:CONJUNCT]->(conjPl:Placement)
OPTIONAL MATCH (pl)-[a:ASPECTS]->(aspectPl:Placement)
RETURN planet.name AS Planet,
       h.number AS House,
       rasi.name AS Sign,
       n.name AS Nakshatra,
       collect(DISTINCT lordOfHouse.number) AS LordOfHouses,
       collect(DISTINCT conjPl.planet) AS ConjunctWith,
       collect(DISTINCT aspectPl.planet) AS AspectingPlanets;


// Query C: Analyze Maraka Dasha Rule performance vs Death Events
// Tells you which subjects died during a Maraka-triggered Dasha and the details
MATCH (p:Person)-[:EXPERIENCED]->(e:Event {type: "DEATH"})
MATCH (e)-[rel:TRIGGERS_RULE]->(rule:Rule {name: "Maraka Dasha Rule"})
RETURN p.name AS Subject, e.description AS EventDescription, e.year AS DeathYear, rel.details AS MarakaProof;


// Query D: Find all planets aspecting a person's 10th house (Career House)
MATCH (p:Person {name: "Albert Einstein"})-[:HAS_PLACEMENT]->(pl:Placement)
MATCH (pl)-[:ASPECTS_HOUSE]->(h:House {number: 10})
RETURN pl.planet AS AspectingPlanet, pl.deg AS Degrees, pl.house AS OccupyingHouse;
