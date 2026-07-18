"""Prashna (Horary) — Question chart system.

Source: Prashna Marga, KP Reader Vol 6 (KP horary), classical Prashna texts.
Cast a chart at the moment a question is asked, then read the answer.
"""
import sys, datetime as dt
sys.path.insert(0, ".")
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)

from vedic_core import RASIS, RASI_LORDS  # canonical 12 signs + lords

# Houses for question types
QUESTION_HOUSES = {
    "marriage": 7,
    "career": 10,
    "money": 2,
    "loan": 6,
    "health": 1,
    "disease": 6,
    "court_case": 6,
    "child": 5,
    "education": 4,
    "travel": 9,
    "foreign": 12,
    "property": 4,
    "vehicle": 4,
    "spouse": 7,
    "partner": 7,
    "enemy": 6,
    "death": 8,
    "longevity": 8,
    "spiritual": 12,
    "father": 9,
    "mother": 4,
    "sibling": 3,
    "younger_sibling": 3,
    "elder_sibling": 11,
    "gain": 11,
    "wishes": 11,
}


def cast_prashna_chart(question_dt, lat, lon):
    """Cast a chart at the moment of asking. Returns chart dict."""
    h = question_dt.hour + question_dt.minute / 60.0
    jd = swe.julday(question_dt.year, question_dt.month, question_dt.day, h, swe.GREG_CAL)
    flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    # Houses (Placidus)
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flag)
    asc_lon = ascmc[0] % 360
    lagna_idx = int(asc_lon / 30)

    PLANETS = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
               "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN,"Rahu":swe.MEAN_NODE}
    pos = {}
    for name, pid in PLANETS.items():
        x, _ = swe.calc_ut(jd, pid, flag)
        plon = x[0] % 360
        ri = int(plon / 30)
        pos[name] = {"lon":plon,"rasi":RASIS[ri],"rasi_idx":ri,"deg":plon-ri*30,
                      "house":((ri - lagna_idx) % 12) + 1}
    rahu_lon = pos["Rahu"]["lon"]
    ketu_lon = (rahu_lon + 180) % 360
    ki = int(ketu_lon / 30)
    pos["Ketu"] = {"lon":ketu_lon,"rasi":RASIS[ki],"rasi_idx":ki,"deg":ketu_lon-ki*30,
                    "house":((ki - lagna_idx) % 12) + 1}

    return {
        "type": "Prashna chart",
        "datetime": question_dt.strftime("%Y-%m-%d %H:%M"),
        "lat": lat,
        "lon": lon,
        "lagna": RASIS[lagna_idx],
        "lagna_idx": lagna_idx,
        "lagna_lord": RASI_LORDS[RASIS[lagna_idx]],
        "asc_degree": asc_lon - lagna_idx * 30,
        "positions": pos,
    }


def answer_prashna(prashna_chart, question_type, simple=True):
    """Read the prashna chart for the answer.

    Basic Prashna rules:
      1. Identify the question's house (e.g., marriage = 7H)
      2. Examine the lord of that house — strong & in benefic house = YES
      3. Examine the question's house occupants — benefics = YES, malefics = NO
      4. Examine Moon's relationship to the question house
    """
    q_house = QUESTION_HOUSES.get(question_type)
    if not q_house:
        return {"error": f"Unknown question type: {question_type}"}

    pos = prashna_chart["positions"]
    lagna_idx = prashna_chart["lagna_idx"]
    q_sign = RASIS[(lagna_idx + q_house - 1) % 12]
    q_lord = RASI_LORDS[q_sign]

    score = 0
    reasoning = []

    # Question lord placement
    if q_lord in pos:
        ql_h = pos[q_lord]["house"]
        if ql_h in [1, 4, 5, 9, 10, 11]:
            score += 2
            reasoning.append(f"Question lord {q_lord} in good house {ql_h} (+2)")
        elif ql_h in [6, 8, 12]:
            score -= 2
            reasoning.append(f"Question lord {q_lord} in dusthana {ql_h} (-2)")

    # Question house occupants
    occupants = [p for p, pd in pos.items() if pd["house"] == q_house]
    BENEFICS = ["Moon","Mercury","Jupiter","Venus"]
    MALEFICS = ["Sun","Mars","Saturn","Rahu","Ketu"]
    benefics_in_q = [p for p in occupants if p in BENEFICS]
    malefics_in_q = [p for p in occupants if p in MALEFICS]
    if benefics_in_q:
        score += 1
        reasoning.append(f"Benefics ({', '.join(benefics_in_q)}) in question house (+1)")
    if malefics_in_q:
        score -= 1
        reasoning.append(f"Malefics ({', '.join(malefics_in_q)}) in question house (-1)")

    # Moon's connection
    moon_h = pos["Moon"]["house"]
    if moon_h == q_house:
        score += 2
        reasoning.append(f"Moon in question house (+2)")
    elif moon_h in [1, 4, 7, 10]:
        score += 1
        reasoning.append(f"Moon in kendra (+1)")

    # Lagna lord
    al = prashna_chart["lagna_lord"]
    if al in pos:
        al_h = pos[al]["house"]
        if al_h in [1, 4, 5, 7, 9, 10]:
            score += 1
            reasoning.append(f"Lagna lord {al} strong in {al_h}H (+1)")

    # Verdict
    if score >= 4: verdict = "YES — strongly favorable"
    elif score >= 2: verdict = "YES — favorable"
    elif score >= 0: verdict = "MAYBE — uncertain, watch obstacles"
    elif score >= -2: verdict = "NO — unfavorable"
    else: verdict = "NO — strongly unfavorable"

    return {
        "question_type": question_type,
        "question_house": q_house,
        "question_lord": q_lord,
        "score": score,
        "verdict": verdict,
        "reasoning": reasoning,
    }


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    now = dt.datetime.now()
    chart = cast_prashna_chart(now, 11.01, 76.57)  # Coimbatore
    print(f"=== PRASHNA CHART CAST AT {chart['datetime']} ===")
    print(f"  Lagna: {chart['lagna']} ({chart['asc_degree']:.2f}° in sign)")
    print(f"  Lagna Lord: {chart['lagna_lord']}")
    print()
    print("=== ANSWERS ===")
    for q in ["marriage", "career", "money", "travel"]:
        ans = answer_prashna(chart, q)
        print(f"\n  Q: {q.upper()}")
        print(f"    Verdict: {ans['verdict']} (score: {ans['score']})")
        for r in ans["reasoning"]:
            print(f"    - {r}")
