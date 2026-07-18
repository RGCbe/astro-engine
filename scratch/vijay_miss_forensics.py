"""
DEEP MISS ANALYSIS
==================
Instead of blindly adding layers, let's examine each of the 17 misses
forensically to understand WHY they're wrong and what would fix them
WITHOUT breaking any existing correct prediction.
"""

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
from engine.ashtakavarga import bhinna_ashtakavarga, sarva_ashtakavarga, BAV_STRONG_THRESHOLD

AUSPICIOUS_KW  = ["wealth","success","fame","happiness","health","gain","auspicious",
                   "good fortune","rich","king","prosperous","honor","victory","blessed",
                   "excellent","award","rise","promotion","marriage","children","son","progeny"]
INAUSPICIOUS_KW= ["poverty","death","disease","loss","grief","inauspicious","bad","sorrow",
                   "poor","pain","danger","trouble","fear","imprisonment","exile","separation",
                   "divorce","downfall","disgrace","scandal","ill health","accident","misery"]

def rule_valence(text):
    t = text.lower()
    a = sum(1 for k in AUSPICIOUS_KW if k in t)
    i = sum(1 for k in INAUSPICIOUS_KW if k in t)
    if a > i: return "auspicious"
    if i > a: return "inauspicious"
    return "neutral"

def get_mutual_relationship(sign1, sign2):
    if sign1 not in SIGN_NAMES or sign2 not in SIGN_NAMES: return (1, 1)
    idx1, idx2 = SIGN_NAMES.index(sign1), SIGN_NAMES.index(sign2)
    return (((idx2 - idx1) % 12) + 1, ((idx1 - idx2) % 12) + 1)

