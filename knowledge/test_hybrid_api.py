import requests
import json
from connection import get_driver

payload = {
    "name": "Albert Einstein",
    "year": 1879,
    "month": 3,
    "day": 14,
    "time": "11:30",
    "lat": 48.4,
    "lon": 10.0,
    "tz_hours": 1.0,
    "target_date": "1955-04-18"
}

url = "http://localhost:8000/api/astrology/global-hybrid"
print(f"Sending request to {url}...")
response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    res = response.json()
    print("Success!\n")
    print(json.dumps(res, indent=2))
    
    print("--- Vedic Summary ---")
    print(f"Lagnam: {res.get('vedic', {}).get('lagnam')}")
    print(f"Nakshatra: {res.get('vedic', {}).get('nakshatra')}")
    
    print("\n--- Western Summary ---")
    print(f"Sun Sign: {res.get('western', {}).get('calculations', {}).get('planets', {}).get('Sun', {}).get('sign')}")
    print(f"Moon Sign: {res.get('western', {}).get('calculations', {}).get('planets', {}).get('Moon', {}).get('sign')}")
    
    print("\n--- Chinese Summary ---")
    print(f"Zodiac Sign: {res.get('chinese', {}).get('calculations', {}).get('bazi_details', {}).get('Year', {}).get('Branch', {}).get('animal')}")
    print(f"Element: {res.get('chinese', {}).get('calculations', {}).get('bazi_details', {}).get('Year', {}).get('Branch', {}).get('element')}")
    
    print("\n--- Mayan Summary ---")
    print(f"Tzolkin Sign: {res.get('mayan', {}).get('calculations', {}).get('day_glyph', {}).get('name')}")
    
    print("\n--- Numerology Summary ---")
    print(f"Life Path Number (Bhagya): {res.get('numerology', {}).get('calculations', {}).get('tamil_chaldean', {}).get('bhagya_number')}")
    print(f"Destiny/Expression Number: {res.get('numerology', {}).get('calculations', {}).get('pythagorean_triad', {}).get('expression_number')}")

    # Query Neo4j to verify relationships
    print("\n--- Verifying Neo4j Relationships ---")
    driver = get_driver()
    with driver.session() as session:
        cypher = """
            MATCH (p:Person {name: "Albert Einstein"})
            OPTIONAL MATCH (p)-[:HAS_WESTERN_SIGN]->(ws:WesternSign)
            OPTIONAL MATCH (p)-[:HAS_CHINESE_ANIMAL]->(ca:ChineseAnimal)
            OPTIONAL MATCH (p)-[:HAS_LIFE_PATH]->(lp:LifePath)
            RETURN ws.name AS WesternSign, ca.name AS ChineseAnimal, lp.number AS LifePath
        """
        records = list(session.run(cypher))
        if records:
            r = records[0]
            print(f"Linked Western Sign: {r['WesternSign']}")
            print(f"Linked Chinese Animal: {r['ChineseAnimal']}")
            print(f"Linked Life Path: {r['LifePath']}")
        else:
            print("No matching Person node found in Neo4j.")
else:
    print(f"Error: {response.text}")
