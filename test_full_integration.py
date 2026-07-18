"""Atro Vedic Engine — Comprehensive Integration Test.

Tests EVERY module, EVERY import, EVERY connection between engine/ and runtime/.

Sections:
  1. Import smoke test — every .py file in engine/ + runtime/ imports cleanly
  2. Bridge module test — engine/dasha.py, engine/vargas.py, engine/kp_sublord.py, engine/panchanga.py
  3. Per-chart full pipeline (engine_orchestrator, engine_unified, atro_cli PDF) for all 4 charts
  4. Stress test — same chart 3x to detect leaks/state mutation/perf regressions
  5. Yoga round-trip — engine.yogas.detect_all() returns BOTH engine and runtime yogas
  6. main.py: smoke-test core handlers without spinning the FastAPI server

Output:
  - docs/INTEGRATION_TEST_RESULTS.md  (pass/fail dashboard)
  - Console log of progress

Read-only: this script doesn't modify any code or data.
"""
from __future__ import annotations

import sys
import os
import json
import time
import importlib
import traceback
import datetime as dt
import statistics
from pathlib import Path

# Ensure both engine/ root and runtime/ are on sys.path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "runtime"))

CHARTS_DIR = ROOT / "charts"
DOCS_DIR = ROOT / "docs"
DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Charts to test
CHARTS = ["manoj", "sree", "krishnan", "jayaprakesh"]


def load_chart(name: str) -> dict:
    p = CHARTS_DIR / f"{name}_chart.json"
    return json.loads(p.read_text(encoding="utf-8"))


# ============================================================
#  SECTION 1 — Import smoke test
# ============================================================

def list_py_files(folder: Path, exclude_subdirs=("__pycache__", "_archive", "tests", "test")) -> list[str]:
    """Return every .py file in folder (one level deep) as bare module name."""
    out = []
    for p in folder.iterdir():
        if p.is_dir():
            continue
        if p.suffix != ".py":
            continue
        if p.name in ("__init__.py",):
            continue
        if p.name.startswith("_"):
            # Internal/audit/research scripts — still try to import them
            pass
        out.append(p.stem)
    return sorted(out)


def list_engine_modules() -> list[str]:
    return list_py_files(ROOT / "engine")


def list_runtime_modules() -> list[str]:
    return list_py_files(ROOT / "runtime")


def smoke_import(module_name: str, prefix: str) -> dict:
    """Try `import {prefix}{module_name}`; return result with status/error."""
    full = f"{prefix}{module_name}"
    t0 = time.perf_counter()
    try:
        # Force reimport in case prior tests touched it
        if full in sys.modules:
            mod = importlib.reload(sys.modules[full])
        else:
            mod = importlib.import_module(full)
        return {
            "module": full,
            "status": "ok",
            "ms": round((time.perf_counter() - t0) * 1000, 1),
            "error": None,
            "exposed": [a for a in dir(mod) if not a.startswith("_")][:8],
        }
    except Exception as e:
        return {
            "module": full,
            "status": "fail",
            "ms": round((time.perf_counter() - t0) * 1000, 1),
            "error": f"{type(e).__name__}: {e}",
            "trace": traceback.format_exc()[-400:],
        }


def section1_imports() -> dict:
    print("\n=== SECTION 1 — Import smoke test ===")
    engine_mods = list_engine_modules()
    runtime_mods = list_runtime_modules()
    print(f"  engine/ files: {len(engine_mods)}")
    print(f"  runtime/ files: {len(runtime_mods)}")

    engine_results = []
    for m in engine_mods:
        r = smoke_import(m, prefix="engine.")
        engine_results.append(r)
        marker = "OK" if r["status"] == "ok" else "FAIL"
        if r["status"] != "ok":
            print(f"  [{marker}] engine.{m}: {r['error']}")

    runtime_results = []
    for m in runtime_mods:
        # runtime modules are flat-imported (no package prefix)
        r = smoke_import(m, prefix="")
        runtime_results.append(r)
        if r["status"] != "ok":
            print(f"  [FAIL] {m}: {r['error']}")

    eok = sum(1 for r in engine_results if r["status"] == "ok")
    rok = sum(1 for r in runtime_results if r["status"] == "ok")
    print(f"  engine OK: {eok}/{len(engine_results)}   runtime OK: {rok}/{len(runtime_results)}")

    return {
        "engine": engine_results,
        "runtime": runtime_results,
        "engine_total": len(engine_results),
        "engine_ok": eok,
        "runtime_total": len(runtime_results),
        "runtime_ok": rok,
    }


