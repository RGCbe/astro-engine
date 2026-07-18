"""Longevity engine."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import Engine, CategoryReport, Prediction, Citation, planet_house


class LongevityEngine(Engine):
    category = "longevity"
    title = "Longevity"

    def predict(self, chart) -> CategoryReport:
        from .. import life_domains
        l = life_domains.predict_longevity(chart)
        preds = [
            Prediction(
                key="band",
                label="Longevity band (Bala/Madhya/Purna yoga)",
                value=l["band"],
                confidence="MEDIUM",
                chart_evidence="; ".join(l["reasons"]) or "standard placement",
                citations=[Citation(book="BPHS Ch.69"), Citation(book="Phaladeepika Ch.16")],
            ),
        ]
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
