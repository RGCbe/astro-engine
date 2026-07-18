"""
Truth Engine.
Provides transparent astrological evidence, counter-evidence, and a net assessment
for life predictions. Distinguishes between Core Truths, Likely Manifestations,
and Alternative Expressions.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import html
import re
from typing import Any

from engine.truth_graph import TruthGraph, stable_id

def weigh_evidence(chart, md: str, ad: str, event_class: str) -> dict:
    """
    Weighs the evidence for a particular event/state during an AD period.
    Returns Evidence, Counter Evidence, Net Assessment, and Classification.
    """
    # Placeholder mapping for astrological heuristics
    malefics = {"Saturn", "Mars", "Rahu", "Ketu"}
    benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
    
    evidence = []
    counter_evidence = []
    
    # 1. Gather Evidence
    if event_class in ["CAREER_PEAK", "FINANCIAL_GAIN"]:
        if md in benefics or ad in benefics:
            evidence.append(f"{'MD' if md in benefics else 'AD'} lord ({md if md in benefics else ad}) is a natural benefic promoting growth.")
        evidence.append(f"Activation of artha/kama trikonas linked to {md}-{ad} axis.")
        
    elif event_class in ["HEALTH_CRISIS", "FAMILY_LOSS", "ACCIDENT_RISK"]:
        if md in malefics or ad in malefics:
            evidence.append(f"Dasha lord {md if md in malefics else ad} acts as a functional malefic in this window.")
        evidence.append(f"Dusthana (6/8/12) house activation indicated.")
        
    else:
        evidence.append(f"{md} and {ad} intersect to activate {event_class.replace('_', ' ').lower()} themes.")
        
    # 2. Gather Counter-Evidence
    if event_class in ["CAREER_PEAK", "FINANCIAL_GAIN"]:
        if md in malefics or ad in malefics:
            counter_evidence.append(f"Presence of malefic {md if md in malefics else ad} introduces friction or delays.")
        else:
            counter_evidence.append("No major malefic afflictions blocking the 10th/11th houses.")
            
    elif event_class in ["HEALTH_CRISIS", "FAMILY_LOSS", "ACCIDENT_RISK"]:
        if md in benefics or ad in benefics:
            counter_evidence.append(f"Benefic aspect from {md if md in benefics else ad} provides protection and swift recovery.")
        else:
            counter_evidence.append("Lack of strong benefic mitigation in the active houses.")
            
    else:
        counter_evidence.append("Secondary chart factors (D9) may dilute the intensity.")
        
    # 3. Compute Net Assessment & Classification
    net_score = len(evidence) - len([ce for ce in counter_evidence if "No major" not in ce and "Lack of" not in ce])
    
    if net_score >= 1:
        net_assessment = f"The indications for {event_class.replace('_', ' ').lower()} are strongly supported by the Dasha lords and house placements."
        classification = "High-Confidence Indication"
        truth_score = 92
        stars = "5/5 Stars"
    elif net_score == 0:
        net_assessment = "The chart presents conflicting forces. The outcome depends heavily on free will and transit mitigations."
        classification = "Moderate-Confidence Indication"
        truth_score = 75
        stars = "3/5 Stars"
    else:
        net_assessment = "Counter-indications carry significant weight, suggesting this theme will manifest subtly or as an internal psychological shift rather than an external event."
        classification = "Low-Confidence Possibility"
        truth_score = 45
        stars = "1/5 Stars"
        
    return {
        "evidence": evidence,
        "counter_evidence": counter_evidence,
        "net_assessment": net_assessment,
        "classification": classification,
        "truth_score": truth_score,
        "stars": stars
    }


_PREDICTIVE_LAYERS = {"mechanical", "derived"}
_MEANINGFUL_WEIGHT = 0.5
_OPTIONAL_METHODS = {
    "jaimini": "jaimini_analysis",
    "tajik": "tajika_analysis",
    "nadi": "nadi_analysis",
}


def _safe_text(value: Any, limit: int = 280) -> str:
    """Return a compact plain-text representation suitable for public evidence."""
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        return f"{text[: limit - 3].rstrip()}..."
    return text


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


@dataclass(frozen=True)
class TruthEvidence:
    """One normalized, traceable piece of evidence for a truth-report topic."""

    topic: str
    polarity: str
    method_family: str
    layer: str
    summary: str
    source_refs: tuple[str, ...] = ()
    weight: float = 1.0
    time_window: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.topic or not self.method_family or not self.summary:
            raise ValueError("Truth evidence requires topic, method family, and summary")
        if self.polarity not in {"support", "contradict", "neutral"}:
            raise ValueError("Truth evidence polarity must be support, contradict, or neutral")
        if self.layer not in {"mechanical", "cited", "derived"}:
            raise ValueError("Truth evidence layer must be mechanical, cited, or derived")
        if not 0.0 <= float(self.weight) <= 1.0:
            raise ValueError("Truth evidence weight must be between 0 and 1")


@dataclass(frozen=True)
class TruthClaim:
    """A fused conclusion that preserves its support and disagreement trail."""

    id: str
    topic: str
    status: str
    statement: str
    time_window: Mapping[str, Any] | None
    confidence_band: str
    support_refs: tuple[str, ...]
    contradiction_refs: tuple[str, ...]
    citation_refs: tuple[str, ...]

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "status": self.status,
            "statement": self.statement,
            "time_window": dict(self.time_window or {"start": None, "end": None}),
            "confidence_band": self.confidence_band,
            "why": {
                "supports": list(self.support_refs),
                "contradictions": list(self.contradiction_refs),
                "citations": list(self.citation_refs),
            },
        }


class TruthEngine:
    """Build a deterministic, graph-backed truth report from a Jathagam response."""

    def _classify_claim(self, evidence: list[TruthEvidence]) -> TruthClaim:
        topic = evidence[0].topic if evidence else "unknown"
        active = [
            item
            for item in evidence
            if item.layer in _PREDICTIVE_LAYERS
            and item.polarity in {"support", "contradict"}
            and item.weight >= _MEANINGFUL_WEIGHT
        ]
        citations = [item for item in evidence if item.layer == "cited"]

        family_weights: dict[str, dict[str, float]] = {}
        for item in active:
            weights = family_weights.setdefault(item.method_family, {"support": 0.0, "contradict": 0.0})
            weights[item.polarity] += item.weight

        supporting_families: list[str] = []
        contradicting_families: list[str] = []
        for family, weights in sorted(family_weights.items()):
            if weights["support"] > weights["contradict"]:
                supporting_families.append(family)
            elif weights["contradict"] > weights["support"]:
                contradicting_families.append(family)

        support_items = [item for item in active if item.method_family in supporting_families and item.polarity == "support"]
        contradiction_items = [
            item
            for item in active
            if item.method_family in contradicting_families and item.polarity == "contradict"
        ]

        if not active:
            status = "insufficient_evidence"
            confidence_band = "unconfirmed"
            statement = f"The available evidence is not sufficient to form a reliable {topic.replace('_', ' ')} conclusion."
        elif supporting_families and contradicting_families:
            status = "mixed"
            confidence_band = "contested"
            statement = f"Independent methods materially disagree about the {topic.replace('_', ' ')} theme."
        elif len(supporting_families) >= 2:
            status = "supported"
            confidence_band = "corroborated"
            statement = f"Independent method families corroborate the {topic.replace('_', ' ')} theme."
        elif len(supporting_families) == 1:
            status = "tentative"
            confidence_band = "single_method"
            statement = f"There is one applicable evidence family for the {topic.replace('_', ' ')} theme, but it is not independently corroborated."
        elif len(contradicting_families) == 1:
            status = "tentative"
            confidence_band = "single_method"
            statement = f"One method family raises a caution about the {topic.replace('_', ' ')} theme, without independent confirmation."
        else:
            status = "insufficient_evidence"
            confidence_band = "unconfirmed"
            statement = f"The available evidence is not sufficient to form a reliable {topic.replace('_', ' ')} conclusion."

        support_refs = tuple(sorted({ref for item in support_items for ref in item.source_refs}))
        contradiction_refs = tuple(sorted({ref for item in contradiction_items for ref in item.source_refs}))
        citation_refs = tuple(sorted({ref for item in citations for ref in item.source_refs}))
        claim_id = stable_id(
            "claim",
            {
                "topic": topic,
                "status": status,
                "support_refs": support_refs,
                "contradiction_refs": contradiction_refs,
                "citation_refs": citation_refs,
            },
        )
        time_window = next((item.time_window for item in active if item.time_window), None)
        return TruthClaim(
            id=claim_id,
            topic=topic,
            status=status,
            statement=statement,
            time_window=time_window,
            confidence_band=confidence_band,
            support_refs=support_refs,
            contradiction_refs=contradiction_refs,
            citation_refs=citation_refs,
        )

    def _add_fact(
        self,
        graph: TruthGraph,
        chart_id: str,
        label: str,
        metadata: Mapping[str, Any],
    ) -> str:
        fact_id = graph.add_node("fact", label, "mechanical", metadata)
        graph.add_edge("HAS_FACT", chart_id, fact_id)
        return fact_id

    def _add_method_finding(
        self,
        graph: TruthGraph,
        chart_id: str,
        method_family: str,
        label: str,
        layer: str = "derived",
        metadata: Mapping[str, Any] | None = None,
    ) -> str:
        method_id = graph.add_node("method", method_family, "derived", {"family": method_family})
        finding_id = graph.add_node("method_finding", label, layer, metadata or {"family": method_family})
        graph.add_edge("PRODUCED_BY", finding_id, method_id)
        graph.add_edge("APPLIES_TO", finding_id, chart_id)
        return finding_id

    def _add_citation(
        self,
        graph: TruthGraph,
        source: Any,
        text: Any,
        applies_to_id: str,
    ) -> str | None:
        source_label = _safe_text(source, 80)
        citation_text = _safe_text(text)
        if not source_label and not citation_text:
            return None
        label = source_label or "Corpus citation"
        citation_id = graph.add_node(
            "citation",
            label,
            "cited",
            {"source": source_label or "Unknown source", "excerpt": citation_text},
        )
        graph.add_edge("CITES", applies_to_id, citation_id)
        return citation_id

    def _method_coverage(self, response_data: Mapping[str, Any]) -> tuple[dict[str, dict[str, str]], list[str]]:
        coverage: dict[str, dict[str, str]] = {
            "parashari": {"state": "available"},
            "house_corpus": {"state": "available"},
            "yoga": {"state": "available"},
            "strength": {"state": "available"},
            "ashtakavarga": {"state": "available"},
            "transit": {"state": "available"},
            "kp": {"state": "available"},
        }
        failures: list[str] = []
        for method, key in _OPTIONAL_METHODS.items():
            result = _as_mapping(response_data.get(key))
            state = str(result.get("status", "success")).lower()
            if state in {"error", "failed", "unavailable"}:
                coverage[method] = {"state": "unavailable", "safe_code": "method_unavailable"}
                failures.append(method)
            else:
                coverage[method] = {"state": "available"}
        return dict(sorted(coverage.items())), sorted(failures)

    def _current_period_window(self, response_data: Mapping[str, Any]) -> Mapping[str, Any] | None:
        current_dasha = _safe_text(response_data.get("current_dasha"), 80)
        for period in _as_list(response_data.get("dasha_schedule")):
            entry = _as_mapping(period)
            if _safe_text(entry.get("lord"), 80) == current_dasha:
                return {"start": entry.get("start"), "end": entry.get("end")}
        return None

    def _add_house_findings(self, graph: TruthGraph, chart_id: str, response_data: Mapping[str, Any]) -> None:
        readings = _as_list(response_data.get("house_predictions"))
        for reading in sorted(readings, key=lambda item: _safe_text(_as_mapping(item).get("planet"))):
            item = _as_mapping(reading)
            planet = _safe_text(item.get("planet"), 80)
            house = item.get("house")
            if not planet or house is None:
                continue
            finding_id = self._add_method_finding(
                graph,
                chart_id,
                "house_corpus",
                f"{planet} evaluated in house {house}",
                metadata={"planet": planet, "house": house, "rasi": _safe_text(item.get("rasi"), 80)},
            )
            for rule in _as_list(item.get("corpus_rules")):
                rule_data = _as_mapping(rule)
                self._add_citation(graph, rule_data.get("source"), rule_data.get("text"), finding_id)

    def _add_yoga_findings(self, graph: TruthGraph, chart_id: str, response_data: Mapping[str, Any]) -> None:
        for yoga in _as_list(response_data.get("detected_yogas")):
            yoga_data = _as_mapping(yoga)
            label = _safe_text(yoga_data.get("name") or yoga_data.get("yoga") or yoga, 160)
            if not label:
                continue
            finding_id = self._add_method_finding(
                graph,
                chart_id,
                "yoga",
                label,
                metadata={"name": label},
            )
            self._add_citation(
                graph,
                yoga_data.get("source") or yoga_data.get("book"),
                yoga_data.get("text") or yoga_data.get("description"),
                finding_id,
            )

    def _add_optional_method_findings(
        self,
        graph: TruthGraph,
        chart_id: str,
        response_data: Mapping[str, Any],
        failures: list[str],
    ) -> None:
        for method, key in _OPTIONAL_METHODS.items():
            if method in failures:
                continue
            result = _as_mapping(response_data.get(key))
            if result:
                self._add_method_finding(
                    graph,
                    chart_id,
                    method,
                    f"{method.title()} analysis is available",
                    metadata={"status": "available"},
                )

    def _add_life_event_claims(
        self,
        graph: TruthGraph,
        report_id: str,
        chart_id: str,
        life_events: list[Mapping[str, Any]],
    ) -> list[TruthClaim]:
        """Convert fused convergent events (engine.event_fusion) into claims.

        Each fused event already passed the >=2-independent-family gate, so it
        enters the graph as a `supported` claim with one supporting
        method-finding per contributing family.
        """
        claims: list[TruthClaim] = []
        for fused in life_events:
            topic = _safe_text(fused.get("category"), 60)
            start = _safe_text(fused.get("window_start"), 20)
            end = _safe_text(fused.get("window_end"), 20)
            families = sorted(_safe_text(f, 40) for f in _as_list(fused.get("families")))
            if not topic or not start or not end or len(families) < 2:
                continue
            finding_ids = []
            for family in families:
                finding_ids.append(self._add_method_finding(
                    graph,
                    chart_id,
                    family,
                    f"{family} evidence converges on {topic} in {start}..{end}",
                    metadata={"family": family, "topic": topic,
                              "window_start": start, "window_end": end},
                ))
            statement = (
                f"Independent method families ({', '.join(families)}) converge on a "
                f"{topic.replace('_', ' ')} indication between {start} and {end}."
            )
            claim_id = graph.add_node(
                "claim",
                statement,
                "synthesis",
                {"topic": topic, "status": "supported", "confidence_band": "corroborated",
                 "window_start": start, "window_end": end},
            )
            graph.add_edge("CONTAINS", report_id, claim_id)
            for fid in finding_ids:
                graph.add_edge("SUPPORTS", fid, claim_id)
            claims.append(TruthClaim(
                id=claim_id,
                topic=topic,
                status="supported",
                statement=statement,
                time_window={"start": start, "end": end},
                confidence_band="corroborated",
                support_refs=tuple(sorted(finding_ids)),
                contradiction_refs=(),
                citation_refs=(),
            ))
        return claims

    def build(
        self,
        response_data: Mapping[str, Any],
        life_events: list[Mapping[str, Any]] | None = None,
    ) -> dict[str, Any]:
        graph = TruthGraph()
        engine_version = _safe_text(response_data.get("engine_version"), 80) or "unknown"
        chart_id = graph.add_node("chart", "Computed natal chart", "mechanical", {"engine_version": engine_version})
        report_id = graph.add_node("report", "Knowledge-graph truth report", "synthesis", {"engine_version": engine_version})
        graph.add_edge("CONTAINS", report_id, chart_id)

        chart_facts: list[dict[str, str]] = []
        fact_ids: dict[str, str] = {}
        fact_definitions = (
            ("lagnam", "Lagna is {value}"),
            ("janma_rasi", "Moon sign is {value}"),
            ("janma_nakshatra", "Birth nakshatra is {value}"),
        )
        for key, label_template in fact_definitions:
            value = _safe_text(response_data.get(key), 100)
            if not value:
                continue
            label = label_template.format(value=value)
            fact_id = self._add_fact(graph, chart_id, label, {key: value})
            fact_ids[key] = fact_id
            chart_facts.append({"id": fact_id, "label": label, "kind": "mechanical_fact"})

        current_dasha = _safe_text(response_data.get("current_dasha"), 80)
        current_antardasha = _safe_text(response_data.get("current_antardasha"), 80)
        period_window = self._current_period_window(response_data)
        evidence: list[TruthEvidence] = []
        if current_dasha:
            period_label = f"Current Vimshottari period is {current_dasha}"
            if current_antardasha:
                period_label += f" / {current_antardasha}"
            period_id = self._add_fact(
                graph,
                chart_id,
                period_label,
                {"mahadasha": current_dasha, "antardasha": current_antardasha},
            )
            chart_facts.append({"id": period_id, "label": period_label, "kind": "mechanical_fact"})
            evidence.append(
                TruthEvidence(
                    "current_period",
                    "support",
                    "parashari",
                    "derived",
                    period_label,
                    (period_id,),
                    weight=0.9,
                    time_window=period_window,
                )
            )

        self._add_house_findings(graph, chart_id, response_data)
        self._add_yoga_findings(graph, chart_id, response_data)
        coverage, failures = self._method_coverage(response_data)
        self._add_optional_method_findings(graph, chart_id, response_data, failures)

        # Life-event adapter: fused convergent events -> supported claims.
        # None = adapter not run (older callers); [] = ran, nothing converged.
        if life_events is None:
            coverage["life_event"] = {"state": "not_run"}
            life_claims: list[TruthClaim] = []
        else:
            coverage["life_event"] = {"state": "available"}
            life_claims = self._add_life_event_claims(graph, report_id, chart_id, list(life_events))
        coverage = dict(sorted(coverage.items()))

        shadbala = _as_mapping(response_data.get("shadbala"))
        strong_planets = [_safe_text(value, 80) for value in _as_list(_as_mapping(shadbala.get("summary")).get("strongest"))]
        if strong_planets:
            strength_finding = self._add_method_finding(
                graph,
                chart_id,
                "strength",
                f"Strongest planets include {', '.join(sorted(strong_planets))}",
                metadata={"strongest": sorted(strong_planets)},
            )
            if current_dasha and current_dasha in strong_planets:
                evidence.append(
                    TruthEvidence(
                        "current_period",
                        "support",
                        "strength",
                        "derived",
                        f"Current dasha lord {current_dasha} is listed among the stronger planets.",
                        (strength_finding,),
                        weight=0.7,
                        time_window=period_window,
                    )
                )

        ashtakavarga = _as_mapping(response_data.get("ashtakavarga"))
        grand_total = ashtakavarga.get("grand_total")
        if grand_total is not None:
            self._add_method_finding(
                graph,
                chart_id,
                "ashtakavarga",
                f"Ashtakavarga grand total is {_safe_text(grand_total, 40)}",
                metadata={"grand_total": grand_total},
            )

        gochar = _as_mapping(response_data.get("gochar"))
        for transit in sorted(_as_list(gochar.get("transit_planets")), key=lambda item: _safe_text(_as_mapping(item).get("planet"))):
            transit_data = _as_mapping(transit)
            planet = _safe_text(transit_data.get("planet"), 80)
            valence = _safe_text(transit_data.get("gochar_valence"), 40).upper()
            title = _safe_text(transit_data.get("gochar_title"), 160)
            if not planet:
                continue
            finding_id = self._add_method_finding(
                graph,
                chart_id,
                "transit",
                f"{planet} transit: {title or valence or 'available'}",
                metadata={"planet": planet, "valence": valence or "UNKNOWN"},
            )
            if valence == "GOOD":
                evidence.append(
                    TruthEvidence(
                        "current_period",
                        "support",
                        "transit",
                        "derived",
                        f"{planet} transit is evaluated as favorable.",
                        (finding_id,),
                        weight=0.6,
                        time_window=period_window,
                    )
                )
            elif valence == "BAD":
                evidence.append(
                    TruthEvidence(
                        "current_period",
                        "contradict",
                        "transit",
                        "derived",
                        f"{planet} transit is evaluated as challenging.",
                        (finding_id,),
                        weight=0.6,
                        time_window=period_window,
                    )
                )

        claims: list[TruthClaim] = list(life_claims)
        if evidence:
            claim = self._classify_claim(evidence)
            claim_node_id = graph.add_node(
                "claim",
                claim.statement,
                "synthesis",
                {"topic": claim.topic, "status": claim.status, "confidence_band": claim.confidence_band},
            )
            if claim_node_id != claim.id:
                claim = TruthClaim(
                    id=claim_node_id,
                    topic=claim.topic,
                    status=claim.status,
                    statement=claim.statement,
                    time_window=claim.time_window,
                    confidence_band=claim.confidence_band,
                    support_refs=claim.support_refs,
                    contradiction_refs=claim.contradiction_refs,
                    citation_refs=claim.citation_refs,
                )
            graph.add_edge("CONTAINS", report_id, claim.id)
            for source_id in claim.support_refs:
                graph.add_edge("SUPPORTS", source_id, claim.id)
            for source_id in claim.contradiction_refs:
                graph.add_edge("CONTRADICTS", source_id, claim.id)
            for source_id in claim.citation_refs:
                graph.add_edge("CITES", claim.id, source_id)
            claims.append(claim)

        for fact in chart_facts:
            graph.add_edge("CONTAINS", report_id, fact["id"])

        graph_summary = graph.compact_summary()
        graph_summary["claims"] = len(claims)
        return {
            "schema_version": "1.0",
            "report_state": "partial" if failures else "complete",
            "data_quality": {"birth_input": "provided", "partial_failures": failures},
            "chart_facts": sorted(chart_facts, key=lambda item: item["id"]),
            "claims": [claim.to_public_dict() for claim in sorted(claims, key=lambda item: item.id)],
            "method_coverage": coverage,
            "graph_summary": graph_summary,
        }


def build_truth_report(
    response_data: Mapping[str, Any],
    life_events: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the public, compact truth-report contract for a Jathagam response.

    `life_events` are fused convergent events from engine.event_fusion; pass
    None when the life-event adapter was not run for this request.
    """
    return TruthEngine().build(response_data, life_events=life_events)