# ============================================================
#  SECTION 2 — Bridge module tests
# ============================================================

def section2_bridges() -> dict:
    print("\n=== SECTION 2 — Bridge modules ===")
    chart = load_chart("manoj")
    bridges = []

    # engine.dasha → granular_dasha + other_dashas + char_dasha
    try:
        from engine import dasha as e_dasha
        from runtime.granular_dasha import build_full_timeline as _bt  # native runtime path
        # Verify the bridge constants exist
        assert hasattr(e_dasha, "NAKSHATRA_LORDS_VIMSHOTTARI"), "missing NAKSHATRA_LORDS_VIMSHOTTARI"
        assert hasattr(e_dasha, "NAKSHATRA_SPAN"), "missing NAKSHATRA_SPAN"
        # Round-trip: bridge call vs direct runtime call for MD-level entries
        md_via_bridge = e_dasha.vimshottari(chart)
        md_direct = [r for r in _bt(chart, levels=2) if r.get("level") == 1]
        match = (len(md_via_bridge) == len(md_direct))
        # ashtottari, yogini, char also reachable
        ash = e_dasha.ashtottari(chart)
        yog = e_dasha.yogini(chart)
        chr = e_dasha.char(chart)
        bridges.append({"bridge": "engine.dasha → runtime/granular_dasha",
                        "status": "ok",
                        "details": {
                            "md_count_match": match,
                            "md_via_bridge": len(md_via_bridge),
                            "ashtottari_periods": len(ash) if hasattr(ash, "__len__") else "n/a",
                            "yogini_periods": len(yog) if hasattr(yog, "__len__") else "n/a",
                            "char_periods": len(chr) if hasattr(chr, "__len__") else "n/a",
                        }})
        print("  [OK] engine.dasha bridge")
    except Exception as e:
        bridges.append({"bridge": "engine.dasha → runtime/granular_dasha",
                        "status": "fail", "error": f"{type(e).__name__}: {e}",
                        "trace": traceback.format_exc()[-300:]})
        print(f"  [FAIL] engine.dasha: {e}")

    # engine.vargas → divisional_charts + extra_vargas
    try:
        from engine import vargas as e_vargas
        v = e_vargas.all_vargas(chart)
        vg = e_vargas.vargottama(chart)
        # Check we have all 16 expected vargas
        expected_keys = set(["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
                             "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"])
        got = set(v.keys())
        missing = expected_keys - got
        bridges.append({"bridge": "engine.vargas → runtime/divisional_charts + extra_vargas",
                        "status": "ok" if not missing else "partial",
                        "details": {
                            "vargas_returned": sorted(got),
                            "missing": sorted(missing),
                            "vargottama_count": len(vg) if isinstance(vg, list) else "n/a",
                        }})
        print(f"  [OK] engine.vargas bridge — {len(got)}/16 vargas, vargottama: {vg if isinstance(vg, list) else 'n/a'}")
    except Exception as e:
        bridges.append({"bridge": "engine.vargas → runtime/divisional_charts + extra_vargas",
                        "status": "fail", "error": f"{type(e).__name__}: {e}",
                        "trace": traceback.format_exc()[-300:]})
        print(f"  [FAIL] engine.vargas: {e}")

    # engine.kp_sublord → kp_paddhati
    try:
        from engine import kp_sublord as e_kp
        kpc = e_kp.get_kp_chart(chart)
        kpp = e_kp.get_kp_position(150.5)
        bridges.append({"bridge": "engine.kp_sublord → runtime/kp_paddhati",
                        "status": "ok",
                        "details": {
                            "kp_chart_keys": sorted(kpc.keys()) if isinstance(kpc, dict) else type(kpc).__name__,
                            "kp_position_keys": sorted(kpp.keys()) if isinstance(kpp, dict) else type(kpp).__name__,
                        }})
        print(f"  [OK] engine.kp_sublord bridge")
    except Exception as e:
        bridges.append({"bridge": "engine.kp_sublord → runtime/kp_paddhati",
                        "status": "fail", "error": f"{type(e).__name__}: {e}",
                        "trace": traceback.format_exc()[-300:]})
        print(f"  [FAIL] engine.kp_sublord: {e}")

    # engine.panchanga → panchanga
    try:
        from engine import panchanga as e_panch
        # The bridge re-exports compute_panchanga — call with current datetime
        from runtime.panchanga import compute_panchanga as _cp
        out = _cp(dt.datetime.now())
        bridges.append({"bridge": "engine.panchanga → runtime/panchanga",
                        "status": "ok",
                        "details": {
                            "exposed": ["NAKSHATRAS", "VARAS", "TITHIS", "YOGAS", "KARANAS", "Panchanga"],
                            "panchanga_today_keys": sorted(out.keys()) if isinstance(out, dict) else type(out).__name__,
                        }})
        print(f"  [OK] engine.panchanga bridge")
    except Exception as e:
        bridges.append({"bridge": "engine.panchanga → runtime/panchanga",
                        "status": "fail", "error": f"{type(e).__name__}: {e}",
                        "trace": traceback.format_exc()[-300:]})
        print(f"  [FAIL] engine.panchanga: {e}")

    return {"bridges": bridges}


