"""Career engine — industry, role, peak windows."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import (Engine, CategoryReport, Prediction, Citation,
                planet_house, planet_sign, lord_of_house, SIGNS)


class CareerEngine(Engine):
    category = "career"
    title = "Career & Public Role"

    def predict(self, chart) -> CategoryReport:
        from .. import life_domains
        c = life_domains.predict_career(chart)
        sun_h = planet_house(chart, "Sun")
        sat_h = planet_house(chart, "Saturn")
        l10 = lord_of_house(chart, 10)
        h_l10 = planet_house(chart, l10)
        sign10 = SIGNS[(int(chart.lagna_lon // 30) + 9) % 12]

        # Strength of career axis
        bs = getattr(chart, "bala_summary", {}) or {}
        sun_strong = "Sun" in (bs.get("strongest") or [])
        sat_strong = "Saturn" in (bs.get("strongest") or [])
        confidence = "HIGH" if (sun_strong or sat_strong) else "MEDIUM"

        preds = [
            Prediction(
                key="industry_primary",
                label="Industries / fields the chart suits",
                value=c["industries_primary"],
                confidence=confidence,
                chart_evidence=f"10th sign = {sign10}, lord = {l10} in H{h_l10}",
                citations=[Citation(book="BPHS Ch.20"),
                            Citation(book="Phaladeepika Ch.6")],
            ),
            Prediction(
                key="industry_secondary",
                label="Secondary industries (via 10th-lord placement)",
                value=c["industries_secondary"],
                confidence="MEDIUM",
                chart_evidence=f"10th lord {l10} in {planet_sign(chart, l10)}",
            ),
            Prediction(
                key="self_employed_lean",
                label="Self-employed vs salaried lean",
                value=("self-employed lean" if sat_h in (3, 6, 11)
                       else "salaried/structured lean"),
                confidence="MEDIUM",
                chart_evidence=f"Saturn in H{sat_h}",
            ),
            Prediction(
                key="career_peak_window",
                label="Career peak window",
                value=("ages 30s-40s" if sat_h in (10, 11, 1)
                       else "ages 40s-50s"),
                confidence="MEDIUM",
                chart_evidence=f"Saturn in H{sat_h} (career-discipline karaka)",
            ),
            Prediction(
                key="authority_level",
                label="Authority over others",
                value=("strong" if sun_h in (1, 10) else "moderate"),
                confidence="HIGH" if sun_strong else "MEDIUM",
                chart_evidence=f"Sun in H{sun_h}",
                citations=[Citation(book="BPHS Ch.30")],
            ),
            Prediction(
                key="job_change_frequency",
                label="Job-change frequency lean",
                value=("frequent" if planet_house(chart, "Rahu") in (10, 11, 3)
                       else "stable"),
                confidence="MEDIUM",
                chart_evidence=f"Rahu in H{planet_house(chart, 'Rahu')}",
            ),
        ]
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
