"""Muhurta Extended — 14 specialized muhurta types for life events.

Source: Muhurta Chintamani by Ramacharya, Muhurta Ganapati, Phaladeepika Ch. 26.
Each function takes (chart, target_date, **kwargs) and returns:
    {
      "verdict": "AUSPICIOUS" | "NOT IDEAL" | "AVOID",
      "score": 0-100,
      "reasons_supportive": [...],
      "reasons_against": [...],
      "panchanga": {...},
      "better_dates": [{"date": ..., "score": ...}, ...]
    }

Each muhurta type has its own classical rules for:
  - Suitable tithi (lunar day)
  - Suitable nakshatra
  - Suitable vara (weekday)
  - Suitable karana (half-tithi)
  - Sometimes: lagna constraints + transit constraints

14 types implemented:
  1.  gemstone        (ratna-dharana / first wearing)
  2.  griha-pravesh   (house-warming, entering new home)
  3.  garbhadhana     (conception)
  4.  namakarana      (naming, day 11/12 after birth)
  5.  upanayana       (sacred-thread initiation)
  6.  annaprashana    (first feeding, month 6-8)
  7.  chudakarana     (first haircut, age 1-3)
  8.  vidyarambha     (education start, age 5-7)
  9.  vahana          (vehicle purchase / new ride)
  10. bhumi           (land / property purchase)
  11. vyavahara       (court case / litigation)
  12. rajyabhisheka   (coronation / new role / promotion ceremony)
  13. rina            (loan-taking / borrowing money)
  14. dahana          (funeral / cremation timing)
"""
import sys, datetime as dt
sys.path.insert(0, ".")
from vedic_core import RASIS, RASI_LORDS, NAKSHATRAS
from panchanga import compute_panchanga, TITHIS, VARAS, KARANAS
from muhurta_engine import tara_bala, chandra_bala, TARA_GOOD


# ============================================================
# GENERIC HELPERS
# ============================================================
SHUBHA_NAKSHATRAS_ALL_PURPOSE = [
    "Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Chitra",
    "Swati", "Anuradha", "Uttara Ashadha", "Shravana", "Dhanishta", "Revati",
    "Uttara Phalguni", "Uttara Bhadrapada",
]
RIKTA_TITHIS = [4, 9, 14]  # 14 also includes Chaturdashi
NANDA_TITHIS = [1, 6, 11]  # Pratipada, Shashthi, Ekadashi — joyful
BHADRA_TITHIS = [2, 7, 12]  # Dwitiya, Saptami, Dwadashi — supportive
JAYA_TITHIS = [3, 8, 13]  # Tritiya, Ashtami, Trayodashi — victorious
PURNA_TITHIS = [5, 10, 15]  # Panchami, Dashami, Purnima — full

VAR_FOR_PUJA = ["Monday", "Wednesday", "Thursday", "Friday"]
VAR_FOR_AGGRESSIVE = ["Tuesday", "Saturday"]


def _verdict(score):
    if score >= 75: return "AUSPICIOUS"
    if score >= 55: return "ACCEPTABLE"
    if score >= 35: return "NOT IDEAL"
    return "AVOID"


