// ============================================================================
// Astrology & Dasha Knowledge Graph (Astro-KG) — Methods & Categories Seeder
// ============================================================================

CREATE CONSTRAINT prediction_method_name IF NOT EXISTS FOR (m:PredictionMethod) REQUIRE m.name IS UNIQUE;

MERGE (m:PredictionMethod {name: "Classical Yogas"})
SET m.type = "Yoga Engine", m.description = "Predicts life milestones via classical combinations from BPHS, Phaladeepika, and Saravali.";

MERGE (c:Category {name: "yoga"})
WITH c
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "fame"})
WITH c
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "wealth"})
WITH c
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "career"})
WITH c
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "marriage"})
WITH c
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "progeny"})
WITH c
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Gaja Kesari Yoga"})
WITH r
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Ruchaka Yoga (Pancha Mahapurusha)"})
WITH r
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Bhadra Yoga (Pancha Mahapurusha)"})
WITH r
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Hamsa Yoga (Pancha Mahapurusha)"})
WITH r
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Malavya Yoga (Pancha Mahapurusha)"})
WITH r
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Sasa Yoga (Pancha Mahapurusha)"})
WITH r
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Harsha Vipareeta Raja Yoga"})
WITH r
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Sarala Vipareeta Raja Yoga"})
WITH r
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Vimala Vipareeta Raja Yoga"})
WITH r
MATCH (m:PredictionMethod {name: "Classical Yogas"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Book-Based Rules"})
SET m.type = "Declarative Rules Engine", m.description = "Evaluates raw house and sign placement effects directly from textbook translations.";

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "wealth"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "health"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "career"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "marriage"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "travel"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "siblings"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "children"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "father"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "mother"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "property"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "education"})
WITH c
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Planet in House Placements"})
WITH r
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Planet in Sign Placements"})
WITH r
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Lagna Lord Placements"})
WITH r
MATCH (m:PredictionMethod {name: "Book-Based Rules"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
SET m.type = "Semantic Extraction Engine", m.description = "Surfaces verse-precise predictions using over 14,795 AI-structured extractions.";

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "wealth"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "health"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "career"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "marriage"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "travel"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "siblings"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "children"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "father"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "mother"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "property"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "education"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "spirituality"})
WITH c
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Verse-Precise Placement Rules"})
WITH r
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Deep Scriptural Citations"})
WITH r
MATCH (m:PredictionMethod {name: "Deep AI-Extracted Rules"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Lal Kitab System"})
SET m.type = "Alternative Urdu/Punjabi Engine", m.description = "Computes Pakka Ghar aspects, sleeping planets, and suggests specific karmic remedies.";

MERGE (c:Category {name: "remedies"})
WITH c
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "health"})
WITH c
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "wealth"})
WITH c
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "property"})
WITH c
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "siblings"})
WITH c
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "progeny"})
WITH c
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "father"})
WITH c
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "mother"})
WITH c
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Pakka Ghar Rules"})
WITH r
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Lal Kitab Aspects"})
WITH r
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Closed/Asleep House Rules"})
WITH r
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "7 Karmic Debts (Rins)"})
WITH r
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Lal Kitab Upayas (Remedies)"})
WITH r
MATCH (m:PredictionMethod {name: "Lal Kitab System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "KP Stellar System"})
SET m.type = "Stellar Astrology Engine", m.description = "Calculates event significators based on Cuspal Sublord and Star Lord relationships.";

MERGE (c:Category {name: "career"})
WITH c
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "marriage"})
WITH c
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "health"})
WITH c
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "wealth"})
WITH c
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "travel"})
WITH c
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "children"})
WITH c
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "education"})
WITH c
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Cuspal Sublord Significators"})
WITH r
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Star Lord Activations"})
WITH r
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "1-12 Cuspal Placements"})
WITH r
MATCH (m:PredictionMethod {name: "KP Stellar System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Tajik Solar Return"})
SET m.type = "Annual Horoscopy Engine", m.description = "Annual predictions based on Solar Return charts, Tajik aspects, and Muntha progressions.";