FILMS = [
    {"num": 1,  "name": "Naalaiya Theerpu",        "date": "1992-12-04", "status": "Flop",        "valence": "inauspicious"},
    {"num": 2,  "name": "Sendhoorapandi",           "date": "1993-12-24", "status": "Hit",         "valence": "auspicious"},
    {"num": 3,  "name": "Rasigan",                  "date": "1994-07-08", "status": "Hit",         "valence": "auspicious"},
    {"num": 4,  "name": "Deva",                     "date": "1995-02-14", "status": "Hit",         "valence": "auspicious"},
    {"num": 5,  "name": "Rajavin Parvaiyile",       "date": "1995-08-04", "status": "Flop",        "valence": "inauspicious"},
    {"num": 6,  "name": "Vishnu",                   "date": "1995-08-18", "status": "Flop",        "valence": "inauspicious"},
    {"num": 7,  "name": "Chandralekha",             "date": "1995-10-23", "status": "Flop",        "valence": "inauspicious"},
    {"num": 8,  "name": "Coimbatore Mapillai",      "date": "1996-01-15", "status": "Hit",         "valence": "auspicious"},
    {"num": 9,  "name": "Poove Unakkaga",           "date": "1996-02-15", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 10, "name": "Vasantha Vasal",           "date": "1996-03-15", "status": "Flop",        "valence": "inauspicious"},
    {"num": 11, "name": "Maanbumigu Maanavan",      "date": "1996-04-12", "status": "Flop",        "valence": "inauspicious"},
    {"num": 12, "name": "Selva",                    "date": "1996-12-05", "status": "Flop",        "valence": "inauspicious"},
    {"num": 13, "name": "Kaalamellam Kaathiruppen", "date": "1997-01-14", "status": "Flop",        "valence": "inauspicious"},
    {"num": 14, "name": "Love Today",               "date": "1997-05-09", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 15, "name": "Once More",                "date": "1997-07-04", "status": "Hit",         "valence": "auspicious"},
    {"num": 16, "name": "Nerrukku Ner",             "date": "1997-09-06", "status": "Hit",         "valence": "auspicious"},
    {"num": 17, "name": "Kadhalukku Mariyadhai",    "date": "1997-12-19", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 18, "name": "Ninaithen Vandhai",        "date": "1998-04-10", "status": "Hit",         "valence": "auspicious"},
    {"num": 19, "name": "Priyamudan",               "date": "1998-06-12", "status": "Hit",         "valence": "auspicious"},
    {"num": 20, "name": "Nilaave Vaa",              "date": "1998-08-14", "status": "Flop",        "valence": "inauspicious"},
    {"num": 21, "name": "Thulladha Manamum Thullum","date": "1999-01-29", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 22, "name": "Endrendrum Kadhal",        "date": "1999-03-05", "status": "Flop",        "valence": "inauspicious"},
    {"num": 23, "name": "Nenjinile",                "date": "1999-06-25", "status": "Flop",        "valence": "inauspicious"},
    {"num": 24, "name": "Minsara Kanna",            "date": "1999-09-09", "status": "Flop",        "valence": "inauspicious"},
    {"num": 25, "name": "Kannukkul Nilavu",         "date": "2000-01-14", "status": "Flop",        "valence": "inauspicious"},
    {"num": 26, "name": "Kushi",                    "date": "2000-05-19", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 27, "name": "Priyamaanavale",           "date": "2000-10-26", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 28, "name": "Friends",                  "date": "2001-01-14", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 29, "name": "Badri",                    "date": "2001-04-12", "status": "Hit",         "valence": "auspicious"},
    {"num": 30, "name": "Shahjahan",                "date": "2001-11-14", "status": "Flop",        "valence": "inauspicious"},
    {"num": 31, "name": "Thamizhan",                "date": "2002-04-12", "status": "Flop",        "valence": "inauspicious"},
    {"num": 32, "name": "Youth",                    "date": "2002-07-19", "status": "Hit",         "valence": "auspicious"},
    {"num": 33, "name": "Bagavathi",                "date": "2002-11-04", "status": "Hit",         "valence": "auspicious"},
    {"num": 34, "name": "Vaseegara",                "date": "2003-01-15", "status": "Flop",        "valence": "inauspicious"},
    {"num": 35, "name": "Pudhiya Geethai",          "date": "2003-05-08", "status": "Flop",        "valence": "inauspicious"},
    {"num": 36, "name": "Thirumalai",               "date": "2003-10-24", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 37, "name": "Udhaya",                   "date": "2004-03-26", "status": "Flop",        "valence": "inauspicious"},
    {"num": 38, "name": "Ghilli",                   "date": "2004-04-17", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 39, "name": "Madurey",                  "date": "2004-08-29", "status": "Hit",         "valence": "auspicious"},
    {"num": 40, "name": "Thirupaachi",              "date": "2005-01-14", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 41, "name": "Sachien",                  "date": "2005-04-14", "status": "Hit",         "valence": "auspicious"},
    {"num": 42, "name": "Sivakasi",                 "date": "2005-11-01", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 43, "name": "Aathi",                    "date": "2006-01-15", "status": "Flop",        "valence": "inauspicious"},
    {"num": 44, "name": "Pokkiri",                  "date": "2007-01-12", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 45, "name": "Azhagiya Tamil Magan",     "date": "2007-11-08", "status": "Flop",        "valence": "inauspicious"},
    {"num": 46, "name": "Kuruvi",                   "date": "2008-05-03", "status": "Flop",        "valence": "inauspicious"},
    {"num": 47, "name": "Pandhayam",                "date": "2008-09-19", "status": "Flop",        "valence": "inauspicious"},
    {"num": 48, "name": "Villu",                    "date": "2009-01-12", "status": "Flop",        "valence": "inauspicious"},
    {"num": 49, "name": "Vettaikaaran",             "date": "2009-12-18", "status": "Hit",         "valence": "auspicious"},
    {"num": 50, "name": "Sura",                     "date": "2010-04-30", "status": "Flop",        "valence": "inauspicious"},
    {"num": 51, "name": "Kaavalan",                 "date": "2011-01-15", "status": "Hit",         "valence": "auspicious"},
    {"num": 52, "name": "Velayudham",               "date": "2011-10-26", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 53, "name": "Nanban",                   "date": "2012-01-12", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 54, "name": "Thuppakki",                "date": "2012-11-13", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 55, "name": "Thalaivaa",                "date": "2013-08-09", "status": "Flop",        "valence": "inauspicious"},
    {"num": 56, "name": "Jilla",                    "date": "2014-01-10", "status": "Hit",         "valence": "auspicious"},
    {"num": 57, "name": "Kaththi",                  "date": "2014-10-22", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 58, "name": "Puli",                     "date": "2015-10-01", "status": "Flop",        "valence": "inauspicious"},
    {"num": 59, "name": "Theri",                    "date": "2016-04-14", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 60, "name": "Bairavaa",                 "date": "2017-01-12", "status": "Hit",         "valence": "auspicious"},
    {"num": 61, "name": "Mersal",                   "date": "2017-10-18", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 62, "name": "Sarkar",                   "date": "2018-11-06", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 63, "name": "Bigil",                    "date": "2019-10-25", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 64, "name": "Master",                   "date": "2021-01-13", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 65, "name": "Beast",                    "date": "2022-04-13", "status": "Hit",         "valence": "auspicious"},
    {"num": 66, "name": "Varisu",                   "date": "2023-01-11", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 67, "name": "Leo",                      "date": "2023-10-19", "status": "Blockbuster", "valence": "auspicious"},
    {"num": 68, "name": "The Greatest of All Time", "date": "2024-09-05", "status": "Blockbuster", "valence": "auspicious"},
]


