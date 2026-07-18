"""engine.jaimini_full — Jaimini Astrology predictive wrapper.

Bridges to runtime/jaimini_full.py.
Exposes: get_jaimini_analysis() — formatting a Parashari chart to Jaimini-compatible and calculating results.
"""
import sys, os
import datetime as dt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))

try:
    from jaimini_full import jaimini_summary, all_jaimini_dashas_full
except ImportError:
    # Fallback to absolute paths or runtime relative imports if needed
    pass

def get_jaimini_analysis(year, month, day, decimal_hour, lat, lon, planet_positions, asc_sid):
    """
    Format a standard chart input into the dictionary structure expected by runtime/jaimini_full.py
    and run comprehensive Jaimini calculations.
    """
    hrs = int(decimal_hour)
    mins = int((decimal_hour - hrs) * 60)
    
    # Standard Jaimini Sign Names (canonical 12 signs)
    SIGN_NAMES = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    # Format compatible chart dictionary
    chart_dict = {
        "lagna_idx": int(asc_sid / 30) % 12,
        "positions": {},
        "birth": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hrs,
            "min": mins
        }
    }
    
    # Map planetary positions
    for p, pdata in planet_positions.items():
        lon = pdata["longitude"]
        rasi_idx = int(lon / 30) % 12
        chart_dict["positions"][p] = {
            "deg": lon % 30,
            "rasi_idx": rasi_idx,
            "rasi": SIGN_NAMES[rasi_idx],
            "lon": lon,
            "lon_abs": lon
        }
        
    try:
        from jaimini_full import jaimini_summary, all_jaimini_dashas_full
        js = jaimini_summary(chart_dict)
        dashas = all_jaimini_dashas_full(chart_dict)
        
        # Serialize datetime objects inside dashas for FastAPI JSON response
        serializable_dashas = {}
        for dasha_name, timeline in dashas.items():
            serializable_timeline = []
            for entry in timeline:
                rec = dict(entry)
                if isinstance(rec.get("start"), dt.datetime):
                    rec["start"] = rec["start"].isoformat()
                if isinstance(rec.get("end"), dt.datetime):
                    rec["end"] = rec["end"].isoformat()
                serializable_timeline.append(rec)
            serializable_dashas[dasha_name] = serializable_timeline
            
        return {
            "summary": js,
            "dashas": serializable_dashas,
            "status": "success"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
