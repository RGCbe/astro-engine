import re
import os

target_file = r'f:\astro\runtime\category_engine.py'
with open(target_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports for meta_reasoner at the top of the file
import_stmt = """
from vedic_core import RASIS, RASI_LORDS, DIGNITIES
from granular_dasha import build_full_timeline
import sys
sys.path.insert(0, str(_ROOT / "engine"))
from meta_reasoner import Evidence, MetaReasoner, ResolvedConclusion
"""
content = content.replace(
    "from vedic_core import RASIS, RASI_LORDS, DIGNITIES\nfrom granular_dasha import build_full_timeline",
    import_stmt
)

# Replace the evaluate_category function
new_evaluate_func = '''
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
'''

# Find the evaluate_category function and replace it
# It starts at def evaluate_category(self, chart, ds, tr, yogas, age, cat_id):
# and ends right before def scan_year(self, chart, year, timeline=None, transits=None, yogas=None, sample_days=10, min_severity=2):

pattern = r'    def evaluate_category\(self, chart, ds, tr, yogas, age, cat_id\):.*?    def scan_year'
content = re.sub(pattern, new_evaluate_func + '\n    def scan_year', content, flags=re.DOTALL)

# Update scan_year signature and internal logic
content = content.replace(
    'def scan_year(self, chart, year, timeline=None, transits=None, yogas=None, sample_days=10, min_severity=2):',
    'def scan_year(self, chart, year, timeline=None, transits=None, yogas=None, sample_days=10, min_probability=0.4):'
)

content = content.replace(
    'if pred and pred["severity"] >= min_severity:',
    'if pred and pred["probability"] >= min_probability:'
)

content = content.replace(
    '"severity": pred["severity"],',
    '"probability": pred["probability"],\n                            "confidence_band": pred["confidence_band"],'
)

# Update scan_lifetime signature
content = content.replace(
    'def scan_lifetime(self, chart, year_from, year_to, sample_days=14, min_severity=2):',
    'def scan_lifetime(self, chart, year_from, year_to, sample_days=14, min_probability=0.4):'
)

content = content.replace(
    'sample_days=sample_days, min_severity=min_severity',
    'sample_days=sample_days, min_probability=min_probability'
)

# Update collapse_consecutive
content = content.replace(
    'cur["severity"] = max(cur["severity"], e["severity"])',
    'cur["probability"] = max(cur["probability"], e["probability"])'
)

with open(target_file, 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS")
