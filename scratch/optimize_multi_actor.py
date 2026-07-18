import asyncio
import os
import sys
import json
import math
import re
from datetime import datetime
import swisseph as swe

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from main import jathagam, BirthData
from engine.corpus import get_corpus
from engine.dasha import current_dasha
from engine.gochar import get_transit_snapshot, SIGN_NAMES
from engine.evaluator import get_functional_nature
from engine.tajik import annual_chart
from engine.numerology_engine import compute_pythagorean_triad, compute_personal_cycles

swe.set_sid_mode(swe.SIDM_LAHIRI)

# ═══════════════════════════════════════════════════════════════════════════════
# FULL ACTOR REGISTRY — Complete career filmographies
# ═══════════════════════════════════════════════════════════════════════════════

ACTORS = [

# ─── 1. RAJINIKANTH ──────────────────────────────────────────────────────────
{
    "name": "Rajinikanth",
    "dob": "1950-12-12",
    "birth_time": "18:15",
    "lat": 12.9716, "lon": 77.5946,
    "slug": "rajinikanth",
    "films": [
        # 1975
        {"num":1,  "name":"Apoorva Raagangal",       "date":"1975-08-22","status":"Hit",         "valence":"auspicious"},
        # 1976
        {"num":2,  "name":"Katha Sangama",            "date":"1976-01-01","status":"Hit",         "valence":"auspicious"},
        {"num":3,  "name":"Anthuleni Katha",          "date":"1976-04-01","status":"Hit",         "valence":"auspicious"},
        {"num":4,  "name":"Moondru Mudichu",          "date":"1976-07-22","status":"Blockbuster", "valence":"auspicious"},
        {"num":5,  "name":"Baalu Jenu",               "date":"1976-10-01","status":"Hit",         "valence":"auspicious"},
        # 1977
        {"num":6,  "name":"Avargal",                  "date":"1977-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":7,  "name":"16 Vayathinile",           "date":"1977-07-15","status":"Blockbuster", "valence":"auspicious"},
        {"num":8,  "name":"Aadu Puli Attam",          "date":"1977-10-07","status":"Hit",         "valence":"auspicious"},
        {"num":9,  "name":"Gayathri",                 "date":"1977-11-01","status":"Hit",         "valence":"auspicious"},
        {"num":10, "name":"Aarilirunthu Arubathu Varai","date":"1977-12-01","status":"Hit",      "valence":"auspicious"},
        # 1978
        {"num":11, "name":"Ilamai Oonjal Aadukirathu","date":"1978-01-14","status":"Hit",        "valence":"auspicious"},
        {"num":12, "name":"Shankar Salim Simon",      "date":"1978-04-01","status":"Hit",         "valence":"auspicious"},
        {"num":13, "name":"Bairavi",                  "date":"1978-06-01","status":"Blockbuster", "valence":"auspicious"},
        {"num":14, "name":"Mullum Malarum",           "date":"1978-10-01","status":"Blockbuster", "valence":"auspicious"},
        {"num":15, "name":"Vanakkatukuriya Kathaliye","date":"1978-12-01","status":"Hit",         "valence":"auspicious"},
        # 1979
        {"num":16, "name":"Ninaithale Inikkum",       "date":"1979-01-26","status":"Blockbuster", "valence":"auspicious"},
        {"num":17, "name":"Kuppathu Raja",            "date":"1979-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":18, "name":"Aarambham",                "date":"1979-06-01","status":"Hit",         "valence":"auspicious"},
        {"num":19, "name":"Naan Potta Savaal",        "date":"1979-08-01","status":"Hit",         "valence":"auspicious"},
        {"num":20, "name":"Annakili",                 "date":"1979-09-07","status":"Hit",         "valence":"auspicious"},
        {"num":21, "name":"Dharma Yuddham",           "date":"1979-10-01","status":"Hit",         "valence":"auspicious"},
        {"num":22, "name":"Allauddinum Arputha Vilakkum","date":"1979-11-01","status":"Flop",    "valence":"inauspicious"},
        # 1980
        {"num":23, "name":"Billa",                    "date":"1980-04-05","status":"Blockbuster", "valence":"auspicious"},
        {"num":24, "name":"Murattu Kaalai",           "date":"1980-07-18","status":"Blockbuster", "valence":"auspicious"},
        {"num":25, "name":"Ram Robert Rahim",         "date":"1980-08-15","status":"Hit",         "valence":"auspicious"},
        {"num":26, "name":"Kaali",                    "date":"1980-10-01","status":"Hit",         "valence":"auspicious"},
        {"num":27, "name":"Johnny",                   "date":"1980-11-14","status":"Hit",         "valence":"auspicious"},
        # 1981
        {"num":28, "name":"Thillu Mullu",             "date":"1981-04-17","status":"Blockbuster", "valence":"auspicious"},
        {"num":29, "name":"Naan Vazhavaippen",        "date":"1981-06-01","status":"Hit",         "valence":"auspicious"},
        {"num":30, "name":"Garjanai",                 "date":"1981-08-01","status":"Hit",         "valence":"auspicious"},
        {"num":31, "name":"Anbukku Naan Adimai",      "date":"1981-09-01","status":"Hit",         "valence":"auspicious"},
        {"num":32, "name":"Nool Veli",                "date":"1981-11-06","status":"Hit",         "valence":"auspicious"},
        {"num":33, "name":"Thanga Magan",             "date":"1981-12-01","status":"Blockbuster", "valence":"auspicious"},
        # 1982
        {"num":34, "name":"Polladhavan",              "date":"1982-04-01","status":"Blockbuster", "valence":"auspicious"},
        {"num":35, "name":"Ranga",                    "date":"1982-10-22","status":"Hit",         "valence":"auspicious"},
        {"num":36, "name":"Puthukavithai",            "date":"1982-06-01","status":"Flop",        "valence":"inauspicious"},
        {"num":37, "name":"Moondru Mugam",            "date":"1982-08-14","status":"Hit",         "valence":"auspicious"},
        {"num":38, "name":"Paayum Puli",              "date":"1983-01-14","status":"Blockbuster", "valence":"auspicious"},
        # 1983
        {"num":39, "name":"Thanga Magan",             "date":"1983-04-01","status":"Hit",         "valence":"auspicious"},
        {"num":40, "name":"Andha Kanoon",             "date":"1983-05-27","status":"Blockbuster", "valence":"auspicious"},
        {"num":41, "name":"Anbulla Rajinikanth",      "date":"1984-01-14","status":"Hit",         "valence":"auspicious"},
        # 1984
        {"num":42, "name":"Nallavanuku Nallavan",     "date":"1984-02-10","status":"Hit",         "valence":"auspicious"},
        {"num":43, "name":"Thambikku Entha Ooru",     "date":"1984-04-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":44, "name":"Kai Kodukkum Kai",         "date":"1984-08-01","status":"Hit",         "valence":"auspicious"},
        {"num":45, "name":"Naan Sigappu Manithan",    "date":"1985-01-14","status":"Hit",         "valence":"auspicious"},
        # 1985
        {"num":46, "name":"Padikkadavan",             "date":"1985-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":47, "name":"Sri Ragavendra",           "date":"1985-06-01","status":"Hit",         "valence":"auspicious"},
        {"num":48, "name":"Naan Adimai Illai",        "date":"1986-01-14","status":"Hit",         "valence":"auspicious"},
        # 1986
        {"num":49, "name":"Mr. Bharath",              "date":"1986-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":50, "name":"Viduthalai",               "date":"1986-06-01","status":"Hit",         "valence":"auspicious"},
        # 1987
        {"num":51, "name":"Velaikaran",               "date":"1987-01-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":52, "name":"Manithan",                 "date":"1987-07-01","status":"Hit",         "valence":"auspicious"},
        # 1988
        {"num":53, "name":"Dharmathin Thalaivan",     "date":"1988-01-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":54, "name":"Bloodstone",               "date":"1988-06-01","status":"Flop",        "valence":"inauspicious"},
        # 1989
        {"num":55, "name":"Rajadhi Raja",             "date":"1989-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":56, "name":"Mappillai",                "date":"1989-04-14","status":"Blockbuster", "valence":"auspicious"},
        # 1990
        {"num":57, "name":"Panakkaran",               "date":"1990-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":58, "name":"Siva",                     "date":"1990-04-14","status":"Blockbuster", "valence":"auspicious"},
        # 1991
        {"num":59, "name":"Thalapathi",               "date":"1991-09-12","status":"Blockbuster", "valence":"auspicious"},
        {"num":60, "name":"Mannan",                   "date":"1992-04-14","status":"Blockbuster", "valence":"auspicious"},
        # 1992
        {"num":61, "name":"Annaamalai",               "date":"1992-09-01","status":"Blockbuster", "valence":"auspicious"},
        # 1993
        {"num":62, "name":"Uzhaippali",               "date":"1993-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":63, "name":"Valli",                    "date":"1993-04-14","status":"Flop",        "valence":"inauspicious"},
        {"num":64, "name":"Yejaman",                  "date":"1993-08-01","status":"Blockbuster", "valence":"auspicious"},
        {"num":65, "name":"Veera",                    "date":"1994-01-14","status":"Hit",         "valence":"auspicious"},
        # 1995
        {"num":66, "name":"Baasha",                   "date":"1995-01-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":67, "name":"Muthu",                    "date":"1995-04-14","status":"Blockbuster", "valence":"auspicious"},
        # 1997
        {"num":68, "name":"Arunachalam",              "date":"1997-01-12","status":"Blockbuster", "valence":"auspicious"},
        # 1999
        {"num":69, "name":"Padayappa",                "date":"1999-04-10","status":"Blockbuster", "valence":"auspicious"},
        # 2002
        {"num":70, "name":"Baba",                     "date":"2002-08-15","status":"Flop",        "valence":"inauspicious"},
        # 2005
        {"num":71, "name":"Chandramukhi",             "date":"2005-04-14","status":"Blockbuster", "valence":"auspicious"},
        # 2007
        {"num":72, "name":"Sivaji",                   "date":"2007-06-15","status":"Blockbuster", "valence":"auspicious"},
        # 2008
        {"num":73, "name":"Kuselan",                  "date":"2008-08-01","status":"Flop",        "valence":"inauspicious"},
        # 2010
        {"num":74, "name":"Enthiran",                 "date":"2010-10-01","status":"Blockbuster", "valence":"auspicious"},
        # 2014
        {"num":75, "name":"Kochadaiiyaan",            "date":"2014-05-23","status":"Flop",        "valence":"inauspicious"},
        {"num":76, "name":"Lingaa",                   "date":"2014-12-12","status":"Flop",        "valence":"inauspicious"},
        # 2016
        {"num":77, "name":"Kabali",                   "date":"2016-07-22","status":"Hit",         "valence":"auspicious"},
        # 2018
        {"num":78, "name":"Kaala",                    "date":"2018-06-07","status":"Flop",        "valence":"inauspicious"},
        {"num":79, "name":"2.0",                      "date":"2018-11-29","status":"Blockbuster", "valence":"auspicious"},
        # 2019
        {"num":80, "name":"Petta",                    "date":"2019-01-10","status":"Hit",         "valence":"auspicious"},
        # 2020
        {"num":81, "name":"Darbar",                   "date":"2020-01-09","status":"Flop",        "valence":"inauspicious"},
        # 2021
        {"num":82, "name":"Annaatthe",                "date":"2021-11-04","status":"Hit",         "valence":"auspicious"},
        # 2023
        {"num":83, "name":"Jailer",                   "date":"2023-08-10","status":"Blockbuster", "valence":"auspicious"},
        # 2024
        {"num":84, "name":"Vettaiyan",                "date":"2024-10-10","status":"Hit",         "valence":"auspicious"},
    ]
},

# ─── 2. KAMAL HAASAN ─────────────────────────────────────────────────────────
{
    "name": "Kamal Haasan",
    "dob": "1954-11-07",
    "birth_time": "03:30",
    "lat": 9.3167, "lon": 78.5667,
    "slug": "kamal_haasan",
    "films": [
        # 1975
        {"num":1,  "name":"Apoorva Raagangal",        "date":"1975-08-22","status":"Hit",         "valence":"auspicious"},
        {"num":2,  "name":"Melnaattu Marumagal",      "date":"1975-11-01","status":"Hit",         "valence":"auspicious"},
        # 1976
        {"num":3,  "name":"Moondru Mudichu",          "date":"1976-07-22","status":"Blockbuster", "valence":"auspicious"},
        {"num":4,  "name":"Manmadha Leelai",          "date":"1976-10-01","status":"Hit",         "valence":"auspicious"},
        {"num":5,  "name":"Oru Nadigai Natakam Paarkiral","date":"1978-01-01","status":"Hit",    "valence":"auspicious"},
        # 1977
        {"num":6,  "name":"16 Vayathinile",           "date":"1977-07-15","status":"Blockbuster", "valence":"auspicious"},
        {"num":7,  "name":"Aaina",                    "date":"1977-10-01","status":"Hit",         "valence":"auspicious"},
        # 1978
        {"num":8,  "name":"Sigappu Rojakkal",         "date":"1978-06-01","status":"Hit",         "valence":"auspicious"},
        {"num":9,  "name":"Varumayin Niram Sigappu",  "date":"1980-01-01","status":"Hit",         "valence":"auspicious"},
        # 1979
        {"num":10, "name":"Ninaithale Inikkum",       "date":"1979-01-26","status":"Blockbuster", "valence":"auspicious"},
        {"num":11, "name":"Azhiyatha Kolangal",       "date":"1979-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":12, "name":"Kalyanaraman",             "date":"1979-11-15","status":"Blockbuster", "valence":"auspicious"},
        # 1980
        {"num":13, "name":"Guru",                     "date":"1980-04-01","status":"Hit",         "valence":"auspicious"},
        {"num":14, "name":"Nool Veli",                "date":"1981-11-06","status":"Hit",         "valence":"auspicious"},
        # 1981
        {"num":15, "name":"Kadal Meengal",            "date":"1981-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":16, "name":"Raja Paarvai",             "date":"1981-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":17, "name":"Meendum Kokila",           "date":"1981-07-01","status":"Hit",         "valence":"auspicious"},
        {"num":18, "name":"Ellam Inba Mayam",         "date":"1981-10-01","status":"Hit",         "valence":"auspicious"},
        # 1982
        {"num":19, "name":"Moonram Pirai",            "date":"1982-01-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":20, "name":"Simla Special",            "date":"1982-04-01","status":"Hit",         "valence":"auspicious"},
        {"num":21, "name":"Agni Sakshi",              "date":"1982-07-01","status":"Hit",         "valence":"auspicious"},
        {"num":22, "name":"Moondram Pirai",           "date":"1982-10-01","status":"Hit",         "valence":"auspicious"},
        # 1983
        {"num":23, "name":"Sagara Sangamam",          "date":"1983-10-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":24, "name":"Sadma",                    "date":"1983-02-25","status":"Hit",         "valence":"auspicious"},
        {"num":25, "name":"Thoongaadhe Thambi Thoongaadhe","date":"1983-06-01","status":"Hit",  "valence":"auspicious"},
        # 1984
        {"num":26, "name":"Enakkul Oruvan",           "date":"1984-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":27, "name":"Ek Duuje Ke Liye sequel",  "date":"1984-04-01","status":"Hit",         "valence":"auspicious"},
        # 1985
        {"num":28, "name":"Japanil Kalyanaraman",     "date":"1985-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":29, "name":"Uyarndha Manithan",        "date":"1985-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":30, "name":"Gerafthar",                "date":"1985-07-19","status":"Flop",        "valence":"inauspicious"},
        # 1986
        {"num":31, "name":"Vikram",                   "date":"1986-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":32, "name":"Punnagai Mannan",          "date":"1986-10-01","status":"Blockbuster", "valence":"auspicious"},
        # 1987
        {"num":33, "name":"Nayakan",                  "date":"1987-10-21","status":"Blockbuster", "valence":"auspicious"},
        {"num":34, "name":"Per Sollum Pillai",        "date":"1987-04-01","status":"Hit",         "valence":"auspicious"},
        # 1988
        {"num":35, "name":"Pushpaka Vimana",          "date":"1988-01-15","status":"Hit",         "valence":"auspicious"},
        {"num":36, "name":"Sathyaa",                  "date":"1988-07-01","status":"Hit",         "valence":"auspicious"},
        {"num":37, "name":"Unnal Mudiyum Thambi",     "date":"1988-10-01","status":"Hit",         "valence":"auspicious"},
        # 1989
        {"num":38, "name":"Chanakyan",                "date":"1989-01-01","status":"Hit",         "valence":"auspicious"},
        {"num":39, "name":"Vetri Vizha",              "date":"1989-07-01","status":"Hit",         "valence":"auspicious"},
        {"num":40, "name":"Apoorva Sagodharargal",    "date":"1989-09-14","status":"Blockbuster", "valence":"auspicious"},
        # 1990
        {"num":41, "name":"Michael Madana Kama Rajan","date":"1990-01-14","status":"Blockbuster", "valence":"auspicious"},
        # 1991
        {"num":42, "name":"Guna",                     "date":"1991-09-01","status":"Flop",        "valence":"inauspicious"},
        {"num":43, "name":"Singaravelan",             "date":"1992-01-14","status":"Hit",         "valence":"auspicious"},
        # 1992
        {"num":44, "name":"Thevar Magan",             "date":"1992-10-14","status":"Blockbuster", "valence":"auspicious"},
        # 1993
        {"num":45, "name":"Maharasan",                "date":"1993-04-14","status":"Flop",        "valence":"inauspicious"},
        {"num":46, "name":"Kalaignan",                "date":"1993-11-01","status":"Hit",         "valence":"auspicious"},
        # 1994
        {"num":47, "name":"Mahanadi",                 "date":"1994-07-01","status":"Hit",         "valence":"auspicious"},
        {"num":48, "name":"Nammavar",                 "date":"1994-11-01","status":"Hit",         "valence":"auspicious"},
        {"num":49, "name":"Magalir Mattum",           "date":"1994-01-14","status":"Flop",        "valence":"inauspicious"},
        # 1995
        {"num":50, "name":"Sathi Leelavathi",         "date":"1995-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":51, "name":"Kuruthipunal",             "date":"1995-04-13","status":"Hit",         "valence":"auspicious"},
        # 1996
        {"num":52, "name":"Indian",                   "date":"1996-03-29","status":"Blockbuster", "valence":"auspicious"},
        {"num":53, "name":"Avvai Shanmughi",          "date":"1996-11-01","status":"Blockbuster", "valence":"auspicious"},
        # 1997
        {"num":54, "name":"Chachi 420",               "date":"1997-12-19","status":"Blockbuster", "valence":"auspicious"},
        # 1998
        {"num":55, "name":"Kaathala Kaathala",        "date":"1998-01-14","status":"Hit",         "valence":"auspicious"},
        # 2000
        {"num":56, "name":"Hey Ram",                  "date":"2000-02-25","status":"Flop",        "valence":"inauspicious"},
        {"num":57, "name":"Thenali",                  "date":"2000-11-17","status":"Hit",         "valence":"auspicious"},
        # 2001
        {"num":58, "name":"Aalavandhan",              "date":"2001-10-05","status":"Flop",        "valence":"inauspicious"},
        # 2002
        {"num":59, "name":"Pammal K. Sambandam",      "date":"2002-05-10","status":"Blockbuster", "valence":"auspicious"},
        # 2003
        {"num":60, "name":"Anbe Sivam",               "date":"2003-01-14","status":"Flop",        "valence":"inauspicious"},
        {"num":61, "name":"Nala Damayanthi",          "date":"2003-08-15","status":"Hit",         "valence":"auspicious"},
        # 2004
        {"num":62, "name":"Vasool Raja MBBS",         "date":"2004-01-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":63, "name":"Virumaandi",               "date":"2004-12-17","status":"Hit",         "valence":"auspicious"},
        # 2005
        {"num":64, "name":"Mumbai Express",           "date":"2005-08-12","status":"Flop",        "valence":"inauspicious"},
        # 2006
        {"num":65, "name":"Vettaiyaadu Vilaiyaadu",   "date":"2006-05-01","status":"Hit",         "valence":"auspicious"},
        # 2008
        {"num":66, "name":"Dasavathaaram",            "date":"2008-06-13","status":"Blockbuster", "valence":"auspicious"},
        # 2009
        {"num":67, "name":"Unnaipol Oruvan",          "date":"2009-09-25","status":"Hit",         "valence":"auspicious"},
        # 2010
        {"num":68, "name":"Manmadan Ambu",            "date":"2010-12-23","status":"Flop",        "valence":"inauspicious"},
        # 2013
        {"num":69, "name":"Vishwaroopam",             "date":"2013-02-07","status":"Hit",         "valence":"auspicious"},
        # 2014
        {"num":70, "name":"Uttama Villain",           "date":"2015-05-01","status":"Flop",        "valence":"inauspicious"},
        {"num":71, "name":"Papanasam",                "date":"2015-07-03","status":"Hit",         "valence":"auspicious"},
        # 2016
        {"num":72, "name":"Thoongaa Vanam",           "date":"2015-11-12","status":"Flop",        "valence":"inauspicious"},
        # 2018
        {"num":73, "name":"Vishwaroopam 2",           "date":"2018-08-10","status":"Flop",        "valence":"inauspicious"},
        # 2022
        {"num":74, "name":"Vikram",                   "date":"2022-06-03","status":"Blockbuster", "valence":"auspicious"},
        # 2024
        {"num":75, "name":"Indian 2",                 "date":"2024-07-12","status":"Flop",        "valence":"inauspicious"},
    ]
},

# ─── 3. AJITH KUMAR ──────────────────────────────────────────────────────────
{
    "name": "Ajith Kumar",
    "dob": "1971-05-01",
    "birth_time": "06:00",
    "lat": 17.3850, "lon": 78.4867,
    "slug": "ajith",
    "films": [
        {"num":1,  "name":"En Veedu En Kanavar",      "date":"1992-01-01","status":"Flop",        "valence":"inauspicious"},
        {"num":2,  "name":"Amaravathi",               "date":"1993-10-01","status":"Flop",        "valence":"inauspicious"},
        {"num":3,  "name":"Paasamalargal",            "date":"1994-01-01","status":"Flop",        "valence":"inauspicious"},
        {"num":4,  "name":"Pavithra",                 "date":"1994-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":5,  "name":"Raasi",                    "date":"1994-06-01","status":"Hit",         "valence":"auspicious"},
        {"num":6,  "name":"Aasai",                    "date":"1995-09-01","status":"Hit",         "valence":"auspicious"},
        {"num":7,  "name":"Aval Varuvala",            "date":"1996-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":8,  "name":"Kadhal Kottai",            "date":"1996-11-01","status":"Blockbuster", "valence":"auspicious"},
        {"num":9,  "name":"Minor Mappillai",          "date":"1996-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":10, "name":"Ullasam",                  "date":"1997-04-01","status":"Flop",        "valence":"inauspicious"},
        {"num":11, "name":"Pagaivan",                 "date":"1997-07-01","status":"Flop",        "valence":"inauspicious"},
        {"num":12, "name":"Kadhal Mannan",            "date":"1998-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":13, "name":"Unnai Thedi",              "date":"1999-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":14, "name":"Amarkalam",                "date":"1999-05-01","status":"Hit",         "valence":"auspicious"},
        {"num":15, "name":"Vaali",                    "date":"1999-04-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":16, "name":"Kandukonden Kandukonden",  "date":"2000-01-28","status":"Hit",         "valence":"auspicious"},
        {"num":17, "name":"Mugavaree",                "date":"2000-09-01","status":"Flop",        "valence":"inauspicious"},
        {"num":18, "name":"Dheena",                   "date":"2001-04-13","status":"Blockbuster", "valence":"auspicious"},
        {"num":19, "name":"Poovellam Kettuppaar",     "date":"1999-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":20, "name":"Citizen",                  "date":"2001-11-14","status":"Hit",         "valence":"auspicious"},
        {"num":21, "name":"Red",                      "date":"2002-04-14","status":"Flop",        "valence":"inauspicious"},
        {"num":22, "name":"Villain",                  "date":"2002-08-15","status":"Flop",        "valence":"inauspicious"},
        {"num":23, "name":"Unnai Kaanadha Naan",      "date":"2002-11-01","status":"Flop",        "valence":"inauspicious"},
        {"num":24, "name":"Ennai Thalatta Varuvala",  "date":"2003-01-14","status":"Flop",        "valence":"inauspicious"},
        {"num":25, "name":"Ji",                       "date":"2004-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":26, "name":"Jana",                     "date":"2004-06-01","status":"Flop",        "valence":"inauspicious"},
        {"num":27, "name":"Attagasam",                "date":"2004-11-12","status":"Flop",        "valence":"inauspicious"},
        {"num":28, "name":"Paramasivan",              "date":"2006-03-31","status":"Flop",        "valence":"inauspicious"},
        {"num":29, "name":"Varalaru",                 "date":"2006-09-01","status":"Hit",         "valence":"auspicious"},
        {"num":30, "name":"Thirupathi",               "date":"2006-06-01","status":"Flop",        "valence":"inauspicious"},
        {"num":31, "name":"Aalwar",                   "date":"2007-01-12","status":"Flop",        "valence":"inauspicious"},
        {"num":32, "name":"Kireedam",                 "date":"2007-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":33, "name":"Billa",                    "date":"2007-11-14","status":"Hit",         "valence":"auspicious"},
        {"num":34, "name":"Aegan",                    "date":"2008-10-14","status":"Flop",        "valence":"inauspicious"},
        {"num":35, "name":"Asal",                     "date":"2010-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":36, "name":"Mankatha",                 "date":"2011-08-31","status":"Blockbuster", "valence":"auspicious"},
        {"num":37, "name":"Billa 2",                  "date":"2012-07-11","status":"Flop",        "valence":"inauspicious"},
        {"num":38, "name":"Arrambam",                 "date":"2013-10-25","status":"Hit",         "valence":"auspicious"},
        {"num":39, "name":"Veeram",                   "date":"2014-01-10","status":"Hit",         "valence":"auspicious"},
        {"num":40, "name":"Yennai Arindhaal",         "date":"2015-02-06","status":"Hit",         "valence":"auspicious"},
        {"num":41, "name":"Vedalam",                  "date":"2015-11-12","status":"Blockbuster", "valence":"auspicious"},
        {"num":42, "name":"Vivegam",                  "date":"2017-08-24","status":"Hit",         "valence":"auspicious"},
        {"num":43, "name":"Viswasam",                 "date":"2019-01-10","status":"Blockbuster", "valence":"auspicious"},
        {"num":44, "name":"Nerkonda Paarvai",         "date":"2019-08-10","status":"Hit",         "valence":"auspicious"},
        {"num":45, "name":"Valimai",                  "date":"2022-02-24","status":"Hit",         "valence":"auspicious"},
        {"num":46, "name":"Thunivu",                  "date":"2023-01-11","status":"Hit",         "valence":"auspicious"},
        {"num":47, "name":"Vidaamuyarchi",            "date":"2025-02-06","status":"Hit",         "valence":"auspicious"},
    ]
},

# ─── 4. SURIYA ────────────────────────────────────────────────────────────────
{
    "name": "Suriya",
    "dob": "1975-07-23",
    "birth_time": "12:00",
    "lat": 13.0827, "lon": 80.2707,
    "slug": "suriya",
    "films": [
        {"num":1,  "name":"Nerrukku Ner",             "date":"1997-09-06","status":"Hit",         "valence":"auspicious"},
        {"num":2,  "name":"Sandhippoma",               "date":"1998-01-14","status":"Flop",        "valence":"inauspicious"},
        {"num":3,  "name":"Uyire",                     "date":"1998-09-11","status":"Blockbuster", "valence":"auspicious"},
        {"num":4,  "name":"Poovellam Kettuppaar",      "date":"1999-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":5,  "name":"Vaali",                     "date":"1999-04-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":6,  "name":"Periyanna",                 "date":"1999-10-14","status":"Flop",        "valence":"inauspicious"},
        {"num":7,  "name":"Nee Varuvai Ena",           "date":"2000-08-11","status":"Flop",        "valence":"inauspicious"},
        {"num":8,  "name":"Rhythm",                    "date":"2000-11-16","status":"Hit",         "valence":"auspicious"},
        {"num":9,  "name":"Friends",                   "date":"2001-01-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":10, "name":"Nandha",                    "date":"2001-10-20","status":"Hit",         "valence":"auspicious"},
        {"num":11, "name":"Mounam Pesiyadhe",          "date":"2002-04-12","status":"Blockbuster", "valence":"auspicious"},
        {"num":12, "name":"Unnai Ninaithu",            "date":"2002-08-01","status":"Hit",         "valence":"auspicious"},
        {"num":13, "name":"Kaakha Kaakha",             "date":"2003-09-26","status":"Blockbuster", "valence":"auspicious"},
        {"num":14, "name":"Pithamagan",                "date":"2003-10-10","status":"Hit",         "valence":"auspicious"},
        {"num":15, "name":"Perazhagan",                "date":"2004-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":16, "name":"Aaru",                      "date":"2005-05-01","status":"Hit",         "valence":"auspicious"},
        {"num":17, "name":"Ghajini",                   "date":"2005-11-11","status":"Blockbuster", "valence":"auspicious"},
        {"num":18, "name":"Sillunu Oru Kaadhal",       "date":"2006-12-15","status":"Hit",         "valence":"auspicious"},
        {"num":19, "name":"Vel",                       "date":"2007-12-13","status":"Hit",         "valence":"auspicious"},
        {"num":20, "name":"Vaaranam Aayiram",          "date":"2008-11-14","status":"Hit",         "valence":"auspicious"},
        {"num":21, "name":"Ayan",                      "date":"2009-04-10","status":"Blockbuster", "valence":"auspicious"},
        {"num":22, "name":"Aadhavan",                  "date":"2009-10-16","status":"Hit",         "valence":"auspicious"},
        {"num":23, "name":"Singam",                    "date":"2010-05-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":24, "name":"7aum Arivu",                "date":"2011-11-04","status":"Hit",         "valence":"auspicious"},
        {"num":25, "name":"Maattrraan",                "date":"2012-07-13","status":"Flop",        "valence":"inauspicious"},
        {"num":26, "name":"Singam 2",                  "date":"2013-07-05","status":"Blockbuster", "valence":"auspicious"},
        {"num":27, "name":"Anjaan",                    "date":"2014-08-15","status":"Flop",        "valence":"inauspicious"},
        {"num":28, "name":"Masss",                     "date":"2015-07-03","status":"Flop",        "valence":"inauspicious"},
        {"num":29, "name":"24",                        "date":"2016-04-22","status":"Hit",         "valence":"auspicious"},
        {"num":30, "name":"S3",                        "date":"2017-01-26","status":"Flop",        "valence":"inauspicious"},
        {"num":31, "name":"Thaanaa Serndha Koottam",   "date":"2018-01-12","status":"Hit",         "valence":"auspicious"},
        {"num":32, "name":"NGK",                       "date":"2019-05-31","status":"Flop",        "valence":"inauspicious"},
        {"num":33, "name":"Kaappaan",                  "date":"2019-09-20","status":"Flop",        "valence":"inauspicious"},
        {"num":34, "name":"Soorarai Pottru",           "date":"2020-10-30","status":"Blockbuster", "valence":"auspicious"},
        {"num":35, "name":"Jai Bhim",                  "date":"2021-11-02","status":"Blockbuster", "valence":"auspicious"},
        {"num":36, "name":"Etharkkum Thunindhavan",    "date":"2022-03-10","status":"Hit",         "valence":"auspicious"},
        {"num":37, "name":"Kanguva",                   "date":"2024-11-14","status":"Flop",        "valence":"inauspicious"},
    ]
},

# ─── 5. VIKRAM ────────────────────────────────────────────────────────────────
{
    "name": "Vikram",
    "dob": "1966-04-17",
    "birth_time": "12:00",
    "lat": 9.9252, "lon": 78.1198,
    "slug": "vikram",
    "films": [
        {"num":1,  "name":"En Kadhal Kanmani",        "date":"1990-01-01","status":"Flop",        "valence":"inauspicious"},
        {"num":2,  "name":"Meera",                     "date":"1992-01-01","status":"Flop",        "valence":"inauspicious"},
        {"num":3,  "name":"Mafia",                     "date":"1993-01-01","status":"Flop",        "valence":"inauspicious"},
        {"num":4,  "name":"Pudhiya Mannargal",         "date":"1994-01-01","status":"Flop",        "valence":"inauspicious"},
        {"num":5,  "name":"Sethu",                     "date":"1999-02-05","status":"Hit",         "valence":"auspicious"},
        {"num":6,  "name":"Dhill",                     "date":"2001-06-01","status":"Hit",         "valence":"auspicious"},
        {"num":7,  "name":"Gemini",                    "date":"2002-04-04","status":"Blockbuster", "valence":"auspicious"},
        {"num":8,  "name":"Kasi",                      "date":"2001-11-01","status":"Hit",         "valence":"auspicious"},
        {"num":9,  "name":"Dhool",                     "date":"2003-08-08","status":"Hit",         "valence":"auspicious"},
        {"num":10, "name":"Saamy",                     "date":"2003-12-12","status":"Blockbuster", "valence":"auspicious"},
        {"num":11, "name":"Pithamagan",                "date":"2003-10-10","status":"Hit",         "valence":"auspicious"},
        {"num":12, "name":"Arul",                      "date":"2004-12-17","status":"Hit",         "valence":"auspicious"},
        {"num":13, "name":"Anniyan",                   "date":"2005-06-10","status":"Blockbuster", "valence":"auspicious"},
        {"num":14, "name":"Majaa",                     "date":"2005-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":15, "name":"Lankeshwarudu",             "date":"2006-01-01","status":"Flop",        "valence":"inauspicious"},
        {"num":16, "name":"Bheemaa",                   "date":"2008-01-14","status":"Flop",        "valence":"inauspicious"},
        {"num":17, "name":"Kanthaswamy",               "date":"2009-07-31","status":"Hit",         "valence":"auspicious"},
        {"num":18, "name":"Raavanan",                  "date":"2010-06-18","status":"Flop",        "valence":"inauspicious"},
        {"num":19, "name":"Deiva Thirumagal",          "date":"2011-10-27","status":"Hit",         "valence":"auspicious"},
        {"num":20, "name":"Rajapattai",                "date":"2011-12-23","status":"Flop",        "valence":"inauspicious"},
        {"num":21, "name":"Thaandavam",                "date":"2012-10-25","status":"Hit",         "valence":"auspicious"},
        {"num":22, "name":"David",                     "date":"2013-02-01","status":"Flop",        "valence":"inauspicious"},
        {"num":23, "name":"I",                         "date":"2015-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":24, "name":"10 Endrathukulla",          "date":"2015-10-22","status":"Flop",        "valence":"inauspicious"},
        {"num":25, "name":"Iru Mugan",                 "date":"2016-09-09","status":"Flop",        "valence":"inauspicious"},
        {"num":26, "name":"Sketch",                    "date":"2018-01-12","status":"Flop",        "valence":"inauspicious"},
        {"num":27, "name":"Saamy 2",                   "date":"2018-08-15","status":"Flop",        "valence":"inauspicious"},
        {"num":28, "name":"Kadaram Kondan",            "date":"2019-08-02","status":"Hit",         "valence":"auspicious"},
        {"num":29, "name":"Cobra",                     "date":"2022-08-31","status":"Flop",        "valence":"inauspicious"},
        {"num":30, "name":"Ponniyin Selvan I",         "date":"2022-09-30","status":"Blockbuster", "valence":"auspicious"},
        {"num":31, "name":"Ponniyin Selvan II",        "date":"2023-04-28","status":"Hit",         "valence":"auspicious"},
        {"num":32, "name":"Thangalaan",                "date":"2024-08-15","status":"Hit",         "valence":"auspicious"},
    ]
},

# ─── 6. DHANUSH ───────────────────────────────────────────────────────────────
{
    "name": "Dhanush",
    "dob": "1983-07-28",
    "birth_time": "12:00",
    "lat": 13.0827, "lon": 80.2707,
    "slug": "dhanush",
    "films": [
        {"num":1,  "name":"Thulluvadho Ilamai",       "date":"2002-11-01","status":"Flop",        "valence":"inauspicious"},
        {"num":2,  "name":"Kadhal Kondein",            "date":"2003-10-03","status":"Hit",         "valence":"auspicious"},
        {"num":3,  "name":"Thiruda Thirudi",           "date":"2003-10-17","status":"Hit",         "valence":"auspicious"},
        {"num":4,  "name":"Sullan",                    "date":"2003-12-05","status":"Hit",         "valence":"auspicious"},
        {"num":5,  "name":"Pudhukottaiyilirundhu Saravanan","date":"2004-05-14","status":"Hit",   "valence":"auspicious"},
        {"num":6,  "name":"Dreams",                    "date":"2004-09-01","status":"Flop",        "valence":"inauspicious"},
        {"num":7,  "name":"Thiruvilaiyaadal Aarambam", "date":"2006-06-01","status":"Flop",        "valence":"inauspicious"},
        {"num":8,  "name":"Pudhupettai",               "date":"2006-04-14","status":"Hit",         "valence":"auspicious"},
        {"num":9,  "name":"Parattai Engira Azhagu Sundaram","date":"2006-10-14","status":"Flop", "valence":"inauspicious"},
        {"num":10, "name":"Polladhavan",               "date":"2007-09-14","status":"Hit",         "valence":"auspicious"},
        {"num":11, "name":"Yaaradi Nee Mohini",        "date":"2008-07-11","status":"Blockbuster", "valence":"auspicious"},
        {"num":12, "name":"Padikathavan",              "date":"2009-04-10","status":"Hit",         "valence":"auspicious"},
        {"num":13, "name":"Kutty",                     "date":"2010-01-14","status":"Flop",        "valence":"inauspicious"},
        {"num":14, "name":"Aadukalam",                 "date":"2011-02-04","status":"Blockbuster", "valence":"auspicious"},
        {"num":15, "name":"Mappillai",                 "date":"2011-09-09","status":"Hit",         "valence":"auspicious"},
        {"num":16, "name":"Mayakkam Enna",             "date":"2011-12-16","status":"Blockbuster", "valence":"auspicious"},
        {"num":17, "name":"3",                         "date":"2012-03-30","status":"Hit",         "valence":"auspicious"},
        {"num":18, "name":"Maryan",                    "date":"2013-05-30","status":"Hit",         "valence":"auspicious"},
        {"num":19, "name":"Raanjhanaa",                "date":"2013-06-21","status":"Hit",         "valence":"auspicious"},
        {"num":20, "name":"Ethir Neechal",             "date":"2013-10-11","status":"Hit",         "valence":"auspicious"},
        {"num":21, "name":"Naiyaandi",                 "date":"2013-11-22","status":"Flop",        "valence":"inauspicious"},
        {"num":22, "name":"Velai Illa Pattadhaari",    "date":"2014-07-18","status":"Blockbuster", "valence":"auspicious"},
        {"num":23, "name":"Shamitabh",                 "date":"2015-02-06","status":"Flop",        "valence":"inauspicious"},
        {"num":24, "name":"Anegan",                    "date":"2015-02-13","status":"Flop",        "valence":"inauspicious"},
        {"num":25, "name":"Maari",                     "date":"2015-06-04","status":"Hit",         "valence":"auspicious"},
        {"num":26, "name":"Thanga Magan",              "date":"2015-12-25","status":"Flop",        "valence":"inauspicious"},
        {"num":27, "name":"Thodari",                   "date":"2016-09-23","status":"Flop",        "valence":"inauspicious"},
        {"num":28, "name":"Kodi",                      "date":"2016-11-11","status":"Hit",         "valence":"auspicious"},
        {"num":29, "name":"Velai Illa Pattadhaari 2",  "date":"2017-06-22","status":"Hit",         "valence":"auspicious"},
        {"num":30, "name":"Maari 2",                   "date":"2018-12-21","status":"Flop",        "valence":"inauspicious"},
        {"num":31, "name":"Enai Noki Paayum Thota",    "date":"2019-09-27","status":"Flop",        "valence":"inauspicious"},
        {"num":32, "name":"Pattas",                    "date":"2020-01-15","status":"Hit",         "valence":"auspicious"},
        {"num":33, "name":"Karnan",                    "date":"2021-04-09","status":"Blockbuster", "valence":"auspicious"},
        {"num":34, "name":"Jagame Thandhiram",         "date":"2021-06-18","status":"Hit",         "valence":"auspicious"},
        {"num":35, "name":"Atrangi Re",                "date":"2021-12-24","status":"Hit",         "valence":"auspicious"},
        {"num":36, "name":"Thiruchitrambalam",         "date":"2022-09-01","status":"Blockbuster", "valence":"auspicious"},
        {"num":37, "name":"Naane Varuvean",            "date":"2022-10-28","status":"Hit",         "valence":"auspicious"},
        {"num":38, "name":"Vaathi",                    "date":"2023-03-17","status":"Flop",        "valence":"inauspicious"},
        {"num":39, "name":"Captain Miller",            "date":"2024-01-12","status":"Hit",         "valence":"auspicious"},
        {"num":40, "name":"Raayan",                    "date":"2024-07-26","status":"Blockbuster", "valence":"auspicious"},
    ]
},

# ─── 7. SIVAKARTHIKEYAN ──────────────────────────────────────────────────────
{
    "name": "Sivakarthikeyan",
    "dob": "1985-02-17",
    "birth_time": "12:00",
    "lat": 8.1833, "lon": 77.4119,
    "slug": "sivakarthikeyan",
    "films": [
        {"num":1,  "name":"Marina",                    "date":"2012-11-30","status":"Hit",         "valence":"auspicious"},
        {"num":2,  "name":"Manam Kothi Paravai",       "date":"2012-12-21","status":"Hit",         "valence":"auspicious"},
        {"num":3,  "name":"Kedi Billa Killadi Ranga",  "date":"2013-08-29","status":"Hit",         "valence":"auspicious"},
        {"num":4,  "name":"Ethir Neechal",             "date":"2013-10-11","status":"Hit",         "valence":"auspicious"},
        {"num":5,  "name":"Varuthapadatha Valibar Sangam","date":"2013-12-13","status":"Blockbuster","valence":"auspicious"},
        {"num":6,  "name":"Maan Karate",               "date":"2014-04-11","status":"Hit",         "valence":"auspicious"},
        {"num":7,  "name":"Kaaki Sattai",              "date":"2015-01-14","status":"Hit",         "valence":"auspicious"},
        {"num":8,  "name":"Rajini Murugan",            "date":"2016-01-15","status":"Hit",         "valence":"auspicious"},
        {"num":9,  "name":"Remo",                      "date":"2016-10-07","status":"Blockbuster", "valence":"auspicious"},
        {"num":10, "name":"Velaikkaran",               "date":"2017-12-22","status":"Blockbuster", "valence":"auspicious"},
        {"num":11, "name":"Seemaraja",                 "date":"2018-09-13","status":"Flop",        "valence":"inauspicious"},
        {"num":12, "name":"Mr. Local",                 "date":"2019-05-17","status":"Flop",        "valence":"inauspicious"},
        {"num":13, "name":"Hero",                      "date":"2019-12-25","status":"Flop",        "valence":"inauspicious"},
        {"num":14, "name":"Doctor",                    "date":"2021-10-09","status":"Blockbuster", "valence":"auspicious"},
        {"num":15, "name":"Don",                       "date":"2022-05-13","status":"Hit",         "valence":"auspicious"},
        {"num":16, "name":"Prince",                    "date":"2022-10-21","status":"Flop",        "valence":"inauspicious"},
        {"num":17, "name":"Maaveeran",                 "date":"2023-07-14","status":"Hit",         "valence":"auspicious"},
        {"num":18, "name":"Amaran",                    "date":"2024-10-31","status":"Blockbuster", "valence":"auspicious"},
    ]
},

# ─── 8. KARTHI ────────────────────────────────────────────────────────────────
{
    "name": "Karthi",
    "dob": "1977-05-25",
    "birth_time": "12:00",
    "lat": 13.0827, "lon": 80.2707,
    "slug": "karthi",
    "films": [
        {"num":1,  "name":"Paruthiveeran",             "date":"2007-03-30","status":"Blockbuster", "valence":"auspicious"},
        {"num":2,  "name":"Aayirathil Oruvan",         "date":"2010-01-14","status":"Flop",        "valence":"inauspicious"},
        {"num":3,  "name":"Paiyaa",                    "date":"2010-07-09","status":"Blockbuster", "valence":"auspicious"},
        {"num":4,  "name":"Naan Mahaan Alla",          "date":"2010-09-17","status":"Hit",         "valence":"auspicious"},
        {"num":5,  "name":"Siruthai",                  "date":"2011-01-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":6,  "name":"Saguni",                    "date":"2012-06-15","status":"Hit",         "valence":"auspicious"},
        {"num":7,  "name":"Alex Pandian",              "date":"2013-02-22","status":"Flop",        "valence":"inauspicious"},
        {"num":8,  "name":"Biriyani",                  "date":"2013-12-20","status":"Flop",        "valence":"inauspicious"},
        {"num":9,  "name":"All in All Azhagu Raja",    "date":"2013-08-23","status":"Flop",        "valence":"inauspicious"},
        {"num":10, "name":"Madras",                    "date":"2014-10-10","status":"Blockbuster", "valence":"auspicious"},
        {"num":11, "name":"Komban",                    "date":"2015-04-02","status":"Hit",         "valence":"auspicious"},
        {"num":12, "name":"Kaashmora",                 "date":"2016-10-28","status":"Flop",        "valence":"inauspicious"},
        {"num":13, "name":"Theeran Adhigaaram Ondru",  "date":"2017-11-17","status":"Hit",         "valence":"auspicious"},
        {"num":14, "name":"Kadaikutty Singam",         "date":"2018-07-13","status":"Hit",         "valence":"auspicious"},
        {"num":15, "name":"Dev",                       "date":"2019-01-11","status":"Flop",        "valence":"inauspicious"},
        {"num":16, "name":"Kaithi",                    "date":"2019-10-25","status":"Blockbuster", "valence":"auspicious"},
        {"num":17, "name":"Sulthan",                   "date":"2021-04-02","status":"Hit",         "valence":"auspicious"},
        {"num":18, "name":"Viruman",                   "date":"2022-07-15","status":"Hit",         "valence":"auspicious"},
        {"num":19, "name":"Ponniyin Selvan I",         "date":"2022-09-30","status":"Blockbuster", "valence":"auspicious"},
        {"num":20, "name":"Sardar",                    "date":"2022-10-21","status":"Hit",         "valence":"auspicious"},
        {"num":21, "name":"Ponniyin Selvan II",        "date":"2023-04-28","status":"Hit",         "valence":"auspicious"},
        {"num":22, "name":"Japan",                     "date":"2023-12-22","status":"Hit",         "valence":"auspicious"},
        {"num":23, "name":"Meiyazhagan",               "date":"2024-09-27","status":"Hit",         "valence":"auspicious"},
    ]
},

# ─── 9. VIJAY SETHUPATHI ─────────────────────────────────────────────────────
{
    "name": "Vijay Sethupathi",
    "dob": "1978-01-16",
    "birth_time": "12:00",
    "lat": 9.4523, "lon": 77.5599,
    "slug": "vijay_sethupathi",
    "films": [
        {"num":1,  "name":"Thenmerku Paruvakaatru",    "date":"2010-08-06","status":"Hit",         "valence":"auspicious"},
        {"num":2,  "name":"Pizza",                     "date":"2012-07-06","status":"Blockbuster", "valence":"auspicious"},
        {"num":3,  "name":"Sundarapandian",            "date":"2012-10-12","status":"Hit",         "valence":"auspicious"},
        {"num":4,  "name":"Naduvula Konjam Pakkatha Kaanom","date":"2012-12-28","status":"Hit",   "valence":"auspicious"},
        {"num":5,  "name":"Mundhinam Paartheney",      "date":"2013-01-18","status":"Flop",        "valence":"inauspicious"},
        {"num":6,  "name":"Vanakkam Chennai",          "date":"2013-05-10","status":"Hit",         "valence":"auspicious"},
        {"num":7,  "name":"Soodhu Kavvum",             "date":"2013-06-07","status":"Blockbuster", "valence":"auspicious"},
        {"num":8,  "name":"Inaindha Kaigal",           "date":"2013-09-06","status":"Flop",        "valence":"inauspicious"},
        {"num":9,  "name":"Puriyaadha Pudhir",         "date":"2013-10-25","status":"Flop",        "valence":"inauspicious"},
        {"num":10, "name":"Idam Porul Yaeval",         "date":"2013-11-14","status":"Hit",         "valence":"auspicious"},
        {"num":11, "name":"Rummy",                     "date":"2014-05-02","status":"Flop",        "valence":"inauspicious"},
        {"num":12, "name":"Naaigal Jaakiradhai",       "date":"2014-05-23","status":"Flop",        "valence":"inauspicious"},
        {"num":13, "name":"Pannaiyarum Padminiyum",    "date":"2014-09-05","status":"Hit",         "valence":"auspicious"},
        {"num":14, "name":"Kaaka Muttai",              "date":"2015-06-05","status":"Hit",         "valence":"auspicious"},
        {"num":15, "name":"Orange Mittai",             "date":"2015-08-14","status":"Hit",         "valence":"auspicious"},
        {"num":16, "name":"Naanum Rowdy Dhaan",        "date":"2015-10-22","status":"Blockbuster", "valence":"auspicious"},
        {"num":17, "name":"Sethupathi",                "date":"2016-04-22","status":"Blockbuster", "valence":"auspicious"},
        {"num":18, "name":"Rekka",                     "date":"2016-09-09","status":"Hit",         "valence":"auspicious"},
        {"num":19, "name":"Dharma Durai",              "date":"2016-09-30","status":"Hit",         "valence":"auspicious"},
        {"num":20, "name":"Aandavan Kattalai",         "date":"2016-10-14","status":"Hit",         "valence":"auspicious"},
        {"num":21, "name":"Kavan",                     "date":"2017-03-31","status":"Hit",         "valence":"auspicious"},
        {"num":22, "name":"Vikram Vedha",              "date":"2017-07-21","status":"Blockbuster", "valence":"auspicious"},
        {"num":23, "name":"Karuppan",                  "date":"2017-09-29","status":"Flop",        "valence":"inauspicious"},
        {"num":24, "name":"Junga",                     "date":"2018-06-27","status":"Flop",        "valence":"inauspicious"},
        {"num":25, "name":"96",                        "date":"2018-10-04","status":"Blockbuster", "valence":"auspicious"},
        {"num":26, "name":"Chekka Chivantha Vaanam",   "date":"2018-09-27","status":"Hit",         "valence":"auspicious"},
        {"num":27, "name":"Petta",                     "date":"2019-01-10","status":"Hit",         "valence":"auspicious"},
        {"num":28, "name":"Super Deluxe",              "date":"2019-03-29","status":"Hit",         "valence":"auspicious"},
        {"num":29, "name":"Sindhubaadh",               "date":"2019-06-14","status":"Flop",        "valence":"inauspicious"},
        {"num":30, "name":"Comali",                    "date":"2019-08-15","status":"Hit",         "valence":"auspicious"},
        {"num":31, "name":"Sanga Thamizhan",           "date":"2019-11-15","status":"Flop",        "valence":"inauspicious"},
        {"num":32, "name":"Master",                    "date":"2021-01-13","status":"Blockbuster", "valence":"auspicious"},
        {"num":33, "name":"Laabam",                    "date":"2021-09-09","status":"Flop",        "valence":"inauspicious"},
        {"num":34, "name":"Annabelle Sethupathi",      "date":"2021-09-17","status":"Hit",         "valence":"auspicious"},
        {"num":35, "name":"Kaathu Vaakula Rendu Kaadhal","date":"2022-04-28","status":"Flop",     "valence":"inauspicious"},
        {"num":36, "name":"Vikram",                    "date":"2022-06-03","status":"Blockbuster", "valence":"auspicious"},
        {"num":37, "name":"Maamanithan",               "date":"2022-07-08","status":"Flop",        "valence":"inauspicious"},
        {"num":38, "name":"DSP",                       "date":"2022-12-02","status":"Flop",        "valence":"inauspicious"},
        {"num":39, "name":"Viduthalai Part 1",         "date":"2023-03-31","status":"Hit",         "valence":"auspicious"},
        {"num":40, "name":"Merry Christmas",           "date":"2024-01-12","status":"Flop",        "valence":"inauspicious"},
        {"num":41, "name":"Maharaja",                  "date":"2024-06-14","status":"Blockbuster", "valence":"auspicious"},
        {"num":42, "name":"Viduthalai Part 2",         "date":"2024-12-20","status":"Hit",         "valence":"auspicious"},
    ]
},

]

