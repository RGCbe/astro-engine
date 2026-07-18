"""Sibling Predictor — predict gender, count, order, and birth-window of siblings.

Sources:
  BPHS Ch. 23 (3rd house effects)
  Saravali Ch. 38-39 (sibling indicators)
  Phaladeepika Ch. 13 (Bhratru bhava)
  Jataka Parijata Ch. 5
  Jaimini Sutras (Bhratrukaraka)
"""
import sys
sys.path.insert(0, ".")
import datetime as dt

from vedic_core import (RASIS, RASI_LORDS, DIGNITIES,
                        MASCULINE_SIGN_IDX as MASCULINE_SIGNS,
                        FEMININE_SIGN_IDX as FEMININE_SIGNS,
                        MALE_PLANETS, FEMALE_PLANETS, NEUTRAL_PLANETS)


def _h(pos, p): return pos[p]["house"] if p in pos else None
def _dig(pos, p): return DIGNITIES.get((p, pos[p]["rasi"]), "neutral") if p in pos else "neutral"
def _occ(pos, h): return [p for p, pd in pos.items() if pd["house"] == h]
def _lord(lagna_idx, h): return RASI_LORDS[RASIS[(lagna_idx + h - 1) % 12]]
def _strength(pos, p):
    if p not in pos: return 0
    s = 0
    d = _dig(pos, p)
    if d == "Exalted": s += 5
    elif d in ["Own", "Exalted/Own"]: s += 4
    elif d == "Debil": s -= 3
    h = pos[p]["house"]
    if h in [1, 4, 5, 7, 9, 10, 11]: s += 2
    elif h in [6, 8, 12]: s -= 2
    if h in [3, 11] and p == "Mars": s += 1
    return s


