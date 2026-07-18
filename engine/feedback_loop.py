"""
Feedback Loop Engine.
Records user feedback (1-5 stars) and dynamically updates internal
confidence weightings for event predictions over time.
"""
from __future__ import annotations
import json
import os
import datetime as dt

FEEDBACK_DB_PATH = os.path.join(os.path.dirname(__file__), "data", "timeline_feedback.json")

def _load_feedback_db() -> dict:
    if not os.path.exists(FEEDBACK_DB_PATH):
        # Create directory if missing
        os.makedirs(os.path.dirname(FEEDBACK_DB_PATH), exist_ok=True)
        return {"users": {}, "event_weights": {}}
    try:
        with open(FEEDBACK_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "event_weights": {}}

def _save_feedback_db(db_data: dict) -> None:
    with open(FEEDBACK_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db_data, f, indent=2)

def record_feedback(user_id: str, episode_id: str, event_class: str, rating: int) -> dict:
    """
    Records a 1-5 star rating for a specific event class prediction
    and adjusts the global confidence weight for that event class.
    """
    db = _load_feedback_db()
    
    # 1. Record user rating
    current_user = db["users"].get(user_id)
    if not current_user:
        db["users"][user_id] = {}
        current_user = db["users"][user_id]
        
    current_user[episode_id] = {
        "event_class": event_class,
        "rating": rating,
        "timestamp": dt.datetime.now().isoformat()
    }
    
    # 2. Adjust global weight (continuous learning)
    # 3 stars is neutral, 4-5 is positive, 1-2 is negative
    weight_delta = 0.0
    if rating == 5:
        weight_delta = +0.05
    elif rating == 4:
        weight_delta = +0.02
    elif rating == 2:
        weight_delta = -0.02
    elif rating == 1:
        weight_delta = -0.05
        
    current_weight = db["event_weights"].get(event_class, 1.0)
    # Bound the weight multiplier between 0.5 and 1.5
    new_weight = max(0.5, min(1.5, current_weight + weight_delta))
    db["event_weights"][event_class] = new_weight
    
    _save_feedback_db(db)
    
    # Return the new system accuracy to simulate recalibration
    return {
        "event_class": event_class,
        "old_weight": current_weight,
        "new_weight": new_weight,
        "simulated_accuracy_improvement": f"{(new_weight * 100):.1f}%" if weight_delta > 0 else f"{(new_weight * 100):.1f}%"
    }

def get_adjusted_confidence(event_class: str, base_confidence: str) -> str:
    """
    Given a base structural confidence (HIGH, MEDIUM, LOW) from the engine,
    applies the learned weight to return a dynamic percentage confidence.
    """
    db = _load_feedback_db()
    weight = db["event_weights"].get(event_class, 1.0)
    
    base_map = {"HIGH": 85.0, "MEDIUM": 65.0, "LOW": 40.0}
    val = base_map.get(base_confidence, 50.0)
    
    # Apply learning weight
    adjusted = val * weight
    # Cap at 98%
    final = min(98.0, adjusted)
    
    return f"{final:.0f}%"
