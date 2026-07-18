"""Education / subjects engine."""
from __future__ import annotations

from . import Engine, CategoryReport, Prediction, Citation, planet_house, planet_sign


class EducationEngine(Engine):
    category = "education"
    title = "Education & Subjects"

    def predict(self, chart) -> CategoryReport:
        from .. import education
        subjects = education.predict_subjects(chart, top_n=5)
        h_merc = planet_house(chart, "Mercury")
        h_jup = planet_house(chart, "Jupiter")
        preds: list[Prediction] = []
        if subjects:
            top = subjects[0]
            preds.append(Prediction(
                key="primary_field",
                label="Most likely natural subject area",
                value=top.field,
                confidence="HIGH" if top.score >= 4.0 else "MEDIUM",
                chart_evidence=f"D24 + 5L + Mercury convergence (score {top.score:.1f})",
                citations=[Citation(book="BPHS Ch.20 (D24)"),
                            Citation(book="Phaladeepika Ch.6")],
            ))
            for i, s in enumerate(subjects[1:5], start=2):
                preds.append(Prediction(
                    key=f"alt_field_{i}",
                    label=f"Alternative subject lean (rank {i})",
                    value=s.field,
                    confidence="MEDIUM" if s.score >= 2.5 else "LOW",
                    chart_evidence=f"score {s.score:.1f}",
                ))
        preds.append(Prediction(
            key="competitive_exams",
            label="Competitive exam success lean",
            value=("favoured" if h_merc in (1, 5, 9, 10, 11) else "needs effort"),
            confidence="MEDIUM",
            chart_evidence=f"Mercury in H{h_merc}",
        ))
        preds.append(Prediction(
            key="guru_bond",
            label="Teacher / guru bond",
            value=("strong" if h_jup in (1, 5, 9, 4, 10) else "moderate"),
            confidence="MEDIUM",
            chart_evidence=f"Jupiter in H{h_jup}",
        ))
        return CategoryReport(self.category, self.title, predictions=preds)
