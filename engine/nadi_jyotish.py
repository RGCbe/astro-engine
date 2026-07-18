"""engine.nadi_jyotish — Bhrigu Nandi Nadi Engine.

Bridges to runtime/nadi_full.py, runtime/nadi_jyotish.py, and runtime/transit_engine.py.
Computes 108 cells, 13 conjunction rules, karakas, and slow planet transit alignments.
"""
import sys, os
import datetime as dt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))

try:
    from nadi_full import complete_nadi_analysis
    from transit_engine import transit_positions
except ImportError:
    pass

NADI_TRANSIT_RULES = {
    ("Saturn", "Mars"): {
        "conjunction": "Transiting Saturn meets natal Mars. This triggers dynamic karmic energy. Watch for professional clashes, surgical/accident vulnerability, or an intense surge in real estate and physical efforts.",
        "trine": "Transiting Saturn trines natal Mars. Pave the way for constructive action. Highly auspicious for property purchases, technical engineering milestones, and channeled courage.",
        "opposition": "Transiting Saturn opposes natal Mars. Tension rises between duty and desire. Avoid direct conflicts with authorities or siblings; channel energy into disciplined physical work."
    },
    ("Saturn", "Mercury"): {
        "conjunction": "Transiting Saturn conjoins natal Mercury. The native takes on serious business negotiations, intellectual contracts, or commercial duties. Paperwork requires meticulous review.",
        "trine": "Transiting Saturn trines natal Mercury. Business expansion and educational milestones flow easily. Meticulous analytical work brings recognition and stable contracts.",
        "opposition": "Transiting Saturn opposes natal Mercury. Minor business delays or communication misalignments. Patience required in legal paperwork and discussions."
    },
    ("Saturn", "Jupiter"): {
        "conjunction": "Dharmic double-transit: Saturn meets Jupiter. A period of major professional structure, wisdom integration, and spiritual maturity. The native receives long-term status elevation.",
        "trine": "Transiting Saturn trines natal Jupiter. Extremely auspicious period for stable gains, starting noble ventures, and obtaining mentorship or institutional support.",
        "opposition": "Transiting Saturn opposes natal Jupiter. Rebalancing of career duties and personal philosophies. A test of structural faith."
    },
    ("Saturn", "Venus"): {
        "conjunction": "Transiting Saturn conjoins natal Venus. Karmic relationship events. Stable bonds are formalized (marriage); loose bonds are tested. Financial acquisitions require conservative planning.",
        "trine": "Transiting Saturn trines natal Venus. Auspicious for long-term investments in luxury, arts, or vehicles. Stable domestic harmony.",
        "opposition": "Transiting Saturn opposes natal Venus. Temporary coldness in relationships or financial discipline checks. Focus on duty in marriage."
    },
    ("Saturn", "Sun"): {
        "conjunction": "Transiting Saturn meets natal Sun. The king meets the servant. A period of heavy duty, paternal worries, and structural ego purification. Native rises to serious authority.",
        "trine": "Transiting Saturn trines natal Sun. Stable growth in governance, corporate authority, and institutional respect. Father receives gains.",
        "opposition": "Transiting Saturn opposes natal Sun. Friction with elders or governmental structures. Take care of bones and eyes."
    },
    ("Saturn", "Moon"): {
        "conjunction": "Karmic emotional pressure (Sade Sati flavor). Mind experiences deep introspection, structural changes in home, or mother's health worries. Renunciation inclination.",
        "trine": "Transiting Saturn trines natal Moon. Disciplined emotional stability, meditation depth, and long-term travel for business purposes.",
        "opposition": "Transiting Saturn opposes natal Moon. Anxiety or temporary domestic isolation. Cultivate mindfulness."
    },
    ("Jupiter", "Saturn"): {
        "conjunction": "Transiting Jupiter meets natal Saturn (Jiva meets Karma). Blessing upon professional efforts. Financial blocks dissolve; recognition arrives after long effort.",
        "trine": "Transiting Jupiter trines natal Saturn. Smooth career progress, mentorship support, and highly positive expansions in business.",
        "opposition": "Transiting Jupiter opposes natal Saturn. Expansion vs limitation conflicts resolved. Native finds middle path in career."
    },
    ("Jupiter", "Mars"): {
        "conjunction": "Transiting Jupiter meets natal Mars (Jiva meets energy). Extremely high physical energy, bold sports/property success, and victory over adversaries.",
        "trine": "Transiting Jupiter trines natal Mars. Favorable for real estate investments, surgical recoveries, and harmonious relations with brothers.",
        "opposition": "Transiting Jupiter opposes natal Mars. Overconfidence in physical actions. Channel boldness into constructive projects."
    },
    ("Jupiter", "Venus"): {
        "conjunction": "Transiting Jupiter meets natal Venus. High financial prosperity, wedding bells, creative peak, and comfortable domestic arrivals.",
        "trine": "Transiting Jupiter trines natal Venus. Auspicious for wealth accumulation, jewelry purchase, and beautiful relationship expansions.",
        "opposition": "Transiting Jupiter opposes natal Venus. Sensual extravagance. Keep budgets balanced."
    }
}

