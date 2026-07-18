"""Yogas engine — surfaces all detected blessings + Nabhasa + extended."""
from __future__ import annotations

from . import Engine, CategoryReport, Prediction, Citation


class YogasEngine(Engine):
    category = "yogas"
    title = "Yogas & Special Configurations"

    def predict(self, chart) -> CategoryReport:
        from .. import blessings, yogas_extended
        preds: list[Prediction] = []
        try:
            for b in blessings.detect_all(chart):
                preds.append(Prediction(
                    key=f"blessing.{b.code if hasattr(b, 'code') else b.name}",
                    label=b.name,
                    value=b.description,
                    confidence={"SUPREME": "HIGH", "STRONG": "HIGH",
                                "MODERATE": "MEDIUM",
                                "LATENT": "LOW"}.get(b.strength, "MEDIUM"),
                    chart_evidence=getattr(b, "evidence", ""),
                    citations=[Citation(book=getattr(b, "classical_source", "BPHS"))],
                ))
        except Exception:
            pass
        try:
            for y in yogas_extended.detect_all_extended(chart):
                if y.valence != "GOOD":
                    continue
                preds.append(Prediction(
                    key=f"yoga.{y.code}",
                    label=y.name,
                    value=y.description,
                    confidence={"SUPREME": "HIGH", "STRONG": "HIGH",
                                "MODERATE": "MEDIUM",
                                "LATENT": "LOW"}.get(y.strength, "MEDIUM"),
                    chart_evidence=y.evidence,
                    citations=[Citation(book=y.classical_source)],
                ))
        except Exception:
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
