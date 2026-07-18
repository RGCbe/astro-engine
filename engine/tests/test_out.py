import urllib.request
import json
from pathlib import Path

payload = {"year": 1955, "month": 2, "day": 24, "time": "19:15", "lat": 37.775, "lon": -122.418, "focus": "career"}
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/jathagam",
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method="POST"
)
try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode('utf-8'))
        Path("test_out.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print("Wrote test_out.json")
except Exception as e:
    print(e)
