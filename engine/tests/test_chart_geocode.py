"""Place-name chart building must read coords from the local Geo (.lat/.lon).

Regression guard for a geopy->local-Geo refactor miss in chart.py that left
compute_chart(place=...) reading the old .latitude/.longitude attributes.
"""
from __future__ import annotations

import unittest

from engine.chart import compute_chart


class GeocodeChartTests(unittest.TestCase):
    def test_compute_chart_by_place_name_resolves_coords(self):
        chart = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                              place="Coimbatore", name="Manoj")
        # Coimbatore ~ 11.0 N, 77.0 E
        self.assertAlmostEqual(chart.lat, 11.0, delta=1.0)
        self.assertAlmostEqual(chart.lon, 77.0, delta=1.0)
        self.assertTrue(chart.lagna_sign, "chart should compute a lagna sign")


if __name__ == "__main__":
    unittest.main()