def _base_score(pan, chart):
    """Generic positive/negative base assessment from panchanga + tara/chandra."""
    score = 50
    pos, neg = [], []

    # Tithi scoring
    t = pan["tithi_number"]
    if t in NANDA_TITHIS + BHADRA_TITHIS + JAYA_TITHIS + PURNA_TITHIS:
        score += 8
        pos.append(f"Auspicious tithi ({pan['tithi']})")
    if t in RIKTA_TITHIS:
        score -= 12
        neg.append(f"Rikta tithi ({pan['tithi']}) — empty/loss energy")
    if pan.get("tithi_number") == 30 or pan.get("tithi") == "Amavasya":
        score -= 18
        neg.append("Amavasya — generally inauspicious")

    # Karana — Bhadra is the 7th karana ("Vishti(Bhadra)")
    if pan.get("karana") == "Vishti(Bhadra)":
        score -= 15
        neg.append("Bhadra Karana (Vishti) — avoid important work")

    # Nakshatra
    if pan["nakshatra"] in SHUBHA_NAKSHATRAS_ALL_PURPOSE:
        score += 12
        pos.append(f"Shubha nakshatra ({pan['nakshatra']})")

    # Tara + Chandra
    natal_nak = chart.get("janma_nakshatra")
    natal_moon = chart.get("moon_rasi")
    when_dt = pan.get("_when_dt")
    if when_dt is None:
        when_dt = dt.datetime.now()
    tara = tara_bala(natal_nak, when_dt)
    if tara:
        if tara["is_good"]:
            score += 10
            pos.append(f"Tara: {tara['type']}")
        else:
            score -= 10
            neg.append(f"Tara: {tara['type']}")
    cb = chandra_bala(natal_moon, when_dt)
    if cb:
        if cb["is_good"]:
            score += 8
            pos.append(f"Chandra Bala: {cb['verdict']}")
        elif cb["is_bad"]:
            score -= 8
            neg.append(f"Chandra Bala: {cb['verdict']}")

    return score, pos, neg


def _wrap(chart, target_dt, score, pos, neg, pan, event_name, find_better=True):
    """Build standard return shape with optional better-dates."""
    result = {
        "event": event_name,
        "date": target_dt.strftime("%Y-%m-%d %H:%M"),
        "verdict": _verdict(score),
        "score": max(0, min(100, score)),
        "reasons_supportive": pos,
        "reasons_against": neg,
        "panchanga": {
            "tithi": pan["tithi"],
            "vara": pan["vara"],
            "nakshatra": pan["nakshatra"],
            "yoga": pan.get("yoga", ""),
        },
    }
    if find_better and result["verdict"] in ("NOT IDEAL", "AVOID"):
        better = []
        for offset in range(1, 31):
            cand_dt = target_dt + dt.timedelta(days=offset)
            cand_score = _quick_score(chart, cand_dt, event_name)
            if cand_score >= 65:
                better.append({"date": cand_dt.strftime("%Y-%m-%d (%a)"), "score": cand_score})
            if len(better) >= 5: break
        result["better_dates"] = better
    return result


def _quick_score(chart, target_dt, event_name):
    """Re-run target event-fn and return score only."""
    fn_map = {
        "gemstone": compute_gemstone_muhurta,
        "griha-pravesh": compute_griha_pravesh_muhurta,
        "garbhadhana": compute_garbhadhana_muhurta,
        "namakarana": compute_namakarana_muhurta,
        "upanayana": compute_upanayana_muhurta,
        "annaprashana": compute_annaprashana_muhurta,
        "chudakarana": compute_chudakarana_muhurta,
        "vidyarambha": compute_vidyarambha_muhurta,
        "vahana": compute_vahana_muhurta,
        "bhumi": compute_bhumi_muhurta,
        "vyavahara": compute_vyavahara_muhurta,
        "rajyabhisheka": compute_rajyabhisheka_muhurta,
        "rina": compute_rina_muhurta,
        "dahana": compute_dahana_muhurta,
    }
    fn = fn_map.get(event_name)
    if not fn: return 0
    res = fn(chart, target_dt, _suppress_better=True)
    return res["score"]


