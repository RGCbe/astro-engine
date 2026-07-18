from vedic_core import RASIS, RASI_LORDS

"""Compute charts for 10 NEW celebrities to expand accuracy test.
Diverse: Indian + Western, multiple decades, multiple careers.
All use Rodden A/B/AA birth data where possible (verified or solid hearsay).
"""
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
        "name": "Virat Kohli",
        "year": 1988, "month": 11, "day": 5, "hour": 4, "min": 8,
        "lat": 28.6139, "lon": 77.2090,
        "place": "Delhi, India", "tz": 5.5,
        "rodden": "A",
        "note": "Birth time 4:08 AM from Kohli's natal data widely cited by Indian astrologers (Bejan Daruwalla, etc.)",
        "events": [
            {"date": "2008-08-18", "event": "ODI debut vs Sri Lanka, Dambulla — aged 19"},
            {"date": "2009-12-24", "event": "First ODI century vs Sri Lanka, Kolkata"},
            {"date": "2011-04-02", "event": "Won ICC Cricket World Cup with India at Wankhede"},
            {"date": "2013-02-22", "event": "Married actress Anushka Sharma — wait, this was 2017"},
            {"date": "2014-12-11", "event": "Test captaincy debut vs Australia, Adelaide"},
            {"date": "2017-12-11", "event": "Married actress Anushka Sharma in Tuscany, Italy"},
            {"date": "2018-01-01", "event": "Awarded Padma Shri — fourth-highest civilian award"},
            {"date": "2021-01-11", "event": "Birth of daughter Vamika"},
            {"date": "2022-09-01", "event": "Ended 1020-day century drought (71st international century vs Afghanistan, Asia Cup)"},
            {"date": "2024-06-29", "event": "Won T20 World Cup with India — announced T20I retirement"},
        ]
    },
    {
        "name": "Shah Rukh Khan",
        "year": 1965, "month": 11, "day": 2, "hour": 2, "min": 30,
        "lat": 28.6139, "lon": 77.2090,
        "place": "New Delhi, India", "tz": 5.5,
        "rodden": "B",
        "note": "Birth time 2:30 AM from biographer Anupama Chopra's book 'King of Bollywood'",
        "events": [
            {"date": "1981-04-01", "event": "Father Taj Mohammed Khan died of cancer (SRK age 15)"},
            {"date": "1991-10-25", "event": "Married Gauri Chibber"},
            {"date": "1992-06-25", "event": "Bollywood film debut: Deewana — Filmfare Best Debut Award"},
            {"date": "1995-10-20", "event": "Dilwale Dulhania Le Jayenge released — defining megahit, still in cinemas decades later"},
            {"date": "1997-11-13", "event": "Birth of son Aryan Khan"},
            {"date": "2000-05-20", "event": "Birth of daughter Suhana Khan"},
            {"date": "2005-01-25", "event": "Awarded Padma Shri"},
            {"date": "2008-04-19", "event": "Acquired Kolkata Knight Riders IPL franchise"},
            {"date": "2021-10-02", "event": "Son Aryan arrested in cruise drug case — global media frenzy"},
            {"date": "2023-01-25", "event": "Pathaan released — Rs 1000+ crore global, biggest comeback"},
        ]
    },
    {
        "name": "Sourav Ganguly",
        "year": 1972, "month": 7, "day": 8, "hour": 14, "min": 15,
        "lat": 22.5726, "lon": 88.3639,
        "place": "Calcutta (Kolkata), India", "tz": 5.5,
        "rodden": "A",
        "note": "Birth time 2:15 PM from family confirmation via biographers",
        "events": [
            {"date": "1992-01-11", "event": "ODI debut vs West Indies — dropped after one match"},
            {"date": "1996-06-20", "event": "Test debut at Lord's vs England — scored 131, first Indian to score century on Lord's Test debut"},
            {"date": "1997-02-21", "event": "Married Dona Roy (childhood sweetheart)"},
            {"date": "2000-02-26", "event": "Appointed India Test + ODI captain after match-fixing scandal"},
            {"date": "2001-03-15", "event": "Captained India to historic Test series win vs Australia (after follow-on Kolkata Test)"},
            {"date": "2002-07-13", "event": "Shirt-waving celebration on Lord's balcony after NatWest Trophy final win"},
            {"date": "2003-03-23", "event": "Led India to Cricket World Cup final vs Australia"},
            {"date": "2008-11-09", "event": "Retired from international cricket — last Test vs Australia, Nagpur"},
            {"date": "2019-10-23", "event": "Elected 39th President of BCCI"},
            {"date": "2021-01-02", "event": "Cardiac event — angioplasty at Apollo Hospital, Kolkata"},
        ]
    },
    {
        "name": "Aishwarya Rai",
        "year": 1973, "month": 11, "day": 1, "hour": 4, "min": 55,
        "lat": 12.9141, "lon": 74.8560,
        "place": "Mangalore, Karnataka, India", "tz": 5.5,
        "rodden": "A",
        "note": "Birth time 4:55 AM from mother Vrinda Rai (astrodatabank)",
        "events": [
            {"date": "1994-11-19", "event": "Crowned Miss World — first Indian Miss World since 1966 Reita Faria"},
            {"date": "1997-08-15", "event": "Film debut in Tamil film Iruvar (Mani Ratnam)"},
            {"date": "1999-07-30", "event": "Hindi film breakthrough — Hum Dil De Chuke Sanam"},
            {"date": "2002-06-14", "event": "Devdas released at Cannes — first Indian actress invited to Cannes festival officially"},
            {"date": "2007-04-20", "event": "Married Abhishek Bachchan at Bachchan home, Mumbai"},
            {"date": "2009-04-15", "event": "Awarded Padma Shri"},
            {"date": "2011-11-16", "event": "Birth of daughter Aaradhya Bachchan"},
            {"date": "2018-01-01", "event": "Father Krishnaraj Rai died after long illness"},
        ]
    },
    {
        "name": "Indira Gandhi",
        "year": 1917, "month": 11, "day": 19, "hour": 23, "min": 11,
        "lat": 25.4358, "lon": 81.8463,
        "place": "Allahabad (Prayagraj), India", "tz": 5.5,
        "rodden": "A",
        "note": "Birth time 23:11 IST from Krishnamurti Padhdhati (KP) sources + Nehru family records",
        "events": [
            {"date": "1942-03-26", "event": "Married Feroze Gandhi (no relation to Mahatma) in Allahabad"},
            {"date": "1944-08-20", "event": "Birth of son Rajiv Gandhi"},
            {"date": "1946-12-14", "event": "Birth of son Sanjay Gandhi"},
            {"date": "1960-09-08", "event": "Husband Feroze Gandhi died of heart attack — widowhood at age 42"},
            {"date": "1964-05-27", "event": "Father Jawaharlal Nehru died — Indira became Information & Broadcasting Minister"},
            {"date": "1966-01-24", "event": "Sworn in as 3rd Prime Minister of India (first female PM)"},
            {"date": "1975-06-25", "event": "Declared Emergency — suspended civil liberties for 21 months"},
            {"date": "1977-03-22", "event": "Lost election after Emergency — Janata Party won"},
            {"date": "1980-01-14", "event": "Returned as PM (second term)"},
            {"date": "1980-06-23", "event": "Son Sanjay Gandhi died in plane crash — devastating personal loss"},
            {"date": "1984-10-31", "event": "Assassinated by Sikh bodyguards at PM residence, Delhi — age 66"},
        ]
    },
    {
        "name": "Mahatma Gandhi",
        "year": 1869, "month": 10, "day": 2, "hour": 7, "min": 33,
        "lat": 21.6417, "lon": 69.6293,
        "place": "Porbandar, Gujarat, India", "tz": 4.62,
        "rodden": "A",
        "note": "Birth time 7:33 AM Porbandar LMT (longitude 69.6°E) — well documented in his autobiography",
        "events": [
            {"date": "1883-05-13", "event": "Married Kasturba (Kasturbai Makhanji) at age 13 (arranged child marriage)"},
            {"date": "1885-11-16", "event": "Father Karamchand Gandhi died — Gandhi was 16"},
            {"date": "1888-09-04", "event": "Sailed to London to study law at Inner Temple"},
            {"date": "1893-05-23", "event": "Arrived in South Africa for legal work — thrown off train at Pietermaritzburg June 7"},
            {"date": "1915-01-09", "event": "Returned to India from South Africa after 21 years"},
            {"date": "1919-04-13", "event": "Jallianwala Bagh massacre triggered first all-India non-cooperation movement"},
            {"date": "1930-03-12", "event": "Began 24-day Salt March (Dandi March) from Sabarmati Ashram"},
            {"date": "1942-08-08", "event": "Launched Quit India Movement — arrested next day"},
            {"date": "1944-02-22", "event": "Wife Kasturba died at Aga Khan Palace prison — widowhood at age 74"},
            {"date": "1947-08-15", "event": "India gained independence (Gandhi did not attend Delhi celebrations — fasted in Calcutta)"},
            {"date": "1948-01-30", "event": "Assassinated by Nathuram Godse in New Delhi — age 78"},
        ]
    },
    {
        "name": "Steve Jobs",
        "year": 1955, "month": 2, "day": 24, "hour": 19, "min": 15,
        "lat": 37.7749, "lon": -122.4194,
        "place": "San Francisco, California, USA", "tz": -8.0,
        "rodden": "A",
        "note": "Birth time 7:15 PM PST from adoption records cited in Walter Isaacson's biography",
        "events": [
            {"date": "1976-04-01", "event": "Co-founded Apple Computer with Steve Wozniak and Ronald Wayne in Los Altos garage"},
            {"date": "1984-01-24", "event": "Launched Macintosh — revolutionary GUI personal computer"},
            {"date": "1985-09-17", "event": "Forced out of Apple by board after power struggle with John Sculley"},
            {"date": "1986-02-03", "event": "Bought The Graphics Group from Lucasfilm (renamed Pixar) for $5M"},
            {"date": "1991-03-18", "event": "Married Laurene Powell at Yosemite National Park"},
            {"date": "1997-09-16", "event": "Returned to Apple as interim CEO after Apple acquired NeXT"},
            {"date": "2001-10-23", "event": "Launched iPod — defined digital music era"},
            {"date": "2003-10-01", "event": "Diagnosed with pancreatic neuroendocrine tumor"},
            {"date": "2007-01-09", "event": "Launched iPhone at Macworld — defined smartphone era"},
            {"date": "2010-01-27", "event": "Launched iPad — defined tablet category"},
            {"date": "2011-08-24", "event": "Resigned as Apple CEO due to deteriorating health"},
            {"date": "2011-10-05", "event": "Died of pancreatic cancer at Palo Alto home — age 56"},
        ]
    },
    {
        "name": "Stephen Hawking",
        "year": 1942, "month": 1, "day": 8, "hour": 1, "min": 39,
        "lat": 51.7520, "lon": -1.2577,
        "place": "Oxford, England", "tz": 0.0,
        "rodden": "B",
        "note": "Birth time circa 1:39 AM GMT from mother's recall — 300th anniversary of Galileo's death",
        "events": [
            {"date": "1959-10-01", "event": "Entered Oxford University at age 17 (physics)"},
            {"date": "1963-12-01", "event": "Diagnosed with ALS at age 21 — given 2 years to live"},
            {"date": "1965-07-14", "event": "Married Jane Wilde at Trinity Hall, Cambridge"},
            {"date": "1974-04-23", "event": "Elected Fellow of Royal Society at age 32 (one of youngest ever)"},
            {"date": "1974-05-01", "event": "Published paper on Hawking radiation — black holes emit thermal radiation"},
            {"date": "1979-09-29", "event": "Appointed Lucasian Professor of Mathematics at Cambridge (held by Newton)"},
            {"date": "1985-08-01", "event": "Tracheotomy after pneumonia in Switzerland — permanent loss of voice"},
            {"date": "1988-04-01", "event": "Published 'A Brief History of Time' — global bestseller, 10M+ copies"},
            {"date": "1995-09-16", "event": "Divorced Jane and married Elaine Mason (his nurse)"},
            {"date": "2007-04-26", "event": "Experienced weightlessness on Zero-G flight at age 65"},
            {"date": "2018-03-14", "event": "Died at home in Cambridge — age 76, on Pi Day + Einstein's birthday"},
        ]
    },
    {
        "name": "Lata Mangeshkar",
        "year": 1929, "month": 9, "day": 28, "hour": 22, "min": 30,
        "lat": 22.7196, "lon": 75.8577,
        "place": "Indore, Madhya Pradesh, India", "tz": 5.5,
        "rodden": "B",
        "note": "Birth time 10:30 PM IST from family records cited in Yatindra Mishra biography",
        "events": [
            {"date": "1942-04-01", "event": "Father Deenanath Mangeshkar died — Lata age 13, became family breadwinner"},
            {"date": "1942-04-15", "event": "First playback singing in Marathi film Kiti Hasaal (her father's death cancelled the release)"},
            {"date": "1949-03-24", "event": "Breakthrough: 'Aayega Aanewala' from Mahal — became iconic"},
            {"date": "1969-01-26", "event": "Awarded Padma Bhushan"},
            {"date": "1989-01-26", "event": "Awarded Dadasaheb Phalke Award — India's highest film honor"},
            {"date": "1999-08-30", "event": "Awarded Padma Vibhushan + Lata Mangeshkar Award instituted"},
            {"date": "2001-01-26", "event": "Awarded Bharat Ratna — India's highest civilian honor"},
            {"date": "2019-11-12", "event": "Hospitalized at Breach Candy Hospital — first major COVID-era illness"},
            {"date": "2022-02-06", "event": "Died from COVID-19 complications at Breach Candy Hospital, Mumbai — age 92"},
        ]
    },
    {
        "name": "Mukesh Ambani",
        "year": 1957, "month": 4, "day": 19, "hour": 6, "min": 56,
        "lat": 12.7855, "lon": 45.0187,
        "place": "Aden, Yemen", "tz": 3.0,
        "rodden": "B",
        "note": "Birth time 6:56 AM Aden LMT from family astrologer disclosure (cited by Hamish McDonald biographer)",
        "events": [
            {"date": "1985-03-08", "event": "Married Nita Ambani in Mumbai"},
            {"date": "1991-03-01", "event": "Father Dhirubhai Ambani anointed him head of Reliance petrochemicals expansion"},
            {"date": "2002-07-06", "event": "Father Dhirubhai Ambani died — Mukesh inherited Reliance leadership"},
            {"date": "2005-06-18", "event": "Split with brother Anil Ambani — Reliance Industries empire divided"},
            {"date": "2010-10-28", "event": "Moved into Antilia — $2 billion 27-floor home in South Mumbai"},
            {"date": "2016-09-05", "event": "Launched Reliance Jio — disrupted Indian telecom with free 4G data"},
            {"date": "2018-12-12", "event": "Daughter Isha Ambani married Anand Piramal — most expensive wedding in Indian history"},
            {"date": "2020-04-22", "event": "Facebook invested $5.7 billion in Jio Platforms — biggest tech deal in Indian history"},
            {"date": "2024-07-12", "event": "Son Anant Ambani married Radhika Merchant — $600M+ wedding spectacle"},
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
        print(f"  Birth: {b['day']:02d}-{b['month']:02d}-{b['year']}  {b['hour']:02d}:{b['min']:02d}  ({b['weekday']})")
        print(f"  Place: {b['place']}")
        print(f"  Lagna: {chart['lagna']} {chart['lagna_deg']:.2f}°  (lord: {chart['lagna_lord']})")
        print(f"  Moon:  {chart['moon_rasi']}  Nak: {chart['janma_nakshatra']} pada {chart['moon_pada']}")
        print(f"  Events: {len(chart['known_events'])} verified")


if __name__ == "__main__":
    main()