MERGE (c:Category {name: "career"})
WITH c
MATCH (m:PredictionMethod {name: "Tajik Solar Return"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "wealth"})
WITH c
MATCH (m:PredictionMethod {name: "Tajik Solar Return"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "health"})
WITH c
MATCH (m:PredictionMethod {name: "Tajik Solar Return"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "travel"})
WITH c
MATCH (m:PredictionMethod {name: "Tajik Solar Return"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Tajik Solar Return"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Muntha Placement Rule"})
WITH r
MATCH (m:PredictionMethod {name: "Tajik Solar Return"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Tajik Yogas (16 classical yogas)"})
WITH r
MATCH (m:PredictionMethod {name: "Tajik Solar Return"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Year Lord Strength (Pancha Vargiya Bala)"})
WITH r
MATCH (m:PredictionMethod {name: "Tajik Solar Return"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Prashna Horary"})
SET m.type = "Question-Based Engine", m.description = "Predicts YES/NO/MAYBE outcomes for specific questions based on the moment of the query.";

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Prashna Horary"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "marriage"})
WITH c
MATCH (m:PredictionMethod {name: "Prashna Horary"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "career"})
WITH c
MATCH (m:PredictionMethod {name: "Prashna Horary"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "wealth"})
WITH c
MATCH (m:PredictionMethod {name: "Prashna Horary"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "health"})
WITH c
MATCH (m:PredictionMethod {name: "Prashna Horary"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "travel"})
WITH c
MATCH (m:PredictionMethod {name: "Prashna Horary"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Momentary Lagna Sign"})
WITH r
MATCH (m:PredictionMethod {name: "Prashna Horary"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Query Time Planetary Aspects"})
WITH r
MATCH (m:PredictionMethod {name: "Prashna Horary"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Query Lord Strength"})
WITH r
MATCH (m:PredictionMethod {name: "Prashna Horary"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Bhrigu Samhita Rules"})
SET m.type = "Nadi/Placements Engine", m.description = "Applies Bhrigu Samhita rules using planetary degrees and house progressions.";

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Bhrigu Samhita Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "career"})
WITH c
MATCH (m:PredictionMethod {name: "Bhrigu Samhita Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "wealth"})
WITH c
MATCH (m:PredictionMethod {name: "Bhrigu Samhita Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "marriage"})
WITH c
MATCH (m:PredictionMethod {name: "Bhrigu Samhita Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "children"})
WITH c
MATCH (m:PredictionMethod {name: "Bhrigu Samhita Rules"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Bhrigu House Progression Rules"})
WITH r
MATCH (m:PredictionMethod {name: "Bhrigu Samhita Rules"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Natal Planetary Degrees"})
WITH r
MATCH (m:PredictionMethod {name: "Bhrigu Samhita Rules"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Nadi Jyotish"})
SET m.type = "Trinal Aspect Engine", m.description = "Trinal transit and aspect analysis following Nadi principles (Chandra Kala Nadi, etc.).";

MERGE (c:Category {name: "spirituality"})
WITH c
MATCH (m:PredictionMethod {name: "Nadi Jyotish"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "career"})
WITH c
MATCH (m:PredictionMethod {name: "Nadi Jyotish"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "marriage"})
WITH c
MATCH (m:PredictionMethod {name: "Nadi Jyotish"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Nadi Jyotish"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Trinal Planetary Conjunctions (1-5-9)"})
WITH r
MATCH (m:PredictionMethod {name: "Nadi Jyotish"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Soul Mission (Atmakaraka) Direction"})
WITH r
MATCH (m:PredictionMethod {name: "Nadi Jyotish"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Numerology & Tamil Numerology"})
SET m.type = "Vibrational/Numerology Engine", m.description = "Vedic numerology analyzing birth dates, name spelling vibrations, and friendly numbers.";

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Numerology & Tamil Numerology"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "compatibility"})
WITH c
MATCH (m:PredictionMethod {name: "Numerology & Tamil Numerology"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "remedies"})
WITH c
MATCH (m:PredictionMethod {name: "Numerology & Tamil Numerology"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Janma/Vidhi (Birth/Destiny) Numbers"})
WITH r
MATCH (m:PredictionMethod {name: "Numerology & Tamil Numerology"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Name Number vibrations"})
WITH r
MATCH (m:PredictionMethod {name: "Numerology & Tamil Numerology"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Friendly/Hostile number pairs"})
WITH r
MATCH (m:PredictionMethod {name: "Numerology & Tamil Numerology"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Gemstone & Direction remedies"})
WITH r
MATCH (m:PredictionMethod {name: "Numerology & Tamil Numerology"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Western Tropical System"})
SET m.type = "Aspects & Placements Engine", m.description = "Tropical zodiac placements and aspects to provide personality and behavioral readings.";

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Western Tropical System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "personality"})
WITH c
MATCH (m:PredictionMethod {name: "Western Tropical System"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Tropical House Placements"})
WITH r
MATCH (m:PredictionMethod {name: "Western Tropical System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Western Aspects (Trine, Square, Opposition, Sextile, Conjunction)"})
WITH r
MATCH (m:PredictionMethod {name: "Western Tropical System"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Alternate Cultural Systems"})
SET m.type = "Calendar/Zodiac Engine", m.description = "Integrates BaZi (Four Pillars) clashes and Mayan Tzolk'in calendar calculations.";

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Alternate Cultural Systems"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "personality"})
WITH c
MATCH (m:PredictionMethod {name: "Alternate Cultural Systems"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Chinese Stem & Branch Clashes"})
WITH r
MATCH (m:PredictionMethod {name: "Alternate Cultural Systems"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Chinese Zodiac Animal Sign"})
WITH r
MATCH (m:PredictionMethod {name: "Alternate Cultural Systems"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Mayan Tzolk'in Day Sign"})
WITH r
MATCH (m:PredictionMethod {name: "Alternate Cultural Systems"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
SET m.type = "Data-Driven Calibration Engine", m.description = "Fuses classical rules, transit triggers, and dasha periods with empirical likelihood ratios.";

MERGE (c:Category {name: "general"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "wealth"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "health"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "career"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "marriage"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "travel"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "siblings"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "children"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "father"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "mother"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "property"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (c:Category {name: "education"})
WITH c
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:PREDICTS]->(c);

MERGE (r:Rule {name: "Calibrated Likelihood Ratios (LRs)"})
WITH r
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Learned Transit OR-Conjunctions"})
WITH r
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "V2 Probabilistic Meta-Reasoning"})
WITH r
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:USES_RULE]->(r);

MERGE (r:Rule {name: "Maraka Dasha Rule"})
WITH r
MATCH (m:PredictionMethod {name: "Ensemble & Transit Calibration"})
MERGE (m)-[:USES_RULE]->(r);

