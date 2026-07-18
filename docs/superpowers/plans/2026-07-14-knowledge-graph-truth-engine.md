# Knowledge-Graph Truth Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a graph-native, evidence-weighted truth-report core to Atro's live `jathagam` response without breaking existing API consumers.

**Architecture:** A typed `TruthGraph` holds chart facts, method findings, citations, claims, and their relationships. `TruthEngine` adapts the existing `jathagam` response into normalized evidence, fuses independent method families, and returns a compact public `truth_report`. `SQLiteTruthGraphStore` persists only explicit benchmark/audit graphs; live reports remain ephemeral.

**Tech Stack:** Python 3 standard library (`dataclasses`, `hashlib`, `json`, `sqlite3`), FastAPI, existing Atro engines, `unittest`.

## Global Constraints

- Preserve existing `POST /api/jathagam` response fields and tier behavior.
- Never import or surface `scratch/` research weights.
- Corpus citations explain claims but cannot independently create a predictive claim.
- Treat repeated evidence from one method family as one corroborating family.
- Return `mixed` or `insufficient_evidence` rather than fabricate consensus.
- Live client graphs are ephemeral; never persist API keys or private birth details by default.
- The project has no Git repository; do not run `git commit`. Record changed files in the final verification report instead.

---

### Task 1: Typed Graph Domain Model

**Files:**
- Create: `engine/truth_graph.py`
- Create: `engine/tests/test_truth_graph.py`

**Interfaces:**
- Produces `TruthNode`, `TruthEdge`, `TruthGraph`, and `stable_id(prefix, payload)`.
- `TruthGraph.add_node(kind, label, layer, metadata)` returns a deterministic node id.
- `TruthGraph.add_edge(kind, source_id, target_id, metadata=None)` returns a deterministic edge id.
- `TruthGraph.compact_summary()` returns counts by node and edge type.

- [ ] **Step 1: Write failing graph-domain tests**

```python
class TruthGraphTests(unittest.TestCase):
    def test_equivalent_nodes_share_a_stable_identifier(self):
        graph = TruthGraph()
        first = graph.add_node("fact", "Lagna is Sagittarius", "mechanical", {"lagna": "Sagittarius"})
        second = graph.add_node("fact", "Lagna is Sagittarius", "mechanical", {"lagna": "Sagittarius"})
        self.assertEqual(first, second)
        self.assertEqual(len(graph.nodes), 1)

    def test_edge_rejects_unknown_nodes(self):
        with self.assertRaises(ValueError):
            TruthGraph().add_edge("SUPPORTS", "missing", "also-missing")
```

- [ ] **Step 2: Run the graph tests and verify they fail**

Run: `python -m unittest engine.tests.test_truth_graph -v`  
Expected: failure because `engine.truth_graph` does not exist.

- [ ] **Step 3: Implement a deterministic, serializable graph**

```python
def stable_id(prefix: str, payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    digest = hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}:{digest}"

class TruthGraph:
    def add_node(self, kind, label, layer, metadata):
        payload = {"kind": kind, "label": label, "layer": layer, "metadata": metadata}
        node_id = stable_id(kind, payload)
        self.nodes.setdefault(node_id, TruthNode(node_id, kind, label, layer, dict(metadata)))
        return node_id
```

`add_edge` must validate both nodes exist, deduplicate identical edges, and `to_dict()` must return only JSON-safe data.

- [ ] **Step 4: Run the graph tests and verify they pass**

Run: `python -m unittest engine.tests.test_truth_graph -v`  
Expected: all tests pass.

- [ ] **Step 5: Record the completed files**

Git is unavailable in this project. Keep the changed-file list for final verification instead of attempting a commit.

### Task 2: Evidence Normalization and Fusion

**Files:**
- Create: `engine/truth_engine.py`
- Create: `engine/tests/test_truth_engine.py`

**Interfaces:**
- Produces `TruthEvidence`, `TruthClaim`, `TruthEngine`, and `build_truth_report(response_data)`.
- `TruthEngine.build(response_data)` returns the canonical report contract from the approved design.
- `TruthEngine._classify_claim(evidence)` returns `mechanical_fact`, `supported`, `tentative`, `mixed`, or `insufficient_evidence`.

