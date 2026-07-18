"""Typed, deterministic Knowledge Graph primitives for Atro truth reports."""
from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
import json
from typing import Any, Mapping


GRAPH_SCHEMA_VERSION = "1.0"


def _json_safe(value: Any) -> Any:
    """Normalize graph payloads into deterministic JSON-compatible values."""
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, set):
        return sorted(_json_safe(item) for item in value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    """Create a stable identifier from canonical graph content."""
    if not prefix:
        raise ValueError("Graph identifier prefix is required")
    encoded = json.dumps(
        _json_safe(payload),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"


@dataclass(frozen=True)
class TruthNode:
    """A typed graph node with chart/report metadata."""

    id: str
    kind: str
    label: str
    layer: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "label": self.label,
            "layer": self.layer,
            "metadata": _json_safe(self.metadata),
        }


@dataclass(frozen=True)
class TruthEdge:
    """A typed relationship between two graph nodes."""

    id: str
    kind: str
    source_id: str
    target_id: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "metadata": _json_safe(self.metadata),
        }


class TruthGraph:
    """In-memory graph used by the truth engine and optional audit storage."""

    def __init__(self) -> None:
        self.nodes: dict[str, TruthNode] = {}
        self.edges: dict[str, TruthEdge] = {}

    def add_node(
        self,
        kind: str,
        label: str,
        layer: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        if not kind or not label or not layer:
            raise ValueError("Graph nodes require kind, label, and layer")

        normalized_metadata = _json_safe(dict(metadata or {}))
        payload = {
            "kind": kind,
            "label": label,
            "layer": layer,
            "metadata": normalized_metadata,
        }
        node_id = stable_id(kind, payload)
        self.nodes.setdefault(
            node_id,
            TruthNode(
                id=node_id,
                kind=kind,
                label=label,
                layer=layer,
                metadata=normalized_metadata,
            ),
        )
        return node_id

    def add_edge(
        self,
        kind: str,
        source_id: str,
        target_id: str,
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        if not kind:
            raise ValueError("Graph edges require a kind")
        if source_id not in self.nodes or target_id not in self.nodes:
            raise ValueError("Graph edges must reference existing nodes")

        normalized_metadata = _json_safe(dict(metadata or {}))
        payload = {
            "kind": kind,
            "source_id": source_id,
            "target_id": target_id,
            "metadata": normalized_metadata,
        }
        edge_id = stable_id("edge", payload)
        self.edges.setdefault(
            edge_id,
            TruthEdge(
                id=edge_id,
                kind=kind,
                source_id=source_id,
                target_id=target_id,
                metadata=normalized_metadata,
            ),
        )
        return edge_id

    def compact_summary(self) -> dict[str, Any]:
        nodes_by_kind: dict[str, int] = {}
        edges_by_kind: dict[str, int] = {}
        for node in self.nodes.values():
            nodes_by_kind[node.kind] = nodes_by_kind.get(node.kind, 0) + 1
        for edge in self.edges.values():
            edges_by_kind[edge.kind] = edges_by_kind.get(edge.kind, 0) + 1
        return {
            "nodes": len(self.nodes),
            "edges": len(self.edges),
            "nodes_by_kind": dict(sorted(nodes_by_kind.items())),
            "edges_by_kind": dict(sorted(edges_by_kind.items())),
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": GRAPH_SCHEMA_VERSION,
            "nodes": [self.nodes[node_id].to_dict() for node_id in sorted(self.nodes)],
            "edges": [self.edges[edge_id].to_dict() for edge_id in sorted(self.edges)],
            "summary": self.compact_summary(),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "TruthGraph":
        graph = cls()
        for raw in payload.get("nodes", []):
            node = TruthNode(
                id=str(raw["id"]),
                kind=str(raw["kind"]),
                label=str(raw["label"]),
                layer=str(raw["layer"]),
                metadata=_json_safe(raw.get("metadata", {})),
            )
            graph.nodes[node.id] = node
        for raw in payload.get("edges", []):
            edge = TruthEdge(
                id=str(raw["id"]),
                kind=str(raw["kind"]),
                source_id=str(raw["source_id"]),
                target_id=str(raw["target_id"]),
                metadata=_json_safe(raw.get("metadata", {})),
            )
            if edge.source_id not in graph.nodes or edge.target_id not in graph.nodes:
                raise ValueError("Serialized graph edge references an unknown node")
            graph.edges[edge.id] = edge
        return graph