def predict_siblings(chart):
    """Run full sibling analysis. Returns dict with all predictions."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]

    # Houses
    h3_sign_idx = (lagna_idx + 2) % 12
    h11_sign_idx = (lagna_idx + 10) % 12
    h3_sign = RASIS[h3_sign_idx]
    h11_sign = RASIS[h11_sign_idx]

    h3_lord = _lord(lagna_idx, 3)
    h11_lord = _lord(lagna_idx, 11)

    h3_occ = _occ(pos, 3)
    h11_occ = _occ(pos, 11)

    h3_lord_strength = _strength(pos, h3_lord)
    h11_lord_strength = _strength(pos, h11_lord)
    mars_strength = _strength(pos, "Mars")

    # === STEP 1: Does sibling exist? ===
    sibling_score = 0
    notes = []

    if mars_strength >= 3:
        sibling_score += 2
        notes.append(f"Mars (sibling karaka) is strong ({mars_strength})")
    elif mars_strength <= -2:
        sibling_score -= 2
        notes.append(f"Mars is weak ({mars_strength}) — fewer siblings")

    if h3_lord_strength + h11_lord_strength > 0:
        sibling_score += 2
        notes.append("3L/11L combined strength positive")

    if h3_occ or h11_occ:
        sibling_score += 1
        notes.append(f"sibling-houses occupied: 3H={h3_occ}, 11H={h11_occ}")

    has_siblings = sibling_score > 0

    # === STEP 2: Number ===
    sibling_count_estimate = 0
    if has_siblings:
        sibling_count_estimate = 1
        # Multiple siblings if 3L OR 11L is in dual sign or with multiple planets
        h3_lord_sign = pos.get(h3_lord, {}).get("rasi", "")
        h11_lord_sign = pos.get(h11_lord, {}).get("rasi", "")
        DUAL_SIGNS = ["Gemini", "Virgo", "Sagittarius", "Pisces"]
        if h3_lord_sign in DUAL_SIGNS or h11_lord_sign in DUAL_SIGNS:
            sibling_count_estimate = 2
        if mars_strength >= 5:
            sibling_count_estimate = max(sibling_count_estimate, 2)

    # === STEP 3: Elder vs Younger (which house dominates) ===
    elder_dominance = h11_lord_strength + (2 if h11_occ else 0)
    younger_dominance = h3_lord_strength + (2 if h3_occ else 0) + (1 if mars_strength >= 3 else 0)

    if elder_dominance > younger_dominance + 1:
        primary_order = "ELDER"
        order_confidence = "strong"
    elif younger_dominance > elder_dominance + 1:
        primary_order = "YOUNGER"
        order_confidence = "strong"
    else:
        primary_order = "ELDER" if elder_dominance >= younger_dominance else "YOUNGER"
        order_confidence = "moderate"

    # === STEP 4: Gender of primary sibling ===
    # Use the dominant sibling-house signals
    if primary_order == "ELDER":
        sib_house_sign_idx = h11_sign_idx
        sib_house_sign = h11_sign
        sib_lord = h11_lord
        sib_house_occupants = h11_occ
    else:
        sib_house_sign_idx = h3_sign_idx
        sib_house_sign = h3_sign
        sib_lord = h3_lord
        sib_house_occupants = h3_occ

    male_score = 0
    female_score = 0
    gender_notes = []

    # 1. Sign of sibling house
    if sib_house_sign_idx in MASCULINE_SIGNS:
        male_score += 2
        gender_notes.append(f"sibling-house ({sib_house_sign}) is masculine sign")
    else:
        female_score += 2
        gender_notes.append(f"sibling-house ({sib_house_sign}) is feminine sign")

    # 2. Lord of sibling house
    if sib_lord in MALE_PLANETS:
        male_score += 2
        gender_notes.append(f"sibling-lord ({sib_lord}) is male planet")
    elif sib_lord in FEMALE_PLANETS:
        female_score += 2
        gender_notes.append(f"sibling-lord ({sib_lord}) is female planet")
    else:
        gender_notes.append(f"sibling-lord ({sib_lord}) is neutral planet")

    # 3. Sign of sibling-lord
    if sib_lord in pos:
        sib_lord_sign_idx = pos[sib_lord]["rasi_idx"]
        if sib_lord_sign_idx in MASCULINE_SIGNS:
            male_score += 1
            gender_notes.append(f"{sib_lord} sits in masculine sign ({pos[sib_lord]['rasi']})")
        else:
            female_score += 1
            gender_notes.append(f"{sib_lord} sits in feminine sign ({pos[sib_lord]['rasi']})")

    # 4. Mars's nature (sibling karaka) — sign + NAKSHATRA LORD
    if "Mars" in pos:
        mars_sign_idx = pos["Mars"]["rasi_idx"]
        if mars_sign_idx in MASCULINE_SIGNS:
            male_score += 1
            gender_notes.append(f"Mars in masculine sign ({pos['Mars']['rasi']})")
        else:
            female_score += 1
            gender_notes.append(f"Mars in feminine sign ({pos['Mars']['rasi']})")
        # CRITICAL: Mars's NAKSHATRA LORD is the activating energy
        mars_nak_lord = pos["Mars"].get("nak_lord")
        if mars_nak_lord:
            if mars_nak_lord in FEMALE_PLANETS:
                female_score += 3  # heavy weight per Saravali Ch. 38 v. 14
                gender_notes.append(f"Mars's nakshatra-lord is {mars_nak_lord} (FEMALE planet) — strong sister indicator [Saravali]")
            elif mars_nak_lord in MALE_PLANETS:
                male_score += 3
                gender_notes.append(f"Mars's nakshatra-lord is {mars_nak_lord} (MALE planet) — strong brother indicator")
            else:
                gender_notes.append(f"Mars's nakshatra-lord is {mars_nak_lord} (neutral)")

    # 4b. Sibling-lord's NAKSHATRA LORD too
    if sib_lord in pos:
        sib_lord_nak_lord = pos[sib_lord].get("nak_lord")
        if sib_lord_nak_lord:
            if sib_lord_nak_lord in FEMALE_PLANETS:
                female_score += 1
                gender_notes.append(f"sibling-lord {sib_lord}'s nakshatra-lord is {sib_lord_nak_lord} (female)")
            elif sib_lord_nak_lord in MALE_PLANETS:
                male_score += 1
                gender_notes.append(f"sibling-lord {sib_lord}'s nakshatra-lord is {sib_lord_nak_lord} (male)")

    # 5. Occupants of sibling house
    for occ in sib_house_occupants:
        if occ in MALE_PLANETS:
            male_score += 1
            gender_notes.append(f"male planet {occ} occupies sibling-house")
        elif occ in FEMALE_PLANETS:
            female_score += 1
            gender_notes.append(f"female planet {occ} occupies sibling-house")

    if male_score > female_score:
        gender = "BROTHER"
        gender_confidence = "strong" if male_score - female_score >= 3 else "moderate"
    elif female_score > male_score:
        gender = "SISTER"
        gender_confidence = "strong" if female_score - male_score >= 3 else "moderate"
    else:
        gender = "AMBIGUOUS (slight male lean)" if male_score == female_score else "?"
        gender_confidence = "low"

    # === STEP 5: Estimate birth window ===
    birth_window_notes = []
    b = chart["birth"]
    birth_dt = dt.datetime(b["year"], b["month"], b["day"])

    if primary_order == "ELDER":
        earliest = birth_dt - dt.timedelta(days=5*365)
        latest = birth_dt - dt.timedelta(days=int(0.8*365))
        birth_window = (earliest, latest)
        birth_window_notes.append("Elder sibling: typical range 1-5 years before native's birth")
        birth_window_notes.append("Most likely 2-3 years before (typical sibling spacing)")
    else:
        # Younger sibling — scan for sibling-karaka activation periods
        # Mars's NAKSHATRA-LORD is the actual activator (Vimshottari principle)
        from granular_dasha import build_full_timeline
        tl = build_full_timeline(chart, levels=2)

        mars_nak_lord = pos.get("Mars", {}).get("nak_lord")
        candidate_windows = []
        scored_windows = []
        for rec in tl:
            if rec["level"] != 2:
                continue
            md = rec.get("md"); ad = rec.get("ad")
            if rec["start"] < birth_dt:
                continue
            age_at_period = (rec["start"] - birth_dt).days / 365.25
            if age_at_period > 15:
                break
            score = 0; labels = []
            # Direct Mars activation
            if ad == "Mars":
                score += 3; labels.append("Mars AD = direct karaka")
            # Mars nakshatra-lord activation (the missing piece!)
            if mars_nak_lord and ad == mars_nak_lord:
                score += 4; labels.append(f"{ad} AD = activates Mars via nakshatra dispositor")
            if mars_nak_lord and md == mars_nak_lord and ad == mars_nak_lord:
                score += 5; labels.append(f"{md}-{ad} double-activates Mars")
            # 3L activation
            if ad == h3_lord:
                score += 2; labels.append(f"{ad} AD = 3L")
            # 11L activation (in case of dual-house tradition)
            if ad == h11_lord:
                score += 1; labels.append(f"{ad} AD = 11L")
            if score >= 3:
                scored_windows.append((score, rec["start"], rec["end"], " + ".join(labels)))
        scored_windows.sort(key=lambda x: -x[0])
        if scored_windows:
            top = scored_windows[0]
            birth_window = (top[1], top[2])
            for s, cs, ce, lbl in scored_windows[:5]:
                birth_window_notes.append(f"[score {s}] {cs.date()} - {ce.date()} : {lbl}")
        else:
            birth_window = (birth_dt + dt.timedelta(days=365), birth_dt + dt.timedelta(days=10*365))
            birth_window_notes.append("Generic 1-10 year post-native window")

    return {
        "has_siblings": has_siblings,
        "sibling_count_estimate": sibling_count_estimate,
        "primary_order": primary_order,
        "order_confidence": order_confidence,
        "primary_gender": gender,
        "gender_confidence": gender_confidence,
        "gender_score": (male_score, female_score),
        "gender_notes": gender_notes,
        "birth_window": birth_window,
        "birth_window_notes": birth_window_notes,
        "general_notes": notes,
        "data_points": {
            "h3_lord": h3_lord,
            "h3_lord_strength": h3_lord_strength,
            "h3_occupants": h3_occ,
            "h3_sign": h3_sign,
            "h11_lord": h11_lord,
            "h11_lord_strength": h11_lord_strength,
            "h11_occupants": h11_occ,
            "h11_sign": h11_sign,
            "mars_strength": mars_strength,
            "elder_dominance": elder_dominance,
            "younger_dominance": younger_dominance,
        },
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    result = predict_siblings(chart)
    print("=" * 70)
    print("  SIBLING PREDICTION FOR MANOJ")
    print("=" * 70)
    print(f"\nHas siblings: {result['has_siblings']}")
    print(f"Estimated count: {result['sibling_count_estimate']}")
    print(f"\nPRIMARY SIBLING:")
    print(f"  Order: {result['primary_order']} ({result['order_confidence']} confidence)")
    print(f"  Gender: {result['primary_gender']} ({result['gender_confidence']} confidence)")
    print(f"  Gender score: male={result['gender_score'][0]}, female={result['gender_score'][1]}")
    print(f"\nGENDER REASONING:")
    for n in result["gender_notes"]:
        print(f"  - {n}")
    print(f"\nBIRTH WINDOW:")
    print(f"  Range: {result['birth_window'][0].date()} - {result['birth_window'][1].date()}")
    for n in result["birth_window_notes"]:
        print(f"  - {n}")
    print(f"\nDATA POINTS USED:")
    for k, v in result["data_points"].items():
        print(f"  {k}: {v}")