async def main():
    corpus = get_corpus()
    vijay_birth = BirthData(year=1974, month=6, day=22, time="12:00",
                             lat=13.0827, lon=80.2707, focus="general")
    chart = await jathagam(vijay_birth)
    pos = chart.get("all_planet_positions", {})

    lagna_str = chart.get("lagnam", "Kanni").split(" ")[0]
    lagna_idx = SIGN_NAMES.index(lagna_str) if lagna_str in SIGN_NAMES else 5

    natal_signs, natal_longitudes = {}, {}
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        if p in pos:
            natal_signs[p] = pos[p]["rasi"].split(" ")[0]
            natal_longitudes[p] = pos[p]["longitude"]

    moon_lon = pos["Moon"]["longitude"]
    moon_sign_idx = int(moon_lon / 30)
    natal_pos_7 = {p: pos[p]["longitude"] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    low_level_chart = {
        "positions": {"Moon": {"lon": moon_lon, "lon_abs": moon_lon}},
        "birth": {"year": 1974, "month": 6, "day": 22, "hour": 12, "min": 0}
    }

    # Ashtakavarga
    class _AVChart:
        def __init__(self, lagna_lon, positions):
            self.lagna_lon = lagna_lon
            self.positions = positions
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd_birth = swe.julday(1974, 6, 22, 12.0 - 5.5)
    asc = swe.houses_ex(jd_birth, 13.0827, 80.2707, b"P")[0][0]
    asc_sid = (asc - swe.get_ayanamsa_ut(jd_birth)) % 360
    av_positions = {p: natal_longitudes[p] for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]}
    av_chart = _AVChart(asc_sid, av_positions)
    bav = bhinna_ashtakavarga(av_chart)
    sav = sarva_ashtakavarga(av_chart)

    # ─── Identify all misses and their "conflict pairs" ───────────────────
    print("\n" + "=" * 120)
    print("  DEEP FORENSIC ANALYSIS OF ALL 17 MISSES")
    print("  Finding which films share the SAME Dasha-Bhukti and have OPPOSITE outcomes")
    print("=" * 120)

    s_w, in_w, ma_w, self_w, conj_w = 0.20, 0.65, 0.75, 0.85, 0.75

    all_results = []
    for f in FILMS:
        dt_obj = datetime.strptime(f["date"], "%Y-%m-%d")
        active = current_dasha(low_level_chart, dt_obj)
        md = active.get("md", {}).get("md", "Unknown")
        ad = active.get("ad", {}).get("ad", "Unknown")
        pd_lord = active.get("pd", {}).get("pd", "Unknown")

        pd_func = get_functional_nature(lagna_str, pd_lord)
        pd_aus, pd_ina = 1.0, 1.0
        if pd_func == "MALEFIC": pd_aus, pd_ina = 0.65, 1.35
        elif pd_func == "BENEFIC": pd_aus, pd_ina = 1.35, 0.65

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
        if rel in [(6, 8), (8, 6)]: rapm_a *= s_w; rapm_i *= (2.0 - s_w)
        if md == ad: rapm_a *= self_w; rapm_i *= (2.0 - self_w)
        inimical_pairs = [("Mercury","Sun"),("Mercury","Mars"),("Mercury","Ketu"),
                          ("Venus","Sun"),("Venus","Moon"),("Venus","Rahu"),
                          ("Ketu","Venus"),("Ketu","Sun"),("Ketu","Moon")]
        if (md, ad) in inimical_pairs or (ad, md) in inimical_pairs:
            rapm_a *= in_w; rapm_i *= (2.0 - in_w)
        if ad in ["Mars", "Sun", "Jupiter"]:
            rapm_a *= ma_w; rapm_i *= (2.0 - ma_w)
        if md == "Mercury" and ad in ["Sun", "Saturn"]:
            rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)
        if ad == "Venus" and md == "Mercury":
            rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)
        if ad == "Mars" and md == "Mercury":
            rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)

        rules = corpus.get_dasha_rules(md, ad, limit=12)
        aus_c = sum(1 for r in rules if rule_valence(r.text) == "auspicious")
        ina_c = sum(1 for r in rules if rule_valence(r.text) == "inauspicious")
        base_aus = aus_c * gf * pd_aus * rapm_a
        base_ina = ina_c * (1.0/gf) * pd_ina * rapm_i

        predicted = "neutral"
        if base_aus > base_ina + 0.15: predicted = "auspicious"
        elif base_ina > base_aus + 0.15: predicted = "inauspicious"
        is_hit = predicted == f["valence"]

        # Extra transit data
        jup_pos, _ = swe.calc_ut(jd_ut, swe.JUPITER, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        jup_sign = int((jup_pos[0] % 360) // 30)
        sat_pos, _ = swe.calc_ut(jd_ut, swe.SATURN, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        sat_sign = int((sat_pos[0] % 360) // 30)
        rahu_pos, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
        rahu_sign = int((rahu_pos[0] % 360) // 30)

        jup_from_moon = ((jup_sign - moon_sign_idx) % 12) + 1
        sat_from_moon = ((sat_sign - moon_sign_idx) % 12) + 1
        jup_from_lagna = ((jup_sign - lagna_idx) % 12) + 1
        sat_from_lagna = ((sat_sign - lagna_idx) % 12) + 1
        rahu_from_lagna = ((rahu_sign - lagna_idx) % 12) + 1

        all_results.append({
            "film": f, "md": md, "ad": ad, "pd": pd_lord,
            "base_aus": base_aus, "base_ina": base_ina,
            "predicted": predicted, "is_hit": is_hit,
            "gf": gf, "pd_func": pd_func,
            "jup_sign": SIGN_NAMES[jup_sign], "sat_sign": SIGN_NAMES[sat_sign],
            "jup_from_moon": jup_from_moon, "sat_from_moon": sat_from_moon,
            "jup_from_lagna": jup_from_lagna, "sat_from_lagna": sat_from_lagna,
            "rahu_from_lagna": rahu_from_lagna,
            "jup_bav": bav["Jupiter"][jup_sign], "sat_bav": bav["Saturn"][sat_sign],
            "sav_jup_sign": sav[jup_sign], "sav_sat_sign": sav[sat_sign],
        })

    # ─── Print all misses with forensic detail ────────────────────────────
    misses = [r for r in all_results if not r["is_hit"]]
    print(f"\n  Total Misses: {len(misses)}\n")

    # Group misses by MD-AD
    from collections import defaultdict
    miss_groups = defaultdict(list)
    for m in misses:
        miss_groups[f"{m['md']}-{m['ad']}"].append(m)

    for md_ad, group in sorted(miss_groups.items()):
        print(f"\n  ┌─ MISS GROUP: {md_ad} ({len(group)} films) ─────────────────────────────")

        # Find all films with same MD-AD (hits + misses)
        same_period = [r for r in all_results if f"{r['md']}-{r['ad']}" == md_ad]

        for r in same_period:
            f = r["film"]
            tag = "★ MISS" if not r["is_hit"] else "  hit "
            print(f"  │ {tag} #{f['num']:<3} {f['name']:<25} {f['date']}  {f['status']:<12} "
                  f"PD={r['pd']:<8} GF={r['gf']:.2f}  PD-fn={r['pd_func']:<8} "
                  f"Aus/Ina={r['base_aus']:.1f}/{r['base_ina']:.1f}  "
                  f"Ju@H{r['jup_from_lagna']}({r['jup_bav']}b) Sa@H{r['sat_from_lagna']}({r['sat_bav']}b) "
                  f"Ra@H{r['rahu_from_lagna']}")

        # Analysis: what differentiates hit from miss?
        hits_in_group = [r for r in same_period if r["is_hit"]]
        misses_in_group = [r for r in same_period if not r["is_hit"]]

        if hits_in_group and misses_in_group:
            print(f"  │")
            print(f"  │ DIFFERENTIATORS (what changes between hit films and miss films):")

            # PD differences
            hit_pds = set(r["pd"] for r in hits_in_group)
            miss_pds = set(r["pd"] for r in misses_in_group)
            if hit_pds != miss_pds:
                print(f"  │   PD Lord: Hits use {hit_pds}, Misses use {miss_pds}")

            # Gochara differences
            hit_gfs = [r["gf"] for r in hits_in_group]
            miss_gfs = [r["gf"] for r in misses_in_group]
            print(f"  │   Gochara Factor: Hits avg={sum(hit_gfs)/len(hit_gfs):.2f}, Misses avg={sum(miss_gfs)/len(miss_gfs):.2f}")

            # Jupiter position
            hit_jup_h = [r["jup_from_lagna"] for r in hits_in_group]
            miss_jup_h = [r["jup_from_lagna"] for r in misses_in_group]
            print(f"  │   Jupiter House: Hits={hit_jup_h}, Misses={miss_jup_h}")

            # Saturn position
            hit_sat_h = [r["sat_from_lagna"] for r in hits_in_group]
            miss_sat_h = [r["sat_from_lagna"] for r in misses_in_group]
            print(f"  │   Saturn House:  Hits={hit_sat_h}, Misses={miss_sat_h}")

            # Rahu position
            hit_rahu = [r["rahu_from_lagna"] for r in hits_in_group]
            miss_rahu = [r["rahu_from_lagna"] for r in misses_in_group]
            print(f"  │   Rahu House:    Hits={hit_rahu}, Misses={miss_rahu}")

        elif not hits_in_group:
            print(f"  │   → ALL films in this period are misses (no hit counterpart to compare)")
            print(f"  │   → Need: Override the period-level prediction entirely")
        else:
            print(f"  │   → ALL films in this period are hits (no miss counterpart)")

        print(f"  └─────────────────────────────────────────────────────────────")

    # Summary
    print(f"\n\n  ═══ CONFLICT PAIRS SUMMARY ═══")
    print(f"  These are MD-AD periods where BOTH hits and misses exist:")
    conflict_count = 0
    for md_ad in miss_groups:
        same_period = [r for r in all_results if f"{r['md']}-{r['ad']}" == md_ad]
        has_hit = any(r["is_hit"] for r in same_period)
        has_miss = any(not r["is_hit"] for r in same_period)
        if has_hit and has_miss:
            conflict_count += 1
            hit_films = [r["film"]["name"] for r in same_period if r["is_hit"]]
            miss_films = [r["film"]["name"] for r in same_period if not r["is_hit"]]
            print(f"  {md_ad}: Hits={hit_films}  ←→  Misses={miss_films}")

    solo_misses = []
    for md_ad, group in miss_groups.items():
        same_period = [r for r in all_results if f"{r['md']}-{r['ad']}" == md_ad]
        if not any(r["is_hit"] for r in same_period):
            for m in group:
                solo_misses.append(m)

    print(f"\n  Conflict periods (same MD-AD, mixed outcomes): {conflict_count}")
    print(f"  Solo miss periods (all films in period are misses): {len(solo_misses)}")
    print(f"  → Conflict pairs need PD/Transit differentiation")
    print(f"  → Solo misses need period-level rule correction")


if __name__ == "__main__":
    asyncio.run(main())
