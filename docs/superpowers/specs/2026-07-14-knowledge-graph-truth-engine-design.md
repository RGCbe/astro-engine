# Knowledge-Graph Truth Engine Design

**Status:** Approved by project owner through the "build the best engine" challenge.  
**Scope:** First production foundation for a single, explainable truth-report path.

## Goal

Turn Atro's existing calculations, rule engines, and citations into one canonical
truth report. The report must show one conclusion per topic only when its evidence
is applicable, traceable, and sufficiently corroborated. It must say `mixed` or
`insufficient_evidence` when the engine cannot honestly support a conclusion.

This is not a promise that astrology can guarantee a future event. "Truth" means:

1. Mechanical chart facts are reproducible.
2. Classical citations are traceable and applicable to the native's chart.
3. Derived findings identify the method that produced them.
4. Final synthesis exposes support, conflict, and uncertainty rather than hiding it.

## Chosen Architecture

Use a typed, engine-owned Knowledge Graph rather than a loose collection of module
outputs. The graph is represented by a stable Python domain model and can be stored
in SQLite for benchmark and audit work. Client API requests build an ephemeral graph
unless future consent and retention controls explicitly enable persistence.

SQLite is the first graph store because the current FastAPI/PM2 deployment has no
database service and must remain deployable as one application. The graph model and
store interface remain independent of SQLite so a future Neo4j adapter can be added
without changing report consumers.

### Alternatives Rejected

1. **In-memory JSON only:** quick, but not an auditable core and cannot support
   calibration/outcome links.
2. **Neo4j immediately:** graph-native, but adds a production service, credentials,
   backups, and operations before the evidence contract is proven.
3. **Typed graph + SQLite store:** selected. It provides durable graph semantics,
   deterministic tests, simple VPS deployment, and a clean migration seam.

## Graph Model

### Node Types

- `chart`: one computed natal chart and its engine version.
- `fact`: mechanical fact such as lagna, planetary placement, dasha, transit, or
  strength result.
- `method_finding`: an output from Parashari, Jaimini, KP, Nadi, Tajik, yoga,
  shadbala, ashtakavarga, gochar, or the life-event adapter.
- `citation`: a corpus passage with source label and applicability metadata.
- `claim`: a client-facing conclusion for a topic, period, or chart theme.
- `outcome`: a later verified historical event used only for calibration/audit.
- `report`: a versioned truth-report build.

### Edge Types

- `HAS_FACT`: chart -> fact.
- `PRODUCED_BY`: finding -> method.
- `SUPPORTS`: fact, finding, or citation -> claim.
- `CONTRADICTS`: fact or finding -> claim.
- `CITES`: claim or finding -> citation.
- `APPLIES_TO`: citation -> chart/fact.
- `CALIBRATED_BY`: claim profile -> verified outcome.
- `CONTAINS`: report -> claim or evidence node.

Every node and edge has a deterministic identifier, a source layer, a schema version,
and structured metadata. No raw HTML, random UUID, or untrusted client string is used
as a graph identifier.

## Evidence and Truth Rules

Each adapter emits normalized evidence with:

```json
{
  "topic": "career",
  "polarity": "support|contradict|neutral",
  "method_family": "parashari|jaimini|kp|nadi|tajik|strength|transit|corpus|life_event",
  "layer": "mechanical|cited|derived",
  "summary": "short factual reason",
  "source_refs": ["stable node ids"],
  "time_window": {"start": null, "end": null},
  "weight": 0.0
}
```

The fusion engine must not treat repeated rules from the same method family as
independent confirmation. It uses method-family diversity and applies these states:

- `mechanical_fact`: a directly computed, reproducible statement.
- `supported`: applicable natal evidence plus timing/context evidence from at least
  two independent method families.
- `tentative`: useful but single-family or incomplete corroboration.
- `mixed`: meaningful support and contradiction coexist.
- `insufficient_evidence`: no honest conclusion can be made.

Corpus citations can explain a claim but can never create a predictive claim alone.
Research-only `scratch/` weights remain prohibited from all graph adapters.

## Method Adapters in Phase 1

The first graph builder consumes the existing live `jathagam` response and normalizes:

- Swiss Ephemeris placements, lagna, dasha schedule, and panchangam.
- House readings and lagna-filtered corpus citations.
- Yogas and yoga citations.
- Shadbala and ashtakavarga strength context.
- Gochar/transit findings and citations.
- KP, Jaimini, Tajik, and Nadi output when each module returns success.

The life-event engine becomes an explicit adapter in the next task, after its output
shape is normalized and its current batch-only failure is repaired. It cannot silently
become another contradictory API pathway.

## Canonical Client Contract

`POST /api/jathagam` gains a `truth_report` object while preserving existing fields.
The PDF and translation layers will later consume the same object.

```json
{
  "schema_version": "1.0",
  "report_state": "complete|partial",
  "data_quality": {
    "birth_input": "provided",
    "partial_failures": []
  },
  "chart_facts": [],
  "claims": [
    {
      "id": "claim:...",
      "topic": "current_period",
      "status": "supported",
      "statement": "...",
      "time_window": {"start": null, "end": null},
      "confidence_band": "corroborated",
      "why": {"supports": [], "contradictions": [], "citations": []}
    }
  ],
  "method_coverage": {},
  "graph_summary": {"nodes": 0, "edges": 0, "claims": 0}
}
```

The public response exposes only a compact evidence trail. Full graph serialization is
available to internal benchmark/audit tooling, never required for normal client use.

## Persistence and Privacy

- Public API graphs are ephemeral by default.
- Benchmark graphs may be persisted to `data/truth_graph.sqlite3` with the engine
  version, chart identifier, and known outcomes.
- Persisting a private client graph requires a future explicit consent and deletion
  contract; this phase creates no silent client-history store.
- The graph store writes no API key, raw HTML, or unbounded corpus dump.

## Error Handling

An unavailable optional method becomes a coverage record with a safe code such as
`method_unavailable`; it does not remove unrelated evidence or expose raw exceptions
to clients. A graph build must always preserve mechanical facts and the existing
`truth` policy block.

## Test and Release Standard

1. Unit tests prove stable graph IDs, support/conflict resolution, method-family
   independence, citation-only rejection, and safe partial-method behavior.
2. An API-level test proves `truth_report` is deterministic for a fixed fixture and
   does not remove existing `jathagam` fields.
3. The integration suite must retain its current passing components; the known
   declarative life-event failure must not be masked as a graph success.
4. Deploy only after local tests pass, then run a VPS API smoke request that verifies
   both a normal report and a partial-method report.

## First Deliverable Boundary

This first implementation creates the reusable graph/fusion core and wires the live
API response into it. It does not claim that every historical runtime module is fully
unified, and it does not convert uncertain astrology into numeric event probability.
The next implementation cycle adds the repaired life-event adapter and makes the PDF
renderer read the canonical claim contract.