# ═══════════════════════════════════════════════════════════════════════════════
# SHARED UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

CHALDEAN_VALUES = {
    'A':1,'I':1,'J':1,'Y':1,'Q':1,'B':2,'K':2,'R':2,
    'C':3,'G':3,'L':3,'S':3,'D':4,'M':4,'T':4,
    'E':5,'H':5,'N':5,'X':5,'U':6,'V':6,'W':6,'O':7,'Z':7,'F':8,'P':8
}

def digit_root(n):
    while n > 9: n = sum(int(d) for d in str(n))
    return n

def calculate_chaldean(name):
    s = re.sub(r'[^A-Z]', '', name.upper())
    return digit_root(sum(CHALDEAN_VALUES.get(c, 0) for c in s))

AUSPICIOUS_KW   = ["wealth","success","fame","happiness","health","gain","auspicious",
                    "good fortune","rich","king","prosperous","honor","victory","blessed",
                    "excellent","award","rise","promotion","marriage","children","son","progeny"]
INAUSPICIOUS_KW = ["poverty","death","disease","loss","grief","inauspicious","bad","sorrow",
                    "poor","pain","danger","trouble","fear","imprisonment","exile","separation",
                    "divorce","downfall","disgrace","scandal","ill health","accident","misery"]

def rule_valence(text):
    t = text.lower()
    a = sum(1 for k in AUSPICIOUS_KW if k in t)
    i = sum(1 for k in INAUSPICIOUS_KW if k in t)
    return "auspicious" if a > i else ("inauspicious" if i > a else "neutral")

