"""Tests for synth, dasa_narrative, life_narrative, event_feedback."""
from __future__ import annotations

import datetime as dt
import unittest

from engine.chart import compute_chart
from engine import synth, dasa_narrative, life_narrative, event_feedback


class SynthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = compute_chart(
            date="1996-05-25", time="20:25", tz_hours=5.5,
            place="Coimbatore", name="Manoj",
        )

    def test_synthesize_returns_facts_for_all_planets(self):
        facts = synth.synthesize(self.chart)
        for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter",
                  "Venus", "Saturn", "Rahu", "Ketu"):
            self.assertIn(p, facts)
            self.assertGreater(facts[p].house, 0)
            self.assertGreater(len(facts[p].life_areas), 3)

    def test_jupiter_is_own_sign_for_sagittarius_lagna(self):
        f = synth.fact(self.chart, "Jupiter")
        self.assertEqual(f.dignity, "own")
        self.assertEqual(f.house, 1)
        self.assertIn(1, f.bhavas_owned)
        self.assertIn(4, f.bhavas_owned)

    def test_planets_for_area_finds_father_karaka(self):
        sun_owners = synth.planets_for_area(self.chart, "father")
        self.assertIn("Sun", sun_owners)


class DasaNarrativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = compute_chart(
            date="1996-05-25", time="20:25", tz_hours=5.5,
            place="Coimbatore", name="Manoj",
        )

    def test_timeline_covers_birth_to_at_least_age_50(self):
        tl = dasa_narrative.build_timeline(self.chart)
        self.assertGreater(len(tl), 30)
        latest = max(d.period_end for d in tl)
        self.assertGreater(latest.year, 2040)

    def test_find_for_date_returns_correct_window(self):
        d = dasa_narrative.find_for_date(self.chart, dt.date(2021, 9, 1))
        self.assertEqual(d.md_lord, "Sun")
        self.assertEqual(d.ad_lord, "Mercury")

    def test_family_business_window_detected_in_2021(self):
        wins = dasa_narrative.find_window(self.chart, "family_business")
        self.assertTrue(any(w.period_start.year == 2021 for w in wins))

    def test_upcoming_returns_future_only(self):
        today = dt.date(2026, 4, 26)
        ups = dasa_narrative.upcoming(self.chart, n=4, today=today)
        for d in ups:
            self.assertGreaterEqual(d.period_end, today)


class LifeNarrativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = compute_chart(
            date="1996-05-25", time="20:25", tz_hours=5.5,
            place="Coimbatore", name="Manoj",
        )

    def test_timeline_table_contains_marker_for_current(self):
        out = life_narrative.timeline_table(self.chart, today=dt.date(2026, 4, 26))
        self.assertIn("★", out)
        self.assertIn("Moon-Rahu", out)

    def test_ask_finds_family_business_window(self):
        a = life_narrative.ask(self.chart, "when did I join my dad's shop?")
        self.assertTrue(a.found)
        self.assertIn("Family", a.summary)

    def test_ask_finds_promotion_window_in_future(self):
        a = life_narrative.ask(self.chart, "when will I get a promotion?",
                                today=dt.date(2026, 4, 26))
        self.assertTrue(a.found)
        self.assertGreaterEqual(a.windows[0].period_start, dt.date(2026, 4, 26))

    def test_ask_year_anchored_question(self):
        a = life_narrative.ask(self.chart, "what was happening in 2021?")
        self.assertTrue(a.found)
        self.assertIn("Sun-Mercury", a.summary)

    def test_full_narrative_contains_every_domain(self):
        out = life_narrative.full_narrative(self.chart, today=dt.date(2026, 4, 26))
        for h in ("Career & Profession", "Marriage & Partnership",
                  "Wealth & Finance", "Family — Parents & Siblings",
                  "Life Timeline (Vimshottari)"):
            self.assertIn(h, out)


class EventFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = compute_chart(
            date="1996-05-25", time="20:25", tz_hours=5.5,
            place="Coimbatore", name="Manoj",
        )

    def test_confirm_event_logs_match(self):
        log = event_feedback.confirm_event(
            self.chart, "joined dad shop", "2021-09-01")
        self.assertTrue(log.match)
        self.assertEqual(log.predicted_md, "Sun")
        self.assertGreater(log.score, 0.5)

    def test_get_weights_returns_dict(self):
        d = event_feedback.get_weights()
        self.assertIsInstance(d, dict)


if __name__ == "__main__":
    unittest.main()
