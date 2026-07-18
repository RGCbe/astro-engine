"""Tests for the convergence-gated event fusion layer (option B).

Core contract: a fused event is emitted only when >= 2 INDEPENDENT method
families converge on the same topic with overlapping tight time windows.
Esoteric families (mayan, palmistry, numerology, chinese, western, iching)
never count toward the gate. Output windows are the true intersection.
"""
from __future__ import annotations

import unittest

from engine.event_fusion import (
    classify_family,
    topic_for_category,
    fuse_events,
    GATING_FAMILIES,
    ALL_FAMILIES,
)


def _ev(category, first, last, sev=3, valence=None, source=""):
    e = {
        "category": category,
        "first": first,
        "last": last,
        "max_sev": sev,
        "source": source,
    }
    if valence:
        e["predicted_valence"] = valence
    return e


class FamilyClassifierTests(unittest.TestCase):
    def test_core_families_from_category(self):
        cases = {
            "saham_roga": "tajik",
            "tajik_ithasala": "tajik",
            "annual_profection": "tajik",
            "kp_ruling_planet": "kp",
            "nadi_karaka_shift": "nadi",
            "d27_strength_sub": "divisional",
            "sade_sati": "transit",
            "ashtam_shani": "transit",
            "ardha_ashtam": "transit",
            "career": "parashari",
            "political_office": "parashari",
            "adhi_yoga": "yoga",
            "vish_yoga": "yoga",
        }
        for cat, fam in cases.items():
            self.assertEqual(classify_family({"category": cat}), fam, cat)

    def test_esoteric_families_are_not_gating(self):
        for cat in ("mayan_wave_spell", "bazi_clash_year", "personal_year_shift",
                    "palmistry_life_break", "pluto_transit", "ziwei_palace"):
            fam = classify_family({"category": cat})
            self.assertNotIn(fam, GATING_FAMILIES, cat)

    def test_jaimini_from_source_when_category_ambiguous(self):
        fam = classify_family({"category": "career_breakthrough",
                               "source": "Jaimini Sutras Ch.2 Chara Karaka"})
        self.assertEqual(fam, "jaimini")


class TopicMappingTests(unittest.TestCase):
    def test_known_topics(self):
        self.assertEqual(topic_for_category("political_office"), "career")
        self.assertEqual(topic_for_category("marriage"), "marriage")
        self.assertEqual(topic_for_category("saham_roga"), "health")
        self.assertEqual(topic_for_category("wealth_loss"), "wealth")

    def test_unmapped_categories_return_none(self):
        self.assertIsNone(topic_for_category("mayan_wave_spell"))
        self.assertIsNone(topic_for_category("vitality_cycle"))


class FusionGateTests(unittest.TestCase):
    def test_two_independent_families_fuse_with_intersection_window(self):
        events = [
            _ev("career", "2014-01-01", "2014-08-01", sev=4),          # parashari
            _ev("kp_career_sub", "2014-04-01", "2014-12-01", sev=3),   # kp
        ]
        fused = fuse_events(events)
        self.assertEqual(len(fused), 1)
        f = fused[0]
        self.assertEqual(f["category"], "career")
        self.assertEqual(f["window_start"], "2014-04-01")
        self.assertEqual(f["window_end"], "2014-08-01")
        self.assertEqual(f["max_sev"], 4)
        self.assertEqual(sorted(f["families"]), ["kp", "parashari"])

    def test_same_family_twice_does_not_fuse(self):
        events = [
            _ev("career", "2014-01-01", "2014-08-01"),
            _ev("promotion", "2014-03-01", "2014-09-01"),  # also parashari
        ]
        self.assertEqual(fuse_events(events), [])

    def test_esoteric_partner_does_not_satisfy_gate(self):
        events = [
            _ev("career", "2014-01-01", "2014-08-01"),
            _ev("mayan_wave_spell", "2014-02-01", "2014-07-01"),
        ]
        self.assertEqual(fuse_events(events), [])

    def test_widened_gate_lets_esoteric_family_fuse(self):
        # Experimental mode only: with gating_families=ALL_FAMILIES a topic-mapped
        # esoteric category (palmistry life-line break -> health) can open the gate.
        events = [
            _ev("health", "2014-01-01", "2014-06-01"),
            _ev("palmistry_life_break", "2014-02-01", "2014-05-01"),
        ]
        self.assertEqual(fuse_events(events), [])  # default gate: still refused
        fused = fuse_events(events, gating_families=ALL_FAMILIES)
        self.assertEqual(len(fused), 1)
        self.assertEqual(fused[0]["category"], "health")

    def test_non_overlapping_windows_do_not_fuse(self):
        events = [
            _ev("career", "2014-01-01", "2014-03-01"),
            _ev("kp_career_sub", "2015-01-01", "2015-03-01"),
        ]
        self.assertEqual(fuse_events(events), [])

    def test_different_topics_do_not_fuse(self):
        events = [
            _ev("career", "2014-01-01", "2014-08-01"),
            _ev("saham_roga", "2014-02-01", "2014-07-01"),  # health topic
        ]
        self.assertEqual(fuse_events(events), [])

    def test_overly_wide_intersection_is_discarded(self):
        events = [
            _ev("career", "2010-01-01", "2019-01-01"),
            _ev("kp_career_sub", "2010-06-01", "2018-06-01"),
        ]
        self.assertEqual(fuse_events(events, max_window_days=540), [])

    def test_career_gate_opens_across_parashari_and_tajik(self):
        # Regression: career events were parashari-only, so the >=2-family gate
        # could never open (Modi/SRK/Indira scored 0%). Karya saham (tajik,
        # work/undertakings) must count as career evidence.
        events = [
            _ev("political_office", "2014-03-01", "2014-09-01", sev=5),
            _ev("saham_karya", "2014-04-15", "2014-08-01", sev=3),
        ]
        fused = fuse_events(events)
        self.assertEqual(len(fused), 1)
        self.assertEqual(fused[0]["category"], "career")
        self.assertEqual(sorted(fused[0]["families"]), ["parashari", "tajik"])

    def test_honor_gate_opens_with_yasas_saham(self):
        events = [
            _ev("honor", "1999-01-01", "1999-06-01", sev=4),
            _ev("saham_yasas", "1999-02-01", "1999-05-01", sev=3),
        ]
        fused = fuse_events(events)
        self.assertEqual(len(fused), 1)
        self.assertEqual(fused[0]["category"], "honor")

    def test_output_is_deterministic_and_sorted(self):
        events = [
            _ev("kp_career_sub", "2014-04-01", "2014-12-01"),
            _ev("career", "2014-01-01", "2014-08-01"),
            _ev("saham_roga", "2011-01-01", "2011-05-01"),
            _ev("health", "2011-02-01", "2011-06-01"),
        ]
        fused_a = fuse_events(events)
        fused_b = fuse_events(list(reversed(events)))
        self.assertEqual(fused_a, fused_b)
        self.assertEqual([f["category"] for f in fused_a], ["health", "career"])


if __name__ == "__main__":
    unittest.main()
