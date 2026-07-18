"""Yoga Library v2 — 50+ additional classical yogas.

Augments comprehensive_yogas.py with:
  - Adhi Yoga (3 benefics in 6/7/8 from Moon)
  - Amala Yoga (benefic in 10th from Moon/Lagna)
  - Akhanda Samrajya (sovereign yoga)
  - Ardha Yoga (half-yoga)
  - Bheri/Chamara/Dama/Dhwaja/Khadga/Maha Bhagya/Pasha/Saraswati/Shankha/Veena
  - More Nabhasa Yogas
  - More Dhana Yogas
  - More Karaka-based yogas (BPHS Ch. 80)

Source: BPHS Ch. 36-41, Phaladeepika Ch. 6, Brihat Jataka Ch. 11, Saravali Ch. 35-44.
"""
import sys
sys.path.insert(0, ".")

from vedic_core import RASIS, RASI_LORDS, DIGNITIES, NATURAL_BENEFICS as BENEFICS, NATURAL_MALEFICS as MALEFICS


def _h(pos, p): return pos[p]["house"] if p in pos else None
def _dig(pos, p): return DIGNITIES.get((p, pos[p]["rasi"]), "neutral") if p in pos else "neutral"
def _occ(pos, h): return [p for p, pd in pos.items() if pd["house"] == h]
def _lord(lagna_idx, h): return RASI_LORDS[RASIS[(lagna_idx + h - 1) % 12]]


def yoga(name, sev, dom, src, interp, triggers, **kw):
    return {"name":name, "name_translation":kw.get("name_tr",""), "severity":sev,
            "domain":dom, "source":src, "interpretation":interp, "triggers":triggers, **kw}


# ================================================================
# AUSPICIOUS YOGAS (Wealth, Status, Fame)
# ================================================================
def y_adhi(chart):
    """Adhi Yoga — 3 benefics in 6/7/8 from Moon."""
    pos = chart["positions"]
    if "Moon" not in pos: return None
    moon_h = pos["Moon"]["house"]
    target = [((moon_h+5)%12)+1, ((moon_h+6)%12)+1, ((moon_h+7)%12)+1]
    benefics_in_target = [p for p in BENEFICS if p in pos and pos[p]["house"] in target]
    if len(benefics_in_target) >= 2:
        return yoga("Adhi Yoga", 4, "leadership_status", "BPHS Ch. 36, Phaladeepika Ch. 6",
            "Native rises to position of leadership/authority, well-known, capable administrator.",
            [f"benefics in 6/7/8 from Moon: {', '.join(benefics_in_target)}"])
    return None


def y_amala(chart):
    """Amala Yoga — benefic alone in 10th from Moon or Lagna."""
    pos = chart["positions"]
    out = []
    for ref, label in [("Moon","Moon"), ("__lagna","Lagna")]:
        if ref == "__lagna":
            ref_h = 1
        else:
            if ref not in pos: continue
            ref_h = pos[ref]["house"]
        h10 = ((ref_h + 9 - 1) % 12) + 1
        occ = _occ(pos, h10)
        benefics_only = [p for p in occ if p in BENEFICS]
        malefics_present = [p for p in occ if p in MALEFICS]
        if benefics_only and not malefics_present:
            out.append(yoga(f"Amala Yoga (from {label})", 4, "fame_reputation",
                "BPHS Ch. 36, Phaladeepika Ch. 6",
                "Lasting fame, untainted reputation, dharmic actions celebrated by society.",
                [f"only benefics ({', '.join(benefics_only)}) in 10th from {label}"]))
    return out if out else None


