"""Afflictions / doshas engine."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import Engine, CategoryReport, Prediction, Citation


class AfflictionsEngine(Engine):
    category = "afflictions"
    title = "Afflictions & Doshas"

    def predict(self, chart) -> CategoryReport:
        from .. import afflictions
        preds: list[Prediction] = []
        for a in afflictions.detect_all(chart):
            preds.append(Prediction(
                key=f"affliction.{a.code}",
                label=a.name,
                value=a.description,
                confidence={"CRITICAL": "HIGH", "HIGH": "HIGH",
                             "MODERATE": "MEDIUM",
                             "LOW": "LOW"}.get(a.severity, "MEDIUM"),
                chart_evidence=a.evidence,
                citations=[Citation(book=a.classical_source)],
            ))
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
