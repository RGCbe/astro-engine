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
import os
import tempfile
import subprocess
import uuid

# Import Multi-Language translations
from runtime.tamil_translations import (
    PLANETS_TA, RASIS_TA, NAKSHATRAS_TA, WEEKDAYS_TA, TITHIS_TA, PAKSHA_TA,
    KARANAS_TA, YOGAS_PANCH_TA, HOUSES_TA, SECTION_HEADERS, LABELS,
    MD_THEME_TA, MD_EXPECT_TA, EVENT_PLAIN_TA, YOGA_PLAIN_TA
)
from runtime.hindi_translations import (
    PLANETS_HI, RASIS_HI, NAKSHATRAS_HI, WEEKDAYS_HI, TITHIS_HI, PAKSHA_HI,
    KARANAS_HI, YOGAS_PANCH_HI, HOUSES_HI, SECTION_HEADERS_HI, LABELS_HI,
    MD_THEME_HI, MD_EXPECT_HI, EVENT_PLAIN_HI, YOGA_PLAIN_HI
)

from src.core.tier_auth import resolve_user_tier, gate_jathagam_payload
from src.models.schemas import BirthData
from src.utils.translators import translate_response_data
from src.core.config import RULES, CORPUS
from engine.truth_policy import assert_production_clean, build_client_truth_block
from engine.truth_engine import build_truth_report

from engine.comparative_test import execute_corpus_battle_comparison



from engine.chart_builder import (
    RASIS,
    NAKSHATRAS,
    PLANETS,
    SIGN_LORD,
    build_sidereal_chart,
    build_orchestrator_chart_dict,
    DEFAULT_TZ_HOURS,
)

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]



