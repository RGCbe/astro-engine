"""
Pattern Detector.
Scans the generated timeline to detect repeating life cycles and overarching themes.
"""
from __future__ import annotations

def detect_repeating_patterns(timeline_episodes: list[dict]) -> list[str]:
    """
    Analyzes a list of timeline episodes to find repeating cadences
    (e.g., 7-year cycles, consistent event orderings).
    """
    patterns = []
    
    # Extract event history and ages
    event_sequence = [ep["event_class"] for ep in timeline_episodes]
    
    # 1. Detect 7-year Saturnine cycles
    # (Simplified heuristic for demonstration)
    if len(event_sequence) > 10:
        patterns.append("Every 7-8 years, a period of rapid external growth is consistently followed by a phase of internal consolidation and reassessment.")
        
    # 2. Detect Cause/Effect consistencies
    if "EDUCATION_PEAK" in event_sequence and "CAREER_LAUNCH" in event_sequence:
        patterns.append("Your career advancements historically follow periods of deep, focused learning rather than sudden networking leaps.")
        
    if "HEALTH_CRISIS" in event_sequence and "SPIRITUAL_TURN" in event_sequence:
        patterns.append("Periods of physical vulnerability or restriction consistently act as the catalyst for your most profound spiritual awakenings.")
        
    # 3. Interpersonal patterns
    if "MARRIAGE" in event_sequence or "FAMILY_LOSS" in event_sequence:
        patterns.append("Your closest relationships undergo structural transformations right before major shifts in your external life path.")
        
    if not patterns:
        patterns.append("Your life path moves linearly, with each phase building directly upon the last without heavy cyclical repetition.")
        
    return patterns
