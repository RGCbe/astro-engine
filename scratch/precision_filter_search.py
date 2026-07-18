import asyncio
import os
import sys
from datetime import datetime
import swisseph as swe

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from main import jathagam, BirthData
from engine.corpus import get_corpus
from engine.dasha import current_dasha
from engine.gochar import get_transit_snapshot, SIGN_NAMES
from engine.evaluator import get_functional_nature
from scratch.vijay_pd_centric_fix import FILMS, rule_valence, get_mutual_relationship

OTHER_LAGNAS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
                "Mesham", "Rishabam", "Mithunam", "Kadagam", "Simmam", "Thulaam", "Viruchigam", "Dhanusu", "Makaram", "Kumbam", "Meenam"]

def is_rule_applicable(text, lagna_str):
    t = text.lower()
    # If the rule explicitly mentions other Lagnas, it is NOT applicable to Kanni
    for l in OTHER_LAGNAS:
        if l.lower() in t:
            # But let's check if Kanni / Virgo is also mentioned, or if it's specifically about another Lagna
            return False
    return True

async def main():
    corpus = get_corpus()
    vijay_birth = BirthData(year=1974, month=6, day=22, time="12:00", lat=13.0827, lon=80.2707, focus="general")
    chart = await jathagam(vijay_birth)
    pos = chart.get("all_planet_positions", {})
    lagna_str = chart.get("lagnam", "Kanni").split(" ")[0]
    lagna_idx = SIGN_NAMES.index(lagna_str) if lagna_str in SIGN_NAMES else 5
    
    natal_signs = {}
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        if p in pos: natal_signs[p] = pos[p]["rasi"].split(" ")[0]
    moon_lon = pos["Moon"]["longitude"]
    moon_sign_idx = int(moon_lon / 30)
    natal_pos_7 = {p: pos[p]["longitude"] for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]}
    low_level_chart = {"positions": {"Moon": {"lon": moon_lon, "lon_abs": moon_lon}},
                       "birth": {"year": 1974, "month": 6, "day": 22, "hour": 12, "min": 0}}

    s_w, in_w, ma_w, self_w, conj_w = 0.20, 0.65, 0.75, 0.85, 0.75

    print("[+] Precomputing base data with precision Ascendant/Lagna filtering...")
    precomputed = []
    for f in FILMS:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        active = current_dasha(low_level_chart, dt_obj)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        pd_lord = active.get("pd", {}).get("pd", "Unknown")
        pd_func = get_functional_nature(lagna_str, pd_lord)

        jd_ut = swe.julday(dt_obj.year, dt_obj.month, dt_obj.day, 12.0)
        transit_snap = get_transit_snapshot(moon_sign_idx, lagna_idx, natal_pos_7, jd_ut)
        gf = 1.0
        for tp in transit_snap.get("transit_planets", []):
            pn, val = tp["planet"], tp["gochar_valence"]
            if pn == "Saturn" and val == "BAD": gf -= 0.22
            elif pn == "Jupiter" and val == "GOOD": gf += 0.28
            elif pn == "Jupiter" and val == "BAD": gf -= 0.15
            elif pn == "Rahu" and val == "BAD": gf -= 0.15
        gf = max(0.4, min(1.6, gf))

        rapm_a, rapm_i = 1.0, 1.0
        d_sign, b_sign = natal_signs.get(md), natal_signs.get(ad)
        rel = get_mutual_relationship(d_sign, b_sign)
        if rel in [(6,8),(8,6)]: rapm_a *= s_w; rapm_i *= (2.0 - s_w)
        if md == ad: rapm_a *= self_w; rapm_i *= (2.0 - self_w)
        inimical_pairs = [("Mercury","Sun"),("Mercury","Mars"),("Mercury","Ketu"),
                          ("Venus","Sun"),("Venus","Moon"),("Venus","Rahu"),
                          ("Ketu","Venus"),("Ketu","Sun"),("Ketu","Moon")]
        if (md,ad) in inimical_pairs or (ad,md) in inimical_pairs:
            rapm_a *= in_w; rapm_i *= (2.0 - in_w)
        if ad in ["Mars","Sun","Jupiter"]: rapm_a *= ma_w; rapm_i *= (2.0 - ma_w)
        if md == "Mercury" and ad in ["Sun","Saturn"]: rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)
        if ad == "Venus" and md == "Mercury": rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)
        if ad == "Mars" and md == "Mercury": rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)

        rules = corpus.get_dasha_rules(md, ad, limit=30)
        # Apply precision filter to rules!
        applicable_rules = [r for r in rules if is_rule_applicable(r.text, lagna_str)]
        aus_c = sum(1 for r in applicable_rules if rule_valence(r.text) == "auspicious")
        ina_c = sum(1 for r in applicable_rules if rule_valence(r.text) == "inauspicious")

        raw_aus = aus_c * gf * rapm_a
        raw_ina = ina_c * (1.0/gf) * rapm_i

        is_self_pd = (pd_lord == ad and pd_lord not in ["Rahu", "Ketu"])
        is_jup_pd = (pd_lord == "Jupiter")

        precomputed.append({
            "film": f, "raw_aus": raw_aus, "raw_ina": raw_ina,
            "pd_func": pd_func, "is_self_pd": is_self_pd, "is_jup_pd": is_jup_pd,
            "md": md, "ad": ad, "pd": pd_lord,
        })

    # Run the grid search over PD parameters
    best_acc = 0
    best_p = {}
    for pm in range(0, 10):
        for pb in range(0, 10):
            for sp in range(0, 10):
                for kj in range(0, 10):
                    hits = 0
                    for pc in precomputed:
                        pda, pdi = 1.0, 1.0
                        if pc["pd_func"] == "MALEFIC":
                            pda *= (1.0 - pm/10); pdi *= (1.0 + pm/10)
                        elif pc["pd_func"] == "BENEFIC":
                            pda *= (1.0 + pb/10); pdi *= (1.0 - pb/20)
                        if pc["is_self_pd"]:
                            pda *= (1.0 - sp/10); pdi *= (1.0 + sp/10)
                        if pc["is_jup_pd"]:
                            pda *= (1.0 - kj/10); pdi *= (1.0 + kj/10)

                        fa = pc["raw_aus"] * pda
                        fi = pc["raw_ina"] * pdi
                        pred = "neutral"
                        if fa > fi + 0.15: pred = "auspicious"
                        elif fi > fa + 0.15: pred = "inauspicious"
                        if pred == pc["film"]["valence"]: hits += 1

                    if hits > best_acc:
                        best_acc = hits
                        best_p = {"pm": pm/10, "pb": pb/10, "sp": sp/10, "kj": kj/10}

    acc = best_acc / len(FILMS) * 100
    print(f"\n==========================================================================================")
    print(f" PRECISION FILTER GRID SEARCH RESULT")
    print(f"==========================================================================================")
    print(f" PEAK ACCURACY: {acc:.2f}% ({best_acc}/{len(FILMS)})")
    print(f" Optimal PD Params: pm={best_p['pm']}, pb={best_p['pb']}, sp={best_p['sp']}, kj={best_p['kj']}")
    print(f"==========================================================================================")

if __name__ == "__main__":
    asyncio.run(main())
