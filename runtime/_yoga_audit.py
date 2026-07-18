"""Yoga library audit — count claimed vs actually firing.

Phase 1 of the yoga expansion task. Runs comprehensive_yogas, expanded_yogas,
yoga_library_v2 against all 4 charts and produces a coverage report.
"""
import sys, json, os
sys.path.insert(0, ".")
sys.stdout.reconfigure(encoding="utf-8")

CHARTS_DIR = "../charts"
CHARTS = ["manoj_chart.json", "sree_chart.json", "krishnan_chart.json", "jayaprakesh_chart.json"]


def load_chart(fn):
    return json.load(open(os.path.join(CHARTS_DIR, fn), encoding="utf-8"))


def safe_run(fn_call, label):
    try:
        return fn_call()
    except Exception as e:
        print(f"[ERROR] {label}: {type(e).__name__}: {e}")
        return []


def main():
    print("=" * 78)
    print("YOGA LIBRARY AUDIT")
    print("=" * 78)

    # Phase A — module-level counts
    from comprehensive_yogas import ALL_YOGA_FNS, detect_all_classical_yogas
    from expanded_yogas import (
        ALL_DARIDRA, ALL_PUTRA_BANDHYA, DISEASE_YOGAS_DATA, SADHU_YOGAS_DATA,
        CAREER_YOGAS_DATA, MARRIAGE_YOGAS_DATA, TRAVEL_YOGAS_DATA,
        NABHASA_YOGAS_DATA, DHANA_YOGAS_DATA, ARISHTA_YOGAS_DATA,
        detect_all_expanded_yogas, yoga_count_summary,
    )
    from yoga_library_v2 import EXTRA_YOGA_FNS, detect_extra_yogas

    summary = yoga_count_summary()
    comp_count = len(ALL_YOGA_FNS)
    extra_count = len(EXTRA_YOGA_FNS)

    print(f"\nclaimed counts:")
    print(f"  comprehensive_yogas.ALL_YOGA_FNS         = {comp_count} top-level functions (multi-result)")
    print(f"  expanded_yogas total rules               = {summary['total']}")
    for k, v in summary.items():
        if k == "total": continue
        print(f"     {k:24s} {v}")
    print(f"  yoga_library_v2.EXTRA_YOGA_FNS           = {extra_count}")
    grand_claimed = comp_count + summary["total"] + extra_count
    print(f"  GRAND TOTAL (claimed)                    = {grand_claimed}")

    # Phase B — fire on each chart
    print(f"\nfiring counts per chart:")
    chart_stats = {}
    for cf in CHARTS:
        chart = load_chart(cf)
        nm = chart.get("name", cf)
        comp = safe_run(lambda: detect_all_classical_yogas(chart), f"comprehensive {nm}")
        exp = safe_run(lambda: detect_all_expanded_yogas(chart), f"expanded {nm}")
        ext = safe_run(lambda: detect_extra_yogas(chart), f"extra {nm}")
        chart_stats[nm] = {
            "comp": comp, "exp": exp, "ext": ext,
            "total": len(comp) + len(exp) + len(ext)
        }
        print(f"  {nm:20s}: comp={len(comp):3d}  expanded={len(exp):3d}  extra={len(ext):3d}  total={chart_stats[nm]['total']:3d}")

    # Phase C — find unique-firing yoga names across all charts (UNION)
    all_firing = set()
    for nm, st in chart_stats.items():
        for y in st["comp"] + st["exp"] + st["ext"]:
            all_firing.add(y["name"])
    print(f"\nunique yoga NAMES that fire on at least 1 of 4 charts: {len(all_firing)}")

    # Phase D — by category coverage
    cat_count = {}
    for nm, st in chart_stats.items():
        for y in st["exp"]:
            c = y.get("category", "uncategorized")
            cat_count.setdefault(c, set()).add(y["name"])
        for y in st["comp"] + st["ext"]:
            d = y.get("domain", "general")
            cat_count.setdefault(f"domain:{d}", set()).add(y["name"])

    print(f"\nunique yogas firing per category (across all 4 charts):")
    for c, ns in sorted(cat_count.items(), key=lambda kv: -len(kv[1])):
        print(f"  {c:35s} {len(ns):3d}")

    # Phase E — find dead-stubs (predicates that always return False or use 'False'/'True'-only)
    print(f"\nscanning for dead-stub predicates (lambda returns False unconditionally):")
    suspects = []
    for module_name, data in [
        ("DISEASE_YOGAS_DATA", DISEASE_YOGAS_DATA),
        ("SADHU_YOGAS_DATA", SADHU_YOGAS_DATA),
        ("CAREER_YOGAS_DATA", CAREER_YOGAS_DATA),
        ("MARRIAGE_YOGAS_DATA", MARRIAGE_YOGAS_DATA),
        ("TRAVEL_YOGAS_DATA", TRAVEL_YOGAS_DATA),
        ("NABHASA_YOGAS_DATA", NABHASA_YOGAS_DATA),
        ("DHANA_YOGAS_DATA", DHANA_YOGAS_DATA),
        ("ARISHTA_YOGAS_DATA", ARISHTA_YOGAS_DATA),
    ]:
        for entry in data:
            name = entry[0]; fn = entry[1]
            # Try across all 4 charts.
            results_per_chart = []
            for cf in CHARTS:
                try:
                    chart = load_chart(cf)
                    pos = chart["positions"]; li = chart["lagna_idx"]
                    out = fn(pos, li)
                    results_per_chart.append(bool(out))
                except Exception:
                    results_per_chart.append(False)
            # If never fires AND lambda body contains literal "False" - flag it
            import inspect
            try:
                src = inspect.getsource(fn)
            except Exception:
                src = ""
            never_fires = not any(results_per_chart)
            literal_false = "lambda pos, li: False" in src
            if literal_false:
                suspects.append((module_name, name, "literal-False stub", src.strip()[:120]))
            elif never_fires:
                suspects.append((module_name, name, "never fires on test charts", src.strip()[:120]))

    # Group
    literal_stubs = [s for s in suspects if "literal-False" in s[2]]
    never_fire = [s for s in suspects if "literal-False" not in s[2]]

    print(f"\n  LITERAL DEAD-STUBS (predicate is `lambda pos, li: False`):")
    for s in literal_stubs:
        print(f"     {s[0]:25s} {s[1]}")

    print(f"\n  NEVER FIRES on any of 4 test charts ({len(never_fire)} entries):")
    for s in never_fire[:30]:
        print(f"     {s[0]:25s} {s[1]}")
    if len(never_fire) > 30:
        print(f"     ... and {len(never_fire)-30} more")

    return {
        "claimed_total": grand_claimed,
        "unique_firing": len(all_firing),
        "literal_stubs": [(s[0], s[1]) for s in literal_stubs],
        "never_fire_on_4_charts": [(s[0], s[1]) for s in never_fire],
        "chart_totals": {n: s["total"] for n, s in chart_stats.items()},
    }


if __name__ == "__main__":
    res = main()
    # Persist for the report writer
    with open("../docs/_audit_data.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"\naudit data saved -> docs/_audit_data.json")
