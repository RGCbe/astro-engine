"""Family / parents / siblings engine."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import Engine, CategoryReport, Prediction, Citation, planet_house


class FamilyEngine(Engine):
    category = "family"
    title = "Family — Parents, Siblings, Home"

    def predict(self, chart) -> CategoryReport:
        h_sun = planet_house(chart, "Sun")
        h_moon = planet_house(chart, "Moon")
        h_mars = planet_house(chart, "Mars")

        preds = [
            Prediction(
                key="father_status",
                label="Father — status & relationship",
                value=("strong / elevated" if h_sun in (1, 9, 10)
                       else "moderate or strained"),
                confidence="MEDIUM",
                chart_evidence=f"Sun (father karaka) in H{h_sun}",
                citations=[Citation(book="BPHS Ch.30"), Citation(book="Phaladeepika Ch.13")],
            ),
            Prediction(
                key="mother_status",
                label="Mother — status & relationship",
                value=("strong / supportive" if h_moon in (1, 4, 9, 10)
                       else "moderate"),
                confidence="MEDIUM",
                chart_evidence=f"Moon (mother karaka) in H{h_moon}",
            ),
            Prediction(
                key="sibling_relationship",
                label="Sibling — relationship",
                value=("close" if h_mars in (3, 11) else "distant or rival"),
                confidence="MEDIUM",
                chart_evidence=f"Mars (siblings karaka) in H{h_mars}",
            ),
            Prediction(
                key="inheritance",
                label="Inheritance prospects",
                value=("favoured" if planet_house(chart, "Jupiter") in (2, 4, 8, 11)
                       else "limited"),
                confidence="MEDIUM",
                chart_evidence=f"Jupiter in H{planet_house(chart, 'Jupiter')}",
            ),
            Prediction(
                key="family_disputes",
                label="Family-dispute tendency",
                value=("elevated" if (h_mars in (2, 4) or
                                       planet_house(chart, "Rahu") in (2, 4))
                       else "low"),
                confidence="MEDIUM",
                chart_evidence="2nd / 4th house malefic activity",
            ),
        ]
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
