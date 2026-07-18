"""Tests for the typed, deterministic Knowledge Graph domain model."""
from __future__ import annotations

import json
import unittest

from engine.truth_graph import TruthGraph


class TruthGraphTests(unittest.TestCase):
    def test_equivalent_nodes_share_a_stable_identifier(self):
        graph = TruthGraph()

        first = graph.add_node(
            "fact",
            "Lagna is Sagittarius",
            "mechanical",
            {"lagna": "Sagittarius"},
        )
        second = graph.add_node(
            "fact",
            "Lagna is Sagittarius",
            "mechanical",
            {"lagna": "Sagittarius"},
        )

        self.assertEqual(first, second)
        self.assertEqual(1, len(graph.nodes))

    def test_edge_rejects_unknown_nodes(self):
        with self.assertRaises(ValueError):
            TruthGraph().add_edge("SUPPORTS", "missing", "also-missing")

    def test_graph_serialization_is_json_safe_and_deduplicates_edges(self):
        graph = TruthGraph()
        chart_id = graph.add_node("chart", "Fixture chart", "mechanical", {"fixture": True})
        fact_id = graph.add_node("fact", "Lagna is Aries", "mechanical", {"lagna": "Aries"})

        first_edge = graph.add_edge("HAS_FACT", chart_id, fact_id)
        second_edge = graph.add_edge("HAS_FACT", chart_id, fact_id)
        payload = graph.to_dict()

        self.assertEqual(first_edge, second_edge)
        self.assertEqual(1, len(graph.edges))
        self.assertEqual({"chart": 1, "fact": 1}, payload["summary"]["nodes_by_kind"])
        self.assertEqual({"HAS_FACT": 1}, payload["summary"]["edges_by_kind"])
        json.dumps(payload)


if __name__ == "__main__":
    unittest.main()
