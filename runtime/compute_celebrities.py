from vedic_core import RASIS, RASI_LORDS

"""Compute charts for 6 celebrities: Sachin, Amitabh, Modi, Dhoni, AR Rahman, Rekha."""
import json, sys, calendar
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
import swisseph as swe

ATRO = Path(__import__("os").environ.get("ATRO_ROOT", Path(__file__).resolve().parent.parent))
CHARTS_DIR = ATRO / "charts"


NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
              "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
              "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
              "Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha",
              "Purva Bhadrapada","Uttara Bhadrapada","Revati"]
NAK_LORDS = ["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"] * 3


CELEBRITIES = [
    {
        "name": "Sachin Tendulkar",
        "year": 1973, "month": 4, "day": 24,
        "hour": 13, "min": 0,
        "lat": 18.9667, "lon": 72.8333,
        "place": "Mumbai (Dadar), India", "tz": 5.5,
        "rodden": "A",
        "note": "Birth time 13:00 from Dr. Shraddhanand Thakur (delivering doctor), 2013 interview",
        "events": [
            {"date": "1989-11-15", "event": "Test debut vs Pakistan, Karachi — aged 16y 205d"},
            {"date": "1990-08-14", "event": "Maiden Test century (119*) vs England at Old Trafford — aged 17"},
            {"date": "1994-09-09", "event": "First ODI century vs Australia, Colombo"},
            {"date": "1995-05-24", "event": "Married Anjali Mehta in Mumbai"},
            {"date": "2001-03-01", "event": "First to 10,000 ODI runs (139 vs Australia, Indore)"},
            {"date": "2010-02-24", "event": "First-ever ODI double century (200*) vs South Africa, Gwalior"},
            {"date": "2011-04-02", "event": "India won ICC Cricket World Cup — Tendulkar's 6th World Cup"},
            {"date": "2012-03-16", "event": "100th international century vs Bangladesh, Asia Cup"},
            {"date": "2013-11-16", "event": "Played 200th and final Test match — retired from all cricket"},
            {"date": "2014-02-04", "event": "Awarded Bharat Ratna — first sportsperson and youngest ever"},
        ]
    },
    {
        "name": "Amitabh Bachchan",
        "year": 1942, "month": 10, "day": 11,
        "hour": 3, "min": 30,
        "lat": 25.4358, "lon": 81.8463,
        "place": "Allahabad (Prayagraj), India", "tz": 5.5,
        "rodden": "DD",
        "note": "Birth time disputed: 3:30 AM from his autobiography vs ~15:00 from father's autobiography",
        "events": [
            {"date": "1973-06-03", "event": "Married actress Jaya Bhaduri in Mumbai"},
            {"date": "1973-10-01", "event": "Breakthrough in Zanjeer — launched 'Angry Young Man' era"},
            {"date": "1975-08-15", "event": "Sholay released — highest-grossing Indian film for decades"},
            {"date": "1982-07-26", "event": "Near-fatal accident on Coolie sets — splenic rupture, briefly clinically dead"},
            {"date": "1984-12-01", "event": "Elected to Lok Sabha (MP for Allahabad) on Congress ticket"},
            {"date": "1997-01-01", "event": "ABCL declared bankrupt — 55 legal cases, Rs 90 crore debt"},
            {"date": "2000-07-03", "event": "Career comeback: hosted Kaun Banega Crorepati Season 1 — record ratings"},
            {"date": "2018-10-11", "event": "Received Dadasaheb Phalke Award — India's highest film honour"},
            {"date": "2020-07-11", "event": "Hospitalised with COVID-19 at Nanavati Hospital, Mumbai"},
        ]
    },
    {
        "name": "Narendra Modi",
        "year": 1950, "month": 9, "day": 17,
        "hour": 11, "min": 0,
        "lat": 23.7936, "lon": 72.6376,
        "place": "Vadnagar, Gujarat, India", "tz": 5.5,
        "rodden": "DD",
        "note": "Birth time disputed: 11:00 AM (AstroDatabank) vs 9:35 AM (elder brother Amrit Modi, 2014)",
        "events": [
            {"date": "2001-10-07", "event": "Sworn in as Chief Minister of Gujarat (first term)"},
            {"date": "2002-02-27", "event": "Godhra train burning — Gujarat communal riots followed under his CM tenure"},
            {"date": "2002-12-22", "event": "Re-elected as Gujarat CM — BJP won 127/182 seats"},
            {"date": "2014-05-26", "event": "Sworn in as 14th Prime Minister of India — BJP won 282/543 seats"},
            {"date": "2016-11-08", "event": "Announced demonetisation of Rs 500 and Rs 1000 notes at 8:15 PM"},
            {"date": "2019-05-30", "event": "Sworn in for second PM term — BJP won 303/543 seats"},
            {"date": "2024-06-09", "event": "Sworn in for third PM term heading NDA coalition (BJP won 240 seats)"},
        ]
    },
    {
        "name": "MS Dhoni",
        "year": 1981, "month": 7, "day": 7,
        "hour": 5, "min": 10,
        "lat": 23.3441, "lon": 85.3096,
        "place": "Ranchi, Jharkhand, India", "tz": 5.5,
        "rodden": "A",
        "note": "Birth time 5:10 AM from Dhoni family confirmation via astrodatabank researcher Seth, 2017",
        "events": [
            {"date": "2004-12-23", "event": "ODI debut vs Bangladesh, Chittagong"},
            {"date": "2005-10-31", "event": "Scored 183* vs Sri Lanka, Jaipur — highest ODI score by wicketkeeper"},
            {"date": "2007-09-24", "event": "Captained India to inaugural ICC T20 World Cup title vs Pakistan"},
            {"date": "2010-07-04", "event": "Married Sakshi Singh Rawat in Dehradun"},
            {"date": "2011-04-02", "event": "Captained India to ICC Cricket World Cup 2011 — scored 91* and hit winning six"},
            {"date": "2013-06-23", "event": "Won ICC Champions Trophy — first captain to win all 3 ICC white-ball trophies"},
            {"date": "2014-12-30", "event": "Retired from Test cricket mid-series in Melbourne"},
            {"date": "2020-08-15", "event": "Announced retirement from all international cricket via Instagram"},
        ]
    },
    {
        "name": "A.R. Rahman",
        "year": 1967, "month": 1, "day": 6,
        "hour": 5, "min": 50,
        "lat": 13.0827, "lon": 80.2707,
        "place": "Chennai (Madras), Tamil Nadu, India", "tz": 5.5,
        "rodden": "A",
        "note": "Birth time 5:50 AM self-reported by Rahman in interview (astrodatabank)",
        "events": [
            {"date": "1976-01-01", "event": "Father died (age 9) — began playing piano professionally to support family"},
            {"date": "1989-01-01", "event": "Converted to Islam at age 23 — adopted name A.R. Rahman"},
            {"date": "1992-01-01", "event": "Film scoring debut: Tamil film Roja (dir. Mani Ratnam) — instant sensation"},
            {"date": "1993-01-01", "event": "Won National Film Award (Silver Lotus) for Best Music Direction for Roja"},
            {"date": "1995-03-12", "event": "Married Saira Banu in Chennai"},
            {"date": "1997-01-01", "event": "Released Vande Mataram album — massive global success"},
            {"date": "2009-02-22", "event": "Won two Academy Awards for Slumdog Millionaire: Best Score + Best Original Song ('Jai Ho')"},
            {"date": "2010-01-01", "event": "Won two Grammy Awards + received Padma Bhushan"},
            {"date": "2024-11-01", "event": "Announced separation from wife Saira Banu after 29 years of marriage"},
        ]
    },
    {
        "name": "Rekha",
        "year": 1954, "month": 10, "day": 10,
        "hour": 11, "min": 0,
        "lat": 13.0827, "lon": 80.2707,
        "place": "Madras (Chennai), Tamil Nadu, India", "tz": 5.5,
        "rodden": "A",
        "note": "Birth time 11:00 AM from Kundli Sangraha (Bhat), AstroSage. Alt: 3:00 AM from sister's friend (lower reliability)",
        "events": [
            {"date": "1970-09-01", "event": "Hindi film debut in Sawan Bhadon — became immediate sensation"},
            {"date": "1980-01-01", "event": "Won Filmfare Award for Best Actress for Khubsoorat"},
            {"date": "1981-01-02", "event": "Umrao Jaan released — landmark performance as courtesan-poetess"},
            {"date": "1982-01-01", "event": "Won National Film Award for Best Actress for Umrao Jaan"},
            {"date": "1988-01-01", "event": "Won second Filmfare Best Actress for Khoon Bhari Maang — comeback"},
            {"date": "1990-03-04", "event": "Married businessman Mukesh Agarwal in quiet ceremony"},
            {"date": "1990-10-01", "event": "Husband Mukesh Agarwal died by suicide ~7 months after marriage"},
            {"date": "2010-01-26", "event": "Awarded Padma Shri by Government of India"},
            {"date": "2012-04-27", "event": "Nominated to Rajya Sabha (Indian Parliament's upper house)"},
        ]
    },
]


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
        "name": person["name"],
        "birth": birth,
        "lagna": lagna, "lagna_idx": lri, "lagna_deg": round(ldeg, 4),
        "lagna_lord": RASI_LORDS[lagna],
        "ayanamsa": round(swe.get_ayanamsa(jd), 6),
        "positions": positions,
        "janma_nakshatra": moon["nak"],
        "janma_nakshatra_lord": moon["nak_lord"],
        "moon_rasi": moon["rasi"],
        "moon_pada": moon["pada"],
        "rodden_rating": person.get("rodden", "Unknown"),
        "birth_time_note": person.get("note", ""),
        "known_events": person.get("events", []),
    }