- [ ] **Step 1: Write failing fusion tests**

```python
def test_two_independent_supporting_families_make_a_supported_claim():
    evidence = [
        TruthEvidence("current_period", "support", "parashari", "derived", "Dasha supports the period", (), weight=0.8),
        TruthEvidence("current_period", "support", "transit", "derived", "Transit corroborates the period", (), weight=0.7),
    ]
    claim = TruthEngine()._classify_claim(evidence)
    assert claim.status == "supported"

def test_citations_alone_cannot_create_a_predictive_claim():
    evidence = [
        TruthEvidence("career", "support", "corpus", "cited", "Rule one", (), weight=0.8),
        TruthEvidence("career", "support", "corpus", "cited", "Rule two", (), weight=0.8),
    ]
    claim = TruthEngine()._classify_claim(evidence)
    assert claim.status == "insufficient_evidence"

def test_conflicting_meaningful_evidence_is_mixed():
    evidence = [
        TruthEvidence("career", "support", "parashari", "derived", "Support", (), weight=0.8),
        TruthEvidence("career", "contradict", "kp", "derived", "Denial", (), weight=0.8),
    ]
    assert TruthEngine()._classify_claim(evidence).status == "mixed"
```

- [ ] **Step 2: Run the fusion tests and verify they fail**

Run: `python -m unittest engine.tests.test_truth_engine -v`  
Expected: failure because `engine.truth_engine` does not exist.

- [ ] **Step 3: Implement evidence adapters and deterministic fusion**

`TruthEngine` must create:

```python
TruthEvidence(
    topic="current_period",
    polarity="support",
    method_family="parashari",
    layer="mechanical",
    summary="Current Vimshottari period is Moon / Rahu.",
    source_refs=(dasha_fact_id,),
    weight=1.0,
)
```

It must adapt `lagnam`, `janma_rasi`, `current_dasha`, `dasha_schedule`, house
readings, yoga evidence, shadbala, ashtakavarga, gochar, KP, Jaimini, Tajik, and
Nadi output. It must produce mechanical facts even when optional methods fail.

- [ ] **Step 4: Run fusion tests and a fixture build**

Run: `python -m unittest engine.tests.test_truth_engine -v`  
Expected: all tests pass, including a report built from a minimal `jathagam` fixture.

- [ ] **Step 5: Record the completed files**

Git is unavailable in this project. Keep the changed-file list for final verification instead of attempting a commit.

### Task 3: SQLite Audit Store

**Files:**
- Create: `engine/truth_graph_store.py`
- Create: `engine/tests/test_truth_graph_store.py`

**Interfaces:**
- Produces `SQLiteTruthGraphStore(path)`.
- `save(graph, report_id, purpose="benchmark")` persists nodes and edges transactionally.
- `load(report_id)` reconstructs a `TruthGraph`.

- [ ] **Step 1: Write failing persistence tests**

```python
def test_round_trip_preserves_graph_nodes_and_edges(tmp_path):
    graph = TruthGraph()
    chart_id = graph.add_node("chart", "fixture", "mechanical", {"engine": "test"})
    fact_id = graph.add_node("fact", "fixture lagna", "mechanical", {"lagna": "Aries"})
    graph.add_edge("HAS_FACT", chart_id, fact_id)
    store = SQLiteTruthGraphStore(tmp_path / "truth.sqlite3")
    store.save(graph, "fixture-report")
    loaded = store.load("fixture-report")
    assert loaded.to_dict() == graph.to_dict()
```

- [ ] **Step 2: Run the persistence tests and verify they fail**

Run: `python -m unittest engine.tests.test_truth_graph_store -v`  
Expected: failure because `engine.truth_graph_store` does not exist.

- [ ] **Step 3: Implement a bounded SQLite store**

Use `sqlite3` with `reports`, `nodes`, and `edges` tables. Store JSON metadata,
enable foreign keys, and write each graph in one transaction. Reject purposes other
than `benchmark` or `audit`; do not wire the store into the public API.

