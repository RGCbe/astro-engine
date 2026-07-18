"""Timeline engine — chapter-style mahadasha walk + antardasha events."""
from __future__ import annotations

from . import Engine, CategoryReport, Prediction, Citation


class TimelineEngine(Engine):
    category = "timeline"
    title = "Life Timeline (Vimshottari Maha Dasha)"

    def predict(self, chart) -> CategoryReport:
        from .. import chapters as ch_mod
        chapters = ch_mod.build_chapters(chart)
        preds: list[Prediction] = []
        for ch in chapters:
            preds.append(Prediction(
                key=f"chapter.{ch.n}.{ch.planet}",
                label=f"Chapter {ch.n}: {ch.planet} MD ({ch.year_start}–{ch.year_end} · age {ch.age_start}–{ch.age_end})",
                value={
                    "theme": ch.theme,
                    "intro": ch.intro,
                    "expect": ch.expect,
                    "watch": ch.watch,
                    "antardasha_detail": ch.antardasha_detail,
                    "is_current": ch.is_current,
                },
                confidence="HIGH" if ch.is_current else "MEDIUM",
                chart_evidence=f"{ch.planet} MD via Vimshottari nakshatra-lord",
                citations=[Citation(book="BPHS Ch.46 (Vimshottari)")],
            ))
        return CategoryReport(self.category, self.title, predictions=preds)
