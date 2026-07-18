"""Panchanga — 5-fold time analysis: Tithi, Vara, Nakshatra, Yoga, Karana.

Source: Panchanga texts, BPHS Ch. 80, Muhurta Chintamani.
Computes the 5 elements for any given datetime using Swiss Ephemeris.
"""
import sys, datetime as dt
sys.path.insert(0, ".")
import swisseph as swe

swe.set_sid_mode(swe.SIDM_LAHIRI)

TITHIS = ["Pratipada","Dwitiya","Tritiya","Chaturthi","Panchami","Shashthi","Saptami","Ashtami",
          "Navami","Dashami","Ekadashi","Dwadashi","Trayodashi","Chaturdashi","Purnima/Amavasya"]
VARAS = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"]
VARA_LORDS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]
NAKSHATRAS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya",
              "Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
              "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
              "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
YOGAS = ["Vishkambha","Preeti","Ayushmaan","Saubhagya","Shobhana","Atiganda","Sukarmaa","Dhriti",
         "Shoola","Ganda","Vriddhi","Dhruva","Vyaghata","Harshana","Vajra","Siddhi","Vyatipata",
         "Variyana","Parigha","Shiva","Siddha","Saadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"]
KARANAS = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti(Bhadra)",
           "Shakuni","Chatushpada","Naga","Kintughna"]


def jd(when_dt):
    h = when_dt.hour + when_dt.minute/60.0
    return swe.julday(when_dt.year, when_dt.month, when_dt.day, h, swe.GREG_CAL)


def compute_panchanga(when_dt):
    j = jd(when_dt)
    flag = swe.FLG_SIDEREAL | swe.FLG_SWIEPH

    sun_lon, _ = swe.calc_ut(j, swe.SUN, flag)
    moon_lon, _ = swe.calc_ut(j, swe.MOON, flag)
    sun_lon = sun_lon[0] % 360
    moon_lon = moon_lon[0] % 360

    # Tithi (lunar day) — based on Moon-Sun longitude difference
    diff = (moon_lon - sun_lon) % 360
    tithi_num = int(diff / 12) + 1  # 1-30
    is_shukla = tithi_num <= 15
    paksha = "Shukla" if is_shukla else "Krishna"
    tithi_name = TITHIS[(tithi_num - 1) % 15]
    if tithi_num == 15: tithi_name = "Purnima"
    elif tithi_num == 30: tithi_name = "Amavasya"

    # Vara (weekday) — Vedic week starts at sunrise; for simplicity use civil
    weekday = when_dt.weekday()  # Mon=0
    vara_idx = (weekday + 1) % 7  # adjust to Sun=0
    vara = VARAS[vara_idx]
    vara_lord = VARA_LORDS[vara_idx]

    # Nakshatra — Moon's longitude / 13°20'
    nak_idx = int(moon_lon / (360/27))
    nakshatra = NAKSHATRAS[nak_idx]
    pada = int((moon_lon - nak_idx*(360/27)) / (360/27/4)) + 1

    # Yoga — sum of Sun + Moon longitudes / 13°20'
    yoga_sum = (sun_lon + moon_lon) % 360
    yoga_idx = int(yoga_sum / (360/27))
    yoga = YOGAS[yoga_idx]

    # Karana — half of tithi
    karana_idx = int(diff / 6) % 60
    if karana_idx == 0: karana = KARANAS[10]  # Kintughna
    elif karana_idx >= 57: karana = KARANAS[7 + (karana_idx - 57)]  # Shakuni/Chatushpada/Naga
    else:
        karana = KARANAS[(karana_idx - 1) % 7]

    return {
        "datetime": when_dt.strftime("%Y-%m-%d %H:%M"),
        "tithi": tithi_name,
        "tithi_number": tithi_num,
        "paksha": paksha,
        "vara": vara,
        "vara_lord": vara_lord,
        "nakshatra": nakshatra,
        "pada": pada,
        "yoga": yoga,
        "karana": karana,
        "is_bhadra": karana == "Vishti(Bhadra)",
        "is_amavasya": tithi_num == 30,
        "is_purnima": tithi_num == 15,
    }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    today = dt.datetime.now()
    p = compute_panchanga(today)
    print(f"=== Panchanga for {p['datetime']} ===")
    for k, v in p.items():
        if k == "datetime": continue
        print(f"  {k:20s}: {v}")