def main():
    for person in CELEBRITIES:
        chart = compute_chart(person)
        slug = person["name"].lower().replace(" ", "_").replace(".", "")
        out = CHARTS_DIR / f"{slug}_chart.json"
        json.dump(chart, open(out, "w", encoding="utf-8"), indent=2, default=str)

        b = chart["birth"]
        print(f"\n=== {chart['name']} ===")
        print(f"  Birth: {b['day']:02d}-{b['month']:02d}-{b['year']}  {b['hour']:02d}:{b['min']:02d} IST  ({b['weekday']})")
        print(f"  Place: {b['place']}")
        print(f"  Lagna: {chart['lagna']} {chart['lagna_deg']:.2f}°  (lord: {chart['lagna_lord']})")
        print(f"  Moon:  {chart['moon_rasi']}  Nak: {chart['janma_nakshatra']} pada {chart['moon_pada']}  (lord: {chart['janma_nakshatra_lord']})")
        print(f"  Ayanamsa: {chart['ayanamsa']:.4f}° (Lahiri)  |  Rodden: {person['rodden']}")
        print()
        for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
            pd = chart["positions"][p]
            retro = " R" if pd.get("retrograde") else "  "
            print(f"    {p:<8} {pd['rasi']:<13} H{pd['house']:>2}  {pd['deg']:>6.2f}°  {pd['nak']:<20} pada {pd['pada']}{retro}")
        print(f"  Saved: {out}")


if __name__ == "__main__":
    main()
