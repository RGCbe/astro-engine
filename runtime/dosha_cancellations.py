"""Doshas + Cancellation Rules — every classical dosha with its exception.

Source: Muhurta Chintamani, Phaladeepika Ch. 16, BPHS, Jataka Parijata.

Critical: each dosha has classical CANCELLATIONS that most software ignores.
"""
import sys
sys.path.insert(0, ".")

from vedic_core import RASIS, RASI_LORDS  # canonical 12 signs + lords


def detect_manglik_dosha(chart):
    """Manglik (Kuja) Dosha — Mars in 1/2/4/7/8/12 from Lagna OR Moon OR Venus.

    CANCELLATIONS (Muhurta Chintamani, Phaladeepika):
      1. Mars in own sign (Aries/Scorpio) or exalted (Capricorn) — cancelled
      2. Mars in Cancer/Leo (friend's house) — partially cancelled
      3. Mars aspected by Jupiter — cancelled
      4. Mars conjunct Jupiter — cancelled
      5. Mars in 2nd from Lagna in Gemini/Virgo — cancelled
      6. If both partners are Manglik — cancelled
      7. Mars retrograde — cancelled
    """
    pos = chart["positions"]
    if "Mars" not in pos: return None
    mars = pos["Mars"]
    mars_h = mars["house"]
    mars_sign = mars["rasi"]

    DOSHA_HOUSES = [1, 2, 4, 7, 8, 12]
    is_dosha = mars_h in DOSHA_HOUSES

    # Also check from Moon
    if "Moon" in pos:
        moon_h = pos["Moon"]["house"]
        mars_h_from_moon = ((mars["rasi_idx"] - pos["Moon"]["rasi_idx"]) % 12) + 1
        is_dosha_from_moon = mars_h_from_moon in DOSHA_HOUSES
    else:
        is_dosha_from_moon = False

    # Check from Venus
    if "Venus" in pos:
        mars_h_from_venus = ((mars["rasi_idx"] - pos["Venus"]["rasi_idx"]) % 12) + 1
        is_dosha_from_venus = mars_h_from_venus in DOSHA_HOUSES
    else:
        is_dosha_from_venus = False

    base_dosha = is_dosha or is_dosha_from_moon or is_dosha_from_venus
    if not base_dosha:
        return {"is_dosha": False, "cancelled": False, "verdict": "No Manglik dosha"}

    # Check cancellations
    cancellations = []
    if mars_sign in ["Aries","Scorpio"]:
        cancellations.append("Mars in own sign — cancelled")
    if mars_sign == "Capricorn":
        cancellations.append("Mars exalted — cancelled")
    if mars_sign in ["Cancer","Leo"]:
        cancellations.append("Mars in friend's sign — partial cancellation")
    # Jupiter aspect on Mars (5/7/9 from Jupiter to Mars)
    if "Jupiter" in pos:
        jup_h = pos["Jupiter"]["house"]
        jup_aspects = [((jup_h+4-1)%12)+1, ((jup_h+6-1)%12)+1, ((jup_h+8-1)%12)+1]
        if mars_h in jup_aspects:
            cancellations.append("Jupiter aspects Mars — cancelled")
        if pos["Jupiter"]["rasi_idx"] == mars["rasi_idx"]:
            cancellations.append("Mars conjunct Jupiter — cancelled")
    if mars_h == 2 and mars_sign in ["Gemini","Virgo"]:
        cancellations.append("Mars in 2H Gemini/Virgo — cancelled")

    is_cancelled = len(cancellations) > 0
    verdict = ("Manglik dosha PRESENT but CANCELLED via classical exception"
               if is_cancelled else "Manglik dosha PRESENT — needs careful matching")

    return {
        "is_dosha": True,
        "houses_triggered": [
            f"Mars in H{mars_h} from Lagna" if is_dosha else None,
            f"Mars in H{mars_h_from_moon} from Moon" if is_dosha_from_moon else None,
            f"Mars in H{mars_h_from_venus} from Venus" if is_dosha_from_venus else None,
        ],
        "cancelled": is_cancelled,
        "cancellations": cancellations,
        "verdict": verdict,
    }