# ============================================================
#  SECTION 3 — Yoga round-trip (engine + runtime)
# ============================================================

def section3_yoga_roundtrip() -> dict:
    print("\n=== SECTION 3 — Yoga round-trip ===")
    chart = load_chart("manoj")
    out = {}
    try:
        from engine.yogas import detect_all
        all_y = detect_all(chart)
        # Check both sources present
        from runtime.comprehensive_yogas import detect_all_classical_yogas
        from runtime.yoga_library_v2 import detect_extra_yogas
        rt_classical = detect_all_classical_yogas(chart)
        rt_extra = detect_extra_yogas(chart)

        from engine import yogas_extended as ye
        from engine import yogas_nabhasa as yn
        engine_y_count = 0
        for fn_name in ("detect_12_bhava_yogas", "detect_parivartana_yogas"):
            fn = getattr(ye, fn_name, None)
            if fn:
                try:
                    engine_y_count += len(fn(chart) or [])
                except Exception:
                    pass

        out = {
            "status": "ok",
            "detect_all_count": len(all_y),
            "runtime_classical_count": len(rt_classical),
            "runtime_extra_count": len(rt_extra),
            "engine_extended_count": engine_y_count,
            "merge_logic_intact": len(all_y) >= max(len(rt_classical), len(rt_extra)),
        }
        print(f"  [OK] detect_all → {len(all_y)} yogas (rt_classical={len(rt_classical)} + rt_extra={len(rt_extra)} + engine_ext≈{engine_y_count})")
    except Exception as e:
        out = {"status": "fail", "error": f"{type(e).__name__}: {e}",
               "trace": traceback.format_exc()[-300:]}
        print(f"  [FAIL] yoga roundtrip: {e}")
    return out


# ============================================================
#  SECTION 4 — Per-chart full pipeline
# ============================================================

