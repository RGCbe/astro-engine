"""
Consensus Report Module.
Turns the raw 56-book battle results into premium markdown/HTML visualizations.
"""

def render_consensus_meter(consensus_data: dict) -> str:
    """Renders a visual gauge of how much the 56 books agree."""
    percent = consensus_data.get("consensus_percent", 50)
    status = consensus_data.get("status", "Mixed")
    
    # Choose color based on status
    color = "#d4af37" # Gold for neutral/mixed
    if "Auspicious" in status: color = "#2ecc71" # Green
    elif "Inauspicious" in status: color = "#e74c3c" # Red
    elif "Contradiction" in status: color = "#f39c12" # Orange
    
    meter_html = f'''
    <div style="margin: 10px 0; font-family: sans-serif;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-size: 0.85em; font-weight: bold; color: #555;">{status}</span>
            <span style="font-size: 0.85em; font-weight: bold; color: {color};">{percent}% Consensus</span>
        </div>
        <div style="width: 100%; height: 8px; background: #eee; border-radius: 4px; overflow: hidden;">
            <div style="width: {percent}%; height: 100%; background: {color}; border-radius: 4px;"></div>
        </div>
    </div>
    '''
    return meter_html

def render_client_narrative(subject: str, consensus_data: dict) -> str:
    """Translates raw consensus math into a premium, empathetic consultation tone."""
    status = consensus_data.get("status", "Mixed")
    percent = consensus_data.get("consensus_percent", 50)
    
    if "Supreme" in status or percent > 85:
        return f"There is an overwhelming agreement among the classical masters regarding your {subject}. They speak with one voice on the strength and clarity of this placement."
    elif "Auspicious" in status:
        return f"The majority of our 56 classical sources view your {subject} with favor. While minor nuances exist, the core promise of this placement remains positive and supportive."
    elif "Inauspicious" in status:
        return f"The classical authorities lean toward caution regarding your {subject}. This is not a verdict of failure, but a signpost from the masters to apply discipline and awareness to this area of your life."
    elif "Contradiction" in status:
        return f"Your {subject} creates a fascinating debate among the masters. Some see a great challenge where others see a profound hidden strength. This split consensus suggests that the outcome of this placement is largely in your hands, waiting for your conscious effort to tip the balance."
    else:
        return f"The masters provide a balanced, nuanced view of your {subject}. This placement brings a mix of experiences that will help you grow through both ease and effort."

def generate_consensus_report_markdown(battle_results: dict) -> str:
    """Generates the full Battle Report section in Markdown with client-focused conveyance."""
    out = ["## ✦ The Council of Masters (Classical Consensus Analysis)\n"]
    out.append("To ensure the highest accuracy, your chart was analyzed by our autonomous swarm across **56 classical Vedic texts**. We do not rely on a single opinion; instead, we look for the consensus among the masters.\n")
    
    # Group by type
    by_type = {}
    for subject, data in battle_results.items():
        t = data.get("type", "General")
        by_type.setdefault(t, []).append((subject, data))
        
    for t, subjects in by_type.items():
        out.append(f"### {t}\n")
        for subject, data in subjects:
            consensus = data["consensus"]
            meter = render_consensus_meter(consensus)
            narrative = render_client_narrative(subject, consensus)
            
            out.append(f"#### {subject}")
            out.append(meter)
            out.append(f"\n*{narrative}*\n")
            
            out.append("\n**Classical Evidence:**\n")
            for rule in data.get("top_rules", [])[:2]:
                books = ", ".join(rule["books"])
                text = rule["text"].strip()
                out.append(f"> \"{text}\" — *{books}*\n")
            out.append("\n---\n")
            
    return "\n".join(out)
