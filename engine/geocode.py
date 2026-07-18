"""Geocode — convert place name to lat/lon/timezone for chart computation.

Uses local hardcoded database of common Indian + global cities for offline reliability.
Falls back to Nominatim (OSM) if available and place not in cache.

Returned object has: .lat, .lon, .tz, .place
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Geo:
    place: str
    lat: float
    lon: float
    tz: float = 5.5  # default IST (decimal hours from UTC)
    country: str = "IN"


# Hardcoded city database (lat, lon, timezone-offset-hours, country)
# Covers: Indian cities + major world cities
CITY_DB = {
    # Tamil Nadu
    "coimbatore": (11.0168, 76.9558, 5.5, "IN"),
    "chennai": (13.0827, 80.2707, 5.5, "IN"),
    "madurai": (9.9252, 78.1198, 5.5, "IN"),
    "tiruchirappalli": (10.7905, 78.7047, 5.5, "IN"),
    "trichy": (10.7905, 78.7047, 5.5, "IN"),
    "salem": (11.6643, 78.1460, 5.5, "IN"),
    "tirunelveli": (8.7139, 77.7567, 5.5, "IN"),
    "vellore": (12.9165, 79.1325, 5.5, "IN"),
    "kanchipuram": (12.8342, 79.7036, 5.5, "IN"),
    "thanjavur": (10.7870, 79.1378, 5.5, "IN"),
    "erode": (11.3410, 77.7172, 5.5, "IN"),
    "tiruppur": (11.1085, 77.3411, 5.5, "IN"),
    "tuticorin": (8.7642, 78.1348, 5.5, "IN"),
    "pondicherry": (11.9416, 79.8083, 5.5, "IN"),

    # Karnataka
    "bangalore": (12.9716, 77.5946, 5.5, "IN"),
    "bengaluru": (12.9716, 77.5946, 5.5, "IN"),
    "mysore": (12.2958, 76.6394, 5.5, "IN"),
    "mangalore": (12.9141, 74.8560, 5.5, "IN"),
    "hubli": (15.3647, 75.1240, 5.5, "IN"),
    "udupi": (13.3409, 74.7421, 5.5, "IN"),

    # Kerala
    "kochi": (9.9312, 76.2673, 5.5, "IN"),
    "cochin": (9.9312, 76.2673, 5.5, "IN"),
    "thiruvananthapuram": (8.5241, 76.9366, 5.5, "IN"),
    "trivandrum": (8.5241, 76.9366, 5.5, "IN"),
    "kozhikode": (11.2588, 75.7804, 5.5, "IN"),
    "calicut": (11.2588, 75.7804, 5.5, "IN"),
    "thrissur": (10.5276, 76.2144, 5.5, "IN"),
    "palakkad": (10.7867, 76.6548, 5.5, "IN"),

    # Andhra / Telangana
    "hyderabad": (17.3850, 78.4867, 5.5, "IN"),
    "secunderabad": (17.4399, 78.4983, 5.5, "IN"),
    "vijayawada": (16.5062, 80.6480, 5.5, "IN"),
    "visakhapatnam": (17.6868, 83.2185, 5.5, "IN"),
    "vizag": (17.6868, 83.2185, 5.5, "IN"),
    "tirupati": (13.6288, 79.4192, 5.5, "IN"),
    "guntur": (16.3067, 80.4365, 5.5, "IN"),
    "warangal": (17.9784, 79.5941, 5.5, "IN"),

    # Maharashtra
    "mumbai": (19.0760, 72.8777, 5.5, "IN"),
    "bombay": (19.0760, 72.8777, 5.5, "IN"),
    "pune": (18.5204, 73.8567, 5.5, "IN"),
    "nagpur": (21.1458, 79.0882, 5.5, "IN"),
    "nashik": (19.9975, 73.7898, 5.5, "IN"),
    "aurangabad": (19.8762, 75.3433, 5.5, "IN"),
    "kolhapur": (16.7050, 74.2433, 5.5, "IN"),

    # North India
    "delhi": (28.6139, 77.2090, 5.5, "IN"),
    "new delhi": (28.6139, 77.2090, 5.5, "IN"),
    "noida": (28.5355, 77.3910, 5.5, "IN"),
    "gurgaon": (28.4595, 77.0266, 5.5, "IN"),
    "gurugram": (28.4595, 77.0266, 5.5, "IN"),
    "faridabad": (28.4089, 77.3178, 5.5, "IN"),
    "ghaziabad": (28.6692, 77.4538, 5.5, "IN"),
    "lucknow": (26.8467, 80.9462, 5.5, "IN"),
    "kanpur": (26.4499, 80.3319, 5.5, "IN"),
    "jaipur": (26.9124, 75.7873, 5.5, "IN"),
    "agra": (27.1767, 78.0081, 5.5, "IN"),
    "varanasi": (25.3176, 82.9739, 5.5, "IN"),
    "kashi": (25.3176, 82.9739, 5.5, "IN"),
    "allahabad": (25.4358, 81.8463, 5.5, "IN"),
    "prayagraj": (25.4358, 81.8463, 5.5, "IN"),
    "patna": (25.5941, 85.1376, 5.5, "IN"),
    "amritsar": (31.6340, 74.8723, 5.5, "IN"),
    "ludhiana": (30.9010, 75.8573, 5.5, "IN"),
    "chandigarh": (30.7333, 76.7794, 5.5, "IN"),
    "shimla": (31.1048, 77.1734, 5.5, "IN"),
    "srinagar": (34.0837, 74.7973, 5.5, "IN"),
    "dehradun": (30.3165, 78.0322, 5.5, "IN"),
    "haridwar": (29.9457, 78.1642, 5.5, "IN"),
    "rishikesh": (30.0869, 78.2676, 5.5, "IN"),

    # East India
    "kolkata": (22.5726, 88.3639, 5.5, "IN"),
    "calcutta": (22.5726, 88.3639, 5.5, "IN"),
    "bhubaneswar": (20.2961, 85.8245, 5.5, "IN"),
    "guwahati": (26.1445, 91.7362, 5.5, "IN"),

    # West India
    "ahmedabad": (23.0225, 72.5714, 5.5, "IN"),
    "surat": (21.1702, 72.8311, 5.5, "IN"),
    "vadodara": (22.3072, 73.1812, 5.5, "IN"),
    "rajkot": (22.3039, 70.8022, 5.5, "IN"),
    "indore": (22.7196, 75.8577, 5.5, "IN"),
    "bhopal": (23.2599, 77.4126, 5.5, "IN"),

    # International - top traffic
    "new york": (40.7128, -74.0060, -5.0, "US"),
    "los angeles": (34.0522, -118.2437, -8.0, "US"),
    "chicago": (41.8781, -87.6298, -6.0, "US"),
    "san francisco": (37.7749, -122.4194, -8.0, "US"),
    "london": (51.5074, -0.1278, 0.0, "UK"),
    "dubai": (25.2048, 55.2708, 4.0, "AE"),
    "singapore": (1.3521, 103.8198, 8.0, "SG"),
    "sydney": (-33.8688, 151.2093, 10.0, "AU"),
    "toronto": (43.6532, -79.3832, -5.0, "CA"),
    "tokyo": (35.6762, 139.6503, 9.0, "JP"),
    "hong kong": (22.3193, 114.1694, 8.0, "HK"),
    "berlin": (52.5200, 13.4050, 1.0, "DE"),
    "paris": (48.8566, 2.3522, 1.0, "FR"),
    "moscow": (55.7558, 37.6173, 3.0, "RU"),
}


def geocode(place: str, country: Optional[str] = None) -> Optional[Geo]:
    """Look up lat/lon/tz for a place name.

    Args:
        place: City name (case-insensitive). Can include country suffix like "Coimbatore, India"
        country: optional 2-letter country code filter

    Returns:
        Geo dataclass or None if not found.
    """
    if not place:
        return None

    # Normalize: strip, lowercase, remove country suffix
    p = place.strip().lower()
    if "," in p:
        p = p.split(",")[0].strip()

    # Direct hit
    if p in CITY_DB:
        lat, lon, tz, c = CITY_DB[p]
        return Geo(place=place, lat=lat, lon=lon, tz=tz, country=c)

    # Fuzzy: substring match
    matches = [(k, v) for k, v in CITY_DB.items() if p in k or k in p]
    if matches:
        # Prefer shortest match (most specific)
        matches.sort(key=lambda x: len(x[0]))
        k, (lat, lon, tz, c) = matches[0]
        return Geo(place=place, lat=lat, lon=lon, tz=tz, country=c)

    # Try Nominatim if available (online fallback)
    try:
        import requests
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": place, "format": "json", "limit": 1},
            headers={"User-Agent": "AtroVedic/1.0"},
            timeout=5,
        )
        if r.ok and r.json():
            d = r.json()[0]
            return Geo(
                place=place,
                lat=float(d["lat"]),
                lon=float(d["lon"]),
                tz=5.5,  # default IST; real TZ requires another API
                country=d.get("display_name", "").split(",")[-1].strip()[:2].upper() or "??",
            )
    except Exception:
        pass

    return None


def lookup(place: str) -> Optional[Geo]:
    """Alias for geocode() — some legacy code uses this name."""
    return geocode(place)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    test_places = ["Coimbatore", "Chennai", "Bangalore", "Mumbai", "Delhi",
                   "Coimbatore, India", "Madurai", "Trichy", "Hyderabad",
                   "London", "New York", "UnknownCity"]
    for p in test_places:
        g = geocode(p)
        if g:
            print(f"  {p:30s} → {g.lat:>9.4f}, {g.lon:>9.4f}  TZ={g.tz}  ({g.country})")
        else:
            print(f"  {p:30s} → NOT FOUND")