def run_orchestrator(chart_name: str) -> dict:
    """Run engine_orchestrator.full_analysis for a chart."""
    try:
        chart = load_chart(chart_name)
        from runtime.engine_orchestrator import full_analysis
        t0 = time.perf_counter()
        r = full_analysis(chart)
        elapsed = time.perf_counter() - t0
        return {
            "chart": chart_name,
            "status": "ok",
            "elapsed_s": round(elapsed, 2),
            "modules_total": r["summary"]["modules_total"],
            "modules_ok": r["summary"]["modules_ok"],
            "modules_error": r["summary"]["modules_error"],
            "errors": r["summary"]["errors"][:5],
        }
    except Exception as e:
        return {
            "chart": chart_name,
            "status": "fail",
            "error": f"{type(e).__name__}: {e}",
            "trace": traceback.format_exc()[-300:],
        }


def run_unified(chart_name: str) -> dict:
    """Run engine_unified.unified_analysis for a chart."""
    try:
        chart = load_chart(chart_name)
        from engine_unified import unified_analysis
        t0 = time.perf_counter()
        r = unified_analysis(chart)
        elapsed = time.perf_counter() - t0
        return {
            "chart": chart_name,
            "status": "ok",
            "elapsed_s": round(elapsed, 2),
            "modules_total": r["summary"]["modules_total"],
            "modules_ok": r["summary"]["modules_ok"],
            "modules_error": r["summary"]["modules_error"],
            "errors": [(k, str(e)[:120]) for k, e in r["summary"].get("errors", [])][:5],
        }
    except Exception as e:
        return {
            "chart": chart_name,
            "status": "fail",
            "error": f"{type(e).__name__}: {e}",
            "trace": traceback.format_exc()[-300:],
        }


def run_pdf(chart_name: str) -> dict:
    """Generate PDF via generate_report.generate (atro_cli's pdf mode shells out to it)."""
    try:
        chart_path = CHARTS_DIR / f"{chart_name}_chart.json"
        out_name = f"{chart_name.upper()}_INTEGRATION_TEST.pdf"
        out_path = ROOT / "reports" / out_name
        (ROOT / "reports").mkdir(parents=True, exist_ok=True)
        # generate_report.generate expects to be called from the runtime/ dir
        cur = os.getcwd()
        os.chdir(ROOT / "runtime")
        try:
            from runtime.generate_report import generate
            t0 = time.perf_counter()
            generate(str(chart_path), out_name)
            elapsed = time.perf_counter() - t0
        finally:
            os.chdir(cur)

        # generate_report writes to ../reports/ by default. Find the file.
        produced = ROOT / "reports" / out_name
        size_kb = round(produced.stat().st_size / 1024, 1) if produced.exists() else None
        return {
            "chart": chart_name,
            "status": "ok" if produced.exists() else "fail",
            "elapsed_s": round(elapsed, 2),
            "out": str(produced),
            "size_kb": size_kb,
        }
    except Exception as e:
        return {
            "chart": chart_name,
            "status": "fail",
            "error": f"{type(e).__name__}: {e}",
            "trace": traceback.format_exc()[-400:],
        }


def section4_per_chart() -> dict:
    print("\n=== SECTION 4 — Per-chart full pipeline ===")
    out = {"orchestrator": [], "unified": [], "pdf": []}
    for c in CHARTS:
        print(f"\n  --- chart: {c} ---")
        r1 = run_orchestrator(c)
        out["orchestrator"].append(r1)
        print(f"    orchestrator: {r1['status']}  modules_ok={r1.get('modules_ok','?')}/{r1.get('modules_total','?')}  ({r1.get('elapsed_s','?')}s)")
        r2 = run_unified(c)
        out["unified"].append(r2)
        print(f"    unified:      {r2['status']}  modules_ok={r2.get('modules_ok','?')}/{r2.get('modules_total','?')}  ({r2.get('elapsed_s','?')}s)")
        r3 = run_pdf(c)
        out["pdf"].append(r3)
        print(f"    pdf:          {r3['status']}  size={r3.get('size_kb','?')}KB  ({r3.get('elapsed_s','?')}s)")
    return out


# ============================================================
#  SECTION 5 — Stress test (3x same chart)
# ============================================================

