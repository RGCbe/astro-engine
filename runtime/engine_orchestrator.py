"""Engine Orchestrator — single entry point that runs all 28 modules.

Usage:
  from engine_orchestrator import full_analysis
  result = full_analysis(chart)

Returns a structured dict with all analysis results from every module.
Used by generate_report.py and any external consumer.
"""
import sys, datetime as dt, traceback
sys.path.insert(0, ".")


def safe_run(name, fn, *args, **kwargs):
    """Run a module function, catch errors gracefully."""
    try:
        return {"status": "ok", "data": fn(*args, **kwargs)}
    except Exception as e:
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()[:300]}


def full_analysis(chart, when=None):
    """Run every engine module on the chart. Returns nested dict."""
    if when is None:
        when = dt.datetime.now()

    result = {
        "engine_version": "v15.1",
        "as_of": when.strftime("%Y-%m-%d %H:%M"),
        "chart_name": chart.get("name", "unknown"),
        "modules": {},
    }

    # ─── DASHA SYSTEMS ───
    from granular_dasha import build_full_timeline, lookup
    result["modules"]["granular_dasha"] = safe_run(
        "granular_dasha",
        lambda: {
            "timeline": build_full_timeline(chart, levels=3),
            "active_now": lookup(build_full_timeline(chart, levels=4), when),
        }
    )

    from other_dashas import compute_ashtottari, compute_yogini
    result["modules"]["ashtottari_dasha"] = safe_run("ashtottari", compute_ashtottari, chart)
    result["modules"]["yogini_dasha"] = safe_run("yogini", compute_yogini, chart)

    from char_dasha import char_dasha
    result["modules"]["char_dasha"] = safe_run("char_dasha", char_dasha, chart)

    # ─── DIVISIONAL CHARTS ───
    from divisional_charts import full_varga_analysis
    result["modules"]["divisional_charts"] = safe_run("vargas", full_varga_analysis, chart, with_citations=False)

    from extra_vargas import all_vargas_summary
    result["modules"]["all_vargas"] = safe_run("all_vargas", all_vargas_summary, chart)

    # ─── YOGAS ───
    from comprehensive_yogas import detect_all_classical_yogas
    result["modules"]["classical_yogas"] = safe_run("yogas", detect_all_classical_yogas, chart)

    from yoga_library_v2 import detect_extra_yogas
    result["modules"]["extra_yogas"] = safe_run("extra_yogas", detect_extra_yogas, chart)

    # ─── STRENGTHS ───
    from engine.shadbala import compute_shadbala
    result["modules"]["shadbala"] = safe_run("shadbala", compute_shadbala, chart)

    from engine.ashtakavarga import compute_bhinna_ashtakavarga, compute_sarvashtakavarga
    bhinna_data = safe_run("bhinna_av", compute_bhinna_ashtakavarga, chart)
    if bhinna_data["status"] == "ok":
        result["modules"]["bhinna_ashtakavarga"] = bhinna_data
        result["modules"]["sarvashtakavarga"] = safe_run("sarva_av", compute_sarvashtakavarga, bhinna_data["data"])

    # ─── ASPECTS / CONJUNCTIONS ───
    from aspects_engine import detect_significant_aspects
    result["modules"]["aspects"] = safe_run("aspects", detect_significant_aspects, chart, severity_min=3)

    from conjunction_effects import detect_conjunctions
    result["modules"]["conjunctions"] = safe_run("conjunctions", detect_conjunctions, chart)

    # ─── SADE SATI / TRANSITS ───
    from sade_sati import compute_sade_sati_periods
    result["modules"]["sade_sati"] = safe_run("sade_sati", compute_sade_sati_periods, chart, years_horizon=80)

    from transit_engine import detect_triggers
    result["modules"]["current_transits"] = safe_run("transits", detect_triggers, chart, when, orb=2.5)

    # ─── EVENT PREDICTION ───
    try:
        from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive
        b = chart["birth"]
        events = scan_lifetime_v2(chart, b["year"], b["year"] + 80, sample_days=14, min_severity=3)
        bands = collapse_consecutive(events)
        result["modules"]["life_events"] = {"status": "ok", "data": bands}
    except Exception as e:
        result["modules"]["life_events"] = {"status": "error", "error": str(e)}

    # ─── DECLARATIVE LIFE EVENTS (402 CATEGORIES) ───
    try:
        from category_engine import category_engine_instance
        b = chart["birth"]
        dec_events = category_engine_instance.scan_lifetime(chart, b["year"], b["year"] + 80, sample_days=14, min_probability=0.3)
        dec_bands = category_engine_instance.collapse_consecutive(dec_events)
        result["modules"]["declarative_life_events"] = {"status": "ok", "data": dec_bands}
    except Exception as e:
        result["modules"]["declarative_life_events"] = {"status": "error", "error": str(e)}


    # ─── COMPATIBILITY / SIBLING / SPOUSE ───
    from sibling_predictor import predict_siblings
    result["modules"]["sibling_prediction"] = safe_run("sibling", predict_siblings, chart)

    from spouse_inference import infer_spouse
    result["modules"]["spouse_inference"] = safe_run("spouse", infer_spouse, chart)

    # ─── JAIMINI ───
    from jaimini_full import jaimini_summary
    result["modules"]["jaimini"] = safe_run("jaimini", jaimini_summary, chart)

    from jaimini_full import all_jaimini_dashas_full
    result["modules"]["jaimini_dashas_advanced"] = safe_run(
        "jaimini_dashas_adv", all_jaimini_dashas_full, chart)

    from argala_jaimini import compute_argala
    result["modules"]["argala"] = safe_run("argala", compute_argala, chart)

    # ─── KP ───
    from kp_paddhati import kp_summary
    result["modules"]["kp"] = safe_run("kp", kp_summary, chart)

    # ─── LONGEVITY ───
    from longevity_ayurdaya import longevity_analysis
    result["modules"]["longevity"] = safe_run("longevity", longevity_analysis, chart)

    # ─── PANCHANGA / MUHURTA ───
    from panchanga import compute_panchanga
    result["modules"]["panchanga_today"] = safe_run("panchanga", compute_panchanga, when)

    from muhurta_engine import muhurta_check
    result["modules"]["muhurta_today"] = safe_run("muhurta", muhurta_check, chart, when, "generic")

    # ─── SPECIAL LAGNAS ───
    from special_lagnas import all_special_lagnas
    result["modules"]["special_lagnas"] = safe_run("lagnas", all_special_lagnas, chart)

    # ─── UPAGRAHAS ───
    from upagrahas import compute_upagrahas
    result["modules"]["upagrahas"] = safe_run("upagrahas", compute_upagrahas, chart)

    # ─── DOSHAS ───
    from dosha_cancellations import all_doshas_summary
    result["modules"]["doshas"] = safe_run("doshas", all_doshas_summary, chart)

    # ─── VARSHAPHALA ───
    from varshaphala import varshaphala_timeline
    cur_year = when.year
    result["modules"]["varshaphala"] = safe_run("varshaphala", varshaphala_timeline, chart, cur_year - 1, cur_year + 5)

    # ─── SAHAMS ───
    from sahams import compute_sahams
    result["modules"]["sahams"] = safe_run("sahams", compute_sahams, chart)

    # ─── ECLIPSES ───
    from eclipse_impact import upcoming_eclipses_impact
    result["modules"]["upcoming_eclipses"] = safe_run("eclipses", upcoming_eclipses_impact, chart, years_ahead=3)

    # ─── MEDICAL / NUMEROLOGY / LAL KITAB / NADI ───
    from medical_astrology import medical_analysis
    result["modules"]["medical"] = safe_run("medical", medical_analysis, chart)

    from numerology_vedic import vedic_numerology
    result["modules"]["numerology"] = safe_run("numerology", vedic_numerology, chart)

    from engine.lal_kitab import lal_kitab_summary
    result["modules"]["lal_kitab"] = safe_run("lal_kitab", lal_kitab_summary, chart)

    from nadi_jyotish import nadi_analysis
    result["modules"]["nadi"] = safe_run("nadi", nadi_analysis, chart)

    # ─── TRANSIT FORECAST ───
    from transit_forecast import forecast_period
    result["modules"]["forecast_30day"] = safe_run("forecast", forecast_period, chart, when, 30)

    # ─── TIER 5 — RESEARCH-GRADE ───
    from shadbala_full import compute_shadbala_full
    result["modules"]["shadbala_full"] = safe_run("shadbala_full", compute_shadbala_full, chart)

    from ashtakavarga_reductions import sodhita_ashtakavarga, kakshya_bala
    result["modules"]["sodhita_av"] = safe_run("sodhita_av", sodhita_ashtakavarga, chart)
    result["modules"]["kakshya_bala"] = safe_run("kakshya", kakshya_bala, chart)

    from vimshopaka_bala import compute_vimshopaka
    result["modules"]["vimshopaka"] = safe_run("vimshopaka", compute_vimshopaka, chart)

    from tara_chakra import tara_chakra_summary
    result["modules"]["tara_chakra"] = safe_run("tara_chakra", tara_chakra_summary, chart)

    from tri_pataki_chakra import tri_pataki
    result["modules"]["tri_pataki"] = safe_run("tri_pataki", tri_pataki, chart, when)

    from varshaphala_dashas import annual_dashas_summary
    result["modules"]["varshaphala_dashas"] = safe_run("varshaphala_dashas", annual_dashas_summary, chart, when.year)

    # ─── TIER 1 NEW — palmistry, vastu, face, moles, omens ───
    from palmistry_engine import palmistry_summary
    result["modules"]["palmistry"] = safe_run("palmistry", palmistry_summary, chart)

    from vastu_shastra import vastu_summary
    result["modules"]["vastu"] = safe_run("vastu", vastu_summary, chart)

    from vastu_shastra import comprehensive_vastu_audit, VASTU_PURUSHA_MANDALA_81, VASTU_DEVATAS_45
    result["modules"]["vastu_full"] = safe_run("vastu_full", comprehensive_vastu_audit, chart)
    result["modules"]["vastu_mandala_81"] = {"status": "ok", "data": {"cell_count": len(VASTU_PURUSHA_MANDALA_81), "devata_count": len(VASTU_DEVATAS_45)}}

    from face_reading import face_reading_summary
    result["modules"]["face_reading"] = safe_run("face_reading", face_reading_summary, chart)

    from body_moles import mole_summary
    result["modules"]["body_moles_db"] = safe_run("body_moles", mole_summary)

    from omens_shakuna import omens_summary, check_disha_shoola
    result["modules"]["omens_db"] = safe_run("omens", omens_summary)
    result["modules"]["disha_shoola_today"] = safe_run("disha", check_disha_shoola, when, "North")

    from omens_shakuna import shakuna_full_db, omens_for_today
    result["modules"]["shakuna_db_full"] = safe_run("shakuna_db", shakuna_full_db)
    result["modules"]["omens_today"] = safe_run("omens_today", omens_for_today, chart, when)

    # ─── TIER 1 v2 — extended face/body, rare moles, advanced palmistry ───
    from face_reading_v2 import full_body_appearance_prediction
    result["modules"]["face_v2"] = safe_run("face_v2", full_body_appearance_prediction, chart)

    from face_reading_v2 import samudrika_lakshanas, face_features_from_chart, body_part_health_check
    result["modules"]["samudrika"] = safe_run("samudrika", samudrika_lakshanas, chart)
    result["modules"]["face_features"] = safe_run("face_features", face_features_from_chart, chart)
    result["modules"]["body_part_health"] = safe_run("body_part_health", body_part_health_check, chart)

    from body_moles_v2 import mole_summary_v2
    result["modules"]["body_moles_v2"] = safe_run("body_moles_v2", mole_summary_v2)

    from palmistry_v2 import comprehensive_palm_reading
    result["modules"]["palmistry_v2"] = safe_run("palmistry_v2", comprehensive_palm_reading, chart)

    # ─── PRESENT MOMENT ───
    from present_moment import present_moment_reading
    result["modules"]["present_moment"] = safe_run("present", present_moment_reading, chart, when)

    # ─── TIER 2 NEW — Jaimini dashas, extended muhurtas, Tajik yogas, expanded yogas, full Nadi ───
    from dasha_systems_full import all_advanced_dashas
    result["modules"]["jaimini_dashas_full"] = safe_run("jaimini_dashas_full", all_advanced_dashas, chart)

    from dasha_systems_extended import all_extended_dashas, applicable_dashas, DASHA_REGISTRY
    result["modules"]["extended_dashas_30"] = safe_run("extended_dashas_30", all_extended_dashas, chart)
    result["modules"]["applicable_dashas"] = safe_run("applicable_dashas", applicable_dashas, chart)

    from muhurta_extended import all_muhurtas_for_date, ALL_MUHURTAS
    result["modules"]["muhurta_extended_today"] = safe_run("muhurta_extended", all_muhurtas_for_date, chart, when)

    from tajik_yogas_16 import detect_all_tajik_yogas, all_balas
    result["modules"]["tajik_yogas"] = safe_run("tajik_yogas", detect_all_tajik_yogas, chart)
    result["modules"]["tajik_balas"] = safe_run("tajik_balas", all_balas, chart)

    from expanded_yogas import detect_all_expanded_yogas, yoga_count_summary
    result["modules"]["expanded_yogas"] = safe_run("expanded_yogas", detect_all_expanded_yogas, chart)
    result["modules"]["expanded_yogas_count"] = safe_run("expanded_yogas_count", yoga_count_summary)

    from nadi_full import complete_nadi_analysis
    result["modules"]["nadi_full"] = safe_run("nadi_full", complete_nadi_analysis, chart)

    # ─── AVASTHAS — 4 classical state systems ───
    from avasthas_engine import all_avasthas, avastha_summary
    result["modules"]["avasthas_all"] = safe_run("avasthas_all", all_avasthas, chart)
    result["modules"]["avastha_summary"] = safe_run("avastha_summary", avastha_summary, chart)

    # ─── CHAMATKAR CHINTAMANI — 108-verse character reading ───
    from chamatkar_chintamani import chamatkar_reading, chamatkar_summary
    result["modules"]["chamatkar_reading"] = safe_run("chamatkar_reading", chamatkar_reading, chart)
    result["modules"]["chamatkar_summary"] = safe_run("chamatkar_summary", chamatkar_summary, chart)

    # ─── EVENT YOGA DETECTOR — domain-specific event yogas ───
    from event_yoga_detector import detect_all_yogas as detect_event_yogas
    result["modules"]["event_yogas"] = safe_run("event_yogas", detect_event_yogas, chart)

    # ─── CHART RECTIFICATION — candidate birth times ───
    from chart_rectification import rectify_birth_time
    result["modules"]["chart_rectification"] = safe_run("rectification", rectify_birth_time, chart, [])

    # ─── BOOK CITATIONS ───
    from book_citation import citation_for
    citations = {}
    for topic in ["marriage","career","wealth","father","mother","children","health","navamsa_d9","dashamsa_d10"]:
        citations[topic] = citation_for(topic, max_results=2)
    result["modules"]["book_citations"] = {"status": "ok", "data": citations}

    # ─── SUMMARY STATS ───
    ok_count = sum(1 for m in result["modules"].values() if m.get("status") == "ok")
    err_count = sum(1 for m in result["modules"].values() if m.get("status") == "error")
    # ─── CHART PROFILE + TOPIC FUSION (P0-1 / P0-3) ───
    try:
        from engine.chart_profile import build_chart_profile
        from engine.multi_source_synthesis import synthesize_life_topics

        result["chart_profile"] = safe_run("chart_profile", build_chart_profile, chart)
        result["topic_synthesis"] = safe_run("topic_synthesis", synthesize_life_topics, chart)
    except Exception as e:
        result["chart_profile"] = {"status": "error", "error": str(e)}
        result["topic_synthesis"] = {"status": "error", "error": str(e)}

    result["summary"] = {
        "modules_total": len(result["modules"]),
        "modules_ok": ok_count,
        "modules_error": err_count,
        "errors": [(name, m["error"]) for name, m in result["modules"].items() if m.get("status") == "error"],
    }

    return result


def integrity_check(chart):
    """Run all modules, report which work/fail."""
    print(f"=== ENGINE INTEGRITY CHECK for {chart.get('name','?')} ===\n")
    result = full_analysis(chart)
    print(f"Engine version: {result['engine_version']}")
    print(f"As of: {result['as_of']}")
    print(f"Modules total: {result['summary']['modules_total']}")
    print(f"  OK:    {result['summary']['modules_ok']}")
    print(f"  ERROR: {result['summary']['modules_error']}\n")

    if result["summary"]["errors"]:
        print("ERRORS:")
        for name, err in result["summary"]["errors"]:
            print(f"  ✗ {name}: {err}")
    else:
        print("✓ All modules running cleanly.")

    return result


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    integrity_check(chart)
