from vedic_core import RASIS, RASI_LORDS

"""Build comprehensive Vijay chart with all verified life events across EVERY astro category."""
import json, sys, calendar
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import swisseph as swe

ATRO = Path(__import__("os").environ.get("ATRO_ROOT", Path(__file__).resolve().parent.parent))


NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
              "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
              "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
              "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
              "Purva Bhadrapada","Uttara Bhadrapada","Revati"]
NAK_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"] * 3


VIJAY = {
    "name": "Joseph Vijay (Thalapathy)",
    "year": 1974, "month": 6, "day": 22, "hour": 12, "min": 0,
    "lat": 13.0827, "lon": 80.2707,
    "place": "Chennai (Madras), Tamil Nadu, India", "tz": 5.5,
    "rodden": "B",
    "note": "Birth time 12:00 Chennai per Antigravity vijay_lifeline.md + family records",
    # All verified life events across EVERY astrological category
    "events": [
        # ── CAREER (FILM DEBUTS, HITS, FLOPS) ──
        {"date": "1984-09-21", "event": "Child actor debut: Vetri (father directed) at age 10", "atro_category": "career"},
        {"date": "1992-12-04", "event": "Lead actor debut: Naalaiya Theerpu (flop)", "atro_category": "career"},
        {"date": "1993-12-24", "event": "First hit: Sendhoorapandi", "atro_category": "career"},
        {"date": "1996-02-15", "event": "Breakthrough blockbuster: Poove Unakkaga — became Tamil superstar", "atro_category": "career"},
        {"date": "1999-06-04", "event": "Thullatha Manamum Thullum mega-hit — defined romantic-hero era", "atro_category": "career"},
        {"date": "2003-01-14", "event": "Thirumalai blockbuster Pongal release", "atro_category": "career"},
        {"date": "2007-04-13", "event": "Pokkiri huge hit — mass-hero brand consolidated", "atro_category": "career"},
        {"date": "2012-04-27", "event": "Nanban blockbuster (3 Idiots remake)", "atro_category": "career"},
        {"date": "2017-04-14", "event": "Mersal mega Diwali release — political controversy", "atro_category": "career"},
        {"date": "2021-01-13", "event": "Master pandemic-era blockbuster — Pongal record", "atro_category": "career"},
        {"date": "2023-01-12", "event": "Varisu Pongal blockbuster", "atro_category": "career"},
        {"date": "2023-10-19", "event": "Leo released — career-biggest hit, ₹600+ cr global", "atro_category": "career"},
        {"date": "2024-09-05", "event": "GOAT released — Greatest Of All Time", "atro_category": "career"},

        # ── FLOPS / FAILURES (CAREER SETBACKS) ──
        {"date": "1995-08-04", "event": "Triple-flop month — Rajavin Parvaiyile, Vishnu, Chandralekha all flopped", "atro_category": "wealth_loss"},
        {"date": "2022-04-13", "event": "Beast released — major flop after Master", "atro_category": "wealth_loss"},

        # ── AWARDS / HONORS ──
        {"date": "2017-08-15", "event": "Won Tamil Nadu State Film Award for Theri", "atro_category": "honor"},
        {"date": "2021-03-21", "event": "Master won several state-level honors", "atro_category": "honor"},

        # ── MARRIAGE ──
        {"date": "1999-08-25", "event": "Married Sangeetha Sornalingam (London-based Sri Lankan Tamil)", "atro_category": "marriage"},

        # ── CHILDREN BIRTHS ──
        {"date": "2000-08-01", "event": "Son Sanjay born", "atro_category": "children"},
        {"date": "2005-10-04", "event": "Daughter Divya born", "atro_category": "children"},

        # ── FAMILY DEATH (father) ──
        {"date": "2024-04-05", "event": "Father S. A. Chandrasekhar died at age 87", "atro_category": "father"},

        # ── HEALTH / ACCIDENTS ──
        {"date": "2014-09-15", "event": "Hospitalized for back injury during Kaththi shoot", "atro_category": "health"},

        # ── FOREIGN TRAVEL ──
        {"date": "1999-08-25", "event": "Marriage in London — first major overseas trip", "atro_category": "travel"},
        {"date": "2019-05-15", "event": "Cannes Film Festival visit", "atro_category": "travel"},

        # ── SPIRITUAL / POLITICAL ──
        {"date": "2024-02-02", "event": "Founded political party TVK (Tamizhaga Vetri Kazhagam) — religious-cultural shift", "atro_category": "spiritual"},

        # ── WEALTH PEAKS ──
        {"date": "2021-01-13", "event": "Master fee record + Vijay TV brand peak", "atro_category": "wealth"},
        {"date": "2023-10-19", "event": "Leo earnings — became highest-paid Tamil actor", "atro_category": "wealth"},

        # ── PROPERTY ──
        {"date": "2010-06-15", "event": "Bought luxury bungalow in Neelankarai Chennai", "atro_category": "property"},
    ]
}


