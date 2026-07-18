"""
Orchestrator — runs every category engine and returns a unified
list of CategoryReports for a given chart.

Usage:
    reports = run_all(chart)
    # or filter:
    reports = run_all(chart, only=("career", "marriage"))
"""
from __future__ import annotations

from . import Engine, CategoryReport
from .personality import PersonalityEngine
from .education import EducationEngine
from .career import CareerEngine
from .marriage import MarriageEngine
from .children import ChildrenEngine
from .wealth import WealthEngine
from .health import HealthEngine
from .foreign import ForeignEngine
from .family import FamilyEngine
from .spirituality import SpiritualityEngine
from .longevity import LongevityEngine
from .yogas import YogasEngine
from .afflictions import AfflictionsEngine
from .timeline import TimelineEngine
from .remedies import RemediesEngine


# Canonical engine registry — order is the natural reading order
REGISTRY: list[Engine] = [
    PersonalityEngine(),
    EducationEngine(),
    CareerEngine(),
    MarriageEngine(),
    ChildrenEngine(),
    WealthEngine(),
    HealthEngine(),
    ForeignEngine(),
    FamilyEngine(),
    SpiritualityEngine(),
    LongevityEngine(),
    YogasEngine(),
    AfflictionsEngine(),
    TimelineEngine(),
    RemediesEngine(),
]


def run_all(chart, only: tuple[str, ...] | None = None
            ) -> list[CategoryReport]:
    """Run every engine (or subset) and return ordered CategoryReports."""
    out: list[CategoryReport] = []
    for eng in REGISTRY:
        if only and eng.category not in only:
            continue
        try:
            out.append(eng.predict(chart))
        except Exception as e:
            out.append(CategoryReport(
                category=eng.category,
                title=eng.title,
                notes=[f"Engine error: {e}"],
            ))
    return out


def categories() -> list[str]:
    """All registered engine category-ids."""
    return [e.category for e in REGISTRY]
