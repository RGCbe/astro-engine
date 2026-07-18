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

    print("  Precomputing base data...")
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
        
        transit_sat_bad = False
        transit_jup_good = False
        transit_jup_bad = False
        transit_rah_bad = False
        
        for tp in transit_snap.get("transit_planets", []):
            pn = tp["planet"]
            val = tp["gochar_valence"]
            if pn == "Saturn" and val == "BAD": transit_sat_bad = True
            elif pn == "Jupiter" and val == "GOOD": transit_jup_good = True
            elif pn == "Jupiter" and val == "BAD": transit_jup_bad = True
            elif pn == "Rahu" and val == "BAD": transit_rah_bad = True

        rules = corpus.get_dasha_rules(md, ad, limit=12)
        aus_c = sum(1 for r in rules if rule_valence(r.text) == "auspicious")
        ina_c = sum(1 for r in rules if rule_valence(r.text) == "inauspicious")

        is_self_pd = (pd_lord == ad and pd_lord not in ["Rahu", "Ketu"])
        is_jup_pd = (pd_lord == "Jupiter")

        d_sign, b_sign = natal_signs.get(md), natal_signs.get(ad)
        rel = get_mutual_relationship(d_sign, b_sign)
        
        is_shadashtaka = rel in [(6,8),(8,6)]
        is_self_dasa = md == ad
        
        inimical_pairs = [("Mercury","Sun"), ("Mercury","Mars"), ("Mercury","Ketu"),
                          ("Venus","Sun"), ("Venus","Moon"), ("Venus","Rahu"),
                          ("Ketu","Venus"), ("Ketu","Sun"), ("Ketu","Moon")]
        is_inimical = (md, ad) in inimical_pairs or (ad, md) in inimical_pairs
        
        is_malefic_ad = ad in ["Mars","Sun","Jupiter"]
        
        is_conjunction = False
        if md == "Mercury" and ad in ["Sun","Saturn"]: is_conjunction = True
        elif ad == "Venus" and md == "Mercury": is_conjunction = True
        elif ad == "Mars" and md == "Mercury": is_conjunction = True

        film_base.append({
            "valence": f["valence"],
            "aus_c": aus_c, "ina_c": ina_c,
            "transit_sat_bad": transit_sat_bad,
            "transit_jup_good": transit_jup_good,
            "transit_jup_bad": transit_jup_bad,
            "transit_rah_bad": transit_rah_bad,
            "is_shadashtaka": is_shadashtaka,
            "is_self_dasa": is_self_dasa,
            "is_inimical": is_inimical,
            "is_malefic_ad": is_malefic_ad,
            "is_conjunction": is_conjunction,
            "pd_func": pd_func, "is_self_pd": is_self_pd, "is_jup_pd": is_jup_pd,
        })

    # Exact baseline parameters
    s_w, in_w, ma_w, self_w, conj_w = 0.20, 0.65, 0.75, 0.85, 0.75
    sb, jg, jb, rb = 0.22, 0.28, 0.15, 0.15
    pm, pb, sp, kj = 0.7, 0.8, 0.6, 0.7

    hits = 0
    for fb in film_base:
        gf = 1.0
        if fb["transit_sat_bad"]: gf -= sb
        if fb["transit_jup_good"]: gf += jg
        if fb["transit_jup_bad"]: gf -= jb
        if fb["transit_rah_bad"]: gf -= rb
        gf = max(0.4, min(1.6, gf))
        
        rapm_a, rapm_i = 1.0, 1.0
        if fb["is_shadashtaka"]: rapm_a *= s_w; rapm_i *= (2.0 - s_w)
        if fb["is_self_dasa"]: rapm_a *= self_w; rapm_i *= (2.0 - self_w)
        if fb["is_inimical"]: rapm_a *= in_w; rapm_i *= (2.0 - in_w)
        if fb["is_malefic_ad"]: rapm_a *= ma_w; rapm_i *= (2.0 - ma_w)
        if fb["is_conjunction"]: rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)

        raw_aus = fb["aus_c"] * gf * rapm_a
        raw_ina = fb["ina_c"] * (1.0/gf) * rapm_i

        pda, pdi = 1.0, 1.0
        if fb["pd_func"] == "MALEFIC":
            pda *= (1.0 - pm); pdi *= (1.0 + pm)
        elif fb["pd_func"] == "BENEFIC":
            pda *= (1.0 + pb); pdi *= (1.0 - pb/2.0)
        if fb["is_self_pd"]:
            pda *= (1.0 - sp); pdi *= (1.0 + sp)
        if fb["is_jup_pd"]:
            pda *= (1.0 - kj); pdi *= (1.0 + kj)

        fa = raw_aus * pda
        fi = raw_ina * pdi
        pred = "neutral"
        if fa > fi + 0.15: pred = "auspicious"
        elif fi > fa + 0.15: pred = "inauspicious"
        if pred == fb["valence"]: hits += 1

    print(f"  Accuracy check: {hits / len(FILMS) * 100:.2f}% ({hits}/68)")

if __name__ == "__main__":
    asyncio.run(main())