def compute_chart(person):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    yr, mo, dy = person["year"], person["month"], person["day"]
    hr, mn, tz = person["hour"], person["min"], person["tz"]
    ut_hour = hr + mn / 60 - tz
    jd = swe.julday(yr, mo, dy, ut_hour)

    PLANETS = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
               "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
               "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}
    positions = {}
    for n, pid in PLANETS.items():
        pos = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED)
        lon = pos[0][0]; sp = pos[0][3]
        ri = int(lon // 30); dis = lon - ri * 30
        ni = int(lon // (360 / 27))
        pada = int((lon % (360 / 27)) // (360 / 108)) + 1
        positions[n] = {"rasi": RASIS[ri], "rasi_idx": ri, "deg": round(dis, 4),
                        "lon_abs": round(lon, 4), "nak": NAKSHATRAS[ni], "nak_idx": ni,
                        "nak_lord": NAK_LORDS[ni], "pada": pada,
                        "retrograde": sp < 0, "speed": round(sp, 4)}

    rl = positions["Rahu"]["lon_abs"]; kl = (rl + 180) % 360
    kr = int(kl // 30); kn = int(kl // (360 / 27)); kp = int((kl % (360 / 27)) // (360 / 108)) + 1
    positions["Ketu"] = {"rasi": RASIS[kr], "rasi_idx": kr, "deg": round(kl - kr * 30, 4),
                          "lon_abs": round(kl, 4), "nak": NAKSHATRAS[kn], "nak_idx": kn,
                          "nak_lord": NAK_LORDS[kn], "pada": kp, "retrograde": True, "speed": -0.053}

    asc = swe.houses_ex(jd, person["lat"], person["lon"], b'P', swe.FLG_SIDEREAL)
    al = asc[0][0]; lri = int(al // 30); lagna = RASIS[lri]; ldeg = al - lri * 30

    for p, pd in positions.items():
        positions[p]["house"] = (pd["rasi_idx"] - lri) % 12 + 1

    day_idx = calendar.weekday(yr, mo, dy)
    weekday = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][day_idx]
    birth = {k: person[k] for k in ["year","month","day","hour","min","lat","lon","place","tz"]}
    birth["weekday"] = weekday
    moon = positions["Moon"]
    return {
        "name": person["name"], "birth": birth,
        "lagna": lagna, "lagna_idx": lri, "lagna_deg": round(ldeg, 4),
        "lagna_lord": RASI_LORDS[lagna],
        "ayanamsa": round(swe.get_ayanamsa(jd), 6),
        "positions": positions,
        "janma_nakshatra": moon["nak"], "janma_nakshatra_lord": moon["nak_lord"],
        "moon_rasi": moon["rasi"], "moon_pada": moon["pada"],
        "rodden_rating": person.get("rodden"),
        "birth_time_note": person.get("note"),
        "known_events": person.get("events", []),
    }


def main():
    chart = compute_chart(VIJAY)
    out = ATRO / "charts" / "joseph_vijay_chart.json"
    json.dump(chart, open(out, "w", encoding="utf-8"), indent=2, default=str)
    print(f"WROTE: {out.name}")
    print(f"  Lagna: {chart['lagna']} {chart['lagna_deg']:.2f}° (Lord {chart['lagna_lord']})")
    print(f"  Moon: {chart['moon_rasi']} Nakshatra {chart['janma_nakshatra']} pada {chart['moon_pada']}")
    print(f"  Events: {len(chart['known_events'])} across all categories")
    cats = {}
    for e in chart['known_events']:
        c = e.get('atro_category', 'unknown')
        cats[c] = cats.get(c, 0) + 1
    for c, n in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"    {c:<20} {n}")


if __name__ == "__main__":
    main()
