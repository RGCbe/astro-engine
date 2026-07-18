"""Tests for evidence normalization and graph-based truth fusion."""
from __future__ import annotations

import unittest

from engine.truth_engine import TruthEngine, TruthEvidence, build_truth_report


class TruthFusionTests(unittest.TestCase):
    def test_two_independent_supporting_families_make_a_supported_claim(self):
        evidence = [
            TruthEvidence(
                "current_period",
                "support",
                "parashari",
                "derived",
                "Dasha supports the period.",
                (),
                weight=0.8,
            ),
            TruthEvidence(
                "current_period",
                "support",
                "transit",
                "derived",
                "Transit corroborates the period.",
                (),
                weight=0.7,
            ),
        ]

        claim = TruthEngine()._classify_claim(evidence)

        self.assertEqual("supported", claim.status)
        self.assertEqual("corroborated", claim.confidence_band)

    def test_citations_alone_cannot_create_a_predictive_claim(self):
        evidence = [
            TruthEvidence("career", "support", "corpus", "cited", "Rule one", (), weight=0.8),
            TruthEvidence("career", "support", "corpus", "cited", "Rule two", (), weight=0.8),
        ]

        claim = TruthEngine()._classify_claim(evidence)

        self.assertEqual("insufficient_evidence", claim.status)

    def test_conflicting_independent_evidence_is_mixed(self):
        evidence = [
            TruthEvidence("career", "support", "parashari", "derived", "Support", (), weight=0.8),
            TruthEvidence("career", "contradict", "kp", "derived", "Denial", (), weight=0.8),
        ]

        claim = TruthEngine()._classify_claim(evidence)

        self.assertEqual("mixed", claim.status)
        self.assertEqual("contested", claim.confidence_band)


class TruthReportBuilderTests(unittest.TestCase):
    def test_builds_mechanical_facts_and_safe_partial_method_coverage(self):
        response_data = {
            "status": "success",
            "engine_version": "6.0",
            "lagnam": "Sagittarius",
            "janma_rasi": "Leo",
            "janma_nakshatra": "Magha",
            "current_dasha": "Moon",
            "current_antardasha": "Rahu",
            "dasha_schedule": [{"lord": "Moon", "start": "2025-01-01", "end": "2035-01-01"}],
            "house_predictions": [
                {
                    "planet": "Jupiter",
                    "house": 1,
                    "rasi": "Sagittarius",
                    "nakshatra": "Mula",
                    "corpus_rules": [{"source": "BPHS", "text": "A cited rule."}],
                    "evaluation": {"is_afflicted": False, "caveat": ""},
                }
            ],
            "detected_yogas": [],
            "gochar": {"transit_planets": []},
            "shadbala": {"summary": {"strongest": ["Jupiter"]}},
            "ashtakavarga": {"grand_total": 337},
            "kp_analysis": {"moon_sub_lord": "Venus"},
            "jaimini_analysis": {"status": "success", "karakas": {"AK": "Jupiter"}},
            "tajika_analysis": {"status": "error", "message": "private diagnostic"},
            "nadi_analysis": {"status": "success"},
        }

        report = build_truth_report(response_data)

        fact_labels = {fact["label"] for fact in report["chart_facts"]}
        self.assertIn("Lagna is Sagittarius", fact_labels)
        self.assertIn("Current Vimshottari period is Moon / Rahu", fact_labels)
        self.assertEqual("partial", report["report_state"])
        self.assertEqual(["tajik"], report["data_quality"]["partial_failures"])
        self.assertGreater(report["graph_summary"]["nodes"], 0)
        self.assertNotIn("private diagnostic", str(report))


if __name__ == "__main__":
    unittest.main()
