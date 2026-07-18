"""Wealth / finance engine."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import (Engine, CategoryReport, Prediction, Citation,
                planet_house, planet_sign, lord_of_house, SIGNS)


class WealthEngine(Engine):
    category = "wealth"
    title = "Wealth & Finance"

    def predict(self, chart) -> CategoryReport:
        from .. import life_domains
        w = life_domains.predict_wealth(chart)
        h_jup = planet_house(chart, "Jupiter")
        h_mars = planet_house(chart, "Mars")
        h_sun = planet_house(chart, "Sun")
        h_sat = planet_house(chart, "Saturn")
        sign2 = SIGNS[(int(chart.lagna_lon // 30) + 1) % 12]
        sign11 = SIGNS[(int(chart.lagna_lon // 30) + 10) % 12]
        sat_sign = planet_sign(chart, "Saturn")

        preds = [
            Prediction(
                key="primary_source",
                label="Primary wealth-channel (savings axis)",
                value=w["sources_primary"],
                confidence="MEDIUM",
                chart_evidence=f"2nd sign = {sign2}, 2nd lord {w['2nd_lord_house']}",
                citations=[Citation(book="BPHS Ch.20"), Citation(book="Phaladeepika Ch.14")],
            ),
            Prediction(
                key="gain_channel",
                label="Gains / income channel",
                value=w["sources_gains"],
                confidence="MEDIUM",
                chart_evidence=f"11th sign = {sign11}",
            ),
            Prediction(
                key="peak_years",
                label="Wealth peak windows",
                value="Jupiter / Venus / Mercury mahadashas",
                confidence="HIGH",
                chart_evidence=f"Jupiter in H{h_jup}",
            ),
            Prediction(
                key="asset_preference",
                label="Asset preference",
                value=("real estate" if h_mars == 4
                       else ("gold/jewellery" if h_sun in (2, 4)
                             else "diversified financial")),
                confidence="MEDIUM",
                chart_evidence=f"Mars H{h_mars}, Sun H{h_sun}",
            ),
            Prediction(
                key="saver_vs_spender",
                label="Saver vs spender",
                value=("saver" if sat_sign in ("Capricorn", "Aquarius", "Taurus")
                       else "balanced"),
                confidence="MEDIUM",
                chart_evidence=f"Saturn in {sat_sign}",
            ),
            Prediction(
                key="debt_tendency",
                label="Loan / debt tendency",
                value=("elevated" if (h_sat == 6 or planet_house(chart, "Rahu") == 6)
                       else "moderate"),
                confidence="MEDIUM",
                chart_evidence="6th-house occupants",
            ),
            Prediction(
                key="property",
                label="Property / real-estate",
                value=("yes" if (h_mars == 4 or h_sat == 4) else "moderate"),
                confidence="MEDIUM",
                chart_evidence="4H occupants",
            ),
        ]
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
