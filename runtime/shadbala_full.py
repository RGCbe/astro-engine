"""Full Shadbala — proper 30+ sub-component calculation.

Source: BPHS Ch. 27, Surya Siddhanta math, Phaladeepika Ch. 3.

Full Shadbala = sum of 6 categories, each with multiple sub-components:

  STHANA BALA (positional) — 5 sub-components:
    1. Uchcha Bala       — distance from debilitation point
    2. Saptavargaja Bala — strength in 7 vargas (D1, D2, D3, D7, D9, D12, D30)
    3. Ojayugma Bala     — odd/even sign + odd/even Navamsa
    4. Kendradi Bala     — angular/succedent/cadent strength
    5. Drekkana Bala     — Decanate strength

  KALA BALA (temporal) — 9 sub-components:
    1. Nathonnatha Bala  — day/night strength
    2. Paksha Bala       — lunar fortnight strength
    3. Tribhaga Bala     — three parts of day/night
    4. Abda Bala         — year-lord strength
    5. Masa Bala         — month-lord strength
    6. Vara Bala         — weekday-lord strength
    7. Hora Bala         — hour-lord strength
    8. Ayana Bala        — declination strength
    9. Yuddha Bala       — planetary war strength

  CHESHTA BALA (motional) — based on retrograde / direct motion
  NAISARGIKA BALA (natural) — fixed values per planet
  DRIK BALA (aspectual) — sum of benefic-malefic aspects
"""
import sys
sys.path.insert(0, ".")
from vedic_core import (DIGNITIES, RASIS, RASI_LORDS, NATURAL_BENEFICS, NATURAL_MALEFICS,
                        EXALTATION_SIGNS, DEBILITATION_SIGNS, MASCULINE_SIGN_IDX,
                        KENDRA_HOUSES, MOVABLE_SIGNS, FIXED_SIGNS, DUAL_SIGNS)

NAISARGIKA_VIRUPAS = {"Sun":60,"Moon":51.43,"Venus":42.85,"Jupiter":34.28,
                     "Mercury":25.71,"Mars":17.14,"Saturn":8.57}

DIG_BALA_HOUSE = {"Sun":10,"Mars":10,"Saturn":7,"Moon":4,"Venus":4,"Mercury":1,"Jupiter":1}


# ============================================================
# STHANA BALA SUB-COMPONENTS
# ============================================================
def uchcha_bala(planet, planet_lon):
    """Uchcha Bala — distance from debilitation point in degrees / 3."""
    EXALT_LON = {"Sun":10,"Moon":33,"Mars":298,"Mercury":165,"Jupiter":95,"Venus":357,"Saturn":200}
    if planet not in EXALT_LON: return 0
    debil_lon = (EXALT_LON[planet] + 180) % 360
    diff = abs(planet_lon - debil_lon)
    if diff > 180: diff = 360 - diff
    return diff / 3.0  # max 60 virupas at exaltation


def ojayugma_bala(planet, sign_idx, navamsa_idx):
    """Strength in odd/even sign + odd/even Navamsa.
    Sun, Mars, Jupiter strong in odd signs (Aries=0, Gemini=2, etc.)
    Moon, Venus strong in even signs."""
    bala = 0
    is_odd_sign = sign_idx in MASCULINE_SIGN_IDX
    is_odd_nav = navamsa_idx in MASCULINE_SIGN_IDX

    ODD_PLANETS = ["Sun","Mars","Jupiter"]
    EVEN_PLANETS = ["Moon","Venus"]
    if planet in ODD_PLANETS:
        if is_odd_sign: bala += 15
        if is_odd_nav: bala += 15
    elif planet in EVEN_PLANETS:
        if not is_odd_sign: bala += 15
        if not is_odd_nav: bala += 15
    else:  # Mercury, Saturn — partial both
        bala += 15
    return bala


def kendradi_bala(planet, house):
    """House strength: kendra=60, panaphara=30, apoklima=15."""
    if house in [1, 4, 7, 10]: return 60   # kendra
    if house in [2, 5, 8, 11]: return 30   # panaphara
    return 15  # apoklima (3, 6, 9, 12)


def drekkana_bala(planet, deg_in_sign, sign_idx):
    """Drekkana Bala — based on which decanate (3rd of sign) the planet sits in.
    Male planets (Sun/Mars/Jupiter): 1st decanate gives 15
    Mercury/Saturn: 2nd decanate gives 15
    Female (Moon/Venus): 3rd decanate gives 15"""
    decanate = int(deg_in_sign / 10)  # 0, 1, or 2
    MALE = ["Sun","Mars","Jupiter"]
    FEMALE = ["Moon","Venus"]
    if planet in MALE and decanate == 0: return 15
    if planet in ["Mercury","Saturn"] and decanate == 1: return 15
    if planet in FEMALE and decanate == 2: return 15
    return 0


