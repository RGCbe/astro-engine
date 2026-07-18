"""Tests for engine.chart_render."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.chart import compute_chart
from engine.chart_render import render_south, render_north


def _chart():
    return compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                         place="Coimbatore", name="Manoj")


def test_south_renders_svg():
    s = render_south(_chart())
    assert s.startswith("<svg")
    assert s.endswith("</svg>")
    # Should contain at least one planet symbol
    assert any(p in s for p in ("Su", "Mo", "Ma", "Me", "Ju", "Ve", "Sa"))


def test_north_renders_svg():
    s = render_north(_chart())
    assert s.startswith("<svg")
    assert s.endswith("</svg>")
    # Should contain Asc marker
    assert "As" in s


def test_localized_render_contains_translated_signs():
    s = render_south(_chart(), lang="hi")
    # Should contain Hindi sign characters (Devanagari)
    assert any(ch in s for ch in ("मे", "वृ", "मि", "धनु", "सिं"))
