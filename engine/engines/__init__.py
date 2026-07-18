"""
Divide-and-conquer prediction engines.

Each life-domain has its own dedicated mini-engine that owns:
    - its scope (which chart features it consumes)
    - its rule corpus (which filtered slice of the master rules it uses)
    - its prediction schema (uniform across all engines)
    - its confidence/applicability gate
    - its citations

Engines are composed by `engine.engines.orchestrator.run_all(chart)` which
returns a list of CategoryReport objects, one per category.

This replaces the previous monolithic `client_report` rule selection
logic — every engine is independently testable and improvable.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Citation:
    book: str
    verse_id: str = ""
    text: str = ""

    def cite(self) -> str:
        if self.verse_id:
            return f"{self.book} {self.verse_id}"
        return self.book


@dataclass
class Prediction:
    """One concrete prediction within a category."""
    key: str                    # e.g. "primary_field" / "marriage_window"
    label: str                  # human-readable label
    value: Any                  # primitive or list/dict
    confidence: str             # HIGH / MEDIUM / LOW
    chart_evidence: str = ""    # chart-feature-based reason
    citations: list[Citation] = field(default_factory=list)


@dataclass
class CategoryReport:
    category: str               # canonical category id
    title: str                  # display name
    predictions: list[Prediction] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class Engine(ABC):
    category: str
    title: str

    @abstractmethod
    def predict(self, chart) -> CategoryReport:
        ...

    def __call__(self, chart) -> CategoryReport:
        return self.predict(chart)


# ─── Helper functions every engine can use ────────────────────────────────
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORD = {0: "Mars", 1: "Venus", 2: "Mercury", 3: "Moon", 4: "Sun",
             5: "Mercury", 6: "Venus", 7: "Mars", 8: "Jupiter",
             9: "Saturn", 10: "Saturn", 11: "Jupiter"}


def planet_house(chart, planet: str) -> int:
    lon = chart.positions.get(planet)
    if lon is None:
        return 0
    return ((int(lon // 30) - int(chart.lagna_lon // 30)) % 12) + 1


def planet_sign(chart, planet: str) -> str:
    lon = chart.positions.get(planet)
    if lon is None:
        return ""
    return SIGNS[int(lon // 30)]


def lord_of_house(chart, h: int) -> str:
    return SIGN_LORD[(int(chart.lagna_lon // 30) + h - 1) % 12]
