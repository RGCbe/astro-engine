import json, sys
sys.path.insert(0, "/opt/astro/runtime")
chart = json.load(open("/opt/astro/charts/manoj_chart.json"))
from event_predictor_v2 import scan_lifetime_v2, collapse_consecutive
b = chart["birth"]
events = scan_lifetime_v2(chart, b["year"], b["year"]+80, sample_days=14, min_severity=3)
bands = collapse_consecutive(events)
top = sorted(bands, key=lambda x: x.get("max_sev", x.get("severity", 0)), reverse=True)[:12]
out = []
for e in top:
    out.append({
        "event": e.get("event"),
        "category": e.get("category"),
        "severity": e.get("severity"),
        "max_sev": e.get("max_sev"),
        "window_start": str(e.get("window_start", ""))[:10],
        "window_end": str(e.get("window_end", ""))[:10],
        "why": (e.get("max_why") or e.get("why") or [])[:4] if isinstance(e.get("max_why") or e.get("why"), list) else e.get("why"),
        "source": e.get("source"),
    })
print(json.dumps(out, indent=2, ensure_ascii=False))