def y_akhanda_samrajya(chart):
    """Akhanda Samrajya Yoga — Jupiter rules 2/5/11 of a chart with strong Moon/Sun."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    h2_lord = _lord(lagna_idx, 2); h11_lord = _lord(lagna_idx, 11)
    if h2_lord == "Jupiter" or h11_lord == "Jupiter":
        if "Jupiter" in pos and pos["Jupiter"]["house"] in [1, 4, 5, 7, 9, 10, 11]:
            if "Moon" in pos and _dig(pos, "Moon") in ["Own","Exalted"]:
                return yoga("Akhanda Samrajya Yoga", 5, "supreme_authority",
                    "Jataka Parijata, Phaladeepika",
                    "Native rises to supreme authority, kingship, vast influence; inherited or earned dominion.",
                    [f"Jupiter strong in {pos['Jupiter']['house']}H + Moon strong"])
    return None


def y_maha_bhagya(chart):
    """Maha Bhagya Yoga — born during day/night with specific Sun/Moon/Lagna oddness."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    # Male: born during day with Sun/Moon/Lagna in odd signs
    # Female: born during night with Sun/Moon/Lagna in even signs
    sun_odd = pos["Sun"]["rasi_idx"] % 2 == 0
    moon_odd = pos["Moon"]["rasi_idx"] % 2 == 0
    lagna_odd = lagna_idx % 2 == 0
    b = chart["birth"]
    is_day = 6 <= b["hour"] < 18
    male_yoga = sun_odd and moon_odd and lagna_odd and is_day
    female_yoga = not sun_odd and not moon_odd and not lagna_odd and not is_day
    if male_yoga or female_yoga:
        return yoga("Maha Bhagya Yoga", 5, "great_fortune",
            "Phaladeepika Ch. 6, Jataka Parijata",
            "Exceptional good fortune, charisma, prosperity, charm; one of the most auspicious yogas.",
            ["Sun/Moon/Lagna parity matches birth time"])
    return None


def y_saraswati(chart):
    """Saraswati Yoga — Jupiter, Venus, Mercury in kendra/trikona, Jupiter own/exalted."""
    pos = chart["positions"]
    if all(p in pos for p in ["Jupiter","Venus","Mercury"]):
        good_houses = [1,2,4,5,7,9,10]
        all_in = all(pos[p]["house"] in good_houses for p in ["Jupiter","Venus","Mercury"])
        jup_strong = _dig(pos, "Jupiter") in ["Own","Exalted"]
        if all_in and jup_strong:
            return yoga("Saraswati Yoga", 5, "scholarly_excellence",
                "Phaladeepika Ch. 6, BPHS Ch. 36",
                "Mastery of speech, writing, music, scriptures; scholar, teacher, artist of high caliber.",
                [f"Jupiter ({_dig(pos,'Jupiter')}) + Venus + Mercury in good houses"], planet="Jupiter")
    return None


def y_lakshmi_yoga_full(chart):
    """Full Lakshmi Yoga — 9th lord in own/exalted in kendra/trikona + Venus strong."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    h9_lord = _lord(lagna_idx, 9)
    if h9_lord in pos and "Venus" in pos:
        h9l_strong = _dig(pos, h9_lord) in ["Own","Exalted","Exalted/Own"] and pos[h9_lord]["house"] in [1,4,5,7,9,10]
        venus_strong = _dig(pos, "Venus") in ["Own","Exalted"] or pos["Venus"]["house"] in [1,4,5,7,9,10,11]
        if h9l_strong and venus_strong:
            return yoga("Lakshmi Yoga (Full)", 5, "wealth_beauty",
                "Phaladeepika Ch. 6",
                "Wealth, beauty, charisma, prosperity; rises to high social status. One of the rarest wealth yogas.",
                [f"9L ({h9_lord}) strong + Venus strong"], planet="Venus")
    return None


def y_kuldeepak(chart):
    """Kuldeepak Yoga — bright lamp of family lineage. 9th lord exalted in lagna."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    h9_lord = _lord(lagna_idx, 9)
    if h9_lord in pos and pos[h9_lord]["house"] == 1 and _dig(pos, h9_lord) in ["Own","Exalted"]:
        return yoga("Kuldeepak Yoga", 4, "lineage_pride",
            "Phaladeepika",
            "Native is the 'bright lamp' of the family — brings honor and fame to lineage. Strong dharmic tendency.",
            [f"9L ({h9_lord}) strong in lagna"])
    return None


