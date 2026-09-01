"""Traditional South-Indian jathagam extras missing from the JSON API.

Fills the four gaps between the engine's `/api/jathagam` payload and a
Logic-Vision / AstroSign style Thirukanitham print (the reference used for
Manoj's 2003 booklet):

  1. Sunrise / sunset  (already computed for the PDF path — surfaced here)
  2. Nakshatra reference block: gana, yoni + gender, nadi, deity, tree, bird
  3. Chandrashtama (sadhya-ashtama) nakshatras — the three to avoid
  4. Sripati (Porphyry) bhava cusps — unequal house start / middle / end

Everything here is verifiable astronomy or standard almanac correspondence.
The Sripati cusps were validated to the arc-minute against the AstroSign
print for birth 1996-05-25 20:25 Coimbatore (H1 start 231°38′, mid 245°45′,
end 261°38′).  Tree / bird per nakshatra are canonical only where a source
confirms them; unknown rows return None rather than a guess (project truth
policy: no filler presented as fact).
"""
from __future__ import annotations

from typing import Any, Optional

from engine.chart_builder import RASIS
from engine.kuta import YONI  # canonical 27-nakshatra yoni animals

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Fixed yoni gender per nakshatra (standard Ashtakuta yoni-kuta table).
YONI_GENDER = (
    "Male", "Male", "Female", "Male", "Female", "Female",
    "Female", "Male", "Male", "Male", "Female", "Male",
    "Female", "Female", "Male", "Male", "Female", "Male",
    "Male", "Male", "Male", "Female", "Female", "Female",
    "Male", "Female", "Female",
)

GANA = (
    "Deva", "Manushya", "Rakshasa", "Manushya", "Deva", "Manushya",
    "Deva", "Deva", "Rakshasa", "Rakshasa", "Manushya", "Manushya",
    "Deva", "Rakshasa", "Deva", "Rakshasa", "Deva", "Rakshasa",
    "Rakshasa", "Manushya", "Manushya", "Deva", "Rakshasa", "Rakshasa",
    "Manushya", "Manushya", "Deva",
)

NADI = (
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya",
)

# Tree (vanaspati) and bird (pakshi) per janma nakshatra.
# Only rows confirmed against a reference are populated; None => not asserted.
# Magha is confirmed from the AstroSign print (Banyan / male eagle-vulture).
NAK_TREE_BIRD: dict[str, tuple[Optional[str], Optional[str]]] = {
    "Magha": ("Banyan (Aal)", "Male Eagle (Kazhugu)"),
}


def _nak_index(nak: str) -> int:
    if nak in NAKSHATRAS:
        return NAKSHATRAS.index(nak)
    # tolerate common transliteration variants
    alias = {
        "Uttara Bhadrapada": "Uttara Bhadrapada", "Purva Bhadrapada": "Purva Bhadrapada",
        "Uttarabhadra": "Uttara Bhadrapada", "Purvabhadra": "Purva Bhadrapada",
        "Pushyami": "Pushya", "Aslesha": "Ashlesha", "Anusham": "Anuradha",
    }
    return NAKSHATRAS.index(alias.get(nak, "Ashwini")) if alias.get(nak) in NAKSHATRAS else -1


def nakshatra_reference(janma_nak: str) -> dict[str, Any]:
    """Gana / yoni / nadi / tree / bird for the birth star."""
    idx = _nak_index(janma_nak)
    if idx < 0:
        return {"nakshatra": janma_nak, "known": False}
    tree, bird = NAK_TREE_BIRD.get(NAKSHATRAS[idx], (None, None))
    return {
        "nakshatra": NAKSHATRAS[idx],
        "gana": GANA[idx],
        "yoni": YONI[idx],
        "yoni_gender": YONI_GENDER[idx],
        "nadi": NADI[idx],
        "tree": tree,
        "bird": bird,
        "known": True,
    }


def chandrashtama_nakshatras(janma_nak: str) -> list[str]:
    """Sadhya-ashtama: the 8th-from-Moon star cluster (offsets 15,16,17)."""
    idx = _nak_index(janma_nak)
    if idx < 0:
        return []
    return [NAKSHATRAS[(idx + off) % 27] for off in (15, 16, 17)]


# ── Sripati (Porphyry) bhava cusps ───────────────────────────────────────────

def _mid(a: float, b: float) -> float:
    """Zodiacal midpoint of arc a→b (going in increasing-longitude direction)."""
    return (a + ((b - a) % 360) / 2.0) % 360


