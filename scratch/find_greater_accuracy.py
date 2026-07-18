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
from scratch.vijay_pd_centric_fix import FILMS, get_mutual_relationship, rule_valence

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

    print("  Precomputing base film data...")
    film_data = []
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

        d_sign, b_sign = natal_signs.get(md), natal_signs.get(ad)
        rel = get_mutual_relationship(d_sign, b_sign)

        rules = corpus.get_dasha_rules(md, ad, limit=12)
        aus_c = sum(1 for r in rules if rule_valence(r.text) == "auspicious")
        ina_c = sum(1 for r in rules if rule_valence(r.text) == "inauspicious")

        is_self_pd = (pd_lord == ad and pd_lord not in ["Rahu", "Ketu"])
        is_jup_pd = (pd_lord == "Jupiter")

        film_data.append({
            "film": f,
            "md": md, "ad": ad, "pd": pd_lord,
            "rel": rel,
            "gf": gf,
            "aus_c": aus_c, "ina_c": ina_c,
            "pd_func": pd_func, "is_self_pd": is_self_pd, "is_jup_pd": is_jup_pd
        })

    import itertools
    combinations = list(itertools.product(
        [0.10, 0.20, 0.30],  # s_w
        [0.50, 0.65, 0.80],  # in_w
        [0.60, 0.75, 0.90],  # ma_w
        [0.70, 0.85, 1.00],  # self_w
        [0.60, 0.75, 0.90],  # conj_w
        [0.0, 0.3, 0.6],     # pm
        [0.2, 0.4, 0.6, 0.8],# pb
        [0.0, 0.3, 0.6],     # sp
        [0.0, 0.3, 0.6, 0.8] # kj
    ))

    print(f"  Searching over {len(combinations)} combinations to beat 76.47%...")
    best_acc = 0
    best_p = {}
    
    # Pure lightweight arithmetic
    for s_w, in_w, ma_w, self_w, conj_w, pm, pb, sp, kj in combinations:
        hits = 0
        for fd in film_data:
            md, ad = fd["md"], fd["ad"]
            
            # RAPM
            rapm_a, rapm_i = 1.0, 1.0
            if fd["rel"] in [(6,8),(8,6)]: rapm_a *= s_w; rapm_i *= (2.0 - s_w)
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

            raw_aus = fd["aus_c"] * fd["gf"] * rapm_a
            raw_ina = fd["ina_c"] * (1.0/fd["gf"]) * rapm_i

            pda, pdi = 1.0, 1.0
            if fd["pd_func"] == "MALEFIC":
                pda *= (1.0 - pm); pdi *= (1.0 + pm)
            elif fd["pd_func"] == "BENEFIC":
                pda *= (1.0 + pb); pdi *= (1.0 - pb/2.0)
            if fd["is_self_pd"]:
                pda *= (1.0 - sp); pdi *= (1.0 + sp)
            if fd["is_jup_pd"]:
                pda *= (1.0 - kj); pdi *= (1.0 + kj)

            fa = raw_aus * pda
            fi = raw_ina * pdi
            pred = "neutral"
            if fa > fi + 0.15: pred = "auspicious"
            elif fi > fa + 0.15: pred = "inauspicious"
            if pred == fd["film"]["valence"]: hits += 1

        if hits > best_acc:
            best_acc = hits
            best_p = {
                "s_w": s_w, "in_w": in_w, "ma_w": ma_w, "self_w": self_w, "conj_w": conj_w,
                "pm": pm, "pb": pb, "sp": sp, "kj": kj
            }

    print(f"  BEST ACCURACY ACHIEVED: {best_acc / len(FILMS) * 100:.2f}% ({best_acc}/68)")
    print(f"  Parameters:")
    for k, v in best_p.items():
        print(f"    - {k:<8}: {v:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
