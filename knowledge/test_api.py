import requests
import json

payload = {
    "name": "Albert Einstein",
    "year": 1879,
    "month": 3,
    "day": 14,
    "time": "11:30",
    "lat": 48.4,
    "lon": 10.0,
    "tz_hours": 1.0
}

url = "http://localhost:8000/api/graph/scripture_rules"
print(f"Sending request to {url}...")
response = requests.post(url, json=payload)
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    res = response.json()
    print("Success!")
    print(f"Name: {res.get('name')}")
    print(f"Total Matching Rules Found in Graph DB: {res.get('n_matching_rules')}")
    
    # Print the first 5 rules
    rules = res.get("matching_rules", [])
    print(f"\nShowing first 5 matching rules:")
    for r in rules[:5]:
        print("-" * 50)
        print(f"Planet: {r.get('planet')} | House: {r.get('house')}")
        print(f"Text: {r.get('text')}")
        print(f"Sanskrit: {r.get('sanskrit')}")
        print(f"Source Books: {', '.join(r.get('books', []))}")
        print(f"Categories: {', '.join(r.get('categories', []))}")
else:
    print(f"Error: {response.text}")
