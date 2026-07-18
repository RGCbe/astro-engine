import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.corpus import get_corpus
from scratch.analyze_remaining_25 import rule_valence

def main():
    corpus = get_corpus()
    print("=" * 80)
    print("Forensic Rule Analysis for Mercury-Venus period")
    print("=" * 80)
    rules = corpus.get_dasha_rules("Mercury", "Venus", limit=30)
    for idx, r in enumerate(rules):
        v = rule_valence(r.text)
        print(f"[{idx+1}] [{v.upper()}] {r.text[:120]}...")

if __name__ == "__main__":
    main()
