"""Spirituality / dharma engine."""
from __future__ import annotations

from ..book_rules import predictions_for as _book_preds
from ..deep_rules import predictions_for as _deep_preds

from . import Engine, CategoryReport, Prediction, Citation, planet_house, planet_sign


PATH_BY_KETU_SIGN = {
    "Aries":      "warrior path — yoga, kundalini, action-meditation",
    "Taurus":     "devotional path — bhakti, ritual, deity worship",
    "Gemini":     "study path — scriptural learning, mantra",
    "Cancer":     "devotional motherhood path — Devi worship, care of elders",
    "Leo":        "leadership/Sun path — Surya namaskar, royal-deity worship",
    "Virgo":      "service path — karma yoga, healing, ayurveda",
    "Libra":      "balance path — partnership, harmony, art-as-prayer",
    "Scorpio":    "transformational/tantric path — dark-night, occult",
    "Sagittarius": "jnana path — philosophy, scripture, teaching",
    "Capricorn":  "discipline path — long fasts, austerity, structured practice",
    "Aquarius":   "service-to-collective path — humanitarian, group-yoga",
    "Pisces":     "mystical-devotional path — bhakti, music, surrender",
}


class SpiritualityEngine(Engine):
    category = "spirituality"
    title = "Spirituality & Dharma"

    def predict(self, chart) -> CategoryReport:
        h_ketu = planet_house(chart, "Ketu")
        ketu_sign = planet_sign(chart, "Ketu")
        h_jup = planet_house(chart, "Jupiter")
        h_sat = planet_house(chart, "Saturn")
        preds = [
            Prediction(
                key="path_type",
                label="Spiritual path lean",
                value=PATH_BY_KETU_SIGN.get(ketu_sign, "general dharmic path"),
                confidence="MEDIUM",
                chart_evidence=f"Ketu (past-life skill karaka) in {ketu_sign}, H{h_ketu}",
                citations=[Citation(book="Phaladeepika Ch.6"), Citation(book="BPHS Ch.36")],
            ),
            Prediction(
                key="guru_relationship",
                label="Guru / teacher bond",
                value=("favoured" if h_jup in (5, 9) else "needs cultivation"),
                confidence="MEDIUM",
                chart_evidence=f"Jupiter in H{h_jup}",
            ),
            Prediction(
                key="religious_participation",
                label="Religious participation tendency",
                value=("regular" if h_jup in (1, 4, 9, 10) else "occasional"),
                confidence="MEDIUM",
                chart_evidence=f"Jupiter in H{h_jup}",
            ),
            Prediction(
                key="mantra_inclination",
                label="Mantra / sadhana inclination",
                value=("strong" if h_ketu in (8, 12) else "moderate"),
                confidence="MEDIUM",
                chart_evidence=f"Ketu in H{h_ketu}",
            ),
        ]
        # ── Append matched classical book-rules ──
        try:
            preds.extend(_book_preds(chart, self.category, max_per_category=6))
            preds.extend(_deep_preds(chart, self.category, max_per_category=4))
        except Exception as _e:  # never break the report
            pass
        return CategoryReport(self.category, self.title, predictions=preds)