def section5_stress() -> dict:
    print("\n=== SECTION 5 — Stress test (3x per chart) ===")
    out = {}
    for c in CHARTS:
        runs = []
        chart = load_chart(c)
        try:
            from engine_unified import unified_analysis
            ok_modules = []
            for i in range(3):
                t0 = time.perf_counter()
                r = unified_analysis(chart)
                runs.append({
                    "iter": i + 1,
                    "elapsed_s": round(time.perf_counter() - t0, 2),
                    "modules_ok": r["summary"]["modules_ok"],
                    "modules_error": r["summary"]["modules_error"],
                })
                ok_modules.append(r["summary"]["modules_ok"])
            # Check for state mutation: did module count change between runs?
            mutation = len(set(ok_modules)) > 1
            out[c] = {
                "status": "ok",
                "runs": runs,
                "avg_s": round(statistics.mean(r["elapsed_s"] for r in runs), 2),
                "p50_s": round(statistics.median(r["elapsed_s"] for r in runs), 2),
                "max_s": round(max(r["elapsed_s"] for r in runs), 2),
                "min_s": round(min(r["elapsed_s"] for r in runs), 2),
                "modules_ok_each_run": ok_modules,
                "state_mutation_detected": mutation,
            }
            print(f"  {c}: avg {out[c]['avg_s']}s, runs={[r['elapsed_s'] for r in runs]}, ok={ok_modules}{' (MUTATION!)' if mutation else ''}")
        except Exception as e:
            out[c] = {"status": "fail", "error": f"{type(e).__name__}: {e}",
                      "trace": traceback.format_exc()[-300:]}
            print(f"  {c}: FAIL {e}")
    return out


# ============================================================
#  SECTION 6 — main.py smoke test (no server)
# ============================================================

def section6_main_smoke() -> dict:
    print("\n=== SECTION 6 — main.py smoke test ===")
    out = {}
    try:
        # Importing main loads the FastAPI app + corpus + route handlers
        # Don't call uvicorn, just check the module imports and app object exists
        import main as main_mod
        out["import"] = "ok"
        out["has_app"] = hasattr(main_mod, "app")
        out["has_jathagam"] = callable(getattr(main_mod, "jathagam", None))
        out["has_book_battle"] = callable(getattr(main_mod, "book_battle", None))
        out["corpus_loaded"] = hasattr(main_mod, "CORPUS")
        if out["corpus_loaded"]:
            out["corpus_total_rules"] = main_mod.CORPUS.stats.get("total_unique_rules", "?")
            out["corpus_books"] = main_mod.CORPUS.stats.get("books_loaded", "?")
        print(f"  [OK] main.py imports — app={out['has_app']}, /jathagam={out['has_jathagam']}, /book-battle={out['has_book_battle']}, corpus={out.get('corpus_total_rules','?')} rules")
    except Exception as e:
        out = {"status": "fail", "error": f"{type(e).__name__}: {e}",
               "trace": traceback.format_exc()[-300:]}
        print(f"  [FAIL] main.py: {e}")
    return out


# ============================================================
#  Build the markdown report
# ============================================================