# ============================================================
# 1. GEMSTONE (Ratna-Dharana)
# ============================================================
def compute_gemstone_muhurta(chart, target_dt, _suppress_better=False):
    """First-wearing of gemstone. Best: Shukla paksha, Hora of relevant planet, Shubha nakshatra."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    # Specific rules
    if pan.get("paksha") == "Shukla":
        score += 8; pos.append("Shukla paksha (waxing) preferred for gem-wearing")
    else:
        score -= 5; neg.append("Krishna paksha — generally avoid for gem")
    if pan["vara"] == "Sunday" and pan["nakshatra"] in ["Pushya","Uttara Phalguni","Uttara Ashadha"]:
        score += 12; pos.append("Sun-day + uttara nakshatra perfect for ruby/gold")
    if pan["nakshatra"] == "Pushya":
        score += 15; pos.append("Pushya — universal supreme nakshatra for gem-wearing")
    return _wrap(chart, target_dt, score, pos, neg, pan, "gemstone", not _suppress_better)


# ============================================================
# 2. GRIHA-PRAVESH (House-warming)
# ============================================================
def compute_griha_pravesh_muhurta(chart, target_dt, _suppress_better=False):
    """Entering new home. Best: Pushya/Hasta/Anuradha; avoid Tuesday."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    if pan["vara"] == "Tuesday":
        score -= 15; neg.append("Tuesday — Mars-ruled, avoid for griha-pravesh")
    if pan["vara"] in ["Monday","Wednesday","Thursday","Friday"]:
        score += 5; pos.append("Auspicious weekday for entering home")
    GP_GOOD_NAK = ["Rohini","Mrigashira","Pushya","Anuradha","Hasta","Uttara Phalguni","Uttara Ashadha","Uttara Bhadrapada"]
    if pan["nakshatra"] in GP_GOOD_NAK:
        score += 12; pos.append(f"Excellent nakshatra ({pan['nakshatra']}) for new-home entry")
    if pan["tithi_number"] in [4, 9, 14, 30]:
        score -= 10; neg.append("Avoid 4/9/14/Amavasya for entering new home")
    return _wrap(chart, target_dt, score, pos, neg, pan, "griha-pravesh", not _suppress_better)


# ============================================================
# 3. GARBHADHANA (Conception)
# ============================================================
def compute_garbhadhana_muhurta(chart, target_dt, _suppress_better=False):
    """Sankhya/Shastra timing for conception. Avoid certain tithis + nakshatras."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    GARB_GOOD = ["Rohini","Mrigashira","Anuradha","Swati","Hasta","Pushya","Uttara Phalguni","Uttara Ashadha","Uttara Bhadrapada","Revati","Shravana","Dhanishta"]
    GARB_BAD = ["Bharani","Krittika","Ardra","Ashlesha","Magha","Mula","Jyeshtha","Vishakha"]
    if pan["nakshatra"] in GARB_GOOD:
        score += 14; pos.append(f"Auspicious nakshatra ({pan['nakshatra']}) for conception")
    if pan["nakshatra"] in GARB_BAD:
        score -= 18; neg.append(f"Avoid {pan['nakshatra']} for conception")
    if pan["tithi_number"] in [1, 11, 13, 14, 15, 30]:
        score -= 10; neg.append(f"Avoid tithi {pan['tithi']} for garbhadhana")
    if pan["vara"] == "Tuesday":
        score -= 8; neg.append("Tuesday — Mars day, less ideal")
    return _wrap(chart, target_dt, score, pos, neg, pan, "garbhadhana", not _suppress_better)


# ============================================================
# 4. NAMAKARANA (Naming, day 11/12 after birth)
# ============================================================
def compute_namakarana_muhurta(chart, target_dt, _suppress_better=False):
    """Naming ceremony — usually day 11 or 12 from birth. Janma nakshatra not allowed."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    janma_nak = chart.get("janma_nakshatra")
    if pan["nakshatra"] == janma_nak:
        score -= 20; neg.append(f"Avoid Janma nakshatra ({janma_nak}) for namakarana")
    if pan["vara"] in ["Monday","Wednesday","Thursday","Friday"]:
        score += 6; pos.append("Auspicious weekday")
    if pan["nakshatra"] in SHUBHA_NAKSHATRAS_ALL_PURPOSE:
        score += 10; pos.append(f"Shubha nakshatra ({pan['nakshatra']})")
    if pan["tithi_number"] in RIKTA_TITHIS:
        score -= 8; neg.append("Rikta tithi — avoid")
    return _wrap(chart, target_dt, score, pos, neg, pan, "namakarana", not _suppress_better)


