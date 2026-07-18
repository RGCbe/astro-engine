"""
Cause and Effect Engine.
Analyzes sequential episodes to build a narrative bridge (cause and effect chains).
"""
from __future__ import annotations

def generate_cause_and_effect_chain(previous_episode_events: list[str], current_episode_events: list[str]) -> str:
    """
    Given events from a previous episode and a current episode,
    generates a narrative explaining how the past led to the present.
    """
    if not previous_episode_events or not current_episode_events:
        return ""
        
    # Heuristic mapping for cause-and-effect
    # E.g., EDUCATION_PEAK -> CAREER_LAUNCH
    # HEALTH_CRISIS -> SPIRITUAL_TURN
    
    causality_map = {
        "EDUCATION_PEAK": ["CAREER_LAUNCH", "FINANCIAL_GAIN", "RECOGNITION"],
        "HEALTH_CRISIS": ["SPIRITUAL_TURN", "FAMILY_LOSS"],
        "FOREIGN_TRAVEL": ["FOUND_BUSINESS", "MARRIAGE", "CAREER_LAUNCH"],
        "FAMILY_LOSS": ["SPIRITUAL_TURN", "HEALTH_CRISIS"],
        "CAREER_LAUNCH": ["FINANCIAL_GAIN", "MARRIAGE", "RECOGNITION"],
        "MARRIAGE": ["CHILDREN_BORN", "FINANCIAL_GAIN"],
        "SPIRITUAL_TURN": ["RECOGNITION", "FOUND_BUSINESS"],
    }
    
    chain = []
    for prev_evt in previous_episode_events:
        for curr_evt in current_episode_events:
            if curr_evt in causality_map.get(prev_evt, []):
                # Found a structural link
                prev_label = prev_evt.replace("_", " ").title()
                curr_label = curr_evt.replace("_", " ").title()
                chain.append(f"Your past experience with {prev_label.lower()} created the necessary foundation for the current {curr_label.lower()}.")
                break
                
    if not chain:
        # Fallback generic connection if no specific mapping is found
        prev = previous_episode_events[-1].replace("_", " ").title()
        curr = current_episode_events[0].replace("_", " ").title()
        chain.append(f"The shifts you navigated during your period of {prev.lower()} directly opened the door to {curr.lower()}.")
        
    return " \u2193\n\n".join(chain)
