import json
from pathlib import Path
from main import calculate_jathagam, BirthData

bd = BirthData(year=1955, month=2, day=24, time="19:15", lat=37.775, lon=-122.418, focus="career")
data = calculate_jathagam(bd)

out = {
    "lagnam": data["lagnam"],
    "current_dasha": data["current_dasha"],
    "current_antardasha": data["current_antardasha"],
    "current_antardasha_end": data["current_antardasha_end"],
    "current_yogini_dasha": data["current_yogini_dasha"],
    "shadbala_summary": data.get("shadbala", {}).get("summary", {}),
    "shadbala_planets": data.get("shadbala", {}).get("planets", {}),
    "gochar": data.get("gochar", {}),
    "yoga_count": len(data.get("detected_yogas", [])),
    "total_dasha_periods": len(data.get("all_dasha_periods", [])),
}

Path("full_integration_test.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
)
print(json.dumps(out, indent=2, ensure_ascii=False))
