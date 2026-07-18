import json, os
from collections import Counter

master_path = "gemma_extractions/_MASTER_dedup.json"
master = json.load(open(master_path, encoding="utf-8"))

all_rules = []
if isinstance(master, list):
    all_rules = master
elif isinstance(master, dict):
    for k, v in master.items():
        if isinstance(v, list):
            all_rules.extend(v)

total = len(all_rules)

cats = Counter()
books = Counter()
valence = Counter()

for rule in all_rules:
    if isinstance(rule, dict):
        cats[rule.get("category", "unknown")] += 1
        books[rule.get("source", rule.get("book", "unknown"))] += 1
        valence[rule.get("valence", rule.get("type", "neutral"))] += 1

print(f"TOTAL RULES IN MASTER CORPUS: {total:,}")
print()
print("TOP 20 BOOKS BY RULES:")
for b, cnt in books.most_common(20):
    print(f"  {cnt:5d}  {b}")
print()
print("BY CATEGORY:")
for c, cnt in cats.most_common():
    print(f"  {cnt:5d}  {c}")
print()
print("BY VALENCE:")
for v, cnt in valence.most_common():
    print(f"  {cnt:5d}  {v}")
