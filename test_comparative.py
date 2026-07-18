import json
import os
from engine.comparative_test import execute_corpus_battle_comparison

def main():
    chart_path = os.path.join("charts", "manoj_chart.json")
    with open(chart_path, "r", encoding="utf-8") as f:
        chart_data = json.load(f)
        
    # Test full battle
    print("Running full battle...")
    battle_report = execute_corpus_battle_comparison(chart_data)
    
    print("\nKeys in battle report:")
    for k in battle_report.keys():
        print(" -", k)
        
    # Print one example
    if battle_report:
        first_key = list(battle_report.keys())[0]
        print("\nExample:", first_key)
        print(json.dumps(battle_report[first_key], indent=2))

if __name__ == "__main__":
    main()
