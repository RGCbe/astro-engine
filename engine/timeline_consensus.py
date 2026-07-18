"""
Consensus Timeline Engine.
Synthesizes the 120-year Vimshottari Dasha with the 56-book Battle Engine.
Generates 'Deep Life' narratives for every major life chapter.
"""
from engine.comparative_test import execute_corpus_battle_comparison

def normalize_planet_name(name: str) -> str:
    mapping = {
        "Sun": "Sun", "Mon": "Moon", "Moon": "Moon", "Mar": "Mars", "Mars": "Mars",
        "Mer": "Mercury", "Mercury": "Mercury", "Jup": "Jupiter", "Jupiter": "Jupiter",
        "Ven": "Venus", "Venus": "Venus", "Sat": "Saturn", "Saturn": "Saturn",
        "Rah": "Rahu", "Rahu": "Rahu", "Ket": "Ketu", "Ketu": "Ketu"
    }
    return mapping.get(name[:3].capitalize(), name)

def generate_deep_timeline(full_chart: dict) -> list:
    """Orchestrates the 56-book battle for every Antardasha in the native's life."""
    timeline_blocks = []
    dashas = full_chart.get("dasha_schedule", [])
    
    # We focus on the Maha/Antar level for deep consensus
    for maha in dashas:
        maha_lord = normalize_planet_name(maha["lord"])
        for antar in maha.get("antardashas", []):
            antar_lord = normalize_planet_name(antar["lord"])
            start_date = antar["start"]
            end_date = antar["end"]
            
            # 1. Create a "Time-Slice" Context
            # Focus battle on these two lords
            battle_results = execute_corpus_battle_comparison(full_chart, focus_lords=[maha_lord, antar_lord])
            
            # 3. All results from the focused battle are relevant
            period_consensus = battle_results
            
            timeline_blocks.append({
                "period": f"{maha_lord} / {antar_lord}",
                "dates": f"{start_date} to {end_date}",
                "consensus": period_consensus,
                "maha_lord": maha_lord,
                "antar_lord": antar_lord
            })
            
    return timeline_blocks

def render_deep_timeline_markdown(native_name: str, timeline_blocks: list) -> str:
    """Renders the timeline into the 'Full Deep' report style the user expects."""
    from engine.consensus_report import render_consensus_meter, render_client_narrative
    
    out = [f"# {native_name.upper()} — THE SUPREME LIFE TIMELINE (56-BOOK CONSENSUS)\n"]
    out.append("This is a DNA-level analysis of your life progression. Every period below has been cross-referenced against 56 classical authorities to find the objective truth of your path.\n")
    
    for block in timeline_blocks:
        out.append(f"## ✦ {block['period']} Chapter")
        out.append(f"**Interval:** {block['dates']}\n")
        
        if not block["consensus"]:
            out.append("*The masters suggest this is a foundational period of internal growth with no major external peaks.*")
        else:
            for subject, data in block["consensus"].items():
                meter = render_consensus_meter(data["consensus"])
                narrative = render_client_narrative(subject, data["consensus"])
                
                out.append(f"### {subject}")
                out.append(meter)
                out.append(f"\n*{narrative}*\n")
                
                out.append("**The Council Verdict:**")
                for rule in data.get("top_rules", [])[:1]:
                    books = ", ".join(rule["books"])
                    out.append(f"> \"{rule['text'].strip()}\" — **{books}**")
        
        out.append("\n---\n")
        
    return "\n".join(out)