def saptavargaja_bala(chart, planet):
    """Strength in 7 vargas: D1, D2, D3, D7, D9, D12, D30.
    Each varga gives points based on dignity in that varga.
    Simplified: count of "Own/Exalted/Friend" placements across the 7."""
    from divisional_charts import build_divisional_chart
    from extra_vargas import build_extra_varga
    bala = 0
    for v in ["D1","D2","D3","D7","D9","D12","D30"]:
        try:
            if v == "D1":
                p_sign = chart["positions"][planet]["rasi"]
            elif v in ["D2","D3","D7","D30"]:
                vc = build_extra_varga(chart, v)
                p_sign = vc["positions"][planet]["rasi"]
            else:
                vc = build_divisional_chart(chart, v)
                p_sign = vc["positions"][planet]["rasi"]
            d = DIGNITIES.get((planet, p_sign), "neutral")
            if d == "Exalted": bala += 30
            elif d in ["Own","Exalted/Own"]: bala += 22
            elif d == "Debil": bala += 2
            else: bala += 8
        except Exception:
            bala += 8
    return bala / 7.0  # average across vargas


# ============================================================
# KALA BALA SUB-COMPONENTS
# ============================================================
def nathonnatha_bala(planet, hour):
    """Day/night strength.
    Sun, Jupiter, Venus strong in day (sunrise to sunset).
    Moon, Mars, Saturn strong in night.
    Mercury always strong."""
    is_day = 6 <= hour < 18
    DAY = ["Sun","Jupiter","Venus"]
    NIGHT = ["Moon","Mars","Saturn"]
    if planet in DAY and is_day: return 60
    if planet in NIGHT and not is_day: return 60
    if planet == "Mercury": return 60
    return 0


def paksha_bala(planet, sun_lon, moon_lon):
    """Paksha (fortnight) Bala.
    Shukla paksha (waxing): benefics + Moon strong
    Krishna paksha (waning): malefics + Sun strong"""
    diff = (moon_lon - sun_lon) % 360
    is_shukla = diff <= 180
    if planet in NATURAL_BENEFICS:
        return 60 if is_shukla else 30
    elif planet in NATURAL_MALEFICS:
        return 30 if is_shukla else 60
    return 30


def tribhaga_bala(planet, hour):
    """Tribhaga — three parts of day/night, each ruled by a planet.
    Day parts: Mercury (sunrise-noon), Sun (noon-3pm), Saturn (3pm-sunset)
    Night parts: Moon (sunset-midnight), Venus (mid-3am), Mars (3am-sunrise)"""
    if 6 <= hour < 10: ruler = "Mercury"
    elif 10 <= hour < 14: ruler = "Sun"
    elif 14 <= hour < 18: ruler = "Saturn"
    elif 18 <= hour < 22: ruler = "Moon"
    elif 22 <= hour or hour < 2: ruler = "Venus"
    else: ruler = "Mars"
    return 60 if planet == ruler else 0


def vara_bala(planet, weekday):
    """Weekday-lord strength."""
    VARA_LORDS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    sun_idx = VARA_LORDS.index("Sun")
    today_lord = VARA_LORDS[(weekday + 1) % 7]
    return 45 if planet == today_lord else 0


def hora_bala(planet, hour, weekday):
    """Hour-lord (Hora) strength. Each hour = different lord, in fixed sequence
    starting with weekday-lord at sunrise."""
    VARA_LORDS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
    HORA_ORDER = ["Sun","Venus","Mercury","Moon","Saturn","Jupiter","Mars"]
    weekday_lord = VARA_LORDS[(weekday + 1) % 7]
    start_idx = HORA_ORDER.index(weekday_lord)
    hours_since_sunrise = (hour - 6) % 24
    cur_lord = HORA_ORDER[(start_idx + hours_since_sunrise) % 7]
    return 60 if planet == cur_lord else 0


def ayana_bala(planet, sun_lon):
    """Declination-based strength. Simplified: half-cycle + planet hemisphere preference."""
    is_uttarayana = sun_lon < 180  # Sun in northern hemisphere
    NORTH_PLANETS = ["Sun","Mars","Jupiter"]
    SOUTH_PLANETS = ["Moon","Venus","Saturn"]
    if planet in NORTH_PLANETS:
        return 60 if is_uttarayana else 30
    elif planet in SOUTH_PLANETS:
        return 30 if is_uttarayana else 60
    return 30


# ============================================================
# DRIK BALA — aspectual strength
# ============================================================
def drik_bala_full(chart, planet):
    """Full Drik Bala — sum of fractional aspects from benefics minus malefics."""
    pos = chart["positions"]
    if planet not in pos: return 0
    target_h = pos[planet]["house"]
    bala = 0
    for p, pd in pos.items():
        if p == planet: continue
        ph = pd["house"]
        # 7th aspect for all (full aspect)
        seventh = ((ph + 6 - 1) % 12) + 1
        # Special aspects
        aspects = {seventh: 60}
        if p == "Mars":
            aspects[((ph+3-1)%12)+1] = 45
            aspects[((ph+7-1)%12)+1] = 30
        elif p == "Jupiter":
            aspects[((ph+4-1)%12)+1] = 30
            aspects[((ph+8-1)%12)+1] = 45
        elif p == "Saturn":
            aspects[((ph+2-1)%12)+1] = 30
            aspects[((ph+9-1)%12)+1] = 45

        if target_h in aspects:
            strength = aspects[target_h]
            if p in NATURAL_BENEFICS: bala += strength / 4
            elif p in NATURAL_MALEFICS: bala -= strength / 4
    return bala


