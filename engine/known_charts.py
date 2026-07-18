"""
Known charts library for empirical backtest.

Each chart includes:
    - birthdata (date, time, place, lat, lon, tz)
    - documented life events (year, age, event_type, description)
    - source citation for the birthdata

Used by the validation layer (Phase III on the roadmap) to backtest
predictions against documented outcomes. Most birth times are the
publicly-quoted "Astrodienst Quality A/B/C" values from astro.com or
biographical sources.

Event types follow a controlled vocabulary:
    BIRTH, EDUCATION, MARRIAGE, CAREER_START, CAREER_PEAK, AWARD,
    HEALTH_CRISIS, DEATH, IMPRISONMENT, EXILE, FOUND_BUSINESS,
    POLITICAL_OFFICE, SCANDAL, MAJOR_LOSS, CHILDREN_BORN, DIVORCE
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LifeEvent:
    year: int
    age: int
    event_type: str
    description: str
    confidence: str = "documented"   # documented | reported | rumored
    month: int | None = None         # 1-12 if known (month-precision dasha lookup)
    day: int | None = None           # 1-31 if known (day-precision)


@dataclass
class KnownChart:
    name: str
    birthdata: dict                    # {date, time, place, lat, lon, tz}
    events: list[LifeEvent]
    source: str                         # citation for birthdata + events
    quality: str = "A"                  # Rodden A=verified | B=biography
                                        # | C=quoted | DD=conflicting


# ─── Indian luminaries (Tier 1) ───────────────────────────────────────────
KNOWN_CHARTS: list[KnownChart] = [
    KnownChart(
        name="Mahatma Gandhi",
        birthdata={"date": "1869-10-02", "time": "07:33", "tz": 4.62, "place": "Porbandar, Gujarat, India", "lat": 21.6417, "lon": 69.6293},
        events=[
            LifeEvent(1888, 19, "EDUCATION", "Sails to London for law"),
            LifeEvent(1893, 24, "CAREER_START", "Moves to South Africa, becomes activist"),
            LifeEvent(1915, 46, "CAREER_PEAK", "Returns to India to lead independence movement"),
            LifeEvent(1922, 53, "IMPRISONMENT", "Arrested for sedition, sentenced to 6 yrs"),
            LifeEvent(1930, 61, "AWARD", "Salt March; international fame"),
            LifeEvent(1947, 78, "POLITICAL_OFFICE", "India gains independence"),
            LifeEvent(1948, 78, "DEATH", "Assassinated by Nathuram Godse, Jan 30"),
        ],
        source="Astrodienst (Rodden A; quoted by Gandhi himself)",
        quality="A",
    ),
    KnownChart(
        name="Indira Gandhi",
        birthdata={"date": "1917-11-19", "time": "23:11", "tz": 5.5, "place": "Allahabad (Prayagraj), India", "lat": 25.4358, "lon": 81.8463},
        events=[
            LifeEvent(1942, 24, "MARRIAGE", "Marries Feroze Gandhi"),
            LifeEvent(1944, 26, "CHILDREN_BORN", "Rajiv Gandhi born"),
            LifeEvent(1966, 48, "POLITICAL_OFFICE", "Becomes Prime Minister of India"),
            LifeEvent(1975, 57, "POLITICAL_OFFICE", "Declares Emergency, suspends democracy"),
            LifeEvent(1977, 59, "MAJOR_LOSS", "Loses election after Emergency"),
            LifeEvent(1980, 62, "POLITICAL_OFFICE", "Returns to power"),
            LifeEvent(1984, 66, "DEATH", "Assassinated by bodyguards, Oct 31"),
        ],
        source="Astrodienst Rodden B (biographical)",
        quality="B",
    ),
    KnownChart(
        name="Narendra Modi",
        birthdata={"date": "1950-09-17", "time": "11:00", "tz": 5.5,
                   "place": "Vadnagar, Gujarat, India",
                   "lat": 23.7936, "lon": 72.6376},
        events=[
            LifeEvent(2001, 51, "POLITICAL_OFFICE", "Becomes Chief Minister of Gujarat"),
            LifeEvent(2014, 63, "POLITICAL_OFFICE", "Becomes Prime Minister of India"),
            LifeEvent(2019, 68, "POLITICAL_OFFICE", "Re-elected with massive mandate"),
            LifeEvent(2024, 73, "POLITICAL_OFFICE", "Third term as PM"),
        ],
        source="Astrodienst (quoted by Modi himself)",
        quality="C",
    ),
    KnownChart(
        name="Sachin Tendulkar",
        birthdata={"date": "1973-04-24", "time": "13:00", "tz": 5.5, "place": "Mumbai (Dadar), India", "lat": 18.9667, "lon": 72.8333},
        events=[
            LifeEvent(1989, 16, "CAREER_START", "Test debut at age 16 vs Pakistan"),
            LifeEvent(2002, 29, "MARRIAGE", "Marries Anjali"),
            LifeEvent(2008, 35, "CAREER_PEAK", "Surpasses Brian Lara as highest run-scorer"),
            LifeEvent(2011, 38, "AWARD", "Wins Cricket World Cup with India"),
            LifeEvent(2013, 40, "CAREER_END", "Retires from Test cricket"),
            LifeEvent(2014, 41, "AWARD", "Bharat Ratna (India's highest civilian award)"),
        ],
        source="Astrodienst Rodden A (birth certificate)",
        quality="A",
    ),
    KnownChart(
        name="Lata Mangeshkar",
        birthdata={"date": "1929-09-28", "time": "22:30", "tz": 5.5, "place": "Indore, Madhya Pradesh, India", "lat": 22.7196, "lon": 75.8577},
        events=[
            LifeEvent(1942, 13, "DEATH", "Father dies, becomes family breadwinner"),
            LifeEvent(1948, 19, "CAREER_START", "Mahal song 'Aayega Aanewala'"),
            LifeEvent(1969, 40, "AWARD", "Padma Bhushan"),
            LifeEvent(1989, 60, "AWARD", "Dadasaheb Phalke Award"),
            LifeEvent(2001, 71, "AWARD", "Bharat Ratna"),
            LifeEvent(2022, 92, "DEATH", "Dies Feb 6 from COVID-19 complications"),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),
    KnownChart(
        name="Ratan Tata",
        birthdata={"date": "1937-12-28", "time": "06:30", "tz": 5.5,
                   "place": "Mumbai, India", "lat": 19.072, "lon": 72.882},
        events=[
            LifeEvent(1991, 53, "CAREER_PEAK", "Becomes Chairman of Tata Group"),
            LifeEvent(2000, 62, "FOUND_BUSINESS", "Tetley acquisition (£271M)"),
            LifeEvent(2008, 70, "FOUND_BUSINESS", "Jaguar Land Rover acquisition"),
            LifeEvent(2012, 74, "CAREER_END", "Retires as Chairman"),
            LifeEvent(2024, 86, "DEATH", "Dies Oct 9, 2024"),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),
    KnownChart(
        name="Shah Rukh Khan",
        birthdata={"date": "1965-11-02", "time": "02:30", "tz": 5.5, "place": "New Delhi, India", "lat": 28.6139, "lon": 77.209},
        events=[
            LifeEvent(1991, 25, "MARRIAGE", "Marries Gauri"),
            LifeEvent(1992, 26, "CAREER_START", "Bollywood debut Deewana"),
            LifeEvent(1995, 29, "CAREER_PEAK", "DDLJ — superstar status"),
            LifeEvent(2007, 41, "CHILDREN_BORN", "AbRam born via surrogacy"),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Ramana Maharshi",
        birthdata={"date": "1879-12-30", "time": "01:00", "tz": 5.21,
                   "place": "Tiruchuli, Tamil Nadu, India",
                   "lat": 9.4, "lon": 78.42},
        events=[
            LifeEvent(1896, 16, "SPIRITUAL_AWAKENING",
                       "Death-experience awakening"),
            LifeEvent(1899, 19, "EXILE", "Moves to Arunachala mountain"),
            LifeEvent(1922, 42, "FOUND_BUSINESS", "Sri Ramanasramam founded"),
            LifeEvent(1950, 70, "DEATH", "Dies April 14 from sarcoma"),
        ],
        source="Bhagavan's own statement to devotees",
        quality="C",
    ),
    KnownChart(
        name="Sri Aurobindo",
        birthdata={"date": "1872-08-15", "time": "04:50", "tz": 5.88,
                   "place": "Calcutta, India", "lat": 22.57, "lon": 88.36},
        events=[
            LifeEvent(1908, 35, "IMPRISONMENT", "Alipore Bomb Case, 1 yr in jail"),
            LifeEvent(1910, 37, "EXILE", "Moves to Pondicherry"),
            LifeEvent(1926, 53, "SPIRITUAL_AWAKENING",
                       "'Day of Siddhi' — overhead consciousness"),
            LifeEvent(1950, 77, "DEATH", "Dies Dec 5"),
        ],
        source="Sri Aurobindo Ashram records",
        quality="A",
    ),

    # ─── World figures (Tier 2) ──────────────────────────────────────────
    KnownChart(
        name="Albert Einstein",
        birthdata={"date": "1879-03-14", "time": "11:30", "tz": 1.0,
                   "place": "Ulm, Germany", "lat": 48.4, "lon": 9.99},
        events=[
            LifeEvent(1903, 24, "MARRIAGE", "Marries Mileva Marić"),
            LifeEvent(1905, 26, "AWARD", "Annus Mirabilis — 4 papers"),
            LifeEvent(1919, 40, "CAREER_PEAK",
                       "Eclipse confirms general relativity — global fame"),
            LifeEvent(1921, 42, "AWARD", "Nobel Prize in Physics"),
            LifeEvent(1933, 54, "EXILE", "Flees Nazi Germany to USA"),
            LifeEvent(1955, 76, "DEATH", "Dies April 18"),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Adolf Hitler",
        birthdata={"date": "1889-04-20", "time": "18:30", "tz": 0.92,
                   "place": "Braunau am Inn, Austria",
                   "lat": 48.26, "lon": 13.04},
        events=[
            LifeEvent(1923, 34, "IMPRISONMENT", "Beer Hall Putsch fails, jailed"),
            LifeEvent(1933, 43, "POLITICAL_OFFICE", "Becomes Chancellor"),
            LifeEvent(1939, 49, "MAJOR_LOSS", "Starts WW2 (Sept 1)"),
            LifeEvent(1945, 55, "DEATH", "Suicide April 30"),
        ],
        source="Astrodienst Rodden AA (baptismal record)",
        quality="A",
    ),
    KnownChart(
        name="Steve Jobs",
        birthdata={"date": "1955-02-24", "time": "19:15", "tz": -8.0,
                   "place": "San Francisco, USA",
                   "lat": 37.7749, "lon": -122.4194},
        events=[
            LifeEvent(1976, 21, "FOUND_BUSINESS", "Co-founds Apple"),
            LifeEvent(1985, 30, "MAJOR_LOSS", "Ousted from Apple"),
            LifeEvent(1991, 36, "MARRIAGE", "Marries Laurene Powell"),
            LifeEvent(1997, 42, "CAREER_PEAK", "Returns to Apple as CEO"),
            LifeEvent(2003, 48, "HEALTH_CRISIS", "Pancreatic cancer diagnosed"),
            LifeEvent(2007, 52, "AWARD", "Launches iPhone"),
            LifeEvent(2011, 56, "DEATH", "Dies Oct 5"),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Elon Musk",
        birthdata={"date": "1971-06-28", "time": "07:30", "tz": 2.0,
                   "place": "Pretoria, South Africa",
                   "lat": -25.745, "lon": 28.188},
        events=[
            LifeEvent(1995, 24, "FOUND_BUSINESS", "Zip2 founded"),
            LifeEvent(2002, 31, "FOUND_BUSINESS", "PayPal exit; SpaceX founded"),
            LifeEvent(2004, 33, "FOUND_BUSINESS", "Tesla joining"),
            LifeEvent(2018, 47, "SCANDAL", "Funding-secured tweet, SEC settlement"),
            LifeEvent(2022, 51, "FOUND_BUSINESS", "Twitter acquisition $44B"),
            LifeEvent(2024, 53, "AWARD", "World's richest person"),
        ],
        source="Astrodienst Rodden C (quoted)",
        quality="C",
    ),
    KnownChart(
        name="Bill Gates",
        birthdata={"date": "1955-10-28", "time": "21:15", "tz": -8.0,
                   "place": "Seattle, USA",
                   "lat": 47.61, "lon": -122.33},
        events=[
            LifeEvent(1975, 19, "FOUND_BUSINESS", "Microsoft founded"),
            LifeEvent(1986, 30, "AWARD", "Microsoft IPO; becomes billionaire"),
            LifeEvent(1994, 38, "MARRIAGE", "Marries Melinda French"),
            LifeEvent(2000, 44, "FOUND_BUSINESS", "Gates Foundation founded"),
            LifeEvent(2008, 52, "CAREER_END",
                       "Steps down from Microsoft daily ops"),
            LifeEvent(2021, 65, "DIVORCE", "Divorces Melinda"),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Barack Obama",
        birthdata={"date": "1961-08-04", "time": "19:24", "tz": -10.0,
                   "place": "Honolulu, Hawaii, USA",
                   "lat": 21.30694, "lon": -157.85833},
        events=[
            LifeEvent(1992, 31, "MARRIAGE", "Marries Michelle Robinson"),
            LifeEvent(2004, 43, "POLITICAL_OFFICE", "Senate seat (Illinois)"),
            LifeEvent(2008, 47, "POLITICAL_OFFICE", "Elected President"),
            LifeEvent(2009, 47, "AWARD", "Nobel Peace Prize"),
            LifeEvent(2012, 51, "POLITICAL_OFFICE", "Re-elected"),
            LifeEvent(2017, 55, "CAREER_END", "Leaves White House"),
        ],
        source="Astrodienst Rodden A (birth certificate)",
        quality="A",
    ),
    KnownChart(
        name="Sharon Tate",
        birthdata={"date": "1943-01-24", "time": "17:47", "tz": -6.0,
                   "place": "Dallas, Texas, USA",
                   "lat": 32.78, "lon": -96.8},
        events=[
            LifeEvent(1968, 25, "MARRIAGE", "Marries Roman Polanski"),
            LifeEvent(1969, 26, "DEATH",
                       "Murdered by Manson Family Aug 9, while pregnant"),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),

    # ─── Tragic markers (Tier 4) ──────────────────────────────────────────
    KnownChart(
        name="Princess Diana",
        birthdata={"date": "1961-07-01", "time": "19:45", "tz": -1.0,
                   "place": "Sandringham, England",
                   "lat": 52.83, "lon": 0.50},
        events=[
            LifeEvent(1981, 20, "MARRIAGE", "Marries Prince Charles"),
            LifeEvent(1982, 21, "CHILDREN_BORN", "William born"),
            LifeEvent(1996, 35, "DIVORCE", "Divorces Charles"),
            LifeEvent(1997, 36, "DEATH",
                       "Dies in Paris car crash Aug 31"),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Marilyn Monroe",
        birthdata={"date": "1926-06-01", "time": "09:30", "tz": -8.0,
                   "place": "Los Angeles, USA",
                   "lat": 34.05, "lon": -118.24},
        events=[
            LifeEvent(1953, 27, "CAREER_PEAK",
                       "Gentlemen Prefer Blondes; international stardom"),
            LifeEvent(1956, 30, "MARRIAGE", "Marries Arthur Miller"),
            LifeEvent(1962, 36, "DEATH",
                       "Found dead Aug 5; barbiturate overdose"),
        ],
        source="Astrodienst Rodden AA (birth certificate)",
        quality="A",
    ),
    KnownChart(
        name="Kurt Cobain",
        birthdata={"date": "1967-02-20", "time": "19:38", "tz": -8.0,
                   "place": "Aberdeen, Washington, USA",
                   "lat": 46.97, "lon": -123.82},
        events=[
            LifeEvent(1991, 24, "CAREER_PEAK", "Nevermind released"),
            LifeEvent(1992, 25, "MARRIAGE", "Marries Courtney Love"),
            LifeEvent(1994, 27, "DEATH", "Suicide April 5"),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Steve Irwin",
        birthdata={"date": "1962-02-22", "time": "16:30", "tz": 10.0,
                   "place": "Essendon, Australia",
                   "lat": -37.74, "lon": 144.91},
        events=[
            LifeEvent(1992, 30, "MARRIAGE", "Marries Terri", month=6),
            LifeEvent(1996, 34, "CAREER_PEAK",
                       "The Crocodile Hunter TV series"),
            LifeEvent(2006, 44, "DEATH",
                       "Killed by stingray Sept 4", month=9, day=4),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),

    # ─── Tier 2 expansion — World figures (verified birth records) ────────
    KnownChart(
        name="John F Kennedy",
        birthdata={"date": "1917-05-29", "time": "15:00", "tz": -5.0,
                   "place": "Brookline, MA, USA",
                   "lat": 42.332, "lon": -71.121},
        events=[
            LifeEvent(1953, 36, "MARRIAGE", "Marries Jacqueline Bouvier", month=9, day=12),
            LifeEvent(1957, 40, "CHILDREN_BORN", "Caroline born", month=11, day=27),
            LifeEvent(1960, 43, "POLITICAL_OFFICE", "Wins presidency", month=11, day=8),
            LifeEvent(1961, 43, "POLITICAL_OFFICE", "Inaugurated President", month=1, day=20),
            LifeEvent(1962, 45, "MAJOR_LOSS", "Cuban Missile Crisis", month=10),
            LifeEvent(1963, 46, "DEATH", "Assassinated in Dallas", month=11, day=22),
        ],
        source="Astrodienst Rodden AA (birth certificate)",
        quality="A",
    ),
    KnownChart(
        name="Vladimir Putin",
        birthdata={"date": "1952-10-07", "time": "09:30", "tz": 3.0,
                   "place": "Leningrad (St Petersburg), USSR",
                   "lat": 59.93, "lon": 30.34},
        events=[
            LifeEvent(1983, 30, "MARRIAGE", "Marries Lyudmila", month=7, day=28),
            LifeEvent(1985, 33, "CHILDREN_BORN", "Maria born", month=4, day=28),
            LifeEvent(1999, 47, "POLITICAL_OFFICE", "Acting President", month=12, day=31),
            LifeEvent(2000, 47, "POLITICAL_OFFICE", "Elected President", month=3, day=26),
            LifeEvent(2014, 62, "MAJOR_LOSS", "Crimea annexation, sanctions", month=3),
            LifeEvent(2022, 69, "MAJOR_LOSS", "Invades Ukraine, becomes pariah", month=2, day=24),
        ],
        source="Astrodienst Rodden C (quoted, official biography)",
        quality="C",
    ),
    KnownChart(
        name="Donald Trump",
        birthdata={"date": "1946-06-14", "time": "10:54", "tz": -4.0,
                   "place": "Queens, NY, USA",
                   "lat": 40.728, "lon": -73.795},
        events=[
            LifeEvent(1971, 25, "FOUND_BUSINESS", "Takes over family business", month=1),
            LifeEvent(1977, 31, "MARRIAGE", "Marries Ivana", month=4, day=7),
            LifeEvent(1990, 44, "MAJOR_LOSS", "Near bankruptcy, billion-dollar debt"),
            LifeEvent(2005, 59, "MARRIAGE", "Marries Melania", month=1, day=22),
            LifeEvent(2016, 70, "POLITICAL_OFFICE", "Wins presidency", month=11, day=8),
            LifeEvent(2020, 74, "MAJOR_LOSS", "Loses re-election", month=11, day=3),
            LifeEvent(2024, 78, "POLITICAL_OFFICE", "Re-elected", month=11, day=5),
        ],
        source="Astrodienst Rodden AA (birth certificate)",
        quality="A",
    ),
    KnownChart(
        name="Hillary Clinton",
        birthdata={"date": "1947-10-26", "time": "20:02", "tz": -6.0,
                   "place": "Chicago, IL, USA",
                   "lat": 41.85, "lon": -87.65},
        events=[
            LifeEvent(1975, 27, "MARRIAGE", "Marries Bill Clinton", month=10, day=11),
            LifeEvent(1980, 32, "CHILDREN_BORN", "Chelsea born", month=2, day=27),
            LifeEvent(2000, 53, "POLITICAL_OFFICE", "Elected to US Senate", month=11, day=7),
            LifeEvent(2009, 61, "POLITICAL_OFFICE", "US Secretary of State", month=1, day=21),
            LifeEvent(2016, 69, "MAJOR_LOSS", "Loses presidential election", month=11, day=8),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="Margaret Thatcher",
        birthdata={"date": "1925-10-13", "time": "09:00", "tz": 0.0,
                   "place": "Grantham, England", "lat": 52.91, "lon": -0.64},
        events=[
            LifeEvent(1951, 26, "MARRIAGE", "Marries Denis Thatcher", month=12, day=13),
            LifeEvent(1953, 27, "CHILDREN_BORN", "Twins born", month=8, day=15),
            LifeEvent(1979, 53, "POLITICAL_OFFICE", "Becomes UK PM", month=5, day=4),
            LifeEvent(1990, 65, "MAJOR_LOSS", "Forced from office", month=11, day=22),
            LifeEvent(2013, 87, "DEATH", "Dies of stroke", month=4, day=8),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Nelson Mandela",
        birthdata={"date": "1918-07-18", "time": "14:54", "tz": 2.0,
                   "place": "Mvezo, South Africa",
                   "lat": -31.95, "lon": 28.69},
        events=[
            LifeEvent(1944, 26, "MARRIAGE", "Marries Evelyn Mase", month=10),
            LifeEvent(1962, 44, "IMPRISONMENT", "Arrested", month=8, day=5),
            LifeEvent(1964, 45, "IMPRISONMENT", "Life sentence Robben Island", month=6, day=12),
            LifeEvent(1990, 71, "EXILE", "Released after 27 years", month=2, day=11),
            LifeEvent(1993, 75, "AWARD", "Nobel Peace Prize", month=10, day=15),
            LifeEvent(1994, 75, "POLITICAL_OFFICE", "Elected President of SA", month=5, day=10),
            LifeEvent(2013, 95, "DEATH", "Dies of respiratory infection", month=12, day=5),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Mark Zuckerberg",
        birthdata={"date": "1984-05-14", "time": "14:30", "tz": -5.0,
                   "place": "White Plains, NY, USA",
                   "lat": 41.034, "lon": -73.763},
        events=[
            LifeEvent(2004, 19, "FOUND_BUSINESS", "Launches Facebook", month=2, day=4),
            LifeEvent(2012, 28, "FOUND_BUSINESS", "Facebook IPO", month=5, day=18),
            LifeEvent(2012, 28, "MARRIAGE", "Marries Priscilla Chan", month=5, day=19),
            LifeEvent(2015, 31, "CHILDREN_BORN", "Maxima born", month=12, day=1),
            LifeEvent(2021, 37, "FOUND_BUSINESS", "Renames to Meta, metaverse pivot", month=10, day=28),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="Jeff Bezos",
        birthdata={"date": "1964-01-12", "time": "10:15", "tz": -7.0,
                   "place": "Albuquerque, NM, USA",
                   "lat": 35.085, "lon": -106.65},
        events=[
            LifeEvent(1993, 29, "MARRIAGE", "Marries MacKenzie Tuttle", month=9, day=4),
            LifeEvent(1994, 30, "FOUND_BUSINESS", "Founds Amazon", month=7, day=5),
            LifeEvent(1997, 33, "FOUND_BUSINESS", "Amazon IPO", month=5, day=15),
            LifeEvent(2000, 36, "FOUND_BUSINESS", "Founds Blue Origin", month=9),
            LifeEvent(2019, 55, "DIVORCE", "Divorces MacKenzie", month=4, day=4),
            LifeEvent(2021, 57, "CAREER_END", "Steps down as Amazon CEO", month=7, day=5),
            LifeEvent(2021, 57, "AWARD", "Flies to space on New Shepard", month=7, day=20),
        ],
        source="Astrodienst Rodden A (birth certificate)",
        quality="A",
    ),
    KnownChart(
        name="Warren Buffett",
        birthdata={"date": "1930-08-30", "time": "15:00", "tz": -5.0,
                   "place": "Omaha, NE, USA",
                   "lat": 41.26, "lon": -95.93},
        events=[
            LifeEvent(1952, 21, "MARRIAGE", "Marries Susan Thompson", month=4, day=19),
            LifeEvent(1956, 26, "FOUND_BUSINESS", "Buffett Partnership Ltd", month=5, day=1),
            LifeEvent(1965, 35, "FOUND_BUSINESS", "Takes control of Berkshire Hathaway", month=5, day=10),
            LifeEvent(1990, 60, "AWARD", "Becomes billionaire publicly known"),
            LifeEvent(2004, 74, "MAJOR_LOSS", "Wife Susan dies", month=7, day=29),
            LifeEvent(2006, 76, "MARRIAGE", "Marries Astrid Menks", month=8, day=30),
            LifeEvent(2006, 76, "AWARD", "Pledges 85% wealth to Gates Foundation", month=6, day=26),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="Larry Page",
        birthdata={"date": "1973-03-26", "time": "09:33", "tz": -5.0,
                   "place": "East Lansing, MI, USA",
                   "lat": 42.737, "lon": -84.484},
        events=[
            LifeEvent(1998, 25, "FOUND_BUSINESS", "Founds Google with Brin", month=9, day=4),
            LifeEvent(2004, 31, "FOUND_BUSINESS", "Google IPO", month=8, day=19),
            LifeEvent(2007, 34, "MARRIAGE", "Marries Lucinda Southworth", month=12, day=8),
            LifeEvent(2015, 42, "FOUND_BUSINESS", "Restructures into Alphabet", month=8, day=10),
            LifeEvent(2019, 46, "CAREER_END", "Steps down as Alphabet CEO", month=12, day=3),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="Sergey Brin",
        birthdata={"date": "1973-08-21", "time": "10:00", "tz": 3.0,
                   "place": "Moscow, USSR", "lat": 55.75, "lon": 37.62},
        events=[
            LifeEvent(1998, 25, "FOUND_BUSINESS", "Founds Google", month=9, day=4),
            LifeEvent(2004, 30, "FOUND_BUSINESS", "Google IPO", month=8, day=19),
            LifeEvent(2007, 33, "MARRIAGE", "Marries Anne Wojcicki", month=5),
            LifeEvent(2015, 41, "DIVORCE", "Divorces Anne", month=6, day=24),
        ],
        source="Astrodienst Rodden C (no time verified)",
        quality="C",
    ),

    # ─── Tier 3: Tragic markers / early death ─────────────────────────────
    KnownChart(
        name="Heath Ledger",
        birthdata={"date": "1979-04-04", "time": "06:30", "tz": 8.0,
                   "place": "Perth, Australia", "lat": -31.95, "lon": 115.86},
        events=[
            LifeEvent(2005, 25, "CAREER_PEAK", "Brokeback Mountain", month=12, day=9),
            LifeEvent(2005, 26, "CHILDREN_BORN", "Matilda born", month=10, day=28),
            LifeEvent(2008, 28, "DEATH", "Accidental overdose", month=1, day=22),
            LifeEvent(2009, 28, "AWARD", "Posthumous Oscar (The Dark Knight)", month=2, day=22),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Amy Winehouse",
        birthdata={"date": "1983-09-14", "time": "22:25", "tz": 1.0,
                   "place": "London, UK", "lat": 51.51, "lon": -0.13},
        events=[
            LifeEvent(2007, 23, "AWARD", "Wins 5 Grammys for Back to Black"),
            LifeEvent(2007, 23, "MARRIAGE", "Marries Blake Fielder-Civil", month=5, day=18),
            LifeEvent(2009, 26, "DIVORCE", "Divorce finalized", month=8),
            LifeEvent(2011, 27, "DEATH", "Alcohol poisoning", month=7, day=23),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Whitney Houston",
        birthdata={"date": "1963-08-09", "time": "20:55", "tz": -4.0,
                   "place": "Newark, NJ, USA", "lat": 40.74, "lon": -74.17},
        events=[
            LifeEvent(1985, 22, "CAREER_PEAK", "Debut album, blockbuster", month=2, day=14),
            LifeEvent(1992, 28, "MARRIAGE", "Marries Bobby Brown", month=7, day=18),
            LifeEvent(2007, 43, "DIVORCE", "Divorces Bobby", month=4, day=24),
            LifeEvent(2012, 48, "DEATH", "Drowning, drug-related", month=2, day=11),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Michael Jackson",
        birthdata={"date": "1958-08-29", "time": "19:33", "tz": -5.0,
                   "place": "Gary, IN, USA", "lat": 41.59, "lon": -87.35},
        events=[
            LifeEvent(1982, 24, "CAREER_PEAK", "Thriller released", month=11, day=30),
            LifeEvent(1994, 35, "MARRIAGE", "Marries Lisa Marie Presley", month=5, day=26),
            LifeEvent(1996, 38, "DIVORCE", "Divorce from Lisa Marie", month=1, day=18),
            LifeEvent(1996, 38, "MARRIAGE", "Marries Debbie Rowe", month=11, day=14),
            LifeEvent(2005, 46, "SCANDAL", "Acquitted in molestation trial", month=6, day=13),
            LifeEvent(2009, 50, "DEATH", "Cardiac arrest, propofol", month=6, day=25),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="John Lennon",
        birthdata={"date": "1940-10-09", "time": "18:30", "tz": 1.0,
                   "place": "Liverpool, UK", "lat": 53.41, "lon": -2.99},
        events=[
            LifeEvent(1964, 24, "CAREER_PEAK", "Beatles invade USA", month=2, day=7),
            LifeEvent(1969, 28, "MARRIAGE", "Marries Yoko Ono", month=3, day=20),
            LifeEvent(1970, 29, "MAJOR_LOSS", "Beatles break up", month=4, day=10),
            LifeEvent(1980, 40, "DEATH", "Shot by Mark Chapman", month=12, day=8),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),

    # ─── Tier 4: Spiritual / philosophical figures ───────────────────────
    KnownChart(
        name="Carl Jung",
        birthdata={"date": "1875-07-26", "time": "19:32", "tz": 0.5,
                   "place": "Kesswil, Switzerland",
                   "lat": 47.6, "lon": 9.32},
        events=[
            LifeEvent(1903, 27, "MARRIAGE", "Marries Emma Rauschenbach", month=2, day=14),
            LifeEvent(1913, 38, "SPIRITUAL_AWAKENING", "Confrontation with the Unconscious", month=10),
            LifeEvent(1921, 46, "CAREER_PEAK", "Publishes Psychological Types"),
            LifeEvent(1961, 85, "DEATH", "Dies at home", month=6, day=6),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Sigmund Freud",
        birthdata={"date": "1856-05-06", "time": "18:30", "tz": 1.0,
                   "place": "Pribor, Czech Republic",
                   "lat": 49.64, "lon": 18.15},
        events=[
            LifeEvent(1886, 30, "MARRIAGE", "Marries Martha Bernays", month=9, day=14),
            LifeEvent(1900, 44, "CAREER_PEAK", "Interpretation of Dreams published", month=11, day=4),
            LifeEvent(1923, 67, "HEALTH_CRISIS", "Cancer of jaw diagnosed", month=4),
            LifeEvent(1938, 82, "EXILE", "Flees Vienna for London", month=6, day=4),
            LifeEvent(1939, 83, "DEATH", "Doctor-assisted death", month=9, day=23),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Dalai Lama (14th)",
        birthdata={"date": "1935-07-06", "time": "04:38", "tz": 6.07,
                   "place": "Taktser, Tibet", "lat": 36.5, "lon": 101.5},
        events=[
            LifeEvent(1937, 2, "SPIRITUAL_AWAKENING", "Recognized as 14th Dalai Lama"),
            LifeEvent(1950, 15, "POLITICAL_OFFICE", "Assumes full political power", month=11, day=17),
            LifeEvent(1959, 23, "EXILE", "Flees to India after uprising", month=3, day=17),
            LifeEvent(1989, 54, "AWARD", "Nobel Peace Prize", month=10, day=5),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Pope John Paul II",
        birthdata={"date": "1920-05-18", "time": "17:30", "tz": 1.0,
                   "place": "Wadowice, Poland", "lat": 49.88, "lon": 19.5},
        events=[
            LifeEvent(1946, 26, "CAREER_START", "Ordained priest", month=11, day=1),
            LifeEvent(1978, 58, "POLITICAL_OFFICE", "Elected Pope", month=10, day=16),
            LifeEvent(1981, 60, "HEALTH_CRISIS", "Assassination attempt, survives", month=5, day=13),
            LifeEvent(2005, 84, "DEATH", "Dies of multi-organ failure", month=4, day=2),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),

    # ─── Tier 5: Indian celebrities & figures ────────────────────────────
    KnownChart(
        name="Amitabh Bachchan",
        birthdata={"date": "1942-10-11", "time": "03:30", "tz": 5.5, "place": "Allahabad (Prayagraj), India", "lat": 25.4358, "lon": 81.8463},
        events=[
            LifeEvent(1969, 27, "CAREER_START", "Bollywood debut Saat Hindustani", month=11, day=7),
            LifeEvent(1973, 30, "MARRIAGE", "Marries Jaya Bhaduri", month=6, day=3),
            LifeEvent(1973, 31, "CAREER_PEAK", "Zanjeer launches superstardom", month=5, day=11),
            LifeEvent(1982, 40, "HEALTH_CRISIS", "Near-fatal injury Coolie set", month=7, day=26),
            LifeEvent(2000, 58, "CAREER_PEAK", "KBC TV revival", month=7, day=3),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),
    KnownChart(
        name="Rajinikanth",
        birthdata={"date": "1950-12-12", "time": "23:55", "tz": 5.5,
                   "place": "Bangalore, India", "lat": 12.97, "lon": 77.59},
        events=[
            LifeEvent(1975, 24, "CAREER_START", "Apoorva Raagangal", month=8, day=15),
            LifeEvent(1981, 30, "MARRIAGE", "Marries Latha Rangachari", month=2, day=26),
            LifeEvent(2007, 56, "CAREER_PEAK", "Sivaji highest grosser", month=6, day=15),
            LifeEvent(2010, 60, "CAREER_PEAK", "Enthiran/Robot record"),
            LifeEvent(2011, 60, "HEALTH_CRISIS", "Hospitalized in Singapore", month=4, day=29),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="Mukesh Ambani",
        birthdata={"date": "1957-04-19", "time": "06:56", "tz": 3.0, "place": "Aden, Yemen", "lat": 12.7855, "lon": 45.0187},
        events=[
            LifeEvent(1985, 28, "MARRIAGE", "Marries Nita Ambani", month=3, day=8),
            LifeEvent(2002, 45, "MAJOR_LOSS", "Father Dhirubhai dies", month=7, day=6),
            LifeEvent(2005, 47, "FOUND_BUSINESS", "Splits Reliance with brother", month=6, day=18),
            LifeEvent(2016, 58, "FOUND_BUSINESS", "Launches Jio", month=9, day=5),
            LifeEvent(2018, 61, "AWARD", "Asia's richest person"),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="A R Rahman",
        birthdata={"date": "1967-01-06", "time": "05:50", "tz": 5.5, "place": "Chennai (Madras), Tamil Nadu, India", "lat": 13.0827, "lon": 80.2707},
        events=[
            LifeEvent(1992, 25, "CAREER_START", "Roja soundtrack", month=8, day=15),
            LifeEvent(1995, 28, "MARRIAGE", "Marries Saira Banu", month=3, day=12),
            LifeEvent(2009, 42, "AWARD", "Wins 2 Oscars (Slumdog Millionaire)", month=2, day=22),
            LifeEvent(2010, 43, "AWARD", "Padma Bhushan", month=1, day=26),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="Aishwarya Rai",
        birthdata={"date": "1973-11-01", "time": "04:55", "tz": 5.5, "place": "Mangalore, Karnataka, India", "lat": 12.9141, "lon": 74.856},
        events=[
            LifeEvent(1994, 21, "AWARD", "Miss World", month=11, day=19),
            LifeEvent(1997, 23, "CAREER_START", "Bollywood debut Iruvar", month=1, day=14),
            LifeEvent(2007, 33, "MARRIAGE", "Marries Abhishek Bachchan", month=4, day=20),
            LifeEvent(2011, 38, "CHILDREN_BORN", "Daughter Aaradhya born", month=11, day=16),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),

    # ─── Tier 6: Scientists / mathematicians ─────────────────────────────
    KnownChart(
        name="Stephen Hawking",
        birthdata={"date": "1942-01-08", "time": "01:39", "tz": 0.0, "place": "Oxford, England", "lat": 51.752, "lon": -1.2577},
        events=[
            LifeEvent(1963, 21, "HEALTH_CRISIS", "ALS diagnosed", month=1),
            LifeEvent(1965, 23, "MARRIAGE", "Marries Jane Wilde", month=7, day=14),
            LifeEvent(1988, 46, "CAREER_PEAK", "A Brief History of Time", month=4),
            LifeEvent(1995, 53, "DIVORCE", "Divorces Jane", month=10),
            LifeEvent(1995, 53, "MARRIAGE", "Marries Elaine Mason", month=9, day=16),
            LifeEvent(2018, 76, "DEATH", "Dies of ALS", month=3, day=14),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Marie Curie",
        birthdata={"date": "1867-11-07", "time": "12:00", "tz": 1.4,
                   "place": "Warsaw, Poland", "lat": 52.23, "lon": 21.01},
        events=[
            LifeEvent(1895, 27, "MARRIAGE", "Marries Pierre Curie", month=7, day=26),
            LifeEvent(1903, 35, "AWARD", "Nobel Prize Physics", month=12, day=10),
            LifeEvent(1906, 38, "MAJOR_LOSS", "Pierre dies in road accident", month=4, day=19),
            LifeEvent(1911, 43, "AWARD", "Nobel Prize Chemistry", month=12, day=10),
            LifeEvent(1934, 66, "DEATH", "Aplastic anemia from radiation", month=7, day=4),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),
    KnownChart(
        name="Isaac Newton",
        birthdata={"date": "1643-01-04", "time": "01:38", "tz": 0.0,
                   "place": "Woolsthorpe, England", "lat": 52.81, "lon": -0.62},
        events=[
            LifeEvent(1666, 23, "SPIRITUAL_AWAKENING", "Annus Mirabilis (calculus, gravity, optics)", month=8),
            LifeEvent(1687, 44, "CAREER_PEAK", "Principia Mathematica published", month=7, day=5),
            LifeEvent(1727, 84, "DEATH", "Dies in sleep", month=3, day=31),
        ],
        source="Astrodienst Rodden C (Julian calendar uncertainty)",
        quality="C",
    ),

    # ─── Tier 7: Athletes ────────────────────────────────────────────────
    KnownChart(
        name="Muhammad Ali",
        birthdata={"date": "1942-01-17", "time": "18:35", "tz": -6.0,
                   "place": "Louisville, KY, USA", "lat": 38.25, "lon": -85.76},
        events=[
            LifeEvent(1960, 18, "AWARD", "Olympic gold Rome", month=9, day=5),
            LifeEvent(1964, 22, "CAREER_PEAK", "Beats Sonny Liston, world champ", month=2, day=25),
            LifeEvent(1967, 25, "MAJOR_LOSS", "Stripped of title (Vietnam refusal)", month=4, day=28),
            LifeEvent(1971, 29, "MAJOR_LOSS", "Loses Fight of the Century to Frazier", month=3, day=8),
            LifeEvent(1974, 32, "CAREER_PEAK", "Rumble in the Jungle vs Foreman", month=10, day=30),
            LifeEvent(1984, 42, "HEALTH_CRISIS", "Parkinson's diagnosed", month=9),
            LifeEvent(2016, 74, "DEATH", "Septic shock", month=6, day=3),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Cristiano Ronaldo",
        birthdata={"date": "1985-02-05", "time": "05:25", "tz": 0.0,
                   "place": "Funchal, Madeira, Portugal", "lat": 32.65, "lon": -16.91},
        events=[
            LifeEvent(2003, 18, "CAREER_START", "Signs for Manchester United", month=8, day=12),
            LifeEvent(2008, 23, "AWARD", "First Ballon d'Or", month=12, day=2),
            LifeEvent(2010, 25, "CHILDREN_BORN", "Cristiano Jr born", month=6, day=17),
            LifeEvent(2016, 31, "AWARD", "Wins Euro with Portugal", month=7, day=10),
            LifeEvent(2022, 37, "MAJOR_LOSS", "Acrimonious exit from Man Utd", month=11, day=22),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="Lionel Messi",
        birthdata={"date": "1987-06-24", "time": "06:05", "tz": -3.0,
                   "place": "Rosario, Argentina", "lat": -32.95, "lon": -60.65},
        events=[
            LifeEvent(2004, 17, "CAREER_START", "Barcelona first team debut", month=10, day=16),
            LifeEvent(2009, 22, "AWARD", "First Ballon d'Or", month=12, day=1),
            LifeEvent(2017, 30, "MARRIAGE", "Marries Antonela Roccuzzo", month=6, day=30),
            LifeEvent(2022, 35, "AWARD", "Wins World Cup", month=12, day=18),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="Serena Williams",
        birthdata={"date": "1981-09-26", "time": "20:28", "tz": -7.0,
                   "place": "Saginaw, MI, USA", "lat": 43.42, "lon": -83.95},
        events=[
            LifeEvent(1999, 17, "AWARD", "First Grand Slam (US Open)", month=9, day=11),
            LifeEvent(2017, 35, "MARRIAGE", "Marries Alexis Ohanian", month=11, day=16),
            LifeEvent(2017, 35, "CHILDREN_BORN", "Olympia born", month=9, day=1),
            LifeEvent(2017, 36, "AWARD", "Australian Open while pregnant", month=1, day=28),
            LifeEvent(2022, 41, "CAREER_END", "Retires from tennis", month=9, day=2),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),

    # ─── Tier 8: Indian PMs / political ──────────────────────────────────
    KnownChart(
        name="Jawaharlal Nehru",
        birthdata={"date": "1889-11-14", "time": "23:12", "tz": 5.32,
                   "place": "Allahabad, India", "lat": 25.43, "lon": 81.85},
        events=[
            LifeEvent(1916, 26, "MARRIAGE", "Marries Kamala Kaul", month=2, day=8),
            LifeEvent(1917, 27, "CHILDREN_BORN", "Indira born", month=11, day=19),
            LifeEvent(1942, 53, "IMPRISONMENT", "Quit India arrest", month=8, day=9),
            LifeEvent(1947, 57, "POLITICAL_OFFICE", "First PM of India", month=8, day=15),
            LifeEvent(1962, 73, "MAJOR_LOSS", "Defeat in Sino-Indian war", month=11),
            LifeEvent(1964, 74, "DEATH", "Heart attack", month=5, day=27),
        ],
        source="Astrodienst Rodden A",
        quality="A",
    ),
    KnownChart(
        name="Atal Bihari Vajpayee",
        birthdata={"date": "1924-12-25", "time": "05:00", "tz": 5.5,
                   "place": "Gwalior, India", "lat": 26.21, "lon": 78.18},
        events=[
            LifeEvent(1996, 71, "POLITICAL_OFFICE", "13-day PM", month=5, day=16),
            LifeEvent(1998, 73, "POLITICAL_OFFICE", "PM 2nd term", month=3, day=19),
            LifeEvent(1999, 74, "POLITICAL_OFFICE", "PM 3rd term post-Kargil", month=10, day=13),
            LifeEvent(2018, 93, "DEATH", "Long illness", month=8, day=16),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),
    KnownChart(
        name="Rajiv Gandhi",
        birthdata={"date": "1944-08-20", "time": "08:11", "tz": 5.5,
                   "place": "Mumbai, India", "lat": 19.07, "lon": 72.88},
        events=[
            LifeEvent(1968, 23, "MARRIAGE", "Marries Sonia Maino", month=2, day=25),
            LifeEvent(1980, 36, "MAJOR_LOSS", "Brother Sanjay dies", month=6, day=23),
            LifeEvent(1984, 40, "POLITICAL_OFFICE", "Becomes PM after Indira's death", month=10, day=31),
            LifeEvent(1989, 45, "MAJOR_LOSS", "Loses elections", month=12, day=2),
            LifeEvent(1991, 46, "DEATH", "Assassinated by LTTE bomb", month=5, day=21),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),
    KnownChart(
        name="A P J Abdul Kalam",
        birthdata={"date": "1931-10-15", "time": "01:35", "tz": 5.5,
                   "place": "Rameswaram, India", "lat": 9.28, "lon": 79.31},
        events=[
            LifeEvent(1980, 49, "AWARD", "Padma Bhushan (SLV-3 success)", month=1, day=26),
            LifeEvent(1998, 67, "AWARD", "Bharat Ratna (Pokhran-II)", month=12, day=25),
            LifeEvent(2002, 70, "POLITICAL_OFFICE", "President of India", month=7, day=25),
            LifeEvent(2015, 83, "DEATH", "Cardiac arrest while lecturing", month=7, day=27),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),

    # ─── Tier 9: Gurus & spiritual ──────────────────────────────────────
    KnownChart(
        name="Sathya Sai Baba",
        birthdata={"date": "1926-11-23", "time": "06:00", "tz": 5.5,
                   "place": "Puttaparthi, India", "lat": 14.16, "lon": 77.81},
        events=[
            LifeEvent(1940, 13, "SPIRITUAL_AWAKENING", "Declares Sai Baba avatar", month=10, day=20),
            LifeEvent(1990, 63, "FOUND_BUSINESS", "Super-Specialty Hospital opens", month=11, day=22),
            LifeEvent(2011, 84, "DEATH", "Multiple organ failure", month=4, day=24),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),
    KnownChart(
        name="Osho (Rajneesh)",
        birthdata={"date": "1931-12-11", "time": "17:13", "tz": 5.5,
                   "place": "Kuchwada, India", "lat": 22.5, "lon": 78.0},
        events=[
            LifeEvent(1953, 21, "SPIRITUAL_AWAKENING", "Enlightenment experience under tree", month=3, day=21),
            LifeEvent(1981, 49, "EXILE", "Moves to Oregon, USA", month=6),
            LifeEvent(1985, 53, "IMPRISONMENT", "Arrested in Oregon", month=10, day=28),
            LifeEvent(1985, 53, "EXILE", "Deported back to India", month=11, day=14),
            LifeEvent(1990, 58, "DEATH", "Heart failure", month=1, day=19),
        ],
        source="Astrodienst Rodden C",
        quality="C",
    ),
    KnownChart(
        name="Paramahansa Yogananda",
        birthdata={"date": "1893-01-05", "time": "20:38", "tz": 5.88,
                   "place": "Gorakhpur, India", "lat": 26.76, "lon": 83.37},
        events=[
            LifeEvent(1920, 27, "EXILE", "Sails to USA", month=8, day=19),
            LifeEvent(1925, 32, "FOUND_BUSINESS", "Founds SRF headquarters", month=8),
            LifeEvent(1946, 53, "CAREER_PEAK", "Autobiography of a Yogi published", month=12),
            LifeEvent(1952, 59, "DEATH", "Mahasamadhi during talk", month=3, day=7),
        ],
        source="SRF official",
        quality="A",
    ),

    # ─── Tier 10: Fictional/historical impact ────────────────────────────
    KnownChart(
        name="Charles Darwin",
        birthdata={"date": "1809-02-12", "time": "06:00", "tz": 0.0,
                   "place": "Shrewsbury, England", "lat": 52.71, "lon": -2.75},
        events=[
            LifeEvent(1831, 22, "EXILE", "Sails on HMS Beagle", month=12, day=27),
            LifeEvent(1836, 27, "CAREER_START", "Returns to England", month=10, day=2),
            LifeEvent(1839, 30, "MARRIAGE", "Marries Emma Wedgwood", month=1, day=29),
            LifeEvent(1859, 50, "CAREER_PEAK", "Origin of Species published", month=11, day=24),
            LifeEvent(1882, 73, "DEATH", "Heart failure", month=4, day=19),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),
    KnownChart(
        name="Karl Marx",
        birthdata={"date": "1818-05-05", "time": "02:00", "tz": 0.5,
                   "place": "Trier, Germany", "lat": 49.76, "lon": 6.64},
        events=[
            LifeEvent(1843, 25, "MARRIAGE", "Marries Jenny von Westphalen", month=6, day=19),
            LifeEvent(1848, 29, "CAREER_PEAK", "Communist Manifesto", month=2, day=21),
            LifeEvent(1849, 31, "EXILE", "Exiled to London", month=8, day=24),
            LifeEvent(1867, 49, "CAREER_PEAK", "Das Kapital Vol 1", month=9, day=14),
            LifeEvent(1883, 64, "DEATH", "Bronchitis/pleurisy", month=3, day=14),
        ],
        source="Astrodienst Rodden B",
        quality="B",
    ),
]


def all_charts() -> tuple[KnownChart, ...]:
    return tuple(KNOWN_CHARTS)


def by_quality(min_quality: str = "A") -> list[KnownChart]:
    rank = {"A": 4, "B": 3, "C": 2, "DD": 1}
    threshold = rank.get(min_quality, 1)
    return [c for c in KNOWN_CHARTS if rank.get(c.quality, 1) >= threshold]


def by_event_type(event_type: str) -> list[tuple[KnownChart, LifeEvent]]:
    out = []
    for c in KNOWN_CHARTS:
        for ev in c.events:
            if ev.event_type == event_type:
                out.append((c, ev))
    return out


def stats() -> dict:
    n_charts = len(KNOWN_CHARTS)
    total_events = sum(len(c.events) for c in KNOWN_CHARTS)
    by_q: dict[str, int] = {}
    by_evt: dict[str, int] = {}
    for c in KNOWN_CHARTS:
        by_q[c.quality] = by_q.get(c.quality, 0) + 1
        for ev in c.events:
            by_evt[ev.event_type] = by_evt.get(ev.event_type, 0) + 1
    return {
        "n_charts": n_charts,
        "total_events": total_events,
        "by_quality": by_q,
        "by_event_type": by_evt,
        "names": [c.name for c in KNOWN_CHARTS],
    }
