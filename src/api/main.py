import sys
import os
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(_PROJECT_ROOT)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from engine.western_engine import compute_western_chart
from engine.chinese_engine import compute_chinese_chart
from engine.mayan_engine import compute_mayan_chart
from engine.numerology_engine import compute_numerology_report
import swisseph as swe
import json
import math
import tempfile
import subprocess
import uuid

# Import from refactored src modules
from src.core.config import RULES, CORPUS, DEFAULT_TZ_HOURS
from src.core.tier_auth import cors_allowed_origins, resolve_user_tier, gate_jathagam_payload
from src.models.schemas import BirthData
from src.utils.translators import translate_response_data
from src.services.jathagam_service import jathagam

from engine.truth_policy import assert_production_clean, build_client_truth_block

app = FastAPI(title="AstroMystic Tamil Jyotisham Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

from engine.comparative_test import execute_corpus_battle_comparison

from engine.chart_builder import (
    RASIS,
    NAKSHATRAS,
    PLANETS,
    SIGN_LORD,
    build_sidereal_chart,
    build_orchestrator_chart_dict,
)

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

_FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend")
_STATIC_DIR = os.path.join(_FRONTEND_DIR, "static")

if os.path.isdir(_STATIC_DIR):
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    index_html = os.path.join(_FRONTEND_DIR, "index.html")
    with open(index_html, "r", encoding="utf-8") as f:
        return f.read()


@app.get("/api/engine")
def engine_status():
    cs = CORPUS.stats
    return {
        "status": "AstroMystic Engine Running",
        "truth_policy": assert_production_clean(),
        "documentation": "docs/ENGINE_TRUTH_POLICY.md",
        "corpus": {
            "total_unique_rules": cs["total_unique_rules"],
            "books": cs["books_loaded"],
            "planet_house_slots": cs["planet_house_slots"],
            "yoga_rules": cs["yoga_rules"],
            "dasha_rules": cs["dasha_rules"],
        },
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tools", response_class=HTMLResponse)
def tools_page():
    tools_html = os.path.join(_FRONTEND_DIR, "tools.html")
    with open(tools_html, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/api/jathagam")
async def jathagam_endpoint(data: BirthData):
    return await jathagam(data)


@app.post("/api/book-battle")
async def book_battle(data: BirthData):
    # Reuse the logic from jathagam to get the base chart
    # (In a real app, we'd refactor this into a common 'get_base_chart' function)
    # For now, we'll just run the full analysis and then split it
    full_data = await jathagam(data)
    battle_report = execute_corpus_battle_comparison(full_data)
    
    return {
        "status": "success",
        "chart_summary": {
            "lagnam": full_data["lagnam"],
            "rasi": full_data["janma_rasi"]
        },
        "battle_results": battle_report,
        "battle_note": (
            "Each subject shows agreement among classical book passages for that placement — "
            "not a forecast probability."
        ),
        "truth": full_data.get("truth"),
        "full_data": full_data
    }

class WesternRequest(BaseModel):
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    tz_hours: float
    lat: float
    lon: float
    age: int = 30

class ChineseRequest(BaseModel):
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    tz_hours: float

class MayanRequest(BaseModel):
    date: str  # "YYYY-MM-DD"

@app.post("/api/astrology/western")
async def western_astrology(data: WesternRequest):
    return compute_western_chart(data.date, data.time, data.tz_hours, data.lat, data.lon, data.age)

@app.post("/api/astrology/chinese")
async def chinese_astrology(data: ChineseRequest):
    return compute_chinese_chart(data.date, data.time, data.tz_hours)

@app.post("/api/astrology/mayan")
async def mayan_astrology(data: MayanRequest):
    return compute_mayan_chart(data.date)

class NumerologyRequest(BaseModel):
    name: str
    date: str
    target_date: str | None = None

@app.post("/api/astrology/numerology")
async def numerology_analysis(data: NumerologyRequest):
    return compute_numerology_report(data.name, data.date, data.target_date)

class NumerologyMatchRequest(BaseModel):
    name1: str
    date1: str
    name2: str
    date2: str

@app.post("/api/astrology/numerology/compatibility")
async def numerology_compatibility(data: NumerologyMatchRequest):
    from engine.numerology_match import compute_compatibility
    return compute_compatibility(data.name1, data.date1, data.name2, data.date2)

class NameAdvisorRequest(BaseModel):
    name: str
    date: str

@app.post("/api/astrology/numerology/name-advisor")
async def numerology_name_advisor(data: NameAdvisorRequest):
    from engine.numerology_match import name_advisor
    return name_advisor(data.name, data.date)

class ClassicalTimelineRequest(BaseModel):
    year: int
    month: int
    day: int
    time: str      # "HH:MM"
    lat: float
    lon: float
    tz_hours: float = DEFAULT_TZ_HOURS
    start_year: int
    end_year: int
    api_key: str = None

@app.post("/api/astrology/pure-classical")
async def pure_classical_timeline(data: ClassicalTimelineRequest):
    tier = resolve_user_tier(data)
    if tier not in ("professional", "enterprise"):
        raise HTTPException(
            status_code=403,
            detail="Pure Scriptural Mode is a Professional Pro tier feature. Upgrade to unlock."
        )

    chart_dict = build_orchestrator_chart_dict(
        data.year, data.month, data.day, data.time,
        data.lat, data.lon, data.tz_hours,
    )

    from runtime.pure_classical_engine import pure_classical_engine_instance
    events = pure_classical_engine_instance.scan_lifetime(chart_dict, data.start_year, data.end_year, sample_days=14)
    collapsed = pure_classical_engine_instance.collapse_consecutive(events)
    return {
        "status": "success",
        "timeline": collapsed
    }

@app.post("/api/astrology/hybrid")
async def hybrid_timeline(data: ClassicalTimelineRequest):
    tier = resolve_user_tier(data)
    if tier not in ("professional", "enterprise"):
        raise HTTPException(
            status_code=403,
            detail="The Hybridization Bridge is a Professional Pro tier feature. Upgrade to unlock."
        )

    chart_dict = build_orchestrator_chart_dict(
        data.year, data.month, data.day, data.time,
        data.lat, data.lon, data.tz_hours,
    )

    from runtime.engine_pure_hybrid import hybrid_engine_instance
    res = hybrid_engine_instance.scan_hybrid_lifetime(chart_dict, data.start_year, data.end_year, sample_days=14)
    return {
        "status": "success",
        "hybrid_bands": res["hybrid_bands"],
        "classical_only_bands": res["classical_only_bands"]
    }

@app.post("/api/download-pdf")
async def download_pdf(data: BirthData):
    tier = resolve_user_tier(data)
    if tier not in ("professional", "enterprise"):
        raise HTTPException(
            status_code=403,
            detail="PDF downloading is a premium feature. Please upgrade your account to Professional Pro."
        )

    # Compute the base chart in standard English format first
    english_data = await jathagam(BirthData(
        year=data.year, month=data.month, day=data.day, time=data.time,
        lat=data.lat, lon=data.lon, focus=data.focus, lang="en",
        api_key=data.api_key,
    ))
    
    # Format the positions exactly as expected by the PDF generators
    pos_map = {}
    for p, d in english_data["all_planet_positions"].items():
        pos_map[p] = {
            "lon": d["longitude"],
            "rasi": d["rasi"],
            "rasi_idx": RASIS.index(d["rasi"]),
            "nak": d["nakshatra"],
            "nak_lord": d["nakshatra_lord"],
            "pada": d["nakshatra_pada"],
            "house": d["house"],
            "deg": d["longitude"] % 30,
            "lon_abs": d["longitude"]
        }

    chart_dict = {
        "birth": {
            "year": data.year,
            "month": data.month,
            "day": data.day,
            "hour": int(data.time.split(":")[0]),
            "min": int(data.time.split(":")[1]),
            "lat": data.lat,
            "lon": data.lon,
            "place": "Birth Place",
            "weekday": english_data["panchangam"]["vara"]
        },
        "lagna": english_data["lagnam"],
        "lagna_idx": RASIS.index(english_data["lagnam"]),
        "ayanamsa": 23.8068,
        "positions": pos_map,
        "janma_nakshatra": english_data["janma_nakshatra"],
        "janma_nakshatra_lord": english_data["all_planet_positions"]["Moon"]["nakshatra_lord"],
        "moon_rasi": english_data["janma_rasi"],
        "name": "Seeker",
        # lagna lord = ruler of the ascendant sign (not the Moon-sign lord)
        "lagna_lord": SIGN_LORD.get(RASIS.index(english_data["lagnam"]), english_data["rasi_lord"])
        if english_data["lagnam"] in RASIS else english_data["rasi_lord"],
        "lagna_deg": english_data["all_planet_positions"]["Lagna"]["longitude"] % 30,
        "lagna_lon": english_data["all_planet_positions"]["Lagna"]["longitude"],
        "truth_report": english_data.get("truth_report"),
        "traditional_extras": english_data.get("traditional_extras"),
        "identity": english_data.get("identity"),
    }

    # Carry the seeker's identity into the print header when supplied.
    _ident = english_data.get("identity") or {}
    if _ident.get("name"):
        chart_dict["name"] = _ident["name"]
    if _ident.get("birth_place"):
        chart_dict["birth"]["place"] = _ident["birth_place"]

    # Save to temp file
    temp_dir = tempfile.gettempdir()
    chart_filename = os.path.join(temp_dir, f"chart_{uuid.uuid4().hex}.json")
    report_filename = os.path.join(temp_dir, f"report_{uuid.uuid4().hex}.pdf")
    
    with open(chart_filename, "w", encoding="utf-8") as f:
        json.dump(chart_dict, f, ensure_ascii=False, indent=2)

    try:
        import sys
        python_exe = sys.executable or "python"
        
        if data.lang == "ta":
            script_path = os.path.join(_PROJECT_ROOT, "runtime", "generate_tamil_pdf.py")
        elif data.lang == "hi":
            script_path = os.path.join(_PROJECT_ROOT, "runtime", "generate_hindi_pdf.py")
        else:
            script_path = os.path.join(_PROJECT_ROOT, "runtime", "generate_report.py")
            
        cmd = [python_exe, script_path, "--chart", chart_filename, "--out", report_filename]
        
        # Execute command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Check if file was actually produced
        if not os.path.exists(report_filename):
            raise HTTPException(status_code=500, detail="PDF generation succeeded but output file was not found.")
            
        return FileResponse(
            path=report_filename,
            filename=f"AstroVeda_Report_{data.lang.upper()}.pdf",
            media_type="application/pdf"
        )
    except Exception as e:
        print("Subprocess PDF generation failed:", e)
        if 'result' in locals():
            print("Generator Stderr:", result.stderr)
        raise HTTPException(status_code=500, detail=f"PDF Generation failed: {str(e)}")

# ─────────────────────────────────────────────────────────────
# Phase 18: Kundali Match, Muhurta Finder, Prashna Kundali
# ─────────────────────────────────────────────────────────────

class MatchRequest(BaseModel):
    boy_year: int
    boy_month: int
    boy_day: int
    boy_time: str     # "HH:MM"
    boy_lat: float
    boy_lon: float
    boy_tz_hours: float = DEFAULT_TZ_HOURS
    girl_year: int
    girl_month: int
    girl_day: int
    girl_time: str    # "HH:MM"
    girl_lat: float
    girl_lon: float
    girl_tz_hours: float = DEFAULT_TZ_HOURS
    api_key: str = None

@app.post("/api/astrology/match")

async def kundali_match(data: MatchRequest):
    """Ashta-Kuta 36-point compatibility + Mangal Dosha for both partners."""
    from engine.kuta import match_kuta, mangal_dosha
    from engine.chart_builder import julday_from_birth

    swe.set_sid_mode(swe.SIDM_LAHIRI)

    def _get_moon_lon(year, month, day, time_str, lat, lon, tz_hours):
        jd, _, _, _ = julday_from_birth(year, month, day, time_str, tz_hours)
        pos, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        return pos[0] % 360.0

    def _get_chart(year, month, day, time_str, lat, lon, tz_hours):
        core = build_sidereal_chart(year, month, day, time_str, lat, lon, tz_hours)
        return {
            "lagna": core["asc_sid"],
            "positions": {p: d["longitude"] for p, d in core["planet_positions"].items()},
        }

    boy_moon = _get_moon_lon(
        data.boy_year, data.boy_month, data.boy_day,
        data.boy_time, data.boy_lat, data.boy_lon, data.boy_tz_hours,
    )
    girl_moon = _get_moon_lon(
        data.girl_year, data.girl_month, data.girl_day,
        data.girl_time, data.girl_lat, data.girl_lon, data.girl_tz_hours,
    )

    kuta = match_kuta(boy_moon, girl_moon)

    boy_chart = _get_chart(
        data.boy_year, data.boy_month, data.boy_day,
        data.boy_time, data.boy_lat, data.boy_lon, data.boy_tz_hours,
    )
    girl_chart = _get_chart(
        data.girl_year, data.girl_month, data.girl_day,
        data.girl_time, data.girl_lat, data.girl_lon, data.girl_tz_hours,
    )

    boy_mangal = mangal_dosha(boy_chart)
    girl_mangal = mangal_dosha(girl_chart)

    tier = resolve_user_tier(data)
    if tier in ("free", "premium"):
        # Truncated Free Match payload
        return {
            "status": "success",
            "kuta": {
                "boy_moon_sign": kuta.boy_moon,
                "girl_moon_sign": kuta.girl_moon,
                "boy_nakshatra": kuta.boy_nakshatra,
                "girl_nakshatra": kuta.girl_nakshatra,
                "scores": {
                    "varna": {"score": "🔒", "max": 1},
                    "vasya": {"score": "🔒", "max": 2},
                    "tara": {"score": "🔒", "max": 3},
                    "yoni": {"score": "🔒", "max": 4},
                    "graha_maitri": {"score": "🔒", "max": 5},
                    "gana": {"score": "🔒", "max": 6},
                    "bhakoot": {"score": "🔒", "max": 7},
                    "nadi": {"score": "🔒", "max": 8},
                },
                "total": {"score": kuta.total[0], "max": kuta.total[1]},
                "verdict": kuta.verdict,
                "nadi_dosha": "LOCKED - Upgrade to Pro",
                "bhakoot_dosha": "LOCKED - Upgrade to Pro",
                "notes": "Detailed Ashta Koota factors and Mangal Dosha analysis are locked. Upgrade to Professional Pro."
            },
            "boy_mangal_dosha": {"is_mangalik": "LOCKED", "percentage": 0, "placements": []},
            "girl_mangal_dosha": {"is_mangalik": "LOCKED", "percentage": 0, "placements": []},
            "message": "Detailed Ashta Koota factors and Mangal Dosha analysis are locked. Upgrade to Professional Pro."
        }

    return {
        "status": "success",
        "kuta": {
            "boy_moon_sign": kuta.boy_moon,
            "girl_moon_sign": kuta.girl_moon,
            "boy_nakshatra": kuta.boy_nakshatra,
            "girl_nakshatra": kuta.girl_nakshatra,
            "scores": {
                "varna": {"score": kuta.varna[0], "max": kuta.varna[1]},
                "vasya": {"score": kuta.vasya[0], "max": kuta.vasya[1]},
                "tara": {"score": kuta.tara[0], "max": kuta.tara[1]},
                "yoni": {"score": kuta.yoni[0], "max": kuta.yoni[1]},
                "graha_maitri": {"score": kuta.graha_maitri[0], "max": kuta.graha_maitri[1]},
                "gana": {"score": kuta.gana[0], "max": kuta.gana[1]},
                "bhakoot": {"score": kuta.bhakoot[0], "max": kuta.bhakoot[1]},
                "nadi": {"score": kuta.nadi[0], "max": kuta.nadi[1]},
            },
            "total": {"score": kuta.total[0], "max": kuta.total[1]},
            "verdict": kuta.verdict,
            "nadi_dosha": kuta.nadi_dosha,
            "bhakoot_dosha": kuta.bhakoot_dosha,
            "notes": kuta.notes,
        },
        "boy_mangal_dosha": boy_mangal,
        "girl_mangal_dosha": girl_mangal,
    }



class MuhurtaRequest(BaseModel):
    start_date: str    # "YYYY-MM-DD"
    end_date: str      # "YYYY-MM-DD"
    lat: float
    lon: float
    tz_hours: float = DEFAULT_TZ_HOURS
    activity: str = "general"   # marriage, business_start, travel, naming_ceremony, education_start, general
    top_n: int = 10
    api_key: str = None

@app.post("/api/astrology/muhurta")

async def find_muhurta(data: MuhurtaRequest):
    """Find auspicious time windows within a date range for a given activity."""
    import datetime as dt
    from engine.muhurta import find_windows, ACTIVITY_RULES

    start = dt.datetime.strptime(data.start_date, "%Y-%m-%d")
    end = dt.datetime.strptime(data.end_date, "%Y-%m-%d") + dt.timedelta(days=1)

    # Cap range to 30 days max
    if (end - start).days > 30:
        end = start + dt.timedelta(days=30)

    windows = find_windows(start, end, data.lat, data.lon, data.tz_hours,
                           data.activity, step_minutes=60, top_n=data.top_n)

    results = []
    for w in windows:
        results.append({
            "datetime": w.moment.isoformat(),
            "score": w.score,
            "verdict": w.verdict,
            "breakdown": w.breakdown,
            "accepted_factors": w.accepted_factors,
            "rejected_reasons": w.rejected_reasons,
            "citations": w.verbatim_citations or [],
        })

    tier = resolve_user_tier(data)
    if tier == "free":
        # Limit to 1 window and hide citations/breakdown
        results_gated = []
        if results:
            w = results[0]
            results_gated.append({
                "datetime": w["datetime"],
                "score": w["score"],
                "verdict": w["verdict"],
                "breakdown": {},
                "accepted_factors": [],
                "rejected_reasons": [],
                "citations": [],
            })
        return {
            "status": "success",
            "activity": data.activity,
            "available_activities": list(ACTIVITY_RULES.keys()),
            "date_range": {"start": data.start_date, "end": data.end_date},
            "windows": results_gated,
            "message": "Upgrade to Pro to view 10+ timing windows with complete calculations, positive factors, and scriptures."
        }

    return {
        "status": "success",
        "activity": data.activity,
        "available_activities": list(ACTIVITY_RULES.keys()),
        "date_range": {"start": data.start_date, "end": data.end_date},
        "windows": results,
    }



class PrashnaRequest(BaseModel):
    topic: str         # e.g. "marriage", "career", "health", etc.
    lat: float
    lon: float
    tz_hours: float = DEFAULT_TZ_HOURS
    api_key: str = None

@app.post("/api/astrology/prashna")
async def prashna_kundali(data: PrashnaRequest):
    """Cast a Prashna (horary) chart at this exact moment and answer the question."""
    tier = resolve_user_tier(data)
    if tier not in ("professional", "enterprise"):
        raise HTTPException(
            status_code=403,
            detail="Prashna Kundali (Horary Astrology) is a Professional feature. Upgrade to unlock."
        )

    import datetime as dt
    from engine.prashna import answer, QUESTION_HOUSE

    now = dt.datetime.now()

    try:
        result = answer(now, data.lat, data.lon, data.tz_hours, topic=data.topic)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {

        "status": "success",
        "prashna": result,
        "available_topics": sorted(QUESTION_HOUSE.keys()),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="127.0.0.1", port=8000, reload=True)

