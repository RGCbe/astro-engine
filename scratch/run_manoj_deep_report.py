#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run full Manoj deep report on VPS - orchestrator, unified, PDF, API-shaped summary."""
from __future__ import annotations

import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

_SCRATCH = Path(__file__).resolve().parent
ROOT = Path("/opt/astro") if Path("/opt/astro").exists() else _SCRATCH.parent
sys.path.insert(0, str(_SCRATCH))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "runtime"))

from _report_out_dir import category_report_dir

REPORTS = ROOT / "reports"
MANOJ_REPORTS = category_report_dir("manoj", base=REPORTS)
CHART_PATH = ROOT / "charts" / "manoj_chart.json"

MAX_STR = 500
MAX_LIST = 20


def json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return str(obj)


def truncate_obj(obj, depth=0):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if depth > 6:
        return "..."
    if isinstance(obj, str):
        return obj if len(obj) <= MAX_STR else obj[:MAX_STR] + "..."
    if isinstance(obj, list):
        if len(obj) > MAX_LIST:
            return [truncate_obj(x, depth + 1) for x in obj[:MAX_LIST]] + [f"...+{len(obj)-MAX_LIST} more"]
        return [truncate_obj(x, depth + 1) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for i, (k, v) in enumerate(obj.items()):
            if i >= 40 and depth == 0:
                out["...truncated_keys"] = len(obj) - 40
                break
            out[k] = truncate_obj(v, depth + 1)
        return out
    return obj


def extract_key_findings(full):
    mods = full.get("modules", {})
    findings = {}

    gd = mods.get("granular_dasha", {})
    if gd.get("status") == "ok":
        findings["active_dasha"] = gd["data"].get("active_now", {})

    cy = mods.get("classical_yogas", {})
    if cy.get("status") == "ok" and isinstance(cy.get("data"), list):
        findings["classical_yogas"] = [
            {"name": y.get("name"), "effect": (y.get("effect") or "")[:120]}
            for y in cy["data"][:12]
        ]

    ey = mods.get("expanded_yogas", {})
    if ey.get("status") == "ok" and isinstance(ey.get("data"), list):
        findings["expanded_yogas_count"] = len(ey["data"])
        findings["expanded_yogas_sample"] = [y.get("name") for y in ey["data"][:8]]

    sb = mods.get("shadbala", {})
    if sb.get("status") == "ok" and isinstance(sb.get("data"), dict):
        findings["shadbala"] = sb["data"]

    sbf = mods.get("shadbala_full", {})
    if sbf.get("status") == "ok":
        findings["shadbala_full_summary"] = truncate_obj(sbf["data"], 2)

    kp = mods.get("kp", {})
    if kp.get("status") == "ok":
        findings["kp"] = truncate_obj(kp["data"], 2)

    le = mods.get("life_events", {})
    if le.get("status") == "ok" and isinstance(le.get("data"), list):
        top = sorted(le["data"], key=lambda x: x.get("peak_severity", x.get("severity", 0)), reverse=True)
        findings["top_life_events"] = [
            {
                "start": e.get("start"),
                "end": e.get("end"),
                "domain": e.get("domain"),
                "severity": e.get("peak_severity", e.get("severity")),
                "summary": (e.get("summary") or e.get("label") or "")[:150],
            }
            for e in top[:15]
        ]

    bc = mods.get("book_citations", {})
    if bc.get("status") == "ok":
        findings["book_citations_sample"] = truncate_obj(bc["data"], 2)

    jm = mods.get("jaimini", {})
    if jm.get("status") == "ok":
        findings["jaimini"] = truncate_obj(jm["data"], 2)

    return findings


def main():
    t_start = time.perf_counter()
    meta = {
        "generated_at": datetime.now().isoformat(),
        "chart_path": str(CHART_PATH),
        "vps_path": "/opt/astro",
    }

    chart = json.loads(CHART_PATH.read_text(encoding="utf-8"))
    birth = chart.get("birth", {})
    meta["canonical_birth"] = {
        "name": chart.get("name", "Manoj"),
        "date": f"{birth.get('year')}-{birth.get('month'):02d}-{birth.get('day'):02d}",
        "time": f"{birth.get('hour', 0):02d}:{birth.get('min', 0):02d}",
        "place": birth.get("place"),
        "lat": birth.get("lat"),
        "lon": birth.get("lon"),
        "tz": 5.5,
        "weekday": birth.get("weekday"),
        "lagna": chart.get("lagna"),
        "lagna_deg": chart.get("lagna_deg"),
        "janma_nakshatra": chart.get("janma_nakshatra"),
        "janma_nakshatra_lord": chart.get("janma_nakshatra_lord"),
        "ayanamsa": chart.get("ayanamsa"),
    }

    results = {"meta": meta, "pipelines": {}, "module_failures": []}

    print("=== full_analysis ===", flush=True)
    t0 = time.perf_counter()
    try:
        from runtime.engine_orchestrator import full_analysis
        full = full_analysis(chart)
        elapsed = round(time.perf_counter() - t0, 2)
        results["pipelines"]["orchestrator"] = {
            "status": "ok",
            "elapsed_s": elapsed,
            "engine_version": full.get("engine_version"),
            "summary": full.get("summary"),
        }
        for name, mod in full.get("modules", {}).items():
            if mod.get("status") == "error":
                results["module_failures"].append({
                    "pipeline": "orchestrator",
                    "module": name,
                    "error": mod.get("error", "")[:200],
                })
        results["key_findings"] = extract_key_findings(full)
        results["positions"] = chart.get("positions")
        truncated_full = {
            "summary": full.get("summary"),
            "engine_version": full.get("engine_version"),
            "as_of": full.get("as_of"),
            "key_findings": results["key_findings"],
            "module_status": {k: v.get("status") for k, v in full.get("modules", {}).items()},
        }
    except Exception as e:
        results["pipelines"]["orchestrator"] = {
            "status": "fail",
            "error": f"{type(e).__name__}: {e}",
            "trace": traceback.format_exc()[-400:],
        }
        truncated_full = results
        full = None

    print("=== unified_analysis ===", flush=True)
    t0 = time.perf_counter()
    try:
        from engine_unified import unified_analysis
        uni = unified_analysis(chart)
        elapsed = round(time.perf_counter() - t0, 2)
        results["pipelines"]["unified"] = {
            "status": "ok",
            "elapsed_s": elapsed,
            "summary": uni.get("summary"),
        }
        for name, mod in uni.get("modules", {}).items():
            if mod.get("status") == "error":
                results["module_failures"].append({
                    "pipeline": "unified",
                    "module": name,
                    "error": mod.get("error", str(mod))[:200],
                })
    except Exception as e:
        results["pipelines"]["unified"] = {
            "status": "fail",
            "error": f"{type(e).__name__}: {e}",
        }

    print("=== PDF ===", flush=True)
    pdf_name = "MANOJ_FULL_DEEP_REPORT.pdf"
    t0 = time.perf_counter()
    try:
        import os
        os.chdir(str(ROOT / "runtime"))
        os.environ["ATRO_REPORTS"] = str(MANOJ_REPORTS)
        from generate_report import generate
        generate(str(CHART_PATH), pdf_name)
        pdf_out = MANOJ_REPORTS / pdf_name
        pdf_size = pdf_out.stat().st_size if pdf_out.exists() else 0
        results["pipelines"]["pdf"] = {
            "status": "ok" if pdf_size > 0 else "fail",
            "path": str(pdf_out),
            "size_kb": round(pdf_size / 1024, 1),
            "elapsed_s": round(time.perf_counter() - t0, 2),
        }
    except Exception as e:
        results["pipelines"]["pdf"] = {
            "status": "fail",
            "error": f"{type(e).__name__}: {e}",
            "elapsed_s": round(time.perf_counter() - t0, 2),
        }

    print("=== API-shaped chart build ===", flush=True)
    t0 = time.perf_counter()
    try:
        from engine.chart_builder import build_sidereal_chart
        b = chart["birth"]
        core = build_sidereal_chart(
            b["year"], b["month"], b["day"],
            f"{b['hour']:02d}:{b['min']:02d}",
            b["lat"], b["lon"], 5.5,
        )
        results["pipelines"]["api_shaped"] = {
            "status": "ok",
            "elapsed_s": round(time.perf_counter() - t0, 2),
            "lagnam_rasi": core.get("lagnam_rasi"),
            "janma_nakshatra": core.get("janma_nakshatra"),
            "navamsa_lagnam": core.get("navamsa_lagnam"),
        }
    except Exception as e:
        results["pipelines"]["api_shaped"] = {
            "status": "fail",
            "error": f"{type(e).__name__}: {e}",
        }

    results["total_runtime_s"] = round(time.perf_counter() - t_start, 2)

    out_json = MANOJ_REPORTS / "MANOJ_FULL_DEEP_REPORT_RUN.json"
    out_json.write_text(json.dumps(truncate_obj(results), indent=2, ensure_ascii=False, default=json_default), encoding="utf-8")
    print(f"WROTE {out_json}", flush=True)
    print(json.dumps(results["pipelines"], indent=2), flush=True)
    if full:
        raw_path = MANOJ_REPORTS / "MANOJ_FULL_DEEP_RAW_TRUNC.json"
        raw_path.write_text(json.dumps(truncate_obj(truncated_full), indent=2, ensure_ascii=False, default=json_default), encoding="utf-8")
        print(f"WROTE {raw_path}", flush=True)


if __name__ == "__main__":
    main()
