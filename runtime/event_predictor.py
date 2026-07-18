"""Event Predictor — the integrator.

Combines: granular_dasha + transit_engine + event_yoga_detector
Output: timeline of probable life events with timing, severity, source, classical reasoning.

Each event = (date_range, event_type, severity, why_this_now, classical_source)
"""
import datetime as dt
import sys
sys.path.insert(0, ".")
from vedic_core import RASIS, RASI_LORDS, DIGNITIES


from granular_dasha import build_full_timeline, lookup
from transit_engine import detect_triggers, transit_positions
from event_yoga_detector import detect_all_yogas



# ================================================================
# EVENT PATTERN LIBRARY — each pattern fires when its conditions match
# ================================================================

def _planet_in_yoga_lords(planet, yoga):
    """Check if planet is mentioned in yoga's triggers."""
    return any(planet in t for t in yoga.get("triggers", []))


def event_father_accident(chart, dasha_state, transits, yogas):
    """Father accident/health-event pattern.

    Conditions:
      - Pitru-Kasht Yoga active (predisposition)
      - Either: dasha lord in 6/8/12 OR aspecting Sun
      - Either: transit Saturn near natal Saturn OR Saturn-Sun OR Mars-Sun trigger
      - Severity multiplied by yoga severity
    """
    pitru_yoga = next((y for y in yogas if y["name"] == "Pitru-Kasht Yoga"), None)
    if not pitru_yoga:
        return None

    pos = chart["positions"]
    score = 0
    why = []

    # Dasha trigger
    md_lord = dasha_state.get(1, {}).get("md")
    ad_lord = dasha_state.get(2, {}).get("ad")
    pd_lord = dasha_state.get(3, {}).get("pd")

    for label, lord in [("MD", md_lord), ("AD", ad_lord), ("PD", pd_lord)]:
        if lord and lord in pos:
            lh = pos[lord]["house"]
            if lh in [6, 8, 12]:
                score += 2
                why.append(f"{label} lord {lord} in dusthana (H{lh})")
            if lord in pitru_yoga["triggers"][0]:
                score += 1
                why.append(f"{label} activates Pitru-Kasht trigger")
        if lord == "Ketu" or lord == "Saturn":
            score += 1
            why.append(f"{label} = {lord} (malefic activator)")

    # Transit trigger
    saturn_return = next((t for t in transits if t["type"] == "saturn_return"), None)
    if saturn_return:
        score += 4
        why.append(f"Saturn Return on natal Saturn (orb {saturn_return['orb']}°) — VERY HIGH activator")

    sat_on_sun = next((t for t in transits if t["transit"] == "Saturn" and t["natal"] == "Sun"), None)
    if sat_on_sun:
        score += 3
        why.append(f"Transit Saturn on natal Sun")

    mars_on_sun = next((t for t in transits if t["transit"] == "Mars" and t["natal"] == "Sun"), None)
    if mars_on_sun:
        score += 2
        why.append(f"Transit Mars on natal Sun")

    # Score must be substantial to trigger
    if score < 5:
        return None

    final_severity = min(5, int(pitru_yoga["severity"] * 0.5 + score * 0.4))

    return {
        "event": "Father accident / health crisis / career setback",
        "category": "father",
        "severity": final_severity,
        "score_raw": score,
        "yoga_basis": pitru_yoga["name"],
        "why_this_now": why,
        "classical_source": "Pitru-Kasht Yoga (Jataka Parijata) + Saturn Return rule (Sarvarth Chintamani Ch. 9) + dasha-trigger logic (BPHS Ch. 47)",
        "advice": "Period of high vulnerability for the father figure. If the father is alive, this is a critical period for proactive health/career care. If event already occurred, this is the karmic activation date.",
    }


def event_mother_event(chart, dasha_state, transits, yogas):
    matr_yoga = next((y for y in yogas if y["name"] == "Matruhanta Yoga"), None)
    if not matr_yoga:
        return None
    pos = chart["positions"]
    score = 0
    why = []
    md_lord = dasha_state.get(1, {}).get("md")
    ad_lord = dasha_state.get(2, {}).get("ad")
    if md_lord == "Moon" or ad_lord == "Moon":
        score += 2
        why.append(f"Moon-period active")
    if md_lord and md_lord in pos and pos[md_lord]["house"] == 4:
        score += 2
        why.append(f"MD lord ({md_lord}) in 4H (mother's house)")
    sat_on_moon = next((t for t in transits if t["transit"] == "Saturn" and t["natal"] == "Moon"), None)
    sade = next((t for t in transits if t["type"] == "sade_sati"), None)
    if sat_on_moon:
        score += 3
        why.append("Transit Saturn on natal Moon")
    if sade:
        score += 2
        why.append(sade["label"])
    if score < 4:
        return None
    return {
        "event": "Mother health/wellbeing event",
        "category": "mother",
        "severity": min(5, int(matr_yoga["severity"] * 0.5 + score * 0.4)),
        "score_raw": score,
        "yoga_basis": matr_yoga["name"],
        "why_this_now": why,
        "classical_source": "Matruhanta Yoga (Jataka Parijata) + Sade Sati / Saturn-Moon triggers (BPHS, Sarvarth Chintamani)",
        "advice": "Active mother-related period. Health, emotional, or relationship events likely.",
    }