- [ ] **Step 4: Run persistence tests and verify they pass**

Run: `python -m unittest engine.tests.test_truth_graph_store -v`  
Expected: all tests pass.

- [ ] **Step 5: Record the completed files**

Git is unavailable in this project. Keep the changed-file list for final verification instead of attempting a commit.

### Task 4: API and Truth-Policy Integration

**Files:**
- Modify: `src/services/jathagam_service.py:469-559`
- Modify: `engine/truth_policy.py`
- Create: `engine/tests/test_truth_report_api_contract.py`

**Interfaces:**
- `jathagam()` adds `truth_report` before tier gating and translation.
- `truth_report` is additive; existing response keys retain their current shape.
- `truth.policy_version` is updated only if the new report is correctly attached.

- [ ] **Step 1: Write the failing API-contract test**

```python
def test_jathagam_response_has_truth_report_and_existing_truth_block():
    result = asyncio.run(jathagam(BirthData(year=1996, month=5, day=25, time="20:25")))
    assert result["status"] == "success"
    assert "truth" in result
    assert "truth_report" in result
    assert result["truth_report"]["schema_version"] == "1.0"
    assert result["truth_report"]["chart_facts"]
```

- [ ] **Step 2: Run the API-contract test and verify it fails**

Run: `python -m unittest engine.tests.test_truth_report_api_contract -v`  
Expected: failure because the response lacks `truth_report`.

- [ ] **Step 3: Build the report before the existing truth block and tier gate**

```python
from engine.truth_engine import build_truth_report

response_data["truth_report"] = build_truth_report(response_data)
response_data["truth"] = build_client_truth_block(
    corpus_books=CORPUS.stats["books_loaded"],
    corpus_rules=CORPUS.stats["total_unique_rules"],
    modules_failed=response_data["truth_report"]["data_quality"]["partial_failures"],
)
```

Update `truth_policy.py` to list `truth_report.chart_facts` as mechanical and
`truth_report.claims` as evidence-weighted synthesis, never as guaranteed outcomes.

- [ ] **Step 4: Run the contract test and targeted regression tests**

Run: `python -m unittest engine.tests.test_truth_report_api_contract engine.tests.test_truth_graph engine.tests.test_truth_engine engine.tests.test_truth_graph_store -v`  
Expected: all tests pass.

- [ ] **Step 5: Record the completed files**

Git is unavailable in this project. Keep the changed-file list for final verification instead of attempting a commit.

### Task 5: Full Verification and VPS Release

**Files:**
- Modify only if required by test findings; otherwise no additional files.

**Interfaces:**
- Local test results prove graph, fusion, store, and API compatibility.
- VPS `/health` and `/api/jathagam` prove the deployed engine serves `truth_report`.

- [ ] **Step 1: Run focused graph and API tests**

Run: `python -m unittest engine.tests.test_truth_graph engine.tests.test_truth_engine engine.tests.test_truth_graph_store engine.tests.test_truth_report_api_contract -v`  
Expected: all tests pass.

- [ ] **Step 2: Run the existing integration suite**

Run: `python test_full_integration.py`  
Expected: existing integration components do not regress; report the pre-existing declarative-life-event status separately.

- [ ] **Step 3: Deploy only changed production files**

Deploy `engine/truth_graph.py`, `engine/truth_engine.py`, `engine/truth_graph_store.py`, `engine/truth_policy.py`, and `src/services/jathagam_service.py` to `/opt/astro`, then restart `astro-engine`.

- [ ] **Step 4: Verify the live response**

Run a VPS-local `POST /api/jathagam` using a fixed valid birth fixture. Verify:

```python
assert response["status"] == "success"
assert response["truth_report"]["schema_version"] == "1.0"
assert response["truth_report"]["graph_summary"]["nodes"] > 0
assert response["truth"]["partial_failures"] == response["truth_report"]["data_quality"]["partial_failures"]
```

- [ ] **Step 5: Report proof and remaining boundary**

Report the test results, VPS health response, deployed file hashes, and the explicit
next boundary: normalize and repair the lifetime-event adapter before using it in
canonical claims.
