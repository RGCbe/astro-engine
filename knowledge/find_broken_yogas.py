path = '/opt/astro/runtime/event_predictor_v2.py'
lines = open(path, 'r', encoding='utf-8').read().splitlines()

for i, line in enumerate(lines):
    if 'yogas(), None' in line or 'pass# WARNING: Decompyle' in line:
        print(f"Line {i+1}:")
        for j in range(max(0, i-5), min(len(lines), i+6)):
            print(f"  {j+1}: {lines[j]}")
        print("-" * 50)