def get_holiday_modifier(dt):
    m, d = dt.month, dt.day
    if m == 1 and 10 <= d <= 18: return 0.35
    if m == 4 and 10 <= d <= 18: return 0.25
    if m == 5: return 0.20
    if (m == 10 and d >= 15) or (m == 11 and d <= 20): return 0.35
    return 0.0

def get_mutual_relationship(sign1, sign2):
    if sign1 not in SIGN_NAMES or sign2 not in SIGN_NAMES: return (1, 1)
    i1, i2 = SIGN_NAMES.index(sign1), SIGN_NAMES.index(sign2)
    return (((i2 - i1) % 12) + 1, ((i1 - i2) % 12) + 1)

# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════════

async def precompute_features(actor):
    corpus   = get_corpus()
    dob_parts = actor["dob"].split("-")
    yr, mo, dy = int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2])
    bt_parts  = actor["birth_time"].split(":")
    birth_hr  = float(bt_parts[0]) + float(bt_parts[1])/60.0

    birth_data = BirthData(
        year=yr, month=mo, day=dy,
        time=actor["birth_time"],
        lat=actor["lat"], lon=actor["lon"],
        focus="general"
    )
    chart     = await jathagam(birth_data)
    pos       = chart.get("all_planet_positions", {})
    lagna_str = chart.get("lagnam", "Kanni").split(" ")[0]
    lagna_idx = SIGN_NAMES.index(lagna_str) if lagna_str in SIGN_NAMES else 5

    natal_signs = {}
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        if p in pos: natal_signs[p] = pos[p]["rasi"].split(" ")[0]

    moon_lon       = pos["Moon"]["longitude"]
    moon_sign_idx  = int(moon_lon / 30)
    natal_pos_7    = {p: pos[p]["longitude"] for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]}
    natal_jd       = swe.julday(yr, mo, dy, birth_hr - 5.5)

    low_level_chart = {
        "positions": {"Moon": {"lon": moon_lon, "lon_abs": moon_lon}},
        "birth": {"year": yr, "month": mo, "day": dy, "hour": int(birth_hr), "min": int((birth_hr % 1) * 60)}
    }

    s_w, in_w, ma_w, self_w, conj_w = 0.20, 0.65, 0.75, 0.85, 0.75

    print(f"  [{actor['name']}] Precomputing {len(actor['films'])} films...")
    precomputed = []

    for f in actor["films"]:
        dt = datetime.strptime(f["date"], "%Y-%m-%d")

        active    = current_dasha(low_level_chart, dt)
        md        = active.get("md", {}).get("md", "Unknown")
        ad        = active.get("ad", {}).get("ad", "Unknown")
        pd_lord   = active.get("pd", {}).get("pd", "Unknown")
        pd_func   = get_functional_nature(lagna_str, pd_lord)

        jd_ut = swe.julday(dt.year, dt.month, dt.day, 12.0)
        transit_snap = get_transit_snapshot(moon_sign_idx, lagna_idx, natal_pos_7, jd_ut)
        gf = 1.0
        for tp in transit_snap.get("transit_planets", []):
            pn, val = tp["planet"], tp["gochar_valence"]
            if pn == "Saturn" and val == "BAD":    gf -= 0.22
            elif pn == "Jupiter" and val == "GOOD": gf += 0.28
            elif pn == "Jupiter" and val == "BAD":  gf -= 0.15
            elif pn == "Rahu" and val == "BAD":      gf -= 0.15
        gf = max(0.4, min(1.6, gf))

        rapm_a, rapm_i = 1.0, 1.0
        d_sign = natal_signs.get(md)
        b_sign = natal_signs.get(ad)
        rel    = get_mutual_relationship(d_sign, b_sign)
        if rel in [(6,8),(8,6)]: rapm_a *= s_w; rapm_i *= (2.0 - s_w)
        if md == ad:              rapm_a *= self_w; rapm_i *= (2.0 - self_w)

        inimical_pairs = [
            ("Mercury","Sun"),("Mercury","Mars"),("Mercury","Ketu"),
            ("Venus","Sun"),("Venus","Moon"),("Venus","Rahu"),
            ("Ketu","Venus"),("Ketu","Sun"),("Ketu","Moon")
        ]
        if (md, ad) in inimical_pairs or (ad, md) in inimical_pairs:
            rapm_a *= in_w; rapm_i *= (2.0 - in_w)
        if ad in ["Mars","Sun","Jupiter"]: rapm_a *= ma_w; rapm_i *= (2.0 - ma_w)
        if md == "Mercury" and ad in ["Sun","Saturn","Mars","Venus"]:
            rapm_a *= conj_w; rapm_i *= (2.0 - conj_w)

        rules   = corpus.get_dasha_rules(md, ad, limit=12)
        aus_c   = sum(1 for r in rules if rule_valence(r.text) == "auspicious")
        ina_c   = sum(1 for r in rules if rule_valence(r.text) == "inauspicious")
        raw_aus = aus_c * gf * rapm_a
        raw_ina = ina_c * (1.0/gf) * rapm_i

        pm_m, pb_m, sp_m, kj_m = 0.3, 0.8, 0.4, 0.3
        pda, pdi = 1.0, 1.0
        if pd_func == "MALEFIC":   pda *= (1.0 - pm_m); pdi *= (1.0 + pm_m)
        elif pd_func == "BENEFIC": pda *= (1.0 + pb_m); pdi *= (1.0 - pb_m/2.0)
        if pd_lord == ad and pd_lord not in ["Rahu","Ketu"]: pda *= (1.0-sp_m); pdi *= (1.0+sp_m)
        if pd_lord == "Jupiter": pda *= (1.0-kj_m); pdi *= (1.0+kj_m)

        astro_aus = raw_aus * pda
        astro_ina = raw_ina * pdi

        age_yr = dt.year - yr
        if dt.month < mo or (dt.month == mo and dt.day < dy): age_yr -= 1
        ann_chart    = annual_chart(natal_jd, 5, age_yr, actor["lat"], actor["lon"])
        muntha_house = ((ann_chart.muntha_sign - ann_chart.annual_lagna_sign) % 12) + 1
        taj_mult = 0.25 if muntha_house in [1,2,3,5,9,10,11] else -0.25

        chaldean_num    = calculate_chaldean(f["name"])
        pyth_triad      = compute_pythagorean_triad(f["name"])
        pythagorean_num = pyth_triad["expression_number"]
        cycles          = compute_personal_cycles(actor["dob"], f["date"])

        precomputed.append({
            "film": f,
            "astro_aus": float(astro_aus),
            "astro_ina": float(astro_ina),
            "taj_mult":  float(taj_mult),
            "holiday_boost": float(get_holiday_modifier(dt)),
            "dir_mult":  0.0,
            "music_mult":0.0,
            "prod_mult": 0.0,
            "chaldean_num": int(chaldean_num),
            "pythagorean_num": int(pythagorean_num),
            "personal_year":  int(cycles["personal_year"]),
            "personal_month": int(cycles["personal_month"]),
            "personal_day":   int(cycles["personal_day"]),
            "md": md, "ad": ad, "pd_lord": pd_lord
        })

    return precomputed

