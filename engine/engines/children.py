"""Children / progeny engine."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import (Engine, CategoryReport, Prediction, Citation,
                planet_house, planet_sign, lord_of_house, SIGNS)


class ChildrenEngine(Engine):
    category = "children"
    title = "Children & Progeny"

    def predict(self, chart) -> CategoryReport:
        from .. import life_domains
        c = life_domains.predict_children(chart)
        h_jup = planet_house(chart, "Jupiter")

        preds = [
            Prediction(
                key="count_lean",
                label="Family-size lean",
                value=c["count_lean"],
                confidence="MEDIUM",
                chart_evidence=f"5th lord {c['5th_lord']} in H{c['5th_lord_house']}",
                citations=[Citation(book="BPHS Ch.79"), Citation(book="Phaladeepika Ch.10")],
            ),
            Prediction(
                key="gender_lean",
                label="Gender tendency (classical, weak)",
                value=c["gender_lean"],
                confidence="LOW",
                chart_evidence=f"5th sign = {c['5th_sign']}",
            ),
            Prediction(
                key="children_success",
                label="Children's success potential",
                value=("favoured" if h_jup in (1, 5, 9) else "moderate"),
                confidence="MEDIUM",
                chart_evidence=f"Jupiter in H{h_jup}",
            ),
            Prediction(
                key="fertility_blessing",
                label="Fertility blessing",
                value=("strong" if (c['5th_lord'] == 'Jupiter' or h_jup in (1, 5, 9))
                       else "moderate"),
                confidence="MEDIUM",
                chart_evidence=f"Jupiter (children-karaka) in H{h_jup}",
            ),
        ]
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
