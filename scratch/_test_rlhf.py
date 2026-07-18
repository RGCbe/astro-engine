import sys
from pathlib import Path
sys.path.insert(0, str(Path(r"f:\astro")))
sys.path.insert(0, str(Path(r"f:\astro\engine")))

from engine.feedback_v2 import record_feedback, get_learned_weights
from engine.meta_reasoner import MetaReasoner, Evidence
import json
import os

# Clear existing feedback data for clean test
DATA_FILE = Path(r"f:\astro\engine\data\feedback_v2.json")
if DATA_FILE.exists():
    os.remove(DATA_FILE)

def simulate():
    print("--- RLHF Simulation Started ---")
    
    # 1. Base test: What does the engine output without any feedback?
    reasoner_pre = MetaReasoner()
    
    # Simulate a user getting a prediction based on "dyn_h_lord_md" (House Lord Mahadasha)
    mock_evidence = [
        Evidence(
            rule_id="dyn_h_lord_md", source_tradition="Parashara", category="marriage", 
            direction=1.0, base_confidence=0.8, context_multiplier=1.0,
            explainability_text="7th Lord in Mahadasha indicates marriage."
        )
    ]
    
    conclusion_pre = reasoner_pre.resolve_conflicts(mock_evidence)
    print(f"\n[BEFORE FEEDBACK] Prediction Probability: {conclusion_pre.net_probability:.2f}")
    
    # 2. Feed in 5 fake "1-star" ratings from users complaining the rule is wrong
    print("\n[!] Simulating 5 angry users rating the prediction 1-star...")
    for i in range(5):
        record_feedback(
            chart_id=f"user_{i}",
            event_category="marriage",
            rule_ids=["dyn_h_lord_md"],
            rating_1_to_5=1  # 1 star (Strongly Disagree)
        )
        
    weights_mid = get_learned_weights()
    print(f"    -> Learned multiplier for rule 'dyn_h_lord_md': {weights_mid.get('dyn_h_lord_md', 1.0):.2f}")
    
    # Feed in 15 more angry users (total 20 ratings, all 1-star)
    print("\n[!] Simulating 15 more angry users (Total 20)...")
    for i in range(5, 20):
        record_feedback(
            chart_id=f"user_{i}",
            event_category="marriage",
            rule_ids=["dyn_h_lord_md"],
            rating_1_to_5=1  # 1 star
        )
        
    weights_post = get_learned_weights()
    print(f"    -> Learned multiplier for rule 'dyn_h_lord_md': {weights_post.get('dyn_h_lord_md', 1.0):.2f}")
    
    # 3. Test the engine again
    reasoner_post = MetaReasoner()
    conclusion_post = reasoner_post.resolve_conflicts(mock_evidence)
    print(f"\n[AFTER FEEDBACK] Prediction Probability: {conclusion_post.net_probability:.2f}")
    
    if conclusion_post.net_probability < conclusion_pre.net_probability:
        print("\nSUCCESS! The MetaReasoner successfully learned from human feedback and lowered its confidence automatically.")
    else:
        print("\nFAILED. The feedback did not alter the MetaReasoner logic.")

if __name__ == "__main__":
    simulate()