# ═══════════════════════════════════════════════════════════════════════════════
# 3-PHASE OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════════

def solve_model(precomputed, actor_name):
    pyth_map = {1:0,2:1,3:2,4:3,5:4,6:5,7:6,8:7,9:8,11:9,22:10,33:11}
    X, Y = [], []

    for pc in precomputed:
        x = [0.0] * 57
        x[0], x[1], x[2] = pc["astro_aus"], pc["astro_ina"], pc["holiday_boost"]
        x[3] = pc["dir_mult"]  if pc["dir_mult"]  > 0 else 0.0
        x[4] = -pc["dir_mult"] if pc["dir_mult"]  < 0 else 0.0
        x[5], x[6] = pc["music_mult"], pc["prod_mult"]
        x[7] = pc["taj_mult"]  if pc["taj_mult"]  > 0 else 0.0
        x[8] = -pc["taj_mult"] if pc["taj_mult"]  < 0 else 0.0
        x[9 + pc["chaldean_num"] - 1] = 1.0
        x[18 + pyth_map.get(pc["pythagorean_num"], 0)] = 1.0
        x[30 + pc["personal_year"]  - 1] = 1.0
        x[39 + pc["personal_month"] - 1] = 1.0
        x[48 + pc["personal_day"]   - 1] = 1.0
        X.append(x)
        Y.append(1 if pc["film"]["valence"] == "auspicious" else -1)

    n = len(Y)
    w = [0.0] * 57
    w[0]=1.8; w[1]=-1.8; w[2]=0.5
    w[3]=0.8; w[4]=-0.8; w[5]=0.4; w[6]=0.4; w[7]=0.4; w[8]=-0.4
    w[10]=0.3; w[14]=0.4; w[16]=0.4
    w[11]=-1.2; w[9]=-0.3; w[13]=-0.2; w[17]=-0.3

    def bounds(w):
        w[0]=max(0.5,w[0]); w[1]=min(-0.5,w[1])
        for j in [3,5,6,7]: w[j]=max(0.0,w[j])
        for j in [4,8]:     w[j]=min(0.0,w[j])
        return w

    def evaluate(w):
        hits, preds = 0, []
        for i in range(n):
            s = sum(X[i][j]*w[j] for j in range(57))
            p = "auspicious" if s > 0 else "inauspicious"
            preds.append((s, p))
            if p == precomputed[i]["film"]["valence"]: hits += 1
        return hits, preds

    # Phase 1 — Regularized logistic
    print(f"  [{actor_name}] Phase 1: Logistic warm-up (120k epochs)...")
    for _ in range(120000):
        grads = [0.0]*57
        for i in range(n):
            s = sum(X[i][j]*w[j] for j in range(57))
            e = Y[i]*s
            pf = 0.0 if e>50 else (-Y[i] if e<-50 else -Y[i]/(1.0+math.exp(e)))
            for j in range(57): grads[j] += pf*X[i][j]
        for j in range(57):
            grads[j] = grads[j]/n + 2.0*0.0005*w[j]
            w[j] -= 0.015*grads[j]
        w = bounds(w)
    h1, _ = evaluate(w)
    print(f"  [{actor_name}] Phase 1: {h1}/{n} ({100*h1/n:.2f}%)")

    # Phase 2 — Hard-margin targeting
    if h1 < n:
        print(f"  [{actor_name}] Phase 2: Hard-margin targeting ({n-h1} MISS)...")
        for ep in range(80000):
            grads = [0.0]*57; mc = 0
            for i in range(n):
                s  = sum(X[i][j]*w[j] for j in range(57))
                p  = "auspicious" if s > 0 else "inauspicious"
                if p != precomputed[i]["film"]["valence"]:
                    mc += 1
                    if Y[i]*s < 1.0:
                        for j in range(57): grads[j] -= Y[i]*X[i][j]
            if mc == 0:
                print(f"  [{actor_name}] Phase 2: Converged at epoch {ep}!"); break
            for j in range(57):
                grads[j] = grads[j]/max(1,mc); w[j] -= 0.008*grads[j]
            w = bounds(w)
        h2, _ = evaluate(w)
        print(f"  [{actor_name}] Phase 2: {h2}/{n} ({100*h2/n:.2f}%)")
    else:
        h2 = h1; print(f"  [{actor_name}] Phase 2: Skipped — already perfect.")

    # Phase 3 — SVM hinge sweep
    if h2 < n:
        print(f"  [{actor_name}] Phase 3: SVM hinge sweep (200k epochs)...")
        for ep in range(200000):
            grads = [0.0]*57; ok = True
            for i in range(n):
                s = sum(X[i][j]*w[j] for j in range(57))
                if Y[i]*s < 1.0:
                    ok = False
                    for j in range(57): grads[j] -= Y[i]*X[i][j]
            if ok:
                print(f"  [{actor_name}] Phase 3: Full separation at epoch {ep}!"); break
            for j in range(57):
                grads[j] = grads[j]/n + 2.0*0.00001*w[j]; w[j] -= 0.002*grads[j]
            w = bounds(w)
        h3, _ = evaluate(w)
        print(f"  [{actor_name}] Phase 3: {h3}/{n} ({100*h3/n:.2f}%)")
    else:
        print(f"  [{actor_name}] Phase 3: Skipped — already perfect.")

    hits, predictions = evaluate(w)
    acc = 100.0 * hits / n
    print(f"  [{actor_name}] ✅ FINAL: {acc:.2f}% ({hits}/{n})\n")
    return w, predictions, hits, n

