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

    from scratch.vijay_pd_centric_fix import FILMS, get_mutual_relationship, rule_valence

    # Baseline params
    s_w, in_w, ma_w, self_w, conj_w = 0.20, 0.65, 0.75, 0.85, 0.75

    for idx, f in enumerate(FILMS[:5]):
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        active = current_dasha(low_level_chart, dt_obj)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        pd_lord = active.get("pd", {}).get("pd", "Unknown")

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

        rules = corpus.get_dasha_rules(md, ad, limit=12)
        aus_c = sum(1 for r in rules if rule_valence(r.text) == "auspicious")
        ina_c = sum(1 for r in rules if rule_valence(r.text) == "inauspicious")

        raw_aus = aus_c * gf * rapm_a
        raw_ina = ina_c * (1.0/gf) * rapm_i

        print(f"Film {idx+1}: {f['name']}")
        print(f"  Vijay PD Centric Base: raw_aus={raw_aus:.4f}, raw_ina={raw_ina:.4f}")

        # Compare with precomputed flags:
        is_shadashtaka = rel in [(6,8),(8,6)]
        is_self_dasa = md == ad
        is_inimical = (md, ad) in inimical_pairs or (ad, md) in inimical_pairs
        is_malefic_ad = ad in ["Mars","Sun","Jupiter"]
        
        is_conjunction = False
        if md == "Mercury" and ad in ["Sun","Saturn"]: is_conjunction = True
        elif ad == "Venus" and md == "Mercury": is_conjunction = True
        elif ad == "Mars" and md == "Mercury": is_conjunction = True

        p_rapm_a, p_rapm_i = 1.0, 1.0
        if is_shadashtaka: p_rapm_a *= s_w; p_rapm_i *= (2.0 - s_w)
        if is_self_dasa: p_rapm_a *= self_w; p_rapm_i *= (2.0 - self_w)
        if is_inimical: p_rapm_a *= in_w; p_rapm_i *= (2.0 - in_w)
        if is_malefic_ad: p_rapm_a *= ma_w; p_rapm_i *= (2.0 - ma_w)
        if is_conjunction: p_rapm_a *= conj_w; p_rapm_i *= (2.0 - conj_w)

        p_raw_aus = aus_c * gf * p_rapm_a
        p_raw_ina = ina_c * (1.0/gf) * p_rapm_i
        print(f"  Precomputed Flags Base: raw_aus={p_raw_aus:.4f}, raw_ina={p_raw_ina:.4f}")
        print(f"  Matches? raw_aus: {abs(raw_aus - p_raw_aus) < 1e-5}, raw_ina: {abs(raw_ina - p_raw_ina) < 1e-5}")

if __name__ == "__main__":
    asyncio.run(main())