# ============================================================
# 5. UPANAYANA (Sacred-thread)
# ============================================================
def compute_upanayana_muhurta(chart, target_dt, _suppress_better=False):
    """Sacred thread initiation. Day-time, Uttarayana preferred."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    UP_GOOD_NAK = ["Hasta","Chitra","Swati","Punarvasu","Pushya","Shravana","Dhanishta","Revati"]
    if pan["nakshatra"] in UP_GOOD_NAK:
        score += 14; pos.append(f"Excellent ({pan['nakshatra']}) for upanayana")
    if pan["vara"] == "Saturday":
        score -= 10; neg.append("Saturn-day not ideal for thread ceremony")
    # Best months: Magha-Shravana (uttarayana)
    if target_dt.month in [1, 2, 3, 4, 5, 6]:
        score += 5; pos.append("Uttarayana (Jan-Jun) — auspicious sun-period")
    return _wrap(chart, target_dt, score, pos, neg, pan, "upanayana", not _suppress_better)


# ============================================================
# 6. ANNAPRASHANA (First feeding)
# ============================================================
def compute_annaprashana_muhurta(chart, target_dt, _suppress_better=False):
    """First solid feeding, around month 6-8 after birth."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    if pan["nakshatra"] in ["Rohini","Mrigashira","Punarvasu","Pushya","Hasta","Chitra","Anuradha","Shravana","Revati"]:
        score += 14; pos.append(f"Auspicious ({pan['nakshatra']}) for first feeding")
    if pan["tithi_number"] in NANDA_TITHIS + BHADRA_TITHIS + JAYA_TITHIS:
        score += 6; pos.append("Auspicious tithi")
    if pan["vara"] == "Tuesday":
        score -= 8; neg.append("Tuesday — avoid for child rite")
    return _wrap(chart, target_dt, score, pos, neg, pan, "annaprashana", not _suppress_better)


# ============================================================
# 7. CHUDAKARANA (First haircut)
# ============================================================
def compute_chudakarana_muhurta(chart, target_dt, _suppress_better=False):
    """First haircut/tonsure, age 1-3."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    CHUD_GOOD_NAK = ["Hasta","Chitra","Swati","Pushya","Punarvasu","Mrigashira","Revati","Jyeshtha","Shravana"]
    if pan["nakshatra"] in CHUD_GOOD_NAK:
        score += 12; pos.append(f"Auspicious ({pan['nakshatra']}) for chudakarana")
    if pan["vara"] in ["Monday","Wednesday","Thursday","Friday"]:
        score += 5; pos.append("Benefic weekday")
    if pan["tithi_number"] in RIKTA_TITHIS + [30]:
        score -= 8; neg.append("Rikta or Amavasya — avoid")
    return _wrap(chart, target_dt, score, pos, neg, pan, "chudakarana", not _suppress_better)


# ============================================================
# 8. VIDYARAMBHA (Education start)
# ============================================================
def compute_vidyarambha_muhurta(chart, target_dt, _suppress_better=False):
    """Beginning of formal education, Aksharabhyasa, age 5+."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    VID_GOOD_NAK = ["Hasta","Chitra","Swati","Anuradha","Pushya","Punarvasu","Shravana","Revati","Uttara Phalguni","Uttara Ashadha","Uttara Bhadrapada"]
    if pan["nakshatra"] in VID_GOOD_NAK:
        score += 14; pos.append(f"Auspicious ({pan['nakshatra']}) for education-start")
    if pan["vara"] in ["Wednesday","Thursday"]:
        score += 10; pos.append(f"{pan['vara']} — Mercury/Jupiter day, ideal for learning")
    if pan["vara"] == "Tuesday":
        score -= 8; neg.append("Tuesday — Mars day, avoid")
    return _wrap(chart, target_dt, score, pos, neg, pan, "vidyarambha", not _suppress_better)


