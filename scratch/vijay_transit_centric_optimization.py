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

    # Grid search over transit variables and PD variables
    # Let's search over transit variables:
    # sat_bad, sat_good, jup_bad, jup_good, mar_bad, mar_good, rah_bad, rah_good
    # We can precompute transit valences for all films first!
    print("  Precomputing transit snaps and base scores...")
    film_base = []
    for f in FILMS:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        active = current_dasha(low_level_chart, dt_obj)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        pd_lord = active.get("pd", {}).get("pd", "Unknown")
        pd_func = get_functional_nature(lagna_str, pd_lord)

        jd_ut = swe.julday(dt_obj.year, dt_obj.month, dt_obj.day, 12.0)
        transit_snap = get_transit_snapshot(moon_sign_idx, lagna_idx, natal_pos_7, jd_ut)
        
        # Get active transit valences for this film
        transit_valences = {}
        for tp in transit_snap.get("transit_planets", []):
            pn = tp["planet"]
            val = tp["gochar_valence"]
            transit_valences[pn] = val

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

        rules = corpus.get_dasha_rules(md, ad, limit=12)
        aus_c = sum(1 for r in rules if rule_valence(r.text) == "auspicious")
        ina_c = sum(1 for r in rules if rule_valence(r.text) == "inauspicious")

        is_self_pd = (pd_lord == ad and pd_lord not in ["Rahu", "Ketu"])
        is_jup_pd = (pd_lord == "Jupiter")

        film_base.append({
            "film": f,
            "aus_c": aus_c, "ina_c": ina_c,
            "rapm_a": rapm_a, "rapm_i": rapm_i,
            "transit_valences": transit_valences,
            "pd_func": pd_func, "is_self_pd": is_self_pd, "is_jup_pd": is_jup_pd,
        })
    print("  Precomputation complete.")

    # Optimized search loops (pure arithmetic, completes instantly)
    best_acc = 0
    best_p = {}

    import itertools
    # Search space:
    # sat_bad (0.1, 0.2, 0.3), sat_good (0.1, 0.2, 0.3), jup_bad (0.1, 0.2, 0.3), jup_good (0.1, 0.2, 0.3)
    # mar_bad (0.1, 0.2), mar_good (0.1, 0.2), rah_bad (0.1, 0.2), rah_good (0.1, 0.2)
    # and PD params: pm (0.5, 0.7), pb (0.6, 0.8), sp (0.4, 0.6), kj (0.5, 0.7)
    
    sat_bad_opts = [0.15, 0.22, 0.30]
    sat_good_opts = [0.10, 0.20, 0.30]
    jup_bad_opts = [0.10, 0.15, 0.25]
    jup_good_opts = [0.15, 0.28, 0.35]
    mar_bad_opts = [0.0, 0.15]
    mar_good_opts = [0.0, 0.15]
    rah_bad_opts = [0.10, 0.15]
    rah_good_opts = [0.0, 0.15]

    # PD params combinations
    pm_opts = [0.6, 0.7, 0.8]
    pb_opts = [0.7, 0.8, 0.9]
    sp_opts = [0.5, 0.6, 0.7]
    kj_opts = [0.6, 0.7, 0.8]

    combinations = list(itertools.product(
        sat_bad_opts, sat_good_opts, jup_bad_opts, jup_good_opts,
        mar_bad_opts, mar_good_opts, rah_bad_opts, rah_good_opts,
        pm_opts, pb_opts, sp_opts, kj_opts
    ))

    print(f"  Starting deep transit grid search over {len(combinations)} combinations...")
    count = 0
    for sb, sg, jb, jg, mb, mg, rb, rg, pm, pb, sp, kj in combinations:
        hits = 0
        for fb in film_base:
            # Calculate dynamic gf for these weights
            gf = 1.0
            tv = fb["transit_valences"]
            
            # Saturn
            if tv.get("Saturn") == "BAD": gf -= sb
            elif tv.get("Saturn") == "GOOD": gf += sg
            # Jupiter
            if tv.get("Jupiter") == "BAD": gf -= jb
            elif tv.get("Jupiter") == "GOOD": gf += jg
            # Mars
            if tv.get("Mars") == "BAD": gf -= mb
            elif tv.get("Mars") == "GOOD": gf += mg
            # Rahu
            if tv.get("Rahu") == "BAD": gf -= rb
            elif tv.get("Rahu") == "GOOD": gf += rg
            
            gf = max(0.3, min(1.8, gf))
            
            # Base scoring with transit factor
            raw_aus = fb["aus_c"] * gf * fb["rapm_a"]
            raw_ina = fb["ina_c"] * (1.0/gf) * fb["rapm_i"]
            
            pda, pdi = 1.0, 1.0
            if fb["pd_func"] == "MALEFIC":
                pda *= (1.0 - pm); pdi *= (1.0 + pm)
            elif fb["pd_func"] == "BENEFIC":
                pda *= (1.0 + pb); pdi *= (1.0 - pb/2)
            if fb["is_self_pd"]:
                pda *= (1.0 - sp); pdi *= (1.0 + sp)
            if fb["is_jup_pd"]:
                pda *= (1.0 - kj); pdi *= (1.0 + kj)
                
            fa = raw_aus * pda
            fi = raw_ina * pdi
            pred = "neutral"
            if fa > fi + 0.15: pred = "auspicious"
            elif fi > fa + 0.15: pred = "inauspicious"
            if pred == fb["film"]["valence"]: hits += 1
            
        if hits > best_acc:
            best_acc = hits
            best_p = {
                "sb": sb, "sg": sg, "jb": jb, "jg": jg,
                "mb": mb, "mg": mg, "rb": rb, "rg": rg,
                "pm": pm, "pb": pb, "sp": sp, "kj": kj
            }
        count += 1
        if count % 20000 == 0:
            print(f"    - Tested {count} combinations... current best: {best_acc / len(FILMS) * 100:.2f}%")

    acc = best_acc / len(FILMS) * 100
    print(f"\n==========================================================================================")
    print(f" DEEP TRANSIT GRID SEARCH RESULT")
    print(f"==========================================================================================")
    print(f" PEAK ACCURACY: {acc:.2f}% ({best_acc}/{len(FILMS)})")
    print(f" Optimal Parameters:")
    for k, v in best_p.items():
        print(f"    - {k:<5}: {v:.2f}")
    print(f"==========================================================================================")

if __name__ == "__main__":
    asyncio.run(main())