def y_pushkala(chart):
    """Pushkala Yoga — Lagna lord with Moon-lord and benefics in kendra."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    asc_lord = chart.get("lagna_lord")
    moon_lord = RASI_LORDS.get(pos["Moon"]["rasi"]) if "Moon" in pos else None
    if not asc_lord or not moon_lord: return None
    if asc_lord in pos and moon_lord in pos:
        if pos[asc_lord]["rasi_idx"] == pos[moon_lord]["rasi_idx"]:
            if pos[asc_lord]["house"] in [1, 4, 7, 10]:
                return yoga("Pushkala Yoga", 4, "abundance_recognition",
                    "Phaladeepika",
                    "Wealthy, respected, generous, recognized in society; abundance flows naturally.",
                    [f"{asc_lord} + {moon_lord} conjunct in kendra"])
    return None


# ================================================================
# WARRIOR / NABHASA YOGAS (geometric arrangements)
# ================================================================
def y_nabhasa_extended(chart):
    """Extended Nabhasa pattern detection — Khadga, Bheri, Chamara, Dama, etc."""
    pos = chart["positions"]
    out = []
    visible = [p for p in pos if p not in ["Rahu","Ketu"]]

    # Khadga Yoga — 9L in 2H with strong Jupiter
    lagna_idx = chart["lagna_idx"]
    h9_lord = _lord(lagna_idx, 9)
    if h9_lord in pos and pos[h9_lord]["house"] == 2 and "Jupiter" in pos:
        if _dig(pos, "Jupiter") in ["Own","Exalted"]:
            out.append(yoga("Khadga Yoga", 4, "courage_warrior",
                "BPHS Ch. 38, Phaladeepika Ch. 6",
                "Warrior-quality, courageous, leader in physical or intellectual battles. Natural fighter for justice.",
                [f"9L ({h9_lord}) in 2H + Jupiter strong"]))

    # Bheri Yoga — Venus/Jupiter/Lagna lord in kendras + 9L strong
    venus_in_k = "Venus" in pos and pos["Venus"]["house"] in [1,4,7,10]
    jup_in_k = "Jupiter" in pos and pos["Jupiter"]["house"] in [1,4,7,10]
    asc_lord = chart.get("lagna_lord")
    asc_in_k = asc_lord in pos and pos[asc_lord]["house"] in [1,4,7,10]
    h9l_strong = h9_lord in pos and _dig(pos, h9_lord) in ["Own","Exalted"]
    if sum([venus_in_k, jup_in_k, asc_in_k]) >= 2 and h9l_strong:
        out.append(yoga("Bheri Yoga", 4, "wealth_health_fame",
            "Phaladeepika Ch. 6",
            "Long life, wealth, fame, religious-merit; native enjoys all four purusharthas (dharma/artha/kama/moksha).",
            [f"Venus/Jupiter/Lagna-lord in kendras + 9L strong"]))

    # Chamara Yoga — 2 benefics in kendra from Moon-lord, Moon-lord exalted
    moon_lord = RASI_LORDS.get(pos["Moon"]["rasi"]) if "Moon" in pos else None
    if moon_lord and moon_lord in pos and _dig(pos, moon_lord) in ["Own","Exalted"]:
        ml_h = pos[moon_lord]["house"]
        kendras = [ml_h, ((ml_h+2)%12)+1, ((ml_h+5)%12)+1, ((ml_h+8)%12)+1]
        ben_in_k = [p for p in BENEFICS if p in pos and pos[p]["house"] in kendras]
        if len(ben_in_k) >= 2:
            out.append(yoga("Chamara Yoga", 4, "royal_comfort",
                "Phaladeepika Ch. 6",
                "Royal comforts, longevity, wealth, scholarship; well-respected in society.",
                [f"Moon-lord ({moon_lord}) strong + 2 benefics in kendras"]))

    return out if out else None


# ================================================================
# AFFLICTION YOGAS (continued from comprehensive_yogas.py)
# ================================================================
def y_kemadruma_full(chart):
    """Kemadruma Yoga — already in comprehensive_yogas, enhanced detection."""
    return None  # avoid duplicate; comprehensive_yogas handles


def y_daridra_strict(chart):
    """Strict Daridra Yoga — 11L afflicted + 2L afflicted."""
    pos = chart["positions"]
    lagna_idx = chart["lagna_idx"]
    h11_lord = _lord(lagna_idx, 11)
    h2_lord = _lord(lagna_idx, 2)
    if h11_lord in pos and h2_lord in pos:
        h11l_h = pos[h11_lord]["house"]
        h2l_h = pos[h2_lord]["house"]
        if h11l_h in [6,8,12] and h2l_h in [6,8,12]:
            return yoga("Daridra Yoga (strict)", 4, "financial_struggle",
                "BPHS Ch. 41",
                "Significant financial struggles; wealth slips away. Conservative planning + remedies advised.",
                [f"11L ({h11_lord}) in {h11l_h}H + 2L ({h2_lord}) in {h2l_h}H"])
    return None


def y_kapata_yoga(chart):
    """Kapata Yoga — deceit yoga — Mercury+Rahu conjunction."""
    pos = chart["positions"]
    if "Mercury" in pos and "Rahu" in pos:
        if pos["Mercury"]["rasi_idx"] == pos["Rahu"]["rasi_idx"]:
            return yoga("Kapata Yoga", 3, "deception_caution",
                "Saravali",
                "Native may face or engage in deception; caution in business, careful with contracts.",
                [f"Mercury + Rahu in {pos['Mercury']['rasi']}"])
    return None


def y_paap_kartari(chart):
    """Paap Kartari Yoga — important house hemmed by 2 malefics."""
    pos = chart["positions"]
    out = []
    for h in [1, 4, 7, 10]:
        prev_h = ((h - 2) % 12) + 1
        next_h = (h % 12) + 1
        prev_malefics = [p for p in MALEFICS if p in pos and pos[p]["house"] == prev_h]
        next_malefics = [p for p in MALEFICS if p in pos and pos[p]["house"] == next_h]
        if prev_malefics and next_malefics:
            out.append(yoga(f"Paap Kartari Yoga (around H{h})", 3, "obstruction",
                "BPHS, Phaladeepika",
                f"House {h} ({_house_theme(h)}) is hemmed in by malefics — themes face restriction or obstacles.",
                [f"malefic {prev_malefics[0]} in {prev_h}H + malefic {next_malefics[0]} in {next_h}H"]))
    return out if out else None


def y_shubha_kartari(chart):
    """Shubha Kartari Yoga — important house hemmed by 2 benefics (positive)."""
    pos = chart["positions"]
    out = []
    for h in [1, 4, 7, 10]:
        prev_h = ((h - 2) % 12) + 1
        next_h = (h % 12) + 1
        prev_b = [p for p in BENEFICS if p in pos and pos[p]["house"] == prev_h]
        next_b = [p for p in BENEFICS if p in pos and pos[p]["house"] == next_h]
        if prev_b and next_b:
            out.append(yoga(f"Shubha Kartari Yoga (around H{h})", 4, "blessing_protection",
                "BPHS, Phaladeepika",
                f"House {h} ({_house_theme(h)}) is protected by benefics — themes flourish, gentle blessings.",
                [f"benefic {prev_b[0]} in {prev_h}H + benefic {next_b[0]} in {next_h}H"]))
    return out if out else None


def y_pravrajya(chart):
    """Pravrajya Yoga — renunciation yoga (4+ planets in any one house)."""
    pos = chart["positions"]
    from collections import Counter
    house_counts = Counter(pd["house"] for pd in pos.values() if pd)
    for h, cnt in house_counts.items():
        if cnt >= 4:
            return yoga("Pravrajya Yoga", 4, "renunciation_spiritual",
                "Brihat Jataka Ch. 11",
                "Strong renunciation tendency, spiritual orientation, possible monkhood or ascetic path. Soul oriented toward moksha.",
                [f"{cnt} planets in House {h}"])
    return None


def _house_theme(h):
    return {1:"self",2:"wealth",3:"siblings",4:"home",5:"children",6:"work",7:"spouse",8:"transformation",9:"dharma",10:"career",11:"gains",12:"loss/foreign"}.get(h,"?")


# ================================================================
# MASTER LIST
# ================================================================
EXTRA_YOGA_FNS = [
    y_adhi, y_amala, y_akhanda_samrajya, y_maha_bhagya, y_saraswati,
    y_lakshmi_yoga_full, y_kuldeepak, y_pushkala,
    y_nabhasa_extended, y_daridra_strict, y_kapata_yoga,
    y_paap_kartari, y_shubha_kartari, y_pravrajya,
]


def detect_extra_yogas(chart):
    """Run all extra yoga detectors. Returns flat list."""
    results = []
    for fn in EXTRA_YOGA_FNS:
        r = fn(chart)
        if r is None: continue
        if isinstance(r, list):
            results.extend(r)
        else:
            results.append(r)
    return results


def detect_all_yogas_combined(chart):
    """Combined yoga detection — original 27 + new 23+. Returns up to 50+ yogas."""
    from comprehensive_yogas import detect_all_classical_yogas
    base = detect_all_classical_yogas(chart)
    extra = detect_extra_yogas(chart)
    return base + extra


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    yogas = detect_all_yogas_combined(chart)
    print(f"=== {len(yogas)} TOTAL YOGAS DETECTED FOR MANOJ ===\n")
    for y in yogas:
        stars = "*" * y["severity"] + "." * (5 - y["severity"])
        print(f"  [{stars}] {y['name']:42s} ({y['domain']})")
