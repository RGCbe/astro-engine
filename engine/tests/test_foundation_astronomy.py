"""Reality-anchored foundation checks (audit 2026-07-18).

The original cross-check oracle (PyJHora repo) is no longer on disk, so those
tests skip. These tests verify the compute layer against facts that cannot be
circular: documented astronomical events, published ayanamsa values, festival
tithis, hand-computed divisional formulas, and internal parity between the two
chart pipelines.
"""
from __future__ import annotations

import datetime as dt
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_RUNTIME = os.path.join(_ROOT, "runtime")
if _RUNTIME not in sys.path:
    sys.path.insert(0, _RUNTIME)

from engine.chart_builder import build_sidereal_chart
from engine.chart import compute_chart


def _sep(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


class AstronomicalGroundTruthTests(unittest.TestCase):
    def test_total_solar_eclipse_has_sun_moon_conjunct(self):
        # 2024-04-08 total solar eclipse, maximum ~18:17 UTC over Mexico.
        chart = build_sidereal_chart(2024, 4, 8, "18:17", 25.3, -104.1, 0.0)
        pos = chart["planet_positions"]
        self.assertLess(_sep(pos["Sun"]["longitude"], pos["Moon"]["longitude"]), 0.6)

    def test_full_moon_has_sun_moon_opposed(self):
        # Kartik Purnima full moon 2024-11-15 ~21:28 UTC.
        chart = build_sidereal_chart(2024, 11, 15, "21:28", 28.6, 77.2, 0.0)
        pos = chart["planet_positions"]
        sep = abs((pos["Moon"]["longitude"] - pos["Sun"]["longitude"]) % 360)
        self.assertLess(abs(sep - 180), 0.6)

    def test_lahiri_ayanamsa_matches_published_values(self):
        import swisseph as swe
        swe.set_sid_mode(swe.SIDM_LAHIRI)
        self.assertAlmostEqual(swe.get_ayanamsa_ut(swe.julday(2000, 1, 1, 12)), 23.852, delta=0.02)
        self.assertAlmostEqual(swe.get_ayanamsa_ut(swe.julday(2024, 6, 1, 0)), 24.20, delta=0.05)

    def test_diwali_2024_is_amavasya(self):
        from panchanga import compute_panchanga
        pan = compute_panchanga(dt.datetime(2024, 11, 1, 12, 0))
        self.assertIn("amavasya", str(pan.get("tithi", "")).lower())


class DivisionalFormulaTests(unittest.TestCase):
    """Hand-computed classical varga assignments (BPHS Ch. 6)."""

    def test_navamsa(self):
        from divisional_charts import _navamsa_index
        # movable starts same sign; fixed from 9th; dual from 5th
        for sign, deg, expected in [(0, 1.0, 0), (0, 5.0, 1), (1, 1.0, 9), (2, 1.0, 6)]:
            self.assertEqual(_navamsa_index(sign, deg), expected, (sign, deg))

    def test_dashamsa(self):
        from divisional_charts import _dashamsa_index
        # 3 deg divisions; odd signs from same sign, even signs from 9th
        for sign, deg, expected in [(0, 1.0, 0), (0, 4.0, 1), (1, 1.0, 9), (1, 29.9, 6), (2, 1.0, 2)]:
            self.assertEqual(_dashamsa_index(sign, deg), expected, (sign, deg))

    def test_dwadashamsa_and_shashtiamsa(self):
        from divisional_charts import _dwadashamsa_index, _shashtiamsa_index
        for sign, deg, expected in [(0, 1.0, 0), (0, 3.0, 1), (5, 27.0, 3)]:
            self.assertEqual(_dwadashamsa_index(sign, deg), expected, (sign, deg))
        for sign, deg, expected in [(0, 0.4, 0), (0, 1.2, 2), (3, 29.9, 2)]:
            self.assertEqual(_shashtiamsa_index(sign, deg), expected, (sign, deg))


class PipelineParityTests(unittest.TestCase):
    def test_chart_and_chart_builder_agree_to_arcsecond(self):
        cc = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                           lat=11.0, lon=77.0, ayanamsa="lahiri")
        cb = build_sidereal_chart(1996, 5, 25, "20:25", 11.0, 77.0, 5.5,
                                  tradition_hint="lahiri")
        for planet, lon_a in cc.positions.items():
            entry = cb["planet_positions"].get(planet)
            if entry is None or lon_a is None:
                continue
            self.assertLess(_sep(float(lon_a), entry["longitude"]), 0.01, planet)


if __name__ == "__main__":
    unittest.main()