# ============================================================
# 9. VAHANA (Vehicle purchase)
# ============================================================
def compute_vahana_muhurta(chart, target_dt, _suppress_better=False):
    """Vehicle purchase / new-ride start."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    VAH_GOOD_NAK = ["Ashwini","Mrigashira","Pushya","Hasta","Chitra","Swati","Anuradha","Dhanishta","Revati"]
    if pan["nakshatra"] in VAH_GOOD_NAK:
        score += 14; pos.append(f"Auspicious ({pan['nakshatra']}) for new vehicle")
    if pan["vara"] in ["Monday","Wednesday","Thursday","Friday"]:
        score += 5; pos.append("Benefic weekday for vehicle")
    if pan["vara"] == "Saturday":
        score -= 10; neg.append("Saturn-day — avoid for new vehicle")
    return _wrap(chart, target_dt, score, pos, neg, pan, "vahana", not _suppress_better)


# ============================================================
# 10. BHUMI (Land / property purchase)
# ============================================================
def compute_bhumi_muhurta(chart, target_dt, _suppress_better=False):
    """Land or property purchase / foundation stone."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    BHU_GOOD_NAK = ["Rohini","Mrigashira","Pushya","Uttara Phalguni","Uttara Ashadha","Uttara Bhadrapada","Hasta","Anuradha","Dhanishta","Shravana","Revati"]
    if pan["nakshatra"] in BHU_GOOD_NAK:
        score += 14; pos.append(f"Sthira/auspicious nakshatra ({pan['nakshatra']}) for land")
    if pan["vara"] in ["Monday","Wednesday","Thursday","Friday"]:
        score += 5; pos.append("Benefic weekday")
    if pan["paksha"] == "Shukla":
        score += 6; pos.append("Shukla paksha — growing fortune")
    return _wrap(chart, target_dt, score, pos, neg, pan, "bhumi", not _suppress_better)


# ============================================================
# 11. VYAVAHARA (Court / litigation)
# ============================================================
def compute_vyavahara_muhurta(chart, target_dt, _suppress_better=False):
    """Court appearance / lawsuit. Strong Mars/Jupiter day, Krishna mid-tithi."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    if pan["vara"] in ["Tuesday","Thursday","Saturday"]:
        score += 8; pos.append(f"{pan['vara']} — strong day for legal matters")
    VYA_GOOD_NAK = ["Bharani","Magha","Vishakha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha"]
    if pan["nakshatra"] in VYA_GOOD_NAK:
        score += 10; pos.append(f"{pan['nakshatra']} — assertive nakshatra for litigation")
    if pan["nakshatra"] in ["Punarvasu","Anuradha","Swati"]:
        score += 6; pos.append(f"Conciliatory nakshatra — good for settlement")
    if pan["tithi_number"] in [4, 9, 14]:
        score -= 6; neg.append("Rikta tithi — outcomes uncertain")
    return _wrap(chart, target_dt, score, pos, neg, pan, "vyavahara", not _suppress_better)


# ============================================================
# 12. RAJYABHISHEKA (Coronation / promotion)
# ============================================================
def compute_rajyabhisheka_muhurta(chart, target_dt, _suppress_better=False):
    """Coronation / new role / promotion ceremony."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    RAJ_GOOD_NAK = ["Pushya","Uttara Phalguni","Uttara Ashadha","Uttara Bhadrapada","Hasta","Anuradha","Shravana","Dhanishta","Revati"]
    if pan["nakshatra"] in RAJ_GOOD_NAK:
        score += 14; pos.append(f"Royal nakshatra ({pan['nakshatra']}) for coronation")
    if pan["vara"] == "Sunday":
        score += 12; pos.append("Sunday — Sun rules royalty/leadership")
    if pan["vara"] == "Thursday":
        score += 10; pos.append("Thursday — Jupiter blessing")
    if pan["paksha"] == "Shukla":
        score += 6; pos.append("Shukla paksha — growth phase")
    if pan["tithi_number"] in [4, 9, 14, 30]:
        score -= 12; neg.append("Rikta/Amavasya — avoid for coronation")
    return _wrap(chart, target_dt, score, pos, neg, pan, "rajyabhisheka", not _suppress_better)


