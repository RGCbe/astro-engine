"""Tests for the post-audit Tier 1 + Tier 2 modules."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from engine.chart import compute_chart


def _chart():
    return compute_chart(date="1996-05-25", time="20:25", tz_hours=5.5,
                         place="Coimbatore", name="Manoj")


def test_ashtakavarga_grand_total_337():
    from engine.ashtakavarga import sarva_ashtakavarga, bhinna_ashtakavarga
    c = _chart()
    sav = sarva_ashtakavarga(c)
    assert sum(sav) == 337, f"SAV grand total {sum(sav)}; BPHS canonical = 337"
    bav = bhinna_ashtakavarga(c)
    # Per planet totals: 48, 49, 39, 54, 56, 52, 39 (sum 337)
    expected = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54,
                "Jupiter": 56, "Venus": 52, "Saturn": 39}
    for p, exp in expected.items():
        assert sum(bav[p]) == exp, f"{p} BAV total {sum(bav[p])} != {exp}"


def test_ashtakavarga_shodhana():
    from engine.ashtakavarga import bhinna_ashtakavarga, trikona_shodhana, shodhana
    c = _chart()
    bav = bhinna_ashtakavarga(c)
    for planet, bindus in bav.items():
        purified = shodhana(bindus)
        assert all(p >= 0 for p in purified), f"{planet} shodhana negative bindus"


def test_full_shadbala_six_balas():
    c = _chart()
    sb = c.shadbala
    for planet in ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"):
        assert planet in sb
        comps = sb[planet]["components"]
        # All 6 balas + sub-components present
        for key in ("cheshta", "drig", "saptavargaja", "uchcha",
                    "ojhayugma", "kendradi", "drekkana"):
            assert key in comps, f"{planet} missing {key}"


def test_bhava_bala_12_houses():
    from engine.bhava_bala import bhava_bala
    bb = bhava_bala(_chart())
    assert set(bb.keys()) == set(range(1, 13))
    for h, v in bb.items():
        assert "total_virupas" in v
        assert v["total_virupas"] > 0


def test_ishta_kashta_balanced():
    from engine.bhava_bala import ishta_kashta
    ik = ishta_kashta(_chart())
    for planet, info in ik.items():
        # ishta + kashta should sum to ~60
        s = info["ishta_virupas"] + info["kashta_virupas"]
        assert 55 < s < 65, f"{planet} ishta+kashta = {s}"


def test_conditioned_forecast_applies_modifiers():
    from engine.conditioned import conditioned_forecast_for_chart
    out = conditioned_forecast_for_chart(_chart())
    # Must have entries for every event
    assert "MARRIAGE" in out
    # If Hamsa Yoga present, AWARD should be lifted
    award = out["AWARD"]["conditioned"]
    assert award["conditioned_LR"] >= award["base_LR"] * 0.99


def test_blessing_backtest_runs():
    from engine._research.blessing_backtest import run_blessing_backtest
    r = run_blessing_backtest()
    assert r["n_charts_total"] >= 40
    assert r["overall_good_rate"] > 0
    assert "by_blessing" in r


def test_severity_refit_promotes_high_lift():
    from engine._research.severity_refit import refit_severities
    refit = refit_severities(min_n=2)
    # Top empirical lifts should land in HIGH or CRITICAL
    high_lift_codes = [code for code, info in refit.items()
                       if info["lift_ratio"] >= 1.7]
    for code in high_lift_codes:
        assert refit[code]["empirical_severity"] == "CRITICAL"


def test_argala_for_lagna():
    from engine.argala import argala_for_house
    arg = argala_for_house(_chart(), 1)
    # Should return 5 argala-houses
    assert len(arg) == 5
    for k, v in arg.items():
        assert "fires" in v
        assert "net_strength" in v


def test_varga_modifier_returns_modifier():
    from engine._research.varga_weighted import varga_modifier
    c = _chart()
    m = varga_modifier(c, "Venus", "MARRIAGE")
    assert "modifier" in m
    assert 0.5 < m["modifier"] < 2.0


def test_learned_ensemble_weights_loaded():
    from engine._research.learned_ensemble import cache_weights
    w = cache_weights()
    assert "MARRIAGE" in w
    assert "beta_transit" in w["MARRIAGE"]
