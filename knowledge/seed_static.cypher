// ============================================================================
// Astrology & Dasha Knowledge Graph (Astro-KG) — Static Seed
// Neo4j 5.x · Idempotent constraints + seeding data (including Classical Rules)
// ============================================================================

// 1. Uniqueness Constraints & Indexes
CREATE CONSTRAINT person_name     IF NOT EXISTS FOR (p:Person)    REQUIRE p.name IS UNIQUE;
CREATE CONSTRAINT placement_id    IF NOT EXISTS FOR (pl:Placement) REQUIRE pl.id IS UNIQUE;
CREATE CONSTRAINT planet_name     IF NOT EXISTS FOR (pl:Planet)   REQUIRE pl.name IS UNIQUE;
CREATE CONSTRAINT rasi_name       IF NOT EXISTS FOR (r:Rasi)      REQUIRE r.name IS UNIQUE;
CREATE CONSTRAINT nakshatra_name  IF NOT EXISTS FOR (n:Nakshatra) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT house_num       IF NOT EXISTS FOR (h:House)     REQUIRE h.number IS UNIQUE;
CREATE CONSTRAINT rule_name       IF NOT EXISTS FOR (r:Rule)      REQUIRE r.name IS UNIQUE;

// 2. Seed Planets
UNWIND ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"] AS pName
MERGE (:Planet {name: pName});

// 3. Seed Rasis (Zodiac Signs) and their planetary lords
UNWIND [
  {name: "Aries", idx: 0, lord: "Mars"},
  {name: "Taurus", idx: 1, lord: "Venus"},
  {name: "Gemini", idx: 2, lord: "Mercury"},
  {name: "Cancer", idx: 3, lord: "Moon"},
  {name: "Leo", idx: 4, lord: "Sun"},
  {name: "Virgo", idx: 5, lord: "Mercury"},
  {name: "Libra", idx: 6, lord: "Venus"},
  {name: "Scorpio", idx: 7, lord: "Mars"},
  {name: "Sagittarius", idx: 8, lord: "Jupiter"},
  {name: "Capricorn", idx: 9, lord: "Saturn"},
  {name: "Aquarius", idx: 10, lord: "Saturn"},
  {name: "Pisces", idx: 11, lord: "Jupiter"}
] AS row
MERGE (r:Rasi {name: row.name})
SET r.index = row.idx, r.lord = row.lord;

// 4. Seed Houses 1-12
UNWIND range(1, 12) AS hNum
MERGE (:House {number: hNum});

// 5. Seed Nakshatras (Lunar Mansions) and their lords
UNWIND [
  {name: "Ashwini", lord: "Ketu"}, {name: "Bharani", lord: "Venus"}, {name: "Krittika", lord: "Sun"},
  {name: "Rohini", lord: "Moon"}, {name: "Mrigashira", lord: "Mars"}, {name: "Ardra", lord: "Rahu"},
  {name: "Punarvasu", lord: "Jupiter"}, {name: "Pushya", lord: "Saturn"}, {name: "Ashlesha", lord: "Mercury"},
  {name: "Magha", lord: "Ketu"}, {name: "Purva Phalguni", lord: "Venus"}, {name: "Uttara Phalguni", lord: "Sun"},
  {name: "Hasta", lord: "Moon"}, {name: "Chitra", lord: "Mars"}, {name: "Swati", lord: "Rahu"},
  {name: "Vishakha", lord: "Jupiter"}, {name: "Anuradha", lord: "Saturn"}, {name: "Jyeshtha", lord: "Mercury"},
  {name: "Mula", lord: "Ketu"}, {name: "Purva Ashadha", lord: "Venus"}, {name: "Uttara Ashadha", lord: "Sun"},
  {name: "Shravana", lord: "Moon"}, {name: "Dhanishta", lord: "Mars"}, {name: "Shatabhisha", lord: "Rahu"},
  {name: "Purva Bhadrapada", lord: "Jupiter"}, {name: "Uttara Bhadrapada", lord: "Saturn"}, {name: "Revati", lord: "Mercury"}
] AS row
MERGE (n:Nakshatra {name: row.name})
SET n.lord = row.lord;

// 6. Seed Classical Rules & Yogas
UNWIND [
  {name: "Gaja Kesari Yoga", type: "Yoga", source: "BPHS Ch. 36", formula: "Jupiter in kendra (1, 4, 7, 10) from Moon", summary: "Brings fame, intelligence, wealth, and respected status."},
  {name: "Harsha Vipareeta Raja Yoga", type: "Yoga", source: "Phaladeepika Ch. 6", formula: "6th Lord is situated in the 6th, 8th, or 12th house", summary: "Victory over enemies, financial gains, health, and luxury arising from challenges."},
  {name: "Sarala Vipareeta Raja Yoga", type: "Yoga", source: "Phaladeepika Ch. 6", formula: "8th Lord is situated in the 6th, 8th, or 12th house", summary: "Long life, success, prosperity, and fearlessness. Wins over adverse situations."},
  {name: "Vimala Vipareeta Raja Yoga", type: "Yoga", source: "Phaladeepika Ch. 6", formula: "12th Lord is situated in the 6th, 8th, or 12th house", summary: "Independent, content, virtuous, savings-friendly, and overcomes losses."},
  {name: "Ruchaka Yoga (Pancha Mahapurusha)", type: "Yoga", source: "BPHS Ch. 8", formula: "Mars is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", summary: "Valor, strength, fame, leadership, and bold action."},
  {name: "Bhadra Yoga (Pancha Mahapurusha)", type: "Yoga", source: "BPHS Ch. 8", formula: "Mercury is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", summary: "Sharp intellect, eloquence, learning, success in communication and business."},
  {name: "Hamsa Yoga (Pancha Mahapurusha)", type: "Yoga", source: "BPHS Ch. 8", formula: "Jupiter is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", summary: "Wisdom, spiritual nature, righteousness, good fortune, and respect."},
  {name: "Malavya Yoga (Pancha Mahapurusha)", type: "Yoga", source: "BPHS Ch. 8", formula: "Venus is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", summary: "Artistic talent, beauty, grace, luxury, marital happiness, and popularity."},
  {name: "Sasa Yoga (Pancha Mahapurusha)", type: "Yoga", source: "BPHS Ch. 8", formula: "Saturn is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", summary: "Authority, political power, command over masses, endurance, and longevity."},
  {name: "Maraka Dasha Rule", type: "DashaRule", source: "BPHS Ch. 44", formula: "MD or AD lord owns the 2nd or 7th house", summary: "Dasha periods that carry maraka (death/transformation/illness) potential."}
] AS row
MERGE (rule:Rule {name: row.name})
SET rule.type = row.type, rule.source = row.source, rule.formula = row.formula, rule.summary = row.summary;
