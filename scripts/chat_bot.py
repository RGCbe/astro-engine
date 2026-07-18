import sys
import os
import json
import re
import datetime as dt
from pathlib import Path

# Setup paths to import engine
_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "engine"))

from runtime.category_engine import category_engine_instance

# A simple intent mapping for the demo without needing external LLM API keys
INTENT_MAP = {
    "marriage": ["marriage", "married", "spouse", "wedding", "wife", "husband"],
    "career": ["career", "job", "work", "promotion", "business"],
    "wealth": ["wealth", "money", "finance", "rich", "income"],
    "health": ["health", "sick", "illness", "surgery", "accident"],
    "fame": ["fame", "popular", "success", "award"]
}

def parse_intent(user_input: str) -> str:
    user_input = user_input.lower()
    for category, keywords in INTENT_MAP.items():
        if any(kw in user_input for kw in keywords):
            return category
    return None

def parse_year(user_input: str, current_year: int) -> int:
    # Look for explicit 4-digit years
    match = re.search(r'\b(19\d{2}|20\d{2})\b', user_input)
    if match:
        return int(match.group(1))
    
    # Relative years
    if "next year" in user_input.lower():
        return current_year + 1
    if "last year" in user_input.lower():
        return current_year - 1
        
    return current_year

def run_chat():
    print("="*60)
    print(" AstroReport OS — V2 Conversational AI (Terminal Demo) ")
    print("="*60)
    
    # Load a default chart for the demo
    chart_path = _ROOT / "charts" / "joseph_vijay_chart.json"
    with open(chart_path, "r", encoding="utf-8") as f:
        chart = json.load(f)
        
    name = chart.get("name", "User")
    print(f"[System] Loaded chart for: {name}")
    print("[System] You can ask questions like: 'Will I get married in 1999?' or 'How is my career next year?'")
    print("Type 'exit' or 'quit' to stop.\n")
    
    current_year = 1999 # Hardcode a reference year for relative parsing demo, or use datetime.now().year
    
    while True:
        try:
            user_input = input(f"\nYou ({name}): ")
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            if not user_input.strip():
                continue
                
            # 1. Parse Intent & Year
            category_intent = parse_intent(user_input)
            target_year = parse_year(user_input, current_year)
            
            if not category_intent:
                print("\n[AstroBot] I'm sorry, I didn't understand which life area you're asking about. Try asking about marriage, career, health, wealth, or fame.")
                continue
                
            print(f"\n[AstroBot] Querying the Meta-Reasoner for '{category_intent}' in the year {target_year}...")
            
            # 2. Targeted Real-Time Engine Query
            # We scan the specific year. The engine returns events hitting a minimum probability.
            events = category_engine_instance.scan_year(chart, target_year, min_probability=0.2)
            
            # 3. Filter the results by the requested intent
            matched_events = []
            for k, ev in events.items():
                if category_intent in ev["category"].lower() or category_intent in ev["event"].lower():
                    matched_events.append(ev)
                    
            if not matched_events:
                print(f"[AstroBot] The engine predicts no significant '{category_intent}' events for {target_year}. The probability is below the threshold.")
            else:
                # 4. Present the conversational response
                for ev in matched_events:
                    print(f"\n[AstroBot] Found a highly probable event: {ev['event']}")
                    print(f"  Confidence : {ev['probability']*100:.0f}% ({ev['confidence_band']})")
                    print(f"  Time Window: {ev['window_start']} to {ev['window_end']}")
                    print(f"  Here is my astrological reasoning (Explainability Trace):")
                    for why in ev['why']:
                        print(f"   - {why}")
                        
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    run_chat()
