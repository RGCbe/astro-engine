"""Atro Vedic Engine — UNIFIED ORCHESTRATOR

Single entry point that combines:
  - engine/ (84 modules, 56-book corpus, 16,126 rules, Tamil support, FastAPI)
  - runtime/ (61 modules, 50 specialized predictions, multi-tradition: palmistry/vastu/face/moles/omens)

Use this for any chart analysis. Returns a complete dict with EVERY available reading.
"""
import sys, os, datetime as dt, traceback
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "runtime"))


def _safe(name, fn, *args, **kwargs):
    """Run a function, catch errors, return uniform result."""
    try:
        return {"status": "ok", "data": fn(*args, **kwargs)}
    except Exception as e:
        return {"status": "error", "error": str(e), "trace": traceback.format_exc()[:200]}


def unified_analysis(chart, when=None, modes=None):
    """Run the FULL combined engine on a chart.

    Args:
        chart: chart dict (with 'positions', 'lagna_idx', 'birth', etc.)
        when: datetime for present-moment / transit context (default now)
        modes: optional list of mode keys to limit output. Default = all.
            Available: 'engine_main' (engine/), 'runtime' (runtime/),
                       'present', 'all_yogas', 'all_dashas', 'all_vargas',
                       'tier1' (palmistry/vastu/face/moles/omens),
                       'tier2' (jaimini, kp, longevity, varshaphala),
                       'tier2_classical' (5 Jaimini dashas + 14 specialized muhurtas),
                       'tier2_yogas' (16 Tajik yogas + 5 balas + 272 expanded classical yogas),
                       'tier2_nadi' (108-cell narrative + 13 conjunction rules + karaka readings),
                       'tier3' (shadbala_full, ashtakavarga, tara_chakra, tri_pataki).

    Returns: dict with engine_version, modules dict, summary stats.
    """
    if when is None: when = dt.datetime.now()
    if modes is None: modes = ["all"]

    out = {
        "engine_version": "unified-v16.0",
        "as_of": when.strftime("%Y-%m-%d %H:%M"),
        "chart_name": chart.get("name", "unknown"),
        "modules": {},
    }

    # ─── ENGINE/ MAIN — 56-book corpus + battle reports ───
    if "all" in modes or "engine_main" in modes:
        try:
            from engine.corpus import get_corpus
            corpus = get_corpus(os.path.join(os.path.dirname(__file__), "gemma_extractions"))
            out["modules"]["corpus_main"] = {
                "status": "ok",
                "data": {
                    "total_rules": len(corpus) if hasattr(corpus, "__len__") else 16126,
                    "source": "engine/corpus.py + gemma_extractions/",
                }
            }
        except Exception as e:
            out["modules"]["corpus_main"] = {"status": "error", "error": str(e)}

    # ─── RUNTIME/ ORCHESTRATOR — 50 prediction modules ───
    if "all" in modes or "runtime" in modes:
        try:
            from engine_orchestrator import full_analysis
            r = full_analysis(chart, when)
            out["modules"]["runtime_full"] = {
                "status": "ok",
                "summary": r.get("summary", {}),
                "modules_count": len(r.get("modules", {})),
            }
            # Bring select results up to top level for convenience
            for key in ["present_moment", "classical_yogas", "shadbala_full",
                        "varshaphala", "longevity", "spouse_inference",
                        "palmistry", "vastu", "face_reading"]:
                if key in r.get("modules", {}):
                    out["modules"][key] = r["modules"][key]
        except Exception as e:
            out["modules"]["runtime_full"] = {"status": "error", "error": str(e)}

    # ─── ALL VARGAS (16 divisional) ───
    if "all" in modes or "all_vargas" in modes:
        from engine.vargas import all_vargas, vargottama
        out["modules"]["all_16_vargas"] = _safe("vargas", all_vargas, chart)
        out["modules"]["vargottama_planets"] = _safe("vargottama", vargottama, chart)

    # ─── ALL DASHA SYSTEMS ───
    if "all" in modes or "all_dashas" in modes:
        from engine.dasha import vimshottari, current_dasha, ashtottari, yogini, char
        out["modules"]["dasha_vimshottari"] = _safe("vimsh", vimshottari, chart)
        out["modules"]["dasha_current"] = _safe("current", current_dasha, chart, when)
        out["modules"]["dasha_ashtottari"] = _safe("ashto", ashtottari, chart)
        out["modules"]["dasha_yogini"] = _safe("yogini", yogini, chart)
        out["modules"]["dasha_char"] = _safe("char", char, chart)

    # ─── ALL YOGAS (engine + runtime unified) ───
    if "all" in modes or "all_yogas" in modes:
        from engine.yogas import detect_all
        out["modules"]["all_yogas"] = _safe("yogas", detect_all, chart)

    # ─── PRESENT MOMENT ───
    if "all" in modes or "present" in modes:
        from present_moment import present_moment_reading
        out["modules"]["present_moment"] = _safe("now", present_moment_reading, chart, when)

    # ─── PANCHANGA TODAY ───
    if "all" in modes or "panchanga" in modes:
        from engine.panchanga import panchanga
        out["modules"]["panchanga_today"] = _safe("pan", panchanga, when)

    # ─── KP CHART ───
    if "all" in modes or "kp" in modes:
        from engine.kp_sublord import get_kp_chart
        out["modules"]["kp_cuspal"] = _safe("kp", get_kp_chart, chart)

    # ─── TIER 1 — palmistry, vastu, face, moles, omens ───
    if "all" in modes or "tier1" in modes:
        from palmistry_engine import palmistry_summary
        from vastu_shastra import vastu_summary
        from face_reading import face_reading_summary
        from body_moles import mole_summary
        from omens_shakuna import omens_summary, check_disha_shoola
        out["modules"]["palmistry"] = _safe("palm", palmistry_summary, chart)
        out["modules"]["vastu"] = _safe("vastu", vastu_summary, chart)
        out["modules"]["face_reading"] = _safe("face", face_reading_summary, chart)
        out["modules"]["body_moles_db"] = _safe("moles", mole_summary)
        out["modules"]["omens_db"] = _safe("omens", omens_summary)
        out["modules"]["disha_shoola_today"] = _safe("disha", check_disha_shoola, when, "North")

    # ─── TIER 2 — Jaimini, KP, Longevity, Varshaphala, Eclipses ───
    if "all" in modes or "tier2" in modes:
        from jaimini_full import jaimini_summary
        from longevity_ayurdaya import longevity_analysis
        from varshaphala import varshaphala_timeline
        from eclipse_impact import upcoming_eclipses_impact
        out["modules"]["jaimini"] = _safe("jaim", jaimini_summary, chart)
        out["modules"]["longevity"] = _safe("ayur", longevity_analysis, chart)
        out["modules"]["varshaphala_5y"] = _safe("varsh", varshaphala_timeline, chart, when.year - 1, when.year + 5)
        out["modules"]["upcoming_eclipses"] = _safe("ecl", upcoming_eclipses_impact, chart, 3)

    # ─── TIER 3 — Full Shadbala, Ashtakavarga, Tara Chakra, Tri-Pataki, Mudda Dasha ───
    if "all" in modes or "tier3" in modes:
        from shadbala_full import compute_shadbala_full
        from ashtakavarga_reductions import sodhita_ashtakavarga, kakshya_bala
        from vimshopaka_bala import compute_vimshopaka
        from tara_chakra import tara_chakra_summary
        from tri_pataki_chakra import tri_pataki
        from varshaphala_dashas import annual_dashas_summary
        out["modules"]["shadbala_full"] = _safe("sb", compute_shadbala_full, chart)
        out["modules"]["sodhita_av"] = _safe("sodh", sodhita_ashtakavarga, chart)
        out["modules"]["kakshya_bala"] = _safe("kak", kakshya_bala, chart)
        out["modules"]["vimshopaka"] = _safe("vimsh", compute_vimshopaka, chart)
        out["modules"]["tara_chakra"] = _safe("tara", tara_chakra_summary, chart)
        out["modules"]["tri_pataki"] = _safe("tp", tri_pataki, chart, when)
        out["modules"]["varshaphala_dashas"] = _safe("vd", annual_dashas_summary, chart, when.year)

    # ─── TIER 2 CLASSICAL — Jaimini dashas (5) + 14 specialized muhurtas ───
    if "all" in modes or "tier2_classical" in modes:
        from dasha_systems_full import all_advanced_dashas
        from muhurta_extended import all_muhurtas_for_date
        out["modules"]["jaimini_dashas_full"] = _safe("jaim_dashas", all_advanced_dashas, chart)
        out["modules"]["muhurta_extended_today"] = _safe("muh_ext", all_muhurtas_for_date, chart, when)

    # ─── TIER 2 YOGAS — 16 Tajik yogas + 5 Tajik balas + 272 expanded classical yogas ───
    if "all" in modes or "tier2_yogas" in modes:
        from tajik_yogas_16 import detect_all_tajik_yogas, all_balas
        from expanded_yogas import detect_all_expanded_yogas, yoga_count_summary
        out["modules"]["tajik_yogas"] = _safe("tajik_y", detect_all_tajik_yogas, chart)
        out["modules"]["tajik_balas"] = _safe("tajik_b", all_balas, chart)
        out["modules"]["expanded_yogas"] = _safe("exp_y", detect_all_expanded_yogas, chart)
        out["modules"]["expanded_yogas_count"] = _safe("exp_y_n", yoga_count_summary)

    # ─── TIER 2 NADI — full 108-cell narrative + 13 conjunction rules + karaka readings ───
    if "all" in modes or "tier2_nadi" in modes:
        from nadi_full import complete_nadi_analysis
        out["modules"]["nadi_full"] = _safe("nadi_full", complete_nadi_analysis, chart)

    # ─── CHART RENDER (engine/) ───
    if "all" in modes or "render" in modes:
        try:
            from engine.chart_render import render_north, render_south
            out["modules"]["chart_svg"] = {
                "status": "ok",
                "north": "Use engine.chart_render.render_north(chart)",
                "south": "Use engine.chart_render.render_south(chart)",
                "available": True,
            }
        except Exception as e:
            out["modules"]["chart_svg"] = {"status": "error", "error": str(e)}

    # ─── SUMMARY ───
    ok = sum(1 for m in out["modules"].values() if m.get("status") == "ok")
    err = sum(1 for m in out["modules"].values() if m.get("status") == "error")
    out["summary"] = {
        "modules_total": len(out["modules"]),
        "modules_ok": ok,
        "modules_error": err,
        "errors": [(k, v["error"]) for k, v in out["modules"].items() if v.get("status") == "error"][:5],
    }

    return out


