"""
V2 Continuous Learning Loop (RLHF Engine)

Records user feedback (1-5 stars) on specific events and uses that data
to dynamically adjust the global weights of individual astrological rules
used by the MetaReasoner.
"""

import json
from pathlib import Path
import datetime as dt

DATA_FILE = Path(r"f:\astro\engine\data\feedback_v2.json")

def _load() -> dict:
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "event_feedback": [], # Raw feedback logs
        "rule_stats": {},     # Accumulated metrics per rule
        "learned_weights": {} # The final exported weights used by MetaReasoner
    }

def _save(d: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2)

def record_feedback(chart_id: str, event_category: str, rule_ids: list[str], rating_1_to_5: int) -> None:
    """
    Records human feedback on a predicted event and attributes it to the underlying rules.
    """
    db = _load()
    
    # 1. Log raw feedback
    db["event_feedback"].append({
        "chart_id": chart_id,
        "category": event_category,
        "rule_ids": rule_ids,
        "rating": rating_1_to_5,
        "ts": dt.datetime.utcnow().isoformat()
    })
    
    # 2. Update rule statistics
    for rule_id in rule_ids:
        if rule_id not in db["rule_stats"]:
            db["rule_stats"][rule_id] = {"count": 0, "positive": 0, "negative": 0}
            
        stats = db["rule_stats"][rule_id]
        stats["count"] += 1
        
        if rating_1_to_5 >= 4:
            stats["positive"] += 1
        elif rating_1_to_5 <= 2:
            stats["negative"] += 1
            
    # 3. Recalculate global weights
    _recalculate_weights(db)
    _save(db)

def _recalculate_weights(db: dict) -> None:
    """
    Applies the RLHF mathematical formula to adjust rule weights.
    Rules with < 5 feedback points remain neutral (multiplier = 1.0).
    """
    MIN_FEEDBACK_THRESHOLD = 5
    
    for rule_id, stats in db["rule_stats"].items():
        if stats["count"] < MIN_FEEDBACK_THRESHOLD:
            db["learned_weights"][rule_id] = 1.0
            continue
            
        total_polar = stats["positive"] + stats["negative"]
        if total_polar == 0:
            db["learned_weights"][rule_id] = 1.0
            continue
            
        # Win rate shifts the multiplier between 0.5 (heavy penalty) and 1.5 (heavy boost)
        win_rate = stats["positive"] / total_polar
        
        # Base is 1.0. If win_rate is 100%, multiplier becomes 1.5. If 0%, becomes 0.5.
        multiplier = 0.5 + (win_rate * 1.0)
        
        # Smooth the curve so extreme early feedback doesn't swing it too violently
        damping_factor = min(1.0, stats["count"] / 20.0) # Full effect at 20 ratings
        
        final_multiplier = 1.0 + ((multiplier - 1.0) * damping_factor)
        
        # Clamp between 0.3 and 2.0
        db["learned_weights"][rule_id] = max(0.3, min(2.0, final_multiplier))

def get_learned_weights() -> dict[str, float]:
    """Exposed for MetaReasoner to grab the live RLHF weights."""
    return _load()["learned_weights"]