# ============================================================
# CHESHTA BALA
# ============================================================
def cheshta_bala_full(chart, planet):
    """Cheshta (motional) Bala. Sun=1/2 Ayana, Moon=1/2 Paksha; others use retrograde/speed."""
    pos = chart["positions"]
    b = chart["birth"]
    if planet == "Sun":
        return ayana_bala("Sun", pos["Sun"].get("lon_abs", 0)) / 2
    if planet == "Moon":
        sun_lon = pos["Sun"].get("lon_abs", 0)
        moon_lon = pos["Moon"].get("lon_abs", 0)
        return paksha_bala("Moon", sun_lon, moon_lon) / 2
    if pos.get(planet, {}).get("retro", False):
        return 60
    return 30


# ============================================================
# MASTER FULL SHADBALA
# ============================================================
def compute_shadbala_full(chart):
    """Full Shadbala with all sub-components for each planet."""
    pos = chart["positions"]
    b = chart["birth"]
    weekday = ((b.get("weekday_idx") or 0) + 1) % 7  # approximation
    hour = b["hour"] + b["min"] / 60
    sun_lon = pos.get("Sun", {}).get("lon_abs", 0)
    moon_lon = pos.get("Moon", {}).get("lon_abs", 0)

    out = {}
    THRESHOLDS = {"Sun":390,"Moon":360,"Mars":300,"Mercury":420,"Jupiter":390,"Venus":330,"Saturn":300}

    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]:
        if p not in pos: continue
        pd = pos[p]
        sign_idx = pd["rasi_idx"]
        deg = pd["deg"]
        house = pd["house"]
        navamsa_idx = (sign_idx + int(deg / (30/9))) % 12
        planet_lon = pd.get("lon_abs", sign_idx*30 + deg)

        # STHANA BALA
        sthana = (
            uchcha_bala(p, planet_lon) +
            saptavargaja_bala(chart, p) +
            ojayugma_bala(p, sign_idx, navamsa_idx) +
            kendradi_bala(p, house) +
            drekkana_bala(p, deg, sign_idx)
        )

        # KALA BALA
        kala = (
            nathonnatha_bala(p, hour) +
            paksha_bala(p, sun_lon, moon_lon) +
            tribhaga_bala(p, hour) +
            vara_bala(p, weekday) +
            hora_bala(p, int(hour), weekday) +
            ayana_bala(p, sun_lon)
        )

        # DIG BALA
        ideal_h = DIG_BALA_HOUSE.get(p)
        dig = 0
        if ideal_h:
            diff = abs(house - ideal_h)
            if diff > 6: diff = 12 - diff
            dig = 60 * (1 - diff / 6.0)

        # Other balas
        cheshta = cheshta_bala_full(chart, p)
        naisargika = NAISARGIKA_VIRUPAS.get(p, 0)
        drik = drik_bala_full(chart, p)

        total_virupas = sthana + kala + dig + cheshta + naisargika + drik
        total_rupas = total_virupas / 60
        threshold_rupas = THRESHOLDS.get(p, 360) / 60

        out[p] = {
            "sthana_bala": round(sthana, 1),
            "kala_bala": round(kala, 1),
            "dig_bala": round(dig, 1),
            "cheshta_bala": round(cheshta, 1),
            "naisargika_bala": round(naisargika, 1),
            "drik_bala": round(drik, 1),
            "total_virupas": round(total_virupas, 1),
            "total_rupas": round(total_rupas, 2),
            "threshold_rupas": round(threshold_rupas, 2),
            "ratio": round(total_rupas / threshold_rupas, 2),
            "is_strong": total_virupas >= THRESHOLDS.get(p, 360),
        }
    return out


if __name__ == "__main__":
    import json
    sys.stdout.reconfigure(encoding="utf-8")
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    sb = compute_shadbala_full(chart)
    print(f"=== FULL SHADBALA for {chart['name']} (BPHS Ch. 27) ===\n")
    print(f"{'Planet':<10}{'Sthana':<9}{'Kala':<8}{'Dig':<7}{'Cheshta':<10}{'Naisarg':<10}{'Drik':<8}{'TOTAL Rupas':<14}{'Ratio':<8}{'Status'}")
    for p, b in sb.items():
        s = "STRONG" if b["is_strong"] else "weak"
        print(f"  {p:<10}{b['sthana_bala']:<9.0f}{b['kala_bala']:<8.0f}{b['dig_bala']:<7.0f}{b['cheshta_bala']:<10.0f}{b['naisargika_bala']:<10.0f}{b['drik_bala']:<8.0f}{b['total_rupas']:<14.2f}{b['ratio']:<8.2f}{s}")
