"""Tests for explicit benchmark/audit persistence of truth graphs."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from engine.truth_graph import TruthGraph
from engine.truth_graph_store import SQLiteTruthGraphStore


class SQLiteTruthGraphStoreTests(unittest.TestCase):
    def test_round_trip_preserves_graph_nodes_and_edges(self):
        graph = TruthGraph()
        chart_id = graph.add_node("chart", "Fixture chart", "mechanical", {"engine": "test"})
        fact_id = graph.add_node("fact", "Lagna is Aries", "mechanical", {"lagna": "Aries"})
        graph.add_edge("HAS_FACT", chart_id, fact_id)

        with tempfile.TemporaryDirectory() as temporary_directory:
            store = SQLiteTruthGraphStore(Path(temporary_directory) / "truth.sqlite3")
            store.save(graph, "fixture-report")
            loaded = store.load("fixture-report")

        self.assertEqual(graph.to_dict(), loaded.to_dict())

    def test_rejects_non_audit_persistence_purposes(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            store = SQLiteTruthGraphStore(Path(temporary_directory) / "truth.sqlite3")
            with self.assertRaises(ValueError):
                store.save(TruthGraph(), "fixture-report", purpose="client_request")


if __name__ == "__main__":
    unittest.main()