# ============================================================
# 13. RINA (Loan-taking / borrowing)
# ============================================================
def compute_rina_muhurta(chart, target_dt, _suppress_better=False):
    """Borrowing money / taking loan. Special rule: Krishna paksha preferred so debt wanes."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    if pan["paksha"] == "Krishna":
        score += 12; pos.append("Krishna paksha — debt energy decreases (Moon waning)")
    else:
        score -= 4; neg.append("Shukla paksha — debt may grow")
    if pan["vara"] in ["Wednesday","Thursday","Friday"]:
        score += 6; pos.append("Mercury/Jupiter/Venus day — money flow benevolent")
    if pan["vara"] == "Tuesday":
        score -= 12; neg.append("Tuesday — Mars day, avoid (cuts/disputes)")
    if pan["nakshatra"] in ["Pushya","Hasta","Anuradha","Dhanishta","Revati"]:
        score += 8; pos.append(f"Auspicious nakshatra ({pan['nakshatra']}) for borrowing")
    return _wrap(chart, target_dt, score, pos, neg, pan, "rina", not _suppress_better)


# ============================================================
# 14. DAHANA (Funeral / cremation)
# ============================================================
def compute_dahana_muhurta(chart, target_dt, _suppress_better=False):
    """Funeral / cremation. Avoid Triphala-Shadyoni nakshatras + certain tithis."""
    pan = compute_panchanga(target_dt); pan["_when_dt"] = target_dt
    score, pos, neg = _base_score(pan, chart)
    # Triphala = Magha, Mula, Revati (start of cycles); also Bharani/Krittika difficult
    TRIPHALA_BAD = ["Magha","Mula","Revati","Ashlesha","Jyeshtha"]
    if pan["nakshatra"] in TRIPHALA_BAD:
        score -= 18; neg.append(f"Triphala nakshatra ({pan['nakshatra']}) — avoid for cremation")
    # Avoid nakshatra padas overlapping with Janma nakshatra
    janma = chart.get("janma_nakshatra")
    if janma and pan["nakshatra"] == janma:
        score -= 12; neg.append(f"Janma nakshatra ({janma}) of deceased — avoid")
    if pan["tithi_number"] in [1, 11, 30]:
        score -= 6; neg.append(f"Avoid tithi {pan['tithi']} for funeral")
    if pan["nakshatra"] in ["Anuradha","Pushya","Punarvasu","Hasta"]:
        score += 6; pos.append(f"Acceptable nakshatra ({pan['nakshatra']}) for last rites")
    return _wrap(chart, target_dt, score, pos, neg, pan, "dahana", not _suppress_better)


# ============================================================
# AGGREGATE — run all 14 for a date
# ============================================================
ALL_MUHURTAS = {
    "gemstone": compute_gemstone_muhurta,
    "griha-pravesh": compute_griha_pravesh_muhurta,
    "garbhadhana": compute_garbhadhana_muhurta,
    "namakarana": compute_namakarana_muhurta,
    "upanayana": compute_upanayana_muhurta,
    "annaprashana": compute_annaprashana_muhurta,
    "chudakarana": compute_chudakarana_muhurta,
    "vidyarambha": compute_vidyarambha_muhurta,
    "vahana": compute_vahana_muhurta,
    "bhumi": compute_bhumi_muhurta,
    "vyavahara": compute_vyavahara_muhurta,
    "rajyabhisheka": compute_rajyabhisheka_muhurta,
    "rina": compute_rina_muhurta,
    "dahana": compute_dahana_muhurta,
}


def all_muhurtas_for_date(chart, target_dt):
    """Run all 14 muhurta types and return summary for a date."""
    results = {}
    for name, fn in ALL_MUHURTAS.items():
        try:
            results[name] = fn(chart, target_dt, _suppress_better=True)
        except Exception as e:
            results[name] = {"error": str(e)}
    return results


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    today = dt.datetime.now()
    print(f"=== ALL 14 MUHURTAS for {today.date()} ({chart['name']}) ===\n")
    for name, fn in ALL_MUHURTAS.items():
        r = fn(chart, today)
        print(f"  [{r['verdict']:11s}  {r['score']:3d}/100]  {name}")
        if r.get("reasons_supportive"):
            print(f"        +  {' / '.join(r['reasons_supportive'][:2])}")
        if r.get("reasons_against"):
            print(f"        -  {' / '.join(r['reasons_against'][:2])}")
        if r.get("better_dates"):
            best = r["better_dates"][0]
            print(f"        ->  Better: {best['date']} (score {best['score']})")
        print()
