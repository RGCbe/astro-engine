"""API-level contract: /api/jathagam must carry the knowledge-graph truth report.

Verifies plan Task 4: `truth_report` is additive, deterministic in shape, and the
existing `truth` policy block stays present with consistent partial-failure data.
"""
from __future__ import annotations

import asyncio
import unittest


class TruthReportApiContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from src.api.main import jathagam
        from src.models.schemas import BirthData

        cls.result = asyncio.run(
            jathagam(BirthData(year=1996, month=5, day=25, time="20:25"))
        )

    def test_jathagam_response_has_truth_report_and_existing_truth_block(self):
        result = self.result
        self.assertEqual(result["status"], "success")
        self.assertIn("truth", result)
        self.assertIn("truth_report", result)
        self.assertEqual(result["truth_report"]["schema_version"], "1.0")
        self.assertTrue(result["truth_report"]["chart_facts"])

    def test_truth_report_graph_and_claims_are_populated(self):
        report = self.result["truth_report"]
        self.assertGreater(report["graph_summary"]["nodes"], 0)
        self.assertIn(report["report_state"], {"complete", "partial"})
        for claim in report["claims"]:
            self.assertIn(
                claim["status"],
                {"mechanical_fact", "supported", "tentative", "mixed", "insufficient_evidence"},
            )

    def test_partial_failures_agree_between_truth_block_and_truth_report(self):
        self.assertEqual(
            self.result["truth"]["partial_failures"],
            self.result["truth_report"]["data_quality"]["partial_failures"],
        )

    def test_existing_response_fields_are_preserved(self):
        for key in ("lagnam", "janma_rasi", "current_dasha", "dasha_schedule",
                    "house_predictions", "detected_yogas", "gochar"):
            self.assertIn(key, self.result)


if __name__ == "__main__":
    unittest.main()
