"""Other Dasha Systems — Ashtottari, Yogini, Kalachakra (basic).

Source: BPHS, Phaladeepika.
"""
import sys, datetime as dt
sys.path.insert(0, ".")

# ASHTOTTARI DASHA — alternative to Vimshottari
ASHTOTTARI_YEARS = {"Sun":6,"Moon":15,"Mars":8,"Mercury":17,"Saturn":10,"Jupiter":19,"Rahu":12,"Venus":21}
ASHTOTTARI_ORDER = ["Sun","Moon","Mars","Mercury","Saturn","Jupiter","Rahu","Venus"]
# Total: 108 years (vs Vimshottari's 120)

# YOGINI DASHA
YOGINI_NAMES = ["Mangala","Pingala","Dhanya","Bhramari","Bhadrika","Ulka","Siddha","Sankata"]
YOGINI_LORDS = ["Moon","Sun","Jupiter","Mars","Mercury","Saturn","Venus","Rahu"]
YOGINI_YEARS = [1, 2, 3, 4, 5, 6, 7, 8]
# Total: 36 years per cycle


def compute_ashtottari(natal_chart):
    """Compute Ashtottari MD timeline."""
    pos = natal_chart["positions"]
    moon = pos["Moon"]
    moon_lon = moon.get("lon_abs") or (moon["rasi_idx"] * 30 + moon["deg"])

    # Ashtottari starting lord based on Moon's nakshatra
    nak_idx = int(moon_lon / (360/27))
    # Standard mapping: Krittika=Sun, Rohini-Mrigashira=Moon, etc.
    # Using simplified mapping
    cycle_offset = nak_idx % 8
    starting_lord = ASHTOTTARI_ORDER[cycle_offset]

    # Remaining of starting MD = (1 - progress through nakshatra)
    progress = (moon_lon - nak_idx * (360/27)) / (360/27)
    starting_remaining = ASHTOTTARI_YEARS[starting_lord] * (1 - progress)

    b = natal_chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"], b["hour"], b["min"])

    timeline = []
    cur_lord = starting_lord
    cur_start = birth_dt
    cur_yrs = starting_remaining
    for _ in range(8):
        cur_end = cur_start + dt.timedelta(days=cur_yrs * 365.25)
        timeline.append({
            "lord": cur_lord,
            "start": cur_start,
            "end": cur_end,
            "years": round(cur_yrs, 1),
            "age_from": round((cur_start - birth_dt).days / 365.25, 1),
            "age_to": round((cur_end - birth_dt).days / 365.25, 1),
        })
        idx = (ASHTOTTARI_ORDER.index(cur_lord) + 1) % 8
        cur_lord = ASHTOTTARI_ORDER[idx]
        cur_start = cur_end
        cur_yrs = ASHTOTTARI_YEARS[cur_lord]
    return timeline


def compute_yogini(natal_chart):
    """Compute Yogini Dasha timeline."""
    pos = natal_chart["positions"]
    moon = pos["Moon"]
    moon_lon = moon.get("lon_abs") or (moon["rasi_idx"] * 30 + moon["deg"])

    nak_idx = int(moon_lon / (360/27))
    # Yogini cycle: starts based on nakshatra
    cycle_offset = nak_idx % 8
    progress = (moon_lon - nak_idx * (360/27)) / (360/27)

    starting_yog = YOGINI_NAMES[cycle_offset]
    starting_lord = YOGINI_LORDS[cycle_offset]
    starting_yrs = YOGINI_YEARS[cycle_offset]
    starting_remaining = starting_yrs * (1 - progress)

    b = natal_chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"])

    timeline = []
    cur_idx = cycle_offset
    cur_start = birth_dt
    cur_yrs = starting_remaining
    for _ in range(8):
        cur_end = cur_start + dt.timedelta(days=cur_yrs * 365.25)
        timeline.append({
            "yogini_name": YOGINI_NAMES[cur_idx],
            "lord": YOGINI_LORDS[cur_idx],
            "start": cur_start,
            "end": cur_end,
            "years": round(cur_yrs, 1),
            "age_from": round((cur_start - birth_dt).days / 365.25, 1),
            "age_to": round((cur_end - birth_dt).days / 365.25, 1),
        })
        cur_idx = (cur_idx + 1) % 8
        cur_start = cur_end
        cur_yrs = YOGINI_YEARS[cur_idx]
    return timeline


def all_dashas_summary(natal_chart):
    return {
        "ashtottari": compute_ashtottari(natal_chart),
        "yogini": compute_yogini(natal_chart),
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    print(f"=== ASHTOTTARI DASHA for {chart['name']} ===")
    for d in compute_ashtottari(chart):
        print(f"  {d['lord']:10s} {d['start'].strftime('%Y-%m-%d')} to {d['end'].strftime('%Y-%m-%d')} ({d['years']}y) ages {d['age_from']}-{d['age_to']}")

    print(f"\n=== YOGINI DASHA for {chart['name']} ===")
    for d in compute_yogini(chart):
        print(f"  {d['yogini_name']:10s} ({d['lord']}) {d['start'].strftime('%Y-%m-%d')} to {d['end'].strftime('%Y-%m-%d')} ({d['years']}y) ages {d['age_from']}-{d['age_to']}")