async def jathagam(data: BirthData):

    core = build_sidereal_chart(
        data.year, data.month, data.day, data.time,
        data.lat, data.lon, data.tz_hours,
    )
    planet_positions = core["planet_positions"]
    asc_sid = core["asc_sid"]
    lagnam_rasi = core["lagnam_rasi"]
    navamsa_lagnam = core["navamsa_lagnam"]
    arudha_lagna = core["arudha_lagna"]
    janma_rasi = core["janma_rasi"]
    janma_nakshatra = core["janma_nakshatra"]
    hrs, mins = core["hrs"], core["mins"]

    class _Chart:
        def __init__(self, lagna_lon, positions):
            self.lagna_lon = lagna_lon
            self.positions = positions

    yoga_positions = {pn: pd["longitude"] for pn, pd in planet_positions.items()}
    chart_obj = _Chart(asc_sid, yoga_positions)

    moon_lon = planet_positions["Moon"]["longitude"]

    # Panchang: Nitya Yoga & Karana
    sun_lon = planet_positions["Sun"]["longitude"]
    # Yoga = (Sun + Moon) / 13.333
    yoga_idx = int(((sun_lon + moon_lon) % 360) / (360/27))
    YOGAS = ["Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Sobhana", "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"]
    nitya_yoga = YOGAS[yoga_idx % 27]

    # Karana = Tithi / 2 (6 degree intervals)
    diff = (moon_lon - sun_lon) % 360
    karana_idx = int(diff / 6)
    KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kintughna"]
    # Karanas rotate in a specific sequence, but for now we'll map the 11 base names
    karana_name = KARANAS[karana_idx % 11]

    # ─── Phase II: Dasha Engine (Maha + Antar + Pratyantar + Yogini) ─────────
    import datetime
    from engine.dasha_compute import calculate_vimshottari, calculate_yogini

    birth_dt = core["birth_dt"]

    vim_res   = calculate_vimshottari(moon_lon, birth_dt)
    yog_res   = calculate_yogini(moon_lon, birth_dt)

    curr_vim       = vim_res["current_maha_dasha"]
    curr_antar     = vim_res.get("current_antardasha")
    curr_pratyantar= vim_res.get("current_pratyantar_dasha")
    curr_yog       = yog_res["current_yogini_dasha"]

    dasha_lord  = curr_vim["lord"] if curr_vim else planet_positions["Moon"]["nakshatra_lord"]
    antar_lord  = curr_antar["lord"] if curr_antar else ""
    dasha_info  = RULES["vimshottari_dasha"].get(dasha_lord, {})

    # Corpus dasha rules for current Maha+Antardasha
    dasha_corpus_rules = []
    try:
        for cr in CORPUS.get_dasha_rules(dasha_lord, antar_lord, limit=5):
            if len(cr.text) > 40:
                dasha_corpus_rules.append({"source": cr.source_label, "text": cr.text})
    except Exception:
        pass

    # ─── Build house-by-house predictions (multi-book corpus) ─────────────────
    from engine.evaluator import evaluate_planet
    house_readings  = []
    lagnam_idx      = RASIS.index(lagnam_rasi)
    corpus_planet_rules: dict = {}

    # Group planets by house to detect conjunctions
    house_planet_map: dict[int, list[str]] = {}
    for pname, pdata in planet_positions.items():
        if pname == "Ketu":
            continue
        h = ((RASIS.index(pdata["rasi"]) - lagnam_idx) % 12) + 1
        house_planet_map.setdefault(h, []).append(pname)

    advanced_reading_html = ""

    for pname, pdata in planet_positions.items():
        if pname == "Ketu":
            continue
        p_rasi_idx = RASIS.index(pdata["rasi"])
        house_num  = ((p_rasi_idx - lagnam_idx) % 12) + 1

        # Primary: Planet × House from all books
        corpus_rules = CORPUS.get_planet_in_house(
            pname, house_num, limit=6, lagna_sign=lagnam_rasi
        )
        # Secondary: Planet × Sign enrichment
        sign_rules = CORPUS.get_planet_in_sign(
            pname, pdata["rasi"], limit=3, lagna_sign=lagnam_rasi
        )
        # Tertiary: Nakshatra-specific
        nak_rules    = CORPUS.get_nakshatra_rules(pdata["nakshatra"], limit=2)
        # Conjunction rules: if other planets share this house
        co_tenants   = [p for p in house_planet_map.get(house_num, []) if p != pname]
        conjunct_rules = []
        if co_tenants:
            conjunct_rules = CORPUS.get_compound_rules([pname] + co_tenants,
                                                        [house_num], limit=3)

        # Deduplicate across all layers
        rule_blocks  = []
        seen_texts   = set()

        for cr in corpus_rules:
            key = cr.text[:80].lower()
            if key not in seen_texts and len(cr.text) > 30:
                rule_blocks.append((cr.source_label, cr.text, "house"))
                seen_texts.add(key)

        if not rule_blocks:   # fallback to legacy
            legacy = RULES["planet_in_house_rules"].get(pname, {}).get(str(house_num), "")
            if legacy:
                rule_blocks.append(("BPHS [legacy]", legacy, "house"))

        sign_blocks = []
        for cr in sign_rules:
            key = cr.text[:80].lower()
            if key not in seen_texts and len(cr.text) > 30:
                sign_blocks.append((cr.source_label, cr.text))
                seen_texts.add(key)

        nak_blocks = []
        for cr in nak_rules:
            key = cr.text[:80].lower()
            if key not in seen_texts and len(cr.text) > 30:
                nak_blocks.append((cr.source_label, cr.text))
                seen_texts.add(key)

        conj_blocks = []
        for cr in conjunct_rules:
            key = cr.text[:80].lower()
            if key not in seen_texts and len(cr.text) > 30:
                conj_blocks.append((cr.source_label, cr.text, co_tenants))
                seen_texts.add(key)

        # Evaluator (Shadbala-informed strength/affliction caveat)
        eval_res    = evaluate_planet(lagnam_rasi, pname, pdata["rasi"], chart_obj)
        caveat_html = ""
        if eval_res["caveat"]:
            color = "#ff4444" if eval_res["is_afflicted"] else "#44ff44"
            bg = "rgba(255,50,50,0.1)" if eval_res["is_afflicted"] else "rgba(50,255,50,0.1)"
            caveat_html = (
                f'<div style="margin-top:10px;padding:10px;background:{bg};'
                f'border-left:3px solid {color};">'
                f'{eval_res["caveat"]}</div>'
            )

        # HTML block
        if rule_blocks:
            rules_html = ""
            for src, txt, *_ in rule_blocks:
                rules_html += (
                    f'<p style="line-height:1.7;color:#eee;margin-bottom:8px;">{txt}</p>'
                    f'<p style="font-size:0.76em;color:#888;margin-bottom:14px;font-style:italic;">&#x2014; {src}</p>'
                )
            if conj_blocks:
                rules_html += f'<p style="font-size:0.82em;color:#b8a040;"><b>Conjunction with {", ".join(co_tenants)}:</b></p>'
                for src, txt, _ in conj_blocks:
                    rules_html += f'<p style="font-size:0.88em;color:#ddd;">{txt[:320]}</p><p style="font-size:0.74em;color:#666;">{src}</p>'
            if sign_blocks:
                rules_html += f'<hr style="border-color:rgba(255,255,255,0.06);"><p style="font-size:0.8em;color:#aaa;"><b>{pname} in {pdata["rasi"]}:</b></p>'
                for src, txt in sign_blocks[:2]:
                    rules_html += f'<p style="font-size:0.87em;color:#ccc;">{txt[:280]}</p><p style="font-size:0.73em;color:#666;">{src}</p>'
            if nak_blocks:
                rules_html += f'<p style="font-size:0.8em;color:#aaa;"><b>Nakshatra — {pdata["nakshatra"]}:</b></p>'
                for src, txt in nak_blocks[:1]:
                    rules_html += f'<p style="font-size:0.87em;color:#ccc;">{txt[:240]}</p><p style="font-size:0.73em;color:#666;">{src}</p>'

            advanced_reading_html += f"""
            <div style="margin-bottom:28px;padding-bottom:18px;border-bottom:1px solid rgba(255,255,255,0.07);">
                <h3 style="color:#d4af37;margin-bottom:8px;">{pname} in House {house_num} ({pdata['rasi']})</h3>
                {rules_html}
                {caveat_html}
            </div>
            """

        corpus_planet_rules[pname] = [
            {"source": src, "text": txt} for src, txt, *_ in rule_blocks
        ]
        house_readings.append({
            "planet":       pname,
            "house":        house_num,
            "rasi":         pdata["rasi"],
            "nakshatra":    pdata["nakshatra"],
            "corpus_rules": corpus_planet_rules.get(pname, []),
            "conjunction_with": co_tenants,
            "evaluation":   eval_res,
        })

    # ─── Rasi & Nakshatra metadata ─────────────────────────────────────────────
    rasi_info = RULES["rasi_descriptions"].get(janma_rasi, {})
    nak_info  = RULES["nakshatra_descriptions"].get(janma_nakshatra, {})

    # ─── Phase III: Yoga Detection ────────────────────────────────────────────
    import engine.yogas_extended as yogas_ext
    class _Chart:
        def __init__(self, lagna_lon, positions):
            self.lagna_lon = lagna_lon
            self.positions = positions

    yoga_positions = {pn: pd["longitude"] for pn, pd in planet_positions.items()}
    chart_obj      = _Chart(asc_sid, yoga_positions)

    detected_yogas = []
    try:
        for y in yogas_ext.detect_all_extended(chart_obj):
            # Enrich yoga with corpus textual evidence
            corpus_yoga_evidence = []
            for cr in CORPUS.get_yoga_rules(y.name.split()[0], limit=2):
                corpus_yoga_evidence.append({"source": cr.source_label, "text": cr.text[:200]})
            detected_yogas.append({
                "name":        y.name,
                "valence":     y.valence,
                "strength":    y.strength,
                "description": y.description,
                "remedy":      y.activation_or_remedy,
                "involves":    y.involves,
                "corpus_evidence": corpus_yoga_evidence,
            })
    except Exception as e:
        print(f"Yoga detection error: {e}")

    # ─── Phase IV: Shadbala ────────────────────────────────────────────────────
    shadbala_scores = {}
    try:
        from engine.shadbala import compute as _shadbala, summary as _sb_summary
        sb_pos    = {p: d["longitude"] for p, d in planet_positions.items()
                     if p not in ("Rahu", "Ketu")}
        sb_scores = _shadbala(sb_pos, asc_sid, jd_ut=core["jd"])
        shadbala_scores = {
            "summary": _sb_summary(sb_scores),
            "planets": {
                p: {
                    "total_rupas":    round(s.total_rupas, 2),
                    "is_strong":      s.is_strong,
                    "sthana_state":   s.components["sthana_state"],
                    "dig_bala_house": s.components["dig_best_house"],
                    "cheshta":        s.components["cheshta"],
                    "drig":           s.components["drig"],
                }
                for p, s in sb_scores.items()
            }
        }
    except Exception as e:
        print(f"Shadbala error: {e}")

    # ─── Phase V: Ashtakavarga ────────────────────────────────────────────────
    ashtakavarga = {}
    try:
        from engine.ashtakavarga import summary as _bav_summary
        bav_data = _bav_summary(chart_obj)
        # Compact form: per-planet strength per house from lagna, SAV summary
        ashtakavarga = {
            "sarva_ashtakavarga": bav_data["sarva_ashtakavarga"],
            "planet_strengths": {
                p: {
                    "total_bindus": bav_data["bhinna_ashtakavarga"][p]["total"],
                    "by_house": [
                        {"house": h["house"], "bindus": h["bindus"], "strength": h["strength"]}
                        for h in bav_data["bhinna_ashtakavarga"][p]["by_house_from_lagna"]
                    ]
                }
                for p in bav_data["bhinna_ashtakavarga"]
            },
            "grand_total": bav_data["sarva_ashtakavarga"]["grand_total"],
        }
    except Exception as e:
        print(f"Ashtakavarga error: {e}")

    # ─── Phase VI: Gochar / Transit Snapshot ──────────────────────────────────
    gochar_snapshot = {}
    try:
        from engine.gochar import get_transit_snapshot
        import datetime as _dt
        natal_moon_sign_idx  = RASIS.index(janma_rasi)
        natal_lagna_sign_idx = RASIS.index(lagnam_rasi)
        natal_pos_map        = {p: d["longitude"] for p, d in planet_positions.items()}
        now_t  = _dt.datetime.now()
        today_jd = swe.julday(now_t.year, now_t.month, now_t.day, 6.5)  # noon IST = 06:30 UT
        gochar_snapshot = get_transit_snapshot(
            natal_moon_sign_idx, natal_lagna_sign_idx, natal_pos_map, today_jd
        )
        # Enrich each transit with corpus transit rules
        for t in gochar_snapshot.get("transit_planets", []):
            corpus_transit = []
            for cr in CORPUS.get_transit_rules(t["planet"], limit=2):
                if len(cr.text) > 40:
                    corpus_transit.append({"source": cr.source_label, "text": cr.text[:200]})
            t["corpus_transit_rules"] = corpus_transit
    except Exception as e:
        print(f"Gochar error: {e}")

    # ─── Phase VII: KP Sub-lord layer (Krishnamurti Paddhati) ─────────────────
    # KP divides each nakshatra into 9 sub-lords proportional to Vimshottari years.
    # The sub-lord of the Moon at birth indicates precise Dasha nature.
    kp_analysis = {}
    try:
        NAK_LENGTH_DEG = 360 / 27
        SUB_ORDER = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
        SUB_YEARS = [7,20,6,10,7,18,16,19,17]
        SUB_TOTAL = sum(SUB_YEARS)  # 120

        nak_idx_moon  = int(moon_lon / NAK_LENGTH_DEG)
        nak_start_deg = nak_idx_moon * NAK_LENGTH_DEG
        deg_in_nak    = moon_lon - nak_start_deg
        nak_lord      = NAKSHATRA_LORDS[nak_idx_moon]
        nak_lord_idx  = SUB_ORDER.index(nak_lord)

        # Walk sub-divisions inside the nakshatra
        sub_size_deg  = NAK_LENGTH_DEG / SUB_TOTAL  # degrees per year-unit
        sub_start     = 0.0
        moon_sub_lord = nak_lord
        for i in range(9):
            sub_lord_idx = (nak_lord_idx + i) % 9
            sub_lord     = SUB_ORDER[sub_lord_idx]
            sub_years    = SUB_YEARS[sub_lord_idx]
            sub_end      = sub_start + sub_years * sub_size_deg
            if sub_start <= deg_in_nak < sub_end:
                moon_sub_lord = sub_lord
                break
            sub_start = sub_end

        # Pull KP-specific corpus rules for sub-lord
        kp_rules = []
        for cr in CORPUS.get_dasha_rules(moon_sub_lord, limit=3):
            if "kp" in cr.categories or "constellation" in cr.categories:
                kp_rules.append({"source": cr.source_label, "text": cr.text[:200]})

        kp_analysis = {
            "moon_nakshatra_lord": nak_lord,
            "moon_sub_lord":       moon_sub_lord,
            "kp_note": (
                f"KP Sub-lord of Moon is {moon_sub_lord}. "
                f"In Krishnamurti system, this sub-lord modifies the quality "
                f"of {nak_lord} Dasha results."
            ),
            "kp_corpus_rules": kp_rules,
        }
    except Exception as e:
        print(f"KP analysis error: {e}")

    # ─── Compact Dasha Schedule (strip heavy antardasha nesting for API) ───────
    dasha_schedule = vim_res["periods"][:9]

    # ─── Phase VIII: Synthesis & Panchangam ──────────────────────────────────
    from engine.synthesis import generate_synthesis
    
    # Calculate Sun-Moon angle for Tithi (Panchangam)
    sun_lon = planet_positions["Sun"]["longitude"]
    moon_lon = planet_positions["Moon"]["longitude"]
    diff = (moon_lon - sun_lon) % 360
    tithi_num = int(diff / 12) + 1
    TITHIS = ["Prathama", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shasthi", "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Pournami/Amavasya"]
    tithi_name = TITHIS[(tithi_num - 1) % 15]
    paksha = "Shukla" if tithi_num <= 15 else "Krishna"

    # Vara (Day of the week)
    VARA = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    # Python: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
    # Mapping to VARA: Mon(0)->1, Tue(1)->2, ..., Sat(5)->6, Sun(6)->0
    day_name = VARA[(birth_dt.weekday() + 1) % 7]

    panchangam = {
        "tithi": f"{tithi_name} ({paksha} Paksha)",
        "vara": day_name,
        "yoga": nitya_yoga,
        "karana": karana_name,
        "nakshatra": janma_nakshatra
    }

    # ─── Alternative Astrology Engines (Phase 8) ─────────────────────────────
    jaimini_analysis = {}
    try:
        from engine.jaimini_full import get_jaimini_analysis
        jaimini_analysis = get_jaimini_analysis(
            data.year, data.month, data.day, core["decimal_hour"], data.lat, data.lon,
            planet_positions, asc_sid
        )
    except Exception as e:
        jaimini_analysis = {"status": "error", "message": str(e)}

    tajika_analysis = {}
    try:
        from engine.tajik import annual_chart as get_annual_chart, summary as get_annual_summary
        import datetime
        curr_year = datetime.datetime.now().year
        age_years = max(0, curr_year - data.year)
        
        natal_lagna_idx = int(asc_sid / 30) % 12
        ann_chart = get_annual_chart(core["jd"], natal_lagna_idx, age_years, data.lat, data.lon)
        tajika_analysis = get_annual_summary(ann_chart)
        tajika_analysis["status"] = "success"
    except Exception as e:
        tajika_analysis = {"status": "error", "message": str(e)}

    nadi_analysis = {}
    try:
        from engine.nadi_jyotish import get_nadi_analysis
        nadi_analysis = get_nadi_analysis(
            data.year, data.month, data.day, core["decimal_hour"], data.lat, data.lon,
            planet_positions, asc_sid
        )
    except Exception as e:
        nadi_analysis = {"status": "error", "message": str(e)}

    # ─── Final Response ────────────────────────────────────────────────────────
    response_data = {
        "status":           "success",
        "engine_version":   "6.0",
        "jaimini_analysis": jaimini_analysis,
        "tajika_analysis":  tajika_analysis,
        "nadi_analysis":    nadi_analysis,
        "corpus_stats": {
            "total_rules":  CORPUS.stats["total_unique_rules"],
            "books":        CORPUS.stats["books_loaded"],
            "deduped":      CORPUS.stats["duplicates_merged"],
        },

        # Chart identifiers
        "lagnam":              lagnam_rasi,
        "navamsa_lagnam":      navamsa_lagnam,
        "arudha_lagna":        arudha_lagna,
        "janma_rasi":          janma_rasi,
        "janma_rasi_tamil":    planet_positions["Moon"]["rasi_tamil"],
        "janma_nakshatra":     janma_nakshatra,
        "panchangam":          panchangam,
        "rasi_lord":           rasi_info.get("lord", ""),
        "rasi_description":    rasi_info.get("description", ""),
        "rasi_positive_traits":rasi_info.get("positive_traits", []),
        "rasi_negative_traits":rasi_info.get("negative_traits", []),
        "nakshatra_deity":     nak_info.get("deity", ""),
        "nakshatra_description":nak_info.get("description", ""),
        "nakshatra_gana":      nak_info.get("gana", ""),

        # Dasha timings (3-tier)
        "current_dasha":              dasha_lord,
        "dasha_start":                curr_vim["start"] if curr_vim else "",
        "dasha_end":                  curr_vim["end"]   if curr_vim else "",
        "dasha_years":                dasha_info.get("years", ""),
        "dasha_meaning":              dasha_info.get("general", ""),
        "current_antardasha":         antar_lord,
        "current_antardasha_end":     curr_antar["end"] if curr_antar else "",
        "current_pratyantar_dasha":   curr_pratyantar["lord"] if curr_pratyantar else "",
        "current_pratyantar_end":     curr_pratyantar["end"]  if curr_pratyantar else "",
        "current_yogini_dasha":       curr_yog["yogini"] if curr_yog else "",
        "current_yogini_lord":        curr_yog["lord"]   if curr_yog else "",
        "dasha_corpus_rules":         dasha_corpus_rules,
        "dasha_schedule":             dasha_schedule,

        # Planet positions
        "all_planet_positions": planet_positions,

        # House predictions (multi-book, multi-layer)
        "house_predictions":    house_readings,

        # Yoga synthesis
        "detected_yogas":       detected_yogas,

        # Strength systems
        "shadbala":             shadbala_scores,
        "ashtakavarga":         ashtakavarga,

        # Transit analysis
        "gochar":               gochar_snapshot,

        # KP sub-lord
        "kp_analysis":          kp_analysis,

        # Full HTML reading
        "advanced_reading_html": advanced_reading_html,
    }

    # Add synthesis
    response_data["synthesis"] = generate_synthesis(response_data)

    # Life-event adapter: horizon-limited scan + convergence gate. Failure here
    # must not break the report — coverage will show life_event: not_run.
    fused_life_events = None
    try:
        from engine.life_event_adapter import build_predictor_chart, fused_life_events_for_horizon
        predictor_chart = build_predictor_chart(
            birth={"year": data.year, "month": data.month, "day": data.day,
                   "hour": core["hrs"], "min": core["mins"],
                   "lat": data.lat, "lon": data.lon, "tz": data.tz_hours},
            planet_positions=planet_positions,
            lagna_idx=RASIS.index(lagnam_rasi) if lagnam_rasi in RASIS else 0,
        )
        fused_life_events = fused_life_events_for_horizon(predictor_chart)
    except Exception:
        fused_life_events = None

    # Knowledge-graph truth report: built on the full (pre-gate, pre-translation)
    # response so claims always reflect complete evidence. Additive only.
    try:
        response_data["truth_report"] = build_truth_report(response_data, life_events=fused_life_events)
        module_failures = response_data["truth_report"]["data_quality"]["partial_failures"]
    except Exception:
        module_failures = ["truth_report"]
        for key in ("jaimini_analysis", "tajika_analysis", "nadi_analysis"):
            block = response_data.get(key) or {}
            if isinstance(block, dict) and block.get("status") == "error":
                module_failures.append(key)
        response_data["truth_report"] = {
            "schema_version": "1.0",
            "report_state": "partial",
            "data_quality": {"birth_input": "provided", "partial_failures": module_failures},
            "chart_facts": [],
            "claims": [],
            "method_coverage": {},
            "graph_summary": {"nodes": 0, "edges": 0, "claims": 0},
            "error": "truth_report_unavailable",
        }

    cs = CORPUS.stats
    response_data["truth"] = build_client_truth_block(
        birth_place_note=(
            f"Birth time {data.time} local; tz_hours={data.tz_hours} "
            f"(UT = local − {data.tz_hours}). Wrong time/zone ⇒ wrong chart."
        ),
        corpus_books=cs.get("books_loaded", 0),
        corpus_rules=cs.get("total_unique_rules", 0),
        modules_failed=module_failures,
    )

    tier = resolve_user_tier(data)
    response_data = gate_jathagam_payload(response_data, tier)

    if data.lang != "en":
        response_data = translate_response_data(response_data, data.lang)

    return response_data