def compute_mc_sidereal(jd_ut: float, lat: float, lon: float) -> float:
    """Sidereal Midheaven (Lahiri) for the birth moment."""
    import swisseph as swe
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    aya = swe.get_ayanamsa_ut(jd_ut)
    _cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b"P")
    return (ascmc[1] - aya) % 360.0


def _dms(lon: float) -> str:
    sign_idx = int(lon // 30) % 12
    deg = int(lon % 30)
    minutes = int(round((lon % 30 - deg) * 60))
    if minutes >= 60:
        deg += 1
        minutes = 0
    return f"{RASIS[sign_idx]} {deg}°{minutes:02d}'"


BHAVA_NAMES = [
    "Lagna (self)", "Dhana (wealth)", "Sahaja (siblings)", "Matru (mother/home)",
    "Putra (children)", "Ari (enemies/health)", "Kalatra (spouse)", "Ayush (longevity)",
    "Bhagya (fortune/father)", "Karma (career)", "Labha (gains)", "Vyaya (loss/moksha)",
]


def sripati_bhava_cusps(asc_sid: float, mc_sid: float) -> list[dict[str, Any]]:
    """Unequal Sripati houses: ascendant = middle of bhava 1, cusps trisect
    the arcs between the four angles; sandhi (start/end) = midpoints of madhyas.
    Returns 12 dicts: house, name, start, mid, end (sidereal degrees + DMS)."""
    m = {1: asc_sid % 360, 10: mc_sid % 360,
         7: (asc_sid + 180) % 360, 4: (mc_sid + 180) % 360}

    def _fill(start_h: int, end_h: int, h1: int, h2: int) -> None:
        arc = (m[end_h] - m[start_h]) % 360
        step = arc / 3.0
        m[h1] = (m[start_h] + step) % 360
        m[h2] = (m[start_h] + 2 * step) % 360

    _fill(1, 4, 2, 3)
    _fill(4, 7, 5, 6)
    _fill(7, 10, 8, 9)
    _fill(10, 1, 11, 12)

    out = []
    for h in range(1, 13):
        prev_mid = m[12 if h == 1 else h - 1]
        next_mid = m[1 if h == 12 else h + 1]
        start = _mid(prev_mid, m[h])
        end = _mid(m[h], next_mid)
        out.append({
            "house": h,
            "name": BHAVA_NAMES[h - 1],
            "start": round(start, 4),
            "mid": round(m[h], 4),
            "end": round(end, 4),
            "start_dms": _dms(start),
            "mid_dms": _dms(m[h]),
            "end_dms": _dms(m[h]),
        })
        out[-1]["end_dms"] = _dms(end)
    return out


def traditional_extras(core: dict[str, Any]) -> dict[str, Any]:
    """Assemble the four gap-fill blocks from a chart_builder `core` dict.

    Expects: asc_sid, jd, janma_nakshatra, and birth lat/lon (via `birth`)."""
    from engine.jathagam_extras import compute_sunrise_sunset

    janma_nak = core.get("janma_nakshatra", "")
    jd = core.get("jd")
    b = core.get("birth") or {}
    lat = float(b.get("lat", core.get("lat", 0)))
    lon = float(b.get("lon", core.get("lon", 0)))

    block: dict[str, Any] = {
        "nakshatra_reference": nakshatra_reference(janma_nak),
        "chandrashtama_nakshatras": chandrashtama_nakshatras(janma_nak),
    }

    # Sunrise / sunset — reuse the PDF-path computer (chart-dict shape).
    try:
        yr = b.get("year") or core.get("year")
        chart_for_sun = {"birth": {
            "year": yr, "month": b.get("month") or core.get("month"),
            "day": b.get("day") or core.get("day"),
            "lat": lat, "lon": lon, "tz": b.get("tz", core.get("tz_hours", 5.5)),
        }}
        block["sun_times"] = compute_sunrise_sunset(chart_for_sun)
    except Exception:
        block["sun_times"] = {}

    # Sripati bhava cusps.
    try:
        if jd is not None:
            mc = compute_mc_sidereal(jd, lat, lon)
            block["bhava_cusps"] = sripati_bhava_cusps(core["asc_sid"], mc)
            block["midheaven_sidereal"] = round(mc, 4)
    except Exception:
        block["bhava_cusps"] = []

    return block
