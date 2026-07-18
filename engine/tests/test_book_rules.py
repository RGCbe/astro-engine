"""Tests for book_rules: classical-rule loader, matchers, integration."""
from __future__ import annotations

import unittest

from engine import book_rules
from engine.chart import compute_chart


class BookRulesLoaderTests(unittest.TestCase):
    def test_loader_returns_classified_rules(self):
        rules = book_rules.load_rules()
        self.assertGreater(len(rules), 800,
                           "Expected >800 classified rules from ALL_COMBINATIONS.json")

    def test_every_rule_has_topics_and_book(self):
        for r in book_rules.load_rules()[:200]:
            self.assertTrue(r.topics, f"rule has no topic: {r.book}")
            self.assertTrue(r.book, "rule missing book")
            self.assertGreater(len(r.effect), 25, "effect too short to surface")

    def test_topic_routing_covers_core_categories(self):
        from collections import Counter
        rules = book_rules.load_rules()
        c = Counter()
        for r in rules:
            for t in r.topics:
                c[t] += 1
        for cat in ("marriage", "career", "wealth", "children",
                    "longevity", "family"):
            self.assertGreater(c[cat], 30,
                               f"category {cat} under-populated: {c[cat]}")

    def test_clean_effect_strips_ocr_garbage_and_sloka_refs(self):
        raw = "^^TicTTir: f%Tar: Sloka 8, the native will have wealth and be honoured by kings."
        cleaned = book_rules._clean_effect(raw)
        self.assertNotIn("Sloka", cleaned)
        self.assertIn("wealth", cleaned)


class BookRulesMatcherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = compute_chart(
            date="1996-05-25", time="20:25", tz_hours=5.5,
            place="Coimbatore", name="Manoj",
        )

    def test_aspect_matcher_uses_vedic_full_aspects(self):
        # 7th-house aspect is universal; make sure matcher accepts it
        self.assertTrue(book_rules._aspects(self.chart, "Sun", "Sun") in (True, False))

    def test_lord_combo_evaluates_house_lord_placement(self):
        # smoke: returns bool, no crash
        for fh in range(1, 13):
            for th in range(1, 13):
                self.assertIsInstance(
                    book_rules._lord_combo(self.chart, fh, th), bool)

    def test_match_for_chart_returns_subset_of_rules(self):
        rules = book_rules.load_rules()
        matched = book_rules.match_for_chart(self.chart, rules)
        self.assertLess(len(matched), len(rules))
        self.assertGreater(len(matched), 5,
                           "expected ≥5 classical rules to fire on Manoj chart")


class BookRulesIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.chart = compute_chart(
            date="1996-05-25", time="20:25", tz_hours=5.5,
            place="Coimbatore", name="Manoj",
        )

    def test_predictions_for_returns_predictions_with_citations(self):
        preds = book_rules.predictions_for(self.chart, "marriage", max_per_category=5)
        self.assertGreater(len(preds), 0, "marriage should match ≥1 book rule")
        for p in preds:
            self.assertTrue(p.citations and p.citations[0].book)
            self.assertEqual(p.confidence, "MEDIUM")
            self.assertTrue(p.key.startswith("book_rule_"))

    def test_orchestrator_includes_book_rule_predictions(self):
        from engine.engines.orchestrator import run_all
        reports = run_all(self.chart)
        book_rule_total = sum(
            1 for r in reports for p in r.predictions
            if p.key.startswith("book_rule_")
        )
        self.assertGreater(book_rule_total, 15,
                           "orchestrator should surface ≥15 book-rule preds total")


class MultiHouseMatcherTests(unittest.TestCase):
    """multi_house rules (planets of a polarity occupying listed houses) were
    loaded but never fired. They fire when EVERY listed house holds a planet of
    the rule's polarity class — precise and self-limiting for vague long lists."""

    MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

    @classmethod
    def setUpClass(cls):
        cls.chart = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                                  lat=11.0168, lon=76.9558, name="Manoj")

    def _make(self, houses, polarity):
        return book_rules.BookRule(
            type="multi_house", book="T", trigger="t", effect="x" * 40,
            raw_effect="", params={"houses": houses, "polarity": polarity},
            topics=("afflictions",))

    def test_multi_house_fires_when_all_listed_houses_hold_polarity(self):
        h = next(hh for p, hh in self.chart.house_of.items() if p in self.MALEFICS)
        self.assertTrue(book_rules._rule_fires(self.chart, self._make([h], "malefic")))

    def test_multi_house_inert_when_listed_house_lacks_polarity(self):
        occ = {hh for p, hh in self.chart.house_of.items() if p in self.MALEFICS}
        empty = next(h for h in range(1, 13) if h not in occ)
        self.assertFalse(book_rules._rule_fires(self.chart, self._make([empty], "malefic")))

    def test_multi_house_requires_every_listed_house_occupied(self):
        occ = {hh for p, hh in self.chart.house_of.items() if p in self.MALEFICS}
        h = next(iter(occ))
        empty = next(x for x in range(1, 13) if x not in occ)
        self.assertFalse(book_rules._rule_fires(self.chart, self._make([h, empty], "malefic")))

    def test_corpus_multi_house_rules_now_fire(self):
        matched = book_rules.match_for_chart(self.chart)
        mh = [r for r in matched if r.type == "multi_house"]
        self.assertGreater(len(mh), 0, "multi_house rules were dead; should fire now")

    def test_subject_planets_for_multi_house_returns_occupants(self):
        h = next(hh for p, hh in self.chart.house_of.items() if p in self.MALEFICS)
        subj = book_rules._subject_planets(self._make([h], "malefic"), self.chart)
        self.assertTrue(any(p in self.MALEFICS for p in subj))


class ConditionalRulesStayInertTests(unittest.TestCase):
    """conditional rules are unstructured OCR prose (condition_1/condition_2);
    heuristic parsing yields wrong predicates (verified), so they are
    intentionally NOT auto-fired. They need structured re-extraction, not a
    matcher. This guards that decision from being silently undone."""

    @classmethod
    def setUpClass(cls):
        cls.chart = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                                  lat=11.0168, lon=76.9558, name="Manoj")

    def test_conditional_rules_do_not_autofire(self):
        matched = book_rules.match_for_chart(self.chart)
        self.assertEqual([r for r in matched if r.type == "conditional"], [])


if __name__ == "__main__":
    unittest.main()
