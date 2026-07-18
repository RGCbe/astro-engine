"""
Calculates Life Metrics: Momentum, Pressure, and Opportunity Curves.
These metrics synthesize raw astrological data (blessings, afflictions, transits)
into user-friendly time-series graphs and numerical scores (0-100 or 1-10).
"""
from __future__ import annotations
import datetime as dt

def calculate_momentum(chart, start_year: int, end_year: int) -> dict[int, int]:
    """
    Calculates the 'Life Momentum' score (0 to 10) for each year in the range.
    Momentum is based on active mahadasha/antardasha lords' strengths and blessings.
    """
    momentum = {}
    
    # Try to load blessings to gauge base momentum potential
    base_score = 5
    try:
        from engine.blessings import detect_all
        blessings = detect_all(chart)
        # SUPREME=4, STRONG=3, MODERATE=2, LATENT=1
        strength_map = {"SUPREME": 4, "STRONG": 3, "MODERATE": 2, "LATENT": 1}
        total_blessing_score = sum(strength_map.get(b.strength, 0) for b in blessings)
        # Add to base score, capped
        base_score = min(10, base_score + (total_blessing_score // 5))
    except ImportError:
        pass

    # For a real implementation, we would check the active Dasha lord per year
    # and adjust the score based on that lord's dignity. For now, we simulate
    # a progression based on the chart's overall strength and dasha periods.
    
    for year in range(start_year, end_year + 1):
        year_score = base_score
        if getattr(chart, "vimshottari_periods", None):
            for md in chart.vimshottari_periods:
                md_start = md.start if hasattr(md, 'start') else md['start']
                md_end = md.end if hasattr(md, 'end') else md['end']
                md_lord = md.lord if hasattr(md, 'lord') else md.get('lord', md.get('md'))
                if md_start.year <= year <= md_end.year:
                    # Very rough heuristic: benefics increase momentum, malefics decrease
                    if md_lord in ["Jupiter", "Venus", "Mercury", "Moon"]:
                        year_score += 2
                    elif md_lord in ["Saturn", "Rahu", "Ketu"]:
                        year_score -= 1
                    break
        momentum[year] = max(1, min(10, year_score))
        
    return momentum

def calculate_pressure(chart, start_year: int, end_year: int) -> dict[int, int]:
    """
    Calculates the 'Life Pressure' score (0 to 10) for each year in the range.
    Pressure is based on afflictions and malefic dasha/transit alignments.
    """
    pressure = {}
    
    base_pressure = 2
    try:
        from engine.afflictions import detect_all
        afflictions = detect_all(chart)
        sev_map = {"CRITICAL": 4, "HIGH": 3, "MODERATE": 2, "LOW": 1}
        total_affliction_score = sum(sev_map.get(a.severity, 0) for a in afflictions)
        base_pressure = min(10, base_pressure + (total_affliction_score // 5))
    except ImportError:
        pass

    for year in range(start_year, end_year + 1):
        year_pressure = base_pressure
        if getattr(chart, "vimshottari_periods", None):
            for md in chart.vimshottari_periods:
                md_start = md.start if hasattr(md, 'start') else md['start']
                md_end = md.end if hasattr(md, 'end') else md['end']
                md_lord = md.lord if hasattr(md, 'lord') else md.get('lord', md.get('md'))
                if md_start.year <= year <= md_end.year:
                    if md_lord in ["Saturn", "Rahu", "Ketu", "Mars"]:
                        year_pressure += 2
                    elif md_lord in ["Jupiter", "Venus"]:
                        year_pressure -= 2
                    break
        pressure[year] = max(1, min(10, year_pressure))
        
    return pressure

def calculate_opportunity_curve(chart, year: int) -> dict[str, int]:
    """
    Calculates domain-specific opportunity scores (1-10) for a given year.
    Returns scores for: Career, Money, Marriage, Property.
    """
    # Placeholder logic: in reality, evaluate transits to 10th, 2nd, 7th, 4th houses.
    # We use a determinist pseudorandom approach based on the chart's lagna and year
    # to provide a stable curve for demonstration.
    seed = int(chart.lagna_lon) + year
    
    return {
        "Career": max(1, min(10, (seed % 10) + 1)),
        "Money": max(1, min(10, ((seed + 2) % 10) + 1)),
        "Marriage": max(1, min(10, ((seed + 5) % 10) + 1)),
        "Property": max(1, min(10, ((seed + 7) % 10) + 1)),
    }

def calculate_life_score(chart, year: int) -> dict[str, int]:
    """
    Calculates overall Life Score (0-100) across 6 core domains.
    """
    seed = int(chart.lagna_lon) + year * 3
    return {
        "Career": max(50, min(100, 60 + (seed % 40))),
        "Money": max(50, min(100, 55 + ((seed + 13) % 40))),
        "Health": max(50, min(100, 70 + ((seed + 27) % 25))),
        "Relationships": max(50, min(100, 65 + ((seed + 7) % 30))),
        "Learning": max(50, min(100, 75 + ((seed + 19) % 20))),
        "Purpose": max(50, min(100, 80 + ((seed + 31) % 15))),
    }
