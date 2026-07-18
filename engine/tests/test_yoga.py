import json
from main import calculate_jathagam, BirthData
bd = BirthData(year=1955, month=2, day=24, time="19:15", lat=37.775, lon=-122.418, focus="general")
try:
    res = calculate_jathagam(bd)
    print("Detected yogas:", res.get("detected_yogas"))
except Exception as e:
    print("Error:", e)
