"""Tier-1 condition-aware rule resolution.

When two classical rules describe the SAME placement but opposite outcomes,
they are usually the two arms of one conditional (e.g. BPHS "5L in 7, if strong
-> gains" vs Saravali "5L in 7, if weak -> loss"). For a given chart only the
arm whose condition matches the planet's actual strength should survive.

These tests pin the pure decision core:
  _classify_condition(text)            -> STRONG | WEAK | NEUTRAL
  _condition_applies(condition, states) -> keep this rule for this chart?
"""
from __future__ import annotations

import unittest

from engine import book_rules


class ClassifyConditionTests(unittest.TestCase):
    def test_exalted_text_is_strong_condition(self):
        self.assertEqual(
            book_rules._classify_condition(
                "If the lord is exalted or in his own sign, the native gains wealth."),
            "STRONG")

    def test_debilitated_text_is_weak_condition(self):
        self.assertEqual(
            book_rules._classify_condition(
                "If the lord is debilitated or afflicted, there is loss and grief."),
            "WEAK")

    def test_plain_text_is_neutral_condition(self):
        self.assertEqual(
            book_rules._classify_condition(
                "The native will be devoted to elders and travel to distant lands."),
            "NEUTRAL")

    def test_mixed_strong_and_weak_markers_is_neutral(self):
        # exalted AND afflicted in one line -> not a clean branch -> NEUTRAL
        self.assertEqual(
            book_rules._classify_condition(
                "Though exalted, when afflicted by malefics the result is mixed."),
            "NEUTRAL")


class ConditionAppliesTests(unittest.TestCase):
    def test_strong_rule_dropped_when_planet_weak(self):
        self.assertFalse(book_rules._condition_applies("STRONG", ["WEAK"]))

    def test_weak_rule_dropped_when_planet_strong(self):
        self.assertFalse(book_rules._condition_applies("WEAK", ["STRONG"]))

    def test_strong_rule_kept_when_planet_strong(self):
        self.assertTrue(book_rules._condition_applies("STRONG", ["STRONG"]))

    def test_weak_rule_kept_when_planet_weak(self):
        self.assertTrue(book_rules._condition_applies("WEAK", ["WEAK"]))

    def test_neutral_rule_always_kept(self):
        self.assertTrue(book_rules._condition_applies("NEUTRAL", ["WEAK"]))
        self.assertTrue(book_rules._condition_applies("NEUTRAL", ["STRONG"]))

    def test_unknown_state_keeps_rule(self):
        # no strength info for the planet -> never drop (avoid false negatives)
        self.assertTrue(book_rules._condition_applies("STRONG", []))
        self.assertTrue(book_rules._condition_applies("WEAK", []))


class ChartStateMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from engine.chart import compute_chart
        cls.chart = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                                  place="Coimbatore", lat=11.0168, lon=76.9558,
                                  name="Manoj")

    def test_state_map_covers_grahas_with_valid_states(self):
        sm = book_rules.chart_state_map(self.chart)
        for p in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
            self.assertIn(p, sm)
            self.assertIn(sm[p], ("STRONG", "WEAK", "NEUTRAL"))

    def test_below_threshold_planets_are_weak(self):
        sm = book_rules.chart_state_map(self.chart)
        for p in self.chart.bala_summary.get("below_threshold", []):
            if p in sm:
                self.assertEqual(sm[p], "WEAK",
                                 f"{p} is below shadbala threshold but map says {sm[p]}")

    def test_strong_state_requires_above_threshold(self):
        sm = book_rules.chart_state_map(self.chart)
        above = set(self.chart.bala_summary.get("above_threshold", []))
        for p, st in sm.items():
            if st == "STRONG":
                self.assertIn(p, above,
                              f"{p} marked STRONG but not above shadbala threshold")


class ResolveConditionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from engine.chart import compute_chart
        cls.chart = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                                  place="Coimbatore", lat=11.0168, lon=76.9558,
                                  name="Manoj")
        cls.matched = book_rules.match_for_chart(cls.chart)

    def test_every_loaded_rule_has_condition_tag(self):
        for r in book_rules.load_rules()[:300]:
            self.assertIn(r.condition, ("STRONG", "WEAK", "NEUTRAL"))

    def test_resolve_returns_subset(self):
        kept = book_rules.resolve_conditions(self.matched, self.chart)
        self.assertLessEqual(len(kept), len(self.matched))

    def test_resolve_keeps_every_neutral_rule(self):
        kept_ids = {id(r) for r in book_rules.resolve_conditions(self.matched, self.chart)}
        for r in self.matched:
            if r.condition == "NEUTRAL":
                self.assertIn(id(r), kept_ids, "a NEUTRAL rule was wrongly dropped")

    def test_resolve_only_drops_contradicted_arms(self):
        sm = book_rules.chart_state_map(self.chart)
        kept_ids = {id(r) for r in book_rules.resolve_conditions(self.matched, self.chart)}
        for r in self.matched:
            if id(r) not in kept_ids:
                states = [sm.get(p, "NEUTRAL")
                          for p in book_rules._subject_planets(r, self.chart)]
                self.assertFalse(
                    book_rules._condition_applies(r.condition, states),
                    "a rule whose condition still applies was dropped")

    def test_to_predictions_accepts_chart_and_drops_contradicted_arm(self):
        # Pick a house whose lord is WEAK in this chart, then feed a STRONG-arm
        # rule for it. With no chart it surfaces; with the chart it is filtered.
        sm = book_rules.chart_state_map(self.chart)
        weak_house = next(
            (h for h in range(1, 13)
             if sm.get(book_rules._lord_of_house(self.chart, h)) == "WEAK"),
            None)
        self.assertIsNotNone(weak_house, "expected at least one weak house lord")
        strong_rule = book_rules.BookRule(
            type="lord_combo", book="TestBook", trigger="t",
            effect="If the lord is exalted the native gains great wealth and fame.",
            raw_effect="", params={"from_house": weak_house, "to_house": 1},
            topics=("wealth",), condition="STRONG")
        base = book_rules.to_predictions([strong_rule], "wealth")
        filt = book_rules.to_predictions([strong_rule], "wealth", chart=self.chart)
        self.assertEqual(len(base), 1)
        self.assertEqual(len(filt), 0,
                         "STRONG arm on a WEAK lord should drop when chart passed")


if __name__ == "__main__":
    unittest.main()
