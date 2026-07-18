"""Tests for engine.i18n."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.i18n import (
    LANGUAGES, translate, locale, localize_chart,
    SIGNS, GRAHAS, NAKSHATRAS, VERDICTS,
)


def test_all_languages_have_12_signs():
    for lang in LANGUAGES:
        assert len(SIGNS[lang]) == 12


def test_all_languages_have_27_nakshatras():
    for lang in LANGUAGES:
        assert len(NAKSHATRAS[lang]) == 27


def test_grahas_cover_9_planets():
    expected = {"Sun", "Moon", "Mars", "Mercury", "Jupiter",
                "Venus", "Saturn", "Rahu", "Ketu"}
    for lang in LANGUAGES:
        assert set(GRAHAS[lang]) == expected


def test_verdicts_present_in_all_languages():
    required = {"HIGH", "MEDIUM", "LOW", "WEAK", "REJECTED",
                "STRONG YES", "YES", "WEAK YES", "NO", "INDETERMINATE"}
    for lang in LANGUAGES:
        for v in required:
            assert v in VERDICTS[lang], f"{lang} missing verdict {v}"


def test_translate_sign():
    assert translate("sign", "Sagittarius", "hi") == "धनु"
    assert translate("sign", "Sagittarius", "ta") == "தனுசு"
    assert translate("sign", "Sagittarius", "sa") == "Dhanus"


def test_translate_falls_back_to_english():
    # Unknown lang
    assert translate("sign", "Sagittarius", "fr") == "Sagittarius"
    # Unknown value
    assert translate("sign", "NotASign", "hi") == "NotASign"


def test_localize_chart_recurses():
    sample = {"lagna_sign": "Sagittarius", "moon_sign": "Leo",
              "yogas": [{"name": "Hamsa", "lord": "Jupiter"}]}
    out = localize_chart(sample, "hi")
    assert out["lagna_sign"] == "धनु"
    assert out["moon_sign"] == "सिंह"
    assert out["yogas"][0]["lord"] == "गुरु"


def test_truth_directive_preserved_in_translation():
    # REJECTED must remain rejected in every language
    for lang in LANGUAGES:
        v = translate("verdict", "REJECTED", lang)
        # Just verify translation exists and is non-empty
        assert v
        # Verify it's distinct from a positive verdict
        positive = translate("verdict", "EXCELLENT", lang)
        assert v != positive
