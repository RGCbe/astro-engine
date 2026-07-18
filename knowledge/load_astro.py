"""Load astrology charts, aspects, lordships, conjunctions, and events into Neo4j (idempotent, all MERGE).

Usage:
    python load_astro.py            # create schema constraints + load data
    python load_astro.py --reset    # wipe graph first, then load
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add standard engine paths to sys.path so we can import engine
for path_str in ["/opt/astro/full", "/opt/atro/runtime", ".", str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parent.parent)]:
    p = Path(path_str).resolve()
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from engine.chart import compute_chart
    from engine.known_charts import KNOWN_CHARTS
except ImportError:
    # Fallback/mock definitions for code syntax safety if run outside opt/astro/full
    compute_chart = None
    KNOWN_CHARTS = []

from connection import get_driver

# Names of signs and lords
SIGN_NAMES = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
              "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
SIGN_LORDS = ("Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
              "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")

# Manoj birth data (as a fallback or standard chart)
MANOJ_BIRTH = {
    'date': '1996-05-25', 'time': '20:25', 'tz': 5.5,
    'place': 'Coimbatore', 'lat': 11.01, 'lon': 76.57,
}


def parse_args():
    parser = argparse.ArgumentParser(description="Astro-KG Loader")
    parser.add_argument("--reset", action="store_true", help="Reset database before loading")
    return parser.parse_args()


def load_schema(session):
    print("Applying schema constraints...")
    constraints = [
        "CREATE CONSTRAINT person_name     IF NOT EXISTS FOR (p:Person)    REQUIRE p.name IS UNIQUE",
        "CREATE CONSTRAINT placement_id    IF NOT EXISTS FOR (pl:Placement) REQUIRE pl.id IS UNIQUE",
        "CREATE CONSTRAINT planet_name     IF NOT EXISTS FOR (pl:Planet)   REQUIRE pl.name IS UNIQUE",
        "CREATE CONSTRAINT rasi_name       IF NOT EXISTS FOR (r:Rasi)      REQUIRE r.name IS UNIQUE",
        "CREATE CONSTRAINT nakshatra_name  IF NOT EXISTS FOR (n:Nakshatra) REQUIRE n.name IS UNIQUE",
        "CREATE CONSTRAINT house_num       IF NOT EXISTS FOR (h:House)     REQUIRE h.number IS UNIQUE",
        "CREATE CONSTRAINT rule_name       IF NOT EXISTS FOR (r:Rule)      REQUIRE r.name IS UNIQUE"
    ]
    for c in constraints:
        session.run(c)


def seed_static_metadata(session):
    print("Seeding static astrological concepts...")

    # Planets
    session.run("UNWIND $rows AS name MERGE (:Planet {name: name})",
                rows=["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"])

    # Rasis
    rasis = [
        {"name": "Aries", "idx": 0, "lord": "Mars"},
        {"name": "Taurus", "idx": 1, "lord": "Venus"},
        {"name": "Gemini", "idx": 2, "lord": "Mercury"},
        {"name": "Cancer", "idx": 3, "lord": "Moon"},
        {"name": "Leo", "idx": 4, "lord": "Sun"},
        {"name": "Virgo", "idx": 5, "lord": "Mercury"},
        {"name": "Libra", "idx": 6, "lord": "Venus"},
        {"name": "Scorpio", "idx": 7, "lord": "Mars"},
        {"name": "Sagittarius", "idx": 8, "lord": "Jupiter"},
        {"name": "Capricorn", "idx": 9, "lord": "Saturn"},
        {"name": "Aquarius", "idx": 10, "lord": "Saturn"},
        {"name": "Pisces", "idx": 11, "lord": "Jupiter"}
    ]
    session.run("""
        UNWIND $rows AS r
        MERGE (rasi:Rasi {name: r.name})
        SET rasi.index = r.idx, rasi.lord = r.lord
    """, rows=rasis)

    # Houses
    session.run("UNWIND range(1, 12) AS hNum MERGE (:House {number: hNum})")

    # Nakshatras
    nakshatras = [
        {"name": "Ashwini", "lord": "Ketu"}, {"name": "Bharani", "lord": "Venus"}, {"name": "Krittika", "lord": "Sun"},
        {"name": "Rohini", "lord": "Moon"}, {"name": "Mrigashira", "lord": "Mars"}, {"name": "Ardra", "lord": "Rahu"},
        {"name": "Punarvasu", "lord": "Jupiter"}, {"name": "Pushya", "lord": "Saturn"}, {"name": "Ashlesha", "lord": "Mercury"},
        {"name": "Magha", "lord": "Ketu"}, {"name": "Purva Phalguni", "lord": "Venus"}, {"name": "Uttara Phalguni", "lord": "Sun"},
        {"name": "Hasta", "lord": "Moon"}, {"name": "Chitra", "lord": "Mars"}, {"name": "Swati", "lord": "Rahu"},
        {"name": "Vishakha", "lord": "Jupiter"}, {"name": "Anuradha", "lord": "Saturn"}, {"name": "Jyeshtha", "lord": "Mercury"},
        {"name": "Mula", "lord": "Ketu"}, {"name": "Purva Ashadha", "lord": "Venus"}, {"name": "Uttara Ashadha", "lord": "Sun"},
        {"name": "Shravana", "lord": "Moon"}, {"name": "Dhanishta", "lord": "Mars"}, {"name": "Shatabhisha", "lord": "Rahu"},
        {"name": "Purva Bhadrapada", "lord": "Jupiter"}, {"name": "Uttara Bhadrapada", "lord": "Saturn"}, {"name": "Revati", "lord": "Mercury"}
    ]
    session.run("""
        UNWIND $rows AS n
        MERGE (nak:Nakshatra {name: n.name})
        SET nak.lord = n.lord
    """, rows=nakshatras)

    # Seed Classical Rules & Yogas
    rules = [
        {"name": "Gaja Kesari Yoga", "type": "Yoga", "source": "BPHS Ch. 36", "formula": "Jupiter in kendra (1, 4, 7, 10) from Moon", "summary": "Brings fame, intelligence, wealth, and respected status."},
        {"name": "Harsha Vipareeta Raja Yoga", "type": "Yoga", "source": "Phaladeepika Ch. 6", "formula": "6th Lord is situated in the 6th, 8th, or 12th house", "summary": "Victory over enemies, financial gains, health, and luxury arising from challenges."},
        {"name": "Sarala Vipareeta Raja Yoga", "type": "Yoga", "source": "Phaladeepika Ch. 6", "formula": "8th Lord is situated in the 6th, 8th, or 12th house", "summary": "Long life, success, prosperity, and fearlessness. Wins over adverse situations."},
        {"name": "Vimala Vipareeta Raja Yoga", "type": "Yoga", "source": "Phaladeepika Ch. 6", "formula": "12th Lord is situated in the 6th, 8th, or 12th house", "summary": "Independent, content, virtuous, savings-friendly, and overcomes losses."},
        {"name": "Ruchaka Yoga (Pancha Mahapurusha)", "type": "Yoga", "source": "BPHS Ch. 8", "formula": "Mars is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", "summary": "Valor, strength, fame, leadership, and bold action."},
        {"name": "Bhadra Yoga (Pancha Mahapurusha)", "type": "Yoga", "source": "BPHS Ch. 8", "formula": "Mercury is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", "summary": "Sharp intellect, eloquence, learning, success in communication and business."},
        {"name": "Hamsa Yoga (Pancha Mahapurusha)", "type": "Yoga", "source": "BPHS Ch. 8", "formula": "Jupiter is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", "summary": "Wisdom, spiritual nature, righteousness, good fortune, and respect."},
        {"name": "Malavya Yoga (Pancha Mahapurusha)", "type": "Yoga", "source": "BPHS Ch. 8", "formula": "Venus is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", "summary": "Artistic talent, beauty, grace, luxury, marital happiness, and popularity."},
        {"name": "Sasa Yoga (Pancha Mahapurusha)", "type": "Yoga", "source": "BPHS Ch. 8", "formula": "Saturn is in its own sign or exalted, and in kendra (1,4,7,10) from Lagna", "summary": "Authority, political power, command over masses, endurance, and longevity."},
        {"name": "Maraka Dasha Rule", "type": "DashaRule", "source": "BPHS Ch. 44", "formula": "MD or AD lord owns the 2nd or 7th house", "summary": "Dasha periods that carry maraka (death/transformation/illness) potential."}
    ]
    session.run("""
        UNWIND $rows AS r
        MERGE (rule:Rule {name: r.name})
        SET rule.type = r.type, rule.source = r.source, rule.formula = r.formula, rule.summary = r.summary
    """, rows=rules)


def load_person_chart(session, name, birthdata, events):
    print(f"Loading chart and calculations for {name}...")
    
    # Calculate chart using engine
    if compute_chart is None:
        print(f"Error: Astrology engine not found in path. Cannot compute chart for {name}.")
        return

    bd = birthdata
    chart = compute_chart(name=name, date=bd['date'], time=bd['time'],
                          tz_hours=bd['tz'], lat=bd['lat'], lon=bd['lon'])

    lagna_idx = int(chart.lagna_lon // 30)

    # 1. Create Person node
    session.run("""
        MERGE (p:Person {name: $name})
        SET p.birth_date = $birth_date,
            p.birth_place = $place,
            p.lat = $lat,
            p.lon = $lon,
            p.ayanamsa = $ayanamsa
    """, name=name, birth_date=bd['date'], place=bd.get('place', ''),
         lat=bd.get('lat', 0.0), lon=bd.get('lon', 0.0), ayanamsa=round(chart.ayanamsa, 4))

    # 2. Link Lagna Rasi
    lagna_name = SIGN_NAMES[lagna_idx]
    session.run("""
        MATCH (p:Person {name: $name})
        MATCH (r:Rasi {name: $lagna_name})
        MERGE (p)-[:HAS_LAGNA]->(r)
    """, name=name, lagna_name=lagna_name)

    # 3. Create Placements
    placements = []
    sign_groups = {} # rasi_idx -> list of (planet, deg)
    house_occupations = {} # house_num -> list of planet_names

    for planet, lon in chart.positions.items():
        sign_idx = int(lon // 30)
        deg = lon % 30
        house = ((sign_idx - lagna_idx) % 12) + 1
        nak = chart.nakshatras.get(planet, {})

        pl_id = f"{name}_{planet}"
        placements.append({
            "id": pl_id,
            "planet": planet,
            "lon": round(lon, 4),
            "deg": round(deg, 4),
            "pada": nak.get('pada', 1),
            "house": house,
            "rasi": SIGN_NAMES[sign_idx],
            "nak": nak.get('name', '')
        })

        # Track groups for conjunctions & aspects
        sign_groups.setdefault(sign_idx, []).append((planet, deg, pl_id))
        house_occupations.setdefault(house, []).append((planet, pl_id))

    # Batch write placements
    session.run("""
        UNWIND $rows AS pl
        MATCH (p:Person {name: $name})
        MATCH (planet:Planet {name: pl.planet})
        MATCH (rasi:Rasi {name: pl.rasi})
        MATCH (h:House {number: pl.house})
        MATCH (nak:Nakshatra {name: pl.nak})
        
        MERGE (placement:Placement {id: pl.id})
        SET placement.planet = pl.planet,
            placement.lon = pl.lon,
            placement.deg = pl.deg,
            placement.pada = pl.pada
            
        MERGE (p)-[:HAS_PLACEMENT]->(placement)
        MERGE (placement)-[:OF_PLANET]->(planet)
        MERGE (placement)-[:IN_HOUSE]->(h)
        MERGE (placement)-[:IN_RASI]->(rasi)
        MERGE (placement)-[:IN_NAKSHATRA]->(nak)
    """, name=name, rows=placements)

    # 4. Compute and Link Lordships (House Lords)
    lordships = []
    for h in range(1, 13):
        sign_idx = (lagna_idx + h - 1) % 12
        lord_planet = SIGN_LORDS[sign_idx]
        lordships.append({
            "placement_id": f"{name}_{lord_planet}",
            "house_number": h
        })

    session.run("""
        UNWIND $rows AS l
        MATCH (pl:Placement {id: l.placement_id})
        MATCH (h:House {number: l.house_number})
        MERGE (pl)-[:LORD_OF]->(h)
    """, rows=lordships)

    # 5. Compute and Link Conjunctions
    conjunctions = []
    for sign_idx, planets in sign_groups.items():
        if len(planets) > 1:
            for i in range(len(planets)):
                for j in range(i + 1, len(planets)):
                    p1, d1, id1 = planets[i]
                    p2, d2, id2 = planets[j]
                    orb = abs(d1 - d2)
                    conjunctions.append({"id1": id1, "id2": id2, "orb": round(orb, 4)})

    if conjunctions:
        session.run("""
            UNWIND $rows AS c
            MATCH (pl1:Placement {id: c.id1})
            MATCH (pl2:Placement {id: c.id2})
            MERGE (pl1)-[r1:CONJUNCT {orb: c.orb}]->(pl2)
            MERGE (pl2)-[r2:CONJUNCT {orb: c.orb}]->(pl1)
        """, rows=conjunctions)

    # 6. Compute and Link Aspects (Vedic whole-sign aspects)
    aspects = []
    for pl in placements:
        planet = pl["planet"]
        pl_id = pl["id"]
        h = pl["house"]

        # Calculate target houses aspected
        targets = [] # list of (house_num, type)
        # All planets aspect the 7th house from their position
        targets.append(((h + 6) % 12 + 1, "7th Aspect"))
        
        # Saturn aspects 3rd and 10th houses from its position
        if planet == "Saturn":
            targets.append(((h + 2) % 12 + 1, "Saturn 3rd Aspect"))
            targets.append(((h + 9) % 12 + 1, "Saturn 10th Aspect"))
        # Mars aspects 4th and 8th houses from its position
        elif planet == "Mars":
            targets.append(((h + 3) % 12 + 1, "Mars 4th Aspect"))
            targets.append(((h + 7) % 12 + 1, "Mars 8th Aspect"))
        # Jupiter aspects 5th and 9th houses from its position
        elif planet == "Jupiter":
            targets.append(((h + 4) % 12 + 1, "Jupiter 5th Aspect"))
            targets.append(((h + 8) % 12 + 1, "Jupiter 9th Aspect"))

        for target_house, aspect_type in targets:
            aspects.append({
                "source_id": pl_id,
                "target_house": target_house,
                "type": aspect_type
            })

    # Link Aspects to Houses
    session.run("""
        UNWIND $rows AS a
        MATCH (source:Placement {id: a.source_id})
        MATCH (target:House {number: a.target_house})
        MERGE (source)-[:ASPECTS_HOUSE {type: a.type}]->(target)
    """, rows=aspects)

    # Link Aspects to Planets occupying those aspected houses
    planet_aspects = []
    for a in aspects:
        target_house = a["target_house"]
        occupied_planets = house_occupations.get(target_house, [])
        for pl_name, pl_id in occupied_planets:
            planet_aspects.append({
                "source_id": a["source_id"],
                "target_id": pl_id,
                "type": a["type"]
            })

    if planet_aspects:
        session.run("""
            UNWIND $rows AS pa
            MATCH (source:Placement {id: pa.source_id})
            MATCH (target:Placement {id: pa.target_id})
            MERGE (source)-[:ASPECTS {type: pa.type}]->(target)
        """, rows=planet_aspects)

    # 7. Load Life Events
    for ev in events:
        session.run("""
            MATCH (p:Person {name: $name})
            MATCH (md:Planet {name: $md})
            MATCH (ad:Planet {name: $ad})
            
            CREATE (e:Event {
                type: $event_type,
                age: $age,
                year: $year,
                result: $result,
                description: $description
            })
            
            MERGE (p)-[:EXPERIENCED]->(e)
            MERGE (e)-[:DURING_MD]->(md)
            MERGE (e)-[:DURING_AD]->(ad)
        """, name=name, event_type=ev.event_type if hasattr(ev, 'event_type') else ev.get('event', ''),
             age=ev.age if hasattr(ev, 'age') else ev.get('age', 0),
             year=ev.year if hasattr(ev, 'year') else ev.get('year', 0),
             md=ev.md if hasattr(ev, 'md') else ev.get('md', ''),
             ad=ev.ad if hasattr(ev, 'ad') else ev.get('ad', ''),
             result=ev.result if hasattr(ev, 'result') else ev.get('result', 'UNKNOWN'),
             description=ev.description if hasattr(ev, 'description') else ev.get('description', ''))


def main():
    args = parse_args()
    driver = get_driver()

    with driver.session() as session:
        if args.reset:
            print("Wiping existing graph nodes and relationships...")
            session.run("MATCH (n) DETACH DELETE n")

        load_schema(session)
        seed_static_metadata(session)

        if compute_chart is None:
            print("\nWARNING: Astrology engine not found in python path.")
            print("To load celebrity charts, run this script inside the /opt/astro/full environment.")
            print("Loaded schema and static metadata successfully.")
            return

        # Load Manoj
        load_person_chart(session, "Manoj", MANOJ_BIRTH, [])

        # Load all celebrities from KNOWN_CHARTS
        for k in KNOWN_CHARTS:
            load_person_chart(session, k.name, k.birthdata, k.events)

    print("\nData loading completed successfully!")


if __name__ == "__main__":
    main()