def event_accident(chart, dasha_state, transits, yogas):
    vid_yoga = next((y for y in yogas if y["name"] == "Vidyut Yoga"), None)
    pos = chart["positions"]
    score = 0
    why = []
    md_lord = dasha_state.get(1, {}).get("md")
    ad_lord = dasha_state.get(2, {}).get("ad")
    pd_lord = dasha_state.get(3, {}).get("pd")
    for label, lord in [("MD", md_lord), ("AD", ad_lord), ("PD", pd_lord)]:
        if lord in ["Mars", "Saturn", "Rahu", "Ketu"]:
            score += 1
            why.append(f"{label} = {lord} (sharp/malefic)")
    if vid_yoga:
        for label, lord in [("MD", md_lord), ("AD", ad_lord), ("PD", pd_lord)]:
            if lord in ["Mars", "Mercury"]:
                score += 2
                why.append(f"{label} ({lord}) activates Vidyut Yoga")
    mars_triggers = [t for t in transits if t["transit"] == "Mars" and t["severity"] in ["HIGH", "VERY HIGH"]]
    if mars_triggers:
        score += 2
        why.append(f"Transit Mars active: {mars_triggers[0]['label']}")
    if score < 4:
        return None
    return {
        "event": "Accident / injury / sudden physical event",
        "category": "self_or_family_accident",
        "severity": min(5, score // 2 + 1),
        "score_raw": score,
        "yoga_basis": vid_yoga["name"] if vid_yoga else None,
        "why_this_now": why,
        "classical_source": "Vidyut Yoga (Saravali) + Mars-Saturn dasha rules",
        "advice": "Caution with vehicles, sharp instruments, surgery, physical risk during this window.",
    }


def event_marriage(chart, dasha_state, transits, yogas):
    pos = chart["positions"]
    md = dasha_state.get(1, {}).get("md")
    ad = dasha_state.get(2, {}).get("ad")
    pd = dasha_state.get(3, {}).get("pd")
    score = 0
    why = []
    benefics = ["Venus", "Jupiter", "Moon", "Mercury"]
    if md in benefics:
        score += 2
        why.append(f"MD {md} is benefic (marriage-supporter)")
    if ad in benefics:
        score += 1
        why.append(f"AD {ad} is benefic")
    if pd in benefics:
        score += 1
        why.append(f"PD {pd} is benefic")
    h7_lord_planet = None
    lagna_idx = chart["lagna_idx"]
    
    
    h7_sign = RASIS[(lagna_idx + 6) % 12]
    h7_lord_planet = RASI_LORDS[h7_sign]
    if md == "Venus" or md == h7_lord_planet:
        score += 2
        why.append(f"MD activates marriage axis ({md})")
    if ad == "Venus" or ad == h7_lord_planet:
        score += 2
        why.append(f"AD activates marriage axis ({ad})")
    jup_friendly = next((t for t in transits if t["transit"] == "Jupiter" and t["natal"] in ["Venus","Moon"]), None)
    if jup_friendly:
        score += 1
        why.append(f"Jupiter aspect on Venus/Moon (auspicious)")
    if score < 4:
        return None
    return {
        "event": "Marriage / engagement / serious relationship",
        "category": "marriage",
        "severity": min(5, score // 2),
        "score_raw": score,
        "yoga_basis": None,
        "why_this_now": why,
        "classical_source": "Standard marriage timing rules (BPHS Ch. 80, Phaladeepika Ch. 17)",
        "advice": "Favourable marriage window. Strongest 2-3 month sub-windows within this period are best.",
    }


def event_career_breakthrough(chart, dasha_state, transits, yogas):
    raja = next((y for y in yogas if y["name"] == "Raja Yoga"), None)
    karya = next((y for y in yogas if y["name"] == "Karya-Siddhi Yoga"), None)
    pos = chart["positions"]
    md = dasha_state.get(1, {}).get("md")
    ad = dasha_state.get(2, {}).get("ad")
    score = 0
    why = []
    lagna_idx = chart["lagna_idx"]
    
    
    h10_lord = RASI_LORDS[RASIS[(lagna_idx + 9) % 12]]
    if md == h10_lord or ad == h10_lord:
        score += 3
        why.append(f"10th lord ({h10_lord}) active as MD/AD")
    if md == "Sun" or ad == "Sun":
        score += 2
        why.append(f"Sun period (authority/recognition)")
    if md == "Jupiter" or ad == "Jupiter":
        score += 2
        why.append(f"Jupiter period (expansion)")
    if raja:
        for lord_in_yoga in raja["triggers"][0].split():
            if lord_in_yoga in [md, ad]:
                score += 2
                why.append(f"Raja Yoga lord active")
                break
    jup_on_10 = next((t for t in transits if t["transit"] == "Jupiter" and t["natal"] == h10_lord), None)
    if jup_on_10:
        score += 2
        why.append("Jupiter transit favouring 10L")
    if score < 4:
        return None
    return {
        "event": "Career breakthrough / promotion / public recognition",
        "category": "career",
        "severity": min(5, score // 2),
        "score_raw": score,
        "yoga_basis": raja["name"] if raja else None,
        "why_this_now": why,
        "classical_source": "BPHS Ch. 80, Phaladeepika Ch. 16",
        "advice": "Push for visible achievements. Take career risks. Apply for senior roles.",
    }


# ================================================================
# MASTER EVENT SCANNER
# ================================================================

ALL_EVENT_PATTERNS = [
    event_father_accident,
    event_mother_event,
    event_accident,
    event_marriage,
    event_career_breakthrough,
]


def _age_at(d, chart):
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"])
    return (d - birth_dt).days / 365.25


# Age-based filters — events that only make sense at certain ages
AGE_FILTERS = {
    "Marriage / engagement / serious relationship": (18, 45),
    "Career breakthrough / promotion / public recognition": (20, 65),
    "Father accident / health crisis / career setback": (0, 80),
    "Mother health/wellbeing event": (0, 80),
    "Accident / injury / sudden physical event": (5, 80),
}

# Severity threshold — events below this are filtered as noise
SEVERITY_THRESHOLD = 4


def scan_year(chart, year, sample_days=7, min_severity=SEVERITY_THRESHOLD):
    """Scan a year, sampling every `sample_days` days. Return aggregated events."""
    timeline = build_full_timeline(chart, levels=3)
    yogas = detect_all_yogas(chart)
    events_by_window = {}

    d = dt.datetime(year, 1, 1)
    end = dt.datetime(year, 12, 31)
    while d <= end:
        age = _age_at(d, chart)
        dasha_state = lookup(timeline, d)
        transits = detect_triggers(chart, d, orb=3.0)
        for pattern_fn in ALL_EVENT_PATTERNS:
            event = pattern_fn(chart, dasha_state, transits, yogas)
            if event:
                # Severity threshold
                if event["severity"] < min_severity:
                    continue
                # Age filter
                age_min, age_max = AGE_FILTERS.get(event["event"], (0, 100))
                if age < age_min or age > age_max:
                    continue
                key = event["event"]
                if key not in events_by_window:
                    events_by_window[key] = {
                        **event,
                        "first_seen": d,
                        "last_seen": d,
                        "max_severity": event["severity"],
                        "max_score": event["score_raw"],
                        "max_why": event["why_this_now"],
                        "age_at_first": age,
                    }
                else:
                    events_by_window[key]["last_seen"] = d
                    if event["severity"] > events_by_window[key]["max_severity"]:
                        events_by_window[key]["max_severity"] = event["severity"]
                        events_by_window[key]["max_score"] = event["score_raw"]
                        events_by_window[key]["max_why"] = event["why_this_now"]
        d += dt.timedelta(days=sample_days)
    return events_by_window


def scan_lifetime(chart, year_from=None, year_to=None, sample_days=14):
    """Scan a range of years. Default: full 80-year horizon from birth."""
    b = chart["birth"]
    if year_from is None:
        year_from = b["year"]
    if year_to is None:
        year_to = b["year"] + 80
    all_events = []
    for year in range(year_from, year_to + 1):
        year_events = scan_year(chart, year, sample_days=sample_days)
        for key, ev in year_events.items():
            ev["year"] = year
            all_events.append(ev)
    return all_events


if __name__ == "__main__":
    import json, sys
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))

    # Validation: scan birth year 1996
    print("=" * 70)
    print("VALIDATION TEST: Scan Manoj's birth year 1996")
    print("=" * 70)
    events_1996 = scan_year(chart, 1996, sample_days=3)
    if not events_1996:
        print("NO EVENTS DETECTED — engine missed it!")
    else:
        for key, ev in sorted(events_1996.items(), key=lambda kv: -kv[1]["max_severity"]):
            print(f"\n[{ev['max_severity']}/5] {ev['event']}")
            print(f"  Active window: {ev['first_seen'].date()} -> {ev['last_seen'].date()}")
            print(f"  Yoga: {ev.get('yoga_basis', 'n/a')}")
            print(f"  Why: ")
            for w in ev["max_why"]:
                print(f"    * {w}")
            print(f"  Source: {ev['classical_source']}")
