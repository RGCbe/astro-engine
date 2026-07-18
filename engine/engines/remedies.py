"""Remedies engine — verbatim citations per affliction."""
from __future__ import annotations

from . import Engine, CategoryReport, Prediction, Citation


class RemediesEngine(Engine):
    category = "remedies"
    title = "Remedies (Verbatim Classical)"

    def predict(self, chart) -> CategoryReport:
        from .. import remedies, remedies_verbatim
        plan = remedies.remedies_for_chart(chart)
        preds: list[Prediction] = []
        for entry in plan["afflictions_with_remedies"][:10]:
            a = entry["affliction"]
            affected = a.get("affected") or []
            planets = [x for x in affected
                       if x in ("Sun", "Moon", "Mars", "Mercury",
                                 "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")]
            verbatim = remedies_verbatim.remedies_for_affliction_code(
                a["code"], planets)
            cites = [Citation(book=v.book, verse_id=v.verse_id, text=v.text)
                     for v in verbatim[:3]]
            preds.append(Prediction(
                key=f"remedy.{a['code']}",
                label=f"For: {a['name'].split('—')[0].strip()}",
                value={
                    "remedies": [r["action"] for r in entry["remedies"]],
                    "verbatim": [{"book": c.book, "verse_id": c.verse_id,
                                   "text": c.text[:300]} for c in cites],
                },
                confidence="HIGH",
                chart_evidence=a["evidence"],
                citations=cites,
            ))
        return CategoryReport(self.category, self.title, predictions=preds)
