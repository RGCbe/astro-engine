"""Tests for engine.feedback."""
import json
import os
import tempfile
from unittest.mock import patch

from engine.chart import compute_chart


def test_feedback_round_trip():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmppath = f.name
    try:
        with patch("engine.feedback.DATA_FILE", __import__("pathlib").Path(tmppath)):
            from engine import feedback
            c = compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                              place="Coimbatore")
            feedback.record_feedback(c, "career.industry_primary", "career",
                                     "Career was IT not engineering", False)
            feedback.record_feedback(c, "marriage.window", "marriage",
                                     "Married at 28 — fits prediction", True)
            s = feedback.summary()
            assert s["total_feedback"] == 2
            assert s["by_module"]["career"]["wrong"] == 1
            assert s["by_module"]["marriage"]["right"] == 1
            # Weights should now reflect feedback
            w = feedback.get_module_weights()
            assert w["career"] < 1.0   # demoted
            assert w["marriage"] > 1.0   # promoted
            # Apply weight
            assert feedback.apply_module_weight("career", 1.0) < 1.0
            assert feedback.apply_module_weight("marriage", 1.0) > 1.0
    finally:
        os.unlink(tmppath)


def test_default_weights_are_all_one():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        tmppath = f.name
    os.unlink(tmppath)  # ensure file doesn't exist
    try:
        with patch("engine.feedback.DATA_FILE", __import__("pathlib").Path(tmppath)):
            from engine import feedback
            w = feedback.get_module_weights()
            assert all(v == 1.0 for v in w.values())
    finally:
        if os.path.exists(tmppath):
            os.unlink(tmppath)
