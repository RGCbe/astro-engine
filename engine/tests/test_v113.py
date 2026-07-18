"""Tests for v1.13: ayanamsa_picker, deep_rules, tamil_numerology."""
from __future__ import annotations

import datetime as dt
import unittest

from engine import ayanamsa_picker, deep_rules, tamil_numerology
from engine.chart import compute_chart


class AyanamsaPickerTests(unittest.TestCase):
    def test_tamil_nadu_birth_picks_kp(self):
        c = ayanamsa_picker.pick(11.25, 77.1167, 5.5)
        self.assertEqual(c.mode, "thirukanitham")
        self.assertAlmostEqual(c.pinned_deg, 23.6792, places=4)

    def test_north_india_birth_picks_lahiri(self):
        c = ayanamsa_picker.pick(28.6, 77.2, 5.5)
        self.assertEqual(c.mode, "lahiri")
        self.assertIsNone(c.pinned_deg)

    def test_foreign_birth_picks_true_chitrapaksha(self):
        c = ayanamsa_picker.pick(40.7, -74.0, -5.0)
        self.assertEqual(c.mode, "true_chitrapaksha")

    def test_chart_auto_picks_kp_for_tamil_nadu(self):
        ch = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                           lat=11.25, lon=77.1167, place="Kovilpalayam",
                           name="Manoj")
        # Should match printed PDF ayanamsa within 0.001°
        self.assertAlmostEqual(ch.ayanamsa, 23.6792, places=3)

    def test_methodology_footer_renders(self):
        c = ayanamsa_picker.pick(11.25, 77.1167, 5.5)
        f = ayanamsa_picker.methodology_footer(c)
        self.assertIn("Thirukanitham", f)
        self.assertIn("Swiss Ephemeris", f)


class DeepRulesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                                   lat=11.25, lon=77.1167, place="Kovilpalayam",
                                   name="Manoj")

    def test_loader_returns_thousands_of_classified_rules(self):
        rules = deep_rules.load_deep_rules()
        self.assertGreater(len(rules), 5000,
                           "expected >5000 deep-rules after classification")

    def test_predictions_for_returns_with_verse_id(self):
        preds = deep_rules.predictions_for(self.chart, "career", max_per_category=3)
        self.assertGreater(len(preds), 0)
        # at least one should carry a verse_id
        self.assertTrue(any(p.citations[0].verse_id for p in preds))

    def test_match_for_chart_subset(self):
        rules = deep_rules.load_deep_rules()
        matched = deep_rules.match_for_chart(self.chart, rules)
        self.assertLess(len(matched), len(rules))
        self.assertGreater(len(matched), 50)


class TamilNumerologyTests(unittest.TestCase):
    def test_manoj_matches_printed_page_13(self):
        r = tamil_numerology.compute(dt.date(1996, 5, 25))
        self.assertEqual(r.vidhi_number, 7)
        self.assertEqual(r.vidhi_planet, "Ketu")
        self.assertIn("Vaidooryam", r.lucky_gemstone)
        self.assertEqual(r.lucky_direction, "West")
        self.assertEqual(r.friendly_numbers, [5, 6, 8])
        self.assertEqual(r.hostile_numbers, [9])
        self.assertIn("Chitragupta", r.higher_deity)

    def test_render_markdown_contains_all_fields(self):
        r = tamil_numerology.compute(dt.date(1996, 5, 25))
        md = tamil_numerology.render_markdown(r)
        for tok in ("Vidhi", "Lucky Days", "Lucky Direction",
                    "Lucky Gemstone", "Friendly", "Hostile", "Deity"):
            self.assertIn(tok, md)


if __name__ == "__main__":
    unittest.main()