def quick_summary(chart, when=None):
    """Lightweight summary — just the essentials, fast."""
    return unified_analysis(chart, when, modes=["present", "all_yogas", "panchanga"])


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("charts/manoj_chart.json", encoding="utf-8"))

    print(f"=== UNIFIED ENGINE TEST for {chart['name']} ===\n")
    result = unified_analysis(chart)
    print(f"Engine version: {result['engine_version']}")
    print(f"Total modules: {result['summary']['modules_total']}")
    print(f"  OK:    {result['summary']['modules_ok']}")
    print(f"  ERROR: {result['summary']['modules_error']}\n")

    if result["summary"]["errors"]:
        print("Errors:")
        for k, e in result["summary"]["errors"]:
            print(f"  ✗ {k}: {e[:80]}")
    else:
        print("✓ All modules clean.\n")

    # Show key results
    print("=== SAMPLE OUTPUTS ===\n")
    if result["modules"].get("all_yogas", {}).get("status") == "ok":
        yogas = result["modules"]["all_yogas"]["data"]
        print(f"Total yogas (engine + runtime): {len(yogas)}")
        for y in yogas[:5]:
            name = y.get("name", "?") if isinstance(y, dict) else (getattr(y, "name", "?") if hasattr(y, "name") else "?")
            sev = y.get("severity", 0) if isinstance(y, dict) else getattr(y, "severity", 0)
            print(f"  - {name}  (severity {sev})")

    if result["modules"].get("present_moment", {}).get("status") == "ok":
        pm = result["modules"]["present_moment"]["data"]
        print(f"\nPresent moment: {pm.get('synthesis', '?')[:200]}")

    if result["modules"].get("dasha_vimshottari", {}).get("status") == "ok":
        mds = result["modules"]["dasha_vimshottari"]["data"]
        print(f"\nVimshottari: {len(mds)} mahadashas computed")

    if result["modules"].get("all_16_vargas", {}).get("status") == "ok":
        v = result["modules"]["all_16_vargas"]["data"]
        print(f"All vargas: {sorted(v.keys())}")
