"""Tests for the divide-and-conquer category engines."""
from engine.chart import compute_chart
from engine.engines.orchestrator import run_all, REGISTRY, categories
from engine.engines import CategoryReport, Prediction, Citation


def _manoj():
    return compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                         place="Coimbatore", name="Manoj Kumar Gounder")


def test_registry_has_all_categories():
    cats = categories()
    expected = {"personality", "education", "career", "marriage",
                 "children", "wealth", "health", "foreign", "family",
                 "spirituality", "longevity", "yogas", "afflictions",
                 "timeline", "remedies"}
    assert set(cats) == expected, f"Missing categories: {expected - set(cats)}"


def test_orchestrator_runs_all():
    reports = run_all(_manoj())
    assert len(reports) == len(REGISTRY)
    for r in reports:
        assert isinstance(r, CategoryReport)
        # No engine should be empty (unless flagged in notes)
        if not r.notes:
            assert r.predictions, f"Engine '{r.category}' returned empty predictions"


def test_only_filter_works():
    reports = run_all(_manoj(), only=("career", "marriage"))
    cats = [r.category for r in reports]
    assert cats == ["career", "marriage"]


def test_predictions_have_required_fields():
    reports = run_all(_manoj())
    for r in reports:
        for p in r.predictions:
            assert p.key
            assert p.label
            assert p.confidence in ("HIGH", "MEDIUM", "LOW")
            assert p.chart_evidence is not None


def test_career_engine_returns_industries():
    from engine.engines.career import CareerEngine
    r = CareerEngine().predict(_manoj())
    keys = {p.key for p in r.predictions}
    assert "industry_primary" in keys
    assert "career_peak_window" in keys


def test_marriage_engine_returns_age_window():
    from engine.engines.marriage import MarriageEngine
    r = MarriageEngine().predict(_manoj())
    keys = {p.key for p in r.predictions}
    assert "age_window" in keys
    assert "spouse_profile" in keys


def test_health_engine_returns_either_pattern_or_no_major():
    from engine.engines.health import HealthEngine
    r = HealthEngine().predict(_manoj())
    assert r.predictions  # always something
