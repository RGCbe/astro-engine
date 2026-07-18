"""engine.vargas — Divisional chart computation (D1-D60).

Bridges to runtime/divisional_charts.py + extra_vargas.py.
Exposes: all_vargas(), vargottama() — the API engine/chart.py expects.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))

from divisional_charts import build_divisional_chart
from extra_vargas import build_extra_varga, EXTRA_VARGA_FNS, all_vargas_summary


VARGA_LIST = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12",
              "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]


def all_vargas(chart):
    """Compute all 16 divisional charts (Shodashvarga). Returns dict keyed by varga name."""
    out = {}
    for v in VARGA_LIST:
        try:
            if v == "D1":
                out[v] = chart  # native chart is D1
            elif v in EXTRA_VARGA_FNS:
                out[v] = build_extra_varga(chart, v)
            else:
                out[v] = build_divisional_chart(chart, v)
        except Exception as e:
            out[v] = {"error": str(e)}
    return out


def vargottama(chart):
    """Find Vargottama planets (same sign in D1 and D9 — extra strong).

    Returns list of planet names that are Vargottama.
    """
    try:
        d9 = build_divisional_chart(chart, "D9")
        d9_pos = d9["positions"]
        natal_pos = chart["positions"]
        out = []
        for p in d9_pos:
            if p in natal_pos and natal_pos[p]["rasi_idx"] == d9_pos[p]["rasi_idx"]:
                out.append(p)
        return out
    except Exception:
        return []


def varga_summary(chart):
    """Multi-varga overview."""
    return all_vargas_summary(chart)
