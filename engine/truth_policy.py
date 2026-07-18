"""
Truth policy for client-facing Astro engine output.

Separates:
  - MECHANICAL: Swiss Ephemeris positions, dasha math (verifiable)
  - CITED: Corpus passages with source_label (traceable to books)
  - DERIVED: Rule engines, yogas, shadbala (classical methods, not fortune guarantees)
  - SYNTHESIS: Plain-language summaries (opinionated aggregation, not prophecy)
  - RESEARCH: scratch/* celebrity tuning - must never ship in API responses
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

POLICY_VERSION = "1.0"

RESEARCH_ONLY_MARKERS = (
    "scratch/astro_numerology_weights.json",
    "scratch/optimize_",
    "scratch/vijay_",
    "runtime/_battle_vijay.py",
)

CLIENT_DISCLAIMER = (
    "This report combines calculated chart data with classical text citations. "
    "It describes tendencies from traditional Jyotish rules - not guaranteed future events. "
    "Verify birth time and place; wrong birth data produces wrong charts."
)

MECHANICAL_FIELDS = (
    "all_planet_positions",
    "lagnam",
    "janma_rasi",
    "janma_nakshatra",
    "panchangam",
    "current_dasha",
    "current_antardasha",
    "current_pratyantar_dasha",
    "dasha_schedule",
    "dasha_start",
    "dasha_end",
    "truth_report.chart_facts",
)

CITED_FIELDS = (
    "house_predictions.corpus_rules",
    "dasha_corpus_rules",
    "detected_yogas.corpus_evidence",
)

SYNTHESIS_FIELDS = (
    "synthesis",
    "advanced_reading_html",
    "battle_results",
    "truth_report.claims",
)


def build_client_truth_block(
    *,
    birth_place_note: str = "IST (UTC+5:30) used for time conversion unless tz provided on endpoint",
    corpus_books: int = 0,
    corpus_rules: int = 0,
    modules_failed: list[str] | None = None,
) -> dict:
    """Attach to every major API payload so clients know what they are reading."""
    return {
        "policy_version": POLICY_VERSION,
        "disclaimer": CLIENT_DISCLAIMER,
        "layers": {
            "mechanical": {
                "description": "Planet longitudes, houses, dasha periods from Swiss Ephemeris (Lahiri ayanamsa).",
                "fields": list(MECHANICAL_FIELDS),
                "verifiable": True,
            },
            "cited": {
                "description": "Verbatim or excerpted passages from indexed classical books with source labels.",
                "fields": list(CITED_FIELDS),
                "verifiable": "Check source_label against your Books library",
            },
            "derived": {
                "description": "Yogas, shadbala, ashtakavarga, KP, gochar - computed by rule code, not AI invention.",
                "verifiable": "Re-run engine with same birth data",
            },
            "synthesis": {
                "description": "Short summaries and book-battle consensus - aggregated language, not single-shastra law.",
                "fields": list(SYNTHESIS_FIELDS),
                "verifiable": False,
            },
        },
        "not_guaranteed": [
            "Exact date of marriage, job offer, or box office result",
            "100% accuracy on any celebrity backtest",
            "Consensus percent in book-battle as probability of an event",
            "truth_report.claims as future outcomes - they are evidence-weighted "
            "synthesis; only truth_report.chart_facts are mechanical",
        ],
        "excluded_from_production": list(RESEARCH_ONLY_MARKERS),
        "computation": {
            "ephemeris": "Swiss Ephemeris",
            "ayanamsa": "Lahiri (SIDM_LAHIRI)",
            "timezone_note": birth_place_note,
            "corpus_books_loaded": corpus_books,
            "corpus_rules_indexed": corpus_rules,
        },
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "partial_failures": modules_failed or [],
    }


def assert_production_clean():
    """Call at startup: ensure research weight files are not wired into live app."""
    root = os.environ.get("ATRO_ROOT", os.path.dirname(os.path.dirname(__file__)))
    weight_path = os.path.join(root, "scratch", "astro_numerology_weights.json")
    return {
        "research_weights_on_disk": os.path.isfile(weight_path),
        "research_weights_allowed_in_api": False,
        "policy_version": POLICY_VERSION,
    }
