"""Health & accident engine — wraps engine.accident."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import Engine, CategoryReport, Prediction, Citation, planet_house


class HealthEngine(Engine):
    category = "health"
    title = "Health & Accident Patterns"

    def predict(self, chart) -> CategoryReport:
        from .. import accident
        patterns = accident.detect_accident_patterns(chart)
        preds: list[Prediction] = []
        for p in patterns:
            preds.append(Prediction(
                key=f"pattern.{p.name.lower().replace(' ', '_')}",
                label=p.name,
                value={
                    "nature": p.nature,
                    "body_part": p.body_part,
                    "peak_dashas": p.peak_dashas,
                },
                confidence={"HIGH": "HIGH", "MEDIUM": "MEDIUM",
                            "LOW": "LOW"}.get(p.severity, "MEDIUM"),
                chart_evidence=p.evidence,
                citations=[Citation(book=p.classical_source)],
            ))
        if not preds:
            preds.append(Prediction(
                key="no_major_pattern",
                label="No major classical accident-pattern",
                value="The chart shows no peak-classical accident-signature. "
                      "Standard caution applies during malefic transits to "
                      "lagna or 8th house.",
                confidence="HIGH",
                chart_evidence="No malefic in dusthana (6/8/12); no Mars-Saturn afflictions",
            ))
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
