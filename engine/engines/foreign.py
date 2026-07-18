"""Foreign-travel / settlement engine."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import Engine, CategoryReport, Prediction, Citation, planet_house


class ForeignEngine(Engine):
    category = "foreign"
    title = "Foreign Travel & Settlement"

    def predict(self, chart) -> CategoryReport:
        from .. import life_domains
        f = life_domains.predict_foreign(chart)
        preds = [
            Prediction(
                key="likelihood",
                label="Foreign-settlement likelihood",
                value=f["likelihood"],
                confidence={"HIGH": "HIGH", "MEDIUM": "MEDIUM",
                            "LOW": "LOW"}.get(f["likelihood"], "MEDIUM"),
                chart_evidence="; ".join(f["reasons"]) or "no strong foreign indicator",
                citations=[Citation(book="BPHS Ch.32"), Citation(book="Lal Kitab Ch.5")],
            ),
            Prediction(
                key="direction_lean",
                label="Foreign-direction lean",
                value=f["direction"],
                confidence="LOW",
                chart_evidence=f"Rahu sign-element direction",
            ),
            Prediction(
                key="trigger_window",
                label="Most likely trigger window",
                value="Rahu mahadasha + 12th-lord activations",
                confidence="MEDIUM",
                chart_evidence=f"Rahu in H{f['rahu_house']}, Moon in H{f['moon_house']}",
            ),
        ]
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
