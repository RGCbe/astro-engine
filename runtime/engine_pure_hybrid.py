"""
Astrological Hybridization Bridge — Conjoining Classical & Modern Engines.
Runs both the modern 314-category declarative engine and the pure classical engine,
cross-verifies timeline overlaps within a 180-day window, and injects scriptural proofs.
"""
import datetime as dt
import sys
from pathlib import Path

_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))

from category_engine import category_engine_instance
from pure_classical_engine import pure_classical_engine_instance

# Setup overlapping category aliases for broad alignment
CATEGORY_ALIASES = {
    "career": {"career", "career_breakthrough", "education"},
    "career_breakthrough": {"career", "career_breakthrough", "wealth_peak", "education"},
    "wealth_peak": {"wealth", "wealth_peak", "property"},
    "wealth_loss": {"wealth", "wealth_loss"},
    "marriage": {"marriage", "relationship_phase"},
    "health_self": {"health", "health_self", "self_accident"},
}

class AstrologicalHybridEngine:
    def __init__(self):
        pass

    def scan_hybrid_lifetime(self, chart, year_from, year_to, sample_days=14, min_severity=2):
        """Scans both engines and performs hybrid conjoined cross-verification."""
        # 1. Run Modern Declarative Engine
        modern_events = category_engine_instance.scan_lifetime(chart, year_from, year_to, sample_days, min_severity)
        modern_bands = category_engine_instance.collapse_consecutive(modern_events)

        # 2. Run Pure Classical Scriptural Engine
        classical_events = pure_classical_engine_instance.scan_lifetime(chart, year_from, year_to, sample_days, min_severity)
        classical_bands = pure_classical_engine_instance.collapse_consecutive(classical_events)

        # 3. Hybridize: Align and inject classical proofs into modern bands
        for mod in modern_bands:
            mod_cat = mod.get("category", "")
            mod_start = dt.datetime.strptime(mod["window_start"], "%Y-%m-%d")
            mod_end = dt.datetime.strptime(mod["window_end"], "%Y-%m-%d")

            # Look for a matching classical band
            match_class = None
            for cl in classical_bands:
                cl_cat = cl.get("category", "")
                
                # Normalize category IDs by stripping the "event_" prefix
                norm_mod = mod_cat[6:] if mod_cat.startswith("event_") else mod_cat
                norm_cl = cl_cat[6:] if cl_cat.startswith("event_") else cl_cat

                # Check semantic alignment
                semantic_match = (norm_mod == norm_cl or 
                                  norm_cl in CATEGORY_ALIASES.get(norm_mod, set()) or
                                  norm_mod in CATEGORY_ALIASES.get(norm_cl, set()))
                if not semantic_match:
                    continue

                cl_start = dt.datetime.strptime(cl["window_start"], "%Y-%m-%d")
                cl_end = dt.datetime.strptime(cl["window_end"], "%Y-%m-%d")

                # Check time overlap with a lenient ±180d window tolerance
                buffer = dt.timedelta(days=180)
                time_match = not (mod_end + buffer < cl_start or cl_end + buffer < mod_start)
                
                if time_match:
                    match_class = cl
                    break

            # If cross-verified by scripture, inject the golden badges
            if match_class:
                mod["verified_classical"] = True
                
                # Boost severity (max 5)
                original_sev = mod["severity"]
                mod["severity"] = min(5, original_sev + 1)
                
                # Inject citations & verbatim scriptural prose
                mod["classical_title"] = match_class.get("classical_title", "")
                mod["classical_prose"] = match_class.get("classical_prose", "")
                mod["scripture_source"] = match_class.get("scripture_source", "")
                mod["citation"] = match_class.get("citation", "")
                mod["tradition"] = match_class.get("tradition", "")
                
                # Enrich why
                mod["why"].append(
                    f"[CLASSICAL PROOF] Verifiably confirmed by {match_class['scripture_source']} ({match_class['citation']}) - "
                    f"\"{match_class['classical_title']}\" (Boosted severity from {original_sev} to {mod['severity']})"
                )

        return {
            "hybrid_bands": modern_bands,
            "classical_only_bands": [cl for cl in classical_bands if not any(
                cl.get("classical_title") == m.get("classical_title") for m in modern_bands if m.get("verified_classical")
            )]
        }

hybrid_engine_instance = AstrologicalHybridEngine()
