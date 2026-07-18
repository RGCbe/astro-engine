"""
Marriage outcomes ground-truth dataset.

689 historical marriages with documented outcomes — sourced from
VedAstro/HuggingFace/MarriageTrainingDataset (MIT license). Used to
empirically validate KutaScore and other compatibility predictions.

Outcome distribution:
    Happiness    359 (52.1%)
    Dissolution  299 (43.4%)
    Struggle      22  (3.2%)
    Tragedy        9  (1.3%)

Critical empirical finding: traditional KutaScore does NOT predict outcome.
    Happiness   mean=45.4  median=45
    Dissolution mean=46.6  median=45  ← virtually identical!
    Struggle    mean=34.8  (small n=22)
    Tragedy     mean=42.8  (small n=9)

This confirms a major motivation for our authority-weighted multi-rule
engine: any single classical metric is unreliable. Predictions must
combine many tier-weighted rules + transit/dasha context.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterator

DATA_PATH = Path(__file__).parent / "data" / "marriage_outcomes.csv"


@dataclass(frozen=True)
class MarriageRecord:
    partition_key: str
    outcome: str                 # Happiness | Dissolution | Struggle | Tragedy
    marriage_date: str           # MM/DD/YYYY
    male_id: str
    female_id: str
    kuta_score: int              # 0–95
    duration_years: int          # 0 = unknown
    children_count: int          # biological + adopted
    divorce_reason: str          # 'none' if no divorce
    embeddings: list[float]      # 8-dim feature vector from VedAstro


def _parse_int(s: str, default: int = 0) -> int:
    s = (s or "").strip()
    return int(s) if s.lstrip("-").isdigit() else default


def _parse_children(blob: str) -> int:
    try:
        d = json.loads(blob).get("children") or {}
        bio = _parse_int(d.get("biologicalCount", "0"))
        adopt = _parse_int(d.get("adoptedCount", "0"))
        return bio + adopt
    except (json.JSONDecodeError, AttributeError, TypeError):
        return 0


def _parse_divorce(blob: str) -> str:
    try:
        return json.loads(blob).get("divorce", {}).get("reason", "")
    except (json.JSONDecodeError, AttributeError, TypeError):
        return ""


def _parse_embeddings(blob: str) -> list[float]:
    try:
        return [float(x) for x in json.loads(blob)]
    except (json.JSONDecodeError, ValueError, TypeError):
        return []


@lru_cache(maxsize=1)
def all_records() -> tuple[MarriageRecord, ...]:
    out: list[MarriageRecord] = []
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out.append(MarriageRecord(
                partition_key=row.get("PartitionKey", ""),
                outcome=row.get("Outcome", ""),
                marriage_date=row.get("MarriageDate", ""),
                male_id=row.get("MalePersonId", ""),
                female_id=row.get("FemalePersonId", ""),
                kuta_score=_parse_int(row.get("KutaScore", ""), 0),
                duration_years=_parse_int(row.get("MarriageDuration", ""), 0),
                children_count=_parse_children(row.get("ChildrenData", "")),
                divorce_reason=_parse_divorce(row.get("DivorceData", "")),
                embeddings=_parse_embeddings(row.get("Embeddings", "[]")),
            ))
    return tuple(out)


def by_outcome(outcome: str) -> Iterator[MarriageRecord]:
    return (r for r in all_records() if r.outcome == outcome)


def kuta_outcome_correlation() -> dict:
    """Empirical: KutaScore mean by Outcome. Reveals that classical
    Kuta scoring is NOT predictive — see module docstring."""
    by = {}
    for r in all_records():
        by.setdefault(r.outcome, []).append(r.kuta_score)
    return {
        outcome: {
            "n": len(scores),
            "mean": round(sum(scores) / len(scores), 2),
            "median": sorted(scores)[len(scores) // 2],
            "min": min(scores),
            "max": max(scores),
        }
        for outcome, scores in by.items()
    }


def stats() -> dict:
    rs = all_records()
    durs = [r.duration_years for r in rs if r.duration_years > 0]
    return {
        "n_total": len(rs),
        "outcome_counts": {
            o: sum(1 for r in rs if r.outcome == o)
            for o in {"Happiness", "Dissolution", "Struggle", "Tragedy"}
        },
        "kuta_by_outcome": kuta_outcome_correlation(),
        "duration_known": len(durs),
        "duration_mean_years": round(sum(durs) / len(durs), 1) if durs else 0,
    }
