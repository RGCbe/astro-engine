"""Personality / temperament engine."""
from __future__ import annotations

from . import (Engine, CategoryReport, Prediction, Citation,
                planet_house, planet_sign)


SIGN_TEMPERAMENT = {
    "Aries": "fiery, direct, courageous, quick to act",
    "Taurus": "steady, sensual, patient, materially-grounded",
    "Gemini": "quick-minded, communicative, restless",
    "Cancer": "emotional, nurturing, deeply attached to home",
    "Leo": "regal, generous, dignified, recognition-seeking",
    "Virgo": "analytical, careful, service-oriented, perfectionist",
    "Libra": "diplomatic, aesthetic, partnership-driven",
    "Scorpio": "intense, secretive, transformational, fearless",
    "Sagittarius": "philosophical, ethical, expansive, meaning-seeking",
    "Capricorn": "ambitious, disciplined, slow-burn, structure-builder",
    "Aquarius": "principled, unconventional, networked, future-leaning",
    "Pisces": "compassionate, dreamy, spiritually attuned, porous",
}


class PersonalityEngine(Engine):
    category = "personality"
    title = "Personality & Temperament"

    def predict(self, chart) -> CategoryReport:
        from .. import life_domains  # reuse existing data
        psych = life_domains.predict_psychology(chart)
        sign = planet_sign(chart, chart.lagna_lord)  # lord's sign colours nature
        lagna_sign_name = ["Aries", "Taurus", "Gemini", "Cancer", "Leo",
                            "Virgo", "Libra", "Scorpio", "Sagittarius",
                            "Capricorn", "Aquarius", "Pisces"][int(chart.lagna_lon // 30)]
        moon_sign = psych["moon_sign"]
        moon_house = psych["moon_house"]
        moon_nak = psych["moon_nakshatra"]

        preds = [
            Prediction(
                key="lagna_archetype",
                label="Outer presentation (the room you walk into first)",
                value=SIGN_TEMPERAMENT.get(lagna_sign_name, "distinctive"),
                confidence="HIGH",
                chart_evidence=f"Lagna sign = {lagna_sign_name}, ruled by {chart.lagna_lord}",
                citations=[Citation(book="BPHS Ch.6"),
                            Citation(book="Phaladeepika Ch.3")],
            ),
            Prediction(
                key="moon_temperament",
                label="Inner emotional grain (mind / mood)",
                value=SIGN_TEMPERAMENT.get(moon_sign, "distinctive"),
                confidence="HIGH",
                chart_evidence=f"Moon in {moon_sign}, House {moon_house}, "
                               f"nakshatra {moon_nak}",
                citations=[Citation(book="BPHS Ch.7"),
                            Citation(book="Saravali Ch.18")],
            ),
        ]
        return CategoryReport(
            category=self.category, title=self.title, predictions=preds,
        )
