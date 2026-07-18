"""Transit Engine — compute planetary transits for any date past or future.

Uses Swiss Ephemeris (pyswisseph) in Lahiri sidereal mode.
Detects transit-over-natal triggers: Saturn return, Mars on Sun, Rahu on Moon, etc.
"""
import datetime as dt
import swisseph as swe

PLANET_IDS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS,
    "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,
}
from vedic_core import RASIS  # canonical 12 signs

swe.set_sid_mode(swe.SIDM_LAHIRI)


def jd_from_dt(when_dt):
    """Convert datetime to Julian Day (UT)."""
    h = when_dt.hour + when_dt.minute/60.0 + when_dt.second/3600.0
    return swe.julday(when_dt.year, when_dt.month, when_dt.day, h, swe.GREG_CAL)


def transit_positions(when_dt):
    """Returns sidereal (Lahiri) positions of all planets on given date.
    Output: {planet: {"lon": deg, "rasi": str, "rasi_idx": int, "deg": deg_in_sign}}
    """
    jd = jd_from_dt(when_dt)
    out = {}
    flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH
    for name, pid in PLANET_IDS.items():
        x, _ = swe.calc_ut(jd, pid, flag)
        lon = x[0] % 360
        ri = int(lon // 30)
        out[name] = {"lon": lon, "rasi": RASIS[ri], "rasi_idx": ri, "deg": lon - ri*30}
    # Ketu = Rahu + 180
    rahu_lon = out["Rahu"]["lon"]
    ketu_lon = (rahu_lon + 180) % 360
    ki = int(ketu_lon // 30)
    out["Ketu"] = {"lon": ketu_lon, "rasi": RASIS[ki], "rasi_idx": ki, "deg": ketu_lon - ki*30}
    return out


def detect_triggers(natal_chart, when_dt, orb=2.0):
    """Detect transit-over-natal triggers. Returns list of trigger dicts.

    Triggers detected:
      - Conjunction: transit X within `orb` degrees of natal Y (same rasi)
      - Aspect: transit X aspects natal point (using Vedic special aspects)
      - Saturn Return: transit Saturn near natal Saturn
      - Sade Sati: transit Saturn within 30° before/after natal Moon
      - Rahu/Ketu axis hit: transit nodes near natal point
    """
    natal_pos = natal_chart["positions"]
    transits = transit_positions(when_dt)
    triggers = []

    for tp_name, tp_data in transits.items():
        for np_name, np_data in natal_pos.items():
            tp_lon = tp_data["lon"]
            np_lon = np_data.get("lon_abs") or (np_data["rasi_idx"]*30 + np_data["deg"])
            diff = abs((tp_lon - np_lon + 180) % 360 - 180)

            # Conjunction
            if diff <= orb:
                severity = "HIGH" if tp_name in ["Saturn","Mars","Rahu","Ketu"] else "MEDIUM"
                triggers.append({
                    "type": "conjunction",
                    "transit": tp_name,
                    "natal": np_name,
                    "orb": round(diff, 2),
                    "severity": severity,
                    "label": f"transit {tp_name} on natal {np_name} (orb {diff:.1f}°)"
                })

            # Saturn Return special case
            if tp_name == "Saturn" and np_name == "Saturn" and diff <= 3.0:
                triggers.append({
                    "type": "saturn_return",
                    "transit": tp_name,
                    "natal": np_name,
                    "orb": round(diff, 2),
                    "severity": "VERY HIGH",
                    "label": f"Saturn Return — transit Saturn on natal Saturn (orb {diff:.1f}°)"
                })

            # Vedic 7th aspect (opposition) — applies to all planets
            opp_diff = abs(((tp_lon - np_lon - 180) + 180) % 360 - 180)
            if opp_diff <= orb and tp_name in ["Saturn","Mars","Jupiter","Rahu","Ketu"]:
                triggers.append({
                    "type": "opposition",
                    "transit": tp_name,
                    "natal": np_name,
                    "orb": round(opp_diff, 2),
                    "severity": "MEDIUM",
                    "label": f"transit {tp_name} opposing natal {np_name}"
                })

    # Sade Sati check (Saturn transiting 12th, 1st, or 2nd from natal Moon)
    moon_rasi_idx = natal_pos["Moon"]["rasi_idx"]
    sat_rasi_idx = transits["Saturn"]["rasi_idx"]
    sade_sati_houses = [(moon_rasi_idx - 1) % 12, moon_rasi_idx, (moon_rasi_idx + 1) % 12]
    if sat_rasi_idx in sade_sati_houses:
        phase = ["12th from Moon", "On Moon", "2nd from Moon"][sade_sati_houses.index(sat_rasi_idx)]
        triggers.append({
            "type": "sade_sati",
            "transit": "Saturn",
            "natal": "Moon",
            "orb": 0,
            "severity": "HIGH",
            "label": f"Sade Sati — Saturn in {phase} ({RASIS[sat_rasi_idx]})"
        })

    return triggers


if __name__ == "__main__":
    import json
    chart = json.load(open("../charts/manoj_chart.json", encoding="utf-8"))
    test_date = dt.datetime(1996, 8, 25)
    print(f"Transit triggers for Manoj on {test_date.date()}:")
    triggers = detect_triggers(chart, test_date, orb=3.0)
    for t in sorted(triggers, key=lambda x: {"VERY HIGH":0,"HIGH":1,"MEDIUM":2,"LOW":3}.get(x["severity"],99)):
        print(f"  [{t['severity']:9s}] {t['label']}")
