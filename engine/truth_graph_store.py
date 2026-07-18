"""Explicit SQLite persistence for benchmark and audit truth graphs."""
from __future__ import annotations

from contextlib import closing
import json
from pathlib import Path
import sqlite3

from engine.truth_graph import GRAPH_SCHEMA_VERSION, TruthGraph


_ALLOWED_PURPOSES = {"benchmark", "audit"}


class SQLiteTruthGraphStore:
    """Persist explicitly selected graphs without joining the client API path."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection:
            with connection:
                connection.executescript(
                    """
                CREATE TABLE IF NOT EXISTS reports (
                    report_id TEXT PRIMARY KEY,
                    schema_version TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS nodes (
                    report_id TEXT NOT NULL,
                    node_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    label TEXT NOT NULL,
                    layer TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    PRIMARY KEY (report_id, node_id),
                    FOREIGN KEY (report_id) REFERENCES reports(report_id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS edges (
                    report_id TEXT NOT NULL,
                    edge_id TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    PRIMARY KEY (report_id, edge_id),
                    FOREIGN KEY (report_id) REFERENCES reports(report_id) ON DELETE CASCADE
                );
                """
                )

    def save(self, graph: TruthGraph, report_id: str, purpose: str = "benchmark") -> None:
        """Write one complete graph in a single transaction for explicit audit use."""
        if not report_id:
            raise ValueError("A report identifier is required")
        if purpose not in _ALLOWED_PURPOSES:
            raise ValueError("Truth graph persistence is limited to benchmark or audit purposes")

        graph_payload = graph.to_dict()
        with closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                INSERT INTO reports (report_id, schema_version, purpose)
                VALUES (?, ?, ?)
                ON CONFLICT(report_id) DO UPDATE SET
                    schema_version = excluded.schema_version,
                    purpose = excluded.purpose,
                    updated_at = CURRENT_TIMESTAMP
                """,
                    (report_id, GRAPH_SCHEMA_VERSION, purpose),
                )
                connection.execute("DELETE FROM nodes WHERE report_id = ?", (report_id,))
                connection.execute("DELETE FROM edges WHERE report_id = ?", (report_id,))
                connection.executemany(
                    """
                INSERT INTO nodes (report_id, node_id, kind, label, layer, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                    [
                    (
                        report_id,
                        node["id"],
                        node["kind"],
                        node["label"],
                        node["layer"],
                        json.dumps(node["metadata"], ensure_ascii=True, separators=(",", ":"), sort_keys=True),
                    )
                    for node in graph_payload["nodes"]
                    ],
                )
                connection.executemany(
                    """
                INSERT INTO edges (report_id, edge_id, kind, source_id, target_id, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                    [
                    (
                        report_id,
                        edge["id"],
                        edge["kind"],
                        edge["source_id"],
                        edge["target_id"],
                        json.dumps(edge["metadata"], ensure_ascii=True, separators=(",", ":"), sort_keys=True),
                    )
                    for edge in graph_payload["edges"]
                    ],
                )

    def load(self, report_id: str) -> TruthGraph:
        """Reconstruct a graph previously saved for benchmark or audit work."""
        with closing(self._connect()) as connection:
            report = connection.execute(
                "SELECT schema_version FROM reports WHERE report_id = ?", (report_id,)
            ).fetchone()
            if report is None:
                raise KeyError(f"Truth graph report not found: {report_id}")
            nodes = connection.execute(
                """
                SELECT node_id, kind, label, layer, metadata_json
                FROM nodes WHERE report_id = ? ORDER BY node_id
                """,
                (report_id,),
            ).fetchall()
            edges = connection.execute(
                """
                SELECT edge_id, kind, source_id, target_id, metadata_json
                FROM edges WHERE report_id = ? ORDER BY edge_id
                """,
                (report_id,),
            ).fetchall()

        return TruthGraph.from_dict(
            {
                "schema_version": report["schema_version"],
                "nodes": [
                    {
                        "id": row["node_id"],
                        "kind": row["kind"],
                        "label": row["label"],
                        "layer": row["layer"],
                        "metadata": json.loads(row["metadata_json"]),
                    }
                    for row in nodes
                ],
                "edges": [
                    {
                        "id": row["edge_id"],
                        "kind": row["kind"],
                        "source_id": row["source_id"],
                        "target_id": row["target_id"],
                        "metadata": json.loads(row["metadata_json"]),
                    }
                    for row in edges
                ],
            }
        )
