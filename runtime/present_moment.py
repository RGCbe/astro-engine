"""Present Moment Synthesis — what's happening NOW, fusing all 17+ modules.

The biggest missing piece. Combines:
  - Current MD/AD/PD/SD (4-level dasha)
  - Current transit triggers
  - Active yogas (predispositions)
  - Sade Sati phase
  - Tara Bala + Chandra Bala for today
  - Varshaphala year context
  - Any active event predictions
  - Today's panchanga
"""
import sys, datetime as dt
sys.path.insert(0, ".")


def present_moment_reading(chart, now=None):
    """Generate "right now" synthesis for the chart."""
    if now is None: now = dt.datetime.now()
    out = {"as_of": now.strftime("%Y-%m-%d %H:%M")}

    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"])
    out["age"] = round((now - birth_dt).days / 365.25, 1)

    # 1. Active dasha
    try:
        from granular_dasha import build_full_timeline, lookup
        tl = build_full_timeline(chart, levels=4)
        active = lookup(tl, now)
        out["dashas"] = {}
        for level, rec in sorted(active.items()):
            lvl_name = ["","MD","AD","PD","SD"][level]
            lords = "-".join([rec[k] for k in ["md","ad","pd","sd"] if k in rec])
            out["dashas"][lvl_name] = {
                "lords": lords,
                "from": rec["start"].strftime("%Y-%m-%d"),
                "to": rec["end"].strftime("%Y-%m-%d"),
            }
    except Exception as e:
        out["dashas"] = f"Error: {e}"

    # 2. Active transits
    try:
        from transit_engine import detect_triggers
        triggers = detect_triggers(chart, now, orb=2.5)
        out["active_transits"] = [t for t in triggers if t["severity"] in ["VERY HIGH","HIGH"]][:5]
    except Exception as e:
        out["active_transits"] = []

    # 3. Sade Sati phase
    try:
        from sade_sati import compute_sade_sati_periods
        sp = compute_sade_sati_periods(chart, years_horizon=80)
        cur_sade = next((p for p in sp if p["start"] <= now <= p["end"]), None)
        out["sade_sati"] = cur_sade["phase"] if cur_sade else "Not in Sade Sati"
    except Exception:
        out["sade_sati"] = "?"

    # 4. Tara Bala + Chandra Bala for today
    try:
        from muhurta_engine import tara_bala, chandra_bala
        natal_nak = chart.get("janma_nakshatra")
        natal_moon = chart.get("moon_rasi")
        out["tara_bala_today"] = tara_bala(natal_nak, now) if natal_nak else None
        out["chandra_bala_today"] = chandra_bala(natal_moon, now) if natal_moon else None
    except Exception:
        pass

    # 5. Varshaphala for current year
    try:
        from varshaphala import annual_chart
        ac = annual_chart(chart, now.year)
        out["varshaphala"] = {
            "annual_lagna": ac["annual_lagna"],
            "muntha_house": ac["muntha_house"],
            "muntha_sign": ac["muntha_sign"],
            "year_lord": ac["year_lord_varshesha"],
        }
    except Exception as e:
        out["varshaphala"] = f"err: {e}"

    # 6. Today's panchanga
    try:
        from panchanga import compute_panchanga
        out["panchanga_today"] = compute_panchanga(now)
    except Exception:
        pass

    # 7. Active yogas (chart-static)
    try:
        from comprehensive_yogas import detect_all_classical_yogas
        from yoga_library_v2 import detect_extra_yogas
        yogas = detect_all_classical_yogas(chart) + detect_extra_yogas(chart)
        out["active_yogas"] = [{"name":y["name"],"severity":y["severity"]} for y in yogas if y["severity"] >= 4][:10]
    except Exception:
        out["active_yogas"] = []

    # 8. Synthesis narrative
    out["synthesis"] = _synthesize(out)

    return out


def _synthesize(data):
    """Build human-readable narrative of the present moment."""
    parts = []
    age = data.get("age", 0)
    parts.append(f"You are {age:.0f} years old today.")

    dashas = data.get("dashas", {})
    if isinstance(dashas, dict) and "MD" in dashas:
        md = dashas["MD"]["lords"]
        ad = dashas.get("AD", {}).get("lords", "?").split("-")[-1] if "AD" in dashas else "?"
        parts.append(f"Currently in {md} Mahadasha (until {dashas['MD']['to']}); {ad} sub-period.")

    sade = data.get("sade_sati", "")
    if sade and sade != "Not in Sade Sati":
        parts.append(f"Sade Sati: {sade}.")
    elif sade == "Not in Sade Sati":
        parts.append("Not in Sade Sati currently.")

    tb = data.get("tara_bala_today")
    if tb:
        if tb["is_good"]:
            parts.append(f"Today's Tara is favorable ({tb['type']}).")
        else:
            parts.append(f"Today's Tara is challenging ({tb['type']}).")

    cb = data.get("chandra_bala_today")
    if cb:
        parts.append(f"Chandra Bala today: {cb['verdict']}.")

    transits = data.get("active_transits", [])
    if transits:
        parts.append(f"Major transit triggers active: " + "; ".join(t["label"] for t in transits[:3]))

    vp = data.get("varshaphala", {})
    if isinstance(vp, dict) and "muntha_house" in vp:
        parts.append(f"This year's focus (Muntha) on House {vp['muntha_house']} ({vp.get('muntha_sign','?')}).")

    yogas = data.get("active_yogas", [])
    if yogas:
        parts.append(f"Strong active yogas: " + ", ".join(y["name"] for y in yogas[:3]))

    pan = data.get("panchanga_today", {})
    if pan:
        parts.append(f"Today's panchanga: {pan.get('tithi','?')} ({pan.get('paksha','?')}), {pan.get('vara','?')}, Nakshatra {pan.get('nakshatra','?')}, Yoga {pan.get('yoga','?')}.")

    return " ".join(parts)


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    pm = present_moment_reading(chart)
    print(f"=== PRESENT MOMENT for {chart['name']} (as of {pm['as_of']}) ===\n")
    print(f"AGE: {pm['age']}\n")

    print("DASHAS ACTIVE NOW:")
    for lvl, d in pm.get("dashas", {}).items():
        if isinstance(d, dict):
            print(f"  {lvl}: {d['lords']:30s} ({d['from']} to {d['to']})")
    print()

    print(f"SADE SATI: {pm.get('sade_sati')}")
    if pm.get("tara_bala_today"):
        print(f"TARA TODAY: {pm['tara_bala_today']['type']}")
    if pm.get("chandra_bala_today"):
        print(f"CHANDRA BALA: {pm['chandra_bala_today']['verdict']}")

    print(f"\nVARSHAPHALA {dt.datetime.now().year}:")
    vp = pm.get("varshaphala", {})
    if isinstance(vp, dict):
        for k, v in vp.items():
            print(f"  {k}: {v}")

    print(f"\nACTIVE TRANSIT TRIGGERS:")
    for t in pm.get("active_transits", [])[:5]:
        print(f"  [{t['severity']}] {t['label']}")

    print(f"\nTODAY'S PANCHANGA:")
    pan = pm.get("panchanga_today", {})
    for k in ["tithi","paksha","vara","nakshatra","yoga","karana"]:
        if k in pan:
            print(f"  {k}: {pan[k]}")

    print(f"\nACTIVE YOGAS (severity 4+):")
    for y in pm.get("active_yogas", []):
        print(f"  {'*' * y['severity']}  {y['name']}")

    print(f"\nSYNTHESIS: {pm['synthesis']}")
