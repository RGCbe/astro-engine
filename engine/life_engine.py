"""
Life Intelligence System - Main Orchestrator (Phase 2: Digital Twin)
Generates the timeline in "Netflix Seasons" format, deeply profiling 7 life dimensions,
good/bad dichotomy, psychological insights, and rigorous evidence weighing.
"""
from __future__ import annotations
import datetime as dt

from engine.timeline_deep import predict_ad_events, EVENT_LABEL
from engine.feedback_loop import get_adjusted_confidence
from engine.life_metrics import calculate_momentum, calculate_pressure, calculate_opportunity_curve
from engine.truth_engine import weigh_evidence
from engine.pattern_detector import detect_repeating_patterns

# Delegate mappings to core narrative config
from src.core.narrative_config import (
    get_season_for_age,
    evaluate_dimensions,
    generate_chapter_quote,
    generate_intelligence_tags,
    evaluate_opportunities_pressures,
    evaluate_psychology,
    generate_cause_effect
)

def generate_life_timeline(chart, user_id: str = "default_user") -> dict:
    """
    Generates the full Phase 2 Digital Twin timeline structure.
    """
    ad_events = predict_ad_events(chart)
    seasons = {}
    episodes_list = []

    for i, e in enumerate(ad_events):
        season_num, age_range, title = get_season_for_age(e.age_start)
        
        if season_num not in seasons:
            seasons[season_num] = {
                "season_number": season_num,
                "age_range": age_range,
                "title": title,
                "episodes": []
            }
            
        dominant_event = e.event
        md_lord = e.md_lord
        ad_lord = e.ad_lord
        current_age = float(e.age_start)
        
        # Look ahead for cause-and-effect chaining
        next_event = ad_events[i+1].event if i + 1 < len(ad_events) else None
        
        truth_assessment = weigh_evidence(chart, md_lord, ad_lord, dominant_event)
        confidence = get_adjusted_confidence(e.event, e.confidence)
        
        episode = {
            "episode_id": f"s{season_num}_age{int(e.age_start)}_{e.event}",
            "age_start": e.age_start,
            "age_end": e.age_end,
            "event_class": e.event,
            "confidence": confidence,
            
            "quote": generate_chapter_quote(dominant_event, current_age),
            "intelligence_tags": generate_intelligence_tags(dominant_event, current_age),
            "dimensions": evaluate_dimensions(dominant_event, current_age),
            "opportunities_pressures": evaluate_opportunities_pressures(dominant_event, current_age),
            "psychology": evaluate_psychology(dominant_event, current_age),
            "truth_engine": truth_assessment,
            
            "cause_effect": generate_cause_effect(dominant_event, current_age, next_event)
        }
        seasons[season_num]["episodes"].append(episode)
        episodes_list.append(episode)
        
    start_year = chart.birth_dt.year
    end_year = start_year + 80
    momentum = calculate_momentum(chart, start_year, end_year)
    pressure = calculate_pressure(chart, start_year, end_year)
    repeating_patterns = detect_repeating_patterns(episodes_list)
    
    return {
        "user_id": user_id,
        "repeating_patterns": repeating_patterns,
        "seasons": list(seasons.values()),
        "metrics": {
            "momentum": momentum,
            "pressure": pressure,
            "opportunity": {yr: calculate_opportunity_curve(chart, yr) for yr in range(start_year, end_year + 1, 5)}
        }
    }
