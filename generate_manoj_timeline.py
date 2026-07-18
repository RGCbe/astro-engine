import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from engine.chart import compute_chart
from engine.life_engine import generate_life_timeline

def make_bar(score: int) -> str:
    """Returns a 10-block progress bar based on a 1-10 score."""
    score = max(1, min(10, score))
    return ("█" * score) + ("░" * (10 - score))

def generate_markdown_timeline(timeline_data: dict) -> str:
    from engine.philosophy import get_philosophy_text
    
    md = []
    
    # --- PAGE 1: COVER ---
    md.append("# LIFE INTELLIGENCE DOSSIER")
    md.append("**CONFIDENTIAL**\n")
    md.append(f"Prepared Exclusively For: **{timeline_data.get('user_id', 'User').upper()}**\n")
    md.append("*A Complete Reconstruction of Past • Present • Future*\n")
    md.append("Generated from:\n- Multiple Classical Astrological Systems\n- AI Timeline Intelligence\n- Evidence-Based Analysis\n")
    md.append("**Version 2.0**\n")
    md.append("---\n")
    
    # --- PAGE 2: MANIFESTO ---
    md.append("# HOW TO READ THIS REPORT\n")
    md.append("This report is not a collection of predictions.\n")
    md.append("It is a reconstruction of your life.\n")
    md.append("Every conclusion is ranked by evidence.\n")
    md.append("Every challenge includes its cause.\n")
    md.append("Every opportunity includes its timing.\n")
    md.append("Every chapter explains how it connects to the next.\n")
    md.append("The future is presented as the strongest paths indicated by the chart—not as guaranteed outcomes.\n")
    md.append("Read this report in order.\n")
    md.append("Your life is a story.\nThis report explains why each chapter unfolded the way it did.\n")
    md.append("---\n")
    
    # --- ASCII TIMELINE VISUAL ---
    md.append("# TIMELINE INTELLIGENCE\n")
    md.append("```")
    md.append(f"{timeline_data.get('seasons', [])[0]['episodes'][0]['age_start'] + 1996 if timeline_data.get('seasons') else '1996'}")
    md.append("│")
    for s in timeline_data.get('seasons', []):
        md.append(f"├──────── {s['title']}")
        md.append("│")
    md.append("└──────── New Chapter Begins")
    md.append("```\n")
    md.append("---\n")
    
    # --- EPISODES ---
    for season in timeline_data.get('seasons', []):
        for ep in season.get('episodes', []):
            md.append(f"## DOSSIER: Age {ep['age_start']} to {ep['age_end']}")
            
            # Emotional Quote
            md.append(f"> *{ep['quote']}*\n")
            
            # Intelligence Tags
            tags = ep['intelligence_tags']
            md.append(f"**STATUS**: {tags['status']} | **RISK LEVEL**: {tags['risk_level']} | **MOMENTUM**: {tags['momentum']} | **STABILITY**: {tags['stability']} | **NEXT TURNING POINT**: {tags['next_turning_point']}\n")
            
            # Bar Charts
            dim = ep['dimensions']
            md.append("```")
            md.append(f"Career       {make_bar(dim['career'])}")
            md.append(f"Money        {make_bar(dim['money'])}")
            md.append(f"Relationships{make_bar(dim['relationships'])}")
            md.append(f"Health       {make_bar(dim['health'])}")
            md.append(f"Confidence   {make_bar(dim['confidence'])}")
            md.append(f"Opportunity  {make_bar(dim['opportunity'])}")
            md.append(f"Pressure     {make_bar(dim['pressure'])}")
            md.append("```\n")
            
            # Truth Engine
            truth = ep['truth_engine']
            md.append(f"### Truth Score: {truth['truth_score']}%")
            md.append(f"*(Truth Score is derived from the net sum of supporting evidence vs counter-evidence in the active planetary periods)*\n")
            md.append(f"**Evidence Rating**: {truth['stars']}")
            md.append(f"**Assessment**: {truth['net_assessment']}\n")
            
            # Psychology
            psych = ep['psychology']
            md.append(f"**Deep Personality Profile**")
            md.append(f"- Likely Perception: {psych['what_you_saw']}")
            md.append(f"- Underlying Dynamic: {psych['what_was_really_happening']}")
            md.append(f"- Missed Opportunity: {psych['missed_opportunity']}")
            md.append(f"- Blind Spot: {psych['blind_spot']}")
            md.append(f"- Growth Area: {psych['growth_area']}\n")
            
            # Cause & Effect
            if 'cause_effect' in ep:
                ce = ep['cause_effect']
                md.append("### The Transition")
                md.append(f"**What This Period Built**: {ce['what_this_built']}")
                md.append(f"↓")
                md.append(f"**This Created**: {ce['this_created']}")
                md.append(f"↓")
                md.append(f"**Therefore**: {ce['therefore']}")
                md.append(f"↓")
                md.append(f"**Next Chapter Begins**: {ce['next_chapter']}\n")
                
            md.append("---\n")
            
    return "\n".join(md)

def main():
    chart = compute_chart(
        name="Manoj Kumar",
        date="1996-05-25",
        time="20:25",
        tz_hours=5.5,
        place="Coimbatore",
        lat=11.25,
        lon=77.12
    )
    
    # Generate the new Life Intelligence timeline
    timeline_data = generate_life_timeline(chart, user_id="Manoj Kumar")
    
    # Save raw JSON for the frontend
    output_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(output_dir, exist_ok=True)
    
    json_path = os.path.join(output_dir, "MANOJ_TIMELINE_DATA.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(timeline_data, f, indent=2)
        
    # Save as readable Markdown
    md_content = generate_markdown_timeline(timeline_data)
    md_path = os.path.join(output_dir, "MANOJ_LIFE_INTELLIGENCE_REPORT.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
        
    # Generate PDF
    from engine.pdf_render import render_pdf
    pdf_path = os.path.join(output_dir, "MANOJ_LIFE_INTELLIGENCE_REPORT.pdf")
    render_pdf(md_content, pdf_path)
        
    print(f"Generated Phase 2 Digital Twin timeline for Manoj Kumar.")
    
if __name__ == '__main__':
    main()
