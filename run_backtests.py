import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine.backtest import run_full_backtest

def main():
    print("Running Full Empirical Backtest against Known Charts...")
    results = run_full_backtest()
    
    print("\n================ BACKTEST SUMMARY ================")
    print(f"Total Events Scored: {results['n_events_scored']}")
    print(f"Overall Strict Match (Primary): {results['overall_strict_match_pct']}%")
    print(f"Overall Loose Match (Primary or Secondary): {results['overall_either_match_pct']}%")
    print(f"Overall Weighted Accuracy: {results['overall_weighted_pct']}%")
    
    print("\n--- Accuracy by Event Type ---")
    for evt, stats in results['by_event_type'].items():
        print(f"{evt.ljust(20)} | N={stats['n']} | Strict: {stats['strict_pct']}% | Loose: {stats['either_pct']}% | Weighted: {stats['weighted_pct']}%")

if __name__ == "__main__":
    main()