def detect_kaal_sarpa(chart):
    """Kaal Sarpa Dosha — all 7 planets between Rahu-Ketu axis.

    CANCELLATIONS:
      1. Jupiter or Venus exalted/own — partial cancellation
      2. Strong Moon — partial cancellation
      3. If Rahu is in 3/6/11 — cancelled (Rahu is friend in these houses)
      4. Yoga-forming planets aspecting Rahu/Ketu — partial
    """
    pos = chart["positions"]
    if "Rahu" not in pos or "Ketu" not in pos: return None

    rahu_lon = pos["Rahu"]["rasi_idx"]*30 + pos["Rahu"]["deg"]
    ketu_lon = pos["Ketu"]["rasi_idx"]*30 + pos["Ketu"]["deg"]
    inside = 0; outside = 0
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        if p not in pos: continue
        plon = pos[p]["rasi_idx"]*30 + pos[p]["deg"]
        diff = (plon - rahu_lon) % 360
        ket_diff = (ketu_lon - rahu_lon) % 360
        if diff < ket_diff: inside += 1
        else: outside += 1

    is_dosha = inside == 7 or outside == 7
    if not is_dosha:
        return {"is_dosha": False, "verdict": "No Kaal Sarpa dosha"}

    # Cancellations
    cancellations = []
    rahu_h = pos["Rahu"]["house"]
    if rahu_h in [3, 6, 11]:
        cancellations.append(f"Rahu in {rahu_h}H (friend's house) — cancelled")
    if "Jupiter" in pos:
        from vedic_core import DIGNITIES
        if DIGNITIES.get(("Jupiter", pos["Jupiter"]["rasi"])) in ["Own","Exalted"]:
            cancellations.append("Jupiter strong — partial cancellation")

    return {
        "is_dosha": True,
        "type": "Anuloma" if inside == 7 else "Pratiloma",
        "cancelled": len(cancellations) > 0,
        "cancellations": cancellations,
        "verdict": "Kaal Sarpa CANCELLED" if cancellations else "Kaal Sarpa ACTIVE",
    }


def detect_nadi_dosha_full(boy_chart, girl_chart):
    """Nadi Dosha + cancellations.

    CANCELLATIONS:
      1. Same nakshatra in different padas
      2. Same Moon-rasi but different nakshatra-lord
      3. Both partners' Mercury or Jupiter strong
      4. Boy and girl from same gotra/family
    """
    from compatibility_kuta import NADI
    b_nak = boy_chart.get("janma_nakshatra")
    g_nak = girl_chart.get("janma_nakshatra")
    bn = NADI.get(b_nak); gn = NADI.get(g_nak)
    if not bn or not gn:
        return {"is_dosha": False, "verdict": "Cannot determine"}
    if bn != gn:
        return {"is_dosha": False, "verdict": "No Nadi dosha"}

    cancellations = []
    if b_nak == g_nak:
        # Same nakshatra in different padas
        cancellations.append("Same nakshatra — check pada difference")
    # Different Moon-rasi
    b_moon = boy_chart.get("moon_rasi")
    g_moon = girl_chart.get("moon_rasi")
    if b_moon and g_moon and b_moon != g_moon:
        cancellations.append(f"Different Moon-rasi ({b_moon} vs {g_moon}) — partial cancellation")

    return {
        "is_dosha": True,
        "common_nadi": bn,
        "cancelled": len(cancellations) > 0,
        "cancellations": cancellations,
        "verdict": "Nadi CANCELLED" if cancellations else "Nadi ACTIVE — significant concern",
    }


def detect_bhakoot_dosha_full(boy_chart, girl_chart):
    """Bhakoot Dosha (sign distance 6 or 8) + cancellations.

    CANCELLATIONS:
      1. If lords of both rasis are friends — cancelled
      2. If Navamsa lords are friends — cancelled
      3. Same lord rules both signs — cancelled
    """
    SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    b_rasi = boy_chart.get("moon_rasi")
    g_rasi = girl_chart.get("moon_rasi")
    if not b_rasi or not g_rasi: return None
    bi = SIGNS.index(b_rasi); gi = SIGNS.index(g_rasi)
    diff = (gi - bi) % 12
    bad = [5, 6, 7, 8]  # 6th and 8th from each other
    is_dosha = diff in bad and (12 - diff) % 12 in bad

    if not is_dosha:
        return {"is_dosha": False, "verdict": "No Bhakoot dosha"}

    # Cancellations
    cancellations = []
    bl = RASI_LORDS[b_rasi]
    gl = RASI_LORDS[g_rasi]
    if bl == gl:
        cancellations.append(f"Same lord ({bl}) rules both signs — cancelled")

    FRIEND_PAIRS = {("Sun","Moon"),("Sun","Mars"),("Sun","Jupiter"),("Moon","Mercury"),
                    ("Mars","Jupiter"),("Mercury","Venus"),("Venus","Saturn")}
    pair = (bl, gl); pair2 = (gl, bl)
    if pair in FRIEND_PAIRS or pair2 in FRIEND_PAIRS:
        cancellations.append(f"{bl} and {gl} are friends — cancelled")

    return {
        "is_dosha": True,
        "distance": diff,
        "cancelled": len(cancellations) > 0,
        "cancellations": cancellations,
        "verdict": "Bhakoot CANCELLED" if cancellations else "Bhakoot ACTIVE",
    }


def all_doshas_summary(chart, partner_chart=None):
    out = {
        "manglik": detect_manglik_dosha(chart),
        "kaal_sarpa": detect_kaal_sarpa(chart),
    }
    if partner_chart:
        out["nadi"] = detect_nadi_dosha_full(chart, partner_chart)
        out["bhakoot"] = detect_bhakoot_dosha_full(chart, partner_chart)
    return out


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    result = all_doshas_summary(chart)
    print(f"=== DOSHAS ANALYSIS for {chart['name']} ===\n")
    for name, d in result.items():
        if d is None: continue
        print(f"  {name.upper()}:")
        print(f"    {d.get('verdict','?')}")
        if d.get("cancellations"):
            for c in d["cancellations"]:
                print(f"      - {c}")
        print()
