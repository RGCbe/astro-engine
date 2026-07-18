"""
Declarative Category Engine — Complete 402 Category predictive engine.
Maps every category in ATRO_FULL_CATEGORY_LIST.md to its classical rule logic,
house lordships, planetary signatures, and age limits dynamically.
"""
import datetime as dt
import sys
from pathlib import Path

# Setup paths
_RUNTIME = Path(__file__).resolve().parent
_ROOT = _RUNTIME.parent
sys.path.insert(0, str(_RUNTIME))
sys.path.insert(0, str(_ROOT))
import json
import os

DEFAULT_WEIGHTS = {
    "h_lord_md": 3.0,
    "h_lord_ad": 2.0,
    "h_lord_pd": 1.0,
    "karaka_md": 2.0,
    "karaka_ad": 1.5,
    "karaka_pd": 0.5,
    "karaka_auspicious": 1.0,
    "karaka_dusthana": 1.5,
    "transit_trigger": 1.5,
    "threshold_auspicious": 4.0,
    "threshold_inauspicious": 3.0
}

WEIGHTS_PATH = _ROOT / "scratch" / "engine_weights.json"
def get_weights():
    if WEIGHTS_PATH.exists():
        try:
            return json.load(open(WEIGHTS_PATH, "r", encoding="utf-8"))
        except: pass
    return DEFAULT_WEIGHTS



from vedic_core import RASIS, RASI_LORDS, DIGNITIES
from granular_dasha import build_full_timeline
import sys
sys.path.insert(0, str(_ROOT / "engine"))
from meta_reasoner import Evidence, MetaReasoner, ResolvedConclusion


def _h(pos, p): return pos[p]["house"] if p in pos else None
def _dig(pos, p): return DIGNITIES.get((p, pos[p]["rasi"]), "neutral") if p in pos else "neutral"
def _lord(lagna_idx, h): return RASI_LORDS[RASIS[(lagna_idx + h - 1) % 12]]

# ═════════════════════════════════════════════════════════════════════════════
# 402 CATEGORIES DEFINITION REFERENCE
# ═════════════════════════════════════════════════════════════════════════════

from category_catalog import CATEGORIES_CATALOG