def get_nadi_transit_reading(tp, np, aspect):
    # Lookup in custom rules, or fallback to generic Nadi interpretation
    res = NADI_TRANSIT_RULES.get((tp, np), {}).get(aspect)
    if res:
        return res
    
    # Fallback rules
    if tp == "Jupiter":
        return f"Transiting Jupiter aspects natal {np} via {aspect}. This brings Jiva-blessings, hope, wisdom, and auspicious expansion to {np}'s natural karaka themes."
    elif tp == "Saturn":
        return f"Transiting Saturn aspects natal {np} via {aspect}. This triggers karmic discipline, patience testing, professional duties, and structured evolution relating to {np}."
    elif tp == "Rahu":
        return f"Transiting Rahu aspects natal {np} via {aspect}. This initiates sudden unconventional opportunities, tech integration, foreign connections, or temporary illusion in {np}'s domain."
    elif tp == "Ketu":
        return f"Transiting Ketu aspects natal {np} via {aspect}. This encourages spiritual detachment, intuitive awakening, past-life talent recall, or isolation from standard {np} comforts."
    return f"Transiting {tp} aspects natal {np} via {aspect}."

def get_nadi_analysis(year, month, day, decimal_hour, lat, lon, planet_positions, asc_sid, transit_dt=None):
    """
    Format chart and run complete Bhrigu Nandi Nadi analysis including transit alignments.
    """
    hrs = int(decimal_hour)
    mins = int((decimal_hour - hrs) * 60)
    
    SIGN_NAMES = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    
    # Format compatible chart dictionary
    chart_dict = {
        "lagna_idx": int(asc_sid / 30) % 12,
        "positions": {},
        "birth": {
            "year": year,
            "month": month,
            "day": day,
            "hour": hrs,
            "min": mins
        }
    }
    
    # Map planetary positions
    for p, pdata in planet_positions.items():
        lon_deg = pdata["longitude"]
        rasi_idx = int(lon_deg / 30) % 12
        # Deduce house if not explicitly defined
        h = pdata.get("house")
        if h is None:
            l_idx = int(asc_sid / 30) % 12
            h = ((rasi_idx - l_idx) % 12) + 1
        
        chart_dict["positions"][p] = {
            "deg": lon_deg % 30,
            "rasi_idx": rasi_idx,
            "rasi": SIGN_NAMES[rasi_idx],
            "house": h,
            "lon": lon_deg,
            "lon_abs": lon_deg
        }
        
    try:
        # 1. Complete Nadi narrative, 13 conjunction rules, and karakas
        nadi_static = complete_nadi_analysis(chart_dict)
        
        # 2. Compute live slow planet transits relative to natal coordinates
        if transit_dt is None:
            transit_dt = dt.datetime.now()
            
        transits = transit_positions(transit_dt)
        slow_planets = ["Saturn", "Jupiter", "Rahu", "Ketu"]
        
        transit_alignments = []
        for tp in slow_planets:
            if tp not in transits:
                continue
            tp_lon = transits[tp]["lon"]
            tp_sign_idx = transits[tp]["rasi_idx"]
            
            for np, np_data in chart_dict["positions"].items():
                np_lon = np_data["lon"]
                np_sign_idx = np_data["rasi_idx"]
                
                dist_signs = (tp_sign_idx - np_sign_idx) % 12
                
                # Aspect detection
                aspect = None
                orb = 0.0
                asp_key = ""
                
                if dist_signs == 0:
                    aspect = "Conjunction (1st house)"
                    asp_key = "conjunction"
                    diff = abs(tp_lon - np_lon) % 360
                    orb = min(diff, 360 - diff)
                elif dist_signs in (4, 8):
                    aspect = "Trine (5/9 house alignment)"
                    asp_key = "trine"
                    diff = (tp_lon - np_lon) % 360
                    orb = min(abs(diff - 120), abs(diff - 240))
                elif dist_signs == 6:
                    aspect = "Opposition (7th house alignment)"
                    asp_key = "opposition"
                    diff = abs(tp_lon - np_lon) % 360
                    orb = abs(diff - 180)
                    
                if aspect and orb <= 12.0:  # Allow 12 degree orb for slow transits
                    transit_alignments.append({
                        "transit_planet": tp,
                        "natal_planet": np,
                        "aspect": aspect,
                        "orb_degrees": round(orb, 2),
                        "reading": get_nadi_transit_reading(tp, np, asp_key)
                    })
                    
        return {
            "status": "success",
            "narrative": nadi_static["narrative_108_cells"],
            "two_planet_rules": nadi_static["two_planet_rules_detected"],
            "karakas": nadi_static["karaka_readings"],
            "transits": {
                "observation_date": transit_dt.isoformat()[:10],
                "transit_positions": {tp: transits[tp] for tp in slow_planets if tp in transits},
                "alignments": transit_alignments
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
