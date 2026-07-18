"""Life-event claims in the knowledge-graph truth report.

Fused convergent events (engine.event_fusion) must enter the TruthGraph as
`supported` claims with SUPPORTS edges from one method-finding per contributing
family, and method_coverage must report the life_event adapter state honestly.
"""
from __future__ import annotations

import unittest

from engine.truth_engine import TruthEngine, build_truth_report

_BASE_RESPONSE = {
    "engine_version": "6.0",
    "lagnam": "Dhanusu",
    "janma_rasi": "Simmam",
    "janma_nakshatra": "Magha",
    "current_dasha": "Moon",
    "current_antardasha": "Jupiter",
    "dasha_schedule": [{"lord": "Moon", "start": "2023-06-17", "end": "2033-06-17"}],
}

_FUSED = [{
    "event": "Converged children indication (2 independent methods)",
    "category": "children",
    "window_start": "2025-02-20",
    "window_end": "2025-06-10",
    "date": "2025-04-16",
    "max_sev": 4,
    "families": ["parashari", "tajik"],
    "contributors": 3,
    "predicted_valence": "auspicious",
}]


class LifeEventClaimTests(unittest.TestCase):
    def test_fused_events_become_supported_time_windowed_claims(self):
        report = build_truth_report(_BASE_RESPONSE, life_events=_FUSED)
        life_claims = [c for c in report["claims"] if c["topic"] == "children"]
        self.assertEqual(len(life_claims), 1)
        claim = life_claims[0]
        self.assertEqual(claim["status"], "supported")
        self.assertEqual(claim["confidence_band"], "corroborated")
        self.assertEqual(claim["time_window"], {"start": "2025-02-20", "end": "2025-06-10"})
        # one supporting finding per contributing family
        self.assertEqual(len(claim["why"]["supports"]), 2)
        self.assertIn("parashari", claim["statement"])
        self.assertIn("tajik", claim["statement"])

    def test_coverage_states_are_honest(self):
        ran = build_truth_report(_BASE_RESPONSE, life_events=_FUSED)
        self.assertEqual(ran["method_coverage"]["life_event"], {"state": "available"})
        empty = build_truth_report(_BASE_RESPONSE, life_events=[])
        self.assertEqual(empty["method_coverage"]["life_event"], {"state": "available"})
        self.assertFalse([c for c in empty["claims"] if c["topic"] == "children"])
        not_run = build_truth_report(_BASE_RESPONSE)
        self.assertEqual(not_run["method_coverage"]["life_event"]["state"], "not_run")

    def test_not_run_is_not_a_partial_failure(self):
        report = build_truth_report(_BASE_RESPONSE)
        self.assertNotIn("life_event", report["data_quality"]["partial_failures"])
        self.assertEqual(report["report_state"], "complete")

    def test_claims_are_deterministic(self):
        a = build_truth_report(_BASE_RESPONSE, life_events=_FUSED)
        b = build_truth_report(_BASE_RESPONSE, life_events=list(_FUSED))
        ids_a = sorted(c["id"] for c in a["claims"])
        ids_b = sorted(c["id"] for c in b["claims"])
        self.assertEqual(ids_a, ids_b)


if __name__ == "__main__":
    unittest.main()