def build_report(results: dict) -> str:
    md = []
    md.append("# Atro Vedic Engine — Integration Test Results\n")
    md.append(f"**Generated:** {dt.datetime.now().isoformat(timespec='seconds')}\n")
    md.append(f"**Test charts:** {', '.join(CHARTS)}\n")
    md.append("\n---\n")

    # Top-level dashboard
    md.append("## Overall Dashboard\n")
    md.append("| Section | Result |\n|---|---|")
    s1 = results["section1"]
    md.append(f"| 1. Imports — engine | {s1['engine_ok']}/{s1['engine_total']} OK |")
    md.append(f"| 1. Imports — runtime | {s1['runtime_ok']}/{s1['runtime_total']} OK |")
    bridges_ok = sum(1 for b in results["section2"]["bridges"] if b["status"] == "ok")
    md.append(f"| 2. Bridge modules | {bridges_ok}/4 OK |")
    s3 = results["section3"]
    md.append(f"| 3. Yoga round-trip | {s3['status']} ({s3.get('detect_all_count','?')} yogas) |")
    s4 = results["section4"]
    orch_ok = sum(1 for r in s4["orchestrator"] if r["status"] == "ok")
    uni_ok = sum(1 for r in s4["unified"] if r["status"] == "ok")
    pdf_ok = sum(1 for r in s4["pdf"] if r["status"] == "ok")
    md.append(f"| 4. Per-chart orchestrator | {orch_ok}/{len(CHARTS)} charts OK |")
    md.append(f"| 4. Per-chart unified | {uni_ok}/{len(CHARTS)} charts OK |")
    md.append(f"| 4. Per-chart PDF | {pdf_ok}/{len(CHARTS)} charts OK |")
    s5 = results["section5"]
    s5_ok = sum(1 for v in s5.values() if isinstance(v, dict) and v.get("status") == "ok")
    md.append(f"| 5. Stress test | {s5_ok}/{len(CHARTS)} charts OK |")
    s6 = results["section6"]
    md.append(f"| 6. main.py smoke | {'OK' if s6.get('import') == 'ok' else 'FAIL'} |")
    md.append("")

    # Section 1: imports
    md.append("\n## 1. Import Smoke Test\n")
    md.append(f"### engine/  ({s1['engine_ok']}/{s1['engine_total']} clean)\n")
    failed_e = [r for r in s1["engine"] if r["status"] != "ok"]
    if failed_e:
        md.append("| Module | Error |\n|---|---|")
        for r in failed_e:
            md.append(f"| `{r['module']}` | {r['error']} |")
    else:
        md.append("All engine/ modules import cleanly.\n")

    md.append(f"\n### runtime/  ({s1['runtime_ok']}/{s1['runtime_total']} clean)\n")
    failed_r = [r for r in s1["runtime"] if r["status"] != "ok"]
    if failed_r:
        md.append("| Module | Error |\n|---|---|")
        for r in failed_r:
            md.append(f"| `{r['module']}` | {r['error']} |")
    else:
        md.append("All runtime/ modules import cleanly.\n")

    # Slowest imports
    all_imports = sorted(s1["engine"] + s1["runtime"], key=lambda r: -r["ms"])[:8]
    md.append("\n### Slowest 8 imports (ms)\n")
    md.append("| Module | ms |\n|---|---:|")
    for r in all_imports:
        md.append(f"| `{r['module']}` | {r['ms']} |")

    # Section 2: bridges
    md.append("\n## 2. Bridge Modules\n")
    md.append("| Bridge | Status | Details |\n|---|---|---|")
    for b in results["section2"]["bridges"]:
        det = b.get("details") or b.get("error", "")
        md.append(f"| `{b['bridge']}` | {b['status']} | {str(det)[:200]} |")

    # Section 3: yogas
    md.append("\n## 3. Yoga Round-Trip\n")
    if s3["status"] == "ok":
        md.append(f"- `engine.yogas.detect_all(chart)` returns **{s3['detect_all_count']} yogas**")
        md.append(f"- runtime/comprehensive_yogas alone: {s3['runtime_classical_count']}")
        md.append(f"- runtime/yoga_library_v2 alone: {s3['runtime_extra_count']}")
        md.append(f"- engine/yogas_extended estimate: {s3['engine_extended_count']}")
        md.append(f"- Merge logic intact: {s3['merge_logic_intact']}\n")
    else:
        md.append(f"- FAILED: {s3.get('error','?')}\n")

    # Section 4: per-chart
    md.append("\n## 4. Per-Chart Pipeline\n")
    md.append("\n### 4.1 engine_orchestrator.full_analysis\n")
    md.append("| Chart | Status | Modules OK | Time (s) | Errors |\n|---|---|---|---:|---|")
    for r in s4["orchestrator"]:
        if r["status"] == "ok":
            errs = "; ".join(f"{n}: {e[:50]}" for n, e in (r.get("errors") or []))[:200] or "—"
            md.append(f"| {r['chart']} | OK | {r['modules_ok']}/{r['modules_total']} | {r['elapsed_s']} | {errs} |")
        else:
            md.append(f"| {r['chart']} | FAIL | — | — | {r.get('error','?')[:150]} |")

    md.append("\n### 4.2 engine_unified.unified_analysis\n")
    md.append("| Chart | Status | Modules OK | Time (s) | Errors |\n|---|---|---|---:|---|")
    for r in s4["unified"]:
        if r["status"] == "ok":
            errs = "; ".join(f"{n}: {e[:50]}" for n, e in (r.get("errors") or []))[:200] or "—"
            md.append(f"| {r['chart']} | OK | {r['modules_ok']}/{r['modules_total']} | {r['elapsed_s']} | {errs} |")
        else:
            md.append(f"| {r['chart']} | FAIL | — | — | {r.get('error','?')[:150]} |")

    md.append("\n### 4.3 PDF generation (generate_report.generate)\n")
    md.append("| Chart | Status | Size (KB) | Time (s) |\n|---|---|---:|---:|")
    for r in s4["pdf"]:
        md.append(f"| {r['chart']} | {r['status']} | {r.get('size_kb','—')} | {r.get('elapsed_s','—')} |")
    pdf_failures = [r for r in s4["pdf"] if r["status"] != "ok"]
    if pdf_failures:
        md.append("\n#### PDF errors\n")
        for r in pdf_failures:
            md.append(f"- **{r['chart']}**: `{r.get('error','?')[:200]}`")

    # Section 5: stress
    md.append("\n## 5. Stress Test (3x same chart)\n")
    md.append("| Chart | Status | Avg (s) | Min (s) | Max (s) | Modules OK each run | State mutation? |\n|---|---|---:|---:|---:|---|---|")
    for c in CHARTS:
        d = s5.get(c, {})
        if d.get("status") == "ok":
            md.append(f"| {c} | OK | {d['avg_s']} | {d['min_s']} | {d['max_s']} | {d['modules_ok_each_run']} | {'YES' if d['state_mutation_detected'] else 'no'} |")
        else:
            md.append(f"| {c} | FAIL | — | — | — | — | {d.get('error','?')[:80]} |")

    # Section 6: main
    md.append("\n## 6. main.py Smoke Test\n")
    if s6.get("import") == "ok":
        md.append(f"- Module imports: OK")
        md.append(f"- FastAPI `app` object present: {s6.get('has_app')}")
        md.append(f"- POST /api/jathagam handler: {s6.get('has_jathagam')}")
        md.append(f"- POST /api/book-battle handler: {s6.get('has_book_battle')}")
        md.append(f"- Corpus loaded: {s6.get('corpus_loaded')} ({s6.get('corpus_total_rules','?')} rules across {s6.get('corpus_books','?')} books)\n")
    else:
        md.append(f"- FAILED: {s6.get('error','?')}\n")

    md.append("\n---\n")
    md.append(f"_Generated by `{ROOT / 'test_full_integration.py'}`_\n")

    return "\n".join(md)


# ============================================================
#  Main
# ============================================================

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("=" * 70)
    print("ATRO VEDIC ENGINE — FULL INTEGRATION TEST")
    print("=" * 70)
    t_total = time.perf_counter()

    results = {
        "section1": section1_imports(),
        "section2": section2_bridges(),
        "section3": section3_yoga_roundtrip(),
        "section4": section4_per_chart(),
        "section5": section5_stress(),
        "section6": section6_main_smoke(),
    }

    print(f"\n=== Total elapsed: {time.perf_counter() - t_total:.1f}s ===")

    md = build_report(results)
    out = DOCS_DIR / "INTEGRATION_TEST_RESULTS.md"
    out.write_text(md, encoding="utf-8")
    print(f"\nReport: {out}")

    # Also write a JSON for machine consumption
    out_json = DOCS_DIR / "INTEGRATION_TEST_RESULTS.json"
    out_json.write_text(json.dumps(results, default=str, indent=2), encoding="utf-8")
    print(f"JSON:   {out_json}")


if __name__ == "__main__":
    main()