class DeclarativeCategoryEngine:
    def __init__(self):
        self.catalog = CATEGORIES_CATALOG


    def evaluate_category(self, chart, ds, tr, yogas, age, cat_id):
        """Dynamic evaluator implementing V2 Probabilistic Meta-Reasoning.
        Generates Evidence objects for classical rules and resolves them.
        """
        cfg = self.catalog.get(cat_id)
        if not cfg:
            return None

        # 1. AGE GUARD
        min_age, max_age = cfg["age_guard"]
        if age < min_age or age > max_age:
            return None

        pos = chart["positions"]
        lagna_idx = chart.get("lagna_idx", 0)
        h_lord = _lord(lagna_idx, cfg["bhava"]) if cfg["bhava"] else None
        
        md = ds.get(1, {}).get("md")
        ad = ds.get(2, {}).get("ad")
        pd = ds.get(3, {}).get("pd")
        
        w = get_weights()
        evidence_list = []
        
        direction = 1.0 if cfg["auspicious"] is not False else -1.0
        # If the category is explicitly inauspicious (like accident, debt), direction is positive for that bad event happening.
        # Wait, the MetaReasoner treats positive direction as "the event happens". So direction is always 1.0 for the evidence that the category *will* occur.
        # But we can have negative evidence (cancellations). For now, standard triggers are 1.0.
        ev_dir = 1.0

        def add_ev(rule_name, weight, text):
            evidence_list.append(Evidence(
                rule_id=f"dyn_{rule_name}",
                source_tradition="Parashara",
                category=cat_id,
                direction=ev_dir,
                base_confidence=weight / 4.0, # Normalize 0-4 weights to 0.0-1.0
                context_multiplier=1.0,
                explainability_text=text
            ))

        # 2. HOUSE LORD ACTIVATION
        if h_lord:
            if md == h_lord: add_ev("h_lord_md", w.get("h_lord_md", 3.0), f"{cfg['bhava']}L ({h_lord}) MD — primary house active")
            elif ad == h_lord: add_ev("h_lord_ad", w.get("h_lord_ad", 2.0), f"{cfg['bhava']}L ({h_lord}) AD")
            elif pd == h_lord: add_ev("h_lord_pd", w.get("h_lord_pd", 1.0), f"{cfg['bhava']}L ({h_lord}) PD")

        # 3. KARAKA ACTIVATION
        for karaka in cfg["karakas"]:
            if md == karaka: add_ev("karaka_md", w.get("karaka_md", 2.0), f"{karaka} MD — karaka active")
            elif ad == karaka: add_ev("karaka_ad", w.get("karaka_ad", 1.5), f"{karaka} AD")
            elif pd == karaka: add_ev("karaka_pd", w.get("karaka_pd", 0.5), f"{karaka} PD")

        # 4. NATAL PLACEMENT BOOSTER
        for karaka in cfg["karakas"]:
            kp = _h(pos, karaka)
            if kp in [1, 5, 9, 10, 11]:
                add_ev("karaka_auspicious", w.get("karaka_auspicious", 1.0), f"{karaka} well-placed natally in H{kp}")
            elif kp in [6, 8, 12]:
                if not cfg["auspicious"]:
                    add_ev("karaka_dusthana", w.get("karaka_dusthana", 1.5), f"{karaka} afflicted in Dusthana H{kp}")

        # 5. TRANSIT BOOSTER
        for karaka in cfg["karakas"]:
            t_match = next((t for t in tr if t.get("transit") == karaka 
                            and t.get("severity") in ("MEDIUM", "HIGH", "VERY HIGH")), None)
            if t_match:
                add_ev("transit_trigger", w.get("transit_trigger", 1.5), f"Transit {karaka} active ({t_match.get('severity')})")

        if not evidence_list:
            return None

        reasoner = MetaReasoner()
        conclusion = reasoner.resolve_conflicts(evidence_list)
        
        # Build clean prediction dictionary matching engine outputs
        return {
            "event": f"{cfg['name']} Event",
            "category": cat_id,
            "probability": conclusion.net_probability,
            "confidence_band": conclusion.confidence_band,
            "why": conclusion.primary_factors,
            "source": cfg["source"],
            "contradictions": conclusion.contradictions_flagged
        }

    def scan_year(self, chart, year, timeline=None, transits=None, yogas=None, sample_days=10, min_probability=0.4):
        """Scans a given year using all 402 declarative categories."""
        if not timeline:
            timeline = build_full_timeline(chart, levels=3)
        if not yogas:
            from comprehensive_yogas import detect_all_classical_yogas
            yogas = detect_all_classical_yogas(chart)

        events_by_window = {}
        d = dt.datetime(year, 1, 1)
        end = dt.datetime(year, 12, 31)
        
        b = chart["birth"]
        birth_dt = dt.datetime(b["year"], b["month"], b["day"])

        while d <= end:
            age = (d - birth_dt).days / 365.25
            
            ds = {}
            for e in timeline:
                if e["start"] <= d <= e["end"]:
                    lvl = e.get("level", 1)
                    if lvl == 1: ds[1] = {"md": e["md"]}
                    elif lvl == 2: ds[2] = {"ad": e["ad"]}
                    elif lvl == 3: ds[3] = {"pd": e["pd"]}

            # Transit check for this date
            from transit_engine import detect_triggers
            tr = detect_triggers(chart, d)

            # Evaluate all categories
            for cat_id in self.catalog:
                pred = self.evaluate_category(chart, ds, tr, yogas, age, cat_id)
                if pred and pred["probability"] >= min_probability:
                    window_key = f"{cat_id}_{d.year}_{d.month}"
                    if window_key not in events_by_window:
                        events_by_window[window_key] = {
                            "event": pred["event"],
                            "category": pred["category"],
                            "peak_date": d.strftime("%Y-%m-%d"),
                            "probability": pred["probability"],
                            "severity": pred["probability"],
                            "confidence_band": pred["confidence_band"],
                            "why": pred["why"],
                            "source": pred["source"],
                            "window_start": d.strftime("%Y-%m-%d"),
                            "window_end": (d + dt.timedelta(days=15)).strftime("%Y-%m-%d")
                        }

            d += dt.timedelta(days=sample_days)

        return events_by_window

    def scan_lifetime(self, chart, year_from, year_to, sample_days=14, min_probability=0.4):
        """Scans a lifetime range and returns all collapsed events."""
        timeline = build_full_timeline(chart, levels=3)
        from comprehensive_yogas import detect_all_classical_yogas
        yogas = detect_all_classical_yogas(chart)
        
        all_events = []
        for year in range(year_from, year_to + 1):
            year_events = self.scan_year(chart, year, timeline=timeline, yogas=yogas, sample_days=sample_days, min_probability=min_probability)
            for k, v in year_events.items():
                v["year"] = year
                all_events.append(v)
        return all_events

    def collapse_consecutive(self, events):
        """Merge consecutive-year same-event windows into single lifecycle bands."""
        by_event = {}
        for ev in events:
            by_event.setdefault(ev["event"], []).append(ev)
        
        bands = []
        for event_name, lst in by_event.items():
            # Parse dates
            for e in lst:
                e["dt_start"] = dt.datetime.strptime(e["window_start"], "%Y-%m-%d")
                e["dt_end"] = dt.datetime.strptime(e["window_end"], "%Y-%m-%d")
            
            lst.sort(key=lambda x: x["dt_start"])
            cur = None
            for e in lst:
                if cur is None:
                    cur = dict(e)
                    cur["window_start"] = e["window_start"]
                    cur["window_end"] = e["window_end"]
                else:
                    gap = (e["dt_start"] - dt.datetime.strptime(cur["window_end"], "%Y-%m-%d")).days
                    if gap < 180:
                        cur["window_end"] = max(cur["window_end"], e["window_end"])
                        cur["probability"] = max(cur["probability"], e["probability"])
                    else:
                        bands.append(cur)
                        cur = dict(e)
            if cur:
                bands.append(cur)
        
        # Clean up temporary datetime keys
        for b in bands:
            b.pop("dt_start", None)
            b.pop("dt_end", None)
            
        return sorted(bands, key=lambda x: x["window_start"])

# Global instance for seamless integration
category_engine_instance = DeclarativeCategoryEngine()