# ═══════════════════════════════════════════════════════════════════════════════
# SAVE + REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def save_weights(actor, w, acc):
    pyth_map = {1:0,2:1,3:2,4:3,5:4,6:5,7:6,8:7,9:8,11:9,22:10,33:11}
    data = {
        "actor": actor["name"],
        "dob":   actor["dob"],
        "accuracy": f"{acc:.2f}%",
        "total_films": len(actor["films"]),
        "last_optimized_at": datetime.now().isoformat(),
        "continuous_weights": {
            "astro_auspicious": w[0], "astro_inauspicious": w[1],
            "holiday_boost": w[2], "director_positive": w[3],
            "director_negative": w[4], "music_multiplier": w[5],
            "production_scale": w[6], "tajik_positive": w[7],
            "tajik_negative": w[8]
        },
        "chaldean_coefficients":    {str(n): w[9+n-1]  for n in range(1,10)},
        "pythagorean_coefficients": {str(k): w[18+v]   for k,v in pyth_map.items()},
        "personal_year_coefficients":  {str(n): w[30+n-1] for n in range(1,10)},
        "personal_month_coefficients": {str(n): w[39+n-1] for n in range(1,10)},
        "personal_day_coefficients":   {str(n): w[48+n-1] for n in range(1,10)},
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"weights_{actor['slug']}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"  Weights saved → {out}")
    return out

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    summary = []
    total_films = 0
    total_hits  = 0

    for actor in ACTORS:
        print(f"\n{'═'*80}")
        print(f"  ACTOR: {actor['name'].upper()} | DOB: {actor['dob']} | {len(actor['films'])} Films")
        print(f"{'═'*80}")
        precomputed = await precompute_features(actor)
        w, preds, hits, n_films = solve_model(precomputed, actor["name"])
        acc = 100.0 * hits / n_films
        save_weights(actor, w, acc)
        summary.append((actor["name"], hits, n_films, acc))
        total_films += n_films
        total_hits  += hits

    # Print Master Summary
    print(f"\n{'═'*80}")
    print(f"  MASTER SUMMARY — TOP 10 TAMIL ACTORS (CONJOINED ASTRO-NUMEROLOGY)")
    print(f"  COMPLETE CAREER FILMOGRAPHIES")
    print(f"{'═'*80}")
    print(f"  {'Actor':<22} {'Films':>6} {'Hits':>6} {'Accuracy':>10}")
    print(f"  {'-'*50}")
    for name, hits, total, acc in summary:
        bar = "✅" if acc == 100.0 else "⚠️"
        print(f"  {bar} {name:<20} {total:>6} {hits:>6} {acc:>9.2f}%")
    print(f"  {'-'*50}")
    overall_acc = 100.0 * total_hits / total_films if total_films > 0 else 0
    bar_t = "✅" if overall_acc == 100.0 else "⚠️"
    print(f"  {bar_t} {'GRAND TOTAL':<20} {total_films:>6} {total_hits:>6} {overall_acc:>9.2f}%")
    print(f"{'═'*80}\n")

if __name__ == "__main__":
    asyncio.run(main())
